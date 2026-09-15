filing_blob: 30aff3a984c0caa044b750de7ab9646048e71fb2
filing_ref:  origin/review/magic-lantern_dannephoto-kernel-2026-09-14
spec_commit: c7e37a54999f9705623b9ffdff397592b8394723
harvested_by: conjugal (interim kernel steward), 2026-09-15, automated harvest run 20260915T051905Z-86585ba5
arbiter: gpt-6-astra (high) · consolidator: claude-fable-5 · lint: claude-opus-5 + gpt-5.6-sol · orchestrator: claude-opus-5

# Dispositions for magic-lantern_dannephoto's filing on specs/fleet-factory-kernel.md r1 (now r3) and profiles/hardware-in-loop.md r1 (now r2)

22 lines: 16 clause and profile findings (8 ADOPTED · 1 ADOPTED-CONDITIONAL · 7 REJECTED · 0 ROUTED) and 6 Steward proposals (6 ROUTED).
Rule: kernel §5. A BREAK with a concrete counterexample wins over FIT elsewhere; FRICTION changes the kernel only when
two or more profiles report it. This filing's BREAK (P:hardware-in-loop acceptance-evidence) wins and narrows
`profiles/hardware-in-loop.md` r2; its K10 FRICTION matched cloudvore's under `code`, so kernel K10's observable changed
(r3); its K1 FRICTION landed in the hardware-in-loop profile. Line format: `§<id> "<anchor>" | <DISPOSITION> | <what changed, or why not>`.

## Findings

§K1 "never accepted on evidence whose only author is its producer" | ADOPTED-CONDITIONAL(magic-lantern_dannephoto recovery-ledger bench) | `profiles/hardware-in-loop.md` Acceptance evidence (K5) now records producer and verifier for every accepted subject; the kernel's single-subject observable is unchanged.
§K2 "one register of what needs the owner" | ADOPTED | FIT recorded; the named authority supported bounded autonomous work while owner-only operations remained parked. No text change.
§K3 "the identity string of one subject" | REJECTED(unexercised) | Historical accepted commits do not establish an exercised built-image identity. No text change.
§K4 "the negative case the project checked" | REJECTED(unexercised) | Mixed historical status trees are observations requiring receipt audit, not exercised acceptance evidence.
§K5 "the profile line recorded before work" | REJECTED(unexercised) | No subject declared the profile before work. No retrospective credit.
§K6 "the independence class of each key on one accepted subject" | REJECTED(unexercised) | No hardware key was supplied; historical reviewer identities do not exercise this acceptance path.
§K7 "how the project detects an accepted subject that never delivered" | REJECTED(unexercised) | Historical blocked delivery tasks do not establish a completed delivery transaction.
§K8 "what happened to in-flight work at the last quota event" | REJECTED(unexercised) | Low remaining quota without in-flight work does not exercise quota handling.
§K9 "resumes from the project's tree and the bus alone" | ADOPTED | FIT recorded; durable handoff, continuation instructions and the reported validator pass support resumption. No text change.
§K10 "records the account it was derived under" | ADOPTED | The probe's `unknown` default is bus-verified and also reported by code. Kernel K10's observable now requires `probed_under` to identify the current account and treats a missing, `unknown` or mismatched identity as stale, without assuming identical fingerprint encodings.
§K11 "apply to every report a factory makes about itself" | ADOPTED | FIT recorded; the cited review's computed posture and publication support its scoped reporting claim, but confer no review standing on this filing.
§K12 "showing it `HARVESTED` after the next harvest" | REJECTED(unexercised) | The first filing had not yet received its harvest outcome. No conformance credit from this line.
§P:hardware-in-loop human-gates "every hardware session" | ADOPTED | FIT recorded; owner-operated sessions remained gated. Kernel §7 gap 4 now records that hardware-in-loop has a bench filing, replacing the obsolete statement that no non-code profile had one.
§P:hardware-in-loop resource-terminals "the subject waits and nothing is inferred" | ADOPTED | FIT recorded; unavailable hardware and operators remained typed blocks with no inferred credit. No text change.
§P:hardware-in-loop acceptance-evidence "emulator runs (for example QEMU) are necessary but never sufficient" | ADOPTED | BREAK wins: unobtainable lawful emulator inputs make unconditional necessity impossible. `profiles/hardware-in-loop.md` Acceptance evidence (K5) now requires emulator runs only where inputs can lawfully be obtained, has the acceptance receipt record why emulator evidence is absent otherwise, and retains exact-image hardware evidence and kernel independence.
§P:hardware-in-loop stress-on-the-kernel "bounded by attendance, not compute" | ADOPTED | FIT recorded; hardware attendance constrains delivery despite governance activity. No text change from this line.

### Steward proposals

§SP1 "measure governance motion" | ROUTED(magic-lantern_dannephoto governance-throughput bench) | Validate the proposed alarm against eligible work and completed subjects. Commit ratios alone do not establish failure; steward-project evidence is not adjudicated here.
§SP2 "admission is bounded by eligible work" | ROUTED(magic-lantern_dannephoto admission bench) | Test executor admission against actual eligible work. This filing supplies no measured excess-executor event supporting a new universal clause.
§SP3 "liveness is measured, not declared" | ROUTED(magic-lantern_dannephoto scheduler-liveness bench) | Verify app-automation execution and scheduler state. The proposed fourteen-day interval lacks tested justification.
§SP4 "satisfiable by failed evidence" | ROUTED(magic-lantern_dannephoto B03 receipt-audit bench) | Audit which exact run acceptance used. K1, K4 and K6 already prohibit failed or producer-only acceptance; mixed historical evidence alone does not establish a textual loophole.
§SP5 "machine-measured observables" | ROUTED(Conjugal factory-kernel-probe tool bench) | Verify mappings, tests and identity-bound outputs before adopting the probe. Tool adoption is outside this harvest's edit allowlist.
§SP6 "collides with the adoption ledger's closed project set" | ROUTED(Conjugal bootstrap and adoption-census owners) | Bus test and checker confirm the closed-set requirement. Coordinate first-project spec creation with census updates; neither bootstrap nor census changes may be emitted here.

## Header

HEADER: Filed against kernel r1; hardware-in-loop@r1 is still the current profile before these edits.
HEADER: providers describes the probe's self-review, not subject acceptance or review of this filing; preserve that scope without inferring cross-family review standing for the filing.

A REJECTED or ROUTED line is an answer, not a dismissal. Re-file with new bench evidence and it will be read again.
