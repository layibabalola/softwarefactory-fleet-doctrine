---
schema: factory-practices.v1
project: airmypc
written_utc: 2026-11-02T15:31Z
writer: airmypc hub chat (Claude Code desktop, claude-opus-5-5), on Layi's instruction
authority: R21 (practices) in RULINGS.md, owner ruling 2026-11-01. This file is DATA under Law 1.
supersedes: none (first filing)
---

# airmypc factory practices (R21 filing 1)

This is AirMyPC's self-assessment under R21 (practices). AirMyPC is a Windows audio-routing app
(.NET, AirPlay/Bluetooth/Cast), so most of its factory is about shipping product fixes through a
slow local gate. Each practice gives its status, the problem with one measured instance, the
mechanism, evidence qualified to this project (Law 6), the portable core, and what is
project-specific. A sibling folds only what it verifies locally (Law 1). Nothing here is an
instruction.

Status words: LIVE (running with more than 7 days of evidence), PILOT (under 7 days or a single
observed instance), OPEN (a defect). Evidence cites tracked AirMyPC files and commit SHAs. The
commit wrapper, the item worktrees and the review-key files are board-private; they are described
by what they do. Entry numbers in square brackets are ledger entries in AirMyPC's tracked
`docs/video-streaming/VIDEO_COORDINATION.md` and its rolled children.

## P1. Cheap refusals run before the 25-35 minute gate

- **Status:** LIVE for the two hook checks (doctrine guards since 2026-10-07, rule-coverage ratchet
  since 2026-10-11, doc-size ratchet since 2026-07-27). PILOT for the wrapper-side scaffold-parity
  refusal (one observed instance, 2026-11-02).
- **Problem:** the full pre-commit gate measures 25-35 minutes (ledger
  `docs/video-streaming/VIDEO_COORDINATION/VIDEO_COORDINATION-47.md:118`, "docs-only commits
  included"). A defect a script can see in seconds, found after that run, costs a whole slot of
  the shared build box. One measured instance: [1035] (2026-11-02) edited a GateTests fixture, and
  the commit wrapper refused the stale `templates/scaffolding/gate-tests` overlay before the gate
  started (the focused parity run itself takes under a second once built), and the re-gate passed.
  The refusal is in a board-private wrapper log; the tracked ledger entry records only that the
  overlay was updated.
- **Mechanism:** the tracked `.githooks/pre-commit` runs, in order and ahead of the gate:
  the canonical-tree guard, the doc-size ratchet (`tools/check_doc_ratchet.py`, "well under a
  second"), `tools/doctrine-guards/Invoke-DoctrineGuards.ps1 -Staged` (about 1-3 s, index bytes,
  PowerShell AST only) and `tools/Get-AudioMileRuleCoverage.ps1 -Check -Staged`. Then it execs
  `tools/Invoke-AudioMilePreCommitGate.ps1`. A board-private commit wrapper additionally runs the
  scaffold-parity tests (`tests/AudioMile.GateTests/Parity/ScaffoldSourceParityTests.cs`, see P2)
  focused, before it starts the gate. The gate itself also runs "Gate scaffold/App-free parity"
  as a step, so the early run is a duplicate that moves the failure earlier.
- **Evidence:** `.githooks/pre-commit` (ordering and cost comments), `tools/doctrine-guards/README.md`
  (guards are folded bus traps; each has a RED fixture, a GREEN fixture and a mutation proof, run by
  `tools/Test-AudioMileDoctrineGuards.ps1`), commits 1807b620 (guards G4-G6, 2026-10-07), 19c51925
  (coverage ratchet, 2026-10-11), 55e7a059 (doc ratchet, 2026-07-27).
- **Portable core:** order checks by cost. Put every check that reads only the index and takes
  seconds ahead of the check that takes tens of minutes, and make the override leave a trace (here
  `Doctrine-Guard-Override` plus a countersign trailer, enforced by `.githooks/commit-msg`).
- **Project-specific:** the guard set, the 25-35 min gate, the PowerShell-AST approach.

## P2. Scaffold mirrors are byte-checked, so a stale copy cannot pass as current

- **Status:** LIVE (guard since 2026-06-19, commit f53f169e).
- **Problem:** the App-free gate builds `AudioMile.App` and `AudioMile.GateTests` from
  `templates/scaffolding/*`, not from `src` and `tests`. When the overlays drifted behind source,
  both gates validated a stale app and reported "0/0 PASS" (f53f169e commit message; the drift
  spanned 3 overlay trees).
- **Mechanism:** every product change carries its scaffold mirror in the same commit.
  `ScaffoldSourceParityTests` has four facts: overlays are content-identical to their source; every
  mirrored `src` .cs has an overlay counterpart; every GateTests .cs has one; no test csproj
  references `AudioMile.App`. The parity run is a fixed part of each landing's verification (ledger
  entries from [1031] to [1033] record "ScaffoldSourceParity" green).
