#!/usr/bin/env python3
"""Tests for the generic refusing hooks.   python hooks/hooks.tests.py

Each hook is executed as a subprocess exactly as Claude Code / git would run it (payload or ref
lines on stdin, exit status is the verdict).
"""
from __future__ import annotations

import importlib.util
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
        self.write("tools/doctrine_outbox.py", "print(1)\n")         # a census copy the project already has
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
        self.write("tools/doctrine_outbox.py", "print(2)\n")
        self.commit("edit the project's own copy")
        self.assertEqual(self.judge().returncode, 0, "editing the existing census copy is allowed")
        self.write("other/doctrine-outbox.py", "print(3)\n")
        self.commit("second copy")
        r = self.judge()
        self.assertEqual(r.returncode, 1)
        self.assertIn("a NEW copy of the census-counted tool 'doctrine-outbox'", r.stderr)

    def test_session_checkpoint_is_canonical_since_the_bus_ships_it(self):
        self.write("tools/session-checkpoint.py", "print('a project copy')\n")
        self.commit("a project copy, added after tools/factory/session-checkpoint.py landed")
        r = self.judge()
        self.assertEqual(r.returncode, 1, "a canonical family refuses an add or an edit")
        self.assertIn("pin-runner.py run session-checkpoint", r.stderr)

    def test_unrelated_files_deletion_and_removal_pass(self):
        self.write("src/check-doc-size.md", "doc\n")
        self.write("src/app.py", "x\n")
        self.commit("unrelated")
        self.assertEqual(self.judge().returncode, 0)
        Path(self.repo, "tools/doctrine_outbox.py").unlink()
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

    def test_merging_the_mainline_into_an_old_branch_is_not_the_branch_s_change(self):
        # Cloudvore 2026-10-19: a packet branch cut before the mainline turned tools/kernel-subjects.py into a forwarder
        # merged origin/master (the "merge, never rebase" rule) and its push was refused for the mainline's edits.
        _g(self.repo, "checkout", "-q", "-b", "feature")
        self.write("src/ok.py", "x\n")
        old_tip = self.commit("feature work")
        _g(self.repo, "push", "-q", "origin", "feature")
        _g(self.repo, "checkout", "-q", "master")
        self.write("tools/kernel-subjects.py", "forward()\n")       # landed on the mainline under its own review
        self.write("tools/doctrine-outbox.py", "print(9)\n")        # a census copy the mainline added
        self.commit("mainline lands a forwarder")
        _g(self.repo, "push", "-q", "origin", "master")
        _g(self.repo, "checkout", "-q", "feature")
        _g(self.repo, "merge", "-q", "--no-ff", "-m", "merge origin/master", "origin/master")
        head = _g(self.repo, "rev-parse", "HEAD")
        line = f"refs/heads/feature {head} refs/heads/feature {old_tip}"
        r = self.judge(line)
        self.assertEqual(r.returncode, 0, "files that equal the mainline were judged when they landed: " + r.stderr)
        self.write("tools/kernel-subjects.py", "forward()  # the branch's own edit\n")
        head = self.commit("edit the forwarder on the branch")
        r = self.judge(f"refs/heads/feature {head} refs/heads/feature {old_tip}")
        self.assertEqual(r.returncode, 1, "the branch's own edit to a canonical copy is still refused")
        self.assertIn("tools/kernel-subjects.py -- a copy of the shared tool", r.stderr)
        self.assertEqual(self.judge(f"refs/heads/master {head} refs/heads/master "
                                    f"{_g(self.repo, 'rev-parse', 'origin/master')}").returncode, 1,
                         "the same tip pushed to the mainline itself is judged against the mainline")

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


RUNNER_SRC = HERE.parent / "tools" / "factory" / "pin-runner.py"
README = HERE / "README.md"


