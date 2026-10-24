schema: cos-feedback.v1
project: adobe-ingester
repo: layibabalola/adobe-document-cloud-ingester
pr: 8
head: 6574cd51416ef1ff8629e862bf971fa59ac0218e
reviewed_utc: 2026-10-24T11:48:20Z
event: pr-pushed
verdict: ADVISORY
ci_summary: zero checks/statuses/reviews; independent factory evidence unverified
reviewer: primary dot
review_uuid: 8a01dfd2-cef9-4dba-9818-c3c208721ed5
posture: non-gating ADVISORY under R18

# layibabalola/adobe-document-cloud-ingester #8 / 6574cd51416ef1ff8629e862bf971fa59ac0218e / ADVISORY
## Blockers
No new demonstrated wrong-count defect in this delta under the narrower rendered-DOM-membership contract. Prior PERSPECTIVE-SHADOW-ESCAPE is scope-disclaimed, NOT geometrically fixed: ListingProbe.cs:103-145 deletes paint checks. The earlier obscured-list counterexample remains valid against the former human-visible-row promise; this record does not authorize changing owner requirements.
## Improvements
README.md:158-168 narrows count scope and attributes adjudication to other sessions. That claim is not owner authorization or independent factory evidence. Keep the withdrawn paint guarantee explicit in downstream evidence and do not describe prior findings as implemented fixes.
README:158-162 says data rows in the DOM, but ListingProbe.cs:110-112 still intentionally omits non-rendered rows (existing tests:462). Say rendered-DOM membership, not all DOM rows.
ListingProbe.cs:141-145 may conservatively reject ordinary COL/COLGROUP geometry as skeletons; post-pass Grok6383635873 reports this at 9c62fdf7, not exact reviewed head. Validate a column-sizing fixture before narrowing exemptions.
Prior guarded-query sentinel, debug-environment isolation and uncancelled filesystem-wait hardening remain unchanged.
## Nits
ListingProbeTests.cs:499,580 method names still imply paint/clipping refusal although updated cases intentionally count obscured content.
## Coverage and readiness
Full source-first three-file +76/-105 delta from910ddba4; source and tests retain one-surface/header, row/cell visibility, aria-rowcount, overflow/viewport, busy/skeleton, centre-hit and session/document guards. Prior findings exposure disclosed. No tests/browser/live Adobe executed.
Post-pass author6383606108 explains explicit scope withdrawal; Grok6383635873 reports159 passes on9c62fdf7, attributed and not exact-tip proof. No SHARED BLOCKER.
Open/non-draft/CLEAN; zero checks/statuses/reviews. Synthetic b65d3e308c9a5debc6abcb3908e71652167b2d9a has no runs. Independent keys/requiredCI/actualtree/applicable thirdkey remain unverified.

R18 advice never authorizes merge or waives independent keys/CI/third-key/reserved actions. ACK/DISTINGUISH within24h citing UUID; older duties retained.
Signed: primary dot.
