#!/usr/bin/env bash
# Full Conjugal-standard review posture, stages A-D, in ONE invocation (see README.md here).
#
#   RP_OUT=<abs out dir> RP_SUBJECT=<abs subject file> RP_BENCH=<abs test bench> RP_REPO=<abs subject repo> \
#     bash tools/review-posture/run.sh [--from B|C|D] [--dry-run]
#
# --dry-run   generate and binding-check every prompt it can, dispatch nothing.
# --from X    reuse earlier stages already in RP_OUT (only if subject blob and bench HEAD are unchanged -- say so in the filing).
# The final lines are the posture measurement; exit 1 if the posture is PARTIAL.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
PY="python $HERE/review_posture.py"
: "${RP_OUT:?}" "${RP_SUBJECT:?}" "${RP_BENCH:?}" "${RP_REPO:?}"
FROM=A; DRY=0
while [ $# -gt 0 ]; do case "$1" in --from) FROM=$2; shift 2;; --dry-run) DRY=1; shift;; *) echo "unknown arg $1"; exit 2;; esac; done
export RP_OUT RP_SUBJECT RP_BENCH RP_REPO

# A Windows host can resolve `bash` to WSL's, which sees neither this CLI nor these paths.
case "$(command -v bash)" in */[Ww]indows/[Ss]ystem32/*) echo "WSL bash on PATH -- refuse"; exit 2;; esac
[ -f "$RP_SUBJECT" ] || { echo "SUBJECT MISSING: $RP_SUBJECT"; exit 2; }
eval "$($PY ids)" || exit 2
mkdir -p "$RP_OUT"

stamp() { echo "$(date -u +%FT%TZ) $*"; }
ran()   { grep -q '^LANE-COMPLETE\s*$' "$RP_OUT/$1.txt" 2>/dev/null; }
clear_lanes() { for n in "$@"; do rm -f "$RP_OUT/$n.txt" "$RP_OUT/$n.rc" "$RP_OUT/$n.log"; done; }
claude_lane() {  # name model secs
  ( cd "$RP_REPO" && timeout "$3" claude -p --model "$2" --permission-mode plan --add-dir "$RP_REPO" --add-dir "$RP_BENCH" \
      < "$RP_OUT/$1.prompt" > "$RP_OUT/$1.txt" 2> "$RP_OUT/$1.log"; echo $? > "$RP_OUT/$1.rc" ) & }
codex_lane() {   # name model secs
  ( timeout "$3" codex exec -m "$2" -c model_reasoning_effort=high -s read-only --cd "$RP_REPO" \
      -o "$RP_OUT/$1.txt" - < "$RP_OUT/$1.prompt" > "$RP_OUT/$1.log" 2>&1; echo $? > "$RP_OUT/$1.rc" ) & }
dispatch() {     # name family nickname secs  -> pid on stdout var LASTPID
  local id; id=$(eval echo "\$MODEL_$(echo "$3" | tr a-z A-Z)")
  if [ "$2" = claude ]; then claude_lane "$1" "$id" "$4"; else codex_lane "$1" "$id" "$4"; fi
  LASTPID=$!
}
stage_lanes() {  # stage -> "name family model" lines from roles.json
  python - "$HERE/roles.json" "$1" <<'PY'
import json,sys
for r in json.load(open(sys.argv[1]))["roles"]:
    if r["stage"]==sys.argv[2]:
        for l in r["lanes"]: print(l["name"], l["family"], l["model"])
PY
}
run_stage() {    # stage secs
  local pids=() name fam nick
  while read -r name fam nick; do clear_lanes "$name"; dispatch "$name" "$fam" "$nick" "$2"; pids+=("$LASTPID"); done < <(stage_lanes "$1")
  wait "${pids[@]}"
}

order="A B C D"; order=${order#*"$FROM"}; order="$FROM$order"
for st in $order; do
  $PY prompts "$st" || { echo "STAGE $st prompt generation failed"; break; }
  if [ "$DRY" = 1 ]; then stamp "dry-run: stage $st prompts OK"; [ "$st" = B ] && break; continue; fi
  stamp "stage $st dispatch"
  case $st in
    A) run_stage A 1800 ;;
    B) run_stage B 1800; $PY score ;;
    C) run_stage C 1500 ;;
    D) run_stage D 900; $PY tally ;;
  esac
  stamp "stage $st done"
done

echo "=== lane status (judge on the sentinel, not rc, not bytes) ==="
for st in A B C D; do while read -r name fam nick; do
  ran "$name" && v=RAN || v=DID-NOT-RUN
  printf 'stage=%s lane=%-14s %-11s rc=%-5s bytes=%s\n' "$st" "$name" "$v" "$(cat "$RP_OUT/$name.rc" 2>/dev/null || echo NONE)" "$(wc -c < "$RP_OUT/$name.txt" 2>/dev/null || echo 0)"
done < <(stage_lanes "$st"); done
[ -f "$RP_OUT/rubric_id" ] && echo "rubric_id: $(cat "$RP_OUT/rubric_id")"
$PY posture
