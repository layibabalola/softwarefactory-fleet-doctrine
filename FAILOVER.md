# FAILOVER — Claude-lane outage doctrine (fleet-wide)

**Status: RATIFIED** by the MLV-App hub (hub #32, session `9fe43dff`, fable SEQ 1294,
2026-08-09) under the operator's direct order of 2026-08-09: *"come up with a strategy for
failover... let hub review and ratify strategy first before it becomes doctrine."*
Ratification checked the draft against the three invariants in §5. Sibling projects adopt by
citing this file; project-specific amendments append below with their own ratification line.

## 1. Outage classes — name the class before choosing a response

| class | signal | expected duration | response family |
|---|---|---|---|
| **A. transient API error** | tool/API errors in an otherwise-live session | minutes | retry/wait; no board action |
| **B. 5-hour window exhaustion** | quota refusal record; lease stops renewing | until window reset | `QUOTA-DORMANT`, reroute work |
| **C. weekly cap exhaustion** | quota refusal; reset days away | days | operator decision: rotate account or idle Claude side |
| **D. account rotation** | operator-announced | ~minutes-hours | existing succession machinery (PATH A/B, confirm-dead) |

A **quota-refusal record is a stronger death signal than dormancy** for succession purposes —
but for classes B and C it is NOT death: it is a lane that will return on a known clock.
**New liveness class: `QUOTA-DORMANT(reset_eta)`** — distinct from `DARK`. No fence, no
reseat, no succession while a lane is QUOTA-DORMANT; its work reroutes or waits.

## 2. The first principle: ROLES fail over, CREDENTIALS and AUTHORITIES do not

- A Codex lane may absorb **implementation duties**. It must **never** assume a Claude seat's
  identity, lease, pen, or gate authority — credential impersonation is prohibited in every
  outage class (this restates the standing reseat-authority boundary).
- **The two-key content gate does not fail over, ever.** The review arm requires the CLAUDE
  reviewer actor by construction. During any Claude outage: implementation continues,
  handoffs QUEUE at the gate, and **nothing releases to master**. Blocking verdicts already
  posted remain in force (blocking needs no identity). A gate that admits a substitute
  reviewer under outage pressure is fail-open wearing resilience's costume.

## 3. Per-lane degraded modes (who takes over what)

- **Hub down** (Claude): Codex + Sol continue on already-dispatched cards — the queue is the
  hub's pre-authorization. No NEW adjudications, no queue mutations, no seat changes. Sol
  books state transitions (its normal duty). Recovery is a successor hub via the existing
  ignition/succession machinery; Codex does NOT deputize as hub because every hub primitive
  is seat-gated and would refuse it — correctly.
- **Claude review seat (content gate) down**: Codex proceeds to its next dispatched card;
  finished ranges queue as posted handoffs. Releases resume when a Claude reviewer seat is
  live and allowlisted. **No Codex substitution at the gate, ever** (§2).
- **Claude stage-one reviewer (opus-role) down**: the gate reviewer MAY gate without
  stage-one but must label the absence in the verdict; holding for stage-one is the default.
- **Claude implementer (sonnet-role) down**: its cards are hub-reassignable to a Codex
  implementer lane where scope permits — implementation is substitutable; review is not.
- **Codex lanes down** (the mirror case): Claude implementer absorbs implementation cards;
  the CLAUDE_IMPL handoff token already exists for exactly this. Sol-class automations have
  no Claude substitute; their duties (booking, sweeps) fall to the hub's instruments.

## 4. Scheduling and escalation

- On class B: record `QUOTA-DORMANT(reset_eta)` in the lane's health surface; wake
  instruments stand down until the eta; re-probe at eta, not before.
- Escalation ladder: at liveness threshold → reroute implementable work to the surviving
  side; at ~2h with the gate blocked and work queuing → push-notify the operator; account
  rotation (class C/D) is **operator-only, always** — no agent touches auth.
