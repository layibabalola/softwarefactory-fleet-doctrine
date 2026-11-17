# Tests for tools/machine/host-headroom. No Pester, no elevation; writes only under a temp folder.
#   pwsh -NoProfile -File tools/machine/host-headroom/HostHeadroom.tests.ps1
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
    Assert ((Resolve-PathProject 'git -C C:\abwt\dmncsol3 status') -eq 'agent-bridge') 'abwt worktree -> agent-bridge'
    Assert ((Resolve-PathProject 'python -m pytest "C:\!Layi Wkspc\Adobe Document Cloud Ingester\tests"') -eq 'adobe-ingester') 'adobe slug'
    Assert ((Resolve-PathProject 'C:\!Layi Wkspc\MLV-App\build\x.exe') -eq 'mlv-app') 'mlv slug'
    Assert ($null -eq (Resolve-PathProject 'C:\Windows\system32\svchost.exe -k netsvcs')) 'system process has no project'
    Assert ((Resolve-Family 'MsMpEng.exe') -eq 'defender') 'defender family'
    Assert ((Resolve-Family 'claude.exe') -eq 'llm-cli') 'llm-cli family'
    Assert ((Resolve-Family 'testhost.net8.exe') -eq 'test') 'test family'
    Assert ((Resolve-Family 'notepad.exe') -eq 'other') 'other family'

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
    $hours = 2; $n = [int]($hours * 240)
    $quietRoot = Join-Path $tmp 'quiet-machine'; Write-Samples $quietRoot { 5 } $n
    $sq = Get-HostHeadroomSummary -Hours $hours -Root $quietRoot
    Assert ($sq.headroom.verdict -eq 'ROOM') "quiet machine -> ROOM ($($sq.headroom.verdict): $($sq.headroom.reasons -join ' '))"
    Assert ($sq.headroom.phys_cores_free_p90 -ge 14) "quiet machine has most cores free ($($sq.headroom.phys_cores_free_p90))"
    Assert ((@($sq.projects.project) -contains 'airmypc')) 'project footprint reported'
    Assert ($sq.attribution.unattributed_frac -eq 0.25) "unattributed share reported ($($sq.attribution.unattributed_frac))"

    $busyRoot = Join-Path $tmp 'busy-machine'; Write-Samples $busyRoot { param($i) if ($i % 3 -eq 0) { 99 } else { 20 } } $n
    $sb = Get-HostHeadroomSummary -Hours $hours -Root $busyRoot
    Assert ($sb.headroom.verdict -eq 'FULL') "a third of samples saturated -> FULL ($($sb.headroom.verdict))"

    $thinRoot = Join-Path $tmp 'thin'; Write-Samples $thinRoot { 5 } 40
    Assert ((Get-HostHeadroomSummary -Hours $hours -Root $thinRoot).headroom.verdict -eq 'UNEVALUABLE') 'low coverage -> UNEVALUABLE, never ROOM'

    @{ id = 'fq-test'; armedUtc = [datetime]::UtcNow.AddHours(-3).ToString('o'); untilUtc = [datetime]::UtcNow.AddMinutes(5).ToString('o') } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $qdir 'fq-test.json')
    $sx = Get-HostHeadroomSummary -Hours $hours -Root $busyRoot
    Assert ($sx.samples -eq 0 -and $sx.excluded_quiet_window_samples -ge $n - 1) "quiet-window samples are excluded ($($sx.excluded_quiet_window_samples))"
    Remove-Item -LiteralPath (Join-Path $qdir 'fq-test.json')

    # 7. publisher: refuses to push from a checkout that is not its own clone; -NoPush writes the record
    $fakeBus = Join-Path $tmp 'bus'; New-Item -ItemType Directory -Path $fakeBus | Out-Null
    $threw = $false; try { Publish-HostHeadroom -BusRoot $fakeBus -Hours 2 -Root $quietRoot | Out-Null } catch { $threw = $_.Exception.Message -like '*not a host-headroom publisher clone*' }
    Assert $threw 'publish refuses a non-publisher checkout'
    $res = Publish-HostHeadroom -BusRoot $fakeBus -Hours 2 -NoPush -Root $quietRoot
    Assert ($res.action -eq 'written-first-publication') "first publication written ($($res.action))"
    $rec = Get-Content -LiteralPath (Join-Path $fakeBus "host-headroom/$($env:COMPUTERNAME.ToUpperInvariant()).json") -Raw | ConvertFrom-Json
    Assert ($rec.schema -eq 'fleet-host-headroom.v1' -and $rec.machine -eq $env:COMPUTERNAME.ToUpperInvariant()) 'record schema and machine'
    Assert ($rec.published_utc -match '^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$' -or $rec.published_utc -is [datetime]) 'published_utc stamp'
    $text = Get-Content -LiteralPath (Join-Path $fakeBus "host-headroom/$($env:COMPUTERNAME.ToUpperInvariant()).json") -Raw
    Assert ($text -notmatch '(?i)[a-z]:\\\\' -and $text -notmatch [regex]::Escape($env:USERNAME)) 'law 4: no paths or user name in the record'
} finally {
    Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue
}
"`n$pass passed, $fail failed"
if ($fail) { exit 1 }
