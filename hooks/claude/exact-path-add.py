#!/usr/bin/env python3
"""PreToolUse hook (Bash / PowerShell): refuse sweeping git stages -- add exact paths only.

In a checkout shared by several agents, `git add -A` / `git add .` / `git add -u` / `git commit -a`
stage a PEER's half-finished files into your commit. The rule is "git add <exact paths>, then a bare
git commit". This hook enforces it on the command text before the shell sees it.

Refused (exit 2, reason on stderr -> shown to the agent):
    git add|stage   -A  --all  -u  --update  --no-ignore-removal  (also inside a short cluster, -Av)
                    or a sweeping pathspec: .  ./  :/  :/*  *  :(top)
    git commit      -a  --all  (also clustered: -am, -va) or a sweeping pathspec (. ./ :/ *)
Allowed: everything else, including `git add -- path/a path/b`, `git add -p file`, `git commit -m`.

The command is tokenised like a POSIX shell (quotes, escapes, ; && || | & newlines, $( ), backticks,
comments, heredoc bodies skipped), so `echo "git add -A"` or a heredoc commit message never trips it.
Stdin: the Claude Code hook payload. Exit 0 allow, 2 refuse. Stdlib only; one file, no imports
from siblings (it runs as a single pinned blob).
"""
from __future__ import annotations

import json
import re
import sys

SEPARATORS = {";", "&&", "||", "|", "&", "\n", "(", ")", "$(", "`", "|&", ";;"}
WRAPPERS = {"command", "exec", "time", "nohup", "sudo", "builtin", "noglob", "&"}
GIT_VALUE_OPTS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--super-prefix", "--config-env", "--list-cmds"}
ASSIGN = re.compile(r"^(?:\$env:)?[A-Za-z_][A-Za-z0-9_]*=")


def tokenize(cmd: str) -> list[list[str]]:
    """Split a shell command into segments of words (best effort, never raises)."""
    segs: list[list[str]] = [[]]
    word: list[str] = []
    in_word = False
    heredocs: list[tuple[str, bool]] = []
    pending_heredoc = None
    i, n = 0, len(cmd)

    def end_word():
        nonlocal word, in_word, pending_heredoc
        if in_word:
            w = "".join(word)
            if pending_heredoc is not None:
                heredocs.append((w, pending_heredoc))
                pending_heredoc = None
            else:
                segs[-1].append(w)
        word, in_word = [], False

    def sep(tok: str):
        end_word()
        if segs[-1]:
            segs.append([])

    while i < n:
        c = cmd[i]
        if c == "\n":
            end_word()
            sep("\n")
            i += 1
            while heredocs:  # skip heredoc bodies line by line until each delimiter
                delim, strip = heredocs.pop(0)
                while i < n:
                    j = cmd.find("\n", i)
                    line = cmd[i:] if j < 0 else cmd[i:j]
                    i = n if j < 0 else j + 1
                    if (line.lstrip("\t") if strip else line).rstrip("\r") == delim:
                        break
            continue
        if c in " \t\r":
            end_word()
            i += 1
            continue
        if c == "#" and not in_word:
            j = cmd.find("\n", i)
            i = n if j < 0 else j
            continue
        if c == "'":
            in_word = True
            j = cmd.find("'", i + 1)
            word.append(cmd[i + 1:] if j < 0 else cmd[i + 1:j])
            i = n if j < 0 else j + 1
            continue
        if c == '"':
            in_word = True
            i += 1
            while i < n and cmd[i] != '"':
                if cmd[i] == "\\" and i + 1 < n and cmd[i + 1] in '"\\$`\n':
                    word.append(cmd[i + 1])
                    i += 2
                else:
                    word.append(cmd[i])
                    i += 1
            i += 1
            continue
        if c == "\\" and i + 1 < n:
            in_word = True
            if cmd[i + 1] != "\n":
                word.append(cmd[i + 1])
            i += 2
            continue
        if cmd.startswith("<<", i) and not cmd.startswith("<<<", i):
            end_word()
            strip = cmd.startswith("<<-", i)
            i += 3 if strip else 2
            while i < n and cmd[i] in " \t":
                i += 1
            pending_heredoc = strip
            continue
        two = cmd[i:i + 2]
        if two in ("&&", "||", "$(", "|&", ";;"):
            sep(two)
            i += 2
            continue
        if c in ";|&()`":
            sep(c)
            i += 1
            continue
        in_word = True
        word.append(c)
        i += 1
    end_word()
    return [s for s in segs if s]


