# S23 — key rounds, receipts (Conjugal, `S23-readoption-consumes-the-next-flag`)

Outcome heading (Conjugal): `Outcome — PARKED at the three-round ceiling, NOT ACCEPTED (counts ZERO). The product defect is fixed.`

Ordering / identity / delivery witness (`python coordination/kernel-dogfood/check-ordering.py`, AUTHOR dates, read-only, run 2026-09-26): `S23 NO-CANDIDATE-CITED decl=e0f43f6@2026-09-22T02:09:36-05:00 cand=none identity=none delivered=unwitnessed outcome=DELIVERED-NOT-ACCEPTED note=bus-delivery-no-sha`

Key: class `codex-openai`. Every round below is a `codex exec` session (`session_meta.payload.originator=codex_exec`, `model_provider=openai`); `turn_context.payload.model` and `.effort` are quoted per round. Producer: Claude (class `claude-anthropic`), a different independence class.

Source files are Codex CLI rollout logs (JSONL), machine-local under `~/.codex/sessions/2026/09/<DD>/`. Rollout SHA-256 is of the whole file. **Excerpt** = the last `response_item` record with `payload.type=message`, `payload.role=assistant`, `payload.phase=final_answer`; its bytes are the UTF-8 concatenation of `payload.content[].text`, no trailing newline. **Verdict-line** SHA-256 is of the single verdict line of that excerpt, UTF-8, no newline (the S12/S13 convention). Extracted 2026-09-26, read-only, by a Claude Code receipt-extraction agent.

| Round | Tree named by the key | Model / effort | Rollout (`~/.codex/sessions/2026/09/<DD>/`) | Bytes | Rollout SHA-256 | Final-answer record | Excerpt bytes | Excerpt SHA-256 | Verdict line (verbatim) | Verdict-line SHA-256 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `705dab7b7b73b5e66190c242c7688bed8bb30e99` | `gpt-6-astra` / `high` | 22/`rollout-2026-09-22T02-13-08-01a0c7f6-15f5-7ff3-be22-ce3517616f04.jsonl` | 555,794 | `ec21f06812ab0ceffd9865f9af9334fe0919d43772830693c4e9dd96be0353eb` | line 70, `2026-09-22T07:16:27.512Z` | 4428 | `028e01a2e9fb69146d5bef05fc39a7c72db64dd96f5e8b668143027f04ad53b8` | `REFUSE 705dab7b7b73b5e66190c242c7688bed8bb30e99` | `3dfcd71dfde036b1137e681ee18e932a9698d95968fa59ceeb47f0cd9e2fa6a1` |
| 2 | `99dcd0e269dc6c3010fc3d3c9c44fd70526695a1` | `gpt-6-astra` / `high` | 22/`rollout-2026-09-22T02-20-18-01a0c7fc-a3c9-7021-b7d2-86b259d60788.jsonl` | 662,930 | `7c178c1fd212f8324a6231cb218665fff4c4b15779ed036f9caa2459b5bb566d` | line 74, `2026-09-22T07:23:18.760Z` | 2298 | `07aa30a142ce586c59b6ba88c87328c5d8c162654e7eb4e14a43ddaf1cf4d91c` | `REFUSE 99dcd0e269dc6c3010fc3d3c9c44fd70526695a1` | `8e2a934d384da98d9c61cd9a221e530969f0dcc3cecf22fd226c698b1ff2a359` |
| 3 | `ddc897847b6868e48666a8747c365042c50d0650` | `gpt-6-astra` / `high` | 22/`rollout-2026-09-22T02-27-05-01a0c802-d951-7180-91bf-5a7a26ebefe0.jsonl` | 713,125 | `c1951d3e12085ca7ee50cf5ca1f1a0bed4d13276d63bdfd159c8b3600ace5dd7` | line 88, `2026-09-22T07:30:42.364Z` | 3059 | `dab4df2446ecb57c7430a9fad8d97d48d937e61c83c593d8fbeb7131c488b91e` | `REFUSE ddc897847b6868e48666a8747c365042c50d0650` | `e6fed9e6c23d39d5388dc4414b8c0cfb6fbd0f5261878588a976a58c8798429a` |

