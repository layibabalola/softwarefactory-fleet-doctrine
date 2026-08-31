<#
.SYNOPSIS
Publish one board's sync heartbeat to the bus, so fleet liveness is derivable by anyone.

.DESCRIPTION
`fleet-sweep.mjs` is BOX-scoped: it reports every member without a clone on this machine as
`no-local-clone`, which is correct and means that from any one box the rest of the fleet is
invisible. Each board's sync evidence stays on its own machine, so a board that never installed the
duty and a board whose task silently stopped both look exactly like a quiet board from outside.
That is how eleven of twelve projects went unnoticed: the evidence existed and never left the
machine.

This publishes one board's sync liveness to `heartbeats/<board>.json` on the bus, which is the one
thing a box-scoped sweep cannot do for a member it cannot see. It adds NO opinion about what
"current" means - it reports what the sweep already decided.

LAW COMPLIANCE, because a heartbeat is easy to get wrong on all four:

  Law 2 (single writer)  - one file per board, named by board id. Ownership is proven against the
                           ARTIFACT (the sweep receipt's member list, or the legacy record's project
                           field), never against -BoardId, so a typo cannot publish over a peer.
  Law 3 (push on change, - a naive heartbeat is a CADENCE push and would bury the bus in commits.
        never a cadence)   This pushes only when CONTENT changes (source, verdict, cursor, delta
                           count, machine, or the sweep's own stamp) or when the published record is
                           older than -RefreshHours. Bounded: 24/RefreshHours per board per day, 4
                           by default. Cadence pushing is what got this tool's predecessor withdrawn.
  Law 4 (what travels)   - board id, machine, UTC stamps, verdict token, delta count, bus SHA. No
                           absolute paths, no user names, no transcripts, no credentials. `detail`
                           is length-capped and path-stripped rather than trusted.

Silence is the alarm. A board that dies stops advancing its stamp, and staleness is what
Get-FleetHeartbeatStatus.ps1 reads. This tool therefore never invents a stamp: if no source
artifact exists, it FAILS rather than publishing a healthy-looking record.

.PARAMETER BoardId
Bus board identity; must match a `specs/<BoardId>.md` member and the source artifact.

.PARAMETER ProjectRoot
The board checkout. Source is `.claude-state/doctrine/fleet-sweep-receipt.json` (preferred) or
`.claude-state/doctrine/last-run.json` (legacy fallback).

.PARAMETER BusRoot
Local clone of the fleet doctrine bus.

.PARAMETER RefreshHours
Republish an unchanged heartbeat once it is this old, so a healthy-but-idle board stays visibly
alive. Default 6.

.PARAMETER NoPush
Write and commit nothing; report what would be published. For drills and first inspection.

.OUTPUTS
Exit 0 PUBLISHED or UNCHANGED (nothing owed)
Exit 4 FAILED       could not publish - local heartbeat missing/unreadable, or push blocked
Exit 5 PRECONDITION bad arguments or missing repo; nothing attempted
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidatePattern('^[a-z0-9][a-z0-9-]{1,63}$')][string]$BoardId,
    [Parameter(Mandatory)][string]$ProjectRoot,
    [Parameter(Mandatory)][string]$BusRoot,
    [int]$RefreshHours = 6,
    [switch]$NoPush
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Say([string]$m) { Write-Output $m }

# TRAP (fleet-documented, re-measured here 2026-08-30): ConvertFrom-Json COERCES an ISO-8601 string
# into a local [datetime]. `"2026-08-30T18:37:01Z"` came back out of a [string] cast as
# `08/30/2026 18:37:01` - offset dropped, culture-formatted, and therefore read 5 hours wrong by any
# consumer computing an age from it. Staleness detection would have been silently skewed by the
# machine's UTC offset. Timestamps are read from the RAW TEXT and never from the parsed object.
function Get-RawJsonString([string]$Raw, [string]$Name) {
    if ($Raw -match ('"' + [regex]::Escape($Name) + '"\s*:\s*"([^"]*)"')) { return $Matches[1] }
    return ''
}

# --- preconditions -------------------------------------------------------------------------
foreach ($p in @($ProjectRoot, $BusRoot)) {
    if (-not (Test-Path -LiteralPath $p)) { Say "PRECONDITION: path does not exist: $p"; exit 5 }
}
& git -C $BusRoot rev-parse --git-dir *> $null
if ($LASTEXITCODE -ne 0) { Say "PRECONDITION: bus is not a git checkout: $BusRoot"; exit 5 }

