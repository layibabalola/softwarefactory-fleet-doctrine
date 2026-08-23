#!/usr/bin/env python3
"""Verify frozen Phase12-16 publications, then classify a trusted descendant event."""

from __future__ import annotations

import argparse
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
SHA40 = re.compile(r"[0-9a-f]{40}")

BOOTSTRAP_CONTROL_PATHS = {
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
FORBIDDEN_PREFIXES = ("specs/", "manifests/", "snapshots/")
FORBIDDEN_EXACT = {
    "adoption/universal-token-control-r26.json",
    "tools/universal_provider_control.py",
    "RULINGS.md",
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
        if key in {
            "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_OBJECT_DIRECTORY",
            "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_REPLACE_REF_BASE", "GIT_INDEX_FILE",
            "GIT_NAMESPACE",
        } or key.startswith("GIT_CONFIG"):
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
    workflow = _blob("HEAD", ".github/workflows/disposition-intake.yml").decode("utf-8", errors="strict")
    required = (
        f"python tools/check_phase12_integration.py --treeish {PHASE12}",
        f"python tools/check_phase13_integration.py --treeish {PHASE13}",
        f"python tools/check_phase14_integration.py --treeish {PHASE14}",
        f"python tools/check_phase15_integration.py --treeish {PHASE15}",
        'test_phase16_integration.py" -v',
        f"python tools/check_phase16_integration.py --treeish {PHASE16}",
        'test_phase12_phase16_descendant_scope.py" -v',
        "python tools/check_phase12_phase16_descendant_scope.py",
    )
    positions = [workflow.find(command) for command in required]
    if any(workflow.count(command) != 1 for command in required):
        raise DescendantScopeError("WORKFLOW_ROUTE_COUNT_INVALID")
    if positions != sorted(positions):
        raise DescendantScopeError("WORKFLOW_ROUTE_ORDER_INVALID")
    frozen = "990906b6ea861ca579e1336bcfe8f17dd80c83ae"
    for phase in (2, 3, 5):
        command = f"python tools/check_phase{phase}_"
        rows = [line.strip() for line in workflow.splitlines() if command in line]
        if len(rows) != 1 or f"--treeish {frozen}" not in rows[0] or "--treeish HEAD" in rows[0]:
            raise DescendantScopeError("WORKFLOW_FROZEN_DISPOSITION_ROUTE_INVALID")


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
    if any(path.startswith(FORBIDDEN_PREFIXES) for path in BOOTSTRAP_CONTROL_PATHS) or BOOTSTRAP_CONTROL_PATHS & FORBIDDEN_EXACT:
        raise DescendantScopeError("BOOTSTRAP_ALLOWLIST_INVALID")
    changed = _changed_paths(scope_base)
    if not changed.intersection(BOOTSTRAP_CONTROL_PATHS):
        return "N/A_NO_PHASE12_PHASE16_TRIGGER"
    if not changed.issubset(BOOTSTRAP_CONTROL_PATHS):
        raise DescendantScopeError("DESCENDANT_SCOPE_VIOLATION")
    return "APPLICABLE"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope-event", default=os.environ.get("R26_SCOPE_EVENT", ""))
    parser.add_argument("--scope-base", default=os.environ.get("R26_SCOPE_BASE_SHA", ""))
    args = parser.parse_args(argv)
    try:
        verify_frozen_publications()
        verify_current_workflow()
        scope = classify_event(args.scope_event, args.scope_base)
    except DescendantScopeError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"PASS: frozen Phase12-16 publications exact; descendant scope={scope}; zero authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
