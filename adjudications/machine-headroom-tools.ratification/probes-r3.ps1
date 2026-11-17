# Merit probes for the machine-headroom adjudication. Read-only on the machine: every world is built in a
# temp dir; live probes only READ task definitions, process tables and data-file timestamps.
#   pwsh -NoProfile -File probes.ps1 -Prop <id> -Cand <A|B|C>
param([Parameter(Mandatory)][string]$Prop, [Parameter(Mandatory)][ValidateSet('A','B','C')][string]$Cand)
$ErrorActionPreference = 'Stop'
$M  = $PSScriptRoot
$SA = Join-Path $M 'srcA\tools\machine\machine-load'
$SB = Join-Path $M 'srcB\tools\machine\host-headroom'
$SC = Join-Path $M 'srcC\tools\machine\host-headroom'
$Py = (Get-Command python -CommandType Application | Where-Object Source -notmatch 'WindowsApps' | Select-Object -First 1).Source   # RATIFIER: resolved per host
$OwnerClone = 'C:\!Layi Wkspc\softwarefactory-fleet-doctrine'
$Hosts = @('pc-mini1', 'pc-mini2', 'pc-mini3' | Where-Object { $_ -ne $env:COMPUTERNAME.ToLowerInvariant() })   # RATIFIER: the other two minis, whichever host runs this
$tmp = Join-Path ([IO.Path]::GetTempPath()) ("merit-{0}-{1}-{2}" -f $Prop, $Cand, [guid]::NewGuid().ToString('N').Substring(0, 6))
New-Item -ItemType Directory -Path $tmp | Out-Null
function PyA([string]$p, [string[]]$extra = @()) { & $Py -I (Join-Path $M 'probe_a_r3.py') $p $SA @extra 2>&1; exit $LASTEXITCODE }
function ModB { Import-Module (Join-Path $SB 'HostHeadroom.psm1') -Force -PassThru }
function ModC { Import-Module (Join-Path $SC 'HostHeadroom.psm1') -Force -PassThru }
function OnAll([string]$script) {   # run a read-only snippet here and on the other minis
    $enc = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($script))
    $out = @(); $out += (pwsh -NoProfile -EncodedCommand $enc 2>$null)
    foreach ($h in $Hosts) { $out += (ssh -n -o BatchMode=yes -o ConnectTimeout=15 $h "pwsh -NoProfile -EncodedCommand $enc" 2>$null) }
    $out | Where-Object { $_ -and $_ -notmatch 'CLIXML|<Objs' }
}
# ---- B fixtures (as in B's own tests) ----
$hwB = [ordered]@{ logical = 32; cores = 16; ramGB = 94; commitLimitGB = 110 }
$nowB = [datetime]::UtcNow
function New-WB([datetime]$t, [double]$canary) {
    (New-HHWindowRecord -EndUtc $t -CpuTime ([double[]](1..300 | ForEach-Object { 10 })) -CommitGB @(30) -AvailGB @(60) -DiskMs @(0.5) -CanaryMs $canary -Projects ([ordered]@{ system = [ordered]@{ thr = 0.5; gb = 5.0 } })) | ConvertTo-Json -Depth 6 | ConvertFrom-Json
}
# ---- C fixtures (as in C's own tests) ----
function Write-SamplesC([string]$root, [int]$count, [scriptblock]$single) {
    New-Item -ItemType Directory -Path $root -Force | Out-Null
    $rows = for ($i = $count; $i -ge 1; $i--) {
        $ts = [datetime]::UtcNow.AddSeconds(-15 * $i)
        $r = [ordered]@{ schema = 'host-headroom-sample.v1'; ts = $ts.ToString('yyyy-MM-ddTHH:mm:ssZ'); late_s = 0; lp = 32; cores = 16; elevated = $true
            busy = 5; util = 10; freq = 90; queue = 0; avail_mb = 60000; commit = 30; commit_free_gb = 60; pages_in = 0; disk_idle = 95; disk_ms = 0.1 }
        if ($i % 20 -eq 0) { $s = & $single $i; $r.canary = [ordered]@{ single_ms = $s; wide_ms = $s; wide_threads = 8; disk_ms = 30 } }
        $r | ConvertTo-Json -Compress -Depth 6
    }
    foreach ($g in ($rows | Group-Object { ($_ | ConvertFrom-Json).ts.ToUniversalTime().ToString('yyyyMMdd') })) { Add-Content -LiteralPath (Join-Path $root "samples-$($g.Name).jsonl") -Value $g.Group -Encoding utf8 }
}
function CIsolate($mod) { & $mod { param($t) $script:CoreTempFeed = Join-Path $t 'no-ct.csv'; $script:HeavySlotLedger = Join-Path $t 'no-ledger.jsonl'; $script:QuietWindowDir = Join-Path $t 'no-quiet' } $tmp }

