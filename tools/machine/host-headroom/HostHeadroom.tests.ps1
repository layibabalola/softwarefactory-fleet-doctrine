# Tests for tools/machine/host-headroom. No Pester, no elevation, no network; changes nothing on the
# machine except throwaway temp folders (and a throwaway git repo + bare origin for the publisher).
#   pwsh -NoProfile -File tools/machine/host-headroom/HostHeadroom.tests.ps1
$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $PSCommandPath
$pass = 0; $fail = 0
function Assert([bool]$c, [string]$name) { if ($c) { $script:pass++; "ok   $name" } else { $script:fail++; "FAIL $name" } }

foreach ($f in Get-ChildItem $here -File -Include *.ps1, *.psm1) {
    $errs = $null; [void][Management.Automation.Language.Parser]::ParseFile($f.FullName, [ref]$null, [ref]$errs)
    Assert (-not $errs) "parses: $($f.Name)"
}
Import-Module (Join-Path $here 'HostHeadroom.psm1') -Force

# --- statistics
Assert ((Get-HHPercentile @(1, 2, 3, 4, 5, 6, 7, 8, 9, 10) 0.95) -eq 10) 'percentile: nearest rank p95 of 1..10 is 10'
Assert ((Get-HHPercentile @(1, 2, 3, 4, 5, 6, 7, 8, 9, 10) 0.5) -eq 5) 'percentile: p50 of 1..10 is 5'
Assert ($null -eq (Get-HHPercentile @() 0.5)) 'percentile: empty is null, never 0'
$h = @{}; Add-HHHistogram $h (ConvertTo-HHHistogram @(10, 10, 10, 90)); Add-HHHistogram $h ([pscustomobject]@{ '10' = 2; '50' = 1 })
Assert ((Get-HHHistogramPercentile $h 0.5) -eq 10.5) 'histogram: merged p50 from dict + JSON object'
Assert ((Get-HHHistogramPercentile $h 0.99) -eq 90.5) 'histogram: p99 lands in the top bin'
Assert ((Get-HHHistogramCount $h 75) -eq 1) 'histogram: seconds at or above 75'

# --- synthetic windows: a machine that is busy for bursts but mostly quiet
$hw = [ordered]@{ logical = 32; cores = 16; ramGB = 94; commitLimitGB = 110 }
$now = [datetime]::new(2026, 11, 17, 12, 0, 0, [DateTimeKind]::Utc)
function New-W([datetime]$t, [double[]]$cpu, [double]$canary, [double]$commit = 30, [double]$avail = 60) {
    (New-HHWindowRecord -EndUtc $t -CpuTime $cpu -CommitGB @($commit) -AvailGB @($avail) -DiskMs @(0.5) -CanaryMs $canary -Projects ([ordered]@{ 'MLV-App' = [ordered]@{ thr = 4.0; gb = 8.0 }; 'TopBuilder-X' = [ordered]@{ thr = 1.0; gb = 2.0 }; system = [ordered]@{ thr = 0.5; gb = 5.0 } })) | ConvertTo-Json -Depth 6 | ConvertFrom-Json
}
$quiet = foreach ($i in 0..143) { New-W $now.AddMinutes(-5 * $i) ([double[]](1..300 | ForEach-Object { 10 })) 40 }   # 12 h, 10% CPU
$roll = Get-HHRollup -Windows $quiet -NowUtc $now -Hours 24 -Hardware $hw -CanaryBaselineMs (Get-HHCanaryBaseline $quiet)
Assert ($roll.coverage.windows -eq 144 -and $roll.coverage.gaps -eq 0) 'rollup: 144 windows, no gaps'
Assert ([math]::Abs($roll.coverage.sampledHours - 12) -lt 0.01) 'rollup: 12 sampled hours'
Assert ($roll.cpu.busyThreadsP95 -eq 3.4) "rollup: busy threads p95 = 10.5% of 32 (got $($roll.cpu.busyThreadsP95))"
Assert ($roll.cpu.headroomCoresToKnee -eq 12.6) 'rollup: cores to the knee = 16 - 3.4'
Assert ($roll.memory.headroomGB -eq ([math]::Round([math]::Min(94 * 0.85 - (94 - 60), 110 * 0.85 - 30), 1))) 'rollup: memory headroom keeps a 15% reserve on RAM and commit'
Assert ($roll.canary.ratioP95 -eq 1) 'rollup: steady canary = ratio 1'
Assert ((Get-HHVerdict -Rollup $roll -Hardware $hw).verdict -eq 'ROOM') 'verdict: quiet machine is ROOM'

