# Adversarial Swarms and Continuous Doctrine Publishing Standard

**Authority:** Adobe Document Cloud Ingester factory, standing directive ratification  
**Status:** FLEET STANDARD — effective 2026-09-11  
**Scope:** All factories and multi-agent systems using Haiku-tier agents for decision-making

---

## Standard 1: Adversarial Haiku Swarms

### Rule

**Whenever Haiku is used for investigation, diagnosis, or decision-making, spawn THREE opposing agents (not one).**

Each agent receives the same task but with a distinct brief:
1. **Pessimist** — identify risks, hard blockers, constraints, what could go wrong
2. **Pragmatist** — recommend the achievable path, what works right now, cost-benefit analysis
3. **Innovator** — propose novel approaches, future possibilities, transformative options

### Rationale

- **Single-agent bias:** One Haiku agent gives one angle. Blind spots go undetected.
- **Trio consensus:** Three opposing perspectives catch edge cases, minority views, and hidden assumptions that a single agent would miss.
- **Cheap diversity:** Haiku is low-cost; spawning three is still cheaper than one Opus and gives better coverage.
- **Proven in factory:** Adobe Document Cloud Ingester used adversarial swarms for Q-034 concurrent review, Astra integration, product dogfooding, and multi-provider strategy. All three swarms (Pessimist/Pragmatist/Innovator) delivered non-obvious insights that a single agent would have missed.

### Implementation

```python
# Pseudocode for spawning adversarial swarm

agents = [
  Agent(
    description="Pessimist: risks and blockers",
    prompt=f"""
    You are the Pessimist voice in an adversarial swarm. Your role: identify what could go wrong, 
    hard blockers, constraints, and risks.
    
    {task_context}
    
    Find the worst-case scenario, the constraints that bind the solution, and why the obvious 
    path might fail. Argue for caution.
    """
  ),
  Agent(
    description="Pragmatist: achievable path",
    prompt=f"""
    You are the Pragmatist voice in an adversarial swarm. Your role: recommend the path that 
    works right now, what's achievable today, cost-benefit tradeoffs.
    
    {task_context}
    
    Find the minimal viable solution. What's the fastest path to proof? What's the cost in 
    tokens, time, and complexity? Argue for action.
    """
  ),
  Agent(
    description="Innovator: transformative options",
    prompt=f"""
    You are the Innovator voice in an adversarial swarm. Your role: propose novel approaches, 
    future possibilities, what could be transformative.
    
    {task_context}
    
    What's the approach that seems harder but unlocks disproportionate value? What does the 
    future look like? Argue for ambition.
    """
  )
]

results = parallel_spawn(agents)
synthesis = adjudicate(results)  # Synthesize findings before acting
```

### When to Use

- **Open-ended investigation:** "What's blocking product delivery?"
- **Decision points:** "Should we do X or Y?"
- **Risk assessment:** "What could go wrong with this approach?"
- **Feasibility:** "Is this reachable in the time/token budget?"
- **Architecture:** "How should we structure this?"

### When NOT to Use

- **Routine execution:** Don't swarm for "run this test" or "commit this change"
- **Single-perspective tasks:** Don't swarm if only one view is valid
- **Trivial questions:** Don't swarm for "what's in this file?" — use a single read

---

## Standard 2: Continuous Doctrine Publishing

### Rule

**As the factory produces working strategies, proven patterns, and evidence, publish them to `softwarefactory-fleet-doctrine` immediately. Don't batch. Don't wait for "completion."**

Every insight that other projects could reuse should be codified and shared as soon as it's proven.

### Rationale

- **Fleet acceleration:** Other projects (agent-bridge, MLV-App, Grok integrations, future factories) can reuse strategies and avoid repeating debugging cycles.
- **Knowledge capture:** Documented patterns live longer than institutional memory. They survive team turnover and account rotations.
- **Continuous ratification:** Doctrine is data, not instructions. Publishing early + feedback = continuous refinement.
- **Proven in factory:** Adobe identified three major patterns in one session (phased review, multi-provider failover, factory-for-product strategy) and published all three immediately. Other projects can now adopt without redesign.

### Implementation

1. **Identify what's novel and proven** (not obvious from existing doctrine)
   - Is this a new pattern or a refinement?
   - Is it tested, or just a hypothesis?
   - Does it generalize beyond this project?

2. **Write it as a spec** (markdown or YAML)
   - Evidence links (HUB entries, line numbers, commit SHAs)
   - Trade-offs and when to use it
   - Future refinements