try {
switch ($Prop) {

'quiet' {   # a REAL FleetQuiet window record (copied from this machine) covering now must exclude the sample
    $real = Get-ChildItem 'C:\ProgramData\FleetQuiet\windows' -File | Select-Object -First 1
    if (-not $real) { 'PRECONDITION-MISSING: no FleetQuiet window record on this machine'; exit 3 }
    $w = Get-Content -Raw $real.FullName | ConvertFrom-Json
    $fields = ($w.PSObject.Properties.Name) -join ','
    $w.armedUtc = [datetime]::UtcNow.AddHours(-1).ToString('o'); $w.untilUtc = [datetime]::UtcNow.AddHours(1).ToString('o')
    $qd = Join-Path $tmp 'windows'; New-Item -ItemType Directory $qd | Out-Null
    $w | ConvertTo-Json -Depth 8 | Set-Content (Join-Path $qd 'fq-probe.json')
    "real record fields: $fields"
    switch ($Cand) {
        'A' {
            $ast = [Management.Automation.Language.Parser]::ParseFile((Join-Path $SA 'MachineLoadSampler.ps1'), [ref]$null, [ref]$null)
            # RATIFIER FIX: since 3ab60358 Test-QuietWindow calls ConvertTo-UtcTime; extract both, as A's own tests do (Install-MachineLoad.tests.ps1:112)
            foreach ($fn in $ast.FindAll({ $args[0] -is [Management.Automation.Language.FunctionDefinitionAst] -and $args[0].Name -in 'Test-QuietWindow', 'ConvertTo-UtcTime' }, $true)) { . ([scriptblock]::Create($fn.Extent.Text)) }; $QuietDir = $qd
            "REAL_FORMAT_EXCLUDED=$(Test-QuietWindow ([datetime]::UtcNow))"
            $c = Join-Path $tmp 'ctl'; New-Item -ItemType Directory $c | Out-Null
            @{ startUtc = [datetime]::UtcNow.AddHours(-24).ToString('o'); endUtc = [datetime]::UtcNow.AddHours(24).ToString('o') } | ConvertTo-Json | Set-Content (Join-Path $c 'x.json')
            $QuietDir = $c; "CONTROL (fields startUtc/endUtc +-24 h, which FleetQuiet never writes) excluded=$(Test-QuietWindow ([datetime]::UtcNow))"
            @{ startUtc = [datetime]::UtcNow.AddHours(-1).ToString('o'); endUtc = [datetime]::UtcNow.AddHours(1).ToString('o') } | ConvertTo-Json | Set-Content (Join-Path $c 'x.json')
            "CONTROL (startUtc/endUtc +-1 h) excluded=$(Test-QuietWindow ([datetime]::UtcNow))"
        }
        'B' { $hits = @(Select-String -Path (Join-Path $SB '*') -Pattern 'FleetQuiet|armedUtc|quiet window' -List); "REAL_FORMAT_EXCLUDED=$([bool]$hits.Count) (B has no quiet-window reader: $($hits.Count) files reference FleetQuiet)" }
        'C' {
            $m = ModC; & $m { param($d) $script:QuietWindowDir = $d } $qd
            Copy-Item $real.FullName (Join-Path $qd $real.Name)   # a released historical window, verbatim
            $win = & $m { Get-QuietWindows }
            "REAL_FORMAT_EXCLUDED=$(& $m { param($ws) Test-InWindows ([datetime]::UtcNow) $ws } $win)"
            $mid = ([datetimeoffset]::Parse((Get-Content -Raw $real.FullName | ConvertFrom-Json).armedUtc)).UtcDateTime.AddMinutes(5)
            "RELEASED_HISTORY_EXCLUDED=$(& $m { param($ws, $t) Test-InWindows $t $ws } $win $mid)"
        }
    }
}

'lock' {   # a reader running while HeavySlot appends (HeavySlot's exact open: AppendData, FileShare ReadWrite|Delete)
    $led = Join-Path $tmp 'ledger.jsonl'
    $line = '{"at":"' + [datetime]::UtcNow.ToString('o') + '","event":"admit","ticket":"t-1","label":"airmypc:gate:x","class":"shared","recovered":false,"admission":"clean","waitedMs":79}'
    [IO.File]::WriteAllLines($led, [string[]](1..20000 | ForEach-Object { $line }))
    function Try-Append { try { $fs = [IO.FileSystemAclExtensions]::Create([IO.FileInfo]::new($led), [IO.FileMode]::OpenOrCreate, [Security.AccessControl.FileSystemRights]::AppendData, [IO.FileShare]'ReadWrite, Delete', 4096, [IO.FileOptions]::None, $null); $b = [Text.Encoding]::UTF8.GetBytes("$line`n"); $fs.Write($b, 0, $b.Length); $fs.Dispose(); $true } catch { $false } }
    # negative control: a FileShare.Read holder MUST make the append fail, or this probe cannot detect a lock
    $h = [IO.FileStream]::new($led, 'Open', 'Read', 'Read'); $ctl = Try-Append; $h.Dispose()
    if ($ctl) { 'PROBE-INVALID: the negative control did not block the append'; exit 3 }
    $reader = switch ($Cand) {
        'A' { @{ exe = $Py; args = @('-I', (Join-Path $M 'probe_a_r3.py'), 'lockreader', $SA, $led) } }
        'B' { @{ exe = 'pwsh'; args = @('-NoProfile', '-Command', "Import-Module '$SB\HostHeadroom.psm1'; `$n=0; `$t=[datetime]::UtcNow; while(([datetime]::UtcNow-`$t).TotalSeconds -lt 10){ `$null = Read-HHHeavySlotLedger '$led' ([datetime]::UtcNow.AddDays(-2)); `$n++ }; 'ITER ' + `$n") } }
        'C' { @{ exe = 'pwsh'; args = @('-NoProfile', '-Command', "`$m = Import-Module '$SC\HostHeadroom.psm1' -PassThru; & `$m { param(`$f) `$script:HeavySlotLedger = `$f } '$led'; `$n=0; `$t=[datetime]::UtcNow; while(([datetime]::UtcNow-`$t).TotalSeconds -lt 10){ `$null = Read-HeavySlotWindow -Hours 48; `$n++ }; 'ITER ' + `$n") } }
    }
    $so = Join-Path $tmp 'reader.out'
    $p = Start-Process -FilePath $reader.exe -ArgumentList $reader.args -NoNewWindow -PassThru -RedirectStandardOutput $so -RedirectStandardError (Join-Path $tmp 'reader.err')
    $fail = 0; $att = 0
    while (-not $p.HasExited) { $att++; if (-not (Try-Append)) { $fail++ }; Start-Sleep -Milliseconds 5 }
    $iter = (Get-Content $so -Raw) -replace '\s+', ' '
    if ($iter -notmatch 'ITER [1-9]') { "PRECONDITION-MISSING: reader did not complete an iteration ($iter)"; exit 3 }
    "control: FileShare.Read holder blocked the append (detector works)"
    "APPEND_FAILURES=$fail ATTEMPTS=$att READER=$iter"
}

'failclosed' {
    switch ($Cand) {
        'A' { PyA 'failclosed' }
        'B' { $null = ModB
              $few = @(foreach ($i in 0..19) { New-WB $nowB.AddMinutes(-5 * $i) 40 })
              $v1 = (Get-HHVerdict -Rollup (Get-HHRollup -Windows $few -NowUtc $nowB -Hours 24 -Hardware $hwB -CanaryBaselineMs 40) -Hardware $hwB).verdict
              $v0 = (Get-HHVerdict -Rollup (Get-HHRollup -Windows @() -NowUtc $nowB -Hours 24 -Hardware $hwB) -Hardware $hwB).verdict
              "VERDICT 100min-of-perfect-data=$v1 no-data=$v0" }
        'C' { $m = ModC; CIsolate $m
              $thin = Join-Path $tmp 'thin'; Write-SamplesC $thin 40 { 250 }; $empty = Join-Path $tmp 'empty'; New-Item -ItemType Directory $empty | Out-Null
              "VERDICT 10min-of-perfect-data=$((Get-HostHeadroomSummary -Hours 2 -Root $thin).headroom.verdict) no-data=$((Get-HostHeadroomSummary -Hours 2 -Root $empty).headroom.verdict)" }
    }
}

'timeverdict' {   # 12 h of perfect, quiet data after install: does the CENTRAL (published) verdict exist yet?
    switch ($Cand) {
        'A' { PyA 'timeverdict' }
        'B' { $null = ModB; $w = @(foreach ($i in 0..143) { New-WB $nowB.AddMinutes(-5 * $i) 40 })
              "VERDICT_AFTER_12H=$((Get-HHVerdict -Rollup (Get-HHRollup -Windows $w -NowUtc $nowB -Hours 24 -Hardware $hwB -CanaryBaselineMs 40) -Hardware $hwB).verdict) (published window 24 h)" }
        'C' { $m = ModC; CIsolate $m; $r = Join-Path $tmp 's'; Write-SamplesC $r 2880 { 250 }
              "VERDICT_AFTER_12H=$((Get-HostHeadroomSummary -Hours 168 -Root $r).headroom.verdict) (published window: Run-HostHeadroom -Hours default 168)" }
    }
}

'thru' {   # same utilisation; only the measured slowdown of a running job differs -> the verdict must differ
    switch ($Cand) {
        'A' { PyA 'thru' }
        'B' { $null = ModB
              $flat = @(foreach ($i in 0..143) { New-WB $nowB.AddMinutes(-5 * $i) 40 })
              $slow = @(foreach ($i in 0..143) { New-WB $nowB.AddMinutes(-5 * $i) $(if ($i % 2) { 40 } else { 54 }) })
              $vf = (Get-HHVerdict -Rollup (Get-HHRollup -Windows $flat -NowUtc $nowB -Hours 24 -Hardware $hwB -CanaryBaselineMs (Get-HHCanaryBaseline $flat)) -Hardware $hwB).verdict
              $vs = Get-HHVerdict -Rollup (Get-HHRollup -Windows $slow -NowUtc $nowB -Hours 24 -Hardware $hwB -CanaryBaselineMs (Get-HHCanaryBaseline $slow)) -Hardware $hwB
              "VERDICT_FLAT=$vf VERDICT_SLOW=$($vs.verdict) findings=$($vs.findings -join ',')" }
        'C' { $m = ModC; CIsolate $m
              # RATIFIER FIX: 8 h of samples; C requires >= 6 h of sampled span since b18b38f8 (ported from B)
              $f = Join-Path $tmp 'flat'; Write-SamplesC $f 1920 { 250 }; $s = Join-Path $tmp 'slow'; Write-SamplesC $s 1920 { param($i) if (($i / 20) % 2) { 250 } else { 340 } }
              $sf = Get-HostHeadroomSummary -Hours 8 -Root $f; $ss = Get-HostHeadroomSummary -Hours 8 -Root $s
              "VERDICT_FLAT=$($sf.headroom.verdict) VERDICT_SLOW=$($ss.headroom.verdict) reasons=$($ss.headroom.reasons -join ',')" }
    }
}

'gate' {   # idle CPU, but the HeavySlot gate held 70 % of the time with 20-minute waits
    switch ($Cand) {
        'A' { PyA 'gate' }
        'B' { $null = ModB
              $ev = foreach ($k in 0..23) { $a = $nowB.AddHours(-24).AddMinutes(30 + 60 * $k)
                  [pscustomobject]@{ at = $a.ToString('o'); event = 'admit'; ticket = "t$k"; label = 'airmypc:gate:x'; waitedMs = 1200000 }
                  [pscustomobject]@{ at = $a.AddMinutes(42).ToString('o'); event = 'exit'; ticket = "t$k" } }
              $hs = Get-HHHeavySlotStats -Events @($ev) -FromUtc $nowB.AddHours(-24) -ToUtc $nowB -ProjectOf { param($l) Get-HHLabelProject $l }
              $w = @(foreach ($i in 0..143) { New-WB $nowB.AddMinutes(-5 * $i) 40 })
              $v = Get-HHVerdict -Rollup (Get-HHRollup -Windows $w -NowUtc $nowB -Hours 24 -Hardware $hwB -HeavySlot $hs -CanaryBaselineMs 40) -Hardware $hwB
              "VERDICT=$($v.verdict) GATE_FLAG=$(if ($v.findings -match 'slot') { 'yes:' + ($v.findings -match 'slot' -join ',') } else { 'none' }) duty=$($hs.duty)" }
        'C' { $m = ModC; CIsolate $m; $r = Join-Path $tmp 's'; Write-SamplesC $r 1920 { 250 }   # RATIFIER FIX: 8 h world (C needs >= 6 h span), ledger 70 % held across it
              $led = Join-Path $tmp 'ledger.jsonl'; $u = [datetime]::UtcNow
              $lines = foreach ($k in 0..15) { $a = $u.AddMinutes(-475 + 30 * $k)
                  (@{ at = $a.ToString('o'); event = 'admit'; ticket = "t$k"; label = 'airmypc:gate:x'; class = 'exclusive'; waitedMs = 1200000 } | ConvertTo-Json -Compress)
                  (@{ at = $a.AddMinutes(21).ToString('o'); event = 'exit'; ticket = "t$k"; code = 0 } | ConvertTo-Json -Compress) }
              Set-Content $led $lines; & $m { param($f) $script:HeavySlotLedger = $f } $led
              $s = Get-HostHeadroomSummary -Hours 8 -Root $r
              "VERDICT=$($s.headroom.verdict) GATE_FLAG=$(if ($s.headroom.heavy_slot_verdict -in 'TIGHT','FULL') { 'yes:heavy_slot_verdict=' + $s.headroom.heavy_slot_verdict } else { 'none' }) occupancy=$($s.heavy_slot.occupancy_frac)" }
    }
}

'power' {   # parse the REAL Core Temp adapter feed format (dd.MM.yyyy local dates, package W) into a power signal
    $feed = 'C:\temp\hwinfo-log-adapter.csv'
    if (-not (Test-Path $feed)) { 'PRECONDITION-MISSING: no Core Temp adapter feed'; exit 3 }
    $fs = [IO.FileStream]::new($feed, 'Open', 'Read', 'ReadWrite,Delete'); $len = $fs.Length; $take = [Math]::Min($len, 200000); $null = $fs.Seek($len - $take, 'Begin'); $buf = [byte[]]::new($take); $null = $fs.Read($buf, 0, $take); $fs.Dispose()
    $hdr = Get-Content $feed -TotalCount 1
    $copy = Join-Path $tmp 'feed.csv'; [IO.File]::WriteAllText($copy, $hdr + "`n" + (([Text.Encoding]::UTF8.GetString($buf) -split "`r?`n" | Select-Object -Skip 1) -join "`n"))
    switch ($Cand) {
        'A' { $ast = [Management.Automation.Language.Parser]::ParseFile((Join-Path $SA 'MachineLoadSampler.ps1'), [ref]$null, [ref]$null)
              $fn = $ast.FindAll({ $args[0] -is [Management.Automation.Language.FunctionDefinitionAst] -and $args[0].Name -in 'Read-CoreTemp', 'Write-Log' }, $true)
              foreach ($f in $fn) { . ([scriptblock]::Create($f.Extent.Text)) }
              $script:tz = [TimeZoneInfo]::Local; $script:tzRead = [DateTime]::UtcNow; $CoreTempFeed = $copy
              $r = Read-CoreTemp ([datetime]::UtcNow.AddMinutes(-30)) ([datetime]::UtcNow)
              "POWER_ROWS=$($r.n) PKG_W_MAX=$(($r.pkg_w | Measure-Object -Maximum).Maximum)" }
        'B' { $hits = @(Select-String -Path (Join-Path $SB '*') -Pattern 'hwinfo|Core Temp|Package Power|pkg_w|watt' -List); "POWER_ROWS=0 (B reads no power source: $($hits.Count) files reference one)" }
        'C' { $m = ModC; & $m { param($f) $script:CoreTempFeed = $f } $copy; $q = @()
              $r = & $m { param($q) Read-CoreTempWindow -Hours 0.5 -Exclude $q } $q
              "POWER_ROWS=$($r.rows) AT_POWER_CEILING_FRAC=$($r.at_power_ceiling_frac)" }
    }
}

'privacy' {   # a record built from THIS machine's real local data carries no path, user name, image or script name
    $pat = '[A-Za-z]:\\\\|\\\\Users\\\\|' + [regex]::Escape($env:USERNAME) + '|\.exe|\.ps1|-File '
    switch ($Cand) {
        'A' { PyA 'privacy' }
        'B' { $null = ModB; $d = Join-Path $env:LOCALAPPDATA 'fleet\host-headroom'
              if (-not (Get-ChildItem $d -Filter 'windows-*.jsonl' -EA SilentlyContinue)) { 'PRECONDITION-MISSING: no B windows on this machine'; exit 3 }
              $dd = Join-Path $tmp 'd'; Copy-Item $d $dd -Recurse; $led = Join-Path $tmp 'ledger.jsonl'
              $fs = [IO.FileStream]::new('C:\ProgramData\HeavySlot\ledger.jsonl', 'Open', 'Read', 'ReadWrite,Delete'); $o = [IO.File]::Create($led); $fs.CopyTo($o); $o.Dispose(); $fs.Dispose()
              $rec = Invoke-HHEvaluation -DataDir $dd -BusRoot $OwnerClone -LedgerPath $led
              $s = $rec | ConvertTo-Json -Depth 10 -Compress; $l = @([regex]::Matches($s, $pat, 'IgnoreCase') | ForEach-Object Value | Select-Object -Unique)
              "RECORD_BYTES=$($s.Length) LEAKS=$($l.Count) $($l -join ' ')" }
        'C' { $m = ModC; $s = Get-HostHeadroomSummary -Hours 2 | ConvertTo-Json -Depth 10 -Compress
              $l = @([regex]::Matches($s, $pat, 'IgnoreCase') | ForEach-Object Value | Select-Object -Unique)
              "RECORD_BYTES=$($s.Length) LEAKS=$($l.Count) $($l -join ' ')" }
    }
}

'attrib' {   # a CLI-like parent with NO path in its command line, cwd = a project, and a child that names the project
    $proj = Join-Path 'C:\!Layi Wkspc' 'agent-bridge'
    $env:MERIT_CHILD = "cmd /d /c `"ping -n 45 127.0.0.1 >nul & rem $proj\merit-probe-marker`""
    $pa = Start-Process cmd.exe -ArgumentList '/d', '/c', 'ping -n 45 127.0.0.1 >nul' -WorkingDirectory $proj -WindowStyle Hidden -PassThru     # case 1: cwd only
    $pb = Start-Process cmd.exe -ArgumentList '/d', '/c', '"%MERIT_CHILD%"' -WorkingDirectory $env:WINDIR -WindowStyle Hidden -PassThru     # case 2: child names it
    Start-Sleep -Seconds 3
    $wa = Get-CimInstance Win32_Process -Filter "ProcessId=$($pa.Id)"; $wb = Get-CimInstance Win32_Process -Filter "ProcessId=$($pb.Id)"
    if ($wa.CommandLine -match 'Layi' -or $wb.CommandLine -match 'Layi') { "PROBE-INVALID: a parent command line carries the path"; exit 3 }
    $kidW = Get-CimInstance Win32_Process -Filter "ParentProcessId=$($pb.Id)" | Where-Object { $_.CommandLine -match 'merit-probe-marker' } | Select-Object -First 1
    if (-not $kidW) { 'PRECONDITION-MISSING: case-2 child not found'; exit 3 }
    try {
        switch ($Cand) {
            'A' { Add-Type -Path (Join-Path $SA 'MachineLoadNative.cs')
                  $rules = foreach ($r in (Get-Content -Raw (Join-Path $SA 'projects.json') | ConvertFrom-Json).rules) { [pscustomobject]@{ Project = [string]$r.project; Regex = [regex]::new([string]$r.pattern, 'IgnoreCase') } }
                  function PT([string]$t) { foreach ($r in $rules) { $m = $r.Regex.Match($t); if ($m.Success) { if ($r.Project -eq '$1' -and $m.Groups.Count -gt 1) { return $m.Groups[1].Value.ToLowerInvariant() }; return $r.Project } }; $null }
                  function LabelA($w) { $l = $null; foreach ($t in @([string]$w.CommandLine, [string]$w.ExecutablePath, [MachineLoadNative]::GetCurrentDirectory([int]$w.ProcessId))) { if (-not $l -and $t) { $l = PT $t } }; $l }
                  $c1 = LabelA $wa; $c2 = LabelA $wb
                  if (-not $c2) { $c2 = "(parent-unlabelled;child=$(LabelA $kidW))" } }
            'B' { $null = ModB; $rules = Get-HHProjectRules -WorkspaceRoots @('C:\!Layi Wkspc'); $snap = Get-HHProcessSnapshot $rules
                  $c1 = ($snap.GetEnumerator() | Where-Object { $_.Key -like "$($pa.Id):*" }).Value.cls; $c2 = ($snap.GetEnumerator() | Where-Object { $_.Key -like "$($pb.Id):*" }).Value.cls }
            'C' { # C's snapshot treats its own process tree as the sampler, so take it from a SIBLING pwsh, as the real task does
                  $r = pwsh -NoProfile -Command "`$m = Import-Module '$SC\HostHeadroom.psm1' -PassThru; `$s = & `$m { Get-ProcessSnapshot }; 'P1=' + `$s[$($pa.Id)].project + ';V1=' + `$s[$($pa.Id)].via; 'P2=' + `$s[$($pb.Id)].project + ';V2=' + `$s[$($pb.Id)].via"
                  $c1 = ($r | Where-Object { $_ -like 'P1=*' }) -replace '^P1=', ''; $c2 = ($r | Where-Object { $_ -like 'P2=*' }) -replace '^P2=', '' }
        }
        "CASE1_CWD_ONLY=$c1 CASE2_CHILD_NAMES_PROJECT=$c2"
    } finally { foreach ($p in $pa, $pb) { Get-CimInstance Win32_Process -Filter "ParentProcessId=$($p.Id)" | ForEach-Object { Get-CimInstance Win32_Process -Filter "ParentProcessId=$($_.ProcessId)" | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -EA SilentlyContinue } }; Get-CimInstance Win32_Process -Filter "ParentProcessId=$($p.Id)" | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -EA SilentlyContinue }; Stop-Process -Id $p.Id -Force -EA SilentlyContinue } }
}

