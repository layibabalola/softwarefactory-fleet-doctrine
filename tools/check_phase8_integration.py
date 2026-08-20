#!/usr/bin/env python3
"""Verify the linear, zero-authority integration of accepted R26 Phases 6 and 7."""

from __future__ import annotations

import argparse
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
PHASE7_COMMIT = "c5b9efd00c47a84488b96734dd9b6a94ecd37999"
PHASE7_TREE = "2d9f5d82bf1a8acbef5839ac6fcaecc1caf53023"
PHASE8_COMMIT = "2223647059cb789fd350883597756666357583df"
PHASE8_TREE = "062ee5311cc56b6ea50c2ce3f4e9d095847069e8"
PHASE9_COMMIT = "18b95fd82f92920117c8f0f432ae8e9bc5e8ffc8"
PHASE9_TREE = "fe0ed384bfd9485f4bbc4004225831c6aabe06a4"
LEDGER_PATH = "adoption/universal-token-control-r26.json"
LEDGER_BLOB = "333cc6d47e99a857b64150a87bd9f834590256e1"
GLOBAL_MANIFEST_PATH = "manifests/universal-provider-control-reconciliation-r26.json"
GLOBAL_MANIFEST_BLOB = "898385fb82fbbe9946f937f0486142f4733d03fe"
REPAIRED_GLOBAL_MANIFEST_BLOB = "65901748c5843f05b37e4352c5b469e47804e2f1"

PHASE6_EXACT_TARGET_BLOBS = {
    "adoption/README.md": "13aa1bebfb5e42df28e4c0ec3069c679c547480c",
    "adoption/phase6/README.md": "58e9541e3287431f9712c3fb37cbbf1d506f6c29",
    "adoption/phase6/r26-local-candidate-review-receipts.json": "c10b1b7530e0d9695118a02dd21842e4fc1493e0",
    "tests/test_phase6_candidate_reviews.py": "9a7b44e38fe58bf005dfb5d62866606d215830fd",
}
PHASE7_EXACT_TARGET_BLOBS = {
    "adoption/phase7/README.md": "51f4d9961656a1ee916eff9f84249118150883dd",
    "adoption/phase7/requests/adobe-ingester.json": "893de38f19c90303c4935de47fa535f590c91b4d",
    "adoption/phase7/requests/agent-bridge.json": "b62bef05c4d980808478bed4b063b50751f8b0c3",
    "adoption/phase7/requests/airmypc.json": "7d202d0ad16d79a8ffdcd5589fd9af9422a2dbe3",
    "adoption/phase7/requests/conjugal.json": "1f046669b36e994e26d451fa1341e54ae624081e",
    "tests/test_phase7_owner_publication_requests.py": "9106db255841ce3304a7ca3d62f07db81e9cd02b",
}
PHASE7_SOURCE_DELTA_BLOBS = {
    ".github/workflows/disposition-intake.yml": "858324e60080631c838c3b33250e896947df7a59",
    **PHASE7_EXACT_TARGET_BLOBS,
    "tools/check_phase2_disposition_batch.py": "9dcad34475ae9317c49b08153dcbbacb161b37dd",
    "tools/check_phase3_disposition_batch.py": "5a04692a6545c3cb45ec0c246d36512b2dcac71f",
    "tools/check_phase5_stale_reconciliation.py": "5ec82e2b4448da4c2a97b1b7916a443e6dd86123",
    "tools/check_phase7_owner_publication_requests.py": "76b45702a6c76f65699cc711e88e0602371d0375",
}
PHASE7_SOURCE_DELTA_PATHS = set(PHASE7_SOURCE_DELTA_BLOBS)
EXPECTED_INTEGRATION_PATHS = PHASE7_SOURCE_DELTA_PATHS | {
    "adoption/phase8/README.md",
    "tests/test_phase8_integration.py",
    "tools/check_phase6_candidate_reviews.py",
    "tools/check_phase8_integration.py",
}
PHASE9_FORWARD_PATHS = {
    ".github/workflows/disposition-intake.yml",
    GLOBAL_MANIFEST_PATH,
    "tests/test_phase9_integration.py",
    "tests/test_universal_manifest_spec_bindings.py",
    "tools/check_phase2_disposition_batch.py",
    "tools/check_phase3_disposition_batch.py",
    "tools/check_phase5_stale_reconciliation.py",
    "tools/check_phase6_candidate_reviews.py",
    "tools/check_phase7_owner_publication_requests.py",
    "tools/check_phase8_integration.py",
    "tools/check_phase9_integration.py",
}
PHASE10_FORWARD_PATHS = {
    ".github/workflows/disposition-intake.yml",
    "adoption/phase10/README.md",
    "adoption/phase10/r26-local-candidate-review-receipts.json",
    "tests/test_phase10_integration.py",
    "tools/check_phase2_disposition_batch.py",
    "tools/check_phase3_disposition_batch.py",
    "tools/check_phase5_stale_reconciliation.py",
    "tools/check_phase6_candidate_reviews.py",
    "tools/check_phase7_owner_publication_requests.py",
    "tools/check_phase8_integration.py",
    "tools/check_phase9_integration.py",
    "tools/check_phase10_integration.py",
}

