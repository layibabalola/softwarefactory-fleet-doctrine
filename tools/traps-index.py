#!/usr/bin/env python3
"""Generate TRAPS-INDEX.md, a derived pointer into TRAPS.md. Never edits TRAPS.md.

WHY. TRAPS.md grew from 2,861 lines (2026-09-01) to over 11,000 in seventeen days, with no
index and no ID scheme. A consumer folding since its own marker reads a small diff (median 44
added lines per commit), so size is NOT what blocks the routine fold -- but a COLD reader, and
anyone asking "has this defect class been recorded before", faces the whole file. The fleet
pays for that: the same class has been rediscovered by different boards weeks apart.

WHAT IT IS, EXACTLY -- an index that silently covers a fraction is worse than no index, so the
predicate is stated and the coverage is counted:

  * The unit is a RUN of consecutive `## ` lines with no blank line between them. Long headings
    in this file are hard-wrapped, each continuation line re-prefixed with `##`, so a naive
    per-line heading parser overcounts. Runs are joined back into one logical heading.
  * `## Appended by <project>, <date>` is an era-1 SECTION header whose findings are the bullets
    beneath it. Everything else at `##` is an era-2 ENTRY whose heading IS the finding.
  * `###` is not indexed: it appears inside entry bodies, not as a finding boundary.
  * A trailing `(project, date, machine)` parenthetical is parsed when present. It is a
    CONVENTION, not a schema, so entries without one are still indexed and counted separately.
  * A `CORRECTION to "..."` entry is marked, so a reader sees that a finding was superseded.

WHAT IT IS NOT. It cannot see semantic duplication -- the recurrence in this corpus is
conceptual, not lexical, and entries are deliberately phrased as distinct claims. This index
does not claim to detect it and must not be cited as evidence that none exists.

Generated, never hand-maintained: an enumeration that is edited by hand rots. `--check` is the
guard that keeps it honest.
"""
from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRAPS = ROOT / "TRAPS.md"
INDEX = ROOT / "TRAPS-INDEX.md"

SECTION_RE = re.compile(r"^Appended by\s+(?P<project>.+?),\s*(?P<date>\d{4}-\d{2}-\d{2})", re.I)
# Trailing "(project, date[, machine])" -- a convention, matched leniently and never required.
SUFFIX_RE = re.compile(r"\((?P<body>[^()]*\d{4}-\d{2}-\d{2}[^()]*)\)\s*$")
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
CORRECTION_RE = re.compile(r"^CORRECTION\b", re.I)


def heading_runs(lines: list[str]) -> list[tuple[int, str]]:
    """Join runs of consecutive `## ` lines into one heading, keyed by the run's first line."""
    runs: list[tuple[int, str]] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("## ") and not line.startswith("### "):
            start = i + 1  # 1-indexed, for a file:line reference
            parts = []
            while i < len(lines) and lines[i].startswith("## ") and not lines[i].startswith("### "):
                parts.append(lines[i][3:].strip())
                i += 1
            runs.append((start, " ".join(parts).strip()))
            continue
        i += 1
    return runs


def classify(heading: str) -> dict:
    section = SECTION_RE.match(heading)
    if section:
        return {"kind": "section", "project": section.group("project").strip(),
                "date": section.group("date"), "title": heading}
    project = date = ""
    suffix = SUFFIX_RE.search(heading)
    if suffix:
        body = suffix.group("body")
        found = DATE_RE.search(body)
        date = found.group(0) if found else ""
        bits = [b.strip() for b in body.split(",")]
        lead = [b for b in bits if not DATE_RE.search(b)]
        project = lead[0] if lead else ""
    return {"kind": "entry", "project": project, "date": date,
            "title": heading, "correction": bool(CORRECTION_RE.match(heading))}


def build() -> str:
    lines = io.open(TRAPS, encoding="utf-8").read().split("\n")
    runs = heading_runs(lines)
    rows = [(n, classify(h)) for n, h in runs]
    entries = [(n, r) for n, r in rows if r["kind"] == "entry"]
    sections = [(n, r) for n, r in rows if r["kind"] == "section"]
    attributed = [r for _, r in entries if r["date"]]
    corrections = [r for _, r in entries if r.get("correction")]

    out: list[str] = []
    out.append("# TRAPS index (GENERATED -- do not edit)")
    out.append("")
    out.append("Derived from `TRAPS.md` by `tools/traps-index.py`. `TRAPS.md` is unchanged and remains")
    out.append("append-only and authoritative; this file is a pointer, never a summary, and carries no")
    out.append("authority of its own. Regenerate with `python tools/traps-index.py --write`.")
    out.append("")
    out.append("## Coverage")
    out.append("")
    out.append(f"- `TRAPS.md` lines: **{len(lines)}**")
    out.append(f"- level-2 heading runs: **{len(runs)}** "
               f"(era-2 entries **{len(entries)}**, era-1 `Appended by` sections **{len(sections)}**)")
    out.append(f"- entries carrying a parsed `(… date …)` attribution: **{len(attributed)}** "
               f"of {len(entries)}; the rest are indexed without one")
    out.append(f"- entries marked `CORRECTION`: **{len(corrections)}**")
    out.append("")
    out.append("A heading run is one or more consecutive `## ` lines with no blank line between them:")
    out.append("long headings in this file are hard-wrapped and each continuation re-prefixed with")
    out.append("`##`, so counting `##` lines overcounts findings. `###` is not indexed. This index")
    out.append("**cannot** detect semantic duplication and is not evidence that none exists.")
    out.append("")
    out.append("## Entries")
    out.append("")
    out.append("| line | date | project | finding |")
    out.append("|---|---|---|---|")
    for n, r in rows:
        title = r["title"].replace("|", r"\|")
        if r["kind"] == "section":
            out.append(f"| {n} | {r['date']} | {r['project']} | _(section)_ {title} |")
        else:
            mark = "**CORRECTION** " if r.get("correction") else ""
            out.append(f"| {n} | {r['date'] or '-'} | {r['project'] or '-'} | {mark}{title} |")
    out.append("")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="regenerate TRAPS-INDEX.md")
    ap.add_argument("--check", action="store_true", help="exit 1 if TRAPS-INDEX.md is stale")
    a = ap.parse_args()
    if not TRAPS.is_file():
        print("traps-index: TRAPS.md not found", file=sys.stderr)
        return 2
    built = build()
    if a.write:
        io.open(INDEX, "w", encoding="utf-8", newline="\n").write(built)
        print(f"traps-index: wrote {INDEX.name}")
        return 0
    if a.check:
        if not INDEX.is_file():
            print("traps-index: TRAPS-INDEX.md missing - run --write", file=sys.stderr)
            return 1
        current = io.open(INDEX, encoding="utf-8").read()
        if current != built:
            print("traps-index: TRAPS-INDEX.md is STALE - run `python tools/traps-index.py --write`",
                  file=sys.stderr)
            return 1
        print("traps-index: index is current")
        return 0
    sys.stdout.write(built)
    return 0


if __name__ == "__main__":
    sys.exit(main())
