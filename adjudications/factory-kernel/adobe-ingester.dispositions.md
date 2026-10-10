filing_blob: 2724e0a3b6b0ace15829e444bdb71fb6ba484b99
filing_ref:  origin/review/adobe-ingester-kernel-2026-10-09
spec_commit: d8e985d5c0195efdec04c808304cbe998baf26f9
harvested_by: conjugal (interim kernel steward), 2026-10-09, automated harvest run 20261009T234909Z-a08e5974
arbiter: gpt-6-astra (high) · consolidator: claude-fable-5 · lint: claude-opus-5.5 + gpt-5.6-sol · orchestrator: claude-opus-5-5

# Dispositions for adobe-ingester's fourth filing (re-run, 2026-10-09; declared kernel r4 / code@r4), adjudicated against specs/fleet-factory-kernel.md r5 (unchanged) and profiles/code.md r10 (unchanged)

**Supersedes this file's ruling on blob `5e285849969134fb8cafa7ac1fc520864496ae0e`** (run 20260917T193405Z-ab7b8aef,
spec commit `5d1d0d95b3b82e853cd90019a3cd3457df309304`; dispositions commit `8e2144b1f446e3e54bef9f60511b41570a2dc88e`),
which stands in bus history at that dispositions commit. None of its 21 dispositions or its HEADER line is withdrawn:
no disposition, routing, rejection or adopted text of that ruling is withdrawn, and its routes are re-answered below on
this window's evidence. The filing declares the revisions the instance ran (kernel r4 / code@r4, ADOPT at HUB
2026-09-16T02:34Z), as §5 requires, and quotes the current bus texts (r5 / r10); it is adjudicated against the current
texts without that reading upgrading the instance's declared contract.
Bus-side facts were VERIFIED directly by the arbiter and re-checked by the orchestrator: the filing blob and its ref
binding (tip `44dbc7d8`); kernel blob `6821c4c3390712522b699e72a1781bc9d89a771a` is r5 at 2,867 words and profile blob
`5511ccb3de09cd15f89e8c203e12076e21328a5f` is r10 at 1,209 words; the r4 kernel blob at `da4e920` is
`79fc893cff8a5e1341b874a722a9b8f53db29ff6`; the prior dispositions blob is `435f9f1215c03181cc3d1fec14e3576866be2f7b`;
`specs/adobe-ingester.md` (blob `c66c2229`) carries the quoted summary block and the "MEASURED 2026-09-25" section; and
the prior ledger row and its 21 disposition lines. Adobe repository observations — HUB headings and body counts, commit
and path counts, `sol.md` sizes and directive ids, `state.yaml` fields, work-order files, the `probed_under` search and
the posture computation — are attributed evidence, UNVERIFIED from the bus, and are adjudicated as attributed evidence,
not as independently reproduced measurements; unreadability is not a finding that they are false.

