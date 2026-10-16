#!/usr/bin/env python3
"""check-rule-tags: count which written rules are backed by a refusing check and which are prose.

Owner defect "most rules are prose" (2026-10-16, D2): a rule bullet that names no check is a wish, and a
census that cannot tell the two apart reports the vocabulary, not the enforcement. Every rule bullet
in a configured markdown section is classified as exactly one kind:

  enforced   [enforced: <path>] or [enforced: <path>#<anchor>]  <path> (relative to the project root) is
                       the check that refuses a breach; it must exist AND be invoked (see below).
  prose      [prose]   nothing refuses a breach; the rule holds only by being read.
  judgement  [judgement]  a reviewer-checklist rule: only a reviewer can decide it. EXCLUDED from the denominator.
  record     [record]  history or a verbatim ruling kept as written. EXCLUDED from the denominator.

Coverage = enforced / (distinct rules - judgement - record). All four counts are printed. If judgement+record
exceeds 50% of the rules a WARNING is printed (reclassifying rules out of the denominator games coverage).
Rules are counted by DISTINCT id: a second bullet with identical text is a DUPLICATE (reported, never counted
again), so N copies of one backed rule cannot satisfy a floor of N.

A bullet with no kind is UNTAGGED; one whose enforced path is not a regular file inside the root
(missing, a directory, absolute, or escaping by `..`) is DANGLING; one with two kinds is MIXED. A tag
inside a `code span` is a mention of the syntax, not a tag. The tag is a claim the author makes; this tool
proves the cited path exists, is invoked and carries the anchor, never that it refuses -- review the
citation the way you review the rule.

SIDECAR RULE MAP (a project never edits governing prose to tag it). Project key `rule_map: "<path>"`
(repo-relative; CLI --rule-map FILE overrides). File schema `rule-map.v1`:
  {"schema":"rule-map.v1","rules":{"<id>":{"kind":"enforced|judgement|record|prose",
     "enforcer":"<repo-relative path>","anchor":"<string>","source":"<path>","line_hint":N,"text_head":"..."}}}
`enforcer` and `anchor` are required iff kind is enforced (anchor only where invocation is checked).
`<id>` = first 12 hex of sha256(UTF-8 of the rule text with the bullet marker (`- `, `* `, `+ `, `1. `)
stripped, edges trimmed and internal whitespace runs collapsed to one space). A rewrap keeps the id; a
reword changes it. Inline tags in the prose win over the map. A map entry matching no current rule is
STALE: counted and printed, fatal only with --strict-map. A missing map file is exit 2 (never a zero).
`--emit-map [FILE]` (one --project) writes a skeleton with every current rule as kind `prose`.

INVOKED means wired, not mentioned. An enforcer is invoked only if a file matching the project's
`invocation_surfaces` globs has a NON-COMMENT line (# // REM :: and YAML comments, trailing comments
and block comments removed) holding a token that RESOLVES to the same file, repo-relative or relative to the
surface's own directory (case-insensitive on Windows). A namesake in another directory, `gate.py.disabled`
and a comment do not count; neither does the enforcer itself, nor a test file of the enforcer (stem match:
foo.tests.py, FooTests.cs, test_foo.py for foo.*). A test file is a surface only if you list it, so list only
tests a hook or CI job runs. `invocation_exclude` (globs) drops surface files (frozen copies).
`placement_invoked` (globs) names git-hook enforcers; they count only if the enforcer's directory is the
repo's effective hooks directory (`git config core.hooksPath`, else `.git/hooks`; git unavailable = unwired).
A top-level `**` surface glob walks the whole tree, so anchor your globs.
--require-invoked: `all` (inline and map tags; the default whenever the project configures
invocation_surfaces), `map` (map entries only), `off`. With no invocation_surfaces and no explicit mode the
old behaviour holds and `INVOCATION UNCHECKED` is printed; an EXPLICIT `all`/`map` with no (or empty)
surfaces fails CLOSED: every enforced rule is `enforced-uninvoked` and --check exits 1.

ANCHORS AND FAN-IN. Where invocation is checked, each map `enforced` entry carries an `anchor` that occurs
literally on a non-comment line of the enforcer; anchors must be distinct within one enforcer (a later rule
reusing an anchor is ANCHOR-DUPLICATE and not backed). An inline tag may write `[enforced: path#anchor]`;
without an anchor an inline tag is capped at ONE backed rule per enforcer. A per-enforcer fan-in table
is printed so one hook cannot silently back many rules.

RISING FLOOR (a ratchet that requires better, not only forbids worse). Project key
`floor_schedule: [{"date":"YYYY-MM-DD","backed":N},...]` (integers >= 0, dates strictly increasing, floors
non-decreasing, else exit 2). `--check` exits 1 if the backed count is below the latest floor whose date <=
today (UTC; `--today YYYY-MM-DD` overrides), or on a dangling/mixed rule, or on the fail-closed
misconfiguration above (or a stale map entry with --strict-map). The next floor and its date are printed.

Config (JSON, schema fleet/rule-tags/v1; default: rule-tags.config.json beside this script):
  {"projects": [{"name": "...", "root": "C:/path/to/repo", "root_candidates": ["C:/a", "../sibling"],
                 "files": [{"path": "CLAUDE.md", "section": "## Non-negotiables", "bullet": "^- "}],
                 "rule_map": "...", "invocation_surfaces": [...], "floor_schedule": [...]}]}
`root_candidates` (optional): tried in order, then `root`; the first existing directory wins. A relative
candidate resolves against the bus clone (the parent of the config's directory). `section` (optional) is the
exact heading line; the scan runs to the next heading of the same or a higher level. Headings and bullets
inside ``` / ~~~ fenced code blocks (opener indented 0-3 spaces, CommonMark) are ignored and a fence ends
any bullet. `bullet` is a regex matched at the start of a line; the bullet's text runs to the next bullet,
heading or blank line. Files are read as UTF-8 (a BOM is ignored) as DATA (bus Law 1).

Exit: 0 every bullet tagged and every cited path present and invoked (or --report; or --check floor met);
1 an untagged, dangling, mixed, uninvoked or anchor-duplicate bullet (--check: dangling, mixed, below the
floor, or fail-closed); 2 usage, config or read/write error (the census did not run).

Run:  python tools/check-rule-tags.py [--config FILE] [--project NAME] [--root DIR] [--report] [--check]
        [--json] [--rule-map FILE] [--strict-map] [--require-invoked [all|map|off]] [--today YYYY-MM-DD]
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
import subprocess
import sys

SCHEMA = "fleet/rule-tags/v1"
MAP_SCHEMA = "rule-map.v1"
KINDS = ("enforced", "judgement", "record", "prose")
ENFORCED_RX = re.compile(r"\[enforced:\s*([^\]]+?)\s*\]")
PROSE_RX = re.compile(r"\[prose\]")
JUDGEMENT_RX = re.compile(r"\[judgement\]")
RECORD_RX = re.compile(r"\[record\]")
HEADING_RX = re.compile(r"^(#{1,6})\s")
FENCE_RX = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")          # CommonMark: 0-3 spaces of indent
MARKER_RX = re.compile(r"^\s*(?:[-+*]\s+|\d+[.)]\s+)")
CODE_SPAN_RX = re.compile(r"(`+)(?!`).*?(?<!`)\1(?!`)", re.S)
DATE_RX = re.compile(r"^\d{4}-\d{2}-\d{2}$")
BAD_STATES = ("untagged", "dangling", "mixed", "uninvoked", "dup_anchor")
STATE_LABEL = {"uninvoked": "ENFORCED-UNINVOKED", "dup_anchor": "ANCHOR-DUPLICATE"}
MAX_SURFACE_BYTES = 4_000_000

FULL_COMMENT_RX = re.compile(r"^\s*(?:#|//|::|rem(?:\s|$))", re.I)
TRAILING_COMMENT_RX = re.compile(r"\s(?:#|//).*$")
BLOCK_COMMENTS = (("/*", "*/"), ("<#", "#>"), ("<!--", "-->"))
TOKEN_RX = re.compile(r"[^\s\"'`(){}<>|;&=,\[\]]+")
VAR_PREFIX_RX = re.compile(r"^(?:\$\{?[A-Za-z_]\w*\}?|%\w+%)[/\\]")
TEST_SUFFIX_RX = re.compile(r"(?:[._-][Tt]ests?|Tests?|[._-]TESTS?)$")
TEST_PREFIX_RX = re.compile(r"^(?:[Tt]est[._-])")


class ConfigError(Exception):
    pass


def read_text(path: str) -> str:
    """UTF-8, a BOM is dropped (a BOM before a line-1 heading must not hide the section)."""
    with open(path, encoding="utf-8-sig") as fh:
        return fh.read()


# ---------------------------------------------------------------- markdown scanning

def fence_mask(lines: list[str]) -> tuple[set[int], bool]:
    """(0-based indexes of lines that are fence delimiters or inside a fenced code block, fence-left-open).
    An opener is indented 0-3 spaces; a fence closes on a line of the same character, at least as long,
    with nothing after it. A backtick opener may not carry a backtick in its info string."""
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


# ---------------------------------------------------------------- paths, comments, invocation

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


def norm(path: str) -> str:
    """Identity of a file for comparison: resolved, and case-folded where the filesystem is."""
    return os.path.normcase(os.path.realpath(path))


def code_lines(text: str) -> list[str]:
    """The non-comment part of each line: whole-line comments (# // REM ::), block comments that start a
    line (/* */, <# #>, <!-- -->) and trailing ` # ...` / ` // ...` comments removed."""
    out, block_end = [], None
    for line in text.replace("\r\n", "\n").split("\n"):
        if block_end:
            k = line.find(block_end)
            if k < 0:
                continue
            line, block_end = line[k + len(block_end):], None
        while True:                             # block comments that begin a line; code after a closed one is kept
            stripped = line.lstrip()
            opened = next(((o, c) for o, c in BLOCK_COMMENTS if stripped.startswith(o)), None)
            if not opened:
                break
            k = stripped.find(opened[1], len(opened[0]))
            if k < 0:
                block_end, line = opened[1], ""
                break
            line = stripped[k + len(opened[1]):]
        if FULL_COMMENT_RX.match(line):
            continue
        line = TRAILING_COMMENT_RX.sub("", line)
        if line.strip():
            out.append(line)
    return out


def test_stem(name: str) -> str:
    """The stem a test file tests: foo.tests.py, FooTests.cs, test_foo.py -> foo (case-folded)."""
    stem = os.path.splitext(name)[0]
    stem = TEST_PREFIX_RX.sub("", stem, count=1)
    return TEST_SUFFIX_RX.sub("", stem, count=1).lower()


def run_git(root: str, *args: str) -> tuple[int, str]:
    env = {k: v for k, v in os.environ.items()
           if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_PREFIX", "GIT_COMMON_DIR")}
    try:
        p = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True, timeout=20, env=env)
    except (OSError, subprocess.SubprocessError):
        return 127, ""
    return p.returncode, p.stdout.strip()


def effective_hooks_dir(root: str) -> str | None:
    """The directory git runs hooks from for the repo at `root`: core.hooksPath, else .git/hooks.
    None when git cannot say (fail closed)."""
    rc, top = run_git(root, "rev-parse", "--show-toplevel")
    if rc != 0 or not top:
        return None
    rc, hp = run_git(root, "config", "--get", "core.hooksPath")
    if rc == 0 and hp:
        hp = os.path.expanduser(hp)
        return hp if os.path.isabs(hp) else os.path.join(top, hp)
    if rc not in (0, 1):
        return None
    rc, gp = run_git(root, "rev-parse", "--git-path", "hooks")
    if rc != 0 or not gp:
        return None
    return gp if os.path.isabs(gp) else os.path.join(root, gp)


class Invocation:
    """Answers: is this enforcer wired in from a configured invocation surface (or git-hook placement)?"""

    def __init__(self, root: str, surfaces: list[str], excludes: list[str], placement: list[str], closed: bool = False):
        self.root, self.placement, self.closed = root, placement, closed
        self.files: list[tuple[str, str]] = []          # (path as globbed, normalised identity)
        self.unwired: dict[str, str] = {}
        seen = set()
        for pat in surfaces:
            for hit in glob.glob(os.path.join(glob.escape(root), pat), recursive=True):
                if not os.path.isfile(hit):
                    continue
                rel = os.path.relpath(hit, root).replace(os.sep, "/")
                ident = norm(hit)
                if ident in seen or any(fnmatch.fnmatchcase(rel, ex) for ex in excludes):
                    continue
                seen.add(ident)
                self.files.append((hit, ident))
        self._refs: dict[str, set[str]] = {}
        self._hooks: tuple[str | None] | None = None

    def refs(self, hit: str, ident: str) -> set[str]:
        """Identities of the existing files named by a non-comment line of the surface file."""
        if ident in self._refs:
            return self._refs[ident]
        found: set[str] = set()
        try:
            if os.path.getsize(hit) > MAX_SURFACE_BYTES:
                raise OSError("too large")
            with open(hit, encoding="utf-8", errors="ignore") as fh:
                lines = code_lines(fh.read())
        except OSError:
            lines = []
        here = os.path.dirname(hit)
        for line in lines:
            for tok in TOKEN_RX.findall(line.replace("\\", "/")):
                tok = VAR_PREFIX_RX.sub("", tok).rstrip(",:;.)")
                if tok.startswith("./"):
                    tok = tok[2:]
                if not tok or ("/" not in tok and "." not in tok):
                    continue
                cands = [tok] if os.path.isabs(tok) else []
                cands += [os.path.join(self.root, tok.lstrip("/")), os.path.join(here, tok.lstrip("/"))]
                for c in cands:
                    if os.path.isfile(c):
                        found.add(norm(c))
        self._refs[ident] = found
        return found

    def hooks_wired(self, rel: str) -> bool:
        if self._hooks is None:
            self._hooks = (effective_hooks_dir(self.root),)
        hooks = self._hooks[0]
        if hooks is None:
            self.unwired[rel] = "git could not report the effective hooks directory"
            return False
        if norm(os.path.dirname(os.path.join(self.root, rel))) != norm(hooks):
            self.unwired[rel] = f"effective git hooks directory is {hooks}"
            return False
        return True

    def invoked(self, enforcer: str) -> bool:
        if self.closed:
            return False
        rel = enforcer.replace("\\", "/")
        if rel.startswith("./"):
            rel = rel[2:]
        if any(fnmatch.fnmatchcase(rel, g) for g in self.placement) and self.hooks_wired(rel):
            return True
        me = norm(os.path.join(self.root, enforcer))
        stem = os.path.splitext(os.path.basename(rel))[0].lower()
        for hit, ident in self.files:
            if ident == me or test_stem(os.path.basename(hit)) == stem:
                continue            # a file never invokes itself; a unit test of the enforcer is not its invoker
            if me in self.refs(hit, ident):
                return True
        return False


_ANCHOR_CACHE: dict[tuple, bool] = {}


def anchor_present(root: str, path: str, anchor: str) -> bool:
    full = os.path.join(root, path)
    try:
        st = os.stat(full)
        key = (norm(full), anchor, st.st_mtime_ns, st.st_size)
    except OSError:
        return False
    if key not in _ANCHOR_CACHE:
        try:
            with open(full, encoding="utf-8", errors="ignore") as fh:
                _ANCHOR_CACHE[key] = any(anchor in l for l in code_lines(fh.read()))
        except OSError:
            _ANCHOR_CACHE[key] = False
    return _ANCHOR_CACHE[key]


# ---------------------------------------------------------------- classification

def parse_targets(raw: list[str]) -> list[tuple[str, str | None]]:
    out = []
    for r in raw:
        path, sep, anchor = r.partition("#")
        out.append((path.strip(), anchor.strip() or None if sep else None))
    return out


def classify(text: str, entry: dict | None = None) -> tuple[str, list[tuple[str, str | None]], bool]:
    """(kind, enforced targets, via_map). Kind is a KINDS member, 'mixed' or 'untagged'. Inline tags win."""
    stripped = CODE_SPAN_RX.sub("", text)      # a tag quoted in a code span is a mention, not a tag
    raw = ENFORCED_RX.findall(stripped)
    present = [k for k, on in (("enforced", bool(raw)), ("prose", bool(PROSE_RX.search(stripped))),
                               ("judgement", bool(JUDGEMENT_RX.search(stripped))),
                               ("record", bool(RECORD_RX.search(stripped)))) if on]
    if len(present) > 1:
        return "mixed", parse_targets(raw), False
    if present:
        return present[0], parse_targets(raw) if present[0] == "enforced" else [], False
    if entry is not None:
        if entry["kind"] == "enforced":
            return "enforced", [(entry["enforcer"], entry.get("anchor"))], True
        return entry["kind"], [], True
    return "untagged", [], False


def judge(root: str, targets, inv: Invocation | None, check_inv: bool, claims: dict | None, rid: str):
    """State of an enforced claim: dangling / uninvoked / dup_anchor / backed (+ the paths to show)."""
    shown = [p if a is None else f"{p}#{a}" for p, a in targets]
    missing = [p for p, _a in targets if not cited_check(root, p)]
    if missing:
        return "dangling", missing
    if inv is not None and check_inv:
        dead = [p for p, _a in targets if not inv.invoked(p)]
        if dead:
            return "uninvoked", dead
    if claims is not None:
        for p, a in targets:
            if a is not None and not anchor_present(root, p, a):
                return "dangling", [f"{p}#{a}"]
        keys = [(norm(os.path.join(root, p)), a) for p, a in targets]
        if any(claims.get(k, rid) != rid for k in keys):
            return "dup_anchor", shown
        for k in keys:
            claims[k] = rid
    return "backed", shown


def load_rule_map(path: str, need_anchor: bool) -> dict:
    try:
        data = json.loads(read_text(path))
    except (OSError, ValueError) as e:
        raise ConfigError(f"rule map {path}: {e}")
    if not isinstance(data, dict) or data.get("schema") != MAP_SCHEMA or not isinstance(data.get("rules"), dict):
        raise ConfigError(f"rule map {path}: schema is not {MAP_SCHEMA} with a rules object")
    for rid, e in data["rules"].items():
        if not isinstance(e, dict) or e.get("kind") not in KINDS:
            raise ConfigError(f"rule map {path}: rule {rid} needs kind in {'|'.join(KINDS)}")
        if e["kind"] == "enforced":
            if not (isinstance(e.get("enforcer"), str) and e["enforcer"].strip()):
                raise ConfigError(f"rule map {path}: rule {rid} is enforced but names no enforcer")
            anchor = e.get("anchor")
            if (need_anchor or anchor is not None) and not (isinstance(anchor, str) and anchor.strip()):
                raise ConfigError(f"rule map {path}: rule {rid} is enforced but carries no anchor string")
    return data["rules"]


def resolve_root(project: dict, root_override: str | None, base: str | None) -> str:
    if root_override:
        return root_override
    cands = [c if os.path.isabs(c) or not base else os.path.join(base, c) for c in project.get("root_candidates") or []]
    if project.get("root"):
        cands.append(project["root"])
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
            lines = read_text(full).replace("\r\n", "\n").split("\n")
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
           rule_map_override: str | None = None, require_invoked: str | None = None) -> dict:
    root = resolve_root(project, root_override, base)
    name = project.get("name")
    scanned, warns = scan(project, root)
    surfaces = project.get("invocation_surfaces") or []
    mode = require_invoked or ("all" if surfaces else "off")
    invocation = "unchecked" if mode == "off" else ("checked" if surfaces else "closed")
    inv = None
    if invocation != "unchecked":
        inv = Invocation(root, surfaces, project.get("invocation_exclude") or [], project.get("placement_invoked") or [],
                         closed=(invocation == "closed"))
    entries: dict = {}
    map_path = rule_map_override or project.get("rule_map")
    if map_path:
        if not rule_map_override and (os.path.isabs(map_path) or ".." in map_path.replace("\\", "/").split("/")):
            raise ConfigError(f"project {name!r}: rule_map must be a path inside the root")
        entries = load_rule_map(map_path if rule_map_override else os.path.join(root, map_path),
                                need_anchor=invocation == "checked")
    claims = {} if inv is not None else None
    res = {"project": name, "root": root, "files": [], "counts": {}, "warnings": warns, "stale": [],
           "duplicates": [], "fanin": {}, "invocation": invocation, "placement_unwired": {}}
    keys = ("bullets", "backed", "prose", "judgement", "record", "untagged", "dangling", "mixed", "uninvoked",
            "dup_anchor", "duplicates")
    totals = dict.fromkeys(keys, 0)
    first_seen: dict[str, str] = {}
    fanin: dict[str, list] = {}
    for f in scanned:
        rows = []
        for n, text in f["units"]:
            rid = rule_id(text)
            totals["bullets"] += 1
            if rid in first_seen:                   # the same rule text again: reported, never counted twice
                totals["duplicates"] += 1
                res["duplicates"].append({"id": rid, "path": f["path"], "line": n, "first": first_seen[rid]})
                rows.append({"line": n, "id": rid, "state": "duplicate", "paths": [], "text": " ".join(text.split())[:90]})
                continue
            first_seen[rid] = f"{f['path']}:{n}"
            kind, targets, via_map = classify(text, entries.get(rid))
            if kind == "enforced":
                state, paths = judge(root, targets, inv, via_map or mode == "all", claims, rid)
                if state == "backed":
                    for p, a in targets:
                        fanin.setdefault(p.replace("\\", "/"), []).append(a)
            else:
                state, paths = kind, ([p for p, _a in targets] if kind == "mixed" else [])
            totals[state] += 1
            rows.append({"line": n, "id": rid, "state": state, "paths": paths, "text": " ".join(text.split())[:90]})
        res["files"].append({"path": f["path"], "section": f["section"], "bullets": rows})
    for rid, e in entries.items():
        if rid not in first_seen:
            res["stale"].append({"id": rid, "source": e.get("source"), "line_hint": e.get("line_hint"),
                                 "text_head": e.get("text_head")})
    totals["stale"] = len(res["stale"])
    res["counts"] = totals
    res["fanin"] = {p: {"backed": len(a), "anchors": [x for x in a if x is not None]} for p, a in sorted(fanin.items())}
    if inv is not None:
        res["placement_unwired"] = dict(inv.unwired)
    distinct = totals["bullets"] - totals["duplicates"]
    denom = distinct - totals["judgement"] - totals["record"]
    res["coverage"] = {"backed": totals["backed"], "denominator": denom,
                       "pct": round(100.0 * totals["backed"] / denom, 1) if denom > 0 else None}
    if distinct and 2 * (totals["judgement"] + totals["record"]) > distinct:
        warns.append(f"WARNING {name}: judgement+record = {totals['judgement'] + totals['record']} of "
                     f"{distinct} rules (over 50%); reclassifying rules out of the denominator can game "
                     "coverage -- review the classification")
    return res


def parse_floors(project: dict) -> list[tuple[datetime.date, int]]:
    out = []
    name = project.get("name")
    for e in project.get("floor_schedule") or []:
        try:
            ds, n = e["date"], e["backed"]
            if not (isinstance(ds, str) and DATE_RX.match(ds)) or isinstance(n, bool) or not isinstance(n, int) or n < 0:
                raise ValueError("date must be YYYY-MM-DD and backed an integer >= 0")
            out.append((datetime.date.fromisoformat(ds), n))
        except (KeyError, TypeError, ValueError) as ex:
            raise ConfigError(f"project {name!r}: bad floor_schedule entry {e!r} ({ex})")
    for (d0, n0), (d1, n1) in zip(out, out[1:]):
        if d1 <= d0:
            raise ConfigError(f"project {name!r}: floor_schedule dates must be strictly increasing ({d0} then {d1})")
        if n1 < n0:
            raise ConfigError(f"project {name!r}: floor_schedule floors must not decrease ({n0} then {n1})")
    return out


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
        cfg = json.loads(read_text(path))
    except (OSError, ValueError) as e:
        raise ConfigError(f"config {path}: {e}")
    if cfg.get("schema") != SCHEMA:
        raise ConfigError(f"config {path}: schema is not {SCHEMA}")
    return cfg


def utc_today() -> datetime.date:
    return datetime.datetime.now(datetime.timezone.utc).date()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "rule-tags.config.json"))
    ap.add_argument("--project", action="append", help="project name from the config (repeatable; default all)")
    ap.add_argument("--root", help="override the project's root (only with one --project)")
    ap.add_argument("--report", action="store_true", help="measure only: always exit 0 when the census ran")
    ap.add_argument("--check", action="store_true",
                    help="ratchet gate: exit 1 below the scheduled floor, on a dangling/mixed rule, or fail-closed")
    ap.add_argument("--today", help="YYYY-MM-DD (UTC) override for the floor date, for tests")
    ap.add_argument("--rule-map", help="use this rule-map.v1 file instead of the project's rule_map (one --project)")
    ap.add_argument("--strict-map", action="store_true", help="a STALE map entry is fatal")
    ap.add_argument("--require-invoked", nargs="?", const="all", default=None, choices=("all", "map", "off"),
                    help="enforcer must be wired in from an invocation surface: all (default when surfaces are "
                         "configured; bare flag too), map (map entries only), off; explicit all/map without "
                         "surfaces fails closed")
    ap.add_argument("--emit-map", nargs="?", const="-", metavar="FILE",
                    help="write a rule-map.v1 skeleton (every rule kind prose) for one --project to FILE or stdout")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):     # a rule's text must never crash a cp1252 console into exit 1
            stream.reconfigure(errors="backslashreplace")
    try:
        today = utc_today()
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
                try:
                    with open(a.emit_map, "w", encoding="utf-8", newline="\n") as fh:
                        fh.write(text)
                except OSError as e:
                    raise ConfigError(f"cannot write {a.emit_map}: {e}")
                print(f"check-rule-tags: wrote {len(doc['rules'])} rules to {a.emit_map}")
            return 0
        for p in projects:
            parse_floors(p)
        results = [census(p, a.root, base, a.rule_map, a.require_invoked) for p in projects]
        floors = [floor_status(p, r["counts"]["backed"], today) for p, r in zip(projects, results)]
    except (ConfigError, re.error) as e:
        print(f"check-rule-tags: ERROR {e}", file=sys.stderr)
        return 2
    bad = check_bad = 0
    for r, fl in zip(results, floors):
        c = r["counts"]
        closed = r["invocation"] == "closed"
        stale_bad = c["stale"] if a.strict_map else 0
        bad += sum(c[k] for k in BAD_STATES) + stale_bad + (1 if closed else 0)
        check_bad += c["dangling"] + c["mixed"] + stale_bad + (0 if fl is None or fl["ok"] else 1) + (1 if closed else 0)
        r["floor"] = fl
        if a.json:
            print(json.dumps(r, ensure_ascii=False))
            continue
        for f in r["files"]:
            for b in f["bullets"]:
                if b["state"] in BAD_STATES:
                    extra = {"dangling": " missing ", "uninvoked": " not invoked ", "dup_anchor": " anchor already used "
                             }.get(b["state"], "")
                    extra = f"{extra}{b['paths']}" if extra else ""
                    print(f"{STATE_LABEL.get(b['state'], b['state'].upper())} {r['project']} {f['path']}:{b['line']}{extra} {b['text']}")
        for d in r["duplicates"]:
            print(f"DUPLICATE {r['project']} {d['path']}:{d['line']} same rule text as {d['first']} (id {d['id']}); counted once")
        for s in r["stale"]:
            print(f"STALE {r['project']} map {s['id']} {s['source']}:{s['line_hint']} {s['text_head']}")
        if r["invocation"] == "unchecked":
            print(f"INVOCATION UNCHECKED {r['project']}: no invocation_surfaces configured (or --require-invoked off); "
                  "enforcer existence is the only proof")
        if closed:
            print(f"INVOCATION REQUIRED {r['project']}: --require-invoked asked for but no invocation_surfaces are "
                  "configured; every enforced rule counts as enforced-uninvoked (fail closed)")
        for enf, why in r["placement_unwired"].items():
            print(f"PLACEMENT UNWIRED {r['project']}: {enf} is not run by git: {why}")
        for w in r["warnings"]:
            print(w)
        print(f"rule-tags {r['project']}: {c['bullets']} rules, {c['backed']} backed, {c['prose']} prose, "
              f"{c['untagged']} untagged, {c['dangling']} dangling, {c['mixed']} mixed")
        cov = r["coverage"]
        pct = "n/a" if cov["pct"] is None else f"{cov['pct']}%"
        print(f"rule-tags {r['project']}: coverage {cov['backed']}/{cov['denominator']} = {pct} "
              f"(enforced {c['backed']}, judgement {c['judgement']}, record {c['record']}, prose {c['prose']}; "
              f"enforced-uninvoked {c['uninvoked']}, anchor-duplicate {c['dup_anchor']}, duplicates {c['duplicates']}, "
              f"stale-map {c['stale']})")
        if r["invocation"] != "unchecked":
            for enf, fi in r["fanin"].items():
                anchors = " | ".join(fi["anchors"]) if fi["anchors"] else "(unanchored)"
                print(f"fan-in {r['project']}: {enf} backs {fi['backed']} rule(s): {anchors}")
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
