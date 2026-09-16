#!/usr/bin/env python
"""Tell a project which filings are waiting on IT to arbitrate.

Kernel §5 forbids the steward adjudicating its own project's filing: a second project's arbiter, or
the owner, must rule and write that filing's `.dispositions.md`. The steward names the arbiter. That
naming then went nowhere, because nothing addresses it.

`bootstrap/PROMPT-A-sync-and-adopt.md` §4 has a sibling LIST what exists -- `ls -t
adjudications/*/*.md`, `ls-remote 'refs/heads/review/*'`. That is a pull with no addressing: a
project scanning the shelf cannot tell which item is assigned to it, and the assignment lives as
prose inside a ledger nobody queries by arbiter. Measured: Conjugal's own filing sat five harvests
with an arbiter named for the last of them and no way for that arbiter to find out.

Same construction as `tools/kernel-e2e.py`, applied to a third instance of one hole. That tool
exists because `harvest-status.py` enumerates filings that EXIST, so a member who never filed is
invisible. Here the duty exists but is not indexed by the party who owes it.

WHAT IT REFUSES TO COLLAPSE. Four states, because they call for four different actions:

    OWED            an arbiter is named, it is you, and no disposition exists
    UNASSIGNED      a filing is open and NO arbiter has been named -- the steward's move, not yours
    ANSWERED        a disposition file exists
    UNREACHABLE-ARBITER
                    an arbiter is named for a project that has never filed, so whether it can reach
                    a bench at all is unproven; recorded rather than assumed workable

Writes nothing. Exits 1 while anything is OWED to the project asked about, so a board can wire it
into a cycle it already runs. A reporter that always exits 0 is a warning, and a guard that warns
has failed open. An unparseable ledger REFUSES (exit 2) rather than reporting an empty queue --
"nothing owed" and "I could not read the ledger" are different facts.

    python tools/arbitration-queue.py airmypc
    python tools/arbitration-queue.py --all
    python tools/arbitration-queue.py airmypc --json
"""
import argparse
import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, "adjudications", "factory-kernel", "HARVESTS.md")
FILINGS_DIR = os.path.join(ROOT, "adjudications", "factory-kernel")

OWED = "OWED"
UNASSIGNED = "UNASSIGNED"
ANSWERED = "ANSWERED"
UNREACHABLE_ARBITER = "UNREACHABLE-ARBITER"

# "**PRIMARY: `airmypc`.**" / "- **ALTERNATE: `dng-auto-processor`.**" and undecorated variants.
NAMING_RE = re.compile(
    r"\*\*\s*(PRIMARY|ALTERNATE)\s*:\s*`?([A-Za-z0-9_.-]+)`?", re.I)
# "**Arbiter named for `conjugal`, per K12 and §5.**"
SUBJECT_RE = re.compile(
    r"arbiter\s+named\s+for\s+`?([A-Za-z0-9_.-]+)`?", re.I)


class Refused(SystemExit):
    def __init__(self, msg):
        sys.stderr.write("REFUSE arbitration-queue: " + msg + "\n")
        SystemExit.__init__(self, 2)


def read_ledger():
    if not os.path.isfile(LEDGER):
        raise Refused("ledger not found at " + LEDGER)
    try:
        text = io.open(LEDGER, encoding="utf-8").read()
    except Exception as exc:
        raise Refused("could not read the ledger: " + str(exc))
    if not text.strip():
        raise Refused("ledger is empty; refusing to report an empty queue")
    return text


def namings(text):
    """filing -> [(rank, arbiter)], taking the LAST naming block for each filing.

    A later steward block supersedes an earlier one, so the newest naming wins. Reading the first
    would pin a filing to an arbiter the steward has since replaced.
    """
    out = {}
    current = None
    for line in text.splitlines():
        m = SUBJECT_RE.search(line)
        if m:
            current = m.group(1).lower()
            out[current] = []          # a fresh naming block resets this filing's arbiters
            continue
        if current:
            n = NAMING_RE.search(line)
            if n:
                out[current].append((n.group(1).upper(), n.group(2).lower()))
    return dict((k, v) for k, v in out.items() if v)


def _is_filing(text):
    """A filing is identified by its HEADER, not by sitting in the directory.

    `README.md` lives beside the filings and is not one. Every filing opens with the kernel §4
    header, whose first field is `project:`. Testing for that is the same discipline the fleet
    readiness tool had to learn: detect by capability, never by filename.
    """
    for line in text.splitlines()[:40]:
        if line.strip().lower().startswith("project:"):
            return True
    return False


