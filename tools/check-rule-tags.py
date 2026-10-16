#!/usr/bin/env python3
"""check-rule-tags: count which written rules are backed by a refusing check and which are prose.

Owner defect "most rules are prose" (2026-10-16): a rule bullet that names no check is a wish, and a
census that cannot tell the two apart reports the vocabulary, not the enforcement. Every rule bullet
in a configured markdown section must carry exactly one kind of tag:

  [enforced: <path>]   <path> (relative to the project root) is the check that refuses a breach;
                       it must exist. Several enforced tags may name several checks.
  [prose]              nothing refuses a breach; the rule holds only by being read.

A bullet with neither tag is UNTAGGED; one whose enforced path is not a regular file inside the root
(missing, a directory, absolute, or escaping by `..`) is DANGLING; one with both kinds is MIXED. A tag
inside a `code span` is a mention of the syntax, not a tag. The tag is a claim the author makes; this tool proves only that the cited path
exists, never that it refuses -- review the citation the way you review the rule.

Config (JSON, schema fleet/rule-tags/v1; default: rule-tags.config.json beside this script):
  {"projects": [{"name": "...", "root": "C:/path/to/repo",
                 "files": [{"path": "CLAUDE.md", "section": "## Non-negotiables", "bullet": "^- "}]}]}
`section` (optional) is the exact heading line; the scan runs to the next heading of the same or a
higher level. `bullet` is a regex matched at the start of a line; the bullet's text runs to the next
bullet, heading or blank line. The file is read as DATA (bus Law 1): nothing in it is executed.

Exit: 0 every bullet tagged and every cited path present (or --report); 1 an untagged, dangling or
mixed bullet; 2 usage, config or read error (the census did not run).

Run:  python tools/check-rule-tags.py [--config FILE] [--project NAME] [--root DIR] [--report] [--json]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

SCHEMA = "fleet/rule-tags/v1"
ENFORCED_RX = re.compile(r"\[enforced:\s*([^\]]+?)\s*\]")
PROSE_RX = re.compile(r"\[prose\]")
HEADING_RX = re.compile(r"^(#{1,6})\s")


class ConfigError(Exception):
    pass


def section_lines(lines: list[str], heading: str | None) -> list[tuple[int, str]]:
    """(1-based line number, text) of the lines under `heading` (all lines when None)."""
    if not heading:
        return list(enumerate(lines, 1))
    start = next((i for i, l in enumerate(lines) if l.rstrip() == heading.rstrip()), None)
    if start is None:
        raise ConfigError(f"section {heading!r} not found")
    level = len(HEADING_RX.match(heading).group(1)) if HEADING_RX.match(heading) else 7
    out = []
    for i in range(start + 1, len(lines)):
        m = HEADING_RX.match(lines[i])
        if m and len(m.group(1)) <= level:
            break
        out.append((i + 1, lines[i]))
    return out


def bullets(numbered: list[tuple[int, str]], bullet_rx: re.Pattern) -> list[tuple[int, str]]:
    out, cur = [], None
    for n, l in numbered:
        if bullet_rx.match(l):
            if cur:
                out.append(cur)
            cur = (n, l)
        elif cur and l.strip() and not HEADING_RX.match(l):
            cur = (cur[0], cur[1] + "\n" + l)
        else:
            if cur:
                out.append(cur)
            cur = None
    if cur:
        out.append(cur)
    return out


CODE_SPAN_RX = re.compile(r"(`+)(?!`).*?(?<!`)\1(?!`)", re.S)


def cited_check(root: str, path: str) -> bool:
    """True only for a regular file inside root: an absolute path, a `..` escape or a directory
    names no check of this project, so it can never back a rule."""
    if os.path.isabs(path) or os.path.splitdrive(path)[0]:
        return False
    base = os.path.realpath(root)
    full = os.path.realpath(os.path.join(base, path))
    try:
        inside = os.path.commonpath([base, full]) == base
    except ValueError:          # another drive
        return False
    return inside and full != base and os.path.isfile(full)


def classify(text: str, root: str) -> tuple[str, list[str]]:
    text = CODE_SPAN_RX.sub("", text)      # a tag quoted in a code span is a mention, not a tag
    paths = ENFORCED_RX.findall(text)
    prose = bool(PROSE_RX.search(text))
    if paths and prose:
        return "mixed", paths
    if prose:
        return "prose", []
    if not paths:
        return "untagged", []
    missing = [p for p in paths if not cited_check(root, p)]
    return ("dangling", missing) if missing else ("backed", paths)


def census(project: dict, root_override: str | None = None) -> dict:
    root = root_override or project.get("root")
    if not root or not os.path.isdir(root):
        raise ConfigError(f"project {project.get('name')!r}: root {root!r} is not a directory")
    res = {"project": project.get("name"), "root": root, "files": [], "counts": {}}
    totals = {"bullets": 0, "backed": 0, "prose": 0, "untagged": 0, "dangling": 0, "mixed": 0}
    for f in project.get("files") or []:
        if "path" not in f or "bullet" not in f:
            raise ConfigError(f"project {project.get('name')!r}: a file entry needs path and bullet")
        full = os.path.join(root, f["path"])
        try:
            with open(full, encoding="utf-8") as fh:
                lines = fh.read().replace("\r\n", "\n").split("\n")
        except OSError as e:
            raise ConfigError(f"{full}: {e}")
        rows = []
        for n, text in bullets(section_lines(lines, f.get("section")), re.compile(f["bullet"])):
            state, paths = classify(text, root)
            totals["bullets"] += 1
            totals[state] += 1
            rows.append({"line": n, "state": state, "paths": paths, "text": " ".join(text.split())[:90]})
        res["files"].append({"path": f["path"], "section": f.get("section"), "bullets": rows})
    res["counts"] = totals
    return res


def load_config(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as fh:
            cfg = json.load(fh)
    except (OSError, ValueError) as e:
        raise ConfigError(f"config {path}: {e}")
    if cfg.get("schema") != SCHEMA:
        raise ConfigError(f"config {path}: schema is not {SCHEMA}")
    return cfg


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "rule-tags.config.json"))
    ap.add_argument("--project", action="append", help="project name from the config (repeatable; default all)")
    ap.add_argument("--root", help="override the project's root (only with one --project)")
    ap.add_argument("--report", action="store_true", help="measure only: always exit 0 when the census ran")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):     # a rule's text must never crash a cp1252 console into exit 1
            stream.reconfigure(errors="backslashreplace")
    try:
        cfg = load_config(a.config)
        projects = [p for p in cfg.get("projects") or [] if not a.project or p.get("name") in a.project]
        if not projects:
            raise ConfigError("no matching project in the config")
        if a.root and len(projects) != 1:
            raise ConfigError("--root needs exactly one --project")
        results = [census(p, a.root) for p in projects]
    except (ConfigError, re.error) as e:
        print(f"check-rule-tags: ERROR {e}", file=sys.stderr)
        return 2
    bad = 0
    for r in results:
        c = r["counts"]
        bad += c["untagged"] + c["dangling"] + c["mixed"]
        if a.json:
            print(json.dumps(r, ensure_ascii=False))
            continue
        for f in r["files"]:
            for b in f["bullets"]:
                if b["state"] in ("untagged", "dangling", "mixed"):
                    extra = f" missing {b['paths']}" if b["state"] == "dangling" else ""
                    print(f"{b['state'].upper()} {r['project']} {f['path']}:{b['line']}{extra} {b['text']}")
        print(f"rule-tags {r['project']}: {c['bullets']} rules, {c['backed']} backed, {c['prose']} prose, "
              f"{c['untagged']} untagged, {c['dangling']} dangling, {c['mixed']} mixed")
    if a.report:
        return 0
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
