#!/usr/bin/env python3
"""Verify Phase 7 owner-publication requests remain request-only and zero-authority."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REQUEST_DIR = "adoption/phase7/requests"
SCHEMA = "fleet-r26-owner-publication-request/v1"
BASE_COMMIT = "e4e7f9363185a5e10bb3a92167c785ef29caf2b7"
BASE_TREE = "5233fa0515fcef7b69e70a007f25e6bb78190c42"
BASE_PARENT = "5ac7036705338cfe3370f5fddda224e07d5d1bdd"
R26_CANDIDATE = "e70a044f31dd2f43ab7c716d63a4eb89318c61b6"
R26_MERGE = "909f769d02e8412e51e28e242cfa8d00dadc9a3d"
LEDGER_PATH = "adoption/universal-token-control-r26.json"
LEDGER_BLOB_OID = "333cc6d47e99a857b64150a87bd9f834590256e1"
CAPTURED_AT = "2026-08-20T06:21:30-05:00"
PROJECT_IDS = {"adobe-ingester", "agent-bridge", "airmypc", "conjugal"}
REQUEST_PATHS = {f"{REQUEST_DIR}/{project_id}.json" for project_id in PROJECT_IDS}
PROTECTED_BLOBS = {
    LEDGER_PATH: LEDGER_BLOB_OID,
    "adoption/phase2/r26-project-disposition-intake.json": "6e3fe9d429dfd578c43d8ebaf371074a45b662b1",
    "adoption/phase5/r26-stale-project-reconciliation.json": "7487bce84580c0ef01f45ea8609876a80f60b375",
    "specs/adobe-ingester.md": "f91bbd6be126dc1513c299069677b986b90cd716",
    "specs/agent-bridge.md": "b2070f78be89aa21cf2e6e6e270b03851bb0d029",
    "specs/airmypc.md": "f173f47ca2c045fe24b6ec9383614585d10775d8",
    "specs/conjugal.md": "ffca347d90689766a3418a65a0f12e464bfdfe78",
}
PHASE6_INTEGRATION_PATHS = {
    "adoption/README.md",
    "adoption/phase6/README.md",
    "adoption/phase6/r26-local-candidate-review-receipts.json",
    "tests/test_phase6_candidate_reviews.py",
    "tools/check_phase6_candidate_reviews.py",
}
PHASE8_INTEGRATION_PATHS = {
    "adoption/phase8/README.md",
    "tests/test_phase8_integration.py",
    "tools/check_phase8_integration.py",
}
MANIFEST_BINDING_REPAIR_PATHS = {
    "manifests/universal-provider-control-reconciliation-r26.json",
    "tests/test_universal_manifest_spec_bindings.py",
}
PHASE9_INTEGRATION_PATHS = {
    "tests/test_phase9_integration.py",
    "tools/check_phase9_integration.py",
}
PHASE10_INTEGRATION_PATHS = {
    "adoption/phase10/README.md",
    "adoption/phase10/r26-local-candidate-review-receipts.json",
    "tests/test_phase10_integration.py",
    "tools/check_phase10_integration.py",
}
ALLOWED_PHASE7_PATHS = REQUEST_PATHS | PHASE6_INTEGRATION_PATHS | PHASE8_INTEGRATION_PATHS | {
    ".github/workflows/disposition-intake.yml",
    "adoption/phase7/README.md",
    "tests/test_phase7_owner_publication_requests.py",
    "tools/check_phase2_disposition_batch.py",
    "tools/check_phase3_disposition_batch.py",
    "tools/check_phase5_stale_reconciliation.py",
    "tools/check_phase7_owner_publication_requests.py",
} | MANIFEST_BINDING_REPAIR_PATHS | PHASE9_INTEGRATION_PATHS | PHASE10_INTEGRATION_PATHS
TOP_KEYS = {
    "schema",
    "requestId",
    "projectId",
    "status",
    "frozenDoctrine",
    "currentEvidence",
    "ownerPublicationContract",
    "queue",
    "authority",
    "prohibitedClaims",
}
FROZEN_KEYS = {
    "baseCommit",
    "baseTree",
    "baseParent",
    "r26Candidate",
    "r26Merge",
    "ledgerPath",
    "ledgerGitBlobOid",
    "ledgerProjectRowCanonicalSha256",
    "ledgerStatus",
    "blockerCode",
}
CURRENT_EVIDENCE_KEYS = {
    "classification",
    "auditCapturedAt",
    "remoteObservedAt",
    "machine",
    "host",
    "repositoryRoot",
    "remote",
    "remoteFreshness",
    "observedRefs",
    "historicalObjects",
    "caveat",
}
CONTRACT_KEYS = {
    "exactIdentityBinding",
    "currentDispositionBinding",
    "artifactManifestBinding",
    "nonRegressionBinding",
    "runtimeAndInstallationBinding",
    "projectAuthorityPrerequisites",
}
IDENTITY_FIELDS = [
    "canonicalRepositoryRoot",
    "normalizedRemote",
    "publishedRef",
    "commit",
    "tree",
    "parents",
    "historicalObjectLineageWitness",
]
DISPOSITION_FIELDS = [
    "status",
    "statement",
    "r26Candidate",
    "r26Merge",
    "subjectCommit",
    "subjectTree",
    "publishedAt",
    "ownerIdentity",
]
ARTIFACT_FIELDS = ["path", "gitBlobOid", "bytes", "sha256"]
NON_REGRESSION_AXES = ["model", "effort", "role", "review", "quality", "functionality"]
NON_REGRESSION_FIELDS = ["state", "subject", "evidenceArtifacts", "verdict"]
ADOPT_PROOF_FIELDS = [
    "completeLauncherCensus",
    "pinnedSupervisorInstall",
    "currentClosedGate",
    "requestLevelTokenAccounting",
    "idle1000ZeroInferenceTicks",
    "fullChildLifetimeFencing",
    "rollbackProof",
    "qualityEquivalence",
    "functionalityEquivalence",
    "independentReview",
]
ADOBE_AUTHORITY_FIELDS = [
    "activeWorkOrderId",
    "activeWorkOrderRevision",
    "workOrderStatus",
    "reviewQuorumId",
    "requiredSeats",
    "filledSeats",
    "reviewerIdentities",
    "reviewerIndependence",
    "frozenSubjectCommit",
    "frozenSubjectTree",
]
AUTHORITY_KEYS = {
    "projectDisposition",
    "adoption",
    "runtime",
    "installation",
    "provider",
    "scheduler",
    "gateTransition",
    "repositoryMutation",
    "remoteMutation",
    "publication",
    "message",
}
QUEUE_KEYS = {
    "state",
    "executable",
    "ownerActionRequired",
    "automaticStatusAdvance",
    "writesAuthorized",
    "providerCallsAuthorized",
    "nextLawfulAction",
}
FORMAL_DISPOSITION = re.compile(r"\b(?:ADOPT|DISTINGUISH|REJECT)\s*\(", re.IGNORECASE)
SHA40 = re.compile(r"[0-9a-f]{40}")

PROJECT_BINDINGS = {
    "adobe-ingester": {
        "row": "6e7fa27a699d771c59159f1a9dd325889fb50fcfeaa6578635a05c300bfabf30",
        "blocker": "PROJECT_REPOSITORY_ROOT_UNPUBLISHED_OWNER_WORK_ORDER_AND_QUORUM_REQUIRED",
        "next": "OWNER_MINTS_OR_REPAIRS_ACTIVE_WORK_ORDER_CLOSES_FRESH_REVIEWER_BEARING_Q021_QUORUM_REVALIDATES_EXACT_REMOTE_REF_AND_PUBLISHES_BOUND_PACKET",
    },
    "agent-bridge": {
        "row": "224b2efc7e149a3dd6e1e2800d1635a0cdbd310c4de9a4996028e334348211f8",
        "blocker": "PROJECT_REPOSITORY_ROOT_UNPUBLISHED_CURRENT_R26_DISPOSITION_REQUIRED",
        "next": "OWNER_PUBLISHES_EXACT_REPOSITORY_IDENTITY_CURRENT_REF_OBJECT_LINEAGE_AND_BOUND_R26_DISPOSITION_PACKET",
    },
    "airmypc": {
        "row": "70e2cf180ad3a4b5085a72105cfd5ee585e91cecfc525ce7cefc0e83381f6e82",
        "blocker": "PROJECT_REPOSITORY_ABSENT_CURRENT_R26_DISPOSITION_REQUIRED",
        "next": "OWNER_RESTORES_EXACT_C_TEMP_AIRMYPC_ROOT_OR_PUBLISHES_NORMALIZED_REMOTE_THEN_PUBLISHES_CURRENT_REF_OBJECT_LINEAGE_AND_BOUND_R26_DISPOSITION_PACKET",
    },
    "conjugal": {
        "row": "58afb58093e89992115492c8c70beb0b388980ad366dc5e01645b95d6f51aeb4",
        "blocker": "PROJECT_REPOSITORY_ABSENT_CURRENT_R26_DISPOSITION_REQUIRED",
        "next": "BACHELOR_PROJECT_OWNER_PUBLISHES_EXACT_C_CODE_CONJUGAL_IDENTITY_NORMALIZED_REMOTE_CURRENT_REF_OBJECT_LINEAGE_AND_BOUND_R26_DISPOSITION_PACKET",
    },
}

PROHIBITED_CLAIMS = {
    "adobe-ingester": [
        "NO_DISPOSITION_FROM_REQUEST",
        "NO_CURRENT_REF_FROM_STALE_OBSERVATION",
        "NO_RUNTIME_OR_INSTALLATION_FROM_DISCOVERY",
        "NO_ADOPTION_WITHOUT_PROJECT_OWNED_PROOFS",
        "NO_WORK_ORDER_OR_QUORUM_FROM_FLEET_REQUEST",
    ],
    "agent-bridge": [
        "NO_DISPOSITION_FROM_REQUEST",
        "NO_REPOSITORY_IDENTITY_FROM_PROJECT_NAME",
        "NO_CURRENT_REF_FROM_HISTORICAL_OBJECT_IDENTIFIER",
        "NO_RUNTIME_OR_INSTALLATION_FROM_HISTORICAL_RECEIPTS",
        "NO_ADOPTION_WITHOUT_PROJECT_OWNED_PROOFS",
    ],
    "airmypc": [
        "NO_DISPOSITION_FROM_REQUEST",
        "NO_CURRENT_IDENTITY_FROM_ABSENT_ROOT",
        "NO_REPOSITORY_SUBSTITUTION_BY_SIMILAR_NAME",
        "NO_RUNTIME_OR_INSTALLATION_FROM_R14_PACKET",
        "NO_ADOPTION_WITHOUT_PROJECT_OWNED_PROOFS",
    ],
    "conjugal": [
        "NO_DISPOSITION_FROM_REQUEST",
        "NO_CURRENT_PROJECT_HEAD_FROM_DOCTRINE_OBJECT",
        "NO_REMOTE_IDENTITY_FROM_HOST_OR_PROJECT_NAME",
        "NO_RUNTIME_OR_INSTALLATION_FROM_R14_EVIDENCE",
        "NO_ADOPTION_WITHOUT_PROJECT_OWNED_PROOFS",
    ],
}

CURRENT_EVIDENCE = {
    "adobe-ingester": {
        "classification": "KNOWN_REMOTE_STALE_OBSERVATION_REQUEST_ONLY",
        "auditCapturedAt": CAPTURED_AT,
        "remoteObservedAt": "2026-08-19T16:06:05-05:00",
        "machine": "ULTRA-MAGNUS",
        "host": "virtual-ten",
        "repositoryRoot": None,
        "remote": "https://github.com/layibabalola/adobe-document-cloud-ingester.git",
        "remoteFreshness": "LAST_OBSERVED_2026-08-19_REVALIDATION_REQUIRED",
        "observedRefs": [
            {
                "name": "refs/heads/agent/software-factory-hardening",
                "commit": "0afc24653369eb6129abf7f5263ee37ed1bed7f8",
                "tree": "0cc091c0d738f2d4f6b450e5480bc2b0e3a6149b",
                "parents": ["850a201ebdaca3cb6f4bb7441df6347ce7577cc1"],
                "evidenceStatus": "LAST_PINNED_REMOTE_OBSERVATION_NOT_CURRENT",
            },
            {
                "name": "refs/heads/main",
                "commit": "556f6d1b1ebeab26cda6c400a61e12c9d6a69f76",
                "tree": "2655da443cd7e22e310d432b0aa39ef9e156aa09",
                "parents": ["93dd4f4dd843e4866e408389f571eb63d3aee8a4"],
                "evidenceStatus": "LAST_PINNED_REMOTE_OBSERVATION_NOT_CURRENT",
            },
        ],
        "historicalObjects": [],
        "caveat": "NETWORK_REF_FRESHNESS_UNVERIFIED_NO_CURRENT_DISPOSITION_OR_AUTHORITY_INFERRED",
    },
    "agent-bridge": {
        "classification": "NO_AUTHORITATIVE_CURRENT_PROJECT_IDENTITY",
        "auditCapturedAt": CAPTURED_AT,
        "remoteObservedAt": None,
        "machine": "ULTRA-MAGNUS",
        "host": None,
        "repositoryRoot": None,
        "remote": None,
        "remoteFreshness": "UNPUBLISHED",
        "observedRefs": [],
        "historicalObjects": [
            {"commit": "0623a2c8b0f72661bd05ee8ea3b976be467815bc", "evidenceStatus": "HISTORICAL_UNVERIFIED_PROJECT_OBJECT_IDENTIFIER"},
            {"commit": "13d697c2b778ed566ebb90147aca77bd28f80824", "evidenceStatus": "HISTORICAL_UNVERIFIED_PROJECT_OBJECT_IDENTIFIER"},
            {"commit": "85ee8077d8edb40abd0f0275ec958e3a0b7283ff", "evidenceStatus": "HISTORICAL_UNVERIFIED_PROJECT_OBJECT_IDENTIFIER"},
        ],
        "caveat": "NO_ROOT_REMOTE_CURRENT_REF_OR_ACCESSIBLE_PROJECT_OBJECT_STORE_NO_IDENTITY_INFERRED_FROM_NAMES",
    },
    "airmypc": {
        "classification": "NO_AUTHORITATIVE_CURRENT_PROJECT_IDENTITY",
        "auditCapturedAt": CAPTURED_AT,
        "remoteObservedAt": None,
        "machine": "ULTRA-MAGNUS",
        "host": None,
        "repositoryRoot": "C:\\temp\\AirMyPC",
        "remote": None,
        "remoteFreshness": "UNPUBLISHED",
        "observedRefs": [],
        "historicalObjects": [
            {"commit": "052287887d97a72b416fc7078c4f226509bdea97", "evidenceStatus": "HISTORICAL_PROJECT_BASE_IDENTIFIER_NOT_CURRENT_HEAD"},
        ],
        "caveat": "EXACT_PUBLISHED_ROOT_ABSENT_REMOTE_AND_CURRENT_REF_UNPUBLISHED_NO_RELATED_REPOSITORY_SUBSTITUTION",
    },
    "conjugal": {
        "classification": "NO_AUTHORITATIVE_CURRENT_PROJECT_IDENTITY",
        "auditCapturedAt": CAPTURED_AT,
        "remoteObservedAt": None,
        "machine": "ULTRA-MAGNUS",
        "host": "Bachelor",
        "repositoryRoot": "C:\\code\\Conjugal",
        "remote": None,
        "remoteFreshness": "UNPUBLISHED",
        "observedRefs": [],
        "historicalObjects": [
            {"commit": "37f1246543c86300089b77a51a3b8ad2c5292b8d", "evidenceStatus": "DOCTRINE_LINEAGE_ONLY_NOT_CURRENT_PROJECT_HEAD"},
        ],
        "caveat": "PUBLISHED_ROOT_IS_ON_BACHELOR_AND_NOT_LOCALLY_ACCESSIBLE_REMOTE_UNPUBLISHED_DOCTRINE_OBJECT_IS_NOT_PROJECT_HEAD_PROOF",
    },
}


class Phase7Error(ValueError):
    pass


def _pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in values:
        if key in result:
            raise Phase7Error("DUPLICATE_KEY")
        result[key] = value
    return result


def load_json(raw: bytes) -> dict[str, Any]:
    try:
        value = json.loads(raw, object_pairs_hook=_pairs)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise Phase7Error("JSON_INVALID") from exc
    if not isinstance(value, dict):
        raise Phase7Error("JSON_ROOT_INVALID")
    return value


def _git(args: list[str], *, text: bool = False, error: str = "GIT_OBJECT_UNAVAILABLE") -> bytes | str:
    run = subprocess.run(
        ["git", *args], cwd=ROOT, check=False, capture_output=True,
        text=text, encoding="utf-8" if text else None,
    )
    if run.returncode != 0:
        raise Phase7Error(error)
    return run.stdout


def _blob_spec(treeish: str, path: str) -> str:
    return f":{path}" if treeish == ":" else f"{treeish}:{path}"


def _blob(treeish: str, path: str) -> bytes:
    return _git(["show", _blob_spec(treeish, path)], error="GIT_BLOB_UNAVAILABLE")  # type: ignore[return-value]


def _oid(treeish: str, path: str) -> str:
    value = _git(["rev-parse", _blob_spec(treeish, path)], text=True, error="GIT_BLOB_OID_UNAVAILABLE").strip()
    if SHA40.fullmatch(value) is None:
        raise Phase7Error("GIT_BLOB_OID_INVALID")
    return value


def _commit_tuple(commit: str) -> tuple[str, list[str]]:
    value = _git(["show", "-s", "--format=%T%n%P", commit], text=True, error="BASE_COMMIT_UNAVAILABLE")
    lines = value.splitlines()
    if len(lines) != 2:
        raise Phase7Error("BASE_COMMIT_INVALID")
    return lines[0], lines[1].split() if lines[1] else []


def _is_ancestor(ancestor: str, treeish: str) -> bool:
    descendant = "HEAD" if treeish == ":" else treeish
    return subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=ROOT, check=False, capture_output=True,
    ).returncode == 0


def _changed_paths(treeish: str) -> set[str]:
    args = ["diff", "--cached", "--name-only", BASE_COMMIT] if treeish == ":" else ["diff", "--name-only", f"{BASE_COMMIT}..{treeish}"]
    return set(_git(args, text=True, error="PHASE7_DIFF_UNAVAILABLE").splitlines())


def _tracked_request_paths(treeish: str) -> set[str]:
    if treeish == ":":
        values = _git(["ls-files", REQUEST_DIR], text=True, error="REQUEST_PATH_CENSUS_UNAVAILABLE")
    else:
        values = _git(["ls-tree", "-r", "--name-only", treeish, REQUEST_DIR], text=True, error="REQUEST_PATH_CENSUS_UNAVAILABLE")
    return set(values.splitlines())


def _exact_keys(value: Any, keys: set[str], code: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise Phase7Error(code)
    return value


def _contains_formal_disposition(value: Any) -> bool:
    if isinstance(value, str):
        return FORMAL_DISPOSITION.search(value) is not None
    if isinstance(value, dict):
        return any(_contains_formal_disposition(key) or _contains_formal_disposition(member) for key, member in value.items())
    if isinstance(value, list):
        return any(_contains_formal_disposition(member) for member in value)
    return False


def _verify_repository_scope(treeish: str) -> None:
    if _commit_tuple(BASE_COMMIT) != (BASE_TREE, [BASE_PARENT]):
        raise Phase7Error("FROZEN_BASE_MISMATCH")
    if not _is_ancestor(BASE_COMMIT, treeish):
        raise Phase7Error("FROZEN_BASE_NOT_ANCESTOR")
    if not _changed_paths(treeish).issubset(ALLOWED_PHASE7_PATHS):
        raise Phase7Error("PHASE7_SCOPE_VIOLATION")
    if _tracked_request_paths(treeish) != REQUEST_PATHS:
        raise Phase7Error("REQUEST_SET_MISMATCH")
    for path, expected_oid in PROTECTED_BLOBS.items():
        if _oid(BASE_COMMIT, path) != expected_oid or _oid(treeish, path) != expected_oid:
            raise Phase7Error("PROTECTED_BLOB_DRIFT")


def _verify_frozen(project_id: str, frozen: Any) -> None:
    frozen = _exact_keys(frozen, FROZEN_KEYS, "FROZEN_DOCTRINE_INVALID")
    binding = PROJECT_BINDINGS[project_id]
    expected = {
        "baseCommit": BASE_COMMIT,
        "baseTree": BASE_TREE,
        "baseParent": BASE_PARENT,
        "r26Candidate": R26_CANDIDATE,
        "r26Merge": R26_MERGE,
        "ledgerPath": LEDGER_PATH,
        "ledgerGitBlobOid": LEDGER_BLOB_OID,
        "ledgerProjectRowCanonicalSha256": binding["row"],
        "ledgerStatus": "STALE",
        "blockerCode": binding["blocker"],
    }
    if frozen != expected:
        raise Phase7Error("FROZEN_DOCTRINE_MISMATCH")


def _verify_contract(project_id: str, contract: Any) -> None:
    contract = _exact_keys(contract, CONTRACT_KEYS, "PUBLICATION_CONTRACT_INVALID")

    identity = _exact_keys(contract["exactIdentityBinding"], {"required", "ownerSuppliedFields", "freshReadRequired", "noInferences"}, "IDENTITY_REQUIREMENTS_INCOMPLETE")
    if identity != {"required": True, "ownerSuppliedFields": IDENTITY_FIELDS, "freshReadRequired": True, "noInferences": True}:
        raise Phase7Error("IDENTITY_REQUIREMENTS_INCOMPLETE")

    disposition = _exact_keys(contract["currentDispositionBinding"], {"required", "allowedValues", "ownerSuppliedFields", "projectOwnerChosen"}, "DISPOSITION_REQUIREMENTS_INCOMPLETE")
    if disposition != {"required": True, "allowedValues": ["ADOPT", "DISTINGUISH", "REJECT"], "ownerSuppliedFields": DISPOSITION_FIELDS, "projectOwnerChosen": True}:
        raise Phase7Error("DISPOSITION_REQUIREMENTS_INCOMPLETE")

    artifacts = _exact_keys(contract["artifactManifestBinding"], {"required", "minimumEntries", "ownerSuppliedFields", "exactGitBlobRequired"}, "ARTIFACT_REQUIREMENTS_INCOMPLETE")
    if artifacts != {"required": True, "minimumEntries": 1, "ownerSuppliedFields": ARTIFACT_FIELDS, "exactGitBlobRequired": True}:
        raise Phase7Error("ARTIFACT_REQUIREMENTS_INCOMPLETE")

    non_regression = _exact_keys(contract["nonRegressionBinding"], {"required", "axes", "eachAxisFields", "unknownCannotPass"}, "NON_REGRESSION_REQUIREMENTS_INCOMPLETE")
    if non_regression != {"required": True, "axes": NON_REGRESSION_AXES, "eachAxisFields": NON_REGRESSION_FIELDS, "unknownCannotPass": True}:
        raise Phase7Error("NON_REGRESSION_REQUIREMENTS_INCOMPLETE")

    adopt = _exact_keys(contract["runtimeAndInstallationBinding"], {"requiredForAdopt", "ownerSuppliedFields", "missingMeansDispositionCannotBeAdopt"}, "ADOPT_PROOF_REQUIREMENTS_INCOMPLETE")
    if adopt != {"requiredForAdopt": True, "ownerSuppliedFields": ADOPT_PROOF_FIELDS, "missingMeansDispositionCannotBeAdopt": True}:
        raise Phase7Error("ADOPT_PROOF_REQUIREMENTS_INCOMPLETE")

    prerequisites = _exact_keys(contract["projectAuthorityPrerequisites"], {"required", "ownerSuppliedFields", "knownState"}, "PROJECT_AUTHORITY_REQUIREMENTS_INVALID")
    if project_id == "adobe-ingester":
        expected_state = {
            "activeWorkOrderId": "WO-G0-A01",
            "activeWorkOrderRevision": 12,
            "workOrderStatus": "BLOCKED_REVIEWER_CAPACITY",
            "reviewQuorumId": "Q-021",
            "requiredSeats": 4,
            "filledSeats": 2,
            "satisfied": False,
        }
        if prerequisites != {"required": True, "ownerSuppliedFields": ADOBE_AUTHORITY_FIELDS, "knownState": expected_state}:
            raise Phase7Error("ADOBE_AUTHORITY_REQUIREMENTS_INCOMPLETE")
    elif prerequisites != {"required": False, "ownerSuppliedFields": [], "knownState": None}:
        raise Phase7Error("PROJECT_AUTHORITY_REQUIREMENTS_INVALID")


def _verify_request(project_id: str, request: Any) -> None:
    request = _exact_keys(request, TOP_KEYS, "REQUEST_SHAPE_INVALID")
    if request["schema"] != SCHEMA or request["projectId"] != project_id:
        raise Phase7Error("PROJECT_BINDING_MISMATCH")
    if request["requestId"] != f"r26-owner-publication-{project_id}-20260820":
        raise Phase7Error("PROJECT_BINDING_MISMATCH")
    if request["status"] != "REQUEST_ONLY_ZERO_AUTHORITY":
        raise Phase7Error("REQUEST_STATUS_INVALID")
    if _contains_formal_disposition(request):
        raise Phase7Error("FORMAL_DISPOSITION_FABRICATED")

    _verify_frozen(project_id, request["frozenDoctrine"])

    current = _exact_keys(request["currentEvidence"], CURRENT_EVIDENCE_KEYS, "CURRENT_EVIDENCE_INVALID")
    if current != CURRENT_EVIDENCE[project_id]:
        raise Phase7Error("CURRENT_EVIDENCE_MISMATCH")

    _verify_contract(project_id, request["ownerPublicationContract"])

    queue = _exact_keys(request["queue"], QUEUE_KEYS, "QUEUE_INVALID")
    expected_queue = {
        "state": "AWAITING_PROJECT_OWNER_PUBLICATION",
        "executable": False,
        "ownerActionRequired": True,
        "automaticStatusAdvance": False,
        "writesAuthorized": False,
        "providerCallsAuthorized": False,
        "nextLawfulAction": PROJECT_BINDINGS[project_id]["next"],
    }
    if queue != expected_queue:
        raise Phase7Error("QUEUE_OVERCLAIM")

    authority = _exact_keys(request["authority"], AUTHORITY_KEYS, "AUTHORITY_INVALID")
    if any(value is not False for value in authority.values()):
        raise Phase7Error("AUTHORITY_OVERCLAIM")

    claims = request["prohibitedClaims"]
    if claims != PROHIBITED_CLAIMS[project_id]:
        raise Phase7Error("PROHIBITED_CLAIMS_INVALID")


def verify_request_documents(requests: dict[str, dict[str, Any]]) -> None:
    if set(requests) != PROJECT_IDS:
        raise Phase7Error("REQUEST_SET_MISMATCH")
    for project_id in sorted(PROJECT_IDS):
        _verify_request(project_id, requests[project_id])


def verify_requests(requests: dict[str, dict[str, Any]], treeish: str) -> None:
    _verify_repository_scope(treeish)
    verify_request_documents(requests)


def load_tree_requests(treeish: str) -> dict[str, dict[str, Any]]:
    return {
        project_id: load_json(_blob(treeish, f"{REQUEST_DIR}/{project_id}.json"))
        for project_id in sorted(PROJECT_IDS)
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--treeish", default="HEAD")
    args = parser.parse_args()
    try:
        requests = load_tree_requests(args.treeish)
        verify_requests(requests, args.treeish)
    except Phase7Error as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print("PASS: four R26 owner-publication requests are exact, request-only, zero-authority, and preserve all STALE rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
