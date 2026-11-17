# tools/machine/host-headroom: how much room does each fleet machine have?

A **machine tool**. Each mini samples its own load, measures how much slower a fixed small job runs
when the machine is busy, and publishes one summary record to the bus at `heartbeats/host-headroom/<MACHINE>.json`.
One reader turns those records into a fleet table. It answers the owner's question (2026-11-16):
*can this machine take another project without slowing the projects already on it?*

The verdict is **diagnostic** (`metrics/README.md` law 1). It informs a placement decision; it does
not make one, and nothing may gate on it without a ruling.

## Run it

```powershell
# Every path here is fully qualified, so each command works from any folder (C:\Windows\System32 included).
# The installed copy exists on every machine the tool is installed on; the bus checkout path is the canonical one.

# fleet view from the published records (reads origin/master; never pulls a checkout)
pwsh -NoProfile -File "$env:USERPROFILE\.claude\machine\host-headroom\Get-FleetHostHeadroom.ps1" [-Fit] [-Json]

# compute now on every mini over the ssh mesh, e.g. the last 24 h
pwsh -NoProfile -File "$env:USERPROFILE\.claude\machine\host-headroom\Get-FleetHostHeadroom.ps1" -Live -Hours 24 -Fit

# install or upgrade on one machine, from a reviewed commit (elevated; an ssh key login is elevated)
pwsh -NoProfile -File "C:\!Layi Wkspc\softwarefactory-fleet-doctrine\tools\machine\host-headroom\Install-HostHeadroom.ps1" -Commit <sha>
pwsh -NoProfile -File "C:\!Layi Wkspc\softwarefactory-fleet-doctrine\tools\machine\host-headroom\Install-HostHeadroom.ps1" -Status    # read-only
pwsh -NoProfile -File "C:\!Layi Wkspc\softwarefactory-fleet-doctrine\tools\machine\host-headroom\Install-HostHeadroom.ps1" -Uninstall # tasks only; keeps data

# the dashboard: open it on ANY machine the tool is installed on (Desktop link "Fleet Headroom")
start "$env:LOCALAPPDATA\HostHeadroom\dashboard\index.html"
pwsh -NoProfile -File "$env:USERPROFILE\.claude\machine\host-headroom\Build-FleetDashboard.ps1" -Open                    # rebuild now
pwsh -NoProfile -File "$env:USERPROFILE\.claude\machine\host-headroom\Build-FleetDashboard.ps1" -RefreshFootprint -Open  # re-measure Bachelor's suspended projects

# tests (no Pester, no elevation, temp folder only)
pwsh -NoProfile -File "C:\!Layi Wkspc\softwarefactory-fleet-doctrine\tools\machine\host-headroom\HostHeadroom.tests.ps1"
```

`-Fit` takes each project's largest p95 footprint on any machine (cores, RAM) and marks every machine
`fits` when its p90 free physical cores and free RAM both cover it and its verdict is not FULL.

## What runs on each machine

