# R26 local candidate review receipts — phase 6

`r26-local-candidate-review-receipts.json` durably records two independent, read-only reviews that
were previously available only in conversation state. Both verdicts are deliberately narrow:

- Salesforce commit `d8542ccfb9dde81dcdd57bf55c7959c3b0d521c4` is accepted as an honest,
  zero-authority `DISTINGUISH` evidence repair. It is not published on a project ref known to this
  review, does not change the already-`DISTINGUISH` ledger row, and proves no installation.
- Cloudvore commit `54a7a45c4b223a0d8647bfc61c732dc5325f8d30` is accepted only as an
  observational lower-bound blocker. It is not a project disposition and cannot change the
  already-`DISTINGUISH` ledger row.

The batch exact-binds each commit/tree/parent, every reviewed Git blob, byte count, SHA-256,
review engine, command, hostile result, semantic limit, and next lawful action. All authority
members are false. The canonical R26 ledger remains byte-identical at `0 ADOPT / 5 DISTINGUISH /
0 MISSING / 0 REJECT / 4 STALE`.

Run the local fail-closed controls with:

```console
python tools/check_phase6_candidate_reviews.py --treeish HEAD
python -m unittest discover -s tests -p "test_phase6_candidate_reviews.py" -v
```

When the two allowlisted project worktrees are present, rederive their exact Git objects with:

```console
python tools/check_phase6_candidate_reviews.py --treeish HEAD --verify-local-projects
```

No command in this phase invokes a provider, authenticates, modifies a project, changes a task,
installs a runtime, changes a gate, pushes, merges, publishes, or grants adoption credit.
