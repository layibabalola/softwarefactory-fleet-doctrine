from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "check_phase14_integration.py"
SPEC = importlib.util.spec_from_file_location("check_phase14_integration", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Phase14IntegrationTests(unittest.TestCase):
    @staticmethod
    def _treeish():
        head = str(MODULE._git(["rev-parse", "HEAD"], text=True)).strip()
        return ":" if head == MODULE.PHASE13 else "HEAD"

    def test_01_exact_integration_passes(self):
        MODULE.verify(self._treeish())

    def test_02_duplicate_and_case_colliding_keys_refuse(self):
        for raw in (b'{"schema":1,"schema":2}', b'{"schema":1,"Schema":2}'):
            with self.subTest(raw=raw), self.assertRaisesRegex(MODULE.Phase14Error, "DUPLICATE_OR_CASE_COLLIDING_KEY"):
                MODULE.load_json(raw)

    def test_03_scope_is_closed(self):
        with mock.patch.object(MODULE, "_changed_paths", return_value=MODULE.INTEGRATION_PATHS | {"specs/forged.md"}):
            with self.assertRaisesRegex(MODULE.Phase14Error, "INTEGRATION_SCOPE_MISMATCH"):
                MODULE.verify(self._treeish())

    def test_04_artifact_hash_is_exact(self):
        original = MODULE._blob
        def drift(treeish, path):
            raw = original(treeish, path)
            return raw + b" " if path == MODULE.ARTIFACT else raw
        with mock.patch.object(MODULE, "_blob", side_effect=drift):
            with self.assertRaisesRegex(MODULE.Phase14Error, "ARTIFACT_HASH_MISMATCH"):
                MODULE.verify_artifact(self._treeish())

    def test_05_native_types_do_not_alias(self):
        expected = {"complete": False, "count": 41}
        self.assertFalse(MODULE._native({"complete": 0, "count": 41}, expected))
        self.assertFalse(MODULE._native({"complete": False, "count": True}, expected))

    def test_06_ledger_drift_refuses(self):
        original = MODULE._oid
        def drift(treeish, path):
            return "0" * 40 if path == MODULE.LEDGER and treeish == self._treeish() else original(treeish, path)
        with mock.patch.object(MODULE, "_oid", side_effect=drift):
            with self.assertRaisesRegex(MODULE.Phase14Error, "FROZEN_POLICY_DRIFT"):
                MODULE.verify_policy(self._treeish())

    def test_07_spec_drift_refuses(self):
        original = MODULE._oid
        current = MODULE.PHASE13 if self._treeish() == ":" else self._treeish()
        seen = 0
        def drift(treeish, path):
            nonlocal seen
            if treeish == current and path == "specs/mlv-app.md" and seen == 0:
                seen += 1
                return "0" * 40
            return original(treeish, path)
        with mock.patch.object(MODULE, "_oid", side_effect=drift):
            with self.assertRaisesRegex(MODULE.Phase14Error, "SPEC_DRIFT"):
                MODULE.verify_policy(self._treeish())

    def test_08_workflow_must_freeze_phase13_and_route_phase14(self):
        original = MODULE._blob
        def drift(treeish, path):
            raw = original(treeish, path)
            return raw.replace(MODULE.PHASE13.encode(), b"0" * 40, 1) if path.endswith("disposition-intake.yml") else raw
        with mock.patch.object(MODULE, "_blob", side_effect=drift):
            with self.assertRaisesRegex(MODULE.Phase14Error, "WORKFLOW_ROUTING_INVALID"):
                MODULE.verify_workflow(self._treeish())

    def test_09_source_and_authority_aliases_refuse(self):
        self.assertFalse(MODULE._native({"remoteRefVerified": 1}, {"remoteRefVerified": True}))
        self.assertFalse(MODULE._native({"installation": 0}, {"installation": False}))

    def test_10_review_or_boundary_overclaim_refuses(self):
        raw = MODULE._blob(self._treeish(), MODULE.ARTIFACT)
        doc = MODULE.load_json(raw)
        for path, value in (("verdict", "REVISE"), ("model", "different")):
            hostile = json.loads(json.dumps(doc))
            hostile["independentReview"][path] = value
            with mock.patch.object(MODULE, "_blob", return_value=json.dumps(hostile).encode()):
                with self.assertRaisesRegex(MODULE.Phase14Error, "ARTIFACT_HASH_MISMATCH"):
                    MODULE.verify_artifact(self._treeish())


if __name__ == "__main__":
    unittest.main()