| | |
|---|---|
| **Installed copy** | `%USERPROFILE%\.claude\machine\host-headroom\` plus `installed-from.json` (the commit). Law 1: tasks run this copy, never a bus checkout. |
| **Sampler** | Task `\Fleet\HostHeadroom Sampler`, every 5 min, Priority 4 (Normal), IgnoreNew, hidden-launcher chain. One pwsh run streams one PDH query for 255 s at 15 s intervals (17 samples; it ends well inside the 300 s slot) (rate counters average the whole interval). |
| **Publisher** | Task `\Fleet\HostHeadroom Publisher`, every 6 h. Summarises 7 days and pushes only from its own clone `%LOCALAPPDATA%\HostHeadroom\bus` (sentinel `.host-headroom-publisher-clone`; it resets that clone to origin/master and refuses any other checkout). |
| **Data** | `%LOCALAPPDATA%\HostHeadroom\samples-YYYYMMDD.jsonl` (14 days, ~3 MB/day), `runs.jsonl` (one receipt per run, success or failure). Raw samples never leave the machine. |
| **Cost** | Measured on PC-MINI1: about 6 CPU-seconds per 5-minute run (process snapshot 0.33 s x 5, canary 2.5 s, counters), about 2% of one core, 0.06% of the machine. Every sample also records the sampler's own CPU and how late it landed. |

The chain is the one Core Temp telemetry uses (wscript -> `%USERPROFILE%\.claude\ops\launch-windowless.vbs`
-> `%LOCALAPPDATA%\PairProg\bin\pairprog-hidden-task-launcher.exe` -> pwsh), so no console window ever
appears. The installer refuses to run if that chain is missing. RunLevel is Highest because a normal
token cannot read other processes' command lines, and attribution then collapses into "unattributed".

## What it measures, and why each signal is there

The design was put to three adversarial reviews before any code was written (2026-11-16). These are the
findings that shaped it, each measured on the minis:

- **Average load says nothing; bursts do.** The minis idle at a 5-10% median, but Core Temp's feed shows a
  95th percentile of 100% CPU and 6-11% of the time at or above 80%. So the verdict uses burst and
  saturation **fractions of time**, not mean utilisation.
- **Power, not temperature or the 100% mark, is the limit.** Under load the package sits at its power cap
  (about 74-85 W) and the clock drops, so every running job slows a little and no throttle flag fires
  (Core Temp's throttle columns read No in 0 of ~243k rows). Signals: `% of Maximum Frequency` while busy,
  time at the power ceiling, time at or above 90 C, and the canary.
- **The canary measures slowdown directly.** Once per run the sampler times a fixed job: SHA-256 over 1 MB
  on one thread (~0.25 s), the same on **half the physical cores** (8 threads, ~0.27 s; the owner's
  2026-10-07 rule caps synthetic load at half the cores and forbids saturation runs), and a 32 MB
  write-through file. Its p10 over the window is the quiet baseline; `slowdown_p95 = p95 / p10` is how much
  slower a new normal-priority job runs at busy times, and what existing jobs feel. Duty cycle ~0.2%.
- **`% Processor Utility` exceeds 100** (frequency-scaled; 159-165 seen on PC-MINI2). Busy-ness uses
  `% Processor Time`; utility is recorded only as a work measure.
- **SMT.** 32 logical processors on 16 cores: Windows fills idle cores first, so physical cores in use is
  estimated as `min(cores, busy% x logical / 100)`. Headroom is reported in **physical cores**.
- **HeavySlot is its own resource.** Each mini's `C:\ProgramData\HeavySlot` gate admits heavy builds and
  tests. It is reported separately (`heavy_slot_verdict`), because a project that needs the gate adds queue
  time whatever the CPU headroom says. The verdict reads the **wait** a new job would see: p90 of 10 min or
  more is FULL, 2 min or more TIGHT, fewer than 5 gates in the window is FEW-GATES. `occupancy_frac` is the
  time at least one ticket held the gate. A holder that dies without an exit row is reaped late (PC-MINI3,
  7 days to 2026-11-17: 36 dead holders, reaped 26 to 873 min after admit), so a dead hold ends at the next
  admit when the gate admits one holder at a time (`max_holders`, the peak of exit-closed holds, is 1 on the
  minis), and never later than HeavySlot's 90-min default max hold. Before this fix, dead holds ran to the
  reap time and pushed occupancy toward 100%. (Finding and fix from the PC-MINI3 dashboard session's review,
  2026-11-17; an intermediate commit, 88f24c9e, misread those late reaps as 16 concurrent holders.) "Loaded" uses
  HeavySlot's own admission thresholds (CPU 85%, disk idle 20%, free commit 8 GiB), so this report and the
  gate never disagree about what loaded means. Long waits are the project queueing behind the gate, not
  proof the hardware is full.
- **Attribution.** Claude and Codex CLIs carry no project path in their command lines, and Win32_Process
  has no working directory. A path inside a **linked worktree** resolves through the index every workspace
  repo keeps in `.git\worktrees\*\gitdir`, wherever the worktree lives (`C:\abwt`, `C:\temp` and `C:\mlvtmp`
  on the three minis, measured 2026-11-17), never from a folder name. Main repos are found one level below the workspace and below each top-level folder of every fixed drive (PC-MINI2 keeps AirMyPC at `C:\temp\AirMyPC`). A process's project comes from its
  own path, else its **working folder** (read
  from the process's PEB; ported from candidate A's `MachineLoadNative.cs`, PR #99, as a merit survivor),
  else its nearest ancestor's, else the most common project among its descendants (a CLI is attributed by the git, pwsh and pytest children it
  spawns). What is left is reported as `_unattributed` with its share, plus per-family CPU (`defender`,
  `llm-cli`, `build`, `test`, `shell`, `wmi`): Defender alone measured 7-33% of busy CPU while scanning
  build output. The sampler's own tree is `_sampler`, never a project.
- **Owner quiet windows** (`C:\ProgramData\FleetQuiet\windows`, thermal trials) are excluded from every
  figure, plus 10 minutes of cool-down. Their load is synthetic.
- **Core Temp's feed** is read time-weighted (it writes fewer rows when hot), with its `dd.MM.yyyy` local
  dates and unpadded seconds parsed explicitly.
- **Scope.** Host CPU, memory, disk, power and the HeavySlot gate. Provider quota (Claude/Codex usage) is
  not covered; `capacity-control/` owns that, which is also why this is not called "fleet-usage".

## Dashboard (every machine, every 10 minutes)

Task `\Fleet\HostHeadroom Dashboard` (hidden-launcher chain, like the others) runs `Run-HostHeadroom.ps1 -Mode
Dashboard`. On each machine it:

1. writes that machine's own card, `%LOCALAPPDATA%\HostHeadroom\dashboard\card.json` (`Collect-HostCard.ps1`):
   the sampler's 7-day summary, a 24 h CPU series, HeavySlot figures, installed toolchains, GPU, free disk and
   whether it is a VM guest or a VM host;
2. reads every peer's `card.json` over ssh (a file read; hosts and VM relations in `fleet-hosts.json`), so
   no machine recomputes another's summary and the sampling cost does not grow with the number of viewers;
3. renders `dashboard\index.html`, one self-contained page (no server, nothing listens on a port), which the
   Desktop link "Fleet Headroom" opens. The page reloads every 5 minutes. A card over 30 min old is marked
   stale; a machine without the tool shows as "not installed".

The page shows one card per machine (cores free, RAM free, HeavySlot busy, CPU sparkline, canary, temperature,
power, toolchains), the projects suspended on the footprint source (Bachelor) with their estimated demand,
a placement plan, and a project-by-machine fit grid with the reasons for each verdict. The suspended-project
footprint is measured on Bachelor only with `-RefreshFootprint`, never by the task, because Bachelor is held
for benchmarking; machines without a copy take the newest one a peer holds.

Page design, footprint method and placement rules come from the PC-MINI3 dashboard session (2026-11-16),
ported here with credit. Its HeavySlot math is replaced by the sampler's, which now applies the same rule.

## Virtual machines and their host (Ultra-Magnus and Virtual-TEN)

Virtual-TEN is a VMware guest on Ultra-Magnus (measured 2026-11-17: `VMware Virtual Platform`, 16 vCPUs,
64 GB; Ultra-Magnus is an i9-13900KS, 8 performance + 16 efficiency cores, 32 threads, 128 GB, with the
Hyper-V hypervisor not running). That decides how each is measured:

- **Temperature lives only on the host.** A guest cannot read the CPU's sensors, so Core Temp runs on
  Ultra-Magnus (it is installed there but its logging was off: `EnLog=0`) and the guest's card points at it.
  Enable logging with the Core Temp telemetry bundle the minis use; the sampler then reads its feed.
- **The host's CPU counters are the truth for both.** Under VMware Workstation the guest runs as
  `vmware-vmx.exe` processes on the host, so Ultra-Magnus's `% Processor Time` already includes everything
  Virtual-TEN does, and its card lists the running guest. (Under Hyper-V this would be false: the host is
  itself a partition and only `Hyper-V Hypervisor Logical Processor\% Total Run Time` sees the guests.)
- **A guest's own CPU % is of its vCPUs, not of the machine.** It cannot see the host's contention (Windows
  guests report no steal time), so the guest's **canary** is the direct measure of how much the host slows it.
- **A placement on the guest is charged to the host.** The dashboard limits a guest's room to the smaller of
  its free vCPUs and its host's free cores, and charges whatever it places on the guest to the host too.
- **Hybrid cores.** The physical-core estimate assumes symmetric cores; on Ultra-Magnus 16 of the 24 are
  efficiency cores, so "cores free" overstates performance-core room. The canary still measures real slowdown.

## Verdict (first-cut thresholds; every reason that fired is listed in the record)

| Verdict | When |
|---|---|
| **UNEVALUABLE** | under 6 h of sampled span, coverage under 60% of that span (17 samples per 5-minute slot expected), or fewer than 20 canary runs. Never read as room. A fresh install gives its first verdict after about 6 h, not after most of the 7-day window (merit survivor from candidate B). |
| **FULL** | saturated (CPU >= 95%, run queue >= 1 per logical processor, or a sample landed >= 10 s late) >= 10% of the time; busy >= 80% >= 20% of the time; HeavySlot-loaded >= 25%; canary wide slowdown >= 2.0 or single >= 1.6; free RAM under 4 GB |
| **TIGHT** | the same signals at lower levels (saturated 3%, burst 8%, loaded 10%, wide slowdown 1.3, single 1.2, free RAM 12 GB), memory or disk pressure, >= 5% of time at 90 C, >= 10% at the power ceiling |
| **ROOM** | none of the above |

Free RAM is the 5th-percentile available memory minus a 15% reserve. `agents_max_rule` repeats
`specs/machine-inventory-schema.md` (agents_max <= cores / 2) for comparison. Tune thresholds by changing
them here and in `Get-HostHeadroomSummary` together, after a week of real data.

## Publication (bus laws 3 and 4)

- **Single writer:** the file name is the publishing machine's `COMPUTERNAME`.
- **Push rule:** only when the verdict, the HeavySlot verdict, the kinds of reason, or the project set
  changed **and** the new shape has held for at least 4 h (hysteresis, so a value hovering at a
  threshold does not flap), or when the record is over 24 h old. Expect about one push per machine per day.
- **What travels:** numbers, verdicts, reason tokens, project slugs and process-family names. No paths, no
  user names, no command lines. The tests check this.
- **No CI cost:** records live under `heartbeats/`, which `disposition-intake.yml` already lists in
  `paths-ignore`, so a record push starts no CI matrix and needs no workflow amendment.

## Merit adjudication (2026-11-17)

One owner prompt produced three tools (A: PR #99 `machine-load`; B: branch `machine/host-headroom-20261116`;
C: this tool, PR #100). Under `RULINGS.md` "RULE ON MEASURED MERIT, ALWAYS", a neutral scorer that wrote
none of them ran `tools/merit-adjudicate.mjs` against an incident-based rubric. The rubric, the receipt and
the scorecard are in `adjudications/machine-headroom-tools.*`. Result: C passed 12 of 12 MUST tests, A 8,
B 7. The SHOULD gaps C failed were fixed here by porting the better property from the other candidate,
with credit: working-folder attribution (A), span-based coverage with a 6 h minimum (B), and the
`heartbeats/` record path (B). Survivors not yet ported, recorded as follow-ups: A's clock-versus-load
curve, data-quality states, HeavySlot duration trend and ACL-locked bin; B's per-second histograms,
single-file plumbing commit and `-NeedCores/-NeedGB` fit query.

## Record shape (`fleet-host-headroom.v1`, abridged)

```json
{
  "schema": "fleet-host-headroom.v1", "machine": "PC-MINI2", "published_utc": "2026-11-17T06:00:00Z",
  "tool_commit": "<installed commit>", "window_hours": 168, "span_hours": 168, "samples": 34000, "coverage": 0.99,
  "hardware": { "logical_processors": 32, "cores": 16, "ram_gb": 93.7 },
  "cpu": { "busy_pct_p50": 8, "busy_pct_p95": 62, "burst_frac": 0.05, "saturated_frac": 0.01,
           "freq_pct_busy_p10": 66, "phys_cores_free_p90": 6.1 },
  "canary": { "runs": 2000, "single": { "p10_ms": 250, "slowdown_p95": 1.18 }, "wide": { "slowdown_p95": 1.41 } },
  "heavy_slot": { "gates": 189, "occupancy_frac": 0.99, "dead_holders": 36, "mean_holders": 0.4, "max_holders": 1, "wait_s_p90": 776,
                  "projects": [ { "project": "mlv-app", "wait_s_p95": 1400 } ] },
  "thermal": { "temp_ge90_frac": 0.02, "at_power_ceiling_frac": 0.04 },
  "projects": [ { "project": "airmypc", "cores_p95": 5.2, "ram_gb_p95": 9.8 } ],
  "attribution": { "unattributed_frac": 0.31, "families_cores_p95": { "defender": 2.1, "llm-cli": 0.9 } },
  "headroom": { "verdict": "TIGHT", "reasons": ["canary-wide-slowdown:1.41"], "heavy_slot_verdict": "ROOM",
                "phys_cores_free_p90": 6.1, "ram_gb_free": 48.2, "agents_max_rule": 8 }
}
```

The numbers above illustrate the shape; read real ones from the records.
