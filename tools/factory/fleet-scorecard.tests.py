#!/usr/bin/env python3
"""Regression tests for tools/factory/fleet-scorecard.py. Stdlib only; every repo is a temp fixture
(tests never census the host). Run: python tools/factory/fleet-scorecard.tests.py"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("fleet_scorecard", HERE / "fleet-scorecard.py")
sc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sc)

NOW = "2026-10-16T12:00:00Z"
# The publish path commits through the tool's own git calls; a CI runner has no identity configured.
for _k, _v in (("GIT_AUTHOR_NAME", "t"), ("GIT_AUTHOR_EMAIL", "t@example.invalid"),
               ("GIT_COMMITTER_NAME", "t"), ("GIT_COMMITTER_EMAIL", "t@example.invalid")):
    os.environ.setdefault(_k, _v)

FAKE_RUNNER = r'''
import json, sys
a = sys.argv[1:]
if "status" in a:
    print("[factory-pins] runner: vendored copy = bus blob x (current)")
    print("[factory-pins] check-doc-size: pinned 1 @ bus 2 *** STALE *** moved")
    print("[factory-pins] tool-census: pinned 1 @ bus 2 (current)")
    sys.exit(0)
tool = a[a.index("run") + 1]
if tool == "tool-census":
    cfg = json.load(open(a[a.index("--config") + 1], encoding="utf-8"))
    if any(r.get("path") == "@bus" for r in cfg.get("roots", [])):   # '@bus' under the runner = a temp dir
        sys.exit(9)
    print(json.dumps({"total": 5, "measuredRoots": ["bus", "proj"], "absentRoots": ["far"], "families": [
        {"name": "x", "copies": [{"root": "proj", "path": "a.py", "hash": "h1"},
                                 {"root": "bus", "path": "b.py", "canonical": True, "hash": "h2"},
                                 {"root": "proj", "path": "c.py", "hash": "h3"}, {"root": "other", "path": "d.py", "hash": "h4"}]}]}))
elif tool == "check-rule-tags":
    assert "--report" in a and "--json" in a
    print(json.dumps({"project": "proj", "counts": {"bullets": 5, "backed": 2, "prose": 3, "untagged": 0,
                                                   "dangling": 0, "mixed": 0}}))
elif tool == "check-evidence-dumps":
    print(json.dumps({"violations": 4}))
else:
    sys.exit(2)
'''

# A stand-in for `gh run list`: prints <dir>/gh-runs.json, or fails like an unauthenticated gh when absent.
# The real gh is never called by a test (tests never census the host).
FAKE_GH = r'''
import sys
from pathlib import Path
f = Path(__file__).with_name("gh-runs.json")
if not f.is_file():
    print("HTTP 401: Bad credentials (https://api.github.com/graphql)", file=sys.stderr)
    sys.exit(1)
sys.stdout.write(f.read_text(encoding="utf-8"))
'''


def gh_run(wf, conclusion, created, sha="a" * 40, status="completed", rid=1):
    return {"workflowName": wf, "status": status, "conclusion": conclusion if status == "completed" else "",
            "headSha": sha, "createdAt": created, "databaseId": rid}


def git(repo, *args, env=None):
    e = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid", GIT_COMMITTER_NAME="t",
             GIT_COMMITTER_EMAIL="t@example.invalid", **(env or {}))
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True, env=e).stdout.strip()


def commit(repo, msg, when=None, path="f.txt"):
    p = Path(repo) / path
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as fh:
        fh.write(msg + "\n")
    git(repo, "add", "--", path)
    env = {"GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when} if when else None
    git(repo, "commit", "-q", "-m", msg, env=env)


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="scorecard-test-"))
        gh_dir = self.tmp / "gh"
        gh_dir.mkdir()
        (gh_dir / "fake_gh.py").write_text(FAKE_GH, encoding="utf-8")
        self.gh_runs = gh_dir / "gh-runs.json"
        self.gh_runs.write_text(json.dumps([gh_run("Doctrine sync", "success", "2026-10-16T11:00:00Z")]),
                                encoding="utf-8")
        gh_patch = unittest.mock.patch.object(sc, "gh_argv", return_value=[sys.executable, str(gh_dir / "fake_gh.py")])
        gh_patch.start()
        self.addCleanup(gh_patch.stop)
        # --- bus: bare origin + a clone (the "local bus clone") ---
        self.bus_origin = self.tmp / "bus.git"
        git(self.tmp, "init", "-q", "--bare", "-b", "master", str(self.bus_origin))
        seed = self.tmp / "bus-seed"
        git(self.tmp, "init", "-q", "-b", "master", str(seed))
        (seed / "metrics").mkdir()
        (seed / "tools").mkdir()
        (seed / "metrics" / "product-share-lines.jsonl").write_text(
            json.dumps({"project": "proj", "product_share": 0.1, "product_lines_per_week": 10, "window_days": 14, "ts": "old"}) + "\n"
            + json.dumps({"project": "other", "product_share": 0.9}) + "\n"
            + json.dumps({"project": "proj", "product_share": 0.2, "product_lines_per_week": 20, "window_days": 14, "ts": "new"}) + "\n",
            encoding="utf-8")
        (seed / "metrics" / "tool-census-baseline.json").write_text(json.dumps({"total": 7}), encoding="utf-8")
        (seed / "tools" / "tool-census.config.json").write_text(
            json.dumps({"roots": [{"name": "bus", "path": "@bus"}]}), encoding="utf-8")
        (seed / "tools" / "rule-tags.config.json").write_text("{}", encoding="utf-8")
        git(seed, "add", "-A")
        git(seed, "commit", "-q", "-m", "seed")
        git(seed, "push", "-q", str(self.bus_origin), "master")
        self.bus = self.tmp / "bus"
        git(self.tmp, "clone", "-q", str(self.bus_origin), str(self.bus))
        # --- project: bare origin + checkout ---
        self.proj_origin = self.tmp / "proj.git"
        git(self.tmp, "init", "-q", "--bare", "-b", "master", str(self.proj_origin))
        self.root = self.tmp / "proj"
        git(self.tmp, "init", "-q", "-b", "master", str(self.root))
        git(self.root, "remote", "add", "origin", str(self.proj_origin))
        commit(self.root, "base", "2026-10-01T00:00:00Z")
        git(self.root, "push", "-q", "origin", "master")
        git(self.root, "fetch", "-q", "origin")
        commit(self.root, "kernel-dogfood: S9 Outcome - ACCEPTED, delivered", "2026-10-16T02:00:00Z")
        commit(self.root, "kernel-dogfood: subjects ledger - S10 refused on round 1", "2026-10-16T03:00:00Z")
        commit(self.root, "kernel-dogfood: S8 Outcome - ACCEPTED, delivered", "2026-10-14T03:00:00Z")  # outside 24h
        git(self.root, "checkout", "-q", "-b", "side")
        commit(self.root, "side work", "2026-10-16T04:00:00Z")
        git(self.root, "checkout", "-q", "master")
        st = self.root / ".codex-state" / "doctrine"
        st.mkdir(parents=True)
        self.cursor = git(self.bus, "rev-parse", "refs/remotes/origin/master")
        (st / "last-seen.json").write_text(json.dumps({"lastSeen": self.cursor, "lastSeenAt": "2026-10-16T06:00:00Z"}),
                                           encoding="utf-8")
        (self.root / "cov.py").write_text("print('[cov] GATED TOTAL coverage=12.5%')\n", encoding="utf-8")
        q = self.root / "folds" / "queue.jsonl"
        q.parent.mkdir()
        q.write_text("\n".join(json.dumps(r) for r in [
            {"status": "QUEUED", "queued": "2026-09-16", "expires": "2026-10-15"},
            {"status": "QUEUED", "queued": "2026-10-10", "expires": "2026-11-09"},
            {"status": "ADOPT-PENDING", "queued": "2026-09-01", "expires": "2026-10-01"},
            {"status": "DISTINGUISHED", "queued": "2026-09-01", "expires": "2026-10-01"},
        ]) + "\n", encoding="utf-8")
        (self.root / "outbox.py").write_text("import sys\nprint('[outbox] 3 unsent doctrine item(s)')\nsys.exit(1)\n",
                                             encoding="utf-8")
        pins = self.root / "factory-pins"
        pins.mkdir()
        (pins / "pin-runner.py").write_text(FAKE_RUNNER, encoding="utf-8")
        (pins / "factory-pins.json").write_text(json.dumps({"tools": {"tool-census": {}, "check-rule-tags": {},
                                                                      "check-evidence-dumps": {}},
                                                            "bus_clone": [str(self.bus)]}), encoding="utf-8")
        self.cfg = {"schema": sc.CONFIG_SCHEMA, "name": "proj", "rule_tags": {"project": "proj"},
                    "fold": {"queue": "folds/queue.jsonl"},
                    "outbox": {"argv": ["python", "outbox.py"], "regex": r"(\d+) unsent", "zero_regex": "no unsent"},
                    "evidence_dumps": {"pinned": "check-evidence-dumps", "args": ["--root", "{root}"], "json": "violations"},
                    "rule_coverage": {"argv": ["python", "cov.py"], "regex": r"coverage=([0-9.]+)%", "floor": 10},
                    "kernel": {"ref": "refs/heads/master", "delivered_regex": r"^kernel-dogfood: (S\d+) Outcome - ACCEPTED",
                               "refused_regex": r"^kernel-dogfood: (?:subjects ledger - )?(S\d+) (?:refused|Outcome - REFUSED)"}}
        self.write_cfg()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write_cfg(self):
        (self.root / sc.DEFAULT_CONFIG).write_text(json.dumps(self.cfg), encoding="utf-8")

    def run_tool(self, *extra):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = sc.main(["--root", str(self.root), "--bus", str(self.bus), "--now", NOW, *extra])
        rows = [json.loads(l) for l in out.getvalue().splitlines() if l.startswith("{")]
        return code, rows, err.getvalue()

    def published(self):
        out = subprocess.run(["git", "-C", str(self.bus_origin), "show", f"master:{sc.OUTPUT}"],
                             capture_output=True, text=True)
        return [json.loads(l) for l in out.stdout.splitlines()] if out.returncode == 0 else []


class FieldTests(Fixture):
    def test_every_field_measured(self):
        code, rows, err = self.run_tool()
        self.assertEqual(code, 0, err)
        f = rows[0]["fields"]
        self.assertEqual(rows[0]["schema"], sc.ROW_SCHEMA)
        self.assertEqual(rows[0]["date"], "2026-10-16")
        self.assertEqual(f["tool_census"]["value"]["project_copies"], 2)
        self.assertEqual(f["tool_census"]["value"]["fleet_total"], 5)
        self.assertEqual(f["tool_census"]["value"]["baseline_total"], 7)
        self.assertEqual(f["rule_tags"]["value"]["backed"], 2)
        self.assertEqual(f["rule_tags"]["value"]["prose"], 3)
        self.assertEqual(f["evidence_dumps"]["value"], 4)
        self.assertEqual(f["product_share"]["value"]["product_share"], 0.2)
        d = f["doctrine_fold"]["value"]
        self.assertEqual((d["marker_age_hours"], d["queued"], d["oldest_queued_age_days"], d["overdue"], d["adopt_pending"]),
                         (6.0, 2, 30, 1, 1))
        self.assertEqual(f["outbox_unsent"]["value"], 3)
        self.assertEqual(f["commits_no_remote"]["value"], 4)
        self.assertEqual(f["master_vs_origin"]["value"], {"ahead": 3, "behind": 0})
        self.assertEqual(f["kernel_24h"]["value"], {"delivered": 1, "refused": 1})
        self.assertEqual(f["pin_stale"]["value"], 1)
        for name, v in f.items():
            self.assertIn("cmd", v, name)
            self.assertIsNone(v["error"], name)

    def test_commands_name_placeholders_never_machine_paths(self):
        _, rows, _ = self.run_tool()
        text = json.dumps(rows[0])
        for p in (str(self.root), str(self.bus), str(self.tmp)):
            self.assertNotIn(p, text)
            self.assertNotIn(p.replace("\\", "/"), text)
        self.assertIn("<root>", text)

    def test_missing_tools_and_files_are_null_fields_not_failures(self):
        (self.root / "factory-pins" / "factory-pins.json").write_text(json.dumps({"tools": {}}), encoding="utf-8")
        (self.root / ".codex-state" / "doctrine" / "last-seen.json").unlink()
        self.cfg["fold"] = {"queue": "folds/absent.jsonl"}
        del self.cfg["kernel"]
        self.write_cfg()
        code, rows, err = self.run_tool()
        self.assertEqual(code, 0, err)
        f = rows[0]["fields"]
        for name, why in (("tool_census", "NOT_PINNED"), ("rule_tags", "NOT_PINNED"), ("evidence_dumps", "NOT_PINNED"),
                          ("kernel_24h", "NOT_CONFIGURED")):
            self.assertIsNone(f[name]["value"], name)
            self.assertEqual(f[name]["error"], why, name)
        self.assertIsNone(f["doctrine_fold"]["value"])
        self.assertIn("ABSENT", f["doctrine_fold"]["error"])

    def test_no_config_needs_only_a_project_name(self):
        (self.root / sc.DEFAULT_CONFIG).unlink()
        code, rows, err = self.run_tool("--project", "bare")
        self.assertEqual(code, 0, err)
        self.assertEqual(rows[0]["project"], "bare")
        self.assertEqual(rows[0]["fields"]["rule_tags"]["error"], "NOT_CONFIGURED")
        self.assertEqual(sc.main(["--root", str(self.root), "--now", NOW]), 2)  # no config, no --project

    def test_values_never_change_the_exit_code(self):
        # an overdue queue, unsent outbox, stale pins and refused subjects are all in the fixture: still 0
        code, rows, _ = self.run_tool()
        self.assertEqual(code, 0)
        self.assertGreater(rows[0]["fields"]["doctrine_fold"]["value"]["overdue"], 0)

    def test_project_own_config_overrides_the_fleet_entry(self):
        own = {"schema": sc.CONFIG_SCHEMA, "name": "proj", "fold": {"queue": "folds/queue.jsonl", "queued_states": ["ADOPT-PENDING"]}}
        (self.root / "own.json").write_text(json.dumps(own), encoding="utf-8")
        fleet = {"schema": sc.CONFIG_SCHEMA, "projects": [{"name": "proj", "root": str(self.root), "config": "own.json"}]}
        cfgf = self.tmp / "fleet.json"
        cfgf.write_text(json.dumps(fleet), encoding="utf-8")
        code, rows, err = self.run_tool("--config", str(cfgf))
        self.assertEqual(code, 0, err)
        self.assertEqual(rows[0]["fields"]["doctrine_fold"]["value"]["queued"], 1)
        self.assertEqual(rows[0]["own_config"], "own.json")

    def test_bus_data_is_read_from_origin_master_not_the_clone_worktree(self):
        (self.bus / "metrics" / "product-share-lines.jsonl").write_text(
            json.dumps({"project": "proj", "product_share": 0.99}) + "\n", encoding="utf-8")   # uncommitted edit
        self.cfg["evidence_dumps"]["args"] = ["--cfg", "{bus:metrics/tool-census-baseline.json}"]
        self.write_cfg()
        _, rows, _ = self.run_tool()
        f = rows[0]["fields"]
        self.assertEqual(f["product_share"]["value"]["product_share"], 0.2)
        self.assertIn("<bus@origin/master>/metrics/tool-census-baseline.json", f["evidence_dumps"]["cmd"])

    def test_absent_root_is_skipped(self):
        fleet = {"schema": sc.CONFIG_SCHEMA, "projects": [{"name": "proj", "root": str(self.root)},
                                                          {"name": "gone", "root": str(self.tmp / "nope")}]}
        cfgf = self.tmp / "fleet.json"
        cfgf.write_text(json.dumps(fleet), encoding="utf-8")
        code, rows, err = self.run_tool("--config", str(cfgf))
        self.assertEqual(code, 0)
        self.assertEqual([r["project"] for r in rows], ["proj"])
        self.assertIn("SKIP gone", err)


class ScreenTests(Fixture):
    def test_screen_patterns(self):
        for bad in ("a@b.example", "C:\\Users\\someone\\x", "/home/someone/x", "coordination/lanes/sol.md", "ghp_" + "a" * 30):
            self.assertIsNotNone(sc.screen({"x": bad}), bad)
        self.assertIsNone(sc.screen({"x": "git -C <root> rev-list --count"}))

    def test_refused_row_is_not_published_and_exits_2(self):
        self.cfg["name"] = "someone@example.org"
        self.write_cfg()
        code, rows, err = self.run_tool("--publish")
        self.assertEqual(code, 2)
        self.assertEqual(rows, [])
        self.assertIn("REFUSED", err)
        self.assertEqual(self.published(), [])


class PublishTests(Fixture):
    def test_publish_is_idempotent_per_project_and_date(self):
        head_before = git(self.bus, "rev-parse", "HEAD")
        code, _, err = self.run_tool("--publish")
        self.assertEqual(code, 0, err)
        self.assertEqual(len(self.published()), 1)
        code, _, err = self.run_tool("--publish")
        self.assertEqual(code, 0, err)
        self.assertIn("already published", err)
        self.assertEqual(len(self.published()), 1)
        # the bus clone's own checkout is never touched
        self.assertEqual(git(self.bus, "rev-parse", "HEAD"), head_before)
        self.assertEqual(git(self.bus, "status", "--porcelain"), "")
        self.assertNotIn("fleet-scorecard-", git(self.bus, "worktree", "list"))

    def test_publish_appends_over_a_concurrent_push_fast_forward(self):
        other = self.tmp / "other"
        git(self.tmp, "clone", "-q", str(self.bus_origin), str(other))
        (other / sc.OUTPUT).write_text(json.dumps({"project": "sibling", "date": "2026-10-16"}) + "\n", encoding="utf-8")
        git(other, "add", "--", sc.OUTPUT)
        git(other, "commit", "-q", "-m", "sibling row")
        git(other, "push", "-q", "origin", "master")      # our clone's origin/master is now stale
        code, _, err = self.run_tool("--publish")
        self.assertEqual(code, 0, err)
        self.assertEqual([r["project"] for r in self.published()], ["sibling", "proj"])
        log = subprocess.run(["git", "-C", str(self.bus_origin), "log", "--format=%s", "master"],
                             capture_output=True, text=True).stdout.splitlines()
        self.assertIn("sibling row", log)                  # nothing was overwritten

    def test_publish_without_bus_is_unavailable(self):
        out, err = io.StringIO(), io.StringIO()
        (self.root / "factory-pins" / "factory-pins.json").write_text(json.dumps({"tools": {}}), encoding="utf-8")
        with redirect_stdout(out), redirect_stderr(err), unittest.mock.patch.dict(os.environ, {"FACTORY_BUS_CLONE": ""}):
            code = sc.main(["--root", str(self.root), "--now", NOW, "--publish"])
        self.assertEqual(code, 3, err.getvalue())


THRESHOLDS = {"schema": "fleet/health-thresholds/v1",
              "thresholds": {"bus_publish_days": 3, "fold_oldest_unfolded_hours": 72, "kernel_filing_days": 14}}


class HealthFixture(Fixture):
    """Bus history after the project's fold cursor (NOW = 2026-10-16T12:00Z)."""

    def setUp(self):
        super().setUp()
        self.th = self.tmp / "thresholds.json"
        self.th.write_text(json.dumps(THRESHOLDS), encoding="utf-8")
        self.bw = self.tmp / "bus-writer"
        git(self.tmp, "clone", "-q", str(self.bus_origin), str(self.bw))

    def bus_commit(self, path, msg, when, branch="master"):
        if branch != "master":
            git(self.bw, "checkout", "-q", "-B", branch, "origin/master")
        commit(self.bw, msg, when, path)
        git(self.bw, "push", "-q", "origin", f"HEAD:refs/heads/{branch}")
        if branch != "master":
            git(self.bw, "checkout", "-q", "master")
        git(self.bus, "fetch", "-q", "origin", "+refs/heads/*:refs/remotes/origin/*")

    def history(self):
        self.bus_commit("cos-feedback/_heartbeat/cos.json", "cos heartbeat", "2026-10-11T12:00:00Z")  # pulse: never folds
        self.bus_commit("specs/sib.md", "sib: doctrine", "2026-10-12T12:00:00Z")                        # oldest unfolded
        self.bus_commit("specs/proj.md", "proj: own spec", "2026-10-13T12:00:00Z")                      # own: publish, no fold
        self.bus_commit("TRAPS.md", "trap filed by proj: a race", "2026-10-15T12:00:00Z")               # tagged publish
        self.bus_commit("TRAPS.md", "trap filed by projector", "2026-10-16T06:00:00Z")                  # not a proj token
        self.bus_commit("adjudications/factory-kernel/proj.dispositions.md", "harvest", "2026-10-15T00:00:00Z")
        self.bus_commit("adjudications/factory-kernel/PROJ.md", "kernel filing", "2026-10-06T12:00:00Z",
                        branch="review/proj-kernel-2026-10-06")

    def run_th(self, *extra):
        return self.run_tool("--thresholds", str(self.th), *extra)


