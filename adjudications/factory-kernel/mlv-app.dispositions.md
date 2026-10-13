filing_blob: d39b6f712bf51d2627c8879c1da67ce6fa9a5931
filing_ref:  origin/review/mlv-app-kernel-2026-10-07
spec_commit: a0a1325f9d3543a62a4ca8262d1ea49927e5fa24
harvested_by: conjugal (interim kernel steward), 2026-10-13, automated harvest run 20261013T070405Z-d4564706
arbiter: gpt-6-astra (high) · consolidator: claude-fable-5 · lint: claude-opus-5.5 + gpt-5.6-sol · orchestrator: claude-opus-5-5

# Dispositions for mlv-app's second filing (refile, 2026-10-07; declared kernel r5 / code@r10), adjudicated against specs/fleet-factory-kernel.md r5 (unchanged) and profiles/code.md r10 (now r11)

**Supersedes this file's ruling on blob `db44322efba2a95ecccdbe7b5f5b27e2528429d2`** (run 20260915T060404Z-f14bd764,
spec commit `da4e92019315828ae3504371322ef1473d359aa2`; dispositions commit `6e57b25bda2710258d54642f89f8d34058a4abf0`),
which stands in bus history at that dispositions commit. None of its 41 `§` dispositions or its 3 `HEADER:` lines is
withdrawn: no disposition, routing, rejection, conditional permission or adopted text of that ruling is withdrawn, and
every route it left open stays open. The filing is a rewrite of that HARVESTED 2026-09-14 filing, so it carries no prior
finding forward undisposed. It declares the revisions the instance ran (kernel r5 / code@r10), which are accurate
assessment revisions; it is adjudicated against r5 / r10 and the prospective r11 without that reading rewriting this
window.
Bus-side facts were VERIFIED directly by the arbiter: the filing blob and its ref binding (tip `d53e02a`), the current
specification blobs, the prior dispositions file and the ledger baseline (26 rows); the proposals the filing points to
are read from `specs/mlv-app.md` ("2026-10-07 KERNEL REFILE r5") on the same review branch. MLV-App repository claims —
PR #299's landing chain (head `7712c5b3`, merged `df353652`) and the instance map on fork/master, the S1/S2 PR heads,
trees and merges, the board-local run and key receipts (gitignored on MLV-App), the board ledger lines, the hosted-CI
check-run counts, the quota event and the fold-lag counts — are ATTRIBUTED, UNVERIFIED from the bus, and are
adjudicated as attributed evidence, not as independently reproduced measurements; unavailability is not proof that the
claims are false.

24 `§` lines: 12 clause findings (12 ADOPTED), 4 profile findings (4 ADOPTED), the instance-failures summary and the
sibling-filings note (2 ADOPTED), 3 proposals (3 ROUTED) and 3 Untested readings (3 ROUTED) — 18 ADOPTED ·
0 ADOPTED-CONDITIONAL · 0 REJECTED · 6 ROUTED in all — plus 5 `HEADER:` lines (3 ADOPTED · 2 REJECTED · 0 ROUTED).
Verdict census as filed and as ruled (identical; INSTANCE-FAILURE excluded per kernel §5): **FIT 7 · FRICTION 0 ·
BREAK 0 · N/A 0 · UNEXERCISED 1; separately INSTANCE-FAILURE 8.** Clauses: 5 FIT (K1, K4, K6, K7, K8) · 0 FRICTION ·
0 BREAK · 0 N/A · 1 UNEXERCISED (K9) · 6 INSTANCE-FAILURE (K2, K3, K5, K10, K11, K12). Profile: 2 FIT
(resource-terminals, delivery-target) · 0 FRICTION · 0 BREAK · 0 N/A · 0 UNEXERCISED · 2 INSTANCE-FAILURE
(subject-identity, acceptance-evidence). No reclassification. The filing's seven numbered instance failures are covered
by the K and P lines, including the joint K3/subject-identity item, and are not counted twice. "ADOPTED" on a FIT,
UNEXERCISED or INSTANCE-FAILURE line means recorded as filed within the stated evidence scope, not blanket conformance.
Proposals, Untested readings and headers are outside the census.

