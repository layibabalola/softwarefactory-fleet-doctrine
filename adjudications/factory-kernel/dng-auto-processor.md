project: dng-auto-processor
kernel: fleet-factory-kernel r5
profile: code@r8 (primary) + measured-objective@r3 — kernel §6's row as harvested (M1); both kernel subjects in this window declared code@r7, the revision current when they declared (## Subjects)
instance: DngAutoProcessor/docs/14-ORCHESTRATION.md (instance map below; KERNEL line DOGFOOD-PENDING — docs/12, 13 and 14 are steward-only under docs/14 §7a, no docs/14 §0 entry records a kernel adoption, and the seat that files this may not write the instance map)
subjects: 0 end-to-end. 2 declared under the kernel before production (GATE0-READER-GRAMMAR, RAMP-DECISION-RECEIPT: kernel r5 · code@r7, contract bound by sha256), 0 accepted — both PARKED at attempt 2 when both keys re-found an already-confirmed defect class. Reported as mechanism evidence and never counted: 11 landings on this board's own two-key route that declared nothing.
window: 2026-09-15T20:00Z .. 2026-09-19T20:00Z
health: assurance=UNSATISFIED operability=PRESSURED
providers: none (no lane cleared a sentinel for this filing)
posture: not computed — model review contributed (two read-only claude-opus-5 ratification lanes), and the R9 tool is one PROMPT K names, which docs/13 P-STEWARD step 7e forbids the filing seat to run

Second filing by this board, re-filed because the kernel moved r4 → r5 and measured-objective r2 → r3 (PROMPT K §6).
The first filing (blob `1f2eceff`) was harvested on 2026-09-17, and all 43 of its lines have a disposition, so nothing is
carried forward undisposed. This filing does three things. It answers the benches that harvest ROUTED back where this seat
can measure them (U3, U4, and a denominator for O2). It files this board's first `P:code` lines, since the harvest's remap
(M1) made `code` the primary profile. It reports the first two subjects this board declared under the kernel. The window
opens after the kernel first existed (2026-09-14T20:49:38Z), so `window-opened-before-kernel=no`. The seat that writes
this filing is `dng-design-steward`. It works from this board's own cards, receipts and ledgers, and it ran no subject.

`assurance=UNSATISFIED`: no subject was accepted under the kernel. Its two declared subjects were refused at review, and the
product's own bar, held-out score plus blind judge, produced no acceptance: the one pre-declared measured-objective arm lost
against its own criteria, and the one blind judge was voided by its own controls (K4). `operability=PRESSURED`: 84 dispatches
for 3 landings over the two DAILY lines WORK.md carries, read at 2026-09-20T01:20Z (2026-09-18 23:45Z: dispatched=42,
landed=2; 2026-09-19 20:26Z: dispatched=42, landed=1). Both lines carry `ci=stale`. There are 6 parked cards, and the open-card count is 12. One more card would pass the cap in
docs/13 P-COP's boot ("If more than 12 cards are open, this tick's only act is to split or park"). The derived mirror failed
on 11 of 11 landings (IF14).

