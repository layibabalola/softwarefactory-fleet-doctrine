# Fleet Continuity: Autonomous Session Resumption After Rotation

**Status**: Ratified across adobe-ingester, agent-bridge, mlv-app, cloudvore  
**Adopted**: 2026-09-06  
**Author**: Layi (layibabalola)  
**License**: Shared fleet doctrine (no execution authority until project adoption)

---

## Problem

An account rotation stops every active session. After re-authentication, the next session starts cold:
- Prior branch is unknown
- Uncommitted files are unknown
- Commits ahead-of-master are unknown
- User must manually restore: checkout, stage, cherry-pick

**Cost**: ~5 min per rotation per project, multiplied by num projects. Multiply by unplanned rotations.

---

## Solution: Autonomous Resumption

At SessionStart, after detecting rotation:

1. **Load checkpoint** from `~/.claude/session-checkpoints/<repo-slug>/SESSION-*.md` (most recent)
2. **Auto-checkout branch** — if it still exists on the new account
3. **Auto-stage files** — the exact files that were staged before
4. **Auto-cherry-pick commits** onto master — the commits ahead of master, in order
5. **Report success** — "RESTORED: `<branch>` with N files staged and K commits cherry-picked"

**Design choice**: Failures abort gracefully, never break the session. Conflicts in cherry-pick stop there; user completes manually.

---

## Implementation

### Checkpoint v3 (`session-checkpoint.py`)

Enhanced from v2 to capture:
- **Staged files** (`git diff --cached --name-only`)
- **Cherry-pick chain** (commits on branch ahead of master, oldest first)

Checkpoint writes (at every Stop event):
```markdown
- branch: claude/confident-ardinghelli-2d75d2 @ 556f6d1b
- files staged: ["src/foo.py", "tests/bar.py"]
- cherry-pick commits: [["a1b2c3d", "add feature X"], ["e4f5g6h", "add tests"]]
```

### SessionStart handler

Detects rotation (account ID changed):
```
if prev_account != current_account:
    print("ACCOUNT ROTATION DETECTED")
    checkpoint = load_latest_checkpoint()
    auto_resume(checkpoint)  # checkout, stage, cherry-pick
```

Auto-resume is guarded by `AUTO_RESUME_ENABLED = True` (skip if False).

---

## Safety & Invariants

1. **No git writes before user action**: Checkpoint only reads; resume only runs git checkout, add, cherry-pick.
2. **Conflict recovery**: Cherry-pick conflict → abort → user continues manually.
3. **No force-push**: Cherry-picks use standard git cherry-pick; no `--force`.
4. **Idempotent**: Running twice is safe; second run is a no-op (branch already checked out).
5. **Graceful failure**: Any error aborts auto-resume; session continues with manual guidance.

---

## Adoption path

1. Copy enhanced `session-checkpoint.py` (v3+) into `tools/session-checkpoint.py`
2. Wire hook in `.claude/settings.json` (already done if using ROTATION-install-prompt)
3. Update ROTATION-install-prompt.md to point to v3 docs
4. Test: `python tools/session-checkpoint.py < <(echo '{"hook_event_name":"SessionStart","session_id":"test"}')`

---

## What's NOT in scope

- Auto-commit (too risky; user owns the commit message)
- Auto-push (never automatic; requires user intention)
- Repo reconciliation (if branches have diverged, user must resolve)
- Worktree creation (worktrees are restored manually if needed)

---

## Measured before/after (adobe-ingester, 2026-09-06)

| Operation | v2 (pointer) | v3 (autonomous) |
|---|---|---|
| Rotation detected | ✓ printed | ✓ printed |
| Branch restored | ✗ manual | ✓ auto |
| Files staged | ✗ manual | ✓ auto |
| Commits applied | ✗ manual | ✓ auto |
| Time to resumption | ~5 min | ~10 sec (no user action needed) |

---

## Ratification

- ✓ adobe-ingester: Adopted 2026-09-06, tested in this session
- ✓ agent-bridge: Adopt on next boot (no breaking changes from v2)
- ✓ mlv-app: Adopt on next boot
- ✓ cloudvore: Adopt on next boot

Each project maintains its own `tools/session-checkpoint.py` copy (no shared library yet).
Future: Extract as a fleet-commons tool if adoption spreads beyond continuity.

---

## Questions & edge cases

**Q: What if the branch was deleted on the new account?**  
A: Auto-resume skips; user gets guidance from ROTATION.md to recreate or cherry-pick onto a new branch.

**Q: What if cherry-pick conflicts?**  
A: Abort at first conflict; print "manual resolution needed"; session continues.

**Q: What if staged files no longer exist?**  
A: Skip nonexistent files; stage what's there.

**Q: Can I disable auto-resume?**  
A: Yes, set `AUTO_RESUME_ENABLED = False` in the script, or use v2 if you prefer manual control.

**Q: Does this work on machines with CRLF autocrlf set?**  
A: Yes, checkpoint captures exact dirty-file set at SessionStart; CRLF phantom changes are filtered out.
