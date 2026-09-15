# Factory-kernel dogfood filing — agent-bridge (Virtual-Ten)

project: agent-bridge
kernel: fleet-factory-kernel r2
profile: code@r2
instance: filing section "## Instance map" (r2; the r1 map at agent-bridge 3ab6eea is unlanded)
subjects: 0 completed end-to-end; 4 observed-retrospective at a blocked seam (tree c7b370d6, tree 440af74c, sha256 56F1BC6C, sha256 D994D58E)
window: 2026-09-14T06:21Z .. 2026-09-15T01:10Z
health: assurance=UNEVALUABLE operability=PRESSURED
providers: claude (advisory subagents only, no lane sentinel); codex none (SOL NO_VERDICT TOKEN_METER_UNAVAILABLE)
posture: no model review

**What this filing is.** It is the r2 re-run, triggered because the kernel and `profiles/code.md` both moved to r2. It is also a filing at a **blocked work seam**, which PROMPT-K §6 asks for ("the worst failures prevent completions"). The Opus orchestrator session `fcedf1b7` wrote it on Virtual-Ten and ran no subject of its own. agent-bridge's board has no READY class-A card: unattended hub cycle `59076e15` closed with "class-A backlog exhausted". Every class-B and class-C decision has been parked since hub `9fb04fb8` (see K6). The four subjects cited below were produced today by unattended hub cycles. Each line is labelled **OBSERVED-RETROSPECTIVE**: it was recorded afterwards from the WAL, `docs/internal/RECOVERY_PLAN/log.md` and decision receipts, not instrumented while it ran, and none recorded a K5 profile line before work started. None counts toward `subjects:`. Three adversarial Claude Opus agents (one family, no cross-family standing) reviewed the plan for this filing. Their changes were adopted: the orchestrator's draft counted its own instance-map edit as a subject, and they overturned that. They also found the doctrine checkout stale and caught one mislabel. `4795a8f` had been called "accepted"; it is not.

**Every r1 finding has a disposition** (`adjudications/factory-kernel/agent-bridge.dispositions.md`, harvest `20260914T221904Z-51d5a96b`), so the re-run replaces them. The one undisposed r1 item, the harvest-tool `untested` count note, is carried forward under `## Untested`.

## Observed-retrospective subjects (not counted)

| id | identity (K3, code@r2) | recompute | class per agent-bridge `KERNEL.md` | state |
|---|---|---|---|---|
| S1 P-0a-BAR verifier fail-closed | tree `c7b370d6baed7c4d74d36fa9a36c60310a79c9f1` | `git -C <agent-bridge> rev-parse 70c200c^{tree}` | touches `tools/verify-p0a-bar-v4.py`; committed as class A | produced; no independent acceptance |
| S2 P-0a-BAR bar-doc count 335->336 | tree `440af74cef2b75c8410e9567aabbf031d6e3b69a` | `git -C <agent-bridge> rev-parse 4795a8f^{tree}` | doc + verifier; class-B review owed | produced; "awaiting class B and was not flipped" (log.md, cycle 65513b06) |
| S3 F16-A pulse task XML | sha256 `56F1BC6C41B9D093345A336943980F39F48242174437A06EF41F147EB52487D5` | `Get-FileHash` on `.claude-state\coordination\evidence\F16-A-pulse-definition-20260914\agent-bridge-resume-pulse.xml` | registering it is class C | banked, not registered |
| S4 F18 meter first-bind repro | sha256 `D994D58EE12CE6EE2D72711C90A4B79DB48F3E5887D2622B9A50A04120F20E7E` | `Get-FileHash` on `...\evidence\F18-meter-first-bind-repro-20260914\Repro-F18.ps1` | fixture-only, class A; the fix is class C | reproduced 4/4 arms; fix parked |

## Clauses

K1 | UNEXERCISED | "A candidate is never accepted on evidence whose only author is its producer" | no subject reached acceptance this window. S1/S2 were produced and self-read by the same unattended hub cycle; the board did not treat that read as acceptance (S2 stays "awaiting class B") | PROOF: a completed subject whose accepting receipt names its producer

