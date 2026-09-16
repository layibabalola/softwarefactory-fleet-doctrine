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


def duty_clause(text):
    """The §5 bullet that creates the duty, and ONLY that bullet.

    A markdown bullet runs to the next bullet at the same level or to a blank line followed by a
    non-indented line. Reading past it would let a neighbouring sentence satisfy this check.
    """
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if DUTY_ANCHOR in line:
            start = i
            break
    if start is None:
        raise Refused("the section 5 duty clause anchor is gone; the spec was restructured and this "
                      "guard can no longer say where the route belongs")
    out = [lines[start]]
    for line in lines[start + 1:]:
        if not line.strip():
            break
        if line.lstrip().startswith("- ") or line.startswith("#") or line.startswith("**"):
            break
        out.append(line)
    return "\n".join(out)


def k12_observable(text):
    """K12's `*Observable:*` line, and ONLY it."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.startswith(K12_HEADING):
            start = i
            break
    if start is None:
        raise Refused("the K12 heading is gone; the spec was restructured")
    for line in lines[start + 1:]:
        if line.startswith("### ") or line.startswith("## "):
            break
        if line.startswith(OBSERVABLE):
            return line
    raise Refused("K12 has no *Observable:* line; the spec was restructured")


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
