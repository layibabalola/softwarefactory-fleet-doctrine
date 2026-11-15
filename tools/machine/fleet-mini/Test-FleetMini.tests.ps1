# Tests for tools/machine/fleet-mini. No Pester, no elevation, changes nothing on the machine.
#   pwsh -NoProfile -File tools/machine/fleet-mini/Test-FleetMini.tests.ps1
$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $PSCommandPath
$pass = 0; $fail = 0
function Assert([bool]$c, [string]$name) { if ($c) { $script:pass++; "ok   $name" } else { $script:fail++; "FAIL $name" } }

# 1. every shipped script parses
foreach ($f in Get-ChildItem $here -File -Include *.ps1, *.psm1 -Recurse) {
    $errs = $null; [void][Management.Automation.Language.Parser]::ParseFile($f.FullName, [ref]$null, [ref]$errs)
    Assert (-not $errs) "parses: $($f.Name)"
}

$mod = Import-Module (Join-Path $here 'FleetMini.psm1') -Force -PassThru

# 2. the table is well formed
$items = @(Get-FleetMiniItems)
Assert ($items.Count -ge 20) "baseline has items ($($items.Count))"
Assert (@($items.Id | Select-Object -Unique).Count -eq $items.Count) 'ids are unique'
foreach ($i in $items) {
    Assert ($i.Class -in 'user', 'admin', 'owner') "$($i.Id): known class"
    Assert ([bool]$i.Title -and [bool]$i.Why) "$($i.Id): has title and why"
    if ($i.Class -eq 'owner') { Assert ((-not $i.Fix) -and [bool]$i.How) "$($i.Id): owner item has a How and no Fix" }
    else { Assert ([bool]$i.Fix) "$($i.Id): $($i.Class) item has a Fix" }
}

# 3. Mouse Keys judgement: on = bit 0 set
$mk = $items | Where-Object Id -eq 'mouse-keys'
Assert ((& $mk.Ok 31) -and -not (& $mk.Ok 62) -and -not (& $mk.Ok $null)) 'mouse-keys: 31 on, 62 off, missing off'

# 4. a real read of this machine returns one row per item with a known status
$rows = @(Invoke-FleetMiniCheck)
Assert ($rows.Count -eq $items.Count) 'check returns one row per item'
Assert (-not ($rows | Where-Object { $_.Status -notin 'OK', 'DRIFT', 'UNKNOWN' })) 'every status is OK, DRIFT or UNKNOWN'

# 4b. -Only: comma form accepted, unknown id refused (never "all clear")
Assert (@(Invoke-FleetMiniCheck -Only 'mouse-keys,long-paths').Count -eq 2) '-Only "a,b" selects two items'
$threw = $false; try { Invoke-FleetMiniCheck -Only 'no-such-item' | Out-Null } catch { $threw = $true }
Assert $threw '-Only with an unknown id throws'
$ep = $items | Where-Object Id -eq 'exec-policy'
Assert ((& $ep.Ok 'ps7=RemoteSigned ps51=RemoteSigned') -and -not (& $ep.Ok 'ps7=RemoteSigned ps51=Restricted(default)')) 'exec-policy needs both shells RemoteSigned'
$py = $items | Where-Object Id -eq 'tool-python'
Assert ("$($py.Get)" -match '-V') 'tool-python asks for a version (Store alias does not count)'
$gen = "$((Get-Command Set-FleetMiniMouseKeys).ScriptBlock)"
Assert ($gen -match 'PSScriptRoot' -and $gen -match '-File `"') 'one-shot run.ps1 embeds no paths and the task quotes its -File path'

