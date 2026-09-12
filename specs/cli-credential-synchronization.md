# CLI Auto-Auth on Account Rotation

**Status:** Adopted (2026-09-12)  
**Authority:** User directive (seamless multi-account experience)  
**Scope:** Any machine with manual account rotation

## The Problem

When rotating the desktop account to a fresh org (e.g., budget exhaustion), the CLI credential store does not auto-follow. Users must manually run `claude auth login` to re-authenticate, or operations fail silently with "not authorized" errors.

## The Solution

Three hook + wizard components detect account drift at SessionStart and silently re-authenticate the CLI to match the desktop, requiring zero user intervention after a rotation.

## Components

### 1. Guard Gate (`~/.claude/hooks/parity-pretooluse-guard.ps1`)

Allow the wizard to run with `-Auto` flag (silent re-auth mode):

```powershell
# Line ~64, comment update:
# -DryRun / -Verify / -Auto must appear in THIS segment to earn the exemption.

# Line ~71, gate modification:
if ($t -notmatch '(?i)-DryRun|-Verify|-Auto') {
  $reasons += "blocked: the re-auth wizard was invoked without -DryRun/-Verify/-Auto..."
}
```

**Why separate:** The guard blocks credential mutations. Only the wizard script (by name) earns exemption when it carries a safe flag. `-Auto` is safe because it is non-interactive and runs only on explicit drift detection.

### 2. SessionStart Hook (`~/.claude/hooks/parity-sessionstart.ps1`)

Auto-trigger wizard on "CLI is on different account than desktop":

```powershell
# After drift detection, before printing manual commands:
$shouldAutoRun = ($drift -contains 'CLI is on a different account than the desktop')

if ($shouldAutoRun) {
  Write-Output "  AUTO-FIXING: Running CLI re-auth wizard (silent, no prompts)..."
  try {
    & $wiz -Auto -Quiet 2>&1 | Out-Null
    # Verify alignment restored
    $newStatus = ...
    if ($newStatus.orgId -eq $desktopOrg) {
      Write-Output "  ✓ CLI re-authenticated successfully and is now aligned."
    }
  } catch {
    Write-Output "  ⚠ CLI auto-re-auth error. Manual fix:"
    Write-Output ("       pwsh -File `"{0}`" -Interactive" -f $wiz)
  }
}
```

**Why at SessionStart:** Drift is checked before every session (via parity-sessionstart hook). Fixing it there means users never see "not authorized" errors downstream. The check is read-only until `-Auto` is passed, so cost is minimal.

### 3. Re-Auth Wizard (`coordination/tools/realign-cli.ps1`)

Implements modes:

- `-DryRun`: Print re-auth commands (read-only)
- `-Verify`: Re-check alignment after manual re-auth
- `-Interactive`: Walk through re-auth step-by-step (requires terminal)
- **`-Auto`**: Logout, login to target org, verify (no prompts)

The wizard:
1. Reads CLI's current org from `claude auth status --json`
2. Reads desktop's target org from `%APPDATA%\Claude\config.json` (allowlist keys)
3. Learns account email from `~/.claude/machine/account-email-map.json` (learned over time)
4. On drift, runs `claude auth logout` then `claude auth login --email <target>`
5. Re-reads CLI state and confirms alignment or reports the failure

## Deployment

**Per-machine setup (one-time):**

1. **Update guard** (1-line in parity-pretooluse-guard.ps1):
   ```powershell
   # Add | -Auto to the regex on line ~71
   ```

2. **Update SessionStart hook** (auto-run logic in parity-sessionstart.ps1):
   - Copy the `if ($shouldAutoRun)` block from the pattern
   - Replace the "FIX:" lines it prints

3. **Add wizard** to project (new file):
   ```
   coordination/tools/realign-cli.ps1
   ```

**Then:** Every session start automatically fixes CLI drift after a rotation. No further setup needed.

## Behavior

**Aligned case:**
```
SessionStart: [account-parity] OK - CLI and desktop both on org c96755fb
```
Session proceeds. No action.

**Drift detected, auto-fix succeeds:**
```
SessionStart: [account-parity] DRIFT DETECTED
  Desktop: c96755fb  darktravellersinfo@gmail.com
  CLI:     2a6cf04d  kidfob@gmail.com
  AUTO-FIXING: Running CLI re-auth wizard...
  ✓ CLI re-authenticated and is now aligned.
```
Session proceeds with CLI on correct account.

**Drift detected, auto-fix fails:**
```
SessionStart: [account-parity] DRIFT DETECTED
  ...
  ⚠ CLI auto-re-auth error: [reason]
  Manual fix:
    pwsh -File "..." -Interactive
```
Session proceeds (CLI is still misaligned). User can run `-Interactive` manually if needed.

## Prerequisites

- PowerShell (native Windows or pwsh 7+)
- Claude CLI (`claude` command on PATH or in `%APPDATA%\Claude\claude-code\*\claude.exe`)
- Desktop app running (for usage ledger to exist)
- Account email map optional (wizard learns emails on first login)

## Fail-Closed Principles

1. **Auto-fix only runs on explicit drift:** SessionStart detects alignment first. If aligned, wizard is never invoked.
2. **Auto-fix never overwrites user choice:** Only runs when CLI is on a *different* account than desktop, not when they disagree on which is "correct."
3. **Fallback always available:** If auto-fix fails, manual commands are printed so user can run `-Interactive` or type commands by hand.
4. **No secrets read:** Wizard never touches credential material; only credential *identity* (orgId, email).

## Edge Cases

| Case | Handling |
|---|---|
| First contact with new org | Wizard learns email via `-RecordEmail` flag or prints manual command with `--email` placeholder |
| Shared email (one person, multiple orgs) | Wizard prints which email it will use; user can override via `-RecordEmail` |
| CLI not found | Auto-fix skipped; manual fallback printed |
| Desktop org unknown | Auto-fix skipped; manual fallback printed |
| Login fails or hangs | Auto-fix times out after reasonable wait; manual fallback printed |

## Maintenance

- **Update wizard independently** if CLI auth flow changes (versioning at line 1)
- **Guard gates stay stable** (new flags added to pattern as needed, but gate logic unchanged)
- **Hook stays minimal** (only the auto-run trigger; real logic lives in wizard)

## Testing

Verify per-machine:

```powershell
# Test detection only (no mutation):
& "coordination/tools/realign-cli.ps1" -DryRun

# Test auto-fix (mutates CLI credential):
& "coordination/tools/realign-cli.ps1" -Auto

# Confirm alignment:
claude auth status --json
```

## References

- **User directive:** Seamless multi-account experience, no manual re-auth after rotation
- **Related:** `parity-sessionstart.ps1` (drift detection), `account-email-map.json` (learned identities)
- **Doctrine Law 1:** This is data (the pattern), not authority (lanes never write the bus)
