# Measure-SuspendedFootprint.ps1 - what the projects suspended on a machine used while they ran.
# Runs ON the source machine (the dashboard sends it over ssh). Read-only, one pass over each file.
# Sources (all already on the machine):
#   - the heavy-slot shadow log (C:\t\.heavy-slot-shadow.jsonl): acquires, slot-hours, wait-minutes and
#     package watts (feed.w30) per day, before and after the suspension date;
#   - Claude Code transcripts (~\.claude\projects\*\*.jsonl, first/last timestamp only): session-hours
#     per project, the only per-project split available (Codex sessions are .zst and unattributed);
#   - each project's tracked files (git ls-files): the toolchain it needs.
# Output: one JSON object on stdout.
param([string]$SuspendedUtc = '2026-10-25', [int]$BeforeDays = 15, [string]$ShadowLog = 'C:\t\.heavy-slot-shadow.jsonl',
    [string]$CodeRoot = 'C:\code', [string[]]$Projects = @('Conjugal', 'DropBox Vault', 'slopbar', 'SilentBackgroundProcess', 'magic-lantern_dannephoto'))
$ErrorActionPreference = 'Stop'
$cut = [datetime]::SpecifyKind([datetime]$SuspendedUtc, 'Utc'); $from = $cut.AddDays(-$BeforeDays); $now = [datetime]::UtcNow
$afterDays = [math]::Max(1, ($now - $cut).TotalDays)
function Is-Mlv([string]$l) { $l -match '^(?i)(mlv|quiet-lease)' }

# --- heavy-slot shadow log
$b = @{ acq = 0; slotH = 0.0; waitMin = 0; w = [System.Collections.Generic.List[double]]::new(); t = [System.Collections.Generic.List[double]]::new() }
$a = @{ acq = 0; slotH = 0.0; waitMin = 0; w = [System.Collections.Generic.List[double]]::new(); t = [System.Collections.Generic.List[double]]::new() }
$open = @{}; $labels = @{}
if (Test-Path -LiteralPath $ShadowLog) {
    foreach ($line in [IO.File]::ReadLines($ShadowLog)) {
        try { $o = $line | ConvertFrom-Json } catch { continue }
        $t = [datetime]::SpecifyKind([datetime]$o.utc, 'Utc'); if ($t -lt $from) { continue }
        $side = if ($t -lt $cut) { $b } else { $a }
        $lab = [string]$o.label; $mlv = Is-Mlv $lab
        switch ([string]$o.event) {
            'acquire' {
                if (-not $mlv) { $side.acq++; $k = ($lab -split ' ')[0] -replace '\d+.*$', ''; $labels[$k] = 1 + [int]$labels[$k] }
                $open["$lab"] = $t
                if ($o.feed) { if ($null -ne $o.feed.w30) { $side.w.Add([double]$o.feed.w30) }; if ($null -ne $o.feed.max15) { $side.t.Add([double]$o.feed.max15) } }
            }
            'release' { if ($open.ContainsKey("$lab")) { if (-not $mlv) { $side.slotH += ($t - $open["$lab"]).TotalHours }; $open.Remove("$lab") } }
            'wait' { if (-not $mlv) { $side.waitMin++ } }
        }
    }
}
function Sum-Side($s, [double]$days) {
    [ordered]@{
        days = [math]::Round($days, 1); nonMlvAcquiresPerDay = [math]::Round($s.acq / $days, 1)
        nonMlvSlotHoursPerDay = [math]::Round($s.slotH / $days, 2); nonMlvWaitHoursPerDay = [math]::Round($s.waitMin / 60 / $days, 2)
        packageWattsMean = if ($s.w.Count) { [math]::Round(($s.w | Measure-Object -Average).Average, 1) } else { $null }
        hottestCoreCMean = if ($s.t.Count) { [math]::Round(($s.t | Measure-Object -Average).Average, 1) } else { $null }
    }
}
$heavy = [ordered]@{ present = (Test-Path -LiteralPath $ShadowLog); before = Sum-Side $b $BeforeDays; after = Sum-Side $a $afterDays
    labelFamilies = [ordered]@{}; }
foreach ($k in ($labels.Keys | Sort-Object { - $labels[$_] } | Select-Object -First 8)) { $heavy.labelFamilies[$k] = $labels[$k] }

