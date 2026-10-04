project: dng-auto-processor
kernel: fleet-factory-kernel r5
profile: code@r10 (primary) + measured-objective@r3 — kernel §6's row as harvested (M1)
instance: docs/KERNEL-INSTANCE-MAP.md on nested-repo master (written by card KERNEL-DOGFOOD-INSTANCE-MAP under docs/14 §0's kernel entry, landed `db197676`; KERNEL line DOGFOOD, ## Instance map)
subjects: 0 end-to-end under the kernel, and 0 declared in this window — no `k5-declaration.json` was written after 2026-09-24T02:00Z. Reported as mechanism evidence and never counted: 17 landings on this board's own two-key route, each with a committed receipt; one, the kernel card, wrote a profile line first as text its receipt does not bind (K5), and no other declared a profile. 0 PRODUCT commits landed off that route (## Subjects).
window: 2026-09-24T02:00Z .. 2026-10-04T01:50Z
health: assurance=UNSATISFIED operability=PRESSURED
providers: none (no lane cleared a sentinel for this filing)
posture: not computed — model review contributed (two read-only Opus ratification lanes), and the R9 tool is one PROMPT K names, which docs/13 P-STEWARD step 7e forbids the filing seat to run (U6, ROUTED; unchanged)

Fourth filing by this board, re-filed because `code` moved r9 → r10 (PROMPT K §6), the third is past its week, and the
instance map now stands on master, so the `KERNEL:` line is DOGFOOD. The third
filing (blob `a018daf6`) was harvested on 2026-09-24: `dng-auto-processor.dispositions.md` carries `filing_blob: a018daf6…`
and answers it, so nothing is carried forward undisposed. This filing measures the window against r10, reports that the
board ran no subject through the kernel, and records three changes in the instance: the K8 release rule was repaired,
no PRODUCT commit reached master off the route, and the kernel's DOGFOOD route was recorded in docs/14 §0 and its
instance map landed. The seat that writes it is `dng-design-steward`. It works from this
board's own cards, receipts and ledgers, and it ran no subject.

`assurance=UNSATISFIED`: no subject was declared or accepted under the kernel, and the product's own bar produced no
acceptance either — WORK.md's SCOREBOARD has no line inside the window (its newest is `20260918-1356`).
`operability=PRESSURED`: 180 dispatches for 17 landings, about 11 per landing against about 13 in the last window,
summed over the seven cop daily-ledger lines dated inside the window in WORK.md as committed at the window's end
(dispatched and landed 18 and 2, 19 and 0, 27 and 1, 29 and 5, 38 and 3, 35 and 5, 14 and 1). No cop daily-ledger line is dated 2026-09-25, -26 or -27, and no route landing fell between
2026-09-24T06:41Z and 2026-09-29T01:54Z. The board's own alarm 3 fired on 2026-10-03 for no card landing from 10:35Z to
22:35Z; until 16:25Z of that span an expired CLI sign-in had darkened the Claude family (K8). A rotation moved the board to a new account inside the window (K9). At the
window's end the open set, derived by WORK.md rule 0 (every card whose state is not LANDED, CLOSED, DONE,
DONE-FAIL or SPLIT), is 7 cards (2 RUNNING, 1 PARKED, 2 MEASURED-NEGATIVE, 1 POINTER, 1 RULED; the card whose first token is `Q1a`
is CLOSED by that rule's first trap), under docs/13 P-COP's cap of 12. From 2026-09-30T07:52Z to 2026-10-02 every landing's mirror sync failed to push master — 12 of the window's 17 receipts
record the mirror's master rejected on a remote-only commit (`803cc5f9`) absent from the local mirror clone — and the two
later landings' syncs exited 0 and pushed master. The cop daily-ledger lines read `ci=stale` for 2026-09-30 and -10-01 and
`ci=success` for -10-02 and -10-03. No artifact this filing read records what cleared the rejection.

Unqualified paths and commit ids are this board's repository. Evidence kept outside it is named by description, never by
path: those ledgers sit two directory reads from dispositions that carry reviewers' findings verbatim, and bus law 4 bars
a path that locates in-flight review reasoning. Doctrine paths are qualified.

## Subjects

**Kernel subjects: none.** The declaration step exists only as a practice. No rule, tool or hook reads
`k5-declaration.json` (IF13), and none orders one written. In this window nobody wrote one (IF15).

**Landings on this board's own route, reported and never counted.** Each has a receipt at
`metrics/ratify/<TASK>/<attempt>/receipt.json` on master, and each landed by `git merge --ff-only` of an exact sha onto
nested-repo master. "Keys' subject" is the receipt's `keysSubjectSha` where it has one, else `reviewedSha`. The last
column is measured for the subject-identity row: the PRODUCT paths (docs/14 §4's closed set) the delivered tree carries
beyond the keys' subject, read from each receipt's `landing` field, which records its inert-commit rebase, and checked
with `git diff --name-only` over that rebase's range.

| Task / attempt | Keys' subject → landed (tree same?) | Author → key 1 / key 2 | PRODUCT paths crossed |
|---|---|---|---|
| BUILD-IDENTITY-HERMETIC / 1 | 18d41a2e → 18d41a2e (yes) | claude-sonnet-5 → gpt-5.6-sol / claude-opus-5-5 | — |
| ANCHOR-THREAD-SCORE-SEQUENCE / 4 | 26e43560 → 26e43560 (yes) | claude-fable-5-1 → gpt-5.6-sol / claude-opus-5-5 | — |
| CONTACT-SHEET-AUTO-PROPAGATION / 1 | 19d87310 → c7884d38 (no) | gpt-5.6-sol (committer claude-sonnet-5) → claude-fable-5-1 / claude-opus-5-5 | 0 |
| BUILD-IDENTITY-CLEAN-SOURCE-HYGIENE-BATCH-PASS / 1 | f3e8b58b → f3e8b58b (yes) | claude-sonnet-5-5 → gpt-5.6-sol / claude-opus-5-5 | — |
| MIRROR-SYNC-SIDE-REF-REQUIRED-KILLS / 1 | ed67da89 → ed67da89 (yes) | gpt-5.6-sol (committer claude-sonnet-5) → claude-fable-5-1 / claude-opus-5-5 | — |
| CONTACT-SHEET-DISCLOSURE-WITNESSES-BATCH-PASS / 1 | 5a0cf74a → 6cc6b472 (no) | claude-sonnet-5 → gpt-5.6-sol / claude-opus-5-5 | 0 |
| PROPAGATION-PREFERENCES-TOGGLE / 1 | aaa02865 → 6d246916 (no) | claude-sonnet-5-5 → gpt-5.6-sol / claude-opus-5-5 | 0 |
| LEARN-PROJECT-DCRAW-FAIL-CLOSED / 2 | 65aee6e5 → 3aeabf12 (no) | gpt-5.6-sol, then gpt-6-astra (committer claude-sonnet-5) → claude-fable-5-1 / claude-opus-5-5 | 2 |
| PROPAGATION-UNUSED-ANCHOR-NOTICE / 3 | e8b8636c → e8b8636c (yes) | claude-sonnet-5-5, then claude-fable-5-1 → gpt-5.6-sol / claude-opus-5-5 | — |
| LEARN-PROJECT-INCOMPLETE-SCAN-GUARD / 1 | 8d74df22 → 8d74df22 (yes) | claude-sonnet-5-5 → gpt-5.6-sol / claude-opus-5-5 | — |
| APP-ADD-FINISHED-PROJECT-DCRAW-GUARD / 2 | 50a0af6d → 50a0af6d (yes) | gpt-5.6-sol, then gpt-6-astra (committer claude-sonnet-5-5) → claude-fable-5-1 / claude-opus-5-5 | — |
| APP-ADD-FINISHED-PROJECT-INCOMPLETE-SCAN-GUARD / 1 | 21739dc7 → 21739dc7 (yes) | claude-sonnet-5-5 → gpt-5.6-sol / claude-opus-5-5 | — |
| TEACHING-STORE-CLIP-KEY-COLLISION / 3 | 43f893cd → 43f893cd (yes) | gpt-5.6-sol, then gpt-6-astra (committer claude-sonnet-5-5) → claude-fable-5-1 / claude-opus-5-5 | — |
| BUILD-PROFILE-EXCLUDE-PROJECT-FAIL-CLOSED / 1 | a408760f → a408760f (yes) | gpt-5.6-sol (committer claude-sonnet-5-5) → claude-fable-5-1 / claude-opus-5-5 | — |
| TEACHING-STORE-PROJECT-FOLDER-COLLISION / 1 | 5d8a127b → 5d8a127b (yes) | claude-sonnet-5-5 → gpt-5.6-sol / claude-opus-5-5 | — |
| KERNEL-DOGFOOD-INSTANCE-MAP / 3 | db197676 → db197676 (yes) | claude-sonnet-5-5, then claude-fable-5-1 → gpt-5.6-sol / claude-opus-5-5 | — |
| BUILD-QUEUE-ADOPTION / 1 | b722ab64 → b722ab64 (yes) | claude-sonnet-5-5 (approach, self-reported; implement recorded as the alias `sonnet`) → gpt-5.6-sol / claude-opus-5-5 | — |

LEARN-PROJECT-DCRAW-FAIL-CLOSED's 2 are PROPAGATION-PREFERENCES-TOGGLE's own two PRODUCT paths, which landed first and which
its receipt records as disjoint from its binding.

**Off-route landings: none.** Every first-parent master commit inside the window that touches a PRODUCT path lies inside
one of the 17 landings' delivered ranges (each range runs from the base its receipt's `landing` field names, else
its `rangeEnum.commits`, else its `baseSha`, to its landed sha). The last window had 22.

## Answers to the benches the last harvest routed

- **U7, the O2 denominator across a third window: 12 of 17.** The fraction counts landings whose delivered range touches a
  feature assembly — every `DngAutoProcessor.*/` directory holding a `.csproj`, minus `*.Tests` (Core, App, CorpusBridge).
  The 5 that touch none are BUILD-IDENTITY-HERMETIC, BUILD-IDENTITY-CLEAN-SOURCE-HYGIENE-BATCH-PASS,
  MIRROR-SYNC-SIDE-REF-REQUIRED-KILLS, KERNEL-DOGFOOD-INSTANCE-MAP and BUILD-QUEUE-ADOPTION. The last two windows read 3 of 11 and 7 of 15 (receipted landings, as here). Whether any of the 12 changed the grade
  the shipped defaults emit is not derived here (U8).
- **§a.u4, routed to this board by AdversarialLLM's harvest (a delivered-pipeline delayed-outcome fixture): none to bring.**
  The fixture asks for an ACCEPTED pipeline's pinned identity, scorer and baseline, a declared later outcome observation and
  its remediation record. This board accepted no subject under the kernel, and no SCOREBOARD line falls in the window.
- **K8 (ROUTED to a capacity-admission bench), P:code independent-key (ROUTED to an independence-provenance bench) and U8:**
  answered in their own lines below — K8 by the in-window repair, independent-key by withdrawing the FIT for want of contribution
  records, U8 as still not derived.
- **U5, adoption authority: answered, and now in the register.** The owner's answers of 2026-09-30 to 2026-10-02 are
  recorded verbatim in docs/14 §0's kernel entry and the entry after it, read for PROMPT K's DOGFOOD route only: recording ADOPT needs a
  new owner word, recorded there as its own entry. Under it card KERNEL-DOGFOOD-INSTANCE-MAP, opened by the cop as any card
  is, wrote the instance map, which landed on master (`db197676`). The filing seat gains one exception, the `KERNEL:` line
  and the spec's mirror of it (docs/13 P-STEWARD step 7e); it still runs no tool, subject, spec block or instance map that
  PROMPT K names otherwise.
- **U6, the posture line: unchanged.** No register-authorised seat computed R9 for this filing.

## Clauses

K1 | UNEXERCISED | "A candidate is never accepted on evidence whose only author is its producer" | No kernel subject existed, so no acceptance receipt establishes the observable. Reported without credit: all 17 route receipts name an author whose model is neither key's, and no PRODUCT commit landed off the route, so the last window's producer-only acceptance did not recur | PROOF: a kernel subject accepted here on receipts naming one actor for production and acceptance

K2 | FIT | "Everything unlisted is autonomous. Escalation goes to the owner for decisions reserved by that register" | Register: docs/14 §0 (USER rulings verbatim) plus WORK.md RULES rule 3. Taken without asking because the register allowed it: 17 route landings, none needing an owner act at landing. Escalations on their paths went where the register sends them: CONTACT-SHEET-DISCLOSURE-WITNESSES-BATCH-PASS and MIRROR-SYNC-SIDE-REF-REQUIRED-KILLS were HELD until the owner's 2026-09-30T12:28Z answer, KERNEL-DOGFOOD-INSTANCE-MAP ran under owner rulings that bind that card alone (2026-10-01, 2026-10-02), and BUILD-IDENTITY-HERMETIC was opened and landed by an owner-directed session, each recorded in its receipt or in docs/14 §0. Reserved and held: the owner's 2026-09-30 answer on commits to a card's own branch is recorded in docs/14 §0 with its literal scope (a seat's own `item/<card>` branch, no landing), and seats commit under it only within that scope; the kernel's DOGFOOD route is recorded there with its literal scope too, and the instance map was written by an ordinary card under it | PROOF: an owner-reserved act taken here with no §0 entry authorising it

