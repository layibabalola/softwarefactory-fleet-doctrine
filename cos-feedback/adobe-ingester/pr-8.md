schema: cos-feedback.v1
project: adobe-ingester
repo: layibabalola/adobe-document-cloud-ingester
pr: 8
head: 3a87c3e270b2d763e22454c33aa7985313be80d9
reviewed_utc: 2026-10-24T09:22:30Z
event: changed-head-delta
verdict: ADVISORY
reviewer: primary dot
review_uuid: 507f98e3-d3b4-473b-9911-bd0651840f09
posture: non-gating ADVISORY under R18

# layibabalola/adobe-document-cloud-ingester #8 / 3a87c3e270b2d763e22454c33aa7985313be80d9 / ADVISORY
## Blockers
B1 P2 ROW-DESCENDANT-PASS-THROUGH: spikes/adobe-session/AdobeSessionSpike/ListingProbe.cs:140-148 exempts every counted-row descendant. In the existing Header+Rows fixture, make the grid position:relative and insert an absolute inset:0 opaque white pointer-events:none div inside the first static data row. Its containing block is the grid, so it covers other rows too. Hit-testing passes through; rows.some(row.contains(e)) skips it. Earlier geometry/structure checks permit the fixture; source trace reaches aria-grid:2:3 and stable Counted, contrary to README:189 covered-row refusal. Ordinary loading mask, no hostile API forgery. Static demonstrated path, not executed. Restrict exemption without allowing row descendants to occlude other rows; add this combined fixture.
## Improvements
ListingProbeTests.cs:guarded-read tests still need query sentinels; Program.Main fixtures still need DEBUG/PWDEBUG/DEBUG_FILE isolation. Program.cs:69-71 now bounds root-lookup waiting, but filesystem work behind WaitAsync remains uncancelled.
## Nits
ListingProbe.cs:72-73 ancestor-visibility prose and :234-236 no-early-exit prose still need qualification.
## Coverage and readiness
Source-first e7bd5b6→00fb579 four-file +65/-23, then prepublication live-head move triggered full00fb579→3a87c3 three-file +48/-6 delta. Original surface-child overlay counterexample is now fixed/tested at ListingProbeTests.cs:478; broader omission narrowed to row descendants, not eliminated. Cell geometry, masks/filters, semantic-hidden rendering and final-deadline read changes inspected. Prior findings exposure disclosed.
Post-pass Grok6382477787 reports148/148/no blockers, attributed; discusses conservative edge overlays, not B1. No SHARED BLOCKER.
Open/non-draft/CLEAN; zero checks/statuses/reviews; synthetic501a540914e490b1fbc12fffff177dc27447804d has no runs. Independent keys/requiredCI/actualtree/applicable thirdkey unverified. No tests/browser/live Adobe.

R18 advice never authorizes merge or waives factory evidence/reserved actions. ACK/DISTINGUISH within24h citing UUID; older duties retained.
Signed: primary dot.
