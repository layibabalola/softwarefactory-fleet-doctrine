# PROMPT A — Sync the bus, adopt what binds, install what's needed

Paste this first, in the project you want to join the fleet review. Any model can run it; it is
mechanical throughout. It does **no review** — it makes this project a member in good standing so
that PROMPT B has something to stand on.

Run it again whenever you have been away; step 4 is the part that pays off on every re-run.

**Before §0: confirm where you are running.** Paste A (`bootstrap/README.md`) has already resolved
the project `T` and the checkout `D`. Reuse both and do not search again. "This project" means `T`,
and every write below goes under `T`, never under `D`. Stop with `FROZEN` if any instructions you
hold mark `T` read-only or archived. A path you could not read is `UNREADABLE`, not missing. Never
search for a substitute file.

---

## 0. Account parity — FIRST, before anything that reads a provider

Accounts cycle without warning. When one does, the desktop surface and the CLI credential store
do not necessarily move together, and the usual trigger for repairing that is the phrase "resume
our work" — which this prompt is not.

```bash
python tools/check-cli-auth.py          # or the project's equivalent; expect "MATCHED"
codex login status                      # NOT `codex auth status` -- no such subcommand
```

If the surfaces disagree, repair before continuing: `specs/cli-credential-synchronization.md`
describes the SessionStart hook and `-Auto` wizard that re-authenticate the CLI to match the
desktop. If no hook is installed on this box, re-authenticate manually and say so in the report.

**This check comes before §2's probe, and the order is not cosmetic.** A CLI pointed at a
depleted or mismatched account fails *every* model challenge in exactly the way a genuinely
absent model fails. The probe would then write `available: false` for a whole family, dispatch
would route to a degraded posture or refuse outright, and the review would run wrong — with an
auth cause and a capability-shaped symptom. The probe's guard refuses to write when *nothing*
verifies, but a partially depleted account produces a plausible inventory that is simply false.
Verify identity before deriving capability from it.

**Install the check as a SessionStart hook, once per machine**, so sessions that never run this
prompt still get it:

```bash
python "<doctrine>/tools/check-account-parity.py"      # verify it runs here first
```

Then register it in `~/.claude/settings.json` under `hooks.SessionStart` as a `command` hook
(merge — never replace the file; other settings live there). Verify it *fires*, don't assume:
prepend a sentinel write to the command, start any session, confirm the sentinel, then strip it.
A hook that is configured but never fires is the exact gap R6.3 exists to close.

**There is no circular dependency here**, though it looks like one. Installing the hook is a
filesystem write, not a provider call — a desktop session installs it with no working CLI, and
the CLI can then rotate behind it. And the ordering above is what makes a fresh machine work at
all: this prompt checks parity *directly*, so the very first rotation on a box with no hook yet
is still caught. **The hook is an optimisation for sessions that never run PROMPT A, not the
primary mechanism.** Distribution is the same `git pull` that brought you this file — the
checker lives in `tools/` on the bus, so every project that syncs already has it.

**Derived artifacts do not follow a rotation on their own.** Measured on this machine
2026-09-13: the two auth surfaces rotated and re-aligned correctly, while
`.claude/machine-inventory.yaml` still carried the previous account in `managed_by` — an
inventory probed under one identity and attributed to another. So record the identity a derived
artifact was produced under, and treat a mismatch against the current account as stale rather
than as fact.

## 1. Sync the bus

Use the checkout `D` that paste A resolved, and re-check that its `origin` is the bus. Only when
you were not started by paste A, find the doctrine checkout yourself: a line of this project's
`CLAUDE.md` or `AGENTS.md` containing `softwarefactory-fleet-doctrine`, else the machine convention (`C:\code\softwarefactory-fleet-doctrine` on this box — say so if you
reach this rung, because a path that happens to be right here is a guess anywhere else).

Run these **one at a time**, and check each result before running the next. In a single block, a
wrong-branch checkout was fast-forwarded before anything stopped:

