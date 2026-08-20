#!/usr/bin/env python3
"""Verify the linear, zero-authority Phase 9 manifest-repair integration."""

from __future__ import annotations

import argparse
import ast
from collections import Counter
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PHASE5_BASE = "e4e7f9363185a5e10bb3a92167c785ef29caf2b7"
PHASE5_TREE = "5233fa0515fcef7b69e70a007f25e6bb78190c42"
PHASE5_PARENT = "5ac7036705338cfe3370f5fddda224e07d5d1bdd"
PHASE6_COMMIT = "8d97c399692e678eb4c975127c8ae1189d8dcb20"
PHASE6_TREE = "e62e063b6a55084431dd8f485f59b74c0b897be5"
PHASE6_PARENT = "6a33db0902111b823ae202f534fd1d2da554d436"
PHASE8_COMMIT = "2223647059cb789fd350883597756666357583df"
PHASE8_TREE = "062ee5311cc56b6ea50c2ce3f4e9d095847069e8"
REPAIR_PARENT = "ed8a2f359de8830c5800d1721faf183015eec01f"
REPAIR_PARENT_TREE = "7592c9e600342724a799d73eb636cf3afd34629a"
REPAIR_COMMIT = "1f3c3d8808b3d9bbb1db201039e0c3d18441f7f0"
REPAIR_TREE = "e5686f805dce19a724a94a0e76b9f0ad0f27fe23"

LEDGER_PATH = "adoption/universal-token-control-r26.json"
LEDGER_BLOB = "333cc6d47e99a857b64150a87bd9f834590256e1"
MANIFEST_PATH = "manifests/universal-provider-control-reconciliation-r26.json"
MANIFEST_BLOB = "65901748c5843f05b37e4352c5b469e47804e2f1"
MANIFEST_TEST_PATH = "tests/test_universal_manifest_spec_bindings.py"
MANIFEST_TEST_BLOB = "24078e21787220cbc3af4a3cbfbe2f36a04b6d89"
RECEIPT_PATH = "adoption/phase6/r26-local-candidate-review-receipts.json"
RECEIPT_BLOB = "c10b1b7530e0d9695118a02dd21842e4fc1493e0"
REQUEST_DIR = "adoption/phase7/requests"
REQUEST_BLOBS = {
    f"{REQUEST_DIR}/adobe-ingester.json": "893de38f19c90303c4935de47fa535f590c91b4d",
    f"{REQUEST_DIR}/agent-bridge.json": "b62bef05c4d980808478bed4b063b50751f8b0c3",
    f"{REQUEST_DIR}/airmypc.json": "7d202d0ad16d79a8ffdcd5589fd9af9422a2dbe3",
    f"{REQUEST_DIR}/conjugal.json": "1f046669b36e994e26d451fa1341e54ae624081e",
}

PHASE8_SOURCE_DELTA_PATHS = {
    ".github/workflows/disposition-intake.yml",
    "adoption/phase7/README.md",
    *REQUEST_BLOBS,
    "adoption/phase8/README.md",
    "tests/test_phase7_owner_publication_requests.py",
    "tests/test_phase8_integration.py",
    "tools/check_phase2_disposition_batch.py",
    "tools/check_phase3_disposition_batch.py",
    "tools/check_phase5_stale_reconciliation.py",
    "tools/check_phase6_candidate_reviews.py",
    "tools/check_phase7_owner_publication_requests.py",
    "tools/check_phase8_integration.py",
}
REPAIR_SOURCE_DELTA_PATHS = {
    MANIFEST_PATH,
    MANIFEST_TEST_PATH,
    "tools/check_phase2_disposition_batch.py",
    "tools/check_phase3_disposition_batch.py",
    "tools/check_phase5_stale_reconciliation.py",
}
PHASE9_PROOF_PATHS = {
    "tests/test_phase9_integration.py",
    "tools/check_phase9_integration.py",
}
EXPECTED_INTEGRATION_PATHS = REPAIR_SOURCE_DELTA_PATHS | PHASE9_PROOF_PATHS | {
    ".github/workflows/disposition-intake.yml",
    "tools/check_phase6_candidate_reviews.py",
    "tools/check_phase7_owner_publication_requests.py",
    "tools/check_phase8_integration.py",
}

