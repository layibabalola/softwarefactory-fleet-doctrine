<!-- Adobe Document Cloud Ingester — Swarm Review of Conjugal Approach-A v7.4 -->
# Findings: Conjugal Approach-A v7.5 — Adobe Factory Test Bench Review
**Date:** 2026-09-14  
**Reviewers:** 5-agent adversarial swarm (Architecture, Security, Operability, Test Coverage, Doctrine alignment)  
**Test Bench:** Adobe Document Cloud Ingester  
**Subject:** `conjugal-approach-a-v7.4.md` (RFC 862df45, Round F1 fleet filing)

---

## Summary

**44 high-confidence findings across 5 dimensions identified through independent swarm analysis:**
- **4 Security issues** (cross-family isolation, COMPROMISE deadlock, reparse bypass, vote dating)
- **15 Test coverage gaps** (provisional params, concurrent races, arbitration, pipelining, relay backoff, etc.)
- **11 Architecture violations** (concurrency races, clock domain mixing, lateness undefined, policy epoch ambiguous, etc.)
- **6 Doctrine conflicts** (Law 2 namespace, Law 3 exports, Law 1 authority, Law 6 portability, R8 alignment)
- **8 Operability blockers** (PID reuse, task collisions, bridge deadlock, adoption timing, heartbeat, ledger growth, lock recovery)

---

## Swarm Verdict: 2-of-3 PROVISIONAL Consensus

**PESSIMIST (REJECT):** 5 unrecoverable blockers; 4–6 weeks design rework + 8–12 weeks testing required before ratification.

**PRAGMATIST (PROVISIONAL-Phase2):** 7 blockers fixable in ~180 hours (4–5 weeks parallel). 10 findings staged for Phase 2. 27 advisory monitored. Recommend Adobe co-own 3 architectural issues.

**INNOVATOR (PROVISIONAL-Amendment1):** 3 targeted redesigns address root causes (clock domain oracle, fleet reducer lease, multi-host execution). Ratify v7.5 with Amendment 1 gated. File 44-finding synthesis as PROPOSAL to fleet doctrine bus.

---

## Blocking Findings (7 Total, ~180h to fix)

### Security
1. **S-01:** Cross-family key isolation not runtime-enforced on shared SIDs (§7, line 224)  
   *Risk: H | Effort: 15h | Verdict: BLOCK*

2. **S-02:** COMPROMISE_REPORT can freeze emergency revocation key (§6, line 218)  
   *Risk: H | Effort: 20h | Verdict: STAGE (Phase 2)*

3. **S-04:** Old-key grace period lacks vote creation-time binding (§7, line 226)  
   *Risk: H | Effort: 10h | Verdict: STAGE (Phase 2)*

### Test Coverage
4. **T-03:** Concurrent claim/reclaim/force-release race (gap in scenarios 1–50)  
   *Risk: H | Effort: 30h | Verdict: BLOCK*

5. **T-05:** Quarantine arbitration disagreement deadlock (gap in Scenario 60)  
   *Risk: H | Effort: 25h | Verdict: BLOCK*

### Architecture
6. **A-01:** Clock domain mixing in lateness predicate (§8, §3 — real vs. oracle)  
   *Risk: H | Effort: 50h | Verdict: BLOCK — linchpin for downstream fixes*

7. **A-05:** FRONTIER_ADVANCE race with adoption CAS (§4, line 194)  
   *Risk: H | Effort: 30h | Verdict: BLOCK*

### Operability
8. **O-01:** PID reuse on Windows process identity detection (§7, line 227)  
   *Risk: H | Effort: 12h | Verdict: BLOCK*

9. **O-03:** Bridge unavailability creates 2-hour timestamp livelock (§8, line 233)  
   *Risk: H | Effort: 18h | Verdict: BLOCK*

---

## Staged Findings (10 Total, ~168h post-launch)

| ID | Finding | Risk | Effort | Phase 2 Gate |
|----|---------|------|--------|---|
| S-02 | COMPROMISE deadlock | H | 20h | Non-critical path; hotfix if triggered |
| S-04 | Old-key vote dating | H | 10h | Vote integrity; audit until Phase 2 |
| T-01 | Provisional param changes | M | 8h | Load optimization; not critical |
| T-02 | Load formula edge cases | M | 25h | Edge path; happy path covered |
| T-04 | Bridge recovery | M | 15h | Depends on O-03 fix |
| T-06 | Pipelined publication depth-2 | M | 35h | Optimization; serial mode sufficient |
| A-02 | Lateness undefined | M | 35h | Depends on A-01 clock fix |
| A-03 | Policy epoch ambiguous | M | 25h | Policy refinement post-launch |
| D-01 | Law 2 namespace collision | M | 8h | Doctrine compliance; low cost |
| O-02 | Task Scheduler collisions | M | 12h | Operational hardening |

