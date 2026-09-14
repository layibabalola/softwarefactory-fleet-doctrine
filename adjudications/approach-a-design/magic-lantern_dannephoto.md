project: magic-lantern_dannephoto
subject: specs/conjugal-approach-a-v7.4.md (blob 11af78fa, unchanged from 9f3b1a9 through review)
test_bench: C:\code\magic-lantern_dannephoto @ 1dc6162 (codex/audit-remediation-2026-07)
providers: claude(fable,opus,sonnet,haiku) codex(astra,sol,luna) from ~/.claude/machine-inventory.yaml; no third family in inventory
posture: conjugal-standard COMPLETE (computed: 17/17 role lanes cleared LANE-COMPLETE; table in Provenance)
cross_family: validated (a claude and a codex lane cleared the sentinel in every stage)
seats: designers opus-5 + sol (high); lint haiku-4-5 + luna; arbiter astra; consolidator fable-5; panel fable, opus, sonnet x3, astra, sol, luna; classifier haiku x3 (2-of-3)
rubric_id: e6761fbde1fdb398a2f261e9fd69f9e3e39ab3ad9997797a1e751b6b54f79b6d
panel: composite 78.73 over 8/8 seats, 2 families, seat spread 15.2

<!-- Supersedes this file at f4a032c, which ran designers + lint + an arbiter that saw no lint and was never asked for
     losers, and filed 16 design findings under a conjugal-standard label it had not earned. The full posture kept
     6 + 1 Untested and rejected 9 with counterexamples. -->

## Design findings (Fable consolidation of Astra's arbitration)

§5 | "commits the merged blob by private index (`read-tree HEAD`, `commit-tree`, `update-ref` CAS on master's expected tip" | Bench HEAD is `codex/audit-remediation-2026-07`, 311 commits ahead of master (0b9527e); a HEAD-built tree committed onto master squashes those 311 commits, and the marker never appears "in HEAD", so the relay re-appends every tick. | REPLACES: "CAS on master's expected tip" → "CAS on the ref that `git symbolic-ref HEAD` names, refusing a detached HEAD" | PROOF: in a bundle clone, run the relay once. Check `git rev-list --count master` and `git grep "[outbox:1]" HEAD` before and after.

§7 | "Reducer mutex identity is the `.git` directory file identity" | The bench has 4 worktrees; `.claude/worktrees/cool-saha-5e2996/.git` is a gitfile into `.git/worktrees/…`, so each worktree gets a distinct FileId and mutex while all share `refs/oracle/*`, and `coordination/oracle/journal/<lane>.ndjson` resolves differently per worktree. | REPLACES: "the `.git` directory file identity" → "the file identity of `git rev-parse --git-common-dir`, with journals resolved under that common directory" | PROOF: run `--ensure` in the main checkout and in cool-saha-5e2996. Both should get distinct mutexes, and the two worktrees end up with different journal files.

§4 | "signing ADOPT_REQUEST only after its own independent replay agrees." | Replay proves control-state consistency, not test execution: roadmap/recovery/CONTINUE.md rejects model PASS alone, and tools/roadmap/recovery-transaction.py explicitly treats check argv as metadata. | REPLACES: "signing ADOPT_REQUEST only after its own independent replay agrees." → "Sign only after replay agrees and the pinned risk-class acceptance evidence has been independently executed or authenticated." | PROOF: Supply self-consistent fabricated PASS logs; adoption must reject them without authenticated execution receipts.

§5 | "`executors=5 (provisional)`, from the first real minute in both budget modes" | Bench summary shows eligible_cards=0 and no_implementation_workers_active=true; automatic five-executor admission violates the proven stop condition and burns capacity with no owner-valued work. | REPLACES: "`executors=5 (provisional)`, from the first real minute in both budget modes" → "Admit at most five executors, bounded by owner-authorized eligible subjects; zero eligible subjects admits zero executors." | PROOF: Run admission against execution-state.json; executor count must remain zero.

§9 | "saturation experiments maintain an implementation input backlog." | roadmap/recovery/execution-state.json reports eligible_cards=0 and no active workers; manufacturing a backlog repeats the control-plane-work failure documented in HANDOFF.md. | REPLACES: "saturation experiments maintain an implementation input backlog." → "Saturation experiments consume only pre-existing owner-authorized eligible work; without it, record INSUFFICIENT and dispatch nothing." | PROOF: Start G-MEASURE from current bench state; assert zero new subjects and provider calls.

§9 | "`b=first_adoptions/elapsed_calendar_hours`." | execution-state.json is waiting_external with five blocked cards; calendar-time b decays during input starvation, so later multiples rise without any added factory capacity. | REPLACES: "`b=first_adoptions/elapsed_calendar_hours`." → "Report calendar delivery rate separately; capacity baselines use hours having owner-authorized eligible input." | PROOF: Compare ratios including versus excluding the bench’s waiting_external interval; capacity qualification must remain invariant.