# Bursty: 20% of seconds at 95% CPU, and the canary twice as slow in a fifth of windows.
$busy = foreach ($i in 0..143) {
    $cpu = [double[]](1..300 | ForEach-Object { if ($_ % 5 -eq 0) { 95 } else { 10 } })
    New-W $now.AddMinutes(-5 * $i) $cpu $(if ($i % 5 -eq 0) { 85 } else { 40 })
}
$rb = Get-HHRollup -Windows $busy -NowUtc $now -Hours 24 -Hardware $hw -CanaryBaselineMs 40
$vb = Get-HHVerdict -Rollup $rb -Hardware $hw
Assert ($rb.cpu.secondsAbove75 -eq 144 * 60) 'rollup: bursts counted per second, not averaged away'
Assert ($vb.verdict -eq 'SATURATED' -and $vb.findings -contains 'cpu-over-ceiling' -and $vb.findings -contains 'canary-slowdown') "verdict: bursty machine is SATURATED on cpu + canary (got $($vb.verdict) $($vb.findings -join ','))"

# Low memory alone is TIGHT; commit over 90% of the limit is SATURATED.
$lowmem = foreach ($i in 0..143) { New-W $now.AddMinutes(-5 * $i) ([double[]](1..300 | ForEach-Object { 10 })) 40 80 20 }
$vl = Get-HHVerdict -Rollup (Get-HHRollup -Windows $lowmem -NowUtc $now -Hardware $hw -CanaryBaselineMs 40) -Hardware $hw
Assert ($vl.verdict -eq 'TIGHT' -and $vl.findings -contains 'memory-low') 'verdict: memory under 12 GB headroom is TIGHT'
$hicommit = foreach ($i in 0..143) { New-W $now.AddMinutes(-5 * $i) ([double[]](1..300 | ForEach-Object { 10 })) 40 100 20 }
Assert ((Get-HHVerdict -Rollup (Get-HHRollup -Windows $hicommit -NowUtc $now -Hardware $hw -CanaryBaselineMs 40) -Hardware $hw).verdict -eq 'SATURATED') 'verdict: commit over 90% is SATURATED'

# Too little data is never a verdict, and gaps are counted.
$few = @($quiet | Select-Object -First 20)
Assert ((Get-HHVerdict -Rollup (Get-HHRollup -Windows $few -NowUtc $now -Hardware $hw) -Hardware $hw).verdict -eq 'INSUFFICIENT-DATA') 'verdict: under 6 h of data is INSUFFICIENT-DATA'
$gappy = @($quiet | Where-Object { $_ -ne $quiet[10] -and $_ -ne $quiet[11] -and $_ -ne $quiet[12] })
Assert ((Get-HHRollup -Windows $gappy -NowUtc $now -Hardware $hw).coverage.gaps -eq 1) 'rollup: a 20-minute hole is one gap'

