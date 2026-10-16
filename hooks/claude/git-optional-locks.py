#!/usr/bin/env python3
"""PreToolUse hook (Bash / PowerShell): read-only git observers must not take optional locks.

`git status` and `git diff` refresh the index and write it back when they can -- an OPTIONAL lock.
In a checkout shared with other agents and with scheduled automation, an observer racing a real
commit leaves `index.lock` behind or makes the writer fail. Observers suppress it:

    git --no-optional-locks status            (global option, before the subcommand)
    GIT_OPTIONAL_LOCKS=0 git status           (env prefix, or `env GIT_OPTIONAL_LOCKS=0 git ...`;
                                               `export GIT_OPTIONAL_LOCKS=0` or PowerShell
                                               `$env:GIT_OPTIONAL_LOCKS='0'` earlier in the command;
                                               or the variable already set in the session env)

Refused (exit 2): status, diff, log, show, rev-list without one of those. Mutation commands
(add, commit, push, fetch, rebase, merge, reset, checkout, stash, ...) are never refused: this hook
judges only the read-only observers, and never suppresses or bypasses a real lock.

The command is tokenised like a POSIX shell (quotes, ; && || | & newlines, $( ), backticks,
comments, heredoc bodies skipped), so quoted text that merely mentions git never trips it.
Stdin: the Claude Code hook payload. Exit 0 allow, 2 refuse. Stdlib only; one file, no imports
from siblings (it runs as a single pinned blob).
"""
from __future__ import annotations

import json
import os
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
OBSERVERS = {"status", "diff", "log", "show", "rev-list"}
SESSION_SET = re.compile(r"(?:\bexport\s+|\$env:)GIT_OPTIONAL_LOCKS\s*=\s*['\"]?0['\"]?(?![0-9A-Za-z])", re.I)


def refusals(command: str, environ=os.environ) -> list[str]:
    if environ.get("GIT_OPTIONAL_LOCKS") == "0":
        return []
    out, covered = [], False
    for seg in tokenize(command):
        if SESSION_SET.search(" ".join(seg)) or (seg[:1] == ["export"] and "GIT_OPTIONAL_LOCKS=0" in seg):
            covered = True
        inv = git_invocation(seg)
        if not inv or covered:
            continue
        env, globals_, sub, _args = inv
        if sub not in OBSERVERS:
            continue
        if "--no-optional-locks" in globals_ or any(re.sub(r"^\$env:", "", e) == "GIT_OPTIONAL_LOCKS=0" for e in env):
            continue
        out.append(f"`git {sub}`")
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
    print("REFUSED (git-optional-locks): " + ", ".join(sorted(set(found))) + " without --no-optional-locks.\n"
          "A read-only observer in a shared checkout must not take the index's optional lock.\n"
          "Write it as  git --no-optional-locks <status|diff|log|show|rev-list> ...  "
          "(or prefix GIT_OPTIONAL_LOCKS=0).", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
