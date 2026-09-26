# Factory-kernel dogfood filing — conjugal (machine Bachelor) — re-file against r5 / code@r9

project: conjugal
kernel: fleet-factory-kernel r5
profile: code@r9
instance: `coordination/kernel-dogfood/` (S1..S33 declarations + README + `check-ordering.py`) + tools per clause; `KERNEL:` line to be refreshed to `DOGFOOD-PENDING Sol · fleet-factory-kernel r5 · profile code@r9` in `specs/conjugal.md` on the landing branch (bus master carries no `KERNEL:` line; the 2026-09-18 review branch reads `code@r7`); map under `## Instance map`
subjects: 9 end-to-end claimed, each keyed and delivered at the same tree — S1=721e4b15677a579d1fab3fd430a785d7974e243d S13=d44d8fb78b73d505c25d7ac0d3259251ca83bc50 S22=f08000648013d77360d0e75f88d23d84d2965fc8 S25=e62b15efe2e125c83b6399d243364bd86b340471 S26=bf32a3a454e08401064bfb4cda18c207525b0f74 S27=f52c03ac499ab7fbeabacdb8756f53cd1a521646 S29=d4223e59645634d1205ed3419913747659e0beb4 S30=7cafba0c16649dd05027beb949e7b0b79c114f65 S31=831c204a9830893972db7d8cccc029e0eebd1a74; 1 accepted but NOT delivered at its keyed identity, counted zero (S12 keyed d8dc575001d4a84f310a96c8e2a03061506b2ace, delivered inside merge tree 00559844199291ad61474439529d42497b3259d2); 23 delivered-unaccepted or parked, counted zero (S2..S11, S14..S21, S23, S24, S28, S32, S33); receipts under ## Receipts
window: 2026-09-15T23:18Z .. 2026-09-23T03:46Z (S1 declaration conjugal `96d1b3a27` .. S33 outcome conjugal `09557947f`, author dates); this re-run adds 2026-09-18T23:32Z (S12 declaration `63c9a494f`) .. 2026-09-23T03:46Z
health: assurance=UNSATISFIED operability=PRESSURED
providers: claude(claude-opus-5, producer) codex(gpt-6-astra, acceptance key) — key verdicts on S1, S3, S4, S5, S8 r1, S9, S12..S16, S18..S33; terminated without one on S8 r2, S14 r3, S17 r1-r2, S18 r2, S19 r1
posture: conjugal-standard-PARTIAL (0/17 lanes; missing: Designer-Scope 0/1; Designer-Verify 0/1; Lint-Consistency 0/2; Arbiter 0/1; Consolidator 0/1; Panel 0/8; Classifier 0/3)

**Status.** Steward's own filing (§5), re-filed on PROMPT K's revision trigger: the profile moved r7 → r8 (bus `99b72bb`) → r9 (bus `9e23075`, 2026-09-19T21:46:27-05:00), and eighteen subjects (S12, S13, S18..S33) reached an Outcome since the last blob. Revisions quoted from bus `origin/master` `bbf95f8`: kernel `**Status: \`CANDIDATE r5 — DOGFOODING\`.**`; profile `**Profile of** \`specs/fleet-factory-kernel.md\` r5. **Profile revision:** r9.` Kernel whole read (2,850 words by `wc -w`); profile r9 diffed against r7 (`git diff 21d8c3c 9e23075 -- specs/fleet-factory-kernel/profiles/code.md`): r8/r9 changed four fields — subject-identity (path-manifest identity for landings under a moving target), independent-key (execution vs static charters), resource-terminals (environment-only review blocks are typed terminals, not rounds; retain attempts and expenditure), claims (observer-released claims may replace leases). All four are evaluated below.

**Posture** re-computed 2026-09-26 by the R9 tool: `python tools/review-posture/review_posture.py posture <empty dir>` → the line above, `cross_family: NO-CROSS-FAMILY-VALIDATION`, exit 1. No posture role ran in S12..S33; the acceptance key and S22's three subject-selection agents ran outside the roles, no lane credit (R9.4). Unchanged from the prior blob.

**What the ledger may and may not credit.** The previous blob of this filing (`4598b8ed`, `origin/review/conjugal-kernel-2026-09-18`; routed as `8b727203` to arbiter cloudvore, alternate the owner, bus `71e4ff4`) has **no disposition**: the only `conjugal.dispositions.md` on bus master answers blob `3a36f3e6` (`filing_blob: 3a36f3e63b4704c937a9bd4c91fbfac432e27347`). Per PROMPT K's re-run rule every one of its 23 findings, and its four `## Untested` items, is carried **verbatim with its original evidence** under `## Kept findings` and `## Untested`; this re-run's own lines are under `## Clauses` and `## Profile fields`. So this filing carries 46 finding lines for the arbiter: 23 new, 23 kept. **Criterion-1 delta is 0**, and stays 0 until a foreign `.dispositions.md` bound to this blob exists: the steward may not rule on its own filing (§5), and `tools/kernel-e2e.py` reads `PROJECTS WITH >=1 CLOSED : 0` today. Nine end-to-end claims are claims, not ledger credit.

`[BUS]` re-runs from a clone of the landing branch plus Python; `[INLINE]` is Conjugal-side testimony re-runnable only in a Conjugal clone (the `[INLINE]` re-runs below were executed 2026-09-26 at Conjugal `master` `1755502d6`). Exits read unpiped; Conjugal SHAs qualified (Law 6).

## Subjects

Re-run 2026-09-26, `[INLINE]`: `python coordination/kernel-dogfood/check-ordering.py ; echo "exit=$?"` → `SUMMARY subjects=33 ok=24 open=0 failures=0 -> PASS`, exit 0; every row below is from that output or the S-file's `## Outcome`. Delivery at identity is read two ways: (a) the candidate commit sits on `master`'s first-parent history with a single parent (`git rev-list --first-parent master`), and (b) for S22..S31 each candidate SHA is itself an entry of the shared checkout's `refs/remotes/origin/master` reflog, i.e. it was the pushed tip.

| S | Declaration (author, -05:00) | Profile declared | Candidate → identity | Key rounds (class `codex-openai`, `gpt-6-astra`) | Outcome | Path |
|---|---|---|---|---|---|---|
| S12 | `63c9a494f` 09-18 18:32:12 | `code@r8` literal | `0a738a6b4` → `d8dc5750…` | R1 REFUSE, R2 ACCEPT | ACCEPTED; **delivered via merge `7b309cc81`**, not at identity | non-product |
| S13 | `7fe886459` 09-18 18:50:41 | `code@r8` literal | `c6f35501e` → `d44d8fb7…` | R1 ACCEPT | ACCEPTED, delivered at identity (first-parent, linear on `9e7aad0fe`) | non-product |
| S18 | `4dcfed305` 09-21 01:24:35 | command → r9 @ bus `9e23075` | `340a9c23c` → `a111cc6c…` | R1 REFUSE, R2 NO VERDICT, R3 REFUSE | PARKED at ceiling | non-product |
| S19 | `86638d5c0` 09-21 15:59:33 | command → r9 | `b60f3327a` → not recorded | R1 `KEY_UNAVAILABLE_BY_PROVIDER`, R2 REFUSE | PARKED | product |
| S20 | `da95e9121` 09-21 21:32:56 | command → r9 | none cited | R1–R3 REFUSE | PARKED at ceiling; product defect fixed | product |
| S21 | `a625bbcec` 09-21 23:05:38 | command → r9 | none cited | R1–R3 REFUSE | PARKED at ceiling | product |
| S22 | `ae02d5451` 09-22 01:06:51 | command → r9 | `c323c4af7` → `f0800064…` | R1 ACCEPT | ACCEPTED, delivered at identity | non-product |
| S23 | `e0f43f660` 09-22 02:09:36 | command → r9 | none cited | R1–R3 REFUSE | PARKED at ceiling | product |
| S24 | `27b802040` 09-22 02:52:16 | command → r9 | none cited | R1–R2 REFUSE (R3 unspent) | PARKED, bar false of any correct implementation | product |
| S25 | `e16cbda09` 09-22 03:39:22 | command → r9 | `d7e2fc224` → `e62b15ef…` | R1 REFUSE, R2 ACCEPT (one R2 dispatch died on capacity, uncharged) | ACCEPTED, delivered at identity | product |
| S26 | `9af365cdf` 09-22 04:42:25 | command → r9 | `ee4677985` → `bf32a3a4…` | R1 ACCEPT | ACCEPTED, delivered at identity | product |
| S27 | `9ac3630e1` 09-22 05:32:08 | command → r9 | `96fcad8ae` → `f52c03ac…` | R1 ACCEPT | ACCEPTED, delivered at identity | product |
| S28 | `27eee8198` 09-22 07:10:17 | command → r9 | none cited | R1–R3 REFUSE | PARKED at ceiling | product |
| S29 | `3a5903be7` 09-22 14:06:23 | command → r9 | `272be21e3` → `d4223e59…` | R1 ACCEPT | ACCEPTED, delivered at identity | non-product |
| S30 | `5241b36d0` 09-22 15:20:34 | command → r9 | `8cab657f6` → `7cafba0c…` | R1 ACCEPT | ACCEPTED, delivered at identity | product |
| S31 | `a5b496be4` 09-22 16:26:13 | command → r9 | `e93985e54` → `831c204a…` | R1 REFUSE, R2 ACCEPT | ACCEPTED, delivered at identity; round-2 contract flagged (P:code acceptance-evidence) | product |
| S32 | `666b080fb` 09-22 17:55:13 | command → r9 | none cited | R1 REFUSE (R2–R3 unspent) | PARKED, unbaselined no-regression bar | non-product |
| S33 | `a6b9f026d` 09-22 22:23:29 | command → r9 | none cited | R1–R3 REFUSE | PARKED at ceiling, prose overclaims | product |

