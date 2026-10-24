schema: cos-feedback.v1
project: adobe-ingester
repo: layibabalola/adobe-document-cloud-ingester
pr: 6
head: 5f06ca417b4fe5f15cdf9f81f249fcbb01cf903e
reviewed_utc: 2026-10-24T03:48:22Z
event: changed-tip-delta
verdict: ADVISORY
reviewer: primary dot
review_uuid: a02506ea-d3cd-45d5-8a5a-23ce6ab03b71
posture: non-gating ADVISORY under R18

# layibabalola/adobe-document-cloud-ingester #6 / 5f06ca417b4fe5f15cdf9f81f249fcbb01cf903e / ADVISORY
## Blockers
B1 P2 LATE-READ-TIMEOUT-FAIL-OPEN. spikes/adobe-session/AdobeSessionSpike/Program.cs:1947-1951 discards a timed-out final IMS observation and calls Decide(history). With2s budget, SignedIn reads at0/.5/1s do not early-return (1954-1958 excludes AcrobatRoot); read at1.5s times out at2s, then1982-1986 accepts the previous3samples. ClassifyAsync2047-2056/Resolve2085 return Authenticated with absent marker; Main123 cannot detect it when URL/navigation remain unchanged. Return Error/Unstable on timeout, not successful stale history. Source-proven fail-closed gap, not observed live signed-out acceptance.
## Improvements
SessionBoundaryTests.cs:798-817 uses completed reads/fake elapsed increments, missing this exception branch. Add timeout after3SignedIn samples expecting fail-closed21, plus empty-history timeout.
Prior SETTLE-BUDGET-OVERRUN is source-addressed by pre-read expiry, remaining-budget WaitAsync, capped delay and zero reads atzero budget. Prior privacy suppression remains; strict boolean IMS and navigation tracking address earlier hardening.
## Nits
Post-pass Grok6379281941 notes abandoned read task observation and undocumented short-budget unstable outcome; attributed hardening, not SHARED BLOCKER.
## Coverage and readiness
Complete3file delta from650e02e3, immutable surrounding source/tests before same-tip feedback. No execution/browser/liveAdobe actions. Post-pass Grok found no blockers; no independent matching blocker.
Live open/non-draft/CLEAN; zero head checks/statuses/runs. Exact-head independent Claude+Codex/HIGH-RISK third-key/requiredCI/actualtree evidence unverified; live/commit claims not authority.
R18 ADVISORY never merge authorization or CoS gate. Preserve factory evidence, CI, third-key, ACK and reserved-human/live-action requirements. ACK/DISTINGUISH within24h citing UUID; old duties not reset.
Signed: primary dot.
