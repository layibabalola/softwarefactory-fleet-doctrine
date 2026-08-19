import copy
import importlib.util
import os
from pathlib import Path
import sys
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "check_phase2_disposition_batch.py"
SPEC = importlib.util.spec_from_file_location("check_phase2_disposition_batch", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class Phase2DispositionBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = MODULE.load_json(
            (ROOT / "adoption" / "phase2" / "r26-project-disposition-intake.json").read_bytes()
        )

    def _copy(self):
        return copy.deepcopy(self.batch)

    def _project(self, batch, project_id):
        return next(project for project in batch["projects"] if project["projectId"] == project_id)

    def test_batch_matches_frozen_ledger_and_project_spec_blobs(self):
        MODULE.verify_batch(self._copy(), "HEAD")

    def test_duplicate_json_key_is_rejected(self):
        with self.assertRaisesRegex(MODULE.BatchError, "DUPLICATE_KEY"):
            MODULE.load_json(b'{"schema":"a","schema":"b"}')

    def test_frozen_implementation_and_packet_cannot_be_rewritten(self):
        batch = self._copy()
        batch["frozenBase"]["implementationCommit"] = "0" * 40
        with self.assertRaisesRegex(MODULE.BatchError, "FROZEN_BASE_MISMATCH"):
            MODULE.verify_batch(batch, "HEAD")

        batch = self._copy()
        batch["frozenBase"]["reviewPacketCommit"] = "1" * 40
        with self.assertRaisesRegex(MODULE.BatchError, "FROZEN_BASE_MISMATCH"):
            MODULE.verify_batch(batch, "HEAD")

    def test_project_cannot_be_removed_from_the_batch(self):
        batch = self._copy()
        batch["projects"].pop()
        with self.assertRaisesRegex(MODULE.BatchError, "PROJECT_BATCH_SIZE_INVALID"):
            MODULE.verify_batch(batch, "HEAD")

    def test_salesforce_missing_disposition_remains_first_priority(self):
        batch = self._copy()
        batch["projects"][0], batch["projects"][1] = batch["projects"][1], batch["projects"][0]
        with self.assertRaisesRegex(
            MODULE.BatchError, "PROJECT_PRIORITY_ORDER_INVALID|MISSING_DISPOSITION_NOT_FIRST_PRIORITY"
        ):
            MODULE.verify_batch(batch, "HEAD")

    def test_no_external_blocker_can_be_promoted_to_a_candidate(self):
        batch = self._copy()
        project = self._project(batch, "agent-bridge")
        project["dispositionOutcome"]["candidateProduced"] = True
        with self.assertRaisesRegex(MODULE.BatchError, "DISPOSITION_CANDIDATE_OVERCLAIM"):
            MODULE.verify_batch(batch, "HEAD")

    def test_no_external_blocker_can_claim_adoption_or_runtime_authority(self):
        for field in ("projectDisposition", "adoption", "runtime", "mutation"):
            with self.subTest(field=field):
                batch = self._copy()
                self._project(batch, "airmypc")["authority"][field] = True
                with self.assertRaisesRegex(MODULE.BatchError, "PROJECT_AUTHORITY_OVERCLAIM"):
                    MODULE.verify_batch(batch, "HEAD")

    def test_project_owned_commit_and_blob_pin_are_mandatory(self):
        batch = self._copy()
        self._project(batch, "cloudvore")["sourceEvidence"]["gitBlobOid"] = "0" * 40
        with self.assertRaisesRegex(MODULE.BatchError, "SOURCE_EVIDENCE_LEDGER_MISMATCH"):
            MODULE.verify_batch(batch, "HEAD")

    def test_all_six_non_regression_dimensions_are_required(self):
        batch = self._copy()
        del self._project(batch, "conjugal")["nonRegression"]["quality"]
        with self.assertRaisesRegex(MODULE.BatchError, "DIMENSION_SET_INVALID"):
            MODULE.verify_batch(batch, "HEAD")

    def test_spec_boundary_anchor_must_exist_in_exact_project_blob(self):
        batch = self._copy()
        self._project(batch, "adobe-ingester")["nonRegression"]["model"]["anchors"] = [
            "FABRICATED_CURRENT_R26_MODEL_RECEIPT"
        ]
        with self.assertRaisesRegex(MODULE.BatchError, "DIMENSION_ANCHOR_NOT_IN_SPEC:model"):
            MODULE.verify_batch(batch, "HEAD")

    def test_missing_dimension_cannot_carry_implied_evidence(self):
        batch = self._copy()
        self._project(batch, "salesforce-tools")["nonRegression"]["effort"]["anchors"] = [
            "inferred-effort"
        ]
        with self.assertRaisesRegex(MODULE.BatchError, "MISSING_DIMENSION_HAS_ANCHOR"):
            MODULE.verify_batch(batch, "HEAD")

    def test_absent_repository_cannot_be_marked_accessible_or_worktreed(self):
        for field in ("repositoryAccessible", "worktreeCreated"):
            with self.subTest(field=field):
                batch = self._copy()
                self._project(batch, "salesforce-tools")["boundedDiscovery"][field] = True
                with self.assertRaisesRegex(MODULE.BatchError, "INACCESSIBLE_PROJECT_OVERCLAIM"):
                    MODULE.verify_batch(batch, "HEAD")

    def test_summary_cannot_invent_candidates_or_adoption(self):
        for field in ("dispositionCandidates", "adoptionClaims"):
            with self.subTest(field=field):
                batch = self._copy()
                batch["summary"][field] = 1
                with self.assertRaisesRegex(MODULE.BatchError, "SUMMARY_OVERCLAIM"):
                    MODULE.verify_batch(batch, "HEAD")

    def test_phase2_scope_rejects_product_or_spec_mutation(self):
        batch = self._copy()
        with mock.patch.object(
            MODULE, "_changed_paths", return_value={"specs/dng-auto-processor.md"}
        ):
            with self.assertRaisesRegex(MODULE.BatchError, "PHASE2_SCOPE_VIOLATION"):
                MODULE.verify_batch(batch, "HEAD")

    def test_phase2_scope_allows_exact_forward_adoption_checker_hardening(self):
        batch = self._copy()
        with mock.patch.object(
            MODULE,
            "_changed_paths",
            return_value={
                "adoption/README.md",
                "adoption/phase3/README.md",
                "adoption/phase3/r26-published-project-disposition-intake.json",
                "adoption/phase5/README.md",
                "adoption/phase5/r26-stale-project-reconciliation.json",
                "adoption/universal-token-control-r26.json",
                "specs/adversarialllm.md",
                "specs/cloudvore.md",
                "specs/mlv-app.md",
                "specs/salesforce-tools.md",
                "tests/test_adoption_ledger.py",
                "tools/check_adoption_ledger.py",
                "tests/test_phase2_disposition_batch.py",
                "tools/check_phase2_disposition_batch.py",
                "tests/test_phase3_disposition_batch.py",
                "tools/check_phase3_disposition_batch.py",
                "tests/test_phase5_stale_reconciliation.py",
                "tools/check_phase5_stale_reconciliation.py",
            },
        ):
            MODULE.verify_batch(batch, "HEAD")

    def test_local_probe_verifier_is_bounded_and_fails_on_drift(self):
        batch = self._copy()
        with (
            mock.patch.dict(os.environ, {"COMPUTERNAME": "ULTRA-MAGNUS"}),
            mock.patch.object(MODULE.Path, "exists", return_value=False),
            mock.patch.object(MODULE.Path, "iterdir", return_value=iter(())),
        ):
            MODULE.verify_local_probes(batch)

        with (
            mock.patch.dict(os.environ, {"COMPUTERNAME": "ULTRA-MAGNUS"}),
            mock.patch.object(MODULE.Path, "exists", return_value=True),
            mock.patch.object(MODULE.Path, "iterdir", return_value=iter(())),
        ):
            with self.assertRaisesRegex(MODULE.BatchError, "LOCAL_PROBE_DRIFT"):
                MODULE.verify_local_probes(batch)


if __name__ == "__main__":
    unittest.main()
