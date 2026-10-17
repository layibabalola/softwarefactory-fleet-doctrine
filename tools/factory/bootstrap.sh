#!/bin/sh
# Make a project a consumer WITHOUT running unverified bytes: write the reviewed runner blob into a PRIVATE temporary
# directory, prove its identity against git's own tree entry, and only then run it there, isolated (python -I: the
# project's files can never be imported into it). The project itself is touched only by install/init, which plan
# everything first and refuse (writing nothing) on any mismatch. Refuses (exit 2, runner never started) on a mismatch.
# usage: bootstrap.sh <bus-clone> <bus-sha> <tool | profile:NAME> <reviewer> <reason> [project-root]
# profile:NAME runs `init --profile NAME` (a whole factory) instead of `install <tool>`.
set -eu
[ $# -ge 5 ] || { echo "usage: bootstrap.sh <bus-clone> <bus-sha> <tool|profile:NAME> <reviewer> <reason> [project-root]" >&2; exit 2; }
bus=$1 sha=$2 tool=$3 who=$4 why=$5 proj=${6:-.}
rel=tools/factory/pin-runner.py
want=$(git -C "$bus" rev-parse --verify "$sha:$rel") || { echo "REFUSED: $sha has no $rel in $bus" >&2; exit 2; }
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
git -C "$bus" show "$sha:$rel" > "$tmp/pin-runner.py"
got=$(git hash-object --no-filters "$tmp/pin-runner.py")
if [ "$got" != "$want" ]; then
  echo "REFUSED: runner bytes hash to $got, not object $want; nothing was run" >&2
  exit 2
fi
rc=0
case $tool in
  profile:*) "${PYTHON:-python}" -I "$tmp/pin-runner.py" init --profile "${tool#profile:}" --commit "$sha" --reviewer "$who" --reason "$why" --project-root "$proj" --bus "$bus" || rc=$? ;;
  *) "${PYTHON:-python}" -I "$tmp/pin-runner.py" install "$tool" --commit "$sha" --reviewer "$who" --reason "$why" --project-root "$proj" --bus "$bus" || rc=$? ;;
esac
exit $rc
