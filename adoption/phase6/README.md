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

The receipt itself is frozen as Git blob `c10b1b7530e0d9695118a02dd21842e4fc1493e0`,
`11,174` bytes, SHA-256
`16b1b3c033d2909d3fa0b3d10b845673dca8183607555525f04e9f52ab029623`. The checker also
requires a sole-parent descendant chain from canonical doctrine commit
`e4e7f9363185a5e10bb3a92167c785ef29caf2b7`; an unrelated tree or merge cannot substitute for
that history.

All exact-bound JSON values are compared recursively with exact Python types, so JSON booleans and
integers cannot alias one another. Local inspection removes inherited Git repository/configuration
redirection, resolves the expected worktree root, and requires symbolic `HEAD`, the declared local
branch tip, and the reviewed subject commit to be the same exact object.

Run the local fail-closed controls with:

```console
python tools/check_phase6_candidate_reviews.py --treeish HEAD
python -m unittest discover -s tests -p "test_phase6_candidate_reviews.py" -v
```

When the two allowlisted project worktrees are present, rederive their exact Git objects, resolved
worktree root, symbolic `HEAD` and branch tip, sole fetch/push `origin` URL, cleanliness, and absence
from every local remote-tracking ref with:

```console
python tools/check_phase6_candidate_reviews.py --treeish HEAD --verify-local-projects
```

That option performs local Git inspection only. It does not fetch, contact, or authenticate to a
remote, so network publication remains explicitly unverified even when no current local
remote-tracking ref contains either subject.

No command in this phase invokes a provider, authenticates, modifies a project, changes a task,
installs a runtime, changes a gate, pushes, merges, publishes, or grants adoption credit.
