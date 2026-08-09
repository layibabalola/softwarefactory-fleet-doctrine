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
