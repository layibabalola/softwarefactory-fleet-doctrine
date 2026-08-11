[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9a-fA-F]{40}$')]
    [string]$ExpectedRemoteHead,

    [string]$Remote = 'origin',
    [string]$TargetBranch = 'master',

    [Parameter(Mandatory = $true)]
    [string]$WorktreePath,

    [Parameter(Mandatory = $true)]
    [string]$FeatureBranch
)

$ErrorActionPreference = 'Stop'

function Invoke-Git {
    param(
        [Parameter(Mandatory = $true)][string]$Repository,
        [Parameter(Mandatory = $true)][string[]]$Arguments
    )
    $output = @(& git.exe -C $Repository @Arguments 2>&1)
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Arguments -join ' ') failed with exit $LASTEXITCODE`: $($output -join [Environment]::NewLine)"
    }
    return $output
}

try {
    if ($Remote -notmatch '^[A-Za-z0-9._-]+$') {
        throw 'Remote must contain only letters, numbers, dot, underscore, or hyphen.'
    }
    if ($TargetBranch -notmatch '^[A-Za-z0-9._/-]+$') {
        throw 'TargetBranch contains unsupported characters.'
    }

    $repo = (Resolve-Path -LiteralPath $RepoRoot).Path
    [void](Invoke-Git -Repository $repo -Arguments @('rev-parse', '--git-dir'))
    [void](Invoke-Git -Repository $repo -Arguments @('check-ref-format', '--branch', $FeatureBranch))

    $worktree = [IO.Path]::GetFullPath($WorktreePath)
    $repoPrefix = $repo.TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
    if ($worktree.StartsWith($repoPrefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Publication worktree must be outside the canonical doctrine checkout.'
    }
    if (Test-Path -LiteralPath $worktree) {
        throw "Publication worktree path already exists: $worktree"
    }

    $branchRef = "refs/heads/$FeatureBranch"
    & git.exe -C $repo show-ref --verify --quiet $branchRef
    if ($LASTEXITCODE -eq 0) {
        throw "Publication feature branch already exists: $FeatureBranch"
    }
    if ($LASTEXITCODE -ne 1) {
        throw "Unable to determine whether branch exists: $FeatureBranch"
    }

    $canonicalHead = (@(Invoke-Git -Repository $repo -Arguments @('rev-parse', 'HEAD')))[-1].Trim()
    $canonicalStatus = @(Invoke-Git -Repository $repo -Arguments @('status', '--porcelain=v1'))

    $remoteRef = "refs/heads/$TargetBranch"
    $advertised = @(Invoke-Git -Repository $repo -Arguments @('ls-remote', '--exit-code', $Remote, $remoteRef))
    $remoteHead = (($advertised[-1] -split '\s+')[0]).ToLowerInvariant()
    $expected = $ExpectedRemoteHead.ToLowerInvariant()
    if ($remoteHead -ne $expected) {
        throw "Remote target drifted: expected=$expected actual=$remoteHead ref=$remoteRef"
    }

    $trackingRef = "refs/remotes/$Remote/$TargetBranch"
    [void](Invoke-Git -Repository $repo -Arguments @(
        'fetch', '--no-tags', $Remote, "+${remoteRef}:${trackingRef}"
    ))
    $fetchedHead = (@(Invoke-Git -Repository $repo -Arguments @('rev-parse', $trackingRef)))[-1].Trim().ToLowerInvariant()
    if ($fetchedHead -ne $expected) {
        throw "Fetched target does not match the advertised pin: expected=$expected actual=$fetchedHead"
    }

    $counts = ((@(Invoke-Git -Repository $repo -Arguments @(
        'rev-list', '--left-right', '--count', "$trackingRef...HEAD"
    )))[-1].Trim() -split '\s+')
    $canonicalBehind = [int]$counts[0]
    $canonicalAhead = [int]$counts[1]

    [void](Invoke-Git -Repository $repo -Arguments @(
        'worktree', 'add', '-b', $FeatureBranch, $worktree, $expected
    ))
    $createdHead = (@(Invoke-Git -Repository $worktree -Arguments @('rev-parse', 'HEAD')))[-1].Trim().ToLowerInvariant()
    $createdStatus = @(Invoke-Git -Repository $worktree -Arguments @('status', '--porcelain=v1'))
    if ($createdHead -ne $expected -or $createdStatus.Count -ne 0) {
        throw "Created publication worktree failed verification: head=$createdHead dirty=$($createdStatus.Count)"
    }

    [ordered]@{
        schema = 'clean-doctrine-publication-worktree.v1'
        status = 'READY'
        canonicalRepo = $repo
        canonicalHead = $canonicalHead
        canonicalDirty = ($canonicalStatus.Count -gt 0)
        canonicalDirtyPaths = @($canonicalStatus)
        canonicalAhead = $canonicalAhead
        canonicalBehind = $canonicalBehind
        remote = $Remote
        targetBranch = $TargetBranch
        remoteHead = $remoteHead
        worktree = $worktree
        featureBranch = $FeatureBranch
        worktreeHead = $createdHead
        worktreeDirty = $false
    } | ConvertTo-Json -Depth 5 -Compress
    exit 0
} catch {
    [ordered]@{
        schema = 'clean-doctrine-publication-worktree.v1'
        status = 'BLOCKED'
        error = $_.Exception.Message
    } | ConvertTo-Json -Compress
    exit 2
}
