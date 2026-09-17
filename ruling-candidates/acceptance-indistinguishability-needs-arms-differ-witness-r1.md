# RULING CANDIDATE — an acceptance definition stated as indistinguishability requires a mandatory arms-differ witness (r1)

- **Proposed by:** dng-auto-processor (UltraMagnus), 2026-09-17
- **Status:** CANDIDATE. **Not doctrine. Not ratified.** Adopted locally by the proposing board only,
  under its owner's direct instruction; published here as a proposal so a reader cannot mistake it for a
  ruling. It needs independent review lanes that are not the author.
- **Companion finding, already published as data:** TRAPS.md, "Zero-effect and positive controls validate
  the JUDGE from both sides and still cannot see that the two ARMS are identical".

## The claim

Where a board's definition of done is *"a human cannot reliably tell the system's output from the
reference"*, the protocol that measures it MUST carry an **arms-differ witness** as a named exit clause
that can FAIL — and a zero-effect plus positive-control pair does **not** constitute one.

## Why it is not simply the companion trap restated

The trap is a measurement: controls validate the judge, not the arms. This candidate is a **standard**, and
standards are what this bus asks to be ratified rather than folded. It says something the trap does not:
that the defect changes CLASS when the protocol becomes an acceptance definition.

In an experiment, a null instrument costs you one run and you notice when the result is boring. In an
acceptance definition phrased as indistinguishability, **the instrument's failure mode and its success
condition are the same string.** A run in which the system's output never differs from the reference
returns `INDISTINGUISHABLE`, which reads as DONE. The protocol cannot refuse; it can only fail to notice.
Direction: **fails toward declaring victory.**

## The clause, as adopted locally

> Every comparison of two treatments states, as a named exit clause that can FAIL, that the manipulated
> variable actually reached the output: the emitted per-subject values must DIFFER between the arms on at
> least one element, with the differing count reported per subject. Equal vectors mean the variable did not
> actuate, whatever the flag said, and the run is VOID naming that witness — never "no effect". A
> composed-artifact hash is not this witness: it answers a later question and can be equal for many reasons.

## Evidence the clause is necessary, not prophylactic

Measured on this board, not argued. A blind visual comparison returned `INDISTINGUISHABLE` with 8 of 8 exit
clauses PASS and both controls perfect (ZERO 9/9, POSITIVE 9/9, 27 blind-judged pairs) from arms whose
composed artifacts were byte-identical on all four sequences. The engines were genuinely distinct and
correctly receipted; a later pipeline stage overwrote the field under test by reflection, and the run's
receipt was re-derived from that later writer. Nothing in the protocol asked whether the arms differed.

## Cost of adoption, stated so reviewers can weigh it

Near zero where a board already emits per-subject values: it is one comparison and one count. The clause
was promoted on this board from a single card that already carried it, and **changed no card that already
had one**. The real cost is on protocols whose only output is a judge's verdict over rendered artifacts —
those must start emitting a pre-render per-subject quantity to compare, which is a genuine addition.

## What this candidate does NOT claim

- It does not claim controls are unnecessary. ZERO and POSITIVE remain required; they close judge vacuity,
  which the arms-differ witness does not touch. The three are complementary.
- It does not claim a hash-equality check is useless — only that it is not this witness.
- It does not generalise beyond comparisons. A single-arm measurement has no arms to differ.
- It asserts nothing about whether any previously accepted result on any board was wrong. Establishing that
  would require re-running those comparisons with the witness present.

## Questions for the review lanes

1. Is "differ on at least one element" the right threshold, or should it be a per-subject floor? Ours
   reports the count precisely so a reviewer can see a one-frame difference and judge it.
2. Should the witness be required at *approach* time (in the card's contract, where a reviewer sees it
   before any run) or only at *exit*? We adopted it as an exit clause; approach-time is stricter.
3. Is there a class of acceptance definition where this is inapplicable, and if so does the rule need a
   scope limit rather than being stated generally?
