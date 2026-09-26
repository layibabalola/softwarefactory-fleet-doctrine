# S18 — key rounds, receipts (Conjugal, `S18-provider-limit-classifier-fails-closed-on-spend`)

Outcome heading (Conjugal): `Outcome — PARKED at the three-round ceiling, NOT ACCEPTED, 2026-09-21 (counts ZERO)`

Ordering / identity / delivery witness (`python coordination/kernel-dogfood/check-ordering.py`, AUTHOR dates, read-only, run 2026-09-26): `S18 OK decl=4dcfed3@2026-09-21T01:24:35-05:00 cand=340a9c2@2026-09-21T02:22:39-05:00 identity=ok delivered=yes outcome=DELIVERED-NOT-ACCEPTED`

Key: class `codex-openai`. Every round below is a `codex exec` session (`session_meta.payload.originator=codex_exec`, `model_provider=openai`); `turn_context.payload.model` and `.effort` are quoted per round. Producer: Claude (class `claude-anthropic`), a different independence class.

Source files are Codex CLI rollout logs (JSONL), machine-local under `~/.codex/sessions/2026/09/<DD>/`. Rollout SHA-256 is of the whole file. **Excerpt** = the last `response_item` record with `payload.type=message`, `payload.role=assistant`, `payload.phase=final_answer`; its bytes are the UTF-8 concatenation of `payload.content[].text`, no trailing newline. **Verdict-line** SHA-256 is of the single verdict line of that excerpt, UTF-8, no newline (the S12/S13 convention). Extracted 2026-09-26, read-only, by a Claude Code receipt-extraction agent.

| Round | Tree named by the key | Model / effort | Rollout (`~/.codex/sessions/2026/09/<DD>/`) | Bytes | Rollout SHA-256 | Final-answer record | Excerpt bytes | Excerpt SHA-256 | Verdict line (verbatim) | Verdict-line SHA-256 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `17931a100b2731d0187401569c45272292cb2f5b` | `gpt-6-astra` / `high` | 21/`rollout-2026-09-21T01-41-41-01a0c2b2-ecd6-7601-9954-d94aeb3d2eaa.jsonl` | 947,477 | `bc43d961674c6306b684ee8dae562d01f991746cd33276bc1435ae725d81b60b` | line 282, `2026-09-21T06:54:52.744Z` | 2977 | `ab4615ebd827f480da8ef9d7570616fb26527dafadec3304794d6b5f18630cec` | `REFUSE 17931a100b2731d0187401569c45272292cb2f5b` | `3fd57960af45a1e5e62a3ac6d9dd2d118126c71cba896c679fced0ef8e3785d0` |
| 2 | — | `gpt-6-astra` / `high` | 21/`rollout-2026-09-21T02-07-41-01a0c2ca-b9a8-7d73-bf50-4c878a268f7f.jsonl` | 721,879 | `12730418a1348454ba38ba41b375e9605260250724927b42ad302780a8f0e823` | none | — | — | **none — no final_answer record** | — |
| 3 | `a111cc6c28c921bba106acfa83296d6aaaddf27b` | `gpt-6-astra` / `high` | 21/`rollout-2026-09-21T02-23-27-01a0c2d9-2975-77a0-84f8-339680ffef74.jsonl` | 744,286 | `2991bc4ec6c77c6203c14d631a12c7fd8060c604fa38a4ddbdb461c4cdef2063` | line 181, `2026-09-21T07:35:10.466Z` | 2845 | `107c241f615034dae73aeece7331c113473eca84bede5abae4c315d1777a76ea` | `REFUSE a111cc6c28c921bba106acfa83296d6aaaddf27b` | `c0be1e655bee8da3b98832a1538bcff99f7277f1db9ddf5b607d456dd92e14bd` |

Every excerpt was extracted from, and hashed against, its rollout file in the same pass; each verdict line is byte-present in its excerpt.

## Reconciliation with the value recorded in the Conjugal Outcome

