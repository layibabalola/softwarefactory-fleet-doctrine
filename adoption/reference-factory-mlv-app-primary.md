# MLV-App as Primary Reference Factory

**Status:** RECOMMENDED  
**Date:** 2026-09-11  
**Authority:** Fleet adjudication (swarm synthesis: Maximalist/Risk Manager/Logistics briefs); AirMyPC multi-provider factory redesign ([5xx] DECISIONS.md)  
**Scope:** All projects choosing factory architecture; foundational topology for process-driven governance

---

## Why MLV-App

**Proven claim:** Process topology collapse measured at scale — 335 commits overhead → 2 commits (heartbeat + ledger-first + pre-commit gates). Product velocity +56% sustained across 2.5 commit/day on dual-lane Codex pair.

**Universal advantage:** Seats are expensive in every factory. MLV-App proves the remedy works across multi-provider, cross-family review, and autonomous production dispatch.

---

## Phased Adoption Path

**Phase 1: Foundation (Day 0)**
- **Heartbeat:** OS-scoped Windows Scheduled Task (10-min snapshot). Survives account rotation. Command: derive board state from `.claude-state/` raw.
- **Ledger-first:** Append-only DECISIONS.md + ledger tail (BOARD.md). No seats, no leases, no state.json polling.
- **Pre-commit gates:** Git hooks on master (repo-global, no seat registration).

**Phase 2: Multi-lane (Day 1–7)**
- **Dual-lane dispatch:** Codex (Sol/Luna) + Claude (Opus/Sonnet). Heartbeat routes work; no seat leases.
- **Process topology:** Scheduled Tasks execute via CLI. Each lane reads board state from heartbeat snapshot; no shared state lock.

**Phase 3: Cross-family review (Day 7+)**
- **Review independence:** Claude reviewers (Opus+Sonnet) blind to Codex implementers (Sol/Luna). One-way glass model (Adobe pattern, see adoption/patterns-adobe-ingester-safety-first.md).

---

## What Ports vs. What Doesn't

**Ports to any factory:**
- Heartbeat pattern (Windows Task, OS-scoped, survives rotation)
- Ledger-first model (append-only truth store, no SQLite/JSON polling)
- Pre-commit gates on master (no seat registration required)
- Process topology (dispatch via CLI, not seat leases)

**Niche (project-specific):**
- Dual-lane Codex pair (MLV-App uses Sol/Luna; single-provider projects skip this)
- Product work on VolumeLabelConverter (domain-specific; mechanism transfers, work doesn't)

---

## Cost Baseline

**Pending P05a Phase 1 measurement** (AirMyPC VolumeLabelConverter, Haiku implementation, Sonnet review):
- Implementation tokens (input/output, Haiku low-tier)
- Review tokens (Sonnet low-high-tier)
- Defect count (must be ≤ baseline to pass Phase 2 gate)
- Parity vs. prior art (must be 0.95–1.05 to unblock Phase 2 Opus re-implementation)

Baseline data will populate this section after 2026-09-11 (Phase 1 complete, expected <24 h).

---

## How to Adopt

1. Start with Phase 1: heartbeat + ledger + pre-commit gates
2. Deploy Windows Scheduled Task (see `tools/Invoke-AudioMileResumeHeartbeat.ps1` pattern in AirMyPC for reference)
3. Wire ledger append (DECISIONS.md or project-local equivalent)
4. Add pre-commit gates (repo-specific, but pattern is portable)
5. Add lanes when ready (Phase 2); maintain heartbeat cadence throughout

---

## Related Patterns

- **Safety-first review layer (Adobe):** see adoption/patterns-adobe-ingester-safety-first.md — use when multi-provider failover or cross-family review required
- **Factory selection decision tree:** see adoption/decision-tree-factory-selection.md — when to choose MLV-App vs. Adobe vs. CloudVore
- **Measurement schema:** see schemas/multi-provider-orchestration-v1.md §2–3 — defect count, review verdict, parity gates

---

**Next review:** Post-P05c (after Luna cross-provider test lands, measurement proof complete)
