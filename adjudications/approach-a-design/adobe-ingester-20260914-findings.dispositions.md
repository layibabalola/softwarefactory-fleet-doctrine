filing_blob: 5d9c32e1c5223b1591de6b5ecd43af793886ddbd
filing_ref:  origin/master
spec_commit: bfbfda113b0fb322e9f873c57071f494047216f9
harvested_by: conjugal (subject owner), Round F3, 2026-09-14, automated harvest run 20260914T214904Z-14fa4afc
arbiter: gpt-6-astra (high) · consolidator: claude-fable-5 · lint: claude-opus-5 + gpt-5.6-sol · orchestrator: claude-opus-5

# Dispositions for adobe-ingester's filing on specs/conjugal-approach-a-v7.4.md (now v7.7)

50 items: 17 IDed findings, 3 redesign proposals, 1 release-gate motion, 29 advisory bullets.
0 ADOPTED · 49 REJECTED · 1 ROUTED. v7.7 changed nothing on this filing's account.
Single writer: Conjugal. Line format: `<id> §<sec> "<v7.6 anchor the ruling rests on>" | <DISPOSITION> | <why>`.
The filing carries no anchors, so each `§` and quote below is the v7.6 clause the arbiter checked the claim against, not a filed anchor.
A REJECTED finding with a counterexample is an answer, not a dismissal. Re-file with a `REPLACES:` anchor quoted verbatim from the current spec and a path, tool or measured number from the Adobe Document Cloud Ingester repo, and it will be read again.
Divergences were decided for the bench the spec is written for: Conjugal's shared Windows checkout, `C:\code\Conjugal`.

## Header

- HEADER: no `project:`, `providers:`, `seats:`, `posture:`, `cross_family:` or `rubric_id:` lines (harvest-status flag NO-PROVIDERS-HEADER; the tool counts 0 anchored findings). The only provenance is a trailer naming one family, Claude Haiku 4.5 (5-agent swarm): weight as one family's opinion.
- HEADER: no test bench path or commit; no finding cites a path, tool or measured number in the filing project's repo, so the test-bench rule that gives filings their weight is unmet. Every ruling below rests on the v7.6 text alone.
- HEADER: no finding carries a `REPLACES:` anchor or a verbatim subject quote; its "line 224/226/227/233/194/218" references do not address the bus file.
- HEADER: internal counts disagree — "44 findings" vs 17 IDs plus 29 advisory bullets; "7 Total" blocking lists 9; S-02 and S-04 are listed as both blocking and staged; advisory headings say 10/6/4/4 but list 13/8/4/4; "Lateness undefined" appears as A-02 and again as advisory; proposal 2 addresses "S-07", which is never defined.
- HEADER: the title calls the subject v7.5 while the subject line cites v7.4 at "RFC 862df45"; which text was read cannot be established.
- HEADER: its motions (ratify a PROVISIONAL v7.5 in RULINGS.md, Sol ratification gate, Adobe co-ownership) confer no authority on a subject with a single writer; they are dispositioned as proposals (m.1).

## Findings