- Wake/turn-taker instruments are per-side: each side's scheduler wakes its own lanes. A
  scheduler registry can be silently emptied by an account rotation (measured 2026-08-09:
  every app-store task dead, SKILL.md files intact, zero receipts) — **wake tasks must write
  receipts on EVERY run including stand-downs**, because an absent log is indistinguishable
  from a dead task.

## 5. Ratification invariants (what any amendment must preserve)

1. **Two-key gate integrity** — no outage mode may let one side both implement and release.
2. **No credential impersonation** — duties move; identities never do.
3. **Fail-closed defaults** — a lane that cannot prove its authority refuses; queues grow
   rather than gates opening.

## 6. Ratification log

- 2026-08-09 — MLV-App hub #32 (`9fe43dff`), fable SEQ 1294: initial ratification. Reviewed
  against §5; the draft's only rejected variant was a "deputy hub" clause for Codex, removed
  because it would require either credential sharing (violates 2) or ungated writes
  (violates 3).

---

## Cloudvore adoption — RATIFIED by the Cloudvore hub, 2026-08-09 13:1x CDT

Cloudvore ADOPTS this doctrine by citation (own ratified ruling:
`review/hub-ruling-failover-0809.md`, converged independently under the same operator order;
durable copy `knowledge/failover-strategy-2026-08-09.md`). Folded back from this file:
`QUOTA-DORMANT(reset_eta)` as a liveness class distinct from DARK, and the phrasing "roles fail
over; credentials and authorities do not."

**SUPERSEDED 2026-08-09 — Cloudvore candidate-only amendment:** the former construction allowing a
Codex caretaker to bank through `MERGED` is retired. Under direct local USER authorization,
Cloudvore adopts the fleet Codex Outage Bank Mode in `RULINGS.md` by immutable citation: commit
`e7dbe21`, Git blob `53a2f9168d6ef43c39abd30aa4417393f1cb141e`, 7,369 raw blob bytes,
SHA-256 `899644E1DEF8E2283B3085F5BAEF8790E00237D1223B097D2FA0419B287C6AA6`.

Cloudvore bank workers are fresh task-scoped specialties, never standing seats. They stop at
`BANKED-CANDIDATE`, `BANKED-ADVISORY`, or `WAITING-EXACT-BYTES` and never mutate canonical refs or
lifecycle. A local activation adds an absolute read-time clock, validator-readable artifact-bound
return event, visible isolated non-null branches, exact-byte register/drain digest, fixed-path OS
file lease, and a scheduler fence. Any unproven seat/merge-capable automation blocks admission.
Safety surfaces halt; judgment, acceptance, landing, verification, closure, and release remain in
their ordinary corridors. Cloudvore hub ruling: `review/hub-ruling-codex-outage-bank-mode-0809.md`.

---

## Provider-neutral amendment — RATIFIED by the Cloudvore hub, 2026-08-09

Owner order: add MoonshotAI Kimi and generalize the Claude↔Codex failover pair into an extensible
provider pool. Cloudvore ruling: `review/hub-ruling-multi-provider-failover-0809.md`; durable local
copy: `knowledge/provider-failover-strategy-2026-08-09.md`.

This amendment **supersedes the provider-specific part** of §2 and §3: the independent content key
is no longer defined as a CLAUDE credential. Canonical acceptance requires two local role keys held
by actors from **distinct qualified provider families** (producer and reviewer/adjudicator). The
gate remains two-key and fail-closed; changing vendors cannot let one family implement and accept
its own artifact. Existing provider-specific seat allowlists remain in force until their adapters
are explicitly qualified under this contract.

Providers are runners, not authorities. Roles, leases, claims, gates, and release authority remain
local factory state; credentials remain provider-local. A successor receives a fresh actor identity
only after the prior slice is terminally fenced. The slice-boundary rule, safety HALT, owner-only
release, and candidate-only outage-bank boundaries are unchanged.

Every additional provider runner subscribes through the same PULL-DIFF-FOLD handshake before work
and records the consumed doctrine commit in its terminal receipt. Provider-derived findings may
propose doctrine amendments, but a runner never gains canonical doctrine authority and never races a
doctrine write. Only the hub-authorized publisher transaction may commit and push after the proposed
delta is independently reviewed and ratified.

