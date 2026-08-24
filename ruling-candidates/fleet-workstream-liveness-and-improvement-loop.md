# Fleet workstream liveness and autonomous improvement loop (R1 candidate)

> **STATUS: CANDIDATE / ZERO AUTHORITY.** This document proposes portable doctrine.
> It does not enable a scheduler, create or resume a provider session, grant path or
> release authority, change a project queue, or declare any workstream healthy.

## Problem

Multi-lane factories can look healthy while doing no inference or product work. A
heartbeat writer may keep stamping after its owning inference turn has ended; a
queue can contain valid work without an authorized owner; and multiple lane labels
may secretly share one provider, model, account, or launcher failure domain. These
states turn visible activity into false liveness and make "fail over" mean "retry
the same outage under another name."

The opposite failure is passive correctness: every lane waits safely at a gate,
but nobody repeatedly asks which bounded action can improve the system without
crossing that gate. The factory remains fail-closed and unproductive indefinitely.

## Proposed contract

### 1. Health is a vector, not a color

Each workstream reports these axes separately:

- **owner continuity**: the exact owner/session is current and unambiguous;
- **inference liveness**: the owner has produced a completed or in-flight inference
  signal inside the declared window;
- **instrument liveness**: watchers, heartbeat writers, and schedulers are running;
- **admission**: required capacity, disk, policy, and external platform gates pass;
- **execution authority**: the exact task, paths, base, reviewer, prerequisites, and
  stop conditions have a current grant;
- **evidence freshness**: the decision is bound to current immutable inputs and has
  not been superseded.

`instrument liveness` never proves `inference liveness`. A fresh watcher heartbeat
with a completed or absent owner turn is `INSTRUMENT_LIVE_OWNER_IDLE_OR_DARK`, not
healthy. A workstream is healthy only for the next named action whose required axes
are all satisfied.

### 2. Classify failure domains before failover

Provider label, lane label, and model nickname are not independence. Every route
records an opaque failure-domain tuple covering the actual provider family, account
or quota domain, model endpoint, launcher/harness, host, and relevant credential
path. Raw identities remain project-local.

Context overflow, provider quota, authentication failure, transport failure,
process death, and policy refusal are distinct typed outcomes. A context-overflow
receipt must not become quota evidence. Re-routing between two labels with the same
failure-domain tuple is a retry, not failover, and must retain the original adverse
history and retry budget.

### 3. One immutable ingress, exactly one adjudication

Cross-lane work enters through one immutable receipt containing a stable request id,
source task, requested owner, artifact hashes, scope, prerequisites, and forbidden
effects. The receiver independently verifies the receipt and bound artifacts before
acting.

If the registered owner session exists but is idle, the coordinator resumes that
exact session and routes the existing receipt. It does not create a second nudge,
seat, task, queue card, intent, heartbeat, or authority. Concurrent delivery of the
same request id is idempotent. The terminal result is exactly one durable `BEGIN` or
one durable `REFUSAL`, each naming the request id and current evidence tuple.

`BEGIN` must bind the exact task, canonical base, clean worktree/branch, path scope,
cross-lane ownership handling, reviewer, prerequisite receipts, and stop conditions.
`REFUSAL` must name every missing or stale prerequisite and the smallest observable
state change that permits reconsideration. Neither result may infer implementation,
publication, release, deletion, or policy authority that the receipt did not carry.

### 4. A bounded recurring improvement loop

Every active factory root runs a local, model-free evaluation on a bounded cadence
(30 minutes is the recommended default) and on material state-change events. The
cadence is for local re-evaluation; doctrine publication remains event-driven at a
reviewed landing seam.

Each cycle asks, in order:

1. What useful outcome can each workstream lawfully advance now?
2. What exact external or internal fact blocks each stopped workstream?
3. Which single safe action has the highest expected unblock value?
4. Can that action be executed now without duplicating ownership or weakening a
   gate?

The cycle executes at most one state-changing action, then re-derives health from
authoritative bytes. Useful actions include renewing an exact owner, routing an
already-authorized ingress, producing a missing review/evidence packet, running a
bounded diagnostic, or retiring a proven duplicate. Repeating an unchanged audit,
renaming a lane, or writing another request for the same work does not count as
progress.

Every due cycle atomically persists one closed-key advancement record before it can
claim progress. The record binds the authoritative input identities, baseline,
largest observed failure, selected action or `HOLD`, verifier/evaluation result,
before/after score delta, and next candidate. A timestamp change, heartbeat, packet
refresh, repeated census, or unchanged successful test has zero score value unless
it changes one of those bound facts. `HOLD` is a safety verdict, not progress.

Two consecutive due records with the same largest failure and the same `HOLD`
reason trigger a bounded root-cause pass. That pass must either repair the control
loop forward-only, select one independently safe backlog action, or persist why no
such action is authorized. Projects may choose another small bounded threshold only
with a dated rationale and a negative test proving that the threshold cannot turn
repeated blockage into authority. The trigger never permits a provider launch,
ownership transfer, review bypass, production mutation, or release.

The assessment cadence and the operational heartbeat cadence are separate controls.
A fast heartbeat may preserve instruments and still fail advancement liveness; a due
assessment may therefore be required even when every watcher is fresh. Exact cadence,
storage, scoring, and notification thresholds remain project-local.

The loop is quiet when authoritative state is unchanged. It emits a user-facing
update when health changes, a new blocker appears, an action is taken, authority is
needed, or a deadline is at risk. The loop never converts repeated blockage into
permission.

### 4.1. Falsification comes before repetition