K3 | FIT | "under a claim an observer other than the claimant can decide stale and release; an expiring lease is one such mechanism" | The claim is the card's owner line plus a launch json written before the launch (docs/14 §3); staleness is decided from outside the seat by §3's liveness rule. In-window release by an observer other than the claimant: cop tick 232 released BUILD-IDENTITY-CLEAN-SOURCE-HYGIENE's Fable seat after it "died with its host" and relaunched it whole at attempt 3, no attempt charged (`cf57cc4b`'s message). The instance map's K3 row is NONE for an identity held by one claimant at a time with an atomic claim; this line rates only the observer-release reading the last harvest adopted, which that row does not deny | PROOF: a claim here still held after its seat was dead, with no observer able to release it

K4 | FIT | "Work is complete only on positive evidence it was asked to produce" | The board found K4 violations inside its own product and landed the repairs in the window: a learn-project run that ingests zero clips is refused before the teaching store is loaded (`3aeabf12`), and both learn sites refuse to replace a project's rows when the folder scan abandoned a subtree to a blocked directory read (`0fcb90f1`/`8d74df22` for the corpus bridge, `677ade21`/`21739dc7` for the App) — a scan that silently skipped work no longer counts as a complete one; and the corpus bridge's profile builder refuses a non-blank `--exclude-project` value that names no project, where it had exited 0 having excluded nothing (`a408760f`); a blank value still exits 0, a MINOR its receipt records as owed. Cards whose review is still in flight are not cited here (law 4) | PROOF: a card here closed DONE on a return code or a file's presence alone

