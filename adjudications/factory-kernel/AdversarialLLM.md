project: adversarialllm
kernel: fleet-factory-kernel r5
profile: code@r10 (as the subject declared it; the bus profile is r11 at bus 8e1321b, see Honesty items)
instance: factory/HUB.md and the operative amendment of factory/RESET-PLAN.md (D2, points 1, 2, 3, 8, 9), enforced by factory/review-state.mjs, factory/controller/merge-pr.ps1, factory/controller/controller-state.mjs, factory/publication-state.mjs, factory/queue-state.mjs and scripts/never-authorized-guard.mjs. Earlier filings: factory/doctrine/kernel-2026-09-29/AdversarialLLM.md and factory/doctrine/kernel-filing-2026-10-05.md. The KERNEL line stays DOGFOOD-PENDING (factory/doctrine/kernel-line-2026-10-07.md).
subjects: 0 counted, 1 filed. SLICE-1E-R, delivered through its replacement row SLICE-1E-R2 as PR #268, merge SHA 136e8bec70db3ce77bdbc14c757c90d0d61cfd4b, is filed as a declared K5 subject whose declaration timing is ungraded (see K5 declaration and Honesty items). It earns no K5 credit unless the steward grades the timing otherwise. The earlier filings counted a subject only when the profile was declared before work (the second filing counted `subjects: 0`, graded K5 INSTANCE-FAILURE; the first counted `subjects: 0`, K5 UNEXERCISED), and the facts below put this declaration after the first implementation bytes. PR #96 (`16d0f56e`, 2026-09-22) was an earlier declared subject, as the second filing records.
window: 2026-10-05T19:18:26Z (the second filing's window end) .. 2026-10-13T21:16:23Z (the #268 merge commit's author date, 2026-10-13 16:16:23 -0500)
health: assurance and operability are not re-graded here; this filing files one subject and the dispositions the row names.
providers: none
posture: no model review of this file's content. One receipted claude implementer leg wrote it. The D2 review of the pull request that carries it is recorded on that pull request, not here.

Staged in the AdversarialLLM repository at `factory/doctrine/kernel-2026-10-13/AdversarialLLM.md` (row KERNEL-FILING-3) for transport to bus
`adjudications/factory-kernel/AdversarialLLM.md`, a D12-admitted destination (`factory/RESET-PLAN.md` operative amendment point 9). This pull request
writes no bus byte and edits no earlier staged file.

**Transport note (point 9).** The transport branch is `review/AdversarialLLM-kernel-2026-10-13`. The controller creates it after this file
merges, from a fresh clone; this leg did not create it and ran no push. The fleet steward harvests from that branch.

