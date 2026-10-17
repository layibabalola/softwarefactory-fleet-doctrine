# hooks/ — generic refusing hooks for member projects

Four guards that every member project had as prose ("never grow your own copy of a shared tool" is the fourth) ("never force-push", "add exact paths",
"observers use `--no-optional-locks`") and almost none enforced. Each is one stdlib-only Python
file, exits non-zero to refuse, and names no project path. Like every factory tool they run from
**pinned** bus bytes through the consumer's vendored `factory-pins/pin-runner.py`
(see [`tools/factory/README.md`](../tools/factory/README.md)) — never from this clone directly
(law 1).

| hook | event | refuses |
|---|---|---|
| [`pre-push-ff-only.py`](pre-push-ff-only.py) | git `pre-push` (ref lines on stdin) | exit 1 when a protected ref is deleted, or its remote tip is not an ancestor of the pushed tip, or ancestry cannot be proven. Protected: `--protect <name>` / `--config <json>` `{"protected": [...]}`; default `master`, `main` |
| [`pre-push-no-unpinned-tool.py`](pre-push-no-unpinned-tool.py) | git `pre-push` (ref lines on stdin) | exit 1 when the pushed commits add or modify a file named like a bus factory tool (tools/factory/*, hooks/*: any add or edit) (session-checkpoint is one since `tools/factory/session-checkpoint.py` landed) or add a NEW copy of a census family (doctrine-outbox, doctrine-triage, resumability-check, doctrine-periodic, account-parity, realign-cli). Exempt: the vendored runner when it equals its pinned blob, and paths in `factory-pins/no-unpinned-tool.json` (read from the pushed tip) with a reason and an expiry at most 120 days out; an expired entry refuses. Families are kept equal to `tools/tool-census.config.json` by the tests |
| [`pre-push-bus-tests.py`](pre-push-bus-tests.py) | git `pre-push` in a **bus clone** (ref lines on stdin) | exit 1 when a push to a protected ref (default `master`, `main`) changes `hooks/`, `tools/factory/`, `tools/tool-census*`, `metrics/tool-census*`, `factory-pins/` or the doctrine-sync workflow and the fast bus suites (`hooks/hooks.tests.py`, `tools/factory/pin-runner.tests.py`, `tools/tool-census.tests.mjs`) fail on the PUSHED tip, checked out into a temporary worktree; a missing interpreter or a timeout also refuses. Also exit 1, with the approved refresh command, when the push touches a file a sealed pin covers (the r45 manifest's subjects such as `README.md`; the R26 census's project specs, a new top-level `specs/*.md`) and that pin's CI checker fails on the tip. Any other push runs nothing |
| [`pre-push.factory.sh`](pre-push.factory.sh) | git `pre-push` (the whole file) | the ff-only layer below (verbatim; a test holds them equal) chained with the same-shaped no-unpinned-tool layer. `pin-runner.py init --profile base` writes it into a consumer's hooks dir when none exists; a hook that has other layers is left alone and the layers are chained by hand |
| [`claude/exact-path-add.py`](claude/exact-path-add.py) | Claude Code `PreToolUse` on `Bash\|PowerShell` | exit 2 on `git add -A/--all/-u/--update/.`/`:/`, `git commit -a/--all` (clusters such as `-am` included), `git commit .` |
| [`claude/git-optional-locks.py`](claude/git-optional-locks.py) | Claude Code `PreToolUse` on `Bash\|PowerShell` | exit 2 on `git status/diff/log/show/rev-list` without the global `--no-optional-locks` or `GIT_OPTIONAL_LOCKS=0`. Mutation commands are never judged -- `run git-optional-locks -- --observe-only` (opt-in per project, for runbooks that still say plain `git status`) prints the finding as OBSERVED and exits 0 |

The Claude hooks tokenise the command like a shell (quotes, operators, `$( )`, comments, heredoc
bodies), so a commit message or `echo` that *mentions* `git add -A` is not refused.

Tests: `python hooks/hooks.tests.py`.

## Install (consumer project)

1. Pin each hook (a review decision, committed in the consumer):

   ```
   python factory-pins/pin-runner.py pin exact-path-add     --commit <bus-sha> --path hooks/claude/exact-path-add.py     --reviewer <who> --reason <why>
   python factory-pins/pin-runner.py pin git-optional-locks --commit <bus-sha> --path hooks/claude/git-optional-locks.py --reviewer <who> --reason <why>
   python factory-pins/pin-runner.py pin pre-push-ff-only   --commit <bus-sha> --path hooks/pre-push-ff-only.py          --reviewer <who> --reason <why>
   ```

2. `.claude/settings.json` (project):

   ```json
   "PreToolUse": [{ "matcher": "Bash|PowerShell", "hooks": [
     { "type": "command", "command": "python -I \"$CLAUDE_PROJECT_DIR/factory-pins/pin-runner.py\" run exact-path-add", "timeout": 30 },
     { "type": "command", "command": "python -I \"$CLAUDE_PROJECT_DIR/factory-pins/pin-runner.py\" run git-optional-locks", "timeout": 30 } ] }]
   ```

   `-I` matters: an isolated runner executes the verified bytes in its own process (no second
   interpreter, no temp file), which is what keeps a hook on every Bash call cheap. The runner exits
   2 (blocks) when the pinned bytes do not match. It exits 3 (non-blocking, loud) only when the
   pinned blob is in neither the runner's verified blob cache nor a bus clone -- a pin never seen on
   this machine -- so a never-provisioned box is warned, not bricked; once a pin has run, a missing
   or moved clone no longer switches the guard off.

3. `.git/hooks/pre-push`: a layer that reads the ref lines once, judges them with the runner AND
   the pins read from a **judge ref**, and hands the same lines to every later layer (git-lfs needs
   them). The judge ref is the first protected remote-tracking ref (`FF_PROTECTED`, edit it per
   project) that already holds `factory-pins/pin-runner.py` AND pins this layer's tool -- there a
   pushed branch cannot weaken or re-pin its own judge -- else the commit being pushed (a project whose
   work never reaches a remote master, e.g. a local-only branch, and the adoption push itself, including
   an existing consumer whose master pins other tools but not yet this one: judging with those pins
   would refuse every push, the adoption push included), else `HEAD`. A judge that does not pin the
   layer's tool at all (a branch from before the adoption) skips the layer with a `not applied` notice: it could
   drop its own pin anyway, so refusing would protect nothing. Pins that cannot be read at all (torn JSON, a wrong
   shape) never switch a layer off: such a ref still judges and the runner refuses. If origin/master itself carries
   torn pins, every push is refused, the repair included; land the repair with `git push --no-verify` after review,
   or fix the file on the remote. Protected
   branches come from the consumer's `factory-pins/ff-only.json` (`{"protected": [...]}`) at the
   judge ref when present, else `master`/`main`:

   ```sh
   # factory-ff-only
   FF_PROTECTED="refs/remotes/origin/master refs/remotes/origin/main"
   FF_REFS=$(cat)
   # ff_pins REF: 0 = REF's pins pin pre-push-ff-only; 3 = they do not, or REF has no pins; any other = unreadable pins
   # (BOM, bad JSON, wrong shape): such a REF still judges, and the runner refuses with its own reason.
   ff_pins() {
     git cat-file -e "$1:factory-pins/factory-pins.json" 2>/dev/null || return 3
     git show "$1:factory-pins/factory-pins.json" | python -I -c "import json, sys; t = json.loads(sys.stdin.buffer.read().decode('utf-8-sig')).get('tools', {}); sys.exit(0 if isinstance(t.get(sys.argv[1]), dict) else 3)" pre-push-ff-only 2>/dev/null
   }
   FF_JUDGE=
   for FF_P in $FF_PROTECTED; do
     if git cat-file -e "$FF_P:factory-pins/pin-runner.py" 2>/dev/null && { ff_pins "$FF_P" || [ $? -ne 3 ]; }; then FF_JUDGE=$FF_P; break; fi
   done
   [ -n "$FF_JUDGE" ] || FF_JUDGE=$(printf '%s\n' "$FF_REFS" | awk '$2 !~ /^0+$/ { print $2; exit }')
   [ -n "$FF_JUDGE" ] || FF_JUDGE=HEAD
   FF_PST=0
   ff_pins "$FF_JUDGE" || FF_PST=$?
   if [ "$FF_PST" -eq 3 ]; then
     echo "[ff-only] not applied: $FF_JUDGE does not pin pre-push-ff-only (it applies once a protected branch pins it)" >&2
   else
   FF_TOOL=$(mktemp) && git show "$FF_JUDGE:factory-pins/pin-runner.py" > "$FF_TOOL" \
     || { rm -f "$FF_TOOL"; echo "[ff-only] PUSH REFUSED: cannot read $FF_JUDGE:factory-pins/pin-runner.py" >&2; exit 1; }
   FF_CFG=$(mktemp)
   ff_run() {
     printf '%s\n' "$FF_REFS" | python -I "$FF_TOOL" --pins "$(git rev-parse --show-toplevel)/factory-pins/factory-pins.json" \
         --pins-ref "$FF_JUDGE" run pre-push-ff-only -- "$@"
   }
   FF_RC=0
   if git show "$FF_JUDGE:factory-pins/ff-only.json" > "$FF_CFG" 2>/dev/null; then
     ff_run "$@" --config "$FF_CFG" || FF_RC=$?
   else
     ff_run "$@" || FF_RC=$?
   fi
   rm -f "$FF_TOOL" "$FF_CFG"
   [ "$FF_RC" -eq 0 ] || { echo "[ff-only] PUSH REFUSED (exit $FF_RC)" >&2; exit 1; }
   fi
   exec 0<<FF_REFS_EOF
   $FF_REFS
   FF_REFS_EOF
   ```

   Regression-tested by `hooks/hooks.tests.py` (the block above is extracted and run by a real `git
   push`), including a repository whose only branch is not master (magic-lantern, 2026-10-16: the
   earlier `refs/remotes/origin/master`-only form refused every push there).

   The no-unpinned-tool layer has the same shape (`run no-unpinned-tool -- "$@"`, its own marker,
   ref lines restored for the next layer); Conjugal's `doctrine_outbox.py install_no_unpinned_tool`
   is the reference installer.

   Put it ahead of any layer that consumes stdin. Any non-zero, including an unavailable pin,
   refuses the push: a push is rare and recoverable, a forced rewrite of a shared branch is not.

## Bus writers: `pre-push-bus-tests`

The bus lands on master by direct push from many automated writers, and its CI runs only after the
push. On 2026-10-16 two writers each pushed a side that passed alone; the merge failed
`hooks.tests.py` on master (f4918600, b2cd2244) and stayed red until someone looked. This layer runs
the same fast suites before the push leaves the writer's bus clone.

1. Pin it in the project that hosts the writer (a review decision, Law 1):

   ```
   python factory-pins/pin-runner.py pin bus-tests --commit <bus-sha> --path hooks/pre-push-bus-tests.py --reviewer <who> --reason <why>
   ```

2. Chain it into the **bus clone's** `.git/hooks/pre-push`, ahead of any layer that consumes stdin, with
   the ref lines restored for the next layer:

   ```sh
   # factory-bus-tests
   BT_REFS=$(cat)
   BT_PINS="<consumer root>/factory-pins/pin-runner.py"   # the project whose pins reviewed this hook
   printf '%s\n' "$BT_REFS" | python -I "$BT_PINS" run bus-tests -- "$@" \
     || { echo "[bus-tests] PUSH REFUSED" >&2; exit 1; }
   exec 0<<BT_REFS_EOF
   $BT_REFS
   BT_REFS_EOF
   ```

   The suites themselves are the bytes being pushed: a bus writer tests its own commit, exactly as CI
   would after the push. The pinned hook decides which suites run and whether the push may go.

Cost (measured 2026-10-17, XPS 17, 20 logical CPUs, Windows, other agents running): a push that
touches none of the trigger paths (outbox, heartbeat, cos-feedback, specs, adjudications) runs
nothing and took 0.6 s. A push that touches them checks out the tip and runs all three
suites, python suites sharded over half the CPUs: 56 s end to end on that box (the slowest pin-runner shard
bounds it; serially the three suites took about 220 s there, and about 30 s on a Linux CI runner).
`--shards N`, `--timeout S` (per shard, default 300), `--all` (run whatever changed) and
`--config <json>` (`protected`, `trigger`, `suites`, `drift`) tune it. Tests: `BusTests` and `BusDrift` in `hooks.tests.py`.

**Drift checks (added 2026-10-17).** Two sealed pins turn CI red after an ordinary edit: the active r45
manifest binds `README.md` and six other subjects by blob (`MANIFEST_SUBJECT_MISMATCH`, repaired by hand at
158a072e and 9b08e709 the same day), and the R26 current census binds every project's `specs/<project>.md` and
the closed set of top-level specs (`PROJECT_SPEC_DRIFT`, `PROJECT_CLOSED_SET_MISMATCH`, repaired at da3e22dc and
797d1b86). When the pushed range touches a path a pin covers -- read from the pin AT THE PUSHED TIP, plus the
pin file, a new top-level `specs/*.md` and the checker -- the layer runs the checker CI runs, in check mode, on
the tip, in the same temporary worktree and in parallel with any suites:

| pin | runs | refusal prints |
|---|---|---|
| `manifests/universal-provider-control-reconciliation-r45.json` | `python tools/check_universal_manifest.py --treeish HEAD` | `python tools/refresh_current_universal_manifest.py --candidate <tip>` and how to write its `manifest` (docs/active-universal-manifest.md) |
| `adoption/current-token-control-r26.json` | `python tools/check_adoption_ledger.py --current --treeish HEAD` | `python tools/refresh_current_adoption_census.py` (adoption/current-token-control-r26.md); for a closed-set change, that it needs an epoch amendment first |

It never refreshes: a refresh is its own reviewed commit on top of the refused tip, and the push carries both.
A push that touches no covered path runs no drift check, so a writer is never refused for drift someone else
left on master (an append to `TRAPS.md` or `specs/<project>/cards.md`, a classified portable spec). Measured
2026-10-17 on the same box against bus 49009d20: untouched push 0.54 s; `README.md` edit refused in 16.6 s and
its refreshed tip passed in 16.0 s; `specs/conjugal.md` edit refused in 7.9 s and its refreshed tip passed in
7.4 s; a new top-level spec refused `PROJECT_CLOSED_SET_MISMATCH` in 10 s. `"drift": []` in `--config` turns the
checks off.