REPAIR_SOURCE_BLOBS = {
    MANIFEST_PATH: MANIFEST_BLOB,
    MANIFEST_TEST_PATH: MANIFEST_TEST_BLOB,
    "tools/check_phase2_disposition_batch.py": "d31f9a8ade964a7b6f584172a8c46cb5066122ee",
    "tools/check_phase3_disposition_batch.py": "fbda37e06571a14aef6f20ed9bdd53525dc80f34",
    "tools/check_phase5_stale_reconciliation.py": "0036bedd73e941694cf02de54320652d007dcd91",
}
RECONCILED_CHECKER_BLOBS = {
    "tools/check_phase2_disposition_batch.py": "58435ac1d117499c40680a3445597ab662dd1cf0",
    "tools/check_phase3_disposition_batch.py": "d7f2d7456ce062c0669bde249ba06adcf558f7d0",
    "tools/check_phase5_stale_reconciliation.py": "b4d649db2a49a2e30fa0cef223b69364ab077043",
}
FORWARD_CHECKER_BLOBS = {
    "tools/check_phase6_candidate_reviews.py": "1c62968ee079bcb71d3f4d2d293383ddf986e32e",
    "tools/check_phase7_owner_publication_requests.py": "3e201141b2758a2f557194d7de4e1a3a625ac415",
    "tools/check_phase8_integration.py": "e27fca7835f54d7e23b50aa508bdaeb5426a6578",
}
WORKFLOW_BLOB = "6bb4eef0b970e3a15f9e69c46c60f628719289b5"

PREDECESSOR_ALLOWLISTS = {
    "phase2": ("tools/check_phase2_disposition_batch.py", "ALLOWED_PHASE2_PATHS"),
    "phase3": ("tools/check_phase3_disposition_batch.py", "ALLOWED_PHASE3_PATHS"),
    "phase5": ("tools/check_phase5_stale_reconciliation.py", "ALLOWED_PHASE5_PATHS"),
}
MANIFEST_REPAIR_PATHS = {MANIFEST_PATH, MANIFEST_TEST_PATH}
EXPECTED_STATUS_COUNTS = {"ADOPT": 0, "DISTINGUISH": 5, "MISSING": 0, "REJECT": 0, "STALE": 4}
EXPECTED_MANIFEST_AUTHORITY = {
    "providerExecution": False,
    "processSpawnResumeKill": False,
    "containmentOrCanaryCredit": False,
    "automaticGateState": "CLOSED",
    "referenceExecutionBoundary": "NOT_INSTALLED",
    "directInvocationImpossible": False,
    "activationRequiresSeparateAdjudication": True,
}
SHA40 = re.compile(r"[0-9a-f]{40}")


class Phase9Error(ValueError):
    pass


def _git(args: list[str], *, text: bool = False, error: str = "GIT_OBJECT_UNAVAILABLE") -> bytes | str:
    run = subprocess.run(
        ["git", *args], cwd=ROOT, check=False, capture_output=True,
        text=text, encoding="utf-8" if text else None,
    )
    if run.returncode != 0:
        raise Phase9Error(error)
    return run.stdout


def _blob_spec(treeish: str, path: str) -> str:
    return f":{path}" if treeish == ":" else f"{treeish}:{path}"


def _blob(treeish: str, path: str) -> bytes:
    return _git(["show", _blob_spec(treeish, path)], error="GIT_BLOB_UNAVAILABLE")  # type: ignore[return-value]


def _oid(treeish: str, path: str) -> str:
    value = str(_git(["rev-parse", _blob_spec(treeish, path)], text=True, error="GIT_BLOB_OID_UNAVAILABLE")).strip()
    if SHA40.fullmatch(value) is None:
        raise Phase9Error("GIT_BLOB_OID_INVALID")
    return value


def _commit_tuple(commit: str) -> tuple[str, list[str]]:
    value = str(_git(["show", "-s", "--format=%T%n%P", commit], text=True, error="COMMIT_UNAVAILABLE"))
    lines = value.splitlines()
    if len(lines) != 2 or SHA40.fullmatch(lines[0]) is None:
        raise Phase9Error("COMMIT_INVALID")
    parents = lines[1].split() if lines[1] else []
    if any(SHA40.fullmatch(parent) is None for parent in parents):
        raise Phase9Error("COMMIT_INVALID")
    return lines[0], parents


