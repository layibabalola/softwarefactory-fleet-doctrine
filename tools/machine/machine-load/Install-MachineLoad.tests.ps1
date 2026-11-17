#Requires -Version 7.2
# Tests for MachineLoadInstallLib.ps1 (the installer's tree, contents and command-line checks). No elevation,
# no scheduled tasks: builds throwaway trees under TEMP. The current user stands in for Administrators.
# Run: pwsh -NoProfile -File tools/machine/machine-load/Install-MachineLoad.tests.ps1   (exit 0 = all pass)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'MachineLoadInstallLib.ps1')
$script:fail = 0; $script:pass = 0
function Check([string]$Name, [bool]$Ok, $Detail = '') {
    if ($Ok) { $script:pass++ } else { $script:fail++; Write-Host "FAIL: $Name $Detail" }
}
$me = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
$trusted = @('S-1-5-18', 'S-1-5-32-544', $me)
$base = Join-Path ([IO.Path]::GetTempPath()) ("ml-install-tests-" + [guid]::NewGuid().ToString('N').Substring(0, 8))

function New-Tree([string]$Name) {
    $root = Join-Path $base $Name
    foreach ($d in $root, "$root\bin", "$root\data") { $null = New-Item -ItemType Directory -Force -Path $d }
    Set-Content -Path "$root\bin\a.ps1" -Value 'a'
    Set-Content -Path "$root\data\minute-2026-11-17.jsonl" -Value '{}'
    # the installer's shape: inheritance cut, trusted full, Users read+execute
    & icacls.exe $root /inheritance:r /grant:r "*S-1-5-18:(OI)(CI)F" "*S-1-5-32-544:(OI)(CI)F" "*${me}:(OI)(CI)F" '*S-1-5-32-545:(OI)(CI)RX' /Q | Out-Null
    & icacls.exe "$root\*" /reset /T /C /Q | Out-Null
    return $root
}

