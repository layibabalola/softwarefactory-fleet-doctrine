#!/usr/bin/env python3
"""Tests for machine_load.py. Stdlib only, no network, no elevation; builds throwaway git repos in a temp dir
with every GIT_* selector stripped from the environment (an inherited GIT_DIR once turned a shared repo bare).

Run: python tools/machine/machine-load/machine_load.tests.py
"""
import datetime as dt
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("machine_load", HERE / "machine_load.py")
ml = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ml)

CLEAN_ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def run(*args, cwd):
    subprocess.run(args, cwd=cwd, env=CLEAN_ENV, check=True, capture_output=True)


def minute(ts, busy=4.0, util=None, quiet=False, proj=None, machine="PC-TEST", code="abc", avail=60.0, free=1500.0, up=1):
    t = busy / 32 * 100
    return {"schema": ml.MINUTE_SCHEMA, "machine": machine, "ts": ts, "code": code, "lp": 32, "n": 6, "secs": 60,
            "cpu": {"time_pct_mean": t, "busy_threads": busy, "util_pct_mean": util if util is not None else t * 1.8},
            "mem": {"avail_gb_min": avail, "commit_pct_max": 30, "hard_faults_mean": 1},
            "disk": {"busy_pct_mean": 1, "lat_ms_max": 1, "c_free_gb": free},
            "net_mbps": 1, "thermal": {"n": 30, "pkg_w_mean": 30, "pkg_w_max": 40, "core_c_max": 70},
            "quiet": quiet, "cpu_s": {"machine": busy * 60, "attributed": busy * 50, "residual": busy * 10},
            "proj": proj if proj is not None else {"airmypc": busy * 40, "~dotnet": busy * 10},
            "top": [["SecretProcessName", 1.0]], "sampler": {"cpu_s": 0.5, "ws_mb": 200, "up_min": up}}


