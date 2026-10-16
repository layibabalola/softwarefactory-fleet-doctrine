#!/usr/bin/env python3
"""git pre-push layer: protected branches move fast-forward only, and are never deleted.

git hands a pre-push hook `<remote-name> <remote-url>` as argv and one line per ref on stdin:

    <local-ref> <local-sha> <remote-ref> <remote-sha>

For every line whose <remote-ref> is protected this refuses (exit 1) when
  * <local-sha> is all zeros                         -- the push DELETES the protected ref;
  * <remote-sha> is not all zeros and is not an ancestor of <local-sha>
                                                     -- a forced / non-fast-forward update
                                                        (`git push --force`, `+refs`, a rewrite);
  * the ancestry cannot be computed (remote object absent locally, git error)
                                                     -- unproven is refused, never assumed fine.
Creating a protected ref (remote-sha all zeros) is allowed. Unprotected refs are never judged.

Protected refs: `--protect <name>` (repeatable; a bare name means refs/heads/<name>), or
`--config <json>` with {"protected": ["master", "refs/heads/release/*"]}; default master and main.
fnmatch globs are allowed. `--repo` defaults to the cwd (git runs hooks at the worktree root).

Exit: 0 allow, 1 refuse, 2 usage/config error (also refuses: git treats any non-zero as refusal).
Stdlib only; one file. Install by chaining it into .git/hooks/pre-push with the ref lines on its
stdin (hooks/README.md shows the layer).
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ZERO = re.compile(r"0{40}(?:0{24})?\Z")
SHA = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?\Z")
DEFAULT_PROTECTED = ["master", "main"]


def full(name: str) -> str:
    return name if name.startswith("refs/") else f"refs/heads/{name}"


def is_ancestor(repo: str, old: str, new: str) -> bool | None:
    env = {**os.environ, "GIT_OPTIONAL_LOCKS": "0"}
    try:
        p = subprocess.run(["git", "--no-optional-locks", "-C", repo, "merge-base", "--is-ancestor", old, new],
                           capture_output=True, timeout=60, env=env)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if p.returncode == 0:
        return True
    if p.returncode == 1:
        return False
    return None  # 128: an object is missing or git failed -- cannot tell


def judge(lines: list[str], protected: list[str], repo: str) -> list[str]:
    refusals = []
    for raw in lines:
        parts = raw.split()
        if not parts:
            continue
        if len(parts) != 4 or not SHA.match(parts[1]) or not SHA.match(parts[3]):
            refusals.append(f"unparseable pre-push line {raw!r}")
            continue
        _lref, lsha, rref, rsha = parts
        if not any(fnmatch.fnmatchcase(rref, p) for p in protected):
            continue
        if ZERO.match(lsha):
            refusals.append(f"{rref}: deleting a protected branch")
        elif ZERO.match(rsha):
            continue  # creation
        else:
            anc = is_ancestor(repo, rsha, lsha)
            if anc is False:
                refusals.append(f"{rref}: {rsha[:12]} -> {lsha[:12]} is not a fast-forward")
            elif anc is None:
                refusals.append(f"{rref}: cannot prove {rsha[:12]} is an ancestor of {lsha[:12]} "
                                f"(remote tip missing locally? git fetch, then rebase)")
    return refusals


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0], allow_abbrev=False)
    ap.add_argument("remote", nargs="?", default="")
    ap.add_argument("url", nargs="?", default="")
    ap.add_argument("--protect", action="append", default=[])
    ap.add_argument("--config")
    ap.add_argument("--repo", default=".")
    args = ap.parse_args(argv)
    protected = list(args.protect)
    if args.config:
        try:
            cfg = json.loads(Path(args.config).read_text(encoding="utf-8-sig"))
            listed = cfg["protected"]
            if not isinstance(listed, list) or not all(isinstance(x, str) and x for x in listed):
                raise ValueError("protected must be a list of names")
        except (OSError, ValueError, KeyError, TypeError) as exc:
            print(f"[ff-only] PUSH REFUSED: config {args.config} unusable ({exc})", file=sys.stderr)
            return 2
        protected += listed
    protected = [full(p) for p in (protected or DEFAULT_PROTECTED)]
    refusals = judge(sys.stdin.read().splitlines(), protected, args.repo)
    if not refusals:
        return 0
    for r in refusals:
        print(f"[ff-only] PUSH REFUSED: {r}", file=sys.stderr)
    print("[ff-only] Protected branches only move forward: git fetch, rebase onto the remote tip, push again. "
          "Never force; never delete.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
