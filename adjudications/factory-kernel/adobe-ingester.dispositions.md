filing_blob: b186075d6514493309548f0448bc43f5463dccd7
filing_ref:  origin/review/adobe-ingester-kernel-2026-11-10
spec_commit: 792b9ed0d7db2ad6d4282e4e5104f16f3d10098a
harvested_by: conjugal (interim kernel steward), 2026-11-26, automated harvest run 20261126T034953Z-a940765d
arbiter: gpt-6-astra (high) · consolidator: claude-fable-5 · lint: claude-opus-5.5 + gpt-6.1-sol · orchestrator: claude-opus-5-5

# Dispositions for adobe-ingester's re-run filing (2026-11-10; window 2026-11-09T05:18Z .. 2026-11-10T18:10Z; declared kernel r5 / code@r11; instance: the direct product route, not the parked governed-lane factory), adjudicated against specs/fleet-factory-kernel.md r5 (unchanged), profiles/code.md r11 (unchanged)

**Supersedes this file's ruling on blob `efe2ed91306c5c957612b09b9a1f12e35de12dbf`** (run 20261013T070405Z-d4564706,
spec commit `a0a1325f9d3543a62a4ca8262d1ea49927e5fa24`; dispositions commit `ce2132b6ae0e55dde09e43175e85bda9bc4f081f`),
which stands in bus history at that dispositions commit. None of its 6 `§` dispositions or its 5 `HEADER:` lines is
withdrawn: no disposition, routing, rejection or adopted text of that ruling is withdrawn, and every route it left open
stays open (HEADER: prior routes, below). There is no unharvested intermediate copy: the filing itself reports every
earlier adobe-ingester filing as HARVESTED and carries nothing forward. This blob is a complete K1-K12 census, with six `P:code`
lines (no acceptance-evidence, resource-terminals, claims or dispatch-preflight line), of a different instance. The governed-lane factory is parked (attributed), and the instance measured here is the
direct product route under the attributed owner ruling of 2026-10-24. The change of instance closes no prior route. The
filing declares kernel r5 / code@r11, which are the current texts.
Bus-side facts were VERIFIED directly by the arbiter: bus HEAD `31049268ab758c8f906c09167a19745c0de600b2` with a clean
worktree; the filing blob equal byte for byte to the harvested copy; kernel r5 at blob
`6821c4c3390712522b699e72a1781bc9d89a771a` (2,867 words), code r11 at `a31b27a75d3f6398a2bde3e0a61bab5e888fddc4`, with
no later revision in `git log`; the prior dispositions file binding `efe2ed91`; `harvest-status.py` reading this filing
STALE; the ledger baseline (33 rows); RECEIPTS calling governance-motion a candidate invariant; Magic Lantern §SP1
remaining ROUTED, so it is not a hardware-in-loop verdict on this filing's P1; and the fleet inventory tooling
(`specs/machine-inventory-schema.md` omits `probed_under`; `tools/probe-machine-inventory.sh` emits a caller-supplied
`PROBE_IDENTITY` that defaults to `unknown`). Adobe repository and machine-local facts — the three PRs, their heads,
merges and tree identities, the TRX receipts and mutants, the Codex falsifier transcripts, the owner ruling of
2026-10-24, the handoff lease and rotation records, the park record, the process and CPU samples, the publication times
on the PR threads, the `nomotion` counts and the root-cause note — are ATTRIBUTED, UNVERIFIED from the bus, and are
adjudicated as attributed evidence, not as independently reproduced measurements; bus verification of the filing
verifies its recorded assertion, not the underlying experiment.

