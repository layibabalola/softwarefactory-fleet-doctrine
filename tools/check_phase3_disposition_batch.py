#!/usr/bin/env python3
"""Verify the exact zero-authority R26 phase-3 published-project distinctions."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
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
R26_CANDIDATE = "e70a044f31dd2f43ab7c716d63a4eb89318c61b6"
R26_MERGE = "909f769d02e8412e51e28e242cfa8d00dadc9a3d"
PROJECT_IDS = {"cloudvore", "mlv-app", "salesforce-tools"}
SPEC_PATHS = {f"specs/{project_id}.md" for project_id in PROJECT_IDS}
EXPECTED_PROJECT_CANDIDATE_SHA256 = {
    "cloudvore": "7bbafaa69078bf3464f5e54c6f1e0a689113c54ce7df7f494d017beef58be436",
    "mlv-app": "55544254f982890efa8b2e309b0eeb2be09f85d7f09f7da86083ba2856cbf9ba",
    "salesforce-tools": "b2278e858cf70c0a6eecca6d7842709e9cc6fe4598fa13af6bf64929c05b0f6f",
}
ALLOWED_PHASE3_PATHS = {
    ".github/workflows/disposition-intake.yml",
    "adoption/README.md",
    "adoption/phase3/README.md",
    INTAKE_PATH,
    LEDGER_PATH,
    "tests/test_adoption_ledger.py",
    "tests/test_phase2_disposition_batch.py",
    "tests/test_phase3_disposition_batch.py",
    "tools/check_adoption_ledger.py",
    "tools/check_phase2_disposition_batch.py",
    "tools/check_phase3_disposition_batch.py",
}
SHA_PATTERN = re.compile(r"[0-9a-f]{40,64}")
FORMAL_ADOPT_PATTERN = re.compile(r"\bADOPT\s*\(", re.IGNORECASE)


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
    if _changed_paths(MASTER_COMMIT, INITIAL_FOLD_COMMIT) != SPEC_PATHS:
        raise Phase3Error("INITIAL_SPEC_FOLD_SCOPE_INVALID")
    if _changed_paths(INITIAL_FOLD_COMMIT, SPEC_BINDING_COMMIT) != SPEC_PATHS:
        raise Phase3Error("SPEC_BINDING_SCOPE_INVALID")
    descendant = "HEAD" if treeish == ":" else treeish
    if not _is_ancestor(SPEC_BINDING_COMMIT, descendant):
        raise Phase3Error("SPEC_BINDING_NOT_ANCESTOR")
    if not _changed_paths(SPEC_BINDING_COMMIT, treeish).issubset(ALLOWED_PHASE3_PATHS):
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
    if central != {
        "commit": SPEC_BINDING_COMMIT,
        "gitBlobOid": _oid(SPEC_BINDING_COMMIT, project["specPath"]),
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
        or _blob(SPEC_BINDING_COMMIT, project["specPath"]).count(
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
    if ledger.get("census", {}).get("baseCommit") != SPEC_BINDING_COMMIT:
        raise Phase3Error("LEDGER_CENSUS_BASE_MISMATCH")
    if ledger.get("summary") != {
        "projectCount": 9,
        "counts": {"ADOPT": 0, "DISTINGUISH": 4, "MISSING": 0, "REJECT": 0, "STALE": 5},
        "fleetStatus": "NO_FLEET_ADOPTION",
        "fleetAdoptionClaim": False,
    }:
        raise Phase3Error("LEDGER_SUMMARY_OVERCLAIM")
    rows = ledger.get("projects")
    if not isinstance(rows, list):
        raise Phase3Error("LEDGER_PROJECTS_INVALID")
    ledger_rows = {
        row.get("projectId"): row for row in rows if isinstance(row, dict)
    }
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
        "projectCount": 3,
        "distinguishCandidates": 3,
        "adoptionClaims": 0,
        "runtimeAuthorityClaims": 0,
    }:
        raise Phase3Error("SUMMARY_OVERCLAIM")


def verify_remotes(batch: dict[str, Any]) -> None:
    for project in batch["projects"]:
        candidate = project["projectCandidate"]
        run = subprocess.run(
            ["git", "ls-remote", candidate["remote"], candidate["publishedRef"]],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        expected = f"{candidate['commit']}\t{candidate['publishedRef']}"
        if run.returncode != 0 or run.stdout.strip() != expected:
            raise Phase3Error(f"PUBLISHED_REMOTE_REF_MISMATCH:{project['projectId']}")


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
    print("PASS: phase-3 published project distinctions are exact, zero-authority, and closed-set")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
