schema: cos-feedback.v1
project: adobe-ingester
repo: layibabalola/adobe-document-cloud-ingester
pr: 8
head: 910ddba446fa2b76dd7a91f59058b8df48386643
reviewed_utc: 2026-10-24T11:19:00Z
event: pr-pushed
verdict: ADVISORY
ci_summary: zero checks/statuses/reviews; independent factory evidence unverified
reviewer: primary dot
review_uuid: 96f059bf-53bd-485b-bd9f-dd082a1540bb
posture: non-gating ADVISORY under R18

# layibabalola/adobe-document-cloud-ingester #8 / 910ddba446fa2b76dd7a91f59058b8df48386643 / ADVISORY
## Blockers
B1 P2 PERSPECTIVE-SHADOW-ESCAPE: spikes/adobe-session/AdobeSessionSpike/ListingProbe.cs:156-164 bounds only matrix a,b,c,d, omitting perspective division. Append a fixed bottom-right1px box to stock Grid with pointer-events:none;z-index:999;box-shadow:0 0 0 20px white;transform:perspective(1000px) translateZ(990px);transform-origin:100% 100%. Matrix a=d=1,b=c=0,w=.01 keeps calculated reach20, but projected shadow spread is2000px. In1280x720 fixture the borderbox≈[1180,620,1280,720]; calculated bound misses grid centres, hit-testing ignores overlay, and later box overlap165-171 misses grid. Static CSS/source trace returns aria-grid:2:3/stable Counted for an obscured list. Refuse unsupported perspective/3D paint or bound complete projection, including ancestors. Add this fixture. Not executed or observed on Acrobat.
## Improvements
Prior scale(100)/individual-scale/ancestor-scale counterexamples and display:none shadow false refusal are source-addressed. Layer summation/negative-spread/inset overestimation remains conservative hardening. Pseudo no-content/zero-size/hidden-host refusal, guarded-query sentinel tests, debug-environment isolation and uncancelled filesystem waits remain unchanged.
## Nits
README:194-196 “upper bound” is too broad until projective transforms are handled; style inventory/visibility prose still need alignment.
## Coverage and readiness
Full source-first three-file+21/-7 delta fromca7f8d07; four new fixtures and pins, prior findings exposure disclosed. Analytic projection follows CSS Transforms2 §4.2 x/w,y/w, not runtime proof.
Post-pass Grok6383420351 reports159/159 and layered-shadow false refusal, attributed. Its “only grows” observation does not establish a projective bound. No matching blocker/SHARED.
Open/non-draft/CLEAN,zero checks/statuses/reviews; syntheticeb915fecac794894e73f1c8d715763e3e2bae757 no runs. Independent keys/requiredCI/actualtree/applicable thirdkey unverified. No tests/browser/live Adobe.

R18 advice never authorizes merge or waives independent keys/CI/third-key/reserved actions. ACK/DISTINGUISH within24h citing UUID; older duties retained.
Signed: primary dot.