class HealthTests(HealthFixture):
    def test_bus_side_fields(self):
        self.history()
        code, rows, err = self.run_th()
        self.assertEqual(code, 0, err)
        f = rows[0]["fields"]
        self.assertEqual(f["bus_publish"]["value"]["days_since"], 1.0)
        self.assertEqual(f["bus_publish"]["value"]["via"], "subject-tag")
        fl = f["fold_lag"]["value"]
        # sib.md + both TRAPS commits; never the heartbeat, the own spec or a dispositions file
        self.assertEqual((fl["unfolded"], fl["oldest_age_hours"]), (3, 96.0))
        self.assertEqual(f["kernel_filing"]["value"]["days_since"], 10.0)   # review branch, case-insensitive
        self.assertEqual(f["rule_coverage"]["value"], {"percent": 12.5, "floor": 10})
        h = rows[0]["health"]
        self.assertEqual(h["status"], "RED")
        self.assertEqual(len(h["reasons"]), 1)
        self.assertIn("fold lag 3 unfolded, oldest 96.0h > 72h", h["reasons"][0])

    def test_green_when_nothing_is_overdue_and_red_when_never(self):
        code, rows, _ = self.run_th()
        h = rows[0]["health"]
        self.assertEqual(code, 0)
        self.assertEqual(h["status"], "RED")      # never published, never filed: overdue, not 'fine'
        self.assertEqual(sorted(h["reasons"]), ["no attributed bus publish", "no kernel filing"])
        self.bus_commit("specs/proj/cards.md", "cards(proj)", "2026-10-16T00:00:00Z")
        self.bus_commit("adjudications/factory-kernel/proj-dogfood.md", "k", "2026-10-15T12:00:00Z", branch="review/k")
        # the cards commit is after the cursor but specs/proj/ is a doctrine surface: parity with doctrine-sync
        _, rows, _ = self.run_th()
        self.assertEqual(rows[0]["health"]["status"], "GREEN", rows[0]["health"])
        self.assertEqual(rows[0]["fields"]["bus_publish"]["value"]["via"], "own-surface")

    def test_coverage_below_own_floor_and_census_over_schedule_are_red(self):
        self.cfg["rule_coverage"]["floor"] = 20
        self.write_cfg()
        (self.bw / "metrics" / "tool-census-baseline.json").write_text(
            json.dumps({"total": 7, "roots": ["bus", "proj"], "families": {"x": {}},
                        "views": [{"name": "box", "roots": ["bus", "proj", "far"], "families": ["x"], "total": 9}],
                        "schedule": [{"by": "2026-10-01", "max": 1}, {"by": "2026-11-01", "max": 0}]}),
            encoding="utf-8")
        git(self.bw, "add", "-A")
        git(self.bw, "commit", "-q", "-m", "schedule")
        git(self.bw, "push", "-q", "origin", "HEAD:refs/heads/master")
        git(self.bus, "fetch", "-q", "origin")
        _, rows, _ = self.run_th()
        c = rows[0]["fields"]["tool_census"]["value"]
        self.assertEqual((c["schedule_max"], c["over_schedule"], c["schedule_next"]), (1, True, {"by": "2026-11-01", "max": 0}))
        # per-view counts: primary over {bus, proj} = 3 distinct - 1; 'box' needs 'far', absent here
        self.assertEqual(c["views"], [{"name": "primary", "count": 2, "baseline": 7},
                                      {"name": "box", "count": None, "baseline": 9}])
        reasons = " | ".join(rows[0]["health"]["reasons"])
        self.assertIn("rule coverage 12.5% < own floor 20%", reasons)
        self.assertIn("census primary view 2 > schedule max 1 (2 copies", reasons)

    def test_unreachable_cursor_and_missing_coverage_are_unmeasured_not_green(self):
        (self.root / ".codex-state" / "doctrine" / "last-seen.json").write_text(
            json.dumps({"lastSeen": "0" * 40, "lastSeenAt": NOW}), encoding="utf-8")
        (self.root / "cov.py").write_text("print('nothing')\n", encoding="utf-8")
        _, rows, _ = self.run_th()
        self.assertIn("UNREACHABLE", rows[0]["fields"]["fold_lag"]["error"])
        self.assertIn("fold_lag", rows[0]["health"]["unmeasured"])
        self.assertIn("coverage", rows[0]["health"]["unmeasured"])

    def test_surfaces_match_doctrine_sync(self):
        src = (HERE.parent / "doctrine-sync.mjs").read_text(encoding="utf-8")
        import re
        m = re.search(r"const BUS_SURFACES = \[([^\]]*)\]", src)
        self.assertIsNotNone(m)
        self.assertEqual(tuple(re.findall(r"'([^']+)'", m.group(1))), sc.DOCTRINE_SURFACES)

    def test_live_share_parses_one_throughput_run(self):
        fake = subprocess.CompletedProcess([], 0, json.dumps({"until_utc": "2026-10-16T12:00:00Z", "projects": [
            {"project": "airmypc", "error": None, "product_share": 0.08, "product_lines_per_week": 3412.5},
            {"project": "mlv-app", "error": "bad ref"}]}), "")
        with unittest.mock.patch.object(sc, "run_cmd", return_value=fake) as rc:
            got = sc.live_shares(sc.SCRIPT_BUS, ["airmypc", "mlv-app", "not-declared"], 14)
        argv = rc.call_args[0][0]
        self.assertIn("-WindowDays", argv)
        self.assertEqual(argv[argv.index("-Project") + 1], "airmypc,mlv-app")
        self.assertEqual(got["airmypc"]["value"]["product_share"], 0.08)
        self.assertEqual(got["airmypc"]["value"]["source"], "live")
        self.assertIn("FAILED", got["mlv-app"]["error"])
        self.assertNotIn("not-declared", got)


