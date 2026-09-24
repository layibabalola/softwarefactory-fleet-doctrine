project: dng-auto-processor
kernel: fleet-factory-kernel r5
profile: code@r9 (primary) + measured-objective@r3 — kernel §6's row as harvested (M1)
instance: DngAutoProcessor/docs/14-ORCHESTRATION.md (instance map below; KERNEL line DOGFOOD-PENDING — docs/12, 13 and 14 are steward-only under docs/14 §7a, no docs/14 §0 entry records a kernel adoption, and the seat that files this may not write the instance map)
subjects: 0 end-to-end under the kernel, and 0 declared in this window — the three `k5-declaration.json` files on disk all predate it (the newest, RAMP-BASE-COORDINATE-FIX, 2026-09-19T06:56:28Z). Reported as mechanism evidence and never counted: 15 landings on this board's own two-key route with committed receipts, and 2 more whose receipts were still uncommitted at the window's end; none declared a profile. Also reported and never counted: 22 PRODUCT commits that landed off that route, 11 of them recorded as the USER-directed orchestrator's (## Subjects).
window: 2026-09-19T20:00Z .. 2026-09-24T02:00Z
health: assurance=UNSATISFIED operability=PRESSURED
providers: none (no lane cleared a sentinel for this filing)
posture: not computed — model review contributed (two read-only Opus ratification lanes), and the R9 tool is one PROMPT K names, which docs/13 P-STEWARD step 7e forbids the filing seat to run (U6, ROUTED by the last harvest; unchanged)

Third filing by this board, re-filed because `code` moved r8 → r9 (PROMPT K §6). The second filing (blob `d6a5f40f`) was
harvested on 2026-09-20: `dng-auto-processor.dispositions.md` carries `filing_blob: d6a5f40f…` and answers all 39 of its
lines and its 5 HEADER lines, so nothing is carried forward undisposed. This filing does three things. It measures this
board against the two `code` r9 rows that were adopted from its own last filing. It answers U7, which that harvest
ROUTED back to this bench. And it reports that the board ran no subject through the kernel in this window. The seat
that writes this filing is `dng-design-steward`. It works from this board's own cards, receipts and ledgers, and it
ran no subject.

`assurance=UNSATISFIED`: no subject was declared or accepted under the kernel, and the product's own bar produced no
acceptance either — WORK.md's SCOREBOARD has no line inside the window (its newest is `20260918-1356`), so no candidate
was held-out-scored. `operability=PRESSURED`: 208 dispatches for 16 cop landings, about 13 per landing against about 28
in the last window, summed over the four cop daily-ledger lines after the one the last filing already counted — dispatched and landed
136 and 12, 37 and 2, 32 and 1, 3 and 1. The first of those lines carries two days' totals, because one of the two days
has no line of its own (an open token on this board); the last is the figure the cop recorded for the window, before a
later tick rewrote that day's line. A 17th route
landing was made by the USER-directed orchestrator, outside the cop's count, and 22 PRODUCT commits landed off the
card route, 11 of them recorded as that seat's (## Subjects). Five cards parked in the window, the open set rose
to 14 inside it, above docs/13 P-COP's cap of 12, and stood at 12 at its end, hosted CI reads `ci=failure` at the window's end, and one scheduled seat is stranded (K9).

Unqualified paths and commit ids are this board's repository. Evidence kept outside it is named by description, never by path: those
ledgers sit two directory reads from dispositions that carry reviewers' findings verbatim, and bus law 4 bars a path
that locates in-flight review reasoning. Doctrine paths are qualified.

## Subjects

**Kernel subjects: none.** The declaration step exists only as a practice. No rule, tool or hook reads
`k5-declaration.json` (IF13), and none orders one written. In this window nobody wrote one (IF15).

