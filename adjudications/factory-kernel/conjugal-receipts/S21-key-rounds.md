# S21 — key rounds, receipts (Conjugal, `S21-assembly-time-completeness-and-silent-figure-loss`)

Outcome heading (Conjugal): `Outcome — PARKED at the three-round ceiling, NOT ACCEPTED (counts ZERO). Three real bugs fixed.`

Ordering / identity / delivery witness (`python coordination/kernel-dogfood/check-ordering.py`, AUTHOR dates, read-only, run 2026-09-26): `S21 NO-CANDIDATE-CITED decl=a625bbc@2026-09-21T23:05:38-05:00 cand=none identity=none delivered=unwitnessed outcome=DELIVERED-NOT-ACCEPTED note=bus-delivery-no-sha`

Key: class `codex-openai`. Every round below is a `codex exec` session (`session_meta.payload.originator=codex_exec`, `model_provider=openai`); `turn_context.payload.model` and `.effort` are quoted per round. Producer: Claude (class `claude-anthropic`), a different independence class.

Source files are Codex CLI rollout logs (JSONL), machine-local under `~/.codex/sessions/2026/09/<DD>/`. Rollout SHA-256 is of the whole file. **Excerpt** = the last `response_item` record with `payload.type=message`, `payload.role=assistant`, `payload.phase=final_answer`; its bytes are the UTF-8 concatenation of `payload.content[].text`, no trailing newline. **Verdict-line** SHA-256 is of the single verdict line of that excerpt, UTF-8, no newline (the S12/S13 convention). Extracted 2026-09-26, read-only, by a Claude Code receipt-extraction agent.

| Round | Tree named by the key | Model / effort | Rollout (`~/.codex/sessions/2026/09/<DD>/`) | Bytes | Rollout SHA-256 | Final-answer record | Excerpt bytes | Excerpt SHA-256 | Verdict line (verbatim) | Verdict-line SHA-256 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `cfac812ec6eb4a0636100bf48263ea62fcba6474` | `gpt-6-astra` / `high` | 21/`rollout-2026-09-21T23-15-18-01a0c753-429e-7152-9a26-ff62c4ba8832.jsonl` | 556,825 | `0e658236b286f1d8773ec43649dd15bc650b47d6a9785aa9f45950000ceb85a7` | line 87, `2026-09-22T04:19:15.421Z` | 4630 | `344b39a962fcedb64f83998113d051ddea1bb94293e799553b0cb3ca3f61b62a` | `REFUSE cfac812ec6eb4a0636100bf48263ea62fcba6474` | `1a9700db816b384ef59256c5e361e574d0bdad70fc4d96c0aa37ee815528cbd7` |
| 2 | `65ac0367745b3e211937ee9d014909e9ab6b3bb7` | `gpt-6-astra` / `high` | 21/`rollout-2026-09-21T23-30-50-01a0c761-7be3-7bc0-8580-5f0ea673d392.jsonl` | 795,517 | `d32f7c7f081946981ea822d160aa5885165865779e6e079c9b03cf99ec1ba20e` | line 104, `2026-09-22T04:35:56.962Z` | 3628 | `24e755dfc1c6a9e188117b585a3cf5c4488bb0d39149cd62bfd79346d598f3fa` | `REFUSE 65ac0367745b3e211937ee9d014909e9ab6b3bb7` | `ff7357edca09826f682235fa9b9c496bd701e5c45facbe854f82784ac3f8d0ea` |
| 3 | `2fba32f3e3f22ef15d41f6eccaec6876e3bb20d6` | `gpt-6-astra` / `high` | 22/`rollout-2026-09-22T00-20-21-01a0c78e-d4a9-7f81-81d4-e47a719e2255.jsonl` | 766,518 | `d93080e741cdb284fe1403ac1200305f16b2309047948deefb312a70e50abd05` | line 133, `2026-09-22T05:27:35.263Z` | 2430 | `e5d1c11e898a69bf849d84e1b5ef0225bcd6cd4e708f60697987afbdf51782a5` | `REFUSE 2fba32f3e3f22ef15d41f6eccaec6876e3bb20d6` | `c285becabb23ed53b7f3f5fc13f090f0fbd89d0bea6ddcb9a68d186e9d018b78` |

