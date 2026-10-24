#!/usr/bin/env python3
"""Dispatch one `codex exec` review with an EXPLICIT, RECORDED model/effort tier.

    python tools/codex-review.py --role swarm       --cd <worktree> --prompt-file p.md --out o.txt
    python tools/codex-review.py --role counterpart --cd <worktree> --prompt-file p.md --out o.txt
    python tools/codex-review.py --role sweep       --cd <worktree> --prompt-file p.md --out o.txt
    python tools/codex-review.py --role census      --cd <worktree> --prompt-file p.md --out o.txt

THE DEFECT THIS CLOSES
-----------------------
Every review dispatched with a bare `codex exec` inherits whatever
`~/.codex/config.toml` happens to say on THIS machine right now -- measured
2026-09-26 as `gpt-6-astra` / `xhigh`, the ultra tier reserved for named sweeps
per `docs/operating-contract-model-routing.md`. The last 40 sessions on disk
(`~/.codex/sessions/**/rollout-*.jsonl`) ran Astra 14 times, Sol once, Luna
zero -- every cheap swarm/review seat and every Opus-counterpart seat paid the
ultra rate because nothing on the call site named a tier. A config file is
per-machine, ambient, and mutates outside any packet's diff, so pinning the
routing table only in prose leaves the same gap open the next time somebody
edits that file for an unrelated reason.

So this tool is the ONLY place a tier is decided: it passes `-m` and `-c
model_reasoning_effort=` on the command line, which override the config file
for that one invocation, and it never touches `~/.codex/config.toml` itself.
Anything that wants a review dispatches through here, not through a bare
`codex exec`.

WHY THE ACTUAL TIER IS READ BACK, NOT ASSUMED
-----------------------------------------------
Requesting a tier and RECEIVING it are different claims -- a stale binary, a
renamed model, or a config file that races this process could all silently
override the flags. So this tool re-derives the tier from the run's own
header lines in its output ("model: X", "reasoning effort: Y") rather than
trusting the argv it built. A run that cannot be read back, or that read back
something other than what was requested, is never reported as fine: it is
`"tier": "mismatch"` or `"tier": "unobserved"`, and the process exits non-zero
either way. Silence must not look like agreement (the same principle
`check-cli-auth.py` states for the account-parity case).

WHY `shutil.which` RESOLVES THE EXECUTABLE INSTEAD OF A BARE ARGV[0]
----------------------------------------------------------------------
On Windows, `subprocess.run(["codex", ...])` with no extension asks
`CreateProcess` to resolve the name, and `CreateProcess` appends only `.exe`
-- it does NOT consult `PATHEXT`, so a `codex.cmd` earlier on PATH loses to a
`codex.exe` later on PATH (measured empirically while building this tool:
prepending a directory containing only `codex.cmd` still ran a real,
installed `codex.exe`). `shutil.which` DOES walk `PATHEXT` per directory, in
PATH order, so it finds the nearest match the way a person typing the bare
command at a shell prompt would expect. Tests rely on this to put a fake
`codex` shim in front of anything real.

THE FINAL MESSAGE GOES TO ITS OWN FILE (K119)
---------------------------------------------
The `--out` file is a TRANSCRIPT: banner, echoed prompt, turn marks, the
answer. Reading a verdict out of it produced false greens and false refusals
(an echoed prompt's ACCEPT template; turn marks inside the answer -- K118). So
every run also passes `-o <FILE>` (`--output-last-message`), which makes codex
write ONLY its final message there, and the kernel receipt reads that file.
`--last-message` names it; omitted, it defaults to `<--out>.last.txt`, so every
documented invocation (`--out o.txt`) gains the file without changing, and no
run can be dispatched without one. A last-message path that is the `--out`
file (same resolved path, or the same file by os.path.samefile) is refused
before codex runs: the transcript would read as the final message. So is one
that is the `--prompt-file`, before anything is deleted: the stale-file delete
would remove the prompt before codex reads it. An `--out` that is the `--prompt-file`
(compared the same way) is refused first, before anything is deleted or written:
opening `--out` truncates it, so codex would read an empty prompt (K122). The path is made absolute before codex sees
it (codex runs with `-C <worktree>`), any stale file there is deleted BEFORE the
run (a previous run's answer must not stand in for this one's), and after the
run a missing, empty or whitespace-only file is a failure: `"last_message_ok": false`, a line on
stderr, and a non-zero exit, whatever the tier and exit code say.
K140 (K6 key round 1): the result also carries `last_message_sha256`, `sha256:<hex>` of the final-message file's
bytes read after the run (null when there is no file). tools/kernel-receipt.py ties the result to the verdict by
it: a result saved from an earlier run at the same path no longer vouches for a later run's final message.
K140 round 2: equal bytes are not the same run, so the result also carries `reviewed_head`, the full sha of HEAD in
`--cd` (`git -C <--cd> rev-parse HEAD`) read at the start of the run, null when it cannot be read; the receipt
requires it to be the landed merge.

A FAILED WINDOWS SANDBOX IS NOT RUN (K135)
------------------------------------------
On Windows a failed sandbox setup makes every shell call in `exec --sandbox read-only` fail while codex still exits 0
with a verdict (sibling cards on the doctrine bus: mlv-app 6020535 and e426a45, topbuilder-interface b825b4f): a key
that never read the tree. So the transcript (`--out`: codex's stdout and stderr) is checked for the one failure LINE a
card measured in full: e426a45's `windows sandbox failed: helper_unknown_error: setup refresh had errors`
(SANDBOX_FAILURE_LINE). A transcript line counts only when, stripped and case folded, it STARTS with that text: a line
codex emits. A line that merely contains a phrase (a file a review prints, a diff line, a fixture, a sentence of the
agent's commentary) starts with something else and is not a failure. A hit makes the tier `not_run`, a NOT RUN line on
stderr and a non-zero exit, whatever the exit code and the final message say. The prompt's first block (echoed once
after the banner) and the final message's last two blocks (printed after `codex` and after `tokens used`) are removed
first, so a prompt or an answer that quotes the line on a line of its own is not a failure. The shell-call counts in
the JSON line (`shell_calls`, `shell_succeeded`, `shell_failed`) are informational and never decide the tier: a call
may exit non-zero in a healthy review (rg with no match), and a status-shaped line inside a call's output is counted
as one. Not caught: a failure that prints any other text, or this text after a prefix (no card shows one). A command
that prints a copy of the measured line at the start of a line reads NOT RUN: a refused run, the safe side.

A FAILED, UNANSWERED RUN IS A STOP, NEVER A RETRY (K178; bus K154 packet 2, key round 3)
---------------------------------------------------------------------------------------
Whether the run was ANSWERED is read from structure only: the --last-message file exists, is not the --out file and
is NON-BLANK (some character other than whitespace; codex writes it only from the agent's final message). Turn-marker lines in the human transcript
(`thinking`, `codex`, `exec`) are never read for this: a command's output can print any of them.

A run that exited non-zero AND was not answered is a credential stop: `credential_refusal` and `credential_kind` are
both `unknown` in the JSON and the exit code stays 1. Its stderr line is CREDENTIAL STOP, except when the transcript
also shows the failed Windows sandbox: then stderr says NOT RUN instead (that check comes first), and the JSON still
carries `sandbox_failure` and both `unknown` fields. `unknown` means STOP AND ESCALATE to
the owner, never retry: a consumer project's wrapper must not re-run, re-authenticate or wait it out on its own.
Why never classified here: a credential or quota refusal can be classified only from a TYPED source, codex's JSON
event stream (`codex exec --json`: typed `error` / `turn.failed` events) or a stderr that carries nothing but codex's
own errors. This tool runs codex in human mode (its tier check reads the human banner), whose transcript mixes codex's
lines with every command's output, so no reading of it can tell codex's error from a command's (key rounds 1-3 of
K178 and three rounds of the bus key found such evasions: `thinking` or `codex` printed by a command, `status 4013`,
`billing.txt`). Until a typed source is wired (a follow-up that needs one live run to record the event shapes), every
failed, unanswered run is `unknown`. When one is wired, its error text is matched only by the strictly anchored
patterns `\bHTTP (401|403)\b`, `\b(401 Unauthorized|403 Forbidden)\b`, `\btoken (expired|revoked)\b`,
`\binsufficient_quota\b`, `\bquota exceeded\b`, `\bbilling hard limit\b` (auth for the first three, quota for the
rest), and anything else stays `unknown`.

The two keys are in the JSON ONLY on such a stop (every other run's line is byte-identical to the line before K178).
A stop never makes a run pass.

THE TIER IS RESOLVED AT LAUNCH, NEVER PINNED AS AN ID (K180; owner ruling 2026-10-22; bus R16.2)
------------------------------------------------------------------------------------------------
A role names a tier (`sol`, `astra`, `luna`) and an effort (always `high`); resolve_tier() turns the tier into the
newest numeric `gpt-<version>-<tier>` id that $CODEX_HOME/models_cache.json (default ~/.codex) lists as visible and
supporting that effort, when the cache is at most 7 days old, and stores it as the tier's last-good id beside the cache
($CODEX_HOME/codex-review-last-good.json). With no usable cache the last-good id is used and the result says so
(`resolution: fallback`, `resolution_reason`, `stale`); with neither, the run is refused (exit 2). The banner read-back
below stays the authority on what actually ran. The result line also carries model_requested (the selector),
model_effective (the banner's id), effort_requested, effort_effective, tokens_used (the transcript's `tokens used`
total, null when absent), `measurement` (the schemas/provider-usage-event-v1.schema.json names; token splits null,
never estimated; active_seconds), `outcome` (APPROVED, CHANGES_REQUESTED, REFUSED, UNKNOWN from the final message's last
line) and `verdict` (that raw line). They follow every key bus master printed, ahead of the two K178 credential keys.

NEVER `-p`/`--profile`. A profile is a name that resolves against the config
file this tool exists to route AROUND; passing one would silently reintroduce
the exact ambient dependency being removed here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ROLES is the single source of truth for the tier table. A role names a TIER and an effort, never a model id (K180,
# owner ruling 2026-10-22; bus R16.2): the id is resolved at launch by resolve_tier() below. The doc sentence in
# docs/operating-contract-model-routing.md is pinned against this dict, in both directions, by
# tools/codex-review.tests.py -- change one without the other and that test goes red.
#   swarm       read-only pre-key and authority seats      sol / high
#   counterpart the key                                    sol / high
#   sweep       occasional diversity of thought, no gate   astra / high
#   census      mechanical census only                     luna / high
ROLES: dict[str, tuple[str, str]] = {
    "swarm": ("sol", "high"),
    "counterpart": ("sol", "high"),
    "sweep": ("astra", "high"),
    "census": ("luna", "high"),
}

# R16.2: the models cache may be at most this old for a resolution to count as read from the cache.
CACHE_MAX_AGE = timedelta(days=7)
CACHE_NAME = "models_cache.json"
LAST_GOOD_NAME = "codex-review-last-good.json"
_SLUG_RE = re.compile(r"gpt-(\d+(?:\.\d+)*)-([a-z]+)")
# The owner's stated default per tier (ruling 2026-10-22: sol -> gpt-6.1-sol). A FLOOR that only REPORTS: an id older
# than it is flagged `stale` (Conjugal request 1), but the floor never selects an id -- a floor newer than anything
# visible must not change which id launches. Raise it with a new owner ruling.
OWNER_DEFAULT_FLOOR: dict[str, str] = {"sol": "gpt-6.1-sol"}

_BANNER_RE = re.compile(r"OpenAI Codex v\S+")
_SEPARATOR = "--------"


SANDBOX = "read-only"

# The one Windows sandbox-failure line a sibling card measured in full (K135; mlv-app e426a45: "every shell call in a
# read-only exec failed with" it). The other measured phrases (the bare setup-refresh phrase, 6020535 and b825b4f; the
# open-ACL validation error, 6020535) were reported inside prose with no line shape, so they cannot be anchored and are
# not matched. A transcript line counts when, stripped and case folded, it STARTS with this text. Built from pieces so
# this file and its diff never print it at the start of a line.
SANDBOX_FAILURE_LINE = "windows sandbox" + " failed: helper_unknown_error: " + "setup refresh" + " had errors"  # e426a45


def read_banner(text: str) -> dict[str, str] | None:
    """The run's own printed banner as {key: value} -- and ONLY the banner.

    codex-cli 0.157.1 prints `OpenAI Codex v<version>`, a `--------` line, `key: value` lines, a closing
    `--------`, and only then echoes the prompt. Searching the whole transcript let a prompt that merely
    NAMES a model stand in for the banner (Codex seat, K32 r1). So the first line must be the banner and only
    lines before the closing separator count; a banner that never closes is no banner (None)."""
    lines = text.splitlines()
    if len(lines) < 2 or not _BANNER_RE.fullmatch(lines[0].strip()) or lines[1].strip() != _SEPARATOR:
        return None
    fields: dict[str, str] = {}
    for line in lines[2:]:
        line = line.strip()
        if line == _SEPARATOR:
            return fields
        key, sep, value = line.partition(": ")
        if sep and value:
            fields.setdefault(key, value)
    return None


def read_header(text: str) -> tuple[str | None, str | None]:
    banner = read_banner(text) or {}
    return banner.get("model"), banner.get("reasoning effort")


def requested(role: str, model: str) -> dict[str, str]:
    """EVERY property the dispatch asks for, keyed as the banner prints it. Verification compares all of them, so a
    property added to the request cannot go unverified -- the r2 hole was the one field (sandbox) no one compared.
    `model` is the id resolved at launch for the role's tier (K180)."""
    _tier, effort = ROLES[role]
    return {"model": model, "reasoning effort": effort, "sandbox": SANDBOX}


