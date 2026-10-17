#!/bin/sh
# Factory pre-push layers, installed by `pin-runner.py init` (bus: hooks/pre-push.factory.sh; layer contract:
# hooks/README.md). Each layer reads the ref lines once, judges them with the vendored runner and the pins read
# from a JUDGE ref (a pushed branch cannot re-pin its own judge), refuses on any non-zero, and restores the ref
# lines on stdin for the next layer. To chain another layer (git-lfs, ...), append it below the last one.
set -e
# factory-ff-only
FF_PROTECTED="refs/remotes/origin/master refs/remotes/origin/main"
FF_REFS=$(cat)
FF_JUDGE=
for FF_P in $FF_PROTECTED; do
  if git cat-file -e "$FF_P:factory-pins/pin-runner.py" 2>/dev/null \
     && git show "$FF_P:factory-pins/factory-pins.json" 2>/dev/null | grep -q '"pre-push-ff-only"'; then
    FF_JUDGE=$FF_P; break
  fi
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
# factory-no-unpinned-tool
NUT_PROTECTED="refs/remotes/origin/master refs/remotes/origin/main"
NUT_REFS=$(cat)
NUT_JUDGE=
for NUT_P in $NUT_PROTECTED; do
  if git cat-file -e "$NUT_P:factory-pins/pin-runner.py" 2>/dev/null \
     && git show "$NUT_P:factory-pins/factory-pins.json" 2>/dev/null | grep -q '"no-unpinned-tool"'; then
    NUT_JUDGE=$NUT_P; break
  fi
done
[ -n "$NUT_JUDGE" ] || NUT_JUDGE=$(printf '%s\n' "$NUT_REFS" | awk '$2 !~ /^0+$/ { print $2; exit }')
[ -n "$NUT_JUDGE" ] || NUT_JUDGE=HEAD
NUT_TOOL=$(mktemp) && git show "$NUT_JUDGE:factory-pins/pin-runner.py" > "$NUT_TOOL" \
  || { rm -f "$NUT_TOOL"; echo "[no-unpinned-tool] PUSH REFUSED: cannot read $NUT_JUDGE:factory-pins/pin-runner.py" >&2; exit 1; }
NUT_RC=0
printf '%s\n' "$NUT_REFS" | python "$NUT_TOOL" --pins "$(git rev-parse --show-toplevel)/factory-pins/factory-pins.json" \
    --pins-ref "$NUT_JUDGE" run no-unpinned-tool -- "$@" || NUT_RC=$?
rm -f "$NUT_TOOL"
[ "$NUT_RC" -eq 0 ] || { echo "[no-unpinned-tool] PUSH REFUSED (exit $NUT_RC)" >&2; exit 1; }
exec 0<<NUT_REFS_EOF
$NUT_REFS
NUT_REFS_EOF
