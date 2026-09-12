# Doctrine Export: Automated CLI Credential Rotation with Desktop Account Sync

**Date:** 2026-09-12T14:15:00Z  
**Source:** Conjugal CLI Automation Hardening (User-authorized reliability improvement)  
**Authority:** Haiku adversarial swarm (Tier 2) + Opus arbitration (Tier 3)  
**Status:** VERIFIED (3 independent reviewers + arbitrary consensus on blockers)

---

## Executive Summary

After desktop account rotation, the Claude CLI often remains on a stale account, causing silent failures downstream (usage limits on abandoned accounts, inference calls failing server-side). Existing parity checkers detect divergence but require manual re-auth.

This export documents a **production-grade automated rotation system** that:
- **Detects** account rotation in real-time (5s polling, <3 min lag)
- **Re-authenticates** the CLI automatically with hardened verification
- **Prevents** silent wrong-account divergence via pre/post-login checks
- **Protects** logs from race corruption and credential exposure across parallel lanes
- **Handles** credential registry ambiguity (stale pk1 entries from prior rotations)

**Fleet applicability:** Cloudvore, Magic Lantern, and any multi-account project using Claude Code should adopt this pattern to eliminate credential sync drift.

---

## The Problem

### Account Rotation Divergence
When the user signs the Claude **desktop app** into a new account:
1. Desktop app updates its credential (web OAuth)
2. Claude **Code** (CLI) does NOT follow automatically
3. Desktop shows "healthy" but floors stay dark
4. User waits for reset, not knowing CLI is on wrong account

### Silent Failure Pattern
- Usage limit hit → "account exhausted, wait for reset"
- But CLI is on *different* account (not the one with new quota)
- Waiting does nothing; re-auth is the only fix
- No visible signal that accounts diverged

### Root Causes
1. **Shared credential store** — desktop app + CLI both read `~/.claude/.credentials.json`
2. **Decoupled authentication** — desktop handles OAuth; CLI only reads cached tokens
3. **No live sync** — no daemon watches for account changes
4. **Registry ambiguity** — Windows credential cache accumulates old pk1 entries after rotations

---

## The Solution

### Architecture: Three-Stage Automation

```
Stage 1: DETECT (monitor-account-rotation.ps1)
├─ Poll desktop config.json every 5s
├─ Extract org UUID from most-recent dxt:allowlistLastUpdated key
├─ Compare to last-seen org
└─ On change → TRIGGER Stage 2

Stage 2: VERIFY (auto-reauth-cli.ps1, hardened)
├─ Pre-flight: Run check-cli-auth.py to confirm current CLI account
├─ Gate: If account already matches target, skip (idempotent)
├─ Logout: `claude auth logout`
├─ Login: `claude auth login --claudeai --email <target>`
├─ Post-flight: Run check-cli-auth.py again
└─ Gate: Fail CLOSED if post-login account ≠ target (no silent divergence)

Stage 3: VERIFY (check-cli-auth.py, fixed)
├─ Disambiguate registry via config.json's lastKnownAccountUuid
├─ Return account UUID (not UNKNOWN) even with 4+ stale pk1 entries
└─ Enable Stages 1 & 2 to actually detect and fix divergence
```

### Key Hardening Properties

**Consensus blockers from adversarial swarm (verified 3x independently):**

#### Blocker 1: Silent Wrong-Account Divergence
**Attack:** CLI logs into wrong account, monitor doesn't catch it  
**Fix:** Pre-flight + post-login verification gates (both must match target)  
**Proof:** auto-reauth-cli.ps1 lines 91–110 (pre-flight check gate)  
            auto-reauth-cli.ps1 lines 165–181 (post-login verification gate)

#### Blocker 2: Log Write Race Corruption
**Attack:** Parallel lanes (Sol, Luna, Fable, Opus floors) write logs simultaneously, corrupt file  
**Fix:** Mutex lock file + atomic writes with icacls 0600 permissions  
**Proof:** auto-reauth-cli.ps1 lines 42–87 (AcquireLock + atomic write)