# --- Claude session-hours per project (sessions capped at 12 h; first/last timestamp only)
function TS([string]$l) { if ($l -match '"timestamp":"([^"]+)"') { try { return ([datetime]$matches[1]).ToUniversalTime() } catch { } }; $null }
$sess = @{}
foreach ($d in Get-ChildItem "$env:USERPROFILE\.claude\projects" -Directory -ErrorAction SilentlyContinue) {
    $proj = $null
    foreach ($p in $Projects) { $slug = 'C--code-' + ($p -replace '[ _]', '-'); if ($d.Name -eq $slug -or $d.Name.StartsWith("$slug--")) { $proj = $p } }
    if (-not $proj) { continue }
    foreach ($f in Get-ChildItem $d.FullName -File -Filter '*.jsonl' -ErrorAction SilentlyContinue) {
        if ($f.LastWriteTimeUtc -lt $from -or $f.CreationTimeUtc -gt $cut) { continue }
        try {
            $fs = [IO.File]::Open($f.FullName, 'Open', 'Read', 'ReadWrite'); $sr = [IO.StreamReader]::new($fs)
            $first = $null; for ($i = 0; $i -lt 8 -and -not $first; $i++) { $l = $sr.ReadLine(); if ($null -eq $l) { break }; $first = TS $l }
            $fs.Seek([math]::Max(0, $fs.Length - 65536), 'Begin') | Out-Null; $sr.DiscardBufferedData(); $tail = $sr.ReadToEnd(); $sr.Close()
            $last = $null; foreach ($l in ($tail -split "`n")) { $x = TS $l; if ($x) { $last = $x } }
            if ($first -and $last -and $last -gt $first) {
                $s0 = if ($first -lt $from) { $from } else { $first }; $e0 = if ($last -gt $cut) { $cut } else { $last }
                if ($e0 -gt $s0) { if (-not $sess[$proj]) { $sess[$proj] = @{ n = 0; h = 0.0 } }; $sess[$proj].n++; $sess[$proj].h += [math]::Min(12, ($e0 - $s0).TotalHours) }
            }
        } catch { }
    }
}
$codexDays = @(for ($dt = $from.Date; $dt -lt $cut.Date; $dt = $dt.AddDays(1)) {
        $dd = Join-Path "$env:USERPROFILE\.codex\sessions" ('{0:yyyy}\{0:MM}\{0:dd}' -f $dt)
        if (Test-Path -LiteralPath $dd) { @(Get-ChildItem -LiteralPath $dd -File).Count } })

# --- toolchain each project needs, from its tracked files
$markers = [ordered]@{ 'Cargo.toml' = 'cargo'; 'package.json' = 'node'; 'pyproject.toml' = 'python'; 'requirements*.txt' = 'python'; '*.csproj' = 'dotnet'; 'CMakeLists.txt' = 'cmake'; 'Makefile' = 'make'; '*.pro' = 'qmake'; '*.cu' = 'nvcc'; 'tauri.conf.json' = 'cargo'; '*.rs' = 'cargo'; '*.mjs' = 'node'; '*.py' = 'python' }
$proj = [ordered]@{}
foreach ($p in $Projects) {
    # A toolchain is "needed" when its marker sits in the project's own code; one found only under
    # samples / fixtures / docs / vendored trees is "may need" (tests or docs builds might still use it).
    $r = Join-Path $CodeRoot $p; $need = @(); $may = @()
    $aside = '(^|/)(samples?|fixtures?|examples?|docs?|vendor|third[_-]?party|external|deps)/'
    if (Test-Path (Join-Path $r '.git')) {
        $paths = @(git -C $r ls-files 2>$null)
        foreach ($m in $markers.Keys) {
            $hits = @($paths | Where-Object { ($_ -split '/')[-1] -like $m })
            if (-not $hits.Count) { continue }
            if (@($hits | Where-Object { $_ -notmatch $aside }).Count) { $need += $markers[$m] } else { $may += $markers[$m] }
        }
    }
    $need = @($need | Sort-Object -Unique); $may = @($may | Where-Object { $need -notcontains $_ } | Sort-Object -Unique)
    $s = $sess[$p]
    $proj[$p] = [ordered]@{ sessions = if ($s) { $s.n } else { 0 }; sessionHours = if ($s) { [math]::Round($s.h, 1) } else { 0 }; needs = $need; mayNeed = $may
        lastCommit = "$(git -C $r log -1 --format=%cs 2>$null)".Trim() }
}
$hw = Get-CimInstance Win32_Processor | Select-Object -First 1
[ordered]@{
    schema = 'fleet-suspended-footprint.v1'; machine = $env:COMPUTERNAME; measuredUtc = $now.ToString('yyyy-MM-ddTHH:mm:ssZ'); suspendedUtc = $cut.ToString('yyyy-MM-dd')
    hardware = [ordered]@{ cpu = $hw.Name.Trim(); cores = [int]((Get-CimInstance Win32_Processor | Measure-Object NumberOfCores -Sum).Sum); logical = [int]((Get-CimInstance Win32_Processor | Measure-Object NumberOfLogicalProcessors -Sum).Sum); ramGB = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB) }
    heavySlot = $heavy; codexSessionsPerDayBefore = if ($codexDays.Count) { [math]::Round((($codexDays | Measure-Object -Sum).Sum) / $codexDays.Count, 1) } else { $null }
    projects = $proj
} | ConvertTo-Json -Depth 6 -Compress
