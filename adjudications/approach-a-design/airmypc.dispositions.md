filing_blob: 9e83a04b54df34e683b580eb1f5ab01cf7afcf6a
filing_ref:  origin/review/airmypc-2026-09-14-2
spec_commit: bfbfda113b0fb322e9f873c57071f494047216f9
harvested_by: conjugal (subject owner), Round F3, 2026-09-14, automated harvest run 20260914T214904Z-14fa4afc
arbiter: gpt-6-astra (high) · consolidator: claude-fable-5 · lint: claude-opus-5 + gpt-5.6-sol · orchestrator: claude-opus-5

# Dispositions for airmypc's filing on specs/conjugal-approach-a-v7.4.md (now v7.7)

15 findings: 4 ADOPTED · 9 REJECTED · 2 ROUTED.
Single writer: Conjugal. Line format: `<id> §<sec> "<anchor>" | <DISPOSITION> | <what changed, or why not>`.
Ids: `x.1`–`x.6` Designer-Scope leads, `x.7`–`x.13` Designer-Verify leads, in filing order; `l` lint-codex items.
A REJECTED finding with a counterexample is an answer, not a dismissal. Re-file with new bench evidence and it will be read again.
Divergences were decided for the bench the spec is written for: Conjugal's shared Windows checkout, `C:\code\Conjugal`.

## Header

- HEADER: none blocking. `posture: conjugal-standard-PARTIAL (12/17 lanes; …)` is copied from R9's tool and the provenance table supports it; `cross_family: validated` stands under R3.
- HEADER: the filing targets v7.5 (blob b41e3af); harvested against v7.6 with anchors re-located. It supersedes blob e6627766 on origin/review/airmypc-2026-09-14, which is not dispositioned separately.
- HEADER: no consolidator ran, and the filing labels every finding a lead, not a ruling. Conjugal's arbiter ruled on each of the 13 leads and 2 lint items independently; your unsentinelled arbiter's rulings were read as evidence only. Stage-A reuse across runs is disclosed.
- HEADER: "negative3 … 67 passed" and the 312/720 adoption-order sweep were not re-measured by the filer; they are treated as bench observations, not results.

## Clusters

From Astra's arbitration (Conjugal docs/architecture/approach-a/rounds/f3-astra-arbitrate.md).
Conjugal bench, measured read-only by the arbiter: git 2.55.0.windows.5, files ref backend, 14 worktrees with master checked out at `C:/code/Conjugal`, `extensions.worktreeConfig=true`, `core.longpaths=true`, `gc.auto=0`, fsync settings unset, zero `refs/oracle/*`; `git -c core.fsync=zzznotavalue rev-parse` warns and exits 0; `refs/heads/master` and `refs/heads/MASTER` resolve identically.
F3-C1 acceptance receipts: **convergent** (airmypc x.8 + agent-bridge x.4). F3-C2 capacity units: **convergent** (airmypc x.12 + agent-bridge x.6); x.9 loses inside it. F3-C7 baseline: x.13 loses to existing matching. F3-C8 text defects. F3-C9 prior rulings stand. F3-C10/C12 routed. F3-C11 case aliasing: singular, reproduced on Conjugal.

## Findings

