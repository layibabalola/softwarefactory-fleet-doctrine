#!/usr/bin/env python3
"""Verify the forward-only Phase 17 DNG post-R60 evidence publication."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = "8149c3f06811f85b833b28940017f2d05448cf5d"
BASE_TREE = "1a8193ae7f8c9982bfe499d039e5c85ae74ea907"
ARTIFACT = "adoption/phase17/r26-dng-post-r60-evidence-publication.json"
LEDGER = "adoption/universal-token-control-r26.json"
LEDGER_BLOB = "2f1808e8df35e6d1bae98f83aab378d93a0c3228"
LEDGER_SHA256 = "77BB2DC10D5289C5FDE102DC93D8B976511DDADCA8115640B5880202F936FCB3"
ALLOWED = {
    ".github/workflows/disposition-intake.yml",
    "adoption/README.md",
    "adoption/phase17/README.md",
    ARTIFACT,
    "tests/test_phase17_dng_r60_publication.py",
    "tools/check_phase17_dng_r60_publication.py",
}


class CheckFailure(RuntimeError):
    pass


def _run(*args: str) -> bytes:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
    )
    if result.returncode != 0:
        raise CheckFailure(result.stderr.decode("utf-8", "replace").strip() or "git command failed")
    return result.stdout


def _blob(treeish: str, path: str) -> bytes:
    if treeish == "WORKTREE":
        target = ROOT / path
        if not target.is_file():
            raise CheckFailure(f"missing worktree path: {path}")
        return target.read_bytes()
    return _run("show", f"{treeish}:{path}")


def _oid(treeish: str, path: str) -> str:
    if treeish == "WORKTREE":
        return "WORKTREE"
    return _run("rev-parse", f"{treeish}:{path}").decode().strip()


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


def _json(treeish: str, path: str) -> dict:
    raw = _blob(treeish, path)
    if raw.startswith(b"\xef\xbb\xbf"):
        raise CheckFailure(f"UTF-8 BOM forbidden: {path}")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CheckFailure(f"invalid strict JSON at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CheckFailure(f"root object required: {path}")
    return value


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    folded: set[str] = set()
    for key, value in pairs:
        lowered = key.casefold()
        if key in result or lowered in folded:
            raise CheckFailure(f"duplicate or case-colliding JSON key: {key}")
        result[key] = value
        folded.add(lowered)
    return result


def _exact_keys(value: object, expected: set[str], where: str) -> dict:
    if not isinstance(value, dict) or set(value) != expected:
        raise CheckFailure(f"{where} keys are not exact")
    return value


def _exact(value: object, expected: object, where: str) -> None:
    if type(value) is not type(expected) or value != expected:
        raise CheckFailure(f"{where} is not exact")


def _tuple(value: object, expected: dict, where: str) -> None:
    row = _exact_keys(value, set(expected), where)
    for key, expected_value in expected.items():
        _exact(row[key], expected_value, f"{where}.{key}")


PROJECT_ARTIFACTS = [
    {
        "path": "docs/evidence/universal-token-control-r26/current-disposition.json",
        "gitBlobOid": "f0a0c6aeee557a2ed24afb30ec8e05947c7a1a0d",
        "bytes": 6481,
        "sha256": "7758870808F9E52F78B258BDB26F2E91C55D3D85E15A0E4E5BA1D945046E9D92",
    },
    {
        "path": "docs/evidence/universal-token-control-r26/post-r60-closed-gate-attestation.json",
        "gitBlobOid": "9404b13990bde43a5477fee9fbcebcbd7a1c9fd4",
        "bytes": 1053,
        "sha256": "06A1AE024695DCBA06E42979B4AA02B7CC768406707AB1E309525AE58AAB036F",
    },
    {
        "path": "docs/evidence/universal-token-control-r26/post-r60-idle-baseline.json",
        "gitBlobOid": "5306b5f37582d940e6a8dea66b137fdfc2e0a2b4",
        "bytes": 2914,
        "sha256": "2FD103904D86C91BB5EA22EE9B92D735CFE7722F72281FC08ACF4631C6DD6682",
    },
    {
        "path": "scripts/verify-universal-token-control-disposition.ps1",
        "gitBlobOid": "bc9a0e64373a425dbea4b0a00a2975ec22b4584c",
        "bytes": 15386,
        "sha256": "71A9AFE1F9C4CE5746ED9E6F0498208F3BF8929E220F9A79C2F728C7268881B8",
    },
    {
        "path": "scripts/test-universal-token-control-disposition.ps1",
        "gitBlobOid": "eaa6fa407c8100011147f81e7c736af3979a8402",
        "bytes": 5067,
        "sha256": "833E8E785766CD67E8E06628BF2DA1791F1451B6D7FCF055167ED86A59A223B4",
    },
]


def validate_document(doc: dict) -> None:
    _exact_keys(
        doc,
        {
            "schema", "status", "doctrineBase", "sourceProject", "projectArtifacts",
            "r60Candidate", "r102Acceptance", "runtimeProof", "currentDisposition",
            "ledgerTreatment", "authority",
        },
        "$",
    )
    _exact(doc["schema"], "fleet-r26-dng-post-r60-evidence-publication/v1", "$.schema")
    _exact(doc["status"], "EVIDENCE_PUBLICATION_NO_LEDGER_CHANGE", "$.status")

    _tuple(doc["doctrineBase"], {
        "commit": BASE, "tree": BASE_TREE,
        "orderedParents": ["488538ca15676823681e241f6be848de1d30a291"],
    }, "$.doctrineBase")
    _tuple(doc["sourceProject"], {
        "projectId": "dng-auto-processor",
        "repositoryPath": r"C:\code\DngAutoProcessor - Claude\DngAutoProcessor",
        "branch": "master",
        "commit": "43507aa20dfaaf198267cda0058689493d43d70a",
        "tree": "c6a2a33f68a5cedcbb26de2fb78befdc2738f323",
        "orderedParents": ["1876f1c379d4d7f755031924322e6cc29132a610"],
        "localOnly": True,
        "remoteFreshnessVerified": False,
    }, "$.sourceProject")
    _exact(doc["projectArtifacts"], PROJECT_ARTIFACTS, "$.projectArtifacts")

    _tuple(doc["r60Candidate"], {
        "path": "coordination/candidates/durable-campaign-hold-installer-r60-r59-opus-proof-closure",
        "files": 134, "subjects": 132,
        "subjectTreeSha256": "5F4791D65B990522418372628142113E5F6DC505A1DF4380B89852B2A28765ED",
        "fullTreeSha256": "0DCA4FB5C559163D1F03EFC5F552660DB909073EB8483ADC5B440E2F8832E1A7",
        "manifestBytes": 65517,
        "manifestSha256": "199BB6D8117145948FAA41685797FA3BBE687AADC2760651A43880B9CFDA1714",
    }, "$.r60Candidate")

    acceptance = _exact_keys(doc["r102Acceptance"], {
        "strictSerial", "naturalRegisteredCadenceOnly", "providerLaunches", "verdicts",
        "actionableFindings", "checkpoint",
    }, "$.r102Acceptance")
    _exact(acceptance["strictSerial"], True, "$.r102Acceptance.strictSerial")
    _exact(acceptance["naturalRegisteredCadenceOnly"], True, "$.r102Acceptance.naturalRegisteredCadenceOnly")
    _exact(acceptance["providerLaunches"], 3, "$.r102Acceptance.providerLaunches")
    _exact(acceptance["verdicts"], {"fable": "ACCEPT", "opus": "ACCEPT", "sonnet": "ACCEPT"}, "$.r102Acceptance.verdicts")
    _exact(acceptance["actionableFindings"], 0, "$.r102Acceptance.actionableFindings")
    _tuple(acceptance["checkpoint"], {
        "path": "coordination/review-packets/r102-unanimous-acceptance-20260822T1600.json",
        "bytes": 1504,
        "sha256": "7A2F2A90F0B405B8EEB23B470DB4371618D94DEA911FA9C225E4C25CD768AE5C",
    }, "$.r102Acceptance.checkpoint")

    runtime = _exact_keys(doc["runtimeProof"], {
        "preview", "firstApply", "rollback", "finalReinstall", "taskState", "lastTaskResult",
        "latchState", "installedTupleSha256", "previewCheckpoint", "firstApplyCheckpoint",
        "rollbackCheckpoint", "finalReinstallCheckpoint",
    }, "$.runtimeProof")
    expected_runtime = {
        "preview": "WOULD_APPLY_NONMUTATING_MEASURED_EXACT",
        "firstApply": "COMMITTED_ENABLED_TWO_CADENCES",
        "rollback": "ROLLED_BACK_ENABLED_EXACT_PREIMAGES_AND_ABSENCE",
        "finalReinstall": "COMMITTED_ENABLED_TWO_FRESH_CADENCES",
        "taskState": "Ready", "lastTaskResult": 0, "latchState": "ABSENT",
        "installedTupleSha256": "4C58027BB045C7E781969627A2E25881BC06F17E4F8AF2D874AC5A32592632BF",
    }
    for key, value in expected_runtime.items():
        _exact(runtime[key], value, f"$.runtimeProof.{key}")
    for key, expected in {
        "previewCheckpoint": ("r102-r60-production-preview-20260822T1600.json", 1683, "2A9DF2E5023B8070FCCB292C4CA9EDF5487039EDA759556075D553A1EF608576"),
        "firstApplyCheckpoint": ("r102-r60-first-live-apply-20260822T1610.json", 2560, "FFA1FCC75045D517B3EF68D797618FA9E4DDC30F4EFD6CB84ABDF29E9B687604"),
        "rollbackCheckpoint": ("r102-r60-live-rollback-proof-20260822T1611.json", 1852, "0B69BF24151A753618BED1B3CE1D0CC20B778175DE40589EEB4A8FA456FD778C"),
        "finalReinstallCheckpoint": ("r102-r60-final-reinstall-20260822T1620.json", 3240, "0BF832B2C23DF6A8A64B54DB1A831C56515497B3C99098B9599E41B23814DB28"),
    }.items():
        filename, size, digest = expected
        _tuple(runtime[key], {
            "path": f"coordination/review-packets/{filename}", "bytes": size, "sha256": digest,
        }, f"$.runtimeProof.{key}")

    _tuple(doc["currentDisposition"], {
        "kind": "DISTINGUISH", "requirementsMet": 2, "requirementsTotal": 13,
        "installationProven": True, "adoptionCredit": False, "fleetDispositionCredit": False,
        "idleTicks": 0, "requiredIdleTicks": 1000,
        "notBeforeUtc": "2026-08-22T21:20:50.0689024Z",
        "controlFingerprint": "20A9EE1618FE3A48041436896FEDB17CA38AFB539BD5C3D1DE5D44E839FA48B8",
        "automaticLaunchGate": "closed", "fullAdoptionRollbackProven": False,
        "qualityEquivalenceProven": False, "functionalityEquivalenceProven": False,
    }, "$.currentDisposition")

    ledger = _exact_keys(doc["ledgerTreatment"], {
        "path", "gitBlobOid", "bytes", "sha256", "counts", "modified", "reason",
    }, "$.ledgerTreatment")
    for key, value in {
        "path": LEDGER, "gitBlobOid": LEDGER_BLOB, "bytes": 16599,
        "sha256": LEDGER_SHA256, "modified": False,
    }.items():
        _exact(ledger[key], value, f"$.ledgerTreatment.{key}")
    _exact(ledger["counts"], {"ADOPT": 0, "DISTINGUISH": 5, "MISSING": 0, "REJECT": 0, "STALE": 4}, "$.ledgerTreatment.counts")
    if not isinstance(ledger["reason"], str) or not ledger["reason"].strip():
        raise CheckFailure("$.ledgerTreatment.reason must be nonblank")

    authority = _exact_keys(doc["authority"], {
        "projectDispositionMutation", "fleetAdoption", "providerExecution", "taskOrGateMutation",
        "installation", "repositoryMutation", "remotePublication",
    }, "$.authority")
    if any(type(value) is not bool or value for value in authority.values()):
        raise CheckFailure("all Phase 17 authority fields must be native false")


def _changed(treeish: str) -> set[str]:
    if treeish == "WORKTREE":
        tracked = set(_run("diff", "--name-only", BASE).decode().splitlines())
        untracked = set(_run("ls-files", "--others", "--exclude-standard").decode().splitlines())
        return tracked | untracked
    return set(_run("diff", "--name-only", BASE, treeish).decode().splitlines())


def verify(treeish: str) -> None:
    validate_document(_json(treeish, ARTIFACT))
    changed = _changed(treeish)
    unexpected = changed - ALLOWED
    missing = ALLOWED - changed
    if unexpected:
        raise CheckFailure(f"unexpected Phase 17 paths: {sorted(unexpected)}")
    if missing:
        raise CheckFailure(f"missing Phase 17 paths: {sorted(missing)}")

    if treeish != "WORKTREE":
        parents = _run("show", "-s", "--format=%P", treeish).decode().strip().split()
        if parents != [BASE]:
            raise CheckFailure("Phase 17 must have the exact Phase 16 parent")
    if _oid(BASE, LEDGER) != LEDGER_BLOB or _sha(_blob(BASE, LEDGER)) != LEDGER_SHA256:
        raise CheckFailure("frozen base ledger identity drift")
    if treeish != "WORKTREE":
        if _oid(treeish, LEDGER) != LEDGER_BLOB:
            raise CheckFailure("Phase 17 changed the frozen adoption ledger")
        if _sha(_blob(treeish, LEDGER)) != LEDGER_SHA256:
            raise CheckFailure("Phase 17 changed the frozen adoption ledger bytes")

    workflow = _blob(treeish, ".github/workflows/disposition-intake.yml").decode("utf-8")
    readme = _blob(treeish, "adoption/README.md").decode("utf-8")
    commands = [
        'test_phase17_dng_r60_publication.py" -v',
        "python tools/check_phase17_dng_r60_publication.py --treeish HEAD",
    ]
    if any(command not in workflow for command in commands):
        raise CheckFailure("workflow does not run both Phase 17 controls")
    if any(command not in readme for command in commands):
        raise CheckFailure("adoption README does not publish both Phase 17 controls")
    if workflow.index("test_phase16_integration.py") > workflow.index("test_phase17_dng_r60_publication.py"):
        raise CheckFailure("Phase 17 workflow ordering is invalid")
    if workflow.index("test_phase17_dng_r60_publication.py") > workflow.index("test_adoption_ledger.py"):
        raise CheckFailure("frozen ledger must run after Phase 17")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--treeish", default="HEAD")
    args = parser.parse_args()
    try:
        verify(args.treeish)
    except CheckFailure as exc:
        print(f"PHASE17_INVALID: {exc}", file=sys.stderr)
        return 1
    print("PHASE17_VALID dng=DISTINGUISH met=2/13 idle=0/1000 ledger=0/5/4 authority=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
