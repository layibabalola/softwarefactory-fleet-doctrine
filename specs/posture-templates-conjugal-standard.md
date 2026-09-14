# Conjugal Standard Posture Template

**Status:** PROVEN. Delivered Approach A from 78.0 to 83.7 composite over 15 rounds (Conjugal). Run in full on a
second project's bench 2026-09-14 (magic-lantern_dannephoto): 17/17 lanes, stages B-D in 5 minutes.

**Requirement:** Both Claude and Codex families available (machine inventory, `~/.claude/machine-inventory.yaml`).

**Executable form:** `tools/review-posture/` — `roles.json` is this table as data, `run.sh` dispatches it, and
`tests/test_review_posture.py` fails if the two name different roles. **Change this table and `roles.json` together.**

## Roles and models

| Role | Model | Family | Count | Reads | Purpose |
|------|-------|--------|-------|-------|---------|
| **Designer-Scope** | Opus | Claude | 1 | subject, bench | Slice: architecture, claims, mutations |
| **Designer-Verify** | Sol | Codex | 1 | subject, bench | Slice: verification, adoption, capacity |
| **Lint-Consistency** | Haiku (Claude) + Luna (Codex) | Claude + Codex | 2 | subject | Cross-family: contradictions between sections |
| **Arbiter** | Astra | Codex | 1 | designers **and** lint | One winner per defect class; names losers with counterexamples; rules KEEP/DROP on each lint item |
| **Consolidator** | Fable | Claude | 1 | arbitration | Weaves the winners into one coherent adjudication body |
| **Panel** | Fable, Opus, Sonnet×3, Astra, Sol, Luna | Claude + Codex (see families below) | 8 | subject only | Blinded scoring on the pinned rubric's six dimensions; three quoted blockers each |
| **Classifier** | Haiku | Claude | 3 | consolidated findings, panel scores, seat-stripped blockers | TEXT vs DESIGN, grounded, must-fix, stopping evidence, ceiling; 2-of-3 consensus; never designs |

## Dispatch pattern

1. **Stage A** — Designers (disjoint slices) and Lint (both families) in parallel.
2. **Stage B** — Arbiter, reading designers **and** lint, in parallel with the Panel, which reads only the subject.
3. **Stage C** — Consolidator weaves the arbitration.
4. **Stage D** — Classifier swarm over the consolidated findings, the panel scores and the seat-stripped blockers.

Every lane is a provider-CLI process (`claude -p`, `codex exec`) judged complete only by its `LANE-COMPLETE` sentinel
(RULINGS R2). The consolidator runs as a lane here; in Conjugal's own design loop it edited the design document in
place, which a fleet review — filing findings, not rewriting another project's spec — does not do.

## Posture completeness is measured (RULINGS R9)

A filing may carry this posture's name **only when every lane of every role above cleared the sentinel.** Otherwise it
reads `conjugal-standard-PARTIAL (<n>/17 lanes; missing: <role n/m>; …)`. The panel and the classifier are not optional
under this name: a run may skip them, but then it is PARTIAL and says so. Cross-family validation (R3) is a separate
claim and does not imply completeness.

*Measured:* the lane orchestrator's first runner dispatched designers, lint and an arbiter that saw no lint (5/17) and
printed `posture: conjugal-standard`. The full posture on the same subject and bench kept 6 + 1 of the 16 findings
that run filed and rejected 9 with counterexamples. Fidelity to the posture changes the findings, not only the label.

## Panel families

This table used to say the panel is "3 families". Conjugal's own Round 15 panel — fable, opus, sonnet×3, astra, sol,
luna — was **2 families**, and so is every inventory probed on the fleet so far. Seat the families the machine
inventory has; record `panel_families` as measured in the filing header. A third family is added to the roster only
after it answers a sentinel challenge in the inventory (R5), never by hand.

## Rubric pinning

The panel scores against a rubric file (`tools/review-posture/rubrics/`; Conjugal R15's by default).
`rubric_id = sha256(canonical JSON of {dimensions with definitions and weights, seat roster, blinding, composite rule})`.
The contract is committed beside the filing as `<project>.rubric.json`. Two panels are comparable only when their
`rubric_id`s match; changing the blinding (for example, withholding score history) changes the id by design.
Composites are recomputed from the dimension numbers, never taken from a seat's stated average.

## Fallbacks

**If only Claude available:** Designer-Scope (Opus) + Designer-Verify (Sonnet), Lint (Haiku), Panel and Classifier
from Claude seats. No Arbiter (both families required). Posture is PARTIAL; `cross_family: NO-CROSS-FAMILY-VALIDATION`.

**If only Codex available:** Designer-Scope (Luna) + Designer-Verify (Sol), Lint (Astra), Panel from Codex seats.
No Arbiter; no Classifier (Haiku). Posture is PARTIAL; `cross_family: NO-CROSS-FAMILY-VALIDATION`.

**If no auth for either family:** FAIL; do not downgrade or invent posture. Report the constraint violation.

## Key properties

- **Disjoint slices:** designers divide the spec; different winners per slice.
- **Cross-family lint feeds the arbiter:** each family finds what the other misses, and the arbiter rules on each item.
- **Arbitration names losers:** one winner per defect class, each loser with a counterexample grounded in the subject.
- **Consolidation:** one Fable consolidator, singleton, weaves the winners.
- **Panel blinded and pinned:** independent seats, no score history, retained rubric contract.
- **Classifier at 2-of-3:** cheap seats find well and attribute badly; the quorum absorbs a misattribution.
- **Stopping rule:** after three comparable flat rounds (Δ 0–2, matching `rubric_id`), hand off to the next phase.

## Integration with Dispatch Trigger

See `specs/dispatch-trigger-standard.md` for how to wire this posture into automatic agent spawning, and
`bootstrap/lane-orchestrator.md` for the orchestrating session's procedure.
