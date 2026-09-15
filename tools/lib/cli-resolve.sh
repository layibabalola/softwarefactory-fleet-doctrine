#!/usr/bin/env bash
# Sourced helper. Resolve a WORKING invocation for a provider CLI family, repair the
# recoverable PATH/shim faults, and RECORD what was repaired. Nothing here mutates the
# machine: every repair is a different argv for the child process, so it is reversible by
# construction and invisible to the next run.
#
#   . "<repo>/tools/lib/cli-resolve.sh"
#   cli_resolve codex          # -> 0 if a VERIFIED invocation exists, 1 otherwise
#   cli_timed codex 180 exec -m "$id" ...    # run it, bounded
#   cli_repair_line codex      # -> CLI_REPAIR family=codex fault=... repair=... verified=...
#
# WHY THIS EXISTS (measured on host VIRTUAL-TEN, Windows 10 / Git Bash, 2026-09-14):
# %APPDATA%\npm\codex is the stock npm Git-Bash shim. It execs "$basedir/node" when that
# file is executable. On this box "$basedir/node" is itself a 200-byte shim that execs
# node_modules/node/bin/node -- a 34-byte text file reading "This file intentionally left
# blank" (a stale npm `node` package). So every `codex` call from bash exits 127 with
# "This: command not found", which probe-machine-inventory.sh recorded as
# `codex: available: false` -- an auth/capability-shaped symptom with a PATH cause.
# claude's shim execs a native .exe and is immune. `node` itself, on PATH, is fine.
#
# THE RULE THIS FILE MUST NOT BREAK: a repair that does not VERIFY is not a repair. Every
# fallback is re-probed with `--version` before it is returned, and a family that cannot be
# made to answer is reported UNAVAILABLE WITH ITS CAUSE -- never silently downgraded and
# never converted into a success.
#
# Portability: POSIX-ish bash, safe under `set -u`, bash 3.2 (macOS) clean -- no
# associative arrays, no `mapfile`, no `${x,,}`, no `command -v -a`.

# ---------------------------------------------------------------- state (set -u safe)
# CLI_ARGC_* shadows the array length on purpose. `${#arr[@]}` on an array declared empty is
# an unbound-variable error under `set -u` in bash < 4.4 -- which includes the bash 3.2 on
# macOS this file claims to support -- so the length is never read from the array itself.
CLI_ARGV_CLAUDE=()   ; CLI_ARGV_CODEX=()
CLI_ARGC_CLAUDE=0    ; CLI_ARGC_CODEX=0
CLI_FAULT_CLAUDE=""  ; CLI_FAULT_CODEX=""
CLI_REPAIR_CLAUDE="" ; CLI_REPAIR_CODEX=""
CLI_VERIFIED_CLAUDE=""; CLI_VERIFIED_CODEX=""
CLI_VERSION_CLAUDE=""; CLI_VERSION_CODEX=""
CLI_INVOKE_CLAUDE="" ; CLI_INVOKE_CODEX=""
CLI_CAUSE_CLAUDE=""  ; CLI_CAUSE_CODEX=""
CLI_REPAIR_LINES=""
CLI_PROBE_SECS="${CLI_PROBE_SECS:-45}"
_CLI_PROBE_OUT=""     # the line that looks most like a version
_CLI_PROBE_ALL=""     # everything the probe printed, stdout then stderr (identity evidence)

_cli_tmpdir() { printf '%s' "${TMPDIR:-/tmp}"; }

# ---------------------------------------------------------------- python discovery
# ONE implementation, used by run.sh, probe-machine-inventory.sh and anything else that needs
# an interpreter. `command -v python3` is not enough on Windows: the Store's `python3` stub is
# on PATH by default, answers `command -v`, and exits 9009 without ever being python -- which
# read downstream as "review_posture.py ids exited nonzero" on a box where python works fine.
# So each candidate is EXECUTED before it is returned.
cli_python() {
  local c
  if [ -n "${RP_PYTHON:-}" ]; then
    "$RP_PYTHON" -c 'import sys' >/dev/null 2>&1 && { printf '%s\n' "$RP_PYTHON"; return 0; }
    echo "cli_python: RP_PYTHON='$RP_PYTHON' is not a runnable python" >&2
    return 1
  fi
  for c in python3 python py; do
    command -v "$c" >/dev/null 2>&1 || continue
    "$c" -c 'import sys' >/dev/null 2>&1 && { printf '%s\n' "$c"; return 0; }
  done
  return 1
}

