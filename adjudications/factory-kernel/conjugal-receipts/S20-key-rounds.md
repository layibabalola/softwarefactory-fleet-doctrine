# S20 — key rounds, receipts (Conjugal, `S20-compendium-unrebuildable-and-five-documents-short`)

Outcome heading (Conjugal): `Outcome — PARKED at the three-round ceiling, NOT ACCEPTED (counts ZERO). The PRODUCT defect is FIXED.`

Ordering / identity / delivery witness (`python coordination/kernel-dogfood/check-ordering.py`, AUTHOR dates, read-only, run 2026-09-26): `S20 NO-CANDIDATE-CITED decl=da95e91@2026-09-21T21:32:56-05:00 cand=none identity=none delivered=unwitnessed outcome=DELIVERED-NOT-ACCEPTED note=bus-delivery-no-sha`

Key: class `codex-openai`. Every round below is a `codex exec` session (`session_meta.payload.originator=codex_exec`, `model_provider=openai`); `turn_context.payload.model` and `.effort` are quoted per round. Producer: Claude (class `claude-anthropic`), a different independence class.

Source files are Codex CLI rollout logs (JSONL), machine-local under `~/.codex/sessions/2026/09/<DD>/`. Rollout SHA-256 is of the whole file. **Excerpt** = the last `response_item` record with `payload.type=message`, `payload.role=assistant`, `payload.phase=final_answer`; its bytes are the UTF-8 concatenation of `payload.content[].text`, no trailing newline. **Verdict-line** SHA-256 is of the single verdict line of that excerpt, UTF-8, no newline (the S12/S13 convention). Extracted 2026-09-26, read-only, by a Claude Code receipt-extraction agent.

| Round | Tree named by the key | Model / effort | Rollout (`~/.codex/sessions/2026/09/<DD>/`) | Bytes | Rollout SHA-256 | Final-answer record | Excerpt bytes | Excerpt SHA-256 | Verdict line (verbatim) | Verdict-line SHA-256 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `4d38fd3126f7f79140628a6d30220ec30df6daba` | `gpt-6-astra` / `high` | 21/`rollout-2026-09-21T21-44-57-01a0c700-8d0e-72f1-aee3-b87ec962cead.jsonl` | 712,178 | `5cd5a6594fcbe3f148df5770d9c479cba1b7d8d4bca4ee024ffbbce2a2bc51ad` | line 100, `2026-09-22T02:49:01.029Z` | 4618 | `bdbe871775483ba9de6667ae18c2fb1b46032985645a90ecc39cbb2496ac99e5` | `REFUSE 4d38fd3126f7f79140628a6d30220ec30df6daba` | `663ced5991c96916466cb779046aebea39df21f7f42ae8121c5b42bec468f35f` |
| 2 | `5bda53c3986caa824179cd10c1d58c59f83295ef` | `gpt-6-astra` / `high` | 21/`rollout-2026-09-21T22-01-37-01a0c70f-cd88-7303-8eed-cb1f5521e217.jsonl` | 816,395 | `b7c930d9c8a035f80b8e6499ecda6bf94876e38ea16af31e9c072a12d6a864d1` | line 102, `2026-09-22T03:07:07.026Z` | 4622 | `2c0a4c052969252dfc247bcd34c0e769710e6a7abc8e05a089da3580b0b2b690` | `REFUSE 5bda53c3986caa824179cd10c1d58c59f83295ef` | `c9173228d5c34160f9aa5006a00287af466a990287bf61969a1631149f13a64d` |
| 3 | `27c12bf34dc51432f1f596c4019b60dbf3508f82` | `gpt-6-astra` / `high` | 21/`rollout-2026-09-21T22-27-22-01a0c727-62f7-78e3-addc-4a874928e97d.jsonl` | 736,709 | `93cc6b3955bc3e574def82defd16124da2627d62a4f2f3d1a178c7abee8f6bae` | line 111, `2026-09-22T03:31:45.522Z` | 2353 | `377167c13b9b77c4e238b2dec0df211d55384e188edf4f1de2f204a4c3703cc7` | `REFUSE 27c12bf34dc51432f1f596c4019b60dbf3508f82` | `2929a67bb3aead224eb2eda4a5cc004a4faba9b558f6830dfda558e7b1d7da4d` |

Every excerpt was extracted from, and hashed against, its rollout file in the same pass; each verdict line is byte-present in its excerpt.

## Reconciliation with the value recorded in the Conjugal Outcome

