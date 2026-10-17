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

PreToolUse guard self-test (upstreamed from Conjugal bc8645fe9). Claude Code proceeds on ANY hook exit
except 2, so a guard whose launcher cannot start (bare `python` missing or shadowed), or whose pinned blob
is UNAVAILABLE (pin-runner exit 3), fails OPEN silently. After the verdict, every Bash|PowerShell
PreToolUse command in the project's .claude/settings.json is run exactly as spelled, through the shell
Claude Code uses (bash, else the OS shell), with a PreToolUse payload for a command that guard must
refuse; anything but exit 2 is reported as REFUSING. A hook is matched to its fixture by a substring of
its command; a hook with no fixture is listed UNTESTED. Default fixtures:
    exact-path-add       git add -A
    git-optional-locks   git status

Options
  --checker PATH       the checker, relative to the project root (default coordination/tools/check-cli-auth.py)
  --repair-hint TEXT   the sanctioned repair line printed on a red (default: the bus realign-cli.py --auto)
  --live               run the live inference probe too
  --config PATH        the consumer's config, relative to the project root (JSON, schema
                       "session-start-auth.v1"; every key optional):
                         guard_fixtures  {hook-command substring: refuse-fixture command}, merged over the
                                         defaults (null removes a default)
                         verified_text   the green line's text (default "AUTH VERIFIED.")
                         settings        the settings file to self-test (default .claude/settings.json)
                       An unreadable or malformed config is reported and the defaults are used.
  --no-guard-self-test skip the self-test
The project root is $CLAUDE_PROJECT_DIR, else the git toplevel of the cwd, else the cwd -- never this
file's location, because a pinned tool runs from verified bytes outside the project.
Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys

DEFAULT_CHECKER = "coordination/tools/check-cli-auth.py"
DEFAULT_REPAIR = r'python "C:\code\softwarefactory-fleet-doctrine\tools\realign-cli.py" --auto'
DEFAULT_SETTINGS = ".claude/settings.json"
DEFAULT_VERIFIED = "AUTH VERIFIED."
DEFAULT_FIXTURES = {"exact-path-add": "git add -A", "git-optional-locks": "git status"}
CONFIG_SCHEMA = "session-start-auth.v1"
CONFIG_KEYS = {"schema", "guard_fixtures", "verified_text", "settings"}


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


def load_config(root: str, rel: str | None) -> tuple[dict, list[str]]:
    """(config, report lines). Never raises: a bad config is reported and the defaults stand."""
    cfg = {"guard_fixtures": dict(DEFAULT_FIXTURES), "verified_text": DEFAULT_VERIFIED, "settings": DEFAULT_SETTINGS}
    if not rel:
        return cfg, []
    path = rel if os.path.isabs(rel) else os.path.join(root, rel)
    try:
        with open(path, encoding="utf-8-sig") as f:
            raw = json.load(f)
        if not isinstance(raw, dict) or raw.get("schema", CONFIG_SCHEMA) != CONFIG_SCHEMA or set(raw) - CONFIG_KEYS:
            raise ValueError(f"must be an object, schema {CONFIG_SCHEMA!r}, keys {sorted(CONFIG_KEYS)}")
        fx = raw.get("guard_fixtures", {})
        if not isinstance(fx, dict) or not all(isinstance(k, str) and k and (v is None or isinstance(v, str) and v)
                                               for k, v in fx.items()):
            raise ValueError("guard_fixtures must map non-empty strings to a command string or null")
        for k in ("verified_text", "settings"):
            if k in raw and (not isinstance(raw[k], str) or not raw[k].strip()):
                raise ValueError(f"{k} must be a non-empty string")
    except (OSError, ValueError) as e:
        return cfg, [f"[session-start] REFUSING: config {path} unusable ({e}); defaults used"]
    for k, v in fx.items():
        if v is None:
            cfg["guard_fixtures"].pop(k, None)
        else:
            cfg["guard_fixtures"][k] = v
    cfg.update({k: raw[k] for k in ("verified_text", "settings") if k in raw})
    return cfg, []


