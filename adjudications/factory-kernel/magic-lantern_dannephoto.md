project: magic-lantern_dannephoto
kernel: fleet-factory-kernel r1
profile: hardware-in-loop@r1
instance: NONE in repo yet (instance map below; the repo's sole integration writer is its recovery coordinator)
subjects: 0 (no owner-authorised subject was runnable: roadmap/recovery/execution-state.json status=waiting_external, 0 eligible, 5 blocked_external)
window: 2026-08-31T00:00Z .. 2026-09-14T21:30Z
health: assurance=UNEVALUABLE operability=PRESSURED
providers: claude, codex (sentinel-cleared lanes in the probe's self-review; none reviewed this filing)
posture: no model review

<!-- PROMPT-K §1, quoted lines as proof of reading:
     kernel:  "A single factory specification cannot be universal."
     profile: "emulator runs (for example QEMU) are necessary but never sufficient"
     PROMPT-K: "Never create work so you have something to measure."
     Filed by a magic-lantern_dannephoto session that had drafted a parallel kernel before finding r1 on master; the
     owner ruled r1 is the kernel. Machine-measured evidence: tools/factory-kernel-probe/evidence/ on this branch. -->

K1 | FRICTION | "A candidate is never accepted on evidence whose only author is its producer" | roadmap/recovery/execution-state.json: all 11 `done` tasks name a `verifier`, but only 1 of 11 (B01: worker "Luna b01_baseline", verifier "Claude Haiku diff review plus completed fresh-clone B01 verification") records its producer, so the observable "receipts name different actors" can be shown for 1 of 11 accepted subjects; cost: producer identity must be reconstructed from audit-packet prose for the other 10 | REPLACES: "*Observable:* for one completed subject, the receipts name different actors for production and acceptance." -> "*Observable:* for one completed subject, the receipts name different actors for production and acceptance, and the project's ledger records both for every accepted subject." | PROOF: a ledger where every accepted subject records producer and verifier and one pair is equal would falsify the need; so would the steward showing the observable is meant for one subject only.
K2 | FIT | "Each project keeps one register of what needs the owner and what does not." | audit-packet/60-owner-autonomous-recovery-20260907.md ("Owner decision 60 — autonomous bounded recovery"), named as `authority` in the ledger; the coordinator completed 11 desk/factory cards under it without asking; owner-only items wait in roadmap/OWNER-ASKS-2026-07-20.md | PROOF: a card in the window that waited on the owner for something decision 60 authorises.
K3 | UNEXERCISED | "the identity string of one subject, and the command that recomputes it from the artifacts" | subjects: 0. Observation only: the native identity is `accepted_commit` per task; no task records a built-image digest (0 of 16 tasks carry any digest field), which hardware-in-loop requires once an image is flashed | PROOF: n/a
K4 | UNEXERCISED | "the negative case the project checked" | subjects: 0. Observation only: the existing evidence trees of accepted task B03 contain `b03/pytest.status` = `1` and `b03/probe.status` = `1` (and their `verify/` copies) beside the corrected `b03-final/` trees, with nothing machine-readable naming which run acceptance rested on (probe K5 WARN; TRAPS 2026-09-14) | PROOF: n/a
K5 | UNEXERCISED | "the profile line recorded before work, and the acceptance receipt bound to the same identity" | subjects: 0; no subject declared a profile before work (the kernel did not exist when the 11 cards ran) | PROOF: n/a
K6 | UNEXERCISED | "the independence class of each key on one accepted subject" | subjects: 0. Observation only: B01's verifier (Claude Haiku) and producer (Luna) are different provider families; hardware keys (H01, H02) have never been supplied | PROOF: n/a
K7 | UNEXERCISED | "the delivery target, and how the project detects an accepted subject that never delivered" | subjects: 0. Observation only: 11 accepted, 0 delivered; delivery-class tasks R01, H01, H02, R02, K01 are `blocked_external` with reasons, which is how the ledger detects non-delivery today | PROOF: n/a
K8 | UNEXERCISED | "what happened to in-flight work at the last quota event" | execution-state.json `cost_policy.codex_weekly_remaining_percent_observed: 10`, but 0 work was in flight, so no quota event met work | PROOF: n/a
K9 | FIT | "A fresh session on a new account, with empty memory, resumes from the project's tree and the bus alone." | this session resumed from roadmap/HANDOFF.md and roadmap/recovery/CONTINUE.md; gate `python tools/roadmap/validate-current-state.py` exited 0 on 2026-09-14 with "CURRENT STATE VALID", static_gates=289/0 | PROOF: the validator failing on the current tree, or a resume that needed a memory note.
K10 | FRICTION | "Provider and model inventory is machine-scoped and probe-derived, and it records the account it was derived under." | ~/.claude/machine-inventory.yaml line 5: `probed_under: unknown` (generated 2026-09-13T22:41-05:00) while this session's parity check reported MATCHED fp=b4d2646b85c1; `tools/probe-machine-inventory.sh` writes `unknown` unless PROBE_IDENTITY is passed by hand; cost: a rotation cannot be detected as inventory staleness | REPLACES: "*Observable:* inventory path, `probed_under` value, parity command output." -> "*Observable:* inventory path, a `probed_under` value that is not `unknown` and matches the current parity fingerprint, parity command output." | PROOF: re-run the probe with PROBE_IDENTITY set to the parity fingerprint; if the file then carries it and the observable is checkable without extra steps, withdraw this line.
K11 | FIT | "R1–R5, R7, R8 and R9 apply to every report a factory makes about itself" | this project's review filing adjudications/approach-a-design/magic-lantern_dannephoto.md (branch review/magic-lantern_dannephoto-2026-09-14 @ ea39041) copies its `posture:` line from tools/review-posture (R9) and was pushed and ls-remote verified (R7) | PROOF: a posture line in either filing that the R9 tool does not reproduce.
K12 | UNEXERCISED | "the project's filing on `origin`, and `harvest-status.py factory-kernel` showing it `HARVESTED` after the next harvest" | first filing; UNHARVESTED until the steward answers | PROOF: n/a

P:hardware-in-loop human-gates | FIT | "every hardware session (the operator is the owner or someone the register names)" | H01 and H02 are `blocked_external`: "need owner camera operation and applicable approved protocol"; no hardware session was attempted without the owner | PROOF: a hardware card marked done without an owner session record.
P:hardware-in-loop resource-terminals | FIT | "device unavailable, battery or thermal limits, operator absent: typed terminals; the subject waits and nothing is inferred" | all 5 delivery-class tasks wait as `blocked_external` with a reason in `next_action`; none was credited from emulator or desk evidence | PROOF: a delivery-class task credited without its terminal clearing.
P:hardware-in-loop acceptance-evidence | BREAK | "emulator runs (for example QEMU) are necessary but never sufficient" | audit-packet/06-qemu/BLOCKED.txt: "QEMU SMOKE TEST: BLOCKED (no legal inputs present)" — the emulator needs camera ROM inputs this project cannot lawfully obtain, so an honest camera acceptance could never satisfy "necessary" | REPLACES: "emulator runs (for example QEMU) are necessary but never sufficient" -> "emulator runs (for example QEMU) are required where lawful inputs exist and are never sufficient; where they cannot lawfully run, the hardware receipt stands alone and the filing records why" | PROOF: a lawful source of 5D3 ROM inputs for QEMU existing for this project would falsify the BREAK.
P:hardware-in-loop stress-on-the-kernel | FIT | "the independent key is a scarce human sitting, so K6 and K7 throughput is bounded by attendance, not compute" | 11 adopted desk cards, 0 delivered; every remaining card waits on the owner's camera, an independent machine or a named steward; the integration branch had 31 governance commits and 0 product commits in 14 days (probe K7) | PROOF: a delivery that closed within the window without an owner sitting.

## Instance map (K1–K12 → mechanism in this repo)

| clause | mechanism | path / command |
|---|---|---|
| K1 roles | ledger `worker` / `verifier` fields (producer recorded 1 of 11) | roadmap/recovery/execution-state.json |
| K2 register | owner decision 60; owner asks | audit-packet/60-owner-autonomous-recovery-20260907.md; roadmap/OWNER-ASKS-2026-07-20.md |
| K3 identity + claimant | `accepted_commit` per task; single integration writer ("workers do not stage or commit") | execution-state.json; **NONE** for built-image digest and for claim leases |
| K4 positive evidence | raw check receipts and cold-clone proofs under audit-packet/recovery-20260907/ | tools/roadmap/recovery-transaction.py; **NONE** machine-readable receipt binding exit status to identity |
| K5 declared profile | **NONE** (no subject declares a profile before work) | — |
| K6 independent key | cross-family reviewer lanes; hardware key = owner's camera | CLAUDE.md "Hardware evidence comes only from the owner's camera" |
| K7 delivery | `blocked_external` delivery-class tasks R01, H01, H02, R02, K01 | execution-state.json; **NONE** for a closure transaction |
| K8 capacity | `cost_policy` routing note | execution-state.json |
| K9 resume | HANDOFF → CONTINUE → validator | roadmap/HANDOFF.md; roadmap/recovery/CONTINUE.md; tools/roadmap/validate-current-state.py |
| K10 inventory + parity | machine inventory; SessionStart parity hook | ~/.claude/machine-inventory.yaml (`probed_under: unknown`) |
| K11 honest reports | R9 review tool; sentinel-judged lanes | softwarefactory-fleet-doctrine tools/review-posture/ |
| K12 feedback | this filing | adjudications/factory-kernel/magic-lantern_dannephoto.md |

Not written into the repo in this window: `roadmap/recovery/execution-state.json` names `integration_writer: current
recovery coordinator; workers do not stage or commit`, and this session is not that coordinator. The map lives here
until the coordinator lands it.

## Steward proposals (not verdicts; each rests on evidence from this repo, most from existing records rather than a subject run in this window)

- **P1 — measure governance motion (candidate clause, or a K12 observable).** The probe counted 31 governance commits,
  0 product commits and 3 other commits on `codex/audit-remediation-2026-07` over 14 days, with 0 eligible subjects
  (`tools/factory-kernel-probe/evidence/magic-lantern_dannephoto-2026-09-14.json`). The fleet has measured the same
  failure at 99.5% (Conjugal's own spec) and 99.7% (adversarialllm). r1 has no clause that sees it. Suggested text:
  "A factory measures the ratio of governance-only to product commits over a window; zero product motion, or a ratio at
  or above the profile's alarm ratio, raises the conformance-fixpoint alarm in the filing."
- **P2 — admission is bounded by eligible work (candidate clause beside K8).** K8 says capacity never stalls the
  factory, but nothing says capacity must not *exceed* eligible work. Conjugal measured open wire lines going 0→181 and
  never draining, with four of seven weeks closing zero subjects, and names the cause: "An always-on admitter in front
  of a blocked pipeline converts uptime into WIP, not throughput" (specs/conjugal.md). Approach A v7.4 admits `executors=5` from the first minute. Suggested text:
  "Executors are admitted only against eligible subjects; zero eligible subjects admits zero executors, and the filing
  shows the eligible count beside the executor count."
- **P3 — liveness is measured, not declared (a K4 observable).** "Magic Lantern Lane Supervisor" has been `Disabled`
  since 2026-08-18, while the continuation runs as an app automation no OS probe can see. K4 already says enabled state
  and actual execution are different facts. Suggested observable: "every declared scheduler's live state, or
  owner-interaction evidence committed within 14 days."
- **P4 — K5 "acceptance evidence exists" is satisfiable by failed evidence.** B03's cited trees contain status files
  reading `1` (K4 observation above). Suggested REPLACES in K5: "Accepted means that profile's acceptance evidence
  exists" → "Accepted means that profile's acceptance evidence exists, records a passing result, and names a verifier
  other than the producer".
- **P5 — machine-measured observables.** `tools/factory-kernel-probe/` on this branch measures r1 observables from a
  project's ledger and git (mapping table in its README; 19 tests). It ran on this repo and on the bus itself. It is
  offered for the steward to adopt, adapt or decline; the proposer will not land it on master.
- **P6 — PROMPT-K §2 "create the file if the project has no spec yet" collides with the adoption ledger's closed project
  set.** This project had no bus spec, so this branch adds `specs/magic-lantern_dannephoto.md`.
  `tests/test_current_adoption_ledger.py::test_unregistered_project_is_not_silently_omitted` shows that any tracked
  spec missing from the current adoption census raises `PROJECT_CLOSED_SET_MISMATCH`, so merging a first-time
  dogfooder's spec block needs a census update in the same landing. Untested end-to-end here: in this session's
  detached worktree, both ledger suites fail on `GIT_BLOB_UNAVAILABLE` before reaching that check, the same worktree
  environment failure recorded for other bus tests. Suggested: PROMPT-K §2 names the census step, or the steward's
  harvest runner performs it when merging a new project's spec block.
