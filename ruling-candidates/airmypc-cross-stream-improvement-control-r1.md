# Cross-stream improvement control — ruling candidate R1

**Status:** PROPOSAL / RULING CANDIDATE. Not ratified doctrine.
**Measuring project:** AirMyPC / AudioMile.
**Authority:** none. This document is data for review; it cannot activate work, providers, hardware,
publication, landing, billing, or repository mutation.

## Candidate purpose

A multi-lane software factory can have active tasks, passing tests, correct bytes, and still remain
systemically unhealthy. Work may be accepted but never landed, evidence may wait behind ceremony,
authority may be defective, or the exact required provider/model may be unavailable. This candidate
defines a small control loop above Product, Software Factory, and Fleet/Doctrine that detects those
conditions and selects one safe systemic improvement at a time.

The control loop coordinates the three delivery workstreams. It does not become a fourth delivery
lane, take their implementation work, grade its own output, or acquire their authority.

## Proposed ruling

### 1. Operate a factory-of-the-factory control loop

Each adopting project SHOULD maintain one coordination loop whose subject is the health of the whole
delivery system rather than the feature backlog of any one lane. The loop:

- reads structured state from Product, Software Factory, and Fleet/Doctrine;
- identifies the shared constraint preventing all workstreams from becoming genuinely green;
- selects at most one highest-leverage safe and reversible systemic improvement per evaluation;
- leaves author, reviewer, adjudicator, lander, publisher, and operator roles distinct; and
- returns ownership of lane-specific work to the owning lane.

The loop MUST NOT duplicate lane implementation, create a hidden fourth delivery queue, or treat its
coordination role as review, adjudication, landing, publication, provider, hardware, or billing
authority.

### 2. Evaluate locally on a bounded cadence; publish doctrine only on events

The AirMyPC measuring project evaluates every 30 minutes:

> What is preventing all workstreams from being genuinely green, and what systemic change can remove
> repeated delay?

An adopting project MAY choose a different local cadence and MUST record it as project configuration.
The evaluation cadence is not a doctrine publication cadence. Shared doctrine remains event-driven:
publish only a ratified, portable change at an authorized landing seam. When evidence and constraints
are unchanged, the evaluation emits `DONT_NOTIFY` and performs no write.

### 3. Measure four independent health dimensions

Health is a vector, not one status bit. A project MUST evaluate these dimensions independently:

1. **Delivery progress:** useful work is moving through its owning lane without duplicate ownership or
   stale coordination.
2. **Validation and evidence acceptance:** evidence is exact, reproducible, reviewed, and accepted at
   the boundary it claims.
3. **Durable authority and landing:** accepted work has lawful durable authority and converts to the
   intended landed or published state with complete readback.
4. **Execution and provider capacity:** the required executor, exact model, credentials, admission,
   infrastructure, and authorized action window are actually available.

`ACTIVE`, passing tests, correct bytes, or a successful review is evidence for one dimension only.
None proves whole-system health.

### 4. Track leading indicators, not only terminal failures

The loop SHOULD retain measurable time series or exact current-state receipts for:

- blocker age and repetition count;
- accepted-but-unlanded age;
- evidence-to-landing conversion rate and latency;
- coordination or review ceremony per successful landing;
- projected document headroom at current growth rate;
- stale or duplicate task, lease, and heartbeat targets;
- lock age and owner liveness;
- exact-model availability and reset horizon;
- byte-correct versus authority-correct state; and
- work returned to an owning lane because the control loop would otherwise duplicate it.

Thresholds are local configuration. A threshold crossing is a reason to prepare a safe transaction,
not authority to perform it.

Every evaluation MUST emit or bind one retrievable, versioned project-local receipt. Its schema MUST
bind at least:

- project and control-loop instance identity;
- evaluation/event identity, observation time, freshness bound, and terminal result;
- exact source subject, revision/tree, and input-receipt digests;
- coordinator, owner, author, reviewer, adjudicator, authority, executor, and session identities,
  using explicit `not-applicable` values where a role has not been invoked;
- proposed action identity and class, before/after measures, and the chosen disposition;
- provider, exact model, and effort identity when inference is used, or an explicit no-inference
  value; and
- every authority reference, validation result, and resulting artifact digest claimed by the
  evaluation.

The adopting project MUST specify a deterministic canonical serialization and digest algorithm for
that receipt, retain the exact bytes, and make every referenced receipt independently retrievable.
Opaque identities are compared as normalized exact values and MUST NOT be inferred from display
names. Credentials, tokens, private prompts, and other secrets MUST be represented only by
non-reversible identifiers or digests and MUST NOT be echoed into evidence. A missing, stale,
malformed, ambiguous, or unretrievable binding makes the affected health dimension `UNKNOWN`; it
cannot be counted as green.

