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
(adds + deletes from `git log --numstat`; merge commits excluded; binary files: lines not counted, counted separately as binary_files; their bytes are counted) per project over the window, bucketed into product / tests / factory-tooling /
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

.PARAMETER Root
Alias -Repo. The repo to measure. Classic mode: required classifier via -ProductPath. Line mode: when given,
measures THIS checkout instead of the config's root, using the config entry whose root matches it, or the
entry named by -Project. Refuses (exit 4) when neither exists. Any project can measure itself:
  pwsh -File tools/Get-ProductThroughput.ps1 -Lines -Repo C:\code\X -Project dng -Days 14 -AsJson

.PARAMETER NoBytes
Line mode: skip the second `git log -p` pass (changed-BYTES column). Bytes are on by default: line counts
hide mega-line paperwork (one 62 KB packet state-line rewrite is 2 lines but ~125 KB).

.PARAMETER At
Line mode: walk this commit instead of the project's configured ref, so a published row can be
re-derived after the branch moves. 'name=sha' entries (one per project, comma-separated or repeated),
or one bare sha when exactly one project is selected. An unknown project name or an unresolvable sha
is FAILED (exit 4), never a silent fallback to the configured ref.

.PARAMETER Until
Line mode window END (default: now, UTC). Same explicit-offset rule as -Since. With -At and -Since,
it pins a row completely: commits after -Until are excluded by committer date (git log --until).

.PARAMETER AsRows
Line mode: print one JSON line per measured project in the metrics/product-share-lines.jsonl row
schema (with until_utc and the exact reproducing `command`), for appending to that file.
Every row's command carries -At <ref_sha> -Since -Until, whatever the run was given, so re-running
it at the same classifier_sha256 reproduces the row's numbers.

.PARAMETER RunId
Line mode -AsRows: the run_id stamped on every row (default product-share-lines-<until>).

.PARAMETER Since
Window start, both modes (alias of the window is -Days/-WindowDays). MUST carry an explicit offset ('2026-09-27T00:00:00Z' or '...-05:00'):
a naive timestamp is read as local time and silently moves the window edge (ruling candidate
product-share-is-the-fixpoint-instrument-r1 §4.4). Default: now (UTC) minus -WindowDays.

.EXAMPLE
pwsh -File tools/Get-ProductThroughput.ps1 -Root C:\repo -ProductPath 'src/' -MaxAgeDays 7

.EXAMPLE
pwsh -File tools/Get-ProductThroughput.ps1 -Lines -WindowDays 14 -AsJson

.EXAMPLE
pwsh -File tools/Get-ProductThroughput.ps1 -Lines -AsRows -Project conjugal -At <sha> -Since 2026-10-02T16:56:44Z -Until 2026-10-16T16:56:44Z

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
    [Alias('Repo')][string]$Root = (Get-Location).Path,
    [string[]]$CoordinationPath = @(),
    [Alias('Days')][int]$WindowDays = 30,
    [int]$MaxAgeDays = 7,
    [Alias('Json')][switch]$AsJson,
    [switch]$Lines,
    [string]$ClassConfig = (Join-Path $PSScriptRoot 'product-throughput-classes.json'),
    [string[]]$Project = @(),
    [string]$Since = '',
    [switch]$NoBytes,
    [string[]]$At = @(),
    [string]$Until = '',
    [switch]$AsRows,
    [string]$RunId = ''
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$RepoArgGiven = $PSBoundParameters.ContainsKey('Root')
$SinceArgGiven = -not [string]::IsNullOrWhiteSpace($Since)

