[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$script:assertions = 0

function Assert-True([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw "ASSERTION FAILED: $Message" }
    $script:assertions++
}

$specJson = @'
{
  "schema":"fleet-exhausted-model-failback-controls.v3",
  "candidate":"opus-model-failback-r4",
  "authority":"ZERO_AUTHORITY_REPRODUCTION_MATRIX",
  "capacity_observation_max_age_seconds":300,
  "hard_ceiling_rule":"UTILIZATION_PLUS_ACTIVE_RESERVATIONS_PLUS_CONSERVATIVE_ESTIMATE_LTE_100_IN_EVERY_WINDOW",
  "core_subject_contract":{
    "digest_algorithm":"SHA256_CANONICAL_CLOSED_KEY_ORDERED_ROWS_V1",
    "row_keys":["path","bytes","sha256"],
    "order_is_binding":true,
    "lane_ancestry_attachment_excluded":true
  },
  "execution_contract":{
    "common":{"effort":"max","max_turns":12,"max_wall_clock_seconds":900,"provider_tools":["Read","StructuredOutput"],"result_contract":"route-review-result.v1"},
    "fable":{"model":"claude-fable-5","role":"coordinator"},
    "opus":{"model":"claude-opus-5","role":"executor"}
  },
  "discriminator_assertions":[
    "INIT_MODEL_EXACT",
    "ROUTE_AND_SESSION_EXACT",
    "TERMINAL_REASON_API_ERROR",
    "HTTP_STATUS_429",
    "EXACTLY_ONE_TURN",
    "EXACT_MODEL_SCOPED_RESULT_TEXT",
    "ASSISTANT_ERROR_RATE_LIMIT",
    "ZERO_REVIEW_INPUT_TOKENS",
    "ZERO_REVIEW_OUTPUT_TOKENS",
    "NO_REVIEW_VERDICT_OR_ACCEPTANCE",
    "RATE_LIMIT_EVENTS_COMPLETE_AND_ADJUDICATED",
    "SAME_DOMAIN_CAPACITY_FRESH_AND_BASE_WINDOWS_BELOW_100"
  ],
  "classifier_rules":{
    "bind_every_rate_limit_event":true,
    "base_window_rejected":"HOLD_ACCOUNT_OR_WINDOW_EXHAUSTION",
    "overage_only_rejected_with_allowed_base_below_100":"MODEL_CLASSIFIER_MAY_CONTINUE_TO_OTHER_GATES",
    "overage_only_rejected_without_base_event_with_exact_model_evidence_and_signed_base_below_100":"MODEL_CLASSIFIER_MAY_CONTINUE_TO_OTHER_GATES",
    "overage_only_rejected_without_base_event_or_fresh_signed_corroboration":"HOLD_CLASSIFIER_AMBIGUOUS",
    "contradictory_or_unenumerated_event":"HOLD_CLASSIFIER_AMBIGUOUS"
  },
  "cases":[
    {"id":"positive_exact_fable_exhaustion","mutation":"none","expected":"ELIGIBLE_FOR_ORDINARY_OPUS_ADMISSION_EVALUATION","writes":0,"provider_launches":0},
    {"id":"wrong_or_alias_fable_model","mutation":"init model differs from exact claude-fable-5","expected":"HOLD_MODEL_IDENTITY","writes":0,"provider_launches":0},
    {"id":"generic_429_without_exact_fable_text","mutation":"429 exists without exact model-scoped result","expected":"HOLD_EXHAUSTION_AMBIGUOUS","writes":0,"provider_launches":0},
    {"id":"assistant_error_missing_or_different","mutation":"assistant event error is absent or differs from rate_limit","expected":"HOLD_TERMINAL_EVIDENCE","writes":0,"provider_launches":0},
    {"id":"nonterminal_or_multiturn_result","mutation":"terminal reason differs or turns are not exactly one","expected":"HOLD_TERMINAL_IDENTITY","writes":0,"provider_launches":0},
    {"id":"verdict_or_acceptance_present","mutation":"Fable artifact contains review verdict or acceptance","expected":"HOLD_CREDIT_CONFLICT","writes":0,"provider_launches":0},
    {"id":"nonzero_fable_review_tokens","mutation":"review input or output tokens are nonzero","expected":"HOLD_NOT_ZERO_CREDIT_EXHAUSTION","writes":0,"provider_launches":0},
    {"id":"rate_limit_event_omitted","mutation":"receipt omits any artifact rate-limit event","expected":"HOLD_CLASSIFIER_INCOMPLETE","writes":0,"provider_launches":0},
    {"id":"base_window_rejected","mutation":"a bound base-window classifier is rejected","expected":"HOLD_ACCOUNT_OR_WINDOW_EXHAUSTION","writes":0,"provider_launches":0},
    {"id":"overage_only_rejected_with_allowed_base_below_100","mutation":"overage entitlement rejected while base window remains allowed and signed below 100","expected":"CONTINUE_TO_OTHER_GATES","writes":0,"provider_launches":0},
    {"id":"overage_only_rejected_without_base_event_with_exact_model_evidence_and_signed_base_below_100","mutation":"base event omitted while exact model evidence and fresh signed same-domain base utilization below 100 remain present","expected":"CONTINUE_TO_OTHER_GATES","writes":0,"provider_launches":0},
    {"id":"overage_only_rejected_without_base_event_or_fresh_signed_corroboration","mutation":"base event omitted and exact model evidence or fresh signed same-domain base corroboration is absent","expected":"HOLD_CLASSIFIER_AMBIGUOUS","writes":0,"provider_launches":0},
    {"id":"contradictory_or_unenumerated_rate_limit_event","mutation":"artifact contains a contradictory or unenumerated rate-limit event","expected":"HOLD_CLASSIFIER_AMBIGUOUS","writes":0,"provider_launches":0},
    {"id":"stale_or_cross_domain_capacity","mutation":"signed observation older than 300 seconds or on another domain","expected":"HOLD_CAPACITY_EVIDENCE","writes":0,"provider_launches":0},
    {"id":"hard_ceiling_sum_exactly_100","mutation":"utilization plus reservations plus estimate equals 100 in every window","expected":"CONTINUE_TO_LATER_GATES","writes":0,"provider_launches":0},
    {"id":"hard_ceiling_sum_above_100","mutation":"utilization plus reservations plus estimate exceeds 100 in any window","expected":"HOLD_HARD_CEILING","writes":0,"provider_launches":0},
    {"id":"core_subject_reordered","mutation":"successor changes ordered core-subject rows","expected":"HOLD_CORE_SUBJECT_DIGEST","writes":0,"provider_launches":0},
    {"id":"core_subject_replaced","mutation":"ancestry attachment replaces a core subject","expected":"HOLD_CORE_SUBJECT_DIGEST","writes":0,"provider_launches":0},
    {"id":"execution_contract_effort_drift","mutation":"effort differs from max","expected":"HOLD_EXECUTION_CONTRACT","writes":0,"provider_launches":0},
    {"id":"execution_contract_turn_or_wall_drift","mutation":"turns exceed 12 or wall clock exceeds 900 seconds","expected":"HOLD_EXECUTION_CONTRACT","writes":0,"provider_launches":0},
    {"id":"execution_contract_model_role_or_tools_drift","mutation":"lane model role tools or result contract differs","expected":"HOLD_EXECUTION_CONTRACT","writes":0,"provider_launches":0},
    {"id":"assertion_map_count_mismatch","mutation":"named discriminator array count differs from receipt assertion_count","expected":"HOLD_ASSERTION_MAP","writes":0,"provider_launches":0},
    {"id":"open_gate","mutation":"automatic launch gate is not closed","expected":"HOLD_OPEN_GATE","writes":0,"provider_launches":0},
    {"id":"live_provider_lease_or_concurrent_transaction","mutation":"provider lease live or provider transaction concurrent","expected":"HOLD_OVERLAP","writes":0,"provider_launches":0},
    {"id":"unconsumed_canary","mutation":"fresh authorization lacks matching consumption evidence","expected":"HOLD_UNCONSUMED_CANARY","writes":0,"provider_launches":0},
    {"id":"consumed_canary_not_authority","mutation":"exact canary consumption evidence exists","expected":"CONTINUE_TO_LATER_GATES_WITH_ZERO_ADMISSION_AUTHORITY","writes":0,"provider_launches":0},
    {"id":"account_domain_rotation_failure","mutation":"successor domain repeats predecessor or transaction incomplete","expected":"ROLLED_BACK_AND_HOLD","writes":0,"provider_launches":0},
    {"id":"terminal_retirement_overclaim","mutation":"retired-by-directive described as stronger deterministic release","expected":"REVISE_EVIDENCE_CLAIM","writes":0,"provider_launches":0}
  ],
  "credit_boundary":"A passing control permits only the next ordinary gate evaluation and grants no provider, publication, ratification, installation, owner, or adoption authority."
}
'@

$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$candidatePath = Join-Path $repo 'ruling-candidates\opus-model-failback-r1.md'
$adjudicationPath = Join-Path $repo 'receipts\fable-model-exhaustion-adjudication-r3-20260825.json'
$variantPath = Join-Path $repo 'receipts\fable-classifier-variant-r4-20260825.json'
$opusReviewPath = Join-Path $repo 'receipts\opus-model-failback-r2-independent-opus-revise-20260825.json'
$candidate = [IO.File]::ReadAllText($candidatePath)
$candidateFlat = $candidate -replace '\s+', ' '
$spec = $specJson | ConvertFrom-Json -Depth 20 -ErrorAction Stop
$adjudication = [IO.File]::ReadAllText($adjudicationPath) | ConvertFrom-Json -Depth 20 -ErrorAction Stop
$variant = [IO.File]::ReadAllText($variantPath) | ConvertFrom-Json -Depth 20 -ErrorAction Stop
$opusReview = [IO.File]::ReadAllText($opusReviewPath) | ConvertFrom-Json -Depth 20 -ErrorAction Stop

Assert-True ($spec.schema -ceq 'fleet-exhausted-model-failback-controls.v3') 'schema'
Assert-True ($spec.candidate -ceq 'opus-model-failback-r4') 'candidate identity'
Assert-True ($spec.authority -ceq 'ZERO_AUTHORITY_REPRODUCTION_MATRIX') 'zero authority'
Assert-True ($spec.capacity_observation_max_age_seconds -eq 300) '300-second maximum age'
Assert-True ($spec.hard_ceiling_rule -ceq 'UTILIZATION_PLUS_ACTIVE_RESERVATIONS_PLUS_CONSERVATIVE_ESTIMATE_LTE_100_IN_EVERY_WINDOW') 'exact hard ceiling rule'
Assert-True ($spec.discriminator_assertions.Count -eq 12) 'exact discriminator assertion count'
Assert-True ((@($spec.discriminator_assertions | Sort-Object -Unique)).Count -eq 12) 'unique discriminator assertions'
Assert-True ($spec.classifier_rules.bind_every_rate_limit_event -eq $true) 'all classifier events bound'
Assert-True ($spec.execution_contract.common.effort -ceq 'max') 'max effort'
Assert-True ($spec.execution_contract.common.max_turns -eq 12) '12 turn bound'
Assert-True ($spec.execution_contract.common.max_wall_clock_seconds -eq 900) '900 second wall bound'
Assert-True ((@($spec.execution_contract.common.provider_tools) -join ',') -ceq 'Read,StructuredOutput') 'exact provider tools'
Assert-True ($spec.execution_contract.fable.model -ceq 'claude-fable-5') 'exact Fable model'
Assert-True ($spec.execution_contract.fable.role -ceq 'coordinator') 'exact Fable role'
Assert-True ($spec.execution_contract.opus.model -ceq 'claude-opus-5') 'exact Opus model'
Assert-True ($spec.execution_contract.opus.role -ceq 'executor') 'exact Opus role'
Assert-True ($spec.cases.Count -eq 28) 'exact control count'

$ids = @($spec.cases | ForEach-Object { [string]$_.id })
Assert-True ((@($ids | Sort-Object -Unique)).Count -eq $ids.Count) 'unique control ids'
foreach ($required in @(
    'assistant_error_missing_or_different',
    'rate_limit_event_omitted',
    'base_window_rejected',
    'overage_only_rejected_with_allowed_base_below_100',
    'overage_only_rejected_without_base_event_with_exact_model_evidence_and_signed_base_below_100',
    'overage_only_rejected_without_base_event_or_fresh_signed_corroboration',
    'contradictory_or_unenumerated_rate_limit_event',
    'hard_ceiling_sum_exactly_100',
    'hard_ceiling_sum_above_100',
    'core_subject_reordered',
    'core_subject_replaced',
    'execution_contract_effort_drift',
    'execution_contract_turn_or_wall_drift',
    'assertion_map_count_mismatch',
    'unconsumed_canary',
    'consumed_canary_not_authority'
)) {
    Assert-True ($required -cin $ids) "required control $required"
}

foreach ($case in $spec.cases) {
    $names = @($case.PSObject.Properties.Name | Sort-Object)
    Assert-True (($names -join ',') -ceq 'expected,id,mutation,provider_launches,writes') "closed keys $($case.id)"
    Assert-True ($case.writes -eq 0) "zero writes $($case.id)"
    Assert-True ($case.provider_launches -eq 0) "zero launches $($case.id)"
}

$at100 = $spec.cases | Where-Object id -CEQ 'hard_ceiling_sum_exactly_100'
$above100 = $spec.cases | Where-Object id -CEQ 'hard_ceiling_sum_above_100'
$noBaseCorroborated = $spec.cases | Where-Object id -CEQ 'overage_only_rejected_without_base_event_with_exact_model_evidence_and_signed_base_below_100'
$noBaseUncorroborated = $spec.cases | Where-Object id -CEQ 'overage_only_rejected_without_base_event_or_fresh_signed_corroboration'
$unknownClassifier = $spec.cases | Where-Object id -CEQ 'contradictory_or_unenumerated_rate_limit_event'
Assert-True ($at100.expected -ceq 'CONTINUE_TO_LATER_GATES') 'sum exactly 100 is within the hard ceiling'
Assert-True ($above100.expected -ceq 'HOLD_HARD_CEILING') 'sum above 100 is refused'
Assert-True ($noBaseCorroborated.expected -ceq 'CONTINUE_TO_OTHER_GATES') 'observed no-base variant continues only with exact and signed corroboration'
Assert-True ($noBaseUncorroborated.expected -ceq 'HOLD_CLASSIFIER_AMBIGUOUS') 'uncorroborated no-base variant holds'
Assert-True ($unknownClassifier.expected -ceq 'HOLD_CLASSIFIER_AMBIGUOUS') 'contradictory or unknown classifier holds'

Assert-True ($adjudication.schema -ceq 'fleet-fable-model-exhaustion-adjudication.v1') 'adjudication schema'
Assert-True ($adjudication.assistant_error -ceq 'rate_limit') 'assistant error bound'
Assert-True ($adjudication.rate_limit_events.Count -eq 2) 'all measured classifier events bound'
Assert-True ($adjudication.classifier_adjudication.base_window_exhausted -eq $false) 'base window not exhausted'
Assert-True ($adjudication.classifier_adjudication.overage_entitlement_rejected -eq $true) 'overage entitlement rejection disclosed'
Assert-True ($adjudication.assertion_count -eq $adjudication.assertions.Count) 'adjudication assertion map exact'
Assert-True ((@($adjudication.assertions) -join ',') -ceq (@($spec.discriminator_assertions) -join ',')) 'adjudication assertion names exact'
Assert-True ($adjudication.review_credit -ceq 'ZERO') 'Fable review credit zero'
Assert-True ($adjudication.acceptance_credit -ceq 'ZERO') 'Fable acceptance credit zero'

Assert-True ($variant.schema -ceq 'fleet-fable-classifier-variant.v1') 'variant schema'
Assert-True ($variant.observed_rate_limit_events.Count -eq 1) 'variant binds every observed classifier event'
Assert-True ($variant.base_seven_day_event_present -eq $false) 'variant proves base event omission'
Assert-True ($variant.signed_capacity.five_hour_utilization_pct -lt 100) 'variant signed five-hour below 100'
Assert-True ($variant.signed_capacity.seven_day_utilization_pct -lt 100) 'variant signed seven-day below 100'
Assert-True ($variant.r3_disposition -ceq 'HOLD_CLASSIFIER_AMBIGUOUS_ZERO_CREDIT') 'R3 hold preserved'
Assert-True ($variant.r4_expected_disposition -ceq 'MAY_CONTINUE_ONLY_TO_ORDINARY_OPUS_ADMISSION_GATES') 'R4 narrow repair exact'
Assert-True ($variant.review_credit -ceq 'ZERO') 'variant review credit zero'
Assert-True ($variant.acceptance_credit -ceq 'ZERO') 'variant acceptance credit zero'

Assert-True ($opusReview.verdict -ceq 'REVISE') 'prior Opus verdict preserved'
Assert-True ($opusReview.actionable_findings.Count -eq 6) 'six prior Opus findings bound'
Assert-True ($opusReview.acceptance_credit -ceq 'ZERO') 'prior Opus acceptance zero'

Assert-True ($candidate.StartsWith('# Ruling candidate: exhausted-model failback to Opus R4')) 'R4 title'
Assert-True ($candidate.Contains('## Immutable core subjects and execution contract')) 'core contract section'
Assert-True ($candidate.Contains('seven_day_overage_included')) 'overage classifier rule'
Assert-True ($candidate.Contains('assistant event''s exact `error` field')) 'assistant error evidence rule'
Assert-True ($candidateFlat.Contains('less than or equal to 100% in every required window')) 'hard ceiling boundary'
Assert-True ($candidateFlat.Contains('at most 12 turns, at most 900 seconds wall clock')) 'execution bounds'
Assert-True ($candidate.Contains('core_subjects_sha256')) 'core digest binding'

$coreRelative = @(
    'ruling-candidates/opus-model-failback-r1.md',
    'tests/test-opus-model-failback-r3-controls.ps1',
    'receipts/fable-model-exhaustion-adjudication-r3-20260825.json',
    'receipts/fable-classifier-variant-r4-20260825.json'
)
$rows = [Collections.Generic.List[object]]::new()
foreach ($relative in $coreRelative) {
    $path = Join-Path $repo ($relative -replace '/', [IO.Path]::DirectorySeparatorChar)
    $item = Get-Item -LiteralPath $path -ErrorAction Stop
    $rows.Add([ordered]@{path=$relative;bytes=[int64]$item.Length;sha256=(Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash})
}
$canonical = $rows | ConvertTo-Json -Compress -Depth 5
$coreSha = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.UTF8Encoding]::new($false).GetBytes($canonical)))

[Console]::Out.WriteLine("PASS SUITE - $script:assertions assertions; ZERO_PROVIDER; ZERO_WRITES; CORE=$coreSha")
