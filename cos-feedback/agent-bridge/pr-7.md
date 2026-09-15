schema: cos-feedback.v1
project: agent-bridge
repo: layibabalola/agent-bridge
pr: 7
head: 050a1e2d64be44cf85a98daad02c187c9b7361d5
reviewed_utc: 2026-09-15T17:44:06Z
event: pr-opened
verdict: merge-when-ci-green
ci_summary: Windows CI test IN_PROGRESS (run 35003048345). No content blockers.

## Blockers

(none)

## Improvements

- `test_doctor_cli.py`: host-config existence assert is global (`"(missing)" in output or "(exists)" in output`); tighten to require a measured `(exists)`/`(missing)` on each of the `claude_desktop_config:` and `codex_config:` lines so one silent line cannot hide behind the other.

## Notes

- CARD:P-8: adds `AgentBridge.doctor()` + `agent-bridge doctor` subparser (json/text), deferred import of `default_claude_config_path` / `default_codex_config_path` to avoid setup_bridge cycle, watcher via `_health_read_json` (ok/missing/UNKNOWN), measured python version + `sys.executable`.
- Diff: `agent_bridge/bridge.py` (+67), new `test_doctor_cli.py` (+58), `.github/workflows/windows-ci.yml` (+3/−2) registers `test_doctor_cli.py` and de-dupes `test_delivery_ci.py` / `test_dispatch_budget.py` for R1.
- Local claim: `pytest test_doctor_cli.py test_phase0_contract.py test_server_wrapper_phase2.py -q` → 130 passed, 18 subtests. MERGEABLE while hosted Windows CI runs.
- CoS review via `gh`. No GitHub PR comment posted. Cloud Agents unavailable on plan.
