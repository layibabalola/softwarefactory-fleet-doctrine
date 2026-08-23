from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "check_phase12_integration.py"
SPEC = importlib.util.spec_from_file_location("check_phase12_integration", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Phase12IntegrationTests(unittest.TestCase):
    @staticmethod
    def _treeish():
        return "990906b6ea861ca579e1336bcfe8f17dd80c83ae"

    def test_01_exact_staged_integration_passes(self):
        MODULE.verify_integration(self._treeish())

    def test_02_duplicate_and_case_colliding_keys_fail_closed(self):
        for raw in (b'{"schema":1,"schema":2}', b'{"schema":1,"Schema":2}'):
            with self.subTest(raw=raw), self.assertRaisesRegex(MODULE.Phase12Error, "DUPLICATE_OR_CASE_COLLIDING_KEY"):
                MODULE.load_json(raw)

    def test_03_merge_parent_order_is_exact(self):
        original = MODULE._tuple

        def drift(commit):
            if commit == MODULE.MERGE_COMMIT:
                return MODULE.MERGE_TREE, [MODULE.PHASE11_COMMIT, MODULE.CURRENT_MASTER]
            return original(commit)

        with mock.patch.object(MODULE, "_tuple", side_effect=drift):
            with self.assertRaisesRegex(MODULE.Phase12Error, "MERGE_TUPLE_MISMATCH"):
                MODULE.verify_sources()

    def test_04_integration_scope_is_closed(self):
        with mock.patch.object(MODULE, "_changed_paths", return_value=MODULE.INTEGRATION_PATHS | {"specs/forged.md"}):
            with self.assertRaisesRegex(MODULE.Phase12Error, "INTEGRATION_SCOPE_MISMATCH"):
                MODULE.verify_integration(self._treeish())

    def test_05_native_authority_false_cannot_alias_zero(self):
        expected = MODULE._expected_artifact()
        hostile = copy.deepcopy(expected)
        hostile["authority"]["runtime"] = 0
        self.assertFalse(MODULE._type_exact(hostile, expected))

    def test_06_ledger_count_integer_cannot_alias_boolean(self):
        expected = MODULE._expected_artifact()
        hostile = copy.deepcopy(expected)
        hostile["activePolicy"]["counts"]["ADOPT"] = False
        self.assertFalse(MODULE._type_exact(hostile, expected))

    def test_07_manifest_repair_cannot_be_reactivated(self):
        original = MODULE._oid

        def drift(treeish, path):
            if treeish == self._treeish() and path == MODULE.MANIFEST:
                return "65901748c5843f05b37e4352c5b469e47804e2f1"
            return original(treeish, path)

        with mock.patch.object(MODULE, "_oid", side_effect=drift):
            with self.assertRaisesRegex(MODULE.Phase12Error, "ACTIVE_MANIFEST_POLICY_DRIFT"):
                MODULE.verify_current_policy(self._treeish())

    def test_08_frozen_manifest_checker_oid_drift_is_rejected(self):
        original = MODULE._oid

        def drift(treeish, path):
            if treeish == self._treeish() and path == MODULE.MANIFEST_CHECKER:
                return "0" * 40
            return original(treeish, path)

        with mock.patch.object(MODULE, "_oid", side_effect=drift):
            with self.assertRaisesRegex(MODULE.Phase12Error, "ACTIVE_MANIFEST_POLICY_DRIFT"):
                MODULE.verify_current_policy(self._treeish())

    def test_09_ledger_drift_is_rejected(self):
        original = MODULE._oid

        def drift(treeish, path):
            if treeish == self._treeish() and path == MODULE.LEDGER:
                return "0" * 40
            return original(treeish, path)

        with mock.patch.object(MODULE, "_oid", side_effect=drift):
            with self.assertRaisesRegex(MODULE.Phase12Error, "LEDGER_DRIFT"):
                MODULE.verify_current_policy(self._treeish())

    def test_10_current_master_spec_drift_is_rejected(self):
        original = MODULE._oid

        def drift(treeish, path):
            if treeish == self._treeish() and path == "specs/cloudvore.md":
                return "0" * 40
            return original(treeish, path)

        with mock.patch.object(MODULE, "_oid", side_effect=drift):
            with self.assertRaisesRegex(MODULE.Phase12Error, "SPEC_BLOB_DRIFT"):
                MODULE.verify_current_policy(self._treeish())

    def test_11_imported_evidence_drift_is_rejected(self):
        target = next(iter(MODULE.EVIDENCE))
        original = MODULE._oid

        def drift(treeish, path):
            if treeish == self._treeish() and path == target:
                return "0" * 40
            return original(treeish, path)

        with mock.patch.object(MODULE, "_oid", side_effect=drift):
            with self.assertRaisesRegex(MODULE.Phase12Error, "IMPORTED_EVIDENCE_DRIFT"):
                MODULE.verify_evidence(self._treeish())

    def test_12_workflow_must_route_historical_and_current_checkers(self):
        original = MODULE._blob

        def drift(treeish, path):
            raw = original(treeish, path)
            if path == ".github/workflows/disposition-intake.yml":
                return raw.replace(MODULE.PHASE11_COMMIT.encode(), b"0" * 40, 1)
            return raw

        with mock.patch.object(MODULE, "_blob", side_effect=drift):
            with self.assertRaisesRegex(MODULE.Phase12Error, "HISTORICAL_CHECKER_ROUTING_INVALID"):
                MODULE.verify_workflow(self._treeish())

    def test_13_artifact_closed_shape_is_exact(self):
        expected = MODULE._expected_artifact()
        for mutate in (
            lambda value: value.update({"extra": False}),
            lambda value: value["importedEvidence"].pop(),
            lambda value: value["activePolicy"].update({"manifestBinding": "MUTABLE"}),
        ):
            hostile = copy.deepcopy(expected)
            mutate(hostile)
            self.assertFalse(MODULE._type_exact(hostile, expected))


if __name__ == "__main__":
    unittest.main()
