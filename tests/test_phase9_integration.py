from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
from unittest import mock
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "check_phase9_integration.py"
SPEC = importlib.util.spec_from_file_location("check_phase9_integration", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
HISTORICAL_TREEISH = "e7311e3038bbfeebe15cc10004f40b3795811659"


class Phase9IntegrationTests(unittest.TestCase):
    def test_exact_committed_integration_passes(self):
        MODULE.verify_integration(HISTORICAL_TREEISH)

    def test_source_commit_tree_parent_and_delta_are_exact_bound(self):
        original_tuple = MODULE._commit_tuple

        def tuple_drift(commit):
            if commit == MODULE.REPAIR_COMMIT:
                return "0" * 40, [MODULE.REPAIR_PARENT]
            return original_tuple(commit)

        with mock.patch.object(MODULE, "_commit_tuple", side_effect=tuple_drift):
            with self.assertRaisesRegex(MODULE.Phase9Error, "REPAIR_SOURCE_MISMATCH"):
                MODULE.verify_source_objects()

        original_paths = MODULE._changed_paths

        def path_drift(base, treeish):
            paths = original_paths(base, treeish)
            if base == MODULE.PHASE6_COMMIT and treeish == MODULE.PHASE8_COMMIT:
                return paths | {"specs/cloudvore.md"}
            return paths

        with mock.patch.object(MODULE, "_changed_paths", side_effect=path_drift):
            with self.assertRaisesRegex(MODULE.Phase9Error, "PHASE8_SOURCE_DELTA_MISMATCH"):
                MODULE.verify_source_objects()

    def test_non_phase8_parent_is_rejected(self):
        original = MODULE._commit_tuple

        def drift(commit):
            if commit == HISTORICAL_TREEISH:
                return original(commit)[0], [MODULE.REPAIR_COMMIT]
            return original(commit)

        with mock.patch.object(MODULE, "_commit_tuple", side_effect=drift):
            with self.assertRaisesRegex(MODULE.Phase9Error, "INTEGRATION_PARENT_MISMATCH"):
                MODULE.verify_integration(HISTORICAL_TREEISH)

    def test_any_extra_or_missing_integration_path_is_rejected(self):
        original = MODULE._changed_paths
        for paths in (
            MODULE.EXPECTED_INTEGRATION_PATHS | {"src/runtime.py"},
            MODULE.EXPECTED_INTEGRATION_PATHS - {MODULE.MANIFEST_TEST_PATH},
        ):
            with self.subTest(paths=paths):
                def drift(base, treeish, *, replacement=paths):
                    if base == MODULE.PHASE8_COMMIT and treeish == HISTORICAL_TREEISH:
                        return replacement
                    return original(base, treeish)

                with mock.patch.object(MODULE, "_changed_paths", side_effect=drift):
                    with self.assertRaisesRegex(MODULE.Phase9Error, "INTEGRATION_SCOPE_MISMATCH"):
                        MODULE.verify_integration(HISTORICAL_TREEISH)

    def test_manifest_and_hostile_test_are_exact_accepted_blobs(self):
        original = MODULE._oid
        for path in (MODULE.MANIFEST_PATH, MODULE.MANIFEST_TEST_PATH):
            with self.subTest(path=path):
                def drift(treeish, candidate_path, *, target=path):
                    if treeish == HISTORICAL_TREEISH and candidate_path == target:
                        return "0" * 40
                    return original(treeish, candidate_path)

                with mock.patch.object(MODULE, "_oid", side_effect=drift):
                    with self.assertRaisesRegex(MODULE.Phase9Error, "MECHANICAL_REPAIR_DRIFT"):
                        MODULE.verify_exact_artifacts(HISTORICAL_TREEISH)

    def test_phase2_phase3_phase5_allowlists_are_exact_unions(self):
        original = MODULE._assignment_set
        cases = (
            ("ALLOWED_PHASE2_PATHS", lambda value: value - {MODULE.MANIFEST_PATH}),
            ("ALLOWED_PHASE3_PATHS", lambda value: value | {"src/runtime.py"}),
            ("PHASE9_INTEGRATION_PATHS", lambda value: value | {"specs/cloudvore.md"}),
        )
        for attribute, mutate in cases:
            with self.subTest(attribute=attribute):
                def drift(treeish, path, name, *, target=attribute, transform=mutate):
                    value = original(treeish, path, name)
                    if treeish == HISTORICAL_TREEISH and name == target:
                        return transform(value)
                    return value

                with mock.patch.object(MODULE, "_assignment_set", side_effect=drift):
                    with self.assertRaisesRegex(MODULE.Phase9Error, "(ALLOWLIST_UNION|PHASE9_SCOPE)_"):
                        MODULE.verify_allowlist_union(HISTORICAL_TREEISH)

    def test_receipt_and_request_artifacts_remain_exact(self):
        original = MODULE._oid
        for path in (MODULE.RECEIPT_PATH, next(iter(MODULE.REQUEST_BLOBS))):
            with self.subTest(path=path):
                def drift(treeish, candidate_path, *, target=path):
                    if treeish == HISTORICAL_TREEISH and candidate_path == target:
                        return "0" * 40
                    return original(treeish, candidate_path)

                expected = "RECEIPT_DRIFT" if path == MODULE.RECEIPT_PATH else "REQUEST_DRIFT"
                with mock.patch.object(MODULE, "_oid", side_effect=drift):
                    with self.assertRaisesRegex(MODULE.Phase9Error, expected):
                        MODULE.verify_exact_artifacts(HISTORICAL_TREEISH)

    def test_ledger_spec_and_authority_advances_are_rejected(self):
        original_oid = MODULE._oid

        def spec_drift(treeish, path):
            if treeish == HISTORICAL_TREEISH and path == "specs/cloudvore.md":
                return "0" * 40
            return original_oid(treeish, path)

        with mock.patch.object(MODULE, "_oid", side_effect=spec_drift):
            with self.assertRaisesRegex(MODULE.Phase9Error, "SPEC_STATUS_DRIFT"):
                MODULE.verify_frozen_status_and_authority(HISTORICAL_TREEISH)

        original_json = MODULE._load_json
        cases = (
            (MODULE.LEDGER_PATH, "LEDGER_STATUS_ADVANCE"),
            (MODULE.MANIFEST_PATH, "MANIFEST_AUTHORITY_ADVANCE"),
            (MODULE.RECEIPT_PATH, "RECEIPT_AUTHORITY_ADVANCE"),
            (next(iter(MODULE.REQUEST_BLOBS)), "REQUEST_STATUS_ADVANCE"),
        )
        for path, error in cases:
            with self.subTest(path=path):
                def drift(treeish, candidate_path, *, target=path):
                    value = copy.deepcopy(original_json(treeish, candidate_path))
                    if candidate_path != target:
                        return value
                    if target == MODULE.LEDGER_PATH:
                        value["summary"]["counts"]["ADOPT"] = 1
                    elif target == MODULE.MANIFEST_PATH:
                        value["authority"]["providerExecution"] = True
                    elif target == MODULE.RECEIPT_PATH:
                        value["summary"]["adoptionClaims"] = 1
                    else:
                        value["status"] = "ADOPT"
                    return value

                with mock.patch.object(MODULE, "_load_json", side_effect=drift):
                    with self.assertRaisesRegex(MODULE.Phase9Error, error):
                        MODULE.verify_frozen_status_and_authority(HISTORICAL_TREEISH)

    def test_global_manifest_historical_blob_drift_is_rejected(self):
        with mock.patch.object(MODULE, "_oid", return_value="0" * 40):
            with self.assertRaisesRegex(MODULE.Phase9Error, "GLOBAL_MANIFEST_RESULT_MISMATCH"):
                MODULE.verify_global_manifest(HISTORICAL_TREEISH)

    def test_workflow_runs_phase9_and_preserves_the_full_corridor(self):
        workflow = (ROOT / ".github" / "workflows" / "disposition-intake.yml").read_text(encoding="utf-8")
        expected = [
            *[f'test_phase{phase}_' for phase in (2, 3, 5, 6, 7, 8, 9)],
            *[f"check_phase{phase}_" for phase in (2, 3, 5, 6, 7, 8, 9)],
            'test_adoption_ledger.py" -v',
            "check_adoption_ledger.py --treeish HEAD",
        ]
        for command in expected:
            self.assertIn(command, workflow)


if __name__ == "__main__":
    unittest.main()
