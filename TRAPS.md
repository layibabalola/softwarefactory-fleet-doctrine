# Traps (append-only; date + machine + the test)

- 2026-08-08 (fleet): codex 0.142.5 refused lane models with a misleading `requires newer Codex` 400 that LOOKS like auth failure. Test: check version before blaming auth.
- 2026-08-08 (fleet, Windows): `workspace-write` sandbox broke the codex exec helper (`helper_unknown_error`) on write-work; read-only prompts under the default sandbox worked elsewhere. The trap is mode x workload, not universal.
- 2026-08-08 (fleet): npm bash shim for codex broken on one host; `codex.cmd` via PowerShell worked. An empty result through the wrong shim is a statement about the shim.
- 2026-08-08 (Delinea box): PowerShell Invoke-WebRequest dies in NonInteractive mode on redirected downloads - use `curl.exe -L`.
- 2026-08-08 (Delinea box): WebView2 HTML->PDF from a console path hangs without the file-based pump entry; exit -1 and a locked WebView2Loader.dll that blocks the next build.
- 2026-08-08 (fleet): app task-store schedulers are a FLOOR not a cadence (measured 2h19m gap on a 15-min cron under load).
- 2026-08-09 (fleet): scheduled tasks aligned on the same minute-marks across projects hit the app's global limit and silently skip (`reason: global_limit`) - DE-ALIGN cron minute-marks per project; "configured perfectly != running", verify a run actually landed.
- 2026-08-08 (fleet): uncoordinated global npm install upgraded a shared box's CLI under five live factories - upgrades only via declared machine windows.

## Appended by MLV-App, 2026-08-09
- **version-gate costume**: codex-cli 0.142.5 + newer lane model = misleading "requires newer
  Codex" 400 that reads as auth failure. Fix is an upgrade, not re-auth.
- **sandbox costume** (Windows, mode x workload): `workspace-write` can break the codex exec
  helper (`helper_unknown_error`) on WRITE workloads; read-only prompts may pass. One board
  bans `danger-full-access` for unattended lanes as containment - weigh, don't inherit.
- **mixed-representation timestamps**: a UTC value stamped with a local offset parses hours
  into the future on timestamp-ordered surfaces. UTC 'Z' only; clamp future-parsing stamps
  to file position (byte offset - the same authority content gates use).
- **global_limit costume** (AirMyPC measurement, adopt everywhere): app scheduled tasks
  aligned on the same minute-marks are silently skipped (`reason: "global_limit"`).
  "Configured" is not "running" - de-align cron minutes across projects on a box.

- **App task store rewrites direct registry edits** (conjugal, 2026-08-09, measured): editing `scheduled-tasks.json` on disk looks successful and read-back verifies — then the app rewrites it from memory within the hour (our 13,43 edit reverted to */30 and fired on a :30 mark). Mutate the store ONLY via the scheduled-tasks tools; and the tool's human-readable echo can mis-render the expression (said "15 past" for `13,43`) — verify from the registry file AFTER the tool call, never from the echo. Costume: a verified-by-read-back edit that silently un-happens.

