# HostHeadroom.psm1 - per-machine load sampling, slowdown canary, headroom summary and bus publication.
# Read tools/machine/host-headroom/README.md first. Sampling runs as the signed-in user at Highest
# run level (elevation is needed only to read other processes' command lines for attribution).

# StrictMode 1: catches unset variables; property-level strictness would throw on the heterogeneous
# JSON rows this module reads (HeavySlot ledger rows differ by event).
Set-StrictMode -Version 1.0

$script:Schema       = 'fleet-host-headroom.v1'
$script:SampleSchema = 'host-headroom-sample.v1'
$script:CoreTempFeed = 'C:\temp\hwinfo-log-adapter.csv'
$script:HeavySlotLedger = 'C:\ProgramData\HeavySlot\ledger.jsonl'
$script:QuietWindowDir  = 'C:\ProgramData\FleetQuiet\windows'

# English counter paths. The minis are en-US; a localized host fails closed at the first sample.
$script:CounterPaths = [ordered]@{
    busy      = '\Processor Information(_Total)\% Processor Time'       # how busy the logical processors are
    util      = '\Processor Information(_Total)\% Processor Utility'    # work done, clock-scaled, can exceed 100
    freq      = '\Processor Information(_Total)\% of Maximum Frequency' # clock vs max: falls under power/heat limits
    queue     = '\System\Processor Queue Length'
    availMb   = '\Memory\Available MBytes'
    commitPct = '\Memory\% Committed Bytes In Use'
    commitB   = '\Memory\Committed Bytes'
    limitB    = '\Memory\Commit Limit'
    pagesIn   = '\Memory\Pages Input/sec'
    diskIdle  = '\PhysicalDisk(_Total)\% Idle Time'
    diskLat   = '\PhysicalDisk(_Total)\Avg. Disk sec/Transfer'
}

$script:CwdReader = $null

function Get-HostHeadroomRoot {
    $r = Join-Path $env:LOCALAPPDATA 'HostHeadroom'
    if (-not (Test-Path -LiteralPath $r)) { New-Item -ItemType Directory -Path $r -Force | Out-Null }
    $r
}

function Get-HostHardware {
    $cs  = Get-CimInstance Win32_ComputerSystem
    $cpu = @(Get-CimInstance Win32_Processor)
    [ordered]@{
        logical_processors = [int](($cpu | Measure-Object NumberOfLogicalProcessors -Sum).Sum)
        cores              = [int](($cpu | Measure-Object NumberOfCores -Sum).Sum)
        ram_gb             = [math]::Round($cs.TotalPhysicalMemory / 1GB, 1)
        cpu_model          = ($cpu[0].Name).Trim()
    }
}

# Read a file other tools keep appending to (HeavySlot ledger, Core Temp feed, our own samples) without
# blocking their writers: open with FileShare ReadWrite|Delete, read it all into memory, close, then parse.
# [IO.File]::ReadLines holds a FileShare.Read handle for the whole parse, which makes their appends fail.
function Read-SharedLines([string]$Path) {
    $fs = [IO.FileStream]::new($Path, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::ReadWrite -bor [IO.FileShare]::Delete)
    try { $sr = [IO.StreamReader]::new($fs, [Text.Encoding]::UTF8, $true); $text = $sr.ReadToEnd() } finally { $fs.Dispose() }
    $text -split "`r?`n"
}

# Append one line, retrying briefly if a reader without shared access holds the file.
function Add-SharedLine([string]$Path, [string]$Line) {
    for ($i = 1; $i -le 5; $i++) {
        try {
            $fs = [IO.FileStream]::new($Path, [IO.FileMode]::Append, [IO.FileAccess]::Write, [IO.FileShare]::ReadWrite -bor [IO.FileShare]::Delete)
            try { $b = [Text.Encoding]::UTF8.GetBytes($Line + "`n"); $fs.Write($b, 0, $b.Length) } finally { $fs.Dispose() }
            return
        } catch [IO.IOException] { Start-Sleep -Milliseconds (200 * $i) }
    }
    throw "could not append to $Path after 5 tries"
}

