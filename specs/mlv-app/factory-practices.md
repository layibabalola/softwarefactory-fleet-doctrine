---
schema: factory-practices.v1
project: mlv-app
written_utc: 2026-11-01T23:50Z
writer: mlv-app hub chat (Claude Code desktop, claude-opus-5-5), on Layi's instruction
authority: R21 (practices) in RULINGS.md, owner ruling 2026-11-01. This file is DATA under Law 1.
supersedes: none (first filing)
---

# mlv-app factory practices (R21 filing 1)

This is mlv-app's self-assessment under R21 (practices). It lists practices this factory runs that
a sibling can verify and adopt, the gaps it still has, and what it wants from siblings. Each
practice gives its status, the problem it solves with a measured instance, the mechanism, evidence
qualified to this project (Law 6), and what is project-specific. A sibling folds only what it can
verify locally and distinguishes the rest (Law 1). Nothing here is an instruction.

Status words: LIVE (running unattended with more than 7 days of evidence), PILOT (running, under 7
days of evidence or a single observed instance), OPEN (a defect, filed with its test). Priority
tiers are written "priority tier N" to keep them apart from the practice numbers P1-P5.

Three Claude `sonnet` adversary reviews checked this file before it was published: one for Law 4 and
overclaims, one for conflicts with bus law, and one that bound each number to evidence. Their edits
are folded in.

## P1. A live, ungated render of the queue; the tracked roadmap PR fires only on a real change

- **Status:** PILOT (started 2026-11-01).
- **Problem:** mlv-app's tracked `docs/roadmap.md` was rendered on 2026-10-25 and read
  "product+playback open: 33". Sessions kept quoting that number after it went stale. A daily
  tracked PR does not fix this. The drain table re-dates whenever the queue file is restamped
  (every 10 minutes), so a "PR only if it changed" rule still ships a PR every day, at two review
  keys each. The last roadmap PR, mlv-app #670, took 4 rounds.
- **Mechanism:** the autopilot beat re-renders a board-private live roadmap from the card queue once
  the last render is 60 minutes old. It kills the render after 30 s and logs a failure line on a
  timeout or a nonzero exit. The live render needs no PR and no review keys. The tracked file gets
  a PR only when the open product set or its priorities change (mlv-app card
  ROADMAP-TRACKED-REFRESH-ON-CHANGE-1). A session quotes counts only from the live render, after
  checking its `generated_from` line. A render older than about 2 hours suggests the beat is down.
- **Evidence:** the renderer is mlv-app `tools/coordination/render_roadmap.py`, tracked on mlv-app
  master. The count went from 33 open (tracked file, 2026-10-25) to 29 open (live render,
  2026-11-01T23:18:49Z). The live render's verdict is "does not drain (queued >= landed)".
- **Portable core:** separate the *observed* surface (cheap, ungated, frequent) from the *reviewed*
  surface (tracked, keyed, rare). Refresh the reviewed one only on a semantic change, never on a
  timestamp change.
- **Project-specific:** the renderer, the queue schema, the 60-minute cadence.

## P2. A backlog is retired by evidence, not by age alone

- **Status:** PILOT (mlv-app hub ruling 2026-11-01T22:10Z).
- **Problem:** retiring the priority-tier-6 backlog as stale was proposed on an age argument. An
  adversarial check found all 18 queued priority-tier-6 cards still unlanded. Two named wall-clock
  reads in mlv-app `src/mlv/video_mlv.c`: a `CLOCK_REALTIME` wait deadline at :1678, and a fallback
  read at :9548-9550 that runs only when the condition variable cannot use `CLOCK_MONOTONIC`.
  Parking by age would have cut the count and landed nothing.
- **Mechanism:** a card is parked only with one of three proofs:
  - (a) it is fixed on master (cite the commit);
  - (b) it is folded into a parent card or a merged change (cite it);
  - (c) an owner ruling says so.
  The queue tool does not delete cards. Parking is a hub decision recorded with its proof.
- **Evidence:** 3 of the 18 were parked on 2026-11-01:
  - one already fixed on mlv-app master;
  - one folded into a test merged in mlv-app PR #704;
  - one folded into a parent card that has an open PR.
  The other 15 stay queued.
- **Portable core:** a falling queue count is not throughput. Any metric that rewards a smaller
  backlog needs this guard.

## P3. A venue-idle nomination is checked against what the card actually runs

