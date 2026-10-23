project: dng-auto-processor
kernel: fleet-factory-kernel r5
profile: code@r11 (primary) + measured-objective@r3 — kernel §6's row as harvested (M1)
instance: docs/KERNEL-INSTANCE-MAP.md on nested-repo master (written by card KERNEL-DOGFOOD-INSTANCE-MAP under docs/14 §0's kernel entry, landed `db197676`; KERNEL line DOGFOOD, ## Instance map). The map's own first line still declares code@r10 (## Instance map)
subjects: 0 end-to-end under the kernel, and 0 declared inside this window — no `k5-declaration.json` was written after 2026-10-15T02:00Z (K5). Reported as mechanism evidence and never counted: 23 landings on this board's own two-key route, each with a committed receipt; none declared a profile. 0 PRODUCT commits landed off that route (## Subjects).
window: 2026-10-15T02:00Z .. 2026-10-23T08:14Z (nested-repo master as it stood at the window's end)
health: assurance=UNSATISFIED operability=PRESSURED
providers: none (no lane cleared a sentinel for this filing)
posture: not computed — model review contributed (the route's approach reviews and keys), and the R9 tool is one PROMPT K names, which docs/13 P-STEWARD step 7e forbids the filing seat to run (U6, ROUTED; unchanged)

Seventh filing by this board. It is a re-run on PROMPT K §6's weekly cadence: the kernel (r5), `profiles/code.md` (r11) and
`profiles/measured-objective.md` (r3) are unchanged since the sixth filing, and the `KERNEL:` line below is byte-identical
to the sixth filing's. The sixth filing (blob `cce576ba`) was harvested on 2026-10-16: `dng-auto-processor.dispositions.md`
carries `filing_blob: cce576ba99229229d9dda4b2203154069703bdac` and answers it (46 `§` lines: 38 ADOPTED, 1
ADOPTED-CONDITIONAL, 0 REJECTED, 7 ROUTED; plus 10 `HEADER:` lines: 8 ADOPTED, 2 ROUTED), so no finding of the sixth
filing is carried forward undisposed. Its open routes (U7 conditional; U8, independence-provenance, §a.u4 and U6; U9; the
stale instance map) are re-answered below on this window's evidence, and every clause and profile line is re-measured
against r5, r11 and r3. The seat that writes it is `dng-design-steward`. It works from this board's own cards, receipts
and ledgers, and it ran no subject.

`assurance=UNSATISFIED`: no subject was declared or accepted under the kernel, and the product's own bar produced no
acceptance either — WORK.md's SCOREBOARD has no line inside the window (its newest is still `20260918-1356`).
`operability=PRESSURED`: 302 dispatches for 23 receipted landings (about 13 per landing against about 10 in the last
window), summed over the cop's nine daily-ledger lines dated 2026-10-15 to 2026-10-23 in WORK.md (140 ticks; the 10-15
line also covers the two hours before the window opened). The ledger's landed sum (23) now matches the 23 receipts day
by day. Every daily line reads `ci=success` as it stands at the window's end, and that is again not the whole CI story:
master's hosted CI was red on one test after one landing (P:code delivery-target; the ledger read `ci=failure` at
2026-10-18 04:38Z and was rewritten in place, K11). Ten cop-tick commit subjects in the window mention a STALL (§7 alarm 1
or §3); one daily line's STALL note names a card of the parked lineage this filing counts and does not describe. Three account rotations fall in the window
(K9). The design steward seat, which keeps this filing and the docs, began 35 passes inside the window; of the 34 that
ended, 27 ended ACTED, 3 NO-WORK-DEFERRED-ON-LOAD and 4 NO-WORK (the 35th is the pass writing this filing). 14 commits in
the window touch only docs, packets or WORK.md (11 of their subjects name the steward).

Unqualified paths and commit ids are this board's repository. Evidence kept outside it is named by description, never by
path, as before (bus law 4). Doctrine paths are qualified. Three cards of one lineage are PARKED at the window's end with
review in flight; this filing counts them and does not describe them, and none of the window's 23 landings was opened
from that lineage. Every landing below is named. The sixth filing's one aggregate-only landing is released here, because
its lineage left flight: it is RAMP-SAMPLER-REAL-DCRAW-APPLY-WITNESS attempt 1 (`8c92296e`, landed 2026-10-13T03:47:30Z,
one test file, claude-sonnet-5-5 → gpt-5.6-sol / claude-opus-5-5, approach review gpt-6-astra REVISE 0/2/1 with 2
confirmed), opened from RAMP-CLIP-EXPOSURE-SINK-K-PASS, which closed MEASURED-NEGATIVE on 2026-10-20
(`packets/RAMP-CLIP-EXPOSURE-SINK-K-PASS.md`).

## Subjects

**Kernel subjects: none.** No rule, tool or hook reads `k5-declaration.json` (IF13), and none orders one written. In this
window nobody wrote one (IF15): a case-insensitive file-name search of the evidence ledgers for `k5-decl*` returns 4
files in all, none modified after the window opened. No landing receipt and no card changed in the window names a kernel
or profile revision.

**Landings on this board's own route, reported and never counted.** Each has a receipt at
`metrics/ratify/<TASK>/<attempt>/receipt.json` on master, and each landed by `git merge --ff-only` of an exact sha onto
nested-repo master. "Keys' subject" is the receipt's `keysSubjectSha`. The last column is the receipt's
`rangeEnum.surplusProduct` (PRODUCT paths, docs/14 §4's closed set, the delivered range carries beyond the keys'
subject). "Assembly" is the feature assembly the landed range changes beyond tests and tooling. Author → key 1 / key 2
names the implementing author(s).

| Task / attempt | Keys' subject → landed (tree same?) | Assembly | Author → key 1 / key 2 | Surplus PRODUCT |
|---|---|---|---|---|
| RATIFY-RECEIPTS-461BF565-DISPOSITION / 1 | 54188672 → 54188672 (yes) | none (one receipt file, inert) | gpt-5.6-sol → claude-fable-5-1 / claude-opus-5-5 | 0 |
| RAMP-GATE-DECISION-READ-ONCE / 1 | 5be91a30 → 5be91a30 (yes) | Core (`AutoProcessor.cs`) | gpt-5.6-sol → claude-fable-5-1 / claude-opus-5-5 | 0 |
| MANIFEST-RECEIPT-ENVELOPE-OMISSION-WITNESS / 1 | 64a4b523 → 64a4b523 (yes) | tests only | claude-sonnet-5-5 → gpt-5.6-sol / claude-opus-5-5 | 0 |
| HOOK-GOVERNING-DOCS-NO-BUILD / 2 | 10ea8005 → 8fbec461 (no: inert rebase) | none (hook, tools) | gpt-5.6-sol, then gpt-6-astra → claude-fable-5-1 / claude-opus-5-5 (round 1 key 2 REVISE) | 0 |
| BUILD-PROFILE-EXCLUDE-PROJECT-BLANK-VALUE / 1 | e40eff8a → e40eff8a (yes) | CorpusBridge | claude-sonnet-5-5 → gpt-6.1-sol / claude-opus-5-5 | 0 |
| UNUSED-ANCHOR-GAP-CULTURE-ROUNDING / 1 | c4cf4f0d → c4cf4f0d (yes) | Core (`AutoProcessor.cs`) | gpt-6.1-sol → claude-fable-5-1 / claude-opus-5-5 | 0 |
| FACTORY-D2-RULE-CHECKS-BATCH-PASS / 1 | addeb29a → addeb29a (yes) | none (tools, hook, CI) | claude-sonnet-5-5 → gpt-6.1-sol / claude-opus-5-5 | 0 |
| ELTB-2-OL-AT-INGEST / 2 | ab5aa3bd → ab5aa3bd (yes) | Core | claude-sonnet-5-5, then claude-fable-5-1 → gpt-6.1-sol / claude-opus-5-5 (round 1 key 1 BLOCKER, confirmed) | 0 |
| ELTB-1-BISECTION-SOLVER / 1 | 8ac09879 → 3b27141b (no: rebased over ELTB-2's PRODUCT commit, disjoint paths) | Core | gpt-6.1-sol → claude-fable-5-1 / claude-opus-5-5 | 0 |
| RCB2-1-CONTROL-BYTES-CHECK / 1 | 2f6a783d → 2f6a783d (yes) | none (tools) | gpt-6.1-sol → claude-fable-5-1 / claude-opus-5-5 | 0 |
| ELTB-3-CONDITIONAL-TARGET-FIT / 3 | 8d7dd999 → 8d7dd999 (yes) | Core | claude-sonnet-5-5, then claude-fable-5-1 → gpt-6.1-sol / claude-opus-5-5 | 0 |
| RCB2-2-PRE-RESET-SCRIPTS-CHECK / 3 | d0533525 → d0533525 (yes) | none (tools) | claude-sonnet-5-5, then claude-fable-5-1 → gpt-6.1-sol / claude-opus-5-5 | 0 |
| ELTB-4-FLAG-WIRING / 1 | 8e265798 → 8e265798 (yes) | Core | claude-sonnet-5-5 → gpt-6.1-sol / claude-opus-5-5 | 0 |
| LEARN-PROJECT-DCRAW-SCRATCH-CLEANUP-FLAKE / 3 | 68487e6d → 68487e6d (yes) | tests only | claude-fable-5-1 → gpt-6.1-sol / claude-opus-5-5 | 0 |
| RCB2-3-HOOK-CI-RULE-MAP / 1 | 5696b754 → 5696b754 (yes) | none (hook, CI) | gpt-6.1-sol → claude-fable-5-1 / claude-opus-5-5 | 0 |
| LEARNED-TARGET-OL-BACKFILL / 2 | f2ad578d → f2ad578d (yes) | Core, CorpusBridge | claude-sonnet-5-5, then claude-fable-5-1 → gpt-6.1-sol / claude-opus-5-5 | 0 |
| CORPUS-EVIDENCE-COMMIT-20261019 / 1 | 0b90e416 → 0b90e416 (yes) | none (corpus evidence, inert) | claude-sonnet-5-5 → gpt-6.1-sol / claude-opus-5-5 | 0 |
| SESSION-CHECKPOINT-PIN-20261019 / 1 | da363373 → da363373 (yes) | none (tools, factory pins) | claude-sonnet-5-5 → gpt-6.1-sol / claude-opus-5-5 | 0 |
| SINK-ANCHOR-RECEIPT-UNCHECKED-ROUTES-WITNESS / 2 | 41193830 → 41193830 (yes) | tests only | gpt-6.1-sol, then gpt-6-astra → claude-fable-5-1 / claude-opus-5-5 (round 1 key 2 REVISE) | 0 |
| APP-ADD-FINISHED-PROJECT-ZERO-CLIP-INCOMPLETE-SCAN / 1 | 970e9b69 → c677cb9a (no: inert rebase) | App | gpt-6.1-sol → claude-fable-5-1 / claude-opus-5-5 | 0 |
| LEARNED-TARGET-OL-TRACE-ORACLE-BATCH-PASS / 1 | 0a901382 → 1d580153 (no: rebased over APP-ADD-FINISHED's PRODUCT commit, disjoint paths) | Core, CorpusBridge | claude-sonnet-5-5 → gpt-6.1-sol / claude-opus-5-5 | 0 |
| LEARNED-TARGET-OL-BACKFILL-DATA-2A-APPLY / 1 | b87b5d28 → b87b5d28 (yes) | Core | gpt-6.1-sol → claude-fable-5-1 / claude-opus-5-5 | 0 |
| LEARNED-TARGET-OL-BACKFILL-DATA-2B-DATA / 1 | 93930cee → 93930cee (yes) | Core (one pin), `profiles/` data | gpt-6.1-sol → claude-fable-5-1 / claude-opus-5-5 | 0 |

19 of 23 landings have `keysSubjectSha` equal to `landedSha`. The other 4 were rebased after their keys: 2 over inert
bookkeeping only (HOOK-GOVERNING-DOCS-NO-BUILD, APP-ADD-FINISHED-PROJECT-ZERO-CLIP-INCOMPLETE-SCAN) and 2 over another
landing's PRODUCT commit that shares no path with the subject (ELTB-1 over `ab5aa3bd`, TRACE-ORACLE over `c677cb9a`),
which docs/14 §4's narrowed void test permits; each records blob identity and `patch-id --stable` unchanged and a green
hook re-run on the delivered sha. 16 landed at attempt 1, 4 at attempt 2 and 3 at attempt 3. A 24th receipt file added in
the window, `metrics/ratify/8c9ca32/receipt.json`, is not a landing of this window: it is the September receipt of an
earlier landing, committed by RATIFY-RECEIPTS-461BF565-DISPOSITION on a recorded USER disposition. Re-derive the file
count with `git -C <repo> log --since=2026-10-15T02:00Z --until=2026-10-23T08:14Z --diff-filter=A --name-only --format= master --
'metrics/ratify/*/receipt.json' | grep -c .` (24).

**Off-route landings: none.** The window's master history is 124 commits, all first-parent. 32 touch a PRODUCT path, and
every one lies inside the delivered range of one of the 21 landings above that touch PRODUCT. The other 92 are 76 cop
bookkeeping commits, 14 commits touching only docs, packets or WORK.md, and the two inert-only landings
(CORPUS-EVIDENCE-COMMIT-20261019, RATIFY-RECEIPTS-461BF565-DISPOSITION).

## Answers to the benches the last harvest routed

- **U7 (ADOPTED-CONDITIONAL, dng outcome-reporting bench), the O2 denominator across a sixth window: 12 of 23.** Same
  predicate: landings whose delivered range touches a feature assembly — every `DngAutoProcessor.*/` directory holding a
  `.csproj`, minus `*.Tests` (Core, App, CorpusBridge). The 12 are the rows above whose Assembly cell names one. The 11
  that touch none change tests only (3), factory tooling, hook or CI (6), or inert data (2). The earlier windows read 4
  of 11, 6 of 14, 3 of 11, 7 of 15 and 12 of 17, each within its own receipted population. Assembly contact is not proof
  of a changed emitted grade (the dispositions' condition), and this filing does not claim it.
- **U8 (ROUTED, dng measured-objective outcome bench), the emitted-grade effect: partly derived, one more window.** Of
  the 12 assembly landings, 8 belong to one owner-decided lever, the learned exposure target (ELTB-1 to ELTB-4,
  LEARNED-TARGET-OL-BACKFILL, TRACE-ORACLE, and BACKFILL-DATA-2A and 2B). Its switch, `EngineConfig.LearnedExposureTarget`,
  defaults to false (`DngAutoProcessor.Core/Models/RulesEngine.cs:627`), and its flag-off behaviour is witnessed by a
  landed test file, `DngAutoProcessor.Tests/LearnedExposureTargetFlagOffIdentityTests.cs` (ELTB-4 and 2A-APPLY), which
  the receipts describe as byte identity of the sampler sequence, XMP bytes and effective-config bytes with the flag off.
  ELTB-4's receipt states the default flip is the USER's. BACKFILL-DATA-2B adds data to the committed house-style profile
  and teaching store under `profiles/` that is read only when the flag is on. Of the other 4: an emit-decision change
  (`5be91a30`) whose receipt states it is identical when the configuration does not change during a run; a warning-text
  format (`c4cf4f0d`); a CorpusBridge refusal of a blank argument (`e40eff8a`); and an App refusal message
  (`c677cb9a`). None of these four is a grade computation on its face. Still not derived: whether the owner's saved engine
  sets `LearnedExposureTarget` or `PropagateManualGrades` (the latter has no initialiser, `RulesEngine.cs:203`, so its
  class default is false; a saved engine's own value governs and was not read). No SCOREBOARD line in the window measures
  an emitted grade.
- **Independence-provenance bench (ROUTED; P:code independent-key): the contribution records, for this window.** On all
  23 landings key 1 is from the provider opposite the author's (11 Codex-authored landings take `claude-fable-5-1`; 12
  Claude-authored take `gpt-6.1-sol`, or `gpt-5.6-sol` on MANIFEST-RECEIPT), and key 2 is `claude-opus-5-5` (three
  receipts record it by the alias `opus`). On 10 landings the approach reviewer and key 1 are the same model: 9
  Codex-authored with `claude-fable-5-1` in both seats (RATIFY-RECEIPTS, RAMP-GATE, HOOK-GOVERNING-DOCS, UNUSED-ANCHOR,
  RCB2-1, RCB2-3, SINK-ANCHOR, APP-ADD-FINISHED, BACKFILL-DATA-2B) and 1 Claude-authored with `gpt-6.1-sol` in both
  (CORPUS-EVIDENCE). On the other 13 they are different models of one provider: 2 Codex-authored with an
  Opus approach review (ELTB-1 records `claude-opus-5-5`, BACKFILL-DATA-2A the alias `opus`) and 11 Claude-authored with a `gpt-6-astra` approach
  review. So on 23 of 23 landings key 1's provider also reviewed the approach the author then implemented (11 of 11 in
  the last window). Each receipt's approach-review verdict and counts are in its `seats` record. One more observation
  from the same receipts bears on the bench without deciding it: on 5 landings key 1's final-round verdict was not
  ACCEPT and the subject landed after its findings were re-graded — ELTB-3 (a BLOCKER refuted to MINOR by the cop's
  paired-mutation probe), ELTB-4 (a MAJOR refuted to MINOR by key 2's serialization mutant), LEARN-PROJECT-DCRAW (a MAJOR
  refuted to MINOR by measurement under load), LEARNED-TARGET-OL-BACKFILL round 2 (2 MAJOR refuted to MINOR) and
  FACTORY-D2 (one confirmed MAJOR with its severity dropped, `verdictRederived` ACCEPT). Where a receipt names the re-grading seat it is the cop or key 2 (FACTORY-D2's records `verdictRederived` and names none), and no receipt records the author re-grading. Whether the approach-review class makes key 1's provider a producer of the subject is not
  decided here, and provider overlap alone does not decide it (the dispositions' words).
- **§a.u4 (ROUTED, delivered-pipeline delayed-outcome fixture): none to bring.** This board accepted no subject under the
  kernel, and no SCOREBOARD line falls in the window.
- **U6 (ROUTED, authorised posture-computation seat): unchanged.** No register-authorised seat computed R9 for this
  filing, and no owner word authorising one is recorded in docs/14 §0.
- **U9 (ROUTED, dng doctrine-consumer stewardship): unchanged.** WORK.md item 3 still holds the 2026-10-09 doctrine-consumer
  fold-set routing line as unopened and not the cop's to open (docs/13 P-COP bars a tick from editing docs/12-14); no
  card and no docs commit in the window acts on it.
- **Stale instance map (HEADER, ROUTED to its authorised maintainer): unchanged, and two more of its rows are overtaken**
  (## Instance map).
- **P:code resource-terminals (ADOPTED as an INSTANCE-FAILURE): not exercised this window**, reported on that line.

## Clauses

K1 | UNEXERCISED | "A candidate is never accepted on evidence whose only author is its producer" | No kernel subject existed. Reported without credit: all 23 route receipts name an author whose model is neither key's, and no PRODUCT commit landed off the route. Five landings proceeded over a key 1 non-ACCEPT whose findings the cop or key 2 re-graded (independence-provenance bench above); no author re-graded a finding against its own subject | PROOF: a kernel subject accepted here on receipts naming one actor for production and acceptance

K2 | FIT | "Everything unlisted is autonomous. Escalation goes to the owner for decisions reserved by that register" | Register: docs/14 §0 (USER rulings verbatim) plus WORK.md RULES rule 3. Taken without asking because the register allowed it: 23 route landings, none needing an owner act at landing. Reserved decisions went to the owner and were recorded as his: the learned-exposure-target adoption is routed as "USER-decided" (WORK.md 2026-10-17 13:20Z) and its flag ships false with the flip named the USER's (ELTB-4 receipt); the corpus-evidence commit and the session-checkpoint pin were opened on USER selections recorded in a P-RESUME receipt (WORK.md 2026-10-19 18:10Z and 2026-10-20 00:12Z); after the 2026-10-19 rotation a stranded scheduled task was re-created only on the USER's answer, never by a seat on its own (K9). Escalations went where the register sends them: 8 OWNER-DEFECT lines dated in the window and one undated one a cop tick appended in it, each naming its artifact, and none of the window's 76 cop-tick commits touches docs/12, docs/13 or docs/14 | PROOF: an owner-reserved act taken here with no §0 entry authorising it

K3 | FIT | "under a claim an observer other than the claimant can decide stale and release; an expiring lease is one such mechanism" | Mechanism unchanged: the card's owner line plus a launch json written before the launch (docs/14 §3), with staleness decided from outside the seat by §3's liveness rule. Exercised in this window: 5 receipts record a seat the cop decided FROZEN and whose claim it released — a key 1 relaunched after its first launch sat 4 h 27 min without a first act (ELTB-1), two implement seats relaunched whole (ELTB-3 attempt 2, LEARNED-TARGET-OL-BACKFILL attempt 1), and two committers that froze after a green commit whose `binding.json` the cop then wrote from git (UNUSED-ANCHOR-GAP-CULTURE-ROUNDING, HOOK-GOVERNING-DOCS-NO-BUILD). The instance map's K3 row is still NONE for an identity held by one claimant at a time with an atomic claim | PROOF: a claim here still held after its seat was dead, with no observer able to release it

K4 | FIT | "Work is complete only on positive evidence it was asked to produce" | A round-1 key 1 BLOCKER confirmed on a decode-count baseline written as a formula rather than measured stopped ELTB-2 until attempt 2 measured it; RCB2-2 took three rounds (3, then 2 confirmed MAJOR) before both keys accepted; three measurement cards closed MEASURED-NEGATIVE rather than DONE (`packets/LEARNED-TARGET-OL-BACKFILL-DATA.md`, `packets/LEARNED-TARGET-OL-MATCHED-ESTIMATOR-DIAGNOSTIC.md`, `packets/RAMP-CLIP-EXPOSURE-SINK-K-PASS.md`); the flake card replaced a reproduction gate too weak to fail with deterministic lock witnesses before it landed (`packets/LEARN-PROJECT-DCRAW-SCRATCH-CLEANUP-FLAKE.md`); and a hosted CI test failure was recorded as "a finding, never load: a card after a reproduction" (WORK.md QUEUE 5). Counter-observation, kept here rather than credited: TRACE-ORACLE's receipt records key 1 ACCEPT 0/0/0 "thin: no line evidence", and the landing rested on key 2's 28 build-fresh mutants | PROOF: a card here closed DONE on a return code or a file's presence alone

K5 | UNEXERCISED | "Before work starts, a subject declares its profile and profile version." | 0 `k5-declaration.json` dated inside the window (IF15), and no landing receipt records a profile: 0 of the 23 receipts, and 0 of the cards changed in the window, name `code@r`, `measured-objective@r` or the kernel. The sweep that supports this negative: case-insensitive file-name search of the evidence ledgers for `k5-decl*` (4 in all, none modified after 2026-10-15T02:00Z) | PROOF: a subject accepted here whose acceptance receipt names a different identity or profile than its declaration

K6 | UNEXERCISED | "Every acceptance includes a key from an independence class other than the producer's." | No kernel subject was accepted. Reported without credit: 23 of 23 route landings carry a key 1 from the provider opposite the author's, and key 2 is `claude-opus-5-5` on all 23. The independence-provenance records are above | PROOF: an accepted subject here whose keys and producer share one provider

K7 | UNEXERCISED | "Acceptance and delivery are separate states." | Nothing was accepted under the kernel. Reported without credit: all 23 route landings reached nested-repo master by `--ff-only` of an exact sha, and all 23 receipts record the mirror sync (19 in a `mirror` field, 4 inside the `landing` text, each of the latter naming product byte identity). No typed `CLOSURE_INCOMPLETE` exists here (IF9). Hosted CI after one landing's sync was red (P:code delivery-target) | PROOF: an accepted subject here that never landed and that the next tick names unprompted

K8 | UNEXERCISED | "Reset events update capacity telemetry. They never open a gate by themselves." | Mechanism unchanged (docs/14 §2, "on EVIDENCE, never off the window"). In-window: on 2026-10-19 the last fires on the departing account of three scheduled tasks — the cop, the steward and one USER-owned task — each ended at once on a weekly usage limit whose reset the error dated three days later (recorded in the 2026-10-19 P-RESUME receipt); the seats ran again on the new account after the rotation, not on a reset; and no key seat failed over on capacity (P:code resource-terminals). No artifact this filing read records a quota reset as such, the observable's trigger | PROOF: a reset event here that by itself re-opened a darkened seat

K9 | INSTANCE-FAILURE | "A fresh session on a new account, with empty memory, resumes from the project's tree and the bus alone." | Exercised three times in this window, and the adopted failure recurred. Three account rotations are recorded, each by a P-RESUME receipt (2026-10-15 20:28Z, 2026-10-19 09:06Z and 2026-10-23 03:29Z; P-RESUME runs on the owner's "resume our work"). After each, the cop and the steward ran again on the new account by catch-up fire, and one scheduled task registered on the departing account was absent on the new one: on 10-15 and again on 10-23 the status-digest task, listed and not re-created; on 10-19 the usage-watch task, which the pass put to the USER and re-created only on the USER's answer. So a rotation still needs an owner step for the register's full seat set to run again. 0 lines added to docs/13 or docs/14 in the window mention P-RESUME, re-registration or inventory | no replacement | PROOF: a rotation here after which every scheduled seat the register authorises ran again with no owner step

K10 | INSTANCE-FAILURE | "Provider and model inventory is machine-scoped and probe-derived, and it records the account it was derived under." | Unchanged: no machine-readable inventory and no `probed_under` in the repo (the instance map's K10 row); the three rotations' account identity is recorded only outside the repo, in the P-RESUME receipts (SessionStart hook output, the scheduled-task partition each pass derived, and on 2026-10-23 a `claude auth status` re-check) | no replacement | PROOF: an in-repo inventory whose `probed_under` names the current account

K11 | INSTANCE-FAILURE | "R1–R5, R7, R8 and R9 apply to every report a factory makes about itself" | Unchanged: the two CLOSED lines `131ad1f2` appended (WORK.md, dated 2026-09-23 14:05Z) still stand with no correction line beside them, and the seat that found it may append nothing there but a CLOSED line (docs/13 P-STEWARD). Recurrence of the reporting-history observation the dispositions recorded: the 2026-10-18 daily-ledger line read `ci=failure` at 04:38Z and `ci=in_progress` at 09:55Z, and at the window's end it reads `ci=success`, so the ledger keeps no trace of the red interval; the board's WORK.md history and the cop's commit subjects keep it. This filing takes no credit for 23 route landings and asserts no posture it did not compute | no replacement | PROOF: a correction line beside that CLOSED line in the board's ledger

K12 | FIT | "The steward harvests every filing and answers each one." | The sixth filing (blob `cce576ba`) was harvested on 2026-10-16 (harvest `20261016T090409Z-078e6f76`): `dng-auto-processor.dispositions.md` carries its blob and answers every `§` line and header line, and `HARVESTS.md` carries its row (FIT 3 · FRICTION 0 · BREAK 0 · N/A 0 · UNEXERCISED 9). This re-file is the clause's other half. FENCE: the filing seat may not run `tools/harvest-status.py`, so the harvested state is read from the artifacts that tool reads | PROOF: a finding of the sixth filing with no disposition line

## Profile lines

P:code subject-identity | INSTANCE-FAILURE | "its identity is K3's `sha256` of that OID's lowercase hexadecimal text, with no trailing newline" | Held in the window: 0 PRODUCT paths beyond the keys' subject on 23 of 23 landings, and 19 of 23 delivered the very commit the keys reviewed. Not held: on the other 4 the delivered tree differs from the reviewed tree (2 by inert bookkeeping, 2 by another landing's disjoint PRODUCT commit), and the binding the receipt records is per-file blob identity plus `patch-id`, never a tree OID; and 0 of the 23 receipts record a tree OID or its K3 `sha256`, reviewed or delivered (a search of the receipts for a tree field finds none). The measured-objective half moved: `tools/scoreboard.ps1` now dot-sources `tools/scoreboard-input-identity.ps1` and hashes the eval set, store and base engine per clip (lines 99 and 121, landed in FACTORY-D2-RULE-CHECKS-BATCH-PASS's range), but no scoreboard run in the window exercised it | no replacement | PROOF: a receipt here recording each subject's tree OID and K3 digest, reviewed and delivered alike

P:code claims | FIT | "observer-released claims may replace leases" | The observer-release path was exercised 5 times in the window (K3): in each the cop, not the claimant, decided the seat frozen and released or re-dispatched its claim, and the card's attempt ledger records it. The longest interval between a seat's launch and its observer release was 4 h 27 min (ELTB-1's first key 1, which never made a first act) | PROOF: a claim here released by its own claimant's say-so, or held after its seat died with no observer able to release it

P:code claims-audit | INSTANCE-FAILURE | "Audit canonical state before and after: HEAD, index entries and flags, refs, reflogs, stash, tracked contents, and ignored/untracked path inventories" | Unchanged: for a mutation-capable key 2 (every key 2 here builds and runs the suite or a mutant battery), §10 step 6 records the SCRATCH worktree's removal, never the main checkout's state before and after; 0 of the 23 receipts mention a reflog or stash, and no line added to docs/14 in the window mentions either | no replacement | PROOF: a key-2 run here whose receipt records the main checkout's HEAD, index entries and flags, refs, reflogs, stash, tracked contents and ignored/untracked path inventories with content hashes, before and after

P:code independent-key | UNEXERCISED | "a verifier from another model family (R3) whose class has not become a producer of the subject" | No kernel subject was accepted. The contribution records the bench asked for are above: on 23 of 23 landings key 1's provider also reviewed the approach, on 10 of them in the very model that then held key 1 | PROOF: a subject here whose only other-provider key comes from a class that also wrote its product bytes

P:code resource-terminals | INSTANCE-FAILURE | "Before dispatch, declare any register-permitted substitution for a family-bound quorum seat" | The latent gap stands in the rule: docs/14 §2 orders a SINGLE-FAMILY round's `cross_family: UNAVAILABLE <provider> <UTC ISO>` label into "its receipt", written at landing, and no rule orders the substitution declared before dispatch; no line added to docs/14 in the window touches it. Not exercised this window: of 368 `launch*.json` files modified inside the window (searched to depth 4 of the evidence ledgers), 0 carry a cross-family label, and the one that names a failover is a same-family whole relaunch whose record says both families answered the tick's probe | no replacement | PROOF: a rule here that orders every substituted seat's declaration written before its dispatch, and a window in which each substituted seat's launch record carries it

P:code delivery-target | INSTANCE-FAILURE | "build the exact proposed record and run the validators and hooks that commit will face before any product push; refuse on failure" | Half repaired, and exercised. The sixth filing's gap was the build flags: docs/14 §4 now orders that "The build a landing must pass is CI's, not the hook's" — the landing runs the `Release build` step of `.github/workflows/factory-ci.yml` as it reads at the landed sha (steward commit `d237e8ec`, 2026-10-16T02:24Z, closing the cop's OWNER-DEFECT of 2026-10-14). All 20 landings after that commit record that run (19 in a `ciReleaseBuild` field, HOOK-GOVERNING-DOCS in its landing text); the 3 before it record none. What still stands: the hook's own build line still carries no `--warnaserror` (0 occurrences in `.githooks/pre-commit`; docs/14 calls aligning it "a card", and none is open); the landing runs CI's build step and the hook's filtered suite, not CI's other steps; and a hosted validator still failed after a landing. Master's CI run at `8d7dd999` (ELTB-3, landed 2026-10-18T03:13:25Z, the hook 3513/3513 on the pre-rebase subject, key 2 3513/3513 on 8d7dd999) failed 1 of 3513 on one `ProgramSettingsTests` case; the cop recorded it as a finding owed a card after a reproduction, and at the window's end no card is open for it. The ledger read `ci=failure` at 04:38Z and `ci=success` at `5696b754` by 14:30Z | no replacement | PROOF: a landing here whose hosted validators ran green before its mirror push

P:code dispatch-preflight | INSTANCE-FAILURE | "the spending tool runs the project's resume gate before dispatch and retains its result, the inventory snapshot and digest, and account-parity evidence" | Unchanged: docs/13 P-COP orders no resume-gate, inventory or parity read before dispatch, and no line added to docs/13 or docs/14 in the window adds one, so none of the window's 302 dispatches is ordered to retain them. The three rotations' parity evidence was read by the USER-started P-RESUME passes, not by the spending tool; this filing did not read every tick note for a seat that retained them unordered — the K10 gap | no replacement | PROOF: a tick receipt here that retains a resume-gate result, an inventory digest and parity evidence before its first dispatch

P:measured-objective acceptance-evidence | UNEXERCISED | "the declared scorer on a held-out fold the producer never tuned on" | No SCOREBOARD line falls inside the window (its newest is `20260918-1356`), so no candidate was scored by the declared scorer. The window's one new grade lever, the learned exposure target, landed behind a flag that ships false on a recorded owner decision; its fitting step uses nested leave-one-group-out inside the build (ELTB-3), and the window's measurement cards on it measured parity of a computation or closed MEASURED-NEGATIVE — neither is held-out acceptance of a candidate on the declared scorer | PROOF: a scored run in the window that this line missed

## Instance failures

Status of the earlier fifteen:
- **IF1, IF11**: historical, unchanged.
- **IF2: repaired in the latent script**; `tools/ratify.ps1` is still off the live landing path (0 of 23 window receipts land through it). One landing's range edited it (FACTORY-D2-RULE-CHECKS-BATCH-PASS, a launch-effort site).
- **IF3, IF4, IF10: LATENT**, as before.
- **IF5: repaired in the latent script**; no gate0 ran on the live route (0 of 23 receipts record one; ELTB-4 records why no scoreboard run was owed).
- **IF6: LIVE.** WORK.md:4 still reads "Merge: tools/ratify.ps1 (gate 0 + cross-family key + adversarial Claude key)".
- **IF7**: resolved at an earlier read, and outside git.
- **IF8: unchanged.** `tools/claude-review-capture.ps1` and `tools/codex-author-capture.ps1` are both still absent from master.
- **IF9: unchanged.** No file outside the instance map names `CLOSURE_INCOMPLETE`.
- **IF12: drift continues.** The window's 23 receipts use seven combinations of three encodings: `seats` as a role-tagged list (13), an object (8) or an object of strings (2); `rounds` as a prose string (8), a list (7), an object (4) or absent (4); the mirror record in a `mirror` field (19) or the `landing` text (4). A new `ciReleaseBuild` field appears on 19.
- **IF13: unchanged.** No rule, tool or hook names `k5-declaration` (a `git grep` of master's docs, tools, .githooks and scripts finds only the instance map); outside them, only two cards, both closed before the window opened, name it.
- **IF14: resolved**, as before; what hosted CI finds is P:code delivery-target, which this window exercised.
- **IF15: unchanged for this window.** 0 declarations dated inside it.

## Untested

U6 | The `posture:` line (ROUTED, unchanged). The same limit applies to `tools/harvest-status.py`.

U8 | Whether any of the 12 assembly landings changed the grade the owner's saved engine emits: in particular whether that engine sets `LearnedExposureTarget` or `PropagateManualGrades`. The class defaults are derived above; the saved engine was not read.

U9 | Not tested here; read from master WORK.md only: the doctrine-consumer fold-set routing line of 2026-10-09 is still held in item 3 with no card. Its fate is the steward's open item, not a bench question.

U10 | Whether the hosted CI failure at `8d7dd999` (one `ProgramSettingsTests` case, green in the local hook and key 2's run) reproduces, and whether it is environment-bound or order-dependent. The board's own record owes a card after a reproduction; none ran in the window.

## Instance map

KERNEL: DOGFOOD fleet-factory-kernel r5 · profile code@r10 + measured-objective@r3 · instance docs/KERNEL-INSTANCE-MAP.md · since 2026-10-02

The instance map is `docs/KERNEL-INSTANCE-MAP.md` on nested-repo master; this section points at it and keeps no table.
Its first line declares `kernel: fleet-factory-kernel r5 · profile: code@r10 + measured-objective@r3`, and the `KERNEL:`
line above copies its profiles byte for byte. REPORTED, not refreshed: the map's declared code revision (r10) is older
than the fetched profile (r11); the map pins `profiles/code.md` at blob `5511ccb3`, and the bus tip's blob is `a31b27a7`
(its kernel and measured-objective pins, `6821c4c3` and `4e8bcacc`, still match). Two of its rows are now overtaken by
this board's own artifacts, also REPORTED, not refreshed: the K3 row says the measured-objective input identity has "no
production caller", and `tools/scoreboard.ps1` now calls it (P:code subject-identity); the K9 row says the weekly resume
drill's evidence folder is absent, and that folder now holds 5 drill receipts, 3 of them dated in this window. This filing
measures the window against r11 on the lines above. The map is never refreshed by this seat; its K1-K12 rows belong to the
card that wrote it. By its own rows, K3, K5, K6, K7, K8, K9, K10 and K11 are `NONE`, each with its nearest partial
mechanism.

## Counts

Clauses: 4 FIT · 0 FRICTION · 0 BREAK · 0 N/A · 5 UNEXERCISED · 3 INSTANCE-FAILURE
Profile: 1 FIT · 0 FRICTION · 0 BREAK · 0 N/A · 2 UNEXERCISED · 5 INSTANCE-FAILURE
Ledger totals (INSTANCE-FAILURE excluded per kernel §5): **5 FIT · 0 FRICTION · 0 BREAK · 0 N/A · 7 UNEXERCISED**
Moved against the sixth filing: K3 and P:code claims UNEXERCISED → FIT (an observer-release exercise this window).
Plus a status line for each of the fifteen earlier numbered instance failures (no new IF number; this window's
INSTANCE-FAILURE lines are the K and P lines above), answers to U7, U8, U9, U6, §a.u4, the independence-provenance bench,
the stale-map route and the resource-terminals line, and 4 Untested.
