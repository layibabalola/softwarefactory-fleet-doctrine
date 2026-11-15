# Pattern: PATH defense and self-healing on every fleet machine (2026-11)

**Status:** doctrine is data (law 1). Each member adopts or distinguishes this pattern. Each
machine acks it separately (section 5), because PATH belongs to a machine, not to a board.
**Owner request:** *"Update doctrine bus. We need PATH defense and self healing for all machines in
the fleet. Have every machine ack."* (Layi, 2026-11-14, in chat; relayed from the AdversarialLLM
controller session on VIRTUAL-TEN to a bus session, which authored this file.)
**Evidence:** `TRAPS.md`, the entry "An overlong Windows PATH can break shell-string child commands
while direct executables still work" (AdversarialLLM, 2026-08-17), and its recurrence entry of
2026-11-14 from ULTRA-MAGNUS.
**Instruments:** `tools/Repair-MachinePath.ps1` (check, repair, publish),
`tools/Get-FleetPathHealthStatus.ps1` (reader), `tools/Repair-MachinePath.tests.ps1`.
**Relationship to existing doctrine:** extends `SELF-HOSTED-WINDOWS-RUNNER.md` step 4 (host
prerequisites) and reuses the heartbeat ack contract (`heartbeats/README.md` "How to ack") for a
new surface, `path-health/`. It supersedes nothing.

## 1. What breaks, and why it keeps coming back

Every Windows process starts with PATH = Machine PATH + `;` + User PATH, read from the registry.
Both incidents on the bus had PATH over 8,191 characters, the limit Microsoft documents for a
`cmd.exe` command line: 17,592 characters on VIRTUAL-TEN (2026-08-17) and about 10,580 (9,584 User + 994 Machine) on ULTRA-MAGNUS
(2026-11-14). In both, any child that went through `cmd.exe` could no longer find tools by name,
while pwsh, bash and direct executable calls still worked. That includes npm install scripts,
`actions/setup-go`'s `go env`, and Node's `execSync('git …')`. The exact threshold was not isolated.

The growth on ULTRA-MAGNUS has a cause we can read in source. The .NET CLI's first-run step adds the
global-tools folder to the **persisted User PATH** (registry, `CurrentUser`) unless
`DOTNET_ADD_GLOBAL_TOOLS_TO_PATH` is false. The documented default is `true`. Checked in
`dotnet/sdk` at `5947e1a3`:

- `src/Cli/dotnet/FirstRunExperience.cs` reads `DOTNET_ADD_GLOBAL_TOOLS_TO_PATH` (`defaultValue: true`).
  It keeps its "already done" sentinel, `<version>.toolpath.sentinel`, under
  `CliFolderPathCalculator.DotnetUserProfileFolderPath`, which is `<DOTNET_CLI_HOME>\.dotnet`.
- `src/Cli/Microsoft.DotNet.Configurer/CliFolderPathCalculator.cs`: when `DOTNET_CLI_HOME` is set,
  `WindowsNonExpandedToolsShimPath` is the absolute `<DOTNET_CLI_HOME>\.dotnet\tools`. Without it,
  the path is `%USERPROFILE%\.dotnet\tools`.
- `src/Cli/dotnet/ShellShim/WindowsEnvironmentPath.cs` appends that path to the User PATH with
  `SdkEnvironmentVariableTarget.CurrentUser`. It skips the append only if the same path is
  already on the process, User or Machine PATH. So a gate that puts its per-run tools folder on its
  own **process** PATH before the first `dotnet` call also stops the write: a second guard, next to
  the env var.

