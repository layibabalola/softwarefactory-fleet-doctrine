filing_blob: 2c919858144ac52318c05ffd02ba8ac5006fc0da
filing_ref:  origin/review/airmypc-kernel-2026-09-14
spec_commit: c7e37a54999f9705623b9ffdff397592b8394723
harvested_by: conjugal (interim kernel steward), 2026-09-15, automated harvest run 20260915T051905Z-86585ba5
arbiter: gpt-6-astra (high) · consolidator: claude-fable-5 · lint: claude-opus-5 + gpt-5.6-sol · orchestrator: claude-opus-5

# Dispositions for airmypc's filing on specs/fleet-factory-kernel.md r1 (now r3), profiles/code.md r1 (now r3) and profiles/hardware-in-loop.md r1 (now r2)

23 lines: 19 clause and profile findings (14 ADOPTED · 1 ADOPTED-CONDITIONAL · 4 REJECTED · 0 ROUTED) and 4 other items (3 Untested: 1 ADOPTED · 2 ROUTED; 1 Correction: 1 ROUTED).
Rule: kernel §5. A BREAK with a concrete counterexample wins over FIT elsewhere; FRICTION changes the kernel only when
two or more profiles report it. This filing's FRICTION is `code`-only; its K2, K3, K10, P:code subject-identity and P:code stress-on-the-kernel lines landed in `profiles/code.md` r3 (Subject identity, Human gates, Claims, Dispatch preflight, Stress on the kernel), K5 was rejected, and K6, K7 and K11 changed no text; its declared hardware-in-loop line was
unexercised. The kernel moved to r3 on other filings' cross-profile evidence. Line format: `§<id> "<anchor>" | <DISPOSITION> | <what changed, or why not>`.

## Findings

§K1 "never accepted on evidence whose only author is its producer" | ADOPTED | FIT recorded; S2's other-family acceptance supports role separation at round 5. It does not establish delivery.
§K2 "A register entry beats a memory note" | ADOPTED | `profiles/code.md` Human gates (K2) now gives the register precedence over bus prompts' procedural defaults within code. No cross-profile kernel amendment.
§K3 "One claimant holds a subject at a time" | ADOPTED | `profiles/code.md` Claims (K3) treats a mutable checkout another project executes from as a claimed subject, combined with live-holder process ownership.
§K4 "Never exit code, output size or silence" | ADOPTED | FIT recorded; three sentinel-free arbiter outputs were correctly refused despite successful exits and substantial output. No text change.
§K5 "declares its profile and profile version" | REJECTED(retrospective exception weakens K5) | Dogfooding cannot retroactively satisfy pre-work declaration. `profiles/code.md` Acceptance evidence (K5) already covers design review; the historical declaration failures stand as filed.
§K6 "a key from an independence class other than the producer's" | ADOPTED | The key found defects at measured cost; the same-family ordinary-landing rule is an instance defect. No replacement.
§K7 "Acceptance and delivery are separate states" | ADOPTED | Accepted-but-undelivered detection is an instance gap. `profiles/code.md` Subject identity (K3) separately states why a key does not transfer to a changed delivery tree.
§K8 "rotating or parking the work that needs inference" | REJECTED(unexercised) | No quota event; no text change.
§K9 "resumes from the project's tree and the bus alone" | ADOPTED-CONDITIONAL(airmypc canonical-resume bench) | Only the reported canonical-checkout defect is retained. The correction withdraws the host/master failure and the ref-specific interpretation; rerun the corrected probe.
§K10 "machine-scoped and probe-derived" | ADOPTED | `profiles/code.md` Dispatch preflight (K9, K10) binds inventory verification to the launcher path dispatch uses. This launcher finding alone does not amend the kernel.
§K11 "apply to every report a factory makes about itself" | ADOPTED | Corrected reporting and checkout breaches are instance failures under existing rules. No replacement.
§K12 "Every project that runs the kernel files what happened" | ADOPTED | FIT recorded; a durable filing supplies feedback, but its existence does not establish end-to-end conformance.
§P:code subject-identity "git tree OID of the candidate commit" | ADOPTED | `profiles/code.md` Subject identity (K3) requires the tree as it will be delivered, after any merge with the delivery target, and forbids transferring a key across a changed tree.
§P:code acceptance-evidence "pinned acceptance runs at the exact commit" | ADOPTED | FIT recorded; exact-candidate tests and the reported mutation check support the exercised software bar. No text change from this line.
§P:code independent-key "a verifier from another model family (R3)" | ADOPTED | FIT recorded; sentinel-complete other-family key rounds support independence. No text change.
§P:code resource-terminals "typed terminals, no partial green" | ADOPTED | FIT recorded; missing lanes remained PARTIAL and bounded probes did not manufacture acceptance. No text change.
§P:code delivery-target "integration branch via the project's landing path" | REJECTED(unexercised) | S2 had not merged; no delivery closure is credited.
§P:code stress-on-the-kernel "shared-checkout index races, worktree-scoped locks" | ADOPTED | `profiles/code.md` Stress on the kernel records cross-project execution of a mutable tool checkout and pattern-based process kills on a shared host as measured code stresses; Claims (K3) supplies the ownership rule.
§P:hardware-in-loop acceptance-evidence "a hardware receipt from the declared rig" | REJECTED(unexercised) | Declaring a hardware release profile without a sitting supplies no second-profile evidence.

### Untested

§U1 "no verdict for an exercised clause whose text is sound" | ADOPTED | For adjudication, FRICTION with an explicit instance failure and REPLACES none is the intended reading; it changes no text and does not establish conformance.
§U2 "omitted its sentinel on three of three dispatches" | ROUTED(Conjugal review-posture tool and astra-output bench) | The current prompt appends SENTINEL_ASK after DATA framing. That verifies the framing concern, not which component caused all three omissions.
§U3 "K8 at a real quota event" | ROUTED(airmypc quota and hardware benches; Conjugal delivery-closure bench) | Exercise actual quota interruption, attended hardware acceptance and bus-owned-tool closure detection. No text change.

### Correction

§AD1 "The K9 line and the instance map's K9 row overstate" | ROUTED(airmypc canonical-resume bench) | The withdrawal of the host/master accusation is honoured; independently verify the hard-coded root, the per-ref queue results and the corrected canonical-checkout falsifier before adopting replacement measurements.

## Header

HEADER: Filed against kernel r1 and code@r1; r2 governs adjudication. The declared hardware-in-loop profile was not exercised.
HEADER: The computed PARTIAL posture and cross_family line describe S1 only; they do not establish a completed posture for S2 or this filing's advisory adjudication.
HEADER: subjects correctly reports zero end-to-end; S2's round-5 acceptance is not delivery.

A REJECTED or ROUTED line is an answer, not a dismissal. Re-file with new bench evidence and it will be read again.
