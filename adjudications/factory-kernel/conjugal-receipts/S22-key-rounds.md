# S22 — key rounds, receipts (Conjugal, `S22-dispositioned-self-filing-is-silent`)

Outcome heading (Conjugal): `Outcome — ACCEPTED, 2026-09-22. K6 obtained on the FIRST round.`

Ordering / identity / delivery witness (`python coordination/kernel-dogfood/check-ordering.py`, AUTHOR dates, read-only, run 2026-09-26): `S22 OK decl=ae02d54@2026-09-22T01:06:51-05:00 cand=c323c4a@2026-09-22T01:24:16-05:00 identity=ok delivered=yes outcome=ACCEPTED`

Key: class `codex-openai`. Every round below is a `codex exec` session (`session_meta.payload.originator=codex_exec`, `model_provider=openai`); `turn_context.payload.model` and `.effort` are quoted per round. Producer: Claude (class `claude-anthropic`), a different independence class.

Source files are Codex CLI rollout logs (JSONL), machine-local under `~/.codex/sessions/2026/09/<DD>/`. Rollout SHA-256 is of the whole file. **Excerpt** = the last `response_item` record with `payload.type=message`, `payload.role=assistant`, `payload.phase=final_answer`; its bytes are the UTF-8 concatenation of `payload.content[].text`, no trailing newline. **Verdict-line** SHA-256 is of the single verdict line of that excerpt, UTF-8, no newline (the S12/S13 convention). Extracted 2026-09-26, read-only, by a Claude Code receipt-extraction agent.

| Round | Tree named by the key | Model / effort | Rollout (`~/.codex/sessions/2026/09/<DD>/`) | Bytes | Rollout SHA-256 | Final-answer record | Excerpt bytes | Excerpt SHA-256 | Verdict line (verbatim) | Verdict-line SHA-256 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `f08000648013d77360d0e75f88d23d84d2965fc8` | `gpt-6-astra` / `high` | 22/`rollout-2026-09-22T01-27-10-01a0c7cb-ff2f-7711-ae36-b80583d91677.jsonl` | 684,514 | `6a2f6b2452406bdeae292aab43cc7cc516f2657c2003d23d8d8c563a126e486f` | line 203, `2026-09-22T06:39:10.119Z` | 3601 | `d6bf6765f74d4f2cbff04788206343d9eedd27306b7974439276a66c40b7e5c5` | `ACCEPT f08000648013d77360d0e75f88d23d84d2965fc8` | `7d452bde46a495025170a31f199b7914e8323af3c316ce3d18afa9c0268471d8` |

Every excerpt was extracted from, and hashed against, its rollout file in the same pass; each verdict line is byte-present in its excerpt.

## Reconciliation with the value recorded in the Conjugal Outcome

| Round | Recorded "verdict SHA-256" | What those recorded bytes actually are | Reproduced from the ROLLOUT? | Recorded rollout SHA reproduced? |
|---|---|---|---|---|
| 1 | `6107deba348b56e667e26db242413a739afbc39b7d7fa6b9b34246b2a77a505a` | SHA-256 of the producer's machine-local stdout capture of `codex exec`: the final message re-emitted through the Windows console (CRLF line ends; non-ASCII mangled via cp437, e.g. an em dash becomes `ΓÇö`). Capture hash reproduced: yes; capture equals the rollout excerpt after undoing CRLF and cp437: yes | **NOT REPRODUCED from rollout** | yes |

## Excerpts (verbatim)

Machine-local temp paths inside an excerpt are replaced with `[machine-local temp path redacted]`; each digest above is of the **unredacted** original bytes, so a holder of the rollout can verify by re-extracting the record. No other change.

### Round 1

Record: line 203 of `rollout-2026-09-22T01-27-10-01a0c7cb-ff2f-7711-ae36-b80583d91677.jsonl`; `payload.phase=final_answer`; timestamp `2026-09-22T06:39:10.119Z` (UTC).

~~~~text
ACCEPT f08000648013d77360d0e75f88d23d84d2965fc8

- **Bar 1 — Pass.** Verified `c323c4af7^{tree}` equals the supplied OID. The branch sits inside the existing `HARVESTED` check, before its unconditional `continue`, so it emits the new note without reaching ordinary exclusion, debounce, or selection logic.

- **Bar 2 — Pass, with a coverage gap.** The complete state space is:

  | Status | Excluded | Not excluded |
  |---|---|---|
  | `HARVESTED` | New `STEWARD-ROW-OWED` note; never picked | Silent; never picked; unchanged |
  | `UNHARVESTED` | Existing `SELF-FILING` note; never picked | Existing debounce/selection behavior |
  | `STALE` | Existing `SELF-FILING` note; never picked | Existing debounce/selection behavior |

  The three declared neighbours are relevant but not exhaustive. Foreign `UNHARVESTED`, the fifth cell overall, **is already tested** by the new neighbour test. Foreign `STALE` is the sixth: the existing test covers its fresh/debounced case, but the new equality tests omit its older/eligible case. I independently checked both ages against the parent implementation; behavior matches.

- **Bar 1 — Assertion strength confirmed.** Full-list equality catches missing, extra, duplicated, or incorrect notes. Membership would also reject the original empty list; equality additionally excludes unwanted notes. The implementation interpolates `f['filing']` and `f['blob']`. The single fixed fixture alone cannot establish that provenance, so I also checked a different excluded filing and blob; both appeared correctly.

- **Bar 3 — Pass.** Restoring only the parent’s `eligible()` in memory produced exactly one failure: bar 1. The neighbour test and existing `test_rules` remained green. No checkout mutation was needed.

- **Bar 4 — Pass for the requested filtered invocation.** Reruns completed successfully:
  - `python -m unittest coordination.harvest.tests.test_harvest_runner.Eligibility`: **3 tests**, exit 0.
  - `python -m unittest discover -s coordination/harvest/tests -p "test_harvest_runner.py"`: **56 tests**, exit 0.
  - Parent runner and test sources replayed in memory: **54 tests**, exit 0.

  The loader baseline of 54 is correct; direct execution previously collected 52 because `GateDriver` followed `unittest.main()`. The existing SELF-FILING assertion remains unchanged. One documentation correction: the commit message omits `-p`; unrestricted discovery currently collects **91**, not 56.

- **Bar 1 — Scope is explicit; the blocker explanation is overstated.** Deferring ledger append is reasonable. `BUS_UNPLANNED_DISPOSITIONS` is real, and I reproduced its refusal for a changed, unplanned disposition file. However, it checks **changed paths**, not every existing disposition. A ledger-only append leaving an existing foreign disposition untouched passes `validate_bus`; I verified that too. Changing this gate is therefore not inherently required for every possible append implementation.

- **Bars 1/2 — Operational limitations, not failures of the declared contract.** The note repeats on every eligible call, including after a ledger row has been appended: no ledger-presence check or acknowledgement exists. Valid upstream status requires a matching disposition blob reference, but neither this function nor that status proves foreign authorship. A caller supplying fabricated `HARVESTED` data can trigger the note without a disposition. Missing required `filing`/`blob` fields can raise `KeyError`; there is no new validation. For valid inputs, my probes confirmed unchanged picked lists and digests, and no input mutation.
~~~~
