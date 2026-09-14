"""kernel-convergence.py against a real origin + clone, so the git plumbing is what is tested."""
import importlib.util, io, json, pathlib, subprocess, tempfile, unittest
from contextlib import redirect_stdout

TOOL = pathlib.Path(__file__).resolve().parent.parent / "tools" / "kernel-convergence.py"
spec = importlib.util.spec_from_file_location("kernel_convergence", TOOL)
kc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kc)

CANDIDATE = "# kernel\n\n## 2. Clauses\n\n### UFK-1 — one\ntext\n\n### UFK-2 — two\ntext\n\n## 3. After\n"
SUBJ = "adjudications/universal-factory-kernel"
PROJECTS = ("a", "b", "c", "d", "w")
BOTH_ADOPT = [(1, "ADOPT", "x -> ok"), (2, "ADOPT", "y -> ok")]


def filing(project, classes, rows, author="no", revision="r1"):
    head = (f"project: {project}\ndomain: d\nadapter_class: {classes}\nkernel_revision: {revision}\n"
            f"author_of_candidate: {author}\nproviders: claude-only\nseats: haiku reviewer\n\n")
    body = "".join(f"UFK-{n} | {d} | mech | PROOF: {p}\n" for n, d, p in rows)
    return head + body + "\n## Adapter\nartifact: app | class: x | executed_by: ci | evidence_identity: commit\n"


