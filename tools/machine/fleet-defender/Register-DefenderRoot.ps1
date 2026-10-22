# Register-DefenderRoot.ps1 -- call from any project, unelevated, when it creates a new heavy-write root:
#   pwsh -NoProfile -File "$env:ProgramData\FleetDefender\Register-DefenderRoot.ps1" -Path <root> -Project <name> -Reason "<why>"
# Appends one request row (idempotent). The elevated FleetDefenderRoots task applies it within 15 minutes if
# the machine's admin-only policy allows it; otherwise the next session start prints an owner command.
# It never touches Defender and needs no elevation. If the tool is not installed, the row still lands and
# waits for the install.
param(
    [Parameter(Mandatory)][string]$Path,
    [Parameter(Mandatory)][string]$Project,
    [string]$Reason = '',
    [string]$ManifestPath = (Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'fleet\defender-roots.json')
)
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'FleetDefenderRoots.psm1') -Force
$result = Add-RootRequest -ManifestPath $ManifestPath -Path $Path -Project $Project -Reason $Reason
"${result}: $(ConvertTo-RootPath $Path)"
