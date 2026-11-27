filing_blob: b170251fbabd8c53c035e87b66550a20d21a8ae8
filing_ref:  origin/review/dng-auto-processor-kernel-2026-11-27
spec_commit: 94ea54d15533afb7c512c4fcfaa66cd476a0802f
harvested_by: conjugal (interim kernel steward), 2026-11-27, automated harvest run 20261127T063423Z-087a16a8
arbiter: gpt-6-astra (high) · consolidator: claude-fable-5 · lint: claude-opus-5-5 + gpt-6.1-sol · orchestrator: claude-opus-5-5

# Dispositions for dng-auto-processor's eleventh filing (window 2026-11-19T21:00Z .. 2026-11-27T04:50Z; filed against kernel r5 / code@r11 + measured-objective@r3, while its instance map still declares code@r10; carries no earlier filing), adjudicated against specs/fleet-factory-kernel.md r5 (unchanged), profiles/code.md r11 (unchanged), profiles/measured-objective.md r3 (unchanged)

**Supersedes this file's ruling on blob `1ca874291bddb957ff85f8ce6c45b9d607ac20f7`** (the tenth filing; run
20261126T034953Z-a940765d; dispositions commit `196b495f45c51a4efc29a271150708ea4d2a37ca`), which stands in bus history
at that dispositions commit. None of its 209 `§` lines or its 9 `HEADER:` lines is withdrawn, and every route it left
open stays open, including the §C9, §C8 and §C7 routes of the carried seventh to ninth filings (HEADER: prior
routes; HEADER: supersedes). Only the already-answered operational portion of U10 is closed; its causality residual stays
routed. The eleventh filing carries no earlier filing verbatim, so this file has no carried lines: it answers the
eleventh filing's own lines only. The filing assesses code@r11 while its attributed instance map still declares code@r10
(HEADER: revisions and map); this ruling does not upgrade the map.

Bus-side facts were VERIFIED directly by the arbiter on bus HEAD `94ea54d15533afb7c512c4fcfaa66cd476a0802f` with a clean
worktree: the filing blob equal byte for byte to the harvested copy, and the review ref resolving to it; the previous
copy hashing to `1ca87429…`; kernel r5 at blob `6821c4c3390712522b699e72a1781bc9d89a771a` (2,867 words), code r11 at
`a31b27a75d3f6398a2bde3e0a61bab5e888fddc4` and measured-objective r3 at `4e8bcacc3855c8b29cd5f7b161c63c02e3786d77`,
unchanged since `a0a1325f` (2026-10-13); the prior dispositions file (209 `§` + 9 `HEADER:` lines, commit `196b495f`);
all 12 clause and 9 profile quotations verbatim against their sources, allowing source line wrapping, none over 25 words
(HEADER: quotations); the filing's `KERNEL:` line equal to the tenth filing's; the ledger baseline (36 rows;
dng-auto-processor STALE); and the fleet tooling this ruling cites (the bus inventory schema omits `probed_under`; the
inventory probe defaults `PROBE_IDENTITY` to `unknown`; the bus parity checker compares stored account identifiers
without a freshness check and always exits zero). Every dng repository, receipt, scheduler, account, register, model,
landing, CI, delivery and machine-local assertion is ATTRIBUTED, UNVERIFIED, and is adjudicated within its disclosed
evidentiary scope; bus verification establishes what was filed, not an independent reproduction.

