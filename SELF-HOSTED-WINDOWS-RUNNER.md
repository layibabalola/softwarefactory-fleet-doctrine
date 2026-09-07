# Self-hosted Windows Actions runner — fleet playbook

Status: `PLAYBOOK` (doctrine-as-data; adopt, distinguish, or reject locally per Law 1)

Companion to [`CI-COST-CONTROL.md`](CI-COST-CONTROL.md), whose rule 5 already sanctions
"separately controlled self-hosted runners" as evidence. This is the concrete, reproducible
process for moving a project's **Windows** CI off paid `windows-latest` onto a self-hosted runner,
proven on 2026-09-07 by migrating `layibabalola/Cloudvore` and `layibabalola/Conjugal` onto the
always-on box **Ultra Magnus** (i9-13900KS, 32 threads, 128 GB). Windows runners bill at 2x; the
August 2026 ledger put Windows Actions at `$37.43` of the `$50` cap, so this is the largest single
CI-cost lever after fan-out control.

## Outcome (evidence)

- Cloudvore `product-bar` (WPF net8.0-windows build) and `tools-bar` (Python/ctypes) both **green**
  on the runner on the first clean run.
- Conjugal `regression` executes end to end on the runner (long-path checkout, setup-node/python,
  the full bash suite). Its suite is report-only and red-by-design, so "green" there is a repo
  concern, not a runner one — see the fake-shim trap below.

## The process (reusable, reversible at every step)

1. **Register one runner per repo.** Personal-account repos cannot share a runner. Mint a
   registration token where `gh` is logged in (`gh api -X POST
   repos/<owner>/<repo>/actions/runners/registration-token --jq .token`, valid 1 h), download the
   pinned `actions-runner-win-x64-<ver>.zip`, **verify its SHA-256**, `config.cmd --unattended
   --replace --runasservice --labels self-hosted,Windows,X64,<box>`. Confirm `status: online` via
   `gh api repos/<owner>/<repo>/actions/runners`.
2. **Select the runner with a repo variable, not a workflow rewrite.** Change each job's
   `runs-on: windows-latest` to
   `runs-on: ${{ vars.CI_RUNS_ON != '' && fromJSON(vars.CI_RUNS_ON) || 'windows-latest' }}`.
   Turn the runner ON with `gh variable set CI_RUNS_ON -R <owner>/<repo>
   -b '["self-hosted","Windows","X64","<box>"]'`; turn it OFF (back to hosted) with
   `gh variable delete CI_RUNS_ON`. One command flips it; no workflow edit, instantly reversible.
3. **Validate on a PR before merging.** The `pull_request` trigger runs the (patched) workflow on
   the runner without touching `master`. Merge only after the PR run is green.
4. **Meet the host prerequisites** (each is a trap below): Git Bash ahead of WSL on PATH;
   PowerShell `ExecutionPolicy RemoteSigned`; the runner service running as a **real interactive
   user**, not `NETWORK SERVICE`; `git config --global core.longpaths true` and registry
   `LongPathsEnabled=1`.
5. **Before installing any toolchain to satisfy a failing test, check whether the test fakes it.**
   See the fake-shim trap. A suite that stubs its toolchains needs none of them installed; a
   proposed multi-gigabyte install (Java + VS Build Tools + Go + Rust + Gradle + CMake) was
   correctly rejected on exactly this basis.

## Adoption

Any fleet project with Windows CI can adopt without code changes beyond the one-line `runs-on`
expression: register a runner instance for the repo, set `CI_RUNS_ON`, done. Keep hosted as the
documented fallback (delete the variable). The runner service should run as a real user so
`actions/setup-python` and profile-dependent steps behave as they do on hosted.

## Method note: adversarial diagnosis before machine mutation

Diagnosis was fanned out to parallel adversarial agents (one per repo surface, one env-parity
auditor), each read-only, while the hub owned every mutation so parallel agents never collided on
the shared machine. Agent output was **verified before acting** — the toolchain-install plan was
wrong, and reading the test source caught it before ten gigabytes of needless installs. Cheap
parallel diagnosis, single-owner mutation, verify-before-act.
