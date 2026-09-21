# Ruling candidate: JEV-FD-C2-ADVISORY-1 — advisory shown to a human (R2)

Status: **PROPOSED ONLY — NOT YET A RATIFIED RULING.** Supersedes r1 (`07f0ecc`,
sha256 `6db3791af47c116218b85c60852009f70851dde8c460eaaaf8a054aa4687d1dd`), which two
blind cross-family seats **vetoed** — receipts: `ruling-candidates/jev-fd-c2-human-advisory-r1.receipts.md`.
Both seats found the same root defect: verdict-word leakage in `state.review.notes`/`blockers`
reached both Jev and the blind judges, so neither the fidelity run nor the adjudication run was
blind. This candidate corrects that with a new state construction (`state2`) and recomputes every
figure from the corrected data. Per `RULINGS.md` R10.2, no project may record `ADVISORY` for FD-C2
until §2.4 of `specs/fleet-jev-shadow-mode.md` has run (fidelity AND blind adjudication AND a
register row) **and a further ruling names the project**; this candidate names
**softwarefactory-fleet-doctrine**, its own §5 row, for that purpose.

## 1. Proposed `RULINGS.md` entry (exact text)

> **JEV-FD-C2-ADVISORY-1 — advisory shown to a human, for project
> `softwarefactory-fleet-doctrine` (§5 row).** For the exact recorded FD-C2 question `verdict`
> (`questions/q-fd-c2.mjs` v1, blob `7137a360e7a5416153c1d34f1a7cb76df4bb2324`), with state
> construction `state2` (`questions/q-fd-c2-state2.mjs`, `stateVersion 'state2'`,
> `questionSetVersion 48e37f0af89d8e72`; strips any line containing a verdict token before the
> state reaches Jev or a judge), permit a **manually invoked, local, human-read report** that
> prints, beside each cos-feedback review's own written `verdict:` line, Jev's reading and its
> probability under this question module and this state construction. The report may widen human
> review only. It may not write cos-feedback, alter any verdict, change a queue, acknowledge
> doctrine, influence any gate, or grant merge/release authority. This licence requires the
> recorded fidelity and blind-adjudication receipts (§2) and **lapses immediately on any change to
> the question text or to `state2`'s construction** — a lapsed licence reverts to shadow-only until
> re-evidenced under a new version.

## 2. Evidence

All figures from `C:\code\jev-plan` commit `1587b73`.

| Run | Numbers | Source | SHA-256 |
|---|---|---|---|
| State construction | `state2`: `stateVersion 'state2'`; deletes any line containing a verdict token; 49/131 samples had removals (59 lines) | `questions/q-fd-c2-state2.mjs` | `316df5f681be45aae0444e8423c652f16ca6cd602825e379a9ef4fde211beef8` |
| Fidelity (Jev vs. written `verdict:`, 131 rows, incumbent-rule gold) | **114/131 = 87.0%** (corrected; the r1 figure of 90.1% was leak-inflated), vs. 71.0% majority baseline; 92.9% at confidence ≥0.8 (n = 99) — a selected slice, not blind correctness | `reports/p0-fd-c2-state2.json` | `b1aa042a657e3a4606193334bfd1be415abdfdba81853a82984971c981d11e72` |
| Blind model-consensus adjudication of the 17 disagreement rows (judges `anthropic/claude-sonnet-5` + `openai/gpt-5.6-terra`, blind to Jev and to the written verdict; adjudicator `google/gemini-3.8-flash`; 2 of 17 rows independently audited) | 15/17 decided, 2 `UNDECIDABLE`. On the 15 decided rows: Jev agrees with the blind consensus **9/15**; the blind consensus itself agrees with the original written verdict in only **6/15** — i.e. blind re-review corroborated the incumbent label in fewer than half the decided disagreements | `adjudication/fd-c2-state2.labelled.jsonl` | `f0db0a62cbbe0684b867a8e3124e232071f9842791312e72b0d99959ce946321` |
| Rescored (mixed reference: incumbent labels plus the 15 decided consensus labels) | 123/131 = 93.9%; 123/129 = 95.3% excluding the 2 undecidable rows | `reports/p0-fd-c2-state2-rescored.json` | `fa916496c9ce3889e97622842487d38454686612de29706e21151f6139a76905` |
| Question module v1 (unchanged from r1) | pinned by git blob, no `questionSetVersion` export | `questions/q-fd-c2.mjs` | `8cccfa3355e17a105e5033844fdfe41b6ca2ad919f86d8a3a792552a833e73c3` |
| Admissibility | Model-consensus labels count as evidence and are reported as `model-consensus`, never `human` | `C:\code\JEV_PLAN\owner-decisions.md`, row (a), 2026-09-20 | — |

## 3. What this candidate does NOT claim

- **No human labels anywhere.** Every number above is model-consensus against two model judges
  plus one model adjudicator, admissible only under owner-decisions.md row (a), reported as
  `model-consensus`, never `human`.
- **87.0% is fidelity against the (state2-cleaned) written verdict, not blind correctness on 131
  rows.** Blind correctness is measured only on the 15 decided disagreement rows (9/15), plus 2
  audited and 2 undecidable.
- **123/131 and 123/129 are mixed-reference rescores** (116 never-adjudicated incumbent labels plus
  15 decided consensus labels), not a 131-row or 129-row blind-adjudicated cohort.
- **Seventeen disagreement rows, not a fresh blind cohort.** The Q6 promotion bar (a new,
  independently adjudicated 100-row correctness cohort, ≥95/100, ≥10 per verdict class, no silently
  dropped row) remains unmet; this evidence is one order of magnitude short of that cohort size.
- No claim that this display authorizes merge, release, or any queue/gate action.

## 4. Falsifier (executable)

```
node "C:\code\jev-plan\harness\jev-validate.mjs" \
  --questions questions/q-fd-c2-state2.mjs \
  --samples <fresh cos-feedback cohort of >=100 rows, extracted by extractors/extract-fd.py from bus commits newer than 2026-09-20> \
  --out <report>
node "C:\code\jev-plan\harness\blind-adjudication.mjs" <report's disagreement sheet>
node "C:\code\jev-plan\harness\rescore.mjs" --label-field modelLabel --label-source model-consensus
```

**Withdrawn** if fidelity on that fresh cohort is below 85%, or Jev-vs-consensus on the decided
disagreement rows is below 50%. A withdrawal reverts FD-C2 to shadow-only pending re-evidence.

## 5. Ratification

Per the owner ruling of 2026-09-06: two blind, cross-family seats, neither told the other's
identity or verdict in advance, each bind a verdict to this file's own SHA-256 (computed post-write,
pre-commit, over the exact bytes at this commit) and record it in a receipt filed beside this
candidate, not edited into it. This candidate does not self-ratify.

---

**Candidate file SHA-256:** computed post-write, pre-commit, and recorded in the commit that adds
this file.
