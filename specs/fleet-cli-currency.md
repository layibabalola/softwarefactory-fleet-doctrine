# Fleet CLI currency: every machine upgrades claude and codex every six hours

**Status: OWNER RULING R13 (Layi, 2026-09-23), binding fleet-wide.** The ruling is filed in `RULINGS.md`
in the same commit as this file. Writer: Cloudvore (Claude Code desktop session on BACHELOR). It is filed
as `specs/fleet-cli-currency.md` because `tools/fleet-membership.mjs` treats any other `specs/` stem as a
project id. The tool is `tools/cli-currency.py` (stdlib Python). Its tests are in
`tools/cli-currency.tests.py`: 30 tests, which drive `run_once`, `process_cli` and `smoke` against a
simulated machine. All 23 mutations planted by the adversarial review were killed.

For every project, this supersedes `RULINGS.md` line 7 ("check on a clock, upgrade at seams") and the
quiet-window cadence in `dng-auto-processor/standards/CLI-UPDATE-WINDOW-STANDARD.md`. It keeps the parts of
those that were measured: one version per CLI per machine, a smoke test after upgrade, rollback on failure,
and logged versions. dng-auto-processor already upgraded automatically every six hours from 2026-09-11
(`specs/dng-auto-processor.md` › "CLI currency"). This makes that the fleet's rule, run by one shared tool.

## 1. The rule

1. **Every six hours, each machine upgrades every managed `claude` and `codex` install on PATH**, with no
   idle gate and no human step.
   - npm installs and Claude's native install go to the exact npm `latest` version.
   - A winget install goes to whatever winget has. If that is behind npm, the run reports `WINGET-LAGS-NPM`.
   - Any other install (Homebrew, for example) is reported as `DRIFT-UNMANAGED` and left alone.

   New releases land without warning, so a check that only reports lets a machine sit a week behind.
2. **Every upgraded install gets a smoke test through its own path, isolated from the machine's
   configuration.**
   - Claude runs `claude -p` on `--model haiku` with `--setting-sources local`,
     `--settings '{"disableAllHooks":true}'` and `--no-session-persistence`. Without these, a user
     SessionStart hook on BACHELOR can open a login window and a browser when the account has drifted.
     Measured with `--debug-file`: the parity hook fired in a plain `-p` run and not in the isolated one.
   - Codex runs `codex exec --ephemeral --sandbox read-only`. It uses the newest Luna model in the CLI's
     model cache at smoke time, and it passes only if the final message (`-o`) is exactly `READY`.
   - An npm codex on Windows also has its extensionless bash shim checked, because bash-launched lanes
     resolve that shim and not `codex.cmd`.

   Every smoke runs with `CLI_CURRENCY_SMOKE=1` in its environment.
3. **Roll back only on evidence.** If the smoke fails, the previous version is reinstalled and verified
   with `--version`, then smoke-tested.
   - If the old version passes, the run records `ROLLED-BACK`. The rejected version is held on that
     machine until npm `latest` moves past it, so a bad release is not reinstalled every six hours.
   - If the rollback does not restore the old version, the run records `ROLLBACK-FAILED`.
   - If both versions fail, the cause is auth, quota or network. The new version stays and the run records
     `UPGRADED-ENVIRONMENT-SMOKE-FAILED`.
   - Winget installs are never rolled back. A failed smoke there records `UPGRADED-SMOKE-FAILED-NO-ROLLBACK`.

   Every one of these statuses, plus `UPGRADE-FAILED` and `CHECK-FAILED` (npm unreachable), makes the run
   exit 1.
4. **A fleet-wide hold.** `policy/cli-currency-hold.json` on the bus (`{"codex": ["0.157.0"]}`) blocks
   named versions on every machine that pulls the bus. It exists so that a release that breaks a lane
   feature the READY smoke cannot see can be stopped everywhere in one commit.
5. **Receipts.** Each run appends one line to `~/.claude/cli-currency/receipts.jsonl` and rewrites
   `latest.json`. Each install's entry records its path, how it was installed (npm, native, winget), the
   versions before and after, the smoke results, the resolved model, the held versions and the swept npm
   leftovers. A run that raises an exception still appends an `error` receipt. A run that finds a live lock
   writes nothing and exits 0. The log rotates at 5 MB.
6. **New models are reported by the same run, never adopted by it.** The receipt's `new_models` lists
   Claude model ids named in the binary and Codex slugs in the model cache that were not there on the
   previous run.

## 2. Folding in new model versions

- **Claude: dispatch by alias** (`--model opus`, `sonnet`, `haiku`) wherever the act does not need an exact
  id. The alias moves with the CLI, so upgrading the CLI adopts the new model. Measured 2026-09-23:
  `--model haiku` resolved to `claude-haiku-4-5-20251001` (receipt `smoke.model`).
- **Codex: resolve the tier at launch.** Codex slugs are versioned (`gpt-5.6-sol`, `gpt-6-sol`) and there is
  no floating alias, so a lane that hard-codes a slug never picks up the next version. Use
  `python tools/cli-currency.py --resolve sol` (or `luna`, `astra`, `terra`). It prints the
  `gpt-<version>-<tier>` slug with the highest version number in `~/.codex/models_cache.json`, and exits 2
  if there is none. It compares version numbers, not list order, and matches the whole tier name
  (`gpt-6-solar` is not `sol`). Measured 2026-09-23: `sol`→`gpt-6-sol`, `luna`→`gpt-6-luna`,
  `astra`→`gpt-6-astra`, `terra`→`gpt-5.6-terra`.
