[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$UsageObserver,
    [string]$Python = 'python'
)

$ErrorActionPreference = 'Stop'
$candidateRoot = Split-Path $PSScriptRoot -Parent
$tempRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
$testDir = Join-Path $tempRoot ('fleet-usage-shadow-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $testDir | Out-Null

try {
    $rawText = & $UsageObserver -Raw 2>$null | Out-String
    $raw = $rawText | ConvertFrom-Json
    $rawPath = Join-Path $testDir 'anthropic.json'
    [IO.File]::WriteAllText($rawPath, $rawText, [Text.UTF8Encoding]::new($false))

    $domainSeed = [Text.Encoding]::UTF8.GetBytes('local-shadow-anthropic-default')
    $domainHash = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($domainSeed)).ToLowerInvariant()
    $domain = 'anthropic:sha256:' + $domainHash
    $snapshot = Join-Path $testDir 'snapshot.json'
    & $Python (Join-Path $candidateRoot 'reference\normalize_capacity.py') `
        --provider anthropic `
        --input $rawPath `
        --quota-domain $domain `
        --observed-at ([DateTimeOffset]::UtcNow.ToString('o')) `
        --output $snapshot
    if ($LASTEXITCODE -ne 0) { throw 'capacity normalization failed' }

    $now = [DateTimeOffset]::UtcNow
    $request = [ordered]@{
        schema = 'fleet-capacity-admission-request/v1'
        request_id = 'shadow-conjugal-' + [guid]::NewGuid().ToString('N')
        project = 'conjugal'
        lane = 'opus'
        subject_digest = 'sha256:' + ('1' * 64)
        role = 'REVIEW'
        priority = 'REQUIRED_REVIEW'
        profile = [ordered]@{
            provider = 'anthropic'
            quota_domain = $domain
            independence_class = 'anthropic-claude'
            requested_model = 'claude-opus-5'
            requested_effort = 'max'
            transport = 'claude-code/2.1.233'
        }
        issued_at = $now.ToString('o')
        expires_at = $now.AddMinutes(2).ToString('o')
        budget = [ordered]@{
            max_wall_seconds = 900
            max_turns = 16
            max_context_tokens = 100000
            window_estimates = [ordered]@{'five-hour'=0.15; weekly=0.02}
        }
        quality_contract = [ordered]@{
            requires_exact_profile = $true
            role_cell_evidence = 'conjugal-opus-max-existing-contract'
        }
        owner_override = $false
    }
    $requestPath = Join-Path $testDir 'request.json'
    [IO.File]::WriteAllText($requestPath, ($request | ConvertTo-Json -Depth 10), [Text.UTF8Encoding]::new($false))
    $decisionText = & $Python (Join-Path $candidateRoot 'reference\fleet_capacity_broker.py') decide `
        --request $requestPath `
        --snapshot $snapshot `
        --policy (Join-Path $candidateRoot 'policy\default-v1.json') `
        --state (Join-Path $testDir 'state.sqlite3')
    if ($LASTEXITCODE -notin @(0,23)) { throw 'broker shadow decision was unevaluable' }
    $decision = $decisionText | ConvertFrom-Json
    [pscustomobject]@{
        five_hour_utilization = $raw.five_hour.utilization
        weekly_utilization = $raw.seven_day.utilization
        decision = $decision.status
        reasons = @($decision.reason_codes)
        lease_issued = $null -ne $decision.lease
        provider_process_launched = $false
    } | ConvertTo-Json -Compress
}
finally {
    $resolved = [IO.Path]::GetFullPath($testDir)
    if (-not $resolved.StartsWith($tempRoot, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'refusing cleanup outside the OS temporary directory'
    }
    Remove-Item -LiteralPath $resolved -Recurse -Force
}
