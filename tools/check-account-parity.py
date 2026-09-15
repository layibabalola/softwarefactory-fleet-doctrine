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

A SECOND TRAP, measured 2026-09-15 (Conjugal, Dell XPS 17), which is why this file changed:

  * A SIGNED-OUT CLI reads as UNKNOWN, not as drift, and repairs nothing -- and that is the
    exact state the tool exists to catch, because scheduled dead-man floors execute the
    standalone binary and go dark while the desktop app looks perfectly healthy. Widening
    the repair trigger to cover it was considered and REJECTED: `~/.claude.json` is a
    profile cache, not the credential store, so "no accountUuid" has benign causes (a
    desktop-only host, a machine mid-bootstrap, a torn read of a file that is rewritten
    constantly), and an unattended floor wake is a SessionStart -- it would fire a
    focus-stealing login window at a machine nobody is watching. Detection only here;
    enforcement belongs in the consumer's own floor spawn path, where failing closed is
    correct. The verdict is now NAMED so a consumer can act on it.

  * NOTHING PRIMED THE PREFILL AUTOMATICALLY. realign-cli.py's learn() captures fingerprint
    -> address and is called UNCONDITIONALLY, ahead of its own "cannot compare" guard, so any
    direct run of that script while signed in primes the map. But this hook -- the only part
    that runs on its own -- invoked the wizard ONLY from the drift branch, i.e. only while
    the CLI still holds the account being LEFT. So in unattended operation the map could be
    written only by drift events, and priming it with a HEALTHY account depended on a human
    happening to run realign-cli.py by hand. Observed: a host MATCHED all day on 5247997b9e08
    whose map held only b4d2646b85c1, the account it had rotated away from two days earlier.
    `MAP.get(desktop_fp)` then misses and the wizard launches with no --email, inviting
    re-authentication onto the wrong account -- the failure this tool exists to prevent, on a
    credential store the app copy and the runner binary share. Worst on a fresh machine,
    the population PROMPT-A explicitly designs for: the map is empty at the first event, so
    there is nothing to offer. We therefore learn on the MATCHED branch, where the address on
    offer is the healthy one and no manual step is involved.

    (An earlier draft of this note said the map could only EVER learn abandoned accounts.
    That was too strong -- it overlooked that learn() sits before realign-cli.py's guard --
    and is narrowed here rather than left standing.)

Tests: tests/test_account_parity.py (hermetic; sandboxed HOME/APPDATA, launches nothing).
"""
from __future__ import annotations
import hashlib, json, os, pathlib, subprocess, sys

MAP = pathlib.Path.home() / ".claude" / "account-email-map.json"   # shared with realign-cli.py

def fp(v): return hashlib.sha256(v.encode()).hexdigest()[:12] if isinstance(v, str) and v.strip() else None

def load(p):
    try: return json.loads(pathlib.Path(p).read_text(encoding="utf-8", errors="replace"))
    except Exception: return None

def learn(f, email):
    """Record fingerprint -> address while BOTH are visible, which is only true while the
    CLI is signed in to that account. Best effort: a read-only home must never turn a
    parity check into an error. Contains no credential -- an address and a hash."""
    if not (f and email): return
    try:
        m = load(MAP) or {}
        if m.get(f) != email:
            m[f] = email
            MAP.parent.mkdir(parents=True, exist_ok=True)
            MAP.write_text(json.dumps(m, indent=2), encoding="utf-8")
    except Exception:
        pass

def desktop():
    base = os.environ.get("APPDATA") or os.environ.get("XDG_CONFIG_HOME") or (pathlib.Path.home() / ".config")
    p = pathlib.Path(base) / "Claude" / "config.json"
    if not p.exists(): return None, f"desktop config not found at {p}"
    d = load(p)
    if d is None: return None, "desktop config unreadable"
    u = d.get("lastKnownAccountUuid")
    return (fp(u), None) if u else (None, "desktop config has no lastKnownAccountUuid")

def cli():
    """Returns (fingerprint, error, address, signed_out). `signed_out` distinguishes a
    config that exists and names no account -- a CLI that was signed out -- from one that
    is missing or unparseable, which says nothing at all. A consumer that gates on this
    needs to tell those apart; a single UNKNOWN cannot."""
    p = pathlib.Path.home() / ".claude.json"
    if not p.exists(): return None, f"CLI config not found at {p}", None, False
    d = load(p)
    if d is None: return None, "CLI config unreadable", None, False
    acc = d.get("oauthAccount") or {}
    u = acc.get("accountUuid")
    if u: return fp(u), None, acc.get("emailAddress"), False
    return None, "CLI has no oauthAccount.accountUuid (signed out?)", None, True

def main() -> int:
    d_fp, d_err = desktop()
    c_fp, c_err, c_email, c_signed_out = cli()
    print(f"[parity] desktop fp={d_fp or '-'}{'  (' + d_err + ')' if d_err else ''}")
    print(f"[parity] cli     fp={c_fp or '-'}{'  (' + c_err + ')' if c_err else ''}")

    # Learn while the CLI is signed in -- on the HEALTHY account, not only on the one being
    # left behind. Without this the prefill map fills with departed accounts (see docstring).
    learn(c_fp, c_email)

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
            # Flush first. stdout is block-buffered when a hook captures it, so without this
            # the child's writes overtake everything above and the operator reads the remedy
            # before the diagnosis that caused it.
            sys.stdout.flush()
            try:
                subprocess.run([sys.executable, str(wiz), "--auto"], timeout=60)
            except Exception as exc:
                print(f"[parity] wizard failed ({exc.__class__.__name__}); run it yourself: {wiz} --auto")
        else:
            print("[parity] repair: python tools/realign-cli.py --auto   (opens a login window)")
    elif d_fp and c_signed_out:
        # Named, not repaired. This is the state that darkens scheduled floors while the
        # desktop app looks healthy, so it must be distinguishable by a consumer that wants
        # to fail closed before spawning unattended work. Launching a login from here was
        # rejected: see the second trap in the docstring.
        print("[parity] *** CLI-SIGNED-OUT *** the desktop app is signed in; the CLI is not.")
        print("[parity] Nothing is wrong with the app. Anything that runs the standalone")
        print("[parity] binary - scheduled tasks, dead-man floors, `claude -p` - is DARK.")
        print("[parity] This is NOT repaired automatically: a signed-out CLI has benign")
        print("[parity] causes, and an unattended wake must not open a login window.")
        print("[parity] repair (you run it): python tools/realign-cli.py --auto")
    else:
        print("[parity] UNKNOWN - could not read one or both surfaces; parity unverified, "
              "which is not the same as aligned")
    return 0  # always

if __name__ == "__main__":
    sys.exit(main())
