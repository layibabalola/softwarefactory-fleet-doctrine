# Merit adjudication — law-3 seam duty: is `doctrine-sync.mjs export-check` the fleet's one seam checker, or does DNG's `doctrine-sync.ps1 -SeamCheck` do something it does not?

Run 2026-08-30T20:52:03.233Z. Rubric `law3-seam-check-duplicate`, proposed by `adversarialllm`.
Re-run this yourself: `node tools/merit-adjudicate.mjs --criteria <this rubric>`. A ruling with
no re-runnable evidence is an opinion with a timestamp.

Anti-gerrymandering guard: PASSED — the proposer declared its own candidate failing C6, C7, C8.

| Criterion | Weight | Incident | doctrine-sync.mjs | dng doctrine-sync.ps1 -SeamCheck |
|---|---|---|---|---|
| **C1** Detects a clone that is behind while `git status` is clean. | MUST | 2026-08-30: this box's bus clone was 229 commits behind with a clean working tree; nothing reported it. | PASS | UNMEASURED |
| **C2** A debt state exits NON-ZERO, so a caller cannot mistake it for success. | MUST | 2026-08-10..08-18: a correctly-written guard refused to act and logged quietly; the bus was blocked for 279 consecutive runs. Safe-and-silent is still silent. | PASS | UNMEASURED |
| **C3** A clean state exits ZERO, so the check is usable in a gate without false alarms. Probed against a DISPOSABLE consumer the probe creates itself. | MUST | A checker that cannot pass gets disabled within a week, which is how the duty stopped being anyone's in 11 of 12 projects. Second incident, found by THIS rubric on its first run: the original probe read ambient state and scored a MUST FAIL that was really a stale precondition. A probe that does not establish its own precondition is measuring the weather. | PASS | UNMEASURED |
| **C4** Runs on a runtime present on every fleet box. | MUST | 2026-08-09 (MLV-App): `py -3` was measured ABSENT and every hook depending on it had been failing open, silently, for an unknown period. | PASS | UNMEASURED |
| **C5** Stores the consumer's reading position in the CONSUMER, never on the shared bus (law 2). | MUST | Single-writer exists so merge conflicts are impossible by construction; a consumer that writes its cursor to the commons breaks that for every member at once. | PASS | UNMEASURED |
| **C6** Every run leaves a durable receipt with an explicit verdict token, so a run that NEVER HAPPENED is detectable afterwards. | SHOULD | 2026-08-30: a watcher hosting the sync duty stopped running entirely and nothing noticed for 12 days. Absence of output is indistinguishable from absence of problems. | FAIL | UNMEASURED |
| **C7** Cursor stagnation raises an alarm with no human looking. | SHOULD | Same 12-day silent watcher outage. A cursor that stops advancing is the earliest visible symptom and nothing watched it. | FAIL | UNMEASURED |
| **C8** Publication detection is EXACT, not a substring match on commit subjects. | SHOULD | Proposer-declared defect: `export-check` decides a project published by testing whether any bus commit subject contains the project name, so an unrelated commit mentioning the project clears the debt. A check that can be satisfied by accident is a check that reports good news. | FAIL | UNMEASURED |

| Candidate | MUST pass | MUST fail | SHOULD pass | SHOULD fail | UNMEASURED |
|---|---:|---:|---:|---:|---:|
| `doctrine-sync.mjs` | 5 | 0 | 0 | 3 | 0 |
| `dng doctrine-sync.ps1 -SeamCheck` | 0 | 0 | 0 | 0 | 8 |

**Zero MUST failures and nothing unmeasured: `doctrine-sync.mjs`.** That is the measurement, not the ruling —
a seat that owns none of the candidates still has to rule, and merit is per-property: record what
survives from the losing candidate rather than discarding the artifact whole.

Verdict legend: UNMEASURED means no probe was declared. It never counts as PASS —
a criterion nobody measured is a criterion nobody met.
