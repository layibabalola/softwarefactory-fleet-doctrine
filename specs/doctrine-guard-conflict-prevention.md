# Doctrine Export: Automated Doctrine Repo Conflict Prevention

**Date:** 2026-09-12T15:30:00Z  
**Source:** Swarm-Designed System (preventing Conjugal-vs-DNG scenario)  
**Authority:** Fleet consensus via swarm audit  
**Status:** SPECIFICATION (ready for implementation across projects)

---

## Problem

When multiple projects push doctrine specs to the shared repo around the same time, conflicts go undetected until manual audit:
- Naming collisions (same concept, different names)
- Scope overlaps (specs claiming authority over same domain)
- Verdict contradictions (conflicting guidance on same subject)

**Real example:** Conjugal pushed `autonomous-decision-making-with-adversarial-swarms.md` (09:45:47); DNG pushed `autonomous-swarm-adjudication.md` (10:04:25, ~19 min later). Both valid, but overlapping terminology caused manual reconciliation work.

**Cost:** Manual swarm audits after push, conflicts propagate to fleet.

---

## Solution: Doctrine Guard

Automated system that:
1. Intercepts push before specs reach remote
2. Detects conflicts via 3-layer algorithm
3. Runs reconciliation swarm on conflicts
4. Auto-pushes safe changes or prompts user
5. Leaves audit trail for future reference

---

## Architecture

### Where It Lives

**Primary:** Local git pre-push hook (`.git/hooks/pre-push`)  
**Fallback:** Server-side pre-receive hook (if pre-push is bypassed)  
**Tools:** Python scripts in `coordination/doctrine-guard/`  
**Index:** `coordination/doctrine-guard/doctrine-index.json` (cached metadata)

### When It Runs

```
User: git push origin master
  ↓
Pre-push hook triggers
  ↓
Fetch latest remote (non-blocking)
  ↓
Analyze new commits for doctrine specs
  ↓
detect-conflicts.py runs (3-layer algorithm)
  ↓
If conflicts found → reconcile-swarm.py (4-6 agents)
  ↓
Verdict: AUTO_PUSH / PROMPT_USER / BLOCK_PUSH / ESCALATE
  ↓
Proceed or halt based on verdict
```

---

## Conflict Detection (3-Layer Algorithm)

### Layer 1: Name/ID Collision

```python
if new_spec.id in doctrine_index:
    existing = doctrine_index[new_spec.id]
    if existing.hash != new_spec.hash:
        # Same name, different content = hard conflict
        return CONFLICT_HARD
```

**Verdict:** REJECT (same ID must have same content)

### Layer 2: Scope Overlap

```python
overlap = new_spec.scope ∩ existing_specs.scope
if overlap:
    # Do they contradict on overlapping subjects?
    for subject in overlap:
        if new_spec.verdict[subject] ≠ existing_spec.verdict[subject]:
            return CONFLICT_MEDIUM  # Needs swarm review
```

**Verdict:** SWARM_REVIEW (may coexist or need merge)

### Layer 3: Subject-Level Contradictions

```python
shared_subjects = new_spec.subjects ∩ existing_spec.subjects
for subject in shared_subjects:
    if new_spec.verdict[subject] ⊕ existing_spec.verdict[subject]:
        # Contradictory verdicts on same subject
        if new_spec.authority.weight < existing_spec.authority.weight:
            return CONFLICT_AUTHORITY  # Lower authority overriding higher
```

**Verdict:** SWARM_REVIEW or ESCALATE (depends on authority)

### False-Positive Mitigation

- **Keyword-only overlap:** No conflict (e.g., "swarm" mentioned in different contexts)
- **Both scope overlap AND verdict difference:** Conflict (high signal)
- **User intent tags:** Suppress false positives
  ```yaml
  intent: "explore-alternative"  # Swarm allows parallel research
  tags: ["intentional-parallel"]  # Skip conflict checks
  ```

---

## Swarm-Based Reconciliation

### Agents (Standard 4)