# ---------------------------------------------------------------- run_timeout
# A bounded run is not optional: an unbounded provider call is how a stage hangs forever and
# a lane is later scored as "did not run" for the wrong reason. `timeout` is GNU; macOS ships
# it as `gtimeout` only if coreutils is installed; some minimal images have neither. Detect,
# do not assume -- and if nothing here can bound a process, say so and refuse rather than
# running unbounded.
RUN_TIMEOUT_IMPL=""
if command -v timeout >/dev/null 2>&1; then RUN_TIMEOUT_IMPL="timeout"
elif command -v gtimeout >/dev/null 2>&1; then RUN_TIMEOUT_IMPL="gtimeout"
elif command -v sleep >/dev/null 2>&1; then RUN_TIMEOUT_IMPL="bash-watchdog"
else RUN_TIMEOUT_IMPL="none"; fi

run_timeout_impl() { printf '%s\n' "$RUN_TIMEOUT_IMPL"; }

# 0 if this shell can bound a process at all. Callers that must never run unbounded check
# this once, loudly, before probing anything.
run_timeout_selftest() {
  if [ "$RUN_TIMEOUT_IMPL" = "none" ]; then
    echo "FATAL: no way to bound a process (no timeout, no gtimeout, no sleep). Refusing to run unbounded." >&2
    return 1
  fi
  return 0
}

_rt_watchdog() {  # secs cmd...   -- returns 124 on timeout, like GNU timeout
  local secs="$1"; shift
  local marker pid wd rc
  marker="$(_cli_tmpdir)/rt.$$.${RANDOM:-0}.kill"
  rm -f "$marker"
  "$@" &
  pid=$!
  (
    sleep "$secs"
    if kill -0 "$pid" 2>/dev/null; then
      : > "$marker"
      kill -TERM "$pid" 2>/dev/null
      sleep 2
      kill -KILL "$pid" 2>/dev/null
    fi
  ) >/dev/null 2>&1 &
  wd=$!
  rc=0
  wait "$pid" 2>/dev/null || rc=$?
  kill "$wd" >/dev/null 2>&1
  wait "$wd" 2>/dev/null || :
  if [ -f "$marker" ]; then rm -f "$marker"; return 124; fi
  return "$rc"
}

run_timeout() {  # secs cmd...
  local secs="$1"; shift
  case "$RUN_TIMEOUT_IMPL" in
    timeout|gtimeout) "$RUN_TIMEOUT_IMPL" "$secs" "$@" ;;
    bash-watchdog)    _rt_watchdog "$secs" "$@" ;;
    *) echo "run_timeout: FATAL: this shell cannot bound a process; refusing to run: $*" >&2; return 125 ;;
  esac
}

# ---------------------------------------------------------------- file-shape probes
_cli_starts_with() {  # path literal-prefix
  [ -f "$1" ] || return 1
  local got
  got=$(head -c "${#2}" "$1" 2>/dev/null | tr -d '\000')
  [ "$got" = "$2" ]
}

# A real executable image, not a text file wearing the +x bit.
_cli_is_native() {  # path
  [ -f "$1" ] || return 1
  _cli_starts_with "$1" 'MZ' && return 0                      # PE / .exe
  local b
  b=$(od -An -tx1 -N4 "$1" 2>/dev/null | tr -d ' \n')
  case "$b" in
    7f454c46) return 0 ;;                                     # ELF
    feedface|cefaedfe|feedfacf|cffaedfe|cafebabe|bebafeca) return 0 ;;  # Mach-O / fat
  esac
  return 1
}

_cli_has_shebang() { _cli_starts_with "$1" '#!'; }

