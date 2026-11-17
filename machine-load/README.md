# `machine-load/`: one directory per fleet machine, one row per UTC day

**Status: owner-requested 2026-11-16 (*"I want all the mini pcs to track and report their usage to a central
location (doctrine bus?)"*), schema `fleet/machine-load-day/v1` is a CANDIDATE until a RULINGS entry ratifies
it.** Diagnostic only (metrics law 1): a row is a measurement, never authority. The headroom verdict exists only
in the reader's output and is never written here.

| | |
|---|---|
| **Writer** | `tools/machine/machine-load/machine_load.py publish` via task `\Fleet\MachineLoad Publisher` on that machine. Single writer per directory: the directory name is the writer's `COMPUTERNAME`. |
| **Reader** | `python tools/machine/machine-load/machine_load.py headroom --bus <clone> [--days 7] [--live] [--json]` |
| **Files** | `machine-load/<MACHINE>/days-YYYY-MM.jsonl`, append-only; idempotency key (machine, date) |
| **Push rule** | once per machine per day, after the UTC day closes; a missed day is caught up in the same single commit (law 3) |
| **What travels** | aggregates only: percentiles, minute counts, a 24-entry hourly profile, core-hours per allowlisted project and per generic bucket, HeavySlot jobs as `project:kind` with duration. No process names, command lines, paths, branch names or user names (law 4; the bus is public). |
| **Validation** | the reader trusts a machine only with a row no older than 2 days, at least one full day (>= 1,200 minutes that each measured CPU for >= 30 s) in the window, no duplicated minutes, the same newest sampler build as the other machines, and a successful bus fetch; otherwise ABSENT / STALE / LOW-COVERAGE / DUPLICATED / MIXED-CODE / BUS-NOT-REFRESHED, exit 1, and the verdict is UNKNOWN. |
| **CI** | a row push starts `disposition-intake.yml` (its `paths-ignore` covers only `cos-feedback/**` and `heartbeats/**`). Adding `machine-load/**` needs that workflow's epoch amendment: an open follow-up shared with `path-health/**`. |

## Record shape (`fleet/machine-load-day/v1`, abridged)

```json
{
  "schema": "fleet/machine-load-day/v1", "machine": "PC-MINI2", "date": "2026-11-17",
  "code": ["8ba4d41dc3c2"], "tool_commit": "<bus commit>", "published_utc": "2026-11-18T01:31:02Z",
  "lp": 32, "coverage_min": 1438, "quiet_min": 0, "duplicate_min": 0, "unparseable_rows": 0,
  "cpu": { "busy_threads_p50": 2.6, "busy_threads_p95": 13.3, "busy_threads_max": 24.1,
           "min_ge_8": 85, "min_ge_16": 12, "min_ge_24": 1,
           "clock_by_load": { "0-4": {"n": 1210, "perf_p50": 183.1}, "12-16": {"n": 40, "perf_p50": 171.0} },
           "counter": "busy threads = Processor(_Total)\\% Processor Time x LP / 100; clock = % Processor Utility / % Processor Time" },
  "power": { "pkg_w_p50": 28.6, "pkg_w_p95": 75.6, "pkg_w_max": 99.4, "min_pkg_ge_70w": 30, "core_c_p95": 90.1, "core_c_max": 94.0, "feed_min": 1438 },
  "mem": { "avail_gb_p05": 55.2, "avail_gb_min": 51.0, "commit_pct_p95": 40.1, "hard_faults_p95": 120.0 },
  "disk": { "busy_pct_p95": 6.0, "lat_ms_p95": 1.2, "c_free_gb_min": 1680 },
  "net_mbps_p95": 9.1,
  "hourly_utc": { "cov": [60, "..."], "busy_p95": [3.1, "..."], "busy_max": [9.0, "..."] },
  "cpu_core_h": { "machine": 31.2, "attributed": 29.8, "residual_pct": 4.5,
                  "projects": {"airmypc": 9.1}, "buckets": {"dotnet": 14.0, "claude": 2.2, "defender": 1.1} },
  "heavy_jobs": { "airmypc:gate": {"n": 9, "dur_s_p50": 372, "dur_s_max": 410, "busy_threads_during_p50": 14.2} },
  "sampler": { "cpu_s": 880.0, "ws_mb_max": 230, "restarts": 0 }
}
```

`cpu_core_h.buckets` holds CPU that matched no project: shared build servers (`dotnet`, which on a mini is mostly
its resident project), assistants (`claude`, `codex`), `defender`, `system`, and so on. `residual_pct` is CPU the
sampler could not attribute (processes that started and ended between two 10 s reads).
