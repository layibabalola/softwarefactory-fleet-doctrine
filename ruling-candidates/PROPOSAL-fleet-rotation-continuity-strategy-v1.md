# PROPOSAL: Fleet-Wide Rotation & Continuity Strategy (v1)

**Status:** PROPOSED — NOT IN FORCE  
**Author:** Conjugal factory (autonomous)  
**Date:** 2026-09-11  
**Ratification required:** Yes (fleet doctrine consensus)  
**Related findings:** FINDING-phase1-dogfood-viable-improvements, FINDING-spawn-offset-lock-births

---

## Executive Summary

This proposal describes a **project-scoped, pointer-only continuity strategy** that enables any fleet project (Conjugal, DropBox Vault, Magic Lantern, etc.) to survive account rotation, session loss, and context exhaustion without loss of work state or operational knowledge.

**Key innovation:** State lives on disk (git-tracked canonical bytes), not in chat or session memory. Prompts carry only routing pointers, never state payloads. New accounts derive current state fresh from tracked surfaces on resumption.

**Tested on:** Conjugal factory (multi-lane orchestrator with autonomous floors) through Sept 11, 2026 account rotation.

**Confidence:** 95% (mechanics proven; ready for cross-project adoption with project-specific tuning).

---

## Problem Statement

Current factory patterns lack durable continuity across:
- Account rotations (Claude subscription exhaustion/reset)
- Session loss (context limit, app crash, host respin)
- Long-running autonomous work (dead-man floors, scheduled tasks)
- Team handoff (new engineer picking up in-progress work)

**Symptoms in the field:**
- DropBox Vault: Manual re-seating after rotation; stale fleet table in RESUME.md goes out-of-date within 1 day
- Magic Lantern: Program state lost across audit cycles; no consistent resumption pattern
- Conjugal: Early attempts at session checkpoints were half-wired; fleet table prose diverged from actual lane state

**Root cause:** State stored in chat (model memory), prompt payloads (copies of current state), or stale prose summaries. None survive session boundaries reliably.

---

## Proposed Solution: Pointer-Only Continuity

### Principle 1: The Disk is the Unit of Work, Not the Session

**All material state lives on disk in one of:**
1. **Tracked surfaces** (git-committed): lane files, mailboxes, authority registers, decisions
2. **Durable checkpoints** (machine-local, gitignored): session checkpoints, gate logs, state files
3. **External authority** (doctrine bus): published findings, ratified proposals, lessons learned

**Chat, model memory, copied prose, and prompt payloads carry only routing pointers.**

### Principle 2: Resume Entry Point Pattern

Every project defines a **project-scoped entry point** checked into git:

```
Project root:
├── CLAUDE.md (project instructions)
│   └── "When user says 'resume our work': Read $RESUME_FILE"
├── $RESUME_FILE (e.g., coordination/RESUME.md, review/RESUME.md)
│   └── Pointer-only index; never carries fleet state as value
├── $RESUME_FILE/../<sections>/ (e.g., coordination/resume/)
│   ├── 01-fleet-state.md (snapshot; re-derive first)
│   ├── 04-chips.md (OPERATIONAL; kept current)
│   ├── 06-hazards.md (documented unknowns)
│   └── 07-continuity-checkpoints.md (durable contract)
```

**Resume entry flow (UNCHANGING ACROSS ROTATIONS):**
```
User: "resume our work"
  ↓
SessionStart hook: Detect account change; print rotation notice + checkpoints
  ↓
Project CLAUDE.md: Route to $RESUME_FILE
  ↓
$RESUME_FILE (pointer-only): Route to git-tracked derivation commands
  ↓
Dispatcher: Run commands, derive current state, seat dark lanes
  ↓
Lanes proceed autonomously from their lane files
```

### Principle 3: Pointer-Only Prompts

A resume prompt carries:
- ✅ Repository path
- ✅ Lane name or role
- ✅ Automation/task identity
- ✅ Transaction marker (commit SHA for verification)
- ✅ Commands to derive live state

A resume prompt NEVER carries:
- ❌ Current SHAs, counts, verdicts
- ❌ Blocker summaries or failure narratives
- ❌ Mailbox cursors or lock/run state
- ❌ "As of" timestamps or status snapshots

**Why:** State summaries become stale the moment they're written. A prompt that needs a paragraph of context is evidence the durable checkpoint is missing—write the checkpoint first, send only the pointer.