- **A place that must pin an exact id** (a certification, a receipt schema, a ratified panel) pins it
  deliberately. Its owner watches `new_models` and re-pins in its own tree. A pinned id is a decision,
  never a default.
- **The smoke seats are liveness probes, not dispatched seats.** A code string-match checks their output,
  and they produce no analysis, adjudication or durable bytes. So R11 (effort) and R12 (bounded-tier seats)
  do not govern them, and they run at Haiku and Luna-low on purpose.

## 3. Facts the tool relies on (measured, BACHELOR, 2026-09-23)

- **Upgrading under a running process is safe on Windows.** In a throwaway prefix, with that prefix's
  0.154.0 `codex.exe app-server` running, `npm install -g @openai/codex@0.156.1` moved the old package
  directory aside, installed the new one and exited 0. The running process kept working. npm left
  `@openai/.codex-XXXX` behind with `EPERM` on unlink, and that directory could be removed once the process
  exited. The tool sweeps such leftovers on `--apply` runs. Claude's native installer does the same with a
  running `claude.exe`: it was renamed to `claude.exe.old.<n>`.

  An idle gate is therefore not needed, and the fleet has already measured what one costs: TRAPS.md "A CLI
  updater that waits until 'no process of that CLI is running' never updates Claude while the desktop app is
  open".
- **A second install behind the first is real, and it goes stale.** On BACHELOR, `codex` resolved to npm
  0.154.0, with a winget `codex` 0.144.6 behind it on PATH. A launch form that resolves the second install
  would read as a broken CLI.
- **The Claude desktop app runs its own bundled Claude Code** (`%APPDATA%\Claude\claude-code\<version>`)
  and updates it itself. It was on 2.1.280 while the standalone native install that headless `claude -p`
  lanes use sat at 2.1.268, with `autoUpdates: false`. The desktop app being current says nothing about the
  CLI your lanes launch.
- **Output is parsed from stdout only.** An adversarial review reproduced two failures before this version:
  an npm warning on stderr became the "npm prefix", and a trailing CLI warning broke the smoke's JSON parse.
  A child that times out is killed as a tree, by the pid the tool itself started, because killing only a
  `.cmd` shim left its node child holding the pipes.
- **First live run:** claude native 2.1.268→2.1.280, codex npm 0.154.0→0.156.1, codex winget
  0.144.6→0.156.1. All three smoke tests passed and the run exited 0.

## 4. Adoption: one install per machine, not per project

The upgrade is machine-scoped (one version per CLI per box, fleet ruling 2026-08-09), so **one project per
machine installs the schedule, and it covers every project on that box.** Check whether the machine
already has it first.

- **Windows:** `Get-ScheduledTask -TaskName CLI-Currency`. If it is absent, register a task that:
  - runs `python <bus>/tools/cli-currency.py --apply` every 6 h, at a free minute you claim in the MINUTE
    REGISTRY;
  - goes through your box's no-console launcher;
  - has a 2 h execution limit, `IgnoreNew`, and starts and keeps running on battery.

  BACHELOR's registration script, as a template: `%USERPROFILE%\.claude\ops\register-cli-currency.ps1`
  (machine-local, not on the bus). Its action is the PairProg native launcher running `python.exe` with
  CreateNoWindow. Measured on a scheduler launch: the run's children created only windowless `conhost.exe`
  hosts, and no OpenConsole or WindowsTerminal process had the task in its ancestry. The machine
  registry audit (`audit-background-process-registry.ps1`) reported 18/18 compliant.
- **macOS / Linux:** cron has neither npm nor `~/.local/bin` on its PATH, so set PATH in the crontab:
  `PATH=/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:$HOME/.local/bin:<npm prefix>/bin`, then
  `37 */6 * * * python3 <bus>/tools/cli-currency.py --apply >> $HOME/.claude/cli-currency/cron.log 2>&1`.
  The unit tests have run only on Windows so far. The first POSIX adopter runs them and publishes the
  result.
- **Verify** by running it once through the scheduler, not by hand, then read
  `~/.claude/cli-currency/latest.json`.

## 5. What this does not do

- It never kills a process it did not start. When its own child times out, it kills that child's process
  tree by pid, never by name.
- It never touches auth, `~/.claude.json` account state or `~/.codex/auth.json`. Its Claude smoke loads no
  user hooks, so it cannot trigger a login flow.
- It does not upgrade the Claude desktop app or the Codex desktop app. Each updates itself.
- It does not change which model any seat uses. §2 describes how a seat's own launch picks up new models.
- It does not test lane features beyond the READY smoke: `stream-json`, the `workspace-write` and
  `danger-full-access` sandboxes, MCP, and resume are not covered. A project whose lanes depend on one of
  these adds its own probe. When such a feature breaks, the fleet-wide hold (§1.4) stops the rollout.
