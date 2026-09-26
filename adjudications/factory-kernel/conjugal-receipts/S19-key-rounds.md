# S19 — key rounds, receipts (Conjugal, `S19-font-embedding-verifier-cannot-fail`)

Outcome heading (Conjugal): `Outcome — PARKED, NOT ACCEPTED, 2026-09-21 (counts ZERO)`

Ordering / identity / delivery witness (`python coordination/kernel-dogfood/check-ordering.py`, AUTHOR dates, read-only, run 2026-09-26): `S19 OK decl=86638d5@2026-09-21T15:59:33-05:00 cand=b60f332@2026-09-21T16:22:27-05:00 identity=none delivered=yes outcome=DELIVERED-NOT-ACCEPTED`

Key: class `codex-openai`. Every round below is a `codex exec` session (`session_meta.payload.originator=codex_exec`, `model_provider=openai`); `turn_context.payload.model` and `.effort` are quoted per round. Producer: Claude (class `claude-anthropic`), a different independence class.

Source files are Codex CLI rollout logs (JSONL), machine-local under `~/.codex/sessions/2026/09/<DD>/`. Rollout SHA-256 is of the whole file. **Excerpt** = the last `response_item` record with `payload.type=message`, `payload.role=assistant`, `payload.phase=final_answer`; its bytes are the UTF-8 concatenation of `payload.content[].text`, no trailing newline. **Verdict-line** SHA-256 is of the single verdict line of that excerpt, UTF-8, no newline (the S12/S13 convention). Extracted 2026-09-26, read-only, by a Claude Code receipt-extraction agent.

| Round | Tree named by the key | Model / effort | Rollout (`~/.codex/sessions/2026/09/<DD>/`) | Bytes | Rollout SHA-256 | Final-answer record | Excerpt bytes | Excerpt SHA-256 | Verdict line (verbatim) | Verdict-line SHA-256 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | — | `gpt-6-astra` / `high` | 21/`rollout-2026-09-21T16-08-14-01a0c5cc-4676-7a93-81bf-5824f03d1da0.jsonl` | 417,530 | `7b7bf03a36115fb5f4d5feb1f15ec46401df6ec399d06575639a8d187ec4a7b1` | none | — | — | **none — no final_answer record** | — |
| 2 | `d281b6b27d3107b6f55c856741986f1fd54bdfb8` | `gpt-6-astra` / `high` | 21/`rollout-2026-09-21T16-19-43-01a0c5d6-ca56-7b61-88c1-c20ba6241e39.jsonl` | 705,877 | `d598a6481e8829409ba9db53c6aba0d6298d33e830973e6be5787b032b05a228` | line 114, `2026-09-21T21:25:11.453Z` | 4452 | `c7094bd60716a28be5fb6bff07cbeb6f6c6e0e104110840d4aec743e8311ce43` | `REFUSE d281b6b27d3107b6f55c856741986f1fd54bdfb8` | `7c18fd039dd01fa6ffc5bf1bef809ffa8473b0241f0c38350fb27caa03981d13` |

Every excerpt was extracted from, and hashed against, its rollout file in the same pass; each verdict line is byte-present in its excerpt.

## Reconciliation with the value recorded in the Conjugal Outcome

| Round | Recorded "verdict SHA-256" | What those recorded bytes actually are | Reproduced from the ROLLOUT? | Recorded rollout SHA reproduced? |
|---|---|---|---|---|
| 1 | `e3b0c442…b7852b855` | SHA-256 of an EMPTY (0-byte) stdout capture; the rollout holds no final_answer record, which is consistent with no verdict | **REPRODUCED** | yes |
| 2 | `78b4b692a3c9db575a67d3d283d24722e50c37e663b183cd14bd7c3cb3ac9a14` | SHA-256 of the producer's machine-local stdout capture of `codex exec`: the final message re-emitted through the Windows console (CRLF line ends; non-ASCII mangled via cp437, e.g. an em dash becomes `ΓÇö`). Capture hash reproduced: yes; capture equals the rollout excerpt after undoing CRLF and cp437: yes | **NOT REPRODUCED from rollout** | yes |

## Excerpts (verbatim)

Machine-local temp paths inside an excerpt are replaced with `[machine-local temp path redacted]`; each digest above is of the **unredacted** original bytes, so a holder of the rollout can verify by re-extracting the record. No other change.

### Round 1

No `final_answer` record in the rollout. The rollout ends mid-turn (last record a `token_count` after a tool output) with no `task_complete`: no verdict exists.

