# Make a project a consumer WITHOUT running unverified bytes: write the reviewed runner blob, prove its
# identity against git's own tree entry, and only then run it. Refuses (exit 2, runner never started) on mismatch.
# usage: bootstrap.ps1 <bus-clone> <bus-sha> <tool> <reviewer> <reason> [project-root]
param([Parameter(Mandatory)][string]$Bus, [Parameter(Mandatory)][string]$Sha, [Parameter(Mandatory)][string]$Tool,
      [Parameter(Mandatory)][string]$Reviewer, [Parameter(Mandatory)][string]$Reason, [string]$Project = '.')
$ErrorActionPreference = 'Stop'
$rel = 'tools/factory/pin-runner.py'
$dir = Join-Path $Project 'factory-pins'; $dst = Join-Path $dir 'pin-runner.py'; $tmp = "$dst.tmp"
$want = git -C $Bus rev-parse --verify "${Sha}:$rel"
if ($LASTEXITCODE -ne 0) { [Console]::Error.WriteLine("REFUSED: $Sha has no $rel in $Bus"); exit 2 }
New-Item -ItemType Directory -Force $dir | Out-Null
# cmd writes the blob's raw bytes; PowerShell's own `>` would re-encode them.
cmd /c "git -C `"$Bus`" show ${Sha}:$rel > `"$tmp`""
$got = git hash-object --no-filters $tmp
if ($got -ne $want) {
  Remove-Item -Force $tmp
  [Console]::Error.WriteLine("REFUSED: runner bytes hash to $got, not object $want; nothing was run"); exit 2
}
Move-Item -Force $tmp $dst
python $dst install $Tool --commit $Sha --reviewer $Reviewer --reason $Reason --project-root $Project --bus $Bus
exit $LASTEXITCODE
