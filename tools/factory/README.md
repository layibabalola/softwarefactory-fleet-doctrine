# tools/factory/ — canonical, pinned factory tools

Before this directory every member project hand-built its own factory: `check-doc-size.py`
existed as three divergent rewrites (Conjugal 373 lines, Cloudvore 424, magic-lantern 282),
each "ported" and then edited in place. `tools/tool-census.mjs` counts that drift; this directory
is how it falls. One implementation lives here; a project supplies only **data** (a config) and a
**pin** (which reviewed bus bytes it is willing to execute).

| file | what |
|---|---|
| [`pin-runner.py`](pin-runner.py) | the one generic runner: `init --profile`, `install`, `list`, `pin`, `adopt-runner`, `verify`, `status`, `run <tool> -- args`. `run` judges with the pins committed at HEAD (stderr `FALLBACK`) when the working copy is not JSON or carries merge-conflict markers, so a conflicted pins file cannot block the commands that resolve it; an unusable HEAD copy still refuses |
| [`bootstrap.sh`](bootstrap.sh), [`bootstrap.ps1`](bootstrap.ps1) | write the reviewed runner blob, prove `git hash-object` equals git's tree entry, only then run `install` (or `init` for `profile:NAME`) (refuse otherwise) |
| [`registry.json`](registry.json) | tool name to bus path, interpreter and purpose: what `install` and `list` resolve (add a tool here in the commit that adds it); `profiles`: the named bundles `init` installs |
| [`session-checkpoint.py`](session-checkpoint.py) | the fleet's one session checkpoint hook (SessionStart, Stop; with a `doctrine` block also the periodic PreToolUse doctrine tick that was `doctrine-periodic.py`); every project difference is `--config` data. No config = the ROTATION install prompt's v2; [`fixtures/session-checkpoint/dng.config.json`](fixtures/session-checkpoint/dng.config.json) = DNG's v3. Parity with both is tested event for event |
| [`fixtures/session-checkpoint/`](fixtures/session-checkpoint/) | `default.config.json` (what `init` seeds), `dng.config.json`, and the v2/v3 references the parity tests run (`*.py.txt`, so nothing counts them as copies) |
| [`check-doc-size.py`](check-doc-size.py) | markdown size budgets; every tier, glob, exemption, scan mode and unit from `--config` |
| [`session-start-auth.py`](session-start-auth.py) | SessionStart hook: runs the project's CLI auth/parity checker, surfaces the verdict, always exits 0, never re-auths, then self-tests every Bash/PowerShell PreToolUse guard in `.claude/settings.json` against a must-refuse fixture and reports any that fail open (`--checker`, `--repair-hint`, `--live`, `--config` for fixtures/green text/settings path, `--no-guard-self-test`) |
| [`fixtures/check-doc-size/`](fixtures/check-doc-size/) | the three projects' tier tables as configs (test fixtures and adoption starting points) |
| [`check-evidence-dumps.py`](check-evidence-dumps.py) | refuses committed raw evidence; an evidence dir is `SHA256SUMS` + `EVIDENCE-REF` naming the ref that holds the bytes (verified when local) |
| [`fixtures/check-evidence-dumps/`](fixtures/check-evidence-dumps/) | Cloudvore and Conjugal start configs |
| [`../../hooks/`](../../hooks/README.md) | generic refusing hooks: ff-only pre-push, no-unpinned-tool pre-push, exact-path add, optional-locks observers |
| [`kernel-subjects.py`](kernel-subjects.py) | factory kernel: is a packet a declared kernel subject, declared before its first byte (`check`, `advisory`, `block`) |
| [`kernel-receipt.py`](kernel-receipt.py) | factory kernel: write or dry-run a landing's kernel receipt; loads kernel-subjects.py and codex-review.py beside itself, so it is pinned as a **group** |
| [`codex-review.py`](codex-review.py) | dispatch one `codex exec` review with an explicit, recorded model/effort tier |
| [`kernel-config.py`](kernel-config.py), [`factory-config.schema.json`](factory-config.schema.json) | check a project's kernel config with the loader of record (kernel-subjects.py `load_config`); the schema describes the same keys for editors |
| [`fixtures/kernel/`](fixtures/kernel/) | `seed-repo/` (a minimal project: queue, a brief with a kernel block, a stub config, one product file) and Cloudvore's config (the suites' fixture) |

