# Get-HostHeadroom.ps1 - this machine's headroom from its own sampler data (tools/machine/host-headroom).
#   pwsh -NoProfile -File Get-HostHeadroom.ps1 [-Hours 24] [-Json]
#   pwsh -NoProfile -File Get-HostHeadroom.ps1 -Publish [-NoPush]   publish now (owner/manual; the sampler
#                                                                    publishes on its own when installed with -Publish)
# Read-only unless -Publish. Exit 0 = evaluated; 2 = no sampler data on this machine.
[CmdletBinding()]
param([int]$Hours = 24, [switch]$Json, [switch]$Publish, [switch]$NoPush, [string]$DataDir, [string]$BusRoot)
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'HostHeadroom.psm1') -Force
if (-not $BusRoot) { $BusRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path }
if (-not $DataDir) { $DataDir = if ($env:HOST_HEADROOM_DIR) { $env:HOST_HEADROOM_DIR } else { Join-Path $env:LOCALAPPDATA 'fleet\host-headroom' } }
if (-not (Get-ChildItem $DataDir -Filter 'windows-*.jsonl' -ErrorAction SilentlyContinue)) {
    if ($Json) { [ordered]@{ schema = 'fleet-host-headroom.v1'; machine = $env:COMPUTERNAME; error = 'no sampler data (is Fleet-HostHeadroom installed?)' } | ConvertTo-Json -Compress } else { Write-Output "NO DATA on ${env:COMPUTERNAME}: install the sampler (Start-HostHeadroom.ps1 -Install)" }
    exit 2
}
$rec = Invoke-HHEvaluation -DataDir $DataDir -BusRoot $BusRoot -Hours $Hours
if ($Publish) {
    $r = Invoke-HHPublishIfDue -DataDir $DataDir -BusRoot $BusRoot -Record $rec -Force -NoPush:$NoPush
    Write-Output "PUBLISH code=$($r.Code): $($r.Message)"
    exit $(if ($r.Code -in 0, 1, 5) { 0 } else { 4 })
}
if ($Json) { $rec | ConvertTo-Json -Depth 8 -Compress; exit 0 }
$w = $rec.window; $c = $w.cpu; $m = $w.memory; $hs = $w.heavySlot
Write-Output ("{0}: verdict {1} (now {2}) {3}" -f $rec.machine, $rec.verdict, $rec.verdict_now, $(if ($rec.findings.Count) { '[' + ($rec.findings -join ', ') + ']' } else { '' }))
Write-Output ("  data      {0} h sampled in the last {1} h, {2} gaps" -f $w.coverage.sampledHours, $w.hours, $w.coverage.gaps)
Write-Output ("  cpu       p50 {0}% p95 {1}% p99 {2}% (Task Manager basis p95 {3}%); busy threads p95 {4} of {5}" -f $c.timeP50, $c.timeP95, $c.timeP99, $c.utilityP95, $c.busyThreadsP95, $rec.hardware.logical)
Write-Output ("  headroom  {0} cores to the {1}-core knee; {2} threads to the 75% ceiling; {3} GB memory" -f $c.headroomCoresToKnee, $rec.hardware.cores, $c.headroomThreadsToCeiling, $m.headroomGB)
Write-Output ("  memory    commit peak {0} of {1} GB; min available {2} of {3} GB" -f $m.commitPeakGB, $rec.hardware.commitLimitGB, $m.availMinGB, $rec.hardware.ramGB)
Write-Output ("  canary    baseline {0} ms; slowdown p50 x{1} p95 x{2}" -f $w.canary.baselineMs, $w.canary.ratioP50, $w.canary.ratioP95)
Write-Output ("  disk/gpu  disk ms/transfer p95 {0}; busiest GPU engine p95 {1}%" -f $w.disk.msPerTransferP95, $w.gpu.maxEngineP95)
if ($hs) { Write-Output ("  heavyslot duty {0}; wait p50 {1} s p90 {2} s max {3} s; {4} admits, {5} reaped, {6} holders gone with no exit line" -f $hs.duty, $hs.waitP50Sec, $hs.waitP90Sec, $hs.waitMaxSec, $hs.admits, $hs.reaped, $hs.unclosed) }
foreach ($k in $w.projects.Keys) { $p = $w.projects[$k]; Write-Output ("  project   {0,-16} threads mean {1} p95 {2}; RAM p95 {3} GB" -f $k, $p.threadsMean, $p.threadsP95, $p.ramGBP95) }
