#!/usr/bin/env python3
"""Regression tests for tools/factory/model-posture.py. Stdlib only; every repo is a temp fixture (tests never
census the host). Run: python tools/factory/model-posture.tests.py"""
from __future__ import annotations

import datetime as dt
import importlib.util
import io
import json
import os
import re
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUS = HERE.parent.parent
spec = importlib.util.spec_from_file_location("model_posture", HERE / "model-posture.py")
mp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mp)

for _k, _v in (("GIT_AUTHOR_NAME", "t"), ("GIT_AUTHOR_EMAIL", "t@example.invalid"),
               ("GIT_COMMITTER_NAME", "t"), ("GIT_COMMITTER_EMAIL", "t@example.invalid")):
    os.environ.setdefault(_k, _v)

H = "a" * 64


def ev(ts="2026-10-20T10:00:00Z", provider="codex", req="gpt-6.1-sol", eff="gpt-6.1-sol", effort="high",
       role="pre-key-review", outcome="APPROVED", task=None, codes=(), event="TERMINAL", project="conjugal", **m):
    meas = {"quality": "exact", "source": "codex-exec"}
    meas.update({k: v for k, v in m.items()})
    e = {"schema_version": 1, "event_id": "evt-00000001", "ts": ts, "project": project,
         "host_cell": "opaque:" + "0" * 16, "quota_domain_id": "codex/opaque:" + "0" * 16, "provider": provider,
         "transport": "codex-exec", "model_requested": req, "model_effective": eff, "effort_requested": effort,
         "effort_effective": effort, "actor": {"lane": "kernel", "role": role}, "event": event, "outcome": outcome,
         "reason_codes": list(codes), "measurement": meas}
    if task:
        e["task_id_hash"] = task
    return e