**S12 — accepted, and the key does not transfer to what was delivered.** S12's Outcome: *"Landed on Conjugal `master` by fast-forward (merge `7b309cc81`, pushed to origin"*. `git cat-file -p 7b309cc81` shows two parents, `7b0ad750b` (the subject branch, containing `0a738a6b4`) and `bb86742db` (the lane-advanced `master`); `git merge-base --is-ancestor 0a738a6b4 bb86742db` → exit 1, so `master` never pointed at the keyed commit, and `git rev-parse 7b309cc81^{tree}` = `00559844…` ≠ `d8dc5750…`. The bars were re-run green on the merged tree, but a green bar is not a key; under the profile (r8 and r9 alike) *"a key on a different subject identity does not transfer"*. Counted zero. S13, declared and landed immediately after on top of `9e7aad0fe` (a descendant of that merge), was a plain fast-forward and is not affected.

**S18..S33 — the declaration shape changed.** From S18 on, the profile line is a procedure (*"**Profile revision:** recompute with `git -C … show origin/master:specs/fleet-factory-kernel/profiles/code.md | grep -i '^\*\*profile revision'`"*), never a value. Resolved here: `git log -1 --before=<declaration author date> origin/master -- specs/fleet-factory-kernel/profiles/code.md` returns bus `9e23075` for every S18..S33 declaration date, and that commit's file reads `**Profile revision:** r9`; no later commit touches the file (bus `bbf95f8`). None of S18..S33 carries a `DELIVERY TARGET (K7):` line; S12 and S13 do (`DELIVERY TARGET (K7): Conjugal \`master\` (the integration branch every lane shares)`).

**Product-path rule.** Nine of the 18 new subjects are product paths (`docs/product/`, `scripts/`, `templates/`, `dashboard/`, `integrations/`, `samples/`); the S-files' own running cumulative reads *"19 of 32 (59%)"* at S33 against a 2-of-3 target. Accepted product subjects: S25, S26, S27, S30, S31 (five); the first product-path acceptances in this workstream.

**Parks.** Nine subjects parked; each names its mechanism and a re-scope direction, none names a resume actor (K8). The mechanisms, quoted from the Outcomes: S18 *"heuristic detection of QUOTED text in a free-text session log"*; S19 *"attribution of embedding evidence to a font by TEXT PROXIMITY"*; S20 *"verifying CONTENT FIDELITY of a rendered document from the rendered artifact alone"*; S21 *"treating REGEX MATCHES OVER GENERATED MARKUP as HTML element structure"*; S23 *"the declared bars were equalities on a function that no test could call"*; S24 *"bar 3 is false of every correct implementation"*; S28 *"a bound applied at one point in a value's life is not a bound on the value"*; S32 *"I declared a no-regression bar without reading its baseline"*; S33 *"the declaration's prose repeatedly asserted more than its measurements"*. In every park the product fix was kept and shipped.

**Outcome-prose defects the mechanical witness caught, recorded rather than smoothed.** S21's Outcome cites its declaration as `86638d5c0` (that is S19's; the first-add of S21's file is `a625bbcec`). S28's cites `9af365cdf` (S26's; S28's first-add is `27eee8198`). S19's gives the declaration author time as 15:28; the first-add is 15:59:33. `check-ordering.py` reads git, not prose, and passes all three. S19, S20, S21, S23, S24, S28, S32 and S33 cite no full candidate identity, which `check-ordering.py` reports as `identity=none`.

### Subjects carried from blob 4598b8ed (verbatim, S1..S17)

**S1 — `S1-resume-prep-landing`, delivered AND accepted, now with a receipt.** `[INLINE]`
Declaration conjugal `96d1b3a27` (author 2026-09-15T18:18:10-05:00; committer 18:22:09, rebased).
Candidate conjugal `ca4dd1346`, identity `721e4b15…` re-measured 2026-09-18 (`rev-parse ca4dd1346^{tree}`;
`merge-base --is-ancestor ca4dd1346 master` → exit 0). S1: *"Accepted by `gpt-6-astra` (class `codex-openai`) bound to
that exact identity."* The arbiter refused criterion-1 credit because that verdict was `[INLINE]`; now a file (`## Receipts`).

**S2..S11 — delivered, NOT accepted, counted zero.** S11: *"K6 NOT OBTAINED, so this counts ZERO, as S2-S10 do."* Refused: S3 ×3, S4 ×2, S9 ×2, S5, S8 r1; S8 r2 *"terminated mid-review by its provider's security filter"*, no
verdict; S2, S6, S7, S11 unkeyed; S10 *"the declared K6 route does not exist"*.
Delivery: S1, S5–S8, S10, S11 fast-forwarded to Conjugal `master` (`merge-base --is-ancestor` exit 0); S2, S4, S9 pushed to bus
`origin/review/conjugal-kernel-2026-09-15` (`tools/fleet-resume-readiness.py`, `tools/arbitration-queue.py`,
`tools/test-kernel-arbitration-route.py`, suites), `[INLINE]`, not carried here. Conjugal-side bars S6–S11 **not re-run**;
each stands as its S-file's `## Outcome` records (S6 *"acceptance bars green"*, S8 *"4-of-4 mutation-proven"*), `[INLINE]`.
Re-run 2026-09-18: `## Ordering witness`; K7 detector census `git ls-files coordination/tools | grep -iE
"deliver|accepted|kernel"` → nothing, exit 1 — NONE.

**S14 — `S14-jev-evidence-shadow-beside-check-ordering`, delivered, NOT accepted, PARKED, counts zero.** Declaration conjugal
`b8f78db0b` (author 2026-09-19T22:08:04-05:00) precedes candidates `f9ea1dc86`, `5185f08c5`, `16eccf6df` (author dates 22:42:17,
23:22:23, 2026-09-20 09:26:32); each fast-forwarded to `master` (`merge-base --is-ancestor` exit 0). Key `gpt-6-astra`
(class `codex-openai`): round 1 REFUSE, round 2 REFUSE on the same mechanism narrowed (patch-versus-narrow adjudication
by three read-only panelists: PATCH), round 3 *`KEY_UNAVAILABLE_BY_PROVIDER`* — the cybersecurity filter terminated the
review while it read the egress-screen fixtures (second instance after S8 r2). Receipts, mechanisms and the wall:
`adjudications/factory-kernel/conjugal-receipts/S14-key-rounds.md`. Bar 1 as declared named a `check-ordering.py --json`
flag that does not exist: NOT MET as written, a declaration defect recorded rather than amended. The subject is the
first Conjugal instance of the fleet Jev shadow-mode standard (bus `specs/fleet-jev-shadow-mode.md`, CANDIDATE r6).

**S15 — `S15-jev-capacity-refusal-replay`, delivered, NOT accepted, PARKED, counts zero.** Declaration conjugal
`efb8ab8fe` (author 2026-09-20T13:53:42-05:00) precedes candidates `9e7e360f9`, `58dd7f8f0`, `e50b0dcda`, `cfdc286d7`
(author dates 14:17:58, 14:28:00, 14:47:14, 14:57:35); each fast-forwarded to `master` (`merge-base --is-ancestor` exit 0).
Key `gpt-6-astra` (class `codex-openai`): three rounds, three REFUSE verdicts, each on a reproduced defect (hard-link
alias; junction TOCTOU + NDJSON parser; truncation-before-validate + unhashable choice), each fixed in the next commit;
the declared three-round budget is spent. Receipts and mechanisms: `adjudications/factory-kernel/conjugal-receipts/S15-key-rounds.md`.
No provider-filter termination this time: the fixture rule (no token-shaped strings) held. Second Conjugal instance of the
fleet Jev shadow-mode standard; its measured deliverable (6 capacity refusals both keyword lists miss) is in the Outcome.

