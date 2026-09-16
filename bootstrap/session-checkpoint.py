#!/usr/bin/env python
"""Pointer-only session checkpoint, written mechanically at every turn end.

Per ~/.claude/ROTATION-install-prompt.md: make session state survive an account rotation and a new
machine WITHOUT relying on the model remembering to write anything. The checkpoint lives in a
machine-local directory OUTSIDE the repo, so it survives a branch switch, a worktree removal and a
rotation.

Three hard rules from the install prompt, each enforced here rather than trusted:

  * NEVER BLOCKS and NEVER EXITS NON-ZERO. A checkpoint hook that can fail is a hook that can stop
    a turn from ending; every path returns 0, and the whole body is wrapped.
  * NEVER RUNS A GIT WRITE. Only `status --porcelain`, `rev-parse`, `log -1` -- all read-only, all
    with --no-optional-locks so an observer cannot create a lock of its own (repository
    non-negotiable), and all bounded by a timeout so a hung git cannot hang the turn.
  * POINTER-ONLY. It records WHERE to look and WHAT a rotation would lose -- never state a fresh
    session should derive for itself. The dirty-file list is the payload: committed work survives
    on its own, uncommitted work is exactly what a sudden exhaustion loses.

Why this file existed only as an install prompt until now: the prompt was written 2026-09-06 and
names `coordination/tools/session-checkpoint.py` for this repo, but it was never run here. Measured
2026-09-15: newest Conjugal checkpoint was 2026-09-11, four days stale, while three sessions ran.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

TIMEOUT = 10
MAX_DIRTY_LISTED = 40


def git(repo, *args, raw=False, default=""):
    """Read-only git, lock-suppressed and bounded. Returns `default` on any failure.

    raw=True returns stdout UNSTRIPPED.

    `default` exists so a caller can tell FAILURE from an EMPTY ANSWER. Those are different facts,
    and collapsing them here is what let this hook report "a rotation right now would lose nothing"
    when git had exited 128 and it had not managed to look at all (found by the independent
    acceptance key, 2026-09-15). Silence is not evidence (kernel K4).

    Why that matters, found by this hook's own first run: `status --porcelain` encodes the state in
    two leading columns, so a modified-unstaged file is " M path" -- with a LEADING SPACE. Stripping
    the whole output eats that space on the FIRST line only, after which a fixed `line[3:]` slice
    cuts one character too many and silently corrupts that one path (".claude/settings.json" was
    written as "claude/settings.json"). Untracked "?? path" entries have no leading space and are
    unaffected, so exactly one entry is wrong and the rest look right -- which is how it survives a
    glance. A checkpoint exists to tell a resuming session what it would lose; a path that does not
    exist is worse than no list.
    """
    try:
        p = subprocess.run(["git", "--no-optional-locks", *args], cwd=repo,
                           capture_output=True, text=True, timeout=TIMEOUT,
                           encoding="utf-8", errors="replace")
        if p.returncode != 0:
            return default
        return p.stdout if raw else p.stdout.strip()
    except Exception:
        return default


def main():
    raw = ""
    try:
        raw = sys.stdin.read()
    except Exception:
        pass
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        payload = {}

    repo = (payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR")
            or os.getcwd())
    session = str(payload.get("session_id") or os.environ.get("CLAUDE_SESSION_ID") or "unknown")[:16]

    # Checkpoint under the MAIN repo's name, not the worktree's: a worktree can be deleted, and a
    # checkpoint filed under a vanished directory is a checkpoint nobody finds.
    common = git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir") or ""
    main_repo = os.path.dirname(common) if common.endswith(".git") else repo
    # A tree that is NOT A REPOSITORY and a repository whose status command FAILED are different
    # facts, and reporting the first as the second is the evidence-layer collapse this file has
    # already been burned by four times. They also call for opposite conclusions: a failed status
    # means "look by hand", while an unversioned tree means everything in it is uncommitted by
    # construction. Fleet members are not uniformly under git -- salesforce-tools is a real source
    # tree with no VCS at all -- so this is a live case, not a hypothetical.
    #
    # "git is not installed" is a THIRD fact again, and it presents identically: every git call
    # returns its default, so a perfectly normal repository read as "not under version control"
    # until this check existed. Found by the independent acceptance key, 2026-09-16. Probe the tool
    # before concluding anything about the tree.
    git_available = bool(git(repo, "--version"))
    is_repo = git_available and bool(common)
    name = os.path.basename(main_repo.rstrip("\\/")) or "repo"

    branch = git(repo, "rev-parse", "--abbrev-ref", "HEAD") or "?"
    head = git(repo, "rev-parse", "--short", "HEAD") or "?"
    last = git(repo, "log", "-1", "--format=%s") or "?"
    # -z is the only honest way to read porcelain. Without it git C-QUOTES any path that is not
    # plain ASCII, so "café.txt" is reported as "caf\303\251.txt" -- and a checkpoint naming a path
    # that does not exist is the exact failure this hook exists to prevent. -z emits raw bytes,
    # NUL-separated, with no quoting and no escaping, which fixes non-ASCII, spaces and embedded
    # newlines in one move (found by the independent acceptance key, 2026-09-15).
    # --untracked-files=normal is passed EXPLICITLY, never left to configuration. A repo or user
    # with `status.showUntrackedFiles=no` makes untracked work invisible to a plain status, and the
    # checkpoint then reports "a rotation right now would lose nothing" over a tree holding unsaved
    # files -- the same false clean as a failed status, arriving through config instead of error
    # (found by the independent acceptance key, 2026-09-15). A tool whose honesty depends on the
    # reader's settings is not a guard. `normal` restores git's default rather than `all`, so an
    # untracked directory stays collapsed instead of expanding to thousands of scratch paths.
    # --ignore-submodules=none for the same reason: `diff.ignoreSubmodules=all` hides a dirty
    # submodule from status entirely, and the checkpoint would again report that a rotation loses
    # nothing over real uncommitted work (third instance of this class, found by the key).
    # Every observation this hook makes is now pinned on the command line, so no repository or
    # user setting can narrow what it is able to see.
    status = git(repo, "status", "--porcelain", "-z", "--untracked-files=normal",
                 "--ignore-submodules=none", raw=True, default=None)
    dirty = []
    status_failed = status is None
    if not status_failed:
        # Each record is "XY <path>"; a rename or copy is followed by a SECOND record holding the
        # ORIGIN path, which must be consumed rather than read as another dirty file. The
        # destination is what a resuming session needs, so the origin is dropped.
        fields = [f for f in status.split("\0")]
        i = 0
        while i < len(fields):
            entry = fields[i]
            i += 1
            if len(entry) < 4:
                continue
            code, path = entry[:2], entry[3:]
            if "R" in code or "C" in code:
                i += 1        # skip the origin record that belongs to this rename/copy
            if path:
                dirty.append(path)

    # Paths the INDEX hides from status, whatever flags status is given. `assume-unchanged` and
    # `skip-worktree` exist precisely to stop git reporting changes to a file, so no status option
    # can reveal them and the previous three fixes -- all of which added a flag -- could not have
    # closed this road (found by the independent acceptance key, 2026-09-15, fourth instance).
    #
    # The lesson is that chasing each suppression with another flag was the wrong shape. The hook
    # cannot promise it saw everything, so it stops promising: it enumerates what is hidden from it
    # and refuses to state the absolute "nothing would be lost" while anything is. A bounded claim
    # a reader can check beats an absolute one that is occasionally false.
    # `ls-files -v` marks skip-worktree with "S" and assume-unchanged with a LOWERCASE letter.
    hidden = []
    listing = git(repo, "ls-files", "-v", "-z", raw=True, default=None)
    if listing:
        for entry in listing.split("\0"):
            if len(entry) < 3:
                continue
            tag, path = entry[0], entry[2:]
            if path and (tag == "S" or tag.islower()):
                hidden.append(path)

    out_dir = os.path.join(os.path.expanduser("~"), ".claude", "session-checkpoints", name)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "SESSION-{}.md".format(session))

    lines = [
        "# SESSION-{} checkpoint (pointer-only, written mechanically at every turn end)".format(session),
        "",
        "- written: {}".format(datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")),
        "- repo: {}".format(main_repo),
        "- cwd: {}".format(repo),
        "- branch: {} @ {}".format(branch, head),
        "- last commit: {}".format(last),
    ]
    if not git_available:
        # Says nothing about the tree, which may be a perfectly healthy repository. The honest
        # report is about the MEASURING INSTRUMENT, not about what it failed to measure.
        lines.append("- uncommitted files: UNKNOWN -- `git` could not be run at all, so this "
                     "checkpoint could not look. This says nothing about whether the tree is a "
                     "repository or whether it is clean. Fix git on PATH, then look by hand.")
    elif not is_repo:
        # The strongest statement this file ever makes, and the only one that is unconditional --
        # because for an unversioned tree it is true by construction rather than by observation.
        # Nothing here is committed anywhere, so a rotation or a lost disk takes all of it. Saying
        # "git status FAILED" would understate that into a tooling hiccup.
        lines.append("- version control: NONE. This tree is not a git repository, so NOTHING in "
                     "it is committed and ALL of it is at risk -- not just a list of changed "
                     "files. A rotation loses this work unless it is backed up somewhere this "
                     "checkpoint cannot see.")
        lines.append("- uncommitted files: NOT DERIVABLE without version control. Put the tree "
                     "under git, or record its backup location where a resuming session will "
                     "read it.")
    elif status_failed:
        # Refuse to assert safety on no evidence. "Nothing would be lost" and "I could not look"
        # are different facts, and printing the first when the second is true is the most expensive
        # lie this file can tell: it is read precisely when the work is already gone.
        lines.append("- uncommitted files: UNKNOWN -- `git status` FAILED, so this checkpoint "
                     "cannot say what a rotation would lose. Treat the tree as unsaved and run "
                     "`git --no-optional-locks status` by hand before assuming anything.")
    elif dirty:
        lines.append("- files this session dirtied and has NOT committed ({}):".format(len(dirty)))
        for f in dirty[:MAX_DIRTY_LISTED]:
            lines.append("  - {}".format(f))
        if len(dirty) > MAX_DIRTY_LISTED:
            lines.append("  - ... and {} more".format(len(dirty) - MAX_DIRTY_LISTED))
    else:
        # NO ABSOLUTE CLAIM, EVER. Five rounds of independent review found five separate roads to
        # "a rotation right now would lose nothing" printed over real uncommitted work: an erroring
        # status, `status.showUntrackedFiles=no`, `diff.ignoreSubmodules=all`, index flags in this
        # repo, and index flags inside a submodule. Each was fixed and the next appeared, because
        # git has unbounded ways not to report a change and an absolute claim has to be right about
        # all of them at once.
        #
        # So the claim is retired rather than defended. The checkpoint states what it EXAMINED and
        # what it did NOT, and lets the reader judge. A scoped statement that is always true is
        # worth more than an absolute that is usually true, because this file is read at exactly
        # the moment the work is already gone.
        lines.append("- uncommitted files: NONE REPORTED by git.")
        lines.append("  Examined: tracked changes, untracked files, and submodule dirt in this "
                     "working tree.")
        lines.append("  NOT examined, and able to hold unsaved work: files excluded by .gitignore, "
                     "and anything a submodule's own index hides. Changes to a path marked "
                     "assume-unchanged or skip-worktree are invisible to git status; any such path "
                     "in THIS index is listed below.")
    if is_repo and not dirty and not status_failed and not hidden:
        lines.append("  No path in this index carries a hiding flag.")
    if hidden:
        lines.append("- paths the index hides from status ({}):".format(len(hidden)))
        for f in hidden[:MAX_DIRTY_LISTED]:
            lines.append("  ! {}".format(f))
        if len(hidden) > MAX_DIRTY_LISTED:
            lines.append("  ! ... and {} more".format(len(hidden) - MAX_DIRTY_LISTED))
    lines += [
        "",
        # The footer carried the retired absolute in different words -- "everything else is
        # committed and derivable" asserts exactly what the scope note above refuses to. Retiring a
        # claim means retiring its meaning, not one spelling of it, and the key caught this file
        # contradicting itself between two adjacent lines.
        "Resume: read the repo entry file named by its CLAUDE.md, then "
        "`git --no-optional-locks log -5 {}`. What is listed above is what git reported under the "
        "scope stated above; it is not a complete inventory of what a rotation would lose. Treat "
        "the unexamined categories as unknown rather than as empty.".format(branch),
    ]

    try:
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(lines) + "\n")
    except Exception:
        pass            # a checkpoint that cannot be written must still not fail the turn
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)     # never non-zero, under any circumstance
