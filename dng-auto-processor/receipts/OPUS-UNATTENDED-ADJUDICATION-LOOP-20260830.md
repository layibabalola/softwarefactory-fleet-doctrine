# DNG receipt — the unattended adjudication loop, 2026-08-30

Supporting evidence for `ruling-candidates/unattended-adjudication-loop-r1.md`. Measurements and
failures only; this receipt proposes nothing and grants no authority. Figures were current when
written; re-derive rather than cite.

## What the loop did

One owner directive to work autonomously. Over roughly one working day, on a producer/gate split with
the producer on Anthropic and the terminating gate on OpenAI (`codex exec`, read-only sandbox):

- **23 qualified rulings** produced by the gate, none of which consumed the producer's quota.
- **130 blockers** across 30 rulings consolidated into one ordered list. Dominant family: provenance
  or identity unbound — **44 blockers touching 21 of 30 reviewed artifacts**.
- **8 candidates authored by the coordinating seat; 0 accepted.** Every one was refused at least once.

## The failures, which are the point

- **The day's headline was retracted.** An ordinal-1 ACCEPT reported as "the first review gate closed
  in 25 days" was, once the predicate existed, **72.7% authored by a model other than the admitted
  one** (3 of 11 assistant records on the admitted model). It had been relayed verbatim from an
  upstream record and treated as measured.
- **A coherence check counted `findings`; the schema named the array `blockers`.** Every REVISE scored
  zero findings, and **14 substantive rulings were discarded as incoherent** before anyone noticed. A
  sibling check reads `closedSet` where the schema says `closedSetIncludingNegatives`; it fails open
  and has never fired.
- **A census was reported from a projection truncated to six sorted keys, undeclared.** The correct
  subtotal was 79, not 102 — and the truncation had manufactured the "de facto schema exists"
  conclusion the proposal rested on. The repair introduced a *different* undeclared adjustment
  (excluding its own manifest: 498/256/242 vs the true 499/257/242).
- **A fourth review round, argued as a categorical change rather than a grind, regressed two already-
  accepted dimensions** — reopening a corpus write path that had been closed and source-verified, and
  re-encoding 46 LF terminators as 58 CRLF while claiming byte-for-byte preservation.
- **Substitution rate was reported three times before it was right:** 83% (biased newest-six sample) →
  18% (bucket totals) → **2.1% declared substitution** (8 of 381 routes), with a separate 16% having
  no structured-output turn at all. Episodic, clustering on particular days with long clean runs
  between.

## What the gate caught that would otherwise have shipped

- A prose "the corpus is READ-ONLY" boundary on an autonomous loop pointed at the owner's irreplaceable
  photograph corpus. The ordinary code path computes an XMP path beside each source file and writes a
  sidecar; prose does not stop a writer.
- A derived-brief control claimed to close producer influence over the review question, defeatable four
  ways including a template override that still stamped the run as independently derived.
- A capsule declaring schema `v7` whose own runner accepted only `v6`, making it unrunnable and never
  executed — while 68 structural checks passed, none of which asked whether the runner accepts the
  capsule it ships with.
- The only ACCEPT of the day, overturned at falsification for a check-then-write race.

## What it did not close

Adoption gates remained at **zero** for the entire period and had never moved. The review backlog grew
**13 → 71**. Product code had not landed in seven days and did not land during this period. The loop
made review trustworthy and faster; it did not make the factory ship.
