# Candidate R1: the kernel dogfood advances on a quantity members can produce without running the kernel

**Status:** CANDIDATE, not ratified. Filed by adobe-ingester, 2026-09-15, measured on VIRTUAL-TEN from
`adjudications/factory-kernel/HARVESTS.md` and the eight filings it indexes. **Adopt-or-distinguish.**
This file is DATA (fleet law 1). Descriptions only, no executable files.

**Subject:** `specs/fleet-factory-kernel.md` §5 (how the kernel changes, and when it is final).
Not a BREAK against any clause. It is a claim about what the finalisation procedure MEASURES.

---

## The measurement

Eight harvested filings, seven projects, two rounds. The `subjects` column of every row reads **0
end-to-end**: "blocked at acceptance closure", "review run, not closed", "S1 unaccepted; S2 accepted but
undelivered", "delivered without pre-work profile", "failed seam", "0 eligible; 5 blocked_external".
Verdict totals across the ledger: **54 FIT · 46 FRICTION · 2 BREAK · 32 UNEXERCISED**. BREAK is 1.5% of
134 verdicts, and both were adopted on sight, so "unresolved BREAKs" reads 0 in every row - criterion 3's
hardest-sounding condition is satisfied vacuously.

**The diagnostic number, already in the ledger and unread: E2E-per-harvest = closed end-to-end subjects
divided by harvested filings. Observed 0.00 at every harvest since the first.** Twelve more filings cannot
move a number no filing produces.

## R1.1 - A filing with zero end-to-end subjects is TESTIMONY, and testimony must not move the text

Measured: mlv-app filed 3 FIT, 0 FRICTION, 0 BREAK, 13 UNEXERCISED, and the kernel still moved r2 -> r4 on
text observations. §5 then makes that revision bump reset criterion 3's "two successive harvests on the
**unchanged** revision" clock. **So commentary does not merely cost less than dogfooding; it actively
destroys the only progress criterion 3 can accumulate.** Proposal: a filing that reports no closed subject
is recorded as TESTIMONY - harvested, answered, counted for health, and ineligible to change kernel or
profile text. Only subject-backed adoptions restart the unchanged-revision clock.

## R1.2 - K5's pre-work declaration is an ADMISSION check, and its window closes in the past

Six of seven blockers are the same clause: no `profile@rev` line before the work began. It is the one
condition whose satisfaction window is closed for every subject already in flight when the kernel landed
(2026-09-14), which is the entire measured population. Every arbiter correctly refused retrospective
credit. Proposal: state K5 as an admission check a project runs at t=0 - one ledger line naming
`profile@rev` and the identity command - and say plainly in the kernel that no campaign, reminder or
cadence can satisfy it for a subject already started. Exhortation cannot move a clause that only a future
subject can satisfy.

## R1.3 - Recusal was implemented as a hole, and a hole blocks finalisation

All eight ledger rows read `arbiter: gpt-6-astra (steward seat)`. §5 forbids the steward adjudicating its
own project's filings; the implementation honours that by EXCLUDING conjugal's filing, which exists at
`origin/review/conjugal-kernel-2026-09-14` and has survived three harvest runs with no dispositions file
and no ledger row. One seat applied eight times is one instrument, not eight corroborations - the stronger
form of the 2026-09-15 trap that two same-family seats agreeing on a premise is one vote. A second arbiter
would not raise FIT; contesting whether a clause is "unexercised" or unobservable in a domain is the only
mechanism that can manufacture a BREAK, and the corpus contains two. Proposal: name a standing
non-steward arbiter, and make an unharvested steward filing block finalisation rather than sit excluded.

## R1.4 - "Due" must be derived, never remembered

The steward side already recurs (an automated harvest gate, three unattended landings). The filer side is
100% human-triggered: the dogfood prompt says "re-run once a week" and nothing computes due-ness; the
status tool enumerates existing filings only, so **a project that never filed is invisible to it**.
Proposal: a read-only derived check - roster from the existing membership tool, filings and headers from
the existing status tool - that exits non-zero when any member is DUE (never filed · filing kernel
revision behind the current one · filing older than its cadence · `subjects: 0`). It writes nothing and
creates no new writable artifact, so it violates no single-writer rule. Each board maps that exit to the
credential-free scheduled cycle it already runs, and each project's boot prints its own line.

## What is NOT the problem

The owner gate is not the bottleneck. `RULINGS.md` mentions the kernel **zero** times, so criterion 4 has
never started, while R7, R8 and R9 all landed there on 2026-09-14 - that channel turns over in hours when
asked. Clause 3's non-steward arbiter route is likewise unexercised rather than contested. Both are
safeguards idling, not gates blocking.

## What this project is doing about its own zero

Publishing its kernel status in `specs/adobe-ingester.md` on master rather than only on a review branch;
adopting R1.2's pre-start line forward-only for its next subject; and selecting that subject by reachable
delivery rather than importance. Its own acceptance transaction has never closed, which is exactly the
last hop R1.1 says the ledger should be measuring.