Every excerpt was extracted from, and hashed against, its rollout file in the same pass; each verdict line is byte-present in its excerpt.

## Reconciliation with the value recorded in the Conjugal Outcome

| Round | Recorded "verdict SHA-256" | What those recorded bytes actually are | Reproduced from the ROLLOUT? | Recorded rollout SHA reproduced? |
|---|---|---|---|---|
| 1 | `1a71571b6ede3430c5fa5cea98e21550354ded33` | SHA-256 of the producer's machine-local stdout capture of `codex exec`: the final message re-emitted through the Windows console (CRLF line ends; non-ASCII mangled via cp437, e.g. an em dash becomes `ΓÇö`). Capture hash reproduced: yes; capture equals the rollout excerpt after undoing CRLF and cp437: yes | **NOT REPRODUCED from rollout** | none recorded |
| 2 | `b33d213ce0ad88f6e5df6053b3a6a308e829bb72` | SHA-256 of the producer's machine-local stdout capture of `codex exec`: the final message re-emitted through the Windows console (CRLF line ends; non-ASCII mangled via cp437, e.g. an em dash becomes `ΓÇö`). Capture hash reproduced: yes; capture equals the rollout excerpt after undoing CRLF and cp437: yes | **NOT REPRODUCED from rollout** | none recorded |
| 3 | `0df125a1c12033ea08a6f75ef3e5316cf42e4400` | SHA-256 of the producer's machine-local stdout capture of `codex exec`: the final message re-emitted through the Windows console (CRLF line ends; non-ASCII mangled via cp437, e.g. an em dash becomes `ΓÇö`). Capture hash reproduced: yes; capture equals the rollout excerpt after undoing CRLF and cp437: yes | **NOT REPRODUCED from rollout** | none recorded |

## Excerpts (verbatim)

Machine-local temp paths inside an excerpt are replaced with `[machine-local temp path redacted]`; each digest above is of the **unredacted** original bytes, so a holder of the rollout can verify by re-extracting the record. No other change.

### Round 1

Record: line 70 of `rollout-2026-09-22T02-13-08-01a0c7f6-15f5-7ff3-be22-ce3517616f04.jsonl`; `payload.phase=final_answer`; timestamp `2026-09-22T07:16:27.512Z` (UTC).

~~~~text
REFUSE 705dab7b7b73b5e66190c242c7688bed8bb30e99

- **Bar 2 — blocking: the tests do not exercise the declared inputs.** At [test-pairprog-cli.mjs:323](/C:/code/Conjugal/scripts/test-pairprog-cli.mjs:323), `dashValue` is an absolute path; its first character is not `-`. Neither `--retention-days -1` nor the trailing-option/default-`D` equality is tested. In a temporary copy, I changed the guard to reject **every** `-`-prefixed value. The entire suite still passed, despite violating Bar 2.

- **Bar 3 — blocking: the escape-hatch test misses its defining case.** At [test-pairprog-cli.mjs:329](/C:/code/Conjugal/scripts/test-pairprog-cli.mjs:329), the value is another absolute path, not `--json`. This tests ordinary equals syntax, not the declared equality. The implementation itself is correct: `slice(prefix.length)` preserves the complete suffix, so `--out=--json` yields `--json`, and `--out=--a=b=c` yields `--a=b=c`. I verified both directly against the extracted candidate function.

- **Bars 1 and 4 — the CLI observation is weaker than the declared equality.** The test checks successful exit and absence of `cwd/--json`; it does not establish that `readOption` returned exactly `''`. Another return value directing output elsewhere could pass. `resolveSupportOut` also maps multiple falsy values to the same default destination. Bar 4 is covered for the reported defect, but Bar 1 has no independent equality assertion. Removing the guard in a temporary copy made the suite fail specifically because `--json` was created. Thus the principal regression assertion works.

