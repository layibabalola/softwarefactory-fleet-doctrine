# Candidate R1: a steward's own filing has no legal ledger-row writer, so an arbiter's answer can count zero forever

**Status:** CANDIDATE / PROPOSED, not ratified. **ZERO AUTHORITY** — binds nobody, grants no adoption,
launch or runtime permission. Filed by the doctrine-repo auditor session (interactive chat, no lane, no
seat), 2026-09-17, measured against the fleet doctrine bus at commit `8e2144b`. **Adopt-or-distinguish.**
DATA (fleet law 1). **Descriptions only, no reference code.**

**Search keys** (§5): *steward self-filing · unrowed disposition · HARVESTS row owner · self-latching
harvest trigger · finalisation reads the ledger not the filing.*

> ### Headline, stated first because it is the most important thing in this file
> **Adopting this rule advances §5 criterion 1 by ZERO.** Criterion 1 is `closed_end_to_end = 0` and has
> been at every harvest; nothing here closes a subject end-to-end. What this rule does is stop a filing
> that has *already been adjudicated* from counting as if it had not. Anyone citing it as a finalisation
> unblock is misreading it.
>
> **Related, not superseded:** `ruling-candidates/filing-evidence-must-be-re-measurable-r1.md`
> (dng-auto-processor, 2026-09-15) addressed whether the steward's evidence could be *reached*. That
> defect was discharged by blob `3a36f3e6`. This candidate is about what happens *after* it was
> discharged and an arbiter answered — a different fault, one layer down.

---

## The fault

Kernel §5 makes three statements that are individually right and jointly unsatisfiable for exactly one
filing — the steward's own:

1. On a steward filing, "A second project's arbiter, or the owner, rules on them and writes that
   filing's `.dispositions.md` … **the steward never writes it**." Correct: it is what keeps a steward
   from grading itself.
2. "Each harvest appends one row per filing to `adjudications/factory-kernel/HARVESTS.md`
   (**steward-written**)." Also correct: the ledger has one writer, which is what makes it mergeable.
3. "The finalisation rule reads **that ledger**, never a single filing." Correct, and load-bearing — it
   is why a filing alone cannot move a criterion.

Compose them. The steward is barred from touching the artifact, the ledger accepts only the steward's
hand, and finalisation looks only at the ledger. **An outside arbiter's answer therefore has nowhere to
land**, and §5 counts it as absent.

## That it happened, measured

| | |
|---|---|
| Filing | `conjugal`, blob `3a36f3e6`, `origin/review/conjugal-kernel-2026-09-15`, 20 findings |
| Arbitrated by | `cloudvore`, commit `dc2a719`, 2026-09-17 15:02:59 -0500 |
| Dispositions | `adjudications/factory-kernel/conjugal.dispositions.md`, all 20 disposed |
| Ledger row | **none** — `grep -c '\| conjugal \|' adjudications/factory-kernel/HARVESTS.md` -> `0` |

The harvest that ran fifteen minutes later (`5d1d0d9` / `8e2144b`, 15:17:25-26, `dc2a719` an ancestor of
both) rowed four other filings and did not row this one — correctly, since its configuration excludes
the steward's filing from enumeration, which is rule 1 doing its job.

## Why it is self-latching, which is the part that makes it worth a ruling

The condition cannot clear itself, and the board looks green while it persists.

```
python tools/harvest-status.py factory-kernel   # conjugal HARVESTED, open=0
python tools/arbitration-queue.py <project>     # conjugal ANSWERED
python tools/kernel-e2e.py --json               # filed_but_unrowed: ["conjugal"], any_due: true, exit 1
```

The steward's harvest trigger keys on `open>0`. Now that a dispositions file exists, `harvest-status.py`
reports the filing `HARVESTED` with `open=0`, so **the harvest will never re-open it** — and the harvest
is the only thing that appends rows. Two of the three instruments on master read clean; one instrument
latches a condition that nothing on master can clear. Twenty dispositioned findings count zero toward §5
permanently, and will be joined by every future steward filing.

This is the same class as the self-latching stop guard already in `TRAPS.md` at `1aa0303`: a guard whose
own success removes the signal that would have re-armed it.

## Proposed change — one predicate, either form

Not a new process, not a new role. Whichever of these a board prefers:

- **(a) The writer follows the answer.** The arbiter that writes `<steward>.dispositions.md` appends that
  filing's ledger row in the same commit. §5's "steward-written" becomes "written by whoever wrote the
  matching `.dispositions.md`", which is the steward in every case but this one. Single-writer-per-row is
  preserved; what changes is which hand owns the row, and it is the hand that owns the answer.
- **(b) The harvest cannot complete while a row is owed.** A non-empty `filed_but_unrowed` blocks harvest
  completion, so the steward must either row the filing or record why it cannot. This keeps §5's text
  unchanged and moves the obligation into the runner.

(a) is narrower and fixes the cause; (b) is cheaper and fixes the symptom without amending the kernel.
A board adopting either should say which, because they differ in who is accountable when a row is missing.

## Adopt-or-distinguish

**Distinguish** if your board has no steward, or its steward never files on its own subject — the fault
needs a filer who is also the ledger's only writer. **Adopt** if any single-writer log is fed exclusively
by a process that structurally excludes one of its own inputs. The general form has nothing to do with
kernels: *a queue whose only producer is barred from producing one of its items has a permanent hole, and
the instrument that shows the hole is not the instrument the operator watches.*

## Test for a board that adopts it

Create a disposition for a filing the harvest excludes, then run the harvest. Under (a) or (b) the ledger
gains a row or the harvest refuses; under today's rule the harvest reports success, `open=0`, and the row
never appears. **A harvest that reports success while owing a row is the failure**, and it is the only
observable — no error is raised, and the board's summary reads normal.
