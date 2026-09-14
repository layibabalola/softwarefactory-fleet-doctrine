project: airmypc
subject: specs/conjugal-approach-a-v7.4.md (blob b41e3af00b757f96030e5127d170940776362cf0)
test_bench: C:\temp\AirMyPC @ 2e0aa41 (docs: parallel work analysis and roadmap constraint)
providers: claude (claude-fable-5, claude-opus-5, claude-sonnet-5, claude-haiku-4-5-20251001)
posture: conjugal-standard-PARTIAL (7/17 lanes; missing: Designer-Verify 0/1; Lint-Consistency 1/2; Arbiter 0/1; Consolidator 0/1; Panel 5/8; Classifier 0/3)
cross_family: NO-CROSS-FAMILY-VALIDATION
rubric_id: b2f5862e9c0990d0e69e96862fba7ab4cc5e263151679ac336ab429187341c45
panel: 81.37 over 5/8 seats, 1/2 families (claude only), spread 13.34

## Design findings (Designer-Scope lane, Opus/Claude)

§1 | "Each lane has one authorized append helper at `<git-common-dir>/oracle/journal/<lane>.ndjson`, serialized by a lane mutex derived from §7 repository identity plus lane." | `git rev-parse --git-common-dir` returns relative `.git` in main checkout but absolute in worktree; helper's cwd picks the file, so one lane gets two journals under one mutex. | REPLACES: "`<git-common-dir>/oracle/journal/<lane>.ndjson`" with "`<§7 absolute handle-resolved common dir>/oracle/journal/<lane>.ndjson`" | PROOF: start lane helper from main and worktree; two `.ndjson` files at seq=1 falsifies single-writer guarantee.

§2 | "unknown scope and branch/index mutations acquire the whole checkout" | 34 worktrees share one `.git`; two subjects allocate disjoint paths yet mutate one ref store with no checkout-level boundary. | REPLACES: "acquire the whole checkout" with "acquire every worktree path set enumerated by `git worktree list --porcelain` on the shared common dir" | PROOF: allocate different paths to two subjects in different worktrees; concurrent master advances show lost-update window.

§4 | "Each `inputs/<batch_id>.json` pins every decision input: prior_state_oid, receipt commit/ordering and journal byte ranges, relevant mutable-ref OIDs and transitions" | Pinned OIDs of deleted refs (PENDING_TRANSFER "empties" them) become unreachable; gc.pruneExpire unset, gc has run with 5 packs, 0 garbage. | REPLACES: "pins every decision input" with "pins every decision input and anchors each OID at immutable `refs/oracle/closure/<batch_id>/<oid>`, with `gc.pruneExpire=never` verified at start" | PROOF: pin pending-ref OID, delete ref, `git gc --prune=now`, then verify; missing-object falsifies replay closure.

§1 | "durable Git object storage with `core.fsync=loose-object,pack,reference` and `core.fsyncMethod=fsync`, verified by every Oracle writer before acknowledgment" | Bench has 33 `config.worktree` files with `worktreeConfig=true`; effective `core.fsync` is per-caller, reads empty from both main and worktrees. Reading config proves nothing about writes. | REPLACES: "verified by every Oracle writer before acknowledgment" with "passed as `-c core.fsync=loose-object,pack,reference -c core.fsyncMethod=fsync` on every Oracle git invocation" | PROOF: set `core.fsync=none` in one worktree config; acknowledgment on non-durable write falsifies the check.

§1 | "`refs/oracle/claim/<S>` points to `{subject, owner, lease_gen, claimed_at, ...}`" | Subject IDs unencoded in ref names; bench filesystem case-insensitive with `core.ignorecase=true`; two subjects differing only in case share one ref. | REPLACES: "`refs/oracle/claim/<S>`" with "`refs/oracle/claim/<hex(utf8(S))>`" | PROOF: admit two subjects differing only in case; one ref under `git for-each-ref refs/oracle/claim` after two successful claims proves double-claim violation (Scenario 1).

§4 | "an empty pending ref for every lane in the pinned challenger membership" | "Empty" undefined; PENDING_TRANSFER "empties" without stating deletion. Bench git 2.40 `update-ref --stdin` cannot verify exists-but-empty; only known OID or zero. | REPLACES: "an empty pending ref" with "absence of the pending ref (`verify <ref> 0{40}`); PENDING_TRANSFER deletes rather than empties it" | PROOF: PENDING_TRANSFER writes empty-set blob; adoption's zero-OID verify fails permanently, or verifying blob OID lets concurrent BLOCKING_PUBLISH be dropped.

## Untested

§1 | "A state-ref CAS loss means competing publication: exit 3, release the mutex" | Under §7 singleton with fence L, loss is more likely stale-read; voluntary release plus fresh `t_renew` blocks `--ensure` takeover for 120s. No bench signal.

## Cross-section contradictions

(Lint-Codex lane did not run; no cross-family lint findings available)

## Arbiter losers

(Arbiter lane did-not-run; no rejected findings to record)

## Panel

