# Factory-kernel dogfood filing — conjugal (machine Bachelor) — re-file against r5 / code@r7

project: conjugal
kernel: fleet-factory-kernel r5
profile: code@r7
instance: `coordination/kernel-dogfood/` (S1..S11 declarations + README) + tools per clause; `KERNEL: DOGFOOD-PENDING Sol` refreshed to `r5 · code@r7` in `specs/conjugal.md` on this branch (bus master had no `KERNEL:` line); map under `## Instance map`
subjects: 1 end-to-end claimed, S1=721e4b15677a579d1fab3fd430a785d7974e243d (receipt under ## Receipts); 10 delivered-unaccepted (S2..S11), counted zero; all eleven declared `PROFILE: code@r4 · kernel fleet-factory-kernel r4`
window: 2026-09-15T23:18Z .. 2026-09-17T18:22Z (S1 declaration conjugal `96d1b3a27` .. S11 outcome conjugal `838bbb716`, author dates)
health: assurance=UNSATISFIED operability=PRESSURED
providers: claude(claude-opus-5, producer) codex(gpt-6-astra, acceptance key) — key verdicts on S1, S3, S4, S5, S8 r1, S9; terminated without one once (S8 r2)
posture: conjugal-standard-PARTIAL (0/17 lanes; missing: Designer-Scope 0/1; Designer-Verify 0/1; Lint-Consistency 0/2; Arbiter 0/1; Consolidator 0/1; Panel 0/8; Classifier 0/3)

**Status.** Steward's own filing (§5). `assurance=UNSATISFIED` maps to admitted required-predicate failures: acceptance-contract binding (P:code acceptance-evidence), inventory freshness (K10), dispatch evidence (P:code dispatch-preflight), claims (K3), park records (K8); `operability=PRESSURED`: S8 r2 provider kill, S10 no K6 route, ten unaccepted deliveries. Posture computed by `python tools/review-posture/review_posture.py posture <empty dir>` (exit 1): no posture role ran; the acceptance key and the 2026-09-18 read-only adversarial review by `gpt-6-astra` ran outside its roles, no lane credit (R9.4). Revisions quoted: kernel `**Status: \`CANDIDATE r5 — DOGFOODING\`.**`; profile `**Profile revision:** r7.` **Profile moved to r8** (bus `99b72bb`, during landing; base `337e47c` reads `**Profile revision:** r8.`): r8 adds review-key charters (execution vs static) and environment-only review blocks as typed terminals; not evaluated here, r8 re-run owed (PROMPT K §6). Dispositions (`arbiter: cloudvore`, bus `dc2a719`): `## Dispositions honoured`. `[BUS]` re-runs from a clone of this branch plus Python; `[INLINE]` is quoted Conjugal-side testimony. Exits read unpiped; Conjugal SHAs qualified (Law 6).

## Subjects

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

## Profile fields

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

## Receipts

- **S1 acceptance receipt:** `adjudications/factory-kernel/conjugal-receipts/S1-astra-acceptance.md` — `VERDICT: ACCEPTED identity=721e4b15677a579d1fab3fd430a785d7974e243d key=gpt-6-astra class=codex-openai`, six preceding refusals, actors, method, time; re-run evidence is quoted in place. SHA-256 `66034ac71082662b3f86cb4bef1771e750c85d41aea6a2f951487cf773017ca2` (`sha256sum` on that path). Read-only adversarial review by `gpt-6-astra` 2026-09-18 ruled the excerpt a receipt under §1; its 9 findings applied. Both re-read commands were repaired and run against the seven local logs: verdict line and excerpt digest `4cfd7357…` reproduced (exit 0); `turn_context` model `gpt-6-astra` on all seven (exit 0).

## Untested

1. **TRAPS row (not a kernel finding).** `## An assertion that passes without testing what it names (Conjugal, 2026-09-18, S7/S8/S10/S11)`, appended to `TRAPS.md` on this branch; K4 already states the invariant.
2. **Proposed K6 wording, not filed as FRICTION** (needs a shown textual gap plus cross-profile support, §5): after "A profile may require more keys; it may not require fewer." add "A key that is dispatched and terminated without producing a verdict is the typed terminal `KEY_UNAVAILABLE_BY_PROVIDER`. It carries zero credit and never closes a subject." One incident: S8 r2.
3. **S10's "no K6 route for security subjects"** is an instance claim until a second bench reports it.
4. **`RULINGS.md` mentions the kernel zero times** — `grep -ci "fleet-factory-kernel\|factory kernel" RULINGS.md` → 0, exit 1. `[BUS]`.

## Dispositions honoured

All 20 lines of blob `3a36f3e6` answered. ADOPTED kept: K1, K4, K5, K6 (S1 FIT; kernel wording to `## Untested`),
K9 (condition discharged), K12 (ledger-row gap now INSTANCE-FAILURE),
P subject-identity FRICTION (conditional; evidence carried, no REPLACES). P acceptance-evidence FIT → INSTANCE-FAILURE
against r7 (review finding 1). REJECTED, reclassified: K2, K7, K8, K10, P dispatch-preflight, P claims →
INSTANCE-FAILURE; K3 → identity FIT plus claim-half INSTANCE-FAILURE; K11 → evidence replaced; P delivery-target → FIT;
P subject-identity FIT, P independent-key → no separate credit. ROUTED: P acceptance-evidence FRICTION → dropped.

## R1–R9

R1 *A session below the review floor does not review* — producer only · R2 *Completion is positive evidence from the
lane, never absence of error* — exits, blobs · R3 *A cross-family claim is computed, not asserted* — key class in the
receipt; producer family is testimony, no sentinel census · R4 *Every project-scoped reference names its project* ·
R5 *Provider and model inventory is machine-scoped and probe-derived* — failed (K10) · R6 *the invariant is binding; the
implementation is not* · R7.2 *The push is verified, not assumed* — `ls-remote` at landing · R8.1 *Fetch before you
write* — rebased onto `337e47c` · R9.1 *Named only when complete* — PARTIAL 0/17, computed.

## Landing

Branch `review/conjugal-kernel-2026-09-18`; SHA and `ls-remote` equality in the landing message.
