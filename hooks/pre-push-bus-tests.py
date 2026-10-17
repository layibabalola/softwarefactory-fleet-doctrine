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

Drift checks (added 2026-10-17). Some bus files are sealed by pins that CI verifies after the push: the active
r45 manifest binds README.md and six other subjects by blob, and the R26 current census binds every project's
specs/<project>.md by blob and the closed set of top-level specs. An ordinary edit to a pinned file turns CI red
(MANIFEST_SUBJECT_MISMATCH; PROJECT_SPEC_DRIFT, PROJECT_CLOSED_SET_MISMATCH) until someone runs the approved
refresh tool. When the pushed range touches a file a pin covers -- the pin file itself, every path the pin lists
AT THE PUSHED TIP, a new top-level specs/*.md for the census, and the checker -- the CI checker for that pin
runs in check mode on the pushed tip (same temporary worktree as the suites, in parallel with them):
  r45-manifest  python tools/check_universal_manifest.py --treeish HEAD          (~17 s here)
  r26-census    python tools/check_adoption_ledger.py --current --treeish HEAD   (~7 s here)
A failure refuses and prints the approved refresh command for that failure. The hook never refreshes: a
refresh is a reviewed commit (Law 1). A pushed range that touches no covered path runs no drift check, so a
writer is never refused for drift it did not touch. A pin file absent at the tip is no pin (nothing runs).
--config "drift": [{"name", "pin", "covers": "manifest-subjects"|"census-specs"|"pin-only", "also": [...],
"argv", "refresh": {TOKEN: text}}] replaces the defaults ([] turns drift checks off).

`--all` runs the suites and the drift checks whatever changed. `--shards N` (default: half the CPUs, at least 1) and
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
R45_PIN = "manifests/universal-provider-control-reconciliation-r45.json"
R26_PIN = "adoption/current-token-control-r26.json"
# {sha} = full pushed sha, {sha12}, {pin}. Each text is the bus's documented, approved procedure for that failure.
R45_REFRESH = (
    "approved refresh (docs/active-universal-manifest.md), in a clean checkout whose HEAD is {sha12}:\n"
    "    python tools/refresh_current_universal_manifest.py --candidate {sha}\n"
    "  It writes nothing. Review changedBindings (only paths this push edited may appear), write its \"manifest\"\n"
    "  object verbatim to {pin} (two-space JSON, final newline; the bytes must hash to proposedManifestSha256),\n"
    "  commit that file alone on top of {sha12} and push both commits.")
R26_REFRESH = (
    "approved refresh (adoption/current-token-control-r26.md), in a clean checkout whose HEAD is {sha12}:\n"
    "    python tools/refresh_current_adoption_census.py\n"
    "  It writes nothing. Require exit 0, write its stdout JSON verbatim to {pin}, commit that file alone on top\n"
    "  of {sha12} and push both commits. A refusal means a disposition or proof claim changed: that needs review,\n"
    "  not a refresh.")
R26_CLASSIFY = (
    "no refresh can fix this: the set of top-level specs/*.md changed. A new project spec needs a census row and a\n"
    "  portable doctrine spec needs CURRENT_NON_PROJECT_SPECS in sealed tools/check_adoption_ledger.py -- an\n"
    "  epoch amendment (bus da3e22dc), then the census refresh:\n"
    "    python tools/refresh_current_adoption_census.py\n"
    "  Or publish the document outside the top level of specs/.")
DEFAULT_DRIFT = [
    {"name": "r45-manifest", "pin": R45_PIN, "covers": "manifest-subjects", "also": [],
     "argv": ["{python}", "tools/check_universal_manifest.py", "--treeish", "HEAD"],
     "refresh": {"MANIFEST_SUBJECT_MISMATCH": R45_REFRESH, "MANIFEST_BLOB_OID_MISMATCH": R45_REFRESH}},
    {"name": "r26-census", "pin": R26_PIN, "covers": "census-specs", "also": ["tools/check_adoption_ledger.py"],
     "argv": ["{python}", "tools/check_adoption_ledger.py", "--current", "--treeish", "HEAD"],
     "refresh": {"PROJECT_SPEC_DRIFT": R26_REFRESH, "PROJECT_CLOSED_SET_MISMATCH": R26_CLASSIFY}},
]
TOP_SPEC = re.compile(r"specs/[^/]+\.md\Z")
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


def blob_json(repo: str, sha: str, path: str):
    """(present, parsed JSON or None when unreadable) for path at sha."""
    p = git(repo, "cat-file", "blob", f"{sha}:{path}")
    if p.returncode != 0:
        return False, None
    try:
        return True, json.loads(p.stdout.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return True, None


def covered_hits(repo: str, sha: str, base: str | None, paths: list[str] | None, entry: dict) -> list[str] | None:
    """Changed paths the drift entry's pin covers at the pushed tip. None = run (base unknown, or the pin cannot
    say what it covers); [] = nothing covered, or no pin at the tip."""
    present, value = blob_json(repo, sha, entry["pin"])
    if not present:
        return []
    if paths is None:
        return None
    if not paths:
        return []
    covered = {entry["pin"], *entry.get("also", [])}
    kind = entry.get("covers", "pin-only")
    try:
        if kind == "manifest-subjects":
            covered |= {row["path"] for row in value["subjectFiles"]}
        elif kind == "census-specs":
            covered |= {row["specPath"] for row in value["projects"]}
            # A new top-level spec changes the census's closed set.
            for x in paths:
                if TOP_SPEC.match(x) and x not in covered \
                        and git(repo, "cat-file", "-e", f"{base}:{x}").returncode != 0:
                    covered.add(x)
    except (TypeError, KeyError):
        return None
    return [x for x in paths if x in covered]


def drift_note(entry: dict, out: str, sha: str) -> str:
    for token, text in entry.get("refresh", {}).items():
        if token in out:
            return f"{entry['name']}: {token} -- " + text.format(sha=sha, sha12=sha[:12], pin=entry["pin"])
    return f"{entry['name']}: not a drift any approved refresh covers; fix the tip."


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


def test_tip(repo: str, sha: str, suites: list[dict], shards: int, timeout: int,
             drift: list[dict] | None = None) -> list[str]:
    """Check out sha into a temp detached worktree, run every job in parallel, return refusal lines."""
    drift = drift or []
    tmp = tempfile.mkdtemp(prefix="bus-tests-")
    wt = os.path.join(tmp, "tip")
    try:
        add = git(repo, "worktree", "add", "--detach", "--force", wt, sha, timeout=300)
        if add.returncode != 0:
            return [f"cannot check out {sha[:12]} for testing: {add.stderr.decode('utf-8', 'replace').strip()}"]
        jobs = [(n, argv, None) for n, argv in jobs_for(suites, shards)]
        jobs += [(f"drift {e['name']}", [sys.executable if x == "{python}" else x for x in e["argv"]], e)
                 for e in drift]
        refusals = []
        with cf.ThreadPoolExecutor(max_workers=max(1, len(jobs))) as pool:
            results = list(pool.map(lambda j: run_job(j[0], j[1], wt, timeout), jobs))
        for (name, rc, out, secs), (_n, _argv, entry) in zip(results, jobs):
            if rc == 0:
                print(f"[bus-tests] ok   {name} ({secs:.0f}s)", file=sys.stderr)
                continue
            tail = "\n".join(out.strip().splitlines()[-40:])
            line = (f"{name} FAILED on {sha[:12]} ({'exit ' + str(rc) if rc is not None else out})"
                    + (f"\n{tail}" if rc is not None else ""))
            if entry is not None and rc is not None:
                line += "\n[bus-tests] " + drift_note(entry, out, sha)
            refusals.append(line)
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
    if "drift" in cfg:
        ok = isinstance(cfg["drift"], list) and all(
            isinstance(e, dict) and isinstance(e.get("name"), str) and isinstance(e.get("pin"), str)
            and e.get("covers", "pin-only") in ("manifest-subjects", "census-specs", "pin-only")
            and isinstance(e.get("also", []), list) and all(isinstance(x, str) for x in e.get("also", []))
            and isinstance(e.get("argv"), list) and e["argv"] and all(isinstance(a, str) for a in e["argv"])
            and isinstance(e.get("refresh", {}), dict)
            and all(isinstance(k, str) and isinstance(v, str) for k, v in e.get("refresh", {}).items())
            for e in cfg["drift"])
        if not ok:
            raise ValueError("config 'drift' must be a list of {name, pin, covers, also, argv, refresh}")
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
    drift_cfg = cfg["drift"] if "drift" in cfg else DEFAULT_DRIFT
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
        paths = changed_paths(repo, sha, base)
        hit = triggered(paths, trigger)
        run_suites = a.all or hit != []
        drift = []
        for entry in drift_cfg:
            dhit = covered_hits(repo, sha, base, paths, entry)
            if dhit == [] and not (a.all and blob_json(repo, sha, entry["pin"])[0]):
                continue
            drift.append(entry)
            dwhy = "base unknown or pin unreadable" if dhit is None else (", ".join(dhit[:3]) if dhit else "--all")
            print(f"[bus-tests] {sha[:12]}: drift check {entry['name']} ({dwhy})", file=sys.stderr)
        if not run_suites and not drift:
            print(f"[bus-tests] {sha[:12]}: no change under {', '.join(trigger)} and no pinned path touched; "
                  f"no suite run", file=sys.stderr)
            continue
        if run_suites:
            why = "--all" if a.all else ("base unknown" if hit is None else f"{len(hit)} path(s), e.g. {hit[0]}")
            print(f"[bus-tests] {sha[:12]}: running {', '.join(s['name'] for s in suites)} ({why})", file=sys.stderr)
        refusals += test_tip(repo, sha, suites if run_suites else [], max(1, a.shards), a.timeout, drift)
    if refusals:
        for r in refusals:
            print(f"[bus-tests] {r}", file=sys.stderr)
        print(f"[bus-tests] PUSH REFUSED: {len(refusals)} job(s) failed ({time.monotonic() - t0:.0f}s). "
              f"Fix the tip; a red bus master is what this layer exists to stop.", file=sys.stderr)
        return 1
    if pushed:
        print(f"[bus-tests] pass ({time.monotonic() - t0:.0f}s)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
