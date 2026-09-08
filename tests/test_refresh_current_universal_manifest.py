import copy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("refresh_universal", ROOT / "tools/refresh_current_universal_manifest.py")
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="r45-refresh-fixture-")
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "repo"
        self.run_git("clone", "--local", "--no-hardlinks", "--no-checkout", str(ROOT), str(self.repo), cwd=ROOT)
        self.run_git("config", "core.autocrlf", "false")
        self.run_git("config", "user.name", "Manifest fixture")
        self.run_git("config", "user.email", "fixture@example.invalid")
        self.run_git("checkout", "--detach", R.ORIGINAL_PROOF)
        self.original = json.loads((self.repo / R.MANIFEST_PATH).read_bytes())

    def run_git(self, *args, cwd=None):
        result = subprocess.run(["git", "--no-optional-locks", *args], cwd=cwd or self.repo, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        return result.stdout.decode().strip()

    def commit(self, *paths):
        self.run_git("add", "--", *paths)
        self.run_git("-c", "core.hooksPath=/dev/null", "commit", "-m", "Disposable fixture change")
        return self.run_git("rev-parse", "HEAD")

    def test_exact_blob_refresh_is_idempotent_and_preserves_original_proof(self):
        self.assertEqual(R.refreshed_snapshot(self.repo, R.ORIGINAL_PROOF)["manifest"], self.original)
        paths = ["README.md", "specs/fleet-universal-provider-control-reconciliation.md"]
        for path in paths:
            with (self.repo / path).open("ab") as handle:
                handle.write(b"\nFixture documentation clarification.\n")
        candidate = self.commit(*paths)
        before = (self.repo / R.MANIFEST_PATH).read_bytes()
        result = R.refreshed_snapshot(self.repo, candidate)
        self.assertEqual((self.repo / R.MANIFEST_PATH).read_bytes(), before, "generator must not write")
        self.assertEqual(result["changedBindings"], paths)
        self.assertFalse(result["authorityGranted"])
        self.assertEqual(result["originalProofCommit"], R.ORIGINAL_PROOF)
        self.assertEqual(R.claims(result["manifest"]), R.claims(self.original))
        for old, new in zip(self.original["subjectFiles"], result["manifest"]["subjectFiles"], strict=True):
            blob = subprocess.check_output(["git", "show", f"{candidate}:{new['path']}"], cwd=self.repo)
            self.assertEqual(new["sha256"], "sha256:" + hashlib.sha256(blob).hexdigest())
            self.assertEqual(new["bytes"], len(blob))
            self.assertEqual(new["gitBlobOid"], self.run_git("rev-parse", f"{candidate}:{new['path']}"))
            if old["path"] not in paths:
                self.assertEqual(old, new)
        encoded = R.render(result["manifest"])
        self.assertEqual(result["manifest"]["manifestSelf"]["bytes"], len(encoded))
        self.assertEqual(result["manifest"]["manifestSelf"]["canonicalGitBlobSha256"], R.self_digest(encoded))
        (self.repo / R.MANIFEST_PATH).write_bytes(encoded)
        refreshed = self.commit(R.MANIFEST_PATH)
        again = R.refreshed_snapshot(self.repo, refreshed)
        self.assertEqual(again["manifest"], result["manifest"])
        self.assertEqual(again["changedBindings"], [])
        self.assertEqual(json.loads(self.run_git("show", f"{R.ORIGINAL_PROOF}:{R.MANIFEST_PATH}")), self.original)

    def test_claim_path_order_and_policy_mutations_are_refused(self):
        for label in ("path", "order", "authority", "status", "policy", "base", "missing", "boolean_size", "integer_oid"):
            with self.subTest(label=label):
                value = copy.deepcopy(self.original)
                if label == "path":
                    value["subjectFiles"][0]["path"] = "TRAPS.md"
                elif label == "order":
                    value["subjectFiles"].reverse()
                elif label == "authority":
                    value["authority"]["providerExecution"] = True
                elif label == "status":
                    value["status"] = "APPROVED"
                elif label == "policy":
                    value["reviewAdmissionPolicy"]["authority"]["providerExecution"] = True
                elif label == "base":
                    value["candidateBase"]["commit"] = "0" * 40
                elif label == "missing":
                    del value["subjectFiles"][0]["gitBlobOid"]
                elif label == "boolean_size":
                    value["subjectFiles"][0]["bytes"] = True
                else:
                    value["subjectFiles"][0]["gitBlobOid"] = 10 ** 39
                (self.repo / R.MANIFEST_PATH).write_bytes(R.render(value))
                candidate = self.commit(R.MANIFEST_PATH)
                with self.assertRaisesRegex(R.RefreshError, "MANIFEST_CLAIMS_CHANGED"):
                    R.refreshed_snapshot(self.repo, candidate)

    def test_frozen_layer_mutation_is_refused(self):
        path = "manifests/universal-provider-control-reconciliation-r44.json"
        with (self.repo / path).open("ab") as handle:
            handle.write(b"\n")
        candidate = self.commit(path)
        with self.assertRaisesRegex(R.RefreshError, "FROZEN_LAYER_CHANGED"):
            R.refreshed_snapshot(self.repo, candidate)

    def test_noncanonical_manifest_and_self_corruption_are_refused(self):
        path = self.repo / R.MANIFEST_PATH
        path.write_bytes(json.dumps(self.original).encode())
        candidate = self.commit(R.MANIFEST_PATH)
        with self.assertRaisesRegex(R.RefreshError, "NONCANONICAL_MANIFEST"):
            R.refreshed_snapshot(self.repo, candidate)
        value = copy.deepcopy(self.original)
        value["manifestSelf"]["canonicalGitBlobSha256"] = "sha256:" + "0" * 64
        path.write_bytes(R.render(value))
        candidate = self.commit(R.MANIFEST_PATH)
        with self.assertRaisesRegex(R.RefreshError, "SELF_BINDING_INVALID"):
            R.refreshed_snapshot(self.repo, candidate)

    def test_dirty_index_untracked_and_nonexact_candidates_are_refused(self):
        path = self.repo / "README.md"
        path.write_bytes(path.read_bytes() + b"\nfixture\n")
        with self.assertRaisesRegex(R.RefreshError, "DIRTY_OR_AMBIGUOUS_INPUT"):
            R.refreshed_snapshot(self.repo, R.ORIGINAL_PROOF)
        self.run_git("add", "--", "README.md")
        with self.assertRaisesRegex(R.RefreshError, "DIRTY_OR_AMBIGUOUS_INPUT"):
            R.refreshed_snapshot(self.repo, R.ORIGINAL_PROOF)
        candidate = self.commit("README.md")
        (self.repo / "untracked-fixture.txt").write_text("fixture")
        with self.assertRaisesRegex(R.RefreshError, "DIRTY_OR_AMBIGUOUS_INPUT"):
            R.refreshed_snapshot(self.repo, candidate)
        for invalid in ("HEAD", "0" * 40, R.ORIGINAL_PROOF):
            with self.subTest(candidate=invalid), self.assertRaises(R.RefreshError):
                R.refreshed_snapshot(self.repo, invalid)

    def test_missing_subject_and_git_indirection_are_refused(self):
        (self.repo / "README.md").unlink()
        candidate = self.commit("README.md")
        with self.assertRaisesRegex(R.RefreshError, "GIT_OBJECT_OR_COMMAND_UNAVAILABLE"):
            R.refreshed_snapshot(self.repo, candidate)
        common = Path(self.run_git("rev-parse", "--path-format=absolute", "--git-common-dir"))
        (common / "objects/info/alternates").write_text("missing-object-store\n")
        with self.assertRaisesRegex(R.RefreshError, "GIT_OBJECT_INDIRECTION_REFUSED"):
            R.refreshed_snapshot(self.repo, candidate)

    def test_head_move_and_object_environment_refuse_without_output(self):
        original = R.git
        heads = 0
        def moved(repo, *args):
            nonlocal heads
            if args == ("rev-parse", "HEAD"):
                heads += 1
                if heads == 2:
                    return b"0" * 40
            return original(repo, *args)
        with mock.patch.object(R, "git", side_effect=moved), redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()):
            self.assertEqual(R.main(["--repo", str(self.repo), "--candidate", R.ORIGINAL_PROOF]), 1)
        self.assertEqual(output.getvalue(), "")
        with mock.patch.dict(os.environ, {"GIT_INDEX_FILE": "foreign-index"}), self.assertRaisesRegex(R.RefreshError, "GIT_OBJECT_ENV_REFUSED"):
            R.refreshed_snapshot(self.repo, R.ORIGINAL_PROOF)


if __name__ == "__main__":
    unittest.main()
