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
| [`pre-push-no-unpinned-tool.py`](pre-push-no-unpinned-tool.py) | git `pre-push` (ref lines on stdin) | exit 1 when the pushed commits add or modify a file named like a bus factory tool (tools/factory/*, hooks/*: any add or edit) or add a NEW copy of a census family (session-checkpoint, doctrine-outbox, doctrine-triage, resumability-check). Exempt: the vendored runner when it equals its pinned blob, and paths in `factory-pins/no-unpinned-tool.json` (read from the pushed tip) with a reason and an expiry at most 120 days out; an expired entry refuses. Families are kept equal to `tools/tool-census.config.json` by the tests |
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
   project) that already holds `factory-pins/pin-runner.py` -- there a pushed branch cannot weaken
   or re-pin its own judge -- else the commit being pushed (a project whose work never reaches a
   remote master, e.g. a local-only branch, and the adoption push itself), else `HEAD`. Protected
   branches come from the consumer's `factory-pins/ff-only.json` (`{"protected": [...]}`) at the
   judge ref when present, else `master`/`main`:

   ```sh
   # factory-ff-only
   FF_PROTECTED="refs/remotes/origin/master refs/remotes/origin/main"
   FF_REFS=$(cat)
   FF_JUDGE=
   for FF_P in $FF_PROTECTED; do
     if git cat-file -e "$FF_P:factory-pins/pin-runner.py" 2>/dev/null; then FF_JUDGE=$FF_P; break; fi
   done
   [ -n "$FF_JUDGE" ] || FF_JUDGE=$(printf '%s\n' "$FF_REFS" | awk '$2 !~ /^0+$/ { print $2; exit }')
   [ -n "$FF_JUDGE" ] || FF_JUDGE=HEAD
   FF_TOOL=$(mktemp) && git show "$FF_JUDGE:factory-pins/pin-runner.py" > "$FF_TOOL" \
     || { rm -f "$FF_TOOL"; echo "[ff-only] PUSH REFUSED: cannot read $FF_JUDGE:factory-pins/pin-runner.py" >&2; exit 1; }
   FF_CFG=$(mktemp)
   ff_run() {
     printf '%s\n' "$FF_REFS" | python "$FF_TOOL" --pins "$(git rev-parse --show-toplevel)/factory-pins/factory-pins.json" \
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
