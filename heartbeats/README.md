# `heartbeats/` — cross-machine sync liveness

**The gap this closes, stated precisely so this surface does not become a second tool.**
`tools/fleet-sweep.mjs` answers *"is every member cloned on THIS box current?"* — correctly, and it
is the only tool that decides what "current" means. But it is **box-scoped**: every member without a
clone here reports `no-local-clone`, which is information, not an error. The fleet spans machines,
so from any one box most of it is invisible. A board that never installed the duty and a board whose
task silently stopped both look like a quiet board from outside. That is how eleven of twelve
projects went unnoticed: the evidence existed and never left the machine.

Heartbeats are how that evidence crosses machines. **This surface adds no opinion about currency**
— it publishes what the sweep already decided. If it ever starts deciding, it has become the second
tool and should be deleted.

## Contract

| | |
|---|---|
| **One file per board** | `heartbeats/<board-id>.json`. Single writer (law 2), enforced against the source artifact, not against a CLI argument. |
| **Membership** | **Derived**, never declared twice: `specs/<project>.md` minus `specs/fleet-*.md`, the same rule `fleet-sweep.mjs` uses, so the two can never disagree about who exists. |
| **Publisher** | `tools/Publish-BoardHeartbeat.ps1 -BoardId <id> -ProjectRoot <root> -BusRoot <bus>` |
| **Reader** | `tools/Get-FleetHeartbeatStatus.ps1 [-StaleHours 12] [-Json]` |
| **Source** | `<root>/.claude-state/doctrine/fleet-sweep-receipt.json` — written by `node tools/fleet-sweep.mjs --json-out <path>`. A legacy `last-run.json` is accepted as a fallback. |

> A `heartbeats/ROSTER.md` was shipped with the first draft of this surface and **withdrawn the same
> day**. It argued absence was underivable without a declared roster. That was wrong:
> `fleet-sweep.mjs` had already published the rule — the bus layout is the authority, and a registry
> file is a second authority for one fact, which this fleet has already paid for.

## Record shape (`fleet-board-heartbeat.v1`)

```json
{
  "schema": "fleet-board-heartbeat.v1",
  "board": "dng-auto-processor",
  "machine": "ULTRA-MAGNUS",
  "published_utc": "2026-08-30T20:29:03Z",
  "source": "fleet-sweep.v1",
  "sync_ran_utc": "2026-08-30T20:29:02.950Z",
  "verdict": "CLEAN",
  "delta_count": 0,
  "bus_cursor": "d177735bcf6e44e3287faab2071dc913412fda9c",
  "detail": "current; box declared=10 cloned=1 unfolded=0 failed=0"
}
```

`published_utc` is when this record reached the bus; `sync_ran_utc` is when the sweep it reports on
actually ran. **They differ, and the difference is a defect detector** — a board whose sweep is dead
but whose publisher still fires shows a fresh `published_utc` over a frozen `sync_ran_utc`. The
reader classifies that as `PULSE-ONLY`, because a pulse is not progress.

`source` names the artifact the record came from. It exists because this publisher's first source
was withdrawn out from under it and it went on reporting the frozen file as healthy.

## Reading it

- **ALIVE** — published within `-StaleHours` (default 12: two missed refreshes, not one).
- **PULSE-ONLY** — publisher alive, the duty it reports on is not.
- **STALE** — published, then stopped advancing. Silence is the alarm.
- **ABSENT** — a derived member with no file at all. **Not the same failure as STALE.** ABSENT is a
  board with no duty installed, which is the fleet's actual measured scar. The discriminator is a
  missing key, not a low count.
- **UNEVALUABLE** — `specs/` or a heartbeat unreadable; exits non-zero rather than reporting zero
  problems, because a status tool that cannot fail is not a status tool.

## Why this is not a cadence push (law 3)

The publisher pushes only when content changes — source, verdict, cursor, delta count, machine, or
the sweep's own stamp — or when the record is older than `-RefreshHours` (default 6). Worst case is
4 commits per board per day. Cadence pushing is precisely what got this surface's predecessor tool
withdrawn; it is not repeated here.

## The failure this surface cannot fix by itself

Publishing makes darkness *visible*; it does not make anyone *look*. Until a board's wake path runs
the reader and acts on a non-zero exit, this is a dashboard nobody opens — the same shape as
`doctrine-sync.mjs` being found complete and unwired, and as fold markers existing for one project
of five. **A capability with no caller protects nothing.** Wire the reader into a path that runs
without anyone remembering to.
