#!/usr/bin/env bash
# Full Conjugal-standard review posture, stages A-D, in ONE invocation (see README.md here).
#
#   RP_OUT=<abs out dir> RP_SUBJECT=<abs subject file> RP_BENCH=<abs test bench> RP_REPO=<abs subject repo> \
#     bash tools/review-posture/run.sh [--from B|C|D] [--dry-run]
#
# --dry-run   generate and binding-check every prompt it can, dispatch nothing. A dry run
#             prints `posture: NOT-MEASURED (dry-run)` and exits 0 when the binding checks
#             pass: R9 says a posture is a MEASUREMENT, and a run that deliberately dispatched
#             nothing has not measured one. It exits non-zero only on a real binding failure.
# --from X    reuse earlier stages already in RP_OUT (only if subject blob and bench HEAD are unchanged -- say so in the filing).
# --retry-missing  within each stage run, re-dispatch only lanes that have not cleared LANE-COMPLETE (e.g. one arbiter that
#             degenerated) instead of re-running every seat. Disclose retries in the filing.
# The final lines are the posture measurement; exit 1 if the posture is PARTIAL.
set -u
set -o pipefail   # a command substitution that dies mid-pipe must not read as success (see `ids`, below)

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$HERE/../.." && pwd)"
. "$REPO_ROOT/tools/lib/cli-resolve.sh"

# F2: `PY="python $HERE/review_posture.py"` was a STRING, expanded unquoted. From a path
# containing a space ("C:/!Layi Wkspc/...") python received only the fragment before the
# space and every $PY call died. `eval "$($PY ids)"` then succeeded anyway -- `eval ""` is
# exit 0 -- so the run proceeded with no model ids at all. A function keeps the argv intact.
# Discovery lives in cli-resolve.sh (cli_python) and EXECUTES each candidate: a Windows Store
# `python3` stub answers `command -v` and exits 9009.
PYTHON="$(cli_python)" || { echo "no runnable python3/python on PATH -- refuse"; exit 2; }
py() { "$PYTHON" "$HERE/review_posture.py" "$@"; }

: "${RP_OUT:?}" "${RP_SUBJECT:?}" "${RP_BENCH:?}" "${RP_REPO:?}"
FROM=A; DRY=0; RETRY=0
while [ $# -gt 0 ]; do case "$1" in --from) FROM=$2; shift 2;; --dry-run) DRY=1; shift;; --retry-missing) RETRY=1; shift;; *) echo "unknown arg $1"; exit 2;; esac; done
# NOTE: RP_* are exported further down, AFTER the path-dialect normalisation below. Exporting
# them here (as the pre-merge upstream did) would publish the un-normalised values to the
# python half, which is the F2/path-dialect fault this file exists to close.

# A Windows host can resolve `bash` to WSL's, which sees neither this CLI nor these paths.
# `System32\bash.exe` is only ONE of the launchers. The Store/App-Execution-Alias copy lives at
# %LOCALAPPDATA%\Microsoft\WindowsApps\bash.exe and is on PATH by default on Windows 10/11 --
# this repo's own test suite documents it (tests/test-selfheal.sh, the I1 PATH-ordering note),
# and it slipped past a System32-only pattern. `wsl.exe`/`wsl` resolving as `bash` is the same
# launcher wearing a third name. All three are refused: this guard exists so a WSL detour
# cannot quietly produce a posture nobody can reproduce.
wsl_bash_path() {  # -> the offending path, or empty
  local b; b="$(command -v bash 2>/dev/null || true)"
  case "$b" in
    */[Ww]indows/[Ss]ystem32/*) printf '%s\n' "$b" ;;
    */[Ww]indows[Aa]pps/*)      printf '%s\n' "$b" ;;
    */wsl.exe|*/wsl)            printf '%s\n' "$b" ;;
    *) : ;;
  esac
}
WSLBASH="$(wsl_bash_path)"
[ -z "$WSLBASH" ] || { echo "WSL bash on PATH -- refuse: $WSLBASH (WSL sees neither these paths nor these CLIs; use Git Bash)"; exit 2; }

# ---------------------------------------------------------------- paths: absolute, and in ONE dialect
#
# TWO distinct faults, both measured on the fleet doctrine bus, host VIRTUAL-TEN, 2026-09-14.
#
# (1) RELATIVE paths. `claude_lane` runs `cd "$RP_REPO" && ... < "$RP_OUT/x.prompt"`; the
#     redirections resolve AFTER the cd, so a relative RP_OUT made every claude lane
#     DID-NOT-RUN while every codex lane RAN (codex uses `--cd`, not `cd`). A silent
#     cross-FAMILY bias that survives into the posture is worse than a crash.
#
# (2) PATH DIALECT. Git Bash hands a POSIX path to a NATIVE WINDOWS python, which resolves
#     `/c/temp/x` against the current drive as `C:\c\temp\x`. MSYS silently converts such env
#     values on the way out -- but NOT when the value contains a character it declines to
#     translate (an apostrophe is enough). Measured: with RP_OUT=/c/temp/"sp ace'!d"/out5 the
#     bash half wrote environment.json into RP_OUT while python wrote all 17 prompts into
#     C:\c\temp\sp ace'!d\out5 -- outside RP_OUT, on a directory tree it created. `py prompts`
#     exited 0, all 17 lanes were dispatched onto files that were not there, and the run ended
#     `posture: PARTIAL (0/17)` with no line anywhere naming the cause.
#     So: normalise to the one dialect BOTH halves agree on (`cygpath -m` -> `C:/...`, which
#     MSYS bash also accepts) whenever python is a native Windows build. And see
#     `check_prompts` below -- normalisation is the fix, the post-condition is the proof.
abs_dir() {  # label path -> absolute, refusing rather than guessing
  local d
  d=$(cd "$2" 2>/dev/null && pwd) || { echo "$1 is not a readable directory: $2" >&2; return 1; }
  printf '%s\n' "$d"
}
abs_file() {  # label path
  local d
  d=$(cd "$(dirname "$2")" 2>/dev/null && pwd) || { echo "$1 is not in a readable directory: $2" >&2; return 1; }
  printf '%s\n' "$d/$(basename "$2")"
}

[ -f "$RP_SUBJECT" ] || { echo "SUBJECT MISSING: $RP_SUBJECT"; exit 2; }
mkdir -p "$RP_OUT" || { echo "RP_OUT is not creatable: $RP_OUT"; exit 2; }
RP_OUT="$(abs_dir RP_OUT "$RP_OUT")" || exit 2
RP_BENCH="$(abs_dir RP_BENCH "$RP_BENCH")" || exit 2
RP_REPO="$(abs_dir RP_REPO "$RP_REPO")" || exit 2
RP_SUBJECT="$(abs_file RP_SUBJECT "$RP_SUBJECT")" || exit 2

