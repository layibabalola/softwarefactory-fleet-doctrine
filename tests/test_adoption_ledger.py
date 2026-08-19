import copy
import hashlib
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

    def _synthetic_adopt(self):
        ledger = self._copy()
        project = self._project(ledger, "dng-auto-processor")
        project["status"] = "ADOPT"
        project["blocker"] = None
        project["evidence"]["disposition"] = {
            "status": "ADOPT",
            "subjectCommit": MODULE.EXPECTED_MERGE,
        }
        ledger["summary"]["counts"]["ADOPT"] = 1
        ledger["summary"]["counts"]["DISTINGUISH"] = 0

        receipt_path = (
            "receipts/project-adoption/dng-auto-processor/"
            "r26-non-regression.json"
        )
        receipt = {
            "schema": MODULE.ADOPT_RECEIPT_SCHEMA,
            "projectId": "dng-auto-processor",
            "candidateCommit": MODULE.EXPECTED_CANDIDATE,
            "mergeCommit": MODULE.EXPECTED_MERGE,
            "dimensions": {
                dimension: {
                    "claim": MODULE.NON_REGRESSION_CLAIMS[dimension],
                    "passed": True,
                }
                for dimension in MODULE.NON_REGRESSION_DIMENSIONS
            },
        }
        receipt_bytes = json.dumps(
            receipt, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        receipt_sha256 = f"sha256:{hashlib.sha256(receipt_bytes).hexdigest()}"
        project["nonRegressionEvidence"] = {}
        for dimension in MODULE.NON_REGRESSION_DIMENSIONS:
            claim = MODULE.NON_REGRESSION_CLAIMS[dimension]
            project["nonRegressionEvidence"][dimension] = {
                "claim": claim,
                "receiptPath": receipt_path,
                "receiptSha256": receipt_sha256,
                "anchor": MODULE._adopt_non_regression_anchor(
                    dimension,
                    claim,
                    receipt_path,
                    receipt_sha256,
                ),
            }
        spec_lines = [
            f"ADOPT (`{MODULE.EXPECTED_MERGE}`)",
            f"Exact R26 candidate: {MODULE.EXPECTED_CANDIDATE}",
            f"Exact R26 merge: {MODULE.EXPECTED_MERGE}",
            *(record["anchor"] for record in project["nonRegressionEvidence"].values()),
        ]
        return ledger, "\n".join(spec_lines).encode("utf-8"), {
            receipt_path: receipt_bytes
        }

    def _verify_synthetic_adopt(
        self,
        ledger,
        spec_bytes,
        receipt_blobs,
        *,
        receipt_commit=None,
    ):
        original_blob = MODULE._blob
        original_blob_size = MODULE._blob_size
        original_last_path_commit = MODULE._last_path_commit
        project = self._project(ledger, "dng-auto-processor")
        evidence_commit = project["evidence"]["commit"]

        def receipt_at(treeish, path):
            value = receipt_blobs.get(path)
            if isinstance(value, dict):
                return value.get(treeish, value.get("*"))
            return value

        def synthetic_blob(treeish, path):
            if path == project["specPath"]:
                return spec_bytes
            if path.startswith(f"{MODULE.ADOPT_RECEIPT_PREFIX}/"):
                value = receipt_at(treeish, path)
                if value is None:
                    raise MODULE.LedgerError("GIT_BLOB_UNAVAILABLE")
                return value
            return original_blob(treeish, path)

        def synthetic_blob_size(treeish, path, *, error="GIT_BLOB_SIZE_UNAVAILABLE"):
            if path.startswith(f"{MODULE.ADOPT_RECEIPT_PREFIX}/"):
                value = receipt_at(treeish, path)
                if value is None:
                    raise MODULE.LedgerError(error)
                return len(value)
            return original_blob_size(treeish, path, error=error)

        def synthetic_last_path_commit(treeish, path):
            if path.startswith(f"{MODULE.ADOPT_RECEIPT_PREFIX}/"):
                if receipt_at(treeish, path) is None:
                    raise MODULE.LedgerError("PROJECT_EVIDENCE_HISTORY_INVALID")
                return receipt_commit or evidence_commit
            return original_last_path_commit(treeish, path)

        with (
            mock.patch.object(MODULE, "_blob", side_effect=synthetic_blob),
            mock.patch.object(MODULE, "_blob_size", side_effect=synthetic_blob_size),
            mock.patch.object(
                MODULE, "_last_path_commit", side_effect=synthetic_last_path_commit
            ),
        ):
            MODULE.verify_ledger(ledger, "HEAD")

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

    def test_manifest_zero_authority_requires_strict_json_booleans(self):
        original_blob = MODULE._blob
        manifest_bytes = original_blob(MODULE.EXPECTED_CANDIDATE, MODULE.EXPECTED_MANIFEST)
        manifest = MODULE.load_ledger(manifest_bytes)
        cases = {
            "false_as_zero": ("providerExecution", 0),
            "true_as_one": ("activationRequiresSeparateAdjudication", 1),
        }
        for name, (field, invalid_value) in cases.items():
            with self.subTest(name=name):
                invalid_manifest = copy.deepcopy(manifest)
                invalid_manifest["authority"][field] = invalid_value
                invalid_bytes = json.dumps(invalid_manifest).encode("utf-8")

                def manifest_override(treeish, path):
                    if treeish == MODULE.EXPECTED_CANDIDATE and path == MODULE.EXPECTED_MANIFEST:
                        return invalid_bytes
                    return original_blob(treeish, path)

                with mock.patch.object(MODULE, "_blob", side_effect=manifest_override):
                    with self.assertRaisesRegex(
                        MODULE.LedgerError, "MANIFEST_AUTHORITY_DRIFT"
                    ):
                        MODULE.verify_ledger(self._copy(), "HEAD")

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

    def test_synthetic_adopt_row_passes_end_to_end_with_recomputed_receipt(self):
        ledger, spec_bytes, receipt_blobs = self._synthetic_adopt()
        self._verify_synthetic_adopt(ledger, spec_bytes, receipt_blobs)

    def test_synthetic_adopt_rejects_incidental_words_and_incomplete_wiring(self):
        ledger, spec_bytes, receipt_blobs = self._synthetic_adopt()
        project = self._project(ledger, "dng-auto-processor")
        project["nonRegressionEvidence"] = {
            dimension: dimension for dimension in MODULE.NON_REGRESSION_DIMENSIONS
        }
        spec_bytes = (
            f"ADOPT (`{MODULE.EXPECTED_MERGE}`)\n"
            f"Exact R26 candidate: {MODULE.EXPECTED_CANDIDATE}\n"
            f"Exact R26 merge: {MODULE.EXPECTED_MERGE}\n"
            "model effort role review quality functionality"
        ).encode("ascii")
        with self.assertRaisesRegex(
            MODULE.LedgerError, "ADOPT_NON_REGRESSION_EVIDENCE_INVALID"
        ):
            self._verify_synthetic_adopt(ledger, spec_bytes, receipt_blobs)

    def test_synthetic_adopt_rejects_invalid_structured_records(self):
        mutations = {
            "missing_receipt_path": lambda record: record.pop("receiptPath"),
            "wrong_claim": lambda record: record.update({"claim": "MODEL"}),
            "malformed_digest": lambda record: record.update(
                {"receiptSha256": "sha256:not-a-digest"}
            ),
            "forged_anchor": lambda record: record.update(
                {"anchor": f"{record['anchor']}-fabricated"}
            ),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                ledger, spec_bytes, receipt_blobs = self._synthetic_adopt()
                record = self._project(ledger, "dng-auto-processor")[
                    "nonRegressionEvidence"
                ]["model"]
                mutate(record)
                with self.assertRaisesRegex(
                    MODULE.LedgerError, "ADOPT_NON_REGRESSION_EVIDENCE_INVALID"
                ):
                    self._verify_synthetic_adopt(ledger, spec_bytes, receipt_blobs)

    def test_synthetic_adopt_rejects_nonexistent_or_forged_receipt(self):
        ledger, spec_bytes, receipt_blobs = self._synthetic_adopt()
        with self.assertRaisesRegex(MODULE.LedgerError, "ADOPT_RECEIPT_UNAVAILABLE"):
            self._verify_synthetic_adopt(ledger, spec_bytes, {})

        receipt_path, receipt_bytes = next(iter(receipt_blobs.items()))
        with self.assertRaisesRegex(
            MODULE.LedgerError, "ADOPT_RECEIPT_SHA256_MISMATCH"
        ):
            self._verify_synthetic_adopt(
                ledger,
                spec_bytes,
                {receipt_path: receipt_bytes + b"\n"},
            )

    def test_synthetic_adopt_rejects_quoted_or_negated_anchor(self):
        for prefix in ('"', "> ", "NOT "):
            with self.subTest(form=prefix):
                ledger, spec_bytes, receipt_blobs = self._synthetic_adopt()
                anchor = self._project(ledger, "dng-auto-processor")[
                    "nonRegressionEvidence"
                ]["model"]["anchor"]
                replacement = f'{prefix}{anchor}"' if prefix == '"' else f"{prefix}{anchor}"
                spec_bytes = spec_bytes.replace(
                    anchor.encode("ascii"), replacement.encode("ascii"), 1
                )
                with self.assertRaisesRegex(
                    MODULE.LedgerError, "ADOPT_NON_REGRESSION_EVIDENCE_MISSING"
                ):
                    self._verify_synthetic_adopt(ledger, spec_bytes, receipt_blobs)

        ledger, spec_bytes, receipt_blobs = self._synthetic_adopt()
        anchor = self._project(ledger, "dng-auto-processor")["nonRegressionEvidence"][
            "model"
        ]["anchor"]
        spec_bytes += f"\n{anchor}".encode("ascii")
        with self.assertRaisesRegex(
            MODULE.LedgerError, "ADOPT_NON_REGRESSION_EVIDENCE_MISSING"
        ):
            self._verify_synthetic_adopt(ledger, spec_bytes, receipt_blobs)

    def test_synthetic_adopt_receipt_wiring_fails_closed(self):
        ledger, spec_bytes, receipt_blobs = self._synthetic_adopt()
        project = self._project(ledger, "dng-auto-processor")
        record = project["nonRegressionEvidence"]["model"]
        record["receiptPath"] = "receipts/project-adoption/other/r26.json"
        with self.assertRaisesRegex(MODULE.LedgerError, "ADOPT_RECEIPT_PATH_INVALID"):
            self._verify_synthetic_adopt(ledger, spec_bytes, receipt_blobs)

        ledger, spec_bytes, receipt_blobs = self._synthetic_adopt()
        with self.assertRaisesRegex(
            MODULE.LedgerError, "ADOPT_RECEIPT_COMMIT_MISMATCH"
        ):
            self._verify_synthetic_adopt(
                ledger,
                spec_bytes,
                receipt_blobs,
                receipt_commit=MODULE.EXPECTED_MERGE,
            )

        ledger, spec_bytes, receipt_blobs = self._synthetic_adopt()
        receipt_path, receipt_bytes = next(iter(receipt_blobs.items()))
        with self.assertRaisesRegex(MODULE.LedgerError, "ADOPT_RECEIPT_DRIFT"):
            self._verify_synthetic_adopt(
                ledger,
                spec_bytes,
                {receipt_path: {"*": receipt_bytes, "HEAD": receipt_bytes + b"\n"}},
            )

        ledger, spec_bytes, receipt_blobs = self._synthetic_adopt()
        receipt_path = next(iter(receipt_blobs))
        with self.assertRaisesRegex(MODULE.LedgerError, "ADOPT_RECEIPT_SIZE_INVALID"):
            self._verify_synthetic_adopt(
                ledger,
                spec_bytes,
                {receipt_path: b"x" * (MODULE.MAX_ADOPT_RECEIPT_BYTES + 1)},
            )

    def test_synthetic_adopt_receipt_rejects_bool_one(self):
        ledger, spec_bytes, receipt_blobs = self._synthetic_adopt()
        receipt_path, receipt_bytes = next(iter(receipt_blobs.items()))
        receipt = MODULE.load_ledger(receipt_bytes)
        receipt["dimensions"]["model"]["passed"] = 1
        invalid_receipt = json.dumps(
            receipt, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        with self.assertRaisesRegex(
            MODULE.LedgerError, "ADOPT_RECEIPT_BINDING_INVALID"
        ):
            self._verify_synthetic_adopt(
                ledger,
                spec_bytes,
                {receipt_path: invalid_receipt},
            )

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
