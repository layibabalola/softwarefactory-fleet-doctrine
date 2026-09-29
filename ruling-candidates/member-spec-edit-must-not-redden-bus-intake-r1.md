# CANDIDATE r1: a member's spec edit must not turn bus intake red (zero runtime authority)

Status: PROPOSED 2026-09-29 by a bus-auditor chat session (record only).

## Evidence

- `adoption/current-token-control-r26.json` pins each project spec's evidence: the last commit and the blob
  OID. `tests/test_current_adoption_ledger.py` fails with `PROJECT_SPEC_DRIFT` whenever a member edits its
  own `specs/<project>.md`.
- On 2026-09-29 the census was re-pinned at 08:25 CDT (Landing B2, `68cc500`). The adobe-ingester spec
  addendum `a034fda` at 10:41 CDT turned R26 intake red again on the next bus push (`1b942ab`). The fix was a
  third tool-verbatim refresh (`0401993`), keyed by a cross-family key.
- Project specs saw 34 commits between 2026-09-18 and 2026-09-29. At that rate, intake is red most of the
  time, and every red run costs a full matrix.
- The README pin in the r45 manifest had the same treadmill shape (22640ed, then re-broken three times).

## Proposal (pick one at ratification)

- **A. Refresh in the same commit.** A member push that edits `specs/<project>.md` must carry the
  refreshed census in the same commit. Enforce this with a CI job that runs
  `tools/refresh_current_adoption_census.py` and fails with a specific, actionable message. The job must
  not be a git hook: hooks run with `GIT_DIR` set (63ca737 TRAP).
- **B. Check what the pin is actually for.** The current-ledger check treats a member-owned spec edit as
  expected drift. It still refuses unclassified specs, closed-set changes, and any change to a pinned
  disposition. It stops refusing a newer commit on the member's own spec. The historical check stays strict.
- **C. Status quo.** A bus steward refreshes after every member spec edit. This is the measured cost today.

A and B both need changes to sealed `tools/check_adoption_ledger.py` and the intake epoch, so either one is
an epoch amendment (precedent 8727672 and Landing B, packet r2) run as its own K1/K6 subject.