'runtime' {   # installed, running, fresh data (< 10 min) on ALL three minis, principal resolves, one data location
    $snip = switch ($Cand) {
        'A' { '$f = Get-ChildItem C:\ProgramData\MachineLoad\data -Filter minute-*.jsonl -EA SilentlyContinue | Sort LastWriteTimeUtc | Select -Last 1; $t = Get-ScheduledTask -TaskPath \Fleet\ -TaskName "MachineLoad Sampler" -EA SilentlyContinue; $split = @(Get-ChildItem "$env:LOCALAPPDATA\MachineLoad" -Filter minute-*.jsonl -EA SilentlyContinue).Count' }
        'B' { '$f = Get-ChildItem "$env:LOCALAPPDATA\fleet\host-headroom" -Filter windows-*.jsonl -EA SilentlyContinue | Sort LastWriteTimeUtc | Select -Last 1; $t = Get-ScheduledTask -TaskName Fleet-HostHeadroom -EA SilentlyContinue; $split = 0' }
        'C' { '$f = Get-ChildItem "$env:LOCALAPPDATA\HostHeadroom" -Filter samples-*.jsonl -EA SilentlyContinue | Sort LastWriteTimeUtc | Select -Last 1; $t = Get-ScheduledTask -TaskPath \Fleet\ -TaskName "HostHeadroom Sampler" -EA SilentlyContinue; $split = 0' }
    }
    $snip += '; $age = if ($f) { [math]::Round(([datetime]::UtcNow - $f.LastWriteTimeUtc).TotalMinutes, 1) } else { -1 }; $sid = if ($t) { try { [void]([Security.Principal.NTAccount]$t.Principal.UserId).Translate([Security.Principal.SecurityIdentifier]); "ok" } catch { "UNRESOLVED" } } else { "no-task" }; $ok = ($t -and $t.State -ne "Disabled" -and $age -ge 0 -and $age -lt 10 -and $sid -eq "ok" -and $split -eq 0); "HOST $env:COMPUTERNAME ok=$ok task=$(if ($t) { $t.State } else { "ABSENT" }) newest_age_min=$age principal=$sid split_files=$split"'
    $rows = @(OnAll $snip); $rows
    "HOSTS_OK=$(@($rows | Where-Object { $_ -match 'ok=True' }).Count) of 3"
}

