# Factory-kernel dogfood filing — adobe-ingester (Adobe Document Cloud Ingester, virtual-ten)

project: adobe-ingester
kernel: fleet-factory-kernel r1
profile: code@r1
instance: .claude-state/kernel/INSTANCE-MAP-fleet-factory-kernel-r1.md (adobe-ingester, git-excluded auditor draft; reproduced below under ## Instance map)
subjects: 0 closed end-to-end; 1 blocked at acceptance closure — WO-G0-A01 rev13, reviewed commit adobe-ingester 64a99e4ae202e6ea5497e08830d37d3f19543da2, candidate manifest SHA-256 9A2CBC6D48543FEC03C0EDA849309977EC10FD0EF8E6237EBC1FDF29E559DA66
window: 2026-09-07T00:00Z .. 2026-09-14T22:00Z
health: assurance=UNSATISFIED operability=PRESSURED
providers: none
posture: no model review

**Adoption status: `KERNEL: DOGFOOD-PENDING adobe-ingester Sol hub ratification`.** This project's bus spec says adoption
happens "only via the ingress and ordinary quorum" (`specs/adobe-ingester.md`, Distinguishing carve-outs). So the
`KERNEL:` line is not written there, and the request went to Sol through the advisory ingress. This filing is
operational evidence, measured by the project's seatless auditor session from the filesystem. It is not a review
(R1). No lane cleared a review sentinel for it (R3), and no posture ran (R9). The `## Untested` advisory section was
drafted with three read-only Claude Opus agents, all one family, and claims no cross-family standing.

The kernel header reads `r1`, but doctrine `45f4a2c` changed §5 text ("Harvest runs continuously") without incrementing
it. This filing ran against the text at `45f4a2c`.

## Clauses

K1 | FIT | "A candidate is never accepted on evidence whose only author is its producer" | adobe-ingester `FACTORY.md` "Separation of duties": Luna implements, "Luna does not approve its own work"; Opus+Sonnet read-only reviewers; Sol accepts only after both reviews exist. WO-G0-A01 rev13 acceptance record binds both independent report blobs (HUB `2026-09-10T09:13:43.995Z SOL — TRANSITION WO-G0-A01 REVIEWING -> ACCEPTED`) | PROOF: an adobe-ingester acceptance binding whose report blobs were written by the implementing lane

K2 | FRICTION | "Each project keeps one register of what needs the owner and what does not" | adobe-ingester's register is spread over `FACTORY.md` "Autonomous safety invariants", ADR-0003, ADR-0004 and `.claude-state/coordination/owner-directives/`. None classifies files written by fleet tooling. Measured cost: one untracked fleet receipt became `OWNER_DECISION_REQUIRED` and held every orchestrator commit about 3h50m (HUB `2026-09-14T17:41:41.619Z SOL — PREFLIGHT FAILURE Q-034 rev3`, plus 7 checkpoints to `21:31:16.592Z`) | REPLACES: "Each project keeps one register" -> "Each project keeps one register, including how files written by fleet tooling are classified" | PROOF: a governed project with such a row runs PROMPT A mid-review without an owner-decision entry

K3 | FIT | "A subject's identity is a content digest over its declared artifact set" | adobe-ingester identity is reviewed commit + candidate manifest SHA-256; recompute: `pwsh -NoProfile -File .factory/tools/Test-FactoryCandidateIntegrity.ps1` prints `manifest_sha256=9A2CBC6D…DA66` (exit 0, 2026-09-14T21:4xZ). Identity is two digests, not the §2 single sha256-over-components form; no cost measured | PROOF: the manifest recomputes to a different digest at the same reviewed commit

K4 | FIT | "Capability, configuration, enabled state and actual execution are four different facts" | Negative check 1: adobe-ingester's 09-10 ACCEPTED transition was refused as an acceptance claim when its real-HEAD postflight failed ("not a canonical acceptance claim unless that real-HEAD postflight … pass", same HUB entry). Negative check 2: Scheduled Task `AdobeIngesterFactory-ResumeCheckpoint` reports State=Ready, but LastTaskResult=125 and its checkpoint was last generated 2026-09-12T17:04:33Z | PROOF: any adobe-ingester status surface that reports that heartbeat healthy from its Ready state

K5 | FRICTION | "Accepted means that profile's acceptance evidence exists for that exact subject identity" | adobe-ingester's acceptance binding (`.factory/acceptance/WO-G0-A01-rev13.binding.json`) binds the exact commit, tree and manifest, and also a HUB byte range (offset 7029615, length 1302). A later ledger append was re-framed with CRLF, so the same disposition now parses as length 1306 and the binding rejects. The first 1302 bytes are unchanged (HUB `2026-09-10T09:29:58.162Z SOL — QUORUM_PROPOSAL Q-034 … POSTGENERATION-REPAIR rev1`). Measured cost: acceptance has not closed since 2026-09-10T09:29Z (about 4.5 days, Q-034 rev1→rev3, terminal TWO_OF_FOUR). No profile id is declared before work, because the project has no profile concept | REPLACES: "acceptance evidence exists for that exact subject identity" -> "acceptance evidence exists for that exact subject identity, and binds content digests, never offsets into a log that can be re-framed" | PROOF: a binding by byte offset that survives a line-ending re-frame of its ledger

K6 | FIT | "Every acceptance includes a key from an independence class other than the producer's" | adobe-ingester producers are Codex (Sol gpt-5.6-sol, Luna gpt-5.6-luna); reviewers are Claude (Opus, Sonnet); the product gate AC-07 is an attended human login | PROOF: an adobe-ingester acceptance whose only keys come from the Codex backend

K7 | FIT | "It closes as one transaction, or it reports CLOSURE_INCOMPLETE and blocks conflicting deliveries" | adobe-ingester WO-G0-A01 rev13: record and binding held in machine-local custody at exact hashes. The transition failed "before ref movement", HEAD and index stayed REVIEWING, and nothing half-closed (HUB `2026-09-10T09:29:58.162Z`). The project's token is not `CLOSURE_INCOMPLETE`, but the behaviour matches. Delivery target for this Gate-0 feasibility work is a decision, not a merge; see `P:code delivery-target` | PROOF: an adobe-ingester state.yaml showing ACCEPTED with no committed acceptance binding

K8 | FRICTION | "Running out of quota means rotating or parking the work that needs inference, never failing the factory closed" | adobe-ingester: governance changes need reviewer votes, and reviewer capacity/identity was lost. HUB `2026-09-10T10:15:06.532Z SOL — EXTERNAL_CAPABILITY_UNAVAILABLE Q-034 rev2 | OPUS AUTH-IDENTITY PREFLIGHT | BOTH REVIEWER ATTEMPTS CONSUMED | NO QUORUM`; `Test-FactoryDispatch.ps1` exit 2 `adjudication_age_minutes=10310`; Luna `WAITING_FOR_READY_WORK_ORDER`; reviewer run receipts about 3145 min old at 2026-09-14T21:4xZ. Parking was lawful, but nothing else could proceed, because the scarce resource *is* the independent key (K6) | REPLACES: "never failing the factory closed" -> "never failing it closed silently: work that needs an unavailable key parks under a typed terminal with a named resume condition; other work continues" | PROOF: an adobe-ingester window in which reviewer capacity was lost and a non-review work order still advanced

K9 | FRICTION | "A fresh session on a new account, with empty memory, resumes from the project's tree and the bus alone" | adobe-ingester `.claude-state/RESUME.md` (pointer-only, 200-line cap) worked for this session. But the resumability heartbeat's last passing output is 2026-09-12T17:04:33Z (task exit 125 since then; `Repin-ResumeCheckpointTask.ps1 -Verify` reports the source pin MATCH, so the documented cause is excluded). Cost: this session derived state by hand in roughly 15 tool calls | PROOF: a fresh adobe-ingester CHECKPOINT-CURRENT.md generated after 2026-09-12T17:34Z by the scheduled task

K10 | FIT | "Account parity is verified before any provider work" | virtual-ten: `check-account-parity.py` `MATCHED` (fp b4d2646b85c1); `~/.claude/machine-inventory.yaml` generated 2026-09-14T15:41:56-05:00 with a `probed_under` identity recorded (not reproduced here) | PROOF: an inventory on this machine with `probed_under: unknown`

K11 | FRICTION | "R1–R5, R7, R8 and R9 apply to every report a factory makes about itself" | This session's own first pass (a Haiku model) printed wall-clock stamps about 8 hours early and wrote one into the readiness receipt. It was corrected in-session against `(Get-Date).ToUniversalTime()`. adobe-ingester `FACTORY.md` "Evidence standard" already requires labelled observations; the defect was in a fleet-bootstrap session outside that contract | REPLACES: "apply to every report a factory makes about itself" -> "apply to every report a factory makes about itself, including reports by fleet-bootstrap sessions running in the project" | PROOF: a fleet-bootstrap receipt in any project whose `synced_at` disagrees with the commit or clock evidence it cites

K12 | BREAK | "Every project that runs the kernel files what happened" | Counterexample from this repo. The route to filing (PROMPT A §2b in-tree receipt, then PROMPT K §2 in-repo instance map) cannot be followed by a governed project with a frozen candidate without halting it. adobe-ingester HUB `2026-09-14T17:41:41.619Z SOL — PREFLIGHT FAILURE Q-034 rev3 | SHARED WORKSPACE UNREVIEWED DOCTRINE RECEIPT | OWNER_DECISION_REQUIRED` and 7 later checkpoints. Resolved by the producing session withdrawing the file; governance exit 0 afterwards. Prompt guards landed on master in doctrine `f6e1972` | REPLACES: kernel §3 list "Kernel text must not assume: … a software delivery target." -> add "a project tree that fleet tooling may write into" | PROOF: PROMPT A and PROMPT K at `f6e1972` or later, run in adobe-ingester during an open review order, leave `Test-FactoryGovernance.ps1` at exit 0

## Profile lines

P:code subject-identity | FIT | "git tree OID of the candidate commit" | adobe-ingester reviewed commit 64a99e4… plus manifest digest (K3) | PROOF: see K3

P:code acceptance-evidence | FRICTION | "the project's pinned acceptance runs at the exact commit" | adobe-ingester binds acceptance to reports plus a HUB byte range, and that binding broke on re-framing (K5) | REPLACES: add "bound by content digest, not log offset" | PROOF: see K5

P:code independent-key | FRICTION | "a verifier from another model family (R3) or a CI runner the producer does not control" | adobe-ingester's product gate AC-07 is an attended, user-present headed login, a human key this field cannot name. `hardware-in-loop` already names "the human operating it" | REPLACES: add "or an attended human sitting that the register names" | PROOF: an adobe-ingester AC-07 receipt accepted without a human present

P:code delivery-target | FRICTION | "integration branch via the project's landing path" | adobe-ingester is a Gate-0 feasibility factory: "a well-evidenced stop is a successful outcome" (`specs/adobe-ingester.md` Shape). Its terminal deliverable is a go/stop decision record, and the delivery plane is deliberately not built before Gate 0 | REPLACES: add "or, for feasibility work, the owner decision record (as in `business-strategy`)" | PROOF: an adobe-ingester Gate-0 outcome that required an integration merge to count as delivered

P:code human-gates | FIT | "releases, security-sensitive paths, frozen bytes, and anything the project's register lists" | adobe-ingester AC-07 credential and MFA entry is owner-only and never automated (`FACTORY.md` "User-presence handshake") | PROOF: an automated AC-07 attempt in adobe-ingester's ledger

## Instance map

(adobe-ingester paths. Status is from 2026-09-14; all read-only observations.)

- K1: `FACTORY.md` "Separation of duties"
- K2: `FACTORY.md` "Autonomous safety invariants" + ADR-0003 + ADR-0004 + owner-directives. No single register; **NONE** for fleet-tool writes
- K3: `.factory/tools/Test-FactoryCandidateIntegrity.ps1`; single writer per coordination log; one active Luna work order. **NONE** for an expiring lease on a subject
- K4: `FACTORY.md` "Evidence standard"; `%LOCALAPPDATA%/AdobeIngesterFactory/receipts/*.json`
- K5: `FACTORY.md` "Acceptance policy"; `.factory/acceptance/<wo>-rev<N>.binding.json`. **NONE** for a declared profile id
- K6: Codex producers vs Claude reviewers; AC-07 human key
- K7: `ACCEPTED -> INTEGRATED` closure merge (delivery plane deferred until Gate 0)
- K8: `FACTORY.md` "Reviewer capacity recovery"; task `AdobeIngesterFactory-ReviewerCapacityRecovery` (Disabled)
- K9: `.claude-state/RESUME.md`; task `AdobeIngesterFactory-ResumeCheckpoint` (exit 125 since 2026-09-12)
- K10: machine inventory + `check-account-drift.ps1` (machine-scoped, outside the factory)
- K11: `FACTORY.md` evidence labels; RULINGS R1–R9 confirmed via PROMPT A §3
- K12: advisory ingress `.claude-state/coordination/fable-ingress/` + bus spec. **NONE** for a kernel filing loop inside the factory

## Untested

These are advisory, not evidence from this repo, and the steward may weigh them at will. Three read-only Claude Opus
agents were each given an opposing brief: against the default, what outranks it, and a pre-mortem bound to evidence.
They estimated the chances below. The claims marked verified were checked by this session.

- **Estimates.**
  - A §5-compliant v1 ratified within about 90 days: 25% (15–40), 40% (25–55) and 12% (5–25). Midpoint about 25%.
  - v1 usable unchanged by creative writing, Unreal or games, mobile, business strategy, Blender and three.js: 10%
    (5–20) and 20% (10–35).
  - A listed future domain filing a real-subject report by 2026-12-14: 15% (5–30).
- **§5 criterion 2 can be met without any of those domains** (verified: `hardware-in-loop` and `measured-objective` are
  the benched non-test-suite profiles, §6 "No bench yet" for the other six). So "universal v1" can be ratified with
  no evidence from the domains the owner named. Suggest: either require one filing from a non-code creative or asset
  domain before §5 criterion 4, or name the v1 "fleet-current kernel".
- **The kernel assumes AI-model workers, and §3 has no bullet for that.** K8 (inference quota), K9 (rotating
  accounts), K10 (provider inventory) and K11 (model-review posture) presume the producer is a model on a provider
  account. A human-authored creative-writing or Blender pipeline would find these N/A, not FIT. Suggest: move K8–K10
  into an `ai-lane` overlay profile and keep the kernel to identity, positive evidence, independent key, delivery
  state and ordered health.
- **K2 conflicts with `business-strategy`.** K2 limits owner escalation to "deadlock, a novel class, high risk, or an
  irreversible act"; the profile makes "every decision" owner authority. One must be narrowed.
- **The revision clock does not track text changes** (verified: `45f4a2c` edited §5, header still `r1`). §5
  criterion 3 ("two successive harvests on the unchanged revision") needs the revision to change whenever the text
  does, and "harvest" needs a unit now that harvest is continuous. Suggest: a test that fails when the kernel blob
  changes and `r<n>` does not, and a harvest window of at least 7 days.
- **Base rate.** The pre-mortem agent counted 1 ratified portable core and 26 unratified ruling candidates on the bus,
  and approach-a-design at 6 filings with 2 harvested. The counts come from that agent's commands and were not
  re-run here.
- **The health enum has no word for "stalled".** This factory has made no forward progress for about 4.5 days, and
  `operability=PRESSURED` is the nearest value.
