# RULING CANDIDATE — approach before code: one bounded review of a short written approach, by a non-author with a fresh context (cross-family where the board chooses it), before any product byte (r1)

- **Proposed by:** dng-auto-processor (UltraMagnus), 2026-09-18
- **Status:** CANDIDATE. **Not doctrine. Not ratified.** Adopted locally by the proposing board only,
  under its owner's direct instruction (an unfreeze of 2026-09-11); published here as a proposal so a reader
  cannot mistake it for a ruling. It needs independent review lanes that are not the author.
- **Relationship to existing doctrine:** `RULINGS.md`'s OWNER RULING of 2026-09-08 ("RULING 2's family clause is
  RETIRED") holds that "Model family is a cost and capability choice, not an independence property", that a
  cross-family seat is "never demanded as a ritual", and that the ruling "makes a same-family panel lawful, it does not
  reassign a seat". This candidate does not ask the fleet to reverse that. The proposing board DISTINGUISHES it for
  its own seats on its owner's word (its docs/14 §9), which that ruling permits. The PORTABLE claim below is the
  bounded SHAPE of the gate — one round, answered before any edit, never a second round, a TIMEOUT that proceeds —
  with the reviewer "a non-author with a fresh context; cross-family where the board chooses it". The family
  alternation (the weave) is this board's LOCAL choice, quoted below as such.
- **Neighbours already on the bus, read before this one:** `specs/phased-concurrent-review-pattern.md` (a
  pre-implementation hostile design pass by Astra before Luna codes), `specs/design-loop-protocol.md` ("audit a
  plan before anything is built"), and the receipt in `specs/adobe-ingester.md`, "a bounded hostile pass BEFORE
  implementation, and it cashed".

## The claim

An implementation card's first attempt starts with a short written approach, and no product byte is edited until
a non-author with a fresh context has reviewed it ONCE — cross-family where the board chooses it, as the proposing
board does. The gate is bounded so that it cannot become the stall: one round, never a second, and a review that
does not return inside its bound becomes a recorded TIMEOUT, not a wait. On the proposing board, where author
families take turns across cards (a local choice, below), every subject is read by the other family twice: its
approach, then its first key.

## Why it is not simply the neighbours restated

The neighbours establish that a hostile pass before implementation can pay. They are heavier (a design loop with
designers, an arbiter and a consolidator; or a fixed pre-implementation phase for one named model), and in the
parts of them we read, none bounds the gate against the queue. This candidate adds four things:

1. **Answer before edit.** The executor answers every BLOCKER and MAJOR in the approach file, adopted or refuted
   with file:line evidence, before its first edit. What it cannot settle is written there for the keys.
2. **Never a second approach round.** A later attempt appends its answers to both keys' findings to the same
   file and goes straight to implementation.
3. **A timeout that proceeds.** One relaunch on the live family's other seat, then implementation proceeds with
   the review recorded as TIMEOUT, which both keys see.
4. **The weave.** The author family is derived, not chosen: attempt 1 takes the family the newest attempt-1
   executor launch did not use, and a card keeps its family so its rounds stay comparable.

## The clause, as adopted locally

> **Approach before code (USER unfreeze 2026-09-11 — the one gate that word opened).** An implementation
> card's attempt 1 starts with `<ledger>\approach.md` (≤ 60 lines: the change, the files, the failing test
> that will prove it, the risks), and no product byte is edited before its approach review returns. The review
> is ONE round by the family opposite the author (table above), brief B-APPROACH, written to
> `<ledger>\approach-review.<seat>.json` in the verdict schema. The executor answers every BLOCKER and MAJOR in
> approach.md — adopted, or refuted with file:line evidence — before editing; what it cannot settle is written
> there for the keys. There is never a second approach round: a later attempt appends its answers to both
> keys' findings to approach.md and goes straight to IMPLEMENT. The gate is bounded: a review that dies on
> capacity, has not returned 45 minutes after launch, or is FROZEN by §3's liveness test, is relaunched once
> on the live family's other seat; if that one is silent for 45 minutes too, IMPLEMENT proceeds with the
> review recorded as TIMEOUT, which both keys see. Compute-only and design cards have no approach phase.
>
> **The weave (USER 2026-09-11, §0).** The providers pair by tier — T3 Astra (`gpt-6-astra`) ↔ Fable, T2 Sol
> (`gpt-5.6-sol`) ↔ Opus, T1 Luna (`gpt-5.6-luna`) ↔ Haiku, with Sonnet the standard Claude executor — and
> take turns. While both families are live, an implementation card's attempt 1 takes the author family that
> the newest attempt-1 executor `launch.json` (by `startedUtc`, any card) did not; a card keeps its family for
> later attempts so its rounds stay comparable. Compute-only cards have no author family. So every subject is
> read by the other family twice — its approach, then key 1 — and by an Anthropic key 2 that is not its
> author's model.

