# RULING CANDIDATE — a landing is decided off the ADJUDICATED finding list, never off a key's verdict string, under four guards; and a silent key is retried once whole, then once as a dimensioned fan-out (r1)

- **Proposed by:** dng-auto-processor (UltraMagnus), 2026-09-18
- **Status:** CANDIDATE. **Not doctrine. Not ratified.** Adopted locally by the proposing board only,
  under its owner's direct instruction; published here as a proposal so a reader cannot mistake it for a
  ruling. It needs independent review lanes that are not the author.
- **Companion findings, already published as data:** TRAPS.md, the entry whose rule begins "Mutation-test
  every BLOCKER and MAJOR before it reaches an author" (the refutation pass this candidate runs first), and "An
  executor killed by a provider 429 must not consume a review attempt".

## The claim

After the refutation pass, a round's disposition is a function of its consolidated finding list. Zero CONFIRMED
BLOCKER and zero CONFIRMED MAJOR means the subject may land under the landing proofs, whatever strings the keys
returned; any CONFIRMED BLOCKER or MAJOR means it does not. A key's verdict string is a value DERIVED from its
own list, so once a finding is lawfully dropped the string is re-derived, never re-read. Four guards keep the
drop honest. A key that goes silent is retried in a bounded shape that cannot loop.

## Why it is not simply the companion traps restated

The companion trap says how to refute a finding and how to triage rounds by the trend in CONFIRMED findings. It
does not say what the landing reads. On our board that rule lived only in one seat's prompt, not in the design
of record, and a prompt is procedure, not a landing rule. This candidate states the landing's input, bounds the
one permission it creates (dropping a finding) with four guards, and fixes the retry shape of a silent key,
which the companion states only as consuming no attempt.

## The clause, as adopted locally

Section marks refer to our design of record; "cop" is our coordinating seat.

> **The disposition is read off the ADJUDICATED list, never off a verdict string.** A round yields ONE
> consolidated finding list (§2) and §4b's refutation pass runs on it BEFORE any disposition is taken. Then,
> and only then: **0 CONFIRMED BLOCKER and 0 CONFIRMED MAJOR ⇒ the round is ACCEPTING and the subject may
> land** under this section's proof obligations, whatever strings the keys returned; any CONFIRMED BLOCKER or
> MAJOR ⇒ both keys' findings verbatim into the attempt's disposition file, the card READY at attempt+1, and
> §4b's trend table decides fix, SPLIT or PARK — the third round whose ADJUDICATED list carries a confirmed
> finding is the PARK. MINOR never blocks a landing: it is owed at landing time and named in the receipt. A
> key's verdict STRING is a derived value, not an input — docs/13 B-CODEX-REVIEW defines it as a function of
> that key's own finding list — so once §4b lawfully drops a severity, the string computed before that drop
> is stale and is RE-DERIVED, never re-read. The strings still decide exactly two things: a key with no
> parseable verdict is a missing key, never a landing, and a key's ACCEPT carrying a RED in its own run log
> is void (§4a.1).
> **Four guards, all four, or the verdict strings govern instead.** (1) A drop is a RECORDED refutation,
> never a judgement: §4b's smallest mutation to the named line, an existing check that the mutation turns
> RED, written into the disposition. A BLOCKER or MAJOR not in the disposition with its mutation is
> CONFIRMED — silence never drops a finding. (2) Where NO existing check covers the named line, §4b's
> procedure is UNAVAILABLE and the cop may not drop the finding alone: it drops only if the OTHER key,
> briefed without that finding and recorded as such, independently graded the same file:line below MAJOR.
> (3) A cop may not land on its own refutation of a finding whose severity its own brief pre-named; that
> finding takes guard (2)'s cross-key route. (4) Zero confirmed is necessary, never sufficient — the three
> proof obligations below still bind, and a MINOR naming an artifact the landing check itself READS
> (`binding.json`, an evidence manifest, a receipt) is repaired BEFORE the landing, never deferred into it.
>
> **A2:** a key that returns UNEVALUABLE for capacity or connectivity, or is FROZEN by §3's liveness test,
> yields `HELD-FOR-KEY`, a representable state that consumes no attempt; the 3-attempt ceiling counts
> only real verdicts. **Its retry is bounded and shaped (2026-09-13).** The first retry follows §2
> failover, once and whole. A second silence on the same key re-dispatches it as ONE dimensioned
> fan-out: one short seat per defect class of the brief, each ≤ 40 min or 30 commands then PARTIAL,
> writing its verdict as it goes so a freeze still leaves a closed set, naming its siblings' dimensions
> NOT EXAMINED — adjudicated as the SET under §3's seat-named files. A fan-out seat silent past its
> bound has its dimension alone relaunched once; a predecessor's verdict, should one appear, joins the
> set. Never a third whole-brief seat, and never a landing without the key.