1. **Novelty Analyst** → Is the new spec genuinely novel?
2. **Quality Reviewer** → Which is higher quality/more comprehensive?
3. **Scope Complementarian** → Can they safely coexist?
4. **Authority Arbiter** → Does authority hierarchy resolve this?

### Agents (Add for Severe Conflicts)

5. **Synthesis Designer** → Propose merged/unified spec
6. **Risk Assessor** → Warn of downstream breakage

### Consensus Rule

**Proceed if ≥3/4 agents agree on same verdict.**

### Verdicts

- **MERGE** → Specs should combine; generate unified version
- **RENAME** → New spec valid but needs naming change
- **COEXIST** → Both valid; add cross-refs, live separately
- **DEFER** → Needs owner decision; escalate
- **REJECT** → New spec doesn't add value; existing is superior

---

## User Intent Specification

Developers can declare intent in spec header or commit trailer:

```yaml
intent: ["propose" | "validate" | "explore-alternative" | "parallel-research"]
rationale: "Why you're pushing this spec"
override: false  # true → forces push despite conflicts (audit trail required)
```

### Intent Levels

| Intent | Swarm Response | Auto-Push | Use Case |
|--------|---|---|---|
| **propose** | Full evaluation | Only if green | Standard new spec |
| **validate** | Verify against existing | Only if green | Validating prior art |
| **explore-alternative** | Allow coexistence | Yes if coexist verdict | Testing variant approaches |
| **parallel-research** | Tag as experimental | Yes if safe | Non-binding exploration |
| **override: true** | Analyze but proceed | Yes (with audit) | Emergency; needs owner ACK |

---

## Verdict and Action

### Green (Novel/Safe)
```
✓ No conflicts detected
✓ Auto-push with optional reconciliation artifact
```

### Yellow (Potential Conflicts)
```
⚠️  Scope overlap detected
⚠️  Swarm verdict: COEXIST (needs cross-refs)
⚠️  Pushing with reconciliation commit
```

### Red (Hard Conflicts)
```
✗ Name collision detected
✗ Hard conflict; cannot auto-push
✗ Requires user resolution or --force-doctrine-push override
```

### Escalation (Deadlock)
```
❓ Swarm deadlock (no consensus)
❓ Escalating to owner for judgment
❓ Block push; awaiting owner decision
```

---

## Reconciliation Artifacts

When swarm resolves a conflict, doctrine-guard auto-generates:

```
Reconciliation Commit:
├── Adds cross-references between conflicting specs
├── Documents swarm verdict and reasoning
├── Updates doctrine-index.json metadata
└── Auditable record of resolution process
```

**Example:**

```
docs(doctrine): reconcile SwarmGovernance-v1 ↔ SwarmPattern-v2

Both specs are valid and complementary:
- SwarmPattern-v2 (Conjugal): Binding fleet standard, role-based,
  comprehensive escalation/failure-mode guidance
- SwarmGovernance-v1 (DNG): Provisional variant, role-free, explores
  application-specific autonomy bounds

Swarm verdict (4/4 agents): COEXIST with bidirectional cross-refs

Agent 1 (Novelty): Genuinely novel (explores different autonomy bounds)
Agent 2 (Quality): v2 more comprehensive; v1 narrower but opinionated
Agent 3 (Scope): Safe coexistence via cross-reference
Agent 4 (Authority): v2 author (Conjugal) higher weight; v1 valid alternative

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
```

---

## Implementation Files

```
coordination/doctrine-guard/
├── doctrine-index.json                    # Cached spec metadata
├── build-index.py                         # Rebuild index from specs
├── detect-conflicts.py                    # 3-layer conflict detection
├── reconcile-swarm.py                     # Orchestrate 4-6 agents
├── git-pre-push-hook.sh                   # Main hook script
├── settings.json                          # Config (thresholds, timeouts)
└── prompts/
    ├── novelty-analyst.md
    ├── quality-reviewer.md
    ├── scope-complementarian.md
    ├── authority-arbiter.md
    ├── synthesis-designer.md               # (for severe conflicts)
    └── risk-assessor.md                    # (for severe conflicts)
```

### Hook Installation

