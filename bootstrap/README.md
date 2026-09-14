# Bootstrap — joining the fleet review from any project, on any machine

**Two pastes.** Everything else is reached by pointer.

| | You paste | Who runs it | What it does |
|---|---|---|---|
| **PROMPT A** | ✅ | your session, any model | Syncs the bus, derives the machine inventory, records this project's adoptions, and harvests what the fleet has learned since you last synced. No review. |
| **PROMPT B** | ✅ | your session, any model | Decides the request is above its tier and spawns **one** chip naming the model it recommends. No review. |
| `lane-orchestrator.md` | — | that chip | Dispatches cross-family lanes over the provider CLIs, arbitrates, files `adjudications/<subject>/<project>.md`. |
| **PROMPT K** | ✅ | every project, after A | Runs this project's real work through `specs/fleet-factory-kernel.md` and files FIT/FRICTION/BREAK evidence to `adjudications/factory-kernel/`. |
| **PROMPT 3** | — | the project that **owns** the subject spec | Harvests every filing, adjudicates across projects, rewrites the spec, publishes dispositions back. |

A and B are separate pastes on purpose: a failed sync should never be mistakable for a failed
review, and A is cheap enough to re-run whenever you have been away.

## The pastes

**A**, in the project you want to join, on any machine. Paste the whole block. It finds an existing
doctrine checkout by its origin URL, fetches the latest, clones only when none exists, and reads PROMPT A
from `origin/master`. No path is hard-wired to one box:

```text
Bootstrap PROMPT A of the fleet doctrine bus (https://github.com/layibabalola/softwarefactory-fleet-doctrine, public, branch master). Do the steps in order and quote each command's output. Never search the disk beyond step 2's list. Never merge, force, reset, clean, stash or switch branches in the doctrine checkout: other sessions share it, and PROMPT A §1 owns its sync. Stop codes: FROZEN, WRONG_PROJECT, UNREADABLE, UNREACHABLE. A stop ends the session's work; never work around one.

1. TARGET. T = output of `git rev-parse --show-toplevel` (else this session's working directory). Print T. STOP FROZEN if T's own instructions, or this machine's user-level instructions, mark T read-only, archived or frozen (frozen is per machine: never assume it from a project name). STOP WRONG_PROJECT if T is your home folder, or `git -C "T" remote get-url origin` names softwarefactory-fleet-doctrine. Every write PROMPT A makes goes under T, never under the doctrine checkout.
2. FIND D. Try, in order: a doctrine path named in T's CLAUDE.md, AGENTS.md or docs/; the folder beside T's main checkout (parent of the first `worktree ` line of `git -C "T" worktree list --porcelain`) + /softwarefactory-fleet-doctrine (if T is not a git repo, the parent of T instead); C:\code\softwarefactory-fleet-doctrine (Windows only); your home directory written out in full (never `~` inside quotes) + /code/softwarefactory-fleet-doctrine. For each: `git -C "<path>" remote get-url origin`. It qualifies if the URL contains layibabalola/softwarefactory-fleet-doctrine, ignoring case; then D = the first `worktree ` line of `git -C "<path>" worktree list --porcelain`. Replace <path> with the real path in every command; never run a command containing < or >.
3. CLONE only if every rung in step 2 failed with "cannot change to" or "not a git repository" (a rung that does not apply, such as no path named or not Windows, counts as failed that way). If any rung failed any other way (permission, sandbox, refused tool), STOP UNREADABLE with the errors. Clone to the step-2 "beside T" path, printed in full. If that path is inside T, STOP WRONG_PROJECT. `git clone -b master https://github.com/layibabalola/softwarefactory-fleet-doctrine "<that path>"`. If it says "already exists", go back to step 2 once. Set D to it.
4. LATEST. `git -C "D" fetch origin +refs/heads/master:refs/remotes/origin/master` (exactly this refspec: a plain `fetch origin master` leaves origin/master stale on checkouts with no fetch rule). On failure, note UNREACHABLE for PROMPT A §1 and continue.
5. READ. `git -C "D" show origin/master:bootstrap/PROMPT-A-sync-and-adopt.md` (the pushed version, not local edits). Only if that fails, read D/bootstrap/PROMPT-A-sync-and-adopt.md with your file tool and say it may be stale. Line 1 must start "# PROMPT A", else STOP UNREADABLE. If shell commands are refused anywhere above, STOP UNREADABLE: the human must grant this session the doctrine folder or paste from a project that has it. Do not fetch the file from the web.
6. REPORT, quoting outputs rather than summarising: T; each step-2 rung and its result; D and how it was found or cloned; the fetch result; the source and line 1 of what you read. Then follow PROMPT A for project T, with D as <doctrine>. If PROMPT A §1 stops, stop, and read nothing further from D.

