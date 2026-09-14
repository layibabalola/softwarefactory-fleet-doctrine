project: airmypc
subject: specs/conjugal-approach-a-v7.4.md (blob b41e3af00b757f96030e5127d170940776362cf0; content is v7.5, Round F1)
test_bench: C:\temp\AirMyPC @ 2e0aa4159c11dd55d96461bc17f711bc75f3a1da (clean detached worktree C:\temp\airmypc-bench)
providers: claude (fable claude-fable-5, opus claude-opus-5, sonnet claude-sonnet-5, haiku claude-haiku-4-5-20251001); codex (astra gpt-6-astra, sol gpt-5.6-sol, luna gpt-5.6-luna) — ~/.claude/machine-inventory.yaml probed 2026-09-14T15:41:56-05:00 under claude-org:b59121b3…
posture: conjugal-standard-PARTIAL (12/17 lanes; missing: Arbiter 0/1; Consolidator 0/1; Classifier 0/3)
cross_family: validated
rubric_id: b2f5862e9c0990d0e69e96862fba7ab4cc5e263151679ac336ab429187341c45
panel: 80.0 over 8/8 seats, 2/2 families (claude, codex), spread 18.5

> **Supersedes** `review/airmypc-2026-09-14` (`2e2966e`, addended `54a1fc5`), which was produced below the review floor with a
> typed posture line. **This filing is PARTIAL and must be read as such.** The Codex arbiter (astra) twice returned a complete
> arbitration body without the closing `LANE-COMPLETE` line, so `run.sh` correctly blocked stages C and D: **no consolidator and no
> classifier ran.** Nothing below is a consolidated finding. The stage-A lane findings are reported as unconsolidated leads with
> verified quotes; the arbiter's rulings are shown for transparency only and carry no standing (R2).

## Design findings

**None consolidated** — the consolidator (fable) did not run because the arbiter did not clear the sentinel.

### Unconsolidated stage-A findings (leads, not rulings)

Every quoted phrase below was checked with `grep -F` against the subject blob (17 of 17 matched). Bench claims re-measured on
2026-09-14 are marked ✓; claims not re-measured are marked ◻.

**Designer-Scope (opus, Claude) — cleared sentinel**

§1 | "`refs/oracle/claim/<S>` points to `{subject, owner, lease_gen, claimed_at, job_id, pid, creation_time, paths_digest}`" | Loose refs are NTFS files and case-collapse: on the bench `git rev-parse refs/heads/WI/CI-20260908` and `refs/heads/wi/ci-20260908` both return `b1404e1` — two subjects differing only in case share one claim ref, so CAS admits both owners | REPLACES: "`refs/oracle/claim/<S>`" -> "`refs/oracle/claim/<S>`, S constrained to lowercase hex so distinct subjects cannot casefold-collide" | PROOF: Scenario 1/14 with subjects `A1` and `a1` on the bench ODB; two claim refs must exist and two distinct owners must be admitted.
§1 | "durable Git object storage with `core.fsync=loose-object,pack,reference` and `core.fsyncMethod=fsync`, verified by every Oracle writer before acknowledgment" | No verification exists on bench git 2.40: `-c core.fsync=zzznotavalue rev-parse` exits 0 (stderr warning only) and every real component is silently accepted, so a writer cannot distinguish honored from ignored durability | REPLACES: "verified by every Oracle writer before acknowledgment" -> "verified by pinning the git executable digest at a version whose `core.fsync` components are known-honored, and by rejecting any stderr `ignoring unknown core.fsync`, before acknowledgment" | PROOF: Scenario 61 under `core.fsync=bogus`; acknowledgment must be withheld — on bench it is not detectable.
§1 | "Mirror updates and relay staging never advance a checked-out branch; only §5 authorized landing integrates into master." | `git worktree list` shows `master` checked out at `C:/temp/AirMyPC` alongside 34 peers on one ODB; landing therefore advances a checked-out branch and desyncs that worktree's 228,729-byte index, which no §5 clause repairs | REPLACES: "only §5 authorized landing integrates into master" -> "§5 landing refuses and records RELAY_CONTENDED whenever master is checked out in any registered worktree" | PROOF: Scenario 72 with master checked out in the main worktree; assert its index and HEAD are unchanged after landing.
§1 | "No claim/vote operation takes `.git/index.lock` (Scenarios 1, 14, 49)." | The named path is the main worktree's index only; the bench has 34 further indexes at `.git/worktrees/*/index`, so the stated invariant is unfalsifiable for 34 of 35 checkouts | REPLACES: "`.git/index.lock`" -> "any `index.lock` under `<git-common-dir>` or `<git-common-dir>/worktrees/*/`" | PROOF: run Scenario 14's CAS storm from `airmypc-bench`; watch for `C:/temp/AirMyPC/.git/worktrees/airmypc-bench/index.lock` births.
§1 | "One `oracle-reduce.py` instance per shared Git object database (§7)" | Bench has `extensions.worktreeConfig = true` and 34 `config.worktree` files, so each checkout under the single reducer identity may override `core.fsync`/`core.fsyncMethod`; one reducer cannot bound durability it does not control | REPLACES: "One `oracle-reduce.py` instance per shared Git object database (§7)" -> "One `oracle-reduce.py` instance per shared Git object database (§7), refusing to start while `extensions.worktreeConfig` is enabled" | PROOF: set `core.fsyncMethod=batch` in one `config.worktree`; the reducer must refuse, else §1 durability is void for that lane.
§2 | "PERMIT, CERTIFICATE and ATTEST_ENVELOPE objects are immutable at `refs/oracle/objects/<S>/<kind>/<state_object_digest>`" | No pruning or packing policy is stated for per-subject immutable refs; the bench already carries a never-pruned `refs/codex/turn-diffs/checkpoints/<64hex>/<64hex>/…` tree reaching 235-char loose-ref paths with `core.longpaths` unset (`git config core.longpaths` exits 1) | REPLACES: "immutable at `refs/oracle/objects/<S>/<kind>/<state_object_digest>`" -> "immutable at `refs/oracle/objects/<S>/<kind>/<state_object_digest>`, packed by a reducer-owned `pack-refs` step under a stated per-subject ref budget and a 200-char path bound" | PROOF: Scenario 14 at 50 subjects on the bench ODB; count loose refs and check claim p95 against its own `≤2.5 s` criterion.

