#!/usr/bin/env python3
"""Verify the forward-only Phase11 closure of the frozen Phase10 review shape."""

from __future__ import annotations

import argparse
from collections import Counter
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PHASE10_COMMIT = "940c790eedd118736ff0207c1b7dc407d5643802"
PHASE10_TREE = "9fe8b86a9408917a01e08564454e6c2a47b9952f"
PHASE10_PARENT = "18b95fd82f92920117c8f0f432ae8e9bc5e8ffc8"
PHASE10_RECEIPT_PATH = "adoption/phase10/r26-local-candidate-review-receipts.json"
PHASE10_RECEIPT_BLOB = "2f5d543754d35eb6e2f8143465e3ea2a1d1abffc"
PHASE10_RECEIPT_BYTES = 18080
PHASE10_RECEIPT_SHA256 = "6c9225317356d2975d97c75d3b4732cfd0f0a8bf14e78485110fd88bacecfcda"
PHASE10_CANONICAL_BYTES = 14830
PHASE10_CANONICAL_SHA256 = "220ba2939dfebbec9e9145cde442c8f83346a84d7b19541e42005617d2816386"
CLOSURE_PATH = "adoption/phase11/r26-phase10-review-shape-closure.json"
CLOSURE_BLOB = "02af11ad375c6de6fffc3cc1f88bd1e0d3a477ee"
CLOSURE_BYTES = 3234
CLOSURE_SHA256 = "f7d82f131d353497ddf66cd36a65b2fa430b5178cc30ca8a52face785eb02aca"
LEDGER_PATH = "adoption/universal-token-control-r26.json"
MANIFEST_PATH = "manifests/universal-provider-control-reconciliation-r26.json"
EXPECTED_COUNTS = {"ADOPT": 0, "DISTINGUISH": 5, "MISSING": 0, "REJECT": 0, "STALE": 4}
SUPERSEDED_PHASE10_COMMIT = "4d8482034c8ebc5eb6b7fdd5611de1b6d282d4c5"
PHASE11_PROOF_PATHS = {
    "adoption/phase11/README.md",
    CLOSURE_PATH,
    "tests/test_phase11_integration.py",
    "tools/check_phase11_integration.py",
}
PREDECESSOR_CHECKERS = {
    "tools/check_phase2_disposition_batch.py": "ALLOWED_PHASE2_PATHS",
    "tools/check_phase3_disposition_batch.py": "ALLOWED_PHASE3_PATHS",
    "tools/check_phase5_stale_reconciliation.py": "ALLOWED_PHASE5_PATHS",
    "tools/check_phase6_candidate_reviews.py": "ALLOWED_PATHS",
    "tools/check_phase7_owner_publication_requests.py": "ALLOWED_PHASE7_PATHS",
}
FORWARD_CHECKERS = {
    "tools/check_phase8_integration.py",
    "tools/check_phase9_integration.py",
    "tools/check_phase10_integration.py",
}
EXPECTED_INTEGRATION_PATHS = PHASE11_PROOF_PATHS | {
    ".github/workflows/disposition-intake.yml",
    *PREDECESSOR_CHECKERS,
    *FORWARD_CHECKERS,
}
EXPECTED_MUTATIONS = [
    {"id": "EXTRA_REVIEW_KEY", "target": "reviews[*]", "expectedResult": "REJECT"},
    {"id": "EXTRA_EXECUTION_EVIDENCE_KEY", "target": "reviews[*].executionEvidence[*]", "expectedResult": "REJECT"},
    {"id": "FORGED_MLV_RESULT", "target": "reviews[mlv-app].executionEvidence[0].result", "expectedResult": "REJECT"},
    {"id": "FORGED_CLOUDVORE_RESULT", "target": "reviews[cloudvore].executionEvidence[*].result", "expectedResult": "REJECT"},
    {"id": "FORGED_R8_SUITE_PATH", "target": "reviews[dng-auto-processor].independentExecutionEvidence[*].path", "expectedResult": "REJECT"},
    {"id": "WIDENED_REVIEW_SCOPE", "target": "reviews[*].reviewScope", "expectedResult": "REJECT"},
    {"id": "MLV_INVENTORY_COMPLETE_TRUE", "target": "reviews[mlv-app].semanticFindings.inventoryComplete", "expectedResult": "REJECT"},
    {"id": "MLV_DISPOSITION_CREDIT_TRUE", "target": "reviews[mlv-app].semanticFindings.dispositionCredit", "expectedResult": "REJECT"},
    {"id": "OMITTED_MLV_ARTIFACT_ROW", "target": "reviews[mlv-app].artifacts", "expectedResult": "REJECT"},
    {"id": "OMITTED_R8_CRITICAL_ARTIFACT_ROW", "target": "reviews[dng-auto-processor].criticalArtifacts", "expectedResult": "REJECT"},
    {"id": "INJECTED_SUPERSEDED_PHASE10_PROVENANCE", "target": "reviews[*]", "forbiddenCommit": SUPERSEDED_PHASE10_COMMIT, "expectedResult": "REJECT"},
]
EXPECTED_AUTHORITY_KEYS = {
    "projectDisposition", "projectAdoption", "fleetAdoption", "runtime", "activation",
    "provider", "authentication", "scheduler", "gate", "installation", "apply",
    "privilegedPreview", "pushMergePublish",
}
SHA40 = re.compile(r"[0-9a-f]{40}")


