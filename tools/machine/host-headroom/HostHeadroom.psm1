# HostHeadroom.psm1 - shared logic for tools/machine/host-headroom (see README.md beside this file).
# Pure functions first (aggregation, rollup, verdict, record validation: what the tests drive), then
# the machine readers (counters, processes, HeavySlot ledger, canary), then the bus publisher.
# Diagnostic only (metrics law 1): nothing here gates, throttles or kills anything.

$script:RecordSchema = 'fleet-host-headroom.v1'
$script:WindowSchema = 'host-headroom-window.v1'

# ---------------------------------------------------------------------------------------------
# Policy. One table, so the README, the verdict and the tests read the same numbers.
# ---------------------------------------------------------------------------------------------
function Get-HHPolicy {
    [ordered]@{
        # CPU. Busy threads = % Processor Time / 100 x logical processors. The KNEE is the physical core
        # count: past it new work shares cores through SMT and per-job throughput starts to fall. The
        # CEILING (75% of logical processors) is where queueing delay climbs steeply.
        CeilingFraction      = 0.75
        TightKneeCores       = 4        # less than this many cores to the knee at p95: TIGHT
        # Memory: keep 15% of RAM and of the commit limit in reserve.
        MemReserveFraction   = 0.15
        TightMemGB           = 12
        SaturatedCommitFrac  = 0.90
        # Canary: a fixed single-thread job run every window at Normal priority. Its time over this
        # machine's own 7-day fast baseline is the direct measure of "a new job here runs this much slower".
        TightCanaryRatio     = 1.25
        SaturatedCanaryRatio = 1.50
        # Disk: average seconds per transfer (NVMe-safe; % Disk Time is not).
        TightDiskMs          = 20
        # HeavySlot: the share of the window the machine-wide slot was held, and how long tickets waited.
        SlotBoundDuty        = 0.70
        SlotBoundWaitP90Sec  = 600
        # Data sufficiency.
        MinCoverageHours     = 6
        GapMinutes           = 15
        # Publishing: a verdict change must hold this many hourly evaluations; otherwise refresh daily.
        HoldEvaluations      = 3
        RefreshHours         = 24
        StaleHours           = 50       # reader: two missed daily refreshes plus slack
    }
}

# ---------------------------------------------------------------------------------------------
# Small statistics.
# ---------------------------------------------------------------------------------------------
function Get-HHPercentile {
    param([AllowNull()][AllowEmptyCollection()][double[]]$Values, [double]$Q)
    if ($null -eq $Values -or $Values.Count -eq 0) { return $null }
    $s = [double[]]($Values | Sort-Object)
    $i = [math]::Min($s.Count - 1, [math]::Max(0, [int][math]::Ceiling($Q * $s.Count) - 1))   # nearest rank
    return $s[$i]
}

# A CPU histogram: 1%-wide integer bins 0..100, stored sparse as { "<bin>": count }.
function ConvertTo-HHHistogram([double[]]$Values) {
    $h = [ordered]@{}
    foreach ($v in $Values) {
        $b = [string][int][math]::Min(100, [math]::Max(0, [math]::Floor($v)))
        if ($h.Contains($b)) { $h[$b]++ } else { $h[$b] = 1 }
    }
    return $h
}
function Add-HHHistogram([hashtable]$Acc, $Hist) {
    if ($null -eq $Hist) { return }
    if ($Hist -is [System.Collections.IDictionary]) { foreach ($k in $Hist.Keys) { $b = [int]$k; $Acc[$b] = [int]($Acc[$b]) + [int]$Hist[$k] } }
    else { foreach ($p in $Hist.PSObject.Properties) { $b = [int]$p.Name; $Acc[$b] = [int]($Acc[$b]) + [int]$p.Value } }
}
function Get-HHHistogramPercentile([hashtable]$Acc, [double]$Q) {
    $n = 0; foreach ($v in $Acc.Values) { $n += $v }
    if ($n -eq 0) { return $null }
    $rank = [math]::Max(1, [int][math]::Ceiling($Q * $n)); $run = 0
    foreach ($k in ($Acc.Keys | Sort-Object)) { $run += $Acc[$k]; if ($run -ge $rank) { return [double]$k + 0.5 } }
    return 100.0
}
function Get-HHHistogramCount([hashtable]$Acc, [int]$AtLeast) {
    $n = 0; foreach ($k in $Acc.Keys) { if ($k -ge $AtLeast) { $n += $Acc[$k] } }; return $n
}

