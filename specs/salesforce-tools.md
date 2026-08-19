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

## Universal token-control R26 current disposition (2026-08-19 phase 3)

Salesforce/context-ultra's current project disposition is:

**DISTINGUISH(909f769d02e8412e51e28e242cfa8d00dadc9a3d, R26_CANDIDATE_ZERO_AUTHORITY_CURRENT_DIRECT_PROVIDER_SUBPROCESS_AND_OPT_IN_SCHEDULED_STANDUP_PATHS_REMAIN_OUTSIDE_A_PINNED_FAIL_CLOSED_SUPERVISOR_PENDING_COMPLETE_LAUNCHER_CENSUS_EXACT_MODEL_EFFORT_ROLE_REVIEW_QUALITY_FUNCTIONALITY_BINDINGS_REQUEST_TOKEN_ACCOUNTING_1000_UNCHANGED_ZERO_INFERENCE_TICKS_FULL_CHILD_FENCING_ROLLBACK_CURRENT_CLOSED_GATE_AND_REVIEW, SALESFORCE_MAIN_3fd3d4a09f77d7b7a5e9fcbc45ca5621ce4727dd, EVIDENCE_SHA256_9f4bedd0700fc2cf3096b3e2ca697a554c5cbb5d10ffe40f3ec56f40172992f4)**

This row folds the independently accepted, project-owned candidate published at
`https://github.com/layibabalola/SalesforceSupportTools.git`, ref
`refs/heads/codex/r26-zero-authority-disposition-candidate-20260819`, commit
`f9f1e9990e5daa3a6d797e26e5c0baeeceb23c2a`, tree
`e45c5badcb0e9cdd48877377d04855fdb7450f13`, sole parent/current project base
`3fd3d4a09f77d7b7a5e9fcbc45ca5621ce4727dd`.

| Published candidate artifact | Git blob | Bytes | SHA-256 |
|---|---|---:|---|
| `docs/provider-control/R26-CURRENT-STATE-EVIDENCE.json` | `15a3e40884dab3be1d76a1aca459d6b4267a1d75` | 6,023 | `9f4bedd0700fc2cf3096b3e2ca697a554c5cbb5d10ffe40f3ec56f40172992f4` |
| `docs/provider-control/R26-DISPOSITION-CANDIDATE.md` | `9704fd3e8c18cf20ff9930f51a3fd634923c4067` | 4,959 | `6e4ede6c672e5bad9152896ea6e4dfeaef2caf0466d3b0b32106381713db5f08` |
| `tools/provider-control/test-r26-disposition-candidate.ps1` | `d9715622ba6472ad5c9bfe9cef61c380a7dd306b` | 23,029 | `07b87c72d353ae02d6b9a8d45aa2992e49a6994d4e53a3e814c09db8fa2f7cf4` |

The project evidence remains `DISTINGUISH_CANDIDATE_ZERO_AUTHORITY`. Its eight authority members
are false. The current source records direct provider process start and optional scheduled standup
reachability, while model and effort remain unpinned for R26 admission; local workflow roles,
redaction/output gates, and deterministic fallbacks are not exact R26 role, review,
quality-equivalence, or functionality receipts. All twelve named adoption proofs remain missing.

This central row records the published candidate as the current distinction after independent
acceptance; it does not rewrite the candidate bytes or turn its all-false authority object into
adoption authority. It authorizes no installation, runtime activation, provider or authentication
action, scheduled-task change, canary, merge, push, publication, or release. The automatic gate
remains CLOSED. A later adoption row still requires the pinned supervisor/adapter, complete
four-surface launcher census, fake-provider and concurrency controls, request reserve/reconcile and
cache accounting, exact model/effort/role/subject/executable/argv binding, exact review and
quality/functionality receipts, 1,000 unchanged zero-inference ticks, full-child quota-domain
fencing, rollback, current persistent CLOSED-gate proof, and separately authorized one-use canary
evidence.
