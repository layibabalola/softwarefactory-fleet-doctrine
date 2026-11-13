# Show-DefenderRootsAlert.ps1 -- Claude Code SessionStart hook. Silent unless something needs the owner.
# Never applies anything; it only prints the owner command from the elevated task's status file. Always exits 0.
param(
    [string]$InstallDir = (Join-Path ([Environment]::GetFolderPath('CommonApplicationData')) 'FleetDefender'),
    [string]$StatusPath = ''
)
# The status file lives in the admin-only install dir: only the SYSTEM task can write it.
if (-not $StatusPath) { $StatusPath = Join-Path $InstallDir 'status.json' }
$ErrorActionPreference = 'SilentlyContinue'
try {
    # Not installed on this machine: nothing to say (Register-DefenderRoot rows wait for the install).
    if (-not (Test-Path -LiteralPath (Join-Path $InstallDir 'Apply-DefenderRoots.ps1'))) { exit 0 }
    Import-Module (Join-Path $PSScriptRoot 'FleetDefenderRoots.psm1') -Force -ErrorAction Stop
    # The SYSTEM task is invisible to an unelevated session (Get-ScheduledTask returns nothing, schtasks says
    # Access is denied), so liveness is judged from the status file the task rewrites every run.
    $status = if (Test-Path -LiteralPath $StatusPath) { Read-JsonFile $StatusPath } else { $null }
    Format-RootAlert -Status $status -StatusPath $StatusPath
} catch { "[defender-roots] alert check failed: $($_.Exception.Message)" }
exit 0
