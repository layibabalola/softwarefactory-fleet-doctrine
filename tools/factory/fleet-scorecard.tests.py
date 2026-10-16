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
    print(json.dumps({"total": 5, "measuredRoots": ["bus", "proj"], "absentRoots": ["far"], "families": [
        {"name": "x", "copies": [{"root": "proj", "path": "a.py"}, {"root": "bus", "path": "b.py", "canonical": True},
                                 {"root": "proj", "path": "c.py"}, {"root": "other", "path": "d.py"}]}]}))
elif tool == "check-rule-tags":
    assert "--report" in a and "--json" in a
    print(json.dumps({"project": "proj", "counts": {"bullets": 5, "backed": 2, "prose": 3, "untagged": 0,
                                                   "dangling": 0, "mixed": 0}}))
elif tool == "check-evidence-dumps":
    print(json.dumps({"violations": 4}))
else:
    sys.exit(2)
'''


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
        (seed / "tools" / "tool-census.config.json").write_text("{}", encoding="utf-8")
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
        (st / "last-seen.json").write_text(json.dumps({"lastSeenAt": "2026-10-16T06:00:00Z"}), encoding="utf-8")
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


if __name__ == "__main__":

    unittest.main(verbosity=1)
