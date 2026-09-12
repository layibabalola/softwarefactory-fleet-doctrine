# Account Rotation & Resumption Strategy

**Status:** REFERENCE IMPLEMENTATION (AirMyPC)  
**Date:** 2026-09-11  
**Authority:** Swarm adjudication (Maximalist/Risk Manager/Logistics briefs); AirMyPC continuity audit  
**Scope:** All projects rotating accounts mid-stream without losing product/factory/fleet workstreams

---

## Why This Matters

Account rotation is imminent for many projects. A new account on the same machine should resume all three workstreams (product, software factory, fleet doctrine coordination) **without user input, without re-running finished work, and without losing governance history**.

This document defines:
1. **What survives rotation** (OS-user scoped vs. account-scoped)
2. **What must be verified before rotation** (seven load-bearing gates)
3. **How "resume our work" works on the new account** (five-step workflow)
4. **How to prevent false resumption** (state machine checks, worktree isolation)

---

## Part 1: Infrastructure Survival (What Lives, What Dies)

### **Survives Account Rotation (OS-User Scoped)**

These exist on the machine, independent of Claude account:

| Asset | Location | Scope | Survives? | Notes |
|-------|----------|-------|-----------|-------|
| Project root + source | `C:\temp\AirMyPC` (or project path) | OS-user, machine | ✅ YES | Git-tracked; works on any account on this OS user |
| Coordination ledger | `.claude-state/hub-20260710/` | OS-user, machine | ✅ YES | Gitignored but backed by OS-user; new account can read/append |
| Delivery queue | `docs/plans/DELIVERY_QUEUE.json` | Git-tracked | ✅ YES | Source of truth for all next steps; any account can read |
| Handoff files | `HANDOFF_RESUME_*.md`, `CLAUDE.md` | Git-tracked | ✅ YES | Project entry point; bootstrap pointer; survives rotation |
| Windows scheduled tasks | AirMyPC-ResumeHeartbeat (and others) | OS-user, machine | ✅ YES | Scoped to Windows user, not Claude account |
| Worktrees | `.claude/worktrees/airmypc-*` | OS-user, machine | ✅ YES | Tracked snapshots; can be restored or cleared |

### **Dies on Account Rotation (Account-Scoped)**

These are per-Claude-account and new account starts fresh:

| Asset | Scope | Survives? | Impact |
|-------|-------|-----------|--------|
| Session auto-memory | `~/.claude/projects/{sessionID}/memory/` | Per-account, per-session | ❌ NO | **Expected.** New account has zero memory. Not a loss; by design. Coordination lives in Git. |
| Lane leases | `~/.claude/lanes/` task store | Per-account | ❌ NO | Lanes are ephemeral (spin up, run, exit). Windows tasks trigger new ones. No data loss. |
| Auth tokens | `.credentials.json` | Per-account | ❌ NO | New account re-authenticates. No credential leakage. |
| CLI config | `~/.claude/config.json` | Per-account | ❌ NO | New account inherits settings; no drift. |

**Key insight:** Session memory dying is intentional. All durable state lives on disk (Git or OS-user `.claude-state/`), not in session volatiles.

---

## Part 2: Pre-Rotation Gates (Seven Load-Bearing Checks)

**All must be GREEN before new account touches product work.**

### **GATE 1: Repository State Integrity**

```powershell
git -C C:\temp\AirMyPC status --porcelain
# EXPECT: Empty (no output)
```

**Why:** Uncommitted work dies on fresh account (worktrees only include tracked files). New account cannot see dirty `.claude-state/` or source changes.

**Fix if RED:**
```powershell
# Commit everything to master
git -C C:\temp\AirMyPC add -p <paths>
git -C C:\temp\AirMyPC commit -m "docs(rotation): final state before account change"
git -C C:\temp\AirMyPC push host master && git push origin master
```

---

### **GATE 2: Handoff Currency (Derive, Don't Trust Dates)**

```powershell
# Run briefing on current account; confirm it exits 0 and names fresh handoff
pwsh -File C:\temp\AirMyPC\tools\Get-AudioMileResumeBrief.ps1
# Output field: activePacket (should match DELIVERY_QUEUE.json activePacket)
# Check: "CURRENT STATE" section in the handoff file is non-empty and dated within 3 hours
```

**Why:** Handoff files carry example hashes. Days later, those hashes are stale. New account must re-derive on day 1.

**Fix if RED:**
- Run Get-AudioMileResumeBrief.ps1 on current account now (updates checksums)
- Verify section names match (§1 CURRENT STATE exists)
- Push updated handoff to master

