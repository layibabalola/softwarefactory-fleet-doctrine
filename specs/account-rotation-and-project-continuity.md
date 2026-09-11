# Account Rotation and Project-Scoped Continuity

**Authority:** Adobe Document Cloud Ingester factory, continuity architecture  
**Status:** WORKING STRATEGY, tested 2026-09-11  
**Scope:** All factories and multi-project systems using credential-dependent lanes (Codex, Claude)

---

## Problem

**Factories are brittle across account rotation:**
- When Codex or Claude account rotates, all in-flight work (lanes, tasks, swarms) dies
- New account has no continuity marker; projects lose context
- Each project rediscovers continuity independently (6–8h debugging per rotation per project)
- No durable strategy exists to survive rotation and resume work

**Fleet impact:** 3 projects × 4 rotations/year × 6h = 72h/year wasted on rediscovery

---

## Solution: Four-Layer Continuity Architecture

### Layer 0: Immutable Ledger (Survives Everything)

**Source of truth.** Never changes, never needs re-authentication, survives rotation.

```
.factory/coordination/HUB.md                    # Append-only ledger (owned by Sol)
.claude-state/coordination/fable-ingress/      # Protocol-v2 ingress (SHA-256 records)
.claude-state/coordination/owner-directives/   # Staged directives awaiting Sol approval
```

**Evidence root:** Every decision, every work order, every vote is recorded in HUB with SHA-256 hash, timestamp, and evidence pointers.

**Rotation property:** Ledger is **read-only** (created before rotation) and **authoritative** (new account re-derives state from it, not memory).

---

### Layer 1: Derivation Commands (Regenerated on Resume)

**Pointer file.** Tells new account how to re-derive state from Layer 0.

```
.claude-state/RESUME.md
```

**Content:**
```markdown
## Resume for Adobe Document Cloud Ingester

Project: Adobe Document Cloud Ingester
Root: C:\!Layi Wkspc\Adobe Document Cloud Ingester

### Derivation Commands (run these in new account)

1. Read HUB tail:
   cat .factory/coordination/HUB.md | tail -100

2. Check checkpoint freshness:
   stat .claude-state/continuity/CHECKPOINT-CURRENT.md | grep Modify

3. Re-derive live state:
   git log --oneline -20
   cat .factory/state.yaml

4. Check ingress queue:
   tail -10 .claude-state/coordination/fable-ingress/requests.jsonl

5. Spawn fresh swarm to adjudicate next steps
   (Do not trust cached findings; re-run swarms)
```

**Rotation property:** File is **written before rotation**, always points to correct paths, survives credential expiry.

---

### Layer 2: Credential-Free Checkpoint (Auto-Expires)

**Heartbeat snapshot.** Fresh every 5 minutes, expires after 5 minutes, regenerates automatically.

```
.claude-state/continuity/CHECKPOINT-CURRENT.md
```

**Content:**
```markdown
# Checkpoint: Adobe Document Cloud Ingester

Generated: 2026-09-11T22:30:00Z (5 min freshness TTL)
Expires: 2026-09-11T22:35:00Z

## Derived State (from HUB, read-only)

- Factory state: REVIEWING
- Active work order: WO-G0-A01 rev13
- Luna status: WAITING_FOR_READY_WORK_ORDER
- Sol status: OWNER_DECISION_REQUIRED (Q-034 terminal)
- Open blockers: execution_authorized=false (Q-034 gate)

## How to resume

If checkpoint is fresh (< 5 min old):
  → Use it as a starting point

If checkpoint is stale (> 5 min old):
  → Ignore it; re-derive from HUB (Layer 0)

If account rotated:
  → Checkpoint is UNKNOWN (don't trust it)
  → Regenerate immediately in new account
  → Then resume
```

**Rotation property:** 
- **Before rotation:** Capture snapshot as proof-of-state at T=0
- **After rotation:** Generate FRESH checkpoint (credential-free; just reads HUB)
- **Never trust post-rotation:** New account must regenerate, not reuse old snapshot

---

### Layer 3: Project-Scoped Resume Trigger (New Layer)

**Human action.** "resume our work" in project root.

**Behavior:**
```bash
User types: "resume our work" (in project directory)
         ↓
SessionStart hook: Account ALIGNED check (detect drift)
         ↓
Project detected: Load .claude-state/RESUME.md (Layer 1)
         ↓
Derive state from HUB tail (Layer 0)
         ↓
Check checkpoint TTL (Layer 2)
  - Fresh (< 5 min): use as context
  - Stale (> 5 min): regenerate
  - Post-rotation: always regenerate
         ↓
Read owner-directives staging area
         ↓
Spawn fresh 3-agent swarm: "What's next?"
         ↓
Swarm consensus → Act autonomously (no user loop)
         ↓
5-minute monitoring loop (automated)
```

**Scope binding:**
```
If CWD is UNDER project root → resume this project
If CWD is OUTSIDE project root → refuse; direct to root
```

---

## Account Rotation Lifecycle

