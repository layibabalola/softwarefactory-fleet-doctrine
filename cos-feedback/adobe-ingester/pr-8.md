schema: cos-feedback.v1
project: adobe-ingester
repo: layibabalola/adobe-document-cloud-ingester
pr: 8
head: ca7f8d07dd4cad2ce7081efdef9d2bfc3eb797f6
reviewed_utc: 2026-10-24T10:50:20Z
event: pr-pushed
verdict: ADVISORY
ci_summary: see exact-head observations below; no merge authorization
reviewer: primary dot
review_uuid: a67ed4f5-c710-497d-87ae-bc1995c3b7aa
posture: non-gating ADVISORY under R18

# layibabalola/adobe-document-cloud-ingester #8 / ca7f8d07dd4cad2ce7081efdef9d2bfc3eb797f6 / ADVISORY
## Blockers
B1 P2 TRANSFORMED-SHADOW-ESCAPE: spikes/adobe-session/AdobeSessionSpike/ListingProbe.cs:151-155 combines transformed getBoundingClientRect with untransformed CSS shadow lengths. In the stock1280x720 fixture, append a fixed right:0;bottom:0;1x1px element with transform:scale(100);transform-origin:bottom right;box-shadow:0 0 0 20px white;z-index:999;pointer-events:none. Border box is x1180..1280/y620..720; calculated reach20 misses grid centres x640/y26..134. Actual2000px shadow covers them. Hit-testing passes through and later box overlap also misses the grid. Static trace returns aria-grid:2:3/stable Counted. Refuse unsupported transformed shadow paint or compute conservative transformed extent; add this combined fixture. Not executed.
## Improvements
ListingProbe.cs:150-155 scans shadow styles before rendered/ancestor suppression; invisible elements can cause conservative false refusals. Layer lengths/negative spread/inset are overapproximated. Pseudo guard145-148 still omits generated-content/hidden-host checks. Prior query sentinels, debug-environment fixture isolation and uncancelled filesystem waits remain.
## Nits
Computed-style documentation/comment inventories need synchronization.
## Coverage and readiness
Full three-file +20/-6 source-first delta9d2f2ca→ca7f8d0. Prior untransformed2000px row-child shadow is source-addressed; transformed variant remains. Fourfixtures/pins; positioned pseudo refusal now includes relative/sticky. Prior findings exposure disclosed.
Post-pass Grok6383064320 reports155/155 and layered-shadow false refusal, attributed. No matching blocker/SHARED. Open/non-draft/CLEAN,zero checks/statuses/reviews; synthetic4eea39f7573d4ecc41107d1c9fac61b17cfa1a6b no runs. Independent keys/requiredCI/actualtree/applicable thirdkey unverified. No tests/browser/live Adobe.

R18 advice never authorizes merge or waives independent keys/CI/third-key/reserved actions. ACK/DISTINGUISH within24h citing UUID; older duties retained.
Signed: primary dot.
