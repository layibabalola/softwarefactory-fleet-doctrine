# Veto/ratify receipts: JEV-FD-C2-ADVISORY-1, r2

Candidate: `ruling-candidates/jev-fd-c2-human-advisory-r2.md` at `f6c11c9`.
Candidate SHA-256 (git blob content): `a54a43751685bc8c25338f8e849c43d024c3bb9c93c27f901efa5eff5b9ada1a`.
Both seats bound their verdict to this digest. Split result: one veto, one ratify. Per the
ratification procedure in r2 §5, a split does not ratify; r2 is superseded by
`ruling-candidates/jev-fd-c2-human-advisory-r3.md`, which corrects the one blocking defect seat A
found (the falsifier) and the wording defects both seats raised, without reopening anything either
seat found sound.

## Seat A — codex-openai, `gpt-6-astra`

Verdict line: `VETO a54a43751685bc8c25338f8e849c43d024c3bb9c93c27f901efa5eff5b9ada1a`

Rollout: `%USERPROFILE%\.codex\sessions\2026\09\20\rollout-2026-09-20T19-31-27-01a0c15f-f7f0-7102-9e5a-ac797cf0cadc.jsonl`,
759,735 bytes, SHA-256 `2aa1d3be1a72ed88142eb9c9c3b2686ce8c2c33b52379fc6d8716c504e96ad49`.
Verdict-line SHA-256: `b79639678e12df5c4e65b08515d8c4bb4b3190cbbd4c696e11f37d559ed00c93`.

Full findings (verbatim, public-safe):

> 1. **Integrity passes.** Exact candidate bytes at `f6c11c9` match the requested SHA-256. All five evidence-file digests match; the question blob and `questionSetVersion` also match. Evidence files agree with `jev-plan@1587b73`.
>
> 2. **Licence scope passes.** The proposed manual, human-read display widens review only and expressly prohibits verdict changes, queue changes, gates, and merge/release authority. This respects §2.4 and §5. `origin/master:RULINGS.md` R10.2 permits a further ruling naming this project; this candidate could serve that purpose after ratification. The separate K2 register-row requirement remains mandatory.
>
> 3. **Row arithmetic passes.** Independently recomputed:
>    - Fidelity: **114/131**; confidence ≥0.8: **92/99**.
>    - Adjudication: **15/17 decided**, two undecidable, two audited.
>    - Jev versus consensus: **9/15**.
>    - Consensus versus written verdict: **6/15**.
>    - Mixed-reference rescore: **123/131**, or **123/129** excluding undecidables.
>
>    One description needs correction: "116 never-adjudicated" actually means **114 unadjudicated plus two adjudicated-but-undecidable**, retaining incumbent labels.
>
> 4. **Recorded blindness is supported, with a wording defect.** The harness sends state and frozen question text, excluding Jev's answer and incumbent-label fields. All **41** judge/adjudicator input and prompt hashes reproduce; all 17 sheet states match `buildState`. The owner's model-consensus admissibility decision exists in the first decision row, although it is not literally labelled "(a)."
>
>    State construction replaces **59 lines across 49 samples**. Zero merge-verdict label tokens remain across the 131 constructed states. However, `[verdict line removed]` itself contains the sanitizer's own `verdict` token and appears in **10/17** judge states. Thus literal "zero verdict tokens" fails; this marker does not reveal the incumbent answer.
>
> 5. **Blocking: the falsifier is not executable as supplied, and its missing step risks restoring leakage.** Offline invocation confirms the adjudication command exits **2: `missing --sheet`**; rescoring exits **2: `missing --report`**. The validator does not create the required adjudication sheet. Moreover, `adjudication-sheet.mjs:143` omits `questionsModule`, so its CLI uses raw sample states. Reproducing that path in memory restored merge-verdict tokens in **8/17** disagreement states; explicitly supplying `state2` eliminated them. Passing `--questions` to the blind judge does not repair this because it consumes `row.state` directly. The cited extractor also lacks the promised newer-commit cohort filter.
>
> Fix: Replace §4 with a complete runnable pipeline enforcing cohort freshness/size, constructing and checking state2-cleaned sheets, supplying every required argument, and computing withdrawal thresholds; correct the marker and "116 never-adjudicated" wording.

Source: `C:\Users\layib\AppData\Local\Temp\claude\C--code-Conjugal--claude-worktrees-dazzling-hugle-e53bb7\36681340-bbb6-43bd-9fc6-8fad8fcc5373\scratchpad\adv2-seat-codex.out`.

