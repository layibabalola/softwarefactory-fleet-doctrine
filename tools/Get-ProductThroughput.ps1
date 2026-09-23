<#
.SYNOPSIS
Instrument the ARTIFACT independently of the process that produces it, and refuse when it stalls.

.DESCRIPTION
Fleet instrument for the trap filed by conjugal and extended by adobe-ingester, 2026-09-23
(TRAPS.md): every instrument measured the factory; none measured what it produced. A factory
instrumented only on its own internal motion will faithfully report success while producing
nothing, because "healthy" comes to mean the gates are cycling, and the gates are cycling.

Three numbers, one pass over `git log --name-only`:
  1. age in days of the most recent PRODUCT commit
  2. count of PRODUCT commits inside the window
  3. coordination-only commits per product commit  <- the ratio IS the finding

Measured when this was written: conjugal 100.7:1 over six weeks; adobe-ingester 391:1 over
30 days, with application source touched on three calendar days in a 54-day project life.

TWO RULES THIS TOOL ENFORCES BY CONSTRUCTION, both paid for in calendar time:

  A. THE CLASSIFIER IS REQUIRED, NEVER GUESSED. -ProductPath has no default and this script
     refuses without it (exit 4). A generous classifier flatters: at adobe-ingester, counting
     the release/ tree -- which its own work order labels Class: PRODUCT -- would have turned a
     silent product month into a busy-looking one, because it is release tooling whose payload
     is the app. Machine-maintenance trees, observability tooling and any committed duplicate of
     the repo must be excluded explicitly. Declare what product means for YOUR board.

  B. THIS MUST NOT GATE THE PRODUCT ACT. Wire the non-zero exit into an OWNER-FACING escalation
     path. Never make it a precondition of a product commit, a product work-order transition, a
     review or an acceptance: the act it would block is the act that clears it. That archetype
     -- the repair requires the capability being repaired -- consumed roughly half of
     adobe-ingester's calendar life. If you wire it into a governing control, assert in that
     control's test suite that a breached threshold leaves its exit code unchanged. Prose will
     not hold this boundary.

And the rule this tool cannot enforce for you: put it somewhere it can BIND. An instrument in a
git-excluded directory with zero callers is decorative, however correct its logic. Check that its
path is tracked and grep the tree for callers before crediting it.

.PARAMETER ProductPath
REQUIRED. Repo-relative path prefixes (or exact file paths) that constitute the product.
Example: -ProductPath 'src/', 'app/', 'pyproject.toml'

.PARAMETER CoordinationPath
Prefixes that are the factory talking to itself. Commits touching ONLY these are the ratio's
numerator. Default: nothing -- meaning every non-product commit counts as coordination. Declare
these when you have a third category (vendored code, docs you consider product-adjacent).

.EXAMPLE
pwsh -File tools/Get-ProductThroughput.ps1 -Root C:\repo -ProductPath 'src/' -MaxAgeDays 7

.OUTPUTS
Exit 0  MOVING   - a product commit landed inside -MaxAgeDays
Exit 1  STALLED  - it did not. This is the point of the tool; let it break something owner-facing.
Exit 4  FAILED   - not a git repo, git unavailable, or no classifier declared
#>
[CmdletBinding()]
param(
    # Not [Mandatory]: that would PROMPT under -File, which hangs an unattended caller.
    # The explicit check below refuses with exit 4 instead, so it fails closed and fast.
    [string[]]$ProductPath = @(),
    [string]$Root = (Get-Location).Path,
    [string[]]$CoordinationPath = @(),
    [int]$WindowDays = 30,
    [int]$MaxAgeDays = 7,
    [switch]$AsJson
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not $ProductPath -or $ProductPath.Count -eq 0) {
    Write-Output 'FAILED: -ProductPath is required. This tool will not guess what product means.'
    exit 4
}
if (-not (Test-Path -LiteralPath (Join-Path $Root '.git'))) {
    Write-Output "FAILED: not a git repository: $Root"; exit 4
}

# Two coercions, both load-bearing, both caught by the cross-repo control run:
#
#   Split(',') - `pwsh -File script.ps1 -ProductPath a,b,c` passes ONE literal string "a,b,c".
#   -File does not parse PowerShell argument syntax. Since every scheduler, hook and CI caller
#   uses -File, a [string[]] parameter silently arrives as a single unmatched element, and the
#   tool then reports zero product commits in a repo that ships daily -- indistinguishable from
#   a true stall. This is the decorative-instrument failure the trap warns about, reproduced in
#   the instrument itself. Splitting here makes -File and -Command behave identically.
#
#   @() - a single-element or empty pipeline returns a scalar or $null, and .Count on $null
#   throws under Set-StrictMode.
$prod  = @($ProductPath      | ForEach-Object { $_ -split ',' } | Where-Object { $_ } | ForEach-Object { ($_.Trim() -replace '\\', '/') })
$coord = @($CoordinationPath | ForEach-Object { $_ -split ',' } | Where-Object { $_ } | ForEach-Object { ($_.Trim() -replace '\\', '/') })

