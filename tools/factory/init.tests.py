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

sys.dont_write_bytecode = True   # importing pin-runner.py in a test must not leave __pycache__ in tools/factory

FACTORY = Path(__file__).resolve().parent
BUS_ROOT = FACTORY.parent.parent
REAL_REGISTRY = json.loads((FACTORY / "registry.json").read_text(encoding="utf-8"))
PROFILE = REAL_REGISTRY["profiles"]["base"]


# Hermetic git: no system or global config of the host (signing, templates, hooksPath, autocrlf) reaches a fixture.
_GITCFG = Path(tempfile.mkdtemp(prefix="factory-tests-gitcfg-")) / "gitconfig"
_GITCFG.write_text("", encoding="utf-8")
HERMETIC = {"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": str(_GITCFG)}


def base_env() -> dict:
    return {**{k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FACTORY_", "CLAUDE_", "DOCTRINE_"))}, **HERMETIC}


def git(repo, *a: str, env: dict | None = None) -> str:
    return subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@example.invalid", "-c", "user.name=t",
                           "-c", "core.autocrlf=false", *a], check=True, capture_output=True, text=True, env=env or base_env()).stdout.strip()


def git_blob(repo: Path, rev: str, path: str) -> bytes:
    return subprocess.run(["git", "-C", str(repo), "cat-file", "blob", f"{rev}:{path}"], check=True, capture_output=True,
                          env=base_env()).stdout


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
        subprocess.run(["git", "init", "-q", str(self.bus)], check=True, env=base_env())
        git(self.bus, "add", "-A")
        git(self.bus, "commit", "-qm", "bus")
        self.c1 = git(self.bus, "rev-parse", "HEAD")
        subprocess.run(["git", "init", "-q", "--bare", str(self.origin)], check=True, env=base_env())
        subprocess.run(["git", "init", "-q", "-b", "master", str(self.proj)], check=True, env=base_env())
        git(self.proj, "remote", "add", "origin", str(self.origin))
        (self.proj / "CLAUDE.md").write_text("# rules\n\n- never force-push master\n- add exact paths only\n", encoding="utf-8")
        git(self.proj, "add", "--", "CLAUDE.md")
        git(self.proj, "commit", "-qm", "base")
        git(self.proj, "push", "-q", "origin", "master")
        self.runner = self.proj / "factory-pins" / "pin-runner.py"

    def tearDown(self):
        self._tmp.cleanup()

    def env(self, **extra) -> dict:
        e = base_env()
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
                            "-Lines"], capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=180, env=self.env())
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
        self.commit_listed(r.stdout)                       # what init lists is enough for the pushed commit
        p = self.push("master")
        self.assertEqual(p.returncode, 0, p.stderr)

    def test_a_hand_placed_runner_is_listed_for_the_commit(self):
        """Review round 1 (Claude key, BLOCKER): an ADOPTED runner was missing from the COMMIT line, so the first push
        was refused by the very pre-push hook init had installed."""
        (self.proj / "factory-pins").mkdir()
        self.runner.write_bytes(git_blob(self.bus, self.c1, "tools/factory/pin-runner.py"))   # git show <sha>:... > it
        p = self.init(runner=self.runner)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("adopted runner", p.stdout)
        self.assertIn("factory-pins/pin-runner.py", next(l for l in p.stdout.splitlines() if l.startswith("COMMIT")))
        self.commit_listed(p.stdout)
        r = self.push("master")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("COMMIT", self.init().stdout)    # everything init manages is now in HEAD

    def test_an_existing_consumer_adopts_without_a_push_lockout(self):
        """Review round 1 (Claude key): a consumer whose master already pins other tools judged the new layers with
        master's pins, which lack them, and every push -- the adoption push included -- was refused."""
        r = subprocess.run([sys.executable, str(self.bus / "tools/factory/pin-runner.py"), "install", "check-rule-tags",
                            "--commit", self.c1, "--reviewer", "t", "--reason", "r", "--project-root", str(self.proj),
                            "--bus", str(self.bus)], capture_output=True, text=True, env=self.env(), stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        git(self.proj, "add", "--", "factory-pins")
        git(self.proj, "commit", "-qm", "an earlier consumer of one tool")
        self.assertEqual(self.push("master").returncode, 0)
        p = self.init()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.commit_listed(p.stdout)
        for ref in ("HEAD:refs/heads/adopt-factory", "master"):
            r = self.push(ref)
            self.assertEqual(r.returncode, 0, f"{ref}: {r.stderr}")
        # once master pins the layers, master judges: a branch can no longer re-pin its own judge
        (self.proj / "tools").mkdir()
        (self.proj / "tools" / "session-checkpoint.py").write_text("print('copy')\n", encoding="utf-8")
        git(self.proj, "add", "--", "tools/session-checkpoint.py")
        git(self.proj, "commit", "-qm", "a copy")
        r = self.push("HEAD:refs/heads/sneak")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("[no-unpinned-tool] PUSH REFUSED", r.stderr)

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
        self.assertEqual(len(hand), 2, hand)
        self.assertTrue(any("session-checkpoint already runs on SessionStart as" in h and "tools/session-checkpoint.py" in h
                            for h in hand), hand)
        # the user settings already run it once on Stop: kept (adding ours would run it twice), never a HAND that the
        # person could only clear by deleting their own user-level hook
        self.assertIn("kept    hook Stop: session-checkpoint already runs once from", p.stdout)
        self.assertTrue(any("pre-push exists without the layer(s) # factory-ff-only, # factory-no-unpinned-tool" in h
                            for h in hand), hand)
        self.assertEqual((hooks / "pre-push").read_bytes(), before_hook)
        self.assertEqual((self.proj / "factory-pins/session-checkpoint.config.json").read_text(encoding="utf-8"),
                         '{"schema": "session-checkpoint.v1"}\n')
        s = self.settings()
        self.assertEqual(s["permissions"], mine["permissions"])
        self.assertEqual(s["hooks"]["SessionStart"], mine["hooks"]["SessionStart"])        # untouched, not doubled
        self.assertNotIn("Stop", s["hooks"])                                                  # the user level runs it
        self.assertEqual(len(s["hooks"]["PreToolUse"][0]["hooks"]), 2)                       # the guards were added
        # the person chains the layers and switches to the pinned hook (as the HAND line printed it); the same init
        # then completes
        (hooks / "pre-push").write_bytes(before_hook + lf(BUS_ROOT / "hooks/pre-push.factory.sh"))
        os.chmod(hooks / "pre-push", 0o755)              # a chained hook git will run (init checks it on POSIX)
        s["hooks"]["SessionStart"][0]["hooks"][0]["command"] = (
            'python -I "$CLAUDE_PROJECT_DIR/factory-pins/pin-runner.py" --never-block run session-checkpoint -- '
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
        no_crt = [t for t in good["profiles"]["base"]["tools"] if t != "check-rule-tags"]
        tools_bad, seeds_bad, hook_bad, git_bad = ("'tools' must be", "'seeds' must map", "malformed claude hook",
                                                   "'git_hooks' entries need")
        cases = [   # (the defect, the reason the refusal must give: each case proves its OWN check, not just any refusal)
            ({"tools": ["no-such-tool"]}, tools_bad),
            ({"tools": []}, tools_bad),
            ({"seeds": {"../outside.json": "tools/factory/registry.json"}}, seeds_bad),
            ({"seeds": {"factory-pins/factory-pins.json": "tools/factory/registry.json"}}, seeds_bad),
            ({"claude_hooks": [{**hook, "tool": "check-doc-size"}]}, hook_bad),
            ({"claude_hooks": [{**hook, "args": ["--config", "a b"]}]}, hook_bad),
            ({"claude_hooks": [{**hook, "args": ['"$(rm -rf ~)"']}]}, hook_bad),
            ({"claude_hooks": [{**hook, "event": "Whenever"}]}, hook_bad),
            ({"claude_hooks": [{**hook, "timeout": 0}]}, hook_bad),
            ({"claude_hooks": [{**hook, "never_block": "yes"}]}, hook_bad),
            ({"git_hooks": [{"hook": "post-merge", "path": "hooks/pre-push.factory.sh", "markers": ["# factory-ff-only"]}]},
             git_bad),
            ({"git_hooks": [{"hook": "pre-push", "path": "hooks/pre-push.factory.sh"}]}, git_bad),
            ({"git_hooks": [{"hook": "pre-push", "path": "hooks/pre-push.factory.sh", "markers": []}]}, git_bad),
            ({"rule_map": True, "tools": no_crt}, "'rule_map' needs check-rule-tags"),
            ({"throughput_stub": "yes"}, "'throughput_stub' must be true or false"),
            ({"surprise": 1}, "only keys from"),
        ]
        for bad, why in cases:
            reg = json.loads(json.dumps(good))
            reg["profiles"]["base"].update(bad)
            reg_path.write_text(json.dumps(reg), encoding="utf-8")
            git(self.bus, "commit", "-qam", "bad profile")
            self.c1 = git(self.bus, "rev-parse", "HEAD")
            with self.subTest(bad=bad):
                p = self.init()
                self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
                self.assertIn("profile 'base'", p.stderr)
                self.assertIn(why, p.stderr)
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


class ReviewRound1(_Init):
    """Regressions for review round 1 (Codex gpt-6.1-sol key): each test fails on e5253fc8."""

    def write(self, rel: str, body: str) -> Path:
        p = self.proj / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
        return p

    def test_a_forged_runner_with_a_matching_record_is_refused(self):
        forged = b"print('not a bus release')\n"
        import hashlib as _h
        self.write("factory-pins/pin-runner.py", "")
        (self.proj / "factory-pins/pin-runner.py").write_bytes(forged)
        self.write("factory-pins/factory-pins.json", json.dumps({"schema": "factory-pins.v1", "tools": {}, "runner": {
            "commit": self.c1, "path": "tools/factory/pin-runner.py", "blob": _h.sha1(b"blob %d\0" % len(forged) + forged).hexdigest(),
            "bytes": len(forged), "sha256": _h.sha256(forged).hexdigest()}}))
        before = tree_digest(self.proj)
        p = self.init()
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertIn("not a bus release", p.stderr)
        self.assertEqual(tree_digest(self.proj), before)

    def test_a_linked_destination_is_refused(self):
        outside = self.t / "outside.json"
        outside.write_text("{}", encoding="utf-8")
        (self.proj / ".claude").mkdir()
        try:
            os.symlink(outside, self.proj / ".claude" / "settings.json")
        except (OSError, NotImplementedError):
            self.skipTest("this account cannot create symlinks")
        before = tree_digest(self.proj)
        p = self.init()
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertIn("is a link", p.stderr)
        self.assertEqual((outside.read_text(encoding="utf-8"), tree_digest(self.proj)), ("{}", before))

    def test_bootstrap_refusal_leaves_an_existing_runner_untouched(self):
        bash = next((Path(p) for p in (shutil.which("bash"), shutil.which("sh")) if p and "system32" not in p.lower()), None)
        if bash is None:
            self.skipTest("no POSIX shell")
        # The project adopted an OLDER runner release; the bus has moved on. A refused bootstrap must not replace it
        # (identical bytes would make this test vacuous, so the two releases differ).
        runner = self.bus / "tools/factory/pin-runner.py"
        current = runner.read_bytes()
        runner.write_bytes(current + b"# an older release\n")
        git(self.bus, "commit", "-qam", "older runner release")
        old_commit, self.c1 = git(self.bus, "rev-parse", "HEAD"), git(self.bus, "rev-parse", "HEAD")
        old_runner = self.elsewhere / "pin-runner.py"
        old_runner.write_bytes(runner.read_bytes())
        self.assertEqual(self.init(runner=old_runner).returncode, 0)
        runner.write_bytes(current)
        git(self.bus, "commit", "-qam", "current runner release")
        self.c1 = git(self.bus, "rev-parse", "HEAD")
        self.assertNotEqual(old_commit, self.c1)
        before = tree_digest(self.proj)
        r = subprocess.run([str(bash), (FACTORY / "bootstrap.sh").as_posix(), self.bus.as_posix(), self.c1, "profile:nope",
                            "tester", "fixture", self.proj.as_posix()], capture_output=True, text=True, cwd=str(self.elsewhere),
                           env=self.env(PYTHON=sys.executable), stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertEqual(tree_digest(self.proj), before)

    def test_bootstrap_runner_is_isolated_from_the_project(self):
        bash = next((Path(p) for p in (shutil.which("bash"), shutil.which("sh")) if p and "system32" not in p.lower()), None)
        if bash is None:
            self.skipTest("no POSIX shell")
        self.write("factory-pins/subprocess.py", "open(r'%s', 'w').write('x')\n" % (self.t / "imported.marker").as_posix())
        r = subprocess.run([str(bash), (FACTORY / "bootstrap.sh").as_posix(), self.bus.as_posix(), self.c1, "profile:base",
                            "tester", "fixture", self.proj.as_posix()], capture_output=True, text=True, cwd=str(self.proj / "factory-pins"),
                           env=self.env(PYTHON=sys.executable), stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse((self.t / "imported.marker").exists(), "a project file was imported into the runner")

    def registry_with(self, **profile_update) -> None:
        reg_path = self.bus / "tools/factory/registry.json"
        reg = json.loads(reg_path.read_text(encoding="utf-8"))
        reg["profiles"]["base"].update(profile_update)
        reg_path.write_text(json.dumps(reg), encoding="utf-8")
        git(self.bus, "commit", "-qam", "profile variant")
        self.c1 = git(self.bus, "rev-parse", "HEAD")

    def test_a_seed_aliasing_the_runner_in_another_case_is_refused(self):
        for dest in ("factory-pins/PIN-RUNNER.PY", "factory-pins/Factory-Pins.json", "factory-pins/.hidden", "factory-pins/a/b"):
            self.registry_with(seeds={dest: "tools/factory/registry.json"})
            with self.subTest(dest=dest):
                p = self.init()
                self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
                self.assertIn("'seeds'", p.stderr)

    def settings_with(self, path: str, event: str, command: str, matcher: str | None = None) -> None:
        g = {"hooks": [{"type": "command", "command": command}], **({"matcher": matcher} if matcher else {})}
        self.write(path, json.dumps({"hooks": {event: [g]}}))

    def test_a_registration_under_another_matcher_or_scope_is_a_hand_step(self):
        cmd = 'python -I "$CLAUDE_PROJECT_DIR/factory-pins/pin-runner.py" run exact-path-add'
        # another matcher in this file: HAND (fix the matcher). One registration in settings.local.json: it already
        # runs once, so it is kept and ours is not added. The same command in BOTH files: it would run twice -> HAND.
        cases = (([(".claude/settings.json", "Read")], 4, "exact-path-add already runs on PreToolUse"),
                 ([(".claude/settings.local.json", "Bash|PowerShell")], 0, "exact-path-add already runs once from"),
                 ([(".claude/settings.json", "Bash|PowerShell"), (".claude/settings.local.json", "Bash|PowerShell")], 4,
                  "exact-path-add runs 2 times on PreToolUse"))
        for regs, rc, text in cases:
            shutil.rmtree(self.proj / ".claude", ignore_errors=True)
            for path, matcher in regs:
                self.settings_with(path, "PreToolUse", cmd, matcher)
            with self.subTest(regs=regs):
                p = self.init()
                self.assertEqual(p.returncode, rc, p.stdout + p.stderr)
                self.assertIn(text, p.stdout)

    def test_tool_detection_reads_commands_not_substrings(self):
        sys.path.insert(0, str(FACTORY))
        import importlib.util
        spec = importlib.util.spec_from_file_location("pr", FACTORY / "pin-runner.py")
        pr = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pr)
        path = "tools/factory/session-checkpoint.py"
        yes = ['python "$CLAUDE_PROJECT_DIR/tools/session-checkpoint.py"', "python3 -X utf8 C:\\x\\hooks\\session_checkpoint.py Stop",
               'python -I "$CLAUDE_PROJECT_DIR/factory-pins/pin-runner.py" run "session-checkpoint" -- --config x',
               "cd /x && FOO=1 python tools/session-checkpoint.py", "./session-checkpoint.py"]
        no = ["echo session-checkpoint.py", 'python -I factory-pins/pin-runner.py run session-checkpoint-v2',
              "python tools/other.py --log session-checkpoint.py", "python factory-pins/pin-runner.py run exact-path-add"]
        for c in yes:
            self.assertTrue(pr.wires_tool(c, "session-checkpoint", path), c)
        for c in no:
            self.assertFalse(pr.wires_tool(c, "session-checkpoint", path), c)

    def test_every_pre_push_layer_is_required(self):
        hooks = Path(git(self.proj, "rev-parse", "--path-format=absolute", "--git-path", "hooks"))
        hooks.mkdir(parents=True, exist_ok=True)
        body = lf(BUS_ROOT / "hooks/pre-push.factory.sh").decode()
        only_nut = "#!/bin/sh\n" + body[body.index("# factory-no-unpinned-tool"):]
        (hooks / "pre-push").write_text(only_nut, encoding="utf-8")
        p = self.init()
        self.assertEqual(p.returncode, 4, p.stdout + p.stderr)
        self.assertIn("without the layer(s) # factory-ff-only", p.stdout)
        self.assertEqual((hooks / "pre-push").read_text(encoding="utf-8"), only_nut)

    def test_a_hooks_path_outside_the_repository_is_never_written(self):
        shared = self.t / "shared-hooks"
        shared.mkdir()
        git(self.proj, "config", "core.hooksPath", str(shared))
        p = self.init()
        self.assertEqual(p.returncode, 4, p.stdout + p.stderr)
        self.assertIn("outside this repository", p.stdout)
        self.assertEqual(list(shared.iterdir()), [])


class ReviewRound1Claude(_Init):
    """Regressions for review round 1 (Claude key)."""

    def test_a_refused_runner_never_blocks_stop_but_still_blocks_a_guard(self):
        self.assertEqual(self.init().returncode, 0)
        pins = self.proj / "factory-pins" / "factory-pins.json"
        pins.write_text(json.dumps({"schema": "not-the-schema", "tools": {}}), encoding="utf-8")
        stop = self.hook("Stop", {"hook_event_name": "Stop", "session_id": "s1", "cwd": str(self.proj)})
        self.assertEqual(stop.returncode, 1, "a Stop hook exiting 2 would block every turn end")
        self.assertIn("REFUSED", stop.stderr)
        guard = self.hook("PreToolUse", {"tool_name": "Bash", "tool_input": {"command": "git add -A"}}, "exact-path-add")
        self.assertEqual(guard.returncode, 2, "a guard still blocks when the runner refuses")

    def test_the_projects_own_pinned_form_is_kept(self):
        own = 'python -I "$CLAUDE_PROJECT_DIR/factory-pins/pin-runner.py" run git-optional-locks -- --observe-only'
        (self.proj / ".claude").mkdir()
        (self.proj / ".claude/settings.json").write_text(json.dumps({"hooks": {"PreToolUse": [
            {"matcher": "Bash|PowerShell", "hooks": [{"type": "command", "command": own}]}]}}), encoding="utf-8")
        p = self.init()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("kept    hook PreToolUse/Bash|PowerShell: git-optional-locks (the project's own form", p.stdout)
        cmds = [h["command"] for g in self.settings()["hooks"]["PreToolUse"] for h in g["hooks"]]
        self.assertEqual(sum("git-optional-locks" in c for c in cmds), 1, cmds)

    def test_settings_keep_their_text_and_duplicate_keys_refuse(self):
        (self.proj / ".claude").mkdir()
        (self.proj / ".claude/settings.json").write_text('{"env": {"GREETING": "café"}}', encoding="utf-8")
        self.assertEqual(self.init().returncode, 0)
        self.assertIn("café", (self.proj / ".claude/settings.json").read_text(encoding="utf-8"))
        shutil.rmtree(self.proj / ".claude")
        (self.proj / ".claude").mkdir()
        (self.proj / ".claude/settings.json").write_text('{"hooks": {}, "hooks": {"Stop": []}}', encoding="utf-8")
        before = tree_digest(self.proj)
        p = self.init()
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertIn("duplicate key", p.stderr)
        self.assertEqual(tree_digest(self.proj), before)

    def test_a_write_that_cannot_be_staged_writes_nothing(self):
        (self.proj / ".claude").write_text("a file where the directory should be", encoding="utf-8")
        before = tree_digest(self.proj)
        p = self.init()
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertIn("nothing written", p.stderr)
        self.assertEqual(tree_digest(self.proj), before)
        self.assertFalse((self.proj / "factory-pins").exists(), "a directory created while staging stays behind")


class ReviewRound2(_Init):
    """Regressions for review round 2 (Codex gpt-6.1-sol key)."""

    def load_pr(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("pr", FACTORY / "pin-runner.py")
        pr = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pr)
        return pr

    def test_an_older_runner_without_never_block_is_not_wired_to_stop(self):
        runner = self.bus / "tools/factory/pin-runner.py"
        runner.write_bytes(runner.read_bytes().replace(b'"--never-block"', b'"--no-such-flag"'))
        git(self.bus, "commit", "-qam", "a runner release that predates --never-block")
        self.c1 = git(self.bus, "rev-parse", "HEAD")
        old = self.elsewhere / "pin-runner.py"
        old.write_bytes(runner.read_bytes())
        p = self.init(runner=old)
        self.assertEqual(p.returncode, 4, p.stdout + p.stderr)
        self.assertEqual(sum("predates --never-block" in l for l in p.stdout.splitlines() if l.startswith("HAND:")), 2)
        hooks = self.settings()["hooks"]
        self.assertNotIn("Stop", hooks)
        self.assertNotIn("SessionStart", hooks)

    def test_a_kept_stop_hook_must_be_never_block(self):
        (self.proj / ".claude").mkdir()
        old = ('python -I "$CLAUDE_PROJECT_DIR/factory-pins/pin-runner.py" run session-checkpoint -- '
               '--config "$CLAUDE_PROJECT_DIR/factory-pins/session-checkpoint.config.json"')
        (self.proj / ".claude/settings.json").write_text(json.dumps({"hooks": {"Stop": [{"hooks": [
            {"type": "command", "command": old}]}]}}), encoding="utf-8")
        p = self.init()
        self.assertEqual(p.returncode, 4, p.stdout + p.stderr)
        self.assertTrue(any("session-checkpoint already runs on Stop" in l and "--never-block run session-checkpoint" in l
                            for l in p.stdout.splitlines() if l.startswith("HAND:")), p.stdout)

    def test_a_stop_hook_elsewhere_by_pin_without_never_block_is_a_hand_step(self):
        """Review round 3 (Claude key): one registration in another scope was kept unchecked; by pin WITHOUT
        --never-block it still exits 2 on a runner refusal and blocks every turn end."""
        cmd = ('python -I "$CLAUDE_PROJECT_DIR/factory-pins/pin-runner.py" run session-checkpoint -- '
               '--config "$CLAUDE_PROJECT_DIR/factory-pins/session-checkpoint.config.json"')
        (self.proj / ".claude").mkdir()
        (self.proj / ".claude/settings.local.json").write_text(json.dumps({"hooks": {"Stop": [{"hooks": [
            {"type": "command", "command": cmd}]}]}}), encoding="utf-8")
        p = self.init()
        self.assertEqual(p.returncode, 4, p.stdout + p.stderr)
        self.assertTrue(any("by pin without --never-block" in l and "settings.local.json" in l
                            for l in p.stdout.splitlines() if l.startswith("HAND:")), p.stdout)
        (self.proj / ".claude/settings.local.json").write_text(json.dumps({"hooks": {"Stop": [{"hooks": [
            {"type": "command", "command": cmd.replace(" run session-checkpoint", " --never-block run session-checkpoint")}]}]}}),
            encoding="utf-8")
        self.assertEqual(self.init().returncode, 0)

    def test_runner_commands_are_parsed_at_the_subcommand(self):
        pr = self.load_pr()
        guard = "hooks/claude/exact-path-add.py"
        smuggled = 'python -I "$CLAUDE_PROJECT_DIR/factory-pins/pin-runner.py" run git-optional-locks -- --observe-only run exact-path-add'
        self.assertFalse(pr.wires_tool(smuggled, "exact-path-add", guard))
        self.assertFalse(pr.by_pin(smuggled, "exact-path-add"))
        self.assertTrue(pr.by_pin(smuggled, "git-optional-locks"))
        self.assertFalse(pr.by_pin("python -I /tmp/pin-runner.py run exact-path-add", "exact-path-add"))
        self.assertTrue(pr.wires_tool("python -I /tmp/pin-runner.py run exact-path-add", "exact-path-add", guard))
        # the project's own form judges with the pins init writes: no runner option but --never-block (round 3)
        self.assertFalse(pr.by_pin('python -I "$CLAUDE_PROJECT_DIR/factory-pins/pin-runner.py" --pins x.json run exact-path-add',
                                   "exact-path-add"))
        self.assertTrue(pr.by_pin('python -I "$CLAUDE_PROJECT_DIR/factory-pins/pin-runner.py" --never-block run exact-path-add',
                                  "exact-path-add"))
        # a '#' inside a word is not a comment (round 3: shlex.shlex kept its default commenters)
        self.assertTrue(pr.wires_tool("python C:/dev/C#/proj/tools/session-checkpoint.py", "session-checkpoint",
                                      "tools/factory/session-checkpoint.py"))
        self.assertTrue(pr.wires_tool("echo x#; python tools/session-checkpoint.py", "session-checkpoint",
                                      "tools/factory/session-checkpoint.py"))
        sc = "tools/factory/session-checkpoint.py"
        for c in ("python tools/session-checkpoint.py; echo done", "(python tools/session-checkpoint.py)",
                  "true&&python tools/session-checkpoint.py", "python tools/session-checkpoint.py>/dev/null"):
            self.assertTrue(pr.wires_tool(c, "session-checkpoint", sc), c)

    def test_publication_failure_restores_every_original(self):
        pr = self.load_pr()
        d = self.t / "pub"
        d.mkdir()
        (d / "a.json").write_text("original a", encoding="utf-8")
        real, calls = os.replace, []

        def flaky(src, dst):
            calls.append(dst)
            if str(dst).endswith("b.json"):
                raise PermissionError("locked")
            return real(src, dst)
        pr.os.replace = flaky
        try:
            with self.assertRaises(pr.Refused) as ctx:
                pr.commit_writes([(d / "a.json", b"new a", 0o644), (d / "b.json", b"new b", 0o644)])
        finally:
            pr.os.replace = real
        self.assertIn("every change undone", str(ctx.exception))
        self.assertEqual(sorted(p.name for p in d.iterdir()), ["a.json"])
        self.assertEqual((d / "a.json").read_text(encoding="utf-8"), "original a")

    def test_a_custom_pins_path_is_refused(self):
        before = tree_digest(self.proj)
        p = self.init("--pins", str(self.proj / "elsewhere" / "pins.json"))
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertIn("drop --pins", p.stderr)
        self.assertEqual(tree_digest(self.proj), before)

    def test_the_judge_reads_pins_not_text(self):
        """Older master pins that MENTION the layer tool (a comment key) but do not pin it must not become the judge."""
        r = subprocess.run([sys.executable, str(self.bus / "tools/factory/pin-runner.py"), "install", "check-rule-tags",
                            "--commit", self.c1, "--reviewer", "t", "--reason", "r", "--project-root", str(self.proj),
                            "--bus", str(self.bus)], capture_output=True, text=True, env=self.env(), stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        pins = json.loads((self.proj / "factory-pins/factory-pins.json").read_text(encoding="utf-8"))
        pins["_planned_layers"] = ["pre-push-ff-only", "no-unpinned-tool"]
        (self.proj / "factory-pins/factory-pins.json").write_text(json.dumps(pins, indent=2), encoding="utf-8")
        git(self.proj, "add", "--", "factory-pins")
        git(self.proj, "commit", "-qm", "an earlier consumer that plans the layers")
        self.assertEqual(self.push("master").returncode, 0)
        p = self.init()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.commit_listed(p.stdout)
        r = self.push("master")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_the_layers_run_the_runner_isolated(self):
        self.assertEqual(self.init().returncode, 0)
        evil = self.t / "evil"
        evil.mkdir()
        (evil / "json.py").write_text("open(r'%s', 'w').write('x')\nfrom importlib import import_module\n"
                                      % (self.t / "imported.marker").as_posix(), encoding="utf-8")
        git(self.proj, "add", "--", ".")
        git(self.proj, "commit", "-qm", "factory")
        r = subprocess.run(["git", "-C", str(self.proj), "push", "origin", "master"], capture_output=True, text=True,
                           env=self.env(PYTHONPATH=str(evil)), stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse((self.t / "imported.marker").exists(), "a PYTHONPATH module was imported by a layer")

    def test_a_non_executable_hook_is_not_certified(self):
        if os.name == "nt":
            self.skipTest("git for Windows runs hooks without an executable bit")
        hooks = Path(git(self.proj, "rev-parse", "--path-format=absolute", "--git-path", "hooks"))
        hooks.mkdir(parents=True, exist_ok=True)
        (hooks / "pre-push").write_bytes(lf(BUS_ROOT / "hooks/pre-push.factory.sh"))
        os.chmod(hooks / "pre-push", 0o644)
        p = self.init()
        self.assertEqual(p.returncode, 4, p.stdout + p.stderr)
        self.assertIn("git will not run it: chmod +x", p.stdout)
        os.chmod(hooks / "pre-push", 0o755)
        self.assertEqual(self.init().returncode, 0)

    def test_a_shared_hooks_dir_converges_once_chained(self):
        shared = self.t / "shared-hooks"
        shared.mkdir()
        git(self.proj, "config", "core.hooksPath", str(shared))
        self.assertEqual(self.init().returncode, 4)
        (shared / "pre-push").write_bytes(lf(BUS_ROOT / "hooks/pre-push.factory.sh"))
        os.chmod(shared / "pre-push", 0o755)
        p = self.init()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("a shared core.hooksPath outside this repository", p.stdout)

    def test_a_branch_from_before_the_adoption_still_pushes(self):
        """Review round 2 (Claude key): until a protected ref pins a layer, the pushed commit judges; a branch that
        predates init has no pins, and the layer refused every push of it."""
        git(self.proj, "checkout", "-q", "-b", "old-feature")
        (self.proj / "feature.txt").write_text("f\n", encoding="utf-8")
        git(self.proj, "add", "--", "feature.txt")
        git(self.proj, "commit", "-qm", "work from before the adoption")
        git(self.proj, "checkout", "-q", "master")
        p = self.init()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        r = self.push("old-feature")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("[ff-only] not applied", r.stderr)
        self.assertIn("[no-unpinned-tool] not applied", r.stderr)

    def test_pins_with_a_bom_still_judge_and_unreadable_pins_refuse(self):
        """Review round 3 (Codex key): the judge helper read the pins as plain UTF-8, so pins with a BOM (Windows
        PowerShell's UTF-8 writer; the runner itself accepts them) looked 'not pinned' and BOTH layers were skipped."""
        self.assertEqual(self.init().returncode, 0)
        pins = self.proj / "factory-pins" / "factory-pins.json"
        pins.write_bytes(b"\xef\xbb\xbf" + pins.read_bytes())
        git(self.proj, "add", "--", ".")
        git(self.proj, "commit", "-qm", "factory, pins written with a BOM")
        r = self.push("master")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("not applied", r.stderr)
        (self.proj / "tools").mkdir()
        (self.proj / "tools" / "session-checkpoint.py").write_text("print('copy')\n", encoding="utf-8")
        git(self.proj, "add", "--", "tools/session-checkpoint.py")
        git(self.proj, "commit", "-qm", "a copy")
        r = self.push("HEAD:refs/heads/sneak")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("[no-unpinned-tool] PUSH REFUSED", r.stderr)

    def test_unreadable_pins_never_turn_a_layer_off(self):
        """Tiebreak (third key): pins that cannot be read must not look 'not pinned'. With no protected ref holding the
        runner yet, the pushed commit judges; its torn pins keep the layer applied and the runner refuses."""
        self.assertEqual(self.init().returncode, 0)
        (self.proj / "factory-pins" / "factory-pins.json").write_text("{not json", encoding="utf-8")
        git(self.proj, "add", "--", ".")
        git(self.proj, "commit", "-qm", "factory, with torn pins")
        r = self.push("master")
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn("not applied", r.stderr)
        self.assertIn("[ff-only] PUSH REFUSED (exit 2)", r.stderr)
        self.assertIn("invalid JSON", r.stderr)

    def test_the_commit_line_is_quoted_for_a_spaced_hooks_dir(self):
        git(self.proj, "config", "core.hooksPath", ".team hooks")
        p = self.init()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        line = next(l for l in p.stdout.splitlines() if l.startswith("COMMIT"))
        self.assertIn("'.team hooks/pre-push'", line)
        self.commit_listed(p.stdout)
        self.assertEqual(git(self.proj, "ls-files", "--", ".team hooks/pre-push"), ".team hooks/pre-push")


class ReviewMinors(_Init):
    """Regressions for the MINOR findings the LAND verdict left open."""

    STOP = "session-checkpoint"

    def user_stop_hook(self, runner: str) -> None:
        (self.home / ".claude" / "settings.json").write_text(json.dumps({"hooks": {"Stop": [{"hooks": [
            {"type": "command", "command": f'python -I "{runner}" run {self.STOP}'}]}]}}), encoding="utf-8")

    def stop_hand(self) -> str:
        p = self.init()
        self.assertEqual(p.returncode, 4, p.stdout + p.stderr)
        lines = [l for l in p.stdout.splitlines() if l.startswith("HAND:") and f"{self.STOP} runs on Stop" in l]
        self.assertEqual(len(lines), 1, p.stdout)
        return lines[0]

    def test_an_older_runner_elsewhere_is_never_told_to_add_never_block(self):
        """MINOR 1: a user-level Stop hook by pin through an older vendored runner was told to add --never-block, a
        flag that runner rejects (exit 2 on every Stop). Gate the advice on the runner's own bytes."""
        old = self.t / "old-project" / "factory-pins" / "pin-runner.py"
        old.parent.mkdir(parents=True)
        old.write_bytes((self.bus / "tools/factory/pin-runner.py").read_bytes().replace(b'"--never-block"', b'"--no-such-flag"'))
        self.user_stop_hook(old.as_posix())
        line = self.stop_hand()
        self.assertNotIn("Add --never-block", line)
        self.assertIn("Run it through this project's runner", line)
        self.assertIn('factory-pins/pin-runner.py" --never-block run session-checkpoint', line)
        # an unresolvable runner path is not presumed to support the flag either
        self.user_stop_hook("$FACTORY_NO_SUCH_VAR/factory-pins/pin-runner.py")
        self.assertIn("Run it through this project's runner", self.stop_hand())
        # a runner that supports it: adding the flag is the fix, and the fixed entry is kept
        new = self.t / "new-project" / "factory-pins" / "pin-runner.py"
        new.parent.mkdir(parents=True)
        new.write_bytes((self.bus / "tools/factory/pin-runner.py").read_bytes())
        self.user_stop_hook(new.as_posix())
        self.assertIn("Add --never-block before `run` in that entry", self.stop_hand())
        (self.home / ".claude" / "settings.json").write_text(json.dumps({"hooks": {"Stop": [{"hooks": [
            {"type": "command", "command": f'python -I "{new.as_posix()}" --never-block run {self.STOP}'}]}]}}), encoding="utf-8")
        p = self.init()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_the_hand_line_names_what_disqualifies_a_project_hook(self):
        """MINOR 2: a project hook through the project's runner with a runner option other than --never-block (--bus)
        was told only "replace it with ..."; the HAND line now names the option (and any other defect)."""
        cases = (('python -I "$CLAUDE_PROJECT_DIR/factory-pins/pin-runner.py" --bus /x run exact-path-add', "Bash|PowerShell",
                  "runner option --bus"),
                 ('python -I "$CLAUDE_PROJECT_DIR/factory-pins/pin-runner.py" run exact-path-add', "Read",
                  "matcher Read, not Bash|PowerShell"),
                 ('python "$CLAUDE_PROJECT_DIR/hooks/exact-path-add.py"', "Bash|PowerShell", "a copy, not run by pin"),
                 ('python -I /opt/pin-runner.py run exact-path-add', "Bash|PowerShell",
                  "through /opt/pin-runner.py, not this project's factory-pins/pin-runner.py"))
        for cmd, matcher, why in cases:
            shutil.rmtree(self.proj / ".claude", ignore_errors=True)
            (self.proj / ".claude").mkdir()
            (self.proj / ".claude/settings.json").write_text(json.dumps({"hooks": {"PreToolUse": [
                {"matcher": matcher, "hooks": [{"type": "command", "command": cmd}]}]}}), encoding="utf-8")
            with self.subTest(cmd=cmd, matcher=matcher):
                p = self.init()
                self.assertEqual(p.returncode, 4, p.stdout + p.stderr)
                line = next(l for l in p.stdout.splitlines() if l.startswith("HAND: exact-path-add already runs on"))
                self.assertIn(f"({why}", line)
                self.assertIn("-- replace it with:", line)
        # a kept Stop hook in this file without --never-block names that defect
        shutil.rmtree(self.proj / ".claude")
        (self.proj / ".claude").mkdir()
        (self.proj / ".claude/settings.json").write_text(json.dumps({"hooks": {"Stop": [{"hooks": [{"type": "command",
            "command": f'python -I "$CLAUDE_PROJECT_DIR/factory-pins/pin-runner.py" run {self.STOP}'}]}]}}), encoding="utf-8")
        p = self.init()
        self.assertIn("(without --never-block: a runner refusal would exit 2", p.stdout)
        # this project's own runner named by an absolute path is called that, not "another runner" (review round 1)
        self.assertTrue(self.runner.is_file())
        own = f'python -I "{self.runner.as_posix()}" run exact-path-add'
        (self.proj / ".claude/settings.json").write_text(json.dumps({"hooks": {"PreToolUse": [
            {"matcher": "Bash|PowerShell", "hooks": [{"type": "command", "command": own}]}]}}), encoding="utf-8")
        p = self.init()
        line = next(l for l in p.stdout.splitlines() if l.startswith("HAND: exact-path-add already runs on"))
        self.assertIn(f"(names this project's runner as {self.runner.as_posix()}; the pinned form is "
                      "$CLAUDE_PROJECT_DIR/factory-pins/pin-runner.py)", line)
        # ... and its option defects are still named (review round 2)
        (self.proj / ".claude/settings.json").write_text(json.dumps({"hooks": {"PreToolUse": [{"matcher": "Bash|PowerShell",
            "hooks": [{"type": "command", "command": own.replace(" run ", " --bus /x run ")}]}]}}), encoding="utf-8")
        line = next(l for l in self.init().stdout.splitlines() if l.startswith("HAND: exact-path-add already runs on"))
        self.assertIn("pin-runner.py; runner option --bus:", line)

    def test_torn_pins_on_origin_master_follow_the_documented_recourse(self):
        """MINOR 4 (hooks/README.md layer 3): torn pins that reach origin/master refuse every later push, the repair
        included, and the documented recourse -- `git push --no-verify` after review -- lands it; the push after
        the repair is judged by the repaired pins again. Pins the README's claim to the hook's behaviour."""
        p = self.init()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.commit_listed(p.stdout)
        self.assertEqual(self.push("master").returncode, 0)
        pins = self.proj / "factory-pins" / "factory-pins.json"
        good = pins.read_bytes()
        pins.write_text("{not json", encoding="utf-8")
        git(self.proj, "commit", "-qam", "torn pins")
        r = self.push("master")
        self.assertEqual(r.returncode, 0, "origin/master's good pins judge this push: " + r.stderr)
        pins.write_bytes(good)
        git(self.proj, "commit", "-qam", "repair the pins")
        r = self.push("master")
        self.assertNotEqual(r.returncode, 0, "the judge is origin/master's torn pins: the repair is refused too")
        self.assertNotIn("not applied", r.stderr)
        self.assertIn("PUSH REFUSED", r.stderr)
        r = self.push("--no-verify", "master")
        self.assertEqual(r.returncode, 0, r.stderr)
        (self.proj / "after.txt").write_text("a\n", encoding="utf-8")
        git(self.proj, "add", "--", "after.txt")
        git(self.proj, "commit", "-qm", "after the repair")
        r = self.push("master")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("not applied", r.stderr)
        # judging resumed: the repaired pins refuse what they exist to refuse (a copy of a shared tool)
        (self.proj / "tools").mkdir()
        (self.proj / "tools" / "session-checkpoint.py").write_text("print('copy')\n", encoding="utf-8")
        git(self.proj, "add", "--", "tools/session-checkpoint.py")
        git(self.proj, "commit", "-qm", "a copy")
        r = self.push("master")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("[no-unpinned-tool] PUSH REFUSED", r.stderr)
        self.assertNotIn("invalid JSON", r.stderr)
        readme = (BUS_ROOT / "hooks" / "README.md").read_text(encoding="utf-8")
        self.assertIn("torn pins, every push is refused, the repair included; land the repair with `git push --no-verify`",
                      " ".join(readme.split()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