Every provider registry record carries provider id, evidence-backed `independence_class` (the
inference vendor/backend trust domain), CLI/version, model/tier, allowed roles, health,
measurement/expiry, and auth/runner receipts. Two wrappers/accounts over one backend remain one
class and cannot supply both keys. Health is `READY`, `QUOTA-DORMANT(reset_eta)`,
`TRANSIENT`, `AUTH-REQUIRED`, `DOWN`, or `UNEVALUABLE`; missing/stale evidence is UNEVALUABLE.
Admission requires authenticated non-interactive inference, unbounded file/stdin prompt transport,
isolated-worktree and claim/terminal drills, containment, tier qualification, and scheduler-visible
receipts. Installation alone is not capacity. Health classifiers use structured process state and
bounded stderr, never agent transcript text.

Availability floor: two distinct qualified providers permit full producer→review flow; one permits
isolated candidate banking only; zero produces one warden notification and waits. This is the
honest “always moving” target: no single provider is a stall point and independence never fails
open.

MoonshotAI Kimi is the first staged third provider: Kimi Code CLI 0.34.0 is installed; binary, PATH,
doctor, managed K2.7/K3 catalog, and authenticated structured K3 smoke are verified. It remains
`LANE-ADAPTER-PENDING / NOT ADMITTED` until ACP/file transport, isolation, claim,
heartbeat/timeout, and terminal-receipt drills pass.
xAI Grok is staged next: official Grok Build 1.0.0, grok.com auth, `grok-4.5`, prompt-file
transport, structured output, native streaming terminal receipt, durable session artifacts, and a
portal read are locally verified. It remains `LANE-ADAPTER-PENDING / NOT ADMITTED` until foreign
compatibility is isolated, effective tools are pinned, and worktree/claim, heartbeat/timeout/health,
and seeded role drills pass. Later providers enter through the same adapter contract, never a new
authority branch.

The Grok adapter sets `GROK_HOME` explicitly, uses `--prompt-file` and
`--output-format streaming-json`, and requires both the stdout `end` event and durable
`turn_completed` update with matching identity. Registry records keep catalog alias and observed
effective backend model separately. Default Claude/Cursor compatibility, inherited foreign hooks,
and a tool inventory broader than the requested allowlist are admission failures until inspected
and disabled/pinned; interactive convenience is not provider isolation.

Provider observability follows the same abstraction. Every admitted adapter records a session id
and offers a pull-only, seatless portal over native session artifacts. A portal reports but never
classifies health, adjudicates, supplies a gate key, or becomes completion evidence. Bind local
debug viewers to loopback; vendor “visualizer” branding is not proof of read-only behavior.

Keep detailed native dashboards and attended chat relays as separate, coexisting views. Chat relays
pull and mechanically pre-filter the same durable event stream, then use the cheapest capable
low-effort narrator (currently Codex `gpt-5.4-mini`/low or Claude Haiku-class/low) to render deltas.
They never prompt a worker, forward peer reasoning to a reviewer, or become a carrier of record.
Inference tier follows authority, not volume: any relay that can steer, mutate, approve, or rule is
not a narrator and must move to a separately claimed coordinator-grade surface.

Grok portals derive percent-encoded cwd plus session id under `$GROK_HOME/sessions` and pull
`summary.json`, `updates.jsonl`, `events.jsonl`, and `chat_history.jsonl`. They exclude thought
content and relay only terminal outcomes, errors, and artifact pointers. `grok dashboard` is an
attended terminal view, not a gate or a carrier of record.

---

## AirMyPC adoption — RATIFIED by the AirMyPC hub, 2026-08-09 22:3x CT

AirMyPC adopts this file and the provider-neutral amendment by citation. Local ruling:
`.claude-state/hub-20260710/DECISIONS.md` 2026-08-09 22:3x; proposal:
`docs/fleet/PROVIDER_CONTINUITY_STRATEGY_20260809.md` (`D904BAC1…DF5627`). The project preserves the
two-key, distinct-qualified-provider, no-credential-impersonation, and fail-closed invariants.

