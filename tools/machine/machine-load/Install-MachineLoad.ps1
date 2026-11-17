#Requires -Version 7.2
<#
.SYNOPSIS
  Install, check or remove the machine-load sampler and its daily bus publisher on THIS machine.

.DESCRIPTION
  -Install (default, ELEVATED; an ssh session on a mini is elevated):
    0. Disables the sampler task and stops the running sampler, so nothing restarts old code mid-install.
    1. LOCKS C:\ProgramData\MachineLoad\{bin,data} before copying any code: owned by Administrators, SYSTEM and
       Administrators full, Users read-only (inheritance cut at the root, every child reset). It then VERIFIES:
       no junction, symlink or hard link anywhere, no owner or write right outside SYSTEM/Administrators, and
       nothing in data but the sampler's own file names. Anything else refuses the install. (C:\ProgramData lets
       Users create folders, so a pre-planted folder, junction, link or file is the attack this exists for.)
    2. Deletes bin and rebuilds it from nothing, copies the tool and the windowless launcher (hash-pinned below),
       re-locks, and verifies bin holds EXACTLY those files with the source's hashes (no planted .config/DLL).
       Everything the ELEVATED task starts lives there: no user-writable file is on the elevated launch path.
    3. Registers \Fleet\MachineLoad Sampler (as SYSTEM: it reads the CPU time of services and protected
       processes, and SYSTEM's environment is not user-writable; at boot + a 5-minute restart net; a running
       copy holds a mutex) and
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
function ConvertTo-Utc($v) {
    # ConvertFrom-Json already turns ISO-8601 strings into DateTime; re-parsing its local-format string would
    # shift it by the UTC offset (a 6 h error that made the staleness check and the proof's "after" test lie).
    if ($v -is [datetime]) { if ($v.Kind -eq 'Unspecified') { return [DateTime]::SpecifyKind($v, 'Utc') } return $v.ToUniversalTime() }
    return [DateTime]::Parse([string]$v, [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::AdjustToUniversal -bor [Globalization.DateTimeStyles]::AssumeUniversal)
}
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
. (Join-Path $PSScriptRoot 'MachineLoadInstallLib.ps1')   # Test-LockedTree, Test-InstallContents, Test-SamplerCommandLine
function Stop-Sampler {
    # by pid, verified by executable and exact command line; never by name pattern alone
    foreach ($w in @(Get-CimInstance Win32_Process -Filter "Name='pwsh.exe'" -ErrorAction SilentlyContinue)) {
        if (Test-SamplerCommandLine -ExecutablePath $w.ExecutablePath -CommandLine $w.CommandLine -Pwsh $Pwsh) {
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
if ($Status) {
    $bad = @()
    foreach ($n in $SamplerTask, $PublisherTask) {
        $t = Get-ScheduledTask -TaskPath $TaskPath -TaskName $n -ErrorAction SilentlyContinue
        if (-not $t) { $bad += "task missing: $n"; continue }
        $i = $t | Get-ScheduledTaskInfo
        '{0,-24} state={1} last={2:u} result=0x{3:X} next={4:u}' -f $n, $t.State, $i.LastRunTime.ToUniversalTime(), $i.LastTaskResult, $i.NextRunTime.ToUniversalTime()
        if ($t.State -eq 'Disabled') { $bad += "task disabled: $n" }
        # 0 ok, 0x41301 running, 0x41303 not yet run; anything else is a failed last run
        if ($i.LastTaskResult -notin 0, 0x41301, 0x41303) { $bad += ("{0} last run failed: 0x{1:X}" -f $n, $i.LastTaskResult) }
    }
    $row = Get-NewestRow
    if (-not $row) { $bad += 'no minute rows' } else {
        $age = [int]([DateTime]::UtcNow - (ConvertTo-Utc $row.ts)).TotalSeconds
        "newest row $((ConvertTo-Utc $row.ts).ToString('yyyy-MM-ddTHH:mm:ssZ')) age ${age}s code=$($row.code) busy=$($row.cpu.busy_threads) sampler ws=$($row.sampler.ws_mb)MB"
        if ($age -gt 180) { $bad += "newest row is ${age}s old (STALE)" }
    }
    $rc = Join-Path $UserDir 'publish-receipt.json'
    if (Test-Path $rc) {
        $r = Get-Content -Raw $rc | ConvertFrom-Json
        'last publish: ' + ($r | ConvertTo-Json -Compress)
        if ($r.exit -ne 0) { $bad += "last publish exited $($r.exit)" }
        # the publisher runs daily; a receipt over 50 h old means at least one daily run left none
        $rage = ([DateTime]::UtcNow - (ConvertTo-Utc $r.utc)).TotalHours
        if ($rage -gt 50) { $bad += ("last publish receipt is {0:N0} h old" -f $rage) }
    } else { 'last publish: none yet' }
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
# (This elevated installer runs python and git from the operator's PATH and is itself run from the operator's
# checkout: the operator is trusted at install time. Only what the SYSTEM task later runs must be admin-only.)
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

# Nothing may restart the old code while it is replaced: disable the task first, then stop the running sampler.
if (Get-ScheduledTask -TaskPath $TaskPath -TaskName $SamplerTask -ErrorAction SilentlyContinue) {
    Disable-ScheduledTask -TaskPath $TaskPath -TaskName $SamplerTask | Out-Null
}
Stop-Sampler | Out-Null

# Source hashes, taken BEFORE anything is copied: the installed bin must match these exactly. A dirty checkout
# is refused, so the bytes installed are the commit the manifest and every published row name.
$src = $PSScriptRoot
$dirty = git -C $src status --porcelain -- . 2>$null
if ($LASTEXITCODE -ne 0) { Write-Host "install refused: $src is not a git checkout (the manifest must name the commit installed)"; exit 2 }
if ($dirty) { $dirty | ForEach-Object { "DIRTY: $_" }; Write-Host 'install refused: uncommitted changes in the tool folder'; exit 2 }
$expectedBin = @{}
foreach ($f in $Files) { $expectedBin[$f] = (Get-FileHash -Algorithm SHA256 (Join-Path $src $f)).Hash.ToLowerInvariant() }
$expectedBin[$LauncherName] = $LauncherSha256.ToLowerInvariant()

# A missing root is created with its final protected DACL in one call. An EXISTING root (and everything under
# it) must already be owned by SYSTEM/Administrators with no other principal able to change permissions, and
# hold no link: otherwise a handle opened before the lock could undo it, so the install refuses instead of
# locking in place. (C:\ProgramData lets Users create folders: a pre-planted root is the attack.)
if (-not (Test-Path -LiteralPath $Root)) {
    New-ProtectedDirectory -Path $Root
} else {
    $pre = @(Test-PreLockTree -Path $Root)
    if ($pre) { $pre | ForEach-Object { "REFUSED: $_" }; Write-Host "install refused: $Root existed with an untrusted owner, right or link; inspect and remove it by hand"; exit 3 }
}
foreach ($d in $BinDir, $DataDir) { $null = New-Item -ItemType Directory -Force -Path $d }

# 1. LOCK FIRST, before any code is copied: Administrators own everything, inheritance cut at the root,
#    every child reset to inherit. From here on no non-admin can add or change anything under $Root.
function Lock-Tree {
    & icacls.exe $Root /setowner '*S-1-5-32-544' /T /C /Q | Out-Null
    & icacls.exe $Root /inheritance:r /grant:r '*S-1-5-18:(OI)(CI)F' '*S-1-5-32-544:(OI)(CI)F' '*S-1-5-32-545:(OI)(CI)RX' /Q | Out-Null
    & icacls.exe "$Root\*" /reset /T /C /Q | Out-Null
}
Lock-Tree
# 2. VERIFY the locked tree before trusting it: no junction, symlink or hard link anywhere (an elevated append
#    through a hard link writes the link's target), no foreign owner or write right, nothing unexpected in data.
$problems = @(Test-LockedTree $Root) + @(Test-InstallContents -BinDir $BinDir -DataDir $DataDir -Expected @{} | Where-Object { $_ -notmatch '^unexpected file in bin|^unexpected folder in bin' })
if ($problems) { $problems | ForEach-Object { "REFUSED: $_" }; Write-Host 'install refused: the existing tree holds something a non-admin may have planted'; exit 3 }

# 3. bin is rebuilt from nothing (a planted .config, DLL or file with an open handle never survives), then filled.
Remove-Item -LiteralPath $BinDir -Recurse -Force
$null = New-Item -ItemType Directory -Path $BinDir
foreach ($f in $Files) { Copy-Item -Force (Join-Path $src $f) (Join-Path $BinDir $f) }
Copy-Item -Force $launcherSrc (Join-Path $BinDir $LauncherName)
$manifest = [ordered]@{ installed_utc = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ'); bus_commit = (git -C $src rev-parse HEAD 2>$null); files = [ordered]@{} }
foreach ($k in $expectedBin.Keys | Sort-Object) { $manifest.files[$k] = $expectedBin[$k] }
$manifest | ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $BinDir 'manifest.json')
$expectedBin['manifest.json'] = (Get-FileHash -Algorithm SHA256 (Join-Path $BinDir 'manifest.json')).Hash.ToLowerInvariant()

# The publisher's receipts and logs live in the user's own folder (it runs NOT elevated). Nothing is ever copied
# FROM there by this elevated script: a user-made symlink there could otherwise land an admin-only file in data.
$null = New-Item -ItemType Directory -Force -Path $UserDir

# 4. Re-lock and re-verify everything, including that bin holds exactly the source's bytes.
Lock-Tree
$problems = @(Test-LockedTree $Root) + @(Test-InstallContents -BinDir $BinDir -DataDir $DataDir -Expected $expectedBin)
if ($problems) { $problems | ForEach-Object { "REFUSED: $_" }; Write-Host 'install refused after copy: the installed tree is not exactly the locked source'; exit 3 }

$user = [Security.Principal.WindowsIdentity]::GetCurrent().Name   # USERDOMAIN reads WORKGROUP in an ssh session
$settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -ExecutionTimeLimit ([TimeSpan]::Zero) -StartWhenAvailable `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -Hidden

# Sampler: runs as SYSTEM (it reads the CPU time of services and protected processes). Not as the logged-on
# user with Highest: that process inherits the user's environment, which any non-elevated process of the user
# can set (DOTNET_STARTUP_HOOKS, CORECLR_PROFILER_PATH load code into pwsh before the script runs). SYSTEM's
# environment is admin-only, and SYSTEM runs whether or not anyone is signed in.
$launcher = Join-Path $BinDir $LauncherName
$samplerArgs = "--stdout `"$DataDir\sampler.out.log`" --stderr `"$DataDir\sampler.err.log`" --label `"MachineLoad Sampler`" -- `"$Pwsh`" -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$BinDir\MachineLoadSampler.ps1`""
$samplerAction = New-ScheduledTaskAction -Execute $launcher -Argument $samplerArgs
$net = New-ScheduledTaskTrigger -Once -At (Get-Date).Date -RepetitionInterval (New-TimeSpan -Minutes 5)
$boot = New-ScheduledTaskTrigger -AtStartup
$samplerPrincipal = New-ScheduledTaskPrincipal -UserId 'S-1-5-18' -LogonType ServiceAccount -RunLevel Highest
Register-ScheduledTask -TaskPath $TaskPath -TaskName $SamplerTask -Action $samplerAction -Trigger @($boot, $net) `
    -Principal $samplerPrincipal -Settings $settings `
    -Description 'Fleet machine-load sampler (bus tools/machine/machine-load), as SYSTEM. One row per UTC minute to C:\ProgramData\MachineLoad\data. Diagnostic only.' -Force | Out-Null
$regTask = Get-ScheduledTask -TaskPath $TaskPath -TaskName $SamplerTask
if ($regTask.Principal.UserId -notin 'SYSTEM', 'S-1-5-18', 'NT AUTHORITY\SYSTEM') { Write-Host "install refused: sampler task principal is $($regTask.Principal.UserId), not SYSTEM"; exit 3 }
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
    # an entry written by an earlier build described an elevated logged-on-user task: correct it in place
    if ($reg -match 'one long-lived hidden sampler \(elevated, launched only') {
        $reg = $reg.Replace('one long-lived hidden sampler (elevated, launched only', 'one long-lived hidden sampler (as SYSTEM, launched only').Replace('logon start plus a 5-minute restart net', 'start at boot plus a 5-minute restart net')
        [IO.File]::WriteAllText($Registry, $reg)
    }
    if ($reg -notmatch [regex]::Escape('### \Fleet\MachineLoad Sampler')) {
        Add-Content -Path $Registry -Value @"

## machine-load (bus tools/machine/machine-load, owner request 2026-11-16)

### \Fleet\MachineLoad Sampler
- **owner:** fleet machine tooling (bus ``tools/machine/machine-load``); machine owner controls retirement
- **purpose:** one long-lived hidden sampler (as SYSTEM, launched only from ACL-locked C:\ProgramData\MachineLoad\bin) writing per-minute CPU, clock, memory, disk and per-project CPU rows to C:\ProgramData\MachineLoad\data.
- **cadence-rationale:** start at boot plus a 5-minute restart net; a running copy holds a mutex, so extra starts exit at once.
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
    if ($s -and $s.code -eq $expected -and (ConvertTo-Utc $s.written_utc) -gt $before -and (Get-Process -Id $s.pid -ErrorAction SilentlyContinue)) { $ok = $true; break }
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
