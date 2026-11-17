#Requires -Version 7.2
<#
.SYNOPSIS
  Install, check or remove the machine-load sampler and its daily bus publisher on THIS machine.

.DESCRIPTION
  -Install (default, ELEVATED; an ssh session on a mini is elevated):
    1. Builds C:\ProgramData\MachineLoad\{bin,data}, owned by Administrators, with SYSTEM and Administrators
       full and Users read-only (inheritance cut at the root, every child reset). It then VERIFIES the result:
       no account other than SYSTEM or Administrators may write anywhere under it, and the owner of every item
       is SYSTEM or Administrators. Anything else refuses the install. (C:\ProgramData lets Users create
       folders, so a pre-planted folder or file is the attack this check exists for.)
    2. Copies the tool and the windowless launcher (hash-pinned below) into bin. Everything the ELEVATED task
       starts lives there: no user-writable file is on the elevated launch path.
    3. Registers \Fleet\MachineLoad Sampler (elevated: it reads the CPU time of services and protected
       processes; at logon + a 5-minute restart net; a running copy holds a mutex) and
       \Fleet\MachineLoad Publisher (NOT elevated, daily after the UTC day closes).
    4. Proves the TASK (not this script) writes a fresh row with the code hash of the files just installed.
  -Status: task state, last results, newest row age, last publish receipt. Read-only, no elevation needed.
  -Remove (elevated): unregisters both tasks and stops the sampler. Keeps the data.

  Exit: 0 ok; 1 -Status found a problem; 2 a prerequisite is missing; 3 install refused or proof failed;
  4 not elevated.
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
$Root = 'C:\ProgramData\MachineLoad'
$BinDir = Join-Path $Root 'bin'
$DataDir = Join-Path $Root 'data'
$UserDir = Join-Path $env:LOCALAPPDATA 'MachineLoad'      # the non-elevated publisher's receipts and logs
$Pwsh = Join-Path $env:ProgramFiles 'PowerShell\7\pwsh.exe'  # absolute: never a user-writable WindowsApps alias
$LauncherName = 'pairprog-hidden-task-launcher.exe'
$LauncherSha256 = 'C91F27B4745B316D94858BBE013C887780EE86CF880294F1BF37572A8287A9DA'   # coretemp-fleet bundle pin
$LauncherSources = @(
    (Join-Path $env:USERPROFILE ".claude\machine\coretemp-fleet\bundle\PairProg-bin\$LauncherName"),
    (Join-Path $env:LOCALAPPDATA "PairProg\bin\$LauncherName"))
$UserVbs = Join-Path $env:USERPROFILE '.claude\ops\launch-windowless.vbs'   # non-elevated publisher only
$Files = 'MachineLoadSampler.ps1', 'MachineLoadNative.cs', 'projects.json', 'machine_load.py'
$Registry = Join-Path $env:USERPROFILE '.claude\machine\SCHEDULED-TASK-REGISTRY.md'
$AdminSids = @('S-1-5-18', 'S-1-5-32-544')   # SYSTEM, Administrators

