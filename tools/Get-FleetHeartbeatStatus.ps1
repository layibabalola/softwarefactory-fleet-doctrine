<#
.SYNOPSIS
Derive fleet-wide sync liveness from published board heartbeats. ABSENT is a finding, not a default.

.DESCRIPTION
Classifies every fleet member by the heartbeat it has (or has not) published to heartbeats/*.json.
It answers the one question `tools/fleet-sweep.mjs` structurally cannot: the sweep is BOX-scoped and
reports `no-local-clone` for every member that lives on another machine, so from any one box the
fleet is mostly invisible. Heartbeats are how a member's liveness crosses machines.

  ALIVE      - published within -StaleHours
  PULSE-ONLY - published recently, but the SYNC it reports on has not run in -StaleHours. The
               publisher is alive and the duty it reports on is not: a pulse is not progress.
  STALE      - published, then stopped advancing. Silence is the alarm.
  ABSENT     - a derived member with NO heartbeat file at all.

ABSENT and STALE are DIFFERENT FAILURES and must never be collapsed. A board that never installed
the sync duty has no file; a board whose task died has an old file. The fleet's own measured scar
is the first kind - eleven of twelve projects had no duty implemented - and a status tool that
reported only on boards it could see would have reported a healthy fleet throughout. This is the
same discriminator the airmypc ruling names: the tell is a MISSING KEY, not a low count.

MEMBERSHIP IS DERIVED, never declared twice. The first draft shipped a `heartbeats/ROSTER.md` and
argued absence was underivable without one. `tools/fleet-sweep.mjs` had already published the
correct rule and the roster was withdrawn the same day - see the derivation block below.

UNEVALUABLE is distinct from healthy: an unreadable specs/ or heartbeat exits 1 rather than
reporting zero problems.

.PARAMETER BusRoot
Local clone of the fleet doctrine bus.

.PARAMETER StaleHours
A published heartbeat older than this is STALE. Default 12 - twice the publisher's 6 h refresh, so
one missed refresh does not raise an alarm but two do.

.PARAMETER Json
Emit one JSON object instead of the text report.

.OUTPUTS
Exit 0 every derived member ALIVE
Exit 3 one or more STALE or PULSE-ONLY (installed, stopped advancing)
Exit 4 one or more ABSENT (never published - duty likely not installed)  [takes precedence over 3]
Exit 1 UNEVALUABLE - specs/ or a heartbeat unreadable
#>
[CmdletBinding()]
param(
    [string]$BusRoot = 'C:\code\softwarefactory-fleet-doctrine',
    [int]$StaleHours = 12,
    [switch]$Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$m) { if (-not $Json) { Write-Output "UNEVALUABLE: $m" } else { @{ status = 'UNEVALUABLE'; reason = $m } | ConvertTo-Json }; exit 1 }

# TRAP (fleet-documented, re-measured 2026-08-30): ConvertFrom-Json coerces an ISO-8601 string into a
# LOCAL [datetime], dropping the offset. Reading `published_utc` off the parsed object skews every
# age by the machine's UTC offset - here 5 hours, enough to call a stale board alive or the reverse.
# Ages are derived from the RAW TEXT.
function Get-RawJsonString([string]$Raw, [string]$Name) {
    if ($Raw -match ('"' + [regex]::Escape($Name) + '"\s*:\s*"([^"]*)"')) { return $Matches[1] }
    return ''
}

if (-not (Test-Path -LiteralPath $BusRoot)) { Fail "bus root absent: $BusRoot" }
$hbDir = Join-Path $BusRoot 'heartbeats'

# MEMBERSHIP IS DERIVED, NOT DECLARED IN A SECOND PLACE.
# The first draft of this tool shipped a `heartbeats/ROSTER.md` and argued that absence was
# underivable without one. That was wrong, and `tools/fleet-sweep.mjs` had already published the
# correct rule: the bus layout is the authority — members are `specs/<project>.md` minus
# `specs/fleet-*.md`, which are cross-cutting candidates with no owning project. A registry file
# would be a second authority for one fact, and this fleet has already paid for that (six-to-eight
# gate ledgers, and the one that gated was whichever you had not checked). The roster was withdrawn
# and this derivation matches the sweep's exactly, so the two tools can never disagree about who
# exists.
$specDir = Join-Path $BusRoot 'specs'
if (-not (Test-Path -LiteralPath $specDir)) { Fail "specs/ absent: $specDir - membership is derived from it" }
$roster = @()
foreach ($f in (Get-ChildItem -LiteralPath $specDir -Filter '*.md' -File)) {
    $id = $f.BaseName
    if ($id -like 'fleet-*') { continue }
    if ($id -notmatch '^[a-z0-9][a-z0-9-]{1,63}$') { continue }
    $roster += [pscustomobject]@{ board = $id }
}
if ($roster.Count -eq 0) { Fail "derived zero members from $specDir" }

$nowUtc = [datetimeoffset]::UtcNow
$rows = foreach ($r in $roster) {
    $f = Join-Path $hbDir "$($r.board).json"
    if (-not (Test-Path -LiteralPath $f)) {
        [pscustomobject]@{ board = $r.board; status = 'ABSENT'; ageHours = $null; verdict = $null; machine = $null; note = 'no heartbeat file - sync duty likely not installed' }
        continue
    }
    $h = $null; $hRaw = Get-Content -LiteralPath $f -Raw
    try { $h = $hRaw | ConvertFrom-Json -ErrorAction Stop } catch {
        [pscustomobject]@{ board = $r.board; status = 'UNREADABLE'; ageHours = $null; verdict = $null; machine = $null; note = 'heartbeat is not valid JSON' }
        continue
    }
    $age = $null
    try { $age = [math]::Round(($nowUtc - [datetimeoffset]::Parse((Get-RawJsonString $hRaw 'published_utc'))).TotalHours, 1) } catch { $age = $null }
    # A fresh publish over a frozen sync is the orphan-pulse shape: the publisher is alive and the
    # thing it reports on is not. Surfaced explicitly rather than left for a reader to notice.
    $syncAge = $null
    try { $syncAge = [math]::Round(($nowUtc - [datetimeoffset]::Parse((Get-RawJsonString $hRaw 'sync_ran_utc'))).TotalHours, 1) } catch { $syncAge = $null }
    $status = if ($null -eq $age) { 'UNREADABLE' } elseif ($age -gt $StaleHours) { 'STALE' } elseif ($null -ne $syncAge -and $syncAge -gt $StaleHours) { 'PULSE-ONLY' } else { 'ALIVE' }
    [pscustomobject]@{
        board = $r.board; status = $status; ageHours = $age; syncAgeHours = $syncAge
        verdict = [string]$h.verdict; machine = [string]$h.machine
        note = switch ($status) {
            'STALE' { "last published $age h ago (> $StaleHours h)" }
            'PULSE-ONLY' { "published $age h ago but its SYNC last ran $syncAge h ago - the publisher is alive and the duty it reports on is not" }
            default { [string]$h.detail }
        }
    }
}

$absent = @($rows | Where-Object { $_.status -in @('ABSENT', 'UNREADABLE') })
$stale = @($rows | Where-Object { $_.status -in @('STALE', 'PULSE-ONLY') })

if ($Json) {
    [pscustomobject]@{ derivedAtUtc = $nowUtc.ToString('yyyy-MM-ddTHH:mm:ssZ'); staleHours = $StaleHours; boards = $rows; absentCount = $absent.Count; staleCount = $stale.Count } | ConvertTo-Json -Depth 5
} else {
    Write-Output ("FLEET SYNC LIVENESS  derived {0}  stale-threshold {1} h" -f $nowUtc.ToString('yyyy-MM-ddTHH:mm:ssZ'), $StaleHours)
    Write-Output ('{0,-38} {1,-10} {2,-8} {3,-9} {4}' -f 'BOARD', 'STATUS', 'AGE(h)', 'VERDICT', 'MACHINE / NOTE')
    foreach ($row in ($rows | Sort-Object @{e = { switch ($_.status) { 'ABSENT' { 0 } 'UNREADABLE' { 1 } 'PULSE-ONLY' { 2 } 'STALE' { 3 } default { 4 } } } }, board)) {
        Write-Output ('{0,-38} {1,-10} {2,-8} {3,-9} {4}' -f $row.board, $row.status, $(if ($null -eq $row.ageHours) { '-' } else { $row.ageHours }), $(if ($row.verdict) { $row.verdict } else { '-' }), $(if ($row.machine) { "$($row.machine)  $($row.note)" } else { $row.note }))
    }
    Write-Output ''
    Write-Output ("SUMMARY: {0} alive, {1} stale, {2} absent/unreadable, of {3} rostered." -f @($rows | Where-Object { $_.status -eq 'ALIVE' }).Count, $stale.Count, $absent.Count, $rows.Count)
    if ($absent.Count) { Write-Output 'ABSENT is not "quiet" - it is a board with no sync duty installed. That is the measured failure this surface exists to make visible.' }
}

if ($absent.Count) { exit 4 }
if ($stale.Count) { exit 3 }
exit 0
