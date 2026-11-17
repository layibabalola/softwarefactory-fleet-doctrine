# Pure checks used by Install-MachineLoad.ps1, kept apart so Install-MachineLoad.tests.ps1 can exercise them
# without elevation. Dot-source only; nothing here changes the machine.

# Atomic write bits only: the composite names (Write, Modify, FullControl) also carry read and Synchronize bits,
# so OR-ing them in flags a correct read-only ACE as writable.
# WriteData/CreateFiles 0x2, AppendData 0x4, WriteEA 0x10, DeleteChild 0x40, WriteAttributes 0x100,
# Delete 0x10000, WRITE_DAC 0x40000, WRITE_OWNER 0x80000, GENERIC_ALL 0x10000000, GENERIC_WRITE 0x40000000.
$script:MLWriteRights = [long](0x2 -bor 0x4 -bor 0x10 -bor 0x40 -bor 0x100 -bor 0x10000 -bor 0x40000 -bor 0x80000 -bor 0x10000000 -bor 0x40000000)

# Files the elevated sampler (and the launcher's --stdout/--stderr) may leave in data. Anything else there is
# refused: the elevated sampler must never read or write a file a non-admin put in place.
$script:MLDataNames = '^(minute-\d{4}-\d{2}-\d{2}\.jsonl|sampler-state\.json|sampler\.log(\.1)?|sampler\.(out|err)\.log|install-receipt\.json)$'

function Test-LockedTree {
    # Returns a list of problems; empty = only $TrustedSids own or can change anything under $Path, and nothing
    # under it is a junction, symlink or hard link (icacls and Get-Acl act on a link itself, not its target, so a
    # pre-planted junction would pass an ACL-only check while pointing at a user-writable folder).
    param([string]$Path, [string[]]$TrustedSids = @('S-1-5-18', 'S-1-5-32-544'))
    $bad = @()
    $root = Get-Item -LiteralPath $Path -Force
    # -Recurse does not follow reparse points (PowerShell 7 needs -FollowSymlink), so a junction is listed, not entered.
    foreach ($item in @($root) + @(Get-ChildItem -LiteralPath $Path -Force -Recurse)) {
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { $bad += "reparse point (junction or symlink) at $($item.FullName)"; continue }
        if (-not $item.PSIsContainer -and $item.LinkType -eq 'HardLink') { $bad += "hard link at $($item.FullName)"; continue }
        $acl = Get-Acl -LiteralPath $item.FullName
        $owner = try { ([Security.Principal.NTAccount]$acl.Owner).Translate([Security.Principal.SecurityIdentifier]).Value } catch { "$($acl.Owner)" }
        if ($owner -notin $TrustedSids) { $bad += "owner $($acl.Owner) on $($item.FullName)" }
        foreach ($ace in $acl.Access) {
            if ($ace.AccessControlType -ne 'Allow') { continue }
            $sid = try { $ace.IdentityReference.Translate([Security.Principal.SecurityIdentifier]).Value } catch { "$($ace.IdentityReference)" }
            if ($sid -in $TrustedSids) { continue }
            if (([long][int]$ace.FileSystemRights -band $script:MLWriteRights) -ne 0) { $bad += "$($ace.IdentityReference) can write ($($ace.FileSystemRights)) on $($item.FullName)" }
        }
    }
    return $bad
}

function Test-InstallContents {
    # bin must hold exactly the files in $Expected (name -> lowercase SHA-256) with those hashes: a planted
    # launcher .config, DLL or extra script would otherwise be loaded by the elevated launcher. data may hold
    # only the sampler's own file names, and no folders.
    param([string]$BinDir, [string]$DataDir, [hashtable]$Expected)
    $bad = @()
    $seen = @{}
    foreach ($i in @(Get-ChildItem -LiteralPath $BinDir -Force)) {
        if ($i.PSIsContainer) { $bad += "unexpected folder in bin: $($i.Name)"; continue }
        $key = $Expected.Keys | Where-Object { $_ -ieq $i.Name } | Select-Object -First 1
        if (-not $key) { $bad += "unexpected file in bin: $($i.Name)"; continue }
        $seen[$key] = $true
        $h = (Get-FileHash -Algorithm SHA256 -LiteralPath $i.FullName).Hash.ToLowerInvariant()
        if ($h -ne $Expected[$key].ToLowerInvariant()) { $bad += "bin\$($i.Name) hash $h is not the source's $($Expected[$key])" }
    }
    foreach ($k in $Expected.Keys) { if (-not $seen[$k]) { $bad += "missing from bin: $k" } }
    if ($DataDir -and (Test-Path -LiteralPath $DataDir)) {
        foreach ($i in @(Get-ChildItem -LiteralPath $DataDir -Force)) {
            if ($i.PSIsContainer) { $bad += "unexpected folder in data: $($i.Name)"; continue }
            if ($i.Name -notmatch $script:MLDataNames) { $bad += "unexpected file in data: $($i.Name)" }
        }
    }
    return $bad
}

function Test-SamplerCommandLine {
    # True only for pwsh 7 itself ($Pwsh) running exactly an installed sampler script, quoted or not (the
    # b4bc3fe6 build launched it unquoted). Never a match on a process name or a script name alone.
    param([string]$ExecutablePath, [string]$CommandLine, [string]$Pwsh)
    if ($ExecutablePath -ne $Pwsh) { return $false }
    return "$CommandLine" -match '-File\s+("[A-Za-z]:\\[^"]*\\MachineLoad\\bin\\MachineLoadSampler\.ps1"|[A-Za-z]:\\\S*\\MachineLoad\\bin\\MachineLoadSampler\.ps1)\s*$'
}
