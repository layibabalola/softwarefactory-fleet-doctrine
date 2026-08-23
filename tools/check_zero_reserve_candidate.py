#!/usr/bin/env python3
"""Verify the exact zero-authority 0% discretionary-reserve R2 candidate."""

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
DEFAULT_MANIFEST = ROOT / "manifests/zero-discretionary-capacity-reserve-r2.json"
SCHEMA = "fleet-zero-discretionary-capacity-reserve-candidate-manifest/v1"
STATUS = "CANDIDATE_ZERO_AUTHORITY"
EXPECTED_CHANGED_PATHS = [
    "README.md",
    "capacity-control/PROJECT-ADOPTION-MATRIX.md",
    "ruling-candidates/zero-discretionary-capacity-reserve-r2.md",
]
EXPECTED_SUBJECT_PATHS = EXPECTED_CHANGED_PATHS + [
    "adoption/universal-token-control-r26.json",
    "examples/provider-admission-snapshot-v1.json",
    "policy/universal-provider-token-control-r22.json",
]
EXPECTED_PROJECT_IDS = [
    "adobe-ingester",
    "adversarialllm",
    "agent-bridge",
    "airmypc",
    "cloudvore",
    "conjugal",
    "dng-auto-processor",
    "mlv-app",
    "salesforce-tools",
]
EXPECTED_MATRIX_LABELS = [
    "Adobe Ingester",
    "AdversarialLLM",
    "agent-bridge",
    "AirMyPC / AudioMile",
    "Cloudvore",
    "Conjugal",
    "DNG AutoProcessor",
    "MLV-App",
    "Salesforce Tools",
]
SHA1 = re.compile(r"[0-9a-f]{40}")
SHA256 = re.compile(r"sha256:[0-9a-f]{64}")
SELF_FIELD = re.compile(
    rb'("canonicalGitBlobSha256"\s*:\s*"sha256:)([0-9a-f]{64})(")'
)


class CandidateError(ValueError):
    pass


def _pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in values:
        if key in result:
            raise CandidateError("DUPLICATE_KEY")
        result[key] = value
    return result


def _strict_json(data: bytes, error: str) -> dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError, CandidateError) as exc:
        raise CandidateError(error) from exc
    if not isinstance(value, dict):
        raise CandidateError(error)
    return value


def _git(root: Path, args: list[str], *, text: bool = False) -> bytes | str:
    run = subprocess.run(
        ["git", *args], cwd=root, check=False, capture_output=True,
        text=text, encoding="utf-8" if text else None,
    )
    if run.returncode != 0:
        raise CandidateError("GIT_OBJECT_UNAVAILABLE")
    return run.stdout


def _blob(root: Path, commit: str, path: str) -> bytes:
    return _git(root, ["show", f"{commit}:{path}"])  # type: ignore[return-value]


def _oid(root: Path, commit: str, path: str) -> str:
    value = str(_git(root, ["rev-parse", f"{commit}:{path}"], text=True)).strip()
    if SHA1.fullmatch(value) is None:
        raise CandidateError("GIT_BLOB_OID_INVALID")
    return value


def _commit_tuple(root: Path, commit: str) -> tuple[str, list[str]]:
    raw = str(_git(root, ["show", "-s", "--format=%T%n%P", commit], text=True))
    lines = raw.splitlines()
    if len(lines) != 2 or SHA1.fullmatch(lines[0]) is None:
        raise CandidateError("SOURCE_COMMIT_INVALID")
    parents = lines[1].split() if lines[1] else []
    if any(SHA1.fullmatch(parent) is None for parent in parents):
        raise CandidateError("SOURCE_COMMIT_INVALID")
    return lines[0], parents


def _changed_paths(root: Path, parent: str, commit: str) -> list[str]:
    raw = str(
        _git(
            root,
            ["diff-tree", "--no-commit-id", "--name-only", "-r", parent, commit],
            text=True,
        )
    )
    return [line for line in raw.splitlines() if line]


