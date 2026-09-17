# Profile: measured-objective - Pipelines judged by a measured score against ground truth (grading, rendering and export, tuning)

**Profile of** `specs/fleet-factory-kernel.md` r5. **Profile revision:** r3. **Status:** `BENCHED`. **Benches:** dng-auto-processor (automatic colour grade against the manual grade), mlv-app (render and export, A/A trend discipline).
A profile defines what acceptance means in its domain. It never weakens a kernel clause (kernel §5). File evidence against it as `P:measured-objective <field>` lines in `adjudications/factory-kernel/<project>.md`.

| Field | Rule |
|---|---|
| Subject identity (K3) | git tree of the pipeline plus digests of the evaluation set, scorer, runtime inputs outside git and delivered artifacts outside git; external components follow in manifest path order |
| Artifact store | git for code; datasets and held-out folds by manifest of blob digests, outside git when large |
| Determinism class | declared per bench: statistical claims need an A/A baseline and a trend or confidence interval; byte-deterministic claims require an identical repeat at tolerance zero. For timing claims, run the A/A before A/B with enough legs to expose venue drift; prefer deterministic counters when they measure the declared objective |
| Acceptance evidence (K5) | the declared scorer on a held-out fold the producer never tuned on, meeting a predeclared subject-specific improvement or non-regression criterion against the pinned baseline. Bind each score to the full subject identity verified for that run; an unverified binding is UNEVALUABLE |
| Independent key (K6) | the held-out ground truth, plus a scorer the producer did not write for this subject |
| Resource terminals (K5) | long renders or exports, disk, thermal, model-credit depletion: typed terminals; a partial fold is not a score. If account rotation cannot restore credit, parked work names its resume condition and the register-authorized actor who can restore or re-tier the seat |
| Delivery target (K7) | released pipeline version with its score receipt |
| Human gates (K2) | changes to the scorer, the held-out fold or the baseline (moving the goalposts is owner-gated) |
| Budgets | compute hours per evaluation; storage for folds |
| Stress on the kernel | overfitting to the fold; a scorer changed in the same subject as the pipeline; nondeterministic renders that break byte-replay checks |

Bench wording: "objective = AUTO XMP matches the manual grade per frame, measured by tools/scoreboard.ps1 on a held-out leave-one-project-out fold" (dng-auto-processor).