AirMyPC measured Kimi Code CLI 0.34.0 installed and design-capable. Its first blind review found real
defects in a Codex candidate, but bounded fires did not emit a signed terminal verdict before the
known timeout/EPIPE failure. Therefore Kimi remains `LANE-ADAPTER-PENDING`, quota domain
`CANDIDATE`, and `gate-verify=WITHHELD`. It may produce banked candidates and design evidence; it
adds no canonical release capacity until a bounded ACP/file transport, terminal receipt, domain
independence, isolation, claim/lease/heartbeat, and seeded verifier drill all pass and a later local
ruling admits the adapter.

AirMyPC's stricter local rule is: a useful partial review captured before timeout is evidence for
repair, never a gate key. Missing terminal receipt is `UNEVALUABLE` and queues fail-closed.

---

## AirMyPC Grok candidate and provider-chat portal — RATIFIED 2026-08-09 23:0x CT

AirMyPC measured official xAI Grok Build 1.0.0 (`3cd0d0cbce`), valid X.AI LLC Authenticode,
SHA-256 `B238FE6B…E92585D1`, pre-existing grok.com OIDC, catalog alias `grok-4.5`, and observed backend
`grok-4.5-build`. Read-only smoke passed with no auth-file mutation. The pinned official installer
does not verify a published checksum, so the signature/hash are recorded evidence and fleet version
alignment remains open.

A bounded design audit and a fresh blind verifier demonstrated substantive review value. The verifier
completed under pinned unattended mode plus read-only sandbox, reran 24/24, bound the subject hashes,
and signed a terminal changes-required receipt. AirMyPC grants only provisional design/evidence and
unattended-execution evidence. `narrate`, `implement`, and `gate-verify` remain withheld; coordinate,
adjudicate, land, and RUN_GO remain ungranted; the xAI credential domain remains CANDIDATE. Installed
Grok adds zero canonical release capacity until the remaining adapter, portal-redaction,
quota/refusal, isolated-role, and clean verifier drills pass and a later ruling grants capabilities.

Provider chat relays are script-filtered first and narrated second. Grok relays must drop the headless
`thought` field, `chat_history.type=reasoning`, system prompts, encrypted reasoning, and raw tool
results. Default AirMyPC cadence is event-driven within 60 seconds for material transitions, changed
active digest every 10 minutes, advancing quiet heartbeat at 30 minutes, possible-stall warning at
10 minutes without advancement, completion within 60 seconds, and silence when idle/unchanged.
Narrators have zero authority. AirMyPC selects Codex `gpt-5.6-luna`/low and Claude Haiku-class/low;
this supersedes AirMyPC's earlier `gpt-5.4-mini` narrator choice because that Codex model is scheduled
to retire on 2026-08-31.

---

## AirMyPC Kimi/Grok bounded admission — RATIFIED 2026-08-10 00:2x CT

AirMyPC completed the adapter, portal-redaction, refusal, timeout, mutation, seeded-verifier and
isolated-bank drills. A 23-case shared harness passed. A direct Claude Code 2.1.220 probe returned
HTTP 429 with reset 03:20 CT while Kimi and Grok returned healthy terminal receipts, proving both are
surviving routes distinct from the current Anthropic Class-B quota domain.

Kimi Code 0.34.0 and Grok Build 1.0.0 are admitted only through AirMyPC's bounded runner for design
review, evidence audit, filtered narration and focused gate verification. Both are provisional
bank-only implementers in isolated claimed workspaces. Kimi review tools are read/glob/grep only;
Grok is pinned to unattended mode plus read-only sandbox and focused prompts. Neither provider can
coordinate, adjudicate, land, issue a release exception or `RUN_GO`, and neither expands the five
functional lane roster.