- **Bars 1–3 — parser edge cases behave correctly under the declared policy.** Direct candidate-function checks gave:

  | Input | Result | Changed? |
  |---|---|---|
  | Following value exactly `--` | Supplied default | Yes; previously literal `--` |
  | Following `-1` | `-1` | No |
  | Following `-weird.zip` | `-weird.zip` | No |
  | Option at end of argv | Supplied default | No |
  | `--out one --out two` | `one` | No; first occurrence wins |
  | `--out --out two` | Supplied default | Yes; previously `--out` |
  | `--out=` | Empty string | No; support-bundle subsequently chooses its default path |

  None of these changes contradicts the declaration. The rule is a **`--` prefix** test, including the bare `--` token, rather than an equality test.

- **Bar 1 — provider forwarding remains inconsistent with the parsing rule.** [stripOption:80](/C:/code/Conjugal/scripts/pairprog-cli.mjs:80) still unconditionally skips the token following `--provider`. With provider default `mock`, `--provider --message hello` now selects `mock` but forwards only `hello`, losing `--message`. I reproduced that result. This stripping defect predates the patch, but the claimed protection does not extend through the provider caller.

  The other callers have these effects:
  - `--port`: a following long flag previously became an invalid port override; now the empty default leaves the inherited/configured port available.
  - `--wait-ms`: effective behavior remains 15000 ms; previously the swallowed flag became `NaN` and triggered that same fallback.
  - `--retention-days`: effective behavior remains 30 days for the same reason.
  
  I found no legitimate caller dependency on swallowing a long flag. `start` removes `--json` before option parsing, so its observations are not always equivalent to parsing raw argv.

- **Bars 4 and 5 — assertion reliability and reruns.** The new targets start absent in a fresh temporary directory, so unrelated preexisting files do not explain their passes. Every invocation checks exit zero, preventing an ordinary early failure from satisfying the complete test. However, successful exit plus file existence does not verify archive contents. No additional introduced portability or cleanup defect was found.

  `node scripts/test-pairprog-cli.mjs` passed. The setup test initially failed because the default Windows Bash could not find Node; rerunning `scripts/test-pairprog-cli-setup.sh` with Git Bash passed.

- **Bar 5 — mutation claim needs correction.** The declaration says removing the guard leaves Bar 5 green, but Bar 5 names the entire test script, which now includes the regression assertion. My guard-removal run exited **1**. Distinguish the unchanged baseline tests from the expanded suite.

The candidate tree matched the supplied OID. Repository files were left unchanged.
~~~~

### Round 2

Record: line 74 of `rollout-2026-09-22T02-20-18-01a0c7fc-a3c9-7021-b7d2-86b259d60788.jsonl`; `payload.phase=final_answer`; timestamp `2026-09-22T07:23:18.760Z` (UTC).

~~~~text
REFUSE 99dcd0e269dc6c3010fc3d3c9c44fd70526695a1

- **Blocking — bars 1 and 2:** The default-destination assertions still cannot prove the declared return values. Changing the guard’s `return defaultValue` to `return null` passes the entire CLI suite. Direct evaluation then returns `null` instead of `''` for bar 1 and instead of `'D'` for bar 2’s trailing-option case. `resolveSupportOut()` accepts any falsy value as the default destination, masking both errors. Add strict assertions for the declared function results. See [default assertions](C:/code/Conjugal/scripts/test-pairprog-cli.mjs:326).

- **Blocking — bar 2:** The corrected `-weird.zip` fixture exercises a single-dash token, but still omits the declared negative-number input. Adding `|| /^-\d/.test(next)` to the rejection condition passes the entire CLI suite while `readOption(['--retention-days','-1'], '--retention-days', '7')` incorrectly returns `'7'`. Assert the exact declared `'-1'` result. See [single-dash fixture](C:/code/Conjugal/scripts/test-pairprog-cli.mjs:336).

