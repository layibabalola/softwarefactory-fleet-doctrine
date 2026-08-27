# Ruling candidate: autonomous production-proof throughput R1

Status: **PROPOSED ONLY — NOT YET A RATIFIED RULING OR PROJECT RUNTIME AUTHORITY**

Owner direction: 2026-08-23/24. The owner requires the software factory to keep product, factory,
and assurance lanes moving without repeated manual prompts. Safety gates remain unchanged. The
strategy is to make production-equivalent proof cheaper, earlier, and more direct while preserving
fail-closed authority.

## Problem this candidate addresses

A factory can increase local fixture rigor while still making no customer progress. The recurring
failure shape is a narrow seam passing in isolation before the exact production composition exposes
a mismatch in process entry, returned objects, parent-held handles, child routing, terminalization,
or downstream release. Authorizing another successor after each isolated repair converts safety
work into churn.

Project-local Cloudvore observations motivated this proposal: pre-authority review caught production
paths that differed from rehearsals, stale cross-file pins, and failures that could spend an identity
without a durable result. Those observations are not submitted here as portable evidence or an
adoption receipt. They identify hypotheses that the acceptance gate below must test independently.

## Proposed portable strategy

### 1. One complete production-equivalent rehearsal before authority

Before a one-use provider, controller, product, merge, or release authority is created, one inert or
disposable rehearsal must exercise the exact shipping composition through:

1. the real process or API entry and final argument/object shape;
2. producer-return objects and content-addressed inputs;
3. parent-held handles, inherited custody, and child ownership boundaries;
4. child routing, output reservations, late collisions, and descendant settlement;
5. claim publication followed by a physical path/bytes/digest/semantic rejoin;
6. provider or worker provenance and terminal framing;
7. durable PASS/HOLD terminalization for every post-claim failure; and
8. the downstream handoff or release boundary that would consume a PASS.

A fixture that substitutes a generic temporary file, simplified return value, synthetic provider
shape, or shorter call path does not prove production equivalence. It may support diagnosis but
cannot authorize execution.

### 2. Immutable proof inputs and single-use evidence

Every long proof starts from an immutable manifest or isolated snapshot. Immediately before launch,
the authority owner rejoins every input tuple and proves every future output namespace absent.
After completion, the same tuples are rejoined. Drift yields HOLD and zero credit.

Every proof namespace has exactly one authorized writer. The claim and result paths are reserved
with exclusive `CreateNew` semantics; the parent retains its claim handle and child/process custody
until descendant settlement; and the terminal result is published atomically and durably. A
pre-existing path, second writer, post-claim collision, late descendant, or lost custody yields
refusal or HOLD. It never permits a successor, replacement namespace, or retry of the spent identity.

Claims, leases, rehearsal identities, provider sessions, and durable validations are single-use.
Process exit or liveness never implies PASS; the authenticated result terminal outranks PID state.
Spent evidence is retained. It is never deleted to make a retry possible.

### 3. HOLD repairs the same source before another execution

On HOLD, preserve all evidence and diagnose the same source generation first. A successor package
is permitted only after the exact contradiction and smallest repair scope are recorded. The repair
must extend the production-equivalent rehearsal through the newly exposed boundary before another
authority is considered.

Static SOURCE_READY, green unit fixtures, or a package freeze grants no runtime, landing, product,
or score authority. Runtime credit begins only at the durable terminal explicitly named by the
current gate.

### 4. Parallelize disjoint reasoning; serialize only real ownership

Disjoint package construction, static review, source audit, debt derivation, and next-gate design
run in parallel under one-writer path custody. Serialization is derived from evidence-backed shared
contention domains, not broad provider or lane labels. Unknown overlap fails closed until the domain
is established. Parallel execution requires proven-disjoint quota and failure domains, output paths,
and ownership. Serialization is reserved for actual shared constraints:

- one provider or opaque quota domain;
- one governed thermal or workload lease;
- one Git ref, lifecycle ledger, or landing transaction owner; and
- explicit review-independence boundaries.

No lane waits merely because another lane is active. Conversely, elapsed time, source drafting, and
parallel activity are not reported as advancement unless a durable gate changes.

### 5. Autonomous critical-path control

While a long proof or repair is active, Cloudvore uses the following project profile. Other projects
must select bounded local cadences and notification thresholds through their own authority maps:

- **continuity loop, no later than every 10 minutes:** rejoin liveness and terminal evidence. Only
  an authenticated content-addressed transition may checkpoint the authoritative ledger and then
  publish phase, outcome, score/authority movement, and next gate;
- **strategy loop, no later than every 30 minutes:** ask what exact customer or score terminal is
  next, which path is critical, whether safe capacity is idle, what false serialization or adoption
  debt can be removed, whether work is producing terminals or successors, and what observed evidence
  says about ETA; then execute the highest-value safe authorized action in each proven-disjoint
  workstream or ownership domain.

An unchanged wake writes and publishes nothing. Identical transition identities are suppressed
before ledger or notification mutation, so replayed observations cannot produce duplicate notices.
A terminal condition such as “continue” persists across wakes without widening authority.

#### Ingress, inference, and publication invariants

The control loop is also bound by these normative invariants:

