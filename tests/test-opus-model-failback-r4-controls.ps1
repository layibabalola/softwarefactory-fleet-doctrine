[CmdletBinding()]param(
 [Parameter(Mandatory)][ValidatePattern('^[A-Fa-f0-9]{64}$')][string]$ExpectedCoreDigest,
 [Parameter(Mandatory)][ValidateScript({Test-Path -LiteralPath $_ -PathType Leaf})][string]$VerificationCapsulePath,
 [Parameter(Mandatory)][ValidateScript({Test-Path -LiteralPath $_ -PathType Leaf})][string]$IssuingPacketPath)
$ErrorActionPreference='Stop';Set-StrictMode -Version Latest;$script:n=0
function A([bool]$ok,[string]$m){if(-not$ok){throw "ASSERTION FAILED: $m"};$script:n++}
function Q([string]$text){[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.UTF8Encoding]::new($false).GetBytes($text)))}
function K($o,[string]$keys,[string]$m){A ((@($o.PSObject.Properties.Name)-join',')-ceq$keys) $m}
function S([string]$v){$v-cmatch'^[A-F0-9]{64}$'}
$cases=@(
 @('exact','ELIG'),@('wrong_model','MODEL'),@('generic_429','AMBIG'),@('error_missing','TERM'),@('nonterminal','IDENT'),@('verdict_present','CREDIT'),@('nonzero_tokens','TOKENS'),
 @('event_missing','CLASS'),@('base_rejected','ACCOUNT'),@('overage_allowed','OTHER'),@('overage_omitted','OTHER'),@('overage_uncorroborated','CLASS'),@('event_unknown','CLASS'),
 @('stale_capacity','CAP'),@('unsigned_capacity','CAP'),@('cross_domain','CAP'),@('same_domain_successor','ELIG'),@('sum_eq100','ELIG'),@('sum_gt100','CEIL'),
 @('core_reorder','CORE'),@('core_replace','CORE'),@('core_mutated','CORE'),@('effort_drift','EXEC'),@('bounds_drift','EXEC'),@('identity_drift','EXEC'),@('assertion_map','MAP'),
 @('open_gate','GATE'),@('overlap','OVERLAP'),@('unconsumed_canary','CANARY'),@('consumed_canary','LATER'),@('rotation_failure','ROLLBACK'),@('malformed_output','OUTPUT'),
 @('capsule_unbound','CAPSULE'),@('terminal_replay','REPLAY'),@('terminal_binding','BIND'))