def readme_layer() -> str:
    """The documented ff-only pre-push layer, extracted verbatim from hooks/README.md (dedented)."""
    text = README.read_text(encoding="utf-8").replace("\r\n", "\n")
    start = text.index("   ```sh\n   # factory-ff-only\n") + len("   ```sh\n")
    end = text.index("   ```\n", start)
    return "".join(l[3:] if l.startswith("   ") else l for l in text[start:end].splitlines(True))


class FactoryPrePushFile(unittest.TestCase):
    """hooks/pre-push.factory.sh is what `pin-runner.py init` writes: its ff-only layer must stay the README layer,
    verbatim (the push behaviour of that layer is regression-tested below), followed by the no-unpinned-tool layer.
    tools/factory/init.tests.py runs the whole file through real pushes."""

    def test_the_file_carries_the_readme_layer_verbatim_then_the_no_unpinned_layer(self):
        body = (HERE / "pre-push.factory.sh").read_text(encoding="utf-8").replace("\r\n", "\n")
        layer = readme_layer()
        self.assertIn(layer, body)
        self.assertGreater(body.index("# factory-no-unpinned-tool\n"), body.index(layer))
        self.assertIn("run no-unpinned-tool --", body)


class FfOnlyLayerSnippet(unittest.TestCase):
    """Regression (magic-lantern adoption, 2026-10-16): the layer read the runner and pins from
    refs/remotes/origin/master only, so a repository whose work never reaches master refused EVERY push.
    The README layer now judges from the first protected remote-tracking ref holding the runner, else the
    pushed commit; protected branches come from factory-pins/ff-only.json at that ref."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        t = Path(self._tmp.name)
        self.bus, self.repo, self.remote, self.seen = t / "bus", t / "consumer", t / "remote.git", t / "seen.txt"
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_") and k != "FACTORY_BUS_CLONE"}
        self.env["FACTORY_PINS_CACHE"] = str(t / "cache")
        lf = lambda p: p.read_bytes().replace(b"\r\n", b"\n")
        (self.bus / "hooks").mkdir(parents=True)
        (self.bus / "tools" / "factory").mkdir(parents=True)
        (self.bus / "hooks" / "pre-push-ff-only.py").write_bytes(lf(FF))
        (self.bus / "tools" / "factory" / "pin-runner.py").write_bytes(lf(RUNNER_SRC))
        subprocess.run(["git", "init", "-q", str(self.bus)], check=True)
        self.g(self.bus, "add", "--", "hooks", "tools")
        self.g(self.bus, "commit", "-qm", "bus")
        c = self.g(self.bus, "rev-parse", "HEAD")
        subprocess.run(["git", "init", "-q", "--bare", str(self.remote)], check=True)
        subprocess.run(["git", "init", "-q", "-b", "codex/audit-remediation", str(self.repo)], check=True)
        self.g(self.repo, "remote", "add", "origin", str(self.remote))
        (self.repo / "factory-pins").mkdir()
        (self.repo / "factory-pins" / "pin-runner.py").write_bytes(lf(RUNNER_SRC))
        (self.repo / "factory-pins" / "factory-pins.json").write_text(
            json.dumps({"schema": "factory-pins.v1", "bus_clone": [self.bus.as_posix()], "tools": {}}), encoding="utf-8")
        for a in (["pin", "pre-push-ff-only", "--commit", c, "--path", "hooks/pre-push-ff-only.py", "--reviewer", "t", "--reason", "fixture"],
                  ["adopt-runner", "--commit", c]):
            p = subprocess.run([sys.executable, str(self.repo / "factory-pins" / "pin-runner.py"), *a],
                               capture_output=True, text=True, env=self.env, cwd=str(self.repo))
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.g(self.repo, "add", "--", "factory-pins")
        self.g(self.repo, "commit", "-qm", "adopt")
        hook = Path(self.g(self.repo, "rev-parse", "--path-format=absolute", "--git-path", "hooks/pre-push"))
        hook.parent.mkdir(parents=True, exist_ok=True)
        hook.write_text("#!/bin/sh\nset -e\n" + readme_layer() + f'cat > "{self.seen.as_posix()}"\n', encoding="utf-8", newline="\n")
        os.chmod(hook, 0o755)

    def tearDown(self):
        self._tmp.cleanup()

    def g(self, repo, *a: str) -> str:
        return subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@example.invalid", "-c", "user.name=t",
                               "-c", "core.autocrlf=false", *a], check=True, capture_output=True, text=True,
                              env=self.env).stdout.strip()

    def push(self, repo, *a: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-C", str(repo), "-c", "core.autocrlf=false", "push", "origin", *a],
                              capture_output=True, text=True, env=self.env)

    def test_repo_whose_only_branch_is_not_master_pushes(self):
        self.assertNotIn("master", self.g(self.repo, "branch", "-a"))
        r = self.push(self.repo, "HEAD:refs/heads/codex/audit-remediation")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("refs/heads/codex/audit-remediation", self.seen.read_text(encoding="utf-8"), "stdin handed on")
        (self.repo / "a.txt").write_text("a\n", encoding="utf-8")
        self.g(self.repo, "add", "--", "a.txt")
        self.g(self.repo, "commit", "-qm", "a")
        r = self.push(self.repo, "HEAD:refs/heads/codex/audit-remediation")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_consumer_config_protects_its_own_branch_and_a_linked_worktree_pushes(self):
        (self.repo / "factory-pins" / "ff-only.json").write_text(json.dumps({"protected": ["codex/*"]}), encoding="utf-8")
        self.g(self.repo, "add", "--", "factory-pins/ff-only.json")
        self.g(self.repo, "commit", "-qm", "protect codex/*")
        self.assertEqual(self.push(self.repo, "HEAD:refs/heads/codex/audit-remediation").returncode, 0)
        self.g(self.repo, "fetch", "-q", "origin")
        self.g(self.repo, "commit", "-q", "--amend", "-m", "rewrite")
        r = self.push(self.repo, "--force", "HEAD:refs/heads/codex/audit-remediation")
        self.assertNotEqual(r.returncode, 0, "a configured protected branch moves fast-forward only")
        self.assertIn("[ff-only] PUSH REFUSED", r.stderr)
        self.g(self.repo, "reset", "-q", "--hard", "refs/remotes/origin/codex/audit-remediation")
        wt = Path(self._tmp.name) / "linked"
        self.g(self.repo, "worktree", "add", "-q", "--detach", str(wt))
        (wt / "b.txt").write_text("b\n", encoding="utf-8")
        self.g(wt, "add", "--", "b.txt")
        self.g(wt, "commit", "-qm", "b")
        r = self.push(wt, "HEAD:refs/heads/codex/audit-remediation")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_observe_only_mode_of_optional_locks(self):
        self.assertEqual(hook(LOCKS, "git status"), 2, "default refuses")
        payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": "git status"}})
        e = {k: v for k, v in os.environ.items() if k != "GIT_OPTIONAL_LOCKS"}
        p = subprocess.run([sys.executable, str(LOCKS), "--observe-only"], input=payload, capture_output=True, text=True, env=e)
        self.assertEqual(p.returncode, 0)
        self.assertIn("OBSERVED", p.stderr)


BT = HERE / "pre-push-bus-tests.py"
# A suite the fixture repo carries: passes unless the TESTED tree holds FAIL, and proves no GIT_DIR leaked in.
FAKE_SUITE = """import os, unittest
from pathlib import Path
class T(unittest.TestCase):
    def test_a(self):
        self.assertFalse(Path("FAIL").exists(), "FAIL marker in the tested tree")
    def test_b(self):
        self.assertNotIn("GIT_DIR", os.environ)
    def test_c(self):
        pass
    def test_d(self):
        pass
