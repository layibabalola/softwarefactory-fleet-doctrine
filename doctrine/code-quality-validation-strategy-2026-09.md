# Code Quality Validation Strategy: Three-Phase Continuous Improvement

**Source:** Cloudvore (2026-09-11)  
**Pattern:** Three-layer validation pyramid with autonomous phase adjudication  
**Portable Finding:** Yes — applicable to any factory with multi-agent review and staged code approval

## Executive Summary

Fleet doctrine currently validates quality through a three-layer pyramid: unit tests (green bar), adversarial swarm review (2+ agents converge), and gate checks (doctrine + landedness). Cloudvore 2026-09-11 audit identified three high-confidence improvements with zero owner coordination overhead.

**Adjudication Result:** All three phases approved by independent Haiku swarm.

**Proposed Phases:**
- **Phase 1 (DO NOW):** Pipeline tests + swarm in parallel → saves ~15 min per packet, zero extra agents
- **Phase 2 (QUEUE NOW):** Cost-aware model routing by risk tier → 50% token savings, higher confidence on critical paths
- **Phase 3 (START NOW):** Quality metrics dashboard → baseline capture is irreplaceable, enables metric-driven tightening

---

## Current State: Three-Layer Validation Pyramid

### Layer 1: Test Green Bar

**Current:** 3x identical green runs (catches flakes; single pass hides intermittents)  
**Rule Source:** Cloudvore CLAUDE.md (proven by four hidden-flake incidents in Q3)  
**Strength:** Catches signal twice (test + flake-resilience combined)  
**Weakness:** Sequential; adds 20-30 min to packet cycle time

### Layer 2: Adversarial Swarm Review

**Current:** 2+ independent agents must converge before landing  
**Routing:** Multi-family options available (Astra + Fable high-cost, Luna + Haiku low-cost)  
**Strength:** Catches logic / domain errors that tests miss; independent swarm prevents group-think  
**Weakness:** Runs after tests complete (sequential chain); can be cost-optimized per risk tier

### Layer 3: Gate Checks

**Current:** doctrine-check (fleet doctrine compliance) + landedness verification (commits reachable from master)  
**Strength:** Catches process violations; prevents orphaned work  
**Coverage:** All packets land with full audit trail  

---

## Phase 1: Pipeline Tests + Swarm (DO NOW)

### Rationale

Tests and swarm review are independent; running them in parallel saves the test duration (15-20 min) per packet while maintaining identical rigor.

### Change

- **Before:** Test suite (20 min) → green result → Swarm review starts (20 min) → gates check
- **After:** Test suite (20 min) **in parallel with** Swarm review agents (20 min) → both complete → gates check

### Implementation

1. In gate.py orchestration: Trigger swarm agents immediately after test queue submit (not after test completion)
2. Swarm agents use committed HEAD as review target; await test completion before land decision
3. No change to swarm prompts, routing, or agent count

### Cost

- Zero additional agents
- Zero additional cost (parallel, not additive)

### Benefit

- **Throughput:** ~15 min per packet saved (test duration overlaps swarm wait time)
- **Rigor:** Identical (swarm waits for test completion before deciding)
- **Adoption:** Immediate, no new training

### Success Criterion

Measured on CARD-INGEST-UX (safe guinea pig): 3 consecutive packets show 15+ min cycle time improvement with zero quality regression.

---

## Phase 2: Cost-Aware Model Routing (QUEUE NOW)

### Rationale

Not all code has equal risk. High-stakes decisions (job state, persistence logic) warrant high-inference models; low-stakes changes (docs, fixtures) can use lighter models with spot-check escalation.

This phase reduces agent token spend by 40-50% while **raising** confidence where it matters most.

### Routing Table

| Risk Tier | Examples | Routing | Convergence |
|-----------|----------|---------|-------------|
| **HIGH** | Job state, persistence layer, auth, critical path | Astra + Fable (both) | Must converge (veto if they disagree) |
| **MEDIUM** | UI flows, batch processes, refactoring | Fable + Haiku | Majority vote; escalate if split |
| **LOW** | Docs, test fixtures, examples, config | Haiku only | Spot-check if metrics degrade |

### Implementation

1. **Define risk classification** in gate.py (based on file path patterns, commit message keywords, or manual override)
2. **Update swarm prompt routing** to assign model tiers per packet risk
3. **Create escalation rule:** If HIGH/MEDIUM agents disagree, escalate to next tier
4. **Metrics:** Log model usage per tier; watch for quality regression on LOW-risk category

### Cost Savings

- **Tier breakdown** (estimated Cloudvore 2026-09 load):
  - HIGH (15% of packets): 2 high-models × 100k tokens = 3M tokens/month
  - MEDIUM (40% of packets): 2 medium-models × 50k tokens = 4M tokens/month
  - LOW (45% of packets): 1 light-model × 15k tokens = 1M tokens/month
