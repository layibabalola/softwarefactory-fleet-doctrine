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
    Check 'unquoted (b4bc3fe6) sampler matches' (Test-SamplerCommandLine $pw "$args0 C:\ProgramData\MachineLoad\bin\MachineLoadSampler.ps1" $pw)
    Check 'other executable ignored' (-not (Test-SamplerCommandLine 'C:\Users\u\pwsh.exe' "$args0 `"C:\ProgramData\MachineLoad\bin\MachineLoadSampler.ps1`"" $pw))
    Check 'trailing arguments ignored' (-not (Test-SamplerCommandLine $pw "$args0 C:\ProgramData\MachineLoad\bin\MachineLoadSampler.ps1 -RunMinutes 5" $pw))
    Check 'other script ignored' (-not (Test-SamplerCommandLine $pw "$args0 `"C:\ProgramData\MachineLoad\bin\Other.ps1`"" $pw))
    # 7. the sampler floors a time with ONE clock read (two UtcNow reads stamped the first minute one early)
    $twice = Select-String -Path (Join-Path $PSScriptRoot 'MachineLoadSampler.ps1') -Pattern 'UtcNow\.Ticks.*UtcNow\.Ticks'
    Check 'no double clock read in a floor' ($null -eq $twice) ($twice | ForEach-Object Line)
    Check 'script name in another folder ignored' (-not (Test-SamplerCommandLine $pw "$args0 `"C:\temp\MachineLoadSampler.ps1`"" $pw))
}
finally {
    Get-ChildItem -LiteralPath $base -Recurse -Force -Attributes ReparsePoint -ErrorAction SilentlyContinue | ForEach-Object { $_.Delete() }
    Remove-Item -LiteralPath $base -Recurse -Force -ErrorAction SilentlyContinue
}
Write-Host "Install-MachineLoad.tests: $script:pass passed, $script:fail failed"
exit ([int]($script:fail -gt 0))
