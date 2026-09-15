#!/usr/bin/env bash
# Dispatch ONE review lane with a fallback ladder, and record provenance that survives both
# a model substitution and a later price change.
#
#   lane-dispatch.sh <outdir> <lane-name> <effort> <prompt-file> <timeout-s> <model> [model...]
#
# Two things this exists to get right:
#
# 1. TIMESTAMPS ARE TAKEN AT DISPATCH, NOT AT EXTRACTION. Cost is derived later by joining
#    raw token counts against a dated price table, so the join key must be when the INFERENCE
#    ran. Extraction can happen minutes or weeks later, can be re-run, and can straddle a
#    price change -- stamping rows at extraction time silently prices old work at new rates.
#
# 2. THE ROW RECORDS THE MODEL THAT ACTUALLY RAN. When the recommended model is unavailable
#    and the ladder falls back (Fable -> Opus, say), attributing the findings to the requested
#    model corrupts every comparison built on top of it -- the same provenance failure as
#    calling a single-family review cross-family. requested_model and actual_model are
#    separate fields, and a substitution is never silent.
#
# 3. THE CLI IS RESOLVED, NOT ASSUMED. `claude` and `timeout` are reached through
#    tools/lib/cli-resolve.sh (invocation seam only -- the ladder, the classifier and the
#    provenance row are untouched). An npm shim whose interpreter is broken exits 127 before
#    any inference, which this script would otherwise walk the whole ladder over and record
#    as "no model available" -- a capability claim with a PATH cause.
set -u

OUT=$1; LANE=$2; EFFORT=$3; PROMPT=$4; TMO=$5; shift 5
LADDER=("$@")
mkdir -p "$OUT"

. "$(cd "$(dirname "$0")" && pwd)/lib/cli-resolve.sh"
# Same one python discovery as run.sh and the probe: it EXECUTES each candidate, because a
# bare `python` can be a Windows Store stub that exits 9009 without ever being an interpreter.
PYTHON="$(cli_python)" || { echo "FAIL(no_python): $LANE -- no runnable python on PATH" >&2; exit 125; }
run_timeout_selftest || exit 125
if ! cli_resolve claude; then
  echo "FAIL(no_cli): $LANE -- $(cli_cause claude)" >&2
  exit 125
fi
cli_repair_line claude >&2

# Classify an attempt STRUCTURALLY, not by matching error prose. The JSON envelope carries an
# explicit `is_error` flag, and a request that never reached a model has zero tokens on every
# counter and duration_api_ms == 0. Both are stable; the wording is not -- an earlier version
# of this script grepped for "does not exist or you may not have access" and missed the real
# message, which says "may not exist". Text signatures rot silently; counters do not.
classify() {  # -> RAN | UNAVAILABLE | ERROR, plus a reason on stdout
"$PYTHON" - "$1" <<'PY'
import json,sys
try: d=json.load(open(sys.argv[1],encoding="utf-8",errors="replace"))
except Exception as e: print(f"ERROR\tunparseable envelope: {e}"); raise SystemExit
u=d.get("usage") or {}
tok=sum(int(u.get(k) or 0) for k in
        ("input_tokens","output_tokens","cache_read_input_tokens","cache_creation_input_tokens"))
no_inference = tok==0 and not (d.get("duration_api_ms") or 0)
msg=(d.get("result") or "")[:160].replace("\n"," ")
if d.get("is_error") or no_inference:
    print(f"UNAVAILABLE\t{msg or d.get('api_error_status') or 'no inference occurred'}")
else:
    print(f"RAN\t{msg[:40]}")
PY
}

started=$(date -u +%FT%TZ)   # -I is GNU-only; BSD/macOS date rejects it
rung=0; actual=""; reason=""; rc=99; t0=$started
for m in "${LADDER[@]}"; do
  t0=$(date -u +%FT%TZ)
  cli_timed claude "$TMO" -p --model "$m" --effort "$EFFORT" --permission-mode plan \
      --output-format json < "$PROMPT" > "$OUT/$LANE.raw" 2> "$OUT/$LANE.err"
  rc=$?
  verdict=$(classify "$OUT/$LANE.raw"); why=${verdict#*$'\t'}; verdict=${verdict%%$'\t'*}
  if [ "$verdict" = "RAN" ]; then actual=$m; break; fi
  echo "DEGRADED: $LANE model=$m -> $verdict ($why) -- advancing ladder" >&2
  reason="${reason}${reason:+; }$m: $why"
  rung=$((rung+1))
done
ended=$(date -u +%FT%TZ)

if [ -z "$actual" ]; then
  echo "FAIL(no_model_available): $LANE exhausted ladder [${LADDER[*]}]" >&2
fi

"$PYTHON" - "$OUT" "$LANE" <<PY
import json,sys,pathlib,re
out,lane=pathlib.Path(sys.argv[1]),sys.argv[2]
raw=out/f"{lane}.raw"
d={}
try: d=json.loads(raw.read_text(encoding="utf-8",errors="replace"))
except Exception: pass
body=d.get("result") or ""
(out/f"{lane}.txt").write_text(body,encoding="utf-8")
u=d.get("usage",{}) or {}
row=dict(
  lane=lane, effort="$EFFORT",
  started_at="$started", lane_started_at="$t0", ended_at="$ended",   # dispatch-time, for price join
  requested_model="${LADDER[0]}", actual_model="$actual" or None,
  fallback_rung=$rung, fallback_reason="$reason" or None,
  ladder="${LADDER[*]}".split(),
  rc=$rc,
  input_tokens=u.get("input_tokens"), output_tokens=u.get("output_tokens"),
  cache_read_tokens=u.get("cache_read_input_tokens"),
  cache_creation_tokens=u.get("cache_creation_input_tokens"),
  thinking_tokens=(u.get("output_tokens_details") or {}).get("thinking_tokens"),
  observed_cost_usd=d.get("total_cost_usd"),          # reconcile against derived to catch price drift
  bytes=len(body.encode()),
  findings=len(re.findall(r"(?m)^\s*§", body)),
  sentinel="RAN" if re.search(r"(?m)^LANE-COMPLETE\$", body) else "DID-NOT-RUN",
)
(out/f"{lane}.row.json").write_text(json.dumps(row), encoding="utf-8")
print(f"{lane}: {row['sentinel']} model={row['actual_model']} rung={row['fallback_rung']} "
      f"findings={row['findings']} cost={row['observed_cost_usd']}")
PY