Bench re-measure: ✓ refs `WI/CI-20260908` and `wi/ci-20260908` both resolve to `b1404e1`; ✓ `git -c core.fsync=zzznotavalue rev-parse`
exits 0 with `warning: ignoring unknown core.fsync component` on stderr; ✓ `master` is checked out at `C:/temp/AirMyPC`, whose index is
228,729 B; ✓ 35 worktrees; ✓ `extensions.worktreeConfig=true` with 34 `config.worktree`; ✓ `core.longpaths` unset (rc 1); ✓ the longest
loose ref is 214 characters relative to the common dir and 235 as an absolute path — the lane's "235-char" is the absolute figure.

**Designer-Verify (sol, Codex) — cleared sentinel**

§10 | "**1b-build** implements one vertical slice:" | Construction omits deployment ordering and mixed-version compatibility. Bench `Test-D5AdoptionOrder.ps1 -Sweep` measured 312/720 unsafe partial-adoption orders. | REPLACES: "**1b-build** implements one vertical slice:" -> "**1b-build** deploys one versioned vertical slice only after mixed-version compatibility and adoption-order testing covers reducer, writers, checkers, helpers, adopter, schemas, refs, and policy:" | PROOF: Adapt the bench D-5 sweep to Oracle components; every reachable mixed-version prefix must remain safe and recoverable.
§4 | "acceptance_spec_sha-required runs at C.candidate_commit_oid are independently executed or authenticated" | Authentication does not prove complete execution. Bench `TEST_CLASSIFICATION_20260907.json` negative3 accepted an injected method: 67 passed, no warning; expected counts and census hash were ignored. | REPLACES: "acceptance_spec_sha-required runs at C.candidate_commit_oid are independently executed or authenticated" -> "acceptance runs produce authenticated receipts binding candidate, command, SDK, configuration, environment, exact test FQNs, census hash, TRX hash, exit code, and zero failures or skips" | PROOF: Inject the bench negative3 TRX mutation; adoption must reject it.
§5 | "by 1 when evidence is UNKNOWN or STALE" | Full-rate dispatch bypasses existing fail-closed routing. Bench `AudioMile.ProviderContinuity.psm1:Select-AudioMileProviderRoute` returns `QUEUED_FAIL_CLOSED` unless a provider is both HEALTHY and ADMITTED. | REPLACES: "by 1 when evidence is UNKNOWN or STALE" -> "by the canonical provider-health and burn decision; UNKNOWN or STALE evidence never overrides QUEUED_FAIL_CLOSED" | PROOF: Feed no healthy provider to the bench router and assert Oracle launches zero inference processes.
§10 | "`coordination/oracle/tests/manifest.yaml` holds one row per scenario" | The claimed manifest is absent in the bench, as are `manifest-sum.py`, `oracle-reduce.py`, and `oracle-adopt.py`; zero `refs/oracle/*` exist, so gates are not executable. | REPLACES: "`coordination/oracle/tests/manifest.yaml` holds one row per scenario" -> "`coordination/oracle/tests/manifest.yaml`, required and schema-validated before admission, holds one receipt-linked row per scenario" | PROOF: A fresh bench checkout must enumerate and execute every required manifest row without missing-path failures.
§9 | "`T_m = max(48, 100 / (m × b)) h (clock_domain=real)`" | The expression divides by zero exactly when the bench’s absent `metrics/items.jsonl` leaves baseline b unavailable or zero; later prose does not repair executable evaluation. | REPLACES: "`T_m = max(48, 100 / (m × b)) h (clock_domain=real)`" -> "`T_m = 48 h when M1 is not measured or b≤0; otherwise max(48,100/(m×b)) h`" | PROOF: Evaluate the gate with b=0 and provisional positive b; both must return 48 without error.
§9 | "`sum_j(lambda_j × service_demand(j,r)) ≤ u_r × available_capacity(r)`" | Left-hand units are resource-seconds/hour, while `available_capacity` has no time unit. Bench `Get-AudioMileBurnDecision` explicitly normalizes capacity using `WindowHours` and `MaxIgnitionsPerWindow`. | REPLACES: "`sum_j(lambda_j × service_demand(j,r)) ≤ u_r × available_capacity(r)`" -> "`Σ_j(λ_j[h⁻¹] × d_jr[s]) ≤ u_r × k_r × 3600 s/h`" | PROOF: Rescale an equivalent bench burn window; the capacity verdict must remain invariant.
§9 | "`b=first_adoptions/elapsed_calendar_hours`" | Unweighted items invite workload-mix gains. Bench classification measures 1,171/63/160/16 test methods across tiers 1–4, demonstrating materially heterogeneous verification demand. | REPLACES: "`b=first_adoptions/elapsed_calendar_hours`" -> "`b` is a rate standardized to a pinned baseline workload-stratum distribution, with unmatched strata reported separately" | PROOF: Duplicate only cheap tier-1 subjects; the standardized multiple must not increase.

