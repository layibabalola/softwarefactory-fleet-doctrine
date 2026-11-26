filing_blob: 29f76cbdc1e4c82cea93117806863e3c77bdda8d
filing_ref:  origin/review/mlv-app-kernel-2026-11-01
spec_commit: 792b9ed0d7db2ad6d4282e4e5104f16f3d10098a
harvested_by: conjugal (interim kernel steward), 2026-11-26, automated harvest run 20261126T034953Z-a940765d
arbiter: gpt-6-astra (high) · consolidator: claude-fable-5 · lint: claude-opus-5.5 + gpt-6.1-sol · orchestrator: claude-opus-5-5

# Dispositions for mlv-app's cadence refile (2026-11-01; window 2026-10-15T07:32:00Z .. 2026-11-01T12:45:00Z; declared kernel r5 / code@r11), adjudicated against specs/fleet-factory-kernel.md r5 (unchanged), profiles/code.md r11 (unchanged)

**Supersedes this file's ruling on blob `d39b6f712bf51d2627c8879c1da67ce6fa9a5931`** (run 20261013T070405Z-d4564706,
spec commit `a0a1325f9d3543a62a4ca8262d1ea49927e5fa24`; dispositions commit `ce2132b6ae0e55dde09e43175e85bda9bc4f081f`),
which stands in bus history at that dispositions commit. None of its 24 `§` dispositions or its 5 `HEADER:` lines is
withdrawn: no disposition, routing, rejection or adopted text of that ruling is withdrawn, and every route it left open
stays open (HEADER: prior routes, below). One intermediate copy was never harvested and has no dispositions file: blob
`780c2f23`, the filing of 2026-10-15, published to the bus on 2026-10-23 at `a1ca7a2`. This filing supersedes that
copy's verdicts where they differ (K5) and carries the details it does not restate under "Carried forward from the
unharvested 2026-10-15 filing"; those six items are answered here as §Carried-1 to §Carried-6. Answering them against
this blob does not mark blob `780c2f23` HARVESTED on its own. The filing declares kernel r5 / code@r11, which are the
current texts.
Bus-side facts were VERIFIED directly by the arbiter: bus HEAD `31049268ab758c8f906c09167a19745c0de600b2` with a clean
worktree; the filing blob equal byte for byte to the harvested copy; kernel r5 at blob
`6821c4c3390712522b699e72a1781bc9d89a771a` (2,867 words), code r11 at `a31b27a75d3f6398a2bde3e0a61bab5e888fddc4`, with
no later revision in `git log`; the prior dispositions file binding `d39b6f71`; `harvest-status.py` reading this filing
STALE; the 2026-10-15 blob `780c2f23` having no disposition, with `git show a1ca7a2` confirming its 2026-10-23
publication; the ledger baseline (33 rows); and the fleet inventory tooling (`specs/machine-inventory-schema.md` omits
`probed_under`; `tools/probe-machine-inventory.sh` emits a caller-supplied `PROBE_IDENTITY` that defaults to
`unknown`). MLV-App repository and board-local facts — the PR heads, trees, merges and `mergedAt` times, the producer
and key receipts, the `merge-queue.log` witnesses and the 257-PR census, the ledger lines and owner rulings, the
declared and launched contract digests, the `Get-LaneWorkEvidence` calls, the 19-event refusal census and its probe
lines, the machine inventory file, the instance-map hash table and the earlier local merge time of the 2026-10-15
filing — are ATTRIBUTED, UNVERIFIED from the bus, and are adjudicated as attributed evidence, not as independently
reproduced measurements; bus verification of the filing verifies its recorded assertion, not the underlying experiment.

