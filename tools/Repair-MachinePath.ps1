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
            empty entries, a `cmd.exe /d /c git --version` probe run with the PATH a new process would
            get, and every self-hosted runner under -RunnerRoot (its .path length, its .env).
            Exit 0 HEALTHY, 1 UNHEALTHY, 2 UNEVALUABLE.

  -Apply    Backs up first, then removes dead, empty and duplicate entries from the User PATH.
            It touches the Machine PATH only when elevated, and only to remove dead entries.
            It never removes an entry whose folder exists, a UNC entry, an entry with an
            unexpanded %VAR%, or an entry on a drive that is not mounted. It then rewrites a
            runner's .path from the repaired PATH only when that .path is missing, empty, over
            the limit, or still lists a dead entry this repair removed (a hand-ordered .path is
            kept), and only when the runner service runs as the current user. It restarts that service only when it is idle (GitHub `busy` = false,
            read with `gh api`) and the shell is elevated; otherwise it skips the restart and says
            why. Writes a receipt and the backups under %LOCALAPPDATA%\FleetPathRepair\<utc>\.
            Exit is the post-repair -Check verdict, or 2 if a write failed.

  -Publish  Writes path-health/<MACHINE>.json in -BusRoot (counts and verdict only: no paths, no
            user names), commits that one file and pushes it to master. It pushes only when
            the content changed or the published record is older than -RefreshHours (law 3).
            The record is published whatever the verdict: an UNHEALTHY ack is still an ack.
            -NoPush rehearses: commits, then undoes its own commit (exit 5, never an ack). A successful publish (or a confirmed
            unchanged one) exits 10 when HEALTHY and 11 when UNHEALTHY; a failed publish exits 4,
            and nothing is published after a failed -Apply (exit stays 2). The ack commit is always
            built on origin's tip (a checkout behind origin is fast-forwarded; a rejected push is
            rebuilt once, never text-merged); a failed publish
            and takes its own ack commit back off the checkout. It refuses a detached HEAD, a
            branch other than master (unless -AllowBranch), a non-empty index, and any push whose
            single commit touches anything but the ack file.

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
    [switch]$AllowBranch,
    [string]$BusRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$RunnerRoot = 'C:\actions-runners',
    [int]$MaxTotalChars = 4096,
    [int]$RefreshHours = 24,
    [switch]$Json,
    [switch]$Library
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Test-AckRecord: the ack validator the reader uses, so publisher and reader judge an ack alike.
. (Join-Path $PSScriptRoot 'PathHealthRecord.ps1')

$script:AckSchema = 'fleet-path-health.v1'

# ------------------------------------------------------------------------------------------------
# Pure functions. No registry, no filesystem, no process: everything arrives as an argument.
# ------------------------------------------------------------------------------------------------

