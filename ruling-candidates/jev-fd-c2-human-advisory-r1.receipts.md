# Veto receipts: JEV-FD-C2-ADVISORY-1, r1

Candidate: `ruling-candidates/jev-fd-c2-human-advisory-r1.md` at `07f0ecc`.
Candidate SHA-256 (git blob content, LF): `6db3791af47c116218b85c60852009f70851dde8c460eaaaf8a054aa4687d1dd`.
Both seats bound their verdict to this digest. Both vetoed. r1 is kept unchanged as history; this
file records the two verdicts beside it, per the ratification procedure in r1 §4.

## Seat A — codex-openai, `gpt-6-astra`

Verdict line: `VETO 6db3791af47c116218b85c60852009f70851dde8c460eaaaf8a054aa4687d1dd`

Rollout: `%USERPROFILE%\.codex\sessions\2026\09\20\rollout-2026-09-20T17-41-05-01a0c0fa-ebef-7761-af8a-83fcf90cc610.jsonl`,
1,223,229 bytes, SHA-256 `5a9209a03b3b6f72758f4796d0c5c931b020553927dc04d512aa4a90813e9308`.
Verdict-line SHA-256: `a207528c4cba238a7419bbb69d71d4711f8fc8e70d58249ecd1eba1a8a91774f`.

Full findings (verbatim, public-safe):

> 1. **Integrity passes.** The candidate's exact bytes at `07f0ecc` match the requested SHA-256. Both evidence files match their cited SHA-256 digests. The question module matches blob `7137a360e7a5416153c1d34f1a7cb76df4bb2324`.
>
> 2. **Blindness fails decisively.** In [fd-c2.labelled.jsonl](C:/code/jev-plan/adjudication/fd-c2.labelled.jsonl:3), rows `adversarialllm/pr-82`, `pr-84`, and `pr-87` contain this in `state.review.notes`: "Verdict **not-merge-ready** until hosted CI is green and D2 lands on this tip." That equals their incumbent label. The harness sends that state directly to judges. I reconstructed all **33 recorded call input/prompt hash pairs: zero mismatches**, binding the leaked states to the receipts. Omitting top-level `currentLabel` and `jev` does not make these prompts blind. Owner decision (a)'s substance exists in the first decision row and admits model-consensus evidence; it does not cure label leakage.
>
> 3. **Evidence exists, but its interpretation and several counts are wrong.** Recomputed from rows:
>
>    | Measure | Actual |
>    |---|---:|
>    | Fidelity | 118/131 |
>    | Fidelity at confidence ≥0.8 | 99/102 |
>    | Rescored report agreement | 121/131 |
>    | Decided adjudication rows | 12/13 |
>    | Jev versus decided labels | **3/12**, not 4/12 |
>    | Incumbent versus decided labels | 8/12 |
>    | First-pass consensus / adjudicator-decided | **7 / 5**, not 6 / 6 |
>
>    The 121/131 figure mixes incumbent labels with 12 model-consensus labels; it is not 131 independently adjudicated comparisons. Undecided `adversarialllm/pr-102` retains its incumbent label and counts as a disagreement, contradicting the claimed exclusion. Excluding it yields **121/130**, still a mixed-reference score.
>
> 4. **Authority boundaries are appropriately narrow, but prerequisites fail.** The proposed manual display stays within §2.4's widening-review limit and §5's prohibition on touching verdicts. Locally stored `origin/master:RULINGS.md`, R10.2, allows a further project-naming ruling through this route, conditional on fidelity, blind adjudication, and a K2 register licence. This candidate cannot satisfy that condition with contaminated adjudication.
>
> 5. **The falsifier is numerically testable but not operationally supplied.** Below 90% on 100 rows means at most 89 agreements. However, no fresh cohort or runnable Q6 verifier is supplied; the referenced `harness/verify-round2.py` is absent. The candidate also acknowledges that Q6's proposed ≥95/100 promotion evidence remains unmet.
>
> Fix: Remove verdict leakage, version the changed state construction, rerun fidelity and independent adjudication, correct counts and label-source denominators, and resubmit with a runnable falsifier and explicit project/register binding.

Source: `C:\code\jev-plan\design\round2\advisory-r1-seat-codex.md`.

## Seat B — claude-anthropic (Opus 5 subagent, in-process; no rollout file)

Verdict line: `VETO 6db3791af47c116218b85c60852009f70851dde8c460eaaaf8a054aa4687d1dd`

Findings:

1. Counts as stated are misstated: r1 §2 reports "12/13 decided (6 consensus, 6 adjudicated)"; the
   actual adjudication file shows **7 first-pass consensus rows and 5 adjudicator-decided rows**
   among the 12 decided rows, not 6/6.
2. Jev versus the 12 decided rows is **3/12**, not the 4/12 r1 §2 reports.
3. The one `UNDECIDABLE` row (`adversarialllm/pr-102`) is not cleanly excluded: it still sits inside
   the 131-row denominator used for the headline fidelity figure, so the "not folded into either
   side's score" claim in r1 §3 is true of the adjudication tally but not of the fidelity tally.
4. No project is named for `RULINGS.md` R10.2's follow-on clause. r1 §1 offers its own text as "the
   further ruling" naming a project, but the text never states which project's queue, gate, or
   register the licence attaches to — `softwarefactory-fleet-doctrine` is referenced only as the
   bus row of origin in r1's preamble, not bound in the operative §1 text.
5. The falsifier in r1 §5 is not executable: it names a threshold ("below 90% on 100 rows") and a
   bar (Q6, ≥95/100) but no command, script path, or extractor that would produce the 100-row
   cohort or run the comparison.
6. The headline **92.4%** figure (r1 §2, "Rescored: Jev 121/131 = 92.4% vs. consensus") mixes 118
   never-blind incumbent-label agreements (the rows Jev was never adjudicated against) with the
   12 rows that did go through blind model-consensus adjudication. It is not a blind-correctness
   figure on 131 rows.

Decisive shared finding (both seats, independently): **verdict-word leakage.** `state.review.notes`
and `state.review.blockers` on several rows (including `adversarialllm/pr-82`, `pr-84`, `pr-87`)
contain the literal written verdict, e.g. "Verdict **not-merge-ready** until…". This text reaches
both Jev (as part of the `state` object it is scored against) and the blind judges (as part of the
prompt state sent by the harness). Neither the fidelity run nor the adjudication run was blind to
the verdict being measured.

## Disposition

Two vetoes on the same candidate SHA-256. r1 is superseded by
`ruling-candidates/jev-fd-c2-human-advisory-r2.md`, which corrects the leakage (state-construction
`state2`), recomputes every figure from the corrected data, and narrows the falsifier to an
executable command.