- **Instrument liveness never proves inference liveness.** A running scheduler, watcher, process,
  transport, or provider client proves only that instrument's observed state. Useful inference
  requires its own authenticated result terminal; an absent or stale inference terminal remains
  absent or stale even when every instrument is healthy.
- **Ingress is immutable and singly adjudicated.** Each accepted observation has one stable
  content-addressed identity, one declared authority and ownership domain, and exactly one durable
  adjudication. A changed, duplicate, ambiguous, or identity-less ingress is HOLD; repeated wakes
  may rejoin it but may not reinterpret it as a new observation or issue another adjudication.
- **Publication is event-driven.** State and user-facing notices publish on authenticated terminal,
  authority, blocker, liveness, or next-gate transitions. The passage of a cadence interval alone
  is not an event and cannot create a ledger mutation, duplicate action, or repeated notification.
- **An unchanged cycle is inert.** When all rejoined inputs and terminals are unchanged, the cycle
  performs zero state-changing work and emits no notice. It creates no successor, authority, claim,
  retry, provider call, workload, duplicate publication, or notification flood.
- **Serialization follows shared ownership.** At most one state-changing action may occur per
  proven shared contention or ownership domain in a cycle. Actions in domains proven disjoint by
  immutable authority maps may proceed concurrently; absence of such proof fails closed to one
  writer, not to an assumption of disjointness.

This proposal folds the overlapping intent of pull request #30, "Fleet workstream liveness and
autonomous improvement loop," into a production-proof strategy rather than establishing a second,
contradictory loop. It preserves #30's separation of inference and instrument liveness, immutable
ingress, event-driven publication, and project-local cadence/notification settings. It narrows the
"one action per cycle" rule to one state-changing action per shared contention or ownership domain,
so proven-disjoint work can proceed concurrently. If this candidate advances, #30 should be closed
as superseded only after its unrelated evidence and candidates have exact scoped successor
references, or revised against the accepted text before either proposal is ratified. The mixed-scope
#30 branch must not be merged as an alternate route to this ruling.

### 6. Reset-aware provider continuity

When a provider rate-limit terminal exposes an exact reset timestamp, retain the timestamp and exact
terminal tuple in canonical state. Do not probe or retry the spent namespace before reset. The reset
is wake eligibility only, never execution authority. At the first wake at or after reset, rejoin the
frozen successor and its still-absent outputs, then independently revalidate unexpired execution
authority, current evidence, admission/capacity gates, account and session identity, and every other
bound prerequisite. A missing, stale, changed, or ambiguous condition yields HOLD and no launch.
Only when all gates remain current may the already-authorized single invocation be consumed. If no
exact reset is exposed, record uncertainty and do not invent one.

Provider capacity is useful inference, not authority. Model, effort, account/quota domain,
permission mode, allowed tools, session, result provenance, auxiliary model usage, and denials are
authenticated from the real terminal rather than hardcoded into a receipt.

### 7. Score moves only at truthful product boundaries

Factory confidence and throughput are separate measures. Stronger safety architecture may improve
confidence without moving delivery score. No score moves from source review, fixtures, partial
composition, package creation, or elapsed effort.

A formal customer/delivery score moves only at the project's exact durable customer or product
delivery terminal, such as an accepted or released customer slice with authenticated downstream
consumption. Permit-backed controller segments, `BEFORE_PRODUCT_TEST`, product-test readiness,
source review, recovery rehearsals, and other internal gates may move explicitly named readiness or
safety submetrics, but never the formal customer/delivery score. The factory may not substitute a
nearby internal PASS for the named delivery terminal.

## Required measurements

An adopter reports both safety and throughput, including:

- median and tail time from frozen package to authenticated terminal;
- provider inference spent per authenticated terminal;
- execution successors per original source generation;
- pre-authority catches versus post-authority HOLDs;
- ready work blocked only by provider, thermal, review, or ownership custody;
- commits/subjects beyond the newest verified or adopted customer event;
- time to the next truthful customer boundary; and
- score movement, explicitly zero when no qualifying boundary occurred.

The desired trend is fewer post-authority successors, lower proof cost, less false serialization,
and shorter customer-terminal latency without weakening any safety gate.

## Failure and rollback criteria

An adoption is unsuccessful if it increases duplicate inference, permits an active or spent proof
to be retried, hides debt, treats PID exit as PASS, allows fixture-only evidence to authorize the
production path, weakens review independence, or moves score without the named durable boundary.

On violation, close automatic execution, preserve evidence, restore the last ratified authority map,
and continue package-only diagnosis. Rollback never deletes the adverse receipt.

## Acceptance gate

Before this becomes portable doctrine, a distinct adjudicator must bind the exact candidate commit,
tree, and file digest; obtain independent review from a qualified independence class; attempt to
falsify the strategy with hostile controls against at least one real production-entry rehearsal and
one result-dominant failure; prove that concurrent double writers and a late output collision cannot
produce two claims, two results, a retry, or false PASS; confirm that the cadence creates no duplicate
work or notification flood; append an exact acceptance or rejection to `RULINGS.md`; and merge the
reviewed bytes to canonical `master`. Actual falsification yields rejection or HOLD, never adoption.

Project adoption remains separate. Each adopter must publish a project-local disposition and proof;
this candidate grants no provider call, workload, task mutation, merge, release, product, score, or
automatic authority.
