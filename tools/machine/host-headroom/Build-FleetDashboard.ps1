<#
  The fleet headroom dashboard: one self-contained HTML page, rebuilt every 10 minutes on EVERY machine the
  tool is installed on (task \Fleet\HostHeadroom Dashboard), so it opens locally on any of them:
    %LOCALAPPDATA%\HostHeadroom\dashboard\index.html   (Desktop link: "Fleet Headroom")

    pwsh -NoProfile -File "$env:USERPROFILE\.claude\machine\host-headroom\Build-FleetDashboard.ps1" [-Open]
    pwsh -NoProfile -File "$env:USERPROFILE\.claude\machine\host-headroom\Build-FleetDashboard.ps1" -RefreshFootprint -Open

  Each machine collects only its OWN card (Collect-HostCard.ps1) and reads every peer's card.json over ssh,
  a file read, so no machine recomputes another's summary. The suspended-project footprint is measured on
  the footprint source only with -RefreshFootprint (it is benchmarking); otherwise the newest copy held by
  any peer is used. Read-only on every peer. Diagnostic only: it informs a placement and gates nothing.
  Ported from the PC-MINI3 dashboard session's draft (2026-11-16), with credit.
#>
[CmdletBinding()]
param(
    [string]$HostsFile = (Join-Path $PSScriptRoot 'fleet-hosts.json'),
    [string]$OutDir = (Join-Path $env:LOCALAPPDATA 'HostHeadroom\dashboard'),
    [switch]$RefreshFootprint,
    [switch]$Open,
    [string]$CardsFrom   # tests: a folder of <MACHINE>.card.json fixtures replaces collection and ssh
)
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Path $OutDir -Force | Out-Null
$cfg = Get-Content -LiteralPath $HostsFile -Raw | ConvertFrom-Json
$self = $env:COMPUTERNAME.ToUpperInvariant()

# Run a read-only script on a peer; return its last JSON line, or $null.
function Invoke-PeerJson([string]$alias, [string]$script) {
    $enc = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($script))
    $out = & ssh -n -o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=10 -o ServerAliveCountMax=2 $alias "pwsh -NoProfile -NonInteractive -EncodedCommand $enc" 2>$null
    $j = @($out | Where-Object { $_ -is [string] -and $_.StartsWith('{') }) | Select-Object -Last 1
    if ($j) { try { return $j | ConvertFrom-Json } catch { } }
    $null
}
$readCard = @'
$p = Join-Path $env:LOCALAPPDATA 'HostHeadroom\dashboard\card.json'
if (Test-Path -LiteralPath $p) { [IO.File]::ReadAllText($p) } else { '{"missing":true,"machine":"' + $env:COMPUTERNAME.ToUpperInvariant() + '"}' }
'@
$readFootprint = @'
$p = Join-Path $env:LOCALAPPDATA 'HostHeadroom\dashboard\suspended-footprint.json'
if (Test-Path -LiteralPath $p) { [IO.File]::ReadAllText($p) } else { '{"missing":true}' }
'@

