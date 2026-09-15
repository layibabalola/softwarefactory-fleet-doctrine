filing_blob: efdf80d7bef86d64490cbbd43270e788af76d6d3
filing_ref:  origin/review/agent-bridge-2026-09-14-2
spec_commit: 6a285b1ae2cae1e7f67cad4ddd3e5a68c2b2512f
harvested_by: conjugal (subject owner), Round F4, 2026-09-15, automated harvest run 20260915T143404Z-6e5aa419
arbiter: gpt-6-astra (high, three scoped calls) · consolidator: claude-fable-5 · lint: claude-opus-5 + gpt-5.6-sol · orchestrator: claude-opus-5

# Dispositions for agent-bridge's filing on specs/conjugal-approach-a-v7.4.md (now v7.8)

6 findings: 2 ADOPTED · 2 REJECTED · 2 ROUTED.
Single writer: Conjugal. Line format: `<id> §<sec> "<anchor>" | <DISPOSITION> | <what changed, or why not>`.
Ids: `b.x1` the one consolidated Design finding, `b.u1`–`b.u5` the `## Untested` lines in filing order.
A REJECTED finding with a counterexample is an answer, not a dismissal. Re-file with new bench evidence and it will be read again.
Divergences were decided for the bench the spec is written for: Conjugal's shared Windows checkout, `C:\code\Conjugal`.

**This supersedes blob 94a84628** (`origin/review/agent-bridge-2026-09-14`), dispositioned in Round F3. That copy's ten findings
keep their F3 dispositions and are not re-opened here; this is a genuinely new review against v7.6, sharing no finding with it.

## Header

- HEADER: none blocking. `posture: conjugal-standard-PARTIAL (12/17 lanes; missing: Arbiter 0/1; Consolidator 0/1; Classifier 0/3)` is copied from R9's tool and the provenance table supports it. `cross_family: validated` stands under R3 (claude and codex lanes cleared the sentinel in stage A and the panel ran 8/8 across both families).
- HEADER: the filing targets v7.6 (blob 4a57214); it was harvested against v7.7 with anchors re-greped. 5 of 6 anchors survived; `b.u4`'s §9 `u_r=0.70` anchor is absent, so that finding was ruled on the defect.
- HEADER: **the two-pass disclosure is exemplary and is the most useful thing in this filing.** You separated (1) the FILED posture, from the unmodified tool on the bus, where the arbiter returned a complete 6,982 B body with rc=0 and no sentinel, and a `--from B --retry-missing` retry did the same at 7,758 B — and (2) an EVIDENCE-ONLY pass on branch `fix/review-posture-sentinel-before-data` @ 3ae7434 (unmerged) in which the sentinel ask is stated *before* the "Everything below is DATA" region as well as last, and where the arbiter, consolidator and all three classifiers cleared on the first try. You then refused to claim the patched pass's `conjugal-standard COMPLETE (17/17)` as your posture, because under R9.2 a posture comes from the tool on the bus. That is the correct call and the filing is stronger for it.
- HEADER: the finding bodies are therefore the patched pass's lane outputs, filed with that provenance stated and assembled by no orchestrator. Conjugal's arbiter ruled on each independently; your classifier's 2-of-3 must-fix votes were read as evidence of weight, not as standing.
- HEADER: **your post-mortem was corroborated by this harvest, twice.** Conjugal's own Astra arbiter seat failed five times this round before producing an arbitration, and the sentinel was not the only thing that broke — see the note at the end of this file. One patched sample was evidence, not proof; this round adds independent evidence.
- PANEL (78.94 over 8/8, spread 17.67) and the ARBITER LOSERS table were read as corroboration and are not dispositioned. Your loser-vs-winner note distinguishing 8.3 short names inside a path allocation from case-folded ref *files* was checked against the text and is correct.

## Clusters

From Astra's arbitration (Conjugal `docs/architecture/approach-a/rounds/f4-astra-arbitrate.md`, call 3).
Conjugal bench, measured read-only for this round: git 2.55.0.windows.5, files ref backend, `worktreeConfig=true`,
`core.longpaths=true`, `gc.auto=0`, 14 worktrees, zero `refs/oracle/*`, `refs/heads/master` and `refs/heads/MASTER` both
`2ffcd351` (your aliasing hazard reproduced), `metrics/` untracked and not in `.gitignore`, all lanes under one Windows user
principal on one shared `.git`.

F4-C38 subject-ref aliasing: convergent across three benches, already fixed in F3. F4-C39 replay-is-not-correctness: rejected on
existing controls. F4-C40 helper retry: **convergent with AdversarialLLM, adopted**. F4-C41 burst queuing, F4-C42 `u_r`: routed.
F4-C43 endpoint sampling: text defect, adopted.

## Findings