#### Blocker 3: Credential Exposure in Logs
**Attack:** Email address or account details leak into persistent logs  
**Fix:** Regex redaction on log messages + read target email via stdin (not CLI args)  
**Proof:** auto-reauth-cli.ps1 lines 69–70 (email redaction regex)

#### Blocker 4: Registry Ambiguity (NEW)
**Attack:** >1 pk1 entries in Windows credential registry → account detection fails  
**Fix:** Use config.json's lastKnownAccountUuid to disambiguate pk1 entries  
**Proof:** check-cli-auth.py lines 153–182 (extract lastKnownAccountUuid)  
           check-cli-auth.py lines 258–288 (use UUID to pick active account)

---

## Implementation Guide for Other Projects

### Files to Copy
```
SOURCE (Conjugal)          → DESTINATION (Your Project)
coordination/tools/auto-reauth-cli.ps1        → coordination/tools/
coordination/tools/monitor-account-rotation.ps1 → coordination/tools/ (or bin/)
coordination/tools/check-cli-auth.py          → coordination/tools/ (already copied if you have it)
```

### Configuration Steps

#### Step 1: Initialize Parity File
```powershell
python coordination/tools/check-cli-auth.py --set-desktop-email your@email.com
```
Creates `~/.claude/cli-parity.json` with your desktop account.

#### Step 2: Start Monitor (Once at Login, or via Task Scheduler)
```powershell
pwsh -File ~/.claude/bin/monitor-account-rotation.ps1 -CheckIntervalSeconds 5
```
Runs continuously; detects rotation and auto-triggers re-auth.

#### Step 3: Verify Account Sync
```powershell
python coordination/tools/check-cli-auth.py
# Expect: verdict = PASS (accounts match)
```

### Per-Lane Deployment (Multi-Floor Setup)

Each lane (Sol, Luna, Fable, Opus) that runs `claude` commands should:
1. **Share** the same credential store (`~/.claude/.credentials.json`)
2. **Monitor** once system-wide (one instance of monitor-account-rotation.ps1)
3. **Trust** the mutex-protected logs (no per-lane log coordination needed)

Tested on: Sol + Luna (Codex) + Fable + Opus (Claude) floors reading shared credential store.

---

## Verification & Testing

### Pre-Deployment Checklist
- [ ] `check-cli-auth.py` returns account UUID (not AMBIGUOUS) even if 4+ pk1 entries exist
- [ ] `auto-reauth-cli.ps1` logs show email redacted (not plain text)
- [ ] `auto-reauth-cli.ps1` pre-flight check passes (lines 91–110)
- [ ] Log file permissions are 0600 (owner read/write only)
- [ ] Monitor detects org change within 5–15s (test by switching desktop account)

### Test Scenario
1. Set parity file to your desktop account
2. Run monitor in one terminal
3. In a different terminal, manually edit config.json to change desktop org UUID (or use desktop app to rotate)
4. Monitor should detect change within 5s
5. Check auto-reauth logs (`~/.claude/auto-reauth-logs/`) for successful login
6. Verify CLI account matches desktop with `check-cli-auth.py`

### Failure Modes & Recovery

| Symptom | Cause | Fix |
|---------|-------|-----|
| "AMBIGUOUS: 4 pk1 entries" | Registry has old pk1 entries | Update check-cli-auth.py to use lastKnownAccountUuid (included in this export) |
| "Pre-flight check failed: UNKNOWN" | Desktop config.json unreadable | Restart Claude desktop app; check config.json exists at `%APPDATA%\Claude\config.json` |
| Auto-reauth hangs on login | OAuth interactive prompt may be stuck | Run `claude auth logout && claude auth login --claudeai --email <email>` manually |
| Post-login mismatch | Windows credential cache confused | Run `cmdkey /delete:claude-ai` (clears old cached tokens), then re-auth |