try {
    $null = New-Item -ItemType Directory -Force -Path $base

    # 1. a correct read-only tree passes (the composite-rights mask once flagged Users RX as writable)
    $ok = New-Tree 'ok'
    $p = @(Test-LockedTree -Path $ok -TrustedSids $trusted)
    Check 'correct RX tree passes' ($p.Count -eq 0) ($p -join '; ')

    # 2. a Users write right anywhere is refused
    $w = New-Tree 'writable'
    & icacls.exe "$w\bin\a.ps1" /grant '*S-1-5-32-545:(M)' /Q | Out-Null
    $p = @(Test-LockedTree -Path $w -TrustedSids $trusted)
    Check 'Users Modify refused' (($p -join ';') -match 'can write') ($p -join '; ')

    # 3. a planted junction is refused (icacls and Get-Acl see only the link itself)
    $j = New-Tree 'junction'
    $target = Join-Path $base 'user-writable-target'
    $null = New-Item -ItemType Directory -Force -Path $target
    Set-Content -Path "$target\evil.ps1" -Value 'x'
    $null = New-Item -ItemType Junction -Path "$j\data\sub" -Target $target
    $p = @(Test-LockedTree -Path $j -TrustedSids $trusted)
    Check 'junction refused' (($p -join ';') -match 'reparse point') ($p -join '; ')
    Check 'junction not entered' (-not (($p -join ';') -match 'evil\.ps1'))

    # 3b. the ROOT itself as a junction is refused
    $p = @(Test-LockedTree -Path "$j\data\sub" -TrustedSids $trusted)
    Check 'root junction refused' (($p -join ';') -match 'reparse point') ($p -join '; ')

    # 4. a planted hard link is refused (an elevated append through it writes the link's target)
    $h = New-Tree 'hardlink'
    $victim = Join-Path $base 'victim.txt'; Set-Content -Path $victim -Value 'v'
    $null = New-Item -ItemType HardLink -Path "$h\data\minute-2026-11-16.jsonl" -Target $victim
    $p = @(Test-LockedTree -Path $h -TrustedSids $trusted)
    Check 'hard link refused' (($p -join ';') -match 'hard link') ($p -join '; ')

    # 5. contents: exact bin set with source hashes; data holds only the sampler's own names
    $c = New-Tree 'contents'
    $exp = @{ 'a.ps1' = (Get-FileHash -Algorithm SHA256 "$c\bin\a.ps1").Hash.ToLowerInvariant() }
    $p = @(Test-InstallContents -BinDir "$c\bin" -DataDir "$c\data" -Expected $exp)
    Check 'exact contents pass' ($p.Count -eq 0) ($p -join '; ')
    Set-Content -Path "$c\bin\pairprog-hidden-task-launcher.exe.config" -Value '<configuration/>'
    Set-Content -Path "$c\data\projects.local.json" -Value '{}'
    foreach ($n in 'sampler.log', 'sampler.log.1', 'sampler.out.log', 'sampler.err.log', 'sampler-state.json', 'install-receipt.json') { Set-Content -Path "$c\data\$n" -Value '' }
    $p = @(Test-InstallContents -BinDir "$c\bin" -DataDir "$c\data" -Expected $exp)
    Check 'planted .config refused' (($p -join ';') -match 'unexpected file in bin: pairprog-hidden-task-launcher\.exe\.config') ($p -join '; ')
    Check 'planted data file refused' (($p -join ';') -match 'unexpected file in data: projects\.local\.json') ($p -join '; ')
    Check 'sampler data names allowed' ($p.Count -eq 2) ($p -join '; ')
    Set-Content -Path "$c\bin\a.ps1" -Value 'tampered'
    $p = @(Test-InstallContents -BinDir "$c\bin" -DataDir $null -Expected ($exp + @{ 'b.cs' = '00' }))
    Check 'hash mismatch refused' (($p -join ';') -match 'is not the source') ($p -join '; ')
    Check 'missing file refused' (($p -join ';') -match 'missing from bin: b\.cs') ($p -join '; ')

    # 6. the sampler is recognised only as pwsh 7 running exactly an installed sampler script
    $pw = 'C:\Program Files\PowerShell\7\pwsh.exe'
    $args0 = '"C:\Program Files\PowerShell\7\pwsh.exe" -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -WindowStyle Hidden -File'
    Check 'quoted sampler matches' (Test-SamplerCommandLine $pw "$args0 `"C:\ProgramData\MachineLoad\bin\MachineLoadSampler.ps1`"" $pw)
    Check 'copy under a user folder ignored' (-not (Test-SamplerCommandLine $pw "$args0 `"C:\Users\victim\MachineLoad\bin\MachineLoadSampler.ps1`"" $pw))
    Check 'unquoted (b4bc3fe6) sampler matches' (Test-SamplerCommandLine $pw "$args0 C:\ProgramData\MachineLoad\bin\MachineLoadSampler.ps1" $pw)
    Check 'other executable ignored' (-not (Test-SamplerCommandLine 'C:\Users\u\pwsh.exe' "$args0 `"C:\ProgramData\MachineLoad\bin\MachineLoadSampler.ps1`"" $pw))
    Check 'trailing arguments ignored' (-not (Test-SamplerCommandLine $pw "$args0 C:\ProgramData\MachineLoad\bin\MachineLoadSampler.ps1 -RunMinutes 5" $pw))
    Check 'other script ignored' (-not (Test-SamplerCommandLine $pw "$args0 `"C:\ProgramData\MachineLoad\bin\Other.ps1`"" $pw))
    # 8. pre-lock: an existing tree owned by someone untrusted, or granting WRITE_DAC to someone untrusted, is
    #    refused before any ACL changes (a handle opened earlier would keep that right)
    $pl = New-Tree 'prelock'
    $p = @(Test-PreLockTree -Path $pl -TrustedSids @('S-1-5-18', 'S-1-5-32-544'))   # owner is me: untrusted here
    Check 'untrusted pre-existing owner refused' (($p -join ';') -match 'pre-existing: owner') ($p -join '; ')
    $p = @(Test-PreLockTree -Path $pl -TrustedSids $trusted)
    Check 'trusted pre-existing tree accepted' ($p.Count -eq 0) ($p -join '; ')
    & icacls.exe "$pl\bin" /grant '*S-1-5-32-545:(WDAC)' /Q | Out-Null
    $p = @(Test-PreLockTree -Path $pl -TrustedSids $trusted)
    Check 'Users WRITE_DAC refused pre-lock' (($p -join ';') -match 'pre-existing: .*can write') ($p -join '; ')
    $pm = New-Tree 'prelock-modify'
    & icacls.exe $pm /grant '*S-1-5-32-545:(M)' /Q | Out-Null      # Modify carries DELETE: the root could be renamed away
    $p = @(Test-PreLockTree -Path $pm -TrustedSids $trusted)
    Check 'Users Modify (DELETE) on the root refused pre-lock' (($p -join ';') -match 'pre-existing: .*can write') ($p -join '; ')

    # 9. a protected directory is born with its final DACL (no inherited ProgramData "Users may create")
    $pd = Join-Path $base 'protected'
    New-ProtectedDirectory -Path $pd
    $acl = Get-Acl $pd
    Check 'protected dir: inheritance cut' $acl.AreAccessRulesProtected
    $usersWrite = $acl.Access | Where-Object { $_.IdentityReference.Translate([Security.Principal.SecurityIdentifier]).Value -eq 'S-1-5-32-545' -and (([long][int]$_.FileSystemRights -band 0x2) -ne 0) }
    Check 'protected dir: Users cannot write' ($null -eq $usersWrite)

    # 10. the sampler's FleetQuiet reader, extracted from the script itself, against a real FleetQuiet record shape
    $ast = [System.Management.Automation.Language.Parser]::ParseFile((Join-Path $PSScriptRoot 'MachineLoadSampler.ps1'), [ref]$null, [ref]$null)
    foreach ($fn in 'Test-QuietWindow', 'ConvertTo-UtcTime') {
        $def = $ast.Find({ param($n) $n -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -eq $fn }, $true)
        . ([scriptblock]::Create($def.Extent.Text))
    }
    $QuietDir = Join-Path $base 'fq-windows'; $null = New-Item -ItemType Directory -Force -Path $QuietDir
    $armed = [DateTime]::new(2026, 11, 17, 10, 0, 0, [DateTimeKind]::Utc); $until = $armed.AddHours(1)
    [ordered]@{ id = 'fq-test'; host = 'X'; armedUtc = $armed.ToString('o'); untilUtc = $until.ToString('o') } | ConvertTo-Json | Set-Content "$QuietDir\fq-test.json"
    Check 'quiet inside an armed window' (Test-QuietWindow $armed.AddMinutes(30))
    Check 'not quiet 6 h off (no local-time shift)' (-not (Test-QuietWindow $armed.AddHours(6).AddMinutes(30)))
    Check 'not quiet after untilUtc' (-not (Test-QuietWindow $until.AddMinutes(1)))
    Move-Item "$QuietDir\fq-test.json" "$QuietDir\fq-test.released"
    Check 'released window is not quiet' (-not (Test-QuietWindow $armed.AddMinutes(30)))

    # 12. the sampler's Core Temp parser (extracted), in Central time: DST gap and repeated hour skipped, never misplaced
    function Write-Log([string]$Message) { }
    $def = $ast.Find({ param($n) $n -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -eq 'Read-CoreTemp' }, $true)
    . ([scriptblock]::Create($def.Extent.Text))
    $script:tz = [TimeZoneInfo]::FindSystemTimeZoneById('Central Standard Time'); $script:tzRead = [DateTime]::UtcNow
    $CoreTempFeed = Join-Path $base 'coretemp.csv'
    Set-Content -Path $CoreTempFeed -Value @('17.11.2026,1:59:59.500,x,70,40', '08.03.2026,2:30:0.000,x,71,41', '01.11.2026,1:30:0.000,x,72,42', 'garbage line')
    $r = Read-CoreTemp ([DateTime]::new(2026, 11, 17, 7, 59, 0, [DateTimeKind]::Utc)) ([DateTime]::new(2026, 11, 17, 8, 0, 0, [DateTimeKind]::Utc))
    Check 'Core Temp 01:59:59.5 CST lands at 07:59Z' ($r.n -eq 1 -and $r.pkg_w[0] -eq 40) "n=$($r.n)"
    Check 'Core Temp age is not negative' ($r.age_s -ge 0) "age=$($r.age_s)"
    $r = Read-CoreTemp ([DateTime]::new(2026, 3, 8, 7, 0, 0, [DateTimeKind]::Utc)) ([DateTime]::new(2026, 3, 8, 10, 0, 0, [DateTimeKind]::Utc))
    Check 'Core Temp spring-forward gap skipped' ($r.n -eq 0) "n=$($r.n)"
    $r = Read-CoreTemp ([DateTime]::new(2026, 11, 1, 5, 0, 0, [DateTimeKind]::Utc)) ([DateTime]::new(2026, 11, 1, 9, 0, 0, [DateTimeKind]::Utc))
    Check 'Core Temp repeated autumn hour skipped' ($r.n -eq 0) "n=$($r.n)"

    # 13. the sampler reads a mutex owner with the static extension form (the instance form does not exist in pwsh 7)
    $mx = [Threading.Mutex]::new($false, "Local\ml-tests-$PID")
    try { $own = [Threading.ThreadingAclExtensions]::GetAccessControl($mx).GetOwner([Security.Principal.SecurityIdentifier]).Value } finally { $mx.Dispose() }
    Check 'mutex owner readable' ($own -eq $me) "owner=$own"
    $src = Get-Content -Raw (Join-Path $PSScriptRoot 'MachineLoadSampler.ps1')
    Check 'sampler uses the static mutex ACL call' ($src -match '\[Threading\.ThreadingAclExtensions\]::GetAccessControl\(\$mutex\)')

    # 11. the sampler task runs as SYSTEM (a logged-on user's environment would load code into elevated pwsh)
    $inst = Get-Content -Raw (Join-Path $PSScriptRoot 'Install-MachineLoad.ps1')
    Check 'sampler principal is SYSTEM' ($inst -match "New-ScheduledTaskPrincipal -UserId 'S-1-5-18' -LogonType ServiceAccount -RunLevel Highest")
    Check 'sampler not registered with a user principal' (-not ($inst -match 'RunLevel Highest\) -Settings'))

    # 7. the sampler floors a time with ONE clock read (two UtcNow reads stamped the first minute one early)
    $twice = Select-String -Path (Join-Path $PSScriptRoot 'MachineLoadSampler.ps1') -Pattern 'UtcNow\.Ticks.*UtcNow\.Ticks'
    Check 'no double clock read in a floor' ($null -eq $twice) ($twice | ForEach-Object Line)
    Check 'script name in another folder ignored' (-not (Test-SamplerCommandLine $pw "$args0 `"C:\temp\MachineLoadSampler.ps1`"" $pw))

    # 14. -Status: the running sampler's 0x800710E0 is benign. LastTaskResult is unsigned, so the literal must be
    # too: plain 0x800710E0 is a negative Int32 and never matched (every healthy machine read as a failed run).
    $m = [regex]::Match($inst, '\{ @\((0x800710E0u?)\) \}')
    $lit = if ($m.Success) { Invoke-Expression $m.Groups[1].Value } else { $null }
    Check '-Status benign code matches an unsigned result' ($m.Success -and ([uint32]2147946720 -in @($lit))) "literal=$($m.Groups[1].Value)"

    # 15. a root that appears between Test-Path and Create is re-checked (Create does not fail on an existing folder)
    Check 'new root re-checked after create' ($inst -match '(?s)New-ProtectedDirectory -Path \$Root\s*\r?\n\s*#[^\n]*\r?\n\s*\$pre = @\(Test-PreLockTree -Path \$Root\)')
}
finally {
    Get-ChildItem -LiteralPath $base -Recurse -Force -Attributes ReparsePoint -ErrorAction SilentlyContinue | ForEach-Object { $_.Delete() }
    Remove-Item -LiteralPath $base -Recurse -Force -ErrorAction SilentlyContinue
}
Write-Host "Install-MachineLoad.tests: $script:pass passed, $script:fail failed"
exit ([int]($script:fail -gt 0))
