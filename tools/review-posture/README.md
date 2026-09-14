# review-posture — the full Conjugal-standard review, as a tested tool

Runs every role of `specs/posture-templates-conjugal-standard.md` over the provider CLIs and reports the posture as a
measurement. Procedure around it: `bootstrap/lane-orchestrator.md` §2. Binding: RULINGS R2, R3, R5, R9.

| file | what it is |
|---|---|
| `roles.json` | the posture's roles, stages and lanes as data; the test fails if it drifts from the spec's roles table |
| `rubrics/approach-a-r15.json` | Conjugal Round 15 dimensions and seat lenses (verbatim); write another of the same shape for other subjects |
| `review_posture.py` | prompts per stage (binding-checked), panel scoring, classifier 2-of-3 tally, posture measurement |
| `run.sh` | stages A→D in one invocation; `--dry-run`, `--from B|C|D` |
| `../../tests/test_review_posture.py` | pins every failure below |

```bash
export RP_REPO=... RP_SUBJECT=... RP_BENCH=... RP_OUT=...     # all absolute; RP_OUT outside the bus
bash tools/review-posture/run.sh --dry-run && bash tools/review-posture/run.sh
```

Outputs in `RP_OUT`: `<lane>.prompt|txt|rc|log`, `panel.json`, `panel-summary.txt`, `classifier.json`, `rubric.json`,
`rubric_id`. Only the filing and `rubric.json` travel; raw lane output never does (Law 4).

## Failures this exists to prevent (all measured 2026-09-13/14)

- **A role missing from a hand-written runner is invisible.** The sentinel proves the lanes that ran; nothing noticed
  the 12 that were never written, and the run was filed as `conjugal-standard`. → `posture` counts against `roles.json`.
- **A prompt bound to nothing still gets an answer.** Bash interpolation sent `…doctrine$SUBJECT`. → prompts are built
  in Python and every one is checked to contain the subject path before it is written.
- **The arbiter never saw lint.** → stage B's arbiter prompt carries all four stage-A outputs and requires losers.
- **A seat's own average is not the composite.** In the measured run every stated composite matched to rounding, but
  one seat had to correct its own arithmetic mid-answer; a composite is data the tool can compute, so it does.
- **Permissive parsing guesses.** A loose regex read "78.73 (current) + 1.5 = 80.23" as a ceiling of 78.73 and ran a
  must-fix list past a newline into prose. → strict `HEADING: value` only; everything else is listed as `unparsed`.
- **`bash` can be WSL.** `shutil.which("bash")` on Windows returned WSL's, which cannot see `C:/` paths. → `run.sh`
  refuses a System32 bash; the test resolves Git Bash explicitly.

## Not covered (yet)

- **Model fallback ladders and token/cost telemetry** live in `tools/lane-dispatch.sh` (Claude lanes only). This tool
  dispatches each lane once at the inventory's id; a lane that fails is reported DID-NOT-RUN and the posture is PARTIAL.
- **Filing assembly** is the orchestrator's job (lane-orchestrator §3): quote verification, re-deriving numbers seats
  disagree on, and reading the arbiter's losers against the subject are judgement, not parsing.
