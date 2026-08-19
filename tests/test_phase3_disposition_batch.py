import copy
import importlib.util
import json
from pathlib import Path
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


class Phase3DispositionBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = MODULE.load_json(
            (ROOT / "adoption" / "phase3" / "r26-published-project-disposition-intake.json").read_bytes()
        )
        cls.ledger = MODULE.load_json(
            (ROOT / "adoption" / "universal-token-control-r26.json").read_bytes()
        )

    def _copy(self):
        return copy.deepcopy(self.batch)

    def _project(self, batch, project_id):
        return next(project for project in batch["projects"] if project["projectId"] == project_id)

    def _ledger_with_candidate(self, project_id, candidate):
        ledger = copy.deepcopy(self.ledger)
        row = next(row for row in ledger["projects"] if row["projectId"] == project_id)
        row["evidence"]["projectCandidate"] = copy.deepcopy(candidate)
        return json.dumps(ledger, separators=(",", ":")).encode("utf-8")

    def test_batch_matches_exact_specs_ledger_and_published_candidate_pins(self):
        MODULE.verify_batch(self._copy(), "HEAD")

    def test_duplicate_json_key_is_rejected(self):
        with self.assertRaisesRegex(MODULE.Phase3Error, "DUPLICATE_KEY"):
            MODULE.load_json(b'{"schema":"a","schema":"b"}')

    def test_published_master_and_forward_spec_commits_are_immutable(self):
        for field in ("publishedMasterCommit", "initialSpecFoldCommit", "specBindingCommit"):
            with self.subTest(field=field):
                batch = self._copy()
                batch["frozenBase"][field] = "0" * 40
                with self.assertRaisesRegex(MODULE.Phase3Error, "FROZEN_BASE_MISMATCH"):
                    MODULE.verify_batch(batch, "HEAD")

    def test_exact_three_project_closed_set_is_required(self):
        batch = self._copy()
        batch["projects"].pop()
        with self.assertRaisesRegex(MODULE.Phase3Error, "PROJECT_SET_INVALID"):
            MODULE.verify_batch(batch, "HEAD")

        batch = self._copy()
        batch["projects"].append(copy.deepcopy(batch["projects"][0]))
        with self.assertRaisesRegex(MODULE.Phase3Error, "PROJECT_SET_INVALID"):
            MODULE.verify_batch(batch, "HEAD")

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

    def test_summary_cannot_claim_adoption_or_runtime_authority(self):
        for field in ("adoptionClaims", "runtimeAuthorityClaims"):
            with self.subTest(field=field):
                batch = self._copy()
                batch["summary"][field] = 1
                with self.assertRaisesRegex(MODULE.Phase3Error, "SUMMARY_OVERCLAIM"):
                    MODULE.verify_batch(batch, "HEAD")

    def test_phase3_scope_rejects_product_or_unrelated_doctrine_mutation(self):
        def changed_paths(base, treeish):
            if (base, treeish) == (MODULE.MASTER_COMMIT, MODULE.INITIAL_FOLD_COMMIT):
                return set(MODULE.SPEC_PATHS)
            if (base, treeish) == (MODULE.INITIAL_FOLD_COMMIT, MODULE.SPEC_BINDING_COMMIT):
                return set(MODULE.SPEC_PATHS)
            return {"src/runtime.py"}

        with mock.patch.object(MODULE, "_changed_paths", side_effect=changed_paths):
            with self.assertRaisesRegex(MODULE.Phase3Error, "PHASE3_SCOPE_VIOLATION"):
                MODULE.verify_batch(self._copy(), "HEAD")


if __name__ == "__main__":
    unittest.main()
