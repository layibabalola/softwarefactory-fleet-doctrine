# Tests for tools/machine/host-headroom. No Pester, no elevation; writes only under a temp folder.
#   pwsh -NoProfile -File "C:\!Layi Wkspc\softwarefactory-fleet-doctrine\tools\machine\host-headroom\HostHeadroom.tests.ps1"
$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $PSCommandPath
$pass = 0; $fail = 0
function Assert([bool]$c, [string]$name) { if ($c) { $script:pass++; "ok   $name" } else { $script:fail++; "FAIL $name" } }

# 1. every shipped script parses and is ASCII (the installer copies blobs through git show)
foreach ($f in Get-ChildItem $here -File -Include *.ps1, *.psm1, *.md -Recurse) {
    if ($f.Extension -ne '.md') { $errs = $null; [void][Management.Automation.Language.Parser]::ParseFile($f.FullName, [ref]$null, [ref]$errs); Assert (-not $errs) "parses: $($f.Name)" }
    Assert (@([IO.File]::ReadAllBytes($f.FullName) | Where-Object { $_ -gt 127 }).Count -eq 0) "ascii: $($f.Name)"
}

$mod = Import-Module (Join-Path $here 'HostHeadroom.psm1') -Force -PassThru
$tmp = Join-Path ([IO.Path]::GetTempPath()) ("host-headroom-tests-" + [guid]::NewGuid().ToString('N').Substring(0, 8))
New-Item -ItemType Directory -Path $tmp | Out-Null
try {
    # 2. project and family attribution
    Assert ((Resolve-PathProject '"C:\Program Files\PowerShell\7\pwsh.exe" -File "C:\!Layi Wkspc\agent-bridge\tools\x.ps1"') -eq 'agent-bridge') 'workspace path -> agent-bridge'
    # worktrees under X:\abwt resolve through their .git file to the repo they belong to
    $wtA = Join-Path $tmp 'abwt\wt-a'; New-Item -ItemType Directory -Path $wtA -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $wtA '.git') -Value 'gitdir: C:/!Layi Wkspc/softwarefactory-fleet-doctrine/.git/worktrees/wt-a'
    Assert ((Resolve-WorktreeProject $wtA) -eq 'fleet-doctrine') 'worktree resolves to its own repo, not a fixed project'
    Assert ((Resolve-WorktreeProject (Join-Path $tmp 'abwt\missing')) -eq 'worktree-unknown') 'unreadable worktree is unknown, never a guess'
    # a worktree anywhere (here a stand-in for C:\temp or C:\mlvtmp) resolves through its repo's .git\worktrees index
    $ws = Join-Path $tmp 'ws'; $gd = Join-Path $ws 'MLV-App\.git\worktrees\wi-x'; New-Item -ItemType Directory -Path $gd -Force | Out-Null
    $far = Join-Path $tmp 'mlvtmp\MLV-wi-x'
    Set-Content -LiteralPath (Join-Path $gd 'gitdir') -Value (($far -replace '\\', '/') + '/.git')
    & $mod { param($w) $script:WorkspaceRoots = @($w); $script:RepoSearchRoots = @($w); $script:WorktreeIndex = $null } $ws
    Assert ((Resolve-PathProject "$far\artifacts\bin\testhost.exe --port 1") -eq 'mlv-app') 'a worktree outside the workspace resolves via the repo worktree index'
    Assert ((Resolve-PathProject ("X:/elsewhere/" + (Split-Path $far -Leaf) + "/x.exe")) -ne 'mlv-app') 'the index matches the full worktree root, not a bare folder name'
    Assert ($null -eq (Resolve-PathProject (Join-Path $tmp 'mlvtmp\other-folder\x.exe'))) 'an unregistered sibling folder is not attributed'
    # a main repo outside the workspace (PC-MINI2: C:\temp\AirMyPC) is found under a search root, with its worktrees
    $sr = Join-Path $tmp 'driveTop'; $main = Join-Path $sr 'AirMyPC'; New-Item -ItemType Directory -Path (Join-Path $main '.git\worktrees\AirMyPC-wi-a') -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $main '.git\worktrees\AirMyPC-wi-a\gitdir') -Value ((Join-Path $sr 'AirMyPC-wi-a\.git') -replace '\\', '/')
    & $mod { param($w, $s) $script:WorkspaceRoots = @($w); $script:RepoSearchRoots = @($w, $s); $script:WorktreeIndex = $null } $ws $sr
    Assert ((Resolve-PathProject "$sr\AirMyPC-wi-a\artifacts\bin\testhost.exe") -eq 'airmypc') 'a worktree of a main repo outside the workspace resolves'
    Assert ((Resolve-PathProject "$main\src\App\dotnet.exe") -eq 'airmypc') 'a main repo outside the workspace resolves by its folder'
    Assert ((Resolve-PathProject "$far\x.exe") -eq 'mlv-app') 'workspace worktrees still resolve with extra search roots'
    & $mod { $script:WorkspaceRoots = @('C:\!Layi Wkspc'); $script:RepoSearchRoots = $null; $script:WorktreeIndex = $null }    Assert ((Resolve-PathProject 'python -m pytest "C:\!Layi Wkspc\Adobe Document Cloud Ingester\tests"') -eq 'adobe-ingester') 'adobe slug'
    Assert ((Resolve-PathProject 'C:\!Layi Wkspc\MLV-App\build\x.exe') -eq 'mlv-app') 'mlv slug'
    Assert ($null -eq (Resolve-PathProject 'C:\Windows\system32\svchost.exe -k netsvcs')) 'system process has no project'
    Assert ((Resolve-Family 'MsMpEng.exe') -eq 'defender') 'defender family'
    Assert ((Resolve-Family 'claude.exe') -eq 'llm-cli') 'llm-cli family'
    Assert ((Resolve-Family 'testhost.net8.exe') -eq 'test') 'test family'
    Assert ((Resolve-Family 'notepad.exe') -eq 'other') 'other family'
    # working-folder attribution (ported from candidate A): our own cwd reads back, and a bare project cwd resolves
    $null = Get-ProcessSnapshot
    Assert (([HostHeadroomNative]::GetCurrentDirectory($PID)).TrimEnd('\') -ieq [Environment]::CurrentDirectory.TrimEnd('\')) 'PEB cwd of this process reads back'
    Assert ((Resolve-PathProject 'C:\!Layi Wkspc\agent-bridge') -eq 'agent-bridge') 'a bare project cwd resolves to its project'
    # 3. percentiles
    Assert ((Get-Pct @(1..100) 95) -eq 95) 'p95 of 1..100'
    Assert ($null -eq (Get-Pct @() 50)) 'pct of empty is null'
    Assert ((Get-WeightedPct ([double[]]@(10, 90)) ([double[]]@(9, 1)) 50) -eq 10) 'weighted p50 follows the time weights'
    Assert ((Get-WeightedPct ([double[]]@(10, 90)) ([double[]]@(1, 9)) 50) -eq 90) 'weighted p50 flips with the weights'

    # 4. Core Temp feed: dd.MM.yyyy, unpadded seconds, time-weighted fractions
    $feed = Join-Path $tmp 'ct.csv'
    $now = Get-Date; $lines = @('Date,Time,Total CPU Usage [%],CPU Package [C],CPU Package Power [W],Core Thermal Throttling (avg) [Yes/No],Package/Ring Thermal Throttling [Yes/No]')
    for ($i = 60; $i -ge 1; $i--) {
        $ts = $now.AddSeconds(-2 * $i); $hot = $i -le 15
        $lines += '{0},{1}:{2}:{3}.000,{4},{5},{6},No,No' -f $ts.ToString('dd.MM.yyyy'), $ts.Hour, $ts.Minute, $ts.Second, $(if ($hot) { 100 } else { 5 }), $(if ($hot) { 92 } else { 60 }), $(if ($hot) { 74 } else { 20 })
    }
    Set-Content -LiteralPath $feed -Value $lines -Encoding utf8
    & $mod { param($f) $script:CoreTempFeed = $f } $feed
    $ct = Read-CoreTempWindow -Hours 1
    Assert ($ct.rows -eq 60) "core temp rows parsed ($($ct.rows))"
    Assert ([math]::Abs($ct.temp_ge90_frac - 0.25) -lt 0.03) "temp>=90 fraction is time-weighted ($($ct.temp_ge90_frac))"
    Assert ($ct.cpu_ge80_frac -gt 0.2) 'cpu>=80 fraction seen'

    # 5. HeavySlot ledger: occupancy is the union of hold intervals; waits per project
    $ledger = Join-Path $tmp 'ledger.jsonl'; $u = [datetime]::UtcNow
    $ev = @(
        @{ at = $u.AddMinutes(-50).ToString('o'); event = 'admit'; ticket = 't1'; label = 'airmypc:gate:x'; class = 'shared'; waitedMs = 100 }
        @{ at = $u.AddMinutes(-35).ToString('o'); event = 'exit'; ticket = 't1'; code = 0 }
        @{ at = $u.AddMinutes(-40).ToString('o'); event = 'admit'; ticket = 't2'; label = 'airmypc:gate:y'; class = 'shared'; waitedMs = 30000 }
        @{ at = $u.AddMinutes(-30).ToString('o'); event = 'exit'; ticket = 't2'; code = 0 }
        @{ at = $u.AddMinutes(-20).ToString('o'); event = 'admit'; ticket = 't3'; class = 'exclusive'; waitedMs = 5 }
        @{ at = $u.AddMinutes(-14).ToString('o'); event = 'exit'; ticket = 't3'; code = 0 }
    )
    Set-Content -LiteralPath $ledger -Value ($ev | ForEach-Object { $_ | ConvertTo-Json -Compress }) -Encoding utf8
    & $mod { param($f) $script:HeavySlotLedger = $f } $ledger
    $hs = Read-HeavySlotWindow -Hours 1
    Assert ($hs.gates -eq 3) "heavy slot gates ($($hs.gates))"
    Assert ([math]::Abs($hs.occupancy_frac - (26 / 60)) -lt 0.01) "occupancy is the union, 20+6 of 60 min ($($hs.occupancy_frac))"
    Assert ((@($hs.projects.project) -join ',') -eq 'airmypc,unlabelled') 'unlabelled admits are kept, not dropped'
    # a reaped ticket closes its gate; an open admit counts as held until now
    Add-Content -LiteralPath $ledger -Value (@{ at = $u.AddMinutes(-12).ToString('o'); event = 'admit'; ticket = 't4'; label = 'mlv:x:pytest'; class = 'shared'; waitedMs = 0 } | ConvertTo-Json -Compress)
    Add-Content -LiteralPath $ledger -Value (@{ at = $u.AddMinutes(-10).ToString('o'); event = 'reaped'; ticket = 't4' } | ConvertTo-Json -Compress)
    Add-Content -LiteralPath $ledger -Value (@{ at = $u.AddMinutes(-5).ToString('o'); event = 'admit'; ticket = 't5'; label = 'mlv:y:pytest'; class = 'shared'; waitedMs = 0 } | ConvertTo-Json -Compress)
    $hs2 = Read-HeavySlotWindow -Hours 1
    Assert ($hs2.gates -eq 5) "reaped and open gates are counted ($($hs2.gates))"
    Assert ([math]::Abs($hs2.occupancy_frac - (33 / 60)) -lt 0.01) "occupancy includes reaped (2 min) and open (5 min) holds ($($hs2.occupancy_frac))"
    Assert ($hs2.max_holders -eq 2) "max holders is the peak of exit-closed holds, t1 and t2 overlap ($($hs2.max_holders))"
    Assert ([math]::Abs($hs2.mean_holders - ((15 + 10 + 6 + 2 + 5) / 60)) -lt 0.02) "mean holders is holder-minutes over the window ($($hs2.mean_holders))"
    Assert ($hs2.wait_s_p90 -eq 30) "wait p90 over every gate in the window ($($hs2.wait_s_p90))"
    # an open admit older than HeavySlot's 90-min default max hold is a dead holder: it stops at 90 min
    $l3 = Join-Path $tmp 'ledger3.jsonl'
    Set-Content -LiteralPath $l3 -Value (@{ at = $u.AddMinutes(-170).ToString('o'); event = 'admit'; ticket = 'd1'; label = 'mlv:dead:pytest'; class = 'shared'; waitedMs = 0 } | ConvertTo-Json -Compress) -Encoding utf8
    & $mod { param($f) $script:HeavySlotLedger = $f } $l3
    $hs3 = Read-HeavySlotWindow -Hours 2
    Assert ([math]::Abs($hs3.occupancy_frac - (40 / 120)) -lt 0.01) "a dead open admit is held 90 min, so 40 of the last 120 ($($hs3.occupancy_frac))"
    # a reaped holder on a one-slot gate ends at the next admit, not at the (late) reap time
    $l4 = Join-Path $tmp 'ledger4.jsonl'
    Set-Content -LiteralPath $l4 -Encoding utf8 -Value @(
        (@{ at = $u.AddMinutes(-330).ToString('o'); event = 'admit'; ticket = 'c1'; label = 'mlv:a:pytest'; class = 'shared'; waitedMs = 0 } | ConvertTo-Json -Compress)
        (@{ at = $u.AddMinutes(-320).ToString('o'); event = 'exit'; ticket = 'c1' } | ConvertTo-Json -Compress)
        (@{ at = $u.AddMinutes(-300).ToString('o'); event = 'admit'; ticket = 'd1'; label = 'mlv:b:pytest'; class = 'shared'; waitedMs = 0 } | ConvertTo-Json -Compress)
        (@{ at = $u.AddMinutes(-290).ToString('o'); event = 'admit'; ticket = 'c2'; label = 'mlv:c:pytest'; class = 'shared'; waitedMs = 0 } | ConvertTo-Json -Compress)
        (@{ at = $u.AddMinutes(-280).ToString('o'); event = 'exit'; ticket = 'c2' } | ConvertTo-Json -Compress)
        (@{ at = $u.AddMinutes(-10).ToString('o'); event = 'reaped'; kind = 'held'; ticket = 'd1' } | ConvertTo-Json -Compress))
    & $mod { param($f) $script:HeavySlotLedger = $f } $l4
    $hs4 = Read-HeavySlotWindow -Hours 6
    Assert ([math]::Abs($hs4.occupancy_frac - (30 / 360)) -lt 0.005) "a dead holder reaped 290 min late counts 10 min, to the next admit ($($hs4.occupancy_frac))"
    Assert ($hs4.max_holders -eq 1 -and $hs4.dead_holders -eq 1) "one slot measured from exit-closed holds; one dead holder ($($hs4.max_holders), $($hs4.dead_holders))"    # the gate verdict reads the wait, not "someone holds it" (a long-held gate with no queue is not full)
    Assert ((Get-HeavySlotVerdict ([ordered]@{ gates = 40; occupancy_frac = 0.99; wait_s_p90 = 3 })) -eq 'ROOM') 'held 99% of the time with no wait is ROOM'
    Assert ((Get-HeavySlotVerdict ([ordered]@{ gates = 40; occupancy_frac = 0.2; wait_s_p90 = 776 })) -eq 'FULL') 'a 13-min p90 wait is FULL'
    Assert ((Get-HeavySlotVerdict ([ordered]@{ gates = 40; occupancy_frac = 0.2; wait_s_p90 = 150 })) -eq 'TIGHT') 'a 2.5-min p90 wait is TIGHT'
    Assert ((Get-HeavySlotVerdict ([ordered]@{ gates = 3; occupancy_frac = 0.2; wait_s_p90 = 900 })) -eq 'FEW-GATES') 'three gates cannot say'
    Assert ((Get-HeavySlotVerdict $null) -eq 'NO-GATE') 'no ledger is NO-GATE'
    # PowerShell binds [math]::Max(0, <double>) to Max(int,int): the module must not round free RAM or lateness
    Assert ([math]::Max(0, 2.54) -eq 3) 'control: the int overload rounds (why the module writes 0.0)'
    $modText = Get-Content -LiteralPath (Join-Path $here 'HostHeadroom.psm1') -Raw
    Assert (-not ($modText -match '\[math\]::Max\(0, \(')) 'no [math]::Max(0, <expression>) left in the module'
    # the same binding hits Min: coverage was 0 or 1, so the 0.6 coverage gate acted at 0.5 (PC-MINI3 read 1 at 3.3 h)
    Assert ([math]::Min(1, 0.4) -eq 0) 'control: Min(1, 0.4) binds Min(int,int) and reads 0'
    Assert (-not ($modText -match '\[math\]::(Min|Max)\(\d+, (?!\[int\])[^)]*/')) 'no [math]::Min/Max(<int literal>, <division>) left in the module'

    # readers never block the appenders (HeavySlot, Core Temp and the sampler append while we read)
    $shared = Join-Path $tmp 'shared.jsonl'; Set-Content -LiteralPath $shared -Value 'a'
    $fs = [IO.FileStream]::new($shared, 'Open', 'Read', ([IO.FileShare]::ReadWrite -bor [IO.FileShare]::Delete))
    try { Add-SharedLine $shared 'b'; $appended = $true } catch { $appended = $false } finally { $fs.Dispose() }
    Assert $appended 'append succeeds while a shared reader is open'
    Assert ((@(Read-SharedLines $shared | Where-Object { $_ }) -join ',') -eq 'a,b') 'shared reader sees the appended line'

    # 6. summary + verdict on synthetic samples (quiet machine -> ROOM; saturated -> FULL; quiet window excluded)
    $qdir = Join-Path $tmp 'quiet'; New-Item -ItemType Directory -Path $qdir | Out-Null
    & $mod { param($f) $script:QuietWindowDir = $f } $qdir
    function Write-Samples([string]$root, [scriptblock]$busy, [int]$count) {
        New-Item -ItemType Directory -Path $root -Force | Out-Null
        $rows = for ($i = $count; $i -ge 1; $i--) {
            $ts = [datetime]::UtcNow.AddSeconds(-15 * $i)
            $r = [ordered]@{ schema = 'host-headroom-sample.v1'; ts = $ts.ToString('yyyy-MM-ddTHH:mm:ssZ'); late_s = 0; lp = 32; cores = 16; elevated = $true
                busy = (& $busy $i); util = 10; freq = 90; queue = 0; avail_mb = 60000; commit = 30; commit_free_gb = 60; pages_in = 0; disk_idle = 95; disk_ms = 0.1 }
            if ($i % 20 -eq 0) { $r.canary = [ordered]@{ single_ms = 250; wide_ms = 260; wide_threads = 8; disk_ms = 30 } }
            if ($i % 4 -eq 0) { $r.attribution = [ordered]@{ seconds = 60; cores_total = 2; unreadable_cores = 0; ended = 0
                projects = [ordered]@{ 'airmypc' = [ordered]@{ cores = 1.5; ram_gb = 3 }; '_unattributed' = [ordered]@{ cores = 0.5; ram_gb = 8 } }; families = [ordered]@{ test = 1.5; other = 0.5 } } }
            $r | ConvertTo-Json -Compress -Depth 6
        }
        foreach ($g in ($rows | Group-Object { ($_ | ConvertFrom-Json).ts.ToUniversalTime().ToString('yyyyMMdd') })) {
            Add-Content -LiteralPath (Join-Path $root "samples-$($g.Name).jsonl") -Value $g.Group -Encoding utf8 }
    }
    & $mod { param($f) $script:CoreTempFeed = $f } (Join-Path $tmp 'no-core-temp.csv')   # summaries below must not see the hot fixture
    $hours = 8; $n = [int]($hours * 240)   # a verdict needs >= 6 h of sampled span
    $quietRoot = Join-Path $tmp 'quiet-machine'; Write-Samples $quietRoot { 5 } $n
    $sq = Get-HostHeadroomSummary -Hours $hours -Root $quietRoot
    Assert ($sq.headroom.verdict -eq 'ROOM') "quiet machine -> ROOM ($($sq.headroom.verdict): $($sq.headroom.reasons -join ' '))"
    Assert ($sq.headroom.phys_cores_free_p90 -ge 14) "quiet machine has most cores free ($($sq.headroom.phys_cores_free_p90))"
    Assert ((@($sq.projects.project) -contains 'airmypc')) 'project footprint reported'
    Assert ($sq.attribution.unattributed_frac -eq 0.25) "unattributed share reported ($($sq.attribution.unattributed_frac))"

    $busyRoot = Join-Path $tmp 'busy-machine'; Write-Samples $busyRoot { param($i) if ($i % 3 -eq 0) { 99 } else { 20 } } $n
    $sb = Get-HostHeadroomSummary -Hours $hours -Root $busyRoot
    Assert ($sb.headroom.verdict -eq 'FULL') "a third of samples saturated -> FULL ($($sb.headroom.verdict))"

    $thinRoot = Join-Path $tmp 'thin'; Write-Samples $thinRoot { 5 } 960   # 4 h of perfect data: span under 6 h
    Assert ((Get-HostHeadroomSummary -Hours $hours -Root $thinRoot).headroom.verdict -eq 'UNEVALUABLE') 'low coverage -> UNEVALUABLE, never ROOM'

    @{ id = 'fq-test'; armedUtc = [datetime]::UtcNow.AddHours(-9).ToString('o'); untilUtc = [datetime]::UtcNow.AddMinutes(5).ToString('o') } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $qdir 'fq-test.json')
    $sx = Get-HostHeadroomSummary -Hours $hours -Root $busyRoot
    Assert ($sx.samples -eq 0 -and $sx.excluded_quiet_window_samples -ge $n - 1) "quiet-window samples are excluded ($($sx.excluded_quiet_window_samples))"
    Remove-Item -LiteralPath (Join-Path $qdir 'fq-test.json')

    # 7. publisher: refuses to push from a checkout that is not its own clone; -NoPush writes the record
    $fakeBus = Join-Path $tmp 'bus'; New-Item -ItemType Directory -Path $fakeBus | Out-Null
    $threw = $false; try { Publish-HostHeadroom -BusRoot $fakeBus -Hours 2 -Root $quietRoot | Out-Null } catch { $threwMsg = $_.Exception.Message; $threw = $threwMsg -like '*not a host-headroom publisher clone*' -or $threwMsg -like '*not its own git repository root*' }
    Assert $threw "publish refuses a non-publisher checkout ($threwMsg)"
    # a sentinel inside a folder that is NOT its own repo root (git would walk up to a parent repo) is refused
    $parent = Join-Path $tmp 'parent-repo'; git init --quiet $parent 2>$null | Out-Null
    $inner = Join-Path $parent 'bus'; New-Item -ItemType Directory -Path $inner | Out-Null
    Set-Content -LiteralPath (Join-Path $inner '.host-headroom-publisher-clone') -Value 'x'
    $threw2 = $false; try { Publish-HostHeadroom -BusRoot $inner -Hours 2 -Root $quietRoot | Out-Null } catch { $threw2 = $_.Exception.Message -like '*not its own git repository root*' }
    Assert $threw2 'publish refuses a sentinel folder nested in another repo (no reset --hard can reach the parent)'
    $res = Publish-HostHeadroom -BusRoot $fakeBus -Hours 2 -NoPush -Root $quietRoot
    Assert (@($res).Count -eq 1 -and $res.action -eq 'written-first-publication') "first publication written ($(($res | ConvertTo-Json -Compress -Depth 2)))"
    $rec = Get-Content -LiteralPath (Join-Path $fakeBus "heartbeats/host-headroom/$($env:COMPUTERNAME.ToUpperInvariant()).json") -Raw | ConvertFrom-Json
    Assert ($rec.schema -eq 'fleet-host-headroom.v1' -and $rec.machine -eq $env:COMPUTERNAME.ToUpperInvariant()) 'record schema and machine'
    Assert ($rec.published_utc -match '^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$' -or $rec.published_utc -is [datetime]) 'published_utc stamp'
    $text = Get-Content -LiteralPath (Join-Path $fakeBus "heartbeats/host-headroom/$($env:COMPUTERNAME.ToUpperInvariant()).json") -Raw
    Assert ($text -notmatch '(?i)[a-z]:\\\\' -and $text -notmatch [regex]::Escape($env:USERNAME)) 'law 4: no paths or user name in the record'

    # 9. dashboard: renders from fixture cards (no ssh, no collection); a VM carries its host; template is ASCII
    $tpl = Get-Content -LiteralPath (Join-Path $here 'dashboard.template.html') -Raw
    Assert (@([IO.File]::ReadAllBytes((Join-Path $here 'dashboard.template.html')) | Where-Object { $_ -gt 127 }).Count -eq 0) 'ascii: dashboard.template.html (git show copies it as text)'
    Assert ($tpl.Contains('/*__DATA__*/null')) 'template has the data placeholder'
    Assert (-not $tpl.Contains("'SATURATED'")) 'template uses the sampler verdicts (FULL), not SATURATED'
    $hostsCfg = Get-Content -LiteralPath (Join-Path $here 'fleet-hosts.json') -Raw | ConvertFrom-Json
    Assert ((@($hostsCfg.hosts | Where-Object { $_.alias -eq 'virtual-ten' }).vm_on) -eq 'ULTRA-MAGNUS') 'fleet-hosts: virtual-ten is a VM on ULTRA-MAGNUS'
    $fx = Join-Path $tmp 'cards'; New-Item -ItemType Directory -Path $fx | Out-Null
    $mk = { param($m, $cores, $free) [ordered]@{ schema = 'fleet-host-card.v1'; machine = $m; collectedUtc = [datetime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
            summary = [ordered]@{ span_hours = 30; window_hours = 168; hardware = [ordered]@{ cores = $cores; ram_gb = 64; cpu_model = 'x' }
                cpu = [ordered]@{ phys_cores_free_p90 = $free; busy_pct_p95 = 40 }; headroom = [ordered]@{ verdict = 'ROOM'; reasons = @(); ram_gb_free = 40 }
                heavy_slot = [ordered]@{ occupancy_frac = 0.1; wait_s_p90 = 5 }; canary = [ordered]@{ wide = [ordered]@{ slowdown_p95 = 1.1 } }; thermal = $null }
            series = @(); tools = @('node', 'python', 'dotnet'); virtualization = [ordered]@{ role = 'none'; guests_running = @() } } }
    (& $mk 'ULTRA-MAGNUS' 24 6) | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $fx 'ULTRA-MAGNUS.card.json') -Encoding utf8
    (& $mk 'VIRTUAL-TEN' 16 12) | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $fx 'VIRTUAL-TEN.card.json') -Encoding utf8
    '{"schema":"fleet-suspended-footprint.v1","machine":"BACHELOR","measuredUtc":"2026-11-17T01:40:00Z","suspendedUtc":"2026-10-25","heavySlot":{"before":{"nonMlvSlotHoursPerDay":12}},"projects":{"Conjugal":{"sessions":3,"sessionHours":40,"needs":["dotnet","node"]}}}' |
        Set-Content -LiteralPath (Join-Path $fx 'suspended-footprint.json') -Encoding utf8
    $outDash = Join-Path $tmp 'dash'
    $msg = & (Join-Path $here 'Build-FleetDashboard.ps1') -CardsFrom $fx -OutDir $outDash
    $page = Get-Content -LiteralPath (Join-Path $outDash 'index.html') -Raw
    Assert ($msg -match '2 hosts' -and -not $page.Contains('/*__DATA__*/null')) "dashboard built from fixtures ($msg)"
    $fleet = Get-Content -LiteralPath (Join-Path $outDash 'fleet.json') -Raw | ConvertFrom-Json
    $vt = $fleet.hosts | Where-Object machine -eq 'VIRTUAL-TEN'
    Assert ($vt.vmOn -eq 'ULTRA-MAGNUS') 'the guest card carries its host (vmOn), so placements are charged to both'
    Assert ($fleet.footprint.machine -eq 'BACHELOR') 'the footprint is embedded'
    if (Get-Command node -ErrorAction SilentlyContinue) {
        $js = $page.Substring($page.IndexOf('<script>') + 8); $js = $js.Substring(0, $js.IndexOf('</script>'))
        $jsf = Join-Path $tmp 'page.js'; [IO.File]::WriteAllText($jsf, $js)
        node --check $jsf 2>&1 | Out-Null
        Assert ($LASTEXITCODE -eq 0) 'the rendered page script parses (node --check)'
        # run the planner headless: a guest with 12 free vCPUs on a host with 6 free cores is limited by the host
        $harness = Join-Path $tmp 'plan.mjs'
        $planJs = $js.Replace('render();', '').Replace("try { const t = localStorage.getItem('fleet-theme'); if (t) document.documentElement.dataset.theme = t; } catch (e) { }", '')
        [IO.File]::WriteAllText($harness, $planJs + @"

const caps = DATA.hosts.map(capacity).filter(Boolean);
const vt = caps.find((c) => c.name === 'VIRTUAL-TEN'), um = caps.find((c) => c.name === 'ULTRA-MAGNUS');
const f = fit({ needs: [], threadsHi: 8, slot: 0, ramGB: 2 }, vt, undefined, um);
console.log(JSON.stringify({ cls: f.cls, why: f.why }));
"@)
        $res = (node $harness 2>&1) -join ''
        Assert ($res -match '"cls":"bad"' -and $res -match 'the host') "a guest placement is limited by its host's free cores ($res)"
    }} finally {
    Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue
}
"`n$pass passed, $fail failed"
if ($fail) { exit 1 }
