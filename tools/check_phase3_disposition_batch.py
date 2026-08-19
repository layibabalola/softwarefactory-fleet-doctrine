#!/usr/bin/env python3
"""Verify the exact zero-authority R26 phase-3 published-project distinctions."""

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
INTAKE_PATH = "adoption/phase3/r26-published-project-disposition-intake.json"
LEDGER_PATH = "adoption/universal-token-control-r26.json"
SCHEMA = "fleet-r26-published-project-disposition-intake/v1"
MASTER_COMMIT = "082f631c7b474211bbe8ecbc783a4fd9cdd2ada0"
MASTER_TREE = "8bba889936defcf5e46573ca26daa81f544a2a81"
INITIAL_FOLD_COMMIT = "c025c1f5b32c71e77142d592107013fbbb677336"
INITIAL_FOLD_TREE = "5e90a7fb72c1c7bc593f8dbfd7d097be18a9c20f"
SPEC_BINDING_COMMIT = "928606d0151814e50ed051d8d5819ca4e23c5940"
SPEC_BINDING_TREE = "402d6818937d4ecb64ac807c77c5792fd121947e"
PHASE3_PUBLISHED_COMMIT = "0c417d8ccf4b0b2b142766fd4aa00072ae150a30"
PHASE3_PUBLISHED_TREE = "dbe000aad9c2ee857dbaf8d2b1e311cade720ce1"
ADVERSARIAL_SPEC_BINDING_COMMIT = "73abc64b92aa96defca08ceab83b75c656dd3357"
ADVERSARIAL_SPEC_BINDING_TREE = "5f383c1475c0168677724fcf155092be7d1010d2"
PRE_ADVERSARIAL_SPEC_REPAIR_COMMIT = "8b20d13c2c27ab6375872be92982ef4b5ff229d5"
PRE_ADVERSARIAL_SPEC_REPAIR_TREE = "5f7778baf2e46d64662fdef3074b9b0e6833a7f9"
ADVERSARIAL_SPEC_REPAIR_COMMIT = "f204b17d4f2be86fe8eb666c6fb1d58ed2633c57"
ADVERSARIAL_SPEC_REPAIR_TREE = "02e4214f7f18ca09d1053218e5747ac9e7a53514"
UTILIZATION_SHADOW_DOCTRINE_BASE_COMMIT = "5ac7036705338cfe3370f5fddda224e07d5d1bdd"
UTILIZATION_SHADOW_DOCTRINE_BASE_TREE = "9e53ff055bbf1a4fe796104d06f009f503082ad5"
UTILIZATION_SHADOW_DOCTRINE_AMENDMENT_COMMIT = "7bf0cf9943de7c33b14496b73f70c18959816c5c"
UTILIZATION_SHADOW_DOCTRINE_AMENDMENT_TREE = "ebac9bbd75d8ae70bf2b4a2d0877020a5af83127"
UTILIZATION_SHADOW_DOCTRINE_AMENDMENT_SPEC_BLOB = "e964d2b77426ece703f8fb1fd82a9cb068e98632"
R26_CANDIDATE = "e70a044f31dd2f43ab7c716d63a4eb89318c61b6"
R26_MERGE = "909f769d02e8412e51e28e242cfa8d00dadc9a3d"
INITIAL_PROJECT_IDS = {"cloudvore", "mlv-app", "salesforce-tools"}
PROJECT_IDS = INITIAL_PROJECT_IDS | {"adversarialllm"}
LEDGER_PROJECT_IDS = {
    "adobe-ingester",
    "adversarialllm",
    "agent-bridge",
    "airmypc",
    "cloudvore",
    "conjugal",
    "dng-auto-processor",
    "mlv-app",
    "salesforce-tools",
}
SPEC_PATHS = {f"specs/{project_id}.md" for project_id in INITIAL_PROJECT_IDS}
PUBLISHED_REMOTE_ALLOWLIST = {
    "adversarialllm": {
        "remote": "https://github.com/layibabalola/AdversarialLLM-ClaudeCode.git",
        "publishedRef": "refs/heads/master",
    },
    "cloudvore": {
        "remote": "https://github.com/layibabalola/Cloudvore.git",
        "publishedRef": "refs/heads/codex/r26-zero-authority-disposition-candidate-20260819",
    },
    "mlv-app": {
        "remote": "https://github.com/layibabalola/MLV-App.git",
        "publishedRef": "refs/heads/codex/r26-zero-authority-disposition-candidate-20260819",
    },
    "salesforce-tools": {
        "remote": "https://github.com/layibabalola/SalesforceSupportTools.git",
        "publishedRef": "refs/heads/codex/r26-zero-authority-disposition-candidate-20260819",
    },
}
EXPECTED_PROJECT_CANDIDATE_SHA256 = {
    "adversarialllm": "07fba4c159ad9250d196945ce6e479c91f7b85040620037b315ce4dd1d0cf47f",
    "cloudvore": "7bbafaa69078bf3464f5e54c6f1e0a689113c54ce7df7f494d017beef58be436",
    "mlv-app": "55544254f982890efa8b2e309b0eeb2be09f85d7f09f7da86083ba2856cbf9ba",
    "salesforce-tools": "b2278e858cf70c0a6eecca6d7842709e9cc6fe4598fa13af6bf64929c05b0f6f",
}
ALLOWED_PHASE3_PATHS = {
    ".github/workflows/disposition-intake.yml",
    "adoption/README.md",
    "adoption/phase3/README.md",
    INTAKE_PATH,
    "adoption/phase5/README.md",
    "adoption/phase5/r26-stale-project-reconciliation.json",
    LEDGER_PATH,
    "tests/test_adoption_ledger.py",
    "tests/test_phase2_disposition_batch.py",
    "tests/test_phase3_disposition_batch.py",
    "tests/test_phase5_stale_reconciliation.py",
    "tests/test_adversarialllm_utilization_shadow_doctrine.py",
    "tools/check_adoption_ledger.py",
    "tools/check_phase2_disposition_batch.py",
    "tools/check_phase3_disposition_batch.py",
    "tools/check_phase5_stale_reconciliation.py",
}
SHA_PATTERN = re.compile(r"[0-9a-f]{40,64}")
FORMAL_ADOPT_PATTERN = re.compile(r"\bADOPT\s*\(", re.IGNORECASE)
REMOTE_FETCH_DEPTH = 64
REMOTE_GIT_TIMEOUT_SECONDS = 60
REMOTE_MAX_ARTIFACT_BYTES = 1_048_576
REMOTE_TEMP_PREFIX = "fleet-doctrine-r26-phase3-remote-"
REMOTE_TOKEN_ENV = "R26_REMOTE_GITHUB_TOKEN"


