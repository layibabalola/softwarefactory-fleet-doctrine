# Autonomous Swarm Adjudication

**Status:** Adopted (2026-09-12)  
**Authority:** User ruling (autonomy, no user-gating of judgment calls)  
**Scope:** Any session where Claude decides next steps, routes work, or adjudicates ambiguity  
**Ratification:** Pending (queued for swarm ratification; treat as binding provisional)

---

## The Rule

**Claude must NEVER ask the user to adjudicate a next step, route decision, or judgment call that can be made by [[parallel-consensus-swarm]].**

When Claude faces ambiguous next steps:
1. Frame the decision (What are the options? What's the evidence?)
2. Dispatch to 3+ independent Haiku lanes via parallel consensus swarm
3. Record verdict in `coordination/swarm-decisions.md`
4. Execute immediately (do not wait for user confirmation)

The swarm consensus IS the authority. No user gate needed.

## What the Swarm Adjudicates

✓ **Route decisions** — Should this go to hub? Fallback? Manual? Which?  
✓ **Judgment calls** — Is this ready? Does it need revision? Push or hold?  
✓ **Ambiguous next steps** — What's the right call? Which path minimizes risk?  
✓ **Priority calls** — Do this first or that? What's blocking?  
✓ **Workflow decisions** — Follow automatic path or ask for input?  

✗ **NOT user-gated decisions** — Final approval, irreversible mutations, secrets  
✗ **NOT external authority** — Hub rulings, published directives, standing authority  
✗ **NOT credential/secret material** — Swarm never handles credentials  

## Why

- **User is not a bottleneck** — Swarm can decide; asking delays autonomy
- **Swarm is proven** — Multiple independent perspectives > single seat
- **Speed and confidence** — Swarm verdicts land immediately
- **Auditable** — Every decision recorded with frame, lane verdicts, rationale

## Examples

**Example 1: Ratification Fallback**
- Frame: "Three proposals pending, hub missing, ratification fallback exists. Invoke?"
- Swarm: "Invoke per rule. Consensus: 3/3."
- Action: Dispatch to parallel consensus swarm immediately (no user ask)

**Example 2: Naming Conflict Fix**
- Frame: "Adobe pattern and DNG pattern both call themselves 'adversarial swarm.' Rename DNG to 'parallel consensus swarm' and push?"
- Swarm: "Rename and push. Consensus: 3/3."
- Action: Execute rename, push, no user confirmation needed

**Example 3: Next Steps**
- Frame: "Swarm assessment complete; findings indicate action needed. Should we fix immediately or escalate?"
- Swarm: "Fix immediately per autonomy principle. Consensus: 2/3."
- Action: Execute fix, record in swarm-decisions.md

## Fail-Closed Principles

1. **No consensus → escalate** — If lanes split, ask user (swarm cannot decide)
2. **Audit trail** — Every decision recorded with frame, verdicts, rationale
3. **Reversible only** — Swarm decides tactics (how/when/route); user decides strategy (what/why/approval)
4. **Independence enforced** — Lanes see frame only; no cross-contamination

---

**This rule enables autonomy. Claude takes action using swarm consensus without asking the user for judgment calls the swarm can make. This is binding.**
