# Factory Operation Modes

## Overview

Factory operation modes describe standing patterns of autonomous work in fleet factories. Each mode is:

- **Always on** (no toggle) — improvements don't pause
- **Autonomous** — improvements land via standard gate process (tests green, swarm converge, gates check); no owner ratification required
- **Measurable** — each mode either generates metrics or integrates with quality signals
- **Portable** — same mode applies across Cloudvore, Magic Lantern, and future fleet factories

---

## Active Modes

### Mode: Continuous Validation Improvement

**Introduced:** 2026-09-11 (Cloudvore code quality audit)  
**Status:** Active (all fleet factories)

**Pattern:** Three-phase improvement roadmap for multi-agent review and staged code approval.

**Phases:**
- **Phase 1 (DO NOW):** Pipeline tests + swarm in parallel → saves ~15 min per packet
- **Phase 2 (QUEUE NOW):** Cost-aware model routing by risk tier → 50% token savings on MEDIUM/LOW code
- **Phase 3 (START NOW):** Quality metrics dashboard → baseline capture enables metric-driven tightening
- **Phase 4 (PENDING):** Design-phase model routing → awaiting adjudication

**Authority:** Autonomous implementation via standard gate process. Phase 4 decision-making awaits design-domain adjudication (not owner-blocked).

**Reporting:**
- Weekly metrics summary (Phase 3): escape rate, review velocity, disagreement rate, test flakiness
- Monthly optional review (owner): design-phase decision status

**Documentation:** `doctrine/code-quality-validation-strategy-2026-09.md`

---

## Retired Modes

(None yet — this section documents modes that have been superseded or completed.)

---

## Mode Lifecycle

### Launch Criteria

A mode enters **Active** when:

1. Strategy document published in `doctrine/`
2. Phases approved by adjudication (independent swarm review or owner decision)
3. Implementation plan specified (effort, timeline, success criteria)
4. First phase can merge to master via standard gate process

### Measurement & Reporting

All active modes must:

- Publish metrics or quality signals weekly (if measurable)
- Report mode health to factory dashboard (if metrics exist)
- Flag regressions to ops channel (if Phase 3-equivalent exists)

### Retirement Criteria

A mode moves to **Retired** when:

1. Its final phase completes and is validated on 5+ packets
2. Improvement is baked into default factory behavior (no longer "mode", just policy)
3. Successor mode (if any) is published and approved

---

## Adoption for New Factories

When standing up a new fleet factory:

1. Clone doctrine patterns from this directory (`doctrine/*.md`)
2. Evaluate which active modes apply to your factory's risk profile
3. Activate modes by:
   - Implementing Phase 1 of each mode (usually pipelining or baseline capture)
   - Publishing weekly metrics for measurable modes
   - Routing improvements through standard gate process

---

## See Also

- `doctrine/code-quality-validation-strategy-2026-09.md` — Full strategy for current mode
- `doctrine/pattern-rotation-continuity-2026-09.md` — Related pattern (account rotation without interruption)