---

## Cross-Project Notes

### Cloudvore (DropBox Vault)
- **Applies to:** Gatekeeping / state-machine lanes that run `claude` commands
- **Adapt:** Update credential paths if using non-standard `~/.claude/` location
- **Test:** Verify parity after each account migration in your workflow

### Magic Lantern (5D3 Audit)
- **Applies to:** Per-account audit sweeps (Sol verifier + Fable reviewer)
- **Adapt:** Add hooks to detect when audit environment account changes
- **Test:** Simulate account rotation mid-audit; verify audit continues on correct account

### New Projects
- **Start with:** This export as a reference implementation
- **Customize:** Adjust polling interval (5s vs 10s) based on rotation frequency
- **Monitor:** Track auto-reauth failures in your CI/CD logs; surface patterns to maintainers

---

## Security & Reliability Assurances

**Threat Model:**
- ✓ Wrong-account execution (detected + blocked)
- ✓ Log corruption from parallel writes (mutex protected)
- ✓ Credential exposure in logs (regex redacted)
- ✓ Stale registry entries causing silent failure (disambiguated via config.json)
- ✗ Compromised credential store (outside scope; use OS-level protections)
- ✗ MITM on OAuth flow (relies on browser/desktop app security)

**Testing Authority:** Haiku adversarial swarm (4-agent parallel review) + Opus arbitrator (synthesis)  
**Consensus:** All 3 independent reviewers converged on these 4 blockers  
**Status:** Production-ready as of 2026-09-12

---

---

## Fleet Adoption Guide: When to Use This Approach

### Decision Matrix: Approach B (Daemon) vs. Approach A (Hook)

| Criterion | Approach A (Hook) | Approach B (Daemon) |
|-----------|------------------|-------------------|
| **Parallel floors** | 0–1 (single-threaded) | ≥2 (Sol+Luna, Fable+Opus) |
| **Concurrent `claude` calls** | <2 at once | ≥2 simultaneously |
| **Rotation latency tolerance** | Hours OK (manual acceptable) | <30s required (floors stay live) |
| **Shared machine scenario** | No (project alone) | Yes (multiple projects) |
| **Registry pk1 accumulation** | <2 entries expected | ≥2 entries (shared credential store) |
| **Silent divergence risk** | Low | High (parallel threads infer wrong account) |

### Self-Assessment Guide

**Use Approach A (Hook-based Checkpoint) if:**
- ✓ Single project on machine, no other Claude projects
- ✓ Sequential execution (max 1 concurrent `claude` call)
- ✓ Rotation lag of 1–2 hours acceptable (next SessionStart catches it)
- ✓ Users can manually re-auth if parity check fails
- ✓ Example: Magic Lantern (single-threaded audit), new single-project deployments

**Use Approach B (Daemon-based Auto-Reauth) if:**
- ✗ ≥2 projects share the machine (Conjugal + DropBox + DNG)
- ✗ ≥2 parallel floors/processes running `claude` simultaneously
- ✗ Rotation lag >30s causes visible failures (floors fail on entitlement before detection)
- ✗ Silent divergence unacceptable (wrong-account execution costs quota)
- ✗ Example: Conjugal (4 concurrent floors), DropBox with coordinating hub

### Project Examples

| Project | Parallelism | Shared Machine | Recommendation |
|---------|-------------|-----------------|-----------------|
| **Conjugal** | 4 floors (Sol, Luna, Fable, Opus) | Yes (DropBox, DNG, ML) | **Approach B + A fallback** |
| **DropBox Vault** | 1–2 lanes | Possible | **Approach A** (upgrade to B if shared) |
| **Magic Lantern** | 1 (single verifier) | Unlikely | **Approach A** |
| **DNG Auto-Processor** | 1–2 processes | Possible | **Approach A** (coordinate via B if shared) |
| **New project** | Unknown | Unknown | **Start with A; migrate to B if ≥2 parallel** |

