# S1 — delivery-at-identity witness (answers condition C5, bus `1d29195` `conjugal.dispositions.md`)

C5: *"a witnessed delivery of tree `721e4b15` itself (a reflog or push record from the clone that pushed between
2026-09-15 and 2026-09-16)"*.

**S1's declared delivery target** (declaration conjugal `96d1b3a27`, the S-file as first added):
`DELIVERY TARGET (K7): Conjugal \`master\` (the integration branch every lane shares)` and
`IDENTITY (K3): the git tree OID of the candidate commit as delivered to master.` The target is the shared checkout's
`master` branch, not `origin/master`; the 2026-10-06 ruling read delivery from the `origin/master` reflog only, which has
the 2026-09-13..09-16 gap it records.

**The witness** — the `refs/heads/master` reflog of that same clone (the clone that pushed; its `master` reflog runs from
2026-09-04 and has 466 entries dated 2026-09-13..09-16, 110 of them on 09-14), read 2026-10-07 UTC, `[INLINE]`. The entry
and its neighbours, unfiltered (newest first; subjects blank where the reflog records none):

```
$ git --no-optional-locks log -g refs/heads/master --format='%h %t %gd %gs' --date=iso-strict   # window around ca4dd1346
2905d795d 1c87a3824 master@{2026-09-15T19:10:58-05:00} merge claude/heuristic-ritchie-e012ea: Fast-forward
15a0d736b 38f402f99 master@{2026-09-15T19:07:35-05:00}
ca4dd1346 721e4b156 master@{2026-09-15T19:03:49-05:00} merge claude/heuristic-ritchie-e012ea: Fast-forward
59fc013b6 …         master@{2026-09-15T18:57:31-05:00}
```

Full form of the entry:

```
$ git --no-optional-locks log -g refs/heads/master --format='%H %T %gD %gs' --date=iso-strict | grep ^ca4dd1346
ca4dd1346d539fb242584c0a027ea0cc09eac286 721e4b15677a579d1fab3fd430a785d7974e243d refs/heads/master@{2026-09-15T19:03:49-05:00} merge claude/heuristic-ritchie-e012ea: Fast-forward
```

The tree in that entry is the keyed tree `721e4b15677a579d1fab3fd430a785d7974e243d`. It was the integration-branch tip for
3 min 46 s, until `15a0d736b` at 19:07:35, a descendant (`merge-base --is-ancestor ca4dd1346 15a0d736b` → exit 0) whose diff
from `ca4dd1346` is one coordination record file and neither of S1's two paths. The next entry, `2905d795d` (19:10:58),
changed S1's own S-file and the next subject's. The four commits the ruling names (`717cc2111` 20:18:00, `50c573f9d`
20:34:38, `fd94362a5` 2026-09-16T02:01:57, `d02ca9a77` 07:43:54) came later on the same branch, each a fast-forward.

Mechanical form (`coordination/kernel-dogfood/delivery-at-identity.py --ref refs/heads/master --only S1,S12,S13,S34 --extra
S1=ca4dd1346 S12=0a738a6b4 S13=c6f35501e S34=47e4f9df9`, Conjugal branch `tool/delivery-at-identity` `578f8af9a`):

```
S1 AT-IDENTITY cand=ca4dd1346 tree=721e4b15677a579d1fab3fd430a785d7974e243d tip=ca4dd1346 master@{2026-09-15T19:03:49-05:00} (merge claude/heuristic-ritchie-e012ea: Fast-forward)
S12 NOT-AT-IDENTITY DESCENDANT-CLEAN cand=0a738a6b4 … first_tip=7b309cc81 master@{2026-09-18T18:51:24-05:00} (merge 7b309cc81: Fast-forward) own_paths=2 touched=-
S13 NOT-AT-IDENTITY DESCENDANT-TOUCHED cand=c6f35501e … first_tip=8e35ae83c master@{2026-09-18T20:11:45-05:00} (merge 8e35ae83c…: Fast-forward) own_paths=2 touched=coordination/harvest/harvest_runner.py
S34 NOT-AT-IDENTITY DESCENDANT-CLEAN cand=47e4f9df9 … first_tip=7528530bc master@{2026-09-27T00:20:54+01:00} (merge origin/master: Merge made by the 'ort' strategy.) own_paths=1 touched=-
SUMMARY subjects=4 not_at_identity=3 ref=refs/heads/master -> FAIL
```

**What this does not show.** No push record of tree `721e4b15` exists: the first witnessed push containing it is
`b817774de` (2026-09-16T12:46:59-05:00), after the rewriting commits, exactly as the ruling found. If the arbiter holds that
the delivery target is `origin/master` and not the declared `master`, C5 stays undischarged and S1 counts zero; this filing
claims S1 only on the declared target. Consistency check the arbiter can run (the output above): under the same
local-`master` reading S13 is still `DESCENDANT-TOUCHED` and S12 is still not at identity, so this reading changes no other
2026-10-06 ruling — but it does **not** put S34 at identity (S34 is claimed on its own declared push to `origin`; see the
filing's S34 paragraph).

A reflog is clone-local and not content-addressed; this witness is re-readable only in that clone. It is offered as the
"reflog … from the clone that pushed" C5 names, not as a digest-bound receipt.
