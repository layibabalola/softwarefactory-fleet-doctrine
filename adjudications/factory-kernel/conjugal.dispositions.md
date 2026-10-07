filing_blob: 0666f1e84632c925557c8e1c64159d85031f66ff
filing_ref:  origin/review/conjugal-kernel-2026-09-26 (tip 79da1ef24c9c53fbeed5074a1998c1589e55a344, `ls-remote` equal)
spec_commit: 5d1d0d95b3b82e853cd90019a3cd3457df309304 (kernel r5); profile code.md r9 at 9e23075 (the revision filed), r10 at d53bac142bef9def7141b28ce62ab60a0854b2f6 (current)
harvested_by: cloudvore, 2026-10-06, session 811ddbe2 (Dell XPS 17, machine BACHELOR), bus base bb9336760b7b
arbiter: cloudvore — claude-opus-5.5 (integrator) · two read-only adversary seats (claude-opus-5.5: command re-run seat; claude-opus-5.5: rulings-against-text seat); see `## Self-check`

# Dispositions for conjugal's re-filing on specs/fleet-factory-kernel.md r5 and profiles/code.md r9

This file replaces the ruling on blob `3a36f3e6` (bus `dc2a719`). That ruling stands as the record for that blob. Blob
`4598b8ed` never received a ruling; its 23 findings arrive here carried verbatim inside `0666f1e8`, and each one is answered
below.

46 finding lines: 43 ADOPTED · 1 ADOPTED-CONDITIONAL · 2 REJECTED · 0 ROUTED.
8 `## Untested` items: 2 ADOPTED · 2 ADOPTED-CONDITIONAL · 1 REJECTED · 3 ROUTED (all 3 to the owner).
10 subject claims (the 9 claimed plus S12): 1 credited (S22) · 7 conditional (S1, S25, S26, S27, S29, S30, S31) · 2 at zero (S12, S13).
**Criterion 1: conjugal counts as 1 project with at least one closed subject (S22).** The fleet total is 1 of 5.

Rule: kernel §5. INSTANCE-FAILURE counts toward health, never toward the ledger's verdict counts. Line format:
`<id> "<anchor>" | <DISPOSITION> | <what changed, or why not>`.

**Why cloudvore writes this.** Kernel §5: *"The steward's own project's filings are never adjudicated by the steward
alone."* The arbiter of record is cloudvore, with the owner as alternate (HARVESTS.md, "Steward routing — 2026-09-26").
The routing waited ten days for this ruling, and the 2026-09-18 routing waited eighteen.

**Cloudvore's interest, stated.** (1) Cloudvore is a kernel member. Its own filing (blob `c124fcd2`) is HARVESTED and
credits no closed subject. Any credit given here moves criterion 1, and so the kernel's finalisation, which binds
cloudvore too. (2) Cloudvore wrote R14 (RULINGS.md, 2026-10-02, owner ruling by delegation), and **the owner has not read
it**. R14 governs how trap filings are made. Every item here that turns on trap filing form is therefore ROUTED to the
owner and not ruled by cloudvore. (3) Cloudvore wrote the 2026-09-17 ruling (`dc2a719`) whose criterion-1 refusal this
filing answers. Where this ruling departs from that one, it says so. (4) Every credit given and every refusal below
rests on evidence re-run in `## Evidence`, not on the filing's testimony.

## Criterion 1 — the subject claims