def codex_home() -> Path:
    """Codex's own state directory: $CODEX_HOME (the variable codex itself reads), else ~/.codex."""
    env = os.environ.get("CODEX_HOME")
    return Path(env) if env else Path.home() / ".codex"


def _version(slug: str) -> tuple[int, ...]:
    return tuple(int(x) for x in _SLUG_RE.fullmatch(slug).group(1).split("."))


def _supports(model: dict, effort: str) -> bool:
    levels = model.get("supported_reasoning_levels")
    if not isinstance(levels, list):
        return False
    return any((item.get("effort") if isinstance(item, dict) else item) == effort for item in levels)


def _parse_time(text: object) -> datetime | None:
    """An RFC 3339 instant; the models cache writes nanoseconds, which datetime cannot hold, so the fraction is cut to 6."""
    if not isinstance(text, str):
        return None
    m = re.fullmatch(r"(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)(?:\.(\d+))?(Z|[+-]\d\d:\d\d)", text.strip())
    if not m:
        return None
    frac = (m.group(2) or "0")[:6].ljust(6, "0")
    zone = "+00:00" if m.group(3) == "Z" else m.group(3)
    try:
        return datetime.fromisoformat(f"{m.group(1)}.{frac}{zone}")
    except ValueError:
        return None


def _floor_finding(tier: str, model: str) -> str | None:
    """The finding when `model` is older than the owner's default for its tier, else None. Reports only."""
    floor = OWNER_DEFAULT_FLOOR.get(tier)
    if floor is not None and _version(model) < _version(floor):
        return f"resolved {model} is older than the owner default {floor} (ruling 2026-10-22)"
    return None


