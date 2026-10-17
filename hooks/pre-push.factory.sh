#!/bin/sh
# Factory pre-push layers, installed by `pin-runner.py init` (bus: hooks/pre-push.factory.sh; layer contract:
# hooks/README.md). Each layer reads the ref lines once, judges them with the vendored runner and the pins read
# from a JUDGE ref (a pushed branch cannot re-pin its own judge), refuses on any non-zero, and restores the ref
# lines on stdin for the next layer. To chain another layer (git-lfs, ...), append it below the last one.
set -e
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
# factory-no-unpinned-tool
NUT_PROTECTED="refs/remotes/origin/master refs/remotes/origin/main"
NUT_REFS=$(cat)
# nut_pins REF: 0 = REF's pins pin no-unpinned-tool; 3 = they do not, or REF has no pins; any other = unreadable pins
# (BOM, bad JSON, wrong shape): such a REF still judges, and the runner refuses with its own reason.
nut_pins() {
  git cat-file -e "$1:factory-pins/factory-pins.json" 2>/dev/null || return 3
  git show "$1:factory-pins/factory-pins.json" | python -I -c "import json, sys; t = json.loads(sys.stdin.buffer.read().decode('utf-8-sig')).get('tools', {}); sys.exit(0 if isinstance(t.get(sys.argv[1]), dict) else 3)" no-unpinned-tool 2>/dev/null
}
NUT_JUDGE=
for NUT_P in $NUT_PROTECTED; do
  if git cat-file -e "$NUT_P:factory-pins/pin-runner.py" 2>/dev/null && { nut_pins "$NUT_P" || [ $? -ne 3 ]; }; then NUT_JUDGE=$NUT_P; break; fi
done
[ -n "$NUT_JUDGE" ] || NUT_JUDGE=$(printf '%s\n' "$NUT_REFS" | awk '$2 !~ /^0+$/ { print $2; exit }')
[ -n "$NUT_JUDGE" ] || NUT_JUDGE=HEAD
NUT_PST=0
nut_pins "$NUT_JUDGE" || NUT_PST=$?
if [ "$NUT_PST" -eq 3 ]; then
  echo "[no-unpinned-tool] not applied: $NUT_JUDGE does not pin no-unpinned-tool (it applies once a protected branch pins it)" >&2
else
NUT_TOOL=$(mktemp) && git show "$NUT_JUDGE:factory-pins/pin-runner.py" > "$NUT_TOOL" \
  || { rm -f "$NUT_TOOL"; echo "[no-unpinned-tool] PUSH REFUSED: cannot read $NUT_JUDGE:factory-pins/pin-runner.py" >&2; exit 1; }
NUT_RC=0
printf '%s\n' "$NUT_REFS" | python -I "$NUT_TOOL" --pins "$(git rev-parse --show-toplevel)/factory-pins/factory-pins.json" \
    --pins-ref "$NUT_JUDGE" run no-unpinned-tool -- "$@" || NUT_RC=$?
rm -f "$NUT_TOOL"
[ "$NUT_RC" -eq 0 ] || { echo "[no-unpinned-tool] PUSH REFUSED (exit $NUT_RC)" >&2; exit 1; }
fi
exec 0<<NUT_REFS_EOF
$NUT_REFS
NUT_REFS_EOF
