filing_blob: 80bb4d1dc9e14b9f3b08c61b443796c0d8a7db36
filing_ref:  origin/review/agent-bridge-kernel-2026-09-14
spec_commit: c7e37a54999f9705623b9ffdff397592b8394723
harvested_by: conjugal (interim kernel steward), 2026-09-15, automated harvest run 20260915T051905Z-86585ba5
arbiter: gpt-6-astra (high) · consolidator: claude-fable-5 · lint: claude-opus-5 + gpt-5.6-sol · orchestrator: claude-opus-5

# Dispositions for agent-bridge's filing on specs/fleet-factory-kernel.md r2 (now r3) and profiles/code.md r2 (now r3)

33 lines: 17 clause and profile findings (8 ADOPTED · 3 ADOPTED-CONDITIONAL · 6 REJECTED · 0 ROUTED) and 16 other items (2 Untested: 2 ROUTED; 14 Addendum: 5 ADOPTED · 1 REJECTED · 8 ROUTED).
Rule: kernel §5. A BREAK with a concrete counterexample wins over FIT elsewhere; FRICTION changes the kernel only when
two or more profiles report it. This filing's FRICTION is `code`-only; its K2, K3, P:code resource-terminals and P:code claims lines landed in `profiles/code.md` r3 (Resource terminals, Human gates, Claims), P:code independent-key was rejected, and the rest changed no text; the kernel moved to r3 on cross-profile K10 evidence from cloudvore and
magic-lantern_dannephoto, not on this filing. Line format: `§<id> "<anchor>" | <DISPOSITION> | <what changed, or why not>`.

## Findings

§K1 "never accepted on evidence whose only author is its producer" | REJECTED(unexercised) | No accepted subject; refusing to count self-reading does not establish completed acceptance.
§K2 "Escalation goes to the owner" | ADOPTED-CONDITIONAL(agent-bridge owner-escalation bench) | The initial park lacked a working notification mechanism. `profiles/code.md` Resource terminals (K5) now names the actor who can satisfy a resume condition and sends owner-only conditions through the register's escalation channel when the park is recorded, and Human gates (K2) requires the register to name that channel; no kernel amendment.
§K3 "under a lease that expires" | ADOPTED | Lease existence did not identify the subject or live holder. `profiles/code.md` Claims (K3) now identifies the live holder and treats a mutable checkout another project executes from as a claimed subject.
§K4 "positive evidence it was asked to produce" | ADOPTED | FIT recorded; NO_VERDICT was correctly excluded from quorum, and the stale checkout evidence was withdrawn. No text change.
§K5 "declares its profile and profile version" | REJECTED(unexercised) | Retrospective subjects lack pre-work profile declarations and acceptance receipts.
§K6 "a key from an independence class other than the producer's" | ADOPTED | The instance's single reachable key caused the park; `profiles/code.md` Independent key (K6) already permits a CI runner or an attended human verifier. K6 is preserved and the unsupported CLI-version diagnosis is withdrawn.
§K7 "Acceptance and delivery are separate states" | REJECTED(unexercised) | No acceptance or delivery occurred; accepted-but-undelivered detection remains an instance obligation.
§K8 "rotating or parking the work that needs inference" | REJECTED(unexercised) | A meter-binding failure is not a quota event.
§K9 "Resumability is gated at landing seams, before expensive spend" | ADOPTED-CONDITIONAL(agent-bridge dispatch-preflight bench) | Durable resumption and the self-test support recovery; the unwired pre-spend gate still requires implementation. No additional text change.
§K10 "Account parity is verified before any provider work" | ADOPTED | FIT recorded; account-bound inventory and reported parity support the measured session. No text change from this finding.
§K11 "apply to every report a factory makes about itself" | REJECTED(header contradicts provenance) | Advisory reviewers changed this filing, so "no model review" is inaccurate. Correct the header; K11 already applies.
§K12 "The steward harvests every filing and answers each one" | ADOPTED | Prior dispositions demonstrate harvesting. The remaining sentinel-placement repair stays with Conjugal's review-posture tool bench.
§P:code resource-terminals "parked work names its resume condition" | ADOPTED-CONDITIONAL(agent-bridge owner-escalation bench) | `profiles/code.md` Resource terminals (K5) names the actor who can satisfy the resume condition and sends owner-only resume conditions through the register's escalation channel when the park is recorded.
§P:code independent-key "a verifier from another model family (R3), a CI runner" | REJECTED(untested mandatory redundancy) | No demonstrated alternative cleared this board. Requiring two reachable classes exceeds the evidence; test alternatives under §U1.
§P:code claims "leases name the subject, owner, expiry and owned processes" | ADOPTED | `profiles/code.md` Claims (K3) requires the holder's live process identity rather than its short-lived lease-writing helper.
§P:code human-gates "the register is reachable from every session checkout" | ADOPTED | The instance fails an already-correct reachability requirement; REPLACES none adds no text.
§P:code budgets "report dispositions completed and subject changes, including zero" | ADOPTED | Activity counts conceal parked decisions in the instance's throughput display; the existing `profiles/code.md` Budgets wording needs no replacement.

