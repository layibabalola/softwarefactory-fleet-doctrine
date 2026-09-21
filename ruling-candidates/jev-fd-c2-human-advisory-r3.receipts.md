# Receipts: JEV-FD-C2-ADVISORY-1 r3 (candidate `cefcbcf0ea87586481fd3c63acf35421d0ef4134ea943e996001540bda4c31cb`)

**Result: VETO (two blind, cross-family seats, same root defect).** Both seats independently
reproduced the same executable failure in r3 §4's falsifier: the falsifier's step-4 command passed
the `state2` question-module **path** to `adjudication-sheet.mjs --questions`, which treats
`--questions` as a comma-separated **question-ID list**, not a module path. The bogus "id" never
matched `verdict`, so the sheet came out with **0 rows**, step 5 adjudicated nothing, and
`computeFalsifierVerdict` returned `WITHDRAW` on `decidedCount 0` regardless of the real
Jev-vs-consensus rate — an unconditionally broken falsifier, not merely an underpowered one.

## Seat A — codex-openai, `gpt-6-astra`, offline/read-only, reasoning effort high

VETO `cefcbcf0ea87586481fd3c63acf35421d0ef4134ea943e996001540bda4c31cb`

1. **Blocking defect: the falsifier's CLI wiring is broken.** At `ebb49d8`,
   `adjudication-sheet.mjs --questions` accepts comma-separated **question IDs**, not a module
   path. It never imports or passes `questionsModule`. The pipeline supplies
   `questions/q-fd-c2-state2.mjs`, so it produces an empty sheet. Executing that CLI with writes
   captured in memory yielded **0 rows**, versus **17** with the correct question ID and module.
   Consequently, reaching 100 samples cannot repair the falsifier: it cannot perform the promised
   adjudication and ultimately withdraws for zero decided disagreements.

2. **Identity and evidence pass.** The candidate hash matches exactly. All five evidence SHA-256
   values match, and their bytes match `1587b73`; the question blob also matches. Independently
   recomputed from rows: fidelity **114/131**, decided **15/17**, Jev–consensus **9/15**,
   consensus–written verdict **6/15**, rescores **123/131** and **123/129**. The rescores are
   correctly disclosed as mixed-reference evidence.

3. **Recorded blindness passes.** State reconstruction reproduces **49 affected samples and 59
   removed lines**. All 17 adjudication states match reconstructed `state2`; all **41**
   judge/adjudicator input and prompt hashes match. Zero merge-verdict label tokens remain across
   the 131 reconstructed states. The answer-neutral removal marker remains in 10/17 judge states.
   Prompts exclude Jev's answer and the incumbent label. The owner's model-consensus admissibility
   decision exists as the first, unlettered table row.

4. **Licence and ruling route pass.** The proposed display only widens human review and preserves
   §5's verdict, queue, and authority boundaries. Cached `origin/master:RULINGS.md` R10.2 permits a
   further ruling naming this project. `CLAUDE.md` identifies `RULINGS.md` as its register; the
   proposed entry can supply that grant once properly ratified and recorded.

5. **Cohort shortage is honest; executable completeness is not established.** Read-only extraction
   reproduced **5 < 100**. That shortage alone means "not yet eligible," not void. However, the CLI
   defect makes this pipeline invalid as supplied. The 11 pure tests pass but miss this
   integration. The requested `--dry` invocation was stopped by a read-only guard before its
   filesystem creation; no full dry-run completion is claimed.

Fix: Add and wire a question-module CLI option that imports `state2`, selects `verdict`, and
passes `questionsModule` into `buildSheet`; test the actual pipeline arguments for nonempty,
leakage-free adjudication output.

**Rollout provenance:** `openai/codex` v0.154.0, model `gpt-6-astra`, provider `openai`, approval
`never`, sandbox `read-only`, reasoning effort `high`, session id `01a0c172-75d8-7b13-9aaa-695fe8be7b35`.
Rollout file: `rollout-2026-09-20T19-51-39-01a0c172-75d8-7b13-9aaa-695fe8be7b35.jsonl`,
980112 bytes, SHA-256 `5fc3144798ea0a8edeff2bc207d277a171313555ced772d74476ae9cc5574733`.
Verdict-line (`VETO cefcbcf0ea87586481fd3c63acf35421d0ef4134ea943e996001540bda4c31cb`, as printed,
trailing newline) SHA-256 `8cac2c8309e46d3d565fc30f1ad397a9d3f73f40167ba1a5e3f708d9801023d6`.

## Seat B — claude-anthropic, Opus 5, in-process subagent

VETO `cefcbcf0ea87586481fd3c63acf35421d0ef4134ea943e996001540bda4c31cb`

`adjudication-sheet.mjs`'s `--questions` flag is a qid list, not a module path, and `main()` passed
no `questionsModule` at all. Running r3 §4's literal step-4 command produced **0 rows**.
`computeFalsifierVerdict` returns `WITHDRAW` whenever `decidedCount` is `0`. Without
`--questions-module`, the same command against the real cohort files decides **8 of 17** rows
correctly, meaning the fix is reachable but not present as specified — the missing piece is a
`--questions-module` flag threading a question module's `buildState`/`stateVersion` into
`buildSheet`.

Fix named: add `--questions-module <path>` to `adjudication-sheet.mjs`.

## Independent corroboration

Both seats, dispatched blind to each other's identity and verdict, converged on the identical root
cause (the module path fed to the wrong flag) and the identical fix shape (a dedicated
`--questions-module` CLI option). This is not two votes on a shared assumption — each seat
re-executed the pipeline's literal r3 §4 commands independently and observed the same 0-row/
`WITHDRAW`-on-`decidedCount-0` signature.

## Remedy (post-veto, informational — not part of the r3 ratification)

`C:\code\jev-plan` commit `a993347` ("adjudication-sheet.mjs: add --questions-module so buildSheet
actually strips leakage; fd-c2-falsifier wires it") adds `--questions-module <path>` to
`adjudication-sheet.mjs`; `fd-c2-falsifier.mjs` step 4 now runs
`adjudication-sheet.mjs --questions verdict --questions-module questions/q-fd-c2-state2.mjs`
instead of overloading `--questions` with the module path. Its commit message records: the
corrected invocation produces **17 rows**, **zero** verdict-token leakage, `stateVersion 'state2'`;
the same command without `--questions-module` leaks raw state; the old broken invocation (module
path as `--questions`) reproduces the **0-row** signature exactly. A new integration test drives
the real step-4 CLI then reaches adjudication with `decidedCount 17` and a reachable `STANDS`. Full
suite: **156/156** passing.
