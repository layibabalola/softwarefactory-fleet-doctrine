# PROPOSAL: Prior-Art Gate for Doctrine Repo Commits

**Status:** PROPOSAL (awaiting ratification)  
**Authority:** None (proposal only, not yet ratified)  
**Originated:** 2026-09-12 (Doctrine Guard implementation work)  
**Rationale:** Measured incident — Haiku committed doctrine specs without checking for prior art or conflicting patterns in repo

---

## Problem

When authoring new doctrine specs, there is no enforcement gate to verify prior-art sweep before pushing to shared repo.

**Measured incident (2026-09-12):**
- Haiku authored 3 specs for Doctrine Guard implementation (integration strategy, implementation plan, Fable chip bootstrap)
- Committed all 3 directly without checking for:
  - Existing conflict-prevention systems in repo
  - Specs addressing similar domains (swarm reconciliation, hook validation)
  - Naming collisions or scope overlaps
- Post-hoc check revealed **no conflicts** (Doctrine Guard is novel), but **process was backwards**
- Should have: prior-art sweep → commit; actually did: commit → sweep

**Risk:** Conflicting specs propagate to fleet undetected (ironically, the problem Doctrine Guard itself will prevent).

---

## Solution: Prior-Art Gate for Doctrine Repo Commits

**Binding rule:** No doctrine repo push without prior-art sweep.

**When:** Before ANY commit to `softwarefactory-fleet-doctrine/specs/`, `adoption/`, or `coordination/` directories.

**How:**

1. **Local git hook (pre-commit):**
   ```bash
   # Intercept commit before local history
   # Scan changed/new files for doctrine spec headers (id, scope, authority, subjects)
   # Query doctrine-index.json for overlaps
   # grep -r for keywords matching spec scope
   # REJECT if:
     - ID already exists in index (hard conflict)
     - Scope overlap ≥30% + verdict difference (medium conflict)
     - Naming collisions (same concept, different id)
   # WARN if:
     - Keyword-only overlap (allow with intent tag: "novel-exploration")
   # ALLOW if:
     - Fully novel (no overlaps)
   # Or: commit with intent tag + rationale
   ```

2. **Via grep + index query (manual check, if hook missing):**
   ```bash
   # Before pushing, run:
   grep -r "scope:\|authority:\|subjects:" <new-spec>
   grep "<scope-terms>" softwarefactory-fleet-doctrine/specs/*.md
   jq '.specs[] | select(.scope[] | contains("<term>"))' doctrine-index.json
   # If overlaps found, inspect those specs + decide: MERGE / RENAME / COEXIST / DEFER
   ```

3. **Publish gate (swarm validation, per Doctrine Guard):**
   - Pre-push hook intercepts push (will be Doctrine Guard itself, once implemented)
   - Runs conflict detection on new commits
   - If conflicts found, triggers reconciliation swarm
   - Verdict determines: auto-push / prompt-user / block-push

---

## Authority & Ratification

**Who should ratify:** Independent swarm (2–3 lanes)
- Lane 1: Safety reviewer (does this gate prevent conflicts? are false positives acceptable?)
- Lane 2: Usability reviewer (is the gate too strict? does it slow down legitimate proposals?)
- Lane 3: Precedent reviewer (are there related gates elsewhere in fleet? consistency with CLI credential rotation coexistence model?)

**Ratification gates on:**
1. Consensus (2+/3 agree) that gate is sound
2. Verdict: ADOPT / REFINE / DEFER
3. If REFINE: specific adjustments named (e.g., "raise overlap threshold from 30% to 50%")

---

## When This Takes Effect

**Immediate (manual discipline):**
- All new doctrine specs include prior-art sweep documented in commit message
- Rationale: "Swept for scope overlaps with [list specs checked]; found [conflicts / no conflicts]"

**On Doctrine Guard Phase 1 completion:**
- Pre-push hook automates sweep via `detect-conflicts.py`
- Manual sweep no longer needed (hook enforces)

**Optional Phase 2:**
- Add git pre-commit hook (local check, faster feedback)
- Prevent bad commits before they reach remote

---

## Edge Cases

**Intent tags (allow override with rationale):**
```yaml
intent: "explore-alternative"  # New approach to existing domain
rationale: "Investigate lightweight variant of X; existing spec Y remains authoritative"
```
Allows commit despite scope overlap, IF commit message documents intent + rationale.

**Cross-project coordination:**
When two projects push simultaneously (Conjugal + DNG case):
- Both pass local prior-art (neither knows about the other's in-flight commit)
- Pre-push hook (Doctrine Guard) catches on second push
- Swarm reconciliation runs
- Verdict: COEXIST + cross-refs (not a violation; gate design catches it)

**Novel proposals:**
Specs marked `intent: "propose"` are expected to have no prior art (by definition, novel).
Gate allows without conflict check IF `intent` tag present.

---

## References & Related Doctrine

- [[autonomous-swarm-adjudication]] — Swarm verdict patterns (MERGE/RENAME/COEXIST/DEFER/REJECT)
- [[doctrine-guard-conflict-prevention]] — Automated conflict detection system (once implemented)
- [[ratify-before-publish]] — Ratification workflow for novel strategies
- [[cli-credential-rotation-coexistence.md]] — Precedent for COEXIST verdict + cross-refs

---

## Success Criteria for Ratification

✅ **Swarm consensus (2+/3 lanes)** on:
1. Gate prevents actual conflicts (measured: 0 conflicting specs post-gate)
2. False-positive rate is acceptable (<10% of new specs flagged without real conflict)
3. Overhead is acceptable (prior-art sweep <5 min per commit)
4. Spec authors find rationale clear + intent tags useful

---

**Status:** PROPOSAL — awaiting independent swarm ratification  
**Next:** Route to fleet hub for ratification decision (target: 2026-09-13)  
**Author:** Haiku swarm (2026-09-12, measured incident)  
**Once ratified:** Publish to `softwarefactory-fleet-doctrine/specs/prior-art-gate-for-doctrine-commits.md`

---

**Note:** This proposal itself demonstrates the gate. Before publishing to doctrine repo (if ratified), should sweep for existing specs addressing:
- Conflict prevention (beyond Doctrine Guard)
- Commit gate patterns (pre-commit, pre-push, pre-receive)
- Doctrine publishing discipline

Currently aware of: Doctrine Guard spec (solution), CLI credential rotation coexistence (precedent), no known conflicts.
