import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("current_adoption_ledger", ROOT / "tools/check_adoption_ledger.py")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class CurrentAdoptionLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = MODULE.load_ledger((ROOT / MODULE.CURRENT_LEDGER_PATH).read_bytes())

    def verify(self, ledger=None):
        MODULE.verify_ledger(copy.deepcopy(self.ledger if ledger is None else ledger), "HEAD", current=True)

    def test_current_census_binds_every_project_to_existing_proof_gates(self):
        self.verify()
        self.assertIs(False, self.ledger["summary"]["fleetAdoptionClaim"])

    def test_current_profile_cannot_change_the_frozen_profile(self):
        with self.assertRaisesRegex(MODULE.LedgerError, "NON_PROJECT_SPEC_SET_INVALID"):
            MODULE.verify_ledger(copy.deepcopy(self.ledger), "HEAD")

    def test_project_cannot_be_reclassified_as_portable_doctrine_by_data(self):
        ledger = copy.deepcopy(self.ledger)
        ledger["census"]["nonProjectSpecs"].append("specs/conjugal.md")
        ledger["census"]["nonProjectSpecs"].sort()
        with self.assertRaisesRegex(MODULE.LedgerError, "NON_PROJECT_SPEC_SET_INVALID"):
            self.verify(ledger)

    def test_unregistered_project_is_not_silently_omitted(self):
        tracked = MODULE._tracked_specs("HEAD")
        with mock.patch.object(MODULE, "_tracked_specs", return_value=tracked | {"specs/new-project.md"}):
            with self.assertRaisesRegex(MODULE.LedgerError, "PROJECT_CLOSED_SET_MISMATCH"):
                self.verify()

    def test_spec_append_requires_a_new_current_census(self):
        original = MODULE._oid

        def changed(treeish, path):
            if treeish == "HEAD" and path == "specs/conjugal.md":
                return "0" * 40
            return original(treeish, path)

        with mock.patch.object(MODULE, "_oid", side_effect=changed):
            with self.assertRaisesRegex(MODULE.LedgerError, "PROJECT_SPEC_DRIFT"):
                self.verify()

    def test_current_mode_cannot_manufacture_adopt(self):
        ledger = copy.deepcopy(self.ledger)
        row = next(row for row in ledger["projects"] if row["projectId"] == "cloudvore")
        row["status"] = "ADOPT"
        row["blocker"] = None
        row["evidence"]["disposition"] = {
            "status": "ADOPT", "subjectCommit": MODULE.EXPECTED_MERGE,
            "profilePath": "receipts/missing-profile.json", "profileSha256": "sha256:" + "a" * 64,
            "reviewReceiptPath": "receipts/missing-review.json", "reviewReceiptSha256": "sha256:" + "b" * 64,
        }
        with self.assertRaisesRegex(MODULE.LedgerError, "ADOPT_"):
            self.verify(ledger)

    def test_current_canonical_negative_declaration_has_no_adoption_credit(self):
        ledger = copy.deepcopy(self.ledger)
        row = next(row for row in ledger["projects"] if row["projectId"] == "cloudvore")
        row["status"] = "DISTINGUISH"
        row["blocker"] = "PROJECT_OWNER_DISTINCTION_OPEN"
        row["evidence"]["projectCandidate"] = None
        row["nonRegressionEvidence"] = None
        row["evidence"]["disposition"]["subjectCommit"] = MODULE.EXPECTED_MERGE
        original = MODULE._blob

        def canonical_only(treeish, path):
            if (treeish, path) == (row["evidence"]["commit"], row["specPath"]):
                return f"DISTINGUISH({MODULE.EXPECTED_MERGE}, pending_local_proof)\n".encode()
            return original(treeish, path)

        with mock.patch.object(MODULE, "_blob", side_effect=canonical_only):
            self.verify(ledger)
        self.assertIsNone(row["evidence"]["projectCandidate"])
        self.assertIsNone(row["nonRegressionEvidence"])

    def test_historical_profile_still_requires_candidate_evidence(self):
        row = copy.deepcopy(next(row for row in self.ledger["projects"] if row["projectId"] == "cloudvore"))
        row["evidence"]["projectCandidate"] = None
        with self.assertRaisesRegex(MODULE.LedgerError, "PROJECT_CANDIDATE_REQUIRED"):
            MODULE._verify_project(row, base_commit=self.ledger["census"]["baseCommit"], treeish="HEAD")

    def test_current_present_malformed_candidate_is_still_refused(self):
        ledger = copy.deepcopy(self.ledger)
        row = next(row for row in ledger["projects"] if row["projectId"] == "adversarialllm")
        row["evidence"]["projectCandidate"] = {}
        with self.assertRaisesRegex(MODULE.LedgerError, "PROJECT_CANDIDATE_INVALID"):
            self.verify(ledger)

    def test_current_candidate_requires_each_exact_historical_artifact_row(self):
        ledger = copy.deepcopy(self.ledger)
        row = next(row for row in ledger["projects"] if row["projectId"] == "adversarialllm")
        candidate = row["evidence"]["projectCandidate"]
        artifact = candidate["artifacts"][0]
        original = MODULE._blob

        def missing_artifact(treeish, path):
            value = original(treeish, path)
            if treeish == row["evidence"]["commit"] and path == row["specPath"]:
                needle = (
                    f"| `{artifact['path']}` | `{artifact['gitBlobOid']}` | "
                    f"{artifact['bytes']:,} | `{artifact['sha256']}` |"
                ).encode("utf-8")
                return value.replace(needle, b"", 1)
            return value

        with mock.patch.object(MODULE, "_blob", side_effect=missing_artifact):
            with self.assertRaisesRegex(MODULE.LedgerError, "PROJECT_CANDIDATE_ARTIFACT_NOT_IN_SPEC"):
                self.verify(ledger)

    def test_current_adopt_attempt_without_real_profile_refuses(self):
        ledger = copy.deepcopy(self.ledger)
        row = next(row for row in ledger["projects"] if row["projectId"] == "adversarialllm")
        row["status"] = "ADOPT"
        row["blocker"] = None
        row["evidence"]["projectCandidate"] = None
        row["evidence"]["disposition"] = {
            "status": "ADOPT", "subjectCommit": MODULE.EXPECTED_MERGE,
            "profilePath": "receipts/missing-profile.json", "profileSha256": "sha256:" + "a" * 64,
            "reviewReceiptPath": "receipts/missing-review.json", "reviewReceiptSha256": "sha256:" + "b" * 64,
        }
        original = MODULE._blob

        def unsupported_adopt(treeish, path):
            if (treeish, path) == (row["evidence"]["commit"], row["specPath"]):
                return (MODULE._adopt_disposition_line(row["evidence"]["disposition"]) + "\n" + MODULE.EXPECTED_CANDIDATE).encode()
            return original(treeish, path)

        with (
            mock.patch.object(MODULE, "_blob", side_effect=unsupported_adopt),
            mock.patch.object(MODULE, "_verify_adopt_disposition_artifacts", wraps=MODULE._verify_adopt_disposition_artifacts) as artifacts,
        ):
            with self.assertRaisesRegex(MODULE.LedgerError, "ADOPT_"):
                self.verify(ledger)
            artifacts.assert_called_once()

    def test_current_wrong_subject_and_conflicting_marker_are_refused(self):
        ledger = copy.deepcopy(self.ledger)
        row = next(row for row in ledger["projects"] if row["projectId"] == "conjugal")
        row["evidence"]["disposition"]["subjectCommit"] = "0" * 40
        with self.assertRaisesRegex(MODULE.LedgerError, "DISPOSITION_NOT_IN_PROJECT_EVIDENCE"):
            self.verify(ledger)

        ledger = copy.deepcopy(self.ledger)
        row = next(row for row in ledger["projects"] if row["projectId"] == "cloudvore")
        row["status"] = "DISTINGUISH"
        row["blocker"] = "PROJECT_OWNER_DISTINCTION_OPEN"
        row["evidence"]["projectCandidate"] = None
        row["evidence"]["disposition"]["subjectCommit"] = MODULE.EXPECTED_MERGE
        original = MODULE._blob

        def conflicting(treeish, path):
            value = original(treeish, path)
            if (treeish, path) == (row["evidence"]["commit"], row["specPath"]):
                return value + f"\nDISTINGUISH({MODULE.EXPECTED_CANDIDATE}, conflicting)\n".encode()
            return value

        with mock.patch.object(MODULE, "_blob", side_effect=conflicting):
            with self.assertRaisesRegex(MODULE.LedgerError, "CURRENT_DISPOSITION_CONFLICT"):
                self.verify(ledger)

    def test_cli_current_flag_reads_only_the_current_ledger(self):
        with (
            mock.patch.object(MODULE, "_blob", return_value=json.dumps(self.ledger).encode()) as read,
            mock.patch.object(MODULE, "verify_ledger") as verify,
        ):
            self.assertEqual(0, MODULE.main(["--current", "--treeish", "HEAD"]))
            read.assert_called_once_with("HEAD", MODULE.CURRENT_LEDGER_PATH)
            verify.assert_called_once_with(self.ledger, "HEAD", current=True)


if __name__ == "__main__":
    unittest.main()
