<#
.SYNOPSIS
  Machine-level sweep that stops scheduled tasks from popping visible console windows.

.DESCRIPTION
  An agent hook (Claude PreToolUse, a git hook, a lint) only sees the launches its own agent makes.
  A Codex lane, an installer, or a script written to a file and run later registers scheduled tasks
  the hook never sees. When such a task runs a console program (pwsh, powershell, cmd, python, node,
  ...) under an interactive logon, Windows gives it a visible console window: a blank, never-closing
  popup when the program is a watcher loop.

  This sweep runs from Task Scheduler itself, outside every agent, so it catches every registrant.
  For each enabled task that runs a console program under an interactive logon it:
    1. backs up the task XML,
    2. rewrites that action to  conhost.exe --headless <program> <same args>  (same program, same
       arguments, same working directory; only the window goes). conhost re-splits and re-quotes its
       client's command line, which changes what cmd.exe and batch files run when the arguments nest
       quotes, so those actions go through a quote-free -EncodedCommand wrapper that starts the
       program with the raw argument string (see Test-ConhostLossless),
    3. hides (never kills) any still-visible window of an instance started before the rewrite,
       matched by the task's original command line and Task Scheduler lineage.
  Default mode is a dry run that reports what -Apply would do.

  Skipped: tasks under \Microsoft\, non-interactive logons (S4U, Password, service accounts: they
  never show a window), actions already wrapped (conhost --headless, wscript, any GUI launcher),
  disabled tasks unless -IncludeDisabled, and any task whose Description contains the opt-out token
  visible-console-ok (the same token the Claude visible-console guard honours).

.EXAMPLE
  pwsh -NoProfile -File Invoke-HeadlessTaskSweep.ps1                 # dry run
  pwsh -NoProfile -File Invoke-HeadlessTaskSweep.ps1 -Apply          # rewrite + hide
  pwsh -NoProfile -File Invoke-HeadlessTaskSweep.ps1 -Install        # copy + register \FleetHygiene\HeadlessTaskSweep
  pwsh -NoProfile -File Invoke-HeadlessTaskSweep.ps1 -Status
  pwsh -NoProfile -File Invoke-HeadlessTaskSweep.ps1 -Uninstall

  Rollback of one rewrite: Register-ScheduledTask -Xml (Get-Content <backup.xml> -Raw) -TaskName <name> -TaskPath <path> -Force

  Runs on Windows PowerShell 5.1 and PowerShell 7.
