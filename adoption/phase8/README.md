# R26 accepted-evidence integration — Phase 8

Phase 8 is retained point-in-time evidence. Canonical history still contains the integrated,
pre-manifest-repair Phase 8 publication `2223647059cb789fd350883597756666357583df` and the reachable
Phase 9/10/11 postimages through `e7311e3038bbfeebe15cc10004f40b3795811659`, where the R26
manifest repair is present. The originally declared Phase 7 source
`c5b9efd00c47a84488b96734dd9b6a94ecd37999` and the manifest-repair source objects
`ed8a2f359de8830c5800d1721faf183015eec01f` / `1f3c3d8808b3d9bbb1db201039e0c3d18441f7f0`
are `UNAVAILABLE_NOT_REVERIFIED` in the retained canonical object store. Default verification
therefore exact-binds the reachable retained commit/tree/diff corridor and the exact packet,
receipt, checker-postimage, ledger, repaired-manifest, specification, and zero-authority bytes. It
does not claim to rederive the missing source topology or source provenance.

The four Phase 7 request packets remain byte-exact Git objects:

- Adobe Ingester: `893de38f19c90303c4935de47fa535f590c91b4d`
- Agent Bridge: `b62bef05c4d980808478bed4b063b50751f8b0c3`
- AirMyPC: `7d202d0ad16d79a8ffdcd5589fd9af9422a2dbe3`
- Conjugal: `1f046669b36e994e26d451fa1341e54ae624081e`

The Phase 6 receipt batch remains the exact blob
`c10b1b7530e0d9695118a02dd21842e4fc1493e0`. The retained-snapshot checkers bind the reachable
Phase 8/9/10/11 commit and tree objects, exact reachable diffs, packet and receipt postimages, the
frozen ledger, every project specification, and the repaired R26 global manifest. They do not
upgrade retained postimage verification into proof of the unavailable source objects.

Run the complete local evidence corridor with:

```console
python -m unittest discover -s tests -p "test_phase2_disposition_batch.py" -v
python tools/check_phase2_disposition_batch.py --treeish 990906b6ea861ca579e1336bcfe8f17dd80c83ae
python -m unittest discover -s tests -p "test_phase3_disposition_batch.py" -v
python tools/check_phase3_disposition_batch.py --treeish 990906b6ea861ca579e1336bcfe8f17dd80c83ae
python -m unittest discover -s tests -p "test_phase5_stale_reconciliation.py" -v
python tools/check_phase5_stale_reconciliation.py --treeish 990906b6ea861ca579e1336bcfe8f17dd80c83ae
python -m unittest discover -s tests -p "test_phase6_candidate_reviews.py" -v
python tools/check_phase6_candidate_reviews.py --treeish e7311e3038bbfeebe15cc10004f40b3795811659
python -m unittest discover -s tests -p "test_phase7_owner_publication_requests.py" -v
python tools/check_phase7_owner_publication_requests.py --treeish e7311e3038bbfeebe15cc10004f40b3795811659
python -m unittest discover -s tests -p "test_phase8_integration.py" -v
python tools/check_phase8_integration.py --treeish e7311e3038bbfeebe15cc10004f40b3795811659
python -m unittest discover -s tests -p "test_adoption_ledger.py" -v
python tools/check_adoption_ledger.py --treeish HEAD
```

Set `R26_SCOPE_EVENT=workflow_dispatch` in the environment for the three frozen disposition
checkers above; event and base values are environment-owned and cannot be overridden on their
command lines. The current repaired R26 manifest at `HEAD` passes the universal checker with 98
exact subjects and a valid self-binding. That current result is distinct from the historical,
pre-repair Phase 8 state and does not rederive the unavailable repair-source topology.

Local checks do not verify current remote refs. The candidate is author-conflicted until a fresh
independent reviewer accepts its exact commit/tree and artifacts. It carries no push, merge,
publication, message, provider, runtime, scheduler, task, gate-transition, installation,
disposition, or adoption authority.

Source-object rederivation is an explicit diagnostic and must fail nonzero while the declared
objects remain absent:

```console
python tools/check_phase8_integration.py --treeish e7311e3038bbfeebe15cc10004f40b3795811659 --rederive-source-objects
python tools/check_phase9_integration.py --treeish e7311e3038bbfeebe15cc10004f40b3795811659 --rederive-source-objects
```