class FleetTests(HealthFixture):
    def fleet(self, *extra):
        roots = self.tmp / "roots.json"
        roots.write_text(json.dumps({"schema": "fleet-roots.v1", "roots": {"proj": str(self.root),
                                                                              "gone": str(self.tmp / "nope")}}), encoding="utf-8")
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = sc.main(["--fleet", "--bus", str(self.bus), "--roots", str(roots), "--thresholds", str(self.th),
                            "--share", "row", "--now", NOW, *extra])
        return code, out.getvalue(), err.getvalue()

    def setUp(self):
        super().setUp()
        for name in ("proj", "gone", "far", "fleet-x"):
            self.bus_commit(f"specs/{name}.md", f"{name}: spec", "2026-10-15T12:00:00Z")

    def test_every_member_has_a_row_absent_ones_unmeasured(self):
        code, out, err = self.fleet("--dry-run")
        self.assertEqual(code, 0, err)
        rows = [json.loads(l) for l in out.splitlines() if l.startswith("{")]
        by = {r["project"]: r for r in rows}
        self.assertEqual(sorted(by), ["far", "gone", "proj"])        # fleet-x is not a member (shared classifier)
        self.assertEqual(by["gone"]["health"]["status"], "UNMEASURED")
        self.assertEqual(by["far"]["fields"], {})
        self.assertIn(by["proj"]["health"]["status"], ("GREEN", "RED"))
        self.assertIsNotNone(by["proj"]["fields"]["tool_census"]["value"])   # bus tool ran from the checkout
        self.assertIn("<bus-checkout>", by["proj"]["fields"]["tool_census"]["cmd"])

    def test_print_table_and_dry_run_writes_nothing(self):
        out_file = self.tmp / "rows.jsonl"
        code, out, err = self.fleet("--dry-run", "--print", "--out", str(out_file), "--publish")
        self.assertEqual(code, 0, err)
        self.assertIn("project", out.splitlines()[0])
        self.assertIn("UNMEASURED (2, no local clone", out)
        self.assertFalse(out_file.exists())
        self.assertEqual(self.published(), [])

    def test_publish_sends_measured_rows_only(self):
        out_file = self.tmp / "rows.jsonl"
        code, _, err = self.fleet("--publish", "--out", str(out_file))
        self.assertEqual(code, 0, err)
        self.assertEqual([r["project"] for r in self.published()], ["proj"])
        self.assertEqual(len(out_file.read_text(encoding="utf-8").splitlines()), 3)  # the local file keeps all
        code, _, err = self.fleet("--publish")
        self.assertIn("already published", err)
        self.assertEqual(len(self.published()), 1)


