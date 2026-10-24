schema: cos-feedback.v1
project: adobe-ingester
repo: layibabalola/adobe-document-cloud-ingester
pr: 8
head: 9d2f2cab46a666bebfdbfacd20ef8c0930585f5c
reviewed_utc: 2026-10-24T10:19:35Z
event: pr-pushed
verdict: ADVISORY
ci_summary: zero checks/statuses/reviews; factory evidence unverified
reviewer: primary dot
review_uuid: 1a82b0f4-e27e-45f7-ad6c-1e1ca0ef1d72
posture: non-gating ADVISORY under R18

# layibabalola/adobe-document-cloud-ingester #8 / 9d2f2cab46a666bebfdbfacd20ef8c0930585f5c / ADVISORY
## Blockers
B1 P2 ROW-PAINT-ESCAPE: spikes/adobe-session/AdobeSessionSpike/ListingProbe.cs:151-155 checks border-box containment, not painted extent. In Header+Rows, put a 1x1px absolute child at left:0;top:0 inside a position:relative counted row; give it pointer-events:none;z-index:1000;box-shadow:0 0 0 2000px white. Its box stays inside its row while opaque shadow covers siblings. Box shadow changes neither layout nor scrollable overflow; hit-testing passes through, unsupportedPaint omits boxShadow, and ownerRow exemption skips it. Static trace reaches stable Counted for an obscured list, contrary to README:190-193. Refuse unsupported ink overflow before exemption and add this fixture. Not executed.
## Improvements
ListingProbe.cs:145-148 also rejects non-generated or zero-size pseudos, and pseudos whose host/ancestor is display:none or opacity:0. Check proven non-painting cases without requiring nonzero host geometry; zero-size hosts may own real fixed overlays. Conservative false refusals, not leakage.
Prior guarded-query sentinel tests, DEBUG/PWDEBUG/DEBUG_FILE fixture isolation and uncancelled filesystem WaitAsync work remain.
## Nits
ListingProbe.cs:72-73 visibility prose remains stale; README computed-style inventory lacks contain/position. Tests:427 regex is a guard, not complete obfuscation detection.
## Coverage and readiness
Full source-first three-file +24/-8 delta from3a87c3e. Exact prior oversized-row-descendant box case fixed by containment; paint escape remains. Three fixtures/pins, paint containment and pseudo checks reviewed. Prior finding exposure disclosed.
Post-pass Grok6382787595 reports151/151 and pseudo no-content/zero-size false refusals, attributed; matches improvement, not B1. No SHARED BLOCKER.
Open/non-draft/CLEAN, zero checks/statuses/reviews; synthetic39393a11b9bad7de72bd10f4424478df1ec0eb0f has no runs. Independent keys/requiredCI/actualtree/applicable thirdkey unverified. No tests/browser/live Adobe.

R18 advice never authorizes merge or waives factory evidence/reserved actions. ACK/DISTINGUISH within24h citing UUID; older duties retained.
Signed: primary dot.
