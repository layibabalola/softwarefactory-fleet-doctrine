# Fleet mini PC baseline: one table of checks, each with how to read it, what it should be, and who may fix it.
# Classes:
#   user   - per-user preference; the script applies it for the signed-in account (no elevation needed).
#   admin  - routine machine setting; applied only when the OWNER runs Initialize-FleetMini.ps1 -Apply elevated.
#   owner  - security setting, credential, install or account step; never applied by the script, only explained.
# Every item says WHY, so a new machine's owner can decide with the reason in front of them.
Set-StrictMode -Version 3
$script:ModuleFile = $PSCommandPath

function Get-RegValue([string]$Path, [string]$Name) {
    $p = Get-ItemProperty -Path $Path -Name $Name -ErrorAction SilentlyContinue
    if ($null -eq $p) { return $null }
    return $p.$Name
}

function Get-PowerAcSeconds([string]$Sub, [string]$Setting) {
    # The two "...Power Setting Index: 0x..." lines are AC then DC; match the hex, not the (localized) label.
    $hex = @(powercfg /q SCHEME_CURRENT $Sub $Setting 2>$null | ForEach-Object { if ($_ -match ':\s*(0x[0-9a-fA-F]{8})\s*$') { $Matches[1] } })
    if ($LASTEXITCODE -or $hex.Count -lt 2) { throw "powercfg could not read $Sub/$Setting (exit $LASTEXITCODE)" }
    return [Convert]::ToInt32($hex[-2], 16)
}

function Assert-Native([string]$What) {
    if ($LASTEXITCODE) { throw "$What exited $LASTEXITCODE" }
    return 'set'
}

function Test-FleetMiniElevated {
    if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) { return $false }
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    return ([Security.Principal.WindowsPrincipal]$id).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# --- Mouse Keys: read and set through SystemParametersInfo so the change is live, not only stored -------------------
$script:MouseKeysType = $null
function Initialize-MouseKeysType {
    if ($script:MouseKeysType) { return }
    if (-not ('FleetMini.MouseKeys' -as [type])) {
        Add-Type -Namespace FleetMini -Name MouseKeys -MemberDefinition @'
[StructLayout(LayoutKind.Sequential)] public struct MOUSEKEYS { public uint cbSize, dwFlags, iMaxSpeed, iTimeToMaxSpeed, iCtrlSpeed, dwReserved1, dwReserved2; }
[DllImport("user32.dll", SetLastError=true)] public static extern bool SystemParametersInfoW(uint a, uint b, ref MOUSEKEYS c, uint d);
[DllImport("user32.dll")] public static extern int GetSystemMetrics(int i);
'@
    }
    $script:MouseKeysType = [FleetMini.MouseKeys]
}

# 0x1F = MKF_MOUSEKEYSON|AVAILABLE|HOTKEYACTIVE|CONFIRMHOTKEY|HOTKEYSOUND. MEASURED, not taken from the docs: on a
# Windows 11 25H2 mini, Settings > Accessibility > Mouse with "Mouse keys" On, "Only use mouse keys when Num lock is
# on" ticked and the taskbar icon unticked stored Flags=31 (0x1F), with MKF_REPLACENUMBERS (0x80) CLEAR. The
# documented meaning of 0x80 reads the other way round; the stored value is what the Settings page writes, so it is
# copied exactly. Writing the whole value (not OR-ing bits) reproduces that page state on every mini.
$script:MouseKeysWant = 0x1F

function Set-FleetMiniMouseKeysHere {
    Initialize-MouseKeysType
    $t = [FleetMini.MouseKeys+MOUSEKEYS]
    $m = [Activator]::CreateInstance($t); $m.cbSize = 28
    [void]$script:MouseKeysType::SystemParametersInfoW(0x36, 28, [ref]$m, 0)
    $m.dwFlags = $script:MouseKeysWant
    if ($m.iMaxSpeed -eq 0) { $m.iMaxSpeed = 80 }
    if ($m.iTimeToMaxSpeed -eq 0) { $m.iTimeToMaxSpeed = 3000 }
    # SPI_SETMOUSEKEYS with SPIF_UPDATEINIFILE|SPIF_SENDCHANGE: live now and saved for later sign-ins.
    if (-not $script:MouseKeysType::SystemParametersInfoW(0x37, 28, [ref]$m, 3)) {
        throw "SystemParametersInfo(SPI_SETMOUSEKEYS) failed, error $([Runtime.InteropServices.Marshal]::GetLastWin32Error())"
    }
    return "mousepresent=$($script:MouseKeysType::GetSystemMetrics(19))"
}