class Phase11Error(ValueError):
    pass


def _load_phase10_module() -> Any:
    path = ROOT / "tools" / "check_phase10_integration.py"
    spec = importlib.util.spec_from_file_location("phase10_for_phase11", path)
    if spec is None or spec.loader is None:
        raise Phase11Error("PHASE10_CHECKER_UNAVAILABLE")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


P10 = _load_phase10_module()


def _clean_git_env() -> dict[str, str]:
    environment = os.environ.copy()
    for key in tuple(environment):
        if key in {
            "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_OBJECT_DIRECTORY",
            "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_REPLACE_REF_BASE", "GIT_INDEX_FILE",
            "GIT_NAMESPACE", "GIT_CEILING_DIRECTORIES", "GIT_EXEC_PATH",
        } or key.startswith("GIT_CONFIG"):
            environment.pop(key, None)
    return environment


def _git(args: list[str], *, text: bool = False, error: str = "GIT_OBJECT_UNAVAILABLE") -> bytes | str:
    run = subprocess.run(
        ["git", *args], cwd=ROOT, env=_clean_git_env(), check=False, capture_output=True,
        text=text, encoding="utf-8" if text else None,
    )
    if run.returncode != 0:
        raise Phase11Error(error)
    return run.stdout


def _blob_spec(treeish: str, path: str) -> str:
    return f":{path}" if treeish == ":" else f"{treeish}:{path}"


def _blob(treeish: str, path: str) -> bytes:
    return _git(["show", _blob_spec(treeish, path)], error="GIT_BLOB_UNAVAILABLE")  # type: ignore[return-value]


def _oid(treeish: str, path: str) -> str:
    value = str(_git(["rev-parse", _blob_spec(treeish, path)], text=True, error="GIT_BLOB_OID_UNAVAILABLE")).strip()
    if SHA40.fullmatch(value) is None:
        raise Phase11Error("GIT_BLOB_OID_INVALID")
    return value


def _commit_tuple(commit: str) -> tuple[str, list[str]]:
    value = str(_git(["show", "-s", "--format=%T%n%P", commit], text=True, error="COMMIT_UNAVAILABLE"))
    lines = value.splitlines()
    if len(lines) != 2 or SHA40.fullmatch(lines[0]) is None:
        raise Phase11Error("COMMIT_INVALID")
    parents = lines[1].split() if lines[1] else []
    if any(SHA40.fullmatch(parent) is None for parent in parents):
        raise Phase11Error("COMMIT_INVALID")
    return lines[0], parents


def _changed_paths(base: str, treeish: str) -> set[str]:
    args = ["diff", "--cached", "--name-only", base] if treeish == ":" else ["diff", "--name-only", f"{base}..{treeish}"]
    return set(str(_git(args, text=True, error="INTEGRATION_DIFF_UNAVAILABLE")).splitlines())