Re-pasting is safe. Step 2 finds an existing clone. Nothing here writes except the one clone and `fetch`.
```

**B**, once A reports ready:

```text
Read .claude/doctrine-sync.json in this project. If it is missing or its status is not SYNCED, run paste A first and stop. Otherwise D = its "path". Run `git -C "D" fetch origin +refs/heads/master:refs/remotes/origin/master`, then follow the output of `git -C "D" show origin/master:bootstrap/PROMPT-B-begin-review.md`. The subject is specs/conjugal-approach-a-v7.4.md; THIS project is the test bench. Use D as <doctrine>. Never search the disk for the file.
```

### Why the paste carries the locate step

A session cannot follow a guard inside a file it cannot open. Measured 2026-09-14 (Dell XPS 17): a
Haiku session opened in `DngAutoProcessor - Claude` was given the absolute path to PROMPT A, reported
that it "doesn't exist", and ran six shell commands searching for it. The file was there, and a
Conjugal session read it the same hour. So the paste finds the checkout itself and reads through git.
Two rounds of Opus review (three drafters, then three attackers) shaped it:

- **It clones only on true absence.** A session without access sees every path fail, and would
  otherwise clone a second bus.
- **It never merges.** A paste-side `merge --ff-only` fast-forwarded a non-master branch in a test,
  and it ran before §1 recorded DIRTY/WRONG_BRANCH. §1 stays the only sync owner.
- **It reads `origin/master`, not the working tree.** The shared checkout is often ahead with
  unpushed commits.
- **It fetches with an explicit refspec.** Measured 2026-09-14 on UltraMagnus: `fetch origin master`
  printed only `-> FETCH_HEAD`, `origin/master` stayed at a commit older than `bootstrap/`, and the
  read failed with "does not exist in 'origin/master'". Reproduced on a checkout with no
  `remote.origin.fetch`; `+refs/heads/master:refs/remotes/origin/master` updates it every time.
- **Frozen is per machine.** A project frozen on one box can be live on another, so the paste names
  no project.
- **It uses `--porcelain`, never `~` inside quotes, and never `../`.** Plain `worktree list` breaks
  on paths with spaces. `~` does not expand inside quotes in any shell. `../` lands inside a project
  that is itself a worktree.

**Never paste into a frozen archive.** An archive may not mark itself as frozen, and PROMPT A writes
into the project it runs in.

Expect B to refuse to review, ask once with a model pre-selected, and hand back a chip. Set the
model picker to what it names **before** clicking — a chip inherits the picker at click time —
and the chip re-checks its own model and stops if it is below what was asked for.

## The bus is lateral, not just vertical

The obvious flow is upward: projects file, the spec owner harvests, the spec improves. That is
PROMPT 3, and it is only half the value.

**The other half is sideways, and it is free.** A finding grounded in another project's test
bench usually names a defect your repo has too — you simply have not hit it yet. Reading a
sibling's filing is the cheapest defect-finding available anywhere on this bus, because someone
else already paid for it. PROMPT A §4 makes that a step rather than a virtue: on every sync,
read `RECEIPTS.md` / `TRAPS.md` since your last sync, and read siblings' filings in
`adjudications/`, not only your own.

So: **a finding that generalises beyond its subject belongs in `RECEIPTS.md` or `TRAPS.md` as
well as in the filing.** A filing is indexed by subject and read by that subject's owner; a
receipt is read by everyone. Putting a portable lesson only in a filing hides it from every
project that is not reviewing that spec.

## The five rules that are not optional

Binding fleet-wide by owner ruling, 2026-09-13 (`RULINGS.md`; measurements in
`ruling-candidates/mandatory-review-floor-r1.md`). They constrain the honesty of a report, never
its content:

**R1** a session below the review floor escalates or fails closed — it never reviews at a lower
tier. **R2** completion is a sentinel the lane emits, never an exit code or a byte count.
**R3** a cross-family claim is computed from which families cleared the sentinel, never
asserted. **R4** every project-scoped reference names its project. **R5** provider inventory is
machine-scoped and probe-derived.

Each exists because it failed on this fleet within one week, silently, and reported green.

## What a filing must contain

`adjudications/<subject>/<project>.md`, one file per project, single writer. Header declares
`project`, `providers`, `seats`, `rubric_id`, and a `posture:` line copied from
`tools/review-posture/review_posture.py posture` (RULINGS R9). Then findings, one per line:

```
§<section> | "<quote, <=25 words>" | <defect, <=40 words> | REPLACES: "<anchor>" -> "<new>" | PROOF: <what would falsify it>
```

**The test-bench rule is the admission criterion:** every finding names how the defect manifests
in *your* repo — a path, a tool, a measured number — or it goes under `## Untested`. That is what
makes a disagreement between two filings a disagreement between two real environments rather
than two opinions.

## Measured, so you can argue with it

From the first run of this pipeline (`RECEIPTS.md`, 2026-09-13, Dell XPS 17): three Opus lanes
at medium effort on disjoint slices found 26 findings in **165 s** for $2.94; one Opus lane at
xhigh on the whole subject found 27 in **781 s** for $3.63. Near-parity on yield, 4.7× on wall
clock, cost per finding within 20% across every arm that worked.

Read that as: **the active ingredient is disjoint slicing, not model strength.** A swarm does not
buy cheaper findings — it buys latency and forced coverage, because slices examine dimensions a
single lane chooses away from. Budget by the coverage you need, not in the hope that swarming is
cheaper.

One arm produced nothing: Sonnet at max effort spent 47,449 thinking tokens and 19 minutes
planning the review, then asked permission to run it — returning `is_error: false`,
`stop_reason: end_turn`, `terminal_reason: completed`. **Effort is not monotonic in usefulness.**
Run autonomous lanes at medium; reserve the top of the range for a step where something can
receive a question. R2 is why that arm scored zero instead of counting as a lane.

Re-measuring any of this on your own hardware is not redundant — it is the independent evidence
`specs/cli-orchestration-standard.md` needs to stop being author-measured on one box.
