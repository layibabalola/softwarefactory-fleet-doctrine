# S24 — key rounds, receipts (Conjugal, `S24-stripoption-deletes-what-readoption-refuses`)

Outcome heading (Conjugal): `Outcome - PARKED at round 2 of 3, NOT ACCEPTED (counts ZERO). The product defect is fixed.`

Ordering / identity / delivery witness (`python coordination/kernel-dogfood/check-ordering.py`, AUTHOR dates, read-only, run 2026-09-26): `S24 NO-CANDIDATE-CITED decl=27b8020@2026-09-22T02:52:16-05:00 cand=none identity=none delivered=unwitnessed outcome=DELIVERED-NOT-ACCEPTED note=bus-delivery-no-sha`

Key: class `codex-openai`. Every round below is a `codex exec` session (`session_meta.payload.originator=codex_exec`, `model_provider=openai`); `turn_context.payload.model` and `.effort` are quoted per round. Producer: Claude (class `claude-anthropic`), a different independence class.

Source files are Codex CLI rollout logs (JSONL), machine-local under `~/.codex/sessions/2026/09/<DD>/`. Rollout SHA-256 is of the whole file. **Excerpt** = the last `response_item` record with `payload.type=message`, `payload.role=assistant`, `payload.phase=final_answer`; its bytes are the UTF-8 concatenation of `payload.content[].text`, no trailing newline. **Verdict-line** SHA-256 is of the single verdict line of that excerpt, UTF-8, no newline (the S12/S13 convention). Extracted 2026-09-26, read-only, by a Claude Code receipt-extraction agent.

| Round | Tree named by the key | Model / effort | Rollout (`~/.codex/sessions/2026/09/<DD>/`) | Bytes | Rollout SHA-256 | Final-answer record | Excerpt bytes | Excerpt SHA-256 | Verdict line (verbatim) | Verdict-line SHA-256 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `384b5567b99603f66c7777db6465d6078284d20e` | `gpt-6-astra` / `high` | 22/`rollout-2026-09-22T02-56-14-01a0c81d-8a76-70d2-a0a6-43724c9703b0.jsonl` | 675,018 | `fe16ebb7ce649edee2995c2473f7cf0be9bc99006c2eb1e7fd215533e9b85185` | line 78, `2026-09-22T08:01:00.591Z` | 3794 | `eaa3ee6481dbca4ff4e5252ab27c12fa413ddd5366843c08205f4c376817e3db` | `REFUSE 384b5567b99603f66c7777db6465d6078284d20e` | `9ff8c51bdaa6702870520fa8e2ed1d606183fd529fd411acc1371c79d5fa6f64` |
| 2 | `8c333ff65c2f755c44b8306aabe677a8c0389567` | `gpt-6-astra` / `high` | 22/`rollout-2026-09-22T03-04-31-01a0c825-1e16-7d73-a101-0956682b1bba.jsonl` | 654,352 | `8d91a2e8645b0aed3c008e5493bb83e6097b1ebb97ec7c88204422fa03db204f` | line 82, `2026-09-22T08:08:44.213Z` | 2230 | `9103a5a7a17c391a6b3626cde34bbb44ebe46f29a4dcb4b21fed604eb930bdc6` | `REFUSE 8c333ff65c2f755c44b8306aabe677a8c0389567` | `2e4c58edb9a6958d2ce5bf3cb57580c7a330235fcc9f5a8b1375e026d4a8cb00` |

Every excerpt was extracted from, and hashed against, its rollout file in the same pass; each verdict line is byte-present in its excerpt.

## Reconciliation with the value recorded in the Conjugal Outcome

| Round | Recorded "verdict SHA-256" | What those recorded bytes actually are | Reproduced from the ROLLOUT? | Recorded rollout SHA reproduced? |
|---|---|---|---|---|
| 1 | `35f6699f7fdfbabf43900112cc04957a7f2a9eba` | SHA-256 of the producer's machine-local **prompt** file sent to the key, NOT of any verdict (capture hash reproduced: yes). Mislabelled in the Outcome | **NOT REPRODUCED from rollout** | none recorded |
| 2 | `c6df3452bf49fb07afc11658db64488ca2af2687` | SHA-256 of the producer's machine-local **prompt** file sent to the key, NOT of any verdict (capture hash reproduced: yes). Mislabelled in the Outcome | **NOT REPRODUCED from rollout** | none recorded |

## Excerpts (verbatim)

Machine-local temp paths inside an excerpt are replaced with `[machine-local temp path redacted]`; each digest above is of the **unredacted** original bytes, so a holder of the rollout can verify by re-extracting the record. No other change.

### Round 1

Record: line 78 of `rollout-2026-09-22T02-56-14-01a0c81d-8a76-70d2-a0a6-43724c9703b0.jsonl`; `payload.phase=final_answer`; timestamp `2026-09-22T08:01:00.591Z` (UTC) (redacted).

~~~~text
REFUSE 384b5567b99603f66c7777db6465d6078284d20e

- **Bar 3 — blocking: the test does not assert the declared reader agreement.** At [test-pairprog-cli.mjs:371](/C:/code/Conjugal/scripts/test-pairprog-cli.mjs:371), `consumed` comes from `isOptionValue(following)`. The imported `readOption` is never called by this test. Consequently, the assertion’s diagnostic claims something about `readOption` it never measured. Assert explicit expected pairs of actual `readOption` and `stripOption` results for each shape. Also, `!kept.includes(following)` measures value membership, not whether that occurrence was removed; duplicate tokens would invalidate this oracle.

