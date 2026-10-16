project: dng-auto-processor
kernel: fleet-factory-kernel r5
profile: code@r11 (primary) + measured-objective@r3 — kernel §6's row as harvested (M1)
instance: docs/KERNEL-INSTANCE-MAP.md on nested-repo master (written by card KERNEL-DOGFOOD-INSTANCE-MAP under docs/14 §0's kernel entry, landed `db197676`; KERNEL line DOGFOOD, ## Instance map). The map's own first line still declares code@r10 (## Instance map)
subjects: 0 end-to-end under the kernel, and 0 declared dated inside this window — no `k5-declaration.json` was written after 2026-10-11T02:43Z (one dated 2026-10-09 exists and was missed by the fifth filing; see K5). Reported as mechanism evidence and never counted: 11 landings on this board's own two-key route, each with a committed receipt; none declared a profile. 0 PRODUCT commits landed off that route (## Subjects).
window: 2026-10-11T02:43Z .. 2026-10-15T02:00Z
health: assurance=UNSATISFIED operability=PRESSURED
providers: none (no lane cleared a sentinel for this filing)
posture: not computed — model review contributed (the route's approach reviews and keys), and the R9 tool is one PROMPT K names, which docs/13 P-STEWARD step 7e forbids the filing seat to run (U6, ROUTED; unchanged)

Sixth filing by this board, re-filed because `profiles/code.md` moved r10 to r11 at the 2026-10-13 harvest (PROMPT K §6
names a profile-revision change as a re-run trigger) and the board's census was not empty. The kernel (r5) and
measured-objective (r3) did not change; only the Subject identity (K3) cell of code did, as `HARVESTS.md` records for
that harvest. The fifth filing (blob `c9ce19d2`) was harvested on 2026-10-13: `dng-auto-processor.dispositions.md`
carries `filing_blob: c9ce19d2a378974217ccd45347608cf3c091f180` and answers it (45 `§` lines, no REJECTED among them;
6 ROUTED; plus 6 `HEADER:` lines, one REJECTED), so no finding of the fifth filing is carried forward undisposed. Its
four ROUTED bench routes stay open and are re-answered below on this window's evidence, and every clause and profile line
is re-measured against r5 and r11. The seat that writes it is `dng-design-steward`. It works from this board's own cards,
receipts and ledgers, and it ran no subject.

`assurance=UNSATISFIED`: no subject was declared or accepted under the kernel, and the product's own bar produced no
acceptance either — WORK.md's SCOREBOARD has no line inside the window (its newest is still `20260918-1356`).
`operability=PRESSURED`: 112 dispatches for 11 receipted landings (about 10 per landing against about 9 in the last
window), summed over the cop's daily ledger in WORK.md for the window. The ledger's landed sum (12)
and the 11 receipted landings are counted from different artifacts and are not matched one to one. Every cop daily-ledger line
of the window reads `ci=success` as it stands at the window's end (the 10-14 line read `ci=failure` at 01:02Z and 01:26Z), and that is not the whole CI story: master's hosted CI was red from the mirror push of one
landing until a fix landing 2 h 24 min later (receipts' `landedUtc` 2026-10-14T00:50:10Z and 03:14:08Z; P:code
delivery-target). WORK.md also records two STALL lines in the window (one docs/14 §3 forced-progress STALL, 2026-10-12 20:31Z, two no-op ticks; one docs/14 §7
alarm 1 STALL, 2026-10-14 00:31Z), each naming the one blocking artifact and the items released because they consume none of its bytes. The design
steward seat, which keeps this filing and the docs, began 15 passes inside the window; of the 14 that ended inside it, 5 ended ACTED and 9
NO-WORK-DEFERRED-ON-LOAD, and the last seven of those in a row were NO-WORK-DEFERRED-ON-LOAD (the 15th ended ACTED after it); it landed one DNG commit (`efe89ac1`,
a docs/14 §10 step edit) in the window. A WORK.md token in the working tree at the window's end (uncommitted, OWNER: steward) names that starvation. No outage of the
hosting app and no account rotation appears in the WORK.md lines and commit subjects this seat read for the window.

Unqualified paths and commit ids are this board's repository. Evidence kept outside it is named by description, never by
path, as before (bus law 4). Doctrine paths are qualified. One measurement card is in
flight at the window's end; this filing reports no interim result of it. Of the window's 11 landings, 1 was opened from
that card's findings and is reported in aggregate only, with no task name, sha, receipt path or test path, until that card
and every card opened from its lineage have left flight. The other 10 are named. RAMP-RECEIPT-K-PASS, the second
measurement card in flight in the fifth filing, left flight on 2026-10-14 (state MEASURED-NEGATIVE, `packets/RAMP-RECEIPT-K-PASS.md`),
so its descendants are named. The dispositions ruled that Law 4 does not by itself require a blanket withholding of every
completed descendant (HEADER: eight aggregate-only landings, REJECTED); this filing narrows the withholding to what is
still in flight. The fifth filing's own eight aggregate landings are not re-derived by this seat.

## Subjects

**Kernel subjects: none.** No rule, tool or hook reads `k5-declaration.json` (IF13), and none orders one written. In this
window nobody wrote one (IF15). Correction to the fifth filing, found by sweeping the evidence ledgers for the file name
case-insensitively: one `K5-DECLARATION.json` exists dated 2026-10-09T23:18Z (inside the fifth window, which reported 0),
declaring kernel r5 and code@r10 before the first implementation byte for a prepared docs/13 doctrine-consumer
fold-coverage candidate. That candidate's own return states it was prepared only, uncommitted, unreviewed and unlanded, so
it is a declaration and not a subject, and it contributes no end-to-end credit.

**Landings on this board's own route, reported and never counted.** Each has a receipt at
`metrics/ratify/<TASK>/<attempt>/receipt.json` on master, and each landed by `git merge --ff-only` of an exact sha onto
nested-repo master. "Keys' subject" is the receipt's `keysSubjectSha`. The last column is the PRODUCT paths (docs/14 §4's
closed set) the delivered tree carries beyond the keys' subject, read from each receipt's `rangeEnum.surplusProduct`.
"Assembly" is the feature assembly the commit changes beyond tests (`DngAutoProcessor.Tests` is PRODUCT by §4 but is not a
feature assembly).

| Task / attempt | Keys' subject → landed (tree same?) | Assembly | Author → key 1 / key 2 | PRODUCT paths crossed |
|---|---|---|---|---|
| RAMP-EMIT-GATE-KNOB-DIRECTION-WITNESS / 1 | 7082efcf → 7082efcf (yes) | tests only | claude-sonnet-5-5 → gpt-5.6-sol / claude-opus-5-5 | 0 |
| RAMP-EMIT-GATE-KNOB-EXTREME-WITNESS / 1 | 4c7010ff → 4c7010ff (yes) | tests only | gpt-5.6-sol → claude-fable-5-1 / claude-opus-5-5 | 0 |
| PROPAGATION-ANCHOR-OVERWRITE-GUARD / 1 | 2051f4d6 → 2051f4d6 (yes) | Core (`AutoProcessor.cs`) | claude-sonnet-5-5 → gpt-5.6-sol / claude-opus-5-5 | 0 |
| CRS-READBACK-TAG-NAMES / 1 | 64701fd3 → 64701fd3 (yes) | Core (`AdobePreviewRenderer.cs`) | gpt-5.6-sol → claude-fable-5-1 / claude-opus-5-5 | 0 |
| ENGINE-RENDER-SAMPLER-PARALLEL / 2 | 716073eb → 716073eb (yes) | Core (`TargetedAutoExposureSolver.cs`, through `118d992b` in its range) | gpt-5.6-sol, then gpt-6-astra for attempt 2's test-only fix → claude-fable-5-1 / claude-opus-5-5 (round 1 key 2 REVISE, round 2 ACCEPT) | 0 |
| ENGINE-RENDER-SAMPLER-ANALYZER-CLEAN / 1 | 10524425 → 10524425 (yes) | Core (`TargetedAutoExposureSolver.cs`) | claude-sonnet-5-5 → gpt-5.6-sol / claude-opus-5-5 | 0 |
| RAMP-RECEIPT-MANIFEST-NULL-ROUNDTRIP-WITNESS / 1 | 89bae41c → 89bae41c (yes) | tests only | claude-sonnet-5-5 → gpt-5.6-sol / claude-opus-5-5 | 0 |
| RAMP-GRADE-ONLY-TIE-AND-PRECISION-WITNESS / 1 | 1de6bfd4 → 1de6bfd4 (yes) | tests only | claude-sonnet-5-5 → gpt-5.6-sol / claude-opus-5-5 | 0 |
| RAMP-RECEIPT-MATRIX-OBSERVES-EMIT-AND-ANCHOR / 1 | 95de0a22 → 95de0a22 (yes) | tests only | claude-sonnet-5-5 → gpt-5.6-sol / claude-opus-5-5 | 0 |
| RAMP-RECEIPT-CONDITION-ARMS-WITNESS / 1 | 8e6b672a → 8e6b672a (yes) | tests only | claude-sonnet-5-5 → gpt-5.6-sol / claude-opus-5-5 | 0 |
| 1 test-only witness landing, withheld in aggregate (above) | 1 of 1 same tree | tests only | claude-sonnet-5-5 → gpt-5.6-sol / claude-opus-5-5 | 0 |

All 11 landings have `reviewedSha`, `keysSubjectSha` and `landedSha` equal: each was rebased onto master before the keys
where master had advanced by inert-only commits, so the keys reviewed the delivered commit (blob identity 2 of 2 or 1 of 1
PASS in every receipt). 10 landed at attempt 1 and ENGINE-RENDER-SAMPLER-PARALLEL at attempt 2, after round 1's key 2
returned REVISE on a confirmed MAJOR. Re-derive the count with `git -C <repo> log --since=2026-10-11T02:43Z --until=2026-10-15T02:00Z --diff-filter=A
--name-only --format= master -- 'metrics/ratify/*/receipt.json' | grep -c .` (11).

**Off-route landings: none.** The window's first-parent master history (36 commits dated inside it by commit time) holds 12
commits that touch a PRODUCT path: the 11 landed shas and `118d992b`, which lies inside ENGINE-RENDER-SAMPLER-PARALLEL's
delivered range. The other 24 are 23 cop bookkeeping commits and the steward's docs commit `efe89ac1` (docs/14 only, not a
PRODUCT path). The last window had none off the route either.

## Answers to the benches the last harvest routed

- **U7 (ADOPTED-CONDITIONAL, dng outcome-reporting bench), the O2 denominator across a fifth window: 4 of 11.** Same
  predicate: landings whose delivered range touches a feature assembly — every `DngAutoProcessor.*/` directory holding a
  `.csproj`, minus `*.Tests` (Core, App, CorpusBridge). The 4 are PROPAGATION-ANCHOR-OVERWRITE-GUARD,
  CRS-READBACK-TAG-NAMES, ENGINE-RENDER-SAMPLER-PARALLEL and ENGINE-RENDER-SAMPLER-ANALYZER-CLEAN, all in Core. The 7 that
  touch none change one test file each (the one in aggregate included). The earlier windows read 6 of 14, 3 of 11, 7 of 15
  and 12 of 17, each within its own receipted population. Assembly contact is not proof of a changed emitted grade
  (the dispositions' condition), and this filing does not claim it.
- **U8 (ROUTED, dng measured-objective outcome bench), the emitted-grade effect: partly derived, one more window.** The 7
  test-only landings change no file a build of the App, Core or CorpusBridge compiles, so none of them can change the grade
  the shipped defaults emit. The 4 Core landings are: a write-loop guard that keeps a hand-graded anchor clip as-is when
  manual-grade propagation is on (`AutoProcessor.cs`, commit subject of `2051f4d6`); a verified-render read-back that now
  requests Temperature under the tag name ExifTool has (`AdobePreviewRenderer.cs`, commit subject of `64701fd3`); a
  concurrency change in the targeted solver whose commit subject states the emitted sidecars stay byte-identical
  (`118d992b`); and a build-cleanliness fix whose commit subject states no behaviour change (`10524425`). Those last two
  are the authors' statements as committed, not something this seat derived; the first changes what the write loop does
  on its face, and whether propagation is on in the shipped defaults is not derived here. No SCOREBOARD line in the window
  measures an emitted grade.
- **Independence-provenance bench (P:code independent-key, left open by the dispositions): the contribution records, for
  this window.** Each receipt records its approach reviewer's model and verdict and how its findings were disposed (the
  counts below are the receipt's own `approachReview` fields `b`/`M`/`m` and `confirmed`). On 2 of 11 landings the approach
  reviewer and key 1 are the same model, `claude-fable-5-1`, both Codex-authored: KNOB-EXTREME-WITNESS (REVISE, 0 BLOCKER, 1
  MAJOR, 4 MINOR, 5 confirmed) and CRS-READBACK-TAG-NAMES (REVISE, 0, 1, 3, 4 confirmed). On 9 more the approach reviewer
  and key 1 are different models of one provider: 8 where the approach reviewer is `gpt-6-astra` and key 1 is `gpt-5.6-sol`,
  all Claude-authored (verdict, then BLOCKER/MAJOR/MINOR counts and the confirmed count: PROPAGATION-ANCHOR-OVERWRITE-GUARD
  BLOCKER 2/1/0, 3 confirmed; KNOB-DIRECTION-WITNESS BLOCKER 1/0/2, 3; ANALYZER-CLEAN REVISE 0/2/3, 2; GRADE-ONLY-TIE REVISE
  0/1/2, 1; CONDITION-ARMS BLOCKER 1/1/1, 2; MANIFEST-NULL-ROUNDTRIP REVISE 0/2/1, 2; MATRIX-OBSERVES REVISE 0/3/1, 3; and
  the landing in aggregate, REVISE 0/2/1, 2), and 1 where the approach reviewer is `claude-opus-5-5` and key 1 is `claude-fable-5-1`, both Anthropic
  (ENGINE-RENDER-SAMPLER-PARALLEL, Codex-authored, REVISE 0/1/8 and 1 confirmed). So on 11 of 11 landings key 1's provider
  also reviewed the approach the author then implemented (13 of 14 in the last window), and every receipt records that
  review's findings as confirmed or adopted, except SAMPLER-PARALLEL (1 of 9 confirmed, no note) and ANALYZER-CLEAN
  (its 2 MAJORs adopted, 3 MINORs unrecorded). The commit subjects of the cop's bookkeeping commits record adoption for all that this seat
  read; the bench's question — whether that makes the class a producer of the subject, or independent criticism — is not
  decided here, and provider overlap alone does not decide it (the dispositions' words). Two observations from the same
  receipts bear on it without deciding it. Key 2 on ENGINE-RENDER-SAMPLER-PARALLEL (`claude-opus-5-5`, also its approach
  reviewer) returned REVISE on a confirmed MAJOR in round 1 and ACCEPT in round 2. And neither key caught the failure that
  turned master's hosted CI red on that landing (P:code delivery-target): no key brief named analyzer warnings.
- **§a.u4 (ROUTED, delivered-pipeline delayed-outcome fixture): none to bring.** This board accepted no subject under the
  kernel, and no SCOREBOARD line falls in the window.
- **U6 (ROUTED, authorised posture-computation seat): unchanged.** No register-authorised seat computed R9 for this
  filing, and no owner word authorising one has been recorded in docs/14 §0.
- **P:code resource-terminals (ADOPTED as an INSTANCE-FAILURE): one exercise this window, reported on that line.**

## Clauses

K1 | UNEXERCISED | "A candidate is never accepted on evidence whose only author is its producer" | No kernel subject existed. Reported without credit: all 11 route receipts name an author whose model is neither key's, and no PRODUCT commit landed off the route | PROOF: a kernel subject accepted here on receipts naming one actor for production and acceptance

K2 | FIT | "Everything unlisted is autonomous. Escalation goes to the owner for decisions reserved by that register" | Register: docs/14 §0 (USER rulings verbatim) plus WORK.md RULES rule 3. Taken without asking because the register allowed it: 11 route landings, none needing an owner act at landing. Escalations went where the register sends them: on 2026-10-12 10:33Z the cop refused to open a routed card-ready artifact that named no allowlist (docs/14 §4 reads it INADMISSIBLE) and filed an OWNER-DEFECT line, which the router answered with a re-issue 24 minutes later; on 2026-10-14 01:02Z the cop filed an OWNER-DEFECT on the landing gate's build flags (P:code delivery-target) rather than editing the hook or docs/14 itself. No owner-reserved act was taken | PROOF: an owner-reserved act taken here with no §0 entry authorising it

K3 | UNEXERCISED | "under a claim an observer other than the claimant can decide stale and release; an expiring lease is one such mechanism" | Mechanism unchanged: the card's owner line plus a launch json written before the launch (docs/14 §3), with staleness decided from outside the seat by §3's liveness rule; every receipt names its claim. No claim was decided stale in the window: each of the 11 landings' claims was released by its own claimant at collect, and the two STALL lines (2026-10-12 20:31Z, 2026-10-14 00:31Z) record an observer deciding a seat LIVE, not releasing it. The fifth filing's FIT rested on a re-dispatch after the host outage, which did not recur. The instance map's K3 row is still NONE for an identity held by one claimant at a time with an atomic claim | PROOF: a claim here still held after its seat was dead, with no observer able to release it

K4 | FIT | "Work is complete only on positive evidence it was asked to produce" | In the product, the verified render's crs read-back had asked ExifTool for a tag name it does not have, so a white-balance drift could not fail verification; it now requests Temperature as `ColorTemperature` (`64701fd3`, landed with a real-ExifTool RED/GREEN test). A write loop that rewrote a hand-graded anchor clip under manual-grade propagation is guarded (`2051f4d6`). In the factory, candidate missing-test classes routed from a measurement card were opened only with a reproduce-RED-first contract, and the one class already killed at master was refused (RAMP-RECEIPT-CONDITION-ARMS-WITNESS, `8e6b672a`, whose own message records which of the routed classes B1-B9 reproduced RED and that B8 was already killed at master); a flaky-test card closed MEASURED-NEGATIVE, not DONE, after 180 isolated runs did not reproduce it, with the residue recorded and a reopen-on-recurrence condition (`packets/LEARN-PROJECT-DCRAW-SCRATCH-CLEANUP-FLAKE.md`); and a round-1 REVISE on a confirmed MAJOR stopped a landing until attempt 2 (ENGINE-RENDER-SAMPLER-PARALLEL). Counter-evidence is filed under P:code delivery-target, not here | PROOF: a card here closed DONE on a return code or a file's presence alone

K5 | UNEXERCISED | "Before work starts, a subject declares its profile and profile version." | 0 `k5-declaration.json` dated inside the window (IF15), and no landing receipt records a profile (0 of the 11 receipts, and none of the four cards read for this, name one). The sweep that supports this negative: case-insensitive file-name search of the evidence ledgers for `k5-decl*` files newer than the window start returned none; the same search found one dated 2026-10-09 that the fifth filing's "0" missed (## Subjects). It declares before first implementation byte but names a candidate that was never landed; its author return says unreviewed, and a handoff 14 minutes later claims an independent review; it was routed to the cop on 2026-10-09 23:35:50Z, which opened no card (WORK.md item 3 holds it as the steward's) | PROOF: a subject accepted here whose acceptance receipt names a different identity or profile than its declaration

K6 | UNEXERCISED | "Every acceptance includes a key from an independence class other than the producer's." | No kernel subject was accepted. Reported without credit: 11 of 11 route landings carry a key 1 from the provider opposite the author's (Claude authors → `gpt-5.6-sol`, Codex authors → `claude-fable-5-1`), and key 2 is `claude-opus-5-5` on all 11. The independence-provenance records are above | PROOF: an accepted subject here whose keys and producer share one provider

K7 | UNEXERCISED | "Acceptance and delivery are separate states." | Nothing was accepted under the kernel. Reported without credit: all 11 route landings reached nested-repo master by `--ff-only` of an exact sha. All 11 receipts record the mirror sync: 3 as a `mirrorSync` field (PROPAGATION-ANCHOR-OVERWRITE-GUARD, KNOB-DIRECTION-WITNESS, KNOB-EXTREME-WITNESS) and 8 inside the `landing` text (7 of them naming a mirror-sync log and 4 a pushed range) with `productByteIdentity` or "product half IDENTICAL". No typed `CLOSURE_INCOMPLETE` exists here (IF9). Hosted CI after one of those syncs was red (P:code delivery-target) | PROOF: an accepted subject here that never landed and that the next tick names unprompted

K8 | UNEXERCISED | "Reset events update capacity telemetry. They never open a gate by themselves." | Mechanism unchanged since the repair the fourth filing reported (docs/14 §2, "on EVIDENCE, never off the window"). In-window: one key-1 seat's model stream failed with "Selected model is at capacity" and the seat was relaunched on the other family (P:code resource-terminals). No artifact this filing read records a quota reset as such, the observable's trigger | PROOF: a reset event here that by itself re-opened a darkened seat

K9 | INSTANCE-FAILURE | "A fresh session on a new account, with empty memory, resumes from the project's tree and the bus alone." | Carried as adopted, unchanged in mechanism: nothing in the instance re-registers a scheduled seat whose registration a previous use of the account left stale, and nothing detects from outside the host that the host ran none of its seats. No rotation and no host outage is recorded in this window, so the clause did not arise again here; the line is kept because the dispositions adopted it and no repair landed (0 commits in the window touch docs/13 P-RESUME or P-COP). The re-classification to UNEXERCISED is the steward's to rule | no replacement | PROOF: a rotation here after which every scheduled seat the register authorises ran again with no owner step

K10 | INSTANCE-FAILURE | "Provider and model inventory is machine-scoped and probe-derived, and it records the account it was derived under." | Unchanged: no machine-readable inventory and no `probed_under` in the repo (the instance map's K10 row) | no replacement | PROOF: an in-repo inventory whose `probed_under` names the current account

K11 | INSTANCE-FAILURE | "R1–R5, R7, R8 and R9 apply to every report a factory makes about itself" | Unchanged: the two CLOSED lines `131ad1f2` appended (WORK.md, dated 2026-09-23 14:05Z) still stand with no correction line beside them, and the seat that found it may append nothing there but a CLOSED line (docs/13 P-STEWARD). This filing takes no credit for 11 route landings and asserts no posture it did not compute | no replacement | PROOF: a correction line beside that CLOSED line in the board's ledger

K12 | FIT | "The steward harvests every filing and answers each one." | The fifth filing (blob `c9ce19d2`) was harvested on 2026-10-13 (bus `ce2132b6`, harvest `20261013T070405Z-d4564706`): `dng-auto-processor.dispositions.md` carries its blob, answers every `§` line and header line, and `HARVESTS.md` carries its row (FIT 5 · FRICTION 0 · BREAK 0 · N/A 0 · UNEXERCISED 7). This re-file is the clause's other half. FENCE: the filing seat may not run `tools/harvest-status.py`, so the harvested state is read from the artifacts that tool reads | PROOF: a finding of the fifth filing with no disposition line

## Profile lines

P:code subject-identity | INSTANCE-FAILURE | "its identity is K3's `sha256` of that OID's lowercase hexadecimal text, with no trailing newline" | Assessed against r11, whose only change is this cell's opening. Held in the window: 11 of 11 route landings delivered the commit the keys reviewed (`keysSubjectSha` = `landedSha`, tree OID identical by construction), against 3 of 14 changed-tree deliveries last window, and 0 PRODUCT paths were crossed beyond the keys' subject; no key had to transfer, so the manifest alternative never arose. Not held: the receipts bind each key to a commit sha and record the reviewed and delivered commits and the stable patch-id, but none records the tree OID or its K3 `sha256`, so the r11 identity is recomputable (`git rev-parse <sha>^{tree}`, then `sha256` of that text with no trailing newline) and nowhere recorded. The instance map's K3 row names the tree OID as the identity half and predates r11's digest. This board's manifest is still `binding.json`'s `files`, the paths a subject changes and never its inputs | no replacement | PROOF: a receipt here recording each subject's tree OID and K3 digest, reviewed and delivered alike

P:code claims | UNEXERCISED | "observer-released claims may replace leases" | The observer-release mechanism is unchanged (K3), and the window did not exercise its release path: no claim was decided stale and released by an observer other than its claimant | PROOF: a claim here released by its own claimant's say-so, or held after its seat died with no observer able to release it

P:code claims-audit | INSTANCE-FAILURE | "Audit canonical state before and after: HEAD, index entries and flags, refs, reflogs, stash, tracked contents, and ignored/untracked path inventories" | Unchanged: for a mutation-capable key 2 (every key 2 here builds and runs the suite or a mutant battery), §10 step 6 records the SCRATCH worktree's state at removal, never the main checkout's before and after | no replacement | PROOF: a key-2 run here whose receipt records the main checkout's HEAD, index entries and flags, refs, reflogs, stash, tracked contents and ignored/untracked path inventories with content hashes, before and after

P:code independent-key | UNEXERCISED | "a verifier from another model family (R3) whose class has not become a producer of the subject" | No kernel subject was accepted. The contribution records the bench asked for are above: on 11 of 11 landings key 1's provider also reviewed the approach, and every receipt records that review's findings as confirmed or adopted, except SAMPLER-PARALLEL (1 of 9 confirmed, no note) and ANALYZER-CLEAN (its 2 MAJORs adopted, 3 MINORs unrecorded) | PROOF: a subject here whose only other-provider key comes from a class that also wrote its product bytes

P:code resource-terminals | INSTANCE-FAILURE | "Before dispatch, declare any register-permitted substitution for a family-bound quorum seat" | The latent gap stands in the rule: docs/14 §2 orders a SINGLE-FAMILY round's `cross_family: UNAVAILABLE <provider> <UTC ISO>` label into "its receipt", written at landing, and no rule orders the substitution declared before dispatch. Exercised once in the window, declared in time by practice: of the 150 launch json files modified inside the window (searched to depth 4 of the evidence ledgers), one carries a failover (key 1 of a measurement card now closed, its `gpt-5.6-sol` stream "at capacity", relaunched on `claude-fable-5-1`), and its launch json carries `crossFamily: UNAVAILABLE openai <UTC ISO>` at the same second as its `startedUtc`. A seat following a practice is not a mechanism, as with K5 | no replacement | PROOF: a rule here that orders every substituted seat's declaration written before its dispatch, and a window in which each substituted seat's launch record carries it

P:code delivery-target | INSTANCE-FAILURE | "build the exact proposed record and run the validators and hooks that commit will face before any product push; refuse on failure" | A concrete exercise this window. ENGINE-RENDER-SAMPLER-PARALLEL landed as `716073eb` with blobs 2 of 2, range 2 of 2, both round-2 keys ACCEPT and a green local hook run on the committed bytes and key 2's own build and filtered suite (both 3356/3356), and hosted CI on its mirror commit then failed: the hosted workflow builds with `--warnaserror` (`.github/workflows/factory-ci.yml`) and the local hook builds without it (`.githooks/pre-commit`, two `dotnet build` lines), so four analyzer diagnostics printed as warnings in that hook log and as errors in CI. Master's CI stayed red until ENGINE-RENDER-SAMPLER-ANALYZER-CLEAN landed as `10524425` 2 h 24 min later (receipts' `landedUtc`; the fix's subject records the CI build clean). The gap itself stands at the window's end: 0 commits in the window touch `.githooks/`, and the cop's OWNER-DEFECT line of 2026-10-14 01:02Z asking whether §4's obligations or the hook must carry CI's flags is open. The cop's 2026-10-14 daily-ledger line read `ci=failure` twice inside the red interval (its 01:02Z and 01:26Z versions, both in the board's WORK.md history). The cop rewrites that line in place each tick, so at the window's end all four daily lines read `ci=success` and the ledger keeps no trace of the red interval | no replacement | PROOF: a landing here whose hosted validators ran green before its mirror push

P:code dispatch-preflight | INSTANCE-FAILURE | "the spending tool runs the project's resume gate before dispatch and retains its result, the inventory snapshot and digest, and account-parity evidence" | Unchanged: docs/13 P-COP orders no resume-gate, inventory or parity read before dispatch, so none of the window's 112 dispatches is ordered to retain them; this filing did not read the tick notes for a seat that retained them unordered — the K10 gap | no replacement | PROOF: a tick receipt here that retains a resume-gate result, an inventory digest and parity evidence before its first dispatch

P:measured-objective acceptance-evidence | UNEXERCISED | "the declared scorer on a held-out fold the producer never tuned on" | No SCOREBOARD line falls inside the window (its newest is `20260918-1356`), so no candidate was scored; the window's measurement cards grade test-suite mutants and do not score a grade candidate on a held-out fold | PROOF: a scored run in the window that this line missed

## Instance failures

Status of the earlier fifteen:
- **IF1, IF11**: historical, unchanged.
- **IF2: repaired in the latent script**; `tools/ratify.ps1` is still off the live landing path (0 of 11 window receipts name it).
- **IF3, IF4, IF10: LATENT**, as before.
- **IF5: repaired in the latent script**; no gate0 ran on the live route (0 of 11 receipts name one).
- **IF6: LIVE.** WORK.md:4 still reads "Merge: tools/ratify.ps1 (gate 0 + cross-family key + adversarial Claude key)".
- **IF7**: resolved at an earlier read, and outside git.
- **IF8: unchanged.** `tools/claude-review-capture.ps1` and `tools/codex-author-capture.ps1` are both still absent.
- **IF9: unchanged.**
- **IF12: unchanged.** The window's receipts use one of the earlier encodings — a `seats` object with an `authors` list and a `rounds` list of `k1`/`k2` maps (11 of 11) — and add none; 3 keep their mirror-sync record in a `mirrorSync` field and 8 in the `landing` text, 7 of them with log files (K7).
- **IF13: unchanged.**
- **IF14: resolved**, as before; what hosted CI finds is P:code delivery-target, which this window exercised.
- **IF15: unchanged for this window.** 0 declarations dated inside it. Corrected count for the fifth window: 1 declaration (2026-10-09), 0 subjects (## Subjects), not the 0 and "third consecutive window" the fifth filing wrote.

## Untested

U6 | The `posture:` line (ROUTED, unchanged). The same limit applies to `tools/harvest-status.py`.

U8 | Whether any of the 4 Core landings changed the grade the shipped defaults emit (the 7 test-only landings cannot); in particular whether manual-grade propagation is on in the shipped defaults. Not derived here.

U9 | Not tested here; read from master WORK.md only: the doctrine-consumer fold-coverage candidate was ROUTED to the cop 2026-10-09 23:35:50Z and no card was opened; WORK.md item 3 holds it as the steward's. Its fate after that is the steward's open item, not a bench question.

## Instance map

KERNEL: DOGFOOD fleet-factory-kernel r5 · profile code@r10 + measured-objective@r3 · instance docs/KERNEL-INSTANCE-MAP.md · since 2026-10-02

The instance map is `docs/KERNEL-INSTANCE-MAP.md` on nested-repo master; this section points at it and keeps no table.
Its first line declares `kernel: fleet-factory-kernel r5 · profile: code@r10 + measured-objective@r3`, and the `KERNEL:`
line above copies its profiles byte for byte. REPORTED, not refreshed: the map's declared code revision (r10) is older
than the fetched profile (r11); the map pins `profiles/code.md` at blob `5511ccb3`, and the bus tip's blob is `a31b27a7`
(its kernel and measured-objective pins, `6821c4c3` and `4e8bcacc`, still match). This filing measures the window against
r11 on the lines above. The map is never refreshed by this seat; its K1-K12 rows, including the K3 row whose identity half
predates r11's digest, belong to the card that wrote it. By its own rows, K3, K5, K6, K7, K8, K9, K10 and K11 are `NONE`,
each with its nearest partial mechanism.

## Counts

Clauses: 3 FIT · 0 FRICTION · 0 BREAK · 0 N/A · 6 UNEXERCISED · 3 INSTANCE-FAILURE
Profile: 0 FIT · 0 FRICTION · 0 BREAK · 0 N/A · 3 UNEXERCISED · 5 INSTANCE-FAILURE
Ledger totals (INSTANCE-FAILURE excluded per kernel §5): **3 FIT · 0 FRICTION · 0 BREAK · 0 N/A · 9 UNEXERCISED**
Plus a status line for each of the fifteen earlier numbered instance failures (no new IF number; this window's INSTANCE-FAILURE lines are the K and P lines above), answers to U6, U7, U8, §a.u4, the
independence-provenance bench and the resource-terminals exercise, and 3 Untested.
