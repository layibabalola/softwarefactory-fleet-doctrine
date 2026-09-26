# S29 — key rounds, receipts (Conjugal, `S29-containment-check-is-lexical`)

Outcome heading (Conjugal): `Outcome - ACCEPTED at round 1 of 3. Counts as an acceptance.`

Ordering / identity / delivery witness (`python coordination/kernel-dogfood/check-ordering.py`, AUTHOR dates, read-only, run 2026-09-26): `S29 OK decl=3a5903b@2026-09-22T14:06:23-05:00 cand=272be21@2026-09-22T14:38:53-05:00 identity=ok delivered=yes outcome=ACCEPTED`

Key: class `codex-openai`. Every round below is a `codex exec` session (`session_meta.payload.originator=codex_exec`, `model_provider=openai`); `turn_context.payload.model` and `.effort` are quoted per round. Producer: Claude (class `claude-anthropic`), a different independence class.

Source files are Codex CLI rollout logs (JSONL), machine-local under `~/.codex/sessions/2026/09/<DD>/`. Rollout SHA-256 is of the whole file. **Excerpt** = the last `response_item` record with `payload.type=message`, `payload.role=assistant`, `payload.phase=final_answer`; its bytes are the UTF-8 concatenation of `payload.content[].text`, no trailing newline. **Verdict-line** SHA-256 is of the single verdict line of that excerpt, UTF-8, no newline (the S12/S13 convention). Extracted 2026-09-26, read-only, by a Claude Code receipt-extraction agent.

| Round | Tree named by the key | Model / effort | Rollout (`~/.codex/sessions/2026/09/<DD>/`) | Bytes | Rollout SHA-256 | Final-answer record | Excerpt bytes | Excerpt SHA-256 | Verdict line (verbatim) | Verdict-line SHA-256 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `d4223e59645634d1205ed3419913747659e0beb4` | `gpt-6-astra` / `high` | 22/`rollout-2026-09-22T14-40-22-01a0caa2-3231-7231-bc08-2efe999ef972.jsonl` | 769,315 | `7fab308e2b8218c86abc01a508b5afc43fc451846292dcfc42c15698842681d5` | line 172, `2026-09-22T19:48:42.316Z` | 3759 | `152ab06d7f60cea9263665a6b46df1df2f20a78454f91f4fe246fa7639380ff6` | `VERDICT: ACCEPT` | `f422a3f09f3f34867781b3d435ff517074b87f9ef6852bd7732ef50f8b95d1e7` |

Every excerpt was extracted from, and hashed against, its rollout file in the same pass; each verdict line is byte-present in its excerpt.

## Reconciliation with the value recorded in the Conjugal Outcome

| Round | Recorded "verdict SHA-256" | What those recorded bytes actually are | Reproduced from the ROLLOUT? | Recorded rollout SHA reproduced? |
|---|---|---|---|---|
| 1 | `48ef8622236a7ac57bbc37f4fd9199a4b441cb78` | SHA-256 of the producer's machine-local **whole console transcript** of the `codex exec` run (138,981 B: banner, prompt, tool calls and outputs, then the final message). Capture hash reproduced: yes. Not a verdict excerpt; the rollout excerpt is contained in it modulo console encoding | **NOT REPRODUCED from rollout** | none recorded |

## Excerpts (verbatim)

Machine-local temp paths inside an excerpt are replaced with `[machine-local temp path redacted]`; each digest above is of the **unredacted** original bytes, so a holder of the rollout can verify by re-extracting the record. No other change.

### Round 1

Record: line 172 of `rollout-2026-09-22T14-40-22-01a0caa2-3231-7231-bc08-2efe999ef972.jsonl`; `payload.phase=final_answer`; timestamp `2026-09-22T19:48:42.316Z` (UTC) (redacted).

~~~~text
Verified candidate tree `d4223e59645634d1205ed3419913747659e0beb4` on Windows, Python 3.14.4. Repository files remained unchanged; pre-existing `nums.json` was untouched.

For the measured paths below:

- `W` = `C:\code\Conjugal\.claude\worktrees\modest-rhodes-8f1078`
- `T` = `[machine-local temp path redacted]`
- P1–P2 used temporary repository `T\repo` and neutral file `T\outside.txt`.

| Property | MEASURED return or output | Exact refusal codes | Result |
|---|---|---|---|
| P1 | Absolute `T\outside.txt` → `None`; relative `../outside.txt` → `None` | Each `['OPEN_REFERENCE']` | **HOLDS** |
| P2 | `coordination/../../outside.txt` → `None` | `['OPEN_REFERENCE']` | **HOLDS** |
| P3 | `coordination/../coordination/HUB.md` → `W\coordination\..\coordination\HUB.md` | `[]` | **HOLDS** |
| P4 | Both supplied spellings → `W\coordination\HUB.md` | Each `[]` | **HOLDS** |
| P5 | Exit `0`; `Ran 4 tests`; `OK` | N/A—suite result | **HOLDS** |
| P6 | Exit `0`; `PASS: 72 compact-hub dry-run scenarios` | N/A—suite result | **HOLDS** |

**Q1.** Correct for the supplied containment cases, but not an exception-free predicate for every possible input and filesystem condition.

Additional **MEASURED** results using `R = T\repo`:

| Input | Returned value | Refusal codes |
|---|---|---|
| Absolute inside file | `R\coordination\HUB.md` | `[]` |
| Empty string | `R` | `[]` |
| `..` | `None` | `['OPEN_REFERENCE']` |
| Nonexistent `coordination/missing.txt` | `R\coordination\missing.txt` | `[]` |
| Nonexistent outside file, absolute and relative | Each `None` | Each `['OPEN_REFERENCE']` |

None raised or gave an incorrect containment result. Empty input identifies the repository directory; this helper does not establish that its return is an existing file.

**INFERRED by inspection:** Windows resolution can propagate an `OSError` for filesystem errors outside its suppressed error set. Also, an input traversing a symlink loop on Python before 3.13 can raise `RuntimeError`, which this helper does not catch. Neither exception case was measured or constructed. The version distinction is documented in [Python’s `Path.resolve` reference](https://docs.python.org/3.14/library/pathlib.html#pathlib.Path.resolve).

**Q2.** **INFERRED by inspection; NOT MEASURED with a link fixture.** Yes, a successfully resolved link inside the repository pointing outside changes from admitted to `None` with `['OPEN_REFERENCE']`. The declaration explicitly acknowledges that behavioral change. Excluding link-specific assertions is defensible for this bounded spelling-invariance fix, but provides no verified guarantee for symlink behavior.

**Q3.** **MEASURED: claim confirmed.** I removed exactly the containment `try/except` block from a temporary scratch planner, pointed the unchanged suite’s `PLANNER` variable at it, and ran all scenarios. Result: exit `0`, `PASS: 72 compact-hub dry-run scenarios`. Repository source and suite files were unchanged.

**Q4.** **INFERRED by inspection:** yes, the shared helper changes `--apply` manifest validation. Outside-repository archive references now accumulate `OPEN_REFERENCE` before the narrower archive check; manifest evidence references also use this helper. The subsequent `archive.relative_to(repo / "coordination/archive")` remains lexical.

Excluding targeted `--apply` assertions is defensible as an explicitly unverified extension of this bounded fix. It cannot establish archive-directory containment or unchanged behavior throughout `--apply`. The containment-specific behavior there was **NOT MEASURED**; the existing suite’s passing apply scenarios do not establish it, as Q3 demonstrates.

No blocking findings for the declared scope.

VERDICT: ACCEPT
~~~~