class BusCiTests(Fixture):
    def bus_ci(self, runs=None, *extra):
        if runs is not None:
            self.gh_runs.write_text(json.dumps(runs), encoding="utf-8")
        code, rows, err = self.run_tool(*extra)
        self.assertEqual(code, 0, err)
        return rows[0]["fields"]["bus_ci"]

    def test_latest_conclusion_per_workflow_and_red_streak_start(self):
        f = self.bus_ci([
            gh_run("Gov", "failure", "2026-10-16T11:00:00Z", rid=9),
            gh_run("Gov", "cancelled", "2026-10-16T10:30:00Z"),          # decides nothing, never breaks a streak
            gh_run("Gov", "failure", "2026-10-16T09:00:00Z"),
            gh_run("Gov", "success", "2026-10-16T08:00:00Z"),
            gh_run("Gov", "failure", "2026-10-16T07:00:00Z"),           # before the green: not this streak
            gh_run("Sync", "", "2026-10-16T11:30:00Z", status="in_progress"),
            gh_run("Sync", "success", "2026-10-16T10:00:00Z", sha="b" * 40, rid=7),
            gh_run("Only cancelled", "cancelled", "2026-10-16T10:00:00Z"),
        ])
        v = f["value"]
        self.assertIsNone(f["error"])
        self.assertTrue(f["cmd"].startswith("gh run list -R "))
        self.assertEqual(v["workflows"]["Gov"]["conclusion"], "failure")
        self.assertEqual(v["workflows"]["Gov"]["red_since"], "2026-10-16T09:00:00Z")
        self.assertEqual(v["workflows"]["Gov"]["run_id"], 9)
        self.assertEqual(v["workflows"]["Sync"], {"conclusion": "success", "head_sha": "b" * 12, "run_id": 7,
                                                  "created_at": "2026-10-16T10:00:00Z", "red_since": None,
                                                  "in_progress": 1})
        self.assertIsNone(v["workflows"]["Only cancelled"]["conclusion"])
        self.assertEqual(v["red"], ["Gov"])
        self.assertEqual(v["red_hours"], 3.0)   # NOW 12:00 - 09:00

    def test_all_green_has_no_red_hours(self):
        v = self.bus_ci([gh_run("A", "success", "2026-10-16T11:00:00Z"),
                         gh_run("A", "failure", "2026-10-16T10:00:00Z")])["value"]
        self.assertEqual((v["red"], v["red_hours"]), ([], None))

    def test_gh_absent_or_failing_is_a_null_field_with_an_error_never_a_failure(self):
        self.gh_runs.unlink()
        f = self.bus_ci()
        self.assertIsNone(f["value"])
        self.assertTrue(f["error"].startswith("GH_FAILED: exit 1: HTTP 401"), f["error"])
        with unittest.mock.patch.object(sc, "gh_argv", return_value=None):
            f = self.bus_ci()
        self.assertIsNone(f["value"])
        self.assertTrue(f["error"].startswith("GH_UNAVAILABLE"), f["error"])
        self.gh_runs.write_text("not json", encoding="utf-8")
        f = self.bus_ci()
        self.assertEqual((f["value"], f["error"]), (None, "GH_OUTPUT_INVALID: not JSON"))

    def test_red_bus_ci_never_changes_exit_code_or_health(self):
        runs = [gh_run("Gov", "failure", "2026-10-01T00:00:00Z")]
        self.gh_runs.write_text(json.dumps(runs), encoding="utf-8")
        code, rows, err = self.run_tool()
        self.assertEqual(code, 0, err)
        self.assertEqual(rows[0]["fields"]["bus_ci"]["value"]["red"], ["Gov"])
        self.assertNotIn("bus_ci", json.dumps(rows[0].get("health", {})))

    def test_repo_from_config_then_github_origin_then_canonical(self):
        self.assertEqual(sc._github_repo("https://github.com/o/r.git"), "o/r")
        self.assertEqual(sc._github_repo("git@github.com:o/r"), "o/r")
        self.assertIsNone(sc._github_repo(str(self.bus_origin)))
        self.assertIn(f"-R {sc.BUS_REPO} ", self.bus_ci()["cmd"])    # fixture origin is a local path
        self.cfg["bus_ci"] = {"repo": "own/bus"}
        self.write_cfg()
        self.assertIn("-R own/bus ", self.bus_ci()["cmd"])

    def test_bus_ci_mode_prints_only_the_field(self):
        self.gh_runs.write_text(json.dumps([gh_run("Gov", "failure", "2026-10-16T09:00:00Z")]), encoding="utf-8")
        out = io.StringIO()
        with redirect_stdout(out):
            code = sc.main(["--bus-ci", "--bus", str(self.bus), "--now", NOW])
        self.assertEqual(code, 0)
        doc = json.loads(out.getvalue())
        self.assertEqual(set(doc), {"ts", "bus_ci"})
        self.assertEqual(doc["bus_ci"]["value"]["red_hours"], 3.0)


if __name__ == "__main__":

    unittest.main(verbosity=1)
