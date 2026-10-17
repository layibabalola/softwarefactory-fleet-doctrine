# Make a project a consumer WITHOUT running unverified bytes: write the reviewed runner blob into a PRIVATE temporary
# directory, prove its identity against git's own tree entry, and only then run it there, isolated (python -I: the
# project's files can never be imported into it). The project itself is touched only by install/init, which plan
# everything first and refuse (writing nothing) on any mismatch. Refuses (exit 2, runner never started) on a mismatch.
# usage: bootstrap.ps1 <bus-clone> <bus-sha> <tool | profile:NAME> <reviewer> <reason> [project-root]
# profile:NAME runs `init --profile NAME` (a whole factory) instead of `install <tool>`.
param([Parameter(Mandatory)][string]$Bus, [Parameter(Mandatory)][string]$Sha, [Parameter(Mandatory)][string]$Tool,
      [Parameter(Mandatory)][string]$Reviewer, [Parameter(Mandatory)][string]$Reason, [string]$Project = '.')
$ErrorActionPreference = 'Stop'
$rel = 'tools/factory/pin-runner.py'
$want = git -C $Bus rev-parse --verify "${Sha}:$rel"
if ($LASTEXITCODE -ne 0) { [Console]::Error.WriteLine("REFUSED: $Sha has no $rel in $Bus"); exit 2 }
$dir = Join-Path ([IO.Path]::GetTempPath()) ("factory-bootstrap-" + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Force $dir | Out-Null
try {
  $dst = Join-Path $dir 'pin-runner.py'
  # cmd writes the blob's raw bytes; PowerShell's own `>` would re-encode them.
  cmd /c "git -C `"$Bus`" show ${Sha}:$rel > `"$dst`""
  $got = git hash-object --no-filters $dst
  if ($got -ne $want) {
    [Console]::Error.WriteLine("REFUSED: runner bytes hash to $got, not object $want; nothing was run"); exit 2
  }
  if ($Tool -like 'profile:*') {
    python -I $dst init --profile $Tool.Substring(8) --commit $Sha --reviewer $Reviewer --reason $Reason --project-root $Project --bus $Bus
  } else {
    python -I $dst install $Tool --commit $Sha --reviewer $Reviewer --reason $Reason --project-root $Project --bus $Bus
  }
  exit $LASTEXITCODE
} finally {
  Remove-Item -Recurse -Force $dir -ErrorAction SilentlyContinue
}
