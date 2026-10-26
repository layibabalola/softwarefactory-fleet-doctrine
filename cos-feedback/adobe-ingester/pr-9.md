schema: cos-feedback.v1
project: adobe-ingester
repo: layibabalola/adobe-document-cloud-ingester
pr: 9
head: 1909d7b78cc99743ebff8751c9eaf94be2d7417a
reviewed_utc: 2026-10-26T21:13:20Z
event: source review and evidence reconciliation
verdict: ADVISORY
reviewer: primary dot
review_uuid: 3329f361-fcad-41a1-9be4-bf132c9881b2
posture: non-gating ADVISORY under R18

# layibabalola/adobe-document-cloud-ingester #9 / 1909d7b78cc99743ebff8751c9eaf94be2d7417a / ADVISORY

## Blockers
No demonstrated code blocker in the four-file login-close delta. spikes/adobe-session/AdobeSessionSpike/Program.cs:2179–2239 snapshots page closure before cleanup and suppresses only exact Playwright-owned TargetClosedException. Action failures remain failures; probe classification unchanged.

Required independent-review/CI evidence is unestablished, not passed: fetched GitHub comments/reviews/threads/statuses and PR-triggered workflow runs were empty; workflow lookup scope is limited. Claude attribution and “Codex round-2” commit wording do not authenticate independent legs.

## Improvements
spikes/adobe-session/AdobeSessionSpike.Tests/SessionBoundaryTests.cs:285–326 exercises production helper/default predicate with real internal exception, open-page rejection, unrelated errors, cancellation, crash and cleanup-induced closure. Against base97754221510bb515348684884d00ce251df347e1, original unconditional finally propagates expected close exception: source-supported discrimination, not executed fail-old/pass-new.

Add actual WaitForBrowserCloseAsync crash-path coverage: browser-backed crash test returns directly after Crash, bypassing login polling loop. Head claims257/257 tests; body253 and4/8→8/8 live experiment remain actor claims, not verified exact-head execution.

## Nits
Refresh body exception-policy description and test count.

## Scope/evidence
Localized lifecycle code, tests/docs; no dependencies/import-export/credential export/probe-verdict expansion. Source-first then feedback comparison; no prior same-tip findings exposed. Pinned Playwright1.52 BrowserContext.CloseAsync marks CloseWasCalled before awaits, making second await-using close a no-op; no double-cleanup defect demonstrated. Source: https://github.com/microsoft/playwright-dotnet/blob/v1.52.0/src/Playwright/Core/BrowserContext.cs#L321-L367 .
Live head rechecked21:10Z, open/non-draft. No login or other product execution.

No tests/workflows executed. R18 advisory, not merge authorization/factory leg. Preserve exact-head independent keys, required/merged-tree CI, applicable third key, demonstrated-defect rules, denials and reserved-human requirements.

Signed: primary dot.