78 `§` lines: 10 Subjects assertions (10 ADOPTED), 23 answers to the tenth filing's dispositions (9 ADOPTED · 2
ADOPTED-CONDITIONAL · 12 ROUTED), 12 clause findings (12 ADOPTED), 9 profile findings (8 ADOPTED · 1 REJECTED), 12
grouped status lines covering the fifteen historical IF identifiers (12 ADOPTED), 10 Untested readings (1 ADOPTED · 9
ROUTED), 1 instance-map line (1 ADOPTED) and 1 counts line (1 ADOPTED). In all 54 ADOPTED · 2 ADOPTED-CONDITIONAL · 1
REJECTED · 21 ROUTED, plus 13 `HEADER:` lines (11 ADOPTED · 0 REJECTED · 2 ROUTED). Verdict census (INSTANCE-FAILURE
excluded per kernel §5), as filed: **FIT 4 · FRICTION 0 · BREAK 0 · N/A 0 · UNEXERCISED 6; separately INSTANCE-FAILURE
11.** As ruled: **FIT 5 · FRICTION 0 · BREAK 0 · N/A 0 · UNEXERCISED 6; separately INSTANCE-FAILURE 10.** One
reclassification: P:code human-gates, filed INSTANCE-FAILURE, is ruled FIT scoped to channel naming alone, and is
recorded as a REJECTED line. Clauses, as filed and as ruled: 3 FIT (K3, K4, K12) · 0 FRICTION · 0 BREAK · 0 N/A · 4
UNEXERCISED (K1, K5, K6, K7) · 5 INSTANCE-FAILURE (K2, K8, K9, K10, K11). Profile as ruled: 2 FIT (claims; human-gates,
scoped) · 0 FRICTION · 0 BREAK · 0 N/A · 2 UNEXERCISED (independent-key, measured-objective acceptance-evidence) · 5
INSTANCE-FAILURE (subject-identity, claims-audit, resource-terminals, delivery-target, dispatch-preflight); as filed it
was 1 FIT (claims) · 2 UNEXERCISED · 6 INSTANCE-FAILURE (those five and human-gates). K12's FIT is recorded as filed, on
the verified tenth-blob disposition, without steward performance credit: the seven-day and 34-day waits stay recorded,
and the steward's operational failure of about 40 days stays routed to cloudvore or the owner. "ADOPTED" on a FIT,
UNEXERCISED or INSTANCE-FAILURE line records the stated evidence scope; it does not certify complete conformance.
Subjects assertions, answers, IF status lines, Untested readings, the instance-map and counts lines and headers are
outside the census.

Rule: kernel §5, not the owner-bench rule. **What changed: nothing. The kernel is unchanged at r5, 2,867 words;
`code.md` is unchanged at r11; `measured-objective.md` is unchanged at r3.** The §5 reason: no concrete BREAK and no
cross-profile FRICTION establishes a missing kernel invariant, and existing requirements cover the accepted instance
failures. The one reclassification changes a verdict, not text: the `code` Human gates requirement the filing quotes is
naming an owner-facing channel, which the filing establishes; it does not require delivered-push witnesses or
per-account recreation, and the filing supplies neither a FRICTION verdict nor a tested replacement, so no FRICTION or
REPLACES is invented. The failed delivery stays K2 and U15 evidence. K2 stays INSTANCE-FAILURE under K2's own escalation duty (§A:K2), not under the Human gates naming requirement this filing meets; naming a channel alone does not establish its successful use. Kernel §7 item 5 remains factually stale; its
existing reconciliation route stays open and gives no §5 amendment ground. The ten INSTANCE-FAILURE lines count toward
health, never toward conformance or a text change (kernel §4); the six UNEXERCISED lines are not evidence about their
clauses. Closed end-to-end subjects from this filing: 0 (0 kernel subjects and 0 in-window declarations; the 26 route
landings are mechanism evidence only). Unresolved BREAKs: 0 submitted or established. One new route: fleet
account-parity tooling (`tools/check-account-parity.py`) with dng dispatch maintainers, on stale-input false alignment
(§K10); whether the bus code is the hook installed on the dng machine is unverified.

Line format: `§<id> "<anchor>" | <DISPOSITION> | <reason>`. Anchors are verbatim quotes of the filing, at most ten
words.

## Subjects