# Follow an npm-style shim's `exec "$basedir/<x>"` chain and report whether it terminates in
# something that cannot be executed. This is the STRUCTURAL detector for F1: it fires on the
# file shapes, before and independently of any exit code, so it also catches the variant
# where the broken interpreter produces a rc other than 126/127.
# Returns 0 (= broken) and prints the offending path; 1 otherwise.
_cli_shim_interp_broken() {  # shim-path
  local p="$1" depth=0 basedir target
  while [ "$depth" -lt 6 ]; do
    if _cli_is_native "$p"; then return 1; fi
    if ! _cli_has_shebang "$p"; then
      # A text file with no shebang at the END OF AN EXEC CHAIN: the shell will try to run its
      # first word as a command. This is exactly the stale npm `node` placeholder.
      # depth 0 is NOT that fault. The entry point itself having no shebang is an ordinary
      # POSIX wrapper -- the shell runs it as a script, and plenty of healthy installs ship
      # one. Calling that "shim-interpreter-not-executable" labelled a working CLI as faulted.
      [ "$depth" -gt 0 ] || return 1
      printf '%s\n' "$p"; return 0
    fi
    basedir=$(dirname "$p")
    target=$(sed -n 's|.*exec[[:space:]][[:space:]]*"\$basedir/\([^"]*\)".*|\1|p' "$p" 2>/dev/null | head -1)
    [ -n "$target" ] || return 1          # not a $basedir-chaining shim; not this fault
    [ -e "$basedir/$target" ] || return 1 # shim falls through to PATH lookup; not this fault
    p="$basedir/$target"
    depth=$((depth + 1))
  done
  return 1
}

# ---------------------------------------------------------------- version probe
# Verification criterion, deliberately structural: the exit code. rc 0 means the invocation
# EXISTS AND RAN, which is the only thing --version can honestly establish. What it printed is
# reported, never required: a CLI that answers rc 0 in silence is a healthy CLI, and treating
# an empty banner as "unresolved" refused an entire working family.
#
# stdout and stderr are captured SEPARATELY. Merged with 2>&1, a node deprecation warning on
# stderr raced ahead of the real answer and was recorded as the CLI's version.
_cli_first_nonblank() { sed -n '/[^[:space:]]/{p;q;}' "$1" 2>/dev/null; }

# A line that carries a dotted number is a version line; anything else is a banner or a
# warning. Prefer the first such line, on stdout, before falling back to prose.
_cli_version_line() {  # file
  sed -n 's/[[:space:]]*$//; /[0-9][0-9]*\.[0-9]/{p;q;}' "$1" 2>/dev/null
}

_cli_probe_version() {  # argv...
  local tmp rc
  tmp="$(_cli_tmpdir)/cliprobe.$$.${RANDOM:-0}"
  run_timeout "$CLI_PROBE_SECS" "$@" >"$tmp.out" 2>"$tmp.err"
  rc=$?
  tr -d '\r' < "$tmp.out" > "$tmp.o" 2>/dev/null || : > "$tmp.o"
  tr -d '\r' < "$tmp.err" > "$tmp.e" 2>/dev/null || : > "$tmp.e"
  _CLI_PROBE_OUT=$(_cli_version_line "$tmp.o")
  [ -n "$_CLI_PROBE_OUT" ] || _CLI_PROBE_OUT=$(_cli_version_line "$tmp.e")
  [ -n "$_CLI_PROBE_OUT" ] || _CLI_PROBE_OUT=$(_cli_first_nonblank "$tmp.o")
  [ -n "$_CLI_PROBE_OUT" ] || _CLI_PROBE_OUT=$(_cli_first_nonblank "$tmp.e")
  _CLI_PROBE_ALL=$(cat "$tmp.o" "$tmp.e" 2>/dev/null)
  rm -f "$tmp.out" "$tmp.err" "$tmp.o" "$tmp.e"
  return "$rc"
}

# Preserves the REAL rc. `|| return 1` flattened 126/127 -- the PATH signature this whole file
# exists to name -- into a generic rc1 on every host without the $basedir chain.
_cli_verify() {  # argv...  -> 0 and sets _CLI_PROBE_OUT/_CLI_PROBE_ALL when the invocation answers
  local rc=0
  _cli_probe_version "$@" || rc=$?
  return "$rc"
}