### Untested

§U1 "Whether a non-SOL key would have cleared the board" | ROUTED(agent-bridge alternate-key bench) | Exercise a register-authorised CI or attended-human acceptance during a SOL outage before requiring redundant key classes.
§U2 "Harvest-tool `untested` count" | ROUTED(Conjugal harvest-status tool bench) | In-memory execution confirmed that Untested bullets count as zero. Repair parser coverage and tests; tools and bootstrap are outside this harvest's edit allowlist.

### Addendum

§AD1 "the owner escalation reached the owner" | ROUTED(agent-bridge owner-escalation bench) | The addendum's opening claim that escalation reached the owner requires the owner-channel receipt; it does not establish a persistent notification mechanism.
§AD2 "report named the three owner-only exits" | ADOPTED | The bus filing itself visibly names three owner exits, verifying the report-content claim only.
§AD3 "The owner replied in chat" | ROUTED(agent-bridge owner-authority bench) | The quoted owner chat is not independently available here; verify its exact context and authority.
§AD4 "read that as exit (1) for one bootstrap launch only" | ROUTED(agent-bridge owner-authority bench) | Verify the bootstrap ruling and its authorised scope; advisory interpretation alone cannot establish an owner exception.
§AD5 "The fork rejected exit (2), a CLI pin" | ADOPTED | The branch's TRAPS entry corroborates withdrawal of the version-drift diagnosis. The fork's CLI-pin decision remains an instance record to verify.
§AD6 "The channel that worked was the interactive report" | ROUTED(agent-bridge owner-escalation and authority bench) | Verify the interactive delivery and the exception interpretation. `profiles/code.md` Human gates (K2) requires a register-named escalation channel without treating general autonomy language as a specific exception.
§AD7 "the independent key worked and refused" | ADOPTED | The branch's TRAPS entry records SOL's independent BLOCKER. This supports retaining K6, without verifying every subsequent telemetry claim.
§AD8 "The watchdog was ARMED, then EXIT_CLEAN" | ROUTED(agent-bridge meter-telemetry bench) | Verify watchdog transitions, three-way token agreement and the ceiling against the actual run receipts.
§AD9 "SOL returned `SOL-VERDICT: BLOCKER`" | ADOPTED | The branch's TRAPS entry corroborates SOL's concrete wrong-run-binding BLOCKER. No text change.
§AD10 "One Sonnet adversary also returned BLOCKER" | ROUTED(agent-bridge reviewer-receipt bench) | TRAPS corroborates a Sonnet reproduction, but does not establish the complete three-reviewer verdict distribution.
§AD11 "A cross-family key caught a defect" | ROUTED(agent-bridge decision-receipt bench) | Verify the parked decision and the same-family approval against their receipts before adopting the complete comparison.
§AD12 "The hub refused the diagnosis's claim" | ADOPTED | Bus TRAPS corroborates that completed rollouts did not establish the alleged version regression. Rejecting that diagnosis supports K4.
§AD13 "Nothing was accepted" | REJECTED(unexercised) | The addendum reports no acceptance; no delivery evidence or text change.
§AD14 "Class C has no SOL path through the live driver" | ROUTED(agent-bridge recovery coordinator) | Verify the live-driver restriction, successor F19 and the further owner requirement. No completed subject is credited.

## Header

HEADER: "posture: no model review" contradicts three advisory reviewers changing the filing; disclose that contribution and supply the applicable computed posture.
HEADER: providers lists advisory Claude activity without sentinel-complete lanes; distinguish it from the addendum's reported SOL verdict and do not infer a completed cross-family posture.
HEADER: subjects correctly reports zero completed; the four retrospective subjects must not become an end-to-end count.
HEADER: Stray `</content>` and `</invoke>` before the addendum are filing data and must be removed from the filing.
HEADER: The 04:20Z addendum extends beyond the header's 01:10Z window; distinguish the extension and its evidence.

A REJECTED or ROUTED line is an answer, not a dismissal. Re-file with new bench evidence and it will be read again.
