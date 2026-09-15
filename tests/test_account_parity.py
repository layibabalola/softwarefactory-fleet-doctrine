#!/usr/bin/env python3
"""Hermetic tests for tools/check-account-parity.py and tools/realign-cli.py.

    python -m unittest discover -s tests -p "test_account_parity.py" -v

R6 binds the *check-then-repair* order, not an implementation. These tests pin the
branch behaviour of the implementation the fleet actually ships, so a change to it is
a visible change rather than a silent one, and so R6.3 ("installed and has fired")
can be answered with evidence instead of belief.

WHAT IS AT STAKE IN THE SANDBOX. Both scripts read and WRITE credential-adjacent
files in the operator's home, and one of them can launch an interactive login. The
suite therefore runs each script as a CHILD PROCESS with HOME and APPDATA redirected
at a throwaway directory. Measured on Windows / CPython 3.14 before this file existed:

    HOME                 -> Path.home() UNCHANGED    <- the trap
    HOMEDRIVE + HOMEPATH -> Path.home() UNCHANGED
    USERPROFILE          -> Path.home() REDIRECTED   <- the only one that works

`Path.home()` is `os.path.expanduser("~")`, which consults USERPROFILE first on
Windows. A suite that exported only HOME -- the POSIX reflex -- would run all of this
against the operator's real ~/.claude and overwrite the live account-email-map.json
and the realign cooldown stamp. So: every variable is set, the redirection is PROVEN
by asking a child process before any test runs (setUpClass fails hard otherwise), and
the four real files are hashed before and after so a leak fails the suite loudly.

NO TEST MAY LAUNCH `claude auth`. The single path that could -- DRIFT under --repair
-- is neutralised by planting a FRESH cooldown stamp in the sandbox so realign-cli
takes its documented "not reopening" branch, and the test asserts that it did. PATH is
also pointed at a non-existent directory so a stray `claude` cannot resolve.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

TOOLS = pathlib.Path(__file__).resolve().parent.parent / "tools"
PARITY = TOOLS / "check-account-parity.py"
REALIGN = TOOLS / "realign-cli.py"

UUID_A = "11111111-1111-1111-1111-111111111111"
UUID_B = "22222222-2222-2222-2222-222222222222"
EMAIL_A = "a@example.invalid"
EMAIL_B = "b@example.invalid"

REAL_HOME = pathlib.Path(os.path.expanduser("~"))
TRIPWIRE = [
    REAL_HOME / ".claude" / "account-email-map.json",
    REAL_HOME / ".claude" / ".realign-last-attempt",
    REAL_HOME / ".claude.json",
    REAL_HOME / ".claude" / ".credentials.json",
]


def fp(v: str) -> str:
    return hashlib.sha256(v.encode()).hexdigest()[:12]


def digest(p: pathlib.Path) -> str:
    try:
        return hashlib.sha256(p.read_bytes()).hexdigest()
    except FileNotFoundError:
        return "<absent>"
    except OSError as exc:
        return f"<unreadable:{exc.__class__.__name__}>"


class ParityTestBase(unittest.TestCase):
    """Sandbox lifecycle, the safety proof, and the tripwire."""

    @classmethod
    def setUpClass(cls):
        if not PARITY.exists() or not REALIGN.exists():
            raise unittest.SkipTest(f"tools not found under {TOOLS}")
        cls._before = {p: digest(p) for p in TRIPWIRE}
        cls.root = pathlib.Path(tempfile.mkdtemp(prefix="parity_tests_"))
        cls.home = cls.root / "home"
        cls.appdata = cls.root / "appdata"
        (cls.home / ".claude").mkdir(parents=True, exist_ok=True)
        (cls.appdata / "Claude").mkdir(parents=True, exist_ok=True)

        # PROVE the redirection took, in a child, before running anything at all.
        probe = subprocess.run(
            [sys.executable, "-c",
             "import pathlib,os;print(pathlib.Path.home());print(os.environ.get('APPDATA'))"],
            capture_output=True, text=True, env=cls._env())
        lines = (probe.stdout or "").splitlines()
        norm = lambda p: os.path.normcase(os.path.normpath(str(p)))
        if len(lines) < 2 or norm(lines[0]) != norm(cls.home) or norm(lines[1]) != norm(cls.appdata):
            shutil.rmtree(cls.root, ignore_errors=True)
            raise RuntimeError(
                "sandbox NOT in effect; refusing to run. Running anyway would have "
                f"written to the real credential directory ({REAL_HOME}). "
                f"child reported: {lines!r}")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root, ignore_errors=True)
        touched = [str(p) for p in TRIPWIRE if cls._before[p] != digest(p)]
        if touched:
            raise AssertionError("TRIPWIRE: real credential files changed during the "
                                 "run: " + ", ".join(touched))

    @classmethod
    def _env(cls):
        e = dict(os.environ)
        e["USERPROFILE"] = str(cls.home)    # the only one that redirects Path.home() on Windows
        e["HOME"] = str(cls.home)           # inert on Windows, correct on POSIX
        e["HOMEDRIVE"] = str(cls.home)[:2]
        e["HOMEPATH"] = str(cls.home)[2:]
        e["APPDATA"] = str(cls.appdata)
        # desktop() falls back APPDATA -> XDG_CONFIG_HOME -> ~/.config, so the fallbacks
        # must be cleared too or a scenario could read a real location.
        for k in ("XDG_CONFIG_HOME", "CLAUDE_CONFIG_DIR", "HOMESHARE"):
            e.pop(k, None)
        e["PATH"] = str(cls.root / "no-such-bin")   # a stray `claude` must not resolve
        return e

    # -- sandbox files --------------------------------------------------------
    @property
    def desktop_cfg(self): return self.appdata / "Claude" / "config.json"
    @property
    def cli_cfg(self): return self.home / ".claude.json"
    @property
    def email_map(self): return self.home / ".claude" / "account-email-map.json"
    @property
    def stamp(self): return self.home / ".claude" / ".realign-last-attempt"

    def setUp(self):
        for p in (self.desktop_cfg, self.cli_cfg, self.email_map, self.stamp):
            p.unlink(missing_ok=True)

    def set_desktop(self, uuid=None, raw=None):
        if raw is not None:
            self.desktop_cfg.write_text(raw, encoding="utf-8")
        else:
            self.desktop_cfg.write_text(
                json.dumps({"lastKnownAccountUuid": uuid} if uuid else {}), encoding="utf-8")

    def set_cli(self, uuid=None, email=None, raw=None, signed_out=False):
        if raw is not None:
            self.cli_cfg.write_text(raw, encoding="utf-8"); return
        if signed_out:
            # The real shape of a signed-out CLI: the config survives with its usage
            # history, only the account record goes. Verified against a live
            # ~/.claude.json: 68 top-level keys beside oauthAccount, including
            # numStartups, firstStartTime, installMethod and a 151-entry projects map.
            self.cli_cfg.write_text(json.dumps(
                {"numStartups": 22, "firstStartTime": "2026-02-25T00:38:14.519Z",
                 "installMethod": "native", "hasCompletedOnboarding": True,
                 "projects": {"C:\\code\\x": {}}}), encoding="utf-8")
            return
        acc = {"accountUuid": uuid}
        if email:
            acc["emailAddress"] = email
        self.cli_cfg.write_text(json.dumps({"oauthAccount": acc}), encoding="utf-8")

    def set_email_map(self, mapping):
        self.email_map.write_text(json.dumps(mapping), encoding="utf-8")

    def set_stamp_fresh(self):
        self.stamp.write_text(str(time.time()), encoding="utf-8")

    def run_tool(self, script, *args, timeout=60):
        return subprocess.run([sys.executable, str(script), *args],
                              capture_output=True, text=True, timeout=timeout,
                              env=self._env(), encoding="utf-8", errors="replace")

    def out(self, r):
        return (r.stdout or "") + (r.stderr or "")

    def assertNoLaunch(self, r):
        text = self.out(r)
        self.assertNotIn("opening a login window", text,
                         "a test reached the real login-launch path")
        self.assertNotIn("Traceback", text, "tool crashed")


class TestCheckAccountParity(ParityTestBase):

    def test_aligned_reports_matched_and_repairs_nothing(self):
        self.set_desktop(UUID_A); self.set_cli(UUID_A, EMAIL_A)
        r = self.run_tool(PARITY, "--repair")
        self.assertIn(f"desktop fp={fp(UUID_A)}", self.out(r))
        self.assertIn(f"cli     fp={fp(UUID_A)}", self.out(r))
        self.assertIn("MATCHED", self.out(r))
        self.assertNotIn("DRIFT", self.out(r))
        self.assertNotIn("launching re-auth", self.out(r))
        self.assertEqual(0, r.returncode)
        self.assertNoLaunch(r)

    def test_drift_without_repair_flag_is_advisory_only(self):
        self.set_desktop(UUID_A); self.set_cli(UUID_B, EMAIL_B)
        r = self.run_tool(PARITY)
        self.assertIn("*** DRIFT ***", self.out(r))
        self.assertIn("realign-cli.py --auto", self.out(r))
        self.assertNotIn("launching re-auth", self.out(r))
        self.assertNoLaunch(r)

    def test_drift_with_repair_flag_invokes_the_wizard(self):
        """R6's check-then-repair order. The cooldown is planted fresh so the wizard
        provably stops short of launching; that it got far enough to consult the
        cooldown is what proves the repair path was entered."""
        self.set_desktop(UUID_A); self.set_cli(UUID_B, EMAIL_B)
        self.set_stamp_fresh()
        before = self.stamp.read_text()
        r = self.run_tool(PARITY, "--repair")
        self.assertIn("*** DRIFT ***", self.out(r))
        self.assertIn("launching re-auth", self.out(r))
        self.assertIn("not reopening", self.out(r))
        self.assertEqual(before, self.stamp.read_text(), "cooldown stamp was rewritten")
        self.assertNoLaunch(r)

    def test_parity_verdict_precedes_wizard_output(self):
        """The banner must read in causal order: the DRIFT diagnosis, then the repair
        it triggered. stdout is block-buffered when a hook captures it, so without an
        explicit flush the child's writes overtake the parent's and the operator sees
        the remedy before the reason for it."""
        self.set_desktop(UUID_A); self.set_cli(UUID_B, EMAIL_B)
        self.set_stamp_fresh()
        r = self.run_tool(PARITY, "--repair")
        text = self.out(r)
        self.assertLess(text.index("*** DRIFT ***"), text.index("[realign]"),
                        "wizard output appeared before the parity verdict that caused it")

    # -- the states where no repair happens today ----------------------------

    def test_cli_signed_out_is_named_not_merely_unknown(self):
        """THE HAZARD: a signed-out CLI leaves scheduled floors dark while the desktop
        app looks healthy. It gets its own verdict so a consumer can gate on it, and it
        must never read as agreement."""
        self.set_desktop(UUID_A); self.set_cli(signed_out=True)
        r = self.run_tool(PARITY, "--repair")
        self.assertIn("cli     fp=-", self.out(r))
        self.assertIn("signed out?", self.out(r))
        self.assertIn("*** CLI-SIGNED-OUT ***", self.out(r))
        self.assertIn("DARK", self.out(r))
        self.assertNotIn("MATCHED", self.out(r))
        self.assertNoLaunch(r)

    def test_cli_signed_out_is_detected_but_never_repaired(self):
        """Rejected by design: `~/.claude.json` is a profile cache, not the credential
        store, so 'no accountUuid' has benign causes; and an unattended floor wake is a
        SessionStart, which must not open a focus-stealing login window."""
        self.set_desktop(UUID_A); self.set_cli(signed_out=True)
        r = self.run_tool(PARITY, "--repair")
        self.assertIn("NOT repaired automatically", self.out(r))
        self.assertNotIn("launching re-auth", self.out(r))
        self.assertFalse(self.stamp.exists(), "a repair was attempted")
        self.assertNoLaunch(r)

    def test_unreadable_surfaces_stay_unknown_and_are_not_signed_out(self):
        """A missing or corrupt config says nothing about being signed out. Collapsing
        the two would make the signed-out verdict unactionable."""
        for name, setup in [
            ("cli missing", lambda: self.set_desktop(UUID_A)),
            ("cli corrupt", lambda: (self.set_desktop(UUID_A), self.set_cli(raw="}{"))),
            ("desktop missing", lambda: self.set_cli(UUID_A, EMAIL_A)),
        ]:
            with self.subTest(state=name):
                self.setUp(); setup()
                out = self.out(self.run_tool(PARITY, "--repair"))
                self.assertIn("UNKNOWN", out)
                self.assertNotIn("CLI-SIGNED-OUT", out)

    def test_matched_learns_the_healthy_account(self):
        """The regression this guards against: no AUTOMATIC path primed the map with a
        healthy account. learn() is unconditional inside realign-cli.py, so running that
        script by hand primes it -- but the hook invoked the wizard only on DRIFT, i.e.
        only while the CLI still held the account being LEFT. Unattended, the map could
        accumulate only departed accounts, and the later lookup of the account being moved
        TO missed. Observed on a live host: MATCHED all day on one fingerprint, map holding
        only the account it had rotated away from two days earlier. Worst on a fresh
        machine, where the map is empty at the first event."""
        self.set_desktop(UUID_A); self.set_cli(UUID_A, EMAIL_A)
        r = self.run_tool(PARITY)
        self.assertIn("MATCHED", self.out(r))
        self.assertTrue(self.email_map.exists(), "MATCHED learned nothing")
        self.assertEqual(EMAIL_A, json.loads(self.email_map.read_text()).get(fp(UUID_A)))

    def test_drift_does_not_learn_the_departed_account(self):
        """R6.4.2: an identity cache learns from the HEALTHY state. An earlier revision
        called learn() ahead of the branch, so the drift path also recorded the departed
        fingerprint -- the behaviour this change exists to stop. Raised in fleet review of
        _bus #69; pinned here so the nesting cannot quietly regress."""
        self.set_desktop(UUID_A); self.set_cli(UUID_B, EMAIL_B)
        r = self.run_tool(PARITY)               # no --repair: the wizard must not run either
        self.assertIn("*** DRIFT ***", self.out(r))
        learned = json.loads(self.email_map.read_text()) if self.email_map.exists() else {}
        self.assertNotIn(fp(UUID_B), learned,
                         "drift recorded the departed account in the prefill map")
        self.assertEqual({}, learned, f"drift learned something: {learned}")

    def test_learned_healthy_account_prefills_a_later_repair(self):
        """The point of learning on MATCHED: when drift does happen, the wizard can offer
        the right address instead of an empty login the operator may complete on the
        wrong account."""
        self.set_desktop(UUID_A); self.set_cli(UUID_A, EMAIL_A)
        self.run_tool(PARITY)                        # healthy day: learn UUID_A -> EMAIL_A
        self.set_cli(UUID_B, EMAIL_B)                # later: CLI drifts to another account
        out = self.out(self.run_tool(REALIGN, "--dry-run"))
        self.assertIn("DRIFT", out)
        self.assertIn(f"--email {EMAIL_A}", out)

    def test_learn_survives_an_unwritable_home(self):
        """A parity check must not become an error because the map could not be written."""
        self.set_desktop(UUID_A); self.set_cli(UUID_A, EMAIL_A)
        self.email_map.parent.mkdir(parents=True, exist_ok=True)
        self.email_map.mkdir(exist_ok=True)          # a directory where a file must go
        try:
            r = self.run_tool(PARITY)
            self.assertIn("MATCHED", self.out(r))
            self.assertEqual(0, r.returncode)
            self.assertNotIn("Traceback", self.out(r))
        finally:
            self.email_map.rmdir()

    def test_cli_config_missing_is_unknown(self):
        self.set_desktop(UUID_A)
        r = self.run_tool(PARITY, "--repair")
        self.assertIn("CLI config not found", self.out(r))
        self.assertIn("UNKNOWN", self.out(r))
        self.assertNoLaunch(r)

    def test_desktop_config_missing_is_unknown(self):
        self.set_cli(UUID_A, EMAIL_A)
        r = self.run_tool(PARITY, "--repair")
        self.assertIn("desktop config not found", self.out(r))
        self.assertIn("UNKNOWN", self.out(r))
        self.assertNoLaunch(r)

    def test_corrupt_desktop_config_does_not_crash(self):
        self.set_desktop(raw="{not json at all"); self.set_cli(UUID_A, EMAIL_A)
        r = self.run_tool(PARITY, "--repair")
        self.assertIn("unreadable", self.out(r))
        self.assertIn("UNKNOWN", self.out(r))
        self.assertEqual(0, r.returncode)
        self.assertNoLaunch(r)

    def test_corrupt_cli_config_does_not_crash(self):
        self.set_desktop(UUID_A); self.set_cli(raw="}{")
        r = self.run_tool(PARITY, "--repair")
        self.assertIn("unreadable", self.out(r))
        self.assertIn("UNKNOWN", self.out(r))
        self.assertEqual(0, r.returncode)
        self.assertNoLaunch(r)

    def test_hook_never_exits_nonzero(self):
        """Deliberate: a parity checker that can block a session is worse than the
        drift it detects. Pinned so the always-0 contract cannot regress by accident."""
        for name, setup in [
            ("aligned", lambda: (self.set_desktop(UUID_A), self.set_cli(UUID_A, EMAIL_A))),
            ("drift", lambda: (self.set_desktop(UUID_A), self.set_cli(UUID_B, EMAIL_B))),
            ("signed-out", lambda: (self.set_desktop(UUID_A), self.set_cli(signed_out=True))),
            ("both-absent", lambda: None),
        ]:
            with self.subTest(state=name):
                self.setUp(); setup()
                if name == "drift":
                    self.set_stamp_fresh()
                self.assertEqual(0, self.run_tool(PARITY, "--repair").returncode)


