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

## Kimi model portfolio — measured proposal, awaiting hub ratification (2026-08-10)

Operator order: exploit model diversity inside every provider, while retaining exact
`provider/model/effort/adapter-version` identity. Kimi Code CLI `0.34.0` was queried locally
through its authenticated managed catalog (`kimi provider list --json`). The catalog returned
exactly four aliases under provider `managed:kimi-code`:

| exact profile candidate | catalog display | context | intended fleet role |
|---|---|---:|---|
| `moonshot/kimi-code/k3/native:low/kimi-code-cli@0.34.0` | K3 | 1,048,576 | narration, relay, triage, bounded summarization; never a final gate vote |
| `moonshot/kimi-code/k3/native:high/kimi-code-cli@0.34.0` | K3 | 1,048,576 | default complex implementation, design, and deep review candidate |
| `moonshot/kimi-code/k3/native:max/kimi-code-cli@0.34.0` | K3 | 1,048,576 | escalation profile for the hardest adjudication-grade analysis; reserve for measured need |
| `moonshot/kimi-code/k3-256k/native:low/kimi-code-cli@0.34.0` | K3-256k | 262,144 | fast bounded-context scan, relay, and low-risk maintenance candidate |
| `moonshot/kimi-code/k3-256k/native:high/kimi-code-cli@0.34.0` | K3-256k | 262,144 | ordinary bounded-context implementation/review candidate when the 256k window is sufficient |
| `moonshot/kimi-code/k3-256k/native:max/kimi-code-cli@0.34.0` | K3-256k | 262,144 | bounded-context escalation candidate; benchmark against full K3 before preference |
| `moonshot/kimi-code/kimi-for-coding/native:fixed(always-thinking)/kimi-code-cli@0.34.0` | K2.7 Coding | 262,144 | alternate same-provider coding architecture/second-opinion candidate |
| `moonshot/kimi-code/kimi-for-coding-highspeed/native:fixed(always-thinking)/kimi-code-cli@0.34.0` | K2.7 Coding Highspeed | 262,144 | throughput-oriented ordinary coding, iteration, and repair candidate |

Measured capabilities: all four aliases expose thinking, always-thinking, image input, and
tool use; K3, K2.7 Coding, and K2.7 Coding Highspeed also expose video input, while the
current K3-256k catalog row does not. Only K3 and K3-256k expose selectable efforts, exactly
`low|high|max`, with `high` as the current managed default. The K2.7 aliases expose no
selectable effort list; their fleet identity is therefore explicitly
`native:fixed(always-thinking)`, never the vague label `low` or `high`.

Routing ranks exact profiles, not provider names. Intra-Moonshot model diversity can improve
latency, cost, and error correlation, but it remains one `independence_class=moonshot-kimi`
and can never supply both keys of a cross-provider acceptance gate. No newly listed profile is
admitted by catalog discovery. Before routing, each profile requires its own exact-model receipt,
effective-backend verification, terminal/containment drills, current qualification expiry, and
MODEL-BENCH cells for latency, task accuracy, review catch rate, tool correctness, terminal
reliability, context consumption, and normalized cost. Until those cells exist, the table is a
qualification/routing proposal; the already-qualified K3/high evidence does not transfer to a
different alias or effort.

Primary source: Kimi Code CLI configuration/model documentation,
`https://moonshotai.github.io/kimi-code/en/configuration/config-files`.