# 5. apply logic, on fake items inside the module scope (nothing real is touched)
$probe = Join-Path ([IO.Path]::GetTempPath()) ('fleet-mini-test-' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory $probe | Out-Null
try {
    & $mod {
        param($probe)
        $script:TestProbe = $probe
        $script:RealItems = ${function:Get-FleetMiniItems}
        Set-Item function:Get-FleetMiniItems {
            @(
                New-FleetMiniItem 'fake-user' 'user' 't' 'w' { 'bad' } { param($v) $v -eq 'good' } { New-Item -ItemType File (Join-Path $script:TestProbe 'user-fixed') | Out-Null; 'x' } ''
                New-FleetMiniItem 'fake-owner' 'owner' 't' 'w' { 'bad' } { param($v) $v -eq 'good' } { New-Item -ItemType File (Join-Path $script:TestProbe 'owner-fixed') | Out-Null } 'do it'
                New-FleetMiniItem 'fake-throws' 'user' 't' 'w' { throw 'boom' } { param($v) $true } { New-Item -ItemType File (Join-Path $script:TestProbe 'throw-fixed') | Out-Null } ''
                New-FleetMiniItem 'fake-ok' 'user' 't' 'w' { 'good' } { param($v) $v -eq 'good' } { New-Item -ItemType File (Join-Path $script:TestProbe 'ok-fixed') | Out-Null } ''
            )
        }
    } $probe
    $dry = @(Invoke-FleetMiniApply)
    Assert (($dry | Where-Object Id -eq 'fake-user').Action -eq 'WOULD-SET') 'dry run reports WOULD-SET'
    Assert (-not (Get-ChildItem $probe)) 'dry run changes nothing'
    $chk = @(Invoke-FleetMiniCheck)
    Assert (($chk | Where-Object Id -eq 'fake-throws').Status -eq 'UNKNOWN') 'a read that throws is UNKNOWN, never OK'
    $wet = @(Invoke-FleetMiniApply -Apply)
    Assert (Test-Path (Join-Path $probe 'user-fixed')) '-Apply runs a user fix'
    Assert (-not (Test-Path (Join-Path $probe 'owner-fixed'))) '-Apply never runs an owner item'
    Assert (-not (Test-Path (Join-Path $probe 'throw-fixed'))) '-Apply skips an UNKNOWN item'
    Assert (-not (Test-Path (Join-Path $probe 'ok-fixed'))) '-Apply leaves an OK item alone'
    Assert (-not ($wet | Where-Object Id -in 'fake-owner', 'fake-ok', 'fake-throws')) 'receipt lists only what it acted on'
} finally {
    & $mod { Set-Item function:Get-FleetMiniItems $script:RealItems }
    Remove-Item -Recurse -Force $probe -ErrorAction SilentlyContinue
}

# 6. admin items are skipped, not attempted, when not elevated
if (-not (Test-FleetMiniElevated)) {
    & $mod { $script:RealItems = ${function:Get-FleetMiniItems}; Set-Item function:Get-FleetMiniItems { @(New-FleetMiniItem 'fake-admin' 'admin' 't' 'w' { 'bad' } { param($v) $false } { throw 'must not run' } '') } }
    try { Assert ((@(Invoke-FleetMiniApply -Apply))[0].Action -eq 'SKIPPED-NEEDS-ELEVATION') 'admin item skipped when not elevated' }
    finally { & $mod { Set-Item function:Get-FleetMiniItems $script:RealItems } }
} else { 'skip admin-not-elevated case (this shell is elevated)' }

# 7. law 4: the shipped files name no user, host, address or account
$patterns = @('[A-Za-z]:\\Users\\[A-Za-z]', '(?<![~\d.])\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[\w.+-]+@[\w-]+\.[\w.]+', ('PC-' + 'MINI'), ('VIRTUAL' + '-TEN'), ('ultra' + '-magnus'))
foreach ($f in Get-ChildItem $here -File -Recurse) {
    $hits = @(foreach ($p in $patterns) { Select-String -Path $f.FullName -Pattern $p -AllMatches | Where-Object { $_.Line -notmatch 'patterns = @' } })
    Assert (-not $hits) "law 4 clean: $($f.Name)$(if ($hits) { ' -> ' + $hits[0].Line.Trim() })"
}

"`n$pass passed, $fail failed"
if ($fail) { exit 1 }
