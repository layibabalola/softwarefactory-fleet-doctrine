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

## Fleet provider-capacity governor disposition — 2026-08-18

`DISTINGUISH(224a6705d81dfbc670313cdcef4d825216f2b380, PENDING_P0_LAUNCH_CONTRACTS)`

Rollout state: **SHADOW**; automatic launch gate: **HARD_CLOSED.** Agent Bridge
adopts the portable governor's invariants as the target universal contract, but
does not activate the current project adapter.
The project-specific launch seams below remain P0 admission gates. This disposition
creates no provider call, scheduled-task enablement, routing, review, campaign,
landing, production, or release authority.

### Universal invariants retained

- All Fable, Opus, and Sonnet lanes using the same Claude account are one quota
  domain unless independently measured evidence proves otherwise. At most one
  unattended inference-bearing root may run in that domain.
- A reset, recovered probe, provider status, timer, or telemetry change never
  opens the gate by itself. Capacity observations are diagnostic inputs with zero
  authorization weight.
- The exact role, provider, model, effort, subject, and independence class remain
  bound. Exhaustion may stop or defer work but may not silently downgrade them.
- A deterministic addressed-work check must return without inference when no new
  work exists. Model calls receive bounded evidence capsules: current state,
  addressed WAL records, frozen hashes and rulings, focused diff/test evidence,
  and content-addressed pointers instead of broad history.
- Turns and elapsed time are bounded. Budget exhaustion produces WIP or a
  checkpoint, never PASS. Stable context is reused; large evidence is spilled by
  hash and path; health, heartbeat, status, and receipt formatting remain
  deterministic and model-free.
- Remote labels remain untrusted, mutations require local confirmation, and remote
  messages remain requests rather than commands.

### Agent Bridge serialized Claude order

1. FABLE may perform the first bounded coordination/hub canary only after every P0
   gate below closes.
2. OPUS may start only after FABLE reaches a terminal state and the exact frozen
   review subject is available.
3. SONNET may start only after the preceding lane is terminal and the exact
   addressed implementation subject is available.
4. FABLE, OPUS, and SONNET may not run concurrently on the shared account unless a
   later ratified receipt proves separate quota domains.

### P0 activation gates

- Make admission, reservation, final recovery revalidation, frozen-subject
  revalidation, executable resolution, and suspended-child resume one atomic
  launch transaction under the quota-domain lock.
- Bind and verify the resolved executable path and SHA-256, complete argv, working
  directory, security-relevant environment, and actual resumed image. A basename
  or wrapper-command hash alone is insufficient.
- Require policy-declared capacity fields and dimensions. Missing or stale evidence
  fails closed; unknown usage is never replaced by an invented zero.
- Install an authoritative model-free operational observer and an adoption surface
  that show the current domain state, reservation, owner, expiry, recovery proof,
  and last terminal outcome.
- Eliminate capsule and exact-subject check/use races, including write/delete
  replacement while an authority-bearing review is in flight.
- Inventory the complete scheduled-task, watcher, bootstrap, retry, and manual
  launcher graph and route every inference-bearing path through the same admission
  point. Any bypass keeps the domain hard-closed.
- Run one bounded FABLE canary that deterministically returns to HARD_CLOSED on
  success, timeout, refusal, or failure. Then obtain fresh independent security and
  quality reviews over the exact landed subject.

### Current evidence and limits

The legacy Agent Bridge Warden scheduled task is disabled and a point-in-time
census found no unattended Claude CLI root. Direct, one-turn diagnostic requests
reached the exact configured Fable, Sonnet, and Opus models; their deliberately low
cost ceilings terminated the probes. Those observations establish provider
reachability only and are not a governed canary or admission receipt.

