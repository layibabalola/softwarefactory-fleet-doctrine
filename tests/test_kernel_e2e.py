"""Criterion 1 is a DISTINCT-PROJECT count, not a fleet sum.

specs/fleet-factory-kernel.md:219 requires "At least five member projects have filed, each
covering at least one real subject end-to-end". Summing across the ledger says true when ONE
project closes five -- a permissive failure, the direction nobody audits.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def load():
    spec = importlib.util.spec_from_file_location("kernel_e2e", ROOT / "tools" / "kernel-e2e.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def row(project: str, subjects: str) -> str:
    # Column layout per adjudications/factory-kernel/HARVESTS.md: c[3] project, c[7] subjects,
    # c[8..12] the FIT/FRICTION/BREAK/N-A/UNEXERCISED counts.
    cells = ["2026-09-14", "run-id", project, "sha", "r1", "code@r1", subjects,
             "0", "0", "0", "0", "0"]
    return "| " + " | ".join(cells) + " |\n"


@pytest.fixture
def kernel(monkeypatch):
    module = load()

    def use(rows):
        monkeypatch.setattr(module, "ledger_rows", lambda: list(rows))
        return module.e2e_and_totals()

    return use


def test_one_project_with_five_does_not_meet_criterion_1(kernel):
    # THE BUG: a fleet sum of 5 from a single project used to report criterion_1_met true.
    led = kernel([row("mlv-app", "5 end-to-end")])
    assert led["closed_end_to_end"] == 5
    assert led["projects_closing_end_to_end"] == ["mlv-app"]
    assert len(led["projects_closing_end_to_end"]) < 5


def test_five_distinct_projects_with_one_each_meets_criterion_1(kernel):
    led = kernel([row(p, "1 end-to-end") for p in
                  ("adobe-ingester", "agent-bridge", "airmypc", "cloudvore", "conjugal")])
    assert len(led["projects_closing_end_to_end"]) == 5


def test_a_project_filing_twice_is_not_double_counted(kernel):
    # Rows are per-filing-per-harvest, so summing lets two harvests of one project inflate it.
    led = kernel([row("mlv-app", "2 end-to-end"), row("mlv-app", "3 end-to-end")])
    assert led["projects_closing_end_to_end"] == ["mlv-app"]
    assert led["closed_end_to_end_by_project"]["mlv-app"] == 3


def test_prose_drift_is_named_not_silently_scored_zero(kernel):
    # E2E_RE reads a number out of a free-text cell. A miss must not look like a real zero.
    led = kernel([row("cloudvore", "end-to-end: two subjects closed")])
    assert led["e2e_unreadable"] == ["cloudvore"]
    assert led["projects_closing_end_to_end"] == []


def test_a_genuine_zero_is_not_flagged_unreadable(kernel):
    led = kernel([row("conjugal", "0 end-to-end (1 blocked at acceptance closure)")])
    assert led["e2e_unreadable"] == []
    assert led["projects_closing_end_to_end"] == []
