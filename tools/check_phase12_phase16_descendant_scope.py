#!/usr/bin/env python3
"""Verify frozen Phase12-16 publications, then classify a trusted descendant event."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PHASE12 = "990906b6ea861ca579e1336bcfe8f17dd80c83ae"
PHASE13 = "eca6e364cf03e388f0416e3f8e80fe4091321aa0"
PHASE14 = "95df488b2e2ec7120e992c0043d54b8e67a65dba"
PHASE15 = "488538ca15676823681e241f6be848de1d30a291"
PHASE16 = "8149c3f06811f85b833b28940017f2d05448cf5d"
PHASE17_REPAIR_BASE = "054b2569344fc3ed8da0cffc329c02f06b10c3da"
SHA40 = re.compile(r"[0-9a-f]{40}")

MUTABLE_BOOTSTRAP_ALLOWLIST = {
    ".github/workflows/disposition-intake.yml",
    "adoption/phase8/README.md",
    "tests/test_phase2_disposition_batch.py",
    "tests/test_phase3_disposition_batch.py",
    "tests/test_phase5_stale_reconciliation.py",
    "tests/test_phase8_integration.py",
    "tests/test_phase9_integration.py",
    "tests/test_phase10_integration.py",
    "tests/test_phase11_integration.py",
    "tests/test_phase12_integration.py",
    "tests/test_phase16_integration.py",
    "tests/test_phase12_phase16_descendant_scope.py",
    "tools/check_phase2_disposition_batch.py",
    "tools/check_phase3_disposition_batch.py",
    "tools/check_phase5_stale_reconciliation.py",
    "tools/check_phase8_integration.py",
    "tools/check_phase9_integration.py",
    "tools/check_phase10_integration.py",
    "tools/check_phase11_integration.py",
    "tools/check_phase12_phase16_descendant_scope.py",
}
BOOTSTRAP_CONTROL_PATHS = MUTABLE_BOOTSTRAP_ALLOWLIST
PHASE17_REPAIR_ALLOWLIST = {
    "tests/test_phase3_disposition_batch.py",
    "tests/test_phase12_phase16_descendant_scope.py",
    "tools/check_phase3_disposition_batch.py",
    "tools/check_phase12_phase16_descendant_scope.py",
}
PROTECTED_TRIGGER_PATHS = MUTABLE_BOOTSTRAP_ALLOWLIST | {
    "adoption/phase2/README.md",
    "adoption/phase2/r26-project-disposition-intake.json",
    "adoption/phase3/README.md",
    "adoption/phase3/r26-published-project-disposition-intake.json",
    "adoption/phase5/README.md",
    "adoption/phase5/r26-stale-project-reconciliation.json",
    "adoption/phase12/README.md",
    "adoption/phase12/r26-current-master-review-integration.json",
    "adoption/phase13/README.md",
    "adoption/phase13/r26-dng-install-evidence-publication.json",
    "adoption/phase14/README.md",
    "adoption/phase14/r26-mlv-task-definition-publication.json",
    "adoption/phase15/README.md",
    "adoption/phase15/r26-mlv-prelaunch-boundary-publication.json",
    "adoption/phase16/README.md",
    "adoption/phase16/phase15-review-consumption.json",
    "adoption/phase16/phase15-review-packet.json",
    "adoption/phase16/phase15-review-result.jsonl",
    "adoption/phase16/r26-phase15-review-publication.json",
    "adoption/universal-token-control-r26.json",
    "manifests/universal-provider-control-reconciliation-r26.json",
    "tests/test_phase6_candidate_reviews.py",
    "tests/test_phase7_owner_publication_requests.py",
    "tests/test_adoption_ledger.py",
    "tools/check_phase6_candidate_reviews.py",
    "tools/check_phase7_owner_publication_requests.py",
    "tools/check_adoption_ledger.py",
    *{f"tests/test_phase{phase}_integration.py" for phase in range(12, 17)},
    *{f"tools/check_phase{phase}_integration.py" for phase in range(12, 17)},
}

WORKFLOW_ROUTE_LINES = (
    b'        run: python -m unittest discover -s tests -p "test_phase2_disposition_batch.py" -v',
    b'        run: python -m unittest discover -s tests -p "test_adversarialllm_utilization_shadow_doctrine.py" -v',
    f"        run: python tools/check_phase2_disposition_batch.py --treeish {PHASE12}".encode(),
    b'        run: python -m unittest discover -s tests -p "test_phase3_disposition_batch.py" -v',
    f"        run: python tools/check_phase3_disposition_batch.py --treeish {PHASE12} ${{{{ env.R26_REMOTE_AUTH_CONFIGURED == 'true' && '--verify-remotes' || '' }}}}".encode(),
    b'        run: python -m unittest discover -s tests -p "test_phase5_stale_reconciliation.py" -v',
    f"        run: python tools/check_phase5_stale_reconciliation.py --treeish {PHASE12} ${{{{ env.R26_REMOTE_AUTH_CONFIGURED == 'true' && '--verify-remotes' || '' }}}}".encode(),
    b'        run: python -m unittest discover -s tests -p "test_phase6_candidate_reviews.py" -v',
    b"        run: python tools/check_phase6_candidate_reviews.py --treeish e7311e3038bbfeebe15cc10004f40b3795811659",
    b'        run: python -m unittest discover -s tests -p "test_phase7_owner_publication_requests.py" -v',
    b"        run: python tools/check_phase7_owner_publication_requests.py --treeish e7311e3038bbfeebe15cc10004f40b3795811659",
    b'        run: python -m unittest discover -s tests -p "test_phase8_integration.py" -v',
    b"        run: python tools/check_phase8_integration.py --treeish e7311e3038bbfeebe15cc10004f40b3795811659",
    b'        run: python -m unittest discover -s tests -p "test_phase9_integration.py" -v',
    b"        run: python tools/check_phase9_integration.py --treeish e7311e3038bbfeebe15cc10004f40b3795811659",
    b'        run: python -m unittest discover -s tests -p "test_phase10_integration.py" -v',
    b"        run: python tools/check_phase10_integration.py --treeish e7311e3038bbfeebe15cc10004f40b3795811659",
    b'        run: python -m unittest discover -s tests -p "test_phase11_integration.py" -v',
    b"        run: python tools/check_phase11_integration.py --treeish e7311e3038bbfeebe15cc10004f40b3795811659",
    b'        run: python -m unittest discover -s tests -p "test_phase12_integration.py" -v',
    f"        run: python tools/check_phase12_integration.py --treeish {PHASE12}".encode(),
    b'        run: python -m unittest discover -s tests -p "test_phase13_integration.py" -v',
    f"        run: python tools/check_phase13_integration.py --treeish {PHASE13}".encode(),
    b'        run: python -m unittest discover -s tests -p "test_phase14_integration.py" -v',
    f"        run: python tools/check_phase14_integration.py --treeish {PHASE14}".encode(),
    b'        run: python -m unittest discover -s tests -p "test_phase15_integration.py" -v',
    f"        run: python tools/check_phase15_integration.py --treeish {PHASE15}".encode(),
    b'        run: python -m unittest discover -s tests -p "test_phase16_integration.py" -v',
    f"        run: python tools/check_phase16_integration.py --treeish {PHASE16}".encode(),
    b'        run: python -m unittest discover -s tests -p "test_phase12_phase16_descendant_scope.py" -v',
    b"        run: python tools/check_phase12_phase16_descendant_scope.py",
    b'        run: python -m unittest discover -s tests -p "test_adoption_ledger.py" -v',
    b"        run: python tools/check_adoption_ledger.py --treeish HEAD",
)
WORKFLOW_ENV_LINES = (
    b"      R26_REMOTE_AUTH_CONFIGURED: ${{ secrets.R26_CROSS_REPO_READ_TOKEN != '' }}",
    b"      R26_SCOPE_EVENT: ${{ github.event_name }}",
    b"      R26_SCOPE_BASE_SHA: ${{ github.event_name == 'pull_request' && github.event.pull_request.base.sha || github.event_name == 'push' && github.event.before || '' }}",
)
WORKFLOW_TOKEN_LINE = b"          R26_REMOTE_GITHUB_TOKEN: ${{ secrets.R26_CROSS_REPO_READ_TOKEN }}"
WORKFLOW_TIMEOUT_LINE = b"    timeout-minutes: 30"
WORKFLOW_EVIDENCE_HEADER_BLOCK = b"\n".join((
    b"  evidence:",
    b"    env:",
    *WORKFLOW_ENV_LINES,
    b"    strategy:",
    b"      fail-fast: false",
    b"      matrix:",
    b"        os: [windows-latest, ubuntu-latest]",
    b'        python-version: ["3.13", "3.14"]',
    b"    runs-on: ${{ matrix.os }}",
    WORKFLOW_TIMEOUT_LINE,
))
WORKFLOW_PHASE3_REMOTE_BLOCK = b"\n".join((
    b"      - name: Verify exact zero-authority phase-3 distinctions locally",
    b"        env:",
    WORKFLOW_TOKEN_LINE,
    WORKFLOW_ROUTE_LINES[4],
))
WORKFLOW_PHASE5_REMOTE_BLOCK = b"\n".join((
    b"      - name: Verify phase-5 zero-authority reconciliation locally",
    b"        env:",
    WORKFLOW_TOKEN_LINE,
    WORKFLOW_ROUTE_LINES[6],
))
WORKFLOW_BYTES = 7304
WORKFLOW_SHA256 = "b51e56b8391c3d4cd6a854a38dcf81379c305d3c41b150d397ea57f781371e01"
UNSAFE_GIT_ENV = {
    "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_REPLACE_REF_BASE", "GIT_INDEX_FILE",
    "GIT_NAMESPACE",
}


class DescendantScopeError(ValueError):
    pass


def _load(name: str) -> Any:
    path = ROOT / "tools" / f"check_{name}_integration.py"
    spec = importlib.util.spec_from_file_location(f"bootstrap_{name}", path)
    if spec is None or spec.loader is None:
        raise DescendantScopeError(f"{name.upper()}_CHECKER_UNAVAILABLE")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


P12 = _load("phase12")
P13 = _load("phase13")
P14 = _load("phase14")
P15 = _load("phase15")
P16 = _load("phase16")


def _clean_git_env() -> dict[str, str]:
    environment = os.environ.copy()
    for key in tuple(environment):
        if key in UNSAFE_GIT_ENV or key.startswith("GIT_CONFIG"):
            environment.pop(key, None)
    return environment


def _git(args: list[str], *, text: bool = False, error: str = "GIT_COMMAND_FAILED") -> bytes | str:
    run = subprocess.run(
        ["git", "--no-replace-objects", "-c", "core.useReplaceRefs=false", *args],
        cwd=ROOT, env=_clean_git_env(), check=False, capture_output=True,
        text=text, encoding="utf-8" if text else None,
    )
    if run.returncode != 0:
        raise DescendantScopeError(error)
    return run.stdout


def _blob(treeish: str, path: str) -> bytes:
    return _git(["show", f"{treeish}:{path}"], error="WORKFLOW_BLOB_UNAVAILABLE")  # type: ignore[return-value]


def verify_git_object_isolation() -> None:
    if any(key in os.environ for key in UNSAFE_GIT_ENV) or any(key.startswith("GIT_CONFIG") for key in os.environ):
        raise DescendantScopeError("GIT_OBJECT_INDIRECTION_REFUSED")
    common = Path(str(_git(["rev-parse", "--git-common-dir"], text=True)).strip())
    if not common.is_absolute():
        common = ROOT / common
    if (common.resolve() / "objects" / "info" / "alternates").exists():
        raise DescendantScopeError("GIT_ALTERNATE_OBJECT_STORE_REFUSED")
    if str(_git(["replace", "-l"], text=True)).splitlines():
        raise DescendantScopeError("GIT_REPLACE_OBJECT_REFUSED")


def verify_frozen_publications() -> None:
    checks = (
        ("PHASE12", lambda: P12.verify_integration(PHASE12)),
        ("PHASE13", lambda: P13.verify(PHASE13)),
        ("PHASE14", lambda: P14.verify(PHASE14)),
        ("PHASE15", lambda: P15.verify(PHASE15)),
        ("PHASE16", lambda: P16.verify(PHASE16)),
    )
    for name, check in checks:
        try:
            check()
        except Exception as exc:
            raise DescendantScopeError(f"{name}_FROZEN_PUBLICATION_INVALID") from exc


def verify_current_workflow() -> None:
    workflow = _blob("HEAD", ".github/workflows/disposition-intake.yml")
    if len(workflow) != WORKFLOW_BYTES or hashlib.sha256(workflow).hexdigest() != WORKFLOW_SHA256:
        raise DescendantScopeError("WORKFLOW_BYTES_INVALID")
    for block in (WORKFLOW_EVIDENCE_HEADER_BLOCK, WORKFLOW_PHASE3_REMOTE_BLOCK, WORKFLOW_PHASE5_REMOTE_BLOCK):
        if workflow.count(block) != 1:
            raise DescendantScopeError("WORKFLOW_STRUCTURAL_BINDING_INVALID")
    lines = workflow.splitlines()
    if any(lines.count(route) != 1 for route in WORKFLOW_ROUTE_LINES):
        raise DescendantScopeError("WORKFLOW_ROUTE_COUNT_INVALID")
    positions = [lines.index(route) for route in WORKFLOW_ROUTE_LINES]
    if positions != sorted(positions):
        raise DescendantScopeError("WORKFLOW_ROUTE_ORDER_INVALID")
    if any(lines.count(line) != 1 for line in WORKFLOW_ENV_LINES):
        raise DescendantScopeError("WORKFLOW_ENV_BINDING_INVALID")
    if lines.count(WORKFLOW_TOKEN_LINE) != 2:
        raise DescendantScopeError("WORKFLOW_REMOTE_TOKEN_BINDING_INVALID")
    if lines.count(WORKFLOW_TIMEOUT_LINE) != 1:
        raise DescendantScopeError("WORKFLOW_TIMEOUT_INVALID")
    if b"--scope-event" in workflow or b"--scope-base" in workflow:
        raise DescendantScopeError("WORKFLOW_SCOPE_CLI_OVERRIDE")


def _changed_paths(base: str) -> set[str]:
    value = str(_git(["diff", "--name-only", f"{base}..HEAD"], text=True, error="EVENT_DIFF_UNAVAILABLE"))
    return set(value.splitlines())


def _is_ancestor(base: str) -> bool:
    run = subprocess.run(
        ["git", "--no-replace-objects", "merge-base", "--is-ancestor", base, "HEAD"],
        cwd=ROOT, env=_clean_git_env(), check=False, capture_output=True,
    )
    return run.returncode == 0


def classify_event(event_name: str, scope_base: str) -> str:
    if event_name == "workflow_dispatch":
        return "N/A_WORKFLOW_DISPATCH"
    if event_name not in {"pull_request", "push"}:
        raise DescendantScopeError("SCOPE_EVENT_INVALID")
    if not isinstance(scope_base, str) or SHA40.fullmatch(scope_base) is None:
        raise DescendantScopeError("SCOPE_BASE_INVALID")
    try:
        _git(["cat-file", "-e", f"{scope_base}^{{commit}}"], error="SCOPE_BASE_INVALID")
    except DescendantScopeError as exc:
        raise DescendantScopeError("SCOPE_BASE_INVALID") from exc
    if not _is_ancestor(scope_base):
        raise DescendantScopeError("SCOPE_BASE_INVALID")
    changed = _changed_paths(scope_base)
    if not changed.intersection(PROTECTED_TRIGGER_PATHS):
        return "N/A_NO_PHASE12_PHASE16_TRIGGER"
    if scope_base == PHASE16:
        if changed != MUTABLE_BOOTSTRAP_ALLOWLIST:
            raise DescendantScopeError("DESCENDANT_SCOPE_VIOLATION")
        return "APPLICABLE"
    if scope_base == PHASE17_REPAIR_BASE:
        if changed != PHASE17_REPAIR_ALLOWLIST:
            raise DescendantScopeError("DESCENDANT_SCOPE_VIOLATION")
        return "APPLICABLE_PHASE17_REPAIR"
    raise DescendantScopeError("BOOTSTRAP_SCOPE_CLOSED")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    try:
        verify_git_object_isolation()
        verify_frozen_publications()
        verify_current_workflow()
        scope = classify_event(os.environ.get("R26_SCOPE_EVENT", ""), os.environ.get("R26_SCOPE_BASE_SHA", ""))
    except DescendantScopeError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"PASS: frozen Phase12-16 publications exact; descendant scope={scope}; zero authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