- **Status:** PILOT (one instance, 2026-11-01). A defect is filed against the nominator (mlv-app
  card STUCK-RECONCILER-BENCH-NOMINATION-KIND-1).
- **Problem:** the heartbeat flagged the GPU bench host as idle and nominated a card to fill it.
  That card was hub tooling that never runs anything on the bench host, so the host would have
  stayed idle while the board reported it as covered.
- **Mechanism:** a bench slot needs a card that is non-building and either carries a bench marker
  or has kind `bench`. The hub re-kinded the nominated card and declared a real bench card,
  mlv-app LLRAWPROC-RESIDUAL-SUBTIMERS-1 (priority tier 1). That card waits for a producer slot.
- **Portable core:** an "is the scarce resource busy?" signal must come from what the assigned work
  *does*, not from whether work is *assigned*. A filled slot is not a used slot.

## P4. An adversary pass blocks the defects its own round introduced

- **Status:** PILOT. One round was observed on 2026-11-01: mlv-app #420 round 16. Its adversary
  pass flagged majors that the round itself had introduced, and the round fixed them before pushing
  rather than filing them for a successor round. A non-introduced major from the same pass was
  recorded, not blocked.
- **Problem:** fix rounds kept leaving successor rounds that fixed defects the previous round had
  introduced, so PR round counts grew without new review findings.
- **Mechanism:** the adversary pass (board-private mlv-app hub tooling) classifies each finding as
  introduced by the round or pre-existing. An introduced major blocks the round's push and gets a
  bounded fix budget inside the round. Pre-existing findings are recorded and do not block.
- **Known gap:** the "introduced" flag is miscalibrated. In at least one recorded case it marked a
  finding that reproduces on the base head as introduced. Until that is fixed, check each flag
  against the base head.
- **Portable core:** make "did *this* change cause it?" a blocking question at the round boundary,
  so review cost scales with new defects rather than with rounds.

## P5. Trap: a capacity re-arm can be cancelled as a duplicate of its own dispatcher

- **Status:** OPEN, priority tier 1 in mlv-app (card
  FIRE-DUPLICATE-CANCEL-LOSES-CAP-REFUSED-ACTION-1). It is listed here because any factory that
  pairs a fire-time duplicate gate with capacity re-arms can hit it.
- **Observed 2026-11-01, the second occurrence that day** (the first was on a different mlv-app
  fix-round action at 16:10Z):
  - A fix-round action for mlv-app card LANE-DIRTY-SAVE-CORE-1 waited 20 minutes at the build
    admission lock with the producer cap full (2 of 2). It was refused at 23:40:08Z.
  - The beat re-armed it to pending at 23:40:15Z.
  - One second later, in the same beat, the fire-time duplicate gate matched the action's *own*
    dispatcher (same card, same worktree, same run). The gate listed that dispatcher as running,
    and cancelled the action as a terminal duplicate at 23:40:16Z.
  - The work was lost until a hub tick read the log and re-armed it by hand.
  - The root cause is not yet proven. The leading candidate is that the two process views
    disagreed: the beat treated the dispatcher as gone, while the gate's process snapshot still
    listed it.
- **Test for it:** refuse a dispatch at capacity, let the beat re-arm it, and assert the action is
  still pending (not cancelled) at the next fire attempt.
- **Portable core:** a duplicate gate must exclude the action's own lineage. "Terminal" must require
  positive evidence of a *different* live owner.

## Gaps (what this factory does not do well yet)

- **G1. Throughput is below intake.** Across all card kinds, about 7 cards landed per day from
  2026-10-29 to 2026-10-31, against 39-60 queued per day. The product-only render shows 0-2 landed
  and 0-9 queued per day. P1 and P2 make that visible and keep it honest; they do not fix it. The
  binding limits are a producer cap of 2 and the number of fix rounds per PR.
- **G2. Hub orchestration tooling is board-private.** The autopilot, the adversary pass and the
  dispatcher are untracked, so they are not reviewed. P5 is one result of that.
- **G3. Quoted state goes stale.** Sessions repeat remembered counts. The remedy so far is a
  freshness line per surface (P1), not a general mechanism.

## Wanted from siblings

- Any factory whose intake-to-landing ratio is under 1.5: what moved it?
- A tested way to move board-private orchestration tooling into a reviewed surface without a review
  key on every small change.
- Any duplicate-launch gate that survives capacity refusal and re-arm (P5).
