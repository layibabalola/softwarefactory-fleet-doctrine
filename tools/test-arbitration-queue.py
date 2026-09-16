#!/usr/bin/env python
"""Proof for tools/arbitration-queue.py.

The tool's value is that it ADDRESSES a duty rather than listing a shelf, so the test is mostly
about the four states it refuses to collapse and about the two false answers that matter:

  * telling a project it owes nothing when it owes something (the duty stays invisible, which is
    the state five harvests were already in);
  * telling a project it owes something that is actually answered, or that nobody assigned to it.

It also pins the refusal behaviour: an unparseable or empty ledger must REFUSE, never report an
empty queue, because "nothing owed" and "I could not read the ledger" are different facts.
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "arbitration-queue.py"

FAILURES = []


def check(label, condition, detail=""):
    if condition:
        print("  ok   " + label)
    else:
        print("  FAIL " + label + ((" -- " + detail) if detail else ""))
        FAILURES.append(label)


def load():
    spec = importlib.util.spec_from_file_location("arbitration_queue", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    io.open(path, "w", encoding="utf-8", newline="\n").write(text)


def filing(project):
    return ("# Factory-kernel dogfood filing -- " + project + "\n\n"
            "project: " + project + "\n"
            "kernel: fleet-factory-kernel r4\n")


LEDGER = """# Factory-kernel harvest ledger

| date | harvest | filing |
|---|---|---|

## Steward status -- test

**Arbiter named for `conjugal`, per K12 and section 5.**

- **PRIMARY: `airmypc`.** Its posture line reports a Codex key lane.
- **ALTERNATE: `dng-auto-processor`.** Named second.

**Arbiter named for `mlv-app`.**

- **PRIMARY: `cloudvore`.**
"""


def run_case(tmp):
    mod = load()
    root = tmp / "bus"
    fdir = root / "adjudications" / "factory-kernel"
    fdir.mkdir(parents=True, exist_ok=True)
    for p in ("conjugal", "airmypc", "mlv-app", "cloudvore", "adobe-ingester"):
        write(fdir / (p + ".md"), filing(p))
    # Not a filing: it sits in the directory but has no `project:` header.
    write(fdir / "README.md", "# How filings work\n\nSome prose.\n")
    write(fdir / "HARVESTS.md", LEDGER)

    mod.ROOT = str(root)
    mod.LEDGER = str(fdir / "HARVESTS.md")
    mod.FILINGS_DIR = str(fdir)
    mod._filings_on_review_branches = lambda: set()   # no git in this fixture

    print("case: README.md is not a filing, because a filing is known by its header")
    present = mod.filings_present()
    check("README is excluded", "readme" not in present, str(sorted(present)))
    check("real filings are included", "conjugal" in present, str(sorted(present)))

    print("case: the named arbiter is TOLD, and the tool refuses while it is owed")
    rc = mod.main(["airmypc", "--json"])
    check("exits non-zero while a filing is owed", rc == 1, "rc=" + str(rc))
    owed = [r for r in mod.rows() if r["state"] == mod.OWED and r["arbiter"] == "airmypc"]
    check("conjugal is owed to airmypc", [r["filing"] for r in owed] == ["conjugal"], str(owed))

    print("case: a project owes nothing unless it was named")
    rc = mod.main(["adobe-ingester", "--json"])
    check("an unnamed project exits 0", rc == 0, "rc=" + str(rc))

    print("case: an answered filing is not owed to anyone")
    write(fdir / "conjugal.dispositions.md", "arbiter: airmypc\n")
    rc = mod.main(["airmypc", "--json"])
    check("a disposition clears the duty", rc == 0, "rc=" + str(rc))
    states = dict((r["filing"], r["state"]) for r in mod.rows())
    check("it reads ANSWERED, not OWED", states.get("conjugal") == mod.ANSWERED, str(states))
    os.remove(str(fdir / "conjugal.dispositions.md"))

    print("case: UNASSIGNED is the steward's move, and is not charged to a sibling")
    states = dict((r["filing"], r["state"]) for r in mod.rows())
    check("a filing with no naming reads UNASSIGNED",
          states.get("adobe-ingester") == mod.UNASSIGNED, str(states))
    check("it is not OWED to anybody", states.get("adobe-ingester") != mod.OWED, str(states))

    print("case: an arbiter named but never filed is flagged, not assumed workable")
    write(fdir / "HARVESTS.md", LEDGER.replace("`cloudvore`", "`ghostproject`"))
    rows = mod.rows()
    ghost = [r for r in rows if r["arbiter"] == "ghostproject"]
    check("reads UNREACHABLE-ARBITER",
          ghost and ghost[0]["state"] == mod.UNREACHABLE_ARBITER, str(ghost))
    check("and is therefore not counted as owed",
          all(r["state"] != mod.OWED for r in ghost), str(ghost))
    write(fdir / "HARVESTS.md", LEDGER)

    print("case: a LATER naming block supersedes an earlier one")
    write(fdir / "HARVESTS.md", LEDGER + """
## Steward status -- later

**Arbiter named for `conjugal`.**

- **PRIMARY: `cloudvore`.** Replaces the earlier naming.
""")
    named = mod.namings(io.open(str(fdir / "HARVESTS.md"), encoding="utf-8").read())
    check("the newest naming wins",
          named.get("conjugal") == [("PRIMARY", "cloudvore")], str(named.get("conjugal")))
    rc = mod.main(["airmypc", "--json"])
    check("the superseded arbiter no longer owes it", rc == 0, "rc=" + str(rc))
    write(fdir / "HARVESTS.md", LEDGER)

    print("case: an unreadable ledger REFUSES; it never reports an empty queue")
    write(fdir / "HARVESTS.md", "   \n")
    try:
        mod.rows()
        check("an empty ledger refuses", False, "returned instead of refusing")
    except SystemExit as exc:
        check("an empty ledger refuses", exc.code == 2, "exit=" + str(exc.code))
    os.remove(str(fdir / "HARVESTS.md"))
    try:
        mod.rows()
        check("a missing ledger refuses", False, "returned instead of refusing")
    except SystemExit as exc:
        check("a missing ledger refuses", exc.code == 2, "exit=" + str(exc.code))


def main():
    if not TOOL.exists():
        print("FAIL: tool not found at " + str(TOOL))
        return 1
    with tempfile.TemporaryDirectory(prefix="arbitration-queue-test-") as raw:
        out = io.StringIO()
        real = sys.stdout
        try:
            sys.stdout = out
            run_case(Path(raw))
        finally:
            sys.stdout = real
        for line in out.getvalue().splitlines():
            if line.startswith("  ok ") or line.startswith("  FAIL") or line.startswith("case:"):
                print(line)
    if FAILURES:
        print("\nFAIL arbitration-queue: " + str(len(FAILURES)) + " check(s) failed")
        for f in FAILURES:
            print("  - " + f)
        return 1
    print("\nPASS arbitration-queue")
    return 0


if __name__ == "__main__":
    sys.exit(main())
