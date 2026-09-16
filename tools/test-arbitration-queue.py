#!/usr/bin/env python
"""Proof for tools/arbitration-queue.py.

The tool's value is that it ADDRESSES a duty rather than listing a shelf, so the test is mostly
about the four states it refuses to collapse and about the two false answers that matter:

  * telling a project it owes nothing when it owes something (the duty stays invisible, which is
    the state five harvests were already in);
  * telling a project it owes something that is actually answered, or that nobody assigned to it.

It also pins the refusal behaviour: an unparseable or empty ledger must REFUSE, never report an
empty queue, because "nothing owed" and "I could not read the ledger" are different facts.

ROUND 2. The independent adversarial key refused this candidate with `reason=false-empty-queues`
and, separately, showed the MUTATION BAR was not met: five reverts left the suite green. Both are
answered in `run_round2_case` and in the strengthened `run_discovery_case`. Every assertion added
there is named for the item it proves (A..J) or for the mutation it kills (M1..M5), so a mutation
harness can report WHICH named assertion went red rather than only that something did.
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import re
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
| 2026-09-15 | 20260915T051905Z-86585ba5 | conjugal |

## Steward status -- test

**Arbiter named for `conjugal`, per K12 and section 5.**

- **PRIMARY: `airmypc`.** Its posture line reports a Codex key lane.
- **ALTERNATE: `dng-auto-processor`.** Named second.

**Arbiter named for `mlv-app`.**

- **PRIMARY: `cloudvore`.**
"""


def refuses(mod, fn, label, detail=""):
    """Assert that `fn()` REFUSES with exit 2 rather than answering."""
    try:
        fn()
    except SystemExit as exc:
        check(label, exc.code == 2, "exit=" + str(exc.code))
        return
    check(label, False, detail or "returned an answer instead of refusing")


def fixture(tmp, name):
    """A tool module pointed at a throwaway bus tree, with review-branch discovery stubbed."""
    mod = load()
    root = tmp / name
    fdir = root / "adjudications" / "factory-kernel"
    fdir.mkdir(parents=True, exist_ok=True)
    for p in ("conjugal", "airmypc", "mlv-app", "cloudvore", "adobe-ingester"):
        write(fdir / (p + ".md"), filing(p))
    write(fdir / "HARVESTS.md", LEDGER)
    mod.ROOT = str(root)
    mod.LEDGER = str(fdir / "HARVESTS.md")
    mod.FILINGS_DIR = str(fdir)
    mod._filings_on_review_branches = lambda: set()   # no git in this fixture
    return mod, fdir


