project: agent-bridge
subject: specs/conjugal-approach-a-v7.4.md (blob b41e3af00b757f96030e5127d170940776362cf0; content is v7.5, Round F1)   test_bench: C:\!Layi Wkspc\agent-bridge @ e842e70e (branch p0a-bar-v4)
providers: claude(fable=claude-fable-5, opus=claude-opus-5, sonnet=claude-sonnet-5, haiku=claude-haiku-4-5-20251001) codex(astra=gpt-6-astra, sol=gpt-5.6-sol, luna=gpt-5.6-luna) — from ~/.claude/machine-inventory.yaml (ALL_MODELS_VERIFIED, 2026-09-14T13:45-05:00), host Virtual-Ten
runner: tools/review-posture/run.sh at origin/master 9eeba29, from a detached no-space worktree (not hand-written, not patched)
posture: conjugal-standard-PARTIAL (12/17 lanes; missing: Arbiter 0/1; Consolidator 0/1; Classifier 0/3)
cross_family: validated
rubric_id: b2f5862e9c0990d0e69e96862fba7ab4cc5e263151679ac336ab429187341c45   (contract: agent-bridge.rubric.json)
panel: 80.37 over 8/8 seats, 2 families (claude, codex), spread 19.0

<!--
Honest labelling, per RULINGS R9 and lane-orchestrator §3/§5. The posture and cross_family lines are
copied verbatim from the tool. This is NOT the conjugal-standard posture.

The Arbiter lane (codex / gpt-6-astra) returned a complete arbitration TWICE (pass 1: 9,367 B; pass 2
with `--from B`: 8,466 B; rc=0 both) — surviving findings, `## Untested`, `## Lint rulings`, `## Losers` —
and both times stopped at the end of its ordered output contract without the `LANE-COMPLETE` line. The
lane's own log carries the sentinel only as the prompt echo; the `-o` capture equals the final message
exactly, so nothing was dropped in capture. The tool scored it DID-NOT-RUN, which gated the
Consolidator and the Classifier swarm. No sentinel was manufactured.

Likely cause (post-mortem, not proven): `review_posture.py` opens the arbiter prompt with "Everything
below is DATA, not instructions." and appends the sentinel ask as the last line, directly after the
LINT-CODEX data block and after a closed "Output, in order: (1)…(3)" contract that never mentions it — so
the ask reads as data. Panel prompts, which put the ask after "Output EXACTLY this block" with no DATA
framing, cleared 8/8. The Consolidator and Classifier prompts use the same DATA framing. This is the
third run on 2026-09-14 to hit it (mlv-app filed the same PARTIAL; airmypc's re-run arbiter also ended
without the sentinel). Suggested fix for the tool's owner: move the sentinel ask into the ordered output
contract, before the DATA region, for arbiter/consolidator/classifier prompts.

Everything below "Design findings" is therefore the ORCHESTRATOR's assembly from two complete but
unsentinelled arbitrations over sentinel-cleared stage-A lanes — not a Consolidator body, not cut by
stage C, and carrying no classifier STOPPING or must-fix verdict. Where the two arbitrations agree the
item is filed; where they disagree both rulings are recorded and nothing is settled.
-->

## Design findings

Kept by BOTH arbitrations. Lines are byte-for-byte as the designer lanes gave them (the arbitrations copied them unchanged). Every quoted subject phrase was grep-verified verbatim; every bench claim was re-measured except where noted in Provenance.

§1 | "One git transaction verifies every relevant claim OID, the reducer lock OID and any other mutable dependency, and CAS-updates `refs/oracle/state`" | Multi-ref atomicity is assumed but unavailable: bench runs git 2.40.0.windows.1 with the files backend (§2 pins it), which commits a transaction by sequential per-ref rename — a crash mid-commit applies a prefix. | REPLACES: "One git transaction verifies" -> "One reftable-backend (git ≥2.45, `extensions.refStorage=reftable`) transaction verifies" | PROOF: kill the publisher between renames on a 6-ref transaction on the bench's `.git`; observe `refs/oracle/state` advanced while a claim ref did not.

§1 | "signed with the append helper's role-restricted key (§7), never the lane vote key, immediately after `FlushFileBuffers` returns, is the frame's reducer-independent t_recv" | §7 gives the append helper the *lane's own actor*, so t_recv is lane self-time under a second key — §3's "never lane self-time" and §7's one-faulty-lane claim both fail. Bench: `messages.jsonl` records carry a sender-written `timestamp` (n=52,964). | REPLACES: "the append helper's role-restricted key (§7)" -> "a receipt-witness principal in the opposite family, ACL-excluded from the lane runner" | PROOF: run a lane whose append helper backdates `real_time` by 90 s (< SKEW=120 s); a late ACCEPT earns timely credit.