'launch' {   # the task launch is windowless AND passes the script's exit code (TRAPS 2026-09-02, 2026-10-20)
    switch ($Cand) {
        'B' { $code = Get-Content -Raw (Join-Path $SB 'Start-HostHeadroom.ps1'); $exe = [regex]::Match($code, 'New-ScheduledTaskAction -Execute "([^"]+)"').Groups[1].Value
              "TASK_EXECUTE=$exe (B's task is absent on every mini, so read from its installer)"; if ($exe -match 'conhost') { 'LAUNCH=conhost-headless (exit code hidden, child outlives a stop)' } else { 'LAUNCH=hidden-exitcode' } }
        default { $names = if ($Cand -eq 'A') { "'MachineLoad Sampler','MachineLoad Publisher'" } else { "'HostHeadroom Sampler','HostHeadroom Publisher'" }
              $rows = @(OnAll "foreach (`$n in $names) { `$t = Get-ScheduledTask -TaskPath \Fleet\ -TaskName `$n -EA SilentlyContinue; if (`$t) { `"`$env:COMPUTERNAME `$n EXEC=`$(Split-Path -Leaf `$t.Actions[0].Execute)`" } else { `"`$env:COMPUTERNAME `$n EXEC=ABSENT`" } }")
              $rows; $bad = @($rows | Where-Object { $_ -notmatch 'EXEC=(wscript\.exe|pairprog-hidden-task-launcher\.exe)$' })
              if ($bad.Count -or $rows.Count -lt 6) { 'LAUNCH=bad' } else { 'LAUNCH=hidden-exitcode' } }
    }
}

