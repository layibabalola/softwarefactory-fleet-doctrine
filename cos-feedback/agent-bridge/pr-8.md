schema: cos-feedback.v1
project: agent-bridge
repo: layibabalola/agent-bridge
pr: 8
head: c19e1255fcf009de37aa57d28a83c49aa9c4701c
reviewed_utc: 2026-09-16T01:38:56Z
event: pr-pushed
verdict: merge-when-ci-green
ci_summary: Windows CI run 35044842299 IN_PROGRESS on head c19e1255 (Ruff + Mypy baseline PASS; Phase smoke in progress; Full bridge / Wheel install smoke / Remaining governed still pending); author reports local full CI bar green (ruff, mypy 12 files, phase 129, bridge 486, wheel 3, remaining 435)

## Blockers

- **CI: Windows CI `test`** — IN_PROGRESS on head `c19e1255fcf009de37aa57d28a83c49aa9c4701c` (Actions run 35044842299). Ruff and Mypy already green; wait for Phase smoke, Full bridge suite, Wheel install smoke, and Remaining governed suites before merge.

## Improvements

- `agent_bridge.py` rewrites the root CLI from `from agent_bridge import *` to path-based `spec_from_file_location` loading. Adjacent to P-16, not the PowerShell SoT card itself. Confirm an existing suite already pins `python agent_bridge.py` / package import after this facade; if not, add a one-liner smoke so a future import-shadow regression fails closed.
- `test_wake_codex_wrapper.py` skips when `powershell` is missing. Fine for this repo's Windows CI; if Linux runners ever list the file, they will vacuous-skip the forwarding cases — keep the job Windows-only or gate the file list explicitly.

## Notes

- Tip `c19e1255` fixes the third place duplication was pinned: `test_wheel_install.py` still asserted checkout↔packaged byte identity for `wake_codex.ps1` (Wheel install smoke job). That assertion is removed; new `test_root_wake_codex_is_a_wrapper_over_the_packaged_asset` requires root ≠ packaged, root under 8 KiB, packaged over 8 KiB, and root text naming `ps_assets` / `wake_codex.ps1`. `codex_thread_title_probe.ps1` keeps byte parity in the loop.
- Prior tip `c9c12159` retargeted ten `test_agent_bridge.py` locators at packaged SoT after CI red on `4fbc7e47`. Root wrapper coverage remains in `test_wake_codex_wrapper.py` (`ROOT_WAKE`).
- Card intent unchanged: packaged `agent_bridge/ps_assets/wake_codex.ps1` is SoT; root `wake_codex.ps1` stays a thin forwarding wrapper (installed prefer → checkout fallback → fail loudly; forwards `@args` and child exit code).
- Class B cross-family review APPROVED on earlier tip; no new GitHub `reviewDecision` on this push. Cursor Cloud Agents not used; review via `gh`. No GitHub PR comment posted.
- Doctrine bus: refreshed on `master` at `cos-feedback/agent-bridge/pr-8.md` for head `c19e1255`.
