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


class _Fixture(unittest.TestCase):
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

class PinRunner(_Fixture):
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

class WorkingCopyFallback(_Fixture):
    """Regression (Conjugal 2026-10-16): mid-merge, factory-pins.json held conflict markers; every PreToolUse hook
    run through the runner refused (invalid JSON, exit 2), so every shell command was blocked -- including the
    ones that resolve the conflict. `run` now judges with the pins committed at HEAD; never with no guard."""

    def commit_pins(self):
        self.pin_echo()
        git(self.consumer, "add", "factory-pins")
        git(self.consumer, "commit", "-qm", "pins")

    def assert_fallback_runs(self, p):
        self.assertEqual((p.returncode, "v1" in p.stdout), (0, True), p.stderr)
        self.assertIn("FALLBACK", p.stderr)

    def test_a_real_merge_conflict_in_the_pins_runs_with_heads_pins(self):
        self.commit_pins()
        base = git(self.consumer, "rev-parse", "--abbrev-ref", "HEAD")
        git(self.consumer, "checkout", "-qb", "side")
        pins = json.loads(self.pins.read_text(encoding="utf-8"))
        pins["tools"]["echo"]["reason"] = "side"
        self.pins.write_text(json.dumps(pins, indent=2), encoding="utf-8")
        git(self.consumer, "commit", "-qam", "side")
        git(self.consumer, "checkout", "-q", base)
        pins["tools"]["echo"]["reason"] = "main"
        self.pins.write_text(json.dumps(pins, indent=2), encoding="utf-8")
        git(self.consumer, "commit", "-qam", "main")
        m = subprocess.run(["git", "-C", str(self.consumer), "-c", "user.email=t@example.invalid", "-c", "user.name=t",
                            "merge", "side"], capture_output=True, text=True)
        self.assertNotEqual(m.returncode, 0)
        self.assertIn(b"<<<<<<<", self.pins.read_bytes())
        for iso in (False, True):
            self.assert_fallback_runs(self.run_pr("run", "echo", "--", "0", isolated=iso))
        # verify and status stay strict: they report on the working copy, they do not judge a command
        self.assertEqual(self.run_pr("verify").returncode, 2)

    def test_torn_json_runs_with_heads_pins(self):
        self.commit_pins()
        self.pins.write_bytes(self.pins.read_bytes()[:40])
        self.assert_fallback_runs(self.run_pr("run", "echo", "--", "0", isolated=True))

    def test_conflict_markers_in_a_linked_worktree_hook_environment(self):
        self.commit_pins()
        wt = self.consumer.parent / "wt"
        git(self.consumer, "worktree", "add", "-q", "--detach", str(wt))
        wpins = wt / "factory-pins" / "factory-pins.json"
        wpins.write_bytes(b"<<<<<<< HEAD\n" + wpins.read_bytes() + b"\n=======\n{}\n>>>>>>> side\n")
        env = {**os.environ, "FACTORY_PINS_CACHE": str(self.cache),
               "GIT_DIR": git(wt, "rev-parse", "--absolute-git-dir")}
        env.pop("FACTORY_BUS_CLONE", None)
        # the main checkout's pins must not be what saves it: empty them so only wt's HEAD can name echo
        self.pins.write_text(json.dumps({"schema": "factory-pins.v1", "tools": {}}), encoding="utf-8")
        for iso in ([], ["-I"]):
            p = subprocess.run([sys.executable, *iso, str(wt / "factory-pins" / "pin-runner.py"), "run", "echo", "--", "0"],
                               capture_output=True, text=True, cwd=str(wt), env=env)
            self.assert_fallback_runs(p)

    def test_unusable_head_keeps_refusing(self):
        marked = b"<<<<<<< HEAD\n{}\n=======\n{}\n>>>>>>> side\n"
        self.pin_echo()
        self.pins.write_bytes(marked)  # no commit at all: nothing reviewed to fall back to
        p = self.run_pr("run", "echo", "--", "0")
        self.assertEqual((p.returncode, "v1" in p.stdout), (2, False))
        self.assertIn("no committed pins at HEAD", p.stderr)
        git(self.consumer, "add", "factory-pins")
        git(self.consumer, "commit", "-qm", "markers committed")  # HEAD itself carries the markers
        for iso in (False, True):
            p = self.run_pr("run", "echo", "--", "0", isolated=iso)
            self.assertEqual((p.returncode, "v1" in p.stdout), (2, False), p.stderr)
            self.assertIn("unusable too", p.stderr)
        self.pins.write_text('{"schema": "factory-pins.v1", "tools": {"echo": {"path": "../x"}}}', encoding="utf-8")
        git(self.consumer, "commit", "-qam", "schema-invalid at HEAD")
        self.pins.write_bytes(marked)
        self.assertEqual(self.run_pr("run", "echo", "--", "0").returncode, 2)

    def test_parseable_but_invalid_pins_never_fall_back(self):
        self.commit_pins()
        self.pins.write_text('{"schema": "factory-pins.v1", "tools": {}}', encoding="utf-8")  # a pin decision, not a torn file
        p = self.run_pr("run", "echo", "--", "0")
        self.assertEqual((p.returncode, "FALLBACK" in p.stderr), (2, False))
        self.pins.write_text('{"schema": "factory-pins.v1", "tools": {"echo": {"path": "../x"}}}', encoding="utf-8")
        self.assertEqual(self.run_pr("run", "echo").returncode, 2)

    def test_pins_ref_never_falls_back(self):
        self.commit_pins()
        self.pins.write_bytes(b"<<<<<<< HEAD\n{}\n=======\n{}\n>>>>>>> side\n")
        git(self.consumer, "commit", "-qam", "markers at HEAD")
        p = self.run_pr("--pins-ref", "HEAD", "run", "echo", "--", "0")
        self.assertEqual((p.returncode, "v1" in p.stdout), (2, False))


