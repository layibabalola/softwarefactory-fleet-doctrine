#!/usr/bin/env python3
"""Re-align the CLI credential store to the desktop account, by launching an interactive login.

    realign-cli.py --dry-run     print what would happen, touch nothing (default)
    realign-cli.py --auto        on drift, open the login flow in a new window
    realign-cli.py --verify      re-check alignment and report

Three deliberate constraints, each protecting against a way this could make things worse than
the drift it repairs:

1. IT NEVER LOGS OUT FIRST. The spec this implements describes `logout` then `login`, but a
   logout that is followed by an abandoned or failed login leaves the operator with no working
   credential at all -- strictly worse than being on the wrong account. `claude auth login`
   switches accounts on its own; if it ever refuses while signed in, that is reported for a
   human to resolve rather than forced.

2. IT OPENS A VISIBLE WINDOW, it does not authenticate for you. The login flow needs a browser
   and a human; run headless inside a hook subprocess with no console, it would appear to hang
   and then fail. A new console window is the only shape where the operator can actually see
   and finish the flow.

3. IT HAS A COOLDOWN. A SessionStart hook fires on every session. Without a cooldown, an
   operator who dismisses the browser once gets it reopened on every subsequent session --
   drift repair turning into a popup loop that trains the operator to ignore it.
"""
from __future__ import annotations
import argparse, hashlib, json, os, pathlib, subprocess, sys, time

HOME = pathlib.Path.home()
MAP = HOME / ".claude" / "account-email-map.json"      # learned fingerprint -> email
STAMP = HOME / ".claude" / ".realign-last-attempt"
COOLDOWN_S = 30 * 60


def fp(v): return hashlib.sha256(v.encode()).hexdigest()[:12] if isinstance(v, str) and v.strip() else None
def load(p):
    try: return json.loads(pathlib.Path(p).read_text(encoding="utf-8", errors="replace"))
    except Exception: return None


def desktop_fp():
    base = os.environ.get("APPDATA") or os.environ.get("XDG_CONFIG_HOME") or (HOME / ".config")
    d = load(pathlib.Path(base) / "Claude" / "config.json") or {}
    return fp(d.get("lastKnownAccountUuid"))


def cli_identity():
    d = load(HOME / ".claude.json") or {}
    acc = d.get("oauthAccount") or {}
    return fp(acc.get("accountUuid")), acc.get("emailAddress")


def learn(f, email):
    """Record fingerprint -> email while we can see both. This is the only way the wizard can
    later pre-fill --email for an account it is NOT currently signed in to: the desktop config
    publishes a uuid and no address, so the mapping has to be captured at a moment when the CLI
    happens to be on that account."""
    if not (f and email): return
    m = load(MAP) or {}
    if m.get(f) != email:
        m[f] = email
        MAP.parent.mkdir(parents=True, exist_ok=True)
        MAP.write_text(json.dumps(m, indent=2), encoding="utf-8")


def cooled_down():
    try: return (time.time() - float(STAMP.read_text().strip())) > COOLDOWN_S
    except Exception: return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--auto", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    d_fp = desktop_fp()
    c_fp, c_email = cli_identity()
    learn(c_fp, c_email)                       # always learn while signed in

    if not d_fp or not c_fp:
        print(f"[realign] cannot compare (desktop={d_fp or '-'} cli={c_fp or '-'}); doing nothing")
        return 0
    if d_fp == c_fp:
        print(f"[realign] aligned (fp={d_fp}, {c_email or 'email unknown'}) - nothing to do")
        return 0

    target = (load(MAP) or {}).get(d_fp)
    print(f"[realign] DRIFT: cli fp={c_fp} ({c_email or '?'}) but desktop fp={d_fp} "
          f"({target or 'email not yet learned'})")

    cmd = ["claude", "auth", "login"] + (["--email", target] if target else [])
    if a.verify:
        return 0
    if a.dry_run or not a.auto:
        print("[realign] dry run. Would launch, in a NEW window:", " ".join(cmd))
        print("[realign] (no logout first - a failed login after logout leaves you with nothing)")
        return 0
    if not cooled_down():
        # Say WHEN, not just "recently": a suppressed relaunch with no timestamp reads as
        # "the automation never fired" (Conjugal, 2026-09-18 - the window HAD opened).
        try:
            launched = float(STAMP.read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            launched = time.time()
        remaining = max(0, int((launched + COOLDOWN_S - time.time()) // 60))
        print(f"[realign] a login window was ALREADY opened at "
              f"{time.strftime('%H:%M:%S', time.localtime(launched))} local "
              f"(cooldown {COOLDOWN_S//60} min, ~{remaining} min left); not reopening. "
              f"Look for that window / browser tab and finish it, or re-run with --auto "
              f"after the cooldown. Stamp: {STAMP}")
        return 0

    STAMP.write_text(str(time.time()), encoding="utf-8")
    print("[realign] opening a login window; complete it in the browser that appears.")
    try:
        if os.name == "nt":
            subprocess.Popen(["cmd", "/c", "start", "Claude CLI re-auth", *cmd],
                             creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0))
        else:
            subprocess.Popen(cmd, start_new_session=True)
    except Exception as exc:
        print(f"[realign] could not launch ({exc.__class__.__name__}: {exc}). Run yourself: {' '.join(cmd)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
