#!/usr/bin/env bash
# Derive this machine's provider inventory by DISPATCHING to each candidate model,
# not by asserting a table. Writes ~/.claude/machine-inventory.yaml.
#
# Why probe rather than declare: a model id that has been retired or mistyped still
# answers -- the CLI returns an unrecognized-model error, on stdout, at a byte count
# LARGER than a real reply. Neither exit code nor output size separates a live model
# from a dead one. Asking for a fixed token and requiring exactly it does.
#
# Usage: probe-machine-inventory.sh [--dry-run]
set -u

DRY=0; [ "${1:-}" = "--dry-run" ] && DRY=1
DEST="$HOME/.claude/machine-inventory.yaml"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
SENTINEL="INVENTORY-OK"

CLAUDE_MODELS="opus:claude-opus-5 sonnet:claude-sonnet-5 haiku:claude-haiku-4-5-20251001 fable:claude-fable-5"
CODEX_MODELS="sol:gpt-5.6-sol luna:gpt-5.6-luna astra:gpt-6-astra"

printf 'Reply with exactly this and nothing else: %s\n' "$SENTINEL" > "$WORK/ask"

probe() {  # family nickname id
  local fam=$1 nick=$2 id=$3
  local codex_cmd="codex"
  # On Windows, the bash shim for codex is broken (TRAP: npm bash shim for codex).
  # Use codex.cmd (PowerShell native) instead of codex (bash shim).
  if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "mingw"* || "$OSTYPE" == "win32" ]] || uname -s | grep -qi "MINGW"; then
    codex_cmd="codex.cmd"
  fi
  if [ "$fam" = claude ]; then
    timeout 120 claude -p --model "$id" < "$WORK/ask" > "$WORK/$fam.$nick" 2>&1
  else
    timeout 180 $codex_cmd exec -m "$id" -s read-only --skip-git-repo-check \
      -o "$WORK/$fam.$nick" - < "$WORK/ask" > /dev/null 2>&1
  fi
  # Anchored, whole-line match. An unanchored grep accepts the token wherever it appears --
  # including inside an echoed prompt or an error that quotes the instruction -- which would
  # verify a model that never answered.
  grep -qx "$SENTINEL" "$WORK/$fam.$nick" 2>/dev/null && echo "$nick:$id:VERIFIED" \
    || echo "$nick:$id:UNVERIFIED"
}

echo "probing (parallel) ..." >&2
for pair in $CLAUDE_MODELS; do probe claude "${pair%%:*}" "${pair##*:}" > "$WORK/r.claude.${pair%%:*}" & done
for pair in $CODEX_MODELS;  do probe codex  "${pair%%:*}" "${pair##*:}" > "$WORK/r.codex.${pair%%:*}"  & done
wait

emit_family() {  # family  auth_probe  invoke
  local fam=$1
  local n_ok=0 lines=""
  for f in "$WORK"/r.$fam.*; do
    [ -e "$f" ] || continue
    IFS=: read -r nick id state < "$f"
    if [ "$state" = VERIFIED ]; then
      lines="$lines      $nick: $id"$'\n'; n_ok=$((n_ok+1))
    else
      lines="$lines      # $nick: $id   # UNVERIFIED -- not dispatchable"$'\n'
    fi
  done
  [ "$n_ok" -gt 0 ] && echo "    available: true" || echo "    available: false"
  echo "    models:"
  printf '%s' "$lines"
}

{
  echo "# Derived by tools/probe-machine-inventory.sh -- every id below answered a sentinel"
  echo "# challenge on this machine. Commented ids did not; they are not dispatchable."
  echo "# Re-run after a CLI upgrade or account rotation."
  echo "generated_at: $(date -Iseconds)"
  # Stamp the identity this inventory was derived UNDER. Accounts cycle without warning, and a
  # rotation re-aligns the auth surfaces while leaving artifacts derived under the old account
  # in place -- measured 2026-09-13, when both surfaces rotated correctly and the inventory
  # still named the previous account. A capability table is only true for the identity that
  # probed it: a later reader whose account differs from this line is holding a stale file,
  # and without the line there is nothing to compare against.
  echo "probed_under: ${PROBE_IDENTITY:-unknown}   # pass PROBE_IDENTITY=<account or fingerprint>; 'unknown' means staleness cannot be detected"
  echo "host_cores: ${NUMBER_OF_PROCESSORS:-$(nproc 2>/dev/null || echo unknown)}"
  echo "agents_max: $(( ${NUMBER_OF_PROCESSORS:-4} / 2 ))"
  echo "providers:"
  echo "  claude:"
  echo "    cli_path: claude"
  echo "    auth_probe: \"python tools/check-cli-auth.py\""
  echo "    invoke: \"claude -p --model <id> --permission-mode plan --add-dir <repo> < <prompt-file>\""
  emit_family claude
  echo "  codex:"
  echo "    cli_path: codex"
  echo "    auth_probe: \"codex login status\""
  echo "    invoke: \"codex exec -m <id> -s read-only -C <repo> -o <out> - < <prompt-file>\""
  emit_family codex
} > "$WORK/inventory.yaml"

echo "--- derived ---"
cat "$WORK/inventory.yaml"

# Refuse to write an inventory in which nothing verified. On a box where the shell lacks
# `timeout`, or the CLIs are absent, or auth is dead, every probe fails the same way a
# genuinely-unavailable model does -- and an all-false inventory written from that state is
# indistinguishable from an honest one. Fail loudly instead; a missing file is a better
# signal than a confident empty one.
if ! grep -qE '^      [a-z]+: [a-z0-9.-]+$' "$WORK/inventory.yaml"; then
  echo "--- REFUSING TO WRITE: zero models verified ---" >&2
  echo "    Every probe failed. Check: CLIs on PATH, auth (\`codex login status\`," >&2
  echo "    \`python tools/check-cli-auth.py\`), and that this shell has \`timeout\`." >&2
  exit 3
fi

if [ "$DRY" = 1 ]; then
  echo "--- dry run: $DEST not written ---"
else
  mkdir -p "$(dirname "$DEST")"
  cp "$WORK/inventory.yaml" "$DEST"
  echo "--- wrote $DEST ---"
fi
