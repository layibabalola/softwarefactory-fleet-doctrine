# adversarialllm (AdversarialLLM-ClaudeCode) — living spec

> Single writer: the AdversarialLLM project. Wholesale rewrite at doctrine seams.
> Seeded 2026-08-09 by operator-directed session — this project joined the bus LATE;
> its 2026-08-09 four-hour stall is partly attributable to never having folded the
> fleet's ignition doctrine (scheduled-task headless lanes, configured!=running).

## What this project is
Chrome extension (WXT) for multi-LLM adversarial evaluation across 7 provider
harnesses (ChatGPT, Claude, Gemini, Grok, Kimi, Perplexity, DeepSeek), governed by a
five-lane software factory hub in `adversarialllm/docs/33_FOUR_LANE_HUB.md` (§5/§6
append-only tail is authoritative).

## Lane topology (operator directive 2026-08-09, five lanes)
- SOL — Codex, orchestrator/integrator. Ignition: `codex exec` scheduled task (minutes 13/43).
- LUNA — Codex, implementer. Ignition: `codex exec` scheduled task (minutes 13/43).
- FABLE — Claude reviewer half A (`claude-fable-5`; cover-labels itself on model downgrade).
- OPUS — Claude reviewer half B (`claude-opus-5`), owner of the living report.
- SONNET — Claude warden + overflow reviewer (`claude-sonnet-5`), liveness + drain audits, log `docs/33_SONNET_WARDEN_LOG.md`.

## Ignition (adopted from adobe-ingester pattern, 2026-08-09)
Windows Scheduled Tasks `AdvLLM-Lane-{Fable,Opus,Sonnet}` → `scripts/ignition/invoke-claude-lane.ps1`
→ newest installed Claude Code CLI headless with lane runner prompt
(`scripts/ignition/prompts/<lane>-runner.md`). Per-lane lockfile + live-PID check
enforces no-double-staffing. 30-minute repetition; live lane makes the tick a no-op.
Minute-marks claimed in RULINGS.md: **26/56**. spawn_task chips are fallback only.

## CLI versions on this box (drift is derived state)
- Claude Code CLI: 2.1.222 (`%APPDATA%\Claude\claude-code\2.1.222\claude.exe`)
- Codex Desktop: 26.803.5235.0 (no headless CLI on PATH)
- PowerShell 7 (`pwsh`) + Windows PowerShell 5.1 both present

## Bus sync mechanization (2026-08-09)
Every lane's wake checklist carries pull-diff-fold on boot and EXPORT-IF-SEAM at closeout
(3-question seam test + class routing in `adversarialllm/.claude-state/rules/rule-doctrine-seam.md`);
bus updates are checklist-mechanical, not judgment. Rulings still require hub ratification first.

## Open doctrine-relevant state (2026-08-09)
- Plans 1/2/5 (exact-SHA semantic integration gate; lease-authoritative broker release
  K42; boot-snapshot integrity SNAP-01) are P0 prerequisites before production
  integrations; O-5 operator-override + O-7 debt semantics in force.
- Plan 4 (system-TEMP delete-denied wrapper defect) EXECUTED on the commit/push
  critical path; ~60 residual `GetTempFileName` call sites queued for a LUNA sweep.
- Fresh blind FABLE + OPUS halves owed on exact `695d7219`.
- Stale registry note: `adversarialllm-fable-wake-watch` (minutes 19/49) observed in the
  06:37Z collision report no longer exists in this box's task store — collision moot,
  recorded here as data.

## 2026-08-18 disposition — one universal provider-capacity contract

**DISTINGUISH(224a6705d81dfbc670313cdcef4d825216f2b380,
PENDING_LOCAL_SUPERVISOR_AND_COMPLETE_ACTION_GRAPH)**