def write_day(d: Path, day: dt.date, rows):
    d.mkdir(parents=True, exist_ok=True)
    with (d / f"minute-{day.isoformat()}.jsonl").open("a", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")


def full_day(day, busy_fn=lambda i: 4.0, **kw):
    return [minute(f"{day.isoformat()}T{i // 60:02d}:{i % 60:02d}:00Z", busy=busy_fn(i), up=i, **kw) for i in range(1440)]


class Rollup(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.day = dt.date(2026, 11, 10)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_dedupes_and_ignores_other_days(self):
        rows = full_day(self.day)
        rows += rows[:5]                                     # a second sampler wrote five minutes again
        rows.append(minute("2026-11-11T00:00:00Z"))          # a row stamped for the next UTC day
        write_day(self.tmp, self.day, rows)
        row = ml.rollup(self.tmp, self.day, allow={"airmypc"})
        self.assertEqual(row["coverage_min"], 1440)
        self.assertEqual(row["duplicate_min"], 5)
        self.assertEqual(row["unparseable_rows"], 1)

    def test_restart_fragments_merge(self):
        a = minute("2026-11-10T00:05:00Z", busy=4.0, code="old"); a["n"] = 2; a["secs"] = 20
        b = minute("2026-11-10T00:05:00Z", busy=10.0, code="new"); b["n"] = 4; b["secs"] = 40
        write_day(self.tmp, self.day, [a, b])
        row = ml.rollup(self.tmp, self.day, allow=set())
        self.assertEqual((row["coverage_min"], row["duplicate_min"]), (1, 0))
        self.assertAlmostEqual(row["cpu"]["busy_threads_max"], 8.0, delta=0.05)   # duration-weighted
        self.assertAlmostEqual(row["cpu_core_h"]["machine"] * 3600, 4.0 * 60 + 10.0 * 60, delta=20)  # CPU adds (core-hours carry 2 decimals)
        self.assertEqual(row["code"], ["new"])

    def test_replay_of_one_session_is_a_duplicate(self):
        a = minute("2026-11-10T00:05:00Z"); a["n"] = 2; a["secs"] = 20; a["sid"] = "s1"
        b = dict(a)                                            # the same fragment written twice
        write_day(self.tmp, self.day, [a, b])
        rows, dups, bad = ml.read_minutes(self.tmp, self.day)    # 20 + 20 s would pass as a restart split by time alone
        self.assertEqual((len(rows), dups, rows[0]["secs"]), (1, 1, 20))

    def test_overlap_at_a_slow_interval_is_a_duplicate(self):
        # -IntervalSec 20: two samplers each write n=3 over a full minute; counts look like a restart split
        a = minute("2026-11-10T00:05:00Z"); a["n"] = 3; a["sid"] = "s1"
        b = minute("2026-11-10T00:05:00Z"); b["n"] = 3; b["sid"] = "s2"
        write_day(self.tmp, self.day, [a, b])
        self.assertEqual(ml.rollup(self.tmp, self.day, allow=set())["duplicate_min"], 1)

    def test_merge_keeps_the_worse_memory_and_disk(self):
        a = minute("2026-11-10T00:05:00Z", avail=1.0, free=20.0); a["n"] = 1; a["secs"] = 10; a["sid"] = "old"
        a["mem"]["commit_pct_max"] = 95; a["thermal"]["pkg_w_max"] = 74
        b = minute("2026-11-10T00:05:00Z", avail=60.0, free=1500.0); b["n"] = 5; b["secs"] = 50; b["sid"] = "new"
        m = ml.merge_fragments(a, b)
        self.assertEqual((m["mem"]["avail_gb_min"], m["disk"]["c_free_gb"]), (1.0, 20.0))
        self.assertEqual((m["mem"]["commit_pct_max"], m["thermal"]["pkg_w_max"], m["thermal"]["n"]), (95, 74, 60))
        self.assertEqual(m["secs"], 60)

    def test_concurrent_samplers_counted(self):
        a = minute("2026-11-10T00:05:00Z"); b = minute("2026-11-10T00:05:00Z")
        write_day(self.tmp, self.day, [a, b])
        self.assertEqual(ml.rollup(self.tmp, self.day, allow=set())["duplicate_min"], 1)

    def test_minutes_without_cpu_are_not_coverage(self):
        rows = full_day(self.day)
        for x in rows[:600]:
            x["cpu"]["busy_threads"] = None
        for x in rows[600:900]:
            x["secs"] = 10
        write_day(self.tmp, self.day, rows)
        self.assertEqual(ml.rollup(self.tmp, self.day, allow=set())["coverage_min"], 540)

    def test_missing_day_is_none_not_a_crash(self):
        self.assertIsNone(ml.rollup(self.tmp, self.day, allow=set()))
        self.assertEqual(ml.read_minutes(self.tmp, self.day), ([], 0, 0))

    def test_tilde_labels_and_heavy_kinds_are_allowlisted(self):
        allow = ml.load_projects()
        self.assertEqual(ml.public_label("~dotnet", allow), "~dotnet")
        self.assertEqual(ml.public_label("~secret-client", allow), "~other-project")
        self.assertEqual(ml.public_label("airmypc", allow), "airmypc")
        self.assertEqual(ml.public_kind("gate", allow), "gate")
        self.assertEqual(ml.public_kind("secret-client", allow), "?")   # tidy syntax is not membership
        self.assertEqual(ml.public_kind("fix-acme-bug-branch-long", allow), "?")
        self.assertEqual(ml.public_kind("/Users/layib/secret", allow), "?")

    def test_heavy_ledger_bad_lines_and_privacy(self):
        led = self.tmp / "ledger.jsonl"
        led.write_text("\n".join([
            "{not json", json.dumps({"event": "exit", "ticket": "zz"}), json.dumps({"event": "admit", "ticket": "t0"}),
            json.dumps({"event": "exit", "ticket": "t0"}),
            json.dumps({"at": "2026-11-10T01:00:00.1234567Z", "event": "admit", "ticket": "t1", "label": "airmypc:gate:wi/secret-branch"}),
            json.dumps({"at": "2026-11-10T01:06:00Z", "event": "exit", "ticket": "t1"}),
            json.dumps({"at": "2026-11-10T02:00:00Z", "event": "admit", "ticket": "t2", "label": "clientx:C:/Users/layib/x"}),
            json.dumps({"at": "2026-11-10T02:01:00Z", "event": "exit", "ticket": "t2"}),
            json.dumps({"at": "2026-11-10T03:00:00Z", "event": "admit", "ticket": "t3", "label": "airmypc:acmecorp"}),
            json.dumps({"at": "2026-11-10T03:01:00Z", "event": "exit", "ticket": "t3"})]) + "\n")
        old = ml.HEAVYSLOT_LEDGER
        ml.HEAVYSLOT_LEDGER = led
        try:
            jobs = ml.heavy_jobs(self.day, {}, ml.load_projects())
        finally:
            ml.HEAVYSLOT_LEDGER = old
        self.assertEqual(set(jobs), {"airmypc:gate", "~other-project:?", "airmypc:?"})
        self.assertEqual(jobs["airmypc:gate"]["dur_s_p50"], 360)
        self.assertNotIn("secret", json.dumps(jobs))
        self.assertNotIn("acmecorp", json.dumps(jobs))

    def test_nothing_private_travels(self):
        rows = full_day(self.day, proj={"secret-client-repo": 100, "airmypc": 50, "~claude": 10})
        write_day(self.tmp, self.day, rows)
        row = ml.rollup(self.tmp, self.day, allow={"airmypc"})
        text = json.dumps(row)
        self.assertNotIn("SecretProcessName", text)
        self.assertNotIn("secret-client-repo", text)
        self.assertIn("other-project", row["cpu_core_h"]["buckets"])
        self.assertIn("airmypc", row["cpu_core_h"]["projects"])

    def test_quiet_minutes_excluded_from_load_stats(self):
        rows = [minute(f"2026-11-10T00:{i:02d}:00Z", busy=30.0, quiet=True) for i in range(30)]
        rows += [minute(f"2026-11-10T01:{i:02d}:00Z", busy=2.0) for i in range(30)]
        write_day(self.tmp, self.day, rows)
        row = ml.rollup(self.tmp, self.day, allow=set())
        self.assertEqual(row["quiet_min"], 30)
        self.assertEqual(row["cpu"]["busy_threads_max"], 2.0)

    def test_clock_bands_use_utility_over_time(self):
        rows = [minute(f"2026-11-10T00:{i:02d}:00Z", busy=2.0, util=2 / 32 * 100 * 1.8) for i in range(20)]
        write_day(self.tmp, self.day, rows)
        row = ml.rollup(self.tmp, self.day, allow=set())
        self.assertAlmostEqual(row["cpu"]["clock_by_load"]["0-4"]["perf_p50"], 180.0, delta=0.2)

    def test_sampler_restart_counted(self):
        rows = [minute(f"2026-11-10T00:{i:02d}:00Z", up=i) for i in range(10)]
        rows += [minute(f"2026-11-10T00:{i:02d}:00Z", up=i - 10) for i in range(10, 20)]
        write_day(self.tmp, self.day, rows)
        self.assertEqual(ml.rollup(self.tmp, self.day, allow=set())["sampler"]["restarts"], 1)


class Helpers(unittest.TestCase):
    def test_full_day_excludes_quiet_minutes(self):
        self.assertFalse(ml.full_day({"coverage_min": 1440, "quiet_min": 1300}))   # 140 active minutes
        self.assertTrue(ml.full_day({"coverage_min": 1440, "quiet_min": 300}))
        self.assertTrue(ml.full_day({"coverage_min": 1200, "quiet_min": 0}))
        self.assertFalse(ml.full_day({"coverage_min": 1199, "quiet_min": 0}))

    def test_parse_iso_seven_digits(self):
        t = ml.parse_iso("2026-11-17T00:04:18.3742500Z")
        self.assertEqual((t.hour, t.minute, t.second, t.tzinfo), (0, 4, 18, dt.timezone.utc))

    def test_percentile(self):
        self.assertEqual(ml.pct(list(range(1, 101)), 95), 95)
        self.assertIsNone(ml.pct([None, None], 50))

    def test_clock_onset_measured_and_assumed(self):
        def row(bands):
            return {"cpu": {"clock_by_load": {k: {"n": 100, "perf_p50": v} for k, v in bands.items()}}}
        light, onset, _, _ = ml.clock_onset([row({"0-4": 180, "4-8": 178, "8-12": 170, "12-16": 150})])
        self.assertEqual(onset, 12)
        light, onset, seen, _ = ml.clock_onset([row({"0-4": 180, "4-8": 178})])
        self.assertIsNone(onset)
        self.assertEqual(seen, 8)
        light, onset, _, _ = ml.clock_onset([row({"16-20": 140, "28-32": 120})])   # no light-load baseline
        self.assertIsNone(onset)


class Headroom(unittest.TestCase):
    """A fake bus: a bare origin and a clone, rows committed to origin/master."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.origin = self.tmp / "origin.git"
        self.bus = self.tmp / "bus"
        run("git", "init", "-q", "--bare", "-b", "master", str(self.origin), cwd=self.tmp)
        run("git", "clone", "-q", str(self.origin), str(self.bus), cwd=self.tmp)
        run("git", "config", "user.email", "t@t", cwd=self.bus)
        run("git", "config", "user.name", "t", cwd=self.bus)
        (self.bus / "README.md").write_text("x")
        run("git", "add", ".", cwd=self.bus)
        run("git", "commit", "-qm", "init", cwd=self.bus)
        run("git", "push", "-q", "origin", "HEAD:master", cwd=self.bus)
        self.today = ml.utc_now().date()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def add_days(self, machine, days, coverage=1440, busy_fn=lambda i: 4.0, code="abc"):
        data = self.tmp / f"data-{machine}-{coverage}"
        lines = []
        for day in days:
            rows = full_day(day, busy_fn=busy_fn, machine=machine, code=code)[:coverage]
            write_day(data, day, rows)
            row = ml.rollup(data, day, allow={"airmypc"})
            lines.append(json.dumps(row))
        p = self.bus / ml.BUS_DIR / machine / "days-x.jsonl"
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a") as fh:
            fh.write("\n".join(lines) + "\n")
        run("git", "add", ".", cwd=self.bus)
        run("git", "commit", "-qm", machine, cwd=self.bus)
        run("git", "push", "-q", "origin", "HEAD:master", cwd=self.bus)

    def recs(self, expect=()):
        old = os.environ.copy()
        os.environ.clear(); os.environ.update(CLEAN_ENV)
        try:
            return {r["machine"]: r for r in ml.headroom(self.bus, 7, list(expect), live=False)}
        finally:
            os.environ.clear(); os.environ.update(old)

    def test_states_never_read_as_room(self):
        recent = [self.today - dt.timedelta(days=i) for i in (1, 2)]
        self.add_days("GOOD", recent)
        self.add_days("STALEBOX", [self.today - dt.timedelta(days=5)])
        self.add_days("PARTIAL", recent, coverage=600)
        recs = self.recs(expect=["GOOD", "STALEBOX", "PARTIAL", "ABSENTBOX"])
        self.assertEqual(recs["GOOD"]["states"], [])
        self.assertEqual(recs["GOOD"]["verdict"], "ROOM")
        self.assertIn("ABSENT", recs["ABSENTBOX"]["states"])
        self.assertNotIn("verdict", recs["ABSENTBOX"])
        self.assertIn("STALE", recs["STALEBOX"]["states"])
        self.assertEqual(recs["STALEBOX"]["verdict"], "UNKNOWN")          # stale data never reads as capacity
        self.assertEqual(recs["STALEBOX"]["verdict_untrusted"], "ROOM")
        self.assertIn("LOW-COVERAGE", recs["PARTIAL"]["states"])
        self.assertEqual(recs["PARTIAL"]["verdict"], "UNKNOWN")

    def test_busy_machine_is_full_and_mixed_code_flagged(self):
        recent = [self.today - dt.timedelta(days=1)]
        self.add_days("BUSY", recent, busy_fn=lambda i: 20.0)
        self.add_days("OTHER", recent, code="zzz")
        recs = self.recs()
        self.assertEqual(recs["BUSY"]["verdict_untrusted"], "FULL")
        self.assertEqual(recs["BUSY"]["verdict"], "UNKNOWN")
        self.assertIn("MIXED-CODE", recs["BUSY"]["states"])
        self.assertIn("ASSUMED", recs["BUSY"]["safe_basis"])

    def test_old_full_day_with_recent_partial_is_stale(self):
        self.add_days("BOX", [self.today - dt.timedelta(days=6)])
        self.add_days("BOX", [self.today - dt.timedelta(days=1)], coverage=1)
        rec = self.recs(expect=["BOX"])["BOX"]
        self.assertIn("STALE", rec["states"])
        self.assertEqual(rec["verdict"], "UNKNOWN")

    def test_stale_or_retired_machine_does_not_void_others(self):
        self.add_days("NEW", [self.today - dt.timedelta(days=1)], code="v2")
        self.add_days("OLDBOX", [self.today - dt.timedelta(days=5)], code="v1")
        self.add_days("RETIRED", [self.today - dt.timedelta(days=1)], code="v0")
        recs = self.recs(expect=["NEW", "OLDBOX"])
        self.assertNotIn("RETIRED", recs)                        # not expected: not read, cannot hold exit 1
        self.assertEqual((recs["NEW"]["states"], recs["NEW"]["verdict"]), ([], "ROOM"))
        self.assertIn("STALE", recs["OLDBOX"]["states"])
        self.assertNotIn("MIXED-CODE", recs["OLDBOX"]["states"])

    def test_duplicated_and_bus_not_refreshed_void_and_exit_1(self):
        day = self.today - dt.timedelta(days=1)
        data = self.tmp / "dup"
        rows = full_day(day, machine="DUP")
        write_day(data, day, rows + rows[:3])
        row = ml.rollup(data, day, allow={"airmypc"})
        p = self.bus / ml.BUS_DIR / "DUP" / "days-x.jsonl"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(row) + "\n")
        run("git", "add", ".", cwd=self.bus); run("git", "commit", "-qm", "dup", cwd=self.bus); run("git", "push", "-q", "origin", "HEAD:master", cwd=self.bus)
        rec = self.recs(expect=["DUP"])["DUP"]
        self.assertIn("DUPLICATED", rec["states"])
        self.assertEqual((rec["verdict"], rec["verdict_untrusted"]), ("UNKNOWN", "ROOM"))
        run("git", "remote", "set-url", "origin", str(self.tmp / "gone.git"), cwd=self.bus)
        rec = self.recs(expect=["DUP"])["DUP"]
        self.assertIn("BUS-NOT-REFRESHED", rec["states"])
        old = os.environ.copy()
        os.environ.clear(); os.environ.update(CLEAN_ENV)
        try:
            self.assertEqual(ml.main(["headroom", "--bus", str(self.bus), "--expect", "DUP", "--json"]), 1)
        finally:
            os.environ.clear(); os.environ.update(old)

    def test_live_stale_when_this_machine_has_no_rows(self):
        me = ml.socket.gethostname().upper()
        self.add_days(me, [self.today - dt.timedelta(days=1)])
        old_dir = ml.DATA_DIR
        ml.DATA_DIR = self.tmp / "empty-live"
        old = os.environ.copy()
        os.environ.clear(); os.environ.update(CLEAN_ENV)
        try:
            rec = {r["machine"]: r for r in ml.headroom(self.bus, 7, [me], live=True)}[me]
        finally:
            ml.DATA_DIR = old_dir
            os.environ.clear(); os.environ.update(old)
        self.assertIn("LIVE-STALE", rec["states"])
        self.assertEqual(rec["verdict"], "UNKNOWN")

    def test_clean_fleet_exits_0(self):
        self.add_days("ONE", [self.today - dt.timedelta(days=1)])
        old = os.environ.copy()
        os.environ.clear(); os.environ.update(CLEAN_ENV)
        try:
            self.assertEqual(ml.main(["headroom", "--bus", str(self.bus), "--expect", "ONE", "--json"]), 0)
        finally:
            os.environ.clear(); os.environ.update(old)

    def test_busy_machine_alone_is_full(self):
        self.add_days("BUSY", [self.today - dt.timedelta(days=1)], busy_fn=lambda i: 20.0)
        rec = self.recs()["BUSY"]
        self.assertEqual((rec["states"], rec["verdict"]), ([], "FULL"))


class Publish(unittest.TestCase):
    """publish() against a throwaway origin: missing days, idempotency, receipts."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.origin = self.tmp / "origin.git"
        self.bus = self.tmp / "bus"
        run("git", "init", "-q", "--bare", "-b", "master", str(self.origin), cwd=self.tmp)
        run("git", "clone", "-q", str(self.origin), str(self.bus), cwd=self.tmp)
        run("git", "config", "user.email", "t@t", cwd=self.bus)
        run("git", "config", "user.name", "t", cwd=self.bus)
        (self.bus / "README.md").write_text("x")
        run("git", "add", ".", cwd=self.bus)
        run("git", "commit", "-qm", "init", cwd=self.bus)
        run("git", "push", "-q", "origin", "HEAD:master", cwd=self.bus)
        self.data = self.tmp / "data"
        self.receipts = self.tmp / "receipts"
        self.yesterday = ml.utc_now().date() - dt.timedelta(days=1)
        write_day(self.data, self.yesterday, full_day(self.yesterday, machine=ml.socket.gethostname().upper()))
        self.env = os.environ.copy()
        os.environ.clear(); os.environ.update(CLEAN_ENV)

    def tearDown(self):
        os.environ.clear(); os.environ.update(self.env)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_publishes_once_with_gaps_and_is_idempotent(self):
        code = ml.main(["publish", "--bus", str(self.bus), "--dir", str(self.data), "--receipt-dir", str(self.receipts)])
        self.assertEqual(code, 0)
        rows = ml.bus_rows(self.bus)
        self.assertEqual([r["date"] for r in rows], [self.yesterday.isoformat()])   # nine missing days skipped, no crash
        self.assertNotIn("SecretProcessName", json.dumps(rows))
        code = ml.main(["publish", "--bus", str(self.bus), "--dir", str(self.data), "--receipt-dir", str(self.receipts)])
        self.assertEqual(code, 0)
        self.assertEqual(len(ml.bus_rows(self.bus)), 1)
        rec = json.loads((self.receipts / "publish-receipt.json").read_text())
        self.assertEqual((rec["exit"], rec["launched_by"]), (0, "hand"))

    def test_old_retained_day_is_published_after_a_long_outage(self):
        old = ml.utc_now().date() - dt.timedelta(days=12)
        write_day(self.data, old, full_day(old, machine=ml.socket.gethostname().upper()))
        self.assertEqual(ml.main(["publish", "--bus", str(self.bus), "--dir", str(self.data), "--receipt-dir", str(self.receipts)]), 0)
        self.assertEqual(sorted(r["date"] for r in ml.bus_rows(self.bus)), [old.isoformat(), self.yesterday.isoformat()])

    def test_rejected_push_is_retried(self):
        hook = self.origin / "hooks" / "pre-receive"
        hook.write_text("#!/bin/sh\nif [ ! -f rejected-once ]; then touch rejected-once; echo no >&2; exit 1; fi\nexit 0\n", newline="\n")
        os.chmod(hook, 0o755)
        code, report, head = ml.publish(self.bus, self.data)
        self.assertEqual(code, 0)
        self.assertTrue(any("rejected" in line for line in report), report)
        self.assertEqual([r["date"] for r in ml.bus_rows(self.bus)], [self.yesterday.isoformat()])

    def test_unwritable_receipt_is_reported_not_silent(self):
        blocker = self.tmp / "blocker"
        blocker.write_text("a file where the receipt folder should be")
        code = ml.main(["publish", "--bus", str(self.bus), "--dir", str(self.data), "--receipt-dir", str(blocker / "r")])
        self.assertEqual(code, 4)

    def test_failure_writes_a_failing_receipt(self):
        (self.receipts).mkdir(parents=True)
        (self.receipts / "publish-receipt.json").write_text(json.dumps({"exit": 0}))
        code = ml.main(["publish", "--bus", str(self.tmp / "no-such-clone"), "--dir", str(self.data),
                        "--receipt-dir", str(self.receipts), "--launched-by", "task"])
        self.assertEqual(code, 3)
        rec = json.loads((self.receipts / "publish-receipt.json").read_text())
        self.assertEqual((rec["exit"], rec["launched_by"]), (3, "task"))


class InstallerChecks(unittest.TestCase):
    """Runs Install-MachineLoad.tests.ps1 (junctions, hard links, ACLs, planted files, the sampler matcher)."""

    @unittest.skipUnless(os.name == "nt" and shutil.which("pwsh"), "Windows with pwsh 7 only")
    def test_installer_checks(self):
        p = subprocess.run(["pwsh", "-NoProfile", "-File", str(HERE / "Install-MachineLoad.tests.ps1")],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=1)