a.1 §7 "signing requires family-isolated custody" (S-01 cross-family key isolation on shared SIDs) | REJECTED(F1 already requires enforced isolation) | shared-SID signing is unavailable without demonstrated separation, and §13 lists hostile shared-SID signing isolation as requiring qualification [F3-C9]
a.2 §6 "pending that quorum" (S-02 COMPROMISE_REPORT freezes emergency revocation) | REJECTED(freezing compromised authority is intentional) | ordinary non-target signers can still revoke, and §13 explicitly accepts a blocked revocation when authority is unavailable
a.3 §7 "old-key new receipts have grace" (S-04 vote creation-time binding) | REJECTED(validity intentionally uses receipt-time evidence) | the "pinned receipt-time key chain" answers dating; creation-time authority is not promised and no attack using it is shown
a.4 §2 "FORCE_RELEASE replay matches its recorded transition" (T-03 claim/reclaim/force-release race) | REJECTED(race protection and recovery tests already specified) | expected-OID transactions, stop barriers and Scenarios 25/49 reject stale transitions
a.5 §4 "conflicting agreements stay quarantined under the original deadlines" (T-05 arbitration deadlock) | REJECTED(disagreement has an explicit bounded disposition) | QUARANTINE-BLOCKED and Scenario 37 cover unresolved arbitration
a.6 §8 "arithmetic never mixes domains without an explicit mapping" (A-01 clock-domain mixing in lateness) | REJECTED(explicit mapping and interval rules answer it) | lateness is decided by comparable intervals, not by mixed raw timestamps
a.7 §4 "unchanged gate OIDs across the pinned dependency closure" (A-05 FRONTIER_ADVANCE vs adoption CAS) | REJECTED(frontier races are explicitly fenced) | adoption re-checks pending emptiness and gate OIDs in one transaction, so the alleged unfenced adoption cannot occur
a.8 §7 "prior PID/creation identity is dead" (O-01 Windows PID reuse) | REJECTED(process identity includes creation time) | a reused PID alone cannot match the previous holder's `{pid, creation_time}` identity
a.9 §3 "only `clock_miss_count` increments" (O-03 bridge unavailability livelock) | REJECTED(unbridgeable clocks have explicit outcomes) | after 120 s uncertain approvals earn no credit, and §13 acknowledges unavailable mappings; no 2-hour livelock follows from the text
a.10 §9 "Configuration tuple changes invalidate forecasts immediately" (T-01 provisional parameter changes) | REJECTED(configuration changes already invalidate qualification) | no missing parameter transition or failing scenario is named
a.11 §9 "provisional or zero b plans" (T-02 load-formula edge cases) | REJECTED(zero-baseline branch already specified) | the text assigns the 48-hour floor and absolute rates
a.12 §7 "or BRIDGE_UNAVAILABLE" (T-04 bridge recovery) | REJECTED(bridge recovery is bounded and tested) | acquisition publishes a bridge or unavailability within 120 s; Scenario 34
a.13 §11 "no stale build commits" (T-06 pipelined publication depth-2) | REJECTED(Scenario 68 explicitly tests depth-two recovery) | dependency changes, crashes and serial-equivalent replay are required there
a.14 §3 "`late=1`" (A-02 lateness undefined) | REJECTED(lateness is explicitly defined) | interval separation determines lateness; overlapping uncertainty has its own disposition
a.15 §2 "policy_epoch (global)" (A-03 policy epoch ambiguous) | REJECTED(epoch scope and migration are explicit) | §6 requires an in-flight migration map; historical votes keep their policy
a.16 §0 "one shared Windows checkout" (D-01 Law 2 namespace collision) | REJECTED(unanchored doctrine claim; re-file with the rule and evidence) | Conjugal-specific scope asserts no fleet-wide namespace contract; the colliding name is never identified
a.17 §8 "cleanup addresses exact registered identities" (O-02 Task Scheduler collisions) | REJECTED(no production collision established) | injective fixture task names and Scenario 27 already cover test collisions

### Proposals and motions

p.1 §8 "Production fixes SCALE=1/OFFSET=0." (Innovator 1: self-adjusting forecast oracle) | REJECTED(unsupported redesign) | feedback-loop forecasts do not supply clock comparability, the defect it claims to fix (a.6 rejected); §9 already recomputes T_m from measured b
p.2 §7 "a timeout alone never steals a live holder" (Innovator 2: fleet-wide reducer lease per family, 120 s timeout) | REJECTED(weakens established singleton recovery) | a per-family holder can create two publishers for one object database, and a 120 s timeout steals from a live holder [F3-C9]
p.3 §0 "one shared Windows checkout" (Innovator 3: ephemeral cloud execution hosts) | REJECTED(changes scope without qualification, and spends money) | multiple hosts do not establish linear throughput, and a paid runner pool is an owner decision, not a harvest edit
m.1 §10 "zero unresolved safety failures" (Pragmatist MVP release gate, PROVISIONAL v7.5 ruling, Adobe co-ownership, Sol ratification) | REJECTED(unverified release and co-ownership proposal) | §10's executable gates and named owners remain authoritative; Conjugal is the subject's single writer, and the harvest does not publish rulings to RULINGS.md

### Advisory bullets (one grouped ruling, per Astra)

Grouped ruling: REJECTED(covered by existing requirements or unanchored hypotheses) — §§2–9 and Scenarios 25–72 answer the bullets as named; none carries an anchor, a failure trace or bench evidence. Exception: "Unbounded ledger growth" is ROUTED [F3-C10].

