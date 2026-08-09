# AUTONOMOUS LANE IGNITION — investigation on THIS machine (DNG project)

**Author:** fable `565d8b69-3d62-4256-934e-ca5138c0b1c5`, 2026-08-08 ~18:10 -05:00.
**USER ask (verbatim scope):** can Claude desktop/CLI puppet Codex Desktop; can Claude spawn sessions
with a specific model and effort without chips the USER must click. Cross-project fable (epitaxy
fleet) reported both mechanisms proven on its side; this file re-measures **on this machine, for this
project** — nothing is adopted from the other report without local proof.

## Measured findings (all probed this session, not quoted)

### F1 — Codex lanes are ALREADY chip-free here for *existing* threads
`~/.codex/automations/` holds **two ACTIVE automations on this very project**: `sol-lane-coordination-pulse`
and `luna-lane-coordination-pulse` (created 2026-08-07, `kind="heartbeat"`, `FREQ=MINUTELY;INTERVAL=10`,
each pinned to a `target_thread_id`). This is why sol and luna beat every ~10 min with no paste. The
paste bottleneck exists **only for creating a NEW Codex thread** (a dead lane needing a fresh seat).

### F2 — `codex exec` route: mechanism valid, binary NOT installed here
`codex` is not on PATH; no exe under `%LOCALAPPDATA%\Codex`; no npm global shim. `~/.codex/auth.json`
EXISTS (desktop auth present). The other project's route 1 (`codex exec "<prompt>" -m <model>`,
non-interactive, thread-resumable) therefore **cannot run here until codex-cli is installed** — an
install is a machine change: USER-gated per the standing gate list.

### F3 — Claude lanes chip-free: `claude -p --model <id> --effort <level>` CONFIRMED in local help
Claude Code 2.1.224 exposes `-p/--print`, `--model`, `--effort`, `--resume`/`--continue`. A live seat
(or a scheduled task) can spawn an independent top-level session with model+effort pinned — no chip,
no host-model inheritance (deletes the T3-chip inheritance constraint). Caveat measured elsewhere and
consistent with our 08-08 drainage incident: **same account = same usage window**; `-p` children share
the drain. Chip-spawn remains the attended fallback.

### F4 — UI puppeteering: not needed, filed last-resort-only
Nothing the CLIs lack; fragile; adds a screen-automation trust surface. Do not build.

## What adoption needs before any of this ignites a lane (proposed, not ruled)

- **A hub CONSENSUS-CALL on independence:** does a Codex seat invoked/authored by Claude retain
  cross-family review independence? Proposed answer (aligned with the other fable): yes **iff** the
  prompt passed is the frozen RESUME.md §3 seat prompt verbatim — contamination is prompt authorship,
  not invocation mechanics. The prompts are already frozen in RESUME.md §3; the invoker may not edit them.
- **A one-shot drill:** hub-written automation TOML for a NEW thread (no `target_thread_id`) — does
  Codex Desktop create the thread, or is `codex exec` the only new-thread route? Unknown; measure, don't assume.
- **Warden launch mode:** scheduled-task `claude -p` is the obvious candidate; any scheduled task goes
  through the machine registry + `run-hidden.vbs` discipline, and the 07-29 "USER declined OS scheduler"
  ruling is SUPERSEDED by the USER's 08-08 autonomy directive only if the USER confirms that reading.
- **Launcher-code rule:** `codex exec` / `claude -p` exit codes are launcher codes; a lane is proven
  seated only by its lease+beat advancing (same as chips today).
- **USER's one irreducible act stays:** CLI re-auth on account rotation (R-11).

## Blocked-on-USER list (exact)
1. Install codex-cli (machine change) — enables new-thread Codex ignition.
2. Confirm the OS-scheduler reading above if a scheduled warden is wanted.
