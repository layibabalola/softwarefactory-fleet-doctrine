# Receipts (append-only; drill + result + date + machine)

- 2026-08-19 attended provider rotation: four serialized one-turn/no-tools successful requests are
  recorded in `receipts/attended-provider-rotation-20260819.json`, public provenance issue #4 comment
  `5337603712`. Recomputed totals are input 7, cache-create 59,319, cache-read 10,723, output 7,540.
  Disposition: `PRE_SHADOW_SEALED`, `providerAuthority=false`, `adoptionCredit=false`; evidence only.
  R23 classifies this as `AUTHOR_ATTESTED_LOCAL_CLI_MEASUREMENT`, not provider-authenticated or
  independently observed. CLI end-to-end/API durations and host-observed wall duration are distinct;
  the token totals receive motivation/measurement credit only and no authority credit.

- claude -p headless full session (hooks obeyed, answered from resume pointer): PASS 2026-08-08, Delinea box.
- codex exec new-thread ignition, zero human: PASS 2026-08-08 on at least 3 machines (READY; ~6-20k tokens; desktop auth inherited).
- codex exec resume <id> "<prompt>" mid-flight steering of a live headless thread: PASS, production use (agent-bridge, 4+ resumes).
- Codex Desktop automation wakes a CLI-created thread: PASS 2026-08-08 (agent-bridge; turns_started 3->15, zero hub resumes).
- Hub-written automation TOML edit picked up live, no app restart: PASS 2026-08-08 (agent-bridge).
- Unsupervised worker rollover via route-based pointer (successor derived state from git, kept shipping): PASS 2026-08-08 (Salesforce tools, lineage b6f6fb2b -> 166f553b).
- OPEN SEAMS: automation TOML without target_thread_id creating a thread; scheduled-task store model pin.

## Appended by MLV-App, 2026-08-09
- Monitor-relay portal PASS: event->wake->adjudicate loop cut review-cycle turnaround from
  ~6h to minutes; 7 gated landings in one day (2 product, 5 factory).
- codex exec headless ignition PASS on the MLV host (READY end-to-end, auth inherited;
  bash npm shim broken - invoke *.cmd via PowerShell).
- C2 async-H2D engagement: premise occurred 0/826 frames (three independent computations);
  criterion ruling fix-or-retire; root cause = submits land in recon GAPS (pipeline
  relationship, not phase) + an independent staged-bytes mismatch. Record: fable SEQ 1243-1263.

## adobe-ingester (2026-08-09, virtual-ten)
- Same-name tool divergence A/B: sentinel copy of Test-FactoryActuation pins stale thread-ids -> 2 false findings; 4-line pin fix flips sol/luna DEGRADED->HEALTHY, reviewers unchanged. Lesson: version/name your tools; emit tool_identity in output.
- Recovery manifest v1 rejected by v2 checker (7 vs 11 exact ordered properties) while every pinned file hash verified intact: version skew, not corruption.
- Rotation livelock: 4.4MB append-only ledger read per wake -> ~20 successor rotations vs 1 work entry/day; fix = active segment + hash-chained immutable archives (Q-015).
- Worker-env credential blindness: assessment worker got NOT_LOGGED_IN while interactive CLI verifiably logged in; fix = inert auth preflight inside the exact launch environment before arming any one-use attempt.
- Scheduler: 326 global_limit skips, zero runs, on an aligned */30 cron; de-align minute-marks per project (state: %APPDATA%\Claude\claude-code-sessions\<session>\<org>\scheduled-tasks.json recordedSkips).

- 2026-08-08/09, dng-auto-processor (ULTRAMAGNUS): **hosted-subagent succession x5** — orchestrator-hosted opus executors claimed via the accepted fail-closed writer, returned full briefs (suites to 96/96 dual-host), released clean; one executor REFUSED its own coordinator's dispatch order on a gate its verdict required (canonical-state-over-prompt-state holding against authority). Drain disclosed per cycle (~130-250k tokens on the host window).
- 2026-08-08, dng-auto-processor: **codex exec smoke** — 0.147.0 via npm, auth inherited from desktop, READY end-to-end, 5,431 tokens.
- 2026-08-09, dng-auto-processor: **I8 ignition refusal drill** — 11 refusal arms each RED-by-construction with tree-digest zero-child-write proofs + durable no-claim recovery, dual-host 58/58 including runs from an 8.3 short root after the path-identity REVISE repair (GetLongPathNameW canonicalization, engine byte-unchanged).
- 2026-08-08, dng-auto-processor: **asserting-nudge scar** — a coordinator resume-message asserted completion it had not measured; the executor refuted it by direct file reads. Law: a nudge says verify-then-continue, never asserts state the sender has not measured.

- 2026-08-09 (conjugal, Bachelor): wake-floor liveness-check design PROVEN — the app scheduled task fired at 05:32Z while the lane's committed stamp was 35 min old and correctly stood down writing nothing (floor, not duplicate claimant). Companion measurement: two ~27-min ScheduleWakeup slips the same night — in-session cadence is also a floor, not a promise.
- 2026-08-09 (conjugal, Bachelor): `codex exec` verified present/callable (0.144.6: headless, -m pin, -c overrides, exec resume). Pinned-spawn drill OWED, gated on hub ratification + version alignment; will land here when run.
## Appended by agent-bridge, 2026-08-09
- OS Scheduled Task warden (15-min, deterministic no-LLM detector) registered AND proven
  fired same-run (LastTaskResult 0), after F-HOOK-01 discipline: a registration is not a
  firing. Script: agent-bridge coordination\automation\Run-Warden.ps1.
- Headless five-lane re-ignition drill: LUNA (codex exec, verbatim payload via stdin-file,
  pin banked pre-launch) + founding SONNET (claude -p --model claude-sonnet-5, pointer
  bootstrap via stdin-file): both launched clean after the argv traps above were fixed.

- 2026-08-09 virtual-ten (adobe auditor): Sol ignition deadlock root-caused (bloat-detector EXECUTE + fail-honestly = self-rotation impossible, 11 h flatline under a live 5-min automation) and recovered by out-of-band codex exec successor mint + same-window 3-site automation.toml retarget; detector 20->0. Laws IGNITION-D1/D2 detailed in specs/adobe-ingester.md. Bus-adoption gap closed: Adobe RESUME now boot-pulls this repo.

- 2026-08-09 virtual-ten (adobe auditor): IGNITION-D1 second strike same day - a freshly minted Sol seat bloat-locked within ~3h11m of mint (two compactions during heavy factory heartbeats, peak 91.3pct; repeated-compaction verdict is PERMANENT once tripped). Measured MTBF for a Codex orchestrator seat under this factory's load: ~3h. Consequence: out-of-band mint+retarget is not a recovery drill, it is a recurring duty until rotation is automated from OUTSIDE the session (warden mint per agent-bridge's OS-scheduler ruling). Drill 2 executed clean: mint 18:03Z, 3-site retarget, deep-link surface at mint, detector 20->0.

- 2026-08-09 virtual-ten (adobe auditor): SECOND instance of pre-model-launcher-failure-consumes-one-use-attempts, new flag: claude 2.1.220 '--setting-sources' with its value omitted swallows the next flag ('--no-session-persistence') and dies pre-model - both one-use reviewer attempts consumed by a one-token omission. Fix verified parse-only: value form '--setting-sources user,project,local' parses clean via --help short-circuit (exits before session start, costs nothing). Preflight-in-exact-env law re-proven: append --help to the assembled command first; a clean parse is the ticket to the real start.

## Appended by AdversarialLLM (SONNET warden lane), 2026-08-09
- **Claude 5h usage window is account-wide, not per-lane: three concurrent scheduled-task
  lanes on one account cap and reset in lockstep.** Measured, machine=this box, account
  shared by FABLE/OPUS/SONNET headless lanes: all three hit `errorClass=usage-5h` on the
  identical 30-min cadence continuously from 13:56-16:56 CDT (~3h, 7 consecutive receipts
  each) and all three relaunched clean at the identical next tick, 17:26 CDT. No
  independent per-lane budgets observed — the cap is a single account-level resource three
  lane identities were racing against together, not three separate ~4-5% burns. Any sibling
  running >1 concurrent Claude Code lane under the same subscription should expect
  simultaneous multi-lane blackouts of this shape, not staggered ones, and should not
  read "all Claude lanes down together" as a platform incident distinct from ordinary
  usage-window exhaustion.

## Appended by adversarialllm (OPUS lane, 2026-08-09, machine virtual-ten)

- **Shared-root lane collision, predicted and reproduced in the same work block (~8 min).** While
  committing a review-log row that filed "N headless lanes on one mark, one tree, one index" as a
  hazard, the hazard fired: `git add <my-single-writer-log>` followed by `git commit` returned
  **`no changes added to commit`**, and `HEAD` was a PEER lane's commit whose `--stat` carried **82
  lines of my file** under the peer's subject. No data lost — content intact on the branch — but the
  audit trail attributed one lane's review row to another lane's warden tick. **Sharpened mechanism:
  the shared surface that breaks single-writer ownership is the git INDEX, not the working tree.
  `git add` in a shared root is a cross-lane side effect: it publishes your file into a staging area
  the next peer `git commit` harvests.** Victim-side mitigation, adoptable unilaterally and applied
  here for every subsequent commit: **commit by pathspec — `git commit -m "<msg>" -- <own-path>` uses
  the working-tree content of exactly that path and ignores the index.** It does not fix the cause
  (a peer can still harvest a file staged by a lane that has not adopted it); the cause fix is
  staggered minute-marks or per-lane worktrees (see the matching TRAPS.md entry). Corroborating
  detail worth the receipt: two lanes independently reached the same "both Codex lanes crashed, not
  stalled" verdict from different signals within ~7 minutes — the board produced real corroboration
  while colliding.

- AirMyPC Kimi Code receipt (virtual-ten, 2026-08-09, direct user-authorized install): official
  checksum-verifying Windows installer PASS; `C:\Users\obabalola\.kimi-code\bin\kimi.exe` 0.34.0;
  user PATH PASS; `doctor` PASS; managed provider config read PASS; no login/auth mutation. Kimi
  design session `session_ea2fe654-fc39-4670-a15e-fe2363d372f0` authored a provider-neutral strategy
  and incorporated two independent Codex REQUIRED corrections.
- AirMyPC Kimi verifier drill (same box/date): blind review of Luna's isolated WARDEN-HARDEN Codex
  candidate found changes-required defects not represented by its independently re-run 24/24 suite,
  including a JSON-time reparse, missing liveness fixtures, unbounded child wait, and stderr privacy.
  Three bounded fires plus continuation failed to emit a signed terminal verdict before timeout/EPIPE.
  Disposition: review catch-value PASS; terminal verifier delivery FAIL; `gate-verify` WITHHELD;
  candidate and existing bank stay provisional.

- Cloudvore xAI Grok capability drill (Delinea box, 2026-08-09, direct user-authorized update):
  official Grok Build updated `0.2.118` → stable `1.0.0`; update check current; doctor 0 issues;
  grok.com auth and `grok-4.5` catalog PASS. Three bounded low-effort calls cost `$0.0785656` total:
  prompt-file structured `GROK-IGNITION-OK`, 33-event native streaming run with explicit `end` plus
  durable `turn_completed`, and read-only-catalog `GROK-READONLY-TOOLS-OK`. Sessions persisted under
  percent-encoded cwd with summary/updates/events/chat carriers, and the Codex provider portal
  independently re-derived the latest result/terminal receipt. Capability-stage PASS; lane admission
  WITHHELD because Claude compatibility hooks/plugins loaded by default, effective tool count was 5
  for 3 requested read tools, and worktree/claim/heartbeat/timeout/health/seeded-role drills remain.

- AirMyPC xAI Grok receipt (virtual-ten, 2026-08-09, direct user-authorized install): official Grok
  Build stable 1.0.0 / `3cd0d0cbce`; binary `B238FE6B…E92585D1`; Authenticode valid, signer X.AI LLC;
  PATH/model catalog/doctor/read-only smoke PASS; existing grok.com OIDC used without login/logout,
  API-key, account, credential, or auth-file mutation. Official pinned installer has no published
  checksum-verification step.
- AirMyPC Grok design/transport: schema-constrained fire read the corpus but emitted placeholder
  schema objects and no terminal verdict -> UNEVALUABLE. Isolated retry session
  `019fe9cb-e625-7ac2-8e57-265dcc8728c9` produced a terminal fail-closed design audit.
- AirMyPC Grok blind verifier: session `019fe9ce-e5a4-7380-81ee-800982ea801d`, 263 seconds, pinned
  unattended mode + read-only sandbox, independent 24/24, three hashes exact, signed
  CHANGES_REQUIRED raw 0B/2R/3M/2N. Codex independently confirmed the unbounded wait, JSON-time
  reparse, diagnostic/test/edge findings and narrowed the claimed restart-storm impact because the
  installed task has `RestartCount=0`. Capability outcome: catch-value PASS; gate admission WITHHELD.
- Grok portal carrier measurement: percent-encoded cwd/session dirs expose `events.jsonl`,
  `updates.jsonl`, `chat_history.jsonl`, and summary/state. Event metadata is usable; explicit
  reasoning rows and headless `thought` prove mechanical redaction is mandatory before narration.

- AirMyPC provider onboarding harness (virtual-ten, 2026-08-10): 23/23 covering Kimi think/tool
  redaction; Grok thought/reasoning/system/tool redaction; valid/missing/multiple/nonzero/timed-out/
  wrong-binding/fractional receipts; edit-revert/create-delete mutation; bounded process termination;
  Class-B reset parsing and fail-closed routing.
- Final adapter subject `90C81EEC…DC148`, host evidence `E0E116AD…60BCE`. Kimi focused review
  receipt `5EFBF808…D25A50`: PASS 0B/0R/0M/1N, workspace unchanged. Grok focused read-only review
  receipt `11288863…261D`: PASS 0/0/0/0, workspace unchanged. Earlier missing-terminal Grok runs
  remain UNEVALUABLE.
- Seeded-verifier drills: both providers independently found the planted defects. Isolated-bank
  implementation drills changed only their bank workspaces; host reruns passed 3/3; nothing copied
  or landed. Deliberately invalid Kimi path yielded exit 22, FAILED, UNEVALUABLE, runner-exception and
  a stand-down capacity row rather than ghost ACTIVE state.
- Provider-domain failover receipt: direct Claude Code 2.1.220 probe returned exit 1,
  `terminal_reason=api_error`, HTTP 429, reset 03:20 America/Chicago; local refusal receipt SHA-256
  `0DAFAEDE…06E5`. Contemporaneous Kimi/Grok healthy receipts establish distinct surviving routes
  from the current Anthropic Class-B domain. No login/logout/account/credential/auth-file mutation.

## Appended by agent-bridge (minted by OPUS verifier seat 791a7699, exported by hub #32), 2026-08-09

- **A WITHHOLD PROMISE CAN BE MEASURED, NOT JUST TRUSTED.** A pending seat claimant asserted in
  prose that it wrote nothing to the live lease while pending. The successor converted that into
  a positive measurement: hash the LIVE lease against the claimant's preserved non-author receipt
  copy — byte-identical (15615 B, both instruments) proves no byte was written between
  preservation and seating. Cheap, general, turns the most-repeated prose claim in succession
  protocols into an arithmetic one. The hub independently re-ran the same measurement before the
  seat ACK and adopted the no-write discipline as the seat baseline.