# ---------------------------------------------------------------------------------------------
# One 5-minute window record from the 1-second series the sampler collected.
# ---------------------------------------------------------------------------------------------
function New-HHWindowRecord {
    param(
        [Parameter(Mandatory)][datetime]$EndUtc,
        [Parameter(Mandatory)][double[]]$CpuTime,          # % Processor Time, 1 s samples
        [double[]]$CpuUtility = @(),                       # % Processor Utility (Task Manager basis; can exceed 100)
        [double[]]$CommitGB = @(), [double[]]$AvailGB = @(),
        [double[]]$DiskMs = @(), [double[]]$DiskQueue = @(),
        [double[]]$GpuMax = @(),
        [AllowNull()]$CanaryMs = $null,
        [System.Collections.IDictionary]$Projects = @{}
    )
    $r = [ordered]@{
        schema = $script:WindowSchema
        utc    = $EndUtc.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
        secs   = $CpuTime.Count
        cpu    = [ordered]@{
            mean = [math]::Round((($CpuTime | Measure-Object -Average).Average), 2)
            p95  = Get-HHPercentile $CpuTime 0.95
            max  = [math]::Round((($CpuTime | Measure-Object -Maximum).Maximum), 2)
            hist = ConvertTo-HHHistogram $CpuTime
        }
    }
    if ($CpuUtility.Count) { $r.util = [ordered]@{ mean = [math]::Round((($CpuUtility | Measure-Object -Average).Average), 1); p95 = [math]::Round((Get-HHPercentile $CpuUtility 0.95), 1) } }
    if ($CommitGB.Count) { $r.commitMaxGB = [math]::Round((($CommitGB | Measure-Object -Maximum).Maximum), 2) }
    if ($AvailGB.Count) { $r.availMinGB = [math]::Round((($AvailGB | Measure-Object -Minimum).Minimum), 2) }
    if ($DiskMs.Count) { $r.diskMsP95 = [math]::Round((Get-HHPercentile $DiskMs 0.95), 2) }
    if ($DiskQueue.Count) { $r.diskQP95 = [math]::Round((Get-HHPercentile $DiskQueue 0.95), 2) }
    if ($GpuMax.Count) { $r.gpuMax = [math]::Round((($GpuMax | Measure-Object -Maximum).Maximum), 1) }
    if ($null -ne $CanaryMs) { $r.canaryMs = [math]::Round([double]$CanaryMs, 1) }
    $p = [ordered]@{}; foreach ($k in ($Projects.Keys | Sort-Object)) { $p[$k] = $Projects[$k] }
    $r.projects = $p
    return $r
}

# ---------------------------------------------------------------------------------------------
# HeavySlot: duty cycle (share of the window the slot was held), waits, held hours by project.
# ---------------------------------------------------------------------------------------------
function Get-HHHeavySlotStats {
    # -LiveTickets: tickets whose holder process is alive now; only those run to -ToUtc. A holder that
    # died with no exit or reap line in the ledger (measured: 11 such on one mini in 48 h) is otherwise
    # "held forever". With one slot (-SlotCount 1, HeavySlot's default) an admit also proves the previous
    # holder had released, so an open interval closes at the next admit.
    param([object[]]$Events = @(), [datetime]$FromUtc, [datetime]$ToUtc, [scriptblock]$ProjectOf = { param($l) 'other' },
        [string[]]$LiveTickets = @(), [int]$SlotCount = 1)
    $admits = @{}; $intervals = New-Object System.Collections.Generic.List[object]; $waits = New-Object System.Collections.Generic.List[double]
    $byProj = @{}; $reaped = 0; $unclosed = 0
    foreach ($e in ($Events | Sort-Object { [datetime]$_.at })) {
        $at = ([datetime]$e.at).ToUniversalTime(); $ev = [string]$e.event; $tk = [string]$e.ticket
        if ($ev -eq 'admit') {
            if ($SlotCount -eq 1 -and $admits.Count) {
                foreach ($ok in @($admits.Keys)) { $a = $admits[$ok]; $intervals.Add(@{ s = $a.at; e = $at; label = $a.label }); $admits.Remove($ok); if ($at -ge $FromUtc) { $unclosed++ } }
            }
            $admits[$tk] = @{ at = $at; label = [string]$e.label }
            if ($at -ge $FromUtc -and $at -le $ToUtc -and $null -ne $e.waitedMs) { $waits.Add([double]$e.waitedMs / 1000) }
            continue
        }
        if ($ev -eq 'reaped') { if ($at -ge $FromUtc -and $at -le $ToUtc) { $reaped++ }; if ([string]$e.kind -ne 'held') { continue } }
        elseif ($ev -notin 'exit', 'tool-exit') { continue }
        $a = $admits[$tk]
        if ($a) { $intervals.Add(@{ s = $a.at; e = $at; label = $a.label }); $admits.Remove($tk) }
    }
    foreach ($k in @($admits.Keys)) {
        $a = $admits[$k]
        if ($LiveTickets -contains $k) { $intervals.Add(@{ s = $a.at; e = $ToUtc; label = $a.label }) }   # still held
        elseif ($a.at -ge $FromUtc) { $unclosed++ }                                                        # holder gone, end unknown: not counted
    }
    $clipped = @(foreach ($iv in $intervals) {
            $s = if ($iv.s -lt $FromUtc) { $FromUtc } else { $iv.s }; $en = if ($iv.e -gt $ToUtc) { $ToUtc } else { $iv.e }
            if ($en -gt $s) { @{ s = $s; e = $en; label = $iv.label } } }) | Sort-Object { $_.s }
    $held = 0.0; $curS = $null; $curE = $null
    foreach ($iv in $clipped) {
        $proj = & $ProjectOf $iv.label
        if (-not $byProj.ContainsKey($proj)) { $byProj[$proj] = [ordered]@{ admits = 0; heldHours = 0.0 } }
        $byProj[$proj].admits++; $byProj[$proj].heldHours += ($iv.e - $iv.s).TotalHours
        if ($null -eq $curS) { $curS = $iv.s; $curE = $iv.e }
        elseif ($iv.s -le $curE) { if ($iv.e -gt $curE) { $curE = $iv.e } }
        else { $held += ($curE - $curS).TotalSeconds; $curS = $iv.s; $curE = $iv.e }
    }
    if ($null -ne $curS) { $held += ($curE - $curS).TotalSeconds }
    $span = ($ToUtc - $FromUtc).TotalSeconds
    $bp = [ordered]@{}; foreach ($k in ($byProj.Keys | Sort-Object)) { $byProj[$k].heldHours = [math]::Round($byProj[$k].heldHours, 2); $bp[$k] = $byProj[$k] }
    $wa = $waits.ToArray()
    [ordered]@{
        admits     = $wa.Count
        duty       = if ($span -gt 0) { [math]::Round($held / $span, 3) } else { $null }
        waitP50Sec = if ($wa.Count) { [math]::Round((Get-HHPercentile $wa 0.50), 1) } else { $null }
        waitP90Sec = if ($wa.Count) { [math]::Round((Get-HHPercentile $wa 0.90), 1) } else { $null }
        waitMaxSec = if ($wa.Count) { [math]::Round((($wa | Measure-Object -Maximum).Maximum), 1) } else { $null }
        reaped     = $reaped
        unclosed   = $unclosed
        byProject  = $bp
    }
}