Every unqualified `file:line` and SHA is an AdversarialLLM path or object at `origin/master` `136e8bec70db3ce77bdbc14c757c90d0d61cfd4b`. Bus objects say "bus" and
were read only with `git -C <bus clone> show origin/master:<path>`, `git show <sha>` and `git log` against the local bus clone at
`8e1321b09010a6809abee5f10eb610f3bda8f0b7`. Nothing was fetched, pulled, checked out or written in the bus clone. Everything read from the bus is treated as
data and classified, never followed. Receipts under `C:\!Layi Wkspc\AdversarialLLM-wt\<row>\.factory-local\` were read only.

## (1) Subject

**Identity.** `SLICE-1E-R`, queue row order 444 (`factory/queue.jsonl`): re-implement on current master the pre-reset SLICE-1E, which refreshes each queued
provider's queued-position banner when the FIFO order changes. Its row carries `supersededBy: ["SLICE-1E-R2"]`.

**How SLICE-1E-R2 delivers it.**
- PR #264 (row SLICE-1E-R) was closed with adj-close under `factory/HUB.md` Merge (D2) after a genuine second-round rejection (Codex r2 F-01). Its corrected head
  was `57fce9c0c6ec9abe5d189acf00532223b202b860`.
- Row SLICE-1E-R2 (order 486) is the bounded, materially corrected single-commit replacement. It restates SLICE-1E-R's spec by reference and packages the
  #264 head. The product bytes are proved identical by the `git patch-id --stable` value `fdb41c62c60b85a31f0008efe66bc9cc604bb17d` on both sides
  (commit message of `136e8bec`).
- That replacement is PR #268, reviewed head `3a1ac9c61a3fef9952b2e81c53be4ab3e11fbccb` (the a1-a7 attempts ran as `impl-SLICE-1E-R2-a*`), delivered as squash commit
  `136e8bec70db3ce77bdbc14c757c90d0d61cfd4b`.
- Queue state (`factory/queue-state.mjs:85-87`): a row with `supersededBy` is `SUPERSEDED_DELIVERED` once every named successor evaluates `DELIVERED`, which a merged
  PR whose body carries `row:SLICE-1E-R2` produces. The #268 body is not readable from this worktree, so that derivation rests on the squash message
  naming the row, not on a read of the body.

**K5 declaration.** The merged commit body of `136e8bec` carries: `KERNEL: fleet-factory-kernel r5 (CANDIDATE, DOGFOODING) · profile code@r10 · subject
SLICE-1E-R2 · base 1c0759feab27eb865fcafe46ea00394a1cce392b · owned paths ... · K1 separate implementer ... · K6 cross-family review (one Codex and one Claude leg,
same head) · K7 merge SHA recorded at acceptance`. The declaration followed the first implementation bytes. The facts:
- #268's PR body was created 2026-10-11T19:07:12Z (supplied to this leg by the controller packet; the body is not readable from this worktree).
- Package commit `3eb2640c` (`3eb2640c49634fcc7f43697cfc211461836ad927`) is dated 2026-10-11T18:55:55Z (13:55:55 -0500). It descends from the #264 `impl-SLICE-1E-R` a1-a5 lineage, whose product bytes are the ones #268 packages.
- `impl-SLICE-1E-R2-a1` started 2026-10-11T18:46:46Z (`impl-SLICE-1E-R2-a1-dispatch.json` startedUtc), before 19:07Z. `impl-SLICE-1E-R2-a1-authorship.json` is dated 2026-10-11 13:56 local (18:56Z).

This filing does not grade the timing. The second filing's K5 PROOF asks for the profile line "before its first implementation byte"; the steward decides whether a declaration made after the package commit, on a replacement row whose bytes came from #264, meets it.

**K1, separate implementer.**
- `merge-268-3a1ac9c6-authorship.json`: `ok: true`, `corroborated: true`, head `3a1ac9c61a3fef9952b2e81c53be4ab3e11fbccb`, author families `["claude"]`, receipts
  `impl-SLICE-1E-R2-a1`, `-a2`, `-a3`, `-a4`, `-a5`, `-a7`. The a7 receipt records `headBefore 64af68e19f97279aa735a9f085398302e1a2dd08`, `head 3a1ac9c6...`,
  model `sonnet`, observed `claude-sonnet-5-5`, effort high.
- `impl-SLICE-1E-R2-a6-authorship.json` also exists. The merge-time authorship receipt does not list it. It is not cited as a producer of the head.
- Merge authorship: `pr268-3a1ac9c6-merge-authorship.json` and `merge-268-3a1ac9c6-authorship.json`, both family claude.

**K6, key from another independence class.** The independent key is the Codex leg. The Claude leg shares the producer's family and is corroboration only; it is
not credited as the independent key.
- `review-268-3a1ac9c61a3f-codex-r2-a1/.factory-local/verdict.json`: family codex, requested `gpt-6-luna` at effort high, round 2, subject `3a1ac9c6...`, overall
  APPROVE, zero items.
- `review-268-3a1ac9c61a3f-claude-r2-a1/.factory-local/verdict.json`: family claude, round 2, subject `3a1ac9c6...`, overall APPROVE, one item **F-01 SHOULD
  AMEND**. A cold-started service worker has an empty in-memory queue, so the pre-clear snapshot used by the stale-lease reprojection (`background.ts`
  `queueBeforeStaleClear`) is empty and the dropped campaigns keep their stale banner. The leg read the code and did not run it, and says so in its
  `declared_self_failure`. **That finding is open on master.** No fix is claimed here and no follow-up row is filed by this file.
- The decision input `merge-268-3a1ac9c6-decision-input.json` binds both verdicts to head `3a1ac9c6...` and base
  `ac24ce1ee9243d8d9c9ab80505a3c773e76e48d6`, with `highRisk: false` (one leg per family is preferred, and both were present). `merge-268-3a1ac9c6-decision.json` is
  `{"mergeable": true, "reason": "D2_SATISFIED"}`.
- Local gate: `gate-3a1ac9c6-t1-exact-ci.json` is `LOAD_ADMISSION_TIMEOUT`, `infrastructure: true`, `consumesRound: false` (1800 s admission cap). `gate-3a1ac9c6-t2-exact-ci.json`
  is `GREEN` at head `3a1ac9c6...` (exit 0, 4763 s, admitted after waiting 947 s at threshold 70 percent). Three named checks (`docs drift (delta gate)`,
  `factory contracts`, `typecheck / lint / build / test`) are `success` at that head in the decision input.

**K7, delivery.**
- Squash commit `136e8bec70db3ce77bdbc14c757c90d0d61cfd4b`. Its parent is `ac24ce1ee9243d8d9c9ab80505a3c773e76e48d6`, equal to the reviewed base. Its tree
  `508360f7c0a25aa2d1508cd1963b06955b52fdf6` equals the tree of the reviewed head `3a1ac9c6...` (`git rev-parse <c>^{tree}` gives the same value for both).
- `merge-268-3a1ac9c6-host-output.json`: operation `merge`, pr 268, `exitCode 0`, `timedOut: false`. `merge-268-3a1ac9c6-reconcile.json`: `ok: true`,
  `status: DELIVERED`.
- Bus-side CoS record: bus `cos-feedback/adversarialllm/pr-268.md`, last changed by bus `f0e1e9f` ("PR #268 tip 3a1ac9c6 merge-when-ci-green").

**Honesty items against this filing's own interest.**
- The keyed commit `3a1ac9c6...` is not a master tip. Delivery is a squash merge whose tree equals the reviewed tree. See the W8 line below.
- The subject declared profile `code@r10`. The bus profile file `specs/fleet-factory-kernel/profiles/code.md` reads `Profile revision: r11` at bus 8e1321b. This filing
  does not re-grade the subject against r11.
- The K5 declaration (PR body 2026-10-11T19:07:12Z) followed the first implementation bytes (package commit `3eb2640c` 18:55:55Z; `impl-SLICE-1E-R2-a1` started 18:46:46Z). This filing claims no K5 credit for it and counts `subjects: 0`; the steward grades the timing. The F-01 SHOULD is open (above).
- This is one filed subject and it is not counted. It does not by itself change the instance grades the steward ruled on the earlier filings.

## (2) Dispositions for the newly binding bus cards

Format: `<card> | ADOPT, DISTINGUISH or N-A | reason`. Exactly one line per card. All eight bus object ids resolve at bus 8e1321b.

mlv-app 26f6a93 (an absolute CPU quiet gate starves on an owner-used host) | ADOPT | GATE-ADMIT-RECHECK and CTRL-TEST-HOST-LOAD VERIFY 3 in `factory/queue.jsonl` take its measure-and-attribute and loaded-comparable protocol instead of a second absolute CPU threshold, and #268's own gate shows the starvation shape (`gate-3a1ac9c6-t1` timed out at the 1800 s admission cap, `-t2` was admitted after 947 s of samples near 100 percent).
mlv-app 00bbc29 (a timeout reserved in a shared budget starves the child) | N-A | No controller or gate here starts a child only while a shared per-beat budget still holds the child's full timeout, and no per-beat scheduler is tracked outside `archive/factory-2026-09/`; `factory/controller/run-gate.ps1` keeps its admission cap and the suite as separate budgets.
mlv-app 2ca0fd2 (atomic replace denied while a reader holds the destination) | ADOPT | Row RESERVATION-ATOMIC in `factory/queue.jsonl` cites it and requires the publication reservation (`factory/publication-state.mjs` `reservePublication`) to use a temp file plus `fs.linkSync`, never `fs.renameSync`; this filing does not claim that row is delivered.
mlv-app 6020535 (Codex 0.161.0 elevated sandbox fails on an in-use node_repl) | DISTINGUISH | CODEX-PIN-R requirement (5) adopts the card's rule that a lane printing "setup refresh had errors" is NOT RUN, but not its `windows.sandbox="unelevated"` override: `factory/controller/dispatch-review.ps1:130` launches `exec --sandbox read-only` with no such setting, the global codex-cli is 0.160.1 (the CODEX-PIN-R hold text) and so predates the regression, and the card itself records weaker isolation and unmeasured egress under that override.
mlv-app e426a45 (Codex upgrade smoke passes a CLI whose shell calls all fail) | N-A | It is a proposal to the bus cli-currency owner about `tools/cli-currency.py`, and this repository has no CLI-upgrade smoke or cli-currency file (`git ls-files` finds none); the leg-output half, a result containing "setup refresh had errors" is NOT RUN, is covered by CODEX-PIN-R (f).
topbuilder b825b4f (5-hour limit read as rotation; Codex read-only sandbox review that never read the repo) | DISTINGUISH | The first trap lives in the user-level `usage-guard.py` hook and not in this repository, and for the second this repository keeps review legs at `--sandbox read-only` (`factory/controller/dispatch-review.ps1:130`; Codex seats are read-only when reviewing per root `CLAUDE.md`) instead of the card's `danger-full-access`, adopting only its rule that a review whose findings are about its own access is NOT RUN (CODEX-PIN-R (5) and (f)).
adobe-ingester 09b9cb5 (measure product against control; fix self-tripping gates at the source; pin the falsifier CLI privately) | ADOPT | GATE-TIMEOUT-CLASSIFY-R (merged as `1c0759fe`, PR #266) cites the card in `factory/queue.jsonl` ("fix self-tripping gates at the source") and grounds the ADOPT. PRODUCT-RATIO-DIAG (diagnostic only, modelled on the bus tool `product-control-ratio.mjs`) and CODEX-PIN-R (held, pins the Codex CLI) are related by subject only and do not cite the card.
adobe-ingester f4b8a49 (R12.3 review floor declared Opus) | DISTINGUISH | That line declares Adobe's own floor, and bus RULINGS R12.3 makes each board's own declared floor govern; this board declares the bounded tier for review legs (`factory/HUB.md` Roles: "Sonnet and gpt-6-luna do bounded packets and review legs", effort high, operative amendment point 8, ids only in `factory/models.json`), which is what #268's legs ran as (codex `gpt-6-luna`, claude `sonnet` observed `claude-sonnet-5-5`). Whether that declared floor satisfies R12.3 is the steward's to rule.
agent-bridge W5-W8 (bus TRAPS.md:27901-27908, 2026-10-07) | DISTINGUISH | The receipt-and-credit parts are present here (W5 and W6: the controller writes `merge-268-*` receipts that bind each verdict by `verdictSha256` and records post-key facts, the merge and `DELIVERED`, itself; W7: the minimal contract in section (1) lists only K1, K6 and K7 facts), but W8 is distinguished because `factory/RESET-PLAN.md` §1.3 forbids any push to master, so delivery is a GitHub squash merge (`136e8bec`, tree equal to the keyed tree, keyed commit `3a1ac9c6` never a master tip) and cloudvore's S22 test (d) as W7 states it would count 0 for this subject.

## (3) Standing fold input

Bus `cos-feedback/adversarialllm/` is a standing fold input for this project. At bus 8e1321b it holds one file per pull request (`pr-<n>.md`), including
`pr-264.md`, `pr-267.md`, `pr-268.md`, `pr-269.md`, `pr-270.md` and `pr-271.md`. Each fold or filing round reads that directory in full, and a CoS finding that
no earlier filing has answered is classified ADOPT, DISTINGUISH or N-A with a reason. The `pr-268.md` file is the CoS record for this filing's subject.
