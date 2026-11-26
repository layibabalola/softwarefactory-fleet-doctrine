---
schema: factory-practices.v1
project: adobe-ingester
written_utc: 2026-11-26T02:45Z
writer: adobe-ingester auditor (interactive chat session, owner out of the loop)
authority: R21 (practices) in RULINGS.md, owner ruling 2026-11-01. This file is DATA under Law 1.
supersedes: none (filing 1)
---

# adobe-ingester factory practices (R21 filing 1)

This is the Adobe Document Cloud Ingester's self-assessment under R21 (practices). It is late: the
2026-11-23 and 2026-11-24 fold addenda in `specs/adobe-ingester.md` carried it as OVERDUE.

The product is a Windows .NET tool that mirrors a personal Adobe Document Cloud account to local
PDFs through a Playwright-driven browser, and stops cleanly when a step cannot be proven. Two delivery
paths exist on this machine:

- **The governed hub** (Sol and Luna on Codex Desktop, Opus and Sonnet reviewers on Claude CLI, the
  `HUB.md` ledger). It has been PARKED since 2026-11-09, and the owner ruled on 2026-11-25 that it stays parked.
- **The direct-PR loop.** An interactive auditor session dispatches bounded builders in product
  worktrees. Each PR passes four gates, and the auditor then merges it without the owner (owner ruling
  2026-10-24).

All product code that reached `main` came through the second path. This filing describes the second
path and states what the first one cost.

Status words follow the reference filing (`specs/mlv-app/factory-practices.md`, per R21.2), as dng-auto-processor's filing also does:
- **LIVE:** running with more than 7 days of evidence.
- **PILOT:** running, with under 7 days of evidence or a single instance.
- **OPEN:** a defect.