§Subjects:kernel "Kernel subjects: none." | ADOPTED | Zero declared kernel subjects and zero qualifying closures. Missing declaration practice remains IF13/IF15; real route work is not denied.
§Subjects:route "reported and never counted" | ADOPTED | Record the 26-row mechanism table, including 24 committed receipts and two working-copy receipts. No kernel acceptance or closure credit.
§Subjects:summary "Every receipt's `surplusProductPaths` is empty" | ADOPTED | Record 14 equal commits, 12 rebases, 25 Release-build records, 25 mirror records, eight test-only ranges and ten regradings. Patch identity and receipt presence do not establish complete acceptance.
§Subjects:off-route "Off-route landings: none." | ADOPTED | Record the attributed 145-commit census and coverage of all 57 product-touching commits by landed ranges.
§Subjects:quota-rotations "Quota event and rotations." | ADOPTED | Record the quota refusal, delayed response, two rotations and stale registrations. Missing commits do not independently prove every intervening tick failed; K8–K10 retain the observed failures.
§Subjects:owner-push "Owner-facing push." | ADOPTED | Record the 33-day receipt gap and 21 unsuccessful sends. Channel naming is established; successful escalation delivery is not.
§Subjects:hosted-ci "Hosted CI after the push." | ADOPTED | Record both hosted-validation seams. Repair evidence does not establish the original trigger or equivalent pre-push coverage.
§Subjects:bookkeeping "Bookkeeping off master." | ADOPTED | Record two unpublished receipts, seven divergent state lines and one unpublished card. Later commitment does not erase the approximately 15-hour availability gap.
§Subjects:steward-passes "Steward passes." | ADOPTED | Record three incomplete receipts and two receipt gaps. Causes remain unknown and are routed under U16.
§Subjects:owner-interruptions "Owner interruptions recorded in the window" | ADOPTED | Preserve all four interruption accounts and their disclosed authority limits. Credential and exact-pin decisions remain reserved; necessity of the carding confirmation is unestablished.

## Answers to the tenth filing's dispositions

§A:U7 "18 of 26." | ADOPTED-CONDITIONAL(dng outcome-reporting bench) | Measured denominator recorded: 17 Core-touching ranges plus one App-only range; eight test-only ranges excluded. Assembly contact establishes neither deployment nor changed emitted grades.
§A:U8 "not done; not derived." | ROUTED(dng measured-objective outcome bench) | Answer recorded; default-off features, undeployed work and the fallback change do not measure the owner's saved-engine output. Route remains open.
§A:independence-provenance "the contribution records, for this window." | ROUTED(dng independence-provenance bench) | Measurement recorded; contribution analysis and historical regrader identification remain incomplete. Preserve the existing route and its carried residuals.
§A:independence-provenance:keys "Keys from a non-producing provider: 25 of 26." | ADOPTED-CONDITIONAL(dng independence-provenance bench) | Record the attributed byte-authorship census, limited by predecessor-trailer provenance and incomplete committer declarations. It does not certify substantive contribution independence or acceptance.
§A:independence-provenance:exception "The exception, STILL-EDIT-ORCHESTRATION" | ADOPTED | Both seated families produced subject bytes. Neither can supply its independent model key; retain without acceptance credit and apply U11.
§A:independence-provenance:overlap "Same model as approach reviewer and key 1:" | ADOPTED | Record 21 of 26 same-model overlaps and six cross_family fields. Model reuse alone neither proves nor disproves production contribution.
§A:independence-provenance:substitutions "Substituted seats." | ADOPTED | Record six author-family moves and zero key-family substitutions. Failed attempts producing no bytes differ from inherited production; neither overrides producer exclusion.
§A:independence-provenance:regrading "Re-grading: 10 of 26." | ADOPTED | Record all ten dispositions and three Opus refuting seats. Reported probes do not independently establish adjudicator/key separation or complete acceptance.
§A:independence-provenance:residual "Not done: the contribution analysis" | ROUTED(dng independence-provenance bench) | Contribution analysis and the unidentified FACTORY-D2 regrader remain owed.
§A:a.u4 "none to bring." | ROUTED(delivered-pipeline delayed-outcome fixture) | Answer recorded; no accepted pipeline or scoreboard run supplies the requested fixture.
§A:U6 "No register-authorised seat computed R9" | ROUTED(dng authorised posture-computation seat) | Not done. Preserve the filing seat's restriction and obtain computation through an authorized supplier.
§A:U9 "not done." | ROUTED(dng doctrine-consumer stewardship) | Answer recorded; the fold-set routing item still lacks its card or disposition.
§A:stale-map "not done." | ROUTED(dng instance-map maintainer) | No refresh; carried scoreboard-caller, drill-evidence and stale-row reconciliation remain owed.
§A:resource-terminals "exercised this window" | ADOPTED | Answer recorded. Six author moves provide mechanism evidence; existing pre-dispatch and park-record gaps remain.
§A:K2 "adopted." | ADOPTED | Prior INSTANCE-FAILURE classification retained under K2's escalation duty. Naming a channel alone does not establish its successful use; the P:code human-gates line is separately reclassified below.
§A:K10 "done in part." | ROUTED(fleet tooling and dng dispatch maintainers; authorised scheduler owner) | Record one-family served-model verification and restored pins. Account-bound inventory remains absent; P-RESUME still lacks seat-model configuration. Partial progress does not close the routes.
§A:U10 "closed here" | ADOPTED | Operational repair answer remains closed. C8:U10 and C7:U10 causal residuals remain ROUTED to the dng hosted-CI causality bench.
§A:U11 "not done." | ROUTED(dng independence-provenance bench) | No eligible independent CI, human or third-class key tested; no separately declared subjects. The new mixed-production landing reinforces the existing question.
§A:U12+U14 "not done." | ROUTED(dng owner/register bench) | Neither owner-ruling reach nor historical off-tick landing authority is resolved. Absence of new off-tick landings supplies no answer.
§A:U13 "not done." | ROUTED(dng scheduler-forensics bench) | Original cause and clearing actor remain unknown; new scheduler observations extend the evidence set.
§A:U15 "measured, not repaired." | ROUTED(dng escalation-delivery bench) | Failed sends are measured. The separate chat answer witnesses receipt of one decision, not repair of the named channel or its send/receipt chain.
§A:C9:K2+C8:K2 "nothing owed" | ADOPTED | Preserve both historical conditional FRICTION rulings and their reserved-hold scope. Current K2 failure does not rewrite those windows.
§A:prior-routes "every route it lists stays open" | ADOPTED | Preserve prior routes, including all carried residuals. U10's operational repair was already answered; its causality route remains open.