# ---------------------------------------------------------------- identity of a FALLBACK rung
# A fallback rung is something we went looking for; the on-PATH incumbent is something the
# operator installed. Measured 2026-09-14 (fleet doctrine bus, host VIRTUAL-TEN): with the
# broken npm shim first on PATH and a copy of GNU `echo` named `codex.exe` second, the native
# rung verified on "rc 0 plus any non-empty line" and the run went on to report
# `codex: CLI OK (... echo (GNU coreutils) 8.32); every model challenge failed` plus
# `Check: auth` -- a PATH fault presented as an auth verdict, the exact inverse of F1.
#
# The cheapest sound check is the family's own name in its own --version output: it costs the
# probe we already ran, needs no account, no network and no tokens, and an impostor that
# happens to print "codex" while not being codex is a far stranger machine than one that has a
# stray binary of the right name on PATH. A model challenge (the INVENTORY-OK sentinel) is
# strictly stronger but belongs in probe-machine-inventory.sh, which already does it per model
# and would otherwise spend an account round-trip inside a resolver that must work offline.
_cli_identity_ok() {  # family
  local hay
  hay=$(printf '%s' "$_CLI_PROBE_ALL" | tr 'A-Z' 'a-z')   # bash 3.2: no ${x,,}
  case "$hay" in *"$1"*) return 0 ;; esac
  return 1
}

# ---------------------------------------------------------------- node / npm-root discovery
# CLI_NODE is an operator PIN: when set it is the only interpreter considered, so a host with
# several nodes can be made deterministic (and a pinned-but-broken node reports as broken
# rather than being papered over by a different one found later on PATH).
_cli_working_node() {
  local c
  if [ -n "${CLI_NODE:-}" ]; then
    _cli_verify "$CLI_NODE" --version && { printf '%s\n' "$CLI_NODE"; return 0; }
    return 1
  fi
  for c in node "/c/Program Files/nodejs/node" "/c/Program Files/nodejs/node.exe" \
           "/usr/local/bin/node" "/opt/homebrew/bin/node" "/usr/bin/node"; do
    command -v "$c" >/dev/null 2>&1 || [ -x "$c" ] || continue
    if _cli_verify "$c" --version; then printf '%s\n' "$c"; return 0; fi
  done
  return 1
}

_cli_winpath() {  # normalise a Windows path npm may print with backslashes
  printf '%s\n' "$1" | tr -d '\r' | tr '\\' '/'
}

# Candidate global node_modules roots, most authoritative first. `npm root -g` is correct but
# slow, sometimes a .cmd bash cannot run, and absent on a native-binary install -- so it is
# one candidate among several, never the only one.
_cli_npm_roots() {
  local r shimdir nodedir c
  r=$(run_timeout 25 npm root -g 2>/dev/null | sed -n '/[^[:space:]]/{p;q;}')
  [ -n "$r" ] && _cli_winpath "$r"
  for c in codex claude; do
    shimdir=$(command -v "$c" 2>/dev/null) || continue
    [ -n "$shimdir" ] && printf '%s\n' "$(dirname "$shimdir")/node_modules"
  done
  nodedir=$(command -v node 2>/dev/null) && [ -n "$nodedir" ] && {
    printf '%s\n' "$(dirname "$nodedir")/node_modules"
    printf '%s\n' "$(dirname "$nodedir")/../lib/node_modules"
  }
  [ -n "${APPDATA:-}" ] && printf '%s\n' "$(_cli_winpath "$APPDATA")/npm/node_modules"
  printf '%s\n' "${HOME:-/nonexistent}/.npm-global/lib/node_modules"
  printf '%s\n' "/usr/local/lib/node_modules"
  printf '%s\n' "/opt/homebrew/lib/node_modules"
  printf '%s\n' "/usr/lib/node_modules"
}

_cli_js_entrypoints() {  # family -> relative paths under a global node_modules root
  case "$1" in
    codex)  printf '%s\n' "@openai/codex/bin/codex.js" ;;
    claude) printf '%s\n' "@anthropic-ai/claude-code/cli.js" "@anthropic-ai/claude-code/bin/claude.js" ;;
  esac
}