'checkout' {   # the publisher's git repository is its own, never the clone a person works in
    $ownerCommon = (git -C $OwnerClone rev-parse --path-format=absolute --git-common-dir).Trim()
    $bus = switch ($Cand) {
        'A' { $t = Get-ScheduledTask -TaskPath '\Fleet\' -TaskName 'MachineLoad Publisher'; [regex]::Match($t.Actions[0].Arguments, '--bus "([^"]+)"').Groups[1].Value }
        'B' { $log = Get-Content (Join-Path $env:LOCALAPPDATA 'fleet\host-headroom\sampler.log') | Select-Object -Last 1; "using B default BusRoot = <script>\..\..\..; installed script dir $env:LOCALAPPDATA\fleet\host-headroom-tool\tools\machine\host-headroom" | Out-Host
              Join-Path $env:LOCALAPPDATA 'fleet\host-headroom-tool' }
        'C' { $t = Get-ScheduledTask -TaskPath '\Fleet\' -TaskName 'HostHeadroom Publisher'; [Environment]::ExpandEnvironmentVariables([regex]::Match($t.Actions[0].Arguments, '-BusRoot\s+"([^"]+)"').Groups[1].Value) }
    }
    if (-not $bus -or -not (Test-Path $bus)) { "PRECONDITION-MISSING: publisher bus path not found ($bus)"; exit 3 }
    $common = (git -C $bus rev-parse --path-format=absolute --git-common-dir).Trim()
    "PUBLISHER_BUS=$($bus -replace [regex]::Escape($env:USERPROFILE), '~') GIT_COMMON=$($common -replace [regex]::Escape($env:USERPROFILE), '~')"
    "SHARES_PERSON_CLONE=$($common -eq $ownerCommon)"
}

