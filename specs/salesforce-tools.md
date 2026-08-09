# Context Ultra for Salesforce (Delinea box) - factory spec

Single writer: the Salesforce-tools project hub. Wholesale rewrite at doctrine seams.

## What this factory is
C#/WinForms desktop app (Context Ultra for Salesforce) + KMP Android shared-core scaffold.
Repo: C:\SalesforceSupportTools (rename to Context Ultra naming pending at next seam), remote
github.com/layibabalola/SalesforceSupportTools. Gate: build.ps1 (publish -> self-sign ->
~230-check selftest -> deploy -> relaunch). Canonical state = git log; commit messages name
roadmap items (R<nn>).

## Topology
Single-lane worker pipeline with succession (route-based resume pointer; rollover proven
unsupervised) + a steering seat. No leases/hub files - the build gate serializes one writer
per repo by construction. Parallel lane opens only for the KMP Kotlin port (separate toolchain).

## Doctrine this project measured (exported to RULINGS/TRAPS/RECEIPTS)
- Route-not-readings resume pointers; repo-wins-over-pointer.
- Context self-monitoring from transcript jsonl; window resolved from model id; plan against
  200k even on 1M-window models (mid-session model flips).
- Worker+portal pull visibility; digest-never-dump; portal rollover is the cheap case.
- check-on-clock/upgrade-at-seams CLI discipline.

## Box state (2026-08-08)
claude 2.1.221, codex-cli 0.146.0 (both one release stale; upgrade due at worker rollover
seam). No ~/.codex/automations store configured. JDK 17.0.20 + Kotlin 2.0.21 under profile
(app-control gate PASSED). gh authed (layibabalola).

## Open questions this project owes the fleet
None currently; R43.1 KMP port in flight (worker lane), R44 shipped.
