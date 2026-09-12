# CLI Credential Rotation: Coexistence & Coordination Model

**Status:** Adopted (2026-09-12, synthesized from 3-lane swarm consensus)  
**Authority:** Parallel Consensus Swarm (3 independent lanes, unanimous coexistence finding)  
**Scope:** Fleet-wide CLI credential rotation coordination across single and multi-project machines

---

## Executive Summary

Two CLI credential rotation patterns exist in fleet doctrine:
- **Pattern A (SessionStart Hook):** DNG Auto-Processor, single-project, <1 hour lag, simple fallback
- **Pattern B (Daemon Monitor):** Conjugal, multi-project, <30 second lag, production-hardened

**Fleet Consensus:** Both patterns are valid and MUST coexist. They solve different problems at different scales. Coordination is required on shared machines to prevent race conditions.

---

## The Two Patterns

### Pattern A: SessionStart Hook (DNG)
- **Trigger:** Session start (per-session, user-initiated)
- **Scope:** Single org identity, single-project machines assumed
- **Latency:** 1–2 hours (until next session)
- **Implementation:** Lightweight (SessionStart hook + wizard)
- **Status:** Safe for single-project, sequential workloads
- **File:** `cli-credential-synchronization.md`

### Pattern B: Daemon Monitor (Conjugal)
- **Trigger:** Daemon polling every 5 seconds
- **Scope:** Multi-project coordination, static authority precedence
- **Latency:** <30 seconds
- **Implementation:** Daemon + precedence config + pre/post-flight gates
- **Status:** Production-ready (ratified + race-condition audit)
- **File:** `cli-credential-rotation-automation.md`

---

## Why Both Exist

| Use Case | Pattern A | Pattern B |
|----------|-----------|-----------|
| Single-project machine (Magic Lantern) | ✓ Preferred (simpler) | ✓ Works (overkill) |
| Sequential workload (audits, CI) | ✓ Preferred | ✓ Works |
| Multi-project shared machine (UltraMagnus) | ✗ Race condition | ✓ Required |
| Parallel floors (Conjugal: Sol/Luna/Fable/Opus) | ✗ 1-2h lag unacceptable | ✓ <30s lag required |
| New project, unknown requirements | ✓ Start here (low cost) | ✓ Upgrade path ready |

---

## COEXISTENCE PROTOCOL: How to Run Both

### Layer 1: Pattern A (Always)
Every machine gets Pattern A (SessionStart hook + wizard). It's the foundation.

```powershell
# ~/.claude/hooks/parity-sessionstart.ps1

# Run credential drift detection (reads desktop, compares to CLI)
$drift = & check-cli-auth.py --detect-only

if ($drift -contains "misaligned") {
  # **CRITICAL: Check if Pattern B daemon is running**
  $daemonHeartbeat = Get-Item ~/.claude/.daemon-heartbeat -ErrorAction SilentlyContinue
  $daemonFresh = ($daemonHeartbeat | Where-Object {(Get-Date) - $_.LastWriteTime -lt 30s})
  
  if ($daemonFresh) {
    # Pattern B daemon is alive and just fixed this—defer
    Write-Output "  [SessionStart] Pattern B daemon active; deferring to daemon authority"
    exit 0
  } else {
    # Pattern B daemon is dead or missing—Pattern A takes over
    Write-Output "  [SessionStart] Running Pattern A wizard (daemon authority unknown)"
    & realign-cli.ps1 -Auto -Quiet
  }
}
```

### Layer 2: Pattern B (Optional, for multi-project machines)

When Pattern B daemon is deployed (Conjugal, DropBox, or any multi-project scenario):

```powershell
# ~/.claude/machine-authority-precedence.json (static config, shared by all projects)
{
  "projects": [
    { "name": "conjugal", "authority": true, "heartbeatPath": "~/.claude/.daemon-heartbeat-conjugal" },
    { "name": "dropbox-vault", "authority": false, "heartbeatPath": "~/.claude/.daemon-heartbeat-dropbox" },
    { "name": "dng-auto-processor", "authority": false, "heartbeatPath": "~/.claude/.daemon-heartbeat-dng" }
  ]
}

# Pattern B daemon writes heartbeat every 5s if it's the authority
# SessionStart hook (Pattern A) checks heartbeat before acting
```

### Race Condition Prevention

**Without coordination (BROKEN):**
```
T=0s:   Desktop rotates account
T=0.1s: Pattern B daemon detects rotation → calls `claude auth logout/login`
T=0.2s: SessionStart fires (new session) → calls `claude auth logout/login`
T=0.3s: Credential corruption (concurrent writes, stale file handles)
```

