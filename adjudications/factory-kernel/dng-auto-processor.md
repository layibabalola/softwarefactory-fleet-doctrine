project: dng-auto-processor
kernel: fleet-factory-kernel r5
profile: code@r10 (primary) + measured-objective@r3 — kernel §6's row as harvested (M1)
instance: docs/KERNEL-INSTANCE-MAP.md on nested-repo master (written by card KERNEL-DOGFOOD-INSTANCE-MAP under docs/14 §0's kernel entry, landed `db197676`; KERNEL line DOGFOOD, ## Instance map)
subjects: 0 end-to-end under the kernel, and 0 declared in this window — no `k5-declaration.json` was written after 2026-10-04T01:50Z. Reported as mechanism evidence and never counted: 14 landings on this board's own two-key route, each with a committed receipt; none declared a profile. 0 PRODUCT commits landed off that route (## Subjects).
window: 2026-10-04T01:50Z .. 2026-10-11T02:43Z
health: assurance=UNSATISFIED operability=PRESSURED
providers: none (no lane cleared a sentinel for this filing)
posture: not computed — model review contributed (two read-only Opus ratification lanes), and the R9 tool is one PROMPT K names, which docs/13 P-STEWARD step 7e forbids the filing seat to run (U6, ROUTED; unchanged)

Fifth filing by this board, re-filed because the fourth is past PROMPT K §6's week and this board's census was not
empty. Neither the kernel's nor either profile's revision changed. The fourth filing (blob `489ad089`) was harvested on
2026-10-05: `dng-auto-processor.dispositions.md` carries `filing_blob: 489ad0892fb0eae147248e7f1bf477b15d3e5f9f` and
answers it, so nothing is carried forward undisposed. This filing measures the window against r5 and r10, reports that
the board again ran no subject through the kernel, and answers the benches that harvest routed. The seat that writes it
is `dng-design-steward`. It works from this board's own cards, receipts and ledgers, and it ran no subject.

`assurance=UNSATISFIED`: no subject was declared or accepted under the kernel, and the product's own bar produced no
acceptance either — WORK.md's SCOREBOARD has no line inside the window (its newest is still `20260918-1356`).
`operability=PRESSURED`: 128 dispatches for 14 landings, about 9 per landing against about 11 in the last window, summed
over the six cop daily-ledger lines dated inside the window in WORK.md (the last, its 2026-10-11 02:43Z line, is the window's end). The ledger's landed sum and the 14 receipted landings below are counted from different artifacts and are not matched one to one (dispatched and
landed 26 and 2, 25 and 3, 4 and 1, 40 and 4, 32 and 3, 1 and 1). No cop daily-ledger line is dated 2026-10-06 or -07.
The board's own alarms line of 2026-10-08 22:38Z records why: the desktop app that hosts every scheduled seat ran no seat
from about 2026-10-05T15:36Z to its restart at 2026-10-08T22:10:29Z while the machine stayed up, and alarm 1 (STALL) fired
on it. No artifact this filing read names that outage's cause. Every cop daily-ledger line in the window reads
`ci=success`.

Unqualified paths and commit ids are this board's repository. Evidence kept outside it is named by description, never by
path, as before (bus law 4). Doctrine paths are qualified. Two measurement cards are still in flight at the window's end, and a witness card opened from their lineage is running. Eight of the window's
landings descend from their findings: six of those receipts name them or carry their key-round verdicts, and two were
opened from a sibling witness's key review. This filing reports all eight only in aggregate — no task name, sha, receipt path or test path — until those cards, and every card opened from their lineage, have left
flight (bus law 4, as this board's census applies it).

## Subjects

**Kernel subjects: none.** No rule, tool or hook reads `k5-declaration.json` (IF13), and none orders one written. In this
window nobody wrote one (IF15).

**Landings on this board's own route, reported and never counted.** Each has a receipt at
`metrics/ratify/<TASK>/1/receipt.json` on master, and each landed by `git merge --ff-only` of an exact sha onto
nested-repo master. "Keys' subject" is the receipt's `keysSubjectSha` where it has one, else `reviewedSha`. The last
column is the PRODUCT paths (docs/14 §4's closed set) the delivered tree carries beyond the keys' subject, read from each
receipt's `landing` field and `rangeEnum`, which record the inert-commit rebase.

| Task / attempt | Keys' subject → landed (tree same?) | Author → key 1 / key 2 | PRODUCT paths crossed |
|---|---|---|---|
| AUTOMATION-LEARN-PROJECT-DCRAW-GUARD-FOREIGN-POPULATION-BATCH-PASS / 1 | 97a86252 → 37a96e26 (no) | claude-sonnet-5-5 (self-reported) → gpt-5.6-sol / opus (Agent alias) | 0 |
| AUTOMATION-LEARN-PROJECT-INCOMPLETE-SCAN-GUARD / 1 | c6fafb9f → c6fafb9f (yes) | gpt-5.6-sol → claude-fable-5-1 / claude-opus-5-5 | — |
| AUTOMATION-LEARN-PROJECT-DCRAW-NO-SAMPLE-GUARD / 1 | 93c66a4e → 93c66a4e (yes) | gpt-5.6-sol → claude-fable-5-1 / claude-opus-5-5 | — |
| CORPUSBRIDGE-LEARN-PROJECT-DCRAW-NO-SAMPLE-GUARD / 1 | 11642729 → a3eda538 (no) | gpt-5.6-sol → claude-fable-5-1 / claude-opus-5-5 | 0 |
| CORPUSBRIDGE-LEARN-PROJECT-IDENTITY-REFUSAL-FIRST / 1 | 3f57d647 → 540e277d (no) | claude-sonnet (hosted) → gpt-5.6-sol / claude-opus-5-5 | 0 |
| AUTOMATION-LEARN-PROJECT-IDENTITY-REFUSAL-FIRST / 1 | d53068c7 → d53068c7 (yes) | gpt-5.6-sol → claude-fable-5-1 / claude-opus-5-5 | — |
| 8 test-only witness landings, withheld in aggregate (above) | 8 of 8 same tree | 5 claude-sonnet-5-5 → gpt-5.6-sol / claude-opus-5-5; 3 gpt-5.6-sol → claude-fable-5-1 / claude-opus-5-5 | — |

FOREIGN-POPULATION's delivered range is two commits, `7ff1204b` (its parent card's carried product commit) and
`37a96e26`, both in its binding. The three changed-tree deliveries each record 0 surplus PRODUCT paths (two as
`rangeEnum.surplusProduct: 0`, FOREIGN-POPULATION in its `proofObligations.landingRange` prose). All 14 landed at attempt 1.

**Off-route landings: none.** The window's first-parent master history (65 commits dated inside it by commit time) holds 15 commits that
touch a PRODUCT path: the 14 landed shas and `7ff1204b`, which lies inside FOREIGN-POPULATION's delivered range. The last
window had none either.

## Answers to the benches the last harvest routed

- **U7 (ADOPTED-CONDITIONAL, dng outcome-reporting bench), the O2 denominator across a fourth window: 6 of 14.** Same
  predicate: landings whose delivered range touches a feature assembly — every `DngAutoProcessor.*/` directory holding a
  `.csproj`, minus `*.Tests` (Core, App, CorpusBridge). The 6 are FOREIGN-POPULATION (through `7ff1204b`),
  INCOMPLETE-SCAN-GUARD, both DCRAW-NO-SAMPLE-GUARDs and both IDENTITY-REFUSAL-FIRSTs. The 8 that touch none are the eight
  withheld witness landings, each of which changes one test file and nothing else. The earlier windows
  read 3 of 11, 7 of 15 and 12 of 17, each within its own receipted population.
- **U8 (ROUTED, dng measured-objective outcome bench), the emitted-grade effect: partly derived.** The 8 test-only
  landings change no file a build of the App, Core or CorpusBridge compiles, so none of them can change the grade the
  shipped defaults emit. The 6 feature-assembly landings change learn-project's refusal paths in
  `DngAutoProcessor.Core/Automation/AutomationVerbs.cs`, `DngAutoProcessor.Core/Persistence/LookTeachingStore.cs` and `DngAutoProcessor.CorpusBridge/CorpusBridgeApp.cs`
  (which rows a re-teach may replace, and which refusal is reported first). Whether any of them changes an emitted grade
  is not derived here, and no SCOREBOARD line in the window measures one.
- **Independence-provenance bench (P:code independent-key, REJECTED(unexercised) with the bench left open): the
  contribution records, for this window.** Each receipt records its approach reviewer's model and verdict and how its
  findings were disposed, in the approach or by IMPLEMENT (the counts below are the receipt's own: `confirmed`, its note's adopted or
  answered, or its `answeredBy`). On 7 of 14 landings the approach reviewer and key 1 are the same model,
  `claude-fable-5-1`, all seven Codex-authored: INCOMPLETE-SCAN-GUARD (REVISE, 5 confirmed),
  AUTOMATION-DCRAW-NO-SAMPLE-GUARD (REVISE, 4), CORPUSBRIDGE-DCRAW-NO-SAMPLE-GUARD (ACCEPT, 3 adopted),
  AUTOMATION-IDENTITY-REFUSAL-FIRST (REVISE, all four adopted), and three of the withheld witnesses (REVISE 5; ACCEPT 3
  adopted; REVISE 4 adopted). On 6 more the approach reviewer is `gpt-6-astra` and key 1 is `gpt-5.6-sol`, one provider:
  FOREIGN-POPULATION (BLOCKER; its `answeredBy` records two findings adopted, one declared out of universe and one
  recorded), CORPUSBRIDGE-IDENTITY-REFUSAL-FIRST (BLOCKER, answered in the approach before IMPLEMENT), and four of the
  withheld witnesses (REVISE 1 adopted; ACCEPT 1 adopted; ACCEPT 3 adopted; REVISE 2). On the 14th, a withheld witness,
  the approach review was moved to `claude-fable-5-1` by a Codex failover (P:code resource-terminals) and key 1 is
  `gpt-5.6-sol`. So on 13 of 14 the key-1 class also reviewed the approach the author then implemented, and all 13
  receipts record that review's findings as confirmed, adopted or answered, in the approach or by IMPLEMENT. Whether that makes the class
  a producer of the subject is the bench's question; this filing brings the records and claims no FIT.
- **§a.u4 (ROUTED, delivered-pipeline delayed-outcome fixture): none to bring.** This board accepted no subject under the
  kernel, and no SCOREBOARD line falls in the window.
- **U6 (ROUTED, authorised posture-computation seat): unchanged.** No register-authorised seat computed R9 for this
  filing, and no owner word authorising one has been recorded in docs/14 §0.
- **P:code resource-terminals (ADOPTED, with an additional latent INSTANCE-FAILURE disclosed): filed as that
  INSTANCE-FAILURE below, with this window's one exercise.**

## Clauses

K1 | UNEXERCISED | "A candidate is never accepted on evidence whose only author is its producer" | No kernel subject existed. Reported without credit: all 14 route receipts name an author whose model is neither key's, and no PRODUCT commit landed off the route | PROOF: a kernel subject accepted here on receipts naming one actor for production and acceptance

K2 | FIT | "Everything unlisted is autonomous. Escalation goes to the owner for decisions reserved by that register" | Register: docs/14 §0 (USER rulings verbatim) plus WORK.md RULES rule 3. Taken without asking because the register allowed it: 14 route landings, none needing an owner act at landing. Escalations went where the register sends them: the steward's OWNER-DEFECT lines addressed to the owner stayed in its receipts (docs/13 P-STEWARD bars any other WORK.md edit), and no owner-reserved act was taken | PROOF: an owner-reserved act taken here with no §0 entry authorising it

K3 | FIT | "under a claim an observer other than the claimant can decide stale and release; an expiring lease is one such mechanism" | Unchanged mechanism: the card's owner line plus a launch json written before the launch (docs/14 §3), with staleness decided from outside the seat by §3's liveness rule. In-window: when the scheduled host came back on 2026-10-08, cop tick 303, an observer other than any claimant, re-dispatched both cards that were RUNNING when it went dark (the alarms line of 2026-10-08 22:38Z). The instance map's K3 row is still NONE for an identity held by one claimant at a time with an atomic claim | PROOF: a claim here still held after its seat was dead, with no observer able to release it

K4 | FIT | "Work is complete only on positive evidence it was asked to produce" | Two kinds of repair. In the product, learn-project now refuses to replace a project's dcraw-sampled teaching rows when a resolvable dcraw sampled none of the clips it ingested (`93c66a4e` automation, `a3eda538` corpus bridge), refuses when its scan abandoned a subtree (`c6fafb9f`), and reports the store's different-folder refusal before the no-sample one so its remedy never points at another shoot's rows (`d53068c7`, `540e277d`). In the factory, docs/14 §10's CLI-currency smoke had accepted a "Reply PONG" answer, which runs no command, so it passed a Codex version whose read-only sandbox could create no process (WORK.md OWNER-DEFECT 2026-10-09 09:20Z); a Codex upgrade now also runs one read-only `git rev-parse HEAD` and passes only when the output holds that HEAD and not the sandbox's failure text, and a rolled-back version is held while it is npm's newest (`03c6dabc`, in the window; the window's last cop daily-ledger line records a Codex check after it rejecting 0.162.1 again) | PROOF: a card here closed DONE on a return code or a file's presence alone

K5 | UNEXERCISED | "Before work starts, a subject declares its profile and profile version." | 0 `k5-declaration.json` declarations in the window (IF15), and no landing receipt records a profile | PROOF: a subject accepted here whose acceptance receipt names a different identity or profile than its declaration

K6 | UNEXERCISED | "Every acceptance includes a key from an independence class other than the producer's." | No kernel subject was accepted. Reported without credit: 14 of 14 route landings carry a key 1 from the provider opposite the author's; the independence-provenance records are above | PROOF: an accepted subject here whose keys and producer share one provider

K7 | UNEXERCISED | "Acceptance and delivery are separate states." | Nothing was accepted under the kernel. Reported without credit: all 14 route landings reached nested-repo master by `--ff-only` of an exact sha. All 14 receipts receipt the mirror sync: 10 inline (exit 0, with the mirror's master read back), and 4 (AUTOMATION-DCRAW-NO-SAMPLE-GUARD, both CORPUSBRIDGE-*, AUTOMATION-IDENTITY-REFUSAL-FIRST) through a mirror-sync log and an ls-remote read-back listed with sha256 in their `evidence`. No typed `CLOSURE_INCOMPLETE` exists here (IF9) | PROOF: an accepted subject here that never landed and that the next tick names unprompted

K8 | UNEXERCISED | "Reset events update capacity telemetry. They never open a gate by themselves." | Mechanism unchanged since the repair the last filing reported (docs/14 §2, "on EVIDENCE, never off the window"). In-window: one withheld landing's approach review launched under a SINGLE-FAMILY label during a Codex outage; its receipt records Codex answering a probe before its key 1 launched on `gpt-5.6-sol`. So the family re-opened on a probe that answered, the repaired rule's evidence. No artifact this filing read records a quota reset as such, the observable's trigger | PROOF: a reset event here that by itself re-opened a darkened seat

K9 | INSTANCE-FAILURE | "A fresh session on a new account, with empty memory, resumes from the project's tree and the bus alone." | No rotation is recorded in the window. The last filing's failure stands unrepaired in mechanism: nothing in the instance re-registers a scheduled seat whose registration a previous use of the account left stale. A related gap, not this clause's observable: from about 2026-10-05T15:36Z to 2026-10-08T22:10:29Z the one host every scheduled seat runs in ran none of them while the machine stayed up, and nothing in the instance detects that from outside the host; it was found by the first cop tick after the restart | no replacement | PROOF: a rotation here after which every scheduled seat the register authorises ran again with no owner step

K10 | INSTANCE-FAILURE | "Provider and model inventory is machine-scoped and probe-derived, and it records the account it was derived under." | Unchanged: no machine-readable inventory and no `probed_under` in the repo (the instance map's K10 row) | no replacement | PROOF: an in-repo inventory whose `probed_under` names the current account

K11 | INSTANCE-FAILURE | "R1–R5, R7, R8 and R9 apply to every report a factory makes about itself" | Unchanged: the CLOSED line `131ad1f2` appended still stands in the board's ledger with no correction beside it, and the seat that found it may append nothing there but a CLOSED line (docs/13 P-STEWARD). This filing takes no credit for 14 route landings and asserts no posture it did not compute | no replacement | PROOF: a correction line beside that CLOSED line in the board's ledger

K12 | FIT | "The steward harvests every filing and answers each one." | The fourth filing (blob `489ad089`) was harvested on 2026-10-05 (bus `ff429d3b`): `dng-auto-processor.dispositions.md` carries its blob and answers it. This re-file is the clause's other half. FENCE: the filing seat may not run `tools/harvest-status.py`, so the harvested state is read from the artifacts that tool reads | PROOF: a finding of the fourth filing with no disposition line

## Profile lines

P:code subject-identity | INSTANCE-FAILURE | "a nonempty manifest of repository paths that includes every repository input the reviewed behaviour or acceptance checks depend on" | 3 of 14 route landings delivered a tree other than the keys' subject (4 of 17 last window), each by docs/14 §4's inert-commit rebase, and none declared an input manifest before review, so under the row none of those 3 keys transferred. Each crossed 0 PRODUCT paths (## Subjects). This board's manifest is still `binding.json`'s `files`, the paths a subject changes and never its inputs | no replacement | PROOF: a receipt here recording a declared input manifest and its combined digest, reviewed and delivered alike

P:code claims | FIT | "observer-released claims may replace leases" | Limited to the observer-release mechanism, as harvested: the owner line and pre-launch json name the subject, owner and seat, docs/14 §3's liveness rule lets another observer decide a claim stale, and K3 records the in-window re-dispatch after the host outage | PROOF: a claim here released by its own claimant's say-so, or held after its seat died with no observer able to release it

P:code claims-audit | INSTANCE-FAILURE | "Audit canonical state before and after: HEAD, index entries and flags, refs, reflogs, stash, tracked contents, and ignored/untracked path inventories" | Unchanged: for a mutation-capable key 2, §10 step 6 records the SCRATCH worktree's state at removal, never the main checkout's before and after | no replacement | PROOF: a key-2 run here whose receipt records the main checkout's HEAD, index entries and flags, refs, reflogs, stash, tracked contents and ignored/untracked path inventories with content hashes, before and after

P:code independent-key | UNEXERCISED | "a verifier from another model family (R3) whose class has not become a producer of the subject" | No kernel subject was accepted. The contribution records the bench asked for are above: on 13 of 14 landings key 1's class also reviewed the approach, and all 13 receipts record its findings as confirmed, adopted or answered, in the approach or by IMPLEMENT | PROOF: a subject here whose only other-provider key comes from a class that also wrote its product bytes

P:code resource-terminals | INSTANCE-FAILURE | "Before dispatch, declare any register-permitted substitution for a family-bound quorum seat" | The latent gap the last harvest disclosed stands in the rule: docs/14 §2 orders a SINGLE-FAMILY round's `cross_family: UNAVAILABLE <provider> <UTC ISO>` label into "its receipt", written at landing, and no rule orders the substitution declared before dispatch. Exercised three times in the window, each declared in time by practice: one withheld witness's approach review, moved from Codex to `claude-fable-5-1`, carries the label in its launch json, whose `startedUtc` is the same second the file was written, with the seat's verdict file five minutes later; and two key-1 seats of an in-flight measurement card, moved to `claude-fable-5-1` on Codex failovers, each carry the label in their launch json at their own `startedUtc` (reported in aggregate, bus law 4). Seats following a practice are not a mechanism, as with K5 | no replacement | PROOF: a rule here that orders every substituted seat's declaration written before its dispatch, and a window in which each substituted seat's launch record carries it

P:code delivery-target | INSTANCE-FAILURE | "build the exact proposed record and run the validators and hooks that commit will face before any product push; refuse on failure" | Unchanged in mechanism: the local pre-commit hook runs before every landing, but hosted CI runs only on the derived mirror, after the push (docs/14 §3). Every cop daily-ledger line in the window reads `ci=success` | no replacement | PROOF: a landing here whose hosted validators ran green before its mirror push

P:code dispatch-preflight | INSTANCE-FAILURE | "the spending tool runs the project's resume gate before dispatch and retains its result, the inventory snapshot and digest, and account-parity evidence" | Unchanged: docs/13 P-COP orders no resume-gate, inventory or parity read before dispatch, so none of the window's 128 dispatches is ordered to retain them; this filing did not read the tick notes for a seat that retained them unordered — the K10 gap | no replacement | PROOF: a tick receipt here that retains a resume-gate result, an inventory digest and parity evidence before its first dispatch

P:measured-objective acceptance-evidence | UNEXERCISED | "the declared scorer on a held-out fold the producer never tuned on" | No SCOREBOARD line falls inside the window (its newest is `20260918-1356`), so no candidate was scored | PROOF: a scored run in the window that this line missed

## Instance failures

Status of the earlier fifteen:
- **IF1, IF11**: historical, unchanged.
- **IF2: repaired in the latent script**; `tools/ratify.ps1` is still off the live landing path (0 of 14 window receipts name it).
- **IF3, IF4, IF10: LATENT**, as before.
- **IF5: repaired in the latent script**; no gate0 ran on the live route.
- **IF6: LIVE.** WORK.md:4 still reads "Merge: tools/ratify.ps1 (gate 0 + cross-family key + adversarial Claude key)".
- **IF7**: resolved at an earlier read, and outside git.
- **IF8: unchanged.** `tools/claude-review-capture.ps1` and `tools/codex-author-capture.ps1` are both still absent.
- **IF9: unchanged.**
- **IF12: unchanged.** The window's receipts use two of the earlier encodings — a `seats` object with an `authors` list and a `rounds` list of `k1`/`k2` maps (13), and a `seats` list of `{role, model, …}` entries (FOREIGN-POPULATION) — and add none; 4 of the first kind keep their mirror-sync record in `evidence` files rather than a field (K7).
- **IF13: unchanged.**
- **IF14: resolved**, as before; what hosted CI finds is P:code delivery-target.
- **IF15: unchanged.** 0 declarations in a third consecutive window.

## Untested

U6 | The `posture:` line (ROUTED, unchanged). The same limit applies to `tools/harvest-status.py`.

U8 | Whether any of the 6 feature-assembly landings changed the grade the shipped defaults emit (the 8 test-only landings cannot). Not derived here.

## Instance map

KERNEL: DOGFOOD fleet-factory-kernel r5 · profile code@r10 + measured-objective@r3 · instance docs/KERNEL-INSTANCE-MAP.md · since 2026-10-02

The instance map is `docs/KERNEL-INSTANCE-MAP.md` on nested-repo master; this section points at it and keeps no table. Its
first line declares `kernel: fleet-factory-kernel r5 · profile: code@r10 + measured-objective@r3`, the revisions this
filing reads on the bus tip, so no older revision is reported. Its K1-K12 rows are that card's, and this seat writes none
of them. By its own rows, K3, K5, K6, K7, K8, K9, K10 and K11 are `NONE`, each with its nearest partial mechanism.

## Counts

Clauses: 4 FIT · 0 FRICTION · 0 BREAK · 0 N/A · 5 UNEXERCISED · 3 INSTANCE-FAILURE
Profile: 1 FIT · 0 FRICTION · 0 BREAK · 0 N/A · 2 UNEXERCISED · 5 INSTANCE-FAILURE
Ledger totals (INSTANCE-FAILURE excluded per kernel §5): **5 FIT · 0 FRICTION · 0 BREAK · 0 N/A · 7 UNEXERCISED**
Plus a status line for each of the fifteen earlier numbered instance failures (no new IF number; this window's INSTANCE-FAILURE lines are the K and P lines above), answers to U6, U7, U8, §a.u4, the
independence-provenance bench and the resource-terminals disclosure, and 2 Untested.
