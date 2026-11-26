filing_blob: 1ca874291bddb957ff85f8ce6c45b9d607ac20f7
filing_ref:  origin/review/dng-auto-processor-kernel-2026-11-19
spec_commit: 792b9ed0d7db2ad6d4282e4e5104f16f3d10098a
harvested_by: conjugal (interim kernel steward), 2026-11-26, automated harvest run 20261126T034953Z-a940765d
arbiter: gpt-6-astra (high) · consolidator: claude-fable-5 · lint: claude-opus-5.5 + gpt-6.1-sol · orchestrator: claude-opus-5-5

# Dispositions for dng-auto-processor's tenth filing (window 2026-11-06T21:00Z .. 2026-11-19T21:00Z; filed against kernel r5 / code@r11 + measured-objective@r3, while its instance map still declares code@r10; carries the ninth, eighth and seventh filings verbatim), adjudicated against specs/fleet-factory-kernel.md r5 (unchanged), profiles/code.md r11 (unchanged), profiles/measured-objective.md r3 (unchanged)

**Supersedes this file's ruling on blob `cce576ba99229229d9dda4b2203154069703bdac`** (the sixth filing; run
20261016T090409Z-078e6f76, spec commit `d411647341047f091c0e1ebe12e324154551a1c9`; dispositions commit
`5774eb140d97fed11ffcb3f1a4038fc52e072f1d`), which stands in bus history at that dispositions commit. None of its 46 `§`
dispositions or its 10 `HEADER:` lines is withdrawn: no disposition, routing, rejection, conditional permission or
adopted text of that ruling is withdrawn, and every route it left open stays open (HEADER: prior routes, below); U10, whose operational portion this ruling
answers, first appears in the carried seventh filing and was never a route of that ruling. Three intermediate copies were never harvested and have no
dispositions file: blob `27aeb992` (seventh filing, 2026-10-23), blob `ac626991` (eighth, 2026-10-30) and blob
`94a01ff3` (ninth, 2026-11-06). All three are carried verbatim inside the tenth blob, each nested in the next, and are
answered here against the tenth blob as §C7, §C8 and §C9. Answering them here does not mark the earlier blobs HARVESTED
on their own (HEADER: carried coverage). The filing assesses code@r11 on every profile line while its attributed
instance map still declares code@r10 (HEADER: revisions and map); this ruling does not upgrade the map.
Bus-side facts were VERIFIED directly by the arbiter: bus HEAD `31049268ab758c8f906c09167a19745c0de600b2` with a clean
worktree; the filing blob equal byte for byte to the harvested copy; the three nested carried sections, once unquoted,
equal to blobs `94a01ff3`, `ac626991` and `27aeb992` (ignoring surrounding whitespace); kernel r5 at blob
`6821c4c3390712522b699e72a1781bc9d89a771a` (2,867 words), code r11 at `a31b27a75d3f6398a2bde3e0a61bab5e888fddc4` and
measured-objective r3 at `4e8bcacc3855c8b29cd5f7b161c63c02e3786d77`, with no later revision in `git log`; the prior
dispositions file binding `cce576ba`; `harvest-status.py` reading this filing STALE; the ledger baseline (33 rows); the
fleet `TRAPS.md` entry of 2026-09-27 on scheduled-routine model and effort, the scheduled-task model-pin seam in
`RECEIPTS.md` and the H5 quotation from `ruling-candidates/detector-to-control-hardening-r1.md`, all of which the filing
cites; the completed 2026-10-16 harvest of the sixth filing; and the fleet inventory tooling
(`specs/machine-inventory-schema.md` omits `probed_under`; `tools/probe-machine-inventory.sh` emits a caller-supplied
`PROBE_IDENTITY` that defaults to `unknown`). Every dng repository and machine-local fact — the route receipts and
their landings, commits, patch and blob identities, the daily-ledger lines, the steward receipts and cop ticks, the
model-mismatch hold with its cause, the owner's model pin and the recovery, the rotations and P-RESUME receipts, the
usage discontinuity, the approach and key verdicts, the declaration sweep, the CI results, the register restrictions,
the SCOREBOARD absence and the instance-map contents — is ATTRIBUTED, UNVERIFIED, and is adjudicated within its
disclosed evidentiary scope; bus verification of the filing verifies its recorded assertion, not the underlying
experiment.

209 `§` lines. The tenth filing's own 55: 4 Subjects assertions (4 ADOPTED), 8 answers to routed benches (1 ADOPTED ·
1 ADOPTED-CONDITIONAL · 6 ROUTED), 12 clause findings (11 ADOPTED · 1 REJECTED), 8 profile findings (8 ADOPTED),
12 grouped status lines covering the fifteen historical IF identifiers (12 ADOPTED), 9 Untested readings (1 ADOPTED ·
8 ROUTED), 1 instance-map line (1 ADOPTED) and 1 counts line (1 ADOPTED) — 39 ADOPTED · 1 ADOPTED-CONDITIONAL ·
1 REJECTED · 14 ROUTED. The carried material's 154, one line per
carried finding: ninth filing 54 (39 ADOPTED · 2 ADOPTED-CONDITIONAL · 0 REJECTED · 13 ROUTED), eighth filing 52
(37 ADOPTED · 2 ADOPTED-CONDITIONAL · 0 REJECTED · 13 ROUTED), seventh filing 48 (37 ADOPTED · 1 ADOPTED-CONDITIONAL ·
0 REJECTED · 10 ROUTED). In all 152 ADOPTED · 6 ADOPTED-CONDITIONAL · 1 REJECTED · 50 ROUTED, plus 9 `HEADER:` lines
(7 ADOPTED · 0 REJECTED · 2 ROUTED). Verdict census, tenth-filing lines only (INSTANCE-FAILURE excluded per kernel §5),
as filed: **FIT 4 · FRICTION 1 · BREAK 0 · N/A 0 · UNEXERCISED 7; separately INSTANCE-FAILURE 8.** As ruled: **FIT 4 ·
FRICTION 0 · BREAK 0 · N/A 0 · UNEXERCISED 7; separately INSTANCE-FAILURE 9.** One reclassification: the tenth filing's
K2, filed FRICTION, is ruled INSTANCE-FAILURE. Clauses as ruled: 3 FIT (K3, K4, K12) · 0 FRICTION · 0 BREAK · 0 N/A ·
5 UNEXERCISED (K1, K5, K6, K7, K8) · 4 INSTANCE-FAILURE (K2, K9, K10, K11). Profile as ruled: 1 FIT (claims) ·
0 FRICTION · 0 BREAK · 0 N/A · 2 UNEXERCISED (independent-key, measured-objective acceptance-evidence) ·
5 INSTANCE-FAILURE (subject-identity, claims-audit, resource-terminals, delivery-target, dispatch-preflight). K12's FIT
is historical: it is bus-verified for the completed 2026-10-16 harvest of the sixth filing only, and the seventh to
tenth backlog and the missed 2026-11-13 cadence receive no FIT credit; K12 stays one of the 4 FIT on the historical
ground alone. "ADOPTED" on a FIT, UNEXERCISED or
INSTANCE-FAILURE line records the stated evidence scope; it does not certify complete conformance. **Carried lines are
outside the census:** the §C9, §C8 and §C7 lines answer historical windows that stay distinct, and they are not counted
again. Subjects assertions, bench answers, IF status lines, Untested readings, the instance-map and counts lines and headers
are outside the census too.