def _is_ancestor(ancestor: str, descendant: str) -> bool:
    return subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=ROOT, check=False, capture_output=True,
    ).returncode == 0


def _changed_paths(base: str, treeish: str) -> set[str]:
    args = ["diff", "--cached", "--name-only", base] if treeish == ":" else ["diff", "--name-only", f"{base}..{treeish}"]
    return set(str(_git(args, text=True, error="INTEGRATION_DIFF_UNAVAILABLE")).splitlines())


def _tree_paths(treeish: str, prefix: str) -> set[str]:
    args = ["ls-files", prefix] if treeish == ":" else ["ls-tree", "-r", "--name-only", treeish, prefix]
    return set(str(_git(args, text=True, error="TREE_CENSUS_UNAVAILABLE")).splitlines())


def _load_json(treeish: str, path: str) -> dict[str, Any]:
    try:
        value = json.loads(_blob(treeish, path))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise Phase9Error("JSON_INVALID") from exc
    if not isinstance(value, dict):
        raise Phase9Error("JSON_ROOT_INVALID")
    return value


def _ast_value(node: ast.AST, env: dict[str, Any]) -> Any:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name) and node.id in env:
        return env[node.id]
    if isinstance(node, ast.Set):
        values = {_ast_value(item, env) for item in node.elts}
        if not all(isinstance(value, str) for value in values):
            raise Phase9Error("ALLOWLIST_AST_INVALID")
        return values
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        left = _ast_value(node.left, env)
        right = _ast_value(node.right, env)
        if not isinstance(left, set) or not isinstance(right, set):
            raise Phase9Error("ALLOWLIST_AST_INVALID")
        return left | right
    raise Phase9Error("ALLOWLIST_AST_UNSUPPORTED")


def _assignment_set(treeish: str, path: str, name: str) -> set[str]:
    try:
        parsed = ast.parse(_blob(treeish, path).decode("utf-8", errors="strict"))
    except (SyntaxError, UnicodeDecodeError) as exc:
        raise Phase9Error("ALLOWLIST_SOURCE_INVALID") from exc
    env: dict[str, Any] = {}
    for node in parsed.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            continue
        try:
            env[node.targets[0].id] = _ast_value(node.value, env)
        except Phase9Error:
            continue
    value = env.get(name)
    if not isinstance(value, set) or not value or not all(isinstance(item, str) for item in value):
        raise Phase9Error("ALLOWLIST_ASSIGNMENT_INVALID")
    return value


def verify_source_objects() -> None:
    if _commit_tuple(PHASE5_BASE) != (PHASE5_TREE, [PHASE5_PARENT]):
        raise Phase9Error("PHASE5_SOURCE_MISMATCH")
    if _commit_tuple(PHASE6_COMMIT) != (PHASE6_TREE, [PHASE6_PARENT]):
        raise Phase9Error("PHASE6_SOURCE_MISMATCH")
    if _commit_tuple(PHASE8_COMMIT) != (PHASE8_TREE, [PHASE6_COMMIT]):
        raise Phase9Error("PHASE8_SOURCE_MISMATCH")
    if _changed_paths(PHASE6_COMMIT, PHASE8_COMMIT) != PHASE8_SOURCE_DELTA_PATHS:
        raise Phase9Error("PHASE8_SOURCE_DELTA_MISMATCH")
    if _commit_tuple(REPAIR_PARENT) != (REPAIR_PARENT_TREE, [PHASE5_BASE]):
        raise Phase9Error("REPAIR_PARENT_MISMATCH")
    if _commit_tuple(REPAIR_COMMIT) != (REPAIR_TREE, [REPAIR_PARENT]):
        raise Phase9Error("REPAIR_SOURCE_MISMATCH")
    if not _is_ancestor(PHASE5_BASE, PHASE8_COMMIT) or not _is_ancestor(PHASE5_BASE, REPAIR_COMMIT):
        raise Phase9Error("SOURCE_LINEAGE_MISMATCH")
    if _changed_paths(PHASE5_BASE, REPAIR_COMMIT) != REPAIR_SOURCE_DELTA_PATHS:
        raise Phase9Error("REPAIR_CUMULATIVE_DELTA_MISMATCH")
    if _changed_paths(REPAIR_PARENT, REPAIR_COMMIT) != REPAIR_SOURCE_DELTA_PATHS:
        raise Phase9Error("REPAIR_TIP_DELTA_MISMATCH")
    for path, expected in REPAIR_SOURCE_BLOBS.items():
        if _oid(REPAIR_COMMIT, path) != expected:
            raise Phase9Error("REPAIR_SOURCE_ARTIFACT_MISMATCH")
    if _oid(PHASE8_COMMIT, RECEIPT_PATH) != RECEIPT_BLOB:
        raise Phase9Error("PHASE8_RECEIPT_MISMATCH")
    for path, expected in REQUEST_BLOBS.items():
        if _oid(PHASE8_COMMIT, path) != expected:
            raise Phase9Error("PHASE8_REQUEST_MISMATCH")


