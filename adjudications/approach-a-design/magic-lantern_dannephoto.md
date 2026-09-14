project: magic-lantern_dannephoto
subject: specs/conjugal-approach-a-v7.4.md (doctrine 9f3b1a9)
providers: claude(opus,haiku) codex(sol,luna,astra) — from ~/.claude/machine-inventory.yaml; auth probes PASS (claude MATCHED fp=b4d2646b85c1; codex "Logged in using ChatGPT")
posture: conjugal-standard
lanes:   design-scope(claude-opus-5) design-verify(gpt-5.6-sol, effort=high)
         lint(claude-haiku-4-5-20251001 + gpt-5.6-luna, effort=high) arbiter(gpt-6-astra, effort=high)
seats: lane orchestrator session claude-opus-5 (ESCALATION-DEPTH 1), dispatched 2026-09-14T03:52:39Z, lanes done 03:58:38Z, arbiter done ~04:00:37Z
rubric_id: unscored

<!-- Test bench: C:\code\magic-lantern_dannephoto. posture computed, not asserted: claude lanes
     design-scope + lint-claude and codex lanes design-verify + lint-codex all emitted the
     LANE-COMPLETE sentinel; arbiter also cleared it. -->

## Design findings (arbiter-surviving; the two reviews had disjoint defect classes, no conflicts to arbitrate)

§5 | "commits the merged blob by private index (`read-tree HEAD`, `commit-tree`, `update-ref` CAS on master's expected tip" | On the bench, HEAD is `codex/audit-remediation-2026-07`, 311 commits ahead of `master` (0b9527e, 2023). A tree built from HEAD and committed onto master squashes those 311 commits into master. The marker then never appears "in HEAD", so the relay re-appends on every tick. | REPLACES: "CAS on master's expected tip" → "CAS on the ref that `git symbolic-ref HEAD` names, refusing a detached HEAD" | PROOF: in a bundle clone, run the relay once. Check `git rev-list --count master` and `git grep "[outbox:1]" HEAD` before and after.

§7 | "Reducer mutex identity is the `.git` directory file identity" | The bench has 4 worktrees. `.claude/worktrees/cool-saha-5e2996/.git` is a gitfile pointing to `.git/worktrees/…`, so each worktree gets a different FileId and its own mutex name. All of them share `refs/oracle/*`, while `coordination/oracle/journal/<lane>.ndjson` resolves to a different file in each worktree. | REPLACES: "the `.git` directory file identity" → "the file identity of `git rev-parse --git-common-dir`, with journals resolved under that common directory" | PROOF: run `--ensure` in the main checkout and in cool-saha-5e2996. Both should get distinct mutexes, and the two worktrees end up with different journal files.

§4 | "Each helper is a fixed-action Windows scheduled task under its dedicated principal" | Every scheduled task on the bench runs as `layib`, LogonType Interactive, RunLevel Limited: "Magic Lantern Lane Supervisor", "Conjugal-Deadman-Luna" and "MlvAgentBachelorWatchdog". `register-lane-supervisor.ps1` sets its principal with `WindowsIdentity.GetCurrent()`. So SEAL (iii)'s "different custody principals" is met by label only. | REPLACES: "under its dedicated principal" → "under a dedicated Windows SID distinct from every lane runner's, checked at QUALIFY; enrolling a helper whose SID matches a runner's fails lint" | PROOF: enroll all four helpers on the bench. Lint must reject them, because every `Principal.UserId` is `layib`.

§4 | "CAS-creates (zero OID expected) the immutable HELPER_RESULT `refs/oracle/global/helper-result/<request_id>`" | On the bench, refs are loose files plus `.git/packed-refs`, writable by the same `layib` SID that runs every lane. Any runner can create that ref first with junk. The real helper's zero-OID CAS then fails forever, and a floor can take `helper-request` the same way ("first nonce wins"). | REPLACES: "`refs/oracle/global/helper-result/<request_id>`" → "`refs/oracle/global/helper-result/<request_id>/<helper key_id>`, the reducer ignoring any entry not signed by the assigned principal" | PROOF: create the ref from a lane shell before the helper writes. The request should loop on HELPER_TIMEOUT and never reach ATTEST.

§2 | "The ignition wrapper starts `oracle-lease-sidecar.py --subject S --pid P --job J`" | On the bench, work is done in sessions the owner runs by hand, not processes a wrapper starts. `coordination/health/leases/opus.json` shows `leaseMinutes:0` and "Owner-interactive, NO self-wake cron". The continuation in `execution-state.json` is a Codex `send_message_to_thread` task. No PID or Job Object exists for renewal to match. | REPLACES: "The ignition wrapper starts" → "Only executors launched by the ignition wrapper may claim; interactive sessions submit candidates through a wrapped executor. The wrapper starts" | PROOF: try to CLAIM from the Codex thread. There is no Job J, so renewal fails at the first RENEW.