def _exact_keys(value: Any, expected: set[str], error: str) -> None:
    if not isinstance(value, dict) or set(value) != expected:
        raise CandidateError(error)


def _manifest_self(manifest_bytes: bytes, declared: str) -> None:
    matches = list(SELF_FIELD.finditer(manifest_bytes))
    if len(matches) != 1 or SHA256.fullmatch(declared) is None:
        raise CandidateError("MANIFEST_SELF_INVALID")
    zeroed = SELF_FIELD.sub(lambda m: m.group(1) + b"0" * 64 + m.group(3), manifest_bytes)
    actual = "sha256:" + hashlib.sha256(zeroed).hexdigest()
    if actual != declared:
        raise CandidateError("MANIFEST_SELF_MISMATCH")


def verify(root: Path, manifest_path: Path) -> str:
    manifest_bytes = manifest_path.read_bytes()
    manifest = _strict_json(manifest_bytes, "MANIFEST_JSON_INVALID")
    _exact_keys(
        manifest,
        {
            "schema", "status", "candidateId", "source", "predecessor",
            "closedProjectSet", "migrationSurface", "validation", "authorRecusal",
            "subjectFiles", "authority", "manifestSelf",
        },
        "MANIFEST_SHAPE_INVALID",
    )
    if manifest["schema"] != SCHEMA or manifest["status"] != STATUS:
        raise CandidateError("MANIFEST_IDENTITY_INVALID")
    if manifest["candidateId"] != "ZERO_DISCRETIONARY_CAPACITY_RESERVE_R2":
        raise CandidateError("CANDIDATE_ID_INVALID")

    self_record = manifest["manifestSelf"]
    _exact_keys(self_record, {"path", "canonicalGitBlobSha256", "rule"}, "MANIFEST_SELF_SHAPE_INVALID")
    if self_record["path"] != "manifests/zero-discretionary-capacity-reserve-r2.json":
        raise CandidateError("MANIFEST_SELF_PATH_INVALID")
    _manifest_self(manifest_bytes, self_record["canonicalGitBlobSha256"])

    source = manifest["source"]
    _exact_keys(source, {"commit", "tree", "orderedParents", "changedPaths"}, "SOURCE_SHAPE_INVALID")
    commit = source["commit"]
    if not isinstance(commit, str) or SHA1.fullmatch(commit) is None:
        raise CandidateError("SOURCE_COMMIT_INVALID")
    tree, parents = _commit_tuple(root, commit)
    if tree != source["tree"] or parents != source["orderedParents"] or len(parents) != 1:
        raise CandidateError("SOURCE_TUPLE_MISMATCH")
    if source["changedPaths"] != EXPECTED_CHANGED_PATHS:
        raise CandidateError("CHANGED_PATH_MANIFEST_INVALID")
    if _changed_paths(root, parents[0], commit) != EXPECTED_CHANGED_PATHS:
        raise CandidateError("SOURCE_DIFF_INVALID")
    if any(not path.endswith(".md") for path in EXPECTED_CHANGED_PATHS):
        raise CandidateError("SOURCE_DIFF_NOT_DOCUMENTATION_ONLY")

    predecessor = manifest["predecessor"]
    _exact_keys(predecessor, {"commit", "tree", "candidatePath", "disposition"}, "PREDECESSOR_SHAPE_INVALID")
    predecessor_tree, predecessor_parents = _commit_tuple(root, predecessor["commit"])
    if predecessor["commit"] != parents[0] or predecessor_tree != predecessor["tree"]:
        raise CandidateError("PREDECESSOR_TUPLE_MISMATCH")
    if predecessor["candidatePath"] != "ruling-candidates/zero-discretionary-capacity-reserve-r1.md":
        raise CandidateError("PREDECESSOR_PATH_INVALID")
    if not predecessor_parents:
        raise CandidateError("PREDECESSOR_HISTORY_INVALID")

    subjects = manifest["subjectFiles"]
    if not isinstance(subjects, list) or len(subjects) != len(EXPECTED_SUBJECT_PATHS):
        raise CandidateError("SUBJECT_SET_INVALID")
    if [row.get("path") for row in subjects if isinstance(row, dict)] != EXPECTED_SUBJECT_PATHS:
        raise CandidateError("SUBJECT_ORDER_INVALID")
    for row in subjects:
        _exact_keys(row, {"path", "gitBlobOid", "bytes", "sha256"}, "SUBJECT_SHAPE_INVALID")
        blob = _blob(root, commit, row["path"])
        if row["gitBlobOid"] != _oid(root, commit, row["path"]):
            raise CandidateError("SUBJECT_OID_MISMATCH")
        if not isinstance(row["bytes"], int) or isinstance(row["bytes"], bool) or row["bytes"] != len(blob):
            raise CandidateError("SUBJECT_BYTES_MISMATCH")
        digest = "sha256:" + hashlib.sha256(blob).hexdigest()
        if row["sha256"] != digest:
            raise CandidateError("SUBJECT_SHA256_MISMATCH")

    project_set = manifest["closedProjectSet"]
    _exact_keys(project_set, {"ledgerPath", "count", "projectIds"}, "PROJECT_SET_SHAPE_INVALID")
    if project_set["ledgerPath"] != "adoption/universal-token-control-r26.json":
        raise CandidateError("LEDGER_PATH_INVALID")
    if project_set["count"] != 9 or project_set["projectIds"] != EXPECTED_PROJECT_IDS:
        raise CandidateError("PROJECT_SET_INVALID")
    ledger = _strict_json(_blob(root, commit, project_set["ledgerPath"]), "LEDGER_JSON_INVALID")
    projects = ledger.get("projects")
    if not isinstance(projects, list):
        raise CandidateError("LEDGER_PROJECTS_INVALID")
    ledger_ids = [row.get("projectId") for row in projects if isinstance(row, dict)]
    if ledger_ids != EXPECTED_PROJECT_IDS or len(ledger_ids) != len(set(ledger_ids)):
        raise CandidateError("LEDGER_PROJECT_SET_MISMATCH")
    statuses = [row.get("status") for row in projects]
    if statuses.count("ADOPT") != 0 or statuses.count("DISTINGUISH") != 5 or statuses.count("STALE") != 4:
        raise CandidateError("LEDGER_COUNTS_MISMATCH")

    candidate = _blob(root, commit, EXPECTED_CHANGED_PATHS[2]).decode("utf-8")
    required_fragments = [
        "PROPOSED ONLY — NOT YET A RATIFIED RULING OR PROJECT RUNTIME AUTHORITY",
        "discretionary capacity reserve to 0%",
        "fresh proven utilization + active reservations + estimated slice <= 100%",
        "exact provider, model, effort, role, review",
        "output, and functionality",
        "terminal-output token reserves",
        "active work reservations",
        "hard 100% ceiling",
        "RULINGS.md",
    ]
    if any(fragment not in candidate for fragment in required_fragments):
        raise CandidateError("CANDIDATE_LAW_INCOMPLETE")
    candidate_ids = re.findall(r"(?m)^\d+\. `([^`]+)`$", candidate)
    if candidate_ids != EXPECTED_PROJECT_IDS:
        raise CandidateError("CANDIDATE_PROJECT_SET_MISMATCH")

    matrix = _blob(root, commit, EXPECTED_CHANGED_PATHS[1]).decode("utf-8")
    matrix_labels = [
        match.group(1).strip()
        for match in re.finditer(r"(?m)^\| ([^|]+) \|", matrix)
        if match.group(1).strip() != "Project"
    ]
    if matrix_labels != EXPECTED_MATRIX_LABELS:
        raise CandidateError("MATRIX_PROJECT_SET_MISMATCH")
    if "zero-discretionary-capacity-reserve-r2" not in matrix:
        raise CandidateError("MATRIX_CANDIDATE_LINK_MISSING")

    readme = _blob(root, commit, EXPECTED_CHANGED_PATHS[0]).decode("utf-8")
    if "ruling-candidates/zero-discretionary-capacity-reserve-r2.md" not in readme:
        raise CandidateError("README_CANDIDATE_LINK_MISSING")
    if "ruling-candidates/zero-discretionary-capacity-reserve-r1.md" in readme:
        raise CandidateError("README_STALE_ACTIVE_LINK")

    migration = manifest["migrationSurface"]
    _exact_keys(
        migration,
        {"ratifiedGovernorExample", "r22CandidatePolicy", "replacementValuePct", "hardEstimatedCeilingPct"},
        "MIGRATION_SHAPE_INVALID",
    )
    if migration["replacementValuePct"] != 0 or migration["hardEstimatedCeilingPct"] != 100:
        raise CandidateError("MIGRATION_BOUNDARY_INVALID")
    ratified = _strict_json(_blob(root, commit, migration["ratifiedGovernorExample"]["path"]), "RATIFIED_EXAMPLE_INVALID")
    r22 = _strict_json(_blob(root, commit, migration["r22CandidatePolicy"]["path"]), "R22_POLICY_INVALID")
    if ratified.get("policy", {}).get("interactive_reserve_pct") != 30:
        raise CandidateError("RATIFIED_RESERVE_VALUE_MISMATCH")
    if r22.get("completionReserve", {}).get("quotaWindowFloor") != 0.2:
        raise CandidateError("R22_RESERVE_VALUE_MISMATCH")

    validation = manifest["validation"]
    required_true = {
        "sourceDiffIsDocumentationOnly", "requestReservationsRetained",
        "terminalReservationsRetained", "strictSingleFlightRetained",
        "exactModelEffortRoleReviewQualityFunctionalityRetained",
    }
    if any(validation.get(key) is not True for key in required_true):
        raise CandidateError("VALIDATION_RETENTION_INVALID")
    if any(validation.get(key) is not False for key in {"providerInvocation", "deployment", "runtimeMutation"}):
        raise CandidateError("VALIDATION_AUTHORITY_INVALID")
    if validation.get("canonicalAdoptionLedger") != "PASS_0_ADOPT_5_DISTINGUISH_4_STALE":
        raise CandidateError("VALIDATION_LEDGER_INVALID")
    if validation.get("completeProjectResponseCensus") != "PASS_9_OF_9":
        raise CandidateError("VALIDATION_CENSUS_INVALID")
    if any(validation.get(key) != "REQUIRED" for key in {"independentReview", "distinctAdjudication"}):
        raise CandidateError("VALIDATION_REVIEW_GATE_INVALID")
    if validation.get("hostedWorkflow") != "REQUIRED_BEFORE_ADJUDICATION":
        raise CandidateError("VALIDATION_HOSTED_GATE_INVALID")

    recusal = manifest["authorRecusal"]
    _exact_keys(recusal, {"review", "adjudication", "merge", "activation"}, "RECUSAL_SHAPE_INVALID")
    if any(value is not True for value in recusal.values()):
        raise CandidateError("RECUSAL_INVALID")
    authority = manifest["authority"]
    if not isinstance(authority, dict) or not authority or any(value is not False for value in authority.values()):
        raise CandidateError("AUTHORITY_INVALID")

    return (
        "PASS: zero-reserve R2 binds source " + commit[:12]
        + ", 6 exact Git blobs, 9/9 projects, 0% reserve, and a hard 100% ceiling with zero authority"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    try:
        print(verify(args.root.resolve(), args.manifest.resolve()))
        return 0
    except (CandidateError, OSError, KeyError, TypeError) as exc:
        print(f"ZERO_RESERVE_CANDIDATE_INVALID: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