function Test-Elevated { ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator) }
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
    # by pid, verified by command line; never by name pattern alone
    # only pwsh 7 itself, running exactly an installed sampler script (this or the earlier per-user bin)
    foreach ($w in @(Get-CimInstance Win32_Process -Filter "Name='pwsh.exe'" -ErrorAction SilentlyContinue)) {
        if ($w.ExecutablePath -eq $Pwsh -and "$($w.CommandLine)" -match '-File\s+"[A-Za-z]:\\[^"]*\\MachineLoad\\bin\\MachineLoadSampler\.ps1"\s*$') {
            Stop-Process -Id $w.ProcessId -Force -ErrorAction SilentlyContinue; "stopped sampler pid $($w.ProcessId)"
        }
    }
}
function Get-CodeHash([string]$Dir) {
    # the same identity the sampler stamps on each row (MachineLoadSampler.ps1 "code identity")
    $hashes = foreach ($f in 'MachineLoadSampler.ps1', 'MachineLoadNative.cs', 'projects.json') { (Get-FileHash -Algorithm SHA256 (Join-Path $Dir $f)).Hash }
    $sha = [Security.Cryptography.SHA256]::Create()
    ([BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes(($hashes -join ','))))).Replace('-', '').Substring(0, 12).ToLowerInvariant()
}
function Test-LockedTree([string]$Path) {
    # returns a list of problems; empty = only SYSTEM/Administrators can change anything under $Path
    $bad = @()
    # Atomic write bits only: the composite names (Write, Modify, FullControl) also carry read and
    # Synchronize bits, so OR-ing them in flagged a correct read-only ACE as writable.
    # WriteData/CreateFiles 0x2, AppendData 0x4, WriteEA 0x10, DeleteChild 0x40, WriteAttributes 0x100,
    # Delete 0x10000, WRITE_DAC 0x40000, WRITE_OWNER 0x80000, GENERIC_ALL 0x10000000, GENERIC_WRITE 0x40000000.
    $writeRights = 0x2 -bor 0x4 -bor 0x10 -bor 0x40 -bor 0x100 -bor 0x10000 -bor 0x40000 -bor 0x80000 -bor 0x10000000 -bor 0x40000000
    foreach ($item in @(Get-Item -Force $Path) + @(Get-ChildItem -Force -Recurse $Path)) {
        $acl = Get-Acl -LiteralPath $item.FullName
        $owner = ([Security.Principal.NTAccount]$acl.Owner).Translate([Security.Principal.SecurityIdentifier]).Value
        if ($owner -notin $AdminSids) { $bad += "owner $($acl.Owner) on $($item.FullName)" }
        foreach ($ace in $acl.Access) {
            if ($ace.AccessControlType -ne 'Allow') { continue }
            $sid = try { $ace.IdentityReference.Translate([Security.Principal.SecurityIdentifier]).Value } catch { "$($ace.IdentityReference)" }
            if ($sid -in $AdminSids) { continue }
            if (([long][int]$ace.FileSystemRights -band [long]$writeRights) -ne 0) { $bad += "$($ace.IdentityReference) can write ($($ace.FileSystemRights)) on $($item.FullName)" }
        }
    }
    return $bad
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
    $rc = Join-Path $UserDir 'publish-receipt.json'
    if (Test-Path $rc) { 'last publish: ' + ((Get-Content -Raw $rc | ConvertFrom-Json) | ConvertTo-Json -Compress) } else { 'last publish: none yet' }
    $bad | ForEach-Object { "PROBLEM: $_" }
    exit ([int]($bad.Count -gt 0))
}

if (-not (Test-Elevated)) { Write-Host 'needs an elevated shell (from another mini: ssh <alias> pwsh -NoProfile -File <this script>)'; exit 4 }

if ($Remove) {
    foreach ($n in $SamplerTask, $PublisherTask) { Unregister-ScheduledTask -TaskPath $TaskPath -TaskName $n -Confirm:$false -ErrorAction SilentlyContinue }
    Stop-Sampler
    "removed tasks; data kept in $DataDir"
    exit 0
}

# ---------------- install ----------------
if (-not (Test-Path $Pwsh)) { Write-Host "pwsh 7 not at $Pwsh"; exit 2 }
# Resolve the interpreter python itself reports (sys.executable), so a Python install-manager or
# Store alias on PATH resolves to the real python.exe, and a Store "install me" stub (which does not
# run) is refused instead of being written into the task.
$Python = $null
foreach ($c in @(Get-Command python.exe -All -ErrorAction SilentlyContinue)) {
    # No Select-Object -First here: it stops the pipeline before the native exit code is set.
    $out = @(& $c.Source -c 'import sys; print(sys.executable)' 2>$null)
    $exe = if ($out.Count) { "$($out[0])".Trim() } else { '' }
    if ($LASTEXITCODE -eq 0 -and $exe -and (Test-Path -LiteralPath $exe)) { $Python = $exe; break }
}
if (-not $Python) { Write-Host 'no runnable python.exe on PATH'; exit 2 }
if (-not (Test-Path $UserVbs)) { Write-Host "windowless shim missing: $UserVbs (install coretemp-fleet first)"; exit 2 }
$launcherSrc = $LauncherSources | Where-Object { (Test-Path $_) -and (Get-FileHash -Algorithm SHA256 $_).Hash -eq $LauncherSha256 } | Select-Object -First 1
if (-not $launcherSrc) { Write-Host "no $LauncherName matching the pinned SHA-256 $LauncherSha256"; exit 2 }

