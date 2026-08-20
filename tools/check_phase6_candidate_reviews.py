#!/usr/bin/env python3
"""Verify the R26 phase-6 read-only local candidate review receipts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BATCH_PATH = "adoption/phase6/r26-local-candidate-review-receipts.json"
LEDGER_PATH = "adoption/universal-token-control-r26.json"
SCHEMA = "fleet-r26-local-candidate-review-batch/v1"
BASE_COMMIT = "e4e7f9363185a5e10bb3a92167c785ef29caf2b7"
BASE_TREE = "5233fa0515fcef7b69e70a007f25e6bb78190c42"
BASE_PARENT = "5ac7036705338cfe3370f5fddda224e07d5d1bdd"
LEDGER_BLOB = "333cc6d47e99a857b64150a87bd9f834590256e1"
LEDGER_SHA256 = "a41f68c691159813ee58198ca1286683dcb1d20ea53cbe42f42a232cb2cd95ce"
R26_CANDIDATE = "e70a044f31dd2f43ab7c716d63a4eb89318c61b6"
R26_MERGE = "909f769d02e8412e51e28e242cfa8d00dadc9a3d"
ALLOWED_PATHS = {
    "adoption/phase6/README.md",
    BATCH_PATH,
    "tests/test_phase6_candidate_reviews.py",
    "tools/check_phase6_candidate_reviews.py",
}
AUTHORITY_KEYS = {
    "projectDisposition", "projectAdoption", "fleetAdoption", "runtime", "activation",
    "provider", "authentication", "scheduler", "gate", "pushMergePublish",
}
EXPECTED_COUNTS = {"ADOPT": 0, "DISTINGUISH": 5, "MISSING": 0, "REJECT": 0, "STALE": 4}
PROJECT_PATHS = {
    "salesforce-tools": Path(
        r"C:\code\softwarefactory-fleet-doctrine-worktrees\salesforce-adoption-gap-37a2070-20260819"
    ),
    "cloudvore": Path(
        r"C:\code\softwarefactory-fleet-doctrine-worktrees\cloudvore-r28-install-census-candidate-20260819"
    ),
}
EXPECTED = {
    "salesforce-tools": {
        "evidenceKind": "PROJECT_DISTINGUISH_EVIDENCE_CANDIDATE",
        "reviewScope": "ZERO_AUTHORITY_EVIDENCE_CORRECTNESS_ONLY_NOT_ADOPTION_OR_INSTALLATION",
        "commit": "d8542ccfb9dde81dcdd57bf55c7959c3b0d521c4",
        "tree": "4ec6a0433d622f9658789a75403030f8251926b8",
        "parent": "1675e513159d3c6a12e70659c9c0fba9807e7b5a",
        "base": "37a20709d021a7b0c44dbad2e6f2131bd328e4fd",
        "changedPaths": [
            "docs/provider-control/R26-CURRENT-STATE-EVIDENCE.json",
            "docs/provider-control/R26-DISPOSITION-CANDIDATE.md",
            "tools/provider-control/test-r26-disposition-candidate.ps1",
        ],
        "artifacts": [
            {
                "path": "docs/provider-control/R26-CURRENT-STATE-EVIDENCE.json",
                "gitBlobOid": "9c42948bb4c45ab595d62fae1a48e47aa8911102",
                "bytes": 15365,
                "sha256": "948d4af9a388bdf1e7a9ffb36a6cd15d875726ef698515e9e9dc0366a00b90f5",
            },
            {
                "path": "docs/provider-control/R26-DISPOSITION-CANDIDATE.md",
                "gitBlobOid": "43abbd35d47e2e2472fbf57d3fb246404180d59e",
                "bytes": 7344,
                "sha256": "4bdaef900c97e9dabfb6ced17891b19d9a1bceaa3a0ab847e8146ac981b8450c",
            },
            {
                "path": "tools/provider-control/test-r26-disposition-candidate.ps1",
                "gitBlobOid": "be996a114c47ad48ac090b8e66e84e154c815f5a",
                "bytes": 48080,
                "sha256": "725b3d0c0b4d1edb777a9c8cb87046dff36baf713d05284bb2fd0ad742a1e804",
            },
        ],
        "semanticFindings": {
            "candidateStatus": "DISTINGUISH_CANDIDATE_ZERO_AUTHORITY",
            "persistentGateTreatment": "CLOSED_BY_ABSENCE_WITHOUT_PERSISTENT_GATE_CREDIT",
            "launcherSurfaceCount": 4,
            "completeLauncherSurfaceCount": 0,
            "directLauncherClassCount": 5,
            "completeDirectLauncherClassCount": 0,
            "knownMissingAdoptionBlockerCount": 25,
            "missingAdoptionProofSetComplete": False,
            "llmFailoverUniversalProviderOrSessionChokeClaimed": False,
            "unobservedLaunchPathsMayExist": True,
            "allAuthorityMembersFalse": True,
        },
    },
    "cloudvore": {
        "evidenceKind": "ADOPTION_BLOCKER_OBSERVATIONAL_LOWER_BOUND",
        "reviewScope": "ZERO_AUTHORITY_BLOCKER_EVIDENCE_ONLY_NOT_A_PROJECT_DISPOSITION",
        "commit": "54a7a45c4b223a0d8647bfc61c732dc5325f8d30",
        "tree": "c25cea7b2333be786c8ea693f739ae12b25c19c5",
        "parent": "1a01c945756f80737199cd6a9383d74763f9f147",
        "base": "db3e5fd155a6efe41947f5d4aa0bbc4a3d2098a8",
        "changedPaths": [
            "knowledge/universal-token-control-r28-installation-census-blocker-2026-08-19.json",
            "tools/universal-token-control-r28-installation-census-blocker.tests.py",
        ],
        "artifacts": [
            {
                "path": "knowledge/universal-token-control-r28-installation-census-blocker-2026-08-19.json",
                "gitBlobOid": "e2d109c378086684e6da1910088abe6f866ac75c",
                "bytes": 18147,
                "sha256": "952ade087659f24ac3761f6aaeed9eb27a03851f6fa55c30ef5c0491a0f51959",
            },
            {
                "path": "tools/universal-token-control-r28-installation-census-blocker.tests.py",
                "gitBlobOid": "1f330cf1fa7768c7b5c891ade4c8270a5d705a00",
                "bytes": 224300,
                "sha256": "41f31810d601fe27f4b2ef5c3e529a2e14010322d0bc78b85e23a01b2e026974",
            },
        ],
        "semanticFindings": {
            "candidateStatus": "PINNED_BLOCKER_ZERO_AUTHORITY",
            "scannerEvidenceKind": "OBSERVATIONAL_PROCESS_CAPABILITY_LOWER_BOUND",
            "scannerCoverageComplete": False,
            "knownProviderSetLowerBound": True,
            "unresolvedSetLowerBound": True,
            "unobservedExecutionPathsMayExist": True,
            "knownScannerLimitationCount": 6,
            "observedContentInferenceLauncherCount": 3,
            "allObservedContentLaunchersBypassAcceptedSupervisor": True,
            "surfaceClassCount": 4,
            "completeSurfaceClassCount": 0,
            "hostInstalled": False,
            "installedManifestPresent": False,
            "directInvocationImpossible": False,
            "adoptionGapClosed": False,
            "allAuthorityMembersFalse": True,
        },
    },
}


class Phase6Error(ValueError):
    pass


def _pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in values:
        if key in result:
            raise Phase6Error("DUPLICATE_KEY")
        result[key] = value
    return result


def load_json(raw: bytes) -> dict[str, Any]:
    try:
        value = json.loads(raw, object_pairs_hook=_pairs)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise Phase6Error("JSON_INVALID") from exc
    if not isinstance(value, dict):
        raise Phase6Error("JSON_ROOT_INVALID")
    return value


def _git(root: Path, *args: str, text: bool = False) -> bytes | str:
    run = subprocess.run(
        ["git", "-c", "safe.directory=*", "--no-replace-objects", *args],
        cwd=root, capture_output=True, check=False, text=text,
        encoding="utf-8" if text else None,
    )
    if run.returncode != 0:
        raise Phase6Error("GIT_COMMAND_FAILED")
    return run.stdout


def _blob(root: Path, treeish: str, path: str) -> bytes:
    return _git(root, "cat-file", "blob", f"{treeish}:{path}")  # type: ignore[return-value]


def _oid(root: Path, treeish: str, path: str) -> str:
    return str(_git(root, "rev-parse", f"{treeish}:{path}", text=True)).strip()


def _tuple(root: Path, commit: str) -> tuple[str, list[str]]:
    lines = str(_git(root, "show", "-s", "--format=%T%n%P", commit, text=True)).splitlines()
    if len(lines) != 2:
        raise Phase6Error("COMMIT_TUPLE_INVALID")
    return lines[0], lines[1].split() if lines[1] else []


def _exact_authority(value: Any) -> None:
    if not isinstance(value, dict) or set(value) != AUTHORITY_KEYS:
        raise Phase6Error("AUTHORITY_KEYS_INVALID")
    if any(member is not False for member in value.values()):
        raise Phase6Error("AUTHORITY_OVERCLAIM")


def _verify_base(batch: dict[str, Any], treeish: str) -> None:
    expected = {
        "doctrineCommit": BASE_COMMIT,
        "doctrineTree": BASE_TREE,
        "ledgerPath": LEDGER_PATH,
        "ledgerGitBlobOid": LEDGER_BLOB,
        "ledgerGitBlobSha256": LEDGER_SHA256,
        "r26Candidate": R26_CANDIDATE,
        "r26Merge": R26_MERGE,
    }
    if batch["frozenBase"] != expected:
        raise Phase6Error("FROZEN_BASE_MISMATCH")
    if _tuple(ROOT, BASE_COMMIT) != (BASE_TREE, [BASE_PARENT]):
        raise Phase6Error("BASE_OBJECT_MISMATCH")
    if _oid(ROOT, treeish, LEDGER_PATH) != LEDGER_BLOB:
        raise Phase6Error("LEDGER_CHANGED")
    if hashlib.sha256(_blob(ROOT, treeish, LEDGER_PATH)).hexdigest() != LEDGER_SHA256:
        raise Phase6Error("LEDGER_CHANGED")
    changed = set(
        str(_git(ROOT, "diff", "--name-only", f"{BASE_COMMIT}..{treeish}", text=True)).splitlines()
    )
    if not changed.issubset(ALLOWED_PATHS):
        raise Phase6Error("PHASE6_SCOPE_VIOLATION")


def _verify_review(review: Any) -> None:
    if not isinstance(review, dict):
        raise Phase6Error("REVIEW_INVALID")
    required = {
        "projectId", "evidenceKind", "verdict", "reviewScope", "subject", "artifacts",
        "executionEvidence", "semanticFindings", "dispositionTreatment", "nextLawfulActions",
        "authority",
    }
    if set(review) != required:
        raise Phase6Error("REVIEW_KEYS_INVALID")
    project_id = review["projectId"]
    if project_id not in EXPECTED:
        raise Phase6Error("PROJECT_SET_INVALID")
    expected = EXPECTED[project_id]
    if review["evidenceKind"] != expected["evidenceKind"] or review["verdict"] != "ACCEPT":
        raise Phase6Error("VERDICT_INVALID")
    if review["reviewScope"] != expected["reviewScope"]:
        raise Phase6Error("REVIEW_SCOPE_INVALID")
    subject = review["subject"]
    if (
        subject["commit"] != expected["commit"]
        or subject["tree"] != expected["tree"]
        or subject["parent"] != expected["parent"]
        or subject["observedProjectBase"] != expected["base"]
        or subject["changedPaths"] != expected["changedPaths"]
        or subject["remoteTrackingRefContainsSubject"] is not False
        or subject["networkRemoteVerified"] is not False
        or subject["worktreeCleanAtReview"] is not True
    ):
        raise Phase6Error("SUBJECT_BINDING_INVALID")
    if review["artifacts"] != expected["artifacts"]:
        raise Phase6Error("ARTIFACT_BINDING_INVALID")
    if review["semanticFindings"] != expected["semanticFindings"]:
        raise Phase6Error("SEMANTIC_FINDING_INVALID")
    executions = review["executionEvidence"]
    if not isinstance(executions, list) or not executions:
        raise Phase6Error("EXECUTION_EVIDENCE_INVALID")
    for execution in executions:
        if execution.get("exitCode") != 0:
            raise Phase6Error("EXECUTION_NOT_PASSING")
        if "hostileControlsTotal" in execution and (
            execution["hostileControlsPassed"] != execution["hostileControlsTotal"]
        ):
            raise Phase6Error("HOSTILE_CONTROL_FAILURE")
        if "testCasesTotal" in execution and execution["testCasesPassed"] != execution["testCasesTotal"]:
            raise Phase6Error("TEST_CASE_FAILURE")
    treatment = review["dispositionTreatment"]
    if treatment["currentLedgerStatus"] != "DISTINGUISH":
        raise Phase6Error("LEDGER_STATUS_INVALID")
    if any(
        treatment[field] is not False
        for field in (
            "ledgerStatusChangeAuthorized", "publicationAuthority", "adoptionCredit",
            "installationCredit",
        )
    ):
        raise Phase6Error("TREATMENT_OVERCLAIM")
    if project_id == "salesforce-tools":
        if treatment["candidateDispositionKind"] != "DISTINGUISH" or not str(
            treatment["candidateDisposition"]
        ).startswith(f"DISTINGUISH({R26_MERGE}, "):
            raise Phase6Error("SALESFORCE_DISPOSITION_INVALID")
    elif treatment["candidateDispositionKind"] is not None or treatment["candidateDisposition"] is not None:
        raise Phase6Error("CLOUDVORE_DISPOSITION_FABRICATED")
    if not isinstance(review["nextLawfulActions"], list) or len(review["nextLawfulActions"]) != 4:
        raise Phase6Error("NEXT_ACTIONS_INVALID")
    _exact_authority(review["authority"])


def verify_batch(batch: dict[str, Any], treeish: str = "HEAD") -> None:
    if set(batch) != {"schema", "status", "frozenBase", "capture", "summary", "reviews"}:
        raise Phase6Error("ROOT_KEYS_INVALID")
    if batch["schema"] != SCHEMA or batch["status"] != "TWO_READ_ONLY_ACCEPTS_ZERO_AUTHORITY":
        raise Phase6Error("ROOT_IDENTITY_INVALID")
    _verify_base(batch, treeish)
    capture = batch["capture"]
    if capture["reviewMode"] != "READ_ONLY_EXACT_OBJECT_AND_SEMANTIC_REVIEW":
        raise Phase6Error("CAPTURE_MODE_INVALID")
    for field in (
        "networkInspectionPerformed", "providerInvocationPerformed", "authenticationPerformed",
        "projectMutationPerformed", "runtimeMutationPerformed", "scheduledTaskMutationPerformed",
        "gateMutationPerformed", "pushMergePublishPerformed",
    ):
        if capture[field] is not False:
            raise Phase6Error("CAPTURE_AUTHORITY_OVERCLAIM")
    expected_summary = {
        "reviewCount": 2,
        "acceptedEvidenceScopes": 2,
        "projectDispositionCandidatesAccepted": 1,
        "blockerEvidenceCandidatesAccepted": 1,
        "ledgerStatusChangesAuthorized": 0,
        "adoptionClaims": 0,
        "installationClaims": 0,
        "runtimeAuthorityClaims": 0,
        "canonicalLedgerCounts": EXPECTED_COUNTS,
    }
    if batch["summary"] != expected_summary:
        raise Phase6Error("SUMMARY_INVALID")
    ledger = load_json(_blob(ROOT, treeish, LEDGER_PATH))
    if ledger.get("summary", {}).get("counts") != EXPECTED_COUNTS:
        raise Phase6Error("LEDGER_COUNTS_INVALID")
    reviews = batch["reviews"]
    if not isinstance(reviews, list) or [item.get("projectId") for item in reviews] != [
        "salesforce-tools", "cloudvore",
    ]:
        raise Phase6Error("PROJECT_SET_INVALID")
    for review in reviews:
        _verify_review(review)


def verify_local_projects(batch: dict[str, Any]) -> None:
    reviews = {review["projectId"]: review for review in batch["reviews"]}
    for project_id, root in PROJECT_PATHS.items():
        if not root.is_dir():
            raise Phase6Error(f"LOCAL_PROJECT_MISSING:{project_id}")
        review = reviews[project_id]
        commit = review["subject"]["commit"]
        if _tuple(root, commit) != (review["subject"]["tree"], [review["subject"]["parent"]]):
            raise Phase6Error(f"LOCAL_COMMIT_TUPLE_MISMATCH:{project_id}")
        changed = str(
            _git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", commit, text=True)
        ).splitlines()
        if changed != review["subject"]["changedPaths"]:
            raise Phase6Error(f"LOCAL_CHANGED_PATHS_MISMATCH:{project_id}")
        for artifact in review["artifacts"]:
            if _oid(root, commit, artifact["path"]) != artifact["gitBlobOid"]:
                raise Phase6Error(f"LOCAL_ARTIFACT_OID_MISMATCH:{project_id}")
            raw = _blob(root, commit, artifact["path"])
            if len(raw) != artifact["bytes"] or hashlib.sha256(raw).hexdigest() != artifact["sha256"]:
                raise Phase6Error(f"LOCAL_ARTIFACT_BYTES_MISMATCH:{project_id}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--treeish", default="HEAD")
    parser.add_argument("--verify-local-projects", action="store_true")
    args = parser.parse_args()
    try:
        batch = load_json(_blob(ROOT, args.treeish, BATCH_PATH))
        verify_batch(batch, args.treeish)
        if args.verify_local_projects:
            verify_local_projects(batch)
    except Phase6Error as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    suffix = "; local project objects rederived" if args.verify_local_projects else ""
    print("PASS: two exact R26 candidate evidence reviews remain zero-authority" + suffix)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