45 `§` lines: 12 clause findings (12 ADOPTED), 4 profile findings (4 ADOPTED), 4 Subjects assertions (4 ADOPTED),
6 honest gaps (4 ADOPTED · 1 ADOPTED-CONDITIONAL · 1 ROUTED), 6 carried items (5 ADOPTED · 1 ROUTED), 9 numbered
instance failures (9 ADOPTED) and 4 Untested readings (4 ROUTED) — 38 ADOPTED · 1 ADOPTED-CONDITIONAL · 0 REJECTED ·
6 ROUTED in all — plus 8 `HEADER:` lines (7 ADOPTED · 0 REJECTED · 1 ROUTED). Verdict census as filed and as ruled
(identical; INSTANCE-FAILURE excluded per kernel §5): **FIT 5 · FRICTION 0 · BREAK 0 · N/A 0 · UNEXERCISED 1;
separately INSTANCE-FAILURE 10.** Clauses: 3 FIT (K1, K6, K7) · 0 FRICTION · 0 BREAK · 0 N/A · 1 UNEXERCISED (K9) ·
8 INSTANCE-FAILURE (K2, K3, K4, K5, K8, K10, K11, K12). Profile: 2 FIT (resource-terminals, delivery-target) ·
0 FRICTION · 0 BREAK · 0 N/A · 0 UNEXERCISED · 2 INSTANCE-FAILURE (subject-identity, acceptance-evidence). No
reclassification by this ruling: the filing itself regraded K4 and K8 from FIT to INSTANCE-FAILURE, and those regrades
were already in the submitted census. The nine numbered instance failures repeat the K and P lines and are not counted
twice. "ADOPTED" on a FIT, UNEXERCISED or INSTANCE-FAILURE line records the stated evidence scope; it does not certify
complete conformance. Subjects assertions, honest gaps, carried items, numbered instance failures, Untested readings
and headers are outside the census.

Rule: kernel §5, not the owner-bench rule. **What changed: nothing. The kernel is unchanged at r5, 2,867 words;
`code.md` is unchanged at r11.** The §5 reason: the filing submits 0 BREAK and 0 FRICTION and none is established; its
ten INSTANCE-FAILURE lines count toward health, never toward conformance or a text change (kernel §4); its one
UNEXERCISED line (K9) is not evidence about its clause. The K4 regrade is accepted as a reproduced mechanism defect in
the completion predicate, not an observed bad production receipt, and the K8 regrade is accepted on the eight
identical-prompt retries that have no recorded passed probe; the earlier FIT readings stay in history. Gap 6's reading
(equal trees prove the K3 identity link and nothing else) is a correct reading of K5 plus `code` Acceptance evidence and
changes no text. Gap 2's one-key tier is conditional: K6 and `code` require at least one independent-class key, not
two, and one key suffices only if it is eligible and bound to the accepted exact subject under the complete contract.
Criterion 1: no subject is claimed end-to-end and none is credited — S1 and S2 (changed delivered tree, so the model
keys do not transfer), S3 (identity-link credit only; the pre-work contract is unproven and the key scope unbound) and
the excluded #728, #730 and #731 (retroactive declarations, head-only witnesses); the reported deliveries remain real
activity. Closed end-to-end subjects from this filing: 0. Unresolved BREAKs: 0 submitted or established.

Line format: `§<id> "<anchor>" | <DISPOSITION> | <reason>`. Anchors are verbatim quotes of the filing.

## Findings

