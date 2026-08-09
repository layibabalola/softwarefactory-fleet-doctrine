# agent-bridge — factory spec (joined the bus 2026-08-09)

**Late join, and the lateness was measured:** agent-bridge helped design this bus (hub #29,
2026-08-08) but never seeded its own spec, and its resume entry point carried no pointer
here. On 2026-08-09 it re-derived, at the cost of an 11h43m dark board, defects this repo
already carried as rulings ("configured != running", app scheduler is a FLOOR, global_limit
silent skips). This file exists so that never repeats.

## Shape

- **Board:** five lanes (user order 2026-08-09) — SOL (Codex adversary), LUNA (Codex
  implementer), OPUS (Claude verifier), SONNET (Claude implementer), FABLE (Claude hub).
- **Truth:** append-only WAL at `<repo>\.claude-state\HUB_RUN_WAL.md` (outranks every
  document); leases under `coordination\leases\`; entry point
  `coordination\RESUME.md` (§B manifest of self-deriving frozen payloads).
- **Protected invariants (drift-checked, never weaken):** remote_labels_trusted:false;
  mutations_require_local_confirmation:true; remote_messages_are_requests:true.
- **NO-push law** on the product repo; landings are gate-cleared pure-FF at the hub's gate.
  This doctrine repo is a separate remote with the opposite policy, recorded explicitly.

## Ignition (2026-08-09, post-incident)

- App-resident scheduled tasks are RETIRED for this board: registry desyncs on account
  rotation (measured: 22 task dirs on disk, ZERO enumerated live after a 02:40–03:00
  reauth), creation hard-prompts the operator, app-gated execution.
- Primary: OS Windows Scheduled Task `agent-bridge-warden` (every 15 min) →
  `coordination\automation\Run-Warden.ps1` — deterministic no-LLM detector; wakes stuck
  Codex lanes (`codex exec resume <thread>`), ignites vacant/dark lanes headlessly from §B
  payload POINTERS (`claude -p --model <id>` / `codex exec` with the frozen payload
  VERBATIM — independence = prompt authorship, per the fleet R1 ruling). 60-min per-lane
  cooldown; logs under `automation\logs\`.
- Minute registry: agent-bridge's app-store claims 4/19/34/49 are RELEASED (tasks
  retired); the OS warden is outside the app store and does not claim minutes.

## Doctrine duty

- The warden syncs this repo each run: pull always; add/commit/push ONLY
  `specs/agent-bridge.md` and attributed appends. Hubs read `RULINGS.md` + `TRAPS.md` at
  boot and ADOPT-OR-DISTINGUISH on the WAL.
