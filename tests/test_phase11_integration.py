from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "check_phase11_integration.py"
SPEC = importlib.util.spec_from_file_location("check_phase11_integration", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Phase11IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.canonical = MODULE.canonical_phase10_receipt()

    def _treeish(self) -> str:
        head = str(MODULE._git(["rev-parse", "HEAD"], text=True)).strip()
        return ":" if head == MODULE.PHASE10_COMMIT else "HEAD"

    def _batch(self):
        return copy.deepcopy(self.canonical)

    @staticmethod
    def _review(batch, project_id):
        return next(row for row in batch["reviews"] if row["projectId"] == project_id)

    def _assert_receipt_rejected(self, batch):
        with self.assertRaisesRegex(MODULE.Phase11Error, "PHASE10_RECEIPT_CANONICAL_DIGEST_MISMATCH"):
            MODULE.verify_phase10_receipt_closed(batch)

    def test_01_exact_staged_or_committed_integration_passes(self):
        MODULE.verify_integration(self._treeish())

    def test_02_duplicate_json_keys_fail_closed(self):
        raw = MODULE._blob(MODULE.PHASE10_COMMIT, MODULE.PHASE10_RECEIPT_PATH)
        hostile = raw.replace(b'"schema": ', b'"schema": "forged", "schema": ', 1)
        with self.assertRaisesRegex(MODULE.Phase11Error, "DUPLICATE_JSON_KEY"):
            MODULE.load_json(hostile)

    def test_03_extra_review_key_is_rejected(self):
        batch = self._batch()
        batch["reviews"][0]["forgedReviewKey"] = "accepted-by-phase10"
        self._assert_receipt_rejected(batch)

    def test_04_extra_execution_evidence_key_is_rejected(self):
        batch = self._batch()
        batch["reviews"][0]["executionEvidence"][0]["forgedEvidenceKey"] = True
        self._assert_receipt_rejected(batch)

    def test_05_forged_mlv_result_is_rejected(self):
        batch = self._batch()
        self._review(batch, "mlv-app")["executionEvidence"][0]["result"] = "FORGED PASS"
        self._assert_receipt_rejected(batch)

    def test_06_forged_cloudvore_result_is_rejected(self):
        batch = self._batch()
        self._review(batch, "cloudvore")["executionEvidence"][1]["result"] = "FORGED 21/21"
        self._assert_receipt_rejected(batch)

    def test_07_forged_r8_suite_path_is_rejected(self):
        batch = self._batch()
        self._review(batch, "dng-auto-processor")["independentExecutionEvidence"][0]["path"] = "forged-suite.ps1"
        self._assert_receipt_rejected(batch)

    def test_08_widened_review_scope_is_rejected(self):
        batch = self._batch()
        self._review(batch, "mlv-app")["reviewScope"] += "_AND_INSTALLATION"
        self._assert_receipt_rejected(batch)

    def test_09_mlv_inventory_complete_true_is_rejected(self):
        batch = self._batch()
        self._review(batch, "mlv-app")["semanticFindings"]["inventoryComplete"] = True
        self._assert_receipt_rejected(batch)

    def test_10_mlv_disposition_credit_true_is_rejected(self):
        batch = self._batch()
        self._review(batch, "mlv-app")["semanticFindings"]["dispositionCredit"] = True
        self._assert_receipt_rejected(batch)

    def test_11_omitted_mlv_artifact_row_is_rejected(self):
        batch = self._batch()
        self._review(batch, "mlv-app")["artifacts"].pop()
        self._assert_receipt_rejected(batch)

    def test_12_omitted_r8_critical_artifact_row_is_rejected(self):
        batch = self._batch()
        self._review(batch, "dng-auto-processor")["criticalArtifacts"].pop()
        self._assert_receipt_rejected(batch)

    def test_13_injected_superseded_phase10_provenance_is_rejected(self):
        batch = self._batch()
        self._review(batch, "dng-auto-processor")["phase10Commit"] = MODULE.SUPERSEDED_PHASE10_COMMIT
        self._assert_receipt_rejected(batch)

    def test_14_all_eleven_coordinated_mutations_are_rejected(self):
        batch = self._batch()
        mlv = self._review(batch, "mlv-app")
        cloud = self._review(batch, "cloudvore")
        r8 = self._review(batch, "dng-auto-processor")
        mlv["forgedReviewKey"] = "coordinated"
        mlv["executionEvidence"][0]["forgedEvidenceKey"] = 1
        mlv["executionEvidence"][0]["result"] = "FORGED PASS"
        cloud["executionEvidence"][0]["result"] = "FORGED 17/17"
        r8["independentExecutionEvidence"][0]["path"] = "forged-suite.ps1"
        mlv["reviewScope"] += "_AND_AUTHORITY"
        mlv["semanticFindings"]["inventoryComplete"] = True
        mlv["semanticFindings"]["dispositionCredit"] = True
        mlv["artifacts"].pop()
        r8["criticalArtifacts"].pop()
        r8["phase10Commit"] = MODULE.SUPERSEDED_PHASE10_COMMIT
        self._assert_receipt_rejected(batch)

    def test_15_recursive_native_type_and_closed_sets_are_independently_enforced(self):
        for mutate in (
            lambda batch: batch["summary"].update(reviewCount=True),
            lambda batch: batch["reviews"].reverse(),
            lambda batch: batch["reviews"][0]["authority"].pop("runtime"),
            lambda batch: batch["reviews"][0]["artifacts"][0].update(bytes=False),
        ):
            batch = self._batch()
            mutate(batch)
            with self.subTest(mutate=mutate), self.assertRaisesRegex(MODULE.Phase11Error, "PHASE10_RECEIPT_NATIVE_EXACT_MISMATCH"):
                MODULE._exact_native(batch, self.canonical)

    def test_16_closure_artifact_pins_exact_eleven_and_zero_authority(self):
        closure = MODULE.verify_closure_artifact(self._treeish())
        self.assertEqual(closure["closure"]["forbiddenMutations"], MODULE.EXPECTED_MUTATIONS)
        self.assertEqual(closure["closure"]["forbiddenMutationCount"], 11)
        self.assertTrue(all(value is False for value in closure["authority"].values()))

    def test_17_phase10_source_receipt_and_scope_are_exact_bound(self):
        MODULE.verify_phase10_source()
        original = MODULE._commit_tuple
        with mock.patch.object(MODULE, "_commit_tuple", return_value=("0" * 40, [MODULE.PHASE10_PARENT])):
            with self.assertRaisesRegex(MODULE.Phase11Error, "PHASE10_SOURCE_OBJECT_MISMATCH"):
                MODULE.verify_phase10_source()
        with mock.patch.object(MODULE, "_commit_tuple", side_effect=original):
            MODULE.verify_phase10_source()

    def test_18_integration_scope_allowlist_workflow_and_frozen_doctrine_fail_closed(self):
        treeish = self._treeish()
        original_changed = MODULE._changed_paths

        def extra_path(base, candidate):
            value = original_changed(base, candidate)
            return value | {"src/runtime.py"} if base == MODULE.PHASE10_COMMIT and candidate == treeish else value

        with mock.patch.object(MODULE, "_changed_paths", side_effect=extra_path):
            with self.assertRaisesRegex(MODULE.Phase11Error, "INTEGRATION_SCOPE_MISMATCH"):
                MODULE.verify_integration(treeish)

        path, attribute = next(iter(MODULE.PREDECESSOR_CHECKERS.items()))
        original_assignment = MODULE.P10._assignment_set

        def drift_assignment(candidate, candidate_path, name):
            value = original_assignment(candidate, candidate_path, name)
            if candidate == treeish and candidate_path == path and name == attribute:
                return value | {"src/runtime.py"}
            return value

        with mock.patch.object(MODULE.P10, "_assignment_set", side_effect=drift_assignment):
            with self.assertRaisesRegex(MODULE.Phase11Error, "PREDECESSOR_ALLOWLIST_UNION_MISMATCH"):
                MODULE.verify_forward_allowlists(treeish)

        workflow = MODULE._blob(treeish, ".github/workflows/disposition-intake.yml")
        with mock.patch.object(MODULE, "_blob", return_value=workflow.replace(b"test_phase11_integration", b"test_phaseXX_integration")):
            with self.assertRaisesRegex(MODULE.Phase11Error, "WORKFLOW_PHASE11_MISSING"):
                MODULE.verify_workflow(treeish)

        original_oid = MODULE._oid

        def drift_oid(candidate, path):
            if candidate == treeish and path == MODULE.LEDGER_PATH:
                return "0" * 40
            return original_oid(candidate, path)

        with mock.patch.object(MODULE, "_oid", side_effect=drift_oid):
            with self.assertRaisesRegex(MODULE.Phase11Error, "FROZEN_DOCTRINE_ARTIFACT_DRIFT"):
                MODULE.verify_frozen_doctrine(treeish)


if __name__ == "__main__":
    unittest.main()