The router requires `HEALTHY` capacity plus an explicitly `ADMITTED` capability. Each failover run
gets a fresh id, exact subject hash, non-author/recusal proof, deadline, mutation sentinel and exactly
one terminal receipt. Missing/malformed/partial/timed-out/nonzero/multiply signed output remains
UNEVALUABLE. A later success never launders an earlier partial run.

The portal filter mechanically drops private reasoning, prompts and raw tool bodies before display
or optional narration. Mechanical refresh is 30 seconds; human-facing cadence remains material event
within 60 seconds, changed-state digest at 10 minutes, advancing heartbeat at 30 minutes only without
a milestone, possible-stall at 10 minutes without progress, completion within 60 seconds and silence
while idle. Portal and narrator remain seatless and zero-authority.

---

## Cloudvore provider-neutral ordinary implementation — RATIFIED 2026-08-10 01:5x CT

This section supersedes the bounded-admission section's isolated-bank-only implementation limit.
Claude is optional capacity, not a prerequisite, for ordinary implementation or ordinary hub
operation. Kimi Code 0.34.0 and Grok Build 1.0.0 carry the explicit capability
`ordinary-implementation=ADMITTED`; Kimi/Grok still carry no hub, adjudication, landing, push,
release, lifecycle-credit, `RUN_GO`, or bar-launch authority.

Dispatch separately proves fresh health `READY` and the exact capability, plus frozen charter,
fresh actor, clean linked worktree, mechanically matching uncontested project claim, and closed path
set. The scheduler rejects extra changed paths and owns every test, mutation, admission run, and bar;
provider producer profiles expose bounded edit but no general shell/terminal.

Acceptance requires a durable review of the exact producer head/diff by a qualified reviewer with a
distinct evidence-backed `independence_class`. A hub adjudicator is not the accepting reviewer and
never supplies the second key. Without the independent reviewer, the candidate stays isolated and
unlanded. Only an owner-authorized coordinator-grade Codex or Claude surface may hold the ordinary
hub lease and true-merge; only its named bar-lease holder may start the merged-master bar. Live bars
block duplicates; every red or non-terminal result restores exact prior master.

Qualification evidence is Cloudvore candidate `7589acc`: live Kimi/Grok producer READY receipts,
closed path sets, scheduler-owned Full adapter pin batches (27/27 and 21/21), reciprocal
cross-provider candidate reviews PASS, and final blind policy reviews PASS from both independence
classes. Claude may re-enter after fresh health/capability/claim derivation; its return does not
invalidate healthy provider work.

### Forward correction — effective inventory outranks compatibility settings

Conjugal independently reproduced, and Cloudvore's own retained producer receipt confirms, that
Grok Build 1.0.0 can report compatibility settings disabled while still enumerating active
Claude-origin hooks and enabled Claude-path plugins. Therefore the Grok ordinary-implementation
capability above is `SUSPENDED / NOT_ADMITTED / ZERO-KEY` until the complete effective inventory is
clean under an inventory-aware gate. Disabled settings, environment overrides, an empty parsed
compatibility snapshot, successful inference, or a later clean focused run cannot establish that
claim.

A Grok preflight must fail `UNVERIFIED` on an unknown/incomplete inspect schema and must enumerate
all active instructions, hooks, plugins, marketplaces, skills, agents, and MCPs. Any active foreign
provenance refuses launch. A clean result is necessary but still requires the normal fresh health,
capability, claim, containment, scheduler-owned tests, and independent-review gates. Kimi evidence
whose accepting independence key came from the suspended Grok profile remains isolated and unlanded
until a fresh qualified distinct reviewer replaces that key.

### Forward restoration — Grok through an unprivileged WSL boundary

Cloudvore restores Grok Build 1.0.0 capability admission only through the reviewed
`Invoke-GrokWslBoundary.ps1` path represented by candidate `d808607`. Native Windows Grok under a
Windows user profile shared with Claude remains `SUSPENDED / NOT_ADMITTED / ZERO-KEY`; TOML
compatibility settings cannot repair that boundary by themselves.

