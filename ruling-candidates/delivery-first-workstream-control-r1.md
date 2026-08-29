# Ruling candidate: Delivery-first workstream control R1

Status: **OWNER-DIRECTED PROPOSAL / ZERO CROSS-PROJECT RUNTIME AUTHORITY**

Candidate id: `DELIVERY_FIRST_WORKSTREAM_CONTROL_R1`

Project/date: `adversarialllm` / `2026-08-26`

## Objective

Software-factory lanes exist to land accepted changes, close gates, and deliver user-visible
milestones. Receipts, checkpoints, reviews, rotations, and status narration are supporting evidence;
they are not delivery outcomes and earn no progress credit by themselves.

## Proposed control law

1. **Land before expanding.** If any accepted, authorized, unlanded item exists, the lane's next
   executable deliverable is the oldest such item and its action is `LAND_ACCEPTED`. The lane may
   not author a new proposal, packet, review request, or evidence family until that landing either
   completes or reaches a new typed blocker.
2. **Escalate unchanged queues.** An actionable queue unchanged for two consecutive wakes or 30
   minutes, whichever occurs first, is `ESCALATE_STALLED_QUEUE`. Repeating the same checkpoint is
   forbidden. Escalation names exactly one blocker, one callable owner, and a deadline no more than
   60 minutes after observation.
3. **Credit outcomes only.** Progress credit is derived from unique evidence-bound merged commits,
   closed gates, and predeclared user-visible milestones in the reporting window. Bare counts and
   receipt counts are diagnostic and contribute zero credit.
4. **One blocker owner.** Every open primary blocker has exactly one owner and one future deadline.
   A missed deadline invalidates the open status and requires a separate terminal settlement before
   the lane selects its next executable deliverable; it does not create another request for the same
   blocker.
5. **No aimless expansion or rotation.** `EXPAND_LANE` and ordinary rotation require a named next
   executable deliverable. Mandatory safety/session-continuity rotation is the sole exception: it
   preserves the singleton but must terminate in `HOLD_NO_EXECUTABLE_DELIVERABLE` until a concrete
   deliverable is named.
6. **Evidence must close a gate.** New evidence authoring is admissible only when no accepted item is
   landable, the evidence closes one named current gate, and `CLOSE_GATE` is the next executable
   action. General reassurance, re-packetization, and unchanged-state receipts are inadmissible.

## Machine-checkable candidate

`tools/check_delivery_first_lane_status.py` validates a closed status shape and the semantic laws
above. Outcome rows are a cumulative, evidence-bound ledger and progress credit is only the delta
from the immediately previous valid status. Bootstrap validation requires explicit `--bootstrap`;
every later wake must pass `--previous`, which enforces same-lane chronological continuity,
monotonic unchanged-queue counters, append-only outcome history, and one unsettled escalation per
queue/blocker identity. The queue fingerprint is derived from canonical represented queue content,
not supplied discretionarily. Milestone credit includes the predeclared milestone-manifest digest.
The validator bounds the complete document at 16 MiB rather than imposing an artificial row-count
expiry on the cumulative outcome ledger.
`examples/delivery-first-lane-status-v1.json` is a non-authoritative example. Passing the
validator grants no merge, provider, reviewer, Product, Factory, Fleet, release, or runtime
authority; each project must separately adopt and bind the control to its own queue and owner model.

## Rollout and success criteria

- Shadow for one reporting window, then require the status document at every material lane wake.
- Success is a reduction in accepted-but-unlanded age and an increase in merged commits, closed
  gates, or user-visible milestones. More receipts with unchanged outcomes is a regression.
- Abandon or revise R1 if it causes unsafe landing, bypasses an independent gate, or converts a
  mandatory safety rotation into executable authority.
