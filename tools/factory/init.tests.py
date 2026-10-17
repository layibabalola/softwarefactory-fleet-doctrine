#!/usr/bin/env python3
"""Tests for `pin-runner.py init --profile <name>`.   python tools/factory/init.tests.py

A throwaway bus holds the REAL registry, profile and every file the `base` profile names (byte-for-byte, LF), so
these tests prove the profile that ships, not a fixture of it. A throwaway consumer repository (with a bare
origin) is then made a whole factory in one command, and every piece is exercised the way it will run:
the Claude hook commands exactly as written into .claude/settings.json, the pre-push file through a real
`git push`, the rule-map config through the pinned check-rule-tags. Negative controls: every refusal writes
nothing; a project file is never overwritten (HAND step, exit 4); malformed profiles refuse.
"""
from __future__ import annotations

import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

FACTORY = Path(__file__).resolve().parent
BUS_ROOT = FACTORY.parent.parent
REAL_REGISTRY = json.loads((FACTORY / "registry.json").read_text(encoding="utf-8"))
PROFILE = REAL_REGISTRY["profiles"]["base"]


def git(repo, *a: str, env: dict | None = None) -> str:
    return subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@example.invalid", "-c", "user.name=t",
                           "-c", "core.autocrlf=false", *a], check=True, capture_output=True, text=True, env=env).stdout.strip()


def lf(p: Path) -> bytes:
    return p.read_bytes().replace(b"\r\n", b"\n")


