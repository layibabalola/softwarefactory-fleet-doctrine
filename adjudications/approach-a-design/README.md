# Fleet review of Conjugal's Approach A design (v7.4) — how to file findings

Subject: `specs/conjugal-approach-a-v7.4.md`. Protocol: `specs/design-loop-protocol.md` §7. Opened 2026-09-13 (conjugal, Bachelor).

One file per project, single writer: `adjudications/approach-a-design/<project>.md`. Header:

```
project: <name>
providers: <families you could seat, e.g. claude(fable,opus,sonnet) codex(sol,luna,astra) | claude-only>
seats: <who scored; effort>
rubric_id: <sha256 you computed from the six dimensions if you scored; else "unscored">
posture: <copied from tools/review-posture/review_posture.py posture: "<name> COMPLETE (n/n lanes)" or "<name>-PARTIAL (…missing…)">
cross_family: <validated | NO-CROSS-FAMILY-VALIDATION>
panel: <composite over n/8 seats, families as seated>   (commit the scoring contract beside the filing as <project>.rubric.json)
```

`posture:` never names a posture that did not run in full (RULINGS R9). Run it with `tools/review-posture/run.sh`.

Then findings, one per line, nothing else:

```
§<section> | "<≤25-word quote from the spec>" | <defect, ≤40 words> | REPLACES: "<exact anchor>" → "<replacement>" | PROOF: <scenario or test that would falsify>
```

Test-bench rule: every finding names how it manifests in YOUR repo (a path, a tool, a measured number), or it is filed
under a `## Untested` heading. Prose reviews are not merged. Scores (optional) use the six dimensions in the protocol's
source rubric: Timeline Realism, Contract Completeness, Cross-Family Safety, Autonomy Achievement, Throughput Goal,
Risk Mitigation — 0–100 each, composite = mean.

Landing (RULINGS R7, owner ruling 2026-09-14): commit the filing plus its RECEIPTS row on `review/<project>-<YYYY-MM-DD>`
and **push that branch immediately, without asking**; it is done only when `git ls-remote origin refs/heads/<branch>`
matches the local tip. Never push to master. Filings not yet merged live on `origin/review/*` — harvesters read those too.