# Filled only after the mechanical union is staged. These exact postimage blobs make every conflict
# resolution reviewable and prevent a broad allowlist or workflow edit from hiding in the replay.
NARROW_RESOLUTION_BLOBS = {
    ".github/workflows/disposition-intake.yml": "18b75c57685cb5d9cd15e82cc4ce65259fbb86ab",
    "tools/check_phase2_disposition_batch.py": "e23386b7cdb832e967c55e2cdb693ef50f9ecfec",
    "tools/check_phase3_disposition_batch.py": "a82a090a2734ec21ca2542f08009ff16a2c3f8cb",
    "tools/check_phase5_stale_reconciliation.py": "581b5db53dc2a6349dc3a8db7f93c8e637173738",
    "tools/check_phase6_candidate_reviews.py": "11a86d02df7ece734ed68fadd372ad1789511dd0",
    "tools/check_phase7_owner_publication_requests.py": "4f416401e227cc17d48f3cea718f54ec4fc3c7b4",
}
PHASE9_NARROW_RESOLUTION_BLOBS = {
    ".github/workflows/disposition-intake.yml": "6bb4eef0b970e3a15f9e69c46c60f628719289b5",
    "tools/check_phase2_disposition_batch.py": "58435ac1d117499c40680a3445597ab662dd1cf0",
    "tools/check_phase3_disposition_batch.py": "d7f2d7456ce062c0669bde249ba06adcf558f7d0",
    "tools/check_phase5_stale_reconciliation.py": "b4d649db2a49a2e30fa0cef223b69364ab077043",
    "tools/check_phase6_candidate_reviews.py": "1c62968ee079bcb71d3f4d2d293383ddf986e32e",
    "tools/check_phase7_owner_publication_requests.py": "3e201141b2758a2f557194d7de4e1a3a625ac415",
}
EXPECTED_STATUS_COUNTS = {"ADOPT": 0, "DISTINGUISH": 5, "MISSING": 0, "REJECT": 0, "STALE": 4}
REQUEST_STATUS = "REQUEST_ONLY_ZERO_AUTHORITY"
REQUEST_DIR = "adoption/phase7/requests"
REQUEST_IDS = {"adobe-ingester", "agent-bridge", "airmypc", "conjugal"}
SHA40 = re.compile(r"[0-9a-f]{40}")


class Phase8Error(ValueError):
    pass


def _git(args: list[str], *, text: bool = False, error: str = "GIT_OBJECT_UNAVAILABLE") -> bytes | str:
    run = subprocess.run(
        ["git", *args], cwd=ROOT, check=False, capture_output=True,
        text=text, encoding="utf-8" if text else None,
    )
    if run.returncode != 0:
        raise Phase8Error(error)
    return run.stdout


def _blob_spec(treeish: str, path: str) -> str:
    return f":{path}" if treeish == ":" else f"{treeish}:{path}"


def _blob(treeish: str, path: str) -> bytes:
    return _git(["show", _blob_spec(treeish, path)], error="GIT_BLOB_UNAVAILABLE")  # type: ignore[return-value]


def _oid(treeish: str, path: str) -> str:
    value = str(_git(["rev-parse", _blob_spec(treeish, path)], text=True, error="GIT_BLOB_OID_UNAVAILABLE")).strip()
    if SHA40.fullmatch(value) is None:
        raise Phase8Error("GIT_BLOB_OID_INVALID")
    return value


def _commit_tuple(commit: str) -> tuple[str, list[str]]:
    value = str(_git(["show", "-s", "--format=%T%n%P", commit], text=True, error="COMMIT_UNAVAILABLE"))
    lines = value.splitlines()
    if len(lines) != 2 or SHA40.fullmatch(lines[0]) is None:
        raise Phase8Error("COMMIT_INVALID")
    parents = lines[1].split() if lines[1] else []
    if any(SHA40.fullmatch(parent) is None for parent in parents):
        raise Phase8Error("COMMIT_INVALID")
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
        raise Phase8Error("JSON_INVALID") from exc
    if not isinstance(value, dict):
        raise Phase8Error("JSON_ROOT_INVALID")
    return value


