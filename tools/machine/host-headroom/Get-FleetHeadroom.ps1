# Get-FleetHeadroom.ps1 - the cross-machine view (tools/machine/host-headroom).
#   pwsh -NoProfile -File Get-FleetHeadroom.ps1                       read heartbeats/machines/*.json in this bus clone
#   pwsh -NoProfile -File Get-FleetHeadroom.ps1 -Live -Hosts pc-mini1,pc-mini2 [-IncludeLocal]
#                                                                     ask each machine now over ssh (BatchMode)
#   ... -NeedCores 4 -NeedGB 16                                       which machines can take a project that size
#   ... -Json
# Diagnostic only (metrics law 1): the answer informs a placement decision; it gates nothing.
# Exit 0 = every machine read; 1 = some STALE / UNREADABLE / INVALID; 2 = nothing to read.
[CmdletBinding()]
param([switch]$Live, [string[]]$Hosts = @(), [switch]$IncludeLocal, [double]$NeedCores = 0, [double]$NeedGB = 0,
    [switch]$Json, [string]$BusRoot, [string]$RemoteBusRoot = 'C:\!Layi Wkspc\softwarefactory-fleet-doctrine')
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'HostHeadroom.psm1') -Force
if (-not $BusRoot) { $BusRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path }
$pol = Get-HHPolicy; $now = [datetime]::UtcNow
$rows = New-Object System.Collections.Generic.List[object]

function Add-Row($name, $status, $rec, [string]$note, $ageH) {
    $w = if ($rec) { $rec.window } else { $null }
    $fit = $null
    if ($rec -and ($NeedCores -gt 0 -or $NeedGB -gt 0)) {
        $why = @()
        if ($rec.verdict -in 'SATURATED', 'INSUFFICIENT-DATA') { $why += $rec.verdict }
        if ($NeedCores -gt 0 -and ($null -eq $w.cpu.headroomCoresToKnee -or $w.cpu.headroomCoresToKnee -lt $NeedCores)) { $why += "cores $($w.cpu.headroomCoresToKnee) < $NeedCores" }
        if ($NeedGB -gt 0 -and ($null -eq $w.memory.headroomGB -or $w.memory.headroomGB -lt $NeedGB)) { $why += "GB $($w.memory.headroomGB) < $NeedGB" }
        if ($w.heavySlot -and ($w.heavySlot.duty -ge $pol.SlotBoundDuty -or $w.heavySlot.waitP90Sec -ge $pol.SlotBoundWaitP90Sec)) { $why += 'heavy-slot-bound (heavy jobs would queue)' }
        $fit = if ($why.Count) { 'NO: ' + ($why -join '; ') } else { 'FITS' }
    }
    $rows.Add([pscustomobject][ordered]@{
            machine = $name; status = $status; ageHours = $ageH
            verdict = if ($rec) { $rec.verdict } else { $null }; verdictNow = if ($rec) { $rec.verdict_now } else { $null }
            findings = if ($rec) { @($rec.findings) -join ',' } else { $null }
            cpuP95 = if ($w) { $w.cpu.timeP95 } else { $null }; busyThreadsP95 = if ($w) { $w.cpu.busyThreadsP95 } else { $null }
            coresFree = if ($w) { $w.cpu.headroomCoresToKnee } else { $null }; memFreeGB = if ($w) { $w.memory.headroomGB } else { $null }
            canaryP95 = if ($w) { $w.canary.ratioP95 } else { $null }
            slotDuty = if ($w -and $w.heavySlot) { $w.heavySlot.duty } else { $null }; slotWaitP90s = if ($w -and $w.heavySlot) { $w.heavySlot.waitP90Sec } else { $null }
            projects = if ($w -and $w.projects) { (@($w.projects.PSObject.Properties | Where-Object { $_.Name -notin 'system', 'defender' } | Sort-Object { - [double]$_.Value.threadsP95 } | ForEach-Object { '{0}:{1}t/{2}G' -f $_.Name, $_.Value.threadsP95, $_.Value.ramGBP95 })) -join ' ' } else { $null }
            fit = $fit; note = $note
        })
}

if ($Live) {
    $targets = @($Hosts | ForEach-Object { $_ -split ',' } | ForEach-Object { $_.Trim() } | Where-Object { $_ })   # pwsh -File passes "a,b" as one string
    foreach ($h in $targets) {
        $cmd = "pwsh -NoProfile -NonInteractive -File `"$RemoteBusRoot\tools\machine\host-headroom\Get-HostHeadroom.ps1`" -Json"
        $out = & ssh -o BatchMode=yes -o ConnectTimeout=10 $h $cmd 2>$null
        $raw = (@($out) -join "`n").Trim()
        $o = $null; try { $o = $raw | ConvertFrom-Json } catch { }
        if (-not $o) { Add-Row $h 'UNREADABLE' $null "ssh exit $LASTEXITCODE" $null; continue }
        if ($o.error) { Add-Row $o.machine 'NO-DATA' $null $o.error $null; continue }
        Add-Row $o.machine 'LIVE' $o '' 0
    }
    if ($IncludeLocal) {
        $raw = (& pwsh -NoProfile -NonInteractive -File (Join-Path $PSScriptRoot 'Get-HostHeadroom.ps1') -Json) -join "`n"
        $o = $null; try { $o = $raw | ConvertFrom-Json } catch { }
        if ($o -and -not $o.error) { Add-Row $o.machine 'LIVE' $o '' 0 } else { Add-Row $env:COMPUTERNAME 'NO-DATA' $null 'no local sampler data' $null }
    }
} else {
    $dir = Join-Path $BusRoot 'heartbeats\machines'
    foreach ($f in Get-ChildItem -LiteralPath $dir -Filter '*.json' -File -ErrorAction SilentlyContinue | Sort-Object Name) {
        $t = Test-HHRecord -Raw (Get-Content -LiteralPath $f.FullName -Raw) -FileStem $f.BaseName -NowUtc $now
        if (-not $t.Ok) { Add-Row $f.BaseName 'INVALID' $null $t.Why $null; continue }
        $age = [math]::Round(($now - $t.PublishedUtc).TotalHours, 1)
        Add-Row $f.BaseName $(if ($age -gt $pol.StaleHours) { 'STALE' } else { 'OK' }) $t.Record '' $age
    }
}

if ($rows.Count -eq 0) { if ($Json) { '[]' } else { Write-Output 'NOTHING TO READ: no heartbeats/machines/*.json (pull the bus) and no -Live hosts' }; exit 2 }
if ($Json) { $rows | ConvertTo-Json -Depth 4 } else {
    $cols = @('machine', 'status', 'ageHours', 'verdict', 'verdictNow', 'cpuP95', 'busyThreadsP95', 'coresFree', 'memFreeGB', 'canaryP95', 'slotDuty', 'slotWaitP90s')
    if ($NeedCores -gt 0 -or $NeedGB -gt 0) { $cols += 'fit' }
    $rows | Format-Table -Property $cols -AutoSize | Out-String -Width 220 | Write-Output
    foreach ($r in $rows) { if ($r.findings -or $r.projects -or $r.note) { Write-Output ("{0}: {1}{2}{3}" -f $r.machine, $(if ($r.findings) { "findings=$($r.findings) " }), $(if ($r.projects) { "projects=$($r.projects) " }), $r.note) } }
    Write-Output 'coresFree = physical cores left below the SMT knee at p95; memFreeGB keeps a 15% reserve; canaryP95 = slowdown of a fixed job vs the machine''s own quiet baseline.'
}
exit $(if (@($rows | Where-Object { $_.status -notin 'OK', 'LIVE' }).Count) { 1 } else { 0 })
