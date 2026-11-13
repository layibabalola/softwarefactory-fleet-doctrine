# tools/machine/fleet-defender/ — Defender exclusions for new write roots (machine tool)

**Problem it solves.** A project creates a heavy-write root (a lane-worktree parent, a build tree, a temp prefix,
a per-test `LOCALAPPDATA` folder) after the machine's Defender exclusion list was written. Defender then scans
every write there. Measured (MLV-App, 2026-10-17, 16-core host): Defender at 1.3–1.7 cores with the host at
91–100% CPU; after the missing roots were excluded it fell to about 0.2 core. The trap card is
`mlv-app/new-write-roots-need-a-defender-exclusion-alert`, filed to `specs/mlv-app/cards.md` through MLV-App's
doctrine outbox (MLV-App PR #489).

**What it is.** A *machine* tool, not a project tool: it is installed once per Windows machine by the owner and
serves every project on that machine. It is therefore not in `tools/factory/registry.json` (the pin runner
runs python/node project tools; this one runs as a SYSTEM scheduled task).

| file | runs as | what |
|---|---|---|
| `Install-FleetDefenderRoots.ps1` | **owner, elevated, once per machine** | merges the policy, copies the runtime files to `%ProgramData%\FleetDefender` (Administrators/SYSTEM write only), registers the `\Fleet\FleetDefenderRoots` SYSTEM task (every 15 min + at startup), adds the SessionStart alert to `~/.claude/settings.json`, runs one pass |
| `Apply-DefenderRoots.ps1` | SYSTEM task | adds an exclusion (long and 8.3 forms) for each request the admin-only policy allows; everything else stays pending with one owner command; never removes an exclusion; `-DryRun` makes no Defender call |
| `Register-DefenderRoot.ps1` | any project, unelevated | appends one request row to `%LOCALAPPDATA%\fleet\defender-roots.json` (idempotent) |
| `Show-DefenderRootsAlert.ps1` | SessionStart hook, unelevated | silent unless a root is pending, a request was rejected, or the task has stopped running; then prints the owner's one-line elevated command |
| `FleetDefenderRoots.psm1` | (module) | all the logic, as pure functions: verdicts, policy merge, manifest, plan, alert |
| `policy.defaults.json` | — | the shipped, machine-neutral policy: deny prefixes plus the Claude temp root |
| `policy.local.example.json` | — | the shape of a per-machine override |
| `Test-FleetDefenderRoots.ps1` | anyone, unelevated | the tests (no Defender call, no machine state) |

## Rules

- **Agents never install and never add exclusions.** An exclusion is a security setting and Defender's list is
  unreadable without elevation. The owner runs the installer elevated; after that the SYSTEM task applies only
  what the admin-only policy allows, and every other request becomes one printed command for the owner.
- **The deny prefixes always hold**: `%SystemRoot%`, `%ProgramFiles%`, `%ProgramFiles(x86)%`, `%ProgramData%`,
  `%LOCALAPPDATA%\Microsoft`, `%LOCALAPPDATA%\Packages`. A local override can add allowlist entries and deny
  prefixes; it cannot remove one, and an allowlist entry under a deny prefix fails the install.
- **Per-machine values never travel** (law 4): the shipped policy names no user, host or project folder. This
  machine's allowed parents and exact roots go in a local override file kept outside the bus clone.
- **Every request path is refused if it could break out of the owner command**: quotes, backtick, `$`, `;`, `&`,
  `|`, `<`, `>`, `%`, control characters. Also refused: relative or UNC paths, drive roots, `..`, a second `:`
  (alternate data streams), a wildcard anywhere but the last segment, and a path that is (or sits below) a
  link or junction, whose bytes may live outside the allowed parent. A top-level folder (`C:\NewThing`) is never
  auto-applied unless listed exactly.
- **What the owner is shown is never taken on trust**: the SYSTEM task writes the status file into the admin-only
  install dir, and the alert still rebuilds the elevated command from re-validated paths instead of echoing it.
  The installer locks the install dir (owner Administrators, no inherited or explicit user rights) before it
  writes a byte into it, and refuses a link or junction there.
- **Provenance**: the installer refuses to run from a tool directory that differs from the clone's `HEAD`
  (`-AllowDirty` overrides, for bytes the owner reviewed) and records the bus commit in
  `%ProgramData%\FleetDefender\install.json`.

## Install (owner, elevated, once per machine)

From a bus clone checked out at a commit you reviewed:

```
pwsh -NoProfile -File <bus>\tools\machine\fleet-defender\Install-FleetDefenderRoots.ps1 -LocalPolicy <path-to-this-machine's-policy.local.json>
```

`-LocalPolicy` is optional (without it only the Claude temp root is auto-applied; everything else is pending for
you). `-NoClaudeHook` skips the settings edit. Re-run to update; a task with the same name under another folder
is replaced. Run it from the account whose `%LOCALAPPDATA%` the projects use (UAC elevation of your own account,
not a separate admin account), because the manifest and status paths are fixed to that profile at install time.

Uninstall: `Unregister-ScheduledTask -TaskName FleetDefenderRoots -TaskPath '\Fleet\' -Confirm:$false`, then
remove `%ProgramData%\FleetDefender`. Exclusions already added stay.

## Use (any project, unelevated)

In the code that creates a heavy-write root:

```
pwsh -NoProfile -File "$env:ProgramData\FleetDefender\Register-DefenderRoot.ps1" -Path <root> -Project <project> -Reason "<why>"
```

Within 15 minutes the root is excluded (if the policy allows it) or the next session start prints the owner
command. Status: `%ProgramData%\FleetDefender\status.json` (`defender-roots-status.v1`), written by the SYSTEM
task in the admin-only dir; the alert still rebuilds the owner command from re-validated paths rather than
echoing a string from the file.

## Tests

```
pwsh -NoProfile -File tools/machine/fleet-defender/Test-FleetDefenderRoots.ps1
```

Verdict cases (including command-injection paths), policy merge and its refusals, a manifest round-trip through
`Register-DefenderRoot.ps1`, a full `Apply-DefenderRoots.ps1 -DryRun` pass with allowed, pending, rejected and
already-excluded rows, the alert with pending entries (and silent, stale and not-installed cases), and a law-4
scan that no shipped file hard-codes a drive path or user folder. Windows and POSIX pwsh; exit code = failures.

Origin: MLV-App `.claude-state/cpu-triage/fleet-defender/` (machine-local, 2026-10-17), generalised here.