function ConvertTo-UtcStamp([datetime]$d) { $d.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ') }

# ---------------------------------------------------------------- attribution

# Project = first path segment under a workspace root, or a fixed worktree root. Process families
# that carry no path are still classed (claude/codex CLIs, Defender, build and test tools) so the
# unattributed share is reported instead of hidden.
$script:ProjectRules = @(
    @{ re = '(?i)\\!Layi Wkspc\\([^\\"/]+)'; fixed = $null }   # also matches a bare cwd (no trailing separator)
    @{ re = '(?i)\b([a-z]:\\abwt\\[^\\"/ ]+)';  fixed = '<worktree>' }
)
$script:FamilyRules = [ordered]@{
    'defender'    = '^(?i)(MsMpEng|MpDefenderCoreService|NisSrv|MpCopyAccelerator)\.exe$'
    'llm-cli'     = '^(?i)(claude|codex|node)\.exe$'
    'build'       = '^(?i)(MSBuild|dotnet|VBCSCompiler|cl|link|cargo|rustc|cmake|ninja|msvsmon|devenv)\.exe$'
    'test'        = '^(?i)(testhost.*|vstest\.console|python|pytest|py)\.exe$'
    'shell'       = '^(?i)(pwsh|powershell|bash|sh|cmd|conhost|git|ssh)\.exe$'
    'wmi'         = '^(?i)WmiPrvSE\.exe$'
}

function ConvertTo-ProjectSlug([string]$name) {
    $s = ($name.ToLowerInvariant() -replace '[^a-z0-9]+', '-').Trim('-')
    switch -Regex ($s) {
        '^adobe-document-cloud-ingester' { 'adobe-ingester'; break }
        '^softwarefactory-fleet-doctrine' { 'fleet-doctrine'; break }
        '^agent-bridge'                   { 'agent-bridge'; break }
        '^mlv'                            { 'mlv-app'; break }
        default                           { $s }
    }
}

# A worktree outside the workspace belongs to the repo its .git file points at (gitdir: <repo>\.git\worktrees\x).
# Cached per process; unreadable -> 'worktree-unknown', never a guess.
$script:WorktreeCache = @{}
function Resolve-WorktreeProject([string]$wt) {
    $k = $wt.ToLowerInvariant()
    if ($script:WorktreeCache.ContainsKey($k)) { return $script:WorktreeCache[$k] }
    $proj = 'worktree-unknown'
    try {
        $g = Join-Path $wt '.git'
        if (Test-Path -LiteralPath $g -PathType Leaf) {
            $m = [regex]::Match((Get-Content -LiteralPath $g -TotalCount 1), '(?i)gitdir:\s*(.+?)[\\/]\.git[\\/]worktrees[\\/]')
            if ($m.Success) { $proj = ConvertTo-ProjectSlug (Split-Path $m.Groups[1].Value -Leaf) }
        }
    } catch { }
    $script:WorktreeCache[$k] = $proj
    $proj
}

function Resolve-PathProject([string]$text) {
    if ([string]::IsNullOrEmpty($text)) { return $null }
    foreach ($r in $script:ProjectRules) {
        $m = [regex]::Match($text, $r.re)
        if ($m.Success) {
            if ($r.fixed -eq '<worktree>') { return (Resolve-WorktreeProject $m.Groups[1].Value) }
            if ($r.fixed) { return $r.fixed } else { return (ConvertTo-ProjectSlug $m.Groups[1].Value) }
        }
    }
    $null
}

function Resolve-Family([string]$name) {
    foreach ($k in $script:FamilyRules.Keys) { if ($name -match $script:FamilyRules[$k]) { return $k } }
    'other'
}

# One snapshot of the process table. Project is resolved from the process's own path, else its
# nearest ancestor's, else the most common project among its descendants (a claude CLI with no
# path in its command line is attributed by the git/pwsh/pytest children it spawns).
function Get-ProcessSnapshot {
    $procs = @(Get-CimInstance Win32_Process -Property ProcessId, ParentProcessId, Name, ExecutablePath, CommandLine, KernelModeTime, UserModeTime, PrivatePageCount, CreationDate)
    $byPid = @{}; $kids = @{}; $own = @{}; $cwdHits = 0
    if ($null -eq $script:CwdReader) { try { Initialize-HostHeadroomCanary; $script:CwdReader = $true } catch { $script:CwdReader = $false } }
    foreach ($p in $procs) {
        $id = [int]$p.ProcessId; $byPid[$id] = $p
        $own[$id] = Resolve-PathProject ("{0} {1}" -f $p.ExecutablePath, $p.CommandLine)
        if (-not $own[$id] -and $id -gt 4 -and $script:CwdReader) {
            $cwd = [HostHeadroomNative]::GetCurrentDirectory($id)
            if ($cwd) { $own[$id] = Resolve-PathProject $cwd; if ($own[$id]) { $cwdHits++ } }
        }
    }
    foreach ($p in $procs) {
        $pp = [int]$p.ParentProcessId
        if ($byPid.ContainsKey($pp) -and $byPid[$pp].CreationDate -le $p.CreationDate) {
            if (-not $kids.ContainsKey($pp)) { $kids[$pp] = [System.Collections.Generic.List[int]]::new() }
            $kids[$pp].Add([int]$p.ProcessId)
        }
    }
    $up = @{}
    foreach ($p in $procs) {
        $id = [int]$p.ProcessId; $proj = $own[$id]; $cur = $p; $hops = 0
        while (-not $proj -and $hops -lt 16) {
            $pp = [int]$cur.ParentProcessId
            if ($pp -eq 0 -or $pp -eq [int]$cur.ProcessId -or -not $byPid.ContainsKey($pp)) { break }
            $par = $byPid[$pp]
            if ($par.CreationDate -gt $cur.CreationDate) { break }   # reused pid: not the real parent
            $proj = $own[$pp]; $cur = $par; $hops++
        }
        $up[$id] = $proj
    }
    # the sampler's own process tree (this pwsh, its WMI calls' children) is its own family, never a project
    $selfTree = [System.Collections.Generic.HashSet[int]]::new(); $st = [System.Collections.Generic.Stack[int]]::new(); $st.Push($PID)
    while ($st.Count) { $k = $st.Pop(); if ($selfTree.Add($k) -and $kids.ContainsKey($k)) { foreach ($g in $kids[$k]) { $st.Push($g) } } }
    $snap = @{}
    foreach ($p in $procs) {
        $id = [int]$p.ProcessId; $proj = $up[$id]
        if ($selfTree.Contains($id)) { $snap[$id] = [pscustomobject]@{ cpu = ([double]$p.KernelModeTime + [double]$p.UserModeTime) / 1e7; ws = [double]$p.PrivatePageCount; project = $null; via = $null; family = 'headroom-sampler'; created = $p.CreationDate; readable = $true }; continue }; $via = if ($own[$id]) { 'own' } elseif ($proj) { 'ancestor' } else { $null }
        if (-not $proj -and $kids.ContainsKey($id)) {
            $votes = @{}; $stack = [System.Collections.Generic.Stack[int]]::new(); foreach ($k in $kids[$id]) { $stack.Push($k) }
            $seen = 0
            while ($stack.Count -and $seen -lt 400) {
                $k = $stack.Pop(); $seen++
                if ($own[$k]) { $votes[$own[$k]] = 1 + ($votes[$own[$k]] ?? 0) }
                if ($kids.ContainsKey($k)) { foreach ($g in $kids[$k]) { $stack.Push($g) } }
            }
            if ($votes.Count) { $proj = ($votes.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 1).Key; $via = 'descendant' }
        }
        $snap[$id] = [pscustomobject]@{
            cpu     = ([double]$p.KernelModeTime + [double]$p.UserModeTime) / 1e7
            ws      = [double]$p.PrivatePageCount
            project = $proj
            via     = $via
            family  = Resolve-Family $p.Name
            created = $p.CreationDate
            readable = [bool]$p.CommandLine -or [bool]$p.ExecutablePath
        }
    }
    $snap
}

# Cores and RAM per project and per process family between two snapshots. A process that ended
# between snapshots loses its last partial interval; the sample records how many did.
function Get-UsageDelta($prev, $cur, [double]$seconds) {
    $proj = @{}; $fam = @{}; $ram = @{}; $ended = 0; $unreadable = 0.0; $total = 0.0
    foreach ($id in $prev.Keys) { if (-not $cur.ContainsKey($id) -or $cur[$id].created -ne $prev[$id].created) { $ended++ } }
    $cutoff = (Get-Date).AddSeconds(-$seconds - 5)
    foreach ($id in $cur.Keys) {
        $c = $cur[$id]
        if ($id -in 0, 4) { continue }   # Idle and System pseudo-processes
        $base = $null
        if ($prev.ContainsKey($id) -and $prev[$id].created -eq $c.created) { $base = $prev[$id].cpu }
        elseif ($c.created -and $c.created -ge $cutoff) { $base = 0.0 }   # started inside the interval
        if ($null -eq $base) { continue }
        $d = [math]::Max(0.0, $c.cpu - $base); $total += $d
        if (-not $c.readable) { $unreadable += $d }
        $pk = if ($c.project) { $c.project } elseif ($c.family -eq 'headroom-sampler') { '_sampler' } else { '_unattributed' }
        $proj[$pk] = ($proj[$pk] ?? 0.0) + $d
        $ram[$pk]  = ($ram[$pk] ?? 0.0) + $c.ws
        $fam[$c.family] = ($fam[$c.family] ?? 0.0) + $d
    }
    $po = [ordered]@{}; foreach ($k in ($proj.Keys | Sort-Object)) { $po[$k] = [ordered]@{ cores = [math]::Round($proj[$k] / $seconds, 3); ram_gb = [math]::Round($ram[$k] / 1GB, 2) } }
    $fo = [ordered]@{}; foreach ($k in ($fam.Keys | Sort-Object)) { $fo[$k] = [math]::Round($fam[$k] / $seconds, 3) }
    [ordered]@{ seconds = [math]::Round($seconds, 1); cores_total = [math]::Round($total / $seconds, 3)
                unreadable_cores = [math]::Round($unreadable / $seconds, 3); ended = $ended; projects = $po; families = $fo }
}

# ---------------------------------------------------------------- canary (measures slowdown directly)

# A fixed small unit of work, timed on a schedule. Its p10 over the window is the quiet baseline;
# p95/p10 is how much slower the same work ran when the machine was busy. That ratio is the cost a
# NEW job pays and the contention the existing ones feel, including power-limit clock drops that
# no utilisation percentage shows.
$script:CanarySource = @'
using System; using System.Diagnostics; using System.IO; using System.Runtime.InteropServices; using System.Security.Cryptography; using System.Threading.Tasks;
// Ported from candidate A (PR 99, tools/machine/machine-load/MachineLoadNative.cs), per the 2026-11-17 merit
// adjudication (per-property survivor S2): the current directory of another 64-bit process, read from its PEB
// (RTL_USER_PROCESS_PARAMETERS.CurrentDirectory). Null when unreadable (protected, other user, 32-bit, exited).
public static class HostHeadroomNative {
    [StructLayout(LayoutKind.Sequential)] struct Pbi { public IntPtr ExitStatus, PebBaseAddress, AffinityMask, BasePriority, UniqueProcessId, InheritedFromUniqueProcessId; }
    [DllImport("ntdll.dll")] static extern int NtQueryInformationProcess(IntPtr h, int c, ref Pbi i, int l, out int r);
    [DllImport("kernel32.dll", SetLastError = true)] static extern IntPtr OpenProcess(int a, bool i, int pid);
    [DllImport("kernel32.dll", SetLastError = true)] static extern bool ReadProcessMemory(IntPtr h, IntPtr a, byte[] b, IntPtr s, out IntPtr r);
    [DllImport("kernel32.dll")] static extern bool CloseHandle(IntPtr h);
    [DllImport("kernel32.dll")] static extern bool IsWow64Process(IntPtr h, out bool w);
    public static string GetCurrentDirectory(int pid) {
        IntPtr h = OpenProcess(0x0400 | 0x0010, false, pid);
        if (h == IntPtr.Zero) return null;
        try {
            bool w; if (IsWow64Process(h, out w) && w) return null;
            var i = new Pbi(); int r0; if (NtQueryInformationProcess(h, 0, ref i, Marshal.SizeOf(i), out r0) != 0) return null;
            IntPtr rd; var ptr = new byte[8];
            if (!ReadProcessMemory(h, i.PebBaseAddress + 0x20, ptr, (IntPtr)8, out rd)) return null;
            IntPtr pars = (IntPtr)BitConverter.ToInt64(ptr, 0); var us = new byte[16];
            if (!ReadProcessMemory(h, pars + 0x38, us, (IntPtr)16, out rd)) return null;
            int len = BitConverter.ToUInt16(us, 0); IntPtr buf = (IntPtr)BitConverter.ToInt64(us, 8);
            if (len <= 0 || len > 8192) return null;
            var txt = new byte[len]; if (!ReadProcessMemory(h, buf, txt, (IntPtr)len, out rd)) return null;
            return System.Text.Encoding.Unicode.GetString(txt);
        } catch { return null; } finally { CloseHandle(h); }
    }
}
public static class HostHeadroomCanary {
    static byte[] Buf(int kb) { var b = new byte[kb * 1024]; new Random(7).NextBytes(b); return b; }
    static void Spin(byte[] b, int reps) { for (int i = 0; i < reps; i++) { b[i % b.Length] ^= SHA256.HashData(b)[0]; } }
    public static double Single(int kb, int reps) { var b = Buf(kb); var sw = Stopwatch.StartNew(); Spin(b, reps); return sw.Elapsed.TotalMilliseconds; }
    public static double Wide(int threads, int kb, int reps) {
        var bufs = new byte[threads][]; for (int t = 0; t < threads; t++) bufs[t] = Buf(kb);
        var sw = Stopwatch.StartNew();
        Parallel.For(0, threads, new ParallelOptions { MaxDegreeOfParallelism = threads }, t => Spin(bufs[t], reps));
        return sw.Elapsed.TotalMilliseconds;
    }
    public static double Disk(string dir, int mb) {
        var path = Path.Combine(dir, "canary-" + Environment.ProcessId + ".bin"); var b = Buf(1024); var r = new byte[1 << 20];
        var sw = Stopwatch.StartNew();
        using (var fs = new FileStream(path, FileMode.Create, FileAccess.ReadWrite, FileShare.None, 1 << 20, FileOptions.WriteThrough | FileOptions.DeleteOnClose)) {
            for (int i = 0; i < mb; i++) fs.Write(b, 0, b.Length);
            fs.Flush(true); fs.Position = 0; while (fs.Read(r, 0, r.Length) > 0) { }
        }
        return sw.Elapsed.TotalMilliseconds;
    }
}
'@

function Initialize-HostHeadroomCanary {
    if (('HostHeadroomCanary' -as [type]) -and ('HostHeadroomNative' -as [type])) { return }
    $tag = [BitConverter]::ToString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($script:CanarySource + $PSVersionTable.PSVersion))).Replace('-', '').Substring(0, 12)
    $dll = Join-Path (Get-HostHeadroomRoot) "canary-$tag.dll"
    if (-not (Test-Path -LiteralPath $dll)) { Add-Type -TypeDefinition $script:CanarySource -OutputAssembly $dll -OutputType Library }
    Add-Type -Path $dll
}