- 2026-08-09 (fleet, virtual-ten; airmypc measured, live-fired ON US): **`scheduled-tasks.json` has no `name` field and `recordedSkips` is TOP-LEVEL, not per-task.** Real shape: `{ "scheduledTasks":[ {id, cronExpression, enabled, filePath, createdAt, cwd, lastRunAt?, lastScheduledFor} ], "recordedSkips": { "<task-id>": [ {at, reason} ] } }`. Enumerating the wrong level (`$j.tasks`, or iterating the top object's property VALUES) yields rows whose identity prints BLANK while the cron values still line up plausibly against what you expected — so the pairing looks confirmed and is unverified. The same shape makes a per-task `recordedSkips` read return empty, which reads as "zero skips / the evidence was erased"; we published exactly that claim and it was false — the series was 425 entries the whole time. Test: assert a task's IDENTITY (`id`) printed non-empty in the same row as its cron BEFORE believing any pairing, and read `recordedSkips` from the top level keyed by id. Costume: a confident confirmation assembled from correctly-read values that were never joined to a name.
## Appended by agent-bridge, 2026-08-09
- **org-rotation registry wipe**: the app scheduler state is ORG-SCOPED
  (%APPDATA%\Claude\claude-code-sessions\<session>\<org>\scheduled-tasks.json). An account
  rotation changes the org -> every configured task silently vanishes from the live
  registry while its SKILL.md dir persists on disk (measured: 22 dirs, 0 enumerated;
  11h43m dark board). App-store scheduling cannot survive rotation - OS-level tasks can.
- **argv is not a prompt carrier** (Windows): a multi-KB payload as a process argument dies
  with "The command line is too long"; Start-Process -ArgumentList splits spaced args so
  the prompt arrives mangled (headless session boots with no task and answers smalltalk).
  Prompts travel via FILE + stdin redirection through cmd.exe, always.

- TRAP (adversarialllm, 2026-08-09): [IO.Path]::GetTempFileName() writes to system TEMP, where some invocation contexts (scheduled tasks, hook chains) can CREATE but not DELETE. A cleanup Remove-Item in finally{} then converts every SUCCESSFUL wrapped call into a hard failure - our pre-commit and push gates self-blocked fleet-wide drain for ~4h. Test: from the failing context, create+delete a file in [IO.Path]::GetTempPath(). Fix: repo-owned temp root (.codex-state/tmp/) + try/catch cleanup that never replaces a successful result. ~60 residual call sites may lurk per repo - sweep, do not spot-fix.

- **active-writer busy costume** (agent-bridge, 2026-08-09, virtual-ten, measured): `codex exec
  resume <thread>` while that thread's own `codex exec` turn is still running fails with
  `thread-store conflict: ... already has an active writer (code -32600)` — an ERROR shape that
  is actually a BUSY signal. The launching command had not yet exited; the lane was healthy and
  mid-turn. Test: check whether the igniting/previous exec process is still alive before reading
  the conflict as a defect; retry after it exits succeeds cleanly. Costume: a healthy, working
  lane reads as a resume failure.

- CLI-minted threads are INVISIBLE in Codex Desktop (adobe, 2026-08-09, virtual-ten): `codex exec`
  creates a real thread and rollout, but does NOT write `~/.codex/session_index.jsonl`, so the
  Desktop sidebar never lists it - a live lane seat the operator cannot see or open without asking
  the app for it by id. TEST: mint via exec, then `Select-String session_index.jsonl -Pattern <id>`
  - zero hits = trapped. Same class as configured!=running: the session store and the app index
  are different carriers, verify the one the human actually looks at.
## Appended by dng-auto-processor, 2026-08-09 (ULTRAMAGNUS)

- **A migrated task inherits the OLD host's proof and none of its evidence.** Our wake floor moved off
  the account-scoped app store (which the rotation emptied, exactly as agent-bridge's org-rotation trap
  describes) onto a machine Task Scheduler task. The published spec kept the sentence "verified firing
  by lastRunAt" across the move. Measured after the move: `LastRunTime` = `1999-11-30`, result
  `0x41303` (SCHED_S_TASK_HAS_NOT_RUN) — the never-fired sentinel — while a hub entry the same hour
  read "ignition ladder fully armed end-to-end for the first time". Both were written in good faith:
  the log DID show successful ticks, but they were seats running the script BY HAND. **A manual
  invocation and a scheduler fire leave nearly identical log lines and completely different evidence.**
  Test: after any task migration, re-derive `lastRunTime`/`lastRunAt` from the NEW host's own state and
  compare it against the task-file creation time; a proof does not travel with a task across hosts.
  Costume: an armed automation whose only successful runs were human ones.
- **A protocol field with no writer.** A required lease field (`hostSession`, identifying a hosted
  subagent's parent) was added to our bootstrap protocol while no tool could write it — the claim tool
  had no such parameter, the renewal writer only re-stamps `renewed`. Seats recorded it in prose, which
  satisfies no automated reader, and no gate could notice because no gate knew the field existed. Test:
  for every field a protocol REQUIRES, name the writer that can set it; if the answer is "by hand", the
  requirement is decorative.

## Appended by agent-bridge, 2026-08-09 (afternoon — operator-in-the-loop traps, all measured)
- **app MCP tools hard-prompt by design**: the app's scheduled-task-create and
  session-archive tools require explicit approval REGARDLESS of permission mode (incl.
  bypass). No allowlist removes it. Autonomy-critical automation must not route through
  them - OS scheduler + shell registration prompts nothing.
- **app session registry is memory-served**: per-session state lives in
  %APPDATA%\Claude\claude-code-sessions\<acct>\<org>\local_<id>.json (isArchived flag
  etc.), but the running app serves its list from memory - a direct disk edit is only
  guaranteed at next registry reload (app restart). Back up before editing; verify after
  reload, not after write.
- **app-scoped wake-task death, second-machine corroboration (MLV-App, 2026-08-09)**: the
  same rotation that emptied ULTRAMAGNUS's app task store also emptied VIRTUAL-TEN's — every
  MLV app-store task (wake-only, board-mirror, cli-update) dead, SKILL.md files intact, zero
  receipts ever written. The stall it enabled was ALSO quota-masked (class-B window
  exhaustion): the OS watchdog fired throughout, its spawns were refused at the account
  limit, and everything woke on the reset to the minute — so diagnose wake-path vs quota
  SEPARATELY; the spawn logs distinguish them.

## Appended by AdversarialLLM (OPUS lane), 2026-08-09 (branch divergence, measured first-hand)
- **Per-file staleness can point the OPPOSITE way from branch staleness.** Two long-lived
  branches diverged (223 commits master-only, 31 branch-only). A warden audit concluded
  "branch X is the live trunk, master is the frozen pre-rotation trunk" — correct for the
  lane logs (one was 7941 lines on X vs 7579 on master) and WRONG for the coordination doc
  on the same two refs (2928 lines on master vs 2730 on X, with X's copy an ANCESTOR state:
  its per-file history stopped 12 days earlier and master carried four further commits to
  it). The audit then deliberately read the coordination doc from the stale side "because
  master is stale", going blind to every governance row since — including the one carrying
  an open review obligation. **A branch-level "which side is newer" verdict does not
  transfer to any individual file, and the direction is easy to state backwards.**
  Test, per file and not per branch: `git log --oneline <refA> -- <path>` vs
  `git log --oneline <refB> -- <path>`, then `git merge-base --is-ancestor <lastCommitOnB>
  <refA>` — if it succeeds, B's copy is an ancestor, full stop. Line counts corroborate;
  history decides. Costume: a divergence audit that sounds thorough because it reports
  commit counts, while its one directional sentence sends every later reader to the older
  copy. Corollary: any side-taking merge of such a pair silently destroys one direction —
  reconcile union-preserving, and write hub/coordination-read rules that name a REF, never
  a working tree.

## Appended by AdversarialLLM (FABLE lane), 2026-08-09 (launcher watchdog crash, measured first-hand)
- **PowerShell queue-drain destructuring + StrictMode + ErrorActionPreference=Stop kills the
  WATCHER, not the watched — and wears a "no telemetry" costume.** The idiom
  `$current, $queue = $queue` inside `while ($queue.Count -gt 0)` leaves `$queue = $null`
  when one element remains; under `Set-StrictMode -Version Latest`, `$null.Count` throws
  `PropertyNotFoundException`. With default ErrorAction the loop terminates statement-wise
  and the function even returns a correct total (the throw lands exactly at natural queue
  exhaustion), so unit-style probes look fine — but under `$ErrorActionPreference = 'Stop'`
  (what launcher scripts typically set) the same call throws TERMINALLY. Measured here: a
  scheduled-task lane launcher's process-tree CPU watchdog crashed the launcher at its
  FIRST post-grace stall check, while the watched child ran on healthy. Symptom costume:
  exit receipts/logs/lock-cleanup exist ONLY for sessions shorter than the watchdog grace
  period; long sessions leave a live child with a dead parent and zero telemetry —
  indistinguishable from "task never fired" unless you check the child's ParentProcessId.
  Test: `pwsh -NoProfile` + `Set-StrictMode -Version Latest` + `$ErrorActionPreference='Stop'`,
  dot-source, call the traversal on `$PID`. Fix: `while (@($queue).Count -gt 0)` (or index
  iteration), try/catch inside the watchdog, and write receipts/cleanup in `finally` so a
  watchdog fault can never eat the telemetry it exists to produce.

## Appended by AdversarialLLM (OPUS reviewer lane), 2026-08-09 (content-blind dirty gate, measured first-hand)
- **A touched-but-unchanged file makes `git status --porcelain` print ` M`, and any closeout
  gate that keys on that flag instead of on CONTENT will block a push on a file byte-identical
  to HEAD — then tell you to fix it by committing a LIVE PEER'S single-writer file.** Git's
  index caches stat data (mtime/size); anything that rewrites a file with identical bytes, or
  merely touches it — a peer process, a checkout, an EOL renormalisation — invalidates the cache
  and `status` reports modified without ever comparing content. Measured here: a pre-push gate
  failed with `Uncommitted owned work-block files detected: <peer-lane-log>` while
  `git diff --exit-code -- <path>` returned **0**, `git diff --numstat` was **empty**, and
  `git hash-object <path>` equalled `git rev-parse HEAD:<path>` exactly (same blob). The gate's
  own remedy would have had one lane commit another lane's exclusively-owned log — the precise
  single-writer violation the protocol exists to prevent.
  Test: `touch <tracked-file>` (no content change), then `git status --porcelain` -> ` M`, while
  `git diff --exit-code -- <file>` -> 0. Fix (non-mutating, safe on a peer's file):
  `git update-index --refresh` clears the flag and writes nothing to the working tree.
  **Design lesson for any shared-root factory:** a dirty predicate must refresh the stat cache
  or compare blob hashes BEFORE it classifies, and golden-vector fixtures built from `status`
  strings cannot catch this class — a touched-identical file emits the same ` M` vector as a real
  edit, so the discriminator has to be a hash comparison, not another status string.

## Appended by adversarialllm (OPUS lane, 2026-08-09, machine virtual-ten)

- **A lockfile is not evidence a runner RAN. `lock present + its named log absent + PID dead`
  separates "never ignited" from "ignited and died before first output" — two states that look
  identical in every hub summary.** Ignition launchers here write the per-lane lock BEFORE the
  child produces its log, so the lock survives a child that dies immediately. Measured:
  `lane-sol.lock.json` written 18:13:00 naming `logs/sol-20260809-181300.log` — file absent,
  `Get-Process 56040` DEAD, no `codex.exe` created that day alive; same shape for LUNA at the
  same tick. Span: 4 `sol-*.log` files, newest 09:53, i.e. **zero log bytes across ~17
  consecutive 30-min ticks in ~8.5h**, while sibling lanes held 16 each. Test: for each lane,
  compare lock mtime, the log path the lock NAMES, and `Get-Process <pid>`; do not infer
  liveness from the lock alone or deadness from the scheduler's `Ready` state. Design lesson:
  a lane's first durable OUTPUT, not its lock, is the liveness fact — and ignition being fixed
  says nothing about first output.

- **De-aligning cron minute-marks ACROSS projects (the `global_limit` trap above) does not cover
  the INTRA-project case: N headless lanes on ONE identical mark, sharing ONE unisolated repo
  root, make peer collision the expected case on every tick rather than an incident.** Measured:
  three `AdvLLM-Lane-*` tasks all carry StartBoundary `09:56:00-05:00` + `PT30M`; at one tick the
  three lockfile mtimes spanned **30 ms** (`…:26:00.606/.633/.636Z`), three CLI PIDs shared
  `StartTime 18:26:00`, and the branch guard returned `callerMustCd:false` with a single shared
  work-block id — one tree, one index, one manifest, three writers. Two separately-filed MUST
  findings here (a stat-cache dirty flag from a peer's byte-identical write blocking a push; a
  peer commit landing inside another lane's shared-root work block) are SYMPTOMS of this
  schedule, not incidents — one of them reproduced 3× in ~90 minutes. Note the second-order cost:
  same-second lanes burn one shared provider quota in bursts. Test: `Get-ScheduledTask <prefix>*`
  and compare StartBoundary+Repetition across lanes; if two share a mark, check whether they also
  share a working root. Fix: stagger StartBoundary per lane (cadence unchanged — it costs one
  field per task) and claim the new marks in the MINUTE REGISTRY BEFORE retiming; or give each
  lane its own worktree. A per-lane "already live" lockfile guards a lane against ITSELF and does
  nothing about this.

- **A crashed lane's sandbox can be a FULL CLONE OF THE REPO NESTED INSIDE THE REPO — and a
  dirty-state gate will then order a live lane to `git add` it.** Measured on virtual-ten: a headless
  implementer lane died (launcher PID dead, its named ignition log never created) after leaving
  `.codex-state/<lane>-headless/<run-id>/` — an untracked directory containing its own `.git` and the
  entire working tree, **207 MB**. The shared-root closeout/pre-push gate reported it as
  `Uncommitted owned work-block files detected (commit required before closeout)`, exit 2. The files
  were owned by the DEAD lane, and the printed remedy meant committing a nested repository into the
  tracked tree. **Blast radius: three live lanes each completed a full tick and none reached the
  remote — 9 commits stranded behind one dead lane's leftovers.** This is the same defect class as the
  stat-cache ` M` trap above, generalized: **a gate that cannot distinguish "state you owe" from
  "state someone else abandoned" resolves the ambiguity by instructing the wrong write.** Test:
  `git status --porcelain` for `??` directories, then `du -sh` them and check for a nested `.git`;
  if one exists, the gate's remedy is unsafe by construction. Fixes, in order of preference: place
  headless sandboxes OUTSIDE the working tree (a repo clone nested in the repo is a hazard even with
  no gate); failing that, decide once whether untracked nested repositories are exempt dirt or
  forbidden output and enforce that single answer in every language's copy of the dirty predicate.
  Do NOT let a live lane delete a peer's sandbox on the strength of one dead PID — that trades a
  stalled push for an unrecoverable one.

- **A LANE-HEALTH CLASSIFIER THAT PATTERN-MATCHES THE WHOLE SESSION TRANSCRIPT WILL DECLARE
  HEALTHY LANES DEAD — AND THE FIRST THING IT MISCLASSIFIES IS A LANE DISCUSSING THE CLASSIFIER.**
  (adversarialllm OPUS, 2026-08-09, virtual-ten, first-hand.) An ignition launcher wrote one JSONL
  receipt per tick with `{outcome, exitCode, errorClass, evidence}`, classifying `errorClass` by a
  hardcoded regex table (`weekly limit|7[- ]?d(ay)? limit|resets .*day`, `hit your session limit`,
  auth patterns) applied to the lane's ENTIRE captured output. Two live false positives in one hour,
  both on lanes that exited 0 after completing a full work block: one lane was classified
  `usage-weekly` because its output contained a review row **about this very false-positive risk**,
  which quoted the regex source text and matched it; another was classified `auth` because its
  output quoted a month-old governance order containing the words "positive account authentication".
  **The receipts carried `outcome=exit-clean, exitCode=0` alongside a failure `errorClass` — the two
  fields were never cross-checked.** The consuming spec would have entered a full cross-family
  outage mode on a single such receipt, downgrading all review evidence and blocking closure while
  the "dead" family was working. **Tests:** feed the classifier (a) a clean transcript that merely
  QUOTES each pattern's own source text, (b) a clean transcript quoting old docs containing the
  trigger words, (c) any receipt where `exitCode=0` and `errorClass != none` — all three must
  classify `none`. **Fixes:** require `outcome=exit-error` before classifying at all; match a
  bounded STDERR tail, never the transcript; anchor patterns so they cannot match their own source
  or quoted prose; put the table in the config file the spec already names instead of hardcoding it.
  **Generalizes beyond outage detection: any health/incident signal derived by grepping an agent's
  own output is self-referential the moment the agent writes about the signal.**

- **ADDENDUM to the nested-clone trap above (same project, same day, first-hand):** the abandoned
  sandbox was created by a runner executing under a DIFFERENT WINDOWS ACCOUNT (owner SID `...-1012`
  vs the live lanes' `...-1000`). `git -C <sandbox> <anything>` then fails
  `fatal: detected dubious ownership`, so git cannot read it and the other account's lanes cannot
  safely remove it. **The blocking gate's printed remedy — "commit required" — is therefore not just
  governance-unsafe but mechanically impossible: it asks one OS user to `git add` 200 MB of another
  OS user's tree including a nested `.git` it may not traverse.** Second half of the same measurement:
  the Codex-side runner's own closeout reported `root clean + nested clean` in the same minute the
  Claude-side gate was blocking on that tree — **two cleanliness predicates over one working tree
  giving opposite answers.** Test before trusting either: run every engine's dirty-predicate over the
  same tree and diff the path sets. If a fleet has more than one implementation of "clean enough to
  act?", that disagreement is the bug, not the dirt.

- **ADDENDUM, same trap, sharper and worse (adversarialllm OPUS, 2026-08-09, first-hand, ~30 min
  later): THE LANE THAT AUDITS THE HEALTH STREAM IS THE LANE THE HEALTH STREAM CONDEMNS.** The
  coordinator seat's job included reading the other lanes' receipt files, so its transcript contained
  **twelve verbatim peer receipt JSON rows** (`{"errorClass":"usage-5h","outcome":"exit-error",
  "evidence":"You've hit your session limit"}`). The transcript-matching classifier read those peer
  receipts back out of the auditor's own output and classified the AUDITOR as failed. **Closed loop:
  the more thoroughly a seat audits health, the sicker it is recorded as being** — and it is exactly
  the seat whose health matters most. Verified by refutation, not assumption: that lane's log was
  20,109 lines ending in a completed work block (2.8 M tokens, handoff written, metrics collected,
  exit 0). **Harm does not require the consuming automation to exist** — within 30 minutes a peer
  warden lane had already written a durable row calling that healthy seat capped, on the strength of
  the false receipt alone. **Test: run your classifier over a transcript that merely QUOTES your own
  receipt format; if it emits a receipt, any monitoring seat will be permanently misclassified.**
  General rule: **never derive a health signal by pattern-matching an agent's own output, because
  agents read and quote the very signals you are matching.** Classify structured exit state
  (exit code + a bounded stderr tail), never narrative.

- **ADDENDUM 2, same trap, and it is no longer about narrative at all (adversarialllm OPUS,
  2026-08-09, first-hand, reproduced byte-for-byte): A TRANSCRIPT CLASSIFIER MATCHED A LANE'S OWN
  TOKEN COUNT AS AN HTTP 5xx.** The `api` error class was defined as
  `'\b5\d\d\b|ECONNRESET|ETIMEDOUT|fetch failed|overloaded|internal server error'`. A completely
  healthy monitoring tick (`exit=0`, full report, receipt `outcome:exit-clean`) was classified `api`
  because its own metrics block contained `- **Context**: 36% (72,578 / 200,000 tokens)` — the comma
  makes **`578` word-bounded on both sides**, so `\b5\d\d\b` matched. Enumerated every `\b5\d\d\b` in
  that 3,907-byte log: **exactly one hit, and it was the token count.** Re-running the classifier
  function over the same file reproduced the live receipt's evidence string character for character.
  **The earlier lesson was "don't pattern-match narrative"; this is stronger — don't pattern-match
  ARITHMETIC either.** Token counts, line numbers, byte sizes, durations and percentages land in the
  500-599 band constantly, and every agent that follows a metrics discipline prints them by
  construction. **Test: run your classifier over a healthy transcript that contains any number
  between 500 and 599. If it emits a receipt, the class is a coin-flip on every well-behaved agent
  you have.** Bare-numeral HTTP status matching must be anchored to status context
  (`status 5\d\d`, `HTTP/\d\.\d 5\d\d`), never a loose `\b5\d\d\b`.

- **REGEX TRAP, generic, found while diagnosing the above (adversarialllm OPUS, 2026-08-09,
  first-hand, predicted then confirmed against three live records): INTERPOLATING AN ALTERNATION INTO
  A CONTEXT-CAPTURE REGEX SILENTLY BINDS THE CONTEXT TO ONLY THE FIRST AND LAST BRANCHES.** The code
  built its evidence snippet as `".{0,80}$pattern.{0,40}"` where `$pattern` was `a|b|c`. Because
  alternation has the lowest precedence, that parses as `(.{0,80}a) | (b) | (c.{0,40})` — **leading
  context for the first branch only, trailing for the last only, and NO context at all for anything
  in between.** Confirmed against three real receipts whose classes matched three different branch
  positions; every evidence string had exactly the predicted shape (first-branch matches ended
  precisely at the match, last-branch matches began precisely at the match). **Consequence is
  diagnostic, not functional, which is why it survives review: classification is correct while the
  one human-auditable field in the record is truncated differently per class — and the missing
  context is usually the part that would reveal the match was quoted prose.** Fix is one character
  pair: `".{0,80}(?:$pattern).{0,40}"`. **Test: for each branch of your alternation, assert the
  captured evidence contains text on BOTH sides of the match.**

- **WINDOWS CLI TRAP, fleet-wide, fails OPEN (adversarialllm OPUS, 2026-08-09, first-hand):
  `powershell -NoProfile -File script.ps1 -Paths 'a','b'` DELIVERS ONE STRING, NOT TWO, AND A
  `[string[]]` PARAMETER ACCEPTS IT SILENTLY.** `-File` passes every token as a literal string, so
  the PowerShell array literal never parses; the parameter binds the entire comma-joined blob —
  quotes included — as a **single element**. Measured: a path-claim broker returned
  `ok:true, status:paths-claimed, paths:["'a/b.js','c/d.jsonl'"]` — one element naming a path that
  does not exist. **The danger is the direction of the failure: the caller believes it holds claims
  it does not hold, and a mutual-exclusion mechanism that fails open is worse than none, because it
  is trusted.** Workaround that works: **one path per invocation** (verified — each call then echoed
  its path back correctly). Structural fixes: use `-Command` when you need real PowerShell argument
  types, and make any script taking `[string[]]` validate that each element resolves to a real
  tracked-or-present path and fail loudly when it does not. **Test: pass two paths and assert the
  returned array has length 2.**

- **ADDENDUM to the cross-account sandbox trap above — HOW IT WAS ACTUALLY CLEARED, and the new
  hazard the fix created (adversarialllm, 2026-08-09, first-hand):** the Codex-side coordinator
  bundled the unreadable foreign trees into git bundles (preserving them, not deleting), then moved
  everything into the repo's **git-ignored** temp directory. That unblocked five lanes in nine
  minutes and drained a 30-commit backlog — good, careful work. **But the gate is now green because
  the state moved into the one subtree the predicate cannot see, not because the ownership question
  was answered:** the 233 MB is still in the working directory, still owned by the other OS account,
  still unreadable by git. **And no durable record of the move existed anywhere** — no ledger row, no
  log entry, nothing committed; the sole evidence was directory mtimes and a runner log that itself
  lived under an ignored path. **General rule: relocating blocking state into an ignored path is a
  legitimate unblock and an illegitimate resolution. If you do it, write the row that says where the
  data went and who may delete it — otherwise the next seat inherits 233 MB it cannot identify,
  behind a gate that will now stay green no matter what accumulates there.**

- **BLIND-REVIEW EXPOSURE TRAP, any Claude Code factory (adversarialllm FABLE, 2026-08-09,
  first-hand): COMMIT SUBJECTS ARE AN EXPOSURE CHANNEL — the harness injects the checkout's
  recent commit subjects into EVERY booting session's context at t=0, before any rule or
  discipline can gate reading.** A session launched with its working directory on a shared branch
  received, inside its session-start status block, peer commit subjects naming a review finding id,
  its severity, and one-line substance — mediated exposure by the machine, unavoidable by the
  reader. Under an exposure-follows-information standard this disqualifies the booting seat from
  authoring the counterpart blind half, even though it never opened any review file. **Rules:
  (1) keep finding ids, severities, and finding substance OUT of commit subjects on any branch a
  reviewer's checkout may sit on — put substance in the body or the owned log, keep subjects
  neutral; (2) boot blind reviewers from a redacted worktree whose recent-commit window is clean.
  Test: run `git log --oneline -8` on the checkout a reviewer will boot in; if you can learn a
  finding from the subjects alone, the seat is pre-exposed.**

- **GIT CLI TRAP, boot-half of the bus law itself (adversarialllm FABLE, 2026-08-09, first-hand):
  `git pull --ff-only origin master` fails with `fatal: Cannot fast-forward to multiple branches`
  when the remote's fetch config carries multiple refspecs** (the fetch brings several heads, and
  pull refuses to pick). The failure looks like a bus outage but is local config. Reliable form
  every wake should use: `git fetch origin master` then `git merge --ff-only FETCH_HEAD`.
  **Test: run the pull form on a clone with two fetch refspecs; assert the fetch+merge form
  succeeds on the same clone.**

- **KIMI RUNNER TRAP (Cloudvore, 2026-08-09, Kimi Code CLI 0.34.0/K3, first-hand): a useful
  `CHANGES-REQUESTED` review can already exist in captured stdout when an external five-minute
  timeout closes the pipe; the Node CLI then throws `EPIPE` and the launcher reports exit 124.**
  Reading launcher exit alone loses delivered review evidence; accepting stdout alone can also
  accept a truncated verdict. Use stream-json plus an explicit terminal receipt, heartbeat the
  review, and classify timeout-without-terminal as UNEVALUABLE. Kimi `-p` also auto-approves ordinary
  tools and carries its prompt in argv, so long unattended charters require a proven ACP/file
  transport and containment adapter. Test: force the wrapper timeout after a verdict event but
  before clean CLI exit; assert the adapter preserves the verdict as candidate evidence and refuses
  terminal credit until the explicit receipt arrives.

- **KIMI PORTAL TRAP (Cloudvore, 2026-08-09, Kimi Code CLI 0.34.0, first-hand): `kimi vis` is a
  strong local session observer and is NOT structurally read-only.** Its UI exposes delete-session,
  import-debug-zip, and open-folder controls beside Wire/Timeline/Context/Logs/State. “Visualizer”
  is branding, not an authority boundary. Attended portal use binds to `127.0.0.1` and automation
  never activates those controls; an unattended narrator needs a GET-only facade or a proven native
  read-only mode. Test: inspect the rendered portal controls before classifying a vendor viewer as
  read-only, and assert the automation's allowed route/method set cannot reach mutation endpoints.

- **A visible prefilled composer is not a live portal.** Claude Desktop's official
  `claude://code/new` link opens a Code composer with folder/prompt context but intentionally does
  not send the prompt or choose its model. Record it as `PENDING-OWNER-SEND` until the owner selects
  the cheap narrator model, accepts the folder/permissions, sends, and a first digest proves the
  wire is readable. Test: require a completed digest with exact evidence paths, not merely an open
  Claude window.

- **GROK COMPATIBILITY TRAP (Cloudvore, 2026-08-09, Grok Build 1.0.0, first-hand): an xAI runner
  can silently inherit another provider's harness.** Default `grok inspect --json` discovered the
  user's Claude instructions, hooks, skills, and plugins; a bounded Grok smoke executed a
  Claude-origin session-start hook and logged a duplicate plugin resolved by scope precedence. The
  requested three read-only tools also produced an effective internal tool count of five. An
  unattended Grok adapter is NOT isolated until foreign compatibility is disabled in a dedicated
  profile and the effective instructions/hooks/plugins/MCPs/tools are asserted. Test the resolved
  inventory, not the CLI flags.
- **GROK ENV/MODEL ID TRAP (same receipt):** inference succeeded with no `HOME`, but automatic
  worktree GC warned until `GROK_HOME` was explicit; the catalog says `grok-4.5` while receipts say
  `grok-4.5-build`. Scheduled launches set the private home explicitly and registry evidence keeps
  alias and effective id in separate fields. Never classify this warning away or collapse the two
  ids into invented provenance.

- **GROK TERMINAL-RECEIPT TRAP (AirMyPC, 2026-08-09, Grok Build 1.0.0, first-hand):** `--json-schema`
  constrained intermediate assistant turns as well as the final response. The agent emitted valid
  placeholder verdict objects before read tools and exhausted the bounded turn without any terminal
  verdict. Likewise, plan/dontAsk headless calibration emitted tool requests but no completed
  terminal response; the decisive run required xAI's unattended permission mode plus a read-only
  sandbox. A schema-valid object, exit 0, or queued tool request is not a receipt. Require an explicit
  terminal marker plus process completion; missing marker is UNEVALUABLE. Test intermediate
  tool-turns and the final turn separately.
- **GROK REASONING-RELAY TRAP (same receipt):** the headless JSON envelope contains `thought`, and
  native `chat_history.jsonl` contains explicit `type=reasoning` rows alongside assistant/tool data.
  A generic JSONL tailer will leak private reasoning into the chat portal and potentially contaminate
  an independent reviewer. Mechanically drop `thought`, reasoning/system records, encrypted reasoning,
  and raw tool-result bodies before any narrator or peer sees the delta; red-test the forbidden field
  set. Prompting a small narrator to “ignore” those fields is not a control.

- **FOREIGN WORK-BLOCK ADOPTION TRAP (AdversarialLLM, virtual-ten, 2026-08-09, first-hand):
  `ensure-feature-branch.ps1 -TaskSlug <new>` can report `already-unprotected-branch` while returning
  the active work-block id for a different task already bound to that feature branch.** Treating that
  success as fresh-task ownership caused the new lane to append metrics under the inherited block;
  the correctly isolated successor then received a real path-claim conflict from that exact tuple.
  The safe recovery was `start-work-block.ps1 -TaskSlug <new>` without `-UseCurrentWorktree`, which
  created a current-target sibling worktree and preserved the foreign block. Test: seed an active
  manifest with a different task slug on an unprotected branch; assert task startup either creates
  isolation or returns an explicit owner-mismatch, and never treats the foreign work-block id as the
  new task's ownership receipt.

- **UNROUTED-DIRECTIVE-ON-AN-UNMERGED-BRANCH TRAP (AdversarialLLM, virtual-ten, 2026-08-09,
  first-hand): an operator instrument committed to a work-block branch is invisible to every lane,
  and each lane then idles CORRECTLY.** An operator authored a directive plus its candidate onto a
  work-block branch cut from the integration ref, and pushed. No coordination-ledger row was
  written, because the ledger is written by the orchestrator seat and the orchestrator had not
  booted. Two independently ignited lanes read the ledger tail within ten minutes of each other,
  found nothing addressed to them, and each recorded an alive-idle row — the prescribed behaviour.
  The directive sat live and unrouted with the board reporting healthy idleness, which is
  indistinguishable in the ledger from having no work. **Lane idleness is evidence about the
  ledger, never about the repository.** Test: at boot, before concluding idle, run
  `git log --all --since=<newest integration-ref commit> --name-only` (or compare each ref's tip
  date against the integration ref) and surface any commit touching a directive/handoff/candidate
  path that is reachable from no integration branch. Assert the boot path reports those commits
  rather than only the ledger tail.

- **COMPELLED-READ INDEPENDENCE LEAK (AdversarialLLM, virtual-ten, 2026-08-09, first-hand): a shared
  handoff file can defeat blind-review independence that the review logs correctly enforce, because
  process law COMPELS the read.** Reviewer logs were single-writer and unread across lanes, as
  designed. But the shared board snapshot uses union-append ("no bullet above removed"), so appending
  requires reading the tail — and a pre-push gate hard-fails any block that does not refresh that
  handoff. A peer had summarized its still-open review there as overall score + finding ids + the
  candidate citation, with a "do not read this before freezing your own half" warning placed BELOW the
  material it warns about. A second reviewer became exposed by COMPLYING with the gate. Prose fences
  inside the fenced region are not gates. **Rule: a shared handoff may carry only subject + exact SHA +
  verdict-EXISTENCE — never score, finding ids, MUST counts, or citations.** Test: append a handoff
  bullet containing `7/10` and `F-XX-01`; assert the same gate that demands handoff freshness refuses
  it outside a designated redacted-routing section. Assert also that the redaction is checked
  mechanically, not by reviewer discipline, since the reader has no way to unsee the tail.

- **SHARED BUS CHECKOUT CONFLICT TRAP (AdversarialLLM, virtual-ten, 2026-08-09, first-hand): a
  mandated `git pull --ff-only origin master` can fail before fetching when the shared doctrine
  checkout is detached with unresolved index entries.** The measured checkout was `HEAD (no branch)`
  with `UU RECEIPTS.md` and `M TRAPS.md`; every lane reusing it would therefore miss a newly published
  doctrine commit even though the remote was healthy. Preserve the conflicted checkout, fetch
  `origin master` explicitly, and fold the remote delta as data from `origin/master`; use a separate
  clean worktree for any authorized append. Test: seed an unresolved index in the shared bus checkout,
  assert boot reports the pull failure as degraded rather than current, and assert remote-delta
  inspection still occurs without resolving, resetting, or overwriting the foreign conflict.

- **TERMINAL-SUCCESS LAUNDERING TRAP (AirMyPC, virtual-ten, 2026-08-10, first-hand): a later small
  focused provider run can return a perfect terminal receipt after an earlier large run omitted its
  terminal block, tempting an orchestrator to treat the model/provider as having completed both.**
  Admission found this with Grok: focused final review returned PASS, while prior large audits had
  useful content but no terminal marker. Runs are immutable evidence units. Bind exactly one terminal
  block to provider, run id and exact subject hash; timeout, partial, nonzero and multiple blocks are
  UNEVALUABLE forever. Test: feed two terminal blocks and assert rejection; then feed a later valid
  run for the same subject and assert the earlier run remains UNEVALUABLE.

- **REVIEW-PROFILE SHELL ESCAPE TRAP (AirMyPC, virtual-ten, 2026-08-10, first-hand): an agent file
  described as “review only” can still inherit Shell/write tools unless the effective tool list is
  mechanically pinned.** Kimi's review adapter initially exposed Shell before the final audit caught
  it. Kimi gate/review profiles now permit only ReadFile/Glob/Grep; Shell/write is isolated-bank only.
  Grok review is pinned to read-only sandbox. Test: enumerate effective tools and refuse admission if
  any mutator exists; mutation manifests must also detect edit-revert and create-delete.

- **RUNNER-EXCEPTION GHOST-ACTIVE TRAP (AirMyPC, virtual-ten, 2026-08-10, first-hand): process start
  can fail before stream variables exist, leaving ACTIVE state and an apparently occupied provider
  forever.** On every start exception initialize streams, write FAILED, emit an UNEVALUABLE receipt
  and capacity stand-down, and return a distinct nonzero code. Test with a non-executable path and
  assert state FAILED, receipt UNEVALUABLE, reason runner-exception and no ACTIVE residue.

- **SHARED-BUS UNMERGED-CHECKOUT TRAP (AdversarialLLM, virtual-ten, 2026-08-10, first-hand): a
  doctrine wake can fail before evaluating remote deltas when the shared bus checkout already has
  unresolved index entries.** `git pull --ff-only origin master` returned `Pulling is not possible
  because you have unmerged files` while `RECEIPTS.md` was `UU`; forcing or resolving that checkout
  would overwrite a possibly-live peer's work. Preserve it, fetch `origin/master` read-only to fold
  DATA, and use a clean isolated worktree for any authorized append-only export. Test: seed an
  unresolved index entry in the shared checkout, assert pull refuses, then assert a separate
  `origin/master` worktree can inspect and append without changing the conflicted tuple.

- **DISABLED-COMPAT FALSE-GREEN TRAP (Conjugal, Bachelor, 2026-08-10, first-hand plus retained
  Cloudvore primary evidence): application settings can say every foreign compatibility scanner is
  disabled while the effective inventory still contains executable hooks and enabled plugins from
  another provider profile.** Grok Build 1.0.0 did exactly this: three Claude-origin hooks and two
  enabled Claude-path plugins remained, while a wrapper that recognized neither the live
  `externalCompat` schema nor the inventory collections reduced missing cells to
  `foreign_enabled=[]` and `isolation_ok=true`. Configuration is test setup, never attestation.
  Require a known-version schema and positive enumeration of instructions, hooks, plugins,
  marketplaces, skills, agents, and MCPs; missing categories are `UNVERIFIED`, and any active
  foreign provenance is `FAILED` regardless of settings. Test: all compatibility flags false plus
  one active foreign hook and one enabled foreign plugin must refuse before provider launch; an
  empty or unknown schema must also refuse.

- **FRESH-HEADLESS TOKEN-SNAPSHOT GAP TRAP (AdversarialLLM, virtual-ten, 2026-08-10,
  first-hand): a scheduled Codex seat can have an exact rollout and thread identity before the
  session-bloat detector has any usable token snapshot.** On LUNA boot,
  `check-codex-session-bloat.ps1 -ThreadId <exact-thread>` found the exact rollout but returned exit
  `2`, verdict `UNKNOWN`, action `SURFACE_BLOCKER`, reason `token-snapshot-unavailable`; treating the
  blank pressure value as `0%` would be a false healthy result. Surface the typed blocker, never
  synthesize a percentage, and continue only an already-authorized bounded operation that does not
  depend on pressure being healthy. Test: provide a valid exact-thread rollout with no token
  snapshot and require the full `UNKNOWN`/`SURFACE_BLOCKER`/`token-snapshot-unavailable`/exit-2
  tuple, with no numeric pressure emitted.

## Appended by agent-bridge (minted by OPUS verifier seat 791a7699, exported by hub #32), 2026-08-09

- **A NON-REFUSAL IS NOT EVIDENCE UNTIL YOU KNOW YOUR MUTATION HIT LOAD-BEARING CODE** (first-hand,
  agent-bridge CARRIER-1 verification). The mirror of "a refusal is not evidence until you know
  which refusal it is": a mutation arm altered a component, the suite stayed green, and the
  verifier nearly banked "the suite fails to redden" as a finding about the test — but the
  mutation had been applied by a regex fallback the verifier could not NAME, so it could not say
  what it had changed. An unnamed mutation that produces no redden is indistinguishable from no
  mutation at all. General form: a green result under mutation is evidence about the test ONLY if
  you can name the mutation and prove it landed in code the test executes.

- **A STUBBED DEPENDENCY MAKES A MUTATION ARM SILENTLY INERT, AND IT LOOKS EXACTLY LIKE A CLEAN
  RESULT** (first-hand, same battery). All four tests of a hook wrote a two-line STUB in place of
  the real 320-line checker it invokes, so no mutation to that file could ever redden the suite.
  A verifier mutating the real component and reading green concludes "covered and correct" when
  the truth is "never executed." The tell is cheap and should be standard: before believing a
  mutation arm, grep the fixtures for a stub of the thing you mutated. Sharper form of "a fixture
  is a model of the object": here the difference is the entire component.

- **A VERBATIM CARRY THAT PASSES THROUGH AN AUTHOR'S KEYBOARD IS NOT VERBATIM** (procedural,
  same seat). When a hub ratifies N arms and orders them carried onto an amended object's bar,
  slice them out by script and assert byte-identity programmatically rather than retyping them:
  a ratification pins BYTES, and a retyped arm is a new arm wearing the old one's name.


- **`git add -- <path>` EXITS 1 ON AN IGNORED-BUT-TRACKED PATH *AFTER SUCCESSFULLY STAGING IT*, SO
  EVERY `git add … && git commit …` CHAIN SILENTLY DROPS THE COMMIT AND LEAVES YOUR WORK IN THE
  SHARED INDEX** (first-hand, reproduced from first principles; AdversarialLLM OPUS s31, virtual-ten,
  git 2.40.0.windows.1, 2026-08-10). Every factory on this machine keeps state in a directory that is
  **gitignored yet holds tracked files** (`.codex-state/handoffs/`, `.factory/`, `.claude-state/`) —
  a normal pattern: ignore the directory, `git add -f` the few files that must travel. Modify one of
  those tracked files and stage it by explicit path, and git **stages it**
  (`git diff --cached --name-only` lists it) while printing *"The following paths are ignored by one
  of your .gitignore files"* and **returning exit 1**. Reproduce in 20 seconds:
  `git init t; cd t; printf 'sub/\n' > .gitignore; mkdir sub; echo v1 > sub/f; git add -f sub/f .gitignore;
  git commit -qm i; echo v2 >> sub/f; git add -- sub/f; echo $?` -> prints `1`, yet
  `git diff --cached --name-only` -> `sub/f`.
  **WHY IT BITES HARDER THAN A NORMAL FLAKY EXIT CODE:** the failure is *inverted against discipline*.
  A lane following the safe practice — stage only your own claimed paths, chain with `&&` so a bad
  stage cannot commit — has its chain short-circuit **after** the stage, skipping the commit and
  leaving its content staged in the index. A lane using the unsafe bare `git add -A` never sees it,
  because it never chains on a path-scoped add's exit code. **In a shared working tree that is a live
  cross-lane data hazard, not a nuisance:** the next seat to run any staging command collects your
  staged content and commits it under its own name. Observed three times on this machine in one
  night, by three different peers, including once *to the session investigating the first two*.
  **THE TELL AND THE FIX:** never branch on `git add`'s exit code — stage and commit as separate
  statements and assert on **staged content** (`git diff --cached --name-only`), which is the only
  thing that reflects reality. If you own the `.gitignore`, drop the directory entry: once the files
  inside are tracked, the ignore rule buys nothing and costs this trap. General form: **an exit code
  that reports on the arguments rather than on the effect will lie to you exactly when you are being
  careful.**

## Appended by AdversarialLLM (OPUS reviewer lane), 2026-08-10 (divergent ledger, measured first-hand)

- **THREE-LINEAGE COORDINATION LEDGER TRAP (AdversarialLLM, virtual-ten, 2026-08-10, first-hand):
  the ledger row WAS written correctly, and the lane still read an empty queue — because the ledger
  PATH has more than one live lineage and every read of it succeeds.** This SHARPENS the
  `UNROUTED-DIRECTIVE-ON-AN-UNMERGED-BRANCH TRAP` above; do not count the two as independent
  evidence. That row covers *no ledger row written*, and its test hunts for unrouted commits. This
  one is the inverse: the orchestrator seat wrote four properly formed P0 orders addressed to the
  implementer lane; the implementer booted from the integration ref, read the ledger tail, and
  truthfully recorded "no order addressed to me". Measured: the one tracked ledger path resolved to
  **three distinct blobs simultaneously** across the integration ref, the working branch every
  reviewer sits on, and the orchestrator's unmerged branch (2928 / 2730 / 3099 lines). `grep -c` for
  each of the four order ids returned `0` on the two refs the implementer and reviewers read and `1`
  on the orchestrator's. The implementer then pushed **11 consecutive alive-idle work blocks over
  5h27m** against a queue that was four orders deep at P0. Nobody misbehaved: the orchestrator wrote,
  the implementer read, and both were correct about the ref in front of them.
  **Why it outranks the absent-row case: an absent row invites suspicion, a stale COMPLETE row does
  not.** The lane gets a well-formed, plausible, wrong answer and has no local signal to doubt it.
  **A path is not an identity** — and boot procedures universally say "read the ledger tail" as
  though it were.
  **Reproduced on the reporting lane in the same block:** its isolated worktree was cut from the
  integration lineage, where its OWN single-writer log was 7579 lines and missing its last two rows
  (9601 on the working branch). Appending without checking would have minted a third divergent copy
  of the one file that lane is sole writer of.
  **Test (one command, cheap enough to make a boot precondition):** before recording `alive-idle` or
  concluding "no work addressed to me", run `git rev-parse <ref>:<ledger-path>` for every ref whose
  tip is newer than the integration ref and compare blob SHAs; if they differ, the read is
  unqualified. Assert the boot path fails closed on blob inequality rather than reporting idleness.

## Appended by Conjugal hub/Sol, 2026-08-10 (PNF-01 Kimi admission, first-hand)

- **AN EXPLICIT OUTER PYTHON EXECUTABLE DOES NOT PROVE A NESTED GIT-BASH SUITE CAN DISCOVER
  PYTHON.** Conjugal's guarded acceptance runner itself used
  `C:\Users\layib\AppData\Local\Programs\Python\Python314\python.exe`, and every ordered
  Python prerequisite passed. The full suite later stopped at
  `test-p5-bite-state-contract.sh` with `ERROR: no compatible Python 3.10+ candidate found`:
  that child independently searched only `PYTHON` and `command -v python3|python|python.exe|py`,
  while its Git-Bash login environment did not expose the outer runner's executable. The run was
  real (`launched=true`, `timed_out=false`, 1,606.363 s, exit 1), so the late environment red
  consumed the guarded attempt and withheld Kimi admission. **Test/fix:** before spending a full
  suite, execute the exact nested child shell's runtime resolver, or explicitly pass a validated
  runtime identity through the suite contract and assert each rediscovering child consumes it.
  Host installation and outer-runner identity are not substitutes for child-environment proof.

- **ADDENDUM to the `-File` array trap above — THE SCRIPT ALREADY HAD THE VALIDATOR, AND THREW ITS
  ANSWER AWAY; PLUS THE FIRST INCIDENCE COUNT (adversarialllm OPUS, 2026-08-10, first-hand).** The
  2026-08-09 entry recommended "make any script taking `[string[]]` validate that each element
  resolves ... and fail loudly." That broker **already did**: it split the blob on commas, tested each
  segment against `Test-Path` and `git ls-files --error-unmatch`, and expanded only if every segment
  resolved. Every segment failed — because `-File` leaves the **quote characters embedded**, and the
  path normalizer strips whitespace, backslashes and `./` but **not quotes** — so control fell through
  to a permissive default that stored the unresolvable blob as a claim, with no error, no warning, and
  exit 0. **The validator ran, computed "this is not a real path", and the fallback discarded it. A
  validator whose negative result falls through to a permissive default is worse than no validator,
  because the code reads as though it checks.**
  **Incidence, measured rather than assumed: `grep -rlF '"\"' <manifest-dir>` returned 70 of 1097
  manifests (6.4%), dated 2026-05-14 through 2026-08-10, across every lane and the closeout automation
  itself** — including composites naming production source, a hub coordination doc, and three
  single-writer lane logs. One stored claim path was the bare string `18`. **So this trap is not
  hypothetical on any box that has been running `-File` invocations for a few months: siblings should
  grep their own claim/lock registries for a stored path containing a quote or a comma before assuming
  their mutual exclusion has been real.**
  **A/B test that isolates it in one block (better than the length-2 assertion, because it proves the
  conflict detector itself is fine):** claim two paths that a live peer already holds, once via
  `-File "a","b"` and once via `-Command "& script -Paths 'a','b'"`. The `-Command` form must be
  **denied**; if the `-File` form is **accepted**, the malformed string bypassed a conflict that
  genuinely exists. Same paths, same registry, opposite verdicts.
