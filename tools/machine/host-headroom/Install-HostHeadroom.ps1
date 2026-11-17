<#
  Installs host-headroom on THIS machine from a reviewed bus commit (law 1). Needs an elevated shell
  (an ssh key login of an admin account is already elevated): the sampler task runs at Highest so it
  can read other processes' command lines for attribution.

    pwsh -NoProfile -File Install-HostHeadroom.ps1 -Commit <reviewed sha> [-BusRemote <url>]   # install / upgrade
    pwsh -NoProfile -File Install-HostHeadroom.ps1 -Status                                      # read-only check
    pwsh -NoProfile -File Install-HostHeadroom.ps1 -Uninstall                                   # remove tasks; keeps data

  What it creates:
    %USERPROFILE%\.claude\machine\host-headroom\   installed copy of the tool + installed-from.json
    %LOCALAPPDATA%\HostHeadroom\                   samples (14 days), receipts, the publisher's own bus clone
    Tasks \Fleet\HostHeadroom Sampler   (every 5 min)  and  \Fleet\HostHeadroom Publisher (every 6 h)
  Both tasks start through the fleet's hidden launcher (wscript -> launch-windowless.vbs ->
  pairprog-hidden-task-launcher.exe), the chain Core Temp telemetry uses: no console window, ever.
#>
[CmdletBinding(DefaultParameterSetName = 'Install')]
param(
    [Parameter(ParameterSetName = 'Install', Mandatory)][string]$Commit,
    [Parameter(ParameterSetName = 'Install')][string]$SourceRepo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path,
    [Parameter(ParameterSetName = 'Install')][string]$BusRemote = 'https://github.com/layibabalola/softwarefactory-fleet-doctrine.git',
    [Parameter(ParameterSetName = 'Status')][switch]$Status,
    [Parameter(ParameterSetName = 'Uninstall')][switch]$Uninstall
)
$ErrorActionPreference = 'Stop'
$TaskPath = '\Fleet\'
$Sampler = 'HostHeadroom Sampler'; $Publisher = 'HostHeadroom Publisher'
$Dest = Join-Path $env:USERPROFILE '.claude\machine\host-headroom'
$Data = Join-Path $env:LOCALAPPDATA 'HostHeadroom'
$Clone = Join-Path $Data 'bus'
$Vbs = Join-Path $env:USERPROFILE '.claude\ops\launch-windowless.vbs'
$Launcher = Join-Path $env:LOCALAPPDATA 'PairProg\bin\pairprog-hidden-task-launcher.exe'
$WScript = Join-Path $env:WINDIR 'System32\wscript.exe'
$Pwsh = (Get-Command pwsh -ErrorAction Stop).Source
$Files = 'HostHeadroom.psm1', 'Run-HostHeadroom.ps1', 'Get-FleetHostHeadroom.ps1', 'README.md'

function Show-Status {
    $o = [ordered]@{ machine = $env:COMPUTERNAME }
    $from = Join-Path $Dest 'installed-from.json'
    $o.installed = if (Test-Path -LiteralPath $from) { (Get-Content -LiteralPath $from -Raw | ConvertFrom-Json).commit } else { $null }
    foreach ($n in $Sampler, $Publisher) {
        $t = Get-ScheduledTask -TaskPath $TaskPath -TaskName $n -ErrorAction SilentlyContinue
        $i = if ($t) { $t | Get-ScheduledTaskInfo } else { $null }
        $o[$n] = if ($t) { "{0}; last {1:yyyy-MM-dd HH:mm} result {2}; RunLevel {3}" -f $t.State, $i.LastRunTime, $i.LastTaskResult, $t.Principal.RunLevel } else { 'ABSENT' }
    }
    $runs = Join-Path $Data 'runs.jsonl'
    $o.last_runs = if (Test-Path -LiteralPath $runs) { @(Get-Content -LiteralPath $runs -Tail 3) } else { @() }
    $newest = Get-ChildItem -LiteralPath $Data -Filter 'samples-*.jsonl' -ErrorAction SilentlyContinue | Sort-Object LastWriteTimeUtc | Select-Object -Last 1
    $o.newest_sample_age_s = if ($newest) { [math]::Round(([datetime]::UtcNow - $newest.LastWriteTimeUtc).TotalSeconds) } else { $null }
    $o.publisher_clone = Test-Path -LiteralPath (Join-Path $Clone '.host-headroom-publisher-clone')
    [pscustomobject]$o | Format-List
}

if ($Status) { Show-Status; exit 0 }

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) { [Console]::Error.WriteLine('Install-HostHeadroom needs an elevated shell (RunLevel Highest tasks). Run it over ssh from another mini, or elevated.'); exit 3 }

if ($Uninstall) {
    foreach ($n in $Sampler, $Publisher) { Unregister-ScheduledTask -TaskPath $TaskPath -TaskName $n -Confirm:$false -ErrorAction SilentlyContinue }
    "removed tasks; data kept at $Data and $Dest"; exit 0
}

foreach ($p in $Vbs, $Launcher, $WScript) { if (-not (Test-Path -LiteralPath $p)) { [Console]::Error.WriteLine("missing hidden-launch prerequisite: $p (install Core Temp telemetry first)"); exit 4 } }

