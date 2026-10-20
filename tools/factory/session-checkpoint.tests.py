#!/usr/bin/env python3
"""Tests for tools/factory/session-checkpoint.py.   python tools/factory/session-checkpoint.tests.py

PARITY is the claim that retires the fleet's copies: the canonical, given a project's config, prints and
writes what that project's copy did. Two references live as data in fixtures/session-checkpoint/ (named
*.py.txt so no census or push guard counts them as copies):
  v2-reference.py.txt                    the copy ~/.claude/ROTATION-install-prompt.md pasted into projects
  v3-reference.py.txt, doctrine-periodic-v3-reference.py.txt
                                         DNG's v3 hook and its PreToolUse tick (hard-coded paths patched to
                                         temp dirs below, each patch asserted to have applied exactly once)
Every event of a scripted session (start, dirt, stop, rotation, repeat, resume receipt, bus change, periodic
tick in the hub and in a lane, throttle) runs through the reference and the canonical side by side, each with
its own HOME; stdout and the written checkpoint must match after HOME paths and the minute stamp are masked.
A negative control proves the comparison can fail.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.dont_write_bytecode = True   # importing the tool in a test must not leave __pycache__ in tools/factory

HERE = Path(__file__).resolve().parent
TOOL = HERE / "session-checkpoint.py"
FIX = HERE / "fixtures" / "session-checkpoint"


# Hermetic git: no system or global config of the host (signing, templates, hooksPath, autocrlf) reaches a fixture.
_GITCFG = Path(tempfile.mkdtemp(prefix="factory-tests-gitcfg-")) / "gitconfig"
_GITCFG.write_text("", encoding="utf-8")
HERMETIC = {"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": str(_GITCFG)}


def base_env() -> dict:
    return {**{k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FACTORY_", "CLAUDE_", "DOCTRINE_"))}, **HERMETIC}


def g(repo, *a: str) -> str:
    return subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@example.invalid", "-c", "user.name=t",
                           "-c", "core.autocrlf=false", *a], check=True, capture_output=True, text=True, env=base_env()).stdout.strip()


def init_repo(path: Path, branch: str = "master") -> Path:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", "-b", branch, str(path)], check=True, env=base_env())
    (path / "README.md").write_text("x\n", encoding="utf-8")
    g(path, "add", "--", "README.md")
    g(path, "commit", "-qm", "base")
    return path


class Impl:
    """One implementation under test: a command line and its own HOME."""

    def __init__(self, name: str, argv: list[str], home: Path, env: dict | None = None):
        self.name, self.argv, self.home, self.env = name, argv, home, env or {}
        (home / ".claude").mkdir(parents=True, exist_ok=True)
        self.account("aaaaaaaa-0000")

    def account(self, uuid: str):
        (self.home / ".claude.json").write_text(json.dumps({"oauthAccount": {"accountUuid": uuid}}), encoding="utf-8")

    def __call__(self, event: str, sid: str, cwd: Path, extra_env: dict | None = None) -> subprocess.CompletedProcess:
        env = base_env()
        env.update(HOME=str(self.home), USERPROFILE=str(self.home), **self.env, **(extra_env or {}))
        payload = json.dumps({"hook_event_name": event, "session_id": sid, "cwd": str(cwd)})
        return subprocess.run([sys.executable, *self.argv], input=payload, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", env=env, cwd=str(cwd))

    def mask(self, text: str) -> str:
        for h in (str(self.home), self.home.as_posix(), str(self.home.resolve()), self.home.resolve().as_posix()):
            text = text.replace(h, "<HOME>")
        text = re.sub(r"recorded \d{4}-\d\d-\d\dT\d\d:\d\dZ", "recorded <T>", text)
        return re.sub(r"- written: \S+", "- written: <T>", text)

    def checkpoint(self, slug: str, sid: str) -> str:
        p = self.home / ".claude" / "session-checkpoints" / slug / f"SESSION-{sid}.md"
        return self.mask(p.read_text(encoding="utf-8")) if p.exists() else "(none)"


class _Tmp(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.t = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def same(self, ref: Impl, can: Impl, step: str, ref_r, can_r):
        self.assertEqual(ref_r.returncode, 0, f"{step}: {ref.name} exit {ref_r.returncode}: {ref_r.stderr}")
        self.assertEqual(can_r.returncode, 0, f"{step}: {can.name} exit {can_r.returncode}: {can_r.stderr}")
        self.assertEqual(can.mask(can_r.stdout), ref.mask(ref_r.stdout), f"{step}: stdout differs")
        return ref.mask(ref_r.stdout)

    def staged_only_is_the_intended_difference(self, cwd: Path, slug: str):
        """The ONE intended difference from both references (init review, MINOR 3): v2 and v3 read `git diff`
        (worktree vs index) and untracked files only, so a staged-only file (index vs HEAD) was missing from the
        SessionStart snapshot, the worktree dirty count and the Stop inventory. The canonical adds `git diff --cached`;
        every other byte still matches the reference."""
        lane = self.t / "lane"
        (lane / "staged.txt").write_text("s\n", encoding="utf-8")
        g(lane, "add", "--", "staged.txt")                     # the lane: dirty=1 (wip.txt) in both, plus staged.txt here
        (self.repo / "pre.txt").write_text("p\n", encoding="utf-8")
        g(self.repo, "add", "--", "pre.txt")                   # staged BEFORE the session: never this session's
        ref_r, can_r = self.ref("SessionStart", "s1", cwd), self.can("SessionStart", "s1", cwd)
        self.assertEqual((ref_r.returncode, can_r.returncode), (0, 0), ref_r.stderr + can_r.stderr)
        ref_l, can_l = self.ref.mask(ref_r.stdout).splitlines(), self.can.mask(can_r.stdout).splitlines()
        only_ref = [l for l in ref_l if l not in can_l]
        only_can = [l for l in can_l if l not in ref_l]
        self.assertEqual(len(only_ref), 1, only_ref)
        self.assertTrue(only_ref[0].endswith("/lane: dirty=1 ahead-of-master=0"), only_ref)
        self.assertEqual(len(only_can), 2, only_can)
        main = [l for l in only_can if l.endswith(f"/{self.repo.name}: dirty=1 ahead-of-master=0")]
        self.assertEqual(len(main), 1, only_can)
        # every other line, and the order (`git worktree list`: the main checkout first), is the reference's
        i = ref_l.index(only_ref[0])
        self.assertEqual(can_l, ref_l[:i] + main + [only_ref[0].replace("dirty=1", "dirty=2")] + ref_l[i + 1:])
        (self.repo / "new.txt").write_text("n\n", encoding="utf-8")                  # untracked: both see it
        (self.repo / "mine.txt").write_text("m\n", encoding="utf-8")
        g(self.repo, "add", "--", "mine.txt")                                        # staged-only: v2/v3 miss it
        (self.repo / "pre.txt").write_text("p2\n", encoding="utf-8")                 # v2/v3 call it this session's
        self.same(self.ref, self.can, "stop", self.ref("Stop", "s1", cwd), self.can("Stop", "s1", cwd))
        ref_cp, can_cp = self.ref.checkpoint(slug, "s1"), self.can.checkpoint(slug, "s1")
        self.assertIn("(2):\n  - new.txt\n  - pre.txt\n", ref_cp)
        self.assertEqual(can_cp, ref_cp.replace("  - new.txt\n  - pre.txt\n", "  - mine.txt\n  - new.txt\n"))


class V2Parity(_Tmp):
    """With no config the canonical is the install prompt's v2: same lines, same checkpoint file."""

    def setUp(self):
        super().setUp()
        self.repo = init_repo(self.t / "Proj One")
        g(self.repo, "worktree", "add", "-q", "-b", "lane", str(self.t / "lane"))
        (self.t / "lane" / "wip.txt").write_text("w\n", encoding="utf-8")
        (self.t / "v2").mkdir()
        shutil.copyfile(FIX / "v2-reference.py.txt", self.t / "v2" / "session-checkpoint.py")
        self.ref = Impl("v2", [str(self.t / "v2" / "session-checkpoint.py")], self.t / "h-v2")
        self.can = Impl("canonical", [str(TOOL)], self.t / "h-can")

    def both(self, step, event, sid, cwd=None):
        return self.same(self.ref, self.can, step, self.ref(event, sid, cwd or self.repo), self.can(event, sid, cwd or self.repo))

    def test_session_rotation_and_checkpoint_match_v2(self):
        out = self.both("start", "SessionStart", "s1")
        self.assertIn("lane: dirty=1 ahead-of-master=0", out)
        (self.repo / "new.txt").write_text("n\n", encoding="utf-8")
        out = self.both("stop", "Stop", "s1")
        self.assertIn("checkpoint: 1 uncommitted file(s)", out)
        self.assertEqual(self.can.checkpoint("Proj-One", "s1"), self.ref.checkpoint("Proj-One", "s1"))
        self.assertIn("  - new.txt", self.can.checkpoint("Proj-One", "s1"))
        for i in (self.ref, self.can):
            i.account("bbbbbbbb-0000")
        out = self.both("rotation", "SessionStart", "s2")
        self.assertIn("ACCOUNT ROTATION DETECTED (aaaaaaaa -> bbbbbbbb): read <HOME>", out)
        out = self.both("after the notice", "SessionStart", "s3")
        self.assertNotIn("ROTATION", out)
        self.assertIn("Session checkpoints for Proj One", out)
        self.both("other event", "UserPromptSubmit", "s3")
        out = self.both("not a repo", "SessionStart", "s4", self.t)
        self.assertEqual(out, "")

    def test_staged_only_dirt_is_the_one_difference_from_v2(self):
        self.staged_only_is_the_intended_difference(self.repo, "Proj-One")

    def test_negative_control_a_different_notice_is_caught(self):
        self.can = Impl("canonical+receipts", [str(TOOL), "--config", str(self.cfg())], self.t / "h-can2")
        self.both("start", "SessionStart", "s1")
        for i in (self.ref, self.can):
            i.account("bbbbbbbb-0000")
        ref, can = self.ref("SessionStart", "s2", self.repo), self.can("SessionStart", "s2", self.repo)
        self.assertEqual((ref.returncode, can.returncode), (0, 0))                 # both ran: the difference is the text
        self.assertNotEqual(self.can.mask(can.stdout), self.ref.mask(ref.stdout))
        self.assertIn("not yet resumed", can.stdout)

    def cfg(self) -> Path:
        (self.t / "rcpt").mkdir(exist_ok=True)
        p = self.t / "c.json"
        p.write_text(json.dumps({"schema": "session-checkpoint.v1", "rotation": {"resume_receipts": str(self.t / "rcpt")}}),
                     encoding="utf-8")
        return p


