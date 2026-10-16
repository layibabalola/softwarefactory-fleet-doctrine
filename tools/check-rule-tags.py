#!/usr/bin/env python3
"""check-rule-tags: count which written rules are backed by a refusing check and which are prose.

Owner defects "most rules are prose" (2026-10-16, D2): a rule bullet that names no check is a wish, and a
census that cannot tell the two apart reports the vocabulary, not the enforcement. Every rule bullet
in a configured markdown section is classified as exactly one kind:

  enforced   [enforced: <path>]  <path> (relative to the project root) is the check that refuses a
                       breach; it must exist AND be invoked (see below). Several tags may name several checks.
  prose      [prose]   nothing refuses a breach; the rule holds only by being read. The default for an
                       unmapped rule that someone has looked at.
  judgement  [judgement]  a reviewer-checklist rule: only a reviewer can decide it. EXCLUDED from the denominator.
  record     [record]  history or a verbatim ruling kept as written. EXCLUDED from the denominator.

Coverage = enforced / (total - judgement - record). All four counts are printed. If judgement+record
exceeds 50% of the rules a WARNING is printed (reclassifying rules out of the denominator games coverage).

A bullet with no kind is UNTAGGED; one whose enforced path is not a regular file inside the root
(missing, a directory, absolute, or escaping by `..`) is DANGLING; one with two kinds is MIXED. A tag
inside a `code span` is a mention of the syntax, not a tag. The tag is a claim the author makes; this tool
proves the cited path exists and is referenced by an invoker, never that it refuses -- review the
citation the way you review the rule.

SIDECAR RULE MAP (a project never edits governing prose to tag it). Project key `rule_map: "<path>"`
(repo-relative; CLI --rule-map FILE overrides). File schema `rule-map.v1`:
  {"schema":"rule-map.v1","rules":{"<id>":{"kind":"enforced|judgement|record|prose",
     "enforcer":"<repo-relative path, required iff enforced>","source":"<path>","line_hint":N,"text_head":"..."}}}
`<id>` = first 12 hex of sha256(UTF-8 of the rule text with the bullet marker (`- `, `* `, `+ `, `1. `)
stripped, edges trimmed and internal whitespace runs collapsed to one space). A rewrap keeps the id; a
reword changes it. Inline tags in the prose win over the map. A map entry matching no current rule is
STALE: counted and printed, fatal only with --strict-map. A missing map file is exit 2 (never a zero).
`--emit-map [FILE]` (one --project) writes a skeleton with every current rule as kind `prose`.

INVOCATION (existence is not wiring): an enforcer must be referenced -- by its repo path or its
basename -- from at least one file matching the project's `invocation_surfaces` globs (e.g. `.githooks/*`,
`.github/workflows/*.yml`, test projects); the enforcer file itself does not count as its own invoker.
Unreferenced => `enforced-uninvoked`, NOT backed. `invocation_exclude` (globs) drops surface files (frozen
copies); `placement_invoked` (globs) names enforcers the platform invokes by location (git runs
`.githooks/pre-commit` by name). Applies to map entries by default (--require-invoked map); `all` also covers
inline tags (bare --require-invoked), `off` disables. With no `invocation_surfaces` the old behaviour
holds and `INVOCATION UNCHECKED` is printed. Careful: a top-level `**` surface glob walks the whole tree.

RISING FLOOR (a ratchet that requires better, not only forbids worse). Project key
`floor_schedule: [{"date":"YYYY-MM-DD","backed":N},...]`. `--check` exits 1 if the backed count is below the
latest floor whose date <= today (UTC; `--today YYYY-MM-DD` overrides), or on a dangling/mixed rule (or a
stale map entry with --strict-map). The next floor and its date are printed.

Config (JSON, schema fleet/rule-tags/v1; default: rule-tags.config.json beside this script):
  {"projects": [{"name": "...", "root": "C:/path/to/repo", "root_candidates": ["C:/a", "../sibling"],
                 "files": [{"path": "CLAUDE.md", "section": "## Non-negotiables", "bullet": "^- "}],
                 "rule_map": "...", "invocation_surfaces": [...], "floor_schedule": [...]}]}
`root_candidates` (optional): the first existing directory wins over `root`; a relative candidate resolves
against the bus clone (the parent of the config's directory). `section` (optional) is the exact heading line;
the scan runs to the next heading of the same or a higher level. Headings and bullets inside ``` / ~~~
fenced code blocks are ignored (a fence ends any bullet). `bullet` is a regex matched at the start of a line;
the bullet's text runs to the next bullet, heading or blank line. The file is read as DATA (bus Law 1).

Exit: 0 every bullet tagged and every cited path present and invoked (or --report; or --check floor met);
1 an untagged, dangling, mixed or uninvoked bullet (--check: dangling, mixed or below the floor);
2 usage, config or read error (the census did not run).

Run:  python tools/check-rule-tags.py [--config FILE] [--project NAME] [--root DIR] [--report] [--check]
        [--json] [--rule-map FILE] [--strict-map] [--require-invoked [map|all|off]] [--today YYYY-MM-DD]
        [--emit-map [FILE]]
"""
from __future__ import annotations

