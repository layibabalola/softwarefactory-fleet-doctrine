#Requires -Version 7.2
<#
.SYNOPSIS
  Install, check or remove the machine-load sampler and its daily bus publisher on THIS machine.

.DESCRIPTION
  -Install (default, ELEVATED: an ssh session on a mini is elevated): copies the tool from this folder (a bus
  clone) to C:\ProgramData\MachineLoad\bin, ACL-locked like FleetQuiet (SYSTEM and Administrators full,
  Users read and execute) because the sampler runs elevated from it, writes a hash manifest, registers two
  scheduled tasks under \Fleet\ for the signed-in account, and proves the sampler TASK writes a minute row.
  The sampler runs elevated only to read CPU time of system and protected processes (Defender, services);
  non-elevated it cannot see 132 of ~310 processes. The publisher runs non-elevated.
    \Fleet\MachineLoad Sampler    at logon, and every 5 min as a restart net (a second copy exits on the
                                  sampler's mutex; Task Scheduler also ignores a start while one runs)
    \Fleet\MachineLoad Publisher  daily, after the UTC day closes; appends finished days to the bus
  Both launch through the fleet's windowless shim (%USERPROFILE%\.claude\ops\launch-windowless.vbs): a bare
  pwsh/python action under an Interactive principal pops a console window (bus TRAPS).
  -Status: task state, last results, newest row age, last publish receipt. Read-only.
  -Remove: unregisters both tasks and stops the sampler. Keeps the data.

  Exit: 0 ok; 1 -Status found a problem; 2 shim missing; 3 install proof failed; 4 not elevated.
#>
[CmdletBinding(DefaultParameterSetName = 'Install')]
param(
    [Parameter(ParameterSetName = 'Status')][switch]$Status,
    [Parameter(ParameterSetName = 'Remove')][switch]$Remove,
    [string]$BusRoot = 'C:\!Layi Wkspc\softwarefactory-fleet-doctrine',
    [int]$ProofSeconds = 150
)
$ErrorActionPreference = 'Stop'
$TaskPath = '\Fleet\'
$SamplerTask = 'MachineLoad Sampler'
$PublisherTask = 'MachineLoad Publisher'
$DataDir = Join-Path $env:LOCALAPPDATA 'MachineLoad'
$BinDir = 'C:\ProgramData\MachineLoad\bin'   # ACL-locked: the sampler task runs elevated from here
$Vbs = Join-Path $env:USERPROFILE '.claude\ops\launch-windowless.vbs'
$Launcher = Join-Path $env:LOCALAPPDATA 'PairProg\bin\pairprog-hidden-task-launcher.exe'
$Pwsh = (Get-Command pwsh.exe).Source
$Python = (Get-Command python.exe -ErrorAction SilentlyContinue).Source
$Files = 'MachineLoadSampler.ps1', 'MachineLoadNative.cs', 'projects.json', 'machine_load.py'
$Registry = Join-Path $env:USERPROFILE '.claude\machine\SCHEDULED-TASK-REGISTRY.md'

function Get-SamplerState {
    $p = Join-Path $DataDir 'sampler-state.json'
    if (Test-Path $p) { try { return Get-Content -Raw $p | ConvertFrom-Json } catch { } }
    return $null
}
function Get-NewestRow {
    $f = Get-ChildItem $DataDir -Filter 'minute-*.jsonl' -File -ErrorAction SilentlyContinue | Sort-Object Name | Select-Object -Last 1
    if (-not $f) { return $null }
    $line = Get-Content $f.FullName -Tail 1
    if (-not $line) { return $null }
    return $line | ConvertFrom-Json
}
function Stop-Sampler {
    $s = Get-SamplerState
    if ($s -and $s.pid) {
        # by pid, verified by command line; never by name pattern alone (fleet lesson: kill by identity)
        $w = Get-CimInstance Win32_Process -Filter "ProcessId=$($s.pid)" -ErrorAction SilentlyContinue
        if ($w -and "$($w.CommandLine)" -match 'MachineLoadSampler\.ps1') { Stop-Process -Id $s.pid -Force; "stopped sampler pid $($s.pid)" }
    }
}

if ($Status) {
    $bad = @()
    foreach ($n in $SamplerTask, $PublisherTask) {
        $t = Get-ScheduledTask -TaskPath $TaskPath -TaskName $n -ErrorAction SilentlyContinue
        if (-not $t) { $bad += "task missing: $n"; continue }
        $i = $t | Get-ScheduledTaskInfo
        '{0,-24} state={1} last={2:u} result=0x{3:X} next={4:u}' -f $n, $t.State, $i.LastRunTime, $i.LastTaskResult, $i.NextRunTime
    }
    $row = Get-NewestRow
    if (-not $row) { $bad += 'no minute rows' } else {
        $age = [int]([DateTime]::UtcNow - [datetime]::Parse($row.ts).ToUniversalTime()).TotalSeconds
        "newest row $($row.ts) age ${age}s code=$($row.code) busy=$($row.cpu.busy_threads) sampler ws=$($row.sampler.ws_mb)MB"
        if ($age -gt 180) { $bad += "newest row is ${age}s old (STALE)" }
    }
    $rc = Join-Path $DataDir 'publish-receipt.json'
    if (Test-Path $rc) { 'last publish: ' + ((Get-Content -Raw $rc | ConvertFrom-Json) | ConvertTo-Json -Compress) } else { 'last publish: none yet' }
    $bad | ForEach-Object { "PROBLEM: $_" }
    exit ([int]($bad.Count -gt 0))
}

if ($Remove) {
    foreach ($n in $SamplerTask, $PublisherTask) { Unregister-ScheduledTask -TaskPath $TaskPath -TaskName $n -Confirm:$false -ErrorAction SilentlyContinue }
    Stop-Sampler
    "removed tasks; data kept in $DataDir"
    exit 0
}

# ---------------- install ----------------
$elevated = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $elevated) { Write-Host 'install needs an elevated shell (from another mini: ssh <alias> pwsh -NoProfile -File <this script>)'; exit 4 }
if (-not (Test-Path $Vbs) -or -not (Test-Path $Launcher)) { Write-Host "windowless shim missing ($Vbs / $Launcher); install coretemp-fleet first"; exit 2 }
if (-not $Python) { Write-Host 'python.exe not on PATH'; exit 2 }
$null = New-Item -ItemType Directory -Force -Path $BinDir
$null = New-Item -ItemType Directory -Force -Path $DataDir
& icacls.exe (Split-Path $BinDir) /inheritance:r /grant:r '*S-1-5-18:(OI)(CI)F' '*S-1-5-32-544:(OI)(CI)F' '*S-1-5-32-545:(OI)(CI)RX' | Out-Null
if ($LASTEXITCODE -ne 0) { Write-Host 'icacls failed'; exit 3 }
$src = $PSScriptRoot
$manifest = [ordered]@{ installed_utc = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ'); source = $src; bus_commit = (git -C $src rev-parse HEAD 2>$null); files = [ordered]@{} }
foreach ($f in $Files) {
    Copy-Item -Force (Join-Path $src $f) (Join-Path $BinDir $f)
    $manifest.files[$f] = (Get-FileHash -Algorithm SHA256 (Join-Path $BinDir $f)).Hash.ToLowerInvariant()
}
$manifest | ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $BinDir 'manifest.json')