class TestRealignCli(ParityTestBase):

    def test_verify_reports_drift_without_launching(self):
        self.set_desktop(UUID_A); self.set_cli(UUID_B, EMAIL_B)
        r = self.run_tool(REALIGN, "--verify")
        self.assertIn("DRIFT", self.out(r))
        self.assertFalse(self.stamp.exists(), "--verify wrote the cooldown stamp")
        self.assertNoLaunch(r)

    def test_dry_run_shows_the_command_and_launches_nothing(self):
        self.set_desktop(UUID_A); self.set_cli(UUID_B, EMAIL_B)
        r = self.run_tool(REALIGN, "--dry-run")
        self.assertIn("Would launch", self.out(r))
        self.assertIn("claude auth login", self.out(r))
        self.assertIn("no logout first", self.out(r))
        self.assertFalse(self.stamp.exists(), "--dry-run wrote the cooldown stamp")
        self.assertNoLaunch(r)

    def test_never_logs_out_first(self):
        """The invariant the wizard exists to hold: a logout followed by an abandoned
        login leaves the operator with no credential at all."""
        self.set_desktop(UUID_A); self.set_cli(UUID_B, EMAIL_B)
        r = self.run_tool(REALIGN, "--dry-run")
        self.assertNotIn("auth logout", self.out(r))

    def test_learn_records_fingerprint_to_email_while_signed_in(self):
        """The only moment the mapping can be captured: the desktop config publishes a
        uuid and no address, so the address has to be learned from the CLI while it
        happens to be on that account."""
        self.set_desktop(UUID_A); self.set_cli(UUID_B, EMAIL_B)
        self.run_tool(REALIGN, "--verify")
        self.assertTrue(self.email_map.exists(), "learn() wrote nothing")
        self.assertEqual(EMAIL_B, json.loads(self.email_map.read_text()).get(fp(UUID_B)))

    def test_aligned_is_a_no_op(self):
        self.set_desktop(UUID_A); self.set_cli(UUID_A, EMAIL_A)
        r = self.run_tool(REALIGN, "--auto")
        self.assertIn("nothing to do", self.out(r))
        self.assertNoLaunch(r)

    def test_signed_out_cli_is_not_repaired(self):
        """Pins the known gap so a change to it is deliberate and visible: the wizard
        refuses the one state the hazard is actually about."""
        self.set_desktop(UUID_A); self.set_cli(signed_out=True)
        r = self.run_tool(REALIGN, "--auto")
        self.assertIn("cannot compare", self.out(r))
        self.assertIn("doing nothing", self.out(r))
        self.assertNoLaunch(r)

    def test_drift_without_learned_email_carries_no_prefill(self):
        """A login launched with no --email lets the operator re-authenticate onto the
        wrong account -- the very failure the tool exists to prevent."""
        self.set_desktop(UUID_A); self.set_cli(UUID_B, EMAIL_B)
        self.set_email_map({"zzzzzzzzzzzz": "someone-else@example.invalid"})
        r = self.run_tool(REALIGN, "--dry-run")
        self.assertIn("email not yet learned", self.out(r))
        self.assertNotIn("--email", self.out(r).split("Would launch")[-1])
        self.assertNoLaunch(r)

    def test_cooldown_blocks_a_repeat_launch(self):
        """A SessionStart hook fires on every session; without this, a dismissed
        browser window reopens forever."""
        self.set_desktop(UUID_A); self.set_cli(UUID_B, EMAIL_B)
        self.set_stamp_fresh()
        before = self.stamp.read_text()
        r = self.run_tool(REALIGN, "--auto")
        self.assertIn("not reopening", self.out(r))
        self.assertEqual(before, self.stamp.read_text())
        self.assertNoLaunch(r)


if __name__ == "__main__":
    unittest.main(verbosity=2)