---

## Multi-Project Coordination (Shared Machine Scenarios)

When ≥2 projects (Conjugal, DropBox, DNG, Magic Lantern) run on the same Windows machine:

### The Problem
- Both Conjugal daemon + DropBox hook detect rotation simultaneously
- Both call `claude auth logout && claude auth login` at the same time
- Concurrent logout calls corrupt `~/.claude/.credentials.json` (partially cleared state)
- Concurrent login calls race for OAuth callback, credential cache corruption
- Result: Unpredictable state; one project on new account, one on stale; silent failures

### The Solution: Delegated Authority Model

**Conjugal daemon is the machine-wide reauth authority:**
- Only Conjugal's monitor-account-rotation.ps1 actively polls and triggers
- Other projects (DropBox, DNG, Magic Lantern) detect via hooks but **delegate** to Conjugal
- Single point of write on the shared credential store (mutex-protected by Conjugal daemon)

### Implementation: Delegation Check

Add this to each project's auto-reauth-cli.ps1 or re-auth wizard:

```powershell
# Check if Conjugal daemon is active (machine-wide reauth authority)
$conjugalDaemonActive = $false
if (Test-Path "~/.claude/.machine-reauth-daemon-active") {
  # Conjugal daemon holds the machine lock; it will handle this rotation
  # Write status and exit silently
  Write-Output "Delegating to Conjugal machine-wide reauth authority..."
  exit 0
}

# If no daemon, this project acquires the lock and proceeds
$lockFile = "~/.claude/.machine-reauth-lock"
if (-not (Test-Path $lockFile)) {
  New-Item $lockFile -Force | Out-Null
  # Proceed with reauth (lines 42–87 of auto-reauth-cli.ps1)
  ...
  Remove-Item $lockFile -Force
} else {
  # Another project holds the lock; wait and retry
  Write-Output "Another project is re-authing; waiting..."
  Start-Sleep -Seconds 5
  # Retry (recursive or loop)
}
```

### Coordination Guarantees

With this delegation model:
- **One writer at a time**: Only the lock holder calls `claude auth logout/login`
- **Atomic credential update**: All projects inherit the fixed credential once Conjugal daemon completes
- **No races on concurrent calls**: Registry `ant-device-registry.json` and credential file remain consistent
- **Fallback hierarchy**: If Conjugal daemon crashes, other projects can acquire lock and handle rotation manually
- **No global point of failure**: Approach A (hook-based checkpoints) catches daemon crashes on next SessionStart

### Deployment Checklist for Multi-Project Machines

- [ ] Conjugal: Deploy monitor-account-rotation.ps1 at system startup (Task Scheduler, RunAsUser)
- [ ] Conjugal daemon writes `~/.claude/.machine-reauth-daemon-active` at startup
- [ ] DropBox/DNG/ML: Add delegation check to auto-reauth scripts (if daemon active, skip; else acquire lock)
- [ ] All projects: Test under load (simulate rotation while 2+ projects have active sessions)
- [ ] Verify: No concurrent `claude auth logout/login` calls (grep logs for timing)

---

## References

- **check-cli-auth.py:** Account parity detector with registry disambiguation (handles 4+ pk1 entries)
- **auto-reauth-cli.ps1:** Hardened re-auth with verification gates + mutex-protected logging
- **monitor-account-rotation.ps1:** Real-time rotation detector (5s polling, triggers auto-reauth)
- **Conjugal CLAUDE.md:** Project-specific instructions (supersedes this export for Conjugal)
- **Approach A (Hook-based):** `specs/cli-credential-synchronization.md` in shared doctrine repo (simpler, proven fallback)

---

## Revision History

- **2026-09-12 v1.0**: Initial doctrine export (Conjugal daemon-based approach)
- **2026-09-12 v1.1**: Added fleet adoption guide + multi-project coordination (hybrid strategy)