def run(*argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        rc = mp.main(list(argv))
    return rc, out.getvalue(), err.getvalue()


class Reduce(unittest.TestCase):
    def test_groups_stats_histogram_rounds(self):
        rows = [ev(task="1" * 64, outcome="CHANGES_REQUESTED", input_tokens=100, output_tokens=10, active_seconds=30),
                ev(ts="2026-10-21T10:00:00Z", task="1" * 64, outcome="APPROVED", input_tokens=300, output_tokens=30),
                ev(task="2" * 64, outcome="APPROVED", input_tokens=200, output_tokens="unknown"),
                ev(eff="gpt-6-astra", req="gpt-6.1-sol", outcome="FAILED"),          # fallback by model change
                ev(event="USAGE_OBSERVED"),                                           # not a call
                ev(ts="2026-10-27T10:00:00Z")]                                        # next ISO week
        recs = mp.reduce_events(rows, "conjugal", "2026-W43")
        self.assertEqual(len(recs), 2)
        sol = next(r for r in recs if r["model_effective"] == "gpt-6.1-sol")
        self.assertEqual((sol["calls"], sol["tasks"], sol["first_pass_accept"], sol["fallback_count"]), (3, 2, 1, 0))
        self.assertEqual(sol["measurement"]["input_tokens"], {"known": 3, "sum": 600, "p50": 200, "p90": 300})
        self.assertEqual(sol["measurement"]["output_tokens"]["known"], 2)
        self.assertEqual(sol["rounds"], {"known": 2, "sum": 3, "p50": 1, "p90": 2})
        self.assertEqual(sol["outcome"], {"APPROVED": 2, "CHANGES_REQUESTED": 1})
        astra = next(r for r in recs if r["model_effective"] == "gpt-6-astra")
        self.assertEqual(astra["fallback_count"], 1)
        for r in recs:
            mp.validate(r)

    def test_fallback_reason_code(self):
        r = mp.reduce_events([ev(codes=["MODEL_FALLBACK_TIER"])], "conjugal", "2026-W43")[0]
        self.assertEqual(r["fallback_count"], 1)

    def test_bytes_are_deterministic_and_order_free(self):
        rows = [ev(role=r, input_tokens=i) for i, r in enumerate(["b", "a", "c", "a"])]
        a = mp.serialize(mp.reduce_events(rows, "conjugal", "2026-W43"))
        b = mp.serialize(mp.reduce_events(list(reversed(rows)), "conjugal", "2026-W43"))
        self.assertEqual(a, b)

    def test_project_mismatch_and_bad_fields_refuse(self):
        with self.assertRaises(mp.Refused) as c:
            mp.reduce_events([ev(project="other")], "conjugal", "2026-W43")
        self.assertEqual(c.exception.code, "INPUT_PROJECT_MISMATCH")
        with self.assertRaises(mp.Refused) as c:
            mp.reduce_events([ev(role="who@example.com")], "conjugal", "2026-W43")
        self.assertEqual(c.exception.code, "INPUT_FIELD_INVALID")

    def test_nothing_private_travels(self):
        data = mp.serialize(mp.reduce_events([ev(task="f" * 64, input_tokens=1)], "conjugal", "2026-W43"))
        text = data.decode()
        for banned in ("f" * 64, "2026-10-20", "opaque:", "quota", "host_cell", "event_id", "task_id_hash", "codex-exec"):
            self.assertNotIn(banned, text)
        mp.check_shard(data, "conjugal", "2026-W43")

    def test_cli_reduce_round_trip(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "calls.jsonl"
            p.write_text(json.dumps(ev(input_tokens=5)) + "\n", encoding="utf-8")
            rc, out, err = run("reduce", "--input", str(p), "--project", "conjugal", "--week", "2026-W43")
            self.assertEqual(rc, 0, err)
            self.assertEqual(json.loads(out)["calls"], 1)


class Screen(unittest.TestCase):
    def rec(self, **kw):
        r = mp.reduce_events([ev()], "conjugal", "2026-W43")[0]
        r.update(kw)
        return r

    def test_whitelist_refuses_unknown_fields(self):
        for extra in ("session_id_hash", "window_utilization_pct", "account", "ts", "prompt", "subject"):
            with self.assertRaises(mp.Refused) as c:
                mp.validate(self.rec(**{extra: "x"}))
            self.assertEqual(c.exception.code, "RECORD_INVALID", extra)

    def test_screen_refuses_each_never_publish_class(self):
        base = self.rec()
        for bad in ("who@example.com", "12345678-1234-1234-1234-123456789abc", "S147", "2026-10-20T10:00",
                    "C:/code/x", "coordination/lanes/x", "quota", "pairprog_x", "session"):
            line = json.dumps({**base, "role": bad}, sort_keys=True) + "\n"
            with self.assertRaises(mp.Refused, msg=bad) as c:
                mp.screen(line.encode("ascii"))
            self.assertEqual(c.exception.code, "SCREEN_REFUSED", bad)

    def test_stray_sha_refused(self):
        line = json.dumps({**self.rec(), "model_requested": "c" * 40}, sort_keys=True) + "\n"
        with self.assertRaises(mp.Refused):
            mp.screen(line.encode("ascii"))

    def test_shard_over_budget_refuses_never_truncates(self):
        rows = [ev(req=f"m-{i:04d}", eff=f"m-{i:04d}") for i in range(40)]
        data = mp.serialize(mp.reduce_events(rows, "conjugal", "2026-W43"))
        self.assertGreater(len(data), 16 * 1024)
        with self.assertRaises(mp.Refused) as c:
            mp.check_shard(data, "conjugal", "2026-W43")
        self.assertEqual(c.exception.code, "SHARD_OVER_BUDGET")

    def test_union_covers_both_upstream_screens(self):
        """Every class name in bus fleet-scorecard SCREEN is in this tool's union (Conjugal's LAW4 is mirrored by name
        in the spec; the bus cannot import it)."""
        src = (HERE / "fleet-scorecard.py").read_text(encoding="utf-8")
        names = set(re.findall(r'^\s+\("([^"]+)", re\.compile', src.split("SCREEN = (", 1)[1].split("\n)\n", 1)[0], re.M))
        self.assertTrue(names)
        self.assertLessEqual(names, {n for n, _ in mp.SCREEN})
        law4 = {"email address", "account/org uuid", "lane wire path", "HUB heartbeat", "owner transcript store",
                "bearer/API token", "owner state dir", "dead-man floor surface", "user home path", "project subject id",
                "project coordination path", "project-internal identifier"}
        self.assertLessEqual(law4, {n for n, _ in mp.SCREEN})


class SchemaAndPolicy(unittest.TestCase):
    def test_schema_matches_writer_whitelist(self):
        s = json.loads((BUS / "schemas/model-posture-rollup-v1.schema.json").read_text(encoding="utf-8"))
        self.assertFalse(s["additionalProperties"])
        self.assertEqual(set(s["properties"]), mp.TOP_REQUIRED | {"sources"})
        self.assertEqual(set(s["required"]), mp.TOP_REQUIRED)
        self.assertEqual(set(s["properties"]["measurement"]["properties"]), set(mp.MEASURES))
        self.assertEqual(set(s["properties"]["outcome"]["properties"]), set(mp.OUTCOMES))

    def test_field_names_derive_from_provider_usage_event_v1(self):
        u = json.loads((BUS / "schemas/provider-usage-event-v1.schema.json").read_text(encoding="utf-8"))
        for k in ("model_requested", "model_effective", "effort_effective", "provider"):
            self.assertIn(k, u["properties"])
        self.assertLessEqual(set(mp.MEASURES), set(u["properties"]["measurement"]["properties"]))
        self.assertEqual(set(mp.OUTCOMES), {o for o in u["properties"]["outcome"]["enum"] if o})
        self.assertIn("role", u["properties"]["actor"]["properties"])

    def test_policy_loads_and_owner_default_is_on_posture(self):
        pol = mp.load_policy(str(BUS / "policy/model-posture.json"))
        self.assertEqual((pol["providers"]["codex"]["default"]["tier"], pol["providers"]["codex"]["default"]["effort"]), ("sol", "high"))
        recs = mp.reduce_events([ev(), ev(provider="claude", req="opus", eff="claude-opus-5-5")], "conjugal", "2026-W43")
        out = mp.view(recs, pol, None, dt.date(2026, 10, 23))
        self.assertEqual(out["advisories"], [])

    def test_registered(self):
        reg = json.loads((HERE / "registry.json").read_text(encoding="utf-8"))
        self.assertEqual(reg["tools"]["model-posture"]["path"], mp.TOOL_PATH)

    def test_metrics_stays_outside_the_doctrine_fold_surfaces(self):
        src = (BUS / "tools/doctrine-sync.mjs").read_text(encoding="utf-8")
        m = re.search(r"const BUS_SURFACES = \[([^\]]*)\]", src)
        self.assertIsNotNone(m, "doctrine-sync.mjs BUS_SURFACES moved: re-point this guard, never delete it")
        surfaces = re.findall(r"'([^']+)'", m.group(1))
        self.assertTrue(surfaces)
        for s in surfaces:
            for p in ("metrics/", "metrics/conjugal/posture-2026-W43.jsonl", "metrics/model-posture/README.md"):
                self.assertFalse(p.startswith(s) or s.startswith("metrics"), f"{s!r} would fold {p}")


class View(unittest.TestCase):
    pol = None

    def setUp(self):
        self.pol = mp.load_policy(str(BUS / "policy/model-posture.json"))

    def codes(self, recs, declared=None, today=dt.date(2026, 10, 23)):
        return [a["code"] for a in mp.view(recs, self.pol, declared, today)["advisories"]]

    def test_each_advisory(self):
        recs = mp.reduce_events([ev(role="key", eff="gpt-6-astra", req="gpt-6-astra")], "conjugal", "2026-W43")
        self.assertIn("OFF_OWNER_POSTURE", self.codes(recs))
        recs = mp.reduce_events([ev(effort="medium")], "conjugal", "2026-W43")
        self.assertIn("OFF_OWNER_POSTURE", self.codes(recs))
        recs = mp.reduce_events([ev(codes=["MODEL_FALLBACK"]) for _ in range(10)], "conjugal", "2026-W43")
        self.assertIn("FALLBACK_RATE_HIGH", self.codes(recs))
        recs = mp.reduce_events([ev()], "conjugal", "2026-W43")
        decl = {"roles": {"pre-key-review": {"model": "gpt-6-luna", "effort": "high"}}}
        self.assertEqual(self.codes(recs, decl), ["DRIFT_DECLARED_VS_ACTUAL"])
        self.assertEqual(self.codes(recs, today=dt.date(2026, 11, 22)), ["REASSESS_DUE"])

    def test_astra_share_cap(self):
        rows = [ev(eff="gpt-6-astra", req="gpt-6-astra")] * 3 + [ev()]
        self.assertIn("OFF_OWNER_POSTURE", self.codes(mp.reduce_events(rows, "conjugal", "2026-W43")))

    def test_exit_code_never_depends_on_values_and_nothing_is_stored(self):
        with tempfile.TemporaryDirectory() as d:
            shard = Path(d) / "s.jsonl"
            shard.write_bytes(mp.serialize(mp.reduce_events([ev(effort="low", codes=["FALLBACK"])] * 12, "conjugal", "2026-W43")))
            before = sorted(os.listdir(d))
            rc, out, _ = run("view", str(shard), "--policy", str(BUS / "policy/model-posture.json"), "--today", "2027-01-01")
            self.assertEqual(rc, 0)
            self.assertFalse(json.loads(out)["stored"])
            self.assertTrue(json.loads(out)["advisories"])
            self.assertEqual(sorted(os.listdir(d)), before)


def git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True, text=True).stdout.strip()


class PublishAndPrune(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.bus = Path(self.tmp.name) / "bus"
        self.bus.mkdir()
        git(self.bus, "init", "-q", "-b", "master")
        git(self.bus, "config", "core.autocrlf", "false")
        (self.bus / "README.md").write_text("x\n", encoding="utf-8")
        git(self.bus, "add", "README.md")
        git(self.bus, "commit", "-qm", "init")

    def tearDown(self):
        self.tmp.cleanup()

    def publish_week(self, week, ts):
        shard = Path(self.tmp.name) / f"{week}.jsonl"
        shard.write_bytes(mp.serialize(mp.reduce_events([ev(ts=ts, input_tokens=10), ev(ts=ts, role="census",
                          req="gpt-6-luna", eff="gpt-6-luna", input_tokens=4)], "conjugal", week)))
        rc, out, err = run("publish", "--bus", str(self.bus), "--shard", str(shard), "--project", "conjugal", "--week", week)
        self.assertEqual(rc, 0, err)
        rel = json.loads(out)["path"]
        git(self.bus, "add", rel)
        git(self.bus, "commit", "-qm", f"publish {week}")
        return rel

    def test_callers_screen_reduce_and_publish(self):
        """The screen is wired into BOTH CLI paths, not only callable (mutate the caller: drop check_shard -> red)."""
        calls = Path(self.tmp.name) / "calls.jsonl"
        calls.write_text(json.dumps(ev(req="S147", eff="S147")) + "\n", encoding="utf-8")
        rc, out, err = run("reduce", "--input", str(calls), "--project", "conjugal", "--week", "2026-W43")
        self.assertEqual((rc, out, "SCREEN_REFUSED" in err), (2, "", True))
        shard = Path(self.tmp.name) / "bad.jsonl"
        shard.write_bytes(mp.serialize(mp.reduce_events([ev(req="S147", eff="S147")], "conjugal", "2026-W43")))
        rc, _, err = run("publish", "--bus", str(self.bus), "--shard", str(shard), "--project", "conjugal", "--week", "2026-W43")
        self.assertEqual((rc, "SCREEN_REFUSED" in err), (2, True))
        self.assertFalse((self.bus / "metrics").exists())

    def test_publish_refuses_rewrite_and_empty(self):
        self.publish_week("2026-W43", "2026-10-20T10:00:00Z")
        other = Path(self.tmp.name) / "other.jsonl"
        other.write_bytes(mp.serialize(mp.reduce_events([ev(input_tokens=99)], "conjugal", "2026-W43")))
        rc, _, err = run("publish", "--bus", str(self.bus), "--shard", str(other), "--project", "conjugal", "--week", "2026-W43")
        self.assertEqual((rc, "SHARD_EXISTS" in err), (2, True))
        empty = Path(self.tmp.name) / "empty.jsonl"
        empty.write_bytes(b"")
        rc, _, err = run("publish", "--bus", str(self.bus), "--shard", str(empty), "--project", "conjugal", "--week", "2026-W44")
        self.assertEqual((rc, "SHARD_EMPTY" in err), (2, True))

    def test_plan_ages(self):
        weeks = ["2026-W27", "2026-W31", "2026-W36", "2026-W40"]   # July (Thu 2 Jul, 30 Jul), Sept, Oct
        plans = mp.plan_prune(weeks, dt.date(2026, 10, 22))         # this Monday 19 Oct; cutoff Monday 24 Aug
        self.assertEqual(plans, [("2026-07", ["2026-W27", "2026-W31"])])
        self.assertEqual(mp.plan_prune(["2025-09", "2025-10", "2025"], dt.date(2026, 10, 22)), [("2025", ["2025", "2025-09"])])

    def test_prune_commits_add_plus_deletes_and_recomputes(self):
        w1 = self.publish_week("2026-W27", "2026-06-30T10:00:00Z")
        w2 = self.publish_week("2026-W31", "2026-07-28T10:00:00Z")
        keep = self.publish_week("2026-W43", "2026-10-20T10:00:00Z")
        before = git(self.bus, "rev-parse", "HEAD")
        rc, out, err = run("prune", "--bus", str(self.bus), "--project", "conjugal", "--today", "2026-10-22")
        self.assertEqual(rc, 0, err)
        self.assertEqual([p["result"] for p in json.loads(out)["prune"]], ["PLANNED"])
        self.assertEqual(git(self.bus, "rev-parse", "HEAD"), before)          # dry run writes no commit
        rc, out, err = run("prune", "--bus", str(self.bus), "--project", "conjugal", "--today", "2026-10-22", "--commit")
        self.assertEqual(rc, 0, err)
        names = sorted(git(self.bus, "diff", "--name-status", "--no-renames", "HEAD^", "HEAD").splitlines())
        self.assertEqual(names, ["A\tmetrics/conjugal/posture-2026-07.jsonl", f"D\t{w1}", f"D\t{w2}"])
        rec = [json.loads(l) for l in git(self.bus, "show", "HEAD:metrics/conjugal/posture-2026-07.jsonl").splitlines()]
        self.assertEqual(sum(r["calls"] for r in rec), 4)
        self.assertEqual({s["path"] for s in rec[0]["sources"]}, {w1, w2})
        for r in rec:
            mp.validate(r)
            self.assertEqual(r["sources"][0]["blob"], git(self.bus, "rev-parse", f"HEAD^:{r['sources'][0]['path']}"))
        self.assertTrue((self.bus / keep).exists())
        # idempotent, and history is untouched: the sources still resolve from the parent
        rc, out, _ = run("prune", "--bus", str(self.bus), "--project", "conjugal", "--today", "2026-10-22", "--commit")
        self.assertEqual(json.loads(out)["prune"], [])
        git(self.bus, "cat-file", "-e", f"HEAD^:{w1}")

    def test_month_to_year_keeps_year_forever(self):
        self.publish_week("2025-W27", "2025-07-01T10:00:00Z")
        rc, out, err = run("prune", "--bus", str(self.bus), "--project", "conjugal", "--today", "2026-10-22", "--commit")
        self.assertEqual(rc, 0, err)
        self.assertEqual([p["target"] for p in json.loads(out)["prune"]],
                         ["metrics/conjugal/posture-2025-07.jsonl", "metrics/conjugal/posture-2025.jsonl"])
        self.assertEqual(sorted(os.listdir(self.bus / "metrics/conjugal")), ["posture-2025.jsonl"])
        # a late month rolls INTO the year: the yearly file is replaced (M), never deleted
        self.publish_week("2025-W36", "2025-09-02T10:00:00Z")
        rc, out, err = run("prune", "--bus", str(self.bus), "--project", "conjugal", "--today", "2026-10-22", "--commit")
        self.assertEqual(rc, 0, err)
        names = sorted(git(self.bus, "diff", "--name-status", "--no-renames", "HEAD^", "HEAD").splitlines())
        self.assertEqual(names, ["D\tmetrics/conjugal/posture-2025-09.jsonl", "M\tmetrics/conjugal/posture-2025.jsonl"])
        year = [json.loads(l) for l in (self.bus / "metrics/conjugal/posture-2025.jsonl").read_text().splitlines()]
        self.assertEqual(sum(r["calls"] for r in year), 4)

    def test_prune_refuses_a_dirty_index(self):
        self.publish_week("2026-W27", "2026-06-30T10:00:00Z")
        (self.bus / "other.txt").write_text("x", encoding="utf-8")
        git(self.bus, "add", "other.txt")
        rc, _, err = run("prune", "--bus", str(self.bus), "--project", "conjugal", "--today", "2026-10-22", "--commit")
        self.assertEqual((rc, "INDEX_NOT_CLEAN" in err), (2, True))


def rec_line(**kw) -> bytes:
    """One weekly record, canonical, with fields overridden AFTER reduce (so the writer's own input checks are
    bypassed and the shard checks are what is under test)."""
    r = mp.reduce_events([ev()], "conjugal", "2026-W43")[0]
    r.update(kw)
    return mp.serialize([r])


class R19Defects(unittest.TestCase):
    """One test (or more) per RULINGS.md R19.3 defect (a)-(h); each was red on the r1 head 6b6d79dd."""

    def refused(self, fn, *codes):
        with self.assertRaises(mp.Refused) as c:
            fn()
        self.assertIn(c.exception.code, codes)
        return c.exception

    # (a) the screen reads DECODED values: a JSON \u escape of a prohibited value is refused, and a
    # non-canonical line is refused outright.
    def test_a_escaped_identifier_is_screened(self):
        line = rec_line().decode().replace('"model_requested":"gpt-6.1-sol"', '"model_requested":"\\u0053147"')
        self.assertIn("\\u0053147", line)
        self.refused(lambda: mp.screen(line.encode()), "SCREEN_REFUSED", "RECORD_NOT_CANONICAL")
        self.refused(lambda: mp.check_shard(line.encode(), "conjugal", "2026-W43"),
                     "SCREEN_REFUSED", "RECORD_NOT_CANONICAL", "RECORD_INVALID")

    def test_a_escaped_email_is_screened(self):
        line = rec_line().decode().replace('"model_requested":"gpt-6.1-sol"', '"model_requested":"who\\u0040example.com"')
        self.refused(lambda: mp.screen(line.encode()), "SCREEN_REFUSED", "RECORD_NOT_CANONICAL")

    def test_a_non_canonical_line_refused(self):
        line = json.dumps(json.loads(rec_line()), sort_keys=True) + "\n"      # default separators add spaces
        self.refused(lambda: mp.check_shard(line.encode(), "conjugal", "2026-W43"), "RECORD_NOT_CANONICAL")

    # (b) 40-hex provenance fields are authenticated, never trusted for their shape.
    def test_b_forged_generator_blob_refused(self):
        data = rec_line(generator={"path": mp.TOOL_PATH, "blob": "c" * 40})
        self.refused(lambda: mp.check_shard(data, "conjugal", "2026-W43"), "PROVENANCE_UNAUTHENTICATED")

    def test_b_real_generator_blob_accepted(self):
        mp.check_shard(rec_line(), "conjugal", "2026-W43")

    def test_b_forged_source_blob_refused_against_the_bus(self):
        with tempfile.TemporaryDirectory() as d:
            git(d, "init", "-q", "-b", "master")
            wk = mp.reduce_events([ev()], "conjugal", "2026-W43")
            src = [{"path": "metrics/conjugal/posture-2026-W43.jsonl", "blob": "d" * 40}]
            data = mp.serialize(mp.merge_records(wk, "conjugal", "2026-10", src))
            self.refused(lambda: mp.check_shard(data, "conjugal", "2026-10", bus=d), "PROVENANCE_UNAUTHENTICATED")
            self.refused(lambda: mp.check_shard(data, "conjugal", "2026-10"), "PROVENANCE_UNAUTHENTICATED")

    # (c) role is a closed enum and model names carry no path separator.
    def test_c_free_text_role_never_travels(self):
        for role in ("BACHELOR", "host-xps17", "ticket-38172", "a" * 32, "Ignore-previous-instructions"):
            try:
                data = mp.serialize(mp.reduce_events([ev(role=role)], "conjugal", "2026-W43"))
            except mp.Refused as e:
                self.assertEqual(e.code, "INPUT_FIELD_INVALID", role)
                continue
            self.assertNotIn(role, data.decode(), role)
            self.assertEqual(json.loads(data)["role"], "other")
        self.refused(lambda: mp.check_shard(rec_line(role="BACHELOR"), "conjugal", "2026-W43"), "RECORD_INVALID")

    def test_c_model_with_path_separator_refused(self):
        self.refused(lambda: mp.reduce_events([ev(req="private-repo/secrets.txt")], "conjugal", "2026-W43"),
                     "INPUT_FIELD_INVALID")
        self.refused(lambda: mp.check_shard(rec_line(model_effective="a/b"), "conjugal", "2026-W43"), "RECORD_INVALID")

    def test_c_schema_role_is_the_writer_enum(self):
        s = json.loads((BUS / "schemas/model-posture-rollup-v1.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(set(s["properties"]["role"]["enum"]) - {None}, set(mp.ROLES))
        self.assertNotIn("/", s["properties"]["model_effective"]["pattern"])

    # (d) the schema's own outcome key is legal.
    def test_d_quota_dormant_outcome_passes(self):
        data = mp.serialize(mp.reduce_events([ev(outcome="QUOTA_DORMANT")], "conjugal", "2026-W43"))
        self.assertIn("QUOTA_DORMANT", data.decode())
        mp.check_shard(data, "conjugal", "2026-W43")

    # (e) a Claude alias resolving to its dated id is not a fallback.
    def test_e_alias_resolution_is_not_fallback(self):
        pol = mp.load_policy(str(BUS / "policy/model-posture.json"))
        recs = mp.reduce_events([ev(provider="claude", req="opus", eff="claude-opus-5-5")] * 10, "conjugal", "2026-W43")
        self.assertEqual(recs[0]["fallback_count"], 0)
        self.assertNotIn("FALLBACK_RATE_HIGH", [a["code"] for a in mp.view(recs, pol, None, dt.date(2026, 10, 23))["advisories"]])
        other = mp.reduce_events([ev(provider="claude", req="opus", eff="claude-sonnet-5-5")], "conjugal", "2026-W43")
        self.assertEqual(other[0]["fallback_count"], 1)

    # (f) the effective id decides; a matching request cannot hide a stale effective model.
    def test_f_effective_drift_is_not_masked(self):
        pol = mp.load_policy(str(BUS / "policy/model-posture.json"))
        recs = mp.reduce_events([ev(req="gpt-6.1-sol", eff="gpt-5.6-sol")], "conjugal", "2026-W43")
        self.assertIn("OFF_OWNER_POSTURE", [a["code"] for a in mp.view(recs, pol, None, dt.date(2026, 10, 23))["advisories"]])

    # (g) tiers, not literal ids; Luna must be high; R11 swarm lanes run medium.
    def codes(self, rows):
        pol = mp.load_policy(str(BUS / "policy/model-posture.json"))
        return [a["code"] for a in mp.view(mp.reduce_events(rows, "conjugal", "2026-W43"), pol, None, dt.date(2026, 10, 23))["advisories"]]

    def test_g_newer_tier_id_is_on_posture(self):
        self.assertEqual(self.codes([ev(req="gpt-6.2-sol", eff="gpt-6.2-sol")]), [])
        self.assertEqual(self.codes([ev(role="census", req="gpt-6.1-luna", eff="gpt-6.1-luna")]), [])

    def test_g_low_effort_luna_is_off_posture(self):
        self.assertIn("OFF_OWNER_POSTURE", self.codes([ev(role="census", req="gpt-6-luna", eff="gpt-6-luna", effort="low")]))

    def test_g_r11_swarm_lane_at_medium_is_on_posture(self):
        self.assertEqual(self.codes([ev(role="swarm", effort="medium")]), [])
        self.assertIn("OFF_OWNER_POSTURE", self.codes([ev(role="swarm", effort="low")]))

    def test_g_policy_names_no_literal_codex_id(self):
        raw = (BUS / "policy/model-posture.json").read_text(encoding="utf-8")
        roles = json.loads(raw)["roles"]
        for role, rp in roles.items():
            for e in [*rp.get("allowed", []), *rp.get("max_share", [])]:
                if e.get("provider") == "codex":
                    self.assertIn("tier", e, (role, e))
                    self.assertNotIn("model_pattern", e, (role, e))

    # (h) the candidate states its relationship to existing doctrine, naming the append-only supersession.
    def test_h_candidate_relationship_line(self):
        c = (BUS / "ruling-candidates/fleet-model-posture-telemetry-r2.md").read_text(encoding="utf-8")
        line = next((l for l in c.splitlines() if l.startswith("Relationship to existing doctrine:")), "")
        self.assertTrue(line)
        self.assertIn("metrics/README.md", line)
        self.assertIn("supersedes", line)


class RefusalCoverage(unittest.TestCase):
    """Every refusal code the tool can raise has a behavioural test (R19.3: refusals are proven, not named)."""

    def code(self, fn):
        with self.assertRaises(mp.Refused) as c:
            fn()
        return c.exception.code

    def test_input_refusals(self):
        self.assertEqual(self.code(lambda: mp.reduce_events([], "Bad Project", "2026-W43")), "PROJECT_INVALID")
        self.assertEqual(self.code(lambda: mp.reduce_events([], "conjugal", "2026-10")), "PERIOD_INVALID")
        self.assertEqual(self.code(lambda: mp.reduce_events([], "conjugal", "2026-W99")), "PERIOD_INVALID")
        self.assertEqual(self.code(lambda: mp.reduce_events(["x"], "conjugal", "2026-W43")), "INPUT_ROW_INVALID")
        self.assertEqual(self.code(lambda: mp.reduce_events([ev(ts="yesterday")], "conjugal", "2026-W43")), "INPUT_ROW_INVALID")
        self.assertEqual(self.code(lambda: mp.reduce_events([ev(provider=None)], "conjugal", "2026-W43")), "INPUT_FIELD_INVALID")
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "c.jsonl"
            p.write_text("{not json\n", encoding="utf-8")
            self.assertEqual(self.code(lambda: mp.read_events(str(p))), "INPUT_ROW_INVALID")

    def test_policy_refusals(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self.code(lambda: mp.load_policy(str(Path(d) / "missing.json"))), "POLICY_UNREADABLE")
            p = Path(d) / "p.json"
            p.write_text('{"schema": "other"}', encoding="utf-8")
            self.assertEqual(self.code(lambda: mp.load_policy(str(p))), "POLICY_INVALID")
            p.write_text(json.dumps({"schema": mp.POLICY_SCHEMA}), encoding="utf-8")
            self.assertEqual(self.code(lambda: mp.load_policy(str(p))), "POLICY_INVALID")

    def test_source_project_mismatch(self):
        wk = mp.reduce_events([ev()], "conjugal", "2026-W43")
        self.assertEqual(self.code(lambda: mp.merge_records(wk, "other", "2026-10", [])), "SOURCE_PROJECT_MISMATCH")

    def test_screen_fixture_classes(self):
        base = json.loads(rec_line())
        for bad in ("sk-ant-abcdefghijklmnop", "Bearer abcdefghijklmnopqrstuvwxyz", "C:/Users/someone/x",
                    "/home/someone/x", "HUB.md", "loops.json", "x state/y", "coordination/deadman/x", "c" * 40):
            line = (json.dumps({**base, "model_requested": bad}, sort_keys=True, separators=(",", ":")) + "\n").encode()
            self.assertEqual(self.code(lambda: mp.screen(line)), "SCREEN_REFUSED", bad)

    def test_git_failed(self):
        with tempfile.TemporaryDirectory() as d:
            rc, _, err = run("prune", "--bus", d, "--project", "conjugal", "--today", "2026-10-22")
            self.assertEqual((rc, "GIT_FAILED" in err), (2, True))


class RollupRefusals(unittest.TestCase):
    """The two roll-up integrity refusals, provoked by mutating the caller (the tool's own collaborators)."""
    setUp, tearDown, publish_week = PublishAndPrune.setUp, PublishAndPrune.tearDown, PublishAndPrune.publish_week

    def test_rollup_not_reproducible(self):
        self.publish_week("2026-W27", "2026-06-30T10:00:00Z")
        real, n = mp.merge_records, [0]

        def drifting(*a, **k):
            n[0] += 1
            out = real(*a, **k)
            out[0]["calls"] += n[0] % 2
            out[0]["outcome"] = {"APPROVED": out[0]["calls"]}
            return out
        mp.merge_records = drifting
        try:
            rc, _, err = run("prune", "--bus", str(self.bus), "--project", "conjugal", "--today", "2026-10-22", "--commit")
        finally:
            mp.merge_records = real
        self.assertEqual((rc, "ROLLUP_NOT_REPRODUCIBLE" in err), (2, True))

    def test_rollup_census_mismatch(self):
        self.publish_week("2026-W27", "2026-06-30T10:00:00Z")
        real = mp.git

        def no_rm(repo, *args, **kw):
            return "" if args and args[0] == "rm" else real(repo, *args, **kw)
        mp.git = no_rm
        try:
            rc, _, err = run("prune", "--bus", str(self.bus), "--project", "conjugal", "--today", "2026-10-22", "--commit")
        finally:
            mp.git = real
        self.assertEqual((rc, "ROLLUP_CENSUS_MISMATCH" in err), (2, True))

    def test_publish_refuses_forged_generator(self):
        shard = Path(self.tmp.name) / "forged.jsonl"
        shard.write_bytes(rec_line(generator={"path": mp.TOOL_PATH, "blob": "e" * 40}))
        rc, _, err = run("publish", "--bus", str(self.bus), "--shard", str(shard), "--project", "conjugal", "--week", "2026-W43")
        self.assertEqual((rc, "PROVENANCE_UNAUTHENTICATED" in err), (2, True))
        self.assertFalse((self.bus / "metrics").exists())


if __name__ == "__main__":
    unittest.main()
