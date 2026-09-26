# S33 — key rounds, receipts (Conjugal, `S33-args-is-an-automatic-variable-so-the-parameter-is-dead`)

Outcome heading (Conjugal): `Outcome - PARKED at the three-round ceiling, NOT ACCEPTED (counts ZERO). The defect is fixed and shipped.`

Ordering / identity / delivery witness (`python coordination/kernel-dogfood/check-ordering.py`, AUTHOR dates, read-only, run 2026-09-26): `S33 NO-CANDIDATE-CITED decl=a6b9f02@2026-09-22T22:23:29-05:00 cand=none identity=none delivered=unwitnessed outcome=DELIVERED-NOT-ACCEPTED note=bus-delivery-no-sha`

Key: class `codex-openai`. Every round below is a `codex exec` session (`session_meta.payload.originator=codex_exec`, `model_provider=openai`); `turn_context.payload.model` and `.effort` are quoted per round. Producer: Claude (class `claude-anthropic`), a different independence class.

Source files are Codex CLI rollout logs (JSONL), machine-local under `~/.codex/sessions/2026/09/<DD>/`. Rollout SHA-256 is of the whole file. **Excerpt** = the last `response_item` record with `payload.type=message`, `payload.role=assistant`, `payload.phase=final_answer`; its bytes are the UTF-8 concatenation of `payload.content[].text`, no trailing newline. **Verdict-line** SHA-256 is of the single verdict line of that excerpt, UTF-8, no newline (the S12/S13 convention). Extracted 2026-09-26, read-only, by a Claude Code receipt-extraction agent.

| Round | Tree named by the key | Model / effort | Rollout (`~/.codex/sessions/2026/09/<DD>/`) | Bytes | Rollout SHA-256 | Final-answer record | Excerpt bytes | Excerpt SHA-256 | Verdict line (verbatim) | Verdict-line SHA-256 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `fe1b088b7a9c6a82488820ee83d11880cda0a97b` | `gpt-6-astra` / `high` | 22/`rollout-2026-09-22T22-30-50-01a0cc50-eb92-7293-9dc5-fc4e92c8105b.jsonl` | 509,236 | `3702549c414f4ca94885ce5b2511829b0d6191c5f9090bb13ab07ea1ad3c6d78` | line 51, `2026-09-23T03:33:07.485Z` | 3280 | `f5221c1fd7091874f7152485a94fb36a2af33f2e1bbb0396298dba3ed9f31ad1` | `VERDICT: REFUSE` | `bd0ac07c453e4b5b94cce2df44b9a6eff50d228eb50952dc2cab7bca77d1a8ed` |
| 2 | `043c81c7b5275c167f89c1f456bfe2b606c10951` | `gpt-6-astra` / `high` | 22/`rollout-2026-09-22T22-35-03-01a0cc54-c5b7-7703-a7d6-7929a53e0958.jsonl` | 577,344 | `f8874ce4858c902bc5cd9f45b1100fde9f47337e5720d37f7a44cf73b7966eea` | line 51, `2026-09-23T03:37:44.453Z` | 2958 | `84e9cf4328b042da5bb99aa99b89332d402f917ff15acab6e6b3354d6bfa375a` | `VERDICT: REFUSE` | `bd0ac07c453e4b5b94cce2df44b9a6eff50d228eb50952dc2cab7bca77d1a8ed` |
| 3 | `591ca1737` | `gpt-6-astra` / `high` | 22/`rollout-2026-09-22T22-40-10-01a0cc59-774c-76e2-b1de-9db8dcec7431.jsonl` | 468,457 | `04a2a116535a716eda67c33fe394801a9c7b14a3e4bddf28337fd02e4ef72856` | line 52, `2026-09-23T03:42:32.040Z` | 2568 | `774834b5e201f5b7ccef63ca3625fb187cd2db747bd4c6e43522b673c7fe155c` | `VERDICT: REFUSE` | `bd0ac07c453e4b5b94cce2df44b9a6eff50d228eb50952dc2cab7bca77d1a8ed` |

Every excerpt was extracted from, and hashed against, its rollout file in the same pass; each verdict line is byte-present in its excerpt.

## Reconciliation with the value recorded in the Conjugal Outcome

| Round | Recorded "verdict SHA-256" | What those recorded bytes actually are | Reproduced from the ROLLOUT? | Recorded rollout SHA reproduced? |
|---|---|---|---|---|
| 1 | `1b01331ceb5211d9661db8e9dc70fe9d29672a7d` | SHA-256 of the producer's machine-local **whole console transcript** of the `codex exec` run (134,291 B: banner, prompt, tool calls and outputs, then the final message). Capture hash reproduced: yes. Not a verdict excerpt; the rollout excerpt is contained in it modulo console encoding | **NOT REPRODUCED from rollout** | none recorded |
| 2 | `b24fa04eaf4824ee55c3d2161e2f2cab6234e866` | SHA-256 of the producer's machine-local **whole console transcript** of the `codex exec` run (120,691 B: banner, prompt, tool calls and outputs, then the final message). Capture hash reproduced: yes. Not a verdict excerpt; the rollout excerpt is contained in it modulo console encoding | **NOT REPRODUCED from rollout** | none recorded |
| 3 | `40140d8c99ea241fb9fd425865dca3685016a3e4` | SHA-256 of the producer's machine-local **whole console transcript** of the `codex exec` run (89,751 B: banner, prompt, tool calls and outputs, then the final message). Capture hash reproduced: yes. Not a verdict excerpt; the rollout excerpt is contained in it modulo console encoding | **NOT REPRODUCED from rollout** | none recorded |

