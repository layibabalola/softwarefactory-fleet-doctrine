# RULING CANDIDATE — every member project exports findings mechanically: capture gate + unattended drain + measured debt (r1)

- **Proposed by:** `mlv-app` (hub session, Claude Code desktop), 2026-09-28.
- **Status:** CANDIDATE for `RULINGS.md`. Not doctrine until appended.
- **Owner instruction** (Layi, 2026-09-28, in chat, verbatim):
  > "Is publishing novel findings and fixes to the bus not mechanical? I thought we made it mechanical. We are
  > losing a lot of good learnings from all projects in fleet when we dont publish them. The idea is to get a
  > constantly improving constantly learning constantly sharing system with evidence from several projects across
  > the fleet. This would eventually create a hardened efficient and seamless software factory and development
  > process across all projets"

## Measured, not asserted (bus `origin/master`, last 400 commits, 2026-09-28)

| member | export path | outbox commits |
|---|---|---|
| conjugal | reference outbox: item file in the fix's commit, pre-push refusal, Stop nudge, 15-min unattended drain | 42 |
| agent-bridge | ported `tools/doctrine_outbox.py`; its README: "Nothing here runs on its own" (card DOCTRINE-OUTBOX-WIRE open); drained by hand | 13 |
| mlv-app, cloudvore, airmypc, dng-auto-processor, adobe-ingester | none: direct hand-written commits, only when a session remembers | 7 / 9 / 5 / 15 / 1 direct |

One member of the fleet has the mechanism the 2026-09-26 software-factory ruling assumes ("publish ... through your
sanctioned publisher ... its outbox"). For the rest, export depends on a session's memory, which the reference
outbox's own README measured losing a real fix on 2026-09-18. mlv-app's three traps of 2026-09-28 reached the bus only
because the owner asked.

## Proposed rule

Every member project with a `code` profile runs an outbox with all three parts, or DISTINGUISHES item by item:

1. **Capture at a seam the project always crosses.** A finding is a file (`<yyyymmdd>-<slug>.md`, front matter
   `target/kind/source_commit/law4`) committed with the change that teaches it. A gate refuses, or blocks once, when a
   change on a finding path lands with neither an item nor an explicit `Doctrine-Export: none`. **The gate must not
   live only in tracked project settings.** A hook registered in a tracked `.claude/settings.json` is absent from
   any checkout at a ref that predates it (mlv-app TRAPS 2026-09-28, item 1). Register it user-level, cwd-scoped,
   or at a seam that does not depend on the checked-out ref (pre-push installed per clone, OS task).
2. **Unattended drain.** An OS-scheduled task, not a session, drains committed unsent items. It is idempotent
   (`<!-- outbox:<key> <project>:<sha12> -->`), append-only byte-prefix checked, and retries from scratch on a
   non-fast-forward. It proves each push with `ls-remote` and survives an account rotation.
3. **Measured debt.** The member's bus heartbeat reports unsent-item count and oldest age. Debt older than 24 h is
   a heartbeat finding, not silence.

Law 1 and Law 4 are unchanged: a model never composes an export unattended; the session that learned the thing writes
the item; the drain only moves bytes and screens them.

## Reference implementations (adopt, do not re-invent)

- conjugal's `coordination/tools/doctrine_outbox.py` + `harvest_runner.py outbox` (full, pre-push + Stop + drain).
- agent-bridge's `tools/doctrine_outbox.py` (a port; `PROJECT` is a module constant, drain `--push` with ls-remote
  proof; unwired). A member porting it should parameterise the project name, not fork the file.

## Falsifier

After a member records ADOPT: a bus commit carrying that member's findings that is not `outbox(<member>)`, or a
heartbeat showing outbox debt older than 24 h, falsifies its adoption.

## Adoption started

mlv-app declares card DOCTRINE-OUTBOX-ADOPT-MLV-1 (2026-09-28): port agent-bridge's tool, capture gate as a
user-level cwd-scoped hook, OS-scheduled drain, backfill of the project's unpublished learnings.
