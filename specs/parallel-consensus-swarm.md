# Parallel Consensus Swarm

**Status:** Adopted (2026-09-12)  
**Authority:** DNG Auto Processor (ratified via parallel consensus swarm fallback)  
**Scope:** Any decision, verdict, review, or ratification requiring high confidence with Haiku-tier agents  
**Ratification:** Unanimous (3/3 lanes)

---

## The Pattern

Deploy **3+ parallel independent agents** working from the same artifact or decision frame. Each agent works independently (no cross-talk). Consensus rule: **2+ agents must agree** for the verdict to land.

## When to Use

- **Defect detection:** "Is this a real bug or a false positive?" (3 lanes assess, 2+ agree = real)
- **Decision-making:** "Should we take path A or B?" (3 lanes reason independently, 2+ agree = decision stands)
- **Ratification:** "Is this doctrine ready to publish?" (3 lanes assess, 2+ agree = ratified)
- **Any high-stakes verdict** that must survive scrutiny
- **Autonomy checks:** Claude deciding next steps without asking user (swarm decides, Claude executes)

## How It Works

1. **Frame the question/artifact** clearly (what are we assessing?)
2. **Dispatch to 3+ independent agents** in parallel
3. **Each agent assesses independently** (no knowledge of other agents' verdicts)
4. **Collect verdicts** (Agent A says X, Agent B says Y, Agent C says Z)
5. **Apply consensus rule:** If 2+ agree, that verdict lands
6. **If no consensus:** Escalate or re-assess (no verdict lands without consensus)
7. **Record verdicts** in append-only log (immutable audit trail)
8. **Execute immediately** (no user gate, no additional approval needed)

## Why It Works

- **Independence prevents groupthink** — agents can't influence each other
- **3+ catches overlapping blind spots** — what one agent misses, another sees
- **Consensus is strict** — 2+ of N is proportional majority, not bare quorum
- **Audit trail is immutable** — every verdict recorded with reasoning
- **Scalable** — works with any N ≥ 3, any model (Haiku preferred for cost)

## Constraints

- Cannot be used for user-gated decisions (approval, secrets, irreversible mutations)
- Agents must have access to the artifact/frame (cannot reason blind)
- Cannot be used for credential handling or sensitive material
- Minority verdicts recorded but do NOT land as verdicts

## Related Patterns

- **Ratification Fallback:** Parallel Consensus Swarm used for doctrine ratification when hub infrastructure is missing
- **Autonomous Adjudication:** Claude uses swarm to decide next steps without asking the user
- **Haiku Validation:** All Haiku-driven verdicts use this pattern (no single-seat Haiku review)

## Comparison with Adobe's Role-Based Swarm

Adobe's pattern uses fixed roles (Pessimist/Pragmatist/Innovator) to get perspective diversity. This pattern uses independent agents to get redundancy and catch blind spots. Both are valid; use Adobe's when you need distinct perspectives, use this when you need confidence through independence.

---

**This pattern is binding for all high-confidence verdicts using Haiku-tier agents. It is not optional.**