```bash
git -C "<doctrine>" rev-parse --abbrev-ref HEAD     # not master -> WRONG_BRANCH; do not run the rest
git -C "<doctrine>" status --short                  # non-empty -> DIRTY; do not run the rest
git -C "<doctrine>" fetch origin +refs/heads/master:refs/remotes/origin/master   # explicit refspec; fails -> UNREACHABLE
git -C "<doctrine>" merge origin/master --ff-only   # refused -> NON_FF or UNTRACKED_COLLISION
```

Never `--force`, `reset --hard`, `clean`, `stash`, `checkout` or delete in `<doctrine>`; other sessions
leave work there. Report distinctly: `NON_FF`, `UNTRACKED_COLLISION`, `WRONG_BRANCH`, `DIRTY`,
`UNREACHABLE`. They are different problems with different fixes, and the common mistake is to call
them all "sync failed". For each, quote `git -C "<doctrine>" rev-list --left-right --count
master...origin/master` and `git -C "<doctrine>" status --short`.

**`UNREACHABLE` stops.** Every other code is recoverable without touching the shared checkout, so
recover instead of stopping. A checkout older than the lineage, left dirty by another session, or
parked on a work branch still holds every object needed to read current doctrine:

1. Record the class: `git -C "<doctrine>" merge-base master origin/master`. Empty output means
   `LINEAGE_REPLACED`, otherwise `DIVERGED`. Also quote `git -C "<doctrine>" log --oneline
   origin/master..master`. Leave the checkout's branch, index and tree exactly as they are.
2. Let `R` = `<doctrine>-origin`, a sibling folder. If `R` does not exist, run `git -C "<doctrine>"
   worktree add --detach "R" origin/master`. If `R` exists and `git -C "<doctrine>" worktree list
   --porcelain` lists it, stop `DIRTY` when `git -C "R" status --short` is non-empty, and otherwise run
   `git -C "R" checkout --detach origin/master`. If `R` exists and is not listed, stop
   `UNTRACKED_COLLISION`.
3. Use `R` as `<doctrine>` for §2–§5 and as `path` in §2b. Add `"diverged": {"checkout":
   "<original>", "code": "<code>", "class": "LINEAGE_REPLACED|DIVERGED", "local_only": <count>}` to the
   receipt. Report the original checkout as reconciliation the owner may schedule, not as a blocker.

`R` is a read copy. Only this procedure moves it, it holds no branch, and §4b never removes it. Write
to the bus only through a review branch (R7), never from `R`'s detached HEAD.

Syncing is not a boot-only act (RULINGS **R8**). Fetch again before any write to the bus, and after
any push leave the shared checkout level with `origin/master`, your review branches pushed, and your
worktrees removed — `bootstrap/lane-orchestrator.md` §4b is the procedure. A checkout left behind
`origin` is read as current by every session that opens it next.

## 2. Derive the machine inventory

```bash
ls -l ~/.claude/machine-inventory.yaml              # present? how old?
bash "<doctrine>/tools/probe-machine-inventory.sh"  # if absent, or older than your last CLI upgrade
```

The probe dispatches a sentinel challenge to each candidate model and records only ids that
answer it. It does not assert a table: a retired or mistyped id still replies — with an error,
at a byte count *larger* than a real answer — so neither exit code nor output size separates a
live model from a dead one. Inventory is machine-scoped, not per-project (binding rule R5).

## 2b. Write the readiness receipt

```bash
git -C "<doctrine>" log -1 --format='%H %ad' --date=iso
```

Write `.claude/doctrine-sync.json` **in this project**, not in the doctrine checkout — it is a
statement this project makes about its own readiness, and the bus is shared:

```json
{ "status": "SYNCED", "path": "<doctrine checkout>", "head": "<full SHA>",
  "previous_head": "<the head from the receipt this one replaces, or null on first run>",
  "synced_at": "<now, ISO-8601>", "parity": "MATCHED|REPAIRED|UNVERIFIED",
  "inventory": "<path to the inventory that answered>" }
```

