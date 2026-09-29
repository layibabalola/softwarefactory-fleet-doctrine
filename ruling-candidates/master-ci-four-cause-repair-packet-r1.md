# CANDIDATE r1: master CI four-cause repair packet (zero runtime authority)

Status: PROPOSED. Filed 2026-09-29 by a bus-auditor chat session, which records only (RULINGS.md:1493-1498).
The diagnosis is in TRAPS.md, "master CI red for ten days on FOUR stacked causes" (2026-09-29).

## Work packet for ONE implementer lane (K1), with one cross-family key (K6), landed as one push

Profile (K5): the subject is the CI repair only. It makes no doctrine change, raises no budgets, and weakens no running stop.

1. **Manifest re-pin.** Take the bytes of `manifests/universal-provider-control-reconciliation-r45.json` exactly as `python tools/refresh_current_universal_manifest.py --candidate <final-candidate-sha>` emits them. The `changedBindings` must be `["README.md"]` only. Any other changed binding refuses the packet.
2. **Hermetic tests.** In `tests/test_phase8_integration.py` and `tests/test_phase9_integration.py`, patch `missing_source_objects` to return the three pinned SHAs in the fail-closed test, the same way the neighbouring `test_present_source_mismatch_is_not_relabeled_unavailable` patches it. The fail-closed branch must still be exercised.
3. **Tighten, not only repair.** Add a `--rederive-source-objects` step for both checkers to `.github/workflows/disposition-intake.yml` (it already uses `fetch-depth: 0`). If that workflow is sealed under `CI-COST-CONTROL.md`, file this step separately rather than bundling it.
4. **Ledger drift.** Diagnose `PROJECT_SPEC_DRIFT` in `test_current_adoption_ledger` from its first failure on `9fe6a1a`, and fix the stale binding, not the check.
5. **Out of scope:** the Windows `WORKER_DEADLINE_EXCEEDED`. That is a spend and running-stop question (TRAPS "A CI deadline that scales with repo history"). The durable fix makes the anchor test's cost independent of history length.

## Proposed standing rule (for ratification)

A commit that edits a file listed in any active manifest's `subjectFiles` must carry that manifest's re-pin in the same commit. A pre-commit or CI guard should enforce this by running the refresh tool and failing when `changedBindings` is non-empty. That ends the README treadmill (22640ed, then ad426fb, 2d30df9 and ae78464).

Positive evidence required for completion (K4): Ubuntu governor, intake and ledger jobs green on the landed SHA. Windows governor remains red under item 5 until that question is ruled on.