## Untested

§2 | "receipt commits at `refs/oracle/receipts/<receipt_seq>`" | One ref per receipt with no pruning rule grows refs without bound; the bench holds only 7 loose refs plus packed-refs, so growth could not be measured there. | REPLACES: "receipt commits at `refs/oracle/receipts/<receipt_seq>`" → "receipt commits chained under the single ref `refs/oracle/receipts`" | PROOF: Stage S at 50,000 frames, measuring `git for-each-ref` latency.

## Cross-section contradictions (lint, after arbitration)

(none — the arbiter kept no lint items: LINT C produced no findings to adjudicate, and both LINT D items were dropped)

## Arbiter losers (rejected with a counterexample; read these before re-filing any of them)

For the rejected findings below, the existing specification wins; no combined or third replacement is proposed.

Helper custody | REVIEW A §4 “under its dedicated principal” | A same-SID helper already violates §7’s separate identities and ACLs excluding every lane runner, with custody ACL attestation required by §6.

Helper-result poisoning | REVIEW A §4 key_id-suffixed result ref | A runner with the alleged raw-ref write access can pre-create `<request_id>/<helper key_id>` too; signature rejection does not unblock the helper’s zero-OID CAS.

Interactive executor compatibility | REVIEW A §2 wrapper-only claims replacement | A manually opened thread without a Job Object is already outside §2’s executor contract; §7 explicitly excludes wrapper bypass.

Mirror branch divergence | REVIEW A §1 `mirror_ref` replacement | A telemetry-only commit can diverge master without requiring any integration merge, because §1 makes the mirror non-authoritative.

Legacy authority migration | REVIEW A §0 automatic certificate import | A legacy `accepted_commit` row without V proofs or a current attestation envelope cannot satisfy §4 readiness merely by being pinned as a certificate.

Zero-executor recovery bound | REVIEW A §7 floor-readiness replacement | A disabled floor already falls under §7’s explicit reference to §13, which declares never-firing-floor supervision unbounded.

Adoption versus delivered outcomes | REVIEW B §9 separate outcome counters | Eleven legacy DONE rows with no authorized Oracle ADOPTED records contribute zero to the specified counter; the claimed eleven-item result also conflicts with A’s missing-authority observation.

Proportional verification | REVIEW B §3 risk-profile substitution for two A checks | A docs-only subject can use lightweight acceptance evidence while both deterministic A checkers still verify transition integrity; removing that quorum changes a different safety property.

Adopter availability | REVIEW B §4 policy-selected integration writer | A pre-build checkout lacking `oracle-adopt.py` is consistent with §10’s planned adopter implementation and §4’s explicit deferral when runner or key access is missing.

## Panel (blinded; Conjugal Round 15 dimensions and lenses; scoring contract in `magic-lantern_dannephoto.rubric.json`)

| seat | family | Timeline Realism | Contract Completeness | Cross-Family Safety | Autonomy Achievement | Throughput Goal | Risk Mitigation | composite |
|---|---|---|---|---|---|---|---|---|
| fable | claude | 86 | 85 | 90 | 86 | 82 | 88 | 86.2 |
| opus | claude | 70 | 74 | 84 | 80 | 67 | 77 | 75.3 |
| sonnet1 | claude | 60 | 80 | 87 | 85 | 79 | 86 | 79.5 |
| sonnet2 | claude | 78 | 74 | 85 | 80 | 72 | 80 | 78.2 |
| sonnet3 | claude | 74 | 78 | 83 | 87 | 80 | 84 | 81.0 |
| astra | codex | 76 | 69 | 83 | 78 | 72 | 79 | 76.2 |
| sol | codex | 72 | 76 | 91 | 83 | 84 | 89 | 82.5 |
| luna | codex | 64 | 60 | 88 | 72 | 64 | 78 | 71.0 |
| **mean** | | 72.5 | 74.5 | 86.4 | 81.4 | 75 | 82.6 | **78.73** |

Composites are recomputed from the six dimension numbers, never taken from the seat (Opus corrected its own average).
Not comparable with Conjugal's R15 83.7: this panel was not shown score history, so the contract and `rubric_id` differ.

Top blockers (all 27 quoted phrases verified verbatim in the subject):