# Native-Windows python + MSYS bash: put every path python will see into the dialect python
# resolves the same way bash does. Detected, never assumed -- a Git Bash with an MSYS python
# needs no conversion and must not get one.
PATH_DIALECT=posix
case "$(uname -s 2>/dev/null || echo unknown)" in
  MINGW*|MSYS*|CYGWIN*)
    if command -v cygpath >/dev/null 2>&1 &&
       [ "$("$PYTHON" -c 'import sys;print(sys.platform)' 2>/dev/null)" = win32 ]; then
      PATH_DIALECT=windows
      n=$(cygpath -m -- "$RP_OUT" 2>/dev/null)     && [ -n "$n" ] && RP_OUT="${n%/}"
      n=$(cygpath -m -- "$RP_SUBJECT" 2>/dev/null) && [ -n "$n" ] && RP_SUBJECT="$n"
      n=$(cygpath -m -- "$RP_BENCH" 2>/dev/null)   && [ -n "$n" ] && RP_BENCH="${n%/}"
      n=$(cygpath -m -- "$RP_REPO" 2>/dev/null)    && [ -n "$n" ] && RP_REPO="${n%/}"
      # $HERE too. It is not an RP_* value, but it is handed to the SAME native python as an
      # argv path (`py`, `_stage_lanes_raw`), so it needs the same dialect. Measured
      # 2026-09-14 (V4 re-attack, host VIRTUAL-TEN): with the tooling under a path containing
      # an apostrophe, python reported `can't open file "C:\c\temp\...\review_posture.py"` and
      # the run died at `IDS FAILED`. That fails CLOSED -- no false posture -- but the tool
      # could not run at all from such a path.
      n=$(cygpath -m -- "$HERE" 2>/dev/null)       && [ -n "$n" ] && HERE="${n%/}"
      echo "PATH_DIALECT windows: native python detected; RP_* and \$HERE normalised with cygpath -m so both halves resolve them identically" >&2
    fi ;;
esac
export RP_OUT RP_SUBJECT RP_BENCH RP_REPO

REPAIRS="$RP_OUT/repairs.log"

# ---------------------------------------------------------------- model ids, FAIL CLOSED
# rc, emptiness and shape are all checked, and NOTHING is eval'd. The old form could not tell
# "no ids" from "ids fine" (the failure mode that dispatched a whole run with an empty
# --model), and `eval "$ids_out"` executed the inventory FILE: an id written
# `opus: x$(touch PWNED)y` ran that command. A model id is DATA. It is matched against a
# strict charset here and in the python emitter, and assigned by a case dispatch over the
# seven known nicknames -- no indirection, no eval, nothing to inject into.
MODEL_FABLE=""; MODEL_OPUS=""; MODEL_SONNET=""; MODEL_HAIKU=""
MODEL_ASTRA=""; MODEL_SOL=""; MODEL_LUNA=""
# `| tr -d '\r'` -- an explicit CR: a NATIVE WINDOWS python writes CRLF to stdout even when bash is MSYS, so
# every value here arrives with a trailing CR. The old `eval` swallowed it silently and would
# have dispatched `--model "claude-fable-5<CR>"` at a real provider.
ids_out="$(py ids | tr -d '\r')" || { echo "IDS FAILED: review_posture.py ids exited nonzero -- no model ids, refusing to dispatch" >&2; exit 2; }
[ -n "$ids_out" ] || { echo "IDS FAILED: review_posture.py ids produced no output (is \"$PYTHON $HERE/review_posture.py\" runnable from this path?)" >&2; exit 2; }
n_ids=0
while IFS= read -r line; do
  [ -n "$line" ] || continue
  key=${line%%=*}; val=${line#*=}
  case "$line" in MODEL_*=?*) ;; *) echo "IDS FAILED: malformed ids output line: $line" >&2; exit 2;; esac
  case "$val" in
    *[!A-Za-z0-9._-]*)
      # The token stays on STDOUT (PR #62's contract, pinned by its `MODEL ID LINE REJECTED`
      # test); the prose cause goes to stderr with the rest of this block's diagnostics.
      echo "MODEL ID LINE REJECTED: $line -- refuse"
      echo "IDS FAILED: model id for $key is not [A-Za-z0-9._-]+: '$val' -- a model id is data, not a command" >&2
      exit 2 ;;
  esac
  case "$key" in
    MODEL_FABLE)  MODEL_FABLE=$val ;;
    MODEL_OPUS)   MODEL_OPUS=$val ;;
    MODEL_SONNET) MODEL_SONNET=$val ;;
    MODEL_HAIKU)  MODEL_HAIKU=$val ;;
    MODEL_ASTRA)  MODEL_ASTRA=$val ;;
    MODEL_SOL)    MODEL_SOL=$val ;;
    MODEL_LUNA)   MODEL_LUNA=$val ;;
    *) echo "IDS FAILED: unknown nickname in ids output: $key" >&2; exit 2 ;;
  esac
  n_ids=$((n_ids + 1))
done <<EOF
$ids_out
EOF
[ "$n_ids" -gt 0 ] || { echo "IDS FAILED: no MODEL_* assignments in ids output" >&2; exit 2; }

model_for_nick() {  # nickname -> id, or empty
  case "$1" in
    fable) printf '%s\n' "$MODEL_FABLE" ;; opus)  printf '%s\n' "$MODEL_OPUS" ;;
    sonnet) printf '%s\n' "$MODEL_SONNET" ;; haiku) printf '%s\n' "$MODEL_HAIKU" ;;
    astra) printf '%s\n' "$MODEL_ASTRA" ;; sol)   printf '%s\n' "$MODEL_SOL" ;;
    luna)  printf '%s\n' "$MODEL_LUNA" ;; *) printf '%s\n' "" ;;
  esac
}

# ---------------------------------------------------------------- CLI resolution + repair log
# Resolution/repair used to happen HERE, for both families, unconditionally. It now happens in
# the pre-dispatch preflight further down, over the families this run will actually dispatch:
# `--retry-missing` recovering three Claude lanes must not be blocked -- or even slowed -- by a
# Codex launcher no lane in this run will touch (PR #62, Codex sol review round 4).
run_timeout_selftest || exit 2
: > "$REPAIRS"

stamp() { echo "$(date -u +%FT%TZ) $*"; }