# Native binaries the family may also be installed as, plus a PATH sweep (there may be a
# working second `codex` later in PATH, behind the broken shim).
_cli_native_candidates() {  # family
  local fam="$1" d IFS_SAVE
  printf '%s\n' "${HOME:-/nonexistent}/.$fam/bin/$fam" \
                "/opt/homebrew/bin/$fam" "/usr/local/bin/$fam" "/usr/bin/$fam" \
                "${HOME:-/nonexistent}/.local/bin/$fam"
  IFS_SAVE="$IFS"; IFS=:
  for d in $PATH; do
    [ -n "$d" ] || continue
    printf '%s\n' "$d/$fam" "$d/$fam.exe"
  done
  IFS="$IFS_SAVE"
}

# ---------------------------------------------------------------- per-family setters
# No `eval` and no associative arrays: a case dispatch keeps argv an ARRAY, which is the only
# way a path containing a space survives (the whole point of this exercise).
_cli_store() {  # family fault repair verified version invoke argv...
  local fam="$1" fault="$2" repair="$3" verified="$4" version="$5" invoke="$6"; shift 6
  case "$fam" in
    claude) CLI_ARGV_CLAUDE=("$@"); CLI_ARGC_CLAUDE=$#; CLI_FAULT_CLAUDE="$fault"; CLI_REPAIR_CLAUDE="$repair"
            CLI_VERIFIED_CLAUDE="$verified"; CLI_VERSION_CLAUDE="$version"; CLI_INVOKE_CLAUDE="$invoke"
            CLI_DONE_CLAUDE=1 ;;
    codex)  CLI_ARGV_CODEX=("$@");  CLI_ARGC_CODEX=$#;  CLI_FAULT_CODEX="$fault";  CLI_REPAIR_CODEX="$repair"
            CLI_VERIFIED_CODEX="$verified"; CLI_VERSION_CODEX="$version"; CLI_INVOKE_CODEX="$invoke"
            CLI_DONE_CODEX=1 ;;
  esac
}

_cli_set_cause() {
  case "$1" in claude) CLI_CAUSE_CLAUDE="$2" ;; codex) CLI_CAUSE_CODEX="$2" ;; esac
}

cli_fault()    { case "$1" in claude) printf '%s\n' "${CLI_FAULT_CLAUDE:-unknown}";; codex) printf '%s\n' "${CLI_FAULT_CODEX:-unknown}";; esac; }
cli_repair()   { case "$1" in claude) printf '%s\n' "${CLI_REPAIR_CLAUDE:-none}";;  codex) printf '%s\n' "${CLI_REPAIR_CODEX:-none}";;  esac; }
cli_verified() { case "$1" in claude) printf '%s\n' "${CLI_VERIFIED_CLAUDE:-no}";;  codex) printf '%s\n' "${CLI_VERIFIED_CODEX:-no}";;  esac; }
cli_version()  { case "$1" in claude) printf '%s\n' "${CLI_VERSION_CLAUDE:-}";;     codex) printf '%s\n' "${CLI_VERSION_CODEX:-}";;     esac; }
cli_invoke()   { case "$1" in claude) printf '%s\n' "${CLI_INVOKE_CLAUDE:-}";;      codex) printf '%s\n' "${CLI_INVOKE_CODEX:-}";;      esac; }
cli_cause()    { case "$1" in claude) printf '%s\n' "${CLI_CAUSE_CLAUDE:-}";;       codex) printf '%s\n' "${CLI_CAUSE_CODEX:-}";;       esac; }

# A family this run will not dispatch is NOT an unavailable family. Recording it as `no` would
# publish a verdict nothing measured -- the same class of error as calling the plan the
# dispatch record. No argv is stored, so `cli_timed` still refuses it.
cli_mark_not_probed() {  # family
  case "$1" in claude|codex) ;; *) return 2 ;; esac
  _cli_store "$1" not-probed not-probed no "" ""
  _cli_set_cause "$1" "not probed: this run has no pending lane in family $1"
  CLI_REPAIR_LINES="${CLI_REPAIR_LINES}$(cli_repair_line "$1")"$'\n'
}

cli_repair_line() {  # family
  printf 'CLI_REPAIR family=%s fault=%s repair=%s verified=%s\n' \
    "$1" "$(cli_fault "$1")" "$(cli_repair "$1")" "$(cli_verified "$1")"
}