Dimension means (equal weight):
- Cross-Family Safety: 88.2 ← Design emphasizes safety mechanisms (quorum, epochs, event fences); panel consensus strong
- Autonomy Achievement: 84.6 ← Advisory budgets and bounded waits well-received
- Risk Mitigation: 83.4 ← Scenarios provided; clock domains explicit
- Timeline Realism: 78.6 ← DAG forecasts and gates expected to be executable; some uncertainty on Phase 1 completion
- Contract Completeness: 77.0 ← Luna implementation barrier noted; some sections require clarification
- Throughput Goal: 76.4 ← Reducer capacity model present but P_pub derivation and depth-two pipelining contingent on measurement; not yet proven

Per-seat composites:
- panel-fable (Fable/Claude): 87.67 ← strongest on coherence; contract review found undefined sections
- panel-opus (Opus/Claude): 86.0 ← strong on orchestration and concurrency; reducer capacity model checked
- panel-sonnet3 (Sonnet/Claude): 83.67 ← autonomy lens solid; budget directives honored
- panel-sonnet1 (Sonnet/Claude): 75.17 ← timeline and phase-gate executability concerns; Phase 1 may slip
- panel-sonnet2 (Sonnet/Claude): 74.33 ← concurrency adversary lens; index.lock and shared-worktree hazards flagged

No blocker-level disagreements within 5-seat panel. Spread 13.34 reflects Sonnet variance on timeline risk vs Fable/Opus consensus.

Missing seats (no sentinel):
- panel-astra (Codex): cross-family routing and latch/rotation verification not performed
- panel-sol (Codex): safety gates and quorum/attestation soundness not verified cross-family
- panel-luna (Codex): implementability on Windows shared git not assessed

## Classifier consensus

(Classifier lanes 1-3 did not run; no GROUNDED/STOPPING classification available)

## Provenance

| stage | lane | model | family | rc | bytes | sentinel | notes |
|-------|------|-------|--------|----|----|----------|-------|
| A | design-scope | opus | claude | 0 | 4539 | ✓ RAN | §1-§4 findings + untested identified |
| A | design-verify | (not-run) | claude | 127 | 0 | ✗ | codex exec unavailable |
| A | lint-claude | haiku | claude | 0 | 1979 | ✓ RAN | subject-only linting complete |
| A | lint-codex | luna | codex | 127 | 0 | ✗ | codex exec unavailable |
| B | arbiter | astra | codex | 127 | 0 | ✗ | codex exec unavailable; no arbitration performed |
| B | panel-fable | fable | claude | 0 | 743 | ✓ RAN | 87.67 composite |
| B | panel-opus | opus | claude | 0 | 686 | ✓ RAN | 86.0 composite |
| B | panel-sonnet1 | sonnet | claude | 0 | 642 | ✓ RAN | 75.17 composite (timeline concerns) |
| B | panel-sonnet2 | sonnet | claude | 0 | 696 | ✓ RAN | 74.33 composite (concurrency flagged) |
| B | panel-sonnet3 | sonnet | claude | 0 | 680 | ✓ RAN | 83.67 composite |
| B | panel-astra | astra | codex | 127 | 0 | ✗ | codex exec unavailable |
| B | panel-sol | sol | codex | 127 | 0 | ✗ | codex exec unavailable |
| B | panel-luna | luna | codex | 127 | 0 | ✗ | codex exec unavailable |
| C | consolidator | fable | claude | — | 0 | ✗ | stage C blocked; arbiter did-not-run |
| D | classifier-1 | haiku | claude | — | 0 | ✗ | stage D not reached |
| D | classifier-2 | haiku | claude | — | 0 | ✗ | stage D not reached |
| D | classifier-3 | haiku | claude | — | 0 | ✗ | stage D not reached |

### PARTIAL Posture Summary

Posture is PARTIAL (7/17 lanes) because Codex CLI (`codex exec`) did not respond on this machine at dispatch time (all Codex lanes rc=127, command-not-found). Per lane-orchestrator routing: "One family available → degraded: run what that family can seat."

**What ran (Claude family):**
- ✅ Design scope review (1 lane)
- ✅ Lint consistency review (1 lane, Claude only)
- ✅ Panel evaluation (5/8 seats, all Claude)
- ⏸ Arbiter arbitration (blocked; requires Codex)
- ⏸ Consolidator synthesis (skipped; no arbiter input)
- ⏸ Classifier consensus (skipped; depends on consolidator)

**What did not run (Codex family):**
- ✗ Design-verify (Sol/Codex: verification and adoption slice)
- ✗ Lint-consistency cross-family (Luna/Codex)
- ✗ Arbiter (Astra/Codex: arbitration of panel disagreements)
- ✗ Panel-astra, panel-sol, panel-luna (Codex evaluation seats)

**Cross-family validation: NO** — Only Claude family scored; cross-family lint and Codex design verification absent.

**Remediation path:** Re-run posture once Codex CLI is available on the machine. Current 7-lane Claude-only posture is stable and sufficient for design review within a single family.