K5 | UNEXERCISED | "Before work starts, a subject declares its profile and profile version." | 0 `k5-declaration.json` declarations in the window (IF15). The kernel card wrote its profile line first, in its approach.md and as the instance map's line 1 (the map's K5 row), as text: its landing receipt records no profile, so the acceptance half had nothing to bind | PROOF: a subject accepted here whose acceptance receipt names a different identity or profile than its declaration

K6 | UNEXERCISED | "Every acceptance includes a key from an independence class other than the producer's." | No kernel subject was accepted. Reported without credit: 17 of 17 route landings carry a key 1 from the provider opposite the author's; on the six Codex-authored landings key 1 is `claude-fable-5-1` and the committer is `claude-sonnet-5` or `claude-sonnet-5-5`. No PRODUCT commit landed without a key | PROOF: an accepted subject here whose keys and producer share one provider

K7 | UNEXERCISED | "Acceptance and delivery are separate states." | Nothing was accepted under the kernel. Reported without credit: all 17 route landings reached nested-repo master by `--ff-only` of an exact sha. Delivery to the derived mirror is not: from 2026-09-30T07:52Z every landing's mirror sync exited 1 with master rejected on the remote-only `803cc5f9` (12 of 17 receipts' `mirrorSync`), first recorded by `cfc112cd`'s message, through TEACHING-STORE-PROJECT-FOLDER-COLLISION's on 2026-10-02; the two later landings' syncs exited 0 and pushed master. No typed `CLOSURE_INCOMPLETE` exists here (IF9) | PROOF: an accepted subject here that never landed and that the next tick names unprompted