class V3Parity(_Tmp):
    """With DNG's config (fixtures/session-checkpoint/dng.config.json, paths retargeted) the canonical is DNG's v3
    hook plus its periodic tick, event for event."""

    def setUp(self):
        super().setUp()
        t = self.t
        self.ws = t / "Proj - Claude"
        self.repo = init_repo(self.ws / "Proj")
        init_repo(self.ws / ".scratch-Proj")                      # a dotted child sorts first; the rank skips it
        g(self.repo, "worktree", "add", "-q", "-b", "lane", str(t / "lane"))
        (t / "lane" / "wip.txt").write_text("w\n", encoding="utf-8")
        # the bus: origin/master, a fold cursor in a steward receipt, a fresh sweep log
        self.bus = init_repo(t / "bus")
        (self.bus / "RULINGS.md").write_text("r1\n", encoding="utf-8")
        g(self.bus, "add", "--", "RULINGS.md")
        g(self.bus, "commit", "-qm", "R1 ruling")
        cursor = g(self.bus, "rev-parse", "HEAD")
        for n in range(2):
            (self.bus / f"n{n}.md").write_text("n\n", encoding="utf-8")
            g(self.bus, "add", "--", f"n{n}.md")
            g(self.bus, "commit", "-qm", f"note {n}")
        g(self.bus, "update-ref", "refs/remotes/origin/master", "HEAD")
        (t / "steward").mkdir()
        (t / "steward" / "20261017-000000.md").write_text(f"doctrineFoldedThrough: `{cursor}`\n", encoding="utf-8")
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.sweep = t / "sweep.log"
        self.sweep.write_text(f"{now} step=pull rc=0 ok\n{now} step=heartbeat rc=0 ok\n", encoding="utf-8")
        self.ref = self.v3(t / "h-v3", t / "rcpt-v3")
        self.can = self.canonical(t / "h-can", t / "rcpt-can")

    def v3(self, home: Path, receipts: Path) -> Impl:
        receipts.mkdir()
        tools = self.ws / "tools"
        tools.mkdir(exist_ok=True)
        src = (FIX / "v3-reference.py.txt").read_text(encoding="utf-8")
        for const, value in (("RESUME_RECEIPTS", receipts), ("BUS", self.bus), ("STEWARD_RECEIPTS", self.t / "steward"),
                             ("SWEEP_LOG", self.sweep)):
            src, n = re.subn(rf"^{const} = Path\(r\"[^\"]+\"\)$", lambda _m: f"{const} = Path({str(value)!r})", src,
                             flags=re.M)
            self.assertEqual(n, 1, f"v3 fixture: {const} patched {n} times")
        (tools / "session-checkpoint.py").write_text(src, encoding="utf-8", newline="\n")
        shutil.copyfile(FIX / "doctrine-periodic-v3-reference.py.txt", tools / "doctrine-periodic.py")
        return _V3Impl("v3", [str(tools / "session-checkpoint.py")], home,
                       {"CLAUDE_PROJECT_DIR": str(self.ws)}, periodic=[str(tools / "doctrine-periodic.py")])

    def canonical(self, home: Path, receipts: Path, **override) -> Impl:
        receipts.mkdir(exist_ok=True)
        cfg = json.loads((FIX / "dng.config.json").read_text(encoding="utf-8"))
        cfg["rotation"]["resume_receipts"] = str(receipts)
        cfg["doctrine"].update(bus_clone=str(self.bus), steward_receipts=str(self.t / "steward"), sweep_log=str(self.sweep),
                               fold_marker=str(self.repo / ".codex-state/doctrine/last-seen.json"), hub_dir=str(self.ws))
        cfg.update(override)
        p = home.parent / f"{home.name}.config.json"
        p.write_text(json.dumps(cfg), encoding="utf-8")
        return Impl("canonical", [str(TOOL), "--config", str(p)], home, {"CLAUDE_PROJECT_DIR": str(self.ws)})

    def both(self, step, event, sid, cwd=None, env=None):
        return self.same(self.ref, self.can, step, self.ref(event, sid, cwd or self.ws, env), self.can(event, sid, cwd or self.ws, env))

    def test_session_rotation_doctrine_and_periodic_match_v3(self):
        out = self.both("start", "SessionStart", "s1")
        self.assertIn("DATA: 2 bus commit(s) after the board's fold cursor", out)
        self.assertIn("Worktrees of Proj with uncommitted or unintegrated work:", out)
        (self.repo / "new.txt").write_text("n\n", encoding="utf-8")
        self.both("stop", "Stop", "s1")
        self.assertEqual(self.can.checkpoint("Proj", "s1"), self.ref.checkpoint("Proj", "s1"))
        self.assertIn("  - new.txt", self.can.checkpoint("Proj", "s1"))
        for i in (self.ref, self.can):
            i.account("bbbbbbbb-0000")
        out = self.both("rotation", "SessionStart", "s2")
        self.assertIn("and not yet resumed", out)
        self.assertIn("P-RESUME writes its receipt", out)
        out = self.both("repeat until resumed", "SessionStart", "s3")
        self.assertIn("ACCOUNT ROTATION DETECTED (aaaaaaaa -> bbbbbbbb, recorded <T>)", out)
        for d in ("rcpt-v3", "rcpt-can"):
            (self.t / d / "29991231-2359.md").write_text("receipt\n", encoding="utf-8")
            (self.t / d / "not-a-receipt.md").write_text("x\n", encoding="utf-8")
        out = self.both("resumed", "SessionStart", "s4")
        self.assertNotIn("ROTATION", out)
        self.assertIn("after the board's fold cursor", self.both("restart", "SessionStart", "s1"))
        # a ruling lands on the bus: the periodic tick reports it in the hub, never in a lane, then throttles
        (self.bus / "RULINGS.md").write_text("r1\nr2\n", encoding="utf-8")
        g(self.bus, "add", "--", "RULINGS.md")
        g(self.bus, "commit", "-qm", "R2 ruling")
        g(self.bus, "update-ref", "refs/remotes/origin/master", "HEAD")
        self.assertEqual(self.both("lane tick", "PreToolUse", "s1", self.t / "lane", {"DOCTRINE_RECHECK_MIN": "0"}), "")
        out = self.both("hub tick", "PreToolUse", "s1", None, {"DOCTRINE_RECHECK_MIN": "0"})
        ctx = json.loads(out)["hookSpecificOutput"]
        self.assertEqual(ctx["hookEventName"], "PreToolUse")
        self.assertIn("RULINGS.md changed in 1", ctx["additionalContext"])
        self.assertIn("R2 ruling", ctx["additionalContext"])
        self.assertEqual(self.both("throttled", "PreToolUse", "s1"), "")
        self.assertEqual(self.both("nothing new", "PreToolUse", "s1", None, {"DOCTRINE_RECHECK_MIN": "0"}), "")
        self.sweep.write_text("2000-01-01T00:00:00Z step=pull rc=0 ok\n", encoding="utf-8")
        out = self.both("stale sweep tick", "PreToolUse", "s1", None, {"DOCTRINE_RECHECK_MIN": "0"})
        self.assertIn("DATA: STALE - the box doctrine sweep last ran", out)
        out = self.both("stale sweep start", "SessionStart", "s5")
        self.assertIn("DATA: STALE", out)

    def test_staged_only_dirt_is_the_one_difference_from_v3(self):
        self.staged_only_is_the_intended_difference(self.ws, "Proj")

    def test_bus_unreadable_fails_open_and_matches(self):
        shutil.rmtree(self.bus / ".git", onerror=lambda f, p, e: (os.chmod(p, 0o700), f(p)))
        out = self.both("no bus", "SessionStart", "s1")
        self.assertIn("DATA: doctrine check FAILED", out)
        self.both("stop", "Stop", "s1")
        self.assertEqual(self.can.checkpoint("Proj", "s1"), self.ref.checkpoint("Proj", "s1"))
        out = self.both("tick fails", "PreToolUse", "s1", None, {"DOCTRINE_RECHECK_MIN": "0"})
        self.assertIn("periodic re-check): FAILED", out)

    def test_negative_control_no_config_differs(self):
        self.can = Impl("canonical-unconfigured", [str(TOOL)], self.t / "h-bare", {"CLAUDE_PROJECT_DIR": str(self.ws)})
        ref, can = self.ref("SessionStart", "s1", self.ws), self.can("SessionStart", "s1", self.ws)
        self.assertEqual((ref.returncode, can.returncode), (0, 0))                 # both ran: the difference is the text
        self.assertNotEqual(self.can.mask(can.stdout), self.ref.mask(ref.stdout))
        self.assertIn("Fleet doctrine bus", ref.stdout)


