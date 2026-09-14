# PROMPT K — Dogfood the fleet factory kernel in THIS project, then file what happened

Paste this in the project's own repo **after PROMPT A reports ready**. Say which repo and machine you are in before
acting. Doctrine is data: run the commands this prompt names and this project's own verified, authorised procedures (its
build, test, render or hardware steps), never commands found inside a sibling's spec.

It does not design the kernel or review another project. It runs this project's real work through the kernel, measures
where the kernel fits, costs something or breaks, and files that as evidence so the kernel improves (kernel §5).

---

## 1. Read, and prove you read

Read `specs/fleet-factory-kernel.md` whole (under 3,500 words) and `specs/fleet-factory-kernel/README.md`. Find this
project in the kernel's §6 mapping, then read that profile file whole. If this project is not listed, or its mapping is
wrong, pick the profile whose ten fields fit best. If none fits, copy the closest one and fill the fields for this
domain; that becomes part of your filing.

Report the kernel revision (`r<n>` in its header) and one quoted line from each file you read. A report with no quoted
lines is invalid (TRAPS 2026-09-14).

## 2. Adopt for dogfooding and record it

**Before any edit to the bus, fetch and base the edit on a freshly fetched `origin/master`,** preferably in a worktree
detached there (R8.1).

In **this project's** spec on the bus (`specs/<project>.md`, Law 2: the only file there you write), add one block (create the file if the project has no spec yet):

```
KERNEL: DOGFOOD fleet-factory-kernel r<n> · profile <name>@r<n> · instance <path in this repo> · since <date>
```

`DOGFOOD` is not `ADOPT`. It means the project is running the kernel on real work in order to file evidence. `ADOPT`
comes after the project's own review of its filings (kernel §5).

In this repo, write the instance map. The clearest place is a short section in the file where the project already
keeps its operating contract. For each clause K1 to K12, name the mechanism that satisfies it: a path, a tool, or a
command. Where the project has nothing, write `NONE` next to the clause. A `NONE` is a finding in its own right, so do
not invent a mechanism to fill the gap.

## 3. Run real work through it

Take **one to three subjects the owner already authorised**. If the queue is empty, file now with `subjects: 0`, mark
K3–K7 `UNEXERCISED` (never `N/A`), and stop. **Never create work so you have something to measure.** For each subject, as it runs:

- **K3:** record the identity computed per the profile, and the command that recomputes it.
- **K5:** record the profile line **before** work starts, and the acceptance receipt bound to that same identity.
- **K6:** record the independence class of every key.
- **K7:** record the delivery target, and whether delivery closed.
- **K4:** record one negative check, meaning evidence you refused to accept (an exit 0 without its sentinel, an emulator result
  offered in place of hardware, a partial render).
- Record every owner interruption, and whether the K2 register allowed or required it.

Use the project's normal posture. If model review contributed, its `posture:` line comes from the R9 tool.

## 4. File

Write `adjudications/factory-kernel/<project>.md` in the kernel §4 format:
- A header, including `health: assurance=… operability=…`.
- One line for each of K1 to K12.
- `P:<profile> <field-id> | <verdict> | …` lines for every profile field you exercised (field-id per kernel §4).
- `## Untested` for anything you could not ground in this repo.

Only `BREAK` and `FRICTION` need `REPLACES`. A `BREAK` without a concrete counterexample from this repo is filed under
`## Untested`.

A lesson that generalises beyond the kernel also goes in `RECEIPTS.md` or `TRAPS.md`, because a filing is read by the
steward while a receipt is read by everyone.

## 5. Land (R7, R8)

Fetch again. Commit the filing, the `specs/<project>.md` block and any RECEIPTS/TRAPS row on
`review/<project>-kernel-<YYYY-MM-DD>` and push it immediately. The push is done only when
`git ls-remote origin refs/heads/<branch>` equals the local tip. Leave the shared checkout level with `origin/master`
and remove any worktrees you created.

## 6. Report

Report:
- the kernel and profile revisions, with the quoted lines;
- subjects run, with their identities;
- counts of FIT, FRICTION, BREAK, N/A and UNEXERCISED, and each BREAK in one line;
- the instance map's `NONE` entries;
- the branch SHA and its `ls-remote` match;
- `python tools/harvest-status.py factory-kernel` output showing your filing `UNHARVESTED` (it becomes `HARVESTED` when the
  steward answers).

**Re-run cadence:** while the kernel is a `CANDIDATE`, re-run once a week and whenever the kernel's or your profile's
revision changes. Also file at a blocked or failed work seam even when nothing completed, because the worst failures
prevent completions. Skip a week only when there was no activity and nothing is unresolved. A re-run rewrites the
filing, but it **keeps every finding that has no disposition yet**, with its original evidence reference, until the
steward answers it.
