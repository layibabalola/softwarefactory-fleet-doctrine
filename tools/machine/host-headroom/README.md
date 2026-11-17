# tools/machine/host-headroom: how much more can each fleet machine take?

A **machine tool** (like `tools/machine/fleet-mini`): every fleet machine samples its own load, judges its
own headroom, and publishes one aggregate record to `heartbeats/machines/<COMPUTERNAME>.json`. Any machine
reads the whole fleet with one command, and can ask "which machine can take a project needing N cores and
M GB without slowing what already runs there?"

**Diagnostic only** (metrics law 1): the verdict informs an owner's or hub's placement decision. It gates
nothing, and nothing reads it as authority. The sampler never kills, throttles or changes anything.

## Run it

```powershell
# on each machine, once (no elevation; runs as the signed-in user, at logon + a 15 min keep-alive)
pwsh -NoProfile -File <bus>\tools\machine\host-headroom\Start-HostHeadroom.ps1 -Install -Publish
pwsh -NoProfile -File <bus>\tools\machine\host-headroom\Start-HostHeadroom.ps1 -Status     # exit 0 fresh, 4 stale

# this machine, now
pwsh -NoProfile -File <bus>\tools\machine\host-headroom\Get-HostHeadroom.ps1 [-Hours 24] [-Json]

# the fleet, from the bus (pull first) or live over ssh
pwsh -NoProfile -File <bus>\tools\machine\host-headroom\Get-FleetHeadroom.ps1
pwsh -NoProfile -File <bus>\tools\machine\host-headroom\Get-FleetHeadroom.ps1 -Live -Hosts pc-mini1,pc-mini2 -IncludeLocal
pwsh -NoProfile -File <bus>\tools\machine\host-headroom\Get-FleetHeadroom.ps1 -NeedCores 4 -NeedGB 16
```

## Why the verdict is not "100 minus CPU %" (measured 2026-11-16 on the three minis)

Three adversarial reviews and the data refuted the obvious design:

- **Low CPU is not headroom.** On PC-MINI3, CPU p95 read about 28% while HeavySlot jobs waited up to 43
  minutes: the machine-wide heavy slot was held 70% of the day. Heavy work is serialized by policy, so a
  new project that uses HeavySlot adds queue time to every incumbent even on an idle CPU. The verdict
  therefore reads **contention**, not only utilization.
- **Snapshots miss bursts.** A 10 s window every 5 min covers 3% of the day; one mini peaked at 99% in 1 s
  samples while its largest 10 s mean was 29%. This sampler reads every second, all day, and keeps a
  1%-bin histogram per 5-minute window, so day percentiles are exact to the bin.
- **SMT.** 75% of 32 threads is all 16 cores plus most of the SMT gain; per-job throughput falls past
  about 16 busy threads. Headroom is reported in **physical cores to that knee**.
- **Two CPU numbers.** `% Processor Utility` (what Task Manager shows) reads 1.8-1.9x `% Processor Time`
  on these Ryzen parts because it scales by clock. Both are recorded; the budget uses Time, and Utility is
  shown as "Task Manager basis".
- **Bad signals dropped.** Processor Queue Length (almost always 0 on 32 LPs), Pages Input/sec (mapped
  file reads, not pressure), % Disk Time (meaningless on NVMe), and the SUM of GPU engines (over-counts).

## What is measured

| signal | how | used for |
|---|---|---|
| CPU | `% Processor Time` every second; 1%-bin histogram per 5 min | p50/p95/p99, busy threads, seconds above 75% |
| CPU (Task Manager basis) | `% Processor Utility` every second | shown, not judged |
| memory | committed bytes (max) and available MB (min) per window | headroom GB, keeping a 15% reserve of RAM and of the commit limit |
| disk | `Avg. Disk sec/Transfer` and current queue, every second | p95 latency |
| GPU | busiest single engine, once a minute | shown |
| **canary** | a fixed single-thread SHA-256 job (median of 3, ~40 ms idle) at Normal priority, every window | slowdown vs this machine's own 7-day 5th percentile = **how much slower a new job runs here** |
| **HeavySlot** | `%ProgramData%\HeavySlot\ledger.jsonl`, read-only | duty (share of the day the slot was held), wait p50/p90/max, held hours per project |
| per project | CPU-time delta per process between 5-minute snapshots, attributed by command-line ancestry to a project folder | threads mean/p95 and RAM p95 per project: the **footprint** a project would bring to another machine |

