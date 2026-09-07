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

    def test_current_census_binds_every_project_without_new_adoption_credit(self):
        self.verify()
        self.assertEqual(0, self.ledger["summary"]["counts"]["ADOPT"])
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
        row = next(row for row in ledger["projects"] if row["projectId"] == "conjugal")
        row["status"] = "ADOPT"
        row["blocker"] = None
        row["evidence"]["disposition"] = {
            "status": "ADOPT", "subjectCommit": MODULE.EXPECTED_MERGE,
            "profilePath": "receipts/missing-profile.json", "profileSha256": "a" * 64,
            "reviewReceiptPath": "receipts/missing-review.json", "reviewReceiptSha256": "b" * 64,
        }
        with self.assertRaisesRegex(MODULE.LedgerError, "ADOPT_"):
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