class Phase3Error(ValueError):
    pass


def _pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in values:
        if key in result:
            raise Phase3Error("DUPLICATE_KEY")
        result[key] = value
    return result


def load_json(raw: bytes) -> dict[str, Any]:
    try:
        value = json.loads(raw, object_pairs_hook=_pairs)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise Phase3Error("JSON_INVALID") from exc
    if not isinstance(value, dict):
        raise Phase3Error("JSON_ROOT_INVALID")
    return value


def _git(args: list[str], *, text: bool = False, error: str = "GIT_OBJECT_UNAVAILABLE") -> bytes | str:
    run = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=text,
        encoding="utf-8" if text else None,
    )
    if run.returncode != 0:
        raise Phase3Error(error)
    return run.stdout


def _blob_spec(treeish: str, path: str) -> str:
    return f":{path}" if treeish == ":" else f"{treeish}:{path}"


def _blob(treeish: str, path: str) -> bytes:
    return _git(["show", _blob_spec(treeish, path)], error="GIT_BLOB_UNAVAILABLE")  # type: ignore[return-value]


def _oid(treeish: str, path: str) -> str:
    value = _git(
        ["rev-parse", _blob_spec(treeish, path)],
        text=True,
        error="GIT_BLOB_OID_UNAVAILABLE",
    ).strip()
    if SHA_PATTERN.fullmatch(value) is None:
        raise Phase3Error("GIT_BLOB_OID_INVALID")
    return value


def _commit_tuple(commit: str) -> tuple[str, list[str]]:
    value = _git(
        ["show", "-s", "--format=%T%n%P", commit],
        text=True,
        error="COMMIT_UNAVAILABLE",
    )
    lines = value.splitlines()
    if len(lines) != 2 or SHA_PATTERN.fullmatch(lines[0]) is None:
        raise Phase3Error("COMMIT_INVALID")
    return lines[0], lines[1].split() if lines[1] else []