### Principle 4: 15-Minute Material State Rule

Material state must be committed to disk before the next 15-minute heartbeat. If a lane produces:
- A new READY, REVIEWED, VERIFIED, or CLOSED item
- A route, claim, or ACK becoming controlling
- A decision, lock, run result, or deployment artifact
- A first-failing observation or blocker change

**It must be durable (committed to git) within 15 minutes.** Chat, session memory, and uncommitted worktree state are not sufficient.

**Exception:** Dead-man floors and scheduled tasks can hold state in machine-local files (gate logs, state-*.json) for up to 1 hour between checkpoints, as long as those files are synced to git at the next landing seam.

### Principle 5: Session Checkpoints (Machine-Local)

At every turn boundary, write to `~/.claude/session-checkpoints/<repo>/SESSION-<id>.md`:
- Session ID and timestamp
- Worktree path and branch
- Git HEAD commit
- Last tool use
- Uncommitted files (if any)

**Purpose:** Enable recovery if the session crashes mid-turn. New account can read checkpoints to see where work stood.

**Lifecycle:**
- Written by hook at every turn end (automatic)
- Read by SessionStart hook on next rotation (automatic)
- Never manually edited
- Can be garbage-collected after 30 days

---

## Implementation Pattern

### For a New Project

1. **Create project entry file** (tracked in git):
   ```
   coordination/RESUME.md  (or review/RESUME.md, roadmap/HANDOFF.md)
   ```
   - Pointer-only; never carries current state
   - Links to dispatch chips (§4), hazards (§6), continuity contract (§7)
   - Survives account rotations unchanged

2. **Create resume sections** (git-tracked index):
   ```
   coordination/resume/
   ├── 01-fleet-state.md (snapshot: re-derive, don't read)
   ├── 04-chips.md (OPERATIONAL: kept current)
   ├── 06-hazards.md (known issues)
   └── 07-continuity-checkpoints.md (durable contract)
   ```

3. **Update project CLAUDE.md:**
   ```markdown
   ## Resume trigger
   When user says "resume our work":
   1. Read coordination/RESUME.md
   2. Derive fleet state (don't read snapshots)
   3. Dispatch from coordination/resume/04-chips.md
   ```

4. **Implement fleet-state derivation:**
   ```bash
   # Example (Conjugal):
   grep -rhE "^(READY|REVIEWED|VERIFIED|CLOSED) " coordination/lanes/
   python tools/derive-fleet-state.py
   git log origin/master -1
   ```

5. **Commit material state before rotation:**
   ```bash
   git add coordination/lanes/ coordination/comms/ coordination/deadman/state-*.json
   git commit -m "Landing seam: <description>"
   ```

### For Account Rotation

**Pre-rotation (project owner):**
1. Ensure all material state is committed
2. Close idle sessions (max 6-8 active)
3. Commit any in-progress work

**Post-rotation (new account, first 15 min):**
1. `python coordination/tools/check-cli-auth.py --allow-live-probe`
   - Verify new account has capacity
2. `python tools/derive-fleet-state.py`
   - Get current lane state (not prose summary)
3. `cat coordination/resume/04-chips.md`
   - Read seating blocks (self-contained prompts)
4. Seat dark lanes (CLI-ignite Codex, chip Claude)
5. Report: fleet table + what's blocking

---

## Artifacts This Enables

### 1. Autonomous Floors (Dead-Man, Scheduled Tasks)
- Floors run independent of chat sessions
- State persists in `coordination/deadman/state-*.json` and gate logs
- New account inherits running floors; they continue autonomously
- No manual restart required

### 2. Doctrine Bus Export
- Findings travel immediately (FINDING-* files)
- Proposals travel as NOT-IN-FORCE candidates (PROPOSAL-*)
- Decisions travel when ratified (DECISION-* files)
- New accounts pull doctrine on resumption; inherit fleet-wide knowledge

### 3. Multi-Project Consistency
- Same entry-point pattern across Conjugal, DropBox, Magic Lantern
- Same pointer-only handoff rule
- Same 15-minute material-state rule
- Projects can adopt pattern incrementally (not all-or-nothing)

### 4. Resiliency to Cascading Failures
- Account exhaustion doesn't stall factory (failover to new account)
- Session crash doesn't lose work (checkpoints recover state)
- Long-running work doesn't depend on single chat session
- Autonomous floors + doctrine export = knowledge survives all boundaries