Bench re-measure: ✓ `tools/AudioMile.ProviderContinuity.psm1` contains `QUEUED_FAIL_CLOSED`; ✓ `Get-AudioMileBurnDecision` with
`WindowHours`/`MaxIgnitionsPerWindow` exists in `tools/Invoke-AudioMileLaneIgnition.ps1`; ✓ `coordination/oracle/tests/manifest.yaml`,
`oracle-reduce.py`, `oracle-adopt.py` and `metrics/items.jsonl` are absent from the bench index, with 0 `refs/oracle/*`;
✓ `docs/reviews/TEST_CLASSIFICATION_20260907.json` exists and contains 1171; ◻ the "negative3 … 67 passed" detail was not located by a
plain search and is not re-measured; ◻ "312/720 unsafe orders" appears in `docs/fleet/ADOPTION_ORDER_EXPERIMENT_20260731.md`, but the
`Test-D5AdoptionOrder.ps1 -Sweep` was **not re-run**.

## Untested

The arbiter output (no standing) moved three stage-A findings here: the §2 immutable-ref packing finding (Designer-Scope), and the
§10 `1b-build` mixed-version and §4 acceptance-receipt findings (Designer-Verify). Their proposed Oracle proofs are unexecuted.

## Cross-section contradictions

Both lint lanes cleared the sentinel. lint-claude (haiku) reported **NONE**; lint-codex (luna) reported two:

- §0: “no database, daemon, service installation” vs §1: “One `oracle-reduce.py` instance … ticks every `200 ms`” and sidecars invoke `--ensure`. §0 must give: permit a long-running reducer process, or §1 must remove it.
- §0: “Tier 2 verifies and attests without writing Oracle state” vs §4: “floor CAS-creates the immutable HELPER_REQUEST ref” and “helper … CAS-creates … HELPER_RESULT.” §0 must give: narrow “without writing” to “without writing authoritative mutable state,” or §4 must stop Tier 2 from writing Oracle refs.