K2 | FRICTION | "Escalation goes to the owner ... only for deadlock, a novel class, high risk, or an irreversible act" | `DECISION-F17-ROUTE-9274013f.json` records a "CONSTITUTIONAL DEADLOCK" and three exits that belong to the owner alone, listed "as facts and not requests". The machine-local autonomy directive forbids ending a turn on a question, so no escalation reached the owner. The deadlock has stood from 2026-09-14 02:10 CDT to at least 19:50 CDT, and later hub cycles re-verified it each time (`codex --version` = 0.154.0, board `KERNEL.md` mtime 09-07). The register itself is still unreachable from the session branch: `git cat-file -e 3ab6eea:docs/internal/OPERATING_MODEL_2026-09-08.md` exits 128, while on `p0a-bar-v4` it exits 0. The board constitution `.claude-state/coordination/KERNEL.md` is gitignored (`.gitignore:24`) and exists only in the canonical checkout | REPLACES: "Escalation goes to the owner ... for deadlock" -> "Escalation goes to the owner ... for deadlock, through a channel the owner reads without starting a session; a deadlock recorded only in project files is not escalated" | PROOF: a recorded deadlock that reached the owner without the owner opening the project

K3 | FRICTION | "One claimant holds a subject at a time, under a lease that expires" | this session claimed the board with `.claude-state\coordination\HubCycleLock.ps1 -Acquire` (`LOCK-ACQUIRED ... softExpiryAt=2026-09-15T02:15:30Z`). The lease expires and names its session, but the `pid` it records (25508) is the short-lived pwsh child that wrote it. `Get-Process -Id 25508` returned nothing moments later. The lease also names no subject. Unattended cycles take and release the same lock, so the only thing that kept this filing's work from colliding with theirs was the lock's existence | REPLACES: none at kernel level (profile line below) | PROOF: a same-host cleanup that identifies the lease holder's live process from the lease alone

K4 | FIT | "Work is complete only on positive evidence it was asked to produce" | the board refused SOL's process exit as a verdict: `DECISION-F16-B-53b04cdd.json` records SOL `NO_VERDICT` with `processOutcome=TOKEN_METER_UNAVAILABLE after 121s` (receipt `lane-receipts/SOL-20260914-011753-215`), and it did not count toward quorum. Negative check made by this session: the fork evidence said "doctrine checkout = origin/master = 7938f05". Two adversaries measured `ls-remote` at `99e7329`, and a fresh fetch then read `6b5759f`, so the claim was withdrawn and this branch was re-based by merge (`8343a6a`) | PROOF: an agent-bridge decision that counted a lane's exit 0 without its sentinel

K5 | UNEXERCISED | "Before work starts, a subject declares its profile and profile version" | S1–S4 recorded no profile line before work, and no subject reached acceptance, so no receipt could bind to an identity | PROOF: a card that carries `profile: code@r2` before dispatch and an acceptance receipt naming the same tree OID

K6 | FRICTION | "Every acceptance includes a key from an independence class other than the producer's" | the clause held, because nothing was accepted without an independent key, and it cost the whole board its B and C throughput. agent-bridge sources its only cross-family key from SOL (`codex exec`). codex-cli 0.154.0 stopped writing the `user_message` rollout lines that the launcher's token meter binds, so SOL cannot produce a verdict. The repair (F17) is class C, and class C needs SOL: `KERNEL.md` "A missing SOL PARKS class-C work rather than downgrading it". Parked: F16-B, F17, the F18 fix, S2's class-B review, S3's registration. Cost: about 18.5 h without a class-B or class-C decision (01:21 to 19:50 CDT) and two route-adjudication rounds. This is not a BREAK. `profiles/code.md` also admits "a CI runner the producer does not control, or an attended human verifier", and the deadlock comes from the instance's single-source key, not from K6 | REPLACES: none at kernel level (profile line below) | PROOF: an agent-bridge class-B decision accepted with a non-SOL independent key during a SOL outage

