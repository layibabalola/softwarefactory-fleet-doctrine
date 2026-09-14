#!/usr/bin/env bash
# Derive this machine's provider inventory by DISPATCHING to each candidate model,
# not by asserting a table. Writes ~/.claude/machine-inventory.yaml.
#
# Why probe rather than declare: a model id that has been retired or mistyped still
# answers -- the CLI returns an unrecognized-model error, on stdout, at a byte count
# LARGER than a real reply. Neither exit code nor output size separates a live model
# from a dead one. Asking for a fixed token and requiring exactly it does.
#
# And why the CLI is RESOLVED before anything is probed: on 2026-09-14 this script wrote
# `codex: available: false` with every codex id UNVERIFIED. Nothing was wrong with the
# account or the models -- %APPDATA%\npm\codex execs a stale npm `node` placeholder, so the
# CLI exited 127 before reaching a model. A broken interpreter and a dead account produce
# the SAME all-UNVERIFIED shape, so the shape alone must never be reported as a capability.
# tools/lib/cli-resolve.sh separates them, and its repairs are recorded below under `repairs:`.
#
# Usage: probe-machine-inventory.sh [--dry-run]
set -u

SELFDIR="$(cd "$(dirname "$0")" && pwd)"
DRY=0; [ "${1:-}" = "--dry-run" ] && DRY=1
DEST="$HOME/.claude/machine-inventory.yaml"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
SENTINEL="INVENTORY-OK"

. "$SELFDIR/lib/cli-resolve.sh"
# ONE python discovery, shared with tools/review-posture/run.sh (cli_python in cli-resolve.sh):
# it EXECUTES each candidate, because a Windows Store `python3` stub answers `command -v` and
# then exits 9009. Empty here is not fatal -- only derive_identity needs it, and it says so.
PYTHON="$(cli_python 2>/dev/null || true)"
run_timeout_selftest || { echo "--- REFUSING TO PROBE: this shell cannot bound a process ---" >&2; exit 3; }

CLAUDE_MODELS="opus:claude-opus-5 sonnet:claude-sonnet-5 haiku:claude-haiku-4-5-20251001 fable:claude-fable-5"
CODEX_MODELS="sol:gpt-5.6-sol luna:gpt-5.6-luna astra:gpt-6-astra"

printf 'Reply with exactly this and nothing else: %s\n' "$SENTINEL" > "$WORK/ask"

echo "resolving CLIs ..." >&2
for fam in claude codex; do
  cli_resolve "$fam" || echo "CLI_UNAVAILABLE family=$fam cause=$(cli_cause "$fam")" >&2
  cli_repair_line "$fam" >&2
done

# Structural evidence about a failed challenge, with anything token-shaped removed. The point
# is to let a reader tell a 127 from a timeout from a provider error WITHOUT a second run and
# WITHOUT ever writing a credential into a file that gets committed and pasted into filings:
# rc, whether anything came back at all, how much, and a redacted first line.
redact() {  # stdin -> one sanitized line, <=160 chars
  tr -d '\000' | tr '\r' '\n' | sed -n '/[^[:space:]]/{p;q;}' \
    | sed -E -e 's/(sk|pk|ghp|gho|xox[abps])-[A-Za-z0-9_-]{6,}/[REDACTED-TOKEN]/g' \
             -e 's/[Bb]earer[[:space:]]+[A-Za-z0-9._~+\/-]+=*/Bearer [REDACTED]/g' \
             -e 's/ey[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]*/[REDACTED-JWT]/g' \
             -e 's/[A-Za-z0-9_-]{32,}/[REDACTED-LONG-OPAQUE]/g' \
             -e 's/"/'"'"'/g' \
    | cut -c1-160
}