**Unless T's own gates forbid an untracked file there.** A governed factory can hold a frozen review
candidate whose integrity gate fails closed on any unreviewed path. For such a project, an in-tree
receipt halts the factory. Measured 2026-09-14 (adobe-ingester): a receipt written by this section
blocked every orchestrator commit for about four hours (Adobe `HUB.md` heading
`PREFLIGHT FAILURE Q-034 rev3 | SHARED WORKSPACE UNREVIEWED DOCTRINE RECEIPT`, then seven checkpoints).
Before writing, read T's operating contract (`FACTORY.md`, `AGENTS.md`, `CLAUDE.md`, or a `.factory/`-style
tree). If it names a frozen or review-state candidate, a candidate-integrity check, or files with
exclusive owners, or if you cannot tell, write the receipt **outside T** instead, at
`<home>/.claude/doctrine-sync/<basename of T>.json` (home written out in full), and say so in the report.
Never add an ignore or exclude entry so that an in-tree receipt passes: that edits the gate you would be
tripping.

**Read the old receipt's `head` before you overwrite it** and carry it as `previous_head`. It is
§4's `<your-last-sync-sha>`, and the receipt is the only place it lives. Overwrite first and §4's
range collapses to empty (`HEAD..HEAD`), so the harvest reports nothing new every time. Measured
2026-09-14 (agent-bridge): that is how a TRAPS entry recording the exact PROMPT-B failure about to
happen went unread.

On any blocker from §0–§2, write the same file with `status` set to that blocker's code.

**Write it on success, not only on failure.** The review orchestrator refuses to start without
this receipt, and that refusal is the point: a marker written only when something breaks cannot
be told apart from a sync that never ran — and "never ran" is the common case, because it is
what happens when someone skips straight to PROMPT B. Absence of a failure marker is not
evidence of success.

## 3. Adopt or distinguish what binds

Read `<doctrine>/README.md` (its Laws) and the binding rulings in `<doctrine>/RULINGS.md`. RULINGS is
over 2,000 lines, so a first-page read ends long before them, and it also contains older bullets that
begin "R1". **Locate the binding rulings by heading, then read each section whole:**

```bash
grep -nE "^## .*(review-honesty floor|R6: account parity|R7: review branches|R8: work with the bus|R9: a posture)" "<doctrine>/RULINGS.md"
```

Measured 2026-09-14 (Conjugal, Haiku session): a truncated read matched a 2026-08-09 "R1 independence"
bullet instead of the 2026-09-13 floor, and the report marked R1–R5 "can meet" without having read
them. **In the report, quote each rule's title line** (`R1 - A session below the review floor…`); a
claim about a rule with no quoted line is invalid.

**The five rules of the review-honesty floor (R1–R5, owner ruling 2026-09-13) are binding and
are not subject to adopt-or-distinguish.** Read them, and confirm in your report that this
project can meet each one. If it cannot meet one, say which and why — that is a different act
from distinguishing it away in silence, and its filings will be read accordingly.

**R7 — review branches always push (owner ruling 2026-09-14) is binding on the same terms.** Any
review branch this project commits is pushed to `origin` at once and verified with `ls-remote`;
never master, never force. Confirm this project can meet it, and push any review branch it
already holds local-only (`git branch --list 'review/*'` vs `git ls-remote origin 'refs/heads/review/*'`).

**R9 — a posture is named only when it ran in full (owner ruling 2026-09-14) is binding on the same terms.** A review
filing's `posture:` line is copied from `tools/review-posture/review_posture.py posture`, which names the posture only
when every lane of every role cleared its sentinel. If this project holds a filing labelled with a posture it did not
run in full, relabel it `-PARTIAL` or re-run it (R9.5).

Everything else on the bus is `PROPOSED` or a ratified portable core with **zero runtime
authority until this project adopts it**. For each one that is relevant to you, record a
disposition in **your own** `specs/<project>.md` on the bus (Law 2: you write only that file):

