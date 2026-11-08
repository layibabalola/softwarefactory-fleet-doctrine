# Factory prevention plan — proposal (Muse, 2026-11-08)

Status: PROPOSAL, not adopted. Owner decision owed on item 1 (Gate B enforcement) only. Items 2–6 are proposals for Dot (seat-holder) to ratify and the factory to implement. Advisory under R18; nothing here gates merges until the owner decides.

## Background (evidence)

Sampled 8 of Dot's latest verdicts (2026-11-07): all ADVISORY, all name defects. Factory legs + CI are usually green on the same heads (#771: 17 APPROVE references, green CI), so prevention catches broken builds; the legs miss subtle correctness — record-integrity defects, receipt ordering (#753 A1, still open at merge), handover races (#764, found-not-fixed), presentation defects (#420).

Recurring classes: egress gate changes shipped unreviewed three times in two days (#320/#324/#325); repackage pattern (#333/#342); follow-up fixes inheriting gaps (#347/#352).

Coverage, not defect escape, is the bigger hole: 91 merges shipped with no CoS verdict, mostly during dark episodes (7 episodes; latest ~40h, Nov 5–7).

The ACK loop works for named defects but asks die after one reminder (#704, #238, #231/#104; Grok's G1 M0 matrix past due since Oct 31, M0 never built).

## 1. Pre-close verdict check in the merge path (highest leverage)

Mechanics: before any close, the factory reads `cos-feedback/<project>/pr-<N>.md`, compares the recorded tip (`head` / `head_sha`) to the close head, and diffs verdict tip vs close head. Key on content identity (blob SHAs), not PR number. Record the check outcome in the PR (verdict-file check passed / stale-tip / no-verdict / benign clearance).

Would have caught: #333/#342 repackages, #347/#352 follow-ups, #320/#324/#325 egress triple.

Status: Gate B mechanical gate ran report-only Oct 30–Nov 1 and closed with no extension. Enforcement is a separate owner decision — NOT decided here.

## 2. Defect-class checklist in the legs + regression tests

Each A1/B1 class Dot finds becomes a permanent leg checklist item with a regression test:

- Receipt/currency ordering: three-receipt counterexample, both creation orders (#753 A1).
- Handover races: PID reuse, handle-acquisition order (#764).
- Record integrity on shared-helper roots (#420, #748).
- Actual-merge vs synthetic CI distinction (Dot keeps drawing it; legs should verify the actual merge tree).
- Egress/ingress gate changes: full gate review before merge (#320/#324/#325).

Owner: factory implementers + SOL Codex reviewer. Dot to confirm the class list.

## 3. Repackage / follow-up inheritance

A new PR number on the same content, or a follow-up fix to a flagged PR, inherits the original gap: fresh verdict or recorded clearance required. No "review counts as round 2" assertions.

## 4. Tracked ask registry with escalation

Every CoS ask gets an ID, a due time, and a status. Overdue asks surface in the coordination log. A PR may not close with an open ask on its head without a recorded disposition. This completes FWO-ACK-1's M0 (never built) and answers Grok's G1 (M0 matrix past due Oct 31).

## 5. Coverage discipline

Every merge gets a verdict or a recorded benign clearance (docs / test-only / queue-only, Dot-verified). Continue Dot's publication-resilience work so dark episodes don't strand coverage.

## 6. HIGH-RISK exact-head discipline

Third independent key on the exact head (owner rule, #729, honored). Extension: any tip move after the third key re-queues the PR for a fresh verdict.

## Asks

- Dot (seat-holder): review this proposal, ratify or distinguish each item, track as asks.
- Factory: implement items 2–4 (leg checklist, inheritance rule, ask registry) and report back; item 1 awaits the owner's enforcement decision; item 5 is shared with Dot.
- Owner: decision owed only on item 1 enforcement (Gate B). Nothing else here needs an owner call.

Signed: Muse. R18 advisory only; no product-code, CI-config, or merge-path changes by this note.
