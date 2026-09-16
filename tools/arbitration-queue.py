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

ROUND-2 REPAIRS (independent adversarial key, reason=false-empty-queues). Every one of A..J below
was REPRODUCED, and every one of them produced a false NOTHING OWED or a silently dropped duty:

    A  ledger shape was satisfied by a lone steward heading, or a lone table header row, over
       nonsense -- see LEDGER_SHAPE and the documented parse/refuse line there
    B  fenced examples were read as live content, in the ledger AND in a dispositions file
    C  placeholder arbiter values (`arbiter: TODO`, a bare `arbiter:`) cleared a duty
    D  an undated or non-ISO steward heading inherited the previous block's date
    E  an impossible date (`9999-99-99`) outranked every real one
    F  a non-ASCII project name was silently TRUNCATED by the naming token class
    G  the inventory was keyed on the FILENAME stem, so a rename hid a live assignment
    H  the test suite never exercised the CALLER of review-branch discovery
    I  the blob-by-OID assertion accepted `origin/review/...:path` in place of an object id
    J  11 unique blobs were read 30 times
"""
import argparse
import datetime
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

# G: where a filing's FILENAME and its `project:` header disagree, the header wins (it is what the
# ledger names) but the disagreement is REPORTED. Saying "I preferred the header" out loud is the
# difference between a resolved ambiguity and a hidden one.
INVENTORY_NOTES = []

# "**PRIMARY: `airmypc`.**", "- **ALTERNATE: `dng-auto-processor`.**", and the same lines with the
# bold markers absent. The key's D5: requiring `**` meant the documented undecorated form was read as
# NO NAMING AT ALL, which is a false "nothing owed" -- the one answer this tool exists to prevent.
# Anchored to the start of the line (after an optional list marker and optional bold) so that prose
# merely mentioning the word PRIMARY cannot mint an assignment.
#
# F: the token class used to be `[A-Za-z0-9_.-]+`, which SILENTLY TRUNCATED `airm<U+0443>pc` to
# `airm` -- the queried arbiter then got NOTHING OWED for a filing that named it. The token is now
# wide (anything that is not whitespace, a backtick or an asterisk) and is VALIDATED afterwards by
# `_clean_name`, which REFUSES on a non-ASCII name rather than truncating or ignoring it.
NAMING_RE = re.compile(
    r"^\s*(?:[-*+]\s+)?(?:\*\*)?\s*(PRIMARY|ALTERNATE)\s*:\s*(?:\*\*)?\s*"
    r"(?:`([^`\n]*)`|([^\s`*]*))",
    re.I)
# "**Arbiter named for `conjugal`, per K12 and §5.**"
SUBJECT_RE = re.compile(
    r"arbiter\s+named\s+for\s+(?:`([^`\n]*)`|([^\s`*]+))", re.I)

# C: a value that is a placeholder is not a value. `arbiter: TODO` next to an unanswered filing is
# an unanswered filing with a note on it, and it cleared the duty. Same list governs the ledger's
# naming values -- `PRIMARY: TBD` names nobody.
PLACEHOLDER_VALUES = frozenset(
    ["todo", "tbd", "tbc", "none", "n/a", "na", "pending", "?", "-", "--", "---",
     "...", "xxx", "tba", "unknown", "unassigned"])

# A: the ledger's DEFINING structure is the harvest table header row. Nothing else identifies this
# file: a steward heading is prose anybody can type, and the round-1 shape check accepted a file
# whose entire content was one such heading followed by nonsense.
LEDGER_TABLE_HEADER_RE = re.compile(
    r"^\s*\|\s*date\s*\|\s*harvest\s*\|\s*filing\s*\|", re.I)
LEDGER_TABLE_SEPARATOR_RE = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
# Any `## Steward status` heading at all -- D: this RESETS the date state whether or not it carries
# a well-formed date, so an undated or malformed heading can never leave the parser holding the
# PREVIOUS block's date and let a stale block outrank a newer one.
STEWARD_HEADING_RE = re.compile(r"^##+\s*Steward status\b", re.I)
# D6: "last in the file" is not "newest". Rank naming blocks by the date on their enclosing steward
# heading -- `## Steward status -- 2026-09-16b (...)` -- so an appended older block cannot override a
# newer one. The optional trailing letter orders same-day blocks. E: the date is then validated with
# `datetime.date`, so `9999-99-99` is not a date and ranks as undated instead of above everything.
STEWARD_DATE_RE = re.compile(
    r"^##+\s*Steward status\s*[^0-9]*(\d{4}-\d{2}-\d{2})([a-z]?)", re.I)


class Refused(SystemExit):
    def __init__(self, msg):
        sys.stderr.write("REFUSE arbitration-queue: " + msg + "\n")
        SystemExit.__init__(self, 2)


def _unfenced_lines(text):
    """Every line of `text`, with the CONTENT of ``` / ~~~ fenced blocks blanked out.

    B: a worked EXAMPLE is not a record. The round-1 tool read fenced blocks as live content in two
    places -- a `<filing>.dispositions.md` whose only `arbiter:` line sat inside a fence CLEARED the
    duty, and a naming block inside a fenced example in the ledger REPLACED the live assignment.
    `_is_filing` already skipped fences correctly; this lifts that one behaviour into a helper and
    routes the ledger parse, the shape check and the disposition parse through it.

    Lines are blanked rather than dropped so that file positions (used only to break a genuine
    same-rank tie) stay honest.

    Only the marker that OPENED a fence can close it. The sibling guard
    `tools/test-kernel-arbitration-route.py` carried the same "either marker toggles" bug, and its
    independent key showed the consequence: a ``` inside a ~~~ block turns fencing OFF, so the rest
    of the document reads as live content while it is in fact all inside one example.
    """
    out = []
    fence = None
    for line in text.splitlines():
        stripped = line.strip()
        marker = "```" if stripped.startswith("```") else (
            "~~~" if stripped.startswith("~~~") else None)
        if marker and fence is None:
            fence = marker
            out.append("")
            continue
        if fence is not None:
            if marker == fence:
                fence = None
            out.append("")
            continue
        out.append(line)
    return out


def _clean_name(raw):
    """Normalise a captured project name, or REFUSE if it cannot be one. May return "".

    F, reproduced by the independent key: `airm<CYRILLIC U>pc` was matched by a `[A-Za-z0-9_.-]+`
    token class as `airm`, so the ledger's live naming of `airmypc` reached the queue under a name
    nobody queries and the real arbiter was told NOTHING OWED. Truncation and silent skipping are
    both false-empty producers, so a name that is not ASCII is now a REFUSAL with the offending
    text quoted: the operator is told the ledger carries a name this tool cannot key on, which is a
    fact they can act on, rather than being handed a calm empty queue.
    """
    name = (raw or "").strip().strip("*").strip().strip("`").strip()
    # Trailing sentence punctuation from an undecorated form: "PRIMARY: airmypc." / "..., per K12".
    name = name.rstrip(".,;:)]}").strip()
    if not name:
        return ""
    try:
        name.encode("ascii")
    except UnicodeEncodeError:
        raise Refused(
            "a project name in the factory-kernel ledger is not ASCII (%r). Round 1 truncated it "
            "to its leading ASCII run, which routed a live duty to a name nobody queries and told "
            "the real arbiter NOTHING OWED. Refusing rather than guessing which project is meant."
            % (name,))
    if not re.match(r"^[A-Za-z0-9_.-]+$", name):
        raise Refused(
            "a project name in the factory-kernel ledger carries characters this tool cannot key "
            "on (%r); refusing rather than silently dropping the assignment it belongs to" % name)
    if name.lower() in PLACEHOLDER_VALUES:
        return ""
    return name.lower()


def _pick(match, a, b):
    """The backticked capture if it matched, else the bare one."""
    got = match.group(a)
    return got if got is not None else (match.group(b) or "")


def _ledger_is_shaped(lines):
    """(ok, why). A: what makes this file a ledger, and where the parse/refuse line is drawn.

    THE LINE, decided here and stated out loud because round 1 drew it wrong:

      * "could not parse" -> REFUSE (exit 2). The file does not carry the harvest table header row
        (`| date | harvest | filing | ...`) OUTSIDE a fence, or it carries that row and nothing
        else -- no data row and no steward status heading. Round 1 accepted both of the reviewer's
        probes here (a lone steward heading over nonsense; a lone table header over nonsense) and
        answered NOTHING OWED, exit 0.
      * "parsed to no assignments" -> a LEGITIMATE answer, exit 0/1 as the rows dictate. The file
        IS a ledger -- header row plus at least one harvest row or one steward status block -- and
        simply names no arbiter for anyone yet. A real ledger the day before its first naming looks
        exactly like this, and refusing on it would make the tool unusable in a cycle.

    In short: the DEFINING STRUCTURE plus at least one unit of content. Shape, never sentiment.
    """
    header = False
    body = False
    steward = False
    for line in lines:
        if LEDGER_TABLE_HEADER_RE.match(line):
            header = True
            continue
        if STEWARD_HEADING_RE.match(line):
            steward = True
            continue
        if line.lstrip().startswith("|") and not LEDGER_TABLE_SEPARATOR_RE.match(line):
            if line.count("|") >= 4:
                body = True
    if not header:
        return False, ("no harvest table header row (`| date | harvest | filing | ...`) outside a "
                       "fenced block; that row is what makes this file a ledger")
    if not (body or steward):
        return False, ("the harvest table header row is present but the file carries no harvest "
                       "row and no `## Steward status` block; a header over nonsense is not a "
                       "ledger that parsed to no assignments")
    return True, ""


def read_ledger():
    if not os.path.isfile(LEDGER):
        raise Refused("ledger not found at " + LEDGER)
    try:
        text = io.open(LEDGER, encoding="utf-8").read()
    except Exception as exc:
        raise Refused("could not read the ledger: " + str(exc))
    if not text.strip():
        raise Refused("ledger is empty; refusing to report an empty queue")
    ok, why = _ledger_is_shaped(_unfenced_lines(text))
    if not ok:
        raise Refused("ledger does not parse as a factory-kernel harvest ledger -- %s; refusing -- "
                      "'I could not parse it' and 'nobody owes anything' are different facts" % why)
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


def _heading_date(line):
    """(date, suffix) for a well-formed ISO steward heading, else (None, "").

    D + E, both reproduced. D: ANY `## Steward status` heading resets the date state, so
    `## Steward status -- undated` and the non-ISO `## Steward status -- 2026-9-15` no longer leave
    the parser holding the PREVIOUS heading's date -- which let a stale block silently outrank a
    newer one. E: `9999-99-99` matched the digit shape and sorted above every real date; the date
    is now constructed with `datetime.date`, and an impossible one is treated as undated.
    """
    m = STEWARD_DATE_RE.search(line)
    if not m:
        return None, ""
    try:
        datetime.date(*[int(p) for p in m.group(1).split("-")])
    except ValueError:
        return None, ""
    return m.group(1), (m.group(2) or "").lower()


def namings_ranked(text):
    """As `namings`, but keeping every block so the newest can be chosen per filing."""
    out = {}
    current = None
    heading = (None, "")
    seq = 0
    for line in _unfenced_lines(text):
        if STEWARD_HEADING_RE.match(line):
            # D: reset FIRST, unconditionally. Only a well-formed ISO date then sets the state.
            heading = _heading_date(line)
            current = None
            continue
        m = SUBJECT_RE.search(line)
        if m:
            subject = _clean_name(_pick(m, 1, 2))
            if not subject:
                continue
            current = subject
            seq += 1
            key = (1 if heading[0] else 0, heading[0] or "", heading[1], seq)
            out.setdefault(current, []).append([key, []])
            continue
        if current:
            n = NAMING_RE.search(line)
            if n:
                arbiter = _clean_name(_pick(n, 2, 3))
                if arbiter:
                    out[current][-1][1].append((n.group(1).upper(), arbiter))
    best = {}
    for filing, blocks in out.items():
        blocks = [b for b in blocks if b[1]]
        if not blocks:
            continue
        best[filing] = max(blocks, key=lambda b: b[0])[1]
    return best


def _filing_project(text):
    """The `project:` value of a filing, or None if this text is not a filing at all.

    A filing is identified by its HEADER, not by sitting in the directory or being quoted.

    Two D4 defects from the independent key, both false answers in opposite directions:

      * reading only the first 40 lines missed a real filing with front matter above its header,
        which erased a live arbitration duty;
      * reading inside fenced code blocks admitted the README's worked EXAMPLE of a filing header
        as a filing, minting a duty that does not exist.

    So: scan the whole file, skip fenced blocks, and require two header fields rather than one --
    prose that happens to start a line with `project:` is not a filing.

    G: the VALUE is returned, because the round-1 inventory was keyed on the filename stem. Renaming
    `airmypc.md` to a Cyrillic-confusable stem, with `project: airmypc` untouched inside, made the
    live assignment read UNREACHABLE-ARBITER and dropped it out of the owed set entirely.
    """
    seen = set()
    project = None
    for line in _unfenced_lines(text):
        low = line.lower()
        for field in ("project:", "kernel:"):
            if low.startswith(field):
                seen.add(field)
                if field == "project:" and project is None:
                    project = line.split(":", 1)[1]
    if {"project:", "kernel:"} <= seen:
        return project if project is not None else ""
    return None


def _is_filing(text):
    """Kept as the boolean form of `_filing_project`; the two-field rule lives in one place."""
    return _filing_project(text) is not None


def _register(names, raw_project, stem, where):
    """Add one discovered filing to the inventory, keyed on its header (G).

    The STEM is only ever compared, never validated: a filename this tool cannot key on is not a
    reason to refuse when the header inside says exactly which project filed. It becomes a refusal
    only in the fallback branch, where the header gave nothing and the stem is all there is.
    """
    name = _clean_name(raw_project)
    if not name:
        INVENTORY_NOTES.append(
            "%s has no usable `project:` value; keyed on its filename stem `%s` instead"
            % (where, stem))
        name = _clean_name(stem)
        if not name:
            return
    elif name != stem.strip().lower():
        INVENTORY_NOTES.append(
            "%s: filename stem `%s` disagrees with its header `project: %s`; keyed on the HEADER, "
            "because that is the name the ledger addresses" % (where, stem, name))
    names.add(name)


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
    del INVENTORY_NOTES[:]
    names = set()
    for entry in sorted(os.listdir(FILINGS_DIR)):
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
        project = _filing_project(text)
        if project is not None:
            _register(names, project, stem, entry)
    names |= _filings_on_review_branches()
    return names


_BLOB_CACHE = {}


def _git(*args):
    """Run git, or REFUSE.

    D2, from the independent key, and the worst defect it found: this used to return "" on any
    failure, so `git` missing from PATH, an unreadable ref listing or an unreadable blob all
    collapsed into "no filings on review branches" and the tool answered NOTHING OWED. A duty that
    disappears because the instrument broke is exactly the false negative this tool exists to
    prevent. A missing instrument is now a refusal (exit 2), never an absent duty.

    THE CHOICE, documented because the cost is real: refusing on a transient hiccup costs a cycle,
    and a tool that cries wolf gets wired out. So a read-only git call is retried ONCE before the
    refusal stands. A retry cannot manufacture a false green -- a persistently broken instrument
    still refuses -- it only stops a single flaky invocation from stopping a board. What is NOT
    done, deliberately, is degrading to a partial inventory: a partial inventory is precisely the
    false-empty this tool exists to prevent, so it is never traded for availability.
    """
    last = None
    for _attempt in (1, 2):
        try:
            p = subprocess.run(["git", "-C", ROOT, "--no-optional-locks"] + list(args),
                               capture_output=True, text=True, timeout=60,
                               encoding="utf-8", errors="replace")
        except Exception as exc:
            last = ("git could not be run (%s: %s); a missing instrument is not an absent duty"
                    % (type(exc).__name__, exc))
            continue
        if p.returncode == 0:
            return p.stdout
        last = ("git %s failed with status %d (%s); refusing rather than reporting a queue "
                "derived from a partial inventory"
                % (" ".join(args[:2]), p.returncode, (p.stderr or "").strip()[:120]))
    raise Refused(last)


def _read_blob(oid):
    """Read a blob BY OBJECT ID, once per id.

    J: the reviewer measured 30 blob reads for 11 unique object ids -- the same filing, unchanged
    across several review refs, re-read once per ref. Caching is keyed on the object id, which is
    the content, so this is a pure deduplication and not a staleness risk. The cache is cleared at
    the start of every discovery pass so a long-lived process never serves a stale tree.

    A read that FAILS is not cached: `_git` refuses, and the refusal must stay reachable on every
    call rather than being answered from a remembered success.
    """
    if oid not in _BLOB_CACHE:
        _BLOB_CACHE[oid] = _git("cat-file", "blob", oid)
    return _BLOB_CACHE[oid]


def _filings_on_review_branches():
    """Filing names visible on origin/review/* but not yet on master.

    R7.5: "Consumers harvest review branches, not only master." A filing on an unmerged branch is
    still a filing. Every git call here refuses on failure (D2) rather than yielding an empty set.
    """
    _BLOB_CACHE.clear()
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
            blob = _read_blob(parts[2])
            project = _filing_project(blob) if blob else None
            if project is not None:
                _register(found, project, stem, ref + ":" + name)
    return found


def disposition_state(filing):
    """(exists, valid, why).

    D3, from the independent key: an EMPTY or placeholder `<filing>.dispositions.md` cleared the
    duty on the strength of its filename alone. Kernel section 5 says the arbiter "writes that
    filing's `.dispositions.md` with an `arbiter: <project or owner>` line", so that line is what
    makes a disposition a disposition. A file that does not carry it is an unanswered filing with a
    placeholder next to it, and the duty stands.

    B (round 2): the round-1 scan read FENCED blocks, so a dispositions file whose only `arbiter:`
    line sat inside a ``` example cleared the duty. C (round 2): a placeholder VALUE -- `TODO`,
    `TBD`, a bare `arbiter:` with nothing after it, or a backtick-only value -- also cleared it.
    Both are answered here; both are the same failure as D3 wearing a different hat.
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
    saw_placeholder = None
    for line in _unfenced_lines(text):
        low = line.strip().lower().lstrip("*- ")
        if not low.startswith("arbiter:"):
            continue
        value = low.split(":", 1)[1].strip().strip("*` ").strip()
        if value and value not in PLACEHOLDER_VALUES:
            return True, True, ""
        saw_placeholder = value
    if saw_placeholder is not None:
        return True, False, ("the dispositions file's `arbiter:` line carries %s, which names "
                             "nobody; the duty stands"
                             % ("no value" if not saw_placeholder
                                else "the placeholder %r" % saw_placeholder))
    return True, False, ("the dispositions file carries no `arbiter: <project or owner>` line "
                         "outside a fenced example, which section 5 requires; the duty stands")


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
        # The FILING-NOT-FOUND escape, probed by the reviewer and kept deliberately: a disposition
        # still clears a filing the inventory cannot see, so a broken inventory can never WEDGE an
        # arbiter permanently on a duty it has already discharged.
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
        json.dump({"project": args.project or "", "owed": len(owed), "rows": shown,
                   "inventory_notes": list(INVENTORY_NOTES)},
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
        # G: an ambiguity resolved in silence is an ambiguity hidden.
        for note in INVENTORY_NOTES:
            print("  NOTE inventory: " + note)
        if INVENTORY_NOTES:
            print("")
        print("VERDICT: " + ("NOTHING OWED" if not owed
                             else "%d FILING(S) AWAIT YOUR ARBITRATION" % len(owed)))
    return 1 if owed else 0


if __name__ == "__main__":
    sys.exit(main())
