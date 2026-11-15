<#
.SYNOPSIS
Check, and on request repair, a Windows machine's persisted PATH, and publish a per-machine
path-health ack to the bus.

.DESCRIPTION
Why this exists (TRAPS.md: "An overlong Windows PATH can break shell-string child commands while
direct executables still work", 2026-08-17, and its recurrence of 2026-11-14 on ULTRA-MAGNUS).
Tools that set DOTNET_CLI_HOME per run make the .NET CLI's first-run step append
`<DOTNET_CLI_HOME>\.dotnet\tools` to the persisted User PATH, once per fresh home, and nothing ever
removes it. The PATH grows by one dead folder per run until cmd.exe children stop finding git,
node and go while pwsh and bash still find them. See doctrine/pattern-path-defense-2026-11.md.

Modes (exactly one of -Check or -Apply; -Publish may ride on either):

  -Check    READ-ONLY. Reports User and Machine PATH length, segment count, dead, duplicate and
            empty entries, a `cmd.exe /d /c where git` probe run with the PATH a new process would
            get, and every self-hosted runner under -RunnerRoot (its .path length, its .env).
            Exit 0 HEALTHY, 1 UNHEALTHY, 2 UNEVALUABLE.

  -Apply    Backs up first, then removes dead, empty and duplicate entries from the User PATH.
            It touches the Machine PATH only when elevated, and only to remove dead entries.
            It never removes an entry whose folder exists, a UNC entry, an entry with an
            unexpanded %VAR%, or an entry on a drive that is not mounted. It then rewrites each
            runner's .path from the repaired PATH (only when the runner service runs as the
            current user) and restarts that service only when it is idle (GitHub `busy` = false,
            read with `gh api`) and the shell is elevated; otherwise it skips the restart and says
            why. Writes a receipt and the backups under %LOCALAPPDATA%\FleetPathRepair\<utc>\.
            Exit is the post-repair -Check verdict, or 2 if a write failed.

  -Publish  Writes path-health/<MACHINE>.json in -BusRoot (counts and verdict only: no paths, no
            user names), commits that one file and pushes the current branch. It pushes only when
            the content changed or the published record is older than -RefreshHours (law 3).
            The record is published whatever the verdict: an UNHEALTHY ack is still an ack.
            -NoPush commits locally and stops (rehearsal). A failed publish exits 4.

Tests dot-source this file with -Library and call the pure functions with injected PATH strings
and an injected folder-exists predicate. Nothing in the test path reads or writes the real
environment.