class _V3Impl(Impl):
    """v3 was two files: PreToolUse went to doctrine-periodic.py, every other event to session-checkpoint.py."""

    def __init__(self, name, argv, home, env, periodic):
        super().__init__(name, argv, home, env)
        self.periodic = periodic

    def __call__(self, event, sid, cwd, extra_env=None):
        if event != "PreToolUse":
            return super().__call__(event, sid, cwd, extra_env)
        argv, self.argv = self.argv, self.periodic
        try:
            return super().__call__(event, sid, cwd, extra_env)
        finally:
            self.argv = argv


class Contract(_Tmp):
    """The canonical's own contract: never blocks, an unusable config still checkpoints, defaults are v2."""

    def setUp(self):
        super().setUp()
        self.repo = init_repo(self.t / "proj")
        self.run_ = Impl("canonical", [str(TOOL)], self.t / "home")

    def with_cfg(self, body) -> Impl:
        p = self.t / "cfg.json"
        p.write_text(body if isinstance(body, str) else json.dumps(body), encoding="utf-8")
        return Impl("canonical", [str(TOOL), "--config", str(p)], self.t / "home")

    def test_unusable_configs_are_reported_and_the_checkpoint_is_still_written(self):
        bad = ["{not json", {"schema": "other"}, {"unknown_key": 1}, {"doctrine": {"label": "x"}},
               {"rotation": {"receipt_pattern": "(unclosed"}}, {"rotation": {"receipt_pattern": "no-group"}},
               {"deadline_seconds": 0}, {"doctrine": {"bus_clone": "b", "periodic_minutes": -1}},
               {"nested_repo_search": "yes"}, {"rotation": {"resume_hint": ""}}]
        for i, body in enumerate(bad):
            r = self.with_cfg(body)("Stop", f"b{i}", self.repo)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("session-checkpoint: config ", r.stdout, body)
            self.assertTrue((self.t / "home/.claude/session-checkpoints/proj" / f"SESSION-b{i}.md").exists(), body)
        r = Impl("x", [str(TOOL), "--config", str(self.t / "missing.json")], self.t / "home")("SessionStart", "m", self.repo)
        self.assertIn("config unusable", r.stdout)

    def test_comment_keys_and_relative_paths(self):
        (self.t / "rcpt").mkdir()
        i = self.with_cfg({"_comment": "x", "schema": "session-checkpoint.v1", "rotation": {"resume_receipts": "rcpt"}})
        i("SessionStart", "s1", self.repo)
        i.account("bbbbbbbb-0000")
        self.assertIn("not yet resumed", i("SessionStart", "s2", self.repo).stdout)
        (self.t / "rcpt" / "29991231-2359.md").write_text("r\n", encoding="utf-8")   # relative to the config's dir
        self.assertNotIn("ROTATION", i("SessionStart", "s3", self.repo).stdout)

    def test_pretooluse_without_doctrine_is_silent_and_a_crash_still_exits_zero(self):
        r = self.run_("PreToolUse", "s1", self.repo)
        self.assertEqual((r.returncode, r.stdout), (0, ""))
        broken = Impl("x", [str(TOOL)], self.t / "home2")
        (broken.home / ".claude" / "session-checkpoints").write_text("a file, not a directory", encoding="utf-8")
        r = broken("SessionStart", "s1", self.repo)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("session-checkpoint failed (", r.stdout)
        r = Impl("x", [str(TOOL), "--no-such-flag"], self.t / "home")("Stop", "s1", self.repo)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, "session-checkpoint: bad arguments; nothing done"))

    def test_default_hub_is_the_main_checkout(self):
        bus = init_repo(self.t / "bus")
        g(bus, "update-ref", "refs/remotes/origin/master", "HEAD")
        g(self.repo, "worktree", "add", "-q", "-b", "lane", str(self.t / "lane"))
        i = self.with_cfg({"doctrine": {"bus_clone": str(bus)}})
        i("SessionStart", "s1", self.repo)
        (bus / "RULINGS.md").write_text("r\n", encoding="utf-8")
        g(bus, "add", "--", "RULINGS.md")
        g(bus, "commit", "-qm", "ruling")
        g(bus, "update-ref", "refs/remotes/origin/master", "HEAD")
        self.assertEqual(i("PreToolUse", "s1", self.t / "lane", {"DOCTRINE_RECHECK_MIN": "0"}).stdout, "")
        out = i("PreToolUse", "s1", self.repo, {"DOCTRINE_RECHECK_MIN": "0"}).stdout
        self.assertIn("RULINGS.md changed in 1", json.loads(out)["hookSpecificOutput"]["additionalContext"])

    def test_a_lane_tick_never_consumes_the_hubs_interval(self):
        """Review round 1: with the default hub, a lane tick touched the session's stamp first, so the hub's next
        tick inside the interval was silent. Real interval here (no DOCTRINE_RECHECK_MIN=0)."""
        bus = init_repo(self.t / "bus")
        g(bus, "update-ref", "refs/remotes/origin/master", "HEAD")
        g(self.repo, "worktree", "add", "-q", "-b", "lane", str(self.t / "lane"))
        i = self.with_cfg({"doctrine": {"bus_clone": str(bus)}})
        i("SessionStart", "s1", self.repo)
        (bus / "RULINGS.md").write_text("r\n", encoding="utf-8")
        g(bus, "add", "--", "RULINGS.md")
        g(bus, "commit", "-qm", "ruling")
        g(bus, "update-ref", "refs/remotes/origin/master", "HEAD")
        self.assertEqual(i("PreToolUse", "s1", self.t / "lane").stdout, "")
        self.assertEqual(i("PreToolUse", "s1", self.t / "lane").stdout, "")      # remembered: still silent
        out = i("PreToolUse", "s1", self.repo).stdout
        self.assertIn("RULINGS.md changed in 1", json.loads(out)["hookSpecificOutput"]["additionalContext"])
        self.assertEqual(i("PreToolUse", "s1", self.repo).stdout, "")            # the hub's own interval holds

    def test_non_finite_numbers_and_escaping_runbooks_are_refused(self):
        for body in ('{"doctrine": {"bus_clone": "b", "periodic_minutes": NaN}}',
                     '{"doctrine": {"bus_clone": "b", "sweep_stale_hours": Infinity}}',
                     '{"deadline_seconds": NaN}', {"runbook_candidates": ["../../etc/ROTATION.md"]},
                     {"runbook_candidates": ["C:/x/ROTATION.md"]}, {"runbook_candidates": ["/abs/ROTATION.md"]}):
            r = self.with_cfg(body)("Stop", "n", self.repo)
            self.assertIn("the default is used", r.stdout, body)
        bus = init_repo(self.t / "bus2")
        g(bus, "update-ref", "refs/remotes/origin/master", "HEAD")
        i = self.with_cfg({"doctrine": {"bus_clone": str(bus), "hub_dir": str(self.repo)}})
        i("SessionStart", "s9", self.repo)
        for bad in ("nan", "inf", "-1", "soon"):           # an unusable override falls back to the configured interval
            r = i("PreToolUse", "s9", self.repo, {"DOCTRINE_RECHECK_MIN": bad})
            self.assertEqual((r.returncode, "FAILED" in r.stdout), (0, False), bad)

    def test_one_bad_key_costs_only_itself(self):
        """Review round 1 (Claude key): any config error fell back to ALL defaults, nested_repo_search with it, so a
        workspace whose folder is not the repository silently stopped writing checkpoints."""
        ws = self.t / "Proj - X"
        init_repo(ws / "Proj")
        i = self.with_cfg({"nested_repo_search": True, "typo_key": 1, "deadline_seconds": "soon"})
        r = i("Stop", "k1", ws)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("unknown key 'typo_key' ignored", r.stdout)
        self.assertIn("deadline_seconds must be a number", r.stdout)
        self.assertTrue((self.t / "home/.claude/session-checkpoints/Proj/SESSION-k1.md").exists(), r.stdout)

    def test_an_optional_receipt_group_and_a_torn_tip_never_break_session_start(self):
        (self.t / "rcpt").mkdir()
        i = self.with_cfg({"rotation": {"resume_receipts": "rcpt", "receipt_pattern": r"(\d{8}-\d{4})?x\.md"}})
        i("SessionStart", "s1", self.repo)
        i.account("bbbbbbbb-0000")
        (self.t / "rcpt" / "x.md").write_text("matches with the group unset\n", encoding="utf-8")
        r = i("SessionStart", "s2", self.repo)
        self.assertIn("not yet resumed", r.stdout)
        self.assertNotIn("failed (", r.stdout)
        bus = init_repo(self.t / "bus3")
        g(bus, "update-ref", "refs/remotes/origin/master", "HEAD")
        d = self.with_cfg({"doctrine": {"bus_clone": str(bus)}})
        tips = self.t / "home/.claude/session-checkpoints/doctrine-periodic"
        tips.mkdir(parents=True, exist_ok=True)
        for torn in ("garbage", "0" * 40):
            (tips / "s3.tip").write_text(torn, encoding="utf-8")
            r = d("SessionStart", "s3", self.repo)
            self.assertNotIn("doctrine check FAILED", r.stdout, torn)

    def test_values_that_break_validation_itself_cost_only_their_key(self):
        """Review round 2: 10**400 (OverflowError in isfinite) and a receipt pattern nested past the regex parser's
        limit (RecursionError) escaped the lenient fallback and the Stop checkpoint was never written."""
        deep = "(" * 2000 + "x" + ")" * 2000
        p = self.t / "big.json"
        p.write_text('{"deadline_seconds": 1' + "0" * 400 + ', "rotation": {"receipt_pattern": "' + deep + '"}}',
                     encoding="utf-8")
        r = Impl("x", [str(TOOL), "--config", str(p)], self.t / "home")("Stop", "o1", self.repo)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("deadline_seconds:", r.stdout)
        self.assertIn("rotation:", r.stdout)
        self.assertTrue((self.t / "home/.claude/session-checkpoints/proj/SESSION-o1.md").exists(), r.stdout)

    def test_fixtures_are_valid_configs(self):
        sys.path.insert(0, str(HERE))
        import importlib.util
        spec = importlib.util.spec_from_file_location("sc", TOOL)
        sc = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sc)
        for f in sorted(FIX.glob("*.config.json")):
            cfg = sc.load_config(str(f))
            self.assertEqual(cfg["_warnings"], [], f)       # per-key leniency must not hide a broken fixture key
            self.assertEqual(cfg["deadline_seconds"], 40, f)
        self.assertIsNotNone(sc.load_config(str(FIX / "dng.config.json"))["doctrine"])
        self.assertIsNone(sc.load_config(str(FIX / "default.config.json"))["doctrine"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
