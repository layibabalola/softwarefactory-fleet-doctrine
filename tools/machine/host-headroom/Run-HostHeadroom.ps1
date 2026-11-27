<#
  Entry point the scheduled tasks call (from the INSTALLED copy, never from a bus checkout - law 1).
    -Mode Sample   one 5-minute sampling pass (task "HostHeadroom Sampler", every 5 min)
    -Mode Publish  7-day summary, pushed to host-headroom/<MACHINE>.json on change or when stale
    -Mode Summary  print the summary as JSON (read-only; what the fleet reader's -Live calls)
    -Mode Dashboard  rebuild this machine's card and the fleet dashboard page (task "HostHeadroom Dashboard", every 10 min)
  Every run appends one receipt line to %LOCALAPPDATA%\HostHeadroom\runs.jsonl, success or not.
#>
[CmdletBinding()]
param(
    [ValidateSet('Sample', 'Publish', 'Summary', 'Dashboard')][string]$Mode = 'Summary',
    [double]$Hours = 168,
    [string]$BusRoot = (Join-Path $env:LOCALAPPDATA 'HostHeadroom\bus'),
    [switch]$NoPush
)
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'HostHeadroom.psm1') -Force
$root = Join-Path $env:LOCALAPPDATA 'HostHeadroom'
New-Item -ItemType Directory -Path $root -Force | Out-Null
$started = [datetime]::UtcNow
$receipt = [ordered]@{ at = $started.ToString('yyyy-MM-ddTHH:mm:ssZ'); mode = $Mode; pid = $PID; ok = $false }
$code = 0
try {
    switch ($Mode) {
        'Sample'  { Invoke-HostHeadroomSampler; $receipt.ok = $true }
        'Publish' { $r = Publish-HostHeadroom -BusRoot $BusRoot -Hours $Hours -NoPush:$NoPush; $receipt.result = $r; $receipt.ok = $true }
        'Summary' { Get-HostHeadroomSummary -Hours $Hours | ConvertTo-Json -Depth 8 -Compress; $receipt.ok = $true }
        'Dashboard' { $receipt.result = ((& (Join-Path $PSScriptRoot 'Build-FleetDashboard.ps1')) -join ' '); $receipt.ok = $true }
    }
} catch {
    $receipt.error = "$($_.Exception.Message)"; $code = 1
    [Console]::Error.WriteLine("host-headroom $Mode failed: $($_.Exception.Message)")
} finally {
    $receipt.seconds = [math]::Round(([datetime]::UtcNow - $started).TotalSeconds, 1)
    Add-SharedLine (Join-Path $root 'runs.jsonl') ($receipt | ConvertTo-Json -Compress -Depth 4)
}
exit $code
