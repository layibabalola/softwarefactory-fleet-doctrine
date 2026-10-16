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

    # Regression (verifier 2026-10-16): each of these staged every file in a scratch repo, and passed.
    SWEEP_SPELLINGS = [
        "git add ':!secret.txt'", "git add -- ':(exclude)x'", "git add ':^a'", "git add ..", "git add ./.",
        "git add .//", "git add sub/..", "cd sub && git add ../", "git add :", "git add ':/:'", "git add '**'",
        "git add ':(glob)**'", "git add ':(top,glob)**'", "git add ':(top)'", "git commit -m x -- ':!a'",
        "git commit -m x ..", "bash -c 'git add -A'", "pwsh -Command \"git add .\"", "eval 'git add -A'",
        "cmd /c git add -A", "sh -c 'cd x && git commit -am y'",
    ]
    EXACT_SPELLINGS = [
        "git add ':!x' src/a.py", "git add ':(attr:foo)src'", "git add 'src/*.py'", "git add '*.md'",
        "git add ../sibling/a.py", "git add .gitignore", "git add ':/src/a.py'", "bash -c 'git add -- a.py'",
        "git commit -m @'\nDon't stage everything\ngit add -A was the old way\n'@",
        "git commit -m @\"\nSay \"no\"\ngit commit -a was the old way\n\"@\ngit status",
    ]

    def test_refuses_every_whole_tree_spelling(self):
        for c in self.SWEEP_SPELLINGS:
            with self.subTest(c=c):
                self.assertEqual(hook(ADD, c), 2)

    def test_allows_exact_paths_and_powershell_here_strings(self):
        for c in self.EXACT_SPELLINGS:
            with self.subTest(c=c):
                self.assertEqual(hook(ADD, c, tool="PowerShell"), 0)


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

    def test_quoted_mention_never_covers_and_statements_do(self):
        # Regression (verifier 2026-10-16): text that merely MENTIONED the variable covered what followed.
        for c in ("echo 'export GIT_OPTIONAL_LOCKS=0'; git status", "echo \"$env:GIT_OPTIONAL_LOCKS=0\"; git diff",
                  "bash -c 'git status'", "eval 'git log -1'"):
            with self.subTest(c=c):
                self.assertEqual(hook(LOCKS, c), 2)
        for c in ("Set-Item Env:GIT_OPTIONAL_LOCKS 0; git status", "$env:GIT_OPTIONAL_LOCKS = \"0\"\ngit log -1",
                  "git commit -m @'\nDon't\ngit status said so\n'@", "bash -c 'git --no-optional-locks status'"):
            with self.subTest(c=c):
                self.assertEqual(hook(LOCKS, c, tool="PowerShell"), 0)


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


NUT = HERE / "pre-push-no-unpinned-tool.py"
TODAY = "2026-10-16"


def _g(repo: str, *a: str, env: dict | None = None) -> str:
    return subprocess.run(["git", "-C", repo, "-c", "user.email=t@example.invalid", "-c", "user.name=t", *a],
                          check=True, capture_output=True, text=True, env=env).stdout.strip()