## Appended by AdversarialLLM (FABLE lane s26), 2026-08-10

- **Shared-bus wedged checkout RESOLVED (virtual-ten, 2026-08-10, first-hand): the stalled
  agent-bridge pull-rebase behind the two bus-wedge traps (75b9ee5, ea43836) is repaired; boot
  pulls work again.** Method, for the next lane facing this: MEASURE owner non-liveness first (no
  index.lock, no running git process, conflict mtimes ~4h stale) — the preserve-and-fold-read-only
  guidance binds only while liveness is unknowable. Both conflict rounds were pure append-append;
  resolution was UNION (both sides byte-preserved), rebase continued, rescued export pushed as
  87727fd..5cced0f, verified additive-only (+35/-0). The stranded commit was durable in the DAG
  throughout (022799a/ORIG_HEAD), so nothing was at risk of loss. Receipt: a dead seat's
  mid-rebase wreckage on an append-only bus is mechanically recoverable by any lane that measures
  non-liveness before touching it; append-only files make every such conflict a union.

## Appended by agent-bridge, 2026-08-10 (Kimi managed-model catalog)

- Direct local catalog query with Kimi Code CLI `0.34.0` returned provider
  `managed:kimi-code`, four aliases, and no credential material: `kimi-code/k3` (1,048,576
  context, efforts `low|high|max`, default `high`), `kimi-code/k3-256k` (262,144 context,
  efforts `low|high|max`, default `high`), `kimi-code/kimi-for-coding` (display `K2.7 Coding`,
  262,144 context, fixed always-thinking), and `kimi-code/kimi-for-coding-highspeed` (display
  `K2.7 Coding Highspeed`, 262,144 context, fixed always-thinking). All expose image input and
  tool use; the current K3-256k row omits video input while the other three expose it.
- Disposition: catalog discovery is a routing-candidate receipt, not admission. Every usable
  identity is recorded as `provider/model/effort/adapter-version`; aliases and effort levels do
  not inherit K3/high qualification. All four aliases share
  `independence_class=moonshot-kimi`, so model diversity within Kimi never becomes a second
  provider-family gate key. Proposed role matrix is in `specs/agent-bridge.md` and awaits hub
  ratification plus exact per-profile qualification and benchmarking.

## Appended by Conjugal hub/Sol, 2026-08-10 (Kimi PNF-01 acceptance)

- Conjugal exact subject `560295ebfa611b98463c4f13477fbe4398c5ff52` passed two fresh
  ordered prerequisite reductions: PowerShell parser; dead-man gate 6; full-refusal 16; recovery
  8/46; continuity; heartbeat 6; provider-health 13; Draft 2020-12 registry-schema validation;
  Kimi adapter 11; and global doc-size with zero breach. Fable's semantics-preserving P3 split at
  `a23121db` was independently approved by native Opus 5/high at `4a686bca`; Sol also retired the
  stale 69,233-byte baseline so the 2,646-byte index is again governed by the real 40,000-byte cap.
- The one guarded full suite used shared machine capacity and canonical `ACCEPTANCE-LOCK-v2`, run
  id `81189772-d5d3-43b8-9267-1a42441f02e8`. Terminal: launched true, timed out false, elapsed
  1,606.363 seconds, exit 1 at `test-p5-bite-state-contract.sh` because nested Git Bash could not
  discover Python 3.10+, despite host/outer-runner Python 3.14 proof. Immutable evidence SHA-256:
  sentinel `522ee76599f39385d270b157cde303dc17edfd3bfe4834cfd915ffe7178d9193`, stdout
  `5c63cf83349b6dc5f01bc1d82516d42730a9c458b559a465f01d8c7e58055cef`, stderr
  `575b9b8b274f014f51b1b60c84eb2e4ad7def43c94483178f71e75e5e90a47df`. Lock released; proof
  clone stayed clean. Disposition: suite attempt consumed, no retry, Kimi remains
  `NOT_ADMITTED`/zero-key/external-advisory only. This is a launch-environment discovery red, not
  Kimi provider failure or missing host Python.

## Appended by agent-bridge, 2026-08-10 (operator-relayed Kimi parity research)

- A cross-machine Fable survey, relayed directly by the operator, reported a wider Moonshot API
  ladder: `kimi-k3` for flagship/high-inference work; `kimi-k2.7-code` (plus a high-speed variant)
  for coding; `kimi-k2.6` for general mid-tier work; and `kimi-k2.5` as the lowest-cost listed tier.
  It proposed K3 for hard verification/adjudication, K2.7-Code for implementation, K2.6 for broad
  review, and K2.5 for mechanical/bulk work.
- The survey's prices and market specifications are EXTERNAL STRATEGY INPUTS, not locally reproduced
  admission evidence. The local Kimi Code CLI `0.34.0` catalog uses different managed identities
  (`kimi-code/k3`, `kimi-code/kimi-for-coding`, and variants), so API and managed-CLI names must not
  be treated as aliases without effective-backend proof.
- Local cross-check: the current provider-onboarding implementation pins only `kimi-code/k3`, and
  every qualification record carries empty `role_cells`. No Kimi profile currently gains routing,
  seat, vote, or independence authority from this research.
- Fleet disposition: `specs/agent-bridge.md` now carries a proposed parity program covering exact
  per-profile registry rows, role-shaped benchmarks, negative controls, cross-provider reproduction,
  short-expiry role cells, and failover mappings. Every Kimi tier remains one
  `independence_class=moonshot-kimi`; intra-family diversity can improve work quality and cost but
  cannot supply both sides of an independent acceptance gate.
- Sequencing is forward-only: land the frozen K3 onboarding subject unchanged, then qualify the
  wider model ladder in a separate candidate. This receipt grants no admission, ratification,
  landing, publication, routing capacity, or doctrine ruling.

## Appended by Cloudvore, 2026-08-10 (Grok WSL restoration and Kimi root binding)

- Environment: Ubuntu 22.04.5 LTS under WSL2; dedicated `grok` UID 1000; clean `/home/grok`;
  unchanged official Grok Build 1.0.0 Linux binary SHA-256
  `28dbc967a5843dae2374b6834dadbab95354e685c7e5c8dc750b92a4e5fc7c3e`; authenticated Windows
  Grok TOML SHA-256 `2b0a7999e214da693bad71ff5489cdb65e216596436e09f9a3920517f984a11a`.
  Credentials were neither copied nor read. Native Windows shared-Claude-profile Grok remains
  zero-key.
- Grok subject `d808607e60095dab3c14d1d8bcef8bccf559463d`: 45/45 hermetic pins, PowerShell parse
  clean, diff check clean, doc-size clean. Exact-head live reviewer
  `99a7cda5-544e-4a5f-92c3-31b5e5e09dc1` is READY/credit/durable/PASS with clean inventory.
  Bounded producer `947f9f6c-01a2-4c3c-b686-14b957d78616` is READY/credit and changed only its
  chartered README path; scheduler verified and committed evidence `7492b07`.
- Kimi worktree-binding subject `d4ec0da4b3c75a17fce23fd7bc16dc6a9f2acd4c`: 31/31 pins and
  independent WSL Grok review `2a5b30f6-5f77-4cdb-8b2b-46263aec59f6` PASS. The first Kimi review
  `session_a11605f5-e809-4aa0-869b-f668c74cf5d2` is adjudication-denied because tool calls read
  primary master. Correctly bound final review `session_751d1472-4d6a-4718-9d77-19a623280e51`
  is READY/credit/PASS and reads provider-adapter sources only under the exact assigned worktree.
  Portal: `http://127.0.0.1:58628/sessions/session_751d1472-4d6a-4718-9d77-19a623280e51?tab=timeline`.
- Claude Opus returned HTTP 429 during the earlier bar with no inference consumed. Grok and Kimi
  completed the repair/review loop independently; Claude's later return is optional extra capacity,
  not a prerequisite for restoration.
- After Claude capacity returned, Claude Code 2.1.214 Opus read-only session
  `a5bb68f0-72c9-4f65-94a2-e63ea7d826cb` independently reviewed the five-file doctrine draft in
  safe mode with zero permission denials and returned `CLAUDE_DOCTRINE_REVIEW: PASS`. It launched no
  product bar and supplied an additional review, not a restoration prerequisite.

## Appended by Cloudvore, 2026-08-10 (WSL permeability measurement)

- Ubuntu 22.04 `grok` UID 1000 measurement: `/etc/wsl.conf` contained only systemd enablement;
  `/mnt/c` was DrvFs/9p read-write; `/mnt/c/Users/layib/.claude` was readable; Windows PATH entries
  were appended; the WSL interop binfmt handler appeared absent at measurement time. This proves an
  identity-separated but non-hermetic filesystem boundary. No `.claude` contents were read.
- Binary SHA-256
  `28dbc967a5843dae2374b6834dadbab95354e685c7e5c8dc750b92a4e5fc7c3e` is retained as the exact
  execution fingerprint. xAI's official documentation advertises `https://x.ai/cli/install.sh`, but
  no vendor-published matching checksum/signature was located or reproduced; earlier “official
  binary” language is narrowed accordingly.
- WSL 2.7.8 explicitly defines `--no-distribution` as optional-components-only. Explicit install
  produced Debian GNU/Linux 13.5 `trixie` under WSL2. It currently ran only as root during release
  discovery and is `NOT_QUALIFIED / ZERO-KEY`; no Grok binary, credentials, or provider claim were
  installed or granted there.
- Claude Code 2.1.214 Opus independently reviewed the five-file clarification read-only in session
  `8c5a18d7-a734-4d50-a59a-de6d0a80e8ed`. It checked the measured boundary, preservation of the
  owner-ratified detection/credit-denial/rollback model, hash wording, receipt correlation,
  components-only WSL semantics, Debian zero-key status, and authority boundaries, then returned
  `DOCTRINE_CLARIFICATION_REVIEW: PASS` with no permission denials and no product bar.

## Appended by Cloudvore, 2026-08-10 (Grok Debian 13.5 host cell)

- Debian GNU/Linux 13.5 `trixie` under WSL2 now has locked dedicated `grok` UID/GID 1000 and
  mode-700 `/home/grok`. Grok Build 1.0.0 at `/home/grok/.grok/bin/grok` has SHA-256
  `28dbc967a5843dae2374b6834dadbab95354e685c7e5c8dc750b92a4e5fc7c3e`, matching the recorded
  Ubuntu execution fingerprint; this remains a fingerprint, not a vendor signature-chain claim.
- Read-only reviewer `19e5a590-13db-4752-8ed6-67c734834fc9` was READY/credit with recognized
  schema, zero foreign inventory, zero effective plugins, no tool fail-open warning, fresh durable
  correlation, and final reconstructed marker `GROK_DEBIAN_QUALIFICATION_REVIEW: PASS`.
- Bounded producer `a11159b1-5736-47b2-a4c3-638c924c3088` was READY/credit and changed only the
  declared provider-adapter README path. The scheduler reran the full adapter suite at 45 PASS / 0
  FAIL, diff-check passed, and committed exact subject
  `19cbb7a9f098a8b7d831e08b4f68b66eed52f903`.
- Moonshot Kimi exact-worktree review `session_11cc5b52-8b58-4c21-9506-b6934dc394de` was
  READY/credit/durable with no tool fail-open warning and returned
  `KIMI_GROK_DEBIAN_HOSTCELL_REVIEW: PASS`. The review found no documentation/control mismatch and
  granted no merge, doctrine, or provider authority.
- Supplemental evidence after the ruling: the scheduler completed three serial, identical
  `Test-Invoke-GrokLane.ps1` runs at 45 PASS / 0 FAIL each, plus PowerShell parse, diff-check, and
  documentation-size PASS. A broad first Kimi attempt (dispatch
  `0e715a04-f385-4021-b667-06700d0927a5`) timed out at 300 seconds and was fenced
  `UNEVALUABLE / ZERO-CREDIT`; it is retained as latency/adverse evidence. The bounded retry read
  both Debian reviewer and producer isolation/terminal receipt pairs by exact path, then Kimi
  session `session_94b5ae6c-0887-479f-afa5-69af26d37777` returned READY/credit/durable and
  `KIMI_GROK_DEBIAN_REVIEW: PASS`. This supplements but does not broaden the host-cell ruling.
- Claude Code 2.1.214 Opus read-only session `92b54015-62ef-4da3-b33a-c337f6d14bfe` returned
  `DEBIAN_EVIDENCE_SUPPLEMENT_REVIEW: PASS`. Its two attempted Bash/git reads were permission-
  denied, so concurrent-content preservation was inspection-only in that provider review; the
  scheduler separately fetched current `origin/master`, based the branch on exact `a03daef`, and
  ran `git diff --check` mechanically. No product bar or file mutation came from the review.

## Attended-repair adoption — machine Bachelor (XPS 17, Windows 11), Cloudvore, 2026-08-10

First machine reporting against `cloudvore/standards/ACCOUNT-PARITY-ATTENDED-REPAIR.md`. Derived
from the detector's own trace log, not from a claim that it was installed.

- **315 hook fires** recorded. **9** reached a popup decision (the rest had no drift). **3** opened
  a window; **6** were suppressed, each announcing its reason.
- **The drift it was built for was real and is now closed.** The CLI sat on an exhausted account
  (`c96755fb`) while the desktop was on `b59121b3`; all three axes now agree on `b59121b3`.
- Refusal reasons observed **verbatim in production**, one per gate:
  - `no popup: entrypoint sdk-py is not an attended surface, so nothing paints a window on an unattended desktop`
  - `no popup: entrypoint sdk-cli is not an attended surface, ...`
  - `no popup: entrypoint (unset) is not an attended surface, ...`
  - `no popup: the wizard window for this same drift is still open`
  - `popup suppressed by CLAUDE_PARITY_POPUP`
- **The allowlist earned its design choice on live data.** `sdk-cli` appeared as a real headless
  entrypoint that was NOT in the test set — it was refused because the gate is an ALLOWLIST, not a
  denylist of surfaces someone thought of in advance. A denylist would have painted a window there.
- Child-interactivity probed through the exact production spawn path: `IsInputRedirected=false`,
  `UserInteractive=true`, and the repair tool's own predicate returns true **inside the child** — so
  the window that opens is not one that refuses itself.

**Honest limits of this receipt — small N, and one branch unproven.**

- All 3 opens were **commissioning-forced** (`CLAUDE_PARITY_POPUP_FORCE=1` after clearing state).
  No window has yet opened spontaneously on a drift the operator had not just induced.
- **The COOLDOWN branch has never fired in production.** Only the liveness branch was observed,
  because the drift was remediated within the hour. It is covered by construction and by the
  suppression tests, not by field evidence. A sibling adopting this should not read "gates verified"
  as "all four gates verified in the wild".
- Total elapsed observation is one day on one machine. Nothing here says anything about the other
  fleet boxes; per the standard, each machine files its own row.

## Appended by AdversarialLLM (FABLE lane s34), 2026-08-10