def verify_exact_artifacts(treeish: str) -> None:
    if _oid(treeish, MANIFEST_PATH) != MANIFEST_BLOB or _oid(treeish, MANIFEST_TEST_PATH) != MANIFEST_TEST_BLOB:
        raise Phase9Error("MECHANICAL_REPAIR_DRIFT")
    if _oid(treeish, RECEIPT_PATH) != RECEIPT_BLOB:
        raise Phase9Error("RECEIPT_DRIFT")
    for path, expected in REQUEST_BLOBS.items():
        if _oid(treeish, path) != expected:
            raise Phase9Error("REQUEST_DRIFT")
    for path, expected in {**RECONCILED_CHECKER_BLOBS, **FORWARD_CHECKER_BLOBS}.items():
        if _oid(treeish, path) != expected:
            raise Phase9Error("CHECKER_POSTIMAGE_DRIFT")
    if _oid(treeish, ".github/workflows/disposition-intake.yml") != WORKFLOW_BLOB:
        raise Phase9Error("WORKFLOW_POSTIMAGE_DRIFT")


def verify_allowlist_union(treeish: str) -> None:
    for phase, (path, attribute) in PREDECESSOR_ALLOWLISTS.items():
        source_allowed = _assignment_set(PHASE8_COMMIT, path, attribute)
        source_repair = _assignment_set(REPAIR_COMMIT, path, "MANIFEST_BINDING_REPAIR_PATHS")
        if source_repair != MANIFEST_REPAIR_PATHS:
            raise Phase9Error(f"{phase.upper()}_REPAIR_SCOPE_MISMATCH")
        if _assignment_set(treeish, path, "MANIFEST_BINDING_REPAIR_PATHS") != MANIFEST_REPAIR_PATHS:
            raise Phase9Error(f"{phase.upper()}_REPAIR_SCOPE_DRIFT")
        if _assignment_set(treeish, path, "PHASE9_INTEGRATION_PATHS") != PHASE9_PROOF_PATHS:
            raise Phase9Error(f"{phase.upper()}_PHASE9_SCOPE_DRIFT")
        if _assignment_set(treeish, path, attribute) != source_allowed | MANIFEST_REPAIR_PATHS | PHASE9_PROOF_PATHS:
            raise Phase9Error(f"{phase.upper()}_ALLOWLIST_UNION_MISMATCH")