MAIN_G = (b"import importlib.util, sys\nfrom pathlib import Path\n"
          b"s = importlib.util.spec_from_file_location('sib', Path(__file__).with_name('sib.py'))\n"
          b"m = importlib.util.module_from_spec(s); s.loader.exec_module(m)\n"
          b"print('main+' + m.WHO, sys.argv[1:])\nsys.exit(int(sys.argv[1]) if sys.argv[1:] else 0)\n")
SIB_G = b"WHO = 'reviewed-sib'\n"


class PinnedGroup(_Fixture):
    """Bus K154: a tool that loads siblings by file name (tools/factory/kernel-receipt.py) runs as a pinned group."""

    def setUp(self):
        super().setUp()
        (self.bus / "tools" / "factory" / "main.py").write_bytes(MAIN_G)
        (self.bus / "tools" / "factory" / "sib.py").write_bytes(SIB_G)
        (self.bus / "tools" / "factory" / "sib2.py").write_bytes(SIB_G)
        git(self.bus, "add", "-A")
        git(self.bus, "commit", "-qm", "group")
        self.c2 = git(self.bus, "rev-parse", "HEAD")

    def pin(self, tool: str, path: str, *extra: str) -> subprocess.CompletedProcess:
        return self.run_pr("pin", tool, "--commit", self.c2, "--path", path, "--reviewer", "t", "--reason", "r", *extra)

    def pin_group(self):
        self.pin_echo()
        self.assertEqual(self.pin("sib", "tools/factory/sib.py").returncode, 0)
        p = self.pin("main", "tools/factory/main.py", "--with", "sib")
        self.assertEqual(p.returncode, 0, p.stderr)

    def test_group_runs_with_its_verified_member_beside_it(self):
        self.pin_group()
        self.assertEqual(json.loads(self.pins.read_text(encoding="utf-8"))["tools"]["main"]["with"], ["sib"])
        for iso in (False, True):
            p = self.run_pr("run", "main", "--", "4", isolated=iso)
            self.assertEqual((p.returncode, "main+reviewed-sib ['4']" in p.stdout), (4, True), p.stderr)
        self.assertEqual(self.run_pr("verify").returncode, 0)

    def test_isolated_group_never_reads_a_sibling_from_the_callers_tree(self):
        # In-process, __file__ is the bus path: a sibling load would read <cwd>/tools/factory/sib.py.
        self.pin_group()
        decoy = self.consumer / "tools" / "factory"
        decoy.mkdir(parents=True)
        (decoy / "sib.py").write_bytes(b"WHO = 'DECOY'\n")
        p = self.run_pr("run", "main", "--", "0", isolated=True)
        self.assertEqual((p.returncode, "reviewed-sib" in p.stdout, "DECOY" in p.stdout), (0, True, False), p.stderr)

    def test_repin_keeps_the_group(self):
        self.pin_group()
        self.assertEqual(self.pin("main", "tools/factory/main.py").returncode, 0)
        self.assertEqual(json.loads(self.pins.read_text(encoding="utf-8"))["tools"]["main"]["with"], ["sib"])

    def test_a_tampered_member_refuses_and_runs_nothing(self):
        self.pin_group()
        pins = json.loads(self.pins.read_text(encoding="utf-8"))
        pins["tools"]["sib"]["sha256"] = "0" * 64
        self.pins.write_text(json.dumps(pins), encoding="utf-8")
        for iso in (False, True):
            p = self.run_pr("run", "main", "--", "0", isolated=iso)
            self.assertEqual((p.returncode, "main+" in p.stdout), (2, False))

    def test_malformed_groups_refuse(self):
        self.pin_group()
        good = json.loads(self.pins.read_text(encoding="utf-8"))
        self.assertEqual(self.pin("sib2", "tools/factory/sib2.py").returncode, 0)
        good = json.loads(self.pins.read_text(encoding="utf-8"))
        bad_with = ([], ["nope"], ["sib", "sib"], ["main"], "sib", [7])
        for w in bad_with:
            pins = json.loads(json.dumps(good))
            pins["tools"]["main"]["with"] = w
            self.pins.write_text(json.dumps(pins), encoding="utf-8")
            with self.subTest(with_=w):
                self.assertEqual(self.run_pr("run", "main", "--", "0").returncode, 2)
        pins = json.loads(json.dumps(good))
        pins["tools"]["sib"]["with"] = ["echo"]                       # a member with its own group
        self.pins.write_text(json.dumps(pins), encoding="utf-8")
        self.assertEqual(self.run_pr("run", "main", "--", "0").returncode, 2)
        pins = json.loads(json.dumps(good))
        pins["tools"]["sib2"]["path"] = "tools/factory/main.py"       # two files named main.py in one directory
        pins["tools"]["main"]["with"] = ["sib2"]
        self.pins.write_text(json.dumps(pins), encoding="utf-8")
        self.assertEqual(self.run_pr("run", "main", "--", "0").returncode, 2)
        p = self.pin("main", "tools/factory/main.py", "--with", "absent")
        self.assertEqual(p.returncode, 2)

    def test_a_group_member_missing_from_the_clone_is_unavailable(self):
        self.pin_group()
        pins = json.loads(self.pins.read_text(encoding="utf-8"))
        data = b"WHO = 'never committed'\n"
        import hashlib
        pins["tools"]["sib"].update(blob=hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest(),
                                    bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        self.pins.write_text(json.dumps(pins), encoding="utf-8")
        self.assertEqual(self.run_pr("run", "main", "--", "0").returncode, 3)

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

    def _substituting(self, mod, spec: str, payload: bytes):
        real = mod.git

        def fake(repo, *a, **kw):
            p = real(repo, *a, **kw)
            return subprocess.CompletedProcess(p.args, 0, payload, p.stderr) if a == ("cat-file", "blob", spec) else p
        mod.git = fake
        return real

    def test_substituted_tool_or_registry_bytes_are_never_recorded(self):
        # Round 2 BLOCKER: the tool blob (and the registry) were hashed into trusted pins without being compared with
        # the commit's tree entry, so substituted bytes became the pin. Every blob read is proven in-process now.
        import argparse
        evil = b"print('UNREVIEWED TOOL EXECUTED')\n"
        for spec, label in ((f"{self.c1}:tools/factory/echo.py", "tool"), (f"{self.c1}:tools/factory/registry.json", "registry")):
            mod = self._module()
            real = self._substituting(mod, spec, evil)
            with self.assertRaises(mod.Refused, msg=label) as cm:
                mod.cmd_install(self._args(mod), [])
            self.assertIn("not object", str(cm.exception), label)
            self.assertFalse((self.proj / "factory-pins").exists(), label)
            mod.git = real
        # `pin` goes through the same reader.
        mod = self._module()
        self._substituting(mod, f"{self.c1}:tools/factory/echo.py", evil)
        a = argparse.Namespace(tool="echo", path="tools/factory/echo.py", commit=self.c1, reviewer="t", reason="r", date=None,
                               interpreter=None, pins=str(self.pins), bus=str(self.bus))
        with self.assertRaises(mod.Refused):
            mod.cmd_pin(a, [])
        self.assertFalse(self.pins.exists())
        # adopt-runner as well (the vendored copy is the real one, the bus answer is substituted).
        self.runner.parent.mkdir()
        self.runner.write_bytes(git_blob(self.bus, self.c1, "tools/factory/pin-runner.py"))
        self.pins.write_text(json.dumps({"schema": "factory-pins.v1", "tools": {}}), encoding="utf-8")
        mod = self._module()
        self._substituting(mod, f"{self.c1}:tools/factory/pin-runner.py", evil)
        with self.assertRaises(mod.Refused):
            mod.cmd_adopt_runner(argparse.Namespace(commit=self.c1, pins=str(self.pins), bus=str(self.bus)), [])
        self.assertNotIn("runner", json.loads(self.pins.read_text(encoding="utf-8")))

    def test_run_and_verify_refuse_substituted_bytes_for_a_recorded_blob(self):
        import argparse
        self.assertEqual(self.install("echo").returncode, 0)
        blob = json.loads(self.pins.read_text(encoding="utf-8"))["tools"]["echo"]["blob"]
        evil = b"open('ran.marker', 'w').write('x')\nprint('UNREVIEWED TOOL EXECUTED')\n"
        old_cache = os.environ.get("FACTORY_PINS_CACHE")
        os.environ["FACTORY_PINS_CACHE"] = str(self.cache)
        try:
            mod = self._module()
            self._substituting(mod, blob, evil)
            ns = argparse.Namespace(pins=str(self.pins), pins_ref=None, bus=str(self.bus))
            cwd = os.getcwd()
            os.chdir(self.elsewhere)
            try:
                with self.assertRaises(mod.Refused):
                    mod.cmd_run(ns, ["echo"])
                import contextlib, io
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(mod.cmd_verify(ns, []), 2)
            finally:
                os.chdir(cwd)
        finally:
            if old_cache is None:
                os.environ.pop("FACTORY_PINS_CACHE", None)
            else:
                os.environ["FACTORY_PINS_CACHE"] = old_cache
        self.assertFalse((self.elsewhere / "ran.marker").exists())

    # --- bootstrap scripts: the reviewed blob is proven BEFORE any of its bytes run -------------------------------
    TAMPER = 'import pathlib; pathlib.Path("ran.marker").write_text("x")'

    def _bash(self):
        git_exe = shutil.which("git")
        cands = [Path(git_exe).resolve().parent.parent / "bin" / "bash.exe"] if git_exe else []
        cands += [Path(p) for p in (shutil.which("bash"), shutil.which("sh")) if p]
        return next((c for c in cands if c.is_file() and "system32" not in str(c).lower()), None)

    def _shim_env(self, kind: str) -> dict:
        shim = Path(self._tmp.name) / f"shim-{kind}"
        shim.mkdir()
        real = shutil.which("git")
        if kind == "sh":
            (shim / "git").write_bytes(('#!/bin/sh\ncase " $* " in *" show "*) "$REAL_GIT" "$@"; echo \'' + self.TAMPER + '\' ;;\n'
                                        '*) exec "$REAL_GIT" "$@" ;; esac\n').encode())
        else:
            (shim / "git.cmd").write_bytes(('@echo off\r\nif not "%~3"=="show" goto passthru\r\n"%REAL_GIT%" %*\r\n'
                                            'echo ' + self.TAMPER + '\r\nexit /b 0\r\n:passthru\r\n"%REAL_GIT%" %*\r\nexit /b %errorlevel%\r\n').encode())
        for f in shim.iterdir():
            f.chmod(0o755)  # POSIX skips a non-executable file on PATH: without this the shim is silently bypassed (CI 2026-10-16)
        env = {**os.environ, "REAL_GIT": real, "PATH": str(shim) + os.pathsep + os.environ["PATH"], "PYTHON": sys.executable}
        found = shutil.which("git", path=env["PATH"])  # the shim must really be what `git` resolves to, or the test proves nothing
        if os.name != "nt" or kind == "cmd":  # (python's which() cannot see an extension-less script on Windows; Git Bash can)
            self.assertTrue(found and Path(found).resolve().parent == shim.resolve(), f"the git shim is not first on PATH: {found}")
        return env

    def _check_bootstrap(self, argv: list, tamper_env: dict, clean_env: dict):
        script_args = [str(self.bus), self.c1, "echo", "tester", "fixture", str(self.proj)]
        p = subprocess.run(argv(script_args), capture_output=True, text=True, cwd=str(self.elsewhere), env=tamper_env)
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertIn("REFUSED", p.stderr)
        self.assertFalse((self.elsewhere / "ran.marker").exists() or (self.proj / "ran.marker").exists(), "the runner must never start")
        self.assertFalse(self.runner.exists() or (self.runner.parent / "pin-runner.py.tmp").exists(), "the tampered file is removed")
        self.assertFalse(self.pins.exists())
        p = subprocess.run(argv(script_args), capture_output=True, text=True, cwd=str(self.elsewhere), env=clean_env)  # control
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(self.sh(self.runner, "verify", cwd=self.proj).returncode, 0)

    def test_bootstrap_sh_refuses_a_tampered_blob_and_installs_a_clean_one(self):
        bash = self._bash()
        if bash is None:
            self.skipTest("no POSIX shell")
        script = (Path(__file__).resolve().parent / "bootstrap.sh").as_posix()
        clean = {**os.environ, "PYTHON": sys.executable}
        self._check_bootstrap(lambda a: [str(bash), script, *[x.replace("\\", "/") for x in a]], self._shim_env("sh"), clean)

    def test_bootstrap_ps1_refuses_a_tampered_blob_and_installs_a_clean_one(self):
        pwsh = shutil.which("pwsh") or shutil.which("powershell")
        if os.name != "nt" or pwsh is None:
            self.skipTest("PowerShell on Windows only (the script drives cmd for raw redirection)")
        script = str(Path(__file__).resolve().parent / "bootstrap.ps1")
        names = ["-Bus", "-Sha", "-Tool", "-Reviewer", "-Reason", "-Project"]
        self._check_bootstrap(lambda a: [pwsh, "-NoProfile", "-File", script, *[x for n, v in zip(names, a) for x in (n, v)]],
                              self._shim_env("cmd"), {**os.environ})

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


class InstallGroup(unittest.TestCase):
    """Bus K154: a registry entry with `with` installs as a pinned group once its members are installed.
    Reuses Install's fixture (not its tests)."""
    SIDE = Install.SIDE
    tearDown, write_registry, sh, install = Install.tearDown, Install.write_registry, Install.sh, Install.install

    def setUp(self):
        Install.setUp(self)
        f = self.bus / "tools" / "factory"
        (f / "main.py").write_bytes(MAIN_G)
        (f / "sib.py").write_bytes(SIB_G)
        self.write_group_registry({"with": ["sib"]})
        git(self.bus, "add", "-A")
        git(self.bus, "commit", "-qm", "group")
        self.c1 = git(self.bus, "rev-parse", "HEAD")

    def write_group_registry(self, main_extra: dict, sib_extra: dict | None = None):
        tools = {n: {"path": f"tools/factory/{n}.py", "interpreter": "python", "purpose": f"{n} fixture"}
                 for n in ("echo", "side", "sib", "main")}
        tools["main"].update(main_extra)
        tools["sib"].update(sib_extra or {})
        (self.bus / "tools" / "factory" / "registry.json").write_text(
            json.dumps({"schema": "factory-registry.v1", "tools": tools}), encoding="utf-8")

    def test_a_group_installs_after_its_members_and_runs(self):
        p = self.install("main")
        self.assertEqual(p.returncode, 2)
        self.assertIn("install sib first", p.stderr)
        self.assertEqual(self.install("sib").returncode, 0)
        p = self.install("main")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(self.pins.read_text(encoding="utf-8"))["tools"]["main"]["with"], ["sib"])
        self.assertIn("NO-OP", self.install("main").stdout)
        for iso in ([], ["-I"]):
            r = subprocess.run([sys.executable, *iso, str(self.runner), "run", "main", "--", "6"], capture_output=True,
                               text=True, cwd=str(self.proj), env={**os.environ, "FACTORY_PINS_CACHE": str(self.cache)})
            self.assertEqual((r.returncode, "main+reviewed-sib ['6']" in r.stdout), (6, True), r.stderr)

    def test_a_malformed_registry_group_refuses(self):
        for main_extra, sib_extra in (({"with": []}, None), ({"with": ["nope"]}, None), ({"with": ["main"]}, None),
                                      ({"with": ["sib", "sib"]}, None), ({"with": ["sib"]}, {"with": ["echo"]}),
                                      ({"with": ["sib"], "interpreter": "node"}, None)):
            self.write_group_registry(main_extra, sib_extra)
            git(self.bus, "commit", "-qam", "bad registry")
            with self.subTest(main=main_extra, sib=sib_extra):
                p = self.install("echo", git(self.bus, "rev-parse", "HEAD"))
                self.assertEqual(p.returncode, 2, p.stdout)
                self.assertIn("registry at", p.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=1)