**S16 — `S16-jev-opt-in-vote-salvage-shadow`, delivered, NOT accepted, PARKED, counts zero.** Declaration conjugal
`5dafef1a3` (author 2026-09-20T16:23:42-05:00) precedes candidates `20158cff0`, `a587f2a18`, `4d9baf1de`, `f0c9485a1`
(author dates 17:04:48, 19:18:49, 20:17:12, 21:36:21); each fast-forwarded to `master` (`merge-base --is-ancestor` exit 0).
Key `gpt-6-astra` (class `codex-openai`): three rounds, three REFUSE verdicts, each on a reproduced defect (unvalidated
log destinations/response fields + non-equivalent Law-4 port + unbounded sidecar call; the same mechanism narrowed to
filesystem-identity/alias/NDJSON/response-key validation; two narrower residuals — a two-object sidecar response and a
missing-final-newline log), each fixed in the next commit; the declared three-round budget is spent. No round was
provider-filter terminated. Receipts and mechanisms: `adjudications/factory-kernel/conjugal-receipts/S16-key-rounds.md`.
This is the **first product-path subject** (README rule: two of every three declarations target a product path), done
under the owner's 2026-09-20 in-product ruling and the amended `PRIVACY.md`; its measured deliverable — 2 of 20 salvaged
votes read the other way at confidence ≥ 0.96 — is in the Outcome.

**S17 — `S17-jev-product-hook-python-io-helper`, delivered, NOT accepted, PARKED, counts zero.** Declaration conjugal
`535135396` (author 2026-09-20T22:15:54-05:00) precedes candidate `72b00e182` (author 23:15:25), identity
`62bdfe78ec1a1b12b081dc6e979be7f74e3f77c1`, fast-forwarded to `master` (`merge-base --is-ancestor` exit 0). Key
`gpt-6-astra` (class `codex-openai`): two rounds on identical prompt bytes, both `KEY_UNAVAILABLE_BY_PROVIDER` (cyber
filter, 1 and 2 hits; no verdict line exists); the third round deliberately unspent. The answer to S16's wall (Python
helper, handle-authoritative writes) is delivered and pinned by 22 + 14 assertions and a live opt-in run (20/20 logged,
17 agree, 2 known reversals); the NEW wall is the reviewer class: `codex-openai` cannot finish reading a Conjugal
write-path subject. Owner-side unblock named (security-adjacent review authorisation, or a second K6 independence
class). Receipts and the trap: `adjudications/factory-kernel/conjugal-receipts/S17-key-rounds.md`.

## Clauses

Re-run 2026-09-26 on S12, S13, S18..S33. Each line below is new evidence; the undispositioned line it sits beside is kept verbatim under `## Kept findings`.

K1 | FIT | "A candidate is never accepted on evidence whose only author is its producer" | Nine new acceptances (S12, S13, S22, S25, S26, S27, S29, S30, S31), every key `gpt-6-astra` (class `codex-openai`). The producer is named in the S-file only for S12 and S13 (*"Producer Claude (`claude-opus-5`)"*); S22..S31 say only *"an independence class other than the producer's"*. `[INLINE]` producer identity re-read from the candidates themselves: `git log -1 --format='%(trailers:key=Co-Authored-By,valueonly)'` → `Claude Opus 5` on `0a738a6b4`, `c323c4af7`, `d7e2fc224`, `ee4677985`, `96fcad8ae`, `272be21e3`, `8cab657f6`, `e93985e54`; `c6f35501e` carries none (re-minted for a `Doctrine-Export:` trailer, S13 Outcome). A commit trailer is testimony about the producer, not a receipt | PROOF: an accepted candidate whose trailer or rollout names the key's family as a co-author

K2 | INSTANCE-FAILURE | "Each project keeps one register of what needs the owner and what does not" | `[INLINE]` Still no register: `git ls-files | grep -iE "register|authority"` returns scheduler-registration scripts and files under the frozen `codeConjugal-worktreesprobe-r3/` snapshot, nothing that classifies decisions. Cost in this window: S18's latch reads *"waits for a filing change or owner"* with no named channel; S19 offered a non-model oracle as a key *"as EVIDENCE for an arbiter, not as self-acceptance"* because no register names who may accept on it; S25 changed `scripts/pairprog-scope-match.py` (a security-sensitive path, P:code human-gates) with no register row to consult. No REPLACES | PROOF: a single Conjugal file every other authority text defers to

K3 | INSTANCE-FAILURE | "for one held subject, its claim record and the procedure by which someone other than the claimant decides it stale" | Identity half: all 18 declarations carry the recompute command; 10 Outcomes cite a full tree identity; 8 do not (`check-ordering.py` `identity=none`: S19..S21, S23, S24, S28, S32, S33) — all parked, so no credit turns on it. Claim half: none, at a measured cost. S25's Outcome commit `af0a21d3f`: landing each seam with `git update-ref refs/heads/master` *"moved the branch while the MAIN checkout had master out"*; the repair's awk predicate then restored three files *"a peer lane had recorded as preserve-unstaged, including Luna's BLOCKED-FIRST-RED candidate"*, and *"Unstaged content has no reflog; it is gone."* A claim record on the shared checkout would have been read before that act. No REPLACES | PROOF: a Conjugal claim record naming subject, holder, expiry or stale-rule, and processes

K4 | FIT | "Never exit code, output size or silence" | Negative checks refused in this window, each measured `[INLINE]` in its S-file: S27 `test-create-loop.sh` exit 0 `PASS: 158 assertions` with `splice()` sabotaged (it stubs the renderer); S29 `test-compact-hub.py` exit 0 `PASS: 72` with the containment block removed; S33 `test-samples-update-status.ps1` `PASS: 7`, exit 0, with the changed function replaced by a constant; S28's concurrency assertion passed with the insertion check removed (it ran on an already-saturated server); S19's Type3 bar *"passed vacuously"* on `(no named fonts found)`, exit 0; S18 r2 and S19 r1 recorded the verdict digest as `e3b0c442…b7852b855`, the SHA-256 of zero bytes, rather than reading a missing verdict as silence. `check-ordering.py` passed S21 and S28 whose Outcome prose cites the wrong declaration SHA (`## Subjects`): the witness reads git, not prose | PROOF: a gate here whose exit status is read through a pipe

K5 | FIT | "the profile line recorded before work, and the acceptance receipt bound to the same identity" | Ordering: `check-ordering.py` exit 0, all 18 new declarations precede their first artifact commit by author date (`## Ordering witness`). Profile version: S12 and S13 declare `code@r8` literally, and bus `99b72bb` (last `code.md` change before both) reads r8. S18..S33 declare a command, not a version; resolved to **r9 at bus `9e23075`** for all sixteen by `git log -1 --before=<declaration author date> origin/master -- specs/fleet-factory-kernel/profiles/code.md` (`## Subjects`). The resolution holds only because `code.md` has not changed since `9e23075`; the declarations themselves would read a later revision after the next bump. Acceptance receipts bound to identity: verdict-line SHA-256 per round in each Outcome, published as receipt files (`## Receipts`) | PROOF: a commit to `code.md` on bus `origin/master` dated between `9e23075` and any S18..S33 declaration

K6 | FIT | "Every acceptance includes a key from an independence class other than the producer's" | Nine acceptances, each keyed by `codex-openai` against a `claude-opus-5` producer. S12..S33: 35 charged rounds, 33 verdicts (9 ACCEPT, 24 REFUSE), 2 without a verdict (S18 r2, *"ended with no first line; no cyber-filter signature in the log"*; S19 r1, `KEY_UNAVAILABLE_BY_PROVIDER`, cyber filter, 2 hits), plus one uncharged S25 r2 dispatch that died on *"Selected model is at capacity"*. S19 r1's cause was the prompt, not the subject: asked to *construct* a PDF defeating the checker; re-issued as VERIFY, 0 filter hits, and 0 filter hits in every round S20..S33 — refuting S17's "reviewer class cannot read a write-path subject" reading. Every refusal in S25 and S31 reproduced a defect the declaration missed. S19 offered a non-model oracle (PyMuPDF, 44 of 45 fonts agree) and did not claim it | PROOF: a K6 acceptance here whose key shares the producer's class

K7 | INSTANCE-FAILURE | "the delivery target, and how the project detects an accepted subject that never delivered" | Target: S12, S13 declare `DELIVERY TARGET (K7): Conjugal \`master\``; **S18..S33 declare no target before work** — `master` appears only in Outcome prose (*"Landed on `master` and pushed"*). Delivery at identity closed for S13, S22, S25, S26, S27, S29, S30, S31 (`## Subjects`, first-parent plus reflog). It did not close for S12: accepted, then delivered inside merge `7b309cc81` (tree `00559844…`), which the Outcome calls *"by fast-forward"*. Detector: still NONE that notices this. `check-ordering.py` prints `delivered=yes` for S12 (it tests ancestry, and `0a738a6b4` is an ancestor), and prints `delivered=unwitnessed … note=bus-delivery-no-sha` for S20, S21, S23, S24, S28, S32, S33, which were delivered to Conjugal `master`, not the bus — the note is wrong about where they went. No REPLACES | PROOF: a Conjugal tool that lists accepted subjects whose keyed tree was never a `master` tree, unprompted