```
ADOPT(<exact commit or subject sha>)            — verified locally, folded
DISTINGUISH(<subject>, <reason>)                — does not fit this project, and why
```

A disposition is a statement you verified something, so verify it. An `ADOPT` nobody tested is
the same defect as a review nobody ran.

## 4. Harvest what the fleet has learned since you last synced

This is the step that makes the bus worth more than a spec folder, and the one most easily
skipped.

```bash
git -C "<doctrine>" log --oneline <your-last-sync-sha>..master -- RECEIPTS.md TRAPS.md RULINGS.md
ls -t "<doctrine>"/adjudications/*/*.md | head
git -C "<doctrine>" ls-remote origin 'refs/heads/review/*'   # filings not yet on master (R7.5)
git -C "<doctrine>" fetch origin 'refs/heads/review/*:refs/remotes/origin/review/*'
grep -nE "PROMPT-?B|PROMPT-?A|lane-orchestrator|bootstrap/" "<doctrine>/TRAPS.md"   # traps against the prompts you run next
```

The `<your-last-sync-sha>` is `previous_head` from §2b; with no previous receipt, read every entry
the grep above finds. The grep runs **regardless of the range**: a trap against a bootstrap file can
land before your last sync and still be unfixed in the file itself, and TRAPS.md is thousands of
lines long, so a top-of-file read never reaches it. `Already up to date` from a pull proves the
checkout is current; it does not prove that no trap applies to the prompt you are about to run.

Three sources, and they are not the same:

- **`RECEIPTS.md` / `TRAPS.md`** — measured findings from sibling projects. These are the fleet's
  lateral channel: a trap another project paid for is one you get free. Read the entries since
  your last sync, not just the newest.
- **`adjudications/<subject>/*.md`** — other projects' filings, on `master` **and on every
  `origin/review/*` branch** (read one with `git show origin/review/<branch>:adjudications/…`). **Read siblings' filings, not
  only your own.** A finding grounded in another repo's test bench often names a defect your
  repo has too; you simply have not hit it yet. The subject's owner harvests these to rewrite
  the spec, but that is not the only use — the fastest way to find a defect is to read someone
  else's report of it.
- **`metrics/`** — the lane telemetry and price table. If another project measured a posture on
  hardware like yours, you do not need to re-measure it; if your hardware differs, your
  re-measurement is exactly the independent evidence the bus needs.

Where something you read applies here, act on it now or record why it does not.

**Every project dogfoods the fleet factory kernel.** If `adjudications/factory-kernel/<this project>.md` does not exist on
master or any `origin/review/*` branch, or its `kernel:` revision is older than `specs/fleet-factory-kernel.md`'s header,
report it and name `bootstrap/PROMPT-K-dogfood-kernel.md` as the next step after this sync.

**If this project owns a subject, check whether its filings are answered — every sync:**

```bash
python "<doctrine>/tools/harvest-status.py" --all        # one line per subject: spec=specs/<owner>-… open=<n>
python "<doctrine>/tools/harvest-status.py" <subject>    # for each subject whose spec is yours
```

`open>0` on a subject you own means filings sit unanswered: report it and name
`bootstrap/PROMPT-3-harvest.md` as the next step. Without this check nothing tells an owner that
anyone filed. Measured 2026-09-14: Conjugal's subject had two unharvested filings for a day, and
finding that out took an ad-hoc search across branches.

## 5. Report

Doctrine head SHA and how far it moved. Inventory: which families available, how many ids
verified in each. R1–R9: for each, its quoted title line and whether this project can meet it. Dispositions recorded,
with their subjects. What you harvested from §4 and what you did about it. For subjects this project owns: the
`harvest-status.py` line (open count).

Then: **ready for PROMPT B**, or blocked and why.

---

Nothing here reviews anything, claims a seat, or spawns an agent. That is PROMPT B's job, and it
is deliberately a separate paste so that a failed sync cannot be mistaken for a failed review.
