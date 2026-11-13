#Requires -Version 7
# Install-FleetDefenderRoots.ps1 -- the OWNER runs this ELEVATED, once per machine, from a bus clone checked out
# at a commit they reviewed. Agents never run it: adding Defender exclusions is a security setting.
#
#   pwsh -NoProfile -File <bus>\tools\machine\fleet-defender\Install-FleetDefenderRoots.ps1 [-LocalPolicy <file>]
#
# It (1) merges policy.defaults.json with the optional per-machine override into an expanded policy.json,
# (2) copies the applier, its module and the two unelevated helpers into %ProgramData%\FleetDefender, writable
# by Administrators/SYSTEM only (so no unelevated agent can change what the elevated task does), (3) registers a
# SYSTEM task that applies allowed requests every 15 minutes and at startup, (4) adds the SessionStart alert to
# the owner's ~/.claude/settings.json, (5) runs the applier once and prints its status. Re-run to update; it is
# idempotent. Uninstall:
#   Unregister-ScheduledTask -TaskName FleetDefenderRoots -TaskPath '\Fleet\' -Confirm:$false
#   Remove-Item "$env:ProgramData\FleetDefender" -Recurse -Force      (exclusions already added stay)
param(
    [string]$LocalPolicy,
    [string]$TaskPath = '\Fleet\',
    [switch]$NoClaudeHook,
    [switch]$AllowDirty
)
$ErrorActionPreference = 'Stop'
$id = [Security.Principal.WindowsIdentity]::GetCurrent()
if (-not ([Security.Principal.WindowsPrincipal]$id).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { throw 'Run elevated (the owner, once per machine).' }
$src = $PSScriptRoot
Import-Module (Join-Path $src 'FleetDefenderRoots.psm1') -Force
$taskName = 'FleetDefenderRoots'
$shipped = 'FleetDefenderRoots.psm1', 'Apply-DefenderRoots.ps1', 'Register-DefenderRoot.ps1', 'Show-DefenderRootsAlert.ps1'

# Provenance: the bytes about to run as SYSTEM must be the reviewed commit's, so a dirty tool dir is refused.
$commit = $null
$top = (& git -C $src rev-parse --show-toplevel 2>$null)
if ($LASTEXITCODE -eq 0 -and $top) {
    $commit = (& git -C $src rev-parse HEAD).Trim()
    $dirty = @(& git -C $src status --porcelain -- . 2>$null)
    if ($dirty.Count -gt 0 -and -not $AllowDirty) { throw "tool dir differs from $commit (pass -AllowDirty only for bytes you reviewed):`n$($dirty -join "`n")" }
} elseif (-not $AllowDirty) { throw 'not run from a git clone of the bus: provenance unknown (pass -AllowDirty only for bytes you reviewed)' }

# Plan everything before the first write: a bad override fails here and changes nothing.
$local = [Environment]::GetFolderPath('LocalApplicationData')   # the installing owner's profile
$fleet = Join-Path $local 'fleet'
$manifest = Join-Path $fleet 'defender-roots.json'
$dst = Join-Path ([Environment]::GetFolderPath('CommonApplicationData')) 'FleetDefender'
# Status is written by SYSTEM into the admin-only dir (users read it), so no unelevated writer can forge the
# alert the owner acts on. Only the request manifest is user-writable, and it is only ever data.
$statusPath = Join-Path $dst 'status.json'
$localDoc = if ($LocalPolicy) { Read-JsonFile (Resolve-Path -LiteralPath $LocalPolicy).Path } else { $null }
$policy = Merge-FleetDefenderPolicy -Defaults (Read-JsonFile (Join-Path $src 'policy.defaults.json')) -Local $localDoc `
    -Tokens (Get-DefaultTokenMap) -ManifestPath $manifest -StatusPath $statusPath
$pwsh = Join-Path $PSHOME 'pwsh.exe'

New-Item -ItemType Directory -Force -Path $dst, $fleet | Out-Null
if ((Get-Item -LiteralPath $dst -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "refusing: $dst is a link or junction" }
# Lock the install dir BEFORE writing into it: owner Administrators; SYSTEM + Administrators full, Users
# read/execute, no inheritance from %ProgramData% (where any user may create folders, so a pre-created dir must
# not keep its creator's rights).
$acl = New-Object Security.AccessControl.DirectorySecurity
$acl.SetOwner((New-Object Security.Principal.SecurityIdentifier 'S-1-5-32-544'))
$acl.SetAccessRuleProtection($true, $false)
$inh = [Security.AccessControl.InheritanceFlags]'ContainerInherit,ObjectInherit'
$none = [Security.AccessControl.PropagationFlags]::None
foreach ($sid in 'S-1-5-18', 'S-1-5-32-544') {
    $acl.AddAccessRule((New-Object Security.AccessControl.FileSystemAccessRule((New-Object Security.Principal.SecurityIdentifier $sid), 'FullControl', $inh, $none, 'Allow')))
}
$acl.AddAccessRule((New-Object Security.AccessControl.FileSystemAccessRule((New-Object Security.Principal.SecurityIdentifier 'S-1-5-32-545'), 'ReadAndExecute', $inh, $none, 'Allow')))
Set-Acl -LiteralPath $dst -AclObject $acl
Get-ChildItem -LiteralPath $dst -Recurse -Force | ForEach-Object {
    if ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "refusing: $($_.FullName) is a link or junction inside the install dir" }
    $a = Get-Acl -LiteralPath $_.FullName
    $a.SetOwner((New-Object Security.Principal.SecurityIdentifier 'S-1-5-32-544')); $a.SetAccessRuleProtection($false, $false)
    foreach ($rule in @($a.Access | Where-Object { -not $_.IsInherited })) { [void]$a.RemoveAccessRule($rule) }
    Set-Acl -LiteralPath $_.FullName -AclObject $a
}
foreach ($f in $shipped) { Copy-Item -LiteralPath (Join-Path $src $f) -Destination $dst -Force }
[IO.File]::WriteAllText((Join-Path $dst 'policy.json'), ($policy | ConvertTo-Json -Depth 5), [Text.UTF8Encoding]::new($false))
[IO.File]::WriteAllText((Join-Path $dst 'install.json'), ([ordered]@{
    schema = 'fleet-defender-install.v1'; installedUtc = (Get-Date).ToUniversalTime().ToString('o'); busCommit = $commit
    dirtyAllowed = [bool]$AllowDirty; localPolicy = $LocalPolicy; taskPath = $TaskPath; files = $shipped
} | ConvertTo-Json -Depth 4), [Text.UTF8Encoding]::new($false))
if (-not (Test-Path -LiteralPath $manifest)) {
    [IO.File]::WriteAllText($manifest, ([ordered]@{ schema = 'defender-roots.v1'; roots = @() } | ConvertTo-Json), [Text.UTF8Encoding]::new($false))
}

# One task per machine: a copy registered under another folder by an earlier install is replaced.
Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue | Where-Object { $_.TaskPath -ne $TaskPath } | ForEach-Object {
    Unregister-ScheduledTask -TaskName $taskName -TaskPath $_.TaskPath -Confirm:$false
    "replaced earlier task $($_.TaskPath)$taskName"
}
$action = New-ScheduledTaskAction -Execute $pwsh -Argument "-NoLogo -NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$dst\Apply-DefenderRoots.ps1`""
$t1 = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 15) -RepetitionDuration (New-TimeSpan -Days 3650)
$t2 = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 5) -MultipleInstances IgnoreNew -StartWhenAvailable
Register-ScheduledTask -TaskName $taskName -TaskPath $TaskPath -Action $action -Trigger $t1, $t2 -Principal $principal -Settings $settings -Description 'Adds Defender exclusions for allowed fleet write roots requested in %LOCALAPPDATA%\fleet\defender-roots.json; anything else is left pending for the owner.' -Force | Out-Null

# The alert as a user-level Claude Code SessionStart hook (idempotent; backup kept beside it).
# An entry naming the alert script with any other command (an older install dir) is replaced, not duplicated.
$settingsPath = Join-Path $env:USERPROFILE '.claude\settings.json'
$hookCmd = "pwsh -NoProfile -NonInteractive -File `"$dst\Show-DefenderRootsAlert.ps1`""
if ($NoClaudeHook) { 'SessionStart hook skipped (-NoClaudeHook)' }
elseif (-not (Test-Path -LiteralPath $settingsPath)) { "no $settingsPath (Claude Code not set up for this account): SessionStart hook NOT registered; add a SessionStart command hook: $hookCmd" }
else { Set-RootAlertHook -SettingsPath $settingsPath -HookCommand $hookCmd }

& $pwsh -NoProfile -ExecutionPolicy Bypass -File "$dst\Apply-DefenderRoots.ps1"
"installed $TaskPath$taskName from bus commit $commit; status: $statusPath"
Get-Content -LiteralPath $statusPath -Raw