# --- cards: own card collected here, peers' cards read over ssh (in parallel)
$cards = [System.Collections.Generic.List[object]]::new()
if ($CardsFrom) {
    foreach ($f in Get-ChildItem -LiteralPath $CardsFrom -Filter '*.card.json') { $cards.Add((Get-Content -LiteralPath $f.FullName -Raw | ConvertFrom-Json)) }
} else {
    $own = (& pwsh -NoProfile -NonInteractive -File (Join-Path $PSScriptRoot 'Collect-HostCard.ps1') -OutDir $OutDir) -join "`n"
    try { $cards.Add(($own.Substring($own.IndexOf('{')) | ConvertFrom-Json)) } catch { $cards.Add([pscustomobject]@{ machine = $self; error = 'local card collection failed' }) }
    $fn = ${function:Invoke-PeerJson}.ToString()
    $peers = @($cfg.hosts | Where-Object { $_.alias.ToUpperInvariant() -ne $self })
    $got = $peers | ForEach-Object -ThrottleLimit 6 -Parallel {
        ${function:Invoke-PeerJson} = $using:fn
        $c = Invoke-PeerJson $_.alias $using:readCard
        if (-not $c) { [pscustomobject]@{ machine = $_.alias.ToUpperInvariant(); error = 'unreachable over ssh' } }
        elseif ($c.missing) { [pscustomobject]@{ machine = $c.machine; error = 'host-headroom not installed here yet' } }
        else { $c }
    }
    foreach ($c in @($got)) { $cards.Add($c) }
}
# a card older than 30 min is shown, but marked stale
foreach ($c in $cards) {
    if ($c.collectedUtc -and ([datetime]::UtcNow - ([datetime]$c.collectedUtc).ToUniversalTime()).TotalMinutes -gt 30) { $c | Add-Member -NotePropertyName stale -NotePropertyValue $true -Force }
    $h = $cfg.hosts | Where-Object { $_.alias.ToUpperInvariant() -eq "$($c.machine)".ToUpperInvariant() } | Select-Object -First 1
    if ($h -and $h.PSObject.Properties['vm_on']) { $c | Add-Member -NotePropertyName vmOn -NotePropertyValue $h.vm_on -Force }
}

# --- suspended-project footprint
$fpPath = Join-Path $OutDir 'suspended-footprint.json'
if ($RefreshFootprint -and -not $CardsFrom) {
    $fp = Invoke-PeerJson $cfg.footprint_source (Get-Content -LiteralPath (Join-Path $PSScriptRoot 'Measure-SuspendedFootprint.ps1') -Raw)
    if ($fp -and -not $fp.missing) { [IO.File]::WriteAllText($fpPath, ($fp | ConvertTo-Json -Depth 8 -Compress), [Text.UTF8Encoding]::new($false)) }
    else { [Console]::Error.WriteLine("footprint: $($cfg.footprint_source) did not answer; keeping the previous copy") }
}
if (-not (Test-Path -LiteralPath $fpPath) -and -not $CardsFrom) {
    # no copy here yet: take the newest a peer holds
    $best = $null
    foreach ($h in @($cfg.hosts | Where-Object { $_.alias.ToUpperInvariant() -ne $self })) {
        $fp = Invoke-PeerJson $h.alias $readFootprint
        if ($fp -and -not $fp.missing -and (-not $best -or [datetime]$fp.measuredUtc -gt [datetime]$best.measuredUtc)) { $best = $fp }
    }
    if ($best) { [IO.File]::WriteAllText($fpPath, ($best | ConvertTo-Json -Depth 8 -Compress), [Text.UTF8Encoding]::new($false)) }
}
$fpFile = if ($CardsFrom) { Join-Path $CardsFrom 'suspended-footprint.json' } else { $fpPath }
$footprint = if (Test-Path -LiteralPath $fpFile) { Get-Content -LiteralPath $fpFile -Raw | ConvertFrom-Json } else { $null }

# --- render
$data = [ordered]@{ schema = 'fleet-dashboard.v1'; builtUtc = [datetime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ'); builtOn = $self
    hosts = @($cards | Sort-Object machine); footprint = $footprint }
$json = $data | ConvertTo-Json -Depth 14 -Compress
[IO.File]::WriteAllText((Join-Path $OutDir 'fleet.json'), $json, [Text.UTF8Encoding]::new($false))
$tpl = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'dashboard.template.html') -Raw
if (-not $tpl.Contains('/*__DATA__*/null')) { throw 'dashboard.template.html has no data placeholder' }
$html = $tpl.Replace('/*__DATA__*/null', $json.Replace('</', '<\/'))
$tmp = Join-Path $OutDir 'index.html.tmp'; $dst = Join-Path $OutDir 'index.html'
[IO.File]::WriteAllText($tmp, $html, [Text.UTF8Encoding]::new($false)); Move-Item -LiteralPath $tmp -Destination $dst -Force
"wrote $dst ($([math]::Round($html.Length / 1KB)) KB; $($cards.Count) hosts; $(@($cards | Where-Object { $_.PSObject.Properties['error'] }).Count) without a card)"
if ($Open) { Start-Process $dst }
