# S12 — key rounds, receipts (Conjugal, `S12-doc-size-gate-blind-to-snapshot-prefix`)

Outcome heading (Conjugal): `Outcome — ACCEPTED, 2026-09-18`

Ordering / identity / delivery witness (`python coordination/kernel-dogfood/check-ordering.py`, AUTHOR dates, read-only, run 2026-09-26): `S12 OK decl=63c9a49@2026-09-18T18:32:12-05:00 cand=0a738a6@2026-09-18T18:43:52-05:00 identity=ok delivered=yes outcome=ACCEPTED`

Key: class `codex-openai`. Every round below is a `codex exec` session (`session_meta.payload.originator=codex_exec`, `model_provider=openai`); `turn_context.payload.model` and `.effort` are quoted per round. Producer: Claude (class `claude-anthropic`), a different independence class.

Source files are Codex CLI rollout logs (JSONL), machine-local under `~/.codex/sessions/2026/09/<DD>/`. Rollout SHA-256 is of the whole file. **Excerpt** = the last `response_item` record with `payload.type=message`, `payload.role=assistant`, `payload.phase=final_answer`; its bytes are the UTF-8 concatenation of `payload.content[].text`, no trailing newline. **Verdict-line** SHA-256 is of the single verdict line of that excerpt, UTF-8, no newline (the S12/S13 convention). Extracted 2026-09-26, read-only, by a Claude Code receipt-extraction agent.

| Round | Tree named by the key | Model / effort | Rollout (`~/.codex/sessions/2026/09/<DD>/`) | Bytes | Rollout SHA-256 | Final-answer record | Excerpt bytes | Excerpt SHA-256 | Verdict line (verbatim) | Verdict-line SHA-256 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `24513851ea2479807ed5bac62040951ce1dce796` | `gpt-6-astra` / `high` | 18/`rollout-2026-09-18T18-37-46-01a0b6e2-1b74-7322-8cbf-33ded2a6473d.jsonl` | 635,685 | `e9946dfdefc6952aacc1e424bd82530521fe6d4ed903cce8a0f957d2c5bca0fa` | line 72, `2026-09-18T23:40:52.357Z` | 1748 | `1590a6b71a977a50f82b1f9d18d4701994faff38f93d2a35ac3484ce7d48fd53` | `VERDICT: REFUSED identity=24513851ea2479807ed5bac62040951ce1dce796 key=gpt-6-astra class=codex-openai reason=operative-path-exclusion-bypass` | `1715abcb07e25f04cffb09177afbb116c31e8d19eeb51b3d6cd46e387e706ff5` |
| 2 | `d8dc575001d4a84f310a96c8e2a03061506b2ace` | `gpt-6-astra` / `high` | 18/`rollout-2026-09-18T18-44-19-01a0b6e8-181e-7071-a1ba-a1a37801b9e0.jsonl` | 675,371 | `cf74d5c9b7033e39537fe8fa0dcbe370ddc134526f585a30a97edfd156813c16` | line 66, `2026-09-18T23:47:43.072Z` | 1506 | `d27776f4a92794d842fcfd885415e1e57be13512e1fad71a096d58484db28ad0` | `VERDICT: ACCEPTED identity=d8dc575001d4a84f310a96c8e2a03061506b2ace key=gpt-6-astra class=codex-openai` | `223a9cf4319a37b1d73f04cc911d035c845137f30086f3cf95d193e0c6f356cf` |

Every excerpt was extracted from, and hashed against, its rollout file in the same pass; each verdict line is byte-present in its excerpt.

## Reconciliation with the value recorded in the Conjugal Outcome

| Round | Recorded "verdict SHA-256" | What those recorded bytes actually are | Reproduced from the ROLLOUT? | Recorded rollout SHA reproduced? |
|---|---|---|---|---|
| 1 | `1715abcb07e25f04cffb09177afbb116c31e8d19eeb51b3d6cd46e387e706ff5` | SHA-256 of the verdict line inside the rollout final answer | **REPRODUCED** | yes |
| 2 | `223a9cf4319a37b1d73f04cc911d035c845137f30086f3cf95d193e0c6f356cf` | SHA-256 of the verdict line inside the rollout final answer | **REPRODUCED** | yes |

