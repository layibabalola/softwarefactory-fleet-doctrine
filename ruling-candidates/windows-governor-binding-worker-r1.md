# CANDIDATE r1: Windows governor cell -- target the binding worker (zero runtime authority)

Status: PROPOSED 2026-09-29 by a bus-auditor chat session (record only).

This candidate supersedes the Windows resume condition parked in
`master-ci-four-cause-repair-packet-r2.md` ("an anchor test whose cost does not depend on history length").
Packet r2 itself is left untouched. The evidence is the TRAPS correction dated 2026-09-29: the anchor is
flat, and a 125-test shard is the binding worker.

## Subject 1: in flight as a K1/K6 pair

**Profile:** code.

**Change:** instrumentation only, in `tools/run_windows_universal_tests.py` and its runner unit tests.
- Every refusal, both `WORKER_DEADLINE_EXCEEDED` and `CHILD_FAILED`, is preceded by one JSON line per
  worker: worker, elapsed, budget, last started test, completed count, and planned count.
- Every run prints the 20 slowest tests of each worker.
- The refusal text and its non-zero exit are unchanged.

**Forbidden:** changes to `DEADLINE_SECONDS`, `JOB_SECONDS`, `RESERVE_SECONDS`, `WORKERS`, `EXPECTED`,
`CENSUS_SHA256`, `HEAVY`, `partition()`, `timeout-minutes`, any workflow, and
`tests/test_universal_provider_control.py`.

**K4 (completion evidence):** one governor push run on the landed SHA whose Windows logs show the
per-worker durations.

## Subject 2: cut after one CI run has produced durations

The fix targets the tests the durations name. The likely class is subprocess- and git-spawn-heavy tests
that run 5 to 18 times slower on Windows. Every check must keep executing. Any proposal that trades runner
security settings (e.g. Defender exclusions) for speed returns to a ruling-candidate first.

## Resume and close condition

The binding Windows worker, as named by the runner, completes in under 85% of `worker_budget()` on 3
consecutive master Windows jobs. None of these may change: `DEADLINE_SECONDS`, `JOB_SECONDS`,
`RESERVE_SECONDS`, `timeout-minutes`, `WORKERS`, `HEAVY`, or the shard shape `[1,1,125,125]`.