### Round 2

Record: line 114 of `rollout-2026-09-21T16-19-43-01a0c5d6-ca56-7b61-88c1-c20ba6241e39.jsonl`; `payload.phase=final_answer`; timestamp `2026-09-21T21:25:11.453Z` (UTC).

~~~~text
REFUSE d281b6b27d3107b6f55c856741986f1fd54bdfb8

- **Bars 1–2 — object-stream attribution fails in both directions.** In `pdf-fonts.mjs:52–58`, compressed `/ObjStm` members lose their `obj…endobj` wrappers after inflation, so embedding evidence is missed. A real embedded Arial font passed in an ordinary-object PDF but failed after object-stream compression; MuPDF extracted all 1,045,720 font bytes from both. Conversely, an **uncompressed** object stream is treated as one object, sharing embedding evidence across its members. A valid mixed Arial/Helvetica PDF then incorrectly passed with unembedded Helvetica. Round 1 refused that identical file; this candidate accepts it. **Mechanism: an outer object-stream span conflates contained font dictionaries.** Cross-reference streams alone do not imply compressed font dictionaries; object-stream membership is the relevant distinction. False acceptance silently ships missing fonts, whereas false refusal visibly stops a recoverable build.

- **Bars 1–2 — names are not font-object identities.** `pdf-fonts.mjs:26–68` merges different font objects sharing a name and transfers embedding evidence between them. `oracle-check.py:51` repeats this merging with Boolean OR, hiding the error. The scanner also fails to decode PDF name escapes: a MuPDF-generated `/Arial#20Regular` becomes `Arial`, producing an additional incorrect refusal.

- **Bars 1, 2 and 4 — the oracle’s score is incomplete and sometimes wrong.** `oracle-check.py:48–51,86–100` skips unnamed fonts, compares only intersecting names, and ignores the scanner’s exit status. The committed corpus yielded **40 agreements but excluded 527 scanner-only names**. I also obtained oracle exit 0 when one agreeing PDF accompanied another PDF whose scanner failed and whose names did not join. `ext == "n/a"` is not universally “glyph data absent”: a valid direct font dictionary returned xref 0 and `"n/a"` despite containing the embedded font. The Type3 exception is conceptually correct for valid Type3 fonts—the glyphs reside in CharProcs—but does not validate those streams. The comment claiming `full=True` enables recursive discovery is also incorrect for installed PyMuPDF: its source shows that flag merely retains the referencer field.

- **Bar 3 — implementation works, but the required test is missing.** The actual candidate build exited 0 for a good PDF and 1 for an unembedded-font PDF in an isolated harness with assembly/rendering stubbed. However, `pdf-fonts.test.mjs:158–167` only searches source text, contrary to the declared bar. Changing the build’s failure branch to `process.exit(0)` still passed that test. Invoke the actual build module with controlled dependencies and assert its process status; also cover child-process startup failure.

- **Bars 4 and 7 — fixtures overstate their coverage.** `make-font-fixtures.mjs:49–53` produces readable PDF containers with correct xrefs, but their font programs are literally `STUBFONT`, not valid glyph data. They exercise descriptor-key detection, not legitimate font embedding. The claimed Type3 fixture is worse: `pdf-fonts.test.mjs:20–25,102–108` creates `/Subtype /TrueType`, references nonexistent CharProc object 99, and supplies no glyph stream. Its surrounding PDF lacks an xref and page font resources. It cannot establish bar 7. The subset-only corpus observation is accurate; the claimed compensating coverage is insufficient.

- **Bar 5 — mutation isolation is not satisfied as declared.** Independently restoring global attribution failed only bar 1, and removing the caller check failed only bar 3. Disabling the verifier’s failing exit, however, failed **both bar 2 and the strengthened bar-4 fixture test**. The required “only its own case goes red” matrix does not hold.

- **Bar 6 — the control does not vary its declared dimension.** `pdf-fonts.test.mjs:87–99` compares one embedded font with two embedded fonts. Both arms contain embedded fonts. Their bytes differ, and both pass, but this does not vary “whether the document contains any embedded font at all,” as declared.

- **Bars 2 and 4 — required reruns completed.** The candidate tree hash matched exactly. Rerunning from an exported copy of that candidate produced **8/8 passing tests** and oracle exit 0 across **14 committed PDFs**, with **40/40 compared fonts agreeing**. These green results do not resolve the failures above.
~~~~