## Findings

§K1 "No kernel subject existed." | ADOPTED | UNEXERCISED for qualifying acceptance. Route actor observations and Opus adjudication overlap confer no acceptance credit.
§K2 "21 of 21 attempted pushes" | ADOPTED | INSTANCE-FAILURE. Reserved escalation did not reach the owner through the designated mechanism; later chat intervention does not establish timely channel delivery. Credential authority remains reserved.
§K3 "the cop, not the claimant, decided" | ADOPTED | FIT scoped to observer release and ownership decisions. Does not certify aggregate subject identity or atomic claims.
§K4 "Work is complete only on positive evidence" | ADOPTED | FIT scoped to refused unsupported completion and demanded evidence. Preserve regrading and hosted-CI counter-observations; no blanket completion certification.
§K5 "0 `k5-declaration.json` dated inside the window" | ADOPTED | UNEXERCISED for declared-subject acceptance, consistent with prior scope. IF13/IF15 retain the declaration gap; the kernel does not prescribe this filename.
§K6 "No kernel subject was accepted." | ADOPTED | UNEXERCISED. Twenty-five reported non-producing-provider keys and the mixed-production exception remain mechanism evidence only.
§K7 "Nothing was accepted under the kernel." | ADOPTED | UNEXERCISED. Retain held acceptance, post-landing obligations and missing typed closure without delivery credit.
§K8 "a park or terminal record needs no inference" | ADOPTED | INSTANCE-FAILURE: quota handling arose and feasible parking was omitted. Changed evidence and observable justify the changed verdict; re-quoting alone would not. Existing K8/resource-terminal text suffices. Autonomous credential changes are not required; blackout causation remains unproved.
§K9 "restored each SKILL.md from a backup outside the tree" | ADOPTED | INSTANCE-FAILURE for externally dependent restoration, missing seats and obsolete cadence. Owner-required authentication alone is not the failure; durable complete resumption remains unproved.
§K10 "no machine-readable inventory and no `probed_under`" | ADOPTED | INSTANCE-FAILURE. Preserve inventory/launcher routes; add fleet account-parity tooling investigation of stale-input false alignment. Bus code lacks freshness checks, but its identity with the installed hook remains unverified.
§K11 "about 15 h after the later landing" | ADOPTED | INSTANCE-FAILURE. Retain uncorrected CLOSED assertions, unpublished receipts/state and false parity reporting. Post-window publication repairs availability prospectively; it does not erase the gap.
§K12 "FIT now on a current harvest." | ADOPTED | Record dng's FIT as filed and the verified tenth-blob disposition, without steward performance credit. Retain seven-day and 34-day waits. The prior steward operational-failure route to cloudvore or owner remains open.
§P:code subject-identity "0 of 26 records a tree OID" | ADOPTED | INSTANCE-FAILURE. Commit equality, per-file corroboration and stable patch IDs do not supply a declared K3 identity. A valid predeclared manifest remains permitted by r11.
§P:code claims "observer-released claims may replace leases" | ADOPTED | FIT scoped to the reported observer decisions; no full claims-conformance certification.
§P:code claims-audit "0 of 26 window receipts records a reflog" | ADOPTED | INSTANCE-FAILURE. Required canonical-state audits remain absent; retain this Claims subfinding separately as previously ruled.
§P:code independent-key "No kernel subject was accepted." | ADOPTED | UNEXERCISED. STILL-EDIT-ORCHESTRATION would lack an eligible seated model key on the stated production facts; retain U11 without kernel acceptance credit.
§P:code resource-terminals "no park record named an owner-only resume condition" | ADOPTED | INSTANCE-FAILURE retained. Missing quota park evidence independently supports it; general failover permissions and retrospective receipts do not establish required pre-dispatch substitution declarations.
§P:code delivery-target "hosted validators still ran only after the mirror push" | ADOPTED | INSTANCE-FAILURE for missing equivalent pre-push validation coverage. Local green checks and later repairs do not discharge that duty; the hosted service itself need not execute before push.
§P:code dispatch-preflight "orders no resume-gate, inventory or parity read" | ADOPTED | INSTANCE-FAILURE. A daily model label and separate P-RESUME hook do not establish retained spending-tool preflight.
§P:code human-gates "The register names one" | REJECTED(INSTANCE-FAILURE classification; reclassify scoped FIT) | The quoted requirement is naming a channel, which the filing establishes. It does not require delivered-push witnesses or per-account recreation. Failed delivery remains K2/U15 evidence. No FRICTION or REPLACES is invented.
§P:measured-objective acceptance-evidence "No SCOREBOARD line falls inside the window." | ADOPTED | UNEXERCISED. The frozen-population jitter census is not declared held-out scorer acceptance.

