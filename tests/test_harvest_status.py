"""harvest-status.py against a real origin + clone, so the git plumbing is what is tested."""
import importlib.util, pathlib, subprocess, tempfile, unittest

TOOL = pathlib.Path(__file__).resolve().parent.parent / "tools" / "harvest-status.py"
spec = importlib.util.spec_from_file_location("harvest_status", TOOL)
hs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hs)

FILING_V1 = "project: bench-a\nproviders: claude-only\n\n§1 | \"q\" | d | REPLACES: \"a\" -> \"b\" | PROOF: p\n"
FILING_V2 = ("project: bench-a\nproviders: claude(opus) codex(sol)\nposture: conjugal-standard\n\n"
             "§1 | \"q\" | d | REPLACES: \"a\" -> \"b\" | PROOF: p\n§2 | \"q\" | d | REPLACES: \"c\" -> \"d\" | PROOF: p\n"
             "## Untested\n§3 | \"q\" | d | REPLACES: \"e\" -> \"f\" | PROOF: p\n")


def run(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


class HarvestStatus(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(self.tmp.name)
        self.origin, self.work, self.clone = root / "origin.git", root / "work", root / "clone"
        run(root, "init", "--bare", "-b", "master", str(self.origin))
        run(root, "clone", str(self.origin), str(self.work))
        for k, v in (("user.name", "t"), ("user.email", "t@t"), ("commit.gpgsign", "false")):
            run(self.work, "config", k, v)
        self.subj = self.work / "adjudications" / "demo"
        self.subj.mkdir(parents=True)
        (self.subj / "README.md").write_text("Subject: `specs/owner-demo.md`.\n", encoding="utf-8")
        (self.subj / "bench-a.md").write_text(FILING_V1, encoding="utf-8")
        self.commit("filing v1", "--date=2026-09-13T10:00:00", env_date="2026-09-13T10:00:00")
        run(self.work, "push", "-q", "origin", "HEAD:master")
        run(self.work, "checkout", "-q", "-b", "review/bench-a")
        (self.subj / "bench-a.md").write_text(FILING_V2, encoding="utf-8")
        self.commit("filing v2", "--date=2026-09-13T12:00:00", env_date="2026-09-13T12:00:00")
        run(self.work, "push", "-q", "origin", "review/bench-a")
        run(self.work, "checkout", "-q", "master")
        run(root, "clone", "-q", str(self.origin), str(self.clone))

    def commit(self, msg, *extra, env_date=None):
        import os
        env = {**os.environ}
        if env_date:
            env["GIT_COMMITTER_DATE"] = env_date
        run(self.work, "add", "-A")
        subprocess.run(["git", "commit", "-q", "-m", msg, *extra], cwd=self.work, check=True, env=env)

    def tearDown(self):
        self.tmp.cleanup()

    def status(self):
        hs.git(self.clone, "fetch", "-q", "origin", "+refs/heads/master:refs/remotes/origin/master",
               "+refs/heads/review/*:refs/remotes/origin/review/*")
        return hs.subject_status(self.clone, "demo")

    def test_review_branch_copy_is_current_and_unharvested(self):
        r = self.status()
        self.assertEqual(r["spec"], "specs/owner-demo.md")
        [f] = r["filings"]
        self.assertEqual(f["status"], "UNHARVESTED")
        self.assertEqual(f["ref"], "origin/review/bench-a")
        self.assertEqual((f["findings"], f["untested"]), (2, 1))
        self.assertIn("POSTURE-NOT-R9-COMPUTED", f["flags"])
        self.assertEqual(len(f["superseded"]), 1)

    def test_dispositions_for_current_blob_harvest_it_and_older_blob_is_stale(self):
        current = self.status()["filings"][0]["blob"]
        (self.subj / "bench-a.dispositions.md").write_text(f"filing_blob: {current}\n", encoding="utf-8")
        self.commit("disp")
        run(self.work, "push", "-q", "origin", "HEAD:master")
        self.assertEqual(self.status()["filings"][0]["status"], "HARVESTED")
        (self.subj / "bench-a.dispositions.md").write_text("filing_blob: 0000000000\n", encoding="utf-8")
        self.commit("stale disp")
        run(self.work, "push", "-q", "origin", "HEAD:master")
        self.assertEqual(self.status()["filings"][0]["status"], "STALE")

    def test_exit_codes(self):
        base = ["demo", "--repo", str(self.clone)]
        self.assertEqual(hs.main(base), 1)
        self.assertEqual(hs.main(["demo", "--repo", str(self.tmp.name)]), 2)

    def test_r9_posture_forms_are_not_flagged(self):
        for p in ("conjugal-standard COMPLETE (17/17 lanes)", "conjugal-standard-PARTIAL (5/17 lanes; missing: panel 0/8)"):
            _, _, _, flags = hs.parse_filing(f"project: x\nproviders: y\nposture: {p}\n")
            self.assertEqual(flags, [], p)


if __name__ == "__main__":
    unittest.main()
