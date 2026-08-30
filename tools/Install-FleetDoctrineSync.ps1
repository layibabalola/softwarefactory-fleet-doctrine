<#
.SYNOPSIS
Register (or re-point) the OS-level scheduled task that runs Sync-FleetDoctrine.ps1
for one fleet project.

.DESCRIPTION
OS-level, not app-resident. App-resident schedulers were retired fleet-wide after their
registry desynced on an account rotation (22 task dirs on disk, ZERO enumerated live) and
because creating one hard-prompts the operator regardless of permission mode.

This installer refuses to arm on minute marks it was not explicitly given, because the
MINUTE REGISTRY ruling exists for a measured reason: uncoordinated schedules collided and
were silently skipped under `reason: "global_limit"`. Claim your marks in RULINGS.md first.

Registering a task is not evidence it runs. After install, read
<ProjectRoot>\.claude-state\doctrine\last-run.json and confirm a fresh stamp on the next
mark. -Verify does exactly that and nothing else.

.PARAMETER MinuteMarks
Minutes past the hour, 0-59, already claimed by this project in RULINGS.md.

.PARAMETER Verify
Do not install. Report whether the task exists, and when it last actually ran.
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)][ValidatePattern('^[a-z0-9][a-z0-9-]{1,63}$')][string]$ProjectId,
    [Parameter(Mandatory)][string]$ProjectRoot,
    [Parameter(Mandatory)][string]$BusRoot,
    [ValidateCount(1, 12)][ValidateRange(0, 59)][int[]]$MinuteMarks = @(),
    [switch]$NoPush,
    [switch]$Verify
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$taskName = "fleet-doctrine-sync-$ProjectId"
$ProjectRoot = [IO.Path]::GetFullPath($ProjectRoot).TrimEnd('\', '/')
$BusRoot = [IO.Path]::GetFullPath($BusRoot).TrimEnd('\', '/')
$syncScript = Join-Path $BusRoot 'tools\Sync-FleetDoctrine.ps1'

if ($Verify) {
    $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if (-not $task) { Write-Output "ABSENT: no task named $taskName"; exit 1 }
    $info = $task | Get-ScheduledTaskInfo
    $beat = Join-Path $ProjectRoot '.claude-state\doctrine\last-run.json'
    $beatText = if (Test-Path -LiteralPath $beat) {
        (Get-Content -LiteralPath $beat -Raw | ConvertFrom-Json) |
            ForEach-Object { "$($_.ran_utc) $($_.verdict) - $($_.detail)" }
    } else {
        'NO HEARTBEAT - registered but never proven to run'
    }
    Write-Output "TASK    : $taskName state=$($task.State)"
    Write-Output "LASTRUN : $($info.LastRunTime) result=$($info.LastTaskResult) missed=$($info.NumberOfMissedRuns)"
    Write-Output "HEARTBEAT: $beatText"
    exit 0
}

foreach ($p in @($ProjectRoot, $BusRoot, $syncScript)) {
    if (-not (Test-Path -LiteralPath $p)) { throw "Path does not exist: $p" }
}
if ($MinuteMarks.Count -eq 0) {
    throw ('Refusing to arm without explicit -MinuteMarks. Claim this project''s minute ' +
           'marks in RULINGS.md first; uncoordinated marks are silently skipped under the ' +
           'scheduler global limit, which looks exactly like a working task that never fires.')
}
$MinuteMarks = @($MinuteMarks | Sort-Object -Unique)

$pwsh = (Get-Command pwsh -ErrorAction SilentlyContinue)
if (-not $pwsh) { throw 'pwsh (PowerShell 7+) is not on PATH; the task needs an absolute interpreter.' }

$argLine = @(
    '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'RemoteSigned',
    '-File', ('"{0}"' -f $syncScript),
    '-ProjectId', $ProjectId,
    '-ProjectRoot', ('"{0}"' -f $ProjectRoot),
    '-BusRoot', ('"{0}"' -f $BusRoot)
)
if ($NoPush) { $argLine += '-NoPush' }

$action = New-ScheduledTaskAction -Execute $pwsh.Source -Argument ($argLine -join ' ')

# One trigger per claimed mark, each repeating hourly. Explicit marks, never a bare
# interval: an interval drifts onto a neighbour's mark after any restart.
$triggers = foreach ($m in $MinuteMarks) {
    $start = (Get-Date -Hour 0 -Minute $m -Second 0).AddDays(-1)
    $t = New-ScheduledTaskTrigger -Once -At $start `
        -RepetitionInterval ([TimeSpan]::FromHours(1))
    $t
}

$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit ([TimeSpan]::FromMinutes(10))

if ($PSCmdlet.ShouldProcess($taskName, "register scheduled task on minutes $($MinuteMarks -join ',')")) {
    if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    }
    [void](Register-ScheduledTask -TaskName $taskName -Action $action `
        -Trigger $triggers -Settings $settings `
        -Description "Fleet doctrine sync for $ProjectId. Pull, surface unread deltas, push owned appends, escalate on failure. See FLEET-SYNC.md.")
    Write-Output "REGISTERED: $taskName on minutes $($MinuteMarks -join ',')"
    Write-Output "NOT YET PROVEN: re-run with -Verify after the next mark and confirm last-run.json gains a fresh stamp."
}