def git_invocation(seg: list[str]):
    """(env assignments, git global options, subcommand, args) or None when the segment is not git."""
    env, k = [], 0
    while k < len(seg) and (ASSIGN.match(seg[k]) or seg[k] in WRAPPERS or seg[k] == "env"):
        if ASSIGN.match(seg[k]):
            env.append(seg[k])
        k += 1
    if k >= len(seg):
        return None
    prog = seg[k].replace("\\", "/").rsplit("/", 1)[-1].lower()
    if prog not in ("git", "git.exe"):
        return None
    k += 1
    globals_: list[str] = []
    while k < len(seg) and seg[k].startswith("-"):
        globals_.append(seg[k])
        if seg[k] in GIT_VALUE_OPTS and k + 1 < len(seg):
            globals_.append(seg[k + 1])
            k += 1
        k += 1
    if k >= len(seg):
        return None
    return env, globals_, seg[k], seg[k + 1:]


# ------------------------------------------------------------------------------------------------
SWEEP_PATHSPECS = {".", "./", ".\\", ":/", ":/*", "*", ":(top)", ":(top)*"}
ADD_SWEEP_LONG = {"--all", "--update", "--no-ignore-removal"}
COMMIT_VALUE_SHORT = set("mFCctSu")  # the rest of a short cluster after one of these is its value
COMMIT_VALUE_LONG = {"--message", "--file", "--reuse-message", "--reedit-message", "--template", "--author",
                     "--date", "--fixup", "--squash", "--trailer", "--cleanup", "--gpg-sign", "--untracked-files",
                     "--pathspec-from-file"}


def add_refusal(args: list[str]) -> str | None:
    dashdash = False
    for a in args:
        if not dashdash and a == "--":
            dashdash = True
            continue
        if not dashdash and a.startswith("--"):
            if a.split("=", 1)[0] in ADD_SWEEP_LONG:
                return a
            continue
        if not dashdash and a.startswith("-") and len(a) > 1:
            if "A" in a[1:] or "u" in a[1:]:
                return a
            continue
        if a in SWEEP_PATHSPECS:
            return a
    return None


def commit_refusal(args: list[str]) -> str | None:
    dashdash, skip = False, False
    for a in args:
        if skip:
            skip = False
            continue
        if not dashdash and a == "--":
            dashdash = True
            continue
        if not dashdash and a.startswith("--"):
            if a == "--all":
                return a
            if a in COMMIT_VALUE_LONG and a not in ("--gpg-sign", "--untracked-files"):
                skip = True
            continue
        if not dashdash and a.startswith("-") and len(a) > 1:
            for ch in a[1:]:
                if ch == "a":
                    return a
                if ch in COMMIT_VALUE_SHORT:
                    if a.endswith(ch) and ch in "mFCct":
                        skip = True  # value is the next word
                    break
            continue
        if a in SWEEP_PATHSPECS:
            return a
    return None


def refusals(command: str) -> list[str]:
    out = []
    for seg in tokenize(command):
        inv = git_invocation(seg)
        if not inv:
            continue
        _env, _g, sub, args = inv
        if sub in ("add", "stage"):
            bad = add_refusal(args)
            if bad:
                out.append(f"`git {sub} ... {bad}` stages more than the paths you name")
        elif sub == "commit":
            bad = commit_refusal(args)
            if bad:
                out.append(f"`git commit ... {bad}` commits every modified tracked file, not the paths you staged")
    return out


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        return 0
    command = (payload.get("tool_input") or {}).get("command") if isinstance(payload, dict) else None
    if not isinstance(command, str) or "git" not in command:
        return 0
    found = refusals(command)
    if not found:
        return 0
    print("REFUSED (exact-path-add): " + "; ".join(found) + ".\n"
          "This checkout is shared: a sweeping stage takes a peer's files into your commit.\n"
          "Stage exact paths, then commit what is staged:  git add -- <path> [<path> ...] && git commit -m \"...\"",
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
