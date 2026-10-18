#!/usr/bin/env python3
"""Dispatch one `codex exec` review with an EXPLICIT, RECORDED model/effort tier.

    python tools/codex-review.py --role swarm       --cd <worktree> --prompt-file p.md --out o.txt
    python tools/codex-review.py --role counterpart --cd <worktree> --prompt-file p.md --out o.txt
    python tools/codex-review.py --role sweep       --cd <worktree> --prompt-file p.md --out o.txt

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
run a missing or empty file is a failure: `"last_message_ok": false`, a line on
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

A CREDENTIAL REFUSAL IS NAMED, NEVER RETRIED (K178)
-------------------------------------------------
On a FAILED run only (codex exit non-zero, or no final message), `credential_refusal` is the transcript's last line
of a run that never got a model response (no `exec`, `codex` or `thinking` mark, so no shell output can be in it)
when that line is in codex's own error shape
(`ERROR: ...` or `stream error: ...`, optionally after a bracketed timestamp) that names an HTTP 401 or 403,
an expired token, unauthorized, an API key, a sign-in, a usage limit, a quota or billing, with the prompt block and
the final-message blocks removed first (as for the sandbox line); `credential_kind` is `auth` or `quota`. The two
keys are in the JSON ONLY on such a stop (every other run's line keeps the earlier keys, byte for byte). A CREDENTIAL
STOP line goes to stderr; the exit code is unchanged (1). It never makes a run pass. A project's admitted-key wrapper
(Cloudvore's is tools/codex-key-admitted.ps1) turns it into a standing stop: an `auth` stop until the owner
re-authenticates, a `quota` stop for six hours.

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
from pathlib import Path

# ROLES is the single source of truth for the tier table. The doc sentence in
# docs/operating-contract-model-routing.md is pinned against this dict, in
# both directions, by tools/codex-review.tests.py -- change one without the
# other and that test goes red.
ROLES: dict[str, tuple[str, str]] = {
    "swarm": ("gpt-6-luna", "low"),
    "counterpart": ("gpt-6-sol", "high"),
    "sweep": ("gpt-6-astra", "high"),
}

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


def requested(role: str) -> dict[str, str]:
    """EVERY property the dispatch asks for, keyed as the banner prints it. Verification compares all of them, so a
    property added to the request cannot go unverified -- the r2 hole was the one field (sandbox) no one compared."""
    model, effort = ROLES[role]
    return {"model": model, "reasoning effort": effort, "sandbox": SANDBOX}


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


# K178: what a Codex refusal on credentials, quota or billing prints. Matched only on a FAILED run (exit non-zero or no
# final message), only on the transcript's LAST line, only in codex's own error shape (`ERROR: ...` or `stream error: ...`, optionally after a
# bracketed timestamp), and only after the echoed prompt block and the final message blocks are removed (the same
# removal as shell_calls). A shell call's output (a file that names "401 Unauthorized", a grep for "billing") is not in
# that shape, and a review that merely discusses a refusal and succeeds is never classified. Measured: "You've hit your
# usage limit. Visit https://chatgpt.com/codex/settings/usage ..." (a codex rollout error, 2026-08); "401 Unauthorized:
# Incorrect API key provided" (2026-09-25); bus key 2026-10-18: "HTTP 401: token expired". Two kinds: `auth` (the owner re-authenticates) and `quota` (a usage limit or
# billing refusal, which passes with time or money). A hit names a stop; it never makes a run pass. Not caught: a refusal
# printed in any other shape reads as an ordinary failure (the run still fails; nothing lands).
CREDENTIAL_MARKERS: dict[str, tuple[str, ...]] = {
    "auth": ("401 unauthorized", "status 401", "incorrect api key", "invalid api key", "invalid_api_key",
             "sign in again", "log in again", "codex login", "refresh token", "unauthorized", "forbidden",
             "token expired", "token has expired", "expired token", "token_expired"),
    "quota": ("usage limit", "insufficient_quota", "quota exceeded", "exceeded your current quota", "billing"),
}
_ANSWER_MARKS = ("exec", "codex", "thinking")    # any of these means the model answered (and shell output may follow)
# Bus key on K154 packet 2, finding 3: any HTTP 401 or 403 in codex's error line is an auth refusal (a whole number:
# not 4013, not 404).
_AUTH_STATUS_RE = re.compile(r"(?<![0-9])40[13](?![0-9])")
_ERROR_LINE_RE = re.compile(r"(?:\[[^\]]*\]\s*)?(?:error|stream error):", re.I)


def credential_refusal(transcript: str, prompt: str = "", final_message: str = "") -> tuple[str, str] | None:
    """K178: (kind, line) when the run never got a model response and the transcript's LAST non-blank line (after
    the prompt and final-message blocks are removed) is a codex error line naming a credential, quota or billing
    refusal, else None. Call on a failed run only."""
    lines = transcript.splitlines()
    lines = _remove_blocks(lines, _block(prompt), 1, from_end=False)
    lines = _remove_blocks(lines, _block(final_message), 2, from_end=True)
    lines = [line.strip() for line in lines if line.strip()]
    # Key rounds 1-3 (three findings in one class, closed by construction): a command's output is printed raw, and turn
    # marks are ordinary lines a command can print, so no reading of a run that reached the model can tell codex's error
    # from a command's. A refusal counts only when the run never got a model response: no `exec`, `codex` or `thinking`
    # mark at all, hence no shell output in the transcript. A mid-run limit reads as an ordinary failure; the next run is
    # refused at its first request and stops there.
    if not lines or any(line.casefold() in _ANSWER_MARKS for line in lines) or not _ERROR_LINE_RE.match(lines[-1]):
        return None
    folded = lines[-1].casefold()
    if _AUTH_STATUS_RE.search(folded):
        return "auth", lines[-1]
    for kind, markers in CREDENTIAL_MARKERS.items():
        if any(marker in folded for marker in markers):
            return kind, lines[-1]
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
    model, effort = ROLES[role]
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
        }
        Path(out_path).write_text("", encoding="utf-8")
        return result

    argv = build_argv(codex_path, model, effort, cd, str(last_path))

    with open(prompt_file, "rb") as prompt_stream, open(out_path, "wb") as out_stream:
        proc = subprocess.run(
            argv,
            stdin=prompt_stream,
            stdout=out_stream,
            stderr=subprocess.STDOUT,
        )

    out_text = Path(out_path).read_text(encoding="utf-8", errors="replace")
    banner = read_banner(out_text)
    want = requested(role)

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
    # K178: on a failed run only, the line that says the account was refused (credentials, quota, billing).
    refusal = None
    if proc.returncode != 0 or not answered:
        refusal = credential_refusal(out_text, _read(Path(prompt_file)), _read(last_path))

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
        print(f"codex-review: CREDENTIAL STOP ({result['credential_kind']}): {result['credential_refusal']!r} in "
              f"{result['out']}: the account was refused; never re-authenticate from a script", file=sys.stderr)
        return 1
    if not result["last_message_ok"]:
        print(f"codex-review: no final message at {result['last_message']} (missing or empty)", file=sys.stderr)
        return 1
    if result["tier"] != "ok":
        return 1
    return 0 if result["exit"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
