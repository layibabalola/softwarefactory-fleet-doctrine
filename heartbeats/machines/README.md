# `heartbeats/machines/` - one headroom record per fleet machine

`heartbeats/machines/<COMPUTERNAME>.json` (`fleet-host-headroom.v1`) is a machine's own measured headroom:
CPU in cores to the SMT knee, memory headroom, a canary slowdown, HeavySlot contention and per-project
footprints. Writer, push rule, what travels and the reader are in
[`tools/machine/host-headroom/README.md`](../../tools/machine/host-headroom/README.md). Diagnostic only.

Read the fleet: `pwsh -NoProfile -File tools/machine/host-headroom/Get-FleetHeadroom.ps1`
