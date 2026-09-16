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
# D2: the ledger names an arbiter for a filing the inventory cannot see. The duty stands; it is
# the inventory that is incomplete. Counted as owed so a broken discovery can never read as calm.
FILING_NOT_FOUND = "FILING-NOT-FOUND"
# States that keep a duty alive, and so keep the exit status non-zero for the named arbiter.
OWED_STATES = (OWED, FILING_NOT_FOUND)

# "**PRIMARY: `airmypc`.**", "- **ALTERNATE: `dng-auto-processor`.**", and the same lines with the
# bold markers absent. The key's D5: requiring `**` meant the documented undecorated form was read as
# NO NAMING AT ALL, which is a false "nothing owed" -- the one answer this tool exists to prevent.
# Anchored to the start of the line (after an optional list marker and optional bold) so that prose
# merely mentioning the word PRIMARY cannot mint an assignment.
NAMING_RE = re.compile(
    r"^\s*(?:[-*+]\s+)?(?:\*\*)?\s*(PRIMARY|ALTERNATE)\s*:\s*(?:\*\*)?\s*`?([A-Za-z0-9_.-]+)`?",
    re.I)
# "**Arbiter named for `conjugal`, per K12 and §5.**"
SUBJECT_RE = re.compile(
    r"arbiter\s+named\s+for\s+`?([A-Za-z0-9_.-]+)`?", re.I)


# D1: a file that is merely non-empty is not a ledger. This tool's whole value is the difference
# between "nothing is owed" and "I could not read it", and `this is not a ledger` previously read as
# the former. A real ledger carries the harvest table or at least one dated steward status block.
LEDGER_SHAPE_RE = re.compile(
    r"^\s*\|\s*date\s*\|\s*harvest\s*\|\s*filing\s*\|"
    r"|^##+\s*Steward status", re.I | re.M)
# D6: "last in the file" is not "newest". Rank naming blocks by the date on their enclosing steward
# heading -- `## Steward status -- 2026-09-16b (...)` -- so an appended older block cannot override a
# newer one. The optional trailing letter orders same-day blocks.
STEWARD_DATE_RE = re.compile(
    r"^##+\s*Steward status\s*[^0-9]*(\d{4}-\d{2}-\d{2})([a-z]?)", re.I)


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
    if not LEDGER_SHAPE_RE.search(text):
        raise Refused("ledger does not parse as a factory-kernel harvest ledger (no harvest table "
                      "and no steward status block); refusing -- 'I could not parse it' and "
                      "'nobody owes anything' are different facts")
    return text


def namings(text):
    """filing -> [(rank, arbiter)] for the NEWEST naming block of each filing.

    D6, from the independent key: the first version took the LAST block in file order and called it
    the newest. An older steward block appended to the end therefore overrode a newer one, silently
    and with no way to notice. Precedence is now read from the date on the enclosing
    `## Steward status -- <date>` heading, with the optional same-day letter suffix ordering blocks
    written on one day, and file order used only to break a genuine tie. A naming block under no
    dated heading ranks below every dated one and can never override one.
    """
    return namings_ranked(text)


def namings_ranked(text):
    """As `namings`, but keeping every block so the newest can be chosen per filing."""
    out = {}
    current = None
    heading = (None, "")
    seq = 0
    for line in text.splitlines():
        h = STEWARD_DATE_RE.search(line)
        if h:
            heading = (h.group(1), (h.group(2) or "").lower())
            continue
        m = SUBJECT_RE.search(line)
        if m:
            current = m.group(1).lower()
            seq += 1
            key = (1 if heading[0] else 0, heading[0] or "", heading[1], seq)
            out.setdefault(current, []).append([key, []])
            continue
        if current:
            n = NAMING_RE.search(line)
            if n:
                out[current][-1][1].append((n.group(1).upper(), n.group(2).lower()))
    best = {}
    for filing, blocks in out.items():
        blocks = [b for b in blocks if b[1]]
        if not blocks:
            continue
        best[filing] = max(blocks, key=lambda b: b[0])[1]
    return best


def _is_filing(text):
    """A filing is identified by its HEADER, not by sitting in the directory or being quoted.

    Two D4 defects from the independent key, both false answers in opposite directions:

      * reading only the first 40 lines missed a real filing with front matter above its header,
        which erased a live arbitration duty;
      * reading inside fenced code blocks admitted the README's worked EXAMPLE of a filing header
        as a filing, minting a duty that does not exist.

    So: scan the whole file, skip fenced blocks, and require two header fields rather than one --
    prose that happens to start a line with `project:` is not a filing.
    """
    fenced = False
    seen = set()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            fenced = not fenced
            continue
        if fenced:
            continue
        low = line.lower()
        for field in ("project:", "kernel:"):
            if low.startswith(field):
                seen.add(field)
    return {"project:", "kernel:"} <= seen


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
    """Run git, or REFUSE.

    D2, from the independent key, and the worst defect it found: this used to return "" on any
    failure, so `git` missing from PATH, an unreadable ref listing or an unreadable blob all
    collapsed into "no filings on review branches" and the tool answered NOTHING OWED. A duty that
    disappears because the instrument broke is exactly the false negative this tool exists to
    prevent. A missing instrument is now a refusal (exit 2), never an absent duty.
    """
    try:
        p = subprocess.run(["git", "-C", ROOT, "--no-optional-locks"] + list(args),
                           capture_output=True, text=True, timeout=60,
                           encoding="utf-8", errors="replace")
    except Exception as exc:
        raise Refused("git could not be run (%s: %s); a missing instrument is not an absent duty"
                      % (type(exc).__name__, exc))
    if p.returncode != 0:
        raise Refused("git %s failed with status %d (%s); refusing rather than reporting a queue "
                      "derived from a partial inventory"
                      % (" ".join(args[:2]), p.returncode, (p.stderr or "").strip()[:120]))
    return p.stdout


