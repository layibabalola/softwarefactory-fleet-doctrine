import copy
from contextlib import redirect_stderr
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "check_phase5_stale_reconciliation.py"
SPEC = importlib.util.spec_from_file_location("check_phase5_stale_reconciliation", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class Phase5StaleReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = MODULE.load_json(
            (ROOT / MODULE.INTAKE_PATH).read_bytes()
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

    def test_published_batch_passes_local_verification(self):
        MODULE.verify_batch(self._copy(), "HEAD")

    def test_duplicate_json_key_fails_closed(self):
        with self.assertRaisesRegex(MODULE.Phase5Error, "DUPLICATE_KEY"):
            MODULE.load_json(b'{"schema":"one","schema":"two"}')

    def test_frozen_base_cannot_move(self):
        batch = self._copy()
        batch["frozenBase"]["publishedMasterCommit"] = "0" * 40
        with self.assertRaisesRegex(MODULE.Phase5Error, "FROZEN_BASE_MISMATCH"):
            MODULE.verify_batch(batch, "HEAD")

    def test_adobe_reachability_cannot_be_converted_to_disposition(self):
        batch = self._copy()
        adobe = self._project(batch, "adobe-ingester")
        adobe["outcome"]["status"] = "DISTINGUISH"
        adobe["outcome"]["advanceAuthorized"] = True
        with self.assertRaisesRegex(MODULE.Phase5Error, "OUTCOME_OVERCLAIM"):
            MODULE.verify_batch(batch, "HEAD")

    def test_adobe_remote_and_ref_are_exact(self):
        for mutation in ("remote", "commit", "marker"):
            with self.subTest(mutation=mutation):
                batch = self._copy()
                discovery = self._project(batch, "adobe-ingester")["discovery"]
                if mutation == "remote":
                    discovery["remote"] = "https://example.invalid/adobe.git"
                elif mutation == "commit":
                    discovery["refs"][0]["commit"] = "0" * 40
                else:
                    discovery["r26MarkerSearch"]["matchingPaths"] = ["fabricated-r26.json"]
                with self.assertRaisesRegex(MODULE.Phase5Error, "ADOBE_DISCOVERY_MISMATCH"):
                    MODULE.verify_batch(batch, "HEAD")

    def test_adobe_workflow_evidence_is_exact_and_zero_authority(self):
        batch = self._copy()
        adobe = self._project(batch, "adobe-ingester")
        adobe["discovery"]["workflowEvidence"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(MODULE.Phase5Error, "ADOBE_DISCOVERY_MISMATCH"):
            MODULE.verify_batch(batch, "HEAD")

    def test_negative_discovery_is_not_global_nonexistence_proof(self):
        for project_id in ("agent-bridge", "airmypc", "conjugal"):
            with self.subTest(project_id=project_id):
                batch = self._copy()
                discovery = self._project(batch, project_id)["discovery"]
                discovery["remote"] = "https://example.invalid/invented.git"
                with self.assertRaisesRegex(MODULE.Phase5Error, "NEGATIVE_DISCOVERY_OVERCLAIM"):
                    MODULE.verify_batch(batch, "HEAD")

    def test_any_authority_claim_fails_closed(self):
        for project_id in sorted(MODULE.PROJECT_IDS):
            with self.subTest(project_id=project_id):
                batch = self._copy()
                self._project(batch, project_id)["authority"]["provider"] = True
                with self.assertRaisesRegex(MODULE.Phase5Error, "AUTHORITY_OVERCLAIM"):
                    MODULE.verify_batch(batch, "HEAD")

    def test_summary_cannot_claim_adoption_or_status_advance(self):
        for field in (
            "currentR26Dispositions", "adoptionClaims", "runtimeAuthorityClaims",
            "projectMutationClaims",
        ):
            with self.subTest(field=field):
                batch = self._copy()
                batch["summary"][field] = 1
                with self.assertRaisesRegex(MODULE.Phase5Error, "SUMMARY_OVERCLAIM"):
                    MODULE.verify_batch(batch, "HEAD")

    def test_phase5_event_allowlist_is_spec_free_and_distinct_from_history(self):
        self.assertFalse(any(path.startswith("specs/") for path in MODULE.EVENT_ALLOWED_PHASE5_PATHS))
        self.assertNotEqual(MODULE.ALLOWED_PHASE5_PATHS, MODULE.EVENT_ALLOWED_PHASE5_PATHS)
        self.assertEqual(20, len(MODULE.COMMON_PHASE_TRIGGER_PATHS))
        self.assertEqual(set(), MODULE.AUXILIARY_EVENT_ALLOWED_PATHS)
        self.assertEqual(MODULE.BOOTSTRAP_CONTROL_PATHS, MODULE.PHASE5_TRIGGER_PATHS)
        self.assertEqual(MODULE.BOOTSTRAP_CONTROL_PATHS, MODULE.EVENT_ALLOWED_PHASE5_PATHS)

    def test_phase5_unrelated_r29_provider_delta_is_explicit_na(self):
        changed = {
            "README.md", "RECONCILIATION.md",
            "manifests/universal-provider-control-reconciliation-r29.json",
            "schemas/universal-provider-review-admission-v1.schema.json",
            "specs/fleet-universal-provider-control-reconciliation.md",
            "tests/test_universal_provider_control.py",
            "tools/check_universal_manifest.py", "tools/universal_provider_control.py",
        }
        self.assertEqual(self._event_scope(changed), "N/A_NO_PHASE5_TRIGGER")

    def test_phase5_clean_control_surface_and_owned_data_are_applicable(self):
        self.assertEqual(self._event_scope(MODULE.COMMON_PHASE_TRIGGER_PATHS), "APPLICABLE")
        self.assertEqual(
            self._event_scope(
                MODULE.COMMON_PHASE_TRIGGER_PATHS | MODULE.AUXILIARY_EVENT_ALLOWED_PATHS
            ),
            "APPLICABLE",
        )
        self.assertEqual(self._event_scope({MODULE.INTAKE_PATH}), "N/A_NO_PHASE5_TRIGGER")

    def test_phase5_rejects_every_formerly_allowed_spec_when_mixed(self):
        former_specs = {
            "specs/adversarialllm.md", "specs/cloudvore.md",
            "specs/mlv-app.md", "specs/salesforce-tools.md",
        }
        self.assertIn("specs/adversarialllm.md", MODULE.ALLOWED_PHASE5_PATHS)
        for path in sorted(former_specs):
            with self.subTest(path=path):
                with self.assertRaisesRegex(MODULE.Phase5Error, "PHASE5_SCOPE_VIOLATION"):
                    self._event_scope({"tools/check_phase5_stale_reconciliation.py", path})

    def test_phase5_control_deletion_or_change_cannot_hide_foreign_mutation(self):
        for control in (
            ".github/workflows/disposition-intake.yml",
            "tests/test_phase5_stale_reconciliation.py",
            "tools/check_phase5_stale_reconciliation.py",
        ):
            with self.subTest(control=control):
                with self.assertRaisesRegex(MODULE.Phase5Error, "PHASE5_SCOPE_VIOLATION"):
                    self._event_scope({control, "src/runtime.py"})

    def test_phase5_carrier_controls_are_na_and_mixing_is_refused(self):
        controls = {"tools/check_universal_manifest.py", "tests/test_universal_provider_control.py"}
        trigger = {".github/workflows/disposition-intake.yml"}
        self.assertEqual(self._event_scope(controls), "N/A_NO_PHASE5_TRIGGER")
        with self.assertRaisesRegex(MODULE.Phase5Error, "PHASE5_SCOPE_VIOLATION"):
            self._event_scope(trigger | controls)
        for foreign in ("tools/universal_provider_control.py", "specs/cloudvore.md"):
            with self.subTest(foreign=foreign):
                with self.assertRaisesRegex(MODULE.Phase5Error, "PHASE5_SCOPE_VIOLATION"):
                    self._event_scope(trigger | controls | {foreign})

    def test_phase5_missing_invalid_or_nonancestor_base_fails_closed(self):
        with self.assertRaisesRegex(MODULE.Phase5Error, "PHASE5_SCOPE_EVENT_INVALID"):
            MODULE.evaluate_event_scope("", "", "HEAD")
        for base in ("", "not-a-sha"):
            with self.subTest(base=base):
                with self.assertRaisesRegex(MODULE.Phase5Error, "PHASE5_SCOPE_BASE_INVALID"):
                    MODULE.evaluate_event_scope("pull_request", base, "HEAD")
        with (
            mock.patch.object(MODULE, "_commit_tuple", return_value=("b" * 40, [])),
            mock.patch.object(MODULE, "_is_ancestor", return_value=False),
        ):
            with self.assertRaisesRegex(MODULE.Phase5Error, "PHASE5_SCOPE_BASE_INVALID"):
                MODULE.evaluate_event_scope("push", "a" * 40, "HEAD")

    def test_phase5_workflow_dispatch_is_explicit_na(self):
        self.assertEqual(
            MODULE.evaluate_event_scope("workflow_dispatch", "", "HEAD"),
            "N/A_WORKFLOW_DISPATCH",
        )

    def test_phase5_main_verifies_frozen_evidence_before_event_scope(self):
        with (
            mock.patch.object(
                MODULE,
                "_blob",
                return_value=(ROOT / MODULE.INTAKE_PATH).read_bytes(),
            ),
            mock.patch.object(
                MODULE,
                "verify_batch",
                side_effect=MODULE.Phase5Error("FROZEN_FAIL"),
            ),
            mock.patch.object(MODULE, "evaluate_event_scope") as scope,
        ):
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                self.assertEqual(1, MODULE.main(["--treeish", MODULE.FROZEN_PUBLICATION, "--scope-event", "workflow_dispatch"]))
        scope.assert_not_called()
        self.assertIn("FROZEN_FAIL", stderr.getvalue())

    def test_publishing_workflow_runs_local_and_authorized_remote_checks(self):
        workflow = (ROOT / ".github" / "workflows" / "disposition-intake.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "python tools/check_phase5_stale_reconciliation.py --treeish 990906b6ea861ca579e1336bcfe8f17dd80c83ae",
            workflow,
        )
        self.assertIn("'--verify-remotes'", workflow)
        self.assertIn("env.R26_REMOTE_AUTH_CONFIGURED == 'true'", workflow)
        self.assertIn("ADOBE REMOTE NOT VERIFIED", workflow)
        self.assertIn("R26_SCOPE_EVENT: ${{ github.event_name }}", workflow)
        self.assertIn("github.event.pull_request.base.sha", workflow)
        self.assertIn("github.event.before", workflow)

    def test_phase5_historical_treeish_cannot_redirect_event_target(self):
        with mock.patch.object(MODULE, "_git", return_value="tools/check_phase5_stale_reconciliation.py\n") as git:
            self.assertEqual(
                {"tools/check_phase5_stale_reconciliation.py"},
                MODULE._event_changed_paths("a" * 40, MODULE.FROZEN_PUBLICATION),
            )
        self.assertIn("a" * 40 + "..HEAD", git.call_args.args[0])

    def test_remote_verifier_rederives_exact_refs_and_commits(self):
        advertised = "".join(
            f"{record['commit']}\t{record['name']}\n" for record in MODULE.ADOBE_REFS
        )

        def remote_git(args, **kwargs):
            if args[:2] == ["init", "--quiet"]:
                return b""
            if args[:3] == ["ls-remote", "--exit-code", "--refs"]:
                return advertised
            if args[0] == "fetch":
                return b""
            if args[:3] == ["rev-parse", "--verify", "--end-of-options"]:
                index = int(args[3].split("/")[-1].split("^")[0])
                return MODULE.ADOBE_REFS[index]["commit"] + "\n"
            if args[:3] == ["show", "-s", "--format=%T%n%P"]:
                record = next(item for item in MODULE.ADOBE_REFS if item["commit"] == args[3])
                return record["tree"] + "\n" + " ".join(record["parents"]) + "\n"
            raise AssertionError(f"unexpected remote git call: {args}")

        with (
            mock.patch.object(MODULE, "_run_remote_git", side_effect=remote_git),
            mock.patch.object(MODULE, "_remote_marker_paths", return_value=[]),
            mock.patch.object(MODULE, "_verify_remote_artifact"),
        ):
            MODULE.verify_remotes(self._copy())

    def test_remote_verifier_fails_on_ref_drift(self):
        advertised = "".join(
            f"{'0' * 40 if index == 0 else record['commit']}\t{record['name']}\n"
            for index, record in enumerate(MODULE.ADOBE_REFS)
        )

        def remote_git(args, **kwargs):
            if args[:2] == ["init", "--quiet"]:
                return b""
            if args[:3] == ["ls-remote", "--exit-code", "--refs"]:
                return advertised
            raise AssertionError(f"unexpected remote git call: {args}")

        with mock.patch.object(MODULE, "_run_remote_git", side_effect=remote_git):
            with self.assertRaisesRegex(MODULE.Phase5Error, "ADOBE_REMOTE_REF_MISMATCH"):
                MODULE.verify_remotes(self._copy())


if __name__ == "__main__":
    unittest.main()
