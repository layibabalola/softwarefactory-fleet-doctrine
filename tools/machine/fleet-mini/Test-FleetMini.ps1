# READ-ONLY. Checks this machine, or other fleet machines over ssh, against the fleet mini baseline.
#   pwsh -NoProfile -File Test-FleetMini.ps1                       # this machine
#   pwsh -NoProfile -File Test-FleetMini.ps1 -Hosts a,b,c           # ssh aliases from ~/.ssh/config
#   add -Json for machine-readable rows. Exit 0 = every item OK, 1 = drift or unknown, 2 = a host could not be read.
param([string[]]$Hosts, [switch]$Json, [int]$TimeoutSeconds = 90)
$ErrorActionPreference = 'Stop'
# `pwsh -File ... -Hosts a,b` passes one string "a,b"; accept both forms.
$Hosts = @($Hosts | ForEach-Object { "$_" -split ',' } | ForEach-Object Trim | Where-Object { $_ })
$here = Split-Path -Parent $PSCommandPath
$module = Join-Path $here 'FleetMini.psm1'

if (-not $Hosts) {
    Import-Module $module -Force
    $rows = @(Invoke-FleetMiniCheck | ForEach-Object { $_ | Add-Member -NotePropertyName Host -NotePropertyValue $env:COMPUTERNAME -PassThru })
    $unreadable = 0
} else {
    $rows = @(); $unreadable = 0
    foreach ($h in $Hosts) {
        $stamp = [Guid]::NewGuid().ToString('N').Substring(0, 8)
        $remoteDir = "fleet-mini-check-$stamp"
        $out = Join-Path ([IO.Path]::GetTempPath()) "fleet-mini-$h-$stamp.out"
        # Copy the module next to the remote user's home, run it, delete it. stdout goes to a FILE, never an inherited
        # pipe: a nested Windows ssh writing to an inherited pipe can hang forever (fleet trap, 2026-11-13).
        & scp -q -o BatchMode=yes -o ConnectTimeout=10 $module "${h}:$remoteDir.psm1"
        if ($LASTEXITCODE -ne 0) { Write-Warning "$h`: could not copy the module (scp exit $LASTEXITCODE)"; $unreadable++; continue }
        # -EncodedCommand: Start-Process -ArgumentList re-splits a spaced, quoted argument, so send no spaces or quotes.
        $remote = "try { Import-Module ~/$remoteDir.psm1 -Force; Invoke-FleetMiniCheck | Select-Object Id,Class,Status,Current,Title,How | ConvertTo-Json -Compress -Depth 3 } finally { Remove-Item ~/$remoteDir.psm1 -ErrorAction SilentlyContinue }"
        $cmd = 'pwsh -NoProfile -NonInteractive -EncodedCommand ' + [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($remote))
        $p = Start-Process ssh -ArgumentList '-n', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', $h, $cmd `
            -RedirectStandardOutput $out -RedirectStandardError "$out.err" -NoNewWindow -PassThru
        if (-not $p.WaitForExit($TimeoutSeconds * 1000)) {
            Stop-Process -Id $p.Id -Force
            # best effort: do not leave the module copy behind on the remote host
            $c = Start-Process ssh -ArgumentList '-n', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', $h, "pwsh -NoProfile -EncodedCommand $([Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes("Remove-Item ~/$remoteDir.psm1 -ErrorAction SilentlyContinue")))" `
                -RedirectStandardOutput "$out.clean" -RedirectStandardError "$out.clean.err" -NoNewWindow -PassThru
            if (-not $c.WaitForExit(20000)) { Stop-Process -Id $c.Id -Force -ErrorAction SilentlyContinue }
            Remove-Item $out, "$out.err", "$out.clean", "$out.clean.err" -ErrorAction SilentlyContinue
            Write-Warning "$h`: TIMEOUT (a copy ~/$remoteDir.psm1 may remain there)"; $unreadable++; continue
        }
        $text = Get-Content $out -Raw -ErrorAction SilentlyContinue
        $errLine = (Get-Content "$out.err" -ErrorAction SilentlyContinue | Where-Object { $_.Trim() } | Select-Object -First 1)
        Remove-Item $out, "$out.err" -ErrorAction SilentlyContinue
        if (-not $text -or $text.IndexOf('[') -lt 0) { Write-Warning "$h`: no result$(if ($errLine) { " ($errLine)" })"; $unreadable++; continue }
        try { $parsed = @($text.Substring($text.IndexOf('[')) | ConvertFrom-Json) }
        catch { Write-Warning "$h`: unreadable result ($($_.Exception.Message))"; $unreadable++; continue }
        $rows += $parsed | ForEach-Object { $_ | Add-Member -NotePropertyName Host -NotePropertyValue $h -PassThru }
    }
}

if ($Json) { $rows | Select-Object Host, Id, Class, Status, Current | ConvertTo-Json -Depth 3 }
else {
    $hostsSeen = @($rows | ForEach-Object Host | Select-Object -Unique)
    $ids = @($rows | ForEach-Object Id | Select-Object -Unique)
    $fmt = '{0,-22} {1,-6} ' + (($hostsSeen | ForEach-Object { '{' + ([array]::IndexOf($hostsSeen, $_) + 2) + ',-22}' }) -join ' ')
    $fmt -f (@('item', 'class') + $hostsSeen)
    foreach ($id in $ids) {
        $cells = foreach ($hs in $hostsSeen) {
            $r = $rows | Where-Object { $_.Host -eq $hs -and $_.Id -eq $id } | Select-Object -First 1
            if (-not $r) { '-' } elseif ($r.Status -eq 'OK') { 'OK' } else { "$($r.Status): $($r.Current)" }
        }
        $class = ($rows | Where-Object Id -eq $id | Select-Object -First 1).Class
        $fmt -f (@($id, $class) + @($cells))
    }
    $bad = @($rows | Where-Object Status -ne 'OK')
    if ($bad) {
        ''
        'To fix (owner items are yours; admin items: run Initialize-FleetMini.ps1 -Apply elevated):'
        foreach ($b in $bad) { "  [$($b.Host)] $($b.Id) ($($b.Class)): $(if ($b.How) { $b.How } else { 'Initialize-FleetMini.ps1 -Apply' })" }
    }
}
if ($unreadable) { exit 2 }
if (@($rows | Where-Object Status -ne 'OK').Count) { exit 1 }
exit 0
