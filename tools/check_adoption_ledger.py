#!/usr/bin/env python3
"""Fail closed unless the R26 adoption ledger matches project-owned Git evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = "adoption/universal-token-control-r26.json"
SCHEMA = "fleet-universal-token-adoption-ledger/v1"
EXPECTED_CANDIDATE = "e70a044f31dd2f43ab7c716d63a4eb89318c61b6"
EXPECTED_MERGE = "909f769d02e8412e51e28e242cfa8d00dadc9a3d"
EXPECTED_MERGE_PARENTS = [
    "c1529bc3030c6663e0be63c4789b07530b9b2ecc",
    EXPECTED_CANDIDATE,
]
EXPECTED_MANIFEST = "manifests/universal-provider-control-reconciliation-r26.json"
EXPECTED_MANIFEST_STATUS = "CANDIDATE_ZERO_AUTHORITY"
EXPECTED_STALE_SUBJECT = "874605e43531c9aa230ee16851f8107a8e0d9cec"
NON_PROJECT_SPECS = {
    "specs/fleet-provider-capacity-governor.md",
    "specs/fleet-universal-provider-control-reconciliation.md",
    "specs/provider-model-benchmarking.md",
}
FINAL_DISPOSITIONS = {"ADOPT", "DISTINGUISH", "REJECT"}
LEDGER_STATUSES = FINAL_DISPOSITIONS | {"STALE", "MISSING"}
NON_REGRESSION_DIMENSIONS = [
    "model",
    "effort",
    "role",
    "review",
    "quality",
    "functionality",
]
NON_REGRESSION_CLAIMS = {
    "model": "EXACT_MODEL_PRESERVED",
    "effort": "EXACT_EFFORT_PRESERVED",
    "role": "EXACT_ROLE_PRESERVED",
    "review": "EXACT_REVIEW_PRESERVED",
    "quality": "QUALITY_NON_INFERIOR",
    "functionality": "FUNCTIONALITY_EQUIVALENT",
}
NON_REGRESSION_RULE = (
    "TOKEN_SAVINGS_MUST_NOT_REGRESS_EXACT_MODEL_EFFORT_ROLE_REVIEW_QUALITY_OR_FUNCTIONALITY"
)
STATUS_BLOCKERS = {
    "ADOPT": None,
    "DISTINGUISH": "PROJECT_OWNER_DISTINCTION_OPEN",
    "REJECT": "FLEET_RECONCILIATION_REQUIRED",
    "STALE": "PROJECT_OWNER_CURRENT_CANDIDATE_DISPOSITION_REQUIRED",
    "MISSING": "PROJECT_OWNER_DISPOSITION_REQUIRED",
}
SHA_PATTERN = re.compile(r"[0-9a-f]{40,64}")
SHA256_PATTERN = re.compile(r"sha256:[0-9a-f]{64}")
DISPOSITION_PATTERN = re.compile(
    rb"\b(ADOPT|DISTINGUISH|REJECT)\s*\(\s*`?([0-9a-f]{40,64})`?",
    re.IGNORECASE,
)


class LedgerError(ValueError):
    pass


def _pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in values:
        if key in result:
            raise LedgerError("DUPLICATE_KEY")
        result[key] = value
    return result


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
        raise LedgerError(error)
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
        raise LedgerError("GIT_BLOB_OID_INVALID")
    return value


def _commit_tuple(commit: str) -> tuple[str, list[str]]:
    value = _git(
        ["show", "-s", "--format=%T%n%P", commit],
        text=True,
        error="COMMIT_UNAVAILABLE",
    )
    lines = value.splitlines()
    if len(lines) != 2 or SHA_PATTERN.fullmatch(lines[0]) is None:
        raise LedgerError("COMMIT_INVALID")
    parents = lines[1].split() if lines[1] else []
    if any(SHA_PATTERN.fullmatch(parent) is None for parent in parents):
        raise LedgerError("COMMIT_INVALID")
    return lines[0], parents


def _is_ancestor(ancestor: str, descendant: str) -> bool:
    run = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    return run.returncode == 0


def _tracked_specs(treeish: str) -> set[str]:
    args = (
        ["ls-files", "--cached", "--", "specs"]
        if treeish == ":"
        else ["ls-tree", "-r", "--name-only", treeish, "--", "specs"]
    )
    output = _git(args, text=True, error="SPEC_CENSUS_UNAVAILABLE")
    return {
        path
        for path in output.splitlines()
        if path.startswith("specs/") and path.endswith(".md") and "/" not in path[6:]
    }


def _last_path_commit(treeish: str, path: str) -> str:
    output = _git(
        ["log", "-1", "--format=%H", treeish, "--", path],
        text=True,
        error="PROJECT_EVIDENCE_HISTORY_UNAVAILABLE",
    ).strip()
    if SHA_PATTERN.fullmatch(output) is None:
        raise LedgerError("PROJECT_EVIDENCE_HISTORY_INVALID")
    return output


def _require_exact_keys(value: Any, keys: set[str], code: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise LedgerError(code)
    return value


def _require_sha(value: Any, code: str) -> str:
    if not isinstance(value, str) or SHA_PATTERN.fullmatch(value) is None:
        raise LedgerError(code)
    return value


def _dispositions(blob: bytes) -> set[tuple[str, str]]:
    return {
        (match.group(1).decode("ascii").upper(), match.group(2).decode("ascii").lower())
        for match in DISPOSITION_PATTERN.finditer(blob)
    }


def load_ledger(raw: bytes) -> dict[str, Any]:
    try:
        ledger = json.loads(raw, object_pairs_hook=_pairs)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise LedgerError("LEDGER_JSON_INVALID") from exc
    if not isinstance(ledger, dict):
        raise LedgerError("LEDGER_ROOT_INVALID")
    return ledger


def _verify_candidate(candidate: Any) -> None:
    candidate = _require_exact_keys(
        candidate,
        {
            "candidateCommit",
            "candidateTree",
            "mergeCommit",
            "mergeTree",
            "mergeParents",
            "manifest",
            "authorityClaims",
        },
        "CANDIDATE_RECORD_INVALID",
    )
    if candidate["candidateCommit"] != EXPECTED_CANDIDATE:
        raise LedgerError("CANDIDATE_COMMIT_MISMATCH")
    if candidate["mergeCommit"] != EXPECTED_MERGE:
        raise LedgerError("MERGE_COMMIT_MISMATCH")
    if candidate["mergeParents"] != EXPECTED_MERGE_PARENTS:
        raise LedgerError("MERGE_PARENT_CLAIM_MISMATCH")

    candidate_tree, candidate_parents = _commit_tuple(EXPECTED_CANDIDATE)
    merge_tree, merge_parents = _commit_tuple(EXPECTED_MERGE)
    if candidate["candidateTree"] != candidate_tree:
        raise LedgerError("CANDIDATE_TREE_MISMATCH")
    if candidate["mergeTree"] != merge_tree or merge_parents != EXPECTED_MERGE_PARENTS:
        raise LedgerError("MERGE_OBJECT_MISMATCH")
    if candidate_tree != merge_tree:
        raise LedgerError("MERGE_NOT_EXACT_CANDIDATE_TREE")
    if len(candidate_parents) != 1:
        raise LedgerError("CANDIDATE_HISTORY_INVALID")

    manifest_record = _require_exact_keys(
        candidate["manifest"],
        {"path", "gitBlobOid", "status"},
        "MANIFEST_RECORD_INVALID",
    )
    if manifest_record["path"] != EXPECTED_MANIFEST:
        raise LedgerError("MANIFEST_PATH_MISMATCH")
    if manifest_record["gitBlobOid"] != _oid(EXPECTED_CANDIDATE, EXPECTED_MANIFEST):
        raise LedgerError("MANIFEST_BLOB_MISMATCH")
    if _oid(EXPECTED_MERGE, EXPECTED_MANIFEST) != manifest_record["gitBlobOid"]:
        raise LedgerError("MERGED_MANIFEST_BLOB_MISMATCH")
    manifest = load_ledger(_blob(EXPECTED_CANDIDATE, EXPECTED_MANIFEST))
    if manifest.get("status") != EXPECTED_MANIFEST_STATUS:
        raise LedgerError("MANIFEST_NOT_ZERO_AUTHORITY")
    if manifest_record["status"] != EXPECTED_MANIFEST_STATUS:
        raise LedgerError("MANIFEST_STATUS_CLAIM_MISMATCH")
    authority = manifest.get("authority")
    validation = manifest.get("validation")
    if not isinstance(authority, dict) or not isinstance(validation, dict):
        raise LedgerError("MANIFEST_AUTHORITY_INVALID")
    expected_manifest_authority = {
        "providerExecution": False,
        "processSpawnResumeKill": False,
        "containmentOrCanaryCredit": False,
        "automaticGateState": "CLOSED",
        "referenceExecutionBoundary": "NOT_INSTALLED",
        "directInvocationImpossible": False,
        "activationRequiresSeparateAdjudication": True,
    }
    if authority != expected_manifest_authority:
        raise LedgerError("MANIFEST_AUTHORITY_DRIFT")
    hosted = validation.get("hosted")
    if not isinstance(hosted, dict) or hosted.get("claimedGreen") is not False:
        raise LedgerError("HOSTED_GREEN_IMPROPERLY_CLAIMED")
    authority_claims = _require_exact_keys(
        candidate["authorityClaims"],
        {
            "doctrinePublicationIsProjectAdoption",
            "doctrinePublicationIsFleetAdoption",
            "runtimeAuthority",
            "activationAuthority",
            "hostedGreenClaimed",
        },
        "AUTHORITY_CLAIMS_INVALID",
    )
    if any(value is not False for value in authority_claims.values()):
        raise LedgerError("ZERO_AUTHORITY_OVERCLAIM")


def _verify_non_regression(non_regression: Any) -> None:
    non_regression = _require_exact_keys(
        non_regression,
        {"rule", "requiredDimensions"},
        "NON_REGRESSION_RECORD_INVALID",
    )
    if non_regression["rule"] != NON_REGRESSION_RULE:
        raise LedgerError("NON_REGRESSION_RULE_MISMATCH")
    if non_regression["requiredDimensions"] != NON_REGRESSION_DIMENSIONS:
        raise LedgerError("NON_REGRESSION_DIMENSIONS_MISMATCH")


def _adopt_non_regression_anchor(dimension: str, claim: str, receipt_sha256: str) -> str:
    return (
        "R26_NON_REGRESSION_EVIDENCE["
        f"dimension={dimension};claim={claim};receiptSha256={receipt_sha256}]"
    )


def _verify_adopt_non_regression(non_regression_evidence: Any, evidence_bytes: bytes) -> None:
    non_regression_evidence = _require_exact_keys(
        non_regression_evidence,
        set(NON_REGRESSION_DIMENSIONS),
        "ADOPT_NON_REGRESSION_EVIDENCE_INVALID",
    )
    for dimension in NON_REGRESSION_DIMENSIONS:
        record = _require_exact_keys(
            non_regression_evidence[dimension],
            {"claim", "receiptSha256", "anchor"},
            "ADOPT_NON_REGRESSION_EVIDENCE_INVALID",
        )
        claim = record["claim"]
        receipt_sha256 = record["receiptSha256"]
        anchor = record["anchor"]
        if claim != NON_REGRESSION_CLAIMS[dimension]:
            raise LedgerError("ADOPT_NON_REGRESSION_EVIDENCE_INVALID")
        if not isinstance(receipt_sha256, str) or SHA256_PATTERN.fullmatch(receipt_sha256) is None:
            raise LedgerError("ADOPT_NON_REGRESSION_EVIDENCE_INVALID")
        expected_anchor = _adopt_non_regression_anchor(dimension, claim, receipt_sha256)
        if anchor != expected_anchor:
            raise LedgerError("ADOPT_NON_REGRESSION_EVIDENCE_INVALID")
        if expected_anchor.encode("ascii") not in evidence_bytes:
            raise LedgerError("ADOPT_NON_REGRESSION_EVIDENCE_MISSING")


def _verify_project(
    project: Any,
    *,
    base_commit: str,
    treeish: str,
) -> tuple[str, str]:
    project = _require_exact_keys(
        project,
        {
            "projectId",
            "specPath",
            "status",
            "evidence",
            "nonRegressionEvidence",
            "blocker",
        },
        "PROJECT_RECORD_INVALID",
    )
    project_id = project["projectId"]
    path = project["specPath"]
    status = project["status"]
    if not isinstance(project_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", project_id):
        raise LedgerError("PROJECT_ID_INVALID")
    if path != f"specs/{project_id}.md":
        raise LedgerError("PROJECT_PATH_INVALID")
    if status not in LEDGER_STATUSES:
        raise LedgerError("PROJECT_STATUS_INVALID")
    if project["blocker"] != STATUS_BLOCKERS[status]:
        raise LedgerError("PROJECT_BLOCKER_INVALID")

    evidence = _require_exact_keys(
        project["evidence"],
        {"commit", "gitBlobOid", "disposition"},
        "PROJECT_EVIDENCE_INVALID",
    )
    evidence_commit = _require_sha(evidence["commit"], "PROJECT_EVIDENCE_COMMIT_INVALID")
    evidence_blob_oid = _require_sha(evidence["gitBlobOid"], "PROJECT_EVIDENCE_BLOB_INVALID")
    if not _is_ancestor(evidence_commit, base_commit):
        raise LedgerError("PROJECT_EVIDENCE_NOT_ANCESTOR")
    if _last_path_commit(base_commit, path) != evidence_commit:
        raise LedgerError("PROJECT_EVIDENCE_NOT_LATEST_AT_CENSUS")
    if _oid(evidence_commit, path) != evidence_blob_oid:
        raise LedgerError("PROJECT_EVIDENCE_COMMIT_BLOB_MISMATCH")
    if _oid(base_commit, path) != evidence_blob_oid or _oid(treeish, path) != evidence_blob_oid:
        raise LedgerError("PROJECT_SPEC_DRIFT")
    evidence_bytes = _blob(evidence_commit, path)
    markers = _dispositions(evidence_bytes)
    current_markers = {
        marker for marker in markers if marker[1] in {EXPECTED_CANDIDATE, EXPECTED_MERGE}
    }

    disposition = evidence["disposition"]
    if status == "MISSING":
        if disposition is not None or markers:
            raise LedgerError("MISSING_STATUS_HAS_DISPOSITION_EVIDENCE")
    else:
        disposition = _require_exact_keys(
            disposition,
            {"status", "subjectCommit"},
            "DISPOSITION_EVIDENCE_INVALID",
        )
        disposition_status = disposition["status"]
        disposition_subject = _require_sha(
            disposition["subjectCommit"], "DISPOSITION_SUBJECT_INVALID"
        )
        if disposition_status not in FINAL_DISPOSITIONS:
            raise LedgerError("DISPOSITION_STATUS_INVALID")
        marker = (disposition_status, disposition_subject)
        if marker not in markers:
            raise LedgerError("DISPOSITION_NOT_IN_PROJECT_EVIDENCE")
        if status == "STALE":
            if disposition_subject != EXPECTED_STALE_SUBJECT:
                raise LedgerError("STALE_DISPOSITION_SUBJECT_INVALID")
            if current_markers:
                raise LedgerError("STALE_STATUS_HAS_CURRENT_DISPOSITION")
        else:
            if disposition_status != status:
                raise LedgerError("CURRENT_DISPOSITION_STATUS_MISMATCH")
            if disposition_subject not in {EXPECTED_CANDIDATE, EXPECTED_MERGE}:
                raise LedgerError("CURRENT_DISPOSITION_SUBJECT_MISMATCH")
            if current_markers != {marker}:
                raise LedgerError("CURRENT_DISPOSITION_CONFLICT")
            if EXPECTED_CANDIDATE.encode("ascii") not in evidence_bytes:
                raise LedgerError("CURRENT_DISPOSITION_CANDIDATE_BINDING_MISSING")
            if EXPECTED_MERGE.encode("ascii") not in evidence_bytes:
                raise LedgerError("CURRENT_DISPOSITION_MERGE_BINDING_MISSING")

    non_regression_evidence = project["nonRegressionEvidence"]
    if status != "ADOPT":
        if non_regression_evidence is not None:
            raise LedgerError("NON_ADOPT_HAS_ADOPTION_CREDIT")
    else:
        _verify_adopt_non_regression(non_regression_evidence, evidence_bytes)
    return path, status


def verify_ledger(ledger: dict[str, Any], treeish: str = "HEAD") -> None:
    ledger = _require_exact_keys(
        ledger,
        {"schema", "candidate", "census", "nonRegression", "summary", "projects"},
        "LEDGER_FIELDS_INVALID",
    )
    if ledger["schema"] != SCHEMA:
        raise LedgerError("LEDGER_SCHEMA_INVALID")
    _verify_candidate(ledger["candidate"])
    _verify_non_regression(ledger["nonRegression"])

    census = _require_exact_keys(
        ledger["census"],
        {"baseCommit", "projectSpecGlob", "nonProjectSpecs"},
        "CENSUS_RECORD_INVALID",
    )
    base_commit = _require_sha(census["baseCommit"], "CENSUS_BASE_INVALID")
    if census["projectSpecGlob"] != "specs/*.md":
        raise LedgerError("CENSUS_GLOB_INVALID")
    if census["nonProjectSpecs"] != sorted(NON_PROJECT_SPECS):
        raise LedgerError("NON_PROJECT_SPEC_SET_INVALID")
    descendant = "HEAD" if treeish == ":" else treeish
    if not _is_ancestor(EXPECTED_MERGE, base_commit) or not _is_ancestor(base_commit, descendant):
        raise LedgerError("CENSUS_BASE_HISTORY_INVALID")

    projects = ledger["projects"]
    if not isinstance(projects, list) or not projects:
        raise LedgerError("PROJECTS_INVALID")
    paths: list[str] = []
    statuses: list[str] = []
    ids: list[str] = []
    for project in projects:
        path, status = _verify_project(project, base_commit=base_commit, treeish=treeish)
        paths.append(path)
        statuses.append(status)
        ids.append(project["projectId"])
    if ids != sorted(ids) or len(ids) != len(set(ids)) or len(paths) != len(set(paths)):
        raise LedgerError("PROJECT_ORDER_OR_DUPLICATE_INVALID")

    tracked_specs = _tracked_specs(treeish)
    if not NON_PROJECT_SPECS.issubset(tracked_specs):
        raise LedgerError("REQUIRED_NON_PROJECT_SPEC_MISSING")
    if set(paths) != tracked_specs - NON_PROJECT_SPECS:
        raise LedgerError("PROJECT_CLOSED_SET_MISMATCH")

    counts = {status: statuses.count(status) for status in sorted(LEDGER_STATUSES)}
    summary = _require_exact_keys(
        ledger["summary"],
        {"projectCount", "counts", "fleetStatus", "fleetAdoptionClaim"},
        "SUMMARY_INVALID",
    )
    if summary["projectCount"] != len(projects) or summary["counts"] != counts:
        raise LedgerError("SUMMARY_COUNT_MISMATCH")
    if summary["fleetStatus"] != "NO_FLEET_ADOPTION" or summary["fleetAdoptionClaim"] is not False:
        raise LedgerError("FLEET_ADOPTION_OVERCLAIM")
    if counts["ADOPT"] == len(projects):
        raise LedgerError("ZERO_AUTHORITY_CANDIDATE_CANNOT_CLAIM_FLEET_ADOPTION")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--treeish", default="HEAD")
    args = parser.parse_args(argv)
    try:
        ledger = load_ledger(_blob(args.treeish, LEDGER_PATH))
        verify_ledger(ledger, args.treeish)
    except LedgerError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(
        "PASS: R26 adoption ledger matches the closed project-spec set and pinned project-owned evidence"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