Every path-valued field in a receipt, manifest, claim, journal, or terminal record MUST be either a
normalized project-relative slash path or an opaque identifier whose immutable mapping and digest
are independently retrievable inside the project's evidence boundary. Before serialization or any
write, the project MUST reject absolute POSIX paths, Windows drive-qualified or drive-relative
paths, UNC or device paths, home-relative paths, traversal (including traversal revealed by decoding
or normalization), and values containing user-profile material. Refusal uses a fixed reason code and
MUST NOT echo, log, quote, or otherwise include the rejected host-local value in any publishable
string. A physical path may be rejoined only inside the project-owned executor after exact root
resolution plus containment and reparse checks; that resolved host-local path remains unpublishable.

Before creating a receipt, the project MUST authenticate a transition identity from the normalized
project, loop and event identities, canonical input digests, prior terminal, and proposed terminal.
Only a new authenticated transition may create exactly one immutable receipt through a create-once
or compare-and-swap boundary. If inputs and terminal are unchanged, or the transition identity is a
duplicate, the evaluation MUST bind the existing immutable receipt by exact digest and reference,
return `DONT_NOTIFY`, and perform no create, rewrite, append, notification, or other state-changing
work. Duplicate suppression occurs before any write. A missing, ambiguous, or conflicting existing
binding yields `UNKNOWN` or `REFUSED` with zero write; it never licenses a replacement receipt.

### 5. Select one safe systemic improvement

At each evaluation, the loop MAY propose or prepare at most one improvement that is all of:

- reversible or naturally fail-closed;
- disjoint from active lane claims;
- measurable before and after;
- narrower than the shared constraint it addresses; and
- unable to self-certify its own acceptance.

If no such improvement exists, the loop records nothing and returns `DONT_NOTIFY`. It MUST NOT invent
work to satisfy the cadence, duplicate implementation, or self-grant review, adjudication, landing,
publication, provider, hardware, authentication, or billing authority.

The loop is proposal/prepare-only by default. A threshold, health result, prepared packet, or doctrine
record is never execution authority. If an adopting project elects to execute a prepared action, a
separate project-owned transaction MUST first provide all of these controls:

1. independent review and durable local authority naming the exact action identity and permitted
   action class;
2. a distinct project-owned supervisor entrypoint and executor/session identity that the control
   loop cannot impersonate;
3. an allowlisted subject, exact tree/input receipts, authority marker, absolute expiry, and
   one-attempt/failure contract;
4. final launch-time revalidation of subject, gates, claims, leases, authority, destination, and
   provider predicates immediately before mutation;
5. structural refusal of direct invocation that bypasses the reviewed supervisor; and
6. automatic return to `CLOSED` on missing, stale, changed, or ambiguous state.

Any rollback MUST be an exact separately authorized rollback already bound by that transaction. A
failure or ambiguous outcome otherwise stops and preserves evidence; it does not invent cleanup,
retry, rollback, or reseal authority. The coordination loop observes the terminal receipt but does
not grade or ratify the execution.

### 6. Treat exact-model availability as a conjunction

Provider readiness MUST distinguish all of these independent predicates:

1. a provider seat exists;
2. authentication is valid;
3. the required exact model is visible to that seat;
4. provider capacity is available and its reset horizon is known;
5. the project admits the invocation under its own safety floor;
6. a concrete actionable ticket is admitted; and
7. durable authority covers the requested action.

Failure of one predicate MUST NOT be reported as failure of another. An exhausted exact model SHOULD
be suppressed until its known reset rather than repeatedly probed. A healthy exact alternate MAY be
preferred only for concrete admitted work and only when role separation and authority remain valid.
Idle inference MUST NOT be used as a provider-health probe.

Each project MUST also maintain a complete census of unattended launchers that can reach a provider
or mutate governed state. The census binds each launcher to one pinned supervisor entrypoint, exact
code digest, task/heartbeat target, lease, child process tree, actionable ticket, provider/model
selection, and start/terminal receipt. Direct provider invocation outside that supervisor MUST be
structurally refused. The supervisor MUST revalidate the full conjunction above at launch time,
contain and account for its child process tree, close or expire the lease deterministically, and
return the relevant gate to `CLOSED` after the attempt. If an exact preauthorized rollback exists,
the supervisor may execute only that rollback; otherwise mutation failure preserves evidence and
stops. Missing, stale, lost, malformed, duplicate, or ambiguous launcher, observer, process, lease,
or terminal evidence yields `UNKNOWN` or `REFUSED`, never healthy execution capacity.

### 7. Fragment stable-parent documents proactively

Append-only authority and evidence documents SHOULD declare a preparation threshold below their hard
cap and a mandatory transaction boundary with enough remaining headroom to record safe authority.
Before the hard cap, a project SHOULD prepare stable-parent fragmentation:

