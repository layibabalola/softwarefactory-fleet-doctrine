#!/usr/bin/env python3
"""SessionStart hook: run the project's CLI auth/parity checker and surface its verdict.

Canonical fleet copy (bus tools/factory/session-start-auth.py), run BY PIN through the consumer's
vendored runner:

    python -I "$CLAUDE_PROJECT_DIR/factory-pins/pin-runner.py" run session-start-auth [-- --live]

It replaces three diverged copies (bus tools/session-start-auth.py, bus
tools/conjugal-reference/session-start-auth.py, Conjugal coordination/tools/session-start-auth.py).
The canonical behaviour is Conjugal's: it SURFACES the verdict and never repairs it. The older bus
copy re-authed from inside the hook and then wrote the CLI's own email in as the desktop email, so
parity was true by construction (self-certification) and a logout followed by an abandoned login
left the owner with no credential at all (Conjugal fix 2026-09-15). Re-auth is an owner action.

Always exits 0 -- a SessionStart hook that exits non-zero has its output hidden, the opposite of
what a rotation check is for. The checker's exit code is printed in the verdict line, so a red is
still a red.

Default is IDENTITY-ONLY (~3 s): it proves account parity (is the CLI on the account the app is
signed into?). It does NOT prove capacity: `--allow-live-probe` takes ~5 s from a terminal but
53-89 s from inside a Claude Code session (measured 2026-09-13), and a session-start hook must not
block for a minute. `--live` forces the probe (timeout 150 s).

Options
  --checker PATH       the checker, relative to the project root (default coordination/tools/check-cli-auth.py)
  --repair-hint TEXT   the sanctioned repair line printed on a red (default: the bus realign-cli.py --auto)
  --live               run the live inference probe too
The project root is $CLAUDE_PROJECT_DIR, else the git toplevel of the cwd, else the cwd -- never this
file's location, because a pinned tool runs from verified bytes outside the project.
Stdlib only.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

DEFAULT_CHECKER = "coordination/tools/check-cli-auth.py"
DEFAULT_REPAIR = r'python "C:\code\softwarefactory-fleet-doctrine\tools\realign-cli.py" --auto'


def project_root() -> str:
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env and os.path.isdir(env):
        return env
    try:
        p = subprocess.run(["git", "--no-optional-locks", "rev-parse", "--show-toplevel"], capture_output=True,
                           text=True, timeout=10)
        if p.returncode == 0 and p.stdout.strip():
            return p.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return os.getcwd()


def main(argv: list[str] | None = None) -> int:
    # Windows console defaults to cp1252; the checker prints em-dashes. Never let the evidence line crash.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0], allow_abbrev=False)
    ap.add_argument("--checker", default=DEFAULT_CHECKER)
    ap.add_argument("--repair-hint", default=DEFAULT_REPAIR)
    ap.add_argument("--live", action="store_true")
    try:
        args = ap.parse_args(argv)
    except SystemExit:
        print("[session-start] bad arguments to session-start-auth; the auth check did not run")
        return 0
    checker = args.checker if os.path.isabs(args.checker) else os.path.join(project_root(), args.checker)
    cmd = [sys.executable, checker] + (["--allow-live-probe"] if args.live else [])
    budget = 150 if args.live else 30
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=budget, encoding="utf-8", errors="replace")
        out = (p.stdout or "").strip() or (p.stderr or "").strip()
        code = p.returncode
    except subprocess.TimeoutExpired:
        out, code = f"checker timed out after {budget} s (treat as UNPROVEN, run it by hand)", 124
    except OSError as e:
        out, code = f"checker could not start: {e}", 127
    mode = "live probe" if args.live else "identity-only"
    print(f"[session-start] CLI auth/parity, {mode} (exit {code}): {out}")
    if code != 0:
        print("[session-start] NOT auto-remedying: re-auth is an owner action, and this hook must never log you out. "
              "Sanctioned repair (opens a visible login window, no logout first):")
        print(f"[session-start]   {args.repair_hint}")
        print("[session-start] NON-ZERO: paste the line above into chat before deriving anything; "
              f'run the printed remedy, then re-run: python "{checker}" --allow-live-probe')
    else:
        print("[session-start] AUTH VERIFIED.")
        if not args.live:
            print("[session-start] capacity UNPROVEN by design here; the resume dispatcher (CLAUDE.md step 0) runs "
                  f'python "{checker}" --allow-live-probe (~1 min from inside a session, ~5 s from a terminal).')
    return 0


if __name__ == "__main__":
    sys.exit(main())