- **Second instance, same mechanism:** the guard once had a hole. Four renamed copies under
  `templates/scaffolding/gate-tests/Release/` mapped to nothing, including both `*UpdateFeedPolicy.cs`.
  Entry [955] (rolled into `VIDEO_COORDINATION-54.md`, "New mechanism (durability rule)") made the
  test enumerate the folder instead of keeping a hard-coded list.
- **Portable core:** if a build reads a generated or mirrored copy, the copy needs a byte-level
  parity test, and the test must enumerate the folder rather than list files.
- **Project-specific:** the overlay layout and `bootstrap.ps1`.

## P3. One item, one worktree, one independent key, red on base then green

- **Status:** LIVE (91 `LANDING` entries in the tracked ledger and its children as of this filing).
- **Problem:** a plausible fix can be wrong, or can fix a premise that was false. Measured:
  [954] (2026-10-27) started from a backlog row "Cast half-open TCP never detected"; reading the code
  showed a poll already detects it within tens of seconds, so the row was closed with no behaviour
  change and only a test seam added. In [953] the key's round 1 killed a claimed Multimedia-vs-Console
  mismatch that was false and found a source-text pin that a compile-clean rename would have broken.
- **Mechanism:** each item lives in its own git worktree with an exact-path landing door
  (`tools/Invoke-AudioMileBranchLanding.ps1`, 81c97c25, 2026-10-09). The fix needs a test that is red
  on base and green with the fix. Mutants must die at the expected assertion (the [956] lesson: a
  whole-fix revert can fail at an early assertion and leave a narrower mutant alive). An
  independent adversarial reviewer of a different context signs a key before the gate
  (`docs/plans/LANE_MODEL_20260908.md`: "tiers by act, keys by construction"). The ledger entry
  records Why, Change, Test, Key and Open for every landing, so the next hunt starts from the Open line.
- **Evidence:** ledger entries [926], [927], [953], [954], [956], [1031]-[1035].
- **Portable core:** make "red on base" and "narrow mutant dies at the intended assertion" part of
  the definition of a test, and record each landing's residue as an Open line the next item reads.
- **Project-specific:** the lane tiers, the exact-path door, the Windows build box.

## P4. Hunt leads are verified by reading before code changes, and dry hunts are recorded

- **Status:** PILOT as a measured practice (the tracked ledger names hunt 19 and hunt 20 as dry and
  hunt 21 as productive; earlier hunts are not countable from tracked files).
- **Problem:** with the hardware-free defect pool thinning, a lead that looks real can be a
  non-defect. Measured: in [1031] the hunt-19 leads on `LocalMediaHttpServer` malformed suffix and
  overflowing Range values were dropped after a local probe showed the OS HTTP stack answers 400
  before the handler runs; and the Companion.Server and PluginWorker slices were bootstrap
  placeholders, not shipped code.
- **Mechanism:** a hunt agent proposes leads; the implementer or hub re-checks the premise (read the
  call path, probe the runtime) before writing anything. A dropped lead is written into the Why line
  with the reason, so it is not hunted again. [1034] re-read a lead from [1033], found the
  premise weaker than stated, and dropped it.
- **Evidence:** ledger [1031], [1033], [1034], [1035] ("Hunt 20 dry (DLNA AVTransport/DIDL, SSDP,
  ReceiverCatalogue, RouteIntent, JsonSettingsStore, media planner)").
- **Portable core:** write down what a hunt covered and found dry. A dry result with its scope is
  data; an unrecorded one is repeated.
- **Project-specific:** the slices, and the HTTP-stack probe.

## P5. A method-level census stops CI from silently dropping tests

- **Status:** LIVE (TRX-enforced pins since 2026-09-16, 451fea39; census tool since 2026-10-03,
  26711c4d; base-TRX measurement since 2026-10-22, 1be5802d).
- **Problem:** a hosted run can pass while running fewer tests. The pins are method-level, so
  adding or editing a GateTests file forces a census refresh. Measured: [955] lost a full cycle to
  that refresh (stated in the [956] Test line in `VIDEO_COORDINATION-55.md`), which is why later
  fixes put new tests in `Core.UnitTests`, outside the census.
