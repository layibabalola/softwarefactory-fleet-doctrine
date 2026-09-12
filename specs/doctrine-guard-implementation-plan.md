# Doctrine Guard Implementation Plan

**Date:** 2026-09-12  
**Decision Method:** Adversarial Haiku swarm (2-lane consensus)  
**Status:** AUTONOMOUS DECISION MADE — Fable implementation chip authorized

---

## Autonomous Decision (2-Lane Consensus)

### Lane 1: Phase 1 Owner Assignment
**Verdict:** ASSIGN_FABLE_NOW

✅ Owner: Fable executor  
✅ Deployment model: Chip immediate (30-min cadence, real-time feedback)  
✅ Risk mitigation: 3-hour heartbeat renewal + swarm validation per increment  
✅ Authority: Haiku can unilaterally authorize Fable per lane-model policy

**Rationale:**
- Doctrine Guard implementation is pure scripting (spec complete, risk isolated to reconcile-swarm logic)
- Fable's 30-min cycle enables rapid feedback loop—critical for closing algorithm gaps
- DNG team async work loses feedback velocity; Claude orchestrator role prevents direct implementation
- 3-hour silent-freeze rule mitigated by heartbeat renewal + real-time swarm consensus on each 30-min output

### Lane 2: Algorithm Gap Remediation Timing
**Verdict:** STAGED approach

**HIGH-RISK gaps (BEFORE Phase 1):**
- Intent-tag enforcement tightening (currently `explore-alternative` bypasses checks too loosely)
- Pre-push hook MUST validate intent tags before any push reaches remote
- **Blocking point:** Phase 1 implementation launch gates on this validation being in place

**MEDIUM-RISK gaps (AFTER Phase 1 pilot):**
- Scope-overlap detection thresholds (% overlap triggers SWARM_REVIEW?)
- Authority-weight calibration rules (how weights resolve conflicts)
- Tuning approach: Swarm-based (3 independent lanes) adjudicates thresholds from false-positive telemetry
- Applied to `settings.json` post-pilot

**Rationale:**
- Aligns with measured practice: pilot-data-first refinement minimizes fleet deployment risk
- Tight intent-tag validation must precede any push (cannot ship loose bypass to doctrine repo)
- Scope/authority thresholds can be tuned without blocking; data-driven approach post-pilot

**Owner:** Doctrine Guard maintainer (codex lane or volunteer)

---

## Critical Dependencies

1. **3-hour heartbeat renewal** on Fable executor (per hosted-subagent-outlives-its-tick rule)
2. **Swarm validation per 30-min increment** — each Fable output (detect-conflicts.py fragment, reconcile-swarm.py logic, etc.) validated by 2+ independent lanes before merging
3. **Tight CI/CD** — specs published to doctrine repo ONLY after adversarial consensus (no direct Fable push)
4. **Intent-tag validation gate** — pre-push hook must be in place before Phase 1 implementation spreads

---

## Phase 1 Implementation Scope

**Fable will write (4–6 hours total, ~30-min increments):**

1. **detect-conflicts.py** (Layer 1: name collision, Layer 2: scope overlap, Layer 3: verdict contradiction)
   - Swarm validation: 2 lanes review algorithm correctness + edge cases
   
2. **reconcile-swarm.py** (Orchestrate 4–6 agents, consensus logic, verdict rendering)
   - Swarm validation: 1 lane reviews orchestration; 1 lane stress-tests consensus edge cases

3. **git-pre-push-hook.sh** (Main entry point, hook installation, flow control)
   - Swarm validation: 1 lane reviews for bypass vectors; 1 lane tests on synthetic conflicts

4. **build-index.py** (Rebuild doctrine-index.json from specs)
   - Swarm validation: 1 lane reviews; verify index structure against 2+ existing specs

5. **settings.json** (Config: scope-overlap %, authority weights, timeouts, intent-tag rules)
   - Swarm validation: 2 lanes review; ensure HIGH-RISK intent-tag enforcement is non-bypassable

6. **Agent role prompts** (6 files: novelty-analyst, quality-reviewer, scope-complementarian, authority-arbiter, synthesis-designer, risk-assessor)
   - Swarm validation: 1 lane reviews for consistency; 1 lane spot-tests prompt quality on mock conflicts

---

## Execution Order

**Immediate (this session):**
1. ✅ Autonomous decision made (swarm consensus)
2. → Create Fable chip for Phase 1 implementation
3. → Dispatch chip with critical dependencies named

**Phase 1 (Fable, 4–6 hours, ~30-min increments):**
1. Fable writes detect-conflicts.py fragment
2. Swarm validates (2 lanes)
3. Merge to WIP branch
4. **[Repeat for each script/prompt]**
5. Integration test (all scripts together)
6. Fable submits to doctrine repo via adversarial consensus gate

**Parallel (Codex/Doctrine Maintainer, during Phase 1):**
1. Draft HIGH-RISK intent-tag validation rules
2. Specify pre-push hook behavior (reject / prompt for ratification)
3. Prepare settings.json intent-tag section (non-bypassable)

**Phase 2 (Pilot, 2–3 weeks):**
1. Deploy Phase 1 implementation to 3–5 volunteer projects
2. Collect false-positive telemetry
3. Swarm (3 lanes) adjudicates scope/authority thresholds
4. Apply to settings.json
5. Re-test with updated thresholds

**Phase 3 (Fleet Rollout, Week 4+):**
1. Deploy to mandatory when consensus confidence met
2. Document verdict patterns for fleet teams

---

## Authority & Governance

**Decision:** Autonomous (Haiku swarm, 2-lane consensus, no user gate)  
**Executed by:** Fable chip (immediate dispatch)  
**Validated by:** Adversarial swarm per 30-min increment (2+ lanes before merge)  
**Published by:** Doctrine Guard maintainer (consensus gate before repo push)  
**Next review:** Phase 1 completion checkpoint (full integration test pass)

---

## References

- Assessment: `specs/doctrine-guard-integration-strategy.md`
- Spec: `specs/doctrine-guard-conflict-prevention.md`
- Autonomous decision: Haiku swarm (this session, 2026-09-12)
- Lane model policy: [[fable-lane-model-authority]]
- Hosted subagent rule: [[hosted-subagent-outlives-its-tick]]

---

**Status:** AUTONOMOUS DECISION EXECUTED  
**Next:** Fable implementation chip created and dispatched  

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
