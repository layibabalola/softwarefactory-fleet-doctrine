# R26 accepted-evidence integration — Phase 8

Phase 8 is a forward-only integration candidate. Its sole parent is the independently accepted
Phase 6 tip `8d97c399692e678eb4c975127c8ae1189d8dcb20` (tree
`e62e063b6a55084431dd8f485f59b74c0b897be5`). It mechanically replays the exact delta from the
independently accepted Phase 7 commit `c5b9efd00c47a84488b96734dd9b6a94ecd37999` (tree
`2d9f5d82bf1a8acbef5839ac6fcaecc1caf53023`) and resolves only their overlapping workflow and
predecessor-scope allowlists. It does not merge either branch and does not change the frozen ledger,
any project specification, any disposition, or any authority state.

The four Phase 7 request packets remain byte-exact Git objects:

- Adobe Ingester: `893de38f19c90303c4935de47fa535f590c91b4d`
- Agent Bridge: `b62bef05c4d980808478bed4b063b50751f8b0c3`
- AirMyPC: `7d202d0ad16d79a8ffdcd5589fd9af9422a2dbe3`
- Conjugal: `1f046669b36e994e26d451fa1341e54ae624081e`

The Phase 6 receipt batch remains the exact blob
`c10b1b7530e0d9695118a02dd21842e4fc1493e0`. The Phase 8 checker also binds both accepted commit
and tree objects, their exact source artifacts, the resulting narrow resolution blobs, the frozen
ledger, every project specification, and the unchanged R26 global manifest baseline.

Run the complete local evidence corridor with:

```console
python -m unittest discover -s tests -p "test_phase2_disposition_batch.py" -v
python tools/check_phase2_disposition_batch.py --treeish HEAD
python -m unittest discover -s tests -p "test_phase3_disposition_batch.py" -v
python tools/check_phase3_disposition_batch.py --treeish HEAD
python -m unittest discover -s tests -p "test_phase5_stale_reconciliation.py" -v
python tools/check_phase5_stale_reconciliation.py --treeish HEAD
python -m unittest discover -s tests -p "test_phase6_candidate_reviews.py" -v
python tools/check_phase6_candidate_reviews.py --treeish HEAD
python -m unittest discover -s tests -p "test_phase7_owner_publication_requests.py" -v
python tools/check_phase7_owner_publication_requests.py --treeish HEAD
python -m unittest discover -s tests -p "test_phase8_integration.py" -v
python tools/check_phase8_integration.py --treeish HEAD
python -m unittest discover -s tests -p "test_adoption_ledger.py" -v
python tools/check_adoption_ledger.py --treeish HEAD
```

The standalone global-manifest baseline is deliberately disclosed rather than rewritten. Running
`python tools/check_universal_manifest.py --treeish HEAD` exits `1` with
`MANIFEST_SUBJECT_MISMATCH`, exactly as it does at the Phase 5 base and both accepted source tips,
because that historical manifest binds the original R26 candidate subject set. The same checker
passes its actual pinned subject `e70a044f31dd2f43ab7c716d63a4eb89318c61b6` with 98 exact
subjects and a valid self-binding. Phase 8 preserves the manifest blob exactly and has no authority
to rewrite that historical evidence.

Local checks do not verify current remote refs. The candidate is author-conflicted until a fresh
independent reviewer accepts its exact commit/tree and artifacts. It carries no push, merge,
publication, message, provider, runtime, scheduler, task, gate-transition, installation,
disposition, or adoption authority.
