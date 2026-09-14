#!/usr/bin/env bash
# THE offline test command for the review-posture tooling. No network, no real model calls,
# no credentials. This is the file the README, bootstrap/lane-orchestrator.md §1b and PROMPT A
# all name, and it is the file that exists -- those docs previously pointed at a `run-tests.sh`
# that had never been written, so the one documented verification step a new member reaches
# exited 127.
#
#   bash tools/review-posture/tests/run-tests.sh
#
# Runs from any working directory and from a path containing a space: every path below is
# derived from $0, and every one is quoted.
#
# It runs, in order:
#   1. bash -n over every shell script the tooling ships
#   2. tests/test-selfheal.sh  -- the offline self-heal suite (fake CLIs, spaced temp dirs)
#   3. tests/test_review_posture.py -- the repo's pytest file for this tool, IF a python with
#      pytest is available. Absent pytest is reported as SKIPPED, never as a pass.
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
RPDIR="$(cd "$HERE/.." && pwd)"
REPO="$(cd "$RPDIR/../.." && pwd)"

. "$REPO/tools/lib/cli-resolve.sh"
PYTHON="$(cli_python 2>/dev/null || true)"

fail=0

echo "=== 1/3  bash -n"
for s in "$REPO/tools/lib/cli-resolve.sh" "$RPDIR/run.sh" \
         "$REPO/tools/probe-machine-inventory.sh" "$REPO/tools/lane-dispatch.sh" \
         "$HERE/test-selfheal.sh" "$HERE/run-tests.sh" "$HERE/fakes/fake-cli-body.sh" "$HERE/fakes/codex.js"; do
  [ -f "$s" ] || { echo "  MISSING  $s"; fail=1; continue; }
  if bash -n "$s" 2>&1; then echo "  ok       ${s#"$REPO"/}"; else echo "  SYNTAX   ${s#"$REPO"/}"; fail=1; fi
done
echo

echo "=== 2/3  tests/test-selfheal.sh"
bash "$HERE/test-selfheal.sh" || fail=1
echo

echo "=== 3/3  tests/test_review_posture.py"
if [ -z "$PYTHON" ]; then
  echo "  SKIPPED: no runnable python found (cli_python)"
elif ! "$PYTHON" -c 'import pytest' >/dev/null 2>&1; then
  echo "  SKIPPED: $PYTHON has no pytest installed"
elif [ ! -f "$REPO/tests/test_review_posture.py" ]; then
  echo "  SKIPPED: $REPO/tests/test_review_posture.py not present"
else
  ( cd "$REPO" && "$PYTHON" -m pytest -q tests/test_review_posture.py ) || fail=1
fi
echo

if [ "$fail" = 0 ]; then echo "ALL OFFLINE TESTS PASSED"; else echo "OFFLINE TESTS FAILED"; fi
exit "$fail"