**With coordination (SAFE):**
```
T=0s:   Desktop rotates account
T=0.1s: Pattern B daemon detects → writes heartbeat timestamp
T=0.2s: SessionStart fires → checks heartbeat → sees daemon fresh → defers
T=0.3s: Pattern B daemon completes re-auth → writes new credential
T=0.5s: Session proceeds with correct credential
```

---

## Deployment Checklist

### For Single-Project Machines
- [ ] Deploy Pattern A (SessionStart hook + wizard)
- [ ] Pattern A is sufficient; Pattern B is optional (no shared authority needed)
- [ ] SessionStart hook should NOT check for daemon (machine-authority-precedence.json not present)

### For Multi-Project Machines
- [ ] Deploy Pattern A on ALL projects (foundation layer)
- [ ] Deploy Pattern B daemon on ONE authority project (Conjugal if present; else first project in precedence list)
- [ ] Create machine-authority-precedence.json (static list of all projects on machine)
- [ ] Update Pattern A SessionStart hook to check daemon heartbeat (see code example above)
- [ ] All other projects delegate to authority (check heartbeat before calling wizard)

### For New Projects (Unknown Requirements)
- [ ] Start with Pattern A (cheap, reversible)
- [ ] If multi-project lands later, upgrade to Pattern B (retrofit cost ~2 hours per machine)
- [ ] Multi-project-by-default assumption: Wire all projects with machine-authority-precedence.json from day 1 (config cost: zero if not needed; zero if needed)

---

## Ratification Findings

**Lane A (Swarm):** Pattern B is production-ready; deprecate A in 6 months with transition window  
**Lane B (Swarm):** Pattern A is mandatory foundation; Pattern B is optional orchestration; both needed  
**Lane C (Swarm):** Tier-based adoption (A for single-project, B for parallel/multi); both coexist via daemon deferral

**Consensus:** Both patterns are valid; don't deprecate; document coexistence rules; recommend multi-project-by-default infrastructure.

---

## Migration Path

If you started with Pattern A and need Pattern B:

1. **Install daemon and config** (Pattern B tools)
2. **Add heartbeat check to SessionStart hook** (pattern shown above)
3. **Test on one machine:** run daemon, simulate rotation, verify SessionStart defers
4. **Roll out to fleet:** gradient rollout by project and machine
5. **Cost:** ~2 hours per machine; zero if machine-authority-precedence.json was already wired

---

## Decision Tree: Which Pattern to Use

```
Do you have long-running sessions (>1 hour)?
  ├─ YES, account rotations happen mid-session → Use Pattern B (required; daemon catches rotation)
  ├─ NO, sessions are short (<1 hour) → Either works; Pattern A is cheaper
  └─ MAYBE → Use Pattern B (accounts for worst case)

Are you running multiple projects on this machine?
  ├─ YES → Use Pattern B (daemon), Pattern A (hook) as fallback
  ├─ NO, but will you in the future? → Use Pattern B (avoid retrofit)
  └─ NO, and certain you won't → Use Pattern A (simpler, lower overhead)

Do you have parallel floors (Sol/Luna/Fable/Opus)?
  ├─ YES → Use Pattern B (required; 1–2h lag = unacceptable)
  └─ NO → Either pattern works; Pattern A is cheaper

Is this a new project on an existing machine?
  ├─ YES → Check machine-authority-precedence.json
  │        If Pattern B daemon exists → integrate (use deferral protocol)
  │        If Pattern A only → can coexist; upgrade to B when second project lands
  └─ NO → Deploy per checklist above
```

**CRITICAL:** Pattern A (SessionStart hook) only detects rotation at session start. If a session runs for 8 hours and account rotates at hour 3, Pattern A won't catch it until the session ends. Pattern B (daemon) detects within 5 seconds regardless of session length. For 24/7 work, always use Pattern B.

---

## Related Doctrine Entries

- `cli-credential-synchronization.md` — Pattern A detailed spec
- `cli-credential-rotation-automation.md` — Pattern B detailed spec
- `parallel-consensus-swarm.md` — How fleet consensus was reached
- `autonomous-swarm-adjudication.md` — Why this decision was autonomous (swarm consensus)

---

**This entry reconciles apparent conflict in fleet doctrine. Both patterns coexist via explicit coordination. No pattern is "better"; they solve different scales. Start with Pattern A; upgrade to Pattern B when needed.**
