# PROMPT R — Install resume prep in THIS project, on THIS host

Paste this into a fresh session opened in the project's canonical checkout, once per project per
machine. It is idempotent and it UPGRADES: running it again after the reference implementation
changes replaces an older copy rather than skipping it.

Say which repo and machine you are in before acting.

---

## Why this replaces the inline version

The previous install instruction (`~/.claude/ROTATION-install-prompt.md`) carried the checkpoint
script INLINE, and guarded itself with *skip if the file already contains "session-checkpoint v2"*.
Both halves were defects, and they compounded:

- an inlined copy goes stale the moment the implementation is corrected, and nothing detects it;
- a skip-if-present guard means the hosts that adopted EARLIEST are exactly the ones a correction
  can never reach.

Measured 2026-09-16: seven defects were found in that implementation by an independent acceptance
key, every one of which caused the checkpoint to **misdescribe what an account rotation would
lose** — the single thing it exists to get right. A host still running the inlined copy has all
seven. So this prompt names a file on the bus instead of carrying one, and compares versions
instead of checking for existence.

## STEP 0 — pick your paths

| repo | script path | settings file |
|---|---|---|
| `C:\code\Conjugal` | `coordination/tools/session-checkpoint.py` | `.claude/settings.json` (exists; merge) |
| `C:\code\DropBox Vault` | `tools/hooks/session-checkpoint.py` | `.claude/settings.json` (exists; merge) |
| `magic-lantern_dannephoto` | `tools/roadmap/session-checkpoint.py` | `.claude/settings.json` |
| any other repo | `tools/session-checkpoint.py` | `.claude/settings.json` (create or merge) |

A project that already implements this doctrine under a DIFFERENT NAME (cloudvore's is
`tools/rotation-ready.py --hook`) keeps its own name. Do not install a second one beside it; port
the corrections in §2 into the implementation that is already wired. Adoption is measured by
capability, never by filename.

## STEP 1 — install or upgrade the script

The reference implementation is `bootstrap/session-checkpoint.py` **on this bus**, with its proof
in `bootstrap/test-session-checkpoint.py` (113 checks, 17 cases; see its docstring for two fixes it does NOT cover).

1. **Compare content digests, not prose.** An earlier draft of this step compared the first
   docstring line; the independent acceptance key showed those lines are identical across versions
   whose BEHAVIOUR differs, so the check would have reported "up to date" over a stale copy — the
   same failure as the skip-if-present guard, wearing a different hat. Run:

   ```
   python -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" <your script>
   python -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" bootstrap/session-checkpoint.py
   ```

   **If the digests differ, replace yours with the reference copy** (or port §2 in full if your
   project implements this under another name). Do not skip merely because a file exists.
2. If your project has no script, copy the reference file to your script path.
3. Copy `bootstrap/test-session-checkpoint.py` beside it, adjusting only the `HOOK` path constant.
4. Run the test. It must exit 0, read directly and **never through a pipe** — `tail` reports its own
   exit status, which has already produced a false green in this fleet.

## STEP 2 — the corrections, if you are porting rather than copying

Each is a way the checkpoint reported that a rotation would lose nothing while real uncommitted
work sat in the tree. Port all of them or copy the file; a partial port leaves the class open.

1. **Read `status --porcelain -z`.** Without `-z`, git C-quotes any non-ASCII path, so `café.txt` is
   recorded as an escape sequence that resolves to nothing. `-z` also removes the hand-rolled quote
   stripping and rename splitting that spaces and renames otherwise need.
2. **Never strip the porcelain output before slicing it.** A modified-unstaged row is `" M path"`,
   with a leading space; stripping eats it on the FIRST row only, and a fixed `[3:]` slice then
   silently truncates exactly one path while every other row looks right.
3. **Distinguish a FAILED status from an EMPTY one.** Returning `""` on failure makes a repo whose
   status exited 128 indistinguishable from a clean tree. Failure must say `UNKNOWN`.
4. **Pin `--untracked-files=normal`.** `status.showUntrackedFiles=no` otherwise hides untracked work.
5. **Pin `--ignore-submodules=none`.** `diff.ignoreSubmodules=all` otherwise hides a dirty submodule.
6. **List paths the index hides.** `assume-unchanged` and `skip-worktree` stop git reporting a file,
   and no status option overrides them. Read `ls-files -v`; `S` is skip-worktree and a lowercase tag
   is assume-unchanged.
7. **Never assert that nothing would be lost — in ANY wording.** This is the one that matters. Git
   has unbounded ways not to report a change, so an absolute claim has to be right about all of them
   at once, and four consecutive flag-fixes each closed one road while another opened. State what
   you EXAMINED and what you did NOT. Check the footer too: the sixth refusal in this sequence was
   for leaving "everything else is committed and derivable" two lines below the new scope note.