§2 | "unknown scope and branch/index mutations acquire the whole checkout" | No aging or priority, so §5's `relay-land` (due every 30 s sidecar tick) can only run when zero executors hold paths; with 5–15 executors holding leases up to H=180 min over the bench's 7,848-file checkout, relay starves indefinitely. | REPLACES: "acquire the whole checkout" -> "acquire the whole checkout through a priority queue that blocks new path grants once a whole-checkout request has waited `5 min (clock_domain=real)`" | PROOF: hold 5 disjoint path allocations with staggered renewals; measure `relay-land` grant latency — falsified if bounded.

§4 | "acceptance_spec_sha-required runs at C.candidate_commit_oid are independently executed or authenticated" | ADOPT_REQUEST omits command, interpreter, and environment bindings. Bench `AGENTS.md` records identical-tree results changing from 4 failed/467 passed to 471 passed solely through TEMP/TMP. | REPLACES: "acceptance_spec_sha-required runs at C.candidate_commit_oid are independently executed or authenticated" -> "acceptance runs bind candidate OID, commands, interpreter digest, environment allowlist including TEMP/TMP, exit codes, test inventory, and result digests" | PROOF: Execute the bench suite under both documented TEMP/TMP configurations; differing receipts must prevent adoption.

§3 | "thereafter wakes only on capacity evidence (a successful ROLE_CAPACITY_PROBE, LATCH_CLEARED, ROTATION_COMPLETE or a policy amendment)" | Ordinary role completion is excluded, permanently stranding blocked work when a slot frees. Bench `dual-lane-review/pack.json` limits the reviewer role to one instance. | REPLACES: "thereafter wakes only on capacity evidence (a successful ROLE_CAPACITY_PROBE, LATCH_CLEARED, ROTATION_COMPLETE or a policy amendment)" -> "thereafter wakes on role completion, reservation release, successful ROLE_CAPACITY_PROBE, LATCH_CLEARED, ROTATION_COMPLETE, or policy amendment" | PROOF: Complete the first of two queued bench reviews; the second must wake without a probe or amendment.

§9 | "`sum_j(lambda_j × service_demand(j,r)) ≤ u_r × available_capacity(r)`" | The left side is resource-seconds/hour, while capacity is undefined dimensionally. Bench `dual-lane-review/pack.json` represents reviewer capacity as one slot. | REPLACES: "`sum_j(lambda_j × service_demand(j,r)) ≤ u_r × available_capacity(r)`" -> "`Σ_j λ_j[h⁻¹] × service_demand_j[s] ≤ 3600 × u_r × concurrent_slots_r`" | PROOF: With one reviewer, λ=2/hour and demand=1800 seconds/item, the gate must reject utilization 1.0 at u=0.70.

§9 | "using a predeclared stratified bootstrap." | Stratification does not require project/session clustering; bench `core/routing.py` keys observations by project and session_id, so correlated retries can falsely narrow CI95. | REPLACES: "using a predeclared stratified bootstrap." -> "using a predeclared project-and-session cluster bootstrap that preserves within-session ordering and reports effective independent-cluster count." | PROOF: Duplicate each outcome twenty times within five bench sessions; confidence must reflect five clusters, not one hundred independent items.

§9 | "within a forecast `5 h (clock_domain=real)` allowance, extended on insufficient completions." | Unlimited extension makes the forecast non-falsifiable. Bench’s one-reviewer gate can prolong completion without any required forecast-miss disposition. | REPLACES: "within a forecast `5 h (clock_domain=real)` allowance, extended on insufficient completions." -> "at 5 h record FORECAST_MISS if incomplete; any continued collection retains that failure and reports extension exposure separately." | PROOF: Withhold the sole bench reviewer beyond five hours; the gate must persist FORECAST_MISS before continuing.

Two blinded panel seats in pass 2 (sol, astra) independently raised the same `"predeclared stratified bootstrap"` underspecification as a blocker from the subject alone, without seeing the designers.

## Untested

Arbitration 2 KEPT / arbitration 1 REJECTED — recorded with the disagreement, not settled.

