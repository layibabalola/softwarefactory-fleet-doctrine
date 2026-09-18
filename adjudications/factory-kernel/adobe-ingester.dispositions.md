filing_blob: 5e285849969134fb8cafa7ac1fc520864496ae0e
filing_ref:  origin/review/adobe-ingester-kernel-2026-09-17
spec_commit: 5d1d0d95b3b82e853cd90019a3cd3457df309304
harvested_by: conjugal (interim kernel steward), 2026-09-17, automated harvest run 20260917T193405Z-ab7b8aef
arbiter: gpt-6-astra (high) · consolidator: claude-fable-5 · lint: claude-opus-5 + gpt-5.6-sol · orchestrator: claude-opus-5

# Dispositions for adobe-ingester's filing on specs/fleet-factory-kernel.md r4 (now r5) and profiles/code.md r4 (now r5)

21 lines: 19 clause and profile findings (12 ADOPTED · 0 ADOPTED-CONDITIONAL · 3 REJECTED · 4 ROUTED) and 2 Untested
(2 ROUTED), plus 1 HEADER line. Filing verdicts (INSTANCE-FAILURE excluded per kernel §5): 1 FIT · 12 FRICTION · 0 BREAK
· 0 N/A · 3 UNEXERCISED; separately 3 INSTANCE-FAILURE (K8, K11, P:code dispatch-preflight).

Rule: kernel §5, not the owner-bench rule. A BREAK with a concrete counterexample from any profile wins; FRICTION
changes the kernel only when two or more profiles report it; one profile's FRICTION changes that profile;
INSTANCE-FAILURE changes no text (kernel §4). **This filing is `code`-only, so none of its FRICTION could amend the
kernel this round.** Its K7, P:code acceptance-evidence and P:code resource-terminals lines landed in
`profiles/code.md` r5 (Delivery target, Acceptance evidence, Resource terminals). The kernel moved to r5 on
dng-auto-processor's measured-objective BREAK, not on this filing. This filing's window opened 2026-09-16T02:34Z,
after the kernel first existed (2026-09-14T20:49:38Z). Line format:
`§<id> "<anchor>" | <DISPOSITION> | <what changed, or why not>`.

## Findings