Every excerpt was extracted from, and hashed against, its rollout file in the same pass; each verdict line is byte-present in its excerpt.

## Reconciliation with the value recorded in the Conjugal Outcome

| Round | Recorded "verdict SHA-256" | What those recorded bytes actually are | Reproduced from the ROLLOUT? | Recorded rollout SHA reproduced? |
|---|---|---|---|---|
| 1 | `93783229b796f01c40b15ae88fc8269c5feebfb788cb2a57` | SHA-256 of the producer's machine-local stdout capture of `codex exec`: the final message re-emitted through the Windows console (CRLF line ends; non-ASCII mangled via cp437, e.g. an em dash becomes `ΓÇö`). Capture hash reproduced: yes; capture equals the rollout excerpt after undoing CRLF and cp437: yes | **NOT REPRODUCED from rollout** | none recorded |
| 2 | `4a1a5e8df444697fb536c291b281ce4918ed99fbd5977fc4` | SHA-256 of the producer's machine-local stdout capture of `codex exec`: the final message re-emitted through the Windows console (CRLF line ends; non-ASCII mangled via cp437, e.g. an em dash becomes `ΓÇö`). Capture hash reproduced: yes; capture equals the rollout excerpt after undoing CRLF and cp437: yes | **NOT REPRODUCED from rollout** | none recorded |
| 3 | `60945affe01734850452cf3d88547f7af79ae7b8fc38a3f1` | SHA-256 of the producer's machine-local stdout capture of `codex exec`: the final message re-emitted through the Windows console (CRLF line ends; non-ASCII mangled via cp437, e.g. an em dash becomes `ΓÇö`). Capture hash reproduced: yes; capture equals the rollout excerpt after undoing CRLF and cp437: yes | **NOT REPRODUCED from rollout** | none recorded |

## Excerpts (verbatim)

Machine-local temp paths inside an excerpt are replaced with `[machine-local temp path redacted]`; each digest above is of the **unredacted** original bytes, so a holder of the rollout can verify by re-extracting the record. No other change.

### Round 1

Record: line 87 of `rollout-2026-09-21T23-15-18-01a0c753-429e-7152-9a26-ff62c4ba8832.jsonl`; `payload.phase=final_answer`; timestamp `2026-09-22T04:19:15.421Z` (UTC).

~~~~text
REFUSE cfac812ec6eb4a0636100bf48263ea62fcba6474

Tree identity verified. Findings:

1. **Bars 1–2 — substring counting does not establish exact chapter equality or membership.** [assemble.mjs:235](C:/code/Conjugal/docs/product/pdf/src/assemble.mjs:235) checks neither chapter boundaries nor surrounding content. In-memory checks against the real assembled HTML returned no problems after replacing `virtual-ten-migration`’s body with an HTML comment or attribute containing that body, and after adding an undeclared chapter. Substring fixtures also demonstrated both error directions: legitimate separate chapters can be rejected when one contains another’s body, while omitting the smaller chapter can pass. Overlapping occurrences are skipped (`aba` in `ababa` counts once). These are exact substring searches, not equality checks between complete chapter bodies.

2. **Bars 1–3 — an empty fragment hangs the verifier.** At [assemble.mjs:241](C:/code/Conjugal/docs/product/pdf/src/assemble.mjs:241), `indexOf('', i)` succeeds indefinitely while `i += body.length` advances zero characters. An isolated execution of the actual function with an empty-body fixture timed out. The “missing-body” probe substitutes nonempty text, so it misses this case.

3. **Bars 1 and 3 — production wiring exists, but the refusal test does not exercise it.** Both `assembleAll()` and `assembleOne('compendium')` call `compendiumHtml()` before writing; I found no other normal producer of that output in the reviewed pipeline. However, the verifier compares an in-memory compendium against freshly reread fragments, not the actual standalone outputs. The renderer subsequently reads disk HTML. More decisively, [assembly-refusal-probe.mjs:40](C:/code/Conjugal/docs/product/pdf/src/assembly-refusal-probe.mjs:40) merely checks stale HTML against changed source and throws itself. It invokes neither the compendium builder nor `build.mjs`. Removing the verification call from `compendiumHtml()` would leave this test passing. Missing, duplicated and altered bodies are therefore not proven to refuse through `build.mjs`, as bar 3 requires.

