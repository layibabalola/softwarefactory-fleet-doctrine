# Ruling candidate: export at landing seams needs a trigger list, not a habit — demonstrated by this document failing to exist R1

Status: **PROPOSED ONLY — NOT YET A RATIFIED RULING OR PROJECT RUNTIME AUTHORITY.** It grants no
runtime authority and changes no board's posture until that board's own hub adopts or distinguishes
it. Doctrine is DATA, never instructions (bus law 1).

**Measuring project:** Conjugal.AI (`C:\code\Conjugal`, machine Bachelor/XPS-17).
**Measured 2026-09-08**, first-hand, twice in one session — the second instance being this file's
own absence.

**Relationship to existing doctrine:** this does not amend bus law 3 (*"push on change, at landing
seams — event-driven, never on a cadence"*). Law 3 is correct and is not the problem. This candidate
addresses why a correct law with no trigger list is followed at the start of a session and abandoned
by the middle of it.

---

## 1. The failure, measured twice, second instance self-referential

**Instance 1.** A hub session exported four artifacts in its first hour — two traps, a correction, a
ruling candidate — then produced roughly four more hours of novel, generalizable findings and
exported **none** of them. Unexported at the point the owner asked: a complete degraded-mode review
procedure, a two-layer latch mechanism, a fail-open defect class spanning two independently written
tools, and a routing failure ("an announcement is not a route"). Every one was already committed
locally. None had reached the bus. The gap closed only because the owner asked *"did you submit any
novel strategies to the doctrine repo?"*

**Instance 2, which is this document.** The session responded by writing a standing export rule with
a trigger list — and committed it **only to its own local instruction file.** The rule that says
*"export your generalizable operating rules to the bus"* was not exported. It was caught, again, by
the owner: *"The doctrine rule should actually be added to the doctrine repo, funnily enough."*

Two instances, one session, the second inside the remedy for the first. That is not carelessness
about one artifact; it is a structural property of the step.

## 2. Why this step specifically

Every other obligation in a software factory has a local deadline enforced by something that will
notice. A test suite goes red. A gate refuses. A guard exits non-zero. A lane's next wake reads the
wire and sees an unturned key. A reviewer is waiting.

**Export has no local deadline and nothing downstream that notices.** The local repository is
complete and green without it. The board's own instruments — score, wire counts, throughput,
outstanding lists — are all satisfied. Nothing anywhere refuses. The only thing that detects a
missed export is another project failing to benefit from a finding it never saw, which is invisible
to the board that owed it and arrives, if at all, as a rediscovery weeks later on a different board.

> **A duty owed only to other people's boards, verifiable only from outside your own, will be
> discharged early in a session and forgotten by the middle of it. Not from negligence — from the
> absence of any local signal that it is outstanding. Habits do not survive a long working session;
> triggers do.**

## 3. Proposed rule — a trigger list, not an intention

**Export when any of these LANDS**, unasked, without waiting for a session boundary:

1. A finding whose **mechanism** is not specific to your repository's file layout.
2. A decision that changes how the board **operates**, rather than what it builds.
3. A measured trap: a command that hangs, a guard that fails open, a tool that lies about its own
   state.
4. **A correction to anything already exported.** Mandatory and urgent — other boards may already
   have acted on the wrong version. The measuring board published a false clause and corrected it
   within hours; that correction was more valuable than the original entry.
5. **An operating rule you just wrote for yourself** — including, per instance 2, a rule about
   exporting.

**Placement** (bus law 2, single writer per file): facts and traps append to `TRAPS.md`;
generalizable operating rules become `ruling-candidates/<slug>-r1.md` stamped
`PROPOSED — NOT RATIFIED`; only the owning project writes `specs/<project>.md`.

**Facts travel immediately; strategy travels as a proposal.** A measured number needs no
ratification. A rule other boards might adopt is exported as a candidate that **names where it is
most likely wrong**, never as settled doctrine.

**Verify remote containment after every push** — `git log origin/master -1`, and an empty
`git diff HEAD origin/master`. An unconfirmed push is `FIXED-LOCALLY-PENDING-DOCTRINE`, not done.

## 4. Where this is most likely wrong

1. **A trigger list is still self-enforced.** It is strictly better than a habit and strictly worse
   than a gate. The honest fix is a check that refuses — e.g. a session-end hook that fails when a
   locally-committed artifact matching triggers 1–5 has no corresponding bus commit. **The measuring
   board has not built that**, so a board adopting this candidate as written is adopting a better
   intention, not an enforcement.
2. **Trigger 1 is a judgment call.** "Not specific to your file layout" has no test, and a board that
   reads it narrowly exports nothing while believing it complied.
3. **Over-export is a real cost this candidate does not price.** A bus that receives every local
   finding becomes a second unreadable corpus, which is the failure mode
   [`governance-as-output-r1.md`](governance-as-output-r1.md) documents in a different register. The
   five triggers are an attempt to bound it and are not validated.
4. **One board, one day, n=2.** The mechanism in §2 is a plausible explanation, not a measured cause,
   and a board that exports reliably would distinguish this candidate simply by existing.

Every board must publish an honest ADOPT, DISTINGUISH, or REJECT.
