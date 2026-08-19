import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "check_adoption_ledger.py"
SPEC = importlib.util.spec_from_file_location("check_adoption_ledger", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AdoptionLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = MODULE.load_ledger(
            (ROOT / "adoption" / "universal-token-control-r26.json").read_bytes()
        )

    def _copy(self):
        return copy.deepcopy(self.ledger)

    def _project(self, ledger, project_id):
        return next(project for project in ledger["projects"] if project["projectId"] == project_id)

    def _adopt_non_regression_evidence(self):
        evidence = {}
        for index, dimension in enumerate(MODULE.NON_REGRESSION_DIMENSIONS, start=1):
            claim = MODULE.NON_REGRESSION_CLAIMS[dimension]
            receipt_sha256 = f"sha256:{index:064x}"
            evidence[dimension] = {
                "claim": claim,
                "receiptSha256": receipt_sha256,
                "anchor": MODULE._adopt_non_regression_anchor(
                    dimension, claim, receipt_sha256
                ),
            }
        return evidence

    def _evidence_bytes(self, evidence):
        return "\n".join(record["anchor"] for record in evidence.values()).encode("ascii")

    def test_canonical_ledger_matches_closed_project_owned_evidence(self):
        MODULE.verify_ledger(self._copy(), "HEAD")

    def test_duplicate_json_key_is_rejected(self):
        with self.assertRaisesRegex(MODULE.LedgerError, "DUPLICATE_KEY"):
            MODULE.load_ledger(b'{"schema":"a","schema":"b"}')

    def test_candidate_and_merge_are_exact_not_symbolic(self):
        ledger = self._copy()
        ledger["candidate"]["candidateCommit"] = "0" * 40
        with self.assertRaisesRegex(MODULE.LedgerError, "CANDIDATE_COMMIT_MISMATCH"):
            MODULE.verify_ledger(ledger, "HEAD")

        ledger = self._copy()
        ledger["candidate"]["mergeParents"].reverse()
        with self.assertRaisesRegex(MODULE.LedgerError, "MERGE_PARENT_CLAIM_MISMATCH"):
            MODULE.verify_ledger(ledger, "HEAD")

    def test_candidate_zero_authority_cannot_be_upgraded_by_ledger_claim(self):
        ledger = self._copy()
        ledger["candidate"]["authorityClaims"]["doctrinePublicationIsFleetAdoption"] = True
        with self.assertRaisesRegex(MODULE.LedgerError, "ZERO_AUTHORITY_OVERCLAIM"):
            MODULE.verify_ledger(ledger, "HEAD")

        ledger = self._copy()
        ledger["candidate"]["manifest"]["status"] = "RATIFIED"
        with self.assertRaisesRegex(MODULE.LedgerError, "MANIFEST_STATUS_CLAIM_MISMATCH"):
            MODULE.verify_ledger(ledger, "HEAD")

    def test_all_six_non_regression_dimensions_are_mandatory_and_ordered(self):
        ledger = self._copy()
        ledger["nonRegression"]["requiredDimensions"].remove("quality")
        with self.assertRaisesRegex(MODULE.LedgerError, "NON_REGRESSION_DIMENSIONS_MISMATCH"):
            MODULE.verify_ledger(ledger, "HEAD")

        ledger = self._copy()
        ledger["nonRegression"]["requiredDimensions"].reverse()
        with self.assertRaisesRegex(MODULE.LedgerError, "NON_REGRESSION_DIMENSIONS_MISMATCH"):
            MODULE.verify_ledger(ledger, "HEAD")

    def test_project_cannot_disappear_from_the_closed_set(self):
        ledger = self._copy()
        ledger["projects"] = [
            project for project in ledger["projects"] if project["projectId"] != "salesforce-tools"
        ]
        ledger["summary"]["projectCount"] = 8
        ledger["summary"]["counts"]["MISSING"] = 0
        with self.assertRaisesRegex(MODULE.LedgerError, "PROJECT_CLOSED_SET_MISMATCH"):
            MODULE.verify_ledger(ledger, "HEAD")

    def test_non_project_exclusion_set_cannot_hide_a_project(self):
        ledger = self._copy()
        ledger["census"]["nonProjectSpecs"].append("specs/salesforce-tools.md")
        ledger["census"]["nonProjectSpecs"].sort()
        with self.assertRaisesRegex(MODULE.LedgerError, "NON_PROJECT_SPEC_SET_INVALID"):
            MODULE.verify_ledger(ledger, "HEAD")

    def test_census_base_must_be_on_the_merge_to_checked_tree_history(self):
        ledger = self._copy()
        ledger["census"]["baseCommit"] = MODULE.EXPECTED_CANDIDATE
        with self.assertRaisesRegex(MODULE.LedgerError, "CENSUS_BASE_HISTORY_INVALID"):
            MODULE.verify_ledger(ledger, "HEAD")

    def test_project_source_commit_and_blob_are_both_enforced(self):
        ledger = self._copy()
        self._project(ledger, "dng-auto-processor")["evidence"]["gitBlobOid"] = "0" * 40
        with self.assertRaisesRegex(MODULE.LedgerError, "PROJECT_EVIDENCE_COMMIT_BLOB_MISMATCH"):
            MODULE.verify_ledger(ledger, "HEAD")

        ledger = self._copy()
        self._project(ledger, "dng-auto-processor")["evidence"]["commit"] = ledger["candidate"][
            "mergeCommit"
        ]
        with self.assertRaisesRegex(MODULE.LedgerError, "PROJECT_EVIDENCE_NOT_LATEST_AT_CENSUS"):
            MODULE.verify_ledger(ledger, "HEAD")

    def test_dng_is_distinguish_at_project_commit_not_adopt(self):
        ledger = self._copy()
        dng = self._project(ledger, "dng-auto-processor")
        self.assertEqual("DISTINGUISH", dng["status"])
        self.assertEqual("76dd97d3110668b6f1391aabee3e270801be00ad", dng["evidence"]["commit"])

        dng["status"] = "ADOPT"
        dng["blocker"] = None
        ledger["summary"]["counts"]["DISTINGUISH"] = 0
        ledger["summary"]["counts"]["ADOPT"] = 1
        with self.assertRaisesRegex(MODULE.LedgerError, "CURRENT_DISPOSITION_STATUS_MISMATCH"):
            MODULE.verify_ledger(ledger, "HEAD")

    def test_conflicting_current_dispositions_are_rejected(self):
        original_dispositions = MODULE._dispositions

        def conflicting_dispositions(blob):
            markers = original_dispositions(blob)
            if ("DISTINGUISH", MODULE.EXPECTED_MERGE) in markers:
                markers.add(("ADOPT", MODULE.EXPECTED_CANDIDATE))
            return markers

        with mock.patch.object(
            MODULE, "_dispositions", side_effect=conflicting_dispositions
        ):
            with self.assertRaisesRegex(MODULE.LedgerError, "CURRENT_DISPOSITION_CONFLICT"):
                MODULE.verify_ledger(self._copy(), "HEAD")

    def test_adopt_non_regression_rejects_incidental_dimension_words(self):
        incidental_words = {
            dimension: dimension for dimension in MODULE.NON_REGRESSION_DIMENSIONS
        }
        with self.assertRaisesRegex(
            MODULE.LedgerError, "ADOPT_NON_REGRESSION_EVIDENCE_INVALID"
        ):
            MODULE._verify_adopt_non_regression(
                incidental_words,
                b"model effort role review quality functionality",
            )

    def test_adopt_non_regression_rejects_invalid_structured_anchors(self):
        evidence = self._adopt_non_regression_evidence()
        evidence["model"]["claim"] = "MODEL"
        with self.assertRaisesRegex(
            MODULE.LedgerError, "ADOPT_NON_REGRESSION_EVIDENCE_INVALID"
        ):
            MODULE._verify_adopt_non_regression(evidence, self._evidence_bytes(evidence))

        evidence = self._adopt_non_regression_evidence()
        evidence["quality"]["receiptSha256"] = "sha256:not-a-digest"
        with self.assertRaisesRegex(
            MODULE.LedgerError, "ADOPT_NON_REGRESSION_EVIDENCE_INVALID"
        ):
            MODULE._verify_adopt_non_regression(evidence, self._evidence_bytes(evidence))

        evidence = self._adopt_non_regression_evidence()
        evidence["functionality"]["anchor"] += "-fabricated"
        with self.assertRaisesRegex(
            MODULE.LedgerError, "ADOPT_NON_REGRESSION_EVIDENCE_INVALID"
        ):
            MODULE._verify_adopt_non_regression(evidence, self._evidence_bytes(evidence))

    def test_adopt_non_regression_requires_structured_anchors_in_project_evidence(self):
        evidence = self._adopt_non_regression_evidence()
        with self.assertRaisesRegex(
            MODULE.LedgerError, "ADOPT_NON_REGRESSION_EVIDENCE_MISSING"
        ):
            MODULE._verify_adopt_non_regression(evidence, b"model")

        MODULE._verify_adopt_non_regression(evidence, self._evidence_bytes(evidence))

    def test_project_rows_must_be_sorted_and_unique(self):
        ledger = self._copy()
        ledger["projects"][0], ledger["projects"][1] = (
            ledger["projects"][1],
            ledger["projects"][0],
        )
        with self.assertRaisesRegex(
            MODULE.LedgerError, "PROJECT_ORDER_OR_DUPLICATE_INVALID"
        ):
            MODULE.verify_ledger(ledger, "HEAD")

    def test_project_blocker_must_match_disposition(self):
        ledger = self._copy()
        self._project(ledger, "dng-auto-processor")["blocker"] = (
            "PROJECT_OWNER_CURRENT_CANDIDATE_DISPOSITION_REQUIRED"
        )
        with self.assertRaisesRegex(MODULE.LedgerError, "PROJECT_BLOCKER_INVALID"):
            MODULE.verify_ledger(ledger, "HEAD")

    def test_stale_requires_an_exact_prior_project_disposition(self):
        ledger = self._copy()
        adobe = self._project(ledger, "adobe-ingester")
        adobe["evidence"]["disposition"][
            "subjectCommit"
        ] = "224a6705d81dfbc670313cdcef4d825216f2b380"
        with self.assertRaisesRegex(MODULE.LedgerError, "STALE_DISPOSITION_SUBJECT_INVALID"):
            MODULE.verify_ledger(ledger, "HEAD")

    def test_missing_cannot_carry_invented_project_evidence(self):
        ledger = self._copy()
        salesforce = self._project(ledger, "salesforce-tools")
        salesforce["evidence"]["disposition"] = {
            "status": "DISTINGUISH",
            "subjectCommit": "874605e43531c9aa230ee16851f8107a8e0d9cec",
        }
        with self.assertRaisesRegex(MODULE.LedgerError, "MISSING_STATUS_HAS_DISPOSITION_EVIDENCE"):
            MODULE.verify_ledger(ledger, "HEAD")

    def test_summary_cannot_convert_publication_into_fleet_adoption(self):
        ledger = self._copy()
        ledger["summary"]["counts"]["ADOPT"] = 9
        with self.assertRaisesRegex(MODULE.LedgerError, "SUMMARY_COUNT_MISMATCH"):
            MODULE.verify_ledger(ledger, "HEAD")

        ledger = self._copy()
        ledger["summary"]["fleetStatus"] = "FLEET_ADOPTED"
        ledger["summary"]["fleetAdoptionClaim"] = True
        with self.assertRaisesRegex(MODULE.LedgerError, "FLEET_ADOPTION_OVERCLAIM"):
            MODULE.verify_ledger(ledger, "HEAD")


if __name__ == "__main__":
    unittest.main()