$user = "$env:USERDOMAIN\$env:USERNAME"
$principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
$samplerPrincipal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -ExecutionTimeLimit ([TimeSpan]::Zero) -StartWhenAvailable `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -Hidden
function New-ShimAction([string]$Label, [string]$Exe, [string]$ArgLine) {
    $log = Join-Path $DataDir ($Label -replace '\s', '-').ToLowerInvariant()
    New-ScheduledTaskAction -Execute "$env:WINDIR\System32\wscript.exe" -Argument ("`"$Vbs`" --stdout `"$log.out.log`" --stderr `"$log.err.log`" --label `"$Label`" -- `"$Exe`" $ArgLine")
}

# Sampler: at logon + a 5-minute restart net.
$samplerAction = New-ShimAction 'MachineLoad Sampler' $Pwsh ("-NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$BinDir\MachineLoadSampler.ps1`"")
$net = New-ScheduledTaskTrigger -Once -At (Get-Date).Date -RepetitionInterval (New-TimeSpan -Minutes 5)
$logon = New-ScheduledTaskTrigger -AtLogOn -User $user
Register-ScheduledTask -TaskPath $TaskPath -TaskName $SamplerTask -Action $samplerAction -Trigger @($logon, $net) -Principal $samplerPrincipal -Settings $settings `
    -Description 'Fleet machine-load sampler (bus tools/machine/machine-load). One row per UTC minute to %LOCALAPPDATA%\MachineLoad. Diagnostic only.' -Force | Out-Null

# Publisher: daily, 75-105 min after the UTC day closes, staggered per machine so the minis do not race.
$offset = 75 + ([Math]::Abs($env:COMPUTERNAME.GetHashCode()) % 30)
$utcAt = [DateTime]::UtcNow.Date.AddMinutes($offset)
$pubAt = [DateTime]::SpecifyKind($utcAt, 'Utc').ToLocalTime()
$pubAction = New-ShimAction 'MachineLoad Publisher' $Python ("`"$BinDir\machine_load.py`" publish --bus `"$BusRoot`" --launched-by task")
$pubSettings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 15) -StartWhenAvailable `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -Hidden
Register-ScheduledTask -TaskPath $TaskPath -TaskName $PublisherTask -Action $pubAction -Trigger (New-ScheduledTaskTrigger -Daily -At $pubAt) -Principal $principal `
    -Settings $pubSettings -Description 'Fleet machine-load publisher: appends finished UTC days to the doctrine bus machine-load/<MACHINE>/. Diagnostic only.' -Force | Out-Null

