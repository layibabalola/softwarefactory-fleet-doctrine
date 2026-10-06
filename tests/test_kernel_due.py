#!/usr/bin/env python3
"""Hermetic tests for tools/kernel-due.py. No network, no bus refs, no repo state.

The negative cases are the point. This tool's first run reported 30 of 30 members DUE because it took
the roster from spec filenames, so topic documents were reported as delinquent projects. A due-check
that cries wolf is ignored by week two - which is the failure it exists to prevent - so the roster
parse and the "nothing due" path are both pinned here.
"""
import importlib.util, pathlib, sys, tempfile, unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("kernel_due", ROOT / "tools" / "kernel-due.py")
kd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kd)

KERNEL_DOC = """# Fleet factory kernel

**Status: `CANDIDATE r4 - DOGFOODING`.**

## 6. Fleet mapping (provisional)

| Project | Proposed profile | Confidence | Acceptance bar |
|---|---|---|---|
| cloudvore (DropBox Vault) | code | high | three identical green runs |
| adobe-ingester | code (automation probe) | medium | a real, user-present login |
| magic-lantern_dannephoto (no bus spec yet; mapped from its repo's CLAUDE.md) | hardware-in-loop | high | owner's camera |

`specs/context-ultra-salesforce.md` is a git-hygiene pattern document, not a project.

## 7. Next
"""


class RosterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = pathlib.Path(self.tmp.name)
        (self.repo / "specs").mkdir()
        (self.repo / "specs" / "fleet-factory-kernel.md").write_text(KERNEL_DOC, encoding="utf-8")
        self.addCleanup(self.tmp.cleanup)

    def test_roster_is_projects_not_documents(self):
        self.assertEqual(kd.roster(self.repo), ["adobe-ingester", "cloudvore", "magic-lantern_dannephoto"])

    def test_roster_drops_the_parenthetical_and_keeps_the_id(self):
        self.assertIn("magic-lantern_dannephoto", kd.roster(self.repo))
        self.assertNotIn("context-ultra-salesforce", kd.roster(self.repo))

    def test_empty_mapping_raises_rather_than_reporting_nothing_due(self):
        (self.repo / "specs" / "fleet-factory-kernel.md").write_text("# no mapping here\n", encoding="utf-8")
        with self.assertRaises(RuntimeError):
            kd.roster(self.repo)

    def test_kernel_revision(self):
        self.assertEqual(kd.kernel_revision(self.repo), 4)


class HeaderTests(unittest.TestCase):
    def test_zero_closed_subjects_is_detected_in_each_phrasing(self):
        for line in ("0 end-to-end", "0 closed end-to-end; 1 blocked at acceptance closure",
                     "none closed", "3 filed; 0 qualifying end-to-end"):
            self.assertEqual(kd.closed_subjects({"subjects": line}), 0, line)

    def test_a_nonzero_line_is_not_scored(self):
        # Deliberately not parsed into a number: a subjects line is prose a human must read.
        self.assertIsNone(kd.closed_subjects({"subjects": "1 closed end-to-end (S-K5-001)"}))

    def test_missing_subjects_line_is_unknown_not_zero(self):
        self.assertIsNone(kd.closed_subjects({}))

    def test_filed_revision(self):
        self.assertEqual(kd.filed_revision({"kernel": "fleet-factory-kernel r2"}), 2)
        self.assertIsNone(kd.filed_revision({}))


if __name__ == "__main__":
    unittest.main(verbosity=2)
