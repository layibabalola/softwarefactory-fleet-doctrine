# PROMPT 1 — Sync the fleet doctrine repository

Paste this into the session that will run PROMPT 2, before PROMPT 2. It brings the doctrine
checkout to the bus head and leaves a receipt saying so. PROMPT 2 refuses to start without
that receipt.

---

## 1. Locate the checkout

Derive the doctrine repo path, in this order, and say which one answered:

1. A doctrine-repo binding in this project's `CLAUDE.md`.
2. A pointer in `docs/` naming the fleet doctrine checkout.
3. The conventional location for this machine: `C:\code\softwarefactory-fleet-doctrine`.

Step 3 is machine-specific, not universal. If you reach it, say so in the report — a path that
happens to be right here is not a derivation, and on another box it is a guess.

## 2. Sync

**If the path does not exist**, clone the bus:

```bash
git clone https://github.com/layibabalola/softwarefactory-fleet-doctrine "<path>"
```

**If it exists**, bring it forward without rewriting anything:

```bash
git -C "<path>" rev-parse --abbrev-ref HEAD     # expect master
git -C "<path>" status --short                  # note dirty + untracked BEFORE fetching
git -C "<path>" fetch origin master
git -C "<path>" merge origin/master --ff-only
```

Never `--force`, never `reset --hard`, never `clean`. Other sessions leave work in this
checkout; right now it carries untracked specs that exist nowhere else.

**Report which of these you hit — they are different problems with different fixes, and the
common mistake is to report them all as one:**

| What happened | Report as | What it means |
|---|---|---|
| merge refused, histories diverged | `NON_FF` | the bus moved in a way local cannot fast-forward to; a human merges |
| merge refused, untracked file would be overwritten | `UNTRACKED_COLLISION` | someone drafted a spec locally that upstream also added; neither copy is safe to discard |
| HEAD is not master | `WRONG_BRANCH` | a session left the checkout elsewhere; do not switch it silently |
| tracked files are modified | `DIRTY` | uncommitted local doctrine edits; do not merge over them |
| fetch failed | `UNREACHABLE` | network or credentials |

On any of these: **stop, report, write the receipt with that status, and do not proceed to
PROMPT 2.**

## 3. Write the receipt — on success as well as failure

```bash
git -C "<path>" log -1 --format='%H %ad' --date=iso
```

Write `.claude/doctrine-sync.json` **in the project repo, not in the doctrine checkout** — it
is a statement this project makes about its own readiness, and the doctrine repo is shared:

```json
{
  "status":    "SYNCED",
  "path":      "<doctrine checkout path>",
  "head":      "<full SHA>",
  "head_date": "<commit date>",
  "synced_at": "<now, ISO-8601>",
  "source":    "claude-md | docs-pointer | machine-convention"
}
```

On failure write the same file with `"status"` set to the code from the table and a `"reason"`
field.

**The success receipt is the point of this step.** A marker written only on failure cannot be
distinguished from a sync that never ran at all — and "never ran" is by far the more common
case, since it is what happens when someone skips straight to PROMPT 2. Absence of a failure
marker is not evidence of success. PROMPT 2 checks for `SYNCED` and a fresh `synced_at`
precisely so that skipping this prompt fails loudly instead of reviewing against stale doctrine.

## 4. Ensure the machine inventory

PROMPT 2 needs to know which providers and model ids this box can actually dispatch. That is a
property of the **machine**, so it lives once at `~/.claude/machine-inventory.yaml`, not once
per project.

```bash
ls -l ~/.claude/machine-inventory.yaml        # present? and how old?
```

If it is absent, or older than the last CLI upgrade or account rotation, derive it:

```bash
bash "<doctrine path>/tools/probe-machine-inventory.sh"
```

The probe dispatches a sentinel challenge to every candidate model and records only the ids
that answered it. It does not assert a table — a retired or mistyped id still replies, with an
error, at a byte count larger than a real answer, so neither exit code nor output size
separates a live model from a dead one. Ids that fail the challenge are written commented-out
and marked not dispatchable.

Report which families came back available and how many ids verified in each.

## 5. Report

Path, and which of the three derivations produced it. Status. Head SHA and its date. Whether
the checkout was cloned fresh or fast-forwarded, and by how many commits. Anything left dirty
or untracked that you did not touch.

Then: ready for PROMPT 2, or blocked and why.

---

**Idempotent.** Second run fast-forwards zero commits and rewrites the same receipt with a new
timestamp. Nothing here mutates history, discards local work, or pushes.
