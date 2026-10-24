schema: cos-feedback.v1
project: adobe-ingester
repo: layibabalola/adobe-document-cloud-ingester
pr: 6
head: baeb2128e5c589074bf6a291327a64ddb329ea18
reviewed_utc: 2026-10-24T04:17:57Z
event: changed-tip-delta
verdict: ADVISORY
reviewer: primary dot
review_uuid: df7016a7-4a2a-4b64-9edc-1d68d1c078ec
posture: non-gating ADVISORY under R18

# layibabalola/adobe-document-cloud-ingester #6 / baeb2128e5c589074bf6a291327a64ddb329ea18 / ADVISORY
## Blockers
None newly demonstrated. Prior LATE-READ-TIMEOUT-FAIL-OPEN is source-addressed at spikes/adobe-session/AdobeSessionSpike/Program.cs:1963-1966: timed-out final observation returns Unknown/Unstable, never successful prior history. Earlier budget-overrun/privacy remedies retained.
## Improvements
SessionBoundaryTests.cs:798-817 still uses completed reads/simulated elapsed time. Add pending final read after3SignedIn samples expecting Unknown/Unstable and fail-closed21.
Program.cs:2254-2306 adds Task.Run, outer WaitAsync and10s cleanup grace; existing cancellation test230-241 is cooperative. Add token-ignoring continuation/cleanup fixtures checking bounded caller wait, retained lease while outstanding, eventual release.
Program.cs:138-145 post-cleanup navigation recheck needs a cleanup-time navigation fixture lowering an initially authenticated verdict.
## Nits
Post-pass Grok6379516728 matches coverage gaps, not an independent blocker. Its timeout+10s/short-budget README and abandoned-read observation suggestions are attributed hardening.
## Coverage and readiness
Complete one-file delta from5f06ca41 plus immutable call chain/tests inspected source-first; no execution/browser/liveAdobe. Commit's Codex/live-validation claims not independent evidence or new authority.
Closed/merged during completed review at04:16:12Z, reviewed tip unchanged on delivery recheck. Earlier zero head checks/statuses/runs and synthetic99026bca251bde97716a8fd2d6834662184c8596 runs; no merge authorization inferred. Exact-head Claude+Codex/HIGH-RISK third-key/requiredCI/actualtree evidence unverified; Grok is advisory, not factory leg. No SHARED BLOCKER.
R18 advice not merge authorization or CoS gate. Preserve all independent factory evidence/CI/third-key, live-action/owner reservations and ACK duties. ACK/DISTINGUISH within24h citing UUID; prior duties not reset.
Signed: primary dot.
