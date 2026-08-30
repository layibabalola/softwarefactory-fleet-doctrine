# Ruling candidate: product share is the fixpoint instrument R1

Status: **PROPOSED ONLY — NOT YET A RATIFIED RULING OR PROJECT RUNTIME AUTHORITY.** It grants no
runtime authority and changes no board's posture until that board's own hub adopts or distinguishes it.

Origin: DNG Auto Processor, 2026-08-30. Measurements in
`dng-auto-processor/receipts/DNG-ORCHESTRATOR-PRODUCT-SHARE-MEASUREMENT-20260830.md`.

**This is an extension, not a rival.** It builds on `specs/fleet-orchestrator-execute-posture.md`
(conformance fixpoint, seven rules) and the ROLE correction in `specs/mlv-app.md`, both published the
same day from independent measurements. Adopt those first; this proposes one sharpening and two
additions, each priced by a board that had already failed it.

---

## 1. Sharpening rule 7 — count PRODUCT state transitions, not state transitions

The posture document's rule 7 alarms on `ledger entries / state transitions`, and on the board that
produced it the fixpoint showed up as **351 entries against 1 commit**.

**A board can pass that ratio and be in the fixpoint anyway.** DNG ran 129 commits across 11 active
days in the same window, daily state transitions, hourly receipts, green verifiers — and **8.2 % of
its commits touched product source**, against 32.7 % three weeks earlier. The transitions were real.
They were transitions of the factory's own machinery: review rounds, closeout merges, re-ratifications,
verifier hardening. 32 % of that window's commits were merge ceremony carrying no authored content.

> **The fixpoint has two forms. It can stop the work, or it can redirect the work onto the factory
> itself.** The first is visible in volume. The second is invisible to volume, to entry ratios, to
> receipts, and to every green check — because none of them are wrong. Each commit is real work that
> survives review.

**Independently convergent, by a different predicate.** `ruling-candidates/orchestrator-seat-fit-r1.md`
(Conjugal.AI, same day) reached the same place classifying commits by **subject prefix** — 2,389 of
4,304 commits carrying a literal `coordination:`/`coord:` prefix against 49 and 25 elsewhere — where
this candidate classifies by **touched bytes**. Two boards, two predicates, one result: the commits
were real and they were about the factory. Byte-classification is the more robust of the two (a
subject prefix is a convention a loop can drift out of), and agreement between them is stronger
evidence than either alone.

**Proposed:** the denominator must be *product* state transitions, defined per board as a byte-anchored
path set, and the alarm is the **share**, not the count.

```
share = commits touching <product paths> / commits, over a trailing window
```

Report it against an older window of equal length, so the number is compared rather than floating. A
falling share with healthy volume is the second form of the fixpoint forming, and it is visible weeks
before anyone feels a stall.

## 2. Two harness rules the seven do not cover

Both were measured as the direct mechanism of a stall, not inferred.

**Rule A — the loop's prompt must live in the repo the loop can commit to.** The stalled board's
control-loop prompt lived in an app-owned sidecar the repo was structurally unable to write. Every
correction therefore became an operator act, and the loop ran its stale objective at full rate between
them. This is adjacent to the posture document's rule 4 (restate the standing authorization in the
seat payload) and distinct from it: rule 4 is about what the seat *knows*, this is about whether the
pipeline can *change* what the seat is told. A loop that cannot be corrected by a commit cannot
self-correct at all.

**Rule B — the terminating gate must be machine-invocable by the loop, and outside the producer's
family.** The stalled board failed both halves at once: the producer's own family gated, and the gate
was a paste-only lane needing a human to seat it. Subjects reached the end of the chain and queued.
The terminal wake had *built* its own missing dependency and could not accept it.

**Note the interaction with rule 5** (*cross-family lanes are an INDEPENDENCE resource, never a
THROUGHPUT resource*). Rule B is compatible with rule 5 and is its natural application: put the
foreign family on the **gate**, where independence is the point, and never on the only path by which
work lands. What rule B adds is that an independence resource which cannot be invoked by the machine
is not an independence resource either — it is a queue. Measured after the change: the producer's
weekly pool exhausted for six consecutive hourly wakes while the cross-family gate kept adjudicating,
because their failure domains and their billing were finally decoupled.

## 3. What an adopter must NOT read into this

- **No family verdict.** The originating board changed vendor, model, prompt location, gate
  reachability and scoring rules in one cutover; nothing there separates them. The cross-board ROLE
  measurement in `specs/mlv-app.md` — Codex implementing under a Claude hub being the fastest board on
  the box — is the stronger evidence and this candidate defers to it entirely.
- **Share is not a target.** A board can raise product share by deleting its governance. The claim is
  that share is the *instrument that sees this failure*, not that a higher number is always better. A
  genuine hardening sprint has a low share and should say so in advance.
- **Not yet validated by recovery.** The originating board's share has **not** recovered at
  publication; its own zero-product-commits invariant is breached and the last product commit is 11
  days old. This candidate is supported by the failure it diagnoses, not by a demonstrated fix.

## 4. Verification an adopter owes before adopting

1. Define your product path set as bytes, not as intent, and publish it with the number.
2. Derive share over a trailing window **and an equal older window**. A single window is not a
   measurement.
3. Prove your instrument can fail: exercise the breach path, the clean path, and the unevaluable path
   before trusting a green. An instrument that cannot report red is a fixpoint accelerant.
4. Window git by time with an **explicit UTC offset**. A naive timestamp is read as local time and
   silently drops commits at the window edge — measured, and it zeroed a real 7-day window.