function Get-ConsoleSessionId {
    $line = (query user 2>$null) | Where-Object { $_ -match '\bconsole\b' } | Select-Object -First 1
    if ($line -and $line -match '\bconsole\s+(\d+)\s') { return [int]$Matches[1] }
    return $null
}

function Set-FleetMiniMouseKeys {
    # In the console session: set it directly. From ssh (another session), a per-user SPI call would land in the
    # wrong session, so run the same call once inside the console session through a one-shot Interactive task.
    # The stored value is per account (HKCU); the live state belongs to whoever is at the console. When this runs in
    # session 0 with nobody at the console, only the stored value changes, and the result says so.
    $here = (Get-Process -Id $PID).SessionId
    $console = Get-ConsoleSessionId
    if ($console -eq $here) { return Set-FleetMiniMouseKeysHere }
    if ($null -eq $console) {
        $r = Set-FleetMiniMouseKeysHere
        if ($here -eq 0) { return "STORED ONLY (no console session found; live state unchanged until the next sign-in): $r" }
        return $r
    }
    $dir = Join-Path ([IO.Path]::GetTempPath()) ('fleet-mini-' + [Guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Force $dir | Out-Null
    try {
        Copy-Item -LiteralPath $script:ModuleFile -Destination "$dir\FleetMini.psm1"
        $receipt = "$dir\result.txt"
        # run.ps1 embeds no paths ($PSScriptRoot), so a quote or space in the temp path cannot break it; the receipt is
        # written to a temp name and renamed, so a reader never sees half a file.
        @'
$ErrorActionPreference = 'Stop'
try { Import-Module (Join-Path $PSScriptRoot 'FleetMini.psm1') -Force; $out = Set-FleetMiniMouseKeysHere }
catch { $out = "ERROR: $_" }
Set-Content -LiteralPath (Join-Path $PSScriptRoot 'result.tmp') -Value $out
Move-Item -LiteralPath (Join-Path $PSScriptRoot 'result.tmp') -Destination (Join-Path $PSScriptRoot 'result.txt') -Force
'@ | Set-Content "$dir\run.ps1" -Encoding utf8
        $ps = Join-Path $env:WINDIR 'System32\WindowsPowerShell\v1.0\powershell.exe'
        $conhost = Join-Path $env:WINDIR 'System32\conhost.exe'
        $name = 'FleetMini-OneShot-' + [Guid]::NewGuid().ToString('N').Substring(0, 8)
        $action = New-ScheduledTaskAction -Execute $conhost -Argument "--headless `"$ps`" -NoProfile -NonInteractive -ExecutionPolicy Bypass -File `"$dir\run.ps1`""
        $principal = New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
        Register-ScheduledTask -TaskName $name -Action $action -Principal $principal -Force | Out-Null
        try {
            Start-ScheduledTask -TaskName $name
            for ($i = 0; $i -lt 30 -and -not (Test-Path $receipt); $i++) { Start-Sleep -Seconds 1 }
        } finally { Unregister-ScheduledTask -TaskName $name -Confirm:$false -ErrorAction SilentlyContinue }
        if (-not (Test-Path $receipt)) { throw 'console-session task left no result in 30 s (state UNKNOWN, not a failure proof)' }
        $r = "$(Get-Content -LiteralPath $receipt -Raw)"
        if ($r -match '^ERROR:') { throw $r.Trim() }
        return "console session $console`: $($r.Trim())"
    } finally { Remove-Item -Recurse -Force $dir -ErrorAction SilentlyContinue }
}

# --- The baseline ---------------------------------------------------------------------------------------------------
function New-FleetMiniItem($Id, $Class, $Title, $Why, [scriptblock]$Get, [scriptblock]$Ok, [scriptblock]$Fix, [string]$How) {
    [pscustomobject]@{ Id = $Id; Class = $Class; Title = $Title; Why = $Why; Get = $Get; Ok = $Ok; Fix = $Fix; How = $How }
}

function Get-FleetMiniItems {
    $items = @(
        New-FleetMiniItem 'mouse-keys' 'user' 'Mouse Keys on (keypad mouse while Num Lock is on)' `
            'A headless mini has no mouse attached, so Windows hides the pointer and remote-control input (TeamViewer and similar) cannot drag a window edge to resize it. Mouse Keys makes Windows treat the session as having a pointing device. Measured: SM_MOUSEPRESENT 0 -> 1, edge drag works again.' `
            { $f = Get-RegValue 'HKCU:\Control Panel\Accessibility\MouseKeys' 'Flags'; if ($null -eq $f) { $null } else { [int]$f } } `
            { param($v) $null -ne $v -and (([int]$v) -band 1) -eq 1 } `
            { Set-FleetMiniMouseKeys } ''
        New-FleetMiniItem 'git-longpaths' 'user' 'git core.longpaths=true' `
            'Worktrees under deep paths fail to check out without it, even with the OS long-path switch on.' `
            { $v = git config --global core.longpaths 2>$null; if ($v) { "$v".Trim() } else { $null } } `
            { param($v) $v -eq 'true' } `
            { git config --global core.longpaths true; Assert-Native 'git config' } ''
        New-FleetMiniItem 'sleep-never' 'admin' 'Never sleep on AC power' `
            'A sleeping mini drops ssh, scheduled lanes and remote control; nobody is at the keyboard to wake it.' `
            { Get-PowerAcSeconds SUB_SLEEP STANDBYIDLE } { param($v) $v -eq 0 } `
            { powercfg /change standby-timeout-ac 0; Assert-Native 'powercfg' } ''
        New-FleetMiniItem 'hibernate-never' 'admin' 'Never hibernate on AC power' 'Same reason as sleep.' `
            { Get-PowerAcSeconds SUB_SLEEP HIBERNATEIDLE } { param($v) $v -eq 0 } `
            { powercfg /change hibernate-timeout-ac 0; Assert-Native 'powercfg' } ''
        New-FleetMiniItem 'fast-startup-off' 'admin' 'Fast startup off' `
            'Fast startup turns a shutdown into a hibernate, so a "restart" may not reload drivers or services and uptime lies.' `
            { Get-RegValue 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power' 'HiberbootEnabled' } { param($v) $v -eq 0 } `
            { Set-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power' -Name HiberbootEnabled -Value 0 -Type DWord; "set" } ''
        New-FleetMiniItem 'long-paths' 'admin' 'Win32 long paths enabled' 'Deep worktree and node_modules paths exceed 260 characters.' `
            { Get-RegValue 'HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem' 'LongPathsEnabled' } { param($v) $v -eq 1 } `
            { Set-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem' -Name LongPathsEnabled -Value 1 -Type DWord; "set" } ''
        New-FleetMiniItem 'w32time-auto' 'admin' 'Windows Time service Automatic' `
            'Ledgers, receipts and token expiry compare clocks across machines; a drifting clock breaks ordering.' `
            { $s = Get-Service w32time -ErrorAction SilentlyContinue; if ($s) { "$($s.StartType)" } else { $null } } { param($v) $v -eq 'Automatic' } `
            { Set-Service w32time -StartupType Automatic; Start-Service w32time -ErrorAction SilentlyContinue; "set" } ''
        New-FleetMiniItem 'exec-policy' 'admin' 'LocalMachine execution policy RemoteSigned (pwsh 7 and Windows PowerShell 5.1)' `
            'Fleet scripts run locally under both shells; Unrestricted prompts on downloaded files and Restricted (the 5.1 default on client Windows) blocks them. The two shells keep separate machine policies.' `
            { $p51 = Get-RegValue 'HKLM:\SOFTWARE\Microsoft\PowerShell\1\ShellIds\Microsoft.PowerShell' 'ExecutionPolicy'
              $p7 = if ($PSVersionTable.PSEdition -eq 'Core') { "$(Get-ExecutionPolicy -Scope LocalMachine)" } else { 'n/a' }
              "ps7=$p7 ps51=$(if ($p51) { $p51 } else { 'Restricted(default)' })" } `
            { param($v) $v -in 'ps7=RemoteSigned ps51=RemoteSigned', 'ps7=n/a ps51=RemoteSigned' } `
            { if ($PSVersionTable.PSEdition -eq 'Core') { Set-ExecutionPolicy RemoteSigned -Scope LocalMachine -Force }
              & (Join-Path $env:WINDIR 'System32\WindowsPowerShell\v1.0\powershell.exe') -NoProfile -NonInteractive -Command 'Set-ExecutionPolicy RemoteSigned -Scope LocalMachine -Force'
              Assert-Native 'powershell.exe Set-ExecutionPolicy' } ''
        New-FleetMiniItem 'sshd' 'admin' 'OpenSSH server running and Automatic' `
            'ssh is how every other fleet machine drives this one (the key mesh).' `
            { $s = Get-Service sshd -ErrorAction SilentlyContinue; if ($s) { "$($s.Status)/$($s.StartType)" } else { $null } } `
            { param($v) $v -eq 'Running/Automatic' } `
            { if (-not (Get-Service sshd -ErrorAction SilentlyContinue)) { throw 'sshd not installed: owner runs Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0' }
              Set-Service sshd -StartupType Automatic; Start-Service sshd; "set" } ''
        New-FleetMiniItem 'ssh-default-shell' 'admin' 'ssh default shell is PowerShell 7' `
            'Remote commands are written for pwsh 7; cmd.exe as the ssh shell mangles them.' `
            { Get-RegValue 'HKLM:\SOFTWARE\OpenSSH' 'DefaultShell' } `
            { param($v) $v -and ($v -like '*\PowerShell\7\pwsh.exe') } `
            { $p = Join-Path $env:ProgramFiles 'PowerShell\7\pwsh.exe'; if (-not (Test-Path $p)) { throw "pwsh 7 not at $p" }
              New-Item -Path 'HKLM:\SOFTWARE\OpenSSH' -Force | Out-Null
              New-ItemProperty -Path 'HKLM:\SOFTWARE\OpenSSH' -Name DefaultShell -Value $p -PropertyType String -Force | Out-Null; "set" } ''
        New-FleetMiniItem 'smart-app-control-off' 'owner' 'Smart App Control off' `
            'While on, it intermittently blocks freshly built test DLLs, so local test results cannot be trusted. Turning it back on needs a Windows reset.' `
            { Get-RegValue 'HKLM:\SYSTEM\CurrentControlSet\Control\CI\Policy' 'VerifiedAndReputablePolicyState' } { param($v) $v -eq 0 } $null `
            'Windows Security > App & browser control > Smart App Control > Off, then restart.'
        New-FleetMiniItem 'auto-sign-in' 'owner' 'Automatic sign-in, no plaintext password' `
            'After a power cut or update restart the mini must come back to a signed-in desktop, or remote control, the console-session tasks and visible sign-in windows have nothing to attach to.' `
            { $a = Get-RegValue 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon' 'AutoAdminLogon'
              $plain = [bool](Get-RegValue 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon' 'DefaultPassword')
              "AutoAdminLogon=$a plaintextPassword=$plain" } `
            { param($v) $v -eq 'AutoAdminLogon=1 plaintextPassword=False' } $null `
            'Run Sysinternals Autologon (winget install Microsoft.Sysinternals.Autologon) and type the password there; it stores it as an LSA secret. If a Microsoft-account PIN blocks it, turn off "For improved security, only allow Windows Hello sign-in" first. Never put the password in DefaultPassword.'
        New-FleetMiniItem 'display-present' 'owner' 'A display is attached (HDMI emulator or capture device)' `
            'With no display, Windows falls back to a tiny virtual screen and remote-control views shrink to it.' `
            { @(Get-CimInstance -Namespace root\wmi WmiMonitorBasicDisplayParams -ErrorAction SilentlyContinue | Where-Object Active).Count } `
            { param($v) $v -ge 1 } $null 'Plug an HDMI EDID emulator (dummy plug) or an HDMI capture device into the mini.'
        New-FleetMiniItem 'remote-control' 'owner' 'TeamViewer service installed and Automatic' `
            'The graphical way in when ssh is not enough; it must start before anyone signs in.' `
            { $s = Get-Service TeamViewer -ErrorAction SilentlyContinue; if ($s) { "$($s.Status)/$($s.StartType)" } else { $null } } `
            { param($v) $v -eq 'Running/Automatic' } $null 'winget install TeamViewer.TeamViewer, then sign in and assign the device to your account (unattended access).'
        New-FleetMiniItem 'tailscale' 'owner' 'Tailscale installed' 'The ssh mesh reaches minis by Tailscale address off the LAN.' `
            { Test-Path (Join-Path $env:ProgramFiles 'Tailscale\tailscale.exe') } { param($v) $v -eq $true } $null `
            'winget install Tailscale.Tailscale, then sign in to the tailnet.'
        New-FleetMiniItem 'ssh-authorized-keys' 'owner' 'administrators_authorized_keys present' `
            'Admin accounts read keys from ProgramData, not ~/.ssh; without it no fleet machine can reach this one.' `
            { Test-Path (Join-Path $env:ProgramData 'ssh\administrators_authorized_keys') } { param($v) $v -eq $true } $null `
            'Authorize each fleet machine''s public key in %ProgramData%\ssh\administrators_authorized_keys (ACL: Administrators and SYSTEM only), and add a Host entry for this mini on each of them. The keys are yours to approve.'
    )
    $tools = [ordered]@{
        git = 'winget install Git.Git'; pwsh = 'winget install Microsoft.PowerShell'; gh = 'winget install GitHub.cli'
        node = 'winget install OpenJS.NodeJS'; python = 'winget install Python.Python.3.14'
        dotnet = 'winget install Microsoft.DotNet.SDK.10'
        claude = 'npm install -g @anthropic-ai/claude-code, then claude auth login'
        codex = 'npm install -g @openai/codex, then codex login'
    }
    foreach ($t in $tools.Keys) {
        $name = $t
        # python: Windows ships a WindowsApps "python.exe" alias that only opens the Store, so being on PATH proves
        # nothing; ask it for a version instead.
        $get = if ($name -eq 'python') {
            { $o = "$(& python -V 2>&1)"; if ($LASTEXITCODE -eq 0 -and $o -match 'Python 3') { $true } else { $false } }
        } else { [scriptblock]::Create("[bool](Get-Command '$name' -ErrorAction SilentlyContinue)") }
        $items += New-FleetMiniItem "tool-$name" 'owner' "$name on PATH" 'Every lane and fleet script assumes the same toolchain on every mini.' `
            $get { param($v) $v -eq $true } $null $tools[$t]
    }
    return $items
}

function Invoke-FleetMiniCheck {
    [CmdletBinding()] param([string[]]$Only)
    $all = @(Get-FleetMiniItems)
    # `pwsh -File ... -Only a,b` passes one string "a,b"; an unknown id must fail loudly, never read as "all clear".
    $Only = @($Only | ForEach-Object { "$_" -split ',' } | ForEach-Object Trim | Where-Object { $_ })
    $unknown = @($Only | Where-Object { $_ -notin $all.Id })
    if ($unknown) { throw "unknown baseline id(s): $($unknown -join ', '). Known: $($all.Id -join ', ')" }
    foreach ($i in $all) {
        if ($Only -and $Only -notcontains $i.Id) { continue }
        $cur = $null; $err = $null
        try { $cur = & $i.Get } catch { $err = "$_" }
        $ok = $false
        if (-not $err) { try { $ok = [bool](& $i.Ok $cur) } catch { $err = "$_" } }
        [pscustomobject]@{
            Id = $i.Id; Class = $i.Class
            Status = if ($err) { 'UNKNOWN' } elseif ($ok) { 'OK' } else { 'DRIFT' }
            Current = if ($err) { $err } elseif ($null -eq $cur) { '<none>' } else { "$cur" }
            Title = $i.Title; Why = $i.Why; How = $i.How
        }
    }
}

function Invoke-FleetMiniApply {
    # Applies DRIFT items of class user (always) and admin (only when elevated). Never touches class owner.
    # Returns one receipt row per item it acted on or skipped, with the value before and after.
    [CmdletBinding()] param([switch]$Apply, [string[]]$Only)
    $elevated = Test-FleetMiniElevated
    foreach ($row in Invoke-FleetMiniCheck -Only $Only) {
        if ($row.Status -ne 'DRIFT' -or $row.Class -eq 'owner') { continue }
        $item = Get-FleetMiniItems | Where-Object Id -eq $row.Id
        $r = [ordered]@{ Id = $row.Id; Class = $row.Class; Before = $row.Current; Action = $null; After = $null }
        if ($row.Class -eq 'admin' -and -not $elevated) { $r.Action = 'SKIPPED-NEEDS-ELEVATION' }
        elseif (-not $Apply) { $r.Action = 'WOULD-SET' }
        else {
            try { $r.Action = "SET: $(& $item.Fix)" } catch { $r.Action = "FAILED: $_" }
            $r.After = (Invoke-FleetMiniCheck -Only $row.Id).Current
        }
        [pscustomobject]$r
    }
}

Export-ModuleMember -Function Get-FleetMiniItems, Invoke-FleetMiniCheck, Invoke-FleetMiniApply, Test-FleetMiniElevated, Set-FleetMiniMouseKeysHere, Set-FleetMiniMouseKeys