# ---------------------------------------------------------------- run bindings (--from)
# `--from B|C|D` REUSES the sentinels already in RP_OUT. Until now nothing checked that those
# sentinels were produced against the SAME subject, the same bench and the same tool: the docs
# said "do that only after re-measuring", which is a request, not a control. Change the subject
# file and re-run `--from C` and the tool will happily print a COMPLETE posture over stage-A and
# stage-B lanes that reviewed the PREVIOUS document -- a manufactured measurement, which is the
# one thing this whole tool exists not to do.
#
# So every real dispatch writes what it was bound to, and `--from` refuses unless every recorded
# value still matches. There is deliberately NO override flag: an operator who has genuinely
# re-measured can re-run from A, and an operator who has not must not be able to assert they
# have. Fails CLOSED on a missing or unreadable bindings file too -- "no record" is not "match".
BINDINGS="$RP_OUT/bindings.env"
# Empty on a from-A run, which reuses nothing. Set by check_bindings on every accepted --from /
# --retry-missing, and from there it reaches stdout, environment.json AND the posture line: a
# reused posture must never read as a pristine one (round F4).
REUSE_LINE=""
blob_of() { git hash-object -- "$1" 2>/dev/null || echo unknown; }
# THREE distinct answers, and collapsing any two of them is how a binding fails open:
#   40-hex          -- measured;
#   not-a-git-tree  -- deterministic, binds NOTHING, and says so (the caller discloses it);
#   unknown         -- COULD NOT BE COMPUTED, which check_bindings treats as a refusal, never
#                      as "same as last time". A directory that is not a git tree is a known
#                      state; a `rev-parse HEAD` that failed inside one (unborn branch, broken
#                      object store) is not, and the two must not share a value.
head_of() {  # dir -> 40-hex | not-a-git-tree | unknown
  local h
  git -C "$1" rev-parse --show-toplevel >/dev/null 2>&1 || { printf '%s\n' not-a-git-tree; return; }
  h=$(git -C "$1" rev-parse HEAD 2>/dev/null) && [ -n "$h" ] || { printf '%s\n' unknown; return; }
  printf '%s\n' "$h"
}
# A HEAD is not a tree state (Codex sol, round X6 item 1). A bench with uncommitted edits to a
# tracked file, or with a brand-new untracked file the lanes read, has exactly the SAME HEAD as
# the clean tree the earlier stages were reviewed against -- so `--from C` would reuse those
# stages over different bytes and still print COMPLETE. That is the manufactured measurement
# this whole binding block exists to prevent, arriving through the one door it left open.
#
# So each tree is also digested over WHAT IS ON DISK AND VISIBLE TO GIT:
#   * `git diff HEAD` over tracked files -- content, unstaged, not merely names;
#   * `git diff --cached HEAD` -- the INDEX. Round F3: `diff HEAD` compares the WORKING FILE to
#     the commit, so a change that was staged and then had its working file restored to HEAD
#     produces an empty `diff HEAD` and an unchanged digest, while the index a lane's `git
#     diff --cached` (or any tool reading the index) would show is different;
#   * every untracked NON-IGNORED path, each with its content hash.
#
# It FAILS CLOSED, which the first version did not (round F1). That version ran the enumeration
# and the per-path hashing inside a brace group whose exit status came only from the FINAL
# `hash-object --stdin`, with `2>/dev/null` on the parts that could fail -- so a failed
# enumeration or an unreadable file yielded a perfectly well-formed digest over PARTIAL text,
# which is worse than no digest: it is a binding that silently stops binding. And `ls-files`
# without `-z` C-QUOTES any path with a newline, a quote or a non-ASCII byte (core.quotePath is
# on by default), so those paths were hashed as their *quoted spelling* -- a stable string that
# does not change when the file's CONTENT does. Now: `-z`, NUL-record filtering, one hash per
# exact path, every command guarded, and ANY failure anywhere makes the whole digest `unknown`
# -- which check_bindings refuses on. Consequence to accept knowingly: an unreadable or dangling
# untracked path makes the tree undigestable, and therefore un-REUSABLE, until it is dealt with.
#
# What it deliberately does NOT cover: ignored content, which `--exclude-standard` drops BY
# CONSTRUCTION. That exclusion is DISCLOSED, NOT ENFORCED, and the reason is that a live bench
# rewrites ignored state continuously -- MLV-App's OS heartbeat rewrites
# .claude-state\heartbeat\board-snapshot.md every ten minutes, ledgers grow, and RP_OUT itself
# usually lives under .claude-state -- so an ENFORCED ignored-content binding would refuse
# nearly every legitimate reuse and would push operators straight to a bypass. A control that is
# always wrong is not a control; it is a habit of ignoring controls. (It is also what keeps the
# digest bounded: 177,449 ignored paths, 4.7 s, measured on the MLV-App bench.) Instead every
# --from / --retry-missing run PRINTS the REUSE line below and carries it into environment.json
# and the posture line, so a reused posture never reads as a pristine one.
# Nor does it cover an RP_OUT that lives inside the tree: the run writes there while it runs, so
# counting it would make every `--from` refuse itself. A non-git directory digests to the
# constant `not-a-git-tree` -- deterministic, and honest that it binds nothing.
worktree_digest() {  # dir -> 40-hex digest | not-a-git-tree | unknown
  local d="$1" top out_rel="" list dig rc=0
  top=$(git -C "$d" rev-parse --show-toplevel 2>/dev/null) || { printf '%s\n' not-a-git-tree; return; }
  [ -n "$top" ] || { printf '%s\n' not-a-git-tree; return; }
  case "$RP_OUT/" in "$top/"*) out_rel="${RP_OUT#"$top/"}/" ;; esac
  # The NUL-delimited list goes to a FILE, not a variable: command substitution deletes NUL
  # bytes, which would silently re-join exactly the paths -z exists to keep apart. It is kept
  # OUTSIDE both trees, so it can never enumerate itself.
  list=$(mktemp "${TMPDIR:-/tmp}/rp-wtd.XXXXXX") || { printf '%s\n' unknown; return; }
  git -C "$top" ls-files -z --others --exclude-standard > "$list" || { rm -f "$list"; printf '%s\n' unknown; return; }
  dig=$(
    set -o pipefail
    { echo "== tracked, modified vs HEAD"
      git -C "$top" diff HEAD -- || exit 1
      echo "== staged vs HEAD"
      git -C "$top" diff --cached HEAD -- || exit 1
      echo "== untracked, not ignored"
      while IFS= read -r -d '' p; do
        [ -n "$out_rel" ] && case "$p" in "$out_rel"*) continue ;; esac
        h=$(git -C "$top" hash-object -- "$top/$p") || exit 1
        case "$h" in [0-9a-f][0-9a-f]*) ;; *) exit 1 ;; esac
        # Length-prefixed: the record is unambiguous even when the path itself contains a
        # newline, a space or the field separator.
        printf '%s %s %s\n' "${#p}" "$h" "$p"
      done < "$list"
    } | git -C "$top" hash-object --stdin
  ) || rc=1
  rm -f "$list"
  { [ "$rc" = 0 ] && [ -n "$dig" ]; } || { printf '%s\n' unknown; return; }
  printf '%s\n' "$dig"
}
binding_values() {   # KEY=value lines describing THIS run's inputs
  printf '%s\n' \
    "subject_path=$RP_SUBJECT" \
    "subject_blob=$(blob_of "$RP_SUBJECT")" \
    "bench_head=$(head_of "$RP_BENCH")" \
    "bench_worktree=$(worktree_digest "$RP_BENCH")" \
    "repo_head=$(head_of "$RP_REPO")" \
    "repo_worktree=$(worktree_digest "$RP_REPO")" \
    "rubric_src_blob=$(blob_of "${RP_RUBRIC:-$HERE/rubrics/approach-a-r15.json}")" \
    "rubric_id=$([ -f "$RP_OUT/rubric_id" ] && tr -d '\r\n' < "$RP_OUT/rubric_id" || echo absent)" \
    "tool_run_sh=$(blob_of "$HERE/run.sh")" \
    "tool_review_posture_py=$(blob_of "$HERE/review_posture.py")"
}
binding_get() {  # file key -> value
  sed -n "s/^$2=//p" "$1" 2>/dev/null | head -1
}
write_bindings() {  # stage -- called AFTER a stage has actually been dispatched
  local prev=""
  [ -f "$BINDINGS" ] && prev=$(binding_get "$BINDINGS" stages_dispatched)
  case " $prev " in *" $1 "*) ;; *) prev="${prev}${prev:+ }$1" ;; esac
  { echo "# review-posture run bindings. Written after each dispatched stage; read by --from."
    echo "# A --from run refuses unless EVERY value below still matches what it re-derives."
    binding_values
    echo "stages_dispatched=$prev"
  } > "$BINDINGS"
}
# Name the TREE and its path under a worktree/HEAD mismatch: the HEADs match by construction
# when only the digest moved (they are separate keys), so an operator reading "digest differs"
# alone would go looking at commits. The difference is uncommitted, and it is on disk right now.
binding_name_tree() {  # key
  local which dir
  case "$1" in
    bench_worktree|repo_worktree|bench_head|repo_head) which=${1%_*} ;;
    *) return 0 ;;
  esac
  eval "dir=\$RP_$(echo "$which" | tr 'a-z' 'A-Z')"
  case "$1" in
    *_worktree)
      echo "    ^ the $which WORKING TREE at $dir changed while its HEAD did not:" >&2
      echo "      uncommitted edits to tracked files, staged content, or untracked non-ignored files," >&2
      echo "      differ from what the reused stages actually inspected. See: git -C '$dir' status --short" >&2 ;;
    *_head)
      echo "    ^ the $which tree at $dir: see git -C '$dir' rev-parse HEAD" >&2 ;;
  esac
}
check_bindings() {  # FROM (A|B|C|D) [label]
  local need="" st bad=0 k cur was
  # $2 names the flag being checked: --from reuses whole stages, --retry-missing reuses the
  # individual lanes it keeps. Same question, so the same check and the same refusals.
  local what="${2:---from $1}"
  # Every stage strictly before $1 is being reused, so every one of them must have been
  # dispatched by the run that wrote these bindings.
  for st in A B C D; do [ "$st" = "$1" ] && break; need="$need $st"; done
  if [ ! -f "$BINDINGS" ]; then
    echo "$what REFUSED: no $BINDINGS in RP_OUT." >&2
    echo "  Reusing stages$need means trusting sentinels this run cannot attribute to any subject," >&2
    echo "  bench or tool version. There is no override: re-run from A." >&2
    return 1
  fi
  was=$(binding_get "$BINDINGS" stages_dispatched)
  for st in $need; do
    case " $was " in *" $st "*) ;; *) echo "$what MISMATCH stages_dispatched: stage $st was never dispatched by the run that wrote $BINDINGS (it recorded: ${was:-none})" >&2; bad=1 ;; esac
  done
  # rubric_id is compared as it stands NOW against what the dispatching run recorded, so a
  # swapped rubric artifact in RP_OUT is caught as well as a changed rubric source.
  while IFS= read -r line; do
    k=${line%%=*}; cur=${line#*=}
    was=$(binding_get "$BINDINGS" "$k")
    # UNKNOWN IS NOT A VALUE, IT IS THE ABSENCE OF ONE (round F2). Two `unknown`s compare equal,
    # so an input that could not be measured -- then or now -- used to sail through this loop as
    # a MATCH and license the reuse it was supposed to gate. For the keys that actually bind the
    # measurement to a subject and a disk state, `unknown` or empty on EITHER side is a refusal.
    case "$k" in
      bench_worktree|repo_worktree|bench_head|repo_head|*_blob)
        if [ "$cur" = unknown ] || [ -z "$cur" ] || [ "$was" = unknown ] || [ -z "$was" ]; then
          echo "$what MISMATCH $k: could not be computed -- refusing rather than assuming it is unchanged" >&2
          echo "    recorded by the run that produced stages$need : ${was:-<absent>}" >&2
          echo "    measured now                                  : ${cur:-<absent>}" >&2
          binding_name_tree "$k"
          bad=1
          continue
        fi
        ;;
    esac
    if [ "$cur" != "$was" ]; then
      echo "$what MISMATCH $k:" >&2
      echo "    recorded by the run that produced stages$need : ${was:-<absent>}" >&2
      echo "    measured now                                  : $cur" >&2
      binding_name_tree "$k"
      bad=1
    fi
  done <<EOF
