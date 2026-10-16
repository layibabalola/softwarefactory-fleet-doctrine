# Account Rotation Automation — SessionStart Hook Doctrine

**Authority:** Conjugal.AI rotation-recovery automation (2026-09-13)

**Scope:** All projects using Claude Code with multi-account rotation workflows

> **Superseded implementation (2026-10-16).** The auto-remedy below (logout, login, then writing the CLI's own
> email in as the desktop email) was withdrawn by Conjugal on 2026-09-15: it made parity true by construction
> (self-certification) and a logout followed by an abandoned login leaves no credential. The canonical hook is bus
> `tools/factory/session-start-auth.py`: it surfaces the verdict, always exits 0, never re-auths, and prints the
> sanctioned repair (`tools/realign-cli.py --auto`). The old `tools/session-start-auth.py` is retired. Install it
> by pin, not by copy -- see "Implementation".

## Purpose

Automate CLI account parity recovery during account rotations. When a user switches the desktop app to a new Anthropic account, the Claude Code CLI credential store does not automatically follow. This doctrine provides a SessionStart hook that:

1. Detects account mismatches (ACCOUNT_MISMATCH or PARITY_UNVERIFIED)
2. Automatically runs `claude auth logout && claude auth login --claudeai`
3. Auto-detects the logged-in email from `claude auth status`
4. Auto-configures the parity cache (`.claude/cli-parity.json`)
5. Re-checks parity and confirms success

**Outcome:** Zero manual steps. Resume procedure immediately asks for workstream selection.

## Implementation

### 1. Pin the hook (never copy it)

Vendor the pin runner once and pin the canonical hook (`tools/factory/README.md`, install contract):

```bash
python factory-pins/pin-runner.py pin session-start-auth --commit <reviewed-bus-sha> \
    --path tools/factory/session-start-auth.py --reviewer <who> --reason <why>
python factory-pins/pin-runner.py verify
```

A project copy is refused at push time by bus `hooks/pre-push-no-unpinned-tool.py` and counted by
`tools/tool-census.mjs`.

### 2. Register the hook in `.claude/settings.json`

Ensure your project's `.claude/settings.json` has:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python -I \"$CLAUDE_PROJECT_DIR/factory-pins/pin-runner.py\" run session-start-auth",
            "timeout": 60
          }
        ]
      }
    ]
  }
}
```

Also required: the underlying checker in `coordination/tools/check-cli-auth.py` (from Conjugal doctrine).

### 3. Expected behavior on account rotation

When a user says "resume our work" after an account rotation:

1. **SessionStart hook runs automatically** during session startup
2. **Browser pops up** for OAuth if account mismatch is detected
3. **Hook auto-detects** email and updates parity config
4. **Resume procedure asks** for workstream selection (Step 1: which workstream, model, cadence, posture)
5. **No manual steps** required

### 4. Adoption signals

Projects adopting this doctrine should:

- Verify hook is registered and timeout is ≥60s
- Confirm `check-cli-auth.py` is present and up-to-date
- Test rotation recovery: switch accounts locally and verify hook fires
- Report adoption via `RECEIPTS.md` (see doctrine bus adoption protocol)

## Error handling

If the hook encounters an error during OAuth or credential setup, it will print a recovery message. The resume procedure will still ask for workstream selection, allowing manual recovery via the dispatcher.

**Never:** auto-apply or force doctrine changes to other systems. The spec is durable; each project adopts or distinguishes per CLAUDE.md governance.