def verify_source_objects() -> None:
    if _commit_tuple(PHASE5_BASE) != (PHASE5_TREE, [PHASE5_PARENT]):
        raise Phase8Error("PHASE5_BASE_MISMATCH")
    if _commit_tuple(PHASE6_COMMIT) != (PHASE6_TREE, [PHASE6_PARENT]):
        raise Phase8Error("PHASE6_SUBJECT_MISMATCH")
    if not _is_ancestor(PHASE5_BASE, PHASE6_COMMIT):
        raise Phase8Error("PHASE6_LINEAGE_MISMATCH")
    if _commit_tuple(PHASE7_COMMIT) != (PHASE7_TREE, [PHASE5_BASE]):
        raise Phase8Error("PHASE7_SUBJECT_MISMATCH")
    if _changed_paths(PHASE5_BASE, PHASE7_COMMIT) != PHASE7_SOURCE_DELTA_PATHS:
        raise Phase8Error("PHASE7_SOURCE_SCOPE_MISMATCH")
    if _commit_tuple(PHASE8_COMMIT) != (PHASE8_TREE, [PHASE6_COMMIT]):
        raise Phase8Error("PHASE8_SUBJECT_MISMATCH")
    if _changed_paths(PHASE6_COMMIT, PHASE8_COMMIT) != EXPECTED_INTEGRATION_PATHS:
        raise Phase8Error("INTEGRATION_SCOPE_MISMATCH")
    for path, expected in PHASE6_EXACT_TARGET_BLOBS.items():
        if _oid(PHASE6_COMMIT, path) != expected:
            raise Phase8Error("PHASE6_SOURCE_ARTIFACT_MISMATCH")
    for path, expected in PHASE7_SOURCE_DELTA_BLOBS.items():
        if _oid(PHASE7_COMMIT, path) != expected:
            raise Phase8Error("PHASE7_SOURCE_ARTIFACT_MISMATCH")


def verify_zero_authority_packets(treeish: str) -> None:
    packet_paths = _tree_paths(treeish, REQUEST_DIR)
    expected_paths = {f"{REQUEST_DIR}/{project_id}.json" for project_id in REQUEST_IDS}
    if packet_paths != expected_paths:
        raise Phase8Error("REQUEST_SET_MISMATCH")
    for project_id in sorted(REQUEST_IDS):
        packet = _load_json(treeish, f"{REQUEST_DIR}/{project_id}.json")
        if packet.get("projectId") != project_id or packet.get("status") != REQUEST_STATUS:
            raise Phase8Error("REQUEST_STATUS_ADVANCE")
        authority = packet.get("authority")
        if not isinstance(authority, dict) or not authority or any(value is not False for value in authority.values()):
            raise Phase8Error("REQUEST_AUTHORITY_ADVANCE")
        queue = packet.get("queue")
        if not isinstance(queue, dict) or queue.get("automaticStatusAdvance") is not False:
            raise Phase8Error("REQUEST_QUEUE_ADVANCE")
        if queue.get("writesAuthorized") is not False or queue.get("providerCallsAuthorized") is not False:
            raise Phase8Error("REQUEST_QUEUE_AUTHORITY_ADVANCE")


def verify_frozen_status(treeish: str) -> None:
    if _oid(PHASE6_COMMIT, LEDGER_PATH) != LEDGER_BLOB or _oid(PHASE7_COMMIT, LEDGER_PATH) != LEDGER_BLOB:
        raise Phase8Error("SOURCE_LEDGER_MISMATCH")
    if _oid(treeish, LEDGER_PATH) != LEDGER_BLOB:
        raise Phase8Error("LEDGER_STATUS_ADVANCE")
    ledger = _load_json(treeish, LEDGER_PATH)
    summary = ledger.get("summary")
    if not isinstance(summary, dict) or summary.get("counts") != EXPECTED_STATUS_COUNTS:
        raise Phase8Error("LEDGER_COUNTS_ADVANCE")
    projects = ledger.get("projects")
    if not isinstance(projects, list) or Counter(row.get("status") for row in projects if isinstance(row, dict)) != Counter({"DISTINGUISH": 5, "STALE": 4}):
        raise Phase8Error("LEDGER_PROJECT_STATUS_ADVANCE")
    if summary.get("fleetStatus") != "NO_FLEET_ADOPTION" or summary.get("fleetAdoptionClaim") is not False:
        raise Phase8Error("FLEET_STATUS_ADVANCE")
    candidate = ledger.get("candidate")
    claims = candidate.get("authorityClaims") if isinstance(candidate, dict) else None
    if not isinstance(claims, dict) or any(value is not False for value in claims.values()):
        raise Phase8Error("LEDGER_AUTHORITY_ADVANCE")