import argparse
import datetime
import fnmatch
import glob
import hashlib
import json
import os
import re
import sys

SCHEMA = "fleet/rule-tags/v1"
MAP_SCHEMA = "rule-map.v1"
KINDS = ("enforced", "judgement", "record", "prose")
ENFORCED_RX = re.compile(r"\[enforced:\s*([^\]]+?)\s*\]")
PROSE_RX = re.compile(r"\[prose\]")
JUDGEMENT_RX = re.compile(r"\[judgement\]")
RECORD_RX = re.compile(r"\[record\]")
HEADING_RX = re.compile(r"^(#{1,6})\s")
FENCE_RX = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
MARKER_RX = re.compile(r"^\s*(?:[-+*]\s+|\d+[.)]\s+)")
CODE_SPAN_RX = re.compile(r"(`+)(?!`).*?(?<!`)\1(?!`)", re.S)
BAD_STATES = ("untagged", "dangling", "mixed", "uninvoked")
MAX_SURFACE_BYTES = 4_000_000


class ConfigError(Exception):
    pass


# ---------------------------------------------------------------- markdown scanning

def fence_mask(lines: list[str]) -> tuple[set[int], bool]:
    """(0-based indexes of lines that are fence delimiters or inside a fenced code block, fence-left-open).
    A fence closes on a line of the same character, at least as long, with nothing after it."""
    masked, opener = set(), None
    for i, l in enumerate(lines):
        m = FENCE_RX.match(l)
        if opener is None:
            if m and not (m.group(1)[0] == "`" and "`" in m.group(2)):
                opener = m.group(1)
                masked.add(i)
        else:
            masked.add(i)
            if m and m.group(1)[0] == opener[0] and len(m.group(1)) >= len(opener) and not m.group(2).strip():
                opener = None
    return masked, opener is not None


def section_lines(lines: list[str], heading: str | None, masked: set[int] | None = None) -> list[tuple[int, str]]:
    """(1-based line number, text) of the lines under `heading` (all lines when None). Fenced lines come back
    as "" so they end a bullet and can never be a heading or a bullet."""
    if masked is None:
        masked = fence_mask(lines)[0]
    view = [("" if i in masked else l) for i, l in enumerate(lines)]
    if not heading:
        return list(enumerate(view, 1))
    start = next((i for i, l in enumerate(view) if l.rstrip() == heading.rstrip()), None)
    if start is None:
        raise ConfigError(f"section {heading!r} not found")
    level = len(HEADING_RX.match(heading).group(1)) if HEADING_RX.match(heading) else 7
    out = []
    for i in range(start + 1, len(view)):
        m = HEADING_RX.match(view[i])
        if m and len(m.group(1)) <= level:
            break
        out.append((i + 1, view[i]))
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


def normalise(text: str) -> str:
    """The rule text the id is taken over: bullet marker stripped, whitespace runs collapsed, edges trimmed."""
    return " ".join(MARKER_RX.sub("", text, count=1).split())


def rule_id(text: str) -> str:
    return hashlib.sha256(normalise(text).encode("utf-8")).hexdigest()[:12]


# ---------------------------------------------------------------- paths, invocation

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


