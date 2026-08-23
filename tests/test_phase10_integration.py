from __future__ import annotations

import copy
from contextlib import redirect_stdout
import hashlib
import io
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
from unittest import mock
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "check_phase10_integration.py"
SPEC = importlib.util.spec_from_file_location("check_phase10_integration", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class Phase10IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads((ROOT / MODULE.RECEIPT_PATH).read_text(encoding="utf-8"))

    def _copy(self):
        return copy.deepcopy(self.receipt)

    @staticmethod
    def _review(batch, project_id):
        return next(row for row in batch["reviews"] if row["projectId"] == project_id)

    @staticmethod
    def _treeish():
        return "e7311e3038bbfeebe15cc10004f40b3795811659"

    @staticmethod
    def _synthetic_git_review():
        data = b"exact artifact\n"
        return {
            "subject": {
                "localRoot": "C:/hermetic-review-subject", "commit": "a" * 40,
                "tree": "b" * 40, "parent": "c" * 40,
                "remote": "https://example.invalid/subject.git", "changedPaths": ["artifact.txt"],
                "networkRemoteVerified": False, "remoteTrackingRefContainsSubject": False,
                "localBranch": "review",
            },
            "artifacts": [{
                "path": "artifact.txt", "gitBlobOid": "d" * 40,
                "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
            }],
        }, data

    def _run_synthetic_git_review(self, review, data):
        expected = self._synthetic_git_review()[0]
        subject = expected["subject"]
        artifact = expected["artifacts"][0]
        def fake_git(args, **kwargs):
            if args[:2] == ["rev-parse", "--verify"]:
                return subject["commit"]
            key = tuple(args)
            values = {
                ("rev-parse", "--show-toplevel"): subject["localRoot"],
                ("show", "-s", "--format=%T", subject["commit"]): subject["tree"],
                ("show", "-s", "--format=%P", subject["commit"]): subject["parent"],
                ("remote", "get-url", "origin"): subject["remote"],
                ("diff-tree", "--no-commit-id", "--name-only", "-r", subject["commit"]): "artifact.txt\n",
                ("show", f'{subject["commit"]}:artifact.txt'): data,
                ("rev-parse", f'{subject["commit"]}:artifact.txt'): artifact["gitBlobOid"],
            }
            return values[key]
        with (
            mock.patch.object(Path, "is_dir", return_value=True),
            mock.patch.object(MODULE, "verify_git_object_isolation"),
            mock.patch.object(MODULE, "_git", side_effect=fake_git),
        ):
            MODULE._verify_local_git_subject(review, "HERMETIC", rederive_mutable_worktree_state=False)

    def test_01_exact_staged_or_committed_integration_passes(self):
        MODULE.verify_integration(self._treeish())

    def test_02_duplicate_json_keys_fail_closed(self):
        with self.assertRaisesRegex(MODULE.Phase10Error, "DUPLICATE_JSON_KEY"):
            MODULE.load_json(b'{"schema":"one","schema":"two"}')

    def test_03_receipt_blob_oid_bytes_and_sha_are_exact(self):
        raw = MODULE._blob(self._treeish(), MODULE.RECEIPT_PATH)
        probes = (
            ("_oid", "0" * 40, "RECEIPT_BLOB_OID_MISMATCH"),
            ("_blob", raw[:-1], "RECEIPT_BYTES_MISMATCH"),
            ("_blob", raw[:-1] + bytes([raw[-1] ^ 1]), "RECEIPT_SHA256_MISMATCH"),
        )
        for target, value, error in probes:
            with self.subTest(error=error), mock.patch.object(MODULE, target, return_value=value):
                with self.assertRaisesRegex(MODULE.Phase10Error, error):
                    MODULE.verify_receipt_blob(self._treeish())

    def test_04_non_phase9_parent_is_rejected(self):
        original = MODULE._commit_tuple

        def drift(commit):
            if commit == self._treeish():
                return original(MODULE.PHASE9_COMMIT)[0], [MODULE.PHASE9_PARENT]
            return original(commit)

        with mock.patch.object(MODULE, "_commit_tuple", side_effect=drift):
            with self.assertRaisesRegex(MODULE.Phase10Error, "INTEGRATION_PARENT_MISMATCH"):
                MODULE.verify_integration(self._treeish())

    def test_05_extra_or_missing_integration_paths_are_rejected(self):
        original = MODULE._changed_paths
        cases = (
            MODULE.EXPECTED_INTEGRATION_PATHS | {"specs/mlv-app.md"},
            MODULE.EXPECTED_INTEGRATION_PATHS - {MODULE.RECEIPT_PATH},
        )
        for paths in cases:
            with self.subTest(paths=paths):
                def drift(base, treeish, replacement=paths):
                    if base == MODULE.PHASE9_COMMIT:
                        return replacement
                    return original(base, treeish)

                with mock.patch.object(MODULE, "_changed_paths", side_effect=drift):
                    with self.assertRaisesRegex(MODULE.Phase10Error, "INTEGRATION_SCOPE_MISMATCH"):
                        MODULE.verify_integration(self._treeish())

    def test_06_mlv_subject_or_artifact_substitution_is_rejected(self):
        review, data = self._synthetic_git_review()
        self._run_synthetic_git_review(copy.deepcopy(review), data)
        for mutate, error in (
            (lambda value: value["subject"].update(commit="0" * 40), "HERMETIC_SUBJECT_MISMATCH"),
            (lambda value: value["subject"].update(tree="0" * 40), "HERMETIC_SUBJECT_MISMATCH"),
            (lambda value: value["subject"].update(parent="0" * 40), "HERMETIC_SUBJECT_MISMATCH"),
            (lambda value: value["subject"].update(remote="https://forged.invalid/repo.git"), "HERMETIC_SUBJECT_MISMATCH"),
            (lambda value: value["artifacts"][0].update(gitBlobOid="0" * 40), "HERMETIC_ARTIFACT_MISMATCH"),
            (lambda value: value["artifacts"][0].update(bytes=1), "HERMETIC_ARTIFACT_MISMATCH"),
            (lambda value: value["artifacts"][0].update(sha256="0" * 64), "HERMETIC_ARTIFACT_MISMATCH"),
        ):
            hostile = copy.deepcopy(review)
            mutate(hostile)
            with self.subTest(error=error), self.assertRaisesRegex(MODULE.Phase10Error, error):
                self._run_synthetic_git_review(hostile, data)

    def test_07_mlv_network_and_authority_overclaims_are_rejected(self):
        for mutate, error in (
            (lambda review: review["semanticFindings"].update(networkVerified=True), "MLV_NETWORK_OVERCLAIM"),
            (lambda review: review["authority"].update(provider=True), "AUTHORITY_OVERCLAIM"),
        ):
            batch = self._copy()
            mutate(self._review(batch, "mlv-app"))
            with self.subTest(error=error), self.assertRaisesRegex(MODULE.Phase10Error, error):
                MODULE.verify_receipt_shape(batch)

    def test_08_unpersisted_mlv_diagnostic_cannot_gain_artifact_credit(self):
        batch = self._copy()
        diagnostic = self._review(batch, "mlv-app")["unpersistedIndependentReviewDiagnostic"]
        diagnostic["artifactPersisted"] = True
        diagnostic["artifactCredit"] = True
        with self.assertRaisesRegex(MODULE.Phase10Error, "MLV_UNPERSISTED_DIAGNOSTIC_INVALID"):
            MODULE.verify_receipt_shape(batch)

    def test_09_cloudvore_subject_or_artifact_substitution_is_rejected(self):
        review, data = self._synthetic_git_review()
        for mutate, error in (
            (lambda value: value["subject"].update(parent="0" * 40), "HERMETIC_SUBJECT_MISMATCH"),
            (lambda value: value["artifacts"][0].update(bytes=2), "HERMETIC_ARTIFACT_MISMATCH"),
        ):
            hostile = copy.deepcopy(review)
            mutate(hostile)
            with self.subTest(error=error), self.assertRaisesRegex(MODULE.Phase10Error, error):
                self._run_synthetic_git_review(hostile, data)

    def test_10_cloudvore_open_or_installable_overclaims_are_rejected(self):
        cases = (
            lambda review: review["keyBindings"].update(gateState="OPEN"),
            lambda review: review["keyBindings"].update(candidateInstallable=True),
            lambda review: review["semanticFindings"].update(executableInstallerPresent=True),
            lambda review: review["dispositionTreatment"].update(installationCredit=True),
        )
        for mutate in cases:
            batch = self._copy()
            mutate(self._review(batch, "cloudvore"))
            with self.subTest(mutate=mutate), self.assertRaises(MODULE.Phase10Error):
                MODULE.verify_receipt_shape(batch)

    def test_11_r8_manifest_tree_and_critical_tuple_substitutions_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix="phase10-r8-hostile-") as directory:
            root = Path(directory)
            payload = b"x"
            payload_hash = hashlib.sha256(payload).hexdigest().upper()
            (root / "subject.txt").write_bytes(payload)
            manifest = {
                "schema": "dng-candidate-manifest.v7", "candidate": "durable-campaign-hold-latch-r8",
                "status": "FROZEN_AUTHOR_CONFLICTED", "authority": {"apply": False},
                "subjects": [{"path": "subject.txt", "bytes": 1, "sha256": payload_hash}],
                "metadata": [], "static_review_bundles": [{"paths": ["subject.txt"], "bytes": 1}],
                "static_limits": {"subject_max_bytes": 24576, "bundle_max_bytes": 32768, "exact_sum_verifier": "test-static-bundle-sums.ps1"},
            }
            raw = json.dumps(manifest, separators=(",", ":")).encode()
            (root / "manifest.json").write_bytes(raw)
            count, tree_hash = MODULE._r8_tree_hash(root)
            review = {
                "subject": {
                    "localRoot": str(root), "manifestPath": "manifest.json", "manifestBytes": len(raw),
                    "manifestSha256": hashlib.sha256(raw).hexdigest(), "subjectCount": 1,
                    "metadataCount": 0, "staticReviewBundleCount": 1, "largestSubjectBytes": 1,
                    "largestBundleBytes": 1, "treeFileCount": count, "treeSha256": tree_hash,
                },
                "criticalArtifacts": [{"path": "subject.txt", "bytes": 1, "sha256": payload_hash.lower()}],
            }
            MODULE._verify_r8_local(copy.deepcopy(review))
            for mutate, error in (
                (lambda value: value["subject"].update(manifestSha256="0" * 64), "R8_MANIFEST_MISMATCH"),
                (lambda value: value["subject"].update(treeSha256="0" * 64), "R8_TREE_MISMATCH"),
                (lambda value: value["criticalArtifacts"][0].update(bytes=2), "R8_CRITICAL_ARTIFACT_MISMATCH"),
            ):
                hostile = copy.deepcopy(review)
                mutate(hostile)
                with self.subTest(error=error), self.assertRaisesRegex(MODULE.Phase10Error, error):
                    MODULE._verify_r8_local(hostile)

    def test_12_r8_suite_preview_and_scope_overclaims_are_rejected(self):
        cases = (
            lambda review: review["independentExecutionEvidence"][0].update(assertionsPerRun=120),
            lambda review: review["productionPreview"].update(afterFingerprintSha256="0" * 64),
            lambda review: review["productionPreview"].update(persistentTargetWrites=1),
            lambda review: review["dispositionTreatment"].update(applyAuthorized=True),
            lambda review: review["authority"].update(privilegedPreview=True),
        )
        for mutate in cases:
            batch = self._copy()
            mutate(self._review(batch, "dng-auto-processor"))
            with self.subTest(mutate=mutate), self.assertRaises(MODULE.Phase10Error):
                MODULE.verify_receipt_shape(batch)

    def test_13_coordinated_boolean_integer_type_aliases_fail_closed(self):
        batch = self._copy()
        batch["capture"]["networkInspectionPerformed"] = 0
        batch["summary"]["ledgerStatusChangesAuthorized"] = False
        mlv = self._review(batch, "mlv-app")
        mlv["authority"]["provider"] = 0
        mlv["unpersistedIndependentReviewDiagnostic"]["artifactCredit"] = 0
        cloud = self._review(batch, "cloudvore")
        cloud["keyBindings"]["candidateInstallable"] = 0
        r8 = self._review(batch, "dng-auto-processor")
        r8["productionPreview"]["persistentTargetWrites"] = False
        with self.assertRaises(MODULE.Phase10Error):
            MODULE.verify_receipt_shape(batch)

    def test_14_ledger_manifest_phase6_receipt_or_spec_drift_is_rejected(self):
        original_oid = MODULE._oid
        for path in (MODULE.LEDGER_PATH, MODULE.MANIFEST_PATH, MODULE.PHASE6_RECEIPT_PATH, "specs/mlv-app.md"):
            with self.subTest(path=path):
                def drift(treeish, candidate_path, target=path):
                    if treeish == self._treeish() and candidate_path == target:
                        return "0" * 40
                    return original_oid(treeish, candidate_path)

                with mock.patch.object(MODULE, "_oid", side_effect=drift):
                    with self.assertRaisesRegex(MODULE.Phase10Error, "(FROZEN_DOCTRINE_ARTIFACT|SPEC_BLOB)_DRIFT"):
                        MODULE.verify_frozen_doctrine(self._treeish())

    def test_15_allowlist_or_workflow_substitution_is_rejected(self):
        path, attribute = next(iter(MODULE.PREDECESSOR_CHECKERS.items()))
        original_assignment = MODULE._assignment_set

        def drift_assignment(treeish, candidate_path, name):
            value = original_assignment(treeish, candidate_path, name)
            if treeish == self._treeish() and candidate_path == path and name == attribute:
                return value | {"src/runtime.py"}
            return value

        with mock.patch.object(MODULE, "_assignment_set", side_effect=drift_assignment):
            with self.assertRaisesRegex(MODULE.Phase10Error, "PREDECESSOR_ALLOWLIST_UNION_MISMATCH"):
                MODULE.verify_forward_allowlists(self._treeish())

        workflow = MODULE._blob(self._treeish(), ".github/workflows/disposition-intake.yml")
        with mock.patch.object(MODULE, "_blob", return_value=workflow.replace(b"test_phase10_integration", b"test_phaseXX_integration")):
            with self.assertRaisesRegex(MODULE.Phase10Error, "WORKFLOW_PHASE10_MISSING"):
                MODULE.verify_workflow(self._treeish())

    def test_16_local_projects_are_explicit_and_output_is_truthful(self):
        MODULE.verify_integration(self._treeish(), verify_local_projects=False)
        with mock.patch.object(MODULE, "verify_local_subjects", side_effect=MODULE.Phase10Error("MLV_ROOT_UNAVAILABLE")):
            self.assertEqual(1, MODULE.main(["--treeish", self._treeish(), "--verify-local-projects"]))
        for enabled, marker in ((False, "LOCAL SUBJECTS NOT REDERIVED"), (True, "LOCAL SUBJECTS REDERIVED")):
            output = io.StringIO()
            with mock.patch.object(MODULE, "verify_integration"), redirect_stdout(output):
                argv = ["--treeish", self._treeish()] + (["--verify-local-projects"] if enabled else [])
                self.assertEqual(0, MODULE.main(argv))
            self.assertIn(marker, output.getvalue())

    def test_17_git_object_indirection_alternates_and_replacements_refuse(self):
        for key in ("GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_REPLACE_REF_BASE", "GIT_CONFIG_COUNT"):
            with self.subTest(key=key), mock.patch.dict(os.environ, {key: "forged"}, clear=False):
                with self.assertRaisesRegex(MODULE.Phase10Error, "GIT_OBJECT_INDIRECTION_REFUSED"):
                    MODULE.verify_git_object_isolation()
        with mock.patch.object(Path, "exists", return_value=True):
            with self.assertRaisesRegex(MODULE.Phase10Error, "GIT_ALTERNATE_OBJECT_STORE_REFUSED"):
                MODULE.verify_git_object_isolation()
        original = MODULE._git
        with mock.patch.object(MODULE, "_git", side_effect=lambda args, **kwargs: "0" * 40 + "\n" if args == ["replace", "-l"] else original(args, **kwargs)):
            with self.assertRaisesRegex(MODULE.Phase10Error, "GIT_REPLACE_OBJECT_REFUSED"):
                MODULE.verify_git_object_isolation()


if __name__ == "__main__":
    unittest.main()
