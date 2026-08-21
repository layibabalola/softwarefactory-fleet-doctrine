from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "check_phase15_integration.py"
SPEC = importlib.util.spec_from_file_location("check_phase15_integration", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Phase15IntegrationTests(unittest.TestCase):
    @staticmethod
    def _treeish():
        head = str(MODULE._git(["rev-parse", "HEAD"], text=True)).strip()
        return ":" if head == MODULE.PHASE14 else "HEAD"

    def _doc(self):
        return MODULE.load_json(MODULE._blob(self._treeish(), MODULE.ARTIFACT))

    def test_01_exact_integration_passes(self):
        MODULE.verify(self._treeish())

    def test_02_duplicate_and_case_colliding_keys_refuse(self):
        for raw in (b'{"schema":1,"schema":2}', b'{"schema":1,"Schema":2}'):
            with self.subTest(raw=raw), self.assertRaisesRegex(MODULE.Phase15Error, "DUPLICATE_OR_CASE_COLLIDING_KEY"):
                MODULE.load_json(raw)

    def test_03_scope_is_closed(self):
        with mock.patch.object(MODULE, "_changed_paths", return_value=MODULE.INTEGRATION_PATHS | {"specs/forged.md"}):
            with self.assertRaisesRegex(MODULE.Phase15Error, "INTEGRATION_SCOPE_MISMATCH"):
                MODULE.verify(self._treeish())

    def test_04_artifact_hash_is_exact(self):
        original = MODULE._blob
        def drift(treeish, path):
            raw = original(treeish, path)
            return raw + b" " if path == MODULE.ARTIFACT else raw
        with mock.patch.object(MODULE, "_blob", side_effect=drift):
            with self.assertRaisesRegex(MODULE.Phase15Error, "ARTIFACT_HASH_MISMATCH"):
                MODULE.verify_artifact(self._treeish())

    def test_05_native_type_aliases_refuse(self):
        attacks = (
            ("sourceProject", "remoteRefVerified", 1),
            ("acceptedBoundary", "productionLauncherWired", 0),
            ("ledgerTreatment", "ledgerModified", 0),
            ("authority", "installation", 0),
        )
        for section, key, value in attacks:
            hostile = copy.deepcopy(self._doc())
            hostile[section][key] = value
            with self.subTest(section=section, key=key), self.assertRaises(MODULE.Phase15Error):
                MODULE.verify_document(hostile)

    def test_06_review_identity_and_profile_are_exact(self):
        for key, value in (("verdict", "REVISE"), ("model", "different"), ("providerTools", ["Read", "Bash"])):
            hostile = copy.deepcopy(self._doc())
            hostile["independentReview"][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(MODULE.Phase15Error, "INDEPENDENT_REVIEW_INVALID"):
                MODULE.verify_document(hostile)

    def test_07_review_and_closure_tuples_are_exact(self):
        for section, key in (("reviewedCandidate", "commit"), ("forwardClosure", "testSha256"), ("durableProjectReceipt", "gitBlobOid")):
            hostile = copy.deepcopy(self._doc())
            hostile[section][key] = "0" * len(hostile[section][key])
            with self.subTest(section=section, key=key), self.assertRaises(MODULE.Phase15Error):
                MODULE.verify_document(hostile)

    def test_08_open_gate_and_installation_overclaims_refuse(self):
        for section, key, value in (
            ("forwardClosure", "openGateHostile", "MISSING"),
            ("acceptedBoundary", "productionLauncherWired", True),
            ("acceptedBoundary", "signedInstallation", True),
            ("acceptedBoundary", "adoption", True),
        ):
            hostile = copy.deepcopy(self._doc())
            hostile[section][key] = value
            with self.subTest(section=section, key=key), self.assertRaises(MODULE.Phase15Error):
                MODULE.verify_document(hostile)

    def test_09_missing_or_extra_keys_refuse(self):
        missing = copy.deepcopy(self._doc())
        del missing["independentReview"]["scope"]
        with self.assertRaisesRegex(MODULE.Phase15Error, "REVIEW_SHAPE_INVALID"):
            MODULE.verify_document(missing)
        extra = copy.deepcopy(self._doc())
        extra["authority"]["preview"] = False
        with self.assertRaisesRegex(MODULE.Phase15Error, "AUTHORITY_SHAPE_INVALID"):
            MODULE.verify_document(extra)

    def test_10_ledger_and_specs_stay_frozen(self):
        original = MODULE._oid
        def drift(treeish, path):
            if treeish == self._treeish() and path == MODULE.LEDGER:
                return "0" * 40
            return original(treeish, path)
        with mock.patch.object(MODULE, "_oid", side_effect=drift):
            with self.assertRaisesRegex(MODULE.Phase15Error, "LEDGER_DRIFT"):
                MODULE.verify_policy(self._treeish())

    def test_11_uncredited_proofs_are_ordered_and_complete(self):
        hostile = copy.deepcopy(self._doc())
        hostile["remainingUncreditedProofs"].pop()
        with self.assertRaisesRegex(MODULE.Phase15Error, "UNCREDITED_PROOFS_INVALID"):
            MODULE.verify_document(hostile)

    def test_12_workflow_routes_frozen_phase14_and_live_phase15(self):
        original = MODULE._blob
        def drift(treeish, path):
            raw = original(treeish, path)
            return raw.replace(MODULE.PHASE14.encode(), b"0" * 40, 1) if path.endswith("disposition-intake.yml") else raw
        with mock.patch.object(MODULE, "_blob", side_effect=drift):
            with self.assertRaisesRegex(MODULE.Phase15Error, "WORKFLOW_ROUTING_INVALID"):
                MODULE.verify_workflow(self._treeish())


if __name__ == "__main__":
    unittest.main()