class NoUnpinnedTool(unittest.TestCase):
    """A consumer push that adds or modifies a shared tool's file is refused unless it is the pinned runner
    or allowlisted with a reason and an unexpired expiry."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        t = Path(self._tmp.name)
        self.remote, self.repo = str(t / "remote.git"), str(t / "work")
        subprocess.run(["git", "init", "-q", "--bare", self.remote], check=True)
        subprocess.run(["git", "init", "-q", "-b", "master", self.repo], check=True)
        _g(self.repo, "remote", "add", "origin", self.remote)
        self.write("tools/session-checkpoint.py", "print(1)\n")      # a census copy the project already has
        self.write("README.md", "x\n")
        self.commit("base")
        _g(self.repo, "push", "-q", "origin", "master")
        self.base = _g(self.repo, "rev-parse", "HEAD")

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, rel: str, body: str):
        p = Path(self.repo) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8", newline="\n")

    def commit(self, msg: str) -> str:
        _g(self.repo, "add", "-A", ".")
        _g(self.repo, "commit", "-q", "-m", msg)
        return _g(self.repo, "rev-parse", "HEAD")

    def judge(self, line: str | None = None, *extra: str) -> subprocess.CompletedProcess:
        head = _g(self.repo, "rev-parse", "HEAD")
        line = line or f"refs/heads/master {head} refs/heads/master {self.base}"
        return subprocess.run([sys.executable, str(NUT), "origin", self.remote, "--repo", self.repo, "--today", TODAY, *extra],
                              input=line + "\n", capture_output=True, text=True)

    def allow(self, entries):
        self.write("factory-pins/no-unpinned-tool.json", json.dumps({"allow": entries}))

    def test_canonical_copy_added_or_modified_refuses(self):
        self.write("coordination/tools/check-doc-size.py", "copy()\n")
        self.commit("copy")
        r = self.judge()
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("adds coordination/tools/check-doc-size.py", r.stderr)
        self.assertIn("pin-runner.py run check-doc-size", r.stderr)
        for name in ("pre_push_ff_only.py", "exact-path-add.py", "Git-Optional-Locks.py", "session_start_auth.py",
                     "pre-push-no-unpinned-tool.py", "pin-runner.py"):
            with self.subTest(name=name):
                self.write(f"elsewhere/{name}", "x\n")
                self.commit(name)
                self.assertEqual(self.judge().returncode, 1)

    def test_census_family_new_copy_refuses_existing_edit_allowed(self):
        self.write("tools/session-checkpoint.py", "print(2)\n")
        self.commit("edit the project's own copy")
        self.assertEqual(self.judge().returncode, 0, "editing the existing census copy is allowed")
        self.write("other/session_checkpoint.py", "print(3)\n")
        self.commit("second copy")
        r = self.judge()
        self.assertEqual(r.returncode, 1)
        self.assertIn("a NEW copy of the census-counted tool 'session-checkpoint'", r.stderr)

    def test_unrelated_files_deletion_and_removal_pass(self):
        self.write("src/check-doc-size.md", "doc\n")
        self.write("src/app.py", "x\n")
        self.commit("unrelated")
        self.assertEqual(self.judge().returncode, 0)
        Path(self.repo, "tools/session-checkpoint.py").unlink()
        self.commit("retire the copy")
        self.assertEqual(self.judge().returncode, 0, "deleting a copy is what the hook wants")
        self.assertEqual(self.judge(f"(delete) {Z} refs/heads/master {self.base}").returncode, 0)

    def test_allowlist_needs_reason_and_unexpired_bounded_expiry(self):
        path = "coordination/tools/check-doc-size.py"
        self.write(path, "forward()\n")
        for entry, rc, why in (
            ({"path": path, "reason": "forwarder; deliver.py names this path", "expires": "2026-11-06"}, 0, None),
            ({"path": path, "reason": "", "expires": "2026-11-06"}, 1, "has no reason"),
            ({"path": path, "reason": "r", "expires": "soon"}, 1, "no valid 'expires'"),
            ({"path": path, "reason": "r", "expires": "2026-10-15"}, 1, "EXPIRED 2026-10-15"),
            ({"path": path, "reason": "r", "expires": "2027-06-01"}, 1, "more than 120 days out"),
        ):
            with self.subTest(entry=entry):
                self.allow([entry])
                self.commit(json.dumps(entry))
                r = self.judge()
                self.assertEqual(r.returncode, rc, r.stderr)
                if why:
                    self.assertIn(why, r.stderr)
        self.write("factory-pins/no-unpinned-tool.json", "{not json")
        self.commit("broken allowlist")
        self.assertEqual(self.judge().returncode, 2, "an unreadable allowlist refuses (exit 2)")

    def test_vendored_runner_only_when_it_equals_the_pin(self):
        body = "RUNNER = 1\n"
        self.write("factory-pins/pin-runner.py", body)
        blob = subprocess.run(["git", "hash-object", "--stdin"], input=body.encode(), capture_output=True,
                              check=True).stdout.decode().strip()   # bytes: text-mode stdin is CRLF on Windows
        self.write("factory-pins/factory-pins.json", json.dumps({"runner": {"blob": blob}}))
        self.commit("adopt runner")
        self.assertEqual(self.judge().returncode, 0, "the pinned vendored runner passes")
        self.write("factory-pins/pin-runner.py", "RUNNER = 2  # local edit\n")
        self.commit("edit runner")
        r = self.judge()
        self.assertEqual(r.returncode, 1)
        self.assertIn("is not the runner blob pinned", r.stderr)

    def test_new_branch_is_judged_against_its_merge_base(self):
        _g(self.repo, "fetch", "-q", "origin")
        _g(self.repo, "checkout", "-q", "-b", "feature")
        self.write("src/ok.py", "x\n")
        head = self.commit("feature work")
        self.assertEqual(self.judge(f"refs/heads/feature {head} refs/heads/feature {Z}").returncode, 0,
                         "a new branch is judged by its own commits, not the whole tree")
        self.write("lib/check_doc_size.py", "x\n")
        head = self.commit("copy on a branch")
        self.assertEqual(self.judge(f"refs/heads/feature {head} refs/heads/feature {Z}").returncode, 1)

    def test_real_push_from_a_linked_worktree(self):
        # git runs the hook with GIT_DIR exported when the push starts in a linked worktree (58017fbbe).
        hooks = Path(_g(self.repo, "rev-parse", "--path-format=absolute", "--git-common-dir")) / "hooks"
        hooks.mkdir(exist_ok=True)
        py = Path(sys.executable).as_posix()
        (hooks / "pre-push").write_text(f'#!/bin/sh\nexec "{py}" "{NUT.as_posix()}" --today {TODAY} "$@"\n',
                                        encoding="utf-8", newline="\n")
        os.chmod(hooks / "pre-push", 0o755)
        wt = str(Path(self._tmp.name) / "linked")
        _g(self.repo, "worktree", "add", "-q", "-b", "wt", wt, "master")
        Path(wt, "src").mkdir()
        Path(wt, "src", "app.py").write_text("x\n", encoding="utf-8")
        _g(wt, "add", "--", "src/app.py")
        _g(wt, "commit", "-q", "-m", "clean")
        ok = subprocess.run(["git", "-C", wt, "push", "-q", "origin", "HEAD:refs/heads/master"], capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        Path(wt, "src", "check-doc-size.py").write_text("copy\n", encoding="utf-8")
        _g(wt, "add", "--", "src/check-doc-size.py")
        _g(wt, "commit", "-q", "-m", "copy")
        bad = subprocess.run(["git", "-C", wt, "push", "-q", "origin", "HEAD:refs/heads/master"], capture_output=True, text=True)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("[no-unpinned-tool] PUSH REFUSED", bad.stderr)
        self.assertIn("adds src/check-doc-size.py", bad.stderr)

    def test_families_equal_the_census_config(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("nut", NUT)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        cfg = json.loads((HERE.parent / "tools" / "tool-census.config.json").read_text(encoding="utf-8"))
        census = {f["name"]: sorted(f["names"]) for f in cfg["families"]}
        hook = {k: sorted(v) for k, v in {**mod.CANONICAL, **mod.CENSUS}.items()}
        self.assertEqual(hook, census, "hook families drifted from tools/tool-census.config.json")
        bus_tools = {p.name for d in ("tools/factory", "hooks", "hooks/claude") for p in (HERE.parent / d).glob("*.py")
                     if not p.name.endswith(".tests.py")}
        for name in bus_tools:
            with self.subTest(name=name):
                self.assertTrue(any(name in v for v in mod.CANONICAL.values()), f"bus factory tool {name} is not a canonical family")


if __name__ == "__main__":
    unittest.main(verbosity=1)