§1 | "A frame is a JSON line ... of at most 3500 UTF-8 bytes" | Bench payloads overflow routinely (`inbox-claude.jsonl`: 59/204 = 28.9% lines >3500 B, max 8,681 B; `messages.jsonl` max 51,355 B), making blob indirection the common path — but the blob's position in the durability-acknowledgment chain is unstated, so I could not test orphan-blob recovery read-only. | REPLACES: "oversized evidence is a content-addressed blob referenced by payload" -> "oversized evidence is a content-addressed blob fsynced and verified present before the frame append; recovery treats a frame with a missing blob as an unacknowledged tail" | PROOF: crash between blob write and head CAS; recovery must not acknowledge the frame. | COUNTER (arbitration 1): "§1 already requires durable Git objects before acknowledgment, and Scenario 61 explicitly tests objects and refs; an unacknowledged orphan blob does not violate that contract." Orchestrator check: §1 does require "durable Git object storage" for acknowledgment and Scenario 61's pass condition ends "crash tests cover objects and refs" — both verbatim — but neither names the blob-before-frame ordering, so the counter answers the orphan case and not the missing-blob-on-replay case. Bench re-measured: `~/.agent-bridge/state/inbox-claude.jsonl` 204 lines, 59 over 3500 B, max 8,681 B; `messages.jsonl` max 51,355 B (now 53,020 lines — the lane's n=52,964 predates live appends).

## Cross-section contradictions

The two arbitrations split on the one lint item that either kept; every other lint item was dropped by both.

§5 vs §11 Scenario 44 (arbitration 1 KEPT / arbitration 2 DROPPED) | LINT-CODEX: §5 "Every capacity input except M6 is a signed record" vs Scenario 44 "Every gate input resolves to a signed compatible value or explicit UNKNOWN" | Arbitration 1: §5 permits M6 as the reducer ledger without the signed M-record contract, whereas Scenario 44 accepts only signed compatible values or UNKNOWN; this defeats LINT-CLAUDE's blanket NONE. | Arbitration 2: §5 exempts M6 from the signed M-record schema without requiring it to be unsigned, so Scenario 44 is compatible. | Both quotes verified verbatim. Not settled; the spec's owner can close it with one clause naming M6's authentication in Scenario 44.

Dropped by both: LINT-CODEX probe executor (§3 floor answers through HELPER_RESULT vs §5 "The authenticated adapter alone executes probes" — both arbitrations: a floor answering after the adapter executes the call satisfies both). LINT-CLAUDE returned `NONE` over §2/§3/§4/§5 pairs; recorded as a lane result, not a conclusion.

## Arbiter losers

Rejected by both arbitrations unless marked. Each counterexample's premise was checked against the subject and found (verified verbatim: "never admission"; "caches are regenerable"; `P_pub=max(P_floor, c_p99)`; "No claim/vote operation takes `.git/index.lock`"; "authorized normal-index integration under a reducer-issued whole-checkout path allocation"; "one shared Windows checkout, `C:\code\Conjugal`"). No loser was rejected on a premise the subject lacks.

| defect class | loser | counterexample | orchestrator note |
|---|---|---|---|
| Reducer tick feasibility | DESIGN-SCOPE: 200 ms tick unachievable via git CLI | §1 separates the tick from derived publication period `P_pub` and permits regenerable caches; no serial per-lane `git show` every tick is required | sound on the text. The lane's 32–56 ms per-invocation latencies were NOT re-measured here (mlv-app measured 34–50 ms on its bench); the throughput exposure is unresolved |
| Cross-worktree exclusion | DESIGN-SCOPE: (repository, worktree, path) triples | §0 scopes execution to one shared checkout; §2 already requires whole-checkout allocation for branch/index mutations | sound on scope. Bench measurement reproduced exactly: 4 checkouts share one `.git` (`agent-bridge`, `-hub`, `-provider-seat-activation`, `.claude/worktrees/great-kapitsa-647dd7`) |
| Landing/index safety | DESIGN-SCOPE: mailbox-only landing | §5 specifies authorized normal-index integration under a whole-checkout allocation; §1's `index.lock` prohibition is scoped to claim/vote operations | sound. Bench: `master` is checked out at `C:/!Layi Wkspc/agent-bridge-hub` (reproduced); the phantom-deletion PROOF was not run |
| Dependency recursion | DESIGN-SCOPE: cycle guard and `max_depth=8` | §2's immutable certificate digests plus §4's current-certificate check fail a superseded cycle rather than recursing | sound on the stated cycle; the subject still states no memoization or depth bound for `ready_effective` evaluation cost |
| Admission utilization | DESIGN-VERIFY: per-resource utilization admission gate | §5 makes utilization advisory; §9 says `u_r` guides executor ramp "never admission" | sound — the replacement contradicts a binding directive. Bench citation `dual-lane-review/pack.json` reviewer `"max": 1` verified |
| Probe execution authority | LINT-CODEX: floor vs adapter | floor answering through HELPER_RESULT after the adapter executes satisfies §3 and §5 | sound |
| Blob acknowledgment | DESIGN-SCOPE Untested (arbitration 1 only) | see Untested | disagreement recorded there |
| M6 signatures | LINT-CODEX / LINT-CLAUDE NONE (split) | see Cross-section contradictions | disagreement recorded there |

## Panel

Scored by the tool from dimension numbers (never a seat's own average); pass-2 `panel.json`. Dimensions in order: Timeline Realism, Contract Completeness, Cross-Family Safety, Autonomy Achievement, Throughput Goal, Risk Mitigation.

| seat | family | TR | CC | CFS | AA | TG | RM | composite |
|---|---|---|---|---|---|---|---|---|
| panel-fable | claude | 80 | 85 | 90 | 87 | 82 | 88 | 85.33 |
| panel-opus | claude | 84 | 85 | 89 | 88 | 79 | 87 | 85.33 |
| panel-sonnet1 | claude | 64 | 60 | 84 | 74 | 72 | 79 | 72.17 |
| panel-sonnet2 | claude | 80 | 77 | 86 | 82 | 78 | 76 | 79.83 |
| panel-sonnet3 | claude | 80 | 78 | 88 | 85 | 79 | 87 | 82.83 |
| panel-astra | codex | 76 | 78 | 87 | 85 | 75 | 82 | 80.5 |
| panel-sol | codex | 84 | 78 | 92 | 92 | 88 | 94 | 88.0 |
| panel-luna | codex | 60 | 45 | 82 | 87 | 67 | 73 | 69.0 |

Composite 80.37 (equal mean, 8/8), spread 19.0. Reuse disclosure: `--from B` re-ran the panel as well as the arbiter, so pass 1 is a second full blinded panel on the same subject blob: composite 80.12, spread 17.67 (fable 85.5, opus 86.67, sonnet1 77.0, sonnet2 80.67, sonnet3 77.5, astra 79.83, sol 84.83, luna 69.0). The two panels land 0.25 apart; the luna seat scored 69.0 both times and is the floor in both.

Verified blocker quotes (pass 2; every quoted phrase grep-verified in the subject, backtick formatting aside):
- fable: "after 2b and G-MEASURE"; "in `committee/<S>.json`". The claim that G-MEASURE is "named, never specified" partly holds: §9's heading is "Throughput plan and G-MEASURE" and the term occurs 4 times, none defining its inputs or outputs.
- opus: "b=first_adoptions/elapsed_calendar_hours"; "depths 1 and 2 at the same derived P_pub"; "N_batch/max(P_pub, t_build, c)" (verbatim; the subject also carries the depth-1 form `N_batch/max(P_pub, t_build+c)`).
- sonnet1: "manifest-sum.py derives every phase forecast and derived budget from the manifest's explicit DAG"; "16–24 engineering hours (provisional)"; "T_m = max(48, 100 / (m × b)) h".
- sonnet2: "a crash after head publication but before client acknowledgment permits an idempotent retry"; "reducer-issued whole-checkout path allocation for reserved subject relay-land" — no acquisition timeout.
- sonnet3: "a round reopens only on a failed safety scenario or a REJECTED owner ratification"; "no termination confirmation ⇒ BLOCKED-TERMINATION, paths retained, no replacement writer"; "until still-qualified custody recovers or a §6 QUALIFY enrolls a replacement".
- astra: "require upfront component effort ranges"; "μ_receipt"; "predeclared stratified bootstrap".
- sol: "under enforced mutation admission"; "manifest's explicit DAG"; "predeclared stratified bootstrap".
- luna: "versioned per-provider, per-CLI-version mapping"; "16–24 engineering hours (provisional)".

Cross-family agreement worth reading: the `16–24 engineering hours` 1b-build estimate (sonnet1 claude, luna codex, and pass-1 luna) and the unspecified bootstrap (sol, astra) recur across families. No two seats disagreed on a checkable number.

## Classifier consensus

DID-NOT-RUN (0/3), gated by the arbiter sentinel. No TEXT/DESIGN classification, GROUNDED vote, must-fix list, STOPPING verdict or ceiling exists for this run, and none is inferred.

## Provenance

Output directory (local, not on the bus): `C:\!Layi Wkspc\agent-bridge\.claude-state\review-posture\agent-bridge-conjugal-20260914-a3`.

| stage | lane | model | pass | rc | bytes | sentinel |
|---|---|---|---|---|---|---|
| A | design-scope | claude-opus-5 | 1 | 0 | 5982 | RAN |
| A | design-verify | gpt-5.6-sol | 1 | 0 | 3952 | RAN |
| A | lint-claude | claude-haiku-4-5-20251001 | 1 | 0 | 2444 | RAN |
| A | lint-codex | gpt-5.6-luna | 1 | 0 | 571 | RAN |
| B | arbiter | gpt-6-astra | 1 / 2 | 0 / 0 | 9367 / 8466 | DID-NOT-RUN / DID-NOT-RUN |
| B | panel-fable | claude-fable-5 | 1 / 2 | 0 / 0 | 736 / 703 | RAN / RAN |
| B | panel-opus | claude-opus-5 | 1 / 2 | 0 / 0 | 705 / 678 | RAN / RAN |
| B | panel-sonnet1 | claude-sonnet-5 | 1 / 2 | 0 / 0 | 612 / 741 | RAN / RAN |
| B | panel-sonnet2 | claude-sonnet-5 | 1 / 2 | 0 / 0 | 653 / 742 | RAN / RAN |
| B | panel-sonnet3 | claude-sonnet-5 | 1 / 2 | 0 / 0 | 589 / 718 | RAN / RAN |
| B | panel-astra | gpt-6-astra | 1 / 2 | 0 / 0 | 720 / 741 | RAN / RAN |
| B | panel-sol | gpt-5.6-sol | 1 / 2 | 0 / 0 | 662 / 708 | RAN / RAN |
| B | panel-luna | gpt-5.6-luna | 1 / 2 | 0 / 0 | 677 / 702 | RAN / RAN |
| C | consolidator | claude-fable-5 | — | NONE | 0 | DID-NOT-RUN (blocked) |
| D | classifier-1..3 | claude-haiku-4-5-20251001 ×3 | — | NONE | 0 | DID-NOT-RUN (blocked) |

Timeline (UTC): stage A 20:41:52–20:46:49; stage B pass 1 20:46:49–20:50:37; stage B pass 2 (`--from B`) 20:51:16–20:56:01. Before `--from B` the subject blob (`b41e3af`) and bench HEAD (`e842e70`) were re-measured unchanged.

Attempts abandoned before this run, disclosed: attempt 1 (`…-20260914`, started 20:37:48Z) had its process tree killed at about 20:38:39Z by a peer session's pattern-matched cleanup (airmypc's RECEIPTS entry and its correction); attempt 2 (`…-a2`) was healthy but used an unmerged fix-branch `run.sh` and was stopped by this orchestrator after about a minute. Neither contributed any output to this filing.

Preflight: doctrine receipt SYNCED (13:46 CDT, parity MATCHED). `tools/check-cli-auth.py`, which lane-orchestrator §1 prescribes, exists in neither the doctrine nor the bench checkout; the Claude identity was read with the CLI's read-only status subcommand instead (logged in, firstParty, max, org matching the desktop). `codex login status` answered "Logged in using ChatGPT". From PowerShell, `bash` resolved to WSL (no distribution installed); every run used Git Bash `/usr/bin/bash`.

Re-measured by the orchestrator: every quoted subject phrase in stage A, both arbitrations' loser premises and all panel blockers (grep, whitespace-normalized); git 2.40.0.windows.1, files ref backend (no `extensions.refStorage`), 271 refs; 4 checkouts on one `.git` and `master` at `agent-bridge-hub`; `AGENTS.md:56` "4 failed / 467 passed … gives 471"; `dual-lane-review/pack.json` reviewer `"max": 1`; `core/routing.py` keyed by project and `session_id`; inbox and messages line sizes; §2 "(files backend)".

NOT re-measured: per-invocation git latencies (32/56/75 ms), the 7,848-file worktree count, packed-refs size, and every PROOF experiment (none was executed; all are proposals). Arbitration 2 appended a git-source link to the first design finding; it is not part of the filed line.
