#!/usr/bin/env python3
"""Tests for tools/cli-currency.py. Run: python tools/cli-currency.tests.py

The `World` tests drive the production entry points (`run_once`, `process_cli`, `smoke`) against a
simulated machine, so deleting a call site fails a test, not just changing a helper."""
import argparse
import importlib.util
import json
import os
import pathlib
import tempfile
import unittest
from unittest import mock

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("cli_currency", HERE / "cli-currency.py")
cc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cc)


class Versions(unittest.TestCase):
    def test_parses_both_cli_banners(self):
        self.assertEqual(cc.parse_version("2.1.268 (Claude Code)"), (2, 1, 268))
        self.assertEqual(cc.parse_version("codex-cli 0.154.0"), (0, 154, 0))
        self.assertIsNone(cc.parse_version("command not found"))

    def test_compares_numerically_not_lexically(self):
        self.assertLess(cc.parse_version("0.99.0"), cc.parse_version("0.156.1"))


class Classify(unittest.TestCase):
    def test_npm_prefix_wins(self):
        pre = os.path.join(tempfile.gettempdir(), "npmprefix")
        with mock.patch.object(cc, "WIN", True):
            self.assertEqual(cc.classify(os.path.join(pre, "codex.cmd"), pre), "npm")

    def test_prefix_is_a_directory_boundary_not_a_string_prefix(self):
        pre = os.path.join(tempfile.gettempdir(), "npm")
        self.assertNotEqual(cc.classify(os.path.join(tempfile.gettempdir(), "npm-other", "codex.cmd"), pre), "npm")

    def test_native_is_claude_only_and_winget_is_case_blind(self):
        self.assertEqual(cc.classify(str(cc.HOME / ".local" / "bin" / "claude.exe"), None), "native")
        self.assertEqual(cc.classify(str(cc.HOME / ".local" / "bin" / "codex"), None), "other")
        self.assertEqual(cc.classify(os.path.join(str(cc.HOME), "AppData", "Local", "Microsoft", "WinGet",
                                                  "Links", "codex.exe"), None), "winget")

    def test_unknown_install_is_never_upgraded(self):
        self.assertEqual(cc.classify("/opt/homebrew/bin/codex", None), "other")
        self.assertIsNone(cc.upgrade_cmd("codex", "other", "/opt/homebrew/bin/codex", "1.0.0"))

    def test_installs_finds_every_install_on_path_in_order(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            name = "codex.cmd" if os.name == "nt" else "codex"
            for d in (a, b):
                p = pathlib.Path(d, name)
                p.write_text("x")
                p.chmod(0o755)
            with mock.patch.dict(os.environ, {"PATH": os.pathsep.join([a, b, a + os.sep]), "PATHEXT": ".EXE;.CMD"}):
                found = cc.installs("codex")
        self.assertEqual([os.path.dirname(f) for f in found], [a, b])

    def test_path_dirs_dedupes_trailing_separators_and_quotes(self):
        d = tempfile.gettempdir()
        self.assertEqual(len(cc.path_dirs(os.pathsep.join([d, d + os.sep, f'"{d}"']))), 1)


class Upgrade(unittest.TestCase):
    def test_commands_pin_the_exact_target_version(self):
        self.assertIn("@openai/codex@0.156.1", cc.upgrade_cmd("codex", "npm", "x", "0.156.1"))
        self.assertEqual(cc.upgrade_cmd("claude", "native", "c.exe", "2.1.280"), ["c.exe", "install", "2.1.280"])
        self.assertIn("OpenAI.Codex", cc.upgrade_cmd("codex", "winget", "codex.exe", "0.156.1"))


class Models(unittest.TestCase):
    def test_diff_reports_only_new_ids_in_arrival_order(self):
        self.assertEqual(cc.diff_models(["a", "b"], ["d", "a", "c"]), ["d", "c"])

    def test_extracts_claude_ids_from_binary_bytes(self):
        blob = b"\x00claude-opus-5-5\x00xx claude-haiku-4-5-20251001 claude-fable-5-1 claudeX notclaude-"
        self.assertEqual(cc.claude_models_in(blob),
                         ["claude-fable-5-1", "claude-haiku-4-5-20251001", "claude-opus-5-5"])

    def test_resolve_tier_picks_highest_version_and_exact_tier(self):
        self.assertEqual(cc.resolve_tier(["gpt-6-solar", "gpt-5.6-sol", "gpt-6-sol"], "sol"), "gpt-6-sol")
        self.assertEqual(cc.resolve_tier(["gpt-5.6-sol", "gpt-5.10-sol"], "sol"), "gpt-5.10-sol")
        self.assertIsNone(cc.resolve_tier(["gpt-6-sol"], "luna"))


class SmokeParse(unittest.TestCase):
    def test_tolerates_trailing_output_after_json(self):
        out = json.dumps({"result": "READY", "is_error": False, "modelUsage": {"claude-haiku-4-5": {}}})
        self.assertEqual(cc.claude_smoke_ok(0, out + "\nDeprecationWarning: x\n"), (True, "claude-haiku-4-5"))

    def test_rejects_error_results_and_nonzero_rc(self):
        self.assertFalse(cc.claude_smoke_ok(0, json.dumps({"result": "READY", "is_error": True}))[0])
        self.assertFalse(cc.claude_smoke_ok(1, json.dumps({"result": "READY"}))[0])
        self.assertFalse(cc.claude_smoke_ok(0, json.dumps({"result": "NOT READY"}))[0])


class World:
    """A simulated machine: installs, npm latest, and which versions pass a smoke."""

    def __init__(self, installed, latest, broken=(), env_broken=False, rollback_fails=False):
        self.v = dict(installed)            # path -> version tuple
        self.latest = latest                # cli -> version tuple
        self.broken, self.env_broken, self.rollback_fails = set(broken), env_broken, rollback_fails
        self.calls = []

    def run(self, cmd, timeout=300, stdin=None, env=None):
        self.calls.append(cmd)
        target = None
        if "install" in cmd:
            npm = cmd[0].endswith("npm.cmd")
            arg = next(c for c in cmd if "@" in c[1:]) if npm else cmd[-1]
            target = cc.parse_version(arg)
        if target:
            paths = [p for p in self.v if (cmd[0] == p) or ("npm" in cmd[0] and p.endswith(".cmd"))]
            if self.rollback_fails and any(target < self.v[p] for p in paths):
                return 1, "", "EPERM"
            for p in paths:
                self.v[p] = target
        return 0, "", ""

    def smoke(self, cli, path, kind=""):
        ok = not self.env_broken and self.v[path] not in self.broken
        return {"ok": ok, "rc": 0 if ok else 1, "model": None}

    def patches(self):
        return [mock.patch.object(cc, "run", self.run), mock.patch.object(cc, "smoke", self.smoke),
                mock.patch.object(cc, "installed_version", lambda p: self.v[p]),
                mock.patch.object(cc, "installs", lambda n: [p for p in self.v if n in p]),
                mock.patch.object(cc, "latest", lambda pkg: self.latest["claude" if "claude" in pkg else "codex"]),
                mock.patch.object(cc, "npm_prefix", lambda: str(NPM)),
                mock.patch.object(cc, "npm_cmd", lambda: str(NPM / "npm.cmd")),
                mock.patch.object(cc, "codex_slugs", lambda: []),
                mock.patch.object(cc, "WIN", True)]


NPM = pathlib.Path(tempfile.gettempdir()) / "cc-world-npm"
CODEX = str(NPM / "codex.cmd")
CLAUDE = str(cc.HOME / ".local" / "bin" / "claude.exe")


class Flow(unittest.TestCase):
    def go(self, world, apply=True, state_dir=None):
        with tempfile.TemporaryDirectory() as td:
            sd = pathlib.Path(state_dir or td)
            with mock.patch.object(cc, "STATE", sd), mock.patch.object(cc, "HOLD_FILE", sd / "hold.json"):
                ps = world.patches()
                for p in ps:
                    p.start()
                try:
                    rc = cc.run_once(argparse.Namespace(apply=apply, json=False, resolve=None))
                finally:
                    for p in ps:
                        p.stop()
                return rc, json.loads((sd / "latest.json").read_text(encoding="utf-8"))

    def status(self, receipt, cli):
        return next(c for c in receipt["clis"] if c["cli"] == cli)

    def test_clean_upgrade_upgrades_every_install(self):
        w = World({CLAUDE: (2, 1, 268), CODEX: (0, 154, 0)}, {"claude": (2, 1, 280), "codex": (0, 156, 1)})
        rc, r = self.go(w)
        self.assertEqual(rc, 0)
        self.assertEqual(w.v, {CLAUDE: (2, 1, 280), CODEX: (0, 156, 1)})
        self.assertEqual(self.status(r, "codex")["status"], "UPGRADED")

    def test_current_install_is_left_alone(self):
        w = World({CODEX: (0, 156, 1)}, {"claude": (2, 1, 280), "codex": (0, 156, 1)})
        rc, r = self.go(w)
        self.assertFalse([c for c in w.calls if "install" in c])
        self.assertEqual(self.status(r, "codex")["status"], "CURRENT")

    def test_check_mode_changes_nothing(self):
        w = World({CODEX: (0, 154, 0)}, {"claude": (2, 1, 280), "codex": (0, 156, 1)})
        with mock.patch.object(cc, "sweep_npm_trash", side_effect=AssertionError("swept in check mode")):
            rc, r = self.go(w, apply=False)
        self.assertEqual(w.v[CODEX], (0, 154, 0))
        self.assertEqual(self.status(r, "codex")["status"], "DRIFT")

    def test_apply_mode_sweeps(self):
        w = World({CODEX: (0, 156, 1)}, {"claude": (2, 1, 280), "codex": (0, 156, 1)})
        with mock.patch.object(cc, "sweep_npm_trash", return_value=["x"]) as sw:
            self.go(w)
        sw.assert_called_once()

    def test_bad_release_rolls_back_and_is_held_next_run(self):
        w = World({CODEX: (0, 154, 0)}, {"claude": (2, 1, 280), "codex": (0, 156, 1)}, broken={(0, 156, 1)})
        with tempfile.TemporaryDirectory() as sd:
            rc, r = self.go(w, state_dir=sd)
            self.assertEqual((rc, self.status(r, "codex")["status"], w.v[CODEX]), (1, "ROLLED-BACK", (0, 154, 0)))
            self.assertEqual(r["rejected"], {"codex": "0.156.1"})
            w.calls.clear()
            rc, r = self.go(w, state_dir=sd)
            self.assertEqual(self.status(r, "codex")["status"], "HELD")
            self.assertFalse([c for c in w.calls if "install" in c])
            w.latest["codex"], w.calls = (0, 157, 0), []   # a newer release lifts the hold
            rc, r = self.go(w, state_dir=sd)
            self.assertEqual((self.status(r, "codex")["status"], r["rejected"]), ("UPGRADED", {}))

    def test_both_versions_failing_keeps_new_and_exits_1(self):
        w = World({CODEX: (0, 154, 0)}, {"claude": (2, 1, 280), "codex": (0, 156, 1)}, env_broken=True)
        rc, r = self.go(w)
        self.assertEqual((rc, self.status(r, "codex")["status"], w.v[CODEX]),
                         (1, "UPGRADED-ENVIRONMENT-SMOKE-FAILED", (0, 156, 1)))

    def test_failed_rollback_is_reported_not_disguised(self):
        w = World({CODEX: (0, 154, 0)}, {"claude": (2, 1, 280), "codex": (0, 156, 1)},
                  broken={(0, 156, 1)}, rollback_fails=True)
        rc, r = self.go(w)
        self.assertEqual((rc, self.status(r, "codex")["status"]), (1, "ROLLBACK-FAILED"))

    def test_fleet_hold_file_blocks_a_version(self):
        w = World({CODEX: (0, 154, 0)}, {"claude": (2, 1, 280), "codex": (0, 156, 1)})
        with tempfile.TemporaryDirectory() as sd:
            (pathlib.Path(sd) / "hold.json").write_text('{"codex": ["0.156.1"]}', encoding="utf-8")
            rc, r = self.go(w, state_dir=sd)
        self.assertEqual((self.status(r, "codex")["status"], w.v[CODEX]), ("HELD", (0, 154, 0)))

    def test_winget_lag_is_reported_not_current(self):
        wg = str(pathlib.Path(tempfile.gettempdir()) / "WinGet" / "Links" / "codex.exe")
        w = World({wg: (0, 144, 6)}, {"claude": (2, 1, 280), "codex": (0, 156, 1)})
        w.run = lambda cmd, timeout=300, stdin=None, env=None: (0, "No available upgrade found.", "")
        rc, r = self.go(w)
        self.assertEqual((rc, self.status(r, "codex")["status"]), (0, "WINGET-LAGS-NPM"))

    def test_npm_install_that_changes_nothing_is_a_failure_not_lag(self):
        w = World({CODEX: (0, 154, 0)}, {"claude": (2, 1, 280), "codex": (0, 156, 1)})
        w.run = lambda cmd, timeout=300, stdin=None, env=None: (0, "", "")
        rc, r = self.go(w)
        self.assertEqual((rc, self.status(r, "codex")["status"]), (1, "UPGRADE-FAILED"))

    def test_new_models_are_diffed_against_the_previous_run(self):
        w = World({CODEX: (0, 156, 1)}, {"claude": (2, 1, 280), "codex": (0, 156, 1)})
        with tempfile.TemporaryDirectory() as sd:
            with mock.patch.object(cc, "model_inventory", lambda p: {"codex": ["gpt-5.6-sol"], "claude": []}):
                self.go(w, state_dir=sd)
            with mock.patch.object(cc, "model_inventory", lambda p: {"codex": ["gpt-6-sol", "gpt-5.6-sol"], "claude": []}):
                _, r = self.go(w, state_dir=sd)
        self.assertEqual(r["new_models"], {"codex": ["gpt-6-sol"]})


class SmokeWiring(unittest.TestCase):
    def test_codex_smoke_uses_resolved_luna_and_reads_only_the_final_message(self):
        seen = {}

        def fake_run(cmd, timeout=300, stdin=None, env=None):
            seen["cmd"] = cmd
            pathlib.Path(cmd[cmd.index("-o") + 1]).write_text("NOT READY", encoding="utf-8")
            return 0, "", "user: Reply with exactly the word READY"   # stderr echoes the prompt

        with mock.patch.object(cc, "run", fake_run), \
                mock.patch.object(cc, "codex_slugs", lambda: ["gpt-5.6-luna", "gpt-6-luna", "gpt-6-sol"]):
            s = cc.smoke("codex", "codex.cmd")
        self.assertEqual(seen["cmd"][seen["cmd"].index("-m") + 1], "gpt-6-luna")
        self.assertIn("--ephemeral", seen["cmd"])
        self.assertFalse(s["ok"])

    def test_claude_smoke_is_isolated_from_user_hooks(self):
        seen = {}

        def fake_run(cmd, timeout=300, stdin=None, env=None):
            seen["cmd"], seen["env"] = cmd, env
            return 0, json.dumps({"result": "READY", "is_error": False}), ""

        with mock.patch.object(cc, "run", fake_run):
            self.assertTrue(cc.smoke("claude", "claude.exe")["ok"])
        self.assertIn('{"disableAllHooks":true}', seen["cmd"])
        self.assertIn("--no-session-persistence", seen["cmd"])
        self.assertEqual(seen["env"].get("CLI_CURRENCY_SMOKE"), "1")


class Lock(unittest.TestCase):
    def test_live_holder_is_not_evicted_and_dead_holder_is(self):
        with tempfile.TemporaryDirectory() as td:
            lock = pathlib.Path(td) / "run.lock"
            lock.write_text(str(os.getpid()))            # this process is alive
            self.assertFalse(cc.acquire_lock(lock))
            lock.write_text("999999999")                 # no such pid
            self.assertTrue(cc.acquire_lock(lock))
            self.assertEqual(lock.read_text(), str(os.getpid()))

    def test_release_only_removes_own_lock(self):
        with tempfile.TemporaryDirectory() as td:
            lock = pathlib.Path(td) / "run.lock"
            lock.write_text("12345")
            cc.release_lock(lock)
            self.assertTrue(lock.exists())


class Sweep(unittest.TestCase):
    def test_removes_only_npm_trash_dirs(self):
        with tempfile.TemporaryDirectory() as pre:
            root = pathlib.Path(pre) / ("node_modules" if os.name == "nt" else "lib/node_modules")
            (root / "@openai" / ".codex-abc123").mkdir(parents=True)
            (root / "@openai" / "codex").mkdir()
            (root / "@anthropic-ai" / ".claude-code-x1").mkdir(parents=True)
            swept = cc.sweep_npm_trash(pre)
            self.assertEqual(len(swept), 2)
            self.assertTrue((root / "@openai" / "codex").is_dir())


if __name__ == "__main__":
    unittest.main()