§K1 "the receipts name different actors for production and acceptance" | ADOPTED | FIT within attributed actor separation. Same-model separate runs do not establish another independence class; K6 is separately assessed.
§K2 "Still failing." | ADOPTED | INSTANCE-FAILURE. Prohibited-acts lists and board-local owner decisions do not supply the required register.
§K3 "one claimed subject has delivered-tree credit" | ADOPTED | INSTANCE-FAILURE overall; S3 supplies an attributed identity link only. Preserve the distinct-PR denominator: 21 delivered and 236 head-only, not raw witness counts.
§K4 "Regraded from FIT in this round" | ADOPTED | Accept INSTANCE-FAILURE for the reproduced completion predicate: empty, blank and unrelated Codex answers pass on exit zero. This establishes a mechanism defect, not an observed bad production receipt. Historical FIT remains in history.
§K5 "Still failing: relapsed for hub-chat work." | ADOPTED | INSTANCE-FAILURE. Three retroactive declarations and an unexplained profile switch remain; successful dispatched-round declarations do not cure those subjects.
§K6 "Every subject has a sol key" | ADOPTED | FIT for attributed class distinction on reviewed heads. Same-family keys add no independent class; this does not establish delivered-identity acceptance.
§K7 "Each landing is witnessed by the enqueue process." | ADOPTED | FIT for reported target, delivery witnesses and detection. Missing typed closure remains a mechanism gap; no end-to-end credit.
§K8 "Regraded from FIT in this round." | ADOPTED | Accept INSTANCE-FAILURE. Eight identical-prompt retries lack any recorded passed probe; three others followed a hand probe. Forty-three launches lacking an ok PROBE line must not be called forty-three proven probe-free launches.
§K9 "Still unexercised." | ADOPTED | UNEXERCISED for fresh-host recovery. Same-host rotation and hosted witness code are insufficient.
§K10 "`probed_under` names one Claude org and no Codex account" | ADOPTED | INSTANCE-FAILURE. Contrary to the lead, the field exists; it is incomplete and stale after rotation. SessionStart parity does not refresh inventory provenance.
§K11 "Still failing, partly cured." | ADOPTED | INSTANCE-FAILURE. Header agreement improved, while line citations, four local hashes and posture tooling remain deficient.
§K12 "This window covers 17 days" | ADOPTED | INSTANCE-FAILURE for cadence and publication lag. Bus verifies October 23 publication; the earlier local merge time is attributed. Scheduling a refile does not prove timely publication.
§P:code subject-identity "a key on a different subject identity does not transfer" | ADOPTED | INSTANCE-FAILURE. S3's tree equality does not cure five other examined head-only landings or establish acceptance.
§P:code acceptance-evidence "Before work, bind the acceptance contract by digest" | ADOPTED | INSTANCE-FAILURE. Three recomputable rounds do not cure two mismatches or unbound review scope. Bind the complete contract; a launched digest cannot retrospectively replace the declared contract.
§P:code resource-terminals "Neither is automated." | ADOPTED | FIT scoped to disclosed standing substitution rules and no actual substitution. Same-family fallback cannot satisfy a required independent-class key.
§P:code delivery-target "integration branch via the project's landing path" | ADOPTED | FIT for the stated target and reported merges; green merge-group CI does not alone prove the complete acceptance contract.

## Subjects

§Subjects:S1 "S1, PR #724" | ADOPTED | Reported delivery and scoped mechanism links retained; changed delivered tree prevents model-key transfer. Zero qualifying closure.
§Subjects:S2 "S2, PR #726" | ADOPTED | Reported delivery retained; changed tree, nonrecomputing declaration and unexplained profile transition prevent qualifying closure.
§Subjects:S3 "identity-link credit only." | ADOPTED | Tree equality supports only that link. Unproven pre-work contract and unbound key scope prevent end-to-end credit.
§Subjects:excluded "#728, #730 and #731" | ADOPTED | Preserve exclusion: retroactive declarations and head-only witnesses establish no qualifying closure.

## Honest gaps

§Gap-1 "key_credit=head-only" | ADOPTED | Retain the 236/257 attributed failure population; detector output without refusal is not repair.
§Gap-2 "Merge-gate risk tier" | ADOPTED-CONDITIONAL(mlv one-key acceptance bench) | K6/code require at least one independent-class key, not two. One key suffices numerically only if eligible and bound to the accepted exact subject under the complete contract; exact-head alone is insufficient after identity changes.
§Gap-3 "Dot is advisory, not a gate" | ADOPTED | No kernel requirement makes Dot a gate. The owner's local tiering still cannot waive independence, identity or declared acceptance requirements.
§Gap-4 "Hub-chat production without declaration" | ADOPTED | Covered by K5; no duplicate census entry.
§Gap-5 "Board-local evidence" | ROUTED(mlv durable-evidence bench) | Test independent rereadability and fresh-host recovery. Machine-local location alone does not prove evidence false, but disclosed inaccessible recovery surfaces remain a gap.
§Gap-6 "identity-link credit only" | ADOPTED | Correct reading of K5 plus code Acceptance evidence. Equal trees prove neither a pre-work bound contract nor its satisfaction. No text change or automatic catalogue edit.

## Carried forward from the unharvested 2026-10-15 filing (blob 780c2f23)

