import copy
from contextlib import redirect_stderr
import importlib.util
import io
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

    def _event_scope(self, changed, event="pull_request"):
        with (
            mock.patch.object(MODULE, "_commit_tuple", return_value=("b" * 40, [])),
            mock.patch.object(MODULE, "_is_ancestor", return_value=True),
            mock.patch.object(MODULE, "_event_changed_paths", return_value=set(changed)),
        ):
            return MODULE.evaluate_event_scope(event, "a" * 40, "HEAD")

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

    def test_phase2_event_allowlist_is_spec_free_and_distinct_from_history(self):
        self.assertFalse(any(path.startswith("specs/") for path in MODULE.EVENT_ALLOWED_PHASE2_PATHS))
        self.assertNotEqual(MODULE.ALLOWED_PHASE2_PATHS, MODULE.EVENT_ALLOWED_PHASE2_PATHS)
        self.assertTrue(MODULE.ORIGINAL_COMMON_PHASE_TRIGGER_PATHS < MODULE.COMMON_PHASE_TRIGGER_PATHS)
        self.assertTrue(MODULE.BOOTSTRAP_CONTROL_PATHS < MODULE.COMMON_PHASE_TRIGGER_PATHS)
        self.assertEqual(
            MODULE.ORIGINAL_COMMON_PHASE_TRIGGER_PATHS | MODULE.BOOTSTRAP_CONTROL_PATHS,
            MODULE.COMMON_PHASE_TRIGGER_PATHS,
        )
        self.assertEqual(
            {"tests/test_universal_provider_control.py", "tools/check_universal_manifest.py"},
            MODULE.AUXILIARY_EVENT_ALLOWED_PATHS,
        )
        self.assertEqual(MODULE.COMMON_PHASE_TRIGGER_PATHS | {MODULE.BATCH_PATH}, MODULE.PHASE2_TRIGGER_PATHS)
        self.assertEqual(
            MODULE.PHASE2_TRIGGER_PATHS | MODULE.AUXILIARY_EVENT_ALLOWED_PATHS,
            MODULE.EVENT_ALLOWED_PHASE2_PATHS,
        )

    def test_phase2_unrelated_r29_provider_delta_is_explicit_na(self):
        changed = {
            "README.md", "RECONCILIATION.md",
            "manifests/universal-provider-control-reconciliation-r29.json",
            "schemas/universal-provider-review-admission-v1.schema.json",
            "specs/fleet-universal-provider-control-reconciliation.md",
            "tests/test_universal_provider_control.py",
            "tools/check_universal_manifest.py", "tools/universal_provider_control.py",
        }
        self.assertEqual(self._event_scope(changed), "N/A_NO_PHASE2_TRIGGER")

    def test_phase2_clean_control_surface_and_owned_data_are_applicable(self):
        self.assertEqual(self._event_scope(MODULE.COMMON_PHASE_TRIGGER_PATHS), "APPLICABLE")
        self.assertEqual(
            self._event_scope(
                MODULE.COMMON_PHASE_TRIGGER_PATHS | MODULE.AUXILIARY_EVENT_ALLOWED_PATHS
            ),
            "APPLICABLE",
        )
        self.assertEqual(self._event_scope({MODULE.BATCH_PATH}), "APPLICABLE")

    def test_phase2_rejects_every_formerly_allowed_spec_when_mixed(self):
        former_specs = {
            "specs/adversarialllm.md", "specs/cloudvore.md",
            "specs/mlv-app.md", "specs/salesforce-tools.md",
        }
        self.assertTrue(former_specs.issubset(MODULE.ALLOWED_PHASE2_PATHS))
        for path in sorted(former_specs):
            with self.subTest(path=path):
                with self.assertRaisesRegex(MODULE.BatchError, "PHASE2_SCOPE_VIOLATION"):
                    self._event_scope({"tools/check_phase2_disposition_batch.py", path})

    def test_phase2_control_deletion_or_change_cannot_hide_foreign_mutation(self):
        for control in (
            ".github/workflows/disposition-intake.yml",
            "tests/test_phase2_disposition_batch.py",
            "tools/check_phase2_disposition_batch.py",
        ):
            with self.subTest(control=control):
                with self.assertRaisesRegex(MODULE.BatchError, "PHASE2_SCOPE_VIOLATION"):
                    self._event_scope({control, "src/runtime.py"})

    def test_phase2_carrier_controls_are_na_and_trigger_union_is_bounded(self):
        controls = {"tools/check_universal_manifest.py", "tests/test_universal_provider_control.py"}
        trigger = {".github/workflows/disposition-intake.yml"}
        self.assertEqual(self._event_scope(controls), "N/A_NO_PHASE2_TRIGGER")
        self.assertEqual(self._event_scope(trigger | controls), "APPLICABLE")
        for foreign in ("tools/universal_provider_control.py", "specs/cloudvore.md"):
            with self.subTest(foreign=foreign):
                with self.assertRaisesRegex(MODULE.BatchError, "PHASE2_SCOPE_VIOLATION"):
                    self._event_scope(trigger | controls | {foreign})

    def test_phase2_missing_invalid_or_nonancestor_base_fails_closed(self):
        with self.assertRaisesRegex(MODULE.BatchError, "PHASE2_SCOPE_EVENT_INVALID"):
            MODULE.evaluate_event_scope("", "", "HEAD")
        for base in ("", "not-a-sha"):
            with self.subTest(base=base):
                with self.assertRaisesRegex(MODULE.BatchError, "PHASE2_SCOPE_BASE_INVALID"):
                    MODULE.evaluate_event_scope("pull_request", base, "HEAD")
        with (
            mock.patch.object(MODULE, "_commit_tuple", return_value=("b" * 40, [])),
            mock.patch.object(MODULE, "_is_ancestor", return_value=False),
        ):
            with self.assertRaisesRegex(MODULE.BatchError, "PHASE2_SCOPE_BASE_INVALID"):
                MODULE.evaluate_event_scope("push", "a" * 40, "HEAD")

    def test_phase2_workflow_dispatch_is_explicit_na(self):
        self.assertEqual(
            MODULE.evaluate_event_scope("workflow_dispatch", "", "HEAD"),
            "N/A_WORKFLOW_DISPATCH",
        )

    def test_phase2_main_verifies_frozen_evidence_before_event_scope(self):
        with (
            mock.patch.object(
                MODULE,
                "_blob",
                return_value=(ROOT / MODULE.BATCH_PATH).read_bytes(),
            ),
            mock.patch.object(MODULE, "verify_batch", side_effect=MODULE.BatchError("FROZEN_FAIL")),
            mock.patch.object(MODULE, "evaluate_event_scope") as scope,
            mock.patch.dict(os.environ, {"R26_SCOPE_EVENT": "workflow_dispatch", "R26_SCOPE_BASE_SHA": ""}, clear=False),
        ):
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                self.assertEqual(1, MODULE.main(["--treeish", MODULE.FROZEN_PUBLICATION]))
        scope.assert_not_called()
        self.assertIn("FROZEN_FAIL", stderr.getvalue())

    def test_phase2_historical_treeish_cannot_redirect_event_target(self):
        original = MODULE._event_changed_paths
        with mock.patch.object(MODULE, "_git", return_value="tools/check_phase2_disposition_batch.py\n") as git:
            self.assertEqual(
                {"tools/check_phase2_disposition_batch.py"},
                original("a" * 40, MODULE.FROZEN_PUBLICATION),
            )
        self.assertIn("a" * 40 + "..HEAD", git.call_args.args[0])

    def test_phase2_scope_inputs_are_environment_only(self):
        for option in ("--scope-event", "--scope-base"):
            with self.subTest(option=option), self.assertRaises(SystemExit):
                MODULE.main([option, "workflow_dispatch"])

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