# About 0.3 s single-thread, 0.3 s on HALF the physical cores (owner rule 2026-10-07: never a saturation
# load, at most half the cores), and a 32 MB write-through file, at idle. Duty cycle is about 0.2%.
function Invoke-HostHeadroomCanary([int]$PhysicalCores) {
    Initialize-HostHeadroomCanary
    $null = [HostHeadroomCanary]::Single(64, 50)   # warm-up: JIT and caches, not recorded
    $w = [math]::Max(1, [int][math]::Floor($PhysicalCores / 2))
    [ordered]@{
        single_ms = [math]::Round([HostHeadroomCanary]::Single(1024, 600), 1)
        wide_ms   = [math]::Round([HostHeadroomCanary]::Wide($w, 1024, 600), 1)
        wide_threads = $w
        disk_ms   = [math]::Round([HostHeadroomCanary]::Disk((Get-HostHeadroomRoot), 32), 1)
    }
}

# ---------------------------------------------------------------- sampler

# One pwsh run streams one PDH query (rate counters average the whole interval, not a 1 s spot),
# takes a process snapshot every AttributionEvery samples, and runs the canary once per run.
# Every sample records how late it landed: a sampler starved by load is itself contention evidence.
function Invoke-HostHeadroomSampler {
    [CmdletBinding()]
    param([int]$DurationSec = 255, [int]$IntervalSec = 15, [int]$AttributionEvery = 4, [int]$RetentionDays = 14, [switch]$NoCanary)
    $startedAt = Get-Date
    $root = Get-HostHeadroomRoot
    $hw = Get-HostHardware
    # Get-Counter waits one interval before its first sample, and snapshots/canary add time: 255 s of
    # samples leaves ~30 s of slack in the 300 s slot, so a slow run under load is not skipped by IgnoreNew.
    $max = [math]::Max(1, [int][math]::Floor($DurationSec / $IntervalSec))
    $keys = @($script:CounterPaths.Keys); $paths = @($script:CounterPaths.Values)
    $suffix = @($paths | ForEach-Object { $_.Substring($_.IndexOf('\', 1)).ToLowerInvariant() })
    $elevated = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    $self = Get-Process -Id $PID
    $selfCpu0 = $self.TotalProcessorTime.TotalSeconds
    $prevSnap = Get-ProcessSnapshot; $prevAt = Get-Date
    $canaryAt = [math]::Max(1, [int][math]::Floor($max / 2))
    $i = 0; $last = Get-Date
    $file = { Join-Path $root ("samples-{0}.jsonl" -f [datetime]::UtcNow.ToString('yyyyMMdd')) }
    Get-Counter -Counter $paths -SampleInterval $IntervalSec -MaxSamples $max -ErrorAction Stop | ForEach-Object {
        $i++; $now = Get-Date
        $v = @{}
        foreach ($s in $_.CounterSamples) {
            $sp = $s.Path.ToLowerInvariant()
            for ($k = 0; $k -lt $suffix.Count; $k++) { if ($sp.EndsWith($suffix[$k])) { $v[$keys[$k]] = $s.CookedValue; break } }
        }
        $rec = [ordered]@{
            schema    = $script:SampleSchema
            ts        = ConvertTo-UtcStamp $now
            late_s    = [math]::Round([math]::Max(0, ($now - $last).TotalSeconds - $IntervalSec), 1)
            lp        = $hw.logical_processors
            cores     = $hw.cores
            elevated  = $elevated
            busy      = [math]::Round([double]($v['busy'] ?? -1), 1)
            util      = [math]::Round([double]($v['util'] ?? -1), 1)
            freq      = [math]::Round([double]($v['freq'] ?? -1), 1)
            queue     = [int]($v['queue'] ?? -1)
            avail_mb  = [int]($v['availMb'] ?? -1)
            commit    = [math]::Round([double]($v['commitPct'] ?? -1), 1)
            commit_free_gb = $(if ($v.ContainsKey('commitB') -and $v.ContainsKey('limitB')) { [math]::Round(([double]$v['limitB'] - [double]$v['commitB']) / 1GB, 1) } else { -1 })
            pages_in  = [math]::Round([double]($v['pagesIn'] ?? -1), 1)
            disk_idle = [math]::Round([double]($v['diskIdle'] ?? -1), 1)
            disk_ms   = [math]::Round(1000 * [double]($v['diskLat'] ?? -0.001), 2)
        }
        if ($i -eq 1) { $rec.run_start_delay_s = [math]::Round(($now - $startedAt).TotalSeconds - $IntervalSec, 1) }
        $last = $now
        if ($i % $AttributionEvery -eq 0) {
            $snap = Get-ProcessSnapshot; $t = Get-Date
            $rec.attribution = Get-UsageDelta $prevSnap $snap ($t - $prevAt).TotalSeconds
            $prevSnap = $snap; $prevAt = $t
        }
        if (-not $NoCanary -and $i -eq $canaryAt) { $rec.canary = Invoke-HostHeadroomCanary $hw.cores }
        if ($i -eq $max) { $self.Refresh(); $rec.sampler_cpu_s = [math]::Round($self.TotalProcessorTime.TotalSeconds - $selfCpu0, 2) }
        Add-SharedLine (& $file) ($rec | ConvertTo-Json -Compress -Depth 6)
    }
    Get-ChildItem -LiteralPath $root -Filter 'samples-*.jsonl' | Where-Object { $_.LastWriteTimeUtc -lt [datetime]::UtcNow.AddDays(-$RetentionDays) } | Remove-Item -Force
}

# ---------------------------------------------------------------- readers

function Get-Pct($xs, [double]$p) {
    $a = @($xs | Where-Object { $null -ne $_ })
    if ($a.Count -eq 0) { return $null }
    $s = [double[]]($a | Sort-Object)
    $idx = [math]::Min($s.Count - 1, [math]::Max(0, [int][math]::Ceiling($p / 100 * $s.Count) - 1))
    [math]::Round($s[$idx], 2)
}

# ConvertFrom-Json turns ISO stamps into DateTime on its own; accept either form.
function ConvertTo-UtcDate($v, $styles = ([Globalization.DateTimeStyles]::AdjustToUniversal -bor [Globalization.DateTimeStyles]::AssumeUniversal)) {
    if ($v -is [datetime]) { if ($v.Kind -eq [DateTimeKind]::Unspecified) { return [datetime]::SpecifyKind($v, [DateTimeKind]::Utc) }; return $v.ToUniversalTime() }
    if ($v -is [datetimeoffset]) { return $v.UtcDateTime }
    [datetime]::ParseExact([string]$v, 'yyyy-MM-ddTHH:mm:ssZ', [Globalization.CultureInfo]::InvariantCulture, $styles)
}

function Read-HostHeadroomSamples([double]$Hours, [string]$Root = (Get-HostHeadroomRoot)) {
    $since = [datetime]::UtcNow.AddHours(-$Hours)
    $files = 0..([int][math]::Ceiling($Hours / 24) + 1) | ForEach-Object { Join-Path $Root ("samples-{0}.jsonl" -f $since.AddDays($_).ToString('yyyyMMdd')) } |
             Select-Object -Unique | Where-Object { Test-Path -LiteralPath $_ }
    $styles = [Globalization.DateTimeStyles]::AdjustToUniversal -bor [Globalization.DateTimeStyles]::AssumeUniversal
    foreach ($f in $files) {
        foreach ($line in (Read-SharedLines $f)) {
            if (-not $line) { continue }
            try { $r = $line | ConvertFrom-Json } catch { continue }
            $ts = ConvertTo-UtcDate $r.ts $styles
            if ($ts -ge $since) { $r | Add-Member -NotePropertyName tsUtc -NotePropertyValue $ts -Force; $r }
        }
    }
}

# Owner quiet windows (FleetQuiet) pause the projects for thermal trials and admin work; the
# trial load inside them is synthetic, so samples inside a window are excluded from every figure.
function Get-QuietWindows {
    $dir = $script:QuietWindowDir
    if (-not (Test-Path -LiteralPath $dir)) { return @() }
    foreach ($f in Get-ChildItem -LiteralPath $dir -File) {
        try { $w = Get-Content -LiteralPath $f.FullName -Raw | ConvertFrom-Json } catch { continue }
        if (-not $w.PSObject.Properties['armedUtc']) { continue }
        $s = ConvertTo-UtcDate $w.armedUtc
        $e = if ($w.PSObject.Properties['untilUtc'] -and $w.untilUtc) { ConvertTo-UtcDate $w.untilUtc } else { [datetime]::UtcNow }
        if ($f.Name -like '*.released' -and $f.LastWriteTimeUtc -lt $e) { $e = $f.LastWriteTimeUtc }
        [pscustomobject]@{ start = $s; end = $e.AddMinutes(10) }   # +10 min: cool-down after a trial
    }
}

function Test-InWindows([datetime]$utc, $windows) {
    foreach ($w in $windows) { if ($utc -ge $w.start -and $utc -le $w.end) { return $true } }
    $false
}

# Weighted percentile: each value counts for the seconds it covered.
function Get-WeightedPct([double[]]$v, [double[]]$wt, [double]$p) {
    if (-not $v -or $v.Count -eq 0) { return $null }
    $idx = [int[]](0..($v.Count - 1) | Sort-Object { $v[$_] })
    $total = ($wt | Measure-Object -Sum).Sum; $acc = 0.0
    foreach ($i in $idx) { $acc += $wt[$i]; if ($acc -ge $p / 100 * $total) { return [math]::Round($v[$i], 2) } }
    [math]::Round($v[$idx[-1]], 2)
}

# Core Temp's dense feed: date dd.MM.yyyy, local time with unpadded fields, a row every 2-4 s
# (fewer rows when hot), so every figure is TIME-weighted, not row-weighted. Its throttle
# columns read No even at the power ceiling, so they are not used as evidence.
function Read-CoreTempWindow([double]$Hours, $Exclude = @()) {
    if (-not (Test-Path -LiteralPath $script:CoreTempFeed)) { return $null }
    $since = [datetime]::Now.AddHours(-$Hours)
    $cpu = [System.Collections.Generic.List[double]]::new(); $c = [System.Collections.Generic.List[double]]::new()
    $w = [System.Collections.Generic.List[double]]::new(); $dt = [System.Collections.Generic.List[double]]::new()
    $inv = [Globalization.CultureInfo]::InvariantCulture; $prev = $null
    foreach ($line in (Read-SharedLines $script:CoreTempFeed)) {
        if ($line.Length -lt 20 -or $line[0] -eq 'D') { continue }
        $f = $line.Split(',')
        if ($f.Count -lt 5) { continue }
        $d = $f[0].Split('.'); $t = $f[1].Split(':')
        if ($d.Count -ne 3 -or $t.Count -lt 3) { continue }
        try { $ts = [datetime]::new([int]$d[2], [int]$d[1], [int]$d[0], [int]$t[0], [int]$t[1], [int][math]::Floor([double]::Parse($t[2], $inv)), [DateTimeKind]::Local) } catch { continue }
        if ($ts -lt $since) { $prev = $ts; continue }
        $gap = if ($prev) { [math]::Min(10.0, [math]::Max(0.0, ($ts - $prev).TotalSeconds)) } else { 2.0 }
        $prev = $ts
        if ($Exclude -and (Test-InWindows $ts.ToUniversalTime() $Exclude)) { continue }
        $vc = 0.0; $vt = 0.0; $vw = 0.0; $fl = [Globalization.NumberStyles]::Float
        if (-not ([double]::TryParse($f[2], $fl, $inv, [ref]$vc) -and [double]::TryParse($f[3], $fl, $inv, [ref]$vt) -and [double]::TryParse($f[4], $fl, $inv, [ref]$vw))) { continue }
        $cpu.Add($vc); $c.Add($vt); $w.Add($vw); $dt.Add($gap)
    }
    if ($cpu.Count -eq 0) { return [ordered]@{ rows = 0 } }
    $T = ($dt | Measure-Object -Sum).Sum
    $frac = { param($list, $pred) $s = 0.0; for ($i = 0; $i -lt $list.Count; $i++) { if (& $pred $list[$i]) { $s += $dt[$i] } }; [math]::Round($s / [math]::Max(1, $T), 4) }
    $wCeil = Get-WeightedPct $w.ToArray() $dt.ToArray() 99
    [ordered]@{
        rows              = $cpu.Count
        covered_hours     = [math]::Round($T / 3600, 1)
        feed_age_s        = [math]::Round(([datetime]::UtcNow - (Get-Item -LiteralPath $script:CoreTempFeed).LastWriteTimeUtc).TotalSeconds, 0)
        cpu_ge80_frac     = & $frac $cpu { $args[0] -ge 80 }
        cpu_pct_p95       = Get-WeightedPct $cpu.ToArray() $dt.ToArray() 95
        temp_c_p95        = Get-WeightedPct $c.ToArray() $dt.ToArray() 95
        temp_ge90_frac    = & $frac $c { $args[0] -ge 90 }
        package_w_p99     = $wCeil
        at_power_ceiling_frac = $(if ($wCeil) { & $frac $w { $args[0] -ge 0.95 * $wCeil } } else { $null })
    }
}

# HeavySlot is each machine's shared gate for heavy builds and tests. Its ledger gives queue
# wait and hold time per project. Waits are the project queueing behind the gate (its own or a
# peer's), so they are reported per project and as slot occupancy, never as CPU headroom.
function Read-HeavySlotWindow([double]$Hours) {
    if (-not (Test-Path -LiteralPath $script:HeavySlotLedger)) { return $null }
    $since = [datetime]::UtcNow.AddHours(-$Hours)
    $admits = @{}; $gates = [System.Collections.Generic.List[object]]::new(); $reaped = 0
    foreach ($line in (Read-SharedLines $script:HeavySlotLedger)) {
        if (-not $line) { continue }   # the shared read splits on newlines: the last element is empty
        try { $e = $line | ConvertFrom-Json } catch { continue }
        if ($null -eq $e -or -not $e.PSObject.Properties['at']) { continue }
        $at = ConvertTo-UtcDate $e.at
        if ($at -lt $since.AddHours(-12)) { continue }
        $ev = "$($e.event)"
        if ($ev -like 'reap*' -and $at -ge $since) { $reaped++ }
        if (-not $e.PSObject.Properties['ticket']) { continue }
        if ($ev -eq 'admit') {
            $label = if ($e.PSObject.Properties['label'] -and $e.label) { "$($e.label)" } else { 'unlabelled' }
            $admits[$e.ticket] = [pscustomobject]@{ at = $at; label = $label; cls = "$($e.class)"; waited = [double]($e.waitedMs ?? 0) }
        } elseif (($ev -eq 'exit' -or $ev -like 'reap*') -and $admits.ContainsKey($e.ticket)) {
            $a = $admits[$e.ticket]; $admits.Remove($e.ticket)
            if ($at -lt $since) { continue }
            $gates.Add([pscustomobject]@{ project = ConvertTo-ProjectSlug (($a.label -split ':')[0]); cls = $a.cls
                start = $(if ($a.at -lt $since) { $since } else { $a.at }); end = $at; waitS = $a.waited / 1000 })
        }
    }
    # admits still open: held until now, at most 3 h (HeavySlot's default max hold is 90 min, so an
    # older open admit is a holder that died without an exit row, not a live hold)
    $nowU = [datetime]::UtcNow
    foreach ($a in @($admits.Values)) {
        $s0 = if ($a.at -lt $since) { $since } else { $a.at }
        $e0 = if (($nowU - $a.at).TotalHours -gt 3) { $a.at.AddHours(3) } else { $nowU }
        if ($e0 -gt $s0) { $gates.Add([pscustomobject]@{ project = ConvertTo-ProjectSlug (($a.label -split ':')[0]); cls = $a.cls; start = $s0; end = $e0; waitS = $a.waited / 1000 }) }
    }
    # whole-machine occupancy: union of hold intervals
    $held = 0.0; $curS = $null; $curE = $null
    foreach ($g in ($gates | Sort-Object start)) {
        if ($null -eq $curS) { $curS = $g.start; $curE = $g.end; continue }
        if ($g.start -le $curE) { if ($g.end -gt $curE) { $curE = $g.end } } else { $held += ($curE - $curS).TotalSeconds; $curS = $g.start; $curE = $g.end }
    }
    if ($null -ne $curS) { $held += ($curE - $curS).TotalSeconds }
    $byProject = foreach ($grp in ($gates | Group-Object project | Sort-Object Name)) {
        [ordered]@{ project = $grp.Name; gates = $grp.Count; classes = @($grp.Group.cls | Sort-Object -Unique)
                    wait_s_p50 = Get-Pct $grp.Group.waitS 50; wait_s_p95 = Get-Pct $grp.Group.waitS 95
                    hold_s_p50 = Get-Pct ($grp.Group | ForEach-Object { ($_.end - $_.start).TotalSeconds }) 50 }
    }
    [ordered]@{ gates = $gates.Count; reaped = $reaped; occupancy_frac = [math]::Round($held / ($Hours * 3600), 4); projects = @($byProject) }
}

# ---------------------------------------------------------------- summary and verdict

function Get-HostHeadroomSummary {
    [CmdletBinding()]
    param([double]$Hours = 168, [double]$RamReservePct = 15, [string]$Root = (Get-HostHeadroomRoot))
    $hw = Get-HostHardware; $lp = $hw.logical_processors; $cores = $hw.cores
    $quiet = @(Get-QuietWindows)
    $all = @(Read-HostHeadroomSamples -Hours $Hours -Root $Root)
    $excluded = @($all | Where-Object { Test-InWindows $_.tsUtc $quiet }).Count
    $s = @($all | Where-Object { $_.busy -ge 0 -and -not (Test-InWindows $_.tsUtc $quiet) })
    $n = [math]::Max(1, $s.Count)
    $first = if ($s.Count) { ($s | Measure-Object tsUtc -Minimum).Minimum } else { $null }
    $spanH = if ($first) { [math]::Min($Hours, ([datetime]::UtcNow - $first).TotalHours) } else { 0 }
    # Coverage is measured over the span actually sampled (first sample to now, capped at the window), at
    # the sampler's real rate: 17 samples per 300 s slot (255 s at 15 s). A verdict needs >= 6 h of span,
    # so the first real verdict arrives after hours, not after most of a 7-day window has elapsed
    # (merit adjudication 2026-11-17, survivor S3 from candidate B: 24 h window with a 6 h minimum).
    $perHour = 12 * 17
    $expected = [math]::Floor([math]::Max($spanH, 0.01) * $perHour)
    $coverage = if ($s.Count) { [math]::Round([math]::Min(1, $s.Count / [math]::Max(1, $expected)), 3) } else { 0 }

    # physical-core equivalent in use: Windows fills idle physical cores before SMT siblings, so
    # busy% x logical processors, capped at the core count, approximates physical cores occupied.
    $physUsed = @($s | ForEach-Object { [math]::Min($cores, $_.busy / 100 * $lp) })
    $sat = @($s | Where-Object { $_.busy -ge 95 -or ($_.queue / [math]::Max(1, $lp)) -ge 1 -or $_.late_s -ge 10 }).Count
    $burst = @($s | Where-Object { $_.busy -ge 80 }).Count
    # "loaded" uses HeavySlot's own admission thresholds (heavy-slot.ps1 load check: CPU 85%, disk idle
    # 20%, free commit 8 GiB), so this report and the gate never disagree about what loaded means.
    $loaded = @($s | Where-Object { $_.busy -ge 85 -or ($_.disk_idle -ge 0 -and $_.disk_idle -lt 20) -or
                                    ($_.PSObject.Properties['commit_free_gb'] -and $_.commit_free_gb -ge 0 -and $_.commit_free_gb -lt 8) }).Count
    $memHit = @($s | Where-Object { $_.avail_mb -ge 0 -and ($_.avail_mb -lt 0.10 * $hw.ram_gb * 1024 -or $_.commit -ge 90 -or ($_.PSObject.Properties['commit_free_gb'] -and $_.commit_free_gb -ge 0 -and $_.commit_free_gb -lt 8)) }).Count
    $diskHit = @($s | Where-Object { $_.disk_idle -ge 0 -and $_.disk_idle -lt 10 }).Count
    $freqBusy = @($s | Where-Object { $_.busy -ge 50 -and $_.freq -ge 0 } | ForEach-Object freq)
    $freqQuiet = @($s | Where-Object { $_.busy -lt 10 -and $_.freq -ge 0 } | ForEach-Object freq)
    $avail = @($s | Where-Object { $_.avail_mb -ge 0 } | ForEach-Object { $_.avail_mb / 1024 })

    $can = @($s | Where-Object { $_.PSObject.Properties['canary'] } | ForEach-Object canary)
    $canary = [ordered]@{ runs = $can.Count }
    foreach ($k in 'single_ms', 'wide_ms', 'disk_ms') {
        $xs = @($can | ForEach-Object { $_.$k }); $p10 = Get-Pct $xs 10; $p95 = Get-Pct $xs 95
        $canary[$k -replace '_ms$', ''] = [ordered]@{ p10_ms = $p10; p50_ms = (Get-Pct $xs 50); p95_ms = $p95
            slowdown_p95 = $(if ($p10 -and $p95) { [math]::Round($p95 / $p10, 2) } else { $null }) }
    }

    $attr = @($s | Where-Object { $_.PSObject.Properties['attribution'] } | ForEach-Object attribution)
    $pnames = @($attr | ForEach-Object { $_.projects.PSObject.Properties.Name } | Sort-Object -Unique)
    $projects = foreach ($p in $pnames) {
        $c = @($attr | ForEach-Object { $q = $_.projects.PSObject.Properties[$p]; if ($q) { $q.Value.cores } else { 0.0 } })
        $r = @($attr | ForEach-Object { $q = $_.projects.PSObject.Properties[$p]; if ($q) { $q.Value.ram_gb } else { 0.0 } })
        [ordered]@{ project = $p; active_frac = [math]::Round(@($c | Where-Object { $_ -ge 0.05 }).Count / [math]::Max(1, $c.Count), 3)
                    cores_p50 = (Get-Pct $c 50); cores_p95 = (Get-Pct $c 95); cores_max = (Get-Pct $c 100); ram_gb_p95 = (Get-Pct $r 95) }
    }
    $fnames = @($attr | ForEach-Object { $_.families.PSObject.Properties.Name } | Sort-Object -Unique)
    $families = [ordered]@{}; foreach ($f in $fnames) { $families[$f] = Get-Pct @($attr | ForEach-Object { $q = $_.families.PSObject.Properties[$f]; if ($q) { $q.Value } else { 0.0 } }) 95 }
    $totCores = ($attr | Measure-Object cores_total -Sum).Sum
    $unattr = ($attr | ForEach-Object { $q = $_.projects.PSObject.Properties['_unattributed']; if ($q) { $q.Value.cores } else { 0.0 } } | Measure-Object -Sum).Sum
    $unattrFrac = if ($totCores) { [math]::Round($unattr / $totCores, 3) } else { $null }

    $slot = Read-HeavySlotWindow -Hours $Hours
    $thermal = Read-CoreTempWindow -Hours $Hours -Exclude $quiet

    $satFrac = [math]::Round($sat / $n, 4); $burstFrac = [math]::Round($burst / $n, 4); $loadedFrac = [math]::Round($loaded / $n, 4)
    $memFree = if ($avail.Count) { [math]::Round([math]::Max(0, (Get-Pct $avail 5) - $hw.ram_gb * $RamReservePct / 100), 1) } else { $null }
    $freeP50 = if ($physUsed.Count) { [math]::Round($cores - (Get-Pct $physUsed 50), 1) } else { $null }
    $freeP90 = if ($physUsed.Count) { [math]::Round($cores - (Get-Pct $physUsed 90), 1) } else { $null }
    $wideSlow = $canary.wide.slowdown_p95; $singleSlow = $canary.single.slowdown_p95

    # Verdict. Thresholds are first-cut defaults, named in the README; every reason is reported.
    $reasons = [System.Collections.Generic.List[string]]::new(); $rank = 0
    function Bump([int]$to, [string]$why) { if ($to -gt $script:rank) { $script:rank = $to }; $reasons.Add($why) }
    $script:rank = 0
    if ($s.Count -eq 0 -or $spanH -lt 6 -or $coverage -lt 0.6 -or $can.Count -lt 20) {
        $verdict = 'UNEVALUABLE'; $reasons.Add("span-hours:$([math]::Round($spanH, 1))"); $reasons.Add("coverage:$coverage"); $reasons.Add("canary-runs:$($can.Count)")
    } else {
        if ($satFrac -ge 0.10) { Bump 2 "cpu-saturated-frac:$satFrac" } elseif ($satFrac -ge 0.03) { Bump 1 "cpu-saturated-frac:$satFrac" }
        if ($burstFrac -ge 0.20) { Bump 2 "cpu-burst-frac:$burstFrac" } elseif ($burstFrac -ge 0.08) { Bump 1 "cpu-burst-frac:$burstFrac" }
        if ($loadedFrac -ge 0.25) { Bump 2 "heavyslot-loaded-frac:$loadedFrac" } elseif ($loadedFrac -ge 0.10) { Bump 1 "heavyslot-loaded-frac:$loadedFrac" }
        if ($thermal -and $thermal.rows -and $thermal.at_power_ceiling_frac -ge 0.10) { Bump 1 "power-ceiling-frac:$($thermal.at_power_ceiling_frac)" }
        if ($wideSlow -ge 2.0) { Bump 2 "canary-wide-slowdown:$wideSlow" } elseif ($wideSlow -ge 1.3) { Bump 1 "canary-wide-slowdown:$wideSlow" }
        if ($singleSlow -ge 1.6) { Bump 2 "canary-single-slowdown:$singleSlow" } elseif ($singleSlow -ge 1.2) { Bump 1 "canary-single-slowdown:$singleSlow" }
        if ($null -ne $memFree) { if ($memFree -lt 4) { Bump 2 "ram-free-gb:$memFree" } elseif ($memFree -lt 12) { Bump 1 "ram-free-gb:$memFree" } }
        if ([math]::Round($memHit / $n, 4) -ge 0.02) { Bump 1 "memory-pressure-frac:$([math]::Round($memHit / $n, 4))" }
        if ([math]::Round($diskHit / $n, 4) -ge 0.05) { Bump 1 "disk-saturated-frac:$([math]::Round($diskHit / $n, 4))" }
        if ($thermal -and $thermal.rows -and $thermal.temp_ge90_frac -ge 0.05) { Bump 1 "temp-ge90-frac:$($thermal.temp_ge90_frac)" }
        $verdict = @('ROOM', 'TIGHT', 'FULL')[$script:rank]
    }
    $slotVerdict = if (-not $slot) { 'NO-GATE' } elseif ($slot.occupancy_frac -ge 0.5) { 'FULL' } elseif ($slot.occupancy_frac -ge 0.25) { 'TIGHT' } else { 'ROOM' }

    [ordered]@{
        schema           = $script:Schema
        machine          = $env:COMPUTERNAME.ToUpperInvariant()
        window_hours     = $Hours
        span_hours       = [math]::Round($spanH, 1)
        first_sample_utc = $(if ($first) { ConvertTo-UtcStamp $first } else { $null })
        samples          = $s.Count
        excluded_quiet_window_samples = $excluded
        coverage         = $coverage
        elevated_frac    = [math]::Round(@($s | Where-Object { $_.elevated }).Count / $n, 3)
        hardware         = $hw
        cpu              = [ordered]@{
            busy_pct_p50 = (Get-Pct @($s.busy) 50); busy_pct_p95 = (Get-Pct @($s.busy) 95)
            burst_frac = $burstFrac; saturated_frac = $satFrac; heavyslot_loaded_frac = $loadedFrac
            queue_per_lp_p95 = (Get-Pct @($s | ForEach-Object { $_.queue / [math]::Max(1, $lp) }) 95)
            freq_pct_quiet_p50 = (Get-Pct $freqQuiet 50); freq_pct_busy_p10 = (Get-Pct $freqBusy 10)
            phys_cores_free_p50 = $freeP50; phys_cores_free_p90 = $freeP90
            sampler_late_p95_s = (Get-Pct @($s.late_s) 95) }
        memory           = [ordered]@{ avail_gb_p5 = (Get-Pct $avail 5); avail_gb_p50 = (Get-Pct $avail 50)
            commit_pct_p95 = (Get-Pct @($s.commit) 95); hard_faults_p95 = (Get-Pct @($s.pages_in) 95); pressure_frac = [math]::Round($memHit / $n, 4) }
        disk             = [ordered]@{ busy_pct_p95 = (Get-Pct @($s | Where-Object { $_.disk_idle -ge 0 } | ForEach-Object { 100 - $_.disk_idle }) 95)
            latency_ms_p95 = (Get-Pct @($s.disk_ms) 95); saturated_frac = [math]::Round($diskHit / $n, 4) }
        thermal          = $thermal
        canary           = $canary
        heavy_slot       = $slot
        attribution      = [ordered]@{ snapshots = $attr.Count; unattributed_frac = $unattrFrac; families_cores_p95 = $families }
        projects         = @($projects)
        headroom         = [ordered]@{
            verdict = $verdict; reasons = @($reasons); heavy_slot_verdict = $slotVerdict
            phys_cores_free_p90 = $freeP90; ram_gb_free = $memFree; ram_reserve_pct = $RamReservePct
            agents_max_rule = [int][math]::Floor($cores / 2)   # specs/machine-inventory-schema.md: agents_max <= host_cores/2
            scope = 'host CPU, memory, disk, power and the HeavySlot gate only; provider (Claude/Codex) quota is not covered' }
    }
}

# ---------------------------------------------------------------- publish (law 3: change or stale only)

# Pushes host-headroom/<MACHINE>.json when the verdict, its reason kinds, or the project set
# changed and the change held for two consecutive summaries (hysteresis), or the record is older
# than RefreshHours. Single writer: the file name is this machine's COMPUTERNAME.
function Publish-HostHeadroom {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$BusRoot, [double]$Hours = 168, [double]$RefreshHours = 24, [switch]$NoPush, [string]$Root = (Get-HostHeadroomRoot), [double]$MinConfirmGapHours = 4)
    $sum = Get-HostHeadroomSummary -Hours $Hours -Root $Root
    $shape = '{0}|{1}|{2}|{3}' -f $sum.headroom.verdict, $sum.headroom.heavy_slot_verdict,
        ((@($sum.headroom.reasons | ForEach-Object { ($_ -split ':')[0] }) | Sort-Object) -join ','),
        ((@($sum.projects | ForEach-Object { $_.project }) | Sort-Object) -join ',')
    $stateFile = Join-Path $Root 'publish-state.json'
    # Hysteresis: a shape is CONFIRMED once it has been seen continuously for MinConfirmGapHours (state
    # keeps the first time this shape was seen), so a value hovering at a threshold, or two manual runs a
    # minute apart, cannot flip the published verdict. A stale-record refresh still publishes, marked
    # headroom.confirmed = false when its shape is not yet confirmed.
    $since0 = ConvertTo-UtcStamp (Get-Date)
    if (Test-Path -LiteralPath $stateFile) {
        $st = Get-Content -LiteralPath $stateFile -Raw | ConvertFrom-Json
        if ($st.last_shape -eq $shape) { $since0 = "$(ConvertTo-UtcStamp (ConvertTo-UtcDate $st.at))" }
    }
    $confirmed = ([datetime]::UtcNow - (ConvertTo-UtcDate $since0)).TotalHours -ge $MinConfirmGapHours
    $prevShape = if ($confirmed) { $shape } else { $null }
    $sum.headroom.confirmed = $confirmed
    [IO.File]::WriteAllText($stateFile, (@{ last_shape = $shape; at = $since0 } | ConvertTo-Json -Compress))

    $sum.published_utc = ConvertTo-UtcStamp (Get-Date)
    # law 1: the tool runs from an installed copy of a reviewed commit; report THAT commit, not bus HEAD
    $from = Join-Path $PSScriptRoot 'installed-from.json'
    $sum.tool_commit = if (Test-Path -LiteralPath $from) { (Get-Content -LiteralPath $from -Raw | ConvertFrom-Json).commit } else { "uninstalled:$(git -C $BusRoot rev-parse HEAD 2>$null)" }
    # heartbeats/** is in disposition-intake.yml paths-ignore, so a record push starts no CI matrix (merit S4)
    $rel = "heartbeats/host-headroom/$($sum.machine).json"
    $path = Join-Path $BusRoot $rel
    # Pushes only from the publisher's OWN clone (made by Install-HostHeadroom.ps1, marked by a sentinel
    # file), which it resets to origin/master each try. It never touches a checkout a person or a lane uses.
    if (-not $NoPush) {
        $rootFull = [IO.Path]::GetFullPath($BusRoot).TrimEnd('\')
        $top = "$(git -C $BusRoot rev-parse --show-toplevel 2>$null)".Replace('/', '\').TrimEnd('\')
        if ($top -ine $rootFull) { throw "refusing to push from '$BusRoot': it is not its own git repository root (toplevel '$top')" }
        if (-not (Test-Path -LiteralPath (Join-Path $BusRoot '.host-headroom-publisher-clone'))) {
            throw "refusing to push from '$BusRoot': not a host-headroom publisher clone (no sentinel). Use -NoPush, or install."
        }
        git -C $BusRoot fetch --quiet origin master 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "git fetch failed in '$BusRoot' (exit $LASTEXITCODE)" }
        git -C $BusRoot reset --quiet --hard origin/master 2>&1 | Out-Null
    }
    $why = 'first-publication'
    if (Test-Path -LiteralPath $path) {
        $old = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
        $oldShape = '{0}|{1}|{2}|{3}' -f $old.headroom.verdict, $old.headroom.heavy_slot_verdict,
            ((@($old.headroom.reasons | ForEach-Object { ($_ -split ':')[0] }) | Sort-Object) -join ','),
            ((@($old.projects | ForEach-Object { $_.project }) | Sort-Object) -join ',')
        $age = ([datetime]::UtcNow - (ConvertTo-UtcDate $old.published_utc)).TotalHours
        $changed = $shape -ne $oldShape -and $shape -eq $prevShape
        if (-not $changed -and $age -lt $RefreshHours) {
            return [pscustomobject]@{ action = 'unchanged'; verdict = $sum.headroom.verdict; age_h = [math]::Round($age, 1); pending = ($shape -ne $oldShape) }
        }
        $why = if ($changed) { 'changed' } else { 'refresh' }
    }
    $json = ($sum | ConvertTo-Json -Depth 8) + "`n"
    New-Item -ItemType Directory -Path (Split-Path $path) -Force | Out-Null
    if ($NoPush) { [IO.File]::WriteAllText($path, $json, [Text.UTF8Encoding]::new($false)); return [pscustomobject]@{ action = "written-$why"; verdict = $sum.headroom.verdict; path = $rel } }
    $msg = "host-headroom: $($sum.machine) $($sum.headroom.verdict) ($why)"
    for ($try = 1; $try -le 3; $try++) {
        git -C $BusRoot fetch --quiet origin master 2>&1 | Out-Null
        git -C $BusRoot reset --quiet --hard origin/master 2>&1 | Out-Null
        New-Item -ItemType Directory -Path (Split-Path $path) -Force | Out-Null
        [IO.File]::WriteAllText($path, $json, [Text.UTF8Encoding]::new($false))
        git -C $BusRoot add -- $rel
        git -C $BusRoot diff --cached --quiet -- $rel
        if ($LASTEXITCODE -eq 0) { return [pscustomobject]@{ action = 'no-diff'; verdict = $sum.headroom.verdict } }
        $cout = git -C $BusRoot commit --quiet -m $msg -- $rel 2>&1
        if ($LASTEXITCODE -ne 0) { throw "git commit failed in publisher clone: $($cout -join ' ')" }
        if ("$(git -C $BusRoot rev-parse HEAD)" -eq "$(git -C $BusRoot rev-parse origin/master)") { throw 'commit did not advance HEAD past origin/master' }
        git -C $BusRoot push --quiet origin HEAD:master 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) { return [pscustomobject]@{ action = "pushed-$why"; verdict = $sum.headroom.verdict; commit = "$(git -C $BusRoot rev-parse --short HEAD)" } }
        Start-Sleep -Seconds (5 * $try)   # lost a race with another machine's push; the next try resets onto it
    }
    throw "host-headroom publish failed after 3 push attempts"
}

Export-ModuleMember -Function Invoke-HostHeadroomSampler, Get-HostHeadroomSummary, Publish-HostHeadroom, Get-HostHardware,
    Get-ProcessSnapshot, Get-UsageDelta, Resolve-PathProject, Resolve-Family, ConvertTo-ProjectSlug, Read-HeavySlotWindow,
    Read-CoreTempWindow, Read-HostHeadroomSamples, Read-SharedLines, Add-SharedLine, Resolve-WorktreeProject, Invoke-HostHeadroomCanary, Get-Pct, Get-WeightedPct, Get-QuietWindows, Test-InWindows, ConvertTo-UtcDate
