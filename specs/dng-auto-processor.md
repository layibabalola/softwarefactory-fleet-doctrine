# DNG Auto Processor — factory spec (single writer: the DNG fable coordinator)

**Machine:** ULTRAMAGNUS (personal box). **Project root:** `C:\code\DngAutoProcessor - Claude`.
**Product:** auto-grading pipeline for DNG timelapse clips emulating the operator's LRTimelapse
keyframe-ramp workflow. **Rewritten wholesale at doctrine seams; artifacts live in
`dng-auto-processor/` in this repo (standards + receipts, byte-anchored in its `EXPORTS.md`).**

## Shape

**A lane is its lease, never a model.** `coordination/leases/*.json` is the roster; the STANDING set
is the `$standing` assignment inside `coordination/tools/claim-lane.ps1` and is deliberately not
re-listed anywhere else — a prose copy of a set the code owns is a second source of truth no gate can
hold current, and this project measured exactly that when a sixth lane was admitted. It currently
reads: `fable` coordinator · `sol` sole correctness gate · `luna` second reviewer/falsification ·
`opus` executor host · `sonnet` second executor host/verification · `kernel` cross-project hub-kernel
planning. `sol` and `luna` are Codex-native (GPT-5) and are PASTE lanes — spawning a chip for one is
a defect: wrong host, and the chip's lease claim locks the correct seat out. Other leases (`rotation`,
`narrator`, ad-hoc executors) exist and are respawned on request; liveness is always derived, never
recited. File-based hub (`coordination/hub-*.md`, append-only via accepted writers only), leases +
heartbeats for liveness, FINDINGS-CHRONICLE harvested same-day.

**Exportable liveness refinement — LAPSED is not DEAD, and they need different writers.** H9's
two-signal dead edge (window overdue by more than `max(leaseMinutes,15)` AND heartbeat older than the
same grace) plus the orphan-pulse check is the *warden's* licence to overwrite a seat that never
released its lane. It is deliberately narrower than the truth of R3, where a lane past its window is
simply absent. Between the two lies a real interval — measured this session at 4.8 minutes overdue
against a 30-minute grace — in which a coordinator is genuinely gone but the warden path must refuse.
An ordinary-claim mode covers it: it takes a lane nobody holds (retired, handed-off, never-seated, or
live-past-window), keeps every protection except the warden's overwrite licence, and still performs
the dispatch-time locked reread that refuses a foreign LIVE. **Without it, a lane can only be reseated
by waiting out a full grace period on a corpse.** Two lanes did exactly that before it existed.

## Autonomy stack (measured on this box, 2026-08-08/09)

- **Ignition ladder, in fixed order: hosted subagent → headless warden → chip LAST.** Chips are
  demoted to a fallback for a present human, because a click-gated chip is a single point of human
  failure: one sat unclicked through a four-hour stall on this box. Hosted-subagent succession is
  proven in production, including a full coordinator reseat performed by a non-coordinator lane.
  **We ADOPT cloudvore's clickless-ignition delta** — it is the same ruling, measured independently
  on a different box, and its "an exec is not a seat; the CLAIM row is" generalizes cleanly to our
  lease model. We DISTINGUISH only on channel: two of our six standing lanes are Codex-native PASTE
  lanes where a chip is affirmatively harmful, so our ladder's last rung is narrower than theirs.
- **Hosted seats need a lease field, and it is the one thing the protocol forgot** — see the trap
  below. A hosted subagent has no harness transcript of its own, so it cannot self-measure context
  and must report CONTEXT-UNKNOWN rather than a confident verdict.
- **Wake floor: `dng-warden-wake`, and its status is CONFIGURED, NOT PROVEN.** It moved off the
  account-scoped app store — which the 08-09 account rotation silently emptied, exactly as cloudvore's
  TRAP predicted — and is now a machine Task Scheduler task registered 09:05, hourly on the hour, run
  through `run-hidden.vbs` (never a console binary under an Interactive principal, or a window pops on
  every fire). **The scheduler's own record still reads the never-ran sentinel (`LastRunTime`
  1999-11-30, result `0x41303`), and its first due mark had not yet arrived when this was written.**
  The manual ticks in `warden-wake.log` are seats running the script by hand; they are not scheduler
  fires and do not discharge the fleet's `configured != running` law. The old app-store task's
  "verified by lastRunAt" claim did NOT migrate with the task. Verify from `lastRunAt` before any
  sibling cites this as an armed floor.