K8 | INSTANCE-FAILURE | "Running out of quota means rotating or parking the work that needs inference, never failing the factory closed" | Three events. (a) S18's own defect, observed live: the harvest runner booked `You've hit your monthly spend limit` as a hard fault, kept the attempt, and latched `ATTENTION` where *"no timer clears that latch"* — the factory failed closed on quota. Fixed on `master` at `340a9c23c` (54 of 54 tests) but PARKED unaccepted, so the fix carries no acceptance. (b) S25 r2 capacity error: retried, not charged, non-inference work continued — the clause held, but no rollout, byte size or cost of the failed attempt is recorded. (c) S19 r1 filter kill: typed, zero credit. Park records: nine parks, each names its mechanism and a re-scope; `grep -n -i "resume actor\|resume condition"` over S18..S33 → one hit, S18:96, the promise *"PARKED with the mechanism named and a resume actor"*, which S18's Outcome does not keep | PROOF: a Conjugal park record for any of S18..S33 naming resume condition and actor

K9 | FIT | "the resumability gate's command and its last passing output" | Re-run 2026-09-26, `[INLINE]`: `python coordination/tools/resumability-check.py` → `PASS resumability (docs/architecture/approach-a @ 1755502d6): tree-only resume possible; no live values in RESUME.md`, exit 0. `[BUS]` identity unchanged since the previous blob: `git rev-parse master:coordination/tools/resumability-check.py` = `0f05582128a368ca502f8dc2051b0b8b2ce86da9` = `tools/conjugal-reference/resumability-check.py` on `origin/review/conjugal-kernel-2026-09-18`; last change to the live gate is conjugal `3f08a94e8` (2026-09-15) | PROOF: the live gate exiting 1 at Conjugal `master`

K10 | INSTANCE-FAILURE | "Missing, `unknown` or mismatched account identity makes the inventory stale" | `[INLINE]` `grep -l -i "probed_under\|machine-inventory\|check-cli-auth"` over S12..S33 → S15 only; no S12..S33 dispatch records an inventory re-probe. S18 measured the instance's identity instrument as wrong: `account_identity()` *"hashes the bytes of the credential file, so an ordinary token refresh reads as an account rotation"* — fixed at `340a9c23c`, unaccepted | PROOF: a Conjugal preflight comparing `probed_under` to the live parity fingerprint before a key dispatch

K11 | FIT | "the quoted title line of each rule the project confirms it meets" | `## R1–R9` quotes each title; the posture line was re-computed by the R9 tool this run (`## Status`, exit 1, output identical to the previous blob). Three Outcome-prose errors (S19, S21, S28) are disclosed in `## Subjects` rather than corrected silently | PROOF: a rule below this filing violates

K12 | INSTANCE-FAILURE | "The steward harvests every filing and answers each one" | `[BUS]` re-run 2026-09-26 at bus `bbf95f8`: `python tools/harvest-status.py factory-kernel ; echo "exit=$?"` → `filings=9`, `conjugal STALE blob=4598b8ed ref=origin/review/conjugal-kernel-2026-09-18 findings=23 untested=0`, `open=1`, exit 0; `python tools/kernel-e2e.py` → `PROJECTS WITH >=1 CLOSED : 0`, `ledger : 19 rows over 9 projects`, `OPEN (1): conjugal STALE`, `VERDICT: MEMBERS DUE`, exit 0. The blob routed to cloudvore on 2026-09-18 (`71e4ff4`) has had no disposition for eight days, and four later commits made it `STALE`. S22 (accepted) makes the runner speak when a self-filing *has* been dispositioned; its declaration assigned the ledger append to *"S23"*, but S23 became a CLI-parsing subject and the append was never declared, so the steward row is still hand-written — the gap the previous blob filed. No mechanism escalates a routed self-filing to the named alternate (the owner) | PROOF: a runner run id that appended a ledger row for a steward filing

## Profile fields

P:code subject-identity | INSTANCE-FAILURE | "git tree OID of the candidate commit as it will be delivered, after any merge with the delivery target; a key on a different subject identity does not transfer" | S12: keyed `d8dc5750…`, delivered inside merge `7b309cc81` (tree `00559844…`); its bars were re-run on the merged tree, which is not a key. r9's alternative — a path manifest *"declare[d], before review"* — was available and not declared. Eight other acceptances were delivered as the exact keyed commit (`## Subjects`) | PROOF: a K6 verdict naming tree `00559844199291ad61474439529d42497b3259d2`

P:code artifact-store | FIT | "git (shared checkout or worktrees); build outputs are not the subject" | Every subject identity is a tree OID. S31 regenerated a tracked build output (`docs/product/conjugal-roadmap-2026-09-22-5k.png`, `c4818569` → `f1b87ce8`) outside its declared artifact set and recorded it in the Outcome, turning it into a bar (*"the PNG hash is UNCHANGED"*) rather than a subject | PROOF: a subject whose identity is a build output

P:code determinism-class | INSTANCE-FAILURE | "deterministic by default; flaky suites are declared per test, never silently retried" | S32: `test-context-handoff-obligation.py` measured 41 pass / 3 fail on an untouched tree; *"Exactly ONE of the three scenarios … passed on a re-run with no relevant change"*; no test is declared flaky, and the re-run is how it was found. S31 measured determinism before asserting it (*"Two consecutive renders are byte-identical"*), the pattern the field asks for | PROOF: a per-test flaky declaration in Conjugal

P:code acceptance-evidence | INSTANCE-FAILURE | "Before work, bind the acceptance contract by digest, including checks, harness limits, review scope, round budget and round-closing rule; the same contract judges every round" | Improved: every S18..S33 declaration names a round budget (*"Three rounds reserved"*) and a closing rule (the three-round ceiling); S24 and S32 parked rather than rewording a false bar (README *"A bar that turns out to be wrong is a park, not an edit"*). Not met: no declaration binds its contract by digest, and three contracts moved after declaration. S33's bars 1–2 changed fixture `go` → `git` in candidate commit `aec8d157a`, after declaration `a6b9f026d`, and its mutation paragraph changed after round 1 (`9c923f176`). S32's bar 5 *"has already been corrected twice before any key round"* (`260d966d2`, `fe7f76b76`). S31's Outcome says bar 5 *"became 'run `build.py` and the PNG hash is UNCHANGED'"* for round 2, while `git log` shows the declaration file untouched between declaration and Outcome — so which contract round 2 judged is not recoverable from the tree | PROOF: a digest of S31's round-2 contract equal to the digest of its declared bar 5

P:code independent-key | INSTANCE-FAILURE | "Review-key charters declare execution or static review before dispatch. Execution charters require an execution-capable disposable environment" | New r9 sentence. No S12..S33 key budget declares a charter; every key executed commands (*"The key re-ran every bar itself"*, S12, S13, S22) from the shared Conjugal checkout (`codex exec … --cd "C:\code\Conjugal"`, S13), not a disposable environment. S23's key left *"a temporary review directory under `%TEMP%` its own cleanup was refused permission to remove"*. The class half is FIT and a restatement of K6 (no separate credit) | PROOF: an S-file key budget declaring `charter: execution` with a disposable environment

P:code resource-terminals | INSTANCE-FAILURE | "parked work names its resume condition and the actor who can satisfy it … Environment-only review blocks are typed terminals, not subject verdicts or completed rounds; retain attempts and expenditure" | Nine parks, no resume condition or actor (K8). S18 r2 (no verdict, cause unknown) was charged as round 2 of 3 toward the ceiling; S25 r2's capacity death was correctly not charged but its attempt and expenditure were not retained. Owner-only resume conditions: none sent, since no escalation channel exists (K2) | PROOF: a park record under `coordination/kernel-dogfood/` naming a resume actor

P:code delivery-target | INSTANCE-FAILURE | "integration branch via the project's landing path … Stricter instance closure mechanisms and their budgets are declared before work" | S18..S33 declare no target (K7). The landing path used in S25 — `git update-ref refs/heads/master` against a checkout with `master` checked out — staged phantom deletions in the main checkout and its repair destroyed a peer's unstaged candidate (K3). The previous blob's `merge-tree --write-tree` + `git merge --ff-only` path is not the one S25 used | PROOF: a Conjugal landing that swept or destroyed a peer's file

P:code human-gates | INSTANCE-FAILURE | "releases, security-sensitive paths, frozen bytes, and anything the project's register lists" | S25 (`scripts/pairprog-scope-match.py`) and S26 (the untrusted-peer fence in `scripts/render-parallel-prompt.sh`) are security-sensitive paths, accepted by a model key alone with no register to say whether a human gate applies (K2) | PROOF: a register row naming the human verifier for `scripts/pairprog-scope-match.py`

