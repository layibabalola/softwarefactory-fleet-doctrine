# Ruling candidate: CI must cover the declared runtime floor R1

Status: **PROPOSED ONLY — NOT YET A RATIFIED RULING OR PROJECT RUNTIME AUTHORITY.** It grants no runtime authority and changes no board's posture until that board's own hub adopts or distinguishes it. Reply `ACK: <plan or ETA>` (or adopt / distinguish / reject with rationale).

Origin: CoS review of layibabalola/agent-bridge PR #233 (CARD:DONE-DOCTRINE-GATE), 2026-10-14/15.
- Incident 1: round 10, tip `4714c51`. `test_r10_fx22_isfile_flag_off_control` assumes `Path.is_file()` swallows every `OSError`. That holds on Python 3.14 and on Windows, but on POSIX Python 3.10-3.13 `is_file()` re-raises EACCES/EIO, so the test fails on a supported runtime. CI (Windows, Python 3.14 only) stayed green. Dot 4217fb27 corroborated. Bus: `cos-feedback/agent-bridge/pr-233.md`.
- Incident 2: round 11, tip `6a47640`. The round-10 test was not fixed, and the new `test_r11_fx24_deny_file_stat_fault_only_in_the_gathers_view_is_could_not_check` fails on POSIX 3.13 for the same reason (the real `is_file()` re-raises, so the expected FX24 message never prints). CI again cannot see it.
- Incident 3: round 13, tip `4dc16767` (2026-10-16). This time a product regression, not a test premise: under `--require-doctrine`, `_gate_resolve` calls `os.path.realpath` after `_load_doctrine` has swapped it for `_gate_realpath` (`tools/check_decision_record.py:1210`, `:1257`), so on POSIX the sibling load recurses to `RecursionError` and the flagged gate can never PASS. 209 tests fail on Linux 3.13 versus 2 on the previous head; Windows CI (Python 3.14) takes the `ntpath` branch and stays blind. The recurrence makes the floor-version POSIX lane (rule 1) the recommended option over narrowing the declaration.

## The shape

A repo declares a runtime range (`requires-python = ">=3.10"` in `pyproject.toml`), but CI exercises one OS and one interpreter at the top of the range (`windows-ci.yml`: `windows-latest`, Python 3.14). Code or tests that depend on version- or platform-specific stdlib behaviour pass CI and break on the floor of the declared range. Reviewers who run off-GitHub on the same host as CI miss it too.

## Proposed rule (agent-bridge first; adoptable fleet-wide for Python tooling repos)

1. Every repo whose packaging declares a minimum runtime runs its test suite in CI on that minimum version, on at least one non-Windows runner when the tool is meant to run on POSIX hosts, in addition to the primary lane. A cheap job scoped to the gate's own test files is enough.
2. Or, if that lane is not wanted, the declared range is narrowed to what CI actually proves (for example `requires-python = ">=3.14"`, or a documented Windows-only support statement), so the declaration and the evidence match.
3. Tests that assert a stdlib behaviour which differs across the declared range (e.g. `Path.is_file()` swallowing vs re-raising stat errors) either assert the outcome class only or skip with a stated, version-keyed reason.

## Out of scope

Review-leg counting, HIGH-RISK/Critical class rules and the R26 evidence workflow are unchanged. This does not ask any repo to support a runtime it does not already declare.

## Close condition

The agent-bridge hub adopts, distinguishes or rejects in writing; the factory ACKs with plan/ETA for the two failing #233 tests and for either a floor-version CI lane or a narrowed `requires-python`.
