#!/usr/bin/env python3
"""Verify the zero-authority R26 phase-5 reconciliation of four STALE projects."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
INTAKE_PATH = "adoption/phase5/r26-stale-project-reconciliation.json"
LEDGER_PATH = "adoption/universal-token-control-r26.json"
PHASE2_PATH = "adoption/phase2/r26-project-disposition-intake.json"
SCHEMA = "fleet-r26-stale-project-reconciliation/v1"
BASE_COMMIT = "5ac7036705338cfe3370f5fddda224e07d5d1bdd"
BASE_TREE = "9e53ff055bbf1a4fe796104d06f009f503082ad5"
BASE_PARENT = "f204b17d4f2be86fe8eb666c6fb1d58ed2633c57"
LEDGER_BLOB_OID = "333cc6d47e99a857b64150a87bd9f834590256e1"
LEDGER_BLOB_SHA256 = "a41f68c691159813ee58198ca1286683dcb1d20ea53cbe42f42a232cb2cd95ce"
PHASE2_BLOB_OID = "6e3fe9d429dfd578c43d8ebaf371074a45b662b1"
PHASE2_BLOB_SHA256 = "792656b33f3234ada7f13d18ec6cf6ed1349a7f5cc1a03713d58eed126bb346d"
R26_CANDIDATE = "e70a044f31dd2f43ab7c716d63a4eb89318c61b6"
R26_MERGE = "909f769d02e8412e51e28e242cfa8d00dadc9a3d"
PROJECT_IDS = {"adobe-ingester", "agent-bridge", "airmypc", "conjugal"}
EXPECTED_LEDGER_ROW_SHA256 = {
    "adobe-ingester": "6e7fa27a699d771c59159f1a9dd325889fb50fcfeaa6578635a05c300bfabf30",
    "agent-bridge": "224b2efc7e149a3dd6e1e2800d1635a0cdbd310c4de9a4996028e334348211f8",
    "airmypc": "70e2cf180ad3a4b5085a72105cfd5ee585e91cecfc525ce7cefc0e83381f6e82",
    "conjugal": "58afb58093e89992115492c8c70beb0b388980ad366dc5e01645b95d6f51aeb4",
}
EXPECTED_PHASE2_ROW_SHA256 = {
    "adobe-ingester": "27f471a40a8a211f79aff5725bbebb79a6143d37dda0d0dc871cab16512bb60c",
    "agent-bridge": "cf83c957062c8a2338d817e51b5efce6f56ff4509803e1f48a7bc45bd70b9079",
    "airmypc": "579b9a3af669eaab9eb4ed5aa7f28ba87edcc50ab2d8854e8c26a4e2b4af916d",
    "conjugal": "9af2aeea2ca622ac3a34dd7c1b737358852284576894219acc571ba0fe224ecf",
}
EXPECTED_PHASE2_OUTCOME = {
    "adobe-ingester": "PROJECT_REPOSITORY_ROOT_UNPUBLISHED_OWNER_WORK_ORDER_AND_QUORUM_REQUIRED",
    "agent-bridge": "PROJECT_REPOSITORY_ROOT_UNPUBLISHED_CURRENT_R26_DISPOSITION_REQUIRED",
    "airmypc": "PROJECT_REPOSITORY_ABSENT_CURRENT_R26_DISPOSITION_REQUIRED",
    "conjugal": "PROJECT_REPOSITORY_ABSENT_CURRENT_R26_DISPOSITION_REQUIRED",
}
ADOBE_REMOTE = "https://github.com/layibabalola/adobe-document-cloud-ingester.git"
ADOBE_REFS = [
    {
        "name": "refs/heads/agent/software-factory-hardening",
        "commit": "0afc24653369eb6129abf7f5263ee37ed1bed7f8",
        "tree": "0cc091c0d738f2d4f6b450e5480bc2b0e3a6149b",
        "parents": ["850a201ebdaca3cb6f4bb7441df6347ce7577cc1"],
    },
    {
        "name": "refs/heads/main",
        "commit": "556f6d1b1ebeab26cda6c400a61e12c9d6a69f76",
        "tree": "2655da443cd7e22e310d432b0aa39ef9e156aa09",
        "parents": ["93dd4f4dd843e4866e408389f571eb63d3aee8a4"],
    },
]
R26_PATTERNS = ["R26", R26_CANDIDATE, R26_MERGE]
ADOBE_STATE_ARTIFACT = {
    "ref": "refs/heads/agent/software-factory-hardening",
    "path": ".factory/state.yaml",
    "gitBlobOid": "797894a2d2988d37efc520f0dd12a79e6bc8d4d1",
    "bytes": 17085,
    "sha256": "69bcce7034bf213f64344e2395f1e30b629d804bbb77966bf9638c477d1cb121",
    "textAnchors": [
        {"text": "state: IMPLEMENTED", "count": 1},
        {"text": "active_work_order: WO-G0-A01", "count": 1},
        {"text": "active_revision: 12", "count": 1},
        {"text": "status: BLOCKED_REVIEWER_CAPACITY", "count": 2},
    ],
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
PHASE11_INTEGRATION_PATHS = {
    "adoption/phase11/README.md",
    "adoption/phase11/r26-phase10-review-shape-closure.json",
    "tests/test_phase11_integration.py",
    "tools/check_phase11_integration.py",
}
ALLOWED_PHASE5_PATHS = {
    ".github/workflows/disposition-intake.yml",
    "adoption/README.md",
    "adoption/phase5/README.md",
    INTAKE_PATH,
    "adoption/phase6/README.md",
    "adoption/phase6/r26-local-candidate-review-receipts.json",
    "adoption/phase7/README.md",
    "adoption/phase7/requests/adobe-ingester.json",
    "adoption/phase7/requests/agent-bridge.json",
    "adoption/phase7/requests/airmypc.json",
    "adoption/phase7/requests/conjugal.json",
    "adoption/phase8/README.md",
    "tests/test_phase2_disposition_batch.py",
    "tests/test_phase3_disposition_batch.py",
    "tests/test_phase5_stale_reconciliation.py",
    "tests/test_phase6_candidate_reviews.py",
    "tests/test_phase7_owner_publication_requests.py",
    "tests/test_phase8_integration.py",
    "tools/check_phase2_disposition_batch.py",
    "tools/check_phase3_disposition_batch.py",
    "tools/check_phase5_stale_reconciliation.py",
    "tools/check_phase6_candidate_reviews.py",
    "tools/check_phase7_owner_publication_requests.py",
    "tools/check_phase8_integration.py",
} | MANIFEST_BINDING_REPAIR_PATHS | PHASE9_INTEGRATION_PATHS | PHASE10_INTEGRATION_PATHS | PHASE11_INTEGRATION_PATHS
SHA_PATTERN = re.compile(r"[0-9a-f]{40,64}")
REMOTE_TOKEN_ENV = "R26_REMOTE_GITHUB_TOKEN"
REMOTE_TIMEOUT_SECONDS = 60
REMOTE_TEMP_PREFIX = "fleet-doctrine-r26-phase5-remote-"


class Phase5Error(ValueError):
    pass


def _pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in values:
        if key in result:
            raise Phase5Error("DUPLICATE_KEY")
        result[key] = value
    return result


def load_json(raw: bytes) -> dict[str, Any]:
    try:
        value = json.loads(raw, object_pairs_hook=_pairs)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise Phase5Error("JSON_INVALID") from exc
    if not isinstance(value, dict):
        raise Phase5Error("JSON_ROOT_INVALID")
    return value


def _exact_keys(value: Any, keys: set[str], code: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise Phase5Error(code)
    return value


def _git(args: list[str], *, text: bool = False, error: str = "GIT_OBJECT_UNAVAILABLE") -> bytes | str:
    run = subprocess.run(
        ["git", *args], cwd=ROOT, check=False, capture_output=True,
        text=text, encoding="utf-8" if text else None,
    )
    if run.returncode != 0:
        raise Phase5Error(error)
    return run.stdout


def _blob(treeish: str, path: str) -> bytes:
    return _git(["show", f"{treeish}:{path}"], error="GIT_BLOB_UNAVAILABLE")  # type: ignore[return-value]


def _oid(treeish: str, path: str) -> str:
    value = _git(
        ["rev-parse", f"{treeish}:{path}"], text=True, error="GIT_BLOB_OID_UNAVAILABLE"
    ).strip()
    if SHA_PATTERN.fullmatch(value) is None:
        raise Phase5Error("GIT_BLOB_OID_INVALID")
    return value


def _commit_tuple(commit: str) -> tuple[str, list[str]]:
    value = _git(
        ["show", "-s", "--format=%T%n%P", commit], text=True, error="COMMIT_UNAVAILABLE"
    )
    lines = value.splitlines()
    if len(lines) != 2 or SHA_PATTERN.fullmatch(lines[0]) is None:
        raise Phase5Error("COMMIT_INVALID")
    parents = lines[1].split() if lines[1] else []
    if any(SHA_PATTERN.fullmatch(parent) is None for parent in parents):
        raise Phase5Error("COMMIT_INVALID")
    return lines[0], parents


def _is_ancestor(ancestor: str, descendant: str) -> bool:
    return subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=ROOT, check=False, capture_output=True,
    ).returncode == 0


def _changed_paths(treeish: str) -> set[str]:
    return set(
        _git(
            ["diff", "--name-only", f"{BASE_COMMIT}..{treeish}"],
            text=True,
            error="PHASE5_DIFF_UNAVAILABLE",
        ).splitlines()
    )


def _canonical_sha256(value: Any) -> str:
    raw = json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _verify_frozen_base(base: Any, treeish: str) -> None:
    expected = {
        "publishedMasterCommit": BASE_COMMIT,
        "publishedMasterTree": BASE_TREE,
        "ledgerPath": LEDGER_PATH,
        "ledgerGitBlobOid": LEDGER_BLOB_OID,
        "ledgerGitBlobSha256": LEDGER_BLOB_SHA256,
        "phase2Path": PHASE2_PATH,
        "phase2GitBlobOid": PHASE2_BLOB_OID,
        "phase2GitBlobSha256": PHASE2_BLOB_SHA256,
        "r26Candidate": R26_CANDIDATE,
        "r26Merge": R26_MERGE,
    }
    if base != expected:
        raise Phase5Error("FROZEN_BASE_MISMATCH")
    if _commit_tuple(BASE_COMMIT) != (BASE_TREE, [BASE_PARENT]):
        raise Phase5Error("PUBLISHED_MASTER_OBJECT_MISMATCH")
    if _oid(BASE_COMMIT, LEDGER_PATH) != LEDGER_BLOB_OID:
        raise Phase5Error("LEDGER_BLOB_OID_MISMATCH")
    if hashlib.sha256(_blob(BASE_COMMIT, LEDGER_PATH)).hexdigest() != LEDGER_BLOB_SHA256:
        raise Phase5Error("LEDGER_BLOB_SHA256_MISMATCH")
    if _oid(BASE_COMMIT, PHASE2_PATH) != PHASE2_BLOB_OID:
        raise Phase5Error("PHASE2_BLOB_OID_MISMATCH")
    if hashlib.sha256(_blob(BASE_COMMIT, PHASE2_PATH)).hexdigest() != PHASE2_BLOB_SHA256:
        raise Phase5Error("PHASE2_BLOB_SHA256_MISMATCH")
    descendant = "HEAD" if treeish == ":" else treeish
    if not _is_ancestor(BASE_COMMIT, descendant):
        raise Phase5Error("PUBLISHED_MASTER_NOT_ANCESTOR")
    if not _changed_paths(treeish).issubset(ALLOWED_PHASE5_PATHS):
        raise Phase5Error("PHASE5_SCOPE_VIOLATION")


def _verify_capture(capture: Any) -> None:
    capture = _exact_keys(
        capture,
        {
            "capturedAt", "machine", "discoveryPolicy", "networkInspectionPerformed",
            "providerInvocationPerformed", "runtimeMutationPerformed",
            "scheduledTaskMutationPerformed", "projectRepositoryMutationPerformed",
        },
        "CAPTURE_INVALID",
    )
    if not isinstance(capture["capturedAt"], str) or not capture["capturedAt"]:
        raise Phase5Error("CAPTURE_TIME_INVALID")
    if capture["machine"] != "ULTRA-MAGNUS":
        raise Phase5Error("CAPTURE_MACHINE_INVALID")
    if capture["discoveryPolicy"] != "EXACT_PUBLISHED_POINTERS_AND_ALLOWLISTED_REMOTE_REFS_ONLY":
        raise Phase5Error("CAPTURE_POLICY_INVALID")
    if capture["networkInspectionPerformed"] is not True:
        raise Phase5Error("NETWORK_CAPTURE_INVALID")
    if any(
        capture[field] is not False
        for field in (
            "providerInvocationPerformed", "runtimeMutationPerformed",
            "scheduledTaskMutationPerformed", "projectRepositoryMutationPerformed",
        )
    ):
        raise Phase5Error("CAPTURE_AUTHORITY_OVERCLAIM")


def _verify_discovery(project_id: str, discovery: Any) -> None:
    discovery = _exact_keys(
        discovery,
        {"classification", "remote", "refs", "r26MarkerSearch", "workflowEvidence", "caveat"},
        "DISCOVERY_INVALID",
    )
    if project_id == "adobe-ingester":
        expected = {
            "classification": "REACHABLE_PROJECT_REMOTE_NO_CURRENT_R26_DISPOSITION",
            "remote": ADOBE_REMOTE,
            "refs": ADOBE_REFS,
            "r26MarkerSearch": {
                "patterns": R26_PATTERNS,
                "performedAgainstRefs": [record["name"] for record in ADOBE_REFS],
                "matchingPaths": [],
            },
            "workflowEvidence": ADOBE_STATE_ARTIFACT,
            "caveat": "REMOTE_LOCATION_AND_BLOCKER_EVIDENCE_ONLY_NOT_PROJECT_DISPOSITION",
        }
        if discovery != expected:
            raise Phase5Error("ADOBE_DISCOVERY_MISMATCH")
    else:
        expected = {
            "classification": "NO_AUTHORITATIVE_REMOTE_OR_CURRENT_REF_AVAILABLE_TO_RECONCILIATION",
            "remote": None,
            "refs": [],
            "r26MarkerSearch": None,
            "workflowEvidence": None,
            "caveat": "BOUNDED_NEGATIVE_DISCOVERY_NOT_GLOBAL_NONEXISTENCE_PROOF",
        }
        if discovery != expected:
            raise Phase5Error(f"NEGATIVE_DISCOVERY_OVERCLAIM:{project_id}")


def _verify_project(
    project: Any,
    *,
    ledger_rows: dict[str, dict[str, Any]],
    phase2_rows: dict[str, dict[str, Any]],
) -> str:
    project = _exact_keys(
        project,
        {"projectId", "ledgerBinding", "phase2Binding", "discovery", "outcome", "authority"},
        "PROJECT_RECORD_INVALID",
    )
    project_id = project["projectId"]
    if project_id not in PROJECT_IDS:
        raise Phase5Error("PROJECT_ID_INVALID")
    ledger_row = ledger_rows[project_id]
    if _canonical_sha256(ledger_row) != EXPECTED_LEDGER_ROW_SHA256[project_id]:
        raise Phase5Error(f"FROZEN_LEDGER_ROW_MISMATCH:{project_id}")
    evidence = ledger_row.get("evidence")
    if not isinstance(evidence, dict):
        raise Phase5Error("FROZEN_LEDGER_EVIDENCE_INVALID")
    binding = _exact_keys(
        project["ledgerBinding"],
        {"canonicalSha256", "status", "blocker", "projectCandidatePresent"},
        "LEDGER_BINDING_INVALID",
    )
    expected_binding = {
        "canonicalSha256": EXPECTED_LEDGER_ROW_SHA256[project_id],
        "status": "STALE",
        "blocker": "PROJECT_OWNER_CURRENT_CANDIDATE_DISPOSITION_REQUIRED",
        "projectCandidatePresent": False,
    }
    if binding != expected_binding:
        raise Phase5Error(f"LEDGER_BINDING_MISMATCH:{project_id}")
    if (
        ledger_row.get("status") != "STALE"
        or ledger_row.get("blocker") != expected_binding["blocker"]
        or ledger_row.get("nonRegressionEvidence") is not None
        or evidence.get("projectCandidate") is not None
    ):
        raise Phase5Error(f"FROZEN_LEDGER_STATUS_MISMATCH:{project_id}")

    phase2_row = phase2_rows[project_id]
    if _canonical_sha256(phase2_row) != EXPECTED_PHASE2_ROW_SHA256[project_id]:
        raise Phase5Error(f"FROZEN_PHASE2_ROW_MISMATCH:{project_id}")
    phase2_binding = _exact_keys(
        project["phase2Binding"], {"canonicalSha256", "outcomeCode"}, "PHASE2_BINDING_INVALID"
    )
    expected_phase2_binding = {
        "canonicalSha256": EXPECTED_PHASE2_ROW_SHA256[project_id],
        "outcomeCode": EXPECTED_PHASE2_OUTCOME[project_id],
    }
    if phase2_binding != expected_phase2_binding:
        raise Phase5Error(f"PHASE2_BINDING_MISMATCH:{project_id}")
    if phase2_row.get("dispositionOutcome", {}).get("code") != EXPECTED_PHASE2_OUTCOME[project_id]:
        raise Phase5Error(f"FROZEN_PHASE2_OUTCOME_MISMATCH:{project_id}")

    _verify_discovery(project_id, project["discovery"])
    outcome = _exact_keys(
        project["outcome"],
        {"status", "projectCandidate", "r26Disposition", "advanceAuthorized"},
        "OUTCOME_INVALID",
    )
    if outcome != {
        "status": "STALE",
        "projectCandidate": None,
        "r26Disposition": "NOT_PRODUCED",
        "advanceAuthorized": False,
    }:
        raise Phase5Error(f"OUTCOME_OVERCLAIM:{project_id}")
    authority = _exact_keys(
        project["authority"],
        {"projectDisposition", "adoption", "runtime", "provider", "scheduler", "mutation"},
        "AUTHORITY_INVALID",
    )
    if any(value is not False for value in authority.values()):
        raise Phase5Error(f"AUTHORITY_OVERCLAIM:{project_id}")
    return project_id


def verify_batch(batch: dict[str, Any], treeish: str = "HEAD") -> None:
    batch = _exact_keys(
        batch,
        {"schema", "status", "frozenBase", "capture", "summary", "projects"},
        "BATCH_FIELDS_INVALID",
    )
    if batch["schema"] != SCHEMA or batch["status"] != "DISCOVERY_ONLY_ZERO_AUTHORITY_FOUR_STALE":
        raise Phase5Error("BATCH_IDENTITY_INVALID")
    _verify_frozen_base(batch["frozenBase"], treeish)
    _verify_capture(batch["capture"])

    ledger = load_json(_blob(BASE_COMMIT, LEDGER_PATH))
    if ledger.get("summary") != {
        "projectCount": 9,
        "counts": {"ADOPT": 0, "DISTINGUISH": 5, "MISSING": 0, "REJECT": 0, "STALE": 4},
        "fleetStatus": "NO_FLEET_ADOPTION",
        "fleetAdoptionClaim": False,
    }:
        raise Phase5Error("FROZEN_LEDGER_SUMMARY_MISMATCH")
    ledger_projects = ledger.get("projects")
    if not isinstance(ledger_projects, list) or any(not isinstance(row, dict) for row in ledger_projects):
        raise Phase5Error("FROZEN_LEDGER_PROJECTS_INVALID")
    ledger_rows = {row.get("projectId"): row for row in ledger_projects if row.get("projectId") in PROJECT_IDS}
    if set(ledger_rows) != PROJECT_IDS:
        raise Phase5Error("FROZEN_LEDGER_PROJECT_SET_INVALID")

    phase2 = load_json(_blob(BASE_COMMIT, PHASE2_PATH))
    phase2_projects = phase2.get("projects")
    if not isinstance(phase2_projects, list) or any(not isinstance(row, dict) for row in phase2_projects):
        raise Phase5Error("FROZEN_PHASE2_PROJECTS_INVALID")
    phase2_rows = {row.get("projectId"): row for row in phase2_projects if row.get("projectId") in PROJECT_IDS}
    if set(phase2_rows) != PROJECT_IDS:
        raise Phase5Error("FROZEN_PHASE2_PROJECT_SET_INVALID")

    projects = batch["projects"]
    if not isinstance(projects, list) or len(projects) != len(PROJECT_IDS):
        raise Phase5Error("PROJECT_SET_INVALID")
    ids = [
        _verify_project(project, ledger_rows=ledger_rows, phase2_rows=phase2_rows)
        for project in projects
    ]
    if ids != sorted(PROJECT_IDS) or len(ids) != len(set(ids)):
        raise Phase5Error("PROJECT_SET_INVALID")
    if batch["summary"] != {
        "projectCount": 4,
        "stalePreserved": 4,
        "reachableRemotes": 1,
        "currentR26Dispositions": 0,
        "adoptionClaims": 0,
        "runtimeAuthorityClaims": 0,
        "projectMutationClaims": 0,
    }:
        raise Phase5Error("SUMMARY_OVERCLAIM")


def _remote_environment(askpass_path: Path, global_config_path: Path) -> dict[str, str]:
    environment = {
        key: value
        for key, value in os.environ.items()
        if not key.upper().startswith(("GIT_", "GCM_"))
        and key.upper() not in {"SSH_ASKPASS", "SSH_ASKPASS_REQUIRE", REMOTE_TOKEN_ENV}
    }
    environment.update(
        {
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_ASKPASS": str(askpass_path),
            "SSH_ASKPASS": str(askpass_path),
            "SSH_ASKPASS_REQUIRE": "force",
            "GCM_INTERACTIVE": "Never",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": str(global_config_path),
            "GIT_CONFIG_COUNT": "0",
        }
    )
    return environment


def _write_askpass(temp_root: Path) -> Path:
    if os.name == "nt":
        path = temp_root / "deny-askpass.cmd"
        path.write_bytes(b"@echo off\r\nexit /b 1\r\n")
    else:
        path = temp_root / "deny-askpass.sh"
        path.write_bytes(b"#!/bin/sh\nexit 1\n")
        path.chmod(0o700)
    return path


def _remote_auth_token() -> str | None:
    token = os.environ.get(REMOTE_TOKEN_ENV)
    if token is None or token == "":
        return None
    if re.fullmatch(r"[A-Za-z0-9_]{20,512}", token) is None:
        raise Phase5Error("REMOTE_AUTH_TOKEN_INVALID")
    return token


def _write_global_git_config(temp_root: Path, token: str | None) -> Path:
    path = temp_root / "gitconfig"
    content = b"[http]\n\tsslBackend = schannel\n" if os.name == "nt" else b""
    if token is not None:
        basic = base64.b64encode(f"x-access-token:{token}".encode("ascii"))
        content += b'[http "https://github.com/"]\n\textraHeader = AUTHORIZATION: basic ' + basic + b"\n"
    elif os.name == "nt":
        content += b"[credential]\n\thelper = manager\n"
    else:
        content += b"# intentionally empty\n"
    path.write_bytes(content)
    if os.name != "nt":
        path.chmod(0o600)
    return path


def _run_remote_git(
    args: list[str], *, cwd: Path, environment: dict[str, str], error: str,
    text: bool = False,
) -> bytes | str:
    try:
        run = subprocess.run(
            ["git", *args], cwd=cwd, env=environment, check=False, capture_output=True,
            text=text, encoding="utf-8" if text else None, timeout=REMOTE_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise Phase5Error("ADOBE_REMOTE_GIT_TIMEOUT") from exc
    except OSError as exc:
        raise Phase5Error("ADOBE_REMOTE_GIT_EXECUTION_FAILED") from exc
    if run.returncode != 0:
        raise Phase5Error(error)
    return run.stdout


def _remote_commit_tuple(
    repo: Path, environment: dict[str, str], commit: str
) -> tuple[str, list[str]]:
    value = _run_remote_git(
        ["show", "-s", "--format=%T%n%P", commit],
        cwd=repo, environment=environment, error="ADOBE_REMOTE_COMMIT_UNAVAILABLE", text=True,
    )
    lines = value.splitlines()
    if len(lines) != 2 or SHA_PATTERN.fullmatch(lines[0]) is None:
        raise Phase5Error("ADOBE_REMOTE_COMMIT_INVALID")
    parents = lines[1].split() if lines[1] else []
    if any(SHA_PATTERN.fullmatch(parent) is None for parent in parents):
        raise Phase5Error("ADOBE_REMOTE_COMMIT_INVALID")
    return lines[0], parents


def _remote_marker_paths(
    repo: Path, environment: dict[str, str], commit: str
) -> list[str]:
    args = ["git", "grep", "-I", "-l"]
    for pattern in R26_PATTERNS:
        args.extend(["-e", pattern])
    args.extend([commit, "--"])
    try:
        run = subprocess.run(
            args, cwd=repo, env=environment, check=False, capture_output=True,
            text=True, encoding="utf-8", timeout=REMOTE_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise Phase5Error("ADOBE_REMOTE_MARKER_SEARCH_TIMEOUT") from exc
    if run.returncode == 1:
        return []
    if run.returncode != 0:
        raise Phase5Error("ADOBE_REMOTE_MARKER_SEARCH_FAILED")
    return sorted(line for line in run.stdout.splitlines() if line)


def _verify_remote_artifact(repo: Path, environment: dict[str, str], ref_record: dict[str, Any]) -> None:
    artifact = ADOBE_STATE_ARTIFACT
    if artifact["ref"] != ref_record["name"]:
        raise Phase5Error("ADOBE_REMOTE_ARTIFACT_REF_INVALID")
    oid = _run_remote_git(
        ["rev-parse", f"{ref_record['commit']}:{artifact['path']}"],
        cwd=repo, environment=environment, error="ADOBE_REMOTE_ARTIFACT_UNAVAILABLE", text=True,
    ).strip()
    if oid != artifact["gitBlobOid"]:
        raise Phase5Error("ADOBE_REMOTE_ARTIFACT_BLOB_MISMATCH")
    size_text = _run_remote_git(
        ["cat-file", "-s", oid], cwd=repo, environment=environment,
        error="ADOBE_REMOTE_ARTIFACT_SIZE_UNAVAILABLE", text=True,
    ).strip()
    try:
        size = int(size_text)
    except ValueError as exc:
        raise Phase5Error("ADOBE_REMOTE_ARTIFACT_SIZE_INVALID") from exc
    raw = _run_remote_git(
        ["cat-file", "blob", oid], cwd=repo, environment=environment,
        error="ADOBE_REMOTE_ARTIFACT_READ_FAILED",
    )
    if size != artifact["bytes"] or len(raw) != artifact["bytes"]:
        raise Phase5Error("ADOBE_REMOTE_ARTIFACT_BYTE_MISMATCH")
    if hashlib.sha256(raw).hexdigest() != artifact["sha256"]:
        raise Phase5Error("ADOBE_REMOTE_ARTIFACT_SHA256_MISMATCH")
    for anchor in artifact["textAnchors"]:
        if raw.count(anchor["text"].encode("utf-8")) != anchor["count"]:
            raise Phase5Error("ADOBE_REMOTE_ARTIFACT_ANCHOR_MISMATCH")


def verify_remotes(batch: dict[str, Any]) -> None:
    projects = batch.get("projects")
    if not isinstance(projects, list):
        raise Phase5Error("REMOTE_PROJECT_SET_INVALID")
    adobe = next(
        (project for project in projects if isinstance(project, dict) and project.get("projectId") == "adobe-ingester"),
        None,
    )
    if not isinstance(adobe, dict) or adobe.get("discovery", {}).get("remote") != ADOBE_REMOTE:
        raise Phase5Error("REMOTE_ADOBE_RECORD_INVALID")
    token = _remote_auth_token()
    with tempfile.TemporaryDirectory(prefix=REMOTE_TEMP_PREFIX) as temp_name:
        temp_root = Path(temp_name)
        askpass = _write_askpass(temp_root)
        git_config = _write_global_git_config(temp_root, token)
        environment = _remote_environment(askpass, git_config)
        repo = temp_root / "objects"
        repo.mkdir()
        _run_remote_git(
            ["init", "--quiet"], cwd=repo, environment=environment,
            error="ADOBE_REMOTE_INIT_FAILED",
        )
        advertised_raw = _run_remote_git(
            ["ls-remote", "--exit-code", "--refs", "--", ADOBE_REMOTE, *[r["name"] for r in ADOBE_REFS]],
            cwd=repo, environment=environment, error="ADOBE_REMOTE_REF_QUERY_FAILED", text=True,
        )
        advertised: dict[str, str] = {}
        for line in advertised_raw.splitlines():
            fields = line.split("\t")
            if len(fields) != 2 or SHA_PATTERN.fullmatch(fields[0]) is None or fields[1] in advertised:
                raise Phase5Error("ADOBE_REMOTE_REF_ADVERTISEMENT_INVALID")
            advertised[fields[1]] = fields[0]
        expected_advertised = {record["name"]: record["commit"] for record in ADOBE_REFS}
        if advertised != expected_advertised:
            raise Phase5Error("ADOBE_REMOTE_REF_MISMATCH")

        for index, record in enumerate(ADOBE_REFS):
            local_ref = f"refs/remotes/evidence/{index}"
            _run_remote_git(
                [
                    "fetch", "--quiet", "--no-tags", "--no-recurse-submodules", "--depth", "2",
                    "--", ADOBE_REMOTE, f"+{record['name']}:{local_ref}",
                ],
                cwd=repo, environment=environment, error="ADOBE_REMOTE_FETCH_FAILED",
            )
            fetched = _run_remote_git(
                ["rev-parse", "--verify", "--end-of-options", f"{local_ref}^{{commit}}"],
                cwd=repo, environment=environment, error="ADOBE_REMOTE_FETCH_REF_INVALID", text=True,
            ).strip()
            if fetched != record["commit"]:
                raise Phase5Error("ADOBE_REMOTE_FETCH_REF_MISMATCH")
            if _remote_commit_tuple(repo, environment, record["commit"]) != (
                record["tree"], record["parents"]
            ):
                raise Phase5Error("ADOBE_REMOTE_COMMIT_TUPLE_MISMATCH")
            if _remote_marker_paths(repo, environment, record["commit"]) != []:
                raise Phase5Error("ADOBE_REMOTE_R26_MARKER_FOUND")
            if record["name"] == ADOBE_STATE_ARTIFACT["ref"]:
                _verify_remote_artifact(repo, environment, record)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--treeish", default="HEAD")
    parser.add_argument("--verify-remotes", action="store_true")
    args = parser.parse_args(argv)
    try:
        batch = load_json(_blob(args.treeish, INTAKE_PATH))
        verify_batch(batch, args.treeish)
        if args.verify_remotes:
            verify_remotes(batch)
    except Phase5Error as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    if args.verify_remotes:
        print(
            "PASS: phase-5 reconciliation preserves 4 STALE rows, grants zero authority; "
            "ADOBE REMOTE VERIFIED"
        )
    else:
        print(
            "PASS LOCAL-ONLY: phase-5 reconciliation preserves 4 STALE rows, grants zero authority; "
            "ADOBE REMOTE NOT VERIFIED"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
