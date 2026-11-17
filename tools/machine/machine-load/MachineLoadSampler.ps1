#Requires -Version 7.2
<#
.SYNOPSIS
  Fleet machine-load sampler: one long-lived, low-cost process per machine that writes one JSON row per
  UTC minute to %LOCALAPPDATA%\MachineLoad\minute-<UTC date>.jsonl.

.DESCRIPTION
  Every -IntervalSec seconds it reads Windows performance counters (CPU time, effective clock, memory,
  hard faults, disk, network) and diffs per-process CPU time with Get-Process. Each new process is
  labelled once, by its command line, image path and current directory, or inherited from its parent;
  CPU it cannot see (protected processes, processes that started and ended between two reads) is the
  row's residual. Each minute it also joins the newest Core Temp feed rows (package watts, hottest core).

  Single instance per machine (named mutex Global\MachineLoadSampler). Rows carry the schema, the code
  hash and the sampler's own CPU and memory, so a second instance, a stale build or a leak shows up in
  the data. Diagnostic only (bus metrics law 1): nothing here decides anything.

  Exit codes: 0 stopped normally or another instance already holds the mutex; 2 bad arguments;
  3 cannot create the output directory.
#>
[CmdletBinding()]
param(
    [int]$IntervalSec = 10,
    [string]$OutDir = (Join-Path $env:LOCALAPPDATA 'MachineLoad'),
    [int]$RetainDays = 14,
    [string]$CoreTempFeed = 'C:\temp\hwinfo-log-adapter.csv',
    [string]$QuietDir = 'C:\ProgramData\FleetQuiet\windows',
    [int]$RecycleWorkingSetMB = 400,
    [int]$RunMinutes = 0          # 0 = run until stopped; >0 for tests
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 3.0
$SchemaMinute = 'fleet/machine-load-minute/v1'
if ($IntervalSec -lt 2 -or $IntervalSec -gt 60 -or (60 % $IntervalSec) -ne 0) { Write-Error 'IntervalSec must divide 60 and be 2..60'; exit 2 }
try { $null = New-Item -ItemType Directory -Force -Path $OutDir } catch { exit 3 }
$OutDir = [IO.Path]::GetFullPath($OutDir)
$LogPath = Join-Path $OutDir 'sampler.log'
$StatePath = Join-Path $OutDir 'sampler-state.json'

function Write-Log([string]$Message) {
    try {
        if ((Test-Path $LogPath) -and (Get-Item $LogPath).Length -gt 2MB) { Move-Item -Force $LogPath "$LogPath.1" }
        Add-Content -Path $LogPath -Value ('{0} pid={1} {2}' -f [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ'), $PID, $Message)
    } catch { }
}

# ---- single instance ----
$mutex = [Threading.Mutex]::new($false, 'Global\MachineLoadSampler')
$owned = $false
try { $owned = $mutex.WaitOne(0) } catch [Threading.AbandonedMutexException] { $owned = $true }
if (-not $owned) { Write-Log 'another sampler holds the mutex; exiting 0'; exit 0 }

# ---- code identity ----
$here = $PSScriptRoot
$codeFiles = @($PSCommandPath, (Join-Path $here 'MachineLoadNative.cs'), (Join-Path $here 'projects.json')) | Where-Object { Test-Path $_ }
$sha = [Security.Cryptography.SHA256]::Create()
$codeHash = ([BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes((($codeFiles | ForEach-Object { (Get-FileHash -Algorithm SHA256 $_).Hash }) -join ','))))).Replace('-', '').Substring(0, 12).ToLowerInvariant()

if (-not ('MachineLoadNative' -as [type])) {
    Add-Type -Path (Join-Path $here 'MachineLoadNative.cs')
}

# ---- attribution rules ----
# projects.json: ordered [{ "project": "...", "pattern": "<regex>" }]; a pattern may capture group 1 as the
# project name. Optional machine-local additions at %LOCALAPPDATA%\MachineLoad\projects.local.json (first).
$rules = [Collections.Generic.List[object]]::new()
foreach ($rf in @((Join-Path $OutDir 'projects.local.json'), (Join-Path $here 'projects.json'))) {
    if (Test-Path $rf) {
        foreach ($r in (Get-Content -Raw $rf | ConvertFrom-Json).rules) {
            $rules.Add([pscustomobject]@{ Project = [string]$r.project; Regex = [regex]::new([string]$r.pattern, 'IgnoreCase') })
        }
    }
}
$bucketByImage = @{}
$bucketsFile = Join-Path $here 'projects.json'
if (Test-Path $bucketsFile) {
    $b = (Get-Content -Raw $bucketsFile | ConvertFrom-Json).buckets
    foreach ($p in $b.PSObject.Properties) { foreach ($img in $p.Value) { $bucketByImage[$img.ToLowerInvariant()] = $p.Name } }
}

function Get-ProjectFromText([string]$Text) {
    if ([string]::IsNullOrEmpty($Text)) { return $null }
    foreach ($r in $rules) {
        $m = $r.Regex.Match($Text)
        if ($m.Success) {
            if ($r.Project -eq '$1' -and $m.Groups.Count -gt 1) { return $m.Groups[1].Value.ToLowerInvariant() }
            return $r.Project
        }
    }
    return $null
}

# ---- counters ----
$LP = [Environment]::ProcessorCount
function New-Counter($Category, $Name, $Instance) {
    try { $c = [Diagnostics.PerformanceCounter]::new($Category, $Name, $Instance, $true); $null = $c.NextValue(); return $c } catch { Write-Log "counter unavailable: $Category\$Name($Instance): $($_.Exception.Message)"; return $null }
}
$counters = [ordered]@{
    cpu_time_pct   = New-Counter 'Processor' '% Processor Time' '_Total'
    perf_pct       = New-Counter 'Processor Information' '% Processor Performance' '_Total'
    util_pct       = New-Counter 'Processor Information' '% Processor Utility' '_Total'
    avail_mb       = New-Counter 'Memory' 'Available MBytes' ''
    commit_pct     = New-Counter 'Memory' '% Committed Bytes In Use' ''
    hard_faults    = New-Counter 'Memory' 'Pages Input/sec' ''
    disk_idle_pct  = New-Counter 'PhysicalDisk' '% Idle Time' '_Total'
    disk_sec_xfer  = New-Counter 'PhysicalDisk' 'Avg. Disk sec/Transfer' '_Total'
    disk_queue     = New-Counter 'PhysicalDisk' 'Current Disk Queue Length' '_Total'
}
function Read-Counters {
    $v = @{}
    foreach ($k in @($counters.Keys)) {
        $c = $counters[$k]
        if ($null -eq $c) { continue }
        try { $v[$k] = [double]$c.NextValue() } catch { $v[$k] = $null }
    }
    return $v
}
function Get-NetBytes {
    $sum = [long]0
    try {
        foreach ($n in [Net.NetworkInformation.NetworkInterface]::GetAllNetworkInterfaces()) {
            if ($n.OperationalStatus -ne 'Up' -or $n.NetworkInterfaceType -eq 'Loopback') { continue }
            $s = $n.GetIPStatistics(); $sum += $s.BytesReceived + $s.BytesSent
        }
    } catch { }
    return $sum
}

# ---- process CPU attribution ----
$labels = @{}      # key "pid|startTicks" -> label
$lastCpu = @{}     # key -> TotalProcessorTime seconds

function Update-Labels($Procs, $NewKeys) {
    # One WMI query for all new processes this tick: command line, image path, parent.
    if ($NewKeys.Count -eq 0) { return }
    $ids = @($NewKeys.Keys | ForEach-Object { $NewKeys[$_].Id }) | Select-Object -First 200
    $cim = @{}
    try {
        $filter = ($ids | ForEach-Object { "ProcessId=$_" }) -join ' OR '
        foreach ($w in Get-CimInstance Win32_Process -Filter $filter -Property ProcessId, ParentProcessId, CommandLine, ExecutablePath -OperationTimeoutSec 5) { $cim[[int]$w.ProcessId] = $w }
    } catch { Write-Log "cim lookup failed: $($_.Exception.Message)" }
    # Parents first is not guaranteed; resolve in order of start time so a child sees its parent's label.
    foreach ($key in ($NewKeys.Keys | Sort-Object { $NewKeys[$_].StartTicks })) {
        $p = $NewKeys[$key]
        $w = $cim[[int]$p.Id]
        $label = $null
        if ($p.Id -eq $PID) { $labels[$key] = '~machine-load'; continue }
        $texts = @()
        if ($w) { $texts += [string]$w.CommandLine; $texts += [string]$w.ExecutablePath }
        $cwd = [MachineLoadNative]::GetCurrentDirectory([int]$p.Id)
        if ($cwd) { $texts += $cwd }
        foreach ($t in $texts) { if (-not $label) { $label = Get-ProjectFromText $t } }
        if (-not $label -and $w) {
            # inherit a PROJECT label (not a bucket) from the nearest live labelled ancestor
            $parentId = [int]$w.ParentProcessId
            $parentKey = $script:keyByPid[$parentId]
            if ($parentKey -and $labels.ContainsKey($parentKey) -and -not $labels[$parentKey].StartsWith('~')) { $label = $labels[$parentKey] }
        }
        if (-not $label) {
            $img = ($p.Name + '.exe').ToLowerInvariant()
            $label = if ($bucketByImage.ContainsKey($img)) { '~' + $bucketByImage[$img] } else { '~other' }
        }
        $labels[$key] = $label
    }
}

$script:keyByPid = @{}
function Read-ProcessCpu {
    # Returns @{ label = cpuSeconds } since the previous call; seeds new processes at their current total
    # minus nothing (a process first seen this tick contributes its whole lifetime only if it started after
    # the previous tick).
    param([datetime]$PrevTickUtc)
    $out = @{}
    $seen = @{}
    $newKeys = @{}
    $procs = Get-Process
    $script:keyByPid = @{}
    $rows = foreach ($p in $procs) {
        $t = $p.TotalProcessorTime
        if ($null -eq $t) { continue }
        $start = $null
        try { $start = $p.StartTime.ToUniversalTime() } catch { continue }
        $key = '{0}|{1}' -f $p.Id, $start.Ticks
        $script:keyByPid[$p.Id] = $key
        [pscustomobject]@{ Id = $p.Id; Name = $p.ProcessName; Key = $key; Cpu = $t.TotalSeconds; StartUtc = $start; StartTicks = $start.Ticks }
    }
    foreach ($r in $rows) {
        if (-not $labels.ContainsKey($r.Key)) { $newKeys[$r.Key] = $r }
    }
    Update-Labels $rows $newKeys
    foreach ($r in $rows) {
        $seen[$r.Key] = $true
        $prev = $null
        if ($lastCpu.ContainsKey($r.Key)) { $prev = $lastCpu[$r.Key] }
        elseif ($r.StartUtc -gt $PrevTickUtc) { $prev = 0.0 }   # born since last tick: whole life is new
        $lastCpu[$r.Key] = $r.Cpu
        if ($null -eq $prev) { continue }                        # first sight of an old process: seed only
        $d = $r.Cpu - $prev
        if ($d -le 0) { continue }
        $label = $labels[$r.Key]
        if ($out.ContainsKey($label)) { $out[$label] += $d } else { $out[$label] = $d }
        $script:imageCpu[$r.Name] = ($script:imageCpu[$r.Name] ?? 0) + $d
    }
    foreach ($k in @($lastCpu.Keys)) { if (-not $seen.ContainsKey($k)) { $lastCpu.Remove($k); $labels.Remove($k) } }
    return $out
}

# ---- Core Temp feed (local wall-clock rows: "dd.MM.yyyy,H:m:s.fff,cpu%,coreC,pkgW,...") ----
# The zone is re-read every hour: a long-lived process otherwise keeps a cached zone after a zone change
# (a Bachelor sampler erred for 34 h on a cached zone).
$script:tz = [TimeZoneInfo]::Local; $script:tzRead = [DateTime]::UtcNow
function Read-CoreTemp([datetime]$FromUtc, [datetime]$ToUtc) {
    if (([DateTime]::UtcNow - $script:tzRead).TotalHours -ge 1) { [TimeZoneInfo]::ClearCachedData(); $script:tz = [TimeZoneInfo]::Local; $script:tzRead = [DateTime]::UtcNow }
    $tz = $script:tz
    $res = @{ n = 0; pkg_w = [Collections.Generic.List[double]]::new(); core_c = [Collections.Generic.List[double]]::new(); age_s = $null }
    if (-not (Test-Path $CoreTempFeed)) { return $res }
    try {
        $fs = [IO.FileStream]::new($CoreTempFeed, 'Open', 'Read', 'ReadWrite,Delete')
        try {
            $len = $fs.Length; $take = [Math]::Min($len, 16384)
            $null = $fs.Seek($len - $take, 'Begin')
            $buf = [byte[]]::new($take); $null = $fs.Read($buf, 0, $take)
        } finally { $fs.Dispose() }
        $lines = [Text.Encoding]::UTF8.GetString($buf) -split "`r?`n"
        $newest = $null
        foreach ($ln in $lines) {
            $f = $ln.Split(',')
            if ($f.Count -lt 5) { continue }
            $dp = $f[0].Split('.'); $tp = $f[1].Split(':')
            if ($dp.Count -ne 3 -or $tp.Count -ne 3) { continue }
            try {
                $sec = [double]::Parse($tp[2], [Globalization.CultureInfo]::InvariantCulture)
                $local = [datetime]::new([int]$dp[2], [int]$dp[1], [int]$dp[0], [int]$tp[0], [int]$tp[1], [int][Math]::Floor($sec), [DateTimeKind]::Unspecified)
                $utc = [TimeZoneInfo]::ConvertTimeToUtc($local, $tz)
            } catch { continue }
            if (-not $newest -or $utc -gt $newest) { $newest = $utc }
            if ($utc -ge $FromUtc -and $utc -lt $ToUtc) {
                $res.n++
                $res.core_c.Add([double]::Parse($f[3], [Globalization.CultureInfo]::InvariantCulture))
                $res.pkg_w.Add([double]::Parse($f[4], [Globalization.CultureInfo]::InvariantCulture))
            }
        }
        if ($newest) { $res.age_s = [Math]::Round(($ToUtc - $newest).TotalSeconds) }
    } catch { Write-Log "coretemp read failed: $($_.Exception.Message)" }
    return $res
}

function Test-QuietWindow([datetime]$AtUtc) {
    # A FleetQuiet window is armed when a window record exists whose span covers now and that has not been released.
    try {
        if (-not (Test-Path $QuietDir)) { return $false }
        foreach ($f in Get-ChildItem $QuietDir -Filter *.json -File) {
            $w = Get-Content -Raw $f.FullName | ConvertFrom-Json
            $s = $w.PSObject.Properties['startUtc']; $e = $w.PSObject.Properties['endUtc']; $rel = $w.PSObject.Properties['releasedUtc']
            if ($s -and $e -and -not ($rel -and $rel.Value)) {
                if ($AtUtc -ge [datetime]::Parse($s.Value).ToUniversalTime() -and $AtUtc -le [datetime]::Parse($e.Value).ToUniversalTime()) { return $true }
            }
        }
    } catch { }
    return $false
}

function Get-Stat([object[]]$Values, [string]$Kind) {
    $v = @($Values | Where-Object { $null -ne $_ })
    if ($v.Count -eq 0) { return $null }
    switch ($Kind) {
        'mean' { return [Math]::Round((($v | Measure-Object -Average).Average), 3) }
        'max' { return [Math]::Round((($v | Measure-Object -Maximum).Maximum), 3) }
        'min' { return [Math]::Round((($v | Measure-Object -Minimum).Minimum), 3) }
    }
}

function Remove-OldFiles {
    $cut = [DateTime]::UtcNow.Date.AddDays(-$RetainDays)
    foreach ($f in Get-ChildItem $OutDir -Filter 'minute-*.jsonl' -File) {
        if ($f.BaseName -match '^minute-(\d{4}-\d{2}-\d{2})$') {
            $d = [datetime]::ParseExact($Matches[1], 'yyyy-MM-dd', [Globalization.CultureInfo]::InvariantCulture)
            if ($d -lt $cut) { Remove-Item -Force $f.FullName; Write-Log "pruned $($f.Name)" }
        }
    }
}

# ---- main loop ----
$self = Get-Process -Id $PID
$startedUtc = [DateTime]::UtcNow
Write-Log "start code=$codeHash interval=$IntervalSec lp=$LP"
$script:imageCpu = @{}
$prevTick = [DateTime]::UtcNow
$prevNet = Get-NetBytes
try { $null = Read-ProcessCpu -PrevTickUtc $prevTick } catch { Write-Log "fatal in seed: $($_.Exception.Message) at $($_.InvocationInfo.ScriptLineNumber)"; throw }   # seed
$minuteStart = [DateTime]::new(([DateTime]::UtcNow.Ticks - ([DateTime]::UtcNow.Ticks % [TimeSpan]::TicksPerMinute)), [DateTimeKind]::Utc)
$acc = $null
function New-Acc { @{ samples = [Collections.Generic.List[hashtable]]::new(); proj = @{}; secs = 0.0; net = [long]0 } }
$acc = New-Acc
$selfCpu0 = $self.TotalProcessorTime.TotalSeconds
$lastPrune = [DateTime]::MinValue

try {
    while ($true) {
        # sleep to the next tick boundary
        $now = [DateTime]::UtcNow
        $next = [DateTime]::new(($now.Ticks - ($now.Ticks % ([TimeSpan]::TicksPerSecond * $IntervalSec))) + [TimeSpan]::TicksPerSecond * $IntervalSec, [DateTimeKind]::Utc)
        Start-Sleep -Milliseconds ([Math]::Max(50, [int]($next - [DateTime]::UtcNow).TotalMilliseconds))
        $tick = [DateTime]::UtcNow
        $elapsed = ($tick - $prevTick).TotalSeconds
        $c = Read-Counters
        $net = Get-NetBytes
        $pc = Read-ProcessCpu -PrevTickUtc $prevTick
        $prevTick = $tick

        if ($elapsed -gt 3 * $IntervalSec) {
            # suspended, slept or stalled: drop the interval rather than smear it across one sample
            Write-Log ("gap of {0:N0}s; interval discarded" -f $elapsed)
            $prevNet = $net
        } else {
            $acc.samples.Add($c)
            $acc.secs += $elapsed
            if ($net -ge $prevNet) { $acc.net += ($net - $prevNet) }
            $prevNet = $net
            foreach ($k in $pc.Keys) { $acc.proj[$k] = ($acc.proj[$k] ?? 0) + $pc[$k] }
        }

        $thisMinute = [DateTime]::new(($tick.Ticks - ($tick.Ticks % [TimeSpan]::TicksPerMinute)), [DateTimeKind]::Utc)
        if ($thisMinute -gt $minuteStart) {
            if ($acc.samples.Count -gt 0) {
                $s = $acc.samples
                $cpuMean = Get-Stat ($s | ForEach-Object { $_['cpu_time_pct'] }) 'mean'
                $ct = Read-CoreTemp $minuteStart $minuteStart.AddMinutes(1)
                $machineCpuS = if ($null -ne $cpuMean) { [Math]::Round($cpuMean / 100 * $LP * $acc.secs, 2) } else { $null }
                $attributed = 0.0; foreach ($v in $acc.proj.Values) { $attributed += $v }
                $proj = [ordered]@{}
                foreach ($k in ($acc.proj.Keys | Sort-Object { -$acc.proj[$_] })) { $proj[$k] = [Math]::Round($acc.proj[$k], 2) }
                $top = @($script:imageCpu.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 5 | ForEach-Object { , @($_.Key, [Math]::Round($_.Value, 2)) })
                $self.Refresh()
                $row = [ordered]@{
                    schema   = $SchemaMinute
                    machine  = $env:COMPUTERNAME
                    ts       = $minuteStart.ToString('yyyy-MM-ddTHH:mm:00Z')
                    code     = $codeHash
                    lp       = $LP
                    n        = $s.Count
                    secs     = [Math]::Round($acc.secs, 1)
                    cpu      = [ordered]@{
                        time_pct_mean = $cpuMean
                        time_pct_max  = Get-Stat ($s | ForEach-Object { $_['cpu_time_pct'] }) 'max'
                        busy_threads  = if ($null -ne $cpuMean) { [Math]::Round($cpuMean / 100 * $LP, 2) } else { $null }
                        perf_pct_mean = Get-Stat ($s | ForEach-Object { $_['perf_pct'] }) 'mean'
                        perf_pct_min  = Get-Stat ($s | ForEach-Object { $_['perf_pct'] }) 'min'
                        util_pct_mean = Get-Stat ($s | ForEach-Object { $_['util_pct'] }) 'mean'
                    }
                    mem      = [ordered]@{
                        avail_gb_min    = if ($null -ne ($m = Get-Stat ($s | ForEach-Object { $_['avail_mb'] }) 'min')) { [Math]::Round($m / 1024, 2) } else { $null }
                        commit_pct_max  = Get-Stat ($s | ForEach-Object { $_['commit_pct'] }) 'max'
                        hard_faults_mean = Get-Stat ($s | ForEach-Object { $_['hard_faults'] }) 'mean'
                    }
                    disk     = [ordered]@{
                        busy_pct_mean = if ($null -ne ($m = Get-Stat ($s | ForEach-Object { $_['disk_idle_pct'] }) 'mean')) { [Math]::Round([Math]::Max(0, 100 - $m), 2) } else { $null }
                        busy_pct_max  = if ($null -ne ($m = Get-Stat ($s | ForEach-Object { $_['disk_idle_pct'] }) 'min')) { [Math]::Round([Math]::Max(0, 100 - $m), 2) } else { $null }
                        lat_ms_max    = if ($null -ne ($m = Get-Stat ($s | ForEach-Object { $_['disk_sec_xfer'] }) 'max')) { [Math]::Round($m * 1000, 2) } else { $null }
                        queue_max     = Get-Stat ($s | ForEach-Object { $_['disk_queue'] }) 'max'
                        c_free_gb     = [Math]::Round(([IO.DriveInfo]::new('C')).AvailableFreeSpace / 1GB, 1)
                    }
                    net_mbps = if ($acc.secs -gt 0) { [Math]::Round($acc.net * 8 / 1e6 / $acc.secs, 2) } else { $null }
                    thermal  = [ordered]@{
                        n          = $ct.n
                        pkg_w_mean = if ($ct.n) { [Math]::Round(($ct.pkg_w | Measure-Object -Average).Average, 1) } else { $null }
                        pkg_w_max  = if ($ct.n) { [Math]::Round(($ct.pkg_w | Measure-Object -Maximum).Maximum, 1) } else { $null }
                        core_c_max = if ($ct.n) { [Math]::Round(($ct.core_c | Measure-Object -Maximum).Maximum, 1) } else { $null }
                        feed_age_s = $ct.age_s
                    }
                    quiet    = (Test-QuietWindow $minuteStart)
                    cpu_s    = [ordered]@{ machine = $machineCpuS; attributed = [Math]::Round($attributed, 2); residual = if ($null -ne $machineCpuS) { [Math]::Round($machineCpuS - $attributed, 2) } else { $null } }
                    proj     = $proj
                    top      = $top
                    sampler  = [ordered]@{ cpu_s = [Math]::Round($self.TotalProcessorTime.TotalSeconds - $selfCpu0, 2); ws_mb = [Math]::Round($self.WorkingSet64 / 1MB); up_min = [Math]::Round(([DateTime]::UtcNow - $startedUtc).TotalMinutes) }
                }
                $selfCpu0 = $self.TotalProcessorTime.TotalSeconds
                $file = Join-Path $OutDir ('minute-{0}.jsonl' -f $minuteStart.ToString('yyyy-MM-dd'))
                [IO.File]::AppendAllText($file, (($row | ConvertTo-Json -Depth 6 -Compress) + "`n"))
                [IO.File]::WriteAllText($StatePath, ([ordered]@{ pid = $PID; started_utc = $startedUtc.ToString('o'); last_row_ts = $row.ts; written_utc = [DateTime]::UtcNow.ToString('o'); code = $codeHash } | ConvertTo-Json -Compress))
                if ($self.WorkingSet64 / 1MB -gt $RecycleWorkingSetMB) { Write-Log ("working set {0:N0} MB over {1}; exiting for the task to restart" -f ($self.WorkingSet64 / 1MB), $RecycleWorkingSetMB); break }
            }
            $minuteStart = $thisMinute
            $acc = New-Acc
            $script:imageCpu = @{}
            if (([DateTime]::UtcNow - $lastPrune).TotalHours -ge 6) { Remove-OldFiles; $lastPrune = [DateTime]::UtcNow }
            if ($RunMinutes -gt 0 -and ([DateTime]::UtcNow - $startedUtc).TotalMinutes -ge $RunMinutes) { break }
        }
    }
} catch {
    Write-Log "fatal: $($_.Exception.Message) at $($_.InvocationInfo.ScriptLineNumber)"
    throw
} finally {
    Write-Log 'stop'
    try { $mutex.ReleaseMutex() } catch { }
}
exit 0