class Invocation:
    """Answers: is this enforcer referenced from a configured invocation surface?"""

    def __init__(self, root: str, surfaces: list[str], excludes: list[str], placement: list[str]):
        self.root, self.placement = root, placement
        self.files: list[str] = []                      # realpaths of the surface files
        seen = set()
        for pat in surfaces:
            for hit in glob.glob(os.path.join(glob.escape(root), pat), recursive=True):
                if not os.path.isfile(hit):
                    continue
                rel = os.path.relpath(hit, root).replace(os.sep, "/")
                real = os.path.realpath(hit)
                if real in seen or any(fnmatch.fnmatchcase(rel, ex) for ex in excludes):
                    continue
                seen.add(real)
                self.files.append(real)
        self._text: dict[str, str] = {}

    def _read(self, real: str) -> str:
        if real not in self._text:
            try:
                if os.path.getsize(real) > MAX_SURFACE_BYTES:
                    raise OSError("too large")
                with open(real, encoding="utf-8", errors="ignore") as fh:
                    self._text[real] = fh.read().replace("\\", "/")
            except OSError:
                self._text[real] = ""
        return self._text[real]

    def invoked(self, enforcer: str) -> bool:
        rel = enforcer.replace("\\", "/")
        if rel.startswith("./"):
            rel = rel[2:]
        if any(fnmatch.fnmatchcase(rel, g) for g in self.placement):
            return True
        me = os.path.realpath(os.path.join(self.root, enforcer))
        ref_rx = re.compile(r"(?<![\w-])(?:" + re.escape(rel) + "|" + re.escape(os.path.basename(rel)) + r")(?![\w-])")
        for real in self.files:
            if real == me:          # a file never invokes itself
                continue
            text = self._read(real)
            if ref_rx.search(text):
                return True
        return False


# ---------------------------------------------------------------- classification

def check_paths(root: str, paths: list[str], inv: Invocation | None) -> tuple[str, list[str]]:
    missing = [p for p in paths if not cited_check(root, p)]
    if missing:
        return "dangling", missing
    if inv is not None:
        dead = [p for p in paths if not inv.invoked(p)]
        if dead:
            return "uninvoked", dead
    return "backed", paths


def classify(text: str, root: str, entry: dict | None = None, inv: Invocation | None = None,
             inv_inline: bool = False) -> tuple[str, list[str]]:
    """Inline tags win; otherwise the sidecar map entry decides; otherwise UNTAGGED."""
    stripped = CODE_SPAN_RX.sub("", text)      # a tag quoted in a code span is a mention, not a tag
    paths = ENFORCED_RX.findall(stripped)
    present = [k for k, on in (("enforced", bool(paths)), ("prose", bool(PROSE_RX.search(stripped))),
                               ("judgement", bool(JUDGEMENT_RX.search(stripped))),
                               ("record", bool(RECORD_RX.search(stripped)))) if on]
    if len(present) > 1:
        return "mixed", paths
    if present:
        if present[0] == "enforced":
            return check_paths(root, paths, inv if inv_inline else None)
        return present[0], []
    if entry is not None:
        if entry["kind"] == "enforced":
            return check_paths(root, [entry["enforcer"]], inv)
        return entry["kind"], []
    return "untagged", []