P:code budgets | INSTANCE-FAILURE | "wall time per suite, provider calls per subject; review rounds also report dispositions completed and subject changes, including zero, plus window counts" | From the S-files, S12..S33: key rounds S12 2, S13 1, S18 3, S19 2, S20 3, S21 3, S22 1, S23 3, S24 2, S25 2 (+1 uncharged), S26 1, S27 1, S28 3, S29 1, S30 1, S31 2, S32 1, S33 3 = 35 charged, 33 verdicts. Window: accepted 9, delivered at identity 8 new (9 with S1), parked 9, accepted-undelivered-at-identity 1 (S12, age 8 days, blocker: none tracked). Wall time now observed for some suites (S13 key discover 508 s; S21 >600 s → ~135 s after memoising; S29 a 600 s timeout, exit 124, re-run at 1800 s; S32 ~50 s per bar) but not per suite for all; dispositions completed on the previous blob: 0 | PROOF: a Conjugal S-file recording wall time for every suite it cites

P:code claims | INSTANCE-FAILURE | "A mutable checkout another project executes from is itself a claimed subject … Read-only reviewer or adjudicator access requires enforced filesystem/process boundaries" | No claim or lease exists (K3); the S25 landing destroyed a peer lane's unstaged candidate in the shared checkout. Keys ran in that checkout with no enforced boundary; S13 audited `status --porcelain` empty and identity re-read before and after — the only before/after audit, and narrower than the field's list (no index flags, refs, reflogs, stash or untracked hashes) | PROOF: a claim record read before a Conjugal `update-ref` on `master`

P:code dispatch-preflight | INSTANCE-FAILURE | "the spending tool runs the project's resume gate before dispatch and retains its result, the inventory snapshot and digest, and account-parity evidence" | Unchanged: all 36 S12..S33 key dispatches were hand-run `codex exec`; none retains a resume-gate result, inventory digest or parity evidence | PROOF: a Conjugal dispatch receipt carrying an inventory digest

## Kept findings — blob 4598b8ed, undispositioned (verbatim)

Carried byte-for-byte from `origin/review/conjugal-kernel-2026-09-18:adjudications/factory-kernel/conjugal.md` (blob `4598b8ed`), with the `**Status.**` paragraph they cite as `## Status`. No arbiter has answered them, so none is withdrawn, re-verdicted or merged into a line above; where a line above disagrees with one here, both stand for the arbiter. Revision references inside them (`r7`, `r8 re-run owed`) are theirs, not this filing's.

### Status (blob 4598b8ed)

**Status.** Steward's own filing (§5). `assurance=UNSATISFIED` maps to admitted required-predicate failures: acceptance-contract binding (P:code acceptance-evidence), inventory freshness (K10), dispatch evidence (P:code dispatch-preflight), claims (K3), park records (K8); `operability=PRESSURED`: S8 r2 provider kill, S10 no K6 route, ten unaccepted deliveries. Posture computed by `python tools/review-posture/review_posture.py posture <empty dir>` (exit 1): no posture role ran; the acceptance key and the 2026-09-18 read-only adversarial review by `gpt-6-astra` ran outside its roles, no lane credit (R9.4). Revisions quoted: kernel `**Status: \`CANDIDATE r5 — DOGFOODING\`.**`; profile `**Profile revision:** r7.` **Profile moved to r8** (bus `99b72bb`, during landing; base `337e47c` reads `**Profile revision:** r8.`): r8 adds review-key charters (execution vs static) and environment-only review blocks as typed terminals; not evaluated here, r8 re-run owed (PROMPT K §6). Dispositions (`arbiter: cloudvore`, bus `dc2a719`): `## Dispositions honoured`. `[BUS]` re-runs from a clone of this branch plus Python; `[INLINE]` is quoted Conjugal-side testimony. Exits read unpiped; Conjugal SHAs qualified (Law 6).

### Clauses (blob 4598b8ed)

K1 | FIT | "A candidate is never accepted on evidence whose only author is its producer" | ADOPTED. Producer `claude-opus-5`, key `gpt-6-astra`, six refusals then acceptance. `[BUS]` `grep -n "porcelain\|untracked-files\|ignore-submodules\|assume-unchanged\|skip-worktree" bootstrap/session-checkpoint.py` returns the pins the key forced (authorship not established by the grep). The receipt identifies the accepting model and the extraction agent only; producer identity and completion evidence are `[INLINE]` testimony (S1 file), so no verified credit for the producer half | PROOF: an acceptance here whose producing and accepting actors resolve to one independence class

K2 | INSTANCE-FAILURE | "Each project keeps one register of what needs the owner and what does not" | `[INLINE]` Still no single register. Cost: S3 declared a bus artifact Conjugal may not write (*"itself the K2 finding"*); S10: *"the register that would name a human verifier does not exist in this repo"*. No REPLACES | PROOF: a single Conjugal file every other authority text defers to

K3 | INSTANCE-FAILURE | "for one held subject, its claim record and the procedure by which someone other than the claimant decides it stale" | Identity half held (every S-file carries `RECOMPUTE: … rev-parse <candidate>^{tree}`). Claim half, r5's new observable, has nothing: the shared checkout *"is itself a claimed subject"* (disposition) and no lease existed (S8: *"four lane sessions plus scheduled floors share that checkout"*). No REPLACES | PROOF: a Conjugal claim record naming subject, holder, expiry, processes

K4 | FIT | "Never exit code, output size or silence" | ADOPTED. `[BUS]` files carried from `origin/review/conjugal-kernel-2026-09-15` (never on bus master), sha256 `3497a5a32dbb91d87bd4887def890f08d68e632ec9c070ecd5ae27aafbcec053`; 2026-09-18: `python bootstrap/test-session-checkpoint.py ; echo "exit=$?"` → 19 cases, 113 `ok`, `PASS session-checkpoint`, exit 0; delete `"-z", ` at line 177 → exit 1, 103 ok, `FAIL session-checkpoint: 10 check(s) failed`: `new path recorded`, `no unsplit arrow entry`, `listed path resolves on disk: tracked.txt -> renamed.txt`, `the spaced path is actually recorded`, `no quote characters survive into a path`, `listed path resolves on disk: "a file.txt"`, `exact non-ASCII path recorded`, `no C-escape recorded`, `listed path resolves on disk: "caf\303\251.txt"`, `the real untracked file is reported`; restored → 113 ok, exit 0. Negative cases: S5 *"I took the BACKGROUND WRAPPER's exit code … as the test's"*; S7, S8, S10, S11 one hazard (green checks that never tested what they named), filed as a TRAPS row | PROOF: a gate here whose exit status is read through a pipe

K5 | FIT | "the profile line recorded before work, and the acceptance receipt bound to the same identity" | ADOPTED for S1; eleven declarations precede their code; S4–S11 carry `ORDERING: read precedence from AUTHOR dates … never committer dates`. r5 K5 names no date; `review/conjugal-kernel-narrow-corrections-2026-09-17` proposes the AUTHOR-date sentence. Rebased witness: conjugal `96d1b3a27` author 18:18:10 / committer 18:22:09 (pre-rebase twin `f1a9a9dc8`, same patch-id, not on `master`, not cited); rest under `## Ordering witness` | PROOF: a declaration commit touching its own declared artifact set

K6 | FIT | "Every acceptance includes a key from an independence class other than the producer's" | S1 FIT (ADOPTED; receipt `66034ac7…`). S2..S11: ten delivered, zero accepted; every refusal reproduced a defect — the clause's intended cost. One dispatch ended with **no verdict** (S8 r2, *"No verdict was produced: not an accept, not a refusal."*); the profile's *"independent key unavailable: typed terminals"* covers it and the missing park record is K8. S10's CORRECTION: the CI route is no independence class here (*"`CI_RUNS_ON` = [self-hosted …] … no branch protection"*). Proposed kernel wording moved to `## Untested` 2 | PROOF: a K6 acceptance here whose key shares the producer's class

K7 | INSTANCE-FAILURE | "how the project detects an accepted subject that never delivered" | Detector still NONE (§3), at a cost: S8's first K7 section, *"These commits are not on master"* — S6, S7, S8 candidates believed delivered, found by hand, later fast-forwarded. Closed deliveries closed as one transaction (S11: *"the shared checkout saw only a ref advance"*). No REPLACES | PROOF: a Conjugal tool that lists accepted-but-undelivered subjects unprompted

K8 | INSTANCE-FAILURE | "Running out of quota means rotating or parking the work that needs inference" | Event: S8 r2, key *"terminated mid-review by its provider's security filter"*, zero credit; non-inference work continued. What failed: **no S-file records a park record** naming resume condition and actor — `grep -i "resume condition\|park" coordination/kernel-dogfood/S*.md` → no match. Health. Correction: S11:158 says the filter killed S8 AND S10; S10's file records no dispatch — one kill | PROOF: a Conjugal park record for S8 naming resume condition and actor