24 `§` lines: 3 Subjects assertions (3 ADOPTED), 12 clause findings (11 ADOPTED · 1 REJECTED), 6 profile findings
(6 ADOPTED), 1 proposal (1 ROUTED) and 2 Untested readings (2 ROUTED) — 20 ADOPTED · 0 ADOPTED-CONDITIONAL ·
1 REJECTED · 3 ROUTED in all — plus 6 `HEADER:` lines (4 ADOPTED · 2 REJECTED · 0 ROUTED). Verdict census
(INSTANCE-FAILURE excluded per kernel §5), as filed: **FIT 9 · FRICTION 1 · BREAK 0 · N/A 0 · UNEXERCISED 0; separately
INSTANCE-FAILURE 8.** As ruled: **FIT 9 · FRICTION 0 · BREAK 0 · N/A 0 · UNEXERCISED 0; separately
INSTANCE-FAILURE 9.** One reclassification: K2, filed FRICTION, is ruled INSTANCE-FAILURE. Clauses as ruled: 5 FIT (K3,
K4, K6, K7, K8) · 0 FRICTION · 0 BREAK · 0 N/A · 0 UNEXERCISED · 7 INSTANCE-FAILURE (K1, K2, K5, K9, K10, K11, K12).
Profile as ruled: 4 FIT (subject-identity, independent-key, delivery-target, budgets) · 0 FRICTION · 0 BREAK · 0 N/A ·
0 UNEXERCISED · 2 INSTANCE-FAILURE (determinism-class, human-gates). "ADOPTED" on a FIT or INSTANCE-FAILURE line
records the stated evidence scope; it does not certify complete conformance. The proposal (P1, labelled FRICTION by the
filing), the Subjects assertions, the Untested readings and the headers are outside the census.

