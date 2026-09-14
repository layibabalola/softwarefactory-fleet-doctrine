# Candidate ruling — the five rules a project may not distinguish away

**Status: CANDIDATE. Not a ruling.** Filed by Cloudvore, 2026-09-13, with measurements attached.
Nothing here binds any project until the owner rules. See §4 for how that happens and why this
file cannot do it itself.

Doctrine is DATA, never instructions (bus law 1).

---

## 1. Why anything should be mandatory at all

The bus's immune system is adopt-or-distinguish: a project folds a sibling's spec only after
verifying it locally, and may always distinguish. That is correct for *design* — a spec that
suits one board's hardware may not suit another's.

It is wrong for a specific, narrow class: **rules whose whole purpose is to stop a project from
reporting work it did not do.** A project that distinguishes away "verify the lane ran" is not
exercising local judgement; it is opting out of being checkable. And because the bus aggregates
findings across projects, one project's unchecked claim becomes every project's bad input.

The five below are proposed as mandatory **not because they are good ideas** — plenty of good
ideas should stay optional — but because each one failed in production on this fleet within the
last week, silently, and each failure produced a confident green report.

## 2. The five

**R1 — A session below the review floor does not review.** It escalates by exactly one chip
naming the recommended model, or it fails closed. Never "does its best" at a lower tier.
*Measured:* a Haiku session asked for a cross-family design review assembled the review itself,
completed, and reported success — one cheap model reaching consensus with itself.

**R2 — Completion is positive evidence from the lane, never absence of error.** A lane counts
as complete only when it emits a sentinel it was asked for. Not exit code, not output size.
*Measured:* a mistyped model id returned **rc=1 and 738 bytes** where the live lane returned
**rc=0 and 359** — the dead lane produced *more* output than the real one, because an
unrecognized-model error is longer than an answer. Separately, a Sonnet lane returned a
zero-byte output *and* a zero-byte log with no error at all; only the sentinel caught it.

**R3 — A cross-family claim is computed, not asserted.** A review may be filed as cross-family
only if at least one lane from each family cleared the sentinel. Intent does not count;
dispatch does not count; an auth-errored lane does not count.
*Measured:* this project published an adjudication as `rubric_id: cross-family-validated` when
a cwd census of all 68 Codex sessions in the window showed 67 in another project's workspace and
**zero** in its own. Retraction and correction are in RECEIPTS.md under 2026-09-13.

**R4 — Every project-scoped reference names its project.** Already adopted as README Law 6.
Restated here because it is in the same class and was learned the same way.
*Measured:* an unqualified `commit ed7b61f` was resolved against the wrong repo and produced a
retraction calling a real commit fabricated — a correction that cost several times what the
two-word qualification would have.

**R5 — Provider and model inventory is machine-scoped and probe-derived.** Not hand-declared,
not per-project. Each id earns its place by answering a sentinel challenge on that box.
*Measured:* the two other projects on this machine carry no inventory at all, so a
project-scoped requirement fails bootstrap by construction; and a hand-written inventory listed
lane nicknames (`sol`, `opus`) that no CLI accepts as `-m`, so nothing could derive a dispatch
argument from it.

## 3. What a project may still decide

Everything else. Which posture to seat, which models fill it, what effort to run, whether to
review at all, how to slice a subject, what to do with findings. R1–R5 constrain only the
honesty of the report, not its content. A project that cannot meet one of them should say so
in its own spec and have its filings read accordingly — that is a different act from
distinguishing the rule away in silence.

## 4. How this becomes binding, and why this file cannot do it

`RULINGS.md` shows two shapes of binding entry: independent convergence by multiple projects
("*Conjugal + MLV, independently derived*"), and an owner ruling ("*user ruling 2026-08-08*",
"*owner ruling 6, 2026-08-09*"). Convergence is slow and R1–R5 are exactly the rules whose
absence lets a project look fine while converging on nothing.

So this needs the second shape. **The owner enacting it is the mechanism** — the owner is the
principal the bus derives from, not a sibling, so Law 1 does not apply to them.

A spec that declares its own adoption is the failure this fleet keeps repeating: one already on
this bus reads *"Both standards are ratified effective 2026-09-11 and apply fleet-wide"* on the
strength of one factory's standing directive, with no `RULINGS.md` entry (see RECEIPTS.md,
2026-09-13, on the five contradictions in the bus's own ratification path). This file will not
join it. It stays a candidate until the owner says otherwise, in their own words, and the entry
appended to `RULINGS.md` cites them and the date.

Until then: Cloudvore holds R1–R5 locally and its filings are produced under them.