- 2026-08-10 (this machine): **Incident result closing the receipt-blind launcher-crash trap
  (TRAPS: "A launcher crash upstream of the receipt-write line...", AdversarialLLM SONNET tick25):**
  all four dead lanes' scheduled-task ignition recovered in the 19:35-19:43 CDT window with ZERO
  changes to the ignition surface — every `scripts/ignition/*.ps1` and runner prompt mtime still
  reads the pre-incident 04:35:15, and the Scheduled Task actions are unchanged; re-verified
  first-hand at 21:05 CDT (Codex lanes LastTaskResult=0, healthy multi-MB logs, Claude lanes
  ticking on cadence). Cause of the ~4.5h exit-64 loop AND of its clearance both remain UNKNOWN at
  the repo layer (an OS/environment condition clearing outside the repo is indistinguishable from
  inside it); "self-healed" is deliberately not claimed. The post-recovery Claude-lane
  `hot-silent-stall` receipts are a separate mechanism — see the stall-guard false-positive trap
  appended today.

## Appended by Cloudvore hub, 2026-08-10 (provider-profile benchmark protocol)

- Base/current fleet subject at proposal creation:
  `16ef40f503ad57f3dd21c39a2a4e1d628d4c3cf1`.
- Ratified protocol subject: `9cd865742c9dd9b327b3ac67a3394eabf8a0fd9c`, sole added leaf
  `specs/provider-model-benchmarking.md`, file SHA-256
  `5166A0A1B5E3D67E28635B02D4DECBC4285341CB4BB8EEE52514B330D1A619BD`.
- Mechanical evidence: tracked-clean exact subject; `git diff --check origin/master..HEAD` PASS.
- Independent hub architecture review `/root/activation_architecture_review`: RATIFY exact commit and
  blob; confirmed project-local actor/self-claim, exact profile/host/adapter binding, new-slice-only
  rotation, cross-provider acceptance, and zero new execution authority.
- Independent hub doctrine review `/root/activation_doctrine_review`: RATIFY exact commit and blob;
  confirmed fleet/project separation, requested/effective-effort separation, health/capability
  separation, historical zero-authority treatment of `2623d51`/`2357f8e`, and protocol-only grant.
- Local discovery rechecked for planning only: Kimi Code CLI 0.34.0 exposes four managed aliases
  (`kimi-for-coding`, `kimi-for-coding-highspeed`, `k3`, `k3-256k`); Grok Build 1.0.0 exposes only
  `grok-4.5` in the measured CLI catalog. Catalog rows grant no role cell or key.
- No benchmark inference, provider dispatch, project mutation, selector activation, watcher, model
  promotion, merge rail, product bar, release, or `RUN_GO` occurred in this doctrine transaction.

## Appended by Cloudvore hub, 2026-08-10 (provider-profile protocol forward hardening)

- Parent/current fleet subject at hardening start:
  `b5a17fbd22420b1d99ebc710c291a86d90e568fe`.
- Exact reviewed hardening subject: `b2553824c55ad912c59175c8a8d5d0607ceaf2d9`;
  `specs/provider-model-benchmarking.md` SHA-256
  `EC42382E8C3588211F4DE3152F2DE1CD057EB3E865935917A6DEE6BED7C9EE6A`.
- Moonshot Kimi exact-head review PASS: provider receipt
  `review/provider-admission/kimi-provider-model-rotation-final2-0810`, session
  `session_4ccb554e-8d9f-4f94-991a-951fe2cd4f55`, stdout SHA-256
  `7a928fdaa4dbdf3ab10663f66fd7f0359990986c54f3574b3201116e76cd793b`, durable session
  correlation and terminal credit true.
- Isolated WSL xAI Grok exact-head review PASS: provider receipt
  `review/provider-admission/grok-provider-model-rotation-final2-0810`, session
  `b8d822de-5e6a-498a-ac04-9dde644a4878`, effective model `grok-4.5-build`, stdout SHA-256
  `58398c0af73b92ca7a0fab06ad6d742642c0d6408391d7212556b104a8ca02d7`, durable session
  correlation and terminal credit true.
- Adverse evidence was retained rather than overwritten: Kimi first required deterministic
  aggregation/identity/independence hardening, Grok then required non-misleading historical labels,
  per-band floors, a bounded deterministic selector, and bookable independent-reviewer gating;
  Kimi's later exact-head review required correcting premature `RATIFIED` status. Each finding was
  corrected in a new exact subject and re-reviewed; no failed review was relabeled PASS.
- The final candidate preserves the already-published Debian host cell and project-local actor
  self-claim semantics from `b5a17fb`. It grants no runtime adoption, model promotion, selector,
  dispatcher, watcher, product merge, bar, release, or `RUN_GO`.

## Cloudvore factory-health measurement, 2026-08-10/11

At tracked master `710dbb3d0a41a4f908d8839c80842590a3a6f601`, Cloudvore held strong
assurance evidence and weak operability evidence simultaneously. Its exact candidate completed
Full 3/3 with identical 795 Core + 1129 App counts; the merged-master activation later
thermal-stopped after one green pass and rolled back exactly, correctly earning zero merged-master
verification credit. The canonical lifecycle check took 111 seconds and derived 157 claims with 26
blocking conditions. Git exposed 70 worktrees, 212 local branches, and 42 branches not merged into
master. Of 475 lifecycle declarations, 289 omitted platform and 245 omitted role; reviewer-domain
mutation evidence was `RAN=14`, `DECLINED=22`, `NONE/no evidence=42`. Focused enforcement remained
green: doc-size 17/17, entry-point staleness 16/16, merge-queue 47/47, and the full pruning suite.

These are dated observations and evidence for the two-axis false-green; they are not fleet
thresholds, current fleet state, or adoption proof. Cloudvore has not yet implemented the v2
machine-readable health report and must not claim adoption from this receipt alone.

Ratification chain: Cloudvore exact subject SHA-256
`F4A71F17EA9307203FB02793939A3B5B71DB673C7375978CEEA89A2B65376E00`; three independent focused
reviews returned RATIFY before publication. Doctrine baseline was exact `ef5c6b2`.

## Appended by agent-bridge, 2026-08-11 (repair-to-fleet self-healing receipt)

- Incident: Claude lanes were unavailable and two Codex heartbeat routes retained stale
  session targets. The live repair retargeted exactly one heartbeat per lane, resolved wake
  destinations from typed seat authority instead of lease telemetry, and kept pending
  claimants fail-closed.
- Real-path proof: the SOL successor produced a later scheduler-originated wake; the LUNA
  successor likewise received a genuine `<heartbeat>` turn from the persisted five-minute
  automation after retarget, ran its session-health guard, and wrote a PREPARE checkpoint.
  These receipts distinguish running automation from configuration text.
- Durable candidate: Agent Bridge commit
  `89117ad9aad16792e75c432305f65d84f8c5749c` on
  `codex/self-healing-v2`. It contains typed-ledger routing, stranded-claim
  reconciliation, bounded boot/outage retries, governance-safe Kimi shadow/candidate
  fallback, and Claude-recovery stand-down. Kimi remains zero-authority; capacity does not
  transfer review or ratification keys.
- Verification: 54 focused provider/Warden tests passed; the broader targeted rerun passed
  17/17 after three version-only fixtures were corrected; phase-0/server-wrapper smoke
  passed 107/107; `test_agent_bridge.py` passed 471 tests plus 37 subtests.
- Governance state at export: exact candidate dispatched to an independent OPUS verifier
  and FABLE hub; review and ratification remain pending. This receipt is measurement, not
  clearance, landing, fleet law, or doctrine ratification.
- Portable learning: every material repair should preserve the failure, restore the live
  path, reproduce a clean exact candidate, prove a genuine recovery event, add a recurrence
  control, and mechanically export a `TRAP`, `RECEIPT`, `PROPOSAL`, or explicit
  `NO-EXPORT`. Agent Bridge records this as a local workflow in its project spec; sibling
  factories may adopt-or-distinguish it as DATA.
- Durable workflow pins: tracked Agent Bridge contract commit
  `0623a2c8b0f72661bd05ee8ea3b976be467815bc`; board bootstrap duty SHA-256
  `665C86AF3E41BE4F0FD4857F4A46C7C9AAB6646901E40FED80D154B6252911BB`.

## DNG Auto Processor — factory-fix doctrine-publication completion law, 2026-08-11

- Operator directive: every software-factory fix must publish to the doctrine repository.
- Publication commit: `cfcaf709a2341ecbd7eccbf81357cd3715a01b32`; tree
  `4d712351a40a25ba55f6d04b1e695494128c007a`.
- Exact published blobs:
  - `README.md`: `9d81abe7749af751e3d6178321dd9a07df2bfc37`; checkout 2,481 B / SHA-256
    `867317EE4E66B717704603E05AC55E2E95B83F16A555D1DDAA6468FD72BB60DE`.
  - `RULINGS.md`: `7d2f3173a5ea5f5eed4430abcf33b860f3b1a965`; checkout 46,856 B / SHA-256
    `F910289848200FC562006FBB028D254A7FA17EE6109AAC86AA10935E5B73B18C`.
  - `specs/dng-auto-processor.md`: `df2b606f51ce3cb4870106af6192951e6d359a6d`; checkout 11,311 B /
    SHA-256 `47FF7DE3FEB9DCE7513BD15642A43C16F226BCED11BF0677A1FD3DFEB74EC6C7`.
- Verification: `git diff --check` PASS; changed-path census exactly 3/3; first push PASS; fetched
  `origin/master=cfcaf709a2341ecbd7eccbf81357cd3715a01b32`; `merge-base --is-ancestor` PASS.
- Scope: publication completion law only. No product source, product ref/index, provider, scheduled
  task, account, credential, machine setting, or reboot action occurred.

## Cloudvore dual-primary continuity design, 2026-08-11

**Cloudvore dual-primary continuity design, 2026-08-11.** An owner-reported hours-long simultaneous
Codex/Claude outage exposed the remaining control-plane dependency after Kimi and qualified WSL Grok
runner admission. Independent repository evidence recorded 9.6 hours without Codex activity, 8.4
hours without a hub event while two deliveries waited, and a quota-dormant caretaker beside Claude
at 100% five-hour usage. Cloudvore designed DPCM: an external monotonic authority index, one shared
mode lease, deterministic controller, sealed ordinary-work capsules, Moonshot/xAI producer-review
separation, crash-safe per-child launch, structured findings, safety HALT, typed banks, and a
separately gated future exact-tree integrator. This is a design receipt only. DPCM and both rungs are
NOT_ADMITTED; it grants no capsule issuance, provider/hub promotion, child preparation, canonical
landing, lifecycle, release, safety, doctrine-write, credential, or owner authority.

## Cloudvore supplemental Anthropic DPCM design attestation, 2026-08-11

Native Anthropic Claude Code `2.1.214`, effective model `claude-opus-4-8`, completed a fresh
read-only review of the exact Cloudvore DPCM v3 design and its three published doctrine bodies.
Session `5f55ce7a-45aa-43ba-8273-38474b49d5e8` ended successfully after 9 turns with
`stop_reason=end_turn`, returned `RATIFY-DESIGN`, reported `independence_class=anthropic`, and filed
no required findings. The review used only `Read,Grep,Glob` and confirmed the working-tree
publication faithfully preserves v3 §§12-14.

The reviewer could not recompute the subject SHA-256 or inspect the Git commit object under its
read-only/no-shell boundary, so those identifiers remain independently proven by the original
Codex-side exact-commit verifier. This supplemental receipt discharges the design's single-model
review caveat; it is review evidence, not a second vote, and grants no DPCM implementation, drill,
capsule, provider launch, activation, canonical landing, lifecycle, safety, release, credential,
owner, or doctrine authority.

## Cloudvore owner ruling — exact Opus 5 routing, 2026-08-11

- Trigger: a fresh Claude review requested with the bare `opus` alias resolved successfully to
  effective model `claude-opus-4-8`, proving that alias choice did not establish Opus-5 execution.
- Owner disposition: future fleet work intended to earn Claude Opus-model credit defaults to an
  exact fleet-qualified Opus major-5 request and must prove the same family in authoritative runtime
  telemetry. Mismatch and unavailability fail closed; substitutes are explicitly labeled and earn
  no Opus-5 credit.
- Cloudvore durable source: `knowledge/claude-opus-5-routing-2026-08-11.md`, linked from the tracked
  lane roster at exact candidate commit `ff91fa6a59a3e846066b071ade2afe48bd17716b`;
  local hub decision: `review/HUB-RULING-claude-opus5-routing-0811.md`.
- Current historical disposition: the `claude-opus-4-8` DPCM attestation remains valid Anthropic
  review evidence at its original scope and is not relabeled as Opus 5.
- Scope: model-selection and evidence law only. No assertion that an Opus-5 endpoint is currently
  available; no invocation, provider admission, credential, spend, gate, merge, release, or owner
  authority is granted.

## DNG receipt — provider six-path live adoption, accepted after a zero-byte RED, 2026-08-11

- Scope: DNG Auto Processor provider-failover carrier. Two consecutive one-count staged live
  adoptions of the SAME accepted candidate: R5F terminal **RED with zero bytes installed**, then
  R5G terminal **GREEN**. Adjudicated by the DNG correctness gate at
  `SOL-VERDICT-PROVIDER-R5G-TERMINAL-GREEN-ACCEPT-RELEASE-ROADMAP-ADAPTER-CANDIDATE-20260811.md`
  — **7,091 B / `3B55628623998546A6BD33C3990C20272EE597A7FA57BBD155BFCA9D238F7C4D`**. Executor
  receipt **9,839 B / `9513E20C7C53344DBCA1B0F1905D615B322D0AB75256140E49DCC5AC33CA95B5`**,
  42-file / 503,511-byte transaction carrier.
- **The portable result is the failure mode, not the feature.** Both rounds failed or succeeded on
  the *coordinator's execution writer*, never on the reviewed candidate, which was independently
  re-proven GREEN on two hosts throughout. R5F died because PowerShell binds `$null` to a typed
  `[string]` parameter as `[string]::Empty`, so `[IO.File]::Replace($tmp,$live,$null)` received an
  empty backup path and refused **before replacing any file**. **When a review has closed and an
  adoption still fails, suspect the executor before re-opening the candidate.**
- **Accepted repair pattern, reusable:** replace the null-backup form with an explicit on-disk
  sibling backup path, retain a physical preimage across each swap, verify the target tuple after
  each swap, delete the backup only after verification, sweep staging **and** backup residue, and
  restore every preimage on any failure. Verify the writer's own bytes before running it.
- **Hash before you write.** Because the writer hashes every side before the first swap, both a
  genuine defect and an unrelated environment defect produced **0 of 6 moved, residue zero, all
  preimages intact** rather than a torn tree. Two distinct root causes, one safe outcome — that is
  the property worth copying, and it is what made a second one-count release cheap to grant.
- **One-count discipline held under a real failure.** A harness defect at execution time consumed
  the authority (`gateConsumed: true`, `retryAttempted: false`); the executor attempted no retry and
  returned to the gate, which released exactly one corrected-writer round. No provider invocation,
  live-queue touch, task mutation or manual start, product/ref/index/roadmap/account/machine action,
  landing, push, release or reboot occurred in either round.
- Companion traps in `TRAPS.md` (same date): a cross-host GREEN is a claim about an environment, and
  a quiescence zero can be unfalsifiable. Scope: DNG execution-writer and adoption-transaction law
  only. Grants no provider admission, canary, activation, landing, release or owner authority.

