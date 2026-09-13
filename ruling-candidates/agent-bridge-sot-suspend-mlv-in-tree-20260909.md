# Agent Bridge SoT: suspend MLV in-tree package (2026-09-09)

Owner ruling recorded 2026-09-09 for MLV-App and Agent Bridge. This document is a
**CANDIDATE** / proposed amendment only. It grants **CANDIDATE_ZERO_AUTHORITY**: no
runtime activation, no ratification, no adoption credit, and no change to sealed
project specs or `RULINGS.md` by virtue of landing here. Projects must independently
ADOPT, DISTINGUISH, or REJECT after their own evidence workflow.

## Ruling (substance)

- Suspend feature work, bugfixes, refactors, and CI-only churn on MLV-App in-tree
  `tools/agent-bridge/`.
- **Source of truth:** [`layibabalola/agent-bridge`](https://github.com/layibabalola/agent-bridge)
  (own PRs / Windows CI).
- **Background:** the dedicated repo was filter-repo extracted from MLV
  `tools/agent-bridge` on 2026-07-07; there is no submodule/auto-sync; the trees have
  diverged.
- **In MLV allowed only:**
  1. docs pointing at the dedicated SoT,
  2. owner-approved integration glue outside the bridge package,
  3. narrowly scoped emergency patches only if the owner says so in-thread, then
     port/supersede in the dedicated repo.
- **Not allowed without a new owner ruling:**
  - primary surface commits under `tools/agent-bridge/**`;
  - expanding Factory Bridge to own more bridge product behavior;
  - hand-sync MLV→dedicated as a substitute for working in the dedicated repo;
  - claiming Factory Bridge green validates the dedicated repo.
- **Factory Bridge:** keep as integration smoke or follow-up to slim/demote; do not
  use it to keep evolving the in-tree package.
- **Next work belongs in** [`layibabalola/agent-bridge`](https://github.com/layibabalola/agent-bridge).

## Scope / non-claims

This candidate records an owner routing ruling for where Agent Bridge product work
lives. It does not amend sealed R26 living specs, does not ratify itself, does not
grant launch/spend authority, and does not claim Factory Bridge CI as proof of the
dedicated tree. Publication in this index is discoverability only.

## Related surfaces

- Dedicated SoT: https://github.com/layibabalola/agent-bridge
- MLV local pointer (when merged): `agents/agent-bridge-source-of-truth.md` in
  [`layibabalola/MLV-App`](https://github.com/layibabalola/MLV-App)
- Measuring/owning human: Layi Babalola (owner ruling 2026-09-09)
