filing_blob: 76169ed0f7542028ce3c448d87eb55b2358ca166
filing_ref:  origin/master
spec_commit: 8841d9befaa50905cd36f92b187b6c07914ff6c0
harvested_by: conjugal (subject owner), Round F5, 2026-09-21, Bachelor / Dell XPS 17
arbiter: gpt-6-astra (high) · consolidator: claude-fable-5 · lint: claude-opus-5 + gpt-5.6-sol · orchestrator: claude-opus-5

# Dispositions for DropBox-Vault's filing on specs/conjugal-approach-a-v7.4.md (spec body v7.8, unchanged by this round)

26 findings: 5 ADOPTED · 2 ADOPTED-CONDITIONAL · 18 REJECTED · 1 ROUTED.
Single writer: Conjugal. Line format: `<id> §<sec> "<anchor>" | <DISPOSITION> | <what changed, or why not>`.
A REJECTED finding with a counterexample is an answer, not a dismissal. Re-file with new bench evidence and it will be read again.

## Why this filing was re-read, and what F5 actually decided

This copy turned STALE under `harvest-status.py` because the blob changed, not because the review did. Measured here:
`git diff d690311f 76169ed0` is **two lines**, and the only change on each is the owner's Windows profile name replaced by
`redacted-user` (bus commit `dc9909f`, "Law 4: redact private identifiers"). All **26 finding lines are present verbatim**
(modulo that redaction) in the 39-finding `49336b90` copy harvested in Round F1, in the same order — checked line-by-line,
0 of 26 unmatched. They are exactly the `F1.c.1`–`F1.c.26` set, whose F1 rulings are retained below.

So F5 adjudicated the two questions a re-read at a later spec version does raise, and nothing else:

1. **Do the F1 rulings still hold at v7.8?** The subject moved v7.5 → v7.6 (F2) → v7.7 (F3) → v7.8 (F4), and the Tier 0 loop
   was moved out of the design into `docs/architecture/approach-a/TIER-0.md` on 2026-09-14. 25 of 26 rulings carry forward.
   **One changes: `d.16` is upgraded REJECTED → ADOPTED** — F1 answered only the missing pre-build installer, but F4 `a.24`
   separately adopted the registration-authority defect this finding names, so the filer is owed the credit.
2. **Did the F1 adoptions survive three consolidations?** All six were re-greped and quoted in v7.8 by the arbiter and
   independently re-found in the design fragments by the consolidator: **no regression** (`f5-astra-arbitrate.md`
   §Regression check; `f5-fable-consolidate-report.md`). The superseded wording is genuinely gone — no `P_par=4`, no
   `.git`-directory mutex identity, no per-`receipt_seq` ref, no master-tip CAS.

**The spec is unchanged by this round and stays at v7.8, 12,674 words.** Arbiter: `NO-CHANGE`. Consolidator: `CONFIRMED
NO-CHANGE`, fragments rebuild byte-identical. An empty round that bumped the version would put a fold in the lineage
sentence that never happened; F5 does not do that.

Anchor survival re-greped against v7.8 (`f5-anchor-check.txt`, 26 findings × 2 anchors): 28 HIT, 24 MISS, spread over 15
findings. A MISS is not a defect here — findings 8, 16, 20, 21 and 24 name text that F1 and F4 deliberately replaced,
finding 25 the sentence F3 deleted (see `d.25`, whose rule survives in §3 and Scenarios 23/40b), findings 9 and 17 text
that now lives in `TIER-0.md`, finding 12 a phrasing (`Its source of truth is fresh HEAD:…`) the design never used, and
findings 6, 10, 11, 13, 18 and 22 a single reworded anchor whose rule survives in the cited section.

## Header

- HEADER: no `subject_blob:` line. Filers have owed one since F4 `a.1`, so that harvest can re-grep every `REPLACES` anchor
  against the blob actually reviewed. F5 re-greped against the current v7.8 body instead and reports the result above. This
  is a redaction-only copy of a 2026-09-13 review; do not relabel it as a fresh review of v7.8.
