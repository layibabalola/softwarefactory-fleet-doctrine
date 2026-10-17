#!/usr/bin/env python3
"""git pre-push layer for BUS WRITERS: run the bus's fast test suites on the pushed tip; refuse on failure.

Why (measured 2026-10-17): the bus lands on master by direct push from many automated writers, and its CI
runs only after the push. hooks/hooks.tests.py was red on f4918600 and b2cd2244 (a semantic merge conflict
between two writers) and four workflows stayed red for days; a red post-push run is advisory, nobody watched
it. This layer moves the fast suites in front of the push.

git hands a pre-push hook `<remote-name> <remote-url>` as argv and one line per ref on stdin:

    <local-ref> <local-sha> <remote-ref> <remote-sha>

Only lines whose <remote-ref> is protected (default master, main) are judged; a deletion is left to
pre-push-ff-only. For each pushed tip it lists the paths changed since <remote-sha> (all paths when the
remote tip is absent locally or new). When none of them is under a TRIGGER prefix nothing runs (exit 0:
outbox, heartbeat and cos-feedback pushes cost nothing). Otherwise the tip is checked out into a temporary
detached worktree -- the PUSHED bytes are tested, never the writer's working tree -- and every suite runs
there, python suites split into shards that run in parallel. Any failure, timeout or missing interpreter
refuses the push (exit 1) with the failing output; unproven is refused, never assumed fine.

Suites (default; --config <json> {"protected": [...], "trigger": [...], "suites": [{"name", "argv", "shard"}]}
replaces any key it names; "{python}" in argv is this interpreter):
  hooks       python hooks/hooks.tests.py                (sharded)
  pin-runner  python tools/factory/pin-runner.tests.py   (sharded)
  tool-census node tools/tool-census.tests.mjs

`--all` runs the suites whatever changed. `--shards N` (default: half the CPUs, at least 1) and
`--timeout S` (per shard, default 300). `--repo` defaults to the cwd (git runs hooks at the worktree root).
Child processes never inherit GIT_DIR / GIT_INDEX_FILE / GIT_WORK_TREE (hooks run with them set; a test
that makes its own repositories would otherwise write into the bus clone).

Exit: 0 allow, 1 refuse, 2 usage/config error (also refuses: git treats any non-zero as refusal).
Stdlib only; one file. Install: hooks/README.md.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

ZERO = re.compile(r"0{40}(?:0{24})?\Z")
SHA = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?\Z")
DEFAULT_PROTECTED = ["master", "main"]
DEFAULT_TRIGGER = ["hooks/", "tools/factory/", "tools/tool-census", "metrics/tool-census", "factory-pins/",
                   ".github/workflows/doctrine-sync.yml"]
DEFAULT_SUITES = [
    {"name": "hooks", "argv": ["{python}", "hooks/hooks.tests.py"], "shard": True},
    {"name": "pin-runner", "argv": ["{python}", "tools/factory/pin-runner.tests.py"], "shard": True},
    {"name": "tool-census", "argv": ["node", "tools/tool-census.tests.mjs"], "shard": False},
]
REPO_ENV = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
            "GIT_COMMON_DIR", "GIT_PREFIX", "GIT_NAMESPACE", "GIT_QUARANTINE_PATH")
# Run shard K of N of a unittest file: load it by path, flatten, take every N-th test by sorted id.
SHARD_DRIVER = r"""
import importlib.util, sys, unittest
path, k, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
spec = importlib.util.spec_from_file_location("bus_suite", path)
mod = importlib.util.module_from_spec(spec)
sys.modules["bus_suite"] = mod
spec.loader.exec_module(mod)
def flat(s):
    for t in s:
        if isinstance(t, unittest.TestSuite):
            yield from flat(t)
        else:
            yield t
tests = sorted(flat(unittest.defaultTestLoader.loadTestsFromModule(mod)), key=lambda t: t.id())
if not tests:
    print("no tests found in " + path, file=sys.stderr)
    sys.exit(1)
