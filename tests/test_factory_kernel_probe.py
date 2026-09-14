"""tools/factory-kernel-probe (proposed to the fleet-factory-kernel r1 steward): shadow checks measure, never assume, and never round UNKNOWN up.

Fixtures are throwaway git repos built per test. Several tests pin findings from the kernel's own pre-landing review
(tools/factory-kernel-probe/REVIEW.md): a failing `pytest.status` counted as evidence,
K1 passing with zero readable units, delivery counted from an id pattern, and same-day records overwriting each other.
"""
import importlib.util, json, os, pathlib, re, shutil, subprocess, tempfile, unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("kernel", ROOT / "tools" / "factory-kernel-probe" / "probe.py")
kernel = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kernel)
GIT_ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")


def sh(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True, env=GIT_ENV).stdout.strip()


class Repo(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.repo = self.tmp / "r"
        self.repo.mkdir()
        sh(self.repo, "init", "-q", "-b", "master")
        self.commit({"src/a.c": "int a;"}, "product change")
        self.commit({"roadmap/plan.md": "plan"}, "governance change")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def commit(self, files, msg):
        for path, text in files.items():
            p = self.repo / path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8")
        sh(self.repo, "add", "-A"); sh(self.repo, "commit", "-q", "-m", msg)
        return sh(self.repo, "rev-parse", "HEAD")

    def ledger(self, tasks, authority="roadmap/plan.md"):
        (self.repo / "ledger.json").write_text(json.dumps({"authority": authority, "updated": "2026-09-14T00:00:00Z", "tasks": tasks}), encoding="utf-8")

    def manifest(self, **over):
        m = {"project": "fixture", "domain_class": "code", "adapter": "code", "repo": str(self.repo), "integration_ref": "master",
             "checkout": {"substrate": "git", "lock_identity": "git-common-dir"},
             "ledger": {"kind": "json-tasks", "path": "ledger.json", "list": "tasks", "authority": "authority", "updated": "updated",
                        "commit": "commit", "evidence": "evidence", "reason": "reason", "author": "author", "verifier": "verifier",
                        "delivery_evidence": "accepted",
                        "state_map": {"ready": "ELIGIBLE", "doing": "CLAIMED", "done": "ADOPTED", "blocked": "BLOCKED_EXTERNAL"},
                        "delivery": {"describe": "R* done", "id_regex": "^R\\d+$", "when_state": "ADOPTED"}},
             "admission": {"configured_min_executors": 0},
             "paths": {"product": ["src/**"], "governance": ["roadmap/**", "evidence/**", "*.md"]},
             "owner_reserved": ["release"], "owner_channel": "roadmap/plan.md",
             "liveness": {"mode": "owner-interactive", "evidence_path": "roadmap/plan.md"}, "doctrine_receipt": False}
        m.update(over)
        return m

    def receipt(self, commit, exit_status=0, author="alice", verifier="bob"):
        return json.dumps({"candidate_identity": commit, "command": "make test", "exit_status": exit_status,
                           "finished_at": "2026-09-14T00:00:00Z", "author": author, "verifier": verifier})


class SpecMatchesTool(unittest.TestCase):
    def test_spec_invariant_table_names_the_tool_invariants(self):
        text = (ROOT / "tools" / "factory-kernel-probe" / "DRAFT-universal-factory-kernel.md").read_text(encoding="utf-8")
        self.assertEqual(set(re.findall(r"^\|\s*\*\*(K\d+)\*\*\s*\|", text, re.M)), set(kernel.INVARIANTS),
                         "spec §4 table and kernel.INVARIANTS drifted")

    def test_constants_are_stated_in_the_spec(self):
        text = (ROOT / "tools" / "factory-kernel-probe" / "DRAFT-universal-factory-kernel.md").read_text(encoding="utf-8")
        for k, v in {**kernel.PROMOTION, **kernel.DEMOTION}.items():
            self.assertIn(str(v), text, f"constant {k}={v} not stated in the spec")
        for c in kernel.DOMAIN_CLASSES:
            self.assertIn(f"`{c}`", text, f"domain class {c} missing from spec §5")


class Invariants(Repo):
    def test_k1_never_assumes_master_and_never_passes_on_zero_units(self):
        self.ledger([])
        self.assertEqual(kernel.check(self.manifest(integration_ref=None))["invariants"]["K1"]["status"], "FAIL")
        self.assertEqual(kernel.check(self.manifest(integration_ref="nope"))["invariants"]["K1"]["status"], "FAIL")
        self.assertEqual(kernel.check(self.manifest(ledger={"kind": "none"}))["invariants"]["K1"]["status"], "UNKNOWN")

    def test_k1_adopted_commit_must_be_reachable(self):
        sh(self.repo, "checkout", "-q", "-b", "side")
        side = self.commit({"src/b.c": "int b;"}, "side work")
        sh(self.repo, "checkout", "-q", "master")
        self.ledger([{"id": "U1", "status": "done", "commit": side, "evidence": ["src/a.c"]}])
        k1 = kernel.check(self.manifest())["invariants"]["K1"]
        self.assertEqual((k1["status"], k1["unreachable"]), ("FAIL", ["U1"]))

    def test_k2_other_substrates_declare_identity(self):
        self.ledger([])
        m = self.manifest(checkout={"substrate": "perforce", "lock_identity": "depot://game"})
        self.assertEqual(kernel.check(m)["invariants"]["K2"]["status"], "PASS")
        m = self.manifest(checkout={"substrate": "perforce"})
        self.assertEqual(kernel.check(m)["invariants"]["K2"]["status"], "UNKNOWN")

    def test_k3_zero_eligible_with_an_admission_floor_fails(self):
        self.ledger([{"id": "U1", "status": "blocked", "reason": "owner"}])
        self.assertEqual(kernel.check(self.manifest(admission={"configured_min_executors": 5}))["invariants"]["K3"]["status"], "FAIL")
        self.assertEqual(kernel.check(self.manifest(admission={}))["invariants"]["K3"]["status"], "UNKNOWN")
        probe = {"configured_min_executors": 0, "observed_executors_argv": ["python", "-c", "print(3)"]}
        self.assertEqual(kernel.check(self.manifest(admission=probe))["invariants"]["K3"]["status"], "FAIL",
                         "observed executors with nothing eligible must fail even when the declared floor is 0")

    def test_k5_existence_is_not_execution(self):
        head = self.commit({"evidence/u1/pytest.status": "1", "evidence/u1/log.txt": "failed"}, "evidence")
        self.ledger([{"id": "U1", "status": "done", "commit": head, "evidence": ["evidence/u1/"], "author": "alice", "verifier": "bob"}])
        k5 = kernel.check(self.manifest())["invariants"]["K5"]
        self.assertEqual(k5["status"], "WARN", "a failing status file in an existing evidence dir must never PASS")
        self.assertTrue(k5["failing_status"] and k5["unreceipted"] == ["U1"])

    def test_k5_passing_receipt_passes_and_failing_or_self_verified_does_not(self):
        work = self.commit({"src/c.c": "int c;"}, "work")
        self.commit({"evidence/u1/run.receipt.json": self.receipt(work)}, "receipt")
        self.ledger([{"id": "U1", "status": "done", "commit": work, "evidence": ["evidence/u1/"], "author": "alice", "verifier": "bob"}])
        self.assertEqual(kernel.check(self.manifest())["invariants"]["K5"]["status"], "PASS")
        self.commit({"evidence/u1/run.receipt.json": self.receipt(work, exit_status=2)}, "failing receipt")
        self.assertEqual(kernel.check(self.manifest())["invariants"]["K5"]["status"], "WARN")
        self.commit({"evidence/u1/run.receipt.json": self.receipt(work, verifier="alice")}, "self-verified receipt")
        self.assertEqual(kernel.check(self.manifest())["invariants"]["K5"]["status"], "WARN")
        self.ledger([{"id": "U1", "status": "done", "commit": work, "evidence": ["evidence/u1/"], "author": "alice", "verifier": "Alice"}])
        self.assertEqual(kernel.check(self.manifest())["invariants"]["K5"]["status"], "FAIL", "ledger author == verifier")

    def test_k5_missing_or_absent_evidence_fails(self):
        head = self.commit({"src/c.c": "int c;"}, "work")
        self.ledger([{"id": "U1", "status": "done", "commit": head, "evidence": ["evidence/none/"]},
                     {"id": "U2", "status": "done", "commit": head, "evidence": []}])
        k5 = kernel.check(self.manifest())["invariants"]["K5"]
        self.assertEqual((k5["status"], k5["no_evidence"]), ("FAIL", ["U2"]))

    def test_k6_delivery_needs_delivery_evidence(self):
        head = self.commit({"src/d.c": "int d;"}, "work")
        self.ledger([{"id": "B1", "status": "done", "commit": head, "evidence": ["src/d.c"]},
                     {"id": "R1", "status": "done", "commit": head, "evidence": ["src/d.c"]}])
        r = kernel.check(self.manifest())
        self.assertEqual(r["invariants"]["K6"]["status"], "FAIL", "an id pattern reaching done is not delivery")
        self.assertEqual(r["metrics"]["delivered"], 0)
        self.ledger([{"id": "R1", "status": "done", "commit": head, "evidence": ["src/d.c"], "accepted": "owner 2026-09-14"}])
        r = kernel.check(self.manifest())
        self.assertEqual((r["invariants"]["K6"]["status"], r["metrics"]["delivered"]), ("PASS", 1))
        m = self.manifest(); del m["ledger"]["delivery_evidence"]
        self.ledger([{"id": "R1", "status": "blocked", "reason": "owner"}])
        self.assertEqual(kernel.check(m)["invariants"]["K6"]["status"], "WARN")
        del m["ledger"]["delivery"]
        self.assertEqual(kernel.check(m)["invariants"]["K6"]["status"], "FAIL")

    def test_k7_zero_product_motion_raises_the_alarm(self):
        for i in range(3):
            self.commit({f"roadmap/n{i}.md": str(i)}, "governance")
        self.commit({"src/x.c": "x"}, "one product commit")
        self.ledger([])
        k7 = kernel.check(self.manifest(paths={"product": ["src/**"], "governance": ["roadmap/**"], "alarm_ratio": 0.9}))["invariants"]["K7"]
        self.assertEqual(k7["status"], "PASS")
        k7 = kernel.check(self.manifest(paths={"product": ["nothing/**"], "governance": ["roadmap/**", "src/**"]}))["invariants"]["K7"]
        self.assertEqual(k7["status"], "WARN"); self.assertIn("CONFORMANCE-FIXPOINT ALARM", k7["evidence"])

    def test_k10_owner_channel_required_even_with_nothing_blocked(self):
        self.ledger([])
        self.assertEqual(kernel.check(self.manifest(owner_channel="missing.md"))["invariants"]["K10"]["status"], "FAIL")
        self.ledger([{"id": "U1", "status": "blocked"}])
        self.assertEqual(kernel.check(self.manifest())["invariants"]["K10"]["status"], "FAIL")

    def test_k11_owner_interactive_needs_recent_evidence(self):
        self.ledger([])
        self.assertEqual(kernel.check(self.manifest())["invariants"]["K11"]["status"], "PASS")
        stale = self.manifest(liveness={"mode": "owner-interactive"})
        self.assertEqual(kernel.check(stale)["invariants"]["K11"]["status"], "WARN", "a declaration alone self-certifies nothing")
        probes = self.manifest(liveness={"mode": "scheduled", "probes": [{"argv": ["python", "-c", "print('Disabled')"], "ok": ["Ready"]},
                                                                        {"argv": ["python", "-c", "print('Ready')"], "ok": ["Ready"]}]})
        self.assertEqual(kernel.check(probes)["invariants"]["K11"]["status"], "PASS", "any live declared floor passes")

    def test_no_ledger_is_unknown_never_pass(self):
        r = kernel.check(self.manifest(ledger={"kind": "none"}))
        for k in ("K1", "K3", "K4", "K5", "K6", "K10"):
            self.assertEqual(r["invariants"][k]["status"], "UNKNOWN", k)

    def test_command_ledger_contract(self):
        head = self.commit({"src/e.c": "int e;"}, "work")
        script = self.tmp / "ledger.py"
        script.write_text("import json;print(json.dumps({'units':[{'id':'U1','state':'ADOPTED','commit':'%s','evidence':['src/e.c']},"
                          "{'id':'U2','state':'SOMETHING'}],'meta':{'authority':'roadmap/plan.md'}}))" % head, encoding="utf-8")
        r = kernel.check(self.manifest(ledger={"kind": "command", "argv": ["python", str(script)]}))
        self.assertEqual(r["invariants"]["K1"]["status"], "PASS"); self.assertEqual(r["unmapped_native_states"], ["SOMETHING"])
        bad = kernel.check(self.manifest(ledger={"kind": "command", "argv": ["python", "-c", "print('not json')"]}))
        self.assertEqual(bad["invariants"]["K5"]["status"], "UNKNOWN")

    def test_glob_classification(self):
        rx = [kernel.glob_to_regex(g) for g in ("src/**", "*.md", "Claude - */**")]
        self.assertTrue(kernel.classify("src/a/b.c", rx)); self.assertTrue(kernel.classify("README.md", rx))
        self.assertFalse(kernel.classify("docs/README.md", rx[1:2]), "*.md is top-level only")
        self.assertTrue(kernel.classify("Claude - Plans/x.md", rx))


class FeedbackAndHarvest(Repo):
    def record(self, bus, project, when, domain="code", status="PASS"):
        d = bus / "feedback" / "factory-kernel" / project
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{when}-abc.json").write_text(json.dumps({
            "kernel_version": kernel.KERNEL_VERSION, "project": project, "domain_class": domain, "metrics": {}, "tally": {},
            "measured_at": f"{when}T00:00:00+00:00", "invariants": {k: {"status": status} for k in kernel.INVARIANTS}}))

    def test_feedback_path_is_single_writer_and_never_overwrites(self):
        self.ledger([])
        bus = self.tmp / "bus"
        out, r = kernel.feedback(self.manifest(), bus, None, 14)
        self.assertEqual(out.parent, bus / "feedback" / "factory-kernel" / "fixture")
        self.assertRegex(out.name, r"^\d{4}-\d{2}-\d{2}T\d{6}Z-[0-9a-f]{12}\.json$")
        with self.assertRaises(SystemExit):
            out.write_text(out.read_text()); kernel.feedback.__globals__["check"] = lambda m, w: r
            try:
                kernel.feedback(self.manifest(), bus, None, 14)
            finally:
                kernel.feedback.__globals__["check"] = kernel.check

    def test_harvest_is_derived_and_withholds_promotion_without_a_landed_amendment(self):
        bus = self.tmp / "bus"; sh_bus = bus
        bus.mkdir(); sh(bus, "init", "-q", "-b", "master")
        for i, (p, dom) in enumerate([("a", "code"), ("b", "firmware"), ("c", "strategy"), ("d", "code"), ("e", "mobile")]):
            self.record(bus, p, "2026-08-30", dom); self.record(bus, p, "2026-09-14", dom)
        text, crit = kernel.harvest(bus)
        self.assertFalse((bus / "feedback" / "factory-kernel" / "SUMMARY.md").exists(), "harvest output is never a committed file")
        self.assertFalse(crit[">= 1 amendment LANDED with a landing_commit reachable from the bus"])
        self.assertIn("NOT YET", text)
        prop = bus / "feedback" / "factory-kernel" / "proposals"; prop.mkdir(parents=True)
        (prop / "2026-09-14-x.md").write_text("status: LANDED\nlanding_commit: deadbeef\n")
        self.assertFalse(kernel.harvest(bus)[1][">= 1 amendment LANDED with a landing_commit reachable from the bus"],
                         "a landing commit that is not on the bus does not count")
        sh(bus, "add", "-A"); sh(bus, "commit", "-q", "-m", "records")
        (prop / "2026-09-14-x.md").write_text(f"status: LANDED\nlanding_commit: {sh(bus, 'rev-parse', 'HEAD')}\n")
        text, crit = kernel.harvest(bus)
        self.assertTrue(all(crit.values()), crit)
        self.assertIn("ELIGIBLE for owner ratification", text)

    def test_harvest_flags_demotion_and_coverage(self):
        bus = self.tmp / "bus"; bus.mkdir()
        for p in ("a", "b", "c"):
            self.record(bus, p, "2026-08-30", status="FAIL"); self.record(bus, p, "2026-09-14", status="FAIL")
        text, crit = kernel.harvest(bus)
        self.assertFalse(crit["no invariant due for demotion"]); self.assertIn("Due for demotion (§8): ['K1'", text)
        bus2 = self.tmp / "bus2"; bus2.mkdir()
        self.record(bus2, "a", "2026-09-14", status="UNKNOWN"); self.record(bus2, "b", "2026-09-14", status="PASS")
        crit = kernel.harvest(bus2)[1]
        self.assertFalse(crit["every invariant measured on >= 0.8 of projects and on >= 1 project per domain"])
        bus3 = self.tmp / "bus3"; bus3.mkdir()
        self.record(bus3, "a", "2026-09-14", domain="code", status="PASS"); self.record(bus3, "bus", "2026-09-14", domain="strategy", status="N/A")
        self.assertTrue(kernel.harvest(bus3)[1]["every invariant measured on >= 0.8 of projects and on >= 1 project per domain"],
                        "an invariant that does not apply to a project must not count against coverage")


if __name__ == "__main__":
    unittest.main()