**Landings on this board's own route, reported and never counted.** Each has a receipt at
`metrics/ratify/<TASK>/<attempt>/receipt.json` on master, and each landed by `git merge --ff-only` of an exact sha onto
nested-repo master. The last column is measured for the r9 subject-identity row: the PRODUCT paths (docs/14 §4's closed
set) in the NET diff between the master the reviewed subject was based on and the master it landed on, none of which the
subject itself changed. Only one row reads differently as a union of the paths each commit touched:
CONSOLE-STREAM-IL-SEAM-BATCH-PASS's range touched 13, two of them restored to their base bytes inside the range.

| Task / attempt | Reviewed → landed (tree same?) | Author → key 1 / key 2 | Disjoint PRODUCT paths crossed |
|---|---|---|---|
| RAMP-DECISION-RECEIPT-DERIVED-DOMAIN / 3 | 977f1fa1 → f1312c2f (no) | gpt-6-astra (committer claude-sonnet-5) → claude-fable-5-1 / claude-opus-5 | 0 |
| MIRROR-SYNC-PIPELINE / 2 | 5d7e4582 → 5b2f23f4 (no) | claude-fable-5-1 → gpt-5.6-sol / claude-opus-5 | 0 |
| MIRROR-GATE-FAILOPEN-CLASS / 2 | c349fd1e → 0542834a (no) | gpt-6-astra (committer claude-sonnet-5) → claude-fable-5-1 / claude-opus-5 | 0 |
| MIRROR-TOOL-RESOLUTION-REDEPLOY / 1 | 13be2cb8 → c926f959 (no) | gpt-5.6-sol (committer claude-sonnet-5) → claude-fable-5-1 / claude-opus-5 | 0 |
| RAMP-CLIP-EXPOSURE-SINK / 2 | 7193e0f9 → 55b4fe96 (no) | claude-sonnet-5, then claude-fable-5-1 → gpt-5.6-sol / claude-opus-5 | 2 |
| RAMP-DEFAULT-TWIN-PINS / 1 | 75ce216e → 80c467a5 (no) | claude-sonnet-5 → gpt-5.6-sol ×2 / claude-opus-5 ×2 | 0 |
| RAMP-TWIN-PIN-WARRANT-MECHANISM / 3 | d2db4848 → 48ee1d53 (no) | claude-sonnet-5 → gpt-5.6-sol / claude-opus-5 | 0 |
| DCRAW-UNRESOLVABLE-SILENT-ZERO / 1 | 5eceb105 → 5eceb105 (yes) | claude-sonnet-5 → gpt-5.6-sol / claude-opus-5 | — |
| CORPUSBRIDGE-RESOLVETOOLPATH-NOT-A-RESOLVER / 1 | 4ef03955 → 4ef03955 (yes) | claude-sonnet-5 → gpt-5.6-sol / claude-opus-5 | — |
| CORPUSBRIDGE-RESOLVETOOLPATH-RENAME / 1 | c5add41a → 668e6338 (no) | gpt-5.6-sol → claude-fable-5-1 / claude-opus-5 | 2 |
| DCRAW-UNRESOLVABLE-AT-WB-SITES / 1 | 7f707d5b → 03c62d3b (no) | gpt-5.6-sol → claude-fable-5-1 / claude-opus-5 | 2 |
| T1F8C-OBSERVER-AUTHENTICATION-BATCH-PASS / 2 | acb5d263 → acb5d263 (yes) | claude-fable-5-1 → gpt-5.6-sol / claude-opus-5 | — |
| TARGETED-EXPOSURE-PRECAP-WITNESS / 1 | 03336314 → 03336314 (yes) | claude-sonnet-5 → gpt-5.6-sol / claude-opus-5 | — |
| MIRROR-EXPORT-REF-SELECTION / 2 | 6f436b18 → b4a01e89 (no) | gpt-6-astra (committer claude-sonnet-5) → claude-fable-5-1 / claude-opus-5 | 0 |
| CONSOLE-STREAM-IL-SEAM-BATCH-PASS / 1 | 8a82695e → d830d423 (no) | gpt-5.6-sol (committer claude-sonnet-5) → claude-fable-5-1 / claude-opus-5 | 11 |