## Excerpts (verbatim)

Machine-local temp paths inside an excerpt are replaced with `[machine-local temp path redacted]`; each digest above is of the **unredacted** original bytes, so a holder of the rollout can verify by re-extracting the record. No other change.

### Round 1

Record: line 51 of `rollout-2026-09-22T22-30-50-01a0cc50-eb92-7293-9dc5-fc4e92c8105b.jsonl`; `payload.phase=final_answer`; timestamp `2026-09-23T03:33:07.485Z` (UTC).

~~~~text
Verified tree `fe1b088b7a9c6a82488820ee83d11880cda0a97b` from the requested worktree using PowerShell 7.6.6. No commits or pushes; tracked files remained unchanged.

| Property | Measured value | Result |
|---|---|---|
| X1 | Actual and independently computed expected: `git version 2.55.0.windows.5` | **HOLDS** |
| X2 | `version` → `git version 2.55.0.windows.5`; configuration query → `true`; unequal | **HOLDS** |
| X3 | Default and independently computed expected: `git version 2.55.0.windows.5` | **HOLDS** |
| X4 | Matching declarations: `0` | **HOLDS** |
| X5 | Exit `0`; `PASS: 4 Get-SampleToolVersion assertions` | **HOLDS** |
| X6 | Original: exit `0`, `PASS: 7 samples winget update-status scenarios`. Scratch constant-body copy: identical exit and PASS output. Independently confirmed the scratch function returned the constant. | **HOLDS** |

**Q1.** Yes, the rename delivers the intended arguments at all 13 production call sites, by inspection. The count is **eight positional lists and five defaults**, not six and five:

- Positional: `go.ps1:4`; `cpp-msbuild.ps1:5,11`; `kotlin.ps1:21,22,31,44,45`.
- Default: `rust.ps1:6,16`; `cpp-cmake.ps1:9,39`; `qt-qmake.ps1:23`.

None uses named `-Args`; no remaining argument-delivery failure was found. This verifies binding, not every tool’s support for its supplied flags.

**Q2.** Yes, X2 is load-bearing against hard-coded `--version`: the measured version outputs used by X1 and X3 are identical. A deterministic implementation completely independent of the caller’s list cannot satisfy X2 for the same executable. These finite probes do not establish correctness for every possible implementation or input; inspection additionally confirms the candidate actually splats `@ArgumentList`. No bypass was constructed.

**Q3.** Switching to Git is a legitimate reproducibility correction that preserves the combined checks for explicit arguments, distinct outputs, and defaults. It changes individual mutation coverage: hard-coded `--version` now passes X1, leaving X2 responsible for detecting it. The declaration’s retained claim that this mutation fails both bars is outdated.

**Q4.** The scope stated in your request—Git executed on one host, all six bootstrap scripts inspected—is accurate for this review. **The candidate declaration claims more:** lines 128–130 say the consequence was executed for **“`go` and `git`”** and omit `go.ps1` from the read-only list. Its earlier table also presents a Go execution result. Historical Go execution is **NOT MEASURED** by this review; the fixture correction does not reconcile those claims.

VERDICT: REFUSE

1. **Inferred by inspection — inconsistent execution evidence.** The declaration retains broader Go execution claims despite the corrected Git-only scope supplied for acceptance. Reconcile the historical Go evidence or explicitly mark it unverified/superseded before accepting the declaration.

2. **Inferred by inspection, supported by measured equal Git outputs — incorrect mutation claim.** Declaration lines 86–88 still claim hard-coded `--version` makes X1 and X2 fail. Under the corrected fixture, X1 passes. Update that claim to identify X2 as the detecting property. All six requested executable properties nevertheless hold.
~~~~

### Round 2

Record: line 51 of `rollout-2026-09-22T22-35-03-01a0cc54-c5b7-7703-a7d6-7929a53e0958.jsonl`; `payload.phase=final_answer`; timestamp `2026-09-23T03:37:44.453Z` (UTC).

~~~~text
Verified HEAD tree equals `043c81c7b5275c167f89c1f456bfe2b606c10951`. Commands ran from the requested worktree using PowerShell 7.6.6. No tracked files changed; no commit or push.

| Property | Measured value | Result |
|---|---|---|
| X1 | Actual and expected both `git version 2.55.0.windows.5`; equality `True` | HOLDS |
| X2 | `version` → `git version 2.55.0.windows.5`; config query → `true`; inequality `True` | HOLDS |
| X3 | Actual and expected both `git version 2.55.0.windows.5`; equality `True` | HOLDS |
| X4 | Matching declaration count: `0` | HOLDS |
| X5 | Exit `0`; printed `PASS: 4 Get-SampleToolVersion assertions` | HOLDS |
| X6 | Original **and constant-body scratch copy** each exited `0`, printing `PASS: 7 samples winget update-status scenarios` | HOLDS |

