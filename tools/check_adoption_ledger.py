#!/usr/bin/env python3
"""Fail closed unless the R26 adoption ledger matches project-owned Git evidence."""

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
PROJECT_CANDIDATE_IDS = {"cloudvore", "mlv-app", "salesforce-tools"}
PROJECT_CANDIDATE_STATUSES = {
    "cloudvore": "CANDIDATE_ZERO_AUTHORITY",
    "mlv-app": "CANDIDATE_ZERO_AUTHORITY",
    "salesforce-tools": "DISTINGUISH_CANDIDATE_ZERO_AUTHORITY",
}
EXPECTED_PROJECT_CANDIDATE_SHA256 = {
    "cloudvore": "7bbafaa69078bf3464f5e54c6f1e0a689113c54ce7df7f494d017beef58be436",
    "mlv-app": "55544254f982890efa8b2e309b0eeb2be09f85d7f09f7da86083ba2856cbf9ba",
    "salesforce-tools": "b2278e858cf70c0a6eecca6d7842709e9cc6fe4598fa13af6bf64929c05b0f6f",
}
PROJECT_CANDIDATE_AUTHORITY_FIELDS = {
    "projectAdoption",
    "fleetAdoption",
    "runtimeActivation",
    "providerInvocation",
    "schedulerMutation",
    "mergePushRelease",
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
ADOPT_RECEIPT_SCHEMA = "fleet-project-r26-non-regression-receipt/v1"
ADOPT_PROFILE_SCHEMA = "fleet-project-r26-adoption-profile/v1"
ADOPT_REVIEW_SCHEMA = "fleet-project-r26-review-receipt/v1"
ADOPT_PROOF_SCHEMA = "fleet-project-r26-adoption-proof/v1"
ADOPT_RECEIPT_PREFIX = "receipts/project-adoption"
MAX_ADOPT_RECEIPT_BYTES = 65_536
MAX_ADOPT_SUBJECT_BYTES = 1_048_576
ADOPT_PROOF_KINDS = {
    "supervisorAdapter",
    "launcherCensus",
    "fakeProviderControls",
    "concurrencyControls",
    "idleTicks",
    "fullChildFencing",
    "rollback",
    "closedGate",
}
ADOPT_REQUIRED_CONTROL_CASES = {
    "fakeProviderControls": [
        "fake-provider-no-network",
        "no-work-zero-inference",
        "quota-refusal-zero-inference",
    ],
    "concurrencyControls": [
        "concurrent-claim-refused",
        "full-child-lifetime-held",
        "single-quota-owner",
    ],
    "fullChildFencing": [
        "descendant-inventory-complete",
        "kill-entire-tree",
        "post-termination-zero-live-children",
    ],
}
ADOPT_REQUIRED_ROLLBACK_STEPS = [
    "close-gate",
    "terminate-full-child-tree",
    "restore-prior-profile",
    "verify-zero-live-children",
]
STATUS_BLOCKERS = {
    "ADOPT": None,
    "DISTINGUISH": "PROJECT_OWNER_DISTINCTION_OPEN",
    "REJECT": "FLEET_RECONCILIATION_REQUIRED",
    "STALE": "PROJECT_OWNER_CURRENT_CANDIDATE_DISPOSITION_REQUIRED",
    "MISSING": "PROJECT_OWNER_DISPOSITION_REQUIRED",
}
SHA_PATTERN = re.compile(r"[0-9a-f]{40,64}")
SHA256_PATTERN = re.compile(r"sha256:[0-9a-f]{64}")
RAW_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
FORMAL_ADOPT_PATTERN = re.compile(r"\bADOPT\s*\(", re.IGNORECASE)
DISPOSITION_PATTERN = re.compile(
    rb"\b(DISTINGUISH|REJECT)\s*\(\s*`?([0-9a-f]{40,64})`?",
    re.IGNORECASE,
)
ADOPT_DISPOSITION_PATTERN = re.compile(
    rb"ADOPT\(([0-9a-f]{40}), (sha256:[0-9a-f]{64}), (sha256:[0-9a-f]{64})\)"
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


def _blob_size(treeish: str, path: str, *, error: str = "GIT_BLOB_SIZE_UNAVAILABLE") -> int:
    value = _git(
        ["cat-file", "-s", _blob_spec(treeish, path)],
        text=True,
        error=error,
    ).strip()
    try:
        size = int(value)
    except ValueError as exc:
        raise LedgerError(error) from exc
    if size < 0:
        raise LedgerError(error)
    return size


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


def _contains_formal_adopt(value: Any) -> bool:
    if isinstance(value, str):
        return FORMAL_ADOPT_PATTERN.search(value) is not None
    if isinstance(value, dict):
        return any(
            _contains_formal_adopt(key) or _contains_formal_adopt(member)
            for key, member in value.items()
        )
    if isinstance(value, list):
        return any(_contains_formal_adopt(member) for member in value)
    return False


def _verify_project_candidate(candidate: Any, *, project_id: str, spec_bytes: bytes) -> None:
    candidate = _require_exact_keys(
        candidate,
        {
            "remote",
            "publishedRef",
            "commit",
            "tree",
            "parent",
            "baseCommit",
            "candidateStatus",
            "primaryEvidencePath",
            "dispositionPath",
            "artifacts",
            "disposition",
            "authorityClaims",
            "adoptionProofCredit",
            "nonRegressionCredit",
        },
        "PROJECT_CANDIDATE_INVALID",
    )
    if _contains_formal_adopt(candidate):
        raise LedgerError("PROJECT_CANDIDATE_ADOPT_OVERCLAIM")
    if (
        not isinstance(candidate["remote"], str)
        or re.fullmatch(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\.git", candidate["remote"])
        is None
        or candidate["publishedRef"]
        != "refs/heads/codex/r26-zero-authority-disposition-candidate-20260819"
    ):
        raise LedgerError("PROJECT_CANDIDATE_PUBLICATION_INVALID")
    for key in ("commit", "tree", "parent", "baseCommit"):
        _require_sha(candidate[key], "PROJECT_CANDIDATE_OBJECT_INVALID")
    if candidate["candidateStatus"] != PROJECT_CANDIDATE_STATUSES[project_id]:
        raise LedgerError("PROJECT_CANDIDATE_STATUS_INVALID")

    artifacts = candidate["artifacts"]
    if not isinstance(artifacts, list) or len(artifacts) < 2:
        raise LedgerError("PROJECT_CANDIDATE_ARTIFACTS_INVALID")
    paths: list[str] = []
    for artifact in artifacts:
        artifact = _require_exact_keys(
            artifact,
            {"path", "gitBlobOid", "bytes", "sha256"},
            "PROJECT_CANDIDATE_ARTIFACT_INVALID",
        )
        path = artifact["path"]
        if (
            not isinstance(path, str)
            or not path
            or path.startswith(("/", "\\"))
            or ".." in Path(path).parts
            or not isinstance(artifact["bytes"], int)
            or isinstance(artifact["bytes"], bool)
            or artifact["bytes"] <= 0
        ):
            raise LedgerError("PROJECT_CANDIDATE_ARTIFACT_INVALID")
        _require_sha(artifact["gitBlobOid"], "PROJECT_CANDIDATE_ARTIFACT_BLOB_INVALID")
        if (
            not isinstance(artifact["sha256"], str)
            or RAW_SHA256_PATTERN.fullmatch(artifact["sha256"]) is None
        ):
            raise LedgerError("PROJECT_CANDIDATE_ARTIFACT_SHA256_INVALID")
        exact_row = (
            f"| `{path}` | `{artifact['gitBlobOid']}` | "
            f"{artifact['bytes']:,} | `{artifact['sha256']}` |"
        ).encode("utf-8")
        if exact_row not in spec_bytes:
            raise LedgerError("PROJECT_CANDIDATE_ARTIFACT_NOT_IN_SPEC")
        paths.append(path)
    if len(paths) != len(set(paths)):
        raise LedgerError("PROJECT_CANDIDATE_ARTIFACT_DUPLICATE")
    if candidate["primaryEvidencePath"] not in paths or candidate["dispositionPath"] not in paths:
        raise LedgerError("PROJECT_CANDIDATE_PRIMARY_ARTIFACT_MISSING")

    disposition = _require_exact_keys(
        candidate["disposition"],
        {"kind", "subjectCommit", "statement"},
        "PROJECT_CANDIDATE_DISPOSITION_INVALID",
    )
    if (
        disposition["kind"] != "DISTINGUISH"
        or disposition["subjectCommit"] != EXPECTED_MERGE
        or not isinstance(disposition["statement"], str)
        or not disposition["statement"].startswith(f"DISTINGUISH({EXPECTED_MERGE}, ")
        or spec_bytes.count(disposition["statement"].encode("utf-8")) != 1
    ):
        raise LedgerError("PROJECT_CANDIDATE_DISPOSITION_INVALID")

    authority = _require_exact_keys(
        candidate["authorityClaims"],
        PROJECT_CANDIDATE_AUTHORITY_FIELDS,
        "PROJECT_CANDIDATE_AUTHORITY_INVALID",
    )
    if any(value is not False for value in authority.values()):
        raise LedgerError("PROJECT_CANDIDATE_AUTHORITY_OVERCLAIM")
    if candidate["adoptionProofCredit"] is not False or candidate["nonRegressionCredit"] is not False:
        raise LedgerError("PROJECT_CANDIDATE_PROOF_OVERCLAIM")

    canonical_sha256 = hashlib.sha256(
        json.dumps(
            candidate,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()
    if canonical_sha256 != EXPECTED_PROJECT_CANDIDATE_SHA256[project_id]:
        raise LedgerError("PROJECT_CANDIDATE_EXACT_BINDING_MISMATCH")

    scalar_tokens = [
        candidate["remote"],
        candidate["publishedRef"],
        candidate["commit"],
        candidate["tree"],
        candidate["parent"],
        candidate["baseCommit"],
        candidate["candidateStatus"],
        candidate["primaryEvidencePath"],
        candidate["dispositionPath"],
    ]
    if any(token.encode("utf-8") not in spec_bytes for token in scalar_tokens):
        raise LedgerError("PROJECT_CANDIDATE_BINDING_NOT_IN_SPEC")


def _dispositions(blob: bytes) -> set[tuple[str, str]]:
    dispositions = {
        (match.group(1).decode("ascii").upper(), match.group(2).decode("ascii").lower())
        for match in DISPOSITION_PATTERN.finditer(blob)
    }
    for line in blob.splitlines():
        match = ADOPT_DISPOSITION_PATTERN.fullmatch(line)
        if match is not None:
            dispositions.add(("ADOPT", match.group(1).decode("ascii")))
    return dispositions


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
    if set(authority) != set(expected_manifest_authority):
        raise LedgerError("MANIFEST_AUTHORITY_DRIFT")
    for field, expected in expected_manifest_authority.items():
        actual = authority[field]
        if isinstance(expected, bool):
            if actual is not expected:
                raise LedgerError("MANIFEST_AUTHORITY_DRIFT")
        elif actual != expected:
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


def _adopt_non_regression_anchor(
    dimension: str,
    claim: str,
    receipt_path: str,
    receipt_sha256: str,
) -> str:
    return (
        "R26_NON_REGRESSION_EVIDENCE["
        f"dimension={dimension};claim={claim};receiptPath={receipt_path};"
        f"receiptSha256={receipt_sha256}]"
    )


def _verified_project_artifact(
    artifact_ref: Any,
    *,
    project_id: str,
    evidence_commit: str,
    base_commit: str,
    treeish: str,
    cache: dict[str, tuple[bytes, str]],
    code_prefix: str = "ADOPT_ARTIFACT",
    json_only: bool = True,
    max_bytes: int = MAX_ADOPT_RECEIPT_BYTES,
) -> tuple[bytes, str, str]:
    artifact_ref = _require_exact_keys(
        artifact_ref,
        {"path", "sha256"},
        f"{code_prefix}_REFERENCE_INVALID",
    )
    path = artifact_ref["path"]
    claimed_sha256 = artifact_ref["sha256"]
    expected_prefix = f"{ADOPT_RECEIPT_PREFIX}/{project_id}/"
    suffix_pattern = (
        r"[a-z0-9][a-z0-9._-]{0,127}\.json"
        if json_only
        else r"[a-z0-9][a-z0-9._-]{0,127}"
    )
    if (
        not isinstance(path, str)
        or len(path) > 220
        or re.fullmatch(rf"{re.escape(expected_prefix)}{suffix_pattern}", path) is None
    ):
        raise LedgerError(f"{code_prefix}_PATH_INVALID")
    if not isinstance(claimed_sha256, str) or SHA256_PATTERN.fullmatch(claimed_sha256) is None:
        raise LedgerError(f"{code_prefix}_REFERENCE_INVALID")

    if path not in cache:
        try:
            last_commit = _last_path_commit(base_commit, path)
        except LedgerError as exc:
            raise LedgerError(f"{code_prefix}_UNAVAILABLE") from exc
        if last_commit != evidence_commit:
            raise LedgerError(f"{code_prefix}_COMMIT_MISMATCH")
        try:
            size = _blob_size(evidence_commit, path, error=f"{code_prefix}_UNAVAILABLE")
        except LedgerError as exc:
            raise LedgerError(f"{code_prefix}_UNAVAILABLE") from exc
        if size <= 0 or size > max_bytes:
            raise LedgerError(f"{code_prefix}_SIZE_INVALID")
        try:
            artifact_bytes = _blob(evidence_commit, path)
            base_bytes = _blob(base_commit, path)
            current_bytes = _blob(treeish, path)
        except LedgerError as exc:
            raise LedgerError(f"{code_prefix}_UNAVAILABLE") from exc
        if (
            len(artifact_bytes) != size
            or base_bytes != artifact_bytes
            or current_bytes != artifact_bytes
        ):
            raise LedgerError(f"{code_prefix}_DRIFT")
        computed_sha256 = f"sha256:{hashlib.sha256(artifact_bytes).hexdigest()}"
        cache[path] = (artifact_bytes, computed_sha256)
    artifact_bytes, computed_sha256 = cache[path]
    if claimed_sha256 != computed_sha256:
        raise LedgerError(f"{code_prefix}_SHA256_MISMATCH")
    return artifact_bytes, path, computed_sha256


def _load_adopt_json(raw: bytes, code: str) -> dict[str, Any]:
    try:
        return load_ledger(raw)
    except LedgerError as exc:
        raise LedgerError(code) from exc


def _verify_adopt_profile(
    profile_bytes: bytes,
    *,
    project_id: str,
) -> None:
    profile = _require_exact_keys(
        _load_adopt_json(profile_bytes, "ADOPT_PROFILE_INVALID"),
        {
            "schema",
            "projectId",
            "candidateCommit",
            "mergeCommit",
            "canonicalCommit",
            "model",
            "effort",
            "role",
            "review",
            "quality",
            "functionality",
        },
        "ADOPT_PROFILE_INVALID",
    )
    if (
        profile["schema"] != ADOPT_PROFILE_SCHEMA
        or profile["projectId"] != project_id
        or profile["candidateCommit"] != EXPECTED_CANDIDATE
        or profile["mergeCommit"] != EXPECTED_MERGE
        or profile["canonicalCommit"] != EXPECTED_MERGE
    ):
        raise LedgerError("ADOPT_PROFILE_BINDING_INVALID")
    for field in ("model", "effort", "role", "review", "quality", "functionality"):
        if not isinstance(profile[field], str) or not profile[field].strip():
            raise LedgerError("ADOPT_PROFILE_INVALID")


def _verify_adopt_review(
    review_bytes: bytes,
    *,
    project_id: str,
    profile_sha256: str,
) -> None:
    review = _require_exact_keys(
        _load_adopt_json(review_bytes, "ADOPT_REVIEW_INVALID"),
        {
            "schema",
            "projectId",
            "candidateCommit",
            "mergeCommit",
            "canonicalCommit",
            "profileSha256",
            "verdict",
            "reviews",
        },
        "ADOPT_REVIEW_INVALID",
    )
    if (
        review["schema"] != ADOPT_REVIEW_SCHEMA
        or review["projectId"] != project_id
        or review["candidateCommit"] != EXPECTED_CANDIDATE
        or review["mergeCommit"] != EXPECTED_MERGE
        or review["canonicalCommit"] != EXPECTED_MERGE
        or review["profileSha256"] != profile_sha256
        or review["verdict"] != "ACCEPT"
    ):
        raise LedgerError("ADOPT_REVIEW_BINDING_INVALID")
    reviews = review["reviews"]
    if not isinstance(reviews, list) or len(reviews) < 2:
        raise LedgerError("ADOPT_REVIEW_INVALID")
    reviewers: list[str] = []
    for item in reviews:
        item = _require_exact_keys(
            item,
            {"reviewer", "role", "verdict"},
            "ADOPT_REVIEW_INVALID",
        )
        if (
            not isinstance(item["reviewer"], str)
            or not item["reviewer"].strip()
            or not isinstance(item["role"], str)
            or not item["role"].strip()
            or item["verdict"] != "ACCEPT"
        ):
            raise LedgerError("ADOPT_REVIEW_INVALID")
        reviewers.append(item["reviewer"])
    if len(reviewers) != len(set(reviewers)):
        raise LedgerError("ADOPT_REVIEW_INVALID")


def _verify_adopt_proof(
    proof_bytes: bytes,
    *,
    kind: str,
    project_id: str,
    profile_sha256: str,
    review_sha256: str,
    evidence_commit: str,
    base_commit: str,
    treeish: str,
    cache: dict[str, tuple[bytes, str]],
) -> None:
    proof = _require_exact_keys(
        _load_adopt_json(proof_bytes, "ADOPT_PROOF_INVALID"),
        {
            "schema",
            "kind",
            "projectId",
            "candidateCommit",
            "mergeCommit",
            "canonicalCommit",
            "profileSha256",
            "reviewReceiptSha256",
            "evidence",
        },
        "ADOPT_PROOF_INVALID",
    )
    if (
        proof["schema"] != ADOPT_PROOF_SCHEMA
        or proof["kind"] != kind
        or proof["projectId"] != project_id
        or proof["candidateCommit"] != EXPECTED_CANDIDATE
        or proof["mergeCommit"] != EXPECTED_MERGE
        or proof["canonicalCommit"] != EXPECTED_MERGE
        or proof["profileSha256"] != profile_sha256
        or proof["reviewReceiptSha256"] != review_sha256
    ):
        raise LedgerError("ADOPT_PROOF_BINDING_INVALID")
    evidence = proof["evidence"]

    if kind == "supervisorAdapter":
        evidence = _require_exact_keys(
            evidence,
            {"supervisor", "adapter"},
            "ADOPT_PROOF_INVALID",
        )
        supervisor_bytes, supervisor_path, _ = _verified_project_artifact(
            evidence["supervisor"],
            project_id=project_id,
            evidence_commit=evidence_commit,
            base_commit=base_commit,
            treeish=treeish,
            cache=cache,
            json_only=False,
            max_bytes=MAX_ADOPT_SUBJECT_BYTES,
        )
        adapter_bytes, adapter_path, _ = _verified_project_artifact(
            evidence["adapter"],
            project_id=project_id,
            evidence_commit=evidence_commit,
            base_commit=base_commit,
            treeish=treeish,
            cache=cache,
            json_only=False,
            max_bytes=MAX_ADOPT_SUBJECT_BYTES,
        )
        if supervisor_path == adapter_path or not supervisor_bytes or not adapter_bytes:
            raise LedgerError("ADOPT_SUPERVISOR_ADAPTER_INVALID")
        return

    if kind == "launcherCensus":
        evidence = _require_exact_keys(
            evidence,
            {"launchers", "unresolvedLaunchers"},
            "ADOPT_PROOF_INVALID",
        )
        launchers = evidence["launchers"]
        if not isinstance(launchers, list) or not 1 <= len(launchers) <= 128:
            raise LedgerError("ADOPT_LAUNCHER_CENSUS_INVALID")
        launcher_paths: list[str] = []
        for launcher_ref in launchers:
            launcher_bytes, launcher_path, _ = _verified_project_artifact(
                launcher_ref,
                project_id=project_id,
                evidence_commit=evidence_commit,
                base_commit=base_commit,
                treeish=treeish,
                cache=cache,
                json_only=False,
                max_bytes=MAX_ADOPT_SUBJECT_BYTES,
            )
            if not launcher_bytes:
                raise LedgerError("ADOPT_LAUNCHER_CENSUS_INVALID")
            launcher_paths.append(launcher_path)
        if (
            len(launcher_paths) != len(set(launcher_paths))
            or evidence["unresolvedLaunchers"] != []
        ):
            raise LedgerError("ADOPT_LAUNCHER_CENSUS_INVALID")
        return

    if kind in {"fakeProviderControls", "concurrencyControls", "fullChildFencing"}:
        evidence = _require_exact_keys(
            evidence,
            {"cases", "passedCases", "failedCases"},
            "ADOPT_PROOF_INVALID",
        )
        if (
            evidence["cases"] != ADOPT_REQUIRED_CONTROL_CASES[kind]
            or evidence["passedCases"] != ADOPT_REQUIRED_CONTROL_CASES[kind]
            or evidence["failedCases"] != []
        ):
            raise LedgerError("ADOPT_CONTROL_PROOF_INVALID")
        return

    if kind == "idleTicks":
        evidence = _require_exact_keys(
            evidence,
            {"ticks", "inferenceCalls", "stateChanges"},
            "ADOPT_PROOF_INVALID",
        )
        if any(type(evidence[field]) is not int for field in evidence):
            raise LedgerError("ADOPT_IDLE_TICKS_INVALID")
        if (
            evidence["ticks"] != 1_000
            or evidence["inferenceCalls"] != 0
            or evidence["stateChanges"] != 0
        ):
            raise LedgerError("ADOPT_IDLE_TICKS_INVALID")
        return

    if kind == "rollback":
        evidence = _require_exact_keys(
            evidence,
            {"steps", "beforeGate", "afterGate", "residualProcesses"},
            "ADOPT_PROOF_INVALID",
        )
        if (
            evidence["steps"] != ADOPT_REQUIRED_ROLLBACK_STEPS
            or evidence["beforeGate"] != "CLOSED"
            or evidence["afterGate"] != "CLOSED"
            or type(evidence["residualProcesses"]) is not int
            or evidence["residualProcesses"] != 0
        ):
            raise LedgerError("ADOPT_ROLLBACK_PROOF_INVALID")
        return

    if kind == "closedGate":
        evidence = _require_exact_keys(
            evidence,
            {
                "state",
                "currentAtEvidenceCommit",
                "providerInvocationEnabled",
                "automaticLaunchEnabled",
            },
            "ADOPT_PROOF_INVALID",
        )
        if (
            evidence["state"] != "CLOSED"
            or evidence["currentAtEvidenceCommit"] is not True
            or evidence["providerInvocationEnabled"] is not False
            or evidence["automaticLaunchEnabled"] is not False
        ):
            raise LedgerError("ADOPT_CLOSED_GATE_INVALID")
        return

    raise LedgerError("ADOPT_PROOF_KIND_INVALID")


def _verify_adopt_receipt(
    receipt_bytes: bytes,
    *,
    project_id: str,
    profile_ref: dict[str, str],
    review_ref: dict[str, str],
    evidence_commit: str,
    base_commit: str,
    treeish: str,
    cache: dict[str, tuple[bytes, str]],
) -> None:
    receipt = _require_exact_keys(
        _load_adopt_json(receipt_bytes, "ADOPT_RECEIPT_INVALID"),
        {
            "schema",
            "projectId",
            "candidateCommit",
            "mergeCommit",
            "canonicalCommit",
            "profile",
            "reviewReceipt",
            "proofs",
            "dimensions",
        },
        "ADOPT_RECEIPT_INVALID",
    )
    if (
        receipt["schema"] != ADOPT_RECEIPT_SCHEMA
        or receipt["projectId"] != project_id
        or receipt["candidateCommit"] != EXPECTED_CANDIDATE
        or receipt["mergeCommit"] != EXPECTED_MERGE
        or receipt["canonicalCommit"] != EXPECTED_MERGE
        or receipt["profile"] != profile_ref
        or receipt["reviewReceipt"] != review_ref
    ):
        raise LedgerError("ADOPT_RECEIPT_BINDING_INVALID")
    proofs = _require_exact_keys(
        receipt["proofs"],
        ADOPT_PROOF_KINDS,
        "ADOPT_RECEIPT_INVALID",
    )
    for kind in sorted(ADOPT_PROOF_KINDS):
        proof_bytes, _, _ = _verified_project_artifact(
            proofs[kind],
            project_id=project_id,
            evidence_commit=evidence_commit,
            base_commit=base_commit,
            treeish=treeish,
            cache=cache,
        )
        _verify_adopt_proof(
            proof_bytes,
            kind=kind,
            project_id=project_id,
            profile_sha256=profile_ref["sha256"],
            review_sha256=review_ref["sha256"],
            evidence_commit=evidence_commit,
            base_commit=base_commit,
            treeish=treeish,
            cache=cache,
        )
    dimensions = _require_exact_keys(
        receipt["dimensions"],
        set(NON_REGRESSION_DIMENSIONS),
        "ADOPT_RECEIPT_INVALID",
    )
    for dimension in NON_REGRESSION_DIMENSIONS:
        result = _require_exact_keys(
            dimensions[dimension],
            {"claim", "passed"},
            "ADOPT_RECEIPT_INVALID",
        )
        if result["claim"] != NON_REGRESSION_CLAIMS[dimension] or result["passed"] is not True:
            raise LedgerError("ADOPT_RECEIPT_BINDING_INVALID")


def _verify_adopt_non_regression(
    non_regression_evidence: Any,
    evidence_bytes: bytes,
    *,
    project_id: str,
    evidence_commit: str,
    base_commit: str,
    treeish: str,
    disposition: dict[str, Any],
    artifact_cache: dict[str, tuple[bytes, str]],
) -> None:
    non_regression_evidence = _require_exact_keys(
        non_regression_evidence,
        set(NON_REGRESSION_DIMENSIONS),
        "ADOPT_NON_REGRESSION_EVIDENCE_INVALID",
    )
    try:
        evidence_lines = evidence_bytes.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise LedgerError("PROJECT_EVIDENCE_UTF8_INVALID") from exc
    profile_ref = {
        "path": disposition["profilePath"],
        "sha256": disposition["profileSha256"],
    }
    review_ref = {
        "path": disposition["reviewReceiptPath"],
        "sha256": disposition["reviewReceiptSha256"],
    }
    validated_receipts: set[str] = set()
    for dimension in NON_REGRESSION_DIMENSIONS:
        record = _require_exact_keys(
            non_regression_evidence[dimension],
            {"claim", "receiptPath", "receiptSha256", "anchor"},
            "ADOPT_NON_REGRESSION_EVIDENCE_INVALID",
        )
        claim = record["claim"]
        receipt_path = record["receiptPath"]
        receipt_sha256 = record["receiptSha256"]
        anchor = record["anchor"]
        if claim != NON_REGRESSION_CLAIMS[dimension]:
            raise LedgerError("ADOPT_NON_REGRESSION_EVIDENCE_INVALID")
        if not isinstance(receipt_sha256, str) or SHA256_PATTERN.fullmatch(receipt_sha256) is None:
            raise LedgerError("ADOPT_NON_REGRESSION_EVIDENCE_INVALID")

        receipt_bytes, verified_path, computed_sha256 = _verified_project_artifact(
            {"path": receipt_path, "sha256": receipt_sha256},
            project_id=project_id,
            evidence_commit=evidence_commit,
            base_commit=base_commit,
            treeish=treeish,
            cache=artifact_cache,
            code_prefix="ADOPT_RECEIPT",
        )
        if verified_path not in validated_receipts:
            _verify_adopt_receipt(
                receipt_bytes,
                project_id=project_id,
                profile_ref=profile_ref,
                review_ref=review_ref,
                evidence_commit=evidence_commit,
                base_commit=base_commit,
                treeish=treeish,
                cache=artifact_cache,
            )
            validated_receipts.add(verified_path)
        if receipt_sha256 != computed_sha256:
            raise LedgerError("ADOPT_RECEIPT_SHA256_MISMATCH")

        expected_anchor = _adopt_non_regression_anchor(
            dimension,
            claim,
            receipt_path,
            receipt_sha256,
        )
        if anchor != expected_anchor:
            raise LedgerError("ADOPT_NON_REGRESSION_EVIDENCE_INVALID")
        if evidence_lines.count(expected_anchor) != 1:
            raise LedgerError("ADOPT_NON_REGRESSION_EVIDENCE_MISSING")


def _adopt_disposition_line(disposition: dict[str, Any]) -> str:
    return (
        f"ADOPT({disposition['subjectCommit']}, {disposition['profileSha256']}, "
        f"{disposition['reviewReceiptSha256']})"
    )


def _verify_adopt_disposition_artifacts(
    disposition: dict[str, Any],
    *,
    project_id: str,
    evidence_commit: str,
    base_commit: str,
    treeish: str,
    cache: dict[str, tuple[bytes, str]],
) -> None:
    profile_ref = {
        "path": disposition["profilePath"],
        "sha256": disposition["profileSha256"],
    }
    review_ref = {
        "path": disposition["reviewReceiptPath"],
        "sha256": disposition["reviewReceiptSha256"],
    }
    profile_bytes, _, profile_sha256 = _verified_project_artifact(
        profile_ref,
        project_id=project_id,
        evidence_commit=evidence_commit,
        base_commit=base_commit,
        treeish=treeish,
        cache=cache,
    )
    _verify_adopt_profile(profile_bytes, project_id=project_id)
    review_bytes, _, review_sha256 = _verified_project_artifact(
        review_ref,
        project_id=project_id,
        evidence_commit=evidence_commit,
        base_commit=base_commit,
        treeish=treeish,
        cache=cache,
    )
    if profile_sha256 != disposition["profileSha256"]:
        raise LedgerError("ADOPT_PROFILE_SHA256_MISMATCH")
    if review_sha256 != disposition["reviewReceiptSha256"]:
        raise LedgerError("ADOPT_REVIEW_SHA256_MISMATCH")
    _verify_adopt_review(
        review_bytes,
        project_id=project_id,
        profile_sha256=profile_sha256,
    )


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
        {"commit", "gitBlobOid", "disposition", "projectCandidate"},
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
    project_candidate = evidence["projectCandidate"]
    if project_id in PROJECT_CANDIDATE_IDS:
        if status != "DISTINGUISH" or project_candidate is None:
            raise LedgerError("PROJECT_CANDIDATE_REQUIRED")
        _verify_project_candidate(
            project_candidate,
            project_id=project_id,
            spec_bytes=evidence_bytes,
        )
    elif project_candidate is not None:
        raise LedgerError("PROJECT_CANDIDATE_UNEXPECTED")
    markers = _dispositions(evidence_bytes)
    current_markers = {
        marker for marker in markers if marker[1] in {EXPECTED_CANDIDATE, EXPECTED_MERGE}
    }

    artifact_cache: dict[str, tuple[bytes, str]] = {}
    disposition = evidence["disposition"]
    if status == "MISSING":
        if disposition is not None or markers:
            raise LedgerError("MISSING_STATUS_HAS_DISPOSITION_EVIDENCE")
    else:
        if not isinstance(disposition, dict) or "status" not in disposition:
            raise LedgerError("DISPOSITION_EVIDENCE_INVALID")
        disposition_status = disposition["status"]
        disposition_keys = (
            {
                "status",
                "subjectCommit",
                "profilePath",
                "profileSha256",
                "reviewReceiptPath",
                "reviewReceiptSha256",
            }
            if disposition_status == "ADOPT"
            else {"status", "subjectCommit"}
        )
        disposition = _require_exact_keys(
            disposition,
            disposition_keys,
            "DISPOSITION_EVIDENCE_INVALID",
        )
        disposition_subject = _require_sha(
            disposition["subjectCommit"], "DISPOSITION_SUBJECT_INVALID"
        )
        if disposition_status not in FINAL_DISPOSITIONS:
            raise LedgerError("DISPOSITION_STATUS_INVALID")
        if disposition_status == "ADOPT":
            if disposition_subject != EXPECTED_MERGE:
                raise LedgerError("ADOPT_CANONICAL_COMMIT_INVALID")
            if (
                not isinstance(disposition["profileSha256"], str)
                or SHA256_PATTERN.fullmatch(disposition["profileSha256"]) is None
                or not isinstance(disposition["reviewReceiptSha256"], str)
                or SHA256_PATTERN.fullmatch(disposition["reviewReceiptSha256"]) is None
            ):
                raise LedgerError("ADOPT_DISPOSITION_EVIDENCE_INVALID")
            try:
                evidence_lines = evidence_bytes.decode("utf-8").splitlines()
            except UnicodeDecodeError as exc:
                raise LedgerError("PROJECT_EVIDENCE_UTF8_INVALID") from exc
            if evidence_lines.count(_adopt_disposition_line(disposition)) != 1:
                raise LedgerError("ADOPT_DISPOSITION_RECORD_INVALID")
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
            if status == "ADOPT":
                _verify_adopt_disposition_artifacts(
                    disposition,
                    project_id=project_id,
                    evidence_commit=evidence_commit,
                    base_commit=base_commit,
                    treeish=treeish,
                    cache=artifact_cache,
                )

    non_regression_evidence = project["nonRegressionEvidence"]
    if status != "ADOPT":
        if non_regression_evidence is not None:
            raise LedgerError("NON_ADOPT_HAS_ADOPTION_CREDIT")
    else:
        _verify_adopt_non_regression(
            non_regression_evidence,
            evidence_bytes,
            project_id=project_id,
            evidence_commit=evidence_commit,
            base_commit=base_commit,
            treeish=treeish,
            disposition=disposition,
            artifact_cache=artifact_cache,
        )
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
