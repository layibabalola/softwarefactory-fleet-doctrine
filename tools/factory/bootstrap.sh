#!/bin/sh
# Make a project a consumer WITHOUT running unverified bytes: write the reviewed runner blob, prove its
# identity against git's own tree entry, and only then run it. Refuses (exit 2, runner never started) on mismatch.
# usage: bootstrap.sh <bus-clone> <bus-sha> <tool | profile:NAME> <reviewer> <reason> [project-root]
# profile:NAME runs `init --profile NAME` (a whole factory) instead of `install <tool>`.
set -eu
[ $# -ge 5 ] || { echo "usage: bootstrap.sh <bus-clone> <bus-sha> <tool|profile:NAME> <reviewer> <reason> [project-root]" >&2; exit 2; }
bus=$1 sha=$2 tool=$3 who=$4 why=$5 proj=${6:-.}
rel=tools/factory/pin-runner.py
dst=$proj/factory-pins/pin-runner.py
want=$(git -C "$bus" rev-parse --verify "$sha:$rel") || { echo "REFUSED: $sha has no $rel in $bus" >&2; exit 2; }
mkdir -p "$proj/factory-pins"
git -C "$bus" show "$sha:$rel" > "$dst.tmp"
got=$(git hash-object --no-filters "$dst.tmp")
if [ "$got" != "$want" ]; then
  rm -f "$dst.tmp"
  echo "REFUSED: runner bytes hash to $got, not object $want; nothing was run" >&2
  exit 2
fi
mv "$dst.tmp" "$dst"
case $tool in
  profile:*) exec "${PYTHON:-python}" "$dst" init --profile "${tool#profile:}" --commit "$sha" --reviewer "$who" --reason "$why" --project-root "$proj" --bus "$bus" ;;
  *) exec "${PYTHON:-python}" "$dst" install "$tool" --commit "$sha" --reviewer "$who" --reason "$why" --project-root "$proj" --bus "$bus" ;;
esac