## Excerpts (verbatim)

Machine-local temp paths inside an excerpt are replaced with `[machine-local temp path redacted]`; each digest above is of the **unredacted** original bytes, so a holder of the rollout can verify by re-extracting the record. No other change.

### Round 1

Record: line 72 of `rollout-2026-09-18T18-37-46-01a0b6e2-1b74-7322-8cbf-33ded2a6473d.jsonl`; `payload.phase=final_answer`; timestamp `2026-09-18T23:40:52.357Z` (UTC).

~~~~text
Refused: the exclusion can bypass enforcement for an operative file.

From outside the fixture directory, this command incorrectly exits **0**, reporting “excluded” for a **40,001-byte operative file**:

```text
python coordination/tools/check-doc-size.py --repo <fixture> --path codeConjugal-worktreesprobe-r3/../operative/large.md
```

The parent checker returns **1 with BREACH** for the identical arguments. Prefix matching occurs without resolving this path against `--repo`.

Independent evidence:

- Candidate and HEAD tree checks: exit **0**, both match the declared identity. Artifact status and final diff are empty.
- Author dates: declaration **18:32:12**, implementation **18:36:59**, September 18. Snapshot, hook, settings, and `BASELINE` unchanged.
- Repo checker: **0**, reports **531 excluded**, matching `git ls-files`; operative WARN/HELD/DEFERRED rows retained. JSON preserves legacy keys and operative rows.
- Independent fixture: five verified tracked files; ordinary, `r30/`, and nested-prefix breaches each return **1**. In-budget and snapshot paths return **0**; snapshot JSON parses.
- Mutation executed against a temporary copy: exactly the three claimed tests turn red; both controls remain green.
- AST checks and doc-size suite: **0**. Observer suite: **1**, solely the expected `test_harvest_runner.py:76` failure; prefix characterization passes.
- Bar 5 also fails its exact search requirement: the quoted literal appears at both `check-doc-size.py:195` and `test-check-doc-size.py:143`.

Repository unchanged; temporary artifacts stayed within the authorized directory.

VERDICT: REFUSED identity=24513851ea2479807ed5bac62040951ce1dce796 key=gpt-6-astra class=codex-openai reason=operative-path-exclusion-bypass
~~~~

### Round 2

Record: line 66 of `rollout-2026-09-18T18-44-19-01a0b6e8-181e-7071-a1ba-a1a37801b9e0.jsonl`; `payload.phase=final_answer`; timestamp `2026-09-18T23:47:43.072Z` (UTC).

~~~~text
- Identity: both `git rev-parse` commands returned the declared tree, exit 0. Final artifact status and diff are clean.
- Ordering/scope: declaration author date precedes both code commits. No snapshot, hook, settings, or `BASELINE` changes.
- `python coordination/tools/check-doc-size.py`: exit 0; exactly **531 excluded**, independently verified with `git ls-files`. Preserved 37 WARN, 5 HELD, and 10 DEFERRED rows. All operative JSON rows match the pre-change checker.
- Independent tracked fixture: operative breach, `r30` lookalike, and nested-prefix files all produced BREACH/exit 1. Outside-cwd traversal variants—including `./`, backslashes, absolute traversal, and paths outside the repository—also produced BREACH/exit 1.
- `--path`: over-cap exit 1; in-budget, snapshot, held baseline, and `CLAUDE.md` exit 0. Snapshot JSON parses correctly; existing operative JSON fields remain unchanged.
- Executed the exact one-line mutation on a temporary copy: **three specified tests red, three controls green**. Mutation verification exited 0 after shortening temporary fixture names.
- Exact-literal search found one definition, in `check-doc-size.py`. Observer characterization passed directly. Observer suite exited 1 solely at the declared `REPO_WIDE_OBSERVER_RED` in `test_harvest_runner.py:76`.
- All three AST checks and `test-check-doc-size.py` exited 0. Repository files were unchanged.

VERDICT: ACCEPTED identity=d8dc575001d4a84f310a96c8e2a03061506b2ace key=gpt-6-astra class=codex-openai
~~~~
