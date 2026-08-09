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
