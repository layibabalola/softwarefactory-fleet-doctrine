# Receipts (append-only; drill + result + date + machine)

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
