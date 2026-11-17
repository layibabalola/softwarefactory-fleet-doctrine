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
**assumed** ceiling of one busy thread per physical core (16), labelled ASSUMED in the output. If the light-load
(0-4 busy threads) clock was never measured, or a band below the first drop was skipped, nothing above the gap is
claimed: safe threads is the gap's low edge (0 with no light-load baseline).

**Why not the `_Total % Processor Performance` counter.** It averages idle cores in and barely moves with load
(measured: 168 % idle vs 178 % at 13 busy threads). **Why no speed probe.** A short single-thread loop lands on
the fastest idle core and mostly measures boost; a 21 % ops/s loss in one thermal trial came from another
process. Both were dropped after an adversarial review.

## The headroom answer (reader only; never stored on the bus)

Per machine (the `--expect` list, default PC-MINI1..3; `--expect ""` reads every machine on the bus), over the
last `--days` (default 7) **full** days: at least 1,200 of 1,440 minutes sampled outside owner quiet windows
(scaled down for quiet minutes, never fewer than 360 active minutes), with memory and disk read in at least
90 % of those minutes (a missing reading is never spare capacity), since the busy figures come from active
minutes only. Quiet minutes are those inside a FleetQuiet window (`C:\ProgramData\FleetQuiet\windows\<Id>.json`,
`armedUtc`..`untilUtc`; a released window is renamed `.released`):
- **CPU spare** = safe threads (measured clock onset, or ASSUMED 16) minus the worst day's p95 busy threads.
- **Memory spare** = lowest daily p05 available GB minus a 16 GB reserve. **Disk spare** = lowest C: free minus the
  owner's 50 GB floor.