Each admitted host runs the recorded Linux binary as a dedicated non-root WSL user with a clean
Linux home and records the distribution release, nonzero UID, binary SHA-256, TOML SHA-256,
and clean same-runtime inspect/plugin receipts without reading credential contents. The gate
enumerates instructions, hooks, plugins, marketplaces, skills, agents, MCPs, LSPs, and permission
sources. Unknown provenance or any foreign provenance refuses before claim even when the item says
disabled; compatibility false cells must be unique real booleans sourced from the adapter env.

Review remains `dontAsk` plus read-only tools. A headless producer uses `auto` only with the exact
bounded edit allowlist and static terminal/web/agent/LSP denylist; interactive `acceptEdits` is not
an unattended policy, and always-approve/yolo/bypass modes remain forbidden. Scheduler authority
still owns tests, path containment, Git, admission, merge, rollback, and bars. Grok regains ordinary
implementation and independent-review keys, but no hub, adjudication, landing, push, release,
`RUN_GO`, or bar-launch authority.

Kimi review/implementation dispatch also requires the worktree-bound pointer contract at Cloudvore
candidate `d4ec0da`: the argv pointer names both the charter and exact scheduler-validated linked
worktree and forbids deriving repository root from the charter location. Transport success from a
different checkout is adjudication-denied. Final evidence is recorded in `RECEIPTS.md` and the
forward restoration ruling in `RULINGS.md`.

### Forward clarification — identity isolation is not filesystem hermeticity

The certified WSL route is identity-isolated and runtime-inventory-gated, not filesystem-hermetic.
On the measured Ubuntu host, DrvFs mounted `/mnt/c` read/write, the `grok` UID could read the Windows
`.claude` directory, and Windows paths were appended to `PATH`; `/etc/wsl.conf` enabled systemd but
did not disable automount or interop. The wrapper intentionally exposes the Windows Grok home plus
the assigned prompt/worktree. A clean `/home/grok` prevents automatic Linux-home inheritance but
does not make Windows profile paths unreachable.

Admission therefore relies on the previously ruled detection-and-credit-denial model: same-runtime
effective-inventory inspection, empty effective plugin resolution, closed tools and paths, durable
terminal correlation, scheduler containment, independent review, and rollback. Any observed foreign
inventory or boundary uncertainty refuses before claim and supplies zero key. Consumers must not
describe this route as a mandatory mount sandbox. Filesystem-hermetic status requires a separately
qualified mount namespace/container exposing only named paths.

The recorded binary SHA-256 identifies exactly what ran; it is not a vendor signature or published
checksum comparison. xAI documents its `x.ai/cli/install.sh` distribution route but no matching
published checksum/signature chain was reproduced in this qualification. Receipts bind the candidate
hash, generated/observed session, streaming terminal, fresh durable completion, runtime inventory,
and credential-free fingerprints; session IDs alone are opaque labels and confer no authority.

`wsl --install --no-distribution` is components-only and supplies no Linux userland or provider
capacity. Debian must be selected explicitly. Debian 13.5 is now a separately qualified host cell
under the same non-hermetic detection-and-credit-denial model: dedicated locked `grok` UID 1000,
the same recorded Grok 1.0.0 binary fingerprint as Ubuntu, clean same-runtime inventory with zero
effective plugins, credited reviewer and bounded-producer drills, three identical scheduler-owned
45/45 pin runs, and exact-worktree Moonshot Kimi review all passed. Candidate `19cbb7a` documents
this host cell; qualification does not make other distributions inherit a key or broaden Grok's
authority.

## Healthy provider-profile rotation after project-local admission

Provider diversity is normal evidence gathering, not only outage recovery, but it remains subordinate
to project-local capability and authority. Health and capability are independent predicates: a
healthy profile without a fresh admitted role cell is ineligible, and an admitted role cell with
stale or non-ready health is also ineligible.

Rotation occurs only at a new slice boundary from an already hub-authorized frozen manifest. It
selects an eligible exact profile for an existing functional role and creates no standing seat. A
controller constitutes a fresh project-local actor bound to the exact worktree; that actor emits its
own claim before provider inference. No scheduler or adapter impersonates the actor, and no provider
runner receives lifecycle, hub, merge, bar, rollback, push, release, or owner authority.

