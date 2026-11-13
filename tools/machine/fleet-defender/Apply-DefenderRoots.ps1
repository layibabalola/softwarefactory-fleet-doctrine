# Apply-DefenderRoots.ps1 -- the body of the FleetDefenderRoots SYSTEM task. Runs from the admin-only install
# dir (%ProgramData%\FleetDefender). Reads the USER-writable request manifest and adds a Defender path
# exclusion ONLY for requests the ADMIN-only policy.json allows. Everything else stays pending, with a
# copy-paste command, for the owner. Never removes an exclusion. Never edits its own policy.
#
# -DryRun: no Defender call at all (reads -CurrentExclusions instead of Get-MpPreference, adds nothing), so the
# whole pass can be exercised unelevated. The status file says dryRun=true.
param(
    [string]$PolicyPath = (Join-Path $PSScriptRoot 'policy.json'),
    [switch]$DryRun,
    [string[]]$CurrentExclusions = @(),
    [string]$LogDir = (Join-Path $PSScriptRoot 'log')
)
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'FleetDefenderRoots.psm1') -Force
$policy = Read-JsonFile $PolicyPath
$manifestPath = [string]$policy.manifestPath
$statusPath   = [string]$policy.statusPath
$now = (Get-Date).ToUniversalTime()

$requests = @(); $manifestError = $null
try { $requests = @((Read-RootManifest $manifestPath).roots) } catch { $manifestError = $_.Exception.Message }

$current = if ($DryRun) { $CurrentExclusions } else { @((Get-MpPreference).ExclusionPath) }
$fso = if ($IsWindows -or $PSVersionTable.PSEdition -eq 'Desktop') { try { New-Object -ComObject Scripting.FileSystemObject } catch { $null } } else { $null }
$shortPath = {
    param($p)
    if (-not $fso -or -not (Test-Path -LiteralPath $p -PathType Container)) { return $null }
    try { return $fso.GetFolder($p).ShortPath } catch { return $null }
}
$isLink = {
    param($p)
    $cur = $p
    while ($cur) {
        $item = Get-Item -LiteralPath $cur -Force -ErrorAction SilentlyContinue
        if ($item -and ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) { return $true }
        $parent = Split-Path -Parent $cur
        if (-not $parent -or $parent -eq $cur) { break }
        $cur = $parent
    }
    return $false
}
$plan = Invoke-RootPlan -Policy $policy -Requests $requests -CurrentExclusions $current -ShortPath $shortPath -IsLink $isLink
if (-not $DryRun -and $plan.toAdd.Count -gt 0) { Add-MpPreference -ExclusionPath $plan.toAdd }

$status = New-RootStatus $plan $manifestPath $manifestError $now ([bool]$DryRun)
$json = $status | ConvertTo-Json -Depth 6
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $statusPath) | Out-Null
$tmp = "$statusPath.tmp-$PID"   # temp + rename, so the alert never reads a half-written file
[IO.File]::WriteAllText($tmp, $json, [Text.UTF8Encoding]::new($false))
Move-Item -LiteralPath $tmp -Destination $statusPath -Force
if ($plan.applied.Count -gt 0 -or $plan.pending.Count -gt 0 -or $plan.rejected.Count -gt 0 -or $manifestError) {
    New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
    Add-Content -LiteralPath (Join-Path $LogDir 'apply.jsonl') -Value ($status | ConvertTo-Json -Depth 6 -Compress)
}
