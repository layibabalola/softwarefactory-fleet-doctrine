#!/usr/bin/env python3
"""delivery-at-identity.py -- K7 detector: was the KEYED tree the delivery target's tip AFTER the key accepted it?

Read-only. For each accepted subject (the last ``VERDICT: ACCEPT`` row of an Outcome table, or the last
``## Outcome - ACCEPTED`` section written by a delivery chain: ``git push origin <cand>:master`` plus a
``**Receipts**`` block), read from the S-file and from any ``*.md`` in its doc-size child directory
``S<n>-<slug>/``, decide from git alone:

  AT-IDENTITY                        a reflog entry of the delivery ref put a commit whose tree equals the
                                     keyed tree at the tip, the tip still held it at an instant at or after
                                     the key's acceptance time, and the NEXT move of the ref recorded the
                                     subject's Outcome (the first first-parent commit after the keyed one
                                     writes ``## Outcome`` into the S-file or its child directory) -- or
                                     the ref still points at it (Outcome pending: the delivery chain's own
                                     check, run between its two pushes)
  NOT-AT-IDENTITY TIP-BEFORE-ACCEPTANCE  the keyed tree was a tip, but the ref moved on before the key
                                     accepted it (the S1 shape, refused by the 2026-10-17 ruling)
  NOT-AT-IDENTITY MOVED-BEFORE-OUTCOME   the keyed tree was the tip at or after acceptance, but the ref's
                                     next move was not the subject's Outcome
  NOT-AT-IDENTITY ACCEPTANCE-UNPROVEN    the keyed tree was a tip, and no acceptance time can be proven
                                     (no ``--accepted-at`` and no verifiable Receipts block)
  NOT-AT-IDENTITY OUTCOME-UNPROVEN       the tip moved after acceptance and the subject has no S-file to
                                     prove the next move was its Outcome
  NOT-AT-IDENTITY DESCENDANT-CLEAN   the keyed tree was never a tip; the first witnessed tip containing the
                                     candidate changed none of the candidate's own paths (a
                                     path-manifest-style reading -- still NOT identity)
  NOT-AT-IDENTITY DESCENDANT-TOUCHED as above, but the range changed the candidate's own paths
  NOT-AT-IDENTITY NOT-DELIVERED      no witnessed tip contains the candidate
  NOT-AT-IDENTITY REFLOG-GAP         candidate older than the oldest reflog entry of the ref
  UNRESOLVABLE / IDENTITY-MISMATCH   the cited candidate does not resolve, or its tree is not the cited tree

Clocks. A tip's interval is [reflog time of the entry that set it, reflog time of the next entry); the
reflog time is when THIS clone's ref moved, which is the only clock K7 asks about. Commit dates are never
read for it (rebase rewrites committer dates; author dates say when bytes were written, not delivered).
Reflog times have whole-second resolution and are truncated, so ``next > accepted`` is conservative: a
move in the same second as the acceptance is not proof that the tip held at or after it.

Acceptance time, in order: ``--accepted-at S<n>=<ISO-8601 with offset or Z>``; else the Outcome's
``**Receipts**`` block -- the rollout it names (``~/.codex/...`` resolved under ``--codex-home``, default
``$CODEX_HOME`` or ``~/.codex``; a ``.zst`` sibling is read with the stdlib ``compression.zstd``), the
final-answer line it names, whose SHA-256 must equal the recorded
final-answer record SHA-256, and that record's ``timestamp``. Anything less is ACCEPTANCE-UNPROVEN.

Candidate's own paths = paths changed on the candidate's first-parent line since the subject's declaration
commit (non-merge commits only), minus the S-file itself.

A reflog is clone-local: run it in the clone that pushes (``--ref refs/remotes/origin/master``, the
default) or name the integration branch the subject declared (``--ref refs/heads/master``).

Exit 0 = every reported subject AT-IDENTITY; 1 = at least one is not; 2 = usage or read error.
Every git call is ``git --no-optional-locks -c core.quotepath=off -C <repo>``; it never writes.

Run:  python delivery-at-identity.py --repo <clone> [--files <checkout>] [--dir coordination/kernel-dogfood]
        [--ref <ref>] [--only S102,S107] [--extra S1=<cand> ...] [--accepted-at S1=<iso> ...] [--codex-home DIR]
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROW = re.compile(
    r"^\|\s*(?P<round>\d+)\s*\|\s*`(?P<cand>[0-9a-f]{7,40})`\s*\|\s*`(?P<tree>[0-9a-f]{40})`\s*\|"
    r"\s*`(?P<verdict>VERDICT: (?:ACCEPT|REFUSE)[^`]*)`\s*\|")
SNUM = re.compile(r"^S(\d+)-")
ACCEPTED_HEAD = re.compile(r"(?m)^## Outcome - ACCEPTED")
NEXT_HEAD = re.compile(r"(?m)^## ")
PUSHED = re.compile(r"`git push origin ([0-9a-f]{7,40}):master`")
VERDICT_TREE = re.compile(r"verdict line `VERDICT: ACCEPT tree=([0-9a-f]{40})`")
RECEIPTS = re.compile(r"\*\*Receipts(?:, round \d+)?\*\* \(`(?P<path>[^`]+)`, \d+ records, final answer on line (?P<line>\d+)\)")
FA_SHA = re.compile(r"final-answer record SHA-256 `(?P<sha>[0-9a-f]{64})`")


class ReadError(Exception):
    pass


def git(repo: str, *args: str) -> tuple[int, str]:
    p = subprocess.run(["git", "--no-optional-locks", "-c", "core.quotepath=off", "-C", repo, *args],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, p.stdout.strip()


def reflog(repo: str, ref: str) -> list[tuple[str, str, str, int]]:
    """(commit, tree, subject, unix time) per entry, newest first."""
    rc, out = git(repo, "log", "-g", ref, "--format=%H%x09%T%x09%gs%x09%gd", "--date=unix")
    if rc:
        raise ReadError(f"cannot read the reflog of {ref} in {repo}")
    rows = []
    for line in out.splitlines():
        parts = line.split("\t")
        m = re.search(r"@\{(\d+)\}$", parts[3]) if len(parts) == 4 else None
        if not m:
            raise ReadError(f"unparseable reflog line: {line!r}")
        rows.append((parts[0], parts[1], parts[2], int(m.group(1))))
    if not rows:
        raise ReadError(f"the reflog of {ref} is empty")
    return rows


def iso(t: float) -> str:
    return _dt.datetime.fromtimestamp(t, _dt.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def parse_time(s: str) -> float:
    s = s.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    t = _dt.datetime.fromisoformat(s)
    if t.tzinfo is None:
        raise ValueError(f"{s!r} has no UTC offset")
    return t.timestamp()


def tree(repo: str, rev: str) -> str:
    return git(repo, "rev-parse", f"{rev}^{{tree}}")[1]


def own_paths(repo: str, cand: str, decl: str | None) -> set[str]:
    # non-merge commits on the candidate's first-parent line since the declaration: a pre-key
    # merge's second-parent content is the target's, not the subject's
    rng = f"{decl}^..{cand}" if decl else f"{cand}^..{cand}"
    rc, out = git(repo, "log", "--first-parent", "--no-merges", "--name-only", "--format=", rng)
    return {p for p in out.splitlines() if p} if rc == 0 else set()


def accepted_section(text: str) -> str | None:
    """The last ``## Outcome - ACCEPTED`` section, whitespace-normalised (the Outcome text is wrapped)."""
    heads = list(ACCEPTED_HEAD.finditer(text))
    if not heads:
        return None
    start = heads[-1].start()
    nxt = NEXT_HEAD.search(text, heads[-1].end())
    return " ".join(text[start:nxt.start() if nxt else len(text)].split())


