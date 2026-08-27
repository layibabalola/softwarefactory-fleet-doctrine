import copy
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "check_phase3_disposition_batch.py"
SPEC = importlib.util.spec_from_file_location("check_phase3_disposition_batch", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class RemoteGitStub:
    def __init__(self, candidate):
        self.candidate = copy.deepcopy(candidate)
        self.calls = []
        self.roots = []
        self.blobs = {}
        for artifact in self.candidate["artifacts"]:
            raw = f"stub:{artifact['path']}".encode("utf-8")
            header = f"blob {len(raw)}\0".encode("ascii")
            oid = hashlib.sha1(header + raw).hexdigest()
            artifact.update(
                {
                    "gitBlobOid": oid,
                    "bytes": len(raw),
                    "sha256": hashlib.sha256(raw).hexdigest(),
                }
            )
            self.blobs[artifact["path"]] = (oid, raw)
        self.fetch_head = self.candidate["commit"]
        self.parents = [self.candidate["parent"]]
        self.global_config_bytes = None

    def __call__(
        self,
        args,
        *,
        cwd,
        environment,
        project_id,
        error,
        text=False,
    ):
        self.calls.append((list(args), Path(cwd), dict(environment), project_id, error, text))
        self.roots.append(Path(cwd).parent)
        if self.global_config_bytes is None:
            self.global_config_bytes = Path(environment["GIT_CONFIG_GLOBAL"]).read_bytes()

        def output(value):
            if text:
                return value.decode("utf-8") if isinstance(value, bytes) else value
            return value.encode("utf-8") if isinstance(value, str) else value

        command = args[0]
        if command in {"init", "fetch"}:
            return output(b"")
        if command == "ls-remote":
            return output(
                f"{self.candidate['commit']}\t{self.candidate['publishedRef']}\n"
            )
        if command == "rev-parse":
            return output(f"{self.fetch_head}\n")
        if command == "show":
            return output(f"{self.candidate['tree']}\n{' '.join(self.parents)}\n")
        if command == "merge-base":
            if args[-2:] != [self.candidate["baseCommit"], self.candidate["commit"]]:
                raise MODULE.Phase3Error(f"{error}:{project_id}")
            return output(b"")
        if command == "ls-tree":
            path = args[-1]
            if path not in self.blobs:
                raise MODULE.Phase3Error(f"{error}:{project_id}")
            oid, _ = self.blobs[path]
            return output(f"100644 blob {oid}\t{path}\0".encode("utf-8"))
        if command == "cat-file" and args[1] == "-e":
            if args[2] != f"{self.candidate['baseCommit']}^{{commit}}":
                raise MODULE.Phase3Error(f"{error}:{project_id}")
            return output(b"")
        if command == "cat-file" and args[1] == "-s":
            for oid, raw in self.blobs.values():
                if args[2] == oid:
                    return output(f"{len(raw)}\n")
            raise MODULE.Phase3Error(f"{error}:{project_id}")
        if command == "cat-file" and args[1] == "blob":
            for oid, raw in self.blobs.values():
                if args[2] == oid:
                    return output(raw)
            raise MODULE.Phase3Error(f"{error}:{project_id}")
        raise AssertionError(f"unexpected remote Git command: {args}")


class Phase3DispositionBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = MODULE.load_json(
            (ROOT / "adoption" / "phase3" / "r26-published-project-disposition-intake.json").read_bytes()
        )
        cls.ledger = MODULE.load_json(
            (ROOT / "adoption" / "universal-token-control-r26.json").read_bytes()
        )

    def setUp(self):
        environment = mock.patch.dict(
            MODULE.os.environ, {MODULE.REMOTE_TOKEN_ENV: ""}, clear=False
        )
        environment.start()
        self.addCleanup(environment.stop)

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

    def _ledger_with_candidate(self, project_id, candidate):
        ledger = copy.deepcopy(self.ledger)
        row = next(row for row in ledger["projects"] if row["projectId"] == project_id)
        row["evidence"]["projectCandidate"] = copy.deepcopy(candidate)
        return json.dumps(ledger, separators=(",", ":")).encode("utf-8")

    def _remote_fixture(self, project_id="cloudvore"):
        project = copy.deepcopy(self._project(self.batch, project_id))
        stub = RemoteGitStub(project["projectCandidate"])
        project["projectCandidate"] = copy.deepcopy(stub.candidate)
        return project, stub

    def _verify_with_ledger(self, ledger):
        original_blob = MODULE._blob
        ledger_bytes = json.dumps(ledger, separators=(",", ":")).encode("utf-8")

        def blob_override(treeish, path):
            if treeish == "HEAD" and path == MODULE.LEDGER_PATH:
                return ledger_bytes
            return original_blob(treeish, path)

        with mock.patch.object(MODULE, "_blob", side_effect=blob_override):
            MODULE.verify_batch(self._copy(), "HEAD")

    def test_batch_matches_exact_specs_ledger_and_published_candidate_pins(self):
        MODULE.verify_batch(self._copy(), "HEAD")

    def test_duplicate_json_key_is_rejected(self):
        with self.assertRaisesRegex(MODULE.Phase3Error, "DUPLICATE_KEY"):
            MODULE.load_json(b'{"schema":"a","schema":"b"}')

    def test_published_master_and_forward_spec_commits_are_immutable(self):
        for field in (
            "publishedMasterCommit",
            "initialSpecFoldCommit",
            "specBindingCommit",
            "adversarialSpecBindingCommit",
            "adversarialSpecRepairCommit",
            "utilizationShadowDoctrineBaseCommit",
            "utilizationShadowDoctrineBaseTree",
            "utilizationShadowDoctrineAmendmentCommit",
            "utilizationShadowDoctrineAmendmentTree",
            "utilizationShadowDoctrineAmendmentSpecBlob",
        ):
            with self.subTest(field=field):
                batch = self._copy()
                batch["frozenBase"][field] = "0" * 40
                with self.assertRaisesRegex(MODULE.Phase3Error, "FROZEN_BASE_MISMATCH"):
                    MODULE.verify_batch(batch, "HEAD")

    def test_utilization_shadow_doctrine_base_object_is_exact(self):
        original = MODULE._commit_tuple

        def commit_tuple(commit):
            if commit == MODULE.UTILIZATION_SHADOW_DOCTRINE_BASE_COMMIT:
                return ("0" * 40, [])
            return original(commit)

        with mock.patch.object(MODULE, "_commit_tuple", side_effect=commit_tuple):
            with self.assertRaisesRegex(
                MODULE.Phase3Error,
                "UTILIZATION_SHADOW_DOCTRINE_BASE_OBJECT_MISMATCH",
            ):
                MODULE.verify_batch(self._copy(), "HEAD")

    def test_utilization_shadow_doctrine_amendment_object_and_parent_are_exact(self):
        original = MODULE._commit_tuple

        def commit_tuple(commit):
            if commit == MODULE.UTILIZATION_SHADOW_DOCTRINE_AMENDMENT_COMMIT:
                return (MODULE.UTILIZATION_SHADOW_DOCTRINE_AMENDMENT_TREE, [])
            return original(commit)

        with mock.patch.object(MODULE, "_commit_tuple", side_effect=commit_tuple):
            with self.assertRaisesRegex(
                MODULE.Phase3Error,
                "UTILIZATION_SHADOW_DOCTRINE_AMENDMENT_OBJECT_MISMATCH",
            ):
                MODULE.verify_batch(self._copy(), "HEAD")

    def test_utilization_shadow_doctrine_amendment_scope_is_spec_only(self):
        original = MODULE._changed_paths

        def changed_paths(base, treeish):
            if (base, treeish) == (
                MODULE.UTILIZATION_SHADOW_DOCTRINE_BASE_COMMIT,
                MODULE.UTILIZATION_SHADOW_DOCTRINE_AMENDMENT_COMMIT,
            ):
                return {"specs/adversarialllm.md", "src/runtime.py"}
            return original(base, treeish)

        with mock.patch.object(MODULE, "_changed_paths", side_effect=changed_paths):
            with self.assertRaisesRegex(
                MODULE.Phase3Error,
                "UTILIZATION_SHADOW_DOCTRINE_AMENDMENT_SCOPE_INVALID",
            ):
                MODULE.verify_batch(self._copy(), "HEAD")

    def test_utilization_shadow_doctrine_amended_spec_blob_is_exact(self):
        original = MODULE._oid

        def oid(treeish, path):
            if (
                treeish == MODULE.UTILIZATION_SHADOW_DOCTRINE_AMENDMENT_COMMIT
                and path == "specs/adversarialllm.md"
            ):
                return "0" * 40
            return original(treeish, path)

        with mock.patch.object(MODULE, "_oid", side_effect=oid):
            with self.assertRaisesRegex(
                MODULE.Phase3Error,
                "UTILIZATION_SHADOW_DOCTRINE_AMENDMENT_SPEC_MISMATCH",
            ):
                MODULE.verify_batch(self._copy(), "HEAD")

    def test_utilization_shadow_doctrine_amendment_must_be_ancestor(self):
        original = MODULE._is_ancestor

        def is_ancestor(ancestor, descendant):
            if ancestor == MODULE.UTILIZATION_SHADOW_DOCTRINE_AMENDMENT_COMMIT:
                return False
            return original(ancestor, descendant)

        with mock.patch.object(MODULE, "_is_ancestor", side_effect=is_ancestor):
            with self.assertRaisesRegex(
                MODULE.Phase3Error,
                "UTILIZATION_SHADOW_DOCTRINE_AMENDMENT_NOT_ANCESTOR",
            ):
                MODULE.verify_batch(self._copy(), "HEAD")

    def test_exact_four_project_closed_set_is_required(self):
        batch = self._copy()
        batch["projects"].pop()
        with self.assertRaisesRegex(MODULE.Phase3Error, "PROJECT_SET_INVALID"):
            MODULE.verify_batch(batch, "HEAD")

        batch = self._copy()
        batch["projects"].append(copy.deepcopy(batch["projects"][0]))
        with self.assertRaisesRegex(MODULE.Phase3Error, "PROJECT_SET_INVALID"):
            MODULE.verify_batch(batch, "HEAD")

    def test_ledger_rows_are_unique_closed_set_and_all_nine_migrated(self):
        self.assertEqual(9, len(self.ledger["projects"]))
        for row in self.ledger["projects"]:
            candidate = row["evidence"]["projectCandidate"]
            self.assertEqual(row["projectId"] in MODULE.PROJECT_IDS, candidate is not None)

        ledger = copy.deepcopy(self.ledger)
        ledger["projects"][-1] = copy.deepcopy(ledger["projects"][0])
        with self.assertRaisesRegex(MODULE.Phase3Error, "LEDGER_PROJECT_SET_INVALID"):
            self._verify_with_ledger(ledger)

        ledger = copy.deepcopy(self.ledger)
        del ledger["projects"][0]["evidence"]["projectCandidate"]
        with self.assertRaisesRegex(
            MODULE.Phase3Error, "LEDGER_PROJECT_CANDIDATE_MIGRATION_INVALID"
        ):
            self._verify_with_ledger(ledger)

        ledger = copy.deepcopy(self.ledger)
        ledger["projects"][0]["evidence"]["projectCandidate"] = copy.deepcopy(
            self._project(self.batch, "cloudvore")["projectCandidate"]
        )
        with self.assertRaisesRegex(
            MODULE.Phase3Error, "LEDGER_PROJECT_CANDIDATE_MIGRATION_INVALID"
        ):
            self._verify_with_ledger(ledger)

    def test_ledger_census_type_failure_has_stable_error(self):
        ledger = copy.deepcopy(self.ledger)
        ledger["census"] = []
        with self.assertRaisesRegex(MODULE.Phase3Error, "LEDGER_CENSUS_INVALID"):
            self._verify_with_ledger(ledger)

    def test_ledger_census_must_match_current_exact_census_commit(self):
        ledger = copy.deepcopy(self.ledger)
        ledger["census"]["baseCommit"] = MODULE.UTILIZATION_SHADOW_DOCTRINE_AMENDMENT_COMMIT
        with self.assertRaisesRegex(MODULE.Phase3Error, "LEDGER_CENSUS_BASE_MISMATCH"):
            self._verify_with_ledger(ledger)

    def test_central_spec_commit_and_blob_are_exact(self):
        batch = self._copy()
        self._project(batch, "cloudvore")["centralEvidence"]["gitBlobOid"] = "0" * 40
        with self.assertRaisesRegex(MODULE.Phase3Error, "CENTRAL_EVIDENCE_MISMATCH"):
            MODULE.verify_batch(batch, "HEAD")

    def test_intake_only_candidate_substitution_cannot_diverge_from_ledger(self):
        batch = self._copy()
        self._project(batch, "mlv-app")["projectCandidate"]["commit"] = "0" * 40
        with self.assertRaisesRegex(MODULE.Phase3Error, "INTAKE_LEDGER_CANDIDATE_MISMATCH"):
            MODULE.verify_batch(batch, "HEAD")

    def test_coordinated_intake_and_ledger_commit_tree_or_artifact_substitution_fails(self):
        cases = (
            ("commit", lambda candidate: candidate.__setitem__("commit", "0" * 40)),
            ("tree", lambda candidate: candidate.__setitem__("tree", "1" * 40)),
            (
                "artifact",
                lambda candidate: candidate["artifacts"][0].update(
                    {"gitBlobOid": "2" * 40, "bytes": 1, "sha256": "3" * 64}
                ),
            ),
        )
        original_blob = MODULE._blob
        for name, mutate in cases:
            with self.subTest(name=name):
                batch = self._copy()
                candidate = self._project(batch, "salesforce-tools")["projectCandidate"]
                mutate(candidate)
                ledger_bytes = self._ledger_with_candidate("salesforce-tools", candidate)

                def blob_override(treeish, path):
                    if treeish == "HEAD" and path == MODULE.LEDGER_PATH:
                        return ledger_bytes
                    return original_blob(treeish, path)

                with mock.patch.object(MODULE, "_blob", side_effect=blob_override):
                    with self.assertRaisesRegex(
                        MODULE.Phase3Error, "PROJECT_CANDIDATE_EXACT_BINDING_MISMATCH"
                    ):
                        MODULE.verify_batch(batch, "HEAD")

    def test_coordinated_disposition_statement_substitution_fails_frozen_digest(self):
        batch = self._copy()
        project = self._project(batch, "cloudvore")
        candidate = project["projectCandidate"]
        old_statement = candidate["disposition"]["statement"]
        new_statement = old_statement.replace("CLOUDVORE_R26", "CLOUDVORE_FABRICATED_R26")
        candidate["disposition"]["statement"] = new_statement
        ledger_bytes = self._ledger_with_candidate("cloudvore", candidate)
        original_blob = MODULE._blob
        original_spec = original_blob(MODULE.SPEC_BINDING_COMMIT, project["specPath"])
        coordinated_spec = original_spec.replace(
            old_statement.encode("utf-8"), new_statement.encode("utf-8")
        )

        def blob_override(treeish, path):
            if treeish == "HEAD" and path == MODULE.LEDGER_PATH:
                return ledger_bytes
            if treeish == MODULE.SPEC_BINDING_COMMIT and path == project["specPath"]:
                return coordinated_spec
            return original_blob(treeish, path)

        with mock.patch.object(MODULE, "_blob", side_effect=blob_override):
            with self.assertRaisesRegex(
                MODULE.Phase3Error, "PROJECT_CANDIDATE_EXACT_BINDING_MISMATCH"
            ):
                MODULE.verify_batch(batch, "HEAD")

    def test_recursive_adoption_and_authority_overclaims_are_rejected(self):
        project = copy.deepcopy(self._project(self.batch, "mlv-app"))
        candidate = project["projectCandidate"]
        candidate["disposition"]["statement"] += " ADOPT(0000000000000000000000000000000000000000)"
        ledger_rows = {
            row["projectId"]: copy.deepcopy(row) for row in self.ledger["projects"]
        }
        ledger_rows["mlv-app"]["evidence"]["projectCandidate"] = copy.deepcopy(candidate)
        with self.assertRaisesRegex(MODULE.Phase3Error, "PROJECT_CANDIDATE_ADOPTION_OVERCLAIM"):
            MODULE._verify_project(project, ledger_rows=ledger_rows, treeish="HEAD")

        project = copy.deepcopy(self._project(self.batch, "mlv-app"))
        candidate = project["projectCandidate"]
        candidate["authorityClaims"]["runtimeActivation"] = True
        ledger_rows = {
            row["projectId"]: copy.deepcopy(row) for row in self.ledger["projects"]
        }
        ledger_rows["mlv-app"]["evidence"]["projectCandidate"] = copy.deepcopy(candidate)
        with self.assertRaisesRegex(MODULE.Phase3Error, "PROJECT_CANDIDATE_AUTHORITY_OVERCLAIM"):
            MODULE._verify_project(project, ledger_rows=ledger_rows, treeish="HEAD")

    def test_remote_verifier_uses_bounded_noninteractive_temp_repo_and_cleans_it(self):
        project, stub = self._remote_fixture()
        with mock.patch.object(MODULE, "_run_remote_git", side_effect=stub):
            MODULE._verify_remote_project(project)

        self.assertTrue(stub.calls)
        self.assertTrue(all(not root.exists() for root in set(stub.roots)))
        for _, _, environment, _, _, _ in stub.calls:
            self.assertEqual("0", environment["GIT_TERMINAL_PROMPT"])
            self.assertEqual("Never", environment["GCM_INTERACTIVE"])
            self.assertEqual(environment["GIT_ASKPASS"], environment["SSH_ASKPASS"])
            self.assertIn(MODULE.REMOTE_TEMP_PREFIX, environment["GIT_ASKPASS"])
            self.assertEqual("force", environment["SSH_ASKPASS_REQUIRE"])
            self.assertEqual("1", environment["GIT_CONFIG_NOSYSTEM"])
            self.assertEqual("0", environment["GIT_CONFIG_COUNT"])
            self.assertIn(MODULE.REMOTE_TEMP_PREFIX, environment["GIT_CONFIG_GLOBAL"])
        expected_config = (
            b"[http]\n\tsslBackend = schannel\n[credential]\n\thelper = manager\n"
            if MODULE.os.name == "nt"
            else b"# intentionally empty\n"
        )
        self.assertEqual(expected_config, stub.global_config_bytes)
        fetch = next(args for args, *_ in stub.calls if args[0] == "fetch")
        self.assertIn("--no-tags", fetch)
        self.assertIn("--no-recurse-submodules", fetch)
        self.assertEqual(str(MODULE.REMOTE_FETCH_DEPTH), fetch[fetch.index("--depth") + 1])
        self.assertIn("--", fetch)
        ls_tree_calls = [args for args, *_ in stub.calls if args[0] == "ls-tree"]
        self.assertTrue(ls_tree_calls)
        self.assertTrue(all("--" in args for args in ls_tree_calls))

    def test_explicit_ci_token_is_temp_config_only_and_never_child_environment(self):
        project, stub = self._remote_fixture("salesforce-tools")
        token = "github_pat_0123456789ABCDEFGHIJKLMNOP"
        with (
            mock.patch.dict(MODULE.os.environ, {MODULE.REMOTE_TOKEN_ENV: token}, clear=False),
            mock.patch.object(MODULE, "_run_remote_git", side_effect=stub),
        ):
            MODULE._verify_remote_project(project)
        self.assertNotIn(token.encode("ascii"), stub.global_config_bytes)
        expected_basic = MODULE.base64.b64encode(f"x-access-token:{token}".encode("ascii"))
        self.assertIn(expected_basic, stub.global_config_bytes)
        self.assertNotIn(b"helper = manager", stub.global_config_bytes)
        self.assertTrue(
            all(MODULE.REMOTE_TOKEN_ENV not in environment for _, _, environment, *_ in stub.calls)
        )

        project, _ = self._remote_fixture("salesforce-tools")
        with mock.patch.dict(
            MODULE.os.environ, {MODULE.REMOTE_TOKEN_ENV: "invalid\ntoken"}, clear=False
        ):
            with self.assertRaisesRegex(
                MODULE.Phase3Error, "PUBLISHED_REMOTE_AUTH_TOKEN_INVALID"
            ):
                MODULE._verify_remote_project(project)

    def test_remote_url_and_ref_are_exact_allowlisted(self):
        for field, value in (
            ("remote", "https://github.com/example/Cloudvore.git"),
            ("publishedRef", "refs/heads/main"),
        ):
            with self.subTest(field=field):
                project, _ = self._remote_fixture()
                project["projectCandidate"][field] = value
                with self.assertRaisesRegex(
                    MODULE.Phase3Error, "PUBLISHED_REMOTE_URL_REF_NOT_ALLOWLISTED:cloudvore"
                ):
                    MODULE._verify_remote_project(project)

    def test_remote_entrypoint_rechecks_frozen_candidate_digest_before_network(self):
        batch = self._copy()
        self._project(batch, "cloudvore")["projectCandidate"]["commit"] = "0" * 40
        with mock.patch.object(MODULE, "_verify_remote_project") as remote_project:
            with self.assertRaisesRegex(
                MODULE.Phase3Error,
                "PUBLISHED_REMOTE_CANDIDATE_EXACT_BINDING_MISMATCH:cloudvore",
            ):
                MODULE.verify_remotes(batch)
        remote_project.assert_not_called()

    def test_remote_commit_fetch_tree_parent_and_base_mutations_fail_exactly(self):
        cases = (
            (
                "commit",
                lambda project, stub: project["projectCandidate"].__setitem__("commit", "0" * 40),
                "PUBLISHED_REMOTE_REF_MISMATCH:cloudvore",
            ),
            (
                "fetch-head",
                lambda project, stub: setattr(stub, "fetch_head", "1" * 40),
                "PUBLISHED_REMOTE_FETCH_HEAD_MISMATCH:cloudvore",
            ),
            (
                "tree",
                lambda project, stub: project["projectCandidate"].__setitem__("tree", "2" * 40),
                "PUBLISHED_REMOTE_TREE_MISMATCH:cloudvore",
            ),
            (
                "parent",
                lambda project, stub: project["projectCandidate"].__setitem__("parent", "3" * 40),
                "PUBLISHED_REMOTE_PARENT_MISMATCH:cloudvore",
            ),
            (
                "parent-count",
                lambda project, stub: setattr(stub, "parents", []),
                "PUBLISHED_REMOTE_PARENT_COUNT_INVALID:cloudvore",
            ),
            (
                "base",
                lambda project, stub: project["projectCandidate"].__setitem__("baseCommit", "4" * 40),
                "PUBLISHED_REMOTE_BASE_UNAVAILABLE:cloudvore",
            ),
        )
        for name, mutate, error in cases:
            with self.subTest(name=name):
                project, stub = self._remote_fixture()
                mutate(project, stub)
                with mock.patch.object(MODULE, "_run_remote_git", side_effect=stub):
                    with self.assertRaisesRegex(MODULE.Phase3Error, error):
                        MODULE._verify_remote_project(project)
                self.assertTrue(all(not root.exists() for root in set(stub.roots)))

    def test_remote_artifact_blob_byte_sha_and_path_mutations_fail_exactly(self):
        cases = (
            ("path", {"path": "fabricated/path.json"}, "PUBLISHED_REMOTE_ARTIFACT_LOOKUP_FAILED"),
            ("blob", {"gitBlobOid": "5" * 40}, "PUBLISHED_REMOTE_ARTIFACT_BLOB_MISMATCH"),
            ("bytes", {"bytes": 999}, "PUBLISHED_REMOTE_ARTIFACT_BYTE_MISMATCH"),
            ("sha", {"sha256": "6" * 64}, "PUBLISHED_REMOTE_ARTIFACT_SHA256_MISMATCH"),
        )
        for name, changes, error in cases:
            with self.subTest(name=name):
                project, stub = self._remote_fixture("salesforce-tools")
                project["projectCandidate"]["artifacts"][0].update(changes)
                with mock.patch.object(MODULE, "_run_remote_git", side_effect=stub):
                    with self.assertRaisesRegex(MODULE.Phase3Error, f"{error}:salesforce-tools"):
                        MODULE._verify_remote_project(project)

    def test_remote_git_timeout_and_execution_failure_have_stable_errors(self):
        with mock.patch.dict(
            MODULE.os.environ,
            {
                "GIT_DIR": "hostile-object-store",
                "GIT_CONFIG_PARAMETERS": "'url.hostile.insteadOf=https://github.com/'",
                "GCM_INTERACTIVE": "Always",
            },
        ):
            environment = MODULE._remote_environment(
                Path("deny-askpass"), Path("empty-gitconfig")
            )
        self.assertNotIn("GIT_DIR", environment)
        self.assertNotIn("GIT_CONFIG_PARAMETERS", environment)
        self.assertEqual("Never", environment["GCM_INTERACTIVE"])
        with mock.patch.object(
            MODULE.subprocess,
            "run",
            side_effect=subprocess.TimeoutExpired(["git", "fetch"], 60),
        ):
            with self.assertRaisesRegex(
                MODULE.Phase3Error, "PUBLISHED_REMOTE_GIT_TIMEOUT:cloudvore"
            ):
                MODULE._run_remote_git(
                    ["fetch"],
                    cwd=ROOT,
                    environment=environment,
                    project_id="cloudvore",
                    error="PUBLISHED_REMOTE_FETCH_FAILED",
                )

        with mock.patch.object(MODULE.subprocess, "run", side_effect=OSError("missing git")):
            with self.assertRaisesRegex(
                MODULE.Phase3Error, "PUBLISHED_REMOTE_GIT_EXECUTION_FAILED:cloudvore"
            ):
                MODULE._run_remote_git(
                    ["fetch"],
                    cwd=ROOT,
                    environment=environment,
                    project_id="cloudvore",
                    error="PUBLISHED_REMOTE_FETCH_FAILED",
                )

    def test_main_distinguishes_local_only_from_remote_verified_success(self):
        batch_bytes = json.dumps(self.batch).encode("utf-8")
        with (
            mock.patch.object(MODULE, "_blob", return_value=batch_bytes),
            mock.patch.object(MODULE, "verify_batch"),
            mock.patch.object(MODULE, "verify_remotes") as remote_verifier,
            mock.patch.dict(os.environ, {"R26_SCOPE_EVENT": "workflow_dispatch", "R26_SCOPE_BASE_SHA": ""}, clear=False),
        ):
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(0, MODULE.main(["--treeish", MODULE.FROZEN_PUBLICATION]))
            self.assertIn("PASS LOCAL-ONLY", output.getvalue())
            self.assertIn("REMOTES NOT VERIFIED", output.getvalue())
            remote_verifier.assert_not_called()

            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(
                    0,
                    MODULE.main(["--treeish", MODULE.FROZEN_PUBLICATION, "--verify-remotes"]),
                )
            self.assertIn("REMOTES VERIFIED", output.getvalue())
            self.assertNotIn("REMOTES NOT VERIFIED", output.getvalue())
            remote_verifier.assert_called_once()

    def test_publishing_workflow_requires_remote_object_verification(self):
        workflow = (ROOT / ".github" / "workflows" / "disposition-intake.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            f"python tools/check_phase3_disposition_batch.py --treeish {MODULE.FROZEN_PUBLICATION}",
            workflow,
        )
        self.assertIn("'--verify-remotes'", workflow)
        self.assertIn(
            'python -m unittest discover -s tests -p "test_adversarialllm_utilization_shadow_doctrine.py" -v',
            workflow,
        )
        self.assertIn(
            "R26_REMOTE_AUTH_CONFIGURED: ${{ secrets.R26_CROSS_REPO_READ_TOKEN != '' }}",
            workflow,
        )
        self.assertEqual(
            2,
            workflow.count(
                "R26_REMOTE_GITHUB_TOKEN: ${{ secrets.R26_CROSS_REPO_READ_TOKEN }}"
            ),
        )
        self.assertIn("env.R26_REMOTE_AUTH_CONFIGURED == 'true'", workflow)
        self.assertIn("if: env.R26_REMOTE_AUTH_CONFIGURED != 'true'", workflow)
        self.assertIn("REMOTES NOT VERIFIED - R26_CROSS_REPO_READ_TOKEN is not configured", workflow)
        self.assertIn("R26_SCOPE_EVENT: ${{ github.event_name }}", workflow)
        self.assertIn("github.event.pull_request.base.sha", workflow)
        self.assertIn("github.event.before", workflow)

    def test_summary_cannot_claim_adoption_or_runtime_authority(self):
        for field in ("adoptionClaims", "runtimeAuthorityClaims"):
            with self.subTest(field=field):
                batch = self._copy()
                batch["summary"][field] = 1
                with self.assertRaisesRegex(MODULE.Phase3Error, "SUMMARY_OVERCLAIM"):
                    MODULE.verify_batch(batch, "HEAD")

    def test_phase3_event_allowlist_is_spec_free_and_distinct_from_history(self):
        self.assertFalse(any(path.startswith("specs/") for path in MODULE.EVENT_ALLOWED_PHASE3_PATHS))
        self.assertNotEqual(MODULE.ALLOWED_PHASE3_PATHS, MODULE.EVENT_ALLOWED_PHASE3_PATHS)
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
        self.assertEqual(MODULE.COMMON_PHASE_TRIGGER_PATHS | {MODULE.INTAKE_PATH, MODULE.LEDGER_PATH}, MODULE.PHASE3_TRIGGER_PATHS)
        self.assertEqual(
            MODULE.PHASE3_TRIGGER_PATHS | MODULE.AUXILIARY_EVENT_ALLOWED_PATHS,
            MODULE.EVENT_ALLOWED_PHASE3_PATHS,
        )

    def test_phase3_unrelated_r29_provider_delta_is_explicit_na(self):
        changed = {
            "README.md", "RECONCILIATION.md",
            "manifests/universal-provider-control-reconciliation-r29.json",
            "schemas/universal-provider-review-admission-v1.schema.json",
            "specs/fleet-universal-provider-control-reconciliation.md",
            "tests/test_universal_provider_control.py",
            "tools/check_universal_manifest.py", "tools/universal_provider_control.py",
        }
        self.assertEqual(self._event_scope(changed), "N/A_NO_PHASE3_TRIGGER")

    def test_phase3_clean_control_surface_and_owned_data_are_applicable(self):
        self.assertEqual(self._event_scope(MODULE.COMMON_PHASE_TRIGGER_PATHS), "APPLICABLE")
        self.assertEqual(
            self._event_scope(
                MODULE.COMMON_PHASE_TRIGGER_PATHS | MODULE.AUXILIARY_EVENT_ALLOWED_PATHS
            ),
            "APPLICABLE",
        )
        self.assertEqual(self._event_scope({MODULE.INTAKE_PATH, MODULE.LEDGER_PATH}), "APPLICABLE")

    def test_phase3_rejects_every_formerly_allowed_spec_when_mixed(self):
        former_specs = {
            "specs/adversarialllm.md", "specs/cloudvore.md",
            "specs/mlv-app.md", "specs/salesforce-tools.md",
        }
        for path in sorted(former_specs):
            with self.subTest(path=path):
                with self.assertRaisesRegex(MODULE.Phase3Error, "PHASE3_SCOPE_VIOLATION"):
                    self._event_scope({"tools/check_phase3_disposition_batch.py", path})

    def test_phase3_control_deletion_or_change_cannot_hide_foreign_mutation(self):
        for control in (
            ".github/workflows/disposition-intake.yml",
            "tests/test_phase3_disposition_batch.py",
            "tools/check_phase3_disposition_batch.py",
        ):
            with self.subTest(control=control):
                with self.assertRaisesRegex(MODULE.Phase3Error, "PHASE3_SCOPE_VIOLATION"):
                    self._event_scope({control, "src/runtime.py"})

    def test_phase3_carrier_controls_are_na_and_trigger_union_is_bounded(self):
        controls = {"tools/check_universal_manifest.py", "tests/test_universal_provider_control.py"}
        trigger = {".github/workflows/disposition-intake.yml"}
        self.assertEqual(self._event_scope(controls), "N/A_NO_PHASE3_TRIGGER")
        self.assertEqual(self._event_scope(trigger | controls), "APPLICABLE")
        for foreign in ("tools/universal_provider_control.py", "specs/cloudvore.md"):
            with self.subTest(foreign=foreign):
                with self.assertRaisesRegex(MODULE.Phase3Error, "PHASE3_SCOPE_VIOLATION"):
                    self._event_scope(trigger | controls | {foreign})

    def test_phase3_missing_invalid_or_nonancestor_base_fails_closed(self):
        with self.assertRaisesRegex(MODULE.Phase3Error, "PHASE3_SCOPE_EVENT_INVALID"):
            MODULE.evaluate_event_scope("", "", "HEAD")
        for base in ("", "not-a-sha"):
            with self.subTest(base=base):
                with self.assertRaisesRegex(MODULE.Phase3Error, "PHASE3_SCOPE_BASE_INVALID"):
                    MODULE.evaluate_event_scope("pull_request", base, "HEAD")
        with (
            mock.patch.object(MODULE, "_commit_tuple", return_value=("b" * 40, [])),
            mock.patch.object(MODULE, "_is_ancestor", return_value=False),
        ):
            with self.assertRaisesRegex(MODULE.Phase3Error, "PHASE3_SCOPE_BASE_INVALID"):
                MODULE.evaluate_event_scope("push", "a" * 40, "HEAD")

    def test_phase3_workflow_dispatch_is_explicit_na(self):
        self.assertEqual(
            MODULE.evaluate_event_scope("workflow_dispatch", "", "HEAD"),
            "N/A_WORKFLOW_DISPATCH",
        )

    def test_phase3_main_verifies_frozen_evidence_before_event_scope(self):
        with (
            mock.patch.object(
                MODULE,
                "_blob",
                return_value=(ROOT / MODULE.INTAKE_PATH).read_bytes(),
            ),
            mock.patch.object(
                MODULE,
                "verify_batch",
                side_effect=MODULE.Phase3Error("FROZEN_FAIL"),
            ),
            mock.patch.object(MODULE, "evaluate_event_scope") as scope,
            mock.patch.dict(os.environ, {"R26_SCOPE_EVENT": "workflow_dispatch", "R26_SCOPE_BASE_SHA": ""}, clear=False),
        ):
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                self.assertEqual(1, MODULE.main(["--treeish", MODULE.FROZEN_PUBLICATION]))
        scope.assert_not_called()
        self.assertIn("FROZEN_FAIL", stderr.getvalue())

    def test_phase3_historical_treeish_cannot_redirect_event_target(self):
        with mock.patch.object(MODULE, "_git", return_value="tools/check_phase3_disposition_batch.py\n") as git:
            self.assertEqual(
                {"tools/check_phase3_disposition_batch.py"},
                MODULE._event_changed_paths("a" * 40, MODULE.FROZEN_PUBLICATION),
            )
        self.assertIn("a" * 40 + "..HEAD", git.call_args.args[0])

    def test_phase3_scope_inputs_are_environment_only(self):
        for option in ("--scope-event", "--scope-base"):
            with self.subTest(option=option), self.assertRaises(SystemExit):
                MODULE.main([option, "workflow_dispatch"])


if __name__ == "__main__":
    unittest.main()
