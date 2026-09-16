schema: cos-feedback.v1
project: agent-bridge
repo: layibabalola/agent-bridge
pr: 8
head: 4fbc7e4729090f9cd8045592871f61fccfead9b4
reviewed_utc: 2026-09-16T01:10:41Z
event: pr-opened
verdict: merge-when-ci-green
ci_summary: Windows CI job `test` IN_PROGRESS on Actions run 35042965426 (head 4fbc7e47); MERGEABLE; no GitHub reviewDecision yet; author reports local 134 passed / 18 subtests on Windows pwsh 7 / Python 3.14.3 after merging master 65de380

## Blockers

- **CI: Windows CI `test`** — IN_PROGRESS on head `4fbc7e4729090f9cd8045592871f61fccfead9b4` (Actions run 35042965426). Wait for green before merge; if red, fix and re-push. Critical rename paths (`windows-ci.yml` + `tasks.json` → `test_wake_codex_wrapper.py`) are in this tip, so a stale CI list should not be the failure mode.

## Improvements

- `agent_bridge.py` rewrites the root CLI from `from agent_bridge import *` to path-based `spec_from_file_location` loading. That is adjacent to P-16 (not the PowerShell SoT card itself). Confirm an existing suite already pins `python agent_bridge.py` / package import after this facade; if not, add a one-liner smoke so a future import-shadow regression fails closed.
- `test_wake_codex_wrapper.py` skips when `powershell` is missing. Fine for this repo’s Windows CI; if Linux runners ever list the file, they will vacuous-skip the forwarding cases — keep the job Windows-only or gate the file list explicitly.

## Notes

- First CoS bus file for this PR. Tip `4fbc7e47` = merge of `github/master` (`65de380`) into `card/p-16` (`ac47fe4`). Owned delta: root `wake_codex.ps1` becomes a ~70-line forwarding wrapper (−2116 lines of duplicated wake body); packaged `agent_bridge/ps_assets/wake_codex.ps1` is SoT (header-only edit); `test_wake_codex_parity.py` deleted; `test_wake_codex_wrapper.py` added (installed prefer / checkout fallback / fail-loudly / wheel bytes); docs/queue/C0/WAKE_CODEX_TUNING + delivery `tasks.json` + `windows-ci.yml` updated for the rename.
- Wrapper resolves installed `agent-bridge` dist via `importlib.metadata`, else checkout `agent_bridge\ps_assets\wake_codex.ps1`, refuses self-target, forwards `@args` and child `$LASTEXITCODE`. Matches the stated acceptance intent (one real wake body + root compat path).
- Process: LUNA implementer lane killed at token ceiling with no self-attested report/commit; hub measured from bytes and finished the card, including the CI/tasks rename without which master CI would break. Class B cross-family review: round 1 CHANGES_REQUESTED (literal “one tracked wake_codex file” bar contradicted the required root wrapper), round 2 APPROVE with ruling that correcting the bar is faithful to intent. Falsification of arg forwarding (spaced / empty / `!` args, exit 7) failed to break the wrapper per PR body.
- Cursor Cloud Agents not used; review via `gh`. No GitHub PR comment posted.
- Doctrine bus: created on `master` at `cos-feedback/agent-bridge/pr-8.md`.