# AirMyPC Multi-Provider Orchestration Schema — v1

**Status:** DRAFT ADOPTED  
**Date:** 2026-09-11  
**Authority:** DECISION [5xx] AirMyPC factory redesign; Logistics route  
**Scope:** Claude (Fable/Opus/Sonnet/Haiku) + Codex (Astra/Sol/Luna); future: Grok, Kimi  

---

## Phase Gates & Progression

| Phase | Packet | Implementer | Reviewer | Gate | Target |
|-------|--------|-------------|----------|------|--------|
| **1** | P05a | Haiku (Claude low) | Sonnet | Baseline established | defect=0, verdict=APPROVE |
| **2** | P05b | Opus (Claude high) | Haiku | Review independence proven | parity_vs_P05a ≥ 0.95 |
| **3** | P05c | Luna (Codex low) | Fable (xhigh) | Multi-provider capability tested | Luna parity vs baseline |

**Measurement every landing:**
- Implementation tokens (input/output)
- Review tokens (input/output)
- Defect count (must be ≤ baseline)
- Review verdict (APPROVE expected)
- Parity vs baseline (0.95–1.05 for same-tier packets)

**Hold gates:**
- P05b: if parity < 0.90 OR defect > P05a, halt
- P05c: gated on P05a+b success; Luna's bounded scope is real test

---

## Failover Protocol (Phase F06, post-P05c)

**Trigger:** Claude >80% cap OR Codex >80% cap → route new packets to other family

**Execution:** RECOVERY_PLAN §4 wrapper (existing infrastructure)

**Doctrine entry:** Failover outcomes published post-P05c

---

## CLI Auto-Update (Concurrent)

**Safe (automatic):** Patch version (1.2.3 → 1.2.4), session-start check, apply only if idle

**Manual review:** Minor (1.2 → 1.3) and major (1.x → 2.x) versions; never mid-session

---

## Doctrine Sync Cadence

**Publish immediately (same hour):**
- Provider matrix updates
- Phase gate results (parity, defect counts)
- Failover trigger outcomes
- Novel patterns (bug class caught by cross-family review)

**Publish post-cycle:**
- Measurement summaries
- Architecture amendments

---

**Next review:** Post-P05c (measurement data available)

Authority: DECISIONS [5xx] AirMyPC + Logistics swarm.