$(binding_values)
EOF
  [ "$bad" = 0 ] || {
    echo "$what REFUSED: the reused stages were produced under different inputs than this run." >&2
    echo "  A posture assembled from them would be a measurement of something that no longer exists." >&2
    echo "  Re-run from A. There is no bypass flag, on purpose." >&2
    return 1
  }
  stamp "$what: bindings match the run that dispatched stages${need:- (none reused wholesale)}"
  # `not-a-git-tree` on both sides is a legitimate MATCH -- it is deterministic and it is the
  # same on both sides -- but it matches by binding NOTHING, and a reader of the log must not
  # read that as "this tree was verified unchanged".
  # What is being reused, and the one thing this run CANNOT say about it.
  local reused=${need# }
  [ "$RETRY" = 1 ] && reused="${reused:+$reused + }kept lanes"
  REUSE_LINE="REUSE: stages ${reused:-none} reused; ignored content NOT bound -- lanes may have cited it"
  for k in bench repo; do
    eval "cur=\$(binding_get \"\$BINDINGS\" ${k}_worktree)"
    [ "$cur" = not-a-git-tree ] || continue
    eval "was=\$RP_$(echo "$k" | tr 'a-z' 'A-Z')"
    echo "DISCLOSURE: the $k tree at $was is not a git tree -- ${k}_head/${k}_worktree bind NOTHING about it; nothing there was verified unchanged."
  done
  echo "$REUSE_LINE"
  return 0
}

# Judge on the sentinel: the exact line, alone, with NOTHING AFTER IT -- which means it must
# be the LAST non-blank line of the file, not merely a line somewhere in it. The contract the
# lanes are given says "Then stop. Nothing after this item"; a `ran` that accepted the
# sentinel followed by 200 lines of prose was measuring something the contract does not say.
# `[[:space:]]`, not `\s`: `\s` is a GNU grep extension that BSD grep (macOS) does not honour,
# and an unportable sentinel test would report every lane DID-NOT-RUN on a Mac. CR is
# tolerated (a CRLF-writing CLI leaves it behind). review_posture.py:ran() must agree exactly.
ran() {
  [ -f "$RP_OUT/$1.txt" ] || return 1
  local last
  last=$(tr -d '\r' < "$RP_OUT/$1.txt" 2>/dev/null | sed -e 's/[[:space:]]*$//' -e '/^$/d' | tail -1)
  [ "$last" = "LANE-COMPLETE" ]
}
# `.prompt` IS cleared, and that is load-bearing, not tidiness. Measured 2026-09-14 (V4
# re-attack, host VIRTUAL-TEN): run 1 completes against subject `doc.md`; run 2 reuses the same
# RP_OUT for `doc2.md` while `py prompts` exits 0 having written elsewhere (the path-dialect
# shape). Run 1's stale `.prompt` files satisfied `check_prompts`, so the backstop never fired
# and 13 lanes were dispatched AT THE PREVIOUS SUBJECT -- while environment.json recorded the
# new subject and its blob sha. A post-condition that a previous run can satisfy is not a
# post-condition.
clear_lanes() { for n in "$@"; do rm -f "$RP_OUT/$n.txt" "$RP_OUT/$n.rc" "$RP_OUT/$n.log" "$RP_OUT/$n.prompt" \
                                     "$RP_OUT/$n.attempt1.txt" "$RP_OUT/$n.attempt1.rc" "$RP_OUT/$n.attempt1.log"; done; }

claude_lane() {  # name model secs
  ( RP_LANE="$1" RP_FAMILY=claude; export RP_LANE RP_FAMILY
    cd "$RP_REPO" && cli_timed claude "$3" -p --model "$2" --permission-mode plan --add-dir "$RP_REPO" --add-dir "$RP_BENCH" \
      < "$RP_OUT/$1.prompt" > "$RP_OUT/$1.txt" 2> "$RP_OUT/$1.log"; echo $? > "$RP_OUT/$1.rc" ) & }
codex_lane() {   # name model secs
  ( RP_LANE="$1" RP_FAMILY=codex; export RP_LANE RP_FAMILY
    cli_timed codex "$3" exec -m "$2" -c model_reasoning_effort=high -s read-only --cd "$RP_REPO" \
      -o "$RP_OUT/$1.txt" - < "$RP_OUT/$1.prompt" > "$RP_OUT/$1.log" 2>&1; echo $? > "$RP_OUT/$1.rc" ) & }