Eligibility binds project, provider, observed effective backend/model, requested effort,
observed-or-null effective effort, transport, exact project-adapter manifest, host boundary, role,
expiry, and independence class. Catalog effort is not effective-effort evidence. Ubuntu and Debian
Grok routes remain distinct host cells; native Windows Grok in a Claude-shared profile remains
zero-key. Same-provider models and same-provider host cells never supply both acceptance keys.

The selector is read-only until separately admitted. It filters health and capability, preserves the
two-class gate, emits an exact reason/expiry/next-probe plan, and revalidates immediately before any
future launch. It never invents or reprioritizes work, creates a charter, requeues, transfers a live
claim, or performs mid-slice succession. A health loss permits termination only of the exact captured
actor/process tree under existing authority with first-red evidence preserved; the hub applies the
existing succession procedure.

Returning Claude capacity is considered only for later new slices and never preempts healthy work.
Canonical Fable debt retains its named authority route and cannot be discharged by Kimi/Grok shadow
review. Profile promotion, project adoption, dispatch, and watcher activation each require later
exact-evidence rulings; this protocol alone changes no live routing.

### Forward hardening: evidence rotation is fail-closed at both ends

Healthy rotation may explore only fresh exact role cells after project-local admission. Historical
admission, catalog discovery, an alias label, and provider availability do not establish benchmark
fitness. Null or unproved effective effort supplies zero qualification credit.

Before selecting a producer, the planner must prove a fresh, healthy, admitted, bookable
acceptance-key reviewer from a different independence class for the slice deadline. It must prove
that fact again immediately before launch. If either proof fails, record
`NO_INDEPENDENT_REVIEWER` and dispatch nothing; do not weaken the acceptance topology to consume
capacity.

Exploration starts a new bounded epoch when the eligible set, frozen control, or evidence version
changes. Outside that epoch, a preferred profile exists only under the ratified deterministic
Pareto rule; non-dominating profiles remain least-sampled-first. Provider recovery adds capacity at
a later slice boundary and never preempts live work or transfers a claim.

Coordination corruption degrades only the dependent transition when its exact scope is known.
Quarantine first-red bytes, notify the owner/hub once and on material change, keep missing evidence
non-green, and allow independently eligible slices to advance. Automated recovery remains
plan/KEEP unless a unique syntactic repair matches its preimage; ambiguous lifecycle meaning and
all authority-bearing transitions remain human/hub adjudications.

## AirMyPC — dual-primary blackout continuity, design-stage ceiling

**RATIFIED-DESIGN / UNACTIVATED / UNDRILLED / NOT-FOR-ADOPTION.** AirMyPC exact local subject
`6F240547308FB42C52B4DF8017A0BECB5DDF9587CDE7E1CE4065BEFBCF7E1298` / 39,797 B proposes a
deterministic warden over pre-ratified capsules, two distinct auxiliary provider keys, and a maximum
unattended `blackout/<machine-id>/<epoch>` ref. It never permits `master`, release, doctrine, live
hardware, or primary-hub decisions, and every integrated card remains subject to 100% returning-
primary content review before ordinary landing.

The design treats provider capacity, local launch governance, and runtime authority as separate
facts. A recovery canary refused before launch is typed
`CANARY_NOT_LAUNCHED_LOCAL_GOVERNOR`, remains sealed, grants no provider-failure or availability
credit, and cannot bypass the existing scheduler/burn-cap floor. Filesystem/UNC remotes require a
proved independently administered ACL split or a server-mediated endpoint; a warden-writable local
hook earns zero protection credit.

This block is a pointer and limit statement, not an executable state machine. It grants no capsule,
role cell, provider key, controller, task, queue, credential, ref, landing, release, or `RUN_GO`
authority. Sibling disposition defaults to `DISTINGUISH(PENDING_DRILLS)` until separately reviewed
implementation, drill, and activation evidence exists.

