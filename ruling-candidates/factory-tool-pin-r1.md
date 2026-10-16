# RULING CANDIDATE — factory tools ship once, from the bus, and run only by reviewed pin (r1)

- **Proposed by:** `conjugal` (implementer session, Claude Code), 2026-10-16.
- **Status:** CANDIDATE for `RULINGS.md`. Not doctrine until appended. Zero runtime authority until
  a project pins (law 1).
- **Package:** `tools/factory/` (`pin-runner.py`, `check-doc-size.py`, fixtures, tests) and
  `hooks/` (`pre-push-ff-only.py`, `claude/exact-path-add.py`, `claude/git-optional-locks.py`, tests).

## Measured, not asserted (2026-10-16, Dell XPS 17)

- `check-doc-size.py` existed as **three divergent rewrites**: Conjugal `coordination/tools/` (373 lines,
  "ported from magic-lantern"), Cloudvore `tools/` (424), magic-lantern `tools/roadmap/` (282). Same
  purpose, three tier vocabularies, three scan domains (git-tracked, worktree walk, minus upstream),
  two size units (bytes on disk, CRLF-normalised KiB).
- `tools/tool-census.config.json` named none of those three projects, so on the box that holds them the
  census reported **0** duplicates. With the roots added it reports the real count (see the commit).
- Conjugal's `CLAUDE.md` states twelve non-negotiables; nothing mechanical refused a force/non-ff push or
  ref deletion, a sweeping `git add -A/./-u` or `commit -a`, or a read-only `git status/diff/log` without
  `--no-optional-locks`. Each was prose a session had to remember.

## Proposed rule

1. **A shared factory tool has one implementation, on the bus.** Projects supply data (a config) and a pin,
   never a copy. A project-local fork of a bus tool is a census excess to retire, not a variant.
2. **Bus bytes run only by pin.** A consumer vendors `tools/factory/pin-runner.py` once at
   `factory-pins/pin-runner.py` and records the blob it equals (`adopt-runner`). Every other tool runs as
   `pin-runner.py run <tool> -- args`, which reads the pinned blob by object id from a local clone,
   re-verifies blob id + bytes + sha256, and executes it from a private temp directory. A mismatch refuses
   (exit 2) before anything runs; a blob in neither the verified cache nor a clone is UNAVAILABLE
   (exit 3, loud, non-blocking).
3. **Staleness is reported, never acted on.** `status` prints `*** STALE ***` when the bus moved past a
   pin. Upgrading is a reviewed `pin` + commit in the consumer with reviewer and reason recorded.
4. **Tools are configured by data and name no project path.** A canonical tool must reproduce each
   adopting project's exit codes on its live tree given its config before that project deletes its copy.
   `check-doc-size.py` did, for all three trees (`fixtures/check-doc-size/`, parity recorded in the
   adopting commit).
5. **Guards ship as hooks that refuse.** `hooks/` holds the generic refusing hooks; a project installs them
   through its pins (PreToolUse entries and a pre-push layer that judges with the runner and pins as
   committed on the remote-tracking ref).

## Install contract

`tools/factory/README.md` § "Install contract" is the procedure; `hooks/README.md` § "Install" shows the
settings entries and the pre-push layer. Pins file schema: `factory-pins.v1`.

## What this does not cover

- The runner trusts the consumer's own checkout (its pins file and vendored runner) the way every project
  hook already does; a pre-push layer closes that gap only for pushes, by reading both from the remote ref.
- A bus clone is required on the box for pinned tools to run. The census root list is a union across boxes;
  a root absent on a box is skipped and named.
- Cloudvore and magic-lantern adoption is per project (law 2): the fixtures are their starting configs.

## Addendum A1 — pinned groups (proposed by Cloudvore K154, 2026-10-16; branch `kernel/package-2026-10-16`)

- **Gap.** `tools/factory/kernel-receipt.py` loads `kernel-subjects.py` and `codex-review.py` by file name beside
  itself. `run` materialises one blob (or none, in-process), so the receipt could not run by pin; and in-process its
  `__file__` is the bus path, so a sibling load would read the CALLER's tree, unverified.
- **Proposal.** A tool pin may carry `with: [<pinned tool>, ...]` (python only; `pin --with T`). `run` verifies every
  member's blob exactly as the tool's own (cache or clone; mismatch exit 2, absent exit 3), writes all of them into one
  private directory, checks the directory holds exactly those blobs, and runs the tool there with `python -I`; a group
  never runs in-process. One level: a member with its own `with` is refused, as are an unpinned member, a duplicate, a
  self-reference and two members with one file name. Pins without `with` behave exactly as before; a runner from before
  this key refuses a pins file that uses it (exit 2), so no group ever runs short of its members.
  `tools/factory/registry.json` entries may carry the same optional `with` (registered python members with no `with`
  of their own); `install <group>` refuses until every member is installed, then records the group. A registry is
  read only by the runner blob at the same commit, so an older runner never meets the key.
- **Evidence.** `tools/factory/pin-runner.tests.py` classes `PinnedGroup` and `InstallGroup` (decoy sibling in the caller's tree never
  loads; tampered or absent member refuses or is unavailable; malformed groups refuse) and
  `tools/factory/kernel-tools.tests.py` (a fresh `git init` project pins the kernel and runs `kernel-subjects check
  HEAD --json`, the `kernel-receipt` and `kernel-config` groups, through this runner).
- **Not decided here.** Whether rule 2 names groups explicitly is the ruling's call; nothing on bus master changes
  until it is merged.
- **reviewed:** independent adversarial review, Claude Opus 5.5 reviewer session dispatched from Conjugal, 2026-10-16,
  at `382276a3` merged with bus master `0f3f6d9c`. Holds: `with` names and member paths are validated before
  anything is read (`../` member name and `..` member path both refuse, exit 2); every member is verified by blob,
  size and sha256 like the tool itself; a group never runs in-process, runs `python -I` with `PYTHON*`/`NODE_*`
  stripped, so neither the script directory, the cwd nor `PYTHONPATH` can supply a module; Conjugal and
  magic-lantern pins files load unchanged. Two defects found and fixed on this branch, each with a test shown red
  first (`kernel-tools.tests.py`): (1) a group tool pinned WITHOUT `with` and run in-process (`python -I`) resolved
  its relative `__file__` against the caller's cwd and executed an unpinned `tools/factory/kernel-subjects.py` from
  the caller's tree (decoy exit 42) -- `kernel-receipt.py` and `kernel-config.py` now refuse (exit 2) unless their
  siblings sit beside an absolute `__file__`; (2) with `$FACTORY_KERNEL_CONFIG` unset, an in-process
  `kernel-subjects` silently read `<cwd>/tools/factory/factory-config.json` while the subprocess form refused -- it
  now refuses in both. Never the bundled fixture config. Residual, pre-existing class: the verify-to-exec window in
  the private temp directory (same-user only); the post-write blob re-check and directory-set check are
  defense-in-depth that no test kills (reviewer mutants: 4/7 killed, 1 equivalent, those 2 survived).
