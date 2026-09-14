#!/usr/bin/env python3
"""Are the desktop and CLI credential surfaces on the same account?

Portable implementation of the R6 parity check (RULINGS.md, owner ruling 2026-09-13).
Designed to run as a SessionStart hook, so it obeys three rules:

  * it ALWAYS exits 0 -- a parity checker that can block a session is worse than the drift
    it detects, and a hook that fails closed on its own bug locks the operator out;
  * it prints exactly one line per surface plus one verdict, so it is readable in a hook banner;
  * it never authenticates for you. With --repair it hands you an interactive login in a
    visible window (see realign-cli.py) -- it never logs out first, and never completes a
    login on your behalf. A depleted account is not fixed by re-auth, so the human stays the
    one who decides and the one who signs in.

THE TRAP THIS EXISTS TO AVOID: the two surfaces publish different KINDS of identifier. The
desktop config carries `lastKnownAccountUuid`; `claude auth status --json` reports `orgId`.
Those never match, so comparing them reports permanent false drift. The comparable pair is
desktop `lastKnownAccountUuid` against CLI `oauthAccount.accountUuid`, each reduced to
sha256(uuid)[:12].
"""
from __future__ import annotations
import hashlib, json, os, pathlib, subprocess, sys

def fp(v): return hashlib.sha256(v.encode()).hexdigest()[:12] if isinstance(v, str) and v.strip() else None

def load(p):
    try: return json.loads(pathlib.Path(p).read_text(encoding="utf-8", errors="replace"))
    except Exception: return None

def desktop():
    base = os.environ.get("APPDATA") or os.environ.get("XDG_CONFIG_HOME") or (pathlib.Path.home() / ".config")
    p = pathlib.Path(base) / "Claude" / "config.json"
    if not p.exists(): return None, f"desktop config not found at {p}"
    d = load(p)
    if d is None: return None, "desktop config unreadable"
    u = d.get("lastKnownAccountUuid")
    return (fp(u), None) if u else (None, "desktop config has no lastKnownAccountUuid")

def cli():
    p = pathlib.Path.home() / ".claude.json"
    if not p.exists(): return None, f"CLI config not found at {p}"
    d = load(p)
    if d is None: return None, "CLI config unreadable"
    u = (d.get("oauthAccount") or {}).get("accountUuid")
    return (fp(u), None) if u else (None, "CLI has no oauthAccount.accountUuid (signed out?)")

def main() -> int:
    d_fp, d_err = desktop()
    c_fp, c_err = cli()
    print(f"[parity] desktop fp={d_fp or '-'}{'  (' + d_err + ')' if d_err else ''}")
    print(f"[parity] cli     fp={c_fp or '-'}{'  (' + c_err + ')' if c_err else ''}")

    if d_fp and c_fp and d_fp == c_fp:
        print("[parity] MATCHED - surfaces agree; provider work may proceed (R6)")
    elif d_fp and c_fp:
        # Loud, and then repaired, because this is the state that silently poisons an inventory
        # probe: a CLI on the wrong account fails every model challenge exactly as an absent
        # model does, yielding a false capability table rather than an auth error.
        print("[parity] *** DRIFT *** CLI and desktop are on DIFFERENT accounts.")
        print("[parity] Do not probe provider capability until this is repaired (R6.1) -")
        print("[parity] a mismatched account reports every model as unavailable.")
        print("[parity] Artifacts derived under the old account are now stale (R6.2):")
        print("[parity]     check `probed_under` in any machine-inventory.yaml before trusting it.")
        if "--repair" in sys.argv:
            # Hands the operator an interactive login in a visible window; it authenticates
            # nothing by itself and never logs out first. The wizard owns the cooldown, so a
            # dismissed browser does not reopen on every subsequent session.
            wiz = pathlib.Path(__file__).with_name("realign-cli.py")
            print("[parity] launching re-auth (interactive; finish it in the browser) ...")
            try:
                subprocess.run([sys.executable, str(wiz), "--auto"], timeout=60)
            except Exception as exc:
                print(f"[parity] wizard failed ({exc.__class__.__name__}); run it yourself: {wiz} --auto")
        else:
            print("[parity] repair: python tools/realign-cli.py --auto   (opens a login window)")
    else:
        print("[parity] UNKNOWN - could not read one or both surfaces; parity unverified, "
              "which is not the same as aligned")
    return 0  # always

if __name__ == "__main__":
    sys.exit(main())
