schema: cos-feedback.v1
project: adobe-ingester
repo: layibabalola/adobe-document-cloud-ingester
pr: 8
head: a01bb23ef893e2e29ae069f48c6d15b43084f136
reviewed_utc: 2026-10-24T12:22:50Z
event: pr-pushed
verdict: ADVISORY
ci_summary: zero checks/statuses/reviews; independent evidence unverified
reviewer: primary dot
review_uuid: a9ede705-3554-4a24-a8cc-5b72c084ed58
posture: non-gating ADVISORY under R18

# layibabalola/adobe-document-cloud-ingester #8 / a01bb23ef893e2e29ae069f48c6d15b43084f136 / ADVISORY
## Blockers
No new demonstrated defect in this delta under rendered-DOM-membership contract. Paint visibility remains withdrawn, NOT repaired or owner-authorized scope change.
## Improvements
ListingProbe.cs:90-93 now rejects whitespace/case/fallback list roles before exact selectors omit them; :124 rejects data-shaped THEAD rows before counting. Nested-owner rows now refuse at :114 instead of silently skipping a presentation-table subtree. Seven fixtures added across both commits; pins updated.
ListingProbe.cs:144-148 COL/COLGROUP skeleton false-refusal remains conservative hardening. README:158-166 all-DOM wording still exceeds rendered-row behavior; prior sentinel/debug-environment/uncancelled-wait concerns unchanged.
## Nits
ListingProbe.cs:90-93 page-wide malformed-role refusal also rejects unrelated header cells; narrow only with omission coverage preserved. ListingProbeTests method names still overstate paint refusal.
## Coverage and readiness
Source-first full two-commit/three-file delta from6574cd5 (first+17/-4, second+6/-3), prior exposure disclosed. No tests/browser/live Adobe.
Post-pass Grok6384138020 reports166 passes and matching G1 column/G2 pagewide hardening on exacthead, attributed; no SHARED BLOCKER. Track its same-thread24h ACK/DISTINGUISH duty without duplicate ask.
Open/non-draft/CLEAN,zero checks/statuses/reviews. Synthetic4b017bc7a43d80238a0f54eeff96040778efce5a no runs. Independent keys/requiredCI/actualtree/applicablethirdkey unverified.

R18 advice never authorizes merge or waives independent keys/CI/third-key/reserved actions. ACK: or DISTINGUISH: on the same thread within24h citing UUID; older duties retained. Owner-confirmed equal reply duty applies to Muse/Grok asks too.
Signed: primary dot.
