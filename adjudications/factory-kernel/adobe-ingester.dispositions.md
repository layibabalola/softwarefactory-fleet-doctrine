filing_blob: 7f1aea3bb5af6188556895c4c86a2c70c0c3a6e4
filing_ref:  origin/review/adobe-ingester-kernel-2026-09-14
spec_commit: ec32d6eeed18b51be09f9b1c087b482087b9e902
harvested_by: conjugal (interim kernel steward), 2026-09-14, automated harvest run 20260914T221904Z-51d5a96b
arbiter: gpt-6-astra (high) · consolidator: claude-fable-5 · lint: claude-opus-5 + gpt-5.6-sol · orchestrator: claude-opus-5

# Dispositions for adobe-ingester's filing on specs/fleet-factory-kernel.md r1 (now r2) and profiles/code.md r1 (now r2)

27 lines: 17 clause and profile findings (13 ADOPTED · 3 ADOPTED-CONDITIONAL · 1 REJECTED) and 10 Untested items (2 ADOPTED · 8 ROUTED).
Rule: kernel §5. A BREAK with a concrete counterexample wins over FIT elsewhere. FRICTION changes the kernel only when
two or more profiles report it; both filings this harvest are `code`, so their FRICTION lands in `profiles/code.md` r2.
The kernel is now r2. Line format: `§<id> "<anchor>" | <DISPOSITION> | <what changed, or why not>`.

## Findings

§K1 "nobody accepts their own work" | ADOPTED | FIT recorded; no text change; role separation does not establish completed acceptance.
§K2 "one register" | ADOPTED | Fleet-tool writes are classified in code's reachable authority register (`profiles/code.md` Human gates (K2)); no kernel change from this FRICTION.
§K3 "content digest" | ADOPTED | FIT recorded; no text change; aggregate identity and expiring lease remain unproved.
§K4 "four different facts" | ADOPTED | FIT recorded; no text change.
§K5 "acceptance evidence exists" | ADOPTED | Code receipts bind durable content digests; mutable-log offsets are locators only (`profiles/code.md` Acceptance evidence (K5)). No retrospective profile declaration.
§K6 "independence class other than the producer's" | ADOPTED | FIT recorded; no text change.
§K7 "one transaction" | ADOPTED | FIT recorded; no text change; observed blocking does not prove delivery or the required terminal spelling.
§K8 "never failing the factory closed" | ADOPTED-CONDITIONAL(adobe-ingester) | Code parks unavailable-key work with a typed terminal and resume condition (`profiles/code.md` Resource terminals (K5)); no weakening of K6.
§K9 "resumes from the project's tree" | ADOPTED | Code dispatch checks resume evidence (`profiles/code.md` Dispatch preflight (K9, K10)); adobe-ingester must repair and rerun its failed checkpoint task.
§K10 "Account parity is verified" | ADOPTED | FIT recorded; no text change; this observation does not establish another run's pre-dispatch inventory.
§K11 "every report" | REJECTED(already covered) | K11 already covers bootstrap reports; correct timestamps from measured clock evidence.
§K12 "Every project that runs the kernel" | ADOPTED | Concrete frozen-tree BREAK wins. Kernel §3 now lists "a project tree that fleet tooling may write into"; f6e1972 guards are landed, but the project rerun remains outstanding.
§P:code subject-identity "git tree OID" | ADOPTED | FIT recorded; no text change from this line; K3's aggregate remains unproved.
§P:code acceptance-evidence "pinned acceptance runs" | ADOPTED | Durable receipt binding merged with agent-bridge's environment binding (`profiles/code.md` Acceptance evidence (K5)).
§P:code independent-key "a verifier from another model family" | ADOPTED-CONDITIONAL(adobe-ingester) | A register-named attended human verifier other than the producer is permitted (`profiles/code.md` Independent key (K6)).
§P:code delivery-target "integration branch" | ADOPTED-CONDITIONAL(adobe-ingester) | The owner decision record is permitted for feasibility subjects (`profiles/code.md` Delivery target (K7)).
§P:code human-gates "anything the project's register lists" | ADOPTED | FIT recorded; no text change from this line.

### Untested

§U1 "Estimates" | ROUTED(Conjugal harvest ledger and future-domain benches) | Forecasts have no evidentiary weight.
§U1a "v1 ratified within about 90 days" | ROUTED(Conjugal harvest ledger) | Compare with the eventual dated ratification.
§U1b "v1 usable unchanged" | ROUTED(creative-writing, game-engine, mobile-app, business-strategy, 3d-render, realtime-web-3d benches) | Requires real subjects.
§U1c "future domain filing" | ROUTED(Conjugal harvest ledger) | Check actual filings after 2026-12-14.
§U2 "criterion 2 can be met" | ROUTED(non-code creative or asset bench) | The textual observation is true; an additional finalisation gate lacks tested justification.
§U3 "kernel assumes AI-model workers" | ROUTED(human-only creative-writing or 3d-render bench) | Test applicability before creating an overlay or removing clauses.
§U4 "K2 conflicts with business-strategy" | ADOPTED | Bus-verified contradiction: kernel K2's escalation sentence now respects decisions the register explicitly reserves for the owner.
§U5 "revision clock does not track text changes" | ADOPTED | Steward verified at 45f4a2c. This harvest bumps the kernel to r2 (header; code profile follows). Kernel §5 Versions now defines a harvest as one completed adjudication of a recorded eligible filing set and requires content-digest stability for finalisation; revision-check automation is routed to Conjugal. Seven days is unsupported.
§U6 "Base rate" | ROUTED(Conjugal doctrine census) | Recompute the counts with a dated population; do not adopt reported estimates.
§U7 "health enum has no word for stalled" | ROUTED(adobe-ingester and agent-bridge code benches) | Test a stalled-state observable before changing the enum.

NOTE: the arbiter's EDIT 4 would have rewritten the §5 "Harvest runs continuously" paragraph on kernel §3 grounds; the steward did not apply it, because no filing proposed replacement text for that paragraph and it quotes owner direction.

## Header

HEADER: instance names a git-excluded auditor draft, not a landed implementation; the reproduced map is evidence only.
HEADER: posture "no model review" conflicts with three Opus agents contributing Untested analysis. Disclose that contribution and obtain applicable computed posture; providers "none" remains consistent with no sentinel-complete lanes.
HEADER: adoption remains DOGFOOD-PENDING; subjects supplies zero completed end-to-end subjects.

A REJECTED or ROUTED line is an answer, not a dismissal. Re-file with new bench evidence and it will be read again.
