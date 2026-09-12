# Multi-Project Credential + Continuity Adoption Checklist

**When:** Before deploying a SECOND project to a shared machine (e.g., DropBox to UltraMagnus after Conjugal is already running)

**Why:** Static precedence config and project-scoped state files must be in place BEFORE concurrent projects try to rotate credentials. Without them, race conditions on `~/.claude/.credentials.json` will cause credential corruption and silent divergence.

**Scope:** Applies when deploying both:
- `specs/cli-credential-rotation-automation.md` (machine-level daemon coordination)
- `specs/account-rotation-and-project-continuity.md` (project-level state preservation)

---

## Pre-Deployment Checklist

### Phase 1: Machine Configuration (MUST COMPLETE BEFORE 2ND PROJECT STARTS)

- [ ] **Create machine authority config**
  ```bash
  cat > ~/.claude/machine-authority-precedence.json <<'EOF'
  {
    "version": "1.0",
    "machines": {
      "UltraMagnus": ["dropbox", "dng", "magic-lantern"],
      "Bachelor": ["conjugal"],
      "default": ["conjugal", "dropbox", "dng", "magic-lantern"]
    },
    "authority_heartbeat_interval_sec": 5,
    "authority_heartbeat_timeout_sec": 30,
    "fallback_wait_retries": 5,
    "fallback_wait_interval_sec": 5
  }
  EOF
  ```
  **Check:** Precedence list matches actual project deployment order for this machine

- [ ] **Document account-to-project mapping** (if machine will host multiple accounts)
  - Example: "UltraMagnus: Account A (DropBox), Account B (DNG), Account C (Magic Lantern)"
  - This informs parity file strategy (see next item)

- [ ] **Parity file strategy (choose based on account count)**
  - **Single account:** Use `~/.claude/cli-parity.json` (existing approach)
  - **Multiple accounts:** Use per-account `~/.claude/cli-parity-<ACCOUNT>.json` and store account UUID (not email)
  - **Reason:** Email is not unique across accounts; UUID from desktop config.json is the only reliable identifier

### Phase 2: Per-Project Setup (BEFORE STARTING EACH PROJECT)

- [ ] **Copy coordination files to project**
  ```bash
  cp coordination/tools/auto-reauth-cli.ps1 <new-project>/coordination/tools/
  cp coordination/tools/monitor-account-rotation.ps1 <new-project>/coordination/tools/
  cp coordination/tools/check-cli-auth.py <new-project>/coordination/tools/
  ```

- [ ] **Initialize parity file for this project's account**
  ```bash
  python coordination/tools/check-cli-auth.py --set-desktop-email <account>@example.com
  ```
  **For multi-account machines:** Also set account UUID in parity file manually (or extend check-cli-auth.py with `--set-account-uuid` flag)

- [ ] **Start daemon (only for authority project)**
  ```bash
  pwsh -File coordination/tools/monitor-account-rotation.ps1 \
    -CheckIntervalSeconds 5 \
    -ProjectName "dropbox"  # Must match precedence list entry
  ```
  **Check:** Only ONE project's daemon should run on the machine at a time (elected by precedence list)

- [ ] **Non-authority projects register delegation check**
  - Add static delegation check to auto-reauth-cli.ps1 (code in CLI rotation spec)
  - Verify: non-authority projects check heartbeat before attempting re-auth

### Phase 3: Continuity Integration (IF ADOPTING ADOBE PATTERN)

- [ ] **Create `.claude-state/RESUME.md` with derivation commands**
  - Include step to check `rotation-state-<PROJECT>.json` freshness
  - If fresh (< 30s old): Trust credential; proceed to re-derive from HUB
  - If stale: Run `check-cli-auth.py --allow-live-probe` to verify credential state

- [ ] **Activate checkpoint regeneration (5-min cycle)**
  - Scheduled Task: `pwsh -File generate-checkpoint.ps1` every 300 seconds
  - Checkpoint reads `rotation-state-<PROJECT>.json` to detect recent rotation
  - If rotation marker exists: Invalidate cached credential; re-derive

- [ ] **SessionStart hook deference (if multi-project)**
  - Modify SessionStart hook to check daemon heartbeat freshness
  - If heartbeat < 30s old: Skip parity check (daemon is handling rotation)
  - If heartbeat stale or missing: Perform parity check as normal

### Phase 4: Testing (BEFORE FLEET-WIDE ROLLOUT)

- [ ] **Isolation test: Multi-project credential independence**
  - Prerequisite: Both projects are running on shared machine
  - Action: Rotate Account A's desktop app to Account A'
  - Verify: 
    - [ ] Only Account A's project daemon detects rotation
    - [ ] Account B's project does NOT attempt re-auth
    - [ ] Credential is updated atomically (all projects see same new state)
    - [ ] No partial-write corruption in `~/.claude/.credentials.json`