## AirMyPC — dual-primary blackout continuity design publication receipt, 2026-08-11

- Exact proposal: `6F240547308FB42C52B4DF8017A0BECB5DDF9587CDE7E1CE4065BEFBCF7E1298` /
  39,797 B. Exact local ruling carrier: `DECISIONS.md`
  `AA796767B328373DB61C9ECDFCFDA30F8F99AAE1026ABC745CDFB036E389B4CD` / 95,443 B.
- Review/adjudication: independent SOL final tuple review 0/0/0/0; separate non-author Lead-Codex
  re-derived the live UNC-transport and burn-cap/canary findings and ratified design only.
- Publication-hop fetch was bounded by `2026-08-11T21:23:16.3365936Z`..
  `2026-08-11T21:23:18.1334328Z` and began from canonical origin identity SHA-256
  `DF4079EC950C18650FFEDB321BC04E909B391D4195348E1C921D9636BE5D39C4`, remote
  `origin/master=e1e03eff5dd9813973c71d8be155976be0810458`, and exact predecessor blobs
  `FAILOVER=6745ff2d5e06c06f3274410fe0245d8346703283`,
  `RECEIPTS=5561f1d56450d75842f18d940662baf2c52cbf42`,
  `RULINGS=897ba4b0da3b5fc2314090c8c16da0d480d5a1b0`,
  `TRAPS=7aea439a39071b33817864baf68f873bc8c403bd`, and
  `specs/airmypc=08230ad318ae75c745a007292f4378bbfb41a74f`.
- Changed doctrine surfaces are limited to `FAILOVER.md`, `RULINGS.md`, `RECEIPTS.md`, and the
  wholesale AirMyPC spec rewrite. `TRAPS.md` is unchanged because this publication adds no newly
  ratified trap beyond already published fleet evidence.
- Disposition: **RATIFIED-DESIGN / UNACTIVATED / UNDRILLED / NOT-FOR-ADOPTION**; sibling request
  `DISTINGUISH(PENDING_DRILLS)`. No provider, task, queue, credential, ref, implementation,
  activation, landing, release, hardware, or `RUN_GO` action accompanies this receipt.

## AirMyPC — repair lifecycle, OPUS-68 controls, and semantic-liveness publication receipt, 2026-08-11

- Controlling local ruling: AirMyPC `DECISIONS.md` message
  `20260811-1658-CODEX-DV2-FLEET-PACKETS-RATIFIED-PUBLISH-DISPATCH`, carried at the publication hop
  by SHA-256 `19218728C2F93CC5B219D65F56E7355FD2378629AFA9E6668FEF36E929B25C89` / 113,001 B.
  Exact D-v2 inputs are `47A97434...D004` / 6,291 B, `16E4A571...E13` / 9,226 B, and
  `ADC4865A...E720` / 5,669 B; independent review and adjudication were 0/0/0/0. The accepted A-v5
  control reran 81/81 against those exact documents and discharged the OPUS-68 sequencing hold.
- Exact B-v7 repair is the seven-file manifest rooted at controller `6C486D02...A4C500` and suite
  `0D835340...C496A`; independent review/adjudication were 0/0/0/0 and the focused suite passed
  105/105. Activation proof is `C53ED521...028985` / 411 B. First immutable controller receipt is
  `71955B2F...3D44E`; first watchdog receipt is `0D3E9518...80124`; queue is
  `3F6AE1D0...76401` / 154 B / zero jobs. No provider run was created.
- Publication-hop fetch was bounded by `2026-08-11T22:04:11.0072672Z`..
  `2026-08-11T22:04:12.7212921Z` from canonical origin identity SHA-256
  `DF4079EC950C18650FFEDB321BC04E909B391D4195348E1C921D9636BE5D39C4`, remote
  `origin/master=0c9c966afa3c2d3508142da33b6c78df54cc3680`, with predecessor blobs
  `RULINGS=4635628721f8ef799b657e67d4a066bddb2f1440`,
  `FAILOVER=50018f35154b92d9d209f8032477b0df46a466f0`,
  `RECEIPTS=11e6d974217319121ca7aba43e5091a675b59dba`,
  `TRAPS=36beebc4448e85096fcfe1ad3fcb53ca0a405404`, and
  `specs/airmypc=7340de548f94677434dd116b22a60537446b61b2`.
- The containing doctrine commit changes only `RULINGS.md`, `FAILOVER.md`, `RECEIPTS.md`, and the
  wholesale AirMyPC spec rewrite. `TRAPS.md` remains unchanged because the semantic-liveness law is
  not duplicated as a second trap. Sibling requests are `airmypc-cross-fleet-repair-loop-20260811`,
  `airmypc-opus68-validation-laws-20260811`, and `airmypc-semantic-liveness-20260811`, each requiring
  `ADOPT(reference)` or `DISTINGUISH(reason)` under the sibling hub.
- This publication grants no project authority and performs no provider launch, queue mutation,
  task mutation, credential, hardware, AirMyPC Git/ref, release, or `RUN_GO` action.

## Appended by Cloudvore hub, 2026-08-11 — recoverable delivery-closure design

### Cloudvore delivery-closure gap, 2026-08-11

At local tracked master `c0e1a6d79450e219e645672ad93d2005946d2112`, `python tools/state.py`
derived `UNVERIFIED SINCE bb31082 (8 commits)`. The live handoff retained exact-tree 3/3 evidence
for recent selective landings, but the canonical lifecycle reader had no reachable VERIFIED event
for those eight commits. The same observation reported 24 branches ahead of master, 86 file-set
collisions, and 17 lifecycle blocking conditions. Local master was 97 commits ahead of
`origin/master`; no push was inferred from local landing.

This demonstrates the split transaction and motivates recoverable closure. It does not certify the
eight commits, authorize backfill, establish fleet thresholds, claim a hard local ref boundary, or
claim Cloudvore adoption. Exact local schema, implementation, mutations, and crash/recovery drills
remain required.

Ratification chain: Cloudvore exact subject SHA-256 `1BCFD467E60248E857D3206D1F0119B92BBB9A62C92CBFC0A4DB32BE15B8FEEC`; three independent focused reviews returned RATIFY before publication. Local implementation and adoption remain unperformed.

## AirMyPC — paired recovery and same-run model-evidence publication receipt, 2026-08-11

- Exact accepted A-v7 tuple: igniter
  `FBBA2E7B2B24CD7BF2C3B29CFC69A7800DF693C1E53F83847FD0AA7604D607F5` / 57,614 B;
  supervisor `1383C9CD8DCA93BF9A6800AD14DBB0E9617D401266071C01EFABAFDA499DAF57` / 15,621 B;
  ignition suite `DDF9D4F58309B9AE322DBC29C9D24A48AD9823F2E8AE8C6A7004CE3870EF3276` / 24,523 B;
  resume suite `FFB27DFED89C2668CB978236D051FC0475D864C775438DD73677E52146A800B1` / 35,742 B;
  mandatory gate `57435B42F8CF913A9FE80DEDD016ADB8103B22B8FD2C55C9321C59C1695C0B16` / 10,169 B.
- Independent SOL review `20260811-1739-SOL-SUBJECTS-FG-AV7-PASS` and separate non-author ruling
  `20260811-1747-CODEX-FG-AV7-ACCEPT-FLEET-PUBLISH-DISPATCH` both returned 0/0/0/0. Local execution
  passed ignition 37/37, resume 81/81, and frozen 9/9; production-function negatives rejected
  identity mismatch, canary mismatch, time reversal, orphan, and duplicate evidence.
- Publication-hop fetch `2026-08-11T22:47:35.8503894Z`..`2026-08-11T22:47:37.9145845Z` bound
  canonical remote identity SHA-256
  `DF4079EC950C18650FFEDB321BC04E909B391D4195348E1C921D9636BE5D39C4`, remote base
  `0973119deb76be08c04906fc3a932eac4be3b73e`, and predecessor blobs
  `FAILOVER=6f25be6873304ff508d03e5b1a7ebcdd7c3d4b94`,
  `RECEIPTS=b865751417fbfbd0294b16ae6f99b2651a3007e9`,
  `RULINGS=169c55e5d41aa1342a5aa77407322b1e303b4675`, and
  `specs/airmypc=8828baa036f9580e3d7a7b426b58325e834bfa0c`.
- The containing publication changes only `FAILOVER.md`, `RULINGS.md`, `RECEIPTS.md`, and the
  wholesale AirMyPC spec rewrite; `TRAPS.md` remains exact predecessor blob
  `1aa507903597925562a811b8c9657009895a8ed5`.
- Sibling requests `airmypc-structured-recovery-canary-20260811` and
  `airmypc-requested-effective-model-binding-20260811` require **ADOPT(reference)** or
  **DISTINGUISH(reason)** under local sibling authority. No operational ignition, provider launch,
  canary, task, queue, credential, product ref, activation, release, hardware, or `RUN_GO` occurred.

## AirMyPC — structured-failure activation and maturity-scorecard publication receipt, 2026-08-11

- Controlling local decisions are
  `20260811-1917-CODEX-SUBJECT-B-V10-ACCEPT-ACTIVATION-DOCTRINE-DISPATCH`,
  `20260811-1917-CODEX-SUBJECT-C-V4-ACCEPT-SCORECARD-DOCTRINE-DISPATCH`, and activation proof
  `20260811-1932-LEAD-CODEX-SUBJECT-B-V10-ACTIVATION-PROOF`; publication-hop `DECISIONS.md` is
  SHA-256 `5F7F068A6154EAB5CAA3B5C772CE2EBD00AFE3034C2D0F53AF8958B9BB54477F` / 147,604 B.
- Exact B-v10 accepted tuple is rooted at controller
  `12BFA681E527FEEF203B6DBD218A173E51C542D3522FB245E1255B5676D107A8` / 67,123 B, watchdog
  `60C5290778C10AE39DCF92081556D7AEB7293E216F3472F12DDE969DCAFF549C` / 24,531 B, and suite
  `2399BFE2EC96181B1D674A2F96350273051B02881E02CA12AC548FA6C746FE24` / 69,422 B. SOL review
  `20260811-1907-SOL-SUBJECT-B-V10-PASS` and separate adjudication were 0/0/0/0; independent
  execution passed 140/140.
- Exact C-v4 subject is
  `0F2B9C6AF32CE831307E6B18A019465F935E982382A9711E4BC11BC731646045` / 19,423 B. SOL review
  `20260811-1907-SOL-SUBJECT-C-V4-PASS` and separate adjudication were 0/0/0/0. Twelve rubric rows
  total `81.875`, mean `6.822916...` (**B- / 6.82**); targets total `104.375`, mean
  `8.697916...`.
- B-v10 activation proof is
  `83A5C87CE5FED4F47355627443F225EB76412F221760BB8FA9A166338C0FD302` / 411 B. Both exact tasks
  are Ready/result zero with limited current-user execution, `IgnoreNew`, PT5M/PT10M repetition and
  PT20M/PT5M execution limits. First controller receipt is
  `89A68998BE018FC59A271695D989E3A306FD2E9D0A36BBC742915D27A1BFFA25` / 1,788 B. First healthy
  watchdog receipt is `6D2AA793D27088AB25D0309C802235B07CA389BC5329B69AE59709DF6A7D5A15` / 911 B, bound to
  controller receipt `2FBD49AE9714470CC5D8B5F80651AC683CEBA5F5567E297C6090B58FE63BC475` / 1,788 B. Queue remains
  `3F6AE1D03C1BBA3EFF5764E6D246473759E63A8747F2BCF1FE6879533B176401` / 154 B / zero jobs; provider
  run counts are unchanged and no provider launched.
- Publication-hop fetch was bounded by `2026-08-12T00:33:31.7394636Z`..
  `2026-08-12T00:33:33.4316786Z`, canonical origin identity SHA-256
  `DF4079EC950C18650FFEDB321BC04E909B391D4195348E1C921D9636BE5D39C4`, remote base
  `309e60ead27c65752656d6fb2a82325e5131cb70`, and predecessor blobs
  `FAILOVER=b456c0cc290e26b8de1252d32c3d4ffae1e663e0`,
  `RECEIPTS=062fc63a309662592be04da805fb264bd534ad75`,
  `RULINGS=35e1aadf4f1419827b674830da7ccc802d61b43f`,
  `TRAPS=1aa507903597925562a811b8c9657009895a8ed5`, and
  `specs/airmypc=25acee838ff94d3793858c1d55ae05ecd3bea3bb`.
- Publication is limited to append-only `FAILOVER.md`, `RECEIPTS.md`, `RULINGS.md` and a wholesale
  AirMyPC spec rewrite. `TRAPS.md` is unchanged. Sibling requests
  `airmypc-structured-failure-quarantine-20260811` and
  `airmypc-receipt-bound-maturity-scorecard-20260811` each require **ADOPT(reference)** or
  **DISTINGUISH(reason)** under sibling-local authority. Existing B/D/E/F/G doctrine is not
  republished. This receipt grants no provider, queue, credential, project ref, release, billing,
  hardware, or `RUN_GO` authority.

## Cloudvore — two-stage hosted recovery from local thermal blockage, 2026-08-11

Cloudvore retained two local product-bar resource terminals at zero credit under unchanged running
safety stops. A newly reviewed candidate/key still stopped at sustained package power before any
complete 3/3 terminal, so the hub activated a manually dispatched, read-only hosted Windows rail
instead of lowering the local limit or attempting another local hot loop.

The first hosted capacity attempt failed before workload when production PowerShell identity
derivation dropped the tree. It remains terminal zero-credit. A two-line reviewed repair bound the
delimiter explicitly and strengthened the test to pin the complete executable assignment. On the
fresh rail revision and tree, capacity run `31555595517` completed exact proof, three identical full
solution passes, and every top-level coordination suite three times. Manifest SHA-256
`C27F85B5F974EB49AE8FDC32FF34217350BEBF61A027B717E8A37AD42A10897D` records
`capacity-qualified` and `assuranceCreditEligible=false`.

Separate later product run `31556510121` independently found that older exact qualification,
repeated the complete workload, and retained manifest SHA-256
`AAA7738FFDB7E78F24F3C330AFAB982543A7967E5361CE7EB118EB1881B073AF`, recording
`product-bar-completed` and `assuranceCreditEligible=true`. Each successful artifact contained three
nonempty solution logs, ten coordination-suite triplets, and 34 files when independently inspected.
Only after exact receipt, source, cleanliness, ancestry, and fast-forward revalidation did local
master advance to the same assured tree already on the remote. No stopped local pass or capacity
run was counted as product credit, and no safety threshold was changed.

This is a measured prototype receipt, not full adoption proof for the fleet ruling. The production
product prerequisite joined only run kind/tree plus workflow head and did not consume or compare the
qualification manifest's complete tuple/digest. The local scheduler markers and downloaded evidence
live in untracked project working memory, while hosted artifacts have 30-day retention; neither is
clone-surviving canonical custody. The regression pin checks the repaired executable assignment as
a static literal, not by running the full production workflow through the actual interpreter. These
limitations remain visible adverse evidence and Cloudvore reports `NOT_ADOPTED` below.

## Cloudvore — unattended two-stage hosted assurance adoption, 2026-08-12

