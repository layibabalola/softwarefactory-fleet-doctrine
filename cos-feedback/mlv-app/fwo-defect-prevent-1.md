# FWO-DEFECT-PREVENT-1: catch defects before CoS review (MLV-App + fleet)

status: APPROVED (Layi via chat, ~7:44 PM CT 2026-10-16)
issued_by: Chief of Staff (Grok Bot)
issued_utc: 2026-10-17T00:45:00Z
D: 2026-10-16
repo: SuperDimensionalSpaceFortress/MLV-App (first), then fleet-wide
delivered: (PR comment on MLV-App #454, same venue as FWO-ACK-1)
ack_due: 2026-10-17 7:45 PM CT (2026-10-18T00:45Z)
asks: FWO-DEFECT-PREVENT-1 items 1-6, ACK with plan+ETA or DISTINGUISH per item

## Why
CoS is acting as first reviewer. Most of today's Blockers were defect shapes the factory could have caught itself before push.

## Items
1. **Master-parity differential on every safety/hook/lint change.** Run the full deny corpus against master and head, and fail on any line master refuses but the head allows. The parity sweep must not skip f-string rows.
   Evidence: #455 r8/r9 cmd bypasses (`if exist P (rd=P)` passed head, refused by master; sweep skipped 21 f-string rows); #465 r2+ clip-argument gap (`Run MLVAppRelease.exe --clip take01.mlv` and 5 variants admitted, master and r1 refuse).
2. **Shared defeater corpus per rule family**, run on every change: glued switches; `(` `;` `,` `=` delimiters; quoting; argument position; extension-less paths.
   Link: ruling-candidates/mlv-safety-lint-exemption-defeater-corpus-r1.md (4 recurrences).
3. **Execute card routes before push.** Run every command a card names in a scratch bus, and check that each command exists.
   Evidence: #468 r3/r4 (adoption steps broke the installed pre-push hook; pin command missing required flags); #469 r1-r4 named `doctrine-sync debt`, which did not exist.
   Link: ruling-candidates/steward-handoff-card-route-is-live-and-exercised-r1.md.
4. **Overlap check for doctrine proposals.** Each proposal lists the rules it touches or supersedes.
   Evidence: #469 r1 contradicted the 2026-08-30 fleet-sweep correction, R15, and the 2026-10-03 fold candidate without saying so.
   Link: ruling-candidates/ruling-candidates-name-what-they-supersede-r1.md.
5. **CI on declared runtime platforms.**
   Link: ruling-candidates/ci-matrix-covers-declared-runtime-floor-r1.md (agent-bridge #233, MLV-App #468).
6. **Run the Claude + Codex adversarial legs on the head before marking ready or requesting CoS review.**
   Evidence: legs were 0/2 at CoS review on most PRs today (#465, #467, #468, #469, #470, #471, #472).

## Ask
Within 24h, reply on the delivery thread per item:
`ACK: <remediation plan + ETA>` or `DISTINGUISH: <reason>`. A bare ACK does not count.

## Limits
Process and tooling changes inside factory lanes only. Enforcement changes (CI workflow, ruleset, branch protection, merge gates or queue) still need Layi's own separate DECISION. This order does not authorize them.

## Related
- cos-feedback/mlv-app/fwo-ack-1.md
