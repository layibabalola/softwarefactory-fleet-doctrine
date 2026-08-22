# Ruling candidate: fail-closed provider-lane lease self-healing R1

Status: **PROPOSED ONLY — NOT A RULING / NOT ACTIVE / ZERO AUTHORITY**

Measuring project: DNG Auto Processor. The privacy-safe incident receipt is
[`dng-auto-processor/receipts/DNG-LEASE-SELF-HEALING-INVESTIGATION-20260822.md`](../dng-auto-processor/receipts/DNG-LEASE-SELF-HEALING-INVESTIGATION-20260822.md).

## Candidate proposition

Adopt one portable rule for provider-lane lease recovery:

> A self-healer may terminate proven-dead authority; it may never manufacture live authority.

Recovery may produce only:

1. `PRECLAIM_RELEASED` — a valid exact preclaim is retired from a durable same-attempt proof that
   provider process creation did not occur;
2. `LEASE_RECOVERED_RELEASED` — damaged or missing lease bytes are reconstructed into a terminal
   release from authenticated attempt-journal evidence; or
3. `LEASE_QUARANTINE_HOLD` — evidence is incomplete, contradictory, unreadable, or process outcome
   remains unknown, so no ownership transition occurs.

Self-healing never claims a lane, opens a provider gate, launches inference, transfers a role,
changes a requested model or effort, or supplies review/acceptance credit. After recovery, a later
owner still enters through the project's ordinary canonical claim path and all existing model,
effort, role, restriction, packet, capacity, gate, process, and quality controls.

## Typed prelaunch recovery

Every provider-admission attempt should durably emit exactly one attempt-bound result before return.
A validation failure before the sole process-creation boundary may authorize exact preclaim release
only when its result binds the attempt, transaction, session, lane, packet, subject, executable,
arguments, policy, authorization, and post-claim lease hash and records:

- `launched=false` as a native boolean;
- `process_creation_reached=false`;
- `process_create_count=0`;
- exact-zero complete provider/token counters; and
- one enumerated prelaunch reason.

The supervisor may release only after a locked dispatch-time reread still matches the preclaim lease
hash and the result tuple matches its in-memory preclaim tuple. Missing, duplicate, malformed,
mismatched, or nonterminal results are `LAUNCH_OUTCOME_UNKNOWN` and retain the lease.

This rule is narrower than checking for a process after failure. Process absence is never recovery
authority: a process may have launched and exited between observations.

## Authenticated damaged-lease recovery

Malformed, torn, semantically invalid, or missing lease bytes require a resumable recovery
transaction. Automated reconstruction is allowed only when every conjunct is proven:

1. the exact lane path is plain, contained, and not a reparse surface;
2. exact bad bytes or exact absence are fingerprinted under the canonical coordination lock;
3. an append-only broker/admission journal authenticates the last owner/preclaim and preserves the
   exact intended lease bytes or a complete field-level record;
4. the attempt journal proves either that process creation was never reached or that the bound
   contained process tree has a terminal receipt and no descendants remain;
5. process observation is evaluable and bound to a non-reusable identity such as PID plus creation
   time;
6. heartbeat, restriction, packet, and route-consumption evidence do not contradict the terminal
   outcome;
7. a unique recovery ID and durable intent bind every input hash before mutation; and
8. the locked dispatch-time reread is byte-identical to the intent.

The transaction archives the exact preimage at a content-addressed path, atomically writes a
reconstructed `retired-by-recovery` terminal lease, verifies it from disk, and commits a terminal
receipt binding the prior bytes/absence, archive, reconstructed bytes, journal head, process proof,
recovery ID, and terminal state. A planner treats that state as free only when the entire receipt
chain validates.

If any conjunct is absent, ambiguous, unavailable, or contradictory, the implementation may write a
zero-authority alert/intent sidecar but must leave lease authority blocked. It may not delete,
overwrite, rename away, or infer the lease.

## Crash and concurrency law

Recovery is monotonic and resumable:

- intent without mutation is revalidated and retried;
- an archive with an unchanged lease is verified and resumed;
- a replaced terminal lease without a committed receipt remains blocked while recovery verifies and
  commits it;
- a committed receipt is audited idempotently; and
- foreign drift at any step preserves all evidence and holds.

One canonical coordination lock protects classification, dispatch-time reread, archive, replacement,
and receipt progression. Every mutation uses exact-preimage compare-and-swap. Concurrent healers must
produce exactly one winner and one byte-identical refusal.

## Mandatory hostile controls

No project may claim conformance until production-derived fixtures prove at least:

1. a frozen-prompt mismatch before process creation returns typed zero-launch and exact same-tick
   preclaim release;
2. slow but valid live ownership is never repaired;
3. a live contained process with stale or missing heartbeat is never repaired;
4. a process that launched and exited without a terminal receipt is not mistaken for a prelaunch
   failure;
5. unavailable, ambiguous, or overflowing process observation holds;
6. PID reuse or creation-time mismatch holds;
7. malformed, zero-byte, truncated, duplicate-key, wrong-type, future-time, and out-of-domain leases
   without an authenticated journal remain byte-identical and blocked;
8. those corruptions recover only with a complete bound zero-launch or terminal-process journal;
9. a missing lease recovers only when exact intended bytes/fields and exact absence are bound;
10. wrong lane, session, transaction, packet, subject, or lease hashes refuse;
11. a lease or packet race before the dispatch-time reread refuses;
12. reparse, alias, and out-of-root archive targets refuse;
13. interruption after every durable transition resumes without dual ownership or lost evidence;
14. concurrent healers yield one recovery only;
15. duplicate, replayed, forked, or hash-broken receipts hold;
16. healing uses zero provider calls, processes, tokens, and tools;
17. recovered terminals still require an ordinary fresh claim with exact model/effort/role controls;
   and
18. at least one guard-removal mutant makes a required negative fail.

## Required adjudication before acceptance

- exact candidate commit, tree, closed manifest, and source/evidence hashes;
- independent non-author mechanics and safety reviews;
- hostile controls under every supported runtime host;
- a production-derived no-launch incident fixture plus corruption/restart fixtures;
- a distinct adjudicator's explicit accept or reject entry in `RULINGS.md`; and
- separate project-local transactional preview, installation, rollback, and natural-cadence proof.

This candidate grants no provider invocation, scheduler or lease mutation, gate transition, task
enablement, authentication action, project adoption, merge, release, or installation authority.