- **Verdict:** ROOM (>= 4 threads, >= 16 GB, >= 100 GB spare), TIGHT (some of each), FULL, or UNKNOWN (no full
  day). The tightest resource (the one closest to its ROOM threshold) is named. **Quiet hours** = hours measured
  (>= 30 minutes) on every day used, whose p95 load stayed under 10 % (FleetQuiet's "quiet") on every day: when a project could borrow the machine without contention.
- It is **compute headroom only**: it does not count Claude/Codex account quota, HeavySlot or gate slots, or
  project rules such as AirMyPC's one-gate-at-a-time. Those can say no while the machine says ROOM.

**Data you cannot trust is never shown as spare capacity.** The reader marks a machine ABSENT (no rows), STALE
(newest day, or newest FULL day, over 2 days old: a recent partial day never vouches for old full days),
LOW-COVERAGE (no full day in the window), DUPLICATED (a minute written twice, or one machine-day published
twice), MISFILED (a row in this machine's directory names another machine; it is ignored), INVALID-ROW (a row
for today or a future date, out-of-range coverage, or a missing or non-finite figure the verdict needs; it is
ignored), MIXED-CODE (judged on the build behind the full days actually used) (machines whose data is in use run different sampler builds; a stale machine does not count), BUS-NOT-REFRESHED (the fetch failed)
or, with `--live`, LIVE-STALE (newest minute over 5 min old). **Any of these makes the verdict UNKNOWN** (the
computed one is kept only as `verdict_untrusted`) and the exit code 1. Exit 2 = the bus could not be read.
A minute counts as sampled only if successful CPU reads covered at least 30 s of it (`cpu_secs`). A minute written in two parts is merged
only when the parts come from different sampler runs (`sid`; a row from before `sid` is identified by its own content, so only a byte-identical copy is a replay)
and add up to at most 75 s (one minute plus one 10 s interval: a restart); a run already merged into that
minute, or more measured time than that, is DUPLICATED. Under `--live`, freshness and duplication are judged
on usable minutes only. A merge keeps each extreme (the lower free memory
and disk, the higher peaks) and weights means by duration. A sample interval that runs more than 2 s past a
minute boundary is dropped, so no work is booked to the wrong minute or UTC day.

## On each machine

| Piece | Where | Does |
|---|---|---|
| `MachineLoadSampler.ps1` + `MachineLoadNative.cs` + `projects.json` + the windowless launcher (SHA-256 pinned) | `C:\ProgramData\MachineLoad\bin\` | one long-lived hidden pwsh; one row per UTC minute to `C:\ProgramData\MachineLoad\data\minute-<UTC date>.jsonl`; keeps 14 days; mutex `Global\MachineLoadSampler`; exits to be restarted above 400 MB |
| Task `\Fleet\MachineLoad Sampler` | at boot + every 5 min (restart net; a running copy holds the mutex) | runs as **SYSTEM**, so it can read the CPU time of services and protected processes (Defender; non-elevated it cannot see ~130 of ~310 processes), samples whether or not anyone is signed in, and inherits no user-writable environment (a logged-on user's `DOTNET_STARTUP_HOOKS` or `CORECLR_PROFILER_PATH` would load code into an elevated pwsh started as that user). Everything it starts is inside `C:\ProgramData\MachineLoad`. The installer refuses a dirty checkout (the manifest names the commit installed), disables the task and stops the sampler (pwsh 7 running exactly the installed script, by pid). A missing root is created with its final protected DACL in one call; an existing one must ALREADY be locked (owned by SYSTEM/Administrators, nobody else holding any write, delete or permission right, no link): a handle opened earlier keeps its rights through a lock, so WRITE_DAC could reopen it and DELETE could rename it away. Otherwise the install refuses and the tree is removed by hand. It then LOCKS the tree before copying any code (Administrators-owned, SYSTEM/Administrators full, Users read-only), VERIFIES it (no junction, symlink or hard link, no non-admin owner or write right, nothing in `data` but the sampler's own file names), deletes and rebuilds `bin`, copies, re-locks, and verifies `bin` holds exactly the source files with the source's hashes; anything else refuses the install. pwsh is the absolute `Program Files` path, the script pins `PSModulePath`, and it reads only the installed `projects.json` (no machine-local override), so no user-writable file is on the elevated path. Open handles a user took on a `data` file before the first lock can still write that file: data integrity only, never code. |
| Task `\Fleet\MachineLoad Publisher` | daily, 75-104 min after the UTC day closes (a fixed per-machine offset) | `machine_load.py publish`, non-elevated: appends every finished, unpublished UTC day still held on the machine (14 days) to the bus in ONE commit (fast-forward, 5 retries, never forced); receipt `%LOCALAPPDATA%\MachineLoad\publish-receipt(s).json(l)` (written even when it crashes) records exit code, bus HEAD and `launched_by`; a receipt that cannot be written is reported on stderr and exits 4. `-Status` flags a failed last task run, a failing receipt or one over 50 h old. |

The publisher launches through the fleet's per-user windowless shim (`~/.claude/ops/launch-windowless.vbs`,
from coretemp-fleet), which is fine because it is not elevated; the sampler calls a hash-pinned copy of the
same launcher from the locked bin. A bare pwsh/python action under an Interactive principal pops a console
window (TRAPS).
Entries are added to `~/.claude/machine/SCHEDULED-TASK-REGISTRY.md` on install.

**Cost (measured on PC-MINI2):** about 0.6 CPU-second per minute (~0.03 % of 32 threads), ~200 MB working set
(pwsh plus one compiled helper), ~1 MB of minute rows per day. Each row carries the sampler's own CPU and memory,
so growth shows in the data.

## What travels to the bus (public repository)

Daily aggregates only (`fleet/machine-load-day/v1`, see `machine-load/README.md`). Project names only from the
`publish` allowlist in `projects.json`; any other project is `~other-project`. HeavySlot job kinds only from
`publish_kinds`; any other kind is `?`. Never process names, command
lines, paths or user names; those stay in the local minute files and in `summarize`/`--live` output over ssh.

## Tests

`python tools/machine/machine-load/machine_load.tests.py`: stdlib only, no network, no elevation (it also runs
`Install-MachineLoad.tests.ps1` on Windows with pwsh 7). Covers:
- **Rollup:** de-duplication and UTC-day bounds; restart-split vs replay vs overlapping samplers; merges that keep
  the worse memory and disk; coverage rules (quiet minutes, short minutes); nothing private in a day row (project
  and job-kind allowlists); quiet minutes excluded; the clock signal; restart counting; percentiles; clock onset
  measured vs assumed.
- **Reader:** ABSENT, STALE (including an old full day behind a recent partial one), LOW-COVERAGE, DUPLICATED,
  MIXED-CODE (a stale or retired machine does not void the others), BUS-NOT-REFRESHED, LIVE-STALE, a FULL machine,
  and exit codes through `main()`.
- **Publish:** missing days, a day 12 days back, idempotency, a rejected push retried, failing and unwritable
  receipts; a HeavySlot pair with an impossible span is dropped (only the day's own minutes are ever walked).
- **Installer** (`Install-MachineLoad.tests.ps1`): a correct read-only tree passes; a Users write right, a junction
  (inside or as the root), a hard link, a planted `.config` or data file, a hash mismatch, a missing file, an
  untrusted pre-existing owner and a pre-lock WRITE_DAC are refused; a protected directory is born without Users
  write; the sampler matcher takes only pwsh 7 running exactly the installed script; the sampler task is SYSTEM;
  the sampler's own FleetQuiet reader (extracted from the script) honours armedUtc/untilUtc/.released with no
  local-time shift; the Core Temp parse (extracted) skips times in the DST gap and the repeated hour; no time is
  floored with two clock reads; `-Status` treats the running sampler's unsigned 0x800710E0 as benign; a root
  created by someone else between the existence check and the protected create is refused.

Not unit-tested: the sampler's live CPU-delta and PID-reuse accounting run only inside
the elevated sampler; the install proof (the task must write a fresh row with the installed code hash) is their
end-to-end check.

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
