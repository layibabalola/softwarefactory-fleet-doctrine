<#
  Tests for Invoke-HeadlessTaskSweep.ps1.  pwsh -NoProfile -File tools/Invoke-HeadlessTaskSweep.tests.ps1 [-Live]

  Pure cases always run (any OS with PowerShell). -Live (Windows, interactive desktop) registers probe
  tasks under a throwaway task folder, briefly shows ONE visible console window on purpose (the stray
  window the sweep must hide), sweeps that folder only with a throwaway state dir, then removes it all.
#>
param([switch]$Live)
$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$sweep = Join-Path $here 'Invoke-HeadlessTaskSweep.ps1'
. $sweep

$script:fail = 0; $script:pass = 0
function Check([string]$Name, [bool]$Ok, [string]$Detail = '') {
    if ($Ok) { $script:pass++; Write-Output "ok    $Name" } else { $script:fail++; Write-Output "FAIL  $Name $Detail" }
}

# --- pure: classification -------------------------------------------------------------------------
$cases = @(
    @('pwsh.exe', '-File x.ps1', 'console'),
    @('"C:\Program Files\PowerShell\7\pwsh.exe"', '-NoProfile', 'console'),
    @('powershell', '-Command 1', 'console'),
    @('%SystemRoot%\System32\cmd.exe', '/c echo', 'console'),
    @('C:\Python\python.exe', 'x.py', 'console'),
    @('node', 'a.js', 'console'),
    @('C:\WINDOWS\System32\conhost.exe', '--headless pwsh.exe -File x', 'wrapped'),
    @('conhost.exe', 'pwsh.exe', 'console'),
    @('C:\ProgramData\Vendor\Update.cmd', '', 'batch'),
    @('"C:\a b\run.BAT"', 'x', 'batch'),
    @('wscript.exe', 'hidden.vbs', 'other'),
    @('pythonw.exe', 'x.pyw', 'other'),
    @('C:\SBP\sbp-launcher.exe', '--run x', 'other'),
    @('', '', 'other')
)
foreach ($c in $cases) {
    $v = Get-ConsoleActionVerdict $c[0] $c[1]
    Check "verdict [$($c[0])] = $($c[2])" ($v -eq $c[2]) "got $v"
}

# --- pure: rewrite keeps the program and every argument ---------------------------------------------
Check 'headless plain' ((Get-HeadlessArguments 'pwsh.exe' '-NoProfile -File "C:\x y\a.ps1"' 'console') -eq '--headless pwsh.exe -NoProfile -File "C:\x y\a.ps1"')
Check 'headless quotes a spaced path' ((Get-HeadlessArguments 'C:\Program Files\PowerShell\7\pwsh.exe' '-c 1' 'console') -eq '--headless "C:\Program Files\PowerShell\7\pwsh.exe" -c 1')
Check 'headless keeps existing quotes' ((Get-HeadlessArguments '"C:\Program Files\x.exe"' '' 'console') -eq '--headless "C:\Program Files\x.exe"')
Check 'headless batch' ((Get-HeadlessArguments 'C:\a b\run.cmd' 'one "two three"' 'batch') -eq '--headless "C:\a b\run.cmd" one "two three"')
Check 'headless batch no args' ((Get-HeadlessArguments 'C:\v\u.cmd' '' 'batch') -eq '--headless C:\v\u.cmd')