# ---------------------------------------------------------------- dispatch EVENTS (not plans)
# environment.json used to publish `models_dispatched`, built by walking roles.json -- i.e. the
# PLAN. Every lane appeared "dispatched at model X" including lanes whose family had no working
# CLI, lanes in a stage that blocked, and lanes of a dry run that launched nothing. A field a
# reader uses to attribute a finding to a model must record what HAPPENED, so it is appended
# here as each thing happens and read back after the stage.
EVENTS="$RP_OUT/dispatch-events.tsv"
CUR_STAGE=""
rp_event() {  # kind lane family model [detail]
  printf '%s|%s|%s|%s|%s|%s|%s\n' \
    "$(date -u +%FT%TZ)" "$1" "${CUR_STAGE:-?}" "$2" "$3" "$4" "${5:-}" >> "$EVENTS"
}

dispatch() {     # name family nickname secs  -> pid in LASTPID
  local id; id=$(model_for_nick "$3")
  [ -n "$id" ] || { echo "DISPATCH REFUSED lane=$1: nickname '$3' has no resolved model id" >&2; exit 2; }
  if [ "$(cli_verified "$2")" != yes ]; then
    echo "DISPATCH REFUSED lane=$1 family=$2: CLI unavailable -- $(cli_cause "$2")" | tee -a "$REPAIRS" >&2
    rp_event dispatch-refused "$1" "$2" "$id" "CLI unavailable: $(cli_fault "$2")"
    LASTPID=""; return 0
  fi
  if [ "$2" = claude ]; then claude_lane "$1" "$id" "$4"; else codex_lane "$1" "$id" "$4"; fi
  LASTPID=$!
  rp_event "${RP_EVENT_KIND:-dispatched}" "$1" "$2" "$id"
}

_stage_lanes_raw() {  # stage -> "name family model" lines from roles.json
  "$PYTHON" - "$HERE/roles.json" "$1" <<'PY'
import json,sys
for r in json.load(open(sys.argv[1]))["roles"]:
    if r["stage"]==sys.argv[2]:
        for l in r["lanes"]: print(l["name"], l["family"], l["model"])
PY
}
stage_lanes() { _stage_lanes_raw "$1" | tr -d '\r'; }   # native-Windows python emits CRLF
all_stages() { for s in A B C D; do stage_lanes "$s"; done; }

# POST-CONDITION on prompt generation. `py prompts <stage>` exiting 0 is NOT evidence that the
# prompts exist where the runner will look for them -- that is exactly what the path-dialect
# fault above proved. Dispatching 17 lanes onto absent files produced a 0/17 posture whose
# cause appeared nowhere. So: after generating, LOOK.
check_prompts() {  # stage
  local name fam nick missing=""
  while read -r name fam nick; do
    [ -f "$RP_OUT/$name.prompt" ] || missing="$missing $name"
  done < <(stage_lanes "$1")
  [ -z "$missing" ] && return 0
  echo "PROMPTS MISSING after 'prompts $1':$missing" >&2
  echo "  expected in RP_OUT=$RP_OUT (path dialect: $PATH_DIALECT, python: $PYTHON)." >&2
  echo "  CAUSE: 'review_posture.py prompts $1' exited 0 without writing them there -- most often" >&2
  echo "  bash and python disagreeing about what an absolute path means. Refusing to dispatch" >&2
  echo "  lanes onto files that are not there." >&2
  return 1
}

# A lane that exited 0, wrote bytes, and did not emit the sentinel is the F4 shape: the model
# answered but never acknowledged the contract. Retry it ONCE, with the SAME prompt, keeping
# attempt 1 intact. We never append a sentinel and never soften `ran` -- a retry that also
# misses stays DID-NOT-RUN.
# `retry_prepare` decides and snapshots; the dispatch and the wait are done by run_stage for
# the whole stage at once. Retrying serially cost N x timeout for N misses in one stage.
RETRY_BYTES=0
retry_prepare() {  # name -> 0 if this lane should be retried
  local name="$1" rc bytes ext
  rc=$(tr -d '[:space:]' < "$RP_OUT/$name.rc" 2>/dev/null || echo 99); [ -n "$rc" ] || rc=99
  bytes=$(wc -c < "$RP_OUT/$name.txt" 2>/dev/null || echo 0); bytes=$(echo "$bytes" | tr -d '[:space:]')
  [ "$rc" = 0 ] || return 1
  [ "${bytes:-0}" -gt 0 ] 2>/dev/null || return 1
  ran "$name" && return 1
  [ -f "$RP_OUT/$name.attempt1.txt" ] && return 1        # bounded: at most one retry, ever
  for ext in txt rc log; do
    [ -f "$RP_OUT/$name.$ext" ] && cp "$RP_OUT/$name.$ext" "$RP_OUT/$name.attempt1.$ext"
  done
  RETRY_BYTES=$bytes
  stamp "SENTINEL_MISSING lane=$name rc=0 bytes=$bytes -- retrying once with the identical prompt" | tee -a "$REPAIRS"
  return 0
}

run_stage() {    # stage secs
  local secs="$2" name fam nick rec npids=0 nrecs=0 nrp=0 nrr=0 result
  local pids=() recs=() rpids=() rrecs=()
  CUR_STAGE="$1"
  while read -r name fam nick; do
    # --retry-missing: a lane that already cleared the sentinel is kept, not relaunched. It is
    # recorded as `kept-from-previous-run`, NOT as dispatched -- this run launched no process
    # for it, and environment.json must not claim one (S-2).
    if [ "$RETRY" = 1 ] && ran "$name"; then
      stamp "keep $name (already cleared the sentinel)"
      rp_event kept-from-previous-run "$name" "$fam" "$(model_for_nick "$nick")"
      recs[$nrecs]="$name $fam $nick"; nrecs=$((nrecs+1))
      continue
    fi
    dispatch "$name" "$fam" "$nick" "$secs"
    [ -n "${LASTPID:-}" ] && { pids[$npids]="$LASTPID"; npids=$((npids+1)); }
    recs[$nrecs]="$name $fam $nick"; nrecs=$((nrecs+1))
  done < <(stage_lanes "$1")
  [ "$npids" -gt 0 ] && { wait "${pids[@]}" || :; }
  # Collect every lane that needs a retry, dispatch them TOGETHER, wait once.
  local i=0
  while [ "$i" -lt "$nrecs" ]; do
    # shellcheck disable=SC2086
    set -- ${recs[$i]}
    i=$((i+1))
    retry_prepare "$1" || continue
    rrecs[$nrr]="$1 $RETRY_BYTES"; nrr=$((nrr+1))
    # Set and cleared explicitly: `VAR=x func` does NOT scope the assignment to a shell
    # function in bash's default mode -- it leaks, and every later dispatch would log "retried".
    RP_EVENT_KIND=retried; dispatch "$1" "$2" "$3" "$secs"; RP_EVENT_KIND=dispatched
    [ -n "${LASTPID:-}" ] && { rpids[$nrp]="$LASTPID"; nrp=$((nrp+1)); }
  done
  [ "$nrp" -gt 0 ] && { wait "${rpids[@]}" || :; }
  i=0
  while [ "$i" -lt "$nrr" ]; do
    # shellcheck disable=SC2086
    set -- ${rrecs[$i]}
    i=$((i+1))
    if ran "$1"; then result=RAN; else result=DID-NOT-RUN; fi
    echo "SENTINEL_RETRY lane=$1 attempt1_bytes=$2 result=$result" | tee -a "$REPAIRS"
  done
  # Outcome, recorded per lane after the stage has finished -- the only point at which
  # "completed" is a measurement rather than a forecast.
  i=0
  while [ "$i" -lt "$nrecs" ]; do
    # shellcheck disable=SC2086
    set -- ${recs[$i]}
    i=$((i+1))
    if ran "$1"; then rp_event completed-with-sentinel "$1" "$2" "$(model_for_nick "$3")"
    else rp_event no-sentinel "$1" "$2" "$(model_for_nick "$3")"; fi
  done
  CUR_STAGE=""
}