```bash
# Link hook into git
ln -s ../../coordination/doctrine-guard/git-pre-push-hook.sh .git/hooks/pre-push

# Test hook
chmod +x coordination/doctrine-guard/git-pre-push-hook.sh
git push --dry-run origin master
```

---

## Example: Conjugal vs. DNG (With Doctrine Guard)

### Timeline

```
T+0:00   Conjugal: Commits SwarmPattern-v2
T+0:05   Conjugal: git push origin master
         → Pre-push hook: No prior art found
         → Auto-push ✓

T+0:10   DNG: Commits SwarmGovernance-v1 (unaware of Conjugal push)

T+0:15   DNG: git push origin master
         → Pre-push hook triggers
         → Fetches latest (includes Conjugal's push)
         → detect-conflicts.py analyzes
         → Layer 2: Scope overlap detected (swarm-governance)
         → Layer 3: Verdict difference (autonomy_level)
         → Severity: MEDIUM → Trigger reconciliation swarm
```

### Swarm Runs (Background)

```
[Novelty]       Genuinely novel? YES (explores different autonomy bounds)
[Quality]       Comparable quality? NO (v2 more comprehensive)
[Scope]         Safe coexistence? YES (via cross-ref)
[Authority]     Authority hierarchy? v2 > v1 (Conjugal > Fable)

Consensus (4/4): COEXIST
```

### Doctrine Guard Action

```
✓ Verdict: COEXIST
✓ Generate reconciliation commit (add cross-refs)
✓ Push both specs + reconciliation artifact
✓ Update doctrine-index.json
```

### Result

- Both specs merge successfully
- Cross-refs link them
- Audit trail documents swarm verdict
- Future developers see relationship immediately
- No manual work

---

## Properties

### Prevents Silent Conflicts
✓ Conflicts are detected before specs propagate  
✓ Audit trail documents resolution process  
✓ No manual swarm audits after push

### Respects Developer Autonomy
✓ Green specs auto-push (doesn't slow dev velocity)  
✓ User intent tags control strictness  
✓ Override flag available (with audit trail)  
✓ Escalation to owner for genuine ambiguity

### Avoids Over-Strictness
✓ Coexistence preferred over rejection  
✓ False positives filtered (scope + verdict both required)  
✓ Keyword overlap alone doesn't block  
✓ Experimental specs can be tagged (skip checks)

### Audit Trail
✓ Reconciliation commit documents every decision  
✓ Swarm verdicts are persisted  
✓ Agent reasoning is captured  
✓ Future developers can understand resolution

---

## Fleet Adoption

### For Projects

1. **Copy files** from `coordination/doctrine-guard/` into your project
2. **Link hook:** `ln -s ../../coordination/doctrine-guard/git-pre-push-hook.sh .git/hooks/pre-push`
3. **Build index:** `python coordination/doctrine-guard/build-index.py`
4. **Test:** `git push --dry-run origin master` to verify hook works

### For Doctrine Repo Steward

1. Maintain `doctrine-index.json` (rebuild after each push lands)
2. Monitor reconciliation commits (audit trail of conflicts resolved)
3. Escalate deadlocks to owner for decision
4. Publish guidance when conflict patterns emerge

---

## Related Specs

- `specs/autonomous-decision-making-via-parallel-consensus-swarms.md` — How swarms make decisions
- `specs/account-rotation-and-project-continuity.md` — Immutable ledger pattern (related to audit trail)
- `adoption/swarm-pattern-guide-three-variants.md` — How to understand swarm pattern variants

---

## Future Enhancements

1. **Spec adoption pipeline** — How projects discover and adopt new specs from doctrine repo
2. **Automated migration** — When doctrine changes, auto-update dependent projects
3. **Doctrine versioning** — Track spec evolution and breaking changes
4. **Fleet metrics** — Which specs are adopted where; adoption lag

---

## Revision History

- **2026-09-12 v1.0**: Initial specification (swarm-designed conflict prevention system)
  - 3-layer conflict detection
  - 4-6 agent reconciliation swarms
  - Pre-push hook architecture
  - Audit trail via reconciliation commits
