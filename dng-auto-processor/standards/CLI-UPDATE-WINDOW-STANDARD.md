# CLI UPDATE WINDOWS — check on cadence, upgrade only in a declared quiet window

**USER directive 2026-08-08 (in chat):** keep both CLIs (claude, codex) current, safely — the hub
spins work down, opens an upgrade window, upgrades, verifies, spins work back up.

## The split that makes it safe

- **CHECK is free and frequent:** every ~6 h the live coordinator (as part of its wake duties, no
  new scheduled task — the warden task stays wake-only) compares installed vs latest:
  `npm view @openai/codex version` vs `codex --version`; `claude --version` (Claude Code manages its
  own updates — note the version, do not force). Post one line only when drift is found.
- **UPGRADE is rare and windowed.** Never upgrade under live executor traffic. Preconditions, all
  derived at window-open: no hosted executor in flight · opus resting between briefs · no exec
  children running · no landing mid-transaction. The hub then: (1) declares the window on the hub;
  (2) snapshots versions; (3) upgrades (`npm install -g @openai/codex`); (4) runs the smoke
  checklist below; (5) posts the receipt with before/after versions; (6) resumes dispatches.
  Rollback is one command: `npm install -g @openai/codex@<previous>`.
- **Cadence ruling:** the CHECK runs ~6-hourly; the UPGRADE runs when a check finds drift AND the
  pipeline reaches its next natural nothing-owed lull — the hub may wait for one, never kill work
  to make one. If a version is security-critical or unblocks a measured defect, the hub may drain
  actively (finish in-flight, hold new dispatches) instead of waiting.

## Post-upgrade smoke checklist (the fleet's three measured traps + one)

1. `codex exec "…READY…"` end-to-end (a 400 "requires newer Codex" on lane models is a VERSION gate
   wearing an auth costume — measured on a sibling at 0.142.5).
2. Sandbox mode: on Windows hosts `workspace-write` has broken the exec helper entirely
   (`helper_unknown_error`); `danger-full-access` was the working mode — verify whichever mode our
   lanes use still starts a shell.
3. PATH/shim: the bash npm shim has been broken while `codex.cmd` via PowerShell worked — verify
   through the SAME invocation path the lanes use. An empty result through the wrong shim is a
   statement about the shim.
4. Codex Desktop coexistence: confirm the automations still fire on their next tick (shared
   `~/.codex` store — an upgrade must not wedge the desktop's scheduler).

## Boundaries

Upgrading is a machine change executed under this standing USER directive — it needs no fresh ask,
but every window and receipt lands on the hub (post-facto reporting, as always). The wake-only
warden task never upgrades anything. A failed smoke check = immediate rollback + one hub line;
never leave the fleet on an unverified version overnight.