**Sharing is the default.** A tool here is never copied into a project: the project pins it.
`hooks/pre-push-no-unpinned-tool.py` refuses a consumer push that adds or edits a file named like any
tool here (or a new copy of a census-counted family), and `tools/tool-census.mjs` counts what is
left; its baseline only falls (rules 4, 7, 8 in its header; CI judges the `bus` view and the
ratchet history on every push).

Tests (stdlib only, Windows and POSIX):

```
python tools/factory/pin-runner.tests.py
python tools/factory/init.tests.py             # init --profile base end to end: hooks as written, a real git push
python tools/factory/session-checkpoint.tests.py  # parity with v2 and DNG's v3, event for event
python tools/factory/check-doc-size.tests.py
python tools/factory/check-evidence-dumps.tests.py
python tools/factory/session-start-auth.tests.py
python hooks/hooks.tests.py
node tools/tool-census.tests.mjs
python tools/factory/kernel-tools.tests.py      # config location, schema = loader, seed project through the runner
python tools/factory/kernel-suites.tests.py     # the kernel's own suites, staged as a project's tools/ directory
```

## A whole factory in one command: `init --profile`

```
sh tools/factory/bootstrap.sh <bus> <bus-sha> profile:base <reviewer> <reason> [project-root]
pwsh tools/factory/bootstrap.ps1 -Bus <bus> -Sha <bus-sha> -Tool profile:base -Reviewer <who> -Reason <why> [-Project <dir>]
python factory-pins/pin-runner.py init --profile base --commit <bus-sha> --reviewer <who> --reason <why> --bus <bus>   # runner already vendored
```

A **profile** is registry data (`profiles` in `registry.json`, checked by `validate_profile`). `base` installs:

| piece | where it lands |
|---|---|
| the runner (vendored, adopted) and a pin per tool: `session-checkpoint`, `exact-path-add`, `git-optional-locks`, `pre-push-ff-only`, `no-unpinned-tool`, `check-rule-tags` | `factory-pins/pin-runner.py`, `factory-pins/factory-pins.json` |
| seeds, copied from verified bus blobs | `factory-pins/session-checkpoint.config.json` |
| Claude hooks, each `python -I "$CLAUDE_PROJECT_DIR/factory-pins/pin-runner.py" run <tool>`: session-checkpoint on SessionStart and Stop, the two guards on PreToolUse `Bash\|PowerShell` | merged into `.claude/settings.json` |
| the git pre-push layers (ff-only, then no-unpinned-tool), [`hooks/pre-push.factory.sh`](../../hooks/pre-push.factory.sh) | the effective hooks dir (`core.hooksPath` honoured) |
| a rule-map skeleton: the pinned `check-rule-tags --emit-map` over `CLAUDE.md`/`AGENTS.md`, every rule `prose` | `factory-pins/rule-tags.config.json`, `factory-pins/rule-map.json` |
| a product-throughput class stub for `tools/Get-ProductThroughput.ps1 -ClassConfig` | `factory-pins/product-throughput-classes.json` |

Law 1 holds exactly as for `install`: the running runner must be git's object at `<bus-sha>`, and every blob init pins,
seeds, writes as a hook or executes is hashed in-process and must equal the commit's tree entry. The one tool it
executes is the profile's pinned `check-rule-tags`, from those verified bytes, in a private directory. Everything is
planned before the first write, so a refusal (exit 2) writes nothing. A file the project already has is **never
overwritten**: a different settings entry already running a profile tool (or the user settings running it, which would
double-register it), or a pre-push hook with other layers, is printed as a `HAND:` step and init exits **4
INCOMPLETE**; re-run it after the step and it exits 0. A second run with the same commit is a `NO-OP`. init never
commits: it prints the exact `git add --` line (a review decision).