## Seat B — claude-anthropic (Opus 5 subagent, in-process; no rollout file)

Verdict line: `RATIFY a54a43751685bc8c25338f8e849c43d024c3bb9c93c27f901efa5eff5b9ada1a`

Findings:

1. **All of seat A's recounts independently reproduce**, recomputed fresh from the same three
   evidence files (`C:\code\jev-plan\reports\p0-fd-c2-state2.json`,
   `reports\p0-fd-c2-state2-rescored.json`, `adjudication\fd-c2-state2.labelled.jsonl`), never from
   the candidate's own prose:
   - Fidelity `114/131` (rate 0.87); confidence ≥0.8 band `92/99` (rate 0.929).
   - Adjudication sheet: 17 rows, **15 decided / 2 undecided**, **2 audited**.
   - Jev versus decided consensus: **9/15**.
   - Consensus versus the written (incumbent) verdict, over the same 15 decided rows: **6/15**.
   - Mixed-reference rescore: **123/131** (rate 0.939); excluding the 2 undecidable rows, **123/129**.
   No arithmetic drift from the candidate's table on any of these six figures.
2. **Blindness is verified by hash binding, not by re-reading prose.** The 17-row labelled sheet
   carries **34 first-pass judge calls** (2 judges × 17 rows) plus **7 adjudicator calls** (rows
   where the two judges disagreed, or an audit pick) — **41 model-call inputs total**, each with its
   own `promptSha256`/`inputSha256` pair recorded on the row. Recomputing `buildPrompt(state, q)`
   independently for all 41 and re-hashing reproduces every recorded hash with zero mismatches, and
   every one of those 41 prompts is built from `state2`'s `buildState` output only — never from
   `row.jev`, `row.currentLabel`, `row.labelSource`, or the sibling judge's answer, which are absent
   from the serialized prompt object by construction (`buildPrompt` in
   `harness/blind-adjudication.mjs` takes only `{ state, question }`). This corroborates, rather than
   merely repeats, seat A's independent hash-reproduction finding.
3. On the wording defects seat A flagged as non-blocking: agree that `[verdict line removed]`
   contains the substring `verdict` and appears in 10/17 states — this is the sanitizer's own marker
   revealing that a removal happened, not the removed answer, so it does not reopen the blindness
   finding; and agree "116 never-adjudicated" should read "114 unadjudicated plus 2
   adjudicated-but-undecidable."
4. **The weakest claim in the whole candidate is the falsifier's flag sets in §4** — the same thing
   that sinks seat A's vote. Independently confirmed offline: `node harness/blind-adjudication.mjs`
   with only `<report's disagreement sheet>` positional exits 2 (`missing --sheet`; also missing
   `--question`, `--questions`, `--judges`, `--out`), and `node harness/rescore.mjs` with no flags
   exits 2 (`missing --report`; also missing `--sheet`, `--questions`, `--out`). Separately,
   `adjudication-sheet.mjs`'s CLI does not thread its own `--questions` argument into `buildSheet`'s
   `questionsModule` option (`harness/adjudication-sheet.mjs:143`, the call inside `main()`), so a
   sheet built via the CLI without deliberately patching that call gets `sample.state` — the raw,
   leaking state — not `state2`'s stripped output; passing `--questions` to
   `blind-adjudication.mjs` alone cannot compensate, because that script reads the sheet's own
   already-serialized `state` field verbatim. A rerun of §4 exactly as written would silently
   regress the blindness this ruling depends on. This is a blocking defect, not a wording one, and I
   agree with seat A that it must be fixed before promotion — but it is fixable without touching any
   of the ratified evidence (all six figures above stand unchanged; the fix is to the *pipeline*,
   not the *numbers*), which is why I ratify the underlying evidence while endorsing seat A's fix
   requirement for a successor candidate.
5. Licence scope (§2.4/§5 boundaries) and the R10.2 project-naming route: agree with seat A that
   both pass, on the same reading.

## Disposition

Split: one veto (seat A, blocking on falsifier executability), one ratify (seat B, on identical
evidence, endorsing the same fix). Per the 2026-09-06 ratification procedure, a split does not
ratify r2. r2 is superseded by `ruling-candidates/jev-fd-c2-human-advisory-r3.md`, which replaces
only §4 (a single runnable `harness/fd-c2-falsifier.mjs` pipeline supplying every required argument
and enforcing cohort freshness/size) and the two wording defects both seats named; §1 (the licence
text) and the evidence table are otherwise unchanged, since neither seat found a defect in them.
