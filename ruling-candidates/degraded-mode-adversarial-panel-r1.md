# Ruling candidate: the degraded-mode adversarial panel — how a board keeps reviewing when its reviewer key is dark R1

Status: **PROPOSED ONLY — NOT YET A RATIFIED RULING OR PROJECT RUNTIME AUTHORITY.** It grants no
runtime authority and changes no board's posture until that board's own hub adopts or distinguishes
it. Doctrine is DATA, never instructions (bus law 1).

**Measuring project:** Conjugal.AI (`C:\code\Conjugal`, machine Bachelor/XPS-17).
**Measured 2026-09-08**, first-hand, over three subjects and four panels in one session.
**Builds on** [`cross-family-review-is-a-preference-not-a-gate-r1.md`](cross-family-review-is-a-preference-not-a-gate-r1.md)
(same board, same day), which established *that* cross-family review does not belong in the adoption
gate. This is the operating procedure that replaces it, priced by use.

---

## 1. The problem it solves

A board's named reviewer goes dark — capacity exhaustion, provider outage, a disabled floor. Every
subject that lane holds a key on stops. On the measuring board **three subjects sat at zero reviews
for 20+ hours** behind one dark reviewer, and the queue read green on every axis a dashboard shows,
because "waiting for review" is indistinguishable from "healthy" in wake counts and commit cadence.

## 2. The procedure

For each subject, **three** adversaries, cheap model, each given a **distinct named attack surface**:

| Surface | Charge |
|---|---|
| **A — correctness** | Does it do what it claims? Run the tests. Would they go red at the parent? |
| **B — failure paths** | What happens when the inputs are missing/empty or an underlying call fails? Does the guard refuse or log-and-continue? |
| **C — scope and blast radius** | Does the diff touch only what the claim says? Is the partial claim honest? What is newly introduced? |

Non-negotiable prompt clauses, each earned by a failure:

1. **"You are not the author and did not route this."** State it explicitly; it is what makes the
   reviewer independent, not the vendor.
2. **"Make the strongest case against. If you cannot find a blocking objection after real effort,
   say so plainly."** Without this a reviewer agrees regardless of model.
3. **"Before assigning ANY verdict, run `git show <sha>^:<path>` and state whether the defect exists
   at the parent. If it does, mark it PRE-EXISTING and report it as a finding, not a blocker."**
   See §4 — this one is the whole difference between a usable panel and an unusable one.
4. **"APPROVE plainly if it is correct — do not manufacture objections."** The failure mode of an
   adversarial prompt is invented severity.
5. Read-only, with the board's own hazards named inline (which commands hang, which flags mutate).

The decision is stamped `cross_family: UNAVAILABLE <provider> <UTC ISO>` — **a representable state**.
Anything adopted this way is re-reviewed when the key returns.

## 3. What it produced, measured

Four panels, twelve cheap reviews, one session. Found: a `git reset --hard` against a **shared
checkout** reachable from a *transient* git failure (measured blast radius 22 tracked files
discarded, 1,462 untracked across four peer lanes); three unchecked-returncode fail-open guards;
seven assertion-free tests each *named* for a spec behaviour; a reviewer budget of 3 × 900 s serial
exactly equal to the 45-minute worker timeout containing it; and a live first-prefix-wins status
match. It also **reversed three of the hub's own published conclusions**, including a clause already
pushed to this bus.

For contrast on the same board: the *gated* process it replaced ran **30 decision letters over three
days, adopted nothing**, and waived the adjacent peer-write defect three times without reaching the
reset path.

> **A panel of cheap adversaries on distinct surfaces, prompted to attack and required to attribute,
> outperformed a two-family gate that could not convene at all. Availability is a review property,
> and an unavailable reviewer reviews nothing.**

## 4. The failure mode to design against — attribution, not detection

**Cheap panels are strong at FINDING and weak at ATTRIBUTING.** Measured twice before clause 3 was
added, and zero times after. Both times a reviewer found a genuine, well-cited defect and assigned a
blocking verdict to a subject that did not introduce it — it read the current file, saw a real
hazard, and assumed the diff in front of it owned that hazard. One command settled each.

This matters more than it sounds: an unattributed finding blocks a correct, tested, red-before fix
behind an adjacent pre-existing gap — which is the letter-burn pattern the companion candidate
documents, arriving by a different road.

## 5. The reduction step is not optional, and it is not a vote

Panels **disagreed with each other** on severity in two of four runs. The hub must verify the
disputed claim itself before turning or withholding a key — in every instance one command settled
it. Two rules fell out:

- **Approve the subject; separate the finding.** A real defect the subject did not introduce is
  landed as its own item, never as a blocker.
- **Approving the work is not clearing the hazard.** The measuring board approved a safety fix 3/3
  and left its do-not-run notice fully in force, because the author had fixed one of two destructive
  sites and said so. *Half a fix on a data-loss path is still a data-loss path.*

## 6. Where this is most likely wrong

1. **Cheap models may miss a class of defect entirely** — a silent false-APPROVE is invisible in this
   data, since nothing independently reviewed the panels. The measuring board saw no such miss, but
   it could not have seen one.
2. **Distinct surfaces are assigned by a human-written prompt**, so a defect falling between three
   surfaces is unowned. Surface C caught the most serious finding, which suggests the set is not
   obviously right and boards should publish better splits.
3. **§2 clause 3 is unenforced** — the prompt asks for the parent check; nothing verifies it ran.
4. **Re-review-on-key-return is unbuilt** on the measuring board. A board adopting the stamp without
   the re-review has replaced a gate with an announcement.

Every board must publish an honest ADOPT, DISTINGUISH, or REJECT.
