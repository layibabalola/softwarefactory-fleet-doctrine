# S31 — key rounds, receipts (Conjugal, `S31-first-of-type-matches-nothing`)

Outcome heading (Conjugal): `Outcome - ACCEPTED at round 2 of 3. Counts as an acceptance.`

Ordering / identity / delivery witness (`python coordination/kernel-dogfood/check-ordering.py`, AUTHOR dates, read-only, run 2026-09-26): `S31 OK decl=a5b496b@2026-09-22T16:26:13-05:00 cand=e93985e@2026-09-22T17:00:13-05:00 identity=ok delivered=yes outcome=ACCEPTED`

Key: class `codex-openai`. Every round below is a `codex exec` session (`session_meta.payload.originator=codex_exec`, `model_provider=openai`); `turn_context.payload.model` and `.effort` are quoted per round. Producer: Claude (class `claude-anthropic`), a different independence class.

Source files are Codex CLI rollout logs (JSONL), machine-local under `~/.codex/sessions/2026/09/<DD>/`. Rollout SHA-256 is of the whole file. **Excerpt** = the last `response_item` record with `payload.type=message`, `payload.role=assistant`, `payload.phase=final_answer`; its bytes are the UTF-8 concatenation of `payload.content[].text`, no trailing newline. **Verdict-line** SHA-256 is of the single verdict line of that excerpt, UTF-8, no newline (the S12/S13 convention). Extracted 2026-09-26, read-only, by a Claude Code receipt-extraction agent.

| Round | Tree named by the key | Model / effort | Rollout (`~/.codex/sessions/2026/09/<DD>/`) | Bytes | Rollout SHA-256 | Final-answer record | Excerpt bytes | Excerpt SHA-256 | Verdict line (verbatim) | Verdict-line SHA-256 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `f7a49615a` | `gpt-6-astra` / `high` | 22/`rollout-2026-09-22T16-55-22-01a0cb1d-c9a5-7e93-a110-43cd26cd5189.jsonl` | 550,630 | `2a5d2e5708b21d502cb7bf3e3a2cc5c2608269a0a82a2da0e2afcd04660c01f8` | line 79, `2026-09-22T21:58:16.428Z` | 2466 | `cbd6342b22819fdb92c030060496833fb73806a4378ea4add7c90d64794610f7` | `VERDICT: REFUSE` | `bd0ac07c453e4b5b94cce2df44b9a6eff50d228eb50952dc2cab7bca77d1a8ed` |
| 2 | `831c204a9830893972db7d8cccc029e0eebd1a74` | `gpt-6-astra` / `high` | 22/`rollout-2026-09-22T17-01-09-01a0cb23-1327-7530-8d91-9e7d3674e651.jsonl` | 453,605 | `161e80da648b5955befcdb0f6609d5ab5d14fbac3a1de34cecd0c798310ae040` | line 72, `2026-09-22T22:04:01.479Z` | 2516 | `afd9b8bcbdda9bbb234cf80c82f903850b3c878501c4a8152e2dfbdaa04200f6` | `VERDICT: ACCEPT` | `f422a3f09f3f34867781b3d435ff517074b87f9ef6852bd7732ef50f8b95d1e7` |

Every excerpt was extracted from, and hashed against, its rollout file in the same pass; each verdict line is byte-present in its excerpt.

## Reconciliation with the value recorded in the Conjugal Outcome

| Round | Recorded "verdict SHA-256" | What those recorded bytes actually are | Reproduced from the ROLLOUT? | Recorded rollout SHA reproduced? |
|---|---|---|---|---|
| 1 | `d17a767b44a29f9c3bb276bca66266330df8c961` | SHA-256 of the producer's machine-local **whole console transcript** of the `codex exec` run (91,412 B: banner, prompt, tool calls and outputs, then the final message). Capture hash reproduced: yes. Not a verdict excerpt; the rollout excerpt is contained in it modulo console encoding | **NOT REPRODUCED from rollout** | none recorded |
| 2 | `aef8cc8e7decb2947b41fe699a3457e64f6e1e36` | SHA-256 of the producer's machine-local **whole console transcript** of the `codex exec` run (83,412 B: banner, prompt, tool calls and outputs, then the final message). Capture hash reproduced: yes. Not a verdict excerpt; the rollout excerpt is contained in it modulo console encoding | **NOT REPRODUCED from rollout** | none recorded |

## Excerpts (verbatim)

Machine-local temp paths inside an excerpt are replaced with `[machine-local temp path redacted]`; each digest above is of the **unredacted** original bytes, so a holder of the rollout can verify by re-extracting the record. No other change.

### Round 1

Record: line 79 of `rollout-2026-09-22T16-55-22-01a0cb1d-c9a5-7e93-a110-43cd26cd5189.jsonl`; `payload.phase=final_answer`; timestamp `2026-09-22T21:58:16.428Z` (UTC).

~~~~text
Candidate tree matches `f7a49615a`. Worktree content remained unchanged.

