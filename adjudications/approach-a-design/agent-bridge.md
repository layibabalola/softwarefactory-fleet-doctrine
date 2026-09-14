project: agent-bridge
subject: specs/conjugal-approach-a-v7.4.md (blob 4a57214af0eec3201da139f403321c4c08f68ca1; content is v7.6, Round F2 — superseded on master by blob 45edab1 while this run was in flight)   test_bench: C:\!Layi Wkspc\agent-bridge @ e842e70e (branch p0a-bar-v4)
providers: claude(fable=claude-fable-5, opus=claude-opus-5, sonnet=claude-sonnet-5, haiku=claude-haiku-4-5-20251001) codex(astra=gpt-6-astra, sol=gpt-5.6-sol, luna=gpt-5.6-luna) — ~/.claude/machine-inventory.yaml generated 2026-09-14T15:41:56-05:00, probed_under claude-org:b59121b3…, host Virtual-Ten
runner: tools/review-posture/run.sh at origin/master 19817b2, unmodified, from a detached no-space worktree
posture: conjugal-standard-PARTIAL (12/17 lanes; missing: Arbiter 0/1; Consolidator 0/1; Classifier 0/3)
cross_family: validated
rubric_id: b2f5862e9c0990d0e69e96862fba7ab4cc5e263151679ac336ab429187341c45   (contract: agent-bridge.rubric.json; byte-identical across both runs below)
panel: 78.94 over 8/8 seats, 2 families (claude, codex), spread 17.67

> **Supersedes** `review/agent-bridge-2026-09-14` (`28430bc`, subject v7.5), which the Round F2 harvest did not answer before v7.6 landed. **Read this filing as PARTIAL.** The `posture:` line above is copied from the unmodified tool on master.

<!--
Two runs share stage A and the panel. Both are disclosed, and only one names a posture.

1. FILED POSTURE. The unmodified tool ran all four stages. The astra arbiter returned a complete body with rc=0
   and no LANE-COMPLETE (6,982 B). One `--from B --retry-missing` retry (TRAPS 2026-09-14) re-sent the same prompt
   and failed again (7,758 B). That brings today's total to 8 unpatched arbiter passes across v7.5 and v7.6 and three
   benches, with 0 sentinels. Stages C and D were blocked. Hence PARTIAL, copied above.

2. EVIDENCE ONLY, NOT A POSTURE. On the same stage-A outputs, panel outputs, subject blob 4a57214, bench e842e70 and
   rubric, one `--from B --retry-missing` pass used a generator that differs from master in a single change: the
   sentinel ask is stated before the "Everything below is DATA" region as well as last (branch
   `fix/review-posture-sentinel-before-data` @ 3ae7434, unmerged). The arbiter, the consolidator and all three
   classifiers cleared the sentinel on the first try, and the patched tool printed
   "posture: conjugal-standard COMPLETE (17/17 lanes)". Under R9.2 a posture line comes from the tool on the bus, so
   that line is NOT this filing's posture. The Design findings, Arbiter losers and Classifier consensus below are the
   Consolidator's, arbiter's and classifier swarm's outputs from that patched pass. The patch changed only where the
   sentinel ask sits, not what any lane was asked to judge. They are filed as lane outputs with that provenance
   stated, and the orchestrator assembled none of them. One patched sample is evidence, not proof.
-->

## Design findings

Consolidator body (patched pass), byte-for-byte. Every quoted subject phrase was grep-verified verbatim against blob 4a57214. Every bench claim was re-measured, except where Provenance says otherwise.