def run_case(tmp):
    mod, fdir = fixture(tmp, "bus")
    # Not a filing: it sits in the directory but has no `project:` header.
    write(fdir / "README.md", "# How filings work\n\nSome prose.\n")

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

    print("case: a NON-EMPTY file that is not a ledger REFUSES (key defect D1)")
    write(fdir / "HARVESTS.md", "this is not a ledger\n")
    refuses(mod, mod.rows, "garbage that is merely non-empty refuses",
            "returned NOTHING OWED instead")
    write(fdir / "HARVESTS.md", LEDGER)

    print("case: a placeholder disposition does NOT clear the duty (key defect D3)")
    write(fdir / "conjugal.dispositions.md", "")
    rc = mod.main(["airmypc", "--json"])
    check("an empty dispositions file leaves the duty standing", rc == 1, "rc=" + str(rc))
    write(fdir / "conjugal.dispositions.md", "# TODO: rule on this\n")
    rc = mod.main(["airmypc", "--json"])
    check("a dispositions file with no arbiter line leaves the duty standing",
          rc == 1, "rc=" + str(rc))
    write(fdir / "conjugal.dispositions.md", "arbiter: airmypc\n")
    rc = mod.main(["airmypc", "--json"])
    check("a real disposition still clears it", rc == 0, "rc=" + str(rc))
    os.remove(str(fdir / "conjugal.dispositions.md"))

    print("case: a filing is found wherever its header sits, and a quoted example is not one (D4)")
    write(fdir / "latefiling.md", ("\n" * 45) + filing("latefiling"))
    write(fdir / "README.md",
          "# How filings work\n\nEvery filing opens like this:\n\n```\n"
          + filing("exampleproject") + "```\n")
    present = mod.filings_present()
    check("a header below line 40 is still a filing", "latefiling" in present, str(sorted(present)))
    check("a fenced example in the README is not a filing",
          "readme" not in present and "exampleproject" not in present, str(sorted(present)))
    os.remove(str(fdir / "latefiling.md"))
    write(fdir / "README.md", "# How filings work\n\nSome prose.\n")

    print("case: the documented UNDECORATED naming form is read (key defect D5)")
    plain = LEDGER.replace("- **PRIMARY: `airmypc`.**", "- PRIMARY: `airmypc`.")
    named = mod.namings(plain)
    check("an undecorated PRIMARY line still names an arbiter",
          ("PRIMARY", "airmypc") in named.get("conjugal", []), str(named.get("conjugal")))
    check("M5: prose merely containing the word PRIMARY names nobody",
          mod.NAMING_RE.search("the primary reason: airmypc was busy") is None, "matched prose")
    check("M5: an indented continuation line cannot mint a naming either",
          mod.NAMING_RE.search("    ... and the primary: cloudvore was not asked") is None,
          "matched a mid-sentence colon form")

    print("case: precedence is the steward DATE, not file position (key defect D6)")
    dated = ("## Steward status -- 2026-09-16\n\n"
             "**Arbiter named for `conjugal`.**\n\n"
             "- **PRIMARY: `airmypc`.**\n\n"
             "## Steward status -- 2026-09-15\n\n"
             "**Arbiter named for `conjugal`.**\n\n"
             "- **PRIMARY: `cloudvore`.** Older block, appended last.\n")
    named = mod.namings(dated)
    check("an older block appended last does NOT override a newer one",
          named.get("conjugal") == [("PRIMARY", "airmypc")], str(named.get("conjugal")))
    named = mod.namings(dated.replace("2026-09-16", "2026-09-14"))
    check("and when the appended block IS the newer one, it wins",
          named.get("conjugal") == [("PRIMARY", "cloudvore")], str(named.get("conjugal")))

    print("case: a named filing the inventory cannot see is NOT silently dropped (key defect D2)")
    os.remove(str(fdir / "mlv-app.md"))
    rows = mod.rows()
    lost = [r for r in rows if r["filing"] == "mlv-app"]
    check("it appears as FILING-NOT-FOUND, not as nothing",
          lost and lost[0]["state"] == mod.FILING_NOT_FOUND, str(lost))
    rc = mod.main(["cloudvore", "--json"])
    check("and its named arbiter still gets a non-zero exit", rc == 1, "rc=" + str(rc))
    print("case: FILING-NOT-FOUND cannot WEDGE an arbiter -- a disposition still clears it")
    write(fdir / "mlv-app.dispositions.md", "arbiter: cloudvore\n")
    rc = mod.main(["cloudvore", "--json"])
    check("a disposition clears a filing the inventory cannot see", rc == 0, "rc=" + str(rc))
    os.remove(str(fdir / "mlv-app.dispositions.md"))
    write(fdir / "mlv-app.md", filing("mlv-app"))

    print("case: an unreadable ledger REFUSES; it never reports an empty queue")
    write(fdir / "HARVESTS.md", "   \n")
    refuses(mod, mod.rows, "an empty ledger refuses")
    os.remove(str(fdir / "HARVESTS.md"))
    refuses(mod, mod.rows, "a missing ledger refuses")


# --------------------------------------------------------------------------------------------
# ROUND 2 -- every case below is a defect the independent key REPRODUCED, not a hypothetical.
# --------------------------------------------------------------------------------------------