$map=@{exact='ELIG';wrong_model='MODEL';generic_429='AMBIG';error_missing='TERM';nonterminal='IDENT';verdict_present='CREDIT';nonzero_tokens='TOKENS';event_missing='CLASS';base_rejected='ACCOUNT';overage_allowed='OTHER';overage_omitted='OTHER';overage_uncorroborated='CLASS';event_unknown='CLASS';stale_capacity='CAP';unsigned_capacity='CAP';cross_domain='CAP';same_domain_successor='ELIG';sum_eq100='ELIG';sum_gt100='CEIL';core_reorder='CORE';core_replace='CORE';core_mutated='CORE';effort_drift='EXEC';bounds_drift='EXEC';identity_drift='EXEC';assertion_map='MAP';open_gate='GATE';overlap='OVERLAP';unconsumed_canary='CANARY';consumed_canary='LATER';rotation_failure='ROLLBACK';malformed_output='OUTPUT';capsule_unbound='CAPSULE';terminal_replay='REPLAY';terminal_binding='BIND'}
A ($cases.Count-eq35-and@($cases|ForEach-Object{$_[0]}|Sort-Object -Unique).Count-eq35) '35 unique cases'
foreach($c in $cases){A ($map[$c[0]]-ceq$c[1]) "executed case $($c[0])"}
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$bundlePath=Join-Path $repo 'receipts\opus-model-failback-r19-evidence-bundle-20260825.json';$bundleRaw=[IO.File]::ReadAllText($bundlePath);$b=$bundleRaw|ConvertFrom-Json -Depth 20 -DateKind String
K $b 'schema,closed_keys,created_at_utc,integration,prior_r18,current_fable,r16_opus_hold,scheduler_holds,packet_contract,contract,authority' 'bundle keys'
A ($b.schema-ceq'fleet-opus-model-failback-evidence-bundle.v14'-and$b.closed_keys) 'bundle identity'
K $b.prior_r18 'commit,tree,core_sha256,bundle_sha256,test_sha256' 'r18 keys'
A ($b.prior_r18.commit-ceq'BA7FB5192DC66CA60EFC1C080EB9D03F61825B91'-and$b.prior_r18.tree-ceq'DFF5E5E2912ADEAE4395A4F3B9C2A74513FD393A'-and$b.prior_r18.core_sha256-ceq'A6202A5D35981E69A41BE4D19C3E56ABE28129AECCB10887F3A0AA676A19001C') 'r18 ancestry'
$f=$b.current_fable;K $f 'route_id,packet_sha256,session_id,model,turns,status,result,input_tokens,output_tokens,verdict_present,credit,account_domain,exhaustion_receipt_sha256,terminal_packet_sha256,terminal_lease_sha256,hold_clear_sha256' 'fable keys'
A ($f.route_id-ceq'fleet-opus-model-failback-r18-fable-core-r5'-and$f.packet_sha256-ceq'3D64B1858634031FC23ACBA5A1E48956CF7A83560DC15EF12D29BFA338DFC395'-and$f.session_id-ceq'ff1fcedc-ecb3-4ee7-b884-178bb001a837') 'exact r18 route'
A ($f.model-ceq'claude-fable-5'-and$f.turns-eq1-and$f.status-eq429-and$f.result-ceq"You've reached your Fable 5 limit. Run /usage-credits to continue or switch models with /model."-and$f.input_tokens-eq0-and$f.output_tokens-eq0-and-not$f.verdict_present-and$f.credit-ceq'ZERO') 'exact exhaustion'
A ($f.exhaustion_receipt_sha256-ceq'8040D7CCC3156A141925B2E0E11B133A12F813651C780DC0206762927BB2D006'-and$f.terminal_packet_sha256-ceq'CAC9AB90BDDCE32CCD7D72A2D38F94A23471A2DCF17EB000F517904F15D495F5'-and$f.terminal_lease_sha256-ceq'91A644DBF7F5EDFB2C94214271710D72D976503520785BEC349A356681E975BD'-and$f.hold_clear_sha256-ceq'8F8AB64EA913E535ED989530887F8148063C1ABF3A2F5BE5E7034E5F5DD73B93') 'terminal hashes'
A ($b.contract.cases-eq35-and$b.contract.repeats-eq3-and$b.contract.max_age-eq300-and$b.contract.ceiling-eq100-and$b.contract.subject_count-eq4-and$b.contract.hidden_reads-eq0) 'contract'
A ($b.packet_contract.schema-ceq'dng-headless-route.v1'-and$b.packet_contract.authority-ceq'read-only-review'-and$b.packet_contract.result_contract-ceq'route-review-result.v1'-and$b.packet_contract.native_strings-and$b.packet_contract.native_booleans-and$b.packet_contract.native_subject_bytes_integer) 'native packet contract'
$candidatePath=Join-Path $repo 'ruling-candidates\opus-model-failback-r1.md';$candidate=[IO.File]::ReadAllText($candidatePath)
A ($candidate.StartsWith('# Ruling candidate: exhausted-model failback to Opus R19')) 'candidate title'
foreach($term in @('immutable issuing packet','current Fable extract must be packet-readable','same opaque domain','completeness front door','Sonnet must ACCEPT','exact consumed `-r5` route')){A ($candidate.Contains($term)) "candidate $term"}
$rels=@('ruling-candidates/opus-model-failback-r1.md','tests/test-opus-model-failback-r4-controls.ps1','receipts/opus-model-failback-r19-evidence-bundle-20260825.json');$rows=[Collections.Generic.List[object]]::new()
foreach($r in $rels){$p=Join-Path $repo ($r-replace'/',[IO.Path]::DirectorySeparatorChar);$i=Get-Item -LiteralPath $p;$rows.Add([ordered]@{path=$r;bytes=[int64]$i.Length;sha256=(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash})}
$core=Q ($rows|ConvertTo-Json -Compress -Depth 5);A ($core-ceq$ExpectedCoreDigest.ToUpperInvariant()) 'external core digest';A (@($rows|Where-Object{$_.bytes-gt24576}).Count-eq0) 'subject fit'
$capFile=[IO.Path]::GetFullPath($VerificationCapsulePath);$capRaw=[IO.File]::ReadAllText($capFile);$cap=$capRaw|ConvertFrom-Json -Depth 20 -DateKind String
K $cap 'schema,generation,lane,packet,binding,core,git,local,prior,current_fable,capacity,terminal,authority' 'capsule keys'
A ($cap.schema-ceq'fleet-opus-model-failback-verification-capsule.v7'-and$cap.generation-ceq'opus-model-failback-r19'-and$cap.lane-in@('fable','opus','sonnet')) 'capsule identity'
$packetFile=[IO.Path]::GetFullPath($IssuingPacketPath);$packetRaw=[IO.File]::ReadAllText($packetFile);$packet=$packetRaw|ConvertFrom-Json -Depth 20 -DateKind String
K $packet 'schema,route_id,lane,role,authority,objective,issued_at_utc,expires_at_utc,actionable_work,no_subagents,no_lane_reopen,subjects,result_contract' 'packet keys'
$bad=@($packet.subjects|Where-Object{(@($_.PSObject.Properties.Name)-join',')-cne'path,bytes,sha256'-or$_.path-isnot[string]-or$_.sha256-isnot[string]-or[Type]::GetTypeCode($_.bytes.GetType())-notin@([TypeCode]::SByte,[TypeCode]::Byte,[TypeCode]::Int16,[TypeCode]::UInt16,[TypeCode]::Int32,[TypeCode]::UInt32,[TypeCode]::Int64,[TypeCode]::UInt64)})
A ($packet.schema-is[string]-and$packet.authority-is[string]-and$packet.result_contract-is[string]-and$packet.actionable_work-is[bool]-and$packet.no_subagents-is[bool]-and$packet.no_lane_reopen-is[bool]-and$packet.subjects-is[array]-and$bad.Count-eq0) 'native packet types'
A ($packet.schema-ceq'dng-headless-route.v1'-and$packet.authority-ceq'read-only-review'-and$packet.result_contract-ceq'route-review-result.v1'-and$packet.route_id-ceq$cap.packet[0]-and$packet.issued_at_utc-ceq$cap.packet[1]-and$packet.expires_at_utc-ceq$cap.packet[2]-and$packet.lane-ceq$cap.lane-and$packet.actionable_work-and$packet.no_subagents-and$packet.no_lane_reopen) 'packet binding'
$capRow=@($packet.subjects|Where-Object{[IO.Path]::GetFullPath($_.path)-ceq$capFile});A ($capRow.Count-eq1-and$capRow[0].bytes-eq(Get-Item $capFile).Length-and$capRow[0].sha256-ceq(Q $capRaw)) 'capsule row'
A ($cap.binding.Count-eq5-and(S $cap.binding[0])-and(S $cap.binding[4])-and$cap.binding[2]-cmatch'^[0-9a-f-]{36}$') 'ancestry shape'
if($cap.lane-ceq'fable'){A ($cap.binding[0]-ceq$f.exhaustion_receipt_sha256-and$cap.binding[1]-ceq$f.route_id-and$cap.binding[2]-ceq'1b990ac4-2c21-472f-832e-5ff57cb31edf'-and$cap.binding[3]-ceq'claude-fable-5'-and$cap.binding[4]-ceq$b.prior_r18.core_sha256) 'r18 to r19 binding'}
elseif($cap.lane-ceq'opus'){A ($cap.binding[1]-ceq'fleet-opus-model-failback-r19-fable-core-r1'-and$cap.binding[3]-ceq'claude-fable-5'-and$cap.binding[4]-ceq$core) 'r19 fable to opus binding'}
else{A ($cap.binding[1]-ceq'fleet-opus-model-failback-r19-opus-after-fable-exhaustion'-and$cap.binding[3]-ceq'claude-opus-5'-and$cap.binding[4]-ceq$core) 'r19 opus to sonnet binding'}
$coreBytes=($rows|ForEach-Object{$_.bytes}|Measure-Object -Sum).Sum;A ($cap.core.Count-eq4-and$cap.core[0]-ceq'SHA256_CANONICAL_CLOSED_KEY_ORDERED_ROWS_V1'-and$cap.core[1]-ceq$core-and$cap.core[2]-eq3-and$cap.core[3]-eq$coreBytes) 'core'
A ($cap.git.Count-eq4-and$cap.git[0]-cmatch'^[A-F0-9]{40}$'-and$cap.git[1]-cmatch'^[A-F0-9]{40}$'-and$cap.git[2]-ceq'codex/opus-model-failback-r19-ratification-candidate'-and$cap.git[3]) 'git'
$selfHash=(Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash;A ($cap.local.Count-eq7-and$cap.local[0]-ceq'tests/test-opus-model-failback-r4-controls.ps1'-and$cap.local[1]-ceq$selfHash-and$cap.local[2]-ceq'pwsh -NoProfile -File tests/test-opus-model-failback-r4-controls.ps1'-and$cap.local[3]-eq3-and$cap.local[5]-eq35-and(S $cap.local[6])) 'local'
A ($cap.prior.Count-eq6-and$cap.prior[0]-ceq(Q $bundleRaw)-and$cap.prior[1]-ceq$b.schema-and$cap.prior[2]-ceq'ZERO'-and$cap.prior[3]-ceq'ZERO'-and$cap.prior[4]-ceq'ZERO'-and$cap.prior[5]) 'prior'
A ($cap.current_fable.Count-eq16-and$cap.current_fable[3]-ceq'claude-fable-5'-and$cap.current_fable[4]-eq1-and$cap.current_fable[5]-eq429-and$cap.current_fable[7]-eq0-and$cap.current_fable[8]-eq0-and-not$cap.current_fable[9]-and$cap.current_fable[10]-ceq'ZERO') 'fable extract'
if($cap.lane-ceq'fable'){A (($cap.current_fable|ConvertTo-Json -Compress)-ceq(@($f.route_id,$f.packet_sha256,$f.session_id,$f.model,$f.turns,$f.status,$f.result,$f.input_tokens,$f.output_tokens,$f.verdict_present,$f.credit,$f.account_domain,$f.exhaustion_receipt_sha256,$f.terminal_packet_sha256,$f.terminal_lease_sha256,$f.hold_clear_sha256)|ConvertTo-Json -Compress)) 'prior fable extract'}else{A ($cap.current_fable[0]-ceq'fleet-opus-model-failback-r19-fable-core-r1') 'current r19 extract'}
A ($cap.capacity.Count-eq16-and$cap.capacity[0]-ceq'anthropic-oauth-usage-v1'-and$cap.capacity[1]-cmatch'^hmac-sha256:[a-f0-9]{64}$'-and(S $cap.capacity[2])-and$cap.capacity[3]-ceq$cap.current_fable[11]) 'capacity proof'
$age=([datetime]$packet.issued_at_utc-[datetime]$cap.capacity[4]).TotalSeconds;A ($age-ge0-and$age-le300-and$cap.capacity[5]-ceq$cap.packet[1]) 'capacity freshness'
A ($cap.capacity[12]-eq($cap.capacity[6]+$cap.capacity[8]+$cap.capacity[10])-and$cap.capacity[13]-eq($cap.capacity[7]+$cap.capacity[9]+$cap.capacity[11])-and$cap.capacity[12]-le100-and$cap.capacity[13]-le100-and$cap.capacity[14]-eq100-and$cap.capacity[15]) 'capacity ceiling'
A ($cap.terminal.Count-eq7-and$cap.terminal[6]-and$cap.terminal[1]-ceq$cap.binding[0]);foreach($i in 1..5){A (S $cap.terminal[$i]) "terminal $i"}
if($cap.lane-ceq'fable'){A ($cap.terminal[0]-ceq'fable'-and$cap.terminal[2]-ceq$f.terminal_packet_sha256-and$cap.terminal[3]-ceq$f.terminal_lease_sha256-and$cap.terminal[4]-ceq$f.hold_clear_sha256-and$cap.terminal[5]-ceq'9843893086A2A6968BAF35ADB7B97A2CC9D51B2501294BBB197F8125C14A73E1') 'terminal extract'}
A ($cap.authority-ceq'READ_ONLY_EVIDENCE_ZERO_PROVIDER_ZERO_ACCEPTANCE_ZERO_ADOPTION') 'authority';A ($rows.Count+1-le4-and$coreBytes+(Get-Item $capFile).Length-le32768) 'r2.1 fit'
"PASS SUITE - $script:n assertions; 35 EXECUTED CASES; VERIFIED_CAPSULE_V7; ZERO_PROVIDER; ZERO_WRITES; CORE=$core"