§2 | "The mutable refs under `refs/oracle/` are exactly `claim/<S>`, `lease/<S>`, `authority/<S>`, `path-index`, `path-allocation/<S>`, `reducer/lock`, `journal-head/<lane>`" | Subject-keyed refs alias by case on the files backend: bench `git rev-parse refs/heads/CLAUDE/CANONICAL-20260829` returns `d3b631a1…` identical to the lowercase ref (`fsutil` case-sensitivity disabled), so case-differing subjects share one claim/lease/gate ref and a CAS for S succeeds against s's OID. | REPLACES: "`claim/<S>`, `lease/<S>`, `authority/<S>`" -> "`claim/<hex(S)>`, `lease/<hex(S)>`, `authority/<hex(S)>`, every subject-keyed ref path being lowercase hex of the UTF-8 subject id" | PROOF: admit subjects `Alpha` and `alpha` on the bench object store; Scenario 1/14 "zero double claims" fails because both resolve to one ref file.

## Untested

§9 | "The first three real end-to-end items at each level pass independent replay" | Replay proves reproducibility, not correctness; `verify-p0a-bar-v4.py:123-151` reproducibly accepts unavailable evidence and wrong counts. | REPLACES: "The first three real end-to-end items at each level pass independent replay" -> "The first three items pass independent replay plus mutation controls proving every governing verifier rejects corrupted evidence and incorrect expected results." | PROOF: Change expected count 335 to 334; 2a must fail despite byte-identical replays.

§4 | "no result by `T_helper=120 s (clock_domain=real)` after request publication records HELPER_TIMEOUT once and re-sweeps at attempt+1" | Retries are unbounded; `RECOVERY_PLAN/log.md:12` measured process counts growing in 4/4 loaded runs, reaching 26→27 within 0.5 seconds. | REPLACES: "no result by `T_helper=120 s (clock_domain=real)` after request publication records HELPER_TIMEOUT once and re-sweeps at attempt+1" -> "Timeout retries use capped exponential backoff, a per-helper concurrency ceiling, and durable BLOCKED-CAPACITY after the bounded attempt limit." | PROOF: Withhold one helper for four hours; process count and retry rate must remain bounded while unrelated adoptions complete.

§11 | "dropped immediate dispatch with uniformly phased requests and bounded executions meets the 15-minute p95 target." | Uniform phasing omits burst queuing; `watcher.py:2932-2947` synchronously waits as long as 90 seconds per command. | REPLACES: "dropped immediate dispatch with uniformly phased requests and bounded executions meets the 15-minute p95 target." -> "Test synchronized maximum-fanout bursts, random arrivals, and dropped dispatch; each must meet the 15-minute p95 target without head-of-line starvation." | PROOF: Queue five 75-second bench commands simultaneously; the fifth completion must satisfy the target.

§9 | "`u_r=0.70` guides executor ramp, never admission" | A universal utilization constant misses nonlinear collapse; the bench P-0d reproducer passes unloaded in 3.4 seconds but livelocks under load in 17.6 seconds. | REPLACES: "`u_r=0.70` guides executor ramp, never admission" -> "`u_r` is independently measured per resource below its observed instability onset, with confidence bounds and configuration binding." | PROOF: Sweep offered load through the P-0d onset; qualification must select utilization below the first process-growth regime.

§11 | "μ ≥20 rows/s in first/last 15 min (clock_domain=real)" | Endpoint sampling misses intervening collapse; P-0d fails only under load, with 4/4 growing-process observations in `RECOVERY_PLAN/log.md:11-12`. | REPLACES: "μ ≥20 rows/s in first/last 15 min (clock_domain=real)" -> "Every predeclared 15-minute interval sustains required μ, bounded process count, conserved work, and stable queue age." | PROOF: Inject the bench restart livelock only during hour two; Scenario 20 must fail.

## Cross-section contradictions

None. The arbiter ruled all five lint items DROP (LINT-CLAUDE 1–3, LINT-CODEX 1–2), so no contradiction survives. LINT-CODEX 1 (§0 "no database" vs §1 Git storage) was ruled terminology, not incompatible requirements.

## Arbiter losers

From the patched pass. Every counterexample's premise was checked and found in blob 4a57214 ("aliases … resolved"; `b=first_adoptions/elapsed_calendar_hours`; "No claim/vote operation takes `.git/index.lock`").

