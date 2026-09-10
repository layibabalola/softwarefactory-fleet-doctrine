schema: cos-feedback.v1
project: cloudvore
repo: layibabalola/Cloudvore
pr: 5
head: f03810c9ae389c6cb0207f9e679f6b2761d84274
reviewed_utc: 2026-09-10T17:32:28Z
event: pr-pushed
verdict: not-merge-ready
ci_summary: product-bar FAILED (C# compile in DropboxVault.App.Tests); tools-bar PASSED

## Blockers

- **CI: `product-bar`** — build of `tests/DropboxVault.App.Tests` fails on this head (run 34507601439). Test doubles do not match `IQueueJobExecutor.RunAsync(string, CancellationToken)` which now returns `Task<QueueRunResult>`:
  - CS0738 on `InertExecutor` / `UncooperativeExecutor` / `NoopExecutor` / `BlockingExecutor` in `VerdictPanelGateTests.cs`, `QueueShutdownWindDownTests.cs`, `VerdictPanelRenderTests.cs`, `HistoryContradictedPairTests.cs`, `VolumeArrivalServiceTests.cs`, `SetFaultDisclosureTests.cs`, `QueueViewModelSetGroupingTests.cs`
  - CS0104 ambiguous `QueueRunResult` (`DropboxVault.Core.Jobs` vs `DropboxVault.App.Services`) in `VerdictPanelRenderTests.cs`, `QueueViewModelSetGroupingTests.cs`, `VolumeArrivalServiceTests.cs`
  - Unblock: update test doubles to return `Task<QueueRunResult>` (prefer Core.Jobs type explicitly) and re-run product-bar. Core.Tests already green (978 passed). This failure is outside the docs diff — fix on a sibling PR or rebase after master is green.

## Improvements

- `agents/doctrine-consumer.md`: template link points at the fleet PR #57 branch blob; once #57 merges, retarget to `master` so the stub does not rot on a deleted branch ref.
- Adoption checklist item for Get-DoctrineBrief-equivalent is correctly deferred; keep stub zero-authority until that lands.

## Notes

- Docs-only head (`+53/−0`, 3 files): new `agents/doctrine-consumer.md` plus Fleet doctrine consumer pointers in `AGENTS.md` / `CLAUDE.md`. Latest push requires briefs to include `cos-feedback/cloudvore/pr-*.md` when present (fail soft if missing).
- Scope: CANDIDATE_ZERO_AUTHORITY stub; cites fleet PR #57 and MLV-App #107. No runtime wiring in this PR.
- Content review: stub and Law 1 / checklist look coherent; merge blocked only by product-bar compile failures above, not by the docs themselves.
- CoS did not post on the GitHub PR.