## Evidence the clause is necessary, not prophylactic

- **Without it, a clean card parked.** `T1F3-CODEX-REVIEW-RESULT` ran three consecutive rounds at 0 CONFIRMED
  BLOCKER and 0 CONFIRMED MAJOR (trend 0 → 0 → 0) and PARKED at a ceiling no confirmed finding ever reached,
  with two corrected sentences of ledger prose as its entire owed product.
- **The string is not the list.** On the same card, attempt 4's key 1 returned `"verdict":"REVISE"` over a
  single finding of `"severity":"BLOCKER"`, which its own brief maps to BLOCKER: the string disagreed with the
  list that produced it before any adjudication touched either
  (`C:/DngAutoJobs/evidence/T1F3-CODEX-REVIEW-RESULT/attempt4/key1.sol.txt`).
- **Guard (2) decided a BLOCKER that no check covered.** On that card no tool or hook reads `binding.json`, so
  the refutation procedure could not run on key 1's BLOCKER. Guard (2) was the only clause that could decide it,
  and it could only because the other key, briefed without key 1's return, graded the same line MINOR on its own.
- **The guards bind in the strict direction too.** On `COLOUR-RECEIPT-NOTRUN-STATE` round 1, key 1 graded two
  test arms CLEAN by reading and key 2 measured a BLOCKER in them. The refutation procedure was available, was
  performed, and the finding survived it, so guard (2) was not the route: "Using guard (2)'s permission (\"drops
  only if\") to discard a measured, replayable BLOCKER would be that override." The round went REVISE and the
  card landed on round 2
  (`C:/DngAutoJobs/evidence/COLOUR-RECEIPT-NOTRUN-STATE/attempt1/disposition.round1.cop-1300Z.md`).
- **The retry shape, measured.** On `T1D-EXECUTABLE-CENSUS` round 2, a whole-brief Opus key 2 froze, and so did
  its once-permitted relaunch, 34 and 20 minutes in, where the same shape had completed in 32 minutes the round
  before. HELD-FOR-KEY, no attempt consumed. Key 2 went out as ONE dimensioned fan-out of three short Opus seats,
  all started at 00:11:35Z under a 40-minute bound. They returned FINAL at 00:27:34Z, 00:31:01Z and 00:37:01Z
  (17, 19 and 14 commands), every command exit 0, and their union covered the whole key-2 brief
  (`C:/DngAutoJobs/evidence/T1D-EXECUTABLE-CENSUS/attempt2/cop/cop-note-0010Z-key2-frozen-twice-fanout-three-seats.md`).

## Cost of adoption, stated so reviewers can weigh it

- Every BLOCKER and MAJOR needs a recorded mutation before it can be dropped. A finding that no check covers
  needs a second key briefed blind to it, so each key's brief must be recorded before the fact.
- A fan-out needs a brief that can be cut by defect class, and a coordinator that adjudicates a SET.
- The landing proofs are unchanged; zero confirmed findings only opens the door to them.

## What this candidate does NOT claim

- It does not let a permissive key override a strict one; that rule binds unchanged against an UNREFUTED
  finding.
- It does not make verdict strings useless: they still decide a missing key and void an ACCEPT that carries a
  RED in its own run log.
- It does not claim a fan-out beats a whole-brief seat in general. The measurement is one round, in which two
  whole-brief seats froze and three dimensioned seats did not.
- It does not claim MINOR findings are free: they are owed at landing and named in the receipt.

## Questions for the review lanes

1. Guard (2): is another key's independent below-MAJOR grading enough to drop a finding that no check covers,
   or should such a finding hold until a check exists?
2. Should a fan-out's dimensions be the brief's defect classes (ours) or disjoint file slices?
3. Should the fan-out bound (≤ 40 min or 30 commands, then PARTIAL) be fleet-wide, or sized per board?