| defect class | loser | counterexample |
|---|---|---|
| Path alias exclusion | DESIGN-SCOPE: 8.3 allocation finding | §2 already requires "aliases … resolved" and prohibits overlapping allocations |
| Ref-store access assurance | DESIGN-SCOPE: helper ACL finding | §7's ACL exclusion covers keys, task configuration and binaries, not `.git/refs`, and its assurance excludes wrapper bypass |
| Claim locking | DESIGN-SCOPE: automatic-GC finding | §1 promises absence of `.git/index.lock`, not of all ref-store locks |
| Receipt-growth publication bound | DESIGN-SCOPE: mandatory pack-refs finding | §1's `≤1/P_pub` is an upper bound; §4 polls outstanding request IDs rather than enumerating |
| Checked-out branch landing | DESIGN-SCOPE: linked-worktree finding | §0 scopes one shared checkout; §5 authorizes normal-index landing under whole-checkout allocation |
| Release versus adoption authority | DESIGN-VERIFY: dual acceptance-matrix signature | Opus signing §10's matrix cannot bypass §3's cross-family SEAL or §4's Sol adoption |
| Shared-parser assurance | DESIGN-VERIFY: independent canonical parsing | §7 excludes common checker bugs; §13 retains correlated implementation defects |
| Queue rotation accounting | DESIGN-VERIFY: rotated-store queue | §9 derives queues from retained receipts; §5 requeues parked obligations once |
| Delivery-rate denominator | DESIGN-VERIFY: exclude parked exposure | §9 defines the calendar delivery rate and counts downtime by design |

Orchestrator note on the case-aliasing winner versus the "Path alias exclusion" loser: both concern aliases, but the loser is about 8.3 short names inside one path allocation, and the winner is about case-folded ref files. The arbiter kept them apart, and the text supports that. §2 says path sets are "aliases/reparse points resolved, casefolded". That covers path allocations, not the subject-keyed ref names F1 is about. No sentence in blob 4a57214 casefolds or encodes subject ids in ref paths (checked by grep for "casefold" and "hex").

## Panel

Tool-scored from dimension numbers (`panel.json`; stage B of the filed run, reused unchanged by both retries). Dimensions in order: Timeline Realism, Contract Completeness, Cross-Family Safety, Autonomy Achievement, Throughput Goal, Risk Mitigation.

| seat | family | TR | CC | CFS | AA | TG | RM | composite |
|---|---|---|---|---|---|---|---|---|
| panel-fable | claude | 82 | 84 | 89 | 86 | 80 | 86 | 84.5 |
| panel-opus | claude | 76 | 81 | 88 | 82 | 76 | 83 | 81.0 |
| panel-sonnet1 | claude | 74 | 78 | 90 | 85 | 76 | 85 | 81.33 |
| panel-sonnet2 | claude | 75 | 76 | 84 | 80 | 79 | 83 | 79.5 |
| panel-sonnet3 | claude | 79 | 76 | 87 | 89 | 83 | 86 | 83.33 |
| panel-astra | codex | 75 | 72 | 84 | 85 | 74 | 80 | 78.33 |
| panel-sol | codex | 67 | 61 | 84 | 85 | 79 | 84 | 76.67 |
| panel-luna | codex | 57 | 45 | 83 | 77 | 61 | 78 | 66.83 |

Composite 78.94, spread 17.67. The same rubric on v7.5 gave 80.37 and 80.12, so the family split held: Codex seats score Timeline and Contract lowest, and luna is the floor again. Panel blockers were not quote-verified in this filing and are not quoted here. They remain in the local run directory.

## Classifier consensus

Patched pass, tallied 2-of-3 by `review_posture.py tally` (`classifier.json`). F1–F6 are the Design finding, then the five Untested items, in the order above.