At least once per 30-minute window, and immediately after a material blocker or
provider result, the root asks a second-order question before repeating the prior
disposition:

> Which belief, blocker, or procedure may now be stale or incomplete; what
> independent evidence could falsify it; and what safe improvement can be made now?

The review must correlate independent surfaces rather than promote one observation
into a system-wide conclusion. Relevant surfaces include account identity and plan
entitlement, endpoint or session availability, authentication method and credential
source, active process ancestry and concurrency, launcher and bridge versions,
watcher/Monitor binding, proposal-bound process receipts, governance state, and the
actual workstream owner turn. Sensitive raw identities remain project-local; fleet
doctrine carries only typed outcomes and opaque failure-domain references.

Conflicting signals are useful evidence, not permission to choose the most
convenient story. For example, an interactive plan meter showing allowance plus a
noninteractive process returning a session error is
`PLAN_ALLOWANCE_PRESENT_SESSION_PATH_UNAVAILABLE_OR_UNKNOWN`. It is not proof of
global quota exhaustion, account mismatch, or provider health. Likewise, a missing
or misbound bridge Monitor is a reachability defect, not evidence that the account
lacks capacity. The root narrows the cause only as far as retained evidence permits.

Every material observation records its source, observation time, account/failure-
domain binding where safe, and freshness window. Before declaring an unchanged
blocker, the loop refreshes the cheapest independent facts that could invalidate it.
`DONT_NOTIFY` or an equivalent quiet result is lawful only after that falsification
check finds no changed evidence, no newly satisfiable gate, and no higher-value safe
action.

Read-only diagnostics, reversible local repairs, and actions already covered by
current authority should proceed without owner relay. A genuinely new policy choice,
irreversible effect, external spend, credential mutation, quorum substitution, or
authority expansion still stops for the proper grant. The periodic review removes
avoidable owner dependency; it does not manufacture permission.

The heartbeat prompt is operational control material. It must preserve singleton
identity, distinguish routine wakes from the deeper review interval, name the
evidence surfaces above, and prohibit duplicate owners or probe attempts that consume
formal authority. Projects test prompt changes and verify the persisted scheduler
target, cadence, status, and content after every update.

The privacy-safe DNG field trial in
[`receipts/dng-workstream-liveness-field-trial-20260824.json`](../receipts/dng-workstream-liveness-field-trial-20260824.json)
demonstrates the intended boundary: an unchanged campaign `HOLD` remained unbypassed
while the loop selected and verified one provider-free, zero-authority migration
candidate. The receipt is motivation and local verification evidence only; it is not
independent acceptance or adoption credit.

### 5. Three workstream roles stay explicit

A project may use different names, but it should expose three non-interchangeable
roles:

- **Product** chooses and validates user-visible outcomes and acceptance evidence.
- **Software/Factory** implements, reviews, tests, builds, and prepares release
  candidates.
- **Fleet/Operations** maintains provider sessions, routing, capacity, custody,
  schedulers, disk/admission controls, and continuity.

One agent may temporarily serve more than one role only when the authority map says
so. Role overlap does not erase separate gates or independent-review requirements.

## Minimum portable proof

A project may claim adoption only after production-path tests prove:

1. a fresh watcher heartbeat plus an ended owner turn is not classified as inference
   healthy;
2. an owner turn plus a stale/foreign instrument is reported as a split health state,
   not collapsed to green;
3. two lane labels sharing one failure-domain tuple are refused as independent
   failover, while a genuinely distinct tuple is identified as such without exposing
   raw account identity;
4. context overflow cannot populate quota/reset fields, and a quota refusal cannot be
   rewritten as context overflow;
5. two concurrent deliveries of one ingress request produce at most one terminal
   adjudication and no duplicate seat, nudge, task, card, intent, or authority;
6. resuming an exact idle owner preserves session identity and independently verifies
   every bound artifact before `BEGIN` or `REFUSAL`;
7. a 30-minute cycle with unchanged authoritative state makes no mutation and emits
   no false progress, while a newly satisfiable gate selects and executes one bounded
   action;
8. the improvement loop cannot bypass admission, ownership, review, path, release,
   deletion, credential, or policy gates even after repeated blocked cycles;
9. every due cycle atomically binds baseline, largest failure, selected action or
   `HOLD`, verifier result, score delta, and next candidate, and cannot claim progress
   by changing only a timestamp;
10. two consecutive identical `HOLD` records trigger root-cause analysis or one
    independently safe backlog action without creating new authority;
11. every health claim identifies the next named action and the axes required for that
    action, so "healthy" cannot mean merely "some process is alive;"
12. interactive plan allowance plus a noninteractive session failure produces a
    split-signal diagnosis, not an unsupported claim of global quota exhaustion,
    account mismatch, or provider health;
13. Desktop and CLI account identities are compared locally before their usage or
    failure receipts are attributed to one failure domain, without publishing raw
    identity to the fleet bus;
14. a missing or misbound bridge Monitor is classified as a reachability defect and
    cannot populate provider-capacity fields;
15. a quiet cycle proves that falsification-relevant facts were refreshed inside
    their freshness windows, rather than relying only on an unchanged state hash; and
16. updating the improvement loop preserves one scheduler singleton and verifies its
    persisted target, cadence, status, and prompt without consuming provider or
    governance attempt authority.

Project-local scheduler names, task ids, intervals, queue schemas, provider names,
models, paths, credentials, capacity thresholds, and release mechanisms do not
travel. Sibling projects adopt by local authority map, reviewed implementation,
negative controls, and dated receipts, or record `DISTINGUISH(reason)`.