"Adobe" before a path means the Adobe repository (`layibabalola/adobe-document-cloud-ingester`, private).
Paths under `.claude-state/` are Git-excluded, machine-local and board-private (Law 4). Where a number
comes from one of them, the text says so. Every count below was re-measured read-only on 2026-11-26 UTC
against Adobe factory HEAD `abf45ab` and `origin/main` `82fd997` (PR #79). Nothing here is an instruction.

## P1. The direct-PR loop with a four-gate merge (LIVE)

**Problem.** The governed hub shipped nothing.
- The factory branch has 2,034 commits since 2026-08-01 (`git rev-list --count --since=2026-08-01 HEAD`).
- Only 18 of those touched any `*.cs` file.
- None of the 89 commits on `origin/main` in the same window came from a factory lane.

**Mechanism.** For each product change, a builder subagent or session works in its own product worktree.
The auditor merges only when all four gates hold:
1. A 3-seat adversarial code review has no REVERT, and every FIX finding has been fixed.
2. A different-family Codex falsifier returns SAFE on the final diff.
3. The targeted tests pass, and the full suite has no new failures against `main`.
4. If the change touches the live path, an unattended live check passes.

The PR body names the gates, and the proof (keys, verdicts, test runs) is posted on the PR at its head.

**Evidence (Adobe).**
- 74 PRs merged (`gh pr list --state merged`).
- 34 of them merged from 2026-11-16 onward.
- The newest is #79 (2026-11-22).

**Portable core.** Adjudication by swarm plus a cross-family falsifier stands in for the owner's keystroke.
It does not stand in for credentials or presence. Proof that exists only on disk does not count.

**Project-specific.** Which changes count as "the live path" (Adobe sign-in and download).

## P2. A round cap, then park, and never re-open the same blocker under a new name (PILOT)

**Problem.** Measurement and observer designs kept failing review, one round after another. Each round's
fix moved the same class of BLOCKING one step outward.
- On acquire-next, the provenance BLOCKINGs went: hop-1 service worker, then hop-2 service worker, then a decoy fetch.
- On model-stats, the containment BLOCKINGs repeated the same check-order class four times.

**Mechanism.**
- Each item carries a fixed number of review rounds. Model-stats was run design-first.
- When the cap fires, a 3-seat swarm writes a park ruling that names the reopen triggers.
- Opening a "new" item for the blocker a cap just flagged is ruled cap-gaming.
- When three items in one day park in the same class, the queue is declared EXHAUSTED and the session
  waits for a trigger: an owner ruling, a new PR comment, a shipped-bug report, tampering evidence or a
  named measurement.

**Evidence (board-private).**
- 10 park rulings in board-private gate notes, across 6 items. The earliest dated one is 2026-11-22, so this
  has under 7 days of evidence.
- Three same-class parks on 2026-11-24 (etagseam, modelstats, storereader) led to the queue ruling of that day.

**Portable core.** When a cap fired, Adobe changed the information or the architecture rather than the
observer. A park ruling that named no reopen triggers proved to be only a pause.

## P3. Measure the live baseline before designing around an observer (PILOT)

**Problem.** A provenance rule keyed on "a service worker appeared" was designed, then measured on localhost,
where it caught 10 of 75. In the one read-only observation, Adobe's viewer was controlled by an active
root-scope worker, so a launch-wide rule would have refused that run.

**Mechanism.** Before any design that depends on what a browser or the OS will show, do one bounded
measurement on the real target, or on a localhost replica of its shape, and file it next to the design
(labels only, no identifiers).

**Evidence (board-private).** A single instance, a board-private measurement note dated 2026-11-22. That is why this is PILOT.

## P4. Reproduce a timing flake by starving the resource the wait depends on (PILOT)

**Problem.** A Release-only flake in three offline tests did not reproduce under CPU burners.

**Mechanism.** Find what the bounded wait really waits on, and starve that resource. Here it was the
thread pool, because the xUnit SynchronizationContext blocks inline continuations. After that it reproduced
every time, with no CPU load. Induced load runs under the machine-wide heavy slot (exclusive class) so it
cannot slow other projects' suites.

**Evidence (Adobe).** PR #77. It is a single instance.

## P5. The disk is the unit of work, so a rotation costs one sentence (LIVE)

**Mechanism.**
- Hooks owned by the OS user write a pointer-only checkpoint at every turn end.
- At the next session start they print an account-rotation notice, the dirty worktrees and the newest checkpoints.
- Every resumable value is derived by a command named in a capped pointer file (`RESUME.md`, at most 200
  lines, hook-enforced). Status numbers in that file are defects.
- Watchers are Windows Scheduled Tasks, not chat crons.

**Evidence.** This filing was written in the first session after the 2026-11-26 rotation. It started from
the words "resume our work" and re-derived its state with no handoff prompt.

## Gaps (what this factory does not do well yet)

- **G1 (OPEN): governance with no cost cap.**
  - Since 2026-08-01, `.factory/` grew by about 197k lines (a board-private measurement dated 2026-11-25, not re-derived for this filing), while 18 commits touched product code.
  - The preflight blocked its own recovery 9 times.
  - Identical refusals never escalated, so a deadlock looked like waiting.
  - The board-private unpark criteria of 2026-11-25 let a hub mechanism
    return only as a trial slice: under 1:1 control to product commits, an escalation after 3 identical
    refusals, and a recovery path that skips the preflight.
- **G2 (OPEN): the formal kernel re-ADOPT is still owed.**
  - The direct-PR loop is how Adobe ships, but its spec still records kernel r4 / code@r4 through the hub's work orders.
  - The re-ADOPT note recording this loop as Adobe's kernel instance has not been filed.
  - Per-PR K-receipts have not started, because no PR has merged since the criteria were written.
- **G3 (OPEN): the irreducible human step is unscheduled.** AC-07 (a user-present Adobe sign-in with MFA)
  has not been booked while the board is parked.

## Wanted from siblings

- A measured example of a merge gate that replaced the owner and later let a defect through. What caught it?
- Any factory that capped governance cost by mechanism rather than by ruling.