34 `§` lines: 18 clause and profile findings (14 ADOPTED · 0 ADOPTED-CONDITIONAL · 0 REJECTED · 4 ROUTED), 11 carried
items (5 ADOPTED · 0 ADOPTED-CONDITIONAL · 0 REJECTED · 6 ROUTED), 1 proposal (1 ROUTED) and 4 Untested readings
(4 ROUTED) — 19 ADOPTED · 0 ADOPTED-CONDITIONAL · 0 REJECTED · 15 ROUTED in all — plus 8 `HEADER:` lines (6 ADOPTED ·
2 ROUTED). Verdict census as ruled (INSTANCE-FAILURE excluded per kernel §5): **FIT 6 · FRICTION 2 · BREAK 0 · N/A 0 ·
UNEXERCISED 5; separately INSTANCE-FAILURE 5.** Clauses: 3 FIT (K4, K8, K9) · 2 FRICTION (K2, K12) · 0 BREAK · 0 N/A ·
3 UNEXERCISED (K3, K6, K7) · 4 INSTANCE-FAILURE (K1, K5, K10, K11). Profile: 3 FIT (subject-identity,
resource-terminals, budgets) · 0 FRICTION · 0 BREAK · 0 N/A · 2 UNEXERCISED (claims, independent-key) ·
1 INSTANCE-FAILURE (dispatch-preflight). As filed: FIT 6 · FRICTION 2 · BREAK 0 · N/A 0 · UNEXERCISED 4 ·
INSTANCE-FAILURE 6. Three reclassifications: **K3 INSTANCE-FAILURE → UNEXERCISED** (a sequential restart does not
establish simultaneous claimants), **P:code claims INSTANCE-FAILURE → UNEXERCISED** (loss of an in-memory start
allowance does not establish that a claim named the wrong live holder) and **K5 UNEXERCISED → INSTANCE-FAILURE** (the
instance's own bus spec reports two product work orders inside this window without a profile declaration). UNEXERCISED
awards no clause evidence and does not assert that no activity occurred. Carried items, the proposal, Untested readings
and headers are outside the census.

Rule: kernel §5, not the owner-bench rule. **What changed: nothing.** Kernel r5 and `code.md` r10 are byte-unchanged.
This filing is `code`-only, so neither of its FRICTION lines can amend the kernel: K2's register-retirement REPLACES is
reported by no second profile and its measured instance mechanism does not establish a domain-wide requirement; K12's
product-share REPLACES rests on a dng-auto-processor ruling candidate that is neither a kernel verdict line nor evidence automatically
attributable to its measured-objective profile, and on Magic Lantern's P1, which is expressly a proposal, previously
ROUTED, so no second profile's measured FRICTION on the same missing
instrument exists. Neither FRICTION changes a `code.md` row either. INSTANCE-FAILURE changes no text (kernel §4).
No §4 field, Status revision, profile revision or profile "Profile of" reference changes. Closed end-to-end subjects
from this filing: 0. Unresolved BREAKs: 0 submitted or established.

Line format: `§<id> "<anchor>" | <DISPOSITION> | <reason>`. Anchors are verbatim quotes of the filing.

## Findings

§K1 "Producer, verifier, adjudicator and owner are distinct roles." | ADOPTED | Recorded as INSTANCE-FAILURE on the named control generation reviewer-dispatch-start-claim-v1, which Sol designed, implemented and consumed, not on all 1,622 Sol-authored headings. A real governance implementation can be a kernel subject; the reported Luna-implements / Opus-Sonnet-review route for governance work orders establishes that compliance was possible, and the external falsifier key does not cure the producer also adjudicating consumption.
§K2 "A consumed one-time grant never leaves the register" | ROUTED(adobe authority-register lifecycle bench) | FRICTION retained for the `code` profile; the kernel REPLACES is rejected: no second profile reports this defect, and the measured append-only instance mechanism does not establish a domain-wide retirement requirement. No `code.md` row changes. Test an active-register view with durable consumption records and pointers that preserve continuing restrictions and historical authority.
§K3 "after the first terminal receipt" | ROUTED(adobe dispatch-claim bench) | Reclassified INSTANCE-FAILURE → UNEXERCISED for the complete K3 observable: a sequential restart after a terminal receipt does not establish simultaneous claimants, and a claim store refusing a start at initialisation is not itself a breach. Supply the subject-bound holder record, an externally decidable release rule and evidence of an actual violation; durable once-per-dispatch admission may repair the instance without being required by K3.
§K4 "Never exit code, output size or silence." | ADOPTED | Recorded as filed: FIT for the sampled admission refusals and the noncountable duplicate publication. These are positive negative-case evidence; they do not establish that the instance's publication grammar is necessary or efficient.
§K5 "no product subject reached acceptance" | ADOPTED | Reclassified UNEXERCISED → INSTANCE-FAILURE. The instance's own `specs/adobe-ingester.md` (blob `c66c2229`, "MEASURED 2026-09-25") reports that no profile declaration was made for the two product work orders of 2026-09-25 (WO-PROD-PDF-INTAKE-CORE-002, WO-PROD-ADOBE-SESSION-ROUTE-FIRST-003), inside this window: attributed evidence of a pre-work obligation failing, irrespective of later acceptance. The declarations reported on WO-013 through WO-015 are narrower positives and show that declaring before work was possible.
§K6 "Every acceptance includes a key from an independence class" | ADOPTED | Recorded as filed: UNEXERCISED for qualifying acceptance evidence. Reported Anthropic reviews of OpenAI production establish candidate-key diversity, but neither those reviews nor the word CONSUMED supplies a complete acceptance receipt; the instance's two-Claude-report requirement exceeds K6's minimum.
§K7 "Acceptance and delivery are separate states." | ADOPTED | Recorded as filed: UNEXERCISED for a qualifying acceptance-to-delivery transaction. The excluded pre-kernel subject WO-G0-A01 and its empty-hooks-directory workaround earn no end-to-end credit.
§K8 "They never open a gate by themselves." | ADOPTED | Recorded as filed: FIT for the reported quota park and the start hold that continued after capacity resumed. This answers the prior ruling's dormant-terminal INSTANCE-FAILURE for the sampled event without withdrawing that earlier finding.
§K9 "every Sol wake resumes filesystem-first" | ADOPTED | Recorded as filed: FIT, scoped to the attributed durable recovery of interrupted-wake edits and the passing governance-gate receipt. Heading counts alone do not prove every rotation or gating seam, and no prompt-size causal cost is established (see §Untested-3).
§K10 "it records the account it was derived under." | ADOPTED | Recorded as filed: INSTANCE-FAILURE within the disclosed search boundary and the reported absence of the required inventory. Compliance was possible by probing and retaining the current-account inventory before dispatch; ACCOUNT-check headings are parity evidence and cannot substitute for it.
§K11 "Provider and model inventory is machine-scoped and probe-derived." | ADOPTED | Recorded as filed: INSTANCE-FAILURE through the supported R5/K10 failure, for which honest compliance was possible. The computed posture line repairs the prior filing's header defect; 76 correction headings establish neither dishonesty nor a required numerical correction-rate threshold.
§K12 "Each filing also reports product share" | ROUTED(code product-share bench; cross-profile instrument bench) | FRICTION retained as an attributed instrument-cost finding; the kernel REPLACES is rejected: Magic Lantern's P1 is expressly a proposal, previously ROUTED, and dng-auto-processor's ruling candidate is neither a kernel verdict line nor evidence automatically attributable to its measured-objective profile. Obtain measured FRICTION on the same missing instrument from a second distinct profile, or a concrete BREAK; neither a kernel amendment nor a §4 header field is adopted now.
§P:code subject-identity "a key on a different subject identity does not transfer." | ADOPTED | Recorded as filed: FIT for dispatch identity binding (candidate_manifest_sha256, reviewed_commit) and the refusal to reuse WO-014 publications on WO-015. This does not certify eventual delivered identity or upgrade the subjects' declared code@r4 contract.
§P:code resource-terminals "retain the stopped candidate's bytes and receipts before rollback" | ADOPTED | Recorded as filed: FIT for the reported typed stops (TIMEOUT_48H, NO DISPOSITION), zero credit and the retained WO-014 candidate named as WO-015's baseline. No text change follows.
§P:code claims "identifies the live holder rather than a short-lived claim-writing helper." | ROUTED(adobe dispatch-claim bench) | Reclassified INSTANCE-FAILURE → UNEXERCISED: loss of a completed dispatch's in-memory start allowance does not establish that a claim identified the wrong live holder. Provide holder, process and release evidence rather than treating the missing once-only admission record as the quoted profile violation; same bench as §K3.
§P:code independent-key "a CI runner the producer does not control" | ADOPTED | Recorded as filed: UNEXERCISED for the CI alternative. The explicitly unfetched remote-tracking ref is not a fresh remote witness, and no window CI receipt is supplied.
§P:code budgets "plus window counts of subjects accepted, delivered, parked" | ADOPTED | Recorded as filed: FIT for the reported subject-outcome accounting (accepted 0, delivered 0, closed undelivered 2, in review 1) and zero accepted-undelivered work. No end-to-end credit follows from those counts.
§P:code dispatch-preflight "retains its result, the inventory snapshot and digest" | ADOPTED | Recorded as filed: INSTANCE-FAILURE for the missing dispatch-bound current-account inventory. Retained launcher diagnostics are a narrower improvement over the prior ruling's discarded output; retaining the required inventory and parity evidence was possible under the existing rule.

## Carried forward

§CF-K1 "exercised, failed" | ADOPTED | The new named control-generation role failure is recorded under §K1. The prior REJECTED(unexercised) stands for its earlier window.
§CF-K2 "still checked by the reader" | ROUTED(adobe admission-grammar bench) | The prior route remains open: four refusals and two redeliveries do not demonstrate machine-checked staging. This is separate from the new register-retirement proposal in §K2.
§CF-K6 "half resolved." | ROUTED(adobe alternate-key bench) | Retained diagnostics support the reported partial repair, but no exercised alternate qualified backend is supplied. The kernel does not require two reviewer backends; this bench addresses the instance's availability and quorum choices.
§CF-K9 "Wall-interrupted effects were recovered from preserved tree" | ADOPTED | The reported recovery is recorded as evidence supporting the prior instance route. It supplies no basis for the previously proposed universal effect-serialisation obligation.
§CF-K10 "exercised, failed" | ADOPTED | The current INSTANCE-FAILURE is recorded under §K10. The prior rejection on the earlier evidence is not withdrawn.
§CF-K12 "HARVESTED with blob-bound dispositions." | ADOPTED | Recorded as resolved for the prior blob: its dispositions binding is bus-VERIFIED. The new blob reading STALE means its findings await disposition, not that the earlier harvest disappeared.
§CF-P:code-independent-key "unchanged" | ROUTED(adobe alternate-key bench) | The prior route remains open because this window supplies no exercised CI or attended-human alternative. Their impossibility is not inferred from non-use.
§CF-Untested-1 "none accepted" | ROUTED(adobe product-subject bench) | Product activity is now reported (15 work orders in headings, 16 `spikes/` commits), but no qualifying acceptance and delivery closes the route. Continue already-authorised work; manufacture no subject for the census.
§CF-Untested-2 "the window cite directive 2026-09-15d clause 6" | ROUTED(adobe Astra-advisory bench) | The requested measurement remains absent. Eleven ASTRA headings do not answer the prior bench question.
§CF-HEADER "HEADER POSTURE-NOT-R9-COMPUTED" | ADOPTED | The prior posture-format defect is recorded as resolved: the current `posture:` line is accepted by the bus parser as computed-form PARTIAL. This awards no posture role and no cross-family-validation badge.
§CF-K4-CRLF "not re-measured." | ROUTED(adobe CRLF publication-verifier bench) | The earlier ruling is preserved and remediation stays unverified. One mention of the verifier supplies no new result.

## Proposal

§Proposal "Neither is a ruling" | ROUTED(adobe Sol-owned register and auditor-instrument benches) | Both experiments (retiring consumed grants behind a pointer; product share in the auditor's tick) remain instance decisions through the existing authority register. This harvest neither grants implementation authority nor converts either proposal into mandatory profile or kernel text.

## Untested

§Untested-1 "Opus and Sonnet as one independence class." | ROUTED(adobe alternate-key and quorum bench) | Existing §1/K6 text supplies the decision: two Anthropic model names do not establish two independent provider trust domains or two model families, although either may supply the required other-family key against an OpenAI producer. No kernel definitional amendment is established; measure whether the extra instance-required reviewer adds useful coverage before changing that quorum.
§Untested-2 "Control generations as kernel subjects." | ROUTED(adobe control-subject mapping bench) | Real owner-authorised governance implementations fall within the existing subject definition; the named K1 implementation is not exempt merely because it is control work. Map actual units, identities, declarations and acceptance decisions rather than counting 378 headings as 378 subjects; absence of a declaration from headings alone does not prove it exists nowhere else.
§Untested-3 "Wall budget from resume size." | ROUTED(adobe resume-cost bench) | Prompt growth, host contention and wall-budget events co-occur, but the filing explicitly lacks a separating measurement. No K9 FRICTION or causal remedy is established.
§Untested-4 "The bus spec's revision labels" | ROUTED(adobe bus-spec publisher) | Correct the stale summary block (`DOGFOOD-PENDING`, `ADOPT: not recorded`) and the false r4-blob association in Adobe's own `specs/adobe-ingester.md`. Preserve the historical adopted revision (r4 / code@r4) and distinguish it from the current revision reviewed here (r5 / r10).

## Header

HEADER: kernel "fleet-factory-kernel r4" | ADOPTED | Legitimate historical revision reporting: §5 says filings name the revisions they ran, and the bus spec corroborates the attributed r4 / code@r4 adoption. Reading and quoting r5 / r10 does not automatically upgrade the instance or certify conformance to every newer profile requirement.
HEADER: preamble "DOGFOOD-PENDING" | ROUTED(adobe bus-spec publisher) | The summary block and the 2026-09-20 note remain inconsistent with the 2026-09-25 correction that reports adoption. Correct those current-facing statements without erasing the historical record.
HEADER: preamble "the r4 blob is" | ROUTED(adobe bus-spec publisher) | VERIFIED: `6821c4c3390712522b699e72a1781bc9d89a771a` is r5; r4 at `da4e920` is `79fc893cff8a5e1341b874a722a9b8f53db29ff6`. The r4 declaration's association with the r5 blob is a genuine provenance defect in Adobe's spec.
HEADER: provenance "Drafted by the Claude auditor" | ADOPTED | No filing-author defect is established: kernel §4 does not require a governed lane to draft the report, and Adobe's bus spec identifies auditor sessions as its publishers. This provenance supplies neither runtime authority nor acceptance credit.
HEADER: posture "conjugal-standard-PARTIAL (0/17 lanes;" | ADOPTED | The bus parser reports no posture-format flag; the empty-scratch computation and its execution details remain attributed. Informal auditor and falsifier participation does not populate the seventeen standard roles.
HEADER: subjects "0 end-to-end." | ADOPTED | Zero qualifying closures recorded. Neither the excluded pre-kernel work nor a consumed control generation establishes complete kernel acceptance-and-delivery evidence.
HEADER: health "assurance=UNSATISFIED operability=PRESSURED" | ADOPTED | The supported instance failures and the reported blocked product flow support this health pair. The reclassifications above do not turn assurance green.
HEADER: pathology "0 of 225 in the last 72 h" | ADOPTED | Recorded as attributed pathology, not a causal demonstration or an independent census finding. The equal-window product share rose from about 0.16 % (1 of 609) to 1.46 % (16 of 1,093); the last-72-hour zero supports a recent stall, not a decline across those two windows.
