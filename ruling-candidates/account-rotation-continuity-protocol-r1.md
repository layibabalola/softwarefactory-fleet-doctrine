# Account Rotation Continuity Protocol — fleet adoption (R1)

**Proposed by:** agent-bridge, 2026-09-11
**Status:** adoption candidate (no runtime authority until project ratification)
**Evidence:** measured rotations at agent-bridge (2026-09-04), Adobe Document Cloud Ingester (2026-09-08), MLV-App (2026-08-09), DNG Auto Processor (2026-08-09), Conjugal (2026-08-09), DropBox Vault/Cloudvore (ongoing).

---

## The law

**Account rotation breaks the session boundary, not the project boundary. The disk is the unit of work.**

When an OS user rotates between Claude accounts (re-authenticates in Claude Desktop, CLI, or both):
- **Sessions die** with any Monitor, artifact watch, or loop armed inside them
- **The app's account-scoped scheduler empties** (org-scoped task registry in Claude Code), while on-disk task definitions persist
- **The OS-user-scoped disk survives** — worktrees, transcripts, `.claude-state/`, machine-local memory, OS-level scheduled tasks
- **Resumption is mechanical**: read an entry file that names derivation commands (never carries values), re-derive all state, dispatch the next step

---

## What each project must wire

Every project (Adobe Document Cloud Ingester, MLV-App, Conjugal, agent-bridge, DropBox Vault, etc.) establishes ONE **resumption entry file** in its canonical checkout.

### 1. Entry file location and content

**File path:** `<project-root>/.claude-state/RESUME.md` (gitignored, lives only in canonical checkout)

**Content structure** (pointer-only; zero perishable values):
- §0: one-line summary (your project, your words)
- §1: board/state derivation command (e.g., `pwsh -File .claude-state\coordination\Get-BoardState.ps1`)
- §A: procedure for "resume our work" (name the sections below in order; never add them inline)
- §B: freshness guard command (e.g., `pwsh -File .claude-state\coordination\Test-ResumeFreshness.ps1 -SelfTest`)
- Everything else: archive or demote to a subdirectory tagged `RESUME-HISTORICAL`

**Size cap:** 8 KB soft / 12 KB hard. Enforce with a project hook if needed.

### 2. Board state derivation script

Name a script that prints **machine-derived, read-only** state at the instant invoked:
- what seats/lanes are live (process check, not registration check)
- what work is blocked (read the ledger or WAL, not a memory file)
- what cards are READY (query the queue, not a cached list)
- which worktrees carry dirt or commits ahead of main (git, not cache)

**The script never reads "is warden running" from config; it checks the process table.**
**The script never reads "last rotation was at X"; it re-derives: `auth status --json | jq .accountId`.**

### 3. Resumption procedure (§A of entry file)

```
1. Read [project-kernel-or-laws file] — ratified rules, roles, how this project adjudicates
2. Run [board-state-derivation-script] — every value, read off disk at the instant you ask
3. Read [open-work-queue-or-cards-file] — READY cards; ignore DONE/BLOCKED
4. Take the next READY card; dispatch and ratify per [project-laws]
5. Report to the user — state, your next step, blockers. Then stop.
```

**That's it. Do not add prose descriptions of "what the board state was last time".**

### 4. Freshness guard (§B of entry file)

Name a command that exits 0 if:
- `RESUME.md` contains only procedures, addresses, and laws (no perishable values)
- The board-state derivation command exists and still runs
- The open-work-queue file exists

**The guard blocks a turn-end commit if the entry file has rotted.**

### 5. Mechanical handoff at every turn (optional but recommended)

Wire a project-level `Stop` hook (`~/.claude/settings.json` or `.claude/settings.local.json`) that writes:
```
~/.claude/session-checkpoints/<repo>/<session-id>.md
```

Content (pointer-only):
- session id, worktree path, branch, HEAD, account id
- the files this session dirtied and has not committed
- any next step (e.g., "waiting for OPUS review of PR #123")

This file survives rotation and lets the next session see where you stopped.

---

## What survives, dies, and breaks

| Category | Mechanism | Survives | Dies | Breaks |
|---|---|---|---|---|
| **OS-scoped state** | Worktrees, transcripts, `.claude-state/`, machine-local memory | ✓ | - | - |
| **Scheduled tasks** | OS-level (Windows Task Scheduler, cron, launchd) | ✓ | - | - |
| **App-scoped scheduler** | Claude Desktop scheduled-tasks registry, org-scoped | - | ✓ | Any watcher/automation using app-scoped tasks |
| **Session state** | Monitor, artifact watch, loop, in-memory edits | - | ✓ | Any entry-point that expects a session to still exist |
| **Seat leases** | A Claude session's claimed role/ownership | - | ✓ | Any handoff that requires a seat to persist; use the OS instead |
| **Codex Dark Lanes** | Codex Desktop seats (thread store) | - | ✓ | Codex-family automation (but Codex CLI can be re-authed separately) |

---

## Measurement gate

**Every project MUST measure continuity at project resume time, before deriving anything.**

Requirement: "within 90 seconds of 'resume our work', report board state"

How to verify:
1. Rotate accounts (or simulate: switch browser tab, re-auth Claude Desktop, then open CLI session in the checked-out repo)
2. In a fresh CLI session, navigate to the project root and invoke:
   ```bash
   time pwsh -NoProfile -File .claude-state/coordination/RESUME.md  # or whatever entry-file prose names
   time [board-state-command-from-RESUME]
   ```