K9 | FIT | "the resumability gate's command and its last passing output" | ADOPTED-CONDITIONAL; condition *"publish the live gate's identity alongside the copy"* is met **now, on this branch, and was not before**: the bus copy was blob `46aaa31b…` (bus `2a1120e`, 2026-09-13; 157 lines), lacking the `SCRIPT_GENERATED` block Conjugal `3f08a94e8` (2026-09-15T10:48:13-05:00) added (live 177 lines), so **the prior K9 [BUS] claim about the script-generated distinction was false**. Now a byte copy of Conjugal `master:coordination/tools/resumability-check.py`; `sha256sum` on both = `a9e00b8f60efdcdd5ff6889ec3cf7f8fbd98e24535119fcb1eb026d0ededdd25`; `[BUS]` `git hash-object tools/conjugal-reference/resumability-check.py` → `0f05582128a368ca502f8dc2051b0b8b2ce86da9` = the Conjugal `master` blob. Live gate at Conjugal `master` `6cb358d43`, `[INLINE]`: `python coordination/tools/resumability-check.py` → `PASS resumability (docs/architecture/approach-a @ 6cb358d43): tree-only resume possible; no live values in RESUME.md`, exit 0 (the bus copy exits 1 here: no Conjugal `RESUME.md`) | PROOF: the live gate exiting 1 at Conjugal `master`

K10 | INSTANCE-FAILURE | "Missing, `unknown` or mismatched account identity makes the inventory stale" | `[INLINE]` No S-file records a re-probe of `~/.claude/machine-inventory.yaml` under the current account before the `gpt-6-astra` dispatches; parity is proved at session start, freshness is not | PROOF: a Conjugal preflight comparing `probed_under` to the live parity fingerprint

K11 | FIT | "the quoted title line of each rule the project confirms it meets" | Prior evidence withdrawn (self-certifying); offered: `## R1–R9`; `harvest-status.py` flagged the previous filing (blob `3a36f3e6`) `POSTURE-NOT-R9-COMPUTED`; this filing's posture line is tool-computed | PROOF: a rule below this filing violates

K12 | INSTANCE-FAILURE | "The steward harvests every filing and answers each one" | ADOPTED and answered (20/20). (a) Prior K12 `[BUS]` outputs REFUTED (filings=3 not 8). `[BUS]` re-run 2026-09-18 at base `337e47cf0cd1f3628eaae1fe603fe1627a2f4543`: `python tools/harvest-status.py factory-kernel ; echo "exit=$?"` → `filings=9`, `conjugal HARVESTED blob=3a36f3e6 ref=origin/review/conjugal-kernel-2026-09-15 findings=20 untested=0 … flags=POSTURE-NOT-R9-COMPUTED`, `open=0`, exit 0 — **the previous filing's status** (blob `3a36f3e6`), no HARVESTED credit transfers to this blob; `python tools/kernel-e2e.py` → `ledger : 16 rows over 9 projects`, `CLOSED END-TO-END SUBJECTS : 0`; revision lines 3 quoted in `## Status`. (b) Ledger-row gap: §5, *"Each harvest appends one row per filing to … HARVESTS.md (steward-written)"*; Conjugal's runner drops the self-filing at `eligible()` (`harvest_runner.py:160`), so a foreign-arbitrated filing gets **no row from any automation** — appended by hand in bus `68b6c69`. §5 is satisfiable, so the instance failed a clause it could meet. Health | PROOF: a runner run id that appended a ledger row for a steward filing

### Profile fields (blob 4598b8ed)

P:code subject-identity | FIT | "git tree OID of the candidate commit as it will be delivered, after any merge with the delivery target" | Identity computed for all eleven (`## Ordering witness`). The prior author-vs-committer FRICTION is ADOPTED-CONDITIONAL on another `code` bench, not re-filed, so no REPLACES; rebased anchors for that bench: S3 amendment `e71c88683` (author 20:21:56, committer 20:24:08), S1 declaration `96d1b3a27` (18:18:10 / 18:22:09) | PROOF: a Conjugal declaration whose precedence survives a rebase read from committer dates

P:code acceptance-evidence | INSTANCE-FAILURE | "Before work, bind the acceptance contract by digest, including checks, harness limits, review scope, round budget and round-closing rule" | All eleven subjects were declared under `code@r4`, whose weaker anchor S1 met (three checks at conjugal `ca4dd1346`; that acceptance stands under K6). Against r7: every S-file pins and baselines its checks; none binds the contract by digest or names a round budget or closing rule — S4's rounds *"against a bar nobody ever wrote down"* are the cost. Retrospective inspection is not execution under a predeclared r7 contract. Health | PROOF: an S-file whose acceptance section was edited after its first key round

P:code independent-key | FIT | "a verifier from another model family (R3)" | Restatement of K6, kept because §4 asks a line per exercised field; **no separate ledger credit** (prior FIT REJECTED as restatement) | PROOF: as K6

P:code resource-terminals | INSTANCE-FAILURE | "parked work names its resume condition and the actor who can satisfy it" | S8 r2 is the typed terminal *"independent key unavailable"*, zero credit, but no park record names a resume condition or actor; no escalation channel exists (K2). Health | PROOF: a park record for S8 or S10 under `coordination/kernel-dogfood/`

P:code delivery-target | FIT | "integration branch via the project's landing path" | Landing path is a command in S8/S11 (`merge-tree --write-tree` census, then `git merge --ff-only`); closed for S1, S5–S8, S10, S11 | PROOF: a Conjugal landing that swept a peer's staged file

P:code dispatch-preflight | INSTANCE-FAILURE | "the spending tool runs the project's resume gate before dispatch and retains its result, the inventory snapshot and digest, and account-parity evidence" | No dispatch tool retains any of it; every `codex exec` was hand-run. Health | PROOF: a Conjugal dispatch receipt carrying an inventory digest

P:code claims | INSTANCE-FAILURE | "A mutable checkout another project executes from is itself a claimed subject" | The clause arose on every shared-checkout landing; no lease existed. Same fact as K3 | PROOF: as K3

P:code human-gates | INSTANCE-FAILURE | "the register is reachable from every session checkout … names an owner-facing escalation channel" | S8/S10 touch security-sensitive paths (`scripts/auto-approve-gate.sh`, `scripts/pairprog-scope-match.py`) this field routes to the register; S10: *"the register … does not exist"* (K2) | PROOF: a register row naming the human verifier for `scripts/auto-approve-gate.sh`

P:code budgets | INSTANCE-FAILURE | "wall time per suite, provider calls per subject; review rounds also report dispositions completed and subject changes, including zero, plus window counts of subjects accepted, delivered, parked and closed undelivered, with age and blocker for accepted-undelivered work" | From the S-files: key dispatches S1 7, S3 3, S4 2, S5 1, S8 2 (one no-verdict), S9 2, others 0 — 17 dispatches, 16 verdicts; window: accepted 1, delivered 11, parked 0 recorded, closed-undelivered 0, accepted-undelivered 0; dispositions completed on the prior filing 20. **Not observed:** wall time per suite, provider calls beyond key dispatches, per-round subject-change counts. Health | PROOF: a Conjugal S-file recording suite wall time

P:code artifact-store | FIT | "git (shared checkout or worktrees); build outputs are not the subject" | Every subject is a git commit, identity a tree OID; no runtime subject exercised, evidence-store clause not observed | PROOF: a subject whose identity is a build output

P:code determinism-class | INSTANCE-FAILURE | "deterministic by default; flaky suites are declared per test, never silently retried" | No S-file declares a flaky test; S6's preview bar ran 134 s against a 120 s `spawnSync` ceiling, neither declared flaky nor made deterministic. Retries: not observed | PROOF: a per-test flaky declaration in Conjugal

## Instance map

`[INLINE]` unless `→ bus`. K1 `codex exec -m gpt-6-astra`; producer from candidate trailers · K2 **NONE** · K3 `coordination/kernel-dogfood/S*.md` recompute commands; **claims NONE** · K4 mutation-proven suites per S-file; sabotage-proven anchors (S27, S29, S30, S33) · K5 `coordination/kernel-dogfood/` + `check-ordering.py` (author-date witness); profile version **recorded as a command** since S18 · K6 `codex exec` key; **no CI or human route**; non-model oracle offered once (S19 `oracle-check.py`), not a declared route · K7 `master` via fast-forward push; **target undeclared S18..S33; detector NONE** (`check-ordering.py` tests ancestry, not delivered identity) · K8 `coordination/harvest/harvest_runner.py` capacity classifier (S18, delivered, unaccepted); **park record NONE** · K9 `coordination/tools/resumability-check.py` + `session-checkpoint.py` `Stop` hook (→ bus copies, unchanged) · K10 `coordination/tools/check-cli-auth.py`; **inventory freshness NONE** · K11 this filing · K12 `coordination/harvest/harvest_runner.py` + task `\Conjugal-Harvest-Steward`; dispositioned-self-filing note (S22); **self-filing ledger row NONE**.