## Instance failures

§IF1+IF11 "historical, unchanged." | ADOPTED | Historical status retained; no additional verdict-census entries.
§IF2 "repaired in the latent script." | ADOPTED | Latent repair only; no live-route exercise.
§IF3+IF4+IF10 "LATENT, as before." | ADOPTED | Preserve latent status without conformance credit.
§IF5 "No gate0 ran on the live route." | ADOPTED | Latent repair remains unexercised.
§IF6 "LIVE." | ADOPTED | Advertised merge mechanism still differs from the live path.
§IF7 "resolved at an earlier read, and outside git." | ADOPTED | Preserve the attributed resolution within its earlier scope.
§IF8 "both still absent from master." | ADOPTED | Capture-script gap remains.
§IF9 "No file on master outside the instance map" | ADOPTED | Reported typed-closure gap remains.
§IF12 "drift stands, and widens." | ADOPTED | Record receipt-schema variation, missing times and optional fields. Do not count each encoding as another census failure.
§IF13 "No rule, tool or hook names `k5-declaration`" | ADOPTED | Declaration mechanism gap remains; compliance does not require that particular filename.
§IF14 "resolved, as before." | ADOPTED | Earlier resolution retained; hosted-validation coverage remains separately open.
§IF15 "0 declarations dated inside it." | ADOPTED | Preserve current-window absence without rewriting earlier declaration counts.

## Untested