Unqualified paths are this board's repository (`C:\code\DngAutoProcessor - Claude\DngAutoProcessor`). Evidence ledgers are
under `C:\DngAutoJobs\evidence\`. Doctrine paths are qualified.

## Subjects

**Kernel subjects: declared before production, not accepted.**

- **GATE0-READER-GRAMMAR.** Declared 2026-09-18T20:36:21Z in `C:\DngAutoJobs\evidence\GATE0-READER-GRAMMAR\attempt1\k5-declaration.json`
  "at placement, before any seat of this card exists" (`ledgerLaunchJsonsAtDeclaration: 0`). Kernel spec blob `6821c4c3`; profile blob `3b38da16`.
  - Contract: the card minus its `state:` line, sha256 `4af51404…`. It recomputes to the same digest at this filing's HEAD, so one contract
    judged both rounds.
  - Seats, from each attempt's launch json: author `claude-sonnet-5`, key 1 `gpt-5.6-sol`, key 2 `claude-opus-5` in both
    rounds; approach review `gpt-6-astra` in round 1 only — attempt 2 carries no `launch.approach-review`, which is by
    design (docs/14 §2: the approach review is one round, before any product byte).
  - Outcome: PARKED at attempt 2 (ceiling 2 of 3). Round 2 adjudicated 5 CONFIRMED BLOCKER and 3 CONFIRMED MAJOR, with its class A re-found
    by both keys independently (WORK.md QUEUE 1). Its own contract clause 9 stop rule is triggered. The branch is retained and never merged.
- **RAMP-DECISION-RECEIPT.** Declared 2026-09-18T15:59:34Z in `…\RAMP-DECISION-RECEIPT\attempt1\k5-declaration.json`. That was after the
  author's read-only APPROACH (15:50-15:54Z) and before any product byte: worktree `status --porcelain` 0 lines, no implement launch json.
  - Contract: sha256 `aca91f24…`, which also recomputes unchanged at HEAD.
  - Seats: author `gpt-5.6-sol`, committer `claude-sonnet-5`, key 1 `claude-sonnet-5`, key 2 `claude-opus-5` in both rounds;
    approach review `claude-opus-5` in round 1 only — attempt 2 carries commit, implement, key 1 and key 2 and no approach
    review, by the same design.
  - Outcome: PARKED at attempt 2 by docs/14 §4b row 3. The confirmed class is "a receipt field whose witness cannot fail on the card's
    fixtures", confirmed 1 → 2 (WORK.md QUEUE 6(b)). Its dimensioned batch pass also parked on that class. A redesigned successor,
    `packets/RAMP-DECISION-RECEIPT-DERIVED-DOMAIN.md`, was READY at the window close and declares nothing.

**Landings on this board's own route, reported and never counted.** Each has a receipt at
`metrics/ratify/<TASK>/<attempt>/receipt.json`, and each landed by `git merge --ff-only` of an exact sha onto nested-repo
master. None declared a kernel profile.

| Task | Reviewed → landed (tree same?) | Author → key 1 / key 2 |
|---|---|---|
| T1F2B-BUILD-IDENTITY-BATCH-PASS | e128ae3c → e46edb9b (no) | claude-sonnet-5 → gpt-5.6-sol / claude-opus-5 |
| T1F4-POPULATION | a9b1d62e → c8f472b1 (no) | claude-sonnet-5 → gpt-5.6-sol / claude-opus-5 |
| T1F6-CODEX-REVIEW-METADATA | 1a2c0093 → 1a2c0093 (yes) | claude-sonnet-5 → gpt-5.6-sol / claude-opus-5 |
| T1F5-CLAUDE-REVIEW-RESULT | 920fa7c0 → 4ae2d9c2 (no) | claude-sonnet-5 → gpt-5.6-sol / claude-opus-5 |
| T1F3-CODEX-REVIEW-RESULT | 507419e3 → 0676cc86 (no) | claude-sonnet-5 → gpt-5.6-sol / claude-opus-5 |
| RUNNER-BASE-IMPORT | 23c8eb41 → 91746357 (no) | gpt-5.6-sol (committer claude-sonnet-5) → claude-sonnet-5 / claude-opus-5 |
| REACH-SUPPLY-OWED | 715e9b8e → 715e9b8e (yes) | gpt-5.6-sol (committer claude-sonnet-5) → claude-sonnet-5 / claude-opus-5 |
| RAMP-GAIN-LEVER | 839ed3cc → 839ed3cc (yes) | gpt-5.6-sol (committer claude-sonnet-5) → claude-sonnet-5 / claude-opus-5 |
| T1F7-ORACLE-REACH-DISCLOSURE | 49879c64 → 1c2a8eba (no) | claude-sonnet-5 → gpt-5.6-sol / claude-opus-5 |
| COLOUR-RECEIPT-NOTRUN-STATE | a43d2545 → 029e73c1 (no) | gpt-5.6-sol (committer claude-sonnet-5) → claude-sonnet-5 / claude-opus-5 |
| RAMP-BASE-COORDINATE-FIX | 8230cf8b → 5f23c194 (no) | claude-sonnet-5 → gpt-5.6-sol / claude-opus-5 |

## Answers to the benches the first harvest routed

- **U3, "whether `tools/ratify.ps1` is on the live path at all": it is not.**
  - 0 of the 11 window landing receipts name `ratify.ps1` or a gate0.
  - The newest file under any `metrics/ratify/<sha7>/` in the main checkout is `b05f1a6/key1.txt`, 2026-09-09 23:54Z.
  - The window's cop notes name `tools/ratify.ps1` only as the file that the GATE0 cards edit.
  - The live gate is docs/14 §4's cop route: adjudicated finding list, per-file blob identity, hook re-run, receipt.
  - So the first filing's IF2, IF3, IF4 and IF10 are latent, and IF6 is live and promoted (below), as the harvest foresaw.
- **U4, S1's four declared criteria: evaluated, and they refused the arm.** WORK.md SCOREBOARD `20260915-1722`
  (`DNG-SELF-TARGET-BUCKET-TIER`, ARM B) scored the arm against the criteria declared before the work:
  - fit=1.88 against `fit < 0.54`: FAIL.
  - median|dTemp|=686 against `<= 587`: FAIL.
  - shape 0.215 and evaluable 90: pass.
  - The line reads "LOSING ARM, NEVER A CANDIDATE". The card closed MEASURED-NEGATIVE; its branch is retained and never merged.
  - Two limits, stated against interest. The declaration still named no profile or version. The score's binding to the subject is asserted
    rather than verified (P:measured-objective acceptance-evidence below).
- **O2, a denominator.** Define the fraction over landings whose delivered bytes touch a feature assembly: every `DngAutoProcessor.*/`
  directory holding a `.csproj`, minus `*.Tests`, derived at read time exactly as docs/14 §7 alarm 1 derives it (today Core, App and
  CorpusBridge).
  - In this window that is **3 of 11**: `839ed3cc` RAMP-GAIN-LEVER, `42e96176` and `5f23c194`
    RAMP-BASE-COORDINATE-FIX. The second is the feature-assembly commit inside COLOUR-RECEIPT-NOTRUN-STATE's delivered range, not
    that landing's sha, which is `029e73c1` (reviewed `a43d2545`) as the Subjects table above records.
  - **0 of those 3 changed the grade the shipped defaults emit.** The gain lever landed "gain 1.0 bitwise-identical". The ramp fix is
    opt-in, and "`AutoSmoothExposure=false` stands" (WORK.md QUEUE 3). The colour change corrects a receipt state, "NotRun, not Declined".
- **U5, adoption authority: unchanged.** docs/14 holds 0 `kernel` or `dogfood` mentions. Both declarations say "DOGFOOD (not ADOPT;
  binds nothing; docs/14 governs)". The seat that files this is forbidden PROMPT K's spec block and instance map, so recording DOGFOOD or
  ADOPT still waits on the owner's word.

## Clauses

K1 | UNEXERCISED | "A candidate is never accepted on evidence whose only author is its producer" | Neither kernel subject was accepted; both were refused at review and parked, so no acceptance receipt establishes the observable. Reported without credit: in every round of both subjects each key's model differs from the author's (## Subjects; the launch json of each seat under each attempt), and the refusals came from the keys | PROOF: a kernel subject accepted here on receipts naming one actor for production and acceptance

K2 | FIT | "Everything unlisted is autonomous. Escalation goes to the owner for decisions reserved by that register" | Register: docs/14 §0 (USER rulings verbatim) plus WORK.md RULES rule 3. In-window evidence, both directions: (a) taken without asking — RAMP-BASE-COORDINATE-FIX landed with no owner step (`metrics/ratify/RAMP-BASE-COORDINATE-FIX/1/receipt.json`: `"gate":"ADJUDICATED 0 BLOCKER 0 MAJOR 4 MINOR => LAND"`); (b) reserved and held — MIRROR-SYNC-PIPELINE is BLOCKED on "a decision only the USER can make", and cop tick 98 declined a swarm-delegated word "on AUTHORITY, not on evidence" because docs/14 §0 "holds a relay to be evidence, never an authority multiplier" (WORK.md QUEUE 2; `C:/DngAutoJobs/evidence/cop-note-20260919-0745Z-tick98.md`); (c) the owner's 2026-09-19 posture recorded in §0 as the exact question, the selected labels and the rejected ones (commit `f69bf619`) | PROOF: an owner-reserved act taken here with no §0 entry authorising it

K3 | FIT | "under a claim an observer other than the claimant can decide stale and release; an expiring lease is one such mechanism" | r5's text (this board's first-filing BREAK, adopted) now fits the mechanism. The claim is the card's owner line and a launch json written before the launch (docs/14 §3 "claim on disk before acting"); staleness is decided from outside the seat by §3's liveness rule. In-window release by an observer other than the claimants: cop tick 82, "three RUNNING cards, all FROZEN and none finished ⇒ BLOCKED-DARK (READY next tick; attempt NOT consumed; worktree kept)" (`C:/DngAutoJobs/evidence/cop-note-20260918-2345Z-tick82.md`). Identity is a content digest over the declared artifact set: per-file blob identity over `binding.json`'s files plus `git patch-id --stable`, recomputed by `git rev-parse <sha>:<path>` per path (RAMP-BASE-COORDINATE-FIX: `"blobIdentity":"2/2 reviewed==landed: d202c940 266956ba"`) | PROOF: a claim here still held after its seat was dead, with no observer able to release it

K4 | FIT | "Work is complete only on positive evidence it was asked to produce" | Two apparent results refused in the window, both on disk. (1) BLIND-AUTO-VS-MANUAL-BASELINE attempt 1: the stand-in model judge was voided by the card's own controls, `"typedResult": "VOID ZERO-FAILED POSITIVE-FAILED POSITION-DEGENERATE"` — 13 byte-identical pairs called different, the positive control 17 of 33, position 1 named on 32 of 39 — "never "no effect", never "indistinguishable"" (`C:\DngAutoJobs\evidence\BLIND-AUTO-VS-MANUAL-BASELINE\attempt1\phaseC-r2\completion.json`). (2) DNG-SELF-TARGET-BUCKET-TIER's arm was refused by its own pre-declared criteria (U4). FENCE: the first filing's IF4 (a GREEN of three exit codes in `tools/ratify.ps1`) is latent, not repaired — the script is off the live path (U3) | PROOF: a card here closed DONE on a return code or a file's presence alone

K5 | UNEXERCISED | "Before work starts, a subject declares its profile and profile version." | The declaration half was exercised twice, the first time on this board; the acceptance half was not reached. Both kernel subjects named kernel r5 and `code@r7` by blob and bound the acceptance contract by sha256 with a recompute command, round budget 3 and docs/14 §4's closing rule (## Subjects). Neither was accepted, so no acceptance receipt exists to bind. One timing fact is left to the harvest (O6): RAMP-DECISION-RECEIPT declared after its author's read-only approach and before any product byte | PROOF: a subject accepted here whose acceptance receipt names a different identity or profile than its declaration

K6 | UNEXERCISED | "Every acceptance includes a key from an independence class other than the producer's." | No kernel subject was accepted. Reported without credit, because it is the observable's own data: every round of both kernel subjects carried a key whose provider differs from the author's (GATE0-READER-GRAMMAR: author Anthropic, key 1 OpenAI; RAMP-DECISION-RECEIPT: author OpenAI, both keys Anthropic), and so did all 11 route landings (7 Claude-authored keyed by `gpt-5.6-sol`; 4 Codex-authored keyed by two Anthropic models). Against interest, see O5: in those 4 and in RAMP-DECISION-RECEIPT, key 1 is the committer's model | PROOF: an accepted subject here whose keys and producer share one provider

K7 | UNEXERCISED | "Acceptance and delivery are separate states." | Nothing was accepted under the kernel. Reported without credit: all 11 route landings reached nested-repo master by `git merge --ff-only` of an exact sha, and all 11 receipts record the derived mirror sync FAILED (IF14), which docs/14 §3 rules is not a delivery failure ("local master is the authority"). The first filing's IF9 stands: no typed `CLOSURE_INCOMPLETE` | PROOF: an accepted subject here that never landed and that the next tick names unprompted

K8 | FIT | "Running out of quota means rotating or parking the work that needs inference, never failing the factory closed." | Two in-window quota events; neither stopped anything that needed no inference. RAMP-BASE-COORDINATE-FIX's key 2 died on a session limit — receipt seat `key2-dead`, `"cause":"429 session limit"`, `"attemptsConsumed":0` — and was relaunched whole on the same model once the window closed, returning ACCEPT (seat `key2`; commit `29206c49`). WB-TRIM-OVERSHOOT-DECOMPOSITION's "Sol seat dies on model capacity and the retry runs on Sonnet" (commit `9962b189`; docs/14 §2 failover). The first filing's per-model credit FRICTION was adopted into measured-objective r3 and did not recur | PROOF: a quota event here after which work that needed no inference stopped

K9 | INSTANCE-FAILURE | "A fresh session on a new account, with empty memory, resumes from the project's tree and the bus alone." | The 2026-09-18 account rotation was resumed by docs/13 P-RESUME (`C:/DngAutoJobs/evidence/RESUME/20260918-1239.md`), which re-created the cop and the steward; both have run since. It stranded `dng-status-digest` and the weekly read-only `dng-resume-drill` that docs/14 §0 records the owner unfreezing on 2026-09-16, for the second rotation running: P-RESUME re-creates two rows and lists the rest for the owner, and the drill "has now been stranded twice and has never run once" (WORK.md OWNER-DEFECT token, cop tick 63). Honest compliance was available — the tree could carry those seats' definitions — so it is the instance's failure, open and addressed to the owner. The first filing's K9 FRICTION was ROUTED and is not re-argued | no replacement | PROOF: a rotation here after which every scheduled seat the register authorises ran again with no owner step

K10 | INSTANCE-FAILURE | "Provider and model inventory is machine-scoped and probe-derived, and it records the account it was derived under." | Unchanged since the first filing, where it was ADOPTED as an instance failure: no machine-readable inventory and no `probed_under` in the repo. `grep -ci parity docs/14-ORCHESTRATION.md` → 2, both prose (§0's option label "Cross-venue parity"; §7 alarm 6's note on account components), and 0 of the window's 57 cop notes mention parity. P:code dispatch-preflight below is the same gap seen from the profile | no replacement | PROOF: an in-repo inventory whose `probed_under` names the current account

K11 | FIT | "R1–R5, R7, R8 and R9 apply to every report a factory makes about itself" | Quoted from the clause this time, correcting the first filing's anchor (its harvest's header note). This filing does not assert a posture line it did not compute; takes no credit for 11 route landings or 2 refused subjects; answers U3 against interest (it makes IF6 live); and reports O5 against this board. Internally: docs/14 §4b's mutation refutation and §4's disposition read off the adjudicated list | PROOF: any claim here that its cited path does not support

K12 | FIT | "The steward harvests every filing and answers each one." | This board's first filing (blob `1f2eceff`) was harvested on 2026-09-17: `adjudications/factory-kernel/dng-auto-processor.dispositions.md` carries `filing_blob: 1f2eceff…` and answers all 43 lines, and `adjudications/factory-kernel/HARVESTS.md` carries its row. This re-file is the clause's other half. FENCE: the filing seat may not run `tools/harvest-status.py`, so the harvested state is read from the artifacts that tool reads, not from its output | PROOF: a finding of the first filing with no disposition line

## Profile lines

P:code subject-identity | FRICTION | "a key on a different tree does not transfer" | 8 of 11 route landings delivered a tree other than the one both keys reviewed (## Subjects). docs/14 §4 rebases a reviewed branch over master's bookkeeping commits and lands it on per-file blob identity of the subject's `binding.json` paths, a green hook re-run on the rebased sha and a shared patch-id — "never root-tree equality" — and voids the transfer when the intervening range touches the subject's own paths. The measured cost of the profile's rule here: "the cop's own bookkeeping commits advance master roughly every 30 minutes while a review takes about 90" (docs/14 §4, "Prefer rebase-before-review"), so re-keying every moved tree starves landings | REPLACES: "a key on a different tree does not transfer" -> "a key transfers to a different delivered tree only when every path the key reviewed has the same blob in both trees, the intervening change touches none of them, and the acceptance checks re-run green on the delivered tree" | PROOF: a landing here where all three held and the delivered tree failed a check the reviewed tree passed

P:code acceptance-evidence | FIT | "Before work, bind the acceptance contract by digest, including checks, harness limits, review scope, round budget and round-closing rule" | Both kernel subjects did this in `k5-declaration.json`: the contract is the card minus its `state:` line by sha256, with the recompute command, a round budget of 3 and docs/14 §4's closing rule; `packets/RAMP-DECISION-RECEIPT.md` names the review scope as the docs/13 briefs as written. Both digests recompute unchanged at this filing's HEAD, so "the same contract judges every round" held for both | PROOF: a round of either subject judged by a card body whose digest differs from the declared one

P:code independent-key | FIT | "a verifier from another model family (R3) whose class has not become a producer of the subject" | 11 of 11 route landings and every round of both kernel subjects carry a key from a provider other than the author's (## Subjects). FENCE: for the four Codex-authored landings and RAMP-DECISION-RECEIPT, the line holds only if a committer that "edits no product byte" (docs/13 C-COMMIT) has not "become a producer" — O5 | PROOF: a subject here whose only other-provider key comes from a class that also wrote its product bytes

P:code resource-terminals | FIT | "independent key unavailable: typed terminals, no partial green; retain the stopped candidate's bytes and receipts" | RAMP-BASE-COORDINATE-FIX's key 2 died on a session limit and was recorded as a death consuming no attempt (`"attemptsConsumed":0`; docs/14 §4 A2 HELD-FOR-KEY), with the candidate `8230cf8b` kept on its branch until the relaunch; cop tick 82 returned three frozen seats "READY next tick; attempt NOT consumed; worktree kept" | PROOF: a key death here recorded as a verdict or a partial green

P:code dispatch-preflight | INSTANCE-FAILURE | "the spending tool runs the project's resume gate before dispatch and retains its result, the inventory snapshot and digest, and account-parity evidence" | The cop dispatched on both window days (DAILY at 2026-09-20T01:20Z: dispatched=42 on 2026-09-18, 42 on 2026-09-19) after docs/14 §2's tick-start CLI probe, with no resume gate, no inventory snapshot and no parity record in any of the window's 57 cop notes — the K10 gap | no replacement | PROOF: a tick receipt here that retains a resume-gate result, an inventory digest and parity evidence before its first dispatch

P:measured-objective subject-identity | FIT | "digests of the evaluation set, scorer, runtime inputs outside git and delivered artifacts outside git" | The out-of-git input that the first filing's BREAK named is now pinned per run. docs/14 §6 (commit `68048c3c`) has a treatment that switches on a path the control leaves off pin the `-BaseEngine` by sha256 before the control and after the treatment, and the ramp cards did (WORK.md SCOREBOARD `20260918-1319`: "base engine ccb03575 pinned before and after"; `C:\DngAutoJobs\evidence\RAMP-BASE-NULL-TEST\attempt1\engine-pin.txt`). FENCE: the components are pinned one by one in each card's ledger; no single identity digest combines them in manifest path order | PROOF: a scored run here whose engine digest was not recorded before and after

P:measured-objective determinism-class | FIT | "byte-deterministic claims require an identical repeat at tolerance zero" | RAMP-BASE-NULL-TEST: "ramp ON at g = 0 ≡ CONTROL byte-for-byte on both folds, and the g = 1.0 witness actuated" (WORK.md QUEUE 3(e); disposition `C:\DngAutoJobs\evidence\RAMP-BASE-NULL-TEST\attempt1\disposition.astra.rbnull-a1-disp-astra-0114dc53.md`) — the r3 text adopted from this board's first filing, exercised with an arms-differ witness | PROOF: a byte-identity claim here with no identical repeat

P:measured-objective acceptance-evidence | INSTANCE-FAILURE | "Bind each score to the full subject identity verified for that run; an unverified binding is UNEVALUABLE" | DNG-SELF-TARGET-BUCKET-TIER's arm was scored on an UNCOMMITTED subject — "this line records the RUN and the card carries the resulting sha" (WORK.md SCOREBOARD `20260915-1722`) — so its binding is asserted by the card, not verified, and `tools/scoreboard.ps1` still has no clean-tree check (`grep -n -i 'porcelain\|diff --quiet\|dirty' tools/scoreboard.ps1` → empty). Under r3 that score is UNEVALUABLE, while the card closed MEASURED-NEGATIVE. Nothing was accepted on it — it refused the arm | no replacement | PROOF: a scoreboard line here that refuses to print against an unverified subject

## Instance failures

Status of the first filing's eleven, all ADOPTED by the harvest:
- **IF1 and IF11**: historical, unchanged.
- **IF2, IF3, IF4 and IF10: LATENT.** `tools/ratify.ps1` is off the live path (U3). It is unchanged since `b2386925` (2026-09-07).
- **IF5: LATENT.** No gate0 ran in the window.
- **IF6: LIVE, and now the operative one.** WORK.md:4 still reads "Merge: tools/ratify.ps1 (gate 0 + cross-family key + adversarial Claude
  key)". 0 of 11 window landings used it.
- **IF7: RESOLVED at read time.** The workspace `.claude/settings.json` Stop hook now runs `tools/session-checkpoint.py`, which is present.
  That file is outside git, so when it changed cannot be derived.
- **IF8: unchanged.** `tools/claude-review-capture.ps1` and `tools/codex-author-capture.ps1` are both still absent from master.
- **IF9: unchanged.**

IF12 | **The landing receipt has no schema.** The window's 11 receipts have 11 distinct sets of top-level keys; only six keys are common to all (`attempt`, `landedSha`, `mirrorSync`, `patchIdStable`, `reviewedSha`, `seats`). Seats are encoded three ways (`{s, m}`, `{p, m}`, `{role, model}`). `crossFamily` is present in 6 and `landedUtc` in 8. A reader can compute K6's independence classes from these receipts only by knowing all three encodings, which is the "computed, not asserted" requirement (R3) met by a human rather than a parser.

IF13 | **The two kernel subjects' declarations bind nothing the gate reads.** Both declarations say "binds nothing; docs/14 governs", and no docs/14 rule, tool or hook reads `k5-declaration.json`. The contract digests held only because nobody edited those card bodies (## Subjects), not because anything checked them.

IF14 | **The derived mirror failed on 11 of 11 window landings.** Every receipt's `mirrorSync` field records FAILED, from T1F2B's "fast-import rejects pre-existing history path DngAutoProcessor/audit.json" to RAMP-BASE-COORDINATE-FIX's "mirror stays baf02b65". Hosted CI therefore never ran on master's product bytes: both window DAILY lines read `ci=stale`. docs/14 §3 correctly keeps this from un-landing anything. The cause is a history path carrying a trailing carriage return (an OWNER-DEFECT token on this board). The card importing the mirror tooling is BLOCKED on an owner decision, and the sync's own repair is named as its successor's (WORK.md QUEUE 2).

## Observations

O5 | **A committer's model can be key 1 for the same subject.** On the four Codex-authored landings and on RAMP-DECISION-RECEIPT, `claude-sonnet-5` committed the author's bytes (docs/13 C-COMMIT: "edits no product byte") and then served as key 1. code@r8 says the independent key's "class has not become a producer of the subject", but it does not say whether a committer that edits no product byte is a producer. This board's 2026-09-19 posture moved key 1 for a Codex author to `claude-fable-5-1` (docs/14 §2, commit `f69bf619`). That ends the overlap going forward, although it was not the change's stated reason, which was the fleet's Opus floor for review acts.

O6 | **"Before work starts" is ambiguous for a read-only planning phase.** GATE0-READER-GRAMMAR declared before any seat existed. RAMP-DECISION-RECEIPT declared after its author's read-only approach and before any product byte, and its card says so literally "so the filing can judge whether that is 'before work'". K5 does not say whether work starts at the first seat or at the first product byte.

O7 | **code@r8's Claims field speaks only of leases.** It reads "leases name the subject, owner, expiry and owned processes". Kernel r5 K3, amended on this board's first-filing BREAK, makes an expiring lease one mechanism among others. A reader of the profile could take the field as re-requiring expiry. This board's claim record names subject and owner, and the seat's `pid` on the CLI route (docs/14 §2), never an expiry.

## Untested

U6 | The `posture:` line. The R9 tool is one PROMPT K names, and the seat that files this may not run such tools, so this filing cannot carry a computed posture. The same limit applies to `tools/harvest-status.py`.

U7 | The feature-assembly denominator for O2 is offered as a definition, not measured across more than this one window.

## Instance map

KERNEL: DOGFOOD-PENDING fleet-factory-kernel r5 · profile code@r8 + measured-objective@r3 · ratifiers: the owner's word "unfreeze" (WORK.md RULES rule 3), then seat `dng-design-steward` (docs/14 §7a, the only seat that may edit docs/12, 13 and 14) — which may not write this map or a spec block (docs/13 P-STEWARD step 7e) · instance home would be `docs/14-ORCHESTRATION.md` · pending since 2026-09-15

| Clause | Mechanism in this repo |
|---|---|
| K1 roles | docs/14 §2 seat table: key 1 from the family opposite the author, key 2 an Anthropic model that is never the author's; §4 "A tick may not edit its own governing document, and the hook enforces it"; §4a.1 voids a key's ACCEPT if its own run log carries a RED |
| K2 authority | docs/14 §0 (owner rulings verbatim) + WORK.md RULES rule 3 |
| K3 identity and claims | per-file blob identity over `binding.json` + `git patch-id --stable` (docs/14 §4); claim = the card's owner line + a launch json written before the launch; staleness decided and released by §3's liveness rule. **Lease: NONE, by design** (§3 "never add a lease") |
| K4 completion | `completion.json`, `return.md`, `binding.json`; typed returns; §5 receipt on every run; void-gated scorers (BLIND-AUTO-VS-MANUAL-BASELINE contract 15) |
| K5 acceptance | the card as contract; `approach.md` pre-code gate; `k5-declaration.json` on 2 cards. **Profile-and-version declaration required by any rule: NONE** (IF13) |
| K6 keys | docs/14 §2; receipts name each seat's model. **Machine-readable receipt schema: NONE** (IF12). **Enforced author-binding: NONE** (IF2, latent) |
| K7 delivery | `git merge --ff-only` of an exact sha to nested-repo master after per-file blob identity and a green hook re-run; mirror derived (§3). **Typed CLOSURE_INCOMPLETE: NONE** |
| K8 capacity | docs/14 §4 HELD-FOR-CAPACITY / HELD-FOR-KEY, §2 family failover, worktree kept; measured-objective r3's credit terminal |
| K9 resume | docs/13 P-RESUME + receipt under `C:\DngAutoJobs\evidence\RESUME\`. **Re-creation of every authorised scheduled seat from the tree: NONE** (K9) |
| K10 inventory | **NONE in repo** — no inventory, no `probed_under`, no parity record in tick notes |
| K11 honesty | docs/14 §4b mutation refutation; §4 disposition off the adjudicated list; this filing's refusals of credit |
| K12 feedback | this file and its harvested predecessor. **In-repo DOGFOOD/ADOPT declaration: NONE** |

## Counts

Clauses: 6 FIT · 0 FRICTION · 0 BREAK · 0 N/A · 4 UNEXERCISED · 2 INSTANCE-FAILURE
Profile: 5 FIT · 1 FRICTION · 0 BREAK · 0 N/A · 0 UNEXERCISED · 2 INSTANCE-FAILURE
Ledger totals (INSTANCE-FAILURE excluded per kernel §5): **11 FIT · 1 FRICTION · 0 BREAK · 0 N/A · 4 UNEXERCISED**
Plus 3 new instance failures (IF12-IF14) and a status line for each of the first filing's eleven, 3 observations, 2 Untested.
