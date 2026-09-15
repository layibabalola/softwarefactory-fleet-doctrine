# Factory-kernel dogfood filing — adobe-ingester (Adobe Document Cloud Ingester, virtual-ten) — re-run on kernel r2

project: adobe-ingester
kernel: fleet-factory-kernel r2
profile: code@r2
instance: none landed (adobe-ingester adoption DEFERRED by Sol, HUB 2026-09-14T22:11:45.942Z); auditor evidence map at .claude-state/kernel/INSTANCE-MAP-fleet-factory-kernel-r1.md (git-excluded, evidence only)
subjects: 0 closed end-to-end; 1 blocked at acceptance closure — WO-G0-A01 rev13 (reviewed commit adobe-ingester 64a99e4ae202e6ea5497e08830d37d3f19543da2, candidate manifest SHA-256 9A2CBC6D48543FEC03C0EDA849309977EC10FD0EF8E6237EBC1FDF29E559DA66), whose repair ballot Q-034 rev4 is at Phase B hold
window: 2026-09-14T22:00Z .. 2026-09-15T00:45Z
health: assurance=UNSATISFIED operability=PRESSURED
providers: none
posture: no model review

**Re-run under PROMPT K's cadence rule.** The kernel moved r1 → r2 in `ec32d6e`, and the steward's dispositions left
three obligations: re-run after the `f6e1972` guards, show the K9 checkpoint repaired, and fix the header. All three are
answered below.

**Header correction.** The r1 filing's `## Untested` section was drafted with three read-only Claude Opus agents. It
should not have been listed as `posture: no model review`. That section has been fully dispositioned and is not
carried forward. Every line in this re-run comes from the auditor's own direct measurements, so `no model review` is
now accurate. Model agents were consulted only on which actions this session should take, and none of their output is
filed as a finding.

**Adoption:** `KERNEL: DOGFOOD-PENDING adobe-ingester Sol hub ratification`, DEFERRED by Sol. Nothing is written to
`specs/adobe-ingester.md` beyond the measured seam note.

## Clauses

K1 | FIT | "A candidate is never accepted on evidence whose only author is its producer" | adobe-ingester Q-034 rev4 Phase A: Sol's `2026-09-15T00:32:52.629Z` reconciliation counts only owner-written votes read directly from each lane log (Luna 1 APPROVE; Opus 0, Sonnet 0). Execution stays `execution_authorized=false` until the independent reviewers vote | PROOF: an adobe-ingester quorum close counting a vote not present in its owner's log

K2 | FIT | "goes to the owner for decisions reserved by that register" | adobe-ingester: OWNER DIRECTIVE 2026-09-14a was delivered through the register's standing-delegation channel and appended verbatim to sol.md with a same-commit re-pin (HUB `2026-09-14T23:00:53.664Z`, `23:03:54.663Z` AB6BE10). The earlier relay was misfiled into Sol's outbound `requests.jsonl` and correctly never counted (0 deliveries for 2 days) | PROOF: an adobe-ingester directive executed without a v2 PROPOSAL binding its path and hash

K3 | FIT | "the command that recomputes it from the artifacts" | `pwsh -NoProfile -File .factory/tools/Test-FactoryCandidateIntegrity.ps1` → `candidate_manifest_sha256=9A2CBC6D…DA66`, unchanged across the window (2026-09-15T00:4xZ) | PROOF: a different manifest digest at reviewed commit 64a99e4

K4 | FIT | "Capability, configuration, enabled state and actual execution are four different facts" | Negative check. Six adobe-ingester Scheduled Tasks showed State `Ready` with on-time runs while exiting 125, because they pinned the prior pwsh SHA-256 362A356C… against the installed BFB46AF8… (HUB `2026-09-14T22:11:45.942Z`; census 2026-09-15T00:30Z; TRAPS on bus `e1be872`). Nothing counted those runs as execution | PROOF: any adobe-ingester health surface reporting those tasks healthy from `Ready`

K5 | FRICTION | "Accepted means that profile's acceptance evidence exists for that exact subject identity" | WO-G0-A01 rev13 closure still blocked, because its binding pinned a HUB byte offset later re-framed (now a code r2 rule). Cost continues: acceptance has not closed since 2026-09-10T09:29Z (~4.6 days); the repair ballot is Q-034 rev4 | REPLACES: none new (code r2 adopted the r1 replacement) | PROOF: a WO-G0-A01 rev13 acceptance binding by content digest committed without a new review