**DISTINGUISH(874605e43531c9aa230ee16851f8107a8e0d9cec,
PENDING_LOCAL_R14_PROFILE_SUPERVISOR_COMPLETE_CENSUS_AND_SHADOW,
RECEIPTS.md@blob:d5af1430aa567e1ba8d97759aa96892ea50675ac#2026-08-18-12:54-CDT-AdversarialLLM)**

AdversarialLLM accepts the ratified portable semantics in
`specs/fleet-provider-capacity-governor.md` and the R14 universal runtime reconciliation in
`specs/fleet-universal-provider-control-reconciliation.md`. These distinctions are activation-status
boundaries, not competing token-saving specifications. Provider adapters may translate native
identity, capacity, cache, reset, and terminal fields, but they may not weaken admission, exact-role
quality, independence, authority, or budget-stop semantics.

The ratified `874605e43531c9aa230ee16851f8107a8e0d9cec` and rejected launch-envelope candidate
`8eee3e4576778a18f92a3aff922c7574904e3fc3` are sibling commits, not a linear authority chain.
Uncommitted or later R15 reconciliation work has zero authority here until an exact successor is
independently reviewed, adjudicated, and merged; it cannot silently replace either accepted subject
or this project disposition.

The project cannot honestly claim `ADOPT` yet. The point-in-time receipt in `RECEIPTS.md` proves
that `AdvLLM-Lane-{Fable,Opus,Sonnet}` were disabled at 2026-08-18 12:54 CDT after typed
`usage-5h` failures. It does not prove a complete launcher action graph or a production governor.
The current scheduled lane launch paths resolve and start provider executables directly behind
per-lane PID locks. The separate observe/browser-provider send seams remain unclassified until the
recursive inventory closes. There is no pinned host-local supervisor at every provider-spawn seam,
no account-wide
quota-domain lease, no fresh required-capacity observation, no atomic final pre-spawn revalidation,
no deterministic changed-work proof, and no automatic reseal receipt. The three enumerated Claude
scheduled lane tasks remain disabled. Their effective policy posture is `HARD_CLOSED`; every future
or shadow admission snapshot must encode `automatic_launch_gate=closed`. No installed runtime gate
is claimed. Other inference-bearing seams remain unclassified and receive no launch authority until
inventory and containment prove them.

### Universal lane behavior

All SOL, LUNA, FABLE, OPUS, SONNET, browser-provider, and future-provider automation will consume
the accepted admission-snapshot and usage-event contracts plus R14's exact request, gate-transition,
launch-attestation, inventory, process-observation, project-profile, native-capacity, broker-health,
manual-canary, and evidence-capsule contracts. Any later schema change becomes binding here only at
an exact reviewed and merged doctrine amendment. Project-specific role names do not create separate
quota semantics.

AdversarialLLM saves provider capacity by:

1. deriving unchanged/no-addressed-work ticks deterministically and spending zero inference on them;
2. serializing all same-host roots that share one opaque provider/account quota domain, across
   repositories; a quota domain shared across hosts remains `HARD_CLOSED`/`SHADOW` until a separately
   reviewed distributed lease/broker amendment is proven;
3. performing polling, liveness, hashing, joins, test selection, and receipt packaging without a
   model turn;
4. replacing broad ledger and transcript loading with bounded, hash-bound evidence capsules and
   digest-addressed expansion;
5. bounding turns, context, wall time, and retry count, with budget exhaustion producing the
   canonical `CHECKPOINTED/WIP` status plus a typed budget reason, never false completion;
6. using stable provider cache prefixes and milestone compaction when the transport exposes them,
   while still counting cached traffic and preserving the functional prompt;
7. selecting model and reasoning effort only from role-cell evidence, never by silent downgrade;
8. reserving capacity for owner foreground work and one independent final review before admitting
   background implementation or maintenance.

FABLE and OPUS exact-model review requirements remain binding. A cheaper or available profile may
perform deterministic preparation or separately qualified bounded implementation, but it cannot
inherit an unavailable reviewer's credit. Required work queues when its accepted role cell is not
available.

### Restoration path

The project deployment overlay is:

`HARD_CLOSED -> INSTALLED_UNVERIFIED -> SHADOW -> CONTAINMENT -> CANARY -> ENABLED`

`HARD_CLOSED` is the required effective posture: every installed/shadow admission snapshot encodes
`automatic_launch_gate=closed`, and the exact inventoried inference task set is disabled. This is a
normative deployment requirement, not a claim that a runtime gate is already installed. Later
overlay stages require exact R14-bound gate, profile, inventory, health, capacity, claimant, and
terminal receipts; the overlay creates no second admission state machine.

A provider reset, successful authentication, fresh usage window, or task-registration success may
update evidence only; none may advance the stage or open the automatic launch gate. Before the first
Claude canary, AdversarialLLM must:

- freeze a complete recursive inventory of scheduled tasks, watchers, heartbeats, recovery paths,
  scripts, CLIs, and app-session wakes that can reach provider inference;
- pin the accepted doctrine bytes plus one reviewed host-local supervisor and provider adapters;
- route every provider-spawn seam through that supervisor and structurally reject direct invocation;
- hold an OS-enforced quota-domain lock/lease for the full child-process lifetime; create the child
  suspended while the canonical claimant remains `STARTING`; after final identity/lease validation,
  atomically record `CLAIMED`, then resume the child and record `RUNNING`;
- immediately before resume, bind an HMAC pre-resume receipt to PID and immutable process-start time,
  requested session constraints and seat epoch, canonical resolved executable path plus digest/platform image identity,
  exact launcher/config path plus digest, canonical argv plus digest, cwd, security-relevant
  environment digest, frozen subject/capsule path plus digest held against TOCTOU, broker health, and
  account-domain fingerprint plus requested provider/model/effort/transport/session constraints;
- capture observed provider/model/effort/transport/session/account-domain/effective-backend identity
  at the earliest authoritative runtime/provider boundary, before completion or review credit and
  before any follow-on turn; a mismatch immediately stops and reseals with no credit. An adapter that
  cannot prove identity before its first inference when the role cell requires that proof remains
  `HARD_CLOSED`, except for an explicitly authorized evidence-only canary that earns no review or
  completion credit;
- require an HMAC-bound, one-use, expiring canary authorization tied to the exact task, subject,
  profile, supervisor build, adapter, capacity snapshot, and gate epoch;
- pass unchanged-tick zero-call, same-domain cross-process exclusion, distinct-account parallelism,
  required-capacity-dimension omission, reset/rollover, replay, direct-launch bypass, frozen-subject
  TOCTOU, stale/partial telemetry, ambiguous identity, orphan, rollback, broker/observer loss,
  actual-image mismatch, and all-terminal reseal controls;
- publish dated zero-inference `SHADOW` and enforced `CONTAINMENT` receipts;
- compare context/capsule and routing changes against an exact frozen manifest binding source
  commit/tree, dependency lock and built-bundle hash, test commands and versions, fixture/capsule
  hashes, provider/model/effort/account-role cells, and accepted results; require the project unit/build
  suite plus three consecutive clean aggregate live campaigns, each exactly five iterations across
  all seven signed-in providers on strongest-live-selectable models, exact model/effort proof, `5/5`
  completion for every provider, rubric and validator `PASS`, zero disqualifying severe/warning carry
  counters, wrong-model fail-fast, and the blind exact-model FABLE and OPUS halves required by the
  then-current hub ruling; and
- run one bounded, explicitly authorized Claude job with completion reserve; every terminal path,
  including success, unconditionally reseals the automatic launch gate to `closed` and the
  deployment overlay to `HARD_CLOSED`.

A successful canary on the exact installed tuple is evidence only. Sequential lane restoration also
requires fresh authenticated evidence, fresh independent review, a project-owned `ADOPT`/activation
ruling, distinct adjudication, and an exact gate-transition receipt before any later move to
`CONTAINMENT`, `OPEN`, or `ENABLED`; each newly admitted lane remains separately reversible. No bulk task
re-enable and no reset-driven queue drain is allowed. This section grants no runtime install, task
enablement, provider launch, canary, gate opening, model substitution, review credit, or release
authority.

## 2026-08-19 R26 project-published disposition binding

**DISTINGUISH(909f769d02e8412e51e28e242cfa8d00dadc9a3d, ADVERSARIALLLM_R26_ZERO_AUTHORITY_EVIDENCE_ONLY_AUTOMATIC_GATE_CLOSED_NO_PROJECT_OWNED_R26_ADOPTION_RULING, ADVERSARIALLLM_MASTER_8f01ea860d22c0e0c0a8c5ac9f7c290b1c050c14, DISPOSITION_BLOB_a337a9bea93daf94e619653edb8b5241ee29b6af)**

This project disposition addresses exact R26 candidate
`e70a044f31dd2f43ab7c716d63a4eb89318c61b6` and exact canonical merge
`909f769d02e8412e51e28e242cfa8d00dadc9a3d`.

This distinction binds the project-published default ref
`https://github.com/layibabalola/AdversarialLLM-ClaudeCode.git` `refs/heads/master` at commit
`8f01ea860d22c0e0c0a8c5ac9f7c290b1c050c14`, tree
`4b39858e0421257fc997bb827571b35fb712e15a`, sole parent
`6c9e54d7962711c7a90828159c172b130ad7d594`. The project-owned machine-readable receipt at
`adversarialllm/docs/reports/softwarefactory-r26-disposition-20260819.json` is exact Git blob
`a337a9bea93daf94e619653edb8b5241ee29b6af`, 3,471 bytes, SHA-256
`33a784a39e9451db68acb96d26b550fd6a8c4aea140b78ac66fde47724e16b7d`. It records
`DISTINGUISH`, `adopted=false`, `automaticLaunchGate=CLOSED`, and zero provider, process,
scheduler, authentication, gate-opening, activation, adoption, or host-hard-close authority.

The exact project-candidate binding uses base commit
`4ca508a041d589aaaa07f995b34238cd43a9303f`, candidate status
`DISTINGUISH_ZERO_AUTHORITY_EVIDENCE_ONLY`, primary evidence path
`adversarialllm/docs/reports/softwarefactory-r26-disposition-20260819.json`, and disposition path
`adversarialllm/docs/reports/softwarefactory-r26-disposition-20260819.md`.

| Artifact | Git blob | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| `adversarialllm/docs/reports/softwarefactory-r26-disposition-20260819.json` | `a337a9bea93daf94e619653edb8b5241ee29b6af` | 3,471 | `33a784a39e9451db68acb96d26b550fd6a8c4aea140b78ac66fde47724e16b7d` |
| `adversarialllm/docs/reports/softwarefactory-r26-disposition-20260819.md` | `a7baf849dca2dea2f56874b3393afead7bd5e6ba` | 3,488 | `d0b5f941b93bca18a4c6906900004612daa8da9077daaa6f635fc0f45e10bcd7` |
| `scripts/verify-fleet-doctrine-disposition.ps1` | `fbc60a92704f8fe9495933953b4ac1a5c332db5d` | 15,183 | `0155c19228638a02c254d6811c0f7402aa996fbfbb0d2eee22033c5e4aff1c35` |
| `scripts/tests/fleet-doctrine-disposition.tests.ps1` | `9cb528a7967e11164d8e5378b63a6022e70b077c` | 6,404 | `cc7649c9a59760406dfe74c7f23d7ec2ec66ace5c9ec22c7ec912ff97e380ee5` |

The companion report, read-only exact-object verifier, and its hostile controls remain project-owned
evidence. Their publication does not transfer proof from another project, install a supervisor, open a
gate, enable a task, launch a provider, or satisfy any R26 adoption proof. AdversarialLLM remains
`DISTINGUISH`, not `ADOPT`; exact model, effort, role, review, quality, and functionality requirements
remain unchanged.

## DISTINGUISH_UTILIZATION_SHADOW_BOUNDED_FOREGROUND_EXCEPTION

Status: `PROJECT_DOCTRINE_EXCEPTION_NO_CURRENT_AUTHORITY`. Decision: `NO_GO`. AdversarialLLM
remains `DISTINGUISH`, not `ADOPT`. This project-owned doctrine exception is necessary but never
sufficient for a provider call. Its canonical merge cannot approve an adjudication, install controls,
issue or consume a permit, dispatch a job, or change the declared automatic-gate policy `CLOSED` or
rollout policy `HARD_CLOSED`. Those are declared policies, not proof of observed host containment;
`hostHardCloseClaimed=false`, `observedHostContainmentState=UNPROVED`, and
`implementationState=NOT_INSTALLED` remain controlling.

This amendment succeeds canonical fleet commit `5ac7036705338cfe3370f5fddda224e07d5d1bdd`, tree
`9e53ff055bbf1a4fe796104d06f009f503082ad5`, and project spec Git blob
`f169a661956830aced574e6c3fa6f4989098e892`, while explicitly resolving only the bounded
foreground conflict inherited from project-owned predecessor blob
`33fe9c7fb7cc31b1f172b9216475fef5fe97aaad` (12,264 bytes, SHA-256
`0d5758fc43094a9029491852faee190c8b34ec28d3fb14c561f82b87137ed99f`). It preserves fleet
`RULINGS.md` blob `34520b7f75386ab2dba6948bb27d256d3b06c2c9`, R26 merge
`909f769d02e8412e51e28e242cfa8d00dadc9a3d`, R26 tree
`e9283a1c297103dd53f0bc7a1310fb1dc86b591e`, and R26 subject
`e70a044f31dd2f43ab7c716d63a4eb89318c61b6` as zero-authority evidence.

### Exact bounded scope

If every separate prerequisite below later passes, the exception can cover exactly one attended,
foreground, one-shot Claude `DOCTRINE_EXACT_OBJECT_REVIEW` evidence job. It is not rollout `SHADOW`,
`CONTAINMENT`, `CANARY`, `OPEN`, `ENABLED`, product adoption, or runtime activation. The child must use
one exact model and effort with no substitution or fallback, one sanitized read-only exact-hash capsule,
a pinned launcher with all provider filesystem tools denied, and bounded stdout only. Its output is
advisory evidence only: no patch, repository mutation, review, correctness, adjudication, merge, release,
activation, or completion credit.

One permit covers one job, one attempt, one provider turn, and at most one concurrent quota-domain job;
admission requires observed concurrency exactly zero. Start TTL and runtime are each at most 900 seconds.
Input is capped at 32,000 estimated tokens and 131,072 bytes; output at 4,000 estimated tokens and 32,768
bytes; measured provider-window consumption is capped at 1 percent. Fresh capacity plus completion and
independent-review reserve are mandatory. There is no retry, continuation, second job, provider/model
fallback, schedule, watcher, persistence, auth mutation, reset, task enable/register/start, Desktop
mutation, deployment, automatic gate transition, or authority over any process except termination of
the exact child after a post-spawn mismatch.

### Conflict and precedence map over `33fe9c7f...`

| Boundary | Exact source | Precedence |
| --- | --- | --- |
| `DISTINGUISH_SUCCESSOR_AND_HARD_CLOSED_BOUNDARY` | `specs/adversarialllm.md@blob:33fe9c7fb7cc31b1f172b9216475fef5fe97aaad#L65-L82` | `PRESERVE_AND_SATISFY_SUCCESSOR_CONDITION_ONLY_AFTER_CANONICAL_MERGE`: preserve the 874/8eee sibling history, non-`ADOPT` conclusion, `HARD_CLOSED` posture, and no-installed-gate statement; this exact successor grants no provider call. |
| `UNIVERSAL_PROVIDER_SEMANTICS` | `specs/adversarialllm.md@blob:33fe9c7fb7cc31b1f172b9216475fef5fe97aaad#L85-L112` | `PRESERVE`: provider identity, capacity, admission, terminal, independence, role-quality, and budget-stop semantics remain controlling. |
| `ROLLOUT_OVERLAY_STATE_MACHINE` | `specs/adversarialllm.md@blob:33fe9c7fb7cc31b1f172b9216475fef5fe97aaad#L119-L127` | `PRESERVE`: the rollout overlay remains `HARD_CLOSED`; `UTILIZATION_SHADOW` creates no second admission or rollout state machine. |
| `CANARY_AND_ROLLOUT_PREREQUISITES` | `specs/adversarialllm.md@blob:33fe9c7fb7cc31b1f172b9216475fef5fe97aaad#L129-L168` | `PRESERVE_WITH_EXPLICIT_CLASSIFICATION`: every canary and rollout prerequisite remains mandatory; this job is not canary, rollout `SHADOW`, `CONTAINMENT`, `OPEN`, or `ENABLED` and earns none of their evidence or credit. The bounded-job slot at lines 166-168 can be satisfied only by the exact separately adjudicated job after installed controls pass. |
| `NARROW_PROVIDER_LAUNCH_EXCEPTION` | `specs/adversarialllm.md@blob:33fe9c7fb7cc31b1f172b9216475fef5fe97aaad#L170-L176` | `SUPERSEDE_ONLY_PROVIDER_LAUNCH_PROHIBITION_FOR_EXACT_CHILD_AFTER_ALL_GATES`: only the categorical provider-launch prohibition is narrowed, and only after the separate owner-approved adjudication, installed controls, one-use permit, durable pre-dispatch receipt, and zero-concurrency admission all pass; canary, task, gate, model-substitution, review-credit, release, and rollout prohibitions remain controlling. |
| `FLEET_RULINGS_NON_ADOPTION_BOUNDARY` | `RULINGS.md@blob:34520b7f75386ab2dba6948bb27d256d3b06c2c9#L982-L987,L1027-L1034` | `PRESERVE`: portable doctrine and a fleet merge are never project adoption or runtime authority; this exception remains `DISTINGUISH`, never `ADOPT`. |

### Required before any provider call

All of the following are mandatory and exact: a separately merged
`adversarialllm-utilization-shadow-adjudication/v1` record with decision
`APPROVE_ONE_SHOT_UTILIZATION_SHADOW`; two independent exact-proposal-byte `PASS` reviews; an explicit
authorized project-owner approval and a distinct authorized adjudicator; authority-registry-bound
identities and attestations; the proposal, amended-spec, precedence-map, job, capsule, launcher, model,
effort, existing-auth read-only evidence, capacity, quota-domain lease, zero concurrency, and reserve
bindings; digest-pinned installed controls and exact negative-control receipts; and create-new,
no-follow/reparse-rejecting, durably flushed, exact-byte-reread pre-dispatch and terminal receipt paths.
Paper records, source files, schemas, tests, existing authentication, or this merged amendment cannot
substitute for installed controls or authorize dispatch.

Content addressing is acyclic and ordered:

1. merge this canonical fleet doctrine amendment and externally resolve its resulting spec blob;
2. separately merge the owner-approved project adjudication and externally resolve its merge and record
   blob; the adjudication record must not embed a future permit or receipt digest;
3. install and digest-pin the adjudicated technical controls and pass the exact negative controls;
4. issue a later canonical one-use permit blob binding the already-resolved adjudication, exact job,
   controls, admission evidence, nonce, 900-second limits, and receipt paths, but no future receipt digest;
5. preflight and durably reserve the create-new terminal-receipt destination through the adjudicated
   no-follow/reparse-rejecting reservation control; then create, durably flush, and exact-byte reread the
   pre-dispatch receipt binding the issued permit, and record its digest while atomically consuming the
   permit before spawn; and
6. after the child terminates, write, durably flush, and exact-byte reread the terminal receipt at the
   already-reserved create-new destination without overwrite or authority credit.

Any absent, expired, unknown, changed, replayed, contested, colliding, over-budget, or mismatched fact is
`NO_GO`; after spawn it is `TERMINATE_EXACT_OWN_CHILD`. The permit remains consumed on failure. Every
terminal path captures bounded stdout or explicit failure, writes the immutable terminal receipt or an
explicit `RECEIPT_WRITE_FAILED_NO_AUTHORITY_CREDIT`, releases only the exact ephemeral lease, and retains
the declared `CLOSED` and `HARD_CLOSED` policies without claiming an observed host hard-close.

This section grants no `ADOPT`, provider lane, runtime activation, rollout stage, canary, containment,
task, schedule, queue, watcher, persistence, authentication, reset, Desktop, deployment, automatic-gate,
repository-write, patch, commit, merge, push, release, review, correctness, adjudication, completion,
model/provider fallback, continuation, retry, second-job, or host-hard-close authority.

