import copy
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "check_phase6_candidate_reviews.py"
SPEC = importlib.util.spec_from_file_location("check_phase6_candidate_reviews", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class Phase6CandidateReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = MODULE.load_json((ROOT / MODULE.BATCH_PATH).read_bytes())

    def _copy(self):
        return copy.deepcopy(self.batch)

    def _review(self, batch, project_id):
        return next(review for review in batch["reviews"] if review["projectId"] == project_id)

    @staticmethod
    def _fixture_git(root, *args):
        environment = os.environ.copy()
        for key in tuple(environment):
            if key in {
                "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_OBJECT_DIRECTORY",
                "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_REPLACE_REF_BASE", "GIT_INDEX_FILE",
                "GIT_NAMESPACE", "GIT_CEILING_DIRECTORIES", "GIT_EXEC_PATH",
            } or key.startswith("GIT_CONFIG"):
                environment.pop(key, None)
        run = subprocess.run(
            ["git", "-c", "user.name=Phase6 Test", "-c", "user.email=phase6@example.invalid", *args],
            cwd=root,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        if run.returncode != 0:
            raise AssertionError(f"fixture git {' '.join(args)} failed: {run.stderr}")
        return run.stdout.strip()

    def _local_identity_fixture(self, parent, name, branch="reviewed/subject"):
        root = Path(parent) / name
        root.mkdir()
        self._fixture_git(root, "init", f"--initial-branch={branch}")
        self._fixture_git(root, "config", "core.autocrlf", "false")
        (root / "subject.txt").write_text("reviewed subject\n", encoding="utf-8", newline="\n")
        self._fixture_git(root, "add", "--", "subject.txt")
        self._fixture_git(root, "commit", "-m", "reviewed subject")
        commit = self._fixture_git(root, "rev-parse", "HEAD")
        remote = f"https://example.invalid/{name}.git"
        self._fixture_git(root, "remote", "add", "origin", remote)
        subject = {
            "commit": commit,
            "headMode": "SYMBOLIC_BRANCH",
            "localBranch": branch,
            "remote": remote,
            "remoteTrackingRefContainsSubject": False,
            "networkRemoteVerified": False,
        }
        return root, subject

    def test_published_candidate_passes(self):
        MODULE.verify_batch(self._copy(), "HEAD")

    def test_duplicate_json_key_fails_closed(self):
        with self.assertRaisesRegex(MODULE.Phase6Error, "DUPLICATE_KEY"):
            MODULE.load_json(b'{"schema":"one","schema":"two"}')

    def test_frozen_doctrine_base_cannot_move(self):
        batch = self._copy()
        batch["frozenBase"]["doctrineCommit"] = "0" * 40
        with self.assertRaisesRegex(MODULE.Phase6Error, "FROZEN_BASE_MISMATCH"):
            MODULE.verify_batch(batch, "HEAD")

    def test_any_authority_claim_fails_closed(self):
        for project_id in MODULE.EXPECTED:
            with self.subTest(project_id=project_id):
                batch = self._copy()
                self._review(batch, project_id)["authority"]["provider"] = True
                with self.assertRaisesRegex(MODULE.Phase6Error, "AUTHORITY_OVERCLAIM"):
                    MODULE.verify_batch(batch, "HEAD")

    def test_failed_execution_cannot_remain_accept(self):
        batch = self._copy()
        self._review(batch, "salesforce-tools")["executionEvidence"][0]["exitCode"] = 1
        with self.assertRaisesRegex(MODULE.Phase6Error, "EXECUTION_EVIDENCE_INVALID"):
            MODULE.verify_batch(batch, "HEAD")

    def test_salesforce_known_blockers_cannot_be_called_complete(self):
        batch = self._copy()
        self._review(batch, "salesforce-tools")["semanticFindings"][
            "missingAdoptionProofSetComplete"
        ] = True
        with self.assertRaisesRegex(MODULE.Phase6Error, "SEMANTIC_FINDING_INVALID"):
            MODULE.verify_batch(batch, "HEAD")

    def test_salesforce_review_cannot_advance_status_or_adoption(self):
        for field in ("ledgerStatusChangeAuthorized", "adoptionCredit", "installationCredit"):
            with self.subTest(field=field):
                batch = self._copy()
                self._review(batch, "salesforce-tools")["dispositionTreatment"][field] = True
                with self.assertRaisesRegex(MODULE.Phase6Error, "DISPOSITION_TREATMENT_INVALID"):
                    MODULE.verify_batch(batch, "HEAD")

    def test_cloudvore_blocker_cannot_become_a_disposition(self):
        batch = self._copy()
        cloud = self._review(batch, "cloudvore")["dispositionTreatment"]
        cloud["candidateDispositionKind"] = "DISTINGUISH"
        cloud["candidateDisposition"] = "DISTINGUISH(fabricated)"
        with self.assertRaisesRegex(MODULE.Phase6Error, "DISPOSITION_TREATMENT_INVALID"):
            MODULE.verify_batch(batch, "HEAD")

    def test_cloudvore_scanner_cannot_claim_completeness(self):
        batch = self._copy()
        self._review(batch, "cloudvore")["semanticFindings"]["scannerCoverageComplete"] = True
        with self.assertRaisesRegex(MODULE.Phase6Error, "SEMANTIC_FINDING_INVALID"):
            MODULE.verify_batch(batch, "HEAD")

    def test_artifact_drift_fails_closed(self):
        batch = self._copy()
        self._review(batch, "cloudvore")["artifacts"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(MODULE.Phase6Error, "ARTIFACT_BINDING_INVALID"):
            MODULE.verify_batch(batch, "HEAD")

    def test_summary_cannot_claim_a_status_advance(self):
        batch = self._copy()
        batch["summary"]["ledgerStatusChangesAuthorized"] = 1
        with self.assertRaisesRegex(MODULE.Phase6Error, "SUMMARY_INVALID"):
            MODULE.verify_batch(batch, "HEAD")

    def test_receipt_blob_oid_bytes_and_sha_are_exact(self):
        raw = MODULE._blob(ROOT, "HEAD", MODULE.BATCH_PATH)
        probes = (
            ("_oid", "0" * 40, "RECEIPT_BLOB_OID_MISMATCH"),
            ("_blob", raw[:-1], "RECEIPT_BYTES_MISMATCH"),
            ("_blob", raw[:-1] + bytes([raw[-1] ^ 1]), "RECEIPT_SHA256_MISMATCH"),
        )
        for target, value, error in probes:
            with self.subTest(error=error), mock.patch.object(MODULE, target, return_value=value):
                with self.assertRaisesRegex(MODULE.Phase6Error, error):
                    MODULE._verify_receipt_blob("HEAD")

    def test_phase6_lineage_requires_base_ancestry(self):
        with mock.patch.object(
            MODULE,
            "_git",
            side_effect=("a" * 40 + "\n", "b" * 40 + "\n"),
        ):
            with self.assertRaisesRegex(MODULE.Phase6Error, "BASE_NOT_ANCESTOR"):
                MODULE._verify_linear_lineage("HEAD")

    def test_phase6_lineage_rejects_merge_or_nonchain_parent(self):
        child = "a" * 40
        other = "b" * 40
        rows = f"{child} {MODULE.BASE_COMMIT} {other}\n"
        with mock.patch.object(
            MODULE,
            "_git",
            side_effect=(child + "\n", MODULE.BASE_COMMIT + "\n", rows),
        ):
            with self.assertRaisesRegex(MODULE.Phase6Error, "PHASE6_LINEAGE_NOT_SOLE_PARENT"):
                MODULE._verify_linear_lineage("HEAD")

    def test_subject_remote_url_substitution_fails_closed(self):
        batch = self._copy()
        self._review(batch, "salesforce-tools")["subject"]["remote"] = (
            "https://attacker.invalid/substitute.git"
        )
        with self.assertRaisesRegex(MODULE.Phase6Error, "SUBJECT_BINDING_INVALID"):
            MODULE.verify_batch(batch, "HEAD")

    def test_subject_local_branch_substitution_fails_closed(self):
        batch = self._copy()
        self._review(batch, "cloudvore")["subject"]["localBranch"] = "substituted/branch"
        with self.assertRaisesRegex(MODULE.Phase6Error, "SUBJECT_BINDING_INVALID"):
            MODULE.verify_batch(batch, "HEAD")

    def test_execution_command_and_result_substitution_fails_closed(self):
        batch = self._copy()
        self._review(batch, "salesforce-tools")["executionEvidence"][0] = {"exitCode": 0}
        with self.assertRaisesRegex(MODULE.Phase6Error, "EXECUTION_EVIDENCE_INVALID"):
            MODULE.verify_batch(batch, "HEAD")

    def test_next_action_authority_substitution_fails_closed(self):
        batch = self._copy()
        self._review(batch, "cloudvore")["nextLawfulActions"] = [
            "PUBLISH_NOW", "ADOPT_NOW", "OPEN_GATE", "INSTALL_NOW",
        ]
        with self.assertRaisesRegex(MODULE.Phase6Error, "NEXT_ACTIONS_INVALID"):
            MODULE.verify_batch(batch, "HEAD")

    def test_salesforce_full_disposition_is_exact_bound(self):
        batch = self._copy()
        self._review(batch, "salesforce-tools")["dispositionTreatment"][
            "candidateDisposition"
        ] = f"DISTINGUISH({MODULE.R26_MERGE}, FABRICATED)"
        with self.assertRaisesRegex(MODULE.Phase6Error, "DISPOSITION_TREATMENT_INVALID"):
            MODULE.verify_batch(batch, "HEAD")

    def test_recursive_unknown_publication_or_authority_claim_fails_closed(self):
        batch = self._copy()
        self._review(batch, "salesforce-tools")["subject"]["publication"] = {
            "remote": {"published": True}
        }
        with self.assertRaisesRegex(MODULE.Phase6Error, "SUBJECT_BINDING_INVALID"):
            MODULE.verify_batch(batch, "HEAD")

    def test_capture_values_and_keys_are_exact_bound(self):
        batch = self._copy()
        batch["capture"]["networkPublicationVerified"] = True
        with self.assertRaisesRegex(MODULE.Phase6Error, "CAPTURE_BINDING_INVALID"):
            MODULE.verify_batch(batch, "HEAD")

    def test_capture_false_cannot_alias_integer_zero(self):
        batch = self._copy()
        batch["capture"]["networkInspectionPerformed"] = 0
        with self.assertRaisesRegex(MODULE.Phase6Error, "CAPTURE_BINDING_INVALID"):
            MODULE.verify_batch(batch, "HEAD")

    def test_summary_zero_cannot_alias_boolean_false(self):
        batch = self._copy()
        batch["summary"]["adoptionClaims"] = False
        with self.assertRaisesRegex(MODULE.Phase6Error, "SUMMARY_INVALID"):
            MODULE.verify_batch(batch, "HEAD")

    def test_semantic_false_cannot_alias_integer_zero(self):
        batch = self._copy()
        self._review(batch, "salesforce-tools")["semanticFindings"][
            "missingAdoptionProofSetComplete"
        ] = 0
        with self.assertRaisesRegex(MODULE.Phase6Error, "SEMANTIC_FINDING_INVALID"):
            MODULE.verify_batch(batch, "HEAD")

    def test_semantic_true_cannot_alias_integer_one(self):
        batch = self._copy()
        self._review(batch, "salesforce-tools")["semanticFindings"][
            "unobservedLaunchPathsMayExist"
        ] = 1
        with self.assertRaisesRegex(MODULE.Phase6Error, "SEMANTIC_FINDING_INVALID"):
            MODULE.verify_batch(batch, "HEAD")

    def test_execution_zero_cannot_alias_boolean_false(self):
        batch = self._copy()
        self._review(batch, "salesforce-tools")["executionEvidence"][0]["exitCode"] = False
        with self.assertRaisesRegex(MODULE.Phase6Error, "EXECUTION_EVIDENCE_INVALID"):
            MODULE.verify_batch(batch, "HEAD")

    def test_treatment_false_cannot_alias_integer_zero(self):
        batch = self._copy()
        self._review(batch, "salesforce-tools")["dispositionTreatment"]["adoptionCredit"] = 0
        with self.assertRaisesRegex(MODULE.Phase6Error, "DISPOSITION_TREATMENT_INVALID"):
            MODULE.verify_batch(batch, "HEAD")

    def test_coordinated_scalar_aliases_still_fail_closed(self):
        batch = self._copy()
        batch["capture"]["networkInspectionPerformed"] = 0
        batch["summary"]["adoptionClaims"] = False
        batch["summary"]["canonicalLedgerCounts"]["MISSING"] = False
        salesforce = self._review(batch, "salesforce-tools")
        salesforce["semanticFindings"]["missingAdoptionProofSetComplete"] = 0
        salesforce["semanticFindings"]["unobservedLaunchPathsMayExist"] = 1
        salesforce["executionEvidence"][0]["exitCode"] = False
        salesforce["dispositionTreatment"]["adoptionCredit"] = 0
        with self.assertRaisesRegex(MODULE.Phase6Error, "CAPTURE_BINDING_INVALID"):
            MODULE.verify_batch(batch, "HEAD")

    def test_local_identity_rederives_branch_origin_cleanliness_and_remote_refs(self):
        subject = copy.deepcopy(MODULE.EXPECTED["salesforce-tools"]["subject"])
        full_branch = f"refs/heads/{subject['localBranch']}"

        def outputs(overrides=None):
            values = {
                ("rev-parse", "--show-toplevel"): str(ROOT.resolve()) + "\n",
                ("rev-parse", "--is-inside-work-tree"): "true\n",
                ("symbolic-ref", "--quiet", "HEAD"): full_branch + "\n",
                ("rev-parse", "--verify", "HEAD^{commit}"): subject["commit"] + "\n",
                ("rev-parse", "--verify", f"{full_branch}^{{commit}}"): subject["commit"] + "\n",
                ("remote", "get-url", "--all", "origin"): subject["remote"] + "\n",
                ("remote", "get-url", "--push", "--all", "origin"): subject["remote"] + "\n",
                ("status", "--porcelain=v1", "--untracked-files=all"): "",
                (
                    "for-each-ref",
                    f"--contains={subject['commit']}",
                    "--format=%(refname)",
                    "refs/remotes",
                ): "",
            }
            values.update(overrides or {})

            def fake_git(root, *args, text=False):
                del root, text
                return values[args]

            return fake_git

        with mock.patch.object(MODULE, "_git", side_effect=outputs()) as git_call:
            MODULE._verify_local_identity(ROOT, "salesforce-tools", subject)
            self.assertEqual(
                [call.args[1:] for call in git_call.call_args_list],
                [
                    ("rev-parse", "--show-toplevel"),
                    ("rev-parse", "--is-inside-work-tree"),
                    ("symbolic-ref", "--quiet", "HEAD"),
                    ("rev-parse", "--verify", "HEAD^{commit}"),
                    ("rev-parse", "--verify", f"{full_branch}^{{commit}}"),
                    ("remote", "get-url", "--all", "origin"),
                    ("remote", "get-url", "--push", "--all", "origin"),
                    ("status", "--porcelain=v1", "--untracked-files=all"),
                    (
                        "for-each-ref",
                        f"--contains={subject['commit']}",
                        "--format=%(refname)",
                        "refs/remotes",
                    ),
                ],
            )

        failures = (
            (
                {("symbolic-ref", "--quiet", "HEAD"): "refs/heads/substituted/branch\n"},
                "LOCAL_BRANCH_MISMATCH",
            ),
            (
                {("rev-parse", "--verify", "HEAD^{commit}"): "0" * 40 + "\n"},
                "LOCAL_HEAD_MISMATCH",
            ),
            (
                {
                    ("rev-parse", "--verify", f"{full_branch}^{{commit}}"): "1" * 40 + "\n"
                },
                "LOCAL_BRANCH_TIP_MISMATCH",
            ),
            (
                {("remote", "get-url", "--all", "origin"): "https://attacker.invalid/repo.git\n"},
                "LOCAL_ORIGIN_MISMATCH",
            ),
            (
                {("status", "--porcelain=v1", "--untracked-files=all"): "?? unexpected.txt\n"},
                "LOCAL_WORKTREE_NOT_CLEAN",
            ),
            (
                {
                    (
                        "for-each-ref",
                        f"--contains={subject['commit']}",
                        "--format=%(refname)",
                        "refs/remotes",
                    ): "refs/remotes/origin/published\n"
                },
                "LOCAL_REMOTE_TRACKING_CONTAINMENT_MISMATCH",
            ),
        )
        for override, error in failures:
            with self.subTest(error=error), mock.patch.object(
                MODULE, "_git", side_effect=outputs(override)
            ):
                with self.assertRaisesRegex(MODULE.Phase6Error, error):
                    MODULE._verify_local_identity(ROOT, "salesforce-tools", subject)

        overclaim = copy.deepcopy(subject)
        overclaim["networkRemoteVerified"] = True
        with mock.patch.object(MODULE, "_git", side_effect=outputs()):
            with self.assertRaisesRegex(MODULE.Phase6Error, "NETWORK_REMOTE_VERIFICATION_OVERCLAIM"):
                MODULE._verify_local_identity(ROOT, "salesforce-tools", overclaim)

    def test_local_identity_rejects_same_named_branch_moved_past_subject(self):
        with tempfile.TemporaryDirectory(prefix="phase6-branch-move-") as temp:
            root, subject = self._local_identity_fixture(temp, "branch-moved")
            (root / "subject.txt").write_text("moved branch\n", encoding="utf-8", newline="\n")
            self._fixture_git(root, "add", "--", "subject.txt")
            self._fixture_git(root, "commit", "-m", "move branch")
            with self.assertRaisesRegex(MODULE.Phase6Error, "LOCAL_HEAD_MISMATCH"):
                MODULE._verify_local_identity(root, "salesforce-tools", subject)

    def test_local_identity_ignores_git_dir_redirection(self):
        with tempfile.TemporaryDirectory(prefix="phase6-git-dir-") as temp:
            expected_root, subject = self._local_identity_fixture(temp, "expected")
            attacker_root, _ = self._local_identity_fixture(temp, "attacker", "attacker/branch")
            with mock.patch.dict(os.environ, {"GIT_DIR": str(attacker_root / ".git")}):
                MODULE._verify_local_identity(expected_root, "salesforce-tools", subject)

    def test_local_identity_ignores_git_work_tree_redirection(self):
        with tempfile.TemporaryDirectory(prefix="phase6-git-work-tree-") as temp:
            expected_root, subject = self._local_identity_fixture(temp, "expected")
            attacker_root, _ = self._local_identity_fixture(temp, "attacker", "attacker/branch")
            with mock.patch.dict(os.environ, {"GIT_WORK_TREE": str(attacker_root)}):
                MODULE._verify_local_identity(expected_root, "salesforce-tools", subject)

    def test_scope_rejects_ledger_or_spec_mutation(self):
        ledger_raw = MODULE._blob(ROOT, "HEAD", MODULE.LEDGER_PATH)
        with (
            mock.patch.object(
                MODULE, "_tuple", return_value=(MODULE.BASE_TREE, [MODULE.BASE_PARENT])
            ),
            mock.patch.object(MODULE, "_verify_linear_lineage"),
            mock.patch.object(MODULE, "_verify_receipt_blob"),
            mock.patch.object(MODULE, "_oid", return_value=MODULE.LEDGER_BLOB),
            mock.patch.object(MODULE, "_blob", return_value=ledger_raw),
            mock.patch.object(MODULE, "_git", return_value="specs/cloudvore.md\n"),
        ):
            with self.assertRaisesRegex(MODULE.Phase6Error, "PHASE6_SCOPE_VIOLATION"):
                MODULE._verify_base(self._copy(), "HEAD")


if __name__ == "__main__":
    unittest.main()
