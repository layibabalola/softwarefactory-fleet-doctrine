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
$exists = { param($p) $fs.Contains($p.TrimEnd('\')) -or $fs.Contains($p) }
$expand = { param($t) $t.Replace('%USERPROFILE%', 'C:\Users\u').Replace('%SystemRoot%', 'C:\Windows') }

# --- 1. classification ---------------------------------------------------------------------------
$machineRaw = '%SystemRoot%\system32;%SystemRoot%;C:\Program Files\Git\cmd;C:\Gone\Machine\bin'
$mA = Get-PathAnalysis -Raw $machineRaw -Scope Machine -Exists $exists -Expand $expand
Ok ($mA.Count -eq 4) 'machine: four segments'
Ok (($mA | Where-Object Class -eq 'dead').Count -eq 1) 'machine: one dead entry'
Ok (@($mA | Where-Object Removable).Count -eq 1 -and @($mA | Where-Object Removable)[0].Raw -eq 'C:\Gone\Machine\bin') 'machine: only the dead entry is removable'

$mDup = Get-PathAnalysis -Raw 'C:\Windows;C:\Windows\' -Scope Machine -Exists $exists -Expand $expand
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
$uA = Get-PathAnalysis -Raw $userRaw -Scope User -Exists $exists -Expand $expand -OtherScopeKeys $mKeys
$cls = @($uA | ForEach-Object Class)
Ok ($cls[0] -eq 'ok') 'user: %USERPROFILE% entry that exists is ok'
Ok ($cls[1] -eq 'ok') 'user: live .dotnet\tools is ok'
Ok ($cls[2] -eq 'dead' -and $uA[2].DotnetTools) 'user: dead per-run .dotnet\tools is dead and flagged dotnet'
Ok ($cls[3] -eq 'empty') 'user: empty segment'
Ok ($cls[4] -eq 'duplicate') 'user: case/trailing-slash duplicate of an earlier entry'
Ok ($cls[5] -eq 'cross-duplicate') 'user: repeats a Machine entry'
Ok ($cls[6] -eq 'unc') 'user: UNC entry is unverifiable'
Ok ($cls[7] -eq 'unresolved') 'user: unexpanded %VAR% is unverifiable'
Ok ($cls[8] -eq 'drive-absent') 'user: entry on an unmounted drive is unverifiable'
Ok ($cls[9] -eq 'ok') 'user: plain existing entry'
Ok (-not ($uA | Where-Object { $_.Class -in @('ok', 'unc', 'unresolved', 'drive-absent') -and $_.Removable })) 'user: no live or unverifiable entry is removable'

# --- 2. repair ------------------------------------------------------------------------------------
$repaired = Get-RepairedPath $uA
Ok ($repaired -eq (@('%USERPROFILE%\AppData\Roaming\npm', 'C:\Users\u\.dotnet\tools', '\\fileserver\share\bin', '%NOT_DEFINED_VAR%\bin', 'Q:\removable\bin', 'C:\Go\bin') -join ';')) 'repair: keeps order and raw %VAR% text, drops dead/empty/duplicate/cross-duplicate'
$again = Get-PathAnalysis -Raw $repaired -Scope User -Exists $exists -Expand $expand -OtherScopeKeys $mKeys
Ok (@($again | Where-Object Removable).Count -eq 0) 'repair: idempotent (second pass removes nothing)'
Ok ((Get-RepairedPath $mA) -eq '%SystemRoot%\system32;%SystemRoot%;C:\Program Files\Git\cmd') 'repair: machine loses only its dead entry'
Ok ((Get-RepairedPath (Get-PathAnalysis -Raw '' -Scope User -Exists $exists)) -eq '') 'repair: empty PATH stays empty'

# --- 3. the ULTRA-MAGNUS shape: 95 entries, 85 dead per-run dotnet tool dirs ----------------------
$live = @('C:\Users\u\AppData\Roaming\npm', 'C:\Users\u\.dotnet\tools', 'C:\Go\bin', 'C:\Program Files\nodejs', 'C:\Users\u\bin')
$deadGate = 1..80 | ForEach-Object { "D:\ContextUltraWindowsGate\20261101-$_-1\cli-home\.dotnet\tools" }
$deadWt = 1..4 | ForEach-Object { "C:\ContextUltraWorktrees\v-$_\ps-setup-cleanup-$_\cu-setup-cleanup-admission-$_\dotnet-home\.dotnet\tools" }
$deadDng = @('C:\DngAutoJobs\evidence\x\dotnet-cli\.dotnet\tools')
$dups = @('C:\Go\bin', 'C:\Users\u\bin', 'C:\Program Files\nodejs', 'C:\Users\u\AppData\Roaming\npm', 'C:\Users\u\.dotnet\tools')
$um = (@($live) + $deadGate + $deadWt + $deadDng + $dups) -join ';'
$umA = Get-PathAnalysis -Raw $um -Scope User -Exists $exists -Expand $expand
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
    @{ name = 'ultra-magnus-advllm'; path_chars = $null; env_lines = 1; env_has_lang = $false }
)
Ok ($f -contains 'total-over-4096:10579') 'findings: total over threshold'
Ok ($f -contains 'user-dead:85' -and $f -contains 'machine-dead:1') 'findings: dead counts per scope'
Ok ($f -contains 'cmd-where-git-failed') 'findings: failed cmd probe'
Ok ($f -contains 'runner-path-missing:ultra-magnus-advllm' -and $f -contains 'runner-env-no-lang:ultra-magnus-advllm') 'findings: runner .path missing and .env without LANG'
$clean = @{ chars = 400; raw_chars = 400; segments = 10; dead = 0; duplicates = 2; empty = 0; unverifiable = 0; dead_dotnet_tools = 0; removable = 2 }
$f2 = Get-PathFindings -User $clean -Machine $clean -TotalChars 801 -WhereGit PASS -Runners @(@{ name = 'r'; path_chars = 801; env_lines = 2; env_has_lang = $true })
Ok ($f2.Count -eq 0) 'findings: duplicates alone do not make a machine unhealthy'
Ok ((Get-PathFindings -User $clean -Machine $clean -TotalChars 4097 -WhereGit PASS).Count -eq 1) 'findings: 4097 chars is over the 4096 threshold'
Ok ((Get-PathFindings -User $clean -Machine $clean -TotalChars 4096 -WhereGit PASS).Count -eq 0) 'findings: 4096 chars is at, not over'
Ok ((Test-EnvHasLang "ACTIONS_RUNNER_HOOK_JOB_COMPLETED=x`r`nLANG=en_US.UTF-8`r`n") -and -not (Test-EnvHasLang 'ACTIONS_RUNNER_HOOK_JOB_COMPLETED=x') -and -not (Test-EnvHasLang $null)) 'env: LANG detection'

# --- 5. the ack record carries no paths and no user names (law 4) ---------------------------------
$now = [datetime]::new(2026, 11, 14, 23, 0, 0, [DateTimeKind]::Utc)
$rec = New-AckRecord -MachineName 'ultra-magnus' -NowUtc $now -ToolCommit ('a' * 40) -User $st -Machine $mStats -TotalChars 10579 -WhereGit FAIL `
    -Runners @(@{ name = 'ultra-magnus-advllm'; path_chars = $null; env_lines = 1; env_has_lang = $false; Dir = 'C:\actions-runners\ultra-magnus-advllm' }) -Findings $f
$recJson = $rec | ConvertTo-Json -Depth 6
Ok ($rec.machine -eq 'ULTRA-MAGNUS' -and $rec.verdict -eq 'UNHEALTHY' -and $rec.schema -eq 'fleet-path-health.v1') 'ack: machine upper-cased, verdict, schema'
Ok ($recJson -notmatch '[A-Za-z]:\\\\' -and $recJson -notmatch '\\\\Users' -and $recJson -notmatch 'ContextUltra') 'ack: no drive paths, no profile paths, no entry text'
Ok ($rec.published_utc -eq '2026-11-14T23:00:00Z') 'ack: UTC Z stamp'
$threw = $false; try { [void](New-AckRecord -MachineName 'bad/name' -NowUtc $now -ToolCommit 'x' -User $st -Machine $mStats -TotalChars 1 -WhereGit PASS) } catch { $threw = $true }
Ok $threw 'ack: refuses a machine name that is not a bus-safe token'
$healthy = New-AckRecord -MachineName 'BACHELOR' -NowUtc $now -ToolCommit 'b' -User $clean -Machine $clean -TotalChars 801 -WhereGit PASS -Findings @()
Ok ($healthy.verdict -eq 'HEALTHY') 'ack: no findings -> HEALTHY'

# --- 6. publish on change only (law 3) -------------------------------------------------------------
$prevRaw = $rec | ConvertTo-Json -Depth 6
Ok ((Test-AckPublishNeeded -PreviousRaw $null -Record $rec -NowUtc $now).Reason -eq 'first-publication') 'publish: first publication'
$later = New-AckRecord -MachineName 'ULTRA-MAGNUS' -NowUtc $now.AddHours(2) -ToolCommit ('c' * 40) -User $st -Machine $mStats -TotalChars 10579 -WhereGit FAIL `
    -Runners @(@{ name = 'ultra-magnus-advllm'; path_chars = $null; env_lines = 1; env_has_lang = $false }) -Findings $f
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

if ($IsWindows) { Ok ([Environment]::GetEnvironmentVariable('Path', 'User') -eq $realUserBefore) 'guard: real User PATH unchanged by the tests' }

Write-Output ("Repair-MachinePath tests: {0} passed, {1} failed" -f $script:pass, $script:fail)
exit $(if ($script:fail) { 1 } else { 0 })