# ---------------------------------------------------------------- resolve
# Returns 0 iff the family ends up with a VERIFIED invocation.
cli_resolve() {  # family
  local fam="$1"
  case "$fam" in claude|codex) ;; *) echo "cli_resolve: unknown family $fam" >&2; return 2 ;; esac

  # Resolve once per process. `cli_verified` defaults to "no", so the done-flag has to be a
  # separate variable -- reading the accessor here made every first call look already-resolved.
  case "$fam" in
    claude) [ -n "${CLI_DONE_CLAUDE:-}" ] && { [ "$CLI_VERIFIED_CLAUDE" = yes ]; return $?; } ;;
    codex)  [ -n "${CLI_DONE_CODEX:-}" ]  && { [ "$CLI_VERIFIED_CODEX" = yes ];  return $?; } ;;
  esac

  if ! run_timeout_selftest; then
    _cli_store "$fam" no-process-bound unresolved no "" "$fam"   # no argv: an unresolved family must not be runnable
    _cli_set_cause "$fam" "this shell cannot bound a process (no timeout/gtimeout/sleep)"
    CLI_REPAIR_LINES="${CLI_REPAIR_LINES}$(cli_repair_line "$fam")"$'\n'
    return 1
  fi

  local onpath fault="" rc=0 broken=""
  onpath=$(command -v "$fam" 2>/dev/null || true)

  if [ -z "$onpath" ]; then
    fault="not-on-path"
  else
    # Structural check FIRST: the shape of the exec chain does not depend on an exit code.
    broken=$(_cli_shim_interp_broken "$onpath" || true)
    # fault is a short CODE (it is a field in a machine-read line); the offending path goes
    # into the cause, which is prose.
    [ -n "$broken" ] && fault="shim-interpreter-not-executable"
    rc=0; _cli_verify "$onpath" --version || rc=$?
    if [ "$rc" -eq 0 ]; then
      # It answers. A measurement outranks a shape heuristic, and it outranks it COMPLETELY:
      # a hop is only "broken" if it is also not runnable, so a healthy install is recorded
      # fault=none even when its wrapper looked odd.
      [ -n "$_CLI_PROBE_OUT" ] || echo "CLI_WARN family=$fam: '$onpath' --version exited 0 but printed nothing; treating rc 0 as healthy and recording an empty version" >&2
      _cli_store "$fam" "none" "none-needed" yes "$_CLI_PROBE_OUT" "$onpath" "$onpath"
      CLI_REPAIR_LINES="${CLI_REPAIR_LINES}$(cli_repair_line "$fam")"$'\n'
      return 0
    fi
    [ -n "$fault" ] || fault="rc$rc"
  fi

  # ---- bounded repair ladder. Every rung is VERIFIED with --version before it is accepted.
  # Candidate lists are read line-by-line, never word-split: a global node_modules root under
  # "C:/Program Files/..." is exactly the input that broke the caller in the first place.
  local node root ep cand impostor=""
  node=$(_cli_working_node || true)
  if [ -n "$node" ]; then
    while IFS= read -r root; do
      [ -n "$root" ] && [ -d "$root" ] || continue
      while IFS= read -r ep; do
        [ -n "$ep" ] && [ -f "$root/$ep" ] || continue
        # Identity is proven by the ENTRYPOINT PATH here: `@openai/codex/bin/codex.js` and
        # `@anthropic-ai/claude-code/cli.js` are the family's own published package paths, not
        # a bare basename anyone can occupy. The banner check is kept as a second signal but
        # is not required -- an entrypoint that answers rc 0 from its own package is the CLI.
        if _cli_verify "$node" "$root/$ep" --version; then
          _cli_store "$fam" "$fault" "node-js-entrypoint" yes "$_CLI_PROBE_OUT" "$node $root/$ep" "$node" "$root/$ep"
          CLI_REPAIR_LINES="${CLI_REPAIR_LINES}$(cli_repair_line "$fam")"$'\n'
          return 0
        fi
      done <<EOF
$(_cli_js_entrypoints "$fam")
EOF
    done <<EOF
