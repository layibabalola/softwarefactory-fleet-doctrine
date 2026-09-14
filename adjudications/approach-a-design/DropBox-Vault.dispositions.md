filing_blob: 49336b90a78e73171cab7ba279d8bbfbd4102030
filing_ref:  origin/review/DropBox-Vault-2026-09-13
spec_commit: f3043ccaab408b3d68bb670bb82b46293de05a05
harvested_by: conjugal (subject owner), Round F1, 2026-09-14, Bachelor / Dell XPS 17
arbiter: gpt-6-astra (high) · consolidator: claude-fable-5 · lint: claude-opus-5 + gpt-5.6-sol · orchestrator: claude-opus-5

# Dispositions for DropBox-Vault's filing on specs/conjugal-approach-a-v7.4.md (now v7.5)

39 findings: 12 ADOPTED · 3 ADOPTED-CONDITIONAL · 22 REJECTED · 2 ROUTED.
Single writer: Conjugal. Line format: `<id> §<sec> "<anchor>" | <DISPOSITION> | <what changed, or why not>`.
A REJECTED finding with a counterexample is an answer, not a dismissal. Re-file with new bench evidence and it will be read again.

## Header

- HEADER: `posture: conjugal-standard` names a posture that ran 5 of 17 lanes; RULINGS R9.5 asks the filer to relabel it `conjugal-standard-PARTIAL (5/17 lanes; …)` or re-run. Harvested anyway at the weight the provenance supports.
- HEADER: the cross-family claim stands under R3 (2 Claude + 3 Codex lanes cleared the sentinel). The kept-verbatim claude-only set (F1.c) was weighed as one family's opinion, and its repeats of the cross-family findings were not counted as independent convergence.
- HEADER: F1.c.8's P_par anchor is in §10, not the §1 it was filed under.
- SUPERSEDED COPY: master still carries blob d690311f (the 26-finding claude-only filing). Its findings are the F1.c set here, so no separate answer is owed.

## Clusters

Cross-project clusters, from Astra's arbitration (Conjugal docs/architecture/approach-a/rounds/f1-astra-arbitrate.md):
C1 relay/mirror commits: convergent defect, divergent fixes; the non-checked-out ref wins. C2 mutex/journal identity: convergent. C3 replay is not acceptance: convergent. C4–C7, C9–C11: divergent, Conjugal's bench and contract win. C8 zero-eligible input: adopted. The calendar-hour estimand is kept. C12 receipts head: adopted for the files backend, growth routed. C13 P_par: bench-qualified.

## Findings

### cross-family findings

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

### Untested

F1.u.1 §2 "`refs/oracle/claim/<S>`" | ROUTED | Windows files-and-packed-ref subject-ID fixture

### prior claude-only set (kept verbatim in the filing)

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
F1.c.16 §4 "floors hold task-start permission only" | REJECTED | Phases 1b and 1b-build establish custody; a missing pre-build installer is not a missing acceptance requirement. [C7]
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