Rule: kernel §5, not the owner-bench rule. **What changed: nothing. The kernel is unchanged at r5, 2,867 words;
`code.md` is unchanged at r11.** The §5 reason: no concrete BREAK and no two-profile FRICTION establishes an amendment.
The filing's one FRICTION line, K2, is reclassified: the required register was unavailable from the product checkout,
and `code` Human gates already requires reachability, so this is an instance failure against existing text, not friction
with it. The proposed K2 REPLACES (a register "inside every repository its instance writes to") is not adopted: a copy in
every repository is unnecessary and fails §3's universality test, and an accessible authoritative sibling register can
suffice. P1 names a possibly missing repair-path requirement, but its unconditional escape and unspecified K have no
tested, authority-preserving mechanism and no second-profile verdict, so it is routed to a `code` bounded-gate-repair
bench and no text is adopted. The nine INSTANCE-FAILURE lines count toward health, never toward conformance or a text
change (kernel §4). Criterion 1: the three reported deliveries (PR #31, #32, #33) are retained as reported deliveries
and receive zero end-to-end credit, because the producer also decided acceptance (K1) and no profile or acceptance
contract was bound before work (K5). Closed end-to-end subjects from this filing: 0. Unresolved BREAKs: 0 submitted or
established.

Line format: `§<id> "<anchor>" | <DISPOSITION> | <reason>`. Anchors are verbatim quotes of the filing.

## Subjects

§Subjects:31 "PR #31" | ADOPTED | Reported delivery retained; zero qualifying closure because production/acceptance separation and pre-work acceptance binding failed.
§Subjects:32 "PR #32" | ADOPTED | Same scope: reported delivery, not qualifying kernel acceptance or closure.
§Subjects:33 "PR #33" | ADOPTED | Same scope. Tree equality and a Codex key do not cure K1 or K5.

## Findings

§K1 "Session af70e674 was both producer and adjudicator" | ADOPTED | INSTANCE-FAILURE. Codex supplies another evidence author, satisfying that limb; the producer also decided acceptance. Agent-landing authority does not waive role separation.
§K2 "So for this instance the register is a memory note." | REJECTED(FRICTION classification; reclassify INSTANCE-FAILURE) | The required register was unavailable from the product checkout. Code Human gates already requires reachability. Requiring a copy inside every repository is unnecessary and fails §3's universality test; an accessible authoritative sibling register can suffice.
§K3 "Each delivered tree equals its reviewed head tree" | ADOPTED | FIT for attributed identity equality and expiring claim. Prefixes are locators; retain full digests and the recomputation witness. No acceptance credit follows.
§K4 "Never exit code, output size or silence." | ADOPTED | FIT for refusing missing TRX and failed-suite evidence. Subsequent re-gating does not cure the separate determinism declaration failure.
§K5 "No subject recorded a profile line" | ADOPTED | INSTANCE-FAILURE. Profile and contract must bind before work starts; adding them merely before the first gate is insufficient if production already began.
§K6 "Key class: openai." | ADOPTED | FIT limited to attributed producer/key class distinction. Printed model/provider provenance is relevant; the filing's zero-role R9 result measures a different claim.
§K7 "Acceptance and delivery are separate states." | ADOPTED | FIT for the reported pinned landing transaction and open-PR detection. Does not turn deficient acceptance into qualifying closure.
§K8 "nothing in flight" | ADOPTED | FIT for the described park, lease transfer and resumed work. Retain the 4.7-hour cost as operability evidence.
§K9 "All three are Git-excluded and machine-local" | ADOPTED | INSTANCE-FAILURE. A tracked bootstrap pointer and independently recoverable artifacts are needed; same-machine rotation survival is insufficient.
§K10 "No inventory file records `probed_under`" | ADOPTED | INSTANCE-FAILURE. Parity output is not a current account-bound capability inventory. Route implementation evidence to fleet inventory tooling and Adobe dispatch maintainers.
§K11 "13 h and 11 h after the merges" | ADOPTED | INSTANCE-FAILURE within the disclosed publication delays and inaccurate reporting. Computed posture does not cure those defects.
§K12 "this one comes 30 days later" | ADOPTED | INSTANCE-FAILURE for missed filing cadence and instance-change seam. Steward nonresponse is a separate failure, not an excuse or favourable steward grade.
§P:code subject-identity "3 of 3 delivered trees equal the reviewed head trees" | ADOPTED | FIT for the attributed identity link only.
§P:code determinism-class "not by a per-test declaration" | ADOPTED | INSTANCE-FAILURE. Control runs and re-gating do not supply the required per-test declaration. Host contention remains an untested cause.
§P:code independent-key "Codex/openai never wrote product bytes in these subjects" | ADOPTED | FIT within attributed contribution provenance; no blanket independence certification beyond these subjects.
§P:code human-gates "the register is reachable from every session checkout" | ADOPTED | INSTANCE-FAILURE, corroborating K2. Reachability is required; physical duplication in every repository is not.
§P:code delivery-target "squash merges to `main`" | ADOPTED | FIT for the stated target and landing path.
§P:code budgets "full Debug 511 s, full Release 443 s" | ADOPTED | FIT for the reported timing and call measurements, not an efficiency or acceptance finding.

## Proposal

§P1 "A fail-closed gate blocked its own repair, repeatedly." | ROUTED(code bounded-gate-repair bench) | Test a register-authorized repair actor, bounded scope, rollback, retained evidence and repetition-triggered escalation. Existing text does not explicitly guarantee such a path. No second-profile verdict exists; an unconditional gate bypass and unspecified K are not adopted.

## Untested

§Untested-1 "Contention as the flake's cause." | ROUTED(adobe flake-causality bench) | Instrument the actual purge-failure branch and compare controlled load conditions; CPU samples establish no cause.
§Untested-2 "Dedicated machines." | ROUTED(adobe dedicated-host comparison bench) | Measure capacity, account isolation and flake rates after migration against a stated baseline.

## Header

HEADER: revisions and instance | ADOPTED | Assess the direct product route against r5/code@r11; retain the parked factory as historical proposal evidence.
HEADER: subjects | REJECTED(unqualified acceptance wording) | Three reported deliveries, zero qualifying end-to-end subjects. K1 and K5 prevent kernel acceptance credit.
HEADER: providers | REJECTED(subject provenance substituted for filing provenance) | The named Anthropic/OpenAI lanes worked on subjects. The filing names a chat drafter and no filing falsifier; its supported sentinel-complete filing-provider census is none.
HEADER: posture | ADOPTED | Retain the attributed computed zero-role PARTIAL/NO-CROSS-FAMILY-VALIDATION result. It establishes no model review of this filing and no subject-wide assurance.
HEADER: health | ADOPTED | UNSATISFIED/PRESSURED is supported by the admitted failures, quota hold and parked instance.
HEADER: prior routes | ADOPTED | HARVESTED means answered, not resolved. Preserve prior stall-outcome, product-share, R14 adoption-observability, headless-fold and implementation routes; the instance change closes none automatically.
