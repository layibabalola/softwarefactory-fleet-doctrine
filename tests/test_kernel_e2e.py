"""Tests for tools/kernel-e2e.py -- the instrument section 5 criterion 1 is read through.

It had no test at all until 2026-09-17, which is why three defects in one three-line reduction
survived: it SUMMED subjects where the criterion counts PROJECTS, it silently read the criterion's
OWN wording as zero, and it would have counted a bare prose number written by the measured party.

Filed by Conjugal (interim steward) on a review branch. Not ratified: section 5 forbids the steward
disposing of its own filing.
"""
import importlib.util
import io
import os
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("kernel_e2e", ROOT / "tools" / "kernel-e2e.py")
ke = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ke)

HEADER = (
    "| date | harvest | filing | blob | kernel | profile | subjects | FIT | FRICTION | BREAK |"
    " N/A | UNEXERCISED | unresolved BREAKs | arbiter |\n"
)


def row(project, subjects_cell):
    return ("| 2026-09-15 | h-1 | {} | blob | r1 | code@r1 | {} | 1 | 0 | 0 | 0 | 0 | 0 | astra |\n"
            .format(project, subjects_cell))


class Criterion1Gate(unittest.TestCase):
    """The gate itself. Previously inline in main(), reached by no test."""

    def led(self, closed_projects, ambiguous=(), per_project=None):
        # per_project MUST be populated: a gate mutated to read the SUM finds nothing to read
        # without it and stays green, which is a fixture that cannot fail. Measured 2026-09-17.
        pp = per_project if per_project is not None else {p: 1 for p in closed_projects}
        return {"closed_projects": list(closed_projects),
                "per_project_closed": dict(pp),
                "ambiguous_subject_cells": list(ambiguous)}

    def test_five_distinct_projects_meet_it(self):
        self.assertTrue(ke.criterion_1_met(self.led(["a", "b", "c", "d", "e"])))

    def test_four_projects_do_not(self):
        self.assertFalse(ke.criterion_1_met(self.led(["a", "b", "c", "d"])))

    def test_one_project_with_many_subjects_does_not_meet_it(self):
        """The defect of record: the old gate compared a SUM of subjects to 5.

        A single project closing five subjects satisfies no part of criterion 1, which counts
        member projects. This assertion is the whole point of the change.
        """
        self.assertFalse(ke.criterion_1_met(self.led(["alpha"], per_project={"alpha": 5})))

    def test_ambiguous_ledger_blocks_even_with_five_projects(self):
        self.assertFalse(ke.criterion_1_met(
            self.led(["a", "b", "c", "d", "e"], ["alpha: 'S1 and S2 closed end-to-end'"])))


class LedgerReduction(unittest.TestCase):
    def reduce(self, *rows):
        fd, path = tempfile.mkstemp(suffix=".md")
        os.close(fd)
        io.open(path, "w", encoding="utf-8").write(HEADER + "".join(rows))
        old = ke.LEDGER
        ke.LEDGER = path
        try:
            return ke.e2e_and_totals()
        finally:
            ke.LEDGER = old
            os.unlink(path)

    def test_criterion_own_wording_is_counted_not_read_as_zero(self):
        """Section 5.1 says 'at least one real subject end-to-end with receipts'.

        A project reporting closure in the criterion's own language must not count as zero.
        This is the defect that made a truthful success indistinguishable from a failure.
        """
        for cell in ("1 closed end-to-end with receipts",
                     "1 subject end-to-end",
                     "1 qualifying end-to-end"):
            got = self.reduce(row("alpha", cell))
            self.assertEqual(got["closed_projects"], ["alpha"], cell)
            self.assertEqual(got["ambiguous_subject_cells"], [], cell)

    def test_five_subjects_in_one_project_do_not_satisfy_criterion_1(self):
        """Criterion 1 counts PROJECTS. The old reduction summed and compared the SUM to 5."""
        got = self.reduce(row("alpha", "5 end-to-end"))
        self.assertEqual(got["closed_projects"], ["alpha"])
        self.assertEqual(len(got["closed_projects"]), 1)

    def test_five_distinct_projects_each_with_one_do_satisfy(self):
        got = self.reduce(*[row(p, "1 end-to-end") for p in "abcde"])
        self.assertEqual(len(got["closed_projects"]), 5)
        self.assertEqual(got["ambiguous_subject_cells"], [])

    def test_repeated_rows_for_one_project_are_not_double_counted(self):
        """Successive harvests restate a standing total; summing would invent closures."""
        got = self.reduce(row("alpha", "1 end-to-end"), row("alpha", "1 end-to-end"))
        self.assertEqual(got["closed_projects"], ["alpha"])
        self.assertEqual(got["closed_end_to_end"], 1)

    def test_unparseable_cell_blocks_rather_than_reading_as_zero(self):
        """An instrument that cannot read must refuse, not report a measured absence."""
        got = self.reduce(row("alpha", "S1 and S2 closed end-to-end"))
        self.assertEqual(got["closed_projects"], [])
        self.assertEqual(len(got["ambiguous_subject_cells"]), 1)
        self.assertIn("alpha", got["ambiguous_subject_cells"][0])

    def test_genuine_zero_is_not_ambiguous(self):
        """'0 end-to-end' is a measurement, not a failure to measure. It must not block."""
        got = self.reduce(row("alpha", "0 end-to-end (1 blocked at acceptance closure)"))
        self.assertEqual(got["closed_projects"], [])
        self.assertEqual(got["ambiguous_subject_cells"], [])

    def test_cell_with_no_mention_at_all_is_a_plain_zero(self):
        got = self.reduce(row("alpha", "3 filed; none delivered"))
        self.assertEqual(got["closed_projects"], [])
        self.assertEqual(got["ambiguous_subject_cells"], [])

    def test_verdict_columns_still_total(self):
        got = self.reduce(row("alpha", "0 end-to-end"), row("beta", "0 end-to-end"))
        self.assertEqual(got["totals"]["FIT"], 2)
        self.assertEqual(sorted(got["projects_in_ledger"]), ["alpha", "beta"])


if __name__ == "__main__":
    unittest.main()