def _tree_paths(treeish: str, prefix: str) -> set[str]:
    if treeish == ":":
        rows = str(_git(["ls-files", "--stage", "--", prefix], text=True)).splitlines()
        return {row.split("\t", 1)[1] for row in rows if "\t" in row}
    return set(str(_git(["ls-tree", "-r", "--name-only", treeish, "--", prefix], text=True)).splitlines())


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise Phase11Error("DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def load_json(raw: bytes) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=_reject_duplicate_keys)
    except Phase11Error:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Phase11Error("JSON_INVALID") from exc
    if not isinstance(value, dict):
        raise Phase11Error("JSON_ROOT_INVALID")
    return value


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _exact_native(actual: Any, expected: Any, path: str = "$") -> None:
    if type(actual) is not type(expected):
        raise Phase11Error(f"PHASE10_RECEIPT_NATIVE_EXACT_MISMATCH:{path}:TYPE")
    if isinstance(expected, dict):
        if set(actual) != set(expected):
            raise Phase11Error(f"PHASE10_RECEIPT_NATIVE_EXACT_MISMATCH:{path}:KEYS")
        for key in expected:
            _exact_native(actual[key], expected[key], f"{path}.{key}")
        return
    if isinstance(expected, list):
        if len(actual) != len(expected):
            raise Phase11Error(f"PHASE10_RECEIPT_NATIVE_EXACT_MISMATCH:{path}:LENGTH")
        for index, (actual_item, expected_item) in enumerate(zip(actual, expected, strict=True)):
            _exact_native(actual_item, expected_item, f"{path}[{index}]")
        return
    if actual != expected:
        raise Phase11Error(f"PHASE10_RECEIPT_NATIVE_EXACT_MISMATCH:{path}:VALUE")


def canonical_phase10_receipt() -> dict[str, Any]:
    raw = _blob(PHASE10_COMMIT, PHASE10_RECEIPT_PATH)
    if _oid(PHASE10_COMMIT, PHASE10_RECEIPT_PATH) != PHASE10_RECEIPT_BLOB:
        raise Phase11Error("PHASE10_RECEIPT_BLOB_MISMATCH")
    if len(raw) != PHASE10_RECEIPT_BYTES or hashlib.sha256(raw).hexdigest() != PHASE10_RECEIPT_SHA256:
        raise Phase11Error("PHASE10_RECEIPT_BYTE_TUPLE_MISMATCH")
    batch = load_json(raw)
    semantic = _canonical_bytes(batch)
    if len(semantic) != PHASE10_CANONICAL_BYTES or hashlib.sha256(semantic).hexdigest() != PHASE10_CANONICAL_SHA256:
        raise Phase11Error("PHASE10_RECEIPT_CANONICAL_DIGEST_MISMATCH")
    return batch


def verify_phase10_receipt_closed(batch: dict[str, Any]) -> None:
    expected = canonical_phase10_receipt()
    semantic = _canonical_bytes(batch)
    if len(semantic) != PHASE10_CANONICAL_BYTES or hashlib.sha256(semantic).hexdigest() != PHASE10_CANONICAL_SHA256:
        raise Phase11Error("PHASE10_RECEIPT_CANONICAL_DIGEST_MISMATCH")
    _exact_native(batch, expected)


def _expected_closure() -> dict[str, Any]:
    return {
        "schema": "fleet-r26-phase11-phase10-review-shape-closure/v1",
        "status": "AUTHOR_CONFLICTED_INDEPENDENT_REVIEW_REQUIRED",
        "frozenPhase10": {
            "commit": PHASE10_COMMIT, "tree": PHASE10_TREE, "parent": PHASE10_PARENT,
            "receiptPath": PHASE10_RECEIPT_PATH, "receiptGitBlobOid": PHASE10_RECEIPT_BLOB,
            "receiptBytes": PHASE10_RECEIPT_BYTES, "receiptSha256": PHASE10_RECEIPT_SHA256,
            "receiptCanonicalSemanticBytes": PHASE10_CANONICAL_BYTES,
            "receiptCanonicalSemanticSha256": PHASE10_CANONICAL_SHA256,
        },
        "closure": {
            "method": "RECURSIVE_EXACT_NATIVE_VALUE_AND_CLOSED_KEY_SET_MATCH_PLUS_CANONICAL_SHA256",
            "objectKeySetsClosed": True, "arrayMembershipAndOrderClosed": True,
            "nativeJsonTypesExact": True, "scalarValuesExact": True,
            "forbiddenMutationCount": 11, "forbiddenMutations": EXPECTED_MUTATIONS,
            "coordinatedMutationPolicy": "ANY_ONE_OR_MORE_MUTATIONS_REJECT_BEFORE_LOCAL_SUBJECT_OR_AUTHORITY_CREDIT",
            "priorAcceptedMutationCredit": False,
        },
        "frozenDisposition": {
            "canonicalLedgerCounts": EXPECTED_COUNTS, "ledgerStatusChangeAuthorized": False,
            "specificationChangeAuthorized": False, "candidateEvidenceCreditChanged": False,
        },
        "authority": {key: False for key in EXPECTED_AUTHORITY_KEYS},
    }


def verify_closure_artifact(treeish: str) -> dict[str, Any]:
    raw = _blob(treeish, CLOSURE_PATH)
    if _oid(treeish, CLOSURE_PATH) != CLOSURE_BLOB:
        raise Phase11Error("CLOSURE_BLOB_OID_MISMATCH")
    if len(raw) != CLOSURE_BYTES or hashlib.sha256(raw).hexdigest() != CLOSURE_SHA256:
        raise Phase11Error("CLOSURE_BYTE_TUPLE_MISMATCH")
    closure = load_json(raw)
    _exact_native(closure, _expected_closure(), "$closure")
    if set(closure["authority"]) != EXPECTED_AUTHORITY_KEYS or any(value is not False for value in closure["authority"].values()):
        raise Phase11Error("CLOSURE_AUTHORITY_OVERCLAIM")
    if Counter(row["expectedResult"] for row in closure["closure"]["forbiddenMutations"]) != Counter({"REJECT": 11}):
        raise Phase11Error("FORBIDDEN_MUTATION_SET_INVALID")
    return closure


def verify_phase10_source() -> None:
    if _commit_tuple(PHASE10_COMMIT) != (PHASE10_TREE, [PHASE10_PARENT]):
        raise Phase11Error("PHASE10_SOURCE_OBJECT_MISMATCH")
    if _changed_paths(PHASE10_PARENT, PHASE10_COMMIT) != P10.EXPECTED_INTEGRATION_PATHS:
        raise Phase11Error("PHASE10_SOURCE_SCOPE_MISMATCH")
    batch = canonical_phase10_receipt()
    verify_phase10_receipt_closed(batch)
    P10.verify_receipt_shape(copy.deepcopy(batch))


def verify_forward_allowlists(treeish: str) -> None:
    for path, attribute in PREDECESSOR_CHECKERS.items():
        source = P10._assignment_set(PHASE10_COMMIT, path, attribute)
        if P10._assignment_set(treeish, path, "PHASE11_INTEGRATION_PATHS") != PHASE11_PROOF_PATHS:
            raise Phase11Error("PHASE11_ALLOWLIST_SCOPE_DRIFT")
        if P10._assignment_set(treeish, path, attribute) != source | PHASE11_PROOF_PATHS:
            raise Phase11Error("PREDECESSOR_ALLOWLIST_UNION_MISMATCH")
    for path in FORWARD_CHECKERS:
        if P10._assignment_set(treeish, path, "PHASE11_FORWARD_PATHS") != EXPECTED_INTEGRATION_PATHS:
            raise Phase11Error("FORWARD_SCOPE_DRIFT")


def verify_frozen_doctrine(treeish: str) -> None:
    for path in (LEDGER_PATH, MANIFEST_PATH):
        if _oid(treeish, path) != _oid(PHASE10_COMMIT, path):
            raise Phase11Error("FROZEN_DOCTRINE_ARTIFACT_DRIFT")
    source_specs = _tree_paths(PHASE10_COMMIT, "specs")
    if _tree_paths(treeish, "specs") != source_specs:
        raise Phase11Error("SPEC_SET_DRIFT")
    for path in source_specs:
        if _oid(treeish, path) != _oid(PHASE10_COMMIT, path):
            raise Phase11Error("SPEC_BLOB_DRIFT")
    ledger = load_json(_blob(treeish, LEDGER_PATH))
    if ledger.get("summary", {}).get("counts") != EXPECTED_COUNTS or ledger.get("summary", {}).get("fleetAdoptionClaim") is not False:
        raise Phase11Error("LEDGER_STATUS_ADVANCE")


def verify_workflow(treeish: str) -> None:
    workflow = _blob(treeish, ".github/workflows/disposition-intake.yml").decode("utf-8", errors="strict")
    required = ('test_phase11_integration.py" -v', "check_phase11_integration.py --treeish HEAD")
    if any(item not in workflow for item in required):
        raise Phase11Error("WORKFLOW_PHASE11_MISSING")


def verify_integration(treeish: str) -> None:
    verify_phase10_source()
    if treeish == ":":
        head = str(_git(["rev-parse", "HEAD"], text=True, error="HEAD_UNAVAILABLE")).strip()
        if head != PHASE10_COMMIT:
            raise Phase11Error("STAGED_BASE_MISMATCH")
    elif _commit_tuple(treeish)[1] != [PHASE10_COMMIT]:
        raise Phase11Error("INTEGRATION_PARENT_MISMATCH")
    if _changed_paths(PHASE10_COMMIT, treeish) != EXPECTED_INTEGRATION_PATHS:
        raise Phase11Error("INTEGRATION_SCOPE_MISMATCH")
    if _oid(treeish, PHASE10_RECEIPT_PATH) != PHASE10_RECEIPT_BLOB:
        raise Phase11Error("PHASE10_RECEIPT_DRIFT")
    batch = load_json(_blob(treeish, PHASE10_RECEIPT_PATH))
    verify_phase10_receipt_closed(batch)
    P10.verify_receipt_shape(copy.deepcopy(batch))
    # The Phase 10 publication state is point-in-time receipt evidence.  Later
    # phases rederive the immutable commit/tree/parent/artifact objects without
    # requiring that the reviewed branch remain unpublished forever.
    P10.verify_local_subjects(
        copy.deepcopy(batch), rederive_mutable_worktree_state=False
    )
    verify_closure_artifact(treeish)
    verify_frozen_doctrine(treeish)
    verify_forward_allowlists(treeish)
    verify_workflow(treeish)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--treeish", default="HEAD")
    args = parser.parse_args()
    try:
        verify_integration(args.treeish)
    except (Phase11Error, P10.Phase10Error) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(
        "PASS: Phase 11 closes the frozen Phase10 receipt recursively over exact keys, native "
        "types, ordered sets, and values; all dispositions, specs, and authority remain frozen"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
