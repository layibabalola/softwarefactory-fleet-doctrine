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

## Repair-learning loop — local workflow; fleet adoption proposed (2026-08-11)

Agent Bridge now treats every material repair as two deliverables: restored local
operation and a portable fleet-learning package. The local sequence is preserve and
classify, contain duplicate execution/authority races, restore the live path, reproduce
the fix on a clean exact candidate, prove the real recovery path, add executable
recurrence controls, classify the fleet seam, export measurements, and record the
doctrine commit or pending proposal key at closeout.

Tracked local contract: Agent Bridge commit
`0623a2c8b0f72661bd05ee8ea3b976be467815bc`,
`docs/internal/FLEET_REPAIR_LEARNING_LOOP.md`. The board bootstrap copy is
`coordination/resume/B8-doctrine-duty.md`, SHA-256
`665C86AF3E41BE4F0FD4857F4A46C7C9AAB6646901E40FED80D154B6252911BB`.

The recovery proof must exercise the actual mechanism: configuration text is not
liveness; scheduled systems need a genuine later scheduled run, provider failover needs
both outage and recovery/stand-down arms, and session succession needs a conformant claim,
typed seat ruling, persisted route, and a genuine successor turn before retirement.
Every recurrence control names bounded retry, deduplication, timeout,
rollback/stand-down, and escalation behavior.

Portable outputs are classified mechanically as `TRAP`, `RECEIPT`, `PROPOSAL`, or
`NO-EXPORT`. Attributed measurements and reproducible traps travel immediately. Strategy
and law remain exact-hash proposals until independent review and hub ratification; this
section is a project-spec disclosure and grants no fleet ruling, provider authority,
review key, billing act, landing, or protected-invariant exception. Sibling factories may
borrow the mechanism as DATA and must adopt-or-distinguish it locally.

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

## Kimi provider-parity strategy — operator-relayed research candidate (2026-08-10)

Status: **PROPOSED STRATEGY, NOT ADMISSION, ROUTING, OR DOCTRINE RULING.** The
operator relayed a fresh cross-machine Fable survey of Moonshot's wider API model
ladder. Its market specifications and prices are planning inputs only until a local
catalog/API discovery and an exact-profile admission drill reproduce them. In
particular, an API product name is not assumed equivalent to a Kimi Code managed
alias.

The reported planning ladder is:

| reported API identity | reported character | proposed fleet use after admission |
|---|---|---|
| `kimi-k3` | flagship/high-inference, long-context reasoning | hard adjudication, hub planning, or verifier escalation |
| `kimi-k2.7-code` and its high-speed variant | coding-tuned, thinking-enabled | primary implementation, repair, and code-heavy review |
| `kimi-k2.6` | general mid-tier | broad adversarial reading and medium-inference review |
| `kimi-k2.5` | lowest-cost listed tier | mechanical transforms, bounded bulk work, and low-risk maintenance |

The survey reported provisional input/output prices per million tokens of `$3/$15`
for K3, `$0.95/$4` for K2.7-Code and K2.6, and `$0.60/$3` for K2.5. These values
MUST be re-read from an authoritative current billing/catalog surface at each cost
benchmark; they never enter an admission receipt by citation alone.

### Identity seam that must stay explicit

- The local managed CLI catalog exposes `kimi-code/k3` and
  `kimi-code/kimi-for-coding`, whereas the survey names API identities `kimi-k3`
  and `kimi-k2.7-code`. The adapter must record the requested identity, effective
  backend, transport (`managed CLI` versus `API`), effort/thinking mode, and adapter
  version. Name similarity, display labels, and pricing pages never prove alias
  equivalence. Neither K2.6 nor K2.5 appeared in the measured local managed catalog;
  their availability and exact API identifiers remain unverified on this machine.
- The current provider-onboarding candidate pins only `kimi-code/k3`; every
  qualification record deliberately carries empty role cells. K3 transport success
  therefore admits neither K3 nor any sibling model to a fleet role.
- Adding K2.7-Code, K2.6, or K2.5 is a separate post-landing candidate. It must not
  alter the frozen K3 onboarding subject and invalidate already-bound review votes.

### Parity program for fleet proposals

1. **Registry parity:** create one immutable profile row per exact
   `provider/model/effort/adapter@version` and transport. Pin context, modalities,
   tool support, effective backend, discovery time, expiry, and
   `independence_class=moonshot-kimi`. No sibling or effort inherits another row.
2. **Capability parity:** benchmark each candidate against the acts actually carried
   by the Claude lanes: hub/roadmap adjudication, falsification-first verification,
   implementation, guard/review work, and narration/mechanical maintenance. A model
   is admitted to named acts, never to a vague provider-wide tier.
3. **Evidence parity:** require terminal and refusal receipts, same-session resume,
   workspace read/write containment, tool correctness, effective-model proof,
   timeout/process-tree cleanup, seeded-defect catch controls, context consumption,
   latency, and normalized cost. Authority-bearing cells additionally require an
   immutable reproduction by a qualified different provider family.
4. **Role-cell parity:** grant short-expiry role cells separately. The initial
   strategy candidate is K3 high/max for one high-authority or high-verification role,
   K2.7-Code for implementation, K2.6 for general review, and K2.5 for mechanical
   work. Benchmarks may overturn the pairing; labels may not.
5. **Independence parity:** every Kimi tier remains one Moonshot provider-family key.
   K3, K2.7, K2.6, and K2.5 may provide useful intra-family diversity, but they can
   never author, independently clear, and finally adjudicate the same canonical
   object without a non-Moonshot arm.
6. **Failover parity:** Kimi may take over Claude-shaped workload capacity after the
   relevant cells are admitted, but never all independent governance keys. Every
   failover plan must name the surviving non-Moonshot reviewer/adjudicator, the
   seat-transition mechanism, expiry, and the exact work that remains bank-only.

Proposed sequencing: finish and land the frozen K3 onboarding candidate unchanged;
freshly qualify and admit its exact K3 profiles; then open a separate model-ladder
candidate for K2.7-Code, K2.6, and K2.5. Until then, the wider ladder is a strategy
input and may generate benchmark/admission proposals, but supplies zero routing
capacity and zero independence keys.

Research pointers relayed by the operator (non-authoritative until reproduced):
Kimi platform K2.7-Code quickstart
`https://platform.kimi.ai/docs/guide/kimi-k2-7-code-quickstart`; Codersera K3 guide
`https://codersera.com/blog/kimi-k3-complete-guide-2026/`; Morph model/pricing list
`https://www.morphllm.com/kimi-api`; NxCode K2.5/K3 pricing report
`https://www.nxcode.io/resources/news/kimi-k2-5-pricing-plans-api-costs-2026`;
MarkTechPost K2.7-Code release report
`https://www.marktechpost.com/2026/06/12/moonshot-ai-releases-kimi-k2-7-code-a-coding-model-reporting-21-8-on-kimi-code-bench-v2-over-k2-6/`;
and Lorphic K2 model overview `https://lorphic.com/kimi-k2-models/`.