Rule: kernel §5, not the owner-bench rule. **What changed: nothing. The kernel is unchanged at r5, 2,867 words;
`code.md` is unchanged at r11; `measured-objective.md` is unchanged at r3.** The §5 reason: no concrete BREAK and no
two-profile FRICTION establishes an amendment, and no exercised finding supports a `measured-objective` change. The
tenth filing's one FRICTION line, K2, is reclassified: the window's escalation stayed in receipts the filing itself
reports as reaching no one, and `code` Human gates and Resource terminals already require an owner-facing channel and
continued eligible work, so this is an instance failure against existing text. A reserved action stays reserved; the
ruling does not require the blocked seat to alter its scheduler. The carried K2 lines are historical and are kept as
filed for their own windows: the ninth and eighth filings' FRICTION is preserved conditionally (dng reserved-hold
bench) with no kernel edit, because the proposed continuation duty is already substantially in `code` Resource
terminals and no second-profile evidence exists; the seventh filing's K2 FIT is preserved. The windows stay distinct: in the eighth and ninth windows the reserved acts
were escalated where the register sends them and answered by owner-side acts, while the tenth window's escalation
stayed in receipts reported as reaching no one, which is what fails the existing owner-facing-channel requirement. The nine INSTANCE-FAILURE
lines count toward health, never toward conformance or a text change (kernel §4); the seven UNEXERCISED lines are not
evidence about their clauses. Closed end-to-end subjects from this filing: 0 (0 kernel subjects and 0 in-window
declarations; the 3 route landings are mechanism evidence only, and neither equal commits nor stable patch IDs supply
the missing declarations and identity receipts). Unresolved BREAKs: 0 submitted or established.

Line format: `§<id> "<anchor>" | <DISPOSITION> | <reason>`. Anchors are verbatim quotes of the filing. In the carried
sections the anchor quotes the carried line itself, read after its `>` quote markers. The arbiter ruled some carried
lines by class (one grouped line naming many ids); each such line is written out below as one line per carried finding,
with the class disposition unchanged.

## Subjects

§Subjects:kernel "Kernel subjects: none." | ADOPTED | Zero qualifying closures and zero in-window declarations. This is the filing's declared acceptance scope, not a claim that its real work did not exist.
§Subjects:route "reported and never counted" | ADOPTED | Retain three attributed route landings and their receipt table as mechanism evidence. Neither equal commits nor stable patch IDs supply the missing kernel declarations and identity receipts.
§Subjects:off-route "Off-route landings: none." | ADOPTED | Retain the attributed eleven-commit census and three product landings.
§Subjects:blocked-seam "The window's blocked seam." | ADOPTED | Retain the nine-day model hold and unread escalation records. Bus TRAP/H5 citations are verified; local cause, owner pin and recovery remain attributed.

## Answers to routed benches

§A:U7 "1 of 3." | ADOPTED-CONDITIONAL(dng outcome-reporting bench) | One App landing satisfies the assembly-touch predicate; two test-only landings do not. Assembly contact does not establish changed emitted grades.
§A:U8 "not derived, one more window." | ROUTED(dng measured-objective outcome bench) | No grade measurement or landed engine change answers the emitted-outcome question.
§A:independence-provenance "the contribution records, for this window." | ROUTED(dng independence-provenance bench) | Retain three non-writing-provider keys, repeated approach/key models and the measured REVISE refutations. No-byte authorship alone does not settle substantive production contribution or the carried-lineage question.
§A:a.u4 "none to bring." | ROUTED(delivered-pipeline delayed-outcome fixture) | No accepted pipeline and no score supply the requested fixture.
§A:U6 "No register-authorised seat computed R9" | ROUTED(dng authorised posture-computation seat) | Existing execution restriction explains the omission; an authorized evidence supplier must resolve it.
§A:U9 "unchanged." | ROUTED(dng doctrine-consumer stewardship) | The fold-set item remains without a card or disposition.
§A:stale-map "No commit in the window touches it." | ROUTED(dng instance-map maintainer) | Refresh through the authorized writer; this filing does not upgrade the map.
§A:resource-terminals "not exercised this window" | ADOPTED | No substituted seat this window; the previously identified ordering gap remains.

## Findings