# --- HeavySlot: duty and waits, reaped holders close their interval, open holders run to now
$ev = @(
    [pscustomobject]@{ at = $now.AddHours(-10).ToString('o'); event = 'admit'; ticket = 'a'; label = 'mlv:X:pytest'; waitedMs = 1000 }
    [pscustomobject]@{ at = $now.AddHours(-8).ToString('o'); event = 'exit'; ticket = 'a' }
    [pscustomobject]@{ at = $now.AddHours(-7).ToString('o'); event = 'admit'; ticket = 'b'; label = 'agent-bridge:Y:z'; waitedMs = 1200000 }
    [pscustomobject]@{ at = $now.AddHours(-6).ToString('o'); event = 'reaped'; kind = 'held'; ticket = 'b' }
    [pscustomobject]@{ at = $now.AddHours(-5).ToString('o'); event = 'reaped'; kind = 'queue'; ticket = 'q' }
    [pscustomobject]@{ at = $now.AddHours(-1).ToString('o'); event = 'admit'; ticket = 'c'; label = 'mlv:Z:build'; waitedMs = 0 }
)
$hs = Get-HHHeavySlotStats -Events $ev -FromUtc $now.AddHours(-24) -ToUtc $now -ProjectOf { param($l) Get-HHLabelProject $l } -LiveTickets @('c')
Assert ($hs.duty -eq [math]::Round(4 / 24, 3)) "heavyslot: duty = 4 h held of 24 (got $($hs.duty))"
$dead = Get-HHHeavySlotStats -Events $ev -FromUtc $now.AddHours(-24) -ToUtc $now -ProjectOf { param($l) Get-HHLabelProject $l }
Assert ($dead.duty -eq [math]::Round(3 / 24, 3) -and $dead.unclosed -eq 1) "heavyslot: an open admit whose holder is gone is not held to now (got $($dead.duty), unclosed $($dead.unclosed))"
$ev2 = @(
    [pscustomobject]@{ at = $now.AddHours(-10).ToString('o'); event = 'admit'; ticket = 'd'; label = 'mlv:A:b'; waitedMs = 0 }
    [pscustomobject]@{ at = $now.AddHours(-9).ToString('o'); event = 'admit'; ticket = 'e'; label = 'mlv:A:b'; waitedMs = 0 }
    [pscustomobject]@{ at = $now.AddHours(-8).ToString('o'); event = 'exit'; ticket = 'e' }
)
$one = Get-HHHeavySlotStats -Events $ev2 -FromUtc $now.AddHours(-24) -ToUtc $now
Assert ($one.duty -eq [math]::Round(2 / 24, 3) -and $one.unclosed -eq 1) 'heavyslot: with one slot, the next admit closes a holder that never logged an exit'
Assert ($hs.admits -eq 3 -and $hs.reaped -eq 2 -and $hs.waitMaxSec -eq 1200) 'heavyslot: admits, reaped, max wait'
Assert ($hs.byProject['mlv-app'].heldHours -eq 3 -and $hs.byProject['agent-bridge'].heldHours -eq 1) 'heavyslot: held hours by project (label prefix mapped)'
$r2 = Get-HHRollup -Windows $quiet -NowUtc $now -Hardware $hw -HeavySlot ([ordered]@{ duty = 0.8; waitP90Sec = 30 }) -CanaryBaselineMs 40
Assert ((Get-HHVerdict -Rollup $r2 -Hardware $hw).findings -contains 'heavy-slot-bound') 'verdict: a slot held 80% of the day is heavy-slot-bound even when CPU is idle'

# --- hysteresis
$s = $null
foreach ($v in 'ROOM', 'TIGHT', 'TIGHT') { $s = Update-HHVerdictState $s $v }
Assert ($s.published -eq 'ROOM') 'hysteresis: two TIGHT after ROOM do not move the published verdict'
$s = Update-HHVerdictState $s 'TIGHT'
Assert ($s.published -eq 'TIGHT') 'hysteresis: the third agreeing evaluation moves it'
$s = Update-HHVerdictState $s 'ROOM'; $s = Update-HHVerdictState $s 'TIGHT'; $s = Update-HHVerdictState $s 'ROOM'
Assert ($s.published -eq 'TIGHT') 'hysteresis: a flapping verdict never publishes'

# --- law 4: only fleet members travel
$members = @('mlv-app', 'agent-bridge')
$rec = New-HHRecord -Machine 'PC-TEST' -NowUtc $now -ToolCommit 'abc' -Hardware $hw -Rollup $roll -Verdict 'ROOM' -Findings @() -RawVerdict 'ROOM' -Members $members
Assert (@($rec.window.projects.Keys) -contains 'mlv-app' -and @($rec.window.projects.Keys) -contains 'other' -and -not (@($rec.window.projects.Keys) -match 'topbuilder')) 'law 4: non-member project folds into "other"'
$json = $rec | ConvertTo-Json -Depth 8
Assert ($json -notmatch '(?i)topbuilder|\\\\|C:\\|Users') 'law 4: no non-member name, path or user in the record'

# --- validator (the reader's)
$t = Test-HHRecord -Raw $json -FileStem 'PC-TEST' -NowUtc $now
Assert $t.Ok 'validator: a built record validates'
Assert (-not (Test-HHRecord -Raw $json -FileStem 'PC-OTHER' -NowUtc $now).Ok) 'validator: machine must equal file name'
Assert (-not (Test-HHRecord -Raw ($json -replace '"ROOM"', '"GREAT"') -FileStem 'PC-TEST' -NowUtc $now).Ok) 'validator: unknown verdict refused'
Assert (-not (Test-HHRecord -Raw $json -FileStem 'PC-TEST' -NowUtc $now.AddHours(-1)).Ok) 'validator: future stamp refused'
Assert (-not (Test-HHRecord -Raw '{"schema":"x"}' -FileStem 'PC-TEST' -NowUtc $now).Ok) 'validator: wrong schema refused'