4. **Bar 4 — unknown figure refusal remains incomplete.** The regex is unchanged from the predecessor. `<!-- FIG: p2_threat -->` does not match, survives as an invisible comment, and triggers neither lookup nor refusal. Also, `id in FIGURES` accepts inherited properties: the actual replacement function converted `<!-- FIG: constructor -->` into `function Object() { [native code] }` without refusing. Existing legitimate IDs still resolve. The empty, per-ID `PENDING_FIGURES` set fits the declared escape hatch; these failures occur outside it.

5. **Bar 3 — the refusal probe is unsafe under interruption and can pass for unrelated failures.** [assembly-refusal-probe.mjs:29](C:/code/Conjugal/docs/product/pdf/src/assembly-refusal-probe.mjs:29) treats any caught error—including damage-write, import or stale-file-read failure—as successful refusal. Forced termination can leave the tracked source damaged because `finally` need not execute. A thrown restoration write escapes before the exit-2 check, ordinarily exiting 1 instead. Exit 2 only reports a detected mismatch; it cannot restore or protect the tree. Concurrent runs can also overwrite each other’s input.

6. **Bar 5 — current replay passed, but the test asserts less than its name.** All eight requested tests passed, and the separate `bad-figure` probe exited 0 with the expected refusal. I independently confirmed the tracked input was restored and all 14 PDF hashes were unchanged. An in-memory predecessor/candidate assembly comparison, using identical fixed Git metadata, produced identical HTML for all 14 outputs. However, the replay test itself checks placeholder membership and job counts—not emitted figure content, exact output equality or PDF hashes.

7. **Bar 6 — the document-count invariant is vacuous.** [assembly.test.mjs:115](C:/code/Conjugal/docs/product/pdf/src/assembly.test.mjs:115) repeatedly verifies the same full compendium, then filters its already-empty problem list by different manifest prefixes. No arm changes the number of documents assembled. The corrected one-character mutation does affect a real body, and the arms differ, but the count-invariance claim is untested.

8. **Bar 7 — independent reversion evidence is missing.** The supplied tests contain no per-defect revert-and-rerun matrix or explicit accounting of coupled failures. The production-gate deletion gap above makes this material: green tests do not establish that the refusal mechanism remains connected.
~~~~

### Round 2

Record: line 104 of `rollout-2026-09-21T23-30-50-01a0c761-7be3-7bc0-8580-5f0ea673d392.jsonl`; `payload.phase=final_answer`; timestamp `2026-09-22T04:35:56.962Z` (UTC).

~~~~text
REFUSE 65ac0367745b3e211937ee9d014909e9ab6b3bb7

1. **Bars 1–2 — The slot regex is not a structural reader.** [assemble.mjs:253](/C:/code/Conjugal/docs/product/pdf/src/assemble.mjs:253). Boundary fixtures returned `[]` for a whole slot inside a comment or quoted attribute. An extra chapter with reordered attributes also returned `[]` against the actual assembled compendium. Conversely, a matching fragment containing `\n</main>` inside a valid comment or quoted attribute falsely fails equality; nested `<main>` also truncates extraction. The reader neither establishes real element boundaries nor accounts for all chapters.

2. **Bars 1, 5, 7 — Actual standalone bodies are never compared.** [assemble.mjs:260](/C:/code/Conjugal/docs/product/pdf/src/assemble.mjs:260) compares slots with freshly read fragments. In an isolated copy, I replaced the standalone template’s `${fragment(doc)}` with `<p>STANDALONE BODY LOST</p>`. **All 11 tests still passed**, although every standalone differed from its compendium chapter. This is assembly damage, within the declared scope—not source damage. The independent defect produced no red case.

3. **Bar 3 — “BOTH producers” exercises one producer twice.** [assembly.test.mjs:33](/C:/code/Conjugal/docs/product/pdf/src/assembly.test.mjs:33). `probe(mode)` forwards only `mode`; `probe(...['empty-body', '--via-all'])` discards the second argument. Both iterations invoke `assembleOne`. Explicitly running `--via-all` worked, but the committed test does not protect that route.

