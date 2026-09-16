schema: cos-feedback.v1
project: agent-bridge
repo: layibabalola/agent-bridge
pr: 9
head: 88e6fa67dc17a6c0a507e409ded226fa1a95c7fd
reviewed_utc: 2026-09-16T02:12:44Z
event: pr-opened
verdict: merge-when-ci-green
ci_summary: Windows CI `test` IN_PROGRESS on head 88e6fa67 (Actions run 35047040849); local author bar 494 passed / 45 subtests on Windows pwsh7 Python 3.14.3; SOL cross-family APPROVE on tip with no BLOCKERs

## Blockers

- **CI: Windows CI `test`** — IN_PROGRESS on head `88e6fa67dc17a6c0a507e409ded226fa1a95c7fd` (Actions run 35047040849). Wait for green before merge; if red, inspect `test_wake_codex_wrapper.py` failures first (new hop test + tightened python.cmd guard).

## Improvements

- `test_wake_codex_wrapper.py` (`test_real_root_wrapper_resolves_and_reaches_the_packaged_asset`): inline comment still says `AGENT_BRIDGE_ROOT survived the hop into the packaged asset` while the docstring correctly says the hop is in-process and that claim cannot fail. Align the comment with the docstring (editorial; SOL already flagged, carried to follow-up).
- `_write_python_resolver` guard checks `%~1==-c` and non-empty `%~2`. That covers the `python.cmd` shim this helper creates; the real `py -3 -c` launcher path (where `-3` precedes `-c`) is neither broken nor validated here. Consider a follow-up that either stubs `py.cmd` with the same argv shape or documents the gap as out of scope for P-16-A2.
- No single test executes the real packaged asset *from an installed distribution*; coverage there remains compositional (resolution-order stubs + this checkout-fallback hop). SOL ruled enhancement, not blocker — still worth a dedicated card if installed-prefer regressions have bitten before.

## Notes

- Single-file delta: `test_wake_codex_wrapper.py` (+74 / −2). No production behaviour touched.
- Intent: P-16 retargeted ten `wake_codex` locators in `test_agent_bridge.py` at the packaged asset; two of those previously *executed* the root wrapper and CI run 35042965426 had proven both green against it. Retarget removed the only end-to-end root→packaged hop; suite stayed green either way. Adversarial panel correctly rejected reverting those two `script =` lines (they assert implementation behaviour). This card adds coverage instead.
- Additive changes: (1) `test_real_root_wrapper_resolves_and_reaches_the_packaged_asset` drives `ROOT_WAKE` with PATH stripped to the empty bin dir, asserts exact `PACKAGED_WAKE` path + `-RunInnerWake` + `AGENT_BRIDGE_ROOT`-derived paths in stdout. (2) `_write_python_resolver` now exits 9 unless argv carries `-c <program>`, closing the vacuous echo control.
- Author mutation table (guard invert / wrong `-c` token / wrong path / wrong root / drop `-PrintInnerCommand`) reported to redden; CoS did not re-run mutations locally.
- Class B cross-family: implementer/hub Claude; independent key SOL (Codex gpt-5.6-sol). Round 1 on `c8441f5` CHANGES_REQUESTED (host PATH not hermetic; overstated “environment survives hop”; guard still green for `python -c` with no program) — all three fixed on tip. Round 2 on `88e6fa6` APPROVE, no BLOCKERs. SOL sandbox lacks writable TEMP so SOL verdict does not cover test evidence; GitHub Windows CI is the independent test key.
- Related: P-16 SoT work on #8 (`c19e1255` tip) — packaged asset SoT, root wrapper thin forwarder. This PR restores hop coverage that P-16’s retarget dropped.
- Cursor Cloud Agents not used (review-only CoS via `gh`). No GitHub PR comment posted.
- Doctrine bus: written on `master` at `cos-feedback/agent-bridge/pr-9.md`.