# Scheduled-task registry entry (machine-local, once).
if (Test-Path (Split-Path $Registry)) {
    $reg = if (Test-Path $Registry) { Get-Content -Raw $Registry } else { '' }
    if ($reg -notmatch [regex]::Escape('### \Fleet\MachineLoad Sampler')) {
        Add-Content -Path $Registry -Value @"

## machine-load (bus tools/machine/machine-load, owner request 2026-11-16)

### \Fleet\MachineLoad Sampler
- **owner:** fleet machine tooling (bus ``tools/machine/machine-load``); machine owner controls retirement
- **purpose:** one long-lived hidden sampler (elevated, from ACL-locked C:\ProgramData\MachineLoad\bin) writing per-minute CPU, clock, memory, disk and per-project CPU rows to %LOCALAPPDATA%\MachineLoad.
- **cadence-rationale:** logon start plus a 5-minute restart net; a running copy holds a mutex, so extra starts exit at once.
- **retire-when:** the owner no longer wants machine headroom reporting, or a successor sampler replaces it (Install-MachineLoad.ps1 -Remove).

### \Fleet\MachineLoad Publisher
- **owner:** fleet machine tooling (bus ``tools/machine/machine-load``); machine owner controls retirement
- **purpose:** appends each finished UTC day's aggregate row to the doctrine bus machine-load/<MACHINE>/.
- **cadence-rationale:** daily, after the UTC day closes; at most one bus commit per machine per day (heartbeats law 3).
- **retire-when:** with the sampler.
"@
    }
}

# Proof: the TASK (not this process) must produce a fresh row.
Stop-Sampler | Out-Null
Start-Sleep -Seconds 2
$before = [DateTime]::UtcNow
Start-ScheduledTask -TaskPath $TaskPath -TaskName $SamplerTask
$deadline = $before.AddSeconds($ProofSeconds)
$ok = $false
while ([DateTime]::UtcNow -lt $deadline) {
    Start-Sleep -Seconds 10
    $s = Get-SamplerState
    if ($s -and [datetime]::Parse($s.written_utc).ToUniversalTime() -gt $before -and (Get-Process -Id $s.pid -ErrorAction SilentlyContinue)) { $ok = $true; break }
}
$t = Get-ScheduledTask -TaskPath $TaskPath -TaskName $SamplerTask | Get-ScheduledTaskInfo
$receipt = [ordered]@{
    utc = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ'); machine = $env:COMPUTERNAME; proof = if ($ok) { 'PASS' } else { 'FAIL' }
    sampler_pid = $s.pid; row_ts = $s.last_row_ts; code = $s.code; task_last_result = ('0x{0:X}' -f $t.LastTaskResult)
    publisher_utc = $utcAt.ToString('HH:mm') + 'Z'; bus_commit = $manifest.bus_commit
}
$receipt | ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $DataDir 'install-receipt.json')
$receipt | ConvertTo-Json -Compress
exit ([int](-not $ok) * 3)