# 1. copy the tool out of the reviewed commit (not out of the working tree)
$full = (git -C $SourceRepo rev-parse --verify "$Commit^{commit}" 2>$null)
if (-not $full) { [Console]::Error.WriteLine("commit $Commit not found in $SourceRepo (git fetch first)"); exit 5 }
New-Item -ItemType Directory -Path $Dest -Force | Out-Null
foreach ($f in $Files) {
    $blob = git -C $SourceRepo show "${full}:tools/machine/host-headroom/$f" 2>$null
    if ($LASTEXITCODE -ne 0) { [Console]::Error.WriteLine("tools/machine/host-headroom/$f is not in $full"); exit 5 }
    [IO.File]::WriteAllText((Join-Path $Dest $f), (($blob -join "`n") + "`n"), [Text.UTF8Encoding]::new($false))
}
[IO.File]::WriteAllText((Join-Path $Dest 'installed-from.json'), (@{ commit = $full; installed_utc = [datetime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ') } | ConvertTo-Json -Compress))

# 2. the publisher's own bus clone (it resets this clone to origin/master; nothing else uses it)
New-Item -ItemType Directory -Path $Data -Force | Out-Null
if (-not (Test-Path -LiteralPath (Join-Path $Clone '.git'))) {
    git clone --quiet --depth 20 --branch master $BusRemote $Clone 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { [Console]::Error.WriteLine("git clone of $BusRemote failed"); exit 6 }
}
Set-Content -LiteralPath (Join-Path $Clone '.host-headroom-publisher-clone') -Value 'This clone belongs to the host-headroom publisher task. It is reset to origin/master on every publish.' -Encoding utf8
Add-Content -LiteralPath (Join-Path $Clone '.git\info\exclude') -Value '.host-headroom-publisher-clone' -Encoding utf8

# 3. tasks, through the hidden launcher. Priority 4 (Normal), as Core Temp's tasks: the default 7 is
#    BelowNormal CPU + Low I/O, which starves pwsh under load and would make the canary measure
#    its own low priority instead of what a new normal job would see.
# the token name, not USERDOMAIN\USERNAME: under ssh USERDOMAIN reads WORKGROUP, which maps to no SID
$user = [Security.Principal.WindowsIdentity]::GetCurrent().Name
function New-HiddenAction([string]$label, [string]$argsLine) {
    $out = Join-Path $Data "$label.out.log"; $err = Join-Path $Data "$label.err.log"
    $a = "`"$Vbs`" --stdout `"$out`" --stderr `"$err`" --label `"$label`" -- `"$Pwsh`" -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$(Join-Path $Dest 'Run-HostHeadroom.ps1')`" $argsLine"
    New-ScheduledTaskAction -Execute $WScript -Argument $a
}
$principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Highest
$common = @{ Hidden = $true; StartWhenAvailable = $true; AllowStartIfOnBatteries = $true; DontStopIfGoingOnBatteries = $true; MultipleInstances = 'IgnoreNew' }
$sSet = New-ScheduledTaskSettingsSet @common -ExecutionTimeLimit (New-TimeSpan -Minutes 8) -Priority 4
$pSet = New-ScheduledTaskSettingsSet @common -ExecutionTimeLimit (New-TimeSpan -Minutes 20) -Priority 4
$sTrig = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 3650)
$pTrig = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(20) -RepetitionInterval (New-TimeSpan -Hours 6) -RepetitionDuration (New-TimeSpan -Days 3650)
Register-ScheduledTask -TaskPath $TaskPath -TaskName $Sampler -Action (New-HiddenAction 'host-headroom-sampler' '-Mode Sample') -Trigger $sTrig -Principal $principal -Settings $sSet -Force | Out-Null
Register-ScheduledTask -TaskPath $TaskPath -TaskName $Publisher -Action (New-HiddenAction 'host-headroom-publisher' "-Mode Publish -BusRoot `"$Clone`"") -Trigger $pTrig -Principal $principal -Settings $pSet -Force | Out-Null

# 4. prove the registration matches the contract (a registration is not a firing: -Status shows runs)
$bad = @()
foreach ($n in $Sampler, $Publisher) {
    $t = Get-ScheduledTask -TaskPath $TaskPath -TaskName $n
    if ($t.Actions[0].Execute -ne $WScript) { $bad += "${n}: Execute is $($t.Actions[0].Execute)" }
    if ($t.Principal.RunLevel -ne 'Highest') { $bad += "${n}: RunLevel $($t.Principal.RunLevel)" }
    if (-not $t.Settings.Hidden) { $bad += "${n}: not Hidden" }
    if ([int]$t.Settings.Priority -ne 4) { $bad += "${n}: Priority $($t.Settings.Priority)" }
    if ($t.Settings.MultipleInstances -ne 'IgnoreNew') { $bad += "${n}: MultipleInstances $($t.Settings.MultipleInstances)" }
}
if ($bad) { [Console]::Error.WriteLine("VERIFY FAILED: $($bad -join '; ')"); exit 10 }
"installed $full on $env:COMPUTERNAME"
Show-Status
