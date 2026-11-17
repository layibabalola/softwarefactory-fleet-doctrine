# tools/machine/machine-load: how busy each machine is, and how much more it can take

Owner request, 2026-11-16: *"I want all the mini pcs to track and report their usage to a central location
(doctrine bus?), so I can determine how much headroom each machine has and whether or not it can handle more
projects. I want to know how much a machine can share resources and compute without negatively impacting
throughput of existing projects."*

A **machine tool** (like `../fleet-mini/`): a sampler on each machine, a daily roll-up published to the bus
under [`machine-load/`](../../../machine-load/README.md), and one reader that answers the owner's question.

```powershell
# the owner's view, from any machine with a bus clone (exit 0 = every machine has trustworthy data)
python tools/machine/machine-load/machine_load.py headroom --bus <bus clone> [--days 7] [--live] [--json]

# install / check / remove on one machine (install is elevated; an ssh session on a mini is elevated)
pwsh -NoProfile -File tools/machine/machine-load/Install-MachineLoad.ps1            # install + prove the task writes rows
pwsh -NoProfile -File tools/machine/machine-load/Install-MachineLoad.ps1 -Status    # read-only
pwsh -NoProfile -File tools/machine/machine-load/Install-MachineLoad.ps1 -Remove    # tasks gone, data kept
```

## What it measures, and why these numbers

| Question | Measure | Source |
|---|---|---|
| How much CPU is in use | **busy threads** = `Processor(_Total)\% Processor Time` x logical processors / 100 (0-32 on the minis) | perf counter, every 10 s |
| Would added work slow what runs now | **clock while busy** = `% Processor Utility / % Processor Time` (x100 = % of nominal clock), grouped by load band | perf counters |
| Is the power limit reached | package W, minutes at >= 70 W | the Core Temp feed already on each mini (`~/.claude/machine/coretemp-fleet/`) |
| Memory, disk, network | available GB (p05), commit %, hard faults; disk busy %, latency, C: free; Mb/s | perf counters, .NET |
| Who uses it | CPU-seconds per project, from each process's command line, image path or current directory (or its parent's project); unmatched processes go to generic buckets (`dotnet`, `claude`, `defender`, ...) | `Get-Process` deltas; WMI only once per new process |
| Do the heavy jobs get slower | each HeavySlot job (`project:kind`) that ended that day: duration, and busy threads while it ran | `C:\ProgramData\HeavySlot\ledger.jsonl` |

