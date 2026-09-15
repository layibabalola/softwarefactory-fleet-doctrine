# Design-loop protocol — audit a plan before anything is built (conjugal, 2026-09-13, Bachelor)

**Status:** PROPOSED portable pattern; zero runtime authority until a project adopts or distinguishes it (law 2).
**Source:** `C:\code\Conjugal\docs\architecture\approach-a\DESIGN-LOOP-DOCTRINE.md` (tracked; scores in `scores.csv`).
**Evidence:** fifteen scored rounds (2026-09-12/13) designing Conjugal's multi-provider orchestration ("Approach A"):
composite 78.0 → 64.5 (layered documents) → 74.8 → 77.8 → 80.6 → 80.9 → 82.2 → 83.7 (single document + the loop below),
stopping rule fired at Round 15. Companion artifact: `specs/conjugal-approach-a-v7.4.md` (the design itself, open for fleet review — §7).

**Distinguished from existing specs:** `parallel-consensus-swarm.md` is the *family-internal adversarial merge* stage here;
`adversarial-swarms-and-doctrine-publishing-standard.md` (Haiku swarms) is the *classifier / stopping-evidence* stage here.
This spec adds the stages neither covers: anchored patches, a single arbiter naming losers, a single consolidator, a
consistency lint that gates the panel, a pinned rubric, and a stopping rule with hand-off.

## 1. Seven findings that survived contact with evidence

1. **Layered documents regress; one self-contained document converges.** Reviewing "v6.1 + patch + patch" fell 78 → 64.
   One consolidated file rose monotonically. Supersession chains are where contradictions hide.
2. **Consistency lint is a different job from review, and it gates the panel.** Every round the lint found a fatal-class defect
   (an idempotency/counting predicate rejecting valid events; a sum that did not add) that eight reviewers scored *around*.
3. **Designs are patches, not essays:** `fix | REPLACES: <exact anchor> | PROOF: <scenario>`. An unanchored idea is a cost.
4. **Adversarial within family before cumulative.** Two instances of the same model with disjoint slices produced different
   winners. Independence is the setup, not the vendor.
5. **One arbiter, with named losers and counterexamples.** Consensus without losers is a word-count leak.
6. **A hard size cap forces deletion of restated rationale** (12,906 → 14,039 → 12,996 words under a 13,000 cap).
7. **A stopping rule with a comparability pin:** |Δ| < 2 for three consecutive rounds, `rubric_id` pinned, seat spread
   narrowing as the convergence signal. The design stage has a ceiling only practice can pierce; reach it fast, hand off.

## 2. The loop (domain-agnostic)

artifact → adversarial designers (anchored patches, disjoint slices) → ONE arbiter (winners/losers) → ONE consolidator →
consistency lint (cross-family) → one fix pass → blinded multi-family panel, pinned rubric → stopping rule → hand-off.
Only the *lint* (continuity/motivation/tone for creative work) and the *proof* (read-through vs scenario) change per domain.

## 3. Model posture (measured)

| Role | Who | Why |
|---|---|---|
| Arbiter | highest-inference model, high effort, **singleton** | a second arbiter produces a merge, not a decision |
| Consolidator / coherence gate | strongest long-context model, **singleton** | coherence is a single-mind property |
| Designers | every family, ×2 for the strongest, disjoint slices | different winners per slice; overlap costs duplication |
| Lint | two families | each finds 7–23 items the other misses |
| Panel | 8 seats across every family the inventory holds (Round 15 seated 2: Claude ×5, Codex ×3), cheap seats ×3 for breadth; record families **as seated** (RULINGS R9.4) | cheap seats find well, attribute badly — require quotes |
| Classifier / stopping evidence | cheapest model, swarm | predicted flat rounds accurately; never designs |

Swarm high-inference models by *slice* for coverage, never by count; adjudication is one seat.
Record `panel_families` from the families whose seats actually completed; never infer it from a planned roster.
Single-provider projects: run designers/lint/panel with two instances at different effort and say so in a `providers:` header.

## 4. Fragmentation vs review

Navigation copy fragmented by section (size-gated); review copy monolithic (~13k words). Fragmenting the review copy
reintroduces finding 1. Cheap seats are limited by reasoning, not context — give them the rubric, the blockers, and demand quotes.

## 5. The under-one-hour falsifier

Before any owner decision, run the cheapest test that isolates the assumption everything rests on (Conjugal: Stage S —
5 writers × 10,000 appends + 200 ref-CAS races on NTFS). A failure invalidates a protocol, not the design.

## 6. Traps met while running it (tests in TRAPS.md, 2026-09-13)

zero-tool-call derivation; a flag that existed only on a replaced git lineage; relative paths in printed commands;
a SessionStart hook whose non-zero exit hid its own output; an in-session auth probe 10× slower than the terminal's.

## 7. Fleet review of `specs/conjugal-approach-a-v7.4.md`

- Review **against your own repo as the test bench**. Return anchored findings only — `§ | quote | defect | REPLACES | PROOF` —
  never prose, to a single-writer file `adjudications/approach-a-design/<project>.md` with a `providers:` header.
- Conjugal holds the arbiter/consolidator seat and folds fleet findings as "Round F<n>" (`bootstrap/PROMPT-3-harvest.md`);
  the rewritten spec keeps this path so filers' references stay valid, and each filing gets
  `adjudications/approach-a-design/<project>.dispositions.md`. Open filings: `python tools/harvest-status.py approach-a-design`.
- Nothing here grants runtime, adoption, or launch authority.
