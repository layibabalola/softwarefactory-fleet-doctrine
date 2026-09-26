# S32 — key rounds, receipts (Conjugal, `S32-a-guard-that-validates-a-value-it-derived-itself`)

Outcome heading (Conjugal): `Outcome - PARKED at round 1, NOT ACCEPTED (counts ZERO). The defect is fixed and shipped.`

Ordering / identity / delivery witness (`python coordination/kernel-dogfood/check-ordering.py`, AUTHOR dates, read-only, run 2026-09-26): `S32 NO-CANDIDATE-CITED decl=666b080@2026-09-22T17:55:13-05:00 cand=none identity=none delivered=unwitnessed outcome=DELIVERED-NOT-ACCEPTED note=bus-delivery-no-sha`

Key: class `codex-openai`. Every round below is a `codex exec` session (`session_meta.payload.originator=codex_exec`, `model_provider=openai`); `turn_context.payload.model` and `.effort` are quoted per round. Producer: Claude (class `claude-anthropic`), a different independence class.

Source files are Codex CLI rollout logs (JSONL), machine-local under `~/.codex/sessions/2026/09/<DD>/`. Rollout SHA-256 is of the whole file. **Excerpt** = the last `response_item` record with `payload.type=message`, `payload.role=assistant`, `payload.phase=final_answer`; its bytes are the UTF-8 concatenation of `payload.content[].text`, no trailing newline. **Verdict-line** SHA-256 is of the single verdict line of that excerpt, UTF-8, no newline (the S12/S13 convention). Extracted 2026-09-26, read-only, by a Claude Code receipt-extraction agent.

| Round | Tree named by the key | Model / effort | Rollout (`~/.codex/sessions/2026/09/<DD>/`) | Bytes | Rollout SHA-256 | Final-answer record | Excerpt bytes | Excerpt SHA-256 | Verdict line (verbatim) | Verdict-line SHA-256 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `7a4a5b362f6c58b6514f66ba32de229c19a2a88e` | `gpt-6-astra` / `high` | 22/`rollout-2026-09-22T21-45-03-01a0cc27-01c6-7e63-a0ee-dde0874e33a3.jsonl` | 675,924 | `3098e3c00991f2bba6cd84d65f9e499dc2ae3e04cf33b3a60c5e063e588e3253` | line 166, `2026-09-23T02:51:49.961Z` | 3981 | `797c0a738d60ea7705bc9ad7ee6e964fe01b8aa0ef52b2042e1970a06d960bbe` | `VERDICT: REFUSE` | `bd0ac07c453e4b5b94cce2df44b9a6eff50d228eb50952dc2cab7bca77d1a8ed` |

Every excerpt was extracted from, and hashed against, its rollout file in the same pass; each verdict line is byte-present in its excerpt.

## Reconciliation with the value recorded in the Conjugal Outcome

| Round | Recorded "verdict SHA-256" | What those recorded bytes actually are | Reproduced from the ROLLOUT? | Recorded rollout SHA reproduced? |
|---|---|---|---|---|
| 1 | `ecc609c53dd19cade59ad72358282feb6b169776` | SHA-256 of the producer's machine-local **whole console transcript** of the `codex exec` run (121,454 B: banner, prompt, tool calls and outputs, then the final message). Capture hash reproduced: yes. Not a verdict excerpt; the rollout excerpt is contained in it modulo console encoding | **NOT REPRODUCED from rollout** | none recorded |

## Excerpts (verbatim)

Machine-local temp paths inside an excerpt are replaced with `[machine-local temp path redacted]`; each digest above is of the **unredacted** original bytes, so a holder of the rollout can verify by re-extracting the record. No other change.

### Round 1

Record: line 166 of `rollout-2026-09-22T21-45-03-01a0cc27-01c6-7e63-a0ee-dde0874e33a3.jsonl`; `payload.phase=final_answer`; timestamp `2026-09-23T02:51:49.961Z` (UTC).

