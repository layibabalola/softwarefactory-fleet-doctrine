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

## Addendum A1: proposed decision, 2026-10-17 (NOT ratified; zero authority)

Written by a Conjugal implementer session (Claude Opus 5.5). It records a decision proposal and its evidence.
It ratifies nothing, edits no sealed control, and grants no adoption, launch or runtime permission.

**Decision proposed.** Adopt **A′**, an A-variant that the writer enforces before the push and that needs no epoch
amendment. Keep **B** open as the structural fix, run as its own K1/K6 subject. Reject **C** as the standing mode.

**A′ as built.** Bus `hooks/pre-push-bus-tests.py` at bus `bfb30116` gained drift checks. The pushed range may
touch a path a sealed pin covers. Coverage is read from the pin at the pushed tip: the r45 `subjectFiles`,
the R26 census `specPath`s, the pin file itself, a new top-level `specs/*.md`, and the checker. When it does,
the layer checks the tip out into a temporary worktree. There it runs the checker CI already runs, in check
mode:

- r45: `tools/check_universal_manifest.py --treeish HEAD`
- R26: `tools/check_adoption_ledger.py --current --treeish HEAD`

On failure it refuses the push and prints the approved refresh for that token:

- `MANIFEST_SUBJECT_MISMATCH` prints `refresh_current_universal_manifest.py --candidate <tip>`.
- `PROJECT_SPEC_DRIFT` prints `refresh_current_adoption_census.py`.
- `PROJECT_CLOSED_SET_MISMATCH` says that no refresh can fix it without an epoch amendment (precedent bus
  `da3e22dc`).

The layer never refreshes. A refresh is a separate, reviewed commit on top of the refused tip, and the push
carries both commits.

**Why A′, not A as written.**

1. "Refresh in the same commit" cannot be done. The census needs `baseCommit` to be the commit it sits in, and
   each `evidence.commit` to be the last commit that touched the spec. So the refresh must be a second commit.
   What matters is the master tip after the push, and that tip is what CI checks.
2. "Must not be a git hook (63ca737 TRAP)." That trap is about GIT_DIR inheritance. The layer strips GIT_DIR,
   GIT_WORK_TREE, GIT_INDEX_FILE and the related variables from its own git calls and from every child. The
   tests push from a linked worktree, and their fixture checkers assert that GIT_DIR is absent:
   - bus `hooks/hooks.tests.py` `BusTests` and `BusDrift`
   - Conjugal `coordination/harvest/tests/test_bus_tests_layer.py`
3. A CI job runs after a direct push to master, so a red result is only advisory.

**Evidence.** Counted on bus `origin/master` from 2026-09-29 to 2026-10-17:

| Edits | Repairs | Red cause | Hand repairs on 2026-10-16 |
|---|---|---|---|
| 20 commits to census-pinned project specs | 3 census refreshes | `PROJECT_SPEC_DRIFT` / `PROJECT_CLOSED_SET_MISMATCH` | `da3e22dc`, `797d1b86` |
| 13 commits to `README.md` | 3 r45 re-pins | `MANIFEST_SUBJECT_MISMATCH` | `158a072e`, `9b08e709` |

Every unrefreshed edit reddened CI until the next repair.

Measured on the XPS 17 against bus `49009d20`, with other agents running:

| Push | Result | Time |
|---|---|---|
| Untouched (layer decision only) | passed | 0.54 s |
| `README.md` edit | refused | 16.6 s |
| `README.md` edit, refreshed tip, following the printed procedure | passed | 16.0 s |
| `specs/conjugal.md` edit | refused | 7.9 s |
| `specs/conjugal.md` edit, refreshed tip | passed | 7.4 s |
| New top-level spec | refused with `PROJECT_CLOSED_SET_MISMATCH` | 10 s |

The layer is installed by pin, under Law 1, in the bus clone that the Conjugal harvest steward pushes from,
along with every linked worktree of that clone (Conjugal `0d4312ba6`, `ce17dfd5e`). Five publish shapes ran
through `git push --dry-run` and all passed with no suite run:

- outbox appends to `TRAPS.md`, `RECEIPTS.md` and `specs/conjugal/cards.md`
- `metrics/scorecard-daily.jsonl`
- `metrics/product-share-lines.jsonl`

End to end, the installed layer took 1.17–1.38 s against a 1.44–1.53 s push round trip.

**What A′ does not do.**

- It covers only writers whose push passes through a clone with the layer installed. Pushes from other
  machines, the web UI, or clones without the layer can still redden CI, so CI stays the backstop.
- It moves the per-edit refresh cost from a steward after landing to the writer before landing. It does not
  remove that cost. Only **B** ends the treadmill for every writer, and **B** is an epoch amendment.
- A push that touches no covered path is not judged, even if master already carries drift. That is
  deliberate: no writer is refused for drift it did not cause.
- The layer does not strip `GIT_CONFIG_PARAMETERS`, the other half of the 63ca737 trap. No steward push uses
  `git -c`.

## Addendum A2: option B built, 2026-10-17 (NOT ratified; zero authority)

Written by a Conjugal implementer session (Claude Opus 5.5). It records a decision proposal, the change
built for it, and its evidence. It ratifies nothing and grants no adoption, launch or runtime permission.
Status stays PROPOSED until the owner rules.

**Decision proposed.** Adopt **B** as the standing fix, built as an epoch amendment at bus `2277ba4e`.
Keep A′ as defence in depth. Reject C. Reject a sibling-file split.

**Evidence that decided it.**

- A′ landed at bus `bfb30116` and was installed in one clone. Three census reds followed in 48 h, from three
  different writers, none through that clone: adobe-ingester headless fold `16ef646c`, dng-auto-processor
  `80a5873d`, and dng-auto-processor `76394aad`, pushed from another machine. Each needed a hand re-pin
  (`797d1b86`, `4c97e5b5`, `28f63f3b`). A writer-side control only works where it is installed, and the
  evidence says it will not be installed everywhere soon.
- A sibling-file split also depends on every writer changing its habits. It moves the same edits to a new
  path and leaves the old path's treadmill in place for any writer who misses the notice.
- Pinning only "normative sections" needs a section grammar that member specs do not share.
- The pin protects claims. Across all 66 spec edits on `origin/master` since 2026-09-18, the claim projection
  below never changed once. 12 of the 23 commits to census-pinned specs since 2026-09-29 removed lines, not
  only appended, so an append-only rule would still have reddened intake 12 times.
- Bus PRs #58 to #85 carried the red as "pre-existing", so reviewers learned to ignore a hard check.

**What B checks now** (`tools/check_adoption_ledger.py`, current mode only):

- The census stays exact at its base. The evidence commit is the last commit that touched the spec at
  `baseCommit`, and its blob is the pinned blob there.
- A later treeish may carry a different blob only if every claim the row reads from the pinned bytes is
  unchanged: the disposition marker set (DISTINGUISH, REJECT and ADOPT lines), whether the candidate and merge
  bindings appear, and, when pinned, every candidate-table row. Anything else is still `PROJECT_SPEC_DRIFT`,
  so the drift alarm, the pre-push layer and the printed refresh are unchanged.
- ADOPT rows and historical verification keep the exact-blob pin. No credit is derived from later bytes. The
  next refresh pins them.

**Tests.** `tests/test_current_adoption_ledger.py` gains admit cases (append, in-place prose) and refuse cases
(new marker, new ADOPT line, removed or added binding, removed candidate row, base drift, historical, ADOPT).
The pre-amendment checker fails the 5 admit cases. Dropping the candidate re-check fails the candidate-row case.
A real-git run on a scratch commit admitted an append to `specs/dng-auto-processor.md` and refused an appended
`REJECT(<merge>)`.

**Not covered.** The r45 `README.md` pin (`MANIFEST_SUBJECT_MISMATCH`) has the same treadmill shape and is not
changed here. A new top-level `specs/*.md` is still `PROJECT_CLOSED_SET_MISMATCH` by design.