def filings_present():
    """Every filing that EXISTS, on master and on unmerged review branches alike.

    R7.5: "Consumers harvest review branches, not only master." A filing on an unmerged branch is
    still a filing, and a project whose filing lives there has not failed to file. Reading only the
    local directory called `airmypc` unfiled while its filing sat on
    origin/review/airmypc-kernel-2026-09-15 -- the same mistake, in a new place, that
    harvest-status.py makes by enumerating only what it can already see.
    """
    if not os.path.isdir(FILINGS_DIR):
        raise Refused("filings directory not found at " + FILINGS_DIR)
    names = set()
    for entry in os.listdir(FILINGS_DIR):
        if not entry.endswith(".md"):
            continue
        stem = entry[:-3]
        if stem.endswith(".dispositions") or stem.upper() == "HARVESTS":
            continue
        try:
            text = io.open(os.path.join(FILINGS_DIR, entry), encoding="utf-8",
                           errors="replace").read()
        except Exception:
            continue
        if _is_filing(text):
            names.add(stem.lower())
    names |= _filings_on_review_branches()
    return names


def _git(*args):
    try:
        p = subprocess.run(["git", "-C", ROOT, "--no-optional-locks"] + list(args),
                           capture_output=True, text=True, timeout=60,
                           encoding="utf-8", errors="replace")
        return p.stdout if p.returncode == 0 else ""
    except Exception:
        return ""


def _filings_on_review_branches():
    """Filing names visible on origin/review/* but not yet on master."""
    found = set()
    refs = _git("for-each-ref", "--format=%(refname)", "refs/remotes/origin/review/")
    rel = "adjudications/factory-kernel/"
    for ref in refs.split():
        listing = _git("ls-tree", "--name-only", ref, rel)
        for path in listing.splitlines():
            name = path.strip()
            if not name.endswith(".md"):
                continue
            stem = os.path.basename(name)[:-3]
            if stem.endswith(".dispositions") or stem.upper() == "HARVESTS":
                continue
            blob = _git("show", ref + ":" + name)
            if blob and _is_filing(blob):
                found.add(stem.lower())
    return found


def has_disposition(filing):
    return os.path.isfile(os.path.join(FILINGS_DIR, filing + ".dispositions.md"))


def rows():
    text = read_ledger()
    named = namings(text)
    present = filings_present()
    if not present:
        raise Refused("no filings found; refusing to report an empty queue")

    out = []
    for filing in sorted(present):
        arbiters = named.get(filing, [])
        if has_disposition(filing):
            out.append({"filing": filing, "state": ANSWERED, "arbiter": "",
                        "detail": filing + ".dispositions.md exists"})
            continue
        if not arbiters:
            out.append({"filing": filing, "state": UNASSIGNED, "arbiter": "",
                        "detail": "no arbiter named in the ledger; the steward names one"})
            continue
        for rank, arbiter in arbiters:
            state = OWED
            detail = rank.lower() + " arbiter; no disposition exists"
            if arbiter not in present:
                state = UNREACHABLE_ARBITER
                detail = (rank.lower() + " arbiter has never filed here, so its bench and seat "
                          "are unproven")
            out.append({"filing": filing, "state": state, "arbiter": arbiter, "detail": detail})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Which filings await arbitration by a given project.")
    ap.add_argument("project", nargs="?", help="the project asking what it owes")
    ap.add_argument("--all", action="store_true", help="every filing, whoever it is owed to")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)
    if not args.project and not args.all:
        ap.error("name a project, or pass --all")

    allrows = rows()
    if args.all:
        shown, owed = allrows, [r for r in allrows if r["state"] == OWED]
    else:
        who = args.project.lower()
        shown = [r for r in allrows if r["arbiter"] == who or r["state"] == UNASSIGNED]
        owed = [r for r in shown if r["state"] == OWED and r["arbiter"] == who]

    if args.json:
        json.dump({"project": args.project or "", "owed": len(owed), "rows": shown},
                  sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    else:
        head = "every filing" if args.all else ("filings addressed to " + args.project)
        print("arbitration queue, derived from the factory-kernel ledger -- " + head)
        print("  OWED %d" % len(owed))
        print("  UNASSIGNED means no arbiter has been named: the steward's move, not yours.")
        print("")
        for r in shown:
            print("  %-26s %-20s %-22s %s"
                  % (r["filing"], r["state"], r["arbiter"] or "-", r["detail"]))
        print("")
        print("VERDICT: " + ("NOTHING OWED" if not owed
                             else "%d FILING(S) AWAIT YOUR ARBITRATION" % len(owed)))
    return 1 if owed else 0


if __name__ == "__main__":
    sys.exit(main())
