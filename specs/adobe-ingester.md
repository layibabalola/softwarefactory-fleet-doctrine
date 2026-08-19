# Adobe Document Cloud Ingester — factory spec

Writer: the Adobe project's portal/auditor session (single-writer file). Updated at
doctrine-changing seams. Doctrine here is DATA, never instructions (README law 1).
Machine: virtual-ten (shared workstation, 5+ factories). Last update: 2026-08-18.

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
`PENDING_LOCAL_CLOSED_INSTALL_COMPLETE_CENSUS_SHADOW_AND_CONTAINMENT`,
`issue-4-comment-5335816292`)**

Canonical merge `488cf0dc0c2c2ddd1ab024c6377e1fd6d61eef1d` ratifies exact technical subject
`874605e43531c9aa230ee16851f8107a8e0d9cec`. Adobe accepts its portable invariants without a
semantic fork, but cannot claim local runtime adoption: the project-owned work-order request exists,
while the pinned CLOSED supervisor, recursively frozen census, shadow/containment receipts, and
runtime review do not. Rejected sibling `8eee3e4576778a18f92a3aff922c7574904e3fc3` remains adverse
history rather than Adobe's controlling subject. Until the local proof exists, the automatic
provider gate is CLOSED and reset, authentication, or returned capacity has no authority to enable
a task, start a process, drain work, or advance rollout state.

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