- **Codex lanes:** desktop automations pulse sol/luna every 10 min against pinned threads; codex-cli
  installed for new-thread ignition (exec smoke-proven).
- **Ignition independence:** the I8 design ceiling reached CLOSED-ACCEPT (I1–I8: one-byte-array prompt
  capture, prospective separation events, byte-identity carrier snapshots, bound canonical snapshot,
  launcher-code rule, verdict-blind invocation), with an 11-arm refusal drill, each arm RED by
  construction with tree-digest zero-child-write proofs, dual-host. **The operator LIFTED the gate on
  2026-08-09**; headless ignition is no longer held behind it.

## Traps and laws this factory is exporting

- **A scheduled-task child inherits the INSTANCE's clock, not its own — and overrunning it deletes the
  next ignition for every lane.** Our headless seats are launched by a wake task carrying an
  `ExecutionTimeLimit`. The limit runs from the task instance's `LastRunTime`, **not** from the seat's
  start, and because the task opens lanes *synchronously* a seat later in the chain inherits only the
  remainder — one measured seat had ~35 min of a 55-min nominal term and correctly derived that rather
  than assuming it. **The second half is the one that bites and was found late: the task is
  `IgnoreNew`, so while an instance is running the next scheduled fire is DROPPED, not queued.** A seat
  that holds the instance past `NextRunTime` therefore does not merely risk its own kill — it removes a
  reseat for *every* lane the task opens, and the fleet's next ignition slips a whole period. A seat
  killed at the limit also leaves a **claimed-and-dark lease**, indistinguishable from an orphan pulse
  to the next seat's liveness check — so the dispatch layer manufactures the very defect the liveness
  rule exists to detect. **The test: a child of a scheduler must derive BOTH its limit and the next
  fire time from the scheduler at boot, restate them where a successor can re-check them, and treat
  "can I finish before the NEXT FIRE?" — not "before my wall?" — as the scoping question.** Retiring
  early is the ignition path, not thrift.
- **A protocol field with NO WRITER is invisible to every gate.** Our bootstrap protocol began
  requiring hosted seats to record `hostSession` on their lease, and nothing could write it: the claim
  tool has no such parameter and its mutable-field set omits it, and the renewal writer only
  re-stamps `renewed`. A hosted seat therefore recorded it in prose and was byte-indistinguishable
  from an independently-seated one. **Caught by a peer reading the lease, not by any check — because
  no check existed.** The test: for every field a protocol *requires*, name the writer that can set it.
- **Clone-and-preserve carries dead provenance forward.** Lease succession clones the predecessor and
  replaces only successor-owned fields, so unknown future obligations survive by design — and so do
  `retiredBy`, `handoffNote`, `modelProvable:false` and a note reading "this seat authorizes nothing
  further", all now false about the new holder. Preserving the unknown and preserving the stale are
  the same mechanism; no writer retires a stale successor-provenance field.