def tree_digest(root: Path) -> dict[str, str]:
    """Every file under root (the hooks dir included, objects excluded) -> sha256: proof that nothing was written."""
    out = {}
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root).as_posix()
        if p.is_file() and not rel.startswith((".git/objects", ".git/logs")) and rel not in (".git/index", ".git/ORIG_HEAD"):
            out[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


class _Init(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        t = Path(self._tmp.name)
        self.t, self.bus, self.proj, self.home = t, t / "bus", t / "My Project", t / "home"
        self.origin, self.elsewhere, self.cache = t / "origin.git", t / "elsewhere", t / "cache"
        for d in (self.bus, self.elsewhere, self.home / ".claude"):
            d.mkdir(parents=True)
        files = {"tools/factory/pin-runner.py", "tools/factory/registry.json", "hooks/pre-push.factory.sh"}
        files |= {REAL_REGISTRY["tools"][n]["path"] for n in PROFILE["tools"]}
        files |= set(PROFILE.get("seeds", {}).values())
        for f in sorted(files):
            (self.bus / f).parent.mkdir(parents=True, exist_ok=True)
            (self.bus / f).write_bytes(lf(BUS_ROOT / f))
        self.bus_files = files
        subprocess.run(["git", "init", "-q", str(self.bus)], check=True)
        git(self.bus, "add", "-A")
        git(self.bus, "commit", "-qm", "bus")
        self.c1 = git(self.bus, "rev-parse", "HEAD")
        subprocess.run(["git", "init", "-q", "--bare", str(self.origin)], check=True)
        subprocess.run(["git", "init", "-q", "-b", "master", str(self.proj)], check=True)
        git(self.proj, "remote", "add", "origin", str(self.origin))
        (self.proj / "CLAUDE.md").write_text("# rules\n\n- never force-push master\n- add exact paths only\n", encoding="utf-8")
        git(self.proj, "add", "--", "CLAUDE.md")
        git(self.proj, "commit", "-qm", "base")
        git(self.proj, "push", "-q", "origin", "master")
        self.runner = self.proj / "factory-pins" / "pin-runner.py"

    def tearDown(self):
        self._tmp.cleanup()

    def env(self, **extra) -> dict:
        e = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FACTORY_", "CLAUDE_"))}
        e.update(HOME=str(self.home), USERPROFILE=str(self.home), FACTORY_PINS_CACHE=str(self.cache), **extra)
        return e

    def init(self, *extra: str, runner: Path | None = None, profile: str = "base", root: Path | None = None):
        return subprocess.run([sys.executable, str(runner or self.bus / "tools/factory/pin-runner.py"), "init", "--profile", profile,
                               "--commit", self.c1, "--reviewer", "tester", "--reason", "fixture", "--project-root",
                               str(root or self.proj), "--bus", str(self.bus), "--date", "2026-10-17", *extra],
                              capture_output=True, text=True, cwd=str(self.elsewhere), env=self.env(), stdin=subprocess.DEVNULL)

    def settings(self) -> dict:
        return json.loads((self.proj / ".claude" / "settings.json").read_text(encoding="utf-8"))

    def hook(self, event: str, payload: dict, tool: str | None = None) -> subprocess.CompletedProcess:
        """Run a hook command exactly as init wrote it into .claude/settings.json."""
        cmds = [h["command"] for g in self.settings()["hooks"][event] for h in g["hooks"]
                if tool is None or f" run {tool}" in h["command"]]
        self.assertEqual(len(cmds), 1, cmds)
        argv = shlex.split(cmds[0].replace("$CLAUDE_PROJECT_DIR", self.proj.as_posix()))
        self.assertEqual(argv[:2], ["python", "-I"])
        return subprocess.run([sys.executable, *argv[1:]], input=json.dumps(payload), capture_output=True, text=True,
                              cwd=str(self.proj), env=self.env(CLAUDE_PROJECT_DIR=str(self.proj)))

    def push(self, *a: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-C", str(self.proj), "push", "origin", *a], capture_output=True, text=True,
                              env=self.env(), stdin=subprocess.DEVNULL)

    def commit_listed(self, out: str) -> None:
        line = next(l for l in out.splitlines() if l.startswith("COMMIT"))
        git(self.proj, "add", "--", *shlex.split(line.split("git add -- ", 1)[1]))
        git(self.proj, "commit", "-qm", "factory: init --profile base")


class Init(_Init):
    def test_one_command_installs_a_whole_working_factory(self):
        p = self.init()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("INIT profile base", p.stdout)
        self.assertIn("as project 'my-project'", p.stdout)
        # pins: the runner adopted, every profile tool pinned at the commit, each blob = git's object
        pins = json.loads((self.proj / "factory-pins" / "factory-pins.json").read_text(encoding="utf-8"))
        self.assertEqual(sorted(pins["tools"]), sorted(PROFILE["tools"]))
        for n, e in pins["tools"].items():
            self.assertEqual((e["commit"], e["blob"], e["reviewer"]), (self.c1, git(self.bus, "rev-parse", f"{self.c1}:{e['path']}"), "tester"))
        self.assertEqual(self.runner.read_bytes(), lf(BUS_ROOT / "tools/factory/pin-runner.py"))
        v = subprocess.run([sys.executable, str(self.runner), "verify"], capture_output=True, text=True, cwd=str(self.proj), env=self.env())
        self.assertEqual(v.returncode, 0, v.stdout + v.stderr)
        # data: seed, stub, rule-tags config, and the map the pinned check-rule-tags emitted from CLAUDE.md
        seed = PROFILE["seeds"]["factory-pins/session-checkpoint.config.json"]
        self.assertEqual((self.proj / "factory-pins/session-checkpoint.config.json").read_bytes(), lf(BUS_ROOT / seed))
        stub = json.loads((self.proj / "factory-pins/product-throughput-classes.json").read_text(encoding="utf-8"))
        self.assertEqual((stub["schema"], stub["projects"][0]["name"]), ("fleet/product-throughput-classes/v1", "my-project"))
        rmap = json.loads((self.proj / "factory-pins/rule-map.json").read_text(encoding="utf-8"))
        self.assertEqual(sorted(r["text_head"] for r in rmap["rules"].values()), ["add exact paths only", "never force-push master"])
        self.assertTrue(all(r["kind"] == "prose" for r in rmap["rules"].values()))
        r = subprocess.run([sys.executable, "-I", str(self.runner), "run", "check-rule-tags", "--", "--config",
                            "factory-pins/rule-tags.config.json", "--project", "my-project", "--report"],
                           capture_output=True, text=True, cwd=str(self.proj), env=self.env())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("rule-tags my-project: 2 rules, 0 backed, 2 prose", r.stdout)
        # Claude hooks, run as written: the checkpoint hook writes and lists a checkpoint; the guard refuses
        s = self.hook("SessionStart", {"hook_event_name": "SessionStart", "session_id": "sess0001", "cwd": str(self.proj)})
        self.assertEqual((s.returncode, s.stderr), (0, ""))
        (self.proj / "wip.txt").write_text("w\n", encoding="utf-8")
        s = self.hook("Stop", {"hook_event_name": "Stop", "session_id": "sess0001", "cwd": str(self.proj)})
        self.assertEqual(s.returncode, 0, s.stderr)
        self.assertIn("checkpoint: 1 uncommitted file(s)", s.stdout)
        self.assertIn("  - wip.txt", (self.home / ".claude/session-checkpoints/My-Project/SESSION-sess0001.md").read_text(encoding="utf-8"))
        (self.proj / "wip.txt").unlink()
        s = self.hook("SessionStart", {"hook_event_name": "SessionStart", "session_id": "sess0002", "cwd": str(self.proj)})
        self.assertIn("SESSION-sess0001.md", s.stdout)
        bad = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": "git add -A"}}
        self.assertEqual(self.hook("PreToolUse", bad, "exact-path-add").returncode, 2)
        good = {**bad, "tool_input": {"command": "git add -- CLAUDE.md"}}
        self.assertEqual(self.hook("PreToolUse", good, "exact-path-add").returncode, 0)
        self.assertEqual(self.hook("PreToolUse", {**bad, "tool_input": {"command": "git status"}}, "git-optional-locks").returncode, 2)
        # git: commit what init listed, push it; a non-fast-forward and a tool copy are then refused by the layers
        self.commit_listed(p.stdout)
        r = self.push("master")
        self.assertEqual(r.returncode, 0, r.stderr)
        (self.proj / "tools").mkdir()
        (self.proj / "tools" / "session-checkpoint.py").write_text("print('my own copy')\n", encoding="utf-8")
        git(self.proj, "add", "--", "tools/session-checkpoint.py")
        git(self.proj, "commit", "-qm", "a hand-built copy")
        r = self.push("master")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("[no-unpinned-tool] PUSH REFUSED", r.stderr)
        git(self.proj, "reset", "-q", "--hard", "HEAD~2")
        (self.proj / "other.txt").write_text("o\n", encoding="utf-8")
        git(self.proj, "add", "--", "other.txt")
        git(self.proj, "commit", "-qm", "diverged")
        r = self.push("--force", "master")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("[ff-only] PUSH REFUSED", r.stderr)
        # idempotent: the same init again writes nothing
        git(self.proj, "reset", "-q", "--hard", "origin/master")
        before = tree_digest(self.proj)
        p2 = self.init()
        self.assertEqual(p2.returncode, 0, p2.stdout + p2.stderr)
        self.assertIn("NO-OP profile base", p2.stdout)
        self.assertNotIn("COMMIT", p2.stdout)
        self.assertEqual(tree_digest(self.proj), before)

    def test_throughput_stub_is_consumable(self):
        pwsh = shutil.which("pwsh")
        if pwsh is None:
            self.skipTest("no pwsh")
        self.assertEqual(self.init().returncode, 0)
        r = subprocess.run([pwsh, "-NoProfile", "-File", str(BUS_ROOT / "tools/Get-ProductThroughput.ps1"), "-Repo", str(self.proj),
                            "-Project", "my-project", "-ClassConfig", str(self.proj / "factory-pins/product-throughput-classes.json"),
                            "-Lines"], capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=180)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("FAILED", r.stdout)

    def test_bootstrap_profile_installs_from_the_verified_blob(self):
        bash = next((Path(p) for p in (shutil.which("bash"), shutil.which("sh")) if p and "system32" not in p.lower()), None)
        if bash is None:
            self.skipTest("no POSIX shell")
        r = subprocess.run([str(bash), (FACTORY / "bootstrap.sh").as_posix(), self.bus.as_posix(), self.c1, "profile:base",
                            "tester", "fixture", self.proj.as_posix()], capture_output=True, text=True, cwd=str(self.elsewhere),
                           env=self.env(PYTHON=sys.executable), stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("INIT profile base", r.stdout)

    def test_list_names_the_profiles(self):
        r = subprocess.run([sys.executable, str(self.bus / "tools/factory/pin-runner.py"), "list", "--bus", str(self.bus)],
                           capture_output=True, text=True, cwd=str(self.elsewhere), env=self.env())
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("profile base\tsession-checkpoint,exact-path-add", r.stdout)


class NeverOverwrites(_Init):
    def test_existing_files_are_kept_and_conflicts_are_hand_steps(self):
        hooks = Path(git(self.proj, "rev-parse", "--path-format=absolute", "--git-path", "hooks"))
        hooks.mkdir(parents=True, exist_ok=True)
        (hooks / "pre-push").write_text("#!/bin/sh\ngit lfs pre-push \"$@\"\n", encoding="utf-8")
        (self.proj / ".claude").mkdir()
        mine = {"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": "python tools/session-checkpoint.py"}]}]},
                "permissions": {"allow": ["Bash(ls)"]}}
        (self.proj / ".claude/settings.json").write_text(json.dumps(mine), encoding="utf-8")
        (self.proj / "factory-pins").mkdir()
        (self.proj / "factory-pins/session-checkpoint.config.json").write_text('{"schema": "session-checkpoint.v1"}\n', encoding="utf-8")
        (self.home / ".claude/settings.json").write_text(json.dumps(
            {"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "python ~/.claude/hooks/session-checkpoint.py"}]}]}}),
            encoding="utf-8")
        before_hook = (hooks / "pre-push").read_bytes()
        p = self.init()
        self.assertEqual(p.returncode, 4, p.stdout + p.stderr)
        hand = [l for l in p.stdout.splitlines() if l.startswith("HAND:")]
        self.assertEqual(len(hand), 3, hand)
        self.assertTrue(any("already runs session-checkpoint on SessionStart" in h for h in hand), hand)
        self.assertTrue(any("the user settings" in h and "on Stop" in h for h in hand), hand)
        self.assertTrue(any("pre-push exists with other layers" in h for h in hand), hand)
        self.assertEqual((hooks / "pre-push").read_bytes(), before_hook)
        self.assertEqual((self.proj / "factory-pins/session-checkpoint.config.json").read_text(encoding="utf-8"),
                         '{"schema": "session-checkpoint.v1"}\n')
        s = self.settings()
        self.assertEqual(s["permissions"], mine["permissions"])
        self.assertEqual(s["hooks"]["SessionStart"], mine["hooks"]["SessionStart"])        # untouched, not doubled
        self.assertNotIn("Stop", s["hooks"])                                                  # the user level runs it
        self.assertEqual(len(s["hooks"]["PreToolUse"][0]["hooks"]), 2)                       # the guards were added
        # the person chains the layers and switches to the pinned hook; the same init then completes
        (hooks / "pre-push").write_bytes(before_hook + lf(BUS_ROOT / "hooks/pre-push.factory.sh"))
        s["hooks"]["SessionStart"][0]["hooks"][0]["command"] = (
            'python -I "$CLAUDE_PROJECT_DIR/factory-pins/pin-runner.py" run session-checkpoint -- '
            '--config "$CLAUDE_PROJECT_DIR/factory-pins/session-checkpoint.config.json"')
        (self.proj / ".claude/settings.json").write_text(json.dumps(s), encoding="utf-8")
        (self.home / ".claude/settings.json").unlink()
        p = self.init()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(len(self.settings()["hooks"]["SessionStart"][0]["hooks"]), 1)


class Refusals(_Init):
    def assert_refused_and_unwritten(self, p, text: str, before: dict):
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertIn(text, p.stderr)
        self.assertEqual(tree_digest(self.proj), before)

    def test_refusals_write_nothing(self):
        before = tree_digest(self.proj)
        self.assert_refused_and_unwritten(self.init(profile="nope"), "unknown profile 'nope'", before)
        sub = self.t / "sub-of-nothing"
        sub.mkdir()
        self.assert_refused_and_unwritten(self.init(root=sub), "top level of a git repository", before)
        tampered = self.elsewhere / "pin-runner.py"
        tampered.write_bytes(lf(BUS_ROOT / "tools/factory/pin-runner.py") + b"\n# edited\n")
        self.assert_refused_and_unwritten(self.init(runner=tampered), "not byte-identical", before)
        (self.proj / ".claude").mkdir()
        (self.proj / ".claude/settings.json").write_text("{not json", encoding="utf-8")
        before = tree_digest(self.proj)
        self.assert_refused_and_unwritten(self.init(), "settings.json is not readable JSON", before)

    def test_malformed_profiles_refuse_and_write_nothing(self):
        reg_path = self.bus / "tools/factory/registry.json"
        good = json.loads(reg_path.read_text(encoding="utf-8"))
        before = tree_digest(self.proj)
        hook = {"event": "Stop", "tool": "session-checkpoint"}
        cases = [
            {"tools": ["no-such-tool"]},
            {"tools": []},
            {"seeds": {"../outside.json": "tools/factory/registry.json"}},
            {"seeds": {"factory-pins/factory-pins.json": "tools/factory/registry.json"}},
            {"claude_hooks": [{**hook, "tool": "check-doc-size"}]},
            {"claude_hooks": [{**hook, "args": ["--config", "a b"]}]},
            {"claude_hooks": [{**hook, "args": ['"$(rm -rf ~)"']}]},
            {"claude_hooks": [{**hook, "event": "Whenever"}]},
            {"claude_hooks": [{**hook, "timeout": 0}]},
            {"git_hooks": [{"hook": "post-merge", "path": "hooks/pre-push.factory.sh", "marker": "#"}]},
            {"git_hooks": [{"hook": "pre-push", "path": "hooks/pre-push.factory.sh"}]},
            {"rule_map": True, "tools": ["session-checkpoint"]},
            {"throughput_stub": "yes"},
            {"surprise": 1},
        ]
        for bad in cases:
            reg = json.loads(json.dumps(good))
            reg["profiles"]["base"].update(bad)
            reg_path.write_text(json.dumps(reg), encoding="utf-8")
            git(self.bus, "commit", "-qam", "bad profile")
            self.c1 = git(self.bus, "rev-parse", "HEAD")
            with self.subTest(bad=bad):
                p = self.init()
                self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
                self.assertIn("profile 'base'", p.stderr)
                self.assertEqual(tree_digest(self.proj), before)

    def test_a_failing_rule_map_tool_refuses_before_any_write(self):
        crt = self.bus / REAL_REGISTRY["tools"]["check-rule-tags"]["path"]
        crt.write_bytes(b"import sys\nopen('ran-here.marker', 'w').write('x')\nsys.exit(3)\n")
        git(self.bus, "commit", "-qam", "a broken check-rule-tags")
        self.c1 = git(self.bus, "rev-parse", "HEAD")
        before = tree_digest(self.proj)
        p = self.init()
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertIn("check-rule-tags --emit-map exited 3", p.stderr)
        self.assertEqual(tree_digest(self.proj), before)
        self.assertFalse((self.elsewhere / "ran-here.marker").exists(), "the emit runs in a private directory, not the caller's cwd")

    def test_substituted_tool_bytes_never_run(self):
        """git returning bytes that are not the tree's object for check-rule-tags: refused before it can run."""
        if os.name == "nt":
            self.skipTest("python's subprocess resolves git.exe only; a .cmd shim would not be what runs")
        shim = self.t / "shim"
        shim.mkdir()
        real = shutil.which("git")
        target = REAL_REGISTRY["tools"]["check-rule-tags"]["path"]
        (shim / "git").write_text(f'#!/bin/sh\ncase "$*" in *"cat-file blob"*"{target}"*) '
                                  f'echo \'open("pwned.marker","w").write("x")\'; exit 0;; esac\nexec "{real}" "$@"\n', encoding="utf-8")
        (shim / "git").chmod(0o755)
        env = self.env(PATH=str(shim) + os.pathsep + os.environ["PATH"])
        found = shutil.which("git", path=env["PATH"])
        if not (found and Path(found).resolve().parent == shim.resolve()):
            self.skipTest("the git shim is not what `git` resolves to here")
        before = tree_digest(self.proj)
        p = subprocess.run([sys.executable, str(self.bus / "tools/factory/pin-runner.py"), "init", "--profile", "base", "--commit",
                            self.c1, "--reviewer", "t", "--reason", "r", "--project-root", str(self.proj), "--bus", str(self.bus)],
                           capture_output=True, text=True, cwd=str(self.elsewhere), env=env, stdin=subprocess.DEVNULL)
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertIn("are not object", p.stderr)
        self.assertEqual(tree_digest(self.proj), before)
        self.assertFalse(any(self.t.rglob("pwned.marker")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
