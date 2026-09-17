#!/usr/bin/env python
"""Derive the two numbers §5 finalisation needs and nothing currently reads.

Criterion 1 counts subjects CLOSED END-TO-END. That number lives in the ledger's `subjects` column
in prose, is never summed, and has been 0 at every harvest. Criterion 1 cannot be evaluated by
reading a filing; it reads the ledger. So the ledger should state the number.

Criterion 4's blocker is the opposite shape: harvest-status.py enumerates filings that EXIST, so a
roster member that has NEVER filed is invisible to it. That hole is why the steward's own filing
sat three runs unrouted. The roster is in the kernel's §6 mapping; the filings come from
harvest-status.py. Members in the first and not the second are DUE.

Writes nothing. Exits 1 when any member is due or any filing is open, so a board can wire it into a
cycle it already runs.

    python tools/kernel-e2e.py            # human
    python tools/kernel-e2e.py --json     # machine

Behaviour taken from layibabalola/softwarefactory-fleet-doctrine#70 (tools/kernel-due.py) per its
author's offer to "take the behaviour and discard the file" -- that PR's CI is RED and its suite
never executes, so it is treated as unreviewed. This implementation reads §6 (never spec filenames:
that bug made 30 of 30 members read as delinquent) and refuses an empty mapping rather than
reporting a clean fleet.
"""
import argparse
import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KERNEL = os.path.join(ROOT, "specs", "fleet-factory-kernel.md")
LEDGER = os.path.join(ROOT, "adjudications", "factory-kernel", "HARVESTS.md")

# Criterion 1 counts PROJECTS with >=1 closed subject; it never sums subjects. The previous
# reduction did both wrong at once: it accumulated the per-row number across rows and compared the
# SUM to 5, so five closed subjects in ONE project would have greened a criterion that requires five
# DISTINCT projects. Measured 2026-09-17; both numbers were 0, so it had never yet mattered.
#
# The extraction was also unsound in both directions. `(\d+)\s+(?:qualifying\s+)?end-to-end`
# silently returned None -- read as zero -- for the criterion's OWN wording:
#     "1 closed end-to-end with receipts"  -> None    (spec 5.1 says "one real subject end-to-end
#     "S1 closed end-to-end"               -> None     with receipts", so a truthful cell reads 0)
#     "one subject end-to-end"             -> None
# while a bare "5 end-to-end" in free prose written by the measured party would have counted 5.
# A cell that mentions end-to-end but carries no parseable count is now UNPARSED and REFUSES to be
# read as zero: an unreadable instrument must never be indistinguishable from a measured absence.
E2E_COUNT_RE = re.compile(r"(?<![\w.])(\d+)\s+(?:\w+\s+){0,2}?end-to-end", re.I)
E2E_MENTION_RE = re.compile(r"end-to-end", re.I)


class Refused(SystemExit):
    def __init__(self, msg):
        print("REFUSE kernel-e2e: " + msg, file=sys.stderr)
        super().__init__(2)


def roster():
    """Projects from the kernel's §6 fleet mapping.

    Reads the SECTION, never spec filenames: topic documents are not projects, and taking the
    roster from filenames is what made #70's first run report 30 of 30 members due.
    """
    if not os.path.isfile(KERNEL):
        raise Refused("kernel spec not found at {}".format(KERNEL))
    text = io.open(KERNEL, encoding="utf-8").read()
    m = re.search(r"^## 6\. Fleet mapping.*?(?=^## 7)", text, re.S | re.M)
    if not m:
        raise Refused("no '## 6. Fleet mapping' section; refusing to guess the roster")
    names = []
    for line in m.group(0).splitlines():
        if not line.startswith("|"):
            continue
        cell = line.split("|")[1].strip()
        if not cell or cell.lower() == "project" or set(cell) <= set("- "):
            continue
        # Roster cells carry annotations -- "cloudvore (DropBox Vault)",
        # "magic-lantern_dannephoto (no bus spec yet; ...)". The project KEY is the text before
        # the parenthesis; matching the whole cell against filing names reports two filed projects
        # as never-filed. Found by this tool's own first run: the same class of false-delinquent
        # defect that made #70 report 30 of 30 due, arriving by a different route.
        cell = re.split(r"\s*\(", cell, maxsplit=1)[0].strip()
        cell = cell.strip("`*_")
        if cell:
            names.append(cell)
    if not names:
        # An empty mapping must refuse, never report a clean fleet: "nobody is due" and "the
        # roster failed to parse" would otherwise be indistinguishable.
        raise Refused("§6 mapping parsed to zero projects; refusing to report a clean fleet")
    return sorted(set(names))


def filings(subject="factory-kernel"):
    """Filing states from harvest-status.py, the tool that already owns this."""
    p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "harvest-status.py"), subject],
                       capture_output=True, text=True, cwd=ROOT)
    out = {}
    for line in p.stdout.splitlines():
        m = re.match(r"^\s{2}(\S+)\s+(HARVESTED|STALE|UNHARVESTED)\b", line)
        if m:
            out[m.group(1)] = m.group(2)
    if not out and "filings=" not in p.stdout:
        raise Refused("harvest-status.py produced no filing rows")
    return out


def ledger_rows():
    if not os.path.isfile(LEDGER):
        raise Refused("ledger not found at {}".format(LEDGER))
    return [l for l in io.open(LEDGER, encoding="utf-8") if l.startswith("| 2026-")]