---

### **GATE 3: Opus Lane Availability**

```powershell
claude auth status --json | ConvertFrom-Json | Select-Object loggedIn, subscriptionType, orgId
# EXPECT: loggedIn: true, subscriptionType: "max" (or "premium" if renamed), orgId matches DESKTOP org
```

**Why:** P05a dispatch is "awaiting Opus lead". Without max tier, lanes don't spawn. New account often gets default tier on first provision.

**Fix if RED:**
- Contact Anthropic: "New account `<email>` needs to be provisioned on max tier before we can resume factory work"
- Wait for provisioning
- Re-check gate before proceeding

---

### **GATE 4: Doctrine Bus Sync (41 Commits Behind)**

```powershell
git -C C:\temp\AirMyPC fetch origin master
git -C C:\temp\AirMyPC rev-list --count master..origin/master
# EXPECT: 0 (no commits between local and remote)
```

**Why:** Doctrine bus has sibling commits (CloudVore patterns, Conjugal updates, fleet coordination). New account pulling stale HEAD may conflict.

**Fix if RED:**
```powershell
git -C C:\temp\AirMyPC fetch origin master
git -C C:\temp\AirMyPC rebase origin/master  # Rebase, don't merge (linearity preserved)
# Verify no conflicts in DECISIONS.md or .factory/* files
git -C C:\temp\AirMyPC push host master && git push origin master
```

---

### **GATE 5: Ledger Pointer Chain (CLAUDE.md → HANDOFF → §1 CURRENT STATE)**

```powershell
# Verify CLAUDE.md RESUME PROTOCOL names the right handoff
grep -A 5 "## RESUME PROTOCOL" C:\temp\AirMyPC\CLAUDE.md | grep HANDOFF

# Verify the handoff file exists
Test-Path C:\temp\AirMyPC\HANDOFF_RESUME_20260804.md

# Verify §1 CURRENT STATE exists and is not placeholder text
grep "## CURRENT STATE" C:\temp\AirMyPC\HANDOFF_RESUME_20260804.md
# Output should name the active packet, not say "TBD" or "placeholder"
```

**Why:** Pointer rot (renamed files, deleted sections) blocks all resumption. New account must be able to follow the chain without breaks.

**Fix if RED:**
- Update CLAUDE.md RESUME PROTOCOL to name the current handoff file
- Update the handoff's §1 CURRENT STATE with the active packet name and next act
- Commit and push

---

### **GATE 6: .claude-state/ Preservation (Cross-Machine Rotation Only)**

**Only applies if rotating to a different machine.**

```powershell
# On old machine, before retiring account:
robocopy C:\temp\AirMyPC\.claude-state\ C:\backup\AirMyPC\.claude-state\ /S /E

# On new machine:
robocopy C:\backup\AirMyPC\.claude-state\ C:\temp\AirMyPC\.claude-state\ /S /E

# Verify timestamps are recent (within 3 hours)
(Get-Item C:\temp\AirMyPC\.claude-state\coordination\DECISIONS.md).LastWriteTime
```

**Why:** `.claude-state/` is gitignored. It's irreplaceable (coordination ledger, decisions, board state, receipts). Loss = audit trail destroyed, lanes can ghost-respawn.

**Fix if RED:**
- Restore from backup
- If no backup: audit the ledger to find what's missing, manually re-enter key decisions and dates

---

### **GATE 7: Heartbeat Liveness State (Informational)**

```powershell
Get-ScheduledTask -TaskName AirMyPC-ResumeHeartbeat -ErrorAction SilentlyContinue | Select-Object State
# EXPECT: Disabled (per 2026-09-08 consolidation, or whatever the project's current rule is)
```

**Why:** If heartbeat is enabled AND .claude-state/ is stale, new account will ghost-spawn old tasks. Must be DISABLED until coordination is verified current.

**Fix if different:**
- If heartbeat should be enabled: verify .claude-state/ is current (GATE 6 passed); enable it
- If heartbeat should be disabled: disable it (one-liner: `Disable-ScheduledTask -TaskName AirMyPC-ResumeHeartbeat`)

---

## Part 3: Five-Step Resumption Workflow (New Account)

When the new account types **"resume our work"** (no bootstrap prompt), this workflow runs:

### **Step 1: Entry-Verify (Derive, Never Assume)**

```powershell
cd C:\temp\AirMyPC
git fetch host master && git fetch origin master
git rev-parse HEAD host/master origin/master
# EXPECT: one hash printed three times (HEAD, host/master, origin/master all equal)

git status --porcelain
# EXPECT: empty (clean tree)
```

