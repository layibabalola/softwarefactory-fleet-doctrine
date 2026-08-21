#!/usr/bin/env python3
"""Verify the zero-authority Phase 14 MLV task-definition publication."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PHASE13 = "eca6e364cf03e388f0416e3f8e80fe4091321aa0"
PHASE13_TREE = "20f47e3e9430aaa79d05551b932ca1a8edd7ff4f"
PHASE13_PARENT = "990906b6ea861ca579e1336bcfe8f17dd80c83ae"
ARTIFACT = "adoption/phase14/r26-mlv-task-definition-publication.json"
ARTIFACT_SHA256 = "5D3FB61ECFEBAC07B6F445DD7B7B72111B11712E67112C38CDEE1A972F5C2F0B"
LEDGER = "adoption/universal-token-control-r26.json"
LEDGER_OID = "2f1808e8df35e6d1bae98f83aab378d93a0c3228"
MANIFEST = "manifests/universal-provider-control-reconciliation-r26.json"
MANIFEST_OID = "898385fb82fbbe9946f937f0486142f4733d03fe"
COUNTS = {"ADOPT": 0, "DISTINGUISH": 5, "MISSING": 0, "REJECT": 0, "STALE": 4}
INTEGRATION_PATHS = {
    ".github/workflows/disposition-intake.yml",
    "adoption/phase14/README.md",
    ARTIFACT,
    "tests/test_phase13_integration.py",
    "tests/test_phase14_integration.py",
    "tests/test_phase5_stale_reconciliation.py",
    "tests/test_phase8_integration.py",
    "tests/test_phase10_integration.py",
    "tools/check_phase10_integration.py",
    "tools/check_phase11_integration.py",
    "tools/check_phase14_integration.py",
}
AUTHORITY_KEYS = {
    "projectDisposition", "fleetAdoption", "installation", "runtime",
    "providerExecution", "taskOrGateMutation", "pushOrMerge",
}


class Phase14Error(ValueError):
    pass


def _pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    folded: set[str] = set()
    for key, value in items:
        if not isinstance(key, str) or key.casefold() in folded:
            raise Phase14Error("DUPLICATE_OR_CASE_COLLIDING_KEY")
        folded.add(key.casefold())
        out[key] = value
    return out


def load_json(raw: bytes) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Phase14Error("JSON_INVALID") from exc
    if type(value) is not dict:
        raise Phase14Error("JSON_ROOT_INVALID")
    return value


def _git(args: list[str], *, text: bool = False) -> bytes | str:
    run = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, check=False,
                         text=text, encoding="utf-8" if text else None)
    if run.returncode != 0:
        raise Phase14Error("GIT_COMMAND_FAILED")
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
        raise Phase14Error("COMMIT_TUPLE_INVALID")
    return lines[0], lines[1].split()


def _changed_paths(base: str, treeish: str) -> set[str]:
    args = ["diff", "--cached", "--name-only", base] if treeish == ":" else ["diff", "--name-only", f"{base}..{treeish}"]
    value = _git(args, text=True)
    assert isinstance(value, str)
    return set(value.splitlines())


def _native(value: Any, expected: Any) -> bool:
    if type(value) is not type(expected):
        return False
    if type(expected) is dict:
        return set(value) == set(expected) and all(_native(value[key], expected[key]) for key in expected)
    if type(expected) is list:
        return len(value) == len(expected) and all(_native(a, b) for a, b in zip(value, expected))
    return value == expected


def verify_artifact(treeish: str) -> None:
    raw = _blob(treeish, ARTIFACT)
    if hashlib.sha256(raw).hexdigest().upper() != ARTIFACT_SHA256:
        raise Phase14Error("ARTIFACT_HASH_MISMATCH")
    doc = load_json(raw)
    if doc.get("schema") != "fleet-r26-mlv-task-definition-publication/v1" or doc.get("status") != "CANDIDATE_ZERO_AUTHORITY":
        raise Phase14Error("ARTIFACT_IDENTITY_INVALID")
    source = doc.get("sourceProject", {})
    expected_source = {
        "projectId": "mlv-app",
        "canonicalOrigin": "https://github.com/layibabalola/MLV-App.git",
        "publishedRef": "refs/heads/codex/mlv-r37-task-definition-enumeration",
        "commit": "a4bb0d7a2833e760ba1d0d6cfb53133d69f09c24",
        "tree": "fd6de9b74a0a2ed48fa751048ad5e215849bf9c8",
        "orderedParents": ["2ef9690649519d91197199d401d46fe3bb6d8dbb"],
        "remoteRefVerified": True,
        "remoteVerifiedCommit": "a4bb0d7a2833e760ba1d0d6cfb53133d69f09c24",
    }
    if not _native(source, expected_source):
        raise Phase14Error("SOURCE_PROJECT_TUPLE_INVALID")
    candidate = doc.get("r37Candidate", {})
    controls = candidate.get("verifiedControls", {}) if type(candidate) is dict else {}
    if not _native(controls, {
        "documentAndGitEnvelope": "PASS x3",
        "providerFreeHostiles": "PASS 40 x3",
        "liveTaskDefinitionRederivation": "PASS",
        "definitionCount": 41,
        "unreadableDefinitionCount": 0,
        "relevantDefinitionCount": 6,
    }):
        raise Phase14Error("R37_CONTROLS_INVALID")
    receipt = doc.get("durableReviewReceipt", {})
    if receipt.get("status") != "ACCEPT_CANDIDATE_ONLY_ZERO_AUTHORITY" or receipt.get("sha256") != "40893F70E26A6137E45A1426547ACD1904752B6A3E2F44A76E9D9FF40A53C52C":
        raise Phase14Error("DURABLE_REVIEW_RECEIPT_INVALID")
    review = doc.get("independentReview", {})
    if review.get("routeId") != "fleet-r62-mlv-r37-task-definitions-fable" or review.get("verdict") != "ACCEPT" or review.get("scope") != "candidate-only":
        raise Phase14Error("INDEPENDENT_REVIEW_INVALID")
    if review.get("model") != "claude-fable-5" or review.get("effort") != "max" or review.get("role") != "coordinator":
        raise Phase14Error("REVIEW_PROFILE_INVALID")
    boundary = doc.get("acceptedBoundary", {})
    expected_boundary = {
        "currentWindowsTaskDefinitionsCompleteForExactQuery": True,
        "currentRelevantBoundedHistoryCompleteForExactQuery": True,
        "allSixRelevantTasksClassifiedAsSeparateGpuBenchFamily": True,
        "mlvUniversalControlInstalled": False,
        "currentClosedGateProof": False,
        "launcherInventoryComplete": False,
        "actionGraphComplete": False,
        "semanticCompletenessClaimed": False,
        "projectOwnerDisposition": False,
        "adoption": False,
    }
    if not _native(boundary, expected_boundary):
        raise Phase14Error("ACCEPTED_BOUNDARY_INVALID")
    treatment = doc.get("ledgerTreatment", {})
    if treatment.get("counts") != COUNTS or treatment.get("mlvDispositionRemains") != "DISTINGUISH":
        raise Phase14Error("LEDGER_TREATMENT_INVALID")
    if treatment.get("ledgerModified") is not False or treatment.get("specificationsModified") is not False:
        raise Phase14Error("POLICY_MUTATION_OVERCLAIM")
    authority = doc.get("authority")
    if type(authority) is not dict or set(authority) != AUTHORITY_KEYS or any(type(v) is not bool or v is not False for v in authority.values()):
        raise Phase14Error("AUTHORITY_OVERCLAIM")


def verify_policy(treeish: str) -> None:
    if _oid(treeish, LEDGER) != LEDGER_OID or _oid(treeish, MANIFEST) != MANIFEST_OID:
        raise Phase14Error("FROZEN_POLICY_DRIFT")
    ledger = load_json(_blob(treeish, LEDGER))
    if ledger.get("summary", {}).get("counts") != COUNTS or ledger.get("summary", {}).get("fleetAdoptionClaim") is not False:
        raise Phase14Error("LEDGER_DRIFT")
    phase13_specs = str(_git(["ls-tree", "-r", "--name-only", PHASE13, "specs"], text=True)).splitlines()
    current_tree = PHASE13 if treeish == ":" else treeish
    current_specs = str(_git(["ls-tree", "-r", "--name-only", current_tree, "specs"], text=True)).splitlines()
    if phase13_specs != current_specs or any(_oid(current_tree, path) != _oid(PHASE13, path) for path in phase13_specs):
        raise Phase14Error("SPEC_DRIFT")


def verify_workflow(treeish: str) -> None:
    workflow = _blob(treeish, ".github/workflows/disposition-intake.yml").decode("utf-8", errors="strict")
    required = (
        f"python tools/check_phase13_integration.py --treeish {PHASE13}",
        'test_phase14_integration.py" -v',
        "python tools/check_phase14_integration.py --treeish HEAD",
    )
    if any(workflow.count(command) != 1 for command in required):
        raise Phase14Error("WORKFLOW_ROUTING_INVALID")


def verify(treeish: str) -> None:
    if _tuple(PHASE13) != (PHASE13_TREE, [PHASE13_PARENT]):
        raise Phase14Error("PHASE13_PROVENANCE_INVALID")
    if treeish == ":":
        head = str(_git(["rev-parse", "HEAD"], text=True)).strip()
        if head != PHASE13:
            raise Phase14Error("STAGED_PARENT_MISMATCH")
    elif _tuple(treeish)[1] != [PHASE13]:
        raise Phase14Error("PHASE14_PARENT_MISMATCH")
    if _changed_paths(PHASE13, treeish) != INTEGRATION_PATHS:
        raise Phase14Error("INTEGRATION_SCOPE_MISMATCH")
    verify_artifact(treeish)
    verify_policy(treeish)
    verify_workflow(treeish)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--treeish", default="HEAD")
    args = parser.parse_args()
    try:
        verify(args.treeish)
    except Phase14Error as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"PASS: Phase14 MLV task definitions exact; ledger=0/5/4; artifact_sha256={ARTIFACT_SHA256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