# SOURCE OF TRUTH, and it must be an artifact a SURVIVING tool writes.
# The first draft read `.claude-state/doctrine/last-run.json`, written by `Sync-FleetDoctrine.ps1`.
# That tool was withdrawn by its own author hours later as a duplicate, and this publisher went on
# reading its now-frozen output - a heartbeat that looked healthy while reporting a dead artifact.
# Preferred source is therefore `fleet-sweep.mjs --json-out` (schema fleet-sweep.v1), which is the
# surviving box-level tool; the legacy file is accepted as a fallback for boards still on it.
$sweepReceipt = Join-Path $ProjectRoot '.claude-state/doctrine/fleet-sweep-receipt.json'
$legacyBeat = Join-Path $ProjectRoot '.claude-state/doctrine/last-run.json'

$src = ''; $ranUtc = ''; $verdict = ''; $cursor = ''; $detailRaw = ''; $deltaCount = -1; $ownerProven = $false
if (Test-Path -LiteralPath $sweepReceipt) {
    $rRaw = Get-Content -LiteralPath $sweepReceipt -Raw
    try { $r = $rRaw | ConvertFrom-Json -ErrorAction Stop } catch { Say "FAILED: sweep receipt is not valid JSON: $sweepReceipt"; exit 4 }
    $src = 'fleet-sweep.v1'
    $ranUtc = Get-RawJsonString $rRaw 'generatedUtc'
    $cursor = Get-RawJsonString $rRaw 'busHead'
    $me = @($r.members | Where-Object { $_.project -eq $BoardId })
    if ($me.Count -ne 1) {
        Say "FAILED: sweep receipt names $($me.Count) member(s) matching '$BoardId'. This board cannot prove it owns heartbeats/$BoardId.json."
        exit 5
    }
    $ownerProven = $true
    $status = [string]$me[0].status
    # `no-local-clone` means the sweep ran on a box that does not host this board. Publishing from
    # there would attribute another machine's view to this board.
    if ($status -eq 'no-local-clone') { Say "FAILED: sweep receipt reports '$BoardId' as no-local-clone - this box does not host it. Refusing to publish."; exit 5 }
    # STATUS -> VERDICT. Tracks fleet-sweep's vocabulary, which CHANGED under this file the same day:
    # the sweep moved from alarming on distance to alarming on staleness, because "behind by some
    # amount" is the steady state of a live bus - it advances during the very ack that folds it, so an
    # alarm keyed on distance fires forever and means nothing. (Independently the same shape as this
    # publisher's own bus_cursor feedback loop, found from the other side.)
    #
    # The consequence here was concrete: `behind-fresh` is the sweep's HEALTHY-with-deltas state, and
    # the old `default { 'ESCALATE' }` would have published a perfectly current board as ESCALATE.
    #
    # So an UNRECOGNISED status is now published as UNKNOWN with the raw token carried in `detail`,
    # never silently folded into ESCALATE. A default arm that swallows vocabulary drift is how this
    # broke; a visible UNKNOWN is how a reader finds out the two tools have diverged.
    switch ($status) {
        'current'         { $verdict = 'CLEAN';        $deltaCount = 0 }
        'behind-fresh'    { $verdict = 'CLEAN';        $deltaCount = 1 }   # deltas exist, fold is fresh
        'stale'           { $verdict = 'FOLD_PENDING'; $deltaCount = 1 }
        'never-folded'    { $verdict = 'FOLD_PENDING'; $deltaCount = 1 }
        'check-failed'    { $verdict = 'ESCALATE';     $deltaCount = -1 }
        'check-timeout'   { $verdict = 'ESCALATE';     $deltaCount = -1 }
        'root-not-a-repo' { $verdict = 'ESCALATE';     $deltaCount = -1 }
        default           { $verdict = 'UNKNOWN';      $deltaCount = -1 }
    }
    # abb2019 renamed this receipt field `unfolded` -> `behindButFresh`; b4a7194 tracked the
    # rename in the status switch above and missed it here, so every board publishing against a
    # post-abb2019 receipt died under StrictMode with "The property 'unfolded' cannot be found".
    # Read either name, and say 'unknown' when neither is present rather than throwing or lying.
    $behindFresh = if ($r.PSObject.Properties.Name -contains 'behindButFresh') { $r.behindButFresh }
                   elseif ($r.PSObject.Properties.Name -contains 'unfolded')  { $r.unfolded }
                   else { 'unknown' }
    $detailRaw = "$status; box declared=$($r.declaredCount) cloned=$($r.withLocalClone) behind-fresh=$behindFresh failed=$($r.failed)"
} elseif (Test-Path -LiteralPath $legacyBeat) {
    $bRaw = Get-Content -LiteralPath $legacyBeat -Raw
    try { $b = $bRaw | ConvertFrom-Json -ErrorAction Stop } catch { Say "FAILED: legacy heartbeat is not valid JSON: $legacyBeat"; exit 4 }
    $src = 'sync-fleetdoctrine.v1(legacy)'
    $ranUtc = Get-RawJsonString $bRaw 'ran_utc'
    $verdict = Get-RawJsonString $bRaw 'verdict'
    $detailRaw = Get-RawJsonString $bRaw 'detail'
    if ($bRaw -match '"delta_count"\s*:\s*(-?\d+)') { $deltaCount = [int]$Matches[1] }
    $localProject = Get-RawJsonString $bRaw 'project'
    if ($localProject -ne $BoardId) { Say "FAILED: -BoardId '$BoardId' does not match the local record's project '$localProject'. A board writes only its own heartbeat (bus law 2)."; exit 5 }
    $ownerProven = $true
    $curFile = Join-Path $ProjectRoot '.claude-state/doctrine/doctrine-cursor.json'
    if (Test-Path -LiteralPath $curFile) {
        $curRaw = Get-Content -LiteralPath $curFile -Raw
        foreach ($n in @('last_folded_commit', 'bus_sha')) { if (-not $cursor) { $cursor = Get-RawJsonString $curRaw $n } }
    }
} else {
    # The single most important failure this tool can report: it is exactly the state of a board that
    # never installed the duty. Publishing anything here would manufacture the appearance of liveness.
    Say "FAILED: no sweep receipt at $sweepReceipt and no legacy heartbeat at $legacyBeat."
    Say "        This board's bus duty is not installed or has never run. Not publishing:"
    Say "        an absent board must read as ABSENT, never as a healthy record."
    exit 4
}

