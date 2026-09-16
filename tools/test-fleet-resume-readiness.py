#!/usr/bin/env python
"""Proof for tools/fleet-resume-readiness.py.

The tool's whole value is that it separates states a careless survey collapses. So the test is
mostly about the separations, not about the happy path:

  * a member not checked out here must NOT read as delinquent, and must NOT read as compliant;
  * a tool present but unwired must not read the same as one never installed;
  * wired but never fired must not read as ready, because configuration is not execution;
  * a differently NAMED implementation must still be recognised -- the tool's own first run
    reported Cloudvore ABSENT while it was firing, because the survey keyed on a filename.

It also pins the refusal behaviour: a reporter that always exits 0 is a warning, and a guard that
warns has failed open.
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "fleet-resume-readiness.py"

FAILURES = []


def check(label, condition, detail=""):
    if condition:
        print("  ok   " + label)
    else:
        print("  FAIL " + label + ((" -- " + detail) if detail else ""))
        FAILURES.append(label)


def load():
    spec = importlib.util.spec_from_file_location("fleet_resume_readiness", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    io.open(path, "w", encoding="utf-8", newline="\n").write(text)


def make_member(root, name, script_rel=None, wired=True, script_body=None):
    """A fake member tree. script_rel None means the member never installed anything."""
    repo = root / name
    repo.mkdir(parents=True, exist_ok=True)
    if script_rel:
        body = script_body if script_body is not None else (
            "import os\n# writes into ~/.claude/session-checkpoints/<repo>\n"
            "ROOT = 'session-checkpoints'\n")
        write(repo / script_rel, body)
        if wired:
            write(repo / ".claude" / "settings.json", json.dumps({
                "hooks": {"Stop": [{"hooks": [{
                    "type": "command",
                    "command": 'python "$CLAUDE_PROJECT_DIR/' + script_rel + '"',
                }]}]}
            }, indent=2) + "\n")
        else:
            write(repo / ".claude" / "settings.json", json.dumps({"hooks": {}}, indent=2) + "\n")
    return repo


def fire(ckroot, repo, age_hours=0.0, name="SESSION-X.md"):
    d = ckroot / repo.name
    d.mkdir(parents=True, exist_ok=True)
    f = d / name
    write(f, "checkpoint\n")
    if age_hours:
        old = time.time() - age_hours * 3600
        os.utime(f, (old, old))


KERNEL_STUB = """# stub

## 6. Fleet mapping (provisional)

| Project | Proposed profile | Confidence | Acceptance bar |
|---|---|---|---|
| alpha | code | high | x |
| beta | code | high | x |
| gamma (with a parenthetical) | code | high | x |
| delta | code | high | x |
| epsilon | code | high | x |
| zeta | code | high | x |