'prereview' {   # no publisher armed to push to master while the tool itself is unmerged
    $branch = @{ A = 'machine/machine-load-20261116'; B = 'machine/host-headroom-20261116'; C = 'tools/host-headroom' }[$Cand]
    git -C $OwnerClone merge-base --is-ancestor "origin/$branch" origin/master 2>$null; "TOOL_MERGED=$($LASTEXITCODE -eq 0)"
    $snip = switch ($Cand) {
        'A' { '$t = Get-ScheduledTask -TaskPath \Fleet\ -TaskName "MachineLoad Publisher" -EA SilentlyContinue; $armed = [bool]($t -and $t.State -ne "Disabled")' }
        'B' { '$t = Get-ScheduledTask -TaskName Fleet-HostHeadroom -EA SilentlyContinue; $armed = [bool]($t -and $t.State -ne "Disabled" -and $t.Actions[0].Arguments -match "-Publish") -or [bool](Get-CimInstance Win32_Process -Filter "Name=''pwsh.exe''" | ? { $_.CommandLine -match "Start-HostHeadroom.+-Publish" })' }
        'C' { '$t = Get-ScheduledTask -TaskPath \Fleet\ -TaskName "HostHeadroom Publisher" -EA SilentlyContinue; $armed = [bool]($t -and $t.State -ne "Disabled")' }
    }
    $rows = @(OnAll ($snip + '; $n = if ($t) { ($t | Get-ScheduledTaskInfo).NextRunTime } else { $null }; "HOST $env:COMPUTERNAME publisher_armed=$armed next=$n"'))
    $rows; "ARMED_HOSTS=$(@($rows | Where-Object { $_ -match 'armed=True' }).Count)"
}

