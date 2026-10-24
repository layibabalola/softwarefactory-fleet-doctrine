schema: cos-feedback.v1
project: adobe-ingester
repo: layibabalola/adobe-document-cloud-ingester
pr: 8
head: a0510ba2c76d64ccc39bed4c974541eb6e14969d
reviewed_utc: 2026-10-24T08:18:00Z
event: changed-head-delta
verdict: ADVISORY
reviewer: primary dot
review_uuid: c3c02964-66af-4f40-a1f9-5deefc54be49
posture: non-gating ADVISORY under R18

# layibabalola/adobe-document-cloud-ingester #8 / a0510ba2c76d64ccc39bed4c974541eb6e14969d / ADVISORY
## Blockers
None newly demonstrated. Prior shadow rejection retained/strengthened; surface-owned shadow, x/y clipping and display:contents cases fail closed.
## Improvements
spikes/adobe-session/AdobeSessionSpike.Tests/ListingProbeTests.cs:524-543 asserts refusal/destruction but not absence of structure reads. Add query counter/throwing sentinel proving off-session paths never inspect structure.
Prior DEBUG/PWDEBUG/DEBUG_FILE fixture isolation remains absent at332-359; Program.cs:78-83,95,114 WaitAsync still does not cancel background filesystem work.
## Nits
ListingProbe.cs:218-221 says no early exit despite intentional off-session return; qualify no early successful-count exit.
## Coverage and readiness
Complete three-file +104/-41 delta and immutable implementation/tests source-first; prior findings exposure disclosed. ListingProbe.cs:140-145,360-380 performs synchronous guarded IMS+structure read through document handle, with mismatch/destroyed-context fixtures.
Post-pass Grok6381708752 attributes ellipsis-cell clipping false partial and read errors reported SessionChanged; updated docs intentionally group errors, still diagnostic hardening. Its126testPASS attributed, not our execution. No SHARED BLOCKER.
Open/non-draft/CLEAN,zero checks/statuses/reviews; synthetic4f0e2b1abcf235ea7742fd52fc4fa26c98fc3738 no runs. Exact-head independent factory keys/requiredCI/actualtree/applicable thirdkey unverified. No tests/browser/live Adobe; PR plans grant no authority.

R18 advice never authorizes merge or waives independent keys/CI/third-key/reserved-human requirements. ACK/DISTINGUISH within24h citing UUID; older duties preserved.
Signed: primary dot.
