#!/usr/bin/env python3
"""Verify the zero-authority Phase 13 DNG installation-evidence publication."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PHASE12 = "990906b6ea861ca579e1336bcfe8f17dd80c83ae"
PHASE12_TREE = "78cde12c2108e257823c183037bc4d05a72f3649"
PHASE12_PARENT = "1bf5ad616c6a2c9200ff34e03c749da0997475c2"
PHASE12_ARTIFACT = "adoption/phase12/r26-current-master-review-integration.json"
PHASE12_ARTIFACT_OID = "c674030d27db28313588745b879e665162e31948"
ARTIFACT = "adoption/phase13/r26-dng-install-evidence-publication.json"
ARTIFACT_SHA256 = "905C7B16C2636C507C0B52910FE18734F8C77A81374BEB2519988E3A06BDD369"
LEDGER = "adoption/universal-token-control-r26.json"
LEDGER_OID = "2f1808e8df35e6d1bae98f83aab378d93a0c3228"
MANIFEST = "manifests/universal-provider-control-reconciliation-r26.json"
MANIFEST_OID = "898385fb82fbbe9946f937f0486142f4733d03fe"
COUNTS = {"ADOPT": 0, "DISTINGUISH": 5, "MISSING": 0, "REJECT": 0, "STALE": 4}
INTEGRATION_PATHS = {
    ".github/workflows/disposition-intake.yml",
    "adoption/phase13/README.md",
    ARTIFACT,
    "tests/test_phase12_integration.py",
    "tests/test_phase13_integration.py",
    "tools/check_phase13_integration.py",
}
AUTHORITY_KEYS = {
    "projectDisposition", "fleetAdoption", "installation", "runtime",
    "providerExecution", "taskOrGateMutation", "pushOrMerge",
}


class Phase13Error(ValueError):
    pass


def _pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    folded: set[str] = set()
    for key, value in items:
        if not isinstance(key, str) or key.casefold() in folded:
            raise Phase13Error("DUPLICATE_OR_CASE_COLLIDING_KEY")
        folded.add(key.casefold())
        out[key] = value
    return out


def load_json(raw: bytes) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Phase13Error("JSON_INVALID") from exc
    if type(value) is not dict:
        raise Phase13Error("JSON_ROOT_INVALID")
    return value


def _git(args: list[str], *, text: bool = False) -> bytes | str:
    run = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, check=False,
                         text=text, encoding="utf-8" if text else None)
    if run.returncode != 0:
        raise Phase13Error("GIT_COMMAND_FAILED")
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
        raise Phase13Error("COMMIT_TUPLE_INVALID")
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
        return set(value) == set(expected) and all(_native(value[k], v) for k, v in expected.items())
    if type(expected) is list:
        return len(value) == len(expected) and all(_native(a, b) for a, b in zip(value, expected))
    return value == expected


def verify_artifact(treeish: str) -> None:
    raw = _blob(treeish, ARTIFACT)
    if hashlib.sha256(raw).hexdigest().upper() != ARTIFACT_SHA256:
        raise Phase13Error("ARTIFACT_HASH_MISMATCH")
    doc = load_json(raw)
    if doc.get("schema") != "fleet-r26-dng-install-evidence-publication/v1" or doc.get("status") != "CANDIDATE_ZERO_AUTHORITY":
        raise Phase13Error("ARTIFACT_IDENTITY_INVALID")
    if doc.get("trackedDisposition", {}).get("disposition") != "DISTINGUISH":
        raise Phase13Error("DNG_DISPOSITION_DRIFT")
    if doc.get("ledgerTreatment", {}).get("counts") != COUNTS or doc["ledgerTreatment"].get("dngDispositionRemains") != "DISTINGUISH":
        raise Phase13Error("LEDGER_TREATMENT_INVALID")
    if doc["ledgerTreatment"].get("ledgerModified") is not False or doc["ledgerTreatment"].get("specificationsModified") is not False:
        raise Phase13Error("POLICY_MUTATION_OVERCLAIM")
    if doc.get("installation", {}).get("r21Receipt", {}).get("status") != "INSTALLED_VERIFIED_ADOPTION_CREDIT_FALSE":
        raise Phase13Error("INSTALLATION_STATUS_INVALID")
    ticks = doc["installation"].get("initialQualifyingTicks", {})
    if type(ticks.get("rows")) is not int or ticks.get("rows") != 2 or type(ticks.get("complete")) is not bool or ticks.get("complete") is not False:
        raise Phase13Error("TICK_CREDIT_INVALID")
    reviews = doc.get("independentReviews")
    if type(reviews) is not list or [r.get("routeId") for r in reviews if type(r) is dict] != ["fleet-r59-dng-r22-install-evidence-opus", "fleet-r60-dng-r23-install-evidence-sonnet"]:
        raise Phase13Error("REVIEW_SET_INVALID")
    if any(r.get("verdict") != "ACCEPT" or r.get("scope") != "candidate-only" for r in reviews):
        raise Phase13Error("REVIEW_VERDICT_INVALID")
    authority = doc.get("authority")
    if type(authority) is not dict or set(authority) != AUTHORITY_KEYS or any(type(v) is not bool or v is not False for v in authority.values()):
        raise Phase13Error("AUTHORITY_OVERCLAIM")


def verify_policy(treeish: str) -> None:
    if _oid(treeish, LEDGER) != LEDGER_OID or _oid(treeish, MANIFEST) != MANIFEST_OID:
        raise Phase13Error("FROZEN_POLICY_DRIFT")
    ledger = load_json(_blob(treeish, LEDGER))
    if ledger.get("summary", {}).get("counts") != COUNTS or ledger.get("summary", {}).get("fleetAdoptionClaim") is not False:
        raise Phase13Error("LEDGER_DRIFT")
    phase12_specs = str(_git(["ls-tree", "-r", "--name-only", PHASE12, "specs"], text=True)).splitlines()
    current_tree = PHASE12 if treeish == ":" else treeish
    current_specs = str(_git(["ls-tree", "-r", "--name-only", current_tree, "specs"], text=True)).splitlines()
    if phase12_specs != current_specs or any(_oid(current_tree, path) != _oid(PHASE12, path) for path in phase12_specs):
        raise Phase13Error("SPEC_DRIFT")


def verify_workflow(treeish: str) -> None:
    workflow = _blob(treeish, ".github/workflows/disposition-intake.yml").decode("utf-8", errors="strict")
    required = (
        f"python tools/check_phase2_disposition_batch.py --treeish {PHASE12}",
        f"python tools/check_phase3_disposition_batch.py --treeish {PHASE12}",
        f"python tools/check_phase5_stale_reconciliation.py --treeish {PHASE12}",
        f"python tools/check_phase12_integration.py --treeish {PHASE12}",
        'test_phase13_integration.py" -v',
        "python tools/check_phase13_integration.py --treeish HEAD",
    )
    if any(workflow.count(command) != 1 for command in required):
        raise Phase13Error("WORKFLOW_ROUTING_INVALID")


def verify(treeish: str) -> None:
    if _tuple(PHASE12) != (PHASE12_TREE, [PHASE12_PARENT]) or _oid(PHASE12, PHASE12_ARTIFACT) != PHASE12_ARTIFACT_OID:
        raise Phase13Error("PHASE12_PROVENANCE_INVALID")
    if treeish == ":":
        head = str(_git(["rev-parse", "HEAD"], text=True)).strip()
        if head != PHASE12:
            raise Phase13Error("STAGED_PARENT_MISMATCH")
    elif _tuple(treeish)[1] != [PHASE12]:
        raise Phase13Error("PHASE13_PARENT_MISMATCH")
    if _changed_paths(PHASE12, treeish) != INTEGRATION_PATHS:
        raise Phase13Error("INTEGRATION_SCOPE_MISMATCH")
    verify_artifact(treeish)
    verify_policy(treeish)
    verify_workflow(treeish)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--treeish", default="HEAD")
    args = parser.parse_args()
    try:
        verify(args.treeish)
    except Phase13Error as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"PASS: Phase13 DNG install evidence exact; ledger=0/5/4; artifact_sha256={ARTIFACT_SHA256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