~~~~text
Verified tree `7a4a5b362f6c58b6514f66ba32de229c19a2a88e`. No tracked files changed; no commit or push.

**Fixture qualification:** The supplied recipe removes the layout mock before the status calls. Literally executed, W2 and W3 raise `repo-root`. Keeping the supplied `_validate_source_layout` mock active during revalidation produces the results below; lane validation and Git receipt validation remain real.

| Property | Result | Assessment |
|---|---|---|
| W1 | **MEASURED:** `"sol"` and `"NOT-A-LANE"` each raise `ObligationError("lane-mismatch")`. | **HOLDS** |
| W2 | **MEASURED:** `"luna"` returns `"RECORDED"` with the fixture qualification above. | **HOLDS** |
| W3 | **MEASURED:** `None` returns `"RECORDED"` without raising, with the same qualification. | **HOLDS** |
| W4 | **MEASURED:** `"luna"` writes `prepare-deferred.json`; `"sol"` raises `lane-mismatch`. Inspection confirms the sibling implementation is unchanged. | **HOLDS** |
| W5 | **NOT MEASURED independently:** the approximately 90-minute suite was not rerun. The declaration reports 41 pass/3 fail → 42 pass/2 fail, violating failure-set equality. | **BLOCKING:** the declared bar remains unmet; the repository explicitly treats a wrong bar as grounds to park the subject. |

**Q1.** Correct for the declared `str | None` contract **when the comparison is reached**. By inspection, `lane=""` is explicitly supplied and therefore rejected; another automation’s lane is rejected when it differs from this automation’s mapping. `"sol"` against the Luna automation was measured. For an unmapped automation, `persist_measurement` raises `automation-unbound` first. At the comparison itself, a `None` mapping rejects every supplied non-`None` lane; omitted `None` continues to subsequent validation. Empty-string and unmapped-automation behavior were **inferred, not measured**. Earlier short circuits still mean this is not unconditional validation of every call.

**Q2.** **Verified by inspection:** the production call at `check-context-usage.py:499–504` derives its lane using the same mapping. Internal callers either forward that value or omit it. Consequently, existing production behavior is unchanged under the current mapping. Declaring this as a latent parameter-contract correction is honest; declaring a repaired live exposure would not be.

**Q3.** The two corrections clearly disclose both mistakes, but the declaration still overclaims evidence. Its final section says **all three failures “ARE flaky”** and that the rerun supplies a load/timing diagnosis. One changed outcome establishes neither the flakiness of the two unchanged failures nor the disappearing failure’s cause. Intermittence also does not exclude a real defect. The “several minutes” suite-cost note is stale relative to the approximately 90-minute estimate.

**Q4.** **Verified by inspection:** `persist_measurement` rejects an unmapped automation at lines 889–890 before either `_deferred_status` call. With the current mapping, the later `lane is None` condition cannot arise through that route. **MEASURED:** omitting `repo` on the recorded fixture returned `("PREPARE", "RECORDED-UNVERIFIED")`.

VERDICT: REFUSE

1. **INFERRED BY INSPECTION — unmet declared acceptance bar.** W5’s reported failure sets differ. “No new failure observed” does not satisfy the declared equality requirement. The [repository rule](C:/code/Conjugal/.claude/worktrees/modest-rhodes-8f1078/coordination/kernel-dogfood/README.md:84) explicitly says a wrong bar requires parking the subject.

2. **INFERRED BY INSPECTION — unsupported evidentiary conclusion.** The [declaration’s diagnosis](C:/code/Conjugal/.claude/worktrees/modest-rhodes-8f1078/coordination/kernel-dogfood/S32-a-guard-that-validates-a-value-it-derived-itself.md:169) generalizes one disappearing failure to all three and claims a cause the reported measurements do not establish. The earlier disclosures do not cure this remaining overclaim.
~~~~
