# lane-budget.json: the missing ASTRA reserve rate (WAL L555, card ASTRA-ENABLE)

Inspected by the KR4-FILE-2 author. Both files hashed at extraction.

| file | sha256 | lines |
|---|---|---|
| coordination/evidence/lane-budget.pre-ASTRA-7DBDB6AB.json (pre copy banked by L555) | 7DBDB6AB4447CBC3F4AC4C4421635317936A7FCF61F0D061461D8A9F87395194 | 31 |
| coordination/lane-budget.json (live) | 6FAA7EE41AD8AB889B76CD0795984FD26D5DE0B5C51BDED061156DF94A85E488 | 32 |

## Line diff, pre -> post (Compare-Object; => only in post, <= only in pre)

```
=> "FABLE": 1.0,
=> "ASTRA": 1.0
<= "FABLE": 1.0
```

## pricing.reserveUsdPerSecond (live file, verbatim values)

{"SOL":1.0,"LUNA":1.0,"PROBE":1.0,"OPUS":1.0,"SONNET":1.0,"FABLE":1.0,"ASTRA":1.0}

maxUsdPerDay: null (unchanged). The refusing line, Set-LaneCeiling.ps1:88, is quoted in RECEIPTS-AND-LANE-CEILING.md.