- HEADER: no `posture:` line at all. There is nothing to check against R9's computed form. An honest `posture: none` naming
  the tool that did not run is what R9 asks for; three sentinel-complete designer lanes are not a posture.
- HEADER: `providers: claude-only` is supported by the provenance — three `claude-opus-5` designer lanes on disjoint slices,
  zero Codex lanes, no arbiter, no consolidator, no classifier, `rubric_id: unscored`. Weighed as one family's opinion.
  **A re-read earns no new convergence.** The convergence this project did supply (reducer mutex, master-CAS) was banked in
  F1 against its cross-family sibling copy and against magic-lantern; it is not re-credited here.
- HEADER: finding 8's `P_par` anchor is in §10, not the §1 it was filed under (unchanged from F1).
- SUPERSEDED COPIES: `49336b90` (`origin/review/DropBox-Vault-2026-09-13`, 39 findings, harvested in F1) and `d690311f`.

## Findings

d.1 §9 "within a forecast `5 h (clock_domain=real)` allowance" | REJECTED | The allowance already extends; §9 continues collection after expiry and F3 added a failed-forecast record with separate extension exposure. Cloudvore's legacy DONE frequency is not an Oracle M1 measurement. [F1.c.1 unchanged]
d.2 §9 "calendar exposure of `336 h (clock_domain=real)`" | REJECTED | §9 invalidates qualification on a configuration change, not on any commit; an unrelated documentation commit can leave the measured configuration digest unchanged. Shortening qualification stays unsupported. [F1.c.2 unchanged]
d.3 §10 "Phase 2 is B63" | REJECTED | §10 retains the 336 h baseline exposure and §11 defines B63 across levels, recalculated when b changes; the replacement wrongly folds the baseline into Phase 2. [F1.c.3 unchanged]
d.4 §9 "first receiving an authorized ADOPTED record" | REJECTED | §4 delivers the authenticated exact candidate through its adopted ref, so master reachability is a different acceptance contract; mirror contention cannot invalidate it. Legacy DONE/landed counters do not demonstrate a miscounted Oracle adoption. [F1.c.4 unchanged, C4]
d.5 §9 "targets `2×/3×/5×`" | REJECTED | §9 already measures shared-checkout mutation capacity and requires qualified confidence bounds; a failed target earns no scale claim. Commit counts do not measure resource capacity. [F1.c.5 unchanged]
d.6 §10 "Remaining components are estimated from the completed slice" | ADOPTED-CONDITIONAL(bench lacking recorded build-effort evidence) | §10 carries the conditional upfront component effort ranges and the later re-estimation. Re-measured 2026-09-21: `git ls-files metrics/` on Conjugal still returns 0 tracked files, so the condition holds on this bench too. [F1.c.6 unchanged]
d.7 §9 "provisional or zero b plans" | REJECTED | §9's 48 h absolute-rate branch is intentional, and nine executors still require a qualified five-executor 2× result, so the floor cannot issue an unsupported unlock. [F1.c.7 unchanged]
d.8 §10 "P_par=4 (provisional)" | ADOPTED | Landed in v7.5 and verified still present in v7.8: `P_par` is bench-qualified, default 1, respecting measured host and thermal admission limits, and Scenario 27 uses the admitted value. No four-clone default was reinstated. [F1.c.8 unchanged]
d.9 §12 "plans are forecasts" | ROUTED(receipt-instrumented Tier-0 provider-quota bench) | The target moved out of the design into `TIER-0.md` on 2026-09-14, which still labels provider usage unmeasured. Token plans alone cannot establish provider-window or calendar feasibility. [F1.c.9 unchanged]
d.10 §5 "extends `coordination/tools/check-cli-auth.py --json`" | REJECTED | DIVERGENT, and Conjugal's bench wins on a measurement: `git cat-file -e HEAD:coordination/tools/check-cli-auth.py` exits 0 here (re-measured 2026-09-21). §5 expressly yields UNKNOWN until the adapter ships. [F1.c.10 unchanged, C10]
d.11 §5 "`credit`" | REJECTED | §5 requires compatible authenticated units. Overlapping five-hour and seven-day rounded percentages establish neither a conservative remaining bound nor an additive per-role cost ledger. [F1.c.11 unchanged]
d.12 §5 "`HEAD:coordination/comms/opus.md`" | REJECTED | DIVERGENT: `git cat-file -e HEAD:coordination/comms/opus.md` exits 0 on Conjugal (re-measured 2026-09-21). The mailbox missing on Cloudvore does not establish a defect here, and this design does not declare that path portable. [F1.c.12 unchanged, C10]
d.13 §0 "Families and eligibility are defined once" | REJECTED | §0 names Conjugal as the target bench and §3 records WAIT-COMMITTEE when seats are unavailable, so a role name is never read as proof of live capacity. Cloudvore's session-only doctrine does not invalidate Conjugal's named-role and floor contract. [F1.c.13 unchanged]
d.14 §7 "a never-firing floor" | REJECTED | The bound is expressly conditional: §7 points at §13, whose third residual makes zero-executor supervision unbounded exactly when scheduled floors never fire. The finding's case is the one the text already names. [F1.c.14 unchanged, C6]
d.15 §14 "rebuilt by `tools/build_single.py`" | REJECTED | DIVERGENT: `git cat-file -e HEAD:docs/architecture/approach-a/tools/build_single.py` exits 0 on Conjugal (re-measured 2026-09-21), and §10/Scenario 27 retain the manifest-tool requirement. Planned tools absent on another bench do not invalidate this build contract. [F1.c.15 unchanged, C10]
d.16 §4 "floors hold task-start permission only" | ADOPTED | **Changed from F1's REJECTED.** F1 answered only the missing pre-build installer. The defect this finding names — nobody is named as the authority that provisions the four custody principals and tasks — was separately adopted in F4 `a.24`, and v7.8 §4 now reads "registered only by an owner-installed change verified against its §6 enrollment before activation; lanes and floors never register, enable or edit it". Credited retrospectively; no text changes and no installer filename is added. [F1.c.16 upgraded]
d.17 §12 "never on score alone" | REJECTED | The stopping rule lives in `TIER-0.md` and is preserved there; v7.8 §12 separates design production from the factory, and §5 admits owner-authorized eligible subjects. Tier-0 dormancy neither stops authorized product work nor authorizes manufacturing backlog. [F1.c.17 unchanged, C8]
d.18 §3 "REAFFIRM {proof_id,candidate_digest,committee_epoch,assignment_digest}" | ADOPTED | Landed in v7.5 and verified still present in v7.8: §3's carry-over enumeration includes "a retained voter's missing current-epoch REAFFIRM requested through V_REQUEST", re-dispatched after reassignment, resumption or reducer recovery; Scenario 51 retains the fixture. [F1.c.18 unchanged]
d.19 §7 "Private keys reside under" | ADOPTED-CONDITIONAL(shared-SID lane signing) | Landed in v7.5 and verified still present in v7.8: where families share runner SIDs, signing requires family-isolated custody denying other-family key reads and signing requests, else cross-family signing is unavailable and never inferred from distinct keys; Scenario 65 keeps the negative checks. [F1.c.19 unchanged]
d.20 §4 "floors hold task-start permission only" | REJECTED | Administrators membership alone proves neither an elevated token nor access to protected helper resources — re-measured 2026-09-21, this runner is at Medium integrity with Administrators deny-only — and §4 still forbids floor task-edit, binary-write and key access. [F1.c.20 unchanged, C7]
d.21 §7 "Reducer mutex identity is the `.git` directory file identity" | ADOPTED | Landed in v7.5 and verified still present in v7.8: identity is the file identity of the absolute, handle-resolved `git rev-parse --git-common-dir`. Re-measured 2026-09-21: Conjugal now has **16** worktrees (14 at F4), all resolving to one common dir, so the fix still covers the bench. The blanket linked-worktree refusal stays unadopted — aliases can safely contend for one mutex. [F1.c.21 unchanged]
d.22 §0 "one emergency key per family" | REJECTED | §6 and Scenario 56 keep per-family emergency substitution deliberately: a live-keyholder minimum could prohibit exactly the revocation needed to recover. [F1.c.22 unchanged, C11]
d.23 §5 "extends `coordination/tools/check-cli-auth.py --json`" | REJECTED | DIVERGENT: the checker exists at Conjugal HEAD. §5 requires a changed account fingerprint plus an authenticated successful probe, and preserves UNKNOWN where extraction is unsupported — so unsupported evidence already fails to verify rotation rather than falsely passing it. [F1.c.23 unchanged, C10]
d.24 §5 "CAS on master's expected tip" | ADOPTED | Landed in v7.5 and verified still present in v7.8: staging is a private-index CAS on the non-checked-out `refs/oracle/mailbox`, seeded from master, delivered by authorized normal-index landing and verified in master; §1 keeps the separate `refs/oracle/mirror`. Nothing in v7.8 authorises advancing master's checked-out tip. [F1.c.24 unchanged]
d.25 §0 "no third quorum family exists." | REJECTED | F3 deleted that sentence, but the rule it stated survives: §3 retains opposite-family V seats and cross-family A checks, and Scenarios 23/40b still forbid family substitution. Local same-family approval cannot satisfy those signature predicates. [F1.c.25 unchanged, C11]
d.26 §6 "substitutes for its own family's unavailable signer" | REJECTED | Dual emergency revocation is intentional recovery authority — §6 and Scenario 56 require the emergency pair to succeed — and §7 still places shared-administrator compromise outside the independence guarantee. [F1.c.26 unchanged, C11]

