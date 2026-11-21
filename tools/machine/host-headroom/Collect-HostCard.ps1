<#
  One machine's dashboard card, read-only. Runs ON the machine (the HostHeadroom Dashboard task, every 10 min)
  and writes %LOCALAPPDATA%\HostHeadroom\dashboard\card.json, which every other machine's dashboard reads over
  ssh. Ported from the PC-MINI3 dashboard session's draft (2026-11-16), with credit; its own HeavySlot math is
  replaced by the sampler's, which now applies the same "a dead holder ends at the next admit" rule.

    pwsh -NoProfile -File "$env:USERPROFILE\.claude\machine\host-headroom\Collect-HostCard.ps1"

  summary : the sampler's own 7-day summary (Run-HostHeadroom.ps1 -Mode Summary), unchanged
  series  : the last 24 h of samples in 10-minute buckets (busy mean, busy max, utility, free RAM GB)
  slot    : HeavySlot occupancy and p90 wait from the summary, plus whether a live holder has the gate now
  tools / gpu / disk / virtualization : what a migrating project would find here
#>
[CmdletBinding()]
param([string]$OutDir = (Join-Path $env:LOCALAPPDATA 'HostHeadroom\dashboard'))
$ErrorActionPreference = 'Continue'
$now = [datetime]::UtcNow
$card = [ordered]@{ schema = 'fleet-host-card.v1'; machine = $env:COMPUTERNAME.ToUpperInvariant(); collectedUtc = $now.ToString('yyyy-MM-ddTHH:mm:ssZ') }

$run = Join-Path $PSScriptRoot 'Run-HostHeadroom.ps1'
$raw = (& pwsh -NoProfile -NonInteractive -File $run -Mode Summary 2>$null) -join "`n"
try { $card.summary = $raw.Substring($raw.IndexOf('{')) | ConvertFrom-Json } catch { $card.summaryError = 'summary did not parse' }

# --- 24 h series
$since = $now.AddHours(-24); $b = @{}
foreach ($f in Get-ChildItem -LiteralPath (Join-Path $env:LOCALAPPDATA 'HostHeadroom') -Filter 'samples-*.jsonl' -ErrorAction SilentlyContinue) {
    if ($f.LastWriteTimeUtc -lt $since) { continue }
    $fs = [IO.File]::Open($f.FullName, 'Open', 'Read', 'ReadWrite, Delete'); $sr = [IO.StreamReader]::new($fs)
    try {
        while ($null -ne ($l = $sr.ReadLine())) {
            if ($l -notmatch '"ts":"([^"]+)"') { continue }
            $t = ([datetime]$matches[1]).ToUniversalTime(); if ($t -lt $since) { continue }
            try { $o = $l | ConvertFrom-Json } catch { continue }
            $k = [int][math]::Floor(($t - $since).TotalMinutes / 10)
            if (-not $b[$k]) { $b[$k] = @{ n = 0; busy = 0.0; max = 0.0; util = 0.0; avail = [double]::MaxValue } }
            $x = $b[$k]; $x.n++; $x.busy += [double]$o.busy; $x.util += [double]$o.util; if ([double]$o.busy -gt $x.max) { $x.max = [double]$o.busy }
            if ([double]$o.avail_mb -lt $x.avail) { $x.avail = [double]$o.avail_mb }
        }
    } finally { $sr.Dispose() }
}
$card.series = @(foreach ($k in ($b.Keys | Sort-Object)) { $x = $b[$k]
        , @($k, [math]::Round($x.busy / $x.n, 1), [math]::Round($x.max, 1), [math]::Round($x.util / $x.n, 1), [math]::Round($x.avail / 1024, 1)) })

# --- HeavySlot: the sampler's figures, plus a live-holder check
$hs = $card.summary.heavy_slot
if ($hs) {
    $live = @(Get-ChildItem 'C:\ProgramData\HeavySlot\held' -Filter '*.json' -ErrorAction SilentlyContinue | Where-Object {
            $p = ($_.BaseName -split '-')[1]; $p -match '^\d+$' -and (Get-Process -Id ([int]$p) -ErrorAction SilentlyContinue) })
    $card.slot = [ordered]@{ d7 = [ordered]@{ duty = $hs.occupancy_frac; waitP90s = $hs.wait_s_p90; admits = $hs.gates; unclosed = $hs.dead_holders }; heldNow = $live.Count }
}

# --- what a migrating project would find here
$names = [ordered]@{ git = 'git'; pwsh = 'pwsh'; python = 'python|py'; node = 'node'; npm = 'npm'; cargo = 'cargo'; dotnet = 'dotnet'; cmake = 'cmake'; make = 'make|mingw32-make'; qmake = 'qmake'; gcc = 'gcc'; claude = 'claude'; codex = 'codex'; gh = 'gh'; nvcc = 'nvcc' }
$card.tools = @(foreach ($k in $names.Keys) { foreach ($nm in ($names[$k] -split '\|')) { if (Get-Command $nm -ErrorAction SilentlyContinue) { $k; break } } })
if (-not ($card.tools -contains 'cargo') -and (Test-Path (Join-Path $env:USERPROFILE '.cargo\bin\cargo.exe'))) { $card.tools += 'cargo' }
$card.gpu = @(Get-CimInstance Win32_VideoController -ErrorAction SilentlyContinue | ForEach-Object { $_.Name } | Where-Object { $_ -notmatch 'Virtual|Remote|Basic|VMware SVGA' })
$c = Get-PSDrive C -ErrorAction SilentlyContinue; if ($c) { $card.diskFreeGB = [math]::Round($c.Free / 1GB) }
$card.uptimeH = [math]::Round(((Get-Date) - (Get-CimInstance Win32_OperatingSystem).LastBootUpTime).TotalHours, 1)

# --- virtualization. A guest cannot see the host's sensors or its contention: its temperature lives on the
#     host's card, and its canary is the only direct measure of how much the host slows it.
$cs = Get-CimInstance Win32_ComputerSystem
$isGuest = ($cs.Manufacturer -match 'VMware') -or ($cs.Model -match 'Virtual Machine|VMware|VirtualBox|KVM')
$guests = @(Get-CimInstance Win32_Process -Filter "Name='vmware-vmx.exe'" -ErrorAction SilentlyContinue | ForEach-Object {
        if ($_.CommandLine -match '([^\\/"]+)\.vmx') { $matches[1] } })
$card.virtualization = [ordered]@{ role = $(if ($isGuest) { 'guest' } elseif ($guests.Count) { 'host' } else { 'none' }); platform = "$($cs.Manufacturer) $($cs.Model)".Trim(); guests_running = $guests }

New-Item -ItemType Directory -Path $OutDir -Force | Out-Null
$json = $card | ConvertTo-Json -Depth 10 -Compress
$tmp = Join-Path $OutDir 'card.json.tmp'
[IO.File]::WriteAllText($tmp, $json, [Text.UTF8Encoding]::new($false)); Move-Item -LiteralPath $tmp -Destination (Join-Path $OutDir 'card.json') -Force
$json
