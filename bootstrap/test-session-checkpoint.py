#!/usr/bin/env python3
"""Behavioural proof for the per-turn session checkpoint hook.

The hook's whole purpose is to tell a session on a NEW ACCOUNT what a sudden
exhaustion just lost. That makes its failure mode quiet and expensive: a
checkpoint naming a path that does not exist is worse than no checkpoint,
because it sends the resuming session after a file that was never there.

Its own first run shipped exactly that defect -- a stripped `status --porcelain`
lost the leading space of " M path", and a fixed `line[3:]` slice then ate one
character of the FIRST listed path only. Untracked "?? path" rows have no
leading space and came out right, so one entry was corrupt and the rest looked
fine. No test existed to catch it. This file is that test.

Every case drives the real hook as a subprocess against a real temporary git
repository, because the defect lived in the seam between git's output format
and the parser -- a seam a mocked git would have reproduced incorrectly and
declared green.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HOOK = Path(__file__).resolve().parent / "session-checkpoint.py"

FAILURES = []


def check(label, condition, detail=""):
    if condition:
        print("  ok   " + label)
    else:
        print("  FAIL " + label + ((" -- " + detail) if detail else ""))
        FAILURES.append(label)


def git(repo, *args):
    return subprocess.run(
        ["git", "--no-optional-locks", *args], cwd=str(repo),
        capture_output=True, text=True, timeout=60,
        encoding="utf-8", errors="replace",
    )


def make_repo(tmp):
    repo = tmp / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.invalid")
    git(repo, "config", "user.name", "test")
    (repo / "tracked.txt").write_text("one\n", encoding="utf-8")
    (repo / ".claude").mkdir()
    (repo / ".claude" / "settings.json").write_text("{}\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "seed")
    return repo


def run_hook(repo, home, stdin_text=None, session="TESTSESS"):
    """Run the hook exactly as Claude Code runs it: JSON payload on stdin.

    HOME and USERPROFILE are BOTH redirected. On Windows os.path.expanduser
    consults USERPROFILE and ignores HOME, so a test that sets only HOME passes
    green while the hook writes into the developer's real home directory -- the
    test would be measuring the wrong filesystem and would never say so.
    """
    env = dict(os.environ)
    env["HOME"] = str(home)
    env["USERPROFILE"] = str(home)
    env.pop("CLAUDE_PROJECT_DIR", None)
    payload = (json.dumps({"cwd": str(repo), "session_id": session})
               if stdin_text is None else stdin_text)
    return subprocess.run(
        [sys.executable, str(HOOK)], input=payload, env=env,
        capture_output=True, text=True, timeout=60,
        encoding="utf-8", errors="replace",
    )


def checkpoint_for(home, repo, session="TESTSESS"):
    return home / ".claude" / "session-checkpoints" / repo.name / ("SESSION-" + session + ".md")


def listed_paths(text):
    out = []
    for line in text.splitlines():
        s = line.strip()
        if line.startswith("  - ") and not s.startswith("- ..."):
            out.append(s[2:])
    return out


def case_leading_space_path_is_not_truncated(tmp):
    """The regression that shipped: a leading-space row as the FIRST porcelain line."""
    print("case: modified tracked file listed with its exact path")
    home = tmp / "home1"
    repo = make_repo(tmp)
    # A dotfile sorts first, so its " M" row is the first porcelain line -- the
    # only position the strip-then-slice defect could corrupt.
    (repo / ".claude" / "settings.json").write_text('{"hooks":{}}\n', encoding="utf-8")
    porcelain = git(repo, "status", "--porcelain").stdout
    check("fixture really produces a leading-space status row",
          porcelain.startswith(" M"), repr(porcelain[:20]))

    rc = run_hook(repo, home)
    check("hook exits 0", rc.returncode == 0, rc.stderr[-300:])
    cp = checkpoint_for(home, repo)
    check("checkpoint written", cp.exists(), str(cp))
    if not cp.exists():
        return
    body = cp.read_text(encoding="utf-8")
    paths = listed_paths(body)
    check("exact path recorded", ".claude/settings.json" in paths, str(paths))
    check("truncated path NOT recorded", "claude/settings.json" not in paths, str(paths))
    for p in paths:
        check("listed path resolves on disk: " + p, (repo / p).exists())


def case_rename_records_new_path(tmp):
    print("case: a rename records the destination, which is what a resume needs")
    home = tmp / "home2"
    repo = make_repo(tmp)
    git(repo, "mv", "tracked.txt", "renamed.txt")
    rc = run_hook(repo, home)
    check("hook exits 0", rc.returncode == 0, rc.stderr[-300:])
    body = checkpoint_for(home, repo).read_text(encoding="utf-8")
    paths = listed_paths(body)
    check("new path recorded", "renamed.txt" in paths, str(paths))
    check("no unsplit arrow entry", not any("->" in p for p in paths), str(paths))
    for p in paths:
        check("listed path resolves on disk: " + p, (repo / p).exists())


def case_path_with_spaces(tmp):
    print("case: porcelain quotes paths containing spaces; quotes are not part of the path")
    home = tmp / "home3"
    repo = make_repo(tmp)
    (repo / "a file.txt").write_text("x\n", encoding="utf-8")
    rc = run_hook(repo, home)
    check("hook exits 0", rc.returncode == 0, rc.stderr[-300:])
    body = checkpoint_for(home, repo).read_text(encoding="utf-8")
    paths = listed_paths(body)
    # Assert the path is PRESENT before asserting things about it. "No quote characters in any
    # path" is trivially true of an empty list, so without this the case could pass while the hook
    # recorded nothing at all (independent acceptance key, 2026-09-15).
    check("the spaced path is actually recorded", "a file.txt" in paths, str(paths))
    check("no quote characters survive into a path",
          not any(ch == '"' for p in paths for ch in p), str(paths))
    for p in paths:
        check("listed path resolves on disk: " + p, (repo / p).exists())


def case_non_ascii_path_is_recorded_verbatim(tmp):
    """git C-quotes non-ASCII paths unless asked otherwise; an escaped path resolves nowhere."""
    print("case: a non-ASCII path is recorded as itself, not as a C-escape")
    home = tmp / "home8"
    repo = make_repo(tmp)
    target = repo / "café.txt"
    try:
        target.write_text("x\n", encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        check("non-ASCII fixture created", False, str(exc))
        return
    rc = run_hook(repo, home)
    check("hook exits 0", rc.returncode == 0, rc.stderr[-300:])
    body = checkpoint_for(home, repo).read_text(encoding="utf-8")
    paths = listed_paths(body)
    check("exact non-ASCII path recorded", "café.txt" in paths, str(paths))
    check("no C-escape recorded", not any("\\3" in p for p in paths), str(paths))
    for p in paths:
        check("listed path resolves on disk: " + p, (repo / p).exists())


def case_git_failure_is_reported_as_unknown_not_clean(tmp):
    """The most expensive lie this file can tell: "nothing would be lost", when it could not look.

    A checkpoint is read precisely when the work is already gone, so a false clean is not a cosmetic
    defect. Failure and emptiness are different facts and must read differently.
    """
    print("case: a failed `git status` reads UNKNOWN, never NONE")
    home = tmp / "home9"
    repo = make_repo(tmp)
    (repo / "tracked.txt").write_text("dirty\n", encoding="utf-8")
    # Corrupt only the index: `status` then fails while the repo is otherwise intact.
    (repo / ".git" / "index").write_bytes(b"not a git index at all")
    broke = git(repo, "status", "--porcelain")
    check("fixture really breaks git status", broke.returncode != 0,
          "rc=" + str(broke.returncode))

    rc = run_hook(repo, home)
    check("hook still exits 0", rc.returncode == 0, rc.stderr[-300:])
    cp = checkpoint_for(home, repo)
    check("checkpoint still written", cp.exists(), str(cp))
    if not cp.exists():
        return
    body = cp.read_text(encoding="utf-8")
    check("does NOT claim a rotation would lose nothing",
          "would lose nothing" not in body, body[-300:])
    check("states the uncertainty explicitly", "UNKNOWN" in body, body[-300:])


def case_untracked_suppressing_config_cannot_hide_work(tmp):
    """A tool whose honesty depends on the reader's git config is not a guard.

    `status.showUntrackedFiles=no` is a legitimate setting a developer may carry for speed. Under
    it a plain porcelain read returns nothing for a tree full of unsaved untracked files, and the
    checkpoint would announce that a rotation loses nothing. Same false clean as a failed status,
    arriving through configuration instead of error.
    """
    print("case: status.showUntrackedFiles=no cannot hide unsaved work")
    home = tmp / "home10"
    repo = make_repo(tmp)
    git(repo, "config", "status.showUntrackedFiles", "no")
    (repo / "unsaved.txt").write_text("work that a rotation would lose\n", encoding="utf-8")
    suppressed = git(repo, "status", "--porcelain").stdout
    check("fixture really hides the file from a plain status",
          "unsaved.txt" not in suppressed, repr(suppressed[:80]))

    rc = run_hook(repo, home)
    check("hook exits 0", rc.returncode == 0, rc.stderr[-300:])
    body = checkpoint_for(home, repo).read_text(encoding="utf-8")
    paths = listed_paths(body)
    check("the untracked file is recorded anyway", "unsaved.txt" in paths, str(paths))
    check("does NOT claim a rotation would lose nothing",
          "would lose nothing" not in body, body[-200:])


def case_submodule_suppressing_config_cannot_hide_work(tmp):
    """Third road to the same false clean: `diff.ignoreSubmodules=all` hides a dirty submodule.

    Every observation the hook makes is pinned on the command line for this reason. A guard that
    any repository setting can narrow is not a guard, and the three instances of this class found
    so far all arrived by a different route: error, untracked config, submodule config.
    """
    print("case: diff.ignoreSubmodules=all cannot hide a dirty submodule")
    home = tmp / "home11"
    parent = make_repo(tmp)
    child = tmp / "child"
    child.mkdir()
    git(child, "init", "-q", "-b", "main")
    git(child, "config", "user.email", "t@example.invalid")
    git(child, "config", "user.name", "test")
    (child / "seed.txt").write_text("one\n", encoding="utf-8")
    git(child, "add", "-A")
    git(child, "commit", "-q", "-m", "child seed")

    env = dict(os.environ)
    env["GIT_ALLOW_PROTOCOL"] = "file"
    added = subprocess.run(
        ["git", "--no-optional-locks", "-c", "protocol.file.allow=always",
         "submodule", "add", "-q", child.as_uri(), "child"],
        cwd=str(parent), capture_output=True, text=True, timeout=120,
        encoding="utf-8", errors="replace", env=env)
    if added.returncode != 0:
        check("submodule fixture created", False, added.stderr[-200:])
        return
    git(parent, "commit", "-q", "-m", "add submodule")
    (parent / "child" / "seed.txt").write_text("dirty in the submodule\n", encoding="utf-8")
    git(parent, "config", "diff.ignoreSubmodules", "all")

    suppressed = git(parent, "status", "--porcelain").stdout
    check("fixture really hides the submodule from a plain status",
          "child" not in suppressed, repr(suppressed[:80]))

    rc = run_hook(parent, home)
    check("hook exits 0", rc.returncode == 0, rc.stderr[-300:])
    body = checkpoint_for(home, parent).read_text(encoding="utf-8")
    check("the dirty submodule is recorded anyway",
          "child" in "\n".join(listed_paths(body)), str(listed_paths(body)))
    check("does NOT claim a rotation would lose nothing",
          "would lose nothing" not in body, body[-200:])


def case_index_hidden_paths_are_named_not_silently_dropped(tmp):
    """The road no status flag can close, and why the claim itself had to change.

    `assume-unchanged` and `skip-worktree` exist to stop git reporting changes to a file. No option
    to `status` overrides them, so the three earlier fixes -- each of which added a flag -- could not
    have reached this case. The hook therefore stops promising it saw everything: it enumerates what
    is hidden from it and withholds the absolute claim while anything is.
    """
    for flag in ("--assume-unchanged", "--skip-worktree"):
        print("case: " + flag + " work is named, not silently dropped")
        home = tmp / ("home12" + flag)
        sub = tmp / flag.strip("-")
        sub.mkdir(parents=True, exist_ok=True)
        repo = make_repo(sub)
        git(repo, "update-index", flag, "tracked.txt")
        (repo / "tracked.txt").write_text("changed under a hiding flag\n", encoding="utf-8")
        invisible = git(repo, "status", "--porcelain", "--untracked-files=normal",
                        "--ignore-submodules=none").stdout
        check("fixture is invisible even to the pinned status" + flag,
              "tracked.txt" not in invisible, repr(invisible[:80]))

        rc = run_hook(repo, home)
        check("hook exits 0" + flag, rc.returncode == 0, rc.stderr[-300:])
        body = checkpoint_for(home, repo).read_text(encoding="utf-8")
        check("does NOT claim a rotation would lose nothing" + flag,
              "would lose nothing" not in body, body[-250:])
        check("names the hidden path" + flag, "tracked.txt" in body, body[-250:])


def case_unversioned_tree_is_not_a_failed_status(tmp):
    """Two facts one string used to cover, calling for opposite conclusions.

    A failed `git status` means "look by hand". A tree that is not a repository at all means
    everything in it is uncommitted by construction -- there is no list to produce, and the whole
    directory is what a rotation takes. Reporting the second as the first understates a total loss
    into a tooling hiccup. Live case: salesforce-tools is a real source tree with no VCS.
    """
    print("case: an unversioned tree is reported as unversioned, not as a failed command")
    home = tmp / "home14"
    plain = tmp / "not-a-repo"
    (plain / "src").mkdir(parents=True)
    (plain / "src" / "Thing.cs").write_text("// real source, no VCS\n", encoding="utf-8")
    check("fixture really has no VCS", not (plain / ".git").exists())

    rc = run_hook(plain, home)
    check("hook exits 0", rc.returncode == 0, rc.stderr[-300:])
    cp = home / ".claude" / "session-checkpoints" / plain.name / "SESSION-TESTSESS.md"
    check("checkpoint written", cp.exists(), str(cp))
    if not cp.exists():
        return
    body = cp.read_text(encoding="utf-8")
    check("states that there is no version control", "version control: NONE" in body, body[-400:])
    check("states that ALL of it is at risk", "ALL of it is at risk" in body, body[-400:])
    check("does NOT blame a failed git command",
          "`git status` FAILED" not in body, body[-400:])
    check("makes no absolute safety claim",
          "would lose nothing" not in body and "NONE REPORTED" not in body, body[-400:])


def case_clean_repo_says_nothing_would_be_lost(tmp):
    print("case: a clean tree states the absence positively, it does not omit the line")
    home = tmp / "home4"
    repo = make_repo(tmp)
    rc = run_hook(repo, home)
    check("hook exits 0", rc.returncode == 0, rc.stderr[-300:])
    body = checkpoint_for(home, repo).read_text(encoding="utf-8")
    # The absence is stated as a SCOPED observation, never as an absolute. Five independent review
    # rounds found five separate roads to a false "a rotation right now would lose nothing", so the
    # absolute is retired: the checkpoint says what it examined and what it could not.
    check("absence stated explicitly", "NONE REPORTED" in body, body[-300:])
    check("no absolute safety claim is made anywhere",
          "would lose nothing" not in body, body[-300:])
    check("names what it did NOT examine", ".gitignore" in body and "submodule" in body,
          body[-300:])


def case_never_exits_non_zero(tmp):
    """A Stop hook that can fail is a hook that can stop a turn from ending."""
    print("case: never exits non-zero, whatever it is handed")
    home = tmp / "home5"
    repo = make_repo(tmp)
    cases = (
        ("empty stdin", "", repo),
        ("non-JSON stdin", "not json at all", repo),
        ("JSON that is not an object", "[1,2,3]", repo),
        ("cwd that is not a repo", json.dumps({"cwd": str(tmp), "session_id": "X"}), tmp),
        ("cwd that does not exist",
         json.dumps({"cwd": str(tmp / "absent"), "session_id": "X"}), repo),
    )
    for label, stdin_text, cwd in cases:
        rc = run_hook(cwd, home, stdin_text=stdin_text)
        check("exit 0 on " + label, rc.returncode == 0,
              "rc=" + str(rc.returncode) + " " + rc.stderr[-200:])


def case_performs_no_git_write(tmp):
    """Read-only is a property of the repository afterwards, not a promise in a docstring."""
    print("case: runs no git write")
    home = tmp / "home6"
    repo = make_repo(tmp)
    (repo / "tracked.txt").write_text("two\n", encoding="utf-8")
    before_head = git(repo, "rev-parse", "HEAD").stdout.strip()
    before_status = git(repo, "status", "--porcelain").stdout
    before_reflog = git(repo, "reflog", "--format=%H %gs").stdout
    index = repo / ".git" / "index"
    before_index = index.stat().st_mtime_ns if index.exists() else None

    rc = run_hook(repo, home)
    check("hook exits 0", rc.returncode == 0, rc.stderr[-300:])
    check("HEAD unchanged", git(repo, "rev-parse", "HEAD").stdout.strip() == before_head)
    check("working tree state unchanged",
          git(repo, "status", "--porcelain").stdout == before_status)
    check("reflog unchanged", git(repo, "reflog", "--format=%H %gs").stdout == before_reflog)
    after_index = index.stat().st_mtime_ns if index.exists() else None
    check("index not rewritten", after_index == before_index)
    check("no index.lock left behind", not (repo / ".git" / "index.lock").exists())


def case_worktree_files_under_main_repo(tmp):
    """A worktree can be deleted; a checkpoint filed under it is one nobody finds."""
    print("case: a worktree checkpoints under the MAIN repo name")
    home = tmp / "home7"
    repo = make_repo(tmp)
    wt = tmp / "wt-elsewhere"
    made = git(repo, "worktree", "add", "-q", "-b", "side", str(wt))
    if made.returncode != 0:
        check("worktree fixture created", False, made.stderr[-200:])
        return
    rc = run_hook(wt, home)
    check("hook exits 0", rc.returncode == 0, rc.stderr[-300:])
    main_named = checkpoint_for(home, repo)
    wt_named = home / ".claude" / "session-checkpoints" / wt.name / "SESSION-TESTSESS.md"
    check("filed under the main repo name", main_named.exists(), str(main_named))
    check("not filed under the worktree name", not wt_named.exists(), str(wt_named))
    if main_named.exists():
        check("records the worktree it ran in",
              str(wt) in main_named.read_text(encoding="utf-8"))


def case_absolute_claim_appears_nowhere(tmp):
    """The class is closed by construction rather than by covering each road into it.

    Five independent review rounds found five different ways to make the old absolute false. This
    is the assertion that makes a sixth road harmless: whatever git does or does not report, the
    hook never tells a reader that nothing would be lost. Two of the fixtures below are conditions
    the key reproduced and no added status flag could have closed -- an index flag inside a
    submodule, and an authored draft that .gitignore excludes.
    """
    print("case: the absolute safety claim cannot be emitted under any fixture")
    home = tmp / "home13"
    repo = make_repo(tmp)

    def clean():
        return None

    def dirty():
        (repo / "tracked.txt").write_text("changed\n", encoding="utf-8")

    def ignored_draft():
        (repo / ".gitignore").write_text("draft.txt\n", encoding="utf-8")
        git(repo, "add", ".gitignore")
        git(repo, "commit", "-q", "-m", "ignore drafts")
        (repo / "draft.txt").write_text("an authored draft a rotation would lose\n",
                                        encoding="utf-8")

    def hidden_flag():
        git(repo, "update-index", "--assume-unchanged", "tracked.txt")
        (repo / "tracked.txt").write_text("hidden change\n", encoding="utf-8")

    for label, setup in (("clean tree", clean), ("dirty tree", dirty),
                         ("ignored authored draft", ignored_draft),
                         ("assume-unchanged change", hidden_flag)):
        setup()
        rc = run_hook(repo, home)
        check("hook exits 0 (" + label + ")", rc.returncode == 0, rc.stderr[-200:])
        body = checkpoint_for(home, repo).read_text(encoding="utf-8")
        # Every known SPELLING of the absolute, not just the one that was retired first. The key
        # found the footer still asserting "everything else is committed and derivable" two lines
        # below a scope note that refuses exactly that, so the file contradicted itself. Retiring a
        # claim means retiring its meaning.
        for phrase in ("would lose nothing", "everything else is committed",
                       "nothing would be lost", "is what a rotation would lose"):
            check("no absolute safety claim [" + phrase + "] (" + label + ")",
                  phrase not in body, body[-200:])
        check("scope is stated (" + label + ")",
              "NOT examined" in body or "UNKNOWN" in body or "NOT committed" in body,
              body[-200:])


def main():
    if not HOOK.exists():
        print("FAIL: hook not found at " + str(HOOK))
        return 1
    cases = (
        case_leading_space_path_is_not_truncated,
        case_rename_records_new_path,
        case_path_with_spaces,
        case_non_ascii_path_is_recorded_verbatim,
        case_git_failure_is_reported_as_unknown_not_clean,
        case_untracked_suppressing_config_cannot_hide_work,
        case_submodule_suppressing_config_cannot_hide_work,
        case_index_hidden_paths_are_named_not_silently_dropped,
        case_absolute_claim_appears_nowhere,
        case_unversioned_tree_is_not_a_failed_status,
        case_clean_repo_says_nothing_would_be_lost,
        case_never_exits_non_zero,
        case_performs_no_git_write,
        case_worktree_files_under_main_repo,
    )
    with tempfile.TemporaryDirectory(prefix="session-checkpoint-test-") as raw:
        tmp = Path(raw)
        for fn in cases:
            sub = tmp / fn.__name__
            sub.mkdir()
            fn(sub)
    if FAILURES:
        print("\nFAIL session-checkpoint: " + str(len(FAILURES)) + " check(s) failed")
        for f in FAILURES:
            print("  - " + f)
        return 1
    print("\nPASS session-checkpoint")
    return 0


if __name__ == "__main__":
    sys.exit(main())