K8 | UNEXERCISED | "Reset events update capacity telemetry. They never open a gate by themselves." | The last filing's K8 claim (ROUTED by the harvest to a capacity-admission bench, not adopted) is answered by a repair in the instance, inside this window: docs/14 §2 (`e7a914c6`, 2026-09-24) now reads "Returns when the dark family does" "on EVIDENCE, never off the window" — a held seat is live again when a one-line probe on its own model answers or any seat on the same meter completes a call, and the owner-defect token on elapsed-time release is closed on that commit. Two in-window holds met the repaired rule. On 2026-09-29 the desktop host went dark and was restarted onto another account; a seat it hosted was held HELD-FOR-CAPACITY (host) with its partial work kept, and the retry author was relaunched only after it was probed live, not on the restart (`cf57cc4b`'s message). On 2026-10-03 an expired Claude CLI sign-in left docs/14 §2's tick-start probe reading the Claude family DARK for cop ticks 277-279 (`ccc460be`); a compute card already running went on until it was collected, every seat needing the Claude family waited, and the family read live again at 16:25Z, when the probe answered after the owner re-authenticated (the cop's alarm-3 reading of 2026-10-03 22:41Z in WORK.md). Reported without credit: neither artifact records a quota event, the observable's trigger | PROOF: a reset event here that by itself re-opened a darkened seat

