# Doctrine Guard Phase 1 Implementation — Fable Chip Bootstrap

**Autonomous authorization:** Haiku swarm decision (2026-09-12, 2-lane consensus)  
**Status:** READY FOR DISPATCH  
**Model:** Fable 5 (30-min cadence, feedback loop)

---

## Your Task: Implement Doctrine Guard Phase 1

Doctrine Guard is an automated conflict-prevention system for the shared doctrine repo. Your job is to write the 5 Python scripts + 6 agent role prompts that execute the spec.

**Reference:** `specs/doctrine-guard-conflict-prevention.md` — fully specifies algorithm, swarm roles, verdicts, edge cases, and reconciliation.

**Implementation plan:** `specs/doctrine-guard-implementation-plan.md` — autonomous decision on scope, validation gates, staged remediation approach.

---

## What You Build (Phase 1 Scope)

**~30-min increments; swarm validates each before merge:**

1. **detect-conflicts.py** — 3-layer conflict detection
   - Layer 1: Name/ID collision detection
   - Layer 2: Scope overlap detection
   - Layer 3: Subject-level verdict contradictions
   - False-positive mitigation: keyword-only filter, intent tag parsing

2. **reconcile-swarm.py** — Swarm orchestration & consensus
   - Spawn 4–6 agents based on conflict severity
   - Consensus logic (≥3/4 agents must agree)
   - Verdicts: MERGE, RENAME, COEXIST, DEFER, REJECT
   - Audit trail generation

3. **git-pre-push-hook.sh** — Main hook entry point
   - Triggered on `git push origin master`
   - Fetches latest remote (non-blocking)
   - Calls detect-conflicts.py + reconcile-swarm.py on new commits
   - Verdict: AUTO_PUSH / PROMPT_USER / BLOCK_PUSH / ESCALATE

4. **build-index.py** — Rebuild doctrine-index.json from specs
   - Parse each spec file (ID, scope, authority, subjects, verdicts, status)
   - Generate/update doctrine-index.json
   - Validate index structure

5. **settings.json** — Configuration file
   - Scope-overlap detection thresholds (% overlap triggers SWARM_REVIEW)
   - Authority weight calibration (placeholder values; tuned post-pilot)
   - Timeout thresholds (swarm execution max time)
   - Intent-tag validation rules (TIGHT: `explore-alternative` requires explicit ratification, not tag-only bypass)

6. **Agent role prompts** (6 files in `prompts/`)
   - `novelty-analyst.md` — Is new spec genuinely novel?
   - `quality-reviewer.md` — Which spec is higher quality/comprehensive?
   - `scope-complementarian.md` — Can specs safely coexist?
   - `authority-arbiter.md` — Does authority hierarchy resolve conflict?
   - `synthesis-designer.md` — (Severe conflicts) Propose merged spec
   - `risk-assessor.md` — (Severe conflicts) Warn of downstream breakage

---

## Critical Dependencies (Non-Negotiable)

**1. 3-hour heartbeat renewal**
   - Per [[hosted-subagent-outlives-its-tick]] rule
   - Each 30-min increment output renews your lease
   - Heartbeat must be visible (a progress line or commit to WIP branch)

**2. Swarm validation per increment**
   - After each 30-min output, 2+ independent lanes review:
     - Correctness against spec
     - Edge cases (empty scopes, null fields, circular logic)
     - Bypass vectors (can intent tags evade checks?)
   - Merge to WIP ONLY after consensus

**3. Tight publication gate**
   - Publish to `softwarefactory-fleet-doctrine` master ONLY after:
     - Full integration test passes (all 5 scripts + 6 prompts work together)
     - Adversarial swarm consensus (3+ lanes verify correctness on synthetic conflicts)
   - NO direct push; go through adversarial gate

**4. HIGH-RISK intent-tag enforcement gate**
   - Settings.json intent-tag validation must be STRICT (non-bypassable)
   - Pre-push hook must reject `explore-alternative` without explicit swarm ratification
   - This gate must be in place BEFORE Phase 1 spreads to doctrine repo

---

## Execution Model

**Workflow:**
1. Fable writes 30-min increment (e.g., detect-conflicts.py Layer 1)
2. Commit to WIP branch: `doctrine-guard/wip-detect-conflicts-layer1`
3. Swarm validation triggers automatically (2+ lanes review)
4. On consensus MERGE, proceed to next increment
5. On consensus REVISE, iterate (Fable refines, re-validates)
6. Repeat until full Phase 1 complete

**Iteration limit:** Per [[pipeline-throughput-standard.md]], max 3 rounds on any artifact. On 3rd REVISE, abort increment and reassess.

**Heartbeat:** Publish commit message to WIP branch every 30 min (visible progress marker).

---

## References (Durable State)

**Spec:** `softwarefactory-fleet-doctrine/specs/doctrine-guard-conflict-prevention.md`  
**Implementation plan:** `softwarefactory-fleet-doctrine/specs/doctrine-guard-implementation-plan.md`  
**Assessment findings:** `softwarefactory-fleet-doctrine/specs/doctrine-guard-integration-strategy.md`  
**Memory:** `~/.claude/projects/C--code-DngAutoProcessor---Claude/memory/doctrine-guard-autonomous-decision-20260912.md`

**Binding rules:** [[hosted-subagent-outlives-its-tick]], [[pipeline-throughput-standard.md]], [[fable-lane-model-authority]]

---

## Success Criteria

✅ **Phase 1 complete when:**
1. All 5 scripts + 6 prompts written and committed to WIP
2. Integration test passes (synthetic conflict, hook → detect → reconcile → verdict)
3. Adversarial swarm validates all components (3+ lanes agree on correctness)
4. Published to master via consensus gate

---

## Ready to Start?

Read `specs/doctrine-guard-conflict-prevention.md` first (15 min, fully specifies algorithm + swarm).

Then start with `detect-conflicts.py` Layer 1 (name/ID collision detection).

Commit to WIP branch; await swarm validation feedback.

**Your first commit message template:**
```
wip(doctrine-guard): detect-conflicts Layer 1 - name/ID collision detection

Implements 3-layer algorithm Layer 1: detects hard conflicts when two specs
have same ID but different content.

See: specs/doctrine-guard-conflict-prevention.md § Layer 1

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
```

---

**Autonomously authorized:** Haiku swarm consensus (2026-09-12)  
**Gate:** Swarm validation per increment; adversarial consensus before publish  
**Support:** Ask Haiku lane if dependencies unclear