§K1 "No kernel subject existed." | ADOPTED | UNEXERCISED for qualifying acceptance; route actor diversity is mechanism evidence only.
§K2 "has reached no one" | REJECTED(FRICTION classification; reclassify INSTANCE-FAILURE) | Current escalation remained in receipts expressly reported as unreached. Existing code Human gates and Resource terminals require an owner-facing channel and continued eligible work. A reserved action stays reserved; this does not require the blocked seat to alter its scheduler. The carried §C9:K2 and §C8:K2 FRICTION lines answer distinct historical windows and are not rewritten.
§K3 "observer other than the claimant" | ADOPTED | FIT for three attributed observer release/re-scope exercises. Does not certify the missing aggregate identity or atomic-claim mechanism.
§K4 "Work is complete only on positive evidence" | ADOPTED | FIT for refusing unsupported completion and obtaining execution evidence. Measured finding refutations remain attributed, not independent verification here.
§K5 "0 `k5-declaration.json` dated inside the window" | ADOPTED | Preserve UNEXERCISED for the scoped declared-subject acceptance observable, consistent with the prior ruling. IF13/IF15 retain missing declaration practice; no filename is universally prescribed.
§K6 "No kernel subject was accepted." | ADOPTED | UNEXERCISED. Reported opposite-provider route keys confer no qualifying acceptance.
§K7 "Nothing was accepted under the kernel." | ADOPTED | UNEXERCISED; retain the accepted-but-held route item and missing typed closure as separate mechanism evidence.
§K8 "no artifact this filing read establishes" | ADOPTED | UNEXERCISED for reset-driven reopening. The usage discontinuity proves neither rotation nor reset; scheduler model mismatch is not itself a capacity event.
§K9 "rotation-readiness 5 of 10" | ADOPTED | INSTANCE-FAILURE remains. A rule repair without a successful exercise does not establish recovery; the drill additionally exposes inaccessible scheduler configuration.
§K10 "no machine-readable inventory and no `probed_under`" | ADOPTED | INSTANCE-FAILURE. Route account-bound inventory and actual-launcher verification to fleet tooling and dng dispatch maintainers; model pinning also needs its authorized scheduler owner.
§K11 "about twelve days later" | ADOPTED | INSTANCE-FAILURE for inaccessible daily history and uncorrected CLOSED assertions. Later commitment repairs availability prospectively, not the elapsed reporting gap.
§K12 "FIT on the sixth filing's harvest of 2026-10-16" | ADOPTED | Historical FIT is bus-verified for that completed harvest only, and K12 is counted as one of the 4 FIT on that ground alone. Seventh–tenth backlog and missed November 13 cadence receive no FIT credit; steward nonresponse is recorded separately.
§P:code subject-identity "0 of 3 records a tree OID" | ADOPTED | INSTANCE-FAILURE. Commit/patch identity observations do not supply the recorded K3 identity and acceptance binding.
§P:code claims "observer-released claims may replace leases" | ADOPTED | FIT for the three reported observer decisions.
§P:code claims-audit "no window receipt records one" | ADOPTED | INSTANCE-FAILURE for missing canonical-state audits; scratch execution alone does not establish confinement.
§P:code independent-key "No kernel subject was accepted." | ADOPTED | UNEXERCISED. The conditional non-producing-provider claim still requires contribution provenance, exact identity and valid acceptance.
§P:code resource-terminals "no rule orders a substituted seat's declaration" | ADOPTED | Preserve the adopted INSTANCE-FAILURE mechanism gap; do not invent a late substitution this window.
§P:code delivery-target "hosted validators run only after the mirror push" | ADOPTED | INSTANCE-FAILURE remains for missing pre-push validation coverage. Equivalent pre-push execution can satisfy the rule; the hosted service itself need not run before push.
§P:code dispatch-preflight "orders no resume-gate, inventory or parity read" | ADOPTED | INSTANCE-FAILURE. A seat's own model check is not the spending tool's complete retained preflight.
§P:measured-objective acceptance-evidence "No SCOREBOARD line falls inside the window" | ADOPTED | UNEXERCISED. Code-seat failures do not become measured-objective evidence because the project lists both profiles.

## Instance failures

§IF1+IF11 "historical, unchanged." | ADOPTED | Preserve historical status; no additional census entries.
§IF2 "repaired in the latent script." | ADOPTED | Latent repair only; no live-route exercise.
§IF3+IF4+IF10 "LATENT" | ADOPTED | Preserve latent status, without conformance credit.
§IF5 "No gate0 ran on the live route." | ADOPTED | Latent repair remains unexercised.
§IF6 "LIVE." | ADOPTED | Advertised merge mechanism still differs from the live path.
§IF7 "resolved at an earlier read, and outside git." | ADOPTED | Preserve the limited attributed earlier resolution.
§IF8 "both still absent from master." | ADOPTED | Capture-script gap remains.
§IF9 "No file outside the instance map names `CLOSURE_INCOMPLETE`." | ADOPTED | Typed closure gap remains.
§IF12 "drift stands." | ADOPTED | Record receipt-shape variation and missing schema; do not count repeated field variants as additional failures.
§IF13 "No rule, tool or hook names `k5-declaration`." | ADOPTED | Declaration-consumption gap remains; kernel compliance does not require this particular filename.
§IF14 "resolved" | ADOPTED | Preserve prior scope; hosted validation remains separately open.
§IF15 "0 declarations dated inside it." | ADOPTED | Current-window count retained; the sixth filing's correction of the fifth window remains binding.

## Untested

§U6 "The `posture:` line" | ROUTED(dng authorised posture-computation seat) | Obtain the required computation without overriding the filing seat's register.
§U8 "changed the grade the owner's saved engine emits" | ROUTED(dng measured-objective outcome bench) | Measure actual saved-engine outcomes, not assembly contact.
§U9 "still held with no card" | ROUTED(dng doctrine-consumer stewardship) | Local ownership/disposition remains owed.
§U10 "Answered:" | ADOPTED | Accept the attributed repair landing and subsequent CI success as answering the repair question. This closes neither pre-push validation parity nor every possible environmental cause.
§U11 "in a two-family seating" | ROUTED(dng independence-provenance bench) | A model family producing any part of the declared subject cannot supply its independent model key. Earlier component keys do not automatically transfer. Test an independent CI/human/third-class key or valid separately declared subjects.
§U12 "research definition of done and its stop rule" | ROUTED(dng owner/register bench) | Only the owner can settle the disputed reach; resumption does not establish the ruling's scope.
§U13 "who cleared it on 2026-10-28" | ROUTED(dng scheduler-forensics bench) | Preserve cause and actor as unknown.
§U14 "a route of this board's register or an exception" | ROUTED(dng owner/register bench) | Resolve landing authority and durable receipt location; keys alone establish neither.
§U15 "any channel the owner reads" | ROUTED(dng escalation-delivery bench) | Test delivery through an agreed owner-facing channel and retain the send/receipt witness. Actual human reading cannot be guaranteed by register wording; blocked-seat restrictions require a separately authorized actor.