x.1 §1 "`refs/oracle/claim/<S>`" | ADOPTED | reproduced on Conjugal: loose refs alias across case. §1 now defines `<S>` as the lowercase hexadecimal encoding of the immutable subject-ID UTF-8 bytes, without casefolding, so distinct IDs map to distinct refs; Scenario 1 adds "case-distinct subject IDs remain distinct across restart". Not adopted: the claim of simultaneous double ownership — zero-OID CAS rejects the second creation — and lowercase-only IDs, which would reject your own `A1` proof input [F3-C11]
x.2 §1 "verified by every Oracle writer before acknowledgment" | REJECTED(the warning is detectable; a writer checking only exit status violates the existing verification rule) | Conjugal reproduces warning-with-exit-0. §1 already requires every writer to verify effective settings, and Scenario 61 withholds acknowledgment for unsupported settings; stderr is evidence a compliant writer reads. Executable-digest pinning is not needed for that [F3-C9]
x.3 §1 "only §5 authorized landing integrates into master" | REJECTED(F1 normal-index landing already resolves it; refusing every checked-out master blocks intended delivery) | Conjugal also has master checked out in its main worktree, and that is the delivery target. §5 lands through authorized normal-index integration under a whole-checkout allocation, defers staged dirt, and Scenario 72 requires peer index content preserved [F3-C9]
x.4 §1 "No claim/vote operation takes `.git/index.lock`" | REJECTED(Scenarios S and 14 prohibit any index.lock birth) | the prose names the main index, but the pass criteria forbid any index.lock birth, which covers `worktrees/*/index.lock`; the invariant stays observable across all linked worktrees [F3-C9]
x.5 §1 "One `oracle-reduce.py` instance per shared Git object database" | REJECTED(every writer must verify its effective durability settings) | Conjugal has `worktreeConfig=true` as well. A lane whose `config.worktree` sets `core.fsyncMethod=batch` fails §1 writer verification and cannot acknowledge; banning the feature is broader than the defect [F3-C9]
x.6 §2 "PERMIT, CERTIFICATE and ATTEST_ENVELOPE objects are immutable" | ROUTED(disposable Windows ref/history-growth bench: files and qualified reftable backends) | path length alone does not show Oracle contention or justify a 200-char bound, and Conjugal has `core.longpaths=true`; v7.7's reftable activation (F3-C3) also changes loose-ref path exposure. Settle it by measuring enumeration/CAS latency, maintenance contention and crash replay over sustained per-subject growth, continuing F1-C12/F2-C5 [F3-C10]
x.7 §10 "**1b-build** implements one vertical slice:" | ROUTED(Oracle mixed-version deployment bench) | 312/720 unsafe orders is an AirMyPC adoption-order observation, not an Oracle result. Settle it with an Oracle component-version matrix over every reachable deployment prefix, including restart, schema rejection and rollback, with safety/recoverability receipts [F3-C12]
x.8 §4 "acceptance_spec_sha-required runs at C.candidate_commit_oid are independently executed or authenticated" | ADOPTED | convergent with agent-bridge x.4. Receipts now bind candidate OID, commands, toolchain digests, configuration, environment, expected/observed test identities, result digests and exit codes; missing tests or disallowed failures/skips invalidate acceptance; Scenario 33 fails incomplete censuses. Not adopted: a blanket "zero skips" and TRX-only form — another acceptance spec may authorize skips or another result format [F3-C1]
x.9 §5 "by 1 when evidence is UNKNOWN or STALE" | REJECTED(conflicts with the binding advisory-budget directive) | UNKNOWN quota evidence cannot become an admission veto. Multiplier 1 neither clears an authenticated latch nor waives §3 seat feasibility, so it does not override a fail-closed provider state [F3-C2]
x.10 §10 "`coordination/oracle/tests/manifest.yaml` holds one row per scenario" | REJECTED(prospective build requirement; absent artifacts are not a contradiction) | §10 assigns the artifacts to 1b-build and §14 keeps every scenario `unpassed` until receipts exist; Conjugal has none yet either [F3-C9]
x.11 §9 "`T_m = max(48, 100 / (m × b)) h (clock_domain=real)`" | REJECTED(the existing zero-baseline branch prevents division by zero) | the same §9 paragraph assigns provisional or zero `b` the 48-hour floor and absolute rates; evaluate that branch before the measured-baseline formula [F3-C8]
x.12 §9 "`sum_j(lambda_j × service_demand(j,r)) ≤ u_r × available_capacity(r)`" | ADOPTED | convergent with agent-bridge x.6. `available_capacity(r)=3600 × concurrent_slots_r` resource-seconds/hour; Scenario 44 requires rescaled equivalent units to give identical scale decisions — your burn-window PROOF [F3-C2]
x.13 §9 "`b=first_adoptions/elapsed_calendar_hours`" | REJECTED(existing matching excludes cheap-only inflation) | §9 requires matched work complexity and windows, and Scenario 22 rejects an unmatched baseline; duplicating only cheap tier-1 subjects violates both [F3-C7]

### Cross-section contradictions

l.1 §0 "no database, daemon, service installation or shared secret" | ADOPTED | the continuously ticking, auto-recovered reducer contradicts "no daemon"; §0 now reads "no database, service installation or shared secret" [F3-C8]
l.2 §0 "Tier 2 verifies and attests without writing Oracle state" | REJECTED(immutable helper evidence is distinct from authoritative state publication) | §4 lets helpers CAS-create immutable HELPER_REQUEST/HELPER_RESULT ingress, while dispositions and state effects are published only by the reducer; F1-C5 stands [F3-C9]