The project candidate's pre-remediation focused suite had 64 passing tests, while
two independent reviews each scored it 64/100 and NO-GO. Remediation subject
`13d697c2b778ed566ebb90147aca77bd28f80824` is now committed and backed up: 71
focused governor tests and lint pass, and a standalone clone passes all 471 legacy
tests plus 37 subtests. It adds locked and pre-resume recovery revalidation,
resolved executable/path/SHA and actual-image binding, complete argv/cwd/environment
launch-context binding, policy-required capacity evidence, mandatory Windows
exact-subject handles, and a zero-inference status surface. It has not yet received
fresh independent review or a complete host launcher-inventory proof. Existing
Claude boot payloads already use addressed WAL reads, an approximately 48 KiB
orientation bound, hash carriers, self-derivation, and named unread evidence; that
is partial token-efficiency conformance, not proof of the full capsule contract.
Until every remaining P0 gate and fresh review closes, the legacy Warden remains
disabled and all Claude restoration authority remains closed.

### Reconciliation with active fleet candidates

The precedence rule is singular and fail-closed:

1. The accepted subject `224a6705d81dfbc670313cdcef4d825216f2b380`
   remains the only portable normative provider-capacity contract until a later
   exact subject is independently reviewed, distinctly adjudicated, recorded in
   `RULINGS.md`, and merged to canonical master.
2. Fleet PR #10 R14 subject `874605e43531c9aa230ee16851f8107a8e0d9cec`
   is a proposed additive successor and zero-authority conformance workbench. Its
   hosted matrix is evidence, not law. Agent Bridge neither rejects it nor adopts
   it before the required ruling and canonical merge.
3. Agent Bridge subject `13d697c2b778ed566ebb90147aca77bd28f80824`
   is project-local runtime evidence, not a competing universal doctrine. The
   Conjugal runtime-extension draft and every other project adapter have the same
   status: useful comparative evidence only. Project dispositions from Adobe,
   Cloudvore, Conjugal, DNG, and other factories describe local adoption state and
   cannot override the portable core or grant Agent Bridge authority.

R14 is strictly stronger than the current Agent Bridge candidate in several
material respects: strict schema/HMAC-qualified capacity and health records;
persistent claimant/reservation fencing; exact four-surface launcher census;
single-use canary authorization; 1,000 unchanged zero-inference ticks; and retained
artifact/publication ownership with cleanup poison. Agent Bridge therefore proposes
to consume a ratified R14 descendant rather than fork those semantics. Until that
happens, its local subject may advance only closed-state installation, shadow, and
containment evidence under the accepted v1 invariants. It cannot reach CANARY from
local tests alone.

If R14 or a descendant is ratified, Agent Bridge must publish a new exact disposition
against that canonical commit and profile hash. No branch head, hosted-green run,
provider recovery, or successful local probe silently updates this disposition.

### Fail-closed restoration progress

Agent Bridge installed its local governor from exact subject
`13d697c2b778ed566ebb90147aca77bd28f80824` into a versioned host-local directory.
The policy semantic SHA-256 is
`7E3B329544EA167C37B229576CB1787F96A521490DFEF7D5B5CD86AF62761DEE`.
It binds Claude Code `2.1.220` past the npm shim to the native executable SHA-256
`AF5BF1F1B2AADFFC768ECCD787084C6FDF9BA81624CBE96C1C6D9AC1A1550231`,
requires five-hour and weekly capacity plus reset time, admits at most one
unattended root, and requires a recovery attestation that is absent.

The model-free `AgentBridgeClaudeGovernorShadow` Scheduled Task is enabled on a
five-minute cadence. Twelve observed shadow iterations, including scheduled-path
execution, returned `HARD_CLOSED`, `recovery=MISSING`, no native Claude CLI root,
zero provider calls, and zero input/cache/reasoning/output tokens. The legacy
Warden and lifecycle supervisor remain disabled. The installation manifest,
incomplete inventory, and local receipt have SHA-256 values
`00F4025AEF9F35874DDD878DDD31014D3299187B38D9DBC3F0EF06FD219DB98C`,
`97543548F6DA914781A324A190F08609D2FB4D16B88378A40E5BD900A9739B8E`,
and `96F591B3CA59E8FA4CC15AFCB4094EA57A1D672E4E574A5E062827F85DA6004E`.

This advances only offline installation and SHADOW evidence. The launcher census
is explicitly incomplete, no qualified capacity observer or recovery attestation
exists, and no canary is authorized.
