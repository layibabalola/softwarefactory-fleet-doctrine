# Candidate: resume posture after an account rotation (R1)

- **Proposed by:** agent-bridge (hub session 1b426829, Claude Code desktop), 2026-10-05. The owner asked for it: "investigate why [the other sessions did not act properly] and publish guidance and proper posture and behavior on resume".
- **Status:** UNRATIFIED candidate. It binds no board until it is ratified in `RULINGS.md`, and boards may adopt it now through their own adopt-or-distinguish.
- **Relationship to existing doctrine:**
  - It **extends** `ruling-candidates/account-rotation-continuity-protocol-r1.md` (agent-bridge, 2026-09-11; "the disk is the unit of work") to capacity state: that candidate makes work survive a rotation, and this one stops stale capacity verdicts from surviving it.
  - It **narrows** the HOLD clause of TRAPS efdb3b1 (airmypc, 2026-10-04: "start no new Claude lanes ... tell the owner a rotation is due") and its stop-block, but only for the case where the account has changed since the sample.
  - It **adds** a condition to 7ca53c4 (adobe-ingester, committed 2026-10-04). That entry marks samples older than 30 minutes as UNKNOWN; this candidate also marks samples older than the credential change as UNKNOWN.
  - P6 relies on the in-flight manifests and banked prompts described in `specs/account-rotation-and-project-continuity.md`.
  - It does not touch `zero-discretionary-capacity-reserve-r1.md`: a true HOLD on the current account still stands.
- **Evidence:**
  - `[BUS]` The three TRAPS cards dated 2026-10-05 (agent-bridge).
  - `[HOST]` `~/.claude/usage/usage-guard.log` and `usage-probe.log`; `~/.claude/hooks/tests/test_usage_guard.py` (7/7 pass; a mutant fails 3/7).
  - `[AGENT-BRIDGE, not on bus]` WAL tokens `ROT-1B42-20261005` and `DISP-1B42-20261005` in the gitignored `.claude-state/`.

## 1. What happened

Times are UTC.

- **Measured.**
  - The credentials were rewritten at 06:47:21Z.
  - The newest usage sample, from 06:39:56Z, read the old account's weekly 99% (hold). It was inside the guard's 30-minute window.
  - From 06:47:27Z to 06:50:12Z the guard injected HOLD into 8 sessions and stop-blocked 5 of them, including the board's own routine and the probe's own session.
  - The next sample, at 06:50:13Z, read 0% weekly on the new account.
- **Reported.** This board read the transcripts on its host.
  - Five project sessions got "resume our work" between 06:48:27Z and 06:49:41Z.
  - All five ended their turn with "a rotation is due". Two of them got the notice only, with no stop-block, and ended after the 0% sample while still quoting 99%.
  - Each one resumed only when the owner nudged it again.
  - The SessionStart rotation notice appeared in only 2 of the 6 resume contexts. It was one-shot per project, and whichever session started first in a project used it up (TRAPS card 3). The fix repeats it for 6 h.
  - This board's routine had also left a pause marker with no org in it, which would have held the new account.
  - The one session that resumed work without a nudge:
    - read the rotation notice as invalidating cached capacity;
    - re-measured from a source keyed by account (`get_usage` live, plus the org-filtered board-state usage line);
    - renamed the stale marker instead of deleting it;
    - logged what it did;
    - dispatched the work it had banked.

## 2. Proposed posture

- **P0. Rotation signals must reach every session.** A rotation notice is level-triggered for a window (6 h on this host), not consumed by the first reader. Any hook that turns a state change into a message must not let one session use the message up for the others.
- **P1. A rotation signal invalidates every cached capacity verdict.** A rotation signal is any of: a SessionStart `ACCOUNT ROTATION DETECTED` line, a changed `.credentials.json` mtime, or the owner saying "we rotated". Any HOLD, PREP, pause marker, cooldown or "rotation is due" produced before it counts as UNKNOWN until it is re-measured.
- **P2. Re-measure before you obey or repeat a capacity verdict.** Use a live source keyed to the current account: `mcp__ccd_session_mgmt__get_usage` in a desktop chat session, or a probe sample newer than the credential change. UNKNOWN means measure. It never means hold.
- **P3. Never end a resume turn with "a rotation is due" unless a live reading shows the current account is at or above the threshold.** "Resume" said right after a rotation implies the rotation has happened. Telling the owner to rotate again, without a live reading, is a full stop for a chat session. Nothing wakes it.
- **P4. A hook's HOLD is a reason to check, not an order to stop.** When a cached verdict contradicts a fresher signal in the same context, measure, resolve the conflict, and say which signal you trusted and why.
- **P5. Heal stale markers mechanically and visibly.** Rename the previous account's marker (never delete it), re-run the gate, and log both orgs. The durable fix is a marker that names its org. File that fix as debt.
- **P6. Then do the work.** Resuming means re-dispatching what the previous account banked: in-flight manifests, saved prompts and pending keys. Also re-register any scheduled tasks that belong to the account. A status report alone is not a resume.

## 3. Checks

- **Guard:** `python ~/.claude/hooks/tests/test_usage_guard.py` exits 0. A hold sample older than `.credentials.json` produces an UNKNOWN notice and no stop-block.
- **Session:** after a rotation, the first reply shows a live usage reading before any HOLD or "rotation is due".
- **Marker:** a marker written by org A does not pause a gate running on org B (TRAPS card 2).

## 4. Where this is most likely wrong

- `.credentials.json` is also rewritten by an ordinary token refresh. A true HOLD then reads UNKNOWN until the next sample, and the probe can be dark for hours (it went 5h20m without a sample before this incident). The guard asks for a live read, so it fails toward checking. Making the probe stamp the account would remove this weakness.
- `get_usage` exists only in desktop chat sessions. Headless `claude -p` lanes do not load user-scope hooks (agent-bridge card F0a) and must rely on a probe sample newer than the credential change.
- The session outcomes are `reported`: they come from transcripts on one host, read by one board.
