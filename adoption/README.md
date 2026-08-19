# Universal token-control adoption evidence

`universal-token-control-r26.json` is the machine-readable closed-set census for exact R26
candidate `e70a044f31dd2f43ab7c716d63a4eb89318c61b6` and exact merge
`909f769d02e8412e51e28e242cfa8d00dadc9a3d`. It derives credit only from each project's pinned,
single-writer spec commit and Git blob. `ADOPT`, `DISTINGUISH`, and `REJECT` mean an explicit
current-candidate project disposition; `STALE` means only the exact prior R14 disposition exists;
`MISSING` means no explicit disposition exists. Doctrine publication never changes any row by itself.

The checker closes on a changed or omitted project spec, a stale evidence pin, a fabricated
disposition, any attempt to convert `CANDIDATE_ZERO_AUTHORITY` into runtime/project/fleet adoption,
or any token-saving claim that drops exact model, effort, role, review, quality, or functionality
from the required non-regression dimensions:

```console
python tools/check_adoption_ledger.py --treeish HEAD
```

`.github/workflows/adoption-ledger.yml` runs the checker and its adverse controls on hosted Windows
and Ubuntu with Python 3.13 and 3.14. The workflow is separate from the R26-frozen provider workflow
so adding the adoption gate cannot alter the exact candidate subject bytes.