| Round | Recorded "verdict SHA-256" | What those recorded bytes actually are | Reproduced from the ROLLOUT? | Recorded rollout SHA reproduced? |
|---|---|---|---|---|
| 1 | `4ac382ba084a16537b891c7963dda840fe30d1720b19d154eacbae8693cfe47d` | SHA-256 of the producer's machine-local stdout capture of `codex exec`: the final message re-emitted through the Windows console (CRLF line ends; non-ASCII mangled via cp437, e.g. an em dash becomes `ΓÇö`). Capture hash reproduced: yes; capture equals the rollout excerpt after undoing CRLF and cp437: yes | **NOT REPRODUCED from rollout** | yes |
| 2 | `e3b0c442…b7852b855` | SHA-256 of an EMPTY (0-byte) stdout capture; the rollout holds no final_answer record, which is consistent with no verdict | **REPRODUCED** | yes |
| 3 | `44cb0c69db99e2fc88abac904375f63b4ef9359677190f0ff88e76833e66eb16` | SHA-256 of the producer's machine-local stdout capture of `codex exec`: the final message re-emitted through the Windows console (CRLF line ends; non-ASCII mangled via cp437, e.g. an em dash becomes `ΓÇö`). Capture hash reproduced: yes; capture equals the rollout excerpt after undoing CRLF and cp437: yes | **NOT REPRODUCED from rollout** | yes |

## Excerpts (verbatim)

Machine-local temp paths inside an excerpt are replaced with `[machine-local temp path redacted]`; each digest above is of the **unredacted** original bytes, so a holder of the rollout can verify by re-extracting the record. No other change.

### Round 1

Record: line 282 of `rollout-2026-09-21T01-41-41-01a0c2b2-ecd6-7601-9954-d94aeb3d2eaa.jsonl`; `payload.phase=final_answer`; timestamp `2026-09-21T06:54:52.744Z` (UTC).

~~~~text
REFUSE 17931a100b2731d0187401569c45272292cb2f5b

- **Bar 2 — quoted prose still misclassifies.** Removing the anchor makes both supplied negative controls fail, so they are falsifiable. However, a fenced quotation containing `You have hit your weekly limit`, introduced as a runbook quotation and followed by “This is documentation, not a live limit,” returns capacity. At `2026-09-21T06:00:00Z`, the parent returns `None`; this candidate returns `2026-09-21T12:00:00Z`. The multiline anchor permits the quoted line, and widening changes its classification.

- **Bar 3 — producer coverage is incomplete.** Deleting either `spend` or `five-hour` leaves all seven S18 tests green. My independent deletion matrix confirms those branches are load-bearing. There is no shadowing: `5-hour`/`5 hour` share one branch; `five-hour` is separate. Reversing `spend` and `monthly spend` preserves both matches—the ordering justification is incorrect.

- **Bar 4 — the captured replay passes, with a parser weakness.** All 20 records match local history through the capture timestamp. Faithful parsing produces exactly one legitimate spend-limit flip and zero spurious flips. However, `exit=1 tail='You have reached your weekly limit'` is missed by the supplied parser because it recognizes only `tail="`. This defect does not alter the actual 20-record result. Also, exempting every `SESSION_NO_SENTINEL` match does not establish that every such failure was genuinely capacity-related.

- **Bar 5 — spend parking passes; reset boundaries are defective.** Independently exercised `cmd_finish → cmd_park`: exit `0`, `ROTATE_REQUEST`, retry `2026-09-25T06:00:00Z`, attempts **1 → 0**. Invalid dates return `None`, triggering the six-hour fallback. Ordinary cross-DST dates work. Passed dates advance an entire year—even exact reset-time equality does so. From December 2027, February 29, 2028 is incorrectly rejected because construction first uses 2027. During the repeated DST hour, an upcoming second `1:30am` can likewise be pushed into next year.

