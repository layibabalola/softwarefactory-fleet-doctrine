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
# An array, not a string: a checkout path with a space (C:\!Layi Wkspc\...) split the string form,
# `ids` failed, `eval ""` succeeded, and stage A died with 17/17 DID-NOT-RUN (airmypc, 2026-09-14).
PY=(python "$HERE/review_posture.py")
: "${RP_OUT:?}" "${RP_SUBJECT:?}" "${RP_BENCH:?}" "${RP_REPO:?}"
FROM=A; DRY=0
while [ $# -gt 0 ]; do case "$1" in --from) FROM=$2; shift 2;; --dry-run) DRY=1; shift;; *) echo "unknown arg $1"; exit 2;; esac; done
export RP_OUT RP_SUBJECT RP_BENCH RP_REPO

# A Windows host can resolve `bash` to WSL's, which sees neither this CLI nor these paths.
case "$(command -v bash)" in */[Ww]indows/[Ss]ystem32/*) echo "WSL bash on PATH -- refuse"; exit 2;; esac
[ -f "$RP_SUBJECT" ] || { echo "SUBJECT MISSING: $RP_SUBJECT"; exit 2; }
ids_out=$("${PY[@]}" ids) || { echo "MODEL IDS UNRESOLVED -- refuse"; exit 2; }
# Parsed, never eval'd: an inventory value is data, and `luna: x; false` must not become shell syntax.
while IFS='=' read -r k v; do
  v=${v%$'\r'}; [ -n "$k" ] || continue
  [[ "$k" =~ ^MODEL_[A-Z0-9_]+$ && "$v" =~ ^[A-Za-z0-9._:-]+$ ]] || { echo "MODEL ID LINE REJECTED: $k=$v -- refuse"; exit 2; }
  printf -v "$k" '%s' "$v"
done <<< "$ids_out"
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
  local var; var="MODEL_$(echo "$3" | tr a-z A-Z)"
  local id="${!var:-}"
  [ -n "$id" ] || { echo "UNRESOLVED nickname $3 for lane $1 -- refuse"; exit 2; }
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

# A launcher that cannot start is not an unavailable family: rc=127 from a broken npm shim once dropped every
# Codex lane while auth and model ids were healthy (TRAPS, airmypc 2026-09-14). Refuse before dispatching anything.
order="A B C D"; order=${order#*"$FROM"}; order="$FROM$order"

# Resolve every lane's model before any lane is cleared or dispatched, so a bad nickname cannot strand paid lanes.
unresolved=0
for st in $order; do while read -r name fam nick; do
  var="MODEL_$(echo "$nick" | tr a-z A-Z)"
  [ -n "${!var:-}" ] || { echo "UNRESOLVED nickname $nick for lane $name"; unresolved=1; }
done < <(stage_lanes "$st"); done
[ "$unresolved" = 0 ] || { echo "UNRESOLVED nicknames -- refuse to dispatch"; exit 2; }

# Probe the entrypoint each lane actually uses, bounded, without spending a model call.
probe() { local out; out=$(timeout -k 5 30 "$@" 2>&1); lrc=$?; lline=$(printf '%s' "$out" | head -n 1); }
launchers_ok=1
for fam in $(for st in $order; do stage_lanes "$st"; done | awk '{print $2}' | sort -u); do
  case "$fam" in
    claude) checks=("claude --version" "claude --help") ;;
    codex)  checks=("codex --version" "codex exec --help") ;;
    *)      checks=("$fam --version") ;;
  esac
  for c in "${checks[@]}"; do
    probe $c
    if [ "$lrc" = 0 ]; then echo "launcher ok family=$fam [$c] $lline"
    else [ "$lrc" = 124 ] && lline="timed out after 30s"; echo "LAUNCHER-BROKEN family=$fam [$c] rc=$lrc: $lline"; launchers_ok=0; fi
  done
done
[ "$launchers_ok" = 1 ] || [ "$DRY" = 1 ] || { echo "LAUNCHER-BROKEN -- refuse to dispatch (a posture cannot be complete)"; exit 2; }
for st in $order; do
  "${PY[@]}" prompts "$st" || { echo "STAGE $st prompt generation failed"; break; }
  if [ "$DRY" = 1 ]; then stamp "dry-run: stage $st prompts OK"; [ "$st" = B ] && break; continue; fi
  stamp "stage $st dispatch"
  case $st in
    A) run_stage A 1800 ;;
    B) run_stage B 1800; "${PY[@]}" score ;;
    C) run_stage C 1500 ;;
    D) run_stage D 900; "${PY[@]}" tally ;;
  esac
  stamp "stage $st done"
done

echo "=== lane status (judge on the sentinel, not rc, not bytes) ==="
for st in A B C D; do while read -r name fam nick; do
  ran "$name" && v=RAN || v=DID-NOT-RUN
  printf 'stage=%s lane=%-14s %-11s rc=%-5s bytes=%s\n' "$st" "$name" "$v" "$(cat "$RP_OUT/$name.rc" 2>/dev/null || echo NONE)" "$(wc -c < "$RP_OUT/$name.txt" 2>/dev/null || echo 0)"
done < <(stage_lanes "$st"); done
[ -f "$RP_OUT/rubric_id" ] && echo "rubric_id: $(cat "$RP_OUT/rubric_id")"
"${PY[@]}" posture
