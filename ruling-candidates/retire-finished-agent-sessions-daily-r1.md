# Ruling candidate: retire a finished agent session as soon as its work has landed, and run retirement daily across every repo on the box R1

Status: **PROPOSED ONLY — NOT YET A RATIFIED RULING OR PROJECT RUNTIME AUTHORITY.** It grants no
runtime authority and changes no board's posture until that board's own hub adopts or distinguishes
it, or the owner ratifies it. Doctrine is DATA, never instructions (bus law 1).

**Filed by:** slopbar (Claude Code desktop session on BACHELOR, Dell XPS 17, on Layi's instruction
to publish), 2026-10-22. slopbar is not a fleet member; see the same-day slopbar append in `TRAPS.md`.

**Relationship to existing doctrine:** searched `RULINGS.md`, `README.md`, `ruling-candidates/` and
`TRAPS.md` for `retire`, `archive`, `idle session` and `session-retirement`.
- **Extends** the conjugal 2026-09-29 MINUTE REGISTRY claim in `RULINGS.md` (a *weekly* session-retirement
  desktop task on the Conjugal box): this candidate makes the pass daily and machine-wide, not per repo.
- **Keeps, unchanged,** Cloudvore's K44/K50 retire predicate recorded in `TRAPS.md` ("Archiving a Claude
  Desktop session removes its worktree"): HEAD an ancestor of the remote default branch, no
  reflog-only or per-worktree-ref commits, no lock, lease or live session, a quiet period, and a strictly
  clean tree. This candidate changes *when* and *where* the pass runs, never what makes a session safe.
- **Distinguishes** `ruling-candidates/PROPOSAL-fleet-rotation-continuity-strategy-v1.md` ("close idle
  sessions, max 6-8 active", a pre-rotation step): that is a cap at rotation time; this is a standing
  retirement at the landing seam. Supersedes nothing ratified.

## Measured (BACHELOR, 2026-10-22, reported by the owner's session; not re-run by this filing)

- 23 finished side sessions were still open and held 12.2 GB of RAM between them: each idle CLI held
  about 520-830 MB, plus its child processes (language servers, MCP servers, watchers).
- Retirement on this box ran weekly and was scoped to one repo, so sessions finished in other repos were
  never candidates, and a week of parallel work piled up between passes. The memory pressure fed the same
  day's machine-wide slowdown (see the slopbar `TRAPS.md` append, item 1).

## Proposed rule

1. **At the landing seam.** A side session is archived as soon as its branch is merged (its HEAD is
   contained in the remote default branch) and its worktree is clean, by the dispatcher that merged it
   or by the next retirement pass. A finished session is not kept open "in case".
2. **Daily, machine-wide.** The retirement pass runs at least daily and enumerates sessions in every repo
   on the box, not only the repo that owns the task. It claims its minute in the MINUTE REGISTRY.
3. **Safety is the existing predicate.** A session is retired only when the K44/K50 predicate holds
   (above); the per-worktree-ref gap recorded beside it must be closed in any implementation.
4. **Report.** Each pass prints sessions retired, sessions kept with the reason, and the RAM freed.

## Check

On a box with several merged, clean side sessions in two repos, run the pass once: every one of them is
retired, a session with an unmerged HEAD or a dirty tree is kept with its reason, and a second run the
same day retires nothing new.

## Close condition

The owner ratifies, amends or rejects it, or each board records ADOPT or DISTINGUISH in its own spec.