def run(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


class KernelConvergence(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(self.tmp.name)
        self.origin, self.work, self.clone = root / "origin.git", root / "work", root / "clone"
        run(root, "init", "--bare", "-b", "master", str(self.origin))
        run(root, "clone", str(self.origin), str(self.work))
        for k, v in (("user.name", "t"), ("user.email", "t@t"), ("commit.gpgsign", "false")):
            run(self.work, "config", k, v)
        self.write("ruling-candidates/universal-factory-kernel-r1.md", CANDIDATE)
        self.write(f"{SUBJ}/README.md", "Subject: `ruling-candidates/universal-factory-kernel-r1.md`.\n")
        self.write("bootstrap/PROMPT-K-dogfood-kernel.md", "prompt\n")
        for p in PROJECTS:
            self.write(f"specs/{p}.md", f"# {p}\n")
        self.commit_push("candidate", "master")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel, text):
        p = self.work / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline="\n")

    def commit_push(self, msg, branch):
        run(self.work, "add", "-A")
        run(self.work, "commit", "-q", "-m", msg)
        run(self.work, "push", "-q", "origin", f"HEAD:{branch}")

    def measure(self, *extra):
        if not self.clone.exists():
            run(self.work.parent, "clone", "-q", str(self.origin), str(self.clone))
        run(self.clone, "fetch", "-q", "origin", "+refs/heads/master:refs/remotes/origin/master",
            "+refs/heads/review/*:refs/remotes/origin/review/*")
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = kc.main(["--repo", str(self.clone), "--no-fetch", "--json", *extra])
        return code, json.loads(buf.getvalue())

    def clause(self, result, cid):
        return next(c for c in result["clauses"] if c["id"] == cid)

    def blob(self, rel):
        return run(self.work, "rev-parse", f"HEAD:{rel}").strip()

    def test_two_nonauthor_adopters_in_two_classes_are_eligible(self):
        self.write(f"{SUBJ}/a.md", filing("a", "deterministic", BOTH_ADOPT))
        self.commit_push("a", "review/a-2026-09-14")
        run(self.work, "checkout", "-q", "-b", "review/b-2026-09-14", "master")
        self.write(f"{SUBJ}/b.md", filing("b", "attended", [(1, "ADOPT-WITH-CHANGE", "x -> ok"), (2, "UNMEASURED", "")]))
        self.commit_push("b", "review/b-2026-09-14")
        code, r = self.measure()
        self.assertEqual(code, 0)
        self.assertTrue(self.clause(r, "UFK-1")["eligible"])
        self.assertFalse(self.clause(r, "UFK-2")["eligible"], "UNMEASURED must count for nothing")
        self.assertFalse(r["universal"])

    def test_same_class_author_and_unproved_are_not_eligible(self):
        self.write(f"{SUBJ}/a.md", filing("a", "deterministic", [(1, "ADOPT", "x -> ok")]))
        self.write(f"{SUBJ}/b.md", filing("b", "deterministic", [(1, "ADOPT", "x -> ok")]))
        self.write(f"{SUBJ}/c.md", filing("c", "attended", [(1, "ADOPT", "x -> ok")], author="yes"))
        self.write(f"{SUBJ}/d.md", filing("d", "statistical", [(1, "ADOPT", "ran it")]))
        self.commit_push("filings", "master")
        _, r = self.measure()
        c1 = self.clause(r, "UFK-1")
        self.assertEqual(c1["adopters"], ["a", "b"])
        self.assertFalse(c1["eligible"], "one class, an author filing and PROOF without '->' must not qualify")

    def test_one_project_with_many_classes_cannot_supply_both_classes(self):
        self.write(f"{SUBJ}/a.md", filing("a", "deterministic, judgment", [(1, "ADOPT", "x -> ok")]))
        self.write(f"{SUBJ}/b.md", filing("b", "deterministic", [(1, "ADOPT", "x -> ok")]))
        self.commit_push("filings", "master")
        _, r = self.measure()
        self.assertTrue(self.clause(r, "UFK-1")["eligible"], "a can contribute judgment while b contributes deterministic")
        self.write(f"{SUBJ}/b.md", filing("b", "deterministic, judgment", [(1, "ADOPT", "x -> ok")]))
        self.write(f"{SUBJ}/a.md", filing("a", "deterministic", [(1, "UNMEASURED", "")]))
        self.write(f"{SUBJ}/c.md", filing("c", "attended", [(1, "UNMEASURED", "")]))
        self.commit_push("only b adopts", "master")
        _, r = self.measure()
        self.assertFalse(self.clause(r, "UFK-1")["eligible"], "a single multi-class project is not two projects")

    def test_stem_mismatch_unknown_project_and_stale_revision_are_ignored(self):
        self.write(f"{SUBJ}/a.md", filing("ghost-a", "deterministic, judgment", BOTH_ADOPT))
        self.write(f"{SUBJ}/ghost-b.md", filing("ghost-b", "statistical", BOTH_ADOPT))
        self.write(f"{SUBJ}/c.md", filing("c", "attended", BOTH_ADOPT, revision="r0"))
        self.commit_push("gaming attempts", "master")
        _, r = self.measure()
        reasons = {i["name"]: i["reason"] for i in r["ignored"]}
        self.assertIn("filename stem", reasons["a"])
        self.assertIn("unknown project", reasons["ghost-b"])
        self.assertIn("kernel_revision", reasons["c"])
        self.assertEqual(r["filings"], [])
        self.assertFalse(any(c["eligible"] for c in r["clauses"]))
        self.assertFalse(r["universal"])

    def test_receipts_heading_on_filing_ref_makes_a_new_project_known(self):
        self.write(f"{SUBJ}/a.md", filing("a", "deterministic", BOTH_ADOPT))
        self.commit_push("a", "master")
        run(self.work, "checkout", "-q", "-b", "review/novel-2026-09-15", "master")
        self.write(f"{SUBJ}/novel.md", filing("novel", "judgment", BOTH_ADOPT))
        self.write("RECEIPTS.md", "## Kernel dogfood: novel (novel, 2026-09-15, laptop)\n")
        self.commit_push("novel", "review/novel-2026-09-15")
        _, r = self.measure()
        self.assertEqual(r["ignored"], [])
        self.assertTrue(r["universal"], "two classes on both clauses plus a judgment adopter")

    def test_reject_blocks_until_a_dispositions_file_answers_that_clause(self):
        self.write(f"{SUBJ}/a.md", filing("a", "deterministic", [(1, "ADOPT", "x -> ok")]))
        self.write(f"{SUBJ}/b.md", filing("b", "statistical", [(1, "ADOPT", "x -> ok")]))
        self.write(f"{SUBJ}/c.md", filing("c", "judgment", [(1, "REJECT", "x -> harm")]))
        self.commit_push("filings", "master")
        _, r = self.measure()
        self.assertEqual(self.clause(r, "UFK-1")["unanswered_rejects"], ["c"])
        self.assertFalse(self.clause(r, "UFK-1")["eligible"])
        blob = self.blob(f"{SUBJ}/c.md")
        self.write(f"{SUBJ}/c.dispositions.md", f"filing_blob: {blob}\nspec_commit: x\n")
        self.commit_push("empty dispositions", "master")
        _, r = self.measure()
        self.assertFalse(self.clause(r, "UFK-1")["eligible"], "a dispositions file with no answer line must not unblock")
        self.write(f"{SUBJ}/a.dispositions.md", f"filing_blob: {blob}\nspec_commit: x\nUFK-1 | REJECTED | reason\n")
        self.commit_push("answer filed under the wrong stem", "master")
        _, r = self.measure()
        self.assertFalse(self.clause(r, "UFK-1")["eligible"], "another filing's dispositions must not answer c")
        self.write(f"{SUBJ}/c.dispositions.md", f"filing_blob: {blob}\nspec_commit: x\nUFK-1 | REJECTED | reason\n")
        self.commit_push("answered", "master")
        _, r = self.measure()
        self.assertTrue(self.clause(r, "UFK-1")["eligible"])

    def test_divergence_in_two_classes_forces_amend_and_blocks_eligibility(self):
        self.write(f"{SUBJ}/a.md", filing("a", "deterministic", [(1, "ADOPT", "x -> ok")]))
        self.write(f"{SUBJ}/b.md", filing("b", "statistical", [(1, "ADOPT", "x -> ok")]))
        self.write(f"{SUBJ}/c.md", filing("c", "judgment", [(1, "DISTINGUISH", "x -> n/a")]))
        self.write(f"{SUBJ}/d.md", filing("d", "attended", [(1, "DISTINGUISH", "x -> n/a")]))
        self.commit_push("filings", "master")
        _, r = self.measure()
        c1 = self.clause(r, "UFK-1")
        self.assertTrue(c1["must_amend"])
        self.assertFalse(c1["eligible"], "a clause that must be amended is not eligible")

    def test_filing_without_seats_or_adapter_is_ignored(self):
        self.write(f"{SUBJ}/a.md", filing("a", "deterministic", BOTH_ADOPT).replace("seats: haiku reviewer\n", ""))
        self.write(f"{SUBJ}/b.md", filing("b", "attended", BOTH_ADOPT).split("## Adapter")[0])
        self.commit_push("bare filings", "master")
        _, r = self.measure()
        self.assertEqual(sorted(i["name"] for i in r["ignored"]), ["a", "b"])

    def test_ignored_filings_do_not_make_harvest_due(self):
        for p in ("a", "b", "c"):
            self.write(f"{SUBJ}/{p}.md", filing(p, "attended", BOTH_ADOPT, revision="r0"))
        self.commit_push("stale filings", "master")
        _, r = self.measure()
        self.assertFalse(r["harvest"]["due"])

    def test_missing_companion_is_a_tool_error(self):
        run(self.work, "rm", "-q", "bootstrap/PROMPT-K-dogfood-kernel.md")
        self.commit_push("drop prompt", "master")
        run(self.work.parent, "clone", "-q", str(self.origin), str(self.clone))
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = kc.main(["--repo", str(self.clone), "--no-fetch", "--json"])
        self.assertEqual(code, 2)

    def test_harvest_due_by_count_and_by_clock(self):
        self.write(f"{SUBJ}/a.md", filing("a", "deterministic", BOTH_ADOPT))
        self.commit_push("one filing", "master")
        _, r = self.measure("--now", "2099-01-01T00:00:00+00:00")
        self.assertTrue(r["harvest"]["due"], "one open filing and a stale clock")
        _, r = self.measure()
        self.assertFalse(r["harvest"]["due"], "one open filing, fresh clock")
        for p in ("b", "c"):
            self.write(f"{SUBJ}/{p}.md", filing(p, "attended", BOTH_ADOPT))
        self.commit_push("three filings", "master")
        _, r = self.measure()
        self.assertTrue(r["harvest"]["due"])

    def test_over_budget_counts_companions_and_exits_1(self):
        big = "# k\n\n## 2. Clauses\n\n" + "".join(f"### UFK-{i} — c\nx\n\n" for i in range(1, 10))
        self.write("ruling-candidates/universal-factory-kernel-r2.md", big)
        self.commit_push("r2", "master")
        code, r = self.measure()
        self.assertEqual(r["candidate"], "ruling-candidates/universal-factory-kernel-r2.md")
        self.assertEqual(code, 1)
        self.assertTrue(any("clauses 9 > 8" in o for o in r["over_budget"]))
        self.write("bootstrap/PROMPT-K-dogfood-kernel.md", "x\n" * 500)
        self.write("ruling-candidates/universal-factory-kernel-r2.md", CANDIDATE)
        self.commit_push("companion bloat", "master")
        code, r = self.measure()
        self.assertEqual(code, 1)
        self.assertTrue(any(o.startswith("normative") for o in r["over_budget"]))
        self.write(f"{SUBJ}/a.md", filing("a", "deterministic", BOTH_ADOPT, revision="r2"))
        self.write(f"{SUBJ}/b.md", filing("b", "attended", BOTH_ADOPT, revision="r2"))
        self.commit_push("adopters while over budget", "master")
        _, r = self.measure()
        self.assertEqual([f["name"] for f in r["filings"]], ["a", "b"], "both filings must count for this pin to bite")
        self.assertFalse(any(c["eligible"] for c in r["clauses"]), "over budget: nothing is eligible")


if __name__ == "__main__":
    unittest.main()
