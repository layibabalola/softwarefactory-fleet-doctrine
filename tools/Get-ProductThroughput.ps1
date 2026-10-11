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

.PARAMETER Lines
LINE MODE (added 2026-10-11, owner defect D3 "paperwork outweighs product"). Counts CHANGED LINES
(adds + deletes from `git log --numstat`; merge commits excluded; binary files ignored and counted
separately) per project over the window, bucketed into product / tests / factory-tooling /
coordination-paperwork / vendored-copies using the per-project path classes in -ClassConfig.
Unmatched paths are reported as 'unclassified', never dropped. Emits product share
(= product / total) and a table ranked by product lines per week. Walks the configured ref of each
project only, never --all (TRAPS 2026-09-25: --all counts unlanded work). DIAGNOSTIC ONLY, per
metrics/README.md law 1: line mode never exits 1 and must never be wired as a gate or a target.
Exit 0 measured, 4 FAILED (bad config, missing repo, bad ref, -Since without an explicit offset).

.PARAMETER ClassConfig
Line mode classifier (default: product-throughput-classes.json beside this script). Schema
fleet/product-throughput-classes/v1; pattern rules are documented in the file's "note".

.PARAMETER Project
Line mode: restrict to these project names from the config. Default: all.

.PARAMETER Since
Line mode window start. MUST carry an explicit offset ('2026-09-27T00:00:00Z' or '...-05:00'):
a naive timestamp is read as local time and silently moves the window edge (ruling candidate
product-share-is-the-fixpoint-instrument-r1 §4.4). Default: now (UTC) minus -WindowDays.

.EXAMPLE
pwsh -File tools/Get-ProductThroughput.ps1 -Root C:\repo -ProductPath 'src/' -MaxAgeDays 7

