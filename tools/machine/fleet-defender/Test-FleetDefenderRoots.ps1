# Test-FleetDefenderRoots.ps1 -- unelevated tests, no Defender call, no machine state touched (Windows and POSIX
# pwsh). Covers: verdicts, policy merge (defaults + local override), manifest round-trip through
# Register-DefenderRoot.ps1, a full Apply-DefenderRoots.ps1 -DryRun pass, the SessionStart alert with pending
# entries, and that no shipped file names a machine. Exit code = number of failures.
#   pwsh -NoProfile -File tools/machine/fleet-defender/Test-FleetDefenderRoots.ps1
$ErrorActionPreference = 'Stop'
$here = $PSScriptRoot
Import-Module (Join-Path $here 'FleetDefenderRoots.psm1') -Force
$pwsh = (Get-Process -Id $PID).Path
$script:fail = 0; $script:pass = 0
function Check([string]$Name, [bool]$Ok, [string]$Detail = '') {
    if ($Ok) { $script:pass++; "PASS  $Name" } else { $script:fail++; "FAIL  $Name  $Detail" }
}
function Throws([scriptblock]$Block, [string]$Like) {
    try { & $Block; return $false } catch { return ($_.Exception.Message -like $Like) }
}
$tmp = Join-Path ([IO.Path]::GetTempPath()) ("fdr-test-" + [guid]::NewGuid().ToString('N').Substring(0, 8))
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
try {
    # A fictional machine: every %TOKEN% resolves to a neutral value, so the cases are host-independent.
    $L = 'C:\Home\u\AppData\Local'
    $tokens = [ordered]@{ LOCALAPPDATA = $L; USERPROFILE = 'C:\Home\u'; SystemRoot = 'C:\Windows'; SystemDrive = 'C:'
                          ProgramFiles = 'C:\Program Files'; 'ProgramFiles(x86)' = 'C:\Program Files (x86)'; ProgramData = 'C:\ProgramData' }
    $defaults = Read-JsonFile (Join-Path $here 'policy.defaults.json')
    $localDoc = '{"schema":"fleet-defender-policy.v1","allowedParents":["%SystemDrive%\\scratch","C:\\Work Space"],"allowedExactRoots":["%SystemDrive%\\scratch","C:\\Qt","%LOCALAPPDATA%\\Builder-*"],"deniedPrefixes":[]}' | ConvertFrom-Json
    $policy = Merge-FleetDefenderPolicy -Defaults $defaults -Local $localDoc -Tokens $tokens -ManifestPath "$tmp\m.json" -StatusPath "$tmp\s.json"

    # --- verdicts -----------------------------------------------------------------------------------------
    $cases = [ordered]@{
        'C:\scratch'                       = 'allow:exact'
        'C:\scratch\lane-X-20261018'       = 'allow:under-allowed-parent'
        'C:/scratch/lane-Y/'               = 'allow:under-allowed-parent'
        'C:\Work Space\NewProject\build'   = 'allow:under-allowed-parent'
        'C:\Qt'                            = 'allow:exact'
        "$L\Builder-*"                     = 'allow:exact'
        "$L\Temp\claude"                   = 'allow:exact'
        "$L\Temp\claude\abc"               = 'allow:under-allowed-parent'
        'C:\NewScratch'                    = 'pending:top-level-folder-needs-owner'
        'C:\Work Space'                    = 'pending:top-level-folder-needs-owner'
        "$L\SomeVendor\cache"              = 'pending:outside-allowlist'
        'C:\Windows\Temp\x'                = 'reject:denied-prefix'
        'C:\Program Files\Foo'             = 'reject:denied-prefix'
        'C:\ProgramData'                   = 'reject:denied-prefix'
        "$L\Microsoft\Edge"                = 'reject:denied-prefix'
        'C:\scratch\*'                     = 'reject:bare-wildcard'
        'C:\scr*\sub'                      = 'reject:wildcard-not-in-last-segment'
        'C:\scratch\..\Windows'            = 'reject:dot-dot'
        'relative\path'                    = 'reject:not-an-absolute-local-path'
        '\\server\share'                   = 'reject:not-an-absolute-local-path'
        'C:\'                              = 'reject:not-an-absolute-local-path'
        "C:\scratch\a'; Remove-Item C:\x"  = 'reject:unsafe-character'
        'C:\scratch\a$(whoami)'            = 'reject:unsafe-character'
        'C:\scratch\a" & calc'             = 'reject:unsafe-character'
        'C:\scratch\%TEMP%'                = 'reject:unsafe-character'
        'C:\scratch\x:hidden'              = 'reject:stream-or-device-colon'
        ''                                 = 'reject:empty'
    }
    foreach ($k in $cases.Keys) {
        $got = Get-RootVerdict (ConvertTo-RootPath $k) $policy
        Check "verdict [$k]" ($got -eq $cases[$k]) "got $got want $($cases[$k])"
    }

    # --- policy merge -------------------------------------------------------------------------------------
    Check 'merge keeps every shipped deny prefix' (@($policy.deniedPrefixes).Count -eq 6 -and ($policy.deniedPrefixes -contains "$L\Packages"))
    Check 'merge expands tokens' (($policy.allowedParents -contains 'C:\scratch') -and -not ($policy.allowedParents -match '%'))
    $dup = '{"schema":"fleet-defender-policy.v1","allowedParents":["%LOCALAPPDATA%\\TEMP\\Claude"]}' | ConvertFrom-Json
    $p2 = Merge-FleetDefenderPolicy -Defaults $defaults -Local $dup -Tokens $tokens -ManifestPath m -StatusPath s
    Check 'merge de-duplicates case-insensitively' (@($p2.allowedParents).Count -eq 1)
    $p3 = Merge-FleetDefenderPolicy -Defaults $defaults -Local $null -Tokens $tokens -ManifestPath m -StatusPath s
    Check 'no local override = shipped defaults only' (@($p3.allowedParents).Count -eq 1 -and (Get-RootVerdict 'C:\scratch\x' $p3) -eq 'pending:outside-allowlist')
    $bad = '{"schema":"fleet-defender-policy.v1","allowedParents":["%SystemRoot%\\Temp"]}' | ConvertFrom-Json
    Check 'merge refuses an allowlist entry under a deny prefix' (Throws { Merge-FleetDefenderPolicy -Defaults $defaults -Local $bad -Tokens $tokens -ManifestPath m -StatusPath s } "*refused by the verdict rules (reject:denied-prefix)*")
    $bad = '{"schema":"fleet-defender-policy.v1","allowedExactRoots":["C:\\"]}' | ConvertFrom-Json
    Check 'merge refuses a drive root' (Throws { Merge-FleetDefenderPolicy -Defaults $defaults -Local $bad -Tokens $tokens -ManifestPath m -StatusPath s } '*refused by the verdict rules*')
    $bad = '{"schema":"fleet-defender-policy.v1","manifestPath":"C:\\elsewhere.json"}' | ConvertFrom-Json
    Check 'merge refuses a local override of other keys' (Throws { Merge-FleetDefenderPolicy -Defaults $defaults -Local $bad -Tokens $tokens -ManifestPath m -StatusPath s } '*may only set*')
    $bad = '{"schema":"fleet-defender-policy.v1","allowedParents":["%NOPE%\\x"]}' | ConvertFrom-Json
    Check 'merge refuses an unknown token' (Throws { Merge-FleetDefenderPolicy -Defaults $defaults -Local $bad -Tokens $tokens -ManifestPath m -StatusPath s } '*%NOPE% has no value*')
    $bad = '{"schema":"other.v9"}' | ConvertFrom-Json
    Check 'merge refuses a wrong schema' (Throws { Merge-FleetDefenderPolicy -Defaults $defaults -Local $bad -Tokens $tokens -ManifestPath m -StatusPath s } '*schema must be*')

    # --- manifest round-trip through the unelevated register script ---------------------------------------
    $man = Join-Path $tmp 'fleet/defender-roots.json'
    $r1 = & $pwsh -NoProfile -File (Join-Path $here 'Register-DefenderRoot.ps1') -Path 'C:/scratch/lane-A/' -Project proj-a -Reason 'lane scratch' -ManifestPath $man
    $r2 = & $pwsh -NoProfile -File (Join-Path $here 'Register-DefenderRoot.ps1') -Path 'c:\SCRATCH\lane-a' -Project proj-b -ManifestPath $man
    $r3 = & $pwsh -NoProfile -File (Join-Path $here 'Register-DefenderRoot.ps1') -Path 'C:\NewScratch' -Project proj-a -ManifestPath $man
    $doc = Read-RootManifest $man
    Check 'register: first call registers' ("$r1" -eq 'registered: C:\scratch\lane-A') "$r1"
    Check 'register: same root, other case/slashes = idempotent' ("$r2" -eq 'already-registered: c:\SCRATCH\lane-a') "$r2"
    Check 'register: manifest round-trips (schema, 2 rows, fields)' ($doc.schema -eq 'defender-roots.v1' -and @($doc.roots).Count -eq 2 -and $doc.roots[0].path -eq 'C:\scratch\lane-A' -and $doc.roots[0].project -eq 'proj-a' -and $doc.roots[0].reason -eq 'lane scratch' -and $doc.roots[0].addedUtc)
    $null = Add-RootRequest -ManifestPath $man -Path "$L\SomeVendor\cache" -Project proj-c
    $null = Add-RootRequest -ManifestPath $man -Path 'C:\Windows\Temp\x' -Project proj-c
    $null = Add-RootRequest -ManifestPath $man -Path 'C:\scratch\done' -Project proj-c
    Check 'register: module and script write the same file' (@((Read-RootManifest $man).roots).Count -eq 5)
    Set-Content -LiteralPath (Join-Path $tmp 'wrong.json') -Value '{"schema":"x","roots":[]}'
    Check 'manifest: wrong schema refused' (Throws { Read-RootManifest (Join-Path $tmp 'wrong.json') } '*schema must be*')

    # --- a full applier pass, dry run (no Defender) -------------------------------------------------------
    $inst = Join-Path $tmp 'install'; New-Item -ItemType Directory -Force -Path $inst | Out-Null
    foreach ($f in 'FleetDefenderRoots.psm1', 'Apply-DefenderRoots.ps1', 'Show-DefenderRootsAlert.ps1') { Copy-Item (Join-Path $here $f) $inst }
    $status = Join-Path $tmp 'fleet/defender-roots.status.json'
    $pol = Merge-FleetDefenderPolicy -Defaults $defaults -Local $localDoc -Tokens $tokens -ManifestPath $man -StatusPath $status
    [IO.File]::WriteAllText((Join-Path $inst 'policy.json'), ($pol | ConvertTo-Json -Depth 5))
    & $pwsh -NoProfile -File (Join-Path $inst 'Apply-DefenderRoots.ps1') -PolicyPath (Join-Path $inst 'policy.json') -DryRun -CurrentExclusions 'C:\scratch\done' -LogDir (Join-Path $tmp 'log')
    $s = Read-JsonFile $status
    Check 'apply: status schema and dryRun flag' ($s.schema -eq 'defender-roots-status.v1' -and $s.dryRun -eq $true)
    Check 'apply: allowed root is applied' (@($s.applied).Count -eq 1 -and $s.applied[0].path -eq 'C:\scratch\lane-A' -and $s.applied[0].added -contains 'C:\scratch\lane-A')
    Check 'apply: already-excluded root is not re-added' (@($s.alreadyExcluded) -contains 'C:\scratch\done')
    Check 'apply: top-level and outside-allowlist roots are pending' (@($s.pending).Count -eq 2 -and (@($s.pending.path) -contains 'C:\NewScratch') -and (@($s.pending.path) -contains "$L\SomeVendor\cache"))
    Check 'apply: denied root is rejected' (@($s.rejected).Count -eq 1 -and $s.rejected[0].verdict -eq 'reject:denied-prefix')
    Check 'apply: owner command names exactly the pending roots' ($s.ownerCommand -like "*Add-MpPreference -ExclusionPath ''C:\NewScratch'',''$L\SomeVendor\cache''*" -and $s.ownerCommand -notlike '*lane-A*' -and $s.ownerCommand -notlike '*Windows*')
    Check 'apply: log row written' (Test-Path (Join-Path $tmp 'log/apply.jsonl'))
    $plan = Invoke-RootPlan -Policy $pol -Requests @([pscustomobject]@{ path = 'C:\scratch\long-name'; project = 'p' }) -ShortPath { param($p) 'C:\scratch\LONG-N~1' }
    Check 'plan: 8.3 short form is added beside the long form' (($plan.toAdd -join '|') -eq 'C:\scratch\long-name|C:\scratch\LONG-N~1')
    $plan = Invoke-RootPlan -Policy $pol -Requests @([pscustomobject]@{ path = 'C:\scratch\long-name'; project = 'p' }) -CurrentExclusions 'c:\SCRATCH\long-name' -ShortPath { param($p) 'C:\scratch\LONG-N~1' }
    $lplan = Invoke-RootPlan -Policy $pol -Requests @([pscustomobject]@{ path = 'C:\scratch\j'; project = 'p' }, [pscustomobject]@{ path = 'C:\scratch\k'; project = 'p' }) -IsLink { param($p) $p -eq 'C:\scratch\j' }
    Check 'plan: a link or junction under an allowed parent is rejected' (@($lplan.rejected).Count -eq 1 -and $lplan.rejected[0].verdict -eq 'reject:link-or-junction' -and ($lplan.toAdd -join '|') -eq 'C:\scratch\k')
    Check 'plan: only the missing form is added' (($plan.toAdd -join '|') -eq 'C:\scratch\LONG-N~1')
    Set-Content -LiteralPath $man -Value '{ not json'
    & $pwsh -NoProfile -File (Join-Path $inst 'Apply-DefenderRoots.ps1') -PolicyPath (Join-Path $inst 'policy.json') -DryRun -LogDir (Join-Path $tmp 'log')
    $s2 = Read-JsonFile $status
    Check 'apply: an unparsable manifest is reported, not fatal' ([bool]$s2.manifestError -and @($s2.applied).Count -eq 0)

    if ($IsWindows) {
        # A real junction under an allowed parent, through the real applier (dry run): rejected, its sibling applied.
        $jroot = Join-Path $tmp 'jroot'; New-Item -ItemType Directory -Force -Path (Join-Path $jroot 'real') | Out-Null
        New-Item -ItemType Junction -Path (Join-Path $jroot 'jn') -Target (Join-Path $jroot 'real') | Out-Null
        $jman = Join-Path $tmp 'jman.json'; $jstat = Join-Path $tmp 'jstat.json'
        $null = Add-RootRequest -ManifestPath $jman -Path (Join-Path $jroot 'jn') -Project p
        $null = Add-RootRequest -ManifestPath $jman -Path (Join-Path $jroot 'real') -Project p
        $jlocal = [pscustomobject]@{ schema = 'fleet-defender-policy.v1'; allowedParents = @($jroot) }
        $jpol = Merge-FleetDefenderPolicy -Defaults $defaults -Local $jlocal -Tokens $tokens -ManifestPath $jman -StatusPath $jstat
        [IO.File]::WriteAllText((Join-Path $inst 'jpolicy.json'), ($jpol | ConvertTo-Json -Depth 5))
        & $pwsh -NoProfile -File (Join-Path $inst 'Apply-DefenderRoots.ps1') -PolicyPath (Join-Path $inst 'jpolicy.json') -DryRun -LogDir (Join-Path $tmp 'log')
        $js = Read-JsonFile $jstat
        Check 'apply (Windows): a real junction is rejected, the real folder applied' (@($js.rejected).Count -eq 1 -and $js.rejected[0].verdict -eq 'reject:link-or-junction' -and @($js.applied).Count -eq 1 -and $js.applied[0].path -like '*\real') ($js | ConvertTo-Json -Depth 5 -Compress)
        (Get-Item -LiteralPath (Join-Path $jroot 'jn') -Force).Delete()   # remove the junction itself, never its target's contents
    }

    # --- the SessionStart alert ---------------------------------------------------------------------------
    [IO.File]::WriteAllText($status, ($s | ConvertTo-Json -Depth 6))   # restore the pass with pending rows
    $s.checkedUtc = (Get-Date).ToUniversalTime().ToString('o'); [IO.File]::WriteAllText($status, ($s | ConvertTo-Json -Depth 6))
    $out = @(& $pwsh -NoProfile -File (Join-Path $inst 'Show-DefenderRootsAlert.ps1') -InstallDir $inst -StatusPath $status)
    $code = $LASTEXITCODE
    Check 'alert: exits 0' ($code -eq 0)
    Check 'alert: header + both pending roots + owner command' ($out[0] -eq '=== DEFENDER ROOTS -- SURFACE THIS TO THE OWNER ===' -and ($out -match [regex]::Escape('- C:\NewScratch  (proj-a; pending:top-level-folder-needs-owner)')) -and ($out -match 'Start-Process pwsh -Verb RunAs') -and ($out -match '1 request\(s\) rejected')) ($out -join ' / ')
    Check 'alert: fresh status is not reported stale' (-not ($out -match 'min old'))
    $forged = $s | ConvertTo-Json -Depth 6 | ConvertFrom-Json
    $forged.ownerCommand = 'pwsh -c Remove-Item C:\important -Recurse'
    $forged.pending = @($forged.pending) + [pscustomobject]@{ path = "C:\scratch\x'; iex evil"; project = 'p'; verdict = 'pending:outside-allowlist' }
    $out = @(Format-RootAlert -Status $forged)
    Check 'alert: the command is rebuilt, never echoed from the status file' (-not ($out -match 'important') -and ($out -match [regex]::Escape("''C:\NewScratch''")))
    Check 'alert: a pending path that fails re-validation is left out of the command' (-not (($out | Where-Object { $_ -match 'RunAs' }) -match 'evil') -and ($out -match 'failed re-validation'))
    $quiet = $s | ConvertTo-Json -Depth 6 | ConvertFrom-Json; $quiet.pending = @(); $quiet.rejected = @(); $quiet.ownerCommand = $null
    [IO.File]::WriteAllText($status, ($quiet | ConvertTo-Json -Depth 6))
    $out = @(& $pwsh -NoProfile -File (Join-Path $inst 'Show-DefenderRootsAlert.ps1') -InstallDir $inst -StatusPath $status)
    Check 'alert: silent when nothing needs the owner' ($out.Count -eq 0) ($out -join ' / ')
    $out = @(Format-RootAlert -Status $quiet -NowUtc ((Get-Date).ToUniversalTime().AddMinutes(90)))
    Check 'alert: a stale status (task not running) is reported' ($out.Count -eq 2 -and $out[1] -match 'min old')
    $out = @(& $pwsh -NoProfile -File (Join-Path $inst 'Show-DefenderRootsAlert.ps1') -InstallDir (Join-Path $tmp 'not-installed') -StatusPath $status)
    Check 'alert: silent when the tool is not installed' ($out.Count -eq 0 -and $LASTEXITCODE -eq 0)
    $out = @(& $pwsh -NoProfile -File (Join-Path $inst 'Show-DefenderRootsAlert.ps1') -InstallDir $inst -StatusPath (Join-Path $tmp 'none.json'))
    Check 'alert: installed but never ran is reported' ($out.Count -eq 1 -and $out[0] -match 'has not run')

    $out = @(Format-RootAlert -Status ([pscustomobject]@{ checkedUtc = 'garbage'; pending = @(); rejected = @() }))
    Check 'alert: an unreadable checkedUtc is reported, not thrown' ([bool]($out -match 'no readable checkedUtc'))

    # --- the SessionStart hook registration ---------------------------------------------------------------
    $set = Join-Path $tmp 'settings.json'
    Set-Content -LiteralPath $set -Value '{"model":"x","hooks":{"SessionStart":[{"hooks":[{"type":"command","command":"other-hook"},{"type":"command","command":"pwsh -File \"D:\\old\\Show-DefenderRootsAlert.ps1\""}]}],"Stop":[{"hooks":[{"type":"command","command":"stop-hook"}]}]}}'
    $cmd = 'pwsh -NoProfile -NonInteractive -File "X\Show-DefenderRootsAlert.ps1"'
    $m1 = Set-RootAlertHook -SettingsPath $set -HookCommand $cmd
    $m2 = Set-RootAlertHook -SettingsPath $set -HookCommand $cmd
    $j = Get-Content -LiteralPath $set -Raw | ConvertFrom-Json -AsHashtable
    $all = @($j.hooks.SessionStart | ForEach-Object { @($_.hooks) } | ForEach-Object { $_.command })
    Check 'hook: registered once, stale entry replaced, other hooks kept' ($m1 -like 'SessionStart hook registered*' -and $m2 -eq 'SessionStart hook already registered' -and ($all -join '|') -eq "other-hook|$cmd" -and $j.model -eq 'x' -and $j.hooks.Stop[0].hooks[0].command -eq 'stop-hook') "$m1 / $m2 / $($all -join '|')"
    Check 'hook: a backup is written before the change' (@(Get-ChildItem -LiteralPath $tmp -Filter 'settings.json.bak-defender-*').Count -eq 1)

    # --- Law 4: nothing shipped names a machine -----------------------------------------------------------
    $shipped = Get-ChildItem -LiteralPath $here -File | Where-Object { $_.Name -notin 'Test-FleetDefenderRoots.ps1', 'README.md' }
    $hits = foreach ($f in $shipped) {
        $n = 0
        foreach ($line in Get-Content -LiteralPath $f.FullName) {
            $n++
            if ($line -match '^\s*#') { continue }
            if ($line -match '(?<![%\w])[A-Za-z]:\\' -or $line -match '\\Users\\') { "$($f.Name):$n" }
        }
    }
    Check 'no shipped file hard-codes a drive path or a user folder' (@($hits).Count -eq 0) (@($hits) -join ', ')
} finally {
    Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue
}
"passed=$script:pass failed=$script:fail"
exit $script:fail
