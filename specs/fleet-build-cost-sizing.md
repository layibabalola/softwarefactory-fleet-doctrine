# Fleet build-cost sizing and placement (DRAFT v1, 2026-11-18)

Status: proposal. Diagnostic until adopted; gates nothing. Lineage: the host-headroom sampler and dashboard
(`tools/machine/host-headroom/`, PR #100). Scope: every project and every machine (mini PC, laptop, VM).
Owner ask: "Is there universal sizing of build slots we can arrive on?" A heavy build for one project may be
light for another, so slots are priced, not counted.

## 1. Evidence that motivates it (one machine, 2026-11-18; re-derive before relying)
- The HeavySlot gate is project-blind: every admit is `class=shared`. Its ledger records wait and exit times, but not cost.
- On one mini, about half of the admits labelled heavy were test runs (`:pytest`), not builds.
- Host-headroom samples are host-level (busy, freq, commit, disk). No instrument measures what one build costs.

## 2. Units: two, never one scalar
- **CE (core-equivalent)** = one physical core of the reference mini (Ryzen 9 9955HX, 16C/32T) at its sustained loaded clock.
  - Other machines scale by a measured canary ratio, never a spec sheet.
  - Hybrid CPUs weight their efficiency cores by the same canary.
  - A VM's CE = min(its vCPUs x ratio, its host's free CE), and a VM's load is charged to its host as well.
- **GB** = peak commit, which is what decides whether a build fits in RAM.
- A display-only "reference-build equivalent" may be shown for people. It is never used for admission.

## 3. Per-ticket cost row (what every project reports, via the gate)
The gate already starts the child process. It runs the child in a Windows Job object and, at exit, appends this row to its ledger:

```
{ "schema": "build-cost.v1", "ticket": "...", "machine": "...", "label": "<project>:<target>:<class>",
  "class": "build|test|lint|link|package|other", "wall_s": 0.0, "cpu_s": 0.0, "cores": 0.0,
  "ce": 0.0, "peak_commit_gb": 0.0, "io_read_mb": 0.0, "io_write_mb": 0.0, "gpu": false,
  "jobs": 0, "toolchain": "cargo|cmake|qmake|msbuild|dotnet|node|python|nvcc|other",
  "holders_during": 0, "exit_code": 0 }
```

- `cores` = cpu_s / wall_s. `ce` = cores x the machine's canary ratio.
- `holders_during` = the most tickets held at once during this one, so the cost of overlap can be read directly.
- `jobs` is the declared parallelism (-j), so a project can see what -j costs it.
- Projects supply only a truthful label: project, target and class. Everything else is measured and never self-declared.
- The sampler joins clock and temperature over [admit, exit].

## 4. Machine capacity
capacity = (physical CE - 2 CE reserve, and RAM GB - 15 %) x thermal derate.

- The derate keys on clock drop, not on temperature: derate = freq_p50 under load / freq_p50 quiet, when that falls below 0.9.
- A temperature of 90 C or more stays a warning column, because it is within spec on current parts.

## 5. Admission (behind a flag; the fixed-cap gate stays the default)
- **Admit while it fits.** A ticket is admitted while the p90 cost of every held ticket, plus the newcomer's class p90, fits capacity.
- **Unknown labels.** An unknown label is charged the largest class p90 seen on that machine.
- **Fuse.** A hard holder cap stays as a fuse.
- **Dead holders.** A dead holder releases its cost at the next admit, and no later than 90 min after its admit.

## 6. Placement
Placement is vector bin-packing of each project's (class p90 cost x typical concurrency) onto machine capacity.
It answers both "which machines fit project P" and "which projects can share machine M".
The dashboard replaces its session-hours estimate with these vectors once 14 days of cost rows exist.

## 7. Order of work
1. Cost rows in the gate (review where the gate's source lives).
2. A per-class p50/p90 cost table in the host-headroom summary.
3. A canary CE ratio per machine.
4. Flagged fit-based admission.
5. Dashboard placement.

A bounded A/B of a fixed second slot may run before step 4. It counts only if dead holders are excluded and waits are split by holders.
