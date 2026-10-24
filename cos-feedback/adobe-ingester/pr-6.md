schema: cos-feedback.v1
project: adobe-ingester
repo: layibabalola/adobe-document-cloud-ingester
pr: 6
head: 650e02e3327e18a8b89368e7085259cc82da4a06
reviewed_utc: 2026-10-24T03:19:47Z
event: first-ready-review
verdict: ADVISORY
reviewer: primary dot
review_uuid: e4c9ade3-cea2-4e64-9e0a-1de99e79a4c5
posture: non-gating ADVISORY under R18

# layibabalola/adobe-document-cloud-ingester #6 / 650e02e3327e18a8b89368e7085259cc82da4a06 / ADVISORY
## Blockers
B1 P2 SETTLE-BUDGET-OVERRUN. spikes/adobe-session/AdobeSessionSpike/Program.cs:1911-1925 starts read before checking budget, even zero, then sleeps full500ms; ReadAsync:1970 uses fixed3s rather than remaining budget. Example operation timeout10s/elapsed8s gives BudgetFor=0, but a pending Acrobat read still starts; operation cancellation after2s escapes the read catch and maps to Cancelled/70 rather than intended fail-closed21. With3s budget, read2.9s+delay0.5s+read2.9s seeks6.3s, exceeding the6s operation remainder. Check deadline before reads/after delay, cap both to remaining budget, and define zero-budget outcome; add boundary loop fixtures. Static source trace, not executed. Late-read pattern pre-existed; new clamp incompletely fixes it. Post-pass Grok6378958606 matches overrun as hardening, not an independent blocker verdict; no SHARED BLOCKER.
## Improvements
Prior #4/#5 unknown-path privacy B1 is source-addressed on this tip by fixed allowlisted labels/suppression. Prior unbounded IMS evaluation now has3s timeout plus cancellation; overall clamp issue remains above. Post-pass Grok truthy-nonboolean IMS and same-URL reload concerns are attributed, not newly demonstrated here.
## Nits
Post-pass Grok notes short budgets can yield unstable/21 without three readings; document this fail-closed limitation (attributed).
## Coverage and readiness
Complete three-file patch, source/tests/README and immutable call-chain review before same-tip feedback; no tests, browsers or live Adobe actions. Claimed live validation is not authority or independent proof.
Open/non-draft/CLEAN; zero head checks/statuses/workflow runs and zero synthetic merge runs. Exact-head independent Claude+Codex/HIGH-RISK third key, required CI and actual merged-tree evidence unverified.
R18 advisory is not merge authorization or a CoS gate. Preserve all factory evidence/CI/third-key/live-operation/reserved-human requirements. ACK/DISTINGUISH within24h citing UUID; prior duties not reset.
Signed: primary dot.