probe() {  # family nickname id
  local fam=$1 nick=$2 id=$3 rc=0 bytes=0 first=""
  # SUPERSEDES 97b6f66 ("windows bash shim invokes codex.cmd not codex"): that OS heuristic
  # forces codex.cmd on every Windows host, which breaks a Windows box with no .cmd rung and
  # needlessly reroutes a Windows box whose shim works. cli_resolve detects the broken shim
  # STRUCTURALLY and verifies a launcher ladder that already contains the .cmd rung.
  if [ "$(cli_verified "$fam")" != yes ]; then
    echo "$nick:$id:UNVERIFIED"                  # no CLI to ask; not a statement about the model
    printf '%s|%s|%s|%s|%s|%s\n' "$fam" "$nick" "$id" "not-attempted" "0" \
      "no resolved $fam CLI -- the challenge was never sent" > "$WORK/e.$fam.$nick"
    return 0
  fi
  if [ "$fam" = claude ]; then
    cli_timed claude 120 -p --model "$id" < "$WORK/ask" > "$WORK/$fam.$nick" 2>"$WORK/$fam.$nick.err"
    rc=$?
  else
    cli_timed codex 180 exec -m "$id" -s read-only --skip-git-repo-check \
      -o "$WORK/$fam.$nick" - < "$WORK/ask" > "$WORK/$fam.$nick.err" 2>&1
    rc=$?
  fi
  bytes=$(wc -c < "$WORK/$fam.$nick" 2>/dev/null || echo 0); bytes=$(echo "$bytes" | tr -d '[:space:]')
  first=$(cat "$WORK/$fam.$nick" "$WORK/$fam.$nick.err" 2>/dev/null | redact)
  # Anchored, whole-line match. An unanchored grep accepts the token wherever it appears --
  # including inside an echoed prompt or an error that quotes the instruction -- which would
  # verify a model that never answered. [[:space:]] not \s: \s is a GNU grep extension.
  if grep -qx "$SENTINEL[[:space:]]*" "$WORK/$fam.$nick" 2>/dev/null; then
    echo "$nick:$id:VERIFIED"
  else
    echo "$nick:$id:UNVERIFIED"
  fi
  printf '%s|%s|%s|%s|%s|%s\n' "$fam" "$nick" "$id" "$rc" "${bytes:-0}" \
    "${first:-(no output at all)}" > "$WORK/e.$fam.$nick"
}

echo "probing (parallel) ..." >&2
for pair in $CLAUDE_MODELS; do probe claude "${pair%%:*}" "${pair##*:}" > "$WORK/r.claude.${pair%%:*}" & done
for pair in $CODEX_MODELS;  do probe codex  "${pair%%:*}" "${pair##*:}" > "$WORK/r.codex.${pair%%:*}"  & done
wait

# Stamp the identity this inventory was derived UNDER. Accounts cycle without warning, and a
# rotation re-aligns the auth surfaces while leaving artifacts derived under the old account
# in place -- measured 2026-09-13, when both surfaces rotated correctly and the inventory
# still named the previous account. A capability table is only true for the identity that
# probed it: a later reader whose account differs from this line is holding a stale file, and
# without the line there is nothing to compare against. The value is the NON-SECRET
# fingerprint check-account-parity.py already publishes to a hook banner -- sha256(uuid)[:12].
# No token, no uuid, no email is read or written here.
derive_identity() {
  if [ -n "${PROBE_IDENTITY:-}" ]; then printf '%s\n' "$PROBE_IDENTITY"; return; fi
  local parity="$SELFDIR/check-account-parity.py" out fp
  [ -n "$PYTHON" ] || { printf '%s\n' "unknown   # reason: no python on PATH to run check-account-parity.py"; return; }
  [ -f "$parity" ] || { printf '%s\n' "unknown   # reason: $parity not found"; return; }
  out=$(run_timeout 30 "$PYTHON" "$parity" 2>/dev/null) || {
    printf '%s\n' "unknown   # reason: check-account-parity.py did not complete"; return; }
  fp=$(printf '%s\n' "$out" | sed -n 's/^\[parity\] cli[[:space:]][[:space:]]*fp=\([0-9a-f][0-9a-f]*\).*/\1/p' | head -1)
  if [ -n "$fp" ]; then printf '%s\n' "cli-account-fp:$fp   # sha256(accountUuid)[:12] via tools/check-account-parity.py"
  else printf '%s\n' "unknown   # reason: CLI surface published no accountUuid (signed out?)"; fi
}