# ---------------------------------------------------------------------------------------------
# Rollup over N hours of window records, and the verdict.
# ---------------------------------------------------------------------------------------------
function Get-HHRollup {
    param(
        [object[]]$Windows = @(),
        [Parameter(Mandatory)][datetime]$NowUtc,
        [int]$Hours = 24,
        [Parameter(Mandatory)][System.Collections.IDictionary]$Hardware,   # logical, cores, ramGB, commitLimitGB
        [AllowNull()]$HeavySlot = $null,
        [AllowNull()]$CanaryBaselineMs = $null
    )
    $pol = Get-HHPolicy
    $from = $NowUtc.AddHours(-$Hours)
    $w = @($Windows | Where-Object { $t = ([datetime]$_.utc).ToUniversalTime(); $t -gt $from -and $t -le $NowUtc.AddMinutes(10) } | Sort-Object { [datetime]$_.utc })
    $secs = 0; foreach ($x in $w) { $secs += [int]$x.secs }
    $gaps = 0; for ($i = 1; $i -lt $w.Count; $i++) { if ((([datetime]$w[$i].utc) - ([datetime]$w[$i - 1].utc)).TotalMinutes -gt $pol.GapMinutes) { $gaps++ } }
    $hist = @{}; foreach ($x in $w) { Add-HHHistogram $hist $x.cpu.hist }
    $lp = [int]$Hardware.logical; $cores = [int]$Hardware.cores
    $cpuP50 = Get-HHHistogramPercentile $hist 0.50; $cpuP95 = Get-HHHistogramPercentile $hist 0.95; $cpuP99 = Get-HHHistogramPercentile $hist 0.99
    $busyP95 = if ($null -ne $cpuP95) { [math]::Round($cpuP95 / 100 * $lp, 1) } else { $null }
    $vals = { param($name) , [double[]]@($w | ForEach-Object { $_.$name } | Where-Object { $null -ne $_ }) }
    $commit = & $vals 'commitMaxGB'; $avail = & $vals 'availMinGB'; $disk = & $vals 'diskMsP95'; $gpu = & $vals 'gpuMax'; $canary = & $vals 'canaryMs'
    $util = [double[]]@($w | ForEach-Object { if ($_.util) { $_.util.p95 } })
    $commitPeak = if ($commit.Count) { ($commit | Measure-Object -Maximum).Maximum } else { $null }
    $availMin = if ($avail.Count) { ($avail | Measure-Object -Minimum).Minimum } else { $null }
    $ram = [double]$Hardware.ramGB; $limit = [double]$Hardware.commitLimitGB
    $memHead = $null
    if ($null -ne $commitPeak -and $null -ne $availMin) {
        $byRam = ($ram * (1 - $pol.MemReserveFraction)) - ($ram - $availMin)
        $byCommit = ($limit * (1 - $pol.MemReserveFraction)) - $commitPeak
        $memHead = [math]::Round([math]::Max(0.0, [math]::Min([double]$byRam, [double]$byCommit)), 1)   # 0.0: Max(0, x) picks the int overload and rounds x
    }
    $ratios = [double[]]@(); if ($null -ne $CanaryBaselineMs -and [double]$CanaryBaselineMs -gt 0) { $ratios = [double[]]@($canary | ForEach-Object { $_ / [double]$CanaryBaselineMs }) }
    $projNames = @($w | ForEach-Object { if ($_.projects) { $_.projects.PSObject.Properties.Name } } | Sort-Object -Unique)
    $proj = [ordered]@{}
    foreach ($pn in $projNames) {
        $thr = [double[]]@($w | ForEach-Object { $x = $_.projects.$pn; if ($x) { $x.thr } else { 0.0 } })
        $gb = [double[]]@($w | ForEach-Object { $x = $_.projects.$pn; if ($x) { $x.gb } else { 0.0 } })
        $proj[$pn] = [ordered]@{
            threadsMean = [math]::Round((($thr | Measure-Object -Average).Average), 2)
            threadsP95  = [math]::Round((Get-HHPercentile $thr 0.95), 2)
            ramGBP95    = [math]::Round((Get-HHPercentile $gb 0.95), 1)
        }
    }
    [ordered]@{
        hours    = $Hours
        coverage = [ordered]@{ windows = $w.Count; sampledHours = [math]::Round($secs / 3600, 2); gaps = $gaps }
        cpu      = [ordered]@{
            timeP50 = $cpuP50; timeP95 = $cpuP95; timeP99 = $cpuP99
            utilityP95 = if ($util.Count) { [math]::Round((Get-HHPercentile $util 0.95), 1) } else { $null }
            busyThreadsP95 = $busyP95
            secondsAbove75 = Get-HHHistogramCount $hist 75
            headroomCoresToKnee = if ($null -ne $busyP95) { [math]::Round([math]::Max(0.0, [double]$cores - $busyP95), 1) } else { $null }
            headroomThreadsToCeiling = if ($null -ne $busyP95) { [math]::Round([math]::Max(0.0, [double]$lp * $pol.CeilingFraction - $busyP95), 1) } else { $null }
        }
        memory   = [ordered]@{ commitPeakGB = $commitPeak; commitP95GB = if ($commit.Count) { Get-HHPercentile $commit 0.95 } else { $null }; availMinGB = $availMin; headroomGB = $memHead }
        disk     = [ordered]@{ msPerTransferP95 = if ($disk.Count) { [math]::Round((Get-HHPercentile $disk 0.95), 2) } else { $null } }
        gpu      = [ordered]@{ maxEngineP95 = if ($gpu.Count) { [math]::Round((Get-HHPercentile $gpu 0.95), 1) } else { $null } }
        canary   = [ordered]@{
            baselineMs = if ($null -ne $CanaryBaselineMs) { [math]::Round([double]$CanaryBaselineMs, 1) } else { $null }
            ratioP50 = if ($ratios.Count) { [math]::Round((Get-HHPercentile $ratios 0.50), 2) } else { $null }
            ratioP95 = if ($ratios.Count) { [math]::Round((Get-HHPercentile $ratios 0.95), 2) } else { $null }
        }
        heavySlot = $HeavySlot
        projects  = $proj
    }
}

