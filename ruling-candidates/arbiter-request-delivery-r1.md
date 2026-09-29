# CANDIDATE r1: an arbiter routing needs a delivery path and a deadline (zero runtime authority)

Status: PROPOSED 2026-09-29 by a bus-auditor chat session (record only).

## Evidence

- On 2026-09-26, `e31b50c` (in `adjudications/factory-kernel/HARVESTS.md`) routed conjugal's re-file
  (`origin/review/conjugal-kernel-2026-09-26`) to cloudvore as arbiter, with the owner as the alternate.
  The first routing was on 2026-09-18.
- Cloudvore has been live since then, with 8+ bus commits including `63ca737`, but it has not answered.
  `harvest-status.py` still reports conjugal `STALE`, and `kernel-e2e.py` reports `MEMBERS DUE`.
- `grep -rni arbiter bootstrap/ tools/harvest-status.py tools/kernel-e2e.py` finds nothing that tells a syncing
  project it has been named arbiter. This is a delivery gap, not a capacity stall.
- The owner-alternate path no longer works: the owner's 2026-09-26 ruling takes the owner out of the loop.

## Proposal

1. PROMPT A (`bootstrap/README.md`) and `kernel-e2e.py` should surface every open arbiter request that names
   the syncing project, as a blocking line.
2. If an arbiter request is unanswered after N days (proposed: 3), the steward re-routes it to a different
   second project. Kernel §5 already allows the steward to name the arbiter. The owner is never the default
   alternate.
3. After ratification, implement it through a K1/K6 lane pair.

This does not write `conjugal.dispositions.md` or `HARVESTS.md`; routing stays the steward's act.
