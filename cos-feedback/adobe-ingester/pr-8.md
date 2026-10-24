schema: cos-feedback.v1
project: adobe-ingester
repo: layibabalola/adobe-document-cloud-ingester
pr: 8
head: 3078f640abd452d5f5c8fb32cb889d459155ebab
reviewed_utc: 2026-10-24T07:48:00Z
event: changed-head-delta
verdict: ADVISORY
reviewer: primary dot
review_uuid: 3aba64d8-497a-4da9-8207-a8b83671e4ee
posture: non-gating ADVISORY under R18

# layibabalola/adobe-document-cloud-ingester #8 / 3078f640abd452d5f5c8fb32cb889d459155ebab / ADVISORY
## Blockers
None newly demonstrated. Prior SHADOW-HOST-BUSY-BYPASS source-addressed: ListingProbe.cs:84,94-95 rejects open-shadow surfaces/rows and slotted/contained composition; tests:457-478 add six rejection fixtures. Composed-ancestor visibility/clipping gap addressed by rejection, not support. Native-table/nonempty safeguards retained.
## Improvements
Program.cs:78-83,95,114 Task.Run(...).WaitAsync bounds awaiting, not filesystem work. Document/quiesce outstanding work before reuse and add delayed-preparation/gate-write fixtures. Hardening, not observed production failure.
ListingProbeTests.cs:332-359 still assumes DEBUG/PWDEBUG/DEBUG_FILE absent; isolate/restore environment.
ListingProbe.cs:345-355,320-323 still maps IMS errors/timeouts to SessionChanged. Fail-closed diagnostic concern, not blocker.
## Nits
ListingProbe.cs:202-205 “no early exit” conflicts with intentional OffSession return:267-270; qualify no early successful-count exit.
## Coverage and readiness
Complete four-file +143/-46 delta/immutable implementation/tests source-first; prior findings exposure disclosed. Early off-session and pre/post-IMS document checks prevent later structure reads after observed session change.
Post-pass Grok6381423600 matches IMS-label and uncancelled-background-work hardening; also attributes cell-clamp false partial and full-viewport short-list limitation. Its118testPASS attributed, not our execution. No SHARED BLOCKER.
Open/non-draft/CLEAN, zero checks/statuses/reviews, synthetic83240d0eaf68de5fa8b6084afff8308da25f172e no runs. Exact-head factory independent keys/requiredCI/actualtree/applicable third key unverified. No tests/browser/live operations; PR plans grant no permission.
R18 advice never authorizes merge or waives independent keys/CI/third-key/reserved-human requirements. ACK/DISTINGUISH within24h citing UUID; older duties retained.
Signed: primary dot.
