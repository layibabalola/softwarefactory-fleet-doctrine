"""The index must be DERIVED and must not touch TRAPS.md."""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "traps-index.py"


def load():
    spec = importlib.util.spec_from_file_location("traps_index", TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_checked_in_index_is_current():
    # The guard that keeps a generated enumeration from rotting.
    assert subprocess.run([sys.executable, str(TOOL), "--check"], cwd=str(ROOT)).returncode == 0


def test_wrapped_headings_collapse_to_one_entry():
    # Long headings are hard-wrapped with each continuation re-prefixed `##`. Counting `##`
    # lines overcounts findings; the reviewer measured ~13% inflation on the real file.
    runs = load().heading_runs([
        "## A long finding that wraps",
        "## across three physical lines",
        "## (project, 2026-09-18, box)",
        "",
        "body text",
        "## A second, separate finding (other, 2026-09-18)",
    ])
    assert len(runs) == 2
    assert runs[0][0] == 1
    assert "wraps across three physical lines" in runs[0][1]


def test_h3_is_not_indexed_and_sections_are_classified():
    module = load()
    runs = module.heading_runs(["### not a finding", "", "## Appended by MLV-App, 2026-08-09"])
    assert len(runs) == 1
    row = module.classify(runs[0][1])
    assert row["kind"] == "section" and row["project"] == "MLV-App"


def test_entry_attribution_is_optional_not_required():
    module = load()
    with_attr = module.classify("A finding (airmypc, 2026-09-05, virtual-ten)")
    assert with_attr["kind"] == "entry" and with_attr["date"] == "2026-09-05"
    assert with_attr["project"] == "airmypc"
    # An entry with no parenthetical must still be indexed, not dropped.
    bare = module.classify("A finding with no attribution suffix")
    assert bare["kind"] == "entry" and bare["date"] == ""


def test_generating_the_index_does_not_modify_traps():
    before = (ROOT / "TRAPS.md").read_bytes()
    subprocess.run([sys.executable, str(TOOL), "--write"], cwd=str(ROOT), check=True)
    assert (ROOT / "TRAPS.md").read_bytes() == before
