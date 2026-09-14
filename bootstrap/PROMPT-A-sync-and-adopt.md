# PROMPT A — Sync the bus, adopt what binds, install what's needed

Paste this first, in the project you want to join the fleet review. Any model can run it; it is
mechanical throughout. It does **no review** — it makes this project a member in good standing so
that PROMPT B has something to stand on.

Run it again whenever you have been away; step 4 is the part that pays off on every re-run.

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

**Derived artifacts do not follow a rotation on their own.** Measured on this machine
2026-09-13: the two auth surfaces rotated and re-aligned correctly, while
`.claude/machine-inventory.yaml` still carried the previous account in `managed_by` — an
inventory probed under one identity and attributed to another. So record the identity a derived
artifact was produced under, and treat a mismatch against the current account as stale rather
than as fact.

## 1. Sync the bus

Find the doctrine checkout: a binding in this project's `CLAUDE.md`, else a pointer in `docs/`,
else the machine convention (`C:\code\softwarefactory-fleet-doctrine` on this box — say so if you
reach this rung, because a path that happens to be right here is a guess anywhere else).

```bash
git -C "<doctrine>" rev-parse --abbrev-ref HEAD     # expect master
git -C "<doctrine>" status --short                  # note dirty/untracked BEFORE fetching
git -C "<doctrine>" fetch origin master
git -C "<doctrine>" merge origin/master --ff-only
```

Never `--force`, `reset --hard`, or `clean`; other sessions leave work here. Report distinctly:
`NON_FF`, `UNTRACKED_COLLISION`, `WRONG_BRANCH`, `DIRTY`, `UNREACHABLE` — they are different
problems with different fixes and the common mistake is to call them all "sync failed". On any
of them, stop.

## 2. Derive the machine inventory

```bash
ls -l ~/.claude/machine-inventory.yaml              # present? how old?
bash "<doctrine>/tools/probe-machine-inventory.sh"  # if absent, or older than your last CLI upgrade
```

The probe dispatches a sentinel challenge to each candidate model and records only ids that
answer it. It does not assert a table: a retired or mistyped id still replies — with an error,
at a byte count *larger* than a real answer — so neither exit code nor output size separates a
live model from a dead one. Inventory is machine-scoped, not per-project (binding rule R5).

## 3. Adopt or distinguish what binds

Read `<doctrine>/RULINGS.md` and `<doctrine>/README.md` (its Laws).

**The five rules of the review-honesty floor (R1–R5, owner ruling 2026-09-13) are binding and
are not subject to adopt-or-distinguish.** Read them, and confirm in your report that this
project can meet each one. If it cannot meet one, say which and why — that is a different act
from distinguishing it away in silence, and its filings will be read accordingly.

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
```

Three sources, and they are not the same:

- **`RECEIPTS.md` / `TRAPS.md`** — measured findings from sibling projects. These are the fleet's
  lateral channel: a trap another project paid for is one you get free. Read the entries since
  your last sync, not just the newest.
- **`adjudications/<subject>/*.md`** — other projects' filings. **Read siblings' filings, not
  only your own.** A finding grounded in another repo's test bench often names a defect your
  repo has too; you simply have not hit it yet. The subject's owner harvests these to rewrite
  the spec, but that is not the only use — the fastest way to find a defect is to read someone
  else's report of it.
- **`metrics/`** — the lane telemetry and price table. If another project measured a posture on
  hardware like yours, you do not need to re-measure it; if your hardware differs, your
  re-measurement is exactly the independent evidence the bus needs.

Where something you read applies here, act on it now or record why it does not.

## 5. Report

Doctrine head SHA and how far it moved. Inventory: which families available, how many ids
verified in each. R1–R5: can this project meet each one. Dispositions recorded, with their
subjects. What you harvested from §4 and what you did about it.

Then: **ready for PROMPT B**, or blocked and why.

---

Nothing here reviews anything, claims a seat, or spawns an agent. That is PROMPT B's job, and it
is deliberately a separate paste so that a failed sync cannot be mistaken for a failed review.
