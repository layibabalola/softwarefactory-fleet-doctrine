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
xAI Grok and later providers enter through the same adapter contract, never a new authority branch.