def run_round2_case(tmp):
    mod, fdir = fixture(tmp, "bus2")

    # ---- A: ledger shape -------------------------------------------------------------------
    print("case A: ledger shape requires the harvest table header row, not a plausible heading")
    write(fdir / "HARVESTS.md",
          "## Steward status -- 2026-09-16\n\nqwertyuiop nonsense nonsense\n")
    refuses(mod, mod.rows,
            "A1: a lone steward heading over nonsense REFUSES, it does not answer NOTHING OWED")
    write(fdir / "HARVESTS.md",
          "| date | harvest | filing |\n|---|---|---|\nqwertyuiop nonsense nonsense\n")
    refuses(mod, mod.rows,
            "A2: a lone harvest table header over nonsense REFUSES")
    write(fdir / "HARVESTS.md",
          "# Factory-kernel harvest ledger\n\n"
          "| date | harvest | filing |\n|---|---|---|\n"
          "| 2026-09-15 | h1 | conjugal |\n")
    try:
        rows = mod.rows()
        check("A3: a real ledger that names nobody PARSES to zero assignments, it does not refuse",
              all(r["state"] == mod.UNASSIGNED for r in rows) and rows, str(rows))
    except SystemExit as exc:
        check("A3: a real ledger that names nobody PARSES to zero assignments, it does not refuse",
              False, "refused with exit " + str(exc.code))
    write(fdir / "HARVESTS.md", LEDGER)

    # ---- B: fenced examples ----------------------------------------------------------------
    print("case B: a fenced EXAMPLE is not a record, in the ledger or in a dispositions file")
    write(fdir / "conjugal.dispositions.md",
          "# Ruling pending\n\nThe file will eventually look like this:\n\n"
          "```\narbiter: airmypc\n```\n\nNothing has been ruled yet.\n")
    rc = mod.main(["airmypc", "--json"])
    check("B1: an `arbiter:` line inside a fence does NOT clear the duty", rc == 1, "rc=" + str(rc))
    os.remove(str(fdir / "conjugal.dispositions.md"))
    fenced_ledger = LEDGER + (
        "\n## Steward status -- 2029-01-01\n\n"
        "Worked example of how a re-naming is written:\n\n"
        "```\n"
        "**Arbiter named for `conjugal`.**\n\n"
        "- **PRIMARY: `cloudvore`.**\n"
        "```\n")
    named = mod.namings(fenced_ledger)
    check("B2: a naming block inside a fenced ledger example does NOT replace the live assignment",
          named.get("conjugal") == [("PRIMARY", "airmypc"),
                                    ("ALTERNATE", "dng-auto-processor")],
          str(named.get("conjugal")))
    # B3 comes from the sibling guard's independent key, which found the same bug in
    # tools/test-kernel-arbitration-route.py: if EITHER marker closes a fence, a ``` written inside
    # a ~~~ example turns fencing off and the rest of the example reads as live content.
    mixed_ledger = LEDGER + (
        "\n## Steward status -- 2029-01-01\n\n"
        "Worked example, written with tildes because it contains backticks:\n\n"
        "~~~\n"
        "```\n"
        "**Arbiter named for `conjugal`.**\n\n"
        "- **PRIMARY: `cloudvore`.**\n"
        "~~~\n")
    named = mod.namings(mixed_ledger)
    check("B3: a ``` inside a ~~~ example does not re-open the ledger to that example",
          named.get("conjugal") == [("PRIMARY", "airmypc"),
                                    ("ALTERNATE", "dng-auto-processor")],
          str(named.get("conjugal")))

    # B4/B5: an HTML comment is not a record either. This helper had NO comment handling while its
    # own sibling guard blanked both -- the threat-model pass found it by looking, not by a key round.
    commented = LEDGER + (
        "\n## Steward status -- 2029-02-02\n\n"
        "**Arbiter named for `conjugal`.**\n\n"
        "<!-- superseded, left in place for the record\n"
        "- **PRIMARY: `cloudvore`.**\n"
        "-->\n")
    check("B4: a commented-out naming does NOT replace the live assignment",
          mod.namings(commented).get("conjugal") == [("PRIMARY", "airmypc"),
                                                     ("ALTERNATE", "dng-auto-processor")],
          str(mod.namings(commented).get("conjugal")))
    after_comment = LEDGER.replace(
        "- **PRIMARY: `airmypc`.**",
        "<!-- superseded --> - **PRIMARY: `airmypc`.**")
    check("B5: a naming AFTER a closed inline comment is still read",
          ("PRIMARY", "airmypc") in mod.namings(after_comment).get("conjugal", []),
          str(mod.namings(after_comment).get("conjugal")))

    # ---- C: placeholder arbiter values -----------------------------------------------------
    print("case C: a placeholder value names nobody and does not clear a duty")
    for value, label in (("TODO", "C1: `arbiter: TODO` leaves the duty standing"),
                         ("", "C2/M4: a bare `arbiter:` with no value leaves the duty standing"),
                         ("``", "C3: a backtick-only arbiter value leaves the duty standing"),
                         ("TBD", "C4: `arbiter: TBD` leaves the duty standing"),
                         ("n/a", "C5: `arbiter: n/a` leaves the duty standing"),
                         ("-", "C6: `arbiter: -` leaves the duty standing")):
        write(fdir / "conjugal.dispositions.md", "arbiter: " + value + "\n")
        rc = mod.main(["airmypc", "--json"])
        check(label, rc == 1, "rc=" + str(rc))
    write(fdir / "conjugal.dispositions.md", "arbiter: airmypc\n")
    rc = mod.main(["airmypc", "--json"])
    check("C7: a real arbiter value still clears it", rc == 0, "rc=" + str(rc))
    os.remove(str(fdir / "conjugal.dispositions.md"))
    check("C8: a placeholder in the LEDGER names nobody either",
          mod.namings(LEDGER.replace("`airmypc`", "`TBD`")).get("conjugal")
          == [("ALTERNATE", "dng-auto-processor")],
          str(mod.namings(LEDGER.replace("`airmypc`", "`TBD`")).get("conjugal")))

    # ---- D: heading date state resets ------------------------------------------------------
    print("case D: ANY steward heading resets the date; only a well-formed ISO date sets it")
    base = ("## Steward status -- 2026-09-16\n\n"
            "**Arbiter named for `conjugal`.**\n\n"
            "- **PRIMARY: `airmypc`.**\n\n"
            "## Steward status -- %s\n\n"
            "**Arbiter named for `conjugal`.**\n\n"
            "- **PRIMARY: `cloudvore`.**\n")
    named = mod.namings(base % "undated")
    check("D1: an UNDATED heading does not inherit the previous block's date",
          named.get("conjugal") == [("PRIMARY", "airmypc")], str(named.get("conjugal")))
    named = mod.namings(base % "2026-9-15")
    check("D2: a NON-ISO heading does not inherit the previous block's date either",
          named.get("conjugal") == [("PRIMARY", "airmypc")], str(named.get("conjugal")))
    named = mod.namings(base % "2026-09-17")
    check("D3: a properly dated later heading still wins, so the reset is not a blanket ignore",
          named.get("conjugal") == [("PRIMARY", "cloudvore")], str(named.get("conjugal")))

    # ---- E: impossible dates ---------------------------------------------------------------
    print("case E: an impossible date is not a date")
    named = mod.namings(base % "9999-99-99")
    check("E1: `9999-99-99` does not outrank a real date; it ranks as undated",
          named.get("conjugal") == [("PRIMARY", "airmypc")], str(named.get("conjugal")))
    named = mod.namings(base % "2026-02-30")
    check("E2: `2026-02-30` is validated away too",
          named.get("conjugal") == [("PRIMARY", "airmypc")], str(named.get("conjugal")))

    # ---- F: names this tool cannot key on ---------------------------------------------------
    print("case F: an unkeyable name is surfaced and attributed to nobody -- it aborts no query")
    cyrillic = LEDGER.replace("`airmypc`", "`airmуpc`")
    # Wrapped, because the behaviour under test IS whether this refuses. Unwrapped, a regression to
    # the global refusal killed the whole suite at exit 2 before any named assertion ran, so the
    # mutation was caught only by an exit code -- which tells a reader that something broke, not what.
    try:
        named = mod.namings(cyrillic)
    except SystemExit as exc:
        check("F0: an unkeyable name does not abort the parse", False,
              "REFUSED exit=" + str(exc.code) + " -- one bad row stops every project's query")
        named = {}
    check("F1: a Cyrillic-confusable arbiter name is NOT truncated to an ASCII prefix",
          all(a != "airm" for _rank, a in named.get("conjugal", [])), str(named.get("conjugal")))
    check("F2: and it is recorded as unkeyable rather than dropped in silence",
          any("airm" in n for n in mod.UNKEYABLE_NAMES), str(mod.UNKEYABLE_NAMES))
    check("F3: the ASCII ledger is unaffected",
          mod.namings(LEDGER).get("conjugal") == [("PRIMARY", "airmypc"),
                                                  ("ALTERNATE", "dng-auto-processor")],
          str(mod.namings(LEDGER).get("conjugal")))
    # F4 is the availability bug the two advisors' evidence exposed together: `_clean_name` runs
    # while walking the WHOLE ledger, before main() filters by project, so raising there aborted
    # every OTHER project's query over one bad row -- and exit 2 reads, on the kernel's own stated
    # interface, as "you owe something".
    write(fdir / "HARVESTS.md", LEDGER.replace("`airmypc`", "`airmуpc`"))
    try:
        rc = mod.main(["mlv-app", "--json"])
    except SystemExit as exc:
        rc = "REFUSED exit=" + str(exc.code)
    check("F4: one unkeyable row does NOT abort an unrelated project's query", rc == 0,
          str(rc) + " -- a malformed row elsewhere reported a duty that does not exist")
    check("F5: the unkeyable record is per-run, not cumulative across runs",
          mod.main(["mlv-app", "--json"]) == 0 and len(mod.UNKEYABLE_NAMES) == len(
              set(mod.UNKEYABLE_NAMES)) and all(
              n for n in mod.UNKEYABLE_NAMES) and mod.UNKEYABLE_NAMES.count(
              mod.UNKEYABLE_NAMES[0]) == 1 if mod.UNKEYABLE_NAMES else True,
          str(mod.UNKEYABLE_NAMES))
    write(fdir / "HARVESTS.md", LEDGER)

    # ---- G: inventory keyed on the header, not the filename --------------------------------
    print("case G: the inventory is keyed on `project:`, so a rename cannot hide an assignment")
    os.remove(str(fdir / "conjugal.md"))
    write(fdir / "conjugаl.md", filing("conjugal"))   # Cyrillic a in the FILENAME only
    present = mod.filings_present()
    check("G1: a filing renamed to a confusable stem is still keyed on its header value",
          "conjugal" in present, str(sorted(present)))
    rc = mod.main(["airmypc", "--json"])
    check("G2: and its live assignment is still OWED to the named arbiter", rc == 1, "rc=" + str(rc))
    primary = [r for r in mod.rows()
               if r["filing"] == "conjugal" and r["arbiter"] == "airmypc"]
    check("G3: it reads OWED, not UNREACHABLE-ARBITER",
          primary and primary[0]["state"] == mod.OWED, str(primary))
    mod.filings_present()
    check("G4: the stem/header disagreement is REPORTED, not silently resolved",
          any("disagrees with its header" in n for n in mod.INVENTORY_NOTES),
          str(mod.INVENTORY_NOTES))
    os.remove(str(fdir / "conjugаl.md"))
    write(fdir / "conjugal.md", filing("conjugal"))
    mod.filings_present()
    check("G5: with no disagreement there is no note, so the note means something",
          not any("disagrees" in n for n in mod.INVENTORY_NOTES), str(mod.INVENTORY_NOTES))

    # ---- M2: two-field filing detection ----------------------------------------------------
    print("case M2: one header field is not a filing")
    write(fdir / "notafiling.md", "# notes\n\nproject: notafiling\n\nSome prose, no kernel line.\n")
    present = mod.filings_present()
    check("M2: a file with `project:` but no `kernel:` is NOT admitted to the inventory",
          "notafiling" not in present, str(sorted(present)))
    os.remove(str(fdir / "notafiling.md"))

    # ---- M3: same-day letter-suffix ranking ------------------------------------------------
    print("case M3: the same-day letter suffix orders blocks written on one day")
    sameday = ("## Steward status -- 2026-09-16b\n\n"
               "**Arbiter named for `conjugal`.**\n\n"
               "- **PRIMARY: `cloudvore`.**\n\n"
               "## Steward status -- 2026-09-16\n\n"
               "**Arbiter named for `conjugal`.**\n\n"
               "- **PRIMARY: `airmypc`.** Written earlier the same day, appended later.\n")
    named = mod.namings(sameday)
    check("M3: `2026-09-16b` outranks `2026-09-16` even when it appears FIRST in the file",
          named.get("conjugal") == [("PRIMARY", "cloudvore")], str(named.get("conjugal")))


