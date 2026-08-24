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

### 5. Select one safe systemic improvement

At each evaluation, the loop MAY propose or execute at most one improvement that is all of:

- within current durable authority;
- reversible or naturally fail-closed;
- disjoint from active lane claims;
- measurable before and after;
- narrower than the shared constraint it addresses; and
- unable to self-certify its own acceptance.

If no such improvement exists, the loop records nothing and returns `DONT_NOTIFY`. It MUST NOT invent
work to satisfy the cadence, duplicate implementation, or self-grant review, adjudication, landing,
publication, provider, hardware, authentication, or billing authority.

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
- `DISTINGUISH(reason)`.

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
- Does the adoption contract require negative-path evidence and zero authority from doctrine data?

Ratification, if any, requires the repository's separate review and authority process and a later
append to the shared ruling log. This proposal branch and any pull request do not perform ratification.