def accepted_row(text: str) -> dict | None:
    """The accepting round: the last ACCEPT row of an Outcome table, else the last ACCEPTED section that
    names a ``git push origin <cand>:master`` and a receipted verdict line."""
    acc = None
    for line in text.splitlines():
        m = ROW.match(line)
        if m and m.group("verdict").startswith("VERDICT: ACCEPT"):
            acc = m.groupdict()
    if acc:
        return acc
    sec = accepted_section(text)
    if sec:
        p, v = PUSHED.search(sec), VERDICT_TREE.search(sec)
        if p and v:
            return {"round": "", "cand": p.group(1), "tree": v.group(1), "verdict": f"VERDICT: ACCEPT tree={v.group(1)}"}
    return None


def acceptance_from_receipts(text: str, codex_home: Path) -> tuple[float | None, str]:
    """(unix time, how) from the ACCEPTED section's Receipts block, or (None, why not)."""
    sec = accepted_section(text) or " ".join(text.split())
    r, f = RECEIPTS.search(sec), FA_SHA.search(sec)
    if not r or not f:
        return None, "no Receipts block with a final-answer record SHA-256"
    path = r.group("path")
    p = codex_home / path[len("~/.codex/"):] if path.startswith("~/.codex/") else Path(path)
    if p.is_file():
        raw = p.read_bytes()
    elif p.with_name(p.name + ".zst").is_file():
        try:
            from compression import zstd   # stdlib from Python 3.14; codex compresses old rollouts
        except ImportError:
            return None, f"rollout is zstd-compressed and this Python has no compression.zstd: {p}.zst"
        raw = zstd.decompress(p.with_name(p.name + ".zst").read_bytes())
    else:
        return None, f"rollout not found: {p}"
    lines = raw.split(b"\n")
    n = int(r.group("line"))
    if not 1 <= n <= len(lines):
        return None, f"{p.name} has no line {n}"
    rec = lines[n - 1].rstrip(b"\r")
    if hashlib.sha256(rec).hexdigest() != f.group("sha"):
        return None, f"{p.name} line {n} does not hash to the recorded final-answer SHA-256"
    try:
        return parse_time(json.loads(rec)["timestamp"]), f"receipt {p.name}:{n}"
    except (ValueError, KeyError, TypeError) as e:
        return None, f"{p.name} line {n} has no readable timestamp ({e})"


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


