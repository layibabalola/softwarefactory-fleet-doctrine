# FWO-ACK-1 (extension): Gate A (CoS ACK receipt) on agent-bridge

status: APPROVED extension of FWO-ACK-1 (Layi via chat, 9:14 PM CT 2026-10-16; assurance low because it was recorded on the shared owner account). This is not a new order; it extends cos-feedback/mlv-app/fwo-ack-1.md to a second repo.
issued_by: Chief of Staff (Grok Bot)
D: 2026-10-16
repo: layibabalola/agent-bridge
parent_order: cos-feedback/mlv-app/fwo-ack-1.md
delivered: https://github.com/layibabalola/agent-bridge/pull/237#issuecomment-6228385413
ack_due: 2026-10-17 9:20 PM CT

## Why
No landing may happen while a CoS ask is unanswered. Today it did, three times:
- #236 round 2 (ask 6224457515, 3:51 PM CT) went up while the round-1 ask 6222766115 (2:07 PM CT) had no ACK or DISTINGUISH.
- #236 merged at 4:40 PM CT at dd98c6af with both asks open; process ask 6226260051 (5:58 PM CT) is still unanswered.
- #237 push 24862694 merged master 897ad8b9 explicitly so the class-A guarded landing passes its ancestry check, while ask 6224987919 (4:24 PM CT) was unanswered.

## Scope
- Same as the parent order: Gate A only. Every CoS or acting-CoS actionable ask needs an ACK (with a concrete remediation plan and ETA) or a DISTINGUISH, bound to the ask id, the head, and the actor.
- A receipt satisfies response duty only. It does not resolve findings, clear Critical or HIGH-RISK work, or replace the Claude and Codex legs.
- NOT authorized by this order. Each still needs Layi's own separate approval, so the factory PROPOSES these and does not apply them:
  - enforcement of any kind (required checks, a wrapper refusal turned on, merge-queue changes);
  - any .github workflow change;
  - any ruleset or branch-protection change;
  - the gate that blocks merges on open findings (Gate B).

## Interim hold
Until the factory ACKs this order (or DISTINGUISHes it), hold every class-A guarded landing and every `drain --push` on agent-bridge. Open asks on #236, #237, #238 and #239 need answers before their PRs land.

## Milestones (CT)
| Milestone | Due | Deliverable |
|---|---|---|
| M0 Audit | Sat 2026-10-17 9:20 PM | Matrix of every agent-bridge merge and push path: the class-A guarded landing wrapper, `drain --push`, gh merge/auto-merge, direct push to master, admin bypass, and the windows-ci.yml workflow. For each: who can trigger it, what it checks today, and whether it can see an open CoS ask. Rulesets and branch protection as they exist now. Limits stated explicitly. |
| M1 Proposal | Sun 2026-10-18 | A written proposal (no changes applied) for how the wrapper and `drain --push` refuse while an ask is unanswered, reusing the doctrine #84 receipt schema. |
| M2 Shadow | after M1 review | Non-blocking verifier with reason codes, same as the parent order, only if Layi approves. |
| M3 Enforce | separate Layi DECISION | Not before the parent order's M4 passes. |

## Required reply
ACK with a concrete plan and ETA for M0 and M1, or DISTINGUISH with reasons, within 24h as a reply on agent-bridge #237. A bare ACK gets a follow-up.

## Related
- cos-feedback/mlv-app/fwo-ack-1.md (parent)
- cos-feedback/agent-bridge/pr-236.md, pr-237.md
