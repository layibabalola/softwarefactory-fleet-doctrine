# Fleet Guide: Three Parallel Consensus Swarm Variants

**Date:** 2026-09-12  
**Authority:** Swarm audit + fleet consensus  
**Status:** GUIDANCE (reference for understanding pattern variants)

---

## Overview

The fleet has three instantiations of the **parallel consensus swarm** pattern, developed independently by different projects. All three describe the same core mechanism (3+ agents, 2+ consensus, independent execution) but emphasize different aspects and roles.

**Core pattern definition:** See `specs/parallel-consensus-swarm.md` (unified mechanism)

---

## The Three Variants

### Variant 1: Role-Based Adversarial (Adobe, Reference)

**Source:** Adobe Document Cloud Ingester (external, non-binding reference)  
**Specification:** Not in our repo (external pattern)  
**Agents:** 3 roles — Pessimist (assume worst), Pragmatist (what works), Innovator (what's possible)  
**Use:** Creative problem-solving, high-stakes decisions, strategic planning  
**Authority:** Informational (not fleet-wide binding)

**Key characteristic:** Roles are deliberately oppositional (each argues from a different position)

---

### Variant 2: Role-Based Autonomous Decision-Making (Conjugal, BINDING)

**Source:** Conjugal CLI Automation Governance (user-authorized, 2026-09-12)  
**Specification:** `specs/autonomous-decision-making-with-adversarial-swarms.md`  
**Agents:** 3 roles — Feasibility (can we build this?), Risk/Security (what breaks?), Pragmatism (what's better in practice?)  
**Use:** Technical trade-offs, code safety, tool selection, architecture decisions  
**Authority:** FLEET-WIDE BINDING (owner-authorized, tested via swarm)  
**Escalation:** 4 cases (deadlock, novel, high-risk, conflicting with user preferences)  
**Failure modes:** Detailed recovery guidance  
**Maturity:** Production-ready

**Key characteristic:** Roles are complementary perspectives (each contributes domain expertise)

---

### Variant 3: Role-Free Autonomous Adjudication (DNG, PROVISIONAL)

**Source:** DNG Auto-Processor (2026-09-12 10:04, pending ratification)  
**Specification:** `specs/parallel-consensus-swarm.md` + `specs/autonomous-swarm-adjudication.md`  
**Agents:** 3+ independent agents (no roles assigned)  
**Use:** Next-step routing, ambiguity resolution, judgment calls  
**Authority:** Provisional (Adopted status, but Ratification: Pending — ambiguous)  
**Escalation:** Minimal (only "no consensus")  
**Failure modes:** Not documented  
**Maturity:** Initial/draft  

**Key characteristic:** Agents are independent (no prescribed perspective); emphasis on redundancy through parallelism

---

## Comparison Matrix

| Criterion | Adobe (Reference) | Conjugal (Binding) | DNG (Provisional) |
|-----------|---|---|---|
| **Source** | External | Internal (Conjugal) | Internal (DNG) |
| **Authority** | Informational | ✓ FLEET-WIDE BINDING | ⚠ Provisional |
| **Status** | Not in repo | IN FORCE | Adopted + Pending (contradictory) |
| **Agents** | 3 (Pessimist, Pragmatist, Innovator) | 3 (Feasibility, Risk, Pragmatism) | 3+ (untyped) |
| **Role assignment** | Prescribed | Prescribed | None |
| **Consensus rule** | 2/3 (implied) | 2/3 | 2/3+ (flexible) |
| **Escalation cases** | Unknown | 4 (detailed) | 1 (minimal) |
| **Failure modes** | Unknown | Documented | Not documented |
| **Maturity** | Mature (used in Adobe) | Production-ready | Initial |
| **When to use** | Creative decisions, strategy | Technical decisions, architecture | Adjudication, routing |

---

## When to Use Each Variant

### Use Variant 1 (Adobe) for:
- High-stakes creative or strategic decisions
- Situations where you want genuine role-based tension (pessimism vs. optimism)
- Non-technical judgment calls
- **Fleet guidance:** Informational reference; not recommended for automation

### Use Variant 2 (Conjugal) for:
- **Technical architecture and design decisions** (Recommended for most lane work)
- Code safety and security reviews
- Tool and library selection
- Trade-off analysis (implementation approach)
- **When:** This is the fleet standard; use this unless your decision is explicitly about next-step routing or ambiguity

### Use Variant 3 (DNG) for:
- Next-step adjudication (what should we do next?)
- Resolving ambiguity in queued work
- Judgment calls about task routing or priority
- **When:** Only after DNG fixes the Adopted/Pending contradiction; requires ratification

---

## Fleet Recommendation

### Immediate (No change needed):
✅ Use Variant 2 (Conjugal) as fleet-wide standard for technical decisions  
✅ Reference Variant 1 (Adobe) as inspiration for role-based approaches  
✅ No lanes should depend on Variant 3 until status is clarified

### Before DNG's Pattern Goes Fleet-Wide:

**DNG must resolve:**
1. **Status contradiction:** Clarify whether spec is:
   - ✓ ADOPTED (binding now, ratification pending only for documentation)
   - or ✓ DRAFT (provisional, ratification required before fleet-wide adoption)
   - **NOT both**

2. **Add escalation rules:** Incorporate Conjugal's 4 escalation cases

3. **Add failure-mode guidance:** Document what to do if swarm consensus was wrong

4. **Clarify scope:** When should a lane use DNG's adjudication variant vs. Conjugal's technical decision variant?

---

## Cross-Project Coordination

**Timeline:**
- **2026-09-12:** Conjugal publishes Variant 2 (Binding)
- **2026-09-12:** DNG publishes Variant 3 (Provisional)
- **2026-09-12:** Audit recommends three-variant framework (this doc)
- **2026-09-13 (target):** DNG clarifies ratification status
- **2026-09-14+:** Once status is clear, Variant 3 can be adopted fleet-wide or remain experimental

**Risk:** Lanes may adopt Variant 3 before status is clarified, then discover ratification was rejected → wasted work, confused audit trail.

---

## Authority and Consensus

**Why three variants exist:**
- **Adobe pattern:** Developed independently (external, not fleet-wide)
- **Conjugal pattern:** Hardened via swarm audit (security review, race condition audit, fleet compatibility)
- **DNG pattern:** Published same day as Conjugal; represents independent parallel development

**Why they're compatible:**
- Core mechanism is identical (3+ agents, 2/3 consensus, independent execution)
- Different scopes (decision types) are complementary
- No contradictory guidance

**Why consolidation isn't needed:**
- Scope differences are intentional and valuable
- Separate docs allow targeted reference
- Cross-refs prevent confusion

---

## Implementation Guidance

### For lanes starting now:
```
if decision_type == "technical" or "architecture" or "code_safety":
  use Variant 2 (Conjugal)  # Fleet-wide standard
elif decision_type == "next_step" or "adjudication":
  wait for DNG ratification  # Variant 3 is provisional
  or implement manually    # Don't depend on Variant 3 until ratified
else:
  use Variant 2 (default)   # Safe default
```

### For new patterns:
```
if proposing new swarm pattern:
  1. Check Variant 2 escalation/authority limits
  2. Explain how your pattern differs
  3. Get swarm consensus before fleet proposal
  4. Cross-ref with existing patterns
```

---

## FAQ

**Q: Should I use Adobe's pattern?**  
A: Only if you explicitly want role-based tension (pessimism vs. optimism). For technical decisions, use Conjugal's Variant 2.

**Q: Can I mix Variant 2 and Variant 3 in the same decision?**  
A: Not recommended. Use Variant 2 for the technical layer, then if you need adjudication on next steps, use Variant 3. Don't nest them.

**Q: What if DNG's status isn't clarified by [date]?**  
A: Assume Variant 3 remains experimental. Lanes should not depend on it for production decisions until status is unambiguous.

**Q: Can I create a Variant 4?**  
A: Yes, but only after proving via swarm consensus (using Variant 2) that it's necessary and safe. Publish to doctrine repo with ratification metadata.

---

## References

- `specs/parallel-consensus-swarm.md` — Core pattern definition (unified mechanism)
- `specs/autonomous-decision-making-with-adversarial-swarms.md` — Variant 2 (Conjugal, role-based, BINDING)
- `specs/autonomous-swarm-adjudication.md` — Variant 3 (DNG, role-free, Provisional)
- `specs/autonomous-swarms-and-doctrine-publishing-standard.md` — (External reference, ratification metadata)

---

## Revision History

- **2026-09-12 v1.0**: Initial three-variant guide (swarm audit finding)
  - Discovered parallel development of similar patterns
  - Documented compatibility and complementarity
  - Recommended status clarification for Variant 3