def verify_frozen_status_and_authority(treeish: str) -> None:
    if _oid(PHASE8_COMMIT, LEDGER_PATH) != LEDGER_BLOB or _oid(treeish, LEDGER_PATH) != LEDGER_BLOB:
        raise Phase9Error("LEDGER_DRIFT")
    ledger = _load_json(treeish, LEDGER_PATH)
    summary = ledger.get("summary")
    if not isinstance(summary, dict) or summary.get("counts") != EXPECTED_STATUS_COUNTS:
        raise Phase9Error("LEDGER_STATUS_ADVANCE")
    projects = ledger.get("projects")
    if not isinstance(projects, list) or Counter(row.get("status") for row in projects if isinstance(row, dict)) != Counter({"DISTINGUISH": 5, "STALE": 4}):
        raise Phase9Error("PROJECT_STATUS_ADVANCE")
    if summary.get("fleetStatus") != "NO_FLEET_ADOPTION" or summary.get("fleetAdoptionClaim") is not False:
        raise Phase9Error("FLEET_STATUS_ADVANCE")
    candidate = ledger.get("candidate")
    claims = candidate.get("authorityClaims") if isinstance(candidate, dict) else None
    if not isinstance(claims, dict) or not claims or any(value is not False for value in claims.values()):
        raise Phase9Error("LEDGER_AUTHORITY_ADVANCE")

    manifest = _load_json(treeish, MANIFEST_PATH)
    if manifest.get("status") != "CANDIDATE_ZERO_AUTHORITY" or manifest.get("authority") != EXPECTED_MANIFEST_AUTHORITY:
        raise Phase9Error("MANIFEST_AUTHORITY_ADVANCE")

    receipt = _load_json(treeish, RECEIPT_PATH)
    receipt_summary = receipt.get("summary")
    if not isinstance(receipt_summary, dict) or any(
        receipt_summary.get(field) != 0
        for field in ("ledgerStatusChangesAuthorized", "adoptionClaims", "installationClaims", "runtimeAuthorityClaims")
    ):
        raise Phase9Error("RECEIPT_AUTHORITY_ADVANCE")
    reviews = receipt.get("reviews")
    if not isinstance(reviews, list) or not reviews:
        raise Phase9Error("RECEIPT_REVIEWS_INVALID")
    for review in reviews:
        authority = review.get("authority") if isinstance(review, dict) else None
        if not isinstance(authority, dict) or not authority or any(value is not False for value in authority.values()):
            raise Phase9Error("RECEIPT_AUTHORITY_ADVANCE")

    for path in sorted(REQUEST_BLOBS):
        request = _load_json(treeish, path)
        if request.get("status") != "REQUEST_ONLY_ZERO_AUTHORITY":
            raise Phase9Error("REQUEST_STATUS_ADVANCE")
        authority = request.get("authority")
        queue = request.get("queue")
        if not isinstance(authority, dict) or not authority or any(value is not False for value in authority.values()):
            raise Phase9Error("REQUEST_AUTHORITY_ADVANCE")
        if not isinstance(queue, dict) or any(queue.get(field) is not False for field in ("executable", "automaticStatusAdvance", "writesAuthorized", "providerCallsAuthorized")):
            raise Phase9Error("REQUEST_QUEUE_ADVANCE")

    source_specs = _tree_paths(PHASE8_COMMIT, "specs")
    if _tree_paths(treeish, "specs") != source_specs:
        raise Phase9Error("SPEC_SET_DRIFT")
    for path in source_specs:
        if _oid(treeish, path) != _oid(PHASE8_COMMIT, path):
            raise Phase9Error("SPEC_STATUS_DRIFT")


def _manifest_check(treeish: str) -> str:
    run = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "check_universal_manifest.py"), "--treeish", treeish],
        cwd=ROOT, check=False, capture_output=True, text=True, encoding="utf-8",
    )
    if run.returncode != 0:
        raise Phase9Error("GLOBAL_MANIFEST_HEAD_FAIL")
    return run.stdout.strip()


def verify_global_manifest(treeish: str) -> None:
    expected = f"MANIFEST_PASS subjects=99 self=PASS treeish={treeish}"
    if _manifest_check(treeish) != expected:
        raise Phase9Error("GLOBAL_MANIFEST_RESULT_MISMATCH")


def verify_integration(treeish: str) -> None:
    verify_source_objects()
    if treeish == ":":
        head = str(_git(["rev-parse", "HEAD"], text=True, error="HEAD_UNAVAILABLE")).strip()
        if head != PHASE8_COMMIT:
            raise Phase9Error("STAGED_BASE_MISMATCH")
    elif _commit_tuple(treeish)[1] != [PHASE8_COMMIT]:
        raise Phase9Error("INTEGRATION_PARENT_MISMATCH")
    if _changed_paths(PHASE8_COMMIT, treeish) != EXPECTED_INTEGRATION_PATHS:
        raise Phase9Error("INTEGRATION_SCOPE_MISMATCH")
    verify_exact_artifacts(treeish)
    verify_allowlist_union(treeish)
    verify_frozen_status_and_authority(treeish)
    verify_global_manifest(treeish)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--treeish", default="HEAD")
    args = parser.parse_args()
    try:
        verify_integration(args.treeish)
    except Phase9Error as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(
        "PASS: Phase 8 is the sole parent; the accepted manifest repair is exact; "
        "receipt/request artifacts, ledger/spec statuses, and all authority remain frozen"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
