#!/usr/bin/env python
"""Guard: the kernel's arbitration duty must name the command that discharges it.

`specs/fleet-factory-kernel.md` §5 says the steward's own filings are ruled on by a second
project's arbiter. That clause creates a duty and, until S9, named no way for the arbiter to
LEARN of it -- `tools/arbitration-queue.py` existed and nothing anywhere pointed at it. A named
arbiter that is never told is indistinguishable from an unnamed one.

This is a GUARD, not a report. It exits non-zero while the route is missing, and it REFUSES
(exit 2) when it cannot measure -- a missing instrument must never read as a satisfied clause.

  exit 0  the route is named in both governed places and the tool it names exists
  exit 1  a governed place does not name it  (the defect this guard exists to catch)
  exit 2  REFUSED: the spec is absent, unreadable, empty, or its anchors are gone

Non-vacuity matters more here than anywhere: a mention of the tool ELSEWHERE in the spec must not
green this guard, because prose in the wrong place is exactly the failure being fixed. Each check
is anchored to the region it governs and reads nothing outside it.
"""
from __future__ import annotations

import io
import os
import sys

TOOL = "tools/arbitration-queue.py"
DUTY_ANCHOR = "The steward's own project's filings are never adjudicated by the steward alone"
K12_HEADING = "### K12"
OBSERVABLE = "*Observable:*"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = os.path.join(ROOT, "specs", "fleet-factory-kernel.md")


class Refused(Exception):
    pass


def read_spec(path=None):
    path = path or SPEC
    if not os.path.isfile(path):
        raise Refused("spec not found at " + path)
    try:
        text = io.open(path, encoding="utf-8").read()
    except Exception as exc:
        raise Refused("could not read the spec: " + str(exc))
    if not text.strip():
        raise Refused("spec is empty; an empty spec is not a satisfied clause")
    return text


BULLETS = ("- ", "* ", "+ ")


def governed_lines(text):
    """The spec's GOVERNING prose: fenced blocks and HTML comments blanked, line numbers kept.

    Round 1 of the independent key greened this guard three ways without changing a single governing
    clause: a prepended fenced EXAMPLE supplied duplicate anchors and the tool name; HTML comments
    carrying the tool name satisfied both assertions; and a neighbouring `* ` bullet supplied the
    name because the walker only terminated on `- `. None of those tell an arbiter anything, which
    is the whole point of the subject -- a guard that a decoy can satisfy is an announcement too.

    Lines are blanked rather than removed so that every anchor keeps its real position.
    """
    out = []
    fence = None            # the marker that OPENED the current fence, or None
    in_comment = False
    for line in text.splitlines():
        stripped = line.strip()
        if not in_comment:
            marker = "```" if stripped.startswith("```") else (
                "~~~" if stripped.startswith("~~~") else None)
            if marker and fence is None:
                fence = marker
                out.append("")
                continue
            if fence is not None:
                # Round 2 of the key: a ``` inside a ~~~ block toggled the state off, so the rest of
                # the spec read as governing prose while it was in fact all inside one fence. Only
                # the marker that opened a fence can close it.
                if marker == fence:
                    fence = None
                out.append("")
                continue
        if fence is not None:
            out.append("")
            continue
        # Round 2 of the key: text after a CLOSED inline comment was discarded, and a second comment
        # on a later line was never seen. Strip every comment on the line, keeping what is outside.
        rest = line
        kept = []
        while True:
            if in_comment:
                if "-->" in rest:
                    rest = rest.split("-->", 1)[1]
                    in_comment = False
                    continue
                rest = ""
                break
            if "<!--" in rest:
                before, after = rest.split("<!--", 1)
                kept.append(before)
                rest = after
                in_comment = True
                continue
            kept.append(rest)
            rest = ""
            break
        out.append("".join(kept))
    return out


def _section_bounds(lines, number):
    """[start, end) of the top-level `## <number>.` section, or REFUSE.

    Round 2 of the key: the duty anchor was found ANYWHERE -- an appendix, a table cell, a different
    section -- so the guard never established that section 5 itself carries the route. Locating the
    section first is the difference between "the clause that creates the duty names the command" and
    "the string appears in the file somewhere", which is the whole distinction this subject is about.
    """
    prefix = "## " + str(number) + "."
    starts = [i for i, line in enumerate(lines) if line.startswith(prefix)]
    if not starts:
        raise Refused("section %s is gone from the governing prose; the spec was restructured"
                      % number)
    if len(starts) > 1:
        raise Refused("section %s appears %d times in the governing prose; refusing rather than "
                      "picking one" % (number, len(starts)))
    start = starts[0]
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("## "):
            return start, i
    return start, len(lines)