def _bash() -> str | None:
    """The bash Claude Code runs hooks with. On Windows that is Git Bash ($CLAUDE_CODE_GIT_BASH_PATH, else the
    bash beside git), never System32's bash.exe: that is the WSL launcher, where a Windows interpreter path does
    not exist, so every guard would be misreported as failing open (measured 2026-10-16 from a PowerShell host)."""
    if os.name != "nt":
        return shutil.which("bash")
    env = os.environ.get("CLAUDE_CODE_GIT_BASH_PATH")
    if env and os.path.isfile(env):
        return env
    git = shutil.which("git")
    if git:
        base = os.path.dirname(os.path.dirname(os.path.realpath(git)))  # <Git>/cmd/git.exe or <Git>/mingw64/bin/git.exe
        for c in (os.path.join(base, "bin", "bash.exe"), os.path.join(os.path.dirname(base), "bin", "bash.exe")):
            if os.path.isfile(c):
                return c
    found = shutil.which("bash")
    return found if found and "\\system32\\" not in found.lower() else None


def _hook_shell(command: str) -> list[str] | str:
    # Claude Code runs hook commands through bash (Git Bash on Windows); fall back to the OS shell.
    bash = _bash()
    return [bash, "-c", command] if bash else command


def guard_self_test(settings_path: str, root: str, fixtures: dict[str, str], timeout: int = 10) -> tuple[list[str], int]:
    """Return (report lines, number of guards that did NOT refuse their fixture)."""
    if not os.path.exists(settings_path):
        return [f"[session-start] PreToolUse guard self-test: no {settings_path}; nothing to test"], 0
    try:
        with open(settings_path, encoding="utf-8") as f:
            groups = (json.load(f).get("hooks") or {}).get("PreToolUse") or []
    except (OSError, ValueError, AttributeError) as e:
        return [f"[session-start] REFUSING: guard self-test could not read {settings_path}: {e}"], 1
    env = {k: v for k, v in os.environ.items() if k != "GIT_OPTIONAL_LOCKS"}
    env["CLAUDE_PROJECT_DIR"] = root.replace("\\", "/")
    lines, bad, ok = [], 0, 0
    for g in groups if isinstance(groups, list) else []:
        if not isinstance(g, dict) or not any(t in str(g.get("matcher", "")).split("|") for t in ("Bash", "PowerShell")):
            continue
        for h in g.get("hooks") or []:
            cmd = h.get("command", "") if isinstance(h, dict) else ""
            fixture = next((v for k, v in fixtures.items() if k in cmd), None)
            if fixture is None:
                lines.append(f"[session-start] guard self-test: UNTESTED (no fixture): {cmd}")
                continue
            payload = json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Bash", "cwd": root,
                                  "tool_input": {"command": fixture}})
            argv = _hook_shell(cmd)
            try:
                p = subprocess.run(argv, input=payload, capture_output=True, text=True, env=env,
                                   cwd=root, timeout=timeout, encoding="utf-8", errors="replace",
                                   shell=isinstance(argv, str))
                rc, err = p.returncode, (p.stderr or "").strip().splitlines()
            except subprocess.TimeoutExpired:
                rc, err = 124, [f"timed out after {timeout} s"]
            except OSError as e:
                rc, err = 127, [str(e)]
            if rc == 2:
                ok += 1
                continue
            bad += 1
            lines.append(f"[session-start] REFUSING: PreToolUse guard exited {rc} (not 2) on known-refuse fixture "
                         f"{fixture!r} -- it FAILS OPEN, Claude Code will proceed: {cmd}"
                         + (f" | stderr: {err[-1][:200]}" if err else ""))
    lines.insert(0, f"[session-start] PreToolUse guard self-test: {ok} refused, {bad} FAILED OPEN")
    return lines, bad


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
    ap.add_argument("--config")
    ap.add_argument("--no-guard-self-test", action="store_true")
    try:
        args = ap.parse_args(argv)
    except SystemExit:
        print("[session-start] bad arguments to session-start-auth; the auth check did not run")
        return 0
    root = project_root()
    cfg, cfg_lines = load_config(root, args.config)
    checker = os.path.normpath(args.checker if os.path.isabs(args.checker) else os.path.join(root, args.checker))
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
        print(f"[session-start] {cfg['verified_text']}")
        if not args.live:
            print("[session-start] capacity UNPROVEN by design here; the resume dispatcher (CLAUDE.md step 0) runs "
                  f'python "{checker}" --allow-live-probe (~1 min from inside a session, ~5 s from a terminal).')
    for line in cfg_lines:
        print(line)
    if not args.no_guard_self_test:
        settings = cfg["settings"] if os.path.isabs(cfg["settings"]) else os.path.join(root, cfg["settings"])
        for line in guard_self_test(os.path.normpath(settings), root, cfg["guard_fixtures"])[0]:
            print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
