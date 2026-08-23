# Universal token-control adoption evidence

`universal-token-control-r26.json` is the machine-readable closed-set census for exact R26
candidate `e70a044f31dd2f43ab7c716d63a4eb89318c61b6` and exact merge
`909f769d02e8412e51e28e242cfa8d00dadc9a3d`. It derives credit only from each project's pinned,
single-writer spec commit and Git blob. `ADOPT`, `DISTINGUISH`, and `REJECT` mean an explicit
current-candidate project disposition; `STALE` means only the exact prior R14 disposition exists;
`MISSING` means no explicit disposition exists. Doctrine publication never changes any row by itself.

Phase 3 records independently accepted published candidates from AdversarialLLM, Cloudvore, MLV-App,
and Salesforce/context-ultra as current `DISTINGUISH` rows. Their exact remote refs, commits, trees,
parents, artifact Git blobs, byte counts, SHA-256 values, and statements are frozen in
`phase3/r26-published-project-disposition-intake.json` and exact-bound by the production checker.
All authority and proof-credit members remain false; see `phase3/README.md`.

Phase 5 records the bounded reconciliation of the four remaining `STALE` rows. Adobe's exact
project remote and two published refs are reachable but contain no current R26 disposition; Agent
Bridge, AirMyPC, and Conjugal still have no authoritative remote/current ref available to the
batch. The ledger and all project specs remain unchanged. See
`phase5/r26-stale-project-reconciliation.json` and `phase5/README.md`.

Phase 6 records independent, read-only review receipts for two newer local project candidates.
Salesforce `d8542ccf` is accepted only as an honest zero-authority `DISTINGUISH` evidence repair;
Cloudvore `54a7a45c` is accepted only as observational lower-bound blocker evidence and is not a
disposition. Neither local commit is credited as published by this phase, neither changes a ledger
row, and both authorize nothing. See `phase6/r26-local-candidate-review-receipts.json` and
`phase6/README.md`.

The checker closes on a changed or omitted project spec, a stale evidence pin, a fabricated
disposition, any attempt to convert `CANDIDATE_ZERO_AUTHORITY` into runtime/project/fleet adoption,
or any token-saving claim that drops exact model, effort, role, review, quality, or functionality
from the required non-regression dimensions.

A future `ADOPT` row must bind every dimension to a standalone canonical anchor in the exact
project spec and to a bounded JSON receipt under
`receipts/project-adoption/<project-id>/<receipt>.json`. The receipt must be committed atomically
with the project evidence, remain byte-identical at census and checked tree, bind the exact R26
candidate and merge, record all six exact claims with strict JSON `true`, and match the ledger's
recomputed SHA-256. A digest-shaped string, a quoted or negated anchor, or doctrine publication
alone earns no adoption credit.

The disposition itself must be exactly one standalone
`ADOPT(<canonical commit>, <profile SHA-256>, <review-receipt SHA-256>)` line. Its profile and review
receipt are recomputed from pinned project artifacts. The adoption receipt must also pin the local
supervisor and adapter subject bytes, complete launcher census, fake-provider controls, concurrency
controls, exactly 1,000 unchanged zero-inference ticks, full-child fencing, rollback proof, and the
current CLOSED gate. Every proof artifact binds the project, exact R26 candidate, merge/canonical
commit, profile, and review receipt. Missing, forged, prose-embedded, duplicated, or self-asserted
records fail closed under the ratified law in `RULINGS.md` lines 1027-1034.

Run the fail-closed verification with:

```console
python tools/check_adoption_ledger.py --treeish HEAD
```

`.github/workflows/adoption-ledger.yml` runs the checker and its adverse controls on hosted Windows
and Ubuntu with Python 3.13 and 3.14. The workflow is separate from the R26-frozen provider workflow
so adding the adoption gate cannot alter the exact candidate subject bytes.
