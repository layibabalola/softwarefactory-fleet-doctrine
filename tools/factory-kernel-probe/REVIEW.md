> **NOT DOCTRINE — superseded draft, kept as evidence.** This is magic-lantern_dannephoto's full-posture self-review of its parallel
> universal-kernel draft. `specs/fleet-factory-kernel.md` r1 (steward: Conjugal) landed first and the owner ruled it is the kernel
> (2026-09-14). What this draft adds is filed to r1's steward in `adjudications/factory-kernel/magic-lantern_dannephoto.md`.
> RULING R10 referenced below was never landed.

project: magic-lantern_dannephoto
subject: specs/universal-factory-kernel.md (pre-landing draft; this filing's findings are folded into the landed text)
test_bench: C:\code\magic-lantern_dannephoto @ 1dc6162 (codex/audit-remediation-2026-07)
providers: claude(fable,opus,sonnet,haiku) codex(astra,sol,luna) from ~/.claude/machine-inventory.yaml
posture: conjugal-standard COMPLETE (17/17 lanes)   <- copied from tools/review-posture/review_posture.py posture (R9)
cross_family: validated
rubric_id: 3f5af0b33548ce87204de610163d9524dd668bf9f7b19561867d6fc201ad02ab   (tools/review-posture/rubrics/factory-kernel-v0.json; contract in REVIEW.rubric.json)
panel: composite 63.88 over 8/8 seats, 2 families, spread 31.2
classifier: STOPPING FLAT (votes {'classifier-1': 'NOT-FLAT', 'classifier-2': 'FLAT', 'classifier-3': 'FLAT'}); ceilings [75.0, 79.0, 74.0] (median 75.0)

<!-- The author reviewing its own draft is a conflict the full posture exists to contain: every lane was a separate
     provider-CLI process that never saw this session's reasoning, and the arbiter, consolidator and classifier chose
     what survived. The folding below was done by the author session and is NOT reviewed; the first §8 amendment round
     reviews it. -->

## Disposition — how each finding changed the landed v0

| finding (classifier F#) | disposition in the landed v0 | pinned by |
|---|---|---|
| F1 §4 K5 existence admits failed evidence (3/3) | **FOLDED.** K5 requires a `*.receipt.json` with exit 0, a matching identity and a non-author verifier. Failing `*.status` files are flagged, and existence alone is WARN, never PASS. On the bench, K5 went PASS → WARN, with 4 failing status files found in B03's first-attempt tree. | `test_k5_existence_is_not_execution`, `test_k5_passing_receipt_passes_and_failing_or_self_verified_does_not` |
| F2 §4 K1 PASS on zero readable units (3/3) | **FOLDED.** K1 is UNKNOWN when no adopted units are readable. On the prose bench, K1 went PASS → UNKNOWN. | `test_k1_never_assumes_master_and_never_passes_on_zero_units` |
| F3 §5 delivery manufactured by regex+state (3/3) | **FOLDED.** Delivery counts only with a mapped `delivery_evidence` field. A delivery-class unit that is done but has no evidence is FAIL; a missing mapping is WARN. | `test_k6_delivery_needs_delivery_evidence` |
| F4 §3 author/verifier unmappable (3/3) | **FOLDED.** `author` and `verifier` are ledger fields, and a ledger author equal to its verifier is K5 FAIL. The receipt carries both. §3 names model seats and reader panels as valid non-author keys. | `test_k5_passing_receipt_passes_and_failing_or_self_verified_does_not` |
| F5 §7 date-only record names overwrite (0/3) | **FOLDED anyway** (cheap and correct): `<UTC-timestamp>-<ref-head12>.json`, and the tool refuses to overwrite. | `test_feedback_path_is_single_writer_and_never_overwrites` |
| F6 §9 coverage (1/3) | **FOLDED.** Every invariant must be measured on ≥ 0.8 of projects and on ≥ 1 project per represented domain; N/A is excluded from the denominator. | `test_harvest_flags_demotion_and_coverage` |
| F7 §9 landed-amendment criterion absent from the tool (2/3) | **FOLDED.** The harvest checks for a proposal with `status: LANDED` whose `landing_commit` is reachable on the bus. | `test_harvest_is_derived_and_withholds_promotion_without_a_landed_amendment` |
| F8 §6 BENCHED without a record (2/3) | **FOLDED.** Statuses are now CONTRACT / MEASURED / PROVEN. Both benches filed records in this landing, and firmware reads "MEASURED; 0 delivered". | the records under `feedback/factory-kernel/` |
| F9 §4 K3 observed executors (Untested, 0/3) | **FOLDED as an optional probe.** `admission.observed_executors_argv` compares observed executors with eligible and active units. Without it, K3 says it saw only the declared floor. | `test_k3_zero_eligible_with_an_admission_floor_fails` |
| F10 §3/§4 candidate identity vs K1 commits (3/3) | **FOLDED.** K1 checks commit identities; non-commit identities are bound by their K5 receipt. | spec §4 K1 row; K1 `non_commit` evidence field |
| Panel: WARN rules, K7 window, K8 freshness, command schema, domain enum (fable, sonnet1, luna) | **FOLDED.** §4 defines each result; the window is 14 days and the receipt limit 7 days; §5 gives the command output schema and the domain classes. | `test_constants_are_stated_in_the_spec`, `test_command_ledger_contract` |
| Panel: K2 and K7 hard-wire git (opus, astra) | **FOLDED.** `checkout.substrate`: a non-git substrate declares its identity, and K7 is UNKNOWN until a substrate adapter exists. | `test_k2_other_substrates_declare_identity` |
| Panel: harvest SUMMARY.md has many writers; amendments land without an owner act (sol) | **FOLDED.** The harvest is derived and never committed. A change in meaning, constant or authority needs an owner approval recorded in RULINGS. | `test_harvest_is_derived_…`; spec §8 |
| Panel: demotion and versioning are prose only (sonnet3) | **FOLDED.** The harvest lists invariants due for demotion and counts only current-version records. | `test_harvest_flags_demotion_and_coverage` |
| Panel: K10 bypassed when nothing is blocked; K11 self-certifies (sonnet2, design-verify) | **FOLDED.** An owner channel is always required; owner-interactive mode needs evidence from the last 14 days; any live probe among several passes. | `test_k10_…`, `test_k11_owner_interactive_needs_recent_evidence` |
| Panel: K7 hides churn by counting any product file (sonnet2) | **FOLDED.** A file-level ratio is reported beside the commit-level one, and zero product commits alarms. | `test_k7_zero_product_motion_raises_the_alarm` |
| Panel: state machine lacks recovery transitions (astra) | **FOLDED.** §3 adds unblock, lease expiry, identity change and rejection. | spec §3 |
| Panel: K4/K9 records are not authenticated (sol) | **DISCLOSED, not fixed.** Shadow mode records these and does not authenticate them; enforcement after v1 needs owner-signed records (spec §4). | — |
| Panel: K7 alarms permanently for the strategy adapter (opus) | **PARTIAL.** Each adapter may set `paths.alarm_ratio`. The bus measured 0.511 with no alarm, but the product/governance split for doctrine itself is still judgement. | notes in the bus's record |
| Panel: solo domains cannot supply a non-author key (opus) | **FOLDED.** A model seat or reader panel that did not author the work counts (spec §3). | spec §3 |

## Design findings

§4 K5 | "evidence paths exist on the integration ref or in the evidence store" | Existence admits failed evidence: bench `audit-packet/recovery-20260907/b03/verify/pytest.status` exists but contains `1`; exit status, SHA, freshness, provenance unchecked. | REPLACES: "evidence paths exist on the integration ref or in the evidence store" → "evidence validates candidate identity, command, exit status, timestamp, toolchain, log digest, and verifier identity" | PROOF: Map an adopted bench unit to that failing status file; K5 must FAIL.

§4 | "**UNKNOWN is never rounded to PASS.**" | K1 violates the kernel's own axiom: bench manifest with `ledger.kind: none` (§5 invites this) yields `K1 PASS 0 adopted commits checked` while K3–K6 and K10 correctly go UNKNOWN. | REPLACES: "`rev-parse`; `merge-base --is-ancestor` per adopted commit" → "`rev-parse`; `merge-base --is-ancestor` per adopted commit; UNKNOWN when no adopted units are readable" | PROOF: check the bench twice, ledger present and `kind: none`; K1 must not PASS on zero units.

§5 | "`delivery.{describe, id_regex, when_state}`" | A regex and state can manufacture delivery without evidence; the bench ledger has 39 work items, 11 `done`, and zero delivery or acceptance fields. | REPLACES: "`delivery.{describe, id_regex, when_state}`" → "`delivery.{describe, when_state, evidence, accepted_by, accepted_at, candidate_identity}`" | PROOF: Map all 11 `done` items to delivery without receipts; K6 must FAIL.

§3 | "CANDIDATE → VERIFIED | a key that did not author the candidate" | Never measured and unmappable: §5's `json-tasks` field list has no author/verifier keys, though `roadmap/recovery/execution-state.json` carries `worker` and `verifier` per task. | REPLACES: "commit, evidence, reason, authority, updated" → "commit, evidence, reason, authority, updated, author, verifier" | PROOF: set B01's `verifier` to `Luna b01_baseline`, matching its `worker`; the check still reports K5 PASS. (Anchor lives in §5's field list; the edit lands there — see notes.)

§7 | "This writes `feedback/factory-kernel/<project>/<YYYY-MM-DD>.json`, single writer." | Date-only names overwrite same-day runs; the bench made 27 commits on 2026-09-07, so per-sync evidence can collapse into one record. | REPLACES: "This writes `feedback/factory-kernel/<project>/<YYYY-MM-DD>.json`, single writer." → "This appends `feedback/factory-kernel/<project>/<UTC-timestamp>-<ref-head>.json`, single writer." | PROOF: Run feedback twice at different bench commits on one date; both records must survive.

§9 | "no invariant UNKNOWN on every project;" | Permits four UNKNOWNs and one PASS per invariant; the bench currently has zero factory-kernel manifests or records, so its domain adds breadth without evidence. | REPLACES: "no invariant UNKNOWN on every project;" → "each mandatory invariant is measured on at least 80% of projects and at least one project per represented domain;" | PROOF: Harvest five records with four UNKNOWN K5 results; promotion must be withheld.

§9 | "at least one amendment landed through §8, which proves the loop works, not just that it exists." | The promotion tool omits this criterion; the bench has zero factory-kernel proposal or record paths, so an unexercised loop does not mechanically block eligibility. | REPLACES: "at least one amendment landed through §8, which proves the loop works, not just that it exists." → "at least one amendment path and landing receipt are validated as a mandatory PROMOTION criterion." | PROOF: Harvest otherwise qualifying records with no proposal or receipt; eligibility must remain false. (Distinct clause of the same §9 criteria list as the previous finding; both REPLACES compose without conflict.)

§6 | "**BENCHED** (magic-lantern_dannephoto, 2026-09-14)" | No record backs it: `feedback/factory-kernel/magic-lantern_dannephoto/` holds only `manifest.json` and `2026-09-14.notes.md`; §7 defines filing as writing `<YYYY-MM-DD>.json`. | REPLACES: "**BENCHED** (magic-lantern_dannephoto, 2026-09-14)" → "MANIFESTED (magic-lantern_dannephoto); BENCHED on its first filed record" | PROOF: `harvest` over the bus counts 0 records, 0 projects, contradicting the table.

## Untested

The following wins provisionally: the bench check reports zero eligible and zero active units, so the claimed-unit/capacity failure mode remains unproved on this bench.

§4 K3 | "eligible and active counts against the declared admission floor" | A configured minimum is not capacity; bench config lists four lanes while `roadmap/handoff/board-state.md` reports zero READY/active and a Disabled scheduler with approximately 12,600 missed runs. | REPLACES: "eligible and active counts against the declared admission floor" → "eligible, claimed, runnable executor slots, resource constraints, observation time, and capacity-source evidence" | PROOF: Declare minimum zero while one bench unit is CLAIMED and runnable capacity is zero; K3 must FAIL.

## Cross-section contradictions

§3/§4/§6 (LINT-CODEX 2, KEPT) | §3 permits an artifact hash or document blob as the exact candidate identity, but K1 universally requires an adopted unit's commit and measures commit ancestry; §6 permits artifacts outside git without defining an identity-to-commit binding. | REPLACES: none supplied by the arbiter — the spec must either restrict candidate identity to commits or define the identity-to-commit binding K1 measures. | PROOF: Adopt a bench unit identified only by an artifact hash per §3; K1's `merge-base --is-ancestor` has no commit to test and must go UNKNOWN or FAIL, not PASS.

## Losers

defect class | loser | counterexample
--- | --- | ---
Verification evidence validation | DESIGN-SCOPE §4 K5 | Its replacement accepts a recorded exit status of `1`; §3 requires evidence supporting VERIFIED, and the cited failing status file still passes the current existence check.
Verifier independence | DESIGN-VERIFY §3 | §3 already requires a non-author key; restating that requirement leaves §5’s missing author/verifier mappings untouched.
BENCHED status | DESIGN-VERIFY §6 | §6 makes filing an adapter record the BENCHED milestone; successful hardware acceptance is delivery, not a prerequisite for bench status.
Delivery accounting | DESIGN-SCOPE §4 K6 | §3 permits units to remain ADOPTED before DELIVERED; accurately reporting 11 adoptions and zero deliveries satisfies §4’s separate-counter requirement.
Admission measurement | DESIGN-SCOPE §4 K3 | §2 defines an executor as a lane or process working a unit; four existing worktrees with zero active units do not establish four admitted executors.
Governance classification | DESIGN-SCOPE §4 K7 | §2 explicitly includes review paths in governance, and K5 permits evidence in an evidence store; citing evidence neither makes its commit product work nor requires governance commits.
Promotion semantics | DESIGN-SCOPE §9 | Its replacement would accept measurements that are FAIL everywhere; §8 expressly allows the conclusion that projects are wrong, so an accurately raised warning need not count as conformance.
Feedback landing destination | DESIGN-SCOPE §7; DESIGN-VERIFY §7; LINT-CODEX 1 | §5 locates these files on the bus and §7 explicitly syncs the bus; the firmware project’s branch being ahead of master does not contradict that destination.
Owner-interactive liveness | DESIGN-VERIFY §4 K11 | A project with zero eligible units may legitimately remain owner-interactive under K11; requiring evidence of an eligible unit served would demand nonexistent work.
Partial review honesty | LINT-CODEX 3 | K8 invokes R9, whose R9.1 explicitly permits skipped roles when honestly labelled PARTIAL.
UNKNOWN coverage contradiction | LINT-CODEX 4 | Four UNKNOWN results remain UNKNOWN when one measured PASS yields a 100% measured PASS rate; §9 does not relabel them.
Blanket consistency clearance | LINT-CLAUDE NONE | §3 admits non-commit candidate identities while K1 specifies only adopted commits and commit ancestry.

## Panel (blinded; factory-kernel-v0 rubric)

| seat | family | Universality | Measurability | Anti-Fixpoint Honesty | Adoption Cost | Self-Improvement Loop | Authority Safety | composite |
|---|---|---|---|---|---|---|---|---|
| panel-fable | claude | 72 | 68 | 88 | 65 | 80 | 90 | 77.2 |
| panel-opus | claude | 52 | 70 | 84 | 72 | 76 | 85 | 73.2 |
| panel-sonnet1 | claude | 58 | 66 | 82 | 40 | 74 | 86 | 67.7 |
| panel-sonnet2 | claude | 64 | 47 | 48 | 68 | 58 | 76 | 60.2 |
| panel-sonnet3 | claude | 58 | 76 | 70 | 64 | 47 | 76 | 65.2 |
| panel-astra | codex | 38 | 43 | 66 | 55 | 54 | 64 | 53.3 |
| panel-sol | codex | 35 | 45 | 65 | 63 | 43 | 25 | 46.0 |
| panel-luna | codex | 68 | 55 | 83 | 60 | 68 | 76 | 68.3 |
| **mean** | | 55.6 | 58.8 | 73.2 | 60.9 | 62.5 | 72.2 | **63.88** |

The spread of 31 points came from the two Codex verifier seats. Sol scored Authority Safety at 25, and Astra and Sol
scored Universality at 35–38. Astra named the K5 existence check and the git hard-wiring. Sol named the unimplemented landed-amendment criterion,
the unauthenticated K4/K9 records, and the multi-writer summary. All are folded above except authentication, which is
disclosed. The panel scored the draft, not the landed text.

## Classifier consensus (Haiku ×3, strict tally, 2-of-3)

| finding | kind | grounded | must-fix votes |
|---|---|---|---|
| F1 | DESIGN | GROUNDED | 3/3 **MUST-FIX** |
| F2 | DESIGN | GROUNDED | 3/3 **MUST-FIX** |
| F3 | DESIGN | GROUNDED | 3/3 **MUST-FIX** |
| F4 | DESIGN | GROUNDED | 3/3 **MUST-FIX** |
| F5 | NO-CONSENSUS | GROUNDED | 0/3 |
| F6 | DESIGN | GROUNDED | 1/3 |
| F7 | DESIGN | GROUNDED | 2/3 **MUST-FIX** |
| F8 | DESIGN | GROUNDED | 2/3 **MUST-FIX** |
| F9 | DESIGN | GROUNDED | 0/3 |
| F10 | DESIGN | GROUNDED | 3/3 **MUST-FIX** |

Every seat's hand-off experiment is now a passing regression test: a failing status file in adopted evidence, K1 on
zero units, and two records on one date.

## Provenance

- Stage A 20:44:14Z–20:49:36Z; stage B 20:49:37Z–20:53:00Z; the rest resumed at 20:53:36Z and stage D finished at
  21:00:47Z (UTC, 2026-09-14).
- **The arbiter degenerated on its first dispatch.** At rc=0 and 8,813 bytes it repeated its last five losers and stopped
  without `LANE-COMPLETE`. The tool refused stages C and D (`STAGE C BLOCKED`). It was re-run with the new
  `run.sh --from B --retry-missing`, which kept all 8 panel seats that had cleared the sentinel and re-dispatched only
  the arbiter (8,733 bytes, cleared). The failed output is kept locally as `arbiter.failed-205336.txt`.
- Lint: Haiku returned NONE (DROPPED by the arbiter: it missed the identity contradiction). Luna's 4 items: 1 KEPT,
  3 DROPPED with reasons.
- Bench facts re-measured by the orchestrator: `b03/verify/pytest.status` = `1` on the integration ref; all 4
  non-passing status files are in `b03/`; the ledger has `worker` and `verifier` fields.
- The classifier's first tally read every finding's kind as NO-CONSENSUS because one seat wrote a label before the
  verdict. The tally was widened to that same-line form, pinned in `test_strict_parse_and_two_of_three`, and re-run
  on the unchanged outputs.

## Lint rulings

- **LINT-CLAUDE — NONE: DROP.** Its blanket clearance misses the candidate-identity mismatch retained below; its three highlighted section pairs do not themselves establish contradictions. It neither duplicates nor specifically undermines a designer finding.
- **LINT-CODEX 1 — DROP.** §5 places manifests on the doctrine bus, and §7 writes through `--doctrine <bus>` and leaves that bus synced; the bench’s project integration branch is a different destination. Duplicates—and its rejection undermines—both designers’ §7 landing findings.
- **LINT-CODEX 2 — KEEP.** §3 permits an artifact hash or document blob as the exact candidate identity, but K1 universally requires an adopted unit’s commit and measures commit ancestry; §6 permits artifacts outside git without defining an identity-to-commit binding. Neither duplicates nor undermines a designer finding: this is distinct from DESIGN-SCOPE’s missing-ledger K1 defect.
- **LINT-CODEX 3 — DROP.** R9.1 explicitly permits skipped roles when labelled PARTIAL, and R9.3 permits cross-family validation of PARTIAL runs; §8’s labelled exception therefore obeys K8. Neither duplicates nor undermines a designer finding.
- **LINT-CODEX 4 — DROP.** Excluding UNKNOWN results from a measured-results denominator does not convert those results to PASS; insufficient promotion coverage is a policy weakness, not the asserted contradiction. Duplicates DESIGN-VERIFY’s coverage concern without undermining that finding.