## Round F1 record, retained (prior filing_blob 49336b90a78e73171cab7ba279d8bbfbd4102030 @ origin/review/DropBox-Vault-2026-09-13)

That copy carried 39 findings: the 26 above plus 13 cross-family findings produced with Codex lanes. Its rulings —
12 ADOPTED · 3 ADOPTED-CONDITIONAL · 22 REJECTED · 2 ROUTED, spec_commit `f3043cca` — are kept here so the filer can still
read the answer to every line it filed. They are superseded only where F5 says so above (`d.16`).

- HEADER (F1): `posture: conjugal-standard` named a posture that ran 5 of 17 lanes; R9.5 asks for `conjugal-standard-PARTIAL (5/17 lanes; …)` or a re-run. Harvested at the weight the provenance supported.
- HEADER (F1): the cross-family claim stood under R3 (2 Claude + 3 Codex lanes cleared the sentinel). The kept-verbatim claude-only set was weighed as one family's opinion, and its repeats of the cross-family findings were not counted as independent convergence.
- Clusters, from Astra's F1 arbitration (`docs/architecture/approach-a/rounds/f1-astra-arbitrate.md`): C1 relay/mirror commits — convergent defect, divergent fixes, the non-checked-out ref wins. C2 mutex/journal identity — convergent. C3 replay is not acceptance — convergent. C4–C7, C9–C11 — divergent, Conjugal's bench and contract win. C8 zero-eligible input — adopted; the calendar-hour estimand is kept. C12 receipts head — adopted for the files backend, growth routed. C13 P_par — bench-qualified.