function Classify([string]$path) {
    $p = $path -replace '\\', '/'
    foreach ($x in $prod)  { if ($p -eq $x -or $p.StartsWith($x)) { return 'product' } }
    if ($coord.Count -eq 0) { return 'coordination' }
    foreach ($x in $coord) { if ($p -eq $x -or $p.StartsWith($x)) { return 'coordination' } }
    return 'other'
}

$since = (Get-Date).ToUniversalTime().AddDays(-$WindowDays).ToString('yyyy-MM-dd')
$raw = & git -C $Root log --all --since=$since --name-only --format="%x00%H%x1f%cI" 2>&1
if ($LASTEXITCODE -ne 0) { Write-Output 'FAILED: git log failed'; exit 4 }

$script:productCommits = 0; $script:coordinationOnly = 0; $script:totalCommits = 0
$script:cur = $null; $script:curKinds = @{}

function Flush {
    if ($null -eq $script:cur) { return }
    $script:totalCommits++
    if ($script:curKinds.ContainsKey('product')) { $script:productCommits++ }
    elseif ($script:curKinds.ContainsKey('coordination') -and -not $script:curKinds.ContainsKey('other')) {
        $script:coordinationOnly++
    }
    $script:cur = $null; $script:curKinds = @{}
}

foreach ($line in $raw) {
    $l = [string]$line
    if ($l.StartsWith([char]0)) {
        Flush
        $parts = $l.TrimStart([char]0).Split([char]31)
        $script:cur = [pscustomobject]@{ sha = $parts[0]; date = $parts[1] }
        $script:curKinds = @{}
        continue
    }
    if ([string]::IsNullOrWhiteSpace($l)) { continue }
    if ($null -ne $script:cur) { $script:curKinds[(Classify $l)] = $true }
}
Flush

# Age is measured over ALL history, not just the window: a board that has shipped nothing in
# six months must not read as healthy merely because the window is short.
$pathArgs = @($prod | ForEach-Object { $_.TrimEnd('/') })
$lastRaw = & git -C $Root log --all -1 --format="%H%x1f%cI" -- @pathArgs 2>&1
$lastSha = $null; $lastDate = $null; $ageDays = $null
if ($LASTEXITCODE -eq 0 -and $lastRaw) {
    $p = ([string]$lastRaw).Split([char]31)
    if ($p.Count -ge 2) {
        $lastSha = $p[0]; $lastDate = $p[1]
        $ageDays = [math]::Round(((Get-Date).ToUniversalTime() - ([datetimeoffset]$lastDate).UtcDateTime).TotalDays, 1)
    }
}

$ratio = if ($script:productCommits -gt 0) {
    [math]::Round($script:coordinationOnly / $script:productCommits, 1)
} else { $null }
$stalled = ($null -eq $ageDays) -or ($ageDays -gt $MaxAgeDays)
$verdict = if ($stalled) { 'STALLED' } else { 'MOVING' }

if ($AsJson) {
    [pscustomobject]@{
        schema                    = 'fleet/product-throughput/v1'
        measured_utc              = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
        root                      = $Root
        product_paths             = $prod
        window_days               = $WindowDays
        max_age_days              = $MaxAgeDays
        last_product_commit       = $lastSha
        last_product_commit_utc   = $lastDate
        last_product_commit_age_d = $ageDays
        product_commits_in_window = $script:productCommits
        coordination_only_commits = $script:coordinationOnly
        total_commits_in_window   = $script:totalCommits
        coordination_per_product  = $ratio
        verdict                   = $verdict
    } | ConvertTo-Json -Depth 4
} else {
    $flag = if ($stalled) { '  [BLOCKING]' } else { '' }
    Write-Output '=========== PRODUCT THROUGHPUT ==========='
    Write-Output ("VERDICT: {0}{1}" -f $verdict, $flag)
    if ($null -eq $ageDays) {
        Write-Output '  last product commit : NONE IN HISTORY'
    } else {
        Write-Output ("  last product commit : {0} days ago  ({1}, {2})" -f $ageDays, $lastSha.Substring(0, 7), $lastDate)
    }
    Write-Output ("  product commits     : {0} in the last {1} days" -f $script:productCommits, $WindowDays)
    Write-Output ("  coordination-only   : {0} in the same window" -f $script:coordinationOnly)
    if ($null -ne $ratio) {
        Write-Output ("  RATIO               : {0} coordination commits per product commit" -f $ratio)
    } else {
        Write-Output '  RATIO               : undefined - the denominator is zero, which IS the finding'
    }
    Write-Output ("  classifier          : product = {0}" -f ($prod -join ', '))
    Write-Output '=========================================='
}

if ($stalled) { exit 1 }
exit 0