- **Bars 1–3 — implementation:** both readers genuinely use the same predicate for a separate following token. Both independently recognize the option name and `name=` prefix; both bypass the predicate for an inline value. Those matching rules agree. Excluding `=` from a claim specifically about consuming the following token is honest: it does not conceal an implementation disagreement.

- **Bars 1–3 — observed state space**, with `--provider` as the target:

  | Input shape | Observed stripping | Assessment |
  |---|---|---|
  | Following long flag: `--provider --message hello` | `--message hello` | Correct |
  | Following single-dash value: `--provider -file x` | `x` | Correct |
  | Following bare `--`: `--provider -- x` | `-- x` | Correct under the declared rule |
  | No following token: `--provider` | Empty array | Correct |
  | Inline value: `--provider=--value x` | `x` | Correct |
  | Empty inline value: `--provider= x` | `x` | Correct; reader returns `""` |
  | Repeated: `--provider mock --provider other x` | `x` | Preserves existing first-read/all-strip behavior |
  | Target inside earlier inline value: `--message=--provider hello` | Unchanged | Correct |

  For `--message --provider hello`, stripping leaves `--message`: under this parser’s declared grammar, the separate `--provider` token cannot be a value because it starts with `--`. Express that literal value as `--message=--provider`.

  Adjacent repetition deserves an explicit fixture: `['--provider','--provider','mock']` reads the default but strips everything. The second option is removed independently as another occurrence. Thus “everything stripped was consumed by the reader” is broader than the implementation guarantees.

- **Bars 2–3 — surviving mutant confirmed.** Changing only the stripping branch to:
  ```js
  if (arg.startsWith(prefix) && arg.length > prefix.length) continue;
  ```
  passes the entire Node dispatcher suite, exit 0, while incorrectly returning `['--provider=', 'x']` for `['--provider=', 'x']`. The candidate handles this correctly; the suite does not protect it. This coverage gap supplements the blocking Bar 3 assertion defect.

- **Bar 4 — verification and compatibility.** Candidate tree identity matched exactly, and reviewed files matched the candidate. Reruns produced:
  - `node scripts/test-pairprog-cli.mjs`: exit 0.
  - Default `bash scripts/test-pairprog-cli-setup.sh`: exit 1 because that Bash could not find Node.
  - Same setup test through Git Bash: exit 0.
  - `node scripts/pairprog-cli.mjs --version`: exit 0, `pairprog 0.1.0-local`.

  Exporting the functions adds no execution behavior. A fresh import produced no stdout/stderr and created no configured home directory. Execution through a verified filesystem symlink printed the version and exited 0. No additional error-handling or portability regression was found in the change.

**Bar 4 — review cleanup:** automatic approval review rejected temporary-directory deletion as “blocked by policy.” Review files remain at `[machine-local temp path redacted]`; candidate files were unchanged.
~~~~

### Round 2

Record: line 82 of `rollout-2026-09-22T03-04-31-01a0c825-1e16-7d73-a101-0956682b1bba.jsonl`; `payload.phase=final_answer`; timestamp `2026-09-22T08:08:44.213Z` (UTC).

~~~~text
REFUSE 8c333ff65c2f755c44b8306aabe677a8c0389567

- **Bar 3 — blocking: the expected pair blesses a counterexample to the declared agreement.** For `['--provider','--provider','mock']`, I measured `readOption → 'D'` and `stripOption → []`. The reader refuses the following `--provider`; the stripper removes it. [The fixture](C:/code/Conjugal/scripts/test-pairprog-cli.mjs:380) accurately records this behavior, but the declaration still requires preservation of the declined token **for each shape**. A test comment acknowledging the exception does not narrow that declared bar. Before S24, stripping this input returned `['mock']`; the candidate returns `[]`.

- **Bar 3 — two additional mutants survive the entire Node suite.** Independently tested:
  - Replace strip’s `arg.startsWith(prefix)` with `arg.startsWith(name)`. The suite passes, but `['--provider','--provider-mode','x']` incorrectly loses `--provider-mode`.
  - Replace `token !== undefined` with `Boolean(token)`. The suite passes, but `['--provider','','x']` changes from `('', ['x'])` to `('D', ['', 'x'])`.
  
  These are coverage gaps, separate from the blocking declaration mismatch.

- **Bar 3 — all twelve expected return pairs are correct.** Both functions are now measured directly; the primary assertions have no derived oracle. The option-name membership assertion and repeated bar-1 assertion are redundant. The duplicate-fixture explanation is inaccurate: `['a','--provider','v','a']` also passes the old membership oracle. `['v','--provider','v','x']` actually exposes that oracle’s occurrence-versus-membership error; I reproduced both.

- **Bars 1 and 2 — pass.** I reproduced rejection of all four named mutants. The direct parser tests also pass independently of earlier tests’ fixture setup. I found no new error-handling, cleanup, or portability defect in the implementation change.

- **Bar 4 — pass under Git Bash.** The candidate tree identity matched exactly. The Node suite exited 0; the setup suite exited 0 using `C:\Program Files\Git\bin\bash.exe`; `--version` exited 0 with `pairprog 0.1.0-local`. The initial bare `bash` resolved to Windows’ WSL launcher and failed because that environment lacked Node on PATH.
~~~~