'ci' {   # a record push to master must not start the sealed disposition-intake matrix (CI-COST-CONTROL)
    $path = @{ A = 'machine-load/PC-MINI1/days-2026-11.jsonl'; B = 'heartbeats/machines/PC-MINI1.json'; C = 'heartbeats/host-headroom/PC-MINI1.json' }[$Cand]   # RATIFIER: C moved its record path in b18b38f8 (HostHeadroom.psm1 Publish-HostHeadroom)
    $wf = (git -C $OwnerClone show origin/master:.github/workflows/disposition-intake.yml) -join "`n"
    $push = [regex]::Match($wf, '(?s)\n  push:\n(.*?)\n  [a-z_]+:').Groups[1].Value
    $globs = @([regex]::Matches($push, '- "([^"]+)"') | ForEach-Object { $_.Groups[1].Value })
    $ignored = [bool]($globs | Where-Object { $path -like ($_ -replace '\*\*', '*') })
    "RECORD_PATH=$path PUSH_PATHS_IGNORE=$($globs -join ',') CI_TRIGGERED=$(-not $ignored)"
}

'cost' {   # sampler CPU over a 5-minute window on pc-mini2 (elevated ssh session: every command line readable)
    $pat = @{ A = 'MachineLoadSampler\.ps1'; B = 'Start-HostHeadroom\.ps1.+-Run'; C = 'Run-HostHeadroom\.ps1.+Sample' }[$Cand]
    $snip = @"
`$seen = @{}; `$t0 = [datetime]::UtcNow
while (([datetime]::UtcNow - `$t0).TotalSeconds -lt 300) {
  foreach (`$w in Get-CimInstance Win32_Process -Filter "Name='pwsh.exe'" | Where-Object { `$_.CommandLine -match '$pat' }) {
    `$p = Get-Process -Id `$w.ProcessId -EA SilentlyContinue; if (-not `$p) { continue }
    `$k = "`$(`$w.ProcessId):`$(`$p.StartTime.Ticks)"; `$c = `$p.TotalProcessorTime.TotalSeconds
    if (-not `$seen.ContainsKey(`$k)) { `$seen[`$k] = @{ first = `$c; last = `$c; old = (`$p.StartTime.ToUniversalTime() -lt `$t0) } } else { `$seen[`$k].last = `$c } }
  Start-Sleep -Seconds 5 }
`$sec = 0.0; foreach (`$v in `$seen.Values) { `$sec += `$(if (`$v.old) { `$v.last - `$v.first } else { `$v.last }) }
"PROCS=`$(`$seen.Count) CPU_S_PER_MIN=`$([math]::Round(`$sec / 5, 2))"
"@
    $enc = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($snip))
    $r = ssh -n -o BatchMode=yes pc-mini1 "ssh -n -o BatchMode=yes pc-mini2 pwsh -NoProfile -EncodedCommand $enc" 2>$null   # RATIFIER: runs on pc-mini2, relayed via pc-mini1 (elevated ssh session, as the 01:50Z run) | Where-Object { $_ -match 'PROCS=' }
    if (-not $r -or $r -match 'PROCS=0') { "PRECONDITION-MISSING: no running sampler on pc-mini2 ($r)"; exit 3 }
    $r
}

'synthcap' {   # synthetic load never exceeds half the physical cores (owner rule 2026-10-07)
    switch ($Cand) {
        'A' { $hits = @(Select-String -Path (Join-Path $SA '*') -Pattern 'Parallel\.For|Start-ThreadJob|SHA256\]::HashData|stress|burn' ); "SYNTH_THREADS_MAX=0 (no synthetic load generator: $($hits.Count) hits)" }
        'B' { $c = Get-Content -Raw (Join-Path $SB 'HostHeadroom.psm1'); $par = [regex]::IsMatch($c, 'Parallel\.For|ThreadJob|RunspacePool'); "SYNTH_THREADS_MAX=$(if ($par) { 'many' } else { 1 }) (single-thread SHA-256 canary)" }
        'C' { $m = ModC; $w = & $m { Initialize-HostHeadroomCanary; $r = Invoke-HostHeadroomCanary -PhysicalCores 16; $r.wide_threads }; "SYNTH_THREADS_MAX=$w of 16 physical cores (measured by running the canary once)" }
    }
}

default { "unknown prop $Prop"; exit 2 }
}
} finally { Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue }
