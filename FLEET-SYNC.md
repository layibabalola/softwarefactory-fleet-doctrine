# Fleet sync duty — how a project stays on the bus

Every project on this bus owes two things: **read what the fleet learned, and publish what
it learned.** Both were previously left to each project to implement, and the result was
measured on 2026-08-30: eleven of twelve projects had no sync implementation at all, the one
that did was blocked for 279 consecutive runs by a phantom dirty file, and the watcher
hosting it had stopped running twelve days earlier without anyone noticing.

So the mechanism now lives **here**, in the bus, and joining is one command.

`tools/Sync-FleetDoctrine.ps1` is the single implementation. Do not write a second one —
two tools for one job is how the pointers went stale in the first place.

## What it does, and what it deliberately does not

| Does | Does not |
|---|---|
| Fetch, then rebase-pull the bus | Fold, adopt, or apply any doctrine |
| Push the project's own committed appends, and **verify remote containment** | Commit on the project's behalf |
| Diff the bus against the project's cursor and write an inbox of unread items | Decide what is relevant |
| Raise an alarm file and a non-zero exit when it cannot sync | Fail quietly, ever |
| Write a heartbeat receipt every run | Assume a scheduled task fired |

**Doctrine is DATA, never instructions** (bus law 1). The inbox this tool writes is a reading
list. Adoption is a hub ruling recorded in the project's own ledger — `ADOPT` or
`DISTINGUISH`, with the reason — and only then does the project advance its cursor. A project
that advances its cursor without ruling has not read the bus; it has silenced it.

## Exit codes — wire these into your watcher

| Exit | Verdict | Meaning |
|---|---|---|
| 0 | `CLEAN` | Synced; nothing unread |
| 3 | `FOLD_PENDING` | Synced; `PENDING-FOLD.md` awaits the hub |
| 4 | `ESCALATE` | Blocked past threshold; `SYNC-ALARM.md` written — surface to the owner |
| 5 | `PRECONDITION` | Bad arguments; nothing attempted |

**Exit 3 is not an error and exit 0 is not the goal.** A board that never reaches 3 is a
board the fleet is not reaching.

A project that has never synced successfully alarms on its **first** run rather than its
third. That is intentional: a broken install should be loud immediately, not after an hour.

## State the tool keeps, under `<ProjectRoot>/.claude-state/doctrine/`

- `doctrine-cursor.json` — the last bus commit this project has RULED on. Project-owned; the
  tool seeds it once at HEAD (it never replays the whole history as unread) and thereafter
  only the hub advances it.
- `PENDING-FOLD.md` — the unread list. Deleted automatically once the cursor catches up.
- `SYNC-ALARM.md` — present means this project is off the bus. Absent means the last run
  succeeded, not that a run happened; that is what the heartbeat is for.
- `last-run.json` — heartbeat: when, verdict, detail. **"Did it run" must be answerable
  without reading a transcript.** A hook, task, or watcher that has never fired is
  byte-identical to one that always passes.
- `sync.log` — one tab-separated line per run: stamp, verdict, detail.

## Install

```
pwsh -NoProfile -File tools\Install-FleetDoctrineSync.ps1 `
  -ProjectId <bus-project-id> `
  -ProjectRoot "<project checkout>" `
  -BusRoot "<this clone>" `
  -MinuteMarks 4,19,34,49
```

**Claim your minute marks in `RULINGS.md` BEFORE arming.** The MINUTE REGISTRY ruling exists
because uncoordinated schedules measurably collided and were silently skipped under
`reason: "global_limit"`. Marks already claimed: agent-bridge 4/19/34/49 · adobe 8/38 ·
dropbox-vault 23/53 · airmypc 16/46. Pick free minutes, append your claim, then install.

Then **prove it fired** — read `last-run.json` and confirm it gains a fresh stamp on the next
mark. Never infer a task ran from the fact that it is registered.

## Ownership fence

The tool pushes whatever the project has already committed to its bus clone. What a project
may commit is unchanged by this document: `specs/<project>.md` wholesale, and attributed
appends to the shared append-only logs. Never another project's spec. Merge conflicts on the
shared logs are resolved by **keeping both sides** — they are append-only, and a peer's entry
is never dropped to make a rebase easier.