def e2e_and_totals():
    """Reduce the ledger to what criterion 1 actually asks: which PROJECTS closed a subject.

    Returns the per-project closed counts, the set of projects with >=1, and the subject total --
    the last for information only. Criterion 1 is evaluated on the PROJECT set, never the total.
    """
    names = ["FIT", "FRICTION", "BREAK", "N/A", "UNEXERCISED"]
    totals = dict.fromkeys(names, 0)
    rowed, unparsed, ambiguous = set(), [], []
    per_project = {}
    for r in ledger_rows():
        c = [x.strip() for x in r.split("|")]
        try:
            for i, n in enumerate(names):
                totals[n] += int(c[8 + i])
        except (ValueError, IndexError):
            unparsed.append(c[3] if len(c) > 3 else r[:40])
            continue
        rowed.add(c[3])
        cell = c[7]
        m = E2E_COUNT_RE.search(cell)
        if m:
            n = int(m.group(1))
            # A project's closed count is the MAX across its rows, never the sum: successive
            # harvests restate the same standing total, so summing double-counts one closure.
            per_project[c[3]] = max(per_project.get(c[3], 0), n)
        elif E2E_MENTION_RE.search(cell):
            ambiguous.append("{}: {!r}".format(c[3], cell[:80]))
        else:
            per_project.setdefault(c[3], 0)
    closed_projects = sorted(k for k, v in per_project.items() if v > 0)
    return {"closed_end_to_end": sum(per_project.values()),
            "closed_projects": closed_projects,
            "per_project_closed": per_project,
            "rows": len(ledger_rows()),
            "projects_in_ledger": sorted(rowed), "totals": totals,
            "unparsed": unparsed, "ambiguous_subject_cells": ambiguous}


def criterion_1_met(led):
    """Section 5.1: ">=5 member PROJECTS ... each covering at least one real subject end-to-end".

    Counted over DISTINCT PROJECTS, never over a sum of subjects. Extracted into its own function
    so the gate is testable; the predicate previously lived inline in main() and no test reached it.
    An ambiguous ledger blocks: a criterion cannot be certified from cells the instrument admits it
    could not read.
    """
    return len(led["closed_projects"]) >= 5 and not led["ambiguous_subject_cells"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--subject", default="factory-kernel")
    a = ap.parse_args()

    members = roster()
    filed = filings(a.subject)
    led = e2e_and_totals()

    never_filed = [m for m in members if m not in filed]
    open_filings = {k: v for k, v in filed.items() if v in ("STALE", "UNHARVESTED")}
    # A filing that exists but has no ledger row is invisible to criterion 1 -- the steward's own
    # filing is the worked example, which is why this is reported separately from "open".
    filed_but_unrowed = [k for k in filed if k not in led["projects_in_ledger"]]

    result = {"subject": a.subject, "roster": members,
              "closed_end_to_end": led["closed_end_to_end"],
              "closed_projects": led["closed_projects"],
              "per_project_closed": led["per_project_closed"],
              # Criterion 1: ">=5 member PROJECTS ... each covering at least one real subject
              # end-to-end". Counted over distinct projects. A ledger row whose subjects cell
              # mentions end-to-end but carries no parseable count is AMBIGUOUS, and an ambiguous
              # ledger cannot certify a criterion -- it blocks rather than reads as zero.
              "criterion_1_met": criterion_1_met(led),
              "criterion_1_projects": len(led["closed_projects"]),
              "ambiguous_subject_cells": led["ambiguous_subject_cells"],
              "ledger_rows": led["rows"], "ledger_totals": led["totals"],
              "projects_in_ledger": led["projects_in_ledger"],
              "never_filed": never_filed, "open_filings": open_filings,
              "filed_but_unrowed": filed_but_unrowed, "unparsed_rows": led["unparsed"]}
    due = bool(never_filed or open_filings or filed_but_unrowed)
    result["any_due"] = due

    if a.json:
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1 if due else 0

    t = led["totals"]
    print("kernel finalisation, derived {}".format(a.subject))
    print("  PROJECTS WITH >=1 CLOSED   : {}   (§5 criterion 1 needs >=5; counted by PROJECT, never summed)"
          .format(len(led["closed_projects"])))
    if led["closed_projects"]:
        print("      {}".format(", ".join(led["closed_projects"])))
    print("  closed subjects (info only): {}".format(led["closed_end_to_end"]))
    print("  ledger                     : {} rows over {} projects | {} FIT, {} FRICTION, {} BREAK, "
          "{} UNEXERCISED".format(led["rows"], len(led["projects_in_ledger"]),
                                  t["FIT"], t["FRICTION"], t["BREAK"], t["UNEXERCISED"]))
    print("  roster (§6)                : {} members".format(len(members)))
    print("")
    if never_filed:
        print("  NEVER FILED ({}) -- invisible to harvest-status.py, which enumerates filings that exist:"
              .format(len(never_filed)))
        for m in never_filed:
            print("      {}".format(m))
    if open_filings:
        print("  OPEN ({}):".format(len(open_filings)))
        for k, v in sorted(open_filings.items()):
            print("      {:<26} {}".format(k, v))
    if filed_but_unrowed:
        print("  FILED BUT NOT IN THE LEDGER ({}) -- counted by no criterion:".format(
            len(filed_but_unrowed)))
        for k in filed_but_unrowed:
            print("      {}".format(k))
    if led["unparsed"]:
        print("  UNPARSED LEDGER ROWS: {}".format(led["unparsed"]))
    if led["ambiguous_subject_cells"]:
        print("  AMBIGUOUS subjects cells ({}) -- mention end-to-end with no parseable count;"
              .format(len(led["ambiguous_subject_cells"])))
        print("  these BLOCK criterion 1 rather than reading as zero:")
        for x in led["ambiguous_subject_cells"]:
            print("      {}".format(x))
    print("")
    print("VERDICT: {}".format("MEMBERS DUE" if due else "no member due"))
    return 1 if due else 0


if __name__ == "__main__":
    sys.exit(main())