K7 | UNEXERCISED | "Acceptance and delivery are separate states" | nothing was accepted, so nothing was due for delivery. Instance NONE carried forward: nothing detects an accepted-but-undelivered subject | PROOF: an accepted subject absent from `github/master` with no alarm raised

K8 | UNEXERCISED | "Running out of quota means rotating or parking the work that needs inference" | no quota event occurred (usage read 73% weekly / 73% five-hour by `Get-BoardState.ps1`, report only). The SOL outage is a CLI schema change, not quota, and is filed under K6 and P:code resource-terminals | PROOF: in-flight work state recorded at an agent-bridge quota refusal

K9 | FIT | "Resumability is gated at landing seams, before expensive spend, at the first rate limit and on the status tick" | this session resumed from durable artifacts alone: `RESUME.md`, the WAL by byte offset, `log.md` handoffs, and decision receipts. `Test-ResumeFreshness.ps1 -SelfTest` returned `VERDICT: PASS` (exit 0) at 2026-09-15T00:50Z. It is still not wired as a pre-spend gate (instance map) | PROOF: a session that could not resume the board from the tree without a pasted bootstrap

K10 | FIT | "Account parity is verified before any provider work" | `tools/check-account-parity.py`: `[parity] MATCHED - surfaces agree`. Inventory `~/.claude/machine-inventory.yaml` has `probed_under: claude-org:b59121b3-...`, matching the CLI `orgId`; claude 4 ids, codex 3 ids. Receipt `.claude/doctrine-sync.json` carries `previous_head 607389cd` | PROOF: provider work dispatched before the parity line in the same session

K11 | FIT | "R1–R5, R7, R8 and R9 apply to every report a factory makes about itself" | quoted in PROMPT A §5 of this session: "R1 - A session below the review floor does not review.", "R2 - Completion is positive evidence from the lane, never absence of error.", "R3 - A cross-family claim is computed, not asserted.", "R4 - Every project-scoped reference names its project.", "R5 - Provider and model inventory is machine-scoped and probe-derived.", R6 "the invariant is binding; the implementation is not.", R7 "review branches always push", R8 "work with the bus is left synced", R9 "a posture is named only when it ran in full". No posture is named here because none ran | PROOF: a claim in this filing with no receipt behind it

K12 | FIT | "The steward harvests every filing and answers each one" | the r1 filing was answered within hours (dispositions `009f216`), and the answer changed `profiles/code.md` r2 (Human gates, Claims, Dispatch preflight rows are r1 findings). The r1 K12 ROUTED item (sentinel before DATA) has a fix branch that is still not on master: `tools/review-posture/review_posture.py` on `origin/master` still sets `SENTINEL_ASK` as a trailing line | PROOF: `harvest-status.py factory-kernel` leaving this filing UNHARVESTED past the steward's cadence

P:code resource-terminals | FRICTION | "parked work names its resume condition, and work not requiring the unavailable resource continues" | both halves held. The terminal is typed (`NO_VERDICT TOKEN_METER_UNAVAILABLE`), and class-A work continued (S1, S2, S3, S4). But the only resume conditions named are the three owner exits, and nothing moves any of them to the owner (see K2). A resume condition that exists only in project files and waits on an actor who is never told is a park with no exit. Corroborated on a sibling bench: TRAPS "A hold released by an event the system can never produce is a deadlock" (adobe-ingester, 2026-09-14) | REPLACES: "parked work names its resume condition" -> "parked work names its resume condition and the actor who can satisfy it; a condition only the owner can satisfy is escalated under K2 when the park is recorded" | PROOF: an agent-bridge park whose owner-only resume condition reached the owner the same day

P:code independent-key | FRICTION | "a verifier from another model family (R3), a CI runner the producer does not control, or an attended human verifier" | agent-bridge's instance offers only the first option: SOL via `automation\Invoke-CodexLane.ps1`. One CLI release took out the whole class B and class C path (K6). The profile row does not require an instance to keep a second key class reachable | REPLACES: "a verifier from another model family (R3), a CI runner ..." -> "at least two of: a verifier from another model family (R3), a CI runner ..., an attended human verifier; an instance with one reachable key class declares it" | PROOF: a code bench whose single key class failed with no board-wide stall

