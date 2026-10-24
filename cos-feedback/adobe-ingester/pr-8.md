schema: cos-feedback.v1
project: adobe-ingester
repo: layibabalola/adobe-document-cloud-ingester
pr: 8
head: e7bd5b6a47564ec757b37b2bf899d58f199b8d5f
reviewed_utc: 2026-10-24T08:47:20Z
event: changed-head-delta
verdict: ADVISORY
reviewer: primary dot
review_uuid: 4d17538d-384f-49bb-a47d-72e0ea1ec118
posture: non-gating ADVISORY under R18

# layibabalola/adobe-document-cloud-ingester #8 / e7bd5b6a47564ec757b37b2bf899d58f199b8d5f / ADVISORY
## Blockers
None newly demonstrated. Own-element visibility, hidden surfaces/rows with shown descendants, clip/clip-path refusal and border/scrollbar ambiguity refusal have source changes and seven fixtures. Prior shadow-host B1 remains source-addressed.
## Improvements
spikes/adobe-session/AdobeSessionSpike.Tests/ListingProbeTests.cs:531-537 still lacks a structural-query sentinel proving no inspection on off-session refusal; source guard at ListingProbe.cs:147-150 short-circuits correctly.
ListingProbeTests.cs:332-360 still lacks DEBUG/PWDEBUG/DEBUG_FILE isolation. Program.cs:78-83,95,114 WaitAsync does not cancel underlying filesystem work or establish one end-to-end deadline. Carry-forward hardening, not new delta blockers.
## Nits
ListingProbe.cs:72-73 incorrectly says every ancestor's visibility is checked; new79-81 intentionally uses own visibility. At223-226 qualify no early successful-count exit because289-293 returns early on refusal.
## Coverage and readiness
Complete three-file +20/-7 delta and immutable implementation/tests/README/context source-first; prior findings exposure disclosed. Updated hash pins separated from seven fixtures.
Post-pass Grok6382013533 reports a benign bordered overflow:hidden card rejected at ListingProbe.cs:130. Concrete reproduction and133/133 tests are attributed, not ours; classic Windows scrollbar impact explicitly inferred. Conservative fail-closed compatibility, not a new count-safety blocker. Earlier ellipsis/IMS-error-label notes remain attributed. No SHARED BLOCKER.
Open/non-draft/CLEAN, zero checks/statuses/reviews; synthetic193230e361a37633ed3e7512428e0fb660643b7b has no runs. Exact-head independent factory keys/requiredCI/actual merged-tree/applicable thirdkey unverified. No tests/browser/live Adobe; PR plans grant no authority.

R18 advice never authorizes merge or waives independent keys/CI/third-key/reserved-human requirements. ACK/DISTINGUISH within24h citing UUID; older duties preserved.
Signed: primary dot.