# The canary baseline: the 5th percentile of the canaries in the given windows (7 days by default),
# so the machine's own quiet moments define "uncontended".
function Get-HHCanaryBaseline([object[]]$Windows) {
    $c = [double[]]@($Windows | ForEach-Object { $_.canaryMs } | Where-Object { $null -ne $_ })
    if ($c.Count -lt 12) { return $null }
    return Get-HHPercentile $c 0.05
}

function Get-HHVerdict {
    param([Parameter(Mandatory)][System.Collections.IDictionary]$Rollup, [Parameter(Mandatory)][System.Collections.IDictionary]$Hardware)
    $pol = Get-HHPolicy
    $sat = New-Object System.Collections.Generic.List[string]; $tight = New-Object System.Collections.Generic.List[string]
    if ($Rollup.coverage.sampledHours -lt $pol.MinCoverageHours) { return @{ verdict = 'INSUFFICIENT-DATA'; findings = @("coverage-under-$($pol.MinCoverageHours)h") } }
    $c = $Rollup.cpu; $m = $Rollup.memory; $k = $Rollup.canary
    if ($null -ne $c.busyThreadsP95 -and $c.busyThreadsP95 -gt ([int]$Hardware.logical * $pol.CeilingFraction)) { $sat.Add('cpu-over-ceiling') }
    elseif ($null -ne $c.headroomCoresToKnee -and $c.headroomCoresToKnee -lt $pol.TightKneeCores) { $tight.Add('cpu-near-knee') }
    if ($null -ne $m.commitPeakGB -and $m.commitPeakGB -gt ([double]$Hardware.commitLimitGB * $pol.SaturatedCommitFrac)) { $sat.Add('commit-over-90pct') }
    elseif ($null -ne $m.headroomGB -and $m.headroomGB -lt $pol.TightMemGB) { $tight.Add('memory-low') }
    if ($null -ne $k.ratioP95) {
        if ($k.ratioP95 -ge $pol.SaturatedCanaryRatio) { $sat.Add('canary-slowdown') }
        elseif ($k.ratioP95 -ge $pol.TightCanaryRatio) { $tight.Add('canary-slowdown') }
    }
    if ($null -ne $Rollup.disk.msPerTransferP95 -and $Rollup.disk.msPerTransferP95 -ge $pol.TightDiskMs) { $tight.Add('disk-latency') }
    $hs = $Rollup.heavySlot
    if ($hs -and (($null -ne $hs.duty -and $hs.duty -ge $pol.SlotBoundDuty) -or ($null -ne $hs.waitP90Sec -and $hs.waitP90Sec -ge $pol.SlotBoundWaitP90Sec))) { $tight.Add('heavy-slot-bound') }
    $f = @($sat) + @($tight)
    $v = if ($sat.Count) { 'SATURATED' } elseif ($tight.Count) { 'TIGHT' } else { 'ROOM' }
    return @{ verdict = $v; findings = @($f) }
}

# Hysteresis: the published verdict moves only after HoldEvaluations hourly evaluations agree.
function Update-HHVerdictState {
    param([AllowNull()]$State, [string]$Verdict)
    $pol = Get-HHPolicy
    $prevRecent = if ($State -and $State.recent) { @($State.recent) } else { @() }
    $recent = @(@($prevRecent) + $Verdict | Where-Object { $_ } | Select-Object -Last $pol.HoldEvaluations)
    $pub = if ($State) { $State.published } else { $null }
    if (-not $pub) { $pub = $Verdict }
    elseif ($Verdict -ne $pub -and $recent.Count -ge $pol.HoldEvaluations -and @($recent | Where-Object { $_ -ne $Verdict }).Count -eq 0) { $pub = $Verdict }
    return [ordered]@{ published = $pub; recent = $recent }
}

