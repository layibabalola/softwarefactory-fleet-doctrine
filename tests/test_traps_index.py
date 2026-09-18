"""The index must be DERIVED and must not touch TRAPS.md."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "traps-index.py"
SPEC = importlib.util.spec_from_file_location("traps_index", TOOL)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class TrapsIndexTests(unittest.TestCase):
    def test_checked_in_index_is_current(self):
        # The guard that keeps a generated enumeration from rotting.
        result = subprocess.run([sys.executable, str(TOOL), "--check"], cwd=str(ROOT),
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_wrapped_headings_collapse_to_one_entry(self):
        # Long headings are hard-wrapped with each continuation re-prefixed `##`. Counting `##`
        # lines overcounts findings by ~13% on the real file.
        runs = MODULE.heading_runs([
            "## A long finding that wraps",
            "## across three physical lines",
            "## (project, 2026-09-18, box)",
            "",
            "body text",
            "## A second, separate finding (other, 2026-09-18)",
        ])
        self.assertEqual(len(runs), 2)
        self.assertEqual(runs[0][0], 1)
        self.assertIn("wraps across three physical lines", runs[0][1])

    def test_h3_is_not_indexed_and_sections_are_classified(self):
        runs = MODULE.heading_runs(["### not a finding", "", "## Appended by MLV-App, 2026-08-09"])
        self.assertEqual(len(runs), 1)
        row = MODULE.classify(runs[0][1])
        self.assertEqual(row["kind"], "section")
        self.assertEqual(row["project"], "MLV-App")

    def test_entry_attribution_is_optional_not_required(self):
        with_attr = MODULE.classify("A finding (airmypc, 2026-09-05, virtual-ten)")
        self.assertEqual(with_attr["kind"], "entry")
        self.assertEqual(with_attr["date"], "2026-09-05")
        self.assertEqual(with_attr["project"], "airmypc")
        # An entry with no parenthetical must still be indexed, not dropped.
        bare = MODULE.classify("A finding with no attribution suffix")
        self.assertEqual(bare["kind"], "entry")
        self.assertEqual(bare["date"], "")

    def test_generating_the_index_does_not_modify_traps(self):
        before = (ROOT / "TRAPS.md").read_bytes()
        subprocess.run([sys.executable, str(TOOL), "--write"], cwd=str(ROOT), check=True,
                       capture_output=True)
        self.assertEqual((ROOT / "TRAPS.md").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