emit_family() {  # family
  local fam=$1
  local n_ok=0 n_total=0 lines="" e efam enick eid erc ebytes efirst
  for f in "$WORK"/r.$fam.*; do
    [ -e "$f" ] || continue
    IFS=: read -r nick id state < "$f"
    n_total=$((n_total+1))
    if [ "$state" = VERIFIED ]; then
      lines="$lines      $nick: $id"$'\n'; n_ok=$((n_ok+1))
    else
      lines="$lines      # $nick: $id   # UNVERIFIED -- not dispatchable"$'\n'
    fi
  done
  [ "$n_ok" -gt 0 ] && echo "    available: true" || echo "    available: false"
  # Do not let a tooling fault masquerade as a capability verdict. If the whole family is
  # UNVERIFIED *and* its CLI never came back from repair, the only honest reading is "not
  # measured", and the line has to say which it is.
  if [ "$n_ok" -eq 0 ] && [ "$n_total" -gt 0 ]; then
    if [ "$(cli_verified "$fam")" != yes ]; then
      echo "    unavailable_cause: \"CLI-NOT-MEASURED -- fault=$(cli_fault "$fam") repair=$(cli_repair "$fam") verified=no; $(cli_cause "$fam")\""
      echo "    # Every $fam id below is UNVERIFIED because no working $fam CLI was reachable, NOT"
      echo "    # because the models or the account were rejected. Do not read this as a capability."
    else
      # NOT "auth". This script holds no auth evidence: it never reads a credential, never calls
      # a login-status surface, and cannot see a 401 separately from a 404, a DNS failure, a
      # retired model id, a sandbox denial or a proxy. "Every challenge failed" is consistent
      # with all of those, and naming the most alarming one sends an operator to re-authenticate
      # a healthy account -- the exact inverse of F1, where a PATH fault was read as auth. The
      # class is UNKNOWN until something actually measures auth; the evidence below is what the
      # probe really saw, so the reader can classify it themselves.
      echo "    unavailable_cause: \"UNKNOWN-PROVIDER-CALL-FAILURE -- CLI reachable ($(cli_invoke "$fam")); every model challenge failed. NOT a statement about authentication: no auth evidence was collected. Consistent with PATH-at-exec, network/proxy, provider outage, config, sandbox denial, or a retired model id.\""
    fi
    echo "    challenge_evidence:   # sanitized structural evidence; no credentials are read or stored"
    for e in "$WORK"/e.$fam.*; do
      [ -e "$e" ] || continue
      IFS='|' read -r efam enick eid erc ebytes efirst < "$e"
      echo "      - model: $eid"
      echo "        rc: $erc"
      echo "        output_empty: $([ "${ebytes:-0}" -gt 0 ] 2>/dev/null && echo false || echo true)"
      echo "        output_bytes: ${ebytes:-0}"
      echo "        first_line_redacted: \"$efirst\""
    done
  fi
  echo "    models:"
  printf '%s' "$lines"
}

