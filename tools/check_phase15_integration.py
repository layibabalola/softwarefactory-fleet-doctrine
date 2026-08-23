#!/usr/bin/env python3
"""Verify the zero-authority Phase 15 MLV prelaunch publication."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PHASE14 = "95df488b2e2ec7120e992c0043d54b8e67a65dba"
PHASE14_TREE = "ef9184c4503a1e9bacef781a3cdb61b8c4a7badf"
PHASE14_PARENT = "eca6e364cf03e388f0416e3f8e80fe4091321aa0"
ARTIFACT = "adoption/phase15/r26-mlv-prelaunch-boundary-publication.json"
ARTIFACT_SHA256 = "45B44C1F598AF29C046FCA44A5C3862742012FD61D276D48549D27082DDDFC4B"
LEDGER = "adoption/universal-token-control-r26.json"
LEDGER_OID = "2f1808e8df35e6d1bae98f83aab378d93a0c3228"
COUNTS = {"ADOPT": 0, "DISTINGUISH": 5, "MISSING": 0, "REJECT": 0, "STALE": 4}
INTEGRATION_PATHS = {
    ".github/workflows/disposition-intake.yml",
    "adoption/phase15/README.md",
    ARTIFACT,
    "tests/test_phase14_integration.py",
    "tests/test_phase15_integration.py",
    "tools/check_phase15_integration.py",
}
ROOT_KEYS = {
    "schema", "status", "phase14", "sourceProject", "reviewedCandidate",
    "independentReview", "forwardClosure", "durableProjectReceipt",
    "acceptedBoundary", "ledgerTreatment", "remainingUncreditedProofs", "authority",
}
AUTHORITY_KEYS = {
    "projectDisposition", "fleetAdoption", "installation", "runtime",
    "providerExecution", "taskOrGateMutation", "pushOrMerge",
}


class Phase15Error(ValueError):
    pass


def _pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    folded: set[str] = set()
    for key, value in items:
        if not isinstance(key, str) or key.casefold() in folded:
            raise Phase15Error("DUPLICATE_OR_CASE_COLLIDING_KEY")
        folded.add(key.casefold())
        out[key] = value
    return out


def load_json(raw: bytes) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Phase15Error("JSON_INVALID") from exc
    if type(value) is not dict:
        raise Phase15Error("JSON_ROOT_INVALID")
    return value


def _git(args: list[str], *, text: bool = False) -> bytes | str:
    run = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, check=False,
                         text=text, encoding="utf-8" if text else None)
    if run.returncode != 0:
        raise Phase15Error("GIT_COMMAND_FAILED")
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
        raise Phase15Error("COMMIT_TUPLE_INVALID")
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


def _exact_keys(value: Any, expected: set[str], code: str) -> dict[str, Any]:
    if type(value) is not dict or set(value) != expected:
        raise Phase15Error(code)
    return value


def verify_document(doc: dict[str, Any]) -> None:
    _exact_keys(doc, ROOT_KEYS, "ROOT_SHAPE_INVALID")
    if doc["schema"] != "fleet-r26-mlv-prelaunch-boundary-publication/v1" or doc["status"] != "CANDIDATE_ZERO_AUTHORITY":
        raise Phase15Error("ARTIFACT_IDENTITY_INVALID")
    if not _native(doc["phase14"], {
        "commit": PHASE14, "tree": PHASE14_TREE, "orderedParents": [PHASE14_PARENT],
    }):
        raise Phase15Error("PHASE14_PROVENANCE_INVALID")
    if not _native(doc["sourceProject"], {
        "projectId": "mlv-app",
        "canonicalOrigin": "https://github.com/layibabalola/MLV-App.git",
        "publishedRef": "refs/heads/codex/mlv-r39-supervisor-integration",
        "commit": "56ed32587388fd6196d9259df381bb004a3c2da0",
        "tree": "483134ae9a7a701240e42039afff7b656f733615",
        "orderedParents": ["ad8d7f5f29882774c8eb5ce2df7c3c8689e73158"],
        "remoteRefVerified": True,
        "remoteVerifiedCommit": "56ed32587388fd6196d9259df381bb004a3c2da0",
    }):
        raise Phase15Error("SOURCE_PROJECT_INVALID")
    candidate = _exact_keys(doc["reviewedCandidate"], {
        "commit", "tree", "orderedParents", "source", "wrapper", "tests", "verifiedControls",
    }, "REVIEWED_CANDIDATE_SHAPE_INVALID")
    if candidate["commit"] != "65bcc9918a0c2bf844607163242caa43577ea713" or candidate["tree"] != "fd2860d35095e86bc161c901036b9bb4d903c6e9" or candidate["orderedParents"] != ["6974cfd868cea2fb60f688d6bacaf087075f55f7"]:
        raise Phase15Error("REVIEWED_CANDIDATE_TUPLE_INVALID")
    expected_subjects = {
        "source": {"path": "tools/provider_control/mlv_lane_supervisor.py", "gitBlobOid": "c56a8680e7c2e76c1da504043f1d20a2e01c2e35", "bytes": 47181, "sha256": "C807DBF42A20155E8C5B9FA69036B371E4F8C85423188C15430EF2F72AF5E8AB"},
        "wrapper": {"path": "tools/provider_control/invoke-mlv-lane-supervisor.ps1", "gitBlobOid": "c2bd5b75119303f5a764973fc21028da8f8f9707", "bytes": 837, "sha256": "A63031BFC1AC5073FB0503A59555B833FB284B1AAEDEB6E0A6590F5B591CAC23"},
        "tests": {"path": "tools/provider_control/tests/test_mlv_prelaunch_boundary.py", "gitBlobOid": "5dd2007d60c9649881e27ac5d82126d9d7dcc28b", "bytes": 5145, "sha256": "68DC63C4AECA301029FCE7C3EF426D73D406BF78659C185D489ED668EE6B4CF5"},
    }
    if any(not _native(candidate[key], expected) for key, expected in expected_subjects.items()):
        raise Phase15Error("REVIEWED_SUBJECT_INVALID")
    if not _native(candidate["verifiedControls"], {"prelaunchBoundary": "PASS 7/7", "legacySupervisor": "PASS 45/45", "reviewerExecutedTests": False}):
        raise Phase15Error("LOCAL_EVIDENCE_INVALID")
    review = _exact_keys(doc["independentReview"], {
        "routeId", "lane", "model", "effort", "role", "sessionId", "authorizationId",
        "packetBytes", "packetSha256", "artifactBytes", "artifactSha256", "resultLineBytes",
        "resultLineSha256", "receiptBytes", "receiptSha256", "providerTools", "verdict", "scope",
    }, "REVIEW_SHAPE_INVALID")
    expected_review = {
        "routeId": "fleet-r64-mlv-r40-prelaunch-sonnet", "lane": "sonnet", "model": "claude-sonnet-5",
        "effort": "max", "role": "verifier", "sessionId": "223c9b6b-1bdb-4e35-8d3a-99884f371150",
        "authorizationId": "ee33f602-274a-4212-8b05-b4b618c08a0e", "packetBytes": 2185,
        "packetSha256": "F81EBD20A0CEEB058F364CFD0A2E2BB8646124BB15E1944D6ACC454C37B01594",
        "artifactBytes": 202492, "artifactSha256": "0B72B7FC4B1FDE6CD993BBC8616358180DE49765B90144AA1BA5C5764CD55F85",
        "resultLineBytes": 8130, "resultLineSha256": "36EF72027A33F3063F9FD5504AD7A27BCD88E60C6827EB5D1300012E1596B1B0",
        "receiptBytes": 526, "receiptSha256": "D685E222FA36C577F4F391FBE77E6DDB9B010361513BD9B05F5BE5A74995471F",
        "providerTools": ["Read", "StructuredOutput"], "verdict": "ACCEPT", "scope": "candidate-only",
    }
    if not _native(review, expected_review):
        raise Phase15Error("INDEPENDENT_REVIEW_INVALID")
    if not _native(doc["forwardClosure"], {
        "commit": "ad8d7f5f29882774c8eb5ce2df7c3c8689e73158", "tree": "b8b989b5abba708d58cd2287a7c965994e206e22",
        "orderedParents": ["65bcc9918a0c2bf844607163242caa43577ea713"], "testPath": "tools/provider_control/tests/test_mlv_prelaunch_boundary.py",
        "testGitBlobOid": "f9ceb4e83b83d43263730e3a088e963857f598cf", "testBytes": 5552,
        "testSha256": "004C4CA77152B5D0A8849406D1B4DB8485CFDFCDCF18640B2E9AFE5D2C7A5F6A", "openGateHostile": "PASS", "suite": "PASS 8/8",
    }):
        raise Phase15Error("FORWARD_CLOSURE_INVALID")
    if not _native(doc["durableProjectReceipt"], {
        "path": "docs/universal-token-control-prelaunch-review-receipt-2026-08-21.json", "gitBlobOid": "6233233f13aa406167de7408149722606ccaf5de",
        "bytes": 4633, "sha256": "3E52376A0680ABB267A5D03ED00FB89EB601DB74CCB8033B7E9D0AE0E08DE057",
        "verifierPath": "tools/universal_token_control_prelaunch_review_receipt_tests.py", "verifierGitBlobOid": "9d4ba6cf8b4b97b2cd4cff1e1f4fc5a94d2aa7cc",
        "verifierBytes": 14049, "verifierSha256": "09362A380095A36B042EAB7EFB9B0CAD852DAE95397C2F1087FF5196702DCD8C", "result": "PASS 5/5",
    }):
        raise Phase15Error("DURABLE_RECEIPT_INVALID")
    expected_boundary = {
        "stopOnlyPrelaunchSource": True, "unknownAndAuthorizationShapesFailClosed": True,
        "nativeZeroCountersRequired": True, "openGateFailsClosed": True,
        "publishedCandidateBranch": True, "productionLauncherWired": False,
        "signedInstallation": False, "runtimeInterception": False,
        "functionalityEquivalence": False, "qualityEquivalence": False,
        "projectOwnerDisposition": False, "adoption": False,
    }
    if not _native(doc["acceptedBoundary"], expected_boundary):
        raise Phase15Error("ACCEPTED_BOUNDARY_INVALID")
    treatment = _exact_keys(doc["ledgerTreatment"], {
        "ledgerPath", "ledgerGitBlobOid", "counts", "mlvDispositionRemains", "ledgerModified", "specificationsModified",
    }, "LEDGER_TREATMENT_SHAPE_INVALID")
    if treatment["ledgerPath"] != LEDGER or treatment["ledgerGitBlobOid"] != LEDGER_OID or not _native(treatment["counts"], COUNTS):
        raise Phase15Error("LEDGER_TREATMENT_INVALID")
    if treatment["mlvDispositionRemains"] != "DISTINGUISH" or treatment["ledgerModified"] is not False or treatment["specificationsModified"] is not False:
        raise Phase15Error("POLICY_OVERCLAIM")
    expected_gaps = [
        "PRODUCTION_LAUNCHER_WIRING", "SIGNED_INSTALLATION", "RUNTIME_INTERCEPTION",
        "COMPLETE_LAUNCHER_INVENTORY", "COMPLETE_ACTION_GRAPH", "EXACT_MODEL_EFFORT_ROLE_BINDING",
        "QUALITY_EQUIVALENCE", "FUNCTIONALITY_EQUIVALENCE", "CURRENT_CLOSED_GATE_PROOF",
        "PROJECT_OWNER_DISPOSITION", "ADOPTION",
    ]
    if not _native(doc["remainingUncreditedProofs"], expected_gaps):
        raise Phase15Error("UNCREDITED_PROOFS_INVALID")
    authority = _exact_keys(doc["authority"], AUTHORITY_KEYS, "AUTHORITY_SHAPE_INVALID")
    if any(type(value) is not bool or value is not False for value in authority.values()):
        raise Phase15Error("AUTHORITY_OVERCLAIM")


def verify_artifact(treeish: str) -> None:
    raw = _blob(treeish, ARTIFACT)
    if hashlib.sha256(raw).hexdigest().upper() != ARTIFACT_SHA256:
        raise Phase15Error("ARTIFACT_HASH_MISMATCH")
    verify_document(load_json(raw))


def verify_policy(treeish: str) -> None:
    if _oid(treeish, LEDGER) != LEDGER_OID:
        raise Phase15Error("LEDGER_DRIFT")
    ledger = load_json(_blob(treeish, LEDGER))
    if not _native(ledger.get("summary", {}).get("counts"), COUNTS) or ledger.get("summary", {}).get("fleetAdoptionClaim") is not False:
        raise Phase15Error("LEDGER_SEMANTICS_DRIFT")
    phase14_specs = str(_git(["ls-tree", "-r", "--name-only", PHASE14, "specs"], text=True)).splitlines()
    if treeish == ":":
        current_specs = str(_git(["ls-files", "--cached", "--", "specs"], text=True)).splitlines()
    else:
        current_specs = str(_git(["ls-tree", "-r", "--name-only", treeish, "specs"], text=True)).splitlines()
    if phase14_specs != current_specs or any(_oid(treeish, path) != _oid(PHASE14, path) for path in phase14_specs):
        raise Phase15Error("SPEC_DRIFT")


def verify_workflow(treeish: str) -> None:
    workflow = _blob(treeish, ".github/workflows/disposition-intake.yml").decode("utf-8", errors="strict")
    required = (
        f"python tools/check_phase14_integration.py --treeish {PHASE14}",
        'test_phase15_integration.py" -v',
        "python tools/check_phase15_integration.py --treeish HEAD",
    )
    positions = [workflow.find(command) for command in required]
    if any(workflow.count(command) != 1 for command in required) or positions != sorted(positions):
        raise Phase15Error("WORKFLOW_ROUTING_INVALID")


def verify(treeish: str) -> None:
    if _tuple(PHASE14) != (PHASE14_TREE, [PHASE14_PARENT]):
        raise Phase15Error("PHASE14_TUPLE_INVALID")
    if treeish == ":":
        if str(_git(["rev-parse", "HEAD"], text=True)).strip() != PHASE14:
            raise Phase15Error("STAGED_PARENT_MISMATCH")
    elif _tuple(treeish)[1] != [PHASE14]:
        raise Phase15Error("PHASE15_PARENT_MISMATCH")
    if _changed_paths(PHASE14, treeish) != INTEGRATION_PATHS:
        raise Phase15Error("INTEGRATION_SCOPE_MISMATCH")
    verify_artifact(treeish)
    verify_policy(treeish)
    verify_workflow(treeish)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--treeish", default="HEAD")
    args = parser.parse_args()
    try:
        verify(args.treeish)
    except Phase15Error as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"PASS: Phase15 MLV prelaunch source boundary published; ledger=0/5/4; artifact_sha256={ARTIFACT_SHA256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