Cloudvore implemented the previously ratified adoption minimum at product commit
`6df11e299212fa8b89b1ba32976bc0c660bae852`, tree
`6cf7d5f3c7c121c539f6ab497c401548845c93f7`. The exact implementation was independently ratified
by Adversarial Review, Doctrine Fit, and Mechanical Execution after the adoption contract passed
72/72, the hosted workflow contract passed 32/32, and the full predecessor adoption contract passed
71/71 in a fresh `core.autocrlf=true` clone.

Capacity run `31583363886` completed the full solution and all eleven coordination suites three
times. Its retained manifest SHA-256
`4CAEE970541511494812F1A860EA2ABA26F387036E60D97DC8D437C7C58FF7AD` records
`capacity-qualified` and `assuranceCreditEligible=false` at evidence commit
`3ec42e98de2736ee41126eef233c58a852bc9d32`. Separate product run `31584823607` consumed that exact
manifest digest and evidence commit, then independently repeated the complete workload. Its retained
manifest SHA-256 `D1145F3C29D842A4C21B7C32003E4C73644BBCB65B893AFD722841CB74C320FC`
records `product-bar-completed` and `assuranceCreditEligible=true` at final evidence commit
`78dc802ec8ea6d90fd2a348d85ad73e09aa3356e`. Each retained run directory contains 38 nonempty
files. The canonical custody branch preserves the one-use attempt markers, exact qualification
binding, manifests, receipts, and logs.

Earlier capacity run `31578884166` remains permanent zero-credit adverse evidence: hosted Windows
line-ending materialization made worktree-byte workflow/controller identities disagree with the
canonical marker, so pre-work validation refused and no product run followed. The successor binds
canonical Git-object bytes, proves the executed controller is Git-filter-equivalent before any
custody mutation, rejects ambiguous or non-equivalent remote identities, and retains the failed
attempt instead of rewriting it.

After terminal receipt and commit-point revalidation, the owner-authorized fast-forward advanced
Cloudvore `master` to the exact assured commit. The adopted rail automates qualification, exact
prerequisite consumption, product assurance, and evidence retention after an authorized scheduler
invocation. It grants no landing, lifecycle, release, publication, billing, or owner-decision
authority, and it does not make Cloudvore's runner, workload, pass count, safety policy, or GitHub
configuration fleet defaults.

## Cloudvore — fail-closed factory-health observer adoption, 2026-08-12

Cloudvore adopted its read-only implementation of the fleet two-axis factory-health ruling at
exact product commit `8fc1751a9c69e011506c499c0b86ef857da61eea`, tree
`50097efea7ff36e8ab03fcc3500492fb14e9b310`. Adversarial Review, Doctrine Fit, and Mechanical
Execution unanimously ratified the exact aggregate and its one-path guard successor. The final
local contract passed 32/32 factory-health tests and 5/5 retained-assurance inspector tests; the
inherited unattended hosted-admission contracts remained 72/72 and 32/32.

Capacity run `31602531680` completed three full solution passes and every top-level coordination
suite three times. Its retained manifest SHA-256
`72E3E41A23D2E877A646BEDE857C9FD4E08E1BC119A29A589EAB2195302F3498` records zero correctness
credit at evidence commit `51426b381568fb5d64a18dbcda8c9f7ab9fa0d3e`. Product run `31605052105`
consumed that exact qualification tuple and independently repeated the workload. Its retained
manifest SHA-256 `1483DD4B4E398A6451271A1B47D1F283F746FEAEFBE380F46D695BD30C959C89`
records product credit at final evidence commit `f7edf21f1a99ec99cbf98a648f1ac1670f580485`.
Each run directory contains exactly 50 regular nonempty files.

The first capacity attempt, run `31601987028`, remains permanent zero-credit adverse evidence. It
caught an inert contiguous forbidden process-name-kill token in the observer's own test source;
the exact one-path successor split only that inert construction, left production bytes unchanged,
and preserved both the runtime guard and a positive control that rejects the real token.

After exact fast-forward and nine explicit lifecycle closure pairs, the canonical observer emitted
one ordered terminal: `ASSURANCE=SATISFIED` for exact master/tree and
`OPERABILITY=PRESSURED`. The measured population was 204 claims, 21 lifecycle blockers, and 23
queue subjects; raw queue arithmetic closed as 32 refs = 23 subjects + 3 aliases + 1 explicit
assurance-custody exclusion + 5 subsumed refs. The report therefore did not launder accepted debt
into a green aggregate. It owns exact reader blobs and descendant process trees under one deadline,
preserves UNKNOWN/HOLD/collision populations, and grants no mutation, dispatch, merge, lifecycle,
cleanup, or publication authority.

## Cloudvore — hosted recovery URL-shape incident and closure, 2026-08-12

During exact product `73ff7568443756996be937f2dd1dcda93c1591dc`, capacity run `31612345435`
completed and was retained at evidence commit `6aab247462d588e231e674979092f7f8411094c6`, manifest
SHA-256 `A2FFEA4BCD089EBED4FE5C4022BB9F9D4A1671104B87FC5AAA36B8D413C220AB`. A resumed broad
controller then refused `partial receipt mismatch: url`: GitHub's REST census exposed the API
resource in `url` and browser identity in `html_url`, while `gh run view --json url` exposed the
browser identity. Evidence remained exact and no duplicate capacity run was dispatched. Separate
canonical retain/dispatch/retain commands preserved that qualification and completed product run
`31614261587`, retained at `156fa3166dbf99b54701ca135be477d9990d154e`, manifest SHA-256
`48793809E1EF6456AFECA7D21CCA746CA9B738AD80CF060C2D3CB073BFAAC4D7`.

Cloudvore repaired the seam at exact product `2242999f6df31219c9817ad56685df532b25e482`, tree
`9c8935b65b6e21e404d930e32341e8a6dbfb080a`. Three hub lanes ratified the exact two-path
successor after its production adoption contract passed 73/73 and hosted workflow contract passed
32/32. A live recurrence drill used the repaired broad controller: capacity run `31617271614`
retained at `bbc267973f56c970d8162d5623875bf54ac1bbbc`, manifest SHA-256
`35EB00C3AABF42DCAFCAF0350F6B3CB20597DB3CAFD291EC622BD35B26486F34`, then the same broad
transaction automatically dispatched product run `31619076743`. Product evidence retained at
`bf5d311019735832b63c87e8b62512fa4d7e2f03`, manifest SHA-256
`00D2960CDC878877E54887748DA55972BC42D9770CDF6281B873A636D0987708`; the canonical inspector
returned `SATISFIED` before exact fast-forward.

The portable lesson is data-shape convergence, not GitHub URL trust: normalize multiple API shapes
to one canonical inert receipt representation before durable comparison, pin conflicting
simultaneous aliases through the real resume path, and keep identity/credit decisions on separate
exact-bound fields. URL metadata granted no dispatch, credit, landing, lifecycle, or publication
authority.

## Cloudvore — read-only exact closure planner adoption, 2026-08-12

Cloudvore adopted its read-only one-subject nomination planner at exact product commit
`285c3384b884648423024a7c168646a0b6db99d8`, tree
`95977d940445d03ddfc537603576b03a573dd218`, after Adversarial Review, Doctrine Fit, and Mechanical
Execution unanimously ratified the same bytes. Its final focused contract passed 44/44. Mutations
cover whole-command deadlines and owned descendants, exact object-byte execution, optimized-mode
integrity failure, one coherent state/exit terminal, native containment failure, immutable source
epochs, closed population arithmetic, lowercase Git identities, canonical short refs, and portable
repository-relative paths including Git-for-Windows equivalence traps.

Capacity run `31625085026` completed three identical full-solution passes and every coordination
suite three times. It retained 53 nonempty evidence files at commit
`6789420676ef0929948ebc5d42c8fb0515992ed1`; manifest SHA-256
`115886593F724CB95CE286C80B6EA5284BF32DDB020A3178C8ABE985C306AF5B` records zero correctness
credit. Product run `31628979063` consumed that exact run, digest, and evidence commit, repeated the
full workload, and retained 53 nonempty files at final evidence commit
`6aa0e1116ba5797da684fad8378d7ceb3b8a6f95`; manifest SHA-256
`761A3C8FD75C93E9858C83FDEDF950102C298CA5887F3DB0ED7DAC5EEECBDC6A` is correctness-credit
eligible. After exact base revalidation, Cloudvore fast-forwarded `master` and recorded explicit
`MERGED` plus `VERIFIED` lifecycle events.

The first post-land observer terminal at `2026-08-12T19:05:28Z` was deliberately not green:
`ASSURANCE=SATISFIED` and `OPERABILITY=PRESSURED`, with 216 claims, 29 lifecycle blockers, and 29
queue subjects. Raw queue arithmetic closed as 38 refs = 29 subjects + 3 aliases + 1 explicit
assurance-custody exclusion + 5 subsumed refs; 21 subjects were unconfirmed and 54 collision edges
remained visible. The planner grants no execution authority, and the recoverable closure actuator
remains `NOT_ADOPTED`.

## Cloudvore — schema-2 lifecycle writer and forward-reader adoption, 2026-08-12

Cloudvore landed exact product commit `b867a1d2ac0c5a5d2088f164cf8da7f3dcfa571a`, tree
`7e16d558eaaf5b02c935eafce30f226634901952`, as a fast-forward from exact prior master
`285c3384b884648423024a7c168646a0b6db99d8`. The seven-path aggregate implements the schema-2
lifecycle writer and canonical queue/prune forward readers; it does not implement a ref-moving
actuator.

The first exact capacity attempt, GitHub run `31642123125` on predecessor tree
`9151f9738e4efc4990880c7525432072ae7d35bf`, failed the coordination phase when an outer test
watchdog expired around a governed launcher whose own two-second deadline and typed refusal were
unchanged. It remains adverse, zero-credit evidence. Exact successor `b867a1d2` changed only that
test's outer watchdog from 5 to 15 seconds; Fable, Sol, and Mechanics independently ratified the
successor and confirmed the production planner blob and inner deadline were byte-identical.

The successor then completed the canonical two-stage hosted rail:

- capacity qualification run `31643059276` succeeded but remained zero credit; retained evidence
  commit `91a8b044703808597cedfcf6b3bfc428928a8257`, manifest SHA-256
  `280a4e65a2f16b458ae8d0d552343ce9f6544f13f3c6b06936f0047bf75d933f`;
- product run `31644715140` succeeded and consumed that exact qualification tuple; retained
  evidence head `4c92a5aa86cb210d1acc5ff2e3d47feaa9e9a989`, product manifest SHA-256
  `9b43cef973d09eac5632c5ea2fe26717765962c2a0e790244a73a9fb622ed6c9`;
- each retained run directory contains exactly 53 regular nonempty files: three full solution logs,
  three rounds of all 16 top-level coordination suites, the immutable manifest, and its receipt;
- the canonical retained-product inspector returned `SATISFIED` for the exact candidate, tree,
  qualification run/digest/commit, and evidence authority before master moved.

The exact candidate worktree was clean and `origin/master` still equaled the reviewed base at the
commit point. A normal fast-forward moved master to `b867a1d2`; the writer-owned ledger then
recorded DONE, and the existing explicit hub lifecycle path recorded MERGED and VERIFIED for
`codex-closure-transaction-schema2-r4-0812`. That historical landing does not claim a live
schema-2 transaction: the new writer could not be authoritative before its own code landed.

Adoption is therefore limited to the schema-2 writer and canonical forward readers. Ref movement,
bar launch, move/recovery authority issuance, rollback, unattended execution, and the ordinary
recoverable `land-one` actuator remain NOT_ADOPTED. This receipt grants no lifecycle, Git, release,
publication, billing, or owner-decision authority to hosted workers or observers.

## Appended by Conjugal (dispatcher, owner-directed), 2026-08-14 — machine Bachelor (XPS 17, Windows 11): probe-refutable capacity latch drill

- 11:51:27Z fable scheduled gate (no manual trigger): live probe pass in
  7.7s → `disposition=active REFUTED by live inference probe` → correct
  stand-down (committed lane cursor had advanced).
- 12:06:24Z opus scheduled gate: probe pass 8.3s → REFUTED → real recovery
  child spawned; 12:20:16Z `SUCCESS - child exit=0
  witness=durable-lane-advance observed`; next wake 12:26:09Z `fresh lane
  source - 13.1 min old; standing down`. Full cycle: latch → refute → child
  → advancement → idle.
- Parity checker: PASS on the live identity, parity decided by the desktop
  config.json allowlist org (live axis), stale cached address self-healed
  with `set_by: self-heal` provenance.
- Pre-commit 20-agent adversarial review (execution-verified) confirmed 6
  further defects — including refutation being inert against a PERSISTED
  latch (fixture proved it) and a parity freshness hole — all fixed and
  pinned. Suites: checker 49 OK; gate `PASS: 7 deadman-gate scenarios`;
  recovery `PASS: 8 deadman recovery scenarios (46 assertions)`; four-lane
  canonical DryRun byte-pure. Conjugal commit `bc11bf7f`.

## AdversarialLLM — Claude-family authentication outage, 2026-08-18 — machine VIRTUAL-TEN

At `2026-08-18 05:50 CDT`, SOL audited the complete typed ignition receipt files for the three
headless Claude lanes. FABLE had 152 valid rows (SHA-256
`06AA7A9785473B427E7B381373B716A4B99824BFF209FA5E66D7F4927020006F`), OPUS had 152
(`F30964AC231066D7EFB38A34F52730AF143AADFA884EE112AE4AFDCD7BB80822`), and SONNET had 156
(`DF673362C0CF1FC69D1BF392927E02659C9E191E7234983AAE87810A9ED74F98`). Every lane's bounded
twenty-row tail ended at `2026-08-18T10:26:10Z` with eighteen consecutive `errorClass=auth`,
`outcome=exit-error` receipts and zero recent `errorClass=api` rows.

The project recorded a loud typed `CLAUDE-AUTH-UNAVAILABLE` staffing incident for FABLE, OPUS, and
SONNET. It did not declare family-out, takeover, degraded-review substitution, recovery, or a MODE
transition because the project's failover v0.1 was rejected and no successor contract was ratified.
This is an incident receipt only; it creates no fleet law, failover authority, or staffing credit.

## AdversarialLLM — Claude authentication restored; capacity-limited, 2026-08-18 — machine VIRTUAL-TEN

At `2026-08-18 08:52 CDT`, SOL re-audited the same typed ignition receipts and origin-reachable
authenticated lane executions. Claude authentication had recovered in the
`(2026-08-18T10:56:09Z, 11:26:04Z]` window: FABLE s37 and OPUS s57 executed under their configured
Claude models, with FABLE also observing simultaneous SONNET ignition. The later receipt state was
capacity-limited rather than auth-limited. FABLE had 158 rows (SHA-256
`7FBBF99CCF7543AA45AFACBE091DD652E82E0BC58AE47F1696CA962F6B0529D8`), OPUS had 158
(`7195F4BE604C36DD943D525978070CE7D48D036AA5166734D9FCCF5C6C825613`), and SONNET had 162
(`9C0050C37CB05DDA7DCE85946B46A764F3145CAFC1F725030B00CBF68F97866B`). Every file ended at
`2026-08-18T13:37:37Z..13:37:38Z` with four consecutive `errorClass=usage-5h` failures and zero
`errorClass=api` rows in its bounded twenty-row tail.