# ---------------------------------------------------------------- environment.json (F5)
# A filing must be able to say what environment it ran under. Data only, no secrets: the
# things that measurably changed results on this fleet -- which bash, spaces in paths, the
# effective core.autocrlf (the SYSTEM gitconfig sets it true here, which reshapes blob
# hashes), the worktree layout of each tree, the bench HEAD, the subject blob the lanes
# actually read, the per-lane DISPATCH RECORD (planned vs dispatched vs retried vs
# completed-with-sentinel -- four distinct measurements, never one field standing in for the
# other three), and where the model ids came from.
git_tree_facts() {  # label dir -> KEY=value lines
  local lbl="$1" d="$2" top common gitdir linked=unknown
  top=$(git -C "$d" rev-parse --show-toplevel 2>/dev/null || echo unknown)
  common=$(git -C "$d" rev-parse --git-common-dir 2>/dev/null || echo unknown)
  gitdir=$(git -C "$d" rev-parse --git-dir 2>/dev/null || echo unknown)
  if [ "$gitdir" != unknown ] && [ "$common" != unknown ]; then
    if [ "$gitdir" = "$common" ]; then linked=false; else linked=true; fi
  fi
  printf '%s\n' "$lbl|toplevel|$top" "$lbl|git_dir|$gitdir" "$lbl|git_common_dir|$common" "$lbl|is_linked_worktree|$linked"
}
# The PLAN, and labelled as such. What actually launched is in $EVENTS.
models_planned() {
  local st name fam nick
  for st in A B C D; do
    while read -r name fam nick; do
      printf '%s|%s|%s|%s\n' "$st" "$name" "$fam" "$(model_for_nick "$nick")"
    done < <(stage_lanes "$st")
  done
}
inventory_path() { printf '%s\n' "${RP_INVENTORY:-$HOME/.claude/machine-inventory.yaml}"; }
inventory_probed_under() {
  local p; p="$(inventory_path)"
  [ -f "$p" ] || { printf '%s\n' "unknown   # reason: inventory not found at $p"; return; }
  sed -n 's/^probed_under:[[:space:]]*//p' "$p" | head -1 | sed -n '1{s/[[:space:]]*$//;p;}' \
    | grep . || printf '%s\n' "unknown   # reason: inventory carries no probed_under line"
}
write_environment() {
  RP_ENV_BASH="$(command -v bash || echo unknown)" \
  RP_ENV_BASH_VERSION="${BASH_VERSION:-unknown}" \
  RP_ENV_UNAME="$(uname -a 2>/dev/null || echo unknown)" \
  RP_ENV_HOST="$(hostname 2>/dev/null || echo unknown)" \
  RP_ENV_PYTHON="$PYTHON" \
  RP_ENV_PYTHON_VERSION="$("$PYTHON" -c 'import sys;print(sys.version.split()[0])' 2>/dev/null || echo unknown)" \
  RP_ENV_PYTHON_PLATFORM="$("$PYTHON" -c 'import sys;print(sys.platform)' 2>/dev/null || echo unknown)" \
  RP_ENV_PATH_DIALECT="$PATH_DIALECT" \
  RP_ENV_TIMEOUT_IMPL="$(run_timeout_impl)" \
  RP_ENV_CLAUDE_INVOKE="$(cli_invoke claude)" RP_ENV_CLAUDE_VERSION="$(cli_version claude)" \
  RP_ENV_CLAUDE_FAULT="$(cli_fault claude)" RP_ENV_CLAUDE_REPAIR="$(cli_repair claude)" \
  RP_ENV_CLAUDE_VERIFIED="$(cli_verified claude)" RP_ENV_CLAUDE_CAUSE="$(cli_cause claude)" \
  RP_ENV_CODEX_INVOKE="$(cli_invoke codex)" RP_ENV_CODEX_VERSION="$(cli_version codex)" \
  RP_ENV_CODEX_FAULT="$(cli_fault codex)" RP_ENV_CODEX_REPAIR="$(cli_repair codex)" \
  RP_ENV_CODEX_VERIFIED="$(cli_verified codex)" RP_ENV_CODEX_CAUSE="$(cli_cause codex)" \
  RP_ENV_AUTOCRLF_BENCH="$(git -C "$RP_BENCH" config --get core.autocrlf 2>/dev/null || echo unset)" \
  RP_ENV_AUTOCRLF_REPO="$(git -C "$RP_REPO" config --get core.autocrlf 2>/dev/null || echo unset)" \
  RP_ENV_BENCH_HEAD="$(head_of "$RP_BENCH")" \
  RP_ENV_REPO_HEAD="$(head_of "$RP_REPO")" \
  RP_ENV_BENCH_WORKTREE="$(worktree_digest "$RP_BENCH")" \
  RP_ENV_REPO_WORKTREE="$(worktree_digest "$RP_REPO")" \
  RP_ENV_TREES="$(git_tree_facts bench "$RP_BENCH"; git_tree_facts repo "$RP_REPO")" \
  RP_ENV_SUBJECT_BLOB="$(git hash-object -- "$RP_SUBJECT" 2>/dev/null || echo unknown)" \
  RP_ENV_MODELS="$(models_planned)" \
  RP_ENV_EVENTS="$(cat "$EVENTS" 2>/dev/null || true)" \
  RP_ENV_FROM="$FROM" RP_ENV_DRY="$DRY" RP_ENV_RETRY="$RETRY" RP_ENV_REUSE="$REUSE_LINE" \
  RP_ENV_INVENTORY="$(inventory_path)" \
  RP_ENV_PROBED_UNDER="$(inventory_probed_under)" \
  RP_ENV_REPAIRS="$(cli_repairs_log)" \
  "$PYTHON" - <<'PY' > "$RP_OUT/environment.json"
import json, os
g = lambda k: os.environ.get("RP_ENV_" + k, "")
def has_space(p): return " " in (p or "")
trees = {}
for line in g("TREES").splitlines():
    parts = line.split("|", 2)
    if len(parts) == 3:
        trees.setdefault(parts[0], {})[parts[1]] = parts[2]
# PLANNED comes from roles.json; every other field comes from an event the runner appended at
# the moment the thing happened. A lane is "dispatched" only if a process was launched for it,
# "retried" only if a second one was, and "completed_with_sentinel" only if its own output was
# judged after the stage. A dry run leaves all three false, which is the honest record of a run
# that deliberately launched nothing -- the old field called all 17 of them dispatched.
lanes = {}
order = []
for line in g("MODELS").splitlines():
    p = line.split("|", 3)
    if len(p) == 4 and p[1]:
        lanes[p[1]] = {"stage": p[0], "lane": p[1], "family": p[2], "model_planned": p[3],
                       "planned": True, "dispatched": False, "retried": False,
                       "completed_with_sentinel": False, "dispatch_refused": None,
                       "models_launched": [], "events": []}
        order.append(p[1])
for line in g("EVENTS").splitlines():
    p = line.split("|", 6)
    if len(p) != 7:
        continue
    ts, kind, stage, lane, fam, model, detail = p
    r = lanes.get(lane)
    if r is None:
        continue
    r["events"].append({"at": ts, "kind": kind, "stage": stage, "model": model,
                        "detail": detail or None})
    if kind in ("dispatched", "retried"):
        if kind == "dispatched":
            r["dispatched"] = True
        else:
            r["retried"] = True
            r["dispatched"] = True     # a retry is a second launch; the first one happened
        if model and model not in r["models_launched"]:
            r["models_launched"].append(model)
    elif kind == "dispatch-refused":
        r["dispatch_refused"] = detail or "refused"
    elif kind == "completed-with-sentinel":
        r["completed_with_sentinel"] = True
models = [lanes[n] for n in order]
counts = {k: sum(1 for r in models if r[k]) for k in
          ("planned", "dispatched", "retried", "completed_with_sentinel")}
counts["dispatch_refused"] = sum(1 for r in models if r["dispatch_refused"])
env = {
  "schema": "review-posture/environment.v1",
  "note": "data only; no credentials, no tokens. Values are measured at run start on this host.",
  "shell": {"bash": g("BASH"), "bash_version": g("BASH_VERSION"), "timeout_impl": g("TIMEOUT_IMPL")},
  "host": {"uname": g("UNAME"), "hostname": g("HOST")},
  "python": {"interpreter": g("PYTHON"), "version": g("PYTHON_VERSION"), "platform": g("PYTHON_PLATFORM")},
  "path_dialect": g("PATH_DIALECT"),
  "paths": {k.lower(): {"value": os.environ.get(k, ""), "has_space": has_space(os.environ.get(k, ""))}
            for k in ("RP_OUT", "RP_SUBJECT", "RP_BENCH", "RP_REPO")},
  "path_has_space": any(has_space(os.environ.get(k, "")) for k in ("RP_OUT", "RP_SUBJECT", "RP_BENCH", "RP_REPO")),
  "clis": {f: {"invocation": g(f.upper() + "_INVOKE"), "version": g(f.upper() + "_VERSION"),
               "fault": g(f.upper() + "_FAULT"), "repair": g(f.upper() + "_REPAIR"),
               "verified": g(f.upper() + "_VERIFIED"), "cause": g(f.upper() + "_CAUSE") or None}
           for f in ("claude", "codex")},
  "repairs_applied": [l for l in g("REPAIRS").splitlines() if l.strip()],
  "git": {"core_autocrlf_effective": {"bench": g("AUTOCRLF_BENCH"), "repo": g("AUTOCRLF_REPO")},
          "bench_head": g("BENCH_HEAD"), "repo_head": g("REPO_HEAD"), "trees": trees,
          # What a HEAD cannot say: whether the tree on disk still IS that commit. Digest of
          # the tracked diff vs HEAD plus every untracked non-ignored file's content; ignored
          # content and a nested RP_OUT are excluded by construction. `--from`/`--retry-missing`
          # refuse on any change to these, naming the tree.
          "worktree_digest": {"bench": g("BENCH_WORKTREE"), "repo": g("REPO_WORKTREE")}},
  "subject_blob_sha": g("SUBJECT_BLOB"),
  # reuse_disclosure is the exact line printed to stdout and appended to the posture line on any
  # --from / --retry-missing run. null on a from-A run, which reuses nothing. Ignored content is
  # DISCLOSED, NOT ENFORCED: a live bench rewrites ignored state continuously (an OS heartbeat
  # rewrites a snapshot every ten minutes, ledgers grow, RP_OUT usually lives under one), so an
  # enforced binding would refuse nearly every reuse and push operators to a bypass.
  "invocation": {"from_stage": g("FROM"), "dry_run": g("DRY") == "1",
                 "retry_missing": g("RETRY") == "1",
                 "reuse_disclosure": g("REUSE") or None},
  "lanes": models,
  "lane_counts": counts,
  "inventory": {"path": g("INVENTORY"), "probed_under": g("PROBED_UNDER")},
}
print(json.dumps(env, indent=2, sort_keys=True))
PY
}
case "$FROM" in A|B|C|D) ;; *) echo "--from must be one of A B C D (got '$FROM')"; exit 2 ;; esac
order="A B C D"; order=${order#*"$FROM"}; order="$FROM$order"

# The event log belongs to THIS invocation. Truncated here, appended to as things launch, and
# read back by write_environment at the end.
: > "$EVENTS"

# --from reuses earlier stages' sentinels; refuse unless they were produced under these inputs.
# Checked BEFORE anything is generated, cleared or dispatched, so a refusal costs nothing and
# destroys nothing. `--retry-missing` reuses the lanes it KEEPS, which is the same reuse with a
# finer grain, so it is bound by the same check -- a retry over a changed subject would splice
# fresh lanes onto stale ones and call the result a posture.
if [ "$FROM" != A ] || [ "$RETRY" = 1 ]; then
  if [ "$RETRY" = 1 ]; then check_bindings "$FROM" "--retry-missing" || exit 2
  else check_bindings "$FROM" || exit 2; fi
fi

# ---------------------------------------------------------------- pre-dispatch preflight
# TWO layers, and the ORDER between them is the design, not an accident:
#   1. cli_resolve REPAIRS   -- structural detection of the broken shim, a bounded ladder, an
#      identity check, and every rung verified with --version before it is accepted.
#   2. this block VERIFIES   -- it probes the entrypoint each lane will really use, on the
#      REPAIRED argv (`cli_timed`), not on a bare `codex`. Probing the bare name here would
#      re-measure the very shim the resolver just routed around, and would report
#      LAUNCHER-BROKEN for a family this run can in fact dispatch.
# A launcher that cannot be repaired still ends in the same refusal PR #62 introduced --
# `LAUNCHER-BROKEN ... -- refuse to dispatch (a posture cannot be complete)` -- now carrying the
# resolver's fault and cause instead of a bare exit code. rc=127 from a stale npm `node` shim
# once dropped every Codex lane while auth and model ids were healthy (TRAPS, 2026-09-14).
#
# Nicknames are resolved for EVERY pending lane first, so a roles.json nickname the inventory
# never defines cannot strand paid lanes that already started (PR #62). Under --retry-missing a
# lane that already cleared the sentinel is not pending, so neither is its family.
unresolved=0; pending_fams=""
for st in $order; do while read -r name fam nick; do
  if [ "$RETRY" = 1 ] && ran "$name"; then continue; fi
  case " $pending_fams " in *" $fam "*) ;; *) pending_fams="$pending_fams $fam" ;; esac
  [ -n "$(model_for_nick "$nick")" ] || { echo "UNRESOLVED nickname $nick for lane $name"; unresolved=1; }
