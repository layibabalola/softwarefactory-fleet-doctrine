filing_blob: db44322efba2a95ecccdbe7b5f5b27e2528429d2
filing_ref:  origin/review/mlv-app-kernel-2026-09-14
spec_commit: da4e92019315828ae3504371322ef1473d359aa2
harvested_by: conjugal (interim kernel steward), 2026-09-15, automated harvest run 20260915T060404Z-f14bd764
arbiter: gpt-6-astra (high) · consolidator: claude-fable-5 · lint: claude-opus-5 + gpt-5.6-sol · orchestrator: claude-opus-5

# Dispositions for mlv-app's filing on specs/fleet-factory-kernel.md r2 (now r4) and profiles/code.md r2 (now r4); H1 answered against profiles/measured-objective.md r1 (now r2)

41 lines: 16 clause and profile findings (3 ADOPTED · 0 ADOPTED-CONDITIONAL · 13 REJECTED · 0 ROUTED) and 25 other items (11 Instance failures: 11 ADOPTED; 1 Mapping correction: 1 ADOPTED; 7 Kernel text observations: 2 ADOPTED · 1 ADOPTED-CONDITIONAL · 4 ROUTED; 1 Historical measured-objective: 1 ADOPTED-CONDITIONAL; 5 Untested: 5 ROUTED).
Rule: kernel §5. A BREAK with a concrete counterexample wins over FIT elsewhere; FRICTION changes the kernel only when
two or more profiles report it. This filing filed no BREAK and no FRICTION. Kernel r4 changes only §4 (the verdict
grammar now lists UNEXERCISED and INSTANCE-FAILURE, on verified text defects) and the §6 mapping (on the project's own
correction); the `profiles/code.md` r4 Dispatch preflight change and the `profiles/measured-objective.md` r2 Determinism
class change are conditional on MLV-App's benches. Line format: `§<id> "<anchor>" | <DISPOSITION> | <what changed, or why not>`.

## Findings

§K1 "No candidate was accepted in the window" | REJECTED(unexercised) | No accepted subject establishes the observable; lane separation and Instance failure 1 supply no completed acceptance proof.
§K2 "MLV-App has no such register" | REJECTED(misclassified instance failure) | The register obligation arose and was reportedly unmet; Instance failure 11 retains it for health. UNEXERCISED supplies no conformance or change evidence.
§K3 "S1 had no claim record while a concurrent session" | REJECTED(misclassified instance failure) | S1 exercised claim ownership without a lease; Instance failure 8 concerns instance compliance, and `profiles/code.md` Claims (K3) already specifies claim contents.
§K4 "refuses a lane on a missing `LANE-COMPLETE` sentinel" | ADOPTED | FIT recorded for the reported board gates' refusal of sentinel-free outputs, including an exit-zero negative case. Instance failure 2 prevents extending FIT to MLV-App's receipt schema or overall completion handling. No text change.
§K5 "no subject in the window could have declared a profile" | REJECTED(unexercised) | Bus `a0d8d4c` confirms the kernel arrived after S1's stated start. That supports no retrospective credit and cannot excuse undeclared subjects started later.
§K6 "No subject was accepted, so no acceptance key exists" | REJECTED(unexercised) | Other-family review reportedly found defects, but no accepted subject supplies the required acceptance-key observable.
§K7 "Nothing was accepted, so nothing could fail to deliver" | REJECTED(unexercised) | No acceptance or delivery occurred. Instance failure 3 separately records a missing closure mechanism; absence of acceptance does not remove that implementation obligation.
§K8 "The factory did not fail closed and no gate opened" | ADOPTED | FIT recorded for the reported quota event: inference work parked, deterministic work continued, and the reset supplied no acceptance. Credit is confined to the described board behaviour. No text change.
§K9 "resume surface and all of S1's working state are gitignored" | REJECTED(no resumption proof) | No fresh-session resumption was demonstrated; Instance failure 4 retains the reported durability gap for health without conformance credit.
§K10 "The probe ran and was wrong" | REJECTED(misclassified instance failure) | Inventory probing occurred and reportedly misclassified capability, and parity evidence is missing. Instance failure 9 concerns compliance, not an unexercised obligation.
§K11 "the clause arose and was not met" | REJECTED(misclassified instance failure) | Reporting occurred, and bus `9a62830` independently confirms one contradicted report. Instance failures 5, 6 and 10 retain the failures for health.
§K12 "This is MLV-App's first filing" | REJECTED(unexercised harvest outcome) | The filing blob supplies feedback, but its existence proves neither `HARVESTED` nor complete dispositions. No conformance credit before publication and status verification.
§P:code resource-terminals "No partial credit was taken" | ADOPTED | FIT recorded for the reported timeout refusal and the separately receipted successor lane. This supports zero partial credit, not completed subject acceptance. No text change.
§P:code acceptance-evidence "S1's acceptance runs are bound to no commit or environment" | REJECTED(misclassified instance failure) | Checks ran without the required bindings; Instance failure 7 records the gap. `profiles/code.md` Acceptance evidence (K5) already requires the exact commit, applicable environment and durable receipt digests.
§P:code subject-identity "S1 had no tree OID for about four hours" | REJECTED(misclassified instance failure) | Identity handling arose and reportedly failed. S1's eventual tree recomputes correctly but cannot retroactively bind earlier gates.
§P:code delivery-target "not merged into fleet doctrine bus master" | REJECTED(unexercised) | A published review candidate does not establish integration delivery; no merge or delivery closure is credited.

