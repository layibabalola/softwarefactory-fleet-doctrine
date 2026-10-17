#!/usr/bin/env python3
"""Tests for tools/factory/session-start-auth.py.   python tools/factory/session-start-auth.tests.py"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parent / "session-start-auth.py"


class _Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "coordination" / "tools").mkdir(parents=True)

    def tearDown(self):
        self._tmp.cleanup()

    def checker(self, code: int, text: str = "verdict", rel: str = "coordination/tools/check-cli-auth.py"):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"import sys\nprint({text!r} + ' ' + ' '.join(sys.argv[1:]))\nsys.exit({code})\n", encoding="utf-8")

    def run_tool(self, *args: str, cwd: Path | None = None, project: bool = True) -> subprocess.CompletedProcess:
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
        if project:
            env["CLAUDE_PROJECT_DIR"] = str(self.root)
        return subprocess.run([sys.executable, str(TOOL), *args], capture_output=True, text=True, env=env,
                              cwd=str(cwd or Path(tempfile.gettempdir())))


class SessionStartAuth(_Base):
    def test_green_is_surfaced_and_capacity_unproven(self):
        self.checker(0, "MATCHED")
        r = self.run_tool()
        self.assertEqual(r.returncode, 0)
        self.assertIn("identity-only (exit 0): MATCHED", r.stdout)
        self.assertIn("capacity UNPROVEN", r.stdout)

    def test_red_is_surfaced_never_repaired_and_exits_zero(self):
        self.checker(3, "ACCOUNT_MISMATCH")
        r = self.run_tool("--repair-hint", "do-the-thing")
        self.assertEqual(r.returncode, 0, "a SessionStart hook always exits 0")
        self.assertIn("(exit 3): ACCOUNT_MISMATCH", r.stdout)
        self.assertIn("NOT auto-remedying", r.stdout)
        self.assertIn("do-the-thing", r.stdout)
        self.assertNotIn("auth logout", r.stdout)

    def test_live_passes_the_probe_flag(self):
        self.checker(0, "LIVE")
        r = self.run_tool("--live")
        self.assertIn("live probe (exit 0): LIVE --allow-live-probe", r.stdout)
        self.assertNotIn("capacity UNPROVEN", r.stdout)

    def test_missing_checker_and_custom_path(self):
        r = self.run_tool()
        self.assertEqual(r.returncode, 0)
        self.assertRegex(r.stdout, r"\(exit (1|2|127)\)")
        self.checker(0, "CUSTOM", rel="tools/check.py")
        self.assertIn("CUSTOM", self.run_tool("--checker", "tools/check.py").stdout)

    def test_root_from_git_toplevel_without_claude_project_dir(self):
        self.checker(0, "TOPLEVEL")
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        sub = self.root / "coordination"
        r = self.run_tool(cwd=sub, project=False)
        self.assertIn("TOPLEVEL", r.stdout)


# A stand-in guard: exits 2 when the PreToolUse payload's command is argv[2], else exits argv[3] (default 0).
GUARD = (b"import json, sys\nd = json.load(sys.stdin)\n"
         b"sys.exit(2 if d['tool_input']['command'] == sys.argv[2] else int(sys.argv[3]) if sys.argv[3:] else 0)\n")


class GuardSelfTest(_Base):
    """Upstreamed from Conjugal bc8645fe9: each Bash|PowerShell PreToolUse hook must refuse a known fixture."""

    def setUp(self):
        super().setUp()
        self.checker(0, "MATCHED")
        (self.root / "guard.py").write_bytes(GUARD)
        self.py = sys.executable.replace("\\", "/")

    def hook(self, key: str, refuses: str, else_code: int = 0) -> dict:
        return {"type": "command", "command": f'"{self.py}" "$CLAUDE_PROJECT_DIR/guard.py" {key} "{refuses}" {else_code}'}

    def settings(self, *groups: dict, rel: str = ".claude/settings.json"):
        f = self.root / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps({"hooks": {"PreToolUse": list(groups)}}), encoding="utf-8")

    def test_guards_that_refuse_their_default_fixture_pass(self):
        self.settings({"matcher": "Bash|PowerShell", "hooks": [self.hook("exact-path-add", "git add -A"),
                                                               self.hook("git-optional-locks", "git status")]})
        r = self.run_tool()
        self.assertEqual(r.returncode, 0)
        self.assertIn("PreToolUse guard self-test: 2 refused, 0 FAILED OPEN", r.stdout)
        self.assertNotIn("REFUSING", r.stdout)

    def test_a_guard_that_fails_open_is_reported_and_the_hook_still_exits_zero(self):
        self.settings({"matcher": "Bash", "hooks": [self.hook("exact-path-add", "something else"),
                                                    self.hook("git-optional-locks", "other", 3)]})
        r = self.run_tool()
        self.assertEqual(r.returncode, 0, "a SessionStart hook always exits 0")
        self.assertIn("0 refused, 2 FAILED OPEN", r.stdout)
        self.assertIn("exited 0 (not 2) on known-refuse fixture 'git add -A'", r.stdout)
        self.assertIn("exited 3 (not 2) on known-refuse fixture 'git status'", r.stdout)

    def test_a_launcher_that_cannot_start_fails_open_loudly(self):
        self.settings({"matcher": "Bash", "hooks": [{"type": "command",
                                                     "command": "no-such-launcher-xyz run exact-path-add"}]})
        r = self.run_tool()
        self.assertIn("0 refused, 1 FAILED OPEN", r.stdout)
        self.assertIn("REFUSING: PreToolUse guard exited", r.stdout)

    def test_untested_hooks_and_other_matchers(self):
        self.settings({"matcher": ".*", "hooks": [self.hook("exact-path-add", "nope")]},
                      {"matcher": "Write|Edit", "hooks": [self.hook("exact-path-add", "nope")]},
                      {"matcher": "PowerShell", "hooks": [self.hook("some-new-guard", "x")]})
        r = self.run_tool()
        self.assertIn("0 refused, 0 FAILED OPEN", r.stdout)
        self.assertIn("UNTESTED (no fixture)", r.stdout)
        self.assertIn("some-new-guard", r.stdout)

    def test_consumer_config_fixtures_text_and_settings_path(self):
        (self.root / "cfg.json").write_text(json.dumps({
            "schema": "session-start-auth.v1", "verified_text": "GREEN, custom",
            "guard_fixtures": {"git-optional-locks": None, "my-guard": "rm -rf /x"},
            "settings": "alt/settings.json"}), encoding="utf-8")
        self.settings({"matcher": "Bash", "hooks": [self.hook("my-guard", "rm -rf /x"),
                                                    self.hook("git-optional-locks", "git status")]},
                      rel="alt/settings.json")
        r = self.run_tool("--config", "cfg.json")
        self.assertIn("[session-start] GREEN, custom", r.stdout)
        self.assertNotIn("AUTH VERIFIED.", r.stdout)
        self.assertIn("1 refused, 0 FAILED OPEN", r.stdout)
        self.assertIn("UNTESTED (no fixture)", r.stdout)  # the removed default

    def test_malformed_config_is_reported_and_defaults_stand(self):
        self.settings({"matcher": "Bash", "hooks": [self.hook("exact-path-add", "git add -A")]})
        for body in ("{not json", json.dumps({"guard_fixtures": {"x": 3}}), json.dumps({"surprise": 1}),
                     json.dumps({"schema": "other"})):
            (self.root / "cfg.json").write_text(body, encoding="utf-8")
            with self.subTest(body=body):
                r = self.run_tool("--config", "cfg.json")
                self.assertEqual(r.returncode, 0)
                self.assertIn("REFUSING: config", r.stdout)
                self.assertIn("AUTH VERIFIED.", r.stdout)
                self.assertIn("1 refused, 0 FAILED OPEN", r.stdout)

    def test_unreadable_settings_is_refusing_and_opt_out_skips(self):
        (self.root / ".claude").mkdir()
        (self.root / ".claude" / "settings.json").write_text("{broken", encoding="utf-8")
        self.assertIn("REFUSING: guard self-test could not read", self.run_tool().stdout)
        self.assertNotIn("guard self-test", self.run_tool("--no-guard-self-test").stdout)

if __name__ == "__main__":
    unittest.main(verbosity=1)
