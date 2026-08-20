# R26 project-disposition intake — phase 2

`r26-project-disposition-intake.json` is a zero-authority blocker batch for the seven `STALE`
projects and the one `MISSING` project in the frozen R26 adoption ledger. It is based on immutable
implementation `490953a4496bab6977d554acb1828d40f4ac92d0` and amended review packet
`5ab5bf14ac900ddb2410d7e36d265cde1db76461`; neither object is rewritten.

Discovery was deliberately bounded to exact repository roots published by each single-writer spec,
or a direct-child name match under `C:\code` when the spec published no absolute root. No recursive,
network, runtime, or DNG product inspection occurred. None of the eight project repositories is
available on ULTRA-MAGNUS, so no independent project worktree could be created and no project
disposition candidate could honestly be authored. Every row is therefore an exact external blocker,
not an inferred `DISTINGUISH` and never `ADOPT`.

Priority is owner-action order, not likelihood of adoption:

1. Salesforce-tools — its current disposition is entirely missing.
2. Agent Bridge — advanced closed SHADOW evidence exists, but only against R14.
3. AirMyPC — a detailed zero-authority R14 packet and closure plan exist.
4. MLV-App — a reviewed R2 zero-authority packet exists, still R14-bound.
5. Cloudvore — a project proposal tuple and non-regression bar exist, still R14-bound.
6. Conjugal — an exact local difference and closure bar exist, still R14-bound.
7. AdversarialLLM — an R26-shaped contract exists without a current project receipt.
8. Adobe — project evidence already says a lawful work order and reviewer quorum are absent.

Structural verification works on every hosted platform:

```console
python tools/check_phase2_disposition_batch.py --treeish HEAD --scope-event workflow_dispatch
python -m unittest discover -s tests -p "test_phase2_disposition_batch.py" -v
```

The author-machine absence probes are separately reproducible and intentionally not run in hosted
CI. If a checkout appears, this command fails with `LOCAL_PROBE_DRIFT` so the project must move into
an isolated worktree and produce new project-owned evidence:

```console
python tools/check_phase2_disposition_batch.py --treeish HEAD --scope-event workflow_dispatch --verify-local-probes
```