## 7. Known gaps
"""


def run_case(tmp):
    mod = load()
    root = tmp / "fleet"
    ckroot = tmp / "ckroot"
    ckroot.mkdir(parents=True, exist_ok=True)

    kernel = tmp / "kernel.md"
    write(kernel, KERNEL_STUB)
    mod.KERNEL = str(kernel)
    mod.checkpoint_root = lambda: str(ckroot)

    print("case: the roster comes from the §6 SECTION, and parentheticals are stripped")
    names = mod.roster()
    check("six members parsed", names == ["alpha", "beta", "gamma", "delta", "epsilon", "zeta"],
          str(names))

    print("case: an empty or missing mapping is REFUSED, never reported as a clean fleet")
    empty = tmp / "empty.md"
    write(empty, "# no section here\n")
    mod.KERNEL = str(empty)
    try:
        mod.roster()
        check("refuses a kernel with no §6", False, "returned instead of refusing")
    except SystemExit as exc:
        check("refuses a kernel with no §6", exc.code == 2, "exit=" + str(exc.code))
    mod.KERNEL = str(kernel)

    # alpha: fully installed, wired, fired recently   -> READY
    a = make_member(root, "alpha", "coordination/tools/session-checkpoint.py")
    fire(ckroot, a, 1.0)
    # beta: installed and wired, never fired          -> NOT-FIRING
    make_member(root, "beta", "tools/session-checkpoint.py")
    # gamma: installed, NOT wired                     -> NOT-WIRED
    make_member(root, "gamma", "tools/session-checkpoint.py", wired=False)
    # delta: nothing installed                        -> ABSENT
    make_member(root, "delta")
    # epsilon: wired under a DIFFERENT NAME, fired    -> READY (capability, not filename)
    e = make_member(root, "epsilon", "tools/rotation-ready.py")
    fire(ckroot, e, 2.0)
    # zeta: unmapped entirely                         -> UNREACHABLE

    paths = {"alpha": str(root / "alpha"), "beta": str(root / "beta"),
             "gamma": str(root / "gamma"), "delta": str(root / "delta"),
             "epsilon": str(root / "epsilon")}
    pm = tmp / "paths.json"
    write(pm, json.dumps({"repos": paths}, indent=2) + "\n")
    mod.PATHMAP = str(pm)

    print("case: the four evidence layers are reported as four different states")
    got = {}
    for name in mod.roster():
        state, detail = mod.assess(name, paths.get(name), 72)
        got[name] = state
    check("installed + wired + fresh  -> READY", got.get("alpha") == mod.READY, str(got))
    check("wired but never fired      -> NOT-FIRING", got.get("beta") == mod.NOT_FIRING, str(got))
    check("installed but not wired    -> NOT-WIRED", got.get("gamma") == mod.NOT_WIRED, str(got))
    check("never installed            -> ABSENT", got.get("delta") == mod.ABSENT, str(got))
    check("unmapped member            -> UNREACHABLE",
          got.get("zeta") == mod.UNREACHABLE, str(got))

    print("case: a differently NAMED implementation is still recognised")
    check("rotation-ready.py reads READY, not ABSENT", got.get("epsilon") == mod.READY, str(got))

    print("case: a script that cannot checkpoint does not count as one")
    d = make_member(root, "delta2", "tools/session-checkpoint.py",
                    script_body="print('I am a linter, not a checkpoint')\n")
    state, _ = mod.assess("delta2", str(d), 72)
    check("a wired non-checkpoint script reads ABSENT", state == mod.ABSENT, state)

    print("case: freshness is a separate layer from firing")
    st = make_member(root, "stalegoat", "tools/session-checkpoint.py")
    fire(ckroot, st, 500.0)
    state, detail = mod.assess("stalegoat", str(st), 72)
    check("an old checkpoint reads STALE, not READY", state == mod.STALE, state + " " + detail)
    state, _ = mod.assess("stalegoat", str(st), 1000)
    check("the same checkpoint is READY under a wider limit", state == mod.READY, state)

    print("case: a file that is not a checkpoint is not evidence of firing")
    # Reproduces a FALSE GREEN the independent acceptance key found: a member whose hook is broken,
    # with an unrelated file sitting in its checkpoint folder, read READY.
    broken = make_member(root, "brokenhook", "tools/session-checkpoint.py")
    d = ckroot / broken.name
    d.mkdir(parents=True, exist_ok=True)
    write(d / "notes.txt", "an unrelated file")
    state, detail = mod.assess("brokenhook", str(broken), 72)
    check("an unrelated file does NOT make it READY", state != mod.READY, state + " " + detail)
    check("it reads NOT-FIRING", state == mod.NOT_FIRING, state)

    print("case: install verification is not a session-driven fire")
    iv = make_member(root, "justinstalled", "tools/session-checkpoint.py")
    fire(ckroot, iv, 0.1, name="SESSION-WIRECHECK.md")
    state, detail = mod.assess("justinstalled", str(iv), 72)
    check("a WIRECHECK checkpoint reads INSTALL-VERIFIED, not READY",
          state == mod.INSTALL_VERIFIED, state + " " + detail)
    check("INSTALL-VERIFIED is not counted ready", state != mod.READY, state)
    # A real session later must override it, whatever the relative ages.
    fire(ckroot, iv, 5.0, name="SESSION-realsession.md")
    state, _ = mod.assess("justinstalled", str(iv), 72)
    check("a real session checkpoint outranks a newer install stamp",
          state == mod.READY, state)

    print("case: UNREACHABLE is neither ready nor failing")
    mod.PATHMAP = str(pm)
    rc = mod.main(["--json"])
    check("exits 1 while a reachable member is not ready", rc == 1, "rc=" + str(rc))

    print("case: exits 0 only when every reachable member is ready")
    ready_only = tmp / "ready.json"
    write(ready_only, json.dumps({"repos": {"alpha": str(root / "alpha")}}, indent=2) + "\n")
    mod.PATHMAP = str(ready_only)
    rc = mod.main(["--json"])
    check("exits 0 when all reachable members are READY", rc == 0, "rc=" + str(rc))


def main():
    if not TOOL.exists():
        print("FAIL: tool not found at " + str(TOOL))
        return 1
    with tempfile.TemporaryDirectory(prefix="fleet-readiness-test-") as raw:
        out = io.StringIO()
        real = sys.stdout
        try:
            sys.stdout = out          # main() prints a report; keep it out of the test log
            run_case(Path(raw))
        finally:
            sys.stdout = real
        for line in out.getvalue().splitlines():
            if line.startswith("  ok ") or line.startswith("  FAIL") or line.startswith("case:"):
                print(line)
    if FAILURES:
        print("\nFAIL fleet-resume-readiness: " + str(len(FAILURES)) + " check(s) failed")
        for f in FAILURES:
            print("  - " + f)
        return 1
    print("\nPASS fleet-resume-readiness")
    return 0


if __name__ == "__main__":
    sys.exit(main())