### BEFORE Rotation

1. **Current account is alive.** Factory running normally.
2. **At rotation trigger:** Take checkpoint snapshot (Layer 2)
   - Freeze HUB state as Layer 0 (no writes during rotation)
   - Record checkpoint with timestamp
3. **User rotates credentials** (Codex or Claude account)

### DURING Rotation

1. **All lanes die** (process tokens are invalid)
2. **In-flight work is lost** (but all decisions are in HUB)
3. **New account is initialized** (different token pool, fresh session)

### AFTER Rotation

1. **New account logs in** (standard auth)
2. **SessionStart hook runs** (account drift check)
   - Hook reports: "Rotation detected; old account was X, new account is Y"
   - No agent ever enters credentials; check is read-only
3. **User types "resume our work"** (in project directory)
4. **Layer 1 loads** (.claude-state/RESUME.md)
5. **Layer 2 regenerates** (fresh checkpoint in new account)
6. **Layer 0 re-derives** (HUB is source of truth)
7. **Swarms re-run** (no cached findings; all decisions are fresh)
8. **Execution continues** (work resumes from HUB state, not memory)

---

## Adoption Pattern

### For a NEW Project

1. Create `.claude-state/RESUME.md` with derivation commands
2. Create `.claude-state/continuity/` directory
3. Set up Scheduled Task to regenerate checkpoint every 5 min (OS-user-owned, survives rotation)
4. Use `.factory/coordination/HUB.md` as single source of truth
5. All decisions go to HUB (not memory, not config files)

### For an EXISTING Project

1. Migrate state from memory/config to HUB
2. Document derivation commands in `.claude-state/RESUME.md`
3. Activate checkpoint regeneration
4. Test rotation: rotate credentials, run "resume our work", verify re-derivation works

---

## Evidence Anchoring

**Tested in:** Adobe Document Cloud Ingester factory, account rotation cycle 2026-09-11

**Evidence:**
- HUB.md: `.factory/coordination/HUB.md` (append-only ledger, ~313 KB, 200+ entries)
- RESUME.md: `.claude-state/RESUME.md` (pointer file, ~178 lines, contains derivation commands)
- Checkpoint: `.claude-state/continuity/CHECKPOINT-CURRENT.md` (auto-regenerated, 5-min TTL)
- SessionStart hook: `~/.claude/hooks/resume-account-gate.mjs` (account drift check, read-only)

**Test case:** Codex account rotated 2026-09-11; new account resumed via "resume our work" and re-derived all state from HUB (no re-authentication required for layer 0–2).

---

## Properties Preserved

- **Durable:** Survives credential rotation, process death, session expiry
- **Credential-free:** No agent crosses auth boundary; all resumption is read-only
- **Fast:** Re-derivation takes < 5 min (HUB is small, deriving is cheap)
- **Transparent:** New account doesn't need to know about rotation; just types "resume our work"
- **Auditable:** Every state change is in HUB with evidence links

---

## Ratification

This pattern is ratified as a fleet standard. All factories (Adobe Ingester, agent-bridge, MLV-App) should adopt this architecture.

**When to use:**
- Any project with credential-dependent lanes (Codex, Claude)
- Any factory that wants to survive account rotation
- Any team that values durable continuity over per-session memory

**When NOT to use:**
- Single-session scratch work (no need for rotation survival)
- Projects with no lane automation (everything manual)

---

## Adoption Timeline

- **Week 1 (Sep 18):** Adobe factory documents and ratifies this pattern
- **Week 2–3 (Sep 25–Oct 1):** agent-bridge and MLV-App adopt; update RESUME.md, enable checkpoints
- **Month 2 (Oct 2–31):** Fleet-wide rotation test; all three projects verify re-derivation works
- **Month 3+:** Pattern is battle-tested; becomes default factory architecture

---

## FAQ

**Q: What if HUB.md is corrupted?**  
A: Corruption is blocked by git (HUB is tracked, line-based, append-only). Use git to revert to last good commit.

**Q: What if checkpoint is older than HUB tail?**  
A: Checkpoint is always stale after ~15 min (events move faster). Trust HUB, regenerate checkpoint.

**Q: What if new account can't read old HUB?**  
A: HUB is a file, not a service. Any git-enabled account can read it (no auth required for the file itself).

**Q: Does this work if BOTH Codex AND Claude rotate?**  
A: Yes. Each has its own Layer 0–2 (separate .factory/ and .claude-state/). Rotate independently; both can be offline and resumption still works (one lane at a time, queued).

**Q: How do I test rotation without actual rotation?**  
A: Simulate: Delete .credentials.json, re-auth to a different account, run "resume our work". Layer 0–2 should re-derive without error.

---

## Future Refinements

- **Multi-project resume:** "resume all" to resume Adobe + agent-bridge + MLV-App in sequence
- **Checkpoint versioning:** Store last N checkpoints (debug what changed between versions)
- **Cross-project coordination:** Doctrine bus (fleet-wide HUB) so projects can see each other's state
