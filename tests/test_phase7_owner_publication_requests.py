import copy
import importlib.util
from pathlib import Path
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "check_phase7_owner_publication_requests.py"
SPEC = importlib.util.spec_from_file_location("check_phase7_owner_publication_requests", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class Phase7OwnerPublicationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.requests = {
            project_id: MODULE.load_json(
                (ROOT / MODULE.REQUEST_DIR / f"{project_id}.json").read_bytes()
            )
            for project_id in sorted(MODULE.PROJECT_IDS)
        }

    def _copy(self):
        return copy.deepcopy(self.requests)

    def test_staged_candidate_passes(self):
        MODULE.verify_requests(self._copy(), ":")

    def test_duplicate_json_key_fails_closed(self):
        with self.assertRaisesRegex(MODULE.Phase7Error, "DUPLICATE_KEY"):
            MODULE.load_json(b'{"schema":"one","schema":"two"}')

    def test_closed_project_set_is_exact(self):
        requests = self._copy()
        requests.pop("conjugal")
        with self.assertRaisesRegex(MODULE.Phase7Error, "REQUEST_SET_MISMATCH"):
            MODULE.verify_request_documents(requests)

    def test_fabricated_disposition_is_rejected(self):
        for project_id in sorted(MODULE.PROJECT_IDS):
            with self.subTest(project_id=project_id):
                requests = self._copy()
                requests[project_id]["prohibitedClaims"][0] = "ADOPT(fabricated)"
                with self.assertRaisesRegex(MODULE.Phase7Error, "FORMAL_DISPOSITION_FABRICATED"):
                    MODULE.verify_request_documents(requests)

    def test_request_status_cannot_become_a_disposition(self):
        requests = self._copy()
        requests["agent-bridge"]["status"] = "DISTINGUISH"
        with self.assertRaisesRegex(MODULE.Phase7Error, "REQUEST_STATUS_INVALID"):
            MODULE.verify_request_documents(requests)

    def test_canonical_r26_pins_are_mandatory(self):
        for field in ("baseCommit", "baseTree", "baseParent", "r26Candidate", "r26Merge", "ledgerGitBlobOid"):
            with self.subTest(field=field):
                requests = self._copy()
                requests["airmypc"]["frozenDoctrine"][field] = "0" * 40
                with self.assertRaisesRegex(MODULE.Phase7Error, "FROZEN_DOCTRINE_MISMATCH"):
                    MODULE.verify_request_documents(requests)

    def test_identity_ref_and_object_requirements_cannot_be_omitted(self):
        for field in MODULE.IDENTITY_FIELDS:
            with self.subTest(field=field):
                requests = self._copy()
                values = requests["conjugal"]["ownerPublicationContract"]["exactIdentityBinding"]["ownerSuppliedFields"]
                values.remove(field)
                with self.assertRaisesRegex(MODULE.Phase7Error, "IDENTITY_REQUIREMENTS_INCOMPLETE"):
                    MODULE.verify_request_documents(requests)

    def test_artifact_binding_fields_cannot_be_omitted(self):
        for field in MODULE.ARTIFACT_FIELDS:
            with self.subTest(field=field):
                requests = self._copy()
                values = requests["agent-bridge"]["ownerPublicationContract"]["artifactManifestBinding"]["ownerSuppliedFields"]
                values.remove(field)
                with self.assertRaisesRegex(MODULE.Phase7Error, "ARTIFACT_REQUIREMENTS_INCOMPLETE"):
                    MODULE.verify_request_documents(requests)

    def test_non_regression_axes_and_evidence_shape_are_closed(self):
        for field, code in (("model", "NON_REGRESSION_REQUIREMENTS_INCOMPLETE"), ("functionality", "NON_REGRESSION_REQUIREMENTS_INCOMPLETE")):
            with self.subTest(field=field):
                requests = self._copy()
                requests["airmypc"]["ownerPublicationContract"]["nonRegressionBinding"]["axes"].remove(field)
                with self.assertRaisesRegex(MODULE.Phase7Error, code):
                    MODULE.verify_request_documents(requests)
        requests = self._copy()
        requests["airmypc"]["ownerPublicationContract"]["nonRegressionBinding"]["eachAxisFields"].remove("evidenceArtifacts")
        with self.assertRaisesRegex(MODULE.Phase7Error, "NON_REGRESSION_REQUIREMENTS_INCOMPLETE"):
            MODULE.verify_request_documents(requests)

    def test_adopt_runtime_and_installation_proofs_are_closed(self):
        for field in MODULE.ADOPT_PROOF_FIELDS:
            with self.subTest(field=field):
                requests = self._copy()
                values = requests["agent-bridge"]["ownerPublicationContract"]["runtimeAndInstallationBinding"]["ownerSuppliedFields"]
                values.remove(field)
                with self.assertRaisesRegex(MODULE.Phase7Error, "ADOPT_PROOF_REQUIREMENTS_INCOMPLETE"):
                    MODULE.verify_request_documents(requests)

    def test_adobe_work_order_and_quorum_fields_are_mandatory(self):
        for field in MODULE.ADOBE_AUTHORITY_FIELDS:
            with self.subTest(field=field):
                requests = self._copy()
                values = requests["adobe-ingester"]["ownerPublicationContract"]["projectAuthorityPrerequisites"]["ownerSuppliedFields"]
                values.remove(field)
                with self.assertRaisesRegex(MODULE.Phase7Error, "ADOBE_AUTHORITY_REQUIREMENTS_INCOMPLETE"):
                    MODULE.verify_request_documents(requests)

    def test_adobe_known_quorum_cannot_masquerade_as_satisfied(self):
        requests = self._copy()
        known = requests["adobe-ingester"]["ownerPublicationContract"]["projectAuthorityPrerequisites"]["knownState"]
        known["filledSeats"] = 4
        known["satisfied"] = True
        with self.assertRaisesRegex(MODULE.Phase7Error, "ADOBE_AUTHORITY_REQUIREMENTS_INCOMPLETE"):
            MODULE.verify_request_documents(requests)

    def test_unknown_identity_cannot_gain_an_invented_remote(self):
        for project_id in ("agent-bridge", "airmypc", "conjugal"):
            with self.subTest(project_id=project_id):
                requests = self._copy()
                requests[project_id]["currentEvidence"]["remote"] = "https://example.invalid/invented.git"
                with self.assertRaisesRegex(MODULE.Phase7Error, "CURRENT_EVIDENCE_MISMATCH"):
                    MODULE.verify_request_documents(requests)

    def test_adobe_stale_observation_cannot_be_marked_current(self):
        requests = self._copy()
        adobe = requests["adobe-ingester"]["currentEvidence"]
        adobe["remoteFreshness"] = "CURRENT"
        adobe["observedRefs"][0]["evidenceStatus"] = "CURRENT"
        with self.assertRaisesRegex(MODULE.Phase7Error, "CURRENT_EVIDENCE_MISMATCH"):
            MODULE.verify_request_documents(requests)

    def test_runtime_install_adoption_and_publication_authority_are_false(self):
        for project_id in sorted(MODULE.PROJECT_IDS):
            for field in ("projectDisposition", "adoption", "runtime", "installation", "provider", "scheduler", "gateTransition", "repositoryMutation", "remoteMutation", "publication", "message"):
                with self.subTest(project_id=project_id, field=field):
                    requests = self._copy()
                    requests[project_id]["authority"][field] = True
                    with self.assertRaisesRegex(MODULE.Phase7Error, "AUTHORITY_OVERCLAIM"):
                        MODULE.verify_request_documents(requests)

    def test_queue_cannot_become_executable_or_advance_status(self):
        for field in ("executable", "automaticStatusAdvance", "writesAuthorized", "providerCallsAuthorized"):
            with self.subTest(field=field):
                requests = self._copy()
                requests["conjugal"]["queue"][field] = True
                with self.assertRaisesRegex(MODULE.Phase7Error, "QUEUE_OVERCLAIM"):
                    MODULE.verify_request_documents(requests)

    def test_product_ledger_and_spec_scope_is_closed(self):
        with mock.patch.object(MODULE, "_changed_paths", return_value={"specs/airmypc.md"}):
            with self.assertRaisesRegex(MODULE.Phase7Error, "PHASE7_SCOPE_VIOLATION"):
                MODULE.verify_requests(self._copy(), ":")

    def test_protected_ledger_and_specs_must_remain_exact(self):
        original_oid = MODULE._oid

        def drift(treeish, path):
            if treeish == ":" and path == MODULE.LEDGER_PATH:
                return "0" * 40
            return original_oid(treeish, path)

        with mock.patch.object(MODULE, "_oid", side_effect=drift):
            with self.assertRaisesRegex(MODULE.Phase7Error, "PROTECTED_BLOB_DRIFT"):
                MODULE.verify_requests(self._copy(), ":")

    def test_workflow_runs_phase7_checker_and_hostile_tests(self):
        workflow = (ROOT / ".github" / "workflows" / "disposition-intake.yml").read_text(encoding="utf-8")
        self.assertIn('python -m unittest discover -s tests -p "test_phase7_owner_publication_requests.py" -v', workflow)
        self.assertIn("python tools/check_phase7_owner_publication_requests.py --treeish HEAD", workflow)

    def test_predecessor_scope_gates_allow_only_the_exact_phase7_surface(self):
        for name in ("phase2", "phase3", "phase5"):
            path = ROOT / "tools" / f"check_{name}_disposition_batch.py"
            if name == "phase5":
                path = ROOT / "tools" / "check_phase5_stale_reconciliation.py"
            spec = importlib.util.spec_from_file_location(f"phase7_predecessor_{name}", path)
            module = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(module)
            allowed = getattr(module, f"ALLOWED_{name.upper()}_PATHS")
            self.assertTrue(MODULE.ALLOWED_PHASE7_PATHS.issubset(allowed), name)


if __name__ == "__main__":
    unittest.main()