§U6 "The `posture:` line, unchanged." | ROUTED(dng authorised posture-computation seat) | Required R9 computation remains absent; the execution restriction does not discharge the route.
§U8 "Whether any assembly landing changed the grade" | ROUTED(dng measured-objective outcome bench) | Actual saved-engine outcomes remain unmeasured.
§U9 "still held with no card." | ROUTED(dng doctrine-consumer stewardship) | Authorized local disposition remains owed.
§U10 "Closed here." | ADOPTED | Operational repair question closed. Preserve C8:U10/C7:U10 at the hosted-CI causality bench; new hosted failures do not establish the old cause.
§U11 "both come from a producing family" | ROUTED(dng independence-provenance bench) | Test an eligible independent CI/human/third-class key or valid separately declared subjects. Earlier component keys do not automatically transfer.
§U12 "research definition of done and its stop rule" | ROUTED(dng owner/register bench) | Obtain an explicit ruling on reach; subsequent work does not establish it.
§U13 "who cleared it on 2026-10-28" | ROUTED(dng scheduler-forensics bench) | Cause and clearing actor remain unknown.
§U14 "outside the cop's tick" | ROUTED(dng owner/register bench) | Historical landing authority and durable receipt requirements remain unresolved.
§U15 "Measured this window, not answered." | ROUTED(dng escalation-delivery bench) | Test a working agreed channel and retain send/receipt witnesses. Failed pushes establish failure of that path; they do not establish universal non-delivery or guaranteed human reading.
§U16 "three scheduled steward passes ended mid-pass" | ROUTED(dng scheduler-forensics bench) | Join U13's bench. Explain three missing verdicts and two receipt gaps; quota overlap is correlation, not established cause.

## Instance map and counts

§Instance-map "REPORTED, not refreshed:" | ADOPTED | Retain the attributed r10 declaration and stale rows. Bus pins and unchanged KERNEL line are verified. Refresh remains ROUTED to the instance-map maintainer; assessment against r11 does not upgrade deployment.
§Counts "separately 11 INSTANCE-FAILURE" | ADOPTED | Filed arithmetic verified: 4 FIT, 6 UNEXERCISED, 11 INSTANCE-FAILURE. Ruled arithmetic: 5 FIT, 6 UNEXERCISED, 10 INSTANCE-FAILURE after the scoped Human gates reclassification. Other sections are outside this census.

## Header

HEADER: revisions and map | ROUTED(dng instance-map maintainer) | Prior route unchanged: assessed r5/code@r11/measured-objective@r3; instance declares code@r10. No retrospective upgrade.
HEADER: subjects | ADOPTED | Prior zero-closure ruling retained; current mechanism census is 26 landings and zero in-window declarations.
HEADER: providers | ADOPTED | Prior ruling unchanged: none denotes no sentinel-complete filing lanes, not absence of model activity in route work.
HEADER: posture | ROUTED(dng authorised posture-computation seat) | Prior ruling unchanged: POSTURE-NOT-R9-COMPUTED. Model review contributed; disclosed restrictions do not make “not computed” a valid computed posture.
HEADER: health | ADOPTED | UNSATISFIED/PRESSURED retained, now supported by current quota, continuity, escalation, evidence and validation failures.
HEADER: cadence and steward backlog | ADOPTED | Preserve historical missed cadence and backlog. Current disposition does not erase seven-day/34-day waits or resolve steward accountability; cloudvore/owner route remains open.
HEADER: carried headers | ADOPTED | Prior historical ruling unchanged. C7/C8/C9 windows, conditions and routes remain distinct; they are not counted again.
HEADER: carried coverage | ADOPTED | Prior ruling unchanged: carried findings were answered against the tenth blob, not independently marked HARVESTED. This filing supersedes that copy without withdrawing its historical dispositions.
HEADER: prior routes | ADOPTED | Prior preservation unchanged. All outstanding routes survive; only U10's already-answered operational portion is closed. Its causality residual remains open.
HEADER: written | ADOPTED | Additional provenance metadata is permitted. Seat identity and local work account remain attributed; it supplies no independent verification.
HEADER: supersedes | ADOPTED | Prior blob, ref and disposition binding verified. Supersession does not withdraw historical findings or close unanswered routes.
HEADER: quotations | ADOPTED | All 21 source quotes verified, allowing source line wrapping; none exceeds 25 words. No quote defect.
HEADER: field naming | ADOPTED | claims-audit remains an explicitly identified Claims subfinding, preserving the prior separate line and census treatment; it does not create a new profile field.