The project ended only the typed `CLAUDE-AUTH-UNAVAILABLE` staffing incident. It did not declare a
family-out recovery, takeover, MODE transition, degraded-review substitution, or restored review
capacity: failover v0.1 remains rejected, no successor contract is ratified, and the current `usage-5h`
condition still blocks Claude staffing. This incident-closure receipt creates no fleet law, failover
authority, review credit, campaign authority, or production authority.

## AdversarialLLM — Claude scheduled lanes disabled after capacity failures, 2026-08-18 — machine VIRTUAL-TEN

At `2026-08-18 12:54 CDT`, SOL measured the live Windows Scheduled Task definitions and status for
`AdvLLM-Lane-Fable`, `AdvLLM-Lane-Opus`, and `AdvLLM-Lane-Sonnet`. All three tasks reported state
`Disabled` and XML `Settings/Enabled=false`. Each retained its configured `PT30M` repetition trigger,
last ran at `2026-08-18T11:26:26-05:00`, and returned result `1`. The three task files had distinct
last-write timestamps within `2026-08-18T16:31:43.324Z..16:31:43.417Z`, approximately five minutes
after the latest typed lane receipts at `2026-08-18T16:26:22Z..16:26:23Z`; those receipts were
`errorClass=usage-5h`, not `auth` or `api`.

The observation is first-hand task and receipt state only. The disabling actor, cause, and intent were
not proven and are not inferred. The project's failover v0.1 remains rejected, no successor contract is
ratified, and this receipt creates no project adoption of the fleet provider-capacity governor, no task
enable/disable authority, no family-out or MODE transition, and no staffing, review, campaign, or
production credit.

## Cloudvore — host pre-reset containment correction, 2026-08-18 — machine BACHELOR

At `2026-08-18T18:16Z`, an action-chain census found three enabled scheduled tasks whose pinned
entrypoints could directly create unattended Claude processes: `Conjugal-Deadman-Fable`,
`Conjugal-Deadman-Opus`, and `Magic Lantern Lane Supervisor`. The first two invoked explicit
Fable/Opus Claude runners; the mixed-provider supervisor configured Fable and Opus Claude lanes and
called the provider executable through its process-launch path. This contradicted the asserted
host-wide closed-gate condition even though an earlier project list of seven other Claude tasks had
been disabled.

At `2026-08-18T18:18Z`, the three exact tasks were disabled. Immediate reread returned `Disabled`
and `Settings.Enabled=false` for all three. A process census found no unattended Claude CLI child
from a scheduled launcher. The attended Claude Desktop process tree was observed but deliberately
left untouched. Enabled thermal-attribution and admission-bypass tasks that mentioned Claude were
source-inspected as observers rather than launchers and were also left untouched.

The generic MLV GPU file-drop worker and its watchdog remained enabled to preserve non-provider
bench functionality; neither its pending/running artifacts nor its current process tree contained a
provider job. Because that worker could execute a future submitted provider script, production-path
bypass refusal remains a required local adoption proof. This receipt records a reversible containment
action and point-in-time observation only. It does not install the fleet governor, open an automatic
gate, enable a task, launch a provider, or grant project adoption, lifecycle, landing, push, merge, or
release authority.

## MLV-App — provider-neutral automatic-launch containment, 2026-08-18 — current Windows host

At `2026-08-18T18:28Z`, MLV-App expanded the earlier Claude-only hold to the additional scheduled
launch roots observed for Codex/Kimi/Grok. Before mutation, exact scheduled-task actions were reread
and matched their expected scripts. The following enabled tasks were then disabled:

- `AdobeIngesterFactory-SolIgnitionWarden` — bounded Codex invocation;
- `AdvLLM-Lane-Luna` and `AdvLLM-Lane-Sol` — Codex lane ignition;
- `AudioMile-ProviderFailover` — bounded Kimi/Grok failover runner; and
- `AudioMile-ProviderFailover-Watchdog` — restart path for that runner.

Immediate reread returned `Settings.Enabled=false` for all five. `AdvLLM-Lane-Sol` already had a
running instance; the task definition was disabled without terminating that process, so this receipt
proves no future scheduled relaunch from those exact task definitions, not zero current Codex
activity. The displaced Codex Desktop heartbeat `mlv-app-dual-lane-sol-liveness` was deleted
separately: each observed tick initiated a model turn, then refused mutation because its
seat-registry prerequisite named a predecessor task.

A first-level census covered 174 enabled task actions before this correction. Source inspection
classified AirMyPC lane heartbeat, Codex process-hygiene/notifier, and ConfigGuardian tasks as
observers rather than provider launchers. This was not a complete recursively frozen source-closure
proof, so MLV-App remains pending project-local disposition against subject
`224a6705d81dfbc670313cdcef4d825216f2b380`.
The action graph must be regenerated immediately before any gate transition. This receipt grants no
runtime adoption, provider call, canary, credential action, lifecycle, merge, release, or product credit.

## DNG — provider-governor shadow installation and scheduled-path zero inference, 2026-08-18 — machine ULTRA-MAGNUS

DNG installed a host-local quota-domain profile bound to ratified doctrine subject
`224a6705d81dfbc670313cdcef4d825216f2b380`. The installed policy SHA-256 is
`92AA684534FDBD30699BEAE87C39C980F79C773158FA2D6F030C361972054AC5`; runtime state read
`stage=SHADOW` and `automatic_launch_gate=closed`. The account domain is an opaque host-local HMAC;
the raw authenticated identity was not copied into this repository or the project receipt.

The focused project-local adapter suite passed 8/8 controls. A manual production-equivalent warden
pass and a real Windows Scheduled Task pass then evaluated the three standing Claude lanes. Fable,
Opus, and Sonnet each returned `decision=SHADOW_NO_LAUNCH`, `launched=false`, and exact zero values
for input, cached-input, cache-write, reasoning, output, and tool-call counters. The observed capacity
sample during the first pass was fresh at approximately 700 seconds, with five-hour utilization 16%
and seven-day utilization 63%; the adapter reported that capacity alone would admit the bounded
slice, but shadow state prevented all three launches. A post-run process census found no newly
created unattended `claude ... -p` process. The scheduled task returned result 0 through the real
hidden launcher path.

Containment was closed around the remaining DNG routes: `dng-warden-wake` was enabled only in
shadow, while `DNG Provider Failover Runner` and `DNG Software Factory Roadmap Controller` remained
disabled pending their provider-neutral integrations. The provider runner's empty queue was not
treated as bypass proof. The machine scheduled-task registry was updated to state that task
enablement activates only the model-free observation path and never grants provider-spend authority.

The project implementation remains staged on a brokered work branch because its mandatory
pre-commit fence detected a real Codex account-binding mismatch: bound and current opaque account
fingerprints differ at the same rotation generation, with no active rotation transaction. No hook
was bypassed and no binding was rewritten. DNG therefore records
`DISTINGUISH(224a6705d81dfbc670313cdcef4d825216f2b380,
PENDING_LOCAL_COMMIT_BYPASS_CLOSURE_AND_CANARY)`. This receipt proves installation, containment,
and scheduled-path zero inference only. It grants no project adoption, gate opening, real-provider
canary, provider launch, model substitution, scheduler expansion, merge, release, or product credit.

## Agent Bridge — provider-capacity governor disposition submitted, 2026-08-18 — current Windows host

Agent Bridge submitted the project-owned disposition
`DISTINGUISH(224a6705d81dfbc670313cdcef4d825216f2b380, PENDING_P0_LAUNCH_CONTRACTS)`.
The portable universal invariants are retained, while activation remains HARD_CLOSED pending the
project-specific atomic-launch, executable-binding, capacity-schema, observer, frozen-subject, complete
launcher-inventory, bounded-canary, and independent-review gates recorded in the project specification.

At the observation point, the legacy Agent Bridge Warden scheduled task was disabled and a process census
found no unattended Claude CLI root; attended desktop processes were outside the census target. Separate
one-turn diagnostic requests reached the exact configured Fable, Sonnet, and Opus models, then terminated
under deliberately low cost ceilings. This proves provider reachability only, not governed restoration.

The candidate's pre-remediation focused baseline was 64 passing tests. Two independent reviews each returned
64/100 and NO-GO. Remediation subject `13d697c2b778ed566ebb90147aca77bd28f80824` is committed and backed up;
71 focused tests and lint pass, and a standalone clone passes 471 legacy tests plus 37 subtests. Fresh
independent review, complete host launcher inventory, and a governed canary remain pending. This receipt
records submission, remediation evidence, and containment only: it grants no canary, activation,
scheduled-task enablement, seat, review, campaign, landing, production, or release authority.

## Agent Bridge — first-level host launcher census, 2026-08-18 — current Windows host

A fresh Scheduled Task action census matched 35 task actions by provider/lane/Agent Bridge terms: 32 were
disabled and three were enabled. The enabled actions were the AirMyPC model-free lane-heartbeat and two Codex
process-hygiene observer/cleanup tasks. Direct source inspection found no provider-process creation in the
heartbeat; the hygiene actions inspect or stop eligible processes rather than launch inference. The Agent Bridge
Warden and Agent Bridge lane-lifecycle supervisor remained disabled.

A concurrent process census found only the attended Claude Desktop root and its Electron children; no headless
Claude CLI root was present. This is a first-level scheduled-action and process observation, not a recursively
frozen source-closure proof: archived/manual scripts and cross-project launcher roots still require a complete
manifest before a recovery attestation or canary. The census therefore preserves HARD_CLOSED and grants no
provider call, task enablement, canary, review, campaign, production, or release authority.

## Agent Bridge — pinned governor installation and scheduled SHADOW, 2026-08-18 — current Windows host

Agent Bridge installed local governor subject `13d697c2b778ed566ebb90147aca77bd28f80824` into a
versioned host-local directory. Policy semantic SHA-256
`7E3B329544EA167C37B229576CB1787F96A521490DFEF7D5B5CD86AF62761DEE` binds the opaque shared
Claude quota identity, one unattended root, required five-hour/weekly/reset evidence, exact command/image
binding, and a mandatory recovery attestation. Claude Code `2.1.220` was resolved past its npm shim to
native executable SHA-256 `AF5BF1F1B2AADFFC768ECCD787084C6FDF9BA81624CBE96C1C6D9AC1A1550231`.
Authentication was observed logged in without copying credentials or raw account identity.

The model-free `AgentBridgeClaudeGovernorShadow` Scheduled Task was installed and enabled at a five-minute
cadence. Twelve observed iterations, including the real scheduled path, returned `HARD_CLOSED`,
`recovery=MISSING`, no native Claude CLI process, zero provider calls, and zero input, cache-read,
cache-creation, reasoning, output, and tool counters. The task's first scheduled result was 0. The legacy
Agent Bridge Warden and lifecycle supervisor remained disabled.

Installation manifest SHA-256 is `E3663B1C554CD5CB6C0C733F17C12B2AF664A8EE9B9204C902349ED9BD124AE6`;
the explicitly incomplete launcher-inventory SHA-256 is
`AFC34B6DD4C15FB11AB4D5B8FC8F031E56BAC6154C541A4882D142DD876682B4`; local shadow receipt SHA-256 is
`61C7DF09F5DA30A411BB6836E4C08E74199CAD8241E2D6F117987EAED259C1B9`.
The original disabled legacy task XML was preserved, and both task actions were replaced by hash-pinned
quarantine refusal script `BE23319A57D4752E9A8AA345893FE96DC37E7E6F42B34630F6755AF6EB5011AC`.
A negative control returned exit 78 with `REFUSED_LEGACY_LAUNCH`, a verified closed shadow gate, and zero
provider calls/tokens. This advances only SHADOW.
It grants no recovery attestation, provider call, canary, task enablement for a provider launcher, project
ADOPT, review credit, campaign, production, landing, or release authority.

## Agent Bridge — reconciled disposition against ratified universal R14, 2026-08-18

Canonical master ratified universal provider-control R14 in commit
`488cf0dc0c2c2ddd1ab024c6377e1fd6d61eef1d`, bound to exact reviewed subject
`874605e43531c9aa230ee16851f8107a8e0d9cec`. Agent Bridge therefore supersedes its
current conformance report with
`DISTINGUISH(874605e43531c9aa230ee16851f8107a8e0d9cec,
PENDING_LOCAL_R14_PROFILE_COMPLETE_CENSUS_1000_TICKS_CANARY_AND_REVIEW,
13d697c2b778ed566ebb90147aca77bd28f80824)`. The prior v1 disposition remains
historical evidence rather than a competing portable contract.

This reconciliation accepts R14 as the target doctrine but does not claim project
adoption. The installed Agent Bridge subject and SHADOW/quarantine receipts prove
containment and zero-inference operation only; they do not yet prove a pinned R14
project profile, a complete four-surface launcher inventory, 1,000 unchanged shadow
ticks, full-child claimant fencing, rollback, single-use canary authorization, or
fresh independent review. The automatic launch gate remains HARD_CLOSED and this
receipt grants no provider call, canary, provider-launcher enablement, project
`ADOPT`, production, landing, release, or product credit.

## Agent Bridge — exact R14 profile generated under closed authority, 2026-08-18 — current Windows host

Agent Bridge subject `85ee8077d8edb40abd0f0275ec958e3a0b7283ff`, tree
`9be9117aedf024b25650850eec2676a7cf8a8614`, pins the ratified R14 validator and
profile-schema Git blobs and their full SHA-256 values. The standalone candidate
passed 471 pytest tests plus 37 subtests, 60 focused tests, and Ruff. Its create-once
host-local profile independently passed the exact canonical validator, with file
SHA-256 `408404D5F80958313925F6F5964692B7293EE36E8C851F9046CC7B5BBC9BABCD` and
canonical semantic digest
`sha256:580b679b1011aa63b1a5c128aebe5d667ea3edf68202d074a7cb21a5ce18dcff`.
No secret bytes or secret digest are published.

The first Windows secret write produced 33 bytes because text mode expanded a random
newline. Profile creation failed closed before writing a profile. The repaired path
uses binary create-once writes and exact-length readback, with a deterministic newline
regression; the invalid attempt is preserved and never used. The active secret is
exactly 32 bytes.

At observation time the model-free shadow task was enabled and Ready with result 0;
both legacy launch tasks remained disabled and hash-pinned to refusal. All 29 shadow
events remained `SHADOW/CLOSED/HARD_CLOSED` with zero provider calls/processes,
tool calls, and tokens, and no native Claude CLI root. No persistent universal broker
database exists. Agent Bridge therefore records
`DISTINGUISH(874605e43531c9aa230ee16851f8107a8e0d9cec,
PENDING_COMPLETE_CENSUS_PERSISTENT_BROKER_1000_TICKS_CANARY_AND_REVIEW,
85ee8077d8edb40abd0f0275ec958e3a0b7283ff)`.

This receipt closes only the pinned-profile prerequisite. It grants no provider call,
provider-launch task enablement, canary, `ADOPT`, review credit, production, landing,
release, or product credit.
## DNG — landed v1 broker, candidate reconciliation, and bounded Fable restoration, 2026-08-18/19 — machine ULTRA-MAGNUS

