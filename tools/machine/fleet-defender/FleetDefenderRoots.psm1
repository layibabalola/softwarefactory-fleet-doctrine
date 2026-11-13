# FleetDefenderRoots.psm1 -- the pure logic of the fleet Defender write-root tool. No Defender calls, no
# elevation, no machine state: every function takes its inputs as parameters, so the unelevated tests
# exercise the same code the SYSTEM task runs.
Set-StrictMode -Version 3

$script:ManifestSchema = 'defender-roots.v1'
$script:StatusSchema   = 'defender-roots-status.v1'
$script:PolicySchema   = 'fleet-defender-policy.v1'
# A request path is printed into a command the owner runs elevated, so any character that could end the
# quoted literal or start another statement is refused outright (never escaped).
$script:UnsafeChars = '[''"`$;&|<>%\x00-\x1f]'

function ConvertTo-RootPath([string]$Path) {
    if ([string]::IsNullOrWhiteSpace($Path)) { return $null }
    $p = $Path.Trim().Trim('"') -replace '/', '\'
    return $p.TrimEnd('\')
}

function Get-DefaultTokenMap {
    # The values the policy's %TOKEN% placeholders expand to on THIS machine, for THIS (installing) user.
    $m = [ordered]@{}
    foreach ($n in 'LOCALAPPDATA', 'USERPROFILE', 'SystemRoot', 'SystemDrive', 'ProgramFiles', 'ProgramFiles(x86)', 'ProgramData') {
        $v = [Environment]::GetEnvironmentVariable($n)
        if ($v) { $m[$n] = $v.TrimEnd('\') }
    }
    return $m
}

function Expand-PolicyString([string]$Value, [System.Collections.IDictionary]$Tokens) {
    $out = [regex]::Replace($Value, '%([^%]+)%', {
        param($mt)
        $k = $mt.Groups[1].Value
        if ($Tokens.Contains($k)) { return [string]$Tokens[$k] }
        throw "policy token %$k% has no value on this machine"
    })
    return (ConvertTo-RootPath $out)
}

function Test-UnderPrefix([string]$Path, [string]$Prefix) {
    $Prefix = ConvertTo-RootPath $Prefix
    return ($Path -ieq $Prefix) -or $Path.StartsWith($Prefix + '\', [StringComparison]::OrdinalIgnoreCase)
}

function Get-RootVerdict([string]$Path, $Policy) {
    # $Path is already normalised (ConvertTo-RootPath); $Policy is EXPANDED (no %TOKEN% left).
    if (-not $Path) { return 'reject:empty' }
    if ($Path -match $script:UnsafeChars) { return 'reject:unsafe-character' }
    if ($Path -notmatch '^[A-Za-z]:\\.+') { return 'reject:not-an-absolute-local-path' }
    if ($Path.IndexOf(':', 2) -ge 0) { return 'reject:stream-or-device-colon' }
    if ($Path -match '\.\.') { return 'reject:dot-dot' }
    $segments = $Path.Split('\')
    for ($i = 0; $i -lt $segments.Count - 1; $i++) { if ($segments[$i] -match '[\*\?]') { return 'reject:wildcard-not-in-last-segment' } }
    if ($segments[-1] -match '^[\*\?]+$') { return 'reject:bare-wildcard' }
    foreach ($d in @($Policy.deniedPrefixes)) { if (Test-UnderPrefix $Path $d) { return 'reject:denied-prefix' } }
    foreach ($a in @($Policy.allowedExactRoots)) { if ((ConvertTo-RootPath $a) -ieq $Path) { return 'allow:exact' } }
    if ($segments.Count -lt 3) { return 'pending:top-level-folder-needs-owner' }
    foreach ($a in @($Policy.allowedParents)) {
        if ($Path.StartsWith((ConvertTo-RootPath $a) + '\', [StringComparison]::OrdinalIgnoreCase)) { return 'allow:under-allowed-parent' }
    }
    return 'pending:outside-allowlist'
}

function Read-JsonFile([string]$Path) {
    return (Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json)
}

function Merge-FleetDefenderPolicy {
    # Shipped defaults + optional per-machine override -> one expanded policy. The override can only ADD
    # allowlist entries and deny prefixes; the shipped deny prefixes always survive. Throws on any allowlist
    # entry the verdict rules would refuse anyway (so a bad override fails at install, not silently later).
    param([Parameter(Mandatory)]$Defaults, $Local, [Parameter(Mandatory)][System.Collections.IDictionary]$Tokens,
          [Parameter(Mandatory)][string]$ManifestPath, [Parameter(Mandatory)][string]$StatusPath)
    foreach ($doc in @($Defaults, $Local)) {
        if ($null -ne $doc -and $doc.schema -ne $script:PolicySchema) { throw "policy schema must be $script:PolicySchema (got '$($doc.schema)')" }
    }
    if ($null -ne $Local) {
        $extra = @($Local.PSObject.Properties.Name | Where-Object { $_ -notin 'schema', '_comment', 'allowedParents', 'allowedExactRoots', 'deniedPrefixes' })
        if ($extra.Count) { throw "local policy may only set allowedParents, allowedExactRoots, deniedPrefixes (got: $($extra -join ', '))" }
    }
    $lists = [ordered]@{}
    foreach ($k in 'allowedParents', 'allowedExactRoots', 'deniedPrefixes') {
        $vals = New-Object System.Collections.Generic.List[string]
        foreach ($doc in @($Defaults, $Local)) {
            if ($null -eq $doc -or -not ($doc.PSObject.Properties.Name -contains $k)) { continue }
            foreach ($v in @($doc.$k)) {
                $e = Expand-PolicyString ([string]$v) $Tokens
                if ($e -and -not ($vals | Where-Object { $_ -ieq $e })) { $vals.Add($e) }
            }
        }
        $lists[$k] = @($vals)
    }
    $policy = [pscustomobject]([ordered]@{
        schema = $script:PolicySchema; manifestPath = $ManifestPath; statusPath = $StatusPath
        allowedParents = $lists.allowedParents; allowedExactRoots = $lists.allowedExactRoots; deniedPrefixes = $lists.deniedPrefixes
    })
    $probe = [pscustomobject]@{ deniedPrefixes = $policy.deniedPrefixes; allowedExactRoots = @(); allowedParents = @() }
    foreach ($a in @($policy.allowedParents) + @($policy.allowedExactRoots)) {
        $v = Get-RootVerdict $a $probe
        if ($v -like 'reject:*') { throw "allowlist entry '$a' is refused by the verdict rules ($v)" }
    }
    return $policy
}

function Read-RootManifest([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path)) { return [pscustomobject]@{ schema = $script:ManifestSchema; roots = @() } }
    $doc = Read-JsonFile $Path
    if ($doc.schema -ne $script:ManifestSchema) { throw "manifest schema must be $script:ManifestSchema (got '$($doc.schema)')" }
    if (-not ($doc.PSObject.Properties.Name -contains 'roots') -or $null -eq $doc.roots) { $doc | Add-Member -Force roots @() }
    return $doc
}

function Add-RootRequest {
    # Append one request row (idempotent, case-insensitive on the normalised path). Returns 'registered' or
    # 'already-registered'. Serialised across processes by a named mutex; written via a temp file + rename.
    param([Parameter(Mandatory)][string]$ManifestPath, [Parameter(Mandatory)][string]$Path,
          [Parameter(Mandatory)][string]$Project, [string]$Reason = '', [datetime]$NowUtc = (Get-Date).ToUniversalTime())
    $norm = ConvertTo-RootPath $Path
    if (-not $norm) { throw 'empty path' }
    $dir = Split-Path -Parent $ManifestPath
    if ($dir) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    $mutex = [Threading.Mutex]::new($false, 'Local\FleetDefenderRootsManifest')
    $held = $false
    try {
        try { $held = $mutex.WaitOne(10000) } catch [Threading.AbandonedMutexException] { $held = $true }
        if (-not $held) { throw 'manifest lock not acquired within 10 s' }
        $doc = Read-RootManifest $ManifestPath
        if (@($doc.roots | Where-Object { (ConvertTo-RootPath ([string]$_.path)) -ieq $norm }).Count -gt 0) { return 'already-registered' }
        $doc.roots = @($doc.roots) + [pscustomobject]([ordered]@{ path = $norm; project = $Project; reason = $Reason; addedUtc = $NowUtc.ToString('o') })
        $tmp = "$ManifestPath.tmp-$PID"
        [IO.File]::WriteAllText($tmp, ($doc | ConvertTo-Json -Depth 5), [Text.UTF8Encoding]::new($false))
        Move-Item -LiteralPath $tmp -Destination $ManifestPath -Force
        return 'registered'
    } finally { if ($held) { $mutex.ReleaseMutex() }; $mutex.Dispose() }
}

function Get-OwnerCommand([string[]]$Paths) {
    # Paths reaching here passed Get-RootVerdict, so none holds a quote or statement separator.
    if (-not $Paths -or $Paths.Count -eq 0) { return $null }
    $list = ($Paths | ForEach-Object { "''" + $_ + "''" }) -join ','
    return "pwsh -NoProfile -Command `"Start-Process pwsh -Verb RunAs -ArgumentList '-NoProfile -Command Add-MpPreference -ExclusionPath $list'`""
}

function Invoke-RootPlan {
    # Classify every request against the policy and the exclusions already present. Pure: the caller does the
    # Add-MpPreference for $plan.toAdd. -ShortPath maps an allowed existing folder to its 8.3 form (or $null).
    # -IsLink says whether the path or an existing ancestor is a link/junction: such a request is rejected, since
    # its text sits under an allowed parent while its bytes may live anywhere.
    param([Parameter(Mandatory)]$Policy, $Requests, [string[]]$CurrentExclusions = @(), [scriptblock]$ShortPath = { param($p) $null },
          [scriptblock]$IsLink = { param($p) $false })
    $current = New-Object System.Collections.Generic.List[string]
    foreach ($c in @($CurrentExclusions)) { if ($c) { $current.Add($c) } }
    $applied = @(); $pending = @(); $rejected = @(); $already = @(); $toAdd = @()
    foreach ($r in @($Requests)) {
        if ($null -eq $r) { continue }
        $path = ConvertTo-RootPath ([string]$r.path)
        $verdict = Get-RootVerdict $path $Policy
        if ($verdict -notlike 'reject:*' -and (& $IsLink $path)) { $verdict = 'reject:link-or-junction' }
        $forms = @($path)
        if ($verdict -like 'allow:*' -and $path -notmatch '[\*\?]') {
            $short = & $ShortPath $path
            if ($short -and $short -ine $path) { $forms += $short }
        }
        $missing = @($forms | Where-Object { $f = $_; -not ($current | Where-Object { $_ -ieq $f }) })
        $row = [ordered]@{ path = $path; project = [string]$r.project; verdict = $verdict; forms = $forms }
        if ($verdict -like 'reject:*') { $rejected += $row; continue }
        if ($missing.Count -eq 0) { $already += $row; continue }
        if ($verdict -like 'allow:*') {
            $row.added = $missing; $applied += $row; $toAdd += $missing
            foreach ($m in $missing) { $current.Add($m) }
        } else { $pending += $row }
    }
    return [pscustomobject]@{ applied = $applied; pending = $pending; rejected = $rejected; already = $already; toAdd = $toAdd
                              ownerCommand = (Get-OwnerCommand @($pending | ForEach-Object { $_.path })) }
}

function New-RootStatus($Plan, [string]$ManifestPath, [string]$ManifestError, [datetime]$NowUtc, [bool]$DryRun = $false) {
    return [ordered]@{
        schema = $script:StatusSchema; checkedUtc = $NowUtc.ToString('o'); dryRun = $DryRun; manifest = $ManifestPath
        manifestError = $ManifestError; applied = @($Plan.applied); alreadyExcluded = @($Plan.already | ForEach-Object { $_.path })
        pending = @($Plan.pending); rejected = @($Plan.rejected); ownerCommand = $Plan.ownerCommand
    }
}

function Format-RootAlert {
    # Lines for the SessionStart hook; empty when nothing needs the owner. Never applies anything.
    param($Status, [datetime]$NowUtc = (Get-Date).ToUniversalTime(), [int]$StaleMinutes = 60, [string]$StatusPath = '')
    $lines = @()
    if ($null -eq $Status) { return @('[defender-roots] installed but no status file yet: the FleetDefenderRoots task has not run.') }
    # As hashtables, a missing key reads as $null under strict mode instead of throwing.
    $Status = $Status | ConvertTo-Json -Depth 8 | ConvertFrom-Json -AsHashtable
    # pwsh 7 ConvertFrom-Json already turns an ISO string into a [datetime]; a string cast would drop its Kind.
    $checked = [datetime]::MinValue
    if ($Status['checkedUtc'] -is [datetime]) { $checked = $Status['checkedUtc'] }
    elseif (-not [datetime]::TryParse([string]$Status['checkedUtc'], [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::RoundtripKind, [ref]$checked)) {
        $lines += '[defender-roots] the status file has no readable checkedUtc: treat the FleetDefenderRoots task as not running.'
        $checked = $NowUtc
    }
    $age = ($NowUtc - $checked.ToUniversalTime()).TotalMinutes
    if ($age -gt $StaleMinutes) { $lines += "[defender-roots] status is $([int]$age) min old: the FleetDefenderRoots task may not be running (expected every 15 min)." }
    if ($Status['manifestError']) { $lines += "[defender-roots] the request manifest did not parse: $($Status['manifestError'])" }
    # The command is REBUILT from paths re-checked here, never echoed from the file: the owner runs it elevated,
    # so a status file someone else wrote must not be able to choose what it says.
    $pending = @($Status['pending'] | Where-Object { $_ -is [System.Collections.IDictionary] })
    $safe = @($pending | ForEach-Object { ConvertTo-RootPath ([string]$_['path']) } | Where-Object { $_ -and $_ -notmatch $script:UnsafeChars -and $_ -match '^[A-Za-z]:\\.+' -and $_ -notmatch '\.\.' })
    if ($pending.Count -gt 0) {
        $lines += "[defender-roots] $($pending.Count) write root(s) need a Defender exclusion that only the owner can approve:"
        foreach ($p in $pending) { $lines += "  - $(ConvertTo-RootPath ([string]$p['path']) -replace $script:UnsafeChars, '?')  ($($p['project']); $($p['verdict']))" }
        if ($safe.Count -lt $pending.Count) { $lines += "  ($($pending.Count - $safe.Count) pending path(s) failed re-validation and are left out of the command: the status file was not written by the task.)" }
        if ($safe.Count -gt 0) {
            $lines += '  Owner, run this (one UAC prompt):'
            $lines += "  $(Get-OwnerCommand $safe)"
        }
    }
    $rejected = @($Status['rejected'] | Where-Object { $_ })
    if ($rejected.Count -gt 0) { $lines += "[defender-roots] $($rejected.Count) request(s) rejected by policy (see $StatusPath)." }
    if ($lines.Count -gt 0) { $lines = @('=== DEFENDER ROOTS -- SURFACE THIS TO THE OWNER ===') + $lines }
    return $lines
}

function Set-RootAlertHook {
    # Register the alert as ONE Claude Code SessionStart command hook in a settings.json. Idempotent; an entry
    # naming the alert script with another command (an older install dir) is replaced, not duplicated; other
    # hooks are kept. A backup is written beside the file before any change. Returns a one-line message.
    param([Parameter(Mandatory)][string]$SettingsPath, [Parameter(Mandatory)][string]$HookCommand)
    $s = Get-Content -LiteralPath $SettingsPath -Raw | ConvertFrom-Json -AsHashtable
    if (-not $s.ContainsKey('hooks')) { $s['hooks'] = [ordered]@{} }
    $groups = @(if ($s['hooks'].ContainsKey('SessionStart')) { $s['hooks']['SessionStart'] })
    $cmds = @($groups | ForEach-Object { @($_['hooks']) } | ForEach-Object { [string]$_['command'] })
    if ($cmds -contains $HookCommand -and @($cmds | Where-Object { $_ -match 'Show-DefenderRootsAlert' }).Count -eq 1) { return 'SessionStart hook already registered' }
    Copy-Item -LiteralPath $SettingsPath -Destination "$SettingsPath.bak-defender-$(Get-Date -Format yyyyMMddTHHmmssfff)"
    $kept = @(foreach ($g in $groups) {
        $g['hooks'] = @(@($g['hooks']) | Where-Object { [string]$_['command'] -notmatch 'Show-DefenderRootsAlert' })
        if ($g['hooks'].Count -gt 0) { $g }
    })
    $s['hooks']['SessionStart'] = @($kept) + @([ordered]@{ hooks = @([ordered]@{ type = 'command'; timeout = 15; command = $HookCommand }) })
    [IO.File]::WriteAllText($SettingsPath, ($s | ConvertTo-Json -Depth 100), [Text.UTF8Encoding]::new($false))
    return "SessionStart hook registered in $SettingsPath"
}

Export-ModuleMember -Function ConvertTo-RootPath, Get-DefaultTokenMap, Expand-PolicyString, Test-UnderPrefix, Get-RootVerdict,
    Read-JsonFile, Merge-FleetDefenderPolicy, Read-RootManifest, Add-RootRequest, Get-OwnerCommand, Invoke-RootPlan,
    New-RootStatus, Format-RootAlert, Set-RootAlertHook
