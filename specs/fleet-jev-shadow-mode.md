# Jev shadow-mode integration standard

**Status: `CANDIDATE r6` — reviewed 2026-09-19 by blind cross-family adversaries over six
packet rounds (record: `receipts/fleet-jev-shadow-mode-ratification-2026-09-19.md`, which carries
the SHA-256 of the exact revision each seat reviewed; a seat's verdict binds only that digest).
Writer (Law 2, single writer per file): Cloudvore, 2026-09-19; the Cloudvore project's session
authored this file and is its only writer until a steward is named on the bus. Zero runtime,
adoption or launch authority: a project is bound only once it records `ADOPT` on its own
`specs/<project>.md` surface (Laws 1 and 2). Filed as `specs/fleet-jev-shadow-mode.md` because
`tools/fleet-membership.mjs` treats any other `specs/` stem as a project id.**
Source of the evidence: the owner's read-only bootstrap pass of 2026-09-19. Two artefacts sit at
the projects root on the owner's machine, outside every fleet repository: the plan of record
(`JEV_PLAN.md` with children in `JEV_PLAN/`), which is unversioned and belongs to no repository;
and the runnable root, the standalone local git repository `jev-plan` (no remote), whose commit id
is the Law-6 qualifier for every `jev-plan` path in this file and is recorded in the receipt.

## 1. What Jev is (facts, measured 2026-09-19)

- TypeSafe's System One decision model, reachable only as `typesafe-ai/jev` through the Vercel AI
  Gateway from the `ai` npm package (`experimental_evaluate`, AI SDK 7; `ai@7.0.107` verified).
  No REST route. The team key is `AI_GATEWAY_API_KEY`, held in the owner's environment, never in
  a file, never printed; a host injects it per process (the sidecar resolves it itself when the
  parent's environment block predates it).
- One call is one `state` (string, object or array) plus a map of typed questions answered in
  parallel: `boolean` returns a probability; `choice` returns a choice, probabilities and a
  confidence; `score` returns a fractional level, probabilities and a confidence (confidence at
  `providerMetadata.typesafe.confidence`). Questions in one call cannot see each other, so
  independent and speculative questions over one state travel together.
- List price $0.042 per 1M input tokens, output free (reproduced from `tier-probe-burst.json`:
  $0.000248 for 5,900 tokens). Measured call sizes (per-report min / p50 / max of per-call
  `usage.inputTokens`, §7.1): the smallest calls ran 444 to 491 tokens (`report-cv-c2`), the
  largest corpus 1,504 to 2,155 (`report-ml-j1-clean`); the overall span across all reports is
  444 to 2,458, and 100 of the 1,074
  successful calls exceeded 1,700 tokens (22 + 5 + 48 + 24 + 1 across five reports, the rest 0).
  Measured latency (per-report p50 / p90, §7.1): the nine paid-tier runs at concurrency 8 had
  per-report p50 between 231 and 348 ms and p90 between 321 and 516 ms; the 12-call burst at
  concurrency 6 ran p50 446 ms; the harness self-test at concurrency 4 ran p50 572 ms. The free
  tier is rate-limited per model (15 paced calls at 8 s spacing over 397 s gave 6 successes in two
  bursts, about one sustained call per minute); the team moved to the paid tier on 2026-09-19.
  Zero data retention is a Pro/Enterprise feature (403 on Hobby), so the egress screen in §4 is
  mandatory.
- Operating restrictions (not measured here; they follow the vendor's own published limitations
  for jev-1.13 at docs.typesafe.ai/model-jaggedness/jev-1.13): counting, numeric, date and hash
  comparisons and every exact rule stay in code; state carries only what the question needs, and
  Jev answers only the semantic residue.

## 2. Shadow mode is the only permitted first step

A project integrates Jev **beside** an existing decision, never instead of it:

1. The host builds the state from what the current rule already sees, passes it through the egress
   screen (§4), and calls the sidecar.
2. The host appends one JSON line to a shadow log outside git and continues on the current rule.
   Any sidecar failure is "fallback taken"; the host never blocks on Jev, and Jev is never on a
   SessionStart hook path.
3. Nothing reads the shadow log at runtime. A replay summarises agreement and the disagreement list.
4. Promotion to "advisory shown to a human" needs two runs, agreement against the current rule
   (fidelity) and against blind adjudication (correctness), AND a row in the project's own
   authority register licensing that advisory (kernel K2: one register of what needs the owner);
   the two runs are evidence, not a licence. Advisory widens review only, never authority.
   Promotion beyond advisory is a separate, recorded owner decision; neither adopting this
   standard nor any threshold in a constants module grants it, and no promotion waives a bounding
   rule in §5.

## 3. The three artefacts of an instance

| Artefact | Shape |
|---|---|
| Constants module | `jev-constants.<project>.mjs` exporting the question sets, the thresholds, and `questionSetVersion()` (sha256 of the canonical questions). Any edit to `instructions` or `criteria` is a new version; shadow logs are comparable only within one version. Future in-tree home: `tools/jev/` in each project |
| Sidecar | `jev-sidecar.mjs`: stdin JSON in, stdout JSON out; `--ndjson` long-running mode with bounded concurrency; per-request timeout; mandatory `id` and `seq` echo; error codes `missing_key`, `invalid_request`, `zdr_unavailable`, `rate_limited`, `timeout`, `auth`, `provider_error`, `unknown`; never calls `process.exit` (Node 24 on Windows asserts on exit with an open keep-alive socket). `zdr: true` passes through; on a plan without zero data retention the gateway refuses before the model, which is the fail-closed behaviour |
| Shadow log record | `{ ts, project, site, questionSetVersion, stateSha256, answers, confidence, latencyMs, currentBehaviour, agree, fallbackTaken, errorCode, marketCostUsd, questionsPerCall, itemsPerCall }`, never the raw state |

The validation harness (`jev-validate.mjs`: `--questions --samples --out --concurrency --limit
--dry --delayMs --maxRetries --rateLimitBackoffMs --timeoutMs --zdr`) replays a samples file
against a questions module and reports per-question agreement, disagreements with confidence,
latency percentiles, tokens and gateway cost.

## 4. Egress screen (mandatory while the plan has no zero data retention)

Detection and masking are two steps, and the count is blocking. `screen-egress.py`
(`extractors/screen-egress.py:7-17` in the runnable root) COUNTS every one of these classes in the
fields that would be sent: e-mail addresses, `sk-ant-`, `sk-`, `gh[pousr]_`, `AKIA`, `xox[bpa]-`
tokens, `Bearer` values, user-home paths, machine names and user names. `mask-samples.py` MASKS
only e-mail addresses, user names and machine names. Tokens and user-home paths the screen finds
are removed by hand or by the repo's own scrubber (Cloudvore `RcLogScrub` and `SecretScrub`; SBP
`TextRedaction` plus a home-path rule it lacks today; Conjugal's Law-4 tuple in
`coordination/tools/doctrine_outbox.py:68-83`), and the screen is run again. No state leaves the
machine while any count is nonzero, except a count that a synthetic-sentinel line explains (the
screen reports those separately). Non-public corpora leave the machine only on the owner's
recorded approval (given 2026-09-19 for the staged Cloudvore, SBP and Conjugal sets).

## 5. Per-project instances (top pick, hook point, log, comparison, bounding rule)

| Project | Top pick | Hook point (future in-tree) | Shadow log | Compare against | Rule that bounds it |
|---|---|---|---|---|---|
| Cloudvore | CV-B1 backlog-row predicates (+CV-B5 risk tier); CV-C2 rclone line | new `tools/jev-shadow.py` run after `gate.py`, never on the SessionStart hook; product: `JobRunner.ObserveLogLine` after `RcLogScrub` | `logs/jev-shadow.jsonl` | `is_owner_gated`, `admits_unmet_scope`, `classify_packet`, `IsRateLimitLine` | landedness stays exact; nothing on the IsSafeToWipe path; "Doctrine checks are advisory and do not auto-ack. Adoption requires the exact reviewed revision and publication evidence" (`docs/operating-contract.md:151-154`) |
| softwarefactory-fleet-doctrine | FD-C1 seam detection; FD-C2 CoS verdict validator | `cmdExportCheck` in `tools/doctrine-sync.mjs` after `hits`; sidecar out of tree (public, stdlib-only repo) | machine-local `jev-shadow/fleet-doctrine.jsonl` | `SEAM_RULES` hits; the written `verdict:` | shadow mode only LOGS a proposed additional owed entry for a human to read; it never adds one to the queue, never removes one, and never touches a verdict. Adding an entry on a Jev answer would be a promotion under §2.4, which this candidate does not authorize; ratify-before-doctrine (`RULINGS.md:89-92`) stands |
| Conjugal | CJ-A3 vote salvage (opt-in flag); CJ-A1 capacity refusal, offline replay | `tally-votes.sh:173` behind `PAIRPROG_JEV=1`; out-of-tree replay of Law-4-screened wake logs | `scratchpad/jev-shadow.jsonl` (gitignored; chosen so the path has no directory segment named state, a token Conjugal's Law-4 screen at `coordination/tools/doctrine_outbox.py:80` refuses) | the salvage token; each capacity keyword list separately | `PRIVACY.md:7-8` "does not phone home": no in-product call until amended; `CLAUDE.md:54` guards refuse |
| magic-lantern_dannephoto | ML-J1 marker triage | `--jev-shadow` flag on `tools/roadmap/todo_inventory.py`; `raise ValueError` kept | `.claude-state/jev-shadow.jsonl` | `FILE_TRIAGE` state | rules the project already holds: the marker census is deterministic and validated by `python tools/roadmap/todo_inventory.py --check` (`CLAUDE.md:52-53`), and "Evidence-first. Never claim a build/QEMU/hardware result without real logs recorded in the repo ... Never weaken or delete harness gates to get to green" (`CLAUDE.md:65-67`). PROPOSED by this standard, not yet a project rule (the pointer line in §6 adds it): Jev output never enters the census and is never cited as evidence |
| SilentBackgroundProcess | SBP-A1 authority classification | after `Get-Owner` and the disposition switch in `tools/classify-universal-authorities.ps1`, diagnostic file only | `%LOCALAPPDATA%\SBP\1.2\tray\jev-shadow.jsonl` (the redacted diagnostic tree) | the disposition switch, new rows only | the registry loader is a fail-closed validator, not a coercion: `src/Sbp.Monitor/AuthorityMatcher.cs:133` throws "UNKNOWN disposition must require review." for any `UNKNOWN` row not already marked `REVIEW_REQUIRED`, so the shadow output itself maps `UNKNOWN` and sub-threshold answers to `REVIEW_REQUIRED` before anything could reach a registry; output carries `authority = USER_DIAGNOSTIC_ONLY, authorizesMachineDecision = false` like the tray oracle's receipts (`src/Sbp.Tray/Oracle/OracleService.cs:89`); console-capability is decided in code by an explicit task-id allowlist (`tools/classify-universal-authorities.ps1:104`: `\ExplorerBootBaseline` and `\npcapwatchdog`), and launcher-host questions that allowlist does not decide, `wscript.exe` among them, are outside shadow mode and are not a Jev question |

## 6. How a fresh session finds this after an account rollover

Auto-memory is per account and empty after a rollover; only tracked files and machine-local files
survive. Three pointers, in order of reach:

1. **This bus.** `tools/doctrine-sync.mjs check --project <p>` lists the commit that adds
   `specs/fleet-jev-shadow-mode.md` as an unfolded sibling entry until the project acks it. Cloudvore runs that check from its
   SessionStart entry (`tools/gate.py --doctrine-check`); a project whose session start does not call
   the bus sees it at its next manual `check`, which is why pointers 2 and 3 exist. The receipt
   sits under `receipts/`, which is not a `BUS_SURFACES` prefix (`tools/doctrine-sync.mjs:34`), so
   it is reached from the README bullet and from this file, not from `check`.
2. **Each repo's entry chain.** One line in the file the project reads first, naming its row in §5
   and the future `tools/jev/` home. The line is a pointer, not a state claim: adoption state is
   derived from the tree.
3. **The owner's machine.** One reference-only line in the owner's user-level `~/.claude/CLAUDE.md`,
   which loads in every session on that machine regardless of account, naming the plan, the
   runnable root and this file; it asserts no setup state.

## 7. Evidence (2026-09-19; details in the plan's validation child)

| Set | Agreement with the current rule or label | Reading |
|---|---|---|
| rclone lines, synthetic (12 of 12; source `tier-probe-burst.json`, the paid-tier run. The free-tier `report-cv-c2-synthetic.json` completed only 4 of 12 and is NOT the source of this row) | `isRateLimit` 6/12 vs the substring rule | the six disagreements are, by the author's unblinded reading (not a measured count), the rule's own errors: four non-Dropbox throttles it misses (B2 `503` 0.58, Google 0.89, S3 0.97, OneDrive 0.98) and two false positives it raises (`429 ` in a path 0.01, `rate_limit` in a flag banner 0.02) |
| rclone lines, real fixtures (47 of 47; `report-cv-c2.json`) | 47/47 | |
| bus seam detection (159 labelled of 160, one SDK tie error; `report-fd-c1.json`) | `owed` 138/159 = 87%; `seamClass` 120/159 = 75% | two comparators: for `owed` (boolean vs "any regex hit"), 4 of the 31 regex positives scored below 0.5 (0.13, 0.15, 0.19, 0.44) and 17 regex-negative commits scored 0.5 or above (21 disagreements); for `seamClass`, the class matched on all 31 regex positives and Jev said `none` on 89 of the 128 regex negatives; 30 of 159 `owed` answers sit within 0.15 of 0.5. The 17 Jev-only positives are the human-read list |
| CoS verdicts (131 of 131; `report-fd-c2.json`) | `verdict` 119/131 = 91% | 10 of 12 misses flatten a minority verdict to the majority class (93 of 131 rows) |
| Cloudvore backlog rows (111 of 111; `report-cv-b1.json`) | `self_blocked` 104/111 = 94%; `admits_unmet` 52/68 = 76% on the 68 DONE rows, 23 of them within 0.15 of 0.5 | all seven blocked-row disagreements are WAITING rows the regex calls workable; 27/27 on READY rows |
| SBP authorities (98 of 98; `report-sbp-a1.json`) | owner 89/98, disposition 70/98, review 75/98 | eight of the nine owner misses are Jev naming a vendor the regex switch drops to its default arm; the ninth is a granularity split (rule `dell`, Jev `dell_fusion`) |
| Conjugal vote packets (20 of 20; `report-cj-a3.json`) | `vote` 17/20 vs the salvage regex | two reversals of the first-mention regex at confidence 1.00 and 0.94, the failure the candidate targets, plus one `no_vote` at 0.44 |
| Magic Lantern markers (338 labelled of 339, one SDK tie error; `report-ml-j1-clean.json`) | `state` 217/338 = 64%; 40/47 = 85% on the 47 rows at confidence ≥ 0.7 (the other 291 labelled rows are below it); 34-option `classification` (33 classes plus `other`) 76/338 = 22% | a two-stage coarse-then-fine choice is required for the classification |

Agreement is against the current heuristic, not truth. Where the current label is documented
wrong, the disagreement list is the product.

### 7.1 Evidence manifest

Each row above is the `summary.perQuestion` block of one harness report (`labelled`, `agree`,
`booleanNearHalf`, `lowConfidence`; `summary.succeeded` / `failed` give the denominators; each
result row carries `usage.inputTokens` and `latencyMs`, from which the per-report figures in §1 are
computed). The files live in the runnable root's `reports/` folder on the owner's machine (a local
git repository outside every fleet repository; commit id in the receipt); they are not committed
to this bus because their `questionsFile` / `samplesFile` fields carry local paths. Full SHA-256 of
each, computed 2026-09-19:

| Report file | SHA-256 | Feeds | succeeded / failed | concurrency | input tokens per call: min / p50 / max | calls above 1,700 | latency p50 / p90 ms |
|---|---|---|---|---|---|---|---|
| `tier-probe-burst.json` | `9cad4f8f07069924b1b906b52889738d0e8495eac2bde4164ec3e075835d8dfc` | synthetic rclone row | 12 / 0 | 6 | 470 / 497 / 503 | 0 | 446 / 510 |
| `report-cv-c2-synthetic.json` | `231aae6795a65f0f14d1287537263952d842529120968270e6b99d619dccfca3` | not a source: free-tier run, 4 of 12 completed | 4 / 8 | 6 | 490 / 499 / 501 | 0 | 748 / 793 |
| `report-cv-c2.json` | `2e154c7287fc82c0730b566432d8fa63b8cf352e32f82bc0fbfb6845f350bbb2` | real rclone fixtures row | 47 / 0 | 8 | 444 / 470 / 491 | 0 | 253 / 501 |
| `report-fd-c1.json` | `863a3a4ffde29d4ad1f740f647c61dd1a2f2eeb9b1804c32b0a6c1a848cf09ba` | seam detection row | 159 / 1 | 8 | 843 / 861 / 999 | 0 | 231 / 466 |
| `report-fd-c2.json` | `1447a268b42b6326b87db0b5f2ef03726878930c0136da1e9c7eed0f5f641236` | CoS verdicts row | 131 / 0 | 8 | 958 / 1,493 / 2,186 | 22 | 246 / 345 |
| `report-fd-c5.json` | `55e2473768f61e7b2da39908a3c1cc30f1bf4452c568a1b156d69271348e3ca8` | kernel dispositions (degenerate all-ADOPTED set; not in the table) | 81 / 0 | 8 | 664 / 712 / 1,090 | 0 | 237 / 403 |
| `report-cv-b1.json` | `83048df5e6bb5d87c7c492a77b536023b8f1268cc90eea80a2be03f844d6f1cc` | Cloudvore backlog rows | 111 / 0 | 8 | 794 / 1,006 / 2,305 | 5 | 243 / 321 |
| `report-sbp-a1.json` | `618263bac3f4d683b5c753673ae8f875a8cb02a828f257180b00e74bf7fa2da6` | SBP authorities row | 98 / 0 | 8 | 1,667 / 1,699 / 1,770 | 48 | 253 / 516 |
| `report-cj-a3.json` | `b5e1fbaa599fabc7c0dd4be8484df37fe623348a791ad1f03a8c488380931648` | Conjugal vote packets row | 20 / 0 | 8 | 697 / 821 / 1,700 | 0 | 348 / 498 |
| `report-ml-j1-clean.json` | `a6996545542fde1364ad7318b1c2fd5331630cb1107ac38cfa26717fb325e6a5` | Magic Lantern markers row | 338 / 1 | 8 | 1,504 / 1,586 / 2,155 | 24 | 252 / 362 |
| `report-ml-j1-active.json` | `21127686943edb2a675f22ae7f754f92ae85e6ee17de55c4ff878e2059ecd54f` | per-file-label variant of the Magic Lantern set (not in the table) | 77 / 0 | 8 | 941 / 1,111 / 2,458 | 1 | 236 / 387 |
| `smoke-report.json` | `dc17526096a5eca537043f127b4be7a34ca84398140ca5ce40dd419fe744d890` | harness self-test, 4 synthetic tickets | 4 / 0 | 4 | 530 / 533 / 543 | 0 | 572 / 822 |

Conventions: p50 and p90 are the value at index `floor(p × n)` of the sorted per-call values of
one report (the harness's `summarize`); "calls above 1,700" counts per-call `usage.inputTokens`
strictly greater than 1,700; the `concurrency` column is NOT a field of any report: it is the
harness's `--concurrency` argument (`harness/jev-validate.mjs:161`, default 4 when omitted) as
recorded for each run in the plan of record, so a reproduction that omits the flag runs at 4; the ten "corpora" of §1 are every row above except
`report-cv-c2-synthetic` and `smoke-report` (12 + 47 + 159 + 131 + 81 + 111 + 98 + 20 + 338 + 77 =
1,074 successful calls); the "nine paid-tier runs at concurrency 8" are those ten minus
`tier-probe-burst`. The free-tier figure is the paced probe of 2026-09-19 (15 calls at 8 s spacing
over 397 s, 6 successes in two bursts about 4.5 minutes apart), recorded in the plan of record;
its report (`probe-fd-c1.json`) is superseded by `report-fd-c1.json` and is not a source for any row.

### 7.2 Per-question extracts (`summary.perQuestion`: labelled, agree, low confidence < 0.5, boolean within 0.15 of 0.5)

| Report | Question | labelled | agree | lowConfidence | booleanNearHalf |
|---|---|---|---|---|---|
| `tier-probe-burst.json` | `isRateLimit` | 12 | 6 | 0 | 1 |
| `report-cv-c2.json` | `isRateLimit` | 47 | 47 | 0 | 0 |
| `report-fd-c1.json` | `owed` | 159 | 138 | 0 | 30 |
| `report-fd-c1.json` | `seamClass` | 159 | 120 | 33 | 0 |
| `report-fd-c1.json` | `exportIfSeam` | 0 (no current label) | 0 | 0 | 29 |
| `report-fd-c2.json` | `verdict` | 131 | 119 | 11 | 0 |
| `report-fd-c2.json` | `hasBlockers` / `blockerSeverity` | 0 (no current label) | 0 | 0 / 47 | 14 / 0 |
| `report-cv-b1.json` | `admits_unmet` | 68 | 52 | 0 | 23 |
| `report-cv-b1.json` | `self_blocked` | 111 | 104 | 0 | 6 |
| `report-cv-b1.json` | `evidence_kind` | 0 (no current label) | 0 | 21 | 0 |
| `report-sbp-a1.json` | `owner` | 98 | 89 | 0 | 0 |
| `report-sbp-a1.json` | `disposition` | 98 | 70 | 20 | 0 |
| `report-sbp-a1.json` | `needsReview` | 98 | 75 | 0 | 22 |
| `report-cj-a3.json` | `vote` | 20 | 17 | 1 | 0 |
| `report-ml-j1-clean.json` | `state` | 338 | 217 | 166 | 0 |
| `report-ml-j1-clean.json` | `classification` | 338 | 76 | 97 | 0 |
| `report-fd-c5.json` | `disposition` | 81 | 45 | 23 | 0 |
| `report-ml-j1-active.json` | `triage` | 77 | 27 | 38 | 0 |
| `smoke-report.json` | `wantsRefund` / `route` / `urgency` | 4 each | 4 each | 0 | 0 |

Specific extracts behind the §7 readings:

- `report-sbp-a1.json` `owner` disagreements (rule label → Jev choice, confidence): other → intel_killer_networking 0.99; other → adobe 1.00; other → cloudvore 0.85, 0.88, 0.94; other → google 1.00, 1.00, 1.00; dell → dell_fusion 0.97. Eight default-arm (`other`) misses and one granularity split.
- `report-fd-c1.json` `owed`: regex positives scoring below 0.5 are 0.13, 0.15, 0.19, 0.44 (four of 31); regex-negative commits scoring 0.5 or above: 17; answers within 0.15 of 0.5: 30 of 159.
- `report-cv-b1.json` `self_blocked` disagreements (row id, Jev probability; every row's status is WAITING): O01 0.80, V02C 0.81, V02 0.77, O02 0.64, V02B 0.63, V03 0.57, O03 0.50.
- `report-ml-j1-clean.json` `state`: 47 rows have `confidence.state` ≥ 0.7, of which 40 agree; the other 291 rows are below 0.7.
- `report-fd-c2.json` `verdict`: 12 misses, of which 10 have Jev choosing `merge-when-ci-green`, the label of 93 of the 131 rows.
- `report-cj-a3.json` `vote` disagreements (salvage label → Jev, confidence): hybrid → no_vote 0.44; claude_plan → hybrid 1.00; hybrid → claude_plan 0.94.
