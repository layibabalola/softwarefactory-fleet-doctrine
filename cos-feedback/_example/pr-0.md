schema: cos-feedback.v1
project: _example
repo: layibabalola/example-fleet-board
pr: 0
head: deadbeefcafebabe000000000000000000000001
reviewed_utc: 2026-09-10T12:00:00Z
event: pr-pushed
verdict: not-merge-ready
ci_summary: lint failed (eslint); unit green; e2e skipped

<!--
  EXAMPLE ONLY — not a live fleet board.
  Path cos-feedback/_example/ is a fixture for schema/docs readers.
  Do not treat this file as feedback for any real PR.
-->

## Blockers

- **CI: `lint` (eslint)** — `src/handlers/ingest.ts` line 88: unused import `LegacyParser`.
  Remove the import or use it; re-run `npm run lint`.
- **Merge: missing required check** — `e2e / smoke` is skipped on this head (`[skip e2e]` in
  commit message). Drop the skip token and push so required checks can run, or get an
  explicit owner waiver outside this file (this feedback cannot waive checks).

## Improvements

- `src/handlers/ingest.ts` (~lines 120–140): the retry loop logs the full response body on
  every attempt. Prefer status + request-id only (keeps CI logs small; avoids accidental PII
  in artifacts).
- `tests/ingest.test.ts`: add a case for empty payload (`{}`) — current suite only covers
  happy path and 500 from upstream mock.
- Consider splitting the 400-line `normalizeRow` helper; the PR diff is hard to review in one
  hunk (non-blocking style note).

## Notes

- EXAMPLE ONLY. Fake SHAs, check names, and paths.
- Review scoped to the fictional diff; no claim about any real repository.
- `verdict: not-merge-ready` here is illustrative data, not a ruling and not merge authority.