## Instance map and counts

§Instance-map "REPORTED, not refreshed:" | ADOPTED | Retain the attributed stale code@r10 map, its code.md pin 5511ccb3 and its eight NONE rows. Bus pins are verified; this filing assesses r11 without upgrading the map, whose refresh stays routed to its maintainer (HEADER: revisions and map; §A:stale-map).
§Counts "Ledger totals" | ADOPTED | Recount confirms the filed 4 FIT · 1 FRICTION · 0 BREAK · 0 N/A · 7 UNEXERCISED and 8 separate INSTANCE-FAILURE lines, and "no verdict moved" against the ninth filing. As ruled, K2 moves FRICTION to INSTANCE-FAILURE (4 · 0 · 0 · 0 · 7; 9 separately). Not an additional census entry.

## Carried: ninth filing (blob 94a01ff3)

§C9:Subjects:kernel "Kernel subjects: none." | ADOPTED | Zero qualifying closures; no declarations.
§C9:Subjects:route "reported and never counted" | ADOPTED | Seven route landings retained as mechanism evidence, including the disclosed mixed-provider production failover.
§C9:Subjects:orchestrator "Two landings keyed off the cop's tick" | ADOPTED | Two additional landings retained; off-tick authority and private receipt location remain U14/K11 questions.
§C9:Subjects:measurement "Closed without a landing" | ADOPTED | Preserve MEASURED-NEGATIVE and RESCOPE/DONE measurement outcomes; neither establishes declared scorer acceptance.
§C9:Subjects:off-route "none beyond the two above" | ADOPTED | Nine total landings, seven committed receipts; do not equate receipt count with landing count.
§C9:Subjects:blocked-seam "The eighth filing's blocked seam, closed." | ADOPTED | Actual stall ended through owner-side acts; scope question U12 remains unanswered.
§C9:A:U7 "6 of 9." | ADOPTED-CONDITIONAL(dng outcome-reporting bench) | Six assembly-touching ranges; no emitted-grade inference.
§C9:A:U8 "partly derived, one more window." | ROUTED(dng measured-objective outcome bench) | DNG 1.7 decoder-input effect is attributed; affected saved-engine frames and emitted-grade change remain unmeasured.
§C9:A:independence-provenance "The exception, recorded at the act." | ROUTED(dng independence-provenance bench) | Six of seven route landings plus two off-tick landings report non-writing-provider keys. The failover subject has both producing families and no eligible model-class key; PARTIAL disclosure does not waive K6.
§C9:A:a.u4 "none to bring." | ROUTED(delivered-pipeline delayed-outcome fixture) | No qualifying fixture.
§C9:A:U6 "unchanged." | ROUTED(dng authorised posture-computation seat) | Same unresolved computation route.
§C9:A:U9 "unchanged." | ROUTED(dng doctrine-consumer stewardship) | Same unresolved fold-set route.
§C9:A:stale-map "No commit in the window touches it." | ROUTED(dng instance-map maintainer) | Stale declaration and map remain.
§C9:A:resource-terminals "exercised this window" | ADOPTED | Retain the substitution launch record; it does not repair the missing ordered pre-dispatch rule.
§C9:K1 "on every one of the nine landings" | ADOPTED | Restated by the tenth filing's §K1 with the same verdict (UNEXERCISED); same scoped ruling. The ninth window's route evidence stays in its own window.
§C9:K2 "Its cost ran on inside this window" | ADOPTED-CONDITIONAL(dng reserved-hold bench) | Preserve historical FRICTION for continued owner-reserved waiting and 134 no-op ticks. No kernel edit; the proposed continuation duty is already substantially in code Resource terminals. Historical windows remain distinct: this window's owner-reserved acts were escalated and answered by owner-side acts, and no escalation is reported unreached, so the tenth window's INSTANCE-FAILURE does not reach back.
§C9:K3 "on more seats than in the eighth" | ADOPTED | Restated by the tenth filing's §K3 with the same verdict (FIT); same scoped ruling. The historical exercises stay in their own window.
§C9:K4 "key 2's confirmed MAJOR stopped" | ADOPTED | Restated by the tenth filing's §K4 with the same verdict (FIT); same scoped ruling. The historical exercises stay in their own window.
§C9:K5 "0 of 7 window receipts name" | ADOPTED | Restated by the tenth filing's §K5 with the same verdict (UNEXERCISED); same scoped ruling, with the zero-declaration count scoped to the ninth window.
§C9:K6 "6 of 7 route landings and both orchestrator-session landings" | ADOPTED | Restated by the tenth filing's §K6 with the same verdict (UNEXERCISED); same scoped ruling. Reported route keys confer no qualifying acceptance.
§C9:K7 "SATURATION-OFFSET-FLAG holds keys FINAL ACCEPT and is not landed" | ADOPTED | Restated by the tenth filing's §K7 with the same verdict (UNEXERCISED); same scoped ruling.
§C9:K8 "This window's capacity event:" | ADOPTED | Restated by the tenth filing's §K8 with the same verdict (UNEXERCISED); same scoped ruling. The capacity failover stays a historical exercise in its own window.
§C9:K9 "New this window, a repair in rule:" | ADOPTED | INSTANCE-FAILURE; actual rotation stranded tasks and required owner acts. Rule repair is prospective and unexercised.
§C9:K10 "a desktop-versus-CLI drift only outside the repo" | ADOPTED | Restated by the tenth filing's §K10 with the same verdict (INSTANCE-FAILURE); same scoped ruling and the same route to fleet inventory tooling.
§C9:K11 "the two orchestrator-session landings' receipts live only" | ADOPTED | INSTANCE-FAILURE; eighth-window stall publication improved, but private landing receipts and uncorrected CLOSED assertions remain.
§C9:K12 "neither the seventh filing (pushed 2026-10-23) nor the eighth" | ADOPTED | Restated by the tenth filing's §K12 with the same verdict; same scoped ruling. The FIT is historical only (the sixth filing's harvest of 2026-10-16); the backlog receives no FIT credit.
§C9:P:code subject-identity "0 of 7 records a tree OID" | ADOPTED | Restated by the tenth filing's §P:code subject-identity with the same verdict (INSTANCE-FAILURE); same scoped ruling. The missing recorded identity stays in its own window.
§C9:P:code claims "Exercised on six card seats the cop released and relaunched" | ADOPTED | Restated by the tenth filing's §P:code claims with the same verdict (FIT); same scoped ruling. The historical exercises stay in their own window.
§C9:P:code claims-audit "none of the window's three docs commits adds a reflog" | ADOPTED | Restated by the tenth filing's §P:code claims-audit with the same verdict (INSTANCE-FAILURE); same scoped ruling.
§C9:P:code independent-key "a key whose family wrote no byte of the subject" | ADOPTED | Restated by the tenth filing's §P:code independent-key with the same verdict (UNEXERCISED); same scoped ruling.
§C9:P:code resource-terminals "1 of 1 substituted seats" | ADOPTED | INSTANCE-FAILURE mechanism status retained alongside reported timely practice. Producer failover does not preserve independent model eligibility merely by labeling the receipt PARTIAL.
§C9:P:code delivery-target "the seven route receipts records a clean Release build" | ADOPTED | Restated by the tenth filing's §P:code delivery-target with the same verdict (INSTANCE-FAILURE); same scoped ruling.
§C9:P:code dispatch-preflight "none of the window's 64 dispatches is ordered to retain" | ADOPTED | Restated by the tenth filing's §P:code dispatch-preflight with the same verdict (INSTANCE-FAILURE); same scoped ruling.
§C9:P:measured-objective acceptance-evidence "The two measurement cards used leave-one-project-out folds" | ADOPTED | Restated by the tenth filing's §P:measured-objective acceptance-evidence with the same verdict (UNEXERCISED); same scoped ruling.
§C9:IF1+IF11 "historical, unchanged." | ADOPTED | Status restated by the tenth filing's §IF1+IF11; same ruling, scoped to the ninth window.
§C9:IF2 "repaired in the latent script." | ADOPTED | Status restated by the tenth filing's §IF2; same ruling, scoped to the ninth window.
§C9:IF3+IF4+IF10 "LATENT" | ADOPTED | Status restated by the tenth filing's §IF3+IF4+IF10; same ruling, scoped to the ninth window.
§C9:IF5 "No gate0 ran on the live route." | ADOPTED | Status restated by the tenth filing's §IF5; same ruling, scoped to the ninth window.
§C9:IF6 "LIVE." | ADOPTED | Status restated by the tenth filing's §IF6; same ruling, scoped to the ninth window.
§C9:IF7 "resolved at an earlier read, and outside git." | ADOPTED | Status restated by the tenth filing's §IF7; same ruling, scoped to the ninth window.
§C9:IF8 "both still absent from master." | ADOPTED | Status restated by the tenth filing's §IF8; same ruling, scoped to the ninth window.
§C9:IF9 "No file outside the instance map names `CLOSURE_INCOMPLETE`." | ADOPTED | Status restated by the tenth filing's §IF9; same ruling, scoped to the ninth window.
§C9:IF12 "drift stands." | ADOPTED | Preserve array/string/object encodings and optional fields as historical schema drift.
§C9:IF13 "No rule, tool or hook names `k5-declaration`." | ADOPTED | Status restated by the tenth filing's §IF13; same ruling, scoped to the ninth window.
§C9:IF14 "resolved" | ADOPTED | Status restated by the tenth filing's §IF14; same ruling, scoped to the ninth window.
§C9:IF15 "0 declarations dated inside it." | ADOPTED | Status restated by the tenth filing's §IF15; same ruling, with zero declarations scoped to the ninth window.
§C9:U6 "The `posture:` line" | ROUTED(dng authorised posture-computation seat) | Restated by U6; route remains open.
§C9:U8 "whether the emitted grade moved" | ROUTED(dng measured-objective outcome bench) | Neither affected-frame prevalence nor grade effect is supplied.
§C9:U9 "still held with no card" | ROUTED(dng doctrine-consumer stewardship) | Restated by U9; route remains open.
§C9:U10 "Answered in part:" | ADOPTED | Preserve the then-running repair as partial progress; tenth-filing U10 supplies the later landing/green-CI answer. No retrospective ninth-window cure.
§C9:U11 "Whether a subject assembled by carrying" | ROUTED(dng independence-provenance bench) | Apply tenth U11's reading; no new qualifying exercise.
§C9:U12 "no artifact this filing read records" | ROUTED(dng owner/register bench) | Stall release does not answer the owner-ruling reach.
§C9:U13 "who cleared it on 2026-10-28" | ROUTED(dng scheduler-forensics bench) | Cause and actor remain unknown.
§C9:U14 "a route of this board's register or an exception" | ROUTED(dng owner/register bench) | Historical off-tick landings require their own authority answer.

