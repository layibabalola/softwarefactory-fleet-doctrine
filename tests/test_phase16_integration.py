from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
PUBLICATION = "8149c3f06811f85b833b28940017f2d05448cf5d"
MODULE_PATH = ROOT / "tools" / "check_phase16_integration.py"
SPEC = importlib.util.spec_from_file_location("check_phase16_integration", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Phase16IntegrationTests(unittest.TestCase):
    @staticmethod
    def _treeish():
        return PUBLICATION

    def _doc(self):
        return MODULE.load_json(MODULE._blob(self._treeish(), MODULE.ARTIFACT))

    def test_01_exact_integration_passes(self):
        MODULE.verify(self._treeish())

    def test_02_duplicate_and_case_colliding_keys_refuse(self):
        for raw in (b'{"schema":1,"schema":2}', b'{"schema":1,"Schema":2}'):
            with self.subTest(raw=raw), self.assertRaisesRegex(MODULE.Phase16Error, "DUPLICATE_OR_CASE_COLLIDING_KEY"):
                MODULE.load_json(raw)

    def test_03_scope_is_closed(self):
        with mock.patch.object(MODULE, "_changed_paths", return_value=MODULE.INTEGRATION_PATHS | {"specs/forged.md"}):
            with self.assertRaisesRegex(MODULE.Phase16Error, "INTEGRATION_SCOPE_MISMATCH"):
                MODULE.verify(self._treeish())

    def test_04_artifact_hash_is_exact(self):
        original = MODULE._blob
        def drift(treeish, path):
            raw = original(treeish, path)
            return raw + b" " if path == MODULE.ARTIFACT else raw
        with mock.patch.object(MODULE, "_blob", side_effect=drift):
            with self.assertRaisesRegex(MODULE.Phase16Error, "ARTIFACT_HASH_MISMATCH"):
                MODULE.verify(self._treeish())

    def test_05_native_aliases_refuse(self):
        for section, key, value in (
            ("independentReview", "permissionDenials", False),
            ("independentReview", "permissionDenials", 0.0),
            ("ledgerTreatment", "ledgerModified", 0),
            ("authority", "installation", 0),
        ):
            hostile = copy.deepcopy(self._doc())
            hostile[section][key] = value
            with self.subTest(section=section, key=key), self.assertRaises(MODULE.Phase16Error):
                MODULE.verify_document(hostile)

    def test_06_review_identity_and_verdict_refuse_drift(self):
        for key, value in (("sessionId", "00000000-0000-0000-0000-000000000000"), ("verdict", "REVISE"), ("providerTools", ["Read", "Bash"])):
            hostile = copy.deepcopy(self._doc())
            hostile["independentReview"][key] = value
            with self.subTest(key=key), self.assertRaises(MODULE.Phase16Error):
                MODULE.verify_document(hostile)

    def test_07_packet_result_and_consumption_snapshots_refuse_drift(self):
        original = MODULE._blob
        for target, code in ((MODULE.PACKET, "PACKET_SNAPSHOT_INVALID"), (MODULE.RESULT, "RESULT_SNAPSHOT_INVALID"), (MODULE.CONSUMPTION, "CONSUMPTION_SNAPSHOT_INVALID")):
            def drift(treeish, path, target=target):
                raw = original(treeish, path)
                return raw + b" " if path == target else raw
            with self.subTest(target=target), mock.patch.object(MODULE, "_blob", side_effect=drift):
                with self.assertRaisesRegex(MODULE.Phase16Error, code):
                    MODULE.verify_snapshots(self._treeish())

    def test_08_result_and_consumption_bindings_are_semantic(self):
        original = MODULE._blob
        raw = MODULE._blob(self._treeish(), MODULE.RESULT)
        hostile = raw.replace(b'"verdict":"ACCEPT"', b'"verdict":"REVISE"', 1)
        with mock.patch.object(MODULE, "_blob", side_effect=lambda treeish, path: hostile if path == MODULE.RESULT else original(treeish, path)):
            with self.assertRaisesRegex(MODULE.Phase16Error, "RESULT_SNAPSHOT_INVALID"):
                MODULE.verify_snapshots(self._treeish())

    def test_09_both_low_closures_are_exact(self):
        for row in ("workflowOrder", "stagedSpecRederivation"):
            hostile = copy.deepcopy(self._doc())
            hostile["findingClosure"][row]["status"] = "OPEN"
            with self.subTest(row=row), self.assertRaisesRegex(MODULE.Phase16Error, "FINDING_CLOSURE_INVALID"):
                MODULE.verify_document(hostile)

    def test_10_closure_source_hash_and_laws_are_exact(self):
        original = MODULE._blob
        def drift(treeish, path):
            raw = original(treeish, path)
            return raw.replace(b"positions != sorted(positions)", b"False", 1) if path == "tools/check_phase15_integration.py" else raw
        with mock.patch.object(MODULE, "_blob", side_effect=drift):
            with self.assertRaisesRegex(MODULE.Phase16Error, "PHASE15_CHECKER_CLOSURE_INVALID"):
                MODULE.verify_closure(self._treeish())

    def test_11_ledger_specs_and_uncredited_proofs_stay_frozen(self):
        hostile = copy.deepcopy(self._doc())
        hostile["remainingUncreditedProofs"].pop()
        with self.assertRaisesRegex(MODULE.Phase16Error, "UNCREDITED_PROOFS_INVALID"):
            MODULE.verify_document(hostile)
        original = MODULE._oid
        with mock.patch.object(MODULE, "_oid", side_effect=lambda treeish, path: "0" * 40 if path == MODULE.LEDGER else original(treeish, path)):
            with self.assertRaisesRegex(MODULE.Phase16Error, "LEDGER_DRIFT"):
                MODULE.verify_policy(self._treeish())

    def test_12_workflow_order_is_enforced(self):
        original = MODULE._blob
        raw = MODULE._blob(self._treeish(), ".github/workflows/disposition-intake.yml")
        first = f"python tools/check_phase15_integration.py --treeish {MODULE.PHASE15}".encode()
        second = b'test_phase16_integration.py" -v'
        swapped = raw.replace(first, b"__FIRST__", 1).replace(second, first, 1).replace(b"__FIRST__", second, 1)
        with mock.patch.object(MODULE, "_blob", side_effect=lambda treeish, path: swapped if path.endswith("disposition-intake.yml") else original(treeish, path)):
            with self.assertRaisesRegex(MODULE.Phase16Error, "WORKFLOW_ROUTING_INVALID"):
                MODULE.verify_workflow(self._treeish())

    def test_13_staged_specs_are_read_from_index(self):
        if self._treeish() != ":":
            self.skipTest("staged-only control")
        original = MODULE._oid
        with mock.patch.object(MODULE, "_oid", side_effect=lambda treeish, path: "0" * 40 if treeish == ":" and path == "specs/mlv-app.md" else original(treeish, path)):
            with self.assertRaisesRegex(MODULE.Phase16Error, "SPEC_DRIFT"):
                MODULE.verify_policy(":")

    def test_14_authority_and_root_shapes_are_closed(self):
        hostile = copy.deepcopy(self._doc())
        hostile["authority"]["preview"] = False
        with self.assertRaisesRegex(MODULE.Phase16Error, "AUTHORITY_SHAPE_INVALID"):
            MODULE.verify_document(hostile)
        hostile = copy.deepcopy(self._doc())
        hostile["extra"] = False
        with self.assertRaisesRegex(MODULE.Phase16Error, "ROOT_SHAPE_INVALID"):
            MODULE.verify_document(hostile)

    def test_15_later_head_is_refused_by_historical_verifier(self):
        with mock.patch.object(MODULE, "_changed_paths", return_value={"tools/foreign.py"}):
            with self.assertRaisesRegex(MODULE.Phase16Error, "INTEGRATION_SCOPE_MISMATCH"):
                MODULE.verify("HEAD")


if __name__ == "__main__":
    unittest.main()