## Install contract (consumer project)

**One command**, bootstrapped so that NOTHING runs before its identity is proven (a runner started from unverified
bytes could do anything before it checks itself). Use the script for your shell; each does (a) write the reviewed
blob, (b) require `git hash-object --no-filters` to equal git's tree entry, (c) only then run `install`, and refuses
(exit 2, runner never started) on a mismatch:

```
sh tools/factory/bootstrap.sh <bus> <bus-sha> check-doc-size <reviewer> <reason> [project-root]
pwsh tools/factory/bootstrap.ps1 -Bus <bus> -Sha <bus-sha> -Tool check-doc-size -Reviewer <who> -Reason <why> [-Project <dir>]
```

The bootstrap script is itself bus bytes: run it from a clone at `<bus-sha>`, or first confirm
`git -C <bus> diff --quiet <bus-sha> -- tools/factory/bootstrap.sh tools/factory/bootstrap.ps1` exits 0.

By hand, never skip (b) (PowerShell's `>` re-encodes; use `cmd /c "git -C <bus> show <sha>:tools/factory/pin-runner.py > factory-pins/pin-runner.py"`):

```
git -C <bus> show <sha>:tools/factory/pin-runner.py > factory-pins/pin-runner.py                              # (a)
[ "$(git hash-object --no-filters factory-pins/pin-runner.py)" = "$(git -C <bus> rev-parse <sha>:tools/factory/pin-runner.py)" ] || exit 2   # (b) POSIX
if ((git hash-object --no-filters factory-pins/pin-runner.py) -ne (git -C <bus> rev-parse <sha>:tools/factory/pin-runner.py)) { exit 2 }     # (b) PowerShell
python factory-pins/pin-runner.py install check-doc-size --commit <sha> --reviewer <who> --reason <why> --bus <bus>   # (c)
python factory-pins/pin-runner.py list      # the registry: what can be installed
```

`install` refuses (exit 2, nothing written) unless the bytes RUNNING it and the bytes it vendors are
byte-identical to git's object `<bus-sha>:tools/factory/pin-runner.py`; it re-checks the vendored file after
writing. Every blob it (and `pin`, `adopt-runner`, the registry read) takes from the bus is hashed in-process
(`sha1("blob N<NUL>" + bytes)`) and must equal `git rev-parse <sha>:<path>` before it is recorded, vendored or run. It adopts the runner, pins the tool from the registry (`tools/factory/registry.json` at that commit),
records `bus_clone`, and prints the `python factory-pins/pin-runner.py run <tool> -- ...` line to wire into your
hook or CI. It writes data only and never executes the tool; `run` is the only executor. Re-running with the same
commit is a no-op; a newer commit re-pins and prints the diff (run it from that commit's runner blob, the same
`git show`). An unknown tool or an edited vendored runner is refused. Steps 1-3 below are what it does; 4-6 stay yours.

Census notes: a vendored `factory-pins/pin-runner.py` whose blob equals any past release on the bus's `origin/master`
(else `master`) counts as the canonical runner, and identical bytes are one version wherever they sit, for DUPLICATE
COUNTING only (`verify`/`status` still flag a stale pin; it is not an approval).

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
# install from the registry (members first; the registry's `with` makes kernel-receipt and kernel-config groups)
python factory-pins/pin-runner.py install kernel-subjects --commit <bus-sha> --reviewer R --reason W
python factory-pins/pin-runner.py install codex-review    --commit <bus-sha> --reviewer R --reason W
python factory-pins/pin-runner.py install kernel-receipt  --commit <bus-sha> --reviewer R --reason W
python factory-pins/pin-runner.py install kernel-config   --commit <bus-sha> --reviewer R --reason W
# or pin by hand (the same records)
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