v.1 §9 "Configuration tuple changes invalidate forecasts immediately" (Provisional parameters, scenario re-runs) | REJECTED(covered; unanchored) | duplicates a.10
v.2 §9 "provisional or zero b plans" (Load formula zero-capacity) | REJECTED(covered; unanchored) | duplicates a.11
v.3 §2 "FORCE_RELEASE replay matches its recorded transition" (Concurrent release races) | REJECTED(covered; unanchored) | duplicates a.4
v.4 §11 "no stale build commits" (Pipelining safety verification) | REJECTED(covered; unanchored) | duplicates a.13; Scenario 68
v.5 §4 "Every mechanism has parameters" (Relay backoff progression) | REJECTED(covered; unanchored) | relay cadence is fixed to sidecar ticks and floor wakes in §5; no progression defect named
v.6 §5 "emit one ROTATE_REQUEST per episode" (Latch episode boundaries) | REJECTED(covered; unanchored) | episode identity and LATCH_CLEARED are specified; owner directive
v.7 §8 "arithmetic never mixes domains without an explicit mapping" (Dynamic horizon mapping) | REJECTED(covered; unanchored) | explicit mapping rule
v.8 §4 "Every mechanism has parameters" (Replace-objects isolation) | REJECTED(covered; unanchored) | no replace-object path is named against any v7.6 clause
v.9 §4 "unchanged gate OIDs across the pinned dependency closure" (Dependency loss split threshold) | REJECTED(covered; unanchored) | dependency closure is re-checked at adoption; no threshold defect shown
v.10 §3 "K_lineage" (K_lineage episode exhaustion) | REJECTED(covered; unanchored) | recovery-episode triggers are enumerated in §3
v.11 §1 "incomplete tails never authorize" (Frame checksum corruption) | REJECTED(covered; unanchored) | invalid tails carry no authority; Scenario 61
v.12 §1 "Every mechanism has parameters" (Frontier deduplication boundary) | REJECTED(covered; unanchored) | idempotency keys are in the §2 registry
v.13 §5 "emit one ROTATE_REQUEST per episode" (Dual provider latches) | REJECTED(covered; unanchored) | latches are per provider episode; Scenario 70
v.14 §5 "Every capacity input except M6" (Admission load stale) | REJECTED(covered; unanchored) | stale inputs resolve to UNKNOWN and are advisory only (owner directive)
v.15 §3 "`late=1`" (Lateness undefined) | REJECTED(covered; unanchored) | duplicates a.14
v.16 §4 "Every mechanism has parameters" (Sealed+suspect closure) | REJECTED(covered; unanchored) | SHADOW_ATTEST and ATTEST_SUSPECT handling are specified
v.17 §7 "a timeout alone never steals a live holder" (Sidecar renewal race) | REJECTED(covered; unanchored) | lease renewal is CAS-fenced; "S-07" is undefined in the filing
v.18 §6 "Every mechanism has parameters" (Amendment Catch-22) | REJECTED(covered; unanchored) | the §6 authorized policy chain governs amendments; no deadlock trace given
v.19 §7 "or BRIDGE_UNAVAILABLE" (Bridge ordering gaps) | REJECTED(covered; unanchored) | duplicates a.12
v.20 §2 "Every mechanism has parameters" (Mutation list recovery) | REJECTED(covered; unanchored) | the mutable-ref list and fence classes are closed in §2
v.21 §4 "Every mechanism has parameters" (Dual adoption fallback) | REJECTED(covered; unanchored) | adoption is keyed by `(subject,phase,verdict_ver,adopter)` and fenced
v.22 §10 "Every mechanism has parameters" (Law 3: checker export surfaces) | REJECTED(covered; unanchored) | doctrine rule and export surface are not identified
v.23 §9 "Configuration tuple changes invalidate forecasts immediately" (Law 3: provisional retest gates) | REJECTED(covered; unanchored) | provisional values are retested on configuration change
v.24 §6 "Every mechanism has parameters" (Law 1: digest authority ambiguity) | REJECTED(covered; unanchored) | genesis and §6 policy chain name the digest authority
v.25 §0 "one shared Windows checkout" (Law 6: Adobe portability contract) | REJECTED(out of scope) | this is the code-profile instance for Conjugal's checkout; portability belongs to the fleet kernel via dogfood filings
v.26 §5 "Every mechanism has parameters" (Downstream queue detection) | REJECTED(covered; unanchored) | no undetected queue path named
v.27 §4 "Every mechanism has parameters" (Floor task heartbeat monitoring) | REJECTED(covered; unanchored) | §13 already names a floor that never fires as a residual; floors sweep every 30 s
v.28 §1 "live receipt OIDs are never pruned" (Unbounded ledger growth) | ROUTED(disposable Windows ref/history-growth bench) | a real open question, continuing F1-C12/F2-C5: measure retention, enumeration/CAS latency and maintenance contention over sustained growth [F3-C10]
v.29 §1 "Every mechanism has parameters" (Lock recovery procedures) | REJECTED(covered; unanchored) | stale-lock recovery is specified through process identity and stop barriers; no failing procedure named
