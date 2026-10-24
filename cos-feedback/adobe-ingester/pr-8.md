schema: cos-feedback.v1
project: adobe-ingester
repo: layibabalola/adobe-document-cloud-ingester
pr: 8
head: 1fdaa069502007dbe594ae50ddfde0b0f75c7584
reviewed_utc: 2026-10-24T07:17:50Z
event: changed-head-delta
verdict: ADVISORY
reviewer: primary dot
review_uuid: 68d9a8a4-6909-4dbd-9905-c22b8c4968c8
posture: non-gating ADVISORY under R18

# layibabalola/adobe-document-cloud-ingester #8 / 1fdaa069502007dbe594ae50ddfde0b0f75c7584 / ADVISORY
## Blockers
B1 P2 SHADOW-HOST-BUSY-BYPASS. spikes/adobe-session/AdobeSessionSpike/ListingProbe.cs:80,90 discovers open shadow-root grids, but closest('[aria-busy="true"]') stops at the shadow boundary. Add aria-busy="true" to host h in ListingProbeTests.cs:457-461 shadowOnly fixture: unchanged grid yields aria-grid:2:3 and stable Counted despite loading ancestor. Static source counterexample, not executed/live-Adobe claim. Walk composed ancestors via ShadowRoot.host or fail closed on unsupported shadow contexts; add host-busy fixture.
## Improvements
ListingProbe.cs:75-78,108 has the same composed-ancestor gap for aria-hidden/inert/dialog exclusion and host clipping. Cover host attributes/nested shadows.
ListingProbeTests.cs:332-359 profile-output test depends on ambient DEBUG/PWDEBUG/DEBUG_FILE being absent; isolate/restore these variables. Not observed CI failure.
Post-pass Grok6381137320 no blocker: IMS timeout still mislabeled SessionChanged and clamped-cell overflow falsely PartialListSurface are attributed hardening. No SHARED BLOCKER.
## Nits
ListingProbeTests.cs:416 covers native role=grid; also pin exact prior role=table counterexample.
## Dispositions and readiness
Prior NATIVE-TABLE-ROLE-ZERO source-addressed by native row/cell selectors and missing-header/nonempty rejection. Hidden rows addressed by shown(row)/fixture; URL wording corrected. Shared session decision, separate read exceptions and cleanup invalidation retained.
Complete four-file +478/-257 delta and immutable implementation/tests source-first; prior review exposure disclosed. No tests/browser/live operations. Grok104testPASS is attributed, not our evidence.
Open/non-draft/CLEAN. Zero checks/statuses/reviews; synthetic88f052399a722691d8407093d3bd430b03e7f1e2 no runs. Exact-head independent factory keys, requiredCI, actual merged-tree and applicable third key unverified. PR live plans grant no authority.
R18 advice never authorizes merge or waives independent keys/CI/third-key/reserved-human requirements. ACK/DISTINGUISH within24h citing UUID; prior duties preserved.
Signed: primary dot.
