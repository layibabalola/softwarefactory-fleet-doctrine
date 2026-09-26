# S30 — key rounds, receipts (Conjugal, `S30-shadowed-case-arm-and-the-batched-assertion-that-hides-it`)

Outcome heading (Conjugal): `Outcome - ACCEPTED at round 1 of 3. Counts as an acceptance.`

Ordering / identity / delivery witness (`python coordination/kernel-dogfood/check-ordering.py`, AUTHOR dates, read-only, run 2026-09-26): `S30 OK decl=5241b36@2026-09-22T15:20:34-05:00 cand=8cab657@2026-09-22T15:49:40-05:00 identity=ok delivered=yes outcome=ACCEPTED`

Key: class `codex-openai`. Every round below is a `codex exec` session (`session_meta.payload.originator=codex_exec`, `model_provider=openai`); `turn_context.payload.model` and `.effort` are quoted per round. Producer: Claude (class `claude-anthropic`), a different independence class.

Source files are Codex CLI rollout logs (JSONL), machine-local under `~/.codex/sessions/2026/09/<DD>/`. Rollout SHA-256 is of the whole file. **Excerpt** = the last `response_item` record with `payload.type=message`, `payload.role=assistant`, `payload.phase=final_answer`; its bytes are the UTF-8 concatenation of `payload.content[].text`, no trailing newline. **Verdict-line** SHA-256 is of the single verdict line of that excerpt, UTF-8, no newline (the S12/S13 convention). Extracted 2026-09-26, read-only, by a Claude Code receipt-extraction agent.

| Round | Tree named by the key | Model / effort | Rollout (`~/.codex/sessions/2026/09/<DD>/`) | Bytes | Rollout SHA-256 | Final-answer record | Excerpt bytes | Excerpt SHA-256 | Verdict line (verbatim) | Verdict-line SHA-256 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `7cafba0c1` | `gpt-6-astra` / `high` | 22/`rollout-2026-09-22T15-51-18-01a0cae3-2379-72b0-a377-86d10fa536e8.jsonl` | 355,951 | `cef728bf2b6c78e923d186dbab2740da0580364036ab8d1235d7474fcc795893` | line 49, `2026-09-22T20:53:24.710Z` | 2052 | `3203875c36e18cb55d2ac78fad1e35c46adcdb8a46c7803cf06783d2083f3c5e` | `VERDICT: ACCEPT` | `f422a3f09f3f34867781b3d435ff517074b87f9ef6852bd7732ef50f8b95d1e7` |

Every excerpt was extracted from, and hashed against, its rollout file in the same pass; each verdict line is byte-present in its excerpt.

## Reconciliation with the value recorded in the Conjugal Outcome

| Round | Recorded "verdict SHA-256" | What those recorded bytes actually are | Reproduced from the ROLLOUT? | Recorded rollout SHA reproduced? |
|---|---|---|---|---|
| 1 | `4b9f7deb2b8379ae3a5d052915b7e306b917b4cb` | SHA-256 of the producer's machine-local **whole console transcript** of the `codex exec` run (62,888 B: banner, prompt, tool calls and outputs, then the final message). Capture hash reproduced: yes. Not a verdict excerpt; the rollout excerpt is contained in it modulo console encoding | **NOT REPRODUCED from rollout** | none recorded |

## Excerpts (verbatim)

Machine-local temp paths inside an excerpt are replaced with `[machine-local temp path redacted]`; each digest above is of the **unredacted** original bytes, so a holder of the rollout can verify by re-extracting the record. No other change.

### Round 1

Record: line 49 of `rollout-2026-09-22T15-51-18-01a0cae3-2379-72b0-a377-86d10fa536e8.jsonl`; `payload.phase=final_answer`; timestamp `2026-09-22T20:53:24.710Z` (UTC).

~~~~text
Verified HEAD’s tree is `7cafba0c1`. Repository unchanged; existing untracked `nums.json` left untouched.

| Property | Measured result | Status |
|---|---|---|
| T1 | DASHBOARD-API alone: `pairprog_certification=1` | HOLDS |
| T2 | Same invocation: `pairprog_dashboard=1` | HOLDS |
| T3 | Byte-for-byte match to all eleven specified lines, in order | HOLDS |
| T4 | CONFIGURATION alone: `pairprog_certification=1`, `pairprog_dashboard=0` | HOLDS |
| T5 | Suite exits `0`, prints `PASS` | HOLDS |

**Q1 — MEASURED:** Exactly one occurrence in the planner’s `case` statements: **line 76**.

**Q2 — MEASURED:** In an external scratch copy, replaced both `pairprog_certification=1` assignments with `pairprog_packet=1`. The suite exited **1**, failing the pre-existing assertion at **test line 130**:

> FAIL: certification artifact and doctor contract surfaces should select the certification lane (expected=1 actual=0)

This confirms the pre-existing suite exercises the planner’s certification behavior.

**Q3 — Inferred by inspection:** Agree for this positive assertion. Lines **129–130** load six paths together; any one selecting certification satisfies the assertion, masking missing coverage for another member. The new standalone DASHBOARD-API assertions and CONFIGURATION control are a substantive remedy for this defect. They do not establish individual coverage for every other member.

**Q4 — MEASURED locations; behavioral conclusions inferred by inspection:** Only two other exact duplicated labels exist:

| Label | Planner lines | Flags set by either listing | Assessment |
|---|---|---|---|
| `dashboard/index.html` | 82, 83 | `pairprog_any=1`, `pairprog_dashboard=1` | Same arm; behaviorally inert |
| `scripts/setup-wizard.ps1` | 66, 170 | `pairprog_any=1`, `pairprog_windows_runtime=1` | Separate arms with identical effects; behaviorally inert |

Both paths have the `.codex-state/agent-loop/` prefix. Leaving these duplicates is defensible scope control; neither hides a second live routing defect.

VERDICT: ACCEPT
~~~~