- **Bar 6 — missing identity falsely signals rotation.** Starting with a known UUID, removing `.claude.json` causes `cmd_plan` to emit `PARK-CLEARED-ROTATION` without an account change. Missing, malformed, and unreadable metadata collapse to the same fallback digest, so unavailable identities cannot distinguish accounts. Valid UUID changes and ordinary credential refresh behave correctly. `oauthAccount: null` additionally raises uncaught `AttributeError`.

- **Bar 1 — passes.** All four declared provider phrasings classify as capacity.

- **Bar 7 — passes.** The declaration explicitly records the sibling residual; its predicate is at `coordination/deadman/deadman-core.psm1:397`.

- **Bars 1–7 verification:** Tree OID matched first. Candidate S18 tests: **7/7 passed**. Full requested suite: **45/45 passed in 686.003 seconds**. Those green results do not detect the reproduced Bar 2 and Bar 6 failures.
~~~~

### Round 2

No `final_answer` record in the rollout. The rollout ends mid-turn (last record a `token_count` after a tool output) with no `task_complete`: no verdict exists.

### Round 3

Record: line 181 of `rollout-2026-09-21T02-23-27-01a0c2d9-2975-77a0-84f8-339680ffef74.jsonl`; `payload.phase=final_answer`; timestamp `2026-09-21T07:35:10.466Z` (UTC).

~~~~text
REFUSE a111cc6c28c921bba106acfa83296d6aaaddf27b

Tree identity verified. The full suite passed **53/53 tests**; the separately rerun S18 checks passed **15/15**. Independent reproductions nevertheless establish these findings:

1. **P1 — Fence stripping suppresses a genuine spend limit.** [harvest_runner.py:834](/C:/code/Conjugal/coordination/harvest/harvest_runner.py:834) counts markers without matching fence character or length. With `L = "You've hit your monthly spend limit"`:

   ```python
   text = "````markdown\n```\nsample\n````\n" + L + "\n```\n"
   ```

   The genuine message is outside the closed four-backtick block, but scanning returns only `"sample"`. End-to-end, this produces `SESSION_NO_SENTINEL`, **attempts=1**, and no capacity retry. The plain-message control emits `ROTATE_REQUEST`, parks, and leaves **attempts=0**.

2. **P1 — Quoted limits still classify as live.** This fully fenced quotation returns a capacity retry:

   ```python
   text = "```markdown\n~~~\n" + L + "\n~~~\n```\nDocumentation only.\n"
   ```

   The inner tildes incorrectly toggle the outer backtick fence. A balanced quotation followed by an unrelated unterminated fence also becomes live because odd marker counts disable all fence stripping. Indented code and lazy blockquote continuations likewise reproduce false positives.

3. **P1 — Indeterminate Codex identity falsely clears a park.** [harvest_runner.py:96](/C:/code/Conjugal/coordination/harvest/harvest_runner.py:96) substitutes `"codex:unreadable"` and still returns a digest when Claude identity is available. Replacing synthetic, valid Codex auth with malformed JSON—while keeping the Claude account unchanged—made `cmd_plan()` remove the park and emit **`PARK-CLEARED-ROTATION`**.

   Escaped lone surrogates in either account identifier also raise `UnicodeEncodeError`. Synthetic newline-containing identifier pairs collide through ambiguous concatenation; this demonstrates missing input validation, not a collision between valid provider UUIDs.

4. **P2 — Replay extraction remains unfaithful.** [test_harvest_runner.py:798](/C:/code/Conjugal/coordination/harvest/tests/test_harvest_runner.py:798) greedily includes the closing quote in the extracted tail. This affects the fixture’s sole `tail=` record. Independent literal decoding still produces exactly **one** capacity reclassification—the spend receipt at `2026-09-21T05:34:54Z`—so the current count is correct despite the extraction defect.

Bar 3 withstands the requested attack: each branch deletion fails exactly its own case, and no pair is jointly deletable. Vocabulary checks, CRLF, an indented live message, an inline fence marker, ordinary spend parking, and the named sibling residual passed. The reproduced suppression, quoted-message classification, and false rotation prevent acceptance.
~~~~
