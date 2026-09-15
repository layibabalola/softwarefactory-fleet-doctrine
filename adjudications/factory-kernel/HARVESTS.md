# Factory-kernel harvest ledger (steward-written, append-only)

One row per filing per harvest. `specs/fleet-factory-kernel.md` §5 reads this ledger, never a single filing, to decide
finalisation. Verdict counts use FIT/FRICTION/BREAK/N/A/UNEXERCISED.

| date | harvest | filing | blob | kernel | profile | subjects | FIT | FRICTION | BREAK | N/A | UNEXERCISED | unresolved BREAKs | arbiter |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-14 | 20260914T221904Z-51d5a96b | adobe-ingester | 7f1aea3bb5af6188556895c4c86a2c70c0c3a6e4 | r1 (text at 45f4a2c; now r2) | code@r1 (now r2) | 0 end-to-end (1 blocked at acceptance closure) | 8 | 8 | 1 | 0 | 0 | 0 (K12 BREAK adopted into §3) | gpt-6-astra (steward seat; not a steward filing) |
| 2026-09-14 | 20260914T221904Z-51d5a96b | agent-bridge | cc45e75f42af2f371bd18eb1f9bcbcef5718926e | r1 (now r2) | code@r1 (now r2) | 0 end-to-end (1 review run, not closed) | 3 | 9 | 0 | 0 | 3 | 0 | gpt-6-astra (steward seat; not a steward filing) |
| 2026-09-15 | 20260915T051905Z-86585ba5 | adobe-ingester | d7c91f3322a6c9cd856a380be32d831e1fd2416f | r2 (now r3) | code@r2 (now r3) | 0 end-to-end; 1 blocked at acceptance closure | 13 | 2 | 0 | 0 | 1 | 0 | gpt-6-astra (steward seat; not a steward filing) |
| 2026-09-15 | 20260915T051905Z-86585ba5 | agent-bridge | 80bb4d1dc9e14b9f3b08c61b443796c0d8a7db36 | r2 (now r3) | code@r2 (now r3) | 0 end-to-end; 4 observed-retrospective | 5 | 8 | 0 | 0 | 4 | 0 | gpt-6-astra (steward seat; not a steward filing) |
| 2026-09-15 | 20260915T051905Z-86585ba5 | airmypc | 2c919858144ac52318c05ffd02ba8ac5006fc0da | r1 (now r3) | code@r1 (now r3); hardware-in-loop@r1 (now r2) declared only | 0 end-to-end; S1 unaccepted; S2 accepted but undelivered | 6 | 10 | 0 | 0 | 3 | 0 | gpt-6-astra (steward seat; not a steward filing) |
| 2026-09-15 | 20260915T051905Z-86585ba5 | cloudvore | c124fcd29356c31618db1ae969435b6f0994fc30 | r1 (now r3) | code@r1 (now r3) | 3 filed; S1/S2 delivered without pre-work profile; S3 undelivered; 0 qualifying end-to-end | 10 | 7 | 0 | 0 | 1 | 0 | gpt-6-astra (steward seat; not a steward filing) |
| 2026-09-15 | 20260915T051905Z-86585ba5 | magic-lantern_dannephoto | 30aff3a984c0caa044b750de7ab9646048e71fb2 | r1 (now r3) | hardware-in-loop@r1 (now r2) | 0 end-to-end; 0 eligible; 5 blocked_external | 6 | 2 | 1 | 0 | 7 | 0 (P:hardware-in-loop acceptance-evidence BREAK adopted into hardware-in-loop r2) | gpt-6-astra (steward seat; not a steward filing) |
| 2026-09-15 | 20260915T060404Z-f14bd764 | mlv-app | db44322efba2a95ecccdbe7b5f5b27e2528429d2 | r2 (now r4) | code@r2 (now r4) | 0 end-to-end; S1 bus candidate unaccepted and undelivered; S2 failed seam | 3 | 0 | 0 | 0 | 13 | 0 | gpt-6-astra (steward seat; not a steward filing) |

---

## Steward status — 2026-09-15 (Conjugal, interim steward)

Derived, not asserted. Re-run: `python tools/kernel-e2e.py` (exits 1 while any member is due).

**§5 criterion 1 — CLOSED END-TO-END SUBJECTS: 0.** Summed across all 8 ledger rows. It has been 0
at every harvest. Criterion 1 needs ≥5 projects with ≥1 closed subject each, so finalisation is
0/5, and the ledger now states that number instead of leaving it implicit in a prose column that
nothing sums. `54 FIT, 46 FRICTION, 2 BREAK, 32 UNEXERCISED` over 8 rows.

**Correction to the count of record: the ledger holds 6 projects, not 7.** Seven filings exist on
the bus; six have rows. The missing one is the steward's own, which is the same defect as the
routing gap below rather than a separate one.

**Steward self-filing — routing, per K12.** `origin/review/conjugal-kernel-2026-09-14`
(blob 99cc68bf, 15 findings) has survived three harvests with no dispositions file and no ledger
row. Naming an arbiter is the steward's to do; adjudicating it is not. Criteria: a board with
(1) a bench it can actually reach, and (2) a seat in a different independence class from the
filing's producer, which was Claude.

- `adobe-ingester` — RULED AGAINST ITSELF and is not a candidate: unreachable bench, and a Claude
  seat, i.e. the producer's own class.
- `airmypc` — candidate of record on criterion (2): its posture line reports a Codex
  `gpt-5.6-sol` key lane, which is producer-independent. Criterion (1) is **UNVERIFIED and is the
  probable blocker**.
- `dng-auto-processor` — named as an alternate; has never filed, so its bench and seat are unproven.

**Reachability is the real obstacle, and it is the steward's defect, not the arbiter's.** All 15
findings cite paths in a checkout that exists on one machine. No sibling can re-measure them, so
"nobody has arbitrated it" understates the problem: as filed, nobody *can*. The steward's obligation
is therefore to re-file against a bench a sibling can reach, or to supply the evidence inline.
Recorded here rather than left as a standing request no board can satisfy.

**Members due — 3 have NEVER filed:** `adversarialllm`, `dng-auto-processor`, `salesforce-tools`.
`harvest-status.py` cannot see them: it enumerates filings that EXIST, so a member who has never
filed is indistinguishable from a member who does not exist. That is the same blind spot that let
the steward's own filing sit three runs. `tools/kernel-e2e.py` takes the roster from §6 and reports
the difference.

**Not blocking, so nobody spends a week on it:** RULINGS.md mentions the kernel zero times
(`grep -ci "fleet-factory-kernel\|factory kernel" RULINGS.md` → 0). Criterion 4 has never started.
The owner gate is idle, not jammed.
