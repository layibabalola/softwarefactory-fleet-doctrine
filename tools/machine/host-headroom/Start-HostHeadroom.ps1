# Start-HostHeadroom.ps1 - the per-machine sampler for tools/machine/host-headroom (README.md beside this file).
#
#   -Run        the long-lived sampler (what the scheduled task starts). One per machine (named mutex).
#               Reads machine counters every second; every 5 minutes it writes one window record
#               (CPU histogram, Task-Manager-basis utility, commit, available RAM, disk latency and queue,
#               GPU busiest engine, a canary timing, CPU/RAM per project) to windows-<yyyyMMdd>.jsonl;
#               every hour it evaluates the verdict and, with -Publish, publishes to the bus when due.
#   -Once       one 60 s window, written and printed (a smoke test; it does not evaluate or publish).
#   -Install    registers task Fleet-HostHeadroom for the signed-in user (at logon + a 15 min keep-alive
#               trigger; a second instance is ignored), then starts it. -Publish is carried into the task.
#   -Uninstall  stops and removes the task. Data is kept.
#   -Status     liveness from the data, never from the task result (conhost --headless hides exit codes):
#               exit 0 fresh, 4 stale or absent.
# Read-only on the machine: it never kills, throttles or changes anything; it runs BelowNormal.
[CmdletBinding()]
param([switch]$Run, [switch]$Once, [switch]$Install, [switch]$Uninstall, [switch]$Status, [switch]$Publish,
    [string]$DataDir, [string]$BusRoot, [string[]]$WorkspaceRoot = @('C:\!Layi Wkspc'), [int]$WindowSeconds = 300,
    [string[]]$AddProjectRule = @())   # with -Install: '<substring>=<project>' rules appended to projects.json
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'HostHeadroom.psm1') -Force
$TaskName = 'Fleet-HostHeadroom'
if (-not $BusRoot) { $BusRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path }
if (-not $DataDir) { $DataDir = if ($env:HOST_HEADROOM_DIR) { $env:HOST_HEADROOM_DIR } else { Join-Path $env:LOCALAPPDATA 'fleet\host-headroom' } }
[void](New-Item -ItemType Directory -Force -Path $DataDir)
$logPath = Join-Path $DataDir 'sampler.log'
function Log([string]$m) {
    $line = "$([datetime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')) $m"
    try { if ((Test-Path $logPath) -and (Get-Item $logPath).Length -gt 1MB) { Move-Item $logPath "$logPath.1" -Force }; Add-Content -LiteralPath $logPath -Value $line -Encoding utf8 } catch { }
}

