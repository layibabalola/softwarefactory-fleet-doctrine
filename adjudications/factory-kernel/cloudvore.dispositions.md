filing_blob: c124fcd29356c31618db1ae969435b6f0994fc30
filing_ref:  origin/review/cloudvore-kernel-2026-09-14
spec_commit: c7e37a54999f9705623b9ffdff397592b8394723
harvested_by: conjugal (interim kernel steward), 2026-09-15, automated harvest run 20260915T051905Z-86585ba5
arbiter: gpt-6-astra (high) · consolidator: claude-fable-5 · lint: claude-opus-5 + gpt-5.6-sol · orchestrator: claude-opus-5

# Dispositions for cloudvore's filing on specs/fleet-factory-kernel.md r1 (now r3) and profiles/code.md r1 (now r3)

23 lines: 18 clause and profile findings (13 ADOPTED · 1 ADOPTED-CONDITIONAL · 4 REJECTED · 0 ROUTED) and 5 Untested items (1 ADOPTED · 4 ROUTED).
Rule: kernel §5. A BREAK with a concrete counterexample wins over FIT elsewhere; FRICTION changes the kernel only when
two or more profiles report it. This filing's K10 FRICTION matched magic-lantern_dannephoto's under `hardware-in-loop`,
so kernel K10's observable changed (r3); its §U3 evidence tightened kernel K12's observable; its adopted K5, K9 and P:code acceptance-evidence FRICTION landed in `profiles/code.md` r3 (Acceptance evidence, Dispatch preflight); its K6, K11 and P:code independent-key FRICTION were rejected. Line format: `§<id> "<anchor>" | <DISPOSITION> | <what changed, or why not>`.

## Findings

§K1 "never accepted on evidence whose only author is its producer" | ADOPTED | Post-landing corrections support the prohibition on producer-only acceptance; they do not demonstrate that Cloudvore complied with it.
§K2 "one register of what needs the owner" | ADOPTED | FIT recorded; the register permitted the measured pushes without owner interruption. No text change.
§K3 "a content digest over its declared artifact set" | ADOPTED | FIT recorded; the stated commands identify candidate trees, but bare tree OIDs alone do not prove K3's required outer digest or leases.
§K4 "Never exit code, output size or silence" | ADOPTED | FIT recorded; refused vacuous mutation success, unevaluable tests and a mismatched counting method support positive-evidence discipline. No text change.
§K5 "declares its profile and profile version" | ADOPTED | `profiles/code.md` Acceptance evidence (K5) defines meaningful acceptance by the declared artifact kind, with documentation and doctrine subjects declaring rubric and roles before work. It grants no retrospective profile declaration.
§K6 "Every acceptance includes a key" | REJECTED(already universal) | "Every acceptance" already includes documentation and doctrine. Producer-only and post-landing review are instance failures, not exceptions requiring kernel expansion.
§K7 "Accepted is not delivered" | ADOPTED | FIT recorded; delivery and aborted landing are distinct observations, and delivered S1 does not prove prior conforming acceptance. No text change.
§K8 "rotating or parking the work that needs inference" | REJECTED(unexercised) | No measured quota event; no text change.
§K9 "resumes from the project's tree and the bus alone" | ADOPTED-CONDITIONAL(cloudvore resumability-attribution bench) | `profiles/code.md` Dispatch preflight (K9, K10) requires resume failures to identify each losable item and its writer. Attribution does not waive durable-resumption requirements or another writer's endangered work.
§K10 "records the account it was derived under" | ADOPTED | Cross-profile unknown-account evidence and the probe's verified `unknown` default justify the change: kernel K10's observable now requires `probed_under` to identify the current account and treats a missing, `unknown` or mismatched identity as stale, with a re-probe before provider work. Parity agreement alone cannot validate an unstamped inventory.
§K11 "apply to every report a factory makes about itself" | REJECTED(existing reporting obligation) | Incorrect command citations already violate honest reporting. The measured failure is within code; it does not justify a kernel-wide command-quotation rule.
§K12 "Every project that runs the kernel files what happened" | ADOPTED | The filing supplies feedback. The bus-verified weakness raised under §U3 is answered separately in kernel K12's observable.
§P:code subject-identity "git tree OID of the candidate commit" | ADOPTED | FIT recorded; tree-component recomputation is supported, and aggregate identity and claimant requirements remain separate. No text change from this line.
§P:code acceptance-evidence "pinned acceptance runs at the exact commit" | ADOPTED | `profiles/code.md` Acceptance evidence (K5) requires checks meaningful for the declared artifact kind while retaining exact identity, durable receipts and independent acceptance.
§P:code independent-key "a CI runner the producer does not control" | REJECTED(base-green prerequisite unsupported) | A green base neither proves candidate acceptance nor defines verifier independence. The candidate still needs its required passing evidence; unrelated base failures require explicit adjudication.
§P:code resource-terminals "typed terminals, no partial green" | ADOPTED | FIT recorded; an unusable test environment was labelled UNEVALUABLE rather than accepted. No text change.
§P:code delivery-target "integration branch via the project's landing path" | ADOPTED | FIT recorded; reported fast-forward publication supports the landing path, and delivery alone does not cure missing acceptance. No text change.
§P:code human-gates "anything the project's register lists" | ADOPTED | FIT recorded; releases and tags remained gated while authorised documentation work proceeded. No text change.

### Untested

§U1 "At least five member projects have filed" | ROUTED(Conjugal harvest-status membership bench) | In-memory execution admitted a ghost filing. Tool enumeration is not criterion-1 proof; mandatory adoption blocks would also exclude legitimate DOGFOOD-PENDING evidence.
§U2 "The word cap in the header does not rise" | ROUTED(Conjugal cross-profile size-budget bench) | The r1-to-r2 diff confirms profile growth, but not policy evasion. A combined kernel/profile/bootstrap cap needs tested scope and budget.
§U3 "showing it `HARVESTED`" | ADOPTED | The test and in-memory status execution confirm that blob-only acknowledgement becomes HARVESTED. Kernel K12's observable now requires a disposition for every filed finding, including Untested items, proposals and addendum claims, bound to the filing's blob; parser enforcement belongs to Conjugal's tool bench.
§U4 "Determinism class" | ROUTED(judgment and measured-objective profile benches) | Four exhaustive classes and two-judge minima lack exercised domain evidence. No text change.
§U5 "Parallel drafting" | ROUTED(Conjugal bootstrap discovery and claims bench) | Test pre-draft discovery and claim coordination. Bootstrap changes are outside the allowlist; no kernel amendment.

## Header

HEADER: Filed against kernel r1 and code@r1; assess changed acceptance and independent-key wording against r2.
HEADER: providers must not credit ad hoc result files or Agent results as sentinel-complete lanes; the disclosed evidence supports no such provider count.
HEADER: "no R9 posture run" is not a computed posture, and model review contributed; retain the disclosed ad hoc provenance without claiming an R9 posture.
HEADER: subjects: 3 counts a never-delivered draft and omits the absence of pre-work profile declarations. Record two delivered retrospective subjects and one undelivered draft, with zero qualifying kernel end-to-end subjects.

A REJECTED or ROUTED line is an answer, not a dismissal. Re-file with new bench evidence and it will be read again.
