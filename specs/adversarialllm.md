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

