# S13 — key rounds, receipts (Conjugal, `S13-undeclared-deletion-polices-one-file`)

Outcome heading (Conjugal): `Outcome — ACCEPTED, 2026-09-18`

Ordering / identity / delivery witness (`python coordination/kernel-dogfood/check-ordering.py`, AUTHOR dates, read-only, run 2026-09-26): `S13 OK decl=7fe8864@2026-09-18T18:50:41-05:00 cand=c6f3550@2026-09-18T19:22:26-05:00 identity=ok delivered=yes outcome=ACCEPTED`

Key: class `codex-openai`. Every round below is a `codex exec` session (`session_meta.payload.originator=codex_exec`, `model_provider=openai`); `turn_context.payload.model` and `.effort` are quoted per round. Producer: Claude (class `claude-anthropic`), a different independence class.

Source files are Codex CLI rollout logs (JSONL), machine-local under `~/.codex/sessions/2026/09/<DD>/`. Rollout SHA-256 is of the whole file. **Excerpt** = the last `response_item` record with `payload.type=message`, `payload.role=assistant`, `payload.phase=final_answer`; its bytes are the UTF-8 concatenation of `payload.content[].text`, no trailing newline. **Verdict-line** SHA-256 is of the single verdict line of that excerpt, UTF-8, no newline (the S12/S13 convention). Extracted 2026-09-26, read-only, by a Claude Code receipt-extraction agent.

| Round | Tree named by the key | Model / effort | Rollout (`~/.codex/sessions/2026/09/<DD>/`) | Bytes | Rollout SHA-256 | Final-answer record | Excerpt bytes | Excerpt SHA-256 | Verdict line (verbatim) | Verdict-line SHA-256 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `d44d8fb78b73d505c25d7ac0d3259251ca83bc50` | `gpt-6-astra` / `high` | 18/`rollout-2026-09-18T19-26-04-01a0b70e-5202-7341-a803-bc629b3f8fad.jsonl` | 1,045,281 | `f240915590860c1f5696fb17f23f1e7ea6abd5c16799855d50b8be5b6679e337` | line 254, `2026-09-19T00:39:18.355Z` | 1953 | `eb37a32f4d0b37d41fafcbfd8ec84e06b86183d5c6a5f42d6bfc2bce09adcd5c` | `VERDICT: ACCEPTED identity=d44d8fb78b73d505c25d7ac0d3259251ca83bc50 key=gpt-6-astra class=codex-openai` | `23ddcd4ed3291be01a55a4ebd7ff77ba2965b3b05b950d8fc2e740cef4213da0` |

Every excerpt was extracted from, and hashed against, its rollout file in the same pass; each verdict line is byte-present in its excerpt.

## Reconciliation with the value recorded in the Conjugal Outcome

| Round | Recorded "verdict SHA-256" | What those recorded bytes actually are | Reproduced from the ROLLOUT? | Recorded rollout SHA reproduced? |
|---|---|---|---|---|
| 1 | `23ddcd4ed3291be01a55a4ebd7ff77ba2965b3b05b950d8fc2e740cef4213da0` | SHA-256 of the verdict line inside the rollout final answer | **REPRODUCED** | yes |

## Excerpts (verbatim)

Machine-local temp paths inside an excerpt are replaced with `[machine-local temp path redacted]`; each digest above is of the **unredacted** original bytes, so a holder of the rollout can verify by re-extracting the record. No other change.

### Round 1

Record: line 254 of `rollout-2026-09-18T19-26-04-01a0b70e-5202-7341-a803-bc629b3f8fad.jsonl`; `payload.phase=final_answer`; timestamp `2026-09-19T00:39:18.355Z` (UTC).

~~~~text
- Identity: both `git rev-parse` checks returned the declared tree, exit **0**. Artifact status was clean before and after testing.
- Author dates and ancestry confirm declaration → fixtures → code. Config diff is empty.
- `python -B -m unittest discover -s coordination/harvest/tests -v`: exit **0**, **45/45 passed** in 508 seconds. Verbose output confirms **34 existing + 11 new** cases, including **0/6 replay refusals**.
- Baseline-copy filtered discover: exit **1**, both deletion tests failed because the old runner silently accepted deletions.
- Mutation A filtered discover: exit **1**, exactly three expected failures—both deletion tests and end-to-end 3b. Eight controls passed, including predicate-level 3b.
- Mutation B filtered discover: exit **1**, exactly three expected failures—row extension, sibling rewrite, and replay with **4/6 refused**. Eight controls passed.
- Provenance: all 132 governed fixture files matched bus content; all twelve `code.md` snapshots matched exact bytes.
- AST parse: exit **0**. `validate_word_cap` and the `moved_to` branch are unchanged.

My attacks found:
- **Pass:** ≥8-word filler, movement between tables within one file, deleting one occurrence of a duplicated key.
- **Refuse:** content moved to a sibling while the original key remains a stub, empty-first-cell rewrites/deletions, emptied bold-labelled fields, and under-eight-word stubs.

The passing attacks follow the declaration’s same-file key-survival rule; they demonstrate its semantic limits rather than an additional undeclared exemption. For bar 4, the independent 3b control is predicate-level; site A’s downstream end-to-end failure is explicitly preserved.

Tests used only permitted scratch storage, with process-local Git long-path support after initial path-length errors. Repository artifacts remain unchanged.

VERDICT: ACCEPTED identity=d44d8fb78b73d505c25d7ac0d3259251ca83bc50 key=gpt-6-astra class=codex-openai
~~~~
