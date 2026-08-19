import copy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "check_phase5_stale_reconciliation.py"
SPEC = importlib.util.spec_from_file_location("check_phase5_stale_reconciliation", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class Phase5StaleReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = MODULE.load_json(
            (ROOT / MODULE.INTAKE_PATH).read_bytes()
        )

    def _copy(self):
        return copy.deepcopy(self.batch)

    def _project(self, batch, project_id):
        return next(project for project in batch["projects"] if project["projectId"] == project_id)

    def test_published_batch_passes_local_verification(self):
        MODULE.verify_batch(self._copy(), "HEAD")

    def test_duplicate_json_key_fails_closed(self):
        with self.assertRaisesRegex(MODULE.Phase5Error, "DUPLICATE_KEY"):
            MODULE.load_json(b'{"schema":"one","schema":"two"}')

    def test_frozen_base_cannot_move(self):
        batch = self._copy()
        batch["frozenBase"]["publishedMasterCommit"] = "0" * 40
        with self.assertRaisesRegex(MODULE.Phase5Error, "FROZEN_BASE_MISMATCH"):
            MODULE.verify_batch(batch, "HEAD")

    def test_adobe_reachability_cannot_be_converted_to_disposition(self):
        batch = self._copy()
        adobe = self._project(batch, "adobe-ingester")
        adobe["outcome"]["status"] = "DISTINGUISH"
        adobe["outcome"]["advanceAuthorized"] = True
        with self.assertRaisesRegex(MODULE.Phase5Error, "OUTCOME_OVERCLAIM"):
            MODULE.verify_batch(batch, "HEAD")

    def test_adobe_remote_and_ref_are_exact(self):
        for mutation in ("remote", "commit", "marker"):
            with self.subTest(mutation=mutation):
                batch = self._copy()
                discovery = self._project(batch, "adobe-ingester")["discovery"]
                if mutation == "remote":
                    discovery["remote"] = "https://example.invalid/adobe.git"
                elif mutation == "commit":
                    discovery["refs"][0]["commit"] = "0" * 40
                else:
                    discovery["r26MarkerSearch"]["matchingPaths"] = ["fabricated-r26.json"]
                with self.assertRaisesRegex(MODULE.Phase5Error, "ADOBE_DISCOVERY_MISMATCH"):
                    MODULE.verify_batch(batch, "HEAD")

    def test_adobe_workflow_evidence_is_exact_and_zero_authority(self):
        batch = self._copy()
        adobe = self._project(batch, "adobe-ingester")
        adobe["discovery"]["workflowEvidence"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(MODULE.Phase5Error, "ADOBE_DISCOVERY_MISMATCH"):
            MODULE.verify_batch(batch, "HEAD")

    def test_negative_discovery_is_not_global_nonexistence_proof(self):
        for project_id in ("agent-bridge", "airmypc", "conjugal"):
            with self.subTest(project_id=project_id):
                batch = self._copy()
                discovery = self._project(batch, project_id)["discovery"]
                discovery["remote"] = "https://example.invalid/invented.git"
                with self.assertRaisesRegex(MODULE.Phase5Error, "NEGATIVE_DISCOVERY_OVERCLAIM"):
                    MODULE.verify_batch(batch, "HEAD")

    def test_any_authority_claim_fails_closed(self):
        for project_id in sorted(MODULE.PROJECT_IDS):
            with self.subTest(project_id=project_id):
                batch = self._copy()
                self._project(batch, project_id)["authority"]["provider"] = True
                with self.assertRaisesRegex(MODULE.Phase5Error, "AUTHORITY_OVERCLAIM"):
                    MODULE.verify_batch(batch, "HEAD")

    def test_summary_cannot_claim_adoption_or_status_advance(self):
        for field in (
            "currentR26Dispositions", "adoptionClaims", "runtimeAuthorityClaims",
            "projectMutationClaims",
        ):
            with self.subTest(field=field):
                batch = self._copy()
                batch["summary"][field] = 1
                with self.assertRaisesRegex(MODULE.Phase5Error, "SUMMARY_OVERCLAIM"):
                    MODULE.verify_batch(batch, "HEAD")

    def test_phase5_scope_rejects_product_or_spec_mutation(self):
        with mock.patch.object(MODULE, "_changed_paths", return_value={"specs/adobe-ingester.md"}):
            with self.assertRaisesRegex(MODULE.Phase5Error, "PHASE5_SCOPE_VIOLATION"):
                MODULE.verify_batch(self._copy(), "HEAD")

    def test_phase5_scope_allows_exact_utilization_shadow_doctrine_binding(self):
        with mock.patch.object(
            MODULE,
            "_changed_paths",
            return_value={
                "adoption/phase3/r26-published-project-disposition-intake.json",
                "adoption/universal-token-control-r26.json",
                "specs/adversarialllm.md",
                "tests/test_adversarialllm_utilization_shadow_doctrine.py",
            },
        ):
            MODULE.verify_batch(self._copy(), "HEAD")

    def test_publishing_workflow_runs_local_and_authorized_remote_checks(self):
        workflow = (ROOT / ".github" / "workflows" / "disposition-intake.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "python tools/check_phase5_stale_reconciliation.py --treeish HEAD\n",
            workflow,
        )
        self.assertIn(
            "python tools/check_phase5_stale_reconciliation.py --treeish HEAD --verify-remotes",
            workflow,
        )
        self.assertIn("if: env.R26_REMOTE_AUTH_CONFIGURED == 'true'", workflow)
        self.assertIn("ADOBE REMOTE NOT VERIFIED", workflow)

    def test_remote_verifier_rederives_exact_refs_and_commits(self):
        advertised = "".join(
            f"{record['commit']}\t{record['name']}\n" for record in MODULE.ADOBE_REFS
        )

        def remote_git(args, **kwargs):
            if args[:2] == ["init", "--quiet"]:
                return b""
            if args[:3] == ["ls-remote", "--exit-code", "--refs"]:
                return advertised
            if args[0] == "fetch":
                return b""
            if args[:3] == ["rev-parse", "--verify", "--end-of-options"]:
                index = int(args[3].split("/")[-1].split("^")[0])
                return MODULE.ADOBE_REFS[index]["commit"] + "\n"
            if args[:3] == ["show", "-s", "--format=%T%n%P"]:
                record = next(item for item in MODULE.ADOBE_REFS if item["commit"] == args[3])
                return record["tree"] + "\n" + " ".join(record["parents"]) + "\n"
            raise AssertionError(f"unexpected remote git call: {args}")

        with (
            mock.patch.object(MODULE, "_run_remote_git", side_effect=remote_git),
            mock.patch.object(MODULE, "_remote_marker_paths", return_value=[]),
            mock.patch.object(MODULE, "_verify_remote_artifact"),
        ):
            MODULE.verify_remotes(self._copy())

    def test_remote_verifier_fails_on_ref_drift(self):
        advertised = "".join(
            f"{'0' * 40 if index == 0 else record['commit']}\t{record['name']}\n"
            for index, record in enumerate(MODULE.ADOBE_REFS)
        )

        def remote_git(args, **kwargs):
            if args[:2] == ["init", "--quiet"]:
                return b""
            if args[:3] == ["ls-remote", "--exit-code", "--refs"]:
                return advertised
            raise AssertionError(f"unexpected remote git call: {args}")

        with mock.patch.object(MODULE, "_run_remote_git", side_effect=remote_git):
            with self.assertRaisesRegex(MODULE.Phase5Error, "ADOBE_REMOTE_REF_MISMATCH"):
                MODULE.verify_remotes(self._copy())


if __name__ == "__main__":
    unittest.main()