Rule: kernel §5, not the owner-bench rule. **What changed: only `code.md`'s Subject identity (K3) opening, r10 → r11
(+18 words, 1,209 → 1,227), adopted in this same harvest on cloudvore's singular code-profile K3 friction; nothing in
this filing contributed to it, and the kernel is unchanged at r5, 2,867 words.** The §5 reason: the filing submits
0 BREAK and 0 FRICTION and none is established; its eight INSTANCE-FAILURE lines count toward health, never toward
conformance or a text change (kernel §4). Its three proposals converge on learning observability within the same
`code` profile as Adobe's K12 findings, but proposals are not FRICTION verdicts; their remainders are routed to the
R14 owner and implementation benches, preserving existing R14.3 and R14.7 rather than rewriting K12. Its proposed
manifest repair (declaring code@r10's path-manifest alternative) is valid only if complete inputs remain untouched,
and a manifest cannot be declared retrospectively; no manifest text changes. Criterion 1: both claimed subjects receive
zero credit — S1 (no pre-work profile declaration or acceptance-contract digest; the required model keys bind a
different tree, without a declared manifest; delivered-commit CI does not discharge the remaining contract) and S2 (the
same disclosed declaration, contract-binding and changed-tree key-transfer failures); both reported deliveries remain
real activity. Closed end-to-end subjects from this filing: 0. Unresolved BREAKs: 0 submitted or established.

Line format: `§<id> "<anchor>" | <DISPOSITION> | <reason>`. Anchors are verbatim quotes of the filing; the
three §Proposals anchors quote the `specs/mlv-app.md` section the filing's "Proposals for the steward" points to.

## Findings

§K1 "the receipts name different actors for production and acceptance" | ADOPTED | Recorded as filed: attributed FIT for actor separation, without certifying private receipts or complete acceptance.
§K2 "Each project keeps one register" | ADOPTED | Recorded as filed: INSTANCE-FAILURE. A prohibited-acts list does not supply the disclosed missing authority register.
§K3 "A subject's identity is a content digest" | ADOPTED | Recorded as filed: INSTANCE-FAILURE. Changed delivered trees and undeclared manifests prevent model-key transfer.
§K4 "Never exit code, output size or silence." | ADOPTED | Recorded as filed: attributed FIT for the work-evidence repair and negative case; the stale map is separately K11.
§K5 "Before work starts, a subject declares its profile" | ADOPTED | Recorded as filed: INSTANCE-FAILURE. The declarations omit required revisions; earlier subjects' profile fields cannot supply them.
§K6 "the independence class of each key" | ADOPTED | Recorded as filed: FIT limited to reported class distinctions. Neither same-family Fable nor hosted location alone proves an independent delivered-subject key.
§K7 "how the project detects an accepted subject that never delivered" | ADOPTED | Recorded as filed: attributed FIT for detection/enqueue behavior; preserve the disclosed absence of typed closure and award no end-to-end credit.
§K8 "Running out of quota means rotating or parking" | ADOPTED | Recorded as filed: attributed FIT for parked Sol work and continued other work without a reset-opened gate.
§K9 "resumes from the project's tree and the bus alone" | ADOPTED | Recorded as filed: UNEXERCISED. Hosted witness code does not prove fresh-host recovery from the board-local resume surface.
§K10 "makes the inventory stale" | ADOPTED | Recorded as filed: INSTANCE-FAILURE. SessionStart alignment does not repair missing current-account inventory provenance.
§K11 "apply to every report a factory makes about itself" | ADOPTED | Recorded as filed: INSTANCE-FAILURE for the stale gap claim; the eventual correction does not erase its duration.
§K12 "Every project that runs the kernel files what happened" | ADOPTED | Recorded as filed: INSTANCE-FAILURE for the reported refile lapse; current publication repairs neither scheduling nor the elapsed window.
§P:code subject-identity "a key on a different subject identity does not transfer" | ADOPTED | Recorded as filed: INSTANCE-FAILURE. The manifest alternative requires complete, stable inputs and cannot be declared retrospectively.
§P:code acceptance-evidence "Before work, bind the acceptance contract by digest" | ADOPTED | Recorded as filed: INSTANCE-FAILURE. Green CI and review prompts do not supply the missing pre-work digest binding.
§P:code resource-terminals "Before dispatch, declare any register-permitted substitution" | ADOPTED | Recorded as filed: FIT for the actual park and reported standing rules. Future substitutions must satisfy authority, quorum and producer independence.
§P:code delivery-target "integration branch via the project's landing path" | ADOPTED | Recorded as filed: attributed FIT for the named target and reported merges; delivery does not establish acceptance.
§IF "acceptance contract not bound by digest." | ADOPTED | Recorded as filed: all seven numbered failures are covered by the K/P lines above, including the joint K3/subject-identity item; do not count them twice.
§Sibling-filings "not read for content in this window" | ADOPTED | Record the disclosed cross-reference scope and corrected Conjugal-harvest citation. A list of sibling refs establishes no convergence.

## Proposals

§Proposals-a "Every trap carries a stable ID" | ROUTED(R14 owner and guard-metadata bench) | Stable legacy IDs and new-card check fields already exist; test the remaining per-consumer Guard mapping and validation.
§Proposals-b "Runnable `probes/<ID>.ps1|py`" | ROUTED(R14 owner and probe-execution bench) | The remainder is execution by doctrine-sync. Reported recurrence in a nonconsumer does not establish that automatic probe execution would prevent it.
§Proposals-c "`ack` records per-entry decisions" | ROUTED(R14 owner and recurrence-scoreboard bench) | R14.3 already carries per-card decisions; preserve R14.7's ack role. Test the proposed recurrence event and guarded-share/rate measurements separately.

## Untested

§Untested-1 "Whether hosted CI at a merge-queue commit" | ROUTED(MLV CI-independence and contract bench) | Code already permits a runner the producer does not control. Establish that condition and exact-subject binding; even a valid CI key cannot replace separately required model reviews.
§Untested-2 "K9 across machine loss." | ROUTED(MLV durable-resume bench) | Retain a fresh-host recovery receipt; no such exercise is supplied.
§Untested-3 "The fold-lag counts in the proposals" | ROUTED(R14 fold-debt measurement bench) | Treat the counts as attributed and underived; `delta_count: 1` measures something different and is already retired as the fold signal.

## Header

HEADER: revisions and instance | ADOPTED | r5/code@r10 are accurate assessment revisions; the PR/map landing chain remains attributed and unverified.
HEADER: subjects | REJECTED(nonqualifying closures) | Replace "2 run end-to-end" with the zero-credit subjects cell in the ledger (0 closed end-to-end; S1 and S2 reported delivered, but undeclared profile, unbound contract and nontransferring model keys); both reported deliveries remain real activity.
HEADER: providers | REJECTED(provenance mismatch) | `claude, codex` exceeds the stated single-Anthropic filing lane and absence of review. Correct using filing-lane sentinel evidence; subject keys do not supply filing provenance.
HEADER: posture | ADOPTED | `no model review` matches the stated filing process; it grants no cross-family validation.
HEADER: health and evidence | ADOPTED | Retain UNSATISFIED/PRESSURED and explicit board-local evidence limits; unavailability is not proof the claims are false.
