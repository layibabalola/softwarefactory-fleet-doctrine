# Ruling candidate: JEV-FD-C2-ADVISORY-1 — advisory shown to a human (R1)

Status: **PROPOSED ONLY — NOT YET A RATIFIED RULING.** Per the owner ruling of 2026-09-06,
ratification is by two blind cross-family adversarial seats bound to this file's own SHA-256
(below); a verdict receipt is recorded beside this file, not inside it. Per `RULINGS.md` R10.2, no
project may record `ADVISORY` for FD-C2 until §2.4 of `specs/fleet-jev-shadow-mode.md` has run
(fidelity run AND blind adjudication AND a register row) **and a further ruling names the
project** — this candidate's text is offered as that further ruling.

Origin: Conjugal's kernel-dogfood FD-C2 packet (bus row: `specs/fleet-jev-shadow-mode.md` §5,
softwarefactory-fleet-doctrine — "FD-C1 seam detection; FD-C2 CoS verdict validator" — "shadow mode
only LOGS a proposed additional owed entry ... it never adds one to the queue, never removes one,
and never touches a verdict"; FD-C2 row itself: `cmdExportCheck` hook, out-of-tree sidecar).

---

## 1. Proposed `RULINGS.md` entry (exact text)

> **JEV-FD-C2-ADVISORY-1 — advisory shown to a human.** For the exact recorded FD-C2 question
> `verdict` (`questions/q-fd-c2.mjs`, question-set version **NONE** — this v1 module exports no
> `questionSetVersion`; pinned instead by its git blob `7137a360e7a5416153c1d34f1a7cb76df4bb2324`
> at `jev-plan` commit `ed5a21a`), state-construction (`buildState = (sample) => sample.state`,
> unchanged from that blob), and renderer, permit a **manually invoked, local, human-read report**
> that prints, beside each cos-feedback review's own written `verdict:` line, Jev's reading and its
> probability. The report may widen human review only. It may not write cos-feedback, alter any
> verdict, change a queue, acknowledge doctrine, influence a gate, or grant merge/release authority.
> This licence requires the recorded fidelity and blind-adjudication receipts (§2 below) and
> **lapses immediately on any change to the question text (`questions.verdict.instructions` or
> `.criteria`) or to state construction (`buildState`)** — a lapsed licence reverts to shadow-only
> until re-evidenced under a new version.

## 2. Evidence

| Run | Numbers | Source |
|---|---|---|
| Fidelity (Jev vs. the written `verdict:`, 131 rows, incumbent-rule gold) | **118/131 = 90.1%**, vs. 71.0% majority baseline; **97.1% (99/102)** at confidence ≥0.8 (a selected slice, not blind correctness) | `docs/p0-report-2026-09-19.md` |
| Blind model-consensus adjudication of the 13 disagreement rows (`harness/blind-adjudication.mjs`; judges `anthropic/claude-sonnet-5` + `openai/gpt-5.6-terra`, blind to Jev and to the written verdict; adjudicator `google/gemini-3.8-flash`) | 12/13 decided (6 consensus, 6 adjudicated), 1 `UNDECIDABLE`. Rescored: Jev **121/131 = 92.4%** vs. consensus; on the 12 decided rows the written verdict matched consensus 8/12, Jev 4/12 | `docs/round2b-report-2026-09-20.md`; `reports/p0-rescored-fd-c2-model-consensus.json` |
| Digests | `p0-rescored-fd-c2-model-consensus.json` sha256 `2f3fd1f3f2f1b7f85e8b21d05b09c61d879737aaaa276c1f30272b76f9c6cdbf`; `adjudication/fd-c2.labelled.jsonl` sha256 `d53acd28177aba2887e738724d12eabb150c917cf52bc60179d486b01c3135a2` | computed locally over both files at rest |
| Admissibility | Model-consensus labels count as evidence and are reported as `model-consensus`, never `human` | `C:\code\JEV_PLAN\owner-decisions.md`, row (a), 2026-09-20 |

## 3. What this candidate does NOT claim

- **No human labels anywhere in this evidence.** Every "correctness" number above is model-consensus
  against three model judges plus one model adjudicator, admissible only under the owner's row-(a)
  ruling and reported as `model-consensus`, never `human`.
- **Thirteen disagreement rows, not a fresh blind cohort.** `design/round2/astra-design.md` Q6 sets
  the promotion bar at a new, independently adjudicated **100-row correctness cohort** (≥95/100,
  ≥10 per verdict class, no silently dropped row). This candidate's 13-row, 12-decided adjudication
  is evidence toward Q6, not a substitute for it — it is one order of magnitude short of the
  required cohort size.
- **One row is undecidable and is not folded into either side's score**, per §2's 12/13 figure.
- No claim that this display authorizes merge, release, or any queue/gate action; §2.4 of the
  standard states advisory "widens review only."

## 4. Ratification procedure

Per the owner ruling of 2026-09-06: **adversarial seats ratify.** Two blind, cross-family seats
(neither told the other's identity or verdict in advance) each read this file bound to its own
SHA-256 hash (computed after this commit lands, over the exact bytes at that commit) and record a
verdict line (`RATIFY` / `REJECT` + one reason) in a receipt filed beside this candidate, not
edited into it. Per `RULINGS.md` R10.2's follow-on clause — no project records `ADVISORY` until
"the standard's §2.4 promotion ... has run and a further ruling names the project" — **this
candidate's §1 text is the further ruling offered for that naming.** It does not self-ratify: it
becomes a ruling only when both seats record `RATIFY` and the receipt is filed.

## 5. Falsifier

**This ruling is withdrawn** if a fresh, independently adjudicated 100-row blind cohort (the Q6
bar) scores Jev agreement below 90% against that cohort's adjudicated labels. A withdrawal reverts
FD-C2 to shadow-only pending re-evidence.

---

**Candidate file SHA-256:** computed below (post-write, pre-commit) and recorded in the commit that
adds this file.