def run_discovery_case(tmp):
    """Key defect D7: review-branch discovery was stubbed out in every case, so a mutation that
    disabled it entirely left the suite green. This case drives a REAL git repository.

    It also pins the failure direction that matters: when git cannot answer, the tool must REFUSE
    (exit 2). Returning an empty set made a broken instrument read as an absent duty, which is the
    one answer this tool exists to prevent.

    ROUND 2, item H: stubbing was only half the hole. The reviewer replaced the CALLER --
    `names |= _filings_on_review_branches()` with `names |= set()` -- and the suite stayed green,
    because nothing asserted that a review-only filing reaches the OWED list through
    `filings_present()`. `M1` below does exactly that, and asserts the state is OWED rather than
    merely a non-zero exit: with discovery disabled the same filing still exits 1, as
    FILING-NOT-FOUND, so an exit-status-only assertion is satisfied by the mutation.
    """
    import subprocess

    mod = load()
    root = tmp / "busrepo"
    fdir = root / "adjudications" / "factory-kernel"
    fdir.mkdir(parents=True, exist_ok=True)

    def git(*args):
        return subprocess.run(["git", "-C", str(root)] + list(args),
                              capture_output=True, text=True)

    if subprocess.run(["git", "--version"], capture_output=True).returncode != 0:
        check("git is available to test discovery", False, "git --version failed")
        return

    repo_ledger = (
        "# Factory-kernel harvest ledger\n\n"
        "| date | harvest | filing |\n|---|---|---|\n"
        "| 2026-09-16 | h1 | onreviewonly |\n\n"
        "## Steward status -- 2026-09-16\n\n"
        "**Arbiter named for `onreviewonly`.**\n\n"
        "- **PRIMARY: `onmaster`.**\n")

    git("init", "-q")
    git("config", "user.email", "test@example.invalid")
    git("config", "user.name", "test")
    write(fdir / "onmaster.md", filing("onmaster"))
    write(fdir / "HARVESTS.md", repo_ledger)
    git("add", "-A")
    git("commit", "-q", "-m", "master filing")
    git("checkout", "-q", "-b", "reviewbranch")
    write(fdir / "onreviewonly.md", filing("onreviewonly"))
    write(fdir / "README.md",
          "# not a filing\n\n```\n" + filing("quotedexample") + "```\n")
    git("add", "-A")
    git("commit", "-q", "-m", "review-branch filing")
    git("update-ref", "refs/remotes/origin/review/onreviewonly-kernel", "reviewbranch")
    # J: a SECOND review ref carrying the identical trees. The reviewer measured 30 blob reads for
    # 11 unique object ids; two refs over one commit is the smallest fixture that reproduces it.
    git("update-ref", "refs/remotes/origin/review/onreviewonly-kernel-dup", "reviewbranch")
    git("checkout", "-q", "master")

    mod.ROOT = str(root)
    mod.LEDGER = str(fdir / "HARVESTS.md")
    mod.FILINGS_DIR = str(fdir)

    print("case: a filing on an unmerged review branch is still a filing (R7.5), proven on real git")
    found = mod._filings_on_review_branches()
    check("discovery finds a filing that exists only on origin/review/*",
          "onreviewonly" in found, str(sorted(found)))
    check("and does not admit a fenced example from that branch's README",
          "readme" not in found and "quotedexample" not in found, str(sorted(found)))
    check("the local filing is still present too",
          "onmaster" in mod.filings_present(), str(sorted(mod.filings_present())))

    print("case H/M1: the CALLER of discovery is exercised end to end, not just the function")
    present = mod.filings_present()
    check("M1a: filings_present() carries the review-only filing into the inventory",
          "onreviewonly" in present, str(sorted(present)))
    rows = mod.rows()
    states = dict((r["filing"], r["state"]) for r in rows)
    check("M1b: a review-only filing reaches the owed list as OWED, not FILING-NOT-FOUND",
          states.get("onreviewonly") == mod.OWED, str(states))
    rc = mod.main(["onmaster", "--json"])
    check("M1c: and its named arbiter gets exit 1 from the real end-to-end path",
          rc == 1, "rc=" + str(rc))

    print("case I: the blob is fetched by a 40-hex OBJECT ID, not a <rev>:<path> string")
    seen_args = []
    real_run_probe = subprocess.run

    def recording_run(cmd, *a, **kw):
        seen_args.append(list(cmd))
        return real_run_probe(cmd, *a, **kw)

    mod.subprocess.run = recording_run
    try:
        mod._filings_on_review_branches()
    finally:
        mod.subprocess.run = real_run_probe
    combined = [c for c in seen_args
                for arg in c if arg.startswith("refs/") and ":" in arg]
    check("no git call joins a ref and a path with a colon",
          not combined,
          "git stats that combined string and, on Windows under a deep checkout, aborts with "
          "ENAMETOOLONG -- every review-branch filing then reads as absent: " + str(combined[:1]))
    catfile = [c for c in seen_args if "cat-file" in c and "blob" in c]
    check("I1: at least one blob read happened at all", bool(catfile), str(seen_args[-1:]))
    oids = [c[-1] for c in catfile]
    check("I2: every blob argument is a 40-hex object id, which `origin/review/...:path` is not",
          bool(oids) and all(re.match(r"^[0-9a-f]{40}$", o) for o in oids), str(oids[:3]))

    print("case J: blobs are read once per object id, not once per ref")
    check("J1: the number of cat-file calls equals the number of DISTINCT object ids",
          len(oids) == len(set(oids)), "%d calls for %d unique ids" % (len(oids), len(set(oids))))
    check("J2: and the two review refs really did present the same blobs",
          len([c for c in seen_args if "ls-tree" in c]) >= 2,
          str(len([c for c in seen_args if "ls-tree" in c])))

    print("case: when git cannot answer, discovery REFUSES -- it never returns an empty set (D2)")
    mod.ROOT = str(tmp / "not-a-repo")
    (tmp / "not-a-repo").mkdir(parents=True, exist_ok=True)
    refuses(mod, mod._filings_on_review_branches, "a non-repository refuses")

    real_run = subprocess.run

    def exploding_run(*a, **kw):
        raise OSError("git is not on PATH")

    mod.ROOT = str(root)
    mod.subprocess.run = exploding_run
    try:
        refuses(mod, mod._filings_on_review_branches, "git missing from PATH refuses")
    finally:
        mod.subprocess.run = real_run

    print("case J3: deduplication must not swallow a failure -- a broken read still refuses")
    calls = {"n": 0}

    def failing_catfile(cmd, *a, **kw):
        if "cat-file" in cmd:
            calls["n"] += 1
            raise OSError("object store unreadable")
        return real_run(cmd, *a, **kw)

    mod.subprocess.run = failing_catfile
    try:
        refuses(mod, mod._filings_on_review_branches,
                "J3: a blob read that fails REFUSES; the cache never turns it into an empty set")
    finally:
        mod.subprocess.run = real_run


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
            run_round2_case(Path(raw))
            run_discovery_case(Path(raw))
        finally:
            sys.stdout = real
        for line in out.getvalue().splitlines():
            if line.startswith("  ok ") or line.startswith("  FAIL") or line.startswith("case"):
                # The confusable-name cases carry non-ASCII in their failure detail, and a Windows
                # cp1252 console raises on it -- a test that CRASHES while reporting a failure
                # reports nothing at all, which is how the G mutation first looked like a bare
                # exit 1 with no named assertion.
                print(line.encode("ascii", "backslashreplace").decode("ascii"))
    if FAILURES:
        print("\nFAIL arbitration-queue: " + str(len(FAILURES)) + " check(s) failed")
        for f in FAILURES:
            print("  - " + f)
        return 1
    print("\nPASS arbitration-queue")
    return 0


if __name__ == "__main__":
    sys.exit(main())