{
  echo "# Derived by tools/probe-machine-inventory.sh -- every id below answered a sentinel"
  echo "# challenge on this machine. Commented ids did not; they are not dispatchable."
  echo "# Re-run after a CLI upgrade or account rotation."
  # `date -I` / `-Iseconds` is GNU-only: BSD/macOS date rejects it, which emitted an EMPTY
  # YAML value plus "date: illegal option -- I" into the inventory stream.
  echo "generated_at: $(date -u +%FT%TZ)"
  echo "probed_under: $(derive_identity)"
  echo "host_cores: ${NUMBER_OF_PROCESSORS:-$(nproc 2>/dev/null || echo unknown)}"
  echo "agents_max: $(( ${NUMBER_OF_PROCESSORS:-4} / 2 ))"
  echo "timeout_impl: $(run_timeout_impl)"
  echo "# Process-local repairs applied before probing. Each is an argv substitution for the"
  echo "# child process only: nothing on this machine was modified, and a re-run re-derives them."
  echo "repairs:"
  for fam in claude codex; do
    echo "  - family: $fam"
    echo "    fault: $(cli_fault "$fam")"
    echo "    repair: $(cli_repair "$fam")"
    echo "    verified: $(cli_verified "$fam")"
    echo "    invocation: \"$(cli_invoke "$fam")\""
    echo "    version: \"$(cli_version "$fam")\""
    c=$(cli_cause "$fam"); [ -n "$c" ] && echo "    cause: \"$c\""
  done
  echo "providers:"
  echo "  claude:"
  echo "    cli_path: \"$(cli_invoke claude)\""
  # F3: the old value named tools/check-cli-auth.py, which does not exist in this repository.
  # A probe field that points at a missing file is worse than an empty one -- it reads as a
  # runnable check right up until someone runs it.
  echo "    auth_probe: \"python tools/check-account-parity.py\""
  echo "    invoke: \"<cli_path> -p --model <id> --permission-mode plan --add-dir <repo> < <prompt-file>\""
  emit_family claude
  echo "  codex:"
  echo "    cli_path: \"$(cli_invoke codex)\""
  # `codex login status` is read-only but owner-gated on some hosts, so it is named as the
  # provider's own check while the portable structural probe is the one this repo ships.
  echo "    auth_probe: \"codex login status   # read-only, owner-gated on some hosts; structural alternative: tools/probe-machine-inventory.sh --dry-run\""
  echo "    invoke: \"<cli_path> exec -m <id> -s read-only -C <repo> -o <out> - < <prompt-file>\""
  emit_family codex
} > "$WORK/inventory.yaml"

echo "--- derived ---"
cat "$WORK/inventory.yaml"

# Refuse to write an inventory in which nothing verified. On a box where the shell lacks
# `timeout`, or the CLIs are absent, or auth is dead, every probe fails the same way a
# genuinely-unavailable model does -- and an all-false inventory written from that state is
# indistinguishable from an honest one. Fail loudly instead; a missing file is a better
# signal than a confident empty one.
if ! grep -qE '^      [a-z0-9]+: [a-z0-9.-]+$' "$WORK/inventory.yaml"; then
  echo "--- REFUSING TO WRITE: zero models verified ---" >&2
  for fam in claude codex; do
    if [ "$(cli_verified "$fam")" != yes ]; then
      echo "    $fam: PATH-FAULT -- no working CLI: fault=$(cli_fault "$fam") repair=$(cli_repair "$fam") verified=no" >&2
      echo "           $(cli_cause "$fam")" >&2
      echo "           NEXT: fix the launcher. This is not an account problem and re-authenticating cannot help." >&2
    else
      echo "    $fam: UNKNOWN-PROVIDER-CALL-FAILURE -- CLI resolved ($(cli_invoke "$fam") -- $(cli_version "$fam"))," >&2
      echo "           every model challenge failed. NOTHING HERE MEASURED AUTH." >&2
      echo "           NEXT, in this order: (1) re-run this probe -- a transient provider or network" >&2
      echo "           failure looks identical; (2) THEN a READ-ONLY auth check" >&2
      echo "           (\`codex login status\` where it is not owner-gated, \`python tools/check-account-parity.py\`);" >&2
      echo "           (3) THEN capacity/quota. Per-probe rc, byte counts and redacted first lines are in" >&2
      echo "           the challenge_evidence block of the derived YAML printed above." >&2
    fi
  done
  # The classes, stated once so nobody re-derives them from the prose:
  #   PATH fault                        -> the CLI never ran. Repair the launcher.
  #   CLI-resolved-but-challenge-failed -> UNKNOWN-PROVIDER-CALL-FAILURE. Re-probe, then
  #                                        read-only auth, then capacity. Never assert "auth".
  #   verified                          -> the model answered the sentinel. Dispatchable.
  echo "    Also confirm this shell can bound a process (timeout impl here: $(run_timeout_impl))." >&2
  exit 3
fi

if [ "$DRY" = 1 ]; then
  echo "--- dry run: $DEST not written ---"
else
  mkdir -p "$(dirname "$DEST")"
  cp "$WORK/inventory.yaml" "$DEST"
  echo "--- wrote $DEST ---"
fi
