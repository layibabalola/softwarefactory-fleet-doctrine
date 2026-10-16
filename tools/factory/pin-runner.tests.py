#!/usr/bin/env python3
"""Tests for tools/factory/pin-runner.py.   python tools/factory/pin-runner.tests.py

A throwaway bus repository and a throwaway consumer (with the runner vendored into
factory-pins/) exercise pin, adopt-runner, verify, status and run end to end.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RUNNER = Path(__file__).resolve().parent / "pin-runner.py"
TOOL_V1 = (b"import sys\ndata = sys.stdin.read()\nprint('v1', sys.argv[1:], len(data))\n"
           b"sys.exit(int(sys.argv[1]) if sys.argv[1:] and sys.argv[1].isdigit() else 0)\n")
TOOL_V2 = b"print('v2')\n"


def git(repo: Path, *a: str) -> str:
    return subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@example.invalid", "-c", "user.name=t",
                           "-c", "core.autocrlf=false", *a], check=True, capture_output=True, text=True).stdout.strip()


def _force(func, path, _exc):
    os.chmod(path, 0o700)  # git marks objects read-only; Windows refuses to delete them otherwise
    func(path)


class PinRunner(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        t = Path(self._tmp.name)
        self.bus, self.consumer = t / "bus", t / "consumer"
        self.cache = t / "cache"
        self.bus.mkdir()
        git(self.bus, "init", "-q")
        (self.bus / "tools" / "factory").mkdir(parents=True)
        (self.bus / "tools" / "factory" / "echo.py").write_bytes(TOOL_V1)
        # The fake bus commits with core.autocrlf=false, so it must hold the runner as the real bus blob
        # is: LF. A Windows autocrlf checkout of this file is CRLF on disk; committing that would make
        # every adopt/verify mismatch here although the runner itself compares as LF (own_bytes()).
        (self.bus / "tools" / "factory" / "pin-runner.py").write_bytes(RUNNER.read_bytes().replace(b"\r\n", b"\n"))
        git(self.bus, "add", "-A")
        git(self.bus, "commit", "-qm", "v1")
        git(self.bus, "update-ref", "refs/remotes/origin/master", "HEAD")
        self.c1 = git(self.bus, "rev-parse", "HEAD")
        self.consumer.mkdir()
        git(self.consumer, "init", "-q")
        (self.consumer / "factory-pins").mkdir()
        # Vendored as the install contract says: the bus blob's bytes (LF). test_crlf_checkout_... then
        # makes the CRLF variant itself; starting from a CRLF working copy would double the CRs.
        (self.consumer / "factory-pins" / "pin-runner.py").write_bytes(RUNNER.read_bytes().replace(b"\r\n", b"\n"))
        self.pins = self.consumer / "factory-pins" / "factory-pins.json"
        self.pins.write_text(json.dumps({"schema": "factory-pins.v1", "bus_clone": ["../bus"], "tools": {}}), encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def run_pr(self, *a: str, stdin: str = "", cwd: Path | None = None, isolated: bool = False) -> subprocess.CompletedProcess:
        # The blob cache lives in this test's temp dir: a test never reads or writes the host's cache.
        env = {**os.environ, "FACTORY_PINS_CACHE": str(self.cache)}
        env.pop("FACTORY_BUS_CLONE", None)
        return subprocess.run([sys.executable, *(["-I"] if isolated else []),
                               str(self.consumer / "factory-pins" / "pin-runner.py"), *a], input=stdin,
                              capture_output=True, text=True, cwd=str(cwd or self.consumer), env=env)

    def pin_echo(self):
        p = self.run_pr("pin", "echo", "--commit", self.c1, "--path", "tools/factory/echo.py",
                        "--reviewer", "tester", "--reason", "fixture")
        self.assertEqual(p.returncode, 0, p.stderr)
        p = self.run_pr("adopt-runner", "--commit", self.c1)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)

    def test_pin_verify_run_passes_args_stdin_and_exit_code(self):
        self.pin_echo()
        self.assertEqual(self.run_pr("verify").returncode, 0)
        p = self.run_pr("run", "echo", "--", "7", "--config", "x.json", stdin="abc")
        self.assertEqual(p.returncode, 7)
        self.assertIn("v1 ['7', '--config', 'x.json'] 3", p.stdout)
        p = self.run_pr("run", "echo", "--json")
        self.assertEqual((p.returncode, "['--json']" in p.stdout), (0, True))

    def test_tampered_pin_refuses_and_runs_nothing(self):
        self.pin_echo()
        pins = json.loads(self.pins.read_text(encoding="utf-8"))
        pins["tools"]["echo"]["sha256"] = "0" * 64
        self.pins.write_text(json.dumps(pins), encoding="utf-8")
        p = self.run_pr("run", "echo", stdin="")
        self.assertEqual((p.returncode, "v1" in p.stdout), (2, False))
        self.assertEqual(self.run_pr("verify").returncode, 2)

    def test_malformed_pins_refuse(self):
        self.pins.write_text('{"schema": "factory-pins.v1", "tools": {"echo": {"path": "../x"}}}', encoding="utf-8")
        self.assertEqual(self.run_pr("run", "echo").returncode, 2)
        self.pins.write_text('{"schema": "factory-pins.v1", "tools": {}, "tools": {}}', encoding="utf-8")
        self.assertEqual(self.run_pr("status").returncode, 2)

    def test_unknown_tool_refuses(self):
        self.pin_echo()
        self.assertEqual(self.run_pr("run", "nope").returncode, 2)

    def test_missing_clone_or_blob_is_unavailable_not_refused(self):
        self.pin_echo()
        self.assertEqual(self.run_pr("--bus", str(self.consumer / "absent"), "run", "echo").returncode, 3)
        pins = json.loads(self.pins.read_text(encoding="utf-8"))
        pins["bus_clone"] = ["../nowhere"]
        self.pins.write_text(json.dumps(pins), encoding="utf-8")
        self.assertEqual(self.run_pr("run", "echo").returncode, 3)
        pins["bus_clone"] = ["../bus"]
        data = b"print('never committed')\n"
        import hashlib
        pins["tools"]["echo"].update(blob=hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest(),
                                     bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        self.pins.write_text(json.dumps(pins), encoding="utf-8")
        self.assertEqual(self.run_pr("run", "echo").returncode, 3)

    def test_bus_change_is_stale_never_upgraded(self):
        self.pin_echo()
        (self.bus / "tools" / "factory" / "echo.py").write_bytes(TOOL_V2)
        git(self.bus, "commit", "-qam", "v2")
        git(self.bus, "update-ref", "refs/remotes/origin/master", "HEAD")
        st = self.run_pr("status")
        self.assertEqual(st.returncode, 0)
        self.assertIn("*** STALE ***", st.stdout)
        p = self.run_pr("run", "echo", "--", "0")
        self.assertIn("v1", p.stdout)
        self.assertNotIn("v2", p.stdout)

    def test_runner_drift_is_reported(self):
        self.pin_echo()
        r = self.consumer / "factory-pins" / "pin-runner.py"
        r.write_bytes(r.read_bytes() + b"\n# local edit\n")
        self.assertEqual(self.run_pr("verify").returncode, 2)

    def test_crlf_checkout_of_runner_still_verifies(self):
        self.pin_echo()
        r = self.consumer / "factory-pins" / "pin-runner.py"
        r.write_bytes(r.read_bytes().replace(b"\n", b"\r\n"))
        self.assertEqual(self.run_pr("verify").returncode, 0)

    def test_pins_ref_reads_the_committed_pins(self):
        self.pin_echo()
        git(self.consumer, "add", "factory-pins")
        git(self.consumer, "commit", "-qm", "pins")
        self.pins.write_text(json.dumps({"schema": "factory-pins.v1", "bus_clone": ["../bus"], "tools": {}}), encoding="utf-8")
        self.assertEqual(self.run_pr("run", "echo").returncode, 2)  # worktree pins no longer name it
        p = self.run_pr("--pins-ref", "HEAD", "run", "echo", "--", "0")
        self.assertEqual((p.returncode, "v1" in p.stdout), (0, True))

    def test_pinning_the_runner_as_a_tool_refuses(self):
        p = self.run_pr("pin", "pin-runner", "--commit", self.c1, "--path", "tools/factory/pin-runner.py",
                        "--reviewer", "t", "--reason", "r")
        self.assertEqual(p.returncode, 2)


    def test_pins_ref_from_a_linked_worktree_hook_environment(self):
        # Regression (verifier 2026-10-16): git exports GIT_DIR to a hook run from a linked worktree. With it
        # set, `git -C factory-pins rev-parse --show-toplevel` answered factory-pins/ itself, so --pins-ref
        # looked up <ref>:factory-pins.json and refused EVERY push from a worktree (exit 2).
        self.pin_echo()
        git(self.consumer, "add", "factory-pins")
        git(self.consumer, "commit", "-qm", "pins")
        wt = self.consumer.parent / "wt"
        git(self.consumer, "worktree", "add", "-q", "--detach", str(wt))
        gitdir = git(wt, "rev-parse", "--absolute-git-dir")
        env = {**os.environ, "FACTORY_PINS_CACHE": str(self.cache), "GIT_DIR": gitdir}
        env.pop("FACTORY_BUS_CLONE", None)
        for iso in ([], ["-I"]):
            p = subprocess.run([sys.executable, *iso, str(wt / "factory-pins" / "pin-runner.py"),
                                "--pins", str(wt / "factory-pins" / "factory-pins.json"), "--pins-ref", "HEAD",
                                "run", "echo", "--", "0"], capture_output=True, text=True, cwd=str(wt), env=env)
            self.assertEqual((p.returncode, "v1" in p.stdout), (0, True), p.stderr)

    def test_isolated_runner_executes_in_process_with_same_contract(self):
        self.pin_echo()
        p = self.run_pr("run", "echo", "--", "7", "--config", "x.json", stdin="abc", isolated=True)
        self.assertEqual(p.returncode, 7, p.stderr)
        self.assertIn("v1 ['7', '--config', 'x.json'] 3", p.stdout)
        self.assertEqual(self.run_pr("run", "echo", "--", "0", isolated=True).returncode, 0)

    def test_cache_keeps_reviewed_bytes_running_without_the_clone(self):
        self.pin_echo()
        self.assertEqual(self.run_pr("run", "echo", "--", "0").returncode, 0)  # populates the cache
        shutil.rmtree(self.bus, onerror=_force)  # clone gone: the verified cached copy still runs
        for iso in (False, True):
            p = self.run_pr("run", "echo", "--", "5", isolated=iso)
            self.assertEqual((p.returncode, "v1" in p.stdout), (5, True), p.stderr)

    def test_tampered_cache_never_runs(self):
        self.pin_echo()
        blob = json.loads(self.pins.read_text(encoding="utf-8"))["tools"]["echo"]["blob"]
        self.cache.mkdir(parents=True, exist_ok=True)
        for iso in (False, True):
            (self.cache / blob).write_bytes(b"print('EVIL')\n")
            p = self.run_pr("run", "echo", "--", "0", isolated=iso)  # bus present: the clone's verified bytes run
            self.assertEqual((p.returncode, "v1" in p.stdout, "EVIL" in p.stdout), (0, True, False), p.stderr)
        (self.cache / blob).write_bytes(b"print('EVIL')\n")
        shutil.rmtree(self.bus, onerror=_force)
        p = self.run_pr("run", "echo", "--", "0", isolated=True)  # bus absent: unavailable, never the tampered copy
        self.assertEqual((p.returncode, "EVIL" in p.stdout), (3, False))

if __name__ == "__main__":
    unittest.main(verbosity=1)
