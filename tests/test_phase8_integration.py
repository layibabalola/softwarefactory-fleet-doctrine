from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from unittest import mock
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "check_phase8_integration.py"
SPEC = importlib.util.spec_from_file_location("check_phase8_integration", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
HISTORICAL_TREEISH = "e7311e3038bbfeebe15cc10004f40b3795811659"


class Phase8IntegrationTests(unittest.TestCase):
    def test_exact_committed_integration_passes(self):
        MODULE.verify_integration(HISTORICAL_TREEISH)

    def test_source_commit_tree_or_parent_drift_is_rejected(self):
        original = MODULE._commit_tuple

        def drift(commit):
            if commit == MODULE.PHASE7_COMMIT:
                return "0" * 40, [MODULE.PHASE5_BASE]
            return original(commit)

        with mock.patch.object(MODULE, "_commit_tuple", side_effect=drift):
            with self.assertRaisesRegex(MODULE.Phase8Error, "PHASE7_SUBJECT_MISMATCH"):
                MODULE.verify_source_objects()

    def test_non_phase6_parent_is_rejected(self):
        original = MODULE._commit_tuple

        def drift(commit):
            if commit == HISTORICAL_TREEISH:
                return original(commit)[0], [MODULE.PHASE7_COMMIT]
            return original(commit)

        with mock.patch.object(MODULE, "_commit_tuple", side_effect=drift):
            with self.assertRaisesRegex(MODULE.Phase8Error, "INTEGRATION_PARENT_MISMATCH"):
                MODULE.verify_integration(HISTORICAL_TREEISH)

    def test_any_extra_integration_path_is_rejected(self):
        with mock.patch.object(
            MODULE,
            "_changed_paths",
            side_effect=lambda base, treeish: (
                MODULE.PHASE7_SOURCE_DELTA_PATHS
                if base == MODULE.PHASE5_BASE
                else MODULE.EXPECTED_INTEGRATION_PATHS | {"specs/cloudvore.md"}
            ),
        ):
            with self.assertRaisesRegex(MODULE.Phase8Error, "INTEGRATION_SCOPE_MISMATCH"):
                MODULE.verify_integration(HISTORICAL_TREEISH)

    def test_ledger_or_packet_blob_drift_is_rejected(self):
        original = MODULE._oid
        for drift_path, error in (
            (MODULE.LEDGER_PATH, "LEDGER_STATUS_ADVANCE"),
            ("adoption/phase7/requests/airmypc.json", "PRESERVED_ARTIFACT_DRIFT"),
        ):
            with self.subTest(path=drift_path):
                def drift(treeish, path, *, target=drift_path):
                    if treeish == HISTORICAL_TREEISH and path == target:
                        return "0" * 40
                    return original(treeish, path)

                with mock.patch.object(MODULE, "_oid", side_effect=drift):
                    with self.assertRaisesRegex(MODULE.Phase8Error, error):
                        MODULE.verify_integration(HISTORICAL_TREEISH)

    def test_packet_authority_and_status_advance_are_rejected(self):
        original = MODULE._load_json
        for field, error in (("authority", "REQUEST_AUTHORITY_ADVANCE"), ("status", "REQUEST_STATUS_ADVANCE")):
            with self.subTest(field=field):
                def drift(treeish, path, *, target=field):
                    value = copy.deepcopy(original(treeish, path))
                    if path.endswith("adobe-ingester.json"):
                        if target == "authority":
                            value["authority"]["publication"] = True
                        else:
                            value["status"] = "ADOPT"
                    return value

                with mock.patch.object(MODULE, "_load_json", side_effect=drift):
                    with self.assertRaisesRegex(MODULE.Phase8Error, error):
                        MODULE.verify_zero_authority_packets(HISTORICAL_TREEISH)

    def test_predecessor_allowlists_cover_only_the_frozen_integration_surface(self):
        modules = {
            "phase2": ("tools/check_phase2_disposition_batch.py", "ALLOWED_PHASE2_PATHS"),
            "phase3": ("tools/check_phase3_disposition_batch.py", "ALLOWED_PHASE3_PATHS"),
            "phase5": ("tools/check_phase5_stale_reconciliation.py", "ALLOWED_PHASE5_PATHS"),
            "phase6": ("tools/check_phase6_candidate_reviews.py", "ALLOWED_PATHS"),
            "phase7": ("tools/check_phase7_owner_publication_requests.py", "ALLOWED_PHASE7_PATHS"),
        }
        for name, (relative, attribute) in modules.items():
            spec = importlib.util.spec_from_file_location(f"phase8_{name}", ROOT / relative)
            module = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(module)
            allowed = getattr(module, attribute)
            self.assertTrue(MODULE.EXPECTED_INTEGRATION_PATHS.issubset(allowed), name)

    def test_workflow_runs_every_phase_and_ledger_corridor(self):
        workflow = (ROOT / ".github" / "workflows" / "disposition-intake.yml").read_text(encoding="utf-8")
        expected = [
            'test_phase2_disposition_batch.py" -v',
            "check_phase2_disposition_batch.py --treeish HEAD",
            'test_phase3_disposition_batch.py" -v',
            "check_phase3_disposition_batch.py --treeish HEAD",
            'test_phase5_stale_reconciliation.py" -v',
            "check_phase5_stale_reconciliation.py --treeish HEAD",
            'test_phase6_candidate_reviews.py" -v',
            f"check_phase6_candidate_reviews.py --treeish {HISTORICAL_TREEISH}",
            'test_phase7_owner_publication_requests.py" -v',
            f"check_phase7_owner_publication_requests.py --treeish {HISTORICAL_TREEISH}",
            'test_phase8_integration.py" -v',
            f"check_phase8_integration.py --treeish {HISTORICAL_TREEISH}",
            'test_adoption_ledger.py" -v',
            "check_adoption_ledger.py --treeish HEAD",
        ]
        for command in expected:
            self.assertIn(command, workflow)

    def test_request_packet_blobs_are_the_accepted_phase7_objects(self):
        expected = {
            path: oid
            for path, oid in MODULE.PHASE7_EXACT_TARGET_BLOBS.items()
            if path.startswith(f"{MODULE.REQUEST_DIR}/")
        }
        self.assertEqual(len(expected), 4)
        for path, oid in expected.items():
            self.assertEqual(MODULE._oid(MODULE.PHASE7_COMMIT, path), oid)
            self.assertEqual(MODULE._oid(HISTORICAL_TREEISH, path), oid)


if __name__ == "__main__":
    unittest.main()
