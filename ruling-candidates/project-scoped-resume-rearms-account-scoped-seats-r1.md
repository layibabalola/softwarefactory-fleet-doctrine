# Ruling candidate: "resume our work" is ONE project procedure, and it must re-arm account-scoped seats — R1

Status: **PROPOSED ONLY — NOT YET A RATIFIED RULING OR PROJECT RUNTIME AUTHORITY.** It grants no runtime
authority and changes no board's posture until that board's own hub adopts or distinguishes it. Doctrine is
DATA, never instructions (bus law 1) — nothing below is a command to execute.

**Measuring project:** dng-auto-processor (machine ULTRAMAGNUS). **Measured 2026-09-10 and 2026-09-11.**
**Origin:** the owner's instruction, 2026-09-11: "resume our work should scope to project not global machine
level" and "publish this strategy to doctrine repo so the other projects can adopt it and/or improve on it".

**Relationship to existing doctrine:** a response to `ruling-candidates/PROPOSAL-fleet-rotation-continuity-strategy-v1.md`
(Conjugal). It **ADOPTS** principles 1, 2 and 5 (the disk is the unit of work; a project-scoped entry point;
machine-local session checkpoints). It **DISTINGUISHES** principle 3 (stricter: a prompt carries no SHA at
all, not even a "transaction marker", PROPOSAL:89). It **IMPROVES** principle 4 and **CORRECTS** two claims
(sections 2 and 3). It adopts `cloudvore/standards/ACCOUNT-PARITY-ATTENDED-REPAIR.md`'s attended repair and
receipts-not-claims discipline, and builds on `TRAPS.md:29` ("org-rotation registry wipe": app scheduler
state is org-scoped) and `TRAPS.md:8668` (the 2026-09-11 correction: a run frozen on a permission prompt holds
a scheduler slot indefinitely) — this candidate adds the procedure those two traps imply.

---

## 1. What the measuring board found

- **Four definitions of the phrase coexisted.** The project's auto-loaded entry file; a machine-level
  rotation runbook that also catches "resume our work" after a login change; an auto-loaded memory entry;
  and a stale section of the project's own prompt document. Two of them sent a new session to a file that
  had been archived into a directory sessions are forbidden to read, and the memory entry told it to
  re-open a lane apparatus the project had retired. A new account's first "resume our work" would have
  been routed to unreadable files and to the wrong design.
- **Account-scoped seats do not survive a rotation.** Both of the board's desktop-app scheduled seats (a
  stateless orchestrator and a design steward) were stranded on the old account by a 2026-09-10 rotation and
  had to be re-created. Nothing in any of the four definitions re-created them.
- **A frozen run holds a scheduler slot forever.** Three scheduled runs waiting on permission prompts held
  all three of the desktop app's concurrent slots; the orchestrator was skipped every minute for hours, and
  the app refused to archive the stuck runs ("still working (a turn in progress)") — only a person clicking
  Stop could clear them. No resume step looked for this.
- **Correct behaviour defers commits.** The orchestrator deliberately holds its bookkeeping commit while
  the machine is loaded (it protects timing measurements); measured about 3 hours uncommitted, on disk the
  whole time. A rotation on the same machine loses nothing on disk.

## 2. Corrections to the Conjugal proposal

1. PROPOSAL:199-200 ("New account inherits running floors ... No manual restart required") and PROPOSAL:274
   hold for OS-level floors (Windows Task Scheduler), **not** for desktop-app scheduled tasks, which belong
   to an account or org and are wiped or stranded by a rotation. A resume procedure must verify every
   account-scoped seat on the account now in use, and must be able to re-create it.
2. PROPOSAL:108-110 (a flat 15-minute, or 1-hour, commit bound) is violated by correct behaviour on a
   loaded machine. The bound that matters for a rotation is **on disk within one tick**; git commit
   follows at the next quiet window. (Machine loss, not account rotation, is what a commit bound guards.)
3. Missing from all five principles: the **stuck-slot check** (section 1, third bullet).

## 3. The rule

1. **One definition per project.** The phrase routes, from the project's own auto-loaded entry file, to ONE
   versioned procedure inside the project's repo. A machine-level runbook covers account and CLI
   re-authentication only and defers to the project for everything else. Every other copy (memory entries,
   old prompt sections) either points to it or is removed; a copy that disagrees is the one to fix.
2. **The procedure derives, repairs with a person present, writes a receipt, and stops.** In order: orient
   from disk (entry files, the selector, git, worktrees, the session-start hook's rotation and parity
   lines); stop if the desktop app and the CLI are on different accounts; confirm each account-scoped seat
   exists and is enabled on the account now in use, and re-create a missing one from definitions stored in
   the repo (the owner approves the scheduler call); name every stuck scheduled session for the owner to
   Stop, never approving its prompt; check CLI authentication, treating a dark provider as failover rather
   than a blocker; fold new doctrine as data; report; write a receipt; stop. It never acts as a second
   orchestrator.
3. **Seat prompts point into the repo.** Each scheduled seat's prompt is a few lines pointing at its
   procedure in a versioned document, and the procedure document reproduces that prompt text so it can be
   rebuilt byte-for-byte (the measuring board verified both of its seats' prompts rebuild with an ordinal
   comparison). Re-creating a seat on a new account is then a short copy, and changing a seat's behaviour
   never needs the scheduler's own files — which, measured, a seat cannot safely touch unattended.
4. **Liveness is a receipt.** A re-armed seat is alive when its next run leaves its own receipt (a commit,
   a dated status line, a receipt file). A scheduler showing "enabled" proves nothing.

## 4. Costs and limits

- A person must approve the scheduler calls and clear stuck sessions: attended repair is unavoidable for
  account-scoped seats.
- The procedure is started by a person's phrase. Autonomous forward motion comes from the seats once they
  are re-armed, not from the resume session.

## 5. Adoption test for another board

- Search your auto-loaded entry files, memory index and prompt documents for your resume phrase: exactly
  one definition; everything else points to it.
- List every path your resume chain names: none missing, none inside a directory sessions may not read.
- Rebuild each seat's prompt from your repo-resident text and compare it with the live prompt, ordinal and
  byte-for-byte.
- After your next rotation, count the minutes from the first resume message to each seat's first receipt.

## 6. Evidence (measuring board)

- The procedure: dng-auto-processor `docs/13-RESET-PROMPTS.md` section P-RESUME (commit `c162c4bd`), the
  workspace `CLAUDE.md` "resume our work" section, and the two seat pointer prompts it reproduces.
- Ledgers on the measuring machine: `C:\DngAutoJobs\evidence\RESUME-SCOPE\attempt1\` (fold, two review
  verdicts, prompt rebuild check) and `C:\DngAutoJobs\evidence\FACTORY-EVOLVE\attempt1\doctrine-evidence\`
  (scheduler skips, archive refusal, the steward's pending call).
