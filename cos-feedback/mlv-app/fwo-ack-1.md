# FWO-ACK-1: Gate A (CoS ACK receipt) on MLV-App

status: APPROVED (decision LD-20261016-FWO-ACK-1, Layi via chat, 10:20 AM CT 2026-10-16; assurance low because it was recorded on the shared owner account)
issued_by: Chief of Staff (Grok Bot)
issued_utc: 2026-10-16T15:22:38Z
D: 2026-10-16
repo: SuperDimensionalSpaceFortress/MLV-App
delivered: https://github.com/SuperDimensionalSpaceFortress/MLV-App/pull/454#issuecomment-6218717904
ack_due: 2026-10-17 10:20 AM CT

## Scope
- Gate A only. Every CoS or acting-CoS actionable ask needs an ACK or DISTINGUISH receipt, bound to the review or ask id, the revision or digest, the applicable head, and the actor identity.
- A receipt satisfies response duty only. It does not resolve findings, clear HIGH-RISK work, or replace the Claude and Codex legs.
- This order does NOT authorize any of the following. Each needs a separate Layi DECISION:
  - Gate B;
  - M3 enforcement: any required check, ruleset, branch protection, or merge-queue change;
  - merging any .github workflow;
  - a GitHub App, credential, or identity;
  - M5 fleet rollout.

## Owner
- Implementation: the MLV-App factory controller, with one named producer lane per milestone.
- Review: CoS reviews each milestone PR; Dot reviews as an advisor; Muse verifies read-only.
- Approvals: Layi.

## Repos and PRs
- doctrine #84 (f468520d): response-duty text plus the receipt schema.
- doctrine #85 (88f11713): the leg-publication and trust path. Its five open blockers must close before it is relied on.
- One new MLV-App PR: the verifier plus the `factory/cos-ack` check, kept in shadow mode.

## Milestones (CT)
| Milestone | Due | Deliverable |
|---|---|---|
| M0 Audit | Sat 2026-10-17 10:20 AM | Matrix of every merge and enqueue path (controller, queue, auto-merge, direct push, admin bypass), rulesets 24445366 and 20991889, classic protection (403), plan eligibility, identities, and bus sources. Limits stated explicitly. |
| M1 Schema | Sun 2026-10-18 | Receipt, review, delivery, and evaluation records in #84. Merges after CoS and Dot review. |
| M2 Shadow | Tue 2026-10-20 | Non-blocking verifier on PR and merge_group events, with reason codes. 48h shadow run until Thu 2026-10-22, then reconcile false positives and delivery gaps. |
| M4 Acceptance | Fri 2026-10-23 | End-to-end refusals on the real merge and queue paths (cases below). |
| M3 Enforce | not before Fri 2026-10-23 | Only after M4 passes and a separate Layi DECISION. Includes a rollback that never turns a failure into a pass. |
| M5 Fleet | not before Mon 2026-10-26 | Repo by repo, with an 8-repo matrix. Separate Layi DECISION. |

## Acceptance evidence (M4)
Each case needs a run link, the SHA, and a reason code.
- **Refused:**
  - missing or generic ACK;
  - wrong UUID, revision, digest, or head;
  - superseded review;
  - pending delivery;
  - bus unavailable;
  - deleted record;
  - forged actor or check;
  - new push;
  - queue rebuild;
  - review published after green;
  - direct merge or push;
  - admin bypass (documented as unenforceable if GitHub cannot block it).
- **Passed:** a valid ACK, and a valid DISTINGUISH.

## Related
- ruling-candidates/merge-gate-requires-tip-scoped-legs-r1.md (r2, 38e24ee)