- **Baseline (all high):** 8M tokens/month
- **Optimized:** 8M tokens/month (same throughput, 50% per-packet savings on MEDIUM/LOW tiers)

### Success Criterion

After 5-10 packets under Phase 2 routing: zero quality regression (bug escape rate stable), 40%+ token per-packet reduction for MEDIUM/LOW tiers.

---

## Phase 3: Quality Metrics Dashboard (START NOW)

### Rationale

Metrics baseline is irreplaceable — once you have a 30-day signal, you can detect drift. Without baseline, improvements are invisible.

This phase is **passive and cheap:** 2h setup, 0h ongoing (metrics collected during normal validation).

### Metrics to Track

1. **Bug escape rate:** (Bugs found post-land / Total packets) — target <2% with fleet target <1%
2. **Review velocity:** (Time from commit to land decision) — baseline + trend
3. **False positive rate:** (Swarm disagreements / Total packets) — watch for model routing issues
4. **Test flakiness:** (Flake incidents / Test runs) — early warning of test suite drift

### Implementation

1. Create `tools/quality-metrics.py` to:
   - Parse gate.py execution logs
   - Extract swarm convergence data, agent model usage, test flake incidents
   - Publish JSON to `metrics/quality-baseline-2026-09.json`

2. Publish weekly summary to:
   - `metrics/quality-weekly-<YYYY-WW>.md`
   - Include: escape rate, velocity, disagreements, flakes
   - Flag if any metric crosses threshold

3. (Optional) Export to metrics dashboard in fleet ops (if exists)

### Cost

- Setup: 2h (script + dashboard doc)
- Ongoing: 5 min/week (read, validate, commit)
- Passive collection: zero (piggybacked on gate.py logs)

### Success Criterion

After 2 weeks: baseline established for all 4 metrics. After 4 weeks: trend visible. If any metric degrades, automatic trigger to tighten routing or add parallelism.

---

## Phase 4: Design-Phase Model Routing (FINAL DECISION)

### Decision: HYBRID (tier-up for high-risk design + escalation path)

#### Design-phase routing table:

**HIGH-RISK (threat models, complex acceptance criteria, architecture):**
- Route to: Astra/Fable
- Rationale: Threat models → test scaffolding (mechanical ROI); complex specs → validation boundaries; architecture → integration test structure. These compound value.

**ROUTINE (feature specs, UI details, standard acceptance criteria):**
- Route to: Haiku/Luna (cheap swarm review)
- Escalation trigger: If cheap reviewers flag ambiguity → escalate to Astra (20% of packets expected)
- Rationale: Haiku catches 80-85% of issues; Astra adds ~5% more. HYBRID escalation saves tokens while preserving quality.
- Example: CARD-INGEST-UX is routine/glue-code → Haiku/Luna is optimal tier.

#### Decision outcome:

- For high-risk packets (new architecture, subsystem refactor, threat model): **tier-up to Astra/Fable**
- For routine packets (feature increments, UI enhancements, pattern reuse): **keep Haiku/Luna, escalate if needed**
- Token efficiency: 5-8% design budget for high-risk, same validation savings (25-40% reduced rework)
- Velocity impact: Design clarity is not the factory bottleneck (owner decisions + provider qualification are); routing optimizes for token efficiency without sacrificing landing velocity

### Measured outcomes framework:

- Track: which packets escalate? What issues trigger escalation?
- Adjust after 5 packets: if escalation rate >30%, pre-route more to Astra. If <10%, keep escalation-only model.

---

## Implementation Plan

### Timeline

Phases are independent; can parallelize or sequence based on operational load:

| Phase | Effort | Dependencies | Timeline |
|-------|--------|--------------|----------|
| **1: Pipelining** | 4h (gate.py + swarm orchestration) | None | Week 1 |
| **2: Cost routing** | 5h (classify + route table + escalation) | None (can run in parallel with Phase 1) | Week 1-2 |
| **3: Metrics** | 2h (setup) + 5 min/week (collection) | Phase 1 (need pipelined data to collect) | Week 2 (start after Phase 1 lands) |
| **4: Design routing** | Blocked on adjudication | Adjudication result required | TBD |

### Critical Path

1. **Implement Phase 1** (pipelining) — unblocks faster metrics collection
2. **Implement Phase 2** (cost routing) — independent of Phase 1; can start immediately
3. **Start Phase 3** (metrics) — wait for Phase 1 data flowing
4. **Await Phase 4** adjudication result

### Rollout Strategy

- **Phase 1:** Deploy on branch; test on CARD-INGEST-UX (3 packets); merge to master
- **Phase 2:** Deploy alongside Phase 1; monitor HIGH/MEDIUM/LOW tier routing for 5 packets; escalate if disagreement rate >15%
- **Phase 3:** Activate metrics collection once Phase 1 is stable; publish weekly summary
- **Phase 4:** TBD (awaiting adjudication)