Stop-Sampler | Out-Null
foreach ($d in $Root, $BinDir, $DataDir, $UserDir) { $null = New-Item -ItemType Directory -Force -Path $d }

# Older installs wrote minute rows to %LOCALAPPDATA%\MachineLoad: carry them over (data only, never code).
foreach ($f in Get-ChildItem $UserDir -Filter 'minute-*.jsonl' -File -ErrorAction SilentlyContinue) {
    $dest = Join-Path $DataDir $f.Name
    if (Test-Path $dest) { Add-Content -Path $dest -Value (Get-Content -Raw $f.FullName).TrimEnd("`n") } else { Copy-Item $f.FullName $dest }
    Remove-Item -Force $f.FullName
}

$src = $PSScriptRoot
$manifest = [ordered]@{ installed_utc = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ'); bus_commit = (git -C $src rev-parse HEAD 2>$null); files = [ordered]@{} }
foreach ($f in $Files) {
    Copy-Item -Force (Join-Path $src $f) (Join-Path $BinDir $f)
    $manifest.files[$f] = (Get-FileHash -Algorithm SHA256 (Join-Path $BinDir $f)).Hash.ToLowerInvariant()
}
Copy-Item -Force $launcherSrc (Join-Path $BinDir $LauncherName)
$manifest.files[$LauncherName] = $LauncherSha256.ToLowerInvariant()
$manifest | ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $BinDir 'manifest.json')

# Lock the tree: Administrators own everything, inheritance cut at the root, every child reset to inherit.
& icacls.exe $Root /setowner '*S-1-5-32-544' /T /C /Q | Out-Null
& icacls.exe $Root /inheritance:r /grant:r '*S-1-5-18:(OI)(CI)F' '*S-1-5-32-544:(OI)(CI)F' '*S-1-5-32-545:(OI)(CI)RX' /Q | Out-Null
& icacls.exe "$Root\*" /reset /T /C /Q | Out-Null
$aclProblems = Test-LockedTree $Root
if ($aclProblems) { $aclProblems | ForEach-Object { "REFUSED: $_" }; Write-Host 'install refused: the install tree is writable by a non-admin'; exit 3 }
if ((Get-FileHash -Algorithm SHA256 (Join-Path $BinDir $LauncherName)).Hash -ne $LauncherSha256) { Write-Host 'launcher hash changed after copy'; exit 3 }