| Round | Recorded "verdict SHA-256" | What those recorded bytes actually are | Reproduced from the ROLLOUT? | Recorded rollout SHA reproduced? |
|---|---|---|---|---|
| 1 | `4dad5aaadf63ca91ba8ce79dfdcfcd694cb9fefdc3735172d064e2fc5522da2b` | SHA-256 of the producer's machine-local stdout capture of `codex exec`: the final message re-emitted through the Windows console (CRLF line ends; non-ASCII mangled via cp437, e.g. an em dash becomes `ΓÇö`). Capture hash reproduced: yes; capture equals the rollout excerpt after undoing CRLF and cp437: yes | **NOT REPRODUCED from rollout** | none recorded |
| 2 | `d506375a34c28e486c38f9b9ea7da0f0ccc6b7f6b3c557976c1773c206e97cb5` | SHA-256 of the producer's machine-local stdout capture of `codex exec`: the final message re-emitted through the Windows console (CRLF line ends; non-ASCII mangled via cp437, e.g. an em dash becomes `ΓÇö`). Capture hash reproduced: yes; capture equals the rollout excerpt after undoing CRLF and cp437: yes | **NOT REPRODUCED from rollout** | none recorded |
| 3 | `d6ee6346c53ae114e3fe830ccf986877bf9afd47426d236cb3ef1e2a0ecdf0c7` | SHA-256 of the producer's machine-local stdout capture of `codex exec`: the final message re-emitted through the Windows console (CRLF line ends; non-ASCII mangled via cp437, e.g. an em dash becomes `ΓÇö`). Capture hash reproduced: yes; capture equals the rollout excerpt after undoing CRLF and cp437: yes | **NOT REPRODUCED from rollout** | none recorded |

## Excerpts (verbatim)

Machine-local temp paths inside an excerpt are replaced with `[machine-local temp path redacted]`; each digest above is of the **unredacted** original bytes, so a holder of the rollout can verify by re-extracting the record. No other change.

### Round 1

Record: line 100 of `rollout-2026-09-21T21-44-57-01a0c700-8d0e-72f1-aee3-b87ec962cead.jsonl`; `payload.phase=final_answer`; timestamp `2026-09-22T02:49:01.029Z` (UTC).

~~~~text
REFUSE 4d38fd3126f7f79140628a6d30220ec30df6daba

- **Bars 3–4 — blocking: titles do not prove chapter completeness.** [check-compendium.py:46](/C:/code/Conjugal/docs/product/pdf/src/check-compendium.py:46) searches all extracted text, including contents and dividers. Running the checker against in-memory subsets of the committed PDF returned **exit 0, “13 of 13”** for both the **contents page alone** and **pages 1–121, with chapters 10–13 removed**. The checker prints page count but never checks it against an expectation. Better evidence already exists: PDF named destinations `sec-<slug>` identify chapter boundaries. Validate their ordered set, chapter spans against standalone page counts, and body content within those spans; destinations alone could still identify empty dividers.

- **Bar 4 — blocking: completeness verification is optional.** [build.mjs:43](/C:/code/Conjugal/docs/product/pdf/src/build.mjs:43) conditions it on `verify`. Thus `--only compendium --no-verify` skips completeness entirely, although `build.ps1` describes that flag as skipping font verification. I confirmed the skipped call using intercepted subprocesses. Missing Python or PyMuPDF otherwise fails closed; missing dependencies do **not** silently pass.

- **Bars 1–2 — implementation supports isolation, but tests do not establish the declared bars.** For a single `--only compendium`, assembly supplies one job, build forwards that job, and [render.mjs:185](/C:/code/Conjugal/docs/product/pdf/src/render.mjs:185) writes only its output. Neither verifier writes standalone PDFs. `--online` and `--no-verify` do not expand that set. However, duplicate flags are first-wins: `--only roadmap --only compendium` selects `01-roadmap.pdf`, confirmed by intercepted renderer arguments. This parsing behavior predates S20. The tests assert HTML existence and returned jobs—not successful PDF production or unchanged standalone bytes. Assert build exit status, the produced compendium, and all 13 standalone hashes before/after; use write interception additionally if proving no writes matters.

- **Bars 3–4 — derivation is genuine but insufficient.** `documents.json` comes from the same imported `DOCS` array used by assembly, so there is no independently maintained expected list. But it describes intended membership, not successfully rendered bodies. Missing/truncated bodies can therefore disagree with it while the title check passes. No expectation is derived from standalone PDFs as bar 3 requires.

