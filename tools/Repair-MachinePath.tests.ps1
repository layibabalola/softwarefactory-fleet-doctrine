# Behavioural tests for tools/Repair-MachinePath.ps1 and tools/Get-FleetPathHealthStatus.ps1.
# No Pester, no elevation. Every PATH is an injected string, and "does this folder exist" is an
# injected predicate, so the real User/Machine PATH, registry, runners and bus are never touched.
#   pwsh -NoProfile -File tools/Repair-MachinePath.tests.ps1      exit 0 pass, 1 fail
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot 'Repair-MachinePath.ps1') -Library
. (Join-Path $PSScriptRoot 'Get-FleetPathHealthStatus.ps1') -Library

$script:pass = 0; $script:fail = 0
function Ok([bool]$cond, [string]$name) {
    if ($cond) { $script:pass++ } else { $script:fail++; Write-Output "FAIL: $name" }
}

# Guard: if the tests ever wrote the real User PATH, this catches it (read-only comparison).
$realUserBefore = if ($IsWindows) { [Environment]::GetEnvironmentVariable('Path', 'User') } else { $null }

# A fake filesystem: only these folders exist (keys compared case-insensitively).
$fs = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
foreach ($p in @('C:\', 'D:\', 'C:\Windows\System32', 'C:\Windows', 'C:\Program Files\Git\cmd', 'C:\Program Files\nodejs',
        'C:\Users\u\AppData\Roaming\npm', 'C:\Users\u\.dotnet\tools', 'C:\Go\bin', 'C:\Users\u\bin')) { [void]$fs.Add($p) }