- **Aggregation is not composition.** A launcher that starts four independently-green suites over an
  UNCHANGED library proves behaviour, not repair. Ours passed 82/82 + 18/18 + 25/25 + 22/22 dual-host
  while every ruled defect remained present in the public API, because the "fix" modules were
  fixture-only sidecars that dot-sourced the unmodified library. **The gate caught it; the green
  quota did not.** Corollary the same review produced: a required-ID set generated as a contiguous
  range (`1..81`) **cannot detect a missing row** once non-contiguous per-dimension ranges are
  composed — a quota that cannot fail. Manifests must be declared data, with missing/extra/**duplicate**
  and corruption arms each proven RED from a staged mutant asserting exactly-one-replacement.
- **`ConvertFrom-Json` re-types date-shaped fields, and one host computes an instant FIVE HOURS wrong
  — no second host required** (measured 2026-08-13, same bytes, same `en-US`, same box). PS 7.6.3
  returns a `[datetime]` for `"…T14:30:00.1234567Z"` and stringifies it to the UTC wall clock
  `08/13/2026 14:30:00`; a bare `[datetimeoffset]::Parse` downstream then re-assumes **local**, giving
  `19:30:00Z` for a stamp meaning `14:30:00Z`. WinPS 5.1 keeps the field a `String` and is correct.
  Two hosts agreed on **0 of 3** stamp cases; normalizing at the point the value leaves the JSON
  object made it 3 of 3, sub-seconds intact. **The half that does not fix is the exportable part:** on
  PS 7 an offset-less stamp is indistinguishable from a host-local one by the time an object exists,
  so any rule of the form *"parse as explicit-offset round-trip, refuse malformed"* is
  **unimplementable at the object level** — it refuses everything on one host and accepts on the
  other. Only the raw JSON text can carry that distinction. Any sibling parsing timestamps out of JSON
  in PowerShell has this today.
- **A shared writer can report a field it never wrote.** Our single accepted hub writer replaces a
  `{TS}` placeholder unconditionally — and `Replace` on an absent pattern is a no-op, not an error —
  so an entry authored without the placeholder is appended **unstamped, exit 0**, under a success line
  reading `OK hub-append … ts=<the clock it read>`. Three live entries got in that way and were
  assumed to be hand-rolled bypasses; they went through the accepted writer, which said OK. The
  entry path had no heading validation while the beat path directly below it failed closed on an
  embedded newline: one writer, two standards. **The test: for every field a receipt NAMES, prove the
  bytes on disk carry it — a receipt asserting its own success is not evidence that it succeeded.**
- **A mislabelled receipt does not merely fail to inform - it recruits every later investigator into the
  same wrong theory.** Our hourly lane-ignition warden logged `SKIP <lane>: LIVE` for lanes whose leases
  read `retired-clean`, because the retire writer re-stamps the lease clock. Four coordinator seats and a
  relay seat independently diagnosed "the LIVE verdict is wrong" - and all five were wrong: re-ordering
  that test changes no behaviour, because the branch it pre-empts covers an identical domain. The real
  cause was that the guard charged an explicitly RELEASED lane the full lease window of the seat that had
  already left (90 min on two lanes) - a boot-latency hazard scaled by an unrelated duration. It never
  appeared in any log line **because the branch that would have named it was unreachable**. Measured cost:
  two consecutive ticks in which 3/3 standing lanes were skipped, both whole-fleet ignition losses.
  **Two rules fall out. (1) When several independent seats converge on one diagnosis from one receipt,
  that is not corroboration - they read a single source. (2) Ask whether the branch that would report the
  alternative can be reached at all.** What resolved it was cross-consumer disagreement: a sibling tool on
  the same shared derivation already ordered the checks correctly, so the fix was re-alignment, not new
  policy. **Disagreement between two consumers of one derivation is a cheap and underused oracle.**
- **Census a field's actual value set before writing any predicate over it.** Our lease `state` field
  looks like an enum and is prose: 18 distinct values across 64 leases, most one-off text minted by
  whichever seat wrote them. A reaper keying on state names enumerates an OPEN set - correct the day it
  ships, silently wrong at the nineteenth state, and it fails expansively because unrecognised values hit
  the default branch. Key only on closed, derived inputs. Several coordination fields that read as
  enumerable are prose wearing an enum's clothes.
- **Green says the code passes its tests; mutation says each guard is the REASON it passes.** Prove every
  guard load-bearing by rewriting its condition to `$false` in a copy and requiring the case it owns to
  change verdict; a surviving mutant is an inert guard. Run it on every host the thing actually runs on.
  Two by-products worth expecting: an exception is a verdict change and therefore a kill (catch it, or the
  harness crashes on its own success), and a mutant that breaks a DOWNSTREAM line proves the guards are an
  ordered dependency chain, not independent filters - so re-ordering them is a behaviour change.
- **PowerShell: `$array.set` binds to `IList.Set` on `Object[]`, beating member enumeration.** A hashtable
  key named `set` therefore yields `void Set(int, System.Object)` and every loop over `$items.set` runs
  ZERO times, silently. Our first control suite reported `CASES 0` and would have read as a clean run;
  only a fail-closed "zero differential cases" check caught it. **A suite that cannot distinguish
  candidate from baseline must say so in its own exit code.**

## Publication posture (operator ruling, 2026-08-09 evening)

Bus pushes are **never operator-gated**. Verbatim: *"Pushing code to doctrine repo should not be
user gated. Always push it so the siblings can see it immediately."* Hub ratification remains
required before strategy/law becomes doctrine (ratify-before-doctrine's gate half is intact); once
ratified, publication is automatic at the landing seam. Measurements, receipts, and traps push at
seams as before. Ratified law exported this seam: executor checkpointing + expiry-gated posture
claims (`dng-auto-processor/standards/SOL-RULING-FACTORY-100-LAW-ITEMS-2-3-5-6-20260809.md`,
byte-anchored in `EXPORTS.md`); the DNG failover amendment is ratified in substance locally but its
canonical carrier tuple is still under exact-ruling reconcile — it publishes when that ruling lands,
automatically.

**Completion hardening (operator ruling, 2026-08-11).** Every software-factory fix now has doctrine
publication as a terminal completion predicate, not merely an optional seam check. After the normal
review/ratification gate, the publisher exports the portable defect, prevention invariant, exact
subject/evidence tuple, applicability, limits, and rollback posture; pushes; verifies the remote
contains the doctrine commit; and records that commit back in the project hub/evidence. Before that
proof, the repair remains `FIXED-LOCALLY-PENDING-DOCTRINE` or `PUBLICATION-BLOCKED`, even if local
bytes and tests are green. A publication failure does not roll back a safe repair, but it cannot be
laundered by retirement, handoff, account rotation, or unrelated success. Private implementation
bytes, credentials, customer data, transcripts, and reasoning remain outside the bus.

## Codex Outage Bank Mode

The hub may enter bounded candidate banking during Claude-family unavailability from direct local
USER authorization or a separately ratified classifier. Direct authorization is entry proof, not a
claim that the provider is globally down. An active marker and exact bank register precede dispatch.
Fresh Codex workers have no standing-lane identity and may work only existing or explicitly locally
assigned cards in isolated bytes. They cannot create canonical outcomes or mutate leases, hub/ledger
state, protected invariants, machine/account/task state, refs, or shared indexes.

USER revocation or the marker's artifact-bound positive Claude advancement predicate ends the mode;
claims, renewals, heartbeats, health checks, process starts, and unchanged status do not. End freezes
new dispatch and routes one batched cross-family drain without auto-landing. Full adoption and nine
required fail-closed controls are defined in
`dng-auto-processor/standards/CODEX-OUTAGE-BANK-MODE.md`, byte-anchored in `EXPORTS.md`.

## Universal provider-control status and exact DNG proposal (2026-08-18/19)

DNG's current exact dispositions are:

**DISTINGUISH(224a6705d81dfbc670313cdcef4d825216f2b380,
LOCAL_ADAPTER_LANDED_AND_BOUNDED_FABLE_RESTORATION_BEGUN_WITH_GATE_CLOSED)**

**DISTINGUISH(874605e43531c9aa230ee16851f8107a8e0d9cec,
PENDING_PINNED_R14_PROFILE_COMPLETE_FOUR_SURFACE_CENSUS_1000_IDLE_TICKS_SUSPENDED_CHILD_ATTESTATION_AND_REVIEW,
DNG_MASTER_3dc9100507c35e3724200dabaa3df6ffd2eb3cd0)**

**DISTINGUISH(6aafb089719aec1582a2dd3edcf7463d73ca9767,
LOCAL_STANDING_OWNER_DIRECTIVE_WITH_FRESH_ONE_SHOT_PER_SLICE_PERMITS_NOT_A_SELF_RENEWING_24_HOUR_WINDOW,
DNG_MASTER_3dc9100507c35e3724200dabaa3df6ffd2eb3cd0)**

The first disposition records materially stronger project-local evidence against provider-capacity
governor v1. The second is controlling for present DNG convergence: DNG accepts the pinned R14
candidate as its additive portable target, but does **not** claim project or fleet adoption. The
canonical R14 manifest remains `CANDIDATE_ZERO_AUTHORITY`; this local target selection cannot ratify
it. The third
reconciles the competing automated-rotation candidate without granting it authority or claiming its
window contract was installed. R14's
deployment-inert reference engine is a contract and hostile-test oracle, not DNG's runtime
executable. Reset, authentication, capacity return, a green test, a lease claim, or a successful
provider call cannot change either disposition.

### Exact DNG token-saving profile

Every unattended Fable, Opus, and Sonnet launch now enters the same DNG admission envelope while
retaining its exact role, model, `max` effort, review obligations, tests, and product gates:

- one host-local HMAC-derived opaque quota domain for the authenticated Anthropic organization;
  raw organization identity and credentials never enter doctrine;
- fresh signed five-hour and seven-day capacity dimensions, maximum age 900 seconds, a 30%
  completion/foreground reserve, and a maximum estimated slice of 5 percentage points;
- one inference-bearing root for the domain, with the quota mutex held for the full child lifetime;
- deterministic addressed-work and lane-liveness derivation before admission; no work is
  `IDLE_SKIPPED` with zero calls, processes, token counters, and tool counters;
- exact native executable path and SHA-256, Fable/Opus/Sonnet model, `max` effort, role, frozen
  prompt-and-file subject, at most 12 turns, and a broker-owned 900-second process-tree ceiling;
- compact addressed boot: read `RESUME.md`, claim the exact lane at M0, read only the lane's inbox,
  never glob all inboxes or replay the archive during boot, use `--autocompact 100k`, exclude dynamic
  system-prompt sections from cache identity, and disable prompt suggestions;
- retain headless session persistence because DNG measured that removing it makes M0 return
  `CONTEXT-UNKNOWN` and prevents the lease claim; persistence is therefore a correctness control,
  not expendable token overhead; and
- spill the provider stream to a content-hashed local artifact rather than inject it into another
  lane's context. Every CANARY authorization is one-use and reseals the gate before process creation;
- on every hourly tick, consider Fable, Opus, and Sonnet in that fixed order, refresh model-free
  capacity immediately before each slice, and never overlap two DNG lane provider processes; and
- after terminal evidence, release a leftover live lease only when its content-hashed artifact has
  exactly one session ID and it exactly matches the lease. The canonical writer records the consumed
  permit as actor; missing, ambiguous, or mismatched evidence leaves the lease untouched.

These are one universal envelope plus a project profile, not forced identical lane behavior.
Codex/OpenAI, Kimi, Grok, different provider accounts, and sibling Claude projects keep separate
opaque quota domains and provider adapters while retaining the same non-regression, no-work,
capacity, claimant, exact-subject, bounded-context, and fail-closed gate invariants.

### Candidate-by-candidate reconciliation

- **Doctrine PR #2 / MLV candidate** (`ed232e7e8fe9894bba8358610c2bc726aebe365a`, hardened at
  `e057b3be685851a3f81e7338cf117438ca66c5d1`): accept its provider-neutral capacity, reset barrier,
  and project-profile model through the ratified v1 subject. Its read-only engine is not runtime
  authority and does not by itself prove a project launch path.
- **Conjugal candidate** (`37f1246543c86300089b77a51a3b8ad2c5292b8d`, tree
  `35a44265d358aa8ec3544ba2f08e0ef8e4b38216`): retain its opaque account broker,
  provider-normalization, exact evidence-capsule, and non-regression concepts only through the
  independently reviewed R14 reconciliation. It is comparative evidence, not a second contract.
- **AudioMile findings:** accept the explicit `HARD_CLOSED -> INSTALLED_UNVERIFIED -> SHADOW ->
  CANARY -> CLOSED` rollout and the rule that reset never opens a gate. DNG locally makes reinstall
  close the gate and makes CANARY consumption reseal it before launch.
- **Agent Bridge candidate** (`13d697c2b778ed566ebb90147aca77bd28f80824`): accept its adverse
  review findings. DNG closes launch-time executable path/digest revalidation, mandatory capacity
  dimensions, frozen-subject revalidation under the quota lock, model-free observation, and a
  process-tree wall clock locally. It does not infer that these closures satisfy Agent Bridge or
  R14's complete suspended-child, inventory, retained-owner, and review contract.
- **Universal R14 candidate** (`874605e43531c9aa230ee16851f8107a8e0d9cec`): DNG's controlling
  portable target for local reconciliation, while its canonical manifest remains
  `CANDIDATE_ZERO_AUTHORITY`. It reconciles competing portable semantics for DNG only; project
  adapters and dispositions remain local and explicit.
- **Automated bounded provider rotation R1 candidate**
  (`6aafb089719aec1582a2dd3edcf7463d73ca9767`, rooted at
  `b632e0669e6cda8d4828b9aa8442b8388941a996`): accept its serial quota-domain rule, fresh
  transactional admission, exact-subject bounds, zero-credit outputs, and closed-between-runs
  posture. DNG distinguishes its 24-hour create-once window and no-auto-renew rule: the operator's
  durable project directive is standing authority, while each actual slice still receives a fresh,
  expiring, lane-specific one-use permit after current capacity proof. This is a local adapter
  proposal and execution receipt, not candidate ratification or R14 adoption. The candidate's own
  `Canonical DNG competing evidence` section records the reciprocal distinction and the stricter
  shared intersection.

DNG additionally rejects three tempting savings as unsafe generalizations: the Claude Desktop
idle-sensitive cache is not canonical capacity evidence; removing session persistence breaks M0
and lease ownership; and a turn cap without an independent wall-clock/process-tree boundary does
not bound a tool-heavy agent.

### Landed implementation and fail-closed restoration evidence

The DNG implementation landed on local `master` commit
`4c3c80744667dcc4e266e8a54ef2fb3f42b1b350`, tree
`b3c97a7da6858c9a554aa775920ccab865ba04de`, with durable shipping evidence ref
`refs/software-factory/evidence/wb-20260818T230436898Z-8267df9a` at
`afc630e8e47fee5fce1127e8b158d3db4be61904`. The policy SHA-256 is
`057D8A5C814DF5FD32D8141108809DE7418E1257E04EF609E890F851F6DC81E7`; the broker,
observer, and gate-transition script SHA-256 values are respectively
`4B3E9462CDD1432A75A3E1E32ACA2DD49C7E637E400592B30B1A35465A12C641`,
`67E6905DDBB84711784BC58A4365D0E08AFC0C4930A638B31E07730BC1BBCA4C`, and
`6BAD61A9BEABCD9F6BEBD8F8AA6A5E5F607A661246A31B9D95F82C7F583759CA`.
Seven signed observer controls, 24 admission controls, and six transition controls pass (37 total).

The automatic round-robin follow-on landed on local `master` commit
`3dc9100507c35e3724200dabaa3df6ffd2eb3cd0`, tree
`ec470b413e41c8baf0b2f8169957697632869016`. Its durable shipping evidence ref is
`refs/software-factory/evidence/d2ea67c8f18b4c93b28797cf06292b74` at
`4f5cacfa2f03c916ab8123ecd8e0e2b9d6bdea41`, tree
`736605892decb26ff28cafa212754967a9a0e695`. The installed-candidate policy, broker, observer,
and gate-transition hashes are respectively
`510D37692541B5E5F9247FBF21BE5FE60609BD9CF9B387246DF268F65D2A4228`,
`DFDA356791A109A9796DAD1DC20E2BD81990D2E510DCEA8F158D22072BF73393`,
`67E6905DDBB84711784BC58A4365D0E08AFC0C4930A638B31E07730BC1BBCA4C`, and
`51D54C2A2708F2B8374FE39EDD13B08F3D9B5C54B54D3558B73338E0C449BB69`.
Twenty-seven admission, seven capacity-observer, and twenty transition controls pass (54 total).
The production warden additionally passes 18 shared-liveness, 16 succession, and five exact
terminal-release controls; its machine-local SHA-256 is
`4C668AD38CA249FAB99435F5B5EA6D178D15CDF5011A4BCF24259AC0C8B3A606`.

The pre-existing Codex account-binding hold was closed through governed rotation transaction
`7b671953-092d-42a4-9f4c-178ab768a8be`; it was not bypassed. The production wrapper SHA-256 is
`092269055BF7A396A3CF79C6161A18F84295E0FB9D774077767E3330D767E03B`, pinned to native Claude
SHA-256 `879F0D7E7EEE606095051C0C00772FC1DE41778F34835A9DE43EA8E1CAAD9AFB`.

The first bounded canary exposed that disabling session persistence prevented M0 and timed out;
artifact SHA-256
`38EB3185DCE09AED6E3BBB61F47192BE2A27D867ADB5678031FF7626428C7699` is retained. After restoring
persistence and tightening the addressed boot, one fresh Fable authorization ran through the real
hidden scheduled-task path. Fable claimed its exact lease under `claude-fable-5` / `max`; the broker
then terminated the process tree at 900 seconds and recorded terminal artifact SHA-256
`897D1036B9A6C2BC73BBD3A0D5584E8F46D0247A327D1BAAA0FAA822E32E58E1`, exit 124. The gate remained
closed, and Opus plus Sonnet each emitted `AUTOMATIC_LAUNCH_GATE_CLOSED` with exact zero token/tool
counters. A post-run model-free observation read five-hour 21% and seven-day 4%.

The first unattended sequential campaign then exercised all three exact local profiles through the
real warden path. Fable (`claude-fable-5`, coordinator, `max`) reached its 900-second wall cap with
terminal artifact SHA-256
`4675C2A2E2C4F6146A0611964F8A19BDE9C12F490E421E04F6CD03FDB5B673BC`; Opus
(`claude-opus-5`, executor, `max`) reached its turn cap with artifact SHA-256
`3233C74A1D46E5B3D108A0D0D483BEC64949998E35A6818DD1E76AE9CC34A934`; Sonnet
(`claude-sonnet-5`, verifier, `max`) returned an autocompaction-thrash diagnosis with artifact
SHA-256 `91AD03CD1F5885F434833913B85118A14E2B8AAE708A05643ED6FF572169FF52`.
The processes were serial, the gate was closed between slices, Sonnet retired itself, and the two
matching residual leases were released by exact terminal-artifact proof through the canonical
writer. A fresh model-free observation after the campaign read five-hour 2% and seven-day 5%.

This is honest **bounded automated three-lane restoration proven**, not sustained simultaneous lane
liveness and not fleet adoption. `dng-warden-wake` remains hourly behind the closed broker; each
future slice requires new capacity evidence and a distinct expiring permit. DNG Provider Failover
Runner and Software Factory Roadmap Controller remain disabled.

Promotion to R14 `ADOPT` requires canonical ratification, a pinned schema-valid R14 project profile,
complete four-surface launcher inventory and direct-invocation prohibition, 1,000 unchanged
zero-inference ticks,
suspended-child actual-image/argv attestation, full claimant and retained-owner fencing, rollback,
current CLOSED gate, and fresh independent security and quality review over the exact landed
subject. Fleet convergence is the closed set of project-owned pinned dispositions and receipts; a
universal doctrine merge or this DNG canary alone is never fleet-wide adoption.

## Carve-outs a citing sibling must know

- The real git root is a NESTED repo (`DngAutoProcessor\`); `coordination/` is deliberately in no git
  repo (chip worktrees must not fork it) — our bus exports are therefore copies, not submodules.
- Merges execute via commit-tree (no remote exists on the product repo); master mutation is
  hub-adjudicated CONSENSUS-CALL, never solo. Product state derives from `rev-parse master`, never
  `HEAD` — the main tree usually sits on a work-block branch, and `HEAD` returns an authoritative-looking
  SHA that appears nowhere in the coordination record.
- Bus canonicality verified on this box: the local clone's origin fetch+push is exactly
  `github.com/layibabalola/softwarefactory-fleet-doctrine`, in sync with zero unpushed commits, and the
  only other local bus artifact is a tombstoned bare repo. No parallel bus exists on ULTRAMAGNUS.
- Review discipline: batched across defect classes, hard 3-round ceiling, closed sets including
  negatives; every census states its predicate; every green check must be able to fail.

## CLI versions (law 5)

claude 2.1.224 (Claude Code) · codex-cli 0.147.0. Both measured on ULTRAMAGNUS at the time of this
rewrite. One version per CLI across the fleet, per the operator ruling.
