# DNG receipt — token economy measured by turn count, 2026-08-30

Supporting evidence for `ruling-candidates/turn-count-is-the-token-lever-r1.md`. Measurements only;
this receipt proposes nothing and grants no authority.

## Source

Result events emitted by the unattended hourly driver (`\dng-driver-wake` → `driver-wake.stream.log`),
twelve consecutive wakes that reached a result event. Two additional launches returned a synthetic
zero-cost result after a provider refusal and are excluded, with the exclusion stated rather than
silent.

## Measured

| turns | cost USD | cache-read tokens | output tokens | cache-read per turn |
|---:|---:|---:|---:|---:|
| 48 | 4.27 | 3,427,905 | 56,206 | 71,414 |
| 52 | 5.96 | 4,897,722 | 73,314 | 94,186 |
| 46 | 6.68 | 5,363,442 | 94,645 | 116,596 |
| 85 | 9.65 | 9,882,411 | 104,669 | 116,263 |
| 81 | 10.36 | 10,299,463 | 110,546 | 127,153 |
| 75 | 10.84 | 10,242,677 | 137,618 | 136,569 |
| 86 | 11.56 | 12,347,031 | 127,632 | 143,570 |
| 93 | 13.89 | 14,841,636 | 156,980 | 159,587 |
| 89 | 15.95 | 16,353,044 | 190,652 | 183,742 |
| 107 | 17.32 | 19,428,334 | 181,384 | 181,573 |
| 129 | 19.65 | 23,277,575 | 203,474 | 180,446 |
| 135 | 19.60 | 24,813,000 | 166,917 | 183,800 |

Totals: **1,026 turns · $145.73 · 155,174,240 cache-read · 1,604,037 output.**
Mean **$10.41 per wake**, **$0.142 per turn**. **Cache-read : output = 97 : 1.**

## The two findings

1. **Superlinear in turns.** 48 turns cost $4.27; 135 turns cost $19.60 — 2.8× the turns for 4.6× the
   cost.
2. **Per-turn context grows within a run**, 71k → 184k cache-read per turn as turn count rises. This
   is the mechanism behind finding 1: early reads are re-charged by every later turn.

## Confounding, stated

Turn count and task scope are confounded across these wakes — a longer wake did more work as well as
more turns. This is observational, not a controlled experiment. It supports the *direction* of the
mechanism and does not isolate the effect size. A controlled before/after on byte-comparable output is
owed before any coefficient is claimed.

## Environment

Windows 10 Pro 19045; unattended hourly scheduled task; `effort=max`, `--max-turns 200`,
`--autocompact 800k`; single-flight, no overlap. Provider figures are the run's own reported usage,
not an estimate.