if ($Lines) {
    $Buckets = @('product', 'tests', 'vendored-copies', 'factory-tooling', 'coordination-paperwork')
    $measuredUtc = (Get-Date).ToUniversalTime()
    $nowUtc = $measuredUtc
    if (-not [string]::IsNullOrWhiteSpace($Until)) {
        if ($Until -notmatch '(Z|[+-]\d\d:?\d\d)$') {
            Write-Output "FAILED: -Until '$Until' has no explicit UTC offset; refusing to guess the window edge."; exit 4
        }
        $nowUtc = ([datetimeoffset]::Parse($Until, [Globalization.CultureInfo]::InvariantCulture)).UtcDateTime
    }
    # Whole seconds: the edges are recorded at second precision, so the measured window must be too.
    $nowUtc = [datetime]::new($nowUtc.Ticks - ($nowUtc.Ticks % [TimeSpan]::TicksPerSecond), [DateTimeKind]::Utc)
    $untilIso = $nowUtc.ToString('yyyy-MM-ddTHH:mm:ssZ')
    if ([string]::IsNullOrWhiteSpace($Since)) {
        $sinceUtc = $nowUtc.AddDays(-$WindowDays)
    } else {
        if ($Since -notmatch '(Z|[+-]\d\d:?\d\d)$') {
            Write-Output "FAILED: -Since '$Since' has no explicit UTC offset; refusing to guess the window edge."; exit 4
        }
        $sinceUtc = ([datetimeoffset]::Parse($Since, [Globalization.CultureInfo]::InvariantCulture)).UtcDateTime
    }
    $sinceIso = $sinceUtc.ToString('yyyy-MM-ddTHH:mm:ssZ')
    $sinceUtc = [datetimeoffset]::Parse($sinceIso, [Globalization.CultureInfo]::InvariantCulture).UtcDateTime
    if ($sinceUtc -ge $nowUtc) { Write-Output "FAILED: -Since $sinceIso is not before -Until $untilIso"; exit 4 }
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
    $atMap = @{}
    foreach ($e in @($At | ForEach-Object { $_ -split ',' } | Where-Object { $_ } | ForEach-Object { $_.Trim() })) {
        if ($e.Contains('=')) {
            $k, $v = $e.Split('=', 2)
            if (@($projects | Where-Object { $_.name -eq $k }).Count -eq 0) { Write-Output "FAILED: -At names '$k', which is not a selected project"; exit 4 }
            $atMap[$k] = $v
        } elseif ($projects.Count -eq 1) {
            $atMap[[string]$projects[0].name] = $e
        } else {
            Write-Output "FAILED: a bare -At '$e' needs exactly one -Project; use name=sha"; exit 4
        }
    }
    # classifier identity: sha256 of the LF-normalised bytes (a CRLF checkout hashes as the committed blob)
    $cfgBytes = [IO.File]::ReadAllBytes((Resolve-Path -LiteralPath $ClassConfig).Path)
    $lf = [Collections.Generic.List[byte]]::new($cfgBytes.Length)
    for ($i = 0; $i -lt $cfgBytes.Length; $i++) { if (-not ($cfgBytes[$i] -eq 13 -and $i + 1 -lt $cfgBytes.Length -and $cfgBytes[$i + 1] -eq 10)) { $lf.Add($cfgBytes[$i]) } }
    $classifierSha = -join ([Security.Cryptography.SHA256]::Create().ComputeHash($lf.ToArray()) | ForEach-Object { $_.ToString('x2') })

    function Get-NormPath([string]$p) {
        try { $p = [IO.Path]::GetFullPath($p) } catch { }
        return (($p -replace '\\', '/').TrimEnd('/')).ToLowerInvariant()
    }
    # -Repo <path>: measure ANY repo checkout. Classes come from the config entry whose root is that
    # repo, or from the entry named by -Project (applied to the -Repo path). No entry = refuse (exit 4):
    # the classifier is required, never guessed (rule A).
    if ($RepoArgGiven) {
        $topRaw = & git -C $Root rev-parse --show-toplevel 2>$null
        if ($LASTEXITCODE -ne 0 -or -not $topRaw) { Write-Output "FAILED: -Repo is not a git repository: $Root"; exit 4 }
        $repoTop = ([string]$topRaw).Trim()
        if ($wanted.Count -gt 0) { $tmpl = $projects[0] }
        else {
            # compare through git's own toplevel so 8.3 short names / junctions / trailing slashes do not defeat the match
            $hit = @($projects | Where-Object {
                $cr = Get-NormPath $_.root
                $gt = if (Test-Path -LiteralPath $_.root) { [string](& git -C $_.root rev-parse --show-toplevel 2>$null) } else { '' }
                $cr -eq (Get-NormPath $repoTop) -or $cr -eq (Get-NormPath $Root) -or ($gt -and (Get-NormPath $gt) -eq (Get-NormPath $repoTop)) })
            if ($hit.Count -eq 0) {
                Write-Output "FAILED: no class entry in the config has root '$repoTop'; add one, or pass -Project <name> to apply that project's classes to this repo."; exit 4
            }
            $tmpl = $hit[0]
        }
        $tmplRef = if ($tmpl.PSObject.Properties['ref'] -and $tmpl.ref) { [string]$tmpl.ref } else { 'HEAD' }
        $projects = @([pscustomobject]@{ name = [string]$tmpl.name; root = $repoTop; ref = $tmplRef; classes = $tmpl.classes })
    }

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
    # git stdout as BYTES (a temp file, never a PowerShell string: strings drop CRs and mangle non-UTF-8).
    function Get-GitBytes([string]$repo, [string[]]$gitArgs) {
        $tmp = [IO.Path]::GetTempFileName()
        try {
            & git -c core.quotepath=off -C $repo @gitArgs "--output=$tmp" 2>$null
            if ($LASTEXITCODE -ne 0) { return $null }
            return , [IO.File]::ReadAllBytes($tmp)
        } finally { Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue }
    }
    function Split-NulTokens([byte[]]$bytes) {
        $out = [Collections.Generic.List[string]]::new(); $pos = 0; $n = $bytes.Length
        while ($pos -lt $n) {
            $e = [Array]::IndexOf[byte]($bytes, [byte]0, $pos)
            if ($e -lt 0) { $e = $n }
            $out.Add([Text.Encoding]::UTF8.GetString($bytes, $pos, $e - $pos)); $pos = $e + 1
        }
        return , $out
    }

    $prevEnc = [Console]::OutputEncoding
    [Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
    $rows = [Collections.Generic.List[object]]::new(); $failed = $false
    try {
        foreach ($pr in $projects) {
            $repoRoot = [string]$pr.root
            $ref = if ($pr.PSObject.Properties['ref'] -and $pr.ref) { [string]$pr.ref } else { 'HEAD' }
            if ($atMap.ContainsKey([string]$pr.name)) { $ref = [string]$atMap[[string]$pr.name] }
            $row = [ordered]@{ project = [string]$pr.name; root = $repoRoot; ref = $ref; ref_sha = $null; ref_name = $null; error = $null }
            if (-not (Test-Path -LiteralPath (Join-Path $repoRoot '.git'))) {
                $row.error = 'not a git repository'; $rows.Add([pscustomobject]$row); $failed = $true; continue
            }
            $sha = & git -C $repoRoot rev-parse --verify -q "$ref^{commit}" 2>$null
            if ($LASTEXITCODE -ne 0 -or -not $sha) {
                $row.error = "ref not found: $ref"; $rows.Add([pscustomobject]$row); $failed = $true; continue
            }
            $row.ref_sha = ([string]$sha).Trim()
            # A pinned -At sha has no symbolic name: rev-parse --abbrev-ref prints nothing (or the sha); record the input.
            $abbrev = & git -C $repoRoot rev-parse --abbrev-ref $ref 2>$null
            $row.ref_name = if ($LASTEXITCODE -eq 0 -and $abbrev) { ([string]$abbrev).Trim() } else { $ref }
            try { $rules = Get-Rules $pr.classes }
            catch { $row.error = "bad classes: $($_.Exception.Message)"; $rows.Add([pscustomobject]$row); $failed = $true; continue }
            $sum = [ordered]@{}; foreach ($b in $Buckets + 'unclassified') { $sum[$b] = [int64]0 }
            $unc = @{}; $commits = 0; $binary = 0
            $cc = [ordered]@{ product = 0; tests = 0; 'paperwork-only' = 0; 'tooling-only' = 0; 'paperwork-and-tooling' = 0; other = 0 }
            $bytes = $null; $bytesTotal = [int64]0

            # PASS 1: `git log --raw --numstat -z` read as BYTES and split on NUL, so a path is never parsed out of
            # prose (a ' and ' or a tab in a name cannot move a file between buckets). Per commit: raw entries
            # (old/new blob ids, path; a rename has old and new paths) then numstat entries in the same order
            # ('-' '-' = binary). Lines, commit classes and binary sizes come from here.
            $b1 = Get-GitBytes $repoRoot @('log', $row.ref_sha, '--no-merges', "--since=$sinceIso", "--until=$untilIso", '--raw', '--numstat', '-z', '--no-abbrev', '--format=%x01%H')
            if ($null -eq $b1) { $row.error = 'git log failed'; $rows.Add([pscustomobject]$row); $failed = $true; continue }
            $toks = Split-NulTokens $b1
            $commitFiles = [Collections.Generic.List[object]]::new(); $commitShas = [Collections.Generic.List[string]]::new()
            $cur = $null; $ni = 0; $bad = $null; $ti = 0
            while ($ti -lt $toks.Count -and -not $bad) {
                $t = $toks[$ti]; $ti++
                if ($t.StartsWith([char]1)) {
                    $cur = [Collections.Generic.List[object]]::new(); $commitFiles.Add($cur); $commitShas.Add($t.Substring(1).Trim()); $ni = 0; $commits++; continue
                }
                $t2 = $t.TrimStart("`n")
                if ($t2 -eq '') { continue }
                if ($null -eq $cur) { $bad = "token before the first commit: $t2"; break }
                if ($t2.StartsWith(':')) {
                    $meta = $t2.Split(' ')
                    if ($meta.Count -lt 5) { $bad = "bad raw entry: $t2"; break }
                    $st = $meta[4]
                    if (($st.StartsWith('R') -or $st.StartsWith('C')) -and $ti + 1 -lt $toks.Count) { $path = $toks[$ti + 1]; $ti += 2 }
                    else { $path = $toks[$ti]; $ti++ }
                    $cur.Add([pscustomobject]@{ path = $path; bucket = (Get-Bucket $path $rules); old = $meta[2]; new = $meta[3]; n = $null; binary = $false })
                    continue
                }
                $nm = [regex]::Match($t2, '^(\d+|-)\t(\d+|-)\t(.*)$', 'Singleline')
                if ($nm.Success) {
                    $np = $nm.Groups[3].Value
                    if ($np -eq '' -and $ti + 1 -lt $toks.Count) { $np = $toks[$ti + 1]; $ti += 2 }
                    if ($ni -ge $cur.Count -or $cur[$ni].path -cne $np) { $bad = "numstat entry '$np' does not match the raw entry at that position"; break }
                    $f = $cur[$ni]; $ni++
                    if ($nm.Groups[1].Value -eq '-' -or $nm.Groups[2].Value -eq '-') { $f.binary = $true } else { $f.n = [int64]$nm.Groups[1].Value + [int64]$nm.Groups[2].Value }
                    continue
                }
                $bad = "unrecognised token: $t2"
            }
            if ($bad) { $row.error = "unparseable git log -z output: $bad"; $rows.Add([pscustomobject]$row); $failed = $true; continue }
            foreach ($cf in $commitFiles) {
                $touched = @{}
                foreach ($f in $cf) {
                    $touched[$f.bucket] = $true
                    if ($f.binary) { if ($f.old -ne $f.new) { $binary++ }; continue }   # identical blob ids = a pure rename/mode change: nothing changed
                    $sum[$f.bucket] += $f.n
                    if ($f.bucket -eq 'unclassified') {
                        $k = if ($f.path.Contains('/')) { $f.path.Substring(0, $f.path.IndexOf('/') + 1) } else { $f.path }
                        $unc[$k] = [int64]($(if ($unc.ContainsKey($k)) { $unc[$k] } else { 0 })) + $f.n
                    }
                }
                if ($touched.ContainsKey('product')) { $cc['product']++ }
                elseif ($touched.ContainsKey('tests')) { $cc['tests']++ }
                else {
                    $pw = $touched.ContainsKey('coordination-paperwork'); $tl = $touched.ContainsKey('factory-tooling')
                    $rest = @($touched.Keys | Where-Object { $_ -ne 'coordination-paperwork' -and $_ -ne 'factory-tooling' }).Count
                    if ($rest -gt 0 -or (-not $pw -and -not $tl)) { $cc['other']++ }
                    elseif ($pw -and $tl) { $cc['paperwork-and-tooling']++ }
                    elseif ($pw) { $cc['paperwork-only']++ } else { $cc['tooling-only']++ }
                }
            }

            # PASS 2 (BYTES): the RAW byte length of every added + removed line, from `git log -p` read as bytes
            # (PowerShell string capture drops CRs, splits on a lone CR and turns invalid UTF-8 into U+FFFD).
            # A line costs its bytes after the +/- marker plus its LF, which is the raw line length with the
            # marker and without the LF; a final line with no EOL (`\ No newline at end of file`) has no LF.
            # No path is read from the patch: the Nth `diff --git` of a commit is the Nth raw entry of pass 1
            # (same diff queue), so quoting or odd names cannot misplace bytes. A binary file counts old size +
            # new size from its blob ids (a replace is a removal plus an addition, even at equal size).
            if (-not $NoBytes) {
                $bsum = [ordered]@{}; foreach ($b in $Buckets + 'unclassified') { $bsum[$b] = [int64]0 }
                $utf8 = [Text.UTF8Encoding]::new($false)
                $b2 = Get-GitBytes $repoRoot @('log', $row.ref_sha, '--no-merges', "--since=$sinceIso", "--until=$untilIso", '-p', '-U0', '--no-ext-diff', '--no-textconv', '--no-color', '--format=%x00%H')
                if ($null -eq $b2) { $row.error = 'git log -p failed'; $rows.Add([pscustomobject]$row); $failed = $true; continue }
                $buf = $b2; $n = $buf.Length; $pos = 0
                $ci = -1; $fi = -1; $inHunk = $false; $curBucket = 'unclassified'; $lastBucket = $null; $desync = $null
                while ($pos -lt $n) {
                    $e = [Array]::IndexOf[byte]($buf, [byte]10, $pos)
                    if ($e -lt 0) { $e = $n }
                    $len = $e - $pos
                    $c = if ($len -gt 0) { $buf[$pos] } else { -1 }
                    if ($inHunk) {
                        if ($c -eq 43 -or $c -eq 45) { $bsum[$curBucket] += $len; $lastBucket = $curBucket; $pos = $e + 1; continue }
                        if ($c -eq 92) {   # '\ No newline at end of file': the previous +/- line had no LF
                            if ($null -ne $lastBucket) { $bsum[$lastBucket] -= 1; $lastBucket = $null }
                            $pos = $e + 1; continue
                        }
                    }
                    $lastBucket = $null
                    if ($c -eq 0) {
                        $inHunk = $false; $ci++; $fi = -1
                        if ($ci -ge $commitShas.Count -or $commitShas[$ci] -ne $utf8.GetString($buf, $pos + 1, $len - 1).Trim()) { $desync = "commit $ci"; break }
                    } elseif ($c -eq 100 -and $len -ge 11 -and $utf8.GetString($buf, $pos, 11) -ceq 'diff --git ') {
                        $inHunk = $false; $fi++
                        if ($ci -lt 0 -or $fi -ge $commitFiles[$ci].Count) { $desync = "file $fi of commit $ci"; break }
                        $curBucket = $commitFiles[$ci][$fi].bucket
                    } elseif ($c -eq 64) { $inHunk = $true }
                    else { $inHunk = $false }
                    $pos = $e + 1
                }
                if (-not $desync) {
                    if ($ci + 1 -ne $commitFiles.Count) { $desync = "commit count $($ci + 1) vs $($commitFiles.Count)" }
                }
                if ($desync) { $row.error = "bytes pass out of step with the file list: $desync"; $rows.Add([pscustomobject]$row); $failed = $true; continue }
                # binary files: sizes of the blobs (all-zero id = absent = 0 bytes)
                $bins = @($commitFiles | ForEach-Object { $_ } | Where-Object { $_.binary -and $_.old -ne $_.new })
                if ($bins.Count -gt 0) {
                    $sizes = @{}
                    foreach ($id in @($bins | ForEach-Object { $_.old; $_.new } | Where-Object { $_ -notmatch '^0+$' } | Sort-Object -Unique)) {
                        $sz = & git -C $repoRoot cat-file -s $id 2>$null
                        if ($LASTEXITCODE -eq 0 -and $sz) { $sizes[$id] = [int64]([string]$sz).Trim() }
                    }
                    foreach ($f in $bins) {
                        $ob = if ($sizes.ContainsKey($f.old)) { $sizes[$f.old] } else { 0 }
                        $nb = if ($sizes.ContainsKey($f.new)) { $sizes[$f.new] } else { 0 }
                        $bsum[$f.bucket] += $ob + $nb
                    }
                }
                foreach ($v in $bsum.Values) { $bytesTotal += $v }
                $bytes = [pscustomobject]$bsum
            }

            $merges = [int](& git -C $repoRoot rev-list --count --merges "--since=$sinceIso" "--until=$untilIso" $row.ref_sha)
            $total = [int64]0; foreach ($v in $sum.Values) { $total += $v }
            $row.commits_counted = $commits
            $row.merges_excluded = $merges
            $row.binary_files = $binary                  # files git calls binary: their LINES are not counted; their BYTES are (unless -NoBytes)
            $row.binary_files_ignored = $binary          # DEPRECATED alias of binary_files, kept for existing readers; the name predates the bytes column
            $row.lines = [pscustomobject]$sum
            $row.total_lines = $total
            $row.product_share = if ($total -gt 0) { [math]::Round($sum['product'] / $total, 4) } else { $null }
            # additive fields (2026-10-16): the line metric hides mega-line paperwork, bytes do not
            $row.product_share_lines = $row.product_share
            $row.bytes = $bytes
            $row.total_bytes = if ($null -ne $bytes) { $bytesTotal } else { $null }
            $row.product_share_bytes = if ($null -ne $bytes -and $bytesTotal -gt 0) { [math]::Round($bytes.product / $bytesTotal, 4) } else { $null }
            $row.commit_classes = [pscustomobject]$cc
            $row.commits_touching_product = $cc['product']
            $row.commits_paperwork_tooling_only = $cc['paperwork-only'] + $cc['tooling-only'] + $cc['paperwork-and-tooling']
            $row.commits_paperwork_only = $cc['paperwork-only']
            $row.paperwork_tooling_commits_per_product_commit = if ($cc['product'] -gt 0) { [math]::Round($row.commits_paperwork_tooling_only / $cc['product'], 2) } else { $null }
            $row.paperwork_only_commits_per_product_commit = if ($cc['product'] -gt 0) { [math]::Round($cc['paperwork-only'] / $cc['product'], 2) } else { $null }
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
            product_share = $_.product_share; product_lines = $_.lines.product; total_lines = $_.total_lines
            product_share_lines = $_.product_share_lines; product_share_bytes = $_.product_share_bytes
            product_bytes = $(if ($null -ne $_.bytes) { $_.bytes.product } else { $null }); total_bytes = $_.total_bytes
            commits_touching_product = $_.commits_touching_product; commits_paperwork_tooling_only = $_.commits_paperwork_tooling_only
            paperwork_tooling_commits_per_product_commit = $_.paperwork_tooling_commits_per_product_commit }
    })
    if ($AsRows) {
        $rid = if ($RunId) { $RunId } else { "product-share-lines-$untilIso" }
        foreach ($r in $ranking) {
            $p = @($rows | Where-Object { $_.project -eq $r.project })[0]
            $cmd = "pwsh -NoProfile -File tools/Get-ProductThroughput.ps1 -Lines -AsRows -Project $($p.project) -At $($p.ref_sha) -Since $sinceIso -Until $untilIso"
            [ordered]@{
                ts = $measuredUtc.ToString('yyyy-MM-ddTHH:mm:ssZ'); run_id = $rid; schema = 'fleet/product-throughput-lines/v1'
                project = $p.project; ref = $p.ref; ref_name = $p.ref_name; ref_sha = $p.ref_sha
                since_utc = $sinceIso; until_utc = $untilIso; window_days = [math]::Round($days, 2)
                classifier_sha256 = $classifierSha; commits_counted = $p.commits_counted; merges_excluded = $p.merges_excluded
                binary_files_ignored = $p.binary_files_ignored; lines = $p.lines; total_lines = $p.total_lines
                product_share = $p.product_share; product_lines_per_week = $p.product_lines_per_week; rank = $r.rank
                top_unclassified = @($p.top_unclassified); error = $null
                # additive (bytes + commit classes, E3): absent keys never break an existing reader
                binary_files = $p.binary_files; product_share_lines = $p.product_share_lines
                bytes = $p.bytes; total_bytes = $p.total_bytes; product_share_bytes = $p.product_share_bytes
                commit_classes = $p.commit_classes; commits_touching_product = $p.commits_touching_product
                commits_paperwork_tooling_only = $p.commits_paperwork_tooling_only; commits_paperwork_only = $p.commits_paperwork_only
                paperwork_tooling_commits_per_product_commit = $p.paperwork_tooling_commits_per_product_commit
                paperwork_only_commits_per_product_commit = $p.paperwork_only_commits_per_product_commit
                command = $cmd
            } | ConvertTo-Json -Depth 6 -Compress
        }
        foreach ($p in @($rows | Where-Object { $_.error })) { [Console]::Error.WriteLine("FAILED {0}: {1}" -f $p.project, $p.error) }
    } elseif ($AsJson) {
        [pscustomobject]@{
            schema       = 'fleet/product-throughput-lines/v1'
            authority    = 'DIAGNOSTIC_ONLY_NEVER_A_GATE_OR_TARGET'
            measured_utc = $measuredUtc.ToString('yyyy-MM-ddTHH:mm:ssZ')
            since_utc    = $sinceIso
            until_utc    = $untilIso
            window_days  = [math]::Round($days, 2)
            classifier_sha256 = $classifierSha
            class_config = $ClassConfig
            buckets      = @($Buckets + 'unclassified')
            projects     = @($rows)
            ranking      = $ranking
        } | ConvertTo-Json -Depth 6
    } else {
        Write-Output ("=========== PRODUCT SHARE BY CHANGED LINES (since {0}, {1:N1} d) ===========" -f $sinceIso, $days)
        Write-Output ('{0,-4} {1,-16} {2,10} {3,9} {4,9} {5,9} {6,9} {7,9} {8,9} {9,9} {10,8} {11,8} {12,7}' -f 'rank', 'project', 'prod/wk', 'product', 'tests', 'tooling', 'paper', 'vendored', 'unclass', 'total', 'share', 'bshare', 'pc/ac')
        foreach ($r in $ranking) {
            $p = @($rows | Where-Object { $_.project -eq $r.project })[0]
            Write-Output ('{0,-4} {1,-16} {2,10} {3,9} {4,9} {5,9} {6,9} {7,9} {8,9} {9,9} {10,8} {11,8} {12,7}' -f $r.rank, $r.project, $r.product_lines_per_week,
                $p.lines.product, $p.lines.tests, $p.lines.'factory-tooling', $p.lines.'coordination-paperwork', $p.lines.'vendored-copies',
                $p.lines.unclassified, $p.total_lines, $(if ($null -ne $p.product_share) { '{0:P1}' -f $p.product_share } else { 'n/a' }),
                $(if ($null -ne $p.product_share_bytes) { '{0:P2}' -f $p.product_share_bytes } else { 'n/a' }),
                $(if ($null -ne $p.paperwork_tooling_commits_per_product_commit) { $p.paperwork_tooling_commits_per_product_commit } else { 'n/a' }))
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

$sinceClassic = (Get-Date).ToUniversalTime().AddDays(-$WindowDays).ToString('yyyy-MM-dd')
if ($SinceArgGiven) {
    if ($Since -notmatch '(Z|[+-]\d\d:?\d\d)$') { Write-Output "FAILED: -Since '$Since' has no explicit UTC offset; refusing to guess the window edge."; exit 4 }
    $sinceClassic = ([datetimeoffset]::Parse($Since, [Globalization.CultureInfo]::InvariantCulture)).UtcDateTime.ToString('yyyy-MM-ddTHH:mm:ssZ')
}
$raw = & git -C $Root log --all --since=$sinceClassic --name-only --format="%x00%H%x1f%cI" 2>&1
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