$(_cli_npm_roots)
EOF
  fi

  while IFS= read -r cand; do
    [ -n "$cand" ] && [ -f "$cand" ] || continue
    [ "$cand" = "$onpath" ] && continue
    _cli_is_native "$cand" || continue
    if _cli_verify "$cand" --version; then
      # A basename on PATH is not an identity. Require the family to name itself.
      if ! _cli_identity_ok "$fam"; then
        impostor="${impostor}${impostor:+; }$cand printed [$_CLI_PROBE_OUT], which does not name '$fam'"
        echo "CLI_REJECTED family=$fam rung=native-binary candidate=$cand reason=identity-unproven version=[$_CLI_PROBE_OUT]" >&2
        continue
      fi
      _cli_store "$fam" "$fault" "native-binary" yes "$_CLI_PROBE_OUT" "$cand" "$cand"
      CLI_REPAIR_LINES="${CLI_REPAIR_LINES}$(cli_repair_line "$fam")"$'\n'
      return 0
    fi
  done <<EOF
$(_cli_native_candidates "$fam")
EOF

  # .cmd shims only if THIS bash can actually execute one -- on many Git Bash installs it
  # cannot, and accepting one unverified is exactly the silent downgrade this file forbids.
  while IFS= read -r cand; do
    [ -n "$cand" ] && [ -f "$cand.cmd" ] || continue
    if _cli_verify "$cand.cmd" --version; then
      if ! _cli_identity_ok "$fam"; then
        impostor="${impostor}${impostor:+; }$cand.cmd printed [$_CLI_PROBE_OUT], which does not name '$fam'"
        echo "CLI_REJECTED family=$fam rung=cmd-shim candidate=$cand.cmd reason=identity-unproven version=[$_CLI_PROBE_OUT]" >&2
        continue
      fi
      _cli_store "$fam" "$fault" "cmd-shim" yes "$_CLI_PROBE_OUT" "$cand.cmd" "$cand.cmd"
      CLI_REPAIR_LINES="${CLI_REPAIR_LINES}$(cli_repair_line "$fam")"$'\n'
      return 0
    fi
  done <<EOF
$(_cli_native_candidates "$fam")
EOF

  # Nothing verified. Fail loudly, with the cause, and do NOT hand back a hopeful argv.
  local cause="$fault"
  case "$fault" in
    not-on-path) cause="$fault; no '$fam' on PATH and no native/npm fallback answered --version" ;;
    shim-interpreter-not-executable)
      cause="$fault; '$onpath' execs an interpreter chain ending at '$broken', which is not an executable image" ;;
    *) cause="$fault from '$onpath'" ;;
  esac
  [ -n "$node" ] || cause="$cause; no working node on this host, so the js-entrypoint repair was not available"
  [ -n "$impostor" ] && cause="$cause; a fallback candidate answered but could not be shown to BE $fam and was rejected ($impostor)"
  _cli_store "$fam" "$fault" "unresolved" no "" "$fam"   # no argv: cli_timed refuses rather than running something hopeful
  _cli_set_cause "$fam" "$cause"
  CLI_REPAIR_LINES="${CLI_REPAIR_LINES}$(cli_repair_line "$fam")"$'\n'
  echo "CLI_UNAVAILABLE family=$fam cause=$cause" >&2
  return 1
}

# ---------------------------------------------------------------- invocation seam
# The ONLY sanctioned way to call a provider CLI. Expands the resolved argv as an array so a
# space in any path survives, and hands a real executable to run_timeout (which may be the
# external `timeout`, and so cannot run a shell function).
cli_timed() {  # family secs args...
  local fam="$1" secs="$2"; shift 2
  case "$fam" in
    claude)
      [ "${CLI_ARGC_CLAUDE:-0}" -gt 0 ] || { echo "cli_timed: claude unresolved (call cli_resolve first)" >&2; return 125; }
      run_timeout "$secs" "${CLI_ARGV_CLAUDE[@]}" "$@" ;;
    codex)
      [ "${CLI_ARGC_CODEX:-0}" -gt 0 ] || { echo "cli_timed: codex unresolved (call cli_resolve first)" >&2; return 125; }
      run_timeout "$secs" "${CLI_ARGV_CODEX[@]}" "$@" ;;
    *) echo "cli_timed: unknown family $fam" >&2; return 2 ;;
  esac
}

cli_repairs_log() { printf '%s' "${CLI_REPAIR_LINES:-}"; }