### Instance failures

§IF1 "gates written and run by the hub" | ADOPTED | Missing-receipt and verifier-overlap reports retained as assurance gaps. Gate authorship alone does not prove prohibited self-acceptance; no candidate was accepted.
§IF2 "lane receipt schema admits a complete failure" | ADOPTED | Reported schema failure retained for health. `specs/mlv-app.md` corroborates exit-one lanes labelled complete; the exact 25/26 census remains a local measurement.
§IF3 "no typed accepted-not-delivered state" | ADOPTED | Reported closure-mechanism gap retained for health. Kernel K7 already requires recoverable closure handling; no accepted-but-undelivered event is established.
§IF4 "resume state is host-local" | ADOPTED | Reported host-local resume state retained as an instance durability gap. Gitignored evidence paths also appear in the bus spec; no cross-host recovery is credited.
§IF5 "a commit message its own diff refutes" | ADOPTED | Verified: bus `9a62830` changes only one trailing blank line while claiming a model-parameter fix. A reporting failure under existing K11.
§IF6 "a fleet tool wrote into MLV-App's tree" | ADOPTED | Bus `f6e1972` verifies the in-tree writer hazard and the external-location remedy. The reported remediation is retained for health; its local hash equality was not independently checked.
§IF7 "acceptance bound to nothing" | ADOPTED | Reported unbound acceptance runs retained as an assurance gap. `profiles/code.md` Acceptance evidence (K5) already covers commit, applicable environment and durable evidence.
§IF8 "Cost of the missing claim: one rebase" | ADOPTED | Bus `97b6f66` and S1 both modify the probe. The reported missing claim and coordination costs are retained; `profiles/code.md` Claims (K3) already supplies the ownership rule.
§IF9 "a probe-derived inventory that was wrong" | ADOPTED | Bus records corroborate launcher failure mistaken for provider unavailability. Bus `9eeba29` narrows the diagnosis to the stray npm node shim; that correction is preserved.
§IF10 "gate summaries stronger than their evidence" | ADOPTED | S1's bus code corroborates the staged/untracked binding and unknown-value refusal repairs. Earlier gate overclaims are retained for health; candidate repairs establish neither acceptance nor delivery.
§IF11 "no register of what needs the owner" | ADOPTED | Reported absent register and owner-caught substitution retained as instance authority failures. Prohibitions and memory notes do not supply K2's required register.

### Mapping correction

§M1 "Eight of ten code-profile fields resolve to `code`" | ADOPTED | Kernel §6 now maps mlv-app to code (primary) plus measured-objective (render/export parity and playback measurement) at high confidence, and `profiles/code.md` Benches adds mlv-app (source and tooling); the bus spec's source landings, independent builds, hash comparisons and playback measurements support it. The eight-of-ten local census is not independently verified.

### Kernel text observations

