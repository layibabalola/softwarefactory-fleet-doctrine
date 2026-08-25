[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$script:assertions = 0

function Assert-True([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw "ASSERTION FAILED: $Message" }
    $script:assertions++
}

$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$candidatePath = Join-Path $repo 'ruling-candidates\opus-model-failback-r1.md'
$controlsPath = Join-Path $repo 'ruling-candidates\opus-model-failback-r2-controls.json'
$candidate = [IO.File]::ReadAllText($candidatePath)
$candidateFlat = $candidate -replace '\s+', ' '
$controls = [IO.File]::ReadAllText($controlsPath) | ConvertFrom-Json -Depth 20 -ErrorAction Stop

Assert-True ($controls.schema -ceq 'fleet-exhausted-model-failback-controls.v1') 'schema'
Assert-True ($controls.candidate -ceq 'opus-model-failback-r2') 'candidate identity'
Assert-True ($controls.authority -ceq 'ZERO_AUTHORITY_REPRODUCTION_MATRIX') 'zero authority'
Assert-True ($controls.capacity_observation_max_age_seconds -eq 300) '300-second maximum age'
Assert-True ($controls.hard_capacity_ceiling_pct -eq 100) 'hard 100 percent ceiling'
Assert-True ($controls.cases.Count -eq 15) 'exact control count'

$ids = @($controls.cases | ForEach-Object { [string]$_.id })
Assert-True ((@($ids | Sort-Object -Unique)).Count -eq $ids.Count) 'unique control ids'
foreach ($required in @(
    'positive_exact_fable_exhaustion',
    'wrong_or_alias_fable_model',
    'generic_429_without_exact_fable_text',
    'stale_or_cross_domain_capacity',
    'hard_ceiling_or_conservative_estimate_exceeded',
    'live_provider_lease_or_concurrent_transaction',
    'unconsumed_canary',
    'consumed_canary_not_authority',
    'terminal_retirement_overclaim'
)) {
    Assert-True ($required -cin $ids) "required control $required"
}

foreach ($case in $controls.cases) {
    $names = @($case.PSObject.Properties.Name | Sort-Object)
    Assert-True (($names -join ',') -ceq 'expected,id,mutation,provider_launches,writes') "closed keys $($case.id)"
    Assert-True ($case.writes -eq 0) "zero writes $($case.id)"
    Assert-True ($case.provider_launches -eq 0) "zero launches $($case.id)"
}

$unconsumed = $controls.cases | Where-Object id -CEQ 'unconsumed_canary'
$consumed = $controls.cases | Where-Object id -CEQ 'consumed_canary_not_authority'
Assert-True ($unconsumed.expected -ceq 'HOLD_UNCONSUMED_CANARY') 'unconsumed canary refuses'
Assert-True ($consumed.expected -ceq 'CONTINUE_TO_LATER_GATES_WITH_ZERO_ADMISSION_AUTHORITY') 'consumed canary grants no admission'

Assert-True ($candidate.StartsWith('# Ruling candidate: exhausted-model failback to Opus R2')) 'R2 title'
Assert-True ($candidate.Contains('## Terminal-exhaustion discriminator')) 'discriminator section'
Assert-True ($candidateFlat.Contains("You've reached your Fable 5 limit. Run /usage-credits to continue or switch models with /model.")) 'exact model-scoped result text'
Assert-True ($candidateFlat.Contains('at most 300 seconds old')) 'capacity age bound'
Assert-True ($candidate.Contains('retired-by-directive')) 'truthful terminal retirement semantics'
Assert-True ($candidate.Contains('unconsumed canary')) 'canary acceptance control'

[Console]::Out.WriteLine("PASS SUITE - $script:assertions assertions; ZERO_PROVIDER; ZERO_WRITES")