- **fable**: Throughput multiples wait on a 336 h runway: "`baseline_items_per_h` (b, M1) is `provisional` until measured"; until then 2b yields absolute rates only.
- **fable**: Latch/rotation evidence rests on an unbuilt 16–24 h adapter: "Until the adapter ships, or when extraction is unsupported, malformed or contradictory, `providers[p]` is UNKNOWN".
- **fable**: 63-level budget "derived:3600×(5+T_m+2)/level" reads as division by level, contradicting "B63 = 3600·Σ_m(5+T_m+2)"; an implementer must ask which.
- **opus**: Pipelining credit can be zero by definition: if P_pub ≥ t_build+c, then μ1=μ2. "only `μ2−μ1` at identical P_pub" leaves nothing to measure. The Scenario 68 budget of 43,200 s also gives each depth ≤2 h per level.
- **opus**: Git refs grow without limit: one "`refs/oracle/receipts/<receipt_seq>`" ref per 200 ms tick is ~432k loose refs/day. The bench repo has 51 refs. No pack or GC policy exists, so the substrate is not proven non-bottleneck.
- **opus**: Renewing the lock every 30 s changes its OID, and nothing says this avoids aborting in-flight "reducer lock OID verified in the publishing transaction" commits. Separately, STUB rows sum to 33,540 s, not the stated "1d `33,240 s`".
- **sonnet1**: "T_m = max(48, 100 / (m × b))" has no ceiling; low measured b can inflate G-MEASURE duration indefinitely, unaddressed.
- **sonnet1**: 1b-build's "16–24 engineering hours (provisional)" likely underestimates building the full described vertical slice plus quota adapter.
- **sonnet1**: 2a gate's "extended on insufficient completions" has no stated cap, unlike 2b's explicit 2T_m INSUFFICIENT stop rule.
- **sonnet2**: Lane append-helper mutex has no OS primitive spec (unlike reducer's), just "serialized by a lane mutex" — Luna cannot implement without guessing.
- **sonnet2**: Relay and mirror both do private-index commits to master with no joint contention scenario testing them racing each other.
- **sonnet2**: Pipelining safety rests on asserted timing, "rereading it at each build stage and before handoff," with no bounded TOCTOU proof for the reread-to-CAS window.
- **sonnet3**: WAIT-FAMILY/BLOCKED-CAPACITY has no owner alert channel like latches' outbox; it "thereafter wakes only on capacity evidence" — a stalled lane may never be noticed.
- **sonnet3**: Tier 0 reopening depends on "a REJECTED owner ratification" whose actor, procedure, and timeout are never defined anywhere in the document.
- **sonnet3**: Resource-gate constant u_r=0.70, marked unmeasured (M3), still "guides executor ramp, never admission" for scaling decisions with no validation path.
- **astra**: HELPER_REQUEST omits seat/helper_id and leaves idem derivation undefined; "first result per request_id" risks collapsing two cross-family checks at identical attempts.
- **astra**: With "N_batch=100" and 200-ms ticks, capacity cannot exceed 500 rows/s; required D15≤350 remains unmeasured, and receipt-commit rates lack row conversion.
- **astra**: Tier 0 claims "stopping rule fired" despite R15 pending and absent rubric-contract evidence establishing three consecutive comparable flat rounds.
- **sol**: Phase forecasts depend on an external "explicit DAG"; row edges and 1b/1c/1e makespans are absent, making the schedule irreproducible.
- **sol**: BLOCKED-CAPACITY "wakes only on capacity evidence" omits ordinary role completion or slot release, permitting permanent stalls after the 15-minute cutoff.
- **sol**: The anchor verifies an "anchored genesis/policy-chain digest", but defines no atomic anchor-update or rollback procedure for amendments or owner-key rotation.
- **luna**: Quota adapter contract is not executable: "versioned per-provider, per-CLI-version mapping" lacks actual mappings, fingerprints, reset semantics, and rate coefficients.
- **luna**: Registry ownership conflicts: "GATE_CLOSE | reducer" but "Adoption CASes the gate CLOSED"; actor, fence, and CAS authority are not uniquely implementable.
- **luna**: Phase 1 DAG is deferred: "Remaining components are estimated from the completed slice"; 1b/1e budgets and dependency witnesses are absent before implementation.

**Unresolved panel disagreement, measured by the orchestrator.** Fable says the §11 STUB rows reproduce "1d `33,240 s`";
Opus says they sum to 33,540 s. Neither reproduces. `1d-extended` 87,900 s does reproduce exactly (SUBSTRATE and MIXED
rows not named in another phase, including 20 and 68). STUB rows not named in another phase sum to 32,220 s; all STUB
rows sum to 33,420 s. Phase-1d membership is not derivable from the document alone, consistent with Sol's blocker that
the "explicit DAG" lives outside it.

## Classifier consensus (Haiku x3, independent; 2-of-3 lands, minority recorded)

| finding | TEXT/DESIGN | GROUNDED | must-fix votes |
|---|---|---|---|
| F1 §5 relay CAS on master | DESIGN 3/3 | 3/3 | 3/3 **MUST-FIX** |
| F2 §7 mutex per worktree | DESIGN 3/3 | 3/3 | 3/3 **MUST-FIX** |
| F3 §4 replay is not execution | DESIGN 3/3 | 3/3 | 3/3 **MUST-FIX** |
| F4 §5 executors=5 at zero eligible | DESIGN 3/3 | 3/3 | 3/3 **MUST-FIX** |
| F5 §9 manufactured backlog | DESIGN 3/3 | 3/3 | 2/3 **MUST-FIX** |
| F6 §9 calendar-hour b | DESIGN 3/3 | 3/3 | 2/3 **MUST-FIX** |
| F7 §2 receipt refs (Untested) | DESIGN 3/3 | 2/3 (minority: unmeasurable on bench) | 1/3, does not land |

- **STOPPING: FLAT, 3/3.** No finding is TEXT, so a wording-only round moves nothing. Ceilings 79.1 / 80.2 / 81.0 (median 80.2).
- **HAND-OFF: no 2-of-3 on a single experiment** (Scenario 66 slice / extended Scenario 59 / one relay run on the bench).
  All three include executor admission against the bench's `eligible_cards=0`; two include one relay run on a HEAD 311
  commits ahead of master. Those two checks are the consensus core.
- Attribution caution ("cheap seats find well, attribute badly"): classifier-3 grounded F7 on "7 loose refs showing
  growth"; the bench has 51 refs in total (`git for-each-ref | wc -l`) and no growth series at all.

## Provenance

| stage | lane | model | rc | bytes | sentinel |
|---|---|---|---|---|---|
| A (reused) | design-scope | claude-opus-5 | 0 | 5897 | RAN |
| A (reused) | design-verify | gpt-5.6-sol | 0 | 4316 | RAN |
| A (reused) | lint-claude | claude-haiku-4-5-20251001 | 0 | 1905 | RAN |
| A (reused) | lint-codex | gpt-5.6-luna | 0 | 609 | RAN |
| B | arbiter | gpt-6-astra | 0 | 7148 | RAN |
| C | consolidator | claude-fable-5 | 0 | 4729 | RAN |
| B | panel-fable | claude-fable-5 | 0 | 1438 | RAN |
| B | panel-opus | claude-opus-5 | 0 | 936 | RAN |
| B | panel-sonnet1 | claude-sonnet-5 | 0 | 585 | RAN |
| B | panel-sonnet2 | claude-sonnet-5 | 0 | 637 | RAN |
| B | panel-sonnet3 | claude-sonnet-5 | 0 | 665 | RAN |
| B | panel-astra | gpt-6-astra | 0 | 677 | RAN |
| B | panel-sol | gpt-5.6-sol | 0 | 661 | RAN |
| B | panel-luna | gpt-5.6-luna | 0 | 689 | RAN |
| D | classifier-1 | claude-haiku-4-5-20251001 | 0 | 2782 | RAN |
| D | classifier-2 | claude-haiku-4-5-20251001 | 0 | 3560 | RAN |
| D | classifier-3 | claude-haiku-4-5-20251001 | 0 | 2521 | RAN |

- **Stage A reused, disclosed.** Designers and lint ran 2026-09-14T03:52:39Z; stages B-D ran 16:05:03Z-16:10:06Z. Reuse
  is valid only because the subject blob (11af78fa) and bench HEAD (1dc6162) were re-measured unchanged before dispatch.
- **Lint.** Haiku lint returned no contradictions (a null result that still cleared the sentinel). Luna's two were both
  DROPPED by the arbiter, with reasons below. No cross-section contradiction survives.
- **Panel families: 2, not the 3 the posture table names.** The inventory has no third family, and Conjugal's own
  Round 15 panel (fable, opus, sonnet x3, astra, sol, luna) was 2 families as well; the table and the practice disagree.
- **Orchestrator verification (§2b).** Every design-finding quote grep-confirmed. Bench re-measured: 311 commits ahead of
  master (0b9527e); 4 worktrees; `eligible_cards: 0`; `status: waiting_external`; no `coordination/oracle/`; every
  scheduled task `layib`/Interactive/Limited with the Lane Supervisor Disabled; 51 refs. Not re-measured: "five blocked
  cards" and the `CONTINUE.md` / `recovery-transaction.py` characterisations.
- **Raw lane outputs and prompts stay local (Law 4).**

## Lint rulings

- **LINT C — no findings to adjudicate.** Its report is not evidence that the executable scenarios passed.
- **LINT D, Tier 2 publication — DROP.** Publishing immutable signed evidence is distinct from writing authoritative Oracle state; §4 reserves disposition and state effects to the reducer. This neither duplicates nor undermines A’s custody or ref-poisoning findings: those concern access and availability, not who applies state transitions.
- **LINT D, ADOPT_DISPATCH fences — DROP.** The encompassing SEAL transaction requires `S` for its subject-state mutation and also satisfies ADOPT_DISPATCH’s `C+E-seat+L` requirements; the registry does not prohibit a stronger enclosing transaction. This duplicates or undermines no designer finding.