- [ ] **Daemon failover test: Authority crash recovery**
  - Prerequisite: DropBox daemon is authority on UltraMagnus
  - Action: Kill DropBox daemon process
  - Verify:
    - [ ] DNG daemon detects fresh heartbeat missing (within 30s timeout)
    - [ ] DNG daemon acquires lock and becomes temporary authority
    - [ ] Daemon completes re-auth
    - [ ] `rotation-state-dng.json` written with `rotation_complete_marker: true`
    - [ ] DropBox resumption does NOT re-trigger re-auth (honors stale marker)

- [ ] **Credential handoff test: Daemon → floors**
  - Prerequisite: Conjugal is running with daemon + continuity
  - Action: Rotate desktop account
  - Verify:
    - [ ] Daemon detects rotation within 5s
    - [ ] Daemon calls `claude auth logout && login`
    - [ ] Daemon writes `rotation_complete_marker: true` to `rotation-state-conjugal.json`
    - [ ] Sol floor resumes; checks `rotation_complete_marker` before re-deriving
    - [ ] Sol does NOT call `check-cli-auth.py` if marker is fresh and heartbeat is live
    - [ ] No redundant re-auth

- [ ] **Hook coordination test: SessionStart + daemon race**
  - Prerequisite: Both daemon and continuity are active
  - Action: Rotate account; immediately trigger "resume our work" in new session
  - Verify:
    - [ ] SessionStart hook detects daemon heartbeat is fresh
    - [ ] SessionStart hook skips parity check
    - [ ] Floors proceed to re-derive from HUB
    - [ ] No false positives on "account drift detected"

- [ ] **Load test: Multiple floors + daemon under concurrent rotation**
  - Prerequisite: Conjugal (4 floors) + DropBox (2 lanes) on UltraMagnus
  - Action: Rotate desktop account while all floors have active processes
  - Verify:
    - [ ] Daemon detects rotation once
    - [ ] All floors eventually re-sync (no divergence between floors)
    - [ ] No duplicate re-auth calls
    - [ ] No credential corruption in `~/.claude/.credentials.json`
    - [ ] Usage accounting is correct (each project's capacity tracked separately)

### Phase 5: Rollout (AFTER ALL TESTS PASS)

- [ ] **Document machine-specific config in DISCOVERIES.md**
  ```markdown
  ## UltraMagnus (Multi-Project Machine)

  - Projects: DropBox (Account A), DNG (Account B), Magic Lantern (Account C)
  - Authority: DropBox (first in precedence)
  - Parity strategy: Per-account UUID-based
  - Tested: 2026-09-12 (isolation, failover, handoff, load)
  - Receipt: <git-sha-of-test-results>
  ```

- [ ] **Commit test results + config to doctrine repo**
  - Commit: Machine config + test receipt
  - Message: "Adopt multi-project credential continuity on UltraMagnus (tested 2026-09-12)"

- [ ] **Enable continuous monitoring**
  - Watch daemon logs for rotation detection lag
  - Watch `rotation-state-*.json` timestamps for stale markers
  - Alert if heartbeat is missing for > 30s (daemon crash)

---

## Troubleshooting

### Symptom: "AMBIGUOUS: 4 pk1 entries" on second project

**Cause:** Windows credential cache has stale pk1 entries from prior rotations  
**Fix:** See `cli-credential-rotation-automation.md` blocker #4 (registry disambiguation via config.json lastKnownAccountUuid)

### Symptom: Daemon takes authority on wrong project

**Cause:** Precedence list order is wrong; wrong project has heartbeat file  
**Fix:** Check `~/.claude/machine-authority-precedence.json`; verify machine entry matches `$env:COMPUTERNAME`

### Symptom: SessionStart hook still performs parity check even when daemon is alive

**Cause:** Hook was not updated with heartbeat deference check  
**Fix:** Add heartbeat freshness check to hook (see Phase 3 above)

### Symptom: Credential corruption (partial writes, mixed-state)

**Cause:** Lock acquisition is not atomic (using `New-Item -Force` instead of `File.Create`)  
**Fix:** Verify CLI rotation spec §3 implements atomic lock via `[System.IO.File]::Create()`; never use `New-Item -Force`

---

## Success Criteria

✅ Multi-project deployment is **ready when**:
- [ ] Machine config is in place (precedence list, account mapping)
- [ ] All isolation tests pass (no credential corruption)
- [ ] All load tests pass (4+ concurrent floors + 2+ projects)
- [ ] Daemon failover works (authority hand-off in < 30s)
- [ ] Handoff boundary works (daemon finish → floors wake cleanly)
- [ ] Hook coordination works (SessionStart defers to daemon)
- [ ] Test receipt is committed to repo
- [ ] Fleet peers have reviewed (or autonomy consensus authorizes deployment)

---

## Related Specs

- `specs/cli-credential-rotation-automation.md` — Machine-level daemon coordination
- `specs/account-rotation-and-project-continuity.md` — Project-level state preservation
- `specs/autonomous-decision-making-with-adversarial-swarms.md` — Governance pattern for adoption decisions

---

## Version History

- **2026-09-12 v1.0**: Initial checklist (Haiku swarm audit)
  - Multi-project coordination, isolation testing, daemon failover
  - Derived from Conjugal + Adobe Ingester experience