### cross-family findings (F1)

F1.x.1 §5 "CAS on master's expected tip" | ADOPTED | convergent (DropBox Vault x2, magic-lantern). Winner: stage on non-checked-out refs/oracle/mailbox + refs/oracle/mirror, deliver by authorized normal-index landing, acknowledge only on the marker in master. Advancing the checked-out branch (the symbolic-HEAD CAS) loses: the index keeps the old blob
F1.x.2 §1 "readers use `git show refs/oracle/state:<path>`" | ADOPTED | GIT_NO_REPLACE_OBJECTS=1 on every Oracle git call; Scenario 54 extended. Conditional on replacement refs being possible (Conjugal has none today) (Astra scoped this conditionally; the consolidated v7.5 text is host-independent, so it is recorded ADOPTED — this bench is the evidence, and the rule is inert or safe where the condition is absent)
F1.x.3 §1 "One `oracle-reduce.py` instance per checkout" | ADOPTED | convergent (DropBox Vault x2, magic-lantern; Conjugal has 14 worktrees, one common dir). Mutex = file identity of git-common-dir; journals and lane mutex under it. Blanket linked-worktree refusal not adopted: aliases can safely contend for one mutex
F1.x.4 §1 "`coordination/oracle/journal/<lane>.ndjson`" | ADOPTED | convergent (DropBox Vault x2, magic-lantern; Conjugal has 14 worktrees, one common dir). Mutex = file identity of git-common-dir; journals and lane mutex under it. Blanket linked-worktree refusal not adopted: aliases can safely contend for one mutex
F1.x.5 §1 "durable git blob storage" | ADOPTED | core.fsync=loose-object,pack,reference + fsyncMethod verified before acknowledgment; Scenario 61 extended. Conjugal also has core.fsync unset (measured)
F1.x.6 §2 "receipt commits at `refs/oracle/receipts/<receipt_seq>`" | ADOPTED-CONDITIONAL(files-backend sustained receipt publication) | single parent-chained CAS head refs/oracle/receipts replaces one ref per receipt; bounds ref cardinality, not history. Growth and latency ROUTED to Stage S / Scenario 20
F1.x.7 §4 "signing ADOPT_REQUEST only after its own independent replay agrees" | ADOPTED | convergent (DropBox Vault, magic-lantern). ADOPT_REQUEST needs replay AND independently executed/authenticated runs required by the pinned acceptance spec, receipts bound in; a bench-specific run count (e.g. 3x green) is not hard-coded
F1.x.8 §4 "at the exact candidate commit" | REJECTED | Conjugal defines delivery through authenticated adopted refs; master reachability is a different acceptance contract. [C4]
F1.x.9 §10 "P_par=4 (provisional)" | ADOPTED | same project twice, not independent convergence. P_par becomes bench-qualified, default 1, respecting measured host/thermal admission; Conjugal's own admissible concurrency not yet measured (Astra scoped this conditionally; the consolidated v7.5 text is host-independent, so it is recorded ADOPTED — this bench is the evidence, and the rule is inert or safe where the condition is absent)
F1.x.10 §11 "depths 1 and 2 at the same derived P_pub" | REJECTED | Four hours are per level across crossover depths, not four hours per depth. [C9]
F1.x.11 §0/§4 "Tier 2 verifies and attests without writing Oracle state" | REJECTED | Helper evidence publication does not apply authoritative state transitions; the reducer does. [C5]
F1.x.12 §2/§3 "The sidecar refuses renewal at H" | ADOPTED | reclaim becomes oracle_now >= claimed_at + H; Scenario 24 pins the boundary