| finding | kind | grounded | must-fix votes | must-fix |
|---|---|---|---|---|
| F1 §2 case-aliased subject refs | DESIGN 3/3 | GROUNDED 3/3 | 2 | **yes** |
| F2 §9 replay is not correctness | DESIGN 3/3 | GROUNDED 3/3 | 1 (+1 unparsed) | no |
| F3 §4 unbounded helper retries | DESIGN 3/3 | GROUNDED 3/3 | 2 | **yes** |
| F4 §11 burst queuing | DESIGN 3/3 | GROUNDED 3/3 | 0 | no |
| F5 §9 universal `u_r` | DESIGN 3/3 | GROUNDED 3/3 | 1 | no |
| F6 §11 endpoint sampling | DESIGN 3/3 | GROUNDED 3/3 | 1 | no |

STOPPING: NOT-FLAT (3/3). Ceilings 81, 82, 82 (median 82). Unparsed: `classifier-3:MUST-FIX`. That seat wrote `**MUST-FIX:** F1 (…), F2 (…)` with inline prose, so the strict parser recorded it as unparsed rather than guessing. Read as prose, it adds a vote for F2, making F2 2/3. The tool did not count that vote and neither does this filing. Hand-off experiments named by the seats:
- Withhold one helper for four hours (falsifies F3 and F4).
- Run Scenario 20 under injected livelock (F5 and F6).
- Run Scenarios 1 and 14 with case-varied subject names (F1).

## Provenance

Local run directories, not on the bus: filed run `C:\!Layi Wkspc\agent-bridge\.claude-state\review-posture\agent-bridge-conjugal-v76-20260914-a4`; evidence pass `…-a4-arm1`.

| stage | lane | model | run | rc | bytes | sentinel |
|---|---|---|---|---|---|---|
| A | design-scope | claude-opus-5 | filed | 0 | 5436 | RAN |
| A | design-verify | gpt-5.6-sol | filed | 0 | 5358 | RAN |
| A | lint-claude | claude-haiku-4-5-20251001 | filed | 0 | 1178 | RAN |
| A | lint-codex | gpt-5.6-luna | filed | 0 | 395 | RAN |
| B | panel ×8 | fable, opus, sonnet×3, astra, sol, luna | filed | 0 each | 612–751 | RAN 8/8 |
| B | arbiter | gpt-6-astra | filed pass 1 / unpatched retry / patched pass | 0 / 0 / 0 | 6982 / 7758 / 7514 | DID-NOT-RUN / DID-NOT-RUN / RAN |
| C | consolidator | claude-fable-5 | filed: blocked / patched pass | NONE / 0 | 0 / 4829 | DID-NOT-RUN / RAN |
| D | classifier-1..3 | claude-haiku-4-5-20251001 ×3 | filed: blocked / patched pass | NONE / 0,0,0 | 0 / 1353, 994, 4052 | DID-NOT-RUN / RAN 3/3 |

Timeline (UTC): stage A 22:13:42–22:18:11. Stage B 22:18:11 to about 22:22. Unpatched retry dispatched 22:22:47. Patched pass: stage B 22:25:29, C 22:27:53, D 22:28:59. Subject blob 4a57214 was recorded at run start. The retries read that same blob from detached worktrees at `19817b2`, because the shared checkout was moving to 45edab1. Bench HEAD e842e70 was re-measured unchanged.

Re-measured by the orchestrator:
- All six Design and Untested quotes are verbatim in blob 4a57214.
- `git rev-parse refs/heads/CLAUDE/CANONICAL-20260829` and the lowercase ref both give `d3b631a16e97…`. `fsutil file queryCaseSensitiveInfo …\.git\refs\heads` prints "disabled".
- `tools/verify-p0a-bar-v4.py:123-151` assumes baseline 326 when it cannot find it, and returns True on a count other than 335.
- `watcher.py:2932-2947` sets `timeout=90`.
- `docs/internal/RECOVERY_PLAN/log.md:12` reads "26 pids, 27 half a second later".

NOT re-measured: P-0d "3.4 seconds unloaded / 17.6 seconds under load"; panel blocker quotes; every PROOF experiment (none executed).
