schema: cos-feedback.v1
project: adobe-ingester
repo: layibabalola/adobe-document-cloud-ingester
pr: 8
head: 5471aefd41009b0d619bcf7495491e7c8927076c
reviewed_utc: 2026-10-24T12:56:40Z
event: pr-pushed
verdict: ADVISORY
ci_summary: zero exact-head checks/statuses/runs; independent evidence unverified
reviewer: primary dot
review_uuid: f7333363-504d-4d73-8d16-630df193cbe4
posture: non-gating ADVISORY under R18

# layibabalola/adobe-document-cloud-ingester #8 / 5471aefd41009b0d619bcf7495491e7c8927076c / ADVISORY
## Blockers
No new demonstrated functional defect or text-output leak in this delta. This is NOT approval of expanded live-data access.
## Improvements
ListingProbe.cs:108-111 now refuses rendered progress/progressbar inside the selected surface; :126-127 refuses all-whitespace data rows before incrementing the count. Four fixtures and fixed-output grammar assertions added.
Privacy contract changed: :127 reads cell textContent to derive a boolean. README:179-182 discloses this, but :133-134 and PR body still claim no reading/no text. Reconcile these claims and retain applicable owner authorization before live use; count-only output does not mean no text access. Paint visibility remains previously withdrawn, not repaired or owner-approved.
Static trace finds only fixed labels/count returned; catch:152, Parse:190-216 and read catch:410-412 do not echo text/exceptions. This is bounded source evidence, not universal leak-proof certification.
## Nits
Existing COL/COLGROUP and page-wide malformed-role refusals remain hardening. Progressbar on a real row can conservatively refuse the entire surface; unrelated malformed progressbar also refuses page-wide (:91-94). Prior sentinel/debug-environment/uncancelled-wait concerns retained.
## Coverage and readiness
Source-first complete three-file/two-commit delta from a01bb23; 2ce2 committed12:51:19,5471 test-only12:53:58. No execution/browser/live Adobe. Prior finding exposure disclosed.
Post-pass Grok6384451067 binds older2ce2, G3/G4 match hardening, not SHARED BLOCKER; G1/G2 remain unanswered. No same-tip independent review verified.
Open/non-draft/CLEAN; zero exact-head checks/statuses/runs, zero formal reviews. Synthetic e39975a4899e8fdb9e3280e9d474667d18dfafe3 has no verified CI. Independent keys/required CI/actual-tree/applicable third key unverified.

R18 advice never authorizes merge or waives factory evidence or reserved actions. Equal dot/Muse/Grok duty: substantive defect disposition target15min; nonurgent improvements24h outer duty, same-thread ACK:/DISTINGUISH:. Older duties retained.
Signed: primary dot.