The arbiter output (no standing) KEPT the first (§0 "no … daemon" against §1's continuously ticking reducer) and DROPPED the
second (§4 separates immutable helper-result ingress from reducer publication). Both quoted phrases verified verbatim.

## Arbiter losers

Shown because the fleet reads losers before re-filing — **not adjudicated here**: the arbiter did not clear the sentinel on either
attempt. Each counterexample was read against the subject and cites text present in it (for example "provisional or zero" in §9,
verified verbatim). One counterexample rests on a premise the bench qualifies: the fsync loser calls the unknown-component warning
"detectable evidence" — it is on stderr, but the command exits 0, so a writer that checks only the exit status cannot see it. That
disagreement is recorded as unresolved, not settled.


defect class | loser | counterexample
--- | --- | ---
Case-colliding claim refs | DESIGN-SCOPE §1 case-collapse finding | §1 requires expected-OID CAS, including zero OID for creation; sharing one ref does not establish simultaneous ownership, and the proposed lowercase-only rule would reject its own `A1` proof input.
Durability verification | DESIGN-SCOPE §1 fsync finding | §1 requires writer verification and Scenario 61 explicitly withholds acknowledgment for unsupported settings; the supplied unknown-value warning is detectable evidence, not proof of undetectability.
Checked-out master landing | DESIGN-SCOPE §1 landing finding | §5 explicitly requires authorized normal-index integration under a whole-checkout allocation, defers staged dirt, and Scenario 72 requires preservation of peer index content.
Index-lock coverage | DESIGN-SCOPE §1 index-lock finding | Scenarios S and 14 prohibit any “index.lock birth”; the narrower prose spelling does not make observation of linked-worktree locks unfalsifiable.
Per-worktree durability configuration | DESIGN-SCOPE §1 worktreeConfig finding | §1 requires verification by **every Oracle writer** before acknowledgment; a lane configured with `core.fsyncMethod=batch` fails that requirement without banning the entire configuration feature.
Provider dispatch policy | DESIGN-VERIFY §5 fail-closed routing finding | §5 explicitly permits UNKNOWN quota evidence while authenticated latch evidence parks dependent inference; a quota multiplier of 1 does not clear a latch or waive §3 seat feasibility.
Missing implementation artifacts | DESIGN-VERIFY §10 manifest finding | §10 assigns implementation to 1b-build, while §14 marks scenarios unpassed until receipts exist; missing artifacts in another bench do not contradict a prospective build contract.
Zero-baseline evaluation | DESIGN-VERIFY §9 division-by-zero finding | The same §9 paragraph explicitly assigns provisional or zero `b` the 48-hour floor and absolute rates only.
Resource-capacity dimensions | DESIGN-VERIFY §9 units finding | §5 requires capacity inputs to carry units and rejects incompatible inputs as UNKNOWN; §9 requires every resource-gate term to be such a record.
Workload-mix inflation | DESIGN-VERIFY §9 standardized-baseline finding | §9 requires matched work complexity and matched windows, and Scenario 22 rejects an unmatched baseline; duplicating only cheap subjects violates those existing conditions.
Background reducer consistency | LINT-CLAUDE “NONE” | §0 excludes a daemon while §1 requires the continuously ticking, automatically recovered reducer identified by LINT-CODEX 1.
Tier 2 state ownership | LINT-CODEX 2 | §4 lets helpers publish immutable results but assigns publication of their dispositions and state effects to the reducer.
## Panel

Computed by the tool (composites recomputed from the dimension numbers). Blocker quotes are **not** reproduced because they were not
individually verified against the subject.

seat | family | Timeline Realism | Contract Completeness | Cross-Family Safety | Autonomy Achievement | Throughput Goal | Risk Mitigation | composite
panel-fable | claude | 86 | 85 | 93 | 90 | 85 | 89 | 88.0
panel-opus | claude | 87 | 88 | 94 | 88 | 82 | 90 | 88.17
panel-sonnet1 | claude | 55 | 63 | 83 | 79 | 74 | 79 | 72.17
panel-sonnet2 | claude | 76 | 72 | 85 | 80 | 78 | 75 | 77.67
panel-sonnet3 | claude | 80 | 74 | 86 | 79 | 83 | 85 | 81.17
panel-astra | codex | 68 | 69 | 84 | 81 | 74 | 77 | 75.5
panel-sol | codex | 81 | 79 | 93 | 91 | 90 | 92 | 87.67
panel-luna | codex | 58 | 48 | 87 | 82 | 66 | 77 | 69.67
PANEL COMPOSITE (equal mean of 8/8 seats): 80.0  spread: 18.5  families: claude,codex  missing: none


The first stage-B attempt (archived; same subject blob and bench HEAD) scored 79.62 over 8/8 with spread 14.83. One seat moved
11.5 points between attempts (sol 76.17 → 87.67), which bounds how far a single panel composite should be trusted.

## Classifier consensus

**Did not run** (stage D blocked together with stage C). This filing has no STOPPING signal and no must-fix consensus.

## Provenance

- **Tool:** softwarefactory-fleet-doctrine origin/master `tools/review-posture/run.sh` at `9eeba29`, unmodified, run from a detached
  worktree with no space in its path (`C:/temp/sffd-rerun-airmypc`) under Git Bash (`/usr/bin/bash`); RP_OUT outside the bus.
- **Orchestrator:** this project's interactive session on **Claude Opus 5 (`claude-opus-5`)**, not seated by a PROMPT-B chip. R1 binds
  only a session below the review floor; a same-family Opus adjudication panel of three briefs ruled 2–1 for self-orchestration (the
  dissent preferred a chip). **Independence disclosure:** this session had earlier read the superseded filing and, running on Claude
  Haiku 4.5, had produced it. No text in the finding sections was authored by the orchestrator; it is lane output, copied.
- **Preflight:** `check-account-drift.ps1` ALIGNED; `claude auth status` logged in, firstParty, max; `codex login status` logged in
  (ChatGPT); `tools/check-cli-auth.py` does not exist on the bus and was not run; inventory re-probed with 7 of 7 ids answering the
  sentinel and `probed_under` stamped. A machine launcher defect that killed every Codex lane earlier the same day was removed first
  (TRAPS 2026-09-14, stray npm `node` package).
- **Run 1** (20:42:30Z): stages A and B; arbiter DID-NOT-RUN (rc 0, 6,199 B, no sentinel); stage C blocked. Outputs archived.
- **Run 2** (`--from B`, 20:51:40Z): **reuse of stage A disclosed** — subject blob `b41e3af` and bench HEAD `2e0aa41` re-measured
  unchanged and the bench worktree clean before reuse. Arbiter again DID-NOT-RUN (rc 0, 6,696 B, no sentinel); stage C blocked.

| stage | lane | family | model | rc | bytes | sentinel |
|---|---|---|---|---|---|---|
| A | design-scope | claude | opus | 0 | 4368 | RAN |
| A | design-verify | codex | sol | 0 | 3979 | RAN |
| A | lint-claude | claude | haiku | 0 | 1430 | RAN |
| A | lint-codex | codex | luna | 0 | 585 | RAN |
| B | arbiter | codex | astra | 0 | 6696 | DID-NOT-RUN |
| B | panel-fable | claude | fable | 0 | 755 | RAN |
| B | panel-opus | claude | opus | 0 | 699 | RAN |
| B | panel-sonnet1 | claude | sonnet | 0 | 679 | RAN |
| B | panel-sonnet2 | claude | sonnet | 0 | 748 | RAN |
| B | panel-sonnet3 | claude | sonnet | 0 | 636 | RAN |
| B | panel-astra | codex | astra | 0 | 722 | RAN |
| B | panel-sol | codex | sol | 0 | 666 | RAN |
| B | panel-luna | codex | luna | 0 | 688 | RAN |
| C | consolidator | claude | fable | NONE | 0 | DID-NOT-RUN |
| D | classifier-1 | claude | haiku | NONE | 0 | DID-NOT-RUN |
| D | classifier-2 | claude | haiku | NONE | 0 | DID-NOT-RUN |
| D | classifier-3 | claude | haiku | NONE | 0 | DID-NOT-RUN |

- **Not re-measured:** the D5 adoption-order sweep; the negative3 TRX mutation detail; any Oracle proof (none is executable on the
  bench); the panel blocker quotes.
- **Trap observed (offered, not asserted as fleet law):** the astra arbiter produced a full body and omitted the trailing sentinel on
  both attempts here; MLV-App's same-day run of this tool also left an `arbiter.attempt1.txt` with no sentinel.

## Addendum 2026-09-14 (airmypc) — third arbiter attempt; subject moved

- **Third run** `run.sh --from B --retry-missing` (tool softwarefactory-fleet-doctrine 89da549, same subject blob b41e3af and bench
  2e0aa41, both re-measured) kept every lane that had cleared and re-dispatched only the arbiter: rc=0, 6,173 B, **no sentinel** again.
  The tool's lines are unchanged: `posture: conjugal-standard-PARTIAL (12/17 lanes; missing: Arbiter 0/1; Consolidator 0/1; Classifier 0/3)`,
  `cross_family: validated`. Retries stopped at three; see TRAPS 2026-09-14 (arbiter sentinel omitted 3/3). agent-bridge's same-day
  kernel filing reports the identical missing-arbiter posture.
- **Subject moved:** Conjugal's automated harvest published v7.6 (softwarefactory-fleet-doctrine 4a57214, commit b7126cc) after this review
  of v7.5 ran. The unconsolidated leads above are against v7.5; the steward should read them as leads that may or may not survive into v7.6.
