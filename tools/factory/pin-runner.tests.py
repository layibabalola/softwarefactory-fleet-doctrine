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


def git_blob(repo: Path, rev: str, path: str) -> bytes:
    return subprocess.run(["git", "-C", str(repo), "cat-file", "blob", f"{rev}:{path}"], check=True, capture_output=True).stdout


class Install(unittest.TestCase):
    """`install`: one command to become a consumer. The bus's own runner is the installer; the project starts empty."""
    SIDE = b"open('ran.marker', 'w').write('x')\nprint('side-effect tool ran')\n"

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        t = Path(self._tmp.name)
        self.bus, self.proj, self.cache, self.elsewhere = t / "bus", t / "proj", t / "cache", t / "elsewhere"
        for d in (self.bus / "tools" / "factory", self.proj, self.elsewhere):
            d.mkdir(parents=True)
        git(self.bus, "init", "-q")
        f = self.bus / "tools" / "factory"
        (f / "echo.py").write_bytes(TOOL_V1)
        (f / "side.py").write_bytes(self.SIDE)
        (f / "pin-runner.py").write_bytes(RUNNER.read_bytes().replace(b"\r\n", b"\n"))
        self.write_registry({"echo": "tools/factory/echo.py", "side": "tools/factory/side.py"})
        git(self.bus, "add", "-A")
        git(self.bus, "commit", "-qm", "v1")
        self.c1 = git(self.bus, "rev-parse", "HEAD")
        git(self.proj, "init", "-q")
        self.pins = self.proj / "factory-pins" / "factory-pins.json"
        self.runner = self.proj / "factory-pins" / "pin-runner.py"

    def tearDown(self):
        self._tmp.cleanup()

    def write_registry(self, tools: dict, interpreter: str = "python"):
        reg = {"schema": "factory-registry.v1",
               "tools": {n: {"path": p, "interpreter": interpreter, "purpose": f"{n} fixture"} for n, p in tools.items()}}
        (self.bus / "tools" / "factory" / "registry.json").write_text(json.dumps(reg), encoding="utf-8")

    def sh(self, script: Path, *a: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
        env = {**os.environ, "FACTORY_PINS_CACHE": str(self.cache)}
        env.pop("FACTORY_BUS_CLONE", None)
        return subprocess.run([sys.executable, str(script), *a], capture_output=True, text=True, cwd=str(cwd or self.elsewhere), env=env)

    def install(self, tool: str, commit: str | None = None, *extra: str) -> subprocess.CompletedProcess:
        return self.sh(self.bus / "tools" / "factory" / "pin-runner.py", "install", tool, "--commit", commit or self.c1,
                       "--reviewer", "tester", "--reason", "fixture", "--project-root", str(self.proj), "--bus", str(self.bus), *extra)

    def test_install_makes_a_working_consumer(self):
        p = self.install("echo")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("WIRE: python factory-pins/pin-runner.py run echo --", p.stdout)
        self.assertEqual(self.runner.read_bytes(), git_blob(self.bus, self.c1, "tools/factory/pin-runner.py"))
        pins = json.loads(self.pins.read_text(encoding="utf-8"))
        self.assertEqual((pins["tools"]["echo"]["commit"], pins["runner"]["commit"], pins["bus_clone"]), (self.c1, self.c1, ["../bus"]))
        self.assertEqual(self.sh(self.runner, "verify", cwd=self.proj).returncode, 0)  # runner adopted, clone recorded, tool pinned
        r = self.sh(self.runner, "run", "echo", "--", "3", cwd=self.proj)
        self.assertEqual((r.returncode, "v1 ['3']" in r.stdout), (3, True))

    def test_reinstall_same_commit_is_a_noop_and_a_new_commit_repins_with_a_diff(self):
        self.assertEqual(self.install("echo").returncode, 0)
        before = {q: q.read_bytes() for q in (self.pins, self.runner)}
        p = self.install("echo")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("NO-OP", p.stdout)
        self.assertEqual(before, {q: q.read_bytes() for q in before})
        (self.bus / "tools" / "factory" / "echo.py").write_bytes(TOOL_V2)
        git(self.bus, "commit", "-qam", "v2")
        c2 = git(self.bus, "rev-parse", "HEAD")
        p = self.install("echo", c2)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("RE-PINNED", p.stdout)
        self.assertIn(f"~ commit: {self.c1[:12]} -> {c2[:12]}", p.stdout)
        self.assertIn("~ blob:", p.stdout)
        self.assertEqual(json.loads(self.pins.read_text(encoding="utf-8"))["tools"]["echo"]["commit"], c2)
        self.assertEqual(self.runner.read_bytes(), before[self.runner], "an adopted runner is never overwritten by a re-pin")
        self.assertIn("v2", self.sh(self.runner, "run", "echo", cwd=self.proj).stdout)

    def test_unknown_tool_and_unregistered_commit_refuse_and_write_nothing(self):
        p = self.install("nope")
        self.assertEqual(p.returncode, 2)
        self.assertIn("echo", p.stderr)  # names what the registry does list
        self.assertFalse((self.proj / "factory-pins").exists())
        self.assertEqual(self.install("pin-runner").returncode, 2)
        git(self.bus, "rm", "-q", "tools/factory/registry.json")
        git(self.bus, "commit", "-qm", "no registry")
        self.assertEqual(self.install("echo", git(self.bus, "rev-parse", "HEAD")).returncode, 2)
        self.assertFalse((self.proj / "factory-pins").exists())

    def test_malformed_registry_refuses(self):
        for bad in ('{"schema": "factory-registry.v1", "tools": {"echo": {"path": "../x", "interpreter": "python", "purpose": "p"}}}',
                    '{"schema": "factory-registry.v1", "tools": {"echo": {"path": "tools/factory/echo.py", "interpreter": "bash", "purpose": "p"}}}',
                    '{"schema": "factory-registry.v1", "tools": {"echo": {"path": "tools/factory/echo.py", "interpreter": "python"}}}',
                    '{"schema": "factory-registry.v1", "tools": {}, "tools": {}}'):
            (self.bus / "tools" / "factory" / "registry.json").write_text(bad, encoding="utf-8")
            git(self.bus, "commit", "-qam", "bad registry")
            self.assertEqual(self.install("echo", git(self.bus, "rev-parse", "HEAD")).returncode, 2, bad)
        self.assertFalse((self.proj / "factory-pins").exists())

    def test_install_never_executes_the_tool_and_run_is_the_only_executor(self):
        for where in (self.elsewhere, self.proj):
            (where / "ran.marker").unlink(missing_ok=True)
        p = self.install("side")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertNotIn("side-effect tool ran", p.stdout + p.stderr)
        self.assertEqual([(self.elsewhere / "ran.marker").exists(), (self.proj / "ran.marker").exists()], [False, False])
        r = self.sh(self.runner, "run", "side", cwd=self.proj)  # the control: the same bytes DO leave the marker through `run`
        self.assertEqual((r.returncode, (self.proj / "ran.marker").exists()), (0, True))

    def test_modified_vendored_runner_is_not_overwritten_or_adopted(self):
        self.runner.parent.mkdir()
        self.runner.write_bytes(RUNNER.read_bytes().replace(b"\r\n", b"\n") + b"\n# local edit\n")
        p = self.install("echo")
        self.assertEqual(p.returncode, 2)
        self.assertIn("neither adopted nor byte-identical", p.stderr)
        self.assertTrue(self.runner.read_bytes().endswith(b"# local edit\n"))
        self.assertFalse(self.pins.exists())

    def test_tampered_running_runner_refuses_before_writing_anything(self):
        # Law 1 on the installer: the bytes RUNNING install must be the reviewed blob at --commit.
        edited = (RUNNER.read_bytes().replace(b"\r\n", b"\n")) + b"\nprint('UNREVIEWED INSTALLER CODE')\n"
        tampered = self.elsewhere / "tampered-runner.py"
        tampered.write_bytes(edited)
        p = self.sh(tampered, "install", "echo", "--commit", self.c1, "--reviewer", "t", "--reason", "r",
                    "--project-root", str(self.proj), "--bus", str(self.bus))
        self.assertEqual(p.returncode, 2)
        self.assertNotIn("UNREVIEWED", p.stdout)
        self.assertIn("not byte-identical", p.stderr)
        self.assertFalse((self.proj / "factory-pins").exists())
        # The reviewed repro: a bus WORKTREE that moved past (or edits) the reviewed commit is not the installer.
        bus_runner = self.bus / "tools" / "factory" / "pin-runner.py"
        bus_runner.write_bytes(edited)
        p = self.install("echo")
        self.assertEqual((p.returncode, "UNREVIEWED" in p.stdout), (2, False))
        self.assertFalse((self.proj / "factory-pins").exists())

    def _module(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("pin_runner_under_test", RUNNER)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def _args(self, mod, **kw):
        import argparse
        return argparse.Namespace(tool="echo", project_root=str(self.proj), pins=None, bus=str(self.bus), commit=self.c1,
                                  reviewer="t", reason="r", date="2026-10-16", **kw)

    def test_corrupted_object_bytes_refuse_and_vendor_nothing(self):
        mod = self._module()
        real = mod.git
        target = ("cat-file", "blob", f"{self.c1}:tools/factory/pin-runner.py")

        def corrupt(repo, *a, **kw):
            p = real(repo, *a, **kw)
            return subprocess.CompletedProcess(p.args, 0, p.stdout + b"\n# substituted object bytes\n", p.stderr) if a == target else p
        mod.git = corrupt
        with self.assertRaises(mod.Refused) as cm:
            mod.cmd_install(self._args(mod), [])
        self.assertIn("not object", str(cm.exception))
        self.assertFalse((self.proj / "factory-pins").exists())
        mod.git = real  # control: the same call without the fault installs
        import contextlib, io
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(mod.cmd_install(self._args(mod), []), 0)
        self.assertTrue(self.runner.is_file())

    def test_vendored_file_that_does_not_read_back_as_the_blob_is_removed(self):
        mod = self._module()
        real_write = Path.write_bytes
        Path.write_bytes = lambda self_, data: real_write(self_, b"print('swapped')\n")
        try:
            with self.assertRaises(mod.Refused) as cm:
                mod.cmd_install(self._args(mod), [])
        finally:
            Path.write_bytes = real_write
        self.assertIn("does not hold the reviewed runner", str(cm.exception))
        self.assertFalse(self.runner.exists())
        self.assertFalse(self.pins.exists())

    def test_bootstrap_from_the_reviewed_blob_installs(self):
        self.runner.parent.mkdir()
        self.runner.write_bytes(git_blob(self.bus, self.c1, "tools/factory/pin-runner.py"))  # git show <sha>:path > factory-pins/pin-runner.py
        p = self.sh(self.runner, "install", "echo", "--commit", self.c1, "--reviewer", "t", "--reason", "r",
                    "--bus", str(self.bus), cwd=self.proj)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("adopted runner", p.stdout)
        self.assertEqual(self.sh(self.runner, "verify", cwd=self.proj).returncode, 0)

    def test_list_prints_the_registry(self):
        p = self.sh(self.bus / "tools" / "factory" / "pin-runner.py", "list", "--bus", str(self.bus))
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("echo\tpython\ttools/factory/echo.py\techo fixture", p.stdout)
        self.assertIn("side\tpython", p.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=1)