8. **Probe the instrument before describing the tree.** Two more members of the same family, both
   found by the key. A tree that is **not a repository at all** is distinct from a clean tree and
   from a failed command: nothing in it is committed anywhere, so a rotation takes all of it, and
   the checkpoint must say so rather than blame git. And when **git itself cannot be run** — absent
   from PATH — every call returns its default and a perfectly healthy repository reads as
   unversioned. Check `git --version` first; if that fails, report the instrument, because you have
   learned nothing about the tree. A repository git cannot OPEN (a malformed `.git/config` makes
   discovery exit 128 while `git --version` still works) is a fourth case again: check for a `.git`
   marker on the filesystem before ever saying "no version control".

9. **Scrub the git environment.** Pinning options on the command line is not enough — inherited
   `GIT_DIR`, `GIT_WORK_TREE` and `GIT_INDEX_FILE` redirect every measurement at another repository,
   and a dirty tree then reports clean. Environment beats command line.

10. **Keep the total runtime under the hook's configured budget.** Several git calls at a generous
    per-call timeout can exceed it; the kill then leaves a STALE checkpoint that reads exactly like
    a current one. Size the per-call timeout so the worst case cannot overrun.

11. **Do not promise a complete list you might truncate.** A sparse-checkout marks every excluded
    path skip-worktree, so the hidden-path list runs to hundreds and truncation buries the one path
    that is hidden AND modified. Raise the cap and DECLARE truncation.

12. **`--path-format` needs git 2.31.** Debian bullseye ships 2.30.2 and RHEL 8 ships 2.27, where
    that option fails and a healthy repository reads as unversioned. Fall back rather than conclude.

## STEP 3 — wire the Stop hook

Merge into your settings file, keeping any hooks already there:

```json
{ "hooks": { "Stop": [ { "hooks": [ { "type": "command",
  "command": "python \"$CLAUDE_PROJECT_DIR/<your script path>\"", "timeout": 20 } ] } ] } }
```

## STEP 4 — prove it, in four separate layers

Do not collapse these. A tool present, a hook declared, the hook firing, and a checkpoint fresh
enough to resume from are four different facts, and reporting an earlier one as a later one is how
a project believes for nine days that it is covered.

1. **TOOL** — the script exists at the path.
2. **WIRED** — the settings file declares a Stop hook whose command names it.
3. **FIRING** — run the configured command string yourself, with `CLAUDE_PROJECT_DIR` set as the
   host sets it, feeding `{"cwd":"<repo>","session_id":"WIRECHECK"}` on stdin. A checkpoint must
   appear under `<home>/.claude/session-checkpoints/<main repo directory name>/`. This proves the
   configured command resolves; only a real session proves the host actually calls it.
4. **FRESH** — after your next real session ends, confirm a new checkpoint appeared.

**Layer 3 is the one that actually fails, and it fails silently.** Measured 2026-09-16 on the
steward's host: `salesforce-tools` had the script installed, the `Stop` hook declared, the project
trusted (`hasTrustDialogAccepted: true`), and the configured command verified to resolve and write —
and then a REAL session ran in that directory across several turns and wrote **no checkpoint at
all**. On the same machine and in the same window, another project's newly-added `Stop` hook fired
normally for five concurrent sessions. So "installed, wired and trusted" did not imply "runs", and
nothing announced the difference. That is the entire reason this list has four entries instead of
two, and why `fleet-resume-readiness.py` refuses to call an install-verified member READY.

**And know what this strategy does NOT cover.** The hook runs when a turn ENDS. A session killed
outright — the process dies, the machine loses power, the host crashes — never reaches that point,
so the work of the turn in flight is unrecorded. What survives is the PREVIOUS turn's checkpoint, so
the exposure is bounded at roughly one turn rather than a whole session. Say that plainly when you
report adoption; a resume strategy oversold is one nobody checks.

   Use exactly `WIRECHECK` as the session id in layer 3. `fleet-resume-readiness.py` treats a
   checkpoint with that id as INSTALL-VERIFIED and deliberately **not** READY, so your install
   cannot report itself as a working hook before the host has been observed calling it. It converts
   to READY on its own at layer 4.

## STEP 5 — report it where it can be counted

Run `python tools/fleet-resume-readiness.py` on this bus. Your project should move off `ABSENT`.
A member the tool cannot reach from the host running it reads `UNREACHABLE`, which is neither ready
nor failing — so a member is only ever counted by a host that can actually see it. If your project's
path is not in `manifests/fleet-repo-paths.json` for your machine, add it there.