Attribution rules: each folder under `C:\!Layi Wkspc` is a project; extra rules (for example lane
worktrees outside the workspace) go in `%LOCALAPPDATA%\fleet\host-headroom\projects.json` as
`{"rules":[{"match":"C:\\mlvtmp\\","project":"MLV-App"}]}`. Known limit: a process that starts and exits
between two snapshots (a short compiler run) is not counted; the machine-level numbers still include it.

## Verdict (policy table: `Get-HHPolicy` in `HostHeadroom.psm1`)

| verdict | when (over 24 h) |
|---|---|
| `INSUFFICIENT-DATA` | under 6 sampled hours |
| `SATURATED` | busy threads p95 above 75% of LPs, or commit peak above 90% of the limit, or canary p95 at least 1.5x |
| `TIGHT` | under 4 cores to the knee, or under 12 GB memory headroom, or canary p95 at least 1.25x, or disk p95 at least 20 ms, or HeavySlot duty at least 0.70 or wait p90 at least 10 min (`heavy-slot-bound`) |
| `ROOM` | none of the above |

`-NeedCores/-NeedGB` answers FITS only when the cores to the knee and the memory headroom both cover the
need and the machine is not SATURATED; a slot-bound machine is called out, because a new project's heavy
jobs would queue behind the incumbents'.

## The published record (`fleet-host-headroom.v1`, `heartbeats/machines/<COMPUTERNAME>.json`)

| | |
|---|---|
| **Writer** | the sampler on that machine (`-Install -Publish`), hourly evaluation. Single writer per file: the file name is the writer's `COMPUTERNAME`. |
| **Push rule** | law 3: when the published verdict changes, or when the last publish is 24 h old. A verdict change must hold for **3 consecutive hourly evaluations** first (hysteresis), so a machine near a threshold never flaps the bus. At most one push an hour by construction. |
| **CI** | `heartbeats/**` is in the `paths-ignore` of `disposition-intake.yml`; no workflow runs on a record push. |
| **What travels** | numbers, the verdict, finding tokens, hardware counts, and project tokens **only for fleet members** (a `specs/<name>.md` exists); every other project folds into `other` (law 4: this bus is public). No paths, process names, user names, card ids or command lines. |
| **How it pushes** | plumbing on origin's tip through a private index (`git commit-tree`), so the checkout's working tree, index and HEAD are never touched; it pushes exactly that one-file commit, refetches and rebuilds once on a rejected push, and never prompts (`GCM_INTERACTIVE=never`). |
| **Reader** | `Get-FleetHeadroom.ps1`: OK / STALE (over 50 h) / INVALID; validation is `Test-HHRecord`, shared with the publisher's tests. |

A failed push is recorded in `state.json` and shown by `-Status`; the reader then shows the machine as
STALE. Over ssh, Git Credential Manager cannot reach the Windows vault, so the sampler runs in the
signed-in (autologon) session, never S4U.

## Local data (`%LOCALAPPDATA%\fleet\host-headroom\`, never on the bus)

`windows-<yyyyMMdd>.jsonl` (one line per 5 min, 30-day retention), `latest.json` (the last evaluation),
`state.json` (hysteresis and last publish), `sampler.log` (rotated at 1 MB). Measured cost: about 2.6
CPU-seconds per window including process snapshots and the canary, under 0.03% of a 32-thread machine;
the sampler runs BelowNormal and raises itself to Normal only for the canary.

## Tests

`pwsh -NoProfile -File tools/machine/host-headroom/HostHeadroom.tests.ps1`: no Pester, no elevation, no
network. Covers percentiles and histograms, rollup and verdict on synthetic quiet, bursty, low-memory,
high-commit and gappy machines, HeavySlot duty (including holders that died without an exit line),
hysteresis, the law-4 token filter, the validator, attribution (including a parent-pid cycle), and the
publisher on a throwaway repo with a throwaway bare origin.
