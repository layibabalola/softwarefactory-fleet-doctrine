# Factory-kernel harvest ledger (steward-written, append-only)

One row per filing per harvest. `specs/fleet-factory-kernel.md` §5 reads this ledger, never a single filing, to decide
finalisation. Verdict counts use FIT/FRICTION/BREAK/N/A/UNEXERCISED.

| date | harvest | filing | blob | kernel | profile | subjects | FIT | FRICTION | BREAK | N/A | UNEXERCISED | unresolved BREAKs | arbiter |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-14 | 20260914T221904Z-51d5a96b | adobe-ingester | 7f1aea3bb5af6188556895c4c86a2c70c0c3a6e4 | r1 (text at 45f4a2c; now r2) | code@r1 (now r2) | 0 end-to-end (1 blocked at acceptance closure) | 8 | 8 | 1 | 0 | 0 | 0 (K12 BREAK adopted into §3) | gpt-6-astra (steward seat; not a steward filing) |
| 2026-09-14 | 20260914T221904Z-51d5a96b | agent-bridge | cc45e75f42af2f371bd18eb1f9bcbcef5718926e | r1 (now r2) | code@r1 (now r2) | 0 end-to-end (1 review run, not closed) | 3 | 9 | 0 | 0 | 3 | 0 | gpt-6-astra (steward seat; not a steward filing) |
