#!/usr/bin/env python3
"""git pre-push layer: a consumer never grows its own copy of a shared factory tool.

Sharing is the default: every factory tool runs from the bus BY PIN (factory-pins/pin-runner.py).
This hook refuses (exit 1) a push whose new commits ADD or MODIFY a file whose basename belongs
to a shared tool family, so the fleet's duplicate count (tools/tool-census.mjs) can only fall:

  * canonical families -- the tool ships from the bus (tools/factory/*, hooks/*): any add or
    modify of a same-named file is refused. Run it by pin instead.
  * census families -- counted by tools/tool-census.mjs but with no bus canonical yet: ADDING a
    new copy is refused; editing the one a project already has is allowed (it is the source).

Not refused:
  * the vendored runner itself (`--runner-path`, default factory-pins/pin-runner.py) when its blob
    in the pushed tip equals the runner blob pinned in that tip's factory-pins.json -- any other
    content is refused (adopt it byte-identical with `pin-runner.py adopt-runner`);
  * a path listed in the allowlist (`--allowlist`, default factory-pins/no-unpinned-tool.json,
    read from the PUSHED tip so the exemption is reviewed in the same change):
        {"allow": [{"path": "coordination/tools/check-doc-size.py",
                    "reason": "forwarder; callers X, Y name this path",
                    "expires": "YYYY-MM-DD"}]}
    An entry needs a reason and an expiry no later than --max-days (default 120) from today; an
    expired entry refuses, naming itself, so a kept copy is re-justified or retired.

Which commits: for each pushed ref, the files that differ between the pushed tip and its base --
the remote tip when it is known locally, else the merge-base with refs/remotes/<remote>/HEAD,
master or main, else (no base at all) every file in the tip. Deleting a ref is never judged.
git hands the hook `<remote> <url>` as argv and `<local-ref> <local-sha> <remote-ref> <remote-sha>`
lines on stdin. git calls inherit the hook's environment (GIT_DIR is set when the push runs from a
linked worktree, and names that worktree's repository correctly) and run in --repo (default cwd).

Exit: 0 allow, 1 refuse, 2 usage/config error (also refuses). Stdlib only; one file.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import subprocess
import sys

ZERO = re.compile(r"0{40}(?:0{24})?\Z")
SHA = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?\Z")

# Families shared on the bus. Kept equal to tools/tool-census.config.json by hooks/hooks.tests.py.
CANONICAL = {   # ships from the bus: refuse add AND modify
    "check-doc-size": ("check-doc-size.py", "check_doc_size.py"),
    "pin-runner": ("pin-runner.py", "pin_runner.py"),
    "pre-push-ff-only": ("pre-push-ff-only.py", "pre_push_ff_only.py"),
    "exact-path-add": ("exact-path-add.py", "exact_path_add.py"),
    "git-optional-locks": ("git-optional-locks.py", "git_optional_locks.py"),
    "no-unpinned-tool": ("pre-push-no-unpinned-tool.py", "pre_push_no_unpinned_tool.py"),
    "session-start-auth": ("session-start-auth.py", "session_start_auth.py"),
    "check-evidence-dumps": ("check-evidence-dumps.py", "check_evidence_dumps.py"),
    "fleet-scorecard": ("fleet-scorecard.py", "fleet_scorecard.py"),
    "kernel-subjects": ("kernel-subjects.py", "kernel_subjects.py"),
    "kernel-receipt": ("kernel-receipt.py", "kernel_receipt.py"),
    "codex-review": ("codex-review.py", "codex_review.py"),
    "kernel-config": ("kernel-config.py", "kernel_config.py"),
    "bus-tests": ("pre-push-bus-tests.py", "pre_push_bus_tests.py"),
    "session-checkpoint": ("session-checkpoint.py", "session_checkpoint.py"),
}
CENSUS = {      # counted, no bus canonical yet: refuse a NEW copy only
    "doctrine-outbox": ("doctrine_outbox.py", "doctrine-outbox.py"),
    "doctrine-triage": ("fold-triage.mjs", "doctrine-triage.mjs"),
    "resumability-check": ("resumability-check.py", "resumability_check.py"),
    "doctrine-periodic": ("doctrine-periodic.py", "doctrine_periodic.py"),
    "account-parity": ("check-account-parity.py", "check_account_parity.py", "check-account-parity.ps1",
                       "check_account_parity.ps1", "account-parity.py", "account-parity.ps1"),
    "realign-cli": ("realign-cli.py", "realign_cli.py", "realign-cli.ps1", "realign_cli.ps1"),
}


class Usage(Exception):
    pass


def git(repo: str, *args: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0"}
    return subprocess.run(["git", "--no-optional-locks", "-C", repo, *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=120, env=env)


def family_of(path: str) -> tuple[str, str] | None:
    base = path.rsplit("/", 1)[-1].lower()
    for kind, table in (("canonical", CANONICAL), ("census", CENSUS)):
        for fam, names in table.items():
            if base in names:
                return fam, kind
    return None


def base_of(repo: str, remote: str, lsha: str, rsha: str) -> str | None:
    if not ZERO.match(rsha) and git(repo, "cat-file", "-e", f"{rsha}^{{commit}}").returncode == 0:
        return rsha
    for ref in (f"refs/remotes/{remote}/HEAD", f"refs/remotes/{remote}/master", f"refs/remotes/{remote}/main",
                "refs/remotes/origin/HEAD", "refs/remotes/origin/master", "refs/remotes/origin/main"):
        if git(repo, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}").returncode == 0:
            mb = git(repo, "merge-base", lsha, ref)
            if mb.returncode == 0 and mb.stdout.strip():
                return mb.stdout.strip()
    return None


def changed(repo: str, base: str | None, lsha: str) -> list[tuple[str, str]]:
    if base is None:
        p = git(repo, "ls-tree", "-r", "--name-only", "-z", lsha)
        if p.returncode != 0:
            raise Usage(f"cannot list {lsha[:12]}: {p.stderr.strip()}")
        return [("A", f) for f in p.stdout.split("\0") if f]
    p = git(repo, "diff", "--no-renames", "--name-status", "-z", "--diff-filter=AM", base, lsha)
    if p.returncode != 0:
        raise Usage(f"cannot diff {base[:12]}..{lsha[:12]}: {p.stderr.strip()}")
    parts = [x for x in p.stdout.split("\0") if x]
    return list(zip(parts[0::2], parts[1::2]))


def show_json(repo: str, sha: str, path: str):
    p = git(repo, "show", f"{sha}:{path}")
    if p.returncode != 0:
        return None
    try:
        return json.loads(p.stdout.lstrip("﻿"))
    except ValueError as exc:
        raise Usage(f"{path} at {sha[:12]} is not JSON ({exc})")


def allowlist(repo: str, sha: str, path: str, today: _dt.date, max_days: int) -> tuple[dict, dict]:
    doc = show_json(repo, sha, path)
    if doc is None:
        return {}, {}
    entries = doc.get("allow") if isinstance(doc, dict) else None
    if not isinstance(entries, list):
        raise Usage(f"{path}: 'allow' must be a list")
    ok, bad = {}, {}
    for e in entries:
        if not isinstance(e, dict) or not isinstance(e.get("path"), str) or not e["path"]:
            raise Usage(f"{path}: every entry needs a 'path'")
        reason, exp = e.get("reason"), e.get("expires")
        if not isinstance(reason, str) or not reason.strip():
            bad[e["path"]] = "its allowlist entry has no reason"
            continue
        try:
            until = _dt.date.fromisoformat(str(exp))
        except ValueError:
            bad[e["path"]] = "its allowlist entry has no valid 'expires' date (YYYY-MM-DD)"
            continue
        if until < today:
            bad[e["path"]] = f"its allowlist entry EXPIRED {until}: retire the copy or re-justify it"
        elif (until - today).days > max_days:
            bad[e["path"]] = f"its allowlist entry expires {until}, more than {max_days} days out: a fork, not an exemption"
        else:
            ok[e["path"]] = e
    return ok, bad


def judge(lines: list[str], args: argparse.Namespace, today: _dt.date) -> list[str]:
    refusals: list[str] = []
    for raw in lines:
        parts = raw.split()
        if not parts:
            continue
        if len(parts) != 4 or not SHA.match(parts[1]) or not SHA.match(parts[3]):
            refusals.append(f"unparseable pre-push line {raw!r}")
            continue
        _lref, lsha, rref, rsha = parts
        if ZERO.match(lsha):
            continue  # deletion: nothing is added
        hits = [(st, p, family_of(p)) for st, p in changed(args.repo, base_of(args.repo, args.remote or "origin", lsha, rsha), lsha)]
        hits = [(st, p, f) for st, p, f in hits if f and (f[1] == "canonical" or st == "A")]
        if not hits:
            continue
        allowed, bad = allowlist(args.repo, lsha, args.allowlist, today, args.max_days)
        for st, path, (fam, kind) in hits:
            verb = "adds" if st == "A" else "modifies"
            if path == args.runner_path and fam == "pin-runner":
                pins = show_json(args.repo, lsha, args.pins) or {}
                want = (pins.get("runner") or {}).get("blob") if isinstance(pins, dict) else None
                have = git(args.repo, "rev-parse", f"{lsha}:{path}").stdout.strip()
                if want and have == want:
                    continue
                refusals.append(f"{rref}: {path} is not the runner blob pinned in {args.pins} "
                                f"({have[:12] or 'absent'} != {str(want)[:12]}); adopt it byte-identical (pin-runner.py adopt-runner)")
                continue
            if path in allowed:
                continue
            why = bad.get(path)
            what = ("a copy of the shared tool '%s'; run it from the bus by pin (factory-pins/pin-runner.py run %s)" % (fam, fam)
                    if kind == "canonical" else
                    "a NEW copy of the census-counted tool '%s'; extend the existing one, or ship it on the bus and pin it" % fam)
            refusals.append(f"{rref}: {verb} {path} -- {what}" + (f" [{why}]" if why else ""))
    return refusals


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0], allow_abbrev=False)
    ap.add_argument("remote", nargs="?", default="")
    ap.add_argument("url", nargs="?", default="")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--allowlist", default="factory-pins/no-unpinned-tool.json")
    ap.add_argument("--pins", default="factory-pins/factory-pins.json")
    ap.add_argument("--runner-path", default="factory-pins/pin-runner.py")
    ap.add_argument("--max-days", type=int, default=120)
    ap.add_argument("--today", help="YYYY-MM-DD (tests); default the local date")
    args = ap.parse_args(argv)
    try:
        today = _dt.date.fromisoformat(args.today) if args.today else _dt.date.today()
        refusals = judge(sys.stdin.read().splitlines(), args, today)
    except (Usage, ValueError, OSError, subprocess.TimeoutExpired) as exc:
        print(f"[no-unpinned-tool] PUSH REFUSED: {exc}", file=sys.stderr)
        return 2
    if not refusals:
        return 0
    for r in refusals:
        print(f"[no-unpinned-tool] PUSH REFUSED: {r}", file=sys.stderr)
    print("[no-unpinned-tool] Shared tools run from the bus by pin, so the fleet's duplicate count only falls. "
          f"A copy that must stay for now goes in {args.allowlist} with a reason and an expiry.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
