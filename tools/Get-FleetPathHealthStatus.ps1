<#
.SYNOPSIS
List which fleet machines have acked path health: ACKED, STALE, ABSENT, DISTINGUISHED or BLOCKED.

.DESCRIPTION
The ack is the artifact (heartbeats/README.md "How to ack"): `path-health/<MACHINE>.json`, written
by `tools/Repair-MachinePath.ps1 -Check -Publish`. This reader is the ledger.

THE ROSTER IS DERIVED, never declared. A machine is on it when any bus artifact names it:
  - the `machine` field of any heartbeats/*.json (boards publish from the box they run on),
  - any path-health/<MACHINE>.json,
  - any `PATH-HEALTH: DISTINGUISH <MACHINE>` or `PATH-HEALTH: BLOCKED <MACHINE>` line in RECEIPTS.md.
A machine that no artifact names cannot be listed by anyone; that is a limit of derivation, and the
remedy is for that machine to publish, not for this file to carry a list.

  ACKED          ack published within -StaleDays. Its verdict (HEALTHY / UNHEALTHY) is shown.
  STALE          ack older than -StaleDays: the machine acked once and its check stopped.
  ABSENT         named by some artifact, no ack and no RECEIPTS line. Not the same as STALE.
  DISTINGUISHED  a reasoned decline in RECEIPTS.md (law 1). Closes the question.
  BLOCKED        tried and failed, recorded in RECEIPTS.md.
A later RECEIPTS line for a machine supersedes an earlier one; a fresh ack outranks either.

Exit 0 every machine ACKED-HEALTHY or DISTINGUISHED; 1 any STALE, ABSENT, BLOCKED or UNHEALTHY;
2 UNEVALUABLE (bus unreadable, or an ack file that does not parse).
#>
[CmdletBinding()]
param(
    [string]$BusRoot = (Split-Path -Parent $PSScriptRoot),
    [int]$StaleDays = 7,
    [switch]$Json,
    [switch]$Library
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-HeartbeatMachines([string[]]$HeartbeatTexts) {
    $out = foreach ($t in @($HeartbeatTexts)) { if ($t -match '"machine"\s*:\s*"([A-Za-z0-9][A-Za-z0-9-]*)"') { $Matches[1].ToUpperInvariant() } }
    return ,@($out)
}

function Get-ReceiptDecisions([string]$ReceiptsText) {
    # Returns ordered map MACHINE -> @{ Kind; Line }; a later line wins.
    $map = [ordered]@{}
    foreach ($line in (([string]$ReceiptsText) -split "`r?`n")) {
        if ($line -match 'PATH-HEALTH:\s+(DISTINGUISH|BLOCKED)\s+([A-Za-z0-9][A-Za-z0-9-]*)') {
            $map[$Matches[2].ToUpperInvariant()] = @{ Kind = $Matches[1]; Line = $line.Trim() }
        }
    }
    return $map
}

<#
Validate one ack at its TOP level: schema, machine equal to the file name, verdict, UTC stamp.
Anything else throws, so a malformed or misfiled ack is UNEVALUABLE, never a pass.
#>
function Test-AckRecord([string]$Raw, [string]$FileMachine) {
    $o = $Raw | ConvertFrom-Json -ErrorAction Stop
    if ($o -isnot [pscustomobject]) { throw "path-health/$FileMachine.json is not a JSON object" }
    $p = $o.PSObject.Properties
    if (-not $p['schema'] -or $o.schema -ne 'fleet-path-health.v1') { throw "path-health/$FileMachine.json: schema is not fleet-path-health.v1" }
    if (-not $p['machine'] -or ([string]$o.machine).ToUpperInvariant() -ne $FileMachine.ToUpperInvariant()) { throw "path-health/$FileMachine.json: machine field does not match the file name" }
    if (-not $p['verdict'] -or $o.verdict -notin @('HEALTHY', 'UNHEALTHY')) { throw "path-health/$FileMachine.json: verdict is not HEALTHY or UNHEALTHY" }
    if (-not $p['published_utc']) { throw "path-health/$FileMachine.json: no top-level published_utc" }
    # ConvertFrom-Json may already have turned the stamp into a [datetime]; a string must carry Z.
    $v = $o.published_utc
    $utc = if ($v -is [datetime]) { if ($v.Kind -eq [DateTimeKind]::Unspecified) { throw "path-health/$FileMachine.json: published_utc has no zone" }; $v.ToUniversalTime() }
           elseif ([string]$v -match 'Z$') { [datetimeoffset]::Parse([string]$v, [Globalization.CultureInfo]::InvariantCulture).UtcDateTime }
           else { throw "path-health/$FileMachine.json: published_utc is not a UTC Z stamp" }
    $findings = if ($p['findings']) { @($o.findings | ForEach-Object { [string]$_ }) } else { @() }
    return [pscustomobject]@{ PublishedUtc = $utc; Verdict = [string]$o.verdict; Findings = $findings }
}

<#
Acks: map MACHINE -> raw JSON text. Returns one row per derived machine, sorted by name.
#>
function Get-PathHealthRows {
    param([string[]]$HeartbeatMachines = @(), [System.Collections.IDictionary]$Acks = @{}, [System.Collections.IDictionary]$Decisions = @{}, [datetime]$NowUtc, [int]$StaleDays = 7)
    $names = [System.Collections.Generic.SortedSet[string]]::new([StringComparer]::Ordinal)
    foreach ($n in @($HeartbeatMachines) + @($Acks.Keys) + @($Decisions.Keys)) { if ($n) { [void]$names.Add(([string]$n).ToUpperInvariant()) } }
    $rows = foreach ($n in $names) {
        $status = 'ABSENT'; $verdict = ''; $age = $null; $detail = ''
        if ($Acks.Contains($n)) {
            $a = Test-AckRecord -Raw ([string]$Acks[$n]) -FileMachine $n   # throws -> UNEVALUABLE upstream
            $age = ($NowUtc - $a.PublishedUtc).TotalDays
            $verdict = $a.Verdict
            $f = $a.Findings -join ', '
            $status = if ($age -le $StaleDays) { 'ACKED' } else { 'STALE' }
            $detail = $f
        }
        if ($status -ne 'ACKED' -and $Decisions.Contains($n)) {
            $d = $Decisions[$n]
            $status = if ($d.Kind -eq 'DISTINGUISH') { 'DISTINGUISHED' } else { 'BLOCKED' }
            $detail = $d.Line
        }
        [pscustomobject]@{ machine = $n; status = $status; verdict = $verdict; age_days = $(if ($null -ne $age) { [math]::Round($age, 2) } else { $null }); detail = $detail }
    }
    return ,@($rows)
}

function Get-PathHealthExitCode([object[]]$Rows) {
    foreach ($r in @($Rows)) {
        if ($r.status -in @('STALE', 'ABSENT', 'BLOCKED')) { return 1 }
        if ($r.status -eq 'ACKED' -and $r.verdict -ne 'HEALTHY') { return 1 }
    }
    return 0
}

if ($Library) { return }

try {
    $hbDir = Join-Path $BusRoot 'heartbeats'
    $phDir = Join-Path $BusRoot 'path-health'
    $receipts = Join-Path $BusRoot 'RECEIPTS.md'
    if (-not (Test-Path -LiteralPath $hbDir) -or -not (Test-Path -LiteralPath $receipts)) { throw "not a bus checkout: $BusRoot" }
    $hbTexts = @(Get-ChildItem -LiteralPath $hbDir -Filter *.json -File | ForEach-Object { Get-Content -LiteralPath $_.FullName -Raw })
    $acks = [ordered]@{}
    if (Test-Path -LiteralPath $phDir) {
        foreach ($f in (Get-ChildItem -LiteralPath $phDir -Filter *.json -File)) { $acks[$f.BaseName.ToUpperInvariant()] = Get-Content -LiteralPath $f.FullName -Raw }
    }
    $rows = Get-PathHealthRows -HeartbeatMachines (Get-HeartbeatMachines $hbTexts) -Acks $acks `
        -Decisions (Get-ReceiptDecisions (Get-Content -LiteralPath $receipts -Raw)) -NowUtc (Get-Date).ToUniversalTime() -StaleDays $StaleDays
} catch {
    Write-Output "UNEVALUABLE: $($_.Exception.Message)"
    exit 2
}

if ($Json) { $rows | ConvertTo-Json -Depth 4 }
else {
    Write-Output ("Fleet path health (stale after {0} days; roster derived from heartbeats, acks and RECEIPTS.md):" -f $StaleDays)
    $rows | Format-Table machine, status, verdict, age_days, detail -AutoSize | Out-String -Width 220 | Write-Output
}
exit (Get-PathHealthExitCode $rows)
