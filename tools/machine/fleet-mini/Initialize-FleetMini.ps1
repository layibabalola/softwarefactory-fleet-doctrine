# Brings THIS machine to the fleet mini baseline. Dry run unless -Apply.
#   pwsh -NoProfile -File Initialize-FleetMini.ps1            # show what would change
#   pwsh -NoProfile -File Initialize-FleetMini.ps1 -Apply     # change it
# class user  : applied for the signed-in account (Mouse Keys goes into the console session even when run over ssh).
# class admin : applied only from an elevated shell AND after the owner types this machine's name at an interactive
#               prompt (enforced in code: no interactive input, no machine settings). Agents never apply these.
# class owner : never applied; printed with the exact step for the owner.
# Every change is recorded with its value before and after in a JSON receipt (path printed at the end).
param([switch]$Apply, [string[]]$Only)
$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $PSCommandPath
Import-Module (Join-Path $here 'FleetMini.psm1') -Force

$elevated = Test-FleetMiniElevated
$commit = git -C $here rev-parse HEAD 2>$null
"fleet-mini baseline on $env:COMPUTERNAME  elevated=$elevated  mode=$(if ($Apply) { 'APPLY' } else { 'DRY-RUN' })  bus=$(if ($commit) { $commit.Substring(0, 12) } else { 'unknown' })"

# Machine (admin) settings need the owner at an interactive prompt typing this machine's name. Agents run with no
# interactive stdin, so an elevated agent session (an admin ssh key login) cannot get past this; over ssh the
# owner uses `ssh -t` to get a prompt.
$ownerConfirmed = $false
$pendingAdmin = @(Invoke-FleetMiniCheck -Only $Only | Where-Object { $_.Class -eq 'admin' -and $_.Status -eq 'DRIFT' })
if ($Apply -and $elevated -and $pendingAdmin) {
    if (-not [Environment]::UserInteractive -or [Console]::IsInputRedirected) {
        "machine settings need the owner at an interactive prompt; skipping $($pendingAdmin.Count) admin item(s)"
    } else {
        $typed = Read-Host "OWNER CONFIRMATION: type this machine's name ($env:COMPUTERNAME) to apply $($pendingAdmin.Count) machine setting(s)"
        $ownerConfirmed = ($typed -eq $env:COMPUTERNAME)
        if (-not $ownerConfirmed) { 'name did not match; machine settings skipped' }
    }
}
$acted = @(Invoke-FleetMiniApply -Apply:$Apply -Only $Only -OwnerConfirmed:$ownerConfirmed)
if ($acted) { $acted | Format-Table Id, Class, Before, Action, After -AutoSize -Wrap | Out-String -Width 200 } else { 'user/admin items: nothing to change' }

$owner = @(Invoke-FleetMiniCheck -Only $Only | Where-Object { $_.Class -eq 'owner' -and $_.Status -ne 'OK' })
if ($owner) {
    'Owner steps still open on this machine:'
    foreach ($o in $owner) { "  - $($o.Title) [now: $($o.Current)]`n      why: $($o.Why)`n      do:  $($o.How)" }
}

if ($Apply -and $acted) {
    $dir = if ($elevated) { Join-Path $env:ProgramData 'fleet\fleet-mini\receipts' } else { Join-Path $env:LOCALAPPDATA 'fleet\fleet-mini\receipts' }
    New-Item -ItemType Directory -Force $dir | Out-Null
    $file = Join-Path $dir ((Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ') + '.json')
    [ordered]@{ host = $env:COMPUTERNAME; at = (Get-Date).ToUniversalTime().ToString('o'); bus = $commit; elevated = $elevated; rows = $acted } |
        ConvertTo-Json -Depth 4 | Set-Content $file -Encoding utf8
    "receipt: $file"
}
$left = @(Invoke-FleetMiniCheck -Only $Only | Where-Object Status -ne 'OK')
"remaining drift: $($left.Count) item(s)$(if ($left) { ': ' + (($left | ForEach-Object Id) -join ', ') })"
if ($left) { exit 1 } else { exit 0 }
