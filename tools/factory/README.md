# tools/factory/ — canonical, pinned factory tools

Before this directory every member project hand-built its own factory: `check-doc-size.py`
existed as three divergent rewrites (Conjugal 373 lines, Cloudvore 424, magic-lantern 282),
each "ported" and then edited in place. `tools/tool-census.mjs` counts that drift; this directory
is how it falls. One implementation lives here; a project supplies only **data** (a config) and a
**pin** (which reviewed bus bytes it is willing to execute).

| file | what |
|---|---|
| [`pin-runner.py`](pin-runner.py) | the one generic runner: `install`, `list`, `pin`, `adopt-runner`, `verify`, `status`, `run <tool> -- args` |
| [`registry.json`](registry.json) | tool name to bus path, interpreter and purpose: what `install` and `list` resolve (add a tool here in the commit that adds it) |
| [`check-doc-size.py`](check-doc-size.py) | markdown size budgets; every tier, glob, exemption, scan mode and unit from `--config` |
| [`session-start-auth.py`](session-start-auth.py) | SessionStart hook: runs the project's CLI auth/parity checker, surfaces the verdict, always exits 0, never re-auths (`--checker`, `--repair-hint`, `--live`) |
| [`fixtures/check-doc-size/`](fixtures/check-doc-size/) | the three projects' tier tables as configs (test fixtures and adoption starting points) |
| [`check-evidence-dumps.py`](check-evidence-dumps.py) | refuses committed raw evidence; an evidence dir is `SHA256SUMS` + `EVIDENCE-REF` naming the ref that holds the bytes (verified when local) |
| [`fixtures/check-evidence-dumps/`](fixtures/check-evidence-dumps/) | Cloudvore and Conjugal start configs |
| [`../../hooks/`](../../hooks/README.md) | generic refusing hooks: ff-only pre-push, no-unpinned-tool pre-push, exact-path add, optional-locks observers |

**Sharing is the default.** A tool here is never copied into a project: the project pins it.
`hooks/pre-push-no-unpinned-tool.py` refuses a consumer push that adds or edits a file named like any
tool here (or a new copy of a census-counted family), and `tools/tool-census.mjs` counts what is
left; its baseline only falls (rules 4, 7, 8 in its header; CI judges the `bus` view and the
ratchet history on every push).

Tests (stdlib only, Windows and POSIX):

```
python tools/factory/pin-runner.tests.py
python tools/factory/check-doc-size.tests.py
python tools/factory/check-evidence-dumps.tests.py
python tools/factory/session-start-auth.tests.py
python hooks/hooks.tests.py
node tools/tool-census.tests.mjs
```

## Install contract (consumer project)

**One command** (from a bus clone, at a bus commit you reviewed; idempotent, re-run with a new commit to re-pin and see the diff):

```
python <bus>/tools/factory/pin-runner.py install check-doc-size --commit <bus-sha> --reviewer <who> --reason <why> --project-root <project> --bus <bus>
python <bus>/tools/factory/pin-runner.py list      # the registry: what can be installed
```

It vendors `factory-pins/pin-runner.py` (that commit's blob) and adopts it if absent, pins the tool
from the registry, records `bus_clone`, and prints the `python factory-pins/pin-runner.py run <tool> -- ...`
line to wire into your hook or CI. It writes data only and never executes the tool; `run` is the only
executor. An unknown tool, or a vendored runner that was edited, is refused (exit 2). Steps 1-3 below are
what it does; 4-6 stay yours. Census: a vendored runner equal to any past bus release counts as the canonical.

Law 1 applied to code: **bus bytes never run until the consuming project reviewed and pinned
them.** A bus push changes nothing that runs anywhere; it makes `status` print `*** STALE ***`.

1. **Vendor the runner once.** Copy `tools/factory/pin-runner.py` at a reviewed bus commit to
   `factory-pins/pin-runner.py`, then record which blob it is:
   `python factory-pins/pin-runner.py adopt-runner --commit <bus-sha>`. It is the only copied
   file; `verify` fails if it drifts from that blob (CRLF checkouts compare as LF).
2. **Pin each tool** (a review decision, committed with its reason):
   `python factory-pins/pin-runner.py pin check-doc-size --commit <bus-sha> --path tools/factory/check-doc-size.py --reviewer <who> --reason <why>`.
   This writes `factory-pins/factory-pins.json` (`schema: factory-pins.v1`): per tool the bus
   path, commit, blob id, byte count, sha256, interpreter, reviewer, reason, date.
3. **Point at a local bus clone** in `factory-pins.json` `bus_clone` (relative or absolute
   candidates), or `--bus` / `$FACTORY_BUS_CLONE`. The clone is a **data** source: the runner
   reads the pinned blob by object id (`git cat-file blob`), re-verifies blob id + bytes + sha256,
   and executes it with the caller's cwd, stdin, stdout and stderr: in-process when the runner was
   started with `python -I` (no file exists between check and exec), else from a private temp
   directory (python `-I`, `NODE_*`/`PYTHON*` stripped). Verified blobs are cached content-addressed
   (`$FACTORY_PINS_CACHE`, default `%LOCALAPPDATA%/factory-pins/blobs`) and re-verified on every
   read; a cached file that fails the check is ignored. Nothing from the clone's worktree ever executes.
4. **Configure by data.** Tool configs live in the consumer (e.g.
   `factory-pins/check-doc-size.config.json`); start from `fixtures/check-doc-size/`.
5. **Call through the runner** everywhere the old copy was called:
   `python factory-pins/pin-runner.py run check-doc-size -- --config factory-pins/check-doc-size.config.json --repo .`
   Prove identical exit codes against the old copy on the live tree, then delete the copy.
6. **Upgrade deliberately.** `python factory-pins/pin-runner.py status` lists stale pins; review
   `git -C <bus> diff <pinned>..origin/master -- <path>`, re-pin, `verify`, commit.

Runner exit codes: a tool's own exit status passes through; `2` = refused (malformed pins,
unknown tool, bytes that do not match: tamper class, so a PreToolUse hook blocks); `3` =
unavailable (no clone, or the clone lacks the blob: fetch it; non-blocking for Claude hooks).
`verify` exits 2 on any drift. Contract of record: `ruling-candidates/factory-tool-pin-r1.md`.