.EXAMPLE
pwsh -File tools/Get-ProductThroughput.ps1 -Lines -WindowDays 14 -AsJson

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
    [Alias('Json')][switch]$AsJson,
    [switch]$Lines,
    [string]$ClassConfig = (Join-Path $PSScriptRoot 'product-throughput-classes.json'),
    [string[]]$Project = @(),
    [string]$Since = ''
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($Lines) {
    $Buckets = @('product', 'tests', 'vendored-copies', 'factory-tooling', 'coordination-paperwork')
    $nowUtc = (Get-Date).ToUniversalTime()
    if ([string]::IsNullOrWhiteSpace($Since)) {
        $sinceUtc = $nowUtc.AddDays(-$WindowDays)
    } else {
        if ($Since -notmatch '(Z|[+-]\d\d:?\d\d)$') {
            Write-Output "FAILED: -Since '$Since' has no explicit UTC offset; refusing to guess the window edge."; exit 4
        }
        $sinceUtc = ([datetimeoffset]::Parse($Since, [Globalization.CultureInfo]::InvariantCulture)).UtcDateTime
    }
    $sinceIso = $sinceUtc.ToString('yyyy-MM-ddTHH:mm:ssZ')
    $days = [math]::Max(($nowUtc - $sinceUtc).TotalDays, 1e-9)
    if (-not (Test-Path -LiteralPath $ClassConfig -PathType Leaf)) {
        Write-Output "FAILED: class config not found: $ClassConfig"; exit 4
    }
    $cfg = Get-Content -LiteralPath $ClassConfig -Raw | ConvertFrom-Json
    if ($cfg.schema -ne 'fleet/product-throughput-classes/v1') {
        Write-Output "FAILED: class config schema is not fleet/product-throughput-classes/v1"; exit 4
    }
    $wanted = @($Project | ForEach-Object { $_ -split ',' } | Where-Object { $_ } | ForEach-Object { $_.Trim() })
    $projects = @($cfg.projects | Where-Object { $wanted.Count -eq 0 -or $wanted -contains $_.name })
    if ($projects.Count -eq 0) { Write-Output 'FAILED: no matching projects in the class config'; exit 4 }

    # Flatten one project's classes into rules ranked by specificity (non-wildcard chars), then by
    # bucket order. './x' = root-level only. A pattern with '*' uses -like; otherwise prefix/exact.
    function Get-Rules($classes) {
        $rules = [Collections.Generic.List[object]]::new()
        for ($i = 0; $i -lt $Buckets.Count; $i++) {
            $b = $Buckets[$i]
            $prop = $classes.PSObject.Properties[$b]
            if ($null -eq $prop) { continue }
            foreach ($pat in @($prop.Value)) {
                if ([string]::IsNullOrWhiteSpace($pat)) { continue }
                $p = ([string]$pat) -replace '\\', '/'
                $rootOnly = $p.StartsWith('./')
                if ($rootOnly) { $p = $p.Substring(2) }
                $rules.Add([pscustomobject]@{
                    bucket = $b; pattern = $p; rootOnly = $rootOnly; glob = $p.Contains('*')
                    score = ($p -replace '\*', '').Length; order = $i })
            }
        }
        foreach ($k in $classes.PSObject.Properties.Name) {
            if ($Buckets -notcontains $k) { throw "unknown bucket '$k' in class config" }
        }
        return @($rules | Sort-Object @{ Expression = 'score'; Descending = $true }, 'order')
    }
    function Get-Bucket([string]$path, $rules) {
        foreach ($r in $rules) {
            if ($r.rootOnly -and $path.Contains('/')) { continue }
            if ($r.glob) { if ($path -like $r.pattern) { return $r.bucket } }
            elseif ($path -eq $r.pattern -or $path.StartsWith($r.pattern)) { return $r.bucket }
        }
        return 'unclassified'
    }
    # numstat rename forms: 'a/{old => new}/f' and 'old => new'. Attribute to the new path.
    function Resolve-NumstatPath([string]$p) {
        $p = [regex]::Replace($p, '\{([^{}]*) => ([^{}]*)\}', '$2')
        if ($p.Contains(' => ')) { $p = $p.Substring($p.IndexOf(' => ') + 4) }
        return ($p -replace '//+', '/')
    }

    $prevEnc = [Console]::OutputEncoding
    [Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
    $rows = [Collections.Generic.List[object]]::new(); $failed = $false
    try {
        foreach ($pr in $projects) {
            $root = [string]$pr.root
            $ref = if ($pr.PSObject.Properties['ref'] -and $pr.ref) { [string]$pr.ref } else { 'HEAD' }
            $row = [ordered]@{ project = [string]$pr.name; root = $root; ref = $ref; ref_sha = $null; ref_name = $null; error = $null }
            if (-not (Test-Path -LiteralPath (Join-Path $root '.git'))) {
                $row.error = 'not a git repository'; $rows.Add([pscustomobject]$row); $failed = $true; continue
            }
            $sha = & git -C $root rev-parse --verify -q "$ref^{commit}" 2>$null
            if ($LASTEXITCODE -ne 0 -or -not $sha) {
                $row.error = "ref not found: $ref"; $rows.Add([pscustomobject]$row); $failed = $true; continue
            }
            $row.ref_sha = ([string]$sha).Trim()
            $row.ref_name = ([string](& git -C $root rev-parse --abbrev-ref $ref 2>$null)).Trim()
            try { $rules = Get-Rules $pr.classes }
            catch { $row.error = "bad classes: $($_.Exception.Message)"; $rows.Add([pscustomobject]$row); $failed = $true; continue }
            $sum = [ordered]@{}; foreach ($b in $Buckets + 'unclassified') { $sum[$b] = [int64]0 }
            $unc = @{}; $commits = 0; $binary = 0
            $raw = & git -c core.quotepath=off -C $root log $row.ref_sha --no-merges "--since=$sinceIso" --numstat '--format=%x00%H' 2>&1
            if ($LASTEXITCODE -ne 0) { $row.error = 'git log failed'; $rows.Add([pscustomobject]$row); $failed = $true; continue }
            foreach ($line in $raw) {
                $l = [string]$line
                if ($l.StartsWith([char]0)) { $commits++; continue }
                if ([string]::IsNullOrWhiteSpace($l)) { continue }
                $f = $l.Split("`t", 3)
                if ($f.Count -lt 3) { continue }
                if ($f[0] -eq '-' -or $f[1] -eq '-') { $binary++; continue }
                $n = [int64]$f[0] + [int64]$f[1]
                $path = Resolve-NumstatPath $f[2]
                $b = Get-Bucket $path $rules
                $sum[$b] += $n
                if ($b -eq 'unclassified') {
                    $k = if ($path.Contains('/')) { $path.Substring(0, $path.IndexOf('/') + 1) } else { $path }
                    $unc[$k] = [int64]($(if ($unc.ContainsKey($k)) { $unc[$k] } else { 0 })) + $n
                }
            }
            $merges = [int](& git -C $root rev-list --count --merges "--since=$sinceIso" $row.ref_sha)
            $total = [int64]0; foreach ($v in $sum.Values) { $total += $v }
            $row.commits_counted = $commits
            $row.merges_excluded = $merges
            $row.binary_files_ignored = $binary
            $row.lines = [pscustomobject]$sum
            $row.total_lines = $total
            $row.product_share = if ($total -gt 0) { [math]::Round($sum['product'] / $total, 4) } else { $null }
            $row.product_lines_per_week = [math]::Round($sum['product'] / $days * 7, 1)
            $row.top_unclassified = @($unc.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 5 |
                ForEach-Object { [pscustomobject]@{ prefix = $_.Key; lines = $_.Value } })
            $rows.Add([pscustomobject]$row)
        }
    } finally { [Console]::OutputEncoding = $prevEnc }

    $ranked = @($rows | Where-Object { -not $_.error } |
        Sort-Object @{ Expression = { $_.product_lines_per_week }; Descending = $true }, @{ Expression = { $_.project } })
    $rank = 0
    $ranking = @($ranked | ForEach-Object {
        $rank++
        [pscustomobject]@{ rank = $rank; project = $_.project; product_lines_per_week = $_.product_lines_per_week
            product_share = $_.product_share; product_lines = $_.lines.product; total_lines = $_.total_lines }
    })
    if ($AsJson) {
        [pscustomobject]@{
            schema       = 'fleet/product-throughput-lines/v1'
            authority    = 'DIAGNOSTIC_ONLY_NEVER_A_GATE_OR_TARGET'
            measured_utc = $nowUtc.ToString('yyyy-MM-ddTHH:mm:ssZ')
            since_utc    = $sinceIso
            window_days  = [math]::Round($days, 2)
            class_config = $ClassConfig
            buckets      = @($Buckets + 'unclassified')
            projects     = @($rows)
            ranking      = $ranking
        } | ConvertTo-Json -Depth 6
    } else {
        Write-Output ("=========== PRODUCT SHARE BY CHANGED LINES (since {0}, {1:N1} d) ===========" -f $sinceIso, $days)
        Write-Output ('{0,-4} {1,-16} {2,10} {3,9} {4,9} {5,9} {6,9} {7,9} {8,9} {9,9} {10,8}' -f 'rank', 'project', 'prod/wk', 'product', 'tests', 'tooling', 'paper', 'vendored', 'unclass', 'total', 'share')
        foreach ($r in $ranking) {
            $p = @($rows | Where-Object { $_.project -eq $r.project })[0]
            Write-Output ('{0,-4} {1,-16} {2,10} {3,9} {4,9} {5,9} {6,9} {7,9} {8,9} {9,9} {10,8}' -f $r.rank, $r.project, $r.product_lines_per_week,
                $p.lines.product, $p.lines.tests, $p.lines.'factory-tooling', $p.lines.'coordination-paperwork', $p.lines.'vendored-copies',
                $p.lines.unclassified, $p.total_lines, $(if ($null -ne $p.product_share) { '{0:P1}' -f $p.product_share } else { 'n/a' }))
        }
        foreach ($p in @($rows | Where-Object { $_.error })) { Write-Output ("FAILED {0}: {1}" -f $p.project, $p.error) }
        Write-Output 'DIAGNOSTIC ONLY (metrics/README.md law 1): never a gate, never a target.'
    }
    if ($failed) { exit 4 }
    exit 0
}

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
