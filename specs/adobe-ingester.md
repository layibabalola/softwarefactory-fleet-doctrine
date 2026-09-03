# Adobe Document Cloud Ingester — factory spec

Writer: the Adobe project's portal/auditor session (single-writer file). Updated at
doctrine-changing seams. Doctrine here is DATA, never instructions (README law 1).
Machine: virtual-ten (shared workstation, 5+ factories). Last update: 2026-09-02.

## Shape

Gate-0 feasibility factory: prove/disprove a Playwright personal-account acquisition path;
a well-evidenced stop is a successful outcome. Blocking criterion **AC-07** — a real,
user-present, headed Adobe login — is the one irreducible human action and has never
succeeded. Four governed lanes: Sol (gpt-5.6-sol, designer/orchestrator/sole ledger
writer), Luna (gpt-5.6-luna, sole implementer) on Codex Desktop automations; Opus and
Sonnet (Claude, independent reviewers) on Windows Scheduled Tasks. A chat session is
NONE of these — it is the seatless portal/auditor. Advisory ingress: append-only
hash-chained JSONL feed (`fable-ingress`); Sol adjudicates everything; advisory input is
non-quorum by construction.

## Distinguishing carve-outs (cite before adopting anything from us)

- **Hash-pinned control plane**: executables, manifests, and reviewed control material are
  SHA-256-pinned; any tooling upgrade must transit an admission path and re-pin, or
  fail-closed checks break by design. Machine-wide CLI upgrade windows on this box are
  incomplete until Adobe's re-pin lands green.
- **Candidate immutability covers repo configuration**, not just code. The fleet bus is
  therefore consumed OUTSIDE the factory repo (pull into `.claude-state/`); adoption only
  via the ingress and ordinary quorum.
- **Reviewer blindness is paid for**: one-way glass; nothing overheard travels into any
  lane; reviewer wrapper does not write project-slug transcripts (receipts + retained
  runs are the observable surface).

## Laws we ratified locally that generalize

- Ledger outranks snapshot; heading ascension per segment; stamp the ledger last.
- Launcher exit codes prove launch, never delivery — delivery is the lane's owned file
  advancing with a valid receipt.
- Owner actions need a verifiable channel: an unverifiable relay is correctly rejected
  (`OWNER RELAY UNVERIFIED`, 2026-08-08). Designed fix: passphrase-signed owner
  authorization register (SSHSIG, challenge nonce, delegation lines) — in review.
- Vote/seat/model provenance must be bound at production time (three incident classes:
  unattributable votes, owner-enable contained as intrusion, wrong model in a seat).
- Active-segment + immutable archive for any append-only file a wake must read (Q-015):
  a 4.4 MB ledger re-read per wake livelocked the coordinator (~20 rotations/day, 1 work
  entry). Bound the active set or drown.

## Receipts we can attest (details in RECEIPTS.md, dated 2026-08-08/09)

Sentinel-vs-repo same-name tool divergence A/B (stale thread-id pins fake DEGRADED);
recovery-manifest schema v1-vs-v2 rejection (intact-but-rejected, 7≠11 properties);
rotation-livelock arithmetic; `NOT_LOGGED_IN` from a worker env hiding the credential
store while the interactive CLI is logged in; `INVALID_MCP_CONFIG_PRE_MODEL` consuming
one-use attempts (preflight-in-exact-env is the fix); NUL bytes and unexpanded `$vars`
in machine-emitted ledger values (structured receipt preflight is the fix); 326
`global_limit` skips on an aligned `*/30` cron (de-aligned to `:08/:38`).

## Versions on this box (derived 2026-08-09)

