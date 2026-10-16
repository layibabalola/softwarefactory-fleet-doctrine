#!/usr/bin/env python3
"""Tests for the generic refusing hooks.   python hooks/hooks.tests.py

Each hook is executed as a subprocess exactly as Claude Code / git would run it (payload or ref
lines on stdin, exit status is the verdict).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ADD = HERE / "claude" / "exact-path-add.py"
LOCKS = HERE / "claude" / "git-optional-locks.py"
FF = HERE / "pre-push-ff-only.py"
Z = "0" * 40


def hook(script: Path, command: str, tool: str = "Bash", env: dict | None = None) -> int:
    payload = json.dumps({"tool_name": tool, "tool_input": {"command": command}})
    e = {k: v for k, v in os.environ.items() if k != "GIT_OPTIONAL_LOCKS"}
    e.update(env or {})
    return subprocess.run([sys.executable, str(script)], input=payload, capture_output=True, text=True, env=e).returncode


class ExactPathAdd(unittest.TestCase):
    REFUSE = [
        "git add -A", "git add --all", "git add .", "git add -u", "git add --update", "git add -Av",
        "git -C /x/y add -A", "git --no-optional-locks add .", "cd repo && git add -A && git commit -m x",
        "git add -- .", "git add :/", "git stage -A", "git commit -a -m x", "git commit -am 'x'",
        "git commit --all -m x", "git commit -vam x", "git commit -m x .", "GIT_DIR=.git git add -A",
        "x=$(git add -A)", "git.exe add -A", "& git add .", "git add src/a.py; git add -u",
    ]
    ALLOW = [
        "git add -- src/a.py docs/b.md", "git add .claude/settings.json", "git add -p src/a.py",
        "git commit -m 'git add -A is banned'", "git commit -m \"commit -a\"", "git commit --amend --no-edit",
        "git commit -F msg.txt", "git commit -m add -- a.py", "echo git add -A", "git status",
        "git commit -ma", "git commit --allow-empty -m x", "git add ./src/a.py",
        "git commit -F- <<'EOF'\ngit add -A\ngit commit -a\nEOF\n", "# git add -A\nls",
        "git log --all", "git stash push -u -m tag", "git push --all origin",
    ]

    def test_refuses_sweeps(self):
        for c in self.REFUSE:
            with self.subTest(c=c):
                self.assertEqual(hook(ADD, c), 2)

    def test_allows_exact_paths_and_quoted_text(self):
        for c in self.ALLOW:
            with self.subTest(c=c):
                self.assertEqual(hook(ADD, c), 0)

    def test_powershell_tool_and_bad_payload(self):
        self.assertEqual(hook(ADD, "git add -A", tool="PowerShell"), 2)
        p = subprocess.run([sys.executable, str(ADD)], input="not json", capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)


class OptionalLocks(unittest.TestCase):
    REFUSE = [
        "git status", "git status -sb", "git diff --cached", "git log --oneline -5", "git show HEAD",
        "git rev-list --count a..b", "git -C /r status", "cd r && git diff", "x=$(git rev-list HEAD | wc -l)",
        "git fetch && git log origin/master", "git status --no-optional-locks",
        "GIT_OPTIONAL_LOCKS=1 git status", "git.exe status",
    ]
    ALLOW = [
        "git --no-optional-locks status", "git -C r --no-optional-locks diff", "GIT_OPTIONAL_LOCKS=0 git log",
        "env GIT_OPTIONAL_LOCKS=0 git status", "export GIT_OPTIONAL_LOCKS=0; git status && git diff",
        "$env:GIT_OPTIONAL_LOCKS='0'; git status", "git add -- a.py", "git commit -m 'git status'",
        "git push origin HEAD:master", "git fetch origin", "git rebase origin/master", "git stash show",
        "git merge-base --is-ancestor a b", "echo git status", "git rev-parse HEAD", "git worktree list",
        "git cat-file -p HEAD",
    ]

    def test_refuses_unsuppressed_observers(self):
        for c in self.REFUSE:
            with self.subTest(c=c):
                self.assertEqual(hook(LOCKS, c), 2)

    def test_allows_suppressed_observers_and_every_mutation(self):
        for c in self.ALLOW:
            with self.subTest(c=c):
                self.assertEqual(hook(LOCKS, c), 0)

    def test_session_env_already_suppresses(self):
        self.assertEqual(hook(LOCKS, "git status", env={"GIT_OPTIONAL_LOCKS": "0"}), 0)


class FastForwardOnly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        r = cls.repo = cls._tmp.name

        def g(*a):
            return subprocess.run(["git", "-C", r, "-c", "user.email=t@example.invalid", "-c", "user.name=t", *a],
                                  check=True, capture_output=True, text=True).stdout.strip()
        g("init", "-q")
        g("commit", "-q", "--allow-empty", "-m", "a")
        cls.a = g("rev-parse", "HEAD")
        g("commit", "-q", "--allow-empty", "-m", "b")
        cls.b = g("rev-parse", "HEAD")
        g("checkout", "-q", "-b", "side", cls.a)
        g("commit", "-q", "--allow-empty", "-m", "c")
        cls.c = g("rev-parse", "HEAD")

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def push(self, line: str, *extra: str) -> int:
        return subprocess.run([sys.executable, str(FF), "origin", "https://example.invalid/r.git", "--repo", self.repo,
                               *extra], input=line + "\n", capture_output=True, text=True).returncode

    def test_fast_forward_and_creation_pass(self):
        self.assertEqual(self.push(f"refs/heads/master {self.b} refs/heads/master {self.a}"), 0)
        self.assertEqual(self.push(f"refs/heads/master {self.b} refs/heads/master {Z}"), 0)

    def test_non_fast_forward_and_deletion_refuse(self):
        self.assertEqual(self.push(f"refs/heads/side {self.c} refs/heads/master {self.b}"), 1)
        self.assertEqual(self.push(f"(delete) {Z} refs/heads/master {self.b}"), 1)
        self.assertEqual(self.push(f"refs/heads/x {self.c} refs/heads/main {self.b}"), 1)

    def test_unknown_remote_tip_refuses(self):
        self.assertEqual(self.push(f"refs/heads/master {self.b} refs/heads/master {'1' * 40}"), 1)

    def test_unprotected_ref_is_not_judged(self):
        self.assertEqual(self.push(f"refs/heads/side {self.c} refs/heads/side {self.b}"), 0)
        self.assertEqual(self.push(f"(delete) {Z} refs/heads/side {self.b}"), 0)

    def test_protect_flag_and_config(self):
        self.assertEqual(self.push(f"refs/heads/side {self.c} refs/heads/side {self.b}", "--protect", "side"), 1)
        cfg = Path(self.repo) / "ff.json"
        cfg.write_text(json.dumps({"protected": ["release/*"]}), encoding="utf-8")
        self.assertEqual(self.push(f"x {self.c} refs/heads/release/1 {self.b}", "--config", str(cfg)), 1)
        cfg.write_text("{}", encoding="utf-8")
        self.assertEqual(self.push(f"x {self.b} refs/heads/master {self.a}", "--config", str(cfg)), 2)

    def test_multiple_lines_any_refusal_refuses(self):
        lines = f"refs/heads/master {self.b} refs/heads/master {self.a}\n(delete) {Z} refs/heads/main {self.a}"
        self.assertEqual(self.push(lines), 1)


if __name__ == "__main__":
    unittest.main(verbosity=1)