K9 | INSTANCE-FAILURE | "A fresh session on a new account, with empty memory, resumes from the project's tree and the bus alone." | A rotation moved the board to a new account on 2026-09-29. Its P-RESUME pass ran in an owner-directed, attended session and waited twice for the owner's answers. It found the cop and the steward already registered on the account in use but with stale bytes — the cop's cron predated the 2026-09-22 cadence change, and both seats' prompts lacked two later tool-rule amendments — and repaired them; the status digest's old registration was alive again; the weekly resume drill's catch-up run froze. So this rotation's seats ran again only after an attended session repaired registrations a previous use of the account had left behind | no replacement | PROOF: a rotation here after which every scheduled seat the register authorises ran again with no owner step

K10 | INSTANCE-FAILURE | "Provider and model inventory is machine-scoped and probe-derived, and it records the account it was derived under." | Unchanged: no machine-readable inventory and no `probed_under` in the repo. Parity is observed only as the SessionStart hook's line, which lives outside the repo | no replacement | PROOF: an in-repo inventory whose `probed_under` names the current account

K11 | INSTANCE-FAILURE | "R1–R5, R7, R8 and R9 apply to every report a factory makes about itself" | Unchanged: the CLOSED line `131ad1f2` appended, which called a re-shaped brief proven before any seat on it had written a byte, still stands in the board's ledger with no correction beside it; the seat that found it may append nothing there but a CLOSED line (docs/13 P-STEWARD). This filing takes no credit for 17 route landings and asserts no posture it did not compute | no replacement | PROOF: a correction line beside that CLOSED line in the board's ledger

K12 | FIT | "The steward harvests every filing and answers each one." | The third filing (blob `a018daf6`) was harvested on 2026-09-24: `dng-auto-processor.dispositions.md` carries its blob and answers it, with `arbiter: gpt-6-astra (high)`. This re-file is the clause's other half. FENCE: the filing seat may not run `tools/harvest-status.py`, so the harvested state is read from the artifacts that tool reads | PROOF: a finding of the third filing with no disposition line

