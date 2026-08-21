#!/usr/bin/env python3
"""Verify the zero-authority Phase 16 publication of the Phase 15 review."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PHASE15 = "488538ca15676823681e241f6be848de1d30a291"
PHASE15_TREE = "8a6ebfb6b1e1ff540006ac3c3c42c0a787fecb98"
PHASE15_PARENT = "95df488b2e2ec7120e992c0043d54b8e67a65dba"
ARTIFACT = "adoption/phase16/r26-phase15-review-publication.json"
ARTIFACT_SHA256 = "D91309FD2B99D675D0B9606213AF531EBB061A67C99A51552284BEB55CD43CE8"
PACKET = "adoption/phase16/phase15-review-packet.json"
RESULT = "adoption/phase16/phase15-review-result.jsonl"
CONSUMPTION = "adoption/phase16/phase15-review-consumption.json"
LEDGER = "adoption/universal-token-control-r26.json"
LEDGER_OID = "2f1808e8df35e6d1bae98f83aab378d93a0c3228"
COUNTS = {"ADOPT": 0, "DISTINGUISH": 5, "MISSING": 0, "REJECT": 0, "STALE": 4}
INTEGRATION_PATHS = {
    ".github/workflows/disposition-intake.yml",
    "adoption/phase16/README.md", ARTIFACT, PACKET, RESULT, CONSUMPTION,
    "tests/test_phase15_integration.py", "tests/test_phase16_integration.py",
    "tools/check_phase15_integration.py", "tools/check_phase16_integration.py",
}
ROOT_KEYS = {
    "schema", "status", "reviewedPhase15", "independentReview", "findingClosure",
    "ledgerTreatment", "remainingUncreditedProofs", "authority",
}
AUTHORITY_KEYS = {
    "projectDisposition", "fleetAdoption", "installation", "runtime",
    "providerExecution", "taskOrGateMutation", "pushOrMerge",
}


class Phase16Error(ValueError):
    pass


def _pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    folded: set[str] = set()
    for key, value in items:
        if not isinstance(key, str) or key.casefold() in folded:
            raise Phase16Error("DUPLICATE_OR_CASE_COLLIDING_KEY")
        folded.add(key.casefold())
        out[key] = value
    return out


def load_json(raw: bytes) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Phase16Error("JSON_INVALID") from exc
    if type(value) is not dict:
        raise Phase16Error("JSON_ROOT_INVALID")
    return value


def _git(args: list[str], *, text: bool = False) -> bytes | str:
    run = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, check=False,
                         text=text, encoding="utf-8" if text else None)
    if run.returncode != 0:
        raise Phase16Error("GIT_COMMAND_FAILED")
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
        raise Phase16Error("COMMIT_TUPLE_INVALID")
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


def _exact(value: Any, keys: set[str], code: str) -> dict[str, Any]:
    if type(value) is not dict or set(value) != keys:
        raise Phase16Error(code)
    return value


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


def verify_document(doc: dict[str, Any]) -> None:
    _exact(doc, ROOT_KEYS, "ROOT_SHAPE_INVALID")
    if doc["schema"] != "fleet-r26-phase15-review-publication/v1" or doc["status"] != "CANDIDATE_ZERO_AUTHORITY":
        raise Phase16Error("ARTIFACT_IDENTITY_INVALID")
    if not _native(doc["reviewedPhase15"], {
        "commit": PHASE15, "tree": PHASE15_TREE, "orderedParents": [PHASE15_PARENT],
        "publicationPath": "adoption/phase15/r26-mlv-prelaunch-boundary-publication.json",
        "publicationGitBlobOid": "417353eb69d0d10c3f72677c352fab63f8f54b00",
        "publicationBytes": 5318, "publicationSha256": "45B44C1F598AF29C046FCA44A5C3862742012FD61D276D48549D27082DDDFC4B",
    }):
        raise Phase16Error("PHASE15_SUBJECT_INVALID")
    review = _exact(doc["independentReview"], {
        "routeId", "lane", "model", "effort", "role", "sessionId", "authorizationId",
        "packet", "artifact", "result", "consumption", "providerTools", "permissionDenials",
        "verdict", "doneConsumedReleasedAtUtc",
    }, "REVIEW_SHAPE_INVALID")
    if not _native({key: review[key] for key in ("routeId", "lane", "model", "effort", "role", "sessionId", "authorizationId")}, {
        "routeId": "fleet-r65-doctrine-phase15-mlv-fable", "lane": "fable", "model": "claude-fable-5",
        "effort": "max", "role": "coordinator", "sessionId": "ed735398-54bb-4e3b-b7a7-a338c0c716c5",
        "authorizationId": "3a491c42-4abf-4c01-b206-1f7664a36ca5",
    }):
        raise Phase16Error("REVIEW_IDENTITY_INVALID")
    if not _native(review["packet"], {"path": PACKET, "bytes": 2280, "sha256": "F43F30374DFA4C2262A7DF1997D35D9B03418B6DBB8877CEECC90F6FA29B3E93"}):
        raise Phase16Error("PACKET_TUPLE_INVALID")
    if not _native(review["artifact"], {
        "externalPath": "C:\\Users\\obabalola\\.claude\\machine\\fleet-provider-capacity\\artifacts\\7bf6dd7d5b7548bfa0a164b5f12adf64.stdout.txt",
        "bytes": 142563, "sha256": "16CE28964B5FE23ACAE478769FF92D1C5EFA89EB53621FDF53491AD6A6662AC3",
    }):
        raise Phase16Error("ARTIFACT_TUPLE_INVALID")
    if not _native(review["result"], {
        "path": RESULT, "fileBytes": 8530, "fileSha256": "4A58EA05B25B821A4A22C56BDD1952188A3E54E4834692B6CCE79E18BAFBE6AC",
        "rawLineBytes": 8529, "rawLineSha256": "77EEED9DAC1AC2A1E1A28D0C8E0EA62157034CC77381555B3B4DE7F84CD9F402",
        "structuredCanonicalBytes": 3388, "structuredCanonicalSha256": "6BC99A216084F6874FB59F4B5850C05065D7CE161784677F4AC15D8DEC50BC0B",
        "subtype": "success", "isError": False, "verdict": "ACCEPT",
    }):
        raise Phase16Error("RESULT_TUPLE_INVALID")
    if not _native(review["consumption"], {
        "path": CONSUMPTION, "fileBytes": 528, "fileSha256": "7C48D4205521FDD8110E70F0BD2A2375489D22DFA69CD9BDCBC9DE3BD50DD98A",
        "rawReceiptBytes": 527, "rawReceiptSha256": "AF67ACDF2F395952D677ABE8999BA0A4C50FCB2BEB839EEAFCAD20CDA11F095A",
    }):
        raise Phase16Error("CONSUMPTION_TUPLE_INVALID")
    if not _native(review["providerTools"], ["Read", "StructuredOutput"]) or type(review["permissionDenials"]) is not int or review["permissionDenials"] != 0:
        raise Phase16Error("REVIEW_TOOL_BOUNDARY_INVALID")
    if review["verdict"] != "ACCEPT_CANDIDATE_ONLY" or review["doneConsumedReleasedAtUtc"] != "2026-08-21T13:34:19.4771490+00:00":
        raise Phase16Error("REVIEW_VERDICT_INVALID")
    closure = _exact(doc["findingClosure"], {"workflowOrder", "stagedSpecRederivation"}, "FINDING_CLOSURE_SHAPE_INVALID")
    expected_row = {
        "severity": "LOW", "status": "CLOSED_FORWARD_ONLY", "checkerPath": "tools/check_phase15_integration.py",
        "checkerGitBlobOid": "82d41c1d049276a0b759b4b71643616d072da218", "checkerBytes": 14002,
        "checkerSha256": "80D3547CA8DD12DE4F3B8D6E75A5E965785B9783BBDCFE82E9C02C0442723EB4",
    }
    for key, law in (
        ("workflowOrder", "required workflow commands occur exactly once and their byte offsets are strictly ordered"),
        ("stagedSpecRederivation", "staged mode enumerates index specs and compares every index blob to immutable Phase 14"),
    ):
        if not _native(closure[key], {**expected_row, "law": law}):
            raise Phase16Error("FINDING_CLOSURE_INVALID")
    treatment = doc["ledgerTreatment"]
    if not _native(treatment, {"counts": COUNTS, "mlvDispositionRemains": "DISTINGUISH", "ledgerModified": False, "specificationsModified": False}):
        raise Phase16Error("LEDGER_TREATMENT_INVALID")
    expected_gaps = [
        "PRODUCTION_LAUNCHER_WIRING", "SIGNED_INSTALLATION", "RUNTIME_INTERCEPTION",
        "COMPLETE_LAUNCHER_INVENTORY", "COMPLETE_ACTION_GRAPH", "EXACT_MODEL_EFFORT_ROLE_BINDING",
        "QUALITY_EQUIVALENCE", "FUNCTIONALITY_EQUIVALENCE", "CURRENT_CLOSED_GATE_PROOF",
        "PROJECT_OWNER_DISPOSITION", "ADOPTION",
    ]
    if not _native(doc["remainingUncreditedProofs"], expected_gaps):
        raise Phase16Error("UNCREDITED_PROOFS_INVALID")
    authority = _exact(doc["authority"], AUTHORITY_KEYS, "AUTHORITY_SHAPE_INVALID")
    if any(type(value) is not bool or value is not False for value in authority.values()):
        raise Phase16Error("AUTHORITY_OVERCLAIM")


def verify_snapshots(treeish: str) -> None:
    packet_raw = _blob(treeish, PACKET)
    result_file = _blob(treeish, RESULT)
    consumption_file = _blob(treeish, CONSUMPTION)
    if len(packet_raw) != 2280 or _sha(packet_raw) != "F43F30374DFA4C2262A7DF1997D35D9B03418B6DBB8877CEECC90F6FA29B3E93":
        raise Phase16Error("PACKET_SNAPSHOT_INVALID")
    packet = load_json(packet_raw)
    if packet.get("route_id") != "fleet-r65-doctrine-phase15-mlv-fable" or packet.get("lane") != "fable" or packet.get("role") != "coordinator":
        raise Phase16Error("PACKET_IDENTITY_INVALID")
    if packet.get("authority") != "read-only-review" or packet.get("no_subagents") is not True or packet.get("no_lane_reopen") is not True:
        raise Phase16Error("PACKET_AUTHORITY_INVALID")
    result_raw = result_file.rstrip(b"\r\n")
    if len(result_file) != 8530 or _sha(result_file) != "4A58EA05B25B821A4A22C56BDD1952188A3E54E4834692B6CCE79E18BAFBE6AC" or len(result_raw) != 8529 or _sha(result_raw) != "77EEED9DAC1AC2A1E1A28D0C8E0EA62157034CC77381555B3B4DE7F84CD9F402":
        raise Phase16Error("RESULT_SNAPSHOT_INVALID")
    result = load_json(result_raw)
    if result.get("type") != "result" or result.get("subtype") != "success" or result.get("is_error") is not False or result.get("session_id") != "ed735398-54bb-4e3b-b7a7-a338c0c716c5":
        raise Phase16Error("RESULT_ENVELOPE_INVALID")
    structured = result.get("structured_output")
    if type(structured) is not dict or structured.get("route_id") != "fleet-r65-doctrine-phase15-mlv-fable" or structured.get("lane") != "fable" or structured.get("verdict") != "ACCEPT":
        raise Phase16Error("STRUCTURED_RESULT_INVALID")
    canonical = json.dumps(structured, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    if len(canonical) != 3388 or _sha(canonical) != "6BC99A216084F6874FB59F4B5850C05065D7CE161784677F4AC15D8DEC50BC0B":
        raise Phase16Error("STRUCTURED_RESULT_DIGEST_INVALID")
    consumption_raw = consumption_file.rstrip(b"\r\n")
    if len(consumption_file) != 528 or _sha(consumption_file) != "7C48D4205521FDD8110E70F0BD2A2375489D22DFA69CD9BDCBC9DE3BD50DD98A" or len(consumption_raw) != 527 or _sha(consumption_raw) != "AF67ACDF2F395952D677ABE8999BA0A4C50FCB2BEB839EEAFCAD20CDA11F095A":
        raise Phase16Error("CONSUMPTION_SNAPSHOT_INVALID")
    consumption = load_json(consumption_raw)
    if consumption.get("route_id") != packet["route_id"] or consumption.get("lane") != "fable" or consumption.get("packet_sha256") != _sha(packet_raw) or consumption.get("output_sha256") != "16CE28964B5FE23ACAE478769FF92D1C5EFA89EB53621FDF53491AD6A6662AC3":
        raise Phase16Error("CONSUMPTION_BINDING_INVALID")


def verify_closure(treeish: str) -> None:
    raw = _blob(treeish, "tools/check_phase15_integration.py")
    if len(raw) != 14002 or _sha(raw) != "80D3547CA8DD12DE4F3B8D6E75A5E965785B9783BBDCFE82E9C02C0442723EB4" or _oid(treeish, "tools/check_phase15_integration.py") != "82d41c1d049276a0b759b4b71643616d072da218":
        raise Phase16Error("PHASE15_CHECKER_CLOSURE_INVALID")
    text = raw.decode("utf-8", errors="strict")
    required = (
        'current_specs = str(_git(["ls-files", "--cached", "--", "specs"], text=True)).splitlines()',
        'any(_oid(treeish, path) != _oid(PHASE14, path) for path in phase14_specs)',
        'positions = [workflow.find(command) for command in required]',
        'positions != sorted(positions)',
    )
    if any(text.count(value) != 1 for value in required):
        raise Phase16Error("PHASE15_CLOSURE_LAW_INVALID")


def verify_policy(treeish: str) -> None:
    if _oid(treeish, LEDGER) != LEDGER_OID:
        raise Phase16Error("LEDGER_DRIFT")
    ledger = load_json(_blob(treeish, LEDGER))
    if not _native(ledger.get("summary", {}).get("counts"), COUNTS) or ledger.get("summary", {}).get("fleetAdoptionClaim") is not False:
        raise Phase16Error("LEDGER_SEMANTICS_DRIFT")
    base_specs = str(_git(["ls-tree", "-r", "--name-only", PHASE15, "specs"], text=True)).splitlines()
    if treeish == ":":
        current_specs = str(_git(["ls-files", "--cached", "--", "specs"], text=True)).splitlines()
    else:
        current_specs = str(_git(["ls-tree", "-r", "--name-only", treeish, "specs"], text=True)).splitlines()
    if base_specs != current_specs or any(_oid(treeish, path) != _oid(PHASE15, path) for path in base_specs):
        raise Phase16Error("SPEC_DRIFT")


def verify_workflow(treeish: str) -> None:
    workflow = _blob(treeish, ".github/workflows/disposition-intake.yml").decode("utf-8", errors="strict")
    required = (
        f"python tools/check_phase15_integration.py --treeish {PHASE15}",
        'test_phase16_integration.py" -v',
        "python tools/check_phase16_integration.py --treeish HEAD",
    )
    positions = [workflow.find(command) for command in required]
    if any(workflow.count(command) != 1 for command in required) or positions != sorted(positions):
        raise Phase16Error("WORKFLOW_ROUTING_INVALID")


def verify(treeish: str) -> None:
    if _tuple(PHASE15) != (PHASE15_TREE, [PHASE15_PARENT]):
        raise Phase16Error("PHASE15_TUPLE_INVALID")
    if _oid(PHASE15, "adoption/phase15/r26-mlv-prelaunch-boundary-publication.json") != "417353eb69d0d10c3f72677c352fab63f8f54b00":
        raise Phase16Error("PHASE15_ARTIFACT_BLOB_INVALID")
    if treeish == ":":
        if str(_git(["rev-parse", "HEAD"], text=True)).strip() != PHASE15:
            raise Phase16Error("STAGED_PARENT_MISMATCH")
    elif _tuple(treeish)[1] != [PHASE15]:
        raise Phase16Error("PHASE16_PARENT_MISMATCH")
    if _changed_paths(PHASE15, treeish) != INTEGRATION_PATHS:
        raise Phase16Error("INTEGRATION_SCOPE_MISMATCH")
    artifact_raw = _blob(treeish, ARTIFACT)
    if _sha(artifact_raw) != ARTIFACT_SHA256:
        raise Phase16Error("ARTIFACT_HASH_MISMATCH")
    verify_document(load_json(artifact_raw))
    verify_snapshots(treeish)
    verify_closure(treeish)
    verify_policy(treeish)
    verify_workflow(treeish)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--treeish", default="HEAD")
    args = parser.parse_args()
    try:
        verify(args.treeish)
    except Phase16Error as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"PASS: Phase16 exact-binds the accepted Phase15 review and two LOW closures; ledger=0/5/4; artifact_sha256={ARTIFACT_SHA256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
