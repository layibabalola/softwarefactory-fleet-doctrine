# Proposed R26 current-intake control epoch

Status: CANDIDATE_ZERO_AUTHORITY. This is an explicit successor control proposal
for independent review. A green CI run proves its recorded checks; it does not
ratify this proposal, adopt Doctrine in any project, or activate a runtime.

## Problem and resulting behavior

The old CI entry points combine two different questions: whether an immutable
publication was valid, and whether today's PR has that old publication's exact
change scope. Applying both to every later PR rejects legitimate later evidence.
The old adoption ledger also compares its historical spec population with HEAD.
The original Phase 17 publication additionally has the wrong parent and an
accumulated diff. Those are retained failures, not successful historical proof.

This proposed epoch verifies immutable history at its recorded subjects, then
checks today's project evidence with a separate current census and one explicit
current-event contract. The old checker CLIs, frozen constants and artifacts
remain available and keep their original refusal behavior. No old workflow hash
is repinned to new bytes.

## Verification obligations

The four-cell Windows/Linux, Python 3.13/3.14 intake workflow retains every
original unit-test module. Phase 6-16 immutable CLI checks remain. The new epoch
controller replaces the overlapping Phase 2/3/5 event CLI invocations with their
unchanged immutable batch validators, verifies Phase 12-16 publications and the
original workflow seal at `6ab0955b94ba3c2698bf9917e7718c4daf1cdc50`, and verifies
the original ledger at `53a48a6a0be5eade253ce1a508872d6874fd474a`.

Optional Phase 3/5 remote checks still run when the existing scoped read token is
configured. Missing remote credentials yield explicit unverified remote credit;
local checks do not claim host-local discovery or optional source-object proof.
The focused adoption workflow runs current-census tests and the same controller;
the full historical suite remains in all four always-on intake cells.

The new Phase 17 proof `e48a538919d339dc46e9fa239d918c3762eae635` has the required
Phase 16 sole parent. All six blobs equal those in the original failed
`b346dc9b20a5c624e8aa5db4278758d5fe956b6b` publication. The unchanged Phase 17
checker validates the new proof and must still reject the old publication's
accumulated scope. This establishes a new proof, not retroactive approval of the
original publication. Full-history checkout fetches the separately published
proof branch; unavailable objects fail the check.

## Current census semantics

The current profile keeps a fixed project population and explicitly names the
later portable specs, including their fleet-prefixed names. Each project spec
must match its latest committed evidence at the census base and HEAD.

Two changes apply only to the current profile. A canonical negative declaration
may name the R26 merge alone: the global candidate validator still binds that
merge's exact candidate, tree and parents. Historical project-candidate metadata
may be absent, granting no corresponding artifact credit. If it is present, its
exact original artifacts and declaration are still required. Cloudvore's current
spec removed its old candidate table; its current row therefore records no old
candidate credit rather than manufacturing that table.

Every ADOPT still requires the canonical merge, both subject text bindings, the
exact disposition line, profile and review artifacts, and all existing
non-regression receipts and controls. No missing profile becomes adoption. The
default historical profile retains its original mandatory candidate rules.
The current census remains 0 ADOPT, 6 DISTINGUISH and 3 STALE.

## Control boundary and bootstrap review

`adoption/current-intake-epoch-r1.json` seals the exact current workflow, checker,
unit-test and control-explanation files by Git blob, length and SHA-256. Every
imported checker is sealed before import; working edits beyond checkout line
endings are refused. Git object indirection, alternate stores and replacement
refs are refused. Original adoption artifacts and the original R26 manifest
cannot change relative to the bootstrap base.

The first PR/push from a base without this epoch must contain exactly the 17
paths enumerated in `BOOTSTRAP_CHANGED` in the proposed controller, relative to
its trusted event base. That base must descend from
`c57997bac73c7f1d3fe3ef386d23cdb9c5b0251d` and be an ancestor of HEAD. It returns
`BOOTSTRAP_CANDIDATE_REQUIRES_INDEPENDENT_REVIEW`. A later intake requires the
identical manifest and no sealed control-file changes. Control amendments fail
with `CONTROL_EPOCH_AMENDMENT_REQUIRED` and require their own reviewed successor.
Unknown project specs still fail the current census even if event scope is valid.
Manual runs validate the full evidence chain and grant no PR/push admission.

A repository-controlled validator is not an independent trust root for its own
amendment. Independent review of the exact candidate and the repository's merge
authority remain necessary; the manifest alone cannot authorize changing itself
or the code which checks it. Do not infer ratification from this document, its
candidate status field, a technical review, or a passing workflow.

## Acceptance and rollback

Require current-census and epoch adverse tests, all retained historical suites,
the full hosted matrix, exact-subject independent control review, and the actual
publication/merge route. Keep original first-red evidence in the project audit.
No continue-on-error, skipped-cell pass credit, or success from a draft PR.
Before activation, rollback is closing the unmerged candidate. After an authorized
merge, use a reviewed forward revert or successor amendment; never rewrite old
proof or claim local installation/adoption from CI.
