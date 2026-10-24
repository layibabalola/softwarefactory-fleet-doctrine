schema: cos-feedback.v1
project: adobe-ingester
repo: layibabalola/adobe-document-cloud-ingester
pr: 8
head: 2d4670237a12e0e12c0a95e4300dcfbb4eb49078
reviewed_utc: 2026-10-24T06:49:10Z
event: first-ready-review
verdict: ADVISORY
reviewer: primary dot
review_uuid: 2c80132b-bb8a-470d-b718-66e64740875f
posture: non-gating ADVISORY under R18

# layibabalola/adobe-document-cloud-ingester #8 / 2d4670237a12e0e12c0a95e4300dcfbb4eb49078 / ADVISORY
## Blockers
B1 P2 NATIVE-TABLE-ROLE-ZERO. spikes/adobe-session/AdobeSessionSpike/ListingProbe.cs:60,66-69 classifies native table role="table" as aria-table, then only selects explicit role=row/cell descendants. A visible one-row native tr/td table with redundant table role returns aria-table:0:0:na; three readings produce Counted/item_count=0 instead of1. Static counterexample, not execution. Respect native implicit semantics or fail closed on unsupported mixtures; add synthetic fixtures.
## Improvements
ListingProbe.cs:67-76 counts hidden descendant rows within visible surface. Define rendered-row policy; test hidden/aria-hidden/display:none and header subtraction with aria-rowcount. ListingProbeTests.cs:315-343 only hides whole surfaces, missing both cases.
Post-pass Grok6380873688 attributes mixed header/data-row rejection, aria-rowcount=-1 rejection and timeout-as-SessionChanged diagnostic ambiguity. No matching independent blocker, no SHARED BLOCKER.
## Nits
ListingProbe.cs:6-8 says no URLs read, but264-282 reads page.Url internally. Clarify not emitted.
## Coverage and readiness
Complete substantive four-file patch and immutable session-host callchain source-first; no execution/live Adobe. Fixed-label/count grammar suppresses profile path; one-use login gate/profile lease and post-cleanup invalidation retained. PriorAdobe6timeoutfailclosed retained. Grok's80passingtests/106base-equivalent failures attributed, not our test evidence.
Open/non-draft/CLEAN; zero checks/statuses, synthetic589239f11bb0d893c2b4ef45ac0a2a37ebd50e12 has no runs. Exact-head independent factory keys/requiredCI/actualtree/HIGH-RISK third key unverified. PR live-run plans grant no authority.
R18 advice never authorizes merge or waives independent keys/CI/third-key/reserved-human requirements. ACK/DISTINGUISH within24h citing UUID; older duties preserved.
Signed: primary dot.