def sfiles_of(files: Path, kdir: str) -> list[Path]:
    kd = files / kdir
    if not kd.is_dir():
        raise ReadError(f"no subject directory {kd}")
    found = [f for f in kd.glob("S*.md") if SNUM.match(f.name)]
    return sorted(found, key=lambda p: int(SNUM.match(p.name).group(1)))


def records_outcome(repo: str, prev: str, nxt: str, rel: str) -> tuple[bool, str]:
    """Did the ref's move prev -> nxt record the subject's Outcome? The first first-parent commit after prev
    on nxt's line must have prev as its first parent and write ``## Outcome`` into the S-file or its child
    directory."""
    if git(repo, "merge-base", "--is-ancestor", prev, nxt)[0]:
        return False, "the next tip does not descend from the keyed commit"
    rc, out = git(repo, "rev-list", "--first-parent", "--reverse", f"{prev}..{nxt}")
    first = out.splitlines()[0] if rc == 0 and out else ""
    if not first or git(repo, "rev-parse", f"{first}^1")[1] != prev:
        return False, "the keyed commit is not on the next tip's first-parent line"
    stem = rel[:-3] + "/"
    rc, out = git(repo, "diff", "--name-only", prev, first)
    touched = [p for p in out.splitlines() if p == rel or p.startswith(stem)]
    for p in touched:
        rc, body = git(repo, "show", f"{first}:{p}")
        if rc == 0 and re.search(r"(?m)^## Outcome", body):
            return True, first
    return False, f"{first[:9]} is not the subject's Outcome"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", required=True, help="the clone whose reflog witnesses delivery")
    ap.add_argument("--files", help="checkout holding the subject directory (default: --repo)")
    ap.add_argument("--dir", default="coordination/kernel-dogfood", help="subject directory, relative to --files")
    ap.add_argument("--ref", default="refs/remotes/origin/master", help="the delivery ref whose reflog is read")
    ap.add_argument("--only", default="", help="comma-separated subject ids to report (default: all)")
    ap.add_argument("--extra", nargs="*", default=[],
                    help="S<n>=<candidate> for subjects whose Outcome is not yet written or predates both grammars")
    ap.add_argument("--accepted-at", nargs="*", default=[],
                    help="S<n>=<ISO-8601 with offset>: the key's acceptance time (overrides the Receipts block)")
    ap.add_argument("--codex-home", help="where ~/.codex/ in a Receipts block resolves (default $CODEX_HOME or ~/.codex)")
    a = ap.parse_args(argv)
    files = Path(a.files or a.repo)
    home = Path(a.codex_home or os.environ.get("CODEX_HOME") or Path.home() / ".codex")

    try:
        log = reflog(a.repo, a.ref)
        sfiles = sfiles_of(files, a.dir)
    except ReadError as e:
        print(f"REFUSE: {e}", file=sys.stderr)
        return 2
    rel_of = {f.name.split("-")[0]: f"{a.dir}/{f.name}" for f in sfiles}
    texts: dict[str, str] = {}
    subjects = []
    for f in sfiles:
        s = f.name.split("-")[0]
        texts[s] = subject_text(f)
        acc = accepted_row(texts[s])
        if acc:
            subjects.append((s, acc["cand"], acc["tree"], rel_of[s]))
    for e in a.extra:
        if "=" not in e:
            print(f"REFUSE: --extra wants S<n>=<candidate>, got {e!r}", file=sys.stderr)
            return 2
        s, c = e.split("=", 1)
        subjects = [x for x in subjects if x[0] != s]
        subjects.append((s, c, tree(a.repo, c), rel_of.get(s)))
    accepted_at: dict[str, float] = {}
    for e in a.accepted_at:
        s, _, t = e.partition("=")
        try:
            accepted_at[s] = parse_time(t)
        except ValueError as err:
            print(f"REFUSE: --accepted-at wants S<n>=<ISO-8601 with offset>, got {e!r} ({err})", file=sys.stderr)
            return 2
    only = {s.strip() for s in a.only.split(",") if s.strip()}
    if only:
        subjects = [x for x in subjects if x[0] in only]
        missing = only - {x[0] for x in subjects}
        if missing:
            print(f"REFUSE: no accepted Outcome row found for {','.join(sorted(missing))}", file=sys.stderr)
            return 2

    chron = [(h, t, gs, ts) for h, t, gs, ts in reversed(log)]  # oldest first
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
        windows = [i for i, e in enumerate(chron) if e[1] == keyed]
        if windows:
            if s in accepted_at:
                acc, how = accepted_at[s], "--accepted-at"
            else:
                acc, how = acceptance_from_receipts(texts.get(s, ""), home) if s in texts else (None, "no S-file")
            if acc is None:
                bad += 1
                print(f"{s} NOT-AT-IDENTITY ACCEPTANCE-UNPROVEN cand={cand[:9]} tree={keyed} ({how})")
                continue
            verdict = None
            for i in windows:
                h, _, gs, since = chron[i]
                nxt = chron[i + 1] if i + 1 < len(chron) else None
                if nxt and not nxt[3] > acc:
                    verdict = verdict or (f"TIP-BEFORE-ACCEPTANCE cand={cand[:9]} tree={keyed} tip={h[:9]} "
                                          f"held {iso(since)}..{iso(nxt[3])} accepted={iso(acc)} ({how})")
                    continue
                if nxt is None:
                    print(f"{s} AT-IDENTITY cand={cand[:9]} tree={keyed} tip={h[:9]} since={iso(since)} ({gs}) "
                          f"accepted={iso(acc)} ({how}) outcome=pending (still the tip)")
                    break
                if not rel:
                    verdict = (f"OUTCOME-UNPROVEN cand={cand[:9]} tree={keyed} tip={h[:9]} next={nxt[0][:9]} "
                               f"at {iso(nxt[3])}: no S-file to prove the next move was the Outcome")
                    continue
                ok, why = records_outcome(a.repo, h, nxt[0], rel)
                if ok:
                    print(f"{s} AT-IDENTITY cand={cand[:9]} tree={keyed} tip={h[:9]} held {iso(since)}..{iso(nxt[3])} "
                          f"({gs}) accepted={iso(acc)} ({how}) outcome={why[:9]}")
                    break
                verdict = (f"MOVED-BEFORE-OUTCOME cand={cand[:9]} tree={keyed} tip={h[:9]} held "
                           f"{iso(since)}..{iso(nxt[3])} accepted={iso(acc)} next={nxt[0][:9]}: {why}")
            else:
                bad += 1
                print(f"{s} NOT-AT-IDENTITY {verdict}")
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
        print(f"{s} NOT-AT-IDENTITY {kind} cand={cand[:9]} tree={keyed} first_tip={first[0][:9]} {iso(first[3])} "
              f"({first[2]}) own_paths={len(mine)} touched={','.join(touched) or '-'}")
    print(f"SUMMARY subjects={len(subjects)} not_at_identity={bad} ref={a.ref} -> {'PASS' if bad == 0 else 'FAIL'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