# --- attribution
$rules = @(@{ match = 'C:\mlvtmp\'; project = 'MLV-App' }, @{ match = 'C:\W\agent-bridge\'; project = 'agent-bridge' })
$byPid = @{
    10 = [pscustomobject]@{ ProcessId = 10; ParentProcessId = 0; CommandLine = 'pwsh -File C:\W\agent-bridge\x.ps1' }
    11 = [pscustomobject]@{ ProcessId = 11; ParentProcessId = 10; CommandLine = 'python -m pytest' }
    12 = [pscustomobject]@{ ProcessId = 12; ParentProcessId = 13; CommandLine = 'cc1plus' }
    13 = [pscustomobject]@{ ProcessId = 13; ParentProcessId = 12; CommandLine = 'make' }   # a parent cycle
}
Assert ((Get-HHProcessClass 11 'python' $byPid $rules) -eq 'agent-bridge') 'attribution: child inherits the ancestor project'
Assert ((Get-HHProcessClass 12 'cc1plus' $byPid $rules) -eq 'system') 'attribution: a parent-pid cycle terminates'
Assert ((Get-HHProcessClass 99 'MsMpEng' $byPid $rules) -eq 'defender') 'attribution: Defender is its own class'
$prev = @{ 'a:1' = @{ cpu = 10.0; ws = 1GB; cls = 'x'; start = 1 } }
$cur = @{ 'a:1' = @{ cpu = 40.0; ws = 1GB; cls = 'x'; start = 1 }; 'b:900' = @{ cpu = 30.0; ws = 1GB; cls = 'x'; start = 900 }; 'c:5' = @{ cpu = 99.0; ws = 1GB; cls = 'y'; start = 5 } }
$u = Measure-HHProjectUse $prev $cur 300 500
Assert ($u['x'].thr -eq 0.2 -and $u['x'].gb -eq 2) 'attribution: delta + newborn CPU / 300 s = 0.2 threads'
Assert ($u['y'].thr -eq 0) 'attribution: a process older than the last snapshot but unseen counts no CPU'

# --- publisher, on a throwaway repo with a throwaway bare origin
$tmp = Join-Path ([IO.Path]::GetTempPath()) ("hh-test-" + [guid]::NewGuid().ToString('n').Substring(0, 8))
try {
    $origin = Join-Path $tmp 'origin.git'; $clone = Join-Path $tmp 'clone'
    & git init -q --bare -b master $origin
    & git clone -q $origin $clone 2>$null
    & git -C $clone config user.name t; & git -C $clone config user.email t@t
    Set-Content (Join-Path $clone 'README.md') 'x'; & git -C $clone add README.md; & git -C $clone commit -q -m init; & git -C $clone push -q origin master 2>$null
    Set-Content (Join-Path $clone 'dirty.txt') 'local work'   # the publisher must never touch the working tree
    $p1 = Publish-HHRecord -BusRoot $clone -Record $rec -Reason 'test'
    Assert ($p1.Code -eq 0) "publisher: first publish pushes ($($p1.Message))"
    $files = @(& git -C $origin ls-tree -r --name-only master)
    Assert ($files -contains 'heartbeats/machines/PC-TEST.json' -and $files.Count -eq 2) 'publisher: origin holds exactly README + the record'
    Assert ((Test-Path (Join-Path $clone 'dirty.txt')) -and -not (Test-Path (Join-Path $clone 'heartbeats'))) 'publisher: working tree untouched'
    Assert ((Publish-HHRecord -BusRoot $clone -Record $rec).Code -eq 1) 'publisher: identical record is unchanged, no commit'
    $p3 = Publish-HHRecord -BusRoot $clone -Record $rec -NoPush
    Assert ($p3.Code -eq 1) 'publisher: rehearsal of an unchanged record reports unchanged'
    $raw = (& git -C $origin show master:heartbeats/machines/PC-TEST.json) -join "`n"
    Assert ((Test-HHRecord -Raw $raw -FileStem 'PC-TEST' -NowUtc $now).Ok) 'publisher: the published bytes pass the reader validator'
} finally { Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue }

"`n$pass passed, $fail failed"
if ($fail) { exit 1 }