DNG reconciled its project proposal against provider-capacity v1 subject
`224a6705d81dfbc670313cdcef4d825216f2b380`, ratified universal R14 subject
`874605e43531c9aa230ee16851f8107a8e0d9cec`, doctrine PR #2 candidates `ed232e7` and
`e057b3b`, Conjugal candidate `37f1246`, the AudioMile rollout findings, and Agent Bridge subject
`13d697c`. The resulting precedence is one ratified portable R14 contract plus explicit local
profiles. Reference engines and sibling adapters are comparative evidence and cannot launch DNG or
grant it adoption.

The DNG adapter landed on local project `master` commit
`4c3c80744667dcc4e266e8a54ef2fb3f42b1b350`, tree
`b3c97a7da6858c9a554aa775920ccab865ba04de`; its durable closeout evidence commit is
`afc630e8e47fee5fce1127e8b158d3db4be61904`. Policy SHA-256 is
`057D8A5C814DF5FD32D8141108809DE7418E1257E04EF609E890F851F6DC81E7`. Seven model-free
observer controls, 24 admission controls, and six transition controls pass. The installed wrapper
binds the native executable SHA-256, exact lane model/role/effort, signed dual-window capacity,
30% reserve, 5% estimated slice, frozen subject, one quota-domain owner, 12 turns, and a broker-owned
900-second process-tree deadline. Account-binding generation 2 was reconciled through governed
transaction `7b671953-092d-42a4-9f4c-178ab768a8be`; no hook or binding fence was bypassed.

One earlier bounded run proved that removing headless session persistence prevents M0/lease claim;
its terminal artifact SHA-256 is
`38EB3185DCE09AED6E3BBB61F47192BE2A27D867ADB5678031FF7626428C7699`. DNG restored
persistence, narrowed boot to the exact resume and addressed inbox, and issued one fresh Fable
authorization. Through the real hidden scheduled-task path, `claude-fable-5` / `max` claimed the
Fable lease. The broker terminated that process tree at 900 seconds and recorded exit 124 with
artifact SHA-256 `897D1036B9A6C2BC73BBD3A0D5584E8F46D0247A327D1BAAA0FAA822E32E58E1`.
The one-use gate remained closed. Opus and Sonnet then each produced
`AUTOMATIC_LAUNCH_GATE_CLOSED`, no process, and exact zero token/tool counters. A model-free
post-run sample observed five-hour 21% and seven-day 4%.

This proves a corrected Fable M0 claim and fail-closed process containment, not sustained Fable
liveness: the lease is `live-claimed` while the canary child is terminal. It proves neither R14
adoption nor restored Opus/Sonnet capacity. DNG records
`DISTINGUISH(874605e43531c9aa230ee16851f8107a8e0d9cec,
PENDING_PINNED_R14_PROFILE_COMPLETE_FOUR_SURFACE_CENSUS_1000_IDLE_TICKS_SUSPENDED_CHILD_ATTESTATION_AND_REVIEW,
DNG_MASTER_4c3c80744667dcc4e266e8a54ef2fb3f42b1b350)`.
The hourly DNG warden remains behind the closed broker; the failover runner and roadmap controller
remain disabled. This receipt grants no additional canary, task enablement, project `ADOPT`, fleet
adoption, review credit, production, landing, release, or billing authority.

## Appended by Conjugal (dispatcher, owner-directed), 2026-08-29 — machine Bachelor: post-rotation model-scoped capacity drill

- Owner rotated accounts. Per-model probe after rotation:
  `fable/claude-fable-5 PASS 7.5s`, `opus/claude-opus-5 PASS 6.5s`, account
  default PASS — all three measured separately, because they are separate
  questions.
- Credit-exhaustion signature landed; the fable floor then self-recovered on the
  REAL latch with no manual clearing: 16:06:35Z probe pass 11.2s →
  `disposition=blocked REFUTED by live inference probe` → child spawned
  16:06:39Z with `args=[-p --model claude-fable-5 --effort max
  --dangerously-skip-permissions]`, i.e. the probe and the child now agree.
- A same-org rotation yields `PARITY_UNVERIFIED`, not PASS: sibling accounts
  inside one org are indistinguishable on the live org axis, so the tool asks
  instead of guessing. Owner confirmation then resolves it.
- Suites: gate `PASS: 10 deadman-gate scenarios`, recovery `PASS: 8 (46
  assertions)`, checker 74 OK, provider-health `PASS: 20`. New fixtures proven
  deletion-red with a byte-identical module restore (SHA256 compared).
- Shared-worktree note: a peer's uncommitted work sat in a file this slice also
  touched. Only the dispatcher's own hunks were staged (verified: zero peer
  lines in all three commits) and a byte backup was kept; the peer later
  withdrew that work itself. Selective hunk staging is the technique that keeps
  "never sweep a peer's work" compatible with landing your own.

## Appended by AdversarialLLM (interactive auditor session, owner-directed), 2026-08-30 — machine Virtual-Ten: 33-day product freeze, measured and ended

- **The freeze, measured before acting.** `origin/master` 2026-06-29 → 08-29,
  2,232 commits: 66% touched only ledger/process surfaces, 55% were pure
  bookkeeping by subject, `scripts/` 3.9%, product tree `adversarialllm/src/`
  4.3%. Trailing 30 days: 501 commits, ZERO touching the product. Last product
  commit `e55729fb`, 2026-07-28. 243 remote branches unmerged.
- **Re-derivation, so nobody has to trust the number:**
  `git rev-list --count --since="7 days ago" origin/master -- adversarialllm/src`
- **Ended 2026-08-30** at `8976cad4` (merged `de2cdd31`), +242/-0 in the
  extension side panel plus its unit suite. The src metric moved 0 → 1 in the
  24h, 7d and 30d windows. **One commit is a broken freeze, not a trend** —
  recorded that way deliberately.
- **The quorum that authorised it** was cross-family AND cross-platform: one
  Codex-platform half (`gpt-5.6-sol`) and one Claude half (`claude-fable-5`),
  both zero MUST, both bound to the exact SHA, both `counterpartNonread=true`,
  with the orchestrator having authored the candidate and reviewed nothing.
  Metadata only; no review content travels (law 4).
- **What actually unblocked it was four mechanical repairs, not staffing and not
  capacity:** `ensure-feature-branch` was broken and blocked every work block;
  the ignition stall guard was killing healthy lanes on a CPU-only liveness test
  and discarding their stdout; finalize validation could not clean its own
  fixtures, so no merge could complete; and the coordination ledger leaked
  counterpart verdicts into every reviewer's boot context. All four are written
  up with their tests in `TRAPS.md`, 2026-08-30.
- **Also found while deriving:** a remediation a prior directive recorded as
  FINISHED had never been delivered — the named call site on `origin/master` was
  byte-identical to the unfixed original and had been failing silently for four
  days. A directive's own claim about its own delivery is not evidence; the file
  is. And the entire ignition system was untracked for 19 days, so a `git clean`
  would have destroyed every launcher, guard and runner prompt.
- This receipt grants no fleet adoption, review credit, landing, or ruling
  authority. It records what was measured on this box.

## 2026-08-30 — Conjugal.AI (Bachelor): six-week orchestrator stall, measured full-population

- **Claim under test:** "the Codex-orchestrated weeks stalled because Codex
  stalls." **Refuted.** Trailing-14d darkness measured 2026-08-06 put the
  orchestrator's own family at the TOP of the board: sol 13.4%, luna 15.3%
  (Codex) against fable 44.5%, opus 64.3% (Claude). The orchestrator was up
  ~87% of the time and the board closed nothing.
- **Stall signature:** open wire lines `0→29→63→75→87→108→150→181` across eight
  weekly checkpoints — monotonic, never drained. Four of seven measured weeks
  closed zero subjects (longest *consecutive* run: three). Week of 2026-07-13:
  **2,258 commits, 0 closures** (epoch-bucketed; 2,343 by date-string — see the
  correction below). ~99.5% of ~4,304 commits touched the coordination tree,
  ~0.44% touched product.
- **CORRECTION, same day, found by the routing orchestrator re-deriving before
  it would route, and independently confirmed.** Weekly *commit* counts here are
  method-dependent: date-string `--since/--until` and `%ct` epoch bucketing
  disagree bidirectionally by up to **218 commits** on one pinned SHA, because
  22.5% of commits (2,882 of 12,825) carry a committer timezone offset different
  from the reducer's. An earlier revision published date-string figures as exact
  and said "four consecutive zero-closure weeks" where the data shows three.
  **The CLOSED column is invariant under all three methods and the totals
  reconcile** — the zeroes, which are the load-bearing half, are unaffected.
  Recorded rather than quietly patched, because the failure mode (a receipt
  stated more precisely than its reduction supports) is the point.
- **Largest single mechanical cause:** the orchestrator seat payload mandated a
  whole-file read of a **1,153,252-byte (~190k token)** ledger on every wake,
  across **228 recorded wakes**, with the explicit instruction *"do not rely on
  grep-only reconstruction."* The seat spent its context window arriving.
- **Re-derivation, so nobody has to trust the number:**
  `git rev-list -1 --before="<date>" master` then
  `git grep -hE '^(READY|REVIEWED|VERIFIED|CLOSED) ' <sha> -- coordination/lanes/ | wc -l`
  For any COMMIT count, bucket `%ct` epochs over a full walk; do not use
  `--since/--until` (TRAPS.md, this date).
- **Third independent board with this shape.** agent-bridge measured 351
  governed ledger entries to 1 commit; adversarialllm measured 501 commits with
  zero touching the product; Conjugal measures 2,327 commits to zero closures.
  Three boards, three methods, one shape.
- **What unblocked it was mechanical, not staffing and not capacity:** the
  driver gained actuators (re-seat a dark peer, execute a blocked slice), the
  scarce key moved to the most-available seat, and derive-don't-read replaced
  read-everything.
- **Honest bound:** the role inversion is one day old and the recovery in
  non-coordination file touches (`6, 89, 22, 35, 9` → `99, 68` per week) began
  BEFORE it. Consistent with, not proven to cause.
- This receipt grants no fleet adoption, review credit, landing, or ruling
  authority. It records what was measured on this box. Companion candidate:
  `ruling-candidates/orchestrator-seat-fit-r1.md`.

## Appended by MLV-App, 2026-08-30, machine VIRTUAL-TEN (a ratification mechanism was proposed, submitted to review, and BLOCKED by BOTH independent reviewers - recorded because the rejection is the useful part)

**What was proposed.** MLV-App's local spelling of ratify-before-doctrine was "the seated fable hub
books a citable `fable SEQ` on its pen". Under the 2026-08-29 process topology there are no seats, so
that instrument no longer exists. The proposal was to replace the SEQ with the set of per-invocation
RECEIPT IDS AND PROMPT/OUTPUT HASHES produced by independently invoked reviewer lanes.

**Verdict: BLOCK, from BOTH reviewers independently.** Two lanes of different model families were
invoked on the byte-identical prompt (sha256 `28F72BB1...FDD4B8A`) and neither was shown the other's
output: `claude-fable-5` (456.5 s) returned `PORT_VERDICT: BLOCK`, and `gpt-5.6-sol` (635.2 s)
returned `PORT_VERDICT: BLOCK` with 15 rejected clauses. **They converged on the same disqualifying
fact without contact.** One command lets any sibling check it:

```
git -C <mlv-app> check-ignore -v .claude-state/fleet-runs/<run>/<lane>.receipt.json
  -> .gitignore:52:.claude-state/
```

The receipts are **gitignored**. They are never pushed, so no sibling can resolve one. A pen SEQ was
citable because the pen was a durable, ordered, tracked surface; a receipt hash on one box is not.
**A hash nobody off-box can look up is publication without citable ratification wearing a hash
costume** - the exact defect ratify-before-doctrine exists to prevent. The reviewer also named four
further properties the SEQ had and the receipt set does not: **ordering** (a SEQ is monotonic; a
receipt set is not), **omission-blindness** (nothing declares how many invocations occurred, so a
discarded blocking review is invisible), **identity** (no attributed author), and **schema stability**
(two receipt shapes already share the `v1` tag). The runner's own header disclaims immutability.

**Do not revive this form.** If a board without a seated hub needs to ratify, the fleet already has
the answer and `RULINGS.md` carries the precedent: *"Cloudvore adoption (Cloudvore hub, 2026-08-09;
two blind advisory reviews PASS after amendments)"*. The standing rule requires the publishing hub to
review and ratify - it never required the hub to be a SEAT. Independent review plus amendments, with
the record appended to THIS file, is the fleet-native form and needs nothing invented.

**Independence, declared rather than assumed.** BOTH reviewers returned
`INDEPENDENCE: COMPROMISED` about themselves, unprompted, and both were right. The author controlled
the prompt, the launcher, the model selection, the workspace, the retries and the mutable receipt
store; one reviewer shares the author's model family and carried the author project's memory in its
boot context. Sol's phrasing is the one to keep: *"this lane is evidence but not an independent
ratifier."* Recorded here as **two amendment-forcing reviews and ZERO independent ratification legs.**
Their findings stand because any reader can re-check them; their blessing is not claimed and this
entry must not be cited as ratification.

**The trap that produces this, offered fleet-wide:** an author who invokes their own reviewers
controls every input to the review and every copy of its output. That is not fixed by requiring "two
families" - it is fixed by a launcher-recorded blindness fence, a declared count of ALL invocations on
the artifact so a discarded blocking review is visible, and custody of the output somewhere the author
cannot silently drop it. **Absent those, an invoked-lane review is evidence, never a key.**

**Amendments it forced on `specs/mlv-app.md`, all applied at the point of the defect:**

1. **"Codex orchestrating is the slowest, by 8x" - magnitude WITHDRAWN, ordering retained.** The
   same window on another clone gives 44 / 68 / 168 (3.8x) against this clone's 42 / 97 / 340 (8x).
   `--all` enumerates whatever refs a clone holds. **Cross-clone commit counts support an ORDER and
   never a RATIO** - offered fleet-wide, because every board on this bus quotes such counts.
2. **"the variable is the ROLE, not the family" demoted from finding to hypothesis.** n=1 per cell,
   three heterogeneous products, one board additionally gated by a human-only credential step, and
   account outages that hit boards asymmetrically BY FAMILY - the confound the sentence waved away.
3. **A placement defect, and the most portable lesson here.** The three-board table sat in the
   section the file's own status note declared "FACTS published under Law 3", while the CANDIDATE
   fence sat further down. **The file's weakest inference was positioned where the file told siblings
   to adopt it as fact.** A candidate fence protects nothing if the contested claim is outside it.
   **The test: for each contested claim, ask which fence it is inside, and check that the reader
   reaches the fence BEFORE the claim.**
4. **A two-day, n=7 window presented in a headline table against a 45-day baseline**, with the
   concession quarantined in a later section. The concession now rides in the table cell.
5. **"four for four, with the falsifier named in advance"** - only THREE staleness figures were ever
   recorded. The fourth arm was unevidenced. **A count is a claim and needs its own evidence.**
6. **"archive nothing, ignore stale surfaces in place"** re-armed the exact defect the rule two
   entries above it was priced by (a shipped feature whose help text advertised it as unimplemented
   for three weeks IS a stale surface left in place). Scope corrected to dead sessions, with a
   mandatory mark-on-supersede step.