- preserve the parent prefix byte-for-byte;
- move governed historical sections into manifest-bound child documents;
- bind child order, hashes, sizes, and parent pointers in one manifest;
- use one exclusive lock for the append/roll operation;
- use compare-and-swap against the exact expected parent and manifest state;
- create children exclusively so a competing writer cannot overwrite them;
- journal every phase and provide crash-safe resume or fail-closed recovery that never invents
  success, retry, rollback, or cleanup authority; and
- validate physical bytes and durable authority separately before declaring the roll complete.

Planning a roll or materializing correct post-images does not authorize the transaction. Physical
headroom and durable authority are separate gates.

The roll transaction MUST use a versioned claim and journal that bind the transaction ID; expected
parent path, hash, size, and tree; expected and proposed manifest identity; ordered child paths,
hashes, sizes, and parent pointers; writer role/task/session; lock identity; and every permitted
phase and terminal outcome. Child creation is create-once, no-overwrite, containment-checked, and
reparse-safe. The writer flushes the claim before mutation and each phase transition before the next
phase, stops at the first failure, and reconciles any existing claim/journal before attempting an
append or roll.

Recovery MUST deterministically handle process death, competing writers, partial child creation,
parent-CAS success followed by journal-write failure, and an ambiguous terminal read. It does so by
re-reading the exact parent, manifest, children, claim, lock, and journal and classifying them against
the declared preimage and postimage. Exact postimages may be preserved as physically materialized
evidence, but they remain authority-invalid until separately reconciled. Any state that cannot be
classified without guessing becomes `REVIEW_REQUIRED` or `REFUSED`. Rollback, retry, overwrite,
cleanup, or completion may occur only when that exact operation was separately authorized; recovery
never infers it from byte correctness.

### 8. Preserve byte-correct evidence when authority is defective

A byte-perfect materialization can still be governance-invalid when the executor, reviewer,
adjudicator, or authority provenance is defective. In that case the project MUST:

- preserve the exact bytes and receipts as non-authoritative evidence;
- stop further mutation;
- identify the defective authority edge precisely;
- reconcile authority through a new independent review and durable ruling; and
- avoid invented retry, cleanup, rollback, or re-execution authority.

Correct bytes do not cure invalid provenance. Invalid provenance does not justify destroying correct
bytes.

### 9. Require explicit sibling adoption

Doctrine data grants zero operational authority. A sibling project that consumes a ratified version of
this candidate MUST record exactly one disposition:

- `ADOPT(reference)`; or
- `DISTINGUISH(reference, reason)`; or
- `REJECT(reference, blocker)`.

`REJECT` is required when reproducible exact evidence falsifies the candidate's core controls or the
consumer cannot install a safe closed-by-default implementation. The blocker record MUST bind the
tested reference, reproducer or counterexample, observed result, and evidence receipt; it is not a
silent opt-out. `DISTINGUISH` is for a documented project difference that leaves the portable core
unfalsified.

An adopter MUST also:

1. choose and record its local evaluation cadence and document thresholds;
2. map coordinator, author, reviewer, adjudicator, lander, publisher, and operator roles;
3. install measurable structured state for the four health dimensions and leading indicators;
4. test negative paths for stale/duplicate targets, document headroom, provider predicates, and
   authority provenance;
5. prove unchanged evaluations perform no write and return `DONT_NOTIFY`; and
6. obtain separate project-local authority for every operational action.

## Measuring-project evidence boundary

AirMyPC / AudioMile supplied the observations used to shape this candidate: accepted work waiting for
headroom, exact-model capacity differing from project admission, and correct roll bytes whose authority
provenance failed independent verification. Those are measuring-project facts, not portable doctrine.
Only the generic controls above are proposed for fleet use.

This candidate intentionally contains no local filesystem paths, credentials, private artifacts, raw
transcripts, or mutable incident hashes.

## Required review before ratification

A non-author reviewer SHOULD challenge at least these questions:

- Does the control loop remain coordination rather than a fourth delivery lane?
- Can any cadence wording be misread as publication or mutation authority?
- Are the four health dimensions independent and falsifiable?
- Do provider predicates prevent exact-model and admission failures from being conflated?
- Does the fragmentation transaction fail closed under competing writers and process death?
- Does the incident rule preserve useful bytes without laundering defective authority?
- Does the launcher census refuse direct or ambiguously observed execution?
- Does the receipt schema make identity, evidence, and terminal state independently re-derivable?
- Does the adoption contract include ADOPT, DISTINGUISH, and evidence-bound REJECT while granting
  zero authority from doctrine data?

Ratification, if any, requires the repository's separate review and authority process and a later
append to the shared ruling log. This proposal branch and any pull request do not perform ratification.