function Split-PathList([AllowNull()][AllowEmptyString()][string]$Raw) {
    if ($null -eq $Raw -or $Raw -eq '') { return ,@() }
    # Split on semicolons OUTSIDE double quotes: Windows reads `"C:\a;b"` as one entry, and a plain
    # split would make a dead-looking fragment of a live folder. Quotes stay in the segment (the
    # analysis trims them), so the repaired PATH keeps the entry exactly as written.
    $out = [System.Collections.Generic.List[string]]::new()
    $sb = [System.Text.StringBuilder]::new()
    $inQuote = $false
    foreach ($ch in $Raw.ToCharArray()) {
        if ($ch -eq '"') { $inQuote = -not $inQuote; [void]$sb.Append($ch) }
        elseif ($ch -eq ';' -and -not $inQuote) { $out.Add($sb.ToString()); [void]$sb.Clear() }
        else { [void]$sb.Append($ch) }
    }
    $out.Add($sb.ToString())
    return ,@($out.ToArray())
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
        [string[]]$OtherScopeKeys = @(),
        [string[]]$PendingKeys = @(),
        [string[]]$OtherScopeVarKeys = @()   # Machine keys that came from %VAR% entries
    )
    $other = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    foreach ($k in $OtherScopeKeys) { [void]$other.Add($k) }
    $otherVar = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    foreach ($k in $OtherScopeVarKeys) { [void]$otherVar.Add($k) }
    $seenVar = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    $pending = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    foreach ($k in $PendingKeys) { [void]$pending.Add($k) }
    $seen = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    $rows = [System.Collections.Generic.List[object]]::new()
    $i = 0
    foreach ($seg in (Split-PathList $Raw)) {
        $expanded = [string](& $Expand $seg)
        $trimmed = $expanded.Trim().Trim('"').Trim()
        $key = if ($trimmed) { Get-PathKey $trimmed } else { '' }
        # An entry written with a %VAR% or with quotes is "indirect": Windows' own search (SearchPathW,
        # where.exe, PowerShell) may not resolve it the way cmd.exe does, so it never stands as the
        # surviving copy that makes a plain twin removable.
        $indirect = ($seg -match '%') -or $seg.Contains('"')
        $class = 'ok'
        # A %VAR% that expands to nothing in THIS process is not an empty entry: the variable may be
        # set for every other session. Only a segment that is empty as written is 'empty'.
        if (-not $trimmed -and $seg -match '%') { $class = 'unresolved' }
        elseif (-not $trimmed) { $class = 'empty' }
        elseif ($trimmed.StartsWith('\\')) { $class = 'unc' }
        elseif ($trimmed -match '%[^%;]+%') { $class = 'unresolved' }
        elseif ($trimmed.Contains(';')) { $class = 'multi' }   # a %VAR% that expands to several folders: never one folder's verdict
        elseif ($trimmed -notmatch '^[A-Za-z]:\\') { $class = 'relative' }   # resolved against the current directory: never this tool's verdict
        elseif ($trimmed -match '^[A-Za-z]:' -and ($true -ne (& $Exists ($trimmed.Substring(0, 2) + '\')))) { $class = 'drive-absent' }
        elseif ($trimmed -match '\\Sysnative(\\|$)') { $class = 'unreadable' }   # WOW64 alias: invisible to a 64-bit process, never dead
        else {
            # $Exists returns $true, $false, or $null for "could not tell" (access denied). Only a
            # definite $false is dead, and only an entry written as an absolute path is removable:
            # a %VAR% entry was expanded with this process's environment, which a harness may have
            # overridden, so its deadness is reported, never acted on.
            $e = & $Exists $trimmed
            if ($null -eq $e) { $class = 'unreadable' }
            elseif (-not $e) {
                if ($pending.Contains($key)) { $class = 'pending' }
                elseif ($seg -match '%') { $class = 'dead-var' }
                else { $class = 'dead' }
            }
            # A duplicate verdict also rests on expansion and quoting. Only a plain LITERAL entry
            # repeating a plain LITERAL entry is removable; a %VAR% or quoted entry on either side is
            # reported, not removed.
            elseif ($Scope -eq 'User' -and $other.Contains($key)) { $class = $(if ($indirect) { 'duplicate-var' } else { 'cross-duplicate' }) }
            elseif ($Scope -eq 'User' -and $otherVar.Contains($key)) { $class = 'duplicate-var' }
            elseif ($seen.Contains($key)) { $class = $(if ($indirect) { 'duplicate-var' } else { 'duplicate' }) }
            elseif ($seenVar.Contains($key)) { $class = 'duplicate-var' }
        }
        if ($key -and $class -in @('ok', 'unc', 'unresolved', 'multi', 'relative', 'drive-absent', 'unreadable', 'pending', 'dead-var')) {
            if ($indirect) { [void]$seenVar.Add($key) } else { [void]$seen.Add($key) }
        }
        $removable = if ($Scope -eq 'User') { $class -in @('empty', 'dead', 'duplicate', 'cross-duplicate') } else { $class -eq 'dead' }
        if ($seg -match '%') { $removable = $false }   # backstop: an entry written with a %VAR% is never removed, whatever its class
        if ($seg.Contains('"')) { $removable = $false }   # any quoted entry, balanced or not: reported, never removed
        $rows.Add([pscustomobject]@{
            # Written keeps every character a new process receives (quotes and whitespace padding
            # included): it is what is measured and what a runner .path is rewritten from.
            Index = $i; Raw = $seg; Expanded = $trimmed; Written = $expanded; Key = $key; Class = $class; Removable = $removable
            DotnetTools = ($trimmed -match '\\\.dotnet\\tools$')
        })
        $i++
    }
    return ,$rows.ToArray()
}

function Test-MalformedQuote([string]$Seg) {
    if (-not $Seg.Contains('"')) { return $false }
    return ($Seg -notmatch '^\s*"[^"]*"\s*$')
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
        duplicates        = @($a | Where-Object { $_.Class -in @('duplicate', 'cross-duplicate', 'duplicate-var') }).Count
        empty             = @($a | Where-Object Class -eq 'empty').Count
        unverifiable      = @($a | Where-Object { $_.Class -in @('unc', 'unresolved', 'multi', 'relative', 'drive-absent', 'unreadable', 'dead-var') }).Count
        pending           = @($a | Where-Object Class -eq 'pending').Count
        dead_dotnet_tools = @($a | Where-Object { $_.Class -eq 'dead' -and $_.DotnetTools }).Count
        removable         = @($a | Where-Object Removable).Count
        # Malformed quoting: an odd quote count, or quotes that do not wrap the whole entry (two stray
        # quotes can balance each other and fold dead entries into one unjudgeable segment).
        unbalanced_quotes = @($a | Where-Object { Test-MalformedQuote ([string]$_.Raw) }).Count
    }
}

function Join-ExpandedPath([object[]]$Analysis) {
    # Every segment, empty ones included, with its quotes kept: the length a new process really gets,
    # and a value that, written to a runner's .path, keeps a quoted entry that contains a semicolon one entry.
    return (@($Analysis | ForEach-Object { [string]$_.Written }) -join ';')
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
    # An unbalanced quote folds every later entry into one segment this tool cannot judge, and it
    # breaks cmd.exe's PATH search for those entries: never a HEALTHY machine.
    if ($User.Contains('unbalanced_quotes') -and $User.unbalanced_quotes -gt 0) { $f.Add("user-unbalanced-quote:$($User.unbalanced_quotes)") }
    if ($Machine.Contains('unbalanced_quotes') -and $Machine.unbalanced_quotes -gt 0) { $f.Add("machine-unbalanced-quote:$($Machine.unbalanced_quotes)") }
    if ($WhereGit -eq 'FAIL') { $f.Add('cmd-where-git-failed') }
    foreach ($r in @($Runners)) {
        if ($null -eq $r.path_chars) { $f.Add("runner-path-missing:$($r.label)") }
        elseif ($r.path_chars -eq 0) { $f.Add("runner-path-empty:$($r.label)") }
        elseif ($r.path_chars -gt $MaxTotalChars) { $f.Add("runner-path-over-${MaxTotalChars}:$($r.label):$($r.path_chars)") }
        if ($null -eq $r.env_lines) { $f.Add("runner-env-missing:$($r.label)") }
        elseif (-not $r.env_has_lang) { $f.Add("runner-env-no-lang:$($r.label)") }
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
        [ordered]@{ label = [string]$r.label; path_chars = $r.path_chars; env_lines = $r.env_lines; env_has_lang = [bool]$r.env_has_lang }
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
    # The previous record must pass the READER's validator (shared, PathHealthRecord.ps1): one the
    # reader would call UNEVALUABLE (bad JSON, non-object root, repeated key, wrong schema/machine/
    # verdict case, non-Z or future stamp, findings that contradict the verdict) is republished,
    # never "unchanged".
    try { $valid = Test-AckRecord -Raw $PreviousRaw -FileMachine ([string]$Record['machine']) -NowUtc $NowUtc }
    catch { return @{ Publish = $true; Reason = 'previous-invalid' } }
    try { $prev = $PreviousRaw | ConvertFrom-Json -AsHashtable -ErrorAction Stop } catch { return @{ Publish = $true; Reason = 'previous-invalid' } }
    $strip = {
        param($h)
        $c = [ordered]@{}
        foreach ($k in @($h.Keys | Sort-Object)) { if ($k -cnotin @('published_utc', 'tool_commit')) { $c[$k] = $h[$k] } }
        ($c | ConvertTo-Json -Depth 6 -Compress)
    }
    $prevCanon = & $strip $prev
    $newCanon = & $strip (($Record | ConvertTo-Json -Depth 6) | ConvertFrom-Json -AsHashtable)
    if ($prevCanon -cne $newCanon) { return @{ Publish = $true; Reason = 'changed' } }   # case-sensitive
    $age = ($NowUtc - $valid.PublishedUtc).TotalHours
    if ($age -lt $RefreshHours) { return @{ Publish = $false; Reason = ('unchanged, {0:n1} h old' -f $age) } }
    return @{ Publish = $true; Reason = "refresh:${RefreshHours}h" }
}

function Test-EnvHasLang([AllowNull()][string]$EnvText) {
    if ($null -eq $EnvText) { return $false }
    return [bool](($EnvText -split "`r?`n") | Where-Object { $_ -match '^\s*LANG\s*=\s*\S' })   # LANG= with no value is no LANG
}

<#
Canonical per-user folders that installers put on PATH before they exist (created on first use):
the .NET SDK writes `%USERPROFILE%\.dotnet\tools` raw, and Node's installer adds `%APPDATA%\npm`.
Missing, they are 'pending', never dead: removing one hides every later global tool, because the
installer's own sentinel says it already added the entry.
#>
function Get-PendingKeys([scriptblock]$Expand) {
    return ,@(@('%USERPROFILE%\.dotnet\tools', '%APPDATA%\npm') | ForEach-Object { Get-PathKey ([string](& $Expand $_)) })
}

# Union of the pending keys under several expanders, FLAT: one string per key. Concatenating two
# `,@(...)` results with + builds an array of arrays, and binding that to [string[]] joins each
# inner array into one space-separated string that matches no key.
function Get-PendingKeySet([scriptblock[]]$Expanders) {
    $set = [System.Collections.Generic.List[string]]::new()
    foreach ($e in @($Expanders)) {
        $keys = Get-PendingKeys $e   # assigned, not @(...): @() would wrap the ,@() result once more
        foreach ($k in $keys) { if ($k -is [string] -and $k -and -not $set.Contains($k)) { $set.Add($k) } }
    }
    return ,([string[]]$set.ToArray())
}

# Qualify a service StartName for SID resolution. `.\name` is a LOCAL account (COMPUTER\name), never
# a domain account of the same short name. Service-only identities (LocalSystem, NT AUTHORITY\...)
# and empty names return $null: no user PATH of ours belongs to them.
function ConvertTo-QualifiedAccount([AllowNull()][string]$StartName, [string]$ComputerName) {
    if (-not $StartName) { return $null }
    if ($StartName -ieq 'LocalSystem' -or $StartName -match '^NT AUTHORITY\\' -or $StartName -match '^NT SERVICE\\') { return $null }
    if ($StartName.StartsWith('.\')) { return "$ComputerName\$($StartName.Substring(2))" }
    if ($StartName -match '^[^\\@]+@[^\\@]+$') { return $StartName }   # UPN
    if ($StartName -notmatch '\\') { return "$ComputerName\$StartName" }
    return $StartName
}

# Same account iff both resolve to the same SID. Resolution failure is "not the same" (fail closed).
# $Resolve: param($qualifiedName) -> SID string or $null.
function Test-SameServiceAccount([AllowNull()][string]$StartName, [string]$MySid, [string]$ComputerName, [scriptblock]$Resolve) {
    $q = ConvertTo-QualifiedAccount $StartName $ComputerName
    if (-not $q -or -not $MySid) { return $false }
    $sid = & $Resolve $q
    return ([bool]$sid -and $sid -eq $MySid)
}

<#
Rewrite a runner's .path only when it is missing, over the limit, or still carries an entry this
repair removed. Otherwise leave it: a hand-ordered .path (Git Bash ahead of WSL) is not ours to flatten.
#>
function Get-RunnerPathAction($PathText,   # untyped: [string] would turn a missing file ($null) into ''
    [string[]]$RemovedKeys = @(), [int]$MaxChars = 4096) {
    if ($null -eq $PathText) { return 'rewrite:missing' }
    $t = $PathText.Trim()
    if ($t.Length -eq 0) { return 'rewrite:empty' }
    if ($PathText.Length -gt $MaxChars) { return 'rewrite:over-limit' }   # untrimmed: padding counts
    $removed = [System.Collections.Generic.HashSet[string]]::new([string[]]@($RemovedKeys), [StringComparer]::Ordinal)
    # Same quote-aware split as the PATH itself. A quoted or unbalanced segment is never matched:
    # its fragments are not entries, so they can never make a healthy .path look stale.
    foreach ($seg in (Split-PathList $t)) {
        $s = $seg.Trim()
        if (-not $s -or $s.Contains('"')) { continue }
        if ($removed.Contains((Get-PathKey $s))) { return 'rewrite:holds-removed-entry' }
    }
    return 'keep'
}

# Keys whose removal makes a runner .path stale: DEAD entries only. A removed duplicate's folder
# still exists, so a .path that lists it is not broken.
function Get-StaleRunnerKeys([object[]]$RemovedRows) {
    return ,@(@($RemovedRows) | Where-Object { $_ -and $_.Key -and $_.Class -eq 'dead' } | ForEach-Object Key)
}

# Restart only when elevated AND GitHub says the runner is idle. $Busy is $true/$false or a string
# saying why busy could not be read.
function Get-RestartDecision([bool]$Elevated, $Busy) {
    if (-not $Elevated) { return 'skip:needs-administrator' }
    if ($Busy -is [bool]) { if ($Busy) { return 'skip:busy' } else { return 'restart' } }
    return "skip:busy-unknown ($Busy)"
}


# Final exit code. A successful publish gets its OWN codes (10 acked HEALTHY, 11 acked UNHEALTHY),
# because pwsh -File exits 1 on a parse or parameter-binding error too: "exit 1" alone cannot prove
# an ack was published. A failed publish (4) shows even on an UNHEALTHY machine.
function Get-FinalExitCode([int]$CheckCode, [bool]$Published, [int]$PublishCode = 0) {
    if (-not $Published) { return $CheckCode }
    if ($PublishCode -ne 0) { return $PublishCode }
    if ($CheckCode -in 0, 1) { return 10 + $CheckCode }
    return $CheckCode
}

# Git-only helpers for the publish step. They run git against -BusRoot alone, so tests drive them
# on a throwaway repository with a throwaway bare origin.
# Why the ack push must not happen, or $null. The push must carry the ack commit and nothing else:
# a board's own master checkout may hold local, unreviewed commits.
function Get-AckPushBlocker([string]$BusRoot, [string]$Branch, [string]$Rel) {
    & git -C $BusRoot fetch -q origin $Branch *> $null
    if ($LASTEXITCODE -ne 0) { return "cannot fetch origin/$Branch" }
    $ahead = "$(& git -C $BusRoot rev-list --count "refs/remotes/origin/${Branch}..HEAD" 2>$null)".Trim()
    if ($ahead -ne '1') { return "HEAD is $ahead commits ahead of origin/$Branch, not 1" }
    $files = @(& git -C $BusRoot diff-tree --no-commit-id --name-only -r HEAD 2>$null)
    if ($files.Count -ne 1 -or $files[0] -ne $Rel) { return "HEAD commit touches $($files -join ', '), not exactly $Rel" }
    return $null
}

# The ack as origin holds it: @{ Ok; Raw } (Raw $null when origin has none). The previous record is
# always read from the REMOTE, never the working tree: a file left on disk by an earlier failed run
# would otherwise make "unchanged" true while nothing is on the bus.
function Get-RemoteAckRaw([string]$BusRoot, [string]$Branch, [string]$Rel) {
    & git -C $BusRoot fetch -q origin $Branch *> $null
    if ($LASTEXITCODE -ne 0) { return @{ Ok = $false; Raw = $null } }
    & git -C $BusRoot cat-file -e "refs/remotes/origin/${Branch}:$Rel" *> $null
    if ($LASTEXITCODE -ne 0) { return @{ Ok = $true; Raw = $null } }
    $raw = (& git -C $BusRoot show "refs/remotes/origin/${Branch}:$Rel" 2>$null) -join "`n"
    if ($LASTEXITCODE -ne 0) { return @{ Ok = $false; Raw = $null } }
    return @{ Ok = $true; Raw = $raw }
}

# Take our own ack commit back off the checkout AND restore the ack file to the new HEAD's copy
# (or remove it if HEAD has none), so a failed publish leaves no ack on disk for a rerun to mistake
# for a published one. Only a HEAD that is exactly our one-file ack commit is undone.
# OWNERSHIP: HEAD is ours only if it is NOT reachable from origin/<Branch> (so no publisher's pushed
# commit, including an equivalent one a rebase dropped ours in favour of, is ever reset), it touches
# exactly the ack file, and its copy of that file is the exact blob this run wrote ($BlobOid).
function Undo-AckCommit([string]$BusRoot, [string]$Rel, [string]$Machine, [string]$Branch, [string]$BlobOid) {
    $files = @(& git -C $BusRoot diff-tree --no-commit-id --name-only -r HEAD 2>$null)
    $subj = "$(& git -C $BusRoot log -1 --format=%s HEAD 2>$null)".Trim()
    & git -C $BusRoot merge-base --is-ancestor HEAD "refs/remotes/origin/$Branch" *> $null
    $onOrigin = ($LASTEXITCODE -eq 0)
    $headBlob = "$(& git -C $BusRoot rev-parse -q --verify "HEAD:$Rel" 2>$null)".Trim()
    if (-not $onOrigin -and $BlobOid -and $headBlob -eq $BlobOid -and $files.Count -eq 1 -and $files[0] -eq $Rel -and $subj.StartsWith("path-health: $Machine ")) {
        & git -C $BusRoot reset -q --mixed HEAD~1 *> $null
        if ($LASTEXITCODE -eq 0) {
            & git -C $BusRoot cat-file -e "HEAD:$Rel" *> $null
            if ($LASTEXITCODE -eq 0) { & git -C $BusRoot checkout -q HEAD -- $Rel *> $null }
            else { Remove-Item -LiteralPath (Join-Path $BusRoot $Rel) -Force -ErrorAction SilentlyContinue }
            return 'ack commit undone locally'
        }
    }
    return 'ack commit left in place (HEAD is not the ack commit)'
}

if ($Library) { return }

# Any terminating error outside the main try (a bad -BusRoot, a failed type load) is UNEVALUABLE,
# never a bare pwsh exit 1 that a caller could read as a verdict.
trap { [Console]::Out.WriteLine("UNEVALUABLE: $($_.Exception.Message)"); exit 2 }

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
if ([Environment]::Is64BitOperatingSystem -and -not [Environment]::Is64BitProcess) {
    # WOW64 redirects System32 for a 32-bit process, so 64-bit-only folders would look dead.
    Say 'UNEVALUABLE: run from a 64-bit pwsh; a 32-bit process sees a redirected System32.'
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

# $true exists, $false definitely absent, $null could not tell (access denied, I/O error): Test-Path
# alone returns $false for a folder it cannot read, which would class a live entry as dead.
$existsReal = {
    param($p)
    try { $i = Get-Item -LiteralPath $p -Force -ErrorAction Stop; return [bool]$i.PSIsContainer }
    catch [System.Management.Automation.ItemNotFoundException] { return $false }
    catch { return $null }
}
$expandReal = { param($t) [Environment]::ExpandEnvironmentVariables($t) }
# Pending folders are named from the user's token (GetFolderPath), not from $env:USERPROFILE /
# $env:APPDATA, which a harness may have overridden. Both spellings count.
$pendingReal = Get-PendingKeySet @(
    $expandReal,
    { param($t) $t.Replace('%USERPROFILE%', [Environment]::GetFolderPath('UserProfile')).Replace('%APPDATA%', [Environment]::GetFolderPath('ApplicationData')) }
)

function Measure-Machine {
    $mRaw = Read-RawPath 'Machine'
    $uRaw = Read-RawPath 'User'
    $mA = Get-PathAnalysis -Raw $mRaw.Value -Scope Machine -Exists $existsReal -Expand $expandReal -PendingKeys $pendingReal
    # Plain literal Machine entries only; %VAR% and quoted ones are indirect (see Get-PathAnalysis).
    $mKeys = @($mA | Where-Object { $_.Key -and $_.Raw -notmatch '%' -and -not $_.Raw.Contains('"') } | ForEach-Object Key)
    $mVarKeys = @($mA | Where-Object { $_.Key -and ($_.Raw -match '%' -or $_.Raw.Contains('"')) } | ForEach-Object Key)
    $uA = Get-PathAnalysis -Raw $uRaw.Value -Scope User -Exists $existsReal -Expand $expandReal -OtherScopeKeys $mKeys -OtherScopeVarKeys $mVarKeys -PendingKeys $pendingReal
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
    $savedNoCwd = $env:NoDefaultCurrentDirectoryInExePath
    try {
        $env:Path = $FreshPath
        # Without this, cmd.exe searches the current directory before PATH: a git.bat in the folder
        # the owner ran from would pass the probe (and run).
        $env:NoDefaultCurrentDirectoryInExePath = '1'
        $cmd = Join-Path $env:SystemRoot 'System32\cmd.exe'
        # cmd.exe's own command search, not where.exe: where.exe skips a quoted PATH entry that
        # cmd.exe (and so every cmd child) honours.
        & $cmd /d /c 'git --version <NUL' *> $null
        if ($LASTEXITCODE -eq 0) { 'PASS' } else { 'FAIL' }
    } catch { 'FAIL' } finally { $env:Path = $saved; $env:NoDefaultCurrentDirectoryInExePath = $savedNoCwd }
}

function Get-RunnerRows([string]$Root) {
    if (-not (Test-Path -LiteralPath $Root -PathType Container)) { return ,@() }
    $n = 0
    $rows = foreach ($d in (Get-ChildItem -LiteralPath $Root -Directory -ErrorAction SilentlyContinue | Sort-Object Name)) {
        if (-not (Test-Path -LiteralPath (Join-Path $d.FullName '.runner'))) { continue }
        $n++
        $pathFile = Join-Path $d.FullName '.path'
        $envFile = Join-Path $d.FullName '.env'
        $pathChars = $null; $envLines = $null; $envText = $null
        if (Test-Path -LiteralPath $pathFile) {
            # Untrimmed, like the registry total: whitespace padding is length the runner really gets.
            $pathText = [string](Get-Content -LiteralPath $pathFile -Raw)
            $pathChars = if ($pathText.Trim().Length -eq 0) { 0 } else { $pathText.Length }
        }
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
            # `label` is what travels: a runner folder may be named after an account (law 4).
            name = $d.Name; label = "runner-$n"; path_chars = $pathChars; env_lines = $envLines; env_has_lang = (Test-EnvHasLang $envText)
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
    Say ("Total (new process): {0} chars (limit {1}); cmd /d /c git --version: {2}" -f $total, $MaxTotalChars, $whereGit)
    foreach ($r in @($runners)) {
        Say ("Runner {0} (published as {1}): .path {2}; .env {3}{4}" -f $r.name, $r.label, $(if ($null -eq $r.path_chars) { 'MISSING' } else { "$($r.path_chars) chars" }), $(if ($null -eq $r.env_lines) { 'MISSING' } else { "$($r.env_lines) lines" }), $(if ($r.env_lines -and -not $r.env_has_lang) { ' (no LANG)' } else { '' }))
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

    $changed = $false; $userWritten = $false; $machineWritten = $false
    $uRemove = @($m.UserAnalysis | Where-Object Removable)
    if ($uRemove.Count) {
        try {
            Write-RawPath 'User' (Get-RepairedPath $m.UserAnalysis) $m.UserRaw.Kind
            $actions.Add("user: removed $($uRemove.Count) entries ($((@($uRemove | Group-Object Class | ForEach-Object { "$($_.Name)=$($_.Count)" })) -join ', '))")
            $changed = $true; $userWritten = $true
        } catch { $failed = $true; $actions.Add("user: WRITE FAILED: $($_.Exception.Message)") }
    } else { $actions.Add('user: nothing removable') }

    $mRemove = @($m.MachineAnalysis | Where-Object Removable)
    if ($mRemove.Count -and $elevated) {
        try {
            Write-RawPath 'Machine' (Get-RepairedPath $m.MachineAnalysis) $m.MachineRaw.Kind
            $actions.Add("machine: removed $($mRemove.Count) dead entries")
            $changed = $true; $machineWritten = $true
        } catch { $failed = $true; $actions.Add("machine: WRITE FAILED: $($_.Exception.Message)") }
    } elseif ($mRemove.Count) { $actions.Add("machine: $($mRemove.Count) dead entries LEFT IN PLACE - not elevated; rerun -Apply as Administrator to remove them") }
    else { $actions.Add('machine: nothing removable') }
    $post = $null
    try {
        if ($changed) { Send-EnvironmentChanged }   # inside the try: a blocked Add-Type must not skip the receipt
        $after = Measure-Machine
        $me = [Security.Principal.WindowsIdentity]::GetCurrent().Name
        $mySid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
        $resolveSid = {
            param($q)
            try { ([Security.Principal.NTAccount]::new($q)).Translate([Security.Principal.SecurityIdentifier]).Value } catch { $null }
        }
        # Only DEAD entries make a runner .path stale: a removed duplicate's folder still exists.
        $removedKeys = Get-StaleRunnerKeys (@($(if ($userWritten) { $uRemove })) + @($(if ($machineWritten) { $mRemove })))
        foreach ($r in $before.Runners) {
            # One runner's failure is recorded and the next runner still runs; the receipt is
            # written in the finally below whatever happens.
            try {
                $svc = $null
                if ($r.Service) { $svc = Get-CimInstance Win32_Service -Filter ("Name='{0}'" -f ($r.Service -replace "'", "''")) -ErrorAction SilentlyContinue }
                $startName = if ($svc) { [string]$svc.StartName } else { '' }
                if (-not (Test-SameServiceAccount $startName $mySid $env:COMPUTERNAME $resolveSid)) {
                    $actions.Add("runner $($r.name): .path NOT rewritten - service runs as '$startName', this shell is '$me'; the User PATH it needs is that account's")
                    continue
                }
                $pathFile = Join-Path $r.Dir '.path'
                $pathText = if (Test-Path -LiteralPath $pathFile) { [string](Get-Content -LiteralPath $pathFile -Raw) } else { $null }
                $pathAction = Get-RunnerPathAction $pathText $removedKeys $MaxTotalChars
                if ($pathAction -eq 'keep') { $actions.Add("runner $($r.name): .path kept (present, within limit, no removed entry)") }
                else {
                    if ($null -ne $pathText) { Copy-Item -LiteralPath $pathFile -Destination (Join-Path $dir "runner-$($r.name).path.backup") }
                    [IO.File]::WriteAllText($pathFile, $after.FreshPath, [Text.UTF8Encoding]::new($false))
                    $actions.Add("runner $($r.name): .path rewritten, $($pathAction -replace '^rewrite:', '') ($($after.FreshPath.Length) chars)")
                }
                if ($null -eq $r.env_lines -or -not $r.env_has_lang) { $actions.Add("runner $($r.name): .env missing or without LANG - not edited; see SELF-HOSTED-WINDOWS-RUNNER.md host prerequisites") }
                if ($pathAction -eq 'keep') { continue }   # nothing changed for this runner: no restart owed
                $decision = Get-RestartDecision $elevated $(if ($elevated) { Get-RunnerBusy $r } else { 'not read' })
                if ($decision -eq 'restart') {
                    # Residual race, accepted and stated: a job picked up between the busy read and
                    # the restart is interrupted.
                    Restart-Service -Name $r.Service -ErrorAction Stop
                    $actions.Add("runner $($r.name): service restarted (idle per gh api)")
                } else { $actions.Add("runner $($r.name): restart SKIPPED - $($decision -replace '^skip:', ''); restart '$($r.Service)' when idle") }
            } catch { $failed = $true; $actions.Add("runner $($r.name): FAILED: $($_.Exception.Message)") }
        }
        $post = Get-CurrentState
    } catch {
        $failed = $true; $actions.Add("post-repair step FAILED: $($_.Exception.Message)")
    } finally {
        $receipt = [ordered]@{
            schema = 'fleet-path-repair-receipt.v1'; utc = $stamp; machine = $env:COMPUTERNAME; elevated = $elevated
            before = [ordered]@{ user = $before.M.UserStats; machine = $before.M.MachineStats; total = $before.Total; where_git = $before.WhereGit; findings = $before.Findings }
            removed_user = @($(if ($userWritten) { $uRemove | ForEach-Object { [ordered]@{ class = $_.Class; entry = $_.Raw } } }))
            removed_machine = @($(if ($machineWritten) { $mRemove | ForEach-Object { [ordered]@{ class = $_.Class; entry = $_.Raw } } }))
            actions = $actions
            after = $(if ($post) { [ordered]@{ user = $post.M.UserStats; machine = $post.M.MachineStats; total = $post.Total; where_git = $post.WhereGit; findings = $post.Findings } } else { $null })
            failed = $failed
        }
        $receipt | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $dir 'receipt.json') -Encoding utf8
    }
    foreach ($a in $actions) { Say "  $a" }
    Say "Receipt: $(Join-Path $dir 'receipt.json')"
    if (-not $post) { $post = Get-CurrentState }
    Say '--- after ---'
    Write-Report $post.M $post.WhereGit $post.Runners $post.Findings $post.Total
    return [pscustomobject]@{ State = $post; Failed = $failed }
}

function Publish-Ack($state) {
    if (-not (Test-Path -LiteralPath (Join-Path $BusRoot '.git'))) { Say "PUBLISH FAILED: $BusRoot is not a git checkout of the bus"; return 4 }
    $now = (Get-Date).ToUniversalTime()
    $record = New-AckRecord -MachineName $env:COMPUTERNAME -NowUtc $now -ToolCommit (Get-ToolCommit $PSScriptRoot) `
        -User $state.M.UserStats -Machine $state.M.MachineStats -TotalChars $state.Total -WhereGit $state.WhereGit `
        -Runners $state.Runners -Findings $state.Findings
    $rel = "path-health/$($record.machine).json"
    $target = Join-Path $BusRoot $rel
    # The ack only counts on master: the reader runs there. A board's own checkout on a feature
    # branch would publish where nobody reads it, and detached HEAD cannot be pushed by name.
    # Checked BEFORE "unchanged", so a branch copy can never report an ack master has not seen.
    $branch = "$(& git -C $BusRoot symbolic-ref -q --short HEAD 2>$null)".Trim()
    if (-not $branch) { Say "PUBLISH FAILED: $BusRoot is on a detached HEAD; publish from a master checkout (the one-line command clones one)"; return 4 }
    if ($branch -ne 'master' -and -not $AllowBranch) { Say "PUBLISH FAILED: $BusRoot is on branch '$branch', not master; the reader would never see this ack. Use the one-line command, or pass -AllowBranch deliberately."; return 4 }
    # "Unchanged" is a claim about the bus, so the previous record is read from origin, never from
    # this working tree (an earlier failed run may have left a file here).
    $remote = Get-RemoteAckRaw -BusRoot $BusRoot -Branch $branch -Rel $rel
    if (-not $remote.Ok) { Say "PUBLISH FAILED: cannot read origin/$branch to compare the ack"; return 4 }
    $need = Test-AckPublishNeeded -PreviousRaw $remote.Raw -Record $record -NowUtc $now -RefreshHours $RefreshHours
    if (-not $need.Publish) {
        if ($NoPush) { Say "REHEARSAL (-NoPush): $rel ($($need.Reason)) as published on origin/$branch; nothing written."; return 5 }   # a rehearsal is never an ack
        Say "ACK UNCHANGED: $rel ($($need.Reason)) as published on origin/$branch; not pushing a cadence commit."; return 0
    }
    $already = @(& git -C $BusRoot diff --cached --name-only)
    if ($already.Count) { Say "PUBLISH FAILED: staging area already holds $($already -join ', '); refusing to write or commit."; return 4 }
    # Before the commit exists, a failure unstages the ack and puts the file back to HEAD's copy (or
    # removes it), so no failed run leaves a staged or stray ack that blocks or fools the next one.
    # When the index is locked, reset/checkout fail too; HEAD's copy is then written directly.
    $unstage = {
        & git -C $BusRoot reset -q -- $rel *> $null
        & git -C $BusRoot cat-file -e "HEAD:$rel" *> $null
        if ($LASTEXITCODE -eq 0) {
            & git -C $BusRoot checkout -q HEAD -- $rel *> $null
            if ($LASTEXITCODE -ne 0) {
                $h = (& git -C $BusRoot show "HEAD:$rel" 2>$null) -join "`n"
                if ($LASTEXITCODE -eq 0) { [IO.File]::WriteAllText($target, $h + "`n", [Text.UTF8Encoding]::new($false)) }
            }
        } else { Remove-Item -LiteralPath $target -Force -ErrorAction SilentlyContinue }
    }
    # A checkout strictly BEHIND origin is fast-forwarded first (a board's own master that has not
    # pulled). Ahead or diverged is left alone: the push guard refuses it.
    $syncToOrigin = {
        & git -C $BusRoot merge-base --is-ancestor HEAD "refs/remotes/origin/$branch" *> $null
        if ($LASTEXITCODE -ne 0) { return $true }
        & git -C $BusRoot merge -q --ff-only "refs/remotes/origin/$branch" *> $null
        return ($LASTEXITCODE -eq 0)
    }
    $json = ($record | ConvertTo-Json -Depth 6) + "`n"
    # The ack commit is always BUILT on origin's tip from the record's own bytes. A rejected push is
    # never resolved by a text merge of the JSON (a rebase can merge two records into one the reader
    # rejects): our commit is undone, the checkout fast-forwarded, and the commit rebuilt, once.
    for ($attempt = 1; $attempt -le 2; $attempt++) {
        if (-not (& $syncToOrigin)) { Say "PUBLISH FAILED: cannot fast-forward $BusRoot to origin/$branch (local changes in the way?)"; return 4 }
        [void](New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target))
        [IO.File]::WriteAllText($target, $json, [Text.UTF8Encoding]::new($false))
        & git -C $BusRoot add -- $rel *> $null
        if ($LASTEXITCODE -ne 0) { $x = $LASTEXITCODE; & $unstage; Say "PUBLISH FAILED: git add $rel failed (exit $x)"; return 4 }
        $staged = @(& git -C $BusRoot diff --cached --name-only)
        # Nothing staged means HEAD already holds these bytes while origin does not (an unpushed
        # earlier commit): not an ack.
        if ($staged.Count -eq 0) { Say "PUBLISH FAILED: HEAD already holds this $rel but origin/$branch does not (an earlier unpushed commit?); rerun the one-line command"; return 4 }
        if ($staged.Count -ne 1 -or $staged[0] -ne $rel) {
            & $unstage
            Say "PUBLISH FAILED: staging area held other files ($($staged -join ', ')); refusing to commit."; return 4
        }
        & git -C $BusRoot -c commit.gpgsign=false commit -q -m "path-health: $($record.machine) $($record.verdict) ($($need.Reason))" *> $null
        if ($LASTEXITCODE -ne 0) { & $unstage; Say 'PUBLISH FAILED: commit failed (is git user.name/user.email set?); ack unstaged'; return 4 }
        $ackBlob = "$(& git -C $BusRoot rev-parse -q --verify "HEAD:$rel" 2>$null)".Trim()   # the exact blob this run committed
        # Any failure after the commit undoes our own ack commit and file (Undo-AckCommit).
        $undo = { Undo-AckCommit -BusRoot $BusRoot -Rel $rel -Machine $record.machine -Branch $branch -BlobOid $ackBlob }
        if ($NoPush) {
            # A rehearsal proves the commit works, then takes it back: a kept rehearsal commit would
            # make every later -Publish on this checkout fail as "2 commits ahead".
            Say "REHEARSAL (-NoPush): $rel verdict=$($record.verdict) ($($need.Reason)) committed, not pushed ($(& $undo))"; return 5
        }
        $why = Get-AckPushBlocker -BusRoot $BusRoot -Branch $branch -Rel $rel
        if ($why) { Say "PUBLISH FAILED: $why; refusing to push anything but the ack ($(& $undo))"; return 4 }
        & git -C $BusRoot push -q --no-follow-tags origin "HEAD:refs/heads/$branch" *> $null
        if ($LASTEXITCODE -eq 0) { Say "ACK PUBLISHED: $rel verdict=$($record.verdict) ($($need.Reason))"; return 0 }
        $u = & $undo
        if ($u -ne 'ack commit undone locally') { Say "PUBLISH FAILED: push rejected ($u)"; return 4 }
        if ($attempt -eq 2) { Say "PUBLISH FAILED: push rejected twice ($u)"; return 4 }
        & git -C $BusRoot fetch -q origin $branch *> $null
        if ($LASTEXITCODE -ne 0) { Say "PUBLISH FAILED: push rejected and origin/$branch cannot be fetched ($u)"; return 4 }
    }
    return 4
}

try {
    if ($Apply) {
        $res = Invoke-Apply
        $state = $res.State
        $code = if ($res.Failed) { 2 } elseif ($state.Findings.Count) { 1 } else { 0 }
    } else {
        $state = Get-CurrentState
        if ($Json) {
            New-AckRecord -MachineName $env:COMPUTERNAME -NowUtc (Get-Date).ToUniversalTime() -ToolCommit (Get-ToolCommit $PSScriptRoot) -User $state.M.UserStats -Machine $state.M.MachineStats -TotalChars $state.Total -WhereGit $state.WhereGit -Runners $state.Runners -Findings $state.Findings | ConvertTo-Json -Depth 6 | ForEach-Object { Say $_ }
        } else {
            Write-Report $state.M $state.WhereGit $state.Runners $state.Findings $state.Total
            if ($state.Findings.Count) { Say 'Repair (owner''s call): pwsh -NoProfile -File tools/Repair-MachinePath.ps1 -Apply   (Administrator only if Machine PATH has dead entries or a runner must restart)' }
        }
        $code = if ($state.Findings.Count) { 1 } else { 0 }
    }
    if ($Publish) {
        # A failed -Apply (2) is not published: exit 2 means "no ack", and a fresh ack on master behind
        # a 2 would make a caller record BLOCKED while the ledger says ACKED.
        if ($code -eq 2) { Say 'NOT PUBLISHED: -Apply failed (exit 2); fix it, then publish with -Check -Publish.' }
        else { $code = Get-FinalExitCode -CheckCode $code -Published $true -PublishCode (Publish-Ack $state) }
    }
    exit $code
} catch {
    Say "UNEVALUABLE: $($_.Exception.Message)"
    exit 2
}