For X6, I verified that the scratch source differed and its function returned `constant-version-probe`.

**Q1.** Yes, the rename delivers arguments for all thirteen call sites, by inspection. However, the measured parser census is **eight positional lists and five defaults**, with **zero named `-Args` arguments**:

- Explicit: `go.ps1:4`; `cpp-msbuild.ps1:5,11`; `kotlin.ps1:21,22,31,44,45`.
- Default: `rust.ps1:6,16`; `cpp-cmake.ps1:9,39`; `qt-qmake.ps1:23`.

No remaining argument-delivery failure was identified. This does not establish successful execution of every underlying tool.

**Q2.** The corrected mutation paragraph matches my scratch measurements: renaming back fails assertions 1–4; hard-coding `--version` fails only assertion 2. The fixture correction now distinguishes the reported profiled-shell execution from clean-shell resolution and limited filesystem evidence. I did not independently replay the historical Go observations. A separate factual error remains: the declaration repeatedly says **six** explicit call sites; there are **eight**.

**Q3.** Yes. The already-described hard-coded `--version` mutation satisfies X1, X3 and X4 while ignoring the caller’s list; I measured that result. X2 is the distinguishing assertion among X1–X4. X5 also detects it because its suite includes that assertion.

**Q4.** Yes, by inspection. The declaration explicitly limits executed consequences to Go and Git on one host, identifies Go’s profiled shell, and states that the other five scripts were read, not run.

VERDICT: REFUSE

1. **MEASURED — the call-site census remains incorrect.** PowerShell AST enumeration found thirteen calls: **eight** supplying positional lists and **five** using the default. The [declaration](/C:/code/Conjugal/.claude/worktrees/modest-rhodes-8f1078/coordination/kernel-dogfood/S33-args-is-an-automatic-variable-so-the-parameter-is-dead.md:46) incorrectly says six at lines 46, 51 and 140–141; [common.ps1](/C:/code/Conjugal/.claude/worktrees/modest-rhodes-8f1078/samples/bootstrap/windows/common.ps1:21) repeats that count. This is a remaining documentation accuracy blocker, not an executable-property failure.
~~~~

### Round 3

Record: line 52 of `rollout-2026-09-22T22-40-10-01a0cc59-774c-76e2-b1de-9db8dcec7431.jsonl`; `payload.phase=final_answer`; timestamp `2026-09-23T03:42:32.040Z` (UTC).

~~~~text
Verified in the requested worktree using PowerShell 7.6.6. Tracked files match candidate tree `591ca1737`. No commits, pushes, or tracked-file changes.

| Property | Measured value | Result |
|---|---|---|
| X1 | Actual and expected: `git version 2.55.0.windows.5` | **HOLDS** |
| X2 | `git version 2.55.0.windows.5` differs from `true` | **HOLDS** |
| X3 | Actual and expected: `git version 2.55.0.windows.5` | **HOLDS** |
| X4 | Matching declarations: `0` | **HOLDS** |
| X5 | Exit `0`; `PASS: 4 Get-SampleToolVersion assertions` | **HOLDS** |
| X6 | Original: exit `0`, `PASS: 7 samples winget update-status scenarios`. Scratch constant-body replacement: identical exit and PASS output. | **HOLDS** |

**Q1.** AST measurement confirms **13 calls: eight explicit lists, five defaults**, excluding the new test:

- Explicit: `cpp-msbuild.ps1:5,11`; `go.ps1:4`; `kotlin.ps1:21,22,31,44,45`.
- Default: `cpp-cmake.ps1:9,39`; `qt-qmake.ps1:23`; `rust.ps1:6,16`.

Both the declaration and `common.ps1` comment agree.

**Q2.** By inspection, the rename suffices for argument delivery at all thirteen sites. All eight supplied lists are positional; the other five receive the default. AST measurement found **zero named `-Args` arguments**. No remaining argument-binding failure was found.

**Q3.** I found one remaining evidence overclaim: the declaration presents an in-flight Go installation as the established cause of the temporarily empty directory and failed resolution. The reported observations support that explanation but do not establish its causality. See finding 1.

**Q4.** Yes. The already-described hard-coded `--version` mutation satisfies X1, X3, and X4 while ignoring supplied lists. X2 is the only independent assertion distinguishing that documented case. X5 also detects it because its suite includes X2. No additional bypass was constructed.

VERDICT: REFUSE

1. **INFERRED BY INSPECTION — unsupported causal certainty.** The [declaration, lines 151–159](C:/code/Conjugal/.claude/worktrees/modest-rhodes-8f1078/coordination/kernel-dogfood/S33-args-is-an-automatic-variable-so-the-parameter-is-dead.md:151) says the directory was empty and Go unresolvable “because an install was in flight.” Different version outputs and later executable presence do not establish installer timing or the cause of the earlier absence. The declaration supplies no installer/process evidence connecting those events. Qualify this as an inference or supply that evidence. I did **not** measure that historical cause, nor establish that the explanation is false.
~~~~
