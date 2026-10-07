#!/usr/bin/env python3
"""delivery-at-identity.py -- K7 detector: was the KEYED tree ever the delivery target's tree?

Read-only. For each accepted kernel-dogfood subject (the last ``VERDICT: ACCEPT`` row of its
Outcome table, read from the S-file and from any ``*.md`` in its doc-size child directory
``S<n>-<slug>/``), decide from git alone:

  AT-IDENTITY                       some reflog entry of the delivery ref points at a commit whose
                                    tree equals the keyed tree (the keyed identity was a witnessed tip)
  NOT-AT-IDENTITY DESCENDANT-CLEAN  not a witnessed tip; the first witnessed tip containing the
                                    candidate changed none of the candidate's own paths (a
                                    path-manifest-style reading -- still NOT identity under profile
                                    code unless a manifest was declared before review)
  NOT-AT-IDENTITY DESCENDANT-TOUCHED as above, but the range changed the candidate's own paths
  NOT-AT-IDENTITY NOT-DELIVERED     no witnessed tip contains the candidate
  NOT-AT-IDENTITY REFLOG-GAP        candidate older than the oldest reflog entry of the ref
  UNRESOLVABLE / IDENTITY-MISMATCH  the cited candidate does not resolve, or its tree is not the
                                    cited tree

Candidate's own paths = paths changed on the candidate's first-parent line since the subject's
declaration commit (non-merge commits only), minus the S-file itself.

A reflog is clone-local: run it in the clone that pushes (``--ref refs/remotes/origin/master``,
the default) or name the integration branch the subject declared (``--ref refs/heads/master``).

Exit 0 = every reported subject AT-IDENTITY; 1 = at least one is not; 2 = usage or read error.
Every git call is ``git --no-optional-locks -C <repo>``; it never writes.

Run:  python coordination/kernel-dogfood/delivery-at-identity.py --repo <clone> [--files <checkout>]
        [--dir coordination/kernel-dogfood] [--ref <ref>] [--only S102,S107] [--extra S1=<cand> ...]
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROW = re.compile(
    r"^\|\s*(?P<round>\d+)\s*\|\s*`(?P<cand>[0-9a-f]{7,40})`\s*\|\s*`(?P<tree>[0-9a-f]{40})`\s*\|"
    r"\s*`(?P<verdict>VERDICT: (?:ACCEPT|REFUSE)[^`]*)`\s*\|")
SNUM = re.compile(r"^S(\d+)-")


class ReadError(Exception):
    pass


def git(repo: str, *args: str) -> tuple[int, str]:
    p = subprocess.run(["git", "--no-optional-locks", "-C", repo, *args],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, p.stdout.strip()


def reflog(repo: str, ref: str) -> list[tuple[str, str, str, str]]:
    rc, out = git(repo, "log", "-g", ref, "--format=%H%x09%T%x09%gs%x09%gd", "--date=iso-strict")
    if rc:
        raise ReadError(f"cannot read the reflog of {ref} in {repo}")
    rows = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) != 4:
            raise ReadError(f"unparseable reflog line: {line!r}")
        rows.append((parts[0], parts[1], parts[2], parts[3]))
    if not rows:
        raise ReadError(f"the reflog of {ref} is empty")
    return rows  # newest first


def tree(repo: str, rev: str) -> str:
    return git(repo, "rev-parse", f"{rev}^{{tree}}")[1]


def own_paths(repo: str, cand: str, decl: str | None) -> set[str]:
    # non-merge commits on the candidate's first-parent line since the declaration: a pre-key
    # merge's second-parent content is the target's, not the subject's
    rng = f"{decl}^..{cand}" if decl else f"{cand}^..{cand}"
    rc, out = git(repo, "log", "--first-parent", "--no-merges", "--name-only", "--format=", rng)
    return {p for p in out.splitlines() if p} if rc == 0 else set()


def accepted_row(text: str) -> dict | None:
    """The accepting round of an Outcome table: the last ACCEPT row."""
    acc = None
    for line in text.splitlines():
        m = ROW.match(line)
        if m and m.group("verdict").startswith("VERDICT: ACCEPT"):
            acc = m.groupdict()
    return acc


def subject_text(sfile: Path) -> str:
    """The S-file plus its doc-size child directory (an Outcome moved to S<n>-<slug>/outcome.md)."""
    parts = [sfile.read_text(encoding="utf-8", errors="replace")]
    child = sfile.with_suffix("")
    if child.is_dir():
        for p in sorted(child.glob("*.md")):
            parts.append(p.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts)


def decl_commit(repo: str, relpath: str, ref: str) -> str | None:
    rc, out = git(repo, "log", ref, "--diff-filter=A", "--format=%H", "--", relpath)
    lines = out.splitlines() if rc == 0 else []
    return lines[-1] if lines else None


def collect(files: Path, kdir: str) -> list[tuple[str, str, str, str]]:
    kd = files / kdir
    if not kd.is_dir():
        raise ReadError(f"no subject directory {kd}")
    found = []
    sfiles = [f for f in kd.glob("S*.md") if SNUM.match(f.name)]
    for f in sorted(sfiles, key=lambda p: int(SNUM.match(p.name).group(1))):
        acc = accepted_row(subject_text(f))
        if acc:
            found.append((f.name.split("-")[0], acc["cand"], acc["tree"], f"{kdir}/{f.name}"))
    return found


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", required=True, help="the clone whose reflog witnesses delivery")
    ap.add_argument("--files", help="checkout holding the subject directory (default: --repo)")
    ap.add_argument("--dir", default="coordination/kernel-dogfood", help="subject directory, relative to --files")
    ap.add_argument("--ref", default="refs/remotes/origin/master", help="the delivery ref whose reflog is read")
    ap.add_argument("--only", default="", help="comma-separated subject ids to report (default: all)")
    ap.add_argument("--extra", nargs="*", default=[],
                    help="S<n>=<candidate> for subjects whose Outcome predates the table grammar")
    a = ap.parse_args(argv)
    files = Path(a.files or a.repo)

    try:
        log = reflog(a.repo, a.ref)
        subjects = collect(files, a.dir)
    except ReadError as e:
        print(f"REFUSE: {e}", file=sys.stderr)
        return 2
    for e in a.extra:
        if "=" not in e:
            print(f"REFUSE: --extra wants S<n>=<candidate>, got {e!r}", file=sys.stderr)
            return 2
        s, c = e.split("=", 1)
        subjects.append((s, c, tree(a.repo, c), None))
    only = {s.strip() for s in a.only.split(",") if s.strip()}
    if only:
        subjects = [x for x in subjects if x[0] in only]
        missing = only - {x[0] for x in subjects}
        if missing:
            print(f"REFUSE: no accepted Outcome row found for {','.join(sorted(missing))}", file=sys.stderr)
            return 2

    chron = [(h, gs, gd) for h, t, gs, gd in reversed(log)]  # oldest first
    tip_trees: dict[str, tuple[str, str, str]] = {}
    for h, t, gs, gd in reversed(log):
        tip_trees.setdefault(t, (h, gs, gd))  # the FIRST time the tree was a tip
    oldest = chron[0][0]

    def is_anc(x: str, y: str) -> bool:
        return git(a.repo, "merge-base", "--is-ancestor", x, y)[0] == 0

    def first_containing(full: str):
        # bisection assumes the ref only moves forward; the hit is re-verified, and a
        # non-monotone reflog falls back to a linear scan
        lo, hi = 0, len(chron)
        while lo < hi:
            mid = (lo + hi) // 2
            if is_anc(full, chron[mid][0]):
                hi = mid
            else:
                lo = mid + 1
        if lo < len(chron) and (lo == 0 or not is_anc(full, chron[lo - 1][0])):
            return chron[lo]
        for e in chron:
            if is_anc(full, e[0]):
                return e
        return None

    bad = 0
    for s, cand, keyed, rel in subjects:
        rc, full = git(a.repo, "rev-parse", "-q", "--verify", f"{cand}^{{commit}}")
        if rc:
            print(f"{s} UNRESOLVABLE cand={cand}")
            bad += 1
            continue
        actual = tree(a.repo, full)
        if actual != keyed:
            print(f"{s} IDENTITY-MISMATCH cand={cand} keyed={keyed} actual={actual}")
            bad += 1
            continue
        if keyed in tip_trees:
            h, gs, gd = tip_trees[keyed]
            print(f"{s} AT-IDENTITY cand={cand[:9]} tree={keyed} tip={h[:9]} {gd} ({gs})")
            continue
        bad += 1
        first = first_containing(full)
        if not first:
            print(f"{s} NOT-AT-IDENTITY NOT-DELIVERED cand={cand[:9]} tree={keyed}")
            continue
        if is_anc(full, oldest):
            print(f"{s} NOT-AT-IDENTITY REFLOG-GAP cand={cand[:9]} older than the oldest reflog entry")
            continue
        decl = decl_commit(a.repo, rel, a.ref) if rel else None
        mine = own_paths(a.repo, full, decl)
        mine.discard(rel or "")
        rc, out = git(a.repo, "diff", "--name-only", full, first[0])
        touched = sorted(mine & set(out.splitlines()))
        kind = "DESCENDANT-TOUCHED" if touched else "DESCENDANT-CLEAN"
        print(f"{s} NOT-AT-IDENTITY {kind} cand={cand[:9]} tree={keyed} first_tip={first[0][:9]} {first[2]} "
              f"({first[1]}) own_paths={len(mine)} touched={','.join(touched) or '-'}")
    print(f"SUMMARY subjects={len(subjects)} not_at_identity={bad} ref={a.ref} -> {'PASS' if bad == 0 else 'FAIL'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