So a gate that gives every run a fresh `DOTNET_CLI_HOME` gets a new sentinel location and a new
tools path each time. Each run appends one more User PATH entry. The run's folder is then deleted
and the entry stays behind as a dead folder. ULTRA-MAGNUS had about 85 of them
(`D:\ContextUltraWindowsGate\<runId>-<n>\cli-home\.dotnet\tools`,
`C:\ContextUltraWorktrees\v-*\…\dotnet-home\.dotnet\tools`, and one under `C:\DngAutoJobs\evidence\`).
VIRTUAL-TEN had one, from a different project
(a per-run `…\scratch\dotnet-home\.dotnet\tools` folder), measured by the
first `-Check` on 2026-11-14. The pattern is fleet-wide, not one gate's bug.

`DOTNET_SKIP_FIRST_TIME_EXPERIENCE` does **not** stop this. Microsoft's environment-variable
reference says it "is no longer supported in .NET Core 3.0 and later" and points to
`DOTNET_NOLOGO`, which only silences the banner. The variable that stops the PATH write is
`DOTNET_ADD_GLOBAL_TOOLS_TO_PATH=0`.

## 2. Rule (a): no tool, gate, test or CI job persists PATH

- A tool, gate, test or CI job never writes the User or Machine PATH. A per-run tool folder goes on
  the **process** PATH only (`$env:Path = "$dir;$env:Path"` in that process or its children).
- Wherever `DOTNET_CLI_HOME` is set per run, set these in the same environment, before the first
  `dotnet` call:

  ```powershell
  $env:DOTNET_ADD_GLOBAL_TOOLS_TO_PATH = '0'   # the one that stops the User PATH write
  $env:DOTNET_NOLOGO = '1'                     # banner only
  $env:DOTNET_SKIP_FIRST_TIME_EXPERIENCE = '1' # no effect on .NET Core 3.0+; harmless, set for older SDKs
  ```

  The same applies to any other installer that "adds itself to PATH" by default (pnpm setup, rustup,
  scoop, winget portable links). Pass its no-modify-path option in automation.
- **Test for your gate:** read the User PATH before a run (`[Environment]::GetEnvironmentVariable('Path','User')`),
  run the gate once with a fresh home, and read it again. Any difference is a leak.

## 3. Rule (b): self-heal with `tools/Repair-MachinePath.ps1`

| Mode | What it does | Needs Administrator |
|---|---|---|
| `-Check` | Read-only. Reports User and Machine PATH length and segment count, plus dead, duplicate and empty entries. Runs `cmd.exe /d /c git --version` with the PATH a new process would get (cmd's own command search, which honours a quoted entry that `where.exe` skips). Reports each runner under `C:\actions-runners\*`: its `.path` length, and whether `.env` exists and sets a non-empty `LANG`. Exit 0 HEALTHY, 1 UNHEALTHY, 2 UNEVALUABLE. UNHEALTHY means any of these: the total is over 4,096 characters; either scope has an absolute entry whose folder is definitely gone; either scope has a malformed quote (an odd quote count, or quotes that do not wrap the whole entry: `user-unbalanced-quote:N` / `machine-unbalanced-quote:N`); the cmd probe failed; or a runner's `.path` or `.env` is missing, empty or wrong. Duplicates alone are reported but are not a finding. The git probe is a smoke test, not a reproduction of the failure; the length limit is the real guard. Length counts every character a new process receives, whitespace padding and empty entries included. Run it from a 64-bit pwsh: a 32-bit process on 64-bit Windows sees a redirected System32 and exits 2 (UNEVALUABLE). | No |
| `-Apply` | Backs up both scopes (raw value and registry kind) under `%LOCALAPPDATA%\FleetPathRepair\<utc>\` before any write. Removes dead, empty and duplicate User PATH entries, including User entries that repeat a Machine entry. Removes **dead** Machine PATH entries only when elevated. It keeps the raw `%VAR%` text and the order of what remains. **It never removes** any of these: an entry whose folder exists; a folder it cannot inspect (access denied); a UNC entry; an entry written with a `%VAR%`, whether judged dead or duplicate (it was expanded with this process's environment, which a harness may have overridden), including one that expands to several folders; a relative entry; an entry on a drive that is not mounted; any entry containing a quote, balanced or not; or the not-yet-created `%USERPROFILE%\.dotnet\tools` and `%APPDATA%\npm`, in either scope. Installers write those last two before the folder exists, and their own sentinels never re-add them. It rewrites a runner's `.path` only when the service account has the same SID as the current user (`.\name` is the local account), and only when `.path` is missing, empty, over the limit, or still holds a dead entry it just removed. A hand-ordered `.path` is kept. It restarts that runner's service only when elevated and `gh api` reports `busy: false`; otherwise it skips the restart and says why. One residual race is accepted: a job picked up between that read and the restart is interrupted. It writes `receipt.json` even when a later step fails. Exit is the post-repair check verdict, or 2 if any write failed. | Only for Machine PATH entries and runner restarts |
| `-Publish` | Adds the ack (section 5) to either mode; after a failed `-Apply` (exit 2) it publishes nothing. It publishes only from a `master` checkout. It refuses a detached HEAD, an index that already holds staged files, and any push that would carry a commit other than the ack (for example local, unpushed commits on a board's own checkout). | No |

`-Apply` is each machine's owner's call. No session runs it on a machine without the owner asking.

## 4. Rule (c): a check that runs without anyone remembering

Each machine wires `-Check` into a path that runs on its own, and alerts on a failure exit (codes below). That
is the adoption step. **The bus never installs it.** Two shapes that fit:

- **SessionStart** (Claude Code, user scope): a hook that runs
  `pwsh -NoProfile -File <bus>\tools\Repair-MachinePath.ps1 -Check` and prints its output only when
  it exits non-zero. Keep it quiet on HEALTHY, and give it a time cap: the check takes a few seconds.
- **Scheduled task**, daily: the same command with `-Publish` added, so the machine's ack stays fresh.
  With `-Publish` the exit codes change: **10** is acked HEALTHY (quiet), **11** is acked UNHEALTHY
  (alert: repair due), and anything else (1, 2, 4, or 5 if `-NoPush` slipped in) means no ack was published (alert). Do not
  alert on "non-zero" here: a successful ack is never 0.
  Launch it through a hidden-window shim, not a bare `pwsh.exe` under an Interactive principal
  (see the 2026-08-30 TRAPS entry on console windows).

A capability with no caller protects nothing (`heartbeats/README.md`). One fixed PATH that nobody
rechecks just restarts the same slow growth.

## 5. Rule (d) and the per-machine ack

**(d) Runner registrations keep `.env` and `.path`.** This is now a host prerequisite in
`SELF-HOSTED-WINDOWS-RUNNER.md` step 4. On ULTRA-MAGNUS, `.path` had gone missing and `.env` had
been cut down to one line (`ACTIONS_RUNNER_HOOK_JOB_COMPLETED=…`). Re-adding a hook variable must
append to `.env`, never overwrite it.

**The ack.** The artifact IS the ack, as for heartbeats. Each machine runs one command. It needs no
Administrator, only git with push access to the bus, and it takes a few seconds. Run it in
PowerShell 7 or Windows PowerShell (PowerShell 7, `pwsh`, must be installed: the tool needs it):

```powershell
$d=Join-Path $env:TEMP ("fleet-path-ack-" + [guid]::NewGuid().ToString("N").Substring(0,8)); if (-not (Get-Command pwsh -ErrorAction SilentlyContinue)) { "BLOCKED: PowerShell 7 (pwsh) is not installed" } else { git clone -q --depth 1 --filter=blob:none --sparse https://github.com/layibabalola/softwarefactory-fleet-doctrine.git $d; if ($LASTEXITCODE) { "BLOCKED: git clone exit $LASTEXITCODE" } else { git -C $d sparse-checkout set tools path-health; if ($LASTEXITCODE) { "BLOCKED: git sparse-checkout exit $LASTEXITCODE - clone kept at $d" } else { $rc=$null; pwsh -NoProfile -File "$d\tools\Repair-MachinePath.ps1" -Check -Publish -BusRoot $d; $rc=$LASTEXITCODE; if ($rc -in 10,11) { Remove-Item -Recurse -Force $d; "ACK DONE (exit $rc)" } else { "BLOCKED: exit $rc - clone kept at $d" } } } }
```

It clones master fresh into a temporary folder, so it never touches a board's own bus checkout or
branch. It runs the read-only check and publishes `path-health/<MACHINE>.json` to master. The record
holds counts, verdict and ordinal runner labels only: no paths, no user names, no runner folder
names (law 4). It pushes only when the content changed or the record is over 24 hours old (law 3).

The last line it prints is `ACK DONE (exit 10)`, `ACK DONE (exit 11)`, or a line starting `BLOCKED:`
(pwsh missing, `git clone` or `git sparse-checkout` failed, or the tool exit code):
- `ACK DONE (exit 10)`: acked, HEALTHY. The clone is deleted.
- `ACK DONE (exit 11)`: acked, UNHEALTHY. The clone is deleted. The repair is `-Apply`,
  separately. An UNHEALTHY ack is still an ack: it tells the fleet the machine looked.
- `BLOCKED: exit <n>`: the check could not evaluate (2), the publish failed (4), or pwsh itself
  failed (1, a parse or parameter error: a success is never 0 or 1 here). The clone is kept for
  diagnosis (a failed publish leaves no ack commit in it). Each run uses a new folder, so a retry
  never collides with a kept clone. Record it as a BLOCKED line (below).

Parsed with zero errors in Windows PowerShell 5.1 and PowerShell 7.6.

**The ledger:** `pwsh -NoProfile -File tools/Get-FleetPathHealthStatus.ps1` lists every machine as
ACKED (with HEALTHY/UNHEALTHY), STALE (older than 7 days), ABSENT, DISTINGUISHED or BLOCKED. The
roster is derived from the `machine` field of `heartbeats/*.json`, from existing acks, and from
RECEIPTS lines. Nothing hard-codes it.

**Only two cases go to `RECEIPTS.md`, one line each**, because the artifact cannot express them:

```text
- <YYYY-MM-DD> PATH-HEALTH: DISTINGUISH <MACHINE> - <one-line reason>
- <YYYY-MM-DD> PATH-HEALTH: BLOCKED <MACHINE> - exit <code>: <message>
```

A board records its decision on rules (a) to (c) in its own spec at its next fold (R14 single
writer), as `PATH-DEFENSE: ADOPTED (<where>)` or `PATH-DEFENSE: DISTINGUISHED (<reason>)`.
