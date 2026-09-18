"""Criterion 1 is a DISTINCT-PROJECT count, not a fleet sum.

specs/fleet-factory-kernel.md:219 requires "At least five member projects have filed, each
covering at least one real subject end-to-end". Summing across the ledger says true when ONE
project closes five -- a permissive failure, the direction nobody audits.
"""
import importlib.util
from pathlib import Path
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("kernel_e2e", ROOT / "tools/kernel-e2e.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def row(project, subjects):
    # Column layout per adjudications/factory-kernel/HARVESTS.md: c[3] project, c[7] subjects,
    # c[8..12] the FIT/FRICTION/BREAK/N-A/UNEXERCISED counts.
    cells = ["2026-09-14", "run-id", project, "sha", "r1", "code@r1", subjects,
             "0", "0", "0", "0", "0"]
    return "| " + " | ".join(cells) + " |\n"


def totals(rows):
    with mock.patch.object(MODULE, "ledger_rows", lambda: list(rows)):
        return MODULE.e2e_and_totals()


class KernelE2ECriterionOneTests(unittest.TestCase):
    def test_one_project_with_five_does_not_meet_criterion_1(self):
        # THE BUG: a fleet sum of 5 from a single project reported criterion_1_met true.
        led = totals([row("mlv-app", "5 end-to-end")])
        self.assertEqual(led["closed_end_to_end"], 5)
        self.assertEqual(led["projects_closing_end_to_end"], ["mlv-app"])
        self.assertLess(len(led["projects_closing_end_to_end"]), 5)

    def test_five_distinct_projects_with_one_each_meets_criterion_1(self):
        led = totals([row(p, "1 end-to-end") for p in
                      ("adobe-ingester", "agent-bridge", "airmypc", "cloudvore", "conjugal")])
        self.assertEqual(len(led["projects_closing_end_to_end"]), 5)

    def test_a_project_filing_twice_is_not_double_counted(self):
        # Rows are per-filing-per-harvest, so summing lets two harvests of one project inflate it.
        led = totals([row("mlv-app", "2 end-to-end"), row("mlv-app", "3 end-to-end")])
        self.assertEqual(led["projects_closing_end_to_end"], ["mlv-app"])
        self.assertEqual(led["closed_end_to_end_by_project"]["mlv-app"], 3)

    def test_prose_drift_is_named_not_silently_scored_zero(self):
        # E2E_RE reads a number out of a free-text cell. A miss must not look like a real zero.
        led = totals([row("cloudvore", "end-to-end: two subjects closed")])
        self.assertEqual(led["e2e_unreadable"], ["cloudvore"])
        self.assertEqual(led["projects_closing_end_to_end"], [])

    def test_a_genuine_zero_is_not_flagged_unreadable(self):
        led = totals([row("conjugal", "0 end-to-end (1 blocked at acceptance closure)")])
        self.assertEqual(led["e2e_unreadable"], [])
        self.assertEqual(led["projects_closing_end_to_end"], [])


if __name__ == "__main__":
    unittest.main()
