#!/usr/bin/env python3
"""Verify the frozen R26 phase-2 disposition-intake blocker batch."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BATCH_PATH = "adoption/phase2/r26-project-disposition-intake.json"
LEDGER_PATH = "adoption/universal-token-control-r26.json"
SCHEMA = "fleet-r26-disposition-intake-batch/v1"
IMPLEMENTATION_COMMIT = "490953a4496bab6977d554acb1828d40f4ac92d0"
IMPLEMENTATION_TREE = "c97a7e8a5df36be11180201d93d29b28ea8b17a1"
PACKET_COMMIT = "5ab5bf14ac900ddb2410d7e36d265cde1db76461"
PACKET_TREE = "a305aa59cac5d7178679efa1dbc0892383fca382"
CENSUS_COMMIT = "76dd97d3110668b6f1391aabee3e270801be00ad"
R26_CANDIDATE = "e70a044f31dd2f43ab7c716d63a4eb89318c61b6"
R26_MERGE = "909f769d02e8412e51e28e242cfa8d00dadc9a3d"
DIMENSIONS = {"model", "effort", "role", "review", "quality", "functionality"}
PROJECT_IDS = {
    "adobe-ingester",
    "adversarialllm",
    "agent-bridge",
    "airmypc",
    "cloudvore",
    "conjugal",
    "mlv-app",
    "salesforce-tools",
}
ALLOWED_PHASE2_PATHS = {
    ".github/workflows/disposition-intake.yml",
    "adoption/README.md",
    "adoption/phase2/README.md",
    BATCH_PATH,
    "tests/test_phase2_disposition_batch.py",
    "tests/test_adoption_ledger.py",
    "tools/check_adoption_ledger.py",
    "tools/check_phase2_disposition_batch.py",
}
PHASE2_SCOPE_FREEZE_COMMIT = "082f631c7b474211bbe8ecbc783a4fd9cdd2ada0"
OWNER_EVIDENCE_REQUIREMENTS = [
    "PROJECT_OWNED_COMMIT_AND_GIT_BLOB_BINDING_R26_E70A044_AND_MERGE_909F769",
    "CURRENT_EXPLICIT_ADOPT_DISTINGUISH_OR_REJECT",
    "PINNED_NON_REGRESSION_EVIDENCE_MODEL_EFFORT_ROLE_REVIEW_QUALITY_FUNCTIONALITY",
    "RUNTIME_EVIDENCE_ONLY_IF_PROJECT_OWNED_NO_INFERENCE_FROM_DOCTRINE",
]
SHA_PATTERN = re.compile(r"[0-9a-f]{40,64}")


class BatchError(ValueError):
    pass


def _pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in values:
        if key in result:
            raise BatchError("DUPLICATE_KEY")
        result[key] = value
    return result


def load_json(raw: bytes) -> dict[str, Any]:
    try:
        value = json.loads(raw, object_pairs_hook=_pairs)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise BatchError("JSON_INVALID") from exc
    if not isinstance(value, dict):
        raise BatchError("JSON_ROOT_INVALID")
    return value


def _git(args: list[str], *, text: bool = False, error: str = "GIT_OBJECT_UNAVAILABLE") -> bytes | str:
    run = subprocess.run(
        ["git", *args], cwd=ROOT, check=False, capture_output=True,
        text=text, encoding="utf-8" if text else None,
    )
    if run.returncode != 0:
        raise BatchError(error)
    return run.stdout


def _blob_spec(treeish: str, path: str) -> str:
    return f":{path}" if treeish == ":" else f"{treeish}:{path}"


def _blob(treeish: str, path: str) -> bytes:
    return _git(["show", _blob_spec(treeish, path)], error="GIT_BLOB_UNAVAILABLE")  # type: ignore[return-value]


def _oid(treeish: str, path: str) -> str:
    value = _git(
        ["rev-parse", _blob_spec(treeish, path)], text=True,
        error="GIT_BLOB_OID_UNAVAILABLE",
    ).strip()
    if SHA_PATTERN.fullmatch(value) is None:
        raise BatchError("GIT_BLOB_OID_INVALID")
    return value


def _commit_tuple(commit: str) -> tuple[str, list[str]]:
    value = _git(
        ["show", "-s", "--format=%T%n%P", commit], text=True,
        error="COMMIT_UNAVAILABLE",
    )
    lines = value.splitlines()
    if len(lines) != 2 or SHA_PATTERN.fullmatch(lines[0]) is None:
        raise BatchError("COMMIT_INVALID")
    return lines[0], lines[1].split() if lines[1] else []


def _is_ancestor(ancestor: str, descendant: str) -> bool:
    run = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=ROOT, check=False, capture_output=True,
    )
    return run.returncode == 0


def _changed_paths(treeish: str) -> set[str]:
    descendant = "HEAD" if treeish == ":" else treeish
    scope_tip = (
        PHASE2_SCOPE_FREEZE_COMMIT
        if _is_ancestor(PHASE2_SCOPE_FREEZE_COMMIT, descendant)
        else descendant
    )
    args = ["diff", "--name-only", f"{PACKET_COMMIT}..{scope_tip}"]
    return set(_git(args, text=True, error="PHASE2_DIFF_UNAVAILABLE").splitlines())


def _exact_keys(value: Any, keys: set[str], code: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise BatchError(code)
    return value


def _ledger_rows() -> dict[str, dict[str, Any]]:
    ledger = load_json(_blob(IMPLEMENTATION_COMMIT, LEDGER_PATH))
    projects = ledger.get("projects")
    if not isinstance(projects, list):
        raise BatchError("FROZEN_LEDGER_INVALID")
    rows = {
        row.get("projectId"): row
        for row in projects
        if isinstance(row, dict) and row.get("status") in {"STALE", "MISSING"}
    }
    if set(rows) != PROJECT_IDS:
        raise BatchError("FROZEN_LEDGER_PROJECT_SET_INVALID")
    return rows


def _verify_frozen_base(base: Any, treeish: str) -> None:
    base = _exact_keys(
        base,
        {
            "implementationCommit", "implementationTree", "reviewPacketCommit",
            "reviewPacketTree", "censusCommit", "r26Candidate", "r26Merge",
        },
        "FROZEN_BASE_INVALID",
    )
    expected = {
        "implementationCommit": IMPLEMENTATION_COMMIT,
        "implementationTree": IMPLEMENTATION_TREE,
        "reviewPacketCommit": PACKET_COMMIT,
        "reviewPacketTree": PACKET_TREE,
        "censusCommit": CENSUS_COMMIT,
        "r26Candidate": R26_CANDIDATE,
        "r26Merge": R26_MERGE,
    }
    if base != expected:
        raise BatchError("FROZEN_BASE_MISMATCH")
    implementation_tree, implementation_parents = _commit_tuple(IMPLEMENTATION_COMMIT)
    packet_tree, packet_parents = _commit_tuple(PACKET_COMMIT)
    if implementation_tree != IMPLEMENTATION_TREE or implementation_parents != [CENSUS_COMMIT]:
        raise BatchError("IMPLEMENTATION_OBJECT_MISMATCH")
    if packet_tree != PACKET_TREE or packet_parents != [IMPLEMENTATION_COMMIT]:
        raise BatchError("PACKET_OBJECT_MISMATCH")
    descendant = "HEAD" if treeish == ":" else treeish
    if not _is_ancestor(PACKET_COMMIT, descendant):
        raise BatchError("FROZEN_PACKET_NOT_ANCESTOR")
    changed = _changed_paths(treeish)
    if not changed.issubset(ALLOWED_PHASE2_PATHS):
        raise BatchError("PHASE2_SCOPE_VIOLATION")


def _verify_capture(capture: Any) -> None:
    capture = _exact_keys(
        capture,
        {
            "capturedAt", "machine", "discoveryPolicy", "runtimeInspectionPerformed",
            "networkInspectionPerformed", "dngMutationPerformed", "projectWorktreesCreated",
        },
        "CAPTURE_INVALID",
    )
    if not isinstance(capture["capturedAt"], str) or not capture["capturedAt"]:
        raise BatchError("CAPTURE_TIME_INVALID")
    if capture["machine"] != "ULTRA-MAGNUS":
        raise BatchError("CAPTURE_MACHINE_INVALID")
    if capture["discoveryPolicy"] != "SPEC_POINTERS_AND_DIRECT_CHILD_MATCHES_ONLY_NO_RECURSIVE_SCAN":
        raise BatchError("DISCOVERY_POLICY_INVALID")
    if any(capture[key] is not False for key in (
        "runtimeInspectionPerformed", "networkInspectionPerformed", "dngMutationPerformed"
    )):
        raise BatchError("CAPTURE_AUTHORITY_OVERCLAIM")
    if capture["projectWorktreesCreated"] != 0:
        raise BatchError("PROJECT_WORKTREE_CLAIM_INVALID")


def _verify_dimensions(dimensions: Any, spec_bytes: bytes) -> None:
    if not isinstance(dimensions, dict) or set(dimensions) != DIMENSIONS:
        raise BatchError("DIMENSION_SET_INVALID")
    for dimension, evidence in dimensions.items():
        evidence = _exact_keys(evidence, {"state", "anchors"}, "DIMENSION_EVIDENCE_INVALID")
        if evidence["state"] not in {
            "SPEC_BOUNDARY_ONLY_NOT_CURRENT_R26_EVIDENCE",
            "MISSING_PROJECT_R26_EVIDENCE",
        }:
            raise BatchError("DIMENSION_STATE_INVALID")
        anchors = evidence["anchors"]
        if not isinstance(anchors, list) or any(not isinstance(anchor, str) or not anchor for anchor in anchors):
            raise BatchError("DIMENSION_ANCHORS_INVALID")
        if evidence["state"] == "MISSING_PROJECT_R26_EVIDENCE" and anchors:
            raise BatchError("MISSING_DIMENSION_HAS_ANCHOR")
        if evidence["state"] == "SPEC_BOUNDARY_ONLY_NOT_CURRENT_R26_EVIDENCE" and not anchors:
            raise BatchError("SPEC_BOUNDARY_ANCHOR_MISSING")
        if any(anchor.encode("utf-8") not in spec_bytes for anchor in anchors):
            raise BatchError(f"DIMENSION_ANCHOR_NOT_IN_SPEC:{dimension}")


def _verify_project(project: Any, ledger_row: dict[str, Any]) -> None:
    project = _exact_keys(
        project,
        {
            "priority", "priorityRationale", "projectId", "ledgerStatus", "sourceEvidence",
            "publishedLocation", "boundedDiscovery", "nonRegression", "dispositionOutcome",
            "authority",
        },
        "PROJECT_RECORD_INVALID",
    )
    project_id = project["projectId"]
    if project_id != ledger_row["projectId"] or project["ledgerStatus"] != ledger_row["status"]:
        raise BatchError("PROJECT_LEDGER_STATUS_MISMATCH")
    if not isinstance(project["priority"], int) or project["priority"] < 1:
        raise BatchError("PROJECT_PRIORITY_INVALID")
    if not isinstance(project["priorityRationale"], str) or not project["priorityRationale"]:
        raise BatchError("PROJECT_PRIORITY_RATIONALE_INVALID")

    source = _exact_keys(
        project["sourceEvidence"], {"commit", "path", "gitBlobOid"},
        "SOURCE_EVIDENCE_INVALID",
    )
    ledger_evidence = ledger_row["evidence"]
    if source != {
        "commit": ledger_evidence["commit"],
        "path": ledger_row["specPath"],
        "gitBlobOid": ledger_evidence["gitBlobOid"],
    }:
        raise BatchError("SOURCE_EVIDENCE_LEDGER_MISMATCH")
    if _oid(source["commit"], source["path"]) != source["gitBlobOid"]:
        raise BatchError("SOURCE_EVIDENCE_BLOB_MISMATCH")
    spec_bytes = _blob(source["commit"], source["path"])

    location = _exact_keys(
        project["publishedLocation"], {"host", "repoPath", "remote", "anchors"},
        "PUBLISHED_LOCATION_INVALID",
    )
    if any(value is not None and not isinstance(value, str) for value in (
        location["host"], location["repoPath"], location["remote"]
    )):
        raise BatchError("PUBLISHED_LOCATION_VALUE_INVALID")
    anchors = location["anchors"]
    if not isinstance(anchors, list) or not anchors:
        raise BatchError("PUBLISHED_LOCATION_ANCHORS_INVALID")
    if any(not isinstance(anchor, str) or anchor.encode("utf-8") not in spec_bytes for anchor in anchors):
        raise BatchError("PUBLISHED_LOCATION_ANCHOR_NOT_IN_SPEC")

    discovery = _exact_keys(
        project["boundedDiscovery"],
        {
            "kind", "checkedPaths", "checkedParent", "namePattern", "matchingPaths",
            "repositoryAccessible", "worktreeCreated", "result",
        },
        "BOUNDED_DISCOVERY_INVALID",
    )
    if discovery["kind"] not in {"EXACT_PUBLISHED_PATH", "DIRECT_CHILD_NAME_MATCH"}:
        raise BatchError("BOUNDED_DISCOVERY_KIND_INVALID")
    if discovery["repositoryAccessible"] is not False or discovery["worktreeCreated"] is not False:
        raise BatchError("INACCESSIBLE_PROJECT_OVERCLAIM")
    if discovery["matchingPaths"] != [] or discovery["result"] != "PROJECT_REPOSITORY_NOT_ACCESSIBLE":
        raise BatchError("BOUNDED_DISCOVERY_RESULT_INVALID")
    if discovery["kind"] == "EXACT_PUBLISHED_PATH":
        if (
            not isinstance(discovery["checkedPaths"], list)
            or discovery["checkedPaths"] != [location["repoPath"]]
            or discovery["checkedParent"] is not None
            or discovery["namePattern"] is not None
        ):
            raise BatchError("EXACT_PATH_DISCOVERY_INVALID")
    else:
        if (
            discovery["checkedPaths"] != []
            or discovery["checkedParent"] != "C:\\code"
            or not isinstance(discovery["namePattern"], str)
            or location["repoPath"] is not None
        ):
            raise BatchError("DIRECT_CHILD_DISCOVERY_INVALID")

    _verify_dimensions(project["nonRegression"], spec_bytes)
    outcome = _exact_keys(
        project["dispositionOutcome"],
        {"kind", "code", "candidateProduced", "reason", "requiredOwnerEvidence"},
        "DISPOSITION_OUTCOME_INVALID",
    )
    if outcome["kind"] != "EXTERNAL_BLOCKER" or outcome["candidateProduced"] is not False:
        raise BatchError("DISPOSITION_CANDIDATE_OVERCLAIM")
    if not isinstance(outcome["code"], str) or not outcome["code"].startswith("PROJECT_"):
        raise BatchError("DISPOSITION_BLOCKER_CODE_INVALID")
    if not isinstance(outcome["reason"], str) or not outcome["reason"]:
        raise BatchError("DISPOSITION_BLOCKER_REASON_INVALID")
    if outcome["requiredOwnerEvidence"] != OWNER_EVIDENCE_REQUIREMENTS:
        raise BatchError("OWNER_EVIDENCE_REQUIREMENTS_INVALID")
    authority = _exact_keys(
        project["authority"],
        {"projectDisposition", "adoption", "runtime", "mutation"},
        "PROJECT_AUTHORITY_INVALID",
    )
    if any(value is not False for value in authority.values()):
        raise BatchError("PROJECT_AUTHORITY_OVERCLAIM")


def verify_batch(batch: dict[str, Any], treeish: str = "HEAD") -> None:
    batch = _exact_keys(
        batch,
        {"schema", "status", "frozenBase", "capture", "summary", "projects"},
        "BATCH_FIELDS_INVALID",
    )
    if batch["schema"] != SCHEMA or batch["status"] != "EXTERNAL_BLOCKERS_ONLY_ZERO_AUTHORITY":
        raise BatchError("BATCH_STATUS_INVALID")
    _verify_frozen_base(batch["frozenBase"], treeish)
    _verify_capture(batch["capture"])
    projects = batch["projects"]
    if not isinstance(projects, list) or len(projects) != len(PROJECT_IDS):
        raise BatchError("PROJECT_BATCH_SIZE_INVALID")
    ledger_rows = _ledger_rows()
    if {project.get("projectId") for project in projects if isinstance(project, dict)} != PROJECT_IDS:
        raise BatchError("PROJECT_BATCH_SET_INVALID")
    priorities = [project.get("priority") for project in projects]
    if priorities != list(range(1, len(PROJECT_IDS) + 1)):
        raise BatchError("PROJECT_PRIORITY_ORDER_INVALID")
    if projects[0].get("projectId") != "salesforce-tools":
        raise BatchError("MISSING_DISPOSITION_NOT_FIRST_PRIORITY")
    for project in projects:
        _verify_project(project, ledger_rows[project["projectId"]])

    summary = _exact_keys(
        batch["summary"],
        {"projectCount", "dispositionCandidates", "externalBlockers", "adoptionClaims"},
        "SUMMARY_INVALID",
    )
    if summary != {
        "projectCount": 8,
        "dispositionCandidates": 0,
        "externalBlockers": 8,
        "adoptionClaims": 0,
    }:
        raise BatchError("SUMMARY_OVERCLAIM")


def verify_local_probes(batch: dict[str, Any]) -> None:
    if os.environ.get("COMPUTERNAME", "").upper() != batch["capture"]["machine"]:
        raise BatchError("LOCAL_PROBE_MACHINE_MISMATCH")
    for project in batch["projects"]:
        discovery = project["boundedDiscovery"]
        if discovery["kind"] == "EXACT_PUBLISHED_PATH":
            actual = [path for path in discovery["checkedPaths"] if Path(path).exists()]
        else:
            parent = Path(discovery["checkedParent"])
            pattern = re.compile(discovery["namePattern"], re.IGNORECASE)
            actual = sorted(
                str(path) for path in parent.iterdir()
                if path.is_dir() and pattern.search(path.name)
            )
        if actual != discovery["matchingPaths"]:
            raise BatchError(f"LOCAL_PROBE_DRIFT:{project['projectId']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--treeish", default="HEAD")
    parser.add_argument("--verify-local-probes", action="store_true")
    args = parser.parse_args(argv)
    try:
        batch = load_json(_blob(args.treeish, BATCH_PATH))
        verify_batch(batch, args.treeish)
        if args.verify_local_probes:
            verify_local_probes(batch)
    except BatchError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    suffix = " local-probes=PASS" if args.verify_local_probes else ""
    print(f"PASS: R26 phase-2 intake has 8 exact external blockers and 0 adoption claims{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