def _is_ancestor(ancestor: str, descendant: str) -> bool:
    run = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    return run.returncode == 0


def _changed_paths(base: str, treeish: str) -> set[str]:
    args = (
        ["diff", "--cached", "--name-only", base]
        if treeish == ":"
        else ["diff", "--name-only", f"{base}..{treeish}"]
    )
    return set(_git(args, text=True, error="PHASE3_DIFF_UNAVAILABLE").splitlines())


def _exact_keys(value: Any, keys: set[str], code: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise Phase3Error(code)
    return value


def _canonical_sha256(value: Any) -> str:
    raw = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _contains_formal_adopt(value: Any) -> bool:
    if isinstance(value, str):
        return FORMAL_ADOPT_PATTERN.search(value) is not None
    if isinstance(value, dict):
        return any(_contains_formal_adopt(k) or _contains_formal_adopt(v) for k, v in value.items())
    if isinstance(value, list):
        return any(_contains_formal_adopt(member) for member in value)
    return False


def _verify_frozen_base(base: Any, treeish: str) -> None:
    expected = {
        "publishedMasterCommit": MASTER_COMMIT,
        "publishedMasterTree": MASTER_TREE,
        "initialSpecFoldCommit": INITIAL_FOLD_COMMIT,
        "initialSpecFoldTree": INITIAL_FOLD_TREE,
        "specBindingCommit": SPEC_BINDING_COMMIT,
        "specBindingTree": SPEC_BINDING_TREE,
        "adversarialSpecBindingCommit": ADVERSARIAL_SPEC_BINDING_COMMIT,
        "adversarialSpecBindingTree": ADVERSARIAL_SPEC_BINDING_TREE,
        "adversarialSpecRepairCommit": ADVERSARIAL_SPEC_REPAIR_COMMIT,
        "adversarialSpecRepairTree": ADVERSARIAL_SPEC_REPAIR_TREE,
        "utilizationShadowDoctrineBaseCommit": UTILIZATION_SHADOW_DOCTRINE_BASE_COMMIT,
        "utilizationShadowDoctrineBaseTree": UTILIZATION_SHADOW_DOCTRINE_BASE_TREE,
        "utilizationShadowDoctrineAmendmentCommit": UTILIZATION_SHADOW_DOCTRINE_AMENDMENT_COMMIT,
        "utilizationShadowDoctrineAmendmentTree": UTILIZATION_SHADOW_DOCTRINE_AMENDMENT_TREE,
        "utilizationShadowDoctrineAmendmentSpecBlob": UTILIZATION_SHADOW_DOCTRINE_AMENDMENT_SPEC_BLOB,
        "r26Candidate": R26_CANDIDATE,
        "r26Merge": R26_MERGE,
    }
    if base != expected:
        raise Phase3Error("FROZEN_BASE_MISMATCH")
    if _commit_tuple(MASTER_COMMIT)[0] != MASTER_TREE:
        raise Phase3Error("PUBLISHED_MASTER_OBJECT_MISMATCH")
    if _commit_tuple(INITIAL_FOLD_COMMIT) != (INITIAL_FOLD_TREE, [MASTER_COMMIT]):
        raise Phase3Error("INITIAL_SPEC_FOLD_OBJECT_MISMATCH")
    if _commit_tuple(SPEC_BINDING_COMMIT) != (SPEC_BINDING_TREE, [INITIAL_FOLD_COMMIT]):
        raise Phase3Error("SPEC_BINDING_OBJECT_MISMATCH")
    if _commit_tuple(PHASE3_PUBLISHED_COMMIT)[0] != PHASE3_PUBLISHED_TREE:
        raise Phase3Error("PHASE3_PUBLISHED_OBJECT_MISMATCH")
    if not _is_ancestor(SPEC_BINDING_COMMIT, PHASE3_PUBLISHED_COMMIT):
        raise Phase3Error("PHASE3_PUBLISHED_LINEAGE_MISMATCH")
    if _commit_tuple(ADVERSARIAL_SPEC_BINDING_COMMIT) != (
        ADVERSARIAL_SPEC_BINDING_TREE,
        [PHASE3_PUBLISHED_COMMIT],
    ):
        raise Phase3Error("ADVERSARIAL_SPEC_BINDING_OBJECT_MISMATCH")
    if _changed_paths(MASTER_COMMIT, INITIAL_FOLD_COMMIT) != SPEC_PATHS:
        raise Phase3Error("INITIAL_SPEC_FOLD_SCOPE_INVALID")
    if _changed_paths(INITIAL_FOLD_COMMIT, SPEC_BINDING_COMMIT) != SPEC_PATHS:
        raise Phase3Error("SPEC_BINDING_SCOPE_INVALID")
    if _changed_paths(PHASE3_PUBLISHED_COMMIT, ADVERSARIAL_SPEC_BINDING_COMMIT) != {
        "specs/adversarialllm.md"
    }:
        raise Phase3Error("ADVERSARIAL_SPEC_BINDING_SCOPE_INVALID")
    if _commit_tuple(PRE_ADVERSARIAL_SPEC_REPAIR_COMMIT)[0] != PRE_ADVERSARIAL_SPEC_REPAIR_TREE:
        raise Phase3Error("PRE_ADVERSARIAL_SPEC_REPAIR_OBJECT_MISMATCH")
    if not _is_ancestor(ADVERSARIAL_SPEC_BINDING_COMMIT, PRE_ADVERSARIAL_SPEC_REPAIR_COMMIT):
        raise Phase3Error("PRE_ADVERSARIAL_SPEC_REPAIR_LINEAGE_MISMATCH")
    if _commit_tuple(ADVERSARIAL_SPEC_REPAIR_COMMIT) != (
        ADVERSARIAL_SPEC_REPAIR_TREE,
        [PRE_ADVERSARIAL_SPEC_REPAIR_COMMIT],
    ):
        raise Phase3Error("ADVERSARIAL_SPEC_REPAIR_OBJECT_MISMATCH")
    if _changed_paths(PRE_ADVERSARIAL_SPEC_REPAIR_COMMIT, ADVERSARIAL_SPEC_REPAIR_COMMIT) != {
        "specs/adversarialllm.md"
    }:
        raise Phase3Error("ADVERSARIAL_SPEC_REPAIR_SCOPE_INVALID")
    if _commit_tuple(UTILIZATION_SHADOW_DOCTRINE_BASE_COMMIT)[0] != UTILIZATION_SHADOW_DOCTRINE_BASE_TREE:
        raise Phase3Error("UTILIZATION_SHADOW_DOCTRINE_BASE_OBJECT_MISMATCH")
    if _commit_tuple(UTILIZATION_SHADOW_DOCTRINE_AMENDMENT_COMMIT) != (
        UTILIZATION_SHADOW_DOCTRINE_AMENDMENT_TREE,
        [UTILIZATION_SHADOW_DOCTRINE_BASE_COMMIT],
    ):
        raise Phase3Error("UTILIZATION_SHADOW_DOCTRINE_AMENDMENT_OBJECT_MISMATCH")
    if _changed_paths(
        UTILIZATION_SHADOW_DOCTRINE_BASE_COMMIT,
        UTILIZATION_SHADOW_DOCTRINE_AMENDMENT_COMMIT,
    ) != {"specs/adversarialllm.md"}:
        raise Phase3Error("UTILIZATION_SHADOW_DOCTRINE_AMENDMENT_SCOPE_INVALID")
    if _oid(
        UTILIZATION_SHADOW_DOCTRINE_AMENDMENT_COMMIT,
        "specs/adversarialllm.md",
    ) != UTILIZATION_SHADOW_DOCTRINE_AMENDMENT_SPEC_BLOB:
        raise Phase3Error("UTILIZATION_SHADOW_DOCTRINE_AMENDMENT_SPEC_MISMATCH")
    descendant = "HEAD" if treeish == ":" else treeish
    if not _is_ancestor(UTILIZATION_SHADOW_DOCTRINE_AMENDMENT_COMMIT, descendant):
        raise Phase3Error("UTILIZATION_SHADOW_DOCTRINE_AMENDMENT_NOT_ANCESTOR")
    if not _changed_paths(UTILIZATION_SHADOW_DOCTRINE_AMENDMENT_COMMIT, treeish).issubset(
        ALLOWED_PHASE3_PATHS
    ):
        raise Phase3Error("PHASE3_SCOPE_VIOLATION")


def _verify_project(
    project: Any,
    *,
    ledger_rows: dict[str, dict[str, Any]],
    treeish: str,
) -> str:
    project = _exact_keys(
        project,
        {"projectId", "specPath", "centralEvidence", "projectCandidate"},
        "PROJECT_RECORD_INVALID",
    )
    project_id = project["projectId"]
    if project_id not in PROJECT_IDS or project["specPath"] != f"specs/{project_id}.md":
        raise Phase3Error("PROJECT_ID_OR_PATH_INVALID")
    ledger_row = ledger_rows.get(project_id)
    if ledger_row is None:
        raise Phase3Error("LEDGER_PROJECT_MISSING")
    if (
        ledger_row.get("status") != "DISTINGUISH"
        or ledger_row.get("blocker") != "PROJECT_OWNER_DISTINCTION_OPEN"
        or ledger_row.get("nonRegressionEvidence") is not None
    ):
        raise Phase3Error("LEDGER_PROJECT_DISPOSITION_INVALID")
    evidence = ledger_row.get("evidence")
    if not isinstance(evidence, dict):
        raise Phase3Error("LEDGER_EVIDENCE_INVALID")
    central = _exact_keys(
        project["centralEvidence"],
        {"commit", "gitBlobOid"},
        "CENTRAL_EVIDENCE_INVALID",
    )
    evidence_commit = (
        UTILIZATION_SHADOW_DOCTRINE_AMENDMENT_COMMIT
        if project_id == "adversarialllm"
        else SPEC_BINDING_COMMIT
    )
    if central != {
        "commit": evidence_commit,
        "gitBlobOid": _oid(evidence_commit, project["specPath"]),
    }:
        raise Phase3Error("CENTRAL_EVIDENCE_MISMATCH")
    if (
        evidence.get("commit") != central["commit"]
        or evidence.get("gitBlobOid") != central["gitBlobOid"]
        or _oid(treeish, project["specPath"]) != central["gitBlobOid"]
    ):
        raise Phase3Error("CENTRAL_SPEC_DRIFT")
    candidate = project["projectCandidate"]
    if candidate != evidence.get("projectCandidate"):
        raise Phase3Error("INTAKE_LEDGER_CANDIDATE_MISMATCH")
    if _contains_formal_adopt(candidate):
        raise Phase3Error("PROJECT_CANDIDATE_ADOPTION_OVERCLAIM")
    authority = candidate.get("authorityClaims") if isinstance(candidate, dict) else None
    if (
        not isinstance(authority, dict)
        or any(value is not False for value in authority.values())
        or candidate.get("adoptionProofCredit") is not False
        or candidate.get("nonRegressionCredit") is not False
    ):
        raise Phase3Error("PROJECT_CANDIDATE_AUTHORITY_OVERCLAIM")
    disposition = candidate.get("disposition")
    if (
        not isinstance(disposition, dict)
        or disposition.get("kind") != "DISTINGUISH"
        or disposition.get("subjectCommit") != R26_MERGE
        or not isinstance(disposition.get("statement"), str)
        or _blob(evidence_commit, project["specPath"]).count(
            disposition["statement"].encode("utf-8")
        )
        != 1
    ):
        raise Phase3Error("PROJECT_CANDIDATE_DISPOSITION_INVALID")
    if _canonical_sha256(candidate) != EXPECTED_PROJECT_CANDIDATE_SHA256[project_id]:
        raise Phase3Error("PROJECT_CANDIDATE_EXACT_BINDING_MISMATCH")
    return project_id


def verify_batch(batch: dict[str, Any], treeish: str = "HEAD") -> None:
    batch = _exact_keys(
        batch,
        {"schema", "status", "frozenBase", "summary", "projects"},
        "BATCH_FIELDS_INVALID",
    )
    if batch["schema"] != SCHEMA or batch["status"] != "PUBLISHED_PROJECT_DISTINCTIONS_ZERO_AUTHORITY":
        raise Phase3Error("BATCH_IDENTITY_INVALID")
    _verify_frozen_base(batch["frozenBase"], treeish)
    ledger = load_json(_blob(treeish, LEDGER_PATH))
    census = ledger.get("census")
    if not isinstance(census, dict):
        raise Phase3Error("LEDGER_CENSUS_INVALID")
    if census.get("baseCommit") != UTILIZATION_SHADOW_DOCTRINE_AMENDMENT_COMMIT:
        raise Phase3Error("LEDGER_CENSUS_BASE_MISMATCH")
    if ledger.get("summary") != {
        "projectCount": 9,
        "counts": {"ADOPT": 0, "DISTINGUISH": 5, "MISSING": 0, "REJECT": 0, "STALE": 4},
        "fleetStatus": "NO_FLEET_ADOPTION",
        "fleetAdoptionClaim": False,
    }:
        raise Phase3Error("LEDGER_SUMMARY_OVERCLAIM")
    rows = ledger.get("projects")
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise Phase3Error("LEDGER_PROJECTS_INVALID")
    ledger_ids = [row.get("projectId") for row in rows]
    if (
        len(rows) != len(LEDGER_PROJECT_IDS)
        or any(not isinstance(project_id, str) for project_id in ledger_ids)
        or ledger_ids != sorted(LEDGER_PROJECT_IDS)
        or len(set(ledger_ids)) != len(ledger_ids)
    ):
        raise Phase3Error("LEDGER_PROJECT_SET_INVALID")
    ledger_rows = {row["projectId"]: row for row in rows}
    for project_id, row in ledger_rows.items():
        evidence = row.get("evidence")
        if not isinstance(evidence, dict) or "projectCandidate" not in evidence:
            raise Phase3Error("LEDGER_PROJECT_CANDIDATE_MIGRATION_INVALID")
        project_candidate = evidence["projectCandidate"]
        if (
            project_id in PROJECT_IDS and project_candidate is None
        ) or (
            project_id not in PROJECT_IDS and project_candidate is not None
        ):
            raise Phase3Error("LEDGER_PROJECT_CANDIDATE_MIGRATION_INVALID")
    projects = batch["projects"]
    if not isinstance(projects, list) or len(projects) != len(PROJECT_IDS):
        raise Phase3Error("PROJECT_SET_INVALID")
    ids = [
        _verify_project(project, ledger_rows=ledger_rows, treeish=treeish)
        for project in projects
    ]
    if ids != sorted(PROJECT_IDS) or len(ids) != len(set(ids)):
        raise Phase3Error("PROJECT_SET_INVALID")
    if batch["summary"] != {
        "projectCount": 4,
        "distinguishCandidates": 4,
        "adoptionClaims": 0,
        "runtimeAuthorityClaims": 0,
    }:
        raise Phase3Error("SUMMARY_OVERCLAIM")


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


def _run_remote_git(
    args: list[str],
    *,
    cwd: Path,
    environment: dict[str, str],
    project_id: str,
    error: str,
    text: bool = False,
) -> bytes | str:
    try:
        run = subprocess.run(
            ["git", *args],
            cwd=cwd,
            env=environment,
            check=False,
            capture_output=True,
            text=text,
            encoding="utf-8" if text else None,
            timeout=REMOTE_GIT_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise Phase3Error(f"PUBLISHED_REMOTE_GIT_TIMEOUT:{project_id}") from exc
    except OSError as exc:
        raise Phase3Error(f"PUBLISHED_REMOTE_GIT_EXECUTION_FAILED:{project_id}") from exc
    if run.returncode != 0:
        raise Phase3Error(f"{error}:{project_id}")
    return run.stdout


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
        raise Phase3Error("PUBLISHED_REMOTE_AUTH_TOKEN_INVALID")
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


def _remote_commit_tuple(
    repo: Path,
    environment: dict[str, str],
    project_id: str,
    commit: str,
) -> tuple[str, list[str]]:
    value = _run_remote_git(
        ["show", "-s", "--format=%T%n%P", commit],
        cwd=repo,
        environment=environment,
        project_id=project_id,
        error="PUBLISHED_REMOTE_COMMIT_UNAVAILABLE",
        text=True,
    )
    lines = value.splitlines()
    if (
        len(lines) != 2
        or SHA_PATTERN.fullmatch(lines[0]) is None
        or any(SHA_PATTERN.fullmatch(parent) is None for parent in lines[1].split())
    ):
        raise Phase3Error(f"PUBLISHED_REMOTE_COMMIT_OBJECT_INVALID:{project_id}")
    return lines[0], lines[1].split() if lines[1] else []


def _remote_artifact_oid(
    repo: Path,
    environment: dict[str, str],
    project_id: str,
    commit: str,
    path: str,
) -> str:
    raw = _run_remote_git(
        ["ls-tree", "-z", "--full-tree", commit, "--", path],
        cwd=repo,
        environment=environment,
        project_id=project_id,
        error="PUBLISHED_REMOTE_ARTIFACT_LOOKUP_FAILED",
    )
    entries = raw[:-1].split(b"\0") if raw.endswith(b"\0") else []
    if len(entries) != 1 or b"\t" not in entries[0]:
        raise Phase3Error(f"PUBLISHED_REMOTE_ARTIFACT_ENTRY_INVALID:{project_id}")
    metadata, raw_path = entries[0].split(b"\t", 1)
    try:
        mode, object_type, oid = metadata.decode("ascii").split()
        decoded_path = raw_path.decode("utf-8")
    except (UnicodeDecodeError, ValueError) as exc:
        raise Phase3Error(f"PUBLISHED_REMOTE_ARTIFACT_ENTRY_INVALID:{project_id}") from exc
    if (
        mode not in {"100644", "100755"}
        or object_type != "blob"
        or SHA_PATTERN.fullmatch(oid) is None
        or decoded_path != path
    ):
        raise Phase3Error(f"PUBLISHED_REMOTE_ARTIFACT_ENTRY_INVALID:{project_id}")
    return oid


def _verify_remote_project(project: dict[str, Any]) -> None:
    project_id = project.get("projectId")
    if project_id not in PROJECT_IDS:
        raise Phase3Error("PUBLISHED_REMOTE_PROJECT_INVALID")
    candidate = project.get("projectCandidate")
    if not isinstance(candidate, dict):
        raise Phase3Error(f"PUBLISHED_REMOTE_CANDIDATE_INVALID:{project_id}")
    allowlisted = PUBLISHED_REMOTE_ALLOWLIST[project_id]
    if {
        "remote": candidate.get("remote"),
        "publishedRef": candidate.get("publishedRef"),
    } != allowlisted:
        raise Phase3Error(f"PUBLISHED_REMOTE_URL_REF_NOT_ALLOWLISTED:{project_id}")
    token = _remote_auth_token()

    with tempfile.TemporaryDirectory(prefix=REMOTE_TEMP_PREFIX) as temp_name:
        temp_root = Path(temp_name)
        askpass_path = _write_askpass(temp_root)
        global_config_path = _write_global_git_config(temp_root, token)
        environment = _remote_environment(askpass_path, global_config_path)
        repo = temp_root / "objects"
        repo.mkdir()
        _run_remote_git(
            ["init", "--quiet"],
            cwd=repo,
            environment=environment,
            project_id=project_id,
            error="PUBLISHED_REMOTE_INIT_FAILED",
        )
        remote = allowlisted["remote"]
        published_ref = allowlisted["publishedRef"]
        advertised = _run_remote_git(
            ["ls-remote", "--exit-code", "--refs", "--", remote, published_ref],
            cwd=repo,
            environment=environment,
            project_id=project_id,
            error="PUBLISHED_REMOTE_REF_QUERY_FAILED",
            text=True,
        )
        if advertised.splitlines() != [f"{candidate['commit']}\t{published_ref}"]:
            raise Phase3Error(f"PUBLISHED_REMOTE_REF_MISMATCH:{project_id}")
        _run_remote_git(
            [
                "fetch",
                "--quiet",
                "--no-tags",
                "--no-recurse-submodules",
                "--depth",
                str(REMOTE_FETCH_DEPTH),
                "--",
                remote,
                published_ref,
            ],
            cwd=repo,
            environment=environment,
            project_id=project_id,
            error="PUBLISHED_REMOTE_FETCH_FAILED",
        )
        fetched = _run_remote_git(
            ["rev-parse", "--verify", "--end-of-options", "FETCH_HEAD^{commit}"],
            cwd=repo,
            environment=environment,
            project_id=project_id,
            error="PUBLISHED_REMOTE_FETCH_HEAD_INVALID",
            text=True,
        ).strip()
        if fetched != candidate["commit"]:
            raise Phase3Error(f"PUBLISHED_REMOTE_FETCH_HEAD_MISMATCH:{project_id}")

        tree, parents = _remote_commit_tuple(repo, environment, project_id, candidate["commit"])
        if tree != candidate["tree"]:
            raise Phase3Error(f"PUBLISHED_REMOTE_TREE_MISMATCH:{project_id}")
        if len(parents) != 1:
            raise Phase3Error(f"PUBLISHED_REMOTE_PARENT_COUNT_INVALID:{project_id}")
        if parents[0] != candidate["parent"]:
            raise Phase3Error(f"PUBLISHED_REMOTE_PARENT_MISMATCH:{project_id}")
        _run_remote_git(
            ["cat-file", "-e", f"{candidate['baseCommit']}^{{commit}}"],
            cwd=repo,
            environment=environment,
            project_id=project_id,
            error="PUBLISHED_REMOTE_BASE_UNAVAILABLE",
        )
        _run_remote_git(
            ["merge-base", "--is-ancestor", candidate["baseCommit"], candidate["commit"]],
            cwd=repo,
            environment=environment,
            project_id=project_id,
            error="PUBLISHED_REMOTE_BASE_ANCESTRY_MISMATCH",
        )

        artifacts = candidate.get("artifacts")
        if not isinstance(artifacts, list) or not artifacts:
            raise Phase3Error(f"PUBLISHED_REMOTE_ARTIFACT_SET_INVALID:{project_id}")
        for artifact in artifacts:
            if not isinstance(artifact, dict) or not isinstance(artifact.get("path"), str):
                raise Phase3Error(f"PUBLISHED_REMOTE_ARTIFACT_RECORD_INVALID:{project_id}")
            path = artifact["path"]
            oid = _remote_artifact_oid(
                repo,
                environment,
                project_id,
                candidate["commit"],
                path,
            )
            if oid != artifact.get("gitBlobOid"):
                raise Phase3Error(f"PUBLISHED_REMOTE_ARTIFACT_BLOB_MISMATCH:{project_id}")
            raw_size = _run_remote_git(
                ["cat-file", "-s", oid],
                cwd=repo,
                environment=environment,
                project_id=project_id,
                error="PUBLISHED_REMOTE_ARTIFACT_SIZE_UNAVAILABLE",
                text=True,
            ).strip()
            try:
                size = int(raw_size)
            except ValueError as exc:
                raise Phase3Error(f"PUBLISHED_REMOTE_ARTIFACT_SIZE_INVALID:{project_id}") from exc
            if size < 0 or size > REMOTE_MAX_ARTIFACT_BYTES:
                raise Phase3Error(f"PUBLISHED_REMOTE_ARTIFACT_SIZE_LIMIT:{project_id}")
            if size != artifact.get("bytes"):
                raise Phase3Error(f"PUBLISHED_REMOTE_ARTIFACT_BYTE_MISMATCH:{project_id}")
            raw = _run_remote_git(
                ["cat-file", "blob", oid],
                cwd=repo,
                environment=environment,
                project_id=project_id,
                error="PUBLISHED_REMOTE_ARTIFACT_READ_FAILED",
            )
            if len(raw) != size:
                raise Phase3Error(f"PUBLISHED_REMOTE_ARTIFACT_READ_SIZE_MISMATCH:{project_id}")
            if hashlib.sha256(raw).hexdigest() != artifact.get("sha256"):
                raise Phase3Error(f"PUBLISHED_REMOTE_ARTIFACT_SHA256_MISMATCH:{project_id}")


def verify_remotes(batch: dict[str, Any]) -> None:
    projects = batch.get("projects")
    if (
        not isinstance(projects, list)
        or len(projects) != len(PROJECT_IDS)
        or any(not isinstance(project, dict) for project in projects)
    ):
        raise Phase3Error("PUBLISHED_REMOTE_PROJECT_SET_INVALID")
    ids = [project.get("projectId") for project in projects]
    if ids != sorted(PROJECT_IDS):
        raise Phase3Error("PUBLISHED_REMOTE_PROJECT_SET_INVALID")
    for project in projects:
        project_id = project["projectId"]
        if _canonical_sha256(project.get("projectCandidate")) != EXPECTED_PROJECT_CANDIDATE_SHA256[
            project_id
        ]:
            raise Phase3Error(f"PUBLISHED_REMOTE_CANDIDATE_EXACT_BINDING_MISMATCH:{project_id}")
    for project in projects:
        _verify_remote_project(project)


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
    except Phase3Error as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    if args.verify_remotes:
        print(
            "PASS: phase-3 published project distinctions are exact, zero-authority, closed-set; "
            "REMOTES VERIFIED"
        )
    else:
        print(
            "PASS LOCAL-ONLY: phase-3 published project distinctions are exact, zero-authority, "
            "closed-set; REMOTES NOT VERIFIED"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