K6 | FIT | "Every acceptance includes a key from an independence class other than the producer's" | Q-034 rev4 still requires Opus and Sonnet (Claude) against Sol and Luna (Codex). Phase B waits instead of substituting a key (HUB `2026-09-15T00:32:52.629Z`) | PROOF: a rev4 execution with no Claude vote

K7 | UNEXERCISED | "Accepted is not delivered" | No delivery was attempted in this window | PROOF: n/a

K8 | FIT | "work that needs an unavailable key parks under a typed terminal with a named resume condition" (code r2 resource terminals) | Q-034 rev4 Phase B is `CAPACITY HELD`. It names its resume condition ("a fresh exact identity-bound recovery_resolution_ready=true after lawful recovery-control remediation") and its cause (`recovery_manifest_invalid`, installed recovery-common 8A36F70F… vs admitted 6F441054…). Non-review work continued: the Luna vote, the pin generation `c622832`, the prompt re-pin `AB6BE10` | PROOF: an adobe-ingester reviewer start while recovery_resolution_ready=false

K9 | FIT | "failed or stale checkpoints name their last passing time and resume condition" (code r2 dispatch preflight) | Obligation answered. `AdobeIngesterFactory-ResumeCheckpoint` LastTaskResult 0 at 2026-09-14 19:34:34 CDT; `CHECKPOINT-CURRENT.md` generated 2026-09-15T00:34:33Z, expires 01:04:33Z. It was dead 2026-09-12T17:04Z → 2026-09-14 and its failure named the last passing time | PROOF: a CHECKPOINT-CURRENT.md older than its 30-minute TTL while the task reports 0

K10 | FIT | "Account parity is verified before any provider work" | virtual-ten `check-account-drift` ALIGNED; plan usage sampled (5h 53%, weekly 68%) before this session dispatched any model agent | PROOF: a model dispatch in this window preceding the parity sample

K11 | FIT | "R1–R5, R7, R8 and R9 apply to every report" | This re-run corrects the r1 header's posture line (see above), and states measured times from `(Get-Date).ToUniversalTime()` and trusted-UTC receipts | PROOF: a line in this filing whose timestamp contradicts its cited ledger heading

K12 | FIT | "Kernel text must not assume … a project tree that fleet tooling may write into" (§3, r2) | Obligation answered. This PROMPT A + PROMPT K run under the `f6e1972` guards wrote nothing inside the adobe-ingester tree. `git status --short` lists only the three lane logs Sol and the lanes own, and `Test-FactoryGovernance.ps1` exits 0 (2026-09-15T00:4xZ). The readiness receipt is at `<home>/.claude/doctrine-sync/Adobe Document Cloud Ingester.json` | PROOF: an untracked path under the adobe-ingester root attributable to a fleet prompt after 2026-09-14T21:45Z

## Profile lines

P:code acceptance-evidence | FRICTION | "Bind durable acceptance receipts by content digest; log offsets are locators only" | adobe-ingester's existing rev13 binding predates the rule and remains unclosable without re-review (K5) | REPLACES: none new | PROOF: see K5

P:code resource-terminals | FIT | "parked work names its resume condition, and work not requiring the unavailable resource continues" | Q-034 rev4 Phase B hold (K8) | PROOF: see K8

P:code dispatch-preflight | FIT | "failed or stale checkpoints name their last passing time and resume condition" | K9 | PROOF: see K9

P:code human-gates | FIT | "classifies fleet-tool writes, including permitted locations" | adobe-ingester writes fleet receipts only outside its tree (K12); the register itself is still spread across FACTORY.md, ADR-0003/0004 and owner-directives, and Sol has not ratified an explicit row for fleet-tool writes | PROOF: a fleet-tool path inside the adobe-ingester tree admitted without a Sol entry

## Untested

- Stalled-state observable (routed here as §U7). Candidate observable: `Test-FactoryDispatch.ps1` `adjudication_age_minutes`, which read 10493 at 2026-09-15T00:4xZ while `health` could say only `PRESSURED`. It has not been tested as an enum value yet; filed for the next re-run once it has a threshold with a counterexample.
