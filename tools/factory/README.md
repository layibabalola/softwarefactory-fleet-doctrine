# tools/factory/ — canonical, pinned factory tools

Before this directory every member project hand-built its own factory: `check-doc-size.py`
existed as three divergent rewrites (Conjugal 373 lines, Cloudvore 424, magic-lantern 282),
each "ported" and then edited in place. `tools/tool-census.mjs` counts that drift; this directory
is how it falls. One implementation lives here; a project supplies only **data** (a config) and a
**pin** (which reviewed bus bytes it is willing to execute).

| file | what |
|---|---|
| [`pin-runner.py`](pin-runner.py) | the one generic runner: `pin`, `adopt-runner`, `verify`, `status`, `run <tool> -- args` |
| [`check-doc-size.py`](check-doc-size.py) | markdown size budgets; every tier, glob, exemption, scan mode and unit from `--config` |
| [`fixtures/check-doc-size/`](fixtures/check-doc-size/) | the three projects' tier tables as configs (test fixtures and adoption starting points) |
| [`../../hooks/`](../../hooks/README.md) | generic refusing hooks: ff-only pre-push, exact-path add, optional-locks observers |
| [`kernel-subjects.py`](kernel-subjects.py) | factory kernel: is a packet a declared kernel subject, declared before its first byte (`check`, `advisory`, `block`) |
| [`kernel-receipt.py`](kernel-receipt.py) | factory kernel: write or dry-run a landing's kernel receipt; loads kernel-subjects.py and codex-review.py beside itself, so it is pinned as a **group** |
| [`codex-review.py`](codex-review.py) | dispatch one `codex exec` review with an explicit, recorded model/effort tier |
| [`kernel-config.py`](kernel-config.py), [`factory-config.schema.json`](factory-config.schema.json) | check a project's kernel config with the loader of record (kernel-subjects.py `load_config`); the schema describes the same keys for editors |
| [`fixtures/kernel/`](fixtures/kernel/) | `seed-repo/` (a minimal project: queue, a brief with a kernel block, a stub config, one product file) and Cloudvore's config (the suites' fixture) |

Tests (stdlib only, Windows and POSIX):

```
python tools/factory/pin-runner.tests.py
python tools/factory/check-doc-size.tests.py
python hooks/hooks.tests.py
python tools/factory/kernel-tools.tests.py      # config location, schema = loader, seed project through the runner
python tools/factory/kernel-suites.tests.py     # the kernel's own suites, staged as a project's tools/ directory
```

## Install contract (consumer project)

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

## The factory kernel (bus K154)

The kernel tools came from Cloudvore (origin/master `31315b2`) with one change: kernel-subjects.py reads its
config from the file `$FACTORY_KERNEL_CONFIG` names (relative to the caller's cwd), else `factory-config.json`
beside itself as before. A pinned tool runs from a private directory, so a consumer always sets the variable.

```
# pin (review decisions; members first, then the groups that load them)
python factory-pins/pin-runner.py pin kernel-subjects --commit <bus-sha> --path tools/factory/kernel-subjects.py --reviewer R --reason W
python factory-pins/pin-runner.py pin codex-review    --commit <bus-sha> --path tools/factory/codex-review.py    --reviewer R --reason W
python factory-pins/pin-runner.py pin kernel-receipt  --commit <bus-sha> --path tools/factory/kernel-receipt.py  --reviewer R --reason W --with kernel-subjects --with codex-review
python factory-pins/pin-runner.py pin kernel-config   --commit <bus-sha> --path tools/factory/kernel-config.py   --reviewer R --reason W --with kernel-subjects
# run (PowerShell: $env:FACTORY_KERNEL_CONFIG = "factory-pins/factory-config.json")
FACTORY_KERNEL_CONFIG=factory-pins/factory-config.json python factory-pins/pin-runner.py run kernel-config -- check factory-pins/factory-config.json
FACTORY_KERNEL_CONFIG=factory-pins/factory-config.json python factory-pins/pin-runner.py run kernel-subjects -- check HEAD --json
```

**Config contract.** One JSON file, `schema: 1`; every key in `factory-config.schema.json` is required and no
other key is allowed; contradicting keys are refused (the schema's description lists them). The config NAMES
project things (subject prefix, row pattern, paths, runner and workflow names, default contract text); what
decides credit stays in code, the bar runner and the workflows (K137). Start from
`fixtures/kernel/seed-repo/factory-config.json`.

**Pinned group.** `pin --with T` records `with: [T, ...]` on a python tool: `run` verifies every member's pinned
blob as it verifies the tool's own, writes them all into one private directory, checks that directory holds
exactly those blobs, and runs the tool there with `python -I`, never in-process. One level only. A runner from
before this key refuses a pins file that uses it (exit 2). Proposed in `ruling-candidates/factory-tool-pin-r1.md`
(addendum A1).

**Known limits.** kernel-receipt.py still carries Cloudvore's .NET product-bar vocabulary (the excluded-count
log line names the `DropboxVault.App.Tests` and `DropboxVault.Core.Tests` assemblies; the product-bar filter
grammar is `dotnet test`'s). kernel-subjects.py (`check`, `advisory`, `block`) names no such thing; moving the
receipt's names into the config is the next kernel change. The kernel-suites harness excludes,
by name, the tests that read a project tree around `tools/`; they remain pins in the adopting project's run.
