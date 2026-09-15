#!/usr/bin/env bash
# Shared body for the FAKE claude / codex CLIs. No network, no model, no credentials.
#
# It answers the two surfaces the review-posture tooling actually uses:
#   claude:  --version | -p --model <id> [...]        prompt on stdin, reply on stdout
#   codex:   --version | exec -m <id> [...] -o <out>  prompt on stdin, reply written to <out>
#
# Sentinel behaviour is driven by env, so a test can reproduce the F4 shape exactly:
#   FAKE_MISS_ONCE=<lane>   that lane omits the sentinel on attempt 1 only (counter on disk)
#   FAKE_NEAR_MISS=<lane>   that lane always emits "LANE-COMPLETE." -- a near miss that must
#                           NEVER be accepted
# The lane name arrives in RP_LANE, which run.sh exports into each lane's subshell.
set -u
FAM="$1"; shift

[ "${1:-}" = "--version" ] && { echo "$FAM-fake 0.0.0"; exit 0; }

OUT=""; prev=""
for a in "$@"; do
  [ "$prev" = "-o" ] && OUT="$a"
  prev="$a"
done

LANE="${RP_LANE:-unknown-lane}"
PROMPT="$(cat)"   # a real CLI reads stdin, so we must too -- and the inventory probe's
                  # challenge is IN it, so it cannot simply be discarded.

# probe-machine-inventory.sh asks every candidate model for one fixed token. Answer it with
# exactly that token (nothing else), unless the test wants an unanswerable family.
#   FAKE_NO_INVENTORY=1    the family answers no challenge at all
#   FAKE_LEAK=<text>       the declined challenge answers with <text> instead, so the probe's
#                          redaction of its structural evidence is MEASURED, not asserted
case "$PROMPT" in
  *INVENTORY-OK*)
    if [ -n "${FAKE_NO_INVENTORY:-}" ]; then out="${FAKE_LEAK:-(this fake declines the challenge)}"
    else out="INVENTORY-OK"; fi
    if [ -n "$OUT" ]; then echo "$out" > "$OUT"; else echo "$out"; fi
    exit 0 ;;
esac

count_file="${RP_OUT:-.}/.fake-attempts.$LANE"
n=0; [ -f "$count_file" ] && n=$(cat "$count_file")
n=$((n + 1)); echo "$n" > "$count_file"

emit() {
  echo "FAKE $FAM reply for lane=$LANE attempt=$n"
  case "$LANE" in
    panel-*)
      # Shaped so review_posture.score() has something real to parse.
      echo "${LANE#panel-} SCORES:" | tr 'a-z' 'A-Z'
      for d in "Timeline Realism" "Contract Completeness" "Cross-Family Safety" \
               "Autonomy Achievement" "Throughput Goal" "Risk Mitigation"; do
        echo "$d: 70"
      done
      echo "COMPOSITE: 70.0"
      echo "TOP 3 REMAINING BLOCKERS:"
      echo "one \"quote a\"; two \"quote b\"; three \"quote c\""
      ;;
    classifier-*)
      echo "CLASSIFY"
      echo "F1: TEXT GROUNDED - fake"
      echo "MUST-FIX: F1"
      echo "STOPPING: FLAT"
      echo "CEILING: 80"
      echo "HAND-OFF: run the fake experiment"
      ;;
    consolidator) echo "## Design findings"; echo "§1 | \"q\" | d | REPLACES: \"a\" -> \"b\" | PROOF: p" ;;
    *) echo "§1 | \"q\" | fake finding | REPLACES: \"a\" -> \"b\" | PROOF: p" ;;
  esac
  if [ "${FAKE_NEAR_MISS:-}" = "$LANE" ]; then
    echo "LANE-COMPLETE."                       # near miss: trailing period
  elif [ "$n" -le 1 ] && case " ${FAKE_MISS_ONCE:-} " in *" $LANE "*) true;; *) false;; esac; then
    echo "(no sentinel on this attempt)"        # the measured F4 shape: rc 0, bytes > 0, no sentinel
  else
    echo "LANE-COMPLETE"
  fi
}

if [ -n "$OUT" ]; then
  emit > "$OUT"
  echo "fake $FAM log: wrote $OUT"
else
  emit
fi
exit 0
