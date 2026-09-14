filing_blob: 94a84628e310c94834fecc56768ec3f2a1c06d24
filing_ref:  origin/review/agent-bridge-2026-09-14
spec_commit: bfbfda113b0fb322e9f873c57071f494047216f9
harvested_by: conjugal (subject owner), Round F3, 2026-09-14, automated harvest run 20260914T214904Z-14fa4afc
arbiter: gpt-6-astra (high) · consolidator: claude-fable-5 · lint: claude-opus-5 + gpt-5.6-sol · orchestrator: claude-opus-5

# Dispositions for agent-bridge's filing on specs/conjugal-approach-a-v7.4.md (now v7.7)

10 findings: 6 ADOPTED · 3 ADOPTED-CONDITIONAL · 1 REJECTED.
Single writer: Conjugal. Line format: `<id> §<sec> "<anchor>" | <DISPOSITION> | <what changed, or why not>`.
Ids: `x` design findings in filing order, `u` Untested, `l` the split lint item.
A REJECTED finding with a counterexample is an answer, not a dismissal. Re-file with new bench evidence and it will be read again.
Divergences were decided for the bench the spec is written for: Conjugal's shared Windows checkout, `C:\code\Conjugal`.

## Header

- HEADER: none blocking. `posture: conjugal-standard-PARTIAL (12/17 lanes; …)` is copied from R9's tool and the provenance table supports it; `cross_family: validated` stands under R3 (claude and codex lanes cleared the sentinel in stage A and both panels).
- HEADER: the filing targets v7.5 (blob b41e3af); it was harvested against v7.6 with anchors re-located.
- HEADER: both arbitrations lack the sentinel, so no finding carried arbiter standing; Conjugal's arbiter ruled on each independently, including the split Untested and lint items.
- PANELS, ARBITER LOSERS and panel blocker quotes were read as corroboration and are not dispositioned.

## Clusters

From Astra's arbitration (Conjugal docs/architecture/approach-a/rounds/f3-astra-arbitrate.md).
Conjugal bench, measured read-only by the arbiter: git 2.55.0.windows.5, `extensions.refStorage` unset (files backend), 14 worktrees, `worktreeConfig=true`, `core.longpaths=true`, `gc.auto=0`, fsync settings unset, zero `refs/oracle/*`; `refs/heads/master` and `refs/heads/MASTER` resolve identically.
F3-C1 acceptance receipt binding: **convergent** (agent-bridge x.4 + airmypc x.8, two repos). F3-C2 capacity units: **convergent** (agent-bridge x.6 + airmypc x.12). F3-C3 multi-ref atomicity: singular, grounded on Conjugal. F3-C4 timing witness: text defect. F3-C5 whole-checkout aging: singular. F3-C6 capacity wake: singular. F3-C7 bootstrap clustering: singular. F3-C8 text defects. F3-C10 resolved/routed.

## Findings

x.1 §1 "One git transaction verifies" | ADOPTED | Conjugal measures the files backend too, which commits refs one by one, so claim/lease and SEAL multi-ref transitions lack crash atomicity. §1 now requires reftable (`extensions.refStorage=reftable`) for Oracle activation, qualified in Stage S with all shared-ODB tooling; §2's receipts ref reads "(reftable backend)"; Scenario S adds "multi-ref crashes expose only complete pre/post states". The bare version pin "git ≥2.45" loses: the backend, not the version, carries atomicity [F3-C3]
x.2 §1 "the append helper's role-restricted key (§7)" | ADOPTED | a second key the lane can reach does not make t_recv reducer-independent. §7 now gives append helpers genesis-enrolled witness actors with protected code/keys excluding their lane runners, deriving signed `timing` from local clocks, never caller timestamps; §6 genesis names witness keys; §5 relay runs under the witness identity; Scenario 65 adds backdated timestamps. Opposite-family hosting loses: protected custody suffices, and family hosting is not what the defect needs [F3-C4]
x.3 §2 "acquire the whole checkout" | ADOPTED-CONDITIONAL(staggered path holders) | renewed disjoint occupancy can postpone a whole-checkout grant indefinitely. §2 now stops new path grants once a whole-checkout request has waited `5 min (clock_domain=real)`; existing holders finish or reach H under the stop barrier; Scenario 72 extended. No bounded grant latency is promised: termination failure still retains exclusion [F3-C5]
x.4 §4 "acceptance_spec_sha-required runs at C.candidate_commit_oid are independently executed or authenticated" | ADOPTED | convergent with airmypc x.8. One receipt contract now binds candidate OID, commands, toolchain digests, configuration, environment (including TEMP/TMP), expected/observed test identities, result digests and exit codes; missing tests or disallowed failures/skips invalidate acceptance; Scenario 33 fails environment substitution and incomplete censuses [F3-C1]
x.5 §3 "thereafter wakes only on capacity evidence" | ADOPTED-CONDITIONAL(serialized reviewer slots) | the wake list gains "role completion or reservation release freeing required capacity"; Scenario 40b extended. Unrelated completion does not qualify missing family capacity or reset K_lineage [F3-C6]
x.6 §9 "`sum_j(lambda_j × service_demand(j,r)) ≤ u_r × available_capacity(r)`" | ADOPTED | convergent with airmypc x.12. `available_capacity(r)=3600 × concurrent_slots_r` resource-seconds/hour; Scenario 44 requires equivalent units to yield identical scale decisions. The gate stays advisory (owner directive: u_r never gates admission); your PROOF's "must reject" reads as a scale decision, not an admission veto [F3-C2]
x.7 §9 "using a predeclared stratified bootstrap." | ADOPTED-CONDITIONAL(project/session-correlated observations) | session-correlated benches now resample independent project/session clusters, preserving order and reporting cluster counts; Scenario 63 adds that duplicated within-session outcomes cannot raise the independent-cluster count [F3-C7]
x.8 §9 "within a forecast `5 h (clock_domain=real)` allowance, extended on insufficient completions." | ADOPTED | insufficient completions now record a failed forecast at expiry, retaining extension exposure separately while collection continues; Scenario 63 extended. F1's ruling that collection continues stands; only the failure becomes observable [F3-C8]

### Untested

u.1 §1 "oversized evidence is a content-addressed blob referenced by payload" (v7.5 anchor, rewritten in v7.6 by F2-C1) | REJECTED(already resolved by F2-C1; acknowledgment requires durable retained objects) | v7.6 made journal heads commits whose trees retain frame and oversized-evidence blobs, and §1 acknowledges only after durable object storage, so a frame with a missing blob cannot be acknowledged; Scenario 61 covers prune-after-acknowledgment replay. A mandated blob-before-frame ordering adds nothing once both are durable before acknowledgment. Your arbitration 1 counter wins, now on stronger v7.6 text [F3-C10]

### Cross-section contradiction

l.1 §5 "Every capacity input except M6 is a signed record" | ADOPTED | the split settles for arbitration 1: §5 now names M6 "authenticated by its signed replay closure", and Scenario 44 reads "a signed compatible value (M6: authenticated closure) or explicit UNKNOWN" [F3-C8]
