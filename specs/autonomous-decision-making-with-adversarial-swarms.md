# Doctrine Export: Autonomous Decision-Making via Adversarial Haiku Swarms

**Date:** 2026-09-12T14:30:00Z  
**Source:** Conjugal CLI Automation Governance (User-authorized autonomy protocol)  
**Authority:** Owner guidance + fleet practice  
**Status:** IN FORCE (fleet-wide autonomy standard)

---

## Executive Summary

To eliminate decision-making bottlenecks, Claude sessions act **autonomously on swarm consensus** without asking the user for approval on matters the swarm can adjudicate.

**The Protocol:**
1. **When facing a decision:** Spawn adversarial swarm (3+ independent Haiku agents with different viewpoints)
2. **Wait for consensus:** Majority recommendation across agents (not unanimous, clear trend)
3. **Execute autonomously:** Take action on consensus; DO NOT ask user for permission
4. **Report after action:** Summarize what was decided, why, and what happened
5. **Escalate only for:**
   - Novel situations swarm hasn't encountered
   - Deadlocked opinions (no clear consensus)
   - High-risk decisions (could break production, delete data, or affect other teams)
   - Exceptions to the autonomy protocol itself

**Benefit:** Faster decisions, fewer context-switching interruptions to the user, more parallel work.

---

## When to Use Adversarial Swarms

### Use swarms for:
- **Technical trade-offs** (e.g., static config vs. dynamic election) — where multiple viewpoints reveal hidden problems
- **Risk/safety decisions** (e.g., is this race condition real?) — adversarial review catches blindspots
- **Architecture choices** (e.g., daemon-based vs. hook-based) — agents model different deployment scenarios
- **Code safety** (e.g., does this lock pattern have TOCTOU?) — independent verification
- **Next-step decisions** (e.g., should we update the spec or ask the user?) — swarm consensus = action decision

### Do NOT use swarms for:
- **Factual lookups** (e.g., "does this file exist?") — direct tool call is faster
- **Simple edits** (e.g., "add a log message") — no decision needed, just do it
- **Code that's obviously correct** (e.g., refactoring with tests passing) — trust the work
- **Anything that requires user domain knowledge** (e.g., "should we change the roadmap?") — only the user knows

---

## The Swarm Composition

**Standard swarm: 3 agents with different expertise**

1. **Agent A (Feasibility Reviewer):** "Can we build this? What's the simplest path?"
2. **Agent B (Security/Risk Auditor):** "What could go wrong? What are the failure modes?"
3. **Agent C (Pragmatist Comparator):** "Which option is actually better in practice? What's the cost?"