## AirMyPC — semantic liveness is required in addition to freshness

**A fresh receipt is not component health.** A watchdog must validate an explicitly allowed semantic
status/reason pair. Expected contention must be distinguished from broken lock or storage
infrastructure. Active work must prove advancement or a bound terminal/failure state; an
intentionally idle controller must emit an explicitly allowed idle state. Unknown statuses, unknown
reasons, and mismatched pairs default-deny.

AirMyPC earned this rule through exact B-v7 repair plus bounded operation. Its 105/105 controlled
suite rejects the predecessor's status-laundering and broken-lock counterexamples while preserving
all seven legitimate pairs. The installed controller then emitted scheduler-bound
`QUIET / no-new-authorized-job`; the watchdog emitted `HEALTHY / health-receipt-fresh`, restart false;
both task results were zero; and the exact queue remained zero jobs. That live evidence proves the
scheduler/task/proof/idle-receipt path only. It does not claim that a provider job progressed; active-
work negative and terminal behavior remains controlled evidence.

Sibling request `airmypc-semantic-liveness-20260811` asks for **ADOPT(reference)** or
**DISTINGUISH(reason)** under each project's own status vocabulary and authority. This law grants no
watcher, task, provider, queue, credential, launch, ref, merge, release, hardware, or `RUN_GO`
authority.

## AirMyPC — structured capacity recovery is a paired-run transaction

A cadence cap may retain ordinary outage backoff while allowing one bounded recovery canary only
from a fresh, pinned, same-quota-domain productive observation newer than the latest paired quota
block. Every credit-bearing observation joins exactly one valid ignition to exactly one terminal
with identical run ID, seat, requested model, quota domain, recovery-canary bit, and producer hash;
the terminal must not predate ignition, and the run-ID seat suffix must agree. Missing, duplicate,
conflicting, cross-seat, stale, wrong-domain, wrong-producer, or time-reversed evidence grants no
quota, recovery, model, or epoch credit.

The valid canary ignition spends the single recovery allowance immediately, including while its
terminal is pending. Missing, failed, or unverified terminal evidence therefore reseals the floor;
only the matching productive canary terminal starts a new cadence epoch. Dispatch intent and raw
provider stdout or assistant prose supply zero burn, model, or recovery credit.

Sibling request `airmypc-structured-recovery-canary-20260811` asks each project to
**ADOPT(reference)** or **DISTINGUISH(reason)** under its own cadence, schema, producer, and authority
map. This rule grants no canary, provider launch, task, queue, credential, ref, activation, release,
hardware, or `RUN_GO` authority.

## AirMyPC — structured failure recovery is a durable transaction

An automatic recovery action requires a versioned, typed failure fingerprint and trusted recurrence
history. The history binds its exact path and task identity; validates schema and fingerprint
versions, admitted statuses, exact scalar types, bounded nonnegative counts, and coherent transition
flags; and uses a durable initialization marker to distinguish a genuine first run from missing
history after initialization. Malformed, contradictory, identity-drifted, missing-after-
initialization, negative, oversized, or unresolved-claim history becomes `REVIEW_REQUIRED` and
performs no recovery action.

The transaction order is **claim → action → seal**. Before the action, write, flush, reread, and
verify a `SELF_HEAL_CLAIMED` row for the exact fingerprint. Perform at most one bounded action, then
seal success as `SELF_HEAL_REQUESTED` or failure as `ALARM`. If the action or seal is interrupted,
the durable claim prevents another automatic attempt; the next observer quarantines the incomplete
claim. A later healthy closed-semantic receipt may reset recurrence state, but the same deterministic
failure after one action is quarantined. Reviewed controller or watchdog byte drift never self-repins.

Sibling request `airmypc-structured-failure-quarantine-20260811` asks each project to
**ADOPT(reference)** or **DISTINGUISH(reason)** with its own schema, fingerprint, action, health
matrix, and authority boundary. This law grants no task install, restart, provider launch, queue
mutation, credential, ref, activation, release, hardware, or `RUN_GO` authority.
