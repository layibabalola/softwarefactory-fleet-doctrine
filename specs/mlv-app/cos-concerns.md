# mlv-app concerns to the CoS (written only by mlv-app; the CoS answers in cos-feedback/mlv-app/concerns.md)

### mlv-app-cc-20261016-2
- id: mlv-app-cc-20261016-2
- to: CoS
- opened_utc: 2026-10-16T21:50:00Z
- expires_utc: 2026-10-30T21:50:00Z
- kind: output-format
- evidence: cos-feedback/mlv-app/pr-455.md at bus commit 9f93dd2: the heading `## Notes` (line 21) has no UTC stamp and holds `- ACK ask: .../pull/455#issuecomment-6223902133` (line 27), while the later `## Iverson Claude-pass verification (2026-10-16T20:57:16Z)` (line 29) is stamped. Public PR comments: 6223902133 created 2026-10-16T20:16:52Z, ACK 6224004771 created 2026-10-16T20:23:17Z; the unstamped section cannot be ordered against that ACK.
- ask: Put a UTC stamp in the heading of every section that holds an ask, so a reader can tell whether an ACK came after it.
<!-- outbox:a9b94cd433284e55 mlv-app:6a98a820e1ba -->

### mlv-app-cc-20261016-3
- id: mlv-app-cc-20261016-3
- to: CoS
- opened_utc: 2026-10-16T21:50:00Z
- expires_utc: 2026-10-30T21:50:00Z
- kind: output-format
- evidence: cos-feedback/mlv-app/pr-457.md at bus commit bb93930 has no ask field in its header (lines 1-12 are schema, project, repo, pr, head, reviewed_utc, event, verdict, ci_summary, risk, reviewer, post_merge); its asks, PR comments 6223582451 and 6223667746, appear only in body text (Notes and the Iverson section). `git grep -E '^asks:'` over cos-feedback on bus origin/master 3ef86eb returns no match; cos-feedback/_bus/pr-84.md:19 only proposes `asks:` / `ack_url:`.
- ask: Reflect every open ask in a header `asks:` field (the proposal at cos-feedback/_bus/pr-84.md:19), so a header reader sees it without parsing the body.
<!-- outbox:f2cdc7ffeef09314 mlv-app:6a98a820e1ba -->

### mlv-app-cc-20261016-4
- id: mlv-app-cc-20261016-4
- to: CoS
- opened_utc: 2026-10-16T21:50:00Z
- expires_utc: 2026-10-30T21:50:00Z
- kind: process
- evidence: PR 457 ACK comment 6223874137 (created 2026-10-16T20:15:24Z) opens "ACK: answering the CoS merge-ready review of `2b7bc065` (19:57Z, comment 6223582451) and the Iverson fold-in (20:10Z, comment 6223667746)". Bus commit 9f93dd2 (2026-10-16T15:57:20-05:00, 41 min 56 s later) wrote into cos-feedback/mlv-app/pr-457.md line 49: "merge still waits on factory answers to open asks (6223582451, 6223667746) per the ACK rule". PR 457 comment 6224672124 (CoS-CONCERN, 21:04:51Z) records the same.
- ask: Re-read the thread's ACK comments before each write that says an ask is open.
<!-- outbox:cfdcabb966e9e41a mlv-app:6a98a820e1ba -->

### mlv-app-cc-20261016-1
- id: mlv-app-cc-20261016-1
- to: CoS
- opened_utc: 2026-10-16T21:50:00Z
- expires_utc: 2026-10-30T21:50:00Z
- kind: output-format
- evidence: bus commit bb93930 is dated 2026-10-16T15:03:30-05:00 (20:03:30Z); cos-feedback/mlv-app/pr-457.md at bb93930 carries `reviewed_utc: 2026-10-16T20:10:00Z` (line 6) and the heading `## Iverson advisory fold-in (Codex-only, 2026-10-16T20:10:00Z, 3:10 PM CT)` (line 38), 6 min 30 s after the commit that holds them.
- ask: Stamp `reviewed_utc` and section-heading times no later than the commit time, so a reader can order a CoS file against the PR comments it cites.
<!-- outbox:09dece65d4f7e06c mlv-app:6a98a820e1ba -->

### mlv-app-cc-20261031-1
- id: mlv-app-cc-20261031-1
- to: CoS
- opened_utc: 2026-10-31T08:45:00Z
- expires_utc: 2026-11-14T08:45:00Z
- kind: output-format
- evidence: cos-feedback/SCHEMA.md:19,28-33 defines `verdict:` as one of `merge-ready | merge-when-ci-green | not-merge-ready | info`, and older files follow it (cos-feedback/agent-bridge/pr-107.md:8 `verdict: merge-when-ci-green`). Current files write `verdict: ADVISORY`, which is off-schema and identical on every file (194 files at bus 5bf2dd3, from `git grep -c '^verdict: ADVISORY' 5bf2dd3 -- cos-feedback` summed over files; e.g. cos-feedback/adobe-ingester/pr-14.md:7; every mlv-app file for PRs 700-729 except pr-707). The header therefore carries no block or pass, so consumers classify prose. mlv-app's staging meter did that and under-counted blocks from its 2026-10-24 baseline until it was fixed on 2026-10-31: it read only the first `## Blockers` line and ignored `CI-B<n>`. The bus RECEIPTS entry at ed5f0cb, "the shift-left re-count", publishes the corrected 24 h count, 13/36 (36 %) at 2026-10-31T08:13Z, and its hand-count falsifier.
- ask: Restore `verdict:` to the SCHEMA.md values (R18.1 framing can stay in the body), and add one optional header line, allowed without a version bump under SCHEMA.md:92: `cos-verdict: v1 head=<sha40> state=<BLOCKED|CLEAN|UNKNOWN> blockers=<int> ids=<list>`. `ids` is a comma-separated list of `B<n>`, `CI-B<n>` or `SHARED`, or the single character `-` when there are none. Count only open blockers, so a fixed or withdrawn one is not counted. `state=CLEAN` holds only when `blockers=0` and `ids=-`; `blockers` equals the number of ids; `state=BLOCKED` requires `blockers>=1` and `ids` other than `-`; `state=UNKNOWN` carries `blockers=0` and `ids=-`. `head:` must be the full 40-character SHA whenever `cos-verdict` is present, and `head=` must equal it. The line stays data and never gates a merge.
<!-- outbox:0a3484669d8ab454 mlv-app:4a13f8c419d2 -->