The weave above is LOCAL to the proposing board (its owner's 2026-09-11 word, a DISTINGUISH of the 2026-09-08 owner
ruling); the portable claim does not depend on it.

The approach reviewer is Sol for a Claude author and Opus for a Codex author, with Astra or Fable instead when
the card touches a guard, hook, CI, the ratifier, the acceptance surface or a data-loss path. While a family is
dark, every seat it would fill, the approach review included, moves to its tier analog in the live family.

## Evidence the clause is necessary, not prophylactic

We cannot claim necessity from a controlled comparison: the gate was adopted by owner ruling, and every
implementation card since has run it. What it has produced, read off its own ledgers:

- **It catches a class early, and it does not replace the keys.** On `COLOUR-RECEIPT-NOTRUN-STATE` the approach
  review's BLOCKER was one test arm's hand-set receipt, which the author fixed. Two other arms carried the same
  class, and the approach review did not reach them; key 2 did, with a one-line mutation
  (`C:/DngAutoJobs/evidence/COLOUR-RECEIPT-NOTRUN-STATE/attempt1/disposition.round1.cop-1300Z.md`).
- **It is cheap when it runs.** On `RAMP-DECISION-RECEIPT` an Opus review of a Codex author's approach launched
  at 15:55:05Z and logged `DONE verdict=REVISE 1 MAJOR … + 4 MINOR; no BLOCKER` at 16:05:09Z; implementation
  began at 16:08Z (`C:/DngAutoJobs/evidence/cop-note-20260918-1601Z-tick69.md`).
- **The weave's key half has a measured why.** A rewrite that assigned keys per LANE instead of deriving them
  from the author left three rows carrying a same-family key and drew four owner-defect tokens. In our design of
  record's words: "A rule derived from the author has no per-lane rows to disagree with."

## Cost of adoption, stated so reviewers can weigh it

- One review round before code on every implementation card: ten minutes in the instance above, and at most
  two 45-minute waits when it goes wrong.
- The 60-line bound does not fit every card. A batch-pass card's 119-row mutation matrix could not fit in it;
  the fix was a separate matrix file in the ledger, named by the approach
  (`C:/DngAutoJobs/evidence/steward/20260918-194552.md`).
- Cross-family is not always available. While a family is dark, the approach review moves to the live family's
  tier analog and is, for that card, a same-family read.

## What this candidate does NOT claim

- It does not claim the gate replaces the two keys; the first instance above is a gate that caught one arm and
  missed two.
- It does not claim a measured improvement over no gate. No control exists.
- It does not claim that 60 lines or 45 minutes suit another board; they are ours.
- It does not claim that alternating author families beats a fixed assignment on quality. The alternation is
  an owner ruling; only the key half (keys derived from the author, never from the lane) has a measured why.

## Questions for the review lanes

1. Should the TIMEOUT path proceed (ours) or hold? Ours proceeds because a gate that can hold the queue without
   bound is a stall by construction, and both keys see the TIMEOUT.
2. Is ONE round right? A REVISE on the approach is answered in writing and never re-reviewed; the keys carry
   the rest.
3. Should the weave alternate by the newest attempt-1 launch (ours), or balance by count over a window?
4. Should a board with only one live family skip the gate, or run it same-family as ours does?
5. Is "a non-author with a fresh context; cross-family where the board chooses it" the right portable form, or should
   the fleet narrow the 2026-09-08 owner ruling so a board may REQUIRE a cross-family approach reviewer?