The two landings without a committed receipt are `b28ffb18` (RUNNER-BASE-MANIFEST-HERMETIC, landed by the USER-directed
orchestrator; four `tools/**` paths) and `47bfe31d` (RAMP-WARRANT-RUN-PAIR-MASTER-RESCOPE; one test file). Their receipts
were on disk, untracked, at the window's end, and were committed after it closed.

**Off-route landings, reported and never counted.** 22 PRODUCT commits reached master inside the window outside every
route landing's delivered range, with committer dates from 2026-09-22T15:28Z to 2026-09-23T19:45Z and no merge commit
among them. The board's committed ledger records 11 of them, its largest batch among them, as the USER-directed
orchestrator's own landings, and records that batch's acceptance evidence as "a mutation proof and a full-suite-green
run" each; it names 4 more as landings without saying who landed them, and does not name the other 7. No key receipt was
committed for any of the 22. Some of their messages record key rounds run before the window on the pre-rebase subjects,
and two messages say of themselves that they need the two-key gate: "Not merged to master -- exposure path, needs the
two-key gate." and "Not merged to master - this is the acceptance surface itself and needs the two-key gate." They are the evidence
K1, K6 and K7 report against below, and they are outside every denominator in this filing.

## Answers to the benches the last harvest routed

- **U7, the O2 denominator across a second window: 7 of 15.** The fraction counts landings whose delivered range touches a
  feature assembly — every `DngAutoProcessor.*/` directory holding a `.csproj`, minus `*.Tests`, derived at read time
  (Core, App, CorpusBridge). The 7 are RAMP-DECISION-RECEIPT-DERIVED-DOMAIN, RAMP-CLIP-EXPOSURE-SINK,
  DCRAW-UNRESOLVABLE-SILENT-ZERO, CORPUSBRIDGE-RESOLVETOOLPATH-NOT-A-RESOLVER, CORPUSBRIDGE-RESOLVETOOLPATH-RENAME,
  DCRAW-UNRESOLVABLE-AT-WB-SITES and TARGETED-EXPOSURE-PRECAP-WITNESS. The two landings without a committed receipt touch
  none, which makes it 7 of 17. The last window read 3 of 11. Each delivered range is the landing's own commits over the
  master it landed on, and for a same-sha landing it runs from the receipt's `baseSha`. Whether any of the 7 changed the
  grade the shipped defaults emit is not derived here (U8). The 22 off-route commits are outside this denominator.
- **U5, adoption authority: unchanged.** docs/14 still holds no kernel adoption, and the filing seat is still forbidden
  PROMPT K's spec block and instance map.
- **U6, the posture line: unchanged.** No register-authorised seat computed R9 for this filing.

## Clauses

K1 | UNEXERCISED | "A candidate is never accepted on evidence whose only author is its producer" | No kernel subject existed, so no acceptance receipt establishes the observable. Reported without credit: all 15 route receipts name an author whose model is neither key's (## Subjects). Against it: the 22 off-route commits carry no key receipt, and the ledger's own record of its largest batch's acceptance is the producer's evidence — "a mutation proof and a full-suite-green run" each — which is this clause's failure case had they been kernel subjects | PROOF: a kernel subject accepted here on receipts naming one actor for production and acceptance