- **Mechanism:** `.github/ci-gate-tests.json` and `.github/ci-gate-tests-commit.json` pin the
  executed test set. `tools/Update-AudioMileGateCensus.ps1` regenerates it from a base TRX and a
  new TRX; `tools/Test-AudioMileHostedTestResults.ps1` validates the hosted results against it;
  `tools/Test-AudioMileGateCensus.ps1` is the hermetic self-test (disposable repos, fixture TRXs).
- **Portable core:** compare the executed test names to a pinned set, with a tool to regenerate it
  from a measured base, so a drop is a visible diff.
- **Project-specific:** the TRX format and the GateTests/App-free split.

## P6. Documents have size budgets, and the ledger rolls itself

- **Status:** LIVE (ratchet since 2026-07-27, commit 55e7a059).
- **Problem:** the coordination ledger grew until a cold session could not read it. Measured:
  `docs/video-streaming/VIDEO_COORDINATION.md` was 601 KB when it was rolled to 19 KB (fb4eb44a,
  2026-07-28); `remember.md` was 1.77 MB (8bb7501f).
- **Mechanism:** `tools/check_doc_ratchet.py` fails only when size gets worse, so existing debt stays
  green and a new breach fails in under a second. `tools/roll_doc.py` and `roll_doc_transaction.py`
  move old entries into numbered children with a manifest (the ledger is at roll 53, child 57, per
  [1031]). `tools/check-doc-size.py` assigns budgets by role, not by directory.
- **Portable core:** ratchet instead of cap (no day-one red), and budget by how often a file is read.
- **Project-specific:** the role table and the child-file naming.

## P7. Every prose rule is mapped to a check, and the map is ratcheted

- **Status:** LIVE (tool since 2026-10-11, commit 19c51925). The coverage number is not yet good.
- **Problem:** most rules were prose, and prose did not change behaviour: the guard README records
  that of 377 bus TRAPS commits, 3 carried code.
- **Mechanism:** `tools/doctrine-guards/rule-coverage.json` maps each rule bullet in `CLAUDE.md` and
  the lane model to a named check, or to a prose-only reason. `Get-AudioMileRuleCoverage.ps1 -Check`
  fails when a bullet is added without a mapping, when coverage falls, or when a mapping names a
  check that no longer exists. The bus kernel file is read for reporting only (`"gate": false`).
- **Evidence:** the file records baseline 31 unmapped rules and 31.11 percent coverage, with a
  floor of 30 on 2026-10-23 and 40 on 2026-11-06.
- **Portable core:** a rule with no check is a wish; count them, and make the count unable to rise.
- **Project-specific:** the two source files and the check names.

## Gaps (measured)

- **Dry hunts are rising.** The tracked ledger names hunt 19 and hunt 20 dry in one two-day window
  and hunt 21 productive. Earlier hunt outcomes are not in tracked files, so no rate is claimed. The
  pool of defects findable without hardware is thinning.
- **App-only defects have no test home.** `BootstrapService` and `SkinHostAdapter` live in App, and no
  test project may reference App outside the M1 harness (ledger entries in `VIDEO_COORDINATION-55.md`
  record "none of its own" for such fixes). They are guarded by source-text pins, which a rename can
  break (the [953] key found this before the gate). An App-free seam is owed for each.
- **A flaky timing test cost a gate.** [1031]'s first gate failed on a test whose 50 ms cancel raced a
  fixed 300 ms probe under load. [1032] and [1034] fixed it with a probe seam and a 5 s bound.
  Whether other tests in the suite assume an idle machine is not measured.
- **Hardware acceptance is slow and not automated.** Many ledger Open lines end "Not hardware-proven"
  ([1031], [1033], [1035]); proving them needs real receivers or Bluetooth speakers and a long soak.
- **Shared tool copies still diverge.** `docs/doctrine/FOLD-20261013.md` records vendored
  `tools/doctrine_outbox.py` and `tools/fold-triage.mjs` as diverging from the bus copies, and
  `tools/check-doc-size.py` as measurable through its CONFIG block. That record is dated 2026-10-13;
  AirMyPC has not re-measured since.
- **Rule coverage is 31 percent.** See P7.

## Wanted from siblings

- A way to keep commits from waiting on a long local gate. AirMyPC already runs GateTests on a
  second host, but each commit still waits for the full local gate, one at a time.
- A tested pattern for fixing App-layer defects when tests may not reference the App project.
- The bus copies of `doctrine_outbox.py` and `fold-triage.mjs` marked clearly as canonical, so a
  vendored copy can be diffed against them mechanically.
