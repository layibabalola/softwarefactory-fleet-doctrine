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
   (exit 2) before anything runs; a missing clone or blob is UNAVAILABLE (exit 3, loud, non-blocking).
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