3. Measure wall time to completion
4. If `>90s` or if the command fails: **continuity is broken**; fix the derivation before the project lands a doctrine amendment

**Why 90s?** That's the threshold a present human (waiting for a board printout) observes as "the system is responsive." Measurement is **wall time on the box**, not parse time — include git clones, script startup, and all I/O.

---

## Adoption checklist per project

- [ ] Canonical checkout has `.claude-state/RESUME.md` (or project's custom name) with no perishable values
- [ ] Run `[board-state-derivation-command]` and verify output within 90 seconds, machine-sourced (no memory)
- [ ] Run `[freshness-guard-command]` and verify exit 0
- [ ] Test rotation: new session, "resume our work", board state appears within 90 seconds (measure with `time`)
- [ ] Any OS-scoped automaton (wake floor, dead man, ignition ladder) uses OS Task Scheduler or cron, never app scheduler
- [ ] If using mechanical handoff checkpoints, verify `~/.claude/session-checkpoints/<repo>/` receives a new file at turn end
- [ ] Project's dispatched cards name their _next_ step (address, not description); handoff file is pointer-only

---

## Why this matters

**Measured failure class:** A board printed "all lanes live, ready to dispatch" after a rotation because it read a stale checkpoint file instead of deriving from the process table. The lanes were actually dead; the automation hung for 11+ hours.

**Root cause:** "configured != running" — a task persisting in the spec after the app erased it from the registry is registration-stale but definition-healthy, looks like success, and masks a dead lane.

**Remedy:** Make every resumption a derivation, not a lookup. If you need a fact the entry-file's derivation command does not print, add it to the command. Do not add it to the entry file.

---

## Exemptions and notes

- **New projects:** may start with an entry file that names manual steps (e.g., "1. git status, 2. read my last transcript, 3. take card X"). Automate the derivation as you learn what always needs checking.
- **Handoff files:** optional for projects with single-seat models; required for multi-lane factories (e.g., Adobe, MLV, agent-bridge).
- **CLI minted threads:** remain invisible in Codex Desktop until the Desktop updates its session index — this is a Codex Desktop behavior, not a project problem; design for it (post the thread id in your entry point).
- **Codex and Claude CLI are separate systems:** rotations break both; CLI re-auth is separate (run `claude auth status --json` before probing anything Codex-bound).

---

## Divergences expected

Projects may diverge on:
- Entry-file location (e.g., `coordination/RESUME.md`, `review/RESUME.md`, `roadmap/HANDOFF.md`)
- Board-state format (JSON, plain text, etc.)
- Freshness guard mechanism (hook, manual probe, etc.)
- Whether to use mechanical checkpoints (optional)

**Converge on:**
- Entry file carries procedures + addresses, zero perishable values
- Board state is DERIVED at read time, every time, not recalled
- Measurement is 90-second wall time
- OS-level scheduling for durable automata (never app-scoped)
- Handoff is pointer-only; next step is an address, not a narrative

---

## Fleet evidence (append-only)

- **agent-bridge (2026-09-04):** 11+ hour dark board from stale checkpoint vs actual process state. Fixed by RESUME.md entry file + Get-BoardState.ps1 derivation. Measured: 2s board derivation, cold.
- **Adobe Document Cloud Ingester (2026-09-08):** account rotation emptied app-scoped task registry while on-disk specs persisted. Sol lane stayed "configured" while execution never fired. Moved all wake floors to OS Task Scheduler.
- **MLV-App (2026-08-09):** same app-scheduler wipe on same rotation. Adopted OS-level wake floor (heartbeat) + derived board state from live process table instead of spec.
- **DNG Auto Processor (2026-08-09):** migrated task to OS scheduler; old "verified firing by lastRunAt" proof did not travel with the task. Re-derive proof from the NEW host's state after migration.
- **Conjugal (2026-08-09):** first fleet convergence on mechanical checkpoint hook + pointer-only handoff file. Single-writer per lane, resumable within two sentences.
- **DropBox Vault/Cloudvore (ongoing):** established project-local `review/RESUME.md` entry point; measurement pending (target 90s, current status unknown).

This is the pattern all projects converged on independently before a single name existed for it. This amendment names it and ratifies adoption.

---

## References

- Trap evidence: `softwarefactory-fleet-doctrine/TRAPS.md` — org-rotation registry wipe (agent-bridge, adobe, mlv, dng)
- Trap evidence: "A migrated task inherits the OLD host's proof" (DNG)
- Ruling precedent: "Machine-scoped wake floors" (MLV-App, 2026-08-09)
- Ruling precedent: "Configured != running" (all projects, converged)
- Ruling precedent: "READ-TIME VERIFICATION" (DNG + agent-bridge, 2026-08-09)

---

## Decision required from each project's hub/leadership

- **ADOPT** — wire this entry-point structure verbatim, customize location/commands as needed
- **DISTINGUISH** — name your divergence and record it in your project spec (e.g., "we use threads instead of processes for liveness check"; explain why)
- **REJECT** — name your reason and append to this file so the next project learns why

Each project's adoption is a pull request to this repo with the decision appended to this file. **No runtime authority until adopted.**