# ---------------------------------------------------------------------------------------------
# The published record and its validator (the reader uses the same one).
# ---------------------------------------------------------------------------------------------
# Law 4 on a PUBLIC bus: project tokens travel only when they are fleet members (a specs/<name>.md
# exists); everything else folds into "other". No paths, process names, users or card ids.
function Limit-HHProjectTokens($Map, [string[]]$Members) {
    $out = [ordered]@{}
    if ($null -eq $Map) { return $out }
    $keys = if ($Map -is [System.Collections.IDictionary]) { @($Map.Keys) } else { @($Map.PSObject.Properties.Name) }
    foreach ($k in $keys) {
        $v = if ($Map -is [System.Collections.IDictionary]) { $Map[$k] } else { $Map.$k }
        $vk = if ($v -is [System.Collections.IDictionary]) { @($v.Keys) } else { @($v.PSObject.Properties.Name) }
        $lk = $k.ToLowerInvariant()
        $t = if ($lk -in 'system', 'agent-cli', 'defender') { $lk } elseif ($Members -contains $lk) { $lk } else { 'other' }
        if (-not $out.Contains($t)) { $out[$t] = [ordered]@{}; foreach ($p in $vk) { $out[$t][$p] = $v.$p } }
        else { foreach ($p in $vk) { $a = $out[$t][$p]; $b = $v.$p; if ($a -is [ValueType] -and $b -is [ValueType]) { $out[$t][$p] = [math]::Round([double]$a + [double]$b, 2) } } }
    }
    return $out
}

function New-HHRecord {
    param([string]$Machine, [datetime]$NowUtc, [string]$ToolCommit, [System.Collections.IDictionary]$Hardware,
        [System.Collections.IDictionary]$Rollup, [string]$Verdict, [string[]]$Findings, [string]$RawVerdict, [string[]]$Members = @())
    $r = [ordered]@{}; foreach ($k in $Rollup.Keys) { $r[$k] = $Rollup[$k] }
    $r.projects = Limit-HHProjectTokens $Rollup.projects $Members
    if ($r.heavySlot) { $hs = [ordered]@{}; foreach ($k in $r.heavySlot.Keys) { $hs[$k] = $r.heavySlot[$k] }; $hs.byProject = Limit-HHProjectTokens $r.heavySlot.byProject $Members; $r.heavySlot = $hs }
    [ordered]@{
        schema        = $script:RecordSchema
        machine       = $Machine
        published_utc = $NowUtc.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
        tool_commit   = $ToolCommit
        hardware      = $Hardware
        verdict       = $Verdict
        verdict_now   = $RawVerdict
        findings      = @($Findings)
        window        = $r
    }
}