**What it does:** Confirms the canonical tree matches both remotes and has no uncommitted changes.

**Risk if skipped:** A stale tree re-runs finished work or conflicts on merge.

---

### **Step 2: Derive Live State (Re-Computed Fresh, Never Cached)**

```powershell
pwsh -File tools/Get-AudioMileResumeBrief.ps1
```

**Output includes:**
- HEAD hash (matches host/master and origin/master? YES = GREEN)
- Ledger tail (newest entry [###], summary)
- Heartbeat age (minutes since last update; >30 = DEAD, no authority)
- Active packet from queue (name, state, owner, dependencies)
- Dependency readiness (all deps DONE? YES = can proceed; NO = wait)

**What it does:** Every call re-computes from raw state; nothing cached.

**Risk if skipped:** Inherited lane state (old seat leases, forgotten worktrees) masks ready work.

---

### **Step 3: Read Authority Sources (Queue + BOARD + DECISIONS)**

Read in this order:

1. **Delivery queue** (primary source of truth):
   ```powershell
   cat docs/plans/DELIVERY_QUEUE.json | jq '.items[] | select(.id == (.."activePacket"))'
   ```
   Output: `id`, `state`, `owner`, `nextAction`, `acceptance`, `phaseGate` (if any)

2. **BOARD dispatch** (if any exist for your seat):
   ```powershell
   tail -50 .claude-state/hub-20260710/BOARD.md | grep -A 10 "TO: <your-seat>"
   ```
   If found: your first act is that dispatch (overrides queue).

3. **DECISIONS rulings** (may override queue or BOARD):
   ```powershell
   tail -30 .claude-state/hub-20260710/DECISIONS.md
   ```
   If a ruling says "P05 PHASE_1 is PASS", unlock that gate.

**What it does:** Establishes authority hierarchy (queue > BOARD > DECISIONS tail).

**Risk if skipped:** A BOARD dispatch you miss breaks parity with the hub.

---

### **Step 4: Check Dispatch Gate (State Machine)**

Before executing the packet:

```powershell
# Confirm state
$packet.state -eq "IN_PROGRESS"  # Must be true

# Confirm dependencies
$packet.dependencyIds | ForEach-Object {
    $dependency = $queue.items | Where-Object { $_.id -eq $_ }
    if ($dependency.state -ne "DONE") { throw "Dependency $_ is not DONE" }
}

# If packet has a phaseGate, confirm it's unlocked
if ($packet.phaseGate) {
    $ruled = (Get-Content .claude-state/hub-20260710/DECISIONS.md | Select-String $packet.phaseGate -Context 0,2)
    if ($ruled -notmatch "PASS") { throw "Phase gate not passed yet; wait" }
}
```

**What it does:** Prevents premature dispatch (e.g., P05 pilot starting before P04 review lands).

**Risk if skipped:** P05 pilot bypasses its entry test, invalidating measurement baseline.

---

### **Step 5: Execute the Packet (Per RECOVERY_PLAN §4)**

**For product packets** (P01-P05, e.g., P05):
```powershell
# Create dedicated worktree
git worktree add C:\temp\AirMyPC-wi-P05 -b wi/P05 master

# Dispatch implementer (Opus lead + Haiku pilot for P05)
pwsh -File tools\Invoke-AudioMileLaneIgnition.ps1 `
  -Seat Haiku `
  -Worktree C:\temp\AirMyPC-wi-P05 `
  -PacketFile docs/plans/EXECUTION_PACKETS_20260907.md#p05 `
  -Execute

# Test: run the packet's acceptance test
cd C:\temp\AirMyPC-wi-P05
python tests/AudioMile.GateTests/UI/VolumeLabelConverterTests.cs  # Example test

# Review: spawn cross-family reviewer (Sonnet reviews Haiku work)
pwsh -File tools\Invoke-AudioMileReviewSpawn.ps1 -Worktree wi/P05 -Reviewer Sonnet

# Land: if review = APPROVE
git -C C:\temp\AirMyPC-wi-P05 rebase master
git -C C:\temp\AirMyPC merge --ff-only wi/P05
git -C C:\temp\AirMyPC push host master && git push origin master

# Cleanup
git worktree remove C:\temp\AirMyPC-wi-P05

# Record in ledger
git -C C:\temp\AirMyPC add docs/plans/DELIVERY_QUEUE.json docs/video-streaming/VIDEO_COORDINATION.md
git -C C:\temp\AirMyPC commit -m "docs(ledger): record [###] P05 Haiku implementation + Sonnet review (parity ✓, APPROVE)"
git push host master && git push origin master
```

**For factory packets** (F01-F05, e.g., F06 failover):
- Same recipe but different owner tier and acceptance criteria
- Phase 2 unlock: if P05a parity holds, P05b continuation items become eligible

**For doctrine/quality packets** (K01-K02, Q01-Q03, R01-R03):
- Lean tier (Haiku, bounded implementation)
- No cross-family review needed (informational work)
- Land to master directly (no worktree isolation required)

**What it does:** Implements work with isolation (worktree), reviews it (cross-family), lands it (both remotes), records it (ledger).

**Risk if skipped:** Shared canonical tree carries peer changes into your commit.

---

## Part 4: False Resumption Prevention (Concrete Checks)

| Scenario | Check | Audit |
|----------|-------|-------|
| "Q02a is done, but new account re-runs it" | `activePacket.state = "IN_PROGRESS"` gate check fails → item skipped | `git log --oneline \| grep "Q02a.*DONE"` confirms landing commit exists |
| "P05 lands before parity check" | `phaseGate: PHASE_1_ENTRY`; gate check finds no PASS ruling → STOP | `grep "P05.*PHASE_1.*PASS" DECISIONS.md` returns match or throws |
| "Two seats merge to same target" | Worktree isolation + pathspec-limited staging | `git status` in canonical before/after merge: only wi/P05 files appear |
| "Heartbeat stale; lane goes dark" | Heartbeat age >30 min = DEAD, no authority on state claims | `heartbeatAge` field in brief output compared to 30 |
| "Ledger entry double-counts work" | Ledger read is last 50 lines; entry is append-only; one [###] per landing | `wc -l VIDEO_COORDINATION.md` grows by exactly one heading per push |

---

## Part 5: Three Workstreams Advancing in Parallel

All three resume independently after rotation:

### **Workstream 1: Product (P01-P05 → P06+)**
- Gate: DELIVERY_QUEUE activePacket queue
- Owner: Opus lead (strategic dispatcher)
- Tier: Haiku (bounded pilot, P05a only); Sonnet (review)
- Landing: worktree → review → merge → ledger

### **Workstream 2: Factory (F01-F06 → governance iteration)**
- Gate: Phase gates (P05a baseline → P05b Opus independence → P05c Luna multi-provider)
- Owner: Codex lead (Sol, evidence audit)
- Tier: Opus (review key, cross-family validator)
- Landing: measurement schema fills with baselines; phase gates unlock

### **Workstream 3: Fleet Doctrine (K01-K02 → patterns published)**
- Gate: No cross-family review needed (patterns are informational)
- Owner: Any project (pub-sub model on fleet bus)
- Tier: Haiku (write patterns); Fable (fold existing contradictions)
- Landing: direct to softwarefactory-fleet-doctrine, no approval gate (law: doctrine is data, never instructions)

**All three are in DELIVERY_QUEUE.** New account reads the queue, sees all three, proceeds on independent gates.

---

## Implementation Checklist (Project Lead Before Rotation)

- [ ] GATE 1: `git status --porcelain` → empty
- [ ] GATE 2: Run `Get-AudioMileResumeBrief.ps1` → exits 0, handoff §1 is fresh
- [ ] GATE 3: `claude auth status` → `loggedIn: true, subscriptionType: "max"`
- [ ] GATE 4: `git rev-list --count master..origin/master` → 0
- [ ] GATE 5: CLAUDE.md RESUME PROTOCOL → names current handoff file; handoff §1 CURRENT STATE is not placeholder
- [ ] GATE 6: (cross-machine only) Backup `.claude-state/` to external drive or network path
- [ ] GATE 7: Verify heartbeat state matches project rule (usually DISABLED for now)
- [ ] Publish this strategy to fleet doctrine (so other projects adopt it)
- [ ] New account day 1: run all gates again (confirmation), then type "resume our work"

---

## Related Resources

- **MLV-App Primary Reference:** adoption/reference-factory-mlv-app-primary.md (process topology, heartbeat pattern)
- **Adobe Safety Patterns:** adoption/patterns-adobe-ingester-safety-first.md (cross-family review, hash-pinning)
- **Factory Selection Decision Tree:** adoption/decision-tree-factory-selection.md (which factory for your constraints)
- **Multi-Provider Orchestration Schema:** schemas/multi-provider-orchestration-v1.md (measurement gates, phase progression)
- **AirMyPC CLAUDE.md:** the project entry (START HERE for account-local projects; updated with account-rotation note)

---

**Next review:** Post-P05c (after account rotation happens in practice; gather learnings and refine gates)