$user = [Security.Principal.WindowsIdentity]::GetCurrent().Name   # USERDOMAIN reads WORKGROUP in an ssh session
$settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -ExecutionTimeLimit ([TimeSpan]::Zero) -StartWhenAvailable `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -Hidden

# Sampler: elevated; the GUI-subsystem launcher in the locked bin starts pwsh with no window.
$launcher = Join-Path $BinDir $LauncherName
$samplerArgs = "--stdout `"$DataDir\sampler.out.log`" --stderr `"$DataDir\sampler.err.log`" --label `"MachineLoad Sampler`" -- `"$Pwsh`" -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$BinDir\MachineLoadSampler.ps1`""
$samplerAction = New-ScheduledTaskAction -Execute $launcher -Argument $samplerArgs
$net = New-ScheduledTaskTrigger -Once -At (Get-Date).Date -RepetitionInterval (New-TimeSpan -Minutes 5)
$logon = New-ScheduledTaskTrigger -AtLogOn -User $user
Register-ScheduledTask -TaskPath $TaskPath -TaskName $SamplerTask -Action $samplerAction -Trigger @($logon, $net) `
    -Principal (New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Highest) -Settings $settings `
    -Description 'Fleet machine-load sampler (bus tools/machine/machine-load). One row per UTC minute to C:\ProgramData\MachineLoad\data. Diagnostic only.' -Force | Out-Null

# Publisher: NOT elevated; 75-104 min after the UTC day closes, a fixed per-machine offset so the minis do not race.
$offset = 75 + (($env:COMPUTERNAME.ToCharArray() | ForEach-Object { [int]$_ } | Measure-Object -Sum).Sum % 30)
$pubAt = [DateTime]::SpecifyKind([DateTime]::UtcNow.Date.AddMinutes($offset), 'Utc').ToLocalTime()
$log = Join-Path $UserDir 'publisher'
$pubAction = New-ScheduledTaskAction -Execute "$env:WINDIR\System32\wscript.exe" -Argument ("`"$UserVbs`" --stdout `"$log.out.log`" --stderr `"$log.err.log`" --label `"MachineLoad Publisher`" -- `"$Python`" `"$BinDir\machine_load.py`" publish --bus `"$BusRoot`" --launched-by task")
$pubSettings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 15) -StartWhenAvailable `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -Hidden
Register-ScheduledTask -TaskPath $TaskPath -TaskName $PublisherTask -Action $pubAction -Trigger (New-ScheduledTaskTrigger -Daily -At $pubAt) `
    -Principal (New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited) -Settings $pubSettings `
    -Description 'Fleet machine-load publisher: appends finished UTC days to the doctrine bus machine-load/<MACHINE>/. Diagnostic only.' -Force | Out-Null

# Scheduled-task registry entry (machine-local, once).
if (Test-Path (Split-Path $Registry)) {
    $reg = if (Test-Path $Registry) { Get-Content -Raw $Registry } else { '' }
    if ($reg -notmatch [regex]::Escape('### \Fleet\MachineLoad Sampler')) {
        Add-Content -Path $Registry -Value @"

## machine-load (bus tools/machine/machine-load, owner request 2026-11-16)

### \Fleet\MachineLoad Sampler
- **owner:** fleet machine tooling (bus ``tools/machine/machine-load``); machine owner controls retirement
- **purpose:** one long-lived hidden sampler (elevated, launched only from ACL-locked C:\ProgramData\MachineLoad\bin) writing per-minute CPU, clock, memory, disk and per-project CPU rows to C:\ProgramData\MachineLoad\data.
- **cadence-rationale:** logon start plus a 5-minute restart net; a running copy holds a mutex, so extra starts exit at once.
- **retire-when:** the owner no longer wants machine headroom reporting, or a successor sampler replaces it (Install-MachineLoad.ps1 -Remove).

### \Fleet\MachineLoad Publisher
- **owner:** fleet machine tooling (bus ``tools/machine/machine-load``); machine owner controls retirement
- **purpose:** appends each finished UTC day's aggregate row to the doctrine bus machine-load/<MACHINE>/ (not elevated).
- **cadence-rationale:** daily, after the UTC day closes; at most one bus commit per machine per day (heartbeats law 3).
- **retire-when:** with the sampler.
"@
    }
}

# Proof: the TASK must produce a fresh row stamped with the code just installed.
$expected = Get-CodeHash $BinDir
$before = [DateTime]::UtcNow
Start-ScheduledTask -TaskPath $TaskPath -TaskName $SamplerTask
$deadline = $before.AddSeconds($ProofSeconds)
$ok = $false
$s = $null
while ([DateTime]::UtcNow -lt $deadline) {
    Start-Sleep -Seconds 10
    $s = Get-SamplerState
    if ($s -and $s.code -eq $expected -and [datetime]::Parse($s.written_utc).ToUniversalTime() -gt $before -and (Get-Process -Id $s.pid -ErrorAction SilentlyContinue)) { $ok = $true; break }
}
$t = Get-ScheduledTask -TaskPath $TaskPath -TaskName $SamplerTask | Get-ScheduledTaskInfo
$receipt = [ordered]@{
    utc = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ'); machine = $env:COMPUTERNAME; proof = if ($ok) { 'PASS' } else { 'FAIL' }
    sampler_pid = $s.pid; row_ts = $s.last_row_ts; code = $s.code; expected_code = $expected; task_last_result = ('0x{0:X}' -f $t.LastTaskResult)
    publisher_local = $pubAt.ToString('HH:mm'); acl = 'locked'; bus_commit = $manifest.bus_commit
}
$receipt | ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $DataDir 'install-receipt.json')
$receipt | ConvertTo-Json -Compress
exit ([int](-not $ok) * 3)
