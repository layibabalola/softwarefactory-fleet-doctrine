# Ratification: machine-headroom tools (A #99, B withdrawn, C #100)

**Ruling: RATIFIED. Winner: C (`tools/host-headroom`, PR #100, head `c57f9c92`).**
Non-author ratifier seat, 2026-11-17T03:18Z, under RULINGS.md "RULE ON MEASURED MERIT, ALWAYS"
(2026-08-30). Seat: a side session on PC-MINI2 started only for this ruling. It wrote none of A, B
or C. Disclosure: A's author session also runs on PC-MINI2; this is a different session.

## What was re-measured

The 01:50Z measurement exported the candidates at about 01:19Z. Both heads moved after that:

- A: `280c7fd7`, nine commits later.
- C: `c57f9c92`, three commits later. `b18b38f8` ports survivors from A and B, with credit.
- B: `8d6e4544`, unchanged and withdrawn.

I re-ran `tools/merit-adjudicate.mjs` on the current heads. The rubric was the committed one, with
its incidents and expectations unchanged.

| | MUST pass | MUST fail | SHOULD pass | SHOULD fail | UNMEASURED |
|---|---:|---:|---:|---:|---:|
| A @ 280c7fd7 | 10 | **2** (M3 HeavySlot, M7 own clone) | 3 | 2 (S3, S4) | 0 |
| B @ 8d6e4544 | 7 | 5 | 2 | 2 | 1 |
| C @ c57f9c92 | **12** | **0** | 5 | 0 | 0 |

**No 01:50Z verdict is overturned for the head it measured.** At the old heads:

- A's M1 FAIL was right: A then read `startUtc/endUtc`, which FleetQuiet never writes.
- A's M8 FAIL was right: A's publisher was armed then.
- C's S2, S3 and S4 FAILs were right: C then lacked those features.

## Verdicts that changed at the current heads, with evidence

| Criterion | 01:50Z | Now | Evidence (receipt row) |
|---|---|---|---|
| M1-quiet A | FAIL | PASS | Fixed in `3ab60358`. `REAL_FORMAT_EXCLUDED=True`. The negative controls still exclude nothing. |
| M8-prereview A | FAIL | PASS | A's author disabled the publisher at 02:44Z. Now `ARMED_HOSTS=0` on all three minis. This is a state probe; see finding 1. |
| S2-cli-attrib C | FAIL | PASS | `CASE1_CWD_ONLY=agent-bridge;V1=own CASE2=agent-bridge;V2=descendant`. Ported from A in `b18b38f8`. |
| S3-first-verdict C | FAIL | PASS | `VERDICT_AFTER_12H=ROOM`. Span coverage ported from B. |
| S4-ci-cost C | FAIL | PASS | Record path is now `heartbeats/host-headroom/<M>.json`, inside `paths-ignore`. |

The failures that stand:

- **M3-heavyslot A FAIL.** Test case: idle CPU, flat clock, every band measured, and a HeavySlot
  ledger held 70 % of the time with 20-minute waits. A returns `VERDICT=ROOM GATE_FLAG=none`. The
  control with an empty ledger also returns `ROOM`. A reports heavy-job durations as data but never
  turns contention into a verdict. That is the PC-MINI3 incident.
- **M7-ownclone A FAIL.** The cause is in A's code, not in how it was installed:
  - `Install-MachineLoad.ps1:32` defaults `-BusRoot` to the person's clone
    `C:\!Layi Wkspc\softwarefactory-fleet-doctrine`.
  - `machine_load.py` `publish()` runs `git worktree add` and `git worktree prune` inside that repo,
    and fetches into its refs.
  - The incident is real: TRAPS.md:173 (three writers, one tree and index) and TRAPS.md:392
    (foreign work-block adoption).
- **S3 A FAIL.** A needs a full UTC day, so 12 h of data gives `UNKNOWN`.
- **S4 A FAIL.** `machine-load/**` is not in `disposition-intake.yml` `paths-ignore`, so every
  daily publish would start the CI matrix.

## Probe defects found and corrected (test 5: a probe must establish its own precondition)

**The probes behind the 01:50Z receipt were never committed.** The rubric points at
`<merit-dir>\probes.ps1`, which existed only in a scratchpad on PC-MINI1. The 01:50Z result
therefore could not be re-run from the repo. This folder commits them as `probes-r3.ps1` and
`probe_a_r3.py`. Every change is marked `RATIFIER` in the code.

Run unchanged against the current heads, those probes gave **five wrong verdicts**. Each was a
probe defect, not a property of a candidate:

1. **M1 A: false FAIL.** The probe extracted only `Test-QuietWindow`. Since `3ab60358` that
   function calls `ConvertTo-UtcTime`, so the call threw and was swallowed. The fix extracts both
   functions, as A's own test does (`Install-MachineLoad.tests.ps1:112`).
2. **M5 A: false FAIL (KeyError).** A's `--expect` names the fleet. It defaults to the three minis
   (`machine_load.py:941`) and leaves out unexpected machines by design. The probe expected only
   `ABSENTBOX`. With PARTIAL expected, A returns `UNKNOWN` with state `LOW-COVERAGE`, so it fails
   closed.
3. **M2 A: false FAIL.** The probe world jumped from 2 to 10 busy threads. Since `d5f8c347`, A
   refuses to claim an onset above a band it never measured, so it returned `FULL/FULL`. In a world
   that visits 2, 6 and 10 threads it returns `ROOM → FULL`, measured at 8 threads.
4. **M2 C: false FAIL.** The probe world held 2 h of data. Since `b18b38f8`, C requires at least
   6 h of sampled span, so it returned `UNEVALUABLE`. With 8 h of data it returns `ROOM → TIGHT`
   (canary slowdown 1.36).
5. **M3 A: false PASS.** A returned `FULL` because of the unmeasured-band refusal, not because of
   HeavySlot. In a band-complete idle world A says `ROOM` (see the failures above). The C gate world
   was also widened to 8 h, with a ledger 70 % held across it. Result:
   `heavy_slot_verdict=FULL, occupancy 0.7`.

S2 ran on PC-MINI1, where the probe's `agent-bridge` folder exists, as in the 01:50Z run. On
PC-MINI2 the probe could not start its world.

## Rubric fairness

- **Every criterion names an incident.** Its probes put both candidates in the same world, or in
  equivalent worlds that suit each tool's own data model.
- **Test 2 is satisfied.** The 01:50Z rubric scored C failing three SHOULDs.
- **C closed those gaps by porting properties from A and B, with credit.** That is test 6 working
  as intended, not gerrymandering.
- **Independence caveat.** The 01:50Z "neutral" subagent was started by C's author session. That
  is why this re-measurement was needed, and why its probes are now committed.

## Findings carried to the winner (not merge-blocking under this rubric)

1. **M8 measures state, not the installer.** Both installers arm a master publisher while
   unmerged:
   - C: `Install-HostHeadroom.ps1:103` registers the publisher enabled, first run 20 minutes after
     install, then every 6 h.
   - A: daily.

   C passes only because its author disabled the task by hand. Any reinstall of C re-arms it, which
   is exactly what A's reinstalls did between 01:44Z and 02:39Z. **Before #100 merges, C's
   installer should register the publisher Disabled while the tool is not on `master`.**
2. **C's headline verdict ignores HeavySlot.** In the HeavySlot world C's top-level verdict is
   `ROOM`, with `heavy_slot_verdict=FULL` in a separate field. M3 passes as written, but the owner's
   question should get one answer.
3. **C's sampler costs more.** C measured 1.42 CPU-s/min against A's 0.27. Both are inside the
   2.0 budget.

## Survivors from A (test 6)

These go to C as data, credited when ported:

- the measured clock-versus-load curve (the M2 result above);
- data-quality states (INVALID-ROW, DUPLICATED, MISFILED, STALE);
- fleet `--expect` semantics;
- the HeavySlot duration trend;
- the ACL-locked bin and the lock-first installer;
- A's low sampler cost.

A's author has committed to withdrawing A's sampler and tasks on all three minis within 24 h, with
backups and proof, and to closing #99.

## Reproduce

```
git -C <bus> fetch origin "+refs/pull/99/head:refs/remotes/pr/99" "+refs/pull/100/head:refs/remotes/pr/100"
# export each head's tools/machine into <merit-dir>\srcA, srcB, srcC:
git -C <bus> archive refs/remotes/pr/99  -- tools/machine | tar -x -C <merit-dir>\srcA   # 280c7fd7
git -C <bus> archive origin/machine/host-headroom-20261116 -- tools/machine | tar -x -C <merit-dir>\srcB   # 8d6e4544
git -C <bus> archive refs/remotes/pr/100 -- tools/machine | tar -x -C <merit-dir>\srcC   # c57f9c92
# copy probes-r3.ps1 and probe_a_r3.py into <merit-dir>
# substitute <merit-dir> (and <merit-dir-on-pc-mini1> for S2) in the rubric, then:
node tools/merit-adjudicate.mjs --criteria <merit-dir>\machine-headroom-tools-ratification.json --out <merit-dir>\out
```

Run it on a mini that can reach the other two over ssh. M10, M8 and M9 are read live on all three
minis. S5 runs on PC-MINI2, relayed through PC-MINI1 because that session is elevated.
