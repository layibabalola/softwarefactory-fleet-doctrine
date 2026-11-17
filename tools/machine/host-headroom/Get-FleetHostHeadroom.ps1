<#
  Fleet headroom view. Read-only. Answers: how much room does each machine have, and would a
  given project fit there without slowing the projects already on it?

    pwsh -NoProfile -File "$env:USERPROFILE\.claude\machine\host-headroom\Get-FleetHostHeadroom.ps1"                    # published records (bus origin/master)
    pwsh -NoProfile -File "$env:USERPROFILE\.claude\machine\host-headroom\Get-FleetHostHeadroom.ps1" -Live -Hours 24    # compute now on each mini over ssh
    pwsh -NoProfile -File "$env:USERPROFILE\.claude\machine\host-headroom\Get-FleetHostHeadroom.ps1" -Fit               # project footprint vs each machine's room
    ... -Json                                                          # machine-readable

  Published mode reads heartbeats/host-headroom/*.json at origin/master of a bus clone (after a fetch), so it
  never needs the checkout to be pulled. Status per record: ALIVE (published within -StaleHours),
  STALE, UNEVALUABLE (unreadable or wrong schema). Exit 0 = all ALIVE, 1 = some STALE/UNEVALUABLE,
  2 = nothing readable. A status tool that cannot fail is not a status tool.

  The verdict is DIAGNOSTIC (metrics law 1): it informs a placement decision, it does not make one.
#>
[CmdletBinding()]
param(
    [string]$BusRoot = $(if (Test-Path -LiteralPath (Join-Path $env:LOCALAPPDATA 'HostHeadroom\bus\.git')) { Join-Path $env:LOCALAPPDATA 'HostHeadroom\bus' } else { 'C:\!Layi Wkspc\softwarefactory-fleet-doctrine' }),
    [switch]$Live,
    [string[]]$Hosts = @('pc-mini1', 'pc-mini2', 'pc-mini3'),
    [double]$Hours = 168,
    [double]$StaleHours = 36,
    [switch]$Fit,
    [switch]$Json
)
$ErrorActionPreference = 'Stop'
$schema = 'fleet-host-headroom.v1'

function ConvertTo-Utc($v) { if ($v -is [datetime]) { if ($v.Kind -eq 'Unspecified') { [datetime]::SpecifyKind($v, 'Utc') } else { $v.ToUniversalTime() } } else { ([datetimeoffset]"$v").UtcDateTime } }

$records = [System.Collections.Generic.List[object]]::new()
if ($Live) {
    # $env:USERPROFILE stays literal here so each machine expands its OWN profile path
    $cmd = "& (Join-Path `$env:USERPROFILE '.claude\machine\host-headroom\Run-HostHeadroom.ps1') -Mode Summary -Hours $Hours"
    $enc = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($cmd))
    foreach ($h in $Hosts) {
        $isLocal = $h -ieq $env:COMPUTERNAME -or ($h -replace '^pc-', '') -ieq ($env:COMPUTERNAME -replace '^pc-', '')
        try {
            $out = if ($isLocal) { & pwsh -NoProfile -EncodedCommand $enc 2>$null } else { ssh -n -o BatchMode=yes -o ConnectTimeout=10 $h "pwsh -NoProfile -EncodedCommand $enc" 2>$null }
            $line = @($out | Where-Object { $_ -like '{*' })[-1]
            if ($line) { $r = $line | ConvertFrom-Json; $r | Add-Member status 'LIVE' -Force; $records.Add($r) }
            else { $records.Add([pscustomobject]@{ machine = $h.ToUpperInvariant(); status = 'UNREACHABLE' }) }
        } catch { $records.Add([pscustomobject]@{ machine = $h.ToUpperInvariant(); status = "UNREACHABLE: $($_.Exception.Message)" }) }
    }
} else {
    git -C $BusRoot fetch --quiet origin master 2>$null
    $names = @(git -C $BusRoot ls-tree --name-only origin/master heartbeats/host-headroom/ 2>$null | Where-Object { $_ -like '*.json' })
    foreach ($n in $names) {
        $machine = [IO.Path]::GetFileNameWithoutExtension($n)
        try {
            $r = (git -C $BusRoot show "origin/master:$n") -join "`n" | ConvertFrom-Json
            if ($r.schema -ne $schema -or $r.machine -ne $machine) { throw "schema/machine mismatch" }
            $age = ([datetime]::UtcNow - (ConvertTo-Utc $r.published_utc)).TotalHours
            $r | Add-Member status $(if ($age -le $StaleHours) { 'ALIVE' } else { 'STALE' }) -Force
            $r | Add-Member age_h ([math]::Round($age, 1)) -Force
            $records.Add($r)
        } catch { $records.Add([pscustomobject]@{ machine = $machine; status = "UNEVALUABLE: $($_.Exception.Message)" }) }
    }
}

$good = @($records | Where-Object { $_.PSObject.Properties['headroom'] })
$table = foreach ($r in $records) {
    if (-not $r.PSObject.Properties['headroom']) { [pscustomobject]@{ machine = $r.machine; status = $r.status }; continue }
    $top = @($r.projects | Where-Object { $_.project -notlike '_*' } | Sort-Object { [double]$_.cores_p95 } -Descending | Select-Object -First 3 |
             ForEach-Object { '{0} {1}c/{2}G' -f $_.project, $_.cores_p95, $_.ram_gb_p95 }) -join ', '
    [pscustomobject]@{
        machine     = $r.machine
        status      = $r.status
        verdict     = $r.headroom.verdict
        heavySlot   = "$($r.headroom.heavy_slot_verdict) $([math]::Round(100 * [double]$r.heavy_slot.occupancy_frac))%"
        busyP50P95  = "$($r.cpu.busy_pct_p50)/$($r.cpu.busy_pct_p95)%"
        burst       = "$([math]::Round(100 * [double]$r.cpu.burst_frac, 1))%"
        coresFreeP90 = $r.headroom.phys_cores_free_p90
        ramFreeGB   = $r.headroom.ram_gb_free
        canarySlow  = "x$($r.canary.single.slowdown_p95)/x$($r.canary.wide.slowdown_p95)"
        hot90       = $(if ($r.thermal -and $r.thermal.PSObject.Properties['temp_ge90_frac']) { "$([math]::Round(100 * [double]$r.thermal.temp_ge90_frac, 1))%" } else { 'n/a' })
        coverage    = $r.coverage
        topProjects = $top
        reasons     = (@($r.headroom.reasons) -join ' ')
    }
}

$fitRows = @()
if ($Fit -and $good) {
    # footprint = the largest p95 a project showed on any machine (cores, RAM); it fits a machine when
    # that machine's p90 free physical cores and free RAM both cover it and the verdict is not FULL.
    $proj = $good | ForEach-Object { $m = $_.machine; $_.projects | Where-Object { $_.project -notlike '_*' } | ForEach-Object { $_ | Add-Member host $m -Force -PassThru } }
    $fitRows = foreach ($g in ($proj | Group-Object project)) {
        $c = ($g.Group | Measure-Object { [double]$_.cores_p95 } -Maximum).Maximum
        $ram = ($g.Group | Measure-Object { [double]$_.ram_gb_p95 } -Maximum).Maximum
        $row = [ordered]@{ project = $g.Name; runs_on = (@($g.Group.host | Sort-Object -Unique) -join ','); cores_p95 = [math]::Round($c, 2); ram_gb_p95 = [math]::Round($ram, 1) }
        foreach ($r in $good) {
            $fits = $r.headroom.verdict -ne 'FULL' -and $r.headroom.verdict -ne 'UNEVALUABLE' -and [double]$r.headroom.phys_cores_free_p90 -ge $c -and [double]$r.headroom.ram_gb_free -ge $ram
            $row[$r.machine] = if ($r.headroom.verdict -eq 'UNEVALUABLE') { '?' } elseif ($fits) { 'fits' } else { 'no' }
        }
        [pscustomobject]$row
    }
}

if ($Json) { [ordered]@{ records = @($records); fit = @($fitRows) } | ConvertTo-Json -Depth 10 }
else {
    $table | Format-Table machine, status, verdict, heavySlot, busyP50P95, burst, coresFreeP90, ramFreeGB, canarySlow, hot90, coverage -AutoSize | Out-Host
    $table | Where-Object { $_.PSObject.Properties['topProjects'] } | Format-Table machine, topProjects, reasons -Wrap | Out-Host
    if ($Fit) { if ($fitRows) { $fitRows | Format-Table -AutoSize | Out-Host } else { 'no evaluable records to fit against' } }
}
if (-not $good) { exit 2 }
if (@($records | Where-Object { $_.status -notin 'ALIVE', 'LIVE' }).Count) { exit 1 }
exit 0
