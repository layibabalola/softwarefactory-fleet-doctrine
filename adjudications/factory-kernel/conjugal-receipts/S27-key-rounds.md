# S27 — key rounds, receipts (Conjugal, `S27-render-prompt-literal-substitution`)

Outcome heading (Conjugal): `Outcome - ACCEPTED at round 1 of 3. Counts as an acceptance.`

Ordering / identity / delivery witness (`python coordination/kernel-dogfood/check-ordering.py`, AUTHOR dates, read-only, run 2026-09-26): `S27 OK decl=9ac3630@2026-09-22T05:32:08-05:00 cand=96fcad8@2026-09-22T05:42:27-05:00 identity=ok delivered=yes outcome=ACCEPTED`

Key: class `codex-openai`. Every round below is a `codex exec` session (`session_meta.payload.originator=codex_exec`, `model_provider=openai`); `turn_context.payload.model` and `.effort` are quoted per round. Producer: Claude (class `claude-anthropic`), a different independence class.

Source files are Codex CLI rollout logs (JSONL), machine-local under `~/.codex/sessions/2026/09/<DD>/`. Rollout SHA-256 is of the whole file. **Excerpt** = the last `response_item` record with `payload.type=message`, `payload.role=assistant`, `payload.phase=final_answer`; its bytes are the UTF-8 concatenation of `payload.content[].text`, no trailing newline. **Verdict-line** SHA-256 is of the single verdict line of that excerpt, UTF-8, no newline (the S12/S13 convention). Extracted 2026-09-26, read-only, by a Claude Code receipt-extraction agent.

| Round | Tree named by the key | Model / effort | Rollout (`~/.codex/sessions/2026/09/<DD>/`) | Bytes | Rollout SHA-256 | Final-answer record | Excerpt bytes | Excerpt SHA-256 | Verdict line (verbatim) | Verdict-line SHA-256 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `f52c03ac499ab7fbeabacdb8756f53cd1a521646` | `gpt-6-astra` / `high` | 22/`rollout-2026-09-22T05-43-34-01a0c8b6-bdbb-7131-a2e7-a05a79e2b8fe.jsonl` | 716,128 | `2b9ccccf880df90699dffb897da827006ce66abf2bf46ad3b4213f62a38396a6` | line 164, `2026-09-22T10:51:26.014Z` | 2519 | `9d972f8d44152073958fa44f5b662433eaef5d0972ad35cbef2e2c4096ff82b6` | `VERDICT: ACCEPT` | `f422a3f09f3f34867781b3d435ff517074b87f9ef6852bd7732ef50f8b95d1e7` |

Every excerpt was extracted from, and hashed against, its rollout file in the same pass; each verdict line is byte-present in its excerpt.

## Reconciliation with the value recorded in the Conjugal Outcome

| Round | Recorded "verdict SHA-256" | What those recorded bytes actually are | Reproduced from the ROLLOUT? | Recorded rollout SHA reproduced? |
|---|---|---|---|---|
| 1 | `a806c2067bf3442ca9db42abee91d5199f84a181` | SHA-256 of the producer's machine-local **whole console transcript** of the `codex exec` run (147,874 B: banner, prompt, tool calls and outputs, then the final message). Capture hash reproduced: yes. Not a verdict excerpt; the rollout excerpt is contained in it modulo console encoding | **NOT REPRODUCED from rollout** | none recorded |

## Excerpts (verbatim)

Machine-local temp paths inside an excerpt are replaced with `[machine-local temp path redacted]`; each digest above is of the **unredacted** original bytes, so a holder of the rollout can verify by re-extracting the record. No other change.

### Round 1

Record: line 164 of `rollout-2026-09-22T05-43-34-01a0c8b6-bdbb-7131-a2e7-a05a79e2b8fe.jsonl`; `payload.phase=final_answer`; timestamp `2026-09-22T10:51:26.014Z` (UTC).

~~~~text
Verified with Bash from the specified worktree, whose HEAD tree is `f52c03ac499ab7fbeabacdb8756f53cd1a521646`. Repository files were unchanged.

All results below are **MEASURED**. Backslash fixtures were confirmed on disk with `od -c`. Output comparisons included terminating LF bytes.

| Property | Measured value | Result |
|---|---|---|
| P1 | `TASK: A & B` — 1 line, 12 bytes; exit 0 | HOLDS |
| P2 | `TASK: C:\notes` — 1 line, 15 bytes; exit 0 | HOLDS |
| P3 | `PKT:` followed by `pkt: C:\notes`; packet bytes identical; exit 0 | HOLDS |
| P4 | `PKT:` followed by `pkt: A & B`; packet bytes identical; exit 0 | HOLDS |
| P5 | `PKT:` followed by `pkt: hello`; packet bytes identical, nonempty; exit 0 | HOLDS |
| P6 | `TASK: plain task` — 1 line, 17 bytes; exit 0 | HOLDS |
| P7 | Exit 0; printed `PASS: 6 assertions` | HOLDS |
| P8 | Exit 0; printed `PASS: 158 assertions` | HOLDS |

**Q1 — Inferred by inspection:** `splice()` correctly performs literal, non-overlapping replacement. Each iteration consumes an occurrence from the original remaining string; inserted values are never rescanned. Self-containing replacements terminate, empty values remove only matched tokens, and repeated occurrences are each replaced once. An empty token returns the input unchanged. No input identified that causes infinite looping, unintended text loss, or duplication within this helper.

**Q2 — Inferred by inspection:** Both awk programs initialize all 21 replacement-value variables from `ENVIRON[]`, including `v_prior_packet_content`. No referenced replacement variable is unassigned. Function parameters, local scratch variables, and awk built-ins have their normal sources.

**Q3 — Inferred by inspection:** All 21 environment values are exported before either awk executes. No executable `-v` assignment remains in `scripts/render-prompt.sh`; its only `-v` occurrence is in a comment.

**Q4 — Inferred by inspection:** Both exclusions are untouched. TASK substitution still precedes BRANCH substitution, allowing later rewriting of inserted tokens. Packet content is still printed directly without a fence. These exclusions leave the narrowly scoped repair internally consistent.

Nonblocking coverage correction, **inferred by inspection**: `scripts/test-create-loop.sh:363` installs a renderer stub. P8 satisfies its stated exit/output property, but does not exercise the actual renderer implementation through its caller. P1–P7 directly verify the renderer.

No blocking findings.

VERDICT: ACCEPT
~~~~