#>
[CmdletBinding(DefaultParameterSetName = 'Sweep')]
param(
    [Parameter(ParameterSetName = 'Sweep')][switch]$Apply,
    [Parameter(ParameterSetName = 'Sweep')][switch]$IncludeDisabled,
    [Parameter(ParameterSetName = 'Sweep')][string]$TaskPathFilter,
    [Parameter(ParameterSetName = 'Install')][switch]$Install,
    [Parameter(ParameterSetName = 'Install')][ValidateRange(1, 1440)][int]$IntervalMinutes = 10,
    [Parameter(ParameterSetName = 'Uninstall')][switch]$Uninstall,
    [Parameter(ParameterSetName = 'Status')][switch]$Status,
    [string]$StateDir = (Join-Path $env:LOCALAPPDATA 'FleetHygiene\HeadlessTaskSweep')
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$script:OptOutToken = 'visible-console-ok'
$script:SweepTaskPath = '\FleetHygiene\'
$script:SweepTaskName = 'HeadlessTaskSweep'
$script:SignatureTtlDays = 7
$script:ReceiptsMaxBytes = 1MB
$script:RetryAfterSeconds = 86400

# Leaf names (lower case, .exe optional) that get a console window when started by Task Scheduler.
$script:ConsoleExes = @(
    'pwsh', 'powershell', 'cmd', 'python', 'python3', 'py', 'node', 'bash', 'sh', 'wsl',
    'cscript', 'ruby', 'perl', 'deno', 'bun', 'uv', 'codex', 'claude', 'git', 'npm', 'npx'
)
$script:BatchExtensions = @('.cmd', '.bat')

function Get-ExecutableLeaf {
    param([string]$Execute)
    $exe = ([string]$Execute).Trim().Trim('"')
    $exe = [Environment]::ExpandEnvironmentVariables($exe)
    return [IO.Path]::GetFileName($exe).ToLowerInvariant()
}

function Get-ConsoleActionVerdict {
    <# Pure: classify one Exec action. Returns 'console', 'batch', 'wrapped' or 'other'. #>
    param([string]$Execute, [string]$Arguments)
    $leaf = Get-ExecutableLeaf $Execute
    if (-not $leaf) { return 'other' }
    $stem = $leaf
    if ($stem.EndsWith('.exe')) { $stem = $stem.Substring(0, $stem.Length - 4) }
    if ($stem -eq 'conhost') {
        if (([string]$Arguments).TrimStart() -match '^--headless(\s|$)') { return 'wrapped' }
        return 'console'
    }
    if ($script:ConsoleExes -contains $stem) { return 'console' }
    $ext = [IO.Path]::GetExtension($leaf)
    if ($script:BatchExtensions -contains $ext) { return 'batch' }
    return 'other'
}

function Test-ConhostLossless {
    <#
      Pure: does an argument string survive conhost --headless unchanged?
      conhost does NOT pass its client's command line through verbatim: it splits it into argv and
      re-joins it, quoting each argument that holds a space and escaping embedded quotes as \".
      Measured 2026-10-24 on Windows 10 19045:  cmd.exe /d /s /c "ping ... rem tag "x y" ""z"""
      reached the child as  cmd.exe /d /s /c "ping ... rem tag x" "y \"z\"".  Programs that read the
      raw line (cmd.exe, batch files) then run something else. So rewrite directly only when the
      split-and-rejoin is the identity; otherwise use the encoded wrapper.
    #>
    param([string]$Arguments)
    $s = ([string]$Arguments).Trim()
    if (-not $s) { return $true }
    if ($s.Contains('\"') -or $s.Contains('""') -or $s.Contains("`t")) { return $false }
    $tokens = New-Object System.Collections.Generic.List[string]
    $cur = New-Object System.Text.StringBuilder
    $inQuote = $false; $has = $false
    foreach ($ch in $s.ToCharArray()) {
        if ($ch -eq '"') { $inQuote = -not $inQuote; $has = $true; continue }
        if ($ch -eq ' ' -and -not $inQuote) {
            if ($has) { $tokens.Add($cur.ToString()); [void]$cur.Clear(); $has = $false }
            continue
        }
        [void]$cur.Append($ch); $has = $true
    }
    if ($inQuote) { return $false }
    if ($has) { $tokens.Add($cur.ToString()) }
    $rebuilt = ($tokens | ForEach-Object { if ($_ -eq '' -or $_.Contains(' ')) { '"' + $_ + '"' } else { $_ } }) -join ' '
    return ($rebuilt -ceq $s)
}

function Get-WrapperScript {
    <# Pure: a PowerShell script that starts Execute with the raw Arguments string (no re-quoting) and returns its exit code. #>
    param([string]$Execute, [string]$Arguments)
    $e = ([string]$Execute).Trim().Trim('"').Replace("'", "''")
    $a = ([string]$Arguments).Replace("'", "''")
    return @"
# fleet-headless-wrapper v1: Task Scheduler expands %VARS% in an action; this does the same for the embedded ones.
`$psi = New-Object System.Diagnostics.ProcessStartInfo
`$psi.FileName = [Environment]::ExpandEnvironmentVariables('$e')
`$psi.Arguments = [Environment]::ExpandEnvironmentVariables('$a')
`$psi.UseShellExecute = `$false
`$p = [System.Diagnostics.Process]::Start(`$psi)
`$p.WaitForExit()
exit `$p.ExitCode
"@
}

function Get-HeadlessArguments {
    <#
      Pure: the conhost.exe argument string that runs the same program with the same arguments.
      Lossless arguments: --headless <program> <args>.  Otherwise: --headless <shell> -EncodedCommand
      <wrapper>, whose base64 has no quotes or spaces for conhost to rewrite.
    #>
    param([string]$Execute, [string]$Arguments, [string]$Verdict, [string]$Shell = 'powershell.exe')
    $exe = ([string]$Execute).Trim()
    $args0 = ([string]$Arguments).Trim()
    if (-not (Test-ConhostLossless $args0)) {
        $b64 = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes((Get-WrapperScript $exe $args0)))
        $sh = $Shell
        if ($sh -match '\s' -and -not $sh.StartsWith('"')) { $sh = '"' + $sh + '"' }
        return '--headless ' + $sh + ' -NoProfile -NonInteractive -ExecutionPolicy Bypass -EncodedCommand ' + $b64
    }
    $quoted = $exe
    if (-not $exe.StartsWith('"') -and $exe -match '\s') { $quoted = '"' + $exe + '"' }
    if ($args0) { return '--headless ' + $quoted + ' ' + $args0 }
    return '--headless ' + $quoted
}

function Get-WrapperShell {
    $c = Get-Command pwsh -ErrorAction SilentlyContinue
    if ($c) { return $c.Source }
    return (Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe')
}

function Test-InteractivePrincipal {
    param($Principal)
    if ($null -eq $Principal) { return $false }
    if ($Principal.GroupId) { return $true }   # group principals run in each member's session
    $lt = [string]$Principal.LogonType
    return ($lt -eq 'Interactive' -or $lt -eq 'InteractiveOrPassword')
}

function Get-TaskFullName { param($Task) return ($Task.TaskPath + $Task.TaskName) }

function Write-Receipt {
    param([hashtable]$Record)
    if (-not (Test-Path -LiteralPath $StateDir)) { New-Item -ItemType Directory -Force -Path $StateDir | Out-Null }
    $path = Join-Path $StateDir 'receipts.jsonl'
    $Record['ts'] = [DateTime]::UtcNow.ToString('o')
    $Record['pid'] = $PID
    $line = ($Record | ConvertTo-Json -Compress -Depth 4)
    Add-Content -LiteralPath $path -Value $line -Encoding UTF8
    $fi = Get-Item -LiteralPath $path
    if ($fi.Length -gt $script:ReceiptsMaxBytes) {
        $keep = Get-Content -LiteralPath $path -Tail 2000
        Set-Content -LiteralPath $path -Value $keep -Encoding UTF8
    }
}

function Read-Signatures {
    $path = Join-Path $StateDir 'signatures.json'
    if (-not (Test-Path -LiteralPath $path)) { return @() }
    try {
        $raw = Get-Content -LiteralPath $path -Raw
        if (-not $raw) { return @() }
        # Times are Unix seconds: pwsh 7's ConvertFrom-Json turns ISO strings into DateTime and can shift the zone.
        $cut = [DateTimeOffset]::UtcNow.AddDays(-$script:SignatureTtlDays).ToUnixTimeSeconds()
        return @(($raw | ConvertFrom-Json) | Where-Object { [long]$_.at -gt $cut })
    } catch { return @() }
}

function Save-Signatures {
    param([object[]]$Signatures)
    if (-not (Test-Path -LiteralPath $StateDir)) { New-Item -ItemType Directory -Force -Path $StateDir | Out-Null }
    $path = Join-Path $StateDir 'signatures.json'
    $json = ConvertTo-Json -InputObject @($Signatures) -Depth 4
    Set-Content -LiteralPath $path -Value $json -Encoding UTF8
}

function Read-Failures {
    <# task full name -> Unix seconds of its last failed rewrite (a task we may not write is retried daily, not every pass). #>
    $map = @{}
    $path = Join-Path $StateDir 'failures.json'
    if (-not (Test-Path -LiteralPath $path)) { return $map }
    try {
        $obj = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
        foreach ($p in $obj.PSObject.Properties) { $map[$p.Name] = [long]$p.Value }
    } catch { }
    return $map
}

function Save-Failures {
    param([hashtable]$Map)
    if (-not (Test-Path -LiteralPath $StateDir)) { New-Item -ItemType Directory -Force -Path $StateDir | Out-Null }
    Set-Content -LiteralPath (Join-Path $StateDir 'failures.json') -Value (ConvertTo-Json -InputObject $Map) -Encoding UTF8
}

function Get-OffendingActions {
    <# Returns one record per console action that would show a window. #>
    param([object[]]$Tasks)
    foreach ($t in $Tasks) {
        if ($t.TaskPath -like '\Microsoft\*') { continue }
        $full = Get-TaskFullName $t
        if ($t.TaskPath -eq $script:SweepTaskPath -and $t.TaskName -eq $script:SweepTaskName) { continue }
        if (-not $IncludeDisabled -and [string]$t.State -eq 'Disabled') { continue }
        if (-not (Test-InteractivePrincipal $t.Principal)) { continue }
        $optedOut = ([string]$t.Description).Contains($script:OptOutToken)
        $i = 0
        foreach ($a in @($t.Actions)) {
            $i++
            if ($a.CimClass.CimClassName -ne 'MSFT_TaskExecAction') { continue }
            $verdict = Get-ConsoleActionVerdict $a.Execute $a.Arguments
            if ($verdict -ne 'console' -and $verdict -ne 'batch') { continue }
            [pscustomobject]@{
                Task = $t; FullName = $full; Index = $i; Execute = [string]$a.Execute
                Arguments = [string]$a.Arguments; WorkingDirectory = [string]$a.WorkingDirectory
                Verdict = $verdict; OptedOut = $optedOut
            }
        }
    }
}

function Get-SafeFileName { param([string]$Name) return (($Name.Trim('\') -replace '[\\/:*?"<>|\s]', '_')) }

function Invoke-Rewrite {
    param($Task, [object[]]$Offenders)
    $full = Get-TaskFullName $Task
    $backupDir = Join-Path $StateDir 'backups'
    if (-not (Test-Path -LiteralPath $backupDir)) { New-Item -ItemType Directory -Force -Path $backupDir | Out-Null }
    $backup = Join-Path $backupDir ((Get-SafeFileName $full) + '.' + [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ') + '.xml')
    Export-ScheduledTask -TaskName $Task.TaskName -TaskPath $Task.TaskPath | Set-Content -LiteralPath $backup -Encoding Unicode
    $conhost = Join-Path $env:SystemRoot 'System32\conhost.exe'
    $newActions = @()
    $i = 0
    foreach ($a in @($Task.Actions)) {
        $i++
        $hit = $Offenders | Where-Object { $_.Index -eq $i } | Select-Object -First 1
        if ($null -eq $hit) {
            $newActions += $a
            continue
        }
        $argText = Get-HeadlessArguments $hit.Execute $hit.Arguments $hit.Verdict (Get-WrapperShell)
        if ($argText.Length -gt 30000) { throw "rewritten argument is $($argText.Length) chars, over the 32 KB action limit; left unchanged" }
        if ($hit.WorkingDirectory) {
            $newActions += New-ScheduledTaskAction -Execute $conhost -Argument $argText -WorkingDirectory $hit.WorkingDirectory
        } else {
            $newActions += New-ScheduledTaskAction -Execute $conhost -Argument $argText
        }
    }
    try {
        Set-ScheduledTask -TaskName $Task.TaskName -TaskPath $Task.TaskPath -Action $newActions | Out-Null
    } catch {
        Remove-Item -LiteralPath $backup -ErrorAction SilentlyContinue   # nothing changed, so no backup to keep
        throw
    }
    return $backup
}

function Get-ScheduleServicePid {
    try { return [int](Get-CimInstance Win32_Service -Filter "Name='Schedule'").ProcessId } catch { return 0 }
}

function Test-CommandLineMatch {
    <# Pure: does a process command line belong to a task action with this Execute/Arguments? #>
    param([string]$CommandLine, [string]$Execute, [string]$Arguments)
    if (-not $CommandLine) { return $false }
    $cl = $CommandLine.Trim()
    $leaf = Get-ExecutableLeaf $Execute
    $args0 = ([string]$Arguments).Trim()
    $head = ($cl -replace '^"([^"]*)".*$', '$1')
    if ($head -eq $cl) { $head = ($cl -split '\s+', 2)[0] }
    $headLeaf = [IO.Path]::GetFileName($head).ToLowerInvariant()
    $leafStem = $leaf -replace '\.exe$', ''
    $headStem = $headLeaf -replace '\.exe$', ''
    if ($headStem -eq 'cmd' -and $script:BatchExtensions -contains [IO.Path]::GetExtension($leaf)) {
        # Task Scheduler starts a batch action as: cmd.exe /c "<path>" <args>
        if (-not $cl.ToLowerInvariant().Contains($leaf)) { return $false }
        if (-not $args0) { return $true }
        return $cl.EndsWith($args0)
    }
    if ($headStem -ne $leafStem) { return $false }
    if (-not $args0) { return ($cl -replace '^("[^"]*"|\S+)\s*', '') -eq '' }
    return $cl.EndsWith($args0)
}

function Hide-StrayWindows {
    <# Hides (never kills) visible windows of task instances started before their task was rewritten. #>
    param([object[]]$Signatures, [switch]$DryRun)
    if (@($Signatures).Count -eq 0) { return }
    $schedPid = Get-ScheduleServicePid
    if ($schedPid -le 0) { return }
    $procs = @(Get-CimInstance Win32_Process -Property ProcessId, ParentProcessId, CommandLine, Name)
    $byPid = @{}
    foreach ($p in $procs) { $byPid[[int]$p.ProcessId] = $p }
    $typeLoaded = $false
    foreach ($p in $procs) {
        if (-not $p.CommandLine) { continue }
        $sig = $Signatures | Where-Object { Test-CommandLineMatch $p.CommandLine $_.execute $_.arguments } | Select-Object -First 1
        if ($null -eq $sig) { continue }
        # Lineage: the instance (or its cmd wrapper) must descend from the Task Scheduler service.
        $cur = $p; $fromScheduler = $false
        for ($d = 0; $d -lt 4 -and $null -ne $cur; $d++) {
            if ([int]$cur.ParentProcessId -eq $schedPid) { $fromScheduler = $true; break }
            $cur = $byPid[[int]$cur.ParentProcessId]
        }
        if (-not $fromScheduler) { continue }
        $gp = Get-Process -Id ([int]$p.ProcessId) -ErrorAction SilentlyContinue
        if ($null -eq $gp -or $gp.MainWindowHandle -eq [IntPtr]::Zero) { continue }
        if ($DryRun) {
            Write-Receipt @{ action = 'would_hide_window'; task = $sig.task; target_pid = [int]$p.ProcessId }
            Write-Output ("WOULD HIDE  pid {0}  ({1})" -f $p.ProcessId, $sig.task)
            continue
        }
        if (-not $typeLoaded) {
            if (-not ('FleetHygiene.Win32' -as [type])) {
                Add-Type -Namespace FleetHygiene -Name Win32 -MemberDefinition '[DllImport("user32.dll")] public static extern bool ShowWindow(System.IntPtr hWnd, int nCmdShow);'
            }
            $typeLoaded = $true
        }
        $ok = [FleetHygiene.Win32]::ShowWindow($gp.MainWindowHandle, 0)
        Write-Receipt @{ action = 'hid_window'; task = $sig.task; target_pid = [int]$p.ProcessId; ok = [bool]$ok }
        Write-Output ("HID         pid {0}  ({1})" -f $p.ProcessId, $sig.task)
    }
}

function Invoke-Sweep {
    $tasks = @(Get-ScheduledTask)
    if ($TaskPathFilter) { $tasks = @($tasks | Where-Object { $_.TaskPath -like ($TaskPathFilter.TrimEnd('\') + '\*') }) }
    $offenders = @(Get-OffendingActions $tasks)
    $signatures = @(Read-Signatures)
    $failures = Read-Failures
    $now = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
    $rewrote = 0; $failed = 0; $optout = 0; $deferred = 0; $needElevation = $false
    foreach ($group in ($offenders | Group-Object FullName)) {
        $items = @($group.Group)
        $task = $items[0].Task
        if ($items[0].OptedOut) {
            $optout++
            Write-Output ("OPT-OUT     {0}" -f $group.Name)
            continue
        }
        foreach ($it in $items) {
            $signatures += [pscustomobject]@{
                task = $group.Name; execute = $it.Execute; arguments = $it.Arguments
                at = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
            }
        }
        if ($Apply -and $failures.ContainsKey($group.Name) -and ($now - [long]$failures[$group.Name]) -lt $script:RetryAfterSeconds) {
            $deferred++
            continue
        }
        if (-not $Apply) {
            Write-Receipt @{ action = 'would_rewrite'; task = $group.Name; executes = @($items | ForEach-Object { $_.Execute }) }
            Write-Output ("WOULD FIX   {0}  [{1}]" -f $group.Name, (($items | ForEach-Object { $_.Execute }) -join ', '))
            continue
        }
        try {
            $backup = Invoke-Rewrite $task $items
            $rewrote++
            $failures.Remove($group.Name)
            Write-Receipt @{ action = 'rewrote'; task = $group.Name; executes = @($items | ForEach-Object { $_.Execute }); backup = $backup }
            Write-Output ("FIXED       {0}  (backup {1})" -f $group.Name, $backup)
        } catch {
            $failed++
            $failures[$group.Name] = $now
            $msg = $_.Exception.Message.Trim()
            # A task registered from an elevated shell denies writes to a filtered (non-elevated) token, even the same user's.
            $elev = ($msg -match 'Access is denied' -and -not (Test-Elevated))
            Write-Receipt @{ action = 'rewrite_failed'; task = $group.Name; error = $msg; needs_elevation = $elev }
            Write-Output ("FAILED      {0}  {1}" -f $group.Name, $msg)
            if ($elev) { $needElevation = $true }
        }
    }
    # Dedupe by task + command, newest wins.
    $seen = @{}; $kept = @()
    foreach ($s in ($signatures | Sort-Object at -Descending)) {
        $k = $s.task + '|' + $s.execute + '|' + $s.arguments
        if ($seen.ContainsKey($k)) { continue }
        $seen[$k] = $true; $kept += $s
    }
    if ($Apply) { Save-Signatures $kept; Save-Failures $failures }
    Hide-StrayWindows -Signatures $kept -DryRun:(-not $Apply)
    $mode = 'dry-run'; if ($Apply) { $mode = 'apply' }
    $nOff = @($offenders | Group-Object FullName).Count
    Write-Receipt @{ action = 'sweep'; mode = $mode; scanned = $tasks.Count; offenders = $nOff; rewrote = $rewrote; failed = $failed; deferred = $deferred; opted_out = $optout }
    Write-Output ("SWEEP {0}: scanned {1} tasks, {2} offending, {3} rewritten, {4} failed, {5} deferred after an earlier failure, {6} opted out" -f $mode, $tasks.Count, $nOff, $rewrote, $failed, $deferred, $optout)
    if ($needElevation) {
        Write-Output 'HINT: tasks registered from an elevated shell can only be rewritten elevated. Run -Install once from an elevated shell; the sweep then runs at the highest run level. Until then their stray windows are still hidden (when they run non-elevated).'
    }
    if ($failed -gt 0) { exit 1 }
}

function Test-Elevated {
    $p = New-Object Security.Principal.WindowsPrincipal ([Security.Principal.WindowsIdentity]::GetCurrent())
    return $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Invoke-Install {
    if (-not (Test-Path -LiteralPath $StateDir)) { New-Item -ItemType Directory -Force -Path $StateDir | Out-Null }
    $dest = Join-Path $StateDir 'Invoke-HeadlessTaskSweep.ps1'
    $src = (Resolve-Path -LiteralPath $PSCommandPath).Path
    if ($src -ne $dest) { Copy-Item -LiteralPath $src -Destination $dest -Force }
    $hash = (Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLowerInvariant()
    $commit = ''
    try { $commit = (& git -C (Split-Path $src) log -1 --format=%H -- (Split-Path $src -Leaf) 2>$null) } catch { }
    $shell = Get-WrapperShell
    $conhost = Join-Path $env:SystemRoot 'System32\conhost.exe'
    $arg = '--headless "' + $shell + '" -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "' + $dest + '" -Apply'
    $action = New-ScheduledTaskAction -Execute $conhost -Argument $arg
    $repeat = New-ScheduledTaskTrigger -Once -At ([DateTime]::Now.AddMinutes(1)) -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes)
    $logon = New-ScheduledTaskTrigger -AtLogOn -User ([Security.Principal.WindowsIdentity]::GetCurrent().Name)
    # Elevated install -> Highest, so the sweep may also rewrite tasks that were registered elevated.
    $runLevel = 'Limited'; if (Test-Elevated) { $runLevel = 'Highest' }
    $principal = New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel $runLevel
    $settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 5) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    $desc = 'Fleet hygiene: rewrites interactive console scheduled tasks to conhost --headless and hides their stray windows. ' +
        'Source: softwarefactory-fleet-doctrine tools/Invoke-HeadlessTaskSweep.ps1 commit ' + $commit + ' sha256 ' + $hash +
        '. Opt a task out by putting ' + $script:OptOutToken + ' in its Description.'
    # A (re)install may change the run level, so retry every earlier failure on the next pass.
    Remove-Item -LiteralPath (Join-Path $StateDir 'failures.json') -ErrorAction SilentlyContinue
    Register-ScheduledTask -TaskName $script:SweepTaskName -TaskPath $script:SweepTaskPath -Action $action -Trigger @($repeat, $logon) -Principal $principal -Settings $settings -Description $desc -Force | Out-Null
    $info = [ordered]@{ installed_at = [DateTime]::UtcNow.ToString('o'); source = $src; source_commit = $commit; sha256 = $hash; interval_minutes = $IntervalMinutes; shell = $shell; run_level = $runLevel }
    Set-Content -LiteralPath (Join-Path $StateDir 'install.json') -Value ($info | ConvertTo-Json) -Encoding UTF8
    Write-Receipt @{ action = 'installed'; sha256 = $hash; source_commit = $commit; interval_minutes = $IntervalMinutes }
    Write-Output ("INSTALLED {0}{1} every {2} min + at logon, run level {3}; script {4} sha256 {5}" -f $script:SweepTaskPath, $script:SweepTaskName, $IntervalMinutes, $runLevel, $dest, $hash)
    if ($runLevel -eq 'Limited') { Write-Output 'NOTE: installed non-elevated; tasks registered elevated cannot be rewritten. Re-run -Install from an elevated shell to cover them.' }
}

function Invoke-Uninstall {
    $t = Get-ScheduledTask -TaskName $script:SweepTaskName -TaskPath $script:SweepTaskPath -ErrorAction SilentlyContinue
    if ($t) { Unregister-ScheduledTask -TaskName $script:SweepTaskName -TaskPath $script:SweepTaskPath -Confirm:$false }
    Write-Receipt @{ action = 'uninstalled' }
    Write-Output 'UNINSTALLED (backups, receipts and signatures kept under the state dir)'
}

function Show-Status {
    $t = Get-ScheduledTask -TaskName $script:SweepTaskName -TaskPath $script:SweepTaskPath -ErrorAction SilentlyContinue
    if (-not $t) { Write-Output 'NOT INSTALLED'; exit 2 }
    $i = $t | Get-ScheduledTaskInfo
    Write-Output ("task {0}{1}: state={2} run_level={3} last_run={4} last_result=0x{5:X} next_run={6}" -f $t.TaskPath, $t.TaskName, $t.State, $t.Principal.RunLevel, $i.LastRunTime, $i.LastTaskResult, $i.NextRunTime)
    $inst = Join-Path $StateDir 'install.json'
    $dest = Join-Path $StateDir 'Invoke-HeadlessTaskSweep.ps1'
    if ((Test-Path -LiteralPath $inst) -and (Test-Path -LiteralPath $dest)) {
        $want = (Get-Content -LiteralPath $inst -Raw | ConvertFrom-Json).sha256
        $have = (Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLowerInvariant()
        $integrity = 'MISMATCH'; if ($want -eq $have) { $integrity = 'ok' }
        Write-Output ("script integrity: {0} (sha256 {1})" -f $integrity, $have)
    }
    $r = Join-Path $StateDir 'receipts.jsonl'
    if (Test-Path -LiteralPath $r) {
        $lines = @(Get-Content -LiteralPath $r)
        $sweeps = @($lines | Where-Object { $_ -match '"action":"sweep"' })
        if ($sweeps.Count -gt 0) {
            # Read ts from the raw line: ConvertFrom-Json would turn it into a zone-shifted DateTime.
            $ts = [regex]::Match($sweeps[-1], '"ts":"([^"]+)"').Groups[1].Value
            $age = ([DateTimeOffset]::UtcNow - [DateTimeOffset]::Parse($ts, [Globalization.CultureInfo]::InvariantCulture)).TotalMinutes
            $verdict = 'LIVE'; if ($age -gt (3 * $IntervalMinutes)) { $verdict = 'STALE' }
            Write-Output ("last sweep {0:N1} min ago ({1}): {2}" -f $age, $verdict, $sweeps[-1])
        } else { Write-Output 'no sweep receipt yet' }
        Write-Output 'recent non-sweep receipts:'
        $lines | Where-Object { $_ -notmatch '"action":"sweep"' } | Select-Object -Last 8 | ForEach-Object { Write-Output ('  ' + $_) }
    }
}

# Dot-sourcing (tests) loads the functions only.
if ($MyInvocation.InvocationName -eq '.') { return }

switch ($PSCmdlet.ParameterSetName) {
    'Install' { Invoke-Install }
    'Uninstall' { Invoke-Uninstall }
    'Status' { Show-Status }
    default { Invoke-Sweep }
}