def _read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def resolve_tier(tier: str, effort: str, home: Path | None = None, now: datetime | None = None) -> dict:
    """Resolve a tier selector (`sol`) to a concrete model id at launch (bus R16.2, K180).

    From the local models cache ($CODEX_HOME/models_cache.json): the NEWEST numeric `gpt-<version>-<tier>` slug (versions
    compared as number tuples, so 6.10 beats 6.9) that the cache lists as visible (`visibility: list`) and that supports
    `effort`, when the cache's `fetched_at` is at most 7 days old. A success is stored as the tier's last-good id
    ($CODEX_HOME/codex-review-last-good.json). When the cache is missing, unreadable, older than 7 days, or lists no
    such slug, the last-good id for the tier is used and the result says so (`resolution: fallback`, with the reason);
    with no last-good id either, ValueError: the tool never invents an id, and holds no literal id in code that could
    silently age.

    `stale` is None, or the finding: a fallback was used, or the id is older than a newer `gpt-<version>-<tier>` the
    cache lists (listed but hidden or without the effort). Never silently keep the older id (Conjugal request, K180).
    Returns {model, resolution, reason, stale}."""
    home = home if home is not None else codex_home()
    now = now or datetime.now(timezone.utc)
    cache = _read_json(home / CACHE_NAME)
    models = cache.get("models") if isinstance(cache, dict) else None
    slugs = [m for m in models if isinstance(m, dict) and isinstance(m.get("slug"), str)
             and _SLUG_RE.fullmatch(m["slug"]) and _SLUG_RE.fullmatch(m["slug"]).group(2) == tier] \
        if isinstance(models, list) else []
    newest_listed = max(slugs, key=lambda m: _version(m["slug"]))["slug"] if slugs else None
    fetched = _parse_time(cache.get("fetched_at")) if isinstance(cache, dict) else None

    reason: str | None = None
    if not isinstance(models, list):
        reason = f"{CACHE_NAME} is missing or unreadable"
    elif fetched is None:
        reason = f"{CACHE_NAME} has no readable fetched_at"
    elif now - fetched > CACHE_MAX_AGE:
        reason = f"{CACHE_NAME} fetched_at {cache['fetched_at']} is more than {CACHE_MAX_AGE.days} days old"
    else:
        usable = [m for m in slugs if m.get("visibility") == "list" and _supports(m, effort)]
        if usable:
            best = max(usable, key=lambda m: _version(m["slug"]))["slug"]
            _store_last_good(home, tier, best, effort)
            stale = None
            if newest_listed is not None and _version(newest_listed) > _version(best):
                stale = (f"resolved {best} is older than {newest_listed}, which the cache lists but not as visible "
                         f"with {effort} effort")
            floor = _floor_finding(tier, best)
            if floor is not None:
                stale = floor if stale is None else f"{stale}; {floor}"
            return {"model": best, "resolution": "cache", "reason": None, "stale": stale}
        reason = f"{CACHE_NAME} lists no visible gpt-<version>-{tier} model supporting {effort}"

    last = _read_json(home / LAST_GOOD_NAME)
    entry = last.get(tier) if isinstance(last, dict) else None
    model = entry.get("model") if isinstance(entry, dict) else None
    if not isinstance(model, str) or not _SLUG_RE.fullmatch(model) or _SLUG_RE.fullmatch(model).group(2) != tier:
        raise ValueError(f"cannot resolve tier {tier!r} at {effort}: {reason}, and {home / LAST_GOOD_NAME} records no "
                         f"last-good id for it (run any codex command once to refresh the cache, or restore the file)")
    stale = f"fallback to the last-good {model}: {reason}; a newer {tier} model may exist"
    floor = _floor_finding(tier, model)
    if floor is not None:
        stale += f"; {floor}"
    return {"model": model, "resolution": "fallback", "reason": reason, "stale": stale}