**Why the clock, not a fixed thread count.** Thermal trials (`coretemp-fleet/RESULTS.md`) show all three minis
holding a ~74 W package limit under all-core load: power, not cores, sets their speed. When load rises past
what the power budget allows, every core's clock drops, and existing work slows even with idle threads left. The
reader therefore finds the **load at which the busy clock falls below 90 % of its light-load value** (measured,
from the machine's own history). Until the machine has been that busy, it says so and falls back to an
**assumed** ceiling of one busy thread per physical core (16), labelled ASSUMED in the output.

**Why not the `_Total % Processor Performance` counter.** It averages idle cores in and barely moves with load
(measured: 168 % idle vs 178 % at 13 busy threads). **Why no speed probe.** A short single-thread loop lands on
the fastest idle core and mostly measures boost; a 21 % ops/s loss in one thermal trial came from another
process. Both were dropped after an adversarial review.

## The headroom answer (reader only; never stored on the bus)

Per machine, over the last `--days` (default 7) **full** days (>= 1,200 minutes sampled):
- **CPU spare** = safe threads (measured clock onset, or ASSUMED 16) minus the worst day's p95 busy threads.
- **Memory spare** = lowest daily p05 available GB minus a 16 GB reserve. **Disk spare** = lowest C: free minus the
  owner's 50 GB floor.
- **Verdict:** ROOM (>= 4 threads, >= 16 GB, >= 100 GB spare), TIGHT (some of each), FULL, or UNKNOWN (no full
  day). The tightest resource is named. **Quiet hours** = hours where p95 load stayed under 10 % (FleetQuiet's
  "quiet") every day: when a project could borrow the machine without contention.
- It is **compute headroom only**: it does not count Claude/Codex account quota, HeavySlot or gate slots, or
  project rules such as AirMyPC's one-gate-at-a-time. Those can say no while the machine says ROOM.

**Data you cannot trust is never shown as spare capacity.** The reader marks a machine ABSENT (no rows), STALE
(newest day over 2 days old), LOW-COVERAGE (no full day in the window; verdict UNKNOWN), DUPLICATED (two
samplers wrote the same minute), MIXED-CODE (machines run different sampler builds) or, with `--live`,
LIVE-STALE (newest minute over 5 min old), and exits 1. Exit 2 = the bus could not be read.

## On each machine

| Piece | Where | Does |
|---|---|---|
| `MachineLoadSampler.ps1` + `MachineLoadNative.cs` + `projects.json` | `C:\ProgramData\MachineLoad\bin\` (ACL-locked: SYSTEM and Administrators full, Users read and execute) | one long-lived hidden pwsh; one row per UTC minute to `%LOCALAPPDATA%\MachineLoad\minute-<UTC date>.jsonl`; keeps 14 days; mutex `Global\MachineLoadSampler`; exits to be restarted above 400 MB |
| Task `\Fleet\MachineLoad Sampler` | at logon + every 5 min (restart net; a running copy holds the mutex) | **elevated**, only so it can read the CPU time of services and protected processes (Defender): non-elevated it cannot see ~130 of ~310 processes |
| Task `\Fleet\MachineLoad Publisher` | daily, 75-105 min after the UTC day closes (staggered per machine) | `machine_load.py publish`, non-elevated: appends every finished, unpublished UTC day to the bus in ONE commit (fast-forward, 5 retries, never forced); receipt `%LOCALAPPDATA%\MachineLoad\publish-receipt(s).json(l)` records exit code, bus HEAD and `launched_by` |

Both tasks launch through the fleet's windowless shim (`~/.claude/ops/launch-windowless.vbs`, from
coretemp-fleet); a bare pwsh/python action under an Interactive principal pops a console window (TRAPS).
Entries are added to `~/.claude/machine/SCHEDULED-TASK-REGISTRY.md` on install.

**Cost (measured on PC-MINI2):** about 0.6 CPU-second per minute (~0.03 % of 32 threads), ~200 MB working set
(pwsh plus one compiled helper), ~1 MB of minute rows per day. Each row carries the sampler's own CPU and memory,
so growth shows in the data.

## What travels to the bus (public repository)

Daily aggregates only (`fleet/machine-load-day/v1`, see `machine-load/README.md`). Project names only from the
`publish` allowlist in `projects.json`; any other project is `~other-project`. Never process names, command
lines, paths or user names; those stay in the local minute files and in `summarize`/`--live` output over ssh.

## Tests

`python tools/machine/machine-load/machine_load.tests.py`: stdlib only, no network, no elevation. Covers
de-duplication and UTC-day bounds, nothing private in a day row, quiet minutes excluded, the clock signal,
restart counting, percentiles, clock-onset measured vs assumed, and the reader: ABSENT, STALE, LOW-COVERAGE
(UNKNOWN, never ROOM), MIXED-CODE and a FULL machine, on a throwaway git origin.

## Open (not done here)

- **Calibration under controlled load.** The clock-onset method is passive: it learns only from load the machine
  has actually carried. A controlled run (fixed reference job while adding 0/4/8/16/24 threads, inside a FleetQuiet
  window like the thermal trials) would measure the slowdown curve directly. It saturates the CPU, so it is an
  owner-launched run.
- **Gate wall time vs load** is published per HeavySlot job; a trend view across days is the next reader feature.
- **Overlap:** Bachelor's `thermal-attribution-sampler.ps1` (Cloudvore) attributes CPU only above 80 % load. One of
  the two should retire once both are seen side by side.
- **CI:** a day-row push to master starts `disposition-intake.yml`, whose `paths-ignore` lacks `machine-load/**`
  (same open follow-up as `path-health/**`).
