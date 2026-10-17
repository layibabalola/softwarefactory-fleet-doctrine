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