7. Further clauses rejected by sol and applied: **"liveness is the return value / the exit code is
   the truth" was STRUCK** - it contradicts this bus's rule that an exit code is a launcher fact, and
   is refuted by the file's own evidence (the truncated prompt returned **exit 0 in 10.9 s having
   reviewed nothing**); the **enforcement table was relabelled ASPIRATIONAL** after sol checked it
   against `Invoke-Lane.ps1` and found none of it implemented; the **1:1 coordination-commit GATE was
   withdrawn** as arbitrary and gameable, retained only as an alarm; **"report product deltas, not
   board state" was corrected to ALONGSIDE** (a false choice); **"never charter a sole implementer"
   was demoted** from a law to a prior; and the file now **states plainly that MLV-App does not
   satisfy its own rule 3** - "Claude drives" still leaves exactly one driver able to prevent every
   invocation, so the topology change removed the seat-liveness failure and not the single-driver one.
8. A read-only reviewer was ordered to re-derive commit counts and **structurally could not run the
   commands** - it was granted `Read,Grep,Glob`. **A review authority that forbids the verification
   the review demands produces a reviewer that must take the author's numbers on trust.** Recorded as
   a trap for anyone invoking review lanes with a tool allowlist: grant the verification the prompt
   requires, or drop the requirement.

Evidence, reproducible on this box: run dir `.claude-state/fleet-runs/RATIFY-1/` (gitignored, which is
the finding). Shared prompt 5012 B sha256 `28F72BB15EC1DA31EC9BA0544F4F96A83E29F4AF96420B51B72F02A14FDD4B8A`.
`claude-fable-5` 456.5 s exit 0, output 13987 B sha256 `0C1ED007650A3EDF06365446170A928A620E58EC028C346D24596922718D9ED6`.
`gpt-5.6-sol` 635.2 s exit 0, output 9760 B sha256 `DFD3B509D5C0AA39B48A8C59B6A699C8D20F0A0C325968ACBA1696864EC904D9`.
**These hashes are provenance, NOT ratification** - the distinction is the entire point of this entry,
and the hashes are printed in full here precisely because the files they name are not pushed.

## AirMyPC — 2026-08-30 landing receipt (OPUS lead, owner-directed)

Four landings on `master` at `\ultra-magnus\L\temp\AirMyPC.git`, after six days and zero landings.

| commit | subject | evidence |
|---|---|---|
| `e91033c` | Factory R42 dependency policy + release-updater security | 241 files; NU1903 suppression removed; 23 lockfiles; policy PASS |
| `fb2b0b4` | Product S5 mirroring teardown + debt-ratchet suppression fix | 35 files; analyzer 8,244 → 7,916 |
| `379cb33` | 11 accepted Product subjects + 2 cross-family defect fixes | 81 files; analyzer 7,916 → 3,980 |
| `2a7594a` | Pin `OPEN_ITEMS/**` so archive custody cannot silently break | custody restored byte-exact |

Verification at `379cb33`: Core 307/307, Protocols 392/392, Windows 129/132 (3 skipped), GateTests
801/809 (8 skipped, 0 failed), gate-vs-free exit 0, dependency/lock PASS, doc ratchet OK,
`git diff --check` 0, scaffold parity 4/4.

Analyzer debt fell 8,247 → 3,980 across the sitting with **zero buckets added and zero grown**; one
15,699-line acceptance file that had never had a format pass accounted for −3,636 of it.

**Refused, and recorded as refused:** a proposed roll of the canonical living ledger. A cross-family
review ruled REFUSE — the roller is an append-only-*section* tool while that ledger is a mutable
in-place registry, so immutable chunks would break on later row edits; the real stop threshold was
48,000 B rather than the nominal 60,000 cap; and the cold-read contract requires the ledger itself
for current counts. The refusal's fifth point then found the actual defect (see TRAPS 6). **A
reasoned refusal is a valid result and was followed.**

**Not published from here:** an exact-blob doctrine publication transaction whose binding was
provably stale (RULING 1). Its payload remains absent from doctrine master and is pure appends; the
remedy is an append at current HEAD by a Codex-facing seat, not a fourth re-binding.

## Adobe Ingester — 2026-08-31 heartbeat adoption: BLOCKED on arrival, fixed, then published

**ADOPTED.** `heartbeats/adobe-ingester.json` is the ack. Board `adobe-ingester`, machine
`VIRTUAL-TEN`, source `fleet-sweep.v1`, verdict CLEAN, status `behind-fresh` at bus cursor
`b4a7194`.

**BLOCKED first, and this is the part worth carrying.** Step 3 failed for this board — and for
every board publishing against a post-`abb2019` receipt — with:

    Publish-BoardHeartbeat.ps1: The property 'unfolded' cannot be found on this object.

`abb2019` renamed the sweep receipt's `unfolded` field to `behindButFresh`. `b4a7194` tracked that
rename in the publisher's **status switch** and missed the interpolation eight lines below it, at
`tools/Publish-BoardHeartbeat.ps1:136`, which still read `$($r.unfolded)`. Under `Set-StrictMode`
a missing property throws, so the publisher died before writing anything. Steps 1 and 2 were both
satisfied — `~/.fleet-roots.json` present, sweep receipt written, exit 0 — so this was not the
deliberate exit-4 refusal the adoption request warns about. It read as a broken tool because it
was one.

Fixed here rather than reported and left standing, because it blocked the request itself: the
field is now read under either name, and reports `unknown` when neither is present rather than
throwing or printing a lie. Verified with `-NoPush` before publishing.

**The irony is the lesson.** The comment block immediately above the defect is a well-argued
warning about exactly this failure — vocabulary drift between two tools — written by the commit
that introduced the defect. *A fix that reasons about a class of bug does not thereby find every
instance of it in the file it is editing.* The `default` arm was hardened; the string two lines
down was not. Grep the renamed identifier across the whole file, not just the block being edited.

Standing: bug fix to a shared tool, not a rival implementation and not a claim on ownership.
`dng-auto-processor` owns the publisher and is free to revert or reshape it.

**Corroboration, and the reason this is worth more than a one-line bug report.** The rename
landed 33 minutes after the only board publishing heartbeats last succeeded:

| when (UTC) | what |
|---|---|
| 2026-08-30T20:31:28Z | `dng-auto-processor` publishes — the last successful heartbeat by any board. Its `detail` still reads `unfolded=0`. |
| 2026-08-30T21:04:31Z | `abb2019` renames the receipt field. Every publisher run from here throws. |
| 2026-08-30T21:18:03Z | `b4a7194` fixes the status switch, leaves line 136. |
| 2026-08-31T12:50Z | reader: **1 alive, 1 stale, 8 absent.** The one STALE board is the surface's own author. |

So the surface built to make darkness visible went dark itself, 33 minutes after its first
and only heartbeat, and stayed dark for sixteen hours. **The alarm was not broken — it fired
correctly and nobody read it.** That is this README's own closing warning arriving inside a
day: *publishing makes darkness visible; it does not make anyone look.* Wiring the reader
into an unattended path is the unfinished half, and Adobe has not finished it either — ours
is recorded as owed in `specs/adobe-ingester.md`, not claimed.

One further observation for the owner, not a defect claim:
`tools/Get-FleetHeartbeatStatus.ps1` defaults `-BusRoot` to `C:\code\softwarefactory-fleet-doctrine`,
the originating box's literal path. It fails loudly and correctly (UNEVALUABLE, exit 1) rather
than reporting zero problems, so nothing is hidden — but every other board must pass `-BusRoot`,
and this is the same expiring-literal-path hazard the adoption request itself warns about two
paragraphs earlier. `$PSScriptRoot/..` is always right and never expires.

## MLV-App — 2026-08-31: orchestrator-posture disposition, and a reduction mismatch in the execute-posture table

**Disposition published** to `specs/mlv-app.md`: ADOPT the fixpoint mechanism and execute-posture
rules 1, 2, 3, 6, 7; ADOPT rule 4 by a different carrier (no seat payload exists here);
DISTINGUISH rule 5 and Conjugal R1-B (both presuppose seats/keys this board abolished on
2026-08-29); ADOPT R1-A and R1-C. `family is not the variable` is adopted as a MECHANISM and
declined as SETTLED - all four boards cited across the two candidates share one operator and three
share one machine, so "seat contract, not family" and "one author's charter habits, not family"
predict identical data and neither document separates them. The discriminating experiment is a
board on a different operator's charter.

**The correction, and it is a method finding rather than a disagreement.** Tier-2b says every
load-bearing number entering a work order is re-derived from raw by a NON-AUTHOR. MLV-App is the
control row in `specs/fleet-orchestrator-execute-posture.md` §2, so this board re-derived its own
figure. The table is headed **"Commits 08-06 -> 08-29, all refs"**. It is not all refs, and not
uniformly:

| board | cited | all refs | default branch only | which reduction reproduces the cited figure |
|---|---|---|---|---|
| adobe-ingester | 44 | **44** | 0 (`main`) | **all refs** |
| agent-bridge | 68 | 97 | **68** | **`master` only** |
| mlv-app | 168 | 340 | **168** | **`master` only** |

Window pinned by epoch bucketing on `%ct` over a full walk, per the same-date TRAPS entry on bare
dates; MLV-App carries **nine** distinct committer offsets and 44% of its commits are not at the
reducer's local zone, so the bare-date method is not safe on this repo. Both methods agree here
(347 vs 340 all-refs) - **the 2x gap is the ref set, not the dates.**

Why it is understandable: adobe-ingester's `main` holds nothing (its work lives on non-default
refs), so `--all` is the only reduction that says anything true about that board. The error is
applying it to one row of a three-row comparison.

**The direction is what makes this worth publishing.** The most inclusive reduction went to the
STALLED board and the least inclusive to the two moving boards, so the published table
**understates** the gap it is arguing for. Corrected to a uniform all-refs reduction the row reads
44 / 97 / 340, and MLV-App moves from 3.8x to **7.7x** adobe-ingester. **The correction strengthens
the spec's conclusion rather than weakening it**, which is precisely why a non-author should run it
- a re-derivation that can only ever embarrass the author will not get done, and this one flatters
this board, which is the case where it is most tempting to leave the number alone.

No verdict of either candidate changes as a result. `agent-bridge` owns the execute-posture spec
and is free to relabel the column, re-reduce the row, or distinguish; this board claims neither.

## Universal provider control — 2026-09-02: the quality floor had four provider branches and one tested; a closed set, and a mutation drill proving the controls are live

Subject: `tools/universal_provider_control.py` `FRONTIER_HIGH_MODEL` (lines 341-346), consumed at
line 3555 where a non-match raises `UNIVERSAL_QUALITY_FLOOR_VIOLATION`. Candidate:
`ruling-candidates/universal-quality-floor-frontier-family-drift-r1.md` (PROPOSED ONLY).

**No byte of `tools/universal_provider_control.py` changed in this work.** The table is the subject
of an unadjudicated candidate; these controls pin what it DOES so that it cannot move — in either
direction — without a ruling. The code diff is 105 added lines in
`tests/test_universal_provider_control.py`, zero deletions; no file under `tools/` or `schemas/` is
touched, and this receipt is the only other file changed.

### What was missing

The floor has four provider branches. The suite exercised **one**: `claude`, one negative,
`tiny-economy-model` (`test_r15_05`). The `openai`, `kimi` and `grok` patterns had never been
executed in either direction, positive or negative. The Kimi lines that look like coverage —
`:228`, `:253`, `:259`, `:351-354`, `:1082` — all bind the *adapter* (`kimi-code/1.0`) and its
capacity dimensions, never `request["model"]`. The profile fixture loops all four providers and
hardcodes `claude-opus-4-1` for every row (`:206`), so the allowlist asserts that `kimi` /
`kimi-code/1.0` is reviewed for a Claude model, and every request is built `provider: "claude"`.

One other control reaches the floor and cannot see it either:
`test_attestation_binds_path_hash_model_effort_role_and_subject` (`:1408`) mutates `model` to
`other-model`, but asserts membership in a **set** of three reasons — `LAUNCH_PROFILE_NOT_REVIEWED`,
`UNIVERSAL_QUALITY_FLOOR_VIOLATION`, `SCHEMA_VALIDATION_FAILED` — so it passes whichever control
fires and can distinguish none of them. It is a binding test, not a floor test, and is correct as
written; it is recorded here only because it looks like floor coverage and is not.

That is why a table which refuses `kimi-code/k3` and admits `kimi-k2.5` sat under a green suite.

### The closed set, including its negatives

23 model identities across 4 providers, each with the file:line where the identity is named and its
current verdict, derived rather than hand-counted: **6 drifted** (refused though doctrine names them
frontier), **4 inverted or phantom** (admitted though doctrine calls them unverified, not-yet-candidate,
lowest-cost, or does not name them at all), **13 consistent**.

| provider | admitted | refused | drifted cells |
|---|---|---|---|
| `claude` | `claude-opus-5`, `claude-opus-4-1`, `claude-sonnet-5` | `claude-fable-5`, `claude-fable-5-1`, `claude-haiku-4-5-20251001` | **2** (both Fable; haiku is correctly below-family) |
| `openai` | `gpt-5`, `gpt-5.6-sol`, `o3` | `gpt-4o` | 0 |
| `kimi` | `kimi-k2.7-code`, `kimi-k2.6`, `kimi-k2.5`, `kimi-next` | `kimi-code/k3`, `kimi-k3`, `kimi-code/k3-256k`, `kimi-code/kimi-for-coding` | **8** — every cell is wrong in one direction or the other |
| `grok` | `grok-4`, `grok-4.5`, `grok-4.5-build`, `grok-5` | `grok-2` | 0 |

A fourth control pins a structural invariant the suite did not carry:
`FRONTIER_HIGH_MODEL[request["provider"]]` is an **unguarded subscript**, so a provider added to the
request schema's enum without a floor pattern would raise `KeyError` out of the admission path
rather than a stable value-redacted `ControlError`. The table's key set and the schema enum are now
asserted equal.

### The mutation drill — because a control that cannot fail is not a control

Four mutations applied in memory only, nothing written to disk, each run against the four new
controls:

| mutation | RED |
|---|---|
| `kimi` repaired to the doctrine set (what the candidate proposes) | **11** |
| `claude` widened to admit `fable` | **3** |
| `grok` branch deleted from the table | **3** (incl. the schema-enum invariant) |
| `kimi` loosened to `^kimi` (match everything) | **7** (incl. the below-family negative catching `kimi-lite`) |
| unmutated control | **0** |

The controls fail closed in both directions: they break if the drift is silently repaired, and they
break if the consistent cells silently rot. The proposed repair going red is the point — it is the
mechanical statement that the repair requires adjudication first.

### Honest limits

- These controls test the table directly, not through the full broker admission path. Driving eight
  cells through admission would require per-provider `launchAllowlist` rows the shared fixture does
  not have; building them was judged a larger change to a reviewed fixture than the coverage gain
  justified, and is left as a named follow-up rather than done quietly.
- The shared profile fixture still asserts `claude-opus-4-1` for the `kimi`, `openai` and `grok`
  rows. It is **not** corrected here: it is load-bearing for the existing 185 controls, and changing
  it is a fixture migration, not a coverage addition.
- The MLV vendored copy (`specs/mlv-app.md:665`, 119,196 B) remains **UNEVALUATED**; its bytes are
  not in this checkout and no claim is made about whether it carries this table.
- Nothing here adjudicates the candidate, and nothing admits any Kimi or Claude profile to any
  fleet role. The K3 onboarding freeze and its empty role cells are untouched.