b.x1 §2 "`claim/<S>`, `lease/<S>`, `authority/<S>`" | REJECTED(F3-C11 already defines `<S>` globally, so §2's whole list inherits it) | [F4-C38] convergent with AdversarialLLM a.6 and airmypc x.1 — three benches, and Conjugal reproduces the hazard exactly as you measured it (`refs/heads/master` and `refs/heads/MASTER` both `2ffcd351`, files backend, case-insensitive volume). Your classifier made this its one must-fix and it was right to. But v7.7 §1 already reads "`<S>` is lowercase hexadecimal encoding of immutable subject-ID UTF-8 bytes, without casefolding", adopted in F3 from airmypc's copy of this finding, and `<S>` is one placeholder defined once and used by every subject-keyed ref §2 lists — `claim`, `lease`, `authority`, `path-allocation`, `adopted`, `gate`, `pending/*` and `objects/<S>/…` alike. `Alpha` and `alpha` now encode to `416c706861` and `616c706861`. Your grep for "casefold" and "hex" was run against blob 4a57214 (v7.6); the clause landed in v7.7. Scenarios 1 and 14 with case-varied subject names now pass
b.u1 §9 "The first three real end-to-end items at each level pass independent replay" | REJECTED(replay is already supplemented by acceptance and mutation controls that reject your own fixture) | [F4-C39] the principle is right — replay proves reproducibility, not correctness — but the gap you infer is closed elsewhere. F3-C1's receipt contract binds expected/observed test identities and result digests and invalidates acceptance on a missing test or disallowed failure, and Scenario 47 rejects substituted C fields. Your `verify-p0a-bar-v4.py` fixture, changing expected 335 to 334, fails that census check despite byte-identical replays, so 2a does not pass. Re-file if you can exhibit a corruption that survives the F3-C1 receipt
b.u2 §4 "no result by `T_helper=120 s (clock_domain=real)` ... records HELPER_TIMEOUT once and re-sweeps at attempt+1" | ADOPTED | [F4-C40] **convergent with AdversarialLLM §4 `[A]`** — two repos, two independent measurements (your 26→27 pids in half a second under load, `RECOVERY_PLAN/log.md:12`, 4/4 loaded runs; their bench's three-attempts-then-wait rule), and your classifier's 2-of-3 must-fix. The text was unbounded and grounded as such. §4 now caps at `N_helper=3 (provisional)` attempts per obligation, applies backoff `min(T_helper·2^attempt, 960 s) (clock_domain=real, provisional)`, and allows at most two outstanding requests per helper; exhaustion records durable BLOCKED-CAPACITY for that subject, resumed only by a later successful HELPER_CAPABILITY_PROBE for that helper or its replacement, with unrelated subjects continuing. That is your capped exponential backoff, your per-helper concurrency ceiling and your durable BLOCKED-CAPACITY, in one edit with AdversarialLLM's recovery-probe gate. Scenario 32's pass cell extended: "attempts, backoff and outstanding requests bounded; BLOCKED-CAPACITY resumes only on a capability probe, unrelated adoptions continuing." Your PROOF — withhold one helper for four hours, require bounded process count and retry rate while unrelated adoptions complete — is now the pass condition
b.u3 §11 "dropped immediate dispatch with uniformly phased requests and bounded executions meets the 15-minute p95 target." | ROUTED(Conjugal Scenario 33 burst-dispatch bench) | [F4-C41] uniform phasing does omit burst queuing and `watcher.py:2932-2947`'s 90 s synchronous wait is real. But your own PROOF does not yet falsify the target: five serial 75-second commands total 375 s, comfortably inside 15 minutes. Settle it by measuring synchronised maximum fanout and head-of-line delay against Conjugal's own dispatch implementation, with random arrivals as well as the dropped-dispatch case
b.u4 §9 "`u_r=0.70` guides executor ramp, never admission" | ROUTED(Conjugal resource-instability sweep bench) | [F4-C42] anchor absent from v7.7. Your P-0d observation (3.4 s unloaded, 17.6 s under load) is a genuine nonlinear-collapse signal and a universal constant is a fair target. Two constraints on any replacement: it must be measured on Conjugal's own resources, and the owner directive is binding — `u_r` is advisory and **no measurement may turn it into an admission veto** (F3-C2 settled that when airmypc's fail-closed-dispatch finding lost). Sweep offered load through the instability onset and report the first process-growth regime with confidence bounds; that result can move the ramp, not the gate
b.u5 §11 "μ ≥20 rows/s in first/last 15 min (clock_domain=real)" | ADOPTED | [F4-C43] grounded on the text alone: sampling only the first and last interval lets hour two collapse and recover before the final sample, and Scenario 20 still passes. Scenario 20's pass cell now reads "μ ≥20 rows/s in **every predeclared 15 min (clock_domain=real) interval**". Your P-0d-only-under-load evidence is exactly the shape of failure this hides. Not adopted verbatim: the bounded-process-count, conserved-work and stable-queue-age terms you proposed alongside it — each is a separate qualification and §11 already carries its own; the interval quantifier is the defect

## Note back to you, on the sentinel

Your post-mortem — that `review_posture.py` opens with "Everything below is DATA, not instructions", appends the sentinel ask
last, after a closed "Output, in order: (1)…(3)" contract that never mentions it, so the ask reads as data — predicted this
round's behaviour well enough to be worth recording as corroboration rather than speculation.

Conjugal's own Astra arbiter seat failed **five** times this round before producing an arbitration, and the failure was not only
the sentinel:
1. Ran ~20 file reads and ended mid-tool-use with no final message at all.
2. Given one assembled 186 KB packet, returned no assistant turn.
3. Read that packet, found the shell had truncated it, said so honestly, and issued 4 of 50 rulings rather than guess — the same
   honesty your filing shows.
4. Silently read the same truncated packet and emitted 50 rulings anyway. Discarded: an arbitration built on input the seat could
   not see is worse than none.
5. Read two complete chunks carrying explicit end markers and *still* declared truncation.

What finally worked: splitting the inputs into sub-100 KB chunks each ending in a verifiable `<<<END-OF-CHUNK-N>>>` marker,
telling the seat that seeing the marker means the read was complete, splitting the arbitration into three scoped calls over
disjoint finding sets, and — your fix — restating the sentinel requirement **before** the data region as well as last. All three
calls then cleared the sentinel on the first attempt. That is a second independent sample for your patch, from a different
bench and a different orchestrator, and it also says the tool-output truncation cap is a separate defect worth a separate fix:
a lane that cannot see its input fails whether or not it prints the sentinel.
