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

The receipt itself is frozen as Git blob `c3f9c84cc39928801ca517cba8b8506c28c4ea20`,
`11,096` bytes, SHA-256
`68dfb623e7ee8b8624a568c8a79cd08b5504e840fcb53252c7a2884597439a0d`. The checker also
requires a sole-parent descendant chain from canonical doctrine commit
`e4e7f9363185a5e10bb3a92167c785ef29caf2b7`; an unrelated tree or merge cannot substitute for
that history.

Run the local fail-closed controls with:

```console
python tools/check_phase6_candidate_reviews.py --treeish HEAD
python -m unittest discover -s tests -p "test_phase6_candidate_reviews.py" -v
```

When the two allowlisted project worktrees are present, rederive their exact Git objects, current
branch, exact `origin` URL, cleanliness, and local remote-tracking-ref containment with:

```console
python tools/check_phase6_candidate_reviews.py --treeish HEAD --verify-local-projects
```

That option performs local Git inspection only. It does not fetch, contact, or authenticate to a
remote, so network publication remains explicitly unverified even when no current local
remote-tracking ref contains either subject.

No command in this phase invokes a provider, authenticates, modifies a project, changes a task,
installs a runtime, changes a gate, pushes, merges, publishes, or grants adoption credit.
