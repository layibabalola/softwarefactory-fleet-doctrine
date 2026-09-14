# EVIDENCE ONLY — Cloudvore's parallel kernel draft (2026-09-14)

**Superseded by `specs/fleet-factory-kernel.md` r1** under the owner ruling recorded in bus 2bed997. Nothing here is a
candidate, a spec or a tool the fleet should run. It is kept so the steward can re-derive the proposals under `## Untested`
in `../cloudvore.md`. The files are reference copies, and their paths inside them are the draft's own (e.g.
`tools/kernel-convergence.py` imports `tools/harvest-status.py` from the bus root). The tests pass from the draft's
original layout, not from this directory.

- `universal-factory-kernel-r1.md`: the draft, 8 clauses `UFK-1`..`UFK-8`, with §3a Known limits
- `filing-format-README.md` and `PROMPT-K-draft.md`: its dogfood format and prompt
- `kernel-convergence.py` and `test_kernel_convergence.py`: an eligibility and harvest-due calculator (12 tests; 13
  single-guard mutations each failed the suite)

Review record: bus RECEIPTS.md on this branch, "Cloudvore's parallel kernel draft folded into fleet-factory-kernel r1
as a dogfood filing". Supersedes nothing on master.