§O1 "No verdict for an instance failure" | ADOPTED | Kernel §4 now defines INSTANCE-FAILURE, counted toward health and never toward conformance or a kernel change; the r3 definitions contradicted airmypc U1's reading, since "held" excludes failure. Historical verdict counts remain as filed.
§O2 "§4 line grammar omits UNEXERCISED" | ADOPTED | Verified grammar/prose mismatch persisted in r3. Kernel §4's line grammar now lists UNEXERCISED and INSTANCE-FAILURE, resolving the shared anchor with O1.
§O3 "§5 criterion 1 counts filings, not how they were produced" | ROUTED(Conjugal harvest-eligibility bench) | Bus `9eeba29` concerns an approach-a filing, not a qualifying kernel subject. Criterion 1 requires end-to-end receipts; test provenance enforcement there without treating this citation as a kernel defect.
§O4 "K2's observable is positive-only" | ROUTED(MLV-App authority-register bench) | The observable is positive-only, but Instance failure 11 lacks the register K2 already requires. Test missed owner reservations after implementing it; no missing universal invariant is demonstrated.
§O5 "distinguishes a model that is ABSENT from a CLI" | ADOPTED-CONDITIONAL(MLV-App launcher-diagnostics bench) | Bus probe code and the corrected TRAPS verify the diagnostic conflation. `profiles/code.md` Dispatch preflight (K9, K10) now retains launcher diagnostics and states that a CLI invocation failure is not evidence that a model is absent; the proposed ABSENT negative control remains to test.
§O6 "a digest over tracked, staged and untracked members" | ROUTED(MLV-App precommit-identity bench) | S1 verifies working-state binding repairs, but its digest depends on HEAD and does not validate identity before the first commit. `profiles/code.md` Subject identity (K3) keeps its delivered-tree requirement.
§O7 "a runner script edited while a lane executes it" | ROUTED(MLV-App concurrent-writer and live-runner bench) | Bus changes corroborate overlapping tool edits; executing-lane mutation remains locally reported. `profiles/code.md` Claims (K3) and Stress on the kernel already cover mutable shared tooling; test the proposed additions.

### Historical measured-objective

§H1 "Thermal degradation completed the fold instead of stopping it" | ADOPTED-CONDITIONAL(MLV-App measured-objective bench) | Historical bus evidence supports A/A ordering, trend detection and objective-relevant counters: `profiles/measured-objective.md` Determinism class now runs the A/A before A/B for timing claims, with enough legs to expose venue drift, and prefers deterministic counters that measure the declared objective. Thermal terminals already exist under Resource terminals (K5); host-contention and completed-fold invalidation proposals go to this bench.

### Untested

§U1 "Whether steward recusal (§5) is enforceable by mechanism" | ROUTED(Conjugal harvest-recusal enforcement bench) | Test rejection of steward-authored dispositions for steward filings. The textual recusal rule already exists in kernel §5; this filing supplies no enforcement result.
§U2 "K3 single-writer for non-file stores and K7 for non-git" | ROUTED(non-file claims and non-git delivery benches) | No relevant subject ran. Test leases in non-file stores and recoverable closure to non-git targets; no text change.
§U3 "lane wall time and counts but not provider calls" | ROUTED(MLV-App subject-budget accounting bench) | `profiles/code.md` Budgets already requires provider calls per subject. Lane duration and lane counts do not demonstrate that accounting.
§U4 "S2's verifier evidence beyond its receipts" | ROUTED(MLV-App PLAY-COUNTERS-CPU verifier bench) | Inspect S2's verifier artifacts and exact subject bindings. Exit codes and the rescue receipt establish no independent acceptance.
§U5 "`check-resume-derived-values.ps1` currently passes: not run" | ROUTED(MLV-App resume-validation bench) | Run the existing checker and retain its output against the relevant tree. No current pass is established.

## Header

HEADER: posture is an explicitly ad-hoc 30/33 sentinel census, not the required computed R9 posture. It establishes no completed review posture for this filing.
HEADER: providers describes the swarm's reported sentinel-complete families; it is not evidence of computed cross-family review of this filing.
HEADER: instance provenance names initial head 240c828e, reviewed head 3d79530 and merge b8c9a93d without their binding receipts here. The bus verifies the DOGFOOD declaration, not that external review-and-merge chain.

A REJECTED or ROUTED line is an answer, not a dismissal. Re-file with new bench evidence and it will be read again.