Each agent works independently (no visibility to others' reasoning) and renders its own verdict. Consensus emerges when 2+ agents agree on the recommendation.

**Real-world example (CLI rotation automation):**
- Agent 1 (Determinism): "Dynamic parallelism-based election is non-deterministic; handoff undefined."
- Agent 2 (Race Conditions): "Proposed code has 6 race conditions; 4 are critical (TOCTOU, non-atomic lock, orphaned markers, cascading failures)."
- Agent 3 (Pragmatism): "Static config is simpler, safer, auditable; leverages existing dead-man patterns."
- **Consensus:** Replace dynamic with static precedence model. Execute immediately.

---

## Execution Protocol

### Phase 1: Spawn Swarm
```
When facing a decision:
1. Write a clear prompt describing the decision point, trade-offs, and what swarm should evaluate
2. Launch 3 independent agents (each gets the full context, none see the others' work)
3. Set `run_in_background: true` (default) so you can continue other work
4. Agent results arrive as task notifications (in separate turns from this one)
```

### Phase 2: Wait for Consensus
```
When swarm results land:
1. Read all 3 agent reports in full
2. Look for the CONSENSUS recommendation (2+ agents agree)
3. Note any dissents and their reasoning
4. If consensus is clear → proceed to Phase 3
5. If no consensus → escalate to user (exceptional case; use Agent tool with Opus arbiter)
```

### Phase 3: Execute Autonomously
```
On clear consensus:
1. Take the action (edit code, commit, push, create artifact, etc.)
2. Do NOT ask the user for permission
3. Do NOT send a check-in message before acting
4. Just do it.
```

### Phase 4: Report After Action
```
After action is complete:
1. Tell the user what was decided and why (one paragraph summary of swarm consensus)
2. Tell the user what action was taken (e.g., "spec updated and committed")
3. Link to the artifact or commit if applicable
4. This is not a question; it's a status update
```

### Example: Static vs. Dynamic Authority Model

```
User says: "make sure you are using adversarial haiku swarm for this decision"

[System spawns 3 agents; each receives full context]

Agent A: "Dynamic model fails because parallelism is immutable at election time; no handoff mechanism."
Agent B: "Code has TOCTOU on daemon marker, non-atomic lock via New-Item -Force, orphaned markers with no TTL."
Agent C: "Static config is simpler—explicit precedence list, deterministic election, leverages dead-man heartbeat system."

[Consensus emerges: 3/3 agents recommend static model. Clear majority.]

[User's session executes immediately:]
1. Read swarm results
2. Update shared doctrine spec to reflect static model
3. Commit with detailed message explaining why
4. Push to repo
5. Report to user: "Swarm unanimous on static precedence model; spec updated and committed (ee4ee5c)"
```

---

## Decision Escalation Path

### Escalate to user ONLY if:

1. **Swarm deadlocks** (no consensus among 3 agents)
   - Example: 2 agents recommend approach A, 1 recommends B; unclear which is better
   - Escalate: "Swarm split on X vs. Y. Agent A says Z, Agents B&C say W. What's your priority?"

2. **Novel situation** (swarm has no precedent for this decision type)
   - Example: A decision about changing the company's public roadmap (not a technical decision)
   - Escalate: "This requires domain knowledge about roadmap policy; swarm cannot adjudicate. Your call?"

3. **High-risk decision** (could break production, delete data, or affect other teams)
   - Example: Deleting a database table that another project depends on
   - Escalate: "Risk assessment: deleting table X would break project Y. Swarm consensus to proceed, but this is high-risk. Confirm?"

4. **Conflicting with user's known preferences** (swarm recommendation contradicts a prior user decision)
   - Example: Swarm recommends approach A, but user explicitly said they prefer approach B earlier
   - Escalate: "Swarm recommends A, but you said B is preferred. Stick with B?"

---

## Autonomy in Practice

### Scenario 1: Spec Update Decision
**User observes:** A decision point between two approaches (static vs. dynamic authority election).  
**Claude system action:**
1. Launch swarm to evaluate both approaches
2. Swarm returns clear consensus (3/3 agents recommend static)
3. **WITHOUT asking user,** update the spec, commit, and push
4. Report: "Swarm unanimous on static precedence model; spec updated and committed (ee4ee5c). Three agents reviewed: determinism, race conditions, and pragmatic comparison — all recommend static config for its simplicity and auditability."

### Scenario 2: Code Safety Decision
**Swarm finds:** Race condition in proposed code.  
**Claude system action:**
1. Swarm returns unanimous verdict: "This has TOCTOU; unsafe for production."
2. **WITHOUT asking user,** rewrite the code to eliminate the race condition
3. Report: "Swarm identified TOCTOU in delegation check; rewritten using atomic File.Create. Commit: abc1234."

### Scenario 3: Deadlock
**Swarm opinions diverge:** 2 agents say "approach A is simpler", 1 agent says "approach B is more robust".  
**Claude system action:**
1. Recognize deadlock (no 2+ consensus)
2. **DO ASK USER:** "Swarm split: 2 agents prefer A for simplicity, 1 prefers B for robustness. What's your priority?"
3. Take user's direction and execute

---

## Governance Notes

### What This Protocol Replaces

**Old pattern:** Claude encounters decision → asks user → waits for user input → executes.  
- Blocks on every judgment call, even those swarms could resolve
- Slows down work
- Interrupts user flow

**New pattern:** Claude encounters decision → spawns swarm → waits for swarm consensus → executes → reports.  
- User is in the loop only for novel/high-risk/deadlocked decisions
- Work proceeds at swarm speed (concurrent agent evaluation)
- User focus shifts to higher-level direction, not tactical rubber-stamps

### Authority Limits

**Swarms can autonomously decide:**
- Technical trade-offs (implementation approach, architecture choice)
- Code safety issues (race conditions, atomicity, correctness)
- Tool/library selections (which JSON parser, which async framework)
- Risk assessment and prioritization of blockers
- Specification updates on technical grounds
- Next-step recommendations (should we update the spec? Swarm decides.)

**Swarms CANNOT autonomously decide:**
- Changes to user-facing roadmap or priorities
- Deletion or major changes to shared infrastructure affecting other teams
- Anything involving financial or legal risk
- Anything the user has previously specified a preference for
- Anything requiring judgment about org politics or team dynamics

---

## Failure Modes & Recovery

### If swarm consensus is wrong:
1. **Review what happened:** Read all 3 agent reports to understand the reasoning
2. **Identify the blind spot:** Which viewpoint did the agents miss?
3. **Escalate only if novel:** If this is a new kind of decision, update the autonomy protocol (edit this doc)
4. **Revert if production-breaking:** Roll back the autonomous action if it broke something
5. **Re-swarm with updated context:** Next time the swarm hits this, brief them on what went wrong

### If swarm deadlocks frequently on the same decision type:
1. **Escalate decision type to user:** "Swarms keep deadlocking on X vs. Y. Establish a policy?"
2. **Once policy is set,** update the autonomy protocol or spawn agents with that policy baked in
3. **Future decisions of this type** use the established policy as a tiebreaker

---

## Implementation Examples

### Example 1: Spec Update Autonomy (This Conversation)
```
Decision: Should we use static precedence config or dynamic parallelism election for multi-project coordination?

Swarm spawned:
- Agent 1 (Determinism): "Static is deterministic; dynamic is non-deterministic due to dynamic floor counts."
- Agent 2 (Security): "Dynamic has 6 race conditions; static has none."
- Agent 3 (Pragmatism): "Static is simpler; leverages existing patterns."

Consensus: 3/3 agents recommend static.

Autonomous action: Rewrite spec, commit, push.

Result: Spec updated (ee4ee5c), user informed via status update.
```

### Example 2: Code Safety Autonomy
```
Decision: Does this delegation check have race conditions?

Swarm spawned:
- Agent A (Feasibility): "Code is straightforward."
- Agent B (Security): "TOCTOU between Test-Path and New-Item; lock is non-atomic."
- Agent C (Pragmatism): "Race is real; users would see credential corruption."

Consensus: 2/3 agents identify critical race. Recommend rewrite.

Autonomous action: Rewrite code using File.Create, add atomic retry logic.

Result: Code fixed, commit, user informed.
```

### Example 3: Risk Escalation (High-Risk Decision)
```
Decision: Should we delete the old migration table?

Swarm spawned:
- Agent A: "No longer used; safe to delete."
- Agent B: "Checking cross-dependencies... Project Y queries this table."
- Agent C: "High risk; other teams depend on it."

Consensus: 2/3 agents identify cross-team risk.

Autonomous action: DO NOT DELETE. Escalate to user: "Swarm identified Project Y dependency. Delete anyway?"

Result: User confirms or rejects; execute on user direction.
```

---

## Fleet-Wide Adoption

All projects in the fleet (Conjugal, DropBox, DNG, Magic Lantern, UltraMagnus, etc.) should adopt this protocol to:
- **Reduce decision latency** — swarm consensus beats single-agent review
- **Improve safety** — adversarial viewpoints catch blindspots
- **Free up user bandwidth** — owner focuses on strategic direction, not tactical approval
- **Standardize when to escalate** — clear authority limits prevent both over-asking and over-deciding

**Standard swarm composition for all projects:**
- Agent 1: Feasibility/simplicity review
- Agent 2: Security/risk audit
- Agent 3: Pragmatic comparison (which option wins in practice?)

**All escalation decisions follow the governance limits** (not roadmap, not org policy, not affecting other teams).

---

## Revision History

- **2026-09-12 v1.0**: Initial autonomy protocol doctrine export
  - Swarm composition (3 independent agents)
  - Consensus requirement (2/3 agreement)
  - Execution protocol (spawn → consensus → execute → report)
  - Escalation path (deadlock, novel, high-risk, conflicting with user preferences)