Previous map (blob `4598b8ed`), verbatim, for the kept lines that cite it:

`[INLINE]` unless `→ bus`. K1 `codex exec -m gpt-6-astra` · K2 **NONE** · K3 `coordination/kernel-dogfood/S*.md` identities; **claims NONE** · K4 mutation-proven suites (→ bus `bootstrap/test-session-checkpoint.py`) · K5 `coordination/kernel-dogfood/` · K6 `codex exec` key; **no CI or human route** (S10) · K7 `merge-tree --write-tree` census + `git merge --ff-only`; **detector NONE** · K8 **park record NONE** · K9 `coordination/tools/resumability-check.py` + `session-checkpoint.py` `Stop` hook (→ bus copies, refreshed here) · K10 `coordination/tools/check-cli-auth.py`; **inventory freshness NONE** · K11 this filing · K12 `coordination/harvest/harvest_runner.py` + task `\Conjugal-Harvest-Steward`; **self-filing ledger row NONE**.

## Ordering witness

Author dates (`git log --date=iso-strict`; day of 2026-09, `-05:00`); declaration = first-add of `S<n>-*.md`, each on
Conjugal `master`; trees match the S-files. Declaration precedes candidate in all eleven. S2 and S5 cite
no candidate SHA in their files; the first-add commits of their artifacts are used.

| S | Declaration (author) | Candidate (author) |
|---|---|---|
| S2 | conjugal `96d1b3a27` 15 18:18:10 | bus `06c1b39` 15 18:31:49 |
| S3 | `3f0abdee9` 15 20:15:06 (amend `e71c88683` 20:21:56) | bus `57a3356` 20:23:52 |
| S4 | `a8efa90f4` 16 01:30:45 | bus `18d7ceb` 16 17:39:45 |
| S5 | `ab1ce9b2e` 16 07:33:14 | `dfaa928e1` 16 07:43:52 |
| S6 | `c45e7255e` 16 10:16:44 | `5308b323a` 16 10:41:20 |
| S7 | `f59c3fcda` 16 10:53:34 | `ca9772ac8` 16 11:05:19 |
| S8 | `e82ad9433` 16 11:19:53 | `36da13f95` 11:28:22 → `5d51a7b29` 17:23:15 |
| S9 | `cffac8484` 16 17:05:51 | bus `d825e9a` 16 17:39:46 |
| S10 | `7db58b05a` 16 17:54:12 | `a34f929a8` 16 18:02:28 |
| S11 | `b7128246e` 17 12:59:50 | `c0f033ff6` 17 13:13:19 |

Ancestry: S5–S8, S10, S11 on Conjugal `master` (exit 0); bus candidates on `origin/review/conjugal-kernel-2026-09-15` only.

New rows, S12..S33 (re-run 2026-09-26, `check-ordering.py` output; declaration = first add of the S-file, candidate as that tool reads it; day of 2026-09, `-05:00`):

| S | Declaration (author) | Candidate (author) | Tool row |
|---|---|---|---|
| S12 | `63c9a494f` 18 18:32:12 | `0a738a6b4` 18 18:43:52 | OK, ACCEPTED |
| S13 | `7fe886459` 18 18:50:41 | `c6f35501e` 18 19:22:26 | OK, ACCEPTED |
| S18 | `4dcfed305` 21 01:24:35 | `340a9c23c` 21 02:22:39 | OK |
| S19 | `86638d5c0` 21 15:59:33 | `b60f3327a` 21 16:22:27 | OK, `identity=none` |
| S20 | `da95e9121` 21 21:32:56 | none cited | NO-CANDIDATE-CITED |
| S21 | `a625bbcec` 21 23:05:38 | none cited | NO-CANDIDATE-CITED |
| S22 | `ae02d5451` 22 01:06:51 | `c323c4af7` 22 01:24:16 | OK, ACCEPTED |
| S23 | `e0f43f660` 22 02:09:36 | none cited | NO-CANDIDATE-CITED |
| S24 | `27b802040` 22 02:52:16 | none cited | NO-CANDIDATE-CITED |
| S25 | `e16cbda09` 22 03:39:22 | `d7e2fc224` 22 03:54:46 | OK, ACCEPTED |
| S26 | `9af365cdf` 22 04:42:25 | `ee4677985` 22 04:48:09 | OK, ACCEPTED |
| S27 | `9ac3630e1` 22 05:32:08 | `96fcad8ae` 22 05:42:27 | OK, ACCEPTED |
| S28 | `27eee8198` 22 07:10:17 | none cited | NO-CANDIDATE-CITED |
| S29 | `3a5903be7` 22 14:06:23 | `272be21e3` 22 14:38:53 | OK, ACCEPTED |
| S30 | `5241b36d0` 22 15:20:34 | `8cab657f6` 22 15:49:40 | OK, ACCEPTED |
| S31 | `a5b496be4` 22 16:26:13 | `e93985e54` 22 17:00:13 | OK, ACCEPTED |
| S32 | `666b080fb` 22 17:55:13 | none cited | NO-CANDIDATE-CITED |
| S33 | `a6b9f026d` 22 22:23:29 | none cited | NO-CANDIDATE-CITED |

`SUMMARY subjects=33 ok=24 open=0 failures=0 -> PASS`, exit 0. Delivery at identity (first-parent membership, single parent, and for S22..S31 an `origin/master` reflog entry naming the candidate): S13, S22, S25, S26, S27, S29, S30, S31 yes; S12 no (merge `7b309cc81`). Every candidate above is an ancestor of `origin/master` (`merge-base --is-ancestor` exit 0).

## Receipts

Kept from blob `4598b8ed`, verbatim:

- **S1 acceptance receipt:** `adjudications/factory-kernel/conjugal-receipts/S1-astra-acceptance.md` — `VERDICT: ACCEPTED identity=721e4b15677a579d1fab3fd430a785d7974e243d key=gpt-6-astra class=codex-openai`, six preceding refusals, actors, method, time; re-run evidence is quoted in place. SHA-256 `66034ac71082662b3f86cb4bef1771e750c85d41aea6a2f951487cf773017ca2` (`sha256sum` on that path). Read-only adversarial review by `gpt-6-astra` 2026-09-18 ruled the excerpt a receipt under §1; its 9 findings applied. Both re-read commands were repaired and run against the seven local logs: verdict line and excerpt digest `4cfd7357…` reproduced (exit 0); `turn_context` model `gpt-6-astra` on all seven (exit 0).
- **S14..S17 key-round receipts** stay as published on `origin/review/conjugal-kernel-2026-09-18`: `adjudications/factory-kernel/conjugal-receipts/S14-key-rounds.md`, `S15-key-rounds.md`, `S16-key-rounds.md`, `S17-key-rounds.md` (cited by the kept `## Subjects` paragraphs).

New in this re-file, one file per subject, each carrying the verbatim verdict record per round with the rollout file's SHA-256 and the verdict record's SHA-256 (README: *"A subject closes on the key's receipt, never on prose"*). The column below is the digest each S-file's Outcome PRINTS, kept as a locator only. It is **not** the receipt digest for S18..S33: see the reconciliation paragraph after the table.

