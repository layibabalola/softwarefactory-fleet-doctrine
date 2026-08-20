#!/usr/bin/env python3
"""Verify the R26 phase-6 read-only local candidate review receipts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BATCH_PATH = "adoption/phase6/r26-local-candidate-review-receipts.json"
BATCH_BLOB = "c10b1b7530e0d9695118a02dd21842e4fc1493e0"
BATCH_BYTES = 11174
BATCH_SHA256 = "16b1b3c033d2909d3fa0b3d10b845673dca8183607555525f04e9f52ab029623"
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
    ".github/workflows/disposition-intake.yml",
    "adoption/README.md",
    "adoption/phase6/README.md",
    BATCH_PATH,
    "adoption/phase7/README.md",
    "adoption/phase7/requests/adobe-ingester.json",
    "adoption/phase7/requests/agent-bridge.json",
    "adoption/phase7/requests/airmypc.json",
    "adoption/phase7/requests/conjugal.json",
    "adoption/phase8/README.md",
    "tests/test_phase6_candidate_reviews.py",
    "tests/test_phase7_owner_publication_requests.py",
    "tests/test_phase8_integration.py",
    "tools/check_phase2_disposition_batch.py",
    "tools/check_phase3_disposition_batch.py",
    "tools/check_phase5_stale_reconciliation.py",
    "tools/check_phase6_candidate_reviews.py",
    "tools/check_phase7_owner_publication_requests.py",
    "tools/check_phase8_integration.py",
}
AUTHORITY_KEYS = {
    "projectDisposition", "projectAdoption", "fleetAdoption", "runtime", "activation",
    "provider", "authentication", "scheduler", "gate", "pushMergePublish",
}
EXPECTED_COUNTS = {"ADOPT": 0, "DISTINGUISH": 5, "MISSING": 0, "REJECT": 0, "STALE": 4}
EXPECTED_CAPTURE = {
    "reviewedAt": "2026-08-20T11:04:10.3493913Z",
    "machine": "ULTRA-MAGNUS",
    "reviewer": "codex-fleet-disposition-census-independent-subagent",
    "reviewMode": "READ_ONLY_EXACT_OBJECT_AND_SEMANTIC_REVIEW",
    "networkInspectionPerformed": False,
    "providerInvocationPerformed": False,
    "authenticationPerformed": False,
    "projectMutationPerformed": False,
    "runtimeMutationPerformed": False,
    "scheduledTaskMutationPerformed": False,
    "gateMutationPerformed": False,
    "pushMergePublishPerformed": False,
}
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
        "subject": {
            "remote": "https://github.com/layibabalola/SalesforceSupportTools.git",
            "headMode": "SYMBOLIC_BRANCH",
            "localBranch": "codex/salesforce-adoption-gap-37a2070-20260819",
            "commit": "d8542ccfb9dde81dcdd57bf55c7959c3b0d521c4",
            "tree": "4ec6a0433d622f9658789a75403030f8251926b8",
            "parent": "1675e513159d3c6a12e70659c9c0fba9807e7b5a",
            "observedProjectBase": "37a20709d021a7b0c44dbad2e6f2131bd328e4fd",
            "remoteTrackingRefContainsSubject": False,
            "networkRemoteVerified": False,
            "worktreeCleanAtReview": True,
            "changedPaths": [
                "docs/provider-control/R26-CURRENT-STATE-EVIDENCE.json",
                "docs/provider-control/R26-DISPOSITION-CANDIDATE.md",
                "tools/provider-control/test-r26-disposition-candidate.ps1",
            ],
        },
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
        "executionEvidence": [
            {
                "engine": "PowerShell 7.6.3",
                "command": "pwsh -NoProfile -File .\\tools\\provider-control\\test-r26-disposition-candidate.ps1",
                "exitCode": 0,
                "result": "PASS R26 forward zero-authority disposition candidate",
                "hostileControlsPassed": 41,
                "hostileControlsTotal": 41,
            },
            {
                "engine": "Windows PowerShell 5.1.19041.7663",
                "command": (
                    "powershell -NoProfile -ExecutionPolicy Bypass -File "
                    ".\\tools\\provider-control\\test-r26-disposition-candidate.ps1"
                ),
                "exitCode": 0,
                "result": "PASS R26 forward zero-authority disposition candidate",
                "hostileControlsPassed": 41,
                "hostileControlsTotal": 41,
            },
        ],
        "dispositionTreatment": {
            "currentLedgerStatus": "DISTINGUISH",
            "candidateDispositionKind": "DISTINGUISH",
            "candidateDisposition": (
                "DISTINGUISH(909f769d02e8412e51e28e242cfa8d00dadc9a3d, "
                "R26_CANDIDATE_ZERO_AUTHORITY_CURRENT_CONTENT_WORK_PROVIDER_TEST_PROVIDER_ADMIN_"
                "CHAT_SESSION_SCHEDULED_STANDUP_SCHEDULED_FOLLOWUP_APP_WATCH_AND_REPOSITORY_"
                "AGENT_WORKFLOW_LAUNCH_PATHS_REMAIN_OUTSIDE_A_PINNED_FAIL_CLOSED_SUPERVISOR_"
                "KNOWN_MISSING_ADOPTION_BLOCKERS_ENUMERATED_PROOF_SET_NOT_COMPLETE_GATE_TREATED_"
                "CLOSED_BY_ABSENCE_WITHOUT_PERSISTENT_GATE_CREDIT, "
                "SALESFORCE_MAIN_37a20709d021a7b0c44dbad2e6f2131bd328e4fd, "
                "EVIDENCE_SHA256_948d4af9a388bdf1e7a9ffb36a6cd15d875726ef698515e9e9dc0366a00b90f5)"
            ),
            "ledgerStatusChangeAuthorized": False,
            "publicationAuthority": False,
            "adoptionCredit": False,
            "installationCredit": False,
        },
        "nextLawfulActions": [
            "PROJECT_OWNER_MAY_PUBLISH_THE_EXACT_REVIEWED_COMMIT_ON_A_NEW_IMMUTABLE_PROJECT_REF",
            "AFTER_EXACT_REF_VERIFICATION_DOCTRINE_MAY_REPIN_THE_EXISTING_DISTINGUISH_ROW_WITHOUT_STATUS_ADVANCE",
            "BUILD_FAKE_PROVIDER_SEAM_AND_AN_INDEPENDENT_COMPLETE_FOUR_SURFACE_CENSUS_BEFORE_SUPERVISOR_INSTALLATION",
            "KEEP_GATE_CLOSED_AND_EARN_EVERY_R26_ADOPTION_AND_NON_REGRESSION_PROOF_BEFORE_ANY_ADOPT_CLAIM",
        ],
    },
    "cloudvore": {
        "evidenceKind": "ADOPTION_BLOCKER_OBSERVATIONAL_LOWER_BOUND",
        "reviewScope": "ZERO_AUTHORITY_BLOCKER_EVIDENCE_ONLY_NOT_A_PROJECT_DISPOSITION",
        "subject": {
            "remote": "https://github.com/layibabalola/Cloudvore.git",
            "headMode": "SYMBOLIC_BRANCH",
            "localBranch": "codex/r28-install-census-candidate-20260819",
            "commit": "54a7a45c4b223a0d8647bfc61c732dc5325f8d30",
            "tree": "c25cea7b2333be786c8ea693f739ae12b25c19c5",
            "parent": "1a01c945756f80737199cd6a9383d74763f9f147",
            "observedProjectBase": "db3e5fd155a6efe41947f5d4aa0bbc4a3d2098a8",
            "acceptedClosedSupervisorCommit": "ed1119845d43fa1042d69c6f6d3ae9e700b1db5f",
            "acceptedClosedSupervisorTree": "0001966e4f155f4b3ef2feae2e5d99f3522eb4c6",
            "remoteTrackingRefContainsSubject": False,
            "networkRemoteVerified": False,
            "worktreeCleanAtReview": True,
            "changedPaths": [
                "knowledge/universal-token-control-r28-installation-census-blocker-2026-08-19.json",
                "tools/universal-token-control-r28-installation-census-blocker.tests.py",
            ],
        },
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
        "executionEvidence": [
            {
                "engine": "CPython 3.14.6",
                "command": (
                    "PYTHONDONTWRITEBYTECODE=1 python "
                    ".\\tools\\universal-token-control-r28-installation-census-blocker.tests.py"
                ),
                "exitCode": 0,
                "result": "Ran 17 tests in 78.193s - OK",
                "testCasesPassed": 17,
                "testCasesTotal": 17,
                "adverseFamiliesPassed": [
                    "DUPLICATE_JSON",
                    "INSTALLATION_AND_DIRECT_INVOCATION_OVERCLAIM",
                    "LAUNCHER_OMISSION_DUPLICATE_DRIFT_AND_ROUTE_OVERCLAIM",
                    "PROCESS_CAPABILITY_OMISSION_DRIFT_AND_OVERCLAIM",
                    "SCANNER_KNOWN_LIMITATIONS_AND_POSITIVE_CONTROLS",
                    "SURFACE_OMISSION_AND_HOST_COMPLETENESS_OVERCLAIM",
                    "NON_REGRESSION_AND_AUTHORITY_OVERCLAIM",
                ],
            }
        ],
        "dispositionTreatment": {
            "currentLedgerStatus": "DISTINGUISH",
            "candidateDispositionKind": None,
            "candidateDisposition": None,
            "ledgerStatusChangeAuthorized": False,
            "publicationAuthority": False,
            "adoptionCredit": False,
            "installationCredit": False,
        },
        "nextLawfulActions": [
            "KEEP_THIS_ACCEPTED_SUBJECT_CLASSIFIED_AS_BLOCKER_EVIDENCE_NOT_A_DISPOSITION",
            "BUILD_EXACT_PREIMAGE_BOUND_GATE_FIRST_INTEGRATION_FOR_THE_THREE_KNOWN_CONTENT_LAUNCHERS",
            "PRODUCE_AN_INDEPENDENT_COMPLETE_CENSUS_METHOD_AND_CLOSED_ROUTING_FOR_ALL_DISCOVERED_EXECUTION_PATHS",
            "PRODUCE_A_HOST_LOCAL_CLOSED_INSTALL_MANIFEST_AND_ALL_R26_NON_REGRESSION_AND_ADOPTION_PROOFS_BEFORE_ANY_ADOPT_CLAIM",
        ],
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


def _type_exact_equal(actual: Any, expected: Any) -> bool:
    """Compare JSON-compatible values without Python's bool/int aliasing."""

    if type(actual) is not type(expected):
        return False
    if isinstance(expected, dict):
        return set(actual) == set(expected) and all(
            _type_exact_equal(actual[key], expected[key]) for key in expected
        )
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(
            _type_exact_equal(actual_item, expected_item)
            for actual_item, expected_item in zip(actual, expected, strict=True)
        )
    return actual == expected


