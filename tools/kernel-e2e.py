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

E2E_RE = re.compile(r"(\d+)\s+(?:qualifying\s+)?end-to-end")


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
    """Verdict totals, plus the end-to-end count PER PROJECT.

    Criterion 1 is a distinct-project count, not a fleet sum: specs/fleet-factory-kernel.md:219
    requires "At least five member projects have filed, each covering at least one real subject
    end-to-end". A fleet sum says true when ONE project closes five, which fails permissively --
    the direction nobody audits. Rows are per-filing-per-harvest, so a project appearing in two
    harvests would also double-count; take that project's MAX rather than its sum.

    E2E_RE reads a number out of a free-text column. A steward writing "end-to-end: 2" or
    "1 closed end-to-end" yields no match, and a miss is indistinguishable from a real zero.
    When the cell mentions end-to-end but does not parse, name the row in `e2e_unreadable`
    instead of silently scoring it 0.
    """
    names = ["FIT", "FRICTION", "BREAK", "N/A", "UNEXERCISED"]
    totals = dict.fromkeys(names, 0)
    rowed, unparsed, unreadable = set(), [], []
    per_project = {}
    for r in ledger_rows():
        c = [x.strip() for x in r.split("|")]
        try:
            for i, n in enumerate(names):
                totals[n] += int(c[8 + i])
        except (ValueError, IndexError):
            unparsed.append(c[3] if len(c) > 3 else r[:40])
            continue
        project = c[3]
        rowed.add(project)
        subjects = c[7] if len(c) > 7 else ""
        m = E2E_RE.search(subjects)
        if m:
            per_project[project] = max(per_project.get(project, 0), int(m.group(1)))
        elif "end-to-end" in subjects.lower():
            unreadable.append(project)
    closed_projects = sorted(p for p, n in per_project.items() if n >= 1)
    return {"closed_end_to_end": sum(per_project.values()),
            "closed_end_to_end_by_project": per_project,
            "projects_closing_end_to_end": closed_projects,
            "rows": len(ledger_rows()),
            "projects_in_ledger": sorted(rowed), "totals": totals,
            "unparsed": unparsed, "e2e_unreadable": sorted(set(unreadable))}


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
              "closed_end_to_end_by_project": led["closed_end_to_end_by_project"],
              "projects_closing_end_to_end": led["projects_closing_end_to_end"],
              # Distinct projects with >=1, NOT the fleet sum. See e2e_and_totals().
              "criterion_1_met": len(led["projects_closing_end_to_end"]) >= 5,
              "e2e_unreadable_rows": led["e2e_unreadable"],
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
    print("  CLOSED END-TO-END SUBJECTS : {} across {} project(s)   "
          "(§5 criterion 1 needs >=5 projects with >=1 each)"
          .format(led["closed_end_to_end"], len(led["projects_closing_end_to_end"])))
    if led["e2e_unreadable"]:
        print("  E2E CELL UNREADABLE        : {}   (says end-to-end, no number parsed -- NOT scored 0)"
              .format(", ".join(led["e2e_unreadable"])))
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
    print("")
    print("VERDICT: {}".format("MEMBERS DUE" if due else "no member due"))
    return 1 if due else 0


if __name__ == "__main__":
    sys.exit(main())
