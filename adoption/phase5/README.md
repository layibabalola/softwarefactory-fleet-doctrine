# R26 remaining-STALE reconciliation — phase 5

`r26-stale-project-reconciliation.json` records the smallest evidence-honest forward result for
the four projects that remain `STALE` in the exact R26 ledger. It changes no project disposition.
Adobe's project remote is now exactly identified and reachable, but neither its published `main`
nor its published hardening ref contains an R26 disposition. Agent Bridge, AirMyPC, and Conjugal
still have no authoritative remote/current ref available to this bounded reconciliation.

The negative results are deliberately narrow. They mean only that this batch received no
project-owned current R26 publication; they are not proof that a repository or later publication
does not exist. Adobe's exact remote objects and the reviewer-capacity state artifact can be
rederived with the optional remote check. That evidence locates the project and explains why no
current R26 receipt can be credited; it does not authorize a work order, manufacture review
quorum, mutate a project, invoke a provider, or advance `STALE` to `DISTINGUISH`.

Run the fail-closed controls with:

```console
python tools/check_phase5_stale_reconciliation.py --treeish HEAD --scope-event workflow_dispatch
python tools/check_phase5_stale_reconciliation.py --treeish HEAD --scope-event workflow_dispatch --verify-remotes
python -m unittest discover -s tests -p "test_phase5_stale_reconciliation.py" -v
```

The local check binds the exact published doctrine base, phase-2 blocker rows, current ledger rows,
four-project closed set, zero-authority fields, and unchanged `0/5/0/0/4` ledger census. It reports
`REMOTE NOT VERIFIED`. Remote mode is bounded to Adobe's exact allowlisted GitHub URL and two refs,
uses a disposable repository with prompts disabled, rederives both commit/tree/parent tuples and the
state artifact, and proves the recorded R26 marker search remains empty. No provider is invoked and
the temporary Git objects are removed on exit.