# --- pure: which argument strings conhost passes through unchanged -----------------------------------
foreach ($c in @(
        @('-NoProfile -EncodedCommand JABFAHIA', $true),
        @('-File "C:\x y\a.ps1" -Flag', $true),
        @('', $true),
        @('/d /s /c ""C:\a b\run.cmd" "arg 1""', $false),
        @('/c "ping x & rem "y z""', $false),
        @('-Arg="C:\x y"', $false),
        @('two  spaces', $false),
        @('-Path "C:\dir\"', $false),
        @('"unbalanced', $false),
        @('""', $false))) {
    Check "lossless [$($c[0])] = $($c[1])" ((Test-ConhostLossless $c[0]) -eq $c[1])
}
$enc = Get-HeadlessArguments 'cmd.exe' '/d /s /c ""C:\a b\run.cmd" "it''s 1""' 'console' 'C:\Program Files\PowerShell\7\pwsh.exe'
Check 'lossy args use the encoded wrapper' ($enc -like '--headless "C:\Program Files\PowerShell\7\pwsh.exe" -NoProfile -NonInteractive -ExecutionPolicy Bypass -EncodedCommand *')
$decoded = [Text.Encoding]::Unicode.GetString([Convert]::FromBase64String(($enc -split ' ')[-1]))
Check 'wrapper carries the raw argument string' ($decoded.Contains('ExpandEnvironmentVariables(''/d /s /c ""C:\a b\run.cmd" "it''''s 1""'')'))
Check 'wrapper base64 has nothing for conhost to re-quote' (Test-ConhostLossless ($enc.Substring('--headless '.Length).Replace('"C:\Program Files\PowerShell\7\pwsh.exe"', 'pwsh')))

# --- pure: command-line matching for stray windows ---------------------------------------------------
Check 'match task cmdline' (Test-CommandLineMatch '"pwsh.exe" -NoProfile -EncodedCommand AAA' 'pwsh.exe' '-NoProfile -EncodedCommand AAA')
Check 'match full path vs leaf' (Test-CommandLineMatch '"C:\Program Files\PowerShell\7\pwsh.exe" -File a.ps1' 'pwsh.exe' '-File a.ps1')
Check 'no match other args' (-not (Test-CommandLineMatch '"pwsh.exe" -File b.ps1' 'pwsh.exe' '-File a.ps1'))
Check 'no match other program' (-not (Test-CommandLineMatch 'node.exe -File a.ps1' 'pwsh.exe' '-File a.ps1'))
Check 'no match no-args task vs args process' (-not (Test-CommandLineMatch '"pwsh.exe" -NoExit' 'pwsh.exe' ''))
Check 'match no-args' (Test-CommandLineMatch '"pwsh.exe"' 'pwsh.exe' '')
Check 'match batch via cmd' (Test-CommandLineMatch 'C:\WINDOWS\system32\cmd.exe /c "C:\v\U.cmd" a' 'C:\v\U.cmd' 'a')
Check 'no match the headless child of conhost by lineage only' (Test-CommandLineMatch 'pwsh.exe -File a.ps1' 'pwsh.exe' '-File a.ps1')  # matched, but MainWindowHandle is zero, so never hidden

# --- pure: principals ---------------------------------------------------------------------------------
Check 'interactive principal' (Test-InteractivePrincipal ([pscustomobject]@{ LogonType = 'Interactive'; GroupId = $null }))
Check 'interactive-or-password principal' (Test-InteractivePrincipal ([pscustomobject]@{ LogonType = 'InteractiveOrPassword'; GroupId = $null }))
Check 'group principal' (Test-InteractivePrincipal ([pscustomobject]@{ LogonType = 'Group'; GroupId = 'Users' }))
Check 'S4U is not interactive' (-not (Test-InteractivePrincipal ([pscustomobject]@{ LogonType = 'S4U'; GroupId = $null })))
Check 'service account is not interactive' (-not (Test-InteractivePrincipal ([pscustomobject]@{ LogonType = 'ServiceAccount'; GroupId = $null })))

if (-not $Live) {
    Write-Output ("{0} passed, {1} failed (pure only; add -Live on a Windows desktop for the end-to-end probe)" -f $script:pass, $script:fail)
    if ($script:fail) { exit 1 } else { exit 0 }
}

# --- live: real tasks, real windows ------------------------------------------------------------------
$id = [guid]::NewGuid().ToString('N').Substring(0, 8)
$folder = "\FleetHygieneTest-$id\"
$work = Join-Path ([IO.Path]::GetTempPath()) "headless sweep test $id"   # a space on purpose
$state = Join-Path $work 'state'
New-Item -ItemType Directory -Force -Path $work | Out-Null
$shell = (Get-Command pwsh).Source
$me = [Security.Principal.WindowsIdentity]::GetCurrent().Name
$principal = New-ScheduledTaskPrincipal -UserId $me -LogonType Interactive -RunLevel Limited
$trigger = New-ScheduledTaskTrigger -Once -At ([DateTime]::Now.AddYears(5))
$conhost = Join-Path $env:SystemRoot 'System32\conhost.exe'
$strayTag = "stray-$id"
$freshMarker = Join-Path $work 'fresh.txt'
$batchMarker = Join-Path $work 'batch.txt'
$batch = Join-Path $work 'probe run.cmd'
Set-Content -LiteralPath $batch -Value ('@echo off' + "`r`n" + 'echo %~1> "' + $batchMarker + '"') -Encoding ASCII

function Reg($name, $exe, $arg, $desc = "probe $id") {
    $a = New-ScheduledTaskAction -Execute $exe -Argument $arg
    Register-ScheduledTask -TaskPath $folder -TaskName $name -Action $a -Trigger $trigger -Principal $principal -Description $desc -Force | Out-Null
}
function ActionOf($name) { (Get-ScheduledTask -TaskPath $folder -TaskName $name).Actions[0] }
function WaitFor([scriptblock]$Cond, [int]$Seconds) {
    $end = [DateTime]::UtcNow.AddSeconds($Seconds)
    while ([DateTime]::UtcNow -lt $end) { $r = & $Cond; if ($r) { return $r }; Start-Sleep -Milliseconds 500 }
    return $null
}
function ProcByTag($tag) { Get-CimInstance Win32_Process -Filter "Name='pwsh.exe'" | Where-Object { $_.CommandLine -like "*$tag*" } | Select-Object -First 1 }

try {
    Reg 'stray' $shell "-NoProfile -Command `"'$strayTag'; Start-Sleep 300`""
    Reg 'fresh' $shell "-NoProfile -Command `"Set-Content -LiteralPath '$freshMarker' -Value fresh-$id; Start-Sleep 20`""
    Reg 'wrapped' $conhost "--headless $shell -NoProfile -Command 1"
    Reg 'optout' $shell '-NoProfile -Command 1' 'needs its window: visible-console-ok'
    Reg 'batch' $batch "`"arg $id`""
    Reg 'nested' (Join-Path $env:SystemRoot 'System32\cmd.exe') "/d /s /c `"`"$batch`" `"nested $id`"`""
    $before = @{}; foreach ($n in 'stray', 'fresh', 'wrapped', 'optout', 'batch', 'nested') { $before[$n] = (ActionOf $n).Execute + '|' + (ActionOf $n).Arguments }

    # The pre-existing visible instance (what an unswept machine shows).
    Start-ScheduledTask -TaskPath $folder -TaskName 'stray'
    $stray = WaitFor { $p = ProcByTag $strayTag; if ($p -and (Get-Process -Id $p.ProcessId).MainWindowHandle -ne [IntPtr]::Zero) { $p } } 30
    Check 'live: unswept task shows a visible console window' ($null -ne $stray)

    $dry = & $shell -NoProfile -File $sweep -TaskPathFilter $folder -StateDir $state 2>&1 | Out-String
    Check 'live dry: reports stray' ($dry -match 'WOULD FIX\s+\\FleetHygieneTest-\w+\\stray')
    Check 'live dry: reports batch' ($dry -match 'WOULD FIX\s+\\FleetHygieneTest-\w+\\batch')
    Check 'live dry: skips wrapped' ($dry -notmatch '\\wrapped')
    Check 'live dry: honours opt-out' ($dry -match 'OPT-OUT\s+\\FleetHygieneTest-\w+\\optout')
    Check 'live dry: would hide the stray window' ($dry -match 'WOULD HIDE')
    $same = $true; foreach ($n in $before.Keys) { if (((ActionOf $n).Execute + '|' + (ActionOf $n).Arguments) -ne $before[$n]) { $same = $false } }
    Check 'live dry: changes nothing' $same
    if ($stray) { Check 'live dry: window still visible' ((Get-Process -Id $stray.ProcessId).MainWindowHandle -ne [IntPtr]::Zero) }

    $out = & $shell -NoProfile -File $sweep -TaskPathFilter $folder -StateDir $state -Apply 2>&1 | Out-String
    $exit = $LASTEXITCODE
    Check 'live apply: exit 0' ($exit -eq 0) "exit $exit`n$out"
    foreach ($n in 'stray', 'fresh', 'batch', 'nested') {
        $a = ActionOf $n
        Check "live apply: $n runs through conhost --headless" (($a.Execute -like '*\conhost.exe') -and ($a.Arguments -like '--headless *')) "$($a.Execute) $($a.Arguments)"
    }
    Check 'live apply: wrapped untouched' (((ActionOf 'wrapped').Execute + '|' + (ActionOf 'wrapped').Arguments) -eq $before['wrapped'])
    Check 'live apply: opt-out untouched' (((ActionOf 'optout').Execute + '|' + (ActionOf 'optout').Arguments) -eq $before['optout'])
    Check 'live apply: fresh keeps program and args' ((ActionOf 'fresh').Arguments -eq ('--headless ' + $(if ($shell -match '\s') { '"' + $shell + '"' } else { $shell }) + ' ' + $before['fresh'].Split('|', 2)[1]))
    $backups = @(Get-ChildItem -LiteralPath (Join-Path $state 'backups') -Filter '*.xml')
    Check 'live apply: one backup per rewritten task' ($backups.Count -eq 4) "got $($backups.Count)"
    Check 'live apply: nested-quote task uses the encoded wrapper' ((ActionOf 'nested').Arguments -like '*-EncodedCommand *')
    $xml = [xml](Get-Content -LiteralPath ($backups | Where-Object Name -like '*stray*' | Select-Object -First 1).FullName -Raw)
    Check 'live apply: backup holds the original action' ($xml.Task.Actions.Exec.Command -eq $shell)
    if ($stray) {
        $gp = Get-Process -Id $stray.ProcessId -ErrorAction SilentlyContinue
        Check 'live apply: stray instance still running (hidden, not killed)' ($null -ne $gp)
        Check 'live apply: stray window hidden' ($null -ne $gp -and $gp.MainWindowHandle -eq [IntPtr]::Zero)
    }
    $receipts = Get-Content -LiteralPath (Join-Path $state 'receipts.jsonl')
    Check 'live apply: receipts record rewrites and the hide' ((@($receipts | Where-Object { $_ -match '"action":"rewrote"' }).Count -eq 4) -and (@($receipts | Where-Object { $_ -match '"action":"hid_window"' }).Count -ge 1))

    # A rewritten task really runs, with no window.
    Start-ScheduledTask -TaskPath $folder -TaskName 'fresh'
    $fp = WaitFor { ProcByTag "fresh-$id" } 30
    Check 'live run: rewritten pwsh task starts' ($null -ne $fp)
    if ($fp) {
        Check 'live run: and has no visible window' ((Get-Process -Id $fp.ProcessId).MainWindowHandle -eq [IntPtr]::Zero)
        Check 'live run: and gets its argument string verbatim' ($fp.CommandLine.EndsWith($before['fresh'].Split('|', 2)[1])) $fp.CommandLine
    }
    Check 'live run: and does its work' ($null -ne (WaitFor { (Test-Path -LiteralPath $freshMarker) -and ((Get-Content -LiteralPath $freshMarker -Raw) -match "fresh-$id") } 30))
    Start-ScheduledTask -TaskPath $folder -TaskName 'batch'
    Check 'live run: rewritten batch task gets its quoted argument' ($null -ne (WaitFor { (Test-Path -LiteralPath $batchMarker) -and ((Get-Content -LiteralPath $batchMarker -Raw).Trim() -eq "arg $id") } 30))
    Remove-Item -LiteralPath $batchMarker -ErrorAction SilentlyContinue
    Start-ScheduledTask -TaskPath $folder -TaskName 'nested'
    Check 'live run: cmd /s /c with nested quotes survives the wrapper' ($null -ne (WaitFor { (Test-Path -LiteralPath $batchMarker) -and ((Get-Content -LiteralPath $batchMarker -Raw).Trim() -eq "nested $id") } 30))
    Check 'live run: the wrapped task reports success' ($null -ne (WaitFor { $i = Get-ScheduledTask -TaskPath $folder -TaskName 'nested' | Get-ScheduledTaskInfo; if ($i.LastTaskResult -eq 0) { $true } } 20))

    # Idempotent: a second pass finds nothing to do.
    $again = & $shell -NoProfile -File $sweep -TaskPathFilter $folder -StateDir $state -Apply 2>&1 | Out-String
    Check 'live: second pass is a no-op' ($again -match '0 offending' -or $again -match '1 offending, 0 rewritten') $again
} finally {
    foreach ($n in 'stray', 'fresh', 'wrapped', 'optout', 'batch', 'nested') {
        try { Stop-ScheduledTask -TaskPath $folder -TaskName $n -ErrorAction SilentlyContinue } catch { }
        try { Unregister-ScheduledTask -TaskPath $folder -TaskName $n -Confirm:$false -ErrorAction SilentlyContinue } catch { }
    }
    $p = ProcByTag $strayTag; if ($p) { Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue }
    try {
        $svc = New-Object -ComObject Schedule.Service; $svc.Connect()
        $svc.GetFolder('\').DeleteFolder($folder.Trim('\'), 0)
    } catch { }
    Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Output ("{0} passed, {1} failed" -f $script:pass, $script:fail)
if ($script:fail) { exit 1 } else { exit 0 }