## Profile lines

P:code subject-identity | INSTANCE-FAILURE | "a nonempty manifest of repository paths that includes every repository input the reviewed behaviour or acceptance checks depend on" | 4 of 17 route landings delivered a tree other than the keys' subject (11 of 15 last window), each by docs/14 §4's inert-commit rebase, and none declared an input manifest before review, so under the row none of those 4 keys transferred. In 3 the rebase crossed 0 PRODUCT paths; in LEARN-PROJECT-DCRAW-FAIL-CLOSED it crossed 2 (## Subjects). This board's manifest is still `binding.json`'s `files`, the paths a subject changes and never its inputs. Honest compliance was available — declare the input manifest before review, or re-key whenever the delivered tree differs | no replacement | PROOF: a receipt here recording a declared input manifest and its combined digest, reviewed and delivered alike

P:code claims | FIT | "observer-released claims may replace leases" | Limited to the observer-release mechanism, as the last harvest adopted it: the card's owner line and a launch json written before the launch name the subject, owner and seat, docs/14 §3's liveness rule is the rule by which another observer decides a claim stale, and K3 records an in-window release by an observer other than the claimant | PROOF: a claim here released by its own claimant's say-so, or held after its seat died with no observer able to release it

P:code claims-audit | INSTANCE-FAILURE | "Audit canonical state before and after: HEAD, index entries and flags, refs, reflogs, stash, tracked contents, and ignored/untracked path inventories" | The last harvest ruled this an instance failure of its own line. Unchanged: for a mutation-capable key 2, §10 step 6 records the SCRATCH worktree's state at removal, never the main checkout's before and after | no replacement | PROOF: a key-2 run here whose receipt records the main checkout's HEAD, index entries and flags, refs, reflogs, stash, tracked contents and ignored/untracked path inventories with content hashes, before and after

P:code independent-key | UNEXERCISED | "a verifier from another model family (R3) whose class has not become a producer of the subject" | No kernel subject was accepted. Reported without credit: 17 of 17 route landings carry a key 1 from the provider opposite the author's, and no key-1 model authored or committed its subject. On 9 of 17 the key-1 model also reviewed the approach (`claude-fable-5-1` on all six Codex-authored landings, `gpt-5.6-sol` on three Claude-authored ones). The last harvest rejected a blanket exemption for approach reviewers and routed this row to an independence-provenance bench asking for each such reviewer's contribution record; this filing brings none, so it claims no FIT | PROOF: a subject here whose only other-provider key comes from a class that also wrote its product bytes

P:code resource-terminals | FIT | "independent key unavailable: typed terminals, no partial green" … "Before dispatch, declare any register-permitted substitution for a family-bound quorum seat" | A seat that died with its host was relaunched whole with no attempt and no round charged (K3). r10's new sentence was not exercised in the window, and the mechanism has a latent gap against it: docs/14 §2's substitutions are derived by rule, never chosen: a dark family's seats move to their tier analogs in the live family, and a round with no live cross-family key runs SINGLE-FAMILY with two live-family keys that are neither the author's model nor each other's, plus a third adversary on a guard, hook, CI, ratifier, acceptance-surface or data-loss card; a challenge pool emptied by lineage independence degrades one tier (2026-09-20), and a ladder exhausted of eligible opposite-family tiers continues into the author's own family (ruled 2026-09-21); an emptied pool parks as `HELD-FOR-KEY`. Each seat's launch json, written before launch, names its model, and a degraded challenge's label goes on the state line and ledger; but the SINGLE-FAMILY label (`cross_family: UNAVAILABLE`) is written in the round's receipt, after dispatch, so the declaration this sentence asks for is not ordered before dispatch | PROOF: a key death here recorded as a verdict or a partial green, or a SINGLE-FAMILY round here whose label was first written after its keys launched

P:code delivery-target | INSTANCE-FAILURE | "build the exact proposed record and run the validators and hooks that commit will face before any product push; refuse on failure" | Unchanged in mechanism: the local pre-commit hook runs before every landing, but hosted CI runs only on the derived mirror, after the push (docs/14 §3). The window's cop daily-ledger lines read `ci=pending`, `ci=success` twice, `ci=stale` twice (2026-09-30 and -10-01), then `ci=success` twice (-10-02 and -10-03) | no replacement | PROOF: a landing here whose hosted validators ran green before its mirror push

P:code dispatch-preflight | INSTANCE-FAILURE | "the spending tool runs the project's resume gate before dispatch and retains its result, the inventory snapshot and digest, and account-parity evidence" | Unchanged: docs/13 P-COP orders no resume-gate, inventory or parity read before dispatch, and none of the window's 180 dispatches carries all three; one tick's note retained a parity reading and per-model probes before its dispatch, without a resume-gate result or an inventory digest — the K10 gap | no replacement | PROOF: a tick receipt here that retains a resume-gate result, an inventory digest and parity evidence before its first dispatch

P:measured-objective acceptance-evidence | UNEXERCISED | "the declared scorer on a held-out fold the producer never tuned on" | No SCOREBOARD line falls inside the window (its newest is `20260918-1356`), so no candidate was scored | PROOF: a scored run in the window that this line missed

## Instance failures

Status of the earlier fifteen:
- **IF1, IF11**: historical, unchanged.
- **IF2: repaired in the latent script**; `tools/ratify.ps1` is still off the live landing path (0 of 17 window receipts name it).
- **IF3, IF4, IF10: LATENT**, as before.
- **IF5: repaired in the latent script**; no gate0 ran on the live route.
- **IF6: LIVE.** WORK.md:4 still reads "Merge: tools/ratify.ps1 (gate 0 + cross-family key + adversarial Claude key)".
- **IF7**: resolved at an earlier read, and outside git.
- **IF8: unchanged.** `tools/claude-review-capture.ps1` and `tools/codex-author-capture.ps1` are both still absent.
- **IF9: unchanged.**
- **IF12: unchanged, and wider.** The window's receipts add a ninth seat encoding: an `authors` list per attempt and a `rounds` list whose entries carry `k1`/`k2` maps, beside the earlier eight. The three later receipts add none: BUILD-QUEUE-ADOPTION's is a list of `{role, model, agentId}` entries, and the other two use the ninth.
- **IF13: unchanged.**
- **IF14: resolved**, as before; what hosted CI finds is P:code delivery-target.
- **IF15: unchanged.** 0 declarations in a second consecutive window.

## Untested

U6 | The `posture:` line (ROUTED, unchanged). The same limit applies to `tools/harvest-status.py`.

U8 | Whether any of U7's 12 feature-assembly landings changed the grade the shipped defaults emit. Not derived here.

## Instance map

KERNEL: DOGFOOD fleet-factory-kernel r5 · profile code@r10 + measured-objective@r3 · instance docs/KERNEL-INSTANCE-MAP.md · since 2026-10-02

The instance map is `docs/KERNEL-INSTANCE-MAP.md` on nested-repo master; this section points at it and keeps no table. Its
first line declares `kernel: fleet-factory-kernel r5 · profile: code@r10 + measured-objective@r3`, the revisions this
filing reads on the bus tip, so no older revision is reported. Its K1-K12 rows are that card's, and this seat writes none
of them. By its own rows, K3, K5, K6, K7, K8, K9, K10 and K11 are `NONE`, each with its nearest partial mechanism.

## Counts

Clauses: 4 FIT · 0 FRICTION · 0 BREAK · 0 N/A · 5 UNEXERCISED · 3 INSTANCE-FAILURE
Profile: 2 FIT · 0 FRICTION · 0 BREAK · 0 N/A · 2 UNEXERCISED · 4 INSTANCE-FAILURE
Ledger totals (INSTANCE-FAILURE excluded per kernel §5): **6 FIT · 0 FRICTION · 0 BREAK · 0 N/A · 7 UNEXERCISED**
Plus a status line for each of the fifteen earlier instance failures (none new), answers to §a.u4, U5, U6 and U7, and 2 Untested.