def _block_from(lines, start, end=None):
    """One markdown block: its first line, its wrapped continuation lines, and its NESTED bullets.

    Ordinary Markdown wrapping put the K12 command on an indented continuation line, and round 1
    correctly called the resulting FAILURE a false one. Round 2 found the mirror case: a nested
    sub-bullet under the duty bullet carrying the command was rejected too. Both belong to the
    block. A bullet at the SAME indentation, a heading, or a new bold run starts a different block
    and must not be read into it.
    """
    end = len(lines) if end is None else end
    base = len(lines[start]) - len(lines[start].lstrip())
    out = [lines[start]]
    for line in lines[start + 1:end]:
        if not line.strip():
            break
        lead = line.lstrip()
        indent = len(line) - len(lead)
        if line.startswith("#") or line.startswith("**"):
            break
        if lead.startswith(BULLETS) and indent <= base:
            break
        if indent == 0 and (lead.startswith(OBSERVABLE) or lead.startswith("*Doctrine:*")):
            break
        out.append(line)
    return "\n".join(out)


def duty_clause(text):
    """The section 5 bullet that creates the duty, inside section 5, and ONLY that bullet."""
    lines = governed_lines(text)
    lo, hi = _section_bounds(lines, 5)
    hits = [i for i in range(lo, hi) if DUTY_ANCHOR in lines[i]]
    if not hits:
        raise Refused("the duty clause anchor is gone from section 5 of the governing prose; the "
                      "spec was restructured and this guard can no longer say where the route "
                      "belongs")
    if len(hits) > 1:
        raise Refused("the duty clause anchor appears %d times inside section 5; refusing rather "
                      "than picking one" % len(hits))
    return _block_from(lines, hits[0], hi)


def k12_observable(text):
    """K12's `*Observable:*` block, and ONLY it.

    Returns "" when K12 exists but carries no Observable line at all. Round 2 of the key was right
    that this must be a named FAILURE, not a refusal: the section is locatable, so the guard CAN
    measure, and the honest answer is that the governed place does not name the command.
    """
    lines = governed_lines(text)
    heads = [i for i, line in enumerate(lines)
             if line.rstrip() == K12_HEADING or line.startswith(K12_HEADING + " ")]
    if not heads:
        raise Refused("the K12 heading is gone from the governing prose; the spec was restructured")
    if len(heads) > 1:
        raise Refused("the K12 heading appears %d times in the governing prose; refusing rather "
                      "than picking one" % len(heads))
    for i in range(heads[0] + 1, len(lines)):
        if lines[i].startswith("### ") or lines[i].startswith("## "):
            break
        if lines[i].startswith(OBSERVABLE):
            return _block_from(lines, i)
    return ""


def checks(text, root=None):
    root = root or ROOT
    return [
        ("the section 5 duty clause names " + TOOL,
         TOOL in duty_clause(text)),
        ("K12's Observable names " + TOOL,
         TOOL in k12_observable(text)),
        ("the named tool exists at " + TOOL,
         os.path.isfile(os.path.join(root, TOOL.replace("/", os.sep)))),
    ]


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    path = argv[0] if argv else None
    root = os.path.dirname(os.path.dirname(os.path.abspath(path))) if path else None
    try:
        text = read_spec(path)
        results = checks(text, root)
    except Refused as exc:
        print("REFUSE kernel-arbitration-route: " + str(exc))
        return 2

    failed = 0
    for label, ok in results:
        print(("  ok   " if ok else "  FAIL ") + label)
        if not ok:
            failed += 1
    if failed:
        print("\nFAIL kernel-arbitration-route: %d check(s) failed -- the arbitration duty exists "
              "in prose with no command that discharges it" % failed)
        return 1
    print("\nPASS kernel-arbitration-route")
    return 0


if __name__ == "__main__":
    sys.exit(main())
