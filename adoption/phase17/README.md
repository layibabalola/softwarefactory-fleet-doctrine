# R26 Phase 17 DNG post-R60 evidence publication

Phase 17 records the project-owned DNG successor at commit
`43507aa20dfaaf198267cda0058689493d43d70a` and the exact R102/R60 runtime chain: unanimous
Fable, Opus, and Sonnet acceptance; non-mutating preview; first live apply; exact slice rollback;
clean reinstall; and two fresh production cadences.

The publication preserves the project’s honest `DISTINGUISH` disposition at 2 of 13 adoption
requirements. R60 changed the exact warden tuple, so idle-observation credit restarts at 0 of 1,000
after the terminal reinstall. The demonstrated slice rollback is not misreported as full adoption
rollback across the supervisor, policy, gate, adapter, and child boundary.

The canonical fleet ledger and every project specification remain byte-identical. Phase 17 grants
no provider, runtime, task, gate, installation, repository, remote-publication, or adoption
authority.

Verify with:

```console
python -m unittest discover -s tests -p "test_phase17_dng_r60_publication.py" -v
python tools/check_phase17_dng_r60_publication.py --treeish HEAD
```