## Carried: eighth filing (blob ac626991)

§C8:Subjects:kernel "Kernel subjects: none." | ADOPTED | Zero qualifying closures and declarations.
§C8:Subjects:route "reported and never counted" | ADOPTED | One attributed landed range; both providers contributed production/test bytes. No kernel acceptance credit.
§C8:Subjects:measurement "Closed without a landing" | ADOPTED | Retain two measured parity cards and the already-landed subpacket pointer; no held-out acceptance or default-change authority follows.
§C8:Subjects:off-route "Off-route landings: none." | ADOPTED | Preserve the sixteen-commit census and one landed range.
§C8:Subjects:blocked-seam "The blocked seam" | ADOPTED | Distinguish held scheduler slot, duplicate-direction caution, boot budget and disputed owner-ruling reach. They are not quota events or four independent kernel defects.
§C8:A:U7 "1 of 1." | ADOPTED-CONDITIONAL(dng outcome-reporting bench) | One assembly-touching range; no emitted-grade inference.
§C8:A:U8 "partly derived, one more window." | ROUTED(dng measured-objective outcome bench) | Default-false switches and four-clip parity do not establish the saved engine's emitted outcome.
§C8:A:independence-provenance "not the whole producer set" | ROUTED(dng independence-provenance bench) | Accept the substantive lineage warning: carried Claude production plus Codex tests make both model families producers. Earlier Sol component keys do not automatically qualify for the assembled subject.
§C8:A:a.u4 "none to bring." | ROUTED(delivered-pipeline delayed-outcome fixture) | No qualifying fixture.
§C8:A:U6 "unchanged." | ROUTED(dng authorised posture-computation seat) | Computation remains absent.
§C8:A:U9 "unchanged." | ROUTED(dng doctrine-consumer stewardship) | Fold-set remains unopened.
§C8:A:stale-map "Its K9 row is overtaken further" | ROUTED(dng instance-map maintainer) | Record six drill receipts as attributed; update the obsolete map through its writer.
§C8:A:resource-terminals "not exercised this window" | ADOPTED | No substitution exercise; ordering gap persists.
§C8:K1 "the one landing's acceptance evidence includes key 2" | ADOPTED | Restated by the tenth filing's §K1 with the same verdict (UNEXERCISED); same scoped ruling. This window's actor evidence is retained as history.
§C8:K2 "Moved from FIT" | ADOPTED-CONDITIONAL(dng reserved-hold bench) | Preserve FRICTION for 108-hour owner-reserved scheduler waiting and addressed alarms. Disputed extension of a research ruling remains U12, not established authority. Neither circumstance proves compliance impossible or supplies second-profile evidence. Historical windows remain distinct: the reserved act's alarm fired to its register-named USER addressee, whereas the tenth window's escalation is reported unreached; the tenth window's INSTANCE-FAILURE does not reach back.
§C8:K3 "Kept from the seventh filing (FIT: 5 observer releases)." | ADOPTED | Restated by the tenth filing's §K3 with the same verdict (FIT); same scoped ruling. The historical exercises stay in their own window.
§C8:K4 "key 2 BLOCKERs confirmed in round 1 (3/1/2)" | ADOPTED | Restated by the tenth filing's §K4 with the same verdict (FIT); same scoped ruling. The historical exercises stay in their own window.
§C8:K5 "0 of the 7 cards changed in the window" | ADOPTED | Restated by the tenth filing's §K5 with the same verdict (UNEXERCISED); same scoped ruling, with the zero-declaration count scoped to the eighth window.
§C8:K6 "key 1 is from the provider opposite the receipt-recorded authors" | ADOPTED | Restated by the tenth filing's §K6 with the same verdict (UNEXERCISED); same scoped ruling. Reported route keys confer no qualifying acceptance.
§C8:K7 "the one landing reached nested-repo master by `--ff-only`" | ADOPTED | Restated by the tenth filing's §K7 with the same verdict (UNEXERCISED); same scoped ruling.
§C8:K8 "This window's one quota event:" | ADOPTED | Restated by the tenth filing's §K8 with the same verdict (UNEXERCISED); same scoped ruling.
§C8:K9 "the adopted failure recurred once" | ADOPTED | INSTANCE-FAILURE. One rotation required task recreation and authentication; the other's successful catch-up does not erase it.
§C8:K10 "This window's two rotations recorded account identity only outside" | ADOPTED | Restated by the tenth filing's §K10 with the same verdict (INSTANCE-FAILURE); same scoped ruling and the same route to fleet inventory tooling.
§C8:K11 "the WORK.md working copy" | ADOPTED | INSTANCE-FAILURE: six-day stall invisible to a fresh clone, alongside existing reporting defects. Later publication is recorded in C9.
§C8:K12 "has no disposition yet" | ADOPTED | Restated by the tenth filing's §K12 with the same verdict; same scoped ruling. The FIT is historical only (the sixth filing's harvest of 2026-10-16); the backlog receives no FIT credit.
§C8:P:code subject-identity "The binding is per-file blob identity plus `patch-id`" | ADOPTED | Restated by the tenth filing's §P:code subject-identity with the same verdict (INSTANCE-FAILURE); same scoped ruling. The historical identity failure is retained.
§C8:P:code claims "once on an expiring lease, the research writer's" | ADOPTED | Restated by the tenth filing's §P:code claims with the same verdict (FIT); same scoped ruling. The historical exercises stay in their own window.
§C8:P:code claims-audit "Its receipt mentions neither reflog nor stash (0 of 1)" | ADOPTED | Restated by the tenth filing's §P:code claims-audit with the same verdict (INSTANCE-FAILURE); same scoped ruling.
§C8:P:code independent-key "the Claude family produced the carried production bytes" | ADOPTED | Restated by the tenth filing's §P:code independent-key with the same verdict (UNEXERCISED); same scoped ruling.
§C8:P:code resource-terminals "a record written with the act" | ADOPTED | INSTANCE-FAILURE mechanism status. A degraded-disposition label is not an ordered substitution declaration before dispatch.
§C8:P:code delivery-target "Hosted CI after the mirror push read success." | ADOPTED | Restated by the tenth filing's §P:code delivery-target with the same verdict (INSTANCE-FAILURE); same scoped ruling.
§C8:P:code dispatch-preflight "none of the window's 25 dispatches is ordered to retain" | ADOPTED | Restated by the tenth filing's §P:code dispatch-preflight with the same verdict (INSTANCE-FAILURE); same scoped ruling.
§C8:P:measured-objective acceptance-evidence "The window's two measurement cards measured exact parity" | ADOPTED | Restated by the tenth filing's §P:measured-objective acceptance-evidence with the same verdict (UNEXERCISED); same scoped ruling. Measurement parity is not declared acceptance.
§C8:IF1+IF11 "historical, unchanged." | ADOPTED | Restated by the tenth filing's §IF1+IF11; same status ruling, scoped to this window.
§C8:IF2 "repaired in the latent script." | ADOPTED | Restated by the tenth filing's §IF2; same status ruling, scoped to this window.
§C8:IF3+IF4+IF10 "LATENT" | ADOPTED | Restated by the tenth filing's §IF3+IF4+IF10; same status ruling, scoped to this window.
§C8:IF5 "No gate0 ran on the live route" | ADOPTED | Restated by the tenth filing's §IF5; same status ruling, scoped to this window.
§C8:IF6 "LIVE." | ADOPTED | Restated by the tenth filing's §IF6; same status ruling, scoped to this window.
§C8:IF7 "resolved at an earlier read, and outside git." | ADOPTED | Restated by the tenth filing's §IF7; same status ruling, scoped to this window.
§C8:IF8 "both still absent from master." | ADOPTED | Restated by the tenth filing's §IF8; same status ruling, scoped to this window.
§C8:IF9 "No file outside the instance map names `CLOSURE_INCOMPLETE`." | ADOPTED | Restated by the tenth filing's §IF9; same status ruling, scoped to this window.
§C8:IF12 "drift stands, no new field." | ADOPTED | Preserve this window's particular object/prose/mirror encoding; no new field is claimed.
§C8:IF13 "No rule, tool or hook names `k5-declaration`" | ADOPTED | Restated by the tenth filing's §IF13; same status ruling, scoped to this window.
§C8:IF14 "resolved" | ADOPTED | Restated by the tenth filing's §IF14; same status ruling, scoped to this window.
§C8:IF15 "0 declarations dated inside it." | ADOPTED | Restated by the tenth filing's §IF15; same status ruling, scoped to this window.
§C8:U6 "The `posture:` line" | ROUTED(dng authorised posture-computation seat) | Route remains open.
§C8:U8 "the owner's saved engine emits" | ROUTED(dng measured-objective outcome bench) | Saved switch values and emitted effects remain unmeasured.
§C8:U9 "still held with no card" | ROUTED(dng doctrine-consumer stewardship) | Route remains open.
§C8:U10 "whether it is environment-bound or order-dependent" | ROUTED(dng hosted-CI causality bench) | Tenth U10 answers repair landing and subsequent green CI. It does not explicitly resolve this original environment-versus-order question; retain that residual.
§C8:U11 "both families produced bytes of it" | ROUTED(dng independence-provenance bench) | No seated model family qualifies for the assembled subject under the stated production facts; test an eligible independent class.
§C8:U12 "It is an owner question, not a repo fact." | ROUTED(dng owner/register bench) | Obtain an explicit scope ruling.
§C8:U13 "No artifact records either" | ROUTED(dng scheduler-forensics bench) | Neither cause nor clearing actor is established.

