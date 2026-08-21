#!/usr/bin/env python3
"""Verify the zero-authority integration of reviewed Phase 6-11 evidence with current master."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = "adoption/phase12/r26-current-master-review-integration.json"
MERGE_COMMIT = "1bf5ad616c6a2c9200ff34e03c749da0997475c2"
MERGE_TREE = "b71faec6fe42881a65d123690d08309cf96a2746"
CURRENT_MASTER = "1f96975233bfa794dd039610c072bf67aa1d20ff"
CURRENT_MASTER_TREE = "fc54c4f9cb53a3dc272767dd4713b99b662368b5"
CURRENT_MASTER_PARENTS = [
    "8c7dc4f4339db82a8b3c2efd689bf5f72631ad6e",
    "4ce276a542d6d6674956e1b8fe6d5a82b5381c4d",
]
PHASE11_COMMIT = "e7311e3038bbfeebe15cc10004f40b3795811659"
PHASE11_TREE = "0d509e980bccdd1f27eecfbde93ec285a6d6ed16"
PHASE11_PARENT = "940c790eedd118736ff0207c1b7dc407d5643802"
MANIFEST = "manifests/universal-provider-control-reconciliation-r26.json"
MANIFEST_OID = "898385fb82fbbe9946f937f0486142f4733d03fe"
MANIFEST_CHECKER = "tools/check_universal_manifest.py"
MANIFEST_CHECKER_OID = "479256c1c7ce7bfee9a9e9cd03f3cd76ac04f3aa"
LEDGER = "adoption/universal-token-control-r26.json"
LEDGER_OID = "2f1808e8df35e6d1bae98f83aab378d93a0c3228"
COUNTS = {"ADOPT": 0, "DISTINGUISH": 5, "MISSING": 0, "REJECT": 0, "STALE": 4}
EVIDENCE = {
    "adoption/phase6/r26-local-candidate-review-receipts.json": "c10b1b7530e0d9695118a02dd21842e4fc1493e0",
    "adoption/phase10/r26-local-candidate-review-receipts.json": "2f5d543754d35eb6e2f8143465e3ea2a1d1abffc",
    "adoption/phase11/r26-phase10-review-shape-closure.json": "02af11ad375c6de6fffc3cc1f88bd1e0d3a477ee",
}
HISTORICAL_CHECKERS = (
    "tools/check_phase6_candidate_reviews.py",
    "tools/check_phase7_owner_publication_requests.py",
    "tools/check_phase8_integration.py",
    "tools/check_phase9_integration.py",
    "tools/check_phase10_integration.py",
    "tools/check_phase11_integration.py",
)
INTEGRATION_PATHS = {
    ".github/workflows/disposition-intake.yml",
    "adoption/phase12/README.md",
    ARTIFACT,
    MANIFEST,
    "tests/test_phase6_candidate_reviews.py",
    "tests/test_phase7_owner_publication_requests.py",
    "tests/test_phase8_integration.py",
    "tests/test_phase9_integration.py",
    "tests/test_phase10_integration.py",
    "tests/test_phase11_integration.py",
    "tests/test_phase12_integration.py",
    "tests/test_universal_manifest_spec_bindings.py",
    "tools/check_phase9_integration.py",
    "tools/check_phase12_integration.py",
}
AUTHORITY_KEYS = {
    "projectDisposition", "fleetAdoption", "installation", "runtime",
    "providerExecution", "taskOrGateMutation", "pushOrMerge",
}


class Phase12Error(ValueError):
    pass


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    folded: set[str] = set()
    for key, value in pairs:
        if key in result or key.casefold() in folded:
            raise Phase12Error("DUPLICATE_OR_CASE_COLLIDING_KEY")
        result[key] = value
        folded.add(key.casefold())
    return result


def load_json(raw: bytes) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Phase12Error("JSON_INVALID") from exc
    if not isinstance(value, dict):
        raise Phase12Error("JSON_ROOT_INVALID")
    return value


def _git(args: list[str], *, text: bool = False) -> bytes | str:
    run = subprocess.run(
        ["git", *args], cwd=ROOT, check=False, capture_output=True,
        text=text, encoding="utf-8" if text else None,
    )
    if run.returncode != 0:
        raise Phase12Error("GIT_COMMAND_FAILED")
    return run.stdout


def _blob(treeish: str, path: str) -> bytes:
    spec = f":{path}" if treeish == ":" else f"{treeish}:{path}"
    value = _git(["show", spec])
    assert isinstance(value, bytes)
    return value


def _oid(treeish: str, path: str) -> str:
    spec = f":{path}" if treeish == ":" else f"{treeish}:{path}"
    value = _git(["rev-parse", spec], text=True)
    assert isinstance(value, str)
    return value.strip()


def _tuple(commit: str) -> tuple[str, list[str]]:
    value = _git(["show", "-s", "--format=%T%n%P", commit], text=True)
    assert isinstance(value, str)
    lines = value.splitlines()
    if len(lines) != 2:
        raise Phase12Error("COMMIT_TUPLE_INVALID")
    return lines[0], lines[1].split()


def _changed_paths(base: str, treeish: str) -> set[str]:
    args = ["diff", "--cached", "--name-only", base] if treeish == ":" else ["diff", "--name-only", f"{base}..{treeish}"]
    value = _git(args, text=True)
    assert isinstance(value, str)
    return set(value.splitlines())


def _expected_artifact() -> dict[str, Any]:
    return {
        "schema": "fleet-r26-current-master-review-integration/v1",
        "status": "CANDIDATE_ZERO_AUTHORITY",
        "merge": {"commit": MERGE_COMMIT, "tree": MERGE_TREE, "orderedParents": [CURRENT_MASTER, PHASE11_COMMIT]},
        "currentMaster": {"commit": CURRENT_MASTER, "tree": CURRENT_MASTER_TREE, "orderedParents": CURRENT_MASTER_PARENTS},
        "reviewedPhase11": {"commit": PHASE11_COMMIT, "tree": PHASE11_TREE, "orderedParents": [PHASE11_PARENT]},
        "activePolicy": {
            "manifestPath": MANIFEST,
            "manifestGitBlobOid": MANIFEST_OID,
            "manifestBinding": "IMMUTABLE_R26_CANDIDATE_SNAPSHOT",
            "phase9ManifestRepairTreatment": "HISTORICAL_ACCEPTED_EVIDENCE_NOT_ACTIVE_POLICY",
            "ledgerPath": LEDGER,
            "ledgerGitBlobOid": LEDGER_OID,
            "counts": COUNTS,
        },
        "importedEvidence": [
            {"path": path, "gitBlobOid": oid} for path, oid in EVIDENCE.items()
        ],
        "authority": {key: False for key in sorted(AUTHORITY_KEYS)},
    }


def _type_exact(actual: Any, expected: Any) -> bool:
    if type(actual) is not type(expected):
        return False
    if isinstance(expected, dict):
        return set(actual) == set(expected) and all(_type_exact(actual[key], value) for key, value in expected.items())
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(_type_exact(a, e) for a, e in zip(actual, expected))
    return actual == expected


def verify_sources() -> None:
    if _tuple(CURRENT_MASTER) != (CURRENT_MASTER_TREE, CURRENT_MASTER_PARENTS):
        raise Phase12Error("CURRENT_MASTER_TUPLE_MISMATCH")
    if _tuple(PHASE11_COMMIT) != (PHASE11_TREE, [PHASE11_PARENT]):
        raise Phase12Error("PHASE11_TUPLE_MISMATCH")
    if _tuple(MERGE_COMMIT) != (MERGE_TREE, [CURRENT_MASTER, PHASE11_COMMIT]):
        raise Phase12Error("MERGE_TUPLE_MISMATCH")


def verify_current_policy(treeish: str) -> None:
    if _oid(treeish, MANIFEST) != MANIFEST_OID or _oid(treeish, MANIFEST_CHECKER) != MANIFEST_CHECKER_OID:
        raise Phase12Error("ACTIVE_MANIFEST_POLICY_DRIFT")
    if _oid(treeish, LEDGER) != LEDGER_OID:
        raise Phase12Error("LEDGER_DRIFT")
    ledger = load_json(_blob(treeish, LEDGER))
    if ledger.get("summary", {}).get("counts") != COUNTS:
        raise Phase12Error("LEDGER_COUNTS_DRIFT")
    if ledger.get("summary", {}).get("fleetAdoptionClaim") is not False:
        raise Phase12Error("FLEET_ADOPTION_OVERCLAIM")
    upstream_specs = str(_git(["ls-tree", "-r", "--name-only", CURRENT_MASTER, "specs"], text=True)).splitlines()
    current_tree = MERGE_COMMIT if treeish == ":" else treeish
    current_specs = str(_git(["ls-tree", "-r", "--name-only", current_tree, "specs"], text=True)).splitlines()
    if current_specs != upstream_specs:
        raise Phase12Error("SPEC_SET_DRIFT")
    for path in upstream_specs:
        if _oid(treeish, path) != _oid(CURRENT_MASTER, path):
            raise Phase12Error("SPEC_BLOB_DRIFT")


def verify_evidence(treeish: str) -> None:
    for path, oid in EVIDENCE.items():
        if _oid(PHASE11_COMMIT, path) != oid or _oid(treeish, path) != oid:
            raise Phase12Error("IMPORTED_EVIDENCE_DRIFT")


def verify_workflow(treeish: str) -> None:
    workflow = _blob(treeish, ".github/workflows/disposition-intake.yml").decode("utf-8", errors="strict")
    for checker in HISTORICAL_CHECKERS:
        command = f"python {checker} --treeish {PHASE11_COMMIT}"
        if workflow.count(command) != 1:
            raise Phase12Error("HISTORICAL_CHECKER_ROUTING_INVALID")
    required = (
        'test_phase12_integration.py" -v',
        "python tools/check_phase12_integration.py --treeish HEAD",
    )
    if any(workflow.count(item) != 1 for item in required):
        raise Phase12Error("PHASE12_WORKFLOW_MISSING")


def verify_integration(treeish: str) -> None:
    verify_sources()
    if treeish == ":":
        head = str(_git(["rev-parse", "HEAD"], text=True)).strip()
        if head != MERGE_COMMIT:
            raise Phase12Error("STAGED_PARENT_MISMATCH")
    elif _tuple(treeish)[1] != [MERGE_COMMIT]:
        raise Phase12Error("INTEGRATION_PARENT_MISMATCH")
    if _changed_paths(MERGE_COMMIT, treeish) != INTEGRATION_PATHS:
        raise Phase12Error("INTEGRATION_SCOPE_MISMATCH")
    artifact = load_json(_blob(treeish, ARTIFACT))
    if not _type_exact(artifact, _expected_artifact()):
        raise Phase12Error("INTEGRATION_ARTIFACT_MISMATCH")
    if set(artifact["authority"]) != AUTHORITY_KEYS or any(value is not False for value in artifact["authority"].values()):
        raise Phase12Error("AUTHORITY_OVERCLAIM")
    verify_current_policy(treeish)
    verify_evidence(treeish)
    verify_workflow(treeish)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--treeish", default="HEAD")
    args = parser.parse_args()
    try:
        verify_integration(args.treeish)
    except Phase12Error as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    raw = _blob(args.treeish, ARTIFACT)
    print(f"PASS: Phase12 current-master integration is exact, zero-authority, ledger=0/5/4 artifact_sha256={hashlib.sha256(raw).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