- **Bar 5 — assembly replay is preserved; complete build behavior is not identical.** The candidate leaves `assembleAll()`, existing standalone assembly branches, manifest entries, and the unknown-slug error unchanged. The rerun exercised all 13 slugs successfully. Full verified builds now additionally require an executable named `python` with PyMuPDF installed; that dependency is absent from the wrapper’s “Node … + headless Chrome/Edge only” description. Provide an explicit interpreter/dependency contract and useful subprocess launch diagnostics.

- **Bar 6 — the control is incomplete.** [compendium.test.mjs:90](/C:/code/Conjugal/docs/product/pdf/src/compendium.test.mjs:90) genuinely varies target and asserts different returned output sets. It never varies manifest length, so it cannot establish the claimed invariance across lengths, and it observes no writes. Exercise multiple manifest sizes and actual intercepted/filesystem writes. The ghost-title test checks an absent title, not a missing body with a retained title. The missing-file test also passes when PyMuPDF is unavailable, because it checks only exit 1.

- **Bars 3–4 — additional pre-existing renderer weakness.** [render.mjs:172](/C:/code/Conjugal/docs/product/pdf/src/render.mjs:172) prints after pagination times out. The new title check cannot reliably catch resulting missing content. Rendering also overwrites the destination before verification, and the temporary Chrome profile is never removed.

- **Bar 7 — the committed artifact has supporting evidence, but acceptance prerequisites remain unmet.** The candidate tree matched exactly. All **7 tests passed**; the requested checker exited **0** on the committed PDF. Independently, standalone counts sum to **161**, plus **2** front-matter pages equals its **163** pages, and all 13 link-defined chapter spans match their standalone counts. Only the compendium PDF changed in the candidate. These observations support the shipped artifact, but do not repair the unsound gate or missing bar assertions. I did not render or modify committed PDFs.
~~~~

### Round 2

Record: line 102 of `rollout-2026-09-21T22-01-37-01a0c70f-cd88-7303-8eed-cb1f5521e217.jsonl`; `payload.phase=final_answer`; timestamp `2026-09-22T03:07:07.026Z` (UTC).

~~~~text
REFUSE 5bda53c3986caa824179cd10c1d58c59f83295ef

1. **Bars 3–4 — Blocking: missing chapter bodies still pass.** [check-compendium.py:92](/C:/code/Conjugal/docs/product/pdf/src/check-compendium.py:92) requires only one text-bearing page per span. I emptied all **148 body pages**, retaining front matter and chapter dividers: exit **0**, “13 of 13.” Replacing every page’s contents with only a page number also returned **0**. Divider text alone satisfies the check; page counts and destination names do not establish chapter content.

2. **Bar 3 — Span boundaries are insufficiently verified.** [check-compendium.py:75](/C:/code/Conjugal/docs/product/pdf/src/check-compendium.py:75) assumes destinations identify chapter starts:
   - Adding a front page returned **0 at 164 pages**; front matter has no independent expectation.
   - Adding a back page returned **1**, because back matter is counted against the final chapter.
   - Moving **every destination one page forward** and appending one blank page returned **0**. All spans retain their expected lengths despite incorrect boundaries.
   - Two chapters sharing a start page returned **1** through the zero-length span. The ordering comparison itself permits equal starts.

   The rule fits the current layout’s intended boundaries but does not prove them.

3. **Bars 3–4 — The standalone expectation can share the defect.** [check-compendium.py:85](/C:/code/Conjugal/docs/product/pdf/src/check-compendium.py:85) trusts standalone page counts without validating their completeness. Deleting the final page from both the final standalone and the compendium returned **0 at 162 pages**. Both outputs use the same content fragments and rendering machinery, so shared omissions are plausible. This establishes consistency with the standalones, not independent completeness.

4. **Bar 2 — Blocking acceptance-evidence gap: the claimed hashing fix is absent.** [compendium.test.mjs:162](/C:/code/Conjugal/docs/product/pdf/src/compendium.test.mjs:162) compares `git ls-files -s` output. Those are **index entries**, not hashes of working-tree PDF bytes. An assembly operation could overwrite every PDF without changing this comparison. Git failures are also unchecked. The earlier test still checks only returned jobs, and neither test exercises rendering.