## Carried: seventh filing (blob 27aeb992)

§C7:Subjects:released-lineage "The sixth filing's one aggregate-only landing is released here" | ADOPTED | Accept the released historical landing identity; it is not an additional seventh-window landing or kernel closure.
§C7:Subjects:kernel "Kernel subjects: none." | ADOPTED | Zero qualifying closures and declarations.
§C7:Subjects:route "reported and never counted" | ADOPTED | Twenty-three route landings; nineteen same-commit and four rebased. Patch/blob corroboration does not replace declared delivered-subject identity. The twenty-fourth added receipt is historical.
§C7:Subjects:off-route "Off-route landings: none." | ADOPTED | Preserve the attributed 124-commit census and range accounting.
§C7:A:U7 "12 of 23." | ADOPTED-CONDITIONAL(dng outcome-reporting bench) | Twelve assembly-touching landings under the disclosed predicate; no emitted-grade inference.
§C7:A:U8 "partly derived, one more window." | ROUTED(dng measured-objective outcome bench) | Preserve flag-off observations and four other assembly effects; saved-engine settings and actual grade change remain unanswered.
§C7:A:independence-provenance "provider overlap alone does not decide it" | ROUTED(dng independence-provenance bench) | Twenty-three approach/key provider overlaps require contribution analysis. Five regraded non-ACCEPTs require retained adjudication evidence; the unidentified FACTORY-D2 regrader remains unresolved.
§C7:A:a.u4 "none to bring." | ROUTED(delivered-pipeline delayed-outcome fixture) | No qualifying fixture.
§C7:A:U6 "unchanged." | ROUTED(dng authorised posture-computation seat) | Computation remains absent.
§C7:A:U9 "not the cop's to open" | ROUTED(dng doctrine-consumer stewardship) | Route to the authorized writer; cop restrictions do not discharge the item.
§C7:A:stale-map "two more of its rows are overtaken" | ROUTED(dng instance-map maintainer) | Reconcile the production scoreboard caller and resume-drill evidence with stale NONE/gap descriptions.
§C7:A:resource-terminals "not exercised this window" | ADOPTED | No substituted seat; mechanism gap remains.
§C7:K1 "all 23 route receipts name an author" | ADOPTED | Restated by the tenth filing's §K1 with the same verdict (UNEXERCISED); same scoped ruling.
§C7:K2 "Everything unlisted is autonomous." | ADOPTED | Preserve historical FIT for twenty-three autonomous landings and registered escalations. C8's subsequent FRICTION and tenth-window INSTANCE-FAILURE do not rewrite this window.
§C7:K3 "5 receipts record a seat the cop decided FROZEN" | ADOPTED | Restated by the tenth filing's §K3 with the same verdict (FIT); same scoped ruling. The five claim releases remain historical FIT.
§C7:K4 "RCB2-2 took three rounds" | ADOPTED | Restated by the tenth filing's §K4 with the same verdict (FIT); same scoped ruling. The historical exercises stay in their own window.
§C7:K5 "0 of the 23 receipts" | ADOPTED | Restated by the tenth filing's §K5 with the same verdict (UNEXERCISED); same scoped ruling, with the zero-declaration count scoped to the seventh window.
§C7:K6 "23 of 23 route landings carry a key 1" | ADOPTED | Restated by the tenth filing's §K6 with the same verdict (UNEXERCISED); same scoped ruling. Reported route keys confer no qualifying acceptance.
§C7:K7 "all 23 route landings reached nested-repo master" | ADOPTED | Restated by the tenth filing's §K7 with the same verdict (UNEXERCISED); same scoped ruling.
§C7:K8 "each ended at once on a weekly usage limit" | ADOPTED | Restated by the tenth filing's §K8 with the same verdict (UNEXERCISED); same scoped ruling.
§C7:K9 "Exercised three times in this window" | ADOPTED | INSTANCE-FAILURE for recurring missing tasks and owner-dependent recovery; later rule changes do not erase these rotations.
§C7:K10 "the three rotations' account identity is recorded only outside" | ADOPTED | Restated by the tenth filing's §K10 with the same verdict (INSTANCE-FAILURE); same scoped ruling and the same route to fleet inventory tooling.
§C7:K11 "the ledger keeps no trace of the red interval" | ADOPTED | INSTANCE-FAILURE within current-row reporting; git history preserves the interval. Do not infer universal erasure or intentional deception.
§C7:K12 "The sixth filing (blob `cce576ba`) was harvested on 2026-10-16" | ADOPTED | Restated by the tenth filing's §K12 with the same verdict; same scoped ruling. The FIT is bus-verified for that completed harvest only.
§C7:P:code subject-identity "19 of 23 delivered the very commit the keys reviewed" | ADOPTED | Restated by the tenth filing's §P:code subject-identity with the same verdict (INSTANCE-FAILURE); same scoped ruling.
§C7:P:code claims "The observer-release path was exercised 5 times" | ADOPTED | Restated by the tenth filing's §P:code claims with the same verdict (FIT); same scoped ruling. The five claim releases remain historical FIT.
§C7:P:code claims-audit "0 of the 23 receipts mention a reflog or stash" | ADOPTED | Restated by the tenth filing's §P:code claims-audit with the same verdict (INSTANCE-FAILURE); same scoped ruling.
§C7:P:code independent-key "on 23 of 23 landings key 1's provider also reviewed" | ADOPTED | Restated by the tenth filing's §P:code independent-key with the same verdict (UNEXERCISED); same scoped ruling.
§C7:P:code resource-terminals "The latent gap stands in the rule" | ADOPTED | Preserve INSTANCE-FAILURE mechanism status; same-family relaunch is not cross-family substitution.
§C7:P:code delivery-target "Half repaired, and exercised." | ADOPTED | Restated by the tenth filing's §P:code delivery-target with the same verdict (INSTANCE-FAILURE); same scoped ruling.
§C7:P:code dispatch-preflight "none of the window's 302 dispatches is ordered to retain" | ADOPTED | Restated by the tenth filing's §P:code dispatch-preflight with the same verdict (INSTANCE-FAILURE); same scoped ruling.
§C7:P:measured-objective acceptance-evidence "the learned exposure target, landed behind a flag" | ADOPTED | Restated by the tenth filing's §P:measured-objective acceptance-evidence with the same verdict (UNEXERCISED); same scoped ruling. Scoreboard hashing without a run supplies no measured-objective acceptance.
§C7:IF1+IF11 "historical, unchanged." | ADOPTED | Restated by the tenth filing's §IF1+IF11; same ruling.
§C7:IF2 "repaired in the latent script" | ADOPTED | Restated by the tenth filing's §IF2; same ruling. Latent script edits do not establish live-route adoption.
§C7:IF3+IF4+IF10 "LATENT" | ADOPTED | Restated by the tenth filing's §IF3+IF4+IF10; same ruling.
§C7:IF5 "no gate0 ran on the live route" | ADOPTED | Restated by the tenth filing's §IF5; same ruling. Latent script edits do not establish live-route adoption.
§C7:IF6 "LIVE." | ADOPTED | Restated by the tenth filing's §IF6; same ruling.
§C7:IF7 "resolved at an earlier read, and outside git." | ADOPTED | Restated by the tenth filing's §IF7; same ruling.
§C7:IF8 "both still absent from master." | ADOPTED | Restated by the tenth filing's §IF8; same ruling.
§C7:IF9 "No file outside the instance map names `CLOSURE_INCOMPLETE`." | ADOPTED | Restated by the tenth filing's §IF9; same ruling.
§C7:IF12 "drift continues." | ADOPTED | Preserve seven combinations of receipt encodings and the nineteen new ciReleaseBuild fields as historical schema evidence.
§C7:IF13 "No rule, tool or hook names `k5-declaration`" | ADOPTED | Restated by the tenth filing's §IF13; same ruling.
§C7:IF14 "resolved" | ADOPTED | Restated by the tenth filing's §IF14; same ruling.
§C7:IF15 "0 declarations dated inside it." | ADOPTED | Restated by the tenth filing's §IF15; same ruling.
§C7:U6 "The `posture:` line" | ROUTED(dng authorised posture-computation seat) | Route remains open.
§C7:U8 "whether that engine sets" | ROUTED(dng measured-objective outcome bench) | Actual saved-engine settings remain unanswered.
§C7:U9 "the steward's open item, not a bench question" | ROUTED(dng doctrine-consumer stewardship) | Preserve the ownership task.
§C7:U10 "whether it is environment-bound or order-dependent" | ROUTED(dng hosted-CI causality bench) | Later repair answers the operational remedy; the original causal distinction is not explicitly answered.