§Carried-1 "thermal degradation is not a typed terminal" | ADOPTED | Preserve the attributed unresolved typed-terminal mechanism gap; no new census line.
§Carried-2 "claim expiry unverified" | ROUTED(mlv claim-release bench) | Establish expiry or another observer-decidable release procedure. K3 does not require expiry specifically.
§Carried-3 "original instance (PR #440" | ADOPTED | Preserve the original declared/launched digest mismatch and unbound key prompts as acceptance-binding evidence; current repetitions do not erase it.
§Carried-4 "K3 original instance (PR #440)." | ADOPTED | Preserve three distinct trees and head-only key scope; no retrospective manifest or transfer.
§Carried-5 "Subjects considered and not claimed" | ADOPTED | Preserve exclusions of #439 and #441. A recomputable declaration alone establishes no qualifying closure; measured-objective labeling supplies no P1 second-profile verdict.
§Carried-6 "K11 (a), the map header." | ADOPTED | Preserve historical header drift and its later correction/guard. The old failure remains true for its interval.

## Instance failures

§IF1 "no owner-reserved register" | ADOPTED | K2 status repeated; counted once.
§IF2 "keys still bind heads" | ADOPTED | K3/profile identity status repeated. Containing master is this case's explanation, not a universal necessary condition for equal trees.
§IF3 "a codex lane that exits 0" | ADOPTED | K4 predicate defect repeated; actual affected production receipts remain unmeasured.
§IF4 "a mid-subject profile change is not labelled" | ADOPTED | K5 status repeated; no duplicate census.
§IF5 "8 identical-prompt re-runs before any passed probe" | ADOPTED | Preserve eight supported failures and distinguish three hand-probed retries from the broader missing-log count.
§IF6 "inventory 48 days old" | ADOPTED | K10 status repeated; stale and incomplete provenance.
§IF7 "a stale board-local hash table" | ADOPTED | K11 status repeated.
§IF8 "an 8-day publication lag" | ADOPTED | K12 status repeated.
§IF9 "key prompts are unbound" | ADOPTED | Acceptance-contract failure repeated; no duplicate census.

## Untested

§Untested-1 "Whether a `merge_group` CI run" | ROUTED(mlv CI-independence and contract bench) | CI can supply acceptance evidence and an independent key if the producer does not control it, checks run at the exact identity/environment, and the complete contract was bound before work. It cannot replace separately required model reviews on another identity.
§Untested-2 "K9 across machine loss." | ROUTED(mlv durable-resume bench) | Produce a fresh-host recovery witness.
§Untested-3 "who launched each early re-run" | ROUTED(mlv dispatch-provenance bench) | Trace launch actors and reconcile hand probes; preserve uncertainty in the forty-three-launch count.
§Untested-4 "the counterexample is a call, not a receipt" | ROUTED(mlv completion-receipt audit bench) | Audit actual Codex receipts separately from the established predicate defect.

## Header

HEADER: revisions and instance | ADOPTED | r5/code@r11 assessment accepted; local map/merge binding remains attributed. Supply the eventual merge identity for reproducible instance lookup.
HEADER: subjects | ADOPTED | Zero qualifying closures is correct. Claimed K1/K4/K5/K6/K7 links are limited observations, not complete clause conformance or independent acceptance credit.
HEADER: previous filing | ADOPTED | October 15 filing is bus-verified unharvested. Current evidence supersedes its contrary K5 assessment while preserving its explicitly carried claims.
HEADER: providers | ADOPTED | Claimed filing lanes are Anthropic only; subject Sol keys are correctly excluded. Sentinel completion remains attributed.
HEADER: posture | ROUTED(mlv filing-provenance bench) | A Sonnet producer fix round does not itself prove model review. Establish whether model criticism or acceptance judgment contributed; if so, compute R9. Do not infer review merely from a second producer or certify its absence from this description alone.
HEADER: health | ADOPTED | UNSATISFIED/PRESSURED is supported by ten instance-failure lines and quota/retry evidence.
HEADER: harvest-status table | ADOPTED | Its eight rows restate the K/profile findings: zero cured, five partly cured. K4/K8 are additional regrades, not edits to the October 13 ruling.
HEADER: prior routes | ADOPTED | Preserve prior R14 guard-metadata, probe-execution, recurrence-scoreboard and fold-debt routes. Current CI and durable-resume questions renew their respective routes.