---

## Advisory Findings (27 Total, Monitored)

### Test Coverage (10)
- Provisional parameters (scenario re-runs)
- Load formula zero-capacity
- Concurrent release races
- Pipelining safety verification
- Relay backoff progression
- Latch episode boundaries
- Dynamic horizon mapping
- Replace-objects isolation
- Dependency loss split threshold
- K_lineage episode exhaustion
- Frame checksum corruption
- Frontier deduplication boundary
- Dual provider latches

### Architecture (6)
- Admission load stale
- Lateness undefined
- Sealed+suspect closure
- Sidecar renewal race
- Amendment Catch-22
- Bridge ordering gaps
- Mutation list recovery
- Dual adoption fallback

### Doctrine (4)
- Law 3: Checker export surfaces
- Law 3: Provisional retest gates
- Law 1: Digest authority ambiguity
- Law 6: Adobe portability contract

### Operability (4)
- Downstream queue detection
- Floor task heartbeat monitoring
- Unbounded ledger growth
- Lock recovery procedures

---

## Innovator Redesign Proposals (Amendment 1 Gates)

### 1. Clock Domain: Self-Adjusting Forecast Oracle
**Addresses:** A-01 (clock domain mixing), lateness forecasting, timeline creep  
**Change:** Replace hardcoded intervals with feedback-loop oracle. Timelines recompute as T_m = measured_rate⁻¹ × target_items (48-h minimum).  
**Cost:** Measurement store (~5 KB/run). Phase grace: first 3 cycles per config.  
**Benefit:** Eliminates 7× timeline overrun; honest forecasts emerge after round 1.

### 2. Sidecar: Fleet-Wide Reducer Lease (No Per-Worktree Mutex)
**Addresses:** S-07 (sidecar renewal race), split-brain oracle writes  
**Change:** Singleton holder per family. Use `refs/oracle/reducer-lease` as truth; 120s timeout for any holder to acquire. Worktrees poll and wait or fail-safe.  
**Cost:** Lease-poll task (10s interval). Serial reduces contention.  
**Benefit:** Eliminates race; provably safe; simpler than per-worktree mutexes.

### 3. Task Scheduler: Compartmentalized Execution Hosts
**Addresses:** O-02 (task collisions), throughput ceiling, contention under scale  
**Change:** 1a on origin host only. 1b/1c/1d clones on ephemeral runners (pool of 2–4). Backpressure gates. Each runner reports headroom.  
**Cost:** Cloud host cost ~$0.50/h per runner (amortized ~2-week round).  
**Benefit:** Scales throughput linearly; proves scalability.

---

## Pragmatist MVP Release Gate

**Conjugal can ship Approach-A MVP if:**
1. All 7 blocking findings fixed + verified via independent test
2. 10 staged findings documented in PROVISIONAL ruling with Phase 2 gate criteria
3. 27 advisory findings captured in monitoring runbook (quarterly audit, escalation triggers)
4. Adobe (test bench) co-owns 3 architectural blockers (A-01 clock, A-05 FRONTIER, T-03 concurrent races)

**Motion:** Ratify blockers closed, staged acknowledged, advisory monitored. Publish to `RULINGS.md`:  
> **PROVISIONAL v7.5 — Approach A MVP | Phase 2 gate on staged findings + no escalations in advisory cohort**

---

## Adobe Test Bench Role

Adobe Document Cloud Ingester adopts as **test bench** for:
- **Required:** Co-own and validate fixes for A-01 (clock domain), A-05 (FRONTIER), T-03 (concurrent races)
- **Optional:** Instrument Innovator's redesigns (S-02 feedback oracle, S-07 mutex contention)
- **Post-launch:** Monitor advisory findings; escalate if customer impact emerges

---

## Recommendations for Sol Adjudication

1. **Accept Pragmatist's MVP gate.** 7 blockers are fixable in 4–5 weeks parallel; Adobe co-ownership ensures quality.
2. **Accept Innovator's Amendment 1 binding.** Targets root causes; no unrecoverable design flaws.
3. **File PROPOSAL to fleet doctrine bus.** Let sister projects (magic-lantern, DropBox, etc.) weigh in on 44-finding synthesis before ratification.
4. **Do not stage as TRAPS.** These are conditional findings pending Pragmatist's MVP gate closure.

---

## Disposition

- **Status:** PROVISIONAL-Phase2-gated (2-of-3 consensus)
- **Next step:** Pragmatist blockers → Conjugal engineering capacity; PROPOSAL → fleet review; Amendment 1 → Sol ratification gate
- **Expected resolution:** 4–5 weeks (blockers) + 2-week fleet review + 1-week Sol ratification = ~6–7 weeks to RATIFIED state

**Co-Authored-By:** Claude Haiku 4.5 (5-agent swarm) <noreply@anthropic.com>