if ($Install) {
    if ($AddProjectRule.Count) {
        $cfg = Join-Path $DataDir 'projects.json'
        $have = @(); if (Test-Path -LiteralPath $cfg) { try { $have = @((Get-Content -LiteralPath $cfg -Raw | ConvertFrom-Json).rules) } catch { } }
        foreach ($r in $AddProjectRule) {
            $i = $r.LastIndexOf('='); if ($i -lt 1) { throw "-AddProjectRule '$r' is not '<substring>=<project>'" }
            $m = $r.Substring(0, $i); $p = $r.Substring($i + 1)
            if (-not ($have | Where-Object { $_.match -eq $m })) { $have += [pscustomobject]@{ match = $m; project = $p } }
        }
        [IO.File]::WriteAllText($cfg, (@{ rules = @($have) } | ConvertTo-Json -Depth 4), [Text.UTF8Encoding]::new($false))
    }
    $pw = (Get-Command pwsh).Source
    $extra = if ($Publish) { ' -Publish' } else { '' }
    $arg = "--headless `"$pw`" -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File `"$PSCommandPath`" -Run$extra"
    $action = New-ScheduledTaskAction -Execute "$env:WINDIR\System32\conhost.exe" -Argument $arg -WorkingDirectory $PSScriptRoot
    $me = [Security.Principal.WindowsIdentity]::GetCurrent().Name   # USERDOMAIN reads WORKGROUP over ssh
    $t1 = New-ScheduledTaskTrigger -AtLogOn -User $me
    $t2 = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 15)
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit ([TimeSpan]::Zero) -Priority 7
    $principal = New-ScheduledTaskPrincipal -UserId $me -LogonType Interactive -RunLevel Limited
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $t1, $t2 -Settings $settings -Principal $principal -Force `
        -Description 'Fleet host-headroom sampler (softwarefactory-fleet-doctrine tools/machine/host-headroom). Read-only; diagnostic only.' | Out-Null
    # A reinstall (new code path or -Publish) replaces a running sampler; otherwise the old one keeps the mutex.
    Get-CimInstance Win32_Process -Filter "Name='pwsh.exe'" | Where-Object { $_.CommandLine -like "*Start-HostHeadroom.ps1*-Run*" } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    Start-ScheduledTask -TaskName $TaskName
    Write-Output "INSTALLED $TaskName (publish=$([bool]$Publish)); data in $DataDir. Check with -Status after 5 minutes."
    return
}
if ($Uninstall) {
    Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Get-CimInstance Win32_Process -Filter "Name='pwsh.exe'" | Where-Object { $_.CommandLine -like "*Start-HostHeadroom.ps1*-Run*" } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    Write-Output "UNINSTALLED $TaskName; data kept in $DataDir"; return
}
if ($Status) {
    $last = Get-ChildItem $DataDir -Filter 'windows-*.jsonl' -ErrorAction SilentlyContinue | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
    $age = if ($last) { [math]::Round(([datetime]::UtcNow - $last.LastWriteTimeUtc).TotalMinutes, 1) } else { -1 }
    $t = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    $st = $null; $sp = Join-Path $DataDir 'state.json'; if (Test-Path $sp) { try { $st = Get-Content $sp -Raw | ConvertFrom-Json } catch { } }
    $live = @(Get-CimInstance Win32_Process -Filter "Name='pwsh.exe'" | Where-Object { $_.CommandLine -like "*Start-HostHeadroom.ps1*-Run*" }).Count
    Write-Output ("machine={0} task={1} sampler_processes={2} newest_window_age_min={3} verdict={4} recent={5} last_publish={6}" -f $env:COMPUTERNAME, $(if ($t) { $t.State } else { 'ABSENT' }), $live, $age, $st.published, (@($st.recent) -join ','), $st.lastPublishResult)
    if ($age -lt 0 -or $age -gt 15) { Write-Output 'STALE: no window in the last 15 minutes'; exit 4 }
    return
}
if (-not ($Run -or $Once)) { Write-Output 'Pass one of -Run, -Once, -Install, -Uninstall, -Status.'; exit 2 }

# ------------------------------------------------------------------------------------------------
# Sampler.
# ------------------------------------------------------------------------------------------------
if ($Once) { $WindowSeconds = 60 }
$mutex = [System.Threading.Mutex]::new($false, 'Local\FleetHostHeadroomSampler')
if ($Run -and -not $mutex.WaitOne(0)) { exit 0 }   # another sampler owns this machine
try { [System.Diagnostics.Process]::GetCurrentProcess().PriorityClass = 'BelowNormal' } catch { }

$paths = @(
    '\Processor Information(_Total)\% Processor Time',
    '\Processor Information(_Total)\% Processor Utility',
    '\Memory\Committed Bytes',
    '\Memory\Available MBytes',
    '\PhysicalDisk(_Total)\Avg. Disk sec/Transfer',
    '\PhysicalDisk(_Total)\Current Disk Queue Length'
)
$gpuPath = '\GPU Engine(*)\Utilization Percentage'
$rules = Get-HHProjectRules -WorkspaceRoots $WorkspaceRoot -ConfigPath (Join-Path $DataDir 'projects.json')
$prevSnap = Get-HHProcessSnapshot $rules; $prevTicks = [datetime]::UtcNow.Ticks; $prevAt = [datetime]::UtcNow
$lastEval = [datetime]::MinValue
Log "sampler start pid=$PID window=${WindowSeconds}s publish=$([bool]$Publish) bus=$(Split-Path -Leaf $BusRoot)"

function New-Series { @{ t = [System.Collections.Generic.List[double]]::new(); u = [System.Collections.Generic.List[double]]::new(); c = [System.Collections.Generic.List[double]]::new(); a = [System.Collections.Generic.List[double]]::new(); d = [System.Collections.Generic.List[double]]::new(); q = [System.Collections.Generic.List[double]]::new(); g = [System.Collections.Generic.List[double]]::new() } }

while ($true) {
    $s = New-Series; $start = [datetime]::UtcNow
    while (([datetime]::UtcNow - $start).TotalSeconds -lt ($WindowSeconds - 1)) {
        $n = [int][math]::Min(60, [math]::Max(1, $WindowSeconds - ([datetime]::UtcNow - $start).TotalSeconds))
        try { $sets = Get-Counter -Counter $paths -SampleInterval 1 -MaxSamples $n -ErrorAction SilentlyContinue } catch { Log "counter read failed: $($_.Exception.Message)"; Start-Sleep -Seconds $n; continue }
        foreach ($set in @($sets)) {
            foreach ($cs in $set.CounterSamples) {
                $v = [double]$cs.CookedValue; $p = $cs.Path
                if ($p -like '*% processor time') { $s.t.Add([math]::Min(100, $v)) }
                elseif ($p -like '*% processor utility') { $s.u.Add($v) }
                elseif ($p -like '*committed bytes') { $s.c.Add($v / 1GB) }
                elseif ($p -like '*available mbytes') { $s.a.Add($v / 1024) }
                elseif ($p -like '*avg. disk sec/transfer') { $s.d.Add($v * 1000) }
                elseif ($p -like '*current disk queue length') { $s.q.Add($v) }
            }
        }
        # GPU: the busiest single engine once a minute (the sum over engines over-counts; the read costs ~1 s).
        try { $g = (Get-Counter $gpuPath -ErrorAction SilentlyContinue).CounterSamples | Measure-Object CookedValue -Maximum; if ($g -and $null -ne $g.Maximum) { $s.g.Add([double]$g.Maximum) } } catch { }
    }
    if ($s.t.Count -eq 0) { Log 'window had no CPU samples'; if ($Once) { exit 2 }; continue }
    $canary = $null; try { $canary = Invoke-HHCanary } catch { Log "canary failed: $($_.Exception.Message)" }
    $snap = Get-HHProcessSnapshot $rules; $now = [datetime]::UtcNow
    $proj = Measure-HHProjectUse $prevSnap $snap ($now - $prevAt).TotalSeconds $prevTicks
    $prevSnap = $snap; $prevTicks = $now.Ticks; $prevAt = $now
    $rec = New-HHWindowRecord -EndUtc $now -CpuTime $s.t.ToArray() -CpuUtility $s.u.ToArray() -CommitGB $s.c.ToArray() -AvailGB $s.a.ToArray() `
        -DiskMs $s.d.ToArray() -DiskQueue $s.q.ToArray() -GpuMax $s.g.ToArray() -CanaryMs $canary -Projects $proj
    $line = $rec | ConvertTo-Json -Compress -Depth 6
    [IO.File]::AppendAllText((Join-Path $DataDir ("windows-{0}.jsonl" -f $now.ToString('yyyyMMdd'))), $line + "`n", [Text.UTF8Encoding]::new($false))
    if ($Once) { Write-Output $line; exit 0 }
    Get-ChildItem $DataDir -Filter 'windows-*.jsonl' | Where-Object { $_.LastWriteTimeUtc -lt $now.AddDays(-30) } | Remove-Item -Force -ErrorAction SilentlyContinue

    if (($now - $lastEval).TotalMinutes -ge 60) {
        $lastEval = $now
        try {
            $r = Invoke-HHEvaluation -DataDir $DataDir -BusRoot $BusRoot -NowUtc $now -UpdateState
            [IO.File]::WriteAllText((Join-Path $DataDir 'latest.json'), ($r | ConvertTo-Json -Depth 8), [Text.UTF8Encoding]::new($false))
            Log "eval verdict_now=$($r.verdict_now) published_verdict=$($r.verdict) findings=$($r.findings -join ',')"
            if ($Publish) { $p = Invoke-HHPublishIfDue -DataDir $DataDir -BusRoot $BusRoot -Record $r -NowUtc $now; if ($p.Code -ne 1 -or $p.Message -ne 'not due') { Log "publish code=$($p.Code) $($p.Message)" } }
        } catch { Log "eval failed: $($_.Exception.Message)" }
    }
}
