import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
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
        ledger["summary"]["counts"]["ADOPT"] = 1
        ledger["summary"]["counts"]["DISTINGUISH"] = 3

        prefix = "receipts/project-adoption/dng-auto-processor"
        artifacts = {}

        def encode(value):
            return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")

        def add_artifact(name, content):
            path = f"{prefix}/{name}"
            raw = content if isinstance(content, bytes) else encode(content)
            artifacts[path] = raw
            return {
                "path": path,
                "sha256": f"sha256:{hashlib.sha256(raw).hexdigest()}",
            }

        profile_ref = add_artifact(
            "profile.json",
            {
                "schema": MODULE.ADOPT_PROFILE_SCHEMA,
                "projectId": "dng-auto-processor",
                "candidateCommit": MODULE.EXPECTED_CANDIDATE,
                "mergeCommit": MODULE.EXPECTED_MERGE,
                "canonicalCommit": MODULE.EXPECTED_MERGE,
                "model": "exact-model",
                "effort": "exact-effort",
                "role": "exact-role",
                "review": "independent-review-required",
                "quality": "non-inferior",
                "functionality": "equivalent",
            },
        )
        review_ref = add_artifact(
            "review.json",
            {
                "schema": MODULE.ADOPT_REVIEW_SCHEMA,
                "projectId": "dng-auto-processor",
                "candidateCommit": MODULE.EXPECTED_CANDIDATE,
                "mergeCommit": MODULE.EXPECTED_MERGE,
                "canonicalCommit": MODULE.EXPECTED_MERGE,
                "profileSha256": profile_ref["sha256"],
                "verdict": "ACCEPT",
                "reviews": [
                    {
                        "reviewer": "synthetic-mechanics-reviewer",
                        "role": "mechanics",
                        "verdict": "ACCEPT",
                    },
                    {
                        "reviewer": "synthetic-safety-reviewer",
                        "role": "safety",
                        "verdict": "ACCEPT",
                    },
                ],
            },
        )
        supervisor_ref = add_artifact(
            "supervisor.py", b"synthetic pinned supervisor subject\n"
        )
        adapter_ref = add_artifact("adapter.py", b"synthetic pinned adapter subject\n")
        launcher_refs = [
            add_artifact("launcher.cmd", b"synthetic launcher one\n"),
            add_artifact("launcher-helper.ps1", b"synthetic launcher two\n"),
        ]
        proof_evidence = {
            "supervisorAdapter": {
                "supervisor": supervisor_ref,
                "adapter": adapter_ref,
            },
            "launcherCensus": {
                "launchers": launcher_refs,
                "unresolvedLaunchers": [],
            },
            "fakeProviderControls": {
                "cases": MODULE.ADOPT_REQUIRED_CONTROL_CASES["fakeProviderControls"],
                "passedCases": MODULE.ADOPT_REQUIRED_CONTROL_CASES[
                    "fakeProviderControls"
                ],
                "failedCases": [],
            },
            "concurrencyControls": {
                "cases": MODULE.ADOPT_REQUIRED_CONTROL_CASES["concurrencyControls"],
                "passedCases": MODULE.ADOPT_REQUIRED_CONTROL_CASES[
                    "concurrencyControls"
                ],
                "failedCases": [],
            },
            "idleTicks": {"ticks": 1_000, "inferenceCalls": 0, "stateChanges": 0},
            "fullChildFencing": {
                "cases": MODULE.ADOPT_REQUIRED_CONTROL_CASES["fullChildFencing"],
                "passedCases": MODULE.ADOPT_REQUIRED_CONTROL_CASES[
                    "fullChildFencing"
                ],
                "failedCases": [],
            },
            "rollback": {
                "steps": MODULE.ADOPT_REQUIRED_ROLLBACK_STEPS,
                "beforeGate": "CLOSED",
                "afterGate": "CLOSED",
                "residualProcesses": 0,
            },
            "closedGate": {
                "state": "CLOSED",
                "currentAtEvidenceCommit": True,
                "providerInvocationEnabled": False,
                "automaticLaunchEnabled": False,
            },
        }
        proof_refs = {}
        for kind in sorted(MODULE.ADOPT_PROOF_KINDS):
            proof_refs[kind] = add_artifact(
                f"proof-{kind.lower()}.json",
                {
                    "schema": MODULE.ADOPT_PROOF_SCHEMA,
                    "kind": kind,
                    "projectId": "dng-auto-processor",
                    "candidateCommit": MODULE.EXPECTED_CANDIDATE,
                    "mergeCommit": MODULE.EXPECTED_MERGE,
                    "canonicalCommit": MODULE.EXPECTED_MERGE,
                    "profileSha256": profile_ref["sha256"],
                    "reviewReceiptSha256": review_ref["sha256"],
                    "evidence": proof_evidence[kind],
                },
            )

        project["evidence"]["disposition"] = {
            "status": "ADOPT",
            "subjectCommit": MODULE.EXPECTED_MERGE,
            "profilePath": profile_ref["path"],
            "profileSha256": profile_ref["sha256"],
            "reviewReceiptPath": review_ref["path"],
            "reviewReceiptSha256": review_ref["sha256"],
        }
        receipt_path = f"{prefix}/r26-non-regression.json"
        receipt = {
            "schema": MODULE.ADOPT_RECEIPT_SCHEMA,
            "projectId": "dng-auto-processor",
            "candidateCommit": MODULE.EXPECTED_CANDIDATE,
            "mergeCommit": MODULE.EXPECTED_MERGE,
            "canonicalCommit": MODULE.EXPECTED_MERGE,
            "profile": profile_ref,
            "reviewReceipt": review_ref,
            "proofs": proof_refs,
            "dimensions": {
                dimension: {
                    "claim": MODULE.NON_REGRESSION_CLAIMS[dimension],
                    "passed": True,
                }
                for dimension in MODULE.NON_REGRESSION_DIMENSIONS
            },
        }
        receipt_bytes = encode(receipt)
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
            MODULE._adopt_disposition_line(project["evidence"]["disposition"]),
            f"Exact R26 candidate: {MODULE.EXPECTED_CANDIDATE}",
            f"Exact R26 merge: {MODULE.EXPECTED_MERGE}",
            *(record["anchor"] for record in project["nonRegressionEvidence"].values()),
        ]
        return ledger, "\n".join(spec_lines).encode("utf-8"), {
            receipt_path: receipt_bytes,
            **artifacts,
        }

    def _rebind_adoption_receipt(self, ledger, spec_bytes, receipt_blobs, receipt):
        receipt_path = next(iter(receipt_blobs))
        receipt_bytes = json.dumps(
            receipt, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        receipt_sha256 = f"sha256:{hashlib.sha256(receipt_bytes).hexdigest()}"
        project = self._project(ledger, "dng-auto-processor")
        for dimension, record in project["nonRegressionEvidence"].items():
            old_anchor = record["anchor"]
            record["receiptSha256"] = receipt_sha256
            record["anchor"] = MODULE._adopt_non_regression_anchor(
                dimension,
                record["claim"],
                receipt_path,
                receipt_sha256,
            )
            spec_bytes = spec_bytes.replace(
                old_anchor.encode("ascii"), record["anchor"].encode("ascii"), 1
            )
        rebound_blobs = dict(receipt_blobs)
        rebound_blobs[receipt_path] = receipt_bytes
        return spec_bytes, rebound_blobs

    def _rebind_proof(self, ledger, spec_bytes, receipt_blobs, kind, proof):
        receipt_path = next(iter(receipt_blobs))
        receipt = MODULE.load_ledger(receipt_blobs[receipt_path])
        proof_path = receipt["proofs"][kind]["path"]
        proof_bytes = json.dumps(
            proof, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        proof_blobs = dict(receipt_blobs)
        proof_blobs[proof_path] = proof_bytes
        receipt["proofs"][kind]["sha256"] = (
            f"sha256:{hashlib.sha256(proof_bytes).hexdigest()}"
        )
        return self._rebind_adoption_receipt(
            ledger, spec_bytes, proof_blobs, receipt
        )

    def _verify_synthetic_adopt(
        self,
        ledger,
        spec_bytes,
        receipt_blobs,
        *,
        receipt_from_prior_commit=False,
    ):
        project = self._project(ledger, "dng-auto-processor")
        receipt_path = next(iter(receipt_blobs))

        def git(repo, *args):
            run = subprocess.run(
                ["git", *args],
                cwd=repo,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            if run.returncode != 0:
                self.fail(
                    f"synthetic Git command failed ({' '.join(args)}): {run.stderr.strip()}"
                )
            return run.stdout.strip()

        def write_blob(repo, path, raw):
            target = repo / path
            if raw is None:
                if target.exists():
                    target.unlink()
                return
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)

        def evidence_blob(value):
            return value.get("*") if isinstance(value, dict) else value

        with tempfile.TemporaryDirectory(prefix="r26-adopt-git-") as temp:
            repo = Path(temp) / "repo"
            source_head_run = subprocess.run(
                [
                    "git",
                    "-c",
                    "safe.directory=*",
                    "-C",
                    str(ROOT),
                    "rev-parse",
                    "HEAD",
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            if source_head_run.returncode != 0:
                self.fail(
                    f"synthetic Git source lookup failed: {source_head_run.stderr.strip()}"
                )
            source_head = source_head_run.stdout.strip()
            clone = subprocess.run(
                [
                    "git",
                    "-c",
                    "safe.directory=*",
                    "clone",
                    "--quiet",
                    "--no-hardlinks",
                    str(ROOT),
                    str(repo),
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            if clone.returncode != 0:
                self.fail(f"synthetic Git clone failed: {clone.stderr.strip()}")
            git(repo, "config", "user.name", "R26 Synthetic Evidence")
            git(repo, "config", "user.email", "r26-synthetic@example.invalid")
            git(repo, "config", "core.autocrlf", "false")
            git(repo, "checkout", "--quiet", "--detach", source_head)

            if receipt_from_prior_commit:
                write_blob(repo, receipt_path, evidence_blob(receipt_blobs[receipt_path]))
                git(repo, "add", "--", receipt_path)
                git(repo, "commit", "--quiet", "-m", "test: add prior receipt evidence")

            write_blob(repo, project["specPath"], spec_bytes)
            evidence_paths = [project["specPath"]]
            for path, value in receipt_blobs.items():
                if receipt_from_prior_commit and path == receipt_path:
                    continue
                raw = evidence_blob(value)
                write_blob(repo, path, raw)
                if raw is not None:
                    evidence_paths.append(path)
            git(repo, "add", "--", *evidence_paths)
            git(repo, "commit", "--quiet", "-m", "test: add coherent adoption evidence")
            evidence_commit = git(repo, "rev-parse", "HEAD")
            project["evidence"]["commit"] = evidence_commit
            project["evidence"]["gitBlobOid"] = git(
                repo, "rev-parse", f"{evidence_commit}:{project['specPath']}"
            )
            ledger["census"]["baseCommit"] = evidence_commit
            for candidate in ledger["projects"]:
                actual_last_commit = git(
                    repo,
                    "log",
                    "-1",
                    "--format=%H",
                    evidence_commit,
                    "--",
                    candidate["specPath"],
                )
                self.assertEqual(
                    candidate["evidence"]["commit"],
                    actual_last_commit,
                    f"incoherent evidence commit for {candidate['projectId']}",
                )

            ledger_path = repo / MODULE.LEDGER_PATH
            ledger_path.write_text(
                json.dumps(ledger, indent=2) + "\n", encoding="utf-8", newline="\n"
            )
            git(repo, "add", "--", MODULE.LEDGER_PATH)
            git(repo, "commit", "--quiet", "-m", "test: bind adoption ledger to evidence")

            drifted = False
            drift_paths = []
            for path, value in receipt_blobs.items():
                if not isinstance(value, dict) or "HEAD" not in value:
                    continue
                write_blob(repo, path, value["HEAD"])
                drifted = True
                drift_paths.append(path)
            if drifted:
                git(repo, "add", "--all", "--", *drift_paths)
                git(repo, "commit", "--quiet", "-m", "test: introduce post-ledger drift")

            treeish = git(repo, "rev-parse", "HEAD")
            original_root = MODULE.ROOT
            try:
                MODULE.ROOT = repo
                committed_ledger = MODULE.load_ledger(
                    MODULE._blob(treeish, MODULE.LEDGER_PATH)
                )
                MODULE.verify_ledger(committed_ledger, treeish)
            finally:
                MODULE.ROOT = original_root

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
        ledger["summary"]["counts"]["DISTINGUISH"] = 3
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

    def test_synthetic_adopt_disposition_must_be_one_exact_canonical_line(self):
        ledger, spec_bytes, receipt_blobs = self._synthetic_adopt()
        disposition = self._project(ledger, "dng-auto-processor")["evidence"][
            "disposition"
        ]
        canonical = MODULE._adopt_disposition_line(disposition)
        profile_sha256 = disposition["profileSha256"]
        review_sha256 = disposition["reviewReceiptSha256"]
        variants = {
            "negated": f"NOT {canonical}",
            "quoted_block": f"> {canonical}",
            "quoted_string": f'"{canonical}"',
            "prefix_prose": f"Project claims {canonical}",
            "suffix_prose": f"{canonical} but not yet effective",
            "short_one_argument": f"ADOPT({MODULE.EXPECTED_MERGE})",
            "short_two_arguments": f"ADOPT({MODULE.EXPECTED_MERGE}, {profile_sha256})",
            "wrong_canonical_commit": (
                f"ADOPT({MODULE.EXPECTED_CANDIDATE}, {profile_sha256}, {review_sha256})"
            ),
            "wrong_profile": (
                f"ADOPT({MODULE.EXPECTED_MERGE}, sha256:{'0' * 64}, {review_sha256})"
            ),
            "wrong_review_receipt": (
                f"ADOPT({MODULE.EXPECTED_MERGE}, {profile_sha256}, sha256:{'1' * 64})"
            ),
            "duplicate": f"{canonical}\n{canonical}",
        }
        for name, replacement in variants.items():
            with self.subTest(name=name):
                changed_spec = spec_bytes.replace(
                    canonical.encode("ascii"), replacement.encode("ascii"), 1
                )
                with self.assertRaisesRegex(
                    MODULE.LedgerError, "ADOPT_DISPOSITION_RECORD_INVALID"
                ):
                    self._verify_synthetic_adopt(
                        copy.deepcopy(ledger),
                        changed_spec,
                        dict(receipt_blobs),
                    )

    def test_synthetic_adopt_requires_all_pinned_ratified_proofs(self):
        ledger, spec_bytes, receipt_blobs = self._synthetic_adopt()
        receipt_path, receipt_bytes = next(iter(receipt_blobs.items()))
        receipt = MODULE.load_ledger(receipt_bytes)

        missing_proof_blobs = dict(receipt_blobs)
        missing_proof_path = receipt["proofs"]["idleTicks"]["path"]
        del missing_proof_blobs[missing_proof_path]
        with self.assertRaisesRegex(MODULE.LedgerError, "ADOPT_ARTIFACT_UNAVAILABLE"):
            self._verify_synthetic_adopt(ledger, spec_bytes, missing_proof_blobs)

        forged_proof_blobs = dict(receipt_blobs)
        forged_proof_blobs[missing_proof_path] += b"\n"
        with self.assertRaisesRegex(
            MODULE.LedgerError, "ADOPT_ARTIFACT_SHA256_MISMATCH"
        ):
            self._verify_synthetic_adopt(ledger, spec_bytes, forged_proof_blobs)

        supervisor_proof_path = receipt["proofs"]["supervisorAdapter"]["path"]
        supervisor_proof = MODULE.load_ledger(receipt_blobs[supervisor_proof_path])
        supervisor_subject_path = supervisor_proof["evidence"]["supervisor"]["path"]
        missing_subject_blobs = dict(receipt_blobs)
        del missing_subject_blobs[supervisor_subject_path]
        with self.assertRaisesRegex(MODULE.LedgerError, "ADOPT_ARTIFACT_UNAVAILABLE"):
            self._verify_synthetic_adopt(ledger, spec_bytes, missing_subject_blobs)

        self_asserted_receipt = {
            "schema": MODULE.ADOPT_RECEIPT_SCHEMA,
            "projectId": "dng-auto-processor",
            "candidateCommit": MODULE.EXPECTED_CANDIDATE,
            "mergeCommit": MODULE.EXPECTED_MERGE,
            "dimensions": receipt["dimensions"],
        }
        self_asserted_spec, self_asserted_blobs = self._rebind_adoption_receipt(
            ledger,
            spec_bytes,
            receipt_blobs,
            self_asserted_receipt,
        )
        with self.assertRaisesRegex(MODULE.LedgerError, "ADOPT_RECEIPT_INVALID"):
            self._verify_synthetic_adopt(
                ledger,
                self_asserted_spec,
                self_asserted_blobs,
            )

    def test_synthetic_adopt_enforces_idle_ticks_and_closed_gate_content(self):
        cases = {
            "idleTicks": ("ADOPT_IDLE_TICKS_INVALID", {"ticks": 999}),
            "closedGate": ("ADOPT_CLOSED_GATE_INVALID", {"state": "OPEN"}),
            "launcherCensus": (
                "ADOPT_LAUNCHER_CENSUS_INVALID",
                {"unresolvedLaunchers": ["unknown-launcher"]},
            ),
            "fakeProviderControls": (
                "ADOPT_CONTROL_PROOF_INVALID",
                {"passedCases": []},
            ),
            "concurrencyControls": (
                "ADOPT_CONTROL_PROOF_INVALID",
                {"failedCases": ["concurrent-claim-refused"]},
            ),
            "fullChildFencing": (
                "ADOPT_CONTROL_PROOF_INVALID",
                {"passedCases": []},
            ),
            "rollback": (
                "ADOPT_ROLLBACK_PROOF_INVALID",
                {"afterGate": "OPEN"},
            ),
        }
        for kind, (error, changes) in cases.items():
            with self.subTest(kind=kind):
                ledger, spec_bytes, receipt_blobs = self._synthetic_adopt()
                receipt_path = next(iter(receipt_blobs))
                receipt = MODULE.load_ledger(receipt_blobs[receipt_path])
                proof_path = receipt["proofs"][kind]["path"]
                proof = MODULE.load_ledger(receipt_blobs[proof_path])
                proof["evidence"].update(changes)
                changed_spec, changed_blobs = self._rebind_proof(
                    ledger,
                    spec_bytes,
                    receipt_blobs,
                    kind,
                    proof,
                )
                with self.assertRaisesRegex(MODULE.LedgerError, error):
                    self._verify_synthetic_adopt(
                        ledger,
                        changed_spec,
                        changed_blobs,
                    )

    def test_synthetic_adopt_rejects_incidental_words_and_incomplete_wiring(self):
        ledger, spec_bytes, receipt_blobs = self._synthetic_adopt()
        project = self._project(ledger, "dng-auto-processor")
        project["nonRegressionEvidence"] = {
            dimension: dimension for dimension in MODULE.NON_REGRESSION_DIMENSIONS
        }
        spec_bytes += b"\nmodel effort role review quality functionality"
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
        receipt_path = next(iter(receipt_blobs))
        missing_receipt_blobs = dict(receipt_blobs)
        del missing_receipt_blobs[receipt_path]
        with self.assertRaisesRegex(MODULE.LedgerError, "ADOPT_RECEIPT_UNAVAILABLE"):
            self._verify_synthetic_adopt(ledger, spec_bytes, missing_receipt_blobs)

        receipt_path, receipt_bytes = next(iter(receipt_blobs.items()))
        forged_receipt_blobs = dict(receipt_blobs)
        forged_receipt_blobs[receipt_path] = receipt_bytes + b"\n"
        with self.assertRaisesRegex(
            MODULE.LedgerError, "ADOPT_RECEIPT_SHA256_MISMATCH"
        ):
            self._verify_synthetic_adopt(
                ledger,
                spec_bytes,
                forged_receipt_blobs,
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
                receipt_from_prior_commit=True,
            )

        ledger, spec_bytes, receipt_blobs = self._synthetic_adopt()
        receipt_path, receipt_bytes = next(iter(receipt_blobs.items()))
        drift_blobs = dict(receipt_blobs)
        drift_blobs[receipt_path] = {"*": receipt_bytes, "HEAD": receipt_bytes + b"\n"}
        with self.assertRaisesRegex(MODULE.LedgerError, "ADOPT_RECEIPT_DRIFT"):
            self._verify_synthetic_adopt(
                ledger,
                spec_bytes,
                drift_blobs,
            )

        ledger, spec_bytes, receipt_blobs = self._synthetic_adopt()
        receipt_path = next(iter(receipt_blobs))
        oversize_blobs = dict(receipt_blobs)
        oversize_blobs[receipt_path] = b"x" * (MODULE.MAX_ADOPT_RECEIPT_BYTES + 1)
        with self.assertRaisesRegex(MODULE.LedgerError, "ADOPT_RECEIPT_SIZE_INVALID"):
            self._verify_synthetic_adopt(
                ledger,
                spec_bytes,
                oversize_blobs,
            )

    def test_synthetic_adopt_receipt_rejects_bool_one(self):
        ledger, spec_bytes, receipt_blobs = self._synthetic_adopt()
        receipt_path, receipt_bytes = next(iter(receipt_blobs.items()))
        receipt = MODULE.load_ledger(receipt_bytes)
        receipt["dimensions"]["model"]["passed"] = 1
        spec_bytes, invalid_receipt_blobs = self._rebind_adoption_receipt(
            ledger, spec_bytes, receipt_blobs, receipt
        )
        with self.assertRaisesRegex(
            MODULE.LedgerError, "ADOPT_RECEIPT_BINDING_INVALID"
        ):
            self._verify_synthetic_adopt(
                ledger,
                spec_bytes,
                invalid_receipt_blobs,
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

    def test_published_project_candidate_is_required_only_for_the_exact_three_rows(self):
        ledger = self._copy()
        self._project(ledger, "salesforce-tools")["evidence"]["projectCandidate"] = None
        with self.assertRaisesRegex(MODULE.LedgerError, "PROJECT_CANDIDATE_REQUIRED"):
            MODULE.verify_ledger(ledger, "HEAD")

        ledger = self._copy()
        self._project(ledger, "adobe-ingester")["evidence"]["projectCandidate"] = copy.deepcopy(
            self._project(ledger, "cloudvore")["evidence"]["projectCandidate"]
        )
        with self.assertRaisesRegex(MODULE.LedgerError, "PROJECT_CANDIDATE_UNEXPECTED"):
            MODULE.verify_ledger(ledger, "HEAD")

    def test_published_project_candidate_entire_object_is_exact_bound(self):
        for project_id in sorted(MODULE.PROJECT_CANDIDATE_IDS):
            with self.subTest(project_id=project_id):
                candidate = self._project(self._copy(), project_id)["evidence"]["projectCandidate"]
                canonical = json.dumps(
                    candidate, ensure_ascii=False, separators=(",", ":"), sort_keys=True
                ).encode("utf-8")
                self.assertEqual(
                    MODULE.EXPECTED_PROJECT_CANDIDATE_SHA256[project_id],
                    hashlib.sha256(canonical).hexdigest(),
                )

    def test_candidate_commit_and_tree_substitutions_fail_exact_binding(self):
        project = self._project(self._copy(), "cloudvore")
        spec_bytes = MODULE._blob(project["evidence"]["commit"], project["specPath"])
        for field, value in (("commit", "0" * 40), ("tree", "1" * 40)):
            with self.subTest(field=field):
                candidate = copy.deepcopy(project["evidence"]["projectCandidate"])
                candidate[field] = value
                with self.assertRaisesRegex(
                    MODULE.LedgerError, "PROJECT_CANDIDATE_EXACT_BINDING_MISMATCH"
                ):
                    MODULE._verify_project_candidate(
                        candidate, project_id="cloudvore", spec_bytes=spec_bytes
                    )

    def test_coordinated_artifact_or_statement_substitution_still_fails_frozen_digest(self):
        project = self._project(self._copy(), "mlv-app")
        original = project["evidence"]["projectCandidate"]
        original_spec = MODULE._blob(project["evidence"]["commit"], project["specPath"])
        mutations = []

        artifact_candidate = copy.deepcopy(original)
        artifact = artifact_candidate["artifacts"][0]
        old_row = (
            f"| `{artifact['path']}` | `{artifact['gitBlobOid']}` | "
            f"{artifact['bytes']:,} | `{artifact['sha256']}` |"
        ).encode("utf-8")
        artifact["gitBlobOid"] = "2" * 40
        artifact["bytes"] += 1
        artifact["sha256"] = "3" * 64
        new_row = (
            f"| `{artifact['path']}` | `{artifact['gitBlobOid']}` | "
            f"{artifact['bytes']:,} | `{artifact['sha256']}` |"
        ).encode("utf-8")
        mutations.append((artifact_candidate, original_spec.replace(old_row, new_row)))

        statement_candidate = copy.deepcopy(original)
        old_statement = statement_candidate["disposition"]["statement"]
        new_statement = old_statement.replace("MLV_APP_R26", "MLV_APP_FABRICATED_R26")
        statement_candidate["disposition"]["statement"] = new_statement
        mutations.append(
            (
                statement_candidate,
                original_spec.replace(old_statement.encode("utf-8"), new_statement.encode("utf-8")),
            )
        )

        for candidate, coordinated_spec in mutations:
            with self.subTest(statement=candidate["disposition"]["statement"][:40]):
                with self.assertRaisesRegex(
                    MODULE.LedgerError, "PROJECT_CANDIDATE_EXACT_BINDING_MISMATCH"
                ):
                    MODULE._verify_project_candidate(
                        candidate, project_id="mlv-app", spec_bytes=coordinated_spec
                    )

    def test_candidate_rejects_recursive_adopt_and_authority_or_proof_credit(self):
        project = self._project(self._copy(), "salesforce-tools")
        spec_bytes = MODULE._blob(project["evidence"]["commit"], project["specPath"])
        candidate = copy.deepcopy(project["evidence"]["projectCandidate"])
        candidate["disposition"]["statement"] += " ADOPT(0000000000000000000000000000000000000000)"
        with self.assertRaisesRegex(MODULE.LedgerError, "PROJECT_CANDIDATE_ADOPTION_OVERCLAIM"):
            MODULE._verify_project_candidate(
                candidate, project_id="salesforce-tools", spec_bytes=spec_bytes
            )

        candidate = copy.deepcopy(project["evidence"]["projectCandidate"])
        candidate["authorityClaims"]["runtimeActivation"] = True
        with self.assertRaisesRegex(MODULE.LedgerError, "PROJECT_CANDIDATE_AUTHORITY_OVERCLAIM"):
            MODULE._verify_project_candidate(
                candidate, project_id="salesforce-tools", spec_bytes=spec_bytes
            )

        candidate = copy.deepcopy(project["evidence"]["projectCandidate"])
        candidate["adoptionProofCredit"] = True
        with self.assertRaisesRegex(MODULE.LedgerError, "PROJECT_CANDIDATE_PROOF_OVERCLAIM"):
            MODULE._verify_project_candidate(
                candidate, project_id="salesforce-tools", spec_bytes=spec_bytes
            )

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
