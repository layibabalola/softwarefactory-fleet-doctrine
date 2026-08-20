import copy
import importlib.util
from pathlib import Path
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "check_phase6_candidate_reviews.py"
SPEC = importlib.util.spec_from_file_location("check_phase6_candidate_reviews", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class Phase6CandidateReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = MODULE.load_json((ROOT / MODULE.BATCH_PATH).read_bytes())

    def _copy(self):
        return copy.deepcopy(self.batch)

    def _review(self, batch, project_id):
        return next(review for review in batch["reviews"] if review["projectId"] == project_id)

    def test_published_candidate_passes(self):
        MODULE.verify_batch(self._copy(), "HEAD")

    def test_duplicate_json_key_fails_closed(self):
        with self.assertRaisesRegex(MODULE.Phase6Error, "DUPLICATE_KEY"):
            MODULE.load_json(b'{"schema":"one","schema":"two"}')

    def test_frozen_doctrine_base_cannot_move(self):
        batch = self._copy()
        batch["frozenBase"]["doctrineCommit"] = "0" * 40
        with self.assertRaisesRegex(MODULE.Phase6Error, "FROZEN_BASE_MISMATCH"):
            MODULE.verify_batch(batch, "HEAD")

    def test_any_authority_claim_fails_closed(self):
        for project_id in MODULE.EXPECTED:
            with self.subTest(project_id=project_id):
                batch = self._copy()
                self._review(batch, project_id)["authority"]["provider"] = True
                with self.assertRaisesRegex(MODULE.Phase6Error, "AUTHORITY_OVERCLAIM"):
                    MODULE.verify_batch(batch, "HEAD")

    def test_failed_execution_cannot_remain_accept(self):
        batch = self._copy()
        self._review(batch, "salesforce-tools")["executionEvidence"][0]["exitCode"] = 1
        with self.assertRaisesRegex(MODULE.Phase6Error, "EXECUTION_NOT_PASSING"):
            MODULE.verify_batch(batch, "HEAD")

    def test_salesforce_known_blockers_cannot_be_called_complete(self):
        batch = self._copy()
        self._review(batch, "salesforce-tools")["semanticFindings"][
            "missingAdoptionProofSetComplete"
        ] = True
        with self.assertRaisesRegex(MODULE.Phase6Error, "SEMANTIC_FINDING_INVALID"):
            MODULE.verify_batch(batch, "HEAD")

    def test_salesforce_review_cannot_advance_status_or_adoption(self):
        for field in ("ledgerStatusChangeAuthorized", "adoptionCredit", "installationCredit"):
            with self.subTest(field=field):
                batch = self._copy()
                self._review(batch, "salesforce-tools")["dispositionTreatment"][field] = True
                with self.assertRaisesRegex(MODULE.Phase6Error, "TREATMENT_OVERCLAIM"):
                    MODULE.verify_batch(batch, "HEAD")

    def test_cloudvore_blocker_cannot_become_a_disposition(self):
        batch = self._copy()
        cloud = self._review(batch, "cloudvore")["dispositionTreatment"]
        cloud["candidateDispositionKind"] = "DISTINGUISH"
        cloud["candidateDisposition"] = "DISTINGUISH(fabricated)"
        with self.assertRaisesRegex(MODULE.Phase6Error, "CLOUDVORE_DISPOSITION_FABRICATED"):
            MODULE.verify_batch(batch, "HEAD")

    def test_cloudvore_scanner_cannot_claim_completeness(self):
        batch = self._copy()
        self._review(batch, "cloudvore")["semanticFindings"]["scannerCoverageComplete"] = True
        with self.assertRaisesRegex(MODULE.Phase6Error, "SEMANTIC_FINDING_INVALID"):
            MODULE.verify_batch(batch, "HEAD")

    def test_artifact_drift_fails_closed(self):
        batch = self._copy()
        self._review(batch, "cloudvore")["artifacts"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(MODULE.Phase6Error, "ARTIFACT_BINDING_INVALID"):
            MODULE.verify_batch(batch, "HEAD")

    def test_summary_cannot_claim_a_status_advance(self):
        batch = self._copy()
        batch["summary"]["ledgerStatusChangesAuthorized"] = 1
        with self.assertRaisesRegex(MODULE.Phase6Error, "SUMMARY_INVALID"):
            MODULE.verify_batch(batch, "HEAD")

    def test_scope_rejects_ledger_or_spec_mutation(self):
        with mock.patch.object(MODULE, "_git", return_value="specs/cloudvore.md\n"):
            with self.assertRaisesRegex(MODULE.Phase6Error, "PHASE6_SCOPE_VIOLATION"):
                MODULE._verify_base(self._copy(), "HEAD")


if __name__ == "__main__":
    unittest.main()