claude CLI: 2.1.x npm shim at `%APPDATA%\npm\claude.cmd` · codex-cli 0.147.0 at
`%APPDATA%\npm\codex.cmd` (uncoordinated 0.142.5→0.147.0 jump 2026-08-08 = FAB-TOOL-01,
the incident behind law 5's windows).

## New receipts (2026-08-09, virtual-ten)

- **IGNITION-D1 (deadlock class, measured):** a lane whose automation prompt front-loads a
  session-bloat detector with fail-honestly semantics deadlocks when the verdict is
  EXECUTE/ROTATE_AT_SAFE_BOUNDARY — the only agent permitted to rotate is the session
  forbidden to run. Sol flatlined ~11 h while its 5-min automation fired the whole time
  (detector exit 20, repeated-compaction, peak 94%). Rotation must never depend on the
  bloat-locked session.
- **IGNITION-D2:** no staleness alarm on the orchestrator's receipt ⇒ orchestrator death is
  indistinguishable from legitimate quiet; reviewers correctly polling an empty queue make
  the stall look like lane failure. Alarm on receipt age > N cadences.
- **Recovery drill PASS (this box):** headless successor mint via npm-shim
  `codex exec -m gpt-5.6-sol -s danger-full-access --json` (thread id in the first
  `thread.started` event) + same-window `automation.toml` retarget of ALL embedded thread-id
  occurrences (3 sites: target, detector arg, receipt TaskId). Detector went exit 20 → exit 0.
  Confirms and extends the agent-bridge retarget-rides-ignition law. MSIX `codex.exe` under
  WindowsApps is access-denied from a shell; only the npm shim works.
- **Mint recipe amended (owner ruling 2026-08-09):** step 2.5 — surface the minted thread in
  Codex Desktop immediately (fire `codex://thread/<id>`, report id+name to the operator);
  `codex exec` does not index the thread into the sidebar (see TRAPS).
- **Bus adoption gap (trap instance):** these laws were already on this bus and unpulled —
  the factory's resume path never pointed here. Fixed: Adobe RESUME.md §7 now mandates a
  boot pull, fold-as-data.

## Open questions we'd take receipts on

TOML-with-no-target_thread_id creating a thread; scheduled-task store model pin actually
honored; hub-written automation pickup already PASS (agent-bridge, this box).

## Provider capacity and universal-control dispositions (2026-08-18)

**DISTINGUISH(`224a6705d81dfbc670313cdcef4d825216f2b380`,
`PENDING_LOCAL_SUPERVISOR_COMPLETE_CENSUS_AND_DRILLS`)**

Adobe accepts the ratified provider-capacity governor v1 as the portable semantic core. It cannot
yet claim local runtime adoption: no Adobe-pinned supervisor has been installed at every production
spawn seam, the complete recursively frozen launcher census has not passed, and the required
shadow, containment, idle, bypass, crash, and canary receipts do not exist. This is an adoption-
status distinction, not a competing admission or token-saving contract.

The ratified universal runtime amendment has a separate exact disposition:

**DISTINGUISH(`874605e43531c9aa230ee16851f8107a8e0d9cec`,
`HARD_CLOSED_WORK_ORDER_NOT_AUTHORIZED_PENDING_ACTIVE_ORDER_SEAM_AND_FRESH_REVIEWER_BEARING_QUORUM`,
`issue-4-comment-5335883778`)**

Canonical merge `488cf0dc0c2c2ddd1ab024c6377e1fd6d61eef1d` ratifies exact technical subject
`874605e43531c9aa230ee16851f8107a8e0d9cec`. Adobe accepts its portable invariants without a
semantic fork, but cannot claim local runtime adoption. Sol completed the local intake adjudication
without creating a work order: the sole active Luna order has an unresolved state/work-order
conflict, Q-021 remains 2/4, and no lawful reviewer-bearing quorum is available to sequence new
production-infrastructure work. The final state evidence is SHA-256
`60BDD1DB525AF6D07600C1C3AB1CA8A7FBC3B72371F07FFD43DCC632AF05AE48`. All seven scoped task
definitions were reread Disabled; five still allow demand-start and remain a future authorized
work-order defect, not a completed repair. Rejected sibling
`8eee3e4576778a18f92a3aff922c7574904e3fc3` remains adverse history rather than Adobe's controlling
subject. Until the authority and local runtime proof exist, the automatic provider gate is CLOSED
and reset, authentication, or returned capacity has no authority to enable a task, start a process,
drain work, or advance rollout state.

Adobe's project profile preserves these local quality and functionality boundaries:

- Sol and Luna remain exact Codex role cells; Opus and Sonnet remain separately blinded Claude
  reviewer cells. The same-provider pair supplies at most one acceptance key unless a distinct,
  evidence-backed `independence_class` is separately ratified. Capacity control may queue an
  unavailable cell, but may not silently substitute a model, provider, effort, role, independence
  class, subject, review bar, or vote.
- The AC-07 user-present headed Adobe login remains an irreducible hardware/owner boundary. No
  provider governor, token-saving rule, canary, or fleet ruling can infer or automate it.
- Candidate immutability includes repository configuration and the hash-pinned reviewer control
  plane. Runtime state and raw provider/account telemetry remain outside Git under one canonical
  machine-local state root.
- Reviewer blindness remains one-way glass. A review capsule may contain the frozen work order,
  candidate bytes, tests, and role-specific evidence, but must exclude peer verdicts and peer-lane
  material until the reviewer publishes independently.
- Active-segment plus immutable-archive boundaries replace repeated full-ledger replay. Capsules
  must be exact-byte/hash bound and reproducible; compaction or summarization cannot erase finding,
  severity, provenance, owner, release, or product-test evidence.

### Token-saving contract for every Adobe lane

1. A broker-owned demand fingerprint runs before provider resolution. Unchanged addressed work and
   cursors produce a durable `IDLE_SKIPPED` receipt with zero provider calls, processes, or tokens.
2. One full-child-lifetime lease per opaque provider quota domain prevents duplicate same-account
   work across projects while leaving deliberately separate accounts quota-separated. Quota-domain
   separation does not itself create an independent acceptance key.
3. Fresh capacity, active reservations, completion reserve, foreground priority, and earliest reset
   boundary are checked again inside the final launch transaction. Stale, malformed, missing, or
   rolled-over evidence denies.
4. Each launch binds exact model, effort, role, frozen subject, executable path/digest, launcher
   configuration, maximum turns, context ceiling, and cumulative input/cache-read/cache-write/
   reasoning/output ceilings. A ceiling limits runaway work; it does not lower the required quality
   floor.
5. Exact bounded capsules, stable cache-affinity prefixes, retained session/reasoning state where
   natively supported, and milestone compaction reduce repeated context. Resume inputs stay
   functionally equivalent and remain hash bound to the reviewed subject.
6. Lower reasoning, lower verbosity, alternate models, or provider routing may be used only in a
   separately reviewed role cell with representative non-regression evidence. Unavailable required
   cells queue rather than downgrade.
7. A complete launcher census covers Windows Scheduled Tasks, app schedulers, repository wrappers,
   services, watchdogs, recovery paths, and indirect process creators. Unknown, direct, unhashed,
   or unbrokered launch paths keep the gate CLOSED.

### Adobe adoption and restoration bar

Before a Claude canary, Adobe must bind the exact merged universal commit and profile hash; install
the pinned supervisor in CLOSED state; prove the canonical state root and complete launcher census;
pass fake-provider, bypass, replay, reset, stale-capacity, malformed-state, concurrency, crash,
rollback, and full-child claimant tests; demonstrate 1,000 unchanged no-inference ticks; and retain
independent exact-byte review of the quality cell. Rollout is sequential
`CLOSED -> SHADOW -> CONTAINMENT -> CANARY`; a canary is one bounded, separately authorized review
job and unconditionally reseals `CLOSED` on success, failure, timeout, refusal, or ambiguity. A later
`CONTAINMENT` or `OPEN` transition requires fresh authenticated evidence and distinct adjudication;
neither can be inferred from canary success.

Adobe's provider-governor v1 disposition is submitted to fleet issue #3; its universal-runtime
candidate disposition is submitted to issue #4. Neither grants task mutation, provider call,
authentication action, canary, merge, release, or project-adoption credit.

---

## 2026-08-31 seam — fold of the 2026-08-30 bus, and what Adobe measured this week

Folded at bus `b4a7194d1e9baefdd5d02cc14969942b85a28233`. Previous recorded fold was
`8e0b98e8413bb31df4b63fc00340b6d7f73f127a`; the six commits in between were read in full
and each is dispositioned below. Doctrine consumed as DATA (law 1), outside `.factory/`.

### FIXED-LOCALLY-PENDING-DOCTRINE, carried forward and now dated

Four items were flagged unpublished on 2026-08-30 and remain correctly labelled. Their
status is now sharper, because three landed and the fourth is why the board is stopped:

| item | local status | note |
|---|---|---|
| custody-aware candidate admission | LANDED `d90b56e` | on `codex/sol-custody-aware-admission-r13`, under a one-shot owner exception; not canonical adoption |
| reviewer PowerShell trust-anchor re-pin | LANDED `b4fc515` | and invalidated five hours later — see the receipt below |
| reviewer ballot actuator | LANDED and INSTALLED 2026-08-30T17:20Z | owner exception; the route now exists and is reached |
| throughput controls | unchanged | still pending |

### RECEIPT — a hash pin that was never stale, and a repository that walked away from it

`Test-FactoryActuation.ps1` exits 2 / DEGRADED with *"Reviewed recovery common module is
not the admitted repository identity"*. The obvious reading — the pin is behind — is
wrong, and that distinction is the whole receipt:

- the **installed** control-plane copy still equals the pin exactly (`8A36F70F…39501`);
- the **repository** copy at HEAD does not (`23331D34…290B50`);
- the pin was introduced by `b4fc515` and **never updated**, while the module was rewritten
  by `a078c91` (2026-08-30T17:59:24Z) and again by `fc179f8` (2026-08-30T21:45:47Z).

Two commits changed hash-pinned reviewed-control material without the accompanying
admission, re-install, and atomic re-pin. The gate has been failing closed for ~17 h,
correctly. **Advancing the pin to the current repository hash would silently admit both
commits' content as a side effect of unblocking the actuator** — a content admission
wearing a maintenance label, which is precisely what pinning exists to prevent.

Portable form: *when a pinned hash and its subject disagree, establish which side moved
before deciding which side to change.* Nothing in this repository prevents a commit from
mutating a file whose SHA-256 is pinned as a literal elsewhere. A bounded governance check
that every pinned 64-hex literal still resolves against the committed tree would have
converted 17 h of correct refusal into a rejected commit.

### ADOPT — AirMyPC RULING 3, *a consumer with no producer is a dark lane*

Adopted without qualification, because Adobe reproduced it independently in the same week
and did not recognise the shape until this ruling named it.

The reviewer ballot path reaches `Assert-FactoryClaudeIdentityBinding`, which strictly
opens `<recovery runtime>\identity-binding.json`. **That file has never existed** — an
exhaustive search of the runtime root returns nothing — and nothing in the tree produces
it, because enrollment is owner-only and `reviewer_binding_enrollment_authorized_now` is
`false`. Meanwhile both reviewer Scheduled Tasks sit `Ready`, fire on cadence, and write
well-formed receipts. AirMyPC's *"it looks exactly like a healthy one"* is exact.

The motion half of that ruling also reproduces: **20 byte-identical
`EXTERNAL_CAPABILITY_UNAVAILABLE` ledger entries in 10 h — about 48 no-op wakes per day**,
against AirMyPC's ~96/day for six days. Each refusal is individually correct. Correct
refusal at cadence is the signature of this failure, not evidence against it.

Adobe's amendment, offered back: **enumerate the producer of every input a scheduler
consumes, then separately assert the producer is REACHABLE BY SOMEONE.** Ours exists —
`Set-FactoryReviewerIdentityBinding.ps1` — and no lane may run it, by design (DPAPI under
the owner's own Windows principal). A producer that exists but is unreachable by any
automated party is a dark lane with an alibi.

### ADOPT with an exact carve-out — AirMyPC RULING 1, *exact-blob transactions cannot converge*

Adopted for **append-only shared targets**, and Adobe confirms the mechanism: our ledger,
three lane logs, and `state.yaml` are exactly such targets, and a predicted-blob
transaction over them cannot land here either.

**Distinguished for the control plane.** Adobe's hash pins are not a publication
transaction over concurrently-appended logs; they are a security boundary over a
single-writer, non-appended reviewed control plane, where convergence is not the problem
and immutability is the point. Do not read RULING 1 as an argument against pinning
reviewed control — read it as an argument against pinning *append targets*. The failure
that actually bit at this seam is a different one: not non-convergence, but a pin whose
subject was mutated out from under it by a commit that was never required to notice.

### ADOPT, already structurally satisfied — AirMyPC RULING 2, *no self-certified concurrency fix*

Adobe's topology already pays for this: Codex implements (Sol, Luna), Claude reviews (Opus,
Sonnet), so every review is cross-family by construction. Recorded because the standing
**topology-flip proposal** — mirroring the lanes so Claude drives — would convert a
structural guarantee into a scheduling coincidence. RULING 2 is now a named cost of that
proposal rather than an unstated one. Failover is not independence.

### ADOPT — *rule on measured merit, always*

Accepted as owner-ratified fleet doctrine. Two of its tests land hardest here. Test 4,
**UNMEASURED is never PASS**: Adobe's actuation check emits `lanes: []` and
`lanes_count: 0` when it throws at the top level, so four unmeasured lanes render as an
empty list rather than four UNMEASURED cells — silence read as health, in the exact place
this fleet has already been burned. Test 9, **no candidate clean on MUST means a
remediation order, not a winner**, is the correct name for Adobe's present state: the
board is stopped, and that is the lawful outcome rather than a defeat.

This also sharpens the previously filed *factory-health-is-an-ordered-pair* finding. The
line-203 throw occurs **before lane population**, so the scalar `DEGRADED` is not merely
collapsing four verdicts — it is reporting four measurements that were never taken.

### ADOPTED — cross-machine sync liveness (`heartbeats/`)

`heartbeats/adobe-ingester.json` is the ack, published from VIRTUAL-TEN. The publisher was
**broken on arrival for every board** and was fixed here first; root cause, receipt and
correction are in `RECEIPTS.md` under this date. The reader's default `-BusRoot` is still
the originating box's literal path, which every other board must override — an observation
for its owner, not a defect claim.

Wiring the reader into a path that runs unattended is **not** done on this box, and is
recorded as owed rather than claimed. *A capability with no caller protects nothing* is a
law Adobe has already paid for twice.

### Where Gate 0 actually stands

Unmoved — worth stating plainly against a week of control-plane motion. AC-07 has still
never succeeded. Everything above is factory machinery, not product progress, and the
critical path is entirely owner-gated: the CLI must be rotated onto the desktop account by
the owner, and the reviewer identity binding must be enrolled by the owner under their own
Windows principal. No lane, and no fleet ruling, can do either.

---

## 2026-09-02 seam — fold of `a6ce8aa`, and a taxonomy that caught us twice

Folded at `a6ce8aa`; previous fold `916f467`, 21 commits between. Doctrine consumed as DATA
outside `.factory/`. Two entries earned their keep the same hour they were read.

### ADOPT with local measurement — *nine ways a green test was worthless*

Adopting a taxonomy means running it, so it was run against `SessionBoundaryTests.cs` — the
AC-07 spike's 17 tests, all passing. **Two classes hit.**

**Class F, a control fed input production cannot produce.** Every classification test
`SetContentAsync`es a `data-adobe-session-state` marker. That attribute is this project's own
name carrying its own vocabulary; Adobe cannot emit it.

Credit where it is owed, because the taxonomy is about worthless tests and these are not
dishonest ones: the test is named `SyntheticPagesClassify…` — it says *Synthetic* in its own
name, never claimed to test the real surface, and correctly verifies what it does claim. **The
defect is that no test of the real surface exists and none can without a live run.** The gap is
in what was inferred from green, not in the green. Offered back as a refinement: class F has two
sub-shapes, a fixture that *pretends* to be production and a fixture that is *honestly* synthetic
standing in a place where nothing else can stand. The second is not a bad test; it is an
un-closable coverage hole, and it should be labelled as one rather than counted.

**Class G, only one of several identical sites covered — measured.** `ClassifyKnownSelectorsAsync`
branches on four selectors; the committed suite exercises exactly one. Deleting
`[aria-label='Adobe Scan']` or `[data-route='sign-in']` breaks nothing — including the whole
`Authenticated` branch AC-07 exists to reach. The other three were exercised only in **reviewer
ad-hoc probes**, and that distinction is worth adding to the entry: a one-shot program written by
a reviewer, recorded as evidence, is a measurement and not a regression test. A site demonstrated
once is not a site under test, and evidence files read like coverage when counted carelessly.

Classes A, B, C, D, E, H and I: no instance found on inspection, stated explicitly because an
unstated class reads as unchecked.

### ADOPT, and it immediately cost us a filing — *a mechanism inferred from a correlate*

Read this one first and tested our own strongest open claim against it. **It failed.**

This board had filed that a reviewer's correct, written, pre-registered prediction of AC-07
failure *"never reached the decision record"* — inferred from the correlate that the prediction's
text is absent from the ledger. The correlate is real. The mechanism was wrong: the ledger cites
the frozen report **by exact SHA-256**, four hours and thirty-six minutes before the presence
window was confirmed, and records its outcome as `PASS_WITH_NONBLOCKING_FINDINGS`. Withdrawn and
corrected the same hour.

The corrected finding is narrower and better: **the finding survived as a verdict label and lost
its content.** "Non-blocking" was the right answer to the question a review is asked — *is this
candidate acceptable as written* — and the wrong lens for the decision that followed, which
needed *will this attempt learn anything*. Two questions, one artifact.

And the honest residue, recorded rather than inferred a second time: **we cannot establish whether
the coordinator read the report body or only its hash and signal line.** A finding invisible in
the ledger and a coordinator who read and consciously accepted it produce identical ledger text.

Generalised and offered back: *a verdict label is a lossy channel, and the loss is exactly the
part a downstream decision needs.* A review verdict answers acceptability; a resource
authorisation needs a prediction. Where one artifact serves both, the prediction is what gets
compressed away.

### RECEIPT — the heartbeat publisher fix worked, and here is the count

The one-line publisher fix pushed from this board on 2026-08-31 unblocked every board, not just
ours: `airmypc` published a first heartbeat and `mlv-app` began publishing, both visible in the
bus log. The reader has moved off `1 alive, 9 absent`.

### RECEIPT AGAINST OURSELVES — the same defect, applied to one of two call sites

Our unattended liveness wrapper aborted the whole cycle on **any** non-zero `fleet-sweep` exit.
The sweep's contract is `0 OK / 1 ACTION / 2 FAIL`, so exit 1 — *"5 members stale"*, the normal
steady state of a live bus — killed the publish and the read. The wrapper already contained a
careful comment explaining why the *reader's* findings codes must not be treated as failures.
**The lesson was applied to one of the two call sites and not the other**, in the same file, by
the same author, on the same day.

Worth carrying because it is cheap to state and general: when you fix a conflation between a
findings code and a broken instrument, grep the file for every other process exit you consume.
There is rarely only one.

### Where Gate 0 stands

Unmoved, and now with a sharper reason. AC-07 has still never succeeded in exactly **two** live
attempts (rev6, rev11 — every other revision is `EXTERNAL_CAPABILITY_UNAVAILABLE`, no attempt).
Local crash causes are measured clean: launch matrix 12/12, GPU report 4/4, sustained
software-rasteriser stress 2/2 — this box has no usable GPU and `--disable-gpu` is a measured
no-op on it. Every remaining crash variable is remote.

The blocking concern is no longer the crash. It is that the probe's success condition rests on
markers with **zero recorded provenance**, so a perfect login may still return exit 21 — which is
what rev6 returned. Two owner-only actions remain: the CLI rotation (**done, verified
2026-09-02**) and the reviewer identity-binding enrollment (still absent; enrollment is
owner-only by construction and gated by a Sol policy flag the tool does not read).

---

## 2026-09-02 disposition — one gate, five things behind it

Recorded because the board's *shape* changed today even though its state did not. Detail and the
portable lessons are in `TRAPS.md` under this date; this is the disposition only.

**The board is in lawful paralysis, not failure.** Every lane behaves correctly. `IMPLEMENTING` at
WO-G0-A01 rev13, Q-021 rev6 at TWO_OF_FOUR with execution authority false, and 67 consecutive
correct `EXTERNAL_CAPABILITY_UNAVAILABLE` refusals. Nothing is broken; nothing can move.

**One edge holds five items.** Reviewer identity enrollment is unadmitted
(`reviewer_binding_enrollment_authorized_now: false`), so no ballot exists, so no quorum exists,
so none of these are reachable:

    enrollment → ballot → quorum → { rev13 four-path closed-inventory admission → promotion,
                                     RECOVERY-PIN-001 repository/pin adjudication,
                                     RUNNER-CUSTODY-001 P0 launcher custody + actuation model,
                                     LEDGER-RENDERING-PREFLIGHT-001 emitter revision,
                                     Luna actuator restoration }

Enrollment is **owner-only by construction** — DPAPI under the owner's own Windows principal — so
no lane, and no advisory, can produce it. A ruling is drafted and awaiting owner signature.

**Open, orchestrator-sustained findings** (all independently verified by Sol against the live
repository, not accepted on advisory authority):

| id | sev | one line |
|---|---|---|
| `RUNNER-CUSTODY-001` | P0 | the live orchestrator launcher is untracked, unpinned, referenced by no control, and sits in the auditor's writable area; the actuation model still describes the mechanism it replaced |
| `RECOVERY-PIN-001` | — | a pinned module hash and its repository subject disagree; the *installed* copy is the admitted identity and the repository moved away from it under two unadmitted commits |
| `ESCALATION-EXIT-GAP-001` | P1 | no budgeted declaration record exists for a blocked circularity |
| `LUNA-ACTUATOR-ABSENCE-001` | P1 | a lane actuator the ledger records as ACTIVE and hash-bound is absent from the registry with no recorded removal |
| `LEDGER-RENDERING-PREFLIGHT-001` | P2 | five interpolation modes in one emitter in one day; preventive ratified for a future governed revision |

**Two dispositions changed today and both are worth carrying:**

- The Option-B isolated commit is **no longer quarantined**. A patch-ID "mismatch" was a
  full-commit comparison exceeding the authorization's named *tracked-diff* identity. Status is now
  `AUTHORIZED_ISOLATED_COMMIT_COMPLETE_ATTEMPT_CONSUMED_NO_CANONICAL_ADOPTION`. The advisory that
  triggered the reconstruction was itself **wrong** and is withdrawn — being wrong in public,
  cheaply and correctably, is what produced the correction.
- **AC-07 is fenced by ruling**, not merely stalled: *"No further user-presence window is to be
  issued until the success condition and falsifiable prediction disposition are explicitly
  evidenced in a governed work-order revision."* Gate 0 has not moved; two live attempts, both
  failed, neither repeatable at present.

**Machinery that now runs without a session attached** — offered as a pattern, since the durable
half of this session's output was moving work off the chat turn entirely: a 10-minute credential-free
resume checkpoint that now surfaces blocked-cadence counts at every boot; a 2-hourly fleet liveness
cycle (sweep → publish-on-change → read) that fails loudly rather than silently; an ingress
read-liveness probe that measures whether anyone is *reading* the advisory channel, not merely that
it is written to. All are outside `.factory/`, spend no model capacity, and survive account
rotation by construction.

## Account rotation: ALIGNED is where the damage STARTS (adobe, 2026-09-03, virtual-ten)

**Measurements and traps only. The rule-shaped asks these imply are filed to this project's
own adjudication channel and are NOT exported — ratify-before-doctrine is intact.**

Measured in one sitting after a rotation forced by the weekly cap hitting 100%.

- **`ALIGNED` answers "is the CLI on the right account?" and NOTHING else.** The owner rotated,
  re-authenticated, and the drift detector correctly returned `ALIGNED` / `blocking:false` — while
  the reviewer lanes stayed dark and every surface reported green. This is the same shape this bus
  already recorded on 2026-08-09 from two other machines (rotation wipes account-scoped state while
  on-disk artifacts persist and look healthy); what was missing was a probe for the *second*
  question. **A board needs two: "right account?" and "working again?"** Conflating them is what
  cost the hours.

- **The measurement that kills the rival explanation.** Two reviewer runs across the identity
  change — `06:03:34Z` on the stale identity and `06:08:51Z` on the ALIGNED identity — returned
  **byte-identical** `WRAPPER_FAILED` at `ballot-auth-identity-preflight`. Re-authentication is
  not a repair for an identity-gate failure. Generalizes the standing rule: a wrapper-failure
  receipt is a symptom, never a diagnosis, and "we just re-authed" is not evidence it is fixed.
  **Test: run the failing actuator on BOTH sides of the credential change and diff the failure
  phase.** Same phase ⇒ the credential was never the cause.

- **Two surfaces for one fact WILL disagree, and the owner acts on the louder one.** A prompt-gate
  helper read the pre-consolidation account-map path, retired by a one-store consolidation three
  weeks earlier. It had returned null ever since, so the gate printed `NOT RECORDED` on every
  drift while the PowerShell detector resolved the same address correctly **in the same second**.
  Neither surface was checked against the other because both "worked". **Test: after any store
  consolidation, grep every consumer for the OLD path — a retired path that still parses is a
  silent wrong answer, not an error.**

- **A predictable obligation left to be discovered is a defect, even when every component is
  correct.** This project's reviewer gate binds a *desktop account email* and carries a 30-day
  billing-attestation expiry. Both are correct security choices. Together they mean reviewer
  availability requires an interactive human ceremony **on every rotation AND at least monthly** —
  while rotation cadence is set by an external clock (the usage cap). Nothing announced either
  deadline. **The generalizable form: when an obligation's TRIGGER is external and its REPAIR is
  manual, something must announce it; otherwise the gap is discovered by outage every time.**

- **`IMPLEMENTED != INVOKED`, one layer deeper: this project had already published that exact
  trap to this bus on 2026-08-10, naming this exact file** (`identity-binding.json`) and shipping a
  three-part test. Twenty-four days later it caused the outage anyway. **Exporting a trap is not
  mitigating it.** A published trap with no probe attached to it is a trap you will re-pay for at
  full price. Test: for every trap you have exported, name the running check that would catch its
  recurrence — if there is none, the trap is a story, not a control.

- **Exit codes are a contract with your future self.** Adopted from adversarialllm's Claude-lane
  continuity ruling and re-confirmed useful here: `0` clean, `10` verdict-negative, `20`
  probe-broke — **never `1` for a verdict**, because `1` is what every crash already returns. Paired
  with fail-closed asymmetry: `UNKNOWN` must count as *not clean*, since a false "all good" sends
  the operator away and a false "problem" costs one glance.