def _filings_on_review_branches():
    """Filing names visible on origin/review/* but not yet on master.

    R7.5: "Consumers harvest review branches, not only master." A filing on an unmerged branch is
    still a filing. Every git call here refuses on failure (D2) rather than yielding an empty set.
    """
    found = set()
    refs = _git("for-each-ref", "--format=%(refname)", "refs/remotes/origin/review/")
    rel = "adjudications/factory-kernel/"
    for ref in refs.split():
        listing = _git("ls-tree", ref, rel)
        for entry in listing.splitlines():
            # "<mode> blob <oid>	<path>"
            head, _, name = entry.partition("	")
            name = name.strip()
            parts = head.split()
            if len(parts) < 3 or parts[1] != "blob" or not name.endswith(".md"):
                continue
            stem = os.path.basename(name)[:-3]
            if stem.endswith(".dispositions") or stem.upper() == "HARVESTS":
                continue
            # Read the blob BY OID, never as `<rev>:<path>`. Git stats that combined string to give
            # a friendlier error, and on Windows, under a deep checkout, the stat fails with
            # ENAMETOOLONG and git aborts -- so every filing on every review branch became
            # unreadable purely because of where the repository sits. The old code swallowed that
            # into "no filings on review branches"; with D2's refusal in place it became visible.
            blob = _git("cat-file", "blob", parts[2])
            if blob and _is_filing(blob):
                found.add(stem.lower())
    return found


def disposition_state(filing):
    """(exists, valid, why).

    D3, from the independent key: an EMPTY or placeholder `<filing>.dispositions.md` cleared the
    duty on the strength of its filename alone. Kernel section 5 says the arbiter "writes that
    filing's `.dispositions.md` with an `arbiter: <project or owner>` line", so that line is what
    makes a disposition a disposition. A file that does not carry it is an unanswered filing with a
    placeholder next to it, and the duty stands.
    """
    path = os.path.join(FILINGS_DIR, filing + ".dispositions.md")
    if not os.path.isfile(path):
        return False, False, ""
    try:
        text = io.open(path, encoding="utf-8", errors="replace").read()
    except Exception as exc:
        return True, False, "the dispositions file exists but could not be read: %s" % exc
    if not text.strip():
        return True, False, "the dispositions file is empty; a placeholder is not an answer"
    for line in text.splitlines():
        low = line.strip().lower().lstrip("*- ")
        if low.startswith("arbiter:") and low.split(":", 1)[1].strip(" *`"):
            return True, True, ""
    return True, False, ("the dispositions file carries no `arbiter: <project or owner>` line, "
                         "which section 5 requires; the duty stands")



def rows():
    text = read_ledger()
    named = namings(text)
    present = filings_present()
    if not present:
        raise Refused("no filings found; refusing to report an empty queue")

    # D2 (second half): reconcile the ledger's namings against the discovered inventory. A filing
    # the steward has NAMED an arbiter for, but which the inventory cannot see, used to be absent
    # from the output entirely -- so a broken or partial discovery answered NOTHING OWED. It is now
    # its own state and it counts as owed to the named arbiter: an assignment is not erased by the
    # evidence for it going missing.
    universe = sorted(set(present) | set(named))

    out = []
    for filing in universe:
        arbiters = named.get(filing, [])
        exists, valid, why = disposition_state(filing)
        if exists and valid:
            out.append({"filing": filing, "state": ANSWERED, "arbiter": "",
                        "detail": filing + ".dispositions.md exists and names an arbiter"})
            continue
        if not arbiters:
            out.append({"filing": filing, "state": UNASSIGNED, "arbiter": "",
                        "detail": "no arbiter named in the ledger; the steward names one"})
            continue
        for rank, arbiter in arbiters:
            state = OWED
            detail = rank.lower() + " arbiter; no disposition exists"
            if exists and not valid:
                detail = rank.lower() + " arbiter; " + why
            if filing not in present:
                state = FILING_NOT_FOUND
                detail = (rank.lower() + " arbiter; the ledger names this filing but the inventory "
                          "cannot see it -- treat the inventory as incomplete, not the duty as gone")
            elif arbiter not in present:
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
        shown, owed = allrows, [r for r in allrows if r["state"] in OWED_STATES]
    else:
        who = args.project.lower()
        shown = [r for r in allrows if r["arbiter"] == who or r["state"] == UNASSIGNED]
        owed = [r for r in shown if r["state"] in OWED_STATES and r["arbiter"] == who]

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