def load_rule_map(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as e:
        raise ConfigError(f"rule map {path}: {e}")
    if not isinstance(data, dict) or data.get("schema") != MAP_SCHEMA or not isinstance(data.get("rules"), dict):
        raise ConfigError(f"rule map {path}: schema is not {MAP_SCHEMA} with a rules object")
    for rid, e in data["rules"].items():
        if not isinstance(e, dict) or e.get("kind") not in KINDS:
            raise ConfigError(f"rule map {path}: rule {rid} needs kind in {'|'.join(KINDS)}")
        if e["kind"] == "enforced" and not (isinstance(e.get("enforcer"), str) and e["enforcer"].strip()):
            raise ConfigError(f"rule map {path}: rule {rid} is enforced but names no enforcer")
    return data["rules"]


def resolve_root(project: dict, root_override: str | None, base: str | None) -> str:
    if root_override:
        return root_override
    cands = [project["root"]] if project.get("root") else []
    for c in project.get("root_candidates") or []:
        cands.append(c if os.path.isabs(c) or not base else os.path.join(base, c))
    for c in cands:
        if os.path.isdir(c):
            return c
    raise ConfigError(f"project {project.get('name')!r}: root {cands[0] if cands else None!r} is not a directory")


def scan(project: dict, root: str) -> tuple[list[dict], list[str]]:
    """[{path, section, units:[(line, raw text)]}], warnings. Reads rule files as data."""
    out, warns = [], []
    for f in project.get("files") or []:
        if "path" not in f or "bullet" not in f:
            raise ConfigError(f"project {project.get('name')!r}: a file entry needs path and bullet")
        full = os.path.join(root, f["path"])
        try:
            with open(full, encoding="utf-8") as fh:
                lines = fh.read().replace("\r\n", "\n").split("\n")
        except OSError as e:
            raise ConfigError(f"{full}: {e}")
        masked, open_fence = fence_mask(lines)
        if open_fence:
            warns.append(f"WARNING {project.get('name')}: {f['path']} ends inside an unclosed code fence; "
                         "everything after it is ignored")
        units = bullets(section_lines(lines, f.get("section"), masked), re.compile(f["bullet"]))
        out.append({"path": f["path"], "section": f.get("section"), "units": units})
    return out, warns


def census(project: dict, root_override: str | None = None, base: str | None = None,
           rule_map_override: str | None = None, require_invoked: str = "map") -> dict:
    root = resolve_root(project, root_override, base)
    name = project.get("name")
    scanned, warns = scan(project, root)
    entries: dict = {}
    map_path = rule_map_override or project.get("rule_map")
    if map_path:
        if not rule_map_override and (os.path.isabs(map_path) or ".." in map_path.replace("\\", "/").split("/")):
            raise ConfigError(f"project {name!r}: rule_map must be a path inside the root")
        entries = load_rule_map(map_path if rule_map_override else os.path.join(root, map_path))
    surfaces = project.get("invocation_surfaces") or []
    inv = None
    if surfaces and require_invoked != "off":
        inv = Invocation(root, surfaces, project.get("invocation_exclude") or [], project.get("placement_invoked") or [])
    res = {"project": name, "root": root, "files": [], "counts": {}, "warnings": warns, "stale": [],
           "invocation": "checked" if inv else "unchecked"}
    keys = ("bullets", "backed", "prose", "judgement", "record", "untagged", "dangling", "mixed", "uninvoked")
    totals = dict.fromkeys(keys, 0)
    seen_ids = set()
    for f in scanned:
        rows = []
        for n, text in f["units"]:
            rid = rule_id(text)
            seen_ids.add(rid)
            state, paths = classify(text, root, entries.get(rid), inv, inv_inline=(require_invoked == "all"))
            totals["bullets"] += 1
            totals[state] += 1
            rows.append({"line": n, "id": rid, "state": state, "paths": paths, "text": " ".join(text.split())[:90]})
        res["files"].append({"path": f["path"], "section": f["section"], "bullets": rows})
    for rid, e in entries.items():
        if rid not in seen_ids:
            res["stale"].append({"id": rid, "source": e.get("source"), "line_hint": e.get("line_hint"),
                                 "text_head": e.get("text_head")})
    totals["stale"] = len(res["stale"])
    res["counts"] = totals
    denom = totals["bullets"] - totals["judgement"] - totals["record"]
    res["coverage"] = {"backed": totals["backed"], "denominator": denom,
                       "pct": round(100.0 * totals["backed"] / denom, 1) if denom > 0 else None}
    if totals["bullets"] and 2 * (totals["judgement"] + totals["record"]) > totals["bullets"]:
        warns.append(f"WARNING {name}: judgement+record = {totals['judgement'] + totals['record']} of "
                     f"{totals['bullets']} rules (over 50%); reclassifying rules out of the denominator can game "
                     "coverage -- review the classification")
    return res


def parse_floors(project: dict) -> list[tuple[datetime.date, int]]:
    out = []
    for e in project.get("floor_schedule") or []:
        try:
            out.append((datetime.date.fromisoformat(e["date"]), int(e["backed"])))
        except (KeyError, TypeError, ValueError):
            raise ConfigError(f"project {project.get('name')!r}: bad floor_schedule entry {e!r}")
    return sorted(out)


def floor_status(project: dict, backed: int, today: datetime.date) -> dict | None:
    floors = parse_floors(project)
    if not floors:
        return None
    due = [f for f in floors if f[0] <= today]
    nxt = next((f for f in floors if f[0] > today), None)
    cur = due[-1] if due else None
    return {"required": cur[1] if cur else None, "since": cur[0].isoformat() if cur else None,
            "ok": cur is None or backed >= cur[1],
            "next_date": nxt[0].isoformat() if nxt else None, "next_backed": nxt[1] if nxt else None}


def emit_map(project: dict, root: str) -> dict:
    scanned, _ = scan(project, root)
    rules = {}
    for f in scanned:
        for n, text in f["units"]:
            rid = rule_id(text)
            if rid not in rules:        # identical text in two places shares one id and one entry
                rules[rid] = {"kind": "prose", "source": f["path"], "line_hint": n, "text_head": normalise(text)[:60]}
    return {"schema": MAP_SCHEMA, "rules": rules}


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
    ap.add_argument("--check", action="store_true",
                    help="ratchet gate: exit 1 below the scheduled floor, or on a dangling/mixed rule")
    ap.add_argument("--today", help="YYYY-MM-DD (UTC) override for the floor date, for tests")
    ap.add_argument("--rule-map", help="use this rule-map.v1 file instead of the project's rule_map (one --project)")
    ap.add_argument("--strict-map", action="store_true", help="a STALE map entry is fatal")
    ap.add_argument("--require-invoked", nargs="?", const="all", default="map", choices=("map", "all", "off"),
                    help="enforcer must be referenced from an invocation surface: map entries (default), all, off")
    ap.add_argument("--emit-map", nargs="?", const="-", metavar="FILE",
                    help="write a rule-map.v1 skeleton (every rule kind prose) for one --project to FILE or stdout")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):     # a rule's text must never crash a cp1252 console into exit 1
            stream.reconfigure(errors="backslashreplace")
    try:
        today = datetime.datetime.now(datetime.timezone.utc).date()
        if a.today:
            try:
                today = datetime.date.fromisoformat(a.today)
            except ValueError:
                raise ConfigError(f"--today {a.today!r} is not YYYY-MM-DD")
        cfg = load_config(a.config)
        base = os.path.dirname(os.path.dirname(os.path.abspath(a.config)))
        projects = [p for p in cfg.get("projects") or [] if not a.project or p.get("name") in a.project]
        if not projects:
            raise ConfigError("no matching project in the config")
        if (a.root or a.rule_map or a.emit_map) and len(projects) != 1:
            raise ConfigError("--root, --rule-map and --emit-map need exactly one --project")
        if a.emit_map:
            doc = emit_map(projects[0], resolve_root(projects[0], a.root, base))
            text = json.dumps(doc, indent=1, ensure_ascii=False) + "\n"
            if a.emit_map == "-":
                sys.stdout.write(text)
            else:
                with open(a.emit_map, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(text)
                print(f"check-rule-tags: wrote {len(doc['rules'])} rules to {a.emit_map}")
            return 0
        results = [census(p, a.root, base, a.rule_map, a.require_invoked) for p in projects]
        floors = [floor_status(p, r["counts"]["backed"], today) for p, r in zip(projects, results)]
    except (ConfigError, re.error) as e:
        print(f"check-rule-tags: ERROR {e}", file=sys.stderr)
        return 2
    bad = check_bad = 0
    for r, fl in zip(results, floors):
        c = r["counts"]
        stale_bad = c["stale"] if a.strict_map else 0
        bad += sum(c[k] for k in BAD_STATES) + stale_bad
        check_bad += c["dangling"] + c["mixed"] + stale_bad + (0 if fl is None or fl["ok"] else 1)
        r["floor"] = fl
        if a.json:
            print(json.dumps(r, ensure_ascii=False))
            continue
        for f in r["files"]:
            for b in f["bullets"]:
                if b["state"] in BAD_STATES:
                    label = "ENFORCED-UNINVOKED" if b["state"] == "uninvoked" else b["state"].upper()
                    extra = {"dangling": " missing ", "uninvoked": " not invoked "}.get(b["state"], "")
                    extra = f"{extra}{b['paths']}" if extra else ""
                    print(f"{label} {r['project']} {f['path']}:{b['line']}{extra} {b['text']}")
        for s in r["stale"]:
            print(f"STALE {r['project']} map {s['id']} {s['source']}:{s['line_hint']} {s['text_head']}")
        if r["invocation"] == "unchecked":
            print(f"INVOCATION UNCHECKED {r['project']}: no invocation_surfaces configured (or --require-invoked off); "
                  "enforcer existence is the only proof")
        for w in r["warnings"]:
            print(w)
        print(f"rule-tags {r['project']}: {c['bullets']} rules, {c['backed']} backed, {c['prose']} prose, "
              f"{c['untagged']} untagged, {c['dangling']} dangling, {c['mixed']} mixed")
        cov = r["coverage"]
        pct = "n/a" if cov["pct"] is None else f"{cov['pct']}%"
        print(f"rule-tags {r['project']}: coverage {cov['backed']}/{cov['denominator']} = {pct} "
              f"(enforced {c['backed']}, judgement {c['judgement']}, record {c['record']}, prose {c['prose']}; "
              f"enforced-uninvoked {c['uninvoked']}, stale-map {c['stale']})")
        if fl is not None:
            req = "none due yet" if fl["required"] is None else f"{fl['required']} backed (since {fl['since']})"
            nxt = (f"; next floor {fl['next_backed']} backed on {fl['next_date']}" if fl["next_date"]
                   else "; no later floor")
            print(f"floor {r['project']}: required {req}, have {c['backed']}: {'OK' if fl['ok'] else 'BELOW FLOOR'}{nxt}")
    if a.report:
        return 0
    return 1 if (check_bad if a.check else bad) else 0


if __name__ == "__main__":
    sys.exit(main())
