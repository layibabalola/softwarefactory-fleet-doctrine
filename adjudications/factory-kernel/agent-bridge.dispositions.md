filing_blob: cc45e75f42af2f371bd18eb1f9bcbcef5718926e
filing_ref:  origin/review/agent-bridge-kernel-2026-09-14
spec_commit: ec32d6eeed18b51be09f9b1c087b482087b9e902
harvested_by: conjugal (interim kernel steward), 2026-09-14, automated harvest run 20260914T221904Z-51d5a96b
arbiter: gpt-6-astra (high) · consolidator: claude-fable-5 · lint: claude-opus-5 + gpt-5.6-sol · orchestrator: claude-opus-5

# Dispositions for agent-bridge's filing on specs/fleet-factory-kernel.md r1 (now r2) and profiles/code.md r1 (now r2)

17 lines: 15 clause and profile findings (6 ADOPTED · 5 ADOPTED-CONDITIONAL · 3 REJECTED · 1 ROUTED) and 2 Untested items (2 ROUTED).
Rule: kernel §5. A BREAK with a concrete counterexample wins over FIT elsewhere. FRICTION changes the kernel only when
two or more profiles report it; both filings this harvest are `code`, so their FRICTION lands in `profiles/code.md` r2.
The kernel is now r2. Line format: `§<id> "<anchor>" | <DISPOSITION> | <what changed, or why not>`.

## Findings

§K1 "never accepted" | REJECTED(unexercised: no evidence) | No change.
§K2 "one register" | ADOPTED | Code requires the register to be reachable from every session checkout, merged with adobe-ingester's classification requirement (`profiles/code.md` Human gates (K2)).
§K3 "under a lease that expires" | ADOPTED-CONDITIONAL(agent-bridge) | Code leases identify owned processes and are consulted before same-host cleanup (`profiles/code.md` Claims (K3)); no kernel amendment.
§K4 "positive evidence" | ADOPTED | FIT recorded; no text change.
§K5 "declares its profile and profile version" | ADOPTED-CONDITIONAL(agent-bridge) | A code/design-review subcase with a predeclared rubric and acceptance contract is added (`profiles/code.md` Acceptance evidence (K5)); the historical run stays unaccepted.
§K6 "computed, not asserted" | ADOPTED | FIT recorded; no text change; scoped to measured cross-family verification.
§K7 "Acceptance and delivery are separate states" | REJECTED(unexercised: no evidence) | No change.
§K8 "Running out of quota" | REJECTED(unexercised: no evidence) | No change.
§K9 "before expensive spend" | ADOPTED | Code's spending tool runs the resume gate before dispatch (`profiles/code.md` Dispatch preflight (K9, K10)).
§K10 "before any provider work" | ADOPTED-CONDITIONAL(agent-bridge) | The actual preflight inventory snapshot, digest and parity evidence are retained (`profiles/code.md` Dispatch preflight (K9, K10)); later inventory replacement cannot substitute.
§K11 "every report" | ADOPTED | FIT recorded; no text change; scoped to the reported review run.
§K12 "answers each one" | ROUTED(Conjugal shared review-posture tool bench) | Assign and test the prompt defect. Other projects mentioned here do not supply additional harvest evidence or profiles.
§P:code subject-identity "git tree OID" | ADOPTED-CONDITIONAL(agent-bridge) | Review component order is defined in code (`profiles/code.md` Subject identity (K3)); K3's outer hash applies once.
§P:code acceptance-evidence "pinned acceptance runs" | ADOPTED | The acceptance environment is bound (`profiles/code.md` Acceptance evidence (K5)); kernel §6's agent-bridge row is corrected to "code (fleet tooling and product)", confidence high, citing `AGENTS.md:56`.
§P:code budgets "provider calls per subject" | ADOPTED-CONDITIONAL(agent-bridge) | Review rounds report dispositions and subject changes, including zero (`profiles/code.md` Budgets); zero changes alone does not establish PRESSURED.

### Untested

§U1 "arbiter prompt fix itself" | ROUTED(Conjugal review-posture tool bench, then agent-bridge rerun) | DATA-framing defect verified on bus; sentinel placement and output-contract remedy still require the stated rerun.
§U2 "mapping for agent-bridge" | ROUTED(second code design-review bench) | Product-bar correction is verified (kernel §6); test the provisional code subcase before creating a separate orchestration profile.

## Header

HEADER: profile contains commentary; retain only "code@r1" and move explanation into the body.
HEADER: instance is explicitly unlanded; it does not establish a durable canonical implementation.
HEADER: providers/posture describe the earlier review subject. Distinguish those measurements from the single-family advisory work contributing to this filing.
HEADER: subjects supplies zero completed end-to-end subjects.

A REJECTED or ROUTED line is an answer, not a dismissal. Re-file with new bench evidence and it will be read again.