- **Bars 2, 3 and 4 — isolation:** No leftover-file false pass found in the current order. The working directory starts fresh, both default-destination cases clear the bundles directory, and earlier successful cases do not create the filenames asserted by later cases. Bar 3 now genuinely supplies `--out=--json`. Independently reproduced: deleting the guard fails on the created `--json` file; rejecting every dash-leading token fails on `-weird.zip`.

- **Bars 1–5 — scope:** Deferring `stripOption` is honest under these specific bars. I reproduced `--provider --message hello` becoming `{provider:"", args:["hello"]}`, but no declared bar requires provider argument preservation. The residual remains real without falsifying a declared bar.

- **Bar 5 — validation:** Candidate tree verified exactly; the candidate’s direct parser results satisfy the declared equalities. `node scripts/test-pairprog-cli.mjs` passes. The setup suite passes with Git Bash; the initial system-Bash invocation failed because Node was unavailable on its PATH. Both surviving mutants above were executed against candidate-derived copies with unchanged tests. The refusal concerns test discrimination, not a demonstrated defect in the candidate parser.
~~~~

### Round 3

Record: line 88 of `rollout-2026-09-22T02-27-05-01a0c802-d951-7180-91bf-5a7a26ebefe0.jsonl`; `payload.phase=final_answer`; timestamp `2026-09-22T07:30:42.364Z` (UTC) (redacted).

~~~~text
REFUSE ddc897847b6868e48666a8747c365042c50d0650

- **Bar 5 — blocking invocation regression:** [The entry guard](/C:/code/Conjugal/scripts/pairprog-cli.mjs:1175) silently skips `main()` through a symlink. Reproduced against candidate and parent: `node <file-symlink> --version` prints `pairprog 0.1.0-local` before this change; the candidate prints nothing and exits 0. A directory junction produces the same regression. `path.resolve()` does not resolve filesystem links. This also affects Unix npm bin links, whose installation uses symlinks. [npm documentation](https://docs.npmjs.com/cli/v11/configuring-npm/package-json/#bin). **Mechanism: lexical path equality incorrectly determines whether this module is the CLI entry point.**

- **Bar 5 — other entry paths:** An actual npm-generated Windows `.cmd` shim passed. Windows directory-case, drive-case, and slash/backslash variations tested successfully. Ordinary `node --eval` imports correctly remain inactive. Thus the guard is useful but incomplete.

- **Bars 1–3 — direct assertions pass:** All four expressly declared equalities are now asserted. The nine cases include five additional checks; none has an incorrect expected value. The second case’s “not a bare null” rationale overlaps the first assertion, but its nonempty default additionally catches hardcoded `''`. The `null`, negative-number rejection, and removed-guard mutations produce values rejected by these assertions.

- **Bars 1–3 — surviving mutant, nonblocking under the exact declared inputs:** Replacing `next.startsWith('--')` with `['--json', '--'].includes(next)` passes the entire suite, verified in an isolated copy. It incorrectly returns `'--verbose'` for `readOption(['--out','--verbose'], '--out', '')`. This exposes limited prefix coverage, but does not falsify the explicitly enumerated equalities.

- **Bar 4 — passes:** The end-to-end case creates the default bundle without creating `--json`. Minor specification mismatch: the test asserts `!existsSync(...)`; the declaration explicitly requests a directory-listing assertion.

- **Bar 5 — import behavior:** Exporting introduces no additional operational side effects. The guard intentionally suppresses previous import-triggered execution: importing with `status --json` previously created the home layout; the candidate creates none. Import still evaluates `dashboard/load-config.mjs`, including its existing `PAIRPROG_USER_CONFIG_PATH` environment read and home-directory fallback.

- **Bar 5 — reruns:** Dispatcher suite: exit 0. Setup suite under Git Bash: exit 0. Direct `--version`: exit 0, expected output. The initial unqualified `bash` selected WSL and failed because Node was unavailable there. The literal named bar passes; refusal rests on the demonstrated invocation regression above.

**Bar 5 — review cleanup:** Automatic approval review rejected deletion of the temporary review directory with “blocked by policy.” `[machine-local temp path redacted]` remains; repository source files were unchanged.
~~~~
