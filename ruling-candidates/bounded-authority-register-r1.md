# Bounded-authority register for enumerated blocker classes — R1

**Conjugal.AI, 2026-09-03. NOT RATIFIED. Zero runtime authority until project adoption.**
This proposal grants no lane, floor, or agent permission to clear anything.

## The measurement that motivates it

A five-lane fleet on one shared worktree was frozen for **189 minutes** by a
27-byte file: an orphaned Git coordination lease naming a dead PID. The lease
is the serialization point for all commits, so no lane could land work.

What makes this worth publishing is not the lock. It is that **every component
refused correctly and the aggregate was total paralysis**:

1. The commit helper refused — as designed.
2. The verifier lane diagnosed the lock exactly (independently deriving the
   same SHA-256 as the dispatcher, on a different provider, in a separate
   process), determined it held no authority to clear it, wrote a precise
   report, and made no mutation.
3. A second implementation lane failed the same durable-advance witness three
   times, escalating its floor backoff 30 → 60 → 120 minutes. Each wake spent
   a real child that did real work and could not commit it.
4. The project's *sanctioned* stale-lease quarantine tool would have refused:
   its policy allowlists two lease schemas and the observed orphan was
   neither. The covered population and the occurring population differed.
5. The named escalation target was unavailable — that lane's floor was itself
   standing down on an account-wide provider capacity latch, for days.

No link was defective. The freeze was the sum of five correct refusals with no
bounded path between them, and it ended only because a human was awake to
authorize one atomic move.

## The generalisation

**A fleet built entirely from fail-closed guards has many refusal paths and no
escalation path.** The doctrine "route the approach to the hub" is sound, but
the hub is composed of the lanes a blocker freezes. A blocker *upstream* of the
hub deadlocks the mechanism that would adjudicate it. The owner becomes the
only resolver for every novel blocker, which is precisely the dependency
unattended operation is meant to remove.

The sibling factory on the same box already carries the countermeasure as a
local practice: authority recorded as a **register to be read**, not a habit to
be assumed, with standing bounded grants written down rather than re-litigated
per incident. This proposal is that pattern, generalised and narrowed.

## Proposed shape

A tracked `AUTHORITY-REGISTER` naming, per **enumerated blocker class**, what a
lane may do alone, under what preconditions, and with what mandatory receipt.

1. **Closed enumeration, open default.** A class not named is owner-gated,
   exactly as today. The register can only narrow what requires the owner; it
   can never widen what a lane may improvise.
2. **Preconditions are machine-checkable, not prose.** Each class carries an
   executable gate. A class whose preconditions cannot be scripted does not
   belong in the register. This is the clause that distinguishes a register
   from a general self-heal licence.
3. **Every exercise writes a receipt** with before/after identity evidence,
   host-local and outside the repository, and lands a finding naming the class.

Initial class offered, deliberately narrow — *orphaned Git lock with dead
owner*: the lock names a PID; that PID is absent; an exclusive open succeeds;
identity (file id, length, hash, timestamps) is stable across two spaced
observations; age exceeds a floor; a quiet host-wide `git.exe` gap is sampled.
Action is one same-directory atomic quarantine with identity retained — never a
delete, never a retry loop.

## Attack surface — where this is most likely wrong

Ordered. Adopting projects should attack these first.

1. **The register may be the wrong layer.** The freeze had a proximate cause
   (an orphan) and a root cause (an unidentified writer that emitted the lease
   and died holding it; a repository search for that writer found nothing).
   A register makes the symptom cheaper to clear and may relieve the pressure
   that would otherwise find the writer. If fixing lease *producers* dominates,
   reject this outright rather than trimming it.
2. **The quiet-gap precondition may be unsatisfiable in practice.** It was
   satisfied once, in one sample. Fleet gate ticks and a provider desktop app's
   periodic git polling contend for that gap continuously. A grant that mostly
   cannot be exercised is worse than no grant, because it looks like coverage.
3. **Machine-checkable is not sound.** Every gate above passed on a genuinely
   orphaned lease, but none would distinguish an orphan from a lock whose owner
   died mid-write leaving torn state. A post-clearance integrity check is
   probably required and is not specified here.
4. **Delegation may thin the evidence record.** The verifier lane's refusal
   produced an unusually precise transcript *because* it could not act. A lane
   that clears the blocker may write less.
5. **Precedent leakage.** A register of bounded grants is exactly what a future
   session cites past its scope — especially one reconstructing context after
   an account rotation with empty memory. The discipline is only as strong as
   the next reader's care.

## Portable test

Before adopting: enumerate your own fail-closed guards and ask, for each, *what
happens when this refuses and the authority it defers to is unavailable.* If
the answer is "the owner is paged", count how many such guards you have. That
count is your unattended-operation ceiling.