K2 | FIT | "Everything unlisted is autonomous. Escalation goes to the owner for decisions reserved by that register" | Register: docs/14 §0 (USER rulings verbatim) plus WORK.md RULES rule 3. Taken without asking because the register allowed it: 16 cop landings with no owner step (the header's daily-ledger sums). Reserved and held: docs/14 §2's two 2026-09-19 USER rulings force a Codex-authored test card's approach review and key 1 onto one model, and the seat that measured it filed an owner-defect token instead of narrowing either ruling | PROOF: an owner-reserved act taken here with no §0 entry authorising it

K3 | FIT | "under a claim an observer other than the claimant can decide stale and release; an expiring lease is one such mechanism" | The claim is the card's owner line plus a launch json written before the launch (docs/14 §3); staleness is decided from outside the seat by §3's liveness rule. In-window release by an observer other than the claimant: DCRAW-UNRESOLVABLE-AT-WB-SITES's first key-1 seat died on a 429 before its progress line, and the cop released that claim and relaunched the key whole — its landing receipt's `keys` field on master: "predecessor died on a 429 pre-progress-line; no attempt, no round". Identity: the r9 subject-identity row is measured under P:code below | PROOF: a claim here still held after its seat was dead, with no observer able to release it

K4 | FIT | "Work is complete only on positive evidence it was asked to produce" | The board found a K4 violation inside its own product and landed the repair in the window: three sampler constructors kept a dcraw path that resolves nowhere, so a later launch produced nothing and the pipeline read the absence as a result — the card's own title is "an unresolvable dcraw path is swallowed, not surfaced". `5eceb105` (DCRAW-UNRESOLVABLE-SILENT-ZERO, landed 2026-09-21) makes it observable, and its sibling DCRAW-UNRESOLVABLE-AT-WB-SITES (`03c62d3b`) carried the same repair to the white-balance call sites. Cards whose review is still in flight are not cited here (law 4) | PROOF: a card here closed DONE on a return code or a file's presence alone

K5 | UNEXERCISED | "Before work starts, a subject declares its profile and profile version." | 0 declarations in the window (IF15). The acceptance half therefore had nothing to bind | PROOF: a subject accepted here whose acceptance receipt names a different identity or profile than its declaration

K6 | UNEXERCISED | "Every acceptance includes a key from an independence class other than the producer's." | No kernel subject was accepted. Reported without credit: 15 of 15 route landings carry a key 1 from the provider opposite the author's. The last filing's O5 overlap, where a committer's model also served as key 1, did not recur: on all seven Codex-authored landings key 1 is `claude-fable-5-1`, and the five receipts that name a committer name `claude-sonnet-5`. The 22 off-route commits carry no key receipt at all | PROOF: an accepted subject here whose keys and producer share one provider

K7 | UNEXERCISED | "Acceptance and delivery are separate states." | Nothing was accepted under the kernel. Reported without credit: all 17 route landings reached nested-repo master by `--ff-only` of an exact sha; the 22 off-route commits carry no landing receipt. The derived mirror exports again (IF14 below). No typed `CLOSURE_INCOMPLETE` exists here (IF9) | PROOF: an accepted subject here that never landed and that the next tick names unprompted

K8 | INSTANCE-FAILURE | "Reset events update capacity telemetry. They never open a gate by themselves." | The first half held: nothing that needed no inference stopped, and 12 landings closed in the two days that carried the window's quota events. The second half failed in the instance. docs/14 §2 releases a capacity-emptied key pool when "the dark family does", and darkness lapses 60 minutes after the last error. A seat that does not run cannot error, so the gate re-opens on elapsed time alone, and cop tick 171 measured a capacity-emptied pool re-launched into the same 429 every tick (an open owner-defect token of this board). The next tick counted 3 Fable-specific 429s in 2 h 01 m on the account then in use and held one card on a 4 h backoff — a release rule written into that one card, `LABEL-DEFINITION-CONTRACT-AND-ATTAINABLE-OUTCOMES`, because docs/14 carries none | no replacement | PROOF: a quota event here after which a darkened seat re-opened only on a successful probe, never on elapsed time or on a reset alone

K9 | INSTANCE-FAILURE | "A fresh session on a new account, with empty memory, resumes from the project's tree and the bus alone." | A rotation moved the board to account `ff851812` inside the window. P-RESUME's run of 2026-09-21 first stopped at its parity gate, because the desktop app and the CLI stood on different accounts; once the owner signed the CLI in, the same run found them aligned and re-created three seats — the cop, the steward and, on the owner's answer to its question, the weekly resume drill. The cop and the steward have run since; the drill, weekly, had not yet fired by the window's end. Its run of 2026-09-23 re-created nothing. So this rotation took at least three owner steps: an answer, a sign-in and another answer. `dng-status-digest` was not re-created and is absent from the account in use, and §7 alarm 7 reads it as stopped: age 57.3 h against a 2.0 h bound, as the cop measured it at 2026-09-24 00:38Z. This is the third rotation to strand it. The last filing's finding stands unchanged | no replacement | PROOF: a rotation here after which every scheduled seat the register authorises ran again with no owner step

K10 | INSTANCE-FAILURE | "Provider and model inventory is machine-scoped and probe-derived, and it records the account it was derived under." | Unchanged: no machine-readable inventory and no `probed_under` in the repo. Parity is observed only as the SessionStart hook's line, which lives outside the repo, and P-RESUME's receipts quote it | no replacement | PROOF: an in-repo inventory whose `probed_under` names the current account

K11 | INSTANCE-FAILURE | "R1–R5, R7, R8 and R9 apply to every report a factory makes about itself" | One committed report on this board asserted an outcome before it was observed: a CLOSED line in the board's own ledger called a re-shaped brief proven because a relaunched seat had begun work on it, and no seat on that brief had written a byte when the line was stamped. The seat that found it may append nothing to that ledger but a CLOSED line (docs/13 P-STEWARD), so the false sentence still stands and the correction lives only in that seat's receipts. The line is the one `131ad1f2` appended; the card it concerns has since landed, so bus law 4 no longer withholds it. This filing takes no credit for 17 route landings or 22 off-route commits, and asserts no posture it did not compute | no replacement | PROOF: a correction line beside that CLOSED line in the board's ledger

K12 | FIT | "The steward harvests every filing and answers each one." | The second filing (blob `d6a5f40f`) was harvested on 2026-09-20: `dng-auto-processor.dispositions.md` answers all 39 lines and 5 HEADER lines, with `arbiter: gpt-6-astra (high)`. This re-file is the clause's other half. FENCE: the filing seat may not run `tools/harvest-status.py`, so the harvested state is read from the artifacts that tool reads | PROOF: a finding of the second filing with no disposition line

## Profile lines

P:code subject-identity | INSTANCE-FAILURE | "a nonempty manifest of repository paths that includes every repository input the reviewed behaviour or acceptance checks depend on" | 11 of 15 route landings delivered a tree other than the one both keys reviewed, and none of them declared an input manifest before review, so under r9 none of those 11 keys transferred: "a key on a different subject identity does not transfer", and the manifest route is open only to a subject that declared one. In 4 of the 11 the intervening range also carried PRODUCT paths the subject did not change — 2, 2, 2 and 11 of them (## Subjects). This board's manifest is `binding.json`'s `files`, the paths a subject changes and never its inputs; docs/14 §4 transfers a key whenever the range misses those paths and lets the pre-commit hook's re-run on the delivered sha stand in for the rest — the reading the last harvest refused, because "path disjointness alone does not exclude changed dependencies, build configuration or shared helpers". No receipt records a combined path-manifest digest. Honest compliance was available — declare the input manifest before review, or re-key whenever the delivered tree differs — so this is the instance's failure: 11 of 15 keys transferred where r9 says they do not | no replacement | PROOF: a receipt here recording a declared input manifest and its combined digest, reviewed and delivered alike

P:code claims | FIT | "observer-released claims may replace leases and name the subject, owner, owned processes and the rule by which another observer decides them stale and releases" | r9's text, adopted from this board's O7, fits the mechanism: owner line and launch json name the subject and the seat (and its `pid` on docs/14 §2's CLI route); §3's liveness rule is the observer's staleness rule; K3 above records an in-window release. FENCE, the same row's older clause: "Audit canonical state before and after: HEAD, index entries and flags, refs, reflogs, stash …" is not met for a mutation-capable key 2 — §10 step 6 records the SCRATCH worktree's state at removal, never the main checkout's before and after | PROOF: a seat here whose claim named no subject or owner, or that no observer could release

P:code independent-key | FIT | "a verifier from another model family (R3) whose class has not become a producer of the subject" | 15 of 15 route landings carry a key 1 from the provider opposite the author's, and on the seven Codex-authored ones key 1 is `claude-fable-5-1`, a model that neither authored nor committed them (five receipts name the committer `claude-sonnet-5`; two record no committer seat), so the last filing's committer FENCE no longer applies to this window. One limit, recorded by the receipts themselves: on three landings the key-1 model also reviewed the approach — `claude-fable-5-1` on MIRROR-TOOL-RESOLUTION-REDEPLOY and CONSOLE-STREAM-IL-SEAM-BATCH-PASS, `gpt-5.6-sol` on CORPUSBRIDGE-RESOLVETOOLPATH-NOT-A-RESOLVER — and the first receipt says so — "COMPROMISED BY RULE: s2 makes key1 Fable for a Codex author and Fable also reviewed this approach"; the row's rule concerns producers, and an approach reviewer is not one | PROOF: a subject here whose only other-provider key comes from a class that also wrote its product bytes

P:code resource-terminals | FIT | "independent key unavailable: typed terminals, no partial green" | DCRAW-UNRESOLVABLE-AT-WB-SITES's first key 1 "died on a 429 pre-progress-line; no attempt, no round", and the whole relaunch returned the landing's key (its receipt's `keys` field) | PROOF: a key death here recorded as a verdict or a partial green

P:code delivery-target | INSTANCE-FAILURE | "build the exact proposed record and run the validators and hooks that commit will face before any product push; refuse on failure" | The local pre-commit hook runs before every landing, but hosted CI runs only on the derived mirror, so a product push reaches its only CI run after it happens (docs/14 §3). In the window, hosted CI failed on two suites that pass locally. RunnerBaseManifest was fixed by `b28ffb18`. The other, `ScoreboardBuildIdentity_PassesItsOwnSuite`, had a card addressing it RUNNING at the window's end. The last cop daily-ledger line of the window reads `ci=failure`. Honest compliance was available: run the hosted validators on a candidate ref before the push | no replacement | PROOF: a landing here whose hosted validators ran green before its mirror push

P:code dispatch-preflight | INSTANCE-FAILURE | "the spending tool runs the project's resume gate before dispatch and retains its result, the inventory snapshot and digest, and account-parity evidence" | Unchanged: the window's 115 cop notes hold 208 dispatches with no resume-gate result, inventory snapshot or parity record before them — the K10 gap | no replacement | PROOF: a tick receipt here that retains a resume-gate result, an inventory digest and parity evidence before its first dispatch

P:measured-objective acceptance-evidence | UNEXERCISED | "the declared scorer on a held-out fold the producer never tuned on" | No SCOREBOARD line falls inside the window (its newest is `20260918-1356`), so no candidate was scored | PROOF: a scored run in the window that this line missed

## Instance failures

Status of the last filings' fourteen:
- **IF1, IF11**: historical, unchanged.
- **IF2: REPAIRED in the latent script**, by a commit that binds each ratify key to a measured author model; `tools/ratify.ps1` is still off the live landing path (U3's ruling stands: 0 of 15 window receipts name it).
- **IF3, IF4, IF10: LATENT**, as before.
- **IF5: repaired in the latent script**, by a commit that makes gate0 refuse non-comparable folds — itself one of the 22 off-route commits, whose own message says it needs the two-key gate. No gate0 ran on the live route.
- **IF6: LIVE.** WORK.md:4 still reads "Merge: tools/ratify.ps1 (gate 0 + cross-family key + adversarial Claude key)".
- **IF7**: resolved at the last read, and outside git.
- **IF8: unchanged.** `tools/claude-review-capture.ps1` and `tools/codex-author-capture.ps1` are both still absent.
- **IF9: unchanged.**
- **IF12: unchanged, and wider.** The window's 15 receipts encode seats eight ways: a map keyed by role (four receipts), a map keyed by dotted role (`author.implement`, `author.widen`), and lists whose entries are keyed by `{p, m, s}`, `{p, seat, model}`, `{phase, seat, model}`, `{seat, phase, agentId, model}` or `{role, model, agentId}` — and two receipts carry no `seats` field at all, only a `keys` list of `{role, seat, model}`.
- **IF13: unchanged, and now measured** as IF15.
- **IF14: RESOLVED.** The mirror exports again since a cop tick on 2026-09-22, so hosted CI now reads master's product bytes. What it finds is P:code delivery-target above.

IF15 | **The kernel declaration lapsed as soon as nothing asked for it.** Three subjects declared on 2026-09-18/19, and none of the 17 route landings or the 22 off-route commits after 2026-09-19T20:00Z did. No docs/13 or docs/14 rule, tool or hook orders or reads a declaration (IF13), so the step ran only while a seat remembered to run it.

## Untested

U6 | The `posture:` line (ROUTED, unchanged). The same limit applies to `tools/harvest-status.py`.

U8 | Whether any of U7's 7 feature-assembly landings changed the grade the shipped defaults emit. The last window's 3 did not. This window's are not derived here.

## Instance map

KERNEL: DOGFOOD-PENDING fleet-factory-kernel r5 · profile code@r9 + measured-objective@r3 · ratifiers: the owner's word "unfreeze" (WORK.md RULES rule 3), then seat `dng-design-steward` (docs/14 §7a, the only seat that may edit docs/12, 13 and 14) — which may not write this map or a spec block (docs/13 P-STEWARD step 7e) · instance home would be `docs/14-ORCHESTRATION.md` · pending since 2026-09-15

| Clause | Mechanism in this repo |
|---|---|
| K1 roles | docs/14 §2 seat table: key 1 from the family opposite the author, key 2 an Anthropic model that is never the author's; §4 "A tick may not edit its own governing document, and the hook enforces it"; §4a.1 voids a key's ACCEPT carrying an unattributed RED on the subject as committed |
| K2 authority | docs/14 §0 (owner rulings verbatim) + WORK.md RULES rule 3 |
| K3 identity and claims | per-file blob identity over `binding.json` + `git patch-id --stable` (docs/14 §4). **Declared INPUT manifest and its combined digest: NONE** (P:code subject-identity). Claim = the card's owner line + a launch json written before the launch; staleness decided and released by §3's liveness rule. Lease: none, by design (§3 "never add a lease") |
| K4 completion | `completion.json`, `return.md`, `binding.json`; typed returns; §5 receipt on every run |
| K5 acceptance | the card as contract; `approach.md` pre-code gate. **Profile-and-version declaration required by any rule: NONE** (IF13, IF15) |
| K6 keys | docs/14 §2; receipts name each seat's model. **Machine-readable receipt schema: NONE** (IF12) |
| K7 delivery | `git merge --ff-only` of an exact sha to nested-repo master after per-file blob identity and a green hook re-run; mirror derived (§3). **Hosted validators before the product push: NONE** (P:code delivery-target). **Typed CLOSURE_INCOMPLETE: NONE** |
| K8 capacity | docs/14 §4 HELD-FOR-CAPACITY / HELD-FOR-KEY, §2 family failover, worktree kept. **A release that needs a successful probe rather than elapsed time: NONE** (K8) |
| K9 resume | docs/13 P-RESUME + a receipt on every resume, outside the repository. **Re-creation of every authorised scheduled seat from the tree: NONE** (K9) |
| K10 inventory | **NONE in repo** — no inventory, no `probed_under`, no parity record in tick notes |
| K11 honesty | docs/14 §4b mutation refutation; §4 disposition off the adjudicated list. **A route for the seat that finds a false ledger line to correct it there: NONE** (K11) |
| K12 feedback | this file and its two harvested predecessors. **In-repo DOGFOOD/ADOPT declaration: NONE** |

## Counts

Clauses: 4 FIT · 0 FRICTION · 0 BREAK · 0 N/A · 4 UNEXERCISED · 4 INSTANCE-FAILURE
Profile: 3 FIT · 0 FRICTION · 0 BREAK · 0 N/A · 1 UNEXERCISED · 3 INSTANCE-FAILURE
Ledger totals (INSTANCE-FAILURE excluded per kernel §5): **7 FIT · 0 FRICTION · 0 BREAK · 0 N/A · 5 UNEXERCISED**
Plus 1 new instance failure (IF15), a status line for each of the fourteen earlier ones, answers to U5, U6 and U7, and 2 Untested.