done < <(stage_lanes "$st"); done
[ "$unresolved" = 0 ] || { echo "UNRESOLVED nicknames -- refuse to dispatch"; exit 2; }

# A family with no pending lane is never probed, and is recorded as not-probed rather than as
# unavailable: environment.json must not report a verdict this run never measured.
for fam in claude codex; do
  case " $pending_fams " in *" $fam "*) ;; *) cli_mark_not_probed "$fam"; cli_repair_line "$fam" | tee -a "$REPAIRS" ;; esac
done

launchers_ok=1
for fam in $pending_fams; do
  if cli_resolve "$fam"; then
    echo "launcher ok family=$fam [$fam --version] $(cli_invoke "$fam") $(cli_version "$fam")"
  else
    # The resolver already exhausted the ladder; its fault code carries the real exit status.
    lrc=$(cli_fault "$fam"); case "$lrc" in rc[0-9]*) lrc=${lrc#rc} ;; esac
    echo "LAUNCHER-BROKEN family=$fam [$fam --version] rc=$lrc: $(cli_cause "$fam")"
    launchers_ok=0
  fi
  cli_repair_line "$fam" | tee -a "$REPAIRS"
  [ "$(cli_verified "$fam")" = yes ] || continue
  # Second rung: `--version` can answer while the subcommand a lane actually invokes cannot.
  case "$fam" in
    claude) checks="--help" ;;
    codex)  checks="exec --help" ;;
    *)      checks="" ;;
  esac
  [ -n "$checks" ] || continue
  # shellcheck disable=SC2086
  if out=$(cli_timed "$fam" 30 $checks 2>&1); then
    echo "launcher ok family=$fam [$fam $checks] $(printf '%s' "$out" | head -n 1)"
  else
    lrc=$?
    lline=$(printf '%s' "$out" | head -n 1)
    [ "$lrc" = 124 ] && lline="timed out after 30s"
    echo "LAUNCHER-BROKEN family=$fam [$fam $checks] rc=$lrc: $lline"
    launchers_ok=0
  fi
