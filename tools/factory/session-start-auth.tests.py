#!/usr/bin/env python3
"""Tests for tools/factory/session-start-auth.py.   python tools/factory/session-start-auth.tests.py"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parent / "session-start-auth.py"


class SessionStartAuth(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main(verbosity=1)
