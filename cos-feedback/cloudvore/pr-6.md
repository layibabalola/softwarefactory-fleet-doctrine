schema: cos-feedback.v1
project: cloudvore
repo: layibabalola/Cloudvore
pr: 6
head: 138df42ddc88bf34f76a288f27269b99e3db5e6c
reviewed_utc: 2026-09-10T18:12:22Z
event: pr-opened
verdict: merge-when-ci-green
ci_summary: product-bar IN_PROGRESS + tools-bar QUEUED on this head; content review clean (fixture-only)

## Blockers

(none for content)

## Improvements

- Optional follow-up (non-blocking): if Core.Jobs.QueueRunResult still appears unqualified in a future App.Tests file that must name the Core type, prefer a fully-qualified name or a second alias (`CoreQueueRunResult`) rather than removing this project-wide App.Services pin — the interface return type is App.Services.

## Notes

- Fixture-only (+6/−0, 1 file): new `tests/DropboxVault.App.Tests/GlobalUsings.cs` with `global using QueueRunResult = DropboxVault.App.Services.QueueRunResult`.
- Unblocks the product-bar App.Tests compile failures noted on #5 / master (CS0104 ambiguous QueueRunResult; CS0738 on IQueueJobExecutor doubles). Interface lives in App.Services and returns App.Services.QueueRunResult; Core.Jobs.QueueRunResult is a different type for ScheduledReVerifyRunner — aliasing App.Services is the correct pin (supersedes earlier CoS hint on #5 that preferred Core.Jobs).
- No product behavior change. App.Tests need net8.0-windows / WPF — Linux box cannot verify locally; rely on product-bar.
- MERGEABLE; mergeStateStatus UNSTABLE only because checks unsettled.
- CoS did not post on the GitHub PR.