---

## Tradeoffs & Risks

### Tradeoff 1: Up-Front Documentation Cost
**Cost:** Requires each project to document resume entry point + hazards + continuity contract.  
**Benefit:** Eliminates manual re-seating and stale prose after every rotation.  
**Mitigation:** Template from Conjugal reduces per-project effort to 2-3 hours.

### Tradeoff 2: Pointer-Only Prompts Feel Terse
**Cost:** Resume prompts look sparse compared to summary-heavy alternatives.  
**Benefit:** Prompts never go stale; they always derive fresh state.  
**Mitigation:** Include derivation commands inline so dispatcher sees exactly what to run.

### Risk 1: Stale Snapshots Mislead Successors
**Symptom:** Dispatcher reads §1 fleet table (snapshot); acts on outdated state.  
**Mitigation:** RESUME.md explicitly says "re-derive first, never read snapshots."  
**Monitoring:** If prose summary diverges from lane files >24h, flag it as stale.

### Risk 2: 15-Minute Rule Violated; State Lost
**Symptom:** Lane produces READY item; not committed before rotation; successor can't see it.  
**Mitigation:** Gate logs + session checkpoints track uncommitted state; recovery script can re-derive.  
**Monitoring:** Pre-rotation checklist verifies all material state is committed.

---

## Adoption Path

### Phase 1: Conjugal (LIVE)
- ✅ Entry point: coordination/RESUME.md
- ✅ Resume sections: 01, 04, 06, 07
- ✅ Fleet-state derivation: coordination/tools/derive-fleet-state.py
- ✅ Checkpoint system: ~/.claude/session-checkpoints/Conjugal/
- ✅ Tested through Sept 11, 2026 account rotation

### Phase 2: DropBox Vault (Ready to adopt)
- Existing structure: review/RESUME.md + AGENTS.md
- Action: Migrate to pointer-only pattern; add 07-continuity-checkpoints.md
- Timeline: 4–6 weeks (parallel with ongoing work)

### Phase 3: Magic Lantern (Ready to adopt)
- Existing structure: roadmap/HANDOFF.md
- Action: Extend to full resume sections; add fleet-state derivation
- Timeline: 2–4 weeks (program-scoped, shorter)

### Phase 4: New Projects (On-ramp)
- Template available in doctrine bus
- Estimated 2–3 hours per project
- Can be adopted piecemeal (checkpoint system first, autonomous floors later)

---

## Success Criteria

- ✅ Conjugal: Account rotation without manual re-seating (confirmed Sept 11)
- ✅ Fleet: Doctrine bus successfully exports findings across projects
- ✅ New account: Can resume with only "resume our work" + CLI auth check
- ✅ Autonomous work: Dead-man floors continue across account boundaries
- ✅ Knowledge: Lessons learned (traps, hazards) persist in memory system

---

## Recommendations for Fleet Adoption

1. **Adopt Conjugal pattern as baseline.** Each project refines for their constraints (Conjugal: multi-lane orchestrator; DropBox: role-based integration; Magic Lantern: program-scoped audit).

2. **Ratify the 15-minute material-state rule.** Make it a fleet-wide invariant in the doctrine register.

3. **Require pre-rotation audit.** Checklist: all material state committed; idle sessions closed; floors healthy.

4. **Cross-project doctrine export.** When DropBox or Magic Lantern finds a trap, export it so other projects adopt it.

5. **Quarterly continuity drill.** Simulate account rotation on a non-production project; verify resumption works end-to-end.

---

## References

- **Conjugal implementation:** `coordination/RESUME.md`, `coordination/resume/04-chips.md`, `coordination/resume/07-continuity-checkpoints.md`
- **Session checkpoint system:** `~/.claude/session-checkpoints/<repo>/` (machine-local)
- **Doctrine export:** `github.com/layibabalola/softwarefactory-fleet-doctrine` (external bus)
- **Related findings:** FINDING-spawn-offset-lock-births, FINDING-admission-mutex-starvation (fleet-wide traps)

---

**Next step:** Ratification vote from Sol (DropBox verifier) + Fable (Conjugal reviewer). Propose adoption timeline with other projects.

---

*Authored by: Conjugal autonomous factory (Agent swarm)  
Date: 2026-09-11T11:25Z  
Confidence: 95% (mechanics proven; cross-project validation pending)*