def _git_environment() -> dict[str, str]:
    """Return a noninteractive Git environment that cannot redirect the inspected repository."""

    environment = os.environ.copy()
    redirected = {
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_COMMON_DIR",
        "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_REPLACE_REF_BASE",
        "GIT_INDEX_FILE",
        "GIT_NAMESPACE",
        "GIT_CEILING_DIRECTORIES",
        "GIT_EXEC_PATH",
    }
    for key in tuple(environment):
        if key in redirected or key.startswith("GIT_CONFIG"):
            environment.pop(key, None)
    environment["GIT_NO_REPLACE_OBJECTS"] = "1"
    environment["GIT_CONFIG_NOSYSTEM"] = "1"
    environment["GIT_CONFIG_GLOBAL"] = os.devnull
    environment["GIT_TERMINAL_PROMPT"] = "0"
    environment["GCM_INTERACTIVE"] = "Never"
    return environment


def _git(root: Path, *args: str, text: bool = False) -> bytes | str:
    try:
        resolved_root = root.resolve(strict=True)
        if not resolved_root.is_dir():
            raise OSError("not a directory")
        run = subprocess.run(
            [
                "git",
                "--no-replace-objects",
                "-c",
                f"safe.directory={resolved_root.as_posix()}",
                *args,
            ],
            cwd=resolved_root,
            env=_git_environment(),
            capture_output=True,
            check=False,
            text=text,
            encoding="utf-8" if text else None,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Phase6Error("GIT_COMMAND_FAILED") from exc
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


def _verify_linear_lineage(treeish: str) -> str:
    resolved = str(_git(ROOT, "rev-parse", "--verify", f"{treeish}^{{commit}}", text=True)).strip()
    merge_base = str(_git(ROOT, "merge-base", BASE_COMMIT, resolved, text=True)).strip()
    if merge_base != BASE_COMMIT:
        raise Phase6Error("BASE_NOT_ANCESTOR")
    rows = str(
        _git(ROOT, "rev-list", "--reverse", "--parents", f"{BASE_COMMIT}..{resolved}", text=True)
    ).splitlines()
    if not rows:
        raise Phase6Error("PHASE6_LINEAGE_EMPTY")
    prior = BASE_COMMIT
    for row in rows:
        fields = row.split()
        if len(fields) != 2 or fields[1] != prior:
            raise Phase6Error("PHASE6_LINEAGE_NOT_SOLE_PARENT")
        prior = fields[0]
    if prior != resolved:
        raise Phase6Error("PHASE6_LINEAGE_TIP_MISMATCH")
    return resolved


def _verify_receipt_blob(treeish: str) -> None:
    if _oid(ROOT, treeish, BATCH_PATH) != BATCH_BLOB:
        raise Phase6Error("RECEIPT_BLOB_OID_MISMATCH")
    raw = _blob(ROOT, treeish, BATCH_PATH)
    if len(raw) != BATCH_BYTES:
        raise Phase6Error("RECEIPT_BYTES_MISMATCH")
    if hashlib.sha256(raw).hexdigest() != BATCH_SHA256:
        raise Phase6Error("RECEIPT_SHA256_MISMATCH")


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
    if not _type_exact_equal(batch["frozenBase"], expected):
        raise Phase6Error("FROZEN_BASE_MISMATCH")
    if _tuple(ROOT, BASE_COMMIT) != (BASE_TREE, [BASE_PARENT]):
        raise Phase6Error("BASE_OBJECT_MISMATCH")
    _verify_linear_lineage(treeish)
    _verify_receipt_blob(treeish)
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
    if not _type_exact_equal(review["subject"], expected["subject"]):
        raise Phase6Error("SUBJECT_BINDING_INVALID")
    if not _type_exact_equal(review["artifacts"], expected["artifacts"]):
        raise Phase6Error("ARTIFACT_BINDING_INVALID")
    if not _type_exact_equal(review["semanticFindings"], expected["semanticFindings"]):
        raise Phase6Error("SEMANTIC_FINDING_INVALID")
    if not _type_exact_equal(review["executionEvidence"], expected["executionEvidence"]):
        raise Phase6Error("EXECUTION_EVIDENCE_INVALID")
    if not _type_exact_equal(review["dispositionTreatment"], expected["dispositionTreatment"]):
        raise Phase6Error("DISPOSITION_TREATMENT_INVALID")
    if not _type_exact_equal(review["nextLawfulActions"], expected["nextLawfulActions"]):
        raise Phase6Error("NEXT_ACTIONS_INVALID")
    _exact_authority(review["authority"])


def verify_batch(batch: dict[str, Any], treeish: str = "HEAD") -> None:
    if set(batch) != {"schema", "status", "frozenBase", "capture", "summary", "reviews"}:
        raise Phase6Error("ROOT_KEYS_INVALID")
    if batch["schema"] != SCHEMA or batch["status"] != "TWO_READ_ONLY_ACCEPTS_ZERO_AUTHORITY":
        raise Phase6Error("ROOT_IDENTITY_INVALID")
    _verify_base(batch, treeish)
    if not _type_exact_equal(batch["capture"], EXPECTED_CAPTURE):
        raise Phase6Error("CAPTURE_BINDING_INVALID")
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
    if not _type_exact_equal(batch["summary"], expected_summary):
        raise Phase6Error("SUMMARY_INVALID")
    ledger = load_json(_blob(ROOT, treeish, LEDGER_PATH))
    if not _type_exact_equal(ledger.get("summary", {}).get("counts"), EXPECTED_COUNTS):
        raise Phase6Error("LEDGER_COUNTS_INVALID")
    reviews = batch["reviews"]
    if (
        not isinstance(reviews, list)
        or any(not isinstance(item, dict) for item in reviews)
        or [item.get("projectId") for item in reviews] != ["salesforce-tools", "cloudvore"]
    ):
        raise Phase6Error("PROJECT_SET_INVALID")
    for review in reviews:
        _verify_review(review)


def _verify_local_identity(root: Path, project_id: str, subject: dict[str, Any]) -> None:
    commit = subject["commit"]
    try:
        resolved_root = root.resolve(strict=True)
    except OSError as exc:
        raise Phase6Error(f"LOCAL_ROOT_MISMATCH:{project_id}") from exc
    top_level = Path(
        str(_git(resolved_root, "rev-parse", "--show-toplevel", text=True)).strip()
    ).resolve(strict=True)
    if os.path.normcase(str(top_level)) != os.path.normcase(str(resolved_root)):
        raise Phase6Error(f"LOCAL_ROOT_MISMATCH:{project_id}")
    if str(_git(resolved_root, "rev-parse", "--is-inside-work-tree", text=True)).strip() != "true":
        raise Phase6Error(f"LOCAL_ROOT_MISMATCH:{project_id}")
    if subject["headMode"] != "SYMBOLIC_BRANCH":
        raise Phase6Error(f"LOCAL_HEAD_MODE_MISMATCH:{project_id}")
    branch = subject["localBranch"]
    full_branch = f"refs/heads/{branch}"
    if str(_git(resolved_root, "symbolic-ref", "--quiet", "HEAD", text=True)).strip() != full_branch:
        raise Phase6Error(f"LOCAL_BRANCH_MISMATCH:{project_id}")
    if str(
        _git(resolved_root, "rev-parse", "--verify", "HEAD^{commit}", text=True)
    ).strip() != commit:
        raise Phase6Error(f"LOCAL_HEAD_MISMATCH:{project_id}")
    if str(
        _git(resolved_root, "rev-parse", "--verify", f"{full_branch}^{{commit}}", text=True)
    ).strip() != commit:
        raise Phase6Error(f"LOCAL_BRANCH_TIP_MISMATCH:{project_id}")
    fetch_urls = str(
        _git(resolved_root, "remote", "get-url", "--all", "origin", text=True)
    ).splitlines()
    push_urls = str(
        _git(resolved_root, "remote", "get-url", "--push", "--all", "origin", text=True)
    ).splitlines()
    if fetch_urls != [subject["remote"]] or push_urls != [subject["remote"]]:
        raise Phase6Error(f"LOCAL_ORIGIN_MISMATCH:{project_id}")
    if str(_git(resolved_root, "status", "--porcelain=v1", "--untracked-files=all", text=True)):
        raise Phase6Error(f"LOCAL_WORKTREE_NOT_CLEAN:{project_id}")
    remote_refs = str(
        _git(
            resolved_root,
            "for-each-ref",
            f"--contains={commit}",
            "--format=%(refname)",
            "refs/remotes",
            text=True,
        )
    ).splitlines()
    if subject["remoteTrackingRefContainsSubject"] is not False or remote_refs:
        raise Phase6Error(f"LOCAL_REMOTE_TRACKING_CONTAINMENT_MISMATCH:{project_id}")
    if subject["networkRemoteVerified"] is not False:
        raise Phase6Error(f"NETWORK_REMOTE_VERIFICATION_OVERCLAIM:{project_id}")


def verify_local_projects(batch: dict[str, Any]) -> None:
    reviews = {review["projectId"]: review for review in batch["reviews"]}
    for project_id, root in PROJECT_PATHS.items():
        if not root.is_dir():
            raise Phase6Error(f"LOCAL_PROJECT_MISSING:{project_id}")
        review = reviews[project_id]
        subject = review["subject"]
        commit = subject["commit"]
        _verify_local_identity(root, project_id, subject)
        if _tuple(root, commit) != (subject["tree"], [subject["parent"]]):
            raise Phase6Error(f"LOCAL_COMMIT_TUPLE_MISMATCH:{project_id}")
        changed = str(
            _git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", commit, text=True)
        ).splitlines()
        if changed != subject["changedPaths"]:
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
    suffix = (
        "; local objects, branch/origin, cleanliness, and remote-tracking containment rederived; "
        "network remotes not queried"
        if args.verify_local_projects
        else ""
    )
    print("PASS: two exact R26 candidate evidence reviews remain zero-authority" + suffix)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