.EXAMPLE
pwsh -NoProfile -File tools/Repair-MachinePath.ps1 -Check
.EXAMPLE
pwsh -NoProfile -File tools/Repair-MachinePath.ps1 -Check -Publish -BusRoot <bus clone>
.EXAMPLE
pwsh -NoProfile -File tools/Repair-MachinePath.ps1 -Apply      # owner's call, per machine
#>
[CmdletBinding()]
param(
    [switch]$Check,
    [switch]$Apply,
    [switch]$Publish,
    [switch]$NoPush,
    [string]$BusRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$RunnerRoot = 'C:\actions-runners',
    [int]$MaxTotalChars = 4096,
    [int]$RefreshHours = 24,
    [switch]$Json,
    [switch]$Library
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$script:AckSchema = 'fleet-path-health.v1'

# ------------------------------------------------------------------------------------------------
# Pure functions. No registry, no filesystem, no process: everything arrives as an argument.
# ------------------------------------------------------------------------------------------------

function Split-PathList([AllowNull()][AllowEmptyString()][string]$Raw) {
    if ($null -eq $Raw -or $Raw -eq '') { return ,@() }
    return ,@($Raw -split ';')
}

function Get-PathKey([string]$Expanded) {
    $k = $Expanded.Trim().Trim('"').Trim()
    while ($k.Length -gt 3 -and $k.EndsWith('\')) { $k = $k.Substring(0, $k.Length - 1) }
    return $k.ToLowerInvariant()
}

<#
Classify every segment of one scope's raw (unexpanded) PATH value.
  -Exists   scriptblock: param($folder) -> $true when the folder exists
  -Expand   scriptblock: param($text)   -> expanded text
  -OtherScopeKeys  keys of the Machine PATH, so a User entry that repeats one is redundant
Classes: ok, empty, unc, unresolved, drive-absent, dead, cross-duplicate, duplicate.
#>
function Get-PathAnalysis {
    param(
        [AllowNull()][AllowEmptyString()][string]$Raw,
        [ValidateSet('User', 'Machine')][string]$Scope,
        [Parameter(Mandatory)][scriptblock]$Exists,
        [scriptblock]$Expand = { param($t) $t },
        [string[]]$OtherScopeKeys = @()
    )
    $other = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    foreach ($k in $OtherScopeKeys) { [void]$other.Add($k) }
    $seen = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    $rows = [System.Collections.Generic.List[object]]::new()
    $i = 0
    foreach ($seg in (Split-PathList $Raw)) {
        $expanded = [string](& $Expand $seg)
        $trimmed = $expanded.Trim().Trim('"').Trim()
        $key = if ($trimmed) { Get-PathKey $trimmed } else { '' }
        $class = 'ok'
        if (-not $trimmed) { $class = 'empty' }
        elseif ($trimmed.StartsWith('\\')) { $class = 'unc' }
        elseif ($trimmed -match '%[^%;]+%') { $class = 'unresolved' }
        elseif ($trimmed -match '^[A-Za-z]:' -and -not (& $Exists ($trimmed.Substring(0, 2) + '\'))) { $class = 'drive-absent' }
        elseif (-not (& $Exists $trimmed)) { $class = 'dead' }
        elseif ($Scope -eq 'User' -and $other.Contains($key)) { $class = 'cross-duplicate' }
        elseif ($seen.Contains($key)) { $class = 'duplicate' }
        if ($key -and $class -in @('ok', 'unc', 'unresolved', 'drive-absent')) { [void]$seen.Add($key) }
        $removable = if ($Scope -eq 'User') { $class -in @('empty', 'dead', 'duplicate', 'cross-duplicate') } else { $class -eq 'dead' }
        $rows.Add([pscustomobject]@{
            Index = $i; Raw = $seg; Expanded = $trimmed; Key = $key; Class = $class; Removable = $removable
            DotnetTools = ($trimmed -match '\\\.dotnet\\tools$')
        })
        $i++
    }
    return ,$rows.ToArray()
}

function Get-RepairedPath([object[]]$Analysis) {
    return (@($Analysis | Where-Object { -not $_.Removable } | ForEach-Object { $_.Raw }) -join ';')
}

function Get-ScopeStats([object[]]$Analysis, [string]$Raw, [string]$ExpandedJoined) {
    $a = @($Analysis)
    [ordered]@{
        chars             = $ExpandedJoined.Length
        raw_chars         = ([string]$Raw).Length
        segments          = $a.Count
        dead              = @($a | Where-Object Class -eq 'dead').Count
        duplicates        = @($a | Where-Object { $_.Class -in @('duplicate', 'cross-duplicate') }).Count
        empty             = @($a | Where-Object Class -eq 'empty').Count
        unverifiable      = @($a | Where-Object { $_.Class -in @('unc', 'unresolved', 'drive-absent') }).Count
        dead_dotnet_tools = @($a | Where-Object { $_.Class -eq 'dead' -and $_.DotnetTools }).Count
        removable         = @($a | Where-Object Removable).Count
    }
}

function Join-ExpandedPath([object[]]$Analysis) {
    return (@($Analysis | Where-Object { $_.Expanded } | ForEach-Object { $_.Expanded }) -join ';')
}

<#
Turn measurements into findings. A finding is a short token; the verdict is HEALTHY only when
there are none. Runner rows: @{ name; path_chars (int or $null); env_lines (int or $null);
env_has_lang (bool) }.
#>
function Get-PathFindings {
    param(
        [System.Collections.IDictionary]$User,
        [System.Collections.IDictionary]$Machine,
        [int]$TotalChars,
        [int]$MaxTotalChars = 4096,
        [ValidateSet('PASS', 'FAIL', 'SKIPPED')][string]$WhereGit,
        [object[]]$Runners = @()
    )
    $f = [System.Collections.Generic.List[string]]::new()
    if ($TotalChars -gt $MaxTotalChars) { $f.Add("total-over-${MaxTotalChars}:$TotalChars") }
    if ($User.dead -gt 0) { $f.Add("user-dead:$($User.dead)") }
    if ($Machine.dead -gt 0) { $f.Add("machine-dead:$($Machine.dead)") }
    if ($WhereGit -eq 'FAIL') { $f.Add('cmd-where-git-failed') }
    foreach ($r in @($Runners)) {
        if ($null -eq $r.path_chars) { $f.Add("runner-path-missing:$($r.name)") }
        elseif ($r.path_chars -gt $MaxTotalChars) { $f.Add("runner-path-over-${MaxTotalChars}:$($r.name):$($r.path_chars)") }
        if ($null -eq $r.env_lines) { $f.Add("runner-env-missing:$($r.name)") }
        elseif (-not $r.env_has_lang) { $f.Add("runner-env-no-lang:$($r.name)") }
    }
    return ,$f.ToArray()
}

function New-AckRecord {
    param(
        [string]$MachineName, [datetime]$NowUtc, [string]$ToolCommit,
        [System.Collections.IDictionary]$User, [System.Collections.IDictionary]$Machine,
        [int]$TotalChars, [string]$WhereGit, [object[]]$Runners = @(), [string[]]$Findings = @()
    )
    if ($MachineName -notmatch '^[A-Za-z0-9][A-Za-z0-9-]{0,62}$') { throw "machine name '$MachineName' is not a bus-safe token" }
    $runnerRows = @(foreach ($r in @($Runners)) {
        [ordered]@{ name = [string]$r.name; path_chars = $r.path_chars; env_lines = $r.env_lines; env_has_lang = [bool]$r.env_has_lang }
    })
    [ordered]@{
        schema        = $script:AckSchema
        machine       = $MachineName.ToUpperInvariant()
        published_utc = $NowUtc.ToString('yyyy-MM-ddTHH:mm:ssZ')
        tool_commit   = $ToolCommit
        verdict       = if (@($Findings).Count -eq 0) { 'HEALTHY' } else { 'UNHEALTHY' }
        findings      = @($Findings)
        total_chars   = $TotalChars
        user          = [ordered]@{ chars = $User.chars; segments = $User.segments; dead = $User.dead; duplicates = $User.duplicates; empty = $User.empty; dead_dotnet_tools = $User.dead_dotnet_tools }
        machine_scope = [ordered]@{ chars = $Machine.chars; segments = $Machine.segments; dead = $Machine.dead; duplicates = $Machine.duplicates; dead_dotnet_tools = $Machine.dead_dotnet_tools }
        cmd_where_git = $WhereGit
        runners       = $runnerRows
    }
}

<#
Law 3: publish on content change, or when the published record is older than RefreshHours.
published_utc and tool_commit never trigger a push: one changes every run, and the other is moved
by the act of publishing (a fresh clone's HEAD is the previous ack).
Returns @{ Publish = bool; Reason = string }.
#>
function Test-AckPublishNeeded {
    param([AllowNull()][string]$PreviousRaw, [System.Collections.IDictionary]$Record, [datetime]$NowUtc, [int]$RefreshHours = 24)
    if (-not $PreviousRaw) { return @{ Publish = $true; Reason = 'first-publication' } }
    try { $prev = $PreviousRaw | ConvertFrom-Json -AsHashtable -ErrorAction Stop } catch { return @{ Publish = $true; Reason = 'previous-unreadable' } }
    $strip = {
        param($h)
        $c = [ordered]@{}
        foreach ($k in $h.Keys) { if ($k -notin @('published_utc', 'tool_commit')) { $c[$k] = $h[$k] } }
        ($c | ConvertTo-Json -Depth 6 -Compress)
    }
    $prevCanon = & $strip $prev
    $newCanon = & $strip (($Record | ConvertTo-Json -Depth 6) | ConvertFrom-Json -AsHashtable)
    if ($prevCanon -ne $newCanon) { return @{ Publish = $true; Reason = 'changed' } }
    # Raw text, never the coerced object: ConvertFrom-Json turns an ISO stamp into local time.
    $age = 9999
    if ($PreviousRaw -match '"published_utc"\s*:\s*"([^"]+)"') {
        try { $age = ($NowUtc - [datetimeoffset]::Parse($Matches[1]).UtcDateTime).TotalHours } catch { $age = 9999 }
    }
    if ($age -lt $RefreshHours) { return @{ Publish = $false; Reason = ('unchanged, {0:n1} h old' -f $age) } }
    return @{ Publish = $true; Reason = "refresh:${RefreshHours}h" }
}

function Test-EnvHasLang([AllowNull()][string]$EnvText) {
    if ($null -eq $EnvText) { return $false }
    return [bool](($EnvText -split "`r?`n") | Where-Object { $_ -match '^\s*LANG\s*=' })
}

if ($Library) { return }

# Messages go straight to stdout: Write-Output inside a function that also returns a value would
# become part of that value.
function Say([string]$m) { [Console]::Out.WriteLine($m) }

# ------------------------------------------------------------------------------------------------
# Environment access. Everything below touches the real machine and is never called by tests.
# ------------------------------------------------------------------------------------------------

if (-not $IsWindows -and $PSVersionTable.PSEdition -eq 'Core') {
    Say 'UNEVALUABLE: this tool reads the Windows registry PATH; run it on Windows.'
    exit 2
}
if ([int]$Check.IsPresent + [int]$Apply.IsPresent -ne 1) {
    Say 'PRECONDITION: pass exactly one of -Check or -Apply (optionally with -Publish).'
    exit 2
}

$userKeyPath = 'Environment'
$machineKeyPath = 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'

function Read-RawPath([string]$Scope) {
    $hive = if ($Scope -eq 'User') { [Microsoft.Win32.Registry]::CurrentUser } else { [Microsoft.Win32.Registry]::LocalMachine }
    $key = $hive.OpenSubKey($(if ($Scope -eq 'User') { $userKeyPath } else { $machineKeyPath }), $false)
    if ($null -eq $key) { return @{ Value = ''; Kind = 'ExpandString'; Present = $false } }
    try {
        if ($key.GetValueNames() -notcontains 'Path') { return @{ Value = ''; Kind = 'ExpandString'; Present = $false } }
        $v = [string]$key.GetValue('Path', '', [Microsoft.Win32.RegistryValueOptions]::DoNotExpandEnvironmentNames)
        return @{ Value = $v; Kind = [string]$key.GetValueKind('Path'); Present = $true }
    } finally { $key.Dispose() }
}

function Write-RawPath([string]$Scope, [string]$Value, [string]$Kind) {
    $hive = if ($Scope -eq 'User') { [Microsoft.Win32.Registry]::CurrentUser } else { [Microsoft.Win32.Registry]::LocalMachine }
    $key = $hive.OpenSubKey($(if ($Scope -eq 'User') { $userKeyPath } else { $machineKeyPath }), $true)
    try { $key.SetValue('Path', $Value, [Microsoft.Win32.RegistryValueKind]$Kind) } finally { $key.Dispose() }
}

function Send-EnvironmentChanged {
    if (-not ('FleetPath.Native' -as [type])) {
        Add-Type -Namespace FleetPath -Name Native -MemberDefinition @'
[DllImport("user32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
public static extern IntPtr SendMessageTimeout(IntPtr hWnd, uint Msg, UIntPtr wParam, string lParam, uint fuFlags, uint uTimeout, out UIntPtr lpdwResult);
'@
    }
    $r = [UIntPtr]::Zero
    [void][FleetPath.Native]::SendMessageTimeout([IntPtr]0xffff, 0x1A, [UIntPtr]::Zero, 'Environment', 2, 5000, [ref]$r)
}

$existsReal = { param($p) try { Test-Path -LiteralPath $p -PathType Container } catch { $false } }
$expandReal = { param($t) [Environment]::ExpandEnvironmentVariables($t) }

function Measure-Machine {
    $mRaw = Read-RawPath 'Machine'
    $uRaw = Read-RawPath 'User'
    $mA = Get-PathAnalysis -Raw $mRaw.Value -Scope Machine -Exists $existsReal -Expand $expandReal
    $mKeys = @($mA | Where-Object Key | ForEach-Object Key)
    $uA = Get-PathAnalysis -Raw $uRaw.Value -Scope User -Exists $existsReal -Expand $expandReal -OtherScopeKeys $mKeys
    $mJoined = Join-ExpandedPath $mA
    $uJoined = Join-ExpandedPath $uA
    $fresh = (@($mJoined, $uJoined) | Where-Object { $_ }) -join ';'
    [pscustomobject]@{
        MachineRaw = $mRaw; UserRaw = $uRaw; MachineAnalysis = $mA; UserAnalysis = $uA
        MachineStats = (Get-ScopeStats $mA $mRaw.Value $mJoined); UserStats = (Get-ScopeStats $uA $uRaw.Value $uJoined)
        FreshPath = $fresh
    }
}

# The probe uses the PATH a NEW process would get (registry Machine;User), not this shell's PATH,
# because the failure this guards against is what a fresh service or child inherits.
function Invoke-WhereGitProbe([string]$FreshPath) {
    $saved = $env:Path
    try {
        $env:Path = $FreshPath
        $cmd = Join-Path $env:SystemRoot 'System32\cmd.exe'
        & $cmd /d /c 'where git' *> $null
        if ($LASTEXITCODE -eq 0) { 'PASS' } else { 'FAIL' }
    } catch { 'FAIL' } finally { $env:Path = $saved }
}

function Get-RunnerRows([string]$Root) {
    if (-not (Test-Path -LiteralPath $Root -PathType Container)) { return ,@() }
    $rows = foreach ($d in (Get-ChildItem -LiteralPath $Root -Directory -ErrorAction SilentlyContinue)) {
        if (-not (Test-Path -LiteralPath (Join-Path $d.FullName '.runner'))) { continue }
        $pathFile = Join-Path $d.FullName '.path'
        $envFile = Join-Path $d.FullName '.env'
        $pathChars = $null; $envLines = $null; $envText = $null
        if (Test-Path -LiteralPath $pathFile) { $pathChars = ([string](Get-Content -LiteralPath $pathFile -Raw)).Trim().Length }
        if (Test-Path -LiteralPath $envFile) {
            $envText = [string](Get-Content -LiteralPath $envFile -Raw)
            $envLines = @(($envText -split "`r?`n") | Where-Object { $_.Trim() }).Count
        }
        $svcName = $null
        $svcFile = Join-Path $d.FullName '.service'
        if (Test-Path -LiteralPath $svcFile) { $svcName = ([string](Get-Content -LiteralPath $svcFile -Raw)).Trim() }
        $runnerJson = $null
        try { $runnerJson = (Get-Content -LiteralPath (Join-Path $d.FullName '.runner') -Raw).TrimStart([char]0xFEFF) | ConvertFrom-Json } catch { }
        [pscustomobject]@{
            name = $d.Name; path_chars = $pathChars; env_lines = $envLines; env_has_lang = (Test-EnvHasLang $envText)
            Dir = $d.FullName; Service = $svcName
            Url = if ($runnerJson -and $runnerJson.PSObject.Properties['gitHubUrl']) { [string]$runnerJson.gitHubUrl } else { $null }
            Agent = if ($runnerJson -and $runnerJson.PSObject.Properties['agentName']) { [string]$runnerJson.agentName } else { $null }
        }
    }
    return ,@($rows)
}

function Get-ToolCommit([string]$Root) {
    try {
        $c = & git -C $Root rev-parse HEAD 2>$null
        if ($LASTEXITCODE -eq 0 -and $c) { return ([string]$c).Trim() }
    } catch { }
    return 'unknown'
}

function Write-Report($m, [string]$whereGit, [object[]]$runners, [string[]]$findings, [int]$total) {
    Say ("User PATH    : {0,6} chars  {1,3} segments  dead {2}  duplicate {3}  empty {4}  (dead .dotnet\tools: {5})" -f $m.UserStats.chars, $m.UserStats.segments, $m.UserStats.dead, $m.UserStats.duplicates, $m.UserStats.empty, $m.UserStats.dead_dotnet_tools)
    Say ("Machine PATH : {0,6} chars  {1,3} segments  dead {2}  duplicate {3}" -f $m.MachineStats.chars, $m.MachineStats.segments, $m.MachineStats.dead, $m.MachineStats.duplicates)
    Say ("Total (new process): {0} chars (limit {1}); cmd /d /c where git: {2}" -f $total, $MaxTotalChars, $whereGit)
    foreach ($r in @($runners)) {
        Say ("Runner {0}: .path {1}; .env {2}{3}" -f $r.name, $(if ($null -eq $r.path_chars) { 'MISSING' } else { "$($r.path_chars) chars" }), $(if ($null -eq $r.env_lines) { 'MISSING' } else { "$($r.env_lines) lines" }), $(if ($r.env_lines -and -not $r.env_has_lang) { ' (no LANG)' } else { '' }))
    }
    if (@($runners).Count -eq 0) { Say "Runners: none under $RunnerRoot" }
    $show = @($m.UserAnalysis | Where-Object { $_.Class -ne 'ok' }) + @($m.MachineAnalysis | Where-Object { $_.Class -ne 'ok' } | ForEach-Object { $_ | Add-Member -NotePropertyName ScopeTag -NotePropertyValue 'Machine' -PassThru -Force })
    if ($show.Count) {
        Say 'Entries that are not ok (this machine only; never published):'
        foreach ($e in ($show | Select-Object -First 40)) {
            $tag = if ($e.PSObject.Properties['ScopeTag']) { 'Machine' } else { 'User' }
            Say ("  {0,-7} {1,-15} {2}{3}" -f $tag, $e.Class, $e.Raw, $(if ($e.Removable) { '  [removable]' } else { '' }))
        }
        if ($show.Count -gt 40) { Say "  ... and $($show.Count - 40) more" }
    }
    Say ("VERDICT: {0}{1}" -f $(if ($findings.Count) { 'UNHEALTHY' } else { 'HEALTHY' }), $(if ($findings.Count) { ' - ' + ($findings -join ', ') } else { '' }))
}

function Get-CurrentState {
    $m = Measure-Machine
    $whereGit = Invoke-WhereGitProbe $m.FreshPath
    $runners = Get-RunnerRows $RunnerRoot
    $total = $m.FreshPath.Length
    $findings = Get-PathFindings -User $m.UserStats -Machine $m.MachineStats -TotalChars $total -MaxTotalChars $MaxTotalChars -WhereGit $whereGit -Runners $runners
    [pscustomobject]@{ M = $m; WhereGit = $whereGit; Runners = $runners; Total = $total; Findings = $findings }
}

function Test-Elevated {
    $p = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
    return $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Get-RunnerBusy($r) {
    # Returns $true / $false, or a string saying why it could not tell.
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { return 'gh not installed' }
    if (-not $r.Url -or -not $r.Agent) { return '.runner has no gitHubUrl/agentName' }
    $u = [uri]$r.Url
    $parts = @($u.AbsolutePath.Trim('/') -split '/')
    $api = if ($parts.Count -ge 2) { "repos/$($parts[0])/$($parts[1])/actions/runners?per_page=100" } else { "orgs/$($parts[0])/actions/runners?per_page=100" }
    $out = & gh api $api 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $out) { return "gh api $api failed" }
    $hit = @((($out | Out-String) | ConvertFrom-Json).runners | Where-Object { $_.name -eq $r.Agent })
    if ($hit.Count -ne 1) { return "runner '$($r.Agent)' not found by gh api" }
    return [bool]$hit[0].busy
}

function Invoke-Apply {
    $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
    $dir = Join-Path $env:LOCALAPPDATA "FleetPathRepair\$stamp"
    [void](New-Item -ItemType Directory -Force -Path $dir)
    $before = Get-CurrentState
    $m = $before.M
    $elevated = Test-Elevated
    $actions = [System.Collections.Generic.List[string]]::new()
    $failed = $false

    # Back up both scopes, raw and with their registry value kind, before any write.
    @{ scope = 'User'; kind = $m.UserRaw.Kind; present = $m.UserRaw.Present; value = $m.UserRaw.Value } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $dir 'user-path.backup.json') -Encoding utf8
    @{ scope = 'Machine'; kind = $m.MachineRaw.Kind; present = $m.MachineRaw.Present; value = $m.MachineRaw.Value } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $dir 'machine-path.backup.json') -Encoding utf8
    Say "Backups: $dir"

    $changed = $false
    $uRemove = @($m.UserAnalysis | Where-Object Removable)
    if ($uRemove.Count) {
        try {
            Write-RawPath 'User' (Get-RepairedPath $m.UserAnalysis) $m.UserRaw.Kind
            $actions.Add("user: removed $($uRemove.Count) entries ($((@($uRemove | Group-Object Class | ForEach-Object { "$($_.Name)=$($_.Count)" })) -join ', '))")
            $changed = $true
        } catch { $failed = $true; $actions.Add("user: WRITE FAILED: $($_.Exception.Message)") }
    } else { $actions.Add('user: nothing removable') }

    $mRemove = @($m.MachineAnalysis | Where-Object Removable)
    if ($mRemove.Count -and $elevated) {
        try {
            Write-RawPath 'Machine' (Get-RepairedPath $m.MachineAnalysis) $m.MachineRaw.Kind
            $actions.Add("machine: removed $($mRemove.Count) dead entries")
            $changed = $true
        } catch { $failed = $true; $actions.Add("machine: WRITE FAILED: $($_.Exception.Message)") }
    } elseif ($mRemove.Count) { $actions.Add("machine: $($mRemove.Count) dead entries LEFT IN PLACE - not elevated; rerun -Apply as Administrator to remove them") }
    else { $actions.Add('machine: nothing removable') }
    if ($changed) { Send-EnvironmentChanged }

    $after = Measure-Machine
    $me = [Security.Principal.WindowsIdentity]::GetCurrent().Name
    foreach ($r in $before.Runners) {
        $svc = $null
        if ($r.Service) { $svc = Get-CimInstance Win32_Service -Filter ("Name='{0}'" -f ($r.Service -replace "'", "''")) -ErrorAction SilentlyContinue }
        $startName = if ($svc) { [string]$svc.StartName } else { '' }
        $sameUser = $startName -and (($startName -ieq $me) -or ($startName -ieq (".\" + ($me -split '\\')[-1])))
        if (-not $sameUser) {
            $actions.Add("runner $($r.name): .path NOT rewritten - service runs as '$startName', this shell is '$me'; the User PATH it needs is that account's")
            continue
        }
        $pathFile = Join-Path $r.Dir '.path'
        try {
            if (Test-Path -LiteralPath $pathFile) { Copy-Item -LiteralPath $pathFile -Destination (Join-Path $dir "runner-$($r.name).path.backup") }
            [IO.File]::WriteAllText($pathFile, $after.FreshPath, [Text.UTF8Encoding]::new($false))
            $actions.Add("runner $($r.name): .path rewritten ($($after.FreshPath.Length) chars)")
        } catch { $failed = $true; $actions.Add("runner $($r.name): .path WRITE FAILED: $($_.Exception.Message)"); continue }
        if ($null -eq $r.env_lines -or -not $r.env_has_lang) { $actions.Add("runner $($r.name): .env missing or without LANG - not edited; see SELF-HOSTED-WINDOWS-RUNNER.md host prerequisites") }
        if (-not $elevated) { $actions.Add("runner $($r.name): restart SKIPPED - needs Administrator"); continue }
        $busy = Get-RunnerBusy $r
        if ($busy -is [bool] -and -not $busy) {
            try { Restart-Service -Name $r.Service -ErrorAction Stop; $actions.Add("runner $($r.name): service restarted (idle per gh api)") }
            catch { $failed = $true; $actions.Add("runner $($r.name): restart FAILED: $($_.Exception.Message)") }
        } elseif ($busy -is [bool]) { $actions.Add("runner $($r.name): restart SKIPPED - runner is busy; restart '$($r.Service)' when idle") }
        else { $actions.Add("runner $($r.name): restart SKIPPED - could not read busy ($busy); restart '$($r.Service)' when idle") }
    }

    $post = Get-CurrentState
    $receipt = [ordered]@{
        schema = 'fleet-path-repair-receipt.v1'; utc = $stamp; machine = $env:COMPUTERNAME; elevated = $elevated
        before = [ordered]@{ user = $before.M.UserStats; machine = $before.M.MachineStats; total = $before.Total; where_git = $before.WhereGit; findings = $before.Findings }
        removed_user = @($uRemove | ForEach-Object { [ordered]@{ class = $_.Class; entry = $_.Raw } })
        removed_machine = @($(if ($elevated) { $mRemove | ForEach-Object { [ordered]@{ class = $_.Class; entry = $_.Raw } } }))
        actions = $actions
        after = [ordered]@{ user = $post.M.UserStats; machine = $post.M.MachineStats; total = $post.Total; where_git = $post.WhereGit; findings = $post.Findings }
        failed = $failed
    }
    $receipt | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $dir 'receipt.json') -Encoding utf8
    foreach ($a in $actions) { Say "  $a" }
    Say "Receipt: $(Join-Path $dir 'receipt.json')"
    Say '--- after ---'
    Write-Report $post.M $post.WhereGit $post.Runners $post.Findings $post.Total
    return [pscustomobject]@{ State = $post; Failed = $failed }
}

function Publish-Ack($state) {
    if (-not (Test-Path -LiteralPath (Join-Path $BusRoot '.git'))) { Say "PUBLISH FAILED: $BusRoot is not a git checkout of the bus"; return 4 }
    $now = (Get-Date).ToUniversalTime()
    $record = New-AckRecord -MachineName $env:COMPUTERNAME -NowUtc $now -ToolCommit (Get-ToolCommit $BusRoot) `
        -User $state.M.UserStats -Machine $state.M.MachineStats -TotalChars $state.Total -WhereGit $state.WhereGit `
        -Runners $state.Runners -Findings $state.Findings
    $rel = "path-health/$($record.machine).json"
    $target = Join-Path $BusRoot $rel
    $prev = if (Test-Path -LiteralPath $target) { Get-Content -LiteralPath $target -Raw } else { $null }
    $need = Test-AckPublishNeeded -PreviousRaw $prev -Record $record -NowUtc $now -RefreshHours $RefreshHours
    if (-not $need.Publish) { Say "ACK UNCHANGED: $rel ($($need.Reason)); not pushing a cadence commit."; return 0 }
    [void](New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target))
    [IO.File]::WriteAllText($target, ($record | ConvertTo-Json -Depth 6) + "`n", [Text.UTF8Encoding]::new($false))
    & git -C $BusRoot add -- $rel *> $null
    $staged = @(& git -C $BusRoot diff --cached --name-only)
    if ($staged.Count -eq 0) { Say "ACK UNCHANGED: $rel bytes identical"; return 0 }
    if ($staged.Count -ne 1 -or $staged[0] -ne $rel) {
        & git -C $BusRoot reset -q -- $rel *> $null
        Say "PUBLISH FAILED: staging area held other files ($($staged -join ', ')); refusing to commit."; return 4
    }
    & git -C $BusRoot -c commit.gpgsign=false commit -q -m "path-health: $($record.machine) $($record.verdict) ($($need.Reason))" *> $null
    if ($LASTEXITCODE -ne 0) { Say 'PUBLISH FAILED: commit failed (is git user.name/user.email set?)'; return 4 }
    if ($NoPush) { Say "ACK COMMITTED, NOT PUSHED (-NoPush): $rel verdict=$($record.verdict) ($($need.Reason))"; return 0 }
    & git -C $BusRoot push -q origin HEAD *> $null
    if ($LASTEXITCODE -ne 0) {
        $branch = (& git -C $BusRoot rev-parse --abbrev-ref HEAD).Trim()
        & git -C $BusRoot pull -q --rebase origin $branch *> $null
        if ($LASTEXITCODE -ne 0) { Say 'PUBLISH FAILED: push rejected and rebase failed; ack committed locally only'; return 4 }
        & git -C $BusRoot push -q origin HEAD *> $null
        if ($LASTEXITCODE -ne 0) { Say 'PUBLISH FAILED: push rejected twice; ack committed locally only'; return 4 }
    }
    Say "ACK PUBLISHED: $rel verdict=$($record.verdict) ($($need.Reason))"
    return 0
}

try {
    if ($Apply) {
        $res = Invoke-Apply
        $state = $res.State
        $code = if ($res.Failed) { 2 } elseif ($state.Findings.Count) { 1 } else { 0 }
    } else {
        $state = Get-CurrentState
        if ($Json) {
            New-AckRecord -MachineName $env:COMPUTERNAME -NowUtc (Get-Date).ToUniversalTime() -ToolCommit (Get-ToolCommit $BusRoot) -User $state.M.UserStats -Machine $state.M.MachineStats -TotalChars $state.Total -WhereGit $state.WhereGit -Runners $state.Runners -Findings $state.Findings | ConvertTo-Json -Depth 6 | ForEach-Object { Say $_ }
        } else {
            Write-Report $state.M $state.WhereGit $state.Runners $state.Findings $state.Total
            if ($state.Findings.Count) { Say 'Repair (owner''s call): pwsh -NoProfile -File tools/Repair-MachinePath.ps1 -Apply   (Administrator only if Machine PATH has dead entries or a runner must restart)' }
        }
        $code = if ($state.Findings.Count) { 1 } else { 0 }
    }
    if ($Publish) {
        $p = Publish-Ack $state
        if ($p -ne 0) { $code = $p }   # a failed ack must show, even on an UNHEALTHY machine
    }
    exit $code
} catch {
    Say "UNEVALUABLE: $($_.Exception.Message)"
    exit 2
}