3. **File a pull request** to `softwarefactory-fleet-doctrine/specs/`
   - Include exact line references so readers can verify
   - Link to factory HUB entries and receipts
   - Flag for ratification if it affects fleet policy

4. **Merge immediately** (don't wait for other work to finish)
   - Doctrine publishing shouldn't block product shipping
   - Run in parallel: implement + publish simultaneously

### What to Publish

**Candidates for immediate publication:**

- **New patterns:** Phased concurrent review, multi-provider failover, factory-for-product strategy
- **Proven constraints:** Hard blockers, trade-offs, architectural limits discovered during implementation
- **Recovery recipes:** How to recover from failure mode X; exact steps that worked
- **Model tier policy:** How to balance Astra/Fable/Sol/Opus/Sonnet/Luna/Haiku by role and cost
- **Provider capacity:** How to detect exhaustion, failover rules, budget tracking

**NOT candidates:**

- Temporary workarounds (unless they generalize)
- One-off fixes to code (those stay in git commit messages)
- Personal preferences (vs. evidence-backed decisions)

### Evidence Anchoring

Every doctrine contribution must be anchored to evidence:

```markdown
# Pattern Name

**Authority:** Factory name, date  
**Status:** WORKING STRATEGY | PROVEN APPROACH | IN DEVELOPMENT  
**Evidence root:** `.factory/coordination/HUB.md` seq 2026-09-11T06:45:00Z or commit hash

---

## Problem

[Context]

## Solution

[Pattern]

**Tested in:** Adobe factory WO-PROD-DOC-CLASSIFIER-001, approved 2026-09-11  
**Evidence:**
- HUB ledger entry: `.factory/coordination/HUB.md` line 26745–26780
- Adversarial swarm findings: agents a06e29bfde7773981, a12c41d867bbcb82d, acc33857571ab5e34
- Disposition: Pragmatist (architectural feasibility), Pessimist (blocker diagnosis), Innovator (multi-provider strategy)

---

## Future Refinements

[What comes next]
```

### Adoption Cadence

- **Week 1:** Factory proves pattern, publishes to doctrine, other projects notice
- **Week 2–4:** Other projects adopt, provide feedback, doctrine spec gets refined
- **Month 2:** Pattern is battle-tested across multiple projects; becomes fleet standard

---

## Ratification

Both standards are ratified effective 2026-09-11 and apply fleet-wide:

1. **Adversarial Haiku Swarms** — required for all Haiku-tier investigations and decisions
2. **Continuous Doctrine Publishing** — required for all factories and multi-agent systems

---

## Immediate Implementations

**Adobe Document Cloud Ingester factory (2026-09-11):**
- ✅ Spawned three adversarial agents (Pessimist, Pragmatist, Innovator) to adjudicate concurrent review, product dogfooding, and multi-provider strategy
- ✅ Published three doctrine contributions immediately: phased-concurrent-review-pattern.md, multi-provider-failover-pattern.md, adversarial-swarms-and-doctrine-publishing-standard.md (this file)

**Next projects adopting this standard should:**
1. Use adversarial swarms for all architectural decisions (not just Haiku; pattern applies to all tiers)
2. Publish findings to doctrine repo within 24 hours of proof, not after "completion"
3. Link evidence back to HUB or run receipts

---

## FAQ

**Q: Isn't spawning three agents wasteful?**  
A: No. Haiku is cheap (~0.001¢/token). The cost of one Pessimist + one Pragmatist + one Innovator is still less than one Opus, and you get three perspectives. The cost of missing a blocker (because one agent was blind) is far higher.

**Q: Can I pick different briefs for the three agents?**  
A: Yes, adapt the briefs to your decision. The pattern is "three opposing perspectives," not the specific names. Use whatever lens catches blind spots in your domain (e.g., "Compliance / Product / Technical" for legal decisions; "Security / Performance / Correctness" for infrastructure).

**Q: What if one agent's finding contradicts another?**  
A: That's a signal. Contradiction means the decision is genuinely hard or depends on assumptions. Surface the disagreement in your synthesis and make the trade-off explicit.

**Q: Can we publish incomplete work?**  
A: Publish working strategies and proven patterns. Incomplete work should say "IN DEVELOPMENT" and link to the issue. Don't publish speculative ideas as doctrine; publish tested approaches.

**Q: Who owns doctrine publishing?**  
A: The factory owner / project lead. It's part of the regular cadence, like shipping code.