$fsExists = { param($p) $fs.Contains($p.TrimEnd('\')) -or $fs.Contains($p) }
$expand = { param($t) $t.Replace('%USERPROFILE%', 'C:\Users\u').Replace('%SystemRoot%', 'C:\Windows') }

# --- 1. classification ---------------------------------------------------------------------------
$machineRaw = '%SystemRoot%\system32;%SystemRoot%;C:\Program Files\Git\cmd;C:\Gone\Machine\bin'
$mA = Get-PathAnalysis -Raw $machineRaw -Scope Machine -Exists $fsExists -Expand $expand
Ok ($mA.Count -eq 4) 'machine: four segments'
Ok (($mA | Where-Object Class -eq 'dead').Count -eq 1) 'machine: one dead entry'
Ok (@($mA | Where-Object Removable).Count -eq 1 -and @($mA | Where-Object Removable)[0].Raw -eq 'C:\Gone\Machine\bin') 'machine: only the dead entry is removable'

$mDup = Get-PathAnalysis -Raw 'C:\Windows;C:\Windows\' -Scope Machine -Exists $fsExists -Expand $expand
Ok (($mDup | Where-Object Class -eq 'duplicate').Count -eq 1) 'machine: duplicate detected (trailing slash normalised)'
Ok (@($mDup | Where-Object Removable).Count -eq 0) 'machine: duplicates are reported, never removed'

$mKeys = @($mA | Where-Object Key | ForEach-Object Key)
$userRaw = @(
    '%USERPROFILE%\AppData\Roaming\npm'
    'C:\Users\u\.dotnet\tools'
    'D:\ContextUltraWindowsGate\run1-1\cli-home\.dotnet\tools'
    ''
    'c:\users\u\appdata\roaming\npm\'
    'C:\Program Files\Git\cmd'
    '\\fileserver\share\bin'
    '%NOT_DEFINED_VAR%\bin'
    'Q:\removable\bin'
    'C:\Go\bin'
) -join ';'
$uA = Get-PathAnalysis -Raw $userRaw -Scope User -Exists $fsExists -Expand $expand -OtherScopeKeys $mKeys
$cls = @($uA | ForEach-Object Class)
Ok ($cls[0] -eq 'ok') 'user: %USERPROFILE% entry that exists is ok'
Ok ($cls[1] -eq 'ok') 'user: live .dotnet\tools is ok'
Ok ($cls[2] -eq 'dead' -and $uA[2].DotnetTools) 'user: dead per-run .dotnet\tools is dead and flagged dotnet'
Ok ($cls[3] -eq 'empty') 'user: empty segment'
Ok ($cls[4] -eq 'duplicate-var' -and -not $uA[4].Removable) 'user: a literal repeat of an earlier %VAR% entry is reported, not removed'
Ok ($cls[5] -eq 'cross-duplicate') 'user: repeats a Machine entry'
Ok ($cls[6] -eq 'unc') 'user: UNC entry is unverifiable'
Ok ($cls[7] -eq 'unresolved') 'user: unexpanded %VAR% is unverifiable'
Ok ($cls[8] -eq 'drive-absent') 'user: entry on an unmounted drive is unverifiable'
Ok ($cls[9] -eq 'ok') 'user: plain existing entry'
Ok (-not ($uA | Where-Object { $_.Class -in @('ok', 'unc', 'unresolved', 'drive-absent') -and $_.Removable })) 'user: no live or unverifiable entry is removable'

# --- 2. repair ------------------------------------------------------------------------------------
$repaired = Get-RepairedPath $uA
Ok ($repaired -eq (@('%USERPROFILE%\AppData\Roaming\npm', 'C:\Users\u\.dotnet\tools', 'c:\users\u\appdata\roaming\npm\', '\\fileserver\share\bin', '%NOT_DEFINED_VAR%\bin', 'Q:\removable\bin', 'C:\Go\bin') -join ';')) 'repair: keeps order and raw %VAR% text, drops dead/empty/duplicate/cross-duplicate'
$again = Get-PathAnalysis -Raw $repaired -Scope User -Exists $fsExists -Expand $expand -OtherScopeKeys $mKeys
Ok (@($again | Where-Object Removable).Count -eq 0) 'repair: idempotent (second pass removes nothing)'
Ok ((Get-RepairedPath $mA) -eq '%SystemRoot%\system32;%SystemRoot%;C:\Program Files\Git\cmd') 'repair: machine loses only its dead entry'
Ok ((Get-RepairedPath (Get-PathAnalysis -Raw '' -Scope User -Exists $fsExists)) -eq '') 'repair: empty PATH stays empty'

# --- 3. the ULTRA-MAGNUS shape: 95 entries, 85 dead per-run dotnet tool dirs ----------------------
$live = @('C:\Users\u\AppData\Roaming\npm', 'C:\Users\u\.dotnet\tools', 'C:\Go\bin', 'C:\Program Files\nodejs', 'C:\Users\u\bin')
$deadGate = 1..80 | ForEach-Object { "D:\ContextUltraWindowsGate\20261101-$_-1\cli-home\.dotnet\tools" }
$deadWt = 1..4 | ForEach-Object { "C:\ContextUltraWorktrees\v-$_\ps-setup-cleanup-$_\cu-setup-cleanup-admission-$_\dotnet-home\.dotnet\tools" }
$deadDng = @('C:\DngAutoJobs\evidence\x\dotnet-cli\.dotnet\tools')
$dups = @('C:\Go\bin', 'C:\Users\u\bin', 'C:\Program Files\nodejs', 'C:\Users\u\AppData\Roaming\npm', 'C:\Users\u\.dotnet\tools')
$um = (@($live) + $deadGate + $deadWt + $deadDng + $dups) -join ';'
$umA = Get-PathAnalysis -Raw $um -Scope User -Exists $fsExists -Expand $expand
$st = Get-ScopeStats $umA $um (Join-ExpandedPath $umA)
Ok ($st.segments -eq 95) 'ultra-magnus fixture: 95 segments'
Ok ($st.dead -eq 85 -and $st.dead_dotnet_tools -eq 85) 'ultra-magnus fixture: 85 dead, all .dotnet\tools'
Ok ($st.duplicates -eq 5) 'ultra-magnus fixture: 5 duplicates'
$umFixed = Get-RepairedPath $umA
Ok ((Split-PathList $umFixed).Count -eq 5 -and $umFixed -eq ($live -join ';')) 'ultra-magnus fixture: repair leaves exactly the live entries in order'
Ok ($um.Length -gt 4096 -and $umFixed.Length -lt 4096) 'ultra-magnus fixture: repair takes it under the threshold'

# --- 4. findings and verdict ----------------------------------------------------------------------
$mStats = Get-ScopeStats $mA $machineRaw (Join-ExpandedPath $mA)
$f = Get-PathFindings -User $st -Machine $mStats -TotalChars 10579 -WhereGit FAIL -Runners @(
    @{ name = 'ultra-magnus-advllm'; label = 'runner-1'; path_chars = $null; env_lines = 1; env_has_lang = $false }
)
Ok ($f -contains 'total-over-4096:10579') 'findings: total over threshold'
Ok ($f -contains 'user-dead:85' -and $f -contains 'machine-dead:1') 'findings: dead counts per scope'
Ok ($f -contains 'cmd-where-git-failed') 'findings: failed cmd probe'
Ok ($f -contains 'runner-path-missing:runner-1' -and $f -contains 'runner-env-no-lang:runner-1') 'findings: runner .path missing and .env without LANG'
$clean = @{ chars = 400; raw_chars = 400; segments = 10; dead = 0; duplicates = 2; empty = 0; unverifiable = 0; dead_dotnet_tools = 0; removable = 2 }
$f2 = Get-PathFindings -User $clean -Machine $clean -TotalChars 801 -WhereGit PASS -Runners @(@{ name = 'r'; label = 'runner-1'; path_chars = 801; env_lines = 2; env_has_lang = $true })
Ok ($f2.Count -eq 0) 'findings: duplicates alone do not make a machine unhealthy'
Ok ((Get-PathFindings -User $clean -Machine $clean -TotalChars 4097 -WhereGit PASS).Count -eq 1) 'findings: 4097 chars is over the 4096 threshold'
Ok ((Get-PathFindings -User $clean -Machine $clean -TotalChars 4096 -WhereGit PASS).Count -eq 0) 'findings: 4096 chars is at, not over'
Ok ((Test-EnvHasLang "ACTIONS_RUNNER_HOOK_JOB_COMPLETED=x`r`nLANG=en_US.UTF-8`r`n") -and -not (Test-EnvHasLang 'ACTIONS_RUNNER_HOOK_JOB_COMPLETED=x') -and -not (Test-EnvHasLang $null)) 'env: LANG detection'

# --- 5. the ack record carries no paths and no user names (law 4) ---------------------------------
$now = [datetime]::new(2026, 11, 14, 23, 0, 0, [DateTimeKind]::Utc)
$rec = New-AckRecord -MachineName 'ultra-magnus' -NowUtc $now -ToolCommit ('a' * 40) -User $st -Machine $mStats -TotalChars 10579 -WhereGit FAIL `
    -Runners @(@{ name = 'ultra-magnus-advllm'; label = 'runner-1'; path_chars = $null; env_lines = 1; env_has_lang = $false; Dir = 'C:\actions-runners\ultra-magnus-advllm' }) -Findings $f
$recJson = $rec | ConvertTo-Json -Depth 6
Ok ($rec.machine -eq 'ULTRA-MAGNUS' -and $rec.verdict -eq 'UNHEALTHY' -and $rec.schema -eq 'fleet-path-health.v1') 'ack: machine upper-cased, verdict, schema'
Ok ($recJson -notmatch '[A-Za-z]:\\\\' -and $recJson -notmatch '\\\\Users' -and $recJson -notmatch 'ContextUltra') 'ack: no drive paths, no profile paths, no entry text'
Ok ($recJson -notmatch 'ultra-magnus-advllm' -and $recJson -match '"runner-1"') 'ack: runner folder names never travel, only ordinal labels'
Ok ($rec.published_utc -eq '2026-11-14T23:00:00Z') 'ack: UTC Z stamp'
$threw = $false; try { [void](New-AckRecord -MachineName 'bad/name' -NowUtc $now -ToolCommit 'x' -User $st -Machine $mStats -TotalChars 1 -WhereGit PASS) } catch { $threw = $true }
Ok $threw 'ack: refuses a machine name that is not a bus-safe token'
$healthy = New-AckRecord -MachineName 'BACHELOR' -NowUtc $now -ToolCommit 'b' -User $clean -Machine $clean -TotalChars 801 -WhereGit PASS -Findings @()
Ok ($healthy.verdict -eq 'HEALTHY') 'ack: no findings -> HEALTHY'

# --- 6. publish on change only (law 3) -------------------------------------------------------------
$prevRaw = $rec | ConvertTo-Json -Depth 6
Ok ((Test-AckPublishNeeded -PreviousRaw $null -Record $rec -NowUtc $now).Reason -eq 'first-publication') 'publish: first publication'
$later = New-AckRecord -MachineName 'ULTRA-MAGNUS' -NowUtc $now.AddHours(2) -ToolCommit ('c' * 40) -User $st -Machine $mStats -TotalChars 10579 -WhereGit FAIL `
    -Runners @(@{ name = 'ultra-magnus-advllm'; label = 'runner-1'; path_chars = $null; env_lines = 1; env_has_lang = $false }) -Findings $f
$n1 = Test-AckPublishNeeded -PreviousRaw $prevRaw -Record $later -NowUtc $now.AddHours(2) -RefreshHours 24
Ok (-not $n1.Publish) 'publish: same content, new stamp and new tool_commit -> no cadence push'
$n2 = Test-AckPublishNeeded -PreviousRaw $prevRaw -Record $later -NowUtc $now.AddHours(25) -RefreshHours 24
Ok ($n2.Publish -and $n2.Reason -eq 'refresh:24h') 'publish: refresh after RefreshHours'
$n3 = Test-AckPublishNeeded -PreviousRaw $prevRaw -Record $healthy -NowUtc $now.AddHours(1)
Ok ($n3.Publish -and $n3.Reason -eq 'changed') 'publish: changed content publishes at once'
Ok ((Test-AckPublishNeeded -PreviousRaw '{not json' -Record $rec -NowUtc $now).Reason -eq 'previous-unreadable') 'publish: unreadable previous record is republished'

# --- 7. reader: derived roster and statuses ---------------------------------------------------------
$hb = @('{"board":"a","machine":"VIRTUAL-TEN"}', '{"board":"b","machine":"BACHELOR"}', '{"board":"c","machine":"ULTRA-MAGNUS"}', '{"board":"d","machine":"VIRTUAL-TEN"}', '{"no":"machine"}')
$hbM = Get-HeartbeatMachines $hb
Ok ($hbM.Count -eq 4) 'reader: machines read from heartbeat machine fields'
$receiptsText = @(
    '- 2026-11-14 PATH-HEALTH: BLOCKED BACHELOR - exit 4, push rejected twice'
    'unrelated line'
    '- 2026-11-15 PATH-HEALTH: DISTINGUISH BACHELOR - no Windows shell tools in use'
    '- 2026-11-15 PATH-HEALTH: BLOCKED NEW-BOX - git not installed'
) -join "`n"
$dec = Get-ReceiptDecisions $receiptsText
Ok ($dec['BACHELOR'].Kind -eq 'DISTINGUISH') 'reader: later RECEIPTS line supersedes an earlier one'
$acks = [ordered]@{ 'VIRTUAL-TEN' = ($healthy | ConvertTo-Json -Depth 6) -replace 'BACHELOR', 'VIRTUAL-TEN'; 'OLD-BOX' = $prevRaw -replace 'ULTRA-MAGNUS', 'OLD-BOX' }
$rows = Get-PathHealthRows -HeartbeatMachines $hbM -Acks $acks -Decisions $dec -NowUtc $now.AddDays(1) -StaleDays 7
$by = @{}; foreach ($r in $rows) { $by[$r.machine] = $r }
Ok ($by['VIRTUAL-TEN'].status -eq 'ACKED' -and $by['VIRTUAL-TEN'].verdict -eq 'HEALTHY') 'reader: fresh ack -> ACKED'
Ok ($by['ULTRA-MAGNUS'].status -eq 'ABSENT') 'reader: heartbeat machine with no ack -> ABSENT'
Ok ($by['BACHELOR'].status -eq 'DISTINGUISHED') 'reader: reasoned decline -> DISTINGUISHED'
Ok ($by['NEW-BOX'].status -eq 'BLOCKED') 'reader: a RECEIPTS line alone puts a machine on the roster'
Ok ($by['OLD-BOX'].status -eq 'ACKED' -and $by['OLD-BOX'].verdict -eq 'UNHEALTHY') 'reader: an ack alone puts a machine on the roster'
$rowsLate = Get-PathHealthRows -HeartbeatMachines @() -Acks $acks -Decisions @{} -NowUtc $now.AddDays(8) -StaleDays 7
Ok (@($rowsLate | Where-Object status -eq 'STALE').Count -eq 2) 'reader: ack older than StaleDays -> STALE'
Ok ((Get-PathHealthExitCode $rows) -eq 1) 'reader: ABSENT/BLOCKED/UNHEALTHY -> exit 1'
$good = Get-PathHealthRows -HeartbeatMachines @('VIRTUAL-TEN') -Acks ([ordered]@{ 'VIRTUAL-TEN' = $acks['VIRTUAL-TEN'] }) -Decisions @{} -NowUtc $now -StaleDays 7
Ok ((Get-PathHealthExitCode $good) -eq 0) 'reader: all ACKED-HEALTHY -> exit 0'
$threw = $false; try { [void](Get-PathHealthRows -Acks @{ 'X' = '{broken' } -NowUtc $now) } catch { $threw = $true }
Ok $threw 'reader: an unparseable ack is UNEVALUABLE, not a pass'
function Throws([scriptblock]$s) { try { $null = & $s; return $false } catch { return $true } }
$goodRaw = $acks['VIRTUAL-TEN']
Ok (-not (Throws { Test-AckRecord -Raw $goodRaw -FileMachine 'VIRTUAL-TEN' })) 'reader: a well-formed ack validates'
Ok (Throws { Test-AckRecord -Raw ($goodRaw.TrimEnd().TrimEnd('}')) -FileMachine 'VIRTUAL-TEN' }) 'reader: a truncated ack (no closing brace) is UNEVALUABLE'
Ok (Throws { Test-AckRecord -Raw '{"metadata":{"published_utc":"2026-11-14T23:00:00Z","verdict":"HEALTHY"},"machine":"VIRTUAL-TEN","schema":"fleet-path-health.v1"}' -FileMachine 'VIRTUAL-TEN' }) 'reader: nested fields do not stand in for top-level ones'
Ok (Throws { Test-AckRecord -Raw ($goodRaw -replace '"VIRTUAL-TEN"', '"OTHER-BOX"') -FileMachine 'VIRTUAL-TEN' }) 'reader: machine field must match the file name'
Ok (Throws { Test-AckRecord -Raw ($goodRaw -replace 'fleet-path-health.v1', 'other.v1') -FileMachine 'VIRTUAL-TEN' }) 'reader: wrong schema is UNEVALUABLE'
Ok (Throws { Test-AckRecord -Raw ($goodRaw -replace '"HEALTHY"', '"FINE"') -FileMachine 'VIRTUAL-TEN' }) 'reader: unknown verdict is UNEVALUABLE'
Ok (Throws { Test-AckRecord -Raw ($goodRaw -replace '(\d\d:\d\d:\d\d)Z', '$1') -FileMachine 'VIRTUAL-TEN' }) 'reader: a stamp without a zone is UNEVALUABLE'
$v = Test-AckRecord -Raw $goodRaw -FileMachine 'virtual-ten'
Ok ($v.PublishedUtc -eq $now -and $v.Verdict -eq 'HEALTHY') 'reader: stamp read as UTC, not shifted by the local zone'

# --- 8. review-found hazards (PR #96 keys) ----------------------------------------------------------
$tri = { param($p) if ($p -like 'C:\Restricted*') { $null } elseif ($p -like 'C:\Lazy*') { $false } else { & $fsExists $p } }
$multiExpand = { param($t) $t.Replace('%TOOL_PATHS%', 'C:\Go\bin;C:\Users\u\bin').Replace('%USERPROFILE%', 'C:\Users\u').Replace('%APPDATA%', 'C:\Users\u\AppData\Roaming') }
$hz = Get-PathAnalysis -Raw '%TOOL_PATHS%;C:\Restricted\bin;%USERPROFILE%\Gone\bin;%USERPROFILE%\.dotnet\tools;%APPDATA%\npm;C:\Gone\abs' -Scope User -Exists {
    param($p) if ($p -like 'C:\Restricted*') { $null } elseif ($p -in @('C:\Users\u\.dotnet\tools', 'C:\Users\u\AppData\Roaming\npm')) { $false } else { & $fsExists $p } } -Expand $multiExpand `
    -PendingKeys (Get-PendingKeys $multiExpand)
$hc = @($hz | ForEach-Object Class)
Ok ($hc[0] -eq 'multi' -and -not $hz[0].Removable) 'hazard: a %VAR% expanding to several folders is never removed'
Ok ($hc[1] -eq 'unreadable' -and -not $hz[1].Removable) 'hazard: a folder that cannot be inspected is unreadable, never dead'
Ok ($hc[2] -eq 'dead-var' -and -not $hz[2].Removable) 'hazard: a dead %VAR% entry is reported, never removed (process env may be overridden)'
Ok ($hc[3] -eq 'pending' -and $hc[4] -eq 'pending' -and -not $hz[3].Removable -and -not $hz[4].Removable) 'hazard: not-yet-created %USERPROFILE%\.dotnet\tools and %APPDATA%\npm are pending, kept'
Ok ($hc[5] -eq 'dead' -and $hz[5].Removable) 'hazard: an absolute dead entry is still removable'
$hs = Get-ScopeStats $hz '' (Join-ExpandedPath $hz)
Ok ($hs.dead -eq 1 -and $hs.pending -eq 2 -and $hs.unverifiable -eq 3) 'hazard: only the absolute dead entry counts as dead'
$mz = Get-PathAnalysis -Raw 'C:\Restricted\sys' -Scope Machine -Exists $tri
Ok ($mz[0].Class -eq 'unreadable' -and -not $mz[0].Removable) 'hazard: elevated Machine repair never removes an unreadable entry'
Ok ((Get-PathAnalysis -Raw 'Z:\x' -Scope User -Exists { param($p) $null })[0].Class -eq 'drive-absent') 'hazard: an unreadable drive root is not proof the entry is dead'

# account matching: by SID, `.\name` is the LOCAL account
$sids = @{ 'CORP\build' = 'S-1-5-21-1-1001'; 'BOX1\build' = 'S-1-5-21-9-1001' }
$res = { param($q) $sids[$q] }
Ok (-not (Test-SameServiceAccount '.\build' 'S-1-5-21-1-1001' 'BOX1' $res)) 'account: domain CORP\build is not local .\build'
Ok (Test-SameServiceAccount '.\build' 'S-1-5-21-9-1001' 'BOX1' $res) 'account: local .\build matches the local account SID'
Ok (Test-SameServiceAccount 'CORP\build' 'S-1-5-21-1-1001' 'BOX1' $res) 'account: same qualified account matches'
Ok (-not (Test-SameServiceAccount 'LocalSystem' 'S-1-5-18' 'BOX1' { param($q) 'S-1-5-18' })) 'account: LocalSystem never owns a user PATH'
Ok (-not (Test-SameServiceAccount 'CORP\ghost' 'S-1-5-21-1-1001' 'BOX1' $res)) 'account: unresolvable account fails closed'
Ok (-not (Test-SameServiceAccount '' 'S-1-5-21-1-1001' 'BOX1' $res)) 'account: empty StartName fails closed'

# runner .path: rewrite only when it is broken or still holds a removed entry
Ok ((Get-RunnerPathAction $null @()) -eq 'rewrite:missing') 'runner: missing .path is rewritten'
Ok ((Get-RunnerPathAction ('x' * 5000) @()) -eq 'rewrite:over-limit') 'runner: over-limit .path is rewritten'
Ok ((Get-RunnerPathAction 'C:\Git\bin;D:\Gate\1\.dotnet\tools' @('d:\gate\1\.dotnet\tools')) -eq 'rewrite:holds-removed-entry') 'runner: .path holding a removed entry is rewritten'
Ok ((Get-RunnerPathAction 'C:\Program Files\Git\bin;C:\Windows\System32' @('d:\gate\1\.dotnet\tools')) -eq 'keep') 'runner: a healthy hand-ordered .path is kept'
Ok ((Get-RestartDecision $false $false) -eq 'skip:needs-administrator') 'restart: never without Administrator'
Ok ((Get-RestartDecision $true $true) -eq 'skip:busy') 'restart: never while busy'
Ok ((Get-RestartDecision $true 'gh not installed') -like 'skip:busy-unknown*') 'restart: never when busy cannot be read'
Ok ((Get-RestartDecision $true $false) -eq 'restart') 'restart: elevated and idle'
Ok ((Get-RunnerPathAction '' @()) -eq 'rewrite:empty' -and (Get-RunnerPathAction "  `r`n" @()) -eq 'rewrite:empty') 'runner: empty or blank .path is rewritten'
$dupA = Get-PathAnalysis -Raw 'C:\Go\bin;C:\Go\bin;C:\Program Files\Git\cmd;C:\Gone\abs' -Scope User -Exists $fsExists -OtherScopeKeys @('c:\program files\git\cmd')
$stale = Get-StaleRunnerKeys @($dupA | Where-Object Removable)
Ok ($stale.Count -eq 1 -and $stale[0] -eq 'c:\gone\abs') 'runner: only dead removals make a .path stale, not duplicates'
Ok ((Get-RunnerPathAction 'C:\Program Files\Git\cmd;C:\Windows\System32;C:\Go\bin' $stale) -eq 'keep') 'runner: a hand-ordered .path listing a removed duplicate is kept'
$varDup2 = Get-PathAnalysis -Raw 'C:\Go\bin;%GO%\bin' -Scope User -Exists $fsExists -Expand { param($t) $t.Replace('%GO%', 'C:\Go') } -OtherScopeKeys @('c:\users\u\bin')
Ok ($varDup2[1].Class -eq 'duplicate-var' -and -not $varDup2[1].Removable) 'hazard: a %VAR% duplicate is reported, never removed'
$varCross = Get-PathAnalysis -Raw '%GO%\bin' -Scope User -Exists $fsExists -Expand { param($t) $t.Replace('%GO%', 'C:\Go') } -OtherScopeKeys @('c:\go\bin')
Ok ($varCross[0].Class -eq 'duplicate-var' -and -not $varCross[0].Removable) 'hazard: a %VAR% repeat of a Machine entry is reported, never removed'
$litAfterVar = Get-PathAnalysis -Raw '%H%\bin;C:\Go\bin' -Scope User -Exists $fsExists -Expand { param($t) $t.Replace('%H%', 'C:\Go') }
Ok ($litAfterVar[1].Class -eq 'duplicate-var' -and -not $litAfterVar[1].Removable) 'hazard: a literal entry repeating an earlier %VAR% entry is reported, never removed'
$litVsMachineVar = Get-PathAnalysis -Raw 'C:\Go\bin' -Scope User -Exists $fsExists -OtherScopeVarKeys @('c:\go\bin')
Ok ($litVsMachineVar[0].Class -eq 'duplicate-var' -and -not $litVsMachineVar[0].Removable) 'hazard: a literal User entry repeating a Machine %VAR% entry is reported, never removed'
$rel = Get-PathAnalysis -Raw 'node_modules\.bin;.\tools;C:' -Scope User -Exists { param($p) $false }
Ok (@($rel | Where-Object { $_.Class -eq 'relative' -and -not $_.Removable }).Count -eq 3) 'hazard: relative entries are never judged or removed'
Ok (Throws { Test-AckRecord -Raw "[$goodRaw]" -FileMachine 'VIRTUAL-TEN' }) 'reader: a top-level array is UNEVALUABLE'
Ok (Throws { Test-AckRecord -Raw ($goodRaw -replace '"verdict":\s*"HEALTHY"', '"verdict": ["HEALTHY"]') -FileMachine 'VIRTUAL-TEN' }) 'reader: an array-valued verdict is UNEVALUABLE'
Ok (Throws { Test-AckRecord -Raw ($goodRaw -replace '"schema":\s*"fleet-path-health.v1"', '"schema": ["fleet-path-health.v1"]') -FileMachine 'VIRTUAL-TEN' }) 'reader: an array-valued schema is UNEVALUABLE'
Ok (Throws { Test-AckRecord -Raw ($goodRaw -replace '(\d\d:\d\d:\d\d)Z', '$1+02:00') -FileMachine 'VIRTUAL-TEN' }) 'reader: an offset stamp that is not Z is UNEVALUABLE'
Ok (Throws { Test-AckRecord -Raw ($goodRaw -replace '2026-11-14T23', '2099-11-14T23') -FileMachine 'VIRTUAL-TEN' -NowUtc $now }) 'reader: a 2099 stamp is UNEVALUABLE, never forever-fresh'
Ok (Throws { Test-AckRecord -Raw $goodRaw -FileMachine 'VIRTUAL-TEN' -NowUtc $now.AddHours(-1) }) 'reader: a stamp in the future is UNEVALUABLE'
Ok (Throws { Test-AckRecord -Raw ($goodRaw -replace '"findings":\s*\[\s*\]', '"findings": ["user-dead:1"]') -FileMachine 'VIRTUAL-TEN' }) 'reader: HEALTHY with findings is UNEVALUABLE'
$fe = Get-PathFindings -User $clean -Machine $clean -TotalChars 801 -WhereGit PASS -Runners @(@{ label = 'runner-1'; path_chars = 0; env_lines = 1; env_has_lang = (Test-EnvHasLang 'LANG=') })
Ok ($fe -contains 'runner-path-empty:runner-1' -and $fe -contains 'runner-env-no-lang:runner-1') 'runner: empty .path and LANG= with no value are findings'

# --- 9. round-3 key findings: pending set, exit codes, publish push guard ---------------------------
$ps = Get-PendingKeySet @($expand, { param($t) $t.Replace('%USERPROFILE%', 'D:\Profiles\u').Replace('%APPDATA%', 'D:\Profiles\u\AppData\Roaming') })
Ok ($ps -is [string[]] -and @($ps | Where-Object { $_ -isnot [string] -or $_ -match ' ' }).Count -eq 0) 'pending: the union is a flat string array, never an array of arrays'
Ok ($ps -contains 'c:\users\u\.dotnet\tools' -and $ps -contains 'd:\profiles\u\.dotnet\tools' -and $ps -contains 'd:\profiles\u\appdata\roaming\npm') 'pending: keys from every expander are present, one per element'
$pz = Get-PathAnalysis -Raw 'D:\Profiles\u\.dotnet\tools' -Scope User -Exists { param($p) $p -eq 'D:\' } -PendingKeys $ps
Ok ($pz[0].Class -eq 'pending' -and -not $pz[0].Removable) 'pending: a token-path dotnet tools folder from the second expander is kept'
Ok ((Get-FinalExitCode 0 $true 0) -eq 10 -and (Get-FinalExitCode 1 $true 0) -eq 11) 'exit: a published ack is 10 HEALTHY / 11 UNHEALTHY, never 0 or 1'
Ok ((Get-FinalExitCode 1 $true 4) -eq 4 -and (Get-FinalExitCode 0 $true 5) -eq 5) 'exit: a failed or rehearsal publish shows its own code'
Ok ((Get-FinalExitCode 2 $true 0) -eq 2) 'exit: a failed -Apply stays 2 even when the ack published'
Ok ((Get-FinalExitCode 1 $false) -eq 1 -and (Get-FinalExitCode 0 $false) -eq 0) 'exit: -Check without -Publish keeps 0/1'

# Publish push guard and undo, on a throwaway repository with a throwaway bare origin.
if (Get-Command git -ErrorAction SilentlyContinue) {
    $tmp = Join-Path ([IO.Path]::GetTempPath()) ('path-ack-test-' + [guid]::NewGuid().ToString('N'))
    $origin = Join-Path $tmp 'origin.git'; $wc = Join-Path $tmp 'wc'
    $g = { & git -c user.name=t -c user.email=t@example.invalid -c commit.gpgsign=false -c init.defaultBranch=master @args *> $null }
    $ackRel = 'path-health/TESTBOX.json'
    $ackMsg = 'path-health: TESTBOX UNHEALTHY (first-publication)'
    try {
        [void](New-Item -ItemType Directory -Force -Path $tmp)
        & $g init -q --bare $origin
        & $g init -q $wc
        Set-Content -LiteralPath (Join-Path $wc 'README.md') -Value 'bus'
        & $g -C $wc add README.md; & $g -C $wc commit -q -m base
        & $g -C $wc remote add origin $origin; & $g -C $wc push -q origin 'HEAD:refs/heads/master'
        [void](New-Item -ItemType Directory -Force -Path (Join-Path $wc 'path-health'))
        Set-Content -LiteralPath (Join-Path $wc $ackRel) -Value '{}'
        & $g -C $wc add $ackRel; & $g -C $wc commit -q -m $ackMsg
        Ok ($null -eq (Get-AckPushBlocker $wc 'master' $ackRel)) 'push guard: exactly one ack-only commit ahead may push'
        Set-Content -LiteralPath (Join-Path $wc 'README.md') -Value 'bus+local'
        & $g -C $wc add README.md; & $g -C $wc commit -q --amend -m $ackMsg
        Ok ((Get-AckPushBlocker $wc 'master' $ackRel) -like 'HEAD commit touches*') 'push guard: an ack commit that also touches another file is refused'
        Ok ((Undo-AckCommit $wc $ackRel 'TESTBOX') -like 'ack commit left in place*') 'undo: a HEAD that is not exactly our ack is never reset'
        & $g -C $wc reset -q --hard origin/master
        Set-Content -LiteralPath (Join-Path $wc 'other.md') -Value 'unreviewed'
        & $g -C $wc add other.md; & $g -C $wc commit -q -m 'local unreviewed work'
        [void](New-Item -ItemType Directory -Force -Path (Join-Path $wc 'path-health'))
        Set-Content -LiteralPath (Join-Path $wc $ackRel) -Value '{}'
        & $g -C $wc add $ackRel; & $g -C $wc commit -q -m $ackMsg
        Ok ((Get-AckPushBlocker $wc 'master' $ackRel) -like 'HEAD is 2 commits ahead*') 'push guard: local unreviewed commits under the ack block the push'
        $prior = ([string](& git -C $wc rev-parse HEAD~1)).Trim()
        Ok ((Undo-AckCommit $wc $ackRel 'TESTBOX') -eq 'ack commit undone locally') 'undo: our own one-file ack commit is taken back'
        Ok (([string](& git -C $wc rev-parse HEAD)).Trim() -eq $prior -and (Test-Path -LiteralPath (Join-Path $wc $ackRel))) 'undo: HEAD returns to the prior commit and the ack file stays on disk'
        Ok ((Get-AckPushBlocker $wc 'nosuchbranch' $ackRel) -like 'cannot fetch*') 'push guard: an unfetchable branch blocks the push'
    } finally { Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue }
} else { Ok $false 'git is required for the publish push-guard tests' }

if ($IsWindows) { Ok ([Environment]::GetEnvironmentVariable('Path', 'User') -eq $realUserBefore) 'guard: real User PATH unchanged by the tests' }

Write-Output ("Repair-MachinePath tests: {0} passed, {1} failed" -f $script:pass, $script:fail)
exit $(if ($script:fail) { 1 } else { 0 })