def _store_last_good(home: Path, tier: str, model: str, effort: str) -> None:
    """Record the id a cache resolution picked, atomically; best effort (an unwritable state directory costs only the
    fallback for a later launch, never this one)."""
    path = home / LAST_GOOD_NAME
    state = _read_json(path)
    state = state if isinstance(state, dict) else {}
    if isinstance(state.get(tier), dict) and state[tier].get("model") == model and state[tier].get("effort") == effort:
        return
    state[tier] = {"model": model, "effort": effort,
                   "recorded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    tmp = path.with_name(path.name + f".{os.getpid()}.tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_text(json.dumps(state, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        os.replace(tmp, path)
    except OSError:
        tmp.unlink(missing_ok=True)


_VERDICT_RE = re.compile(r"VERDICT: (ACCEPT|REJECT|REFUSE)\b")
_OUTCOMES = {"ACCEPT": "APPROVED", "REJECT": "CHANGES_REQUESTED", "REFUSE": "REFUSED"}


def read_verdict(final_message: str) -> tuple[str, str | None]:
    """(outcome, raw verdict line) from the final message's LAST non-blank line: `VERDICT: ACCEPT|REJECT|REFUSE ...`
    reads APPROVED, CHANGES_REQUESTED, REFUSED; anything else is UNKNOWN with no line. Names follow
    schemas/provider-usage-event-v1.schema.json `outcome`."""
    lines = [line.strip() for line in final_message.splitlines() if line.strip()]
    if lines:
        m = _VERDICT_RE.match(lines[-1])
        if m:
            return _OUTCOMES[m.group(1)], lines[-1]
    return "UNKNOWN", None


def tokens_used(transcript: str, final_message: str) -> int | None:
    """The run's reported total, read ONLY from codex's trailer position (K180, K6 key round 2): codex ends a run with
    `tokens used`, the count, then the final message echoed once as the LAST block. One trailing copy of the final
    message is removed from the END (a non-empty answer whose echo ends the transcript is required: with no answer, or no
    such echo, the result is None); the last two non-blank lines must then be `tokens used` and a count.
    Anything else is None -- a pair in the prompt, in shell output or inside the answer is never the run's report, and
    nothing scans the transcript for one. Never estimated. A total is not an input/output split, so the split fields of
    `measurement` stay None."""
    lines = [line.strip() for line in transcript.splitlines()]
    while lines and not lines[-1]:
        lines.pop()
    block = _block(final_message)
    if not block or len(lines) < len(block) or lines[-len(block):] != block:
        return None               # no answer, or no echo of it ending the transcript: nothing anchors a trailer
    del lines[-len(block):]
    tail = [line for line in lines if line][-2:]
    if len(tail) == 2 and tail[0] == "tokens used":
        m = re.fullmatch(r"\d{1,3}(?:,\d{3})+|\d+", tail[1])
        if m:
            return int(m.group(0).replace(",", ""))
    return None


def usage_fields(role: str, actual_model: str | None, actual_effort: str | None, resolution: dict,
                 active_seconds: float | None, total_tokens: int | None, final_message: str) -> dict:
    """The K180 result-line fields, named after schemas/provider-usage-event-v1.schema.json wherever it has one:
    model_requested (the selector), model_effective (the id the run's own banner reports), effort_requested,
    effort_effective, outcome, and a `measurement` object. Token fields not reported are None, never guessed."""
    tier, effort = ROLES[role]
    outcome, verdict = read_verdict(final_message)
    measurement = {
        "quality": "unknown" if active_seconds is None and total_tokens is None else "mixed",
        "source": "codex-review",
        "input_tokens": None, "cached_input_tokens": None, "reasoning_tokens": None, "output_tokens": None,
        "active_seconds": active_seconds,
    }
    return {
        "model_requested": tier,
        "model_effective": actual_model,
        "effort_requested": effort,
        "effort_effective": actual_effort,
        "resolution": resolution["resolution"],
        "resolution_reason": resolution["reason"],
        "stale": resolution["stale"],
        "tokens_used": total_tokens,
        "measurement": measurement,
        "outcome": outcome,
        "verdict": verdict,
    }


def default_last_message(out_path: str) -> str:
    return str(out_path) + ".last.txt"


def same_file(a: Path, b: Path) -> bool:
    """One file under two names? The file system decides wherever it can answer. WindowsPath equality folds case, and in
    a Windows case-sensitive directory `prompt.md` and `PROMPT.MD` are two files (K6 key on 098e118 and 748cef0).
    - Both names exist: os.path.samefile (links, other spellings, another case on an ordinary directory). If samefile
      raises (a name vanished in between, or the file system cannot say), the names are refused as one: a refused run,
      never a destroyed file (ledger limit N3).
    - One exists and the other does not: two files, since one file would be found under both names.
    - Neither exists yet: names that resolve to the same path, case folded, are refused as one (a conservative refusal;
      the tool does not read the directory's case-sensitivity flag; ledger limit N2). run_review refuses a missing
      prompt first, so the `--out` and `--prompt-file` guard never reaches this branch."""
    ea, eb = os.path.exists(a), os.path.exists(b)
    if ea and eb:
        try:
            return os.path.samefile(a, b)
        except OSError:
            return True
    if ea or eb:
        return False
    return a.resolve() == b.resolve()


def _block(text: str) -> list[str]:
    """`text` as stripped lines, leading and trailing blank lines dropped: the shape it has inside a transcript."""
    lines = [line.strip() for line in text.splitlines()]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return lines


def _remove_blocks(lines: list[str], block: list[str], limit: int, from_end: bool) -> list[str]:
    """Remove up to `limit` runs of `lines` that equal `block` line for line (stripped), the first ones or the last."""
    n = len(block)
    if n == 0 or limit <= 0:
        return lines
    starts: list[int] = []
    i = 0
    while i + n <= len(lines):
        if lines[i].strip() == block[0] and [line.strip() for line in lines[i:i + n]] == block:
            starts.append(i)
            i += n
        else:
            i += 1
    chosen = set(starts[-limit:] if from_end else starts[:limit])
    out: list[str] = []
    i = 0
    while i < len(lines):
        if i in chosen:
            i += n
        else:
            out.append(lines[i])
            i += 1
    return out


_STATUS_RE = re.compile(r"\s*(?:(succeeded)|exited (-?\d+)) in \S+:\s*")


def shell_calls(transcript: str, prompt: str = "", final_message: str = "") -> dict:
    """The run's sandbox-failure line, if any, and informational shell-call counts (K135, round 2).

    Returns {"calls": lone `exec` lines, "succeeded": n, "failed": n, "failure": str | None}. `failure` is the first
    transcript line that, stripped and case folded, starts with SANDBOX_FAILURE_LINE. The counts never decide it: a
    healthy call may exit non-zero, and a status-shaped line printed by a command is counted too. The prompt's first
    block and the final message's last two blocks are removed first, line for line, so a quotation of the line on a line
    of its own in either is not a failure."""
    lines = transcript.splitlines()
    lines = _remove_blocks(lines, _block(prompt), 1, from_end=False)
    lines = _remove_blocks(lines, _block(final_message), 2, from_end=True)
    anchor = SANDBOX_FAILURE_LINE.casefold()
    calls = succeeded = failed = 0
    hit: str | None = None
    for line in lines:
        key = line.strip()
        status = _STATUS_RE.fullmatch(line)
        if status:
            ok = status.group(1) is not None or int(status.group(2)) == 0
            succeeded += ok
            failed += not ok
        elif key == "exec":
            calls += 1
        elif hit is None and key.casefold().startswith(anchor):
            hit = key
    return {"calls": calls, "succeeded": succeeded, "failed": failed, "failure": hit}


# K178, bus K154 packet 2 key round 3: the stop is decided from structure only (exit code, final-message file).
UNKNOWN = "unknown"


def credential_refusal(returncode: int, answered: bool) -> tuple[str, str] | None:
    """(kind, refusal) for a failed (non-zero exit), unanswered (no final message) run, else None. Both are
    `unknown`: with no typed event stream there is nothing safe to classify from (see the module doc), so the caller
    stops and escalates. No transcript text is read."""
    if returncode != 0 and not answered:
        return UNKNOWN, UNKNOWN
    return None


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def reviewed_head(cd: str) -> str | None:
    """K140 round 2: the full sha of HEAD in the reviewed worktree, read before codex runs; None when unreadable."""
    try:
        proc = subprocess.run(["git", "-C", cd, "rev-parse", "HEAD"], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    head = proc.stdout.strip()
    return head if proc.returncode == 0 and re.fullmatch(r"[0-9a-f]{40}", head) else None


def last_message_sha256(path: Path) -> str | None:
    """K140: `sha256:<hex>` of the final-message file's bytes as the run left them; None when there is no file."""
    try:
        return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def last_message_ok(path: Path) -> bool:
    """The final-message file exists and says something: absent or blank is no answer."""
    try:
        return path.is_file() and path.read_text(encoding="utf-8", errors="replace").strip() != ""
    except OSError:
        return False


def build_argv(codex_path: str, model: str, effort: str, cd: str, last_message: str) -> list[str]:
    return [
        codex_path,
        "exec",
        "--sandbox",
        SANDBOX,
        "-m",
        model,
        "-c",
        f"model_reasoning_effort={effort}",
        "-C",
        cd,
        "-o",
        last_message,
        "-",
    ]


def run_review(role: str, cd: str, prompt_file: str, out_path: str, last_message: str | None = None) -> dict:
    if role not in ROLES:
        raise ValueError(f"unknown --role {role!r}; must be one of {sorted(ROLES)}")
    tier, effort = ROLES[role]
    # A review without its prompt is no review, and every guard below relies on the prompt existing (K6 key on
    # 3b28903): refused first, before anything is deleted or written.
    if not Path(prompt_file).is_file():
        raise ValueError(f"--prompt-file {Path(prompt_file).resolve()} is not an existing file")
    # Opening --out for writing truncates it, and the no-codex branch writes it empty: one file for both would empty
    # the prompt before codex reads it (K122). Refused first, before anything is deleted or written.
    if same_file(Path(out_path), Path(prompt_file)):
        raise ValueError(f"--out {Path(out_path).resolve()} is the --prompt-file; they must be different files")
    last_path = Path(last_message or default_last_message(out_path)).resolve()
    # The transcript in --out is never a final message: one file for both would read the transcript as the
    # verdict, and would read "ok" even when codex wrote no final message at all (K119 round 1).
    if same_file(last_path, Path(out_path)):
        raise ValueError(f"--last-message {last_path} is the --out transcript file; they must be different files")
    # The stale-file delete below would delete the prompt before codex reads it (K6 key, K119 landing 34c2e5c).
    if same_file(last_path, Path(prompt_file)):
        raise ValueError(f"--last-message {last_path} is the --prompt-file; they must be different files")
    # A previous run's answer must never stand in for this one's.
    last_path.unlink(missing_ok=True)
    head = reviewed_head(cd)                   # K140 round 2: the commit this run reviews, read at its start
    resolution = resolve_tier(tier, effort)    # K180, R16.2: the tier's id, resolved now (ValueError: refused, exit 2)
    model = resolution["model"]

    codex_path = shutil.which("codex")
    if codex_path is None:
        result = {
            "role": role,
            "requested_model": model,
            "requested_effort": effort,
            "actual_model": None,
            "actual_effort": None,
            "exit": 127,
            "out": str(out_path),
            "tier": "unobserved",
            "last_message": str(last_path),
            "last_message_ok": False,
            "last_message_sha256": None,
            "reviewed_head": head,
            "sandbox_failure": None,
            "shell_calls": 0,
            "shell_succeeded": 0,
            "shell_failed": 0,
            **usage_fields(role, None, None, resolution, None, None, ""),
        }
        Path(out_path).write_text("", encoding="utf-8")
        return result

    argv = build_argv(codex_path, model, effort, cd, str(last_path))

    started = time.monotonic()
    with open(prompt_file, "rb") as prompt_stream, open(out_path, "wb") as out_stream:
        proc = subprocess.run(
            argv,
            stdin=prompt_stream,
            stdout=out_stream,
            stderr=subprocess.STDOUT,
        )

    active_seconds = round(time.monotonic() - started, 3)
    out_text = Path(out_path).read_text(encoding="utf-8", errors="replace")
    banner = read_banner(out_text)
    want = requested(role, model)

    if banner is None or any(key not in banner for key in want):
        tier = "unobserved"
    elif any(banner[key] != value for key, value in want.items()):
        tier = "mismatch"
    else:
        tier = "ok"
    # A failed sandbox read nothing: not_run, whatever the banner, the exit code and the final message say (K135).
    shell = shell_calls(out_text, _read(Path(prompt_file)), _read(last_path))
    failure = shell["failure"]
    if failure is not None:
        tier = "not_run"
    seen = banner or {}
    answered = last_message_ok(last_path) and not same_file(last_path, Path(out_path))
    # K178, bus K154 packet 2 key round 3: a failed, unanswered run is a stop, decided from structure only.
    refusal = credential_refusal(proc.returncode, answered)

    result = {
        "role": role,
        "requested_model": model,
        "requested_effort": effort,
        "requested_sandbox": SANDBOX,
        "actual_model": seen.get("model"),
        "actual_effort": seen.get("reasoning effort"),
        "actual_sandbox": seen.get("sandbox"),
        "exit": proc.returncode,
        "out": str(out_path),
        "tier": tier,
        "last_message": str(last_path),
        "last_message_ok": answered,
        "last_message_sha256": last_message_sha256(last_path),
        "reviewed_head": head,
        "sandbox_failure": failure,
        "shell_calls": shell["calls"],
        "shell_succeeded": shell["succeeded"],
        "shell_failed": shell["failed"],
        **usage_fields(role, seen.get("model"), seen.get("reasoning effort"), resolution, active_seconds,
                       tokens_used(out_text, _read(last_path)), _read(last_path)),
    }
    # Bus key on K154 packet 2, finding 2: the two K178 keys exist ONLY on a credential stop, appended after the
    # others, so every other run's JSON line is byte-compatible with the result before K178.
    if refusal:
        result["credential_refusal"], result["credential_kind"] = refusal[1], refusal[0]
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Dispatch a codex exec review with an explicit, recorded model/effort tier."
    )
    ap.add_argument("--role", required=True, choices=sorted(ROLES), help="review role/tier")
    ap.add_argument("--cd", required=True, help="pinned review worktree passed to codex -C")
    ap.add_argument("--prompt-file", required=True, help="file whose contents become codex's stdin prompt")
    ap.add_argument("--out", required=True, help="file to write codex's combined stdout/stderr to")
    ap.add_argument(
        "--last-message",
        default=None,
        help="file codex writes its final message to (codex exec -o); default <--out>.last.txt",
    )
    args = ap.parse_args(argv)

    try:
        result = run_review(args.role, args.cd, args.prompt_file, args.out, args.last_message)
    except ValueError as exc:
        print(f"codex-review: refused: {exc}", file=sys.stderr)
        return 2
    # The path line first: callers read the JSON from the LAST line.
    print(f"last message: {result['last_message']}")
    print(json.dumps(result))

    if result["sandbox_failure"] is not None:
        print(f"codex-review: NOT RUN: the transcript {result['out']} shows a failed Windows sandbox "
              f"({result['sandbox_failure']!r}; shell calls {result['shell_calls']}, succeeded "
              f"{result['shell_succeeded']}, failed {result['shell_failed']}): the review could not read the tree, "
              f"whatever its verdict says", file=sys.stderr)
        return 1
    if result.get("credential_refusal") is not None:
        print(f"codex-review: CREDENTIAL STOP ({result['credential_kind']}): codex exited {result['exit']} with no final "
              f"message (transcript {result['out']}); the cause is not classified without a typed event stream: STOP "
              f"AND ESCALATE to the owner, never retry and never re-authenticate from a script", file=sys.stderr)
        return 1
    if not result["last_message_ok"]:
        print(f"codex-review: no final message at {result['last_message']} (missing, empty or whitespace only)", file=sys.stderr)
        return 1
    if result["tier"] != "ok":
        return 1
    return 0 if result["exit"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