done
# A dry run dispatches nothing, so a broken launcher cannot corrupt its result: it is reported
# and the prompt-generation checks still run. Only a real run refuses.
[ "$launchers_ok" = 1 ] || [ "$DRY" = 1 ] || { echo "LAUNCHER-BROKEN -- refuse to dispatch (a posture cannot be complete)"; exit 2; }

write_environment && stamp "wrote $RP_OUT/environment.json"

# Clear EVERY lane of EVERY stage in $order BEFORE the loop, not per-stage inside it.
# Measured: a blocked stage C `break`s out of the loop, so `run_stage C`/`run_stage D` -- and
# with them the only clearing that ever happened -- never ran. A PREVIOUS run's consolidator
# and classifier files were still in RP_OUT, still carried their sentinels, and were counted
# RAN for lanes that were never dispatched: `posture PARTIAL (16/17)` over a run that should
# have read 13/17, with stage C reported as four successful lanes answering a different
# subject. A lane that was never dispatched in THIS invocation is DID-NOT-RUN, full stop.
# A dry run dispatches nothing, so it clears nothing -- it must not destroy a real run's output.
# `--retry-missing` is the one exception, and it is a narrow one: a lane that already cleared
# the sentinel is KEPT (not cleared, not re-dispatched), and a lane that did not is snapshotted
# to `<name>.failed-<HHMMSS>.txt` before it is cleared, so the failed attempt survives the retry.
# The bindings check above has already proved the kept lanes answer THIS subject.
if [ "$DRY" = 0 ]; then
  kept=""
  for st in $order; do
    while read -r name fam nick; do
      # A kept lane keeps its .txt/.rc/.log but NOT its .prompt: check_prompts must still be
      # answering "did THIS run generate them", never "is an old file lying here" (case Q3).
      if [ "$RETRY" = 1 ] && ran "$name"; then kept="$kept $name"; rm -f "$RP_OUT/$name.prompt"; continue; fi
      [ "$RETRY" = 1 ] && [ -f "$RP_OUT/$name.txt" ] &&
        cp "$RP_OUT/$name.txt" "$RP_OUT/$name.failed-$(date -u +%H%M%S).txt"
      clear_lanes "$name"
    done < <(stage_lanes "$st")
  done
  if [ "$RETRY" = 1 ]; then
    stamp "cleared lane outputs for stages: $order (--retry-missing kept:${kept:- none})"
  else
    stamp "cleared lane outputs for stages: $order"
  fi
fi

BINDING_FAIL=0
for st in $order; do
  py prompts "$st" || { echo "STAGE $st prompt generation failed"; BINDING_FAIL=1; break; }
  check_prompts "$st" || { BINDING_FAIL=1; break; }
  if [ "$DRY" = 1 ]; then stamp "dry-run: stage $st prompts OK"; [ "$st" = B ] && break; continue; fi
  stamp "stage $st dispatch"
  case $st in
    A) run_stage A 1800 ;;
    B) run_stage B 1800; py score ;;
    C) run_stage C 1500 ;;
    D) run_stage D 900; py tally ;;
  esac
  # Record what this dispatch was bound to, so a later `--from` can be checked rather than
  # trusted. Written AFTER the stage: a stage that was not dispatched must not appear here.
  write_bindings "$st"
  stamp "stage $st done"
done

# Rewrite environment.json now that the run is over: the first write could only record the
# plan and the environment, and the dispatch record is only true in retrospect.
[ "$DRY" = 1 ] || write_environment

echo "=== lane status (judge on the sentinel, not rc, not bytes) ==="
for st in A B C D; do while read -r name fam nick; do
  ran "$name" && v=RAN || v=DID-NOT-RUN
  # The [ -f ] guards keep a not-yet-dispatched lane (a --dry-run, or a stage that blocked)
  # from spraying the shell's own redirection errors over the one table a reader trusts.
  printf 'stage=%s lane=%-14s %-11s rc=%-5s bytes=%s\n' "$st" "$name" "$v" \
    "$([ -f "$RP_OUT/$name.rc" ] && cat "$RP_OUT/$name.rc" || echo NONE)" \
    "$([ -f "$RP_OUT/$name.txt" ] && wc -c < "$RP_OUT/$name.txt" | tr -d ' ' || echo 0)"
done < <(stage_lanes "$st"); done
[ -f "$RP_OUT/rubric_id" ] && echo "rubric_id: $(cat "$RP_OUT/rubric_id")"
[ -s "$REPAIRS" ] && { echo "=== repairs applied (see environment.json) ==="; cat "$REPAIRS"; }

# A dry run dispatched nothing, so it has NOT measured a posture. Saying PARTIAL and exiting 1
# invited the reader to file a failed run; R9 says a posture is a measurement, and the honest
# report of a measurement not taken is that it was not taken. Binding failures still exit 1.
if [ "$DRY" = 1 ]; then
  # EVERY posture line carries the reuse disclosure, including this failing one. A reader who
  # quotes "NOT-MEASURED (dry-run; BINDING CHECKS FAILED)" off a `--from C` run and sees no
  # REUSE text reads it as a run that generated everything itself and failed -- when in fact
  # stages A-B were never re-generated at all. The two exit-2 refusals downstream of an accepted
  # reuse (UNRESOLVED nicknames, LAUNCHER-BROKEN) print no `posture:` line and are out of scope
  # by construction; check_bindings already echoed $REUSE_LINE to stdout before either can run.
  if [ "$BINDING_FAIL" = 1 ]; then echo "posture: NOT-MEASURED (dry-run; BINDING CHECKS FAILED -- see the cause above)${REUSE_LINE:+ [$REUSE_LINE]}"; exit 1; fi
  echo "posture: NOT-MEASURED (dry-run) -- prompts generated and binding-checked; no lane was dispatched${REUSE_LINE:+ [$REUSE_LINE]}"
  exit 0
fi
# The posture line itself carries the reuse disclosure. Printing it only further up the log
# leaves the ONE line every filing quotes reading exactly like a run that measured everything
# itself -- which is the whole difference a reader needs (round F4).
export RP_REUSE_NOTE="$REUSE_LINE"
py posture