| Property | Measured result | Status |
|---|---|---|
| U1 | 0 class `:first-of-type` rule blocks in rendered CSS | HOLDS |
| U2 | Both adjacent-sibling rules declare `border-top:1px solid var(--faintline)` | HOLDS |
| U3 | 0 `border-top` declarations in either base rule | HOLDS |
| U4 | 7 `.prow`, 10 `.mrow`; both panels and `.mvp` lead with `.ph`. Rendered markup excluding styles is byte-identical to the parent version. | HOLDS |
| U5 | Exit 0; all 4 tests passed | HOLDS |
| U6 | Not executed: the command overwrites the committed PNG, conflicting with “do not modify anything.” | NOT MEASURED |

**Q1 — MEASURED:** Headless Chrome, `devicePixelRatio = 1`: first `.prow` and `.mrow` each reported `0px`; all remaining 6 and 9 rows respectively reported `1px`. The asserted relation—first zero, later rows sharing one non-zero value—holds.

**Q2 — Inspection:** Adjacent siblings correctly express dividers between consecutive rows. One row receives no divider; zero rows produce none. An intervening element breaks adjacency, so the following row receives no divider, whereas the old base rule generally supplied one. Thus behavior differs for separated rows. That is appropriate for consecutive-row separators; it would not implement “every row after the first” across intervening elements. Current markup contains consecutive rows.

**Q3 — Inspection:** The scope is honest: the test explicitly disclaims computed-style verification and separately identifies the historical browser measurement. It also checks base-rule removal and markup controls. Its “jointly make … correct” wording depends on the current markup and cascade; these checks are not a general proof against every possible CSS override.

**Q4 — Inspection/inference:** Excluding PNG regeneration is defensible for this explicitly scoped source fix. The PNG blob is identical before and after the change. Consequently, it remains a pre-fix snapshot and disagrees with current rendering—an inference from source and artifact history, not an independently measured pixel comparison.

VERDICT: REFUSE

1. **Required verification incomplete: U6 is NOT MEASURED.** Inspection establishes that `build.py` writes `_board.html` and overwrites the committed PNG. Its exit status was not measured under the no-modification constraint. This is an acceptance evidence gap, not a measured build failure.
~~~~

### Round 2

Record: line 72 of `rollout-2026-09-22T17-01-09-01a0cb23-1327-7530-8d91-9e7d3674e651.jsonl`; `payload.phase=final_answer`; timestamp `2026-09-22T22:04:01.479Z` (UTC).

~~~~text
Candidate tree verified: `831c204a9830893972db7d8cccc029e0eebd1a74`.

| Property | Measured result | Status |
|---|---|---|
| V1 | Zero class `:first-of-type` rules in parsed rendered CSS; comments excluded. | HOLDS |
| V2 | Both adjacent-sibling rules declare `border-top:1px solid var(--faintline)`. | HOLDS |
| V3 | Neither base row rule declares `border-top`. | HOLDS |
| V4 | Exactly 7 `.prow`, 10 `.mrow`; both panels and the MVP container have `.ph` as their first direct child `div`. | HOLDS |
| V5 | Exit **0**; **4 tests passed**. | HOLDS |
| V6 | Build exit **0**; PNG byte-identical by Git hash. | HOLDS |

V6 hashes:

```text
Before: f1b87ce8a3c9dc6c5859cf4c923423106fb2e961
After:  f1b87ce8a3c9dc6c5859cf4c923423106fb2e961
```

**Q1 — MEASURED:** Headless Chrome, devicePixelRatio **2**: first `.prow` and `.mrow` each reported **`0px`**; all remaining rows reported **`1px`**. Assertions verified zero first, positive later, and identical later widths across both classes—not a hard-coded non-zero width. Old selectors matched zero elements.

**Q2 — Inferred by inspection:** A zero-row panel is unaffected. A one-row panel has no divider; this preserves the old correct behavior when that row was the first element of its type and fixes the header-first case. Separated rows differ: an intervening element prevents adjacency, so the following row loses its divider even where the old base-border rule correctly retained it. Current rendered rows are contiguous, so this is not a blocker.

**Q3 — MEASURED sizes; inferred explanation:** The PNG decreased from **1,883,159 to 1,882,991 bytes**. Dimensions also decreased from **5120×6778 to 5120×6776**. This is consistent with removing the first-row borders and their layout height. Compressed size alone cannot establish which pixels changed or prove unrelated changes occurred.

**Q4 — Inspected write paths; MEASURED final state:** The command reads the generator, `data.json`, six embedded font files, and `cdp-shot.mjs`. It writes:

- `_board.html`, subsequently deleted.
- `_tall.png`, subsequently deleted after trimming.
- The tracked output PNG, byte-identically.
- Temporary subprocess logs and a browser profile outside the repository; profile cleanup is best-effort.

Neither intermediate image/HTML file remained. No other tracked file is written by the inspected pipeline; final tracked diff was empty. Existing untracked `nums.json` remained untouched. Python bytecode writes were disabled for these checks.

VERDICT: ACCEPT
~~~~
