project: dng-auto-processor
kernel: fleet-factory-kernel r5
profile: code@r11 (primary) + measured-objective@r3 — kernel §6's row as harvested (M1)
instance: docs/KERNEL-INSTANCE-MAP.md on nested-repo master (written by card KERNEL-DOGFOOD-INSTANCE-MAP under docs/14 §0's kernel entry, landed `db197676`; KERNEL line DOGFOOD, ## Instance map). The map's own first line still declares code@r10 (## Instance map)
subjects: 0 end-to-end under the kernel, and 0 declared inside this window — no `k5-declaration.json` was written after 2026-10-23T08:14Z (K5). Reported as mechanism evidence and never counted: 1 landing on this board's own two-key route, with a committed receipt, which declared no profile; 2 ledger-only measurement cards and 1 pointer card closed. 0 PRODUCT commits landed off that route (## Subjects).
window: 2026-10-23T08:14Z .. 2026-10-30T19:58Z (nested-repo master as it stood at the window's end, `ef7a8304`; the WORK.md working copy for the cop's uncommitted ledger lines)
health: assurance=UNSATISFIED operability=PRESSURED
providers: none (no lane cleared a sentinel for this filing)
posture: not computed — model review contributed (the route's approach review and keys), and the R9 tool is one PROMPT K names, which docs/13 P-STEWARD step 7e forbids the filing seat to run (U6, ROUTED; unchanged)

Eighth filing by this board. It is a re-run on PROMPT K §6's weekly cadence, and it is also the filing §6 asks for "at a
blocked or failed work seam even when nothing completed": since 2026-10-24T10:33Z the traffic cop has made no commit,
and its ticks are no-ops (## Subjects, the stall seam). The kernel (r5), `profiles/code.md` (r11) and
`profiles/measured-objective.md` (r3) are unchanged since the seventh filing (no bus commit touches them after
`a0a1325f`, 2026-10-13), and the `KERNEL:` line below is byte-identical to the seventh filing's.

**The seventh filing is not yet answered.** It is blob `27aeb99208a035d09e157936cc4f01b901f26e97` on
`origin/review/dng-auto-processor-kernel-2026-10-23`. The bus's `dng-auto-processor.dispositions.md` still binds
`filing_blob: cce576ba…` (the sixth filing), and `HARVESTS.md`'s newest row is dated 2026-10-17. By PROMPT K §6 this re-run
keeps every finding of the seventh filing, with its original evidence reference, until the steward answers it. So the
seventh filing is carried **whole and verbatim** under `## Carried: the seventh filing, undisposed` at the end of this
file. Each line there is prefixed `> `, and nothing else is changed. The lines above that section are this window's
evidence. Each one names the seventh filing's verdict where the verdict moved, and otherwise says it is kept. The seat
that writes it is `dng-design-steward`. It works from this board's own cards, receipts and ledgers, and it ran no subject.

`assurance=UNSATISFIED`: no subject was declared or accepted under the kernel, and the product's own bar produced no
acceptance either. WORK.md's SCOREBOARD has no line inside the window (its newest is still `20260918-1356`).
`operability=PRESSURED`, and more so than last window. Over the cop's daily-ledger lines dated 2026-10-23 to 2026-10-30
there were 90 ticks, 25 dispatches, 21 collections and 1 landing in the window. The 10-23 line's pre-window share is
subtracted, as that line read on master at the window's start. That is 25 dispatches per landing, against about 13 last
window. From the seventh tick of 2026-10-24 onward, every tick is a no-op. The DAILY note on 2026-10-30 18:33Z records
the seventy-fifth consecutive one, and the DAILY lines for 2026-10-25 to 2026-10-30 each read `collected=0 landed=0
dispatched=0`. The board's THROUGHPUT-STALL has stood since 2026-10-27T03:03Z, 72 h after the newest feature-assembly
commit (`73cb6c06`, committed 2026-10-24T03:03:27Z), and docs/14 §7 alarm 1 has fired since the 2026-10-26 04:11Z tick.
Every daily line reads `ci=success`. The design steward seat's scheduled run was held out of its slot for 108 h 4 min
(K2). Two account rotations fall in the window (K9). Twelve steward passes began inside the window: 10 ended ACTED, 1
never wrote a verdict (the held run), and the 12th is the pass writing this filing. 4 commits in the window are the
steward's, and each touches only docs, packets or WORK.md.

Unqualified paths and commit ids are this board's repository. Evidence kept outside it is named by description, never by
path, as before (bus law 4). Doctrine paths are qualified. **The lineage the seventh filing counted and did not describe
has left flight and is named here.** Its three PARKED cards were PRESET-COLOUR-KEYS-FLAG,
PRESET-COLOUR-KEYS-FLAG-SHAPE-DOMAIN-BATCH-PASS and PRESET-COLOUR-KEYS-FLAG-ANCHOR-RECORD-BATCH-PASS. All three closed
"ON ITS OWN STATED RELEASE: ITS LINEAGE LANDED" at 2026-10-24T04:13Z, when their batch-pass successor landed `7165d27b`
(## Subjects). At this window's end no card is RUNNING, READY, PARKED or HELD: 11 cards are open, all of them POINTER,
MEASURED-NEGATIVE, RULED or the CLOSED `Q1a` trap. So this filing withholds no card.

## Subjects

**Kernel subjects: none.** No rule, tool or hook reads `k5-declaration.json` (IF13), and none orders one written. In this
window nobody wrote one (IF15): a case-insensitive file-name search of the evidence ledgers for `k5-decl*` returns 4
files in all, none modified after the window opened. The one landing receipt names no kernel or profile revision, and
neither do the 7 cards changed in the window.

**The one landing on this board's own route, reported and never counted.** Its receipt is
`metrics/ratify/PRESET-COLOUR-KEYS-FLAG-WIRING-CENSUS-BATCH-PASS/3/receipt.json` on master. It landed by plain
`git merge --ff-only` of `7165d27b` onto master `2a637449` at 2026-10-24T04:12:39Z. The columns are those of the seventh
filing's table.

| Task / attempt | Keys' subject → landed (tree same?) | Assembly | Author → key 1 / key 2 | Surplus PRODUCT |
|---|---|---|---|---|
| PRESET-COLOUR-KEYS-FLAG-WIRING-CENSUS-BATCH-PASS / 3 | 7165d27b → 7165d27b (yes; the committer's `8f1a447c` was rebased by the cop onto `2a637449` over inert paths before the keys ran) | Core (`RulesEngine.cs`, `AutoProcessor.cs`, both carried) | test lines: gpt-6.1-sol (att 1), then gpt-6-astra (att 2, 3); carried production commit: claude-fable-5-1 + claude-sonnet-5-5 (commit trailers) → claude-fable-5-1 / claude-opus-5-5 (rounds 1 and 2 key 2 BLOCKER, 1 confirmed each) | 0 |

The landed range holds 4 commits over 4 paths. The first, `73cb6c06`, is the byte-identical carry of the parked parent's
reviewed subject: it squashes `78b9ead6`, `1d8a40d5` and `23f50adc`. `23f50adc` is the only one of the three that touches
`DngAutoProcessor.Core`, and its trailers name `claude-fable-5-1` and `claude-sonnet-5-5`. The carry commit's own
trailers add `gpt-6.1-sol`. The other three commits are test lines, and their trailers name `gpt-6.1-sol` (`2e7aa320`) and
`gpt-6-astra` (`5671a450`, `7165d27b`; `7165d27b` also carries a `Claude Sonnet 5.5` co-author trailer). The receipt's `seats.author` records only the three test-line attempts. The
approach review is `claude-fable-5-1` ACCEPT 0/0/4. Round 3 reads key 1 Fable ACCEPT 0/0/1 and key 2 Opus ACCEPT 0/0/2,
with 3 MINORs owed (`owedMinors`). The product change ships default-off:
`public bool ApplyUserPresetColourKeys { get; set; } = false;` (`DngAutoProcessor.Core/Models/RulesEngine.cs:651`).

**Closed without a landing (ledger only, nothing committed by a seat, no default moved), reported and never counted.**
- `packets/LEARNED-TARGET-OL-TRACED-MEASUREMENT.md`: DONE at attempt 2. Attempt 1 closed MEASURED-NEGATIVE on the card's
  own stale store pin. The compute seat was gpt-6.1-sol, and the §6 disposition is gpt-6-astra `VERDICT: RESULT-STANDS`
  with 2 MINOR.
- `packets/LEARNED-TARGET-OL-PRODUCT-FACTORIAL.md`: DONE at attempt 1. The compute seat was gpt-6.1-sol, and the §6
  disposition is gpt-6-astra `RESULT-STANDS` with 3 MINOR. Its section 4 routes the next question (does the product's
  parity with the research survive a prospectively specified set of more clips and boundary cases) with no outline. That
  question is the design card at the centre of the stall seam below.
- `packets/LEARNED-TARGET-OL-BACKFILL-DATA-2.md` (a pointer): DONE on its own typed return. Both of its subpackets had
  landed in the seventh filing's window.

**Off-route landings: none.** The window's master history is 16 commits, all first-parent. 4 touch a PRODUCT path (docs/14
§4's closed set): `73cb6c06`, `2e7aa320`, `5671a450` and `7165d27b`, which are exactly the landed range above. The other
12 are 8 cop bookkeeping commits, all dated 2026-10-23T13:16Z to 2026-10-24T10:33Z, and 4 steward commits that touch only
docs, packets or WORK.md (`9ea8beab`, `584f026c`, `0356eea2`, `ef7a8304`). 1 receipt file was added in the window:
`git -C <repo> log --since=2026-10-23T08:14Z --diff-filter=A --name-only --format= master -- 'metrics/ratify/*/receipt.json' | grep -c .` (1).

**The blocked seam (PROMPT K §6), filed against the clauses it exercises.** The cop's last commit is `1893eb97`
(2026-10-24T10:33:40Z). Every tick since then is a no-op that by rule commits nothing (P-COP Step 5: no card state
changed). So the stall is recorded only in the WORK.md working copy: the DAILY lines for 2026-10-24 22:33Z to
2026-10-30 and one `STALL` line (`git diff master -- WORK.md`: 9 insertions, 2 deletions). Its blocking artifact is the
routed design question above, which docs/14 §2 posture (3) lets the cop open as a design card. The cop withheld that card
across the window, and its own tick notes give four successive grounds:
1. From 2026-10-24 to 2026-10-28 07:53Z, the seat for design acts, the design steward, had a scheduled run held out of its
   slot. Its `lastRunAt` stayed 2026-10-23T19:49:51Z until 2026-10-28T07:53:51Z, and its skip run reached 5,898 entries.
   docs/14 §7 alarm 6 arm B fired across that span: the DAILY notes for 2026-10-23 to 2026-10-27 each list 6B, and the
   tick notes this filing sampled name the steward's task with addressee USER. By that alarm's text, a held run occupies
   one of the app's scheduled slots "until a person clears it". The run was stopped between 06:50Z and 07:53Z on
   10-28, and no artifact records by whom. The held pass's receipt has no verdict line, and the next pass recorded the
   hang as having "no recorded cause". → K2 (FRICTION, below).
2. Through 2026-10-28, the cop also withheld the card under a local duplicate-direction caution, WORK.md QUEUE 5's, while
   the separate research campaign's writer lease was live.
3. At the 2026-10-28 22:23Z tick, the lease had expired and its writer had been stranded by the rotation. That tick's own
   boot exceeded docs/14 §3's budget, which left it only split or park.
4. From the 2026-10-30 08:23Z tick on, the cop withheld the card on an owner decision of 2026-10-29: a definition of done
   for the automatic-grading research, with a stop rule the research writer then ruled TRIGGERED. That decision is
   recorded in this board's evidence ledger, outside docs/14 §0 (no §0 line is dated after 2026-10-23). Its recorded scope
   names the research, and it says the decision does not by itself approve a product change or landing. The cop's note
   says plainly that extending it to a factory design card is the cop's own reading, and that a wrong reading costs a
   withheld card.

No artifact this filing read records a question to the owner about that reach (U12). That covers the cop's tick notes
of 2026-10-30, the steward's receipts of 2026-10-28 to 2026-10-30, and the USER items of the 2026-10-30 P-RESUME receipt. This filing claims no BREAK
from the seam. The seam does not exercise capacity (K8): none of the four grounds is a quota event. It does exercise
claims only through the research lease's expiry and the held steward run, and the latter is a scheduler slot, not a
claim on a subject (K3).

## Answers to the benches the last harvest routed

The seventh filing's answers to these benches are carried verbatim below. Each one is re-answered here on this window's
evidence.

- **U7 (ADOPTED-CONDITIONAL, dng outcome-reporting bench), the O2 denominator across a seventh window: 1 of 1.** The
  predicate is unchanged. The one landing's delivered range touches `DngAutoProcessor.Core`. The earlier windows read 4
  of 11, 6 of 14, 3 of 11, 7 of 15, 12 of 17 and 12 of 23. Assembly contact is not proof of a changed emitted grade (the
  dispositions' condition), and this filing does not claim it.
- **U8 (ROUTED, dng measured-objective outcome bench), the emitted-grade effect: partly derived, one more window.** The
  one assembly landing adds an owner-sourced switch, `ApplyUserPresetColourKeys`, which defaults to false
  (`RulesEngine.cs:651`). The receipt's `productChange` states that there is no behaviour change unless the switch is
  set. The window's two measurement cards measured parity between the product's ingest and the research estimator on four
  pinned clips. Both close with `LearnedExposureTarget` still false (`RulesEngine.cs:627`), and both license no default
  change, gate or attribution. Still not derived, as before: whether the owner's saved engine sets
  `LearnedExposureTarget`, `PropagateManualGrades` (no initialiser, `RulesEngine.cs:203`) or now
  `ApplyUserPresetColourKeys`. No SCOREBOARD line in the window measures an emitted grade.
- **Independence-provenance bench (ROUTED; P:code independent-key): the contribution records, for this window.**
  - **Keys and approach review.** On the one landing, key 1 (`claude-fable-5-1`) is from the provider opposite the
    authors the receipt records (Codex: gpt-6.1-sol, gpt-6-astra), and key 2 is `claude-opus-5-5`. The approach reviewer
    and key 1 are the same model (`claude-fable-5-1`). That is the pattern the seventh filing counted on 10 of 23.
  - **New this window: the receipt's author field is not the whole producer set.** The delivered range carries
    production bytes that the receipt's `seats.author` does not name. Those bytes are `RulesEngine.cs` and
    `AutoProcessor.cs`, carried byte-identically from `23f50adc`, whose trailers name `claude-fable-5-1` and
    `claude-sonnet-5-5`. So key 1's own model is a named co-author of product bytes it keyed, and both providers produced
    bytes of the delivered range. The parent lineage's cards record an other-provider key on those production bytes:
    `gpt-6.1-sol` key 1 on PRESET-COLOUR-KEYS-FLAG round 2, and on PRESET-COLOUR-KEYS-FLAG-ANCHOR-RECORD-BATCH-PASS round 2
    (ACCEPT 0/0/0 on `78b9ead6`). That key's provider also wrote this landing's attempt-1 test lines.
  - **Re-grading.** No key's final-round non-ACCEPT was re-graded to land (0 of 1). Key 2's BLOCKERs in rounds 1 and 2
    were confirmed, and attempts 2 and 3 followed.
  - **The measurement cards.** On both cards, the §6 disposition seat (`gpt-6-astra`) is of the same provider as the
    compute seat (`gpt-6.1-sol`).
  - Whether a carried subject's earlier keys count toward the landing's independence is not decided here (U11).
- **§a.u4 (ROUTED, delivered-pipeline delayed-outcome fixture): none to bring.** This board accepted no subject under the
  kernel, and no SCOREBOARD line falls in the window.
- **U6 (ROUTED, authorised posture-computation seat): unchanged.** No register-authorised seat computed R9 for this
  filing, and no owner word authorising one is recorded in docs/14 §0.
- **U9 (ROUTED, dng doctrine-consumer stewardship): unchanged.** The 2026-10-09 doctrine-consumer fold-set routing line
  (WORK.md:100) is still unopened, no card names it, and neither steward docs commit in the window (`584f026c`,
  `0356eea2`) acts on it.
- **Stale instance map (HEADER, ROUTED to its authorised maintainer): unchanged.** Its K9 row is overtaken further: the
  resume-drill evidence folder now holds 6 receipts, 1 of them dated in this window (## Instance map).
- **P:code resource-terminals (ADOPTED as an INSTANCE-FAILURE): not exercised this window**, reported on that line.

## Clauses

K1 | UNEXERCISED | "A candidate is never accepted on evidence whose only author is its producer" | Kept from the seventh filing (UNEXERCISED). No kernel subject existed. Reported without credit: the one landing's acceptance evidence includes key 2 `claude-opus-5-5`, which no commit in the range names as an author. But key 1 `claude-fable-5-1` is a trailer-named co-author of the carried production commit it keyed (`23f50adc` → `73cb6c06`; independence-provenance bench above). No PRODUCT commit landed off the route | PROOF: a kernel subject accepted here on receipts naming one actor for production and acceptance

K2 | FRICTION | "Escalation goes to the owner for decisions reserved by that register" | Moved from FIT (the seventh filing's K2: 23 landings taken without asking; reserved decisions routed to the owner). The register is unchanged: docs/14 §0 plus WORK.md RULES rule 3, with docs/14 §7's alarms naming their addressees. **What held:** the one landing needed no owner act, and the owner-reserved act this window met was escalated, never taken. That act was clearing the design steward's held scheduled run, which docs/14 §7 alarm 6 arm B reserves to "a person". The alarm fired with addressee USER from 2026-10-23 until 2026-10-28T07:53Z (DAILY notes 10-23 to 10-27, sampled tick notes), and no seat stopped the run on its own. **The cost, measured:** the design-act seat was out of its slot for 108 h 4 min (`lastRunAt` 2026-10-23T19:49:51Z → 2026-10-28T07:53:51Z; 5,898 skips). No artifact records the person who cleared it. For the first four days of the stall, the cop's notes name that hold as the limiting authority on the routed design card. **A second cost of the same clause:** from 2026-10-30 08:23Z the card is held by an owner decision recorded outside the register, on a reach the cop calls its own reading (## Subjects, the stall seam). The register neither reserves nor releases that act, and no artifact this filing read records a question to the owner (U12). Seventy-five consecutive no-op ticks and zero dispatches from 2026-10-25 to 2026-10-30 accrued while the clause held. Escalations went where the register sends them: 1 OWNER-DEFECT line dated in the window (2026-10-23 10:52Z, closed 14:29Z by steward commit `584f026c`), and 1 earlier token closed (`ef7a8304`). None of the window's 8 cop-tick commits touches docs/12, docs/13 or docs/14 | REPLACES: "Escalation goes to the owner for decisions reserved by that register" -> "Escalation goes to the owner for decisions reserved by that register, and each reservation that holds work names what proceeds, and by whom, while the owner has not answered" (one profile's FRICTION; kernel §5 changes the kernel only on a second profile's report) | PROOF: a reserved hold in this window that some register text bounded or released without an owner act

K3 | FIT | "under a claim an observer other than the claimant can decide stale and release; an expiring lease is one such mechanism" | Kept from the seventh filing (FIT: 5 observer releases). The mechanism is unchanged. It was exercised in this window twice. (1) A card claim: the attempt-2 COMMIT seat of PRESET-COLOUR-KEYS-FLAG-WIRING-CENSUS-BATCH-PASS froze after committing `af89de5c` ("freeze 1 of 3", receipt `seats.committer`), and the cop's relaunch adopted that commit and wrote its `binding.json` (cop-tick subject `2a637449`). (2) An expiring lease: at the 2026-10-28 22:23Z tick, the cop decided from outside that the research campaign's writer lease was EXPIRED, by the campaign's own lease rule, and treated the writer as stranded by the rotation. Not a subject claim, and so not counted here: the design steward's held scheduled run (K2), which held a scheduler slot, never a card. The instance map's K3 row is still NONE for an identity held by one claimant at a time with an atomic claim | PROOF: a claim here still held after its seat was dead, with no observer able to release it

K4 | FIT | "Work is complete only on positive evidence it was asked to produce" | Kept from the seventh filing (FIT). This window's refused evidence: key 2 BLOCKERs confirmed in round 1 (3/1/2) and round 2 (1/0/3, a new class) each stopped PRESET-COLOUR-KEYS-FLAG-WIRING-CENSUS-BATCH-PASS until attempt 3. LEARNED-TARGET-OL-TRACED-MEASUREMENT's attempt 1 closed MEASURED-NEGATIVE on its own stale store pin rather than DONE, and its first compute seat's BLOCKED was traced to a harness defect, with the pins re-verified rather than refreshed. The landing's CI Release build was run again after the first run "died on the cop's own invocation" (receipt `ciReleaseBuild`). Counter-observation, kept here rather than credited: key 1 read ACCEPT in rounds 1 and 2 both times key 2's BLOCKER was confirmed, and the round-2 receipt records that key 1's own MINOR was the confirmed BLOCKER's route, "adjudicated up" | PROOF: a card here closed DONE on a return code or a file's presence alone

K5 | UNEXERCISED | "Before work starts, a subject declares its profile and profile version." | Kept from the seventh filing (UNEXERCISED). 0 `k5-declaration.json` dated inside the window (IF15). No landing receipt records a profile: 0 of 1 receipts, and 0 of the 7 cards changed in the window, name `code@r`, `measured-objective@r` or the kernel. The sweep that supports this negative is a case-insensitive file-name search of the evidence ledgers for `k5-decl*` (4 in all, none modified after 2026-10-23T08:14Z) | PROOF: a subject accepted here whose acceptance receipt names a different identity or profile than its declaration

K6 | UNEXERCISED | "Every acceptance includes a key from an independence class other than the producer's." | Kept from the seventh filing (UNEXERCISED). No kernel subject was accepted. Reported without credit: on the one landing, key 1 is from the provider opposite the receipt-recorded authors, but the delivered range's production bytes were produced in key 1's and key 2's own provider (independence-provenance bench above). On the two measurement cards, the disposition seat and the compute seat share a provider | PROOF: an accepted subject here whose keys and producer share one provider

K7 | UNEXERCISED | "Acceptance and delivery are separate states." | Kept from the seventh filing (UNEXERCISED). Nothing was accepted under the kernel. Reported without credit: the one landing reached nested-repo master by `--ff-only` of an exact sha. Its receipt's `mirror` field records the mirror sync (rc 0, product byte identity verified), and master's hosted CI read `ci=success` on every daily line of the window. No typed `CLOSURE_INCOMPLETE` exists here (IF9) | PROOF: an accepted subject here that never landed and that the next tick names unprompted

K8 | UNEXERCISED | "Reset events update capacity telemetry. They never open a gate by themselves." | Kept from the seventh filing (UNEXERCISED). This window's one quota event: the cop's 2026-10-30 06:23Z fire died in 5 s on the account's session limit and did no work. Nothing was in flight, because the open set held no RUNNING card, and the 08:23Z fire ran. No artifact this filing read records a reset event as such. The window's stall is not a capacity stall: the four grounds the cop's notes give for it are a held scheduler slot, a local caution, a boot-budget rule and an owner decision (## Subjects) | PROOF: a reset event here that by itself re-opened a darkened seat

K9 | INSTANCE-FAILURE | "A fresh session on a new account, with empty memory, resumes from the project's tree and the bus alone." | Kept from the seventh filing (INSTANCE-FAILURE). Exercised twice in this window, and the adopted failure recurred once. Two account rotations are recorded (the SessionStart hook at 2026-10-28T19:38Z, and a catch-up fire on 2026-10-30 at about 13:40Z), each followed by a P-RESUME receipt (2026-10-28 23:01Z and 2026-10-30 13:50Z). P-RESUME runs on the owner's "resume our work". **On 10-28:** the cop and the steward were found on the new account, and the steward ran there at 19:50Z, but the cop's row carried a stale cron that the pass corrected. Two scheduled tasks registered on the departing account, the resume drill and the usage watch, were absent, and each was re-created only on the USER's answer "Re-create it". The status-digest task was listed and not re-created. The CLI's account had drifted from the desktop's, which needed the USER's re-authentication. The research writer stranded by that rotation is revived only by the attended "resume our work". **On 10-30:** nothing needed re-creating, and the cop ran by catch-up before the P-RESUME pass. 0 lines added to docs/13 or docs/14 in the window mention P-RESUME, re-registration or inventory | no replacement | PROOF: a rotation here after which every scheduled seat the register authorises ran again with no owner step

K10 | INSTANCE-FAILURE | "Provider and model inventory is machine-scoped and probe-derived, and it records the account it was derived under." | Kept from the seventh filing (INSTANCE-FAILURE). Unchanged: there is no machine-readable inventory and no `probed_under` in the repo (the instance map's K10 row). This window's two rotations recorded account identity only outside the repo, in the P-RESUME receipts. On 10-28 that included a detected drift between the CLI's and the desktop's accounts, repaired by the USER's re-authentication | no replacement | PROOF: an in-repo inventory whose `probed_under` names the current account

K11 | INSTANCE-FAILURE | "R1–R5, R7, R8 and R9 apply to every report a factory makes about itself" | Kept from the seventh filing (INSTANCE-FAILURE). Unchanged: the two OWNER-DEFECT-CLOSED lines that `131ad1f2` appended (WORK.md, dated 2026-09-23 14:05Z) still stand with no correction line beside them. New this window, an observation about where the self-report lives rather than whether it is true: the board's only record of the six-day stall is in the WORK.md working copy (DAILY lines 2026-10-24 22:33Z to 2026-10-30, and the STALL line). Master's newest DAILY line is still 2026-10-24 10:33Z, so a fresh clone of master reads no stall. The 2026-10-24 line was again rewritten in place, from `ticks=6` to `ticks=12`. This filing takes no credit for the window's landing and asserts no posture it did not compute | no replacement | PROOF: a correction line beside that CLOSED line in the board's ledger

K12 | FIT | "The steward harvests every filing and answers each one." | Kept from the seventh filing (FIT on the sixth filing's harvest of 2026-10-16, harvest `20261016T090409Z-078e6f76`). Status this window: the seventh filing (blob `27aeb992`, pushed on its review branch 2026-10-23) has no disposition yet. The dispositions file still binds `cce576ba`, and `HARVESTS.md` was last changed 2026-10-17. This re-file keeps the seventh filing's findings whole (the carried section), as §6 asks. FENCE: the filing seat may not run `tools/harvest-status.py`, so the harvested state is read from the artifacts that tool reads | PROOF: a finding of the sixth filing with no disposition line

## Profile lines

P:code subject-identity | INSTANCE-FAILURE | "its identity is K3's `sha256` of that OID's lowercase hexadecimal text, with no trailing newline" | Kept from the seventh filing (INSTANCE-FAILURE). This window's landing delivered the very commit its keys reviewed (both keys' verdict files name `7165d27b`), with 0 PRODUCT paths beyond it. The binding is per-file blob identity plus `patch-id`, never a tree OID. The committer's `binding.json` names `8f1a447c`, which the cop rebased onto `2a637449` before the keys ran. The hook ran on `8f1a447c`, and the CI Release build on `7165d27b`. 0 of 1 receipts records a tree OID or its K3 `sha256`, reviewed or delivered. The measured-objective half is unchanged: `tools/scoreboard.ps1` hashes its inputs, but no scoreboard run in the window exercised it | no replacement | PROOF: a receipt here recording each subject's tree OID and K3 digest, reviewed and delivered alike

P:code claims | FIT | "observer-released claims may replace leases" | Kept from the seventh filing (FIT). Exercised in this window once on a card claim (the frozen attempt-2 committer whose commit the cop's relaunch adopted, K3) and once on an expiring lease, the research writer's, which the cop decided expired from outside (K3). In each case the observer, not the claimant, decided | PROOF: a claim here released by its own claimant's say-so, or held after its seat died with no observer able to release it

P:code claims-audit | INSTANCE-FAILURE | "Audit canonical state before and after: HEAD, index entries and flags, refs, reflogs, stash, tracked contents, and ignored/untracked path inventories" | Kept from the seventh filing (INSTANCE-FAILURE). Unchanged. The one landing's key 2 ran a mutation battery in a scratch worktree. Its receipt mentions neither reflog nor stash (0 of 1), and no line added to docs/14 in the window mentions either | no replacement | PROOF: a key-2 run here whose receipt records the main checkout's HEAD, index entries and flags, refs, reflogs, stash, tracked contents and ignored/untracked path inventories with content hashes, before and after

P:code independent-key | UNEXERCISED | "a verifier from another model family (R3) whose class has not become a producer of the subject" | Kept from the seventh filing (UNEXERCISED). No kernel subject was accepted. This window's records bear directly on the clause without exercising it. In the one landing's delivered range, the Claude family produced the carried production bytes and the Codex family produced the test lines (the last of which also carries a Claude Sonnet co-author trailer). Every key seated on the range was of a family that produced bytes of it: Fable and Opus in this card's rounds, and Sol in the parent lineage's rounds on the carried bytes. So had this subject been declared, no seated key would meet the clause's "class has not become a producer" limb as this filing reads it (U11) | PROOF: a subject here whose only other-provider key comes from a class that also wrote its product bytes

P:code resource-terminals | INSTANCE-FAILURE | "Before dispatch, declare any register-permitted substitution for a family-bound quorum seat" | Kept from the seventh filing (INSTANCE-FAILURE). The latent gap stands in the rule. In the window, `0356eea2` adds one label, `t3: UNAVAILABLE <provider> <UTC ISO>`, recorded beside a degraded disposition, which is again a record written with the act and not a declaration before dispatch. Not exercised this window: of 31 `launch*.json` files modified inside the window (searched to depth 4 of the evidence ledgers), 0 carry a cross-family label and 0 name a failover or substitution | no replacement | PROOF: a rule here that orders every substituted seat's declaration written before its dispatch, and a window in which each substituted seat's launch record carries it

P:code delivery-target | INSTANCE-FAILURE | "build the exact proposed record and run the validators and hooks that commit will face before any product push; refuse on failure" | Kept from the seventh filing (INSTANCE-FAILURE: half repaired). This window's landing ran CI's `Release build` step with `--warnaserror` at `7165d27b`: rc 0, 0 warnings, 0 errors. Hosted CI after the mirror push read success. What still stands: the hook's build line still carries no `--warnaserror` (0 occurrences in `.githooks/pre-commit`); hosted validators still run only after the mirror push; and the repro card owed for the seventh window's hosted failure (one `ProgramSettingsTests` case at `8d7dd999`) is still unopened. The STALL line lists it among the items the stall releases with no card-ready outline (U10) | no replacement | PROOF: a landing here whose hosted validators ran green before its mirror push

P:code dispatch-preflight | INSTANCE-FAILURE | "the spending tool runs the project's resume gate before dispatch and retains its result, the inventory snapshot and digest, and account-parity evidence" | Kept from the seventh filing (INSTANCE-FAILURE). Unchanged: docs/13 P-COP orders no resume-gate, inventory or parity read before dispatch, and no line added to docs/13 or docs/14 in the window adds one. So none of the window's 25 dispatches is ordered to retain them. The two rotations' parity evidence was read by owner-started P-RESUME passes, not by the spending tool | no replacement | PROOF: a tick receipt here that retains a resume-gate result, an inventory digest and parity evidence before its first dispatch

P:measured-objective acceptance-evidence | UNEXERCISED | "the declared scorer on a held-out fold the producer never tuned on" | Kept from the seventh filing (UNEXERCISED). No SCOREBOARD line falls inside the window (its newest is `20260918-1356`), so no candidate was scored by the declared scorer. The window's two measurement cards measured exact parity between the product's computation and the research estimator on four pinned clips. Both say they license no acceptance gate. That is parity of a computation, not held-out acceptance of a candidate | PROOF: a scored run in the window that this line missed

## Instance failures

Status of the earlier fifteen. No new IF number; this window's INSTANCE-FAILURE lines are the K and P lines above.
- **IF1, IF11**: historical, unchanged.
- **IF2: repaired in the latent script.** `tools/ratify.ps1` is still off the live landing path: 0 of 1 window receipts land
  through it ("plain git merge --ff-only"), and the window's landed range does not edit it.
- **IF3, IF4, IF10: LATENT**, as before.
- **IF5: repaired in the latent script.** No gate0 ran on the live route (0 of 1 receipts records one).
- **IF6: LIVE.** WORK.md:4 still reads "Merge: tools/ratify.ps1 (gate 0 + cross-family key + adversarial Claude key)", on
  master and in the working copy.
- **IF7**: resolved at an earlier read, and outside git.
- **IF8: unchanged.** `tools/claude-review-capture.ps1` and `tools/codex-author-capture.ps1` are both still absent from master.
- **IF9: unchanged.** No file outside the instance map names `CLOSURE_INCOMPLETE`.
- **IF12: drift stands, no new field.** The window's one receipt is `seats` as an object, keyed by role and nested by
  attempt and round; `rounds` as a prose string; the mirror record in a `mirror` field; and `ciReleaseBuild` present. Its
  top-level fields are all already present in the seventh window's 23 receipts.
- **IF13: unchanged.** No rule, tool or hook names `k5-declaration` (a `git grep` of master's docs, tools, .githooks and
  scripts finds only the instance map).
- **IF14: resolved**, as before. What hosted CI finds is P:code delivery-target.
- **IF15: unchanged for this window.** 0 declarations dated inside it.

## Untested

U6 | The `posture:` line (ROUTED, unchanged). The same limit applies to `tools/harvest-status.py`.

U8 | Whether any assembly landing, the seventh window's 12 or this window's 1, changed the grade the owner's saved engine emits: in particular, whether that engine sets `LearnedExposureTarget`, `PropagateManualGrades` or `ApplyUserPresetColourKeys`. The class defaults are derived above; the saved engine was not read.

U9 | Not tested here; read from master WORK.md only. The doctrine-consumer fold-set routing line of 2026-10-09 is still held with no card. Its fate is the steward's open item, not a bench question.

U10 | Whether the seventh window's hosted CI failure at `8d7dd999` (one `ProgramSettingsTests` case, green in the local hook and in key 2's run) reproduces, and whether it is environment-bound or order-dependent. The board's own record still owes a card after a reproduction. None ran in this window, and the stall's STALL line lists it among the released items with no card-ready outline.

U11 | Whether a subject assembled by carrying one lineage's reviewed production bytes, under new test lines from the other family, can meet P:code independent-key at all in a two-family seating. This window's one landing is such a subject: both families produced bytes of it, and every key on it, here or in the parent lineage, is of a producing family. It was not a kernel subject, so the clause was not exercised.

U12 | Whether the owner's 2026-10-29 research definition of done and its stop rule reach a factory design card. The cop withholds the routed design card on its own reading of that reach. The decision is not a docs/14 §0 entry, and no artifact this filing read records a question to the owner about it. It is an owner question, not a repo fact.

U13 | Why the design steward's 2026-10-23 19:50Z scheduled run held for 108 h, and who cleared it on 2026-10-28. No artifact records either: the held pass's receipt stops after its step 2, and the next pass found "no recorded cause".

## Instance map

KERNEL: DOGFOOD fleet-factory-kernel r5 · profile code@r10 + measured-objective@r3 · instance docs/KERNEL-INSTANCE-MAP.md · since 2026-10-02

The instance map is `docs/KERNEL-INSTANCE-MAP.md` on nested-repo master; this section points at it and keeps no table.
Its first line declares `kernel: fleet-factory-kernel r5 · profile: code@r10 + measured-objective@r3`, and the `KERNEL:`
line above copies its profiles byte for byte. The map was last changed by `db197676` (2026-10-02); no commit in this window
touches it.

REPORTED, not refreshed: the map's declared code revision (r10) is older than the fetched profile (r11). The map pins
`profiles/code.md` at blob `5511ccb3`, and the bus tip's blob is `a31b27a7`. Its kernel and measured-objective pins,
`6821c4c3` and `4e8bcacc`, still match. The two rows the seventh filing reported as overtaken stay overtaken. The K3 row
says the measured-objective input identity has "no production caller", but `tools/scoreboard.ps1` calls it. The K9 row
says the weekly resume drill's evidence folder is absent, but that folder now holds 6 drill receipts, 1 of them dated in
this window. This filing measures the window against r11 on the lines above. The map is never refreshed by this seat; its
K1-K12 rows belong to the card that wrote it. By its own rows, K3, K5, K6, K7, K8, K9, K10 and K11 are `NONE`, each with
its nearest partial mechanism.

## Counts

Clauses: 3 FIT · 1 FRICTION · 0 BREAK · 0 N/A · 5 UNEXERCISED · 3 INSTANCE-FAILURE
Profile: 1 FIT · 0 FRICTION · 0 BREAK · 0 N/A · 2 UNEXERCISED · 5 INSTANCE-FAILURE
Ledger totals (INSTANCE-FAILURE excluded per kernel §5): **4 FIT · 1 FRICTION · 0 BREAK · 0 N/A · 7 UNEXERCISED**

Moved against the seventh filing: K2 moved FIT → FRICTION (the held design-steward run, 108 h 4 min, escalated and
answered by no recorded owner act; REPLACES given). Every other clause and profile line keeps its verdict. Each line names
the seventh filing's verdict, and the seventh filing's lines stand whole in the carried section below.

The rest of this filing:
- a status line for each of the fifteen earlier numbered instance failures;
- answers to U7, U8, U9, U6, §a.u4, the independence-provenance bench, the stale-map route and the resource-terminals line;
- 7 Untested: U6, U8, U9 and U10 carried, and U11, U12 and U13 new.

## Carried: the seventh filing, undisposed

The seventh filing below is blob `27aeb99208a035d09e157936cc4f01b901f26e97` (`origin/review/dng-auto-processor-kernel-2026-10-23`, window
2026-10-15T02:00Z .. 2026-10-23T08:14Z). No steward disposition binds it yet. It is reproduced verbatim, each line
prefixed `> `, so every finding, answer, IF status and Untested item it filed keeps its original evidence reference until
the steward answers it (PROMPT K §6). Removing the `> ` prefix from each line yields that blob byte for byte. Where this
window's lines above disagree with a carried line, the carried line is the seventh window's evidence. It is not withdrawn,
and it is not this window's reading.

> project: dng-auto-processor
> kernel: fleet-factory-kernel r5
> profile: code@r11 (primary) + measured-objective@r3 — kernel §6's row as harvested (M1)
> instance: docs/KERNEL-INSTANCE-MAP.md on nested-repo master (written by card KERNEL-DOGFOOD-INSTANCE-MAP under docs/14 §0's kernel entry, landed `db197676`; KERNEL line DOGFOOD, ## Instance map). The map's own first line still declares code@r10 (## Instance map)
> subjects: 0 end-to-end under the kernel, and 0 declared inside this window — no `k5-declaration.json` was written after 2026-10-15T02:00Z (K5). Reported as mechanism evidence and never counted: 23 landings on this board's own two-key route, each with a committed receipt; none declared a profile. 0 PRODUCT commits landed off that route (## Subjects).
> window: 2026-10-15T02:00Z .. 2026-10-23T08:14Z (nested-repo master as it stood at the window's end)
> health: assurance=UNSATISFIED operability=PRESSURED
> providers: none (no lane cleared a sentinel for this filing)
> posture: not computed — model review contributed (the route's approach reviews and keys), and the R9 tool is one PROMPT K names, which docs/13 P-STEWARD step 7e forbids the filing seat to run (U6, ROUTED; unchanged)
> 
> Seventh filing by this board. It is a re-run on PROMPT K §6's weekly cadence: the kernel (r5), `profiles/code.md` (r11) and
> `profiles/measured-objective.md` (r3) are unchanged since the sixth filing, and the `KERNEL:` line below is byte-identical
> to the sixth filing's. The sixth filing (blob `cce576ba`) was harvested on 2026-10-16: `dng-auto-processor.dispositions.md`
> carries `filing_blob: cce576ba99229229d9dda4b2203154069703bdac` and answers it (46 `§` lines: 38 ADOPTED, 1
> ADOPTED-CONDITIONAL, 0 REJECTED, 7 ROUTED; plus 10 `HEADER:` lines: 8 ADOPTED, 2 ROUTED), so no finding of the sixth
> filing is carried forward undisposed. Its open routes (U7 conditional; U8, independence-provenance, §a.u4 and U6; U9; the
> stale instance map) are re-answered below on this window's evidence, and every clause and profile line is re-measured
> against r5, r11 and r3. The seat that writes it is `dng-design-steward`. It works from this board's own cards, receipts
> and ledgers, and it ran no subject.
> 
> `assurance=UNSATISFIED`: no subject was declared or accepted under the kernel, and the product's own bar produced no
> acceptance either — WORK.md's SCOREBOARD has no line inside the window (its newest is still `20260918-1356`).
> `operability=PRESSURED`: 302 dispatches for 23 receipted landings (about 13 per landing against about 10 in the last
> window), summed over the cop's nine daily-ledger lines dated 2026-10-15 to 2026-10-23 in WORK.md (140 ticks; the 10-15
> line also covers the two hours before the window opened). The ledger's landed sum (23) now matches the 23 receipts day
> by day. Every daily line reads `ci=success` as it stands at the window's end, and that is again not the whole CI story:
> master's hosted CI was red on one test after one landing (P:code delivery-target; the ledger read `ci=failure` at
> 2026-10-18 04:38Z and was rewritten in place, K11). Ten cop-tick commit subjects in the window mention a STALL (§7 alarm 1
> or §3); one daily line's STALL note names a card of the parked lineage this filing counts and does not describe. Three account rotations fall in the window
> (K9). The design steward seat, which keeps this filing and the docs, began 35 passes inside the window; of the 34 that
> ended, 27 ended ACTED, 3 NO-WORK-DEFERRED-ON-LOAD and 4 NO-WORK (the 35th is the pass writing this filing). 14 commits in
> the window touch only docs, packets or WORK.md (11 of their subjects name the steward).
> 
> Unqualified paths and commit ids are this board's repository. Evidence kept outside it is named by description, never by
> path, as before (bus law 4). Doctrine paths are qualified. Three cards of one lineage are PARKED at the window's end with
> review in flight; this filing counts them and does not describe them, and none of the window's 23 landings was opened
> from that lineage. Every landing below is named. The sixth filing's one aggregate-only landing is released here, because
> its lineage left flight: it is RAMP-SAMPLER-REAL-DCRAW-APPLY-WITNESS attempt 1 (`8c92296e`, landed 2026-10-13T03:47:30Z,
> one test file, claude-sonnet-5-5 → gpt-5.6-sol / claude-opus-5-5, approach review gpt-6-astra REVISE 0/2/1 with 2
> confirmed), opened from RAMP-CLIP-EXPOSURE-SINK-K-PASS, which closed MEASURED-NEGATIVE on 2026-10-20
> (`packets/RAMP-CLIP-EXPOSURE-SINK-K-PASS.md`).
> 
> ## Subjects
> 
> **Kernel subjects: none.** No rule, tool or hook reads `k5-declaration.json` (IF13), and none orders one written. In this
> window nobody wrote one (IF15): a case-insensitive file-name search of the evidence ledgers for `k5-decl*` returns 4
> files in all, none modified after the window opened. No landing receipt and no card changed in the window names a kernel
> or profile revision.
> 
> **Landings on this board's own route, reported and never counted.** Each has a receipt at
> `metrics/ratify/<TASK>/<attempt>/receipt.json` on master, and each landed by `git merge --ff-only` of an exact sha onto
> nested-repo master. "Keys' subject" is the receipt's `keysSubjectSha`. The last column is the receipt's
> `rangeEnum.surplusProduct` (PRODUCT paths, docs/14 §4's closed set, the delivered range carries beyond the keys'
> subject). "Assembly" is the feature assembly the landed range changes beyond tests and tooling. Author → key 1 / key 2
> names the implementing author(s).
> 
> | Task / attempt | Keys' subject → landed (tree same?) | Assembly | Author → key 1 / key 2 | Surplus PRODUCT |
> |---|---|---|---|---|
> | RATIFY-RECEIPTS-461BF565-DISPOSITION / 1 | 54188672 → 54188672 (yes) | none (one receipt file, inert) | gpt-5.6-sol → claude-fable-5-1 / claude-opus-5-5 | 0 |
> | RAMP-GATE-DECISION-READ-ONCE / 1 | 5be91a30 → 5be91a30 (yes) | Core (`AutoProcessor.cs`) | gpt-5.6-sol → claude-fable-5-1 / claude-opus-5-5 | 0 |
> | MANIFEST-RECEIPT-ENVELOPE-OMISSION-WITNESS / 1 | 64a4b523 → 64a4b523 (yes) | tests only | claude-sonnet-5-5 → gpt-5.6-sol / claude-opus-5-5 | 0 |
> | HOOK-GOVERNING-DOCS-NO-BUILD / 2 | 10ea8005 → 8fbec461 (no: inert rebase) | none (hook, tools) | gpt-5.6-sol, then gpt-6-astra → claude-fable-5-1 / claude-opus-5-5 (round 1 key 2 REVISE) | 0 |
> | BUILD-PROFILE-EXCLUDE-PROJECT-BLANK-VALUE / 1 | e40eff8a → e40eff8a (yes) | CorpusBridge | claude-sonnet-5-5 → gpt-6.1-sol / claude-opus-5-5 | 0 |
> | UNUSED-ANCHOR-GAP-CULTURE-ROUNDING / 1 | c4cf4f0d → c4cf4f0d (yes) | Core (`AutoProcessor.cs`) | gpt-6.1-sol → claude-fable-5-1 / claude-opus-5-5 | 0 |
> | FACTORY-D2-RULE-CHECKS-BATCH-PASS / 1 | addeb29a → addeb29a (yes) | none (tools, hook, CI) | claude-sonnet-5-5 → gpt-6.1-sol / claude-opus-5-5 | 0 |
> | ELTB-2-OL-AT-INGEST / 2 | ab5aa3bd → ab5aa3bd (yes) | Core | claude-sonnet-5-5, then claude-fable-5-1 → gpt-6.1-sol / claude-opus-5-5 (round 1 key 1 BLOCKER, confirmed) | 0 |
> | ELTB-1-BISECTION-SOLVER / 1 | 8ac09879 → 3b27141b (no: rebased over ELTB-2's PRODUCT commit, disjoint paths) | Core | gpt-6.1-sol → claude-fable-5-1 / claude-opus-5-5 | 0 |
> | RCB2-1-CONTROL-BYTES-CHECK / 1 | 2f6a783d → 2f6a783d (yes) | none (tools) | gpt-6.1-sol → claude-fable-5-1 / claude-opus-5-5 | 0 |
> | ELTB-3-CONDITIONAL-TARGET-FIT / 3 | 8d7dd999 → 8d7dd999 (yes) | Core | claude-sonnet-5-5, then claude-fable-5-1 → gpt-6.1-sol / claude-opus-5-5 | 0 |
> | RCB2-2-PRE-RESET-SCRIPTS-CHECK / 3 | d0533525 → d0533525 (yes) | none (tools) | claude-sonnet-5-5, then claude-fable-5-1 → gpt-6.1-sol / claude-opus-5-5 | 0 |
> | ELTB-4-FLAG-WIRING / 1 | 8e265798 → 8e265798 (yes) | Core | claude-sonnet-5-5 → gpt-6.1-sol / claude-opus-5-5 | 0 |
> | LEARN-PROJECT-DCRAW-SCRATCH-CLEANUP-FLAKE / 3 | 68487e6d → 68487e6d (yes) | tests only | claude-fable-5-1 → gpt-6.1-sol / claude-opus-5-5 | 0 |
> | RCB2-3-HOOK-CI-RULE-MAP / 1 | 5696b754 → 5696b754 (yes) | none (hook, CI) | gpt-6.1-sol → claude-fable-5-1 / claude-opus-5-5 | 0 |
> | LEARNED-TARGET-OL-BACKFILL / 2 | f2ad578d → f2ad578d (yes) | Core, CorpusBridge | claude-sonnet-5-5, then claude-fable-5-1 → gpt-6.1-sol / claude-opus-5-5 | 0 |
> | CORPUS-EVIDENCE-COMMIT-20261019 / 1 | 0b90e416 → 0b90e416 (yes) | none (corpus evidence, inert) | claude-sonnet-5-5 → gpt-6.1-sol / claude-opus-5-5 | 0 |
> | SESSION-CHECKPOINT-PIN-20261019 / 1 | da363373 → da363373 (yes) | none (tools, factory pins) | claude-sonnet-5-5 → gpt-6.1-sol / claude-opus-5-5 | 0 |
> | SINK-ANCHOR-RECEIPT-UNCHECKED-ROUTES-WITNESS / 2 | 41193830 → 41193830 (yes) | tests only | gpt-6.1-sol, then gpt-6-astra → claude-fable-5-1 / claude-opus-5-5 (round 1 key 2 REVISE) | 0 |
> | APP-ADD-FINISHED-PROJECT-ZERO-CLIP-INCOMPLETE-SCAN / 1 | 970e9b69 → c677cb9a (no: inert rebase) | App | gpt-6.1-sol → claude-fable-5-1 / claude-opus-5-5 | 0 |
> | LEARNED-TARGET-OL-TRACE-ORACLE-BATCH-PASS / 1 | 0a901382 → 1d580153 (no: rebased over APP-ADD-FINISHED's PRODUCT commit, disjoint paths) | Core, CorpusBridge | claude-sonnet-5-5 → gpt-6.1-sol / claude-opus-5-5 | 0 |
> | LEARNED-TARGET-OL-BACKFILL-DATA-2A-APPLY / 1 | b87b5d28 → b87b5d28 (yes) | Core | gpt-6.1-sol → claude-fable-5-1 / claude-opus-5-5 | 0 |
> | LEARNED-TARGET-OL-BACKFILL-DATA-2B-DATA / 1 | 93930cee → 93930cee (yes) | Core (one pin), `profiles/` data | gpt-6.1-sol → claude-fable-5-1 / claude-opus-5-5 | 0 |
> 
> 19 of 23 landings have `keysSubjectSha` equal to `landedSha`. The other 4 were rebased after their keys: 2 over inert
> bookkeeping only (HOOK-GOVERNING-DOCS-NO-BUILD, APP-ADD-FINISHED-PROJECT-ZERO-CLIP-INCOMPLETE-SCAN) and 2 over another
> landing's PRODUCT commit that shares no path with the subject (ELTB-1 over `ab5aa3bd`, TRACE-ORACLE over `c677cb9a`),
> which docs/14 §4's narrowed void test permits; each records blob identity and `patch-id --stable` unchanged and a green
> hook re-run on the delivered sha. 16 landed at attempt 1, 4 at attempt 2 and 3 at attempt 3. A 24th receipt file added in
> the window, `metrics/ratify/8c9ca32/receipt.json`, is not a landing of this window: it is the September receipt of an
> earlier landing, committed by RATIFY-RECEIPTS-461BF565-DISPOSITION on a recorded USER disposition. Re-derive the file
> count with `git -C <repo> log --since=2026-10-15T02:00Z --until=2026-10-23T08:14Z --diff-filter=A --name-only --format= master --
> 'metrics/ratify/*/receipt.json' | grep -c .` (24).
> 
> **Off-route landings: none.** The window's master history is 124 commits, all first-parent. 32 touch a PRODUCT path, and
> every one lies inside the delivered range of one of the 21 landings above that touch PRODUCT. The other 92 are 76 cop
> bookkeeping commits, 14 commits touching only docs, packets or WORK.md, and the two inert-only landings
> (CORPUS-EVIDENCE-COMMIT-20261019, RATIFY-RECEIPTS-461BF565-DISPOSITION).
> 
> ## Answers to the benches the last harvest routed
> 
> - **U7 (ADOPTED-CONDITIONAL, dng outcome-reporting bench), the O2 denominator across a sixth window: 12 of 23.** Same
>   predicate: landings whose delivered range touches a feature assembly — every `DngAutoProcessor.*/` directory holding a
>   `.csproj`, minus `*.Tests` (Core, App, CorpusBridge). The 12 are the rows above whose Assembly cell names one. The 11
>   that touch none change tests only (3), factory tooling, hook or CI (6), or inert data (2). The earlier windows read 4
>   of 11, 6 of 14, 3 of 11, 7 of 15 and 12 of 17, each within its own receipted population. Assembly contact is not proof
>   of a changed emitted grade (the dispositions' condition), and this filing does not claim it.
> - **U8 (ROUTED, dng measured-objective outcome bench), the emitted-grade effect: partly derived, one more window.** Of
>   the 12 assembly landings, 8 belong to one owner-decided lever, the learned exposure target (ELTB-1 to ELTB-4,
>   LEARNED-TARGET-OL-BACKFILL, TRACE-ORACLE, and BACKFILL-DATA-2A and 2B). Its switch, `EngineConfig.LearnedExposureTarget`,
>   defaults to false (`DngAutoProcessor.Core/Models/RulesEngine.cs:627`), and its flag-off behaviour is witnessed by a
>   landed test file, `DngAutoProcessor.Tests/LearnedExposureTargetFlagOffIdentityTests.cs` (ELTB-4 and 2A-APPLY), which
>   the receipts describe as byte identity of the sampler sequence, XMP bytes and effective-config bytes with the flag off.
>   ELTB-4's receipt states the default flip is the USER's. BACKFILL-DATA-2B adds data to the committed house-style profile
>   and teaching store under `profiles/` that is read only when the flag is on. Of the other 4: an emit-decision change
>   (`5be91a30`) whose receipt states it is identical when the configuration does not change during a run; a warning-text
>   format (`c4cf4f0d`); a CorpusBridge refusal of a blank argument (`e40eff8a`); and an App refusal message
>   (`c677cb9a`). None of these four is a grade computation on its face. Still not derived: whether the owner's saved engine
>   sets `LearnedExposureTarget` or `PropagateManualGrades` (the latter has no initialiser, `RulesEngine.cs:203`, so its
>   class default is false; a saved engine's own value governs and was not read). No SCOREBOARD line in the window measures
>   an emitted grade.
> - **Independence-provenance bench (ROUTED; P:code independent-key): the contribution records, for this window.** On all
>   23 landings key 1 is from the provider opposite the author's (11 Codex-authored landings take `claude-fable-5-1`; 12
>   Claude-authored take `gpt-6.1-sol`, or `gpt-5.6-sol` on MANIFEST-RECEIPT), and key 2 is `claude-opus-5-5` (three
>   receipts record it by the alias `opus`). On 10 landings the approach reviewer and key 1 are the same model: 9
>   Codex-authored with `claude-fable-5-1` in both seats (RATIFY-RECEIPTS, RAMP-GATE, HOOK-GOVERNING-DOCS, UNUSED-ANCHOR,
>   RCB2-1, RCB2-3, SINK-ANCHOR, APP-ADD-FINISHED, BACKFILL-DATA-2B) and 1 Claude-authored with `gpt-6.1-sol` in both
>   (CORPUS-EVIDENCE). On the other 13 they are different models of one provider: 2 Codex-authored with an
>   Opus approach review (ELTB-1 records `claude-opus-5-5`, BACKFILL-DATA-2A the alias `opus`) and 11 Claude-authored with a `gpt-6-astra` approach
>   review. So on 23 of 23 landings key 1's provider also reviewed the approach the author then implemented (11 of 11 in
>   the last window). Each receipt's approach-review verdict and counts are in its `seats` record. One more observation
>   from the same receipts bears on the bench without deciding it: on 5 landings key 1's final-round verdict was not
>   ACCEPT and the subject landed after its findings were re-graded — ELTB-3 (a BLOCKER refuted to MINOR by the cop's
>   paired-mutation probe), ELTB-4 (a MAJOR refuted to MINOR by key 2's serialization mutant), LEARN-PROJECT-DCRAW (a MAJOR
>   refuted to MINOR by measurement under load), LEARNED-TARGET-OL-BACKFILL round 2 (2 MAJOR refuted to MINOR) and
>   FACTORY-D2 (one confirmed MAJOR with its severity dropped, `verdictRederived` ACCEPT). Where a receipt names the re-grading seat it is the cop or key 2 (FACTORY-D2's records `verdictRederived` and names none), and no receipt records the author re-grading. Whether the approach-review class makes key 1's provider a producer of the subject is not
>   decided here, and provider overlap alone does not decide it (the dispositions' words).
> - **§a.u4 (ROUTED, delivered-pipeline delayed-outcome fixture): none to bring.** This board accepted no subject under the
>   kernel, and no SCOREBOARD line falls in the window.
> - **U6 (ROUTED, authorised posture-computation seat): unchanged.** No register-authorised seat computed R9 for this
>   filing, and no owner word authorising one is recorded in docs/14 §0.
> - **U9 (ROUTED, dng doctrine-consumer stewardship): unchanged.** WORK.md item 3 still holds the 2026-10-09 doctrine-consumer
>   fold-set routing line as unopened and not the cop's to open (docs/13 P-COP bars a tick from editing docs/12-14); no
>   card and no docs commit in the window acts on it.
> - **Stale instance map (HEADER, ROUTED to its authorised maintainer): unchanged, and two more of its rows are overtaken**
>   (## Instance map).
> - **P:code resource-terminals (ADOPTED as an INSTANCE-FAILURE): not exercised this window**, reported on that line.
> 
> ## Clauses
> 
> K1 | UNEXERCISED | "A candidate is never accepted on evidence whose only author is its producer" | No kernel subject existed. Reported without credit: all 23 route receipts name an author whose model is neither key's, and no PRODUCT commit landed off the route. Five landings proceeded over a key 1 non-ACCEPT whose findings the cop or key 2 re-graded (independence-provenance bench above); no author re-graded a finding against its own subject | PROOF: a kernel subject accepted here on receipts naming one actor for production and acceptance
> 
> K2 | FIT | "Everything unlisted is autonomous. Escalation goes to the owner for decisions reserved by that register" | Register: docs/14 §0 (USER rulings verbatim) plus WORK.md RULES rule 3. Taken without asking because the register allowed it: 23 route landings, none needing an owner act at landing. Reserved decisions went to the owner and were recorded as his: the learned-exposure-target adoption is routed as "USER-decided" (WORK.md 2026-10-17 13:20Z) and its flag ships false with the flip named the USER's (ELTB-4 receipt); the corpus-evidence commit and the session-checkpoint pin were opened on USER selections recorded in a P-RESUME receipt (WORK.md 2026-10-19 18:10Z and 2026-10-20 00:12Z); after the 2026-10-19 rotation a stranded scheduled task was re-created only on the USER's answer, never by a seat on its own (K9). Escalations went where the register sends them: 8 OWNER-DEFECT lines dated in the window and one undated one a cop tick appended in it, each naming its artifact, and none of the window's 76 cop-tick commits touches docs/12, docs/13 or docs/14 | PROOF: an owner-reserved act taken here with no §0 entry authorising it
> 
> K3 | FIT | "under a claim an observer other than the claimant can decide stale and release; an expiring lease is one such mechanism" | Mechanism unchanged: the card's owner line plus a launch json written before the launch (docs/14 §3), with staleness decided from outside the seat by §3's liveness rule. Exercised in this window: 5 receipts record a seat the cop decided FROZEN and whose claim it released — a key 1 relaunched after its first launch sat 4 h 27 min without a first act (ELTB-1), two implement seats relaunched whole (ELTB-3 attempt 2, LEARNED-TARGET-OL-BACKFILL attempt 1), and two committers that froze after a green commit whose `binding.json` the cop then wrote from git (UNUSED-ANCHOR-GAP-CULTURE-ROUNDING, HOOK-GOVERNING-DOCS-NO-BUILD). The instance map's K3 row is still NONE for an identity held by one claimant at a time with an atomic claim | PROOF: a claim here still held after its seat was dead, with no observer able to release it
> 
> K4 | FIT | "Work is complete only on positive evidence it was asked to produce" | A round-1 key 1 BLOCKER confirmed on a decode-count baseline written as a formula rather than measured stopped ELTB-2 until attempt 2 measured it; RCB2-2 took three rounds (3, then 2 confirmed MAJOR) before both keys accepted; three measurement cards closed MEASURED-NEGATIVE rather than DONE (`packets/LEARNED-TARGET-OL-BACKFILL-DATA.md`, `packets/LEARNED-TARGET-OL-MATCHED-ESTIMATOR-DIAGNOSTIC.md`, `packets/RAMP-CLIP-EXPOSURE-SINK-K-PASS.md`); the flake card replaced a reproduction gate too weak to fail with deterministic lock witnesses before it landed (`packets/LEARN-PROJECT-DCRAW-SCRATCH-CLEANUP-FLAKE.md`); and a hosted CI test failure was recorded as "a finding, never load: a card after a reproduction" (WORK.md QUEUE 5). Counter-observation, kept here rather than credited: TRACE-ORACLE's receipt records key 1 ACCEPT 0/0/0 "thin: no line evidence", and the landing rested on key 2's 28 build-fresh mutants | PROOF: a card here closed DONE on a return code or a file's presence alone
> 
> K5 | UNEXERCISED | "Before work starts, a subject declares its profile and profile version." | 0 `k5-declaration.json` dated inside the window (IF15), and no landing receipt records a profile: 0 of the 23 receipts, and 0 of the cards changed in the window, name `code@r`, `measured-objective@r` or the kernel. The sweep that supports this negative: case-insensitive file-name search of the evidence ledgers for `k5-decl*` (4 in all, none modified after 2026-10-15T02:00Z) | PROOF: a subject accepted here whose acceptance receipt names a different identity or profile than its declaration
> 
> K6 | UNEXERCISED | "Every acceptance includes a key from an independence class other than the producer's." | No kernel subject was accepted. Reported without credit: 23 of 23 route landings carry a key 1 from the provider opposite the author's, and key 2 is `claude-opus-5-5` on all 23. The independence-provenance records are above | PROOF: an accepted subject here whose keys and producer share one provider
> 
> K7 | UNEXERCISED | "Acceptance and delivery are separate states." | Nothing was accepted under the kernel. Reported without credit: all 23 route landings reached nested-repo master by `--ff-only` of an exact sha, and all 23 receipts record the mirror sync (19 in a `mirror` field, 4 inside the `landing` text, each of the latter naming product byte identity). No typed `CLOSURE_INCOMPLETE` exists here (IF9). Hosted CI after one landing's sync was red (P:code delivery-target) | PROOF: an accepted subject here that never landed and that the next tick names unprompted
> 
> K8 | UNEXERCISED | "Reset events update capacity telemetry. They never open a gate by themselves." | Mechanism unchanged (docs/14 §2, "on EVIDENCE, never off the window"). In-window: on 2026-10-19 the last fires on the departing account of three scheduled tasks — the cop, the steward and one USER-owned task — each ended at once on a weekly usage limit whose reset the error dated three days later (recorded in the 2026-10-19 P-RESUME receipt); the seats ran again on the new account after the rotation, not on a reset; and no key seat failed over on capacity (P:code resource-terminals). No artifact this filing read records a quota reset as such, the observable's trigger | PROOF: a reset event here that by itself re-opened a darkened seat
> 
> K9 | INSTANCE-FAILURE | "A fresh session on a new account, with empty memory, resumes from the project's tree and the bus alone." | Exercised three times in this window, and the adopted failure recurred. Three account rotations are recorded, each by a P-RESUME receipt (2026-10-15 20:28Z, 2026-10-19 09:06Z and 2026-10-23 03:29Z; P-RESUME runs on the owner's "resume our work"). After each, the cop and the steward ran again on the new account by catch-up fire, and one scheduled task registered on the departing account was absent on the new one: on 10-15 and again on 10-23 the status-digest task, listed and not re-created; on 10-19 the usage-watch task, which the pass put to the USER and re-created only on the USER's answer. So a rotation still needs an owner step for the register's full seat set to run again. 0 lines added to docs/13 or docs/14 in the window mention P-RESUME, re-registration or inventory | no replacement | PROOF: a rotation here after which every scheduled seat the register authorises ran again with no owner step
> 
> K10 | INSTANCE-FAILURE | "Provider and model inventory is machine-scoped and probe-derived, and it records the account it was derived under." | Unchanged: no machine-readable inventory and no `probed_under` in the repo (the instance map's K10 row); the three rotations' account identity is recorded only outside the repo, in the P-RESUME receipts (SessionStart hook output, the scheduled-task partition each pass derived, and on 2026-10-23 a `claude auth status` re-check) | no replacement | PROOF: an in-repo inventory whose `probed_under` names the current account
> 
> K11 | INSTANCE-FAILURE | "R1–R5, R7, R8 and R9 apply to every report a factory makes about itself" | Unchanged: the two CLOSED lines `131ad1f2` appended (WORK.md, dated 2026-09-23 14:05Z) still stand with no correction line beside them, and the seat that found it may append nothing there but a CLOSED line (docs/13 P-STEWARD). Recurrence of the reporting-history observation the dispositions recorded: the 2026-10-18 daily-ledger line read `ci=failure` at 04:38Z and `ci=in_progress` at 09:55Z, and at the window's end it reads `ci=success`, so the ledger keeps no trace of the red interval; the board's WORK.md history and the cop's commit subjects keep it. This filing takes no credit for 23 route landings and asserts no posture it did not compute | no replacement | PROOF: a correction line beside that CLOSED line in the board's ledger
> 
> K12 | FIT | "The steward harvests every filing and answers each one." | The sixth filing (blob `cce576ba`) was harvested on 2026-10-16 (harvest `20261016T090409Z-078e6f76`): `dng-auto-processor.dispositions.md` carries its blob and answers every `§` line and header line, and `HARVESTS.md` carries its row (FIT 3 · FRICTION 0 · BREAK 0 · N/A 0 · UNEXERCISED 9). This re-file is the clause's other half. FENCE: the filing seat may not run `tools/harvest-status.py`, so the harvested state is read from the artifacts that tool reads | PROOF: a finding of the sixth filing with no disposition line
> 
> ## Profile lines
> 
> P:code subject-identity | INSTANCE-FAILURE | "its identity is K3's `sha256` of that OID's lowercase hexadecimal text, with no trailing newline" | Held in the window: 0 PRODUCT paths beyond the keys' subject on 23 of 23 landings, and 19 of 23 delivered the very commit the keys reviewed. Not held: on the other 4 the delivered tree differs from the reviewed tree (2 by inert bookkeeping, 2 by another landing's disjoint PRODUCT commit), and the binding the receipt records is per-file blob identity plus `patch-id`, never a tree OID; and 0 of the 23 receipts record a tree OID or its K3 `sha256`, reviewed or delivered (a search of the receipts for a tree field finds none). The measured-objective half moved: `tools/scoreboard.ps1` now dot-sources `tools/scoreboard-input-identity.ps1` and hashes the eval set, store and base engine per clip (lines 99 and 121, landed in FACTORY-D2-RULE-CHECKS-BATCH-PASS's range), but no scoreboard run in the window exercised it | no replacement | PROOF: a receipt here recording each subject's tree OID and K3 digest, reviewed and delivered alike
> 
> P:code claims | FIT | "observer-released claims may replace leases" | The observer-release path was exercised 5 times in the window (K3): in each the cop, not the claimant, decided the seat frozen and released or re-dispatched its claim, and the card's attempt ledger records it. The longest interval between a seat's launch and its observer release was 4 h 27 min (ELTB-1's first key 1, which never made a first act) | PROOF: a claim here released by its own claimant's say-so, or held after its seat died with no observer able to release it
> 
> P:code claims-audit | INSTANCE-FAILURE | "Audit canonical state before and after: HEAD, index entries and flags, refs, reflogs, stash, tracked contents, and ignored/untracked path inventories" | Unchanged: for a mutation-capable key 2 (every key 2 here builds and runs the suite or a mutant battery), §10 step 6 records the SCRATCH worktree's removal, never the main checkout's state before and after; 0 of the 23 receipts mention a reflog or stash, and no line added to docs/14 in the window mentions either | no replacement | PROOF: a key-2 run here whose receipt records the main checkout's HEAD, index entries and flags, refs, reflogs, stash, tracked contents and ignored/untracked path inventories with content hashes, before and after
> 
> P:code independent-key | UNEXERCISED | "a verifier from another model family (R3) whose class has not become a producer of the subject" | No kernel subject was accepted. The contribution records the bench asked for are above: on 23 of 23 landings key 1's provider also reviewed the approach, on 10 of them in the very model that then held key 1 | PROOF: a subject here whose only other-provider key comes from a class that also wrote its product bytes
> 
> P:code resource-terminals | INSTANCE-FAILURE | "Before dispatch, declare any register-permitted substitution for a family-bound quorum seat" | The latent gap stands in the rule: docs/14 §2 orders a SINGLE-FAMILY round's `cross_family: UNAVAILABLE <provider> <UTC ISO>` label into "its receipt", written at landing, and no rule orders the substitution declared before dispatch; no line added to docs/14 in the window touches it. Not exercised this window: of 368 `launch*.json` files modified inside the window (searched to depth 4 of the evidence ledgers), 0 carry a cross-family label, and the one that names a failover is a same-family whole relaunch whose record says both families answered the tick's probe | no replacement | PROOF: a rule here that orders every substituted seat's declaration written before its dispatch, and a window in which each substituted seat's launch record carries it
> 
> P:code delivery-target | INSTANCE-FAILURE | "build the exact proposed record and run the validators and hooks that commit will face before any product push; refuse on failure" | Half repaired, and exercised. The sixth filing's gap was the build flags: docs/14 §4 now orders that "The build a landing must pass is CI's, not the hook's" — the landing runs the `Release build` step of `.github/workflows/factory-ci.yml` as it reads at the landed sha (steward commit `d237e8ec`, 2026-10-16T02:24Z, closing the cop's OWNER-DEFECT of 2026-10-14). All 20 landings after that commit record that run (19 in a `ciReleaseBuild` field, HOOK-GOVERNING-DOCS in its landing text); the 3 before it record none. What still stands: the hook's own build line still carries no `--warnaserror` (0 occurrences in `.githooks/pre-commit`; docs/14 calls aligning it "a card", and none is open); the landing runs CI's build step and the hook's filtered suite, not CI's other steps; and a hosted validator still failed after a landing. Master's CI run at `8d7dd999` (ELTB-3, landed 2026-10-18T03:13:25Z, the hook 3513/3513 on the pre-rebase subject, key 2 3513/3513 on 8d7dd999) failed 1 of 3513 on one `ProgramSettingsTests` case; the cop recorded it as a finding owed a card after a reproduction, and at the window's end no card is open for it. The ledger read `ci=failure` at 04:38Z and `ci=success` at `5696b754` by 14:30Z | no replacement | PROOF: a landing here whose hosted validators ran green before its mirror push
> 
> P:code dispatch-preflight | INSTANCE-FAILURE | "the spending tool runs the project's resume gate before dispatch and retains its result, the inventory snapshot and digest, and account-parity evidence" | Unchanged: docs/13 P-COP orders no resume-gate, inventory or parity read before dispatch, and no line added to docs/13 or docs/14 in the window adds one, so none of the window's 302 dispatches is ordered to retain them. The three rotations' parity evidence was read by the USER-started P-RESUME passes, not by the spending tool; this filing did not read every tick note for a seat that retained them unordered — the K10 gap | no replacement | PROOF: a tick receipt here that retains a resume-gate result, an inventory digest and parity evidence before its first dispatch
> 
> P:measured-objective acceptance-evidence | UNEXERCISED | "the declared scorer on a held-out fold the producer never tuned on" | No SCOREBOARD line falls inside the window (its newest is `20260918-1356`), so no candidate was scored by the declared scorer. The window's one new grade lever, the learned exposure target, landed behind a flag that ships false on a recorded owner decision; its fitting step uses nested leave-one-group-out inside the build (ELTB-3), and the window's measurement cards on it measured parity of a computation or closed MEASURED-NEGATIVE — neither is held-out acceptance of a candidate on the declared scorer | PROOF: a scored run in the window that this line missed
> 
> ## Instance failures
> 
> Status of the earlier fifteen:
> - **IF1, IF11**: historical, unchanged.
> - **IF2: repaired in the latent script**; `tools/ratify.ps1` is still off the live landing path (0 of 23 window receipts land through it). One landing's range edited it (FACTORY-D2-RULE-CHECKS-BATCH-PASS, a launch-effort site).
> - **IF3, IF4, IF10: LATENT**, as before.
> - **IF5: repaired in the latent script**; no gate0 ran on the live route (0 of 23 receipts record one; ELTB-4 records why no scoreboard run was owed).
> - **IF6: LIVE.** WORK.md:4 still reads "Merge: tools/ratify.ps1 (gate 0 + cross-family key + adversarial Claude key)".
> - **IF7**: resolved at an earlier read, and outside git.
> - **IF8: unchanged.** `tools/claude-review-capture.ps1` and `tools/codex-author-capture.ps1` are both still absent from master.
> - **IF9: unchanged.** No file outside the instance map names `CLOSURE_INCOMPLETE`.
> - **IF12: drift continues.** The window's 23 receipts use seven combinations of three encodings: `seats` as a role-tagged list (13), an object (8) or an object of strings (2); `rounds` as a prose string (8), a list (7), an object (4) or absent (4); the mirror record in a `mirror` field (19) or the `landing` text (4). A new `ciReleaseBuild` field appears on 19.
> - **IF13: unchanged.** No rule, tool or hook names `k5-declaration` (a `git grep` of master's docs, tools, .githooks and scripts finds only the instance map); outside them, only two cards, both closed before the window opened, name it.
> - **IF14: resolved**, as before; what hosted CI finds is P:code delivery-target, which this window exercised.
> - **IF15: unchanged for this window.** 0 declarations dated inside it.
> 
> ## Untested
> 
> U6 | The `posture:` line (ROUTED, unchanged). The same limit applies to `tools/harvest-status.py`.
> 
> U8 | Whether any of the 12 assembly landings changed the grade the owner's saved engine emits: in particular whether that engine sets `LearnedExposureTarget` or `PropagateManualGrades`. The class defaults are derived above; the saved engine was not read.
> 
> U9 | Not tested here; read from master WORK.md only: the doctrine-consumer fold-set routing line of 2026-10-09 is still held in item 3 with no card. Its fate is the steward's open item, not a bench question.
> 
> U10 | Whether the hosted CI failure at `8d7dd999` (one `ProgramSettingsTests` case, green in the local hook and key 2's run) reproduces, and whether it is environment-bound or order-dependent. The board's own record owes a card after a reproduction; none ran in the window.
> 
> ## Instance map
> 
> KERNEL: DOGFOOD fleet-factory-kernel r5 · profile code@r10 + measured-objective@r3 · instance docs/KERNEL-INSTANCE-MAP.md · since 2026-10-02
> 
> The instance map is `docs/KERNEL-INSTANCE-MAP.md` on nested-repo master; this section points at it and keeps no table.
> Its first line declares `kernel: fleet-factory-kernel r5 · profile: code@r10 + measured-objective@r3`, and the `KERNEL:`
> line above copies its profiles byte for byte. REPORTED, not refreshed: the map's declared code revision (r10) is older
> than the fetched profile (r11); the map pins `profiles/code.md` at blob `5511ccb3`, and the bus tip's blob is `a31b27a7`
> (its kernel and measured-objective pins, `6821c4c3` and `4e8bcacc`, still match). Two of its rows are now overtaken by
> this board's own artifacts, also REPORTED, not refreshed: the K3 row says the measured-objective input identity has "no
> production caller", and `tools/scoreboard.ps1` now calls it (P:code subject-identity); the K9 row says the weekly resume
> drill's evidence folder is absent, and that folder now holds 5 drill receipts, 3 of them dated in this window. This filing
> measures the window against r11 on the lines above. The map is never refreshed by this seat; its K1-K12 rows belong to the
> card that wrote it. By its own rows, K3, K5, K6, K7, K8, K9, K10 and K11 are `NONE`, each with its nearest partial
> mechanism.
> 
> ## Counts
> 
> Clauses: 4 FIT · 0 FRICTION · 0 BREAK · 0 N/A · 5 UNEXERCISED · 3 INSTANCE-FAILURE
> Profile: 1 FIT · 0 FRICTION · 0 BREAK · 0 N/A · 2 UNEXERCISED · 5 INSTANCE-FAILURE
> Ledger totals (INSTANCE-FAILURE excluded per kernel §5): **5 FIT · 0 FRICTION · 0 BREAK · 0 N/A · 7 UNEXERCISED**
> Moved against the sixth filing: K3 and P:code claims UNEXERCISED → FIT (an observer-release exercise this window).
> Plus a status line for each of the fifteen earlier numbered instance failures (no new IF number; this window's
> INSTANCE-FAILURE lines are the K and P lines above), answers to U7, U8, U9, U6, §a.u4, the independence-provenance bench,
> the stale-map route and the resource-terminals line, and 4 Untested.