P:code claims | FRICTION | "leases name the subject, owner, expiry and owned processes" | `HUB_CYCLE_LOCK.json` written this session names `sessionId`, `softExpiryAt` and a `pid` (25508) that had already exited. It names no subject and no live owned process, so the r2 row is not yet met by this instance. The cost is recorded, not paid, because no cleanup ran this window | REPLACES: "owned processes" -> "owned processes, recorded as the long-lived holder, never the process that wrote the lease" | PROOF: a lease written by a short-lived helper that correctly names the holder's live process

P:code human-gates | FRICTION | "the register is reachable from every session checkout" | not met: exit 128 on `3ab6eea`, and board `KERNEL.md` gitignored (K2 evidence). Cost this window: the orchestrator had to read the canonical checkout by absolute path from a worktree to find the class table | REPLACES: none; the r2 text is right, and the instance does not meet it | PROOF: `git cat-file -e <session-branch>:<register path>` exiting 0 on every live agent-bridge worktree

P:code budgets | FRICTION | "review rounds also report dispositions completed and subject changes, including zero" | today's hub cycles report per cycle in `log.md` with a "Done / Not done" split, which fits. The board-level view (`Get-BoardState.ps1` throughput) reads "OK (8 WAL entries / 15 commits in 24h)" while every class-B/C decision is parked, so entries/commits scored the deadlock as healthy | REPLACES: none at profile level; instance finding | PROOF: a board throughput line that goes non-OK during a class-B/C park

## Instance map

The r2 map, kept in this filing because landing `docs/internal/FACTORY_KERNEL_INSTANCE.md` is a publication to agent-bridge's integration ref (class B or higher), and class B is parked on K6. `NONE` is a finding.

| Clause | agent-bridge mechanism (r2) |
|---|---|
| K1 | roles in `.claude-state\coordination\KERNEL.md` (hub, implementer, adversary, SOL); acceptance by class table |
| K2 | `KERNEL.md` class table + `docs/internal/OPERATING_MODEL_2026-09-08.md` `never_authorized` (on `p0a-bar-v4`, not on every branch); **owner escalation channel for deadlock: NONE** |
| K3 | identity: git tree OID (code@r2); claims: `HubCycleLock.ps1` (expiring, session-named; **subject and live owned process: NONE**) |
| K4 | lane receipts under `.claude-state\coordination\lane-receipts\`, verdict files, `NO_VERDICT` typing in decision JSON |
| K5 | `AGENTS.md` suite with TEMP/TMP exported; **profile line before work: NONE** |
| K6 | SOL via `automation\Invoke-CodexLane.ps1` only; **second key class: NONE** |
| K7 | hub-gated fast-forward to `github/master`; **accepted-but-undelivered detection: NONE** |
| K8 | usage sampled in `Get-BoardState.ps1` (report only, `stopAtWeeklyUsagePct=null`); **quota park of in-flight work: NONE exercised** |
| K9 | `Test-ResumeFreshness.ps1 -SelfTest`, `Get-BoardState.ps1`; **pre-spend wiring: NONE** |
| K10 | `~/.claude/machine-inventory.yaml` (`probed_under`), `check-account-parity.py`, SessionStart `check-account-drift.ps1` |
| K11 | PROMPT A §5 quotes per session |
| K12 | this filing; `harvest-status.py factory-kernel` |

## Untested

- **Whether a non-SOL key would have cleared the board.** This is the P:code independent-key finding. agent-bridge has no CI runner, and no attended human verifier is named in its register, so no bench exists here. PROOF: one class-B decision accepted by a CI runner or a named human during the SOL outage.
- **Harvest-tool `untested` count (carried from r1, no disposition).** `tools/harvest-status.py` counts `untested` only from `§`, `K<n>` and `P:` lines, so bullets in this section still read `untested=0`. Kernel §4 still does not say how Untested items should be written.
</content>
</invoke>
