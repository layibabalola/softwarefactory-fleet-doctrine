#!/usr/bin/env python3
"""Refuse raw evidence committed to a project's tree (canonical factory tool).

Owner rule 2026-10-16: paperwork shrinks as a rule; evidence is HASHES PLUS A BRANCH, not a
committed dump. The tree keeps only an evidence directory's `SHA256SUMS` and a pointer file naming
the git ref that holds the raw bytes; logs, dumps, mutant JSON and large text live on that ref.

The convention (one evidence directory, on the main line):

    <dir>/SHA256SUMS      "<sha256>  <name>" per raw file (sha256sum format; '*' binary marker ok)
    <dir>/EVIDENCE-REF    "ref: <git ref>"            required: the branch holding the raw files
                          "path: <dir in that ref>"   optional, default <dir>
                          "commit: <sha>"             optional: verify at this commit, not the tip
                          "remote: <name>"            optional: also look for the ref at
                                                      refs/remotes/<name>/<branch> (tried first)
                          "objects: <template>"       optional: CONTENT-ADDRESSED store; each blob is
                                                      at <template> with <aa> = first two hex of its
                                                      sha256 and <sha256> = the full digest; path ignored
    <dir>/*.md            optional short summary, under the per-file and per-dir byte caps

Content-addressed variant (Cloudvore K179, an orphan branch holding every project's blobs):

    ref: refs/heads/evidence-store
    remote: origin
    objects: objects/<aa>/<sha256>

SHA256SUMS lines may end in CRLF and may carry the '*' binary marker.

When the pointer's ref (or commit) resolves in the local repo, every SHA256SUMS line is verified
against the blob at <ref>:<path>/<name> (or <ref>:<objects template>); a missing blob or a
different hash refuses. When it does
not resolve the check says UNVERIFIED and passes, unless --require-ref. A missing pointer refuses.

What refuses (exit 1), for paths in `scope` and not in `exclude`:
  RAW         basename matches `raw_patterns` (logs, dumps, mutant JSON ...), anywhere
  LARGE_TEXT  basename matches `large_text.patterns` and the blob exceeds `large_text.max_bytes`
  NOT_ALLOWED a file in an evidence dir that is not SHA256SUMS, the pointer or `allowed_in_evidence_dir`
  TOO_BIG     an allowed file in an evidence dir over `max_file_bytes`
  DIR_TOO_BIG an evidence dir whose committed bytes exceed `max_dir_bytes`
  NO_SUMS / NO_POINTER / BAD_POINTER   the convention's two files are missing or malformed
  BLOB_MISSING / SUMS_MISMATCH         the pointer resolves and the raw bytes do not match the sums

An evidence dir is any directory matching `evidence_dirs`, and (default on) any directory that
holds a file named SHA256SUMS.

Config (JSON; keys beginning with "_" are comments):
  schema                  "factory-check-evidence-dumps.v1"                         (required)
  scope                   [glob, ...] paths checked                        (default ["*"])
  exclude                 [glob, ...] never checked (test fixtures, vendored trees)
  evidence_dirs           [glob, ...] directories that must follow the convention
  sums_marks_evidence_dir bool, default true
  raw_patterns            [glob, ...] raw evidence types
  large_text              {"patterns": [glob, ...], "max_bytes": int}
  allowed_in_evidence_dir [glob, ...] besides SHA256SUMS and the pointer  (default ["*.md"])
  max_file_bytes          int, default 16384
  max_dir_bytes           int, default 65536
  pointer_name            default "EVIDENCE-REF"
  remedy                  [line, ...] printed when anything refuses

Globs use Python fnmatch semantics ('*' crosses '/'), like check-doc-size.py. A glob without '/'
matches the basename; a glob with '/' matches the repo-relative path.

Usage:
  check-evidence-dumps.py --config C [--repo R] [--tree [REV]]      every blob at REV (default HEAD)
  check-evidence-dumps.py --config C [--repo R] --range A..B        files added or modified in A..B,
                                                                     and every evidence dir they touch
Exit: 0 clean, 1 refused, 2 bad usage / unreadable config / git failed.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import posixpath
import re
import subprocess
import sys
from pathlib import Path

SCHEMA = "factory-check-evidence-dumps.v1"
KNOWN_KEYS = {"schema", "scope", "exclude", "evidence_dirs", "sums_marks_evidence_dir", "raw_patterns",
              "large_text", "allowed_in_evidence_dir", "max_file_bytes", "max_dir_bytes", "pointer_name",
              "remedy"}
SUMS = "SHA256SUMS"
SUM_LINE = re.compile(r"([0-9a-fA-F]{64}) [ *]?(.+)")


class UsageError(Exception):
    pass


def git(repo: Path, *args: str, binary: bool = False):
    p = subprocess.run(["git", "--no-optional-locks", "-C", str(repo), *args], capture_output=True, timeout=300)
    return p.returncode, (p.stdout if binary else p.stdout.decode("utf-8", "replace"))


def load_config(path: Path) -> dict:
    try:
        cfg = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise UsageError(f"cannot read config {path}: {e}") from None
    if not isinstance(cfg, dict) or cfg.get("schema") != SCHEMA:
        raise UsageError(f"config schema must be {SCHEMA!r}")
    unknown = {k for k in cfg if not k.startswith("_")} - KNOWN_KEYS
    if unknown:
        raise UsageError(f"unknown config keys: {sorted(unknown)}")
    cfg.setdefault("scope", ["*"])
    cfg.setdefault("exclude", [])
    cfg.setdefault("evidence_dirs", [])
    cfg.setdefault("sums_marks_evidence_dir", True)
    cfg.setdefault("raw_patterns", [])
    cfg.setdefault("large_text", {"patterns": [], "max_bytes": 0})
    cfg.setdefault("allowed_in_evidence_dir", ["*.md"])
    cfg.setdefault("max_file_bytes", 16384)
    cfg.setdefault("max_dir_bytes", 65536)
    cfg.setdefault("pointer_name", "EVIDENCE-REF")
    for k in ("scope", "exclude", "evidence_dirs", "raw_patterns", "allowed_in_evidence_dir"):
        if not isinstance(cfg[k], list) or not all(isinstance(x, str) for x in cfg[k]):
            raise UsageError(f"{k} must be a list of strings")
    lt = cfg["large_text"]
    if not isinstance(lt, dict) or not isinstance(lt.get("patterns", []), list) or not isinstance(lt.get("max_bytes", 0), int):
        raise UsageError("large_text must be {patterns: [..], max_bytes: int}")
    for k in ("max_file_bytes", "max_dir_bytes"):
        if not isinstance(cfg[k], int) or cfg[k] < 0:
            raise UsageError(f"{k} must be a non-negative int")
    return cfg


def match(path: str, globs: list[str]) -> bool:
    base = posixpath.basename(path)
    return any(fnmatch.fnmatchcase(path if "/" in g else base, g) for g in globs)


def dir_match(d: str, globs: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(d, g.rstrip("/")) for g in globs)


def tree_listing(repo: Path, rev: str) -> dict[str, tuple[int, str]]:
    """{path: (bytes, blob id)} for every blob at rev."""
    rc, out = git(repo, "ls-tree", "-r", "-l", "-z", "--full-tree", rev, binary=True)
    if rc != 0:
        raise UsageError(f"git ls-tree {rev} failed")
    files = {}
    for rec in out.decode("utf-8", "replace").split("\0"):
        if not rec:
            continue
        meta, path = rec.split("\t", 1)
        mode, typ, oid, size = meta.split()
        if typ == "blob":
            files[path] = (int(size) if size != "-" else 0, oid)
    return files


def changed_paths(repo: Path, rng: str) -> list[str]:
    if ".." not in rng:
        raise UsageError("--range must be A..B")
    a, b = rng.split("..", 1)
    rc, out = git(repo, "diff", "--name-only", "-z", "--no-renames", "--diff-filter=AM", a, b, binary=True)
    if rc != 0:
        raise UsageError(f"git diff {rng} failed")
    return [p for p in out.decode("utf-8", "replace").split("\0") if p]


def resolve(repo: Path, ref: str, remote: str | None = None) -> str | None:
    """The commit a pointer's ref names here. With `remote`, its remote-tracking ref is tried first: the
    published copy is what the pointer means, and a stale local branch must not stand in for it."""
    branch = ref[len("refs/heads/"):] if ref.startswith("refs/heads/") else (None if ref.startswith("refs/") else ref)
    cands = [f"refs/remotes/{remote}/{branch}"] if remote and branch else []
    cands.append(ref)
    if ref.startswith("refs/heads/"):
        cands.append("refs/remotes/origin/" + branch)
    elif branch:
        cands += [f"refs/heads/{ref}", f"refs/remotes/origin/{ref}"]
    for c in cands:
        rc, out = git(repo, "rev-parse", "--verify", "-q", f"{c}^{{commit}}")
        if rc == 0 and out.strip():
            return out.strip()
    return None


def parse_pointer(text: str) -> dict:
    p = {}
    for line in text.replace("\r\n", "\n").split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        k, sep, v = line.partition(":")
        if sep and k.strip().lower() in ("ref", "path", "commit", "remote", "objects"):
            p[k.strip().lower()] = v.strip()
    return p


def parse_sums(text: str) -> tuple[dict, list[str]]:
    listed, bad = {}, []
    for line in text.replace("\r\n", "\n").split("\n"):
        if not line.strip():
            continue
        m = SUM_LINE.fullmatch(line.strip())
        if not m:
            bad.append(line.strip()[:80])
        else:
            listed[m.group(2).strip()] = m.group(1).lower()
    return listed, bad


def ancestors(path: str) -> list[str]:
    """Directories above path, shortest first ('a', 'a/b' for 'a/b/c')."""
    parts = path.split("/")[:-1]
    return ["/".join(parts[:i]) for i in range(1, len(parts) + 1)]


def evidence_roots(files: dict, cfg: dict) -> set[str]:
    """Directories that must follow the convention. A root owns its whole subtree; a candidate nested
    under another root is not a second root (its files belong to the outer one)."""
    cands = set()
    for p in files:
        cands |= {d for d in ancestors(p) if dir_match(d, cfg["evidence_dirs"])}
        if cfg["sums_marks_evidence_dir"] and posixpath.basename(p) == SUMS and "/" in p:
            cands.add(posixpath.dirname(p))
    return {d for d in cands if not any(a in cands for a in ancestors(d + "/x")[:-1])}


def check_evidence_dir(repo, d, files, cfg, require_ref, out, notes):
    ptr_name = cfg["pointer_name"]
    members = {p: v for p, v in files.items() if p.startswith(d + "/")}
    total = sum(v[0] for v in members.values())
    for p, (size, _oid) in sorted(members.items()):
        if p in (posixpath.join(d, SUMS), posixpath.join(d, ptr_name)):
            continue
        if match(p, cfg["raw_patterns"]):
            continue  # already refused as RAW
        if not match(p, cfg["allowed_in_evidence_dir"]):
            out.append(("NOT_ALLOWED", p, "only SHA256SUMS, the pointer and a short summary live here; the raw file goes on the evidence ref"))
        elif size > cfg["max_file_bytes"]:
            out.append(("TOO_BIG", p, f"{size} bytes > max_file_bytes {cfg['max_file_bytes']}"))
    if total > cfg["max_dir_bytes"]:
        out.append(("DIR_TOO_BIG", d + "/", f"{total} bytes > max_dir_bytes {cfg['max_dir_bytes']}"))
    sums_p, ptr_p = posixpath.join(d, SUMS), posixpath.join(d, ptr_name)
    if sums_p not in files:
        out.append(("NO_SUMS", d + "/", f"an evidence dir carries {SUMS}"))
        return
    if ptr_p not in files:
        out.append(("NO_POINTER", d + "/", f"{SUMS} without {ptr_name}: name the ref that holds the raw bytes"))
        return
    _, ptr_text = git(repo, "cat-file", "blob", files[ptr_p][1])
    _, sums_text = git(repo, "cat-file", "blob", files[sums_p][1])
    ptr = parse_pointer(ptr_text)
    if not ptr.get("ref"):
        out.append(("BAD_POINTER", ptr_p, "no 'ref: <git ref>' line"))
        return
    tmpl = ptr.get("objects")
    if tmpl is not None and ("<sha256>" not in tmpl or tmpl.startswith("/") or ".." in tmpl.split("/")):
        out.append(("BAD_POINTER", ptr_p, "objects: must be a relative template containing <sha256>"))
        return
    listed, bad = parse_sums(sums_text)
    if bad or not listed:
        out.append(("BAD_SUMS", sums_p, f"unparseable line {bad[0]!r}" if bad else "no entries"))
        return
    at = None
    if ptr.get("commit"):
        rc, o = git(repo, "rev-parse", "--verify", "-q", f"{ptr['commit']}^{{commit}}")
        at = o.strip() if rc == 0 and o.strip() else None
    else:
        at = resolve(repo, ptr["ref"], ptr.get("remote"))
    if not at:
        what = ptr.get("commit") or ptr["ref"]
        if require_ref:
            out.append(("REF_UNAVAILABLE", ptr_p, f"{what} does not resolve locally (git fetch it)"))
        else:
            notes.append(f"UNVERIFIED {d}/: {what} does not resolve locally; {len(listed)} sums not checked")
        return
    base = ptr.get("path") or d
    for name, want in sorted(listed.items()):
        where = tmpl.replace("<aa>", want[:2]).replace("<sha256>", want) if tmpl else posixpath.join(base, name)
        rc, data = git(repo, "cat-file", "blob", f"{at}:{where}", binary=True)
        if rc != 0:
            out.append(("BLOB_MISSING", f"{d}/{name}", f"not at {at[:12]}:{where}"))
            continue
        got = hashlib.sha256(data).hexdigest()
        if got != want:
            out.append(("SUMS_MISMATCH", f"{d}/{name}", f"{SUMS} says {want[:12]}, {at[:12]} has {got[:12]}"))
    notes.append(f"VERIFIED {d}/: {len(listed)} sums against {ptr['ref']} @ {at[:12]}")


def run(repo: Path, cfg: dict, rev: str | None, rng: str | None, require_ref: bool):
    end = rng.split("..", 1)[1] if rng else (rev or "HEAD")
    files_all = tree_listing(repo, end or "HEAD")
    files = {p: v for p, v in files_all.items() if match(p, cfg["scope"]) and not match(p, cfg["exclude"])}
    targets = [p for p in changed_paths(repo, rng) if p in files] if rng else sorted(files)
    out, notes = [], []
    lt = cfg["large_text"]
    for p in targets:
        size = files[p][0]
        if match(p, cfg["raw_patterns"]):
            out.append(("RAW", p, f"{size} bytes of raw evidence; commit its sha256 to <dir>/{SUMS} and the bytes to an evidence ref"))
        elif lt.get("patterns") and match(p, lt["patterns"]) and size > lt.get("max_bytes", 0):
            out.append(("LARGE_TEXT", p, f"{size} bytes > large_text.max_bytes {lt.get('max_bytes', 0)}"))
    ev_dirs = evidence_roots(files, cfg)
    if rng:
        ev_dirs = {d for d in ev_dirs if any(p.startswith(d + "/") for p in targets)}
    for d in sorted(ev_dirs):
        check_evidence_dir(repo, d, files, cfg, require_ref, out, notes)
    return out, notes


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True)
    ap.add_argument("--repo", default=".")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--tree", nargs="?", const="HEAD", metavar="REV")
    g.add_argument("--range", metavar="A..B")
    ap.add_argument("--require-ref", action="store_true", help="refuse when a pointer's ref is not available locally")
    a = ap.parse_args(argv)
    try:
        cfg = load_config(Path(a.config))
        repo = Path(a.repo)
        rc, _ = git(repo, "rev-parse", "--git-dir")
        if rc != 0:
            raise UsageError(f"not a git repository: {repo}")
        out, notes = run(repo, cfg, a.tree, a.range, a.require_ref)
    except UsageError as e:
        print(f"check-evidence-dumps: ERROR {e}", file=sys.stderr)
        return 2
    for n in notes:
        print(n)
    for code, path, why in out:
        print(f"{code} {path}: {why}")
    what = a.range or (a.tree or "HEAD")
    if out:
        print(f"check-evidence-dumps: REFUSED {len(out)} violation(s) in {what}")
        for line in cfg.get("remedy", []):
            print(f"  {line}")
        return 1
    print(f"check-evidence-dumps: OK {what}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