# SINGLE-WRITER, ENFORCED (added after this tool failed its own negative control: the docstring
# claimed it "refuses to write any other board's file" and it did not). Ownership is proven against
# the ARTIFACT - the receipt's member list or the record's project field - never against the
# argument, so a -BoardId typo cannot publish over a peer.
if (-not $ownerProven) { Say "FAILED: could not prove this board owns heartbeats/$BoardId.json"; exit 5 }
if (-not $ranUtc) { Say "FAILED: source '$src' carried no usable timestamp"; exit 4 }
if (-not $verdict) { $verdict = 'UNKNOWN' }

# `detail` is board-authored free text. Strip anything path-shaped and cap it: law 4 is about what
# travels, and the cheapest way to leak a machine layout is an unexamined diagnostic string.
$detail = ''
if ($detailRaw) {
    $detail = ($detailRaw -replace '[A-Za-z]:\\[^\s"]*', '<path>') -replace '\\\\[^\s"]+', '<unc>'
    if ($detail.Length -gt 200) { $detail = $detail.Substring(0, 200) + '...' }
}

$nowUtc = [datetimeoffset]::UtcNow
$record = [ordered]@{
    schema        = 'fleet-board-heartbeat.v1'
    board         = $BoardId
    machine       = $env:COMPUTERNAME
    published_utc = $nowUtc.ToString('yyyy-MM-ddTHH:mm:ssZ')
    source        = $src
    sync_ran_utc  = $ranUtc
    verdict       = $verdict
    delta_count   = $deltaCount
    bus_cursor    = [string]$cursor
    detail        = $detail
}

$hbDir = Join-Path $BusRoot 'heartbeats'
if (-not (Test-Path -LiteralPath $hbDir)) { [void](New-Item -ItemType Directory -Force -Path $hbDir) }
$target = Join-Path $hbDir "$BoardId.json"