function Test-HHRecord {
    param([string]$Raw, [string]$FileStem, [datetime]$NowUtc)
    try { $o = $Raw | ConvertFrom-Json -ErrorAction Stop } catch { return @{ Ok = $false; Why = 'not JSON' } }
    if ($o.schema -cne $script:RecordSchema) { return @{ Ok = $false; Why = "schema is not $script:RecordSchema" } }
    if ($FileStem -and $o.machine -cne $FileStem) { return @{ Ok = $false; Why = "machine '$($o.machine)' does not match file name '$FileStem'" } }
    $pubText = if ($o.published_utc -is [datetime]) { $o.published_utc.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ') } else { [string]$o.published_utc }
    if ($Raw -notmatch '"published_utc":\s*"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ"') { return @{ Ok = $false; Why = 'published_utc is not yyyy-MM-ddTHH:mm:ssZ' } }
    $pub = [datetime]::ParseExact($pubText, "yyyy-MM-dd'T'HH:mm:ss'Z'", [cultureinfo]::InvariantCulture, [Globalization.DateTimeStyles]'AssumeUniversal,AdjustToUniversal')
    if ($pub -gt $NowUtc.AddMinutes(10)) { return @{ Ok = $false; Why = 'published_utc is in the future' } }
    if ($o.verdict -cnotin 'ROOM', 'TIGHT', 'SATURATED', 'INSUFFICIENT-DATA') { return @{ Ok = $false; Why = "unknown verdict '$($o.verdict)'" } }
    if ($null -eq $o.findings -or $null -eq $o.window -or $null -eq $o.hardware) { return @{ Ok = $false; Why = 'missing findings, window or hardware' } }
    return @{ Ok = $true; Record = $o; PublishedUtc = $pub }
}

# ---------------------------------------------------------------------------------------------
# Project attribution by process ancestry. Rules: ordered list of @{ match = '<substring>'; project = '<token>' }.
# Config rules first (projects.json in the data dir), then every folder under each workspace root.
# ---------------------------------------------------------------------------------------------
function Get-HHProjectRules {
    param([string[]]$WorkspaceRoots = @(), [string]$ConfigPath)
    $rules = New-Object System.Collections.Generic.List[object]
    if ($ConfigPath -and (Test-Path -LiteralPath $ConfigPath)) {
        try { foreach ($r in @((Get-Content -LiteralPath $ConfigPath -Raw | ConvertFrom-Json).rules)) { if ($r.match -and $r.project) { $rules.Add(@{ match = [string]$r.match; project = [string]$r.project }) } } } catch { }
    }
    foreach ($root in $WorkspaceRoots) {
        if ($root -and (Test-Path -LiteralPath $root)) {
            foreach ($d in Get-ChildItem -LiteralPath $root -Directory -ErrorAction SilentlyContinue) { $rules.Add(@{ match = (Join-Path $root $d.Name) + '\'; project = $d.Name }) }
        }
    }
    return , $rules.ToArray()
}

function Get-HHProjectOf {
    param([string]$CommandLine, [object[]]$Rules)
    if (-not $CommandLine) { return $null }
    foreach ($r in $Rules) { if ($CommandLine.IndexOf($r.match, [StringComparison]::OrdinalIgnoreCase) -ge 0) { return $r.project } }
    return $null
}

function Get-HHProcessClass {
    param([int]$ProcId, [string]$Name, [hashtable]$ByPid, [object[]]$Rules)
    $n = $Name.ToLowerInvariant()
    if ($n -in 'msmpeng', 'mpdefendercoreservice', 'nissrv', 'mpcmdrun') { return 'defender' }
    $cur = $ProcId; $hops = 0; $seen = @{}
    while ($cur -and $hops -lt 20 -and -not $seen.ContainsKey($cur)) {
        $seen[$cur] = 1
        $p = $ByPid[[int]$cur]; if (-not $p) { break }
        $proj = Get-HHProjectOf ([string]$p.CommandLine) $Rules
        if ($proj) { return $proj }
        $cur = [int]$p.ParentProcessId; $hops++
    }
    if ($n -in 'claude', 'codex', 'node') { return 'agent-cli' }
    return 'system'
}

# Snapshot: key "pid:startTicks" -> @{ cpu = seconds; ws = bytes; cls = class; start = ticks }.
function Get-HHProcessSnapshot([object[]]$Rules) {
    $byPid = @{}; foreach ($p in Get-CimInstance Win32_Process -Property ProcessId, ParentProcessId, Name, CommandLine -ErrorAction SilentlyContinue) { $byPid[[int]$p.ProcessId] = $p }
    $snap = @{}
    foreach ($p in Get-Process) {
        try { $st = $p.StartTime.ToUniversalTime().Ticks; $cpu = $p.TotalProcessorTime.TotalSeconds } catch { continue }
        $snap["$($p.Id):$st"] = @{ cpu = $cpu; ws = $p.WorkingSet64; cls = (Get-HHProcessClass $p.Id $p.ProcessName $byPid $Rules); start = $st }
    }
    return $snap
}

# CPU per class between two snapshots, in busy threads (cpu seconds / wall seconds), plus RAM (GB).
# A process born after the first snapshot counts its whole CPU time; one that died in between is
# missed (documented limit: short-lived compilers are undercounted).
function Measure-HHProjectUse([hashtable]$Prev, [hashtable]$Cur, [double]$Seconds, [long]$PrevTakenTicks) {
    $acc = @{}
    foreach ($k in $Cur.Keys) {
        $c = $Cur[$k]
        $d = if ($Prev.ContainsKey($k)) { $c.cpu - $Prev[$k].cpu } elseif ($c.start -ge $PrevTakenTicks) { $c.cpu } else { 0 }
        if ($d -lt 0) { $d = 0 }
        if (-not $acc.ContainsKey($c.cls)) { $acc[$c.cls] = @{ cpu = 0.0; ws = 0.0 } }
        $acc[$c.cls].cpu += $d; $acc[$c.cls].ws += $c.ws
    }
    $out = [ordered]@{}
    foreach ($k in ($acc.Keys | Sort-Object)) { $out[$k] = [ordered]@{ thr = [math]::Round($acc[$k].cpu / [math]::Max(1, $Seconds), 2); gb = [math]::Round($acc[$k].ws / 1GB, 2) } }
    return $out
}

# ---------------------------------------------------------------------------------------------
# Machine readers.
# ---------------------------------------------------------------------------------------------
function Get-HHHardware {
    $cs = Get-CimInstance Win32_ComputerSystem; $os = Get-CimInstance Win32_OperatingSystem
    $cpu = @(Get-CimInstance Win32_Processor)
    [ordered]@{
        logical       = [int](($cpu | Measure-Object NumberOfLogicalProcessors -Sum).Sum)
        cores         = [int](($cpu | Measure-Object NumberOfCores -Sum).Sum)
        ramGB         = [math]::Round($cs.TotalPhysicalMemory / 1GB, 1)
        commitLimitGB = [math]::Round($os.TotalVirtualMemorySize / 1MB, 1)
    }
}

# A fixed single-thread job: SHA-256 over a fixed buffer. Median of three runs, in ms.
$script:CanaryBuf = $null
function Invoke-HHCanary {
    if ($null -eq $script:CanaryBuf) { $script:CanaryBuf = [byte[]]::new(8MB); [System.Random]::new(7).NextBytes($script:CanaryBuf) }
    $me = [System.Diagnostics.Process]::GetCurrentProcess(); $old = $me.PriorityClass
    try {
        $me.PriorityClass = 'Normal'   # the canary stands in for a new normal-priority job
        $t = foreach ($i in 1..3) { $sw = [System.Diagnostics.Stopwatch]::StartNew(); for ($j = 0; $j -lt 12; $j++) { [void][System.Security.Cryptography.SHA256]::HashData($script:CanaryBuf) }; $sw.Elapsed.TotalMilliseconds }
        return (Get-HHPercentile ([double[]]$t) 0.5)
    } finally { try { $me.PriorityClass = $old } catch { } }
}

function Read-HHHeavySlotLedger([string]$Path, [datetime]$SinceUtc) {
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    $ev = New-Object System.Collections.Generic.List[object]
    $lead = $SinceUtc.AddHours(-24)   # lead-in so admits before the window pair with exits inside it
    foreach ($line in [System.IO.File]::ReadLines($Path)) {
        if (-not $line) { continue }
        try { $e = $line | ConvertFrom-Json } catch { continue }
        if ($e.at -and ([datetime]$e.at).ToUniversalTime() -ge $lead) { $ev.Add($e) }
    }
    return , $ev.ToArray()
}

function Read-HHWindows([string]$DataDir, [datetime]$SinceUtc) {
    $out = New-Object System.Collections.Generic.List[object]
    foreach ($f in Get-ChildItem -LiteralPath $DataDir -Filter 'windows-*.jsonl' -ErrorAction SilentlyContinue | Sort-Object Name) {
        if ($f.LastWriteTimeUtc -lt $SinceUtc) { continue }
        foreach ($line in [System.IO.File]::ReadLines($f.FullName)) { if ($line) { try { $o = $line | ConvertFrom-Json; if (([datetime]$o.utc).ToUniversalTime() -ge $SinceUtc) { $out.Add($o) } } catch { } } }
    }
    return , $out.ToArray()
}

function Get-HHFleetMembers([string]$BusRoot) {
    $d = Join-Path $BusRoot 'specs'
    if (-not (Test-Path -LiteralPath $d)) { return @() }
    return @(Get-ChildItem -LiteralPath $d -Filter '*.md' -File | ForEach-Object { $_.BaseName.ToLowerInvariant() } | Where-Object { $_ -notlike 'fleet-*' })
}

# Map a HeavySlot label "<proj>:<lane>:<id>" to a project token. Only the prefix is kept.
function Get-HHLabelProject([string]$Label) {
    $p = ($Label -split ':')[0].ToLowerInvariant()
    switch ($p) { 'mlv' { 'mlv-app' } 'adobe' { 'adobe-ingester' } default { if ($p) { $p } else { 'other' } } }
}

# ---------------------------------------------------------------------------------------------
# Bus publisher. Builds the commit with plumbing on origin's tip (a private index file), so the
# checkout's working tree, index and HEAD are never touched, and pushes exactly that commit.
# Returns @{ Code = 0 published | 1 unchanged | 4 failed | 5 rehearsal; Message }.
# ---------------------------------------------------------------------------------------------
function Publish-HHRecord {
    param([Parameter(Mandatory)][string]$BusRoot, [Parameter(Mandatory)][System.Collections.IDictionary]$Record,
        [string]$Reason = 'refresh', [string]$Branch = 'master', [switch]$NoPush)
    $env:GIT_TERMINAL_PROMPT = '0'; $env:GCM_INTERACTIVE = 'never'
    $rel = "heartbeats/machines/$($Record.machine).json"
    $json = (($Record | ConvertTo-Json -Depth 8) -replace "`r`n", "`n") + "`n"
    $tmp = [System.IO.Path]::GetTempFileName(); $idx = "$tmp.idx"
    try {
        for ($attempt = 1; $attempt -le 2; $attempt++) {
            & git -C $BusRoot fetch -q origin $Branch *> $null
            if ($LASTEXITCODE -ne 0) { return @{ Code = 4; Message = "cannot fetch origin/$Branch" } }
            $tip = "$(& git -C $BusRoot rev-parse "refs/remotes/origin/$Branch" 2>$null)".Trim()
            [System.IO.File]::WriteAllText($tmp, $json, [System.Text.UTF8Encoding]::new($false))
            $blob = "$(& git -C $BusRoot hash-object -w -- $tmp 2>$null)".Trim()
            $old = "$(& git -C $BusRoot rev-parse -q --verify "${tip}:$rel" 2>$null)".Trim()
            if ($old -and $old -eq $blob) { return @{ Code = 1; Message = "unchanged on origin/$Branch" } }
            $env:GIT_INDEX_FILE = $idx
            try {
                & git -C $BusRoot read-tree $tip 2>$null; if ($LASTEXITCODE -ne 0) { return @{ Code = 4; Message = 'read-tree failed' } }
                & git -C $BusRoot update-index --add --cacheinfo "100644,$blob,$rel" 2>$null; if ($LASTEXITCODE -ne 0) { return @{ Code = 4; Message = 'update-index failed' } }
                $tree = "$(& git -C $BusRoot write-tree 2>$null)".Trim()
            } finally { Remove-Item Env:GIT_INDEX_FILE -ErrorAction SilentlyContinue }
            $msg = "host-headroom: $($Record.machine) $($Record.verdict) ($Reason)"
            $commit = "$(& git -C $BusRoot -c commit.gpgsign=false commit-tree $tree -p $tip -m $msg 2>$null)".Trim()
            if (-not $commit) { return @{ Code = 4; Message = 'commit-tree failed (git user.name/user.email set?)' } }
            $files = @(& git -C $BusRoot diff-tree --no-commit-id --name-only -r $commit 2>$null)
            if ($files.Count -ne 1 -or $files[0] -ne $rel) { return @{ Code = 4; Message = "built commit touches $($files -join ', '), not only $rel" } }
            if ($NoPush) { return @{ Code = 5; Message = "REHEARSAL: built $commit for $rel on $tip; not pushed" } }
            & git -C $BusRoot push -q --no-follow-tags origin "${commit}:refs/heads/$Branch" *> $null
            if ($LASTEXITCODE -eq 0) { return @{ Code = 0; Message = "published $rel verdict=$($Record.verdict) ($Reason) as $commit" } }
        }
        return @{ Code = 4; Message = 'push rejected twice (or no credential for a non-interactive push)' }
    } finally { Remove-Item -LiteralPath $tmp, $idx -Force -ErrorAction SilentlyContinue }
}

# ---------------------------------------------------------------------------------------------
# The whole local evaluation: read windows + ledger, roll up, judge, apply hysteresis, build the
# record. Used by the sampler (hourly) and by Get-HostHeadroom.ps1 (on demand). -UpdateState is
# passed by the hourly caller only, so an on-demand read never moves the hysteresis.
# ---------------------------------------------------------------------------------------------
function Invoke-HHEvaluation {
    param([Parameter(Mandatory)][string]$DataDir, [Parameter(Mandatory)][string]$BusRoot,
        [string]$LedgerPath = (Join-Path $env:ProgramData 'HeavySlot\ledger.jsonl'),
        [datetime]$NowUtc = [datetime]::UtcNow, [int]$Hours = 24, [switch]$UpdateState)
    $hw = Get-HHHardware
    $all = Read-HHWindows $DataDir $NowUtc.AddDays(-7)
    $base = Get-HHCanaryBaseline $all
    $ev = Read-HHHeavySlotLedger $LedgerPath $NowUtc.AddHours(-$Hours)
    $hs = $null
    if ($null -ne $ev) {
        # Live holders: held\<ticket>.json records whose pid (the ticket's middle field) is running.
        $live = @(Get-ChildItem -LiteralPath (Join-Path (Split-Path -Parent $LedgerPath) 'held') -Filter '*.json' -ErrorAction SilentlyContinue | ForEach-Object {
                $t = $_.BaseName; $hp = ($t -split '-')[1]
                if ($hp -match '^\d+$' -and (Get-Process -Id ([int]$hp) -ErrorAction SilentlyContinue)) { $t } })
        $slots = 1; if ($env:HEAVY_SLOT_COUNT -match '^\d+$') { $slots = [int]$env:HEAVY_SLOT_COUNT }
        $hs = Get-HHHeavySlotStats -Events $ev -FromUtc $NowUtc.AddHours(-$Hours) -ToUtc $NowUtc -ProjectOf { param($l) Get-HHLabelProject $l } -LiveTickets $live -SlotCount $slots
    }
    $roll = Get-HHRollup -Windows $all -NowUtc $NowUtc -Hours $Hours -Hardware $hw -HeavySlot $hs -CanaryBaselineMs $base
    $v = Get-HHVerdict -Rollup $roll -Hardware $hw
    $statePath = Join-Path $DataDir 'state.json'
    $state = $null; if (Test-Path -LiteralPath $statePath) { try { $state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json } catch { } }
    $ns = Update-HHVerdictState -State $state -Verdict $v.verdict
    $members = Get-HHFleetMembers $BusRoot
    $commit = "$(& git -C $BusRoot rev-parse HEAD 2>$null)".Trim()
    $rec = New-HHRecord -Machine $env:COMPUTERNAME -NowUtc $NowUtc -ToolCommit $commit -Hardware $hw -Rollup $roll -Verdict $ns.published -Findings $v.findings -RawVerdict $v.verdict -Members $members
    if ($UpdateState) {
        $keep = [ordered]@{ published = $ns.published; recent = $ns.recent; lastEvalUtc = $NowUtc.ToString('yyyy-MM-ddTHH:mm:ssZ') }
        if ($state) { foreach ($p in 'lastPublishUtc', 'lastPublishVerdict', 'lastPublishResult') { if ($state.PSObject.Properties[$p]) { $keep[$p] = $state.$p } } }
        [IO.File]::WriteAllText($statePath, ($keep | ConvertTo-Json -Depth 4), [Text.UTF8Encoding]::new($false))
    }
    return $rec
}

# Publish when the published verdict changed since the last publish, or the last publish is older
# than RefreshHours. Records the outcome in state.json (the status command reads it back).
function Invoke-HHPublishIfDue {
    param([Parameter(Mandatory)][string]$DataDir, [Parameter(Mandatory)][string]$BusRoot,
        [Parameter(Mandatory)][System.Collections.IDictionary]$Record, [datetime]$NowUtc = [datetime]::UtcNow, [switch]$Force, [switch]$NoPush)
    $pol = Get-HHPolicy
    $statePath = Join-Path $DataDir 'state.json'
    $state = [ordered]@{}; if (Test-Path -LiteralPath $statePath) { try { $o = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json; foreach ($p in $o.PSObject.Properties) { $state[$p.Name] = $p.Value } } catch { } }
    $reason = $null
    if ($Force) { $reason = 'manual' }
    elseif (-not $state['lastPublishUtc'] -or $state['lastPublishResult'] -notmatch '^(published|unchanged)') { $reason = 'first-or-retry' }
    elseif ($state['lastPublishVerdict'] -ne $Record.verdict) { $reason = 'verdict-changed' }
    elseif (($NowUtc - ([datetime]$state['lastPublishUtc']).ToUniversalTime()).TotalHours -ge $pol.RefreshHours) { $reason = "refresh:$($pol.RefreshHours)h" }
    if (-not $reason) { return @{ Code = 1; Message = 'not due' } }
    $r = Publish-HHRecord -BusRoot $BusRoot -Record $Record -Reason $reason -NoPush:$NoPush
    if ($r.Code -in 0, 1) { $state['lastPublishUtc'] = $NowUtc.ToString('yyyy-MM-ddTHH:mm:ssZ'); $state['lastPublishVerdict'] = $Record.verdict }
    if ($r.Code -ne 5) {
        $state['lastPublishResult'] = (@{ 0 = 'published'; 1 = 'unchanged'; 4 = 'FAILED' }[[int]$r.Code]) + ': ' + $r.Message + ' @' + $NowUtc.ToString('yyyy-MM-ddTHH:mm:ssZ')
        [IO.File]::WriteAllText($statePath, ($state | ConvertTo-Json -Depth 4), [Text.UTF8Encoding]::new($false))
    }
    return $r
}

Export-ModuleMember -Function *-HH*