### Untested (F1)

F1.u.1 §2 "`refs/oracle/claim/<S>`" | ROUTED | Windows files-and-packed-ref subject-ID fixture

### prior claude-only set (F1 rulings on the same 26 findings re-read above as d.1–d.26)

F1.c.1 §9 "within a forecast `5 h (clock_domain=real)` allowance" | REJECTED | The allowance already extends; legacy DONE frequency is not an Oracle M1 measurement.
F1.c.2 §9 "calendar exposure of `336 h (clock_domain=real)`" | REJECTED | Document commits do not establish configuration-digest changes; shortening qualification is unsupported.
F1.c.3 §10 "Phase 2 is B63" | REJECTED | Baseline plus B63 supplies observation duration; the replacement incorrectly includes baseline inside Phase 2.
F1.c.4 §9 "first receiving an authorized ADOPTED record" | REJECTED | Legacy DONE and landed counters do not demonstrate incorrectly counted Oracle adoptions. [C4]
F1.c.5 §9 "targets `2x/3x/5x`" | REJECTED | Commit counts do not measure resource capacity; proposed lower targets lack qualification evidence.
F1.c.6 §10 "Remaining components are estimated from the completed slice" | ADOPTED-CONDITIONAL(bench lacking recorded build-effort evidence) | on a bench without recorded build-effort evidence, 1a and 1b-build carry upfront component effort ranges
F1.c.7 §9 "provisional or zero b plans" | REJECTED | Absolute-rate observation is intentional; the qualified five-executor result already gates nine executors.
F1.c.8 §10 "P_par=4 (provisional)" | ADOPTED | same project twice, not independent convergence. P_par becomes bench-qualified, default 1, respecting measured host/thermal admission; Conjugal's own admissible concurrency not yet measured (Astra scoped this conditionally; the consolidated v7.5 text is host-independent, so it is recorded ADOPTED — this bench is the evidence, and the rule is inert or safe where the condition is absent)
F1.c.9 §12 "plans are forecasts" | ROUTED | receipt-instrumented Tier-0 provider-quota bench
F1.c.10 §5 "extends `coordination/tools/check-cli-auth.py --json`" | REJECTED | Conjugal's named tool exists; its schema extension is explicitly planned. [C10]
F1.c.11 §5 "`credit`" | REJECTED | Rounded usage percentages establish neither conservative remaining bounds nor additive per-role costs.
F1.c.12 §5 "`HEAD:coordination/comms/opus.md`" | REJECTED | The mailbox exists in Conjugal; this specification does not declare that path portable. [C10]
F1.c.13 §0 "Families and eligibility are defined once" | REJECTED | Cloudvore's session-only doctrine does not invalidate Conjugal's named-role and floor contract.
F1.c.14 §7 "a never-firing floor" | REJECTED | The bound expressly excludes never-firing floors and names the unbounded residual. [C6]
F1.c.15 §14 "rebuilt by `tools/build_single.py`" | REJECTED | Conjugal's builder exists; absent planned implementation tools on another bench do not invalidate the design. [C10]
F1.c.16 §4 "floors hold task-start permission only" | REJECTED | Phases 1b and 1b-build establish custody; a missing pre-build installer is not a missing acceptance requirement. [C7] — **superseded by d.16 (ADOPTED) in Round F5**
F1.c.17 §12 "never on score alone" | REJECTED | Tier-0 dormancy governs design iteration; it neither forbids authorized product work nor authorizes manufacturing backlog. [C8]
F1.c.18 §3 "REAFFIRM {proof_id,candidate_digest,committee_epoch,assignment_digest}" | ADOPTED | missing current-epoch REAFFIRM from a retained voter is added to the §3 carry-over enumeration and dispatched via V_REQUEST; Scenario 51
F1.c.19 §7 "Private keys reside under" | ADOPTED-CONDITIONAL(shared-SID lane signing) |
F1.c.20 §4 "floors hold task-start permission only" | REJECTED | Administrators membership alone proves neither an elevated token nor access to protected helper resources. [C7]
F1.c.21 §7 "Reducer mutex identity is the `.git` directory file identity" | ADOPTED | convergent (DropBox Vault x2, magic-lantern; Conjugal has 14 worktrees, one common dir). Mutex = file identity of git-common-dir; journals and lane mutex under it. Blanket linked-worktree refusal not adopted: aliases can safely contend for one mutex
F1.c.22 §0 "one emergency key per family" | REJECTED | Emergency fallback is intentional; a live-keyholder minimum could prohibit necessary revocation. [C11]
F1.c.23 §5 "extends `coordination/tools/check-cli-auth.py --json`" | REJECTED | The Conjugal path exists; unsupported account evidence already yields UNKNOWN and cannot verify rotation. [C10]
F1.c.24 §5 "CAS on master's expected tip" | ADOPTED | convergent (DropBox Vault x2, magic-lantern). Winner: stage on non-checked-out refs/oracle/mailbox + refs/oracle/mirror, deliver by authorized normal-index landing, acknowledge only on the marker in master. Advancing the checked-out branch (the symbolic-HEAD CAS) loses: the index keeps the old blob
F1.c.25 §0 "no third quorum family exists." | REJECTED | Local same-family approval cannot satisfy the existing Oracle cross-family signature predicates. [C11]
F1.c.26 §6 "substitutes for its own family's unavailable signer" | REJECTED | Dual emergency revocation is intentional recovery authority; shared-owner compromise is outside the independence guarantee. [C11]