# --- should we publish at all? (law 3) -------------------------------------------------------
# Compare everything EXCEPT published_utc, which changes on every run by construction. If only the
# clock moved, this is a cadence push and is skipped until RefreshHours elapses.
$reason = 'first-publication'
$publish = $true
if (Test-Path -LiteralPath $target) {
    try {
        $prevRaw = Get-Content -LiteralPath $target -Raw
        $prev = $prevRaw | ConvertFrom-Json -ErrorAction Stop
        $same = $true
        # The SAME coercion trap, second code path, and it bites harder here: `$prev.sync_ran_utc`
        # comes back as a culture-formatted local datetime, never equals the raw `...Z` string, so
        # every run scored "changed" and pushed - reintroducing the cadence commit that law 3 forbids
        # and that this whole comparison exists to prevent. The rule is not "parse dates from raw
        # text"; it is NEVER LET A COERCED OBJECT CROSS A COMPARISON BOUNDARY. Both sides raw.
        # TWO fields are carried in the record but deliberately EXCLUDED from change detection,
        # because each one made this tool push on every single run:
        #
        #   sync_ran_utc - the sweep's own generatedUtc, new on every run. A timestamp in a
        #                  change-detection set is a cadence commit wearing a content-change costume.
        #   bus_cursor   - the bus HEAD. And PUBLISHING ADVANCES THE BUS HEAD. So the value this
        #                  record reports is changed by the act of reporting it: publish -> new head
        #                  -> "changed" -> publish. A heartbeat that records the state of the commons,
        #                  published INTO the commons, cannot converge. It is not a cadence bug, it is
        #                  a feedback loop, and no refresh interval would have damped it.
        #
        # What is left is what actually says something about this board: what the sweep concluded
        # (verdict), which box and source produced it, and the sweep's own summary counts. Both
        # excluded fields still travel in the record - they are just not allowed to trigger a push,
        # and -RefreshHours keeps them from going stale.
        foreach ($k in @('board', 'machine', 'source', 'verdict', 'detail')) {
            $prevVal = Get-RawJsonString $prevRaw $k
            if ($prevVal -ne [string]$record[$k]) { $same = $false; $reason = "changed:$k"; break }
        }
        if ($same) {
            $prevDelta = if ($prevRaw -match '"delta_count"\s*:\s*(-?\d+)') { [int]$Matches[1] } else { -999 }
            if ($prevDelta -ne [int]$record['delta_count']) { $same = $false; $reason = 'changed:delta_count' }
        }
        if ($same) {
            $age = $null
            $prevPub = Get-RawJsonString $prevRaw 'published_utc'
            try { $age = ($nowUtc - [datetimeoffset]::Parse($prevPub)).TotalHours } catch { $age = 9999 }
            if ($age -lt $RefreshHours) {
                Say ("UNCHANGED: {0} published {1:n1} h ago (<{2} h), content identical - not pushing a cadence commit." -f $BoardId, $age, $RefreshHours)
                exit 0
            }
            $reason = "refresh:${RefreshHours}h"
        }
    } catch { $reason = 'previous-unreadable' }
}

$json = ($record | ConvertTo-Json -Depth 4)
if ($NoPush) {
    Say "WOULD PUBLISH ($reason):"
    Say $json
    exit 0
}

Set-Content -LiteralPath $target -Value $json -Encoding utf8

# --- commit and push -------------------------------------------------------------------------
# Only ever stage this board's own file. A publisher that ran `git add -A` would sweep a peer's
# in-flight edit into a heartbeat commit - the single-writer law protects files, not staging areas.
& git -C $BusRoot add -- "heartbeats/$BoardId.json" *> $null
if ($LASTEXITCODE -ne 0) { Say "FAILED: could not stage heartbeats/$BoardId.json"; exit 4 }

$staged = & git -C $BusRoot diff --cached --name-only
if (-not $staged) { Say "UNCHANGED: $BoardId - bytes identical after write, nothing to commit."; exit 0 }
if (@($staged).Count -ne 1 -or @($staged)[0] -ne "heartbeats/$BoardId.json") {
    & git -C $BusRoot reset -- "heartbeats/$BoardId.json" *> $null
    Say "FAILED: staging area held files other than this board's heartbeat: $($staged -join ', '). Refusing to commit."
    exit 4
}

$msg = "heartbeat: $BoardId $($record.verdict) ($reason)"
& git -C $BusRoot -c commit.gpgsign=false commit -q -m $msg
if ($LASTEXITCODE -ne 0) { Say "FAILED: commit failed"; exit 4 }

# One rebase-and-retry: many boards push here and a race is expected, not exceptional.
& git -C $BusRoot push origin HEAD *> $null
if ($LASTEXITCODE -ne 0) {
    & git -C $BusRoot pull --rebase origin (& git -C $BusRoot rev-parse --abbrev-ref HEAD) *> $null
    if ($LASTEXITCODE -ne 0) { Say 'FAILED: push rejected and rebase failed; heartbeat committed locally only'; exit 4 }
    & git -C $BusRoot push origin HEAD *> $null
    if ($LASTEXITCODE -ne 0) { Say 'FAILED: push rejected twice; heartbeat committed locally only'; exit 4 }
}

Say "PUBLISHED: heartbeats/$BoardId.json verdict=$($record.verdict) cursor=$($record.bus_cursor) ($reason)"
exit 0