def verify_protected_artifacts(
    treeish: str, *, repaired_manifest: bool = False, phase10_forward: bool = False
) -> None:
    for path, expected in {**PHASE6_EXACT_TARGET_BLOBS, **PHASE7_EXACT_TARGET_BLOBS}.items():
        if _oid(treeish, path) != expected:
            raise Phase8Error("PRESERVED_ARTIFACT_DRIFT")
    if not phase10_forward:
        expected_resolutions = PHASE9_NARROW_RESOLUTION_BLOBS if repaired_manifest else NARROW_RESOLUTION_BLOBS
        for path, expected in expected_resolutions.items():
            if SHA40.fullmatch(expected) is None or _oid(treeish, path) != expected:
                raise Phase8Error("NARROW_RESOLUTION_DRIFT")
    source_specs = _tree_paths(PHASE6_COMMIT, "specs")
    if _tree_paths(treeish, "specs") != source_specs:
        raise Phase8Error("SPEC_SET_DRIFT")
    for path in source_specs:
        if _oid(treeish, path) != _oid(PHASE6_COMMIT, path):
            raise Phase8Error("SPEC_BLOB_DRIFT")
    if _oid(PHASE6_COMMIT, GLOBAL_MANIFEST_PATH) != GLOBAL_MANIFEST_BLOB:
        raise Phase8Error("SOURCE_GLOBAL_MANIFEST_MISMATCH")
    expected_manifest = REPAIRED_GLOBAL_MANIFEST_BLOB if repaired_manifest else GLOBAL_MANIFEST_BLOB
    if _oid(treeish, GLOBAL_MANIFEST_PATH) != expected_manifest:
        raise Phase8Error("GLOBAL_MANIFEST_BASELINE_DRIFT")


def verify_integration(treeish: str) -> None:
    verify_source_objects()
    verify_protected_artifacts(PHASE8_COMMIT)
    verify_frozen_status(PHASE8_COMMIT)
    verify_zero_authority_packets(PHASE8_COMMIT)
    if treeish == PHASE8_COMMIT:
        return
    if _commit_tuple(PHASE9_COMMIT) != (PHASE9_TREE, [PHASE8_COMMIT]):
        raise Phase8Error("PHASE9_SOURCE_MISMATCH")
    if _changed_paths(PHASE8_COMMIT, PHASE9_COMMIT) != PHASE9_FORWARD_PATHS:
        raise Phase8Error("PHASE9_SOURCE_SCOPE_MISMATCH")
    resolved = None if treeish == ":" else str(
        _git(["rev-parse", f"{treeish}^{{commit}}"], text=True, error="COMMIT_UNAVAILABLE")
    ).strip()
    if resolved == PHASE9_COMMIT:
        if _commit_tuple(treeish) != (PHASE9_TREE, [PHASE8_COMMIT]):
            raise Phase8Error("INTEGRATION_PARENT_MISMATCH")
        if _changed_paths(PHASE8_COMMIT, treeish) != PHASE9_FORWARD_PATHS:
            raise Phase8Error("INTEGRATION_SCOPE_MISMATCH")
        verify_protected_artifacts(treeish, repaired_manifest=True)
        verify_frozen_status(treeish)
        verify_zero_authority_packets(treeish)
        return
    if treeish == ":":
        if str(_git(["rev-parse", "HEAD"], text=True, error="HEAD_UNAVAILABLE")).strip() != PHASE9_COMMIT:
            raise Phase8Error("STAGED_BASE_MISMATCH")
    elif _commit_tuple(treeish)[1] != [PHASE9_COMMIT]:
        raise Phase8Error("INTEGRATION_PARENT_MISMATCH")
    if _changed_paths(PHASE9_COMMIT, treeish) != PHASE10_FORWARD_PATHS:
        raise Phase8Error("INTEGRATION_SCOPE_MISMATCH")
    verify_protected_artifacts(treeish, repaired_manifest=True, phase10_forward=True)
    verify_frozen_status(treeish)
    verify_zero_authority_packets(treeish)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--treeish", default="HEAD")
    args = parser.parse_args()
    try:
        verify_integration(args.treeish)
    except Phase8Error as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(
        "PASS: the accepted Phase 8 and Phase 9 objects are exact; the bounded Phase 10 "
        "descendant preserves requests, ledger, specs, status, and zero authority"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
