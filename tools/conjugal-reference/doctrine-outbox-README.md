# Doctrine outbox — findings reach the fleet bus by file, not by memory

A finding or improvement with cross-project value is a **file in the same commit as the fix**.
The harvest steward drains it onto the bus on its next 15-minute tick. Nothing here depends on a
session remembering a directive; measured 2026-09-18, that dependency lost a real fix until the
owner asked.

**Derive state; this file holds none:**

```bash
python "C:\code\Conjugal\coordination\tools\doctrine_outbox.py" debt                 # unsent items + age
python "C:\code\Conjugal\coordination\tools\doctrine_outbox.py" check-range          # would origin/master..master pass the push guard?
python "C:\code\Conjugal\coordination\harvest\harvest_runner.py" outbox              # drain now (what the tick does)
python "C:\code\Conjugal\coordination\harvest\harvest_runner.py" status              # receipts, incl. step=outbox rows
git -C "C:\code\Conjugal" ls-tree -r --name-only master -- coordination/doctrine-outbox/sent   # what landed, with bus_commit inside
```

## Writing an item

File: `coordination/doctrine-outbox/<yyyymmdd>-<slug>.md` (slug: lowercase, digits, hyphens).

```markdown
---
target: RECEIPTS.md            # RECEIPTS.md | TRAPS.md | RULINGS.md  (specs are steward-owned; not here)
kind: receipt                  # receipt | trap | ruling
source_commit: PENDING         # PENDING = "the commit that adds this file"; or an explicit sha
law4: attested                 # required, then SCREENED — see below
# ratified_by: <RULINGS anchor>   required for RULINGS.md; sessions do not mint law
---
### <project>, <date> — <one-line title in the bus file's own grammar>

<body, <= 450 words, in the entry grammar of the target file>
```

The commit that adds it carries the trailer `Doctrine-Export: outbox`.

## Declaring "nothing to export"

A commit that touches a **finding path** — `coordination/tools/*.py`, `coordination/harvest/*.py|ps1`,
`CLAUDE.md` — must say so, one line in the commit message:

```
Doctrine-Export: none
```

Ordinary commits elsewhere carry nothing. The set is deliberately narrow: those paths are where
findings have historically come from, and floors never commit there.

## What enforces it

| Seam | Tool | Behaviour |
|---|---|---|
| `git push` of `master` | `.git/hooks/pre-push` → `doctrine_outbox.py pre-push` | **Refuses** (exit 1) when a pushed commit touches a finding path without a trailer, declares `outbox` without adding an item, or adds an item that fails schema / Law 4. Local facts only — no bus round-trip, so a push never becomes a two-repo transaction. Installed idempotently by the SessionStart hook on every machine. |
| Turn end | `Stop` hook → `doctrine_outbox.py stop` | Blocks **once** (`stop_hook_active` ends the loop) when a commit from the last 24 h would be refused at push. A nudge; the gate is pre-push. |
| Every 15 min | `harvest-gate.ps1` → `harvest_runner.py outbox` | **Drains** committed, unsent items through the steward's `publish_bus` (fetched tip, path census, byte-prefix append-only check, `ls-remote` proof) and moves each to `sent/` with `bus_commit:` through the steward's commit gateway. No model. |
| Session start | `doctrine_outbox.py session-start` | Prints unsent debt (informational). |

**Law 4 is a screen, not an attestation.** The body is refused if it carries an email address, an
account/org uuid, a `coordination/lanes|comms` path, `HUB.md`, `loops.json`, a token pattern, or
more than 450 words. The author writes the body; a model never composes an export.

**Idempotency.** Each appended block ends with `<!-- outbox:<key> conjugal:<sha> -->`, `key =
sha256(source_commit, target, body)[:16]`. A key already on the bus tip is not re-appended, so a
crash between the bus push and the `sent/` move only repeats the move.

**Single pusher.** Only the harvest steward writes to the bus's append-only tails (TRAPS 2026-09-14:
two writers on one tail). A session that wants a finding on the bus *now* runs
`harvest_runner.py outbox` itself — same code, same census, same proof.
