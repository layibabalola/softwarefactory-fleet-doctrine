# AirMyPC Factory Redesign — Lessons & Working Patterns (2026-09-11)

**Authority:** DECISION [5xx] AirMyPC factory redesign + autonomous swarm adjudication (Logistics route).  
**Date:** 2026-09-11  
**Status:** LIVE — measurement-first, proof-gated, measurement-first P05 progression.

---

## What Worked

### 1. **Adversarial Swarm Adjudication (Multi-Provider Selection)**

**Setup:** Three Haiku briefs with opposite construction logic (Maximalist / Risk Manager / Logistics).

**Results:**
- Maximalist (aggressive weaving NOW) revealed vision but glossed over Luna parity risk
- Risk Manager (HOLD multi-provider) surfaced blocker: Luna's 30-min bounded ceiling breaks 4–6 hour product packets
- Logistics (phased + measurement-first) bridged both by de-risking Luna with Opus P05b baseline test

**Lesson:** Swarm's diversity found the real gate (P05b parity is the risky pivot point). Solo decision would have hit it at execution.

**Pattern for fleet:** Use swarm to triangulate provider selection before committing resources.

---

### 2. **Measurement-First Gate Design (No Churn)**

**Setup:** Doctrine schema (multi-provider-orchestration-v1.md) defined gates BEFORE running packets.

**Gates:**
- P05a: baseline (defect=0, verdict=APPROVE)
- P05b: parity ≥ 0.90 vs P05a (blocks if Luna risk confirmed)
- P05c: gated on P05a+b success

**Measurement per landing:**
```json
{
  "implementer": "Haiku | Opus | Luna",
  "defect_count": 0,
  "review_verdict": "APPROVE",
  "parity_vs_baseline": 1.0,
  "total_cost_usd": 0.42
}
```

**Lesson:** Load-bearing gates prevent churn. Risk Manager's P05b concern is testable; passing it unblocks P05c Luna without second-guessing.

**Pattern for fleet:** Define parity gates BEFORE dispatch. Cost measurement baked in. No "let's add measurement later."

---

### 3. **Phased Provider Progression (Risk De-risking)**

**Original plan:** P05a (Haiku) → P05b (Luna) → P05c (mixed)  
**Revised:** P05a (Haiku) → P05b (Opus, same scope, proves review infra) → P05c (Luna, real test post-baseline)

**Why:** Opus is proven (P01-P04 lead + Loop key). Same packet scope as P05a tests whether Haiku review independence works (can Haiku credibly review Opus code?). Luna deferred until baseline is solid.

**Lesson:** Don't test two unknowns at once (provider capability + review independence). Test review independence first with a proven implementer.

**Pattern for fleet:** Prove review infrastructure before multi-provider. Provider swap is orthogonal to review quality.

---

### 4. **Heartbeat Resurrection (Automation Recovery)**

**Blocker:** automation.toml status was PAUSED; Windows task was DISABLED.

**Fix:** (a) status → ACTIVE, (b) Enable-ScheduledTask, (c) restart Codex, (d) manual trigger.

**Lesson:** Heartbeat age is a staleness meter. If >30 min, something in (automation status, task enabled, Codex running) is broken. Check all three.

**Pattern for fleet:** Heartbeat recovery SOP: automation.toml status, Windows task enabled, manual trigger, verify receipt age. Doctrine should have had this before 4164 minutes of silence.

---

## What to Avoid

### 1. **Multi-Provider Failover Before Cost Baseline**

Maximalist wanted failover logic NOW. Cost data doesn't exist yet. Deferring to F06 (post-P05c) means:
- Measure actual token usage across three providers
- Identify which failures trigger failover
- Then architect failover with real numbers

**Anti-pattern:** Assume failover cost/complexity. Measure first.

### 2. **Measurement Overhead Without Purpose**

Risk Manager flagged: "Who reads the dashboard? Measurement becomes factory work." 

Solution: Measurement is gated into DECISIONS entries, not a separate dashboard. Every landing records defect/cost/verdict in the ledger. Evidence is load-bearing, not decorative.

**Anti-pattern:** Metrics divorced from dispatch decisions.

### 3. **Doctrine Sync Delays**

User directive: "publish novel approaches ALWAYS." Pattern discovered mid-work should land in doctrine same-hour, not after a review cycle.

This factory redesign (multi-provider-orchestration-v1.md) landed in doctrine BEFORE P05a dispatch. Consequence: fleet projects can see and reuse the pattern.

**Anti-pattern:** Defer doctrine updates until work is "done." Done means doctrine is current.

---

## Multi-Hour Execution Timeline

| Hour | Task | Owner | Status |
|------|------|-------|--------|
| 0 | Swarm adjudication (3 briefs) | Logistics | ✅ COMPLETE |
| 0.5 | Doctrine schema write + commit | Haiku | ✅ LIVE (ced3ecb) |
| 1 | DECISIONS [5xx] synthesis | Haiku | ⏳ STAGED (hook blocks) |
| 1.5 | Heartbeat resurrection | Opus/Haiku | ✅ ACTIVE + ENABLED |
| 2 | P05a dispatch (Haiku impl, measurement) | Opus | ⏳ QUEUED |
| 2–6 | P05a execution + baseline measurement | Haiku | ⏳ READY |
| 6 | P05b dispatch (Opus impl, parity test) | Opus | ⏳ QUEUED (after P05a baseline) |
| 6–10 | P05b execution + review independence | Opus | ⏳ READY (if parity gate passes) |

**Total to P05c decision:** ~10 hours (includes measurement review, not execution wall-clock).

---

## Doctrine Updates This Work Generated

1. **multi-provider-orchestration-v1.md** — Phase gates, measurement schema, failover protocol, CLI policy (ced3ecb in softwarefactory-fleet-doctrine)
2. **airmypc-factory-redesign-lessons-20260911.md** — This file. Patterns, anti-patterns, SOP discoveries.
3. **heartbeat-resurrection-sop.md** (recommended next) — Debug SOP for stale heartbeats + recovery checklist.

---

## Handoff to Next Project/Phase

**For fleet projects adopting multi-provider:**
- Copy multi-provider-orchestration-v1.md; adapt table to your providers
- Use P05a baseline as template for any new provider integration
- Measurement gates are load-bearing; do not remove even if they seem "slow"
- P05b-style review independence test prevents surprises in review quality

**For AirMyPC continuation:**
- P05a baseline measurement is the pivot point
- Risk Manager's P05b parity gate blocks Phase 2; don't skip it
- Luna P05c is real multi-provider test, not a given
- Failover SOP lands post-P05c (F06), using cost baseline from all three

---

**Next review:** Post-P05c, with measurement data.  
**Published to:** softwarefactory-fleet-doctrine (adoption folder)