5. **Bar 6 — Blocking: manifest length never varies.** [compendium.test.mjs:132](/C:/code/Conjugal/docs/product/pdf/src/compendium.test.mjs:132) claims to exercise every manifest prefix, but never creates or supplies one. It iterates standalone targets against the same 13-document manifest. The arms-differ assertion is useful; the declared invariance experiment remains unperformed.

6. **Bars 1, 3–5 — Tests overstate their coverage.**
   - The two carving tests silently return on **any** subprocess failure, reporting success without assertions. Both carving commands succeeded here; missing PyMuPDF would fail other tests, but these two would misleadingly pass.
   - The span fixture supplies a one-document manifest against the entire compendium. I reran it with the **unchanged** standalone: it still returned **1** with “truncated or padded,” because the first chapter’s calculated span extends to EOF. Shortening the standalone is unnecessary to its success.
   - Bar 1 checks an assembled HTML file and job list, not build exit status and PDF output. Bar 5 likewise checks assembly shape.
   - No test invokes `build.mjs`; deleting its completeness gate would leave this suite’s assertions unaffected.

7. **Bar 4 — Optional-gate fix works; exit classification remains inconsistent.** [build.mjs:45](/C:/code/Conjugal/docs/product/pdf/src/build.mjs:45) runs completeness outside `verify`. No successful compendium path skipping it was found in this build entry point. Mocked subprocess checks confirmed `--no-verify` propagates checker exits **1** and **2**. However, missing `python` produces `status: null`, classified as **1**; missing standalone PDFs also return **1**. Malformed JSON and unreadable PDFs escape as tracebacks with **1**. These fail closed, but violate the advertised distinction between incomplete and cannot-run.

8. **Bars 1–7 — Verification result and limits.** The candidate tree matched exactly. The requested Node suite passed **10/10**. The requested checker returned **0** on the shipped artifact: **163 pages**, with **161 standalone pages plus two front-matter pages**. Chrome rendering was not rerun. These green results do not satisfy bars 3–4 given the reproduced false positives, so bar 7’s prerequisites are not established.
~~~~

### Round 3

Record: line 111 of `rollout-2026-09-21T22-27-22-01a0c727-62f7-78e3-addc-4a874928e97d.jsonl`; `payload.phase=final_answer`; timestamp `2026-09-22T03:31:45.522Z` (UTC).

~~~~text
REFUSE 27c12bf34dc51432f1f596c4019b60dbf3508f82

- **Bars 3–4 — blocking: missing content still passes.** Blanking physical pages **58–61** removes monetization content, including the paywall and pricing table. The gate returns **0**, reporting 163 pages and 13/13 chapters; overlap remains **93.47%**. Replacing those four pages with copies of page 62 also passes, at **94.77%**. Standalones remained unchanged.

- **Bars 3–4 — known limits are incomplete.** Reversing all 64 monetization body pages also passes, at **99.18%** overlap. The disclosed assumptions are valid, but omit tolerated partial loss, insensitivity to word/page order, and inability to verify graphics or visible layout from extracted words. “Detects assembly and rendering loss” overstates the guarantee.

- **Bar 6 — the declared experiment remains untested.** Manifest length varies only in `runChecker()`. Both assembly arms still use the original full manifest. Checking the checker’s reported manifest length does not establish invariance of files written by the build.

- **Bars 1, 2, 5, 7 — validation remains narrower than the bars.** Tests exercise assembly and returned jobs, not CLI rendering. Working-tree hashing correctly proves assembly leaves PDFs unchanged, but does not prove a complete build preserves all 13 standalones. Bar 7’s prerequisite is unmet because completeness still admits missing content.

- **Bar 4 — exit-code inconsistency remains.** With only `01-roadmap.pdf` missing from the reference directory, the checker returns **1**, contradicting its documented missing-file **2/CANNOT_RUN** contract. `build.mjs` propagates that misclassification. Malformed JSON correctly returned 2; the missing-Python branch now explicitly returns 2.

- **Bar 4 — a test still silently succeeds without exercising its assertion.** The body-text helper test returns on `ImportError`/`ModuleNotFoundError`. Furthermore, no test exercises rejection by the new word-overlap rule. The carving and full-manifest span tests now make meaningful assertions.

- **Bars 1–7 — rerun evidence:** candidate tree matched exactly; `node --test docs/product/pdf/src/compendium.test.mjs` passed **11/11**; the explicit checker invocation on the committed artifact returned **0**. Those green results coexist with the reproduced false acceptances above.
~~~~