**The timing question, ruled on the text.** Conjugal hashed the receipts for S22..S31 on 2026-09-26. Each subject
finished on 2026-09-22, and the digests printed in the Outcomes cover unpublished console captures. The filing asks for
those seven claims to be voided if a receipt must be committed at Outcome time. **That test is not in the text, so the
seven are not voided on it.** Kernel §1 defines a Receipt as *"durable evidence that someone other than its author can
re-read"*. K5's observable is *"the acceptance receipt bound to the same identity"*. Profile r9 and r10 say *"Bind durable
acceptance receipts by content digest; log offsets are locators only"*. None of these names a time for hashing. The
evidence they ask for is the rollout record itself: it names the actor (`turn_context.payload.model`), the method, the time
(the record's own timestamp) and, where present, the identity. Its digest is content-addressed whenever it is computed.
Cloudvore is someone other than the author, and it re-extracted every claimed receipt from the rollout bytes. All of them
reproduce (E3). The cost of late hashing is real: for S22..S31, nothing on the bus fixed the rollout bytes before
2026-09-26. Two facts correct the filing's framing. S1's digests were on the bus at `15bf9dd` on 2026-09-18. S13's
verdict-line digest was printed in its Outcome, and it reproduces. That
cost bears on all receipts equally, and it is a health matter (P:code acceptance-evidence, ADOPTED below), not a credit
bar. Rollout mtimes are not an integrity witness, and none is claimed.

**What decides credit**, in this order. (a) The tree identity reproduces: `rev-parse <cand>^{tree}`. (b) The key is
another class and the receipt reproduces from the rollout by the receipt's own extraction rule. (c) The receipt binds the
**full** tree, mechanically: the verdict line carries it, or it does not. (d) Delivery happened at that identity. The
profile defines the identity as *"git tree OID of the candidate commit as it will be delivered, after any merge with the
delivery target; a key on a different subject identity does not transfer"*. Its r9 alternative is a path manifest
*"declare[d], before review"*, and no subject here declared one. So delivery at identity is witnessed only when the keyed
commit itself was a pushed `origin/master` tip.
(e) The declared contract judged the accepting round.

| S | (a) tree | (b) receipt reproduces | (c) full tree in verdict line | (d) delivered at identity | (e) contract | Ruling |
|---|---|---|---|---|---|---|
| S1 | `721e4b15…` yes | yes, excerpt `4cfd7357…` | yes | **unwitnessed**. It was a fast-forward: `82c5ed993`, the last witnessed tip before the reflog gap, is an ancestor of `ca4dd1346`, and all 110 commits up to the first witnessed push `b817774de` descend from it. But tree `721e4b15` was never a witnessed tip: four linear commits (`717cc2111`, `50c573f9d`, `fd94362a5`, `d02ca9a77`) rewrote S1's own files by +369/−13 before that push | S-file blob unchanged decl→cand | **ADOPTED-CONDITIONAL** (C5) |
| S22 | `f0800064…` yes | yes | yes (`ACCEPT f0800064…`) | yes: the candidate is itself `origin/master@{361}` (push) | unchanged | **ADOPTED: credited** |
| S25 | `e62b15ef…` yes | yes | **no**: bare `VERDICT: ACCEPT`; full tree in the excerpt body only | yes, `@{344}` | **moved**: the round-2 prompt dropped declared bar 2 (seat A) | **ADOPTED-CONDITIONAL** (C1, C3, C4) |
| S26 | `bf32a3a4…` yes | yes | no, body only | yes, `@{338}` | unchanged | **ADOPTED-CONDITIONAL** (C1, C3) |
| S27 | `f52c03ac…` yes | yes | no, body only | yes, `@{333}` | unchanged | **ADOPTED-CONDITIONAL** (C1) |
| S29 | `d4223e59…` yes | yes | no, body only | yes, `@{321}` | unchanged | **ADOPTED-CONDITIONAL** (C1) |
| S30 | `7cafba0c…` yes | yes | no: the excerpt names the 9-hex prefix `7cafba0c1` only; the full tree appears only in the key's own tool output (rollout record 29) | yes, `@{317}` | unchanged | **ADOPTED-CONDITIONAL** (C2) |
| S31 | `831c204a…` yes | yes | no, body only | yes, `@{312}` | **moved**: the round-2 prompt bar V6 adds "leaves the PNG byte-identical" to the declared bar (round 1 U6, "exits 0"); the declaration file was not amended | **ADOPTED-CONDITIONAL** (C1, C4) |
| S13 | `d44d8fb7…` yes | yes, and printed at Outcome time | yes | **no**: delivered inside merge `8e35ae83c` (tree `b30f8cee…`), whose second parent `8020e55a6` lacks the candidate and carries peer pushes `57d70da90`, `5f16e2ed6`, `aab23cc49`. That merge changed `coordination/harvest/harvest_runner.py` (+21 lines), the file the S13 candidate changed. `c6f35501e` has no `origin/master` reflog entry | unchanged | **REJECTED(key on a different subject identity; counts zero)** |
| S12 | `d8dc5750…` yes | yes | yes | no: merge `7b309cc81`, tree `00559844…` (the filing's own finding, re-run) | — | **REJECTED(stays zero, as filed)** |

**Conditions.** Each conditional subject counts zero until its condition is discharged in a later filing and an arbiter
other than the steward confirms it.
- **C1.** K5's observable is *"the acceptance receipt bound to the same identity"*. A bare verdict line does not bind
  identity: the tree is bound only through the excerpt digest over prose. To
  discharge: either the steward's next profile revision says an excerpt-body 40-hex identity, under the excerpt digest,
  satisfies *"Receipts bind each key to that identity"*, or the subject is re-keyed with a verdict line carrying
  `identity=<40-hex>`. Re-extracting under a new rule chosen after reading the logs does not discharge it.
- **C2 (S30).** C1, and the identity must be bound by more than a prefix (*"Prefixes are locators only"*, profile). A
  rule that reaches a tool-output record would need its own ruling. Otherwise, re-key.
- **C3 (S25, S26).** The profile's gate list reads *"Human gates (K2) | releases, security-sensitive paths, frozen
  bytes, and anything the project's register lists"*. The filing itself classes `scripts/pairprog-scope-match.py` and the
  untrusted-peer fence in `scripts/render-parallel-prompt.sh` as security-sensitive paths.
  A model key alone accepted them, with no register at the time (`K2-REGISTER.md` was first added at Conjugal `dbabbe06e`,
  2026-09-27). To discharge: an attended human verifier other than the producer attests each subject at its exact tree,
  or a register row in force before acceptance exempts it. A register added afterwards does not reach back.
- **C4 (S31; also S25).** The round-2 contract differs from the declared one. Round-1 prompt record 9 has SHA-256 prefix
  `c19b4b8b397b5a8a`; round 2 has `77da50a07e88a92f`. To discharge: a reader other than the producer shows that every
  declared bar is implied by its round-2 counterpart, quoting both prompt digests in full. The change looks like a
  tightening, but the rule is *"the same contract judges every round"*. For S25, whose round 2 dropped declared bar 2,
  the same showing applies, with both round prompts' digests quoted in full.
- **C5 (S1).** The accepted tree was never witnessed as delivered. To discharge: a witnessed delivery of tree
  `721e4b15` itself (a reflog or push record from the clone that pushed between 2026-09-15 and 2026-09-16), or, for
  later subjects, a path-manifest identity declared before work under profile r9 or later.

**On S13, this departs from the filing.** The filing's delivery test (a), *"an ancestor of the candidate's parent was a
pushed origin/master tip, with no merge commit between it and the candidate"*, is satisfied by S13 and does not decide
delivery: the merge came **after** the candidate, on the way to `master`. The filing says the same of its older
first-parent test for S12. The decisive evidence for S22..S31 is the reflog (each candidate is a pushed tip). S13 has no
such entry, and the reflog does cover 2026-09-18 (`@{464}` = `7b309cc81`, 18:51:37). So S13 fails on the rule that
zeroes S12. **The only subject the filing calls receipted at Outcome time counts zero.** That outcome is unrelated to
the timing question.

**On S1, this departs from `dc2a719` only in part.** That ruling refused credit because every load-bearing line was
`[INLINE]`. The receipt now exists, and cloudvore reproduced it from rollout file 7, record 91: excerpt digest
`4cfd7357…`, model `gpt-6-astra`, and a verdict line that binds the full tree. So the receipt half is discharged.
Delivery is not. This clone's `origin/master` reflog has a gap from 2026-09-13 to 2026-09-16. The first witnessed push
after S1 (`b817774de`) carries four commits that rewrote S1's own files (+369/−13). A fast-forward proves ancestry, not
delivery of the keyed tree. Crediting S1 while zeroing S13 for a 21-line merge into its subject file would be
inconsistent, so S1 is conditional (C5). This costs Conjugal nothing, because S22 carries its criterion-1 credit alone.

**Ledger effect.** For conjugal, the steward's row should read `1 closed end-to-end (S22)`. That form parses under
`E2E_COUNT_RE` in `tools/kernel-e2e.py`. `kernel-e2e.py` then reads conjugal as 1 project, so `PROJECTS WITH >=1 CLOSED`
goes from 0 to 1, against 5 needed. No other project's state changes.

## Findings — new lines (`## Clauses` and `## Profile fields`, 2026-09-26)

K1 "A candidate is never accepted on evidence whose only author is its producer" | ADOPTED | FIT recorded, no text change. The key half is now receipted: `turn_context` models = `['gpt-6-astra']` in all nine accepting rollouts (E3). The producer half is trailer testimony (`Claude Opus 5` on 9 of 10 candidates, none on `c6f35501e`, E4), and the filing says so itself.
K2 "Each project keeps one register of what needs the owner and what does not" | ADOPTED | INSTANCE-FAILURE, health. No register existed in the window: `K2-REGISTER.md` is absent at `1755502d6` and first added at `dbabbe06e` (2026-09-27, E5). Its later existence does not change this window's verdict; see C3.
K3 "for one held subject, its claim record and the procedure by which someone other than the claimant decides it stale" | ADOPTED | INSTANCE-FAILURE, health. The S25 cost is verified in Conjugal `af0a21d3f`: *"moved the branch while the MAIN checkout had master"*, *"Unstaged content has no reflog"* (E5).
K4 "Never exit code, output size or silence" | ADOPTED | FIT recorded, no text change. The negative cases are S-file testimony. The `check-ordering.py` point (a witness that reads git, not prose) re-runs: S21 and S28 rows are `NO-CANDIDATE-CITED` with exit 0 (E2).
K5 "the profile line recorded before work, and the acceptance receipt bound to the same identity" | ADOPTED-CONDITIONAL(conjugal) | Ordering re-runs: `SUMMARY subjects=33 ok=24 open=0 failures=0 -> PASS`, exit 0, at `1755502d6` (E2). The r9 resolution re-runs: `git log -1 --before=<decl> -- code.md` → `9e23075` (E6). Receipts reproduce (E3). Condition: a recompute command is not a recorded line, and the PROOF case has now arrived. `code.md` moved to **r10** at bus `d53bac1` (2026-10-01), so S18..S33's own commands, run today, print r10. Credit here rests on the arbiter's date resolution. Future declarations must record the literal `code@r<n>`.
K6 "Every acceptance includes a key from an independence class other than the producer's" | ADOPTED | FIT recorded, no text change. Class `codex-openai` against a `claude` producer on every credited or conditional subject (E3, E4). The construct-to-verify lesson from S19 is recorded as an instance lesson.
K7 "the delivery target, and how the project detects an accepted subject that never delivered" | ADOPTED | INSTANCE-FAILURE, health, **widened**. Delivery at identity also failed for S13 (merge `8e35ae83c`, E1), not only S12. `check-ordering.py` prints `delivered=yes` for both, which shows the detector gap the line names. The filing's statement "Delivery at identity closed for S13" is REFUTED.
K8 "Running out of quota means rotating or parking the work that needs inference, never failing the factory closed" | ADOPTED | INSTANCE-FAILURE, health. (a) is a measured fail-closed event, fixed but unaccepted. This line answers the old K8 PROOF in the negative: no S18..S33 park names a resume actor.
K9 "the resumability gate's command and its last passing output" | ADOPTED | FIT, no text change. Re-run at `1755502d6`: `PASS resumability (docs/architecture/approach-a @ 1755502d6) ...`, exit 0. The live blob `0f055821…` equals the copy on `origin/review/conjugal-kernel-2026-09-18` (E7). Landing note: bus master and the 2026-09-26 branch both still carry the stale copy `46aaa31b…`. The steward lands `0f055821` with this filing, or the dc2a719 K9 condition is undone on master.
K10 "Missing, `unknown` or mismatched account identity makes the inventory stale" | ADOPTED | INSTANCE-FAILURE, health.
K11 "the quoted title line of each rule the project confirms it meets" | ADOPTED | FIT, with a correction. The line's PROOF (*"a rule below this filing violates"*) is not met: R2 governs completion evidence and does not reach a delivery claim. The S13 claim "ACCEPTED, delivered at identity" is wrong (E1). It is corrected under K7 and P:code subject-identity, not here. The posture line is tool-computed, and `harvest-status.py` raises no flag on it (E0).
K12 "The steward harvests every filing and answers each one" | ADOPTED | INSTANCE-FAILURE, health; this file is the answer. Re-run today: `conjugal STALE blob=0666f1e8 ... findings=46 untested=0`, `open=1`, exit 1. `kernel-e2e.py --json` → `criterion_1_projects: 0`, `open_filings: {conjugal: STALE}` (E0). Instrument defect, measured: run under the default Windows console code page, `kernel-e2e.py` prints `REFUSE kernel-e2e: harvest-status.py produced no filing rows`, exit 2, because the child's output cannot be encoded. With `PYTHONUTF8=1` it runs. That gate fails closed, and the fail-closed is correct, but it hides the verdict. Follow-up for the tool's owner.
P:code subject-identity "a key on a different subject identity does not transfer" | ADOPTED | INSTANCE-FAILURE, health, **widened to S13**: merge `8e35ae83c` changed the subject's own file (E1). Correction: "Eight other acceptances were delivered as the exact keyed commit" should read seven (S22, S25, S26, S27, S29, S30, S31).
P:code artifact-store "build outputs are not the subject" | ADOPTED | FIT, no text change.
P:code determinism-class "flaky suites are declared per test, never silently retried" | ADOPTED | INSTANCE-FAILURE, health.
P:code acceptance-evidence "the same contract judges every round" | ADOPTED | INSTANCE-FAILURE, health. Correction: S31's round-2 contract **is** recoverable, from the rollout rather than the tree. Round-2 prompt record 9 (`77da50a0…`) differs from round 1 (`c19b4b8b…`), and bar U6 became V6 (E8); see C4. For the claimed subjects, the declaration blob is identical at declaration and at candidate (E8), so git content-addressing bound the declared text. It bound no harness, budget or rule digest.
P:code independent-key "Review-key charters declare execution or static review before dispatch" | ADOPTED | INSTANCE-FAILURE, health.
P:code resource-terminals "parked work names its resume condition and the actor who can satisfy it" | ADOPTED | INSTANCE-FAILURE, health.
P:code delivery-target "Stricter instance closure mechanisms and their budgets are declared before work" | ADOPTED | INSTANCE-FAILURE, health.
P:code human-gates "releases, security-sensitive paths, frozen bytes" | ADOPTED | INSTANCE-FAILURE, health. It now also bears on credit: C3.
P:code budgets "window counts of subjects accepted, delivered, parked and closed undelivered" | ADOPTED | INSTANCE-FAILURE, health. Corrections: witnessed delivery at identity in the window is 7 (S22, S25..S27, S29..S31). S1 is unwitnessed and S13 is removed. Accepted-undelivered-at-identity is 2 (S12, S13).
P:code claims "A mutable checkout another project executes from is itself a claimed subject" | ADOPTED | INSTANCE-FAILURE, health.
P:code dispatch-preflight "the spending tool runs the project's resume gate before dispatch" | ADOPTED | INSTANCE-FAILURE, health.

## Findings — kept lines (blob 4598b8ed, carried verbatim)

K1 (kept) "A candidate is never accepted on evidence whose only author is its producer" | ADOPTED | FIT, no text change. S1's receipt now reproduces (E3).
K2 (kept) "Each project keeps one register" | ADOPTED | INSTANCE-FAILURE, health; dc2a719's reclassification was honoured.
K3 (kept) "its claim record and the procedure by which someone other than the claimant decides it stale" | ADOPTED | Identity half FIT. Claim half INSTANCE-FAILURE, health.
K4 (kept) "Never exit code, output size or silence" | ADOPTED | FIT. The mutation evidence is the same as dc2a719 re-ran (19 cases / 113 ok; `-z` removed → exit 1, 10 failures; restored → green).
K5 (kept) "the profile line recorded before work" | ADOPTED | FIT for S1. `check-ordering.py`: `S1 OK decl=96d1b3a@...18:18:10 cand=ca4dd13@...19:03:48` (E2).
K6 (kept) "Every acceptance includes a key from an independence class other than the producer's" | ADOPTED | FIT. S1's receipt reproduces (E3); the proposed wording is ruled under Untested 2.
K7 (kept) "how the project detects an accepted subject that never delivered" | ADOPTED | INSTANCE-FAILURE, health.
K8 (kept) "Running out of quota means rotating or parking" | ADOPTED | INSTANCE-FAILURE, health. The S11 correction is accepted.
K9 (kept) "the resumability gate's command and its last passing output" | ADOPTED | dc2a719's condition was met on `origin/review/conjugal-kernel-2026-09-18`: copy `0f055821` = live (E7). See the landing note under the new K9.
K10 (kept) "Missing, `unknown` or mismatched account identity makes the inventory stale" | ADOPTED | INSTANCE-FAILURE, health.
K11 (kept) "the quoted title line of each rule" | ADOPTED | The replaced evidence (a tool-computed posture) is what dc2a719 asked for. This blob made no S13 claim.
K12 (kept) "The steward harvests every filing and answers each one" | ADOPTED | INSTANCE-FAILURE, health. The ledger-row gap stands: this ruling also produces no automated row.
P:code subject-identity (kept FIT) "git tree OID of the candidate commit as it will be delivered" | REJECTED(restatement of K3's identity half) | As in dc2a719. The author-versus-committer FRICTION condition stays open there.
P:code acceptance-evidence (kept) "bind the acceptance contract by digest" | ADOPTED | INSTANCE-FAILURE, health.
P:code independent-key (kept FIT) "a verifier from another model family (R3)" | REJECTED(restatement of K6) | The line itself asks for no credit.
P:code resource-terminals (kept) "parked work names its resume condition" | ADOPTED | INSTANCE-FAILURE, health.
P:code delivery-target (kept FIT) "integration branch via the project's landing path" | ADOPTED | FIT, no text change: the landing path is a fast-forward. Delivery at the keyed identity is a separate question (S1: C5).
P:code dispatch-preflight (kept) | ADOPTED | INSTANCE-FAILURE, health.
P:code claims (kept) | ADOPTED | INSTANCE-FAILURE, health; the same fact as K3.
P:code human-gates (kept) | ADOPTED | INSTANCE-FAILURE, health.
P:code budgets (kept) | ADOPTED | INSTANCE-FAILURE, health.
P:code artifact-store (kept FIT) | ADOPTED | FIT, no text change.
P:code determinism-class (kept) | ADOPTED | INSTANCE-FAILURE, health.

## Untested

The filing carries 8 items (4 kept, 4 new). `harvest-status.py` prints `untested=0` because it counts only `K`/`P` lines.
Kernel K12 asks for a disposition on every Untested item, so all 8 are answered.

U1 TRAPS row (`An assertion that passes without testing what it names`) | ROUTED(owner) | It turns on how a trap is filed, and R14.1/R14.6 (written by cloudvore, unread by the owner) govern exactly that. Cloudvore does not rule on its own unread ruling.
U2 Proposed K6 wording (`KEY_UNAVAILABLE_BY_PROVIDER` typed terminal) | REJECTED(already covered; one profile) | The profile's resource-terminals field already makes *"independent key unavailable"* a typed terminal with no partial green. Kernel text needs FRICTION from two profiles (§5).
U3 S10 "no K6 route for security subjects" | ADOPTED-CONDITIONAL(a second bench reports it) | Recorded as an instance claim. C3 now shows the cost on S25 and S26.
U4 `RULINGS.md` mentions the kernel zero times | ADOPTED | True when filed, and resolved since. Re-run today at bus `bb93367`: `grep -ci "fleet-factory-kernel\|factory kernel" RULINGS.md` → 5.
U5 Five provider-filter terminations and one no-verdict | ADOPTED | Recorded as an instance lesson (construct versus verify), with no kernel text.
U6 A non-model oracle as a K6 class | ROUTED(owner) | This is a question of kernel wording (*"a measured score against held-out ground truth"*), and nothing was accepted on it. The steward is Conjugal, the filer, so it cannot rule on this (§5). The owner is the alternate.
U7 Declaration prose is an unguarded surface: a lesson for `TRAPS.md` | ROUTED(owner) | Trap filing form, R14; same reason as U1.
U8 Subject shape predicts parks | ADOPTED-CONDITIONAL(a second bench reports it) | One bench.

## Header

HEADER: `subjects: 9 end-to-end claimed` | ACCEPTED AS RECORDED, CREDIT 1 OF 9 | See `## Criterion 1`. S22 is credited, S1 and S25..S31 are conditional, and S13 counts zero.
HEADER: `health: assurance=UNSATISFIED operability=PRESSURED` | CONFIRMED | 29 INSTANCE-FAILURE lines are adopted as health.
HEADER: `posture:` R9 line | CONFIRMED | Tool-computed; `harvest-status.py` flags `-` (E0).
HEADER: `profile: code@r9` | ACCEPTED, RE-FILE OWED | The profile is now r10 (bus `d53bac1`, 2026-10-01: a substitution sentence in resource-terminals). PROMPT K's revision trigger fired.

## Evidence

All of the following was run on 2026-10-06 CDT by cloudvore, between about 2026-10-07T00:00Z and 01:05Z UTC. `date -u` read 00:42Z at worktree creation and 01:02Z at the last check. It was read-only against Conjugal (two
detached worktrees `C:/t/conj-1` at `db9fd5643`, `C:/t/conj-2` at `1755502d6`; `C:/code/Conjugal`'s working tree was not
touched). Rollouts were read-only under `~/.codex/sessions/2026/09/`.

**E0 — bus state.**
```
$ git -C <bus> rev-parse origin/review/conjugal-kernel-2026-09-26:adjudications/factory-kernel/conjugal.md
0666f1e84632c925557c8e1c64159d85031f66ff
$ python tools/harvest-status.py factory-kernel            # exit 1
subject=factory-kernel spec=specs/fleet-factory-kernel.md filings=10
  conjugal                     STALE       blob=0666f1e8 ref=origin/review/conjugal-kernel-2026-09-26 findings=46 untested=0 posture='conjugal-standard-PARTIAL (0/17 lanes; ...)' flags=-
      superseded copy blob=4598b8ed ref=origin/review/conjugal-kernel-2026-09-18
open=1  (UNHARVESTED or STALE; 0 means every current filing has a disposition)
$ python tools/kernel-e2e.py --json                        # default console code page
REFUSE kernel-e2e: harvest-status.py produced no filing rows     # exit 2
$ PYTHONUTF8=1 PYTHONIOENCODING=utf-8 python tools/kernel-e2e.py --json    # exit 1
"closed_end_to_end": 0, "criterion_1_met": false, "criterion_1_projects": 0, "ledger_rows": 23,
"open_filings": {"conjugal": "STALE"}, "per_project_closed": {... "conjugal": 0 ...}
```

**E1 — identity, ancestry, delivery** (Conjugal `origin/master` = `db9fd5643a3c`).
```
$ for c: git rev-parse $c^{tree}; git merge-base --is-ancestor $c origin/master
S1  ca4dd1346 tree=721e4b15677a579d1fab3fd430a785d7974e243d match=yes ancestor exit=0 parents=1
S12 0a738a6b4 tree=d8dc575001d4a84f310a96c8e2a03061506b2ace match=yes ancestor exit=0 parents=1
S13 c6f35501e tree=d44d8fb78b73d505c25d7ac0d3259251ca83bc50 match=yes ancestor exit=0 parents=1
S22 c323c4af7 tree=f08000648013d77360d0e75f88d23d84d2965fc8 match=yes ancestor exit=0 parents=1
S25 d7e2fc224 tree=e62b15efe2e125c83b6399d243364bd86b340471 match=yes ancestor exit=0 parents=1
S26 ee4677985 tree=bf32a3a454e08401064bfb4cda18c207525b0f74 match=yes ancestor exit=0 parents=1
S27 96fcad8ae tree=f52c03ac499ab7fbeabacdb8756f53cd1a521646 match=yes ancestor exit=0 parents=1
S29 272be21e3 tree=d4223e59645634d1205ed3419913747659e0beb4 match=yes ancestor exit=0 parents=1
S30 8cab657f6 tree=7cafba0c16649dd05027beb949e7b0b79c114f65 match=yes ancestor exit=0 parents=1
S31 e93985e54 tree=831c204a9830893972db7d8cccc029e0eebd1a74 match=yes ancestor exit=0 parents=1
$ git rev-list --first-parent origin/master | grep <cand>     # all ten: yes (does NOT discriminate: see S12, S13)
$ git reflog show refs/remotes/origin/master --format='%H %gd %gs'   # 560 entries at read time, @{559} 2026-09-11; gap 09-13 16:16 .. 09-16 12:46
# NOTE: @{n} indices drift as this clone fetches; a re-reader should match by SHA, not by index
c323c4af7 @{361} update by push   d7e2fc224 @{344}   ee4677985 @{338}   96fcad8ae @{333}
272be21e3 @{321}   8cab657f6 @{317}   e93985e54 @{312}   7b309cc81 @{464} (2026-09-18 18:51:37)
ca4dd1346 0 entries   0a738a6b4 0 entries   c6f35501e 0 entries
# S12
$ git cat-file -p 7b309cc81 → parents 7b0ad750b bb86742db; tree 00559844199291ad61474439529d42497b3259d2
$ git merge-base --is-ancestor 0a738a6b4 bb86742db → exit 1
# S13
$ git log --first-parent --format='%h %p %s' 8e35ae83c -6
8e35ae83c 9407cb9db 8020e55a6 Merge branch 'master' into claude/confident-elbakyan-b32fbc   (= origin/master@{459})
9407cb9db … fe5670190 … d7902e487 … 564844ab4 … c6f35501e 51d3e9489  (S13 candidate)
$ git merge-base --is-ancestor c6f35501e 8020e55a6 → exit 1
$ git merge-base --is-ancestor 57d70da90 8020e55a6 → exit 0     # peer pushes @{460..462}: aab23cc49 5f16e2ed6 57d70da90, all not descendants of c6f35501e
$ git rev-parse 8e35ae83c^{tree} → b30f8ceee417ceaad5402af284daac3914ba223e  (≠ d44d8fb7…)
$ git diff --name-only 9e7aad0fe c6f35501e   → coordination/harvest/harvest_runner.py, …/test_harvest_runner.py, s13-replay fixtures
$ git diff --stat 9407cb9db 8e35ae83c -- coordination/harvest/harvest_runner.py → 1 file changed, 21 insertions(+)
# S1
$ git merge-base --is-ancestor 82c5ed993 ca4dd1346 → exit 0   # 82c5ed993 = last witnessed tip before the gap (2026-09-13 16:16:15)
$ git rev-list --count ca4dd1346..b817774de → 110             # b817774de = first witnessed push containing S1 (2026-09-16 12:46:59)
$ 717cc2111 (09-15 20:17), 50c573f9d (20:34), fd94362a5 (09-16 02:01), d02ca9a77 (07:43): each descends from ca4dd1346 (exit 0)
$ git diff --shortstat ca4dd1346 d02ca9a77 -- <S1's two files> → 2 files changed, 369 insertions(+), 13 deletions(-)
```

**E2 — ordering witness.**
```
$ (C:/t/conj-2 @ 1755502d6) python coordination/kernel-dogfood/check-ordering.py ; exit=0
S1 OK decl=96d1b3a@2026-09-15T18:18:10-05:00 cand=ca4dd13@2026-09-15T19:03:48-05:00 identity=ok delivered=yes outcome=ACCEPTED
S12 OK … outcome=ACCEPTED     S13 OK decl=7fe8864@…18:50:41 cand=c6f3550@…19:22:26 identity=ok delivered=yes outcome=ACCEPTED
S22 OK decl=ae02d54@2026-09-22T01:06:51-05:00 cand=c323c4a@2026-09-22T01:24:16-05:00 identity=ok delivered=yes outcome=ACCEPTED
S25 OK … S26 OK … S27 OK … S29 OK … S30 OK … S31 OK … (all identity=ok delivered=yes outcome=ACCEPTED)
S21 NO-CANDIDATE-CITED …   S28 NO-CANDIDATE-CITED …
SUMMARY subjects=33 ok=24 open=0 failures=0 -> PASS pinned=bd96a7204
$ (C:/t/conj-1 @ db9fd5643, today's master) same script → SUMMARY subjects=57 ok=27 open=0 failures=16 -> FAIL, exit 1
  (the failures are S34..S107, outside this filing's window; they belong to Conjugal's next filing)
```

**E3 — receipts recomputed from the rollouts by each receipt's own rule.** Rule (S12..S31 receipts): rollout SHA-256 of
the whole file. Excerpt = the last `response_item` with `payload.type=message`, `role=assistant`, `phase=final_answer`,
UTF-8 concatenation of `content[].text`. Verdict line = the line in it beginning `VERDICT`/`ACCEPT`/`REFUSE`. S1 rule:
the record at line 91 of file 7. Script: a read-only Python reader that prints digests and booleans, never excerpt text.
```
S12 R2 bytes=675371  rollout=cf74d5c9…6c16 ✓ rec=66  excerpt=d27776f4…28ad0 ✓ verdict='VERDICT: ACCEPTED identity=d8dc5750…2ace key=gpt-6-astra class=codex-openai' 223a9cf4…56cf ✓ models=[gpt-6-astra]
S13 R1 bytes=1045281 rollout=f2409155…e337 ✓ rec=254 excerpt=eb37a32f…cd5c ✓ verdict='VERDICT: ACCEPTED identity=d44d8fb7…bc50 …' 23ddcd4e…3da0 ✓ models=[gpt-6-astra]
S22 R1 bytes=684514  rollout=6a2f6b24…486f ✓ rec=203 excerpt=d6bf6765…e5c5 ✓ verdict='ACCEPT f08000648013d77360d0e75f88d23d84d2965fc8' 7d452bde…71d8 ✓ models=[gpt-6-astra]
S25 R2 bytes=540629  rollout=3937177c…6bfa ✓ rec=57  excerpt=91c74aef…4c8b ✓ verdict='VERDICT: ACCEPT' f422a3f0…d1e7 ✓ full_tree_in_line=False in_excerpt=True
S26 R1 bytes=714436  rollout=914d4945…2b96 ✓ rec=65  excerpt=1277d2a6…6c0c ✓ verdict='VERDICT: ACCEPT' ✓ in_line=False in_excerpt=True
S27 R1 bytes=716128  rollout=2b9ccccf…96a6 ✓ rec=164 excerpt=9d972f8d…82b6 ✓ verdict='VERDICT: ACCEPT' ✓ in_line=False in_excerpt=True
S29 R1 bytes=769315  rollout=7fab308e…81d5 ✓ rec=172 excerpt=152ab06d…0ff6 ✓ verdict='VERDICT: ACCEPT' ✓ in_line=False in_excerpt=True
S30 R1 bytes=355951  rollout=cef728bf…5893 ✓ rec=49  excerpt=3203875c…3c5e ✓ verdict='VERDICT: ACCEPT' ✓ in_line=False in_excerpt=False prefix9_in_excerpt=True
     full tree occurs only in records 29 (custom_tool_call_output: the key's own rev-parse) and 31 (event echo)
S31 R2 bytes=453605  rollout=161e80da…e310 ✓ rec=72  excerpt=afd9b8bc…00f6 ✓ verdict='VERDICT: ACCEPT' ✓ in_line=False in_excerpt=True
S1  f7   bytes=646775  rollout=c01100d0…a5ce9 ✓ rec=91 ts=2026-09-16T00:08:58.797Z excerpt=4cfd7357…05e2 ✓ verdict='VERDICT: ACCEPTED  identity=721e4b15…243d  key=gpt-6-astra  class=codex-openai' models=[gpt-6-astra]
(✓ = equal to the digest printed in the receipt file on the filing branch; every check exit 0)
$ git show origin/review/conjugal-kernel-2026-09-26:…/conjugal-receipts/S1-astra-acceptance.md | sha256sum
66034ac71082662b3f86cb4bef1771e750c85d41aea6a2f951487cf773017ca2   (= the filing's cited digest)
```

**E4 — producer trailers.** `git log -1 --format='%(trailers:key=Co-Authored-By,valueonly)'`: `Claude Opus 5` on
ca4dd1346, 0a738a6b4, c323c4af7, d7e2fc224, ee4677985, 96fcad8ae, 272be21e3, 8cab657f6, e93985e54; empty on c6f35501e.

**E5 — register and S25 cost.** `ls coordination/kernel-dogfood/K2-REGISTER.md` at `1755502d6` → No such file.
`git log --diff-filter=A -- …/K2-REGISTER.md` → `dbabbe06e 2026-09-27 18:26:28 +0100`. The register (27 lines at
`db9fd5643`) gates "Security-sensitive paths". `git show af0a21d3f | grep -n "MAIN checkout\|no reflog"` → lines 14, 24, 68.

**E6 — r9 resolution.** `git log -1 --format=%h --before=2026-09-21T01:24:35-05:00 origin/master -- specs/fleet-factory-kernel/profiles/code.md`
→ `9e23075`. The same for `2026-09-22T22:23:29-05:00` → `9e23075`. `git log origin/master -- …/code.md` → `d53bac1`
(2026-10-01, r10) is newer.

**E7 — K9.** `(conj-2) python coordination/tools/resumability-check.py` → `PASS resumability (docs/architecture/approach-a
@ 1755502d6): tree-only resume possible; no live values in RESUME.md`, exit 0. `rev-parse HEAD:coordination/tools/resumability-check.py`
→ `0f05582128a3…`. Bus: `…-2026-09-18:tools/conjugal-reference/resumability-check.py` → `0f05582128a3…`;
`…-2026-09-26:tools/conjugal-reference/resumability-check.py` → `46aaa31baf09…` (stale).

**E8 — contracts.** `git rev-list --count <decl>..<cand> -- coordination/kernel-dogfood/<S-file>` → 0 for S1, S22, S25,
S26, S27, S29, S30, S31. The S-file blob is equal at declaration and candidate for all eight. S31: in both rollouts, the
user prompt is record 9. R1 is 4124 bytes, SHA-256 `c19b4b8b397b5a8a…`, with bar `U6 ... build.py exits 0`. R2 is 4336
bytes, SHA-256 `77da50a07e88a92f…`, with bar `V6 ... build.py exits 0 AND leaves ...-5k.png byte-identical`. The declared
bar 5 at `a5b496be4` reads `python docs/product/roadmap-board/build.py exits 0`.

## What the steward does next

1. Append one HARVESTS.md row for conjugal, blob `0666f1e8`, kernel r5 / profile code@r9, with the subjects cell reading
   `1 closed end-to-end (S22); 7 conditional (S1, S25-S27, S29-S31); S12, S13 zero`, plus the verdict counts above.
   The row is the steward's to write; cloudvore did not touch HARVESTS.md.
2. Land this file on bus master, then confirm `harvest-status.py` reads conjugal HARVESTED. `kernel-e2e.py` should then
   read `criterion_1_projects: 1`. Run it with `PYTHONUTF8=1` until the encoding defect (K12) is fixed.
3. When landing the filing, carry the `0f055821` copy of `resumability-check.py` (K9).
4. Conjugal's next filing: re-file against code@r10; discharge or withdraw C1–C4; record literal profile revisions (K5);
   correct the S13 and seven-not-eight statements; and add a delivery-at-identity detector that reads the reflog or a
   merge-on-path test (K7).
5. Owner: U1 and U7 (R14), and U6 (kernel wording; the steward is the filer).

## Self-check

Two read-only adversary seats checked the draft before commit. Their verdicts are below. Each reproduced defect was
fixed in place.

**Seat A** (claude-opus, read-only; re-ran E1, E2, E3 and E8 independently). **Verdict: SOUND-WITH-FIXES.**
- Reproduced: the S13 merge `8e35ae83c` (its second parent lacks the candidate; it changes `harvest_runner.py`; no
  reflog entry for `c6f35501e`). Reflog push entries for S22, S25 and S30. Rollout digests for S1, S22 and S30, and that
  S30's excerpt carries only a prefix. `check-ordering.py` PASS at `1755502d6`. The S31 prompt digests.
- Fix 1: the S1 credit was unsupported. The first push containing `ca4dd1346` is `b817774de` (2026-09-16 12:46), after
  four commits (`717cc2111`, `50c573f9d`, `fd94362a5`, `d02ca9a77`) rewrote S1's own files by +369/−13. `8d431e43e` is
  not on `origin/master`'s first-parent line.
- Fix 2: S25's round 2 dropped declared bar 2.
- Fix 3: E1's count, date and run timestamp; reflog indices drift.

**Seat B** (claude-opus, read-only; rulings against kernel r5, profile r9/r10, PROMPT K, README, dc2a719 and R14).
Its report did not reach this session directly. The integrator relayed its fixes, and every one was taken.
**Verdict: fixes required (SOUND-WITH-FIXES).**
- Remove the "no merge touched the subject" test, and ground delivery in the profile's identity sentence.
- S1's fast-forward ancestry (`82c5ed993` is an ancestor of `ca4dd1346`; all 110 commits descend from it) belongs in the
  file.
- Re-ground C1 on K5's observable, and C3 on the profile's gate list.
- Correct the timing facts: S1's digests were on the bus at `15bf9dd` on 09-18, and S13's were printed at Outcome.
- K11: R2 does not reach a delivery claim, so ADOPTED with a correction, not REJECTED.
- U4 was resolved since, so ADOPTED.
- U6 cannot go to the steward, who is the filer.
- `spec_commit` must name r9 `9e23075`.

**Where the seats conflicted** (S1: B, fast-forward; A, tree never a witnessed tip), the integrator ruled
ADOPTED-CONDITIONAL. S1 is conditional (C5), not credited. Crediting S1 would have been inconsistent with zeroing S13.

**What changed after the seats.**
- S1 moved from credited to ADOPTED-CONDITIONAL (C5).
- S25 gained C4.
- C1 and C3 were re-grounded.
- The timing facts were corrected.
- K11 moved from REJECTED to ADOPTED.
- U4 moved from REJECTED to ADOPTED.
- U6 moved from ROUTED(steward) to ROUTED(owner).
- The P:code budgets and kept delivery-target lines were corrected.
- E1 was extended and its timestamp fixed.
- The headline counts were recomputed. Finding lines: 43 / 1 / 2 / 0. Untested: 2 / 2 / 1 / 3. Credit falls to S22
  alone, and criterion 1 is unchanged at 1 project for conjugal.
