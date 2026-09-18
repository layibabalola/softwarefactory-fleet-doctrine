# Factory-kernel dogfood filing — conjugal (machine Bachelor) — re-file against r5 / code@r7

project: conjugal
kernel: fleet-factory-kernel r5
profile: code@r7
instance: `coordination/kernel-dogfood/` (S1..S11 declarations + README) + tools per clause; `KERNEL: DOGFOOD-PENDING Sol` was only on `origin/review/conjugal-kernel-2026-09-14` (`r2 · code@r2`; bus master `specs/conjugal.md` `grep -c KERNEL` → 0); refreshed to `r5 · code@r7` in `specs/conjugal.md` on this branch; map under `## Instance map`
subjects: 1 end-to-end claimed for S1 with a published acceptance receipt (see ## Receipts); 10 delivered-unaccepted (S2..S11), counted zero
window: 2026-09-15T23:18Z .. 2026-09-17T18:22Z (S1 declaration author date, conjugal `96d1b3a27` .. S11 outcome author date, conjugal `838bbb716`)
health: assurance=SATISFIED operability=PRESSURED
providers: claude(claude-opus-5, producer) codex(gpt-6-astra, acceptance key) — both cleared a sentinel; key verdicts on S1, S3, S4, S5, S8 r1, S9; terminated without one once (S8 r2)
posture: no model review (an acceptance key is not a review panel; R9 does not apply)

**Status.** Steward's own filing; Conjugal never writes `conjugal.dispositions.md` (§5). Revisions read, quoted: kernel `**Status: \`CANDIDATE r5 — DOGFOODING\`.**`; profile `**Profile revision:** r7.` **Profile moved to r8** (bus `99b72bb`, arrived while this filing was landing; branch base `337e47c` now reads `**Profile revision:** r8.`). r8 adds to K6 *"Review-key charters declare execution or static review before dispatch"* and to resource terminals *"Environment-only review blocks are typed terminals, not subject verdicts or completed rounds"*; neither is evaluated here — the r8 re-run is owed per PROMPT K §6.
Every line of `conjugal.dispositions.md` (`arbiter: cloudvore`, bus `dc2a719`) is honoured (`## Dispositions honoured`). `[BUS]` re-runs from a clone of this branch plus Python; `[INLINE]` is quoted Conjugal-side testimony. Exits
read unpiped; Conjugal SHAs qualified (Law 6). Re-run evidence (2026-09-18) is quoted in place; S1 receipt under
`## Receipts`.

## Subjects

**S1 — `S1-resume-prep-landing`, delivered AND accepted, now with a receipt.** `[INLINE]`
Declaration conjugal `96d1b3a27` (author 2026-09-15T18:18:10-05:00; committer 18:22:09 — rebased).
Candidate conjugal `ca4dd1346`, identity `721e4b15677a579d1fab3fd430a785d7974e243d`, re-measured
2026-09-18: `git -C <conjugal> rev-parse ca4dd1346^{tree}` → that string; `merge-base --is-ancestor ca4dd1346 master`
→ exit 0. S1: *"Accepted by `gpt-6-astra` (class `codex-openai`) bound to that exact identity."* The arbiter refused
criterion-1 credit because that verdict was `[INLINE]`; it is now a file (`## Receipts`).

**S2..S11 — delivered, NOT accepted, counted zero.** S11: *"K6 NOT OBTAINED, so this counts ZERO, as S2-S10 do."* S2 no key sought; S3 refused ×3; S4 refused ×2, r3 unkeyed; S5 refused (unbaselined bar); S6, S7, S11
no key; S8 refused r1, r2 *"terminated mid-review by its provider's security filter"*, no verdict; S9 refused ×2,
r3 unkeyed; S10 *"the declared K6 route does not exist"*.
Delivery: S1, S5–S8, S10, S11 fast-forwarded to Conjugal `master` (`merge-base --is-ancestor` exit 0); S2, S4, S9 pushed to bus
`origin/review/conjugal-kernel-2026-09-15` (`tools/fleet-resume-readiness.py`, `tools/arbitration-queue.py`,
`tools/test-kernel-arbitration-route.py`, suites), `[INLINE]`, not carried here. Conjugal-side bars S6–S11: **not re-run
in this filing**; each stands as recorded in its S-file's `## Outcome` (S6 *"acceptance bars green"*, S7 *"bars green, coverage gap disclosed"*, S8 *"4-of-4
mutation-proven"*), `[INLINE]`. Re-run 2026-09-18: trees and ancestry (`## Ordering witness`) and the K7 detector census —
`git ls-files coordination/tools | grep -iE "deliver|accepted|kernel"` → nothing, exit 1; README names no detector — NONE.

## Clauses

K1 | FIT | "A candidate is never accepted on evidence whose only author is its producer" | ADOPTED. Producer `claude-opus-5`, key `gpt-6-astra`, six refusals then acceptance. `[BUS]` `grep -n "porcelain\|untracked-files\|ignore-submodules\|assume-unchanged\|skip-worktree" bootstrap/session-checkpoint.py` returns the pins the key forced. New: the receipt names both actors, `adjudications/factory-kernel/conjugal-receipts/S1-astra-acceptance.md` | PROOF: an acceptance here whose producing and accepting actors resolve to one independence class

K2 | INSTANCE-FAILURE | "Each project keeps one register of what needs the owner and what does not" | Reclassified. `[INLINE]` Still no single register. Cost: S3 declared a bus artifact Conjugal may not write (*"itself the K2 finding"*); S10: *"the register that would name a human verifier does not exist in this repo"*. No REPLACES | PROOF: a single Conjugal file every other authority text defers to

K3 | INSTANCE-FAILURE | "for one held subject, its claim record and the procedure by which someone other than the claimant decides it stale" | Identity half held: every S-file carries `RECOMPUTE: … rev-parse <candidate>^{tree}`. Claim half is r5's new observable; the instance has nothing: the `P:code claims` disposition ruled the shared checkout *"is itself a claimed subject"*; no lease existed (S8: *"four lane sessions plus scheduled floors share that checkout"*). No REPLACES | PROOF: a Conjugal claim record naming subject, holder, expiry and owned processes

K4 | FIT | "Never exit code, output size or silence" | ADOPTED. `[BUS]` both files carried here from `origin/review/conjugal-kernel-2026-09-15` (never on bus master), sha256 `3497a5a32dbb91d87bd4887def890f08d68e632ec9c070ecd5ae27aafbcec053`; 2026-09-18: `python bootstrap/test-session-checkpoint.py ; echo "exit=$?"` → 19 `case:` headers, 113 `ok`, `PASS session-checkpoint`, exit 0; delete `"-z", ` at line 177 → exit 1, 103 ok, `FAIL session-checkpoint: 10 check(s) failed`: `new path recorded`, `no unsplit arrow entry`, `listed path resolves on disk: tracked.txt -> renamed.txt`, `the spaced path is actually recorded`, `no quote characters survive into a path`, `listed path resolves on disk: "a file.txt"`, `exact non-ASCII path recorded`, `no C-escape recorded`, `listed path resolves on disk: "caf\303\251.txt"`, `the real untracked file is reported`; restored (sha256 back to `3497a5a3…`) → 113 ok, exit 0. Negative cases: S5 *"I took the BACKGROUND WRAPPER's exit code … as the test's"*; S7 *"4 of 6 guards are asserted by symmetry"*; S8 the cap mutation *"survives"*; S10 probes *"reported OUT for everything"*; S11 *"would have passed without testing what it named"* — the last four are one hazard, filed as a TRAPS row | PROOF: a gate in this repo whose exit status is read through a pipe

K5 | FIT | "the profile line recorded before work, and the acceptance receipt bound to the same identity" | ADOPTED for S1; eleven declarations precede their code; S4–S11 carry `ORDERING: read precedence from AUTHOR dates or the reflog, never committer dates`. r5 K5 names no date; `review/conjugal-kernel-narrow-corrections-2026-09-17` proposes the AUTHOR-date sentence; carried under `P:code subject-identity`. Rebased declaration witness: conjugal `96d1b3a27` author 18:18:10 / committer 18:22:09 (pre-rebase twin `f1a9a9dc8`, same patch-id, not on `master`, not cited); S2..S11 under `## Ordering witness` | PROOF: a declaration commit touching its own declared artifact set

K6 | FRICTION | "Every acceptance includes a key from an independence class other than the producer's" | S1 FIT (ADOPTED; receipt `dfe9a418…`). Cost on S2..S11: ten delivered, zero accepted. Every refusal reproduced a defect, but one dispatch ended with **no verdict**: S8 round 2, *"No verdict was produced: not an accept, not a refusal."* r5 K6 has no terminal for that state; only the profile does (*"independent key unavailable: typed terminals"*). S10's CORRECTION: the CI route is no independence class here (*"`CI_RUNS_ON` = [self-hosted …] … no branch protection"*) — instance, not text | REPLACES: "A profile may require more keys; it may not require fewer." -> the same, plus the narrow-corrections branch's sentence: "A key that is dispatched and terminated without producing a verdict … is the typed terminal `KEY_UNAVAILABLE_BY_PROVIDER`. It carries zero credit and never closes a subject" | PROOF: a K6 receipt in r5 text that types a no-verdict termination

K7 | INSTANCE-FAILURE | "how the project detects an accepted subject that never delivered" | Reclassified per disposition (§3). Detector still NONE, at a cost: S8's first K7 section, *"These commits are not on master"* — `5308b323a` (S6), `ca9772ac8` (S7), `36da13f95` (S8) believed delivered, found by hand, later fast-forwarded. Deliveries that closed, closed as one transaction (S11: *"the shared checkout saw only a ref advance"*). No REPLACES | PROOF: a Conjugal tool that lists accepted-but-undelivered subjects unprompted

K8 | INSTANCE-FAILURE | "Running out of quota means rotating or parking the work that needs inference" | Reclassified per disposition. Event: S8 round 2, key *"terminated mid-review by its provider's security filter"*, zero credit; non-inference work continued. What failed: the profile requires *"parked work names its resume condition and the actor who can satisfy it"* and **no S-file records a park record** — `grep -i "resume condition\|park" coordination/kernel-dogfood/S*.md` → no match. Health. Correction: S11:158 says the filter killed S8 AND S10; S10's file records no dispatch — one kill (S8 r2) plus the S5 kill the disposition cites | PROOF: a Conjugal park record for S8 naming resume condition and actor

K9 | FIT | "the resumability gate's command and its last passing output" | ADOPTED-CONDITIONAL; condition *"publish the live gate's identity alongside the copy"* is met **now, on this branch, and was not before**. Before: bus `tools/conjugal-reference/resumability-check.py` was blob `46aaa31baf09db73a325bd866161ac6ac0f99c94` (bus `2a1120e`, 2026-09-13; 157 lines, sha256 `857b0f7a…`), lacking the `SCRIPT_GENERATED` block and the `f<N>-` rules Conjugal `3f08a94e8` (2026-09-15T10:48:13-05:00) added; live is 177 lines. **The prior K9 [BUS] claim that the copy showed the script-generated distinction was false.** Now: byte copy of Conjugal `master:coordination/tools/resumability-check.py` (last touched `3f08a94e8`); `sha256sum` on both = `a9e00b8f60efdcdd5ff6889ec3cf7f8fbd98e24535119fcb1eb026d0ededdd25`; `[BUS]` `git hash-object tools/conjugal-reference/resumability-check.py` → `0f05582128a368ca502f8dc2051b0b8b2ce86da9` = `git -C <conjugal> rev-parse master:coordination/tools/resumability-check.py`. Live gate at Conjugal `master` `6cb358d43`: `python coordination/tools/resumability-check.py` → `PASS resumability (docs/architecture/approach-a @ 6cb358d43): tree-only resume possible; no live values in RESUME.md`, exit 0 | PROOF: the live gate exiting 1 at Conjugal `master`

K10 | INSTANCE-FAILURE | "Missing, `unknown` or mismatched account identity makes the inventory stale" | Unchanged (health). `[INLINE]` No S-file records a re-probe of `~/.claude/machine-inventory.yaml` under the current account before the `gpt-6-astra` dispatches; parity is proved at session start, inventory freshness is not | PROOF: a Conjugal preflight comparing `probed_under` to the live parity fingerprint and refusing on mismatch

K11 | FIT | "the quoted title line of each rule the project confirms it meets" | Prior evidence withdrawn (self-certifying). Offered: `## R1–R9`; `python tools/harvest-status.py factory-kernel` emits `POSTURE-NOT-R9-COMPUTED` against this filing — correct for `posture: no model review`, accepted | PROOF: a rule below this filing violates

K12 | INSTANCE-FAILURE | "The steward harvests every filing and answers each one" | ADOPTED and answered (20/20). (a) Prior K12 `[BUS]` outputs were REFUTED (filings=3 not 8): authorship error. `[BUS]` re-run 2026-09-18 in this branch's worktree at base `337e47cf0cd1f3628eaae1fe603fe1627a2f4543`: `python tools/harvest-status.py factory-kernel ; echo "exit=$?"` → `filings=9`, `conjugal HARVESTED blob=3a36f3e6 ref=origin/review/conjugal-kernel-2026-09-15 findings=20 untested=0 … flags=POSTURE-NOT-R9-COMPUTED`, `open=0`, exit 0 (`open=1`, exit 1 at `68b6c69`); `python tools/kernel-e2e.py` → `ledger : 16 rows over 9 projects`, `CLOSED END-TO-END SUBJECTS : 0`; `sed -n 3p specs/fleet-factory-kernel.md` → `**Status: \`CANDIDATE r5 — DOGFOODING\`.**`; `sed -n 3p specs/fleet-factory-kernel/profiles/code.md` → `**Profile of** \`specs/fleet-factory-kernel.md\` r5. **Profile revision:** r8. **Status:** \`BENCHED\`.` (r7 at `68b6c69`). S2..S11 headers still read `PROFILE: code@r4 · kernel fleet-factory-kernel r4`. (b) Ledger-row gap: §5, *"Each harvest appends one row per filing to … HARVESTS.md (steward-written)"*. Conjugal's runner drops the self-filing at `eligible()` (`harvest_runner.py:160`, `SELF-FILING …`), so a foreign-arbitrated filing gets **no row from any automation**; the row was appended by hand in bus `68b6c69`. §5 is satisfiable (`kernel-e2e.py` lists filed-but-unrowed), so the instance failed a clause it could meet. Health | PROOF: a runner run id that appended a ledger row for a foreign-arbitrated steward filing

## Profile fields

P:code subject-identity | FRICTION | "git tree OID of the candidate commit as it will be delivered, after any merge with the delivery target" | ADOPTED-CONDITIONAL, condition external (another `code` bench); carried. The objection that bus `57a3356` has author==committer is accepted; the rebased anchors are Conjugal-side: S3 amendment `e71c88683` (author 20:21:56, committer 20:24:08), S1 declaration `96d1b3a27` (18:18:10 / 18:22:09). No ordering refusal recurred once author dates were read; `## Ordering witness` | REPLACES: unchanged from blob `3a36f3e6` | PROOF: a Conjugal declaration whose precedence survives a rebase read from committer dates

P:code acceptance-evidence | FIT | "Before work, bind the acceptance contract by digest, including checks, harness limits, review scope, round budget and round-closing rule" | ADOPTED for S1 (three checks at conjugal `ca4dd1346`). r7 is stricter than r4; met in part: every S-file pins and baselines its checks; none binds the contract by digest or names a round budget — S4's two refusal rounds *"against a bar nobody ever wrote down"* are that cost. The routed S5 finding is cloudvore's bench | PROOF: an S-file whose acceptance section was edited after its first key round

P:code independent-key | FIT | "a verifier from another model family (R3)" | Restatement of K6; kept because §4 asks a line per exercised field. Receipt `adjudications/factory-kernel/conjugal-receipts/S1-astra-acceptance.md` | PROOF: as K6

P:code resource-terminals | INSTANCE-FAILURE | "parked work names its resume condition and the actor who can satisfy it" | New. S8 r2 is the typed terminal *"independent key unavailable"*, zero credit, but no park record names a resume condition or actor; no escalation channel exists (K2). Health | PROOF: a park record for S8 or S10 under `coordination/kernel-dogfood/`

P:code delivery-target | FIT | "integration branch via the project's landing path" | Rejected as a local doc defect; accepted. Landing path is a command in S8/S11 (`merge-tree --write-tree` census, then `git merge --ff-only`); closed for S1, S5–S8, S10, S11 | PROOF: a Conjugal landing that swept a peer's staged file

P:code dispatch-preflight | INSTANCE-FAILURE | "the spending tool runs the project's resume gate before dispatch and retains its result, the inventory snapshot and digest, and account-parity evidence" | Per disposition. No dispatch tool retains any of it; every `codex exec` was hand-run. Health | PROOF: a Conjugal dispatch receipt carrying an inventory digest

P:code claims | INSTANCE-FAILURE | "A mutable checkout another project executes from is itself a claimed subject" | Reclassified per disposition (was UNEXERCISED): the clause arose on every shared-checkout landing; no lease existed. Same fact as K3 | PROOF: as K3

P:code human-gates | INSTANCE-FAILURE | "the register is reachable from every session checkout … names an owner-facing escalation channel" | New. S8/S10 touch security-sensitive paths (`scripts/auto-approve-gate.sh`, `scripts/pairprog-scope-match.py`) this field routes to the register; S10: *"the register … does not exist"*. Root: K2 | PROOF: a register row naming the human verifier for `scripts/auto-approve-gate.sh`

## Instance map

`[INLINE]` unless `→ bus`. K1 `codex exec -m gpt-6-astra` · K2 **NONE** · K3 `coordination/kernel-dogfood/S*.md` + `rev-parse <candidate>^{tree}`; **claims NONE** · K4 mutation-proven suites, exit read unpiped (→ bus `bootstrap/test-session-checkpoint.py`) · K5 `coordination/kernel-dogfood/` · K6 `codex exec` model key; **no CI or human route** (S10) · K7 `merge-tree --write-tree` census + `git merge --ff-only`; **detector NONE** · K8 **park record NONE** · K9 `coordination/tools/resumability-check.py` + `session-checkpoint.py` `Stop` hook (→ bus copies, gate copy refreshed here, blob `0f05582128…` both sides) · K10 `coordination/tools/check-cli-auth.py`; **inventory freshness NONE** · K11 this filing · K12 `coordination/harvest/harvest_runner.py` + task `\Conjugal-Harvest-Steward`; **self-filing ledger row NONE** (→ bus `tools/kernel-e2e.py`).

## Ordering witness

Author dates (`git log --format=%h %ad --date=iso-strict`; day of 2026-09, `-05:00`). Declaration = first-add of
`S<n>-*.md`, each an ancestor of Conjugal `master` (exit 0). Trees (`git rev-parse <c>^{tree}`) match the S-files.
Declaration precedes candidate in all eleven.

| S | Declaration (author) | Candidate (author) | Note |
|---|---|---|---|
| S2 | conjugal `96d1b3a27` 15 18:18:10 | bus `06c1b39` 15 18:31:49 | file cites NO candidate SHA; first add of the tool |
| S3 | `3f0abdee9` 15 20:15:06; amend `e71c88683` 20:21:56 | bus `57a3356` 20:23:52 … `38bc730` 20:52:34 | refutes `RETROSPECTIVE` |
| S4 | `a8efa90f4` 16 01:30:45 | bus `18d7ceb` 16 17:39:45 | |
| S5 | `ab1ce9b2e` 16 07:33:14 | `dfaa928e1` 16 07:43:52 | file cites NO candidate SHA; first add of the test |
| S6 | `c45e7255e` 16 10:16:44 | `5308b323a` 16 10:41:20 |  |
| S7 | `f59c3fcda` 16 10:53:34 | `ca9772ac8` 16 11:05:19 |  |
| S8 | `e82ad9433` 16 11:19:53 | `36da13f95` 11:28:22 → `5d51a7b29` 17:23:15 |  |
| S9 | `cffac8484` 16 17:05:51 | bus `d825e9a` 16 17:39:46 |  |
| S10 | `7db58b05a` 16 17:54:12 | `a34f929a8` 16 18:02:28 |  |
| S11 | `b7128246e` 17 12:59:50 | `c0f033ff6` 17 13:13:19 |  |

Ancestry: S5–S8, S10, S11 candidates on Conjugal `master` (exit 0); bus candidates exit 1 on bus master, 0 on
`origin/review/conjugal-kernel-2026-09-15`. S3 nuance: `coordination/tools/session-checkpoint.py` (first added `5dd6b8d5e` 15 14:41:26)
was in S1's declared set.

## Receipts

- **S1 acceptance receipt:** `adjudications/factory-kernel/conjugal-receipts/S1-astra-acceptance.md` on this branch — `VERDICT: ACCEPTED identity=721e4b15677a579d1fab3fd430a785d7974e243d key=gpt-6-astra class=codex-openai`, six preceding refusals, actors, method, time. SHA-256 `dfe9a41809b9fea90ec9edd702294322fa586860e853f2a2a553462b8682a3c4` (`sha256sum` on that path). §5 criterion 1 is the arbiter's call.
- **Re-run evidence** (2026-09-18, read-only, exits read unpiped) is quoted in place (K4, `## Ordering witness`, K9, K12, S2..S11); the scratch file it came from is not published.

## Untested

1. **TRAPS row proposed (not a kernel finding).** `## An assertion that passes without testing what it names (Conjugal, 2026-09-18, S7/S8/S10/S11)`. Four green checks proved nothing about what they were named for; rule and test in the row appended to `TRAPS.md` on this branch. TRAPS because it generalises (PROMPT K §4); K4 already states the invariant.
2. **S10's "no K6 route for security subjects"** is an instance claim until a second bench reports it.
3. **`RULINGS.md` mentions the kernel zero times** — `grep -ci "fleet-factory-kernel\|factory kernel" RULINGS.md` → 0, exit 1. `[BUS]`.

## Dispositions honoured

All 20 lines of blob `3a36f3e6` answered. ADOPTED kept or carried: K1 (receipt added), K4 (mutation re-run here), K5, K6
(S1; FRICTION on S2..S11 not re-argued), K9 (conditional — discharged on this branch, prior [BUS] claim withdrawn), K12
(answered; ledger-row gap now INSTANCE-FAILURE), P acceptance-evidence FIT, P subject-identity FRICTION (conditional,
carried). REJECTED, reclassified: K2, K7, K8, K10, P dispatch-preflight, P claims → INSTANCE-FAILURE; K3 → identity FIT
plus claim-half INSTANCE-FAILURE; K11 → evidence replaced; P delivery-target → FIT; P subject-identity FIT and
P independent-key → dropped or exercised-field line only. ROUTED: P acceptance-evidence FRICTION → dropped.

## R1–R9

R1 *A session below the review floor does not review* — Opus 5, producer only · R2 *Completion is positive evidence from
the lane, never absence of error* — exits, blobs, quoted lines · R3 *A cross-family claim is computed, not asserted* — in
the receipt · R4 *Every project-scoped reference names its project* — Conjugal SHAs qualified · R5 *Provider and model
inventory is machine-scoped and probe-derived* — failed in substance (K10) · R6 *the invariant is binding; the
implementation is not* — parity verified, freshness not · R7.2 *The push is verified, not assumed* — `ls-remote` in the
landing message · R8.1 *Fetch before you write* — branch rebased onto bus `master` `337e47c` · R9.1 *Named only when complete* — none claimed.

## Landing

Branch `review/conjugal-kernel-2026-09-18`; SHA and `ls-remote` equality in the landing message.