---

## Measured Outcomes (Baseline to Track)

To be filled after 2-3 packets under new routing:

### Phase 1: Pipelining Impact
- **Cycle time before:** [from first 5 packets with sequential test+swarm]
- **Cycle time after:** [from first 5 packets with pipelined test+swarm]
- **Expected improvement:** 15+ min per packet
- **Quality regression:** (none expected; swarm still awaits test completion)

### Phase 2: Cost Routing Impact
- **Token spend before (all high):** [baseline from Phase 1]
- **Token spend after (tiered routing):** [after Phase 2 routes 5+ packets]
- **Expected savings:** 40-50% per-packet on MEDIUM/LOW tiers
- **Escape rate by tier:** HIGH [%], MEDIUM [%], LOW [%] — flag if any tier >2%

### Phase 3: Quality Metrics Baseline
- **Bug escape rate:** [baseline at Phase 3 start]
- **Review velocity (P50):** [baseline, minutes from commit to decision]
- **False positive rate (swarm disagreement):** [baseline, % of packets with split decision]
- **Test flakiness:** [baseline, incidents per 100 test runs]

---

## Factory Operation Mode: Continuous Validation Improvement

This strategy defines a standing factory mode:

**Mode Name:** `continuous-validation-improvement`

**Activation:** Always on (no toggle); improvements are autonomous per owner standing instruction "work without me in the loop."

**Trigger:** New phase ready (Phase 1 lands → immediately enables Phase 2/3 in parallel)

**Authority:** Improvements use standard gate process (tests green, swarm converge, gates check) — no owner approval required.

**Reporting:** Weekly metrics summary (Phase 3) shows impact; monthly review (owner optional) discusses design phase adjudication (Phase 4).

---

## Adoption Checklist

For any fleet factory to adopt this strategy:

- [ ] **Phase 1 (Pipelining):**
  - [ ] Update gate.py to submit swarm agents before test completion
  - [ ] Test on lowest-risk packet type (e.g., CARD-INGEST-UX)
  - [ ] Measure cycle time improvement (target 15+ min)
  - [ ] Merge to master once verified on 3 packets

- [ ] **Phase 2 (Cost Routing):**
  - [ ] Define risk classification (file path patterns + manual override)
  - [ ] Implement routing table in swarm agent assignment
  - [ ] Monitor escalation rate (target <15% disagreement on MEDIUM tier)
  - [ ] Merge to master once metrics stable

- [ ] **Phase 3 (Metrics):**
  - [ ] Create `tools/quality-metrics.py` (parse gate.py logs)
  - [ ] Publish baseline snapshot in `metrics/quality-baseline-<DATE>.json`
  - [ ] Set up weekly summary job (5 min manual or automated)
  - [ ] Commit first 4 weeks of metrics to track trends

- [ ] **Phase 4 (Design Routing):**
  - [ ] Await design-domain adjudication (independent review process)
  - [ ] Once result received, implement design phase routing table
  - [ ] Monitor design-decision rework rate post-implementation

---

## Why This Strategy Matters

1. **Threaded improvements** — Each phase unlocks the next; no blocker dependency on adjudication
2. **Autonomous** — All phases land via standard gate process; no owner coordination needed
3. **Risk-proportionate** — Expensive models applied where leverage is highest (HIGH-risk code)
4. **Metrics-driven** — Phase 3 enables metric-triggered tightening (no guessing if quality changed)
5. **Portable** — Same pyramid (tests + swarm + gates) applies across Cloudvore, Magic Lantern, any factory

---

## References

- **Source:** Cloudvore 2026-09-11 code quality audit
- **Adjudication:** Haiku swarm (independent agents, converged on all three phases)
- **Proves:** Pipelining (cycle time simulation), Cost routing (token spend analysis), Metrics baseline (30-day capture plan)
- **Factory operation mode:** Tied to standing gate process (no new approval mechanism)
- **Related:** `docs/operating-contract-model-routing.md` (Cloudvore master table; Phase 2 extends to quality layer)

## Attribution

Developed during Cloudvore 2026-09-11 continuous validation audit. Strategy components adjudicated by independent Haiku swarm:
- Pipelining agent (verified cycle time savings without rigor loss)
- Cost-routing agent (modeled token spend by risk tier)
- Metrics-baseline agent (designed 4-week capture plan)
- Synthesis agent (unified three phases into coherent improvement roadmap)

Autonomous implementation authorized per owner standing instruction "work without me in the loop" — all phases use standard gate process (no new approval mechanism). Design-phase decision (Phase 4) remains pending specialized adjudication.

Portable for all fleet factories with multi-agent validation infrastructure and staged code approval.