## Header

HEADER: revisions and map | ROUTED(dng instance-map maintainer) | Assessment is r5/code@r11/measured-objective@r3; the instance still declares code@r10. Bus pins are verified; no retrospective upgrade.
HEADER: subjects | ADOPTED | Zero qualifying closures; three current route landings remain mechanism evidence.
HEADER: providers | ADOPTED | None is consistent with no sentinel-complete filing lanes. Subject-review providers do not populate this header.
HEADER: posture | ROUTED(dng authorised posture-computation seat) | POSTURE-NOT-R9-COMPUTED. Preserve the disclosed restriction and prior U6 route.
HEADER: health | ADOPTED | UNSATISFIED/PRESSURED is supported by missing acceptance and prolonged model hold.
HEADER: cadence and steward backlog | ADOPTED | Missed November 13 refile and undispositioned seventh–ninth filings are recorded. Historical October 16 K12 FIT supplies no current health credit.
HEADER: carried headers | ADOPTED | C7/C8/C9 retain zero closures, UNSATISFIED/PRESSURED, providers none and uncomputed posture. Their stale-map, posture and provenance routes remain; their windows are not additional census populations.
HEADER: carried coverage | ADOPTED | All carried K/profile lines, numbered statuses, bench answers, subjects and Untested items are answered above against this tenth-filing blob. Earlier blobs are not thereby independently marked HARVESTED. Their `## Instance map` and `## Counts` sections are answered by HEADER: carried headers and HEADER: revisions and map, not by separate `§` lines.
HEADER: prior routes | ADOPTED | U7 remains conditional; outcome, independence, delayed-outcome, posture, consumer and map routes remain open except the explicitly answered operational portion of U10.