4. **Bars 3, 7 — Production refusal evidence covers empty content, not the declared composition failures.** [assembly-refusal-probe.mjs:36](/C:/code/Conjugal/docs/product/pdf/src/assembly-refusal-probe.mjs:36). No mode removes, duplicates, or alters a chapter during composition. The other refusal modes exercise figure lookup; `missing-body` intentionally succeeds. The probe never invokes `build.mjs`, either. Thus missing/duplicated/altered chapter refusal through the build’s exit status remains unproven. Removing the entire verifier demonstrates wiring for empty-body only.

5. **Bar 4 — Some unknown figure placeholders still remain invisible.** [assemble.mjs:115](/C:/code/Conjugal/docs/product/pdf/src/assemble.mjs:115). Both `<!-- FIG: p2>threat -->` and `<!-- FIG: p2 threat -->` survive unchanged without refusal. The pattern does not match “any non-empty id” as claimed. I did **not** observe swallowing adjacent, properly terminated comments or markup: excluding `>` prevents crossing their closing delimiter. The remaining failure is incomplete recognition.

6. **Bar 5 — Probe cleanup restores the source but leaves damaged generated output.** [assembly-refusal-probe.mjs:60](/C:/code/Conjugal/docs/product/pdf/src/assembly-refusal-probe.mjs:60). After successful `missing-body --via-all`, the generated roadmap and compendium still contained replacement prose. Running the verifier against that compendium after source restoration reported a mismatch. I regenerated all 14 HTML outputs afterward.

**Verification, bars 1–7:** The candidate tree matched exactly. The requested suite passed 11/11; all five header modes returned exit 0 with their expected outcomes, both normally and with explicit `--via-all`. Actual chapter reordering, duplication replacing another chapter at unchanged count, and body whitespace changes were correctly refused. Bar 6’s altered-body control passed; its count correction is explicit in the tests, although the declaration still states the superseded invariant. All 62 hashed source, asset, and PDF files remained unchanged.
~~~~

### Round 3

Record: line 133 of `rollout-2026-09-22T00-20-21-01a0c78e-d4a9-7f81-81d4-e47a719e2255.jsonl`; `payload.phase=final_answer`; timestamp `2026-09-22T05:27:35.263Z` (UTC).

~~~~text
REFUSE 2fba32f3e3f22ef15d41f6eccaec6876e3bb20d6

- **Bars 1–2 — blocking: the slot reader remains unsound.** In [assemble.mjs](/C:/code/Conjugal/docs/product/pdf/src/assemble.mjs:150), `</main data-x>` and `<main/>` pass the fragment guard. The former closes the HTML element while the regex counts subsequent prose as inside it. Separately, commenting out a chapter slot produced **zero verification problems**, although HTML parsing found only 12 main elements. Wrapping the compendium’s sections in a comment also left **all 12 tests green**. Mechanism: regex matches are still mistaken for actual HTML chapter boundaries.

- **Bar 6 — the declared invariant remains untested.** The “CORRECTION” test changes the manifest while retaining all 13 slots, which tests inconsistent inputs. Varying both the slots and matching manifest preserves the intended invariant: I measured **zero clean-arm problems and one altered-arm problem at 1, 2, 6 and 13 documents**. The assertion that document-count invariance cannot exist is incorrect.

- **Bar 7 — another coupling is undisclosed.** Removing only the slot-count check reddened both **bar 2’s duplicated-slot test and bar 6’s count test**. The recorded bar 1/bar 6 coupling is accurate, but it is not the only coupling.

- **Bar 3 — required integration coverage is incomplete.** The test invokes both assembler APIs, but never `build.mjs`; its refusal fixture covers only an empty fragment. Missing, duplicated and altered composition are not tested through the required build entry point.

- **Bar 5 — metadata caching can become stale within one process.** The cache keys contain no repository revision and never expire. In an isolated checkout, advancing HEAD between assemblies left the old commit in the cover; importing a fresh module produced the new commit. This is a correctness limitation for repeated builds or concurrent repository changes, though not the principal refusal reason.

- **Bars 1, 4–5 — confirmed improvements and replay.** The standalone comparison now uses distinct rendered templates: replacing its body caused `build.mjs --only compendium` to refuse. The candidate tree matched exactly. The requested suite passed **12/12 in 135 seconds**; all five probe modes passed with and without `--via-all`. All 14 PDF SHA-256 hashes matched the candidate. These successful checks do not resolve the structural false acceptance above.
~~~~
