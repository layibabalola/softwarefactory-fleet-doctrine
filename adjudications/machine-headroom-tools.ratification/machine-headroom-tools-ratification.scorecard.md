# Merit adjudication — Owner request 2026-11-16 (per-machine usage to a central location; headroom without hurting existing throughput): which of three rival tools (A machine-load, B host-headroom-20261116, C tools/host-headroom) is the fleet's one tool, and what survives from the others?

Run 2026-11-17T03:18:12.914Z. Rubric `machine-headroom-tools-ratification`, proposed by `neutral-merit-adjudicator (re-run by the non-author ratifier, PC-MINI2, 2026-11-17)`.
Re-run this yourself: `node tools/merit-adjudicate.mjs --criteria <this rubric>`. A ruling with
no re-runnable evidence is an opinion with a timestamp.

Anti-gerrymandering guard: not applicable — proposer owns no candidate here; guard not applicable.

| Criterion | Weight | Incident | A | B | C |
|---|---|---|---|---|---|
| **M1-quiet** Excludes owner quiet windows read in the REAL FleetQuiet record format (windows\<id>.json, armedUtc/untilUtc; .released history). | MUST | coretemp-fleet RESULTS.md 2026-11-15: thermal trials run all-core saturation at the 74 W cap inside FleetQuiet windows, and the unquiet 050413Z-stacked run was contaminated by background work; counting a trial as project load reads a mini as FULL and teaches a false slowdown curve. | PASS | FAIL | PASS |
| **M2-throughput** Answers the throughput question: at the SAME utilisation, a measured slowdown of running work turns ROOM into TIGHT/FULL. | MUST | Owner request 2026-11-16 ("without negatively impacting throughput"); RESULTS.md: all minis hold the ~74 W cap, so power not cores sets speed, and one trial did 21 % less work at the same 74 W; utilisation alone cannot see it. | PASS | PASS | PASS |
| **M3-heavyslot** An idle-CPU machine whose HeavySlot gate is held 70 % of the time with 20-min waits is not reported as plain ROOM (verdict or a surfaced gate verdict says so). | MUST | Measured 2026-11-16 on PC-MINI3: CPU p95 ~28 % while HeavySlot jobs waited up to 43 min (slot held 70 % of the day); a new heavy project queues behind every incumbent whatever the CPU says. | FAIL | PASS | PASS |
| **M4-nolock** Reading the HeavySlot ledger never makes HeavySlot's own append (AppendData, FileShare ReadWrite|Delete) fail. Negative control: a FileShare.Read holder must block it. | MUST | heavy-slot.ps1 Add-LedgerLine swallows a failed append as a WARN, so a reader holding FileShare.Read silently drops admit/exit lines (and so corrupts every duty/wait figure); TRAPS 2026-08-08: a locked file blocked the next build. | PASS | FAIL | PASS |
| **M5-failclosed** Missing or insufficient data never reads as room: no data and ~2 h of data both give UNKNOWN/INSUFFICIENT/UNEVALUABLE. | MUST | heartbeats/README.md: a board that never installed the duty and one whose task stopped both look like a quiet board; RULINGS 2026-08-30 test 4: silence has been read as health too many times on this bus. | PASS | PASS | PASS |
| **M6-law4** A record built from this machine's REAL local data carries no path, user name, image or script name (public bus). | MUST | Bus README law 4 and CI-COST-CONTROL.md: the bus is public by owner decision; heartbeats/README warns literal paths are machine facts with an expiry date. | PASS | PASS | PASS |
| **M7-ownclone** The installed publisher pushes from a repository it owns, never from (or via worktrees/refs of) the clone a person works in. | MUST | Owner rule for this duty ("never pushes from a checkout a person uses"); TRAPS lane-collision entries: three writers on one tree/index produced foreign work-block adoption and pushes blocked by a peer's byte-identical write. | FAIL | FAIL | PASS |
| **M8-prereview** While the tool is unmerged, no installed publisher on any mini is armed to push to master. | MUST | Owner rule: nothing to master before review; RULINGS ratify-before-publish; CI-COST-CONTROL: repeated intermediate publication was the dominant avoidable cost (Aug 2026, $50 cap hit). | PASS | PASS | PASS |
| **M9-launch** Scheduled launch is windowless AND keeps the script's exit code (wscript /wait shim or the GUI launcher; not bare pwsh, not conhost --headless). | MUST | TRAPS 2026-09-02: bare pwsh under an Interactive principal flashed a console every fire for two days; TRAPS 2026-10-20: conhost --headless returns 0 for exit 7 and orphans the child on stop. | PASS | FAIL | PASS |
| **M10-runtime** Installed and producing data now on all three minis: task present and enabled, principal resolves to a SID (not WORKGROUP\\user), newest data < 10 min old, one data location. | MUST | USERDOMAIN reads WORKGROUP under ssh (all three authors hit it 2026-11-16); RULINGS test 7: a MUST tie breaks on runtime availability; a registration is not a firing (F-HOOK-01). | PASS | FAIL | PASS |
| **M11-tests** The candidate's own test suite passes from a temp export of its branch. | MUST | RULINGS 2026-08-30: a ruling with no re-runnable evidence is an opinion with a timestamp. | PASS | PASS | PASS |
| **M12-synthcap** Any synthetic load the sampler generates stays at or below half the physical cores (8 of 16). | MUST | Owner rule 2026-10-07: synthetic load capped at half the cores; saturation/load runs deferred while projects are active (coretemp README). | PASS | PASS | PASS |
| **S1-power** Reads package power from the REAL Core Temp adapter feed (dd.MM.yyyy local rows) so time at the power cap is visible. | SHOULD | RESULTS.md 2026-11-15: power, not temperature, sets the minis' speed (74 W limit); Core Temp throttle columns never fire. | PASS | FAIL | PASS |
| **S2-cli-attrib** A CLI-like process with no path in its command line, cwd in a project, is attributed to that project (case 2, a child naming the project, is recorded as evidence). | SHOULD | Claude/Codex CLIs carry no project path in their command lines; measured 2026-11-16 that attribution otherwise collapses into unattributed/agent-cli buckets. | PASS | FAIL | PASS |
| **S3-first-verdict** After 12 h of perfect data, the verdict the CENTRAL record would carry is already a real verdict. | SHOULD | All three tools were installed 2026-11-16 and at 01:23Z on 11-17 every one still reported INSUFFICIENT/UNKNOWN on every mini (live census); the owner has no answer until this clears. | FAIL | PASS | PASS |
| **S4-ci-cost** A record push to master does not start the sealed disposition-intake matrix (its push paths-ignore covers the record path). | SHOULD | CI-COST-CONTROL.md: Aug 2026 Actions hit the $50 cap; repeated intermediate publication, not storage, was the dominant avoidable cost. | FAIL | PASS | PASS |
| **S5-cost** Measured sampler CPU under 2 CPU-seconds per minute (~0.1 % of a 32-thread mini) over 5 min on pc-mini2. B: UNMEASURED, not installed on any mini at probe time. | SHOULD | The owner question is about not slowing existing work; a monitor is itself load on the machine it measures (coretemp telemetry was budgeted the same way). | PASS | UNMEASURED | PASS |

| Candidate | MUST pass | MUST fail | SHOULD pass | SHOULD fail | UNMEASURED |
|---|---:|---:|---:|---:|---:|
| `A` | 10 | 2 | 3 | 2 | 0 |
| `B` | 7 | 5 | 2 | 2 | 1 |
| `C` | 12 | 0 | 5 | 0 | 0 |

**Zero MUST failures and nothing unmeasured: `C`.** That is the measurement, not the ruling —
a seat that owns none of the candidates still has to rule, and merit is per-property: record what
survives from the losing candidate rather than discarding the artifact whole.

Verdict legend: UNMEASURED means no probe was declared. It never counts as PASS —
a criterion nobody measured is a criterion nobody met.