"""


class BusTests(unittest.TestCase):
    """The bus writers' pre-push layer runs the configured suites on the PUSHED tip and refuses on failure."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        t = Path(self._tmp.name)
        self.remote, self.repo = str(t / "remote.git"), str(t / "work")
        subprocess.run(["git", "init", "-q", "--bare", "-b", "master", self.remote], check=True)
        subprocess.run(["git", "init", "-q", "-b", "master", self.repo], check=True)
        _g(self.repo, "remote", "add", "origin", self.remote)
        self.write("t/fake.tests.py", FAKE_SUITE)
        self.write("hooks/x.py", "x = 1\n")
        self.write("cos-feedback/a.md", "a\n")
        self.commit("base")
        _g(self.repo, "push", "-q", "origin", "master")
        self.base = _g(self.repo, "rev-parse", "HEAD")
        self.cfg = t / "bus-tests.json"
        self.cfg.write_text(json.dumps({"trigger": ["hooks/", "t/"], "suites": [
            {"name": "fake", "argv": ["{python}", "t/fake.tests.py"], "shard": True}]}), encoding="utf-8")

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
        return subprocess.run([sys.executable, str(BT), "origin", self.remote, "--repo", self.repo,
                               "--config", str(self.cfg), "--shards", "2", *extra],
                              input=line + "\n", capture_output=True, text=True)

    def worktrees(self) -> int:
        return len([l for l in _g(self.repo, "worktree", "list", "--porcelain").splitlines() if l.startswith("worktree ")])

    def test_untriggered_push_runs_nothing(self):
        self.write("cos-feedback/a.md", "b\n")
        self.commit("feedback only")
        r = self.judge()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("no suite run", r.stderr)

    def test_triggered_green_tip_passes_sharded_and_cleans_up(self):
        self.write("hooks/x.py", "x = 2\n")
        self.commit("hook edit")
        r = self.judge()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("ok   fake shard 1/2", r.stderr)
        self.assertIn("ok   fake shard 2/2", r.stderr)
        self.assertEqual(self.worktrees(), 1, "the temporary worktree is removed")

    def test_red_tip_refuses_and_the_pushed_bytes_are_tested_not_the_worktree(self):
        self.write("hooks/x.py", "x = 3\n")
        self.commit("hook edit")
        self.write("FAIL", "uncommitted\n")            # dirty worktree: not what is pushed
        self.assertEqual(self.judge().returncode, 0)
        self.commit("commit the failure")
        r = self.judge()
        self.assertEqual(r.returncode, 1)
        self.assertIn("[bus-tests] PUSH REFUSED", r.stderr)
        self.assertIn("FAIL marker in the tested tree", r.stderr)
        self.assertEqual(self.worktrees(), 1)

    def test_unprotected_ref_and_deletion_are_not_judged(self):
        self.write("hooks/x.py", "x = 4\n")
        self.write("FAIL", "x\n")
        head = self.commit("red")
        self.assertEqual(self.judge(f"refs/heads/side {head} refs/heads/side {Z}").returncode, 0)
        self.assertEqual(self.judge(f"(delete) {Z} refs/heads/master {self.base}").returncode, 0)
        self.assertEqual(self.judge(f"refs/heads/side {head} refs/heads/side {Z}", "--protect", "side").returncode, 1)

    def test_unknown_base_runs_everything_and_all_flag_forces(self):
        self.write("cos-feedback/a.md", "c\n")
        self.write("FAIL", "x\n")
        head = self.commit("red but untriggered")
        self.assertEqual(self.judge().returncode, 0)
        self.assertEqual(self.judge(None, "--all").returncode, 1)
        self.assertEqual(self.judge(f"refs/heads/master {head} refs/heads/master {'1' * 40}").returncode, 1)

    def test_missing_interpreter_and_bad_lines_refuse(self):
        self.cfg.write_text(json.dumps({"suites": [{"name": "n", "argv": ["no-such-interpreter-xyz", "a"]}]}),
                            encoding="utf-8")
        r = self.judge(None, "--all")
        self.assertEqual(r.returncode, 1)
        self.assertIn("interpreter not found", r.stderr)
        self.assertEqual(self.judge("garbage").returncode, 2)

    def test_real_push_from_a_linked_worktree(self):
        # git exports GIT_DIR to a hook run from a linked worktree; the suite must not inherit it.
        hooks = Path(_g(self.repo, "rev-parse", "--path-format=absolute", "--git-common-dir")) / "hooks"
        hooks.mkdir(exist_ok=True)
        py = Path(sys.executable).as_posix()
        (hooks / "pre-push").write_text(
            f'#!/bin/sh\nexec "{py}" "{BT.as_posix()}" --config "{self.cfg.as_posix()}" --shards 2 "$@"\n',
            encoding="utf-8", newline="\n")
        os.chmod(hooks / "pre-push", 0o755)
        wt = str(Path(self._tmp.name) / "linked")
        _g(self.repo, "worktree", "add", "-q", "-b", "wt", wt, "master")
        Path(wt, "hooks", "x.py").write_text("x = 5\n", encoding="utf-8")
        _g(wt, "add", "--", "hooks/x.py")
        _g(wt, "commit", "-q", "-m", "green")
        ok = subprocess.run(["git", "-C", wt, "push", "-q", "origin", "HEAD:refs/heads/master"], capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        Path(wt, "FAIL").write_text("x\n", encoding="utf-8")
        _g(wt, "add", "--", "FAIL")
        Path(wt, "hooks", "x.py").write_text("x = 6\n", encoding="utf-8")
        _g(wt, "add", "--", "hooks/x.py")
        _g(wt, "commit", "-q", "-m", "red")
        bad = subprocess.run(["git", "-C", wt, "push", "-q", "origin", "HEAD:refs/heads/master"], capture_output=True, text=True)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("[bus-tests] PUSH REFUSED", bad.stderr)


# Fixture checkers for the drift layer. Each reads its pin at the TESTED tree's HEAD, exactly like the bus checkers
# (tools/check_universal_manifest.py --treeish HEAD, tools/check_adoption_ledger.py --current --treeish HEAD).
FAKE_MANIFEST_CHECK = """import json, os, subprocess, sys
assert "GIT_DIR" not in os.environ
def g(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True, check=True).stdout.strip()
m = json.loads(g("show", "HEAD:pins/manifest.json"))
for row in m["subjectFiles"]:
    if g("rev-parse", "HEAD:" + row["path"]) != row["gitBlobOid"]:
        print("MANIFEST_SUBJECT_MISMATCH"); sys.exit(1)
if m.get("broken"):
    print("MANIFEST_SELF_MISMATCH"); sys.exit(1)
print("MANIFEST_PASS")
"""
FAKE_CENSUS_CHECK = """import json, subprocess, sys
NON_PROJECT = {"specs/portable.md"}
def g(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True, check=True).stdout.strip()
c = json.loads(g("show", "HEAD:pins/census.json"))
for row in c["projects"]:
    if g("rev-parse", "HEAD:" + row["specPath"]) != row["gitBlobOid"]:
        print("FAIL: PROJECT_SPEC_DRIFT", file=sys.stderr); sys.exit(1)
top = {p for p in g("ls-tree", "-r", "--name-only", "HEAD", "--", "specs").splitlines() if "/" not in p[6:]}
if {r["specPath"] for r in c["projects"]} != top - NON_PROJECT:
    print("FAIL: PROJECT_CLOSED_SET_MISMATCH", file=sys.stderr); sys.exit(1)
print("PASS")
"""

NOOP_SUITES = [{"name": "noop", "argv": ["{python}", "-c", "pass"]}]


class BusDrift(unittest.TestCase):
    """The bus writers' pre-push layer runs a pin's CI checker when the push touches a file that pin covers,
    and refuses drift with the approved refresh command; it never refreshes and never judges untouched pins."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        t = Path(self._tmp.name)
        self.repo = str(t / "work")
        subprocess.run(["git", "init", "-q", "-b", "master", self.repo], check=True)
        self.write("t/check_manifest.py", FAKE_MANIFEST_CHECK)
        self.write("t/check_census.py", FAKE_CENSUS_CHECK)
        self.write("README.md", "readme\n")
        self.write("specs/a.md", "a\n")
        self.write("specs/portable.md", "portable\n")
        self.write("specs/a/cards.md", "card\n")
        self.write("TRAPS.md", "trap\n")
        self.commit("content")
        self.repin_manifest()
        self.repin_census()
        self.base = self.commit("pins")
        self.cfg = t / "bus-tests.json"
        self.cfg.write_text(json.dumps({"trigger": ["nothing/"], "suites": NOOP_SUITES, "drift": [
            {"name": "manifest", "pin": "pins/manifest.json", "covers": "manifest-subjects", "also": [],
             "argv": ["{python}", "t/check_manifest.py"],
             "refresh": {"MANIFEST_SUBJECT_MISMATCH": "run refresh-manifest --candidate {sha} then commit {pin}"}},
            {"name": "census", "pin": "pins/census.json", "covers": "census-specs", "also": ["t/check_census.py"],
             "argv": ["{python}", "t/check_census.py"],
             "refresh": {"PROJECT_SPEC_DRIFT": "run refresh-census at {sha12}",
                         "PROJECT_CLOSED_SET_MISMATCH": "no refresh can fix this"}}]}), encoding="utf-8")

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

    def oid(self, rel: str) -> str:
        return _g(self.repo, "hash-object", rel)

    def repin_manifest(self, extra: dict | None = None):
        self.write("pins/manifest.json", json.dumps(
            {"subjectFiles": [{"path": "README.md", "gitBlobOid": self.oid("README.md")}], **(extra or {})}))

    def repin_census(self):
        self.write("pins/census.json", json.dumps({"projects": [{"specPath": "specs/a.md",
                                                                  "gitBlobOid": self.oid("specs/a.md")}]}))

    def judge(self, *extra: str, base: str | None = None) -> subprocess.CompletedProcess:
        head = _g(self.repo, "rev-parse", "HEAD")
        line = f"refs/heads/master {head} refs/heads/master {base or self.base}"
        return subprocess.run([sys.executable, str(BT), "origin", "x", "--repo", self.repo,
                               "--config", str(self.cfg), *extra],
                              input=line + "\n", capture_output=True, text=True)

    def test_untouched_pins_run_nothing_even_when_master_already_drifted(self):
        self.write("TRAPS.md", "trap 2\n")
        self.write("specs/a/cards.md", "card 2\n")       # under specs/, but no pin covers it
        self.write("specs/portable.md", "portable 2\n")  # a classified non-project spec
        self.commit("append-only writer")
        r = self.judge()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("no pinned path touched; no suite run", r.stderr)
        self.write("specs/a.md", "a drifted\n")
        drifted = self.commit("someone else's unrefreshed spec edit")
        self.write("TRAPS.md", "trap 3\n")
        self.commit("next writer")
        r = self.judge(base=drifted)
        self.assertEqual(r.returncode, 0, "a writer is never refused for drift it did not touch\n" + r.stderr)

    def test_readme_edit_refuses_with_the_refresh_command_and_refreshed_tip_passes(self):
        self.write("README.md", "readme 2\n")
        head = self.commit("readme edit")
        r = self.judge()
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("drift manifest FAILED", r.stderr)
        self.assertIn(f"MANIFEST_SUBJECT_MISMATCH -- run refresh-manifest --candidate {head} then commit "
                      f"pins/manifest.json", r.stderr)
        self.assertEqual(_g(self.repo, "rev-parse", "HEAD"), head, "the hook never refreshes or commits")
        self.assertEqual(_g(self.repo, "status", "--porcelain"), "")
        self.repin_manifest()
        self.commit("refresh")
        r = self.judge()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("ok   drift manifest", r.stderr)
        self.assertNotIn("drift census", r.stderr, "only the pin whose coverage was touched runs")

    def test_project_spec_edit_refuses_drift_and_new_top_level_spec_refuses_closed_set(self):
        self.write("specs/a.md", "a 2\n")
        head = self.commit("spec edit")
        r = self.judge()
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn(f"PROJECT_SPEC_DRIFT -- run refresh-census at {head[:12]}", r.stderr)
        self.repin_census()
        refreshed = self.commit("census refresh")
        self.assertEqual(self.judge().returncode, 0)
        self.write("specs/b.md", "new project\n")
        self.commit("new spec")
        r = self.judge(base=refreshed)                     # the range touches only the new spec
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("PROJECT_CLOSED_SET_MISMATCH -- no refresh can fix this", r.stderr)

    def test_coverage_is_read_at_the_pushed_tip(self):
        self.write("TRAPS.md", "now pinned\n")
        self.write("pins/manifest.json", json.dumps({"subjectFiles": [
            {"path": "README.md", "gitBlobOid": self.oid("README.md")},
            {"path": "TRAPS.md", "gitBlobOid": "0" * 40}]}))
        self.commit("pin TRAPS.md with a wrong oid")
        r = self.judge()
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("MANIFEST_SUBJECT_MISMATCH", r.stderr)

    def test_unknown_failure_is_refused_without_a_refresh_and_unreadable_pin_runs(self):
        self.repin_manifest({"broken": True})
        self.commit("hand edit of the pin")
        r = self.judge()
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("not a drift any approved refresh covers", r.stderr)
        self.write("pins/manifest.json", "{not json")
        self.write("README.md", "readme 3\n")
        self.commit("unreadable pin")
        self.assertEqual(self.judge(base=_g(self.repo, "rev-parse", "HEAD~1")).returncode, 1)

    def test_unknown_base_all_flag_absent_pin_and_config(self):
        self.write("README.md", "readme 4\n")
        self.commit("drift")
        self.assertEqual(self.judge(base="1" * 40).returncode, 1, "unknown base runs every present pin")
        _g(self.repo, "rm", "-q", "pins/manifest.json")
        self.commit("pin removed")
        r = self.judge(base="1" * 40)
        self.assertEqual(r.returncode, 0, r.stderr)        # no pin at the tip: nothing to drift from
        self.assertIn("drift check census", r.stderr)
        self.assertEqual(self.judge("--all").returncode, 0)
        self.cfg.write_text(json.dumps({"trigger": ["nothing/"], "suites": NOOP_SUITES, "drift": []}),
                            encoding="utf-8")
        self.write("specs/a.md", "a 3\n")
        self.commit("drift with checks off")
        self.assertEqual(self.judge().returncode, 0)
        self.cfg.write_text(json.dumps({"drift": [{"name": "x", "pin": "p", "covers": "nope", "argv": ["a"]}]}),
                            encoding="utf-8")
        self.assertEqual(self.judge().returncode, 2)

    def test_defaults_name_real_bus_checkers_pins_and_refresh_tools(self):
        spec = importlib.util.spec_from_file_location("bus_tests_hook", BT)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        bus = HERE.parent
        self.assertEqual([e["name"] for e in mod.DEFAULT_DRIFT], ["r45-manifest", "r26-census"])
        for e in mod.DEFAULT_DRIFT:
            self.assertTrue((bus / e["pin"]).is_file(), e["pin"])
            self.assertTrue((bus / e["argv"][1]).is_file(), e["argv"])
            for text in e["refresh"].values():
                for word in text.split():
                    if word.startswith("tools/") and word.endswith(".py"):
                        self.assertTrue((bus / word).is_file(), word)
        workflows = {"r45-manifest": "provider-capacity-governor.yml", "r26-census": "adoption-ledger.yml"}
        for e in mod.DEFAULT_DRIFT:
            text = (bus / ".github" / "workflows" / workflows[e["name"]]).read_text(encoding="utf-8")
            self.assertIn(e["argv"][1], text, "the drift check is a checker CI runs")


if __name__ == "__main__":
    unittest.main(verbosity=1)
