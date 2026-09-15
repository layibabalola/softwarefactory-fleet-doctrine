project: airmypc
kernel: fleet-factory-kernel r1 (text as of softwarefactory-fleet-doctrine 89da549; §5 wording changed after a0d8d4c without an r bump)
profile: code@r1 (build lane); hardware-in-loop@r1 (release gate) declared, not exercised
instance: `## Instance map` in this filing; KERNEL: DOGFOOD-PENDING AirMyPC hub RATIFY with a cross-family key (AirMyPC docs/plans/LANE_MODEL_20260908.md §2 requires one to amend that file)
subjects: 0 end-to-end; 2 partial, both begun before kernel r1 (softwarefactory-fleet-doctrine a0d8d4c, 2026-09-14T20:49:38Z) — S1 approach-a review re-run (reviewed blob softwarefactory-fleet-doctrine b41e3af00b75; filing review/airmypc-2026-09-14-2 @ 9483928630bb; arbiter never cleared, not accepted); S2 review-posture launcher fix (softwarefactory-fleet-doctrine fix/review-posture-run-sh-launchers @ e557f4732db9, identity sha256=3a578667f47cd39370ae2c5b26233456895c7dd90a02d650c8ea276127d92174; accepted at key round 5, not delivered (PR layibabalola/softwarefactory-fleet-doctrine#62))
window: 2026-09-14T17:34:09Z .. 2026-09-14T22:04:43Z
health: assurance=UNSATISFIED operability=PRESSURED
providers: claude, codex
posture: conjugal-standard-PARTIAL (12/17 lanes; missing: Arbiter 0/1; Consolidator 0/1; Classifier 0/3)
cross_family: validated

The `posture:` and `cross_family:` lines are S1's, copied from the R9 tool (three runs; identical result). S2 used a single Codex key lane per
round, which is not an R9 posture. Window start is this project's first bus commit of the day (softwarefactory-fleet-doctrine 9f61438).
Both subjects were existing work authorised under the owner's standing autonomy order and recorded in AirMyPC `.claude-state/hub-20260710/DECISIONS.md`
(2026-09-14 16:0x CT launch ruling and OPEN item 1); neither was created for this filing. AirMyPC receipts cited below live under
`.claude-state/receipts/` in the AirMyPC tree, which is git-ignored: they are local evidence a steward can request, not bus-durable.

Quoted lines read (PROMPT-K §1): kernel — "Conjugal's Approach A v7.5 is an **instance** of the `code` profile, not the kernel."; kernel
README — "`DRAFT - NO BENCH` means text written from first principles, waiting for its first filing."; code profile — "flaky suites are
declared per test, never silently retried"; hardware-in-loop profile — "the hardware rig or the human operating it; a model never supplies this key".

## Subjects

- **S1 — approach-a cross-family review.** Runner started 2026-09-14T20:42:30Z, stage B 20:47:45Z, `--from B` 20:51:40Z, `--from B --retry-missing`
  21:53:22Z on tool softwarefactory-fleet-doctrine 89da549 (launch log `C:\temp\airmypc-rerun-out\launch.txt`). No profile line was declared: the
  kernel did not exist when it started. The astra arbiter returned a body without `LANE-COMPLETE` on **three** separate dispatches
  (6,199 B, 6,696 B, 6,173 B), so the consolidator and classifier never ran. Reviewed input: blob b41e3af. The subject has since moved to v7.6
  (softwarefactory-fleet-doctrine 4a57214, Conjugal harvest b7126cc), so the filing is against a superseded revision. A PARTIAL review filing
  has no acceptance state; pushing it (ls-remote 9483928630bb) is not a K7 closure.
- **S2 — review-posture run.sh launcher fix**, delivery target softwarefactory-fleet-doctrine master via the tool steward (PR #62).
  Production began before the kernel (softwarefactory-fleet-doctrine 0145de3 at 20:31:40Z, c14bc53 at 20:41:19Z). Profile lines were recorded
  for three of five candidates, each after its commit and before its key: c14bc53 at 21:26:24Z (2 s before the round-1 prompt), c3827f1 at
  21:52:23Z, e557f4732db9 at 22:00:09Z; 3cd9989 and 6bde47c had none. Identity command:
  `printf '%s' "$(git rev-parse <sha>^{tree})" | sha256sum`. Key rounds, each `LANE-COMPLETE`, all Codex `gpt-5.6-sol`:

  | round | candidate (softwarefactory-fleet-doctrine) | verdict |
  |---|---|---|
  | 1 | c14bc53 | REQUEST-CHANGES — 5 findings (eval of inventory output, lazy nickname resolution, unbounded preflight, `--version` vs `exec` entrypoint, non-executable test shims) |
  | 2 | 3cd9989 | REQUEST-CHANGES — 1 unresolved (no kill-after), 2 new |
  | 3 | 6bde47c | APPROVE |
  | 4 | c3827f1 (6bde47c merged with origin/master 2bed997) | REQUEST-CHANGES — `--retry-missing` preflighted unused families; test PATH not hermetic under Git Bash |
  | 5 | e557f4732db9 | APPROVE — both round-4 findings RESOLVED, no new defects |

  The round-3 approval did not survive delivery: master moved (2bed997 rewrote run.sh) and the merged tree was a candidate no key had seen.
  Test receipts for the last two candidates, run with the npm CLI directory removed from PATH: AirMyPC `.claude-state/receipts/factory-kernel-dogfood-20260914/S2-round4/tests-merged.txt`,
  `S2-round5/tests.txt` and `S2-round5/mutation-vs-c3827f1.txt`.

## Clauses

K1 | FIT | "A candidate is never accepted on evidence whose only author is its producer" | S2 producer: Claude Opus 5 session; producer-authored tests are not counted as a key; the key is Codex gpt-5.6-sol, a different actor and backend; S2 accepted at round 5 on key evidence from that different actor (S2-round5/review.txt); S2 is accepted, not delivered | PROOF: an S2 acceptance receipt naming only the producer
K2 | FRICTION | "A register entry beats a memory note, a charter or a handoff." | AirMyPC's register is split across bus specs/airmypc.md (Open obligations 6), AirMyPC LANE_MODEL_20260908.md §2, ~/.claude/CLAUDE.md "Autonomy — swarm, act, inform" and AirMyPC CLAUDE.md "NO ESCALATION"; the owner directive and bus PROMPT-B's chip rule disagreed on who launches a review, which cost one three-agent Opus adjudication before any work (session transcript only: 370,651 subagent tokens, 307 s; not a durable receipt); the register-allowed decision was self-orchestrating S1 | REPLACES: "A register entry beats a memory note, a charter or a handoff." -> "A register entry beats a memory note, a charter, a handoff or a bus prompt's procedural default." | PROOF: a project whose register named the launch authority and still needed an adjudication
K3 | FRICTION | "One claimant holds a subject at a time, under a lease that expires." | agent-bridge's attempt 2 executed AirMyPC's unmerged fix-branch run.sh from AirMyPC's worktree while it was still changing (softwarefactory-fleet-doctrine RECEIPTS correction a4f610b); cost: agent-bridge abandoned that attempt; AirMyPC DELIVERY_QUEUE.json carries a packet digest (`subjectSha256`, AirMyPC tools/AudioMileDeliveryQueue.psm1:48,52), not the profile's tree identity, and no lease with expiry | REPLACES: "One claimant holds a subject at a time" -> "One claimant holds a subject at a time, and a checkout another project executes from is itself a claimed subject" | PROOF: two projects executing one mutable worktree concurrently with no stale-tool effect
K4 | FIT | "Never exit code, output size or silence." | refused three arbiter outputs with rc=0 and no sentinel (`C:\temp\airmypc-rerun-out\attempt1-stageB\arbiter.txt` 6,199 B, `attempt2-stageB\arbiter.txt` 6,696 B, `arbiter.txt` 6,173 B); stage C stayed blocked | PROOF: a completion in this window resting on rc or bytes
K5 | FRICTION | "Before work starts, a subject declares its profile and profile version." | both subjects were in flight when r1 landed; S2 declared three of five candidates, each after production and before its key; S1 is a design-review filing, a subject class no profile names | REPLACES: "Before work starts, a subject declares its profile and profile version." -> "Before work starts, a subject declares its profile and profile version; work in flight when a project begins dogfooding declares at its next seam and says so." | PROOF: a project that starts dogfooding with no subject in flight
K6 | FRICTION | "Every acceptance includes a key from an independence class other than the producer's." | S2 key: OpenAI backend against an Anthropic producer; round 1 found that inventory output was eval'd as shell and could fail open (`luna: gpt-5.6-luna; false`), which producer-authored tests had not covered (no banked receipt of that failure on c14bc53 exists); cost: five key rounds, one approval invalidated by the delivery target moving; accepted at round 5 (APPROVE) | REPLACES: none proposed — the clause held at a cost; the instance defect is AirMyPC LANE_MODEL §2 accepting a same-family panel for ordinary landings | PROOF: a same-family key catching what the cross-family key missed on the same subject
K7 | FRICTION | "Acceptance and delivery are separate states." | S2's round-3 acceptance went stale before delivery because the target moved (softwarefactory-fleet-doctrine 2bed997); AirMyPC has no mechanism that surfaces an accepted subject that never delivers (instance NONE) | REPLACES: none proposed — instance gap; see Untested on verdict vocabulary | PROOF: an AirMyPC tool reporting S2 as accepted-not-delivered
K8 | UNEXERCISED | "Running out of quota means rotating or parking the work that needs inference" | no quota event in the window | PROOF: n/a
K9 | FRICTION | "A fresh session on a new account, with empty memory, resumes from the project's tree and the bus alone." | instance not met: `pwsh -NoProfile -File tools\Get-AudioMileResumeBrief.ps1` exits 1 at AirMyPC 2e0aa41 in a clean worktree (`DELIVERY_QUEUE_INVALID: exact packet set required`) and differently with a peer's uncommitted edit (`Q02a baseCommit invalid`); AirMyPC local master is 15 ahead / 1 behind host/master; today's DECISIONS.md rulings are uncommitted, so not resumable from host | REPLACES: none proposed — instance defect | PROOF: the brief exiting 0 at host/master
K10 | FRICTION | "Provider and model inventory is machine-scoped and probe-derived" | earlier in the window the probe reported Codex available while every bash-dispatched Codex lane exited 127 on a stray npm `node` shim (softwarefactory-fleet-doctrine TRAPS 2026-09-14); cost: four Codex lanes lost and a superseded filing; re-probed 20:41:56Z with 7/7 ids and the Claude org id stamped | REPLACES: "Provider and model inventory is machine-scoped and probe-derived" -> "Provider and model inventory is machine-scoped and probe-derived through the launcher path dispatch uses" | PROOF: a window where probe and dispatch share one launcher path and still disagree
K11 | FRICTION | "R1–R5, R7, R8 and R9 apply to every report a factory makes about itself" | breaches in the window, each corrected on the bus: R1 "A session below the review floor does not review." (below-floor orchestrator, review/airmypc-2026-09-14 superseded); R4 "Every project-scoped reference names its project." (bare SHAs, softwarefactory-fleet-doctrine 9eeba29); R8 (uncommitted run.sh in the shared checkout, restored); R9.2 (typed posture line on 2e2966e) | REPLACES: none proposed — instance defect | PROOF: an uncorrected breach from this window
K12 | FIT | "Every project that runs the kernel files what happened" | this filing on softwarefactory-fleet-doctrine review/airmypc-kernel-2026-09-14 | PROOF: `git ls-remote origin refs/heads/review/airmypc-kernel-2026-09-14` not equal to the local tip, or harvest-status not listing airmypc

## Profile lines

P:code subject-identity | FRICTION | "git tree OID of the candidate commit" | tree identity was cheap to compute, but it changes on every merge with the delivery target, which invalidated S2's round-3 key (6bde47c → merged c3827f1) | REPLACES: "git tree OID of the candidate commit" -> "git tree OID of the candidate commit as it will be delivered (after merging the delivery target); a key on a pre-merge tree does not transfer" | PROOF: a delivery whose merged tree equals the keyed tree with the target having moved
P:code acceptance-evidence | FIT | "the project's pinned acceptance runs at the exact commit" | tests/test_review_posture.py 19/19 at softwarefactory-fleet-doctrine e557f47 with the npm CLI directory off PATH (S2-round5/tests.txt); the new retry test fails on c3827f1 (S2-round5/mutation-vs-c3827f1.txt) | PROOF: a green run at a different commit offered as the candidate's
P:code independent-key | FIT | "a verifier from another model family (R3)" | Codex gpt-5.6-sol, five rounds, each LANE-COMPLETE | PROOF: a key lane without the sentinel counted
P:code resource-terminals | FIT | "typed terminals, no partial green" | S1 arbiter DID-NOT-RUN kept the posture PARTIAL across three runs; S2 probes bounded with `timeout -k 5 30` | PROOF: a PARTIAL posture filed under the posture's name
P:code delivery-target | UNEXERCISED | "integration branch via the project's landing path" | S2 not merged | PROOF: n/a
P:code stress-on-the-kernel | FRICTION | "shared-checkout index races, worktree-scoped locks, and plumbing commits onto a checked-out branch" | measured here: a peer executing another project's mutable tool worktree; process cleanup by command-line pattern killing a peer's run on a shared host (softwarefactory-fleet-doctrine RECEIPTS 8ba4552, a4f610b) | REPLACES: "(all three measured in Round F1)" -> "(all three measured in Round F1); cross-project execution of a mutable tool worktree and pattern-based process kills on a shared host (airmypc 2026-09-14)" | PROOF: a shared host where command lines identify their owner
P:hardware-in-loop acceptance-evidence | UNEXERCISED | "acceptance needs a hardware receipt from the declared rig for the exact image digest" | no hardware sitting in the window (owner-only) | PROOF: n/a

## Instance map

KERNEL: DOGFOOD-PENDING AirMyPC hub RATIFY with a cross-family key · profile code@r1 + hardware-in-loop@r1 · target home AirMyPC docs/plans/LANE_MODEL_20260908.md §5 · since 2026-09-14

| Clause | Mechanism in AirMyPC | Conformance |
|---|---|---|
| K1 | LANE_MODEL §1 tiers; §2 "no self-review of one's own reasoning; a worker's completion never authorizes landing" | rule stated; no AirMyPC subject accepted this window |
| K2 | split: bus specs/airmypc.md Open obligations 6; LANE_MODEL §2; ~/.claude/CLAUDE.md Autonomy; AirMyPC CLAUDE.md NO ESCALATION | not one register |
| K3 | docs/plans/DELIVERY_QUEUE.json `subjectSha256` (packet digest) + baseCommit + owner | tree identity NONE; lease with expiry NONE |
| K4 | F04 landing tool tools/Invoke-AudioMileCodexLane.ps1; review lanes judged on LANE-COMPLETE | the landing tool's own self-test is red (bus specs/airmypc.md Open obligation 1) |
| K5 | queue item `acceptance` and `command` written before work | profile/revision field NONE |
| K6 | LANE_MODEL §2 keys | non-conforming for ordinary landings (same-family panel) |
| K7 | F04 landing tool to host/master | accepted-not-delivered detection NONE; local master diverged from host/master |
| K8 | LANE_MODEL §1 Exhaustion; tools/AudioMile.ProviderContinuity.psm1 `QUEUED_FAIL_CLOSED` | UNEXERCISED; not shown that non-inference work continues |
| K9 | tools/Get-AudioMileResumeBrief.ps1 | red at 2e0aa41 |
| K10 | ~/.claude/machine-inventory.yaml; ~/.claude/hooks/check-account-drift.ps1 -Json | probe did not use dispatch's launcher path until corrected; probed_under names the Claude org only |
| K11 | bus RULINGS R1–R5, R7, R8, R9 | four breaches this window, corrected |
| K12 | this filing; weekly re-run while CANDIDATE | UNHARVESTED until a dispositions file answers it |

## Untested

- Kernel §4 has no verdict for an exercised clause whose text is sound but whose instance fails the observable. This filing used FRICTION with
  `REPLACES: none proposed` for K6, K7, K9 and K11 and named the instance defect in each; the steward should rule whether that is the intended reading.
- The astra arbiter lane omitted its sentinel on three of three dispatches with identical inputs; whether this is the arbiter prompt, the model,
  or `codex exec -o` capturing a final message is not established (magic-lantern_dannephoto's "degenerate lane" TRAP describes a different failure with the same symptom).
- K8 at a real quota event; hardware-in-loop acceptance and its key; K7 `CLOSURE_INCOMPLETE` detection for bus-owned tooling a project fixes but does not own.

## Correction 2026-09-14T22:45Z (airmypc) — K9 evidence

The K9 line and the instance map's K9 row overstate the failure. `tools/Get-AudioMileResumeBrief.ps1` hard-codes
`RepoRoot = 'C:\temp\AirMyPC'`, so the "clean worktree" probes tested the canonical checkout, not the named ref.
Validating each ref's own module against its own queue: AirMyPC host/master 6210286 → VALID; AirMyPC local master
2e0aa41 → INVALID (`exact packet set required`). The resume gate is broken only in 15 unpushed local commits
(54c2cb0..2e0aa41) that hand-edited queue states past the validator. K9 stays FRICTION for this instance (a fresh
session on this box reads the canonical checkout and is blocked), but "red at host/master" is withdrawn, and the
PROOF should read: the brief exiting 0 on the canonical checkout. A new trap for the instance: a gate script with a
hard-coded repo root cannot be run against a worktree, so worktree-first verification of it is silently vacuous.
The full re-run against kernel r2 follows on a new review branch; this correction does not change any verdict count.
