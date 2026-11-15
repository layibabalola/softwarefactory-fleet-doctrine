# `path-health/` — one ack per fleet machine

`path-health/<MACHINE>.json` is a machine's ack of `doctrine/pattern-path-defense-2026-11.md`, and
the record of its PATH health. **The artifact IS the ack** (same contract as
`heartbeats/README.md` "How to ack"). There is no roster file: the reader derives the machine list.

| | |
|---|---|
| **Writer** | `tools/Repair-MachinePath.ps1 -Check -Publish` on that machine. Single writer per file: the file name is the writer's `COMPUTERNAME`. |
| **Reader** | `pwsh -NoProfile -File tools/Get-FleetPathHealthStatus.ps1 [-StaleDays 7] [-Json]`: ACKED / STALE / ABSENT / DISTINGUISHED / BLOCKED |
| **Push rule** | on content change, or when the record is over 24 h old (law 3) |
| **What travels** | counts, verdict, finding tokens, ordinal runner labels (`runner-1`, …), tool commit. No paths, no user names, no runner folder names (a folder may be named after an account), no PATH entry text (law 4). |
| **Runner labels** | ordinals over the sorted runner folder names, so adding or removing a runner renumbers the others and publishes once as `changed`. Accepted: the alternative carries the names. |
| **Validation** | the reader requires top-level `schema` = `fleet-path-health.v1`, `machine` equal to the file name, `verdict` HEALTHY/UNHEALTHY, a `published_utc` of exactly `yyyy-MM-ddTHH:mm:ssZ` no later than now + 10 min, `findings` as an array of strings, and a verdict consistent with its findings (HEALTHY iff none). Anything else is UNEVALUABLE (exit 2), never a pass. |
| **CI** | `.github/workflows/path-health.yml` runs when the tools change, not on each ack push: an ack is checked by the reader that reads it. |
| **Not expressible here** | DISTINGUISH and BLOCKED: one line each in `RECEIPTS.md`, as `PATH-HEALTH: DISTINGUISH <MACHINE> - <reason>` or `PATH-HEALTH: BLOCKED <MACHINE> - exit <code>: <message>` |

The one command each machine runs (no Administrator) is in
`doctrine/pattern-path-defense-2026-11.md` section 5.

## Record shape (`fleet-path-health.v1`)

```json
{
  "schema": "fleet-path-health.v1",
  "machine": "VIRTUAL-TEN",
  "published_utc": "2026-11-15T00:47:18Z",
  "tool_commit": "<bus HEAD the tool ran from>",
  "verdict": "UNHEALTHY",
  "findings": ["user-dead:1"],
  "total_chars": 2240,
  "user": { "chars": 696, "segments": 14, "dead": 1, "duplicates": 0, "empty": 0, "dead_dotnet_tools": 1 },
  "machine_scope": { "chars": 1543, "segments": 38, "dead": 0, "duplicates": 0, "dead_dotnet_tools": 0 },
  "cmd_where_git": "PASS",
  "runners": []
}
```

`dead_dotnet_tools` counts the leak class named in the pattern: dead `...\.dotnet\tools` entries
left behind by a per-run `DOTNET_CLI_HOME`. If it rises between two acks, a gate on that machine is
still leaking.
