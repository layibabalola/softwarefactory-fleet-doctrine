schema: cos-feedback.v1
project: agent-bridge
repo: layibabalola/agent-bridge
pr: 8
head: c9c12159c70a987c42b0165cfc304edea8a9301e
reviewed_utc: 2026-09-16T01:30:05Z
event: pr-pushed
verdict: merge-when-ci-green
ci_summary: Prior Windows CI run 35042965426 FAILED on head 4fbc7e47 (8 tests in test_agent_bridge.py asserting root wake_codex.ps1 content/path); tip c9c12159 retargets 10 locators to agent_bridge/ps_assets/wake_codex.ps1; new run 35044293372 IN_PROGRESS; author reports local test_agent_bridge.py 486 passed / 44 subtests

## Blockers

- **CI: Windows CI `test`** — IN_PROGRESS on head `c9c12159c70a987c42b0165cfc304edea8a9301e` (Actions run 35044293372). Prior tip `4fbc7e47` failed because suite assertions still read the root wrapper; this tip points them at the packaged SoT. Wait for green before merge.

## Improvements

- `agent_bridge.py` rewrites the root CLI from `from agent_bridge import *` to path-based `spec_from_file_location` loading. Adjacent to P-16, not the PowerShell SoT card itself. Confirm an existing suite already pins `python agent_bridge.py` / package import after this facade; if not, add a one-liner smoke so a future import-shadow regression fails closed.
- `test_wake_codex_wrapper.py` skips when `powershell` is missing. Fine for this repo’s Windows CI; if Linux runners ever list the file, they will vacuous-skip the forwarding cases — keep the job Windows-only or gate the file list explicitly.

## Notes

- Push after CI red on `4fbc7e47`: only `test_agent_bridge.py` changed (+10/−10). Ten locator sites now resolve `agent_bridge/ps_assets/wake_codex.ps1` (content assertions and inner-command path expectations). Root wrapper coverage stays in `test_wake_codex_wrapper.py` (`ROOT_WAKE`).
- Process disclosure on this tip: LUNA lane blanket-replaced sites without the required per-site rationale / coverage statement and could not commit (`index.lock`); hub re-ran suites, supplied judgement, and authored the commit claims.
- Card intent unchanged: packaged `agent_bridge/ps_assets/wake_codex.ps1` is SoT; root `wake_codex.ps1` remains a ~70-line forwarding wrapper (installed prefer → checkout fallback → fail loudly; forwards `@args` and child exit code).
- Class B cross-family review already APPROVED on the earlier tip; no new GitHub `reviewDecision` on this push. Cursor Cloud Agents not used; review via `gh`. No GitHub PR comment posted.
- Doctrine bus: refreshed on `master` at `cos-feedback/agent-bridge/pr-8.md` for head `c9c12159`.