§1 | "A non-authoritative mirror copies `verdicts.csv` to master" | On the bench, master is the 2023 upstream tip and the work branch is a 311-commit descendant of it. Each mirror commit would make master and the work branch diverge, adding an unplanned merge on top of the relay defect above. | REPLACES: "to master" → "to policy `mirror_ref`, which must not be an ancestor of the integration branch" | PROOF: after one mirror commit on a bench clone, `git merge-base --is-ancestor master HEAD` returns 1.

§0 | "produces, verifies and adopts work on one shared Windows checkout, `C:\code\Conjugal`, using git refs" | The bench's accepted authority lives outside the repo. `roadmap/recovery/transaction-contract.md` says "State initialization rejects paths inside the candidate repo", and `execution-state.json` already records DONE `accepted_commit` rows (B01 76d8c26, P01 2681d2c). The spec has no import step, so dependents of those tasks can never satisfy `ready_effective`. | REPLACES: "using git refs" → "using git refs; genesis imports each existing ledger's accepted_commit rows as pinned certificates, after which that ledger is read-only" | PROOF: admit a subject depending on P01 on the bench. Its readiness check fails because `refs/oracle/authority/P01` does not exist.

§7 | "with zero leased executors `1,020 s (clock_domain=real, provisional)` (floor wakes only" | The only Magic Lantern floor, "Magic Lantern Lane Supervisor", is `Disabled`; the opus lease says it has been off since 2026-08-18. Yet the spec still publishes the target as if it were bounded. | REPLACES: "with zero leased executors `1,020 s" → "with zero leased executors, UNBOUNDED unless the floor task is Ready and last ran within 900 s; otherwise `1,020 s" | PROOF: `Get-ScheduledTask` on the bench shows State=Disabled, so the 1,020 s target cannot be met.

§9 | "saturation experiments maintain an implementation input backlog." | roadmap/recovery/execution-state.json reports eligible_cards=0 and no active workers; manufacturing backlog repeats HANDOFF.md’s documented control-plane-work failure. | REPLACES: "saturation experiments maintain an implementation input backlog." → "Saturation experiments consume only pre-existing owner-authorized eligible work; without it, record INSUFFICIENT and dispatch nothing." | PROOF: Start G-MEASURE from current bench state; assert zero new subjects and provider calls.

§9 | "`b=first_adoptions/elapsed_calendar_hours`." | execution-state.json is waiting_external with five blocked cards; calendar-time b decays during input starvation, allowing later multiples to rise without added factory capacity. | REPLACES: "`b=first_adoptions/elapsed_calendar_hours`." → "Report calendar delivery rate separately; capacity baselines use hours having owner-authorized eligible input." | PROOF: Compare ratios including versus excluding the bench’s waiting_external interval; capacity qualification must remain invariant.

§9 | "An item is one subject first receiving an authorized ADOPTED record for its exact candidate" | This counts 11 completed desk/factory cards although roadmap/recovery/STATUS.md says the package is neither hardware acceptance nor release and five outcomes remain externally blocked. | REPLACES: "An item is one subject first receiving an authorized ADOPTED record for its exact candidate" → "An adoption and an owner-valued delivered outcome are separate counters; throughput claims state which they measure." | PROOF: Recompute bench results; adoption count is 11 while hardware/release delivery count remains zero.

§5 | "`executors=5 (provisional)`, from the first real minute in both budget modes" | Bench summary has eligible_cards=0 and no_implementation_workers_active=true; automatic five-executor admission violates its proven stop condition and wastes capacity without owner-valued work. | REPLACES: "`executors=5 (provisional)`, from the first real minute in both budget modes" → "Admit at most five executors, bounded by owner-authorized eligible subjects; zero eligible subjects admits zero executors." | PROOF: Run admission against execution-state.json; executor count must remain zero.

§4 | "signing ADOPT_REQUEST only after its own independent replay agrees." | Replay proves control-state consistency, not test execution: roadmap/recovery/CONTINUE.md rejects model PASS alone, and tools/roadmap/recovery-transaction.py explicitly treats check argv as metadata. | REPLACES: "signing ADOPT_REQUEST only after its own independent replay agrees." → "Sign only after replay agrees and the pinned risk-class acceptance evidence has been independently executed or authenticated." | PROOF: Supply self-consistent fabricated PASS logs; adoption must reject them without authenticated execution receipts.

§3 | "two eligible, independently implemented, cross-family A checks agreeing on the certificate's digests" | Uniform quorum discards the proportional verification policy adopted in audit-packet/60-owner-autonomous-recovery-20260907.md, which reserves full R4/hardware evidence for high-risk classes. | REPLACES: "two eligible, independently implemented, cross-family A checks agreeing on the certificate's digests" → "Attestation satisfies the pinned risk-class evidence profile; firmware, hardware, and release profiles retain their full independent gates." | PROOF: Classify a docs-only bench commit and a firmware commit; require proportional checks for the former and full R4 for the latter.

§4 | "Default `live-sol` runs oracle-adopt.py through Sol's existing native floor runner" | The bench has zero oracle-adopt.py files and no coordination/oracle directory; coordination/PROMPT-SOL-ARCHITECT.md defines Sol differently, while execution-state.json names the recovery coordinator as integrator. | REPLACES: "Default `live-sol` runs oracle-adopt.py through Sol's existing native floor runner" → "The adopter is a policy-selected, bench-proven integration writer with a tracked executable entry point and verified custody." | PROOF: Cold-start from tracked bench files and adopt one fixed candidate; the configured adopter must be discoverable and executable.


## Untested

§2 | "receipt commits at `refs/oracle/receipts/<receipt_seq>`" | One ref per receipt with no pruning rule means refs grow without bound. The bench has only 7 loose refs plus packed-refs, so the growth could not be measured there. | REPLACES: "receipt commits at `refs/oracle/receipts/<receipt_seq>`" → "receipt commits chained under the single ref `refs/oracle/receipts`" | PROOF: Stage S at 50,000 frames, measuring `git for-each-ref` latency.

## Cross-section contradictions (lint)

- §0 “Tier 2 verifies and attests without writing Oracle state” vs §4 “CAS-creates the immutable HELPER_RESULT `refs/oracle/global/helper-result/<request_id>`.”  
  Must give: §0 must clarify that immutable helper-result publication is permitted, or §4 must stop helpers from writing Oracle refs.

- §2 registry: “ATTEST_REQUEST; ADOPT_DISPATCH … `C+E-seat+L·event`” vs §4 SEAL transaction: “publishes … the durable ADOPT_DISPATCH row” under “`S+C+E-seat+L`.”  
  Must give: §2’s registry entry must add the `S` fence for ADOPT_DISPATCH, or §4 must remove it.


## Provenance

| lane | model | rc | bytes | sentinel | contributed |
|---|---|---|---|---|---|
| design-scope | claude-opus-5 | 0 | 5897 | RAN | first 9 findings above (§5 relay, §7 mutex, §4 principal, §4 helper-result squat, §2 ignition, §1 mirror, §0 genesis import, §7 floor bound, Untested §2 receipts) |
| design-verify | gpt-5.6-sol | 0 | 4316 | RAN | last 7 design findings (§9 backlog, §9 b, §9 item, §5 executors, §4 replay, §3 quorum, §4 live-sol) |
| lint-claude | claude-haiku-4-5-20251001 | 0 | 1905 | RAN | **zero contradictions reported** — cleared the sentinel but returned a null result while lint-codex found two. Treat the Claude lint slice as weak coverage, not as a clean bill. |
| lint-codex | gpt-5.6-luna | 0 | 609 | RAN | both contradictions above |
| arbiter | gpt-6-astra | 0 | 10197 | RAN | kept all 16 design findings; no conflicting defect classes |

Orchestrator verification (not lane testimony): every quoted spec anchor above was grep-confirmed
present in `specs/conjugal-approach-a-v7.4.md` at 9f3b1a9. Bench facts re-measured by the orchestrator
2026-09-14 ~04:00Z: branch `codex/audit-remediation-2026-07` is 311 commits ahead of `master`
(0b9527e, 2023-02-03); `git worktree list` = 4; `roadmap/recovery/execution-state.json` has
`status: waiting_external`, `eligible_cards: 0`, `no_implementation_workers_active` present;
`coordination/oracle/` and `oracle-adopt.py` absent; scheduled tasks "Magic Lantern Lane Supervisor"
(Disabled), "Conjugal-Deadman-Luna", "MlvAgentBachelorWatchdog" all `UserId=layib`, Interactive,
Limited. NOT re-measured: the "11 completed cards" and "five blocked cards" counts, the
`STATUS.md`/`CONTINUE.md`/`recovery-transaction.py` characterisations, and `register-lane-supervisor.ps1`'s
use of `WindowsIdentity.GetCurrent()` — those rest on lane testimony.

Run defect disclosed: a first dispatch at 03:51:46Z carried a broken subject path (`…doctrine$SUBJECT`,
a shell-escaping error in the runner). It was killed within ~1 min, before any lane output, and all
of its processes were terminated; the run above is the second dispatch with a prompt-binding check added.