| Receipt | Rounds | Verdict digests as the S-file prints them |
|---|---|---|
| `adjudications/factory-kernel/conjugal-receipts/S12-key-rounds.md` | R1 REFUSE, R2 ACCEPT | `1715abcb07e25f04cffb09177afbb116c31e8d19eeb51b3d6cd46e387e706ff5`, `223a9cf4319a37b1d73f04cc911d035c845137f30086f3cf95d193e0c6f356cf` |
| `adjudications/factory-kernel/conjugal-receipts/S13-key-rounds.md` | R1 ACCEPT | `23ddcd4ed3291be01a55a4ebd7ff77ba2965b3b05b950d8fc2e740cef4213da0` |
| `adjudications/factory-kernel/conjugal-receipts/S18-key-rounds.md` | R1 REFUSE, R2 no verdict, R3 REFUSE | `4ac382ba…fe47d`, `e3b0c442…b855` (zero bytes), `44cb0c69…eb16` |
| `adjudications/factory-kernel/conjugal-receipts/S19-key-rounds.md` | R1 `KEY_UNAVAILABLE_BY_PROVIDER`, R2 REFUSE | `e3b0c442…b855` (zero bytes), `78b4b692…9a14` |
| `adjudications/factory-kernel/conjugal-receipts/S20-key-rounds.md` | R1–R3 REFUSE | `4dad5aaa…da2b`, `d506375a…7cb5`, `d6ee6346…f0c7` |
| `adjudications/factory-kernel/conjugal-receipts/S21-key-rounds.md` | R1–R3 REFUSE | `93783229…`, `4a1a5e8d…`, `60945aff…` (48-hex prefixes in the S-file) |
| `adjudications/factory-kernel/conjugal-receipts/S22-key-rounds.md` | R1 ACCEPT | `6107deba348b56e667e26db242413a739afbc39b7d7fa6b9b34246b2a77a505a` |
| `adjudications/factory-kernel/conjugal-receipts/S23-key-rounds.md` | R1–R3 REFUSE | `1a71571b…`, `b33d213c…`, `0df125a1…` (40-hex prefixes) |
| `adjudications/factory-kernel/conjugal-receipts/S24-key-rounds.md` | R1–R2 REFUSE | `35f6699f…`, `c6df3452…` |
| `adjudications/factory-kernel/conjugal-receipts/S25-key-rounds.md` | R1 REFUSE, R2 ACCEPT | `ea1e559e…`, `730ba971…` |
| `adjudications/factory-kernel/conjugal-receipts/S26-key-rounds.md` | R1 ACCEPT | `944f0fab…` |
| `adjudications/factory-kernel/conjugal-receipts/S27-key-rounds.md` | R1 ACCEPT | `a806c206…` |
| `adjudications/factory-kernel/conjugal-receipts/S28-key-rounds.md` | R1–R3 REFUSE | `d448de17…`, `c6e8e2e1…`, `30cf3759…` |
| `adjudications/factory-kernel/conjugal-receipts/S29-key-rounds.md` | R1 ACCEPT | `48ef8622…` |
| `adjudications/factory-kernel/conjugal-receipts/S30-key-rounds.md` | R1 ACCEPT | `4b9f7deb…` |
| `adjudications/factory-kernel/conjugal-receipts/S31-key-rounds.md` | R1 REFUSE, R2 ACCEPT | `d17a767b…`, `aef8cc8e…` |
| `adjudications/factory-kernel/conjugal-receipts/S32-key-rounds.md` | R1 REFUSE | `ecc609c5…` |
| `adjudications/factory-kernel/conjugal-receipts/S33-key-rounds.md` | R1–R3 REFUSE | `1b01331c…`, `b24fa04e…`, `40140d8c…` |

**Reconciliation, measured 2026-09-26 (INSTANCE-FAILURE on the receipt definition, kernel §1).** Only S12 R1–R2 and S13 R1 reproduce the Outcome-printed digest from the Codex rollout. For S18..S23 the printed digest is of the producer's machine-local `codex exec` stdout capture (CRLF, cp1252-mangled), for S24 it is of the PROMPT sent to the key (mislabelled as a verdict), and for S25..S33 it is of the whole console transcript (60–185 KB). Those captures hold full prompts and machine paths and are deliberately NOT published. Each receipt file therefore carries its own digests recomputed from the rollout bytes (whole-file SHA-256, final-answer excerpt SHA-256, verdict-line SHA-256) and a per-round reconciliation table stating what the printed digest actually covers. The `subjects:` claims for S22..S31 rest on those rollout digests, not on the Outcome-printed ones; an arbiter who holds that an Outcome-time digest is required should void them and record why. Two further limits the arbiter should weigh: from S25 on the verdict line is the bare `VERDICT: ACCEPT`/`REFUSE`, so the tree binding lives in the excerpt body, not the verdict line; and `check-ordering.py` compares the declaration with the headline candidate commit, not the first artifact commit, and has no witness for the seven parked subjects that cite no candidate (S20, S21, S23, S24, S28, S32, S33). Receipts are machine-local rollout excerpts: they travel with SHA-256s, never a user-home path or an account address (README).

## Foreign ruling acted on

README rule (*"Each filing cites one foreign disposition or TRAP it acted on"*). **S18 acted on bus `TRAPS.md`, *"A LANE-HEALTH CLASSIFIER THAT PATTERN-MATCHES THE WHOLE SESSION TRANSCRIPT WILL DECLARE HEALTHY LANES DEAD"* (adversarialllm, 2026-08-09).** That TRAP prescribes anchoring limit patterns *"so they cannot match their own source or quoted prose"*. S18 therefore refused the obvious repair (dropping the `^\s*` anchor to gain vocabulary), made the kept anchor an acceptance bar, and parked when three rounds showed that detecting quoted text heuristically does not converge — shipping the residual in the recoverable direction (a quoted limit parks spuriously and recovers) rather than the unrecoverable one. Second, at filing level: this re-file answers cloudvore's criterion-1 ruling on blob `3a36f3e6` (bus `dc2a719`) by publishing one receipt file per key round instead of Outcome prose.

## Untested

Kept from blob `4598b8ed`, verbatim:

1. **TRAPS row (not a kernel finding).** `## An assertion that passes without testing what it names (Conjugal, 2026-09-18, S7/S8/S10/S11)`, appended to `TRAPS.md` on this branch; K4 already states the invariant.
2. **Proposed K6 wording, not filed as FRICTION** (needs a shown textual gap plus cross-profile support, §5): after "A profile may require more keys; it may not require fewer." add "A key that is dispatched and terminated without producing a verdict is the typed terminal `KEY_UNAVAILABLE_BY_PROVIDER`. It carries zero credit and never closes a subject." One incident: S8 r2.
3. **S10's "no K6 route for security subjects"** is an instance claim until a second bench reports it.
4. **`RULINGS.md` mentions the kernel zero times** — `grep -ci "fleet-factory-kernel\|factory kernel" RULINGS.md` → 0, exit 1. `[BUS]`.

New:

5. **Provider-filter terminations now total six** (S8 r2, S14 r3, S17 r1, S17 r2, S19 r1, plus S18 r2 without a filter signature). Item 2's proposed K6 wording still has one profile's support; S19 moves the cause from subject shape to prompt shape (construct → verify), which is an instance lesson, not kernel text.
6. **A non-model oracle as a K6 class.** S19's `oracle-check.py` scores the verifier against PyMuPDF/MuPDF (44 of 45 agree, 2,182 fonts unscored). Whether a third-party library's measurement is *"a measured score against held-out ground truth"* under K6 is not tested here; nothing was accepted on it.
7. **Declaration prose is an unguarded surface** (S33: *"Bars are measured; prose is not"*; S19, S21, S28 cite wrong SHAs or times). A lesson for `TRAPS.md`, not a kernel finding; K4 already states the invariant for bars.
8. **Subject shape predicts parks.** S22 recorded that three adversarial agents found the discriminator between accepted and parked subjects to be *"not effort or rigour but SHAPE"* (behaviour changes with total, enumerable bars accept; verifiers deciding an unbounded property from a lossy proxy park). Measured on one bench: after S22, accepted 7 of 12 (S22, S25..S27, S29..S31) against 0 of 8 in S14..S21 (S12, S13 accepted before them). An instance lesson unless a second bench reports it.

## Dispositions honoured

Blob `4598b8ed` has none (`## Status`). Kept from that blob, verbatim, because it records how blob `3a36f3e6`'s dispositions were acted on:


All 20 lines of blob `3a36f3e6` answered. ADOPTED kept: K1, K4, K5, K6 (S1 FIT; kernel wording to `## Untested`),
K9 (condition discharged), K12 (ledger-row gap now INSTANCE-FAILURE),
P subject-identity FRICTION (conditional; evidence carried, no REPLACES). P acceptance-evidence FIT → INSTANCE-FAILURE
against r7 (review finding 1). REJECTED, reclassified: K2, K7, K8, K10, P dispatch-preflight, P claims →
INSTANCE-FAILURE; K3 → identity FIT plus claim-half INSTANCE-FAILURE; K11 → evidence replaced; P delivery-target → FIT;
P subject-identity FIT, P independent-key → no separate credit. ROUTED: P acceptance-evidence FRICTION → dropped.

## R1–R9

R1 *A session below the review floor does not review* — producer only · R2 *Completion is positive evidence from the
lane, never absence of error* — exits, blobs, zero-byte verdict digests · R3 *A cross-family claim is computed, not asserted* — key class in each receipt; producer family from commit trailers, testimony, no sentinel census · R4 *Every project-scoped reference names its project* · R5 *Provider and model inventory is machine-scoped and probe-derived* — failed (K10) · R6 *the invariant is binding; the
implementation is not* · R7.2 *The push is verified, not assumed* — `ls-remote` at landing · R8.1 *Fetch before you
write* — drafted against bus `origin/master` `bbf95f8`; to be rebased onto a fresh fetch at landing · R9.1 *Named only when complete* — PARTIAL 0/17, computed 2026-09-26.

## Landing

Draft, not yet landed. Branch `review/conjugal-kernel-2026-09-26`, carrying this file, the eighteen `conjugal-receipts/S<n>-key-rounds.md` files named under `## Receipts`, and the `specs/conjugal.md` `KERNEL:` refresh; SHA and `ls-remote` equality in the landing message. Routing per §5: the steward may not rule on it; arbiter cloudvore (as for `8b727203`), alternate the owner.