mine = unittest.TestSuite(t for i, t in enumerate(tests) if i % n == k)
result = unittest.TextTestRunner(verbosity=1).run(mine)
sys.exit(0 if result.wasSuccessful() else 1)
"""


def child_env() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if k.upper() not in REPO_ENV}
    env["GIT_OPTIONAL_LOCKS"] = "0"
    return env


def git(repo: str, *args: str, timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, timeout=timeout, env=child_env())


def full(name: str) -> str:
    return name if name.startswith("refs/") else f"refs/heads/{name}"


def protected_ref(ref: str, protected: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(ref, full(p)) for p in protected)


def tips(lines: list[str], protected: list[str]) -> tuple[dict[str, str | None], list[str]]:
    """{pushed sha: remote sha or None (unknown base)} for protected, non-deleting lines; plus usage errors."""
    out: dict[str, str | None] = {}
    errors = []
    for raw in lines:
        if not raw.strip():
            continue
        parts = raw.split()
        if len(parts) != 4:
            errors.append(f"malformed pre-push line: {raw.strip()!r}")
            continue
        _lref, lsha, rref, rsha = parts
        if not protected_ref(rref, protected) or ZERO.match(lsha):
            continue
        if not SHA.match(lsha):
            errors.append(f"malformed sha in line: {raw.strip()!r}")
            continue
        base = None if ZERO.match(rsha) else rsha
        if lsha in out and out[lsha] != base:
            base = None
        out[lsha] = base
    return out, errors


def changed_paths(repo: str, sha: str, base: str | None) -> list[str] | None:
    """Paths changed base..sha; None when the base is unknown or absent locally (then everything runs)."""
    if base is None or git(repo, "cat-file", "-e", f"{base}^{{commit}}").returncode != 0:
        return None
    p = git(repo, "diff", "--no-renames", "--name-only", "-z", base, sha)
    if p.returncode != 0:
        return None
    return [x.decode("utf-8", "replace") for x in p.stdout.split(b"\0") if x]


def triggered(paths: list[str] | None, trigger: list[str]) -> list[str] | None:
    if paths is None:
        return None
    return [p for p in paths if any(p == t or p.startswith(t) for t in trigger)]


def jobs_for(suites: list[dict], shards: int) -> list[tuple[str, list[str]]]:
    out = []
    for s in suites:
        argv = [sys.executable if a == "{python}" else a for a in s["argv"]]
        if s.get("shard") and shards > 1 and argv[0] == sys.executable and len(argv) == 2:
            for k in range(shards):
                out.append((f"{s['name']} shard {k + 1}/{shards}",
                            [sys.executable, "-c", SHARD_DRIVER, argv[1], str(k), str(shards)]))
        else:
            out.append((s["name"], argv))
    return out


def run_job(name: str, argv: list[str], cwd: str, timeout: int) -> tuple[str, int | None, str, float]:
    exe = argv[0] if os.path.isabs(argv[0]) else shutil.which(argv[0])
    if not exe:
        return name, None, f"interpreter not found: {argv[0]}", 0.0
    t0 = time.monotonic()
    try:
        p = subprocess.run([exe, *argv[1:]], cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout, env=child_env())
    except subprocess.TimeoutExpired:
        return name, None, f"timed out after {timeout}s", time.monotonic() - t0
    except OSError as exc:
        return name, None, f"cannot start {argv[0]}: {exc}", time.monotonic() - t0
    return name, p.returncode, (p.stdout or "") + (p.stderr or ""), time.monotonic() - t0


def test_tip(repo: str, sha: str, suites: list[dict], shards: int, timeout: int) -> list[str]:
    """Check out sha into a temp detached worktree, run every job in parallel, return refusal lines."""
    tmp = tempfile.mkdtemp(prefix="bus-tests-")
    wt = os.path.join(tmp, "tip")
    try:
        add = git(repo, "worktree", "add", "--detach", "--force", wt, sha, timeout=300)
        if add.returncode != 0:
            return [f"cannot check out {sha[:12]} for testing: {add.stderr.decode('utf-8', 'replace').strip()}"]
        jobs = jobs_for(suites, shards)
        refusals = []
        with cf.ThreadPoolExecutor(max_workers=len(jobs)) as pool:
            for name, rc, out, secs in pool.map(lambda j: run_job(j[0], j[1], wt, timeout), jobs):
                if rc == 0:
                    print(f"[bus-tests] ok   {name} ({secs:.0f}s)", file=sys.stderr)
                    continue
                tail = "\n".join(out.strip().splitlines()[-40:])
                refusals.append(f"{name} FAILED on {sha[:12]} ({'exit ' + str(rc) if rc is not None else out})"
                                + (f"\n{tail}" if rc is not None else ""))
        return refusals
    finally:
        git(repo, "worktree", "remove", "--force", wt, timeout=300)
        shutil.rmtree(tmp, ignore_errors=True)
        git(repo, "worktree", "prune")


def load_config(path: str | None) -> dict:
    if not path:
        return {}
    with open(path, encoding="utf-8") as fh:
        cfg = json.load(fh)
    if not isinstance(cfg, dict):
        raise ValueError("config must be a JSON object")
    for key in ("protected", "trigger"):
        if key in cfg and not (isinstance(cfg[key], list) and all(isinstance(x, str) for x in cfg[key])):
            raise ValueError(f"config '{key}' must be a list of strings")
    if "suites" in cfg:
        ok = isinstance(cfg["suites"], list) and all(
            isinstance(s, dict) and isinstance(s.get("name"), str) and isinstance(s.get("argv"), list)
            and s["argv"] and all(isinstance(a, str) for a in s["argv"]) for s in cfg["suites"])
        if not ok:
            raise ValueError("config 'suites' must be a list of {name, argv[, shard]}")
    return cfg


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("remote", nargs="?")
    ap.add_argument("url", nargs="?")
    ap.add_argument("--protect", action="append", default=[])
    ap.add_argument("--config")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--all", action="store_true", help="run the suites whatever the push changed")
    ap.add_argument("--shards", type=int, default=max(1, (os.cpu_count() or 2) // 2))
    ap.add_argument("--timeout", type=int, default=300, help="seconds per shard")
    a = ap.parse_args(argv)
    try:
        cfg = load_config(a.config)
    except (OSError, ValueError) as exc:
        print(f"[bus-tests] PUSH REFUSED: config error: {exc}", file=sys.stderr)
        return 2
    protected = a.protect or cfg.get("protected") or DEFAULT_PROTECTED
    trigger = cfg.get("trigger") or DEFAULT_TRIGGER
    suites = cfg.get("suites") or DEFAULT_SUITES
    repo = os.path.abspath(a.repo)
    lines = sys.stdin.read().splitlines()
    pushed, errors = tips(lines, protected)
    if errors:
        for e in errors:
            print(f"[bus-tests] PUSH REFUSED: {e}", file=sys.stderr)
        return 2
    t0 = time.monotonic()
    refusals = []
    for sha, base in pushed.items():
        hit = triggered(changed_paths(repo, sha, base), trigger)
        if hit == [] and not a.all:
            print(f"[bus-tests] {sha[:12]}: no change under {', '.join(trigger)}; no suite run", file=sys.stderr)
            continue
        why = "--all" if a.all else ("base unknown" if hit is None else f"{len(hit)} path(s), e.g. {hit[0]}")
        print(f"[bus-tests] {sha[:12]}: running {', '.join(s['name'] for s in suites)} ({why})", file=sys.stderr)
        refusals += test_tip(repo, sha, suites, max(1, a.shards), a.timeout)
    if refusals:
        for r in refusals:
            print(f"[bus-tests] {r}", file=sys.stderr)
        print(f"[bus-tests] PUSH REFUSED: {len(refusals)} suite job(s) failed ({time.monotonic() - t0:.0f}s). "
              f"Fix the tip; a red bus master is what this layer exists to stop.", file=sys.stderr)
        return 1
    if pushed:
        print(f"[bus-tests] pass ({time.monotonic() - t0:.0f}s)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