§K1 "an adjudicator never supplies the key it is adjudicating" | REJECTED(unexercised) | No subject reached acceptance in the window, so nothing tests the producer-only prohibition. The role note is retained as reported: hub design, vote and adjudication sit in one actor (Sol), which the filing itself flags for the harvester rather than claims as a finding.
§K2 "Everything unlisted is autonomous." | ROUTED(adobe admission-grammar bench) | Two identically worded announcements getting different outcomes (16e accepted 16:28:41Z, 16g refused 20:01:05Z) is an admission-grammar defect in one instance. It does not establish a missing kernel invariant, and `code`-only FRICTION cannot amend K2. Re-file after the grammar is machine-checked.
§K3 "One claimant holds a subject at a time" | ADOPTED | Recorded. Two auditor sessions on shared surfaces settled by an ad-hoc holder/expiry block supports claims discipline, not mandatory fleet lease tooling. The kernel's K3 changed this round on dng-auto-processor's BREAK, in the direction this line wants: staleness must be decidable and releasable by an observer other than the claimant, and an expiring lease is named as one mechanism, not the required one.
§K4 "Work is complete only on positive evidence" | ADOPTED | Recorded, no text change. The CRLF/`(?m)^...$` mismatch at `Invoke-FactoryClaudeLane.ps1:1645` makes the lane report WRAPPER_FAILED on published votes: an instance failing an existing positive-evidence rule, not a gap in it.
§K5 "is a typed terminal with zero partial credit." | ADOPTED | Recorded. The clause held — rev7 and rev8 were typed terminals with no credit. The frozen product track is the cost of an instance's own acceptance transaction, and a closure that cannot finish inside its lane wall supplies no waiver. The mechanism-declaration half is answered in `profiles/code.md` Delivery target (see §K7).
§K6 "a key from an independence class other than the producer's." | ROUTED(adobe alternate-key bench) | Single-shot Claude ballots being the only cross-family key is a real cost, but the filing's own PROOF names the remedy: retain raw output so a ballot failure is diagnosable, or stand up a second qualified key backend. Neither was exercised. `code`-only FRICTION cannot amend K6; see agent-bridge's P:code independent-key, which did change the profile.
§K7 "Acceptance and delivery are separate states." | ADOPTED | `profiles/code.md` Delivery target (K7) now requires that stricter instance closure mechanisms and their budgets are declared before work. The kernel sentence is unchanged: one profile's FRICTION changes that profile.
§K8 "never failing the factory closed." | ADOPTED | Recorded as INSTANCE-FAILURE, which by kernel §4 counts toward health and never toward a kernel change. 3 h 39 m of 30-minute wakes each dying in ~5 s on the usage limit, with no QUOTA-DORMANT terminal and no wake suppression, is the instance failing K8 as written.
§K9 "Accounts rotate without warning." | ROUTED(adobe interrupted-effect bench) | Resumption worked; the proposed addition ("each effect a session starts is durably recorded before the next effect begins") is a new universal serialisation obligation on the strength of two wall-kill strandings in one instance. dng-auto-processor also filed K9 FRICTION from `measured-objective`, but for a different defect (the gate is a procedure, not a command), so the two do not establish one missing invariant and neither remedy entered the kernel. Test durable effect recovery first.
§K10 "Account parity is verified before any provider work." | REJECTED(unexercised) | The filing states the observable is not evidenced: no dispatch-bound inventory snapshot with `probed_under` naming the account used by a ballot. An ALIGNED drift hook is not that snapshot.
§K11 "R1–R5, R7, R8 and R9 apply to every report" | ADOPTED | Recorded as INSTANCE-FAILURE. Two refuted causal advisories and a 2-of-12-rule certification are reporting failures under existing rules; each was corrected on the record and the method changed to measured cost laws. The filing also discloses that its own draft carried false figures caught before publication. No text change.
§K12 "Every project that runs the kernel files what happened to" | REJECTED(unexercised) | Publication is not harvesting. The observable exists from this harvest onward: this file, bound to blob 5e285849.
§P:code subject-identity "a key on a different tree does not transfer." | ADOPTED | FIT recorded. Every Q-036 revision reset all votes because the frozen proposal bytes changed, with a per-revision SHA-256 in the HUB. No text change from this line; the Subject identity row changed on agent-bridge's runtime-manifest evidence.
§P:code acceptance-evidence "run at the exact commit and declared environment" | ADOPTED | Convergent with agent-bridge's P:code acceptance-evidence on the same defect from an independent bench. One consolidated replacement, not two layered: `profiles/code.md` Acceptance evidence now requires the acceptance contract to be bound by digest before work — checks, **harness limits**, review scope, round budget and round-closing rule — and to judge every round. That is the rule the undeclared 120 s per-case constant broke. The row also now reads "exact subject identity" rather than "exact commit", so runtime subjects are covered.
§P:code resource-terminals "typed terminals, no partial green" | ADOPTED | `profiles/code.md` Resource terminals now requires retaining the stopped candidate's bytes and receipts before rollback. The rev8 module surviving only because a later diagnostic rebuilt it is exactly the loss this prevents.
§P:code independent-key "a verifier from another model family (R3)" | ROUTED(adobe alternate-key bench) | Same bench as §K6. The profile's existing alternatives — a CI runner the producer does not control, an attended human verifier named by the register — are unexercised here, so no absence is established.
§P:code delivery-target "for feasibility subjects, the owner decision record" | ADOPTED | Consolidated into the §K7 Delivery target change; the filing itself routes this line to K7. One row, not two.
§P:code dispatch-preflight "launcher diagnostics are retained" | ADOPTED | Recorded as INSTANCE-FAILURE. Discarding provider output on the Sonnet rev6 PROVIDER_NONZERO run and the two Opus validator rejections violates text the profile already carries. No replacement; §4 excludes INSTANCE-FAILURE from text change.
§P:code budgets "wall time per suite, provider calls per subject" | ADOPTED | Recorded. The profiling (3,093 git spawns/479 s; 49.9 s tree parse; 70.7 s cache sorts; 9.97 s typed probe) supports instance repair. Semantic equivalence of the fast probe is open by the filing's own account (HUB ~32105, ~32204) and is not credited here.
§Untested-1 "A PRODUCT subject through the kernel: none ran" | ROUTED(adobe product-subject bench) | Run the owner-authorised product subject banked as code@r4 under directive 2026-09-17a; it is what would exercise K3–K7 on product code. Nothing here is decidable from this window.
§Untested-2 "Astra (gpt-6-astra) as a routine advisory design pass" | ROUTED(adobe Astra-advisory bench) | Directive 2026-09-15d clause 6 measurement has not been collected. Collect it; one use is not a measurement.

## Header

HEADER: `posture:` is not in R9's computed form (`harvest-status.py` flag POSTURE-NOT-R9-COMPUTED). "model review contributed (Sonnet APPROVE on Q-036 rev7 and rev8; Opus AMEND on Q-036 rev2)" and "passed one adversarial gpt-6-astra read-only review" disclose contribution and an adversarial pass; neither is a posture computed by the R9 tool. Harvested on what the provenance supports: the `providers:` line is specific and consistent with the body, and the review's output digest is recorded, so the findings stand. Run the R9 tool for the next filing.
