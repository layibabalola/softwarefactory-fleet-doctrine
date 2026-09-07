#!/usr/bin/env python3
"""Verify immutable history and the separately sealed current R26 intake epoch.

This verifies evidence and CI control integrity. It grants no project adoption,
provider, installation or runtime authority. The old phase CLIs remain intact.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EPOCH_PATH = "adoption/current-intake-epoch-r1.json"
CURRENT_LEDGER = "adoption/current-token-control-r26.json"
SCHEMA = "fleet-current-intake-epoch/v1"
BOOTSTRAP_BASE = "c57997bac73c7f1d3fe3ef386d23cdb9c5b0251d"
SEALED_WORKFLOW = "6ab0955b94ba3c2698bf9917e7718c4daf1cdc50"
FROZEN_LEDGER = "53a48a6a0be5eade253ce1a508872d6874fd474a"
NEW_PHASE17 = "e48a538919d339dc46e9fa239d918c3762eae635"
FAILED_PHASE17 = "b346dc9b20a5c624e8aa5db4278758d5fe956b6b"
SHA40 = re.compile(r"[0-9a-f]{40}")
SHA256 = re.compile(r"[0-9a-f]{64}")
UNSAFE_GIT_ENV = {
    "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_REPLACE_REF_BASE", "GIT_INDEX_FILE", "GIT_NAMESPACE",
}
UNIT_MODULES = (
    "phase2_disposition_batch", "adversarialllm_utilization_shadow_doctrine",
    "phase3_disposition_batch", "phase5_stale_reconciliation",
    "phase6_candidate_reviews", "phase7_owner_publication_requests",
    "phase8_integration", "phase9_integration", "phase10_integration",
    "phase11_integration", "phase12_integration", "phase13_integration",
    "phase14_integration", "phase15_integration", "phase16_integration",
    "phase12_phase16_descendant_scope", "phase17_dng_r60_publication",
    "adoption_ledger", "current_adoption_ledger", "current_intake_epoch",
)
CHECKER_MODULES = tuple(x for x in UNIT_MODULES if x not in {
    "adversarialllm_utilization_shadow_doctrine", "current_adoption_ledger",
})
WORKFLOWS = {".github/workflows/disposition-intake.yml", ".github/workflows/adoption-ledger.yml"}
CONTROL_PATHS = WORKFLOWS | {
    *(f"tools/check_{name}.py" for name in CHECKER_MODULES),
    *(f"tests/test_{name}.py" for name in UNIT_MODULES),
    "adoption/current-token-control-r26.md",
    "ruling-candidates/current-intake-epoch-r1.md",
}
# The first publication admits this exact bounded repair, not accumulated master
# drift. Later normal intake cannot modify these sealed controls or the manifest.
BOOTSTRAP_CHANGED = {
    *WORKFLOWS, EPOCH_PATH, CURRENT_LEDGER,
    "adoption/current-token-control-r26.md", "specs/conjugal.md",
    "ruling-candidates/current-intake-epoch-r1.md",
    "tools/check_adoption_ledger.py", "tools/check_current_intake_epoch.py",
    "tools/check_phase12_phase16_descendant_scope.py",
    "tests/test_adoption_ledger.py", "tests/test_current_adoption_ledger.py",
    "tests/test_current_intake_epoch.py", "tests/test_phase3_disposition_batch.py",
    "tests/test_phase5_stale_reconciliation.py",
    "tests/test_adversarialllm_utilization_shadow_doctrine.py",
    "tests/test_phase12_phase16_descendant_scope.py",
    "tests/test_phase17_dng_r60_publication.py",
}
CURRENT_ADOPTION_PATHS = {EPOCH_PATH, CURRENT_LEDGER, "adoption/current-token-control-r26.md"}


class IntakeError(ValueError):
    pass


def load(name: str):
    path = ROOT / "tools" / f"check_{name}.py"
    spec = importlib.util.spec_from_file_location(f"epoch_{name}", path)
    if spec is None or spec.loader is None:
        raise IntakeError("CHECKER_UNAVAILABLE")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(*args: str, allowed_codes: tuple[int, ...] = (0,)) -> bytes:
    # No shell and no caller-selected Git repository, replacement objects or
    # alternate object store. The existing isolation guard runs before this.
    if any(key in os.environ for key in UNSAFE_GIT_ENV) or any(key.startswith("GIT_CONFIG") for key in os.environ):
        raise IntakeError("GIT_OBJECT_INDIRECTION_REFUSED")
    environment = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    command = ["git", "--no-optional-locks", "--no-replace-objects", "--literal-pathspecs",
               "-c", "core.useReplaceRefs=false", *args]
    try:
        run = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise IntakeError("GIT_UNAVAILABLE_OR_TIMEOUT") from exc
    if run.returncode not in allowed_codes:
        raise IntakeError("GIT_COMMAND_FAILED")
    return run.stdout


def verify_git_object_isolation() -> None:
    common = Path(git("rev-parse", "--git-common-dir").decode().strip())
    if not common.is_absolute():
        common = ROOT / common
    if (common.resolve() / "objects" / "info" / "alternates").exists():
        raise IntakeError("GIT_ALTERNATE_OBJECT_STORE_REFUSED")
    if git("replace", "-l").strip():
        raise IntakeError("GIT_REPLACE_OBJECT_REFUSED")


def blob(subject: str, path: str) -> bytes:
    return git("show", f"{subject}:{path}")


def paths_changed(base: str, head: str = "HEAD") -> set[str]:
    return {p.decode("utf-8") for p in git("diff", "--name-only", "-z", base, head).split(b"\0") if p}


def ancestor(base: str, head: str = "HEAD") -> bool:
    return bool(git("merge-base", base, head).strip() == base.encode("ascii"))


def _pairs(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise IntakeError("DUPLICATE_JSON_KEY")
        value[key] = item
    return value


def parse_manifest(raw: bytes) -> dict:
    try:
        manifest = json.loads(raw, object_pairs_hook=_pairs)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise IntakeError("EPOCH_JSON_INVALID") from exc
    if not isinstance(manifest, dict) or set(manifest) != {
        "schema", "status", "bootstrapBase", "historicalWorkflow", "newPhase17",
        "originalFailedPhase17", "controlFiles", "authority",
    }:
        raise IntakeError("EPOCH_FIELDS_INVALID")
    expected = {
        "schema": SCHEMA, "status": "CANDIDATE_ZERO_AUTHORITY", "bootstrapBase": BOOTSTRAP_BASE,
        "historicalWorkflow": SEALED_WORKFLOW, "newPhase17": NEW_PHASE17,
        "originalFailedPhase17": FAILED_PHASE17,
    }
    if any(manifest[k] != value for k, value in expected.items()):
        raise IntakeError("EPOCH_SUBJECT_INVALID")
    authority = manifest["authority"]
    if not isinstance(authority, dict) or set(authority) != {"runtime", "projectAdoption", "fleetAdoption"} or any(x is not False for x in authority.values()):
        raise IntakeError("EPOCH_AUTHORITY_OVERCLAIM")
    files = manifest["controlFiles"]
    if not isinstance(files, dict) or set(files) != CONTROL_PATHS:
        raise IntakeError("CONTROL_CLOSED_SET_INVALID")
    for record in files.values():
        if not isinstance(record, dict) or set(record) != {"gitBlobOid", "bytes", "sha256"}:
            raise IntakeError("CONTROL_RECORD_INVALID")
        if type(record["bytes"]) is not int or record["bytes"] <= 0:
            raise IntakeError("CONTROL_RECORD_INVALID")
        if not isinstance(record["gitBlobOid"], str) or not SHA40.fullmatch(record["gitBlobOid"]):
            raise IntakeError("CONTROL_RECORD_INVALID")
        if not isinstance(record["sha256"], str) or not SHA256.fullmatch(record["sha256"]):
            raise IntakeError("CONTROL_RECORD_INVALID")
    return manifest


def verify_control_seal(manifest: dict) -> None:
    for path, expected in manifest["controlFiles"].items():
        raw = blob("HEAD", path)
        oid = git("rev-parse", f"HEAD:{path}").decode().strip()
        if len(raw) != expected["bytes"] or hashlib.sha256(raw).hexdigest() != expected["sha256"] or oid != expected["gitBlobOid"]:
            raise IntakeError(f"CONTROL_BYTES_CHANGED:{path}")
        try:
            working = (ROOT / path).read_bytes()
        except OSError as exc:
            raise IntakeError(f"CONTROL_WORKTREE_UNAVAILABLE:{path}") from exc
        # Permit Git's platform checkout line endings, not other working changes.
        if working.replace(b"\r\n", b"\n") != raw.replace(b"\r\n", b"\n"):
            raise IntakeError(f"CONTROL_WORKTREE_DRIFT:{path}")


def verify_retained_current_artifacts() -> None:
    for path in paths_changed(BOOTSTRAP_BASE):
        if path.startswith("adoption/") and path not in CURRENT_ADOPTION_PATHS:
            raise IntakeError(f"HISTORICAL_ARTIFACT_CHANGED:{path}")
        if path == "manifests/universal-provider-control-reconciliation-r26.json":
            raise IntakeError(f"HISTORICAL_ARTIFACT_CHANGED:{path}")


def classify_event(event: str, base: str) -> str:
    if event == "workflow_dispatch":
        return "MANUAL_VALIDATED_ZERO_AUTHORITY"
    if event not in {"pull_request", "push"}:
        raise IntakeError("EVENT_INVALID")
    if not isinstance(base, str) or not SHA40.fullmatch(base) or base == "0" * 40:
        raise IntakeError("EVENT_BASE_INVALID")
    try:
        git("cat-file", "-e", f"{base}^{{commit}}")
        if not ancestor(base) or not ancestor(BOOTSTRAP_BASE, base):
            raise IntakeError("EVENT_BASE_INVALID")
    except IntakeError as exc:
        raise IntakeError("EVENT_BASE_INVALID") from exc
    changed = paths_changed(base)
    present = git("ls-tree", "--name-only", base, "--", EPOCH_PATH).strip()
    if not present:
        if changed != BOOTSTRAP_CHANGED:
            raise IntakeError("BOOTSTRAP_CHANGE_SET_INVALID")
        return "BOOTSTRAP_CANDIDATE_REQUIRES_INDEPENDENT_REVIEW"
    if blob(base, EPOCH_PATH) != blob("HEAD", EPOCH_PATH):
        raise IntakeError("CONTROL_EPOCH_AMENDMENT_REQUIRED")
    if changed.intersection(CONTROL_PATHS):
        raise IntakeError("CONTROL_EPOCH_AMENDMENT_REQUIRED")
    return "CURRENT_INTAKE_VALIDATED_ZERO_AUTHORITY"


def verify_history(*, verify_remotes: bool = False) -> None:
    for name, path_name in (("phase2_disposition_batch", "BATCH_PATH"),
                            ("phase3_disposition_batch", "INTAKE_PATH"),
                            ("phase5_stale_reconciliation", "INTAKE_PATH")):
        module = load(name)
        subject = module.FROZEN_PUBLICATION
        batch = module.load_json(module._blob(subject, getattr(module, path_name)))
        module.verify_batch(batch, subject)
        if verify_remotes and name != "phase2_disposition_batch":
            module.verify_remotes(batch)
        print(f"PASS FROZEN: {name} {subject}")
    descendant = load("phase12_phase16_descendant_scope")
    descendant.verify_frozen_publications()
    descendant.verify_current_workflow(SEALED_WORKFLOW)
    print("PASS FROZEN: Phase12-16 and original sealed workflow")
    phase17 = load("phase17_dng_r60_publication")
    phase17.verify(NEW_PHASE17)
    for path in phase17.ALLOWED:
        if blob(NEW_PHASE17, path) != blob(FAILED_PHASE17, path):
            raise IntakeError("NEW_PHASE17_ORIGINAL_BYTES_CHANGED")
    try:
        phase17.verify(FAILED_PHASE17)
    except phase17.CheckFailure as exc:
        if "unexpected Phase 17 paths" not in str(exc):
            raise IntakeError("ORIGINAL_PHASE17_FAILURE_CHANGED") from exc
    else:
        raise IntakeError("ORIGINAL_PHASE17_FAILURE_ERASED")
    print("PASS NEW PROOF: Phase17; original publication still REFUSED; no historical rehabilitation")
    ledger = load("adoption_ledger")
    ledger.verify_ledger(ledger.load_ledger(ledger._blob(FROZEN_LEDGER, ledger.LEDGER_PATH)), FROZEN_LEDGER)
    print("PASS FROZEN: original adoption ledger")
    if not verify_remotes:
        print("REMOTES NOT VERIFIED; host-local discovery and optional source objects not reverified")


def verify(*, verify_remotes: bool = False) -> str:
    # Establish object isolation and seal every imported checker before import.
    verify_git_object_isolation()
    manifest = parse_manifest(blob("HEAD", EPOCH_PATH))
    verify_control_seal(manifest)
    verify_retained_current_artifacts()
    verify_history(verify_remotes=verify_remotes)
    ledger = load("adoption_ledger")
    ledger.verify_ledger(ledger.load_ledger(blob("HEAD", CURRENT_LEDGER)), "HEAD", current=True)
    return classify_event(os.environ.get("R26_SCOPE_EVENT", ""), os.environ.get("R26_SCOPE_BASE_SHA", ""))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-remotes", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = verify(verify_remotes=args.verify_remotes)
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(f"PASS: current intake epoch scope={result}; runtime/adoption authority=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
