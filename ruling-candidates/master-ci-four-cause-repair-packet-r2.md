# CANDIDATE r2: master CI repair packet (supersedes r1; zero runtime authority)

Status: PROPOSED, and being executed as a kernel subject on 2026-09-29. It supersedes
`master-ci-four-cause-repair-packet-r1.md`, which is left untouched. The corrections are recorded in TRAPS.md
("CORRECTION to the four-cause CI TRAP", 2026-09-29). The chat session orders, integrates and records only; it
writes no fix bytes.

## Roles (kernel K1 / K6 / K4)

- K1 implementer: a headless `claude -p` (Anthropic family, latest Opus, effort high). It runs in a detached
  scratch worktree with the git environment scrubbed (see the 63ca737 cloudvore TRAP), commits locally, and
  never pushes.
- K6 key: `codex exec -s read-only` (OpenAI family, latest tier, effort high). It works from a fresh process
  that has not seen the implementer transcript, reviews the exact diff and re-runs the gate.
- A key REFUSE with a reproduced defect goes back to K1, and the exact new subject is re-keyed. There is no
  round cap.
- K4 completion: the named jobs must be green on the landed SHA. Local runs are not evidence of completion.
- Both landings are integrated in ONE push, as separate commits, each keyed separately (`CI-COST-CONTROL.md`
  batching).

## Landing A: unsealed

The bytes of `manifests/universal-provider-control-reconciliation-r45.json` are exactly the `manifest` that
`python tools/refresh_current_universal_manifest.py --candidate <sha>` emits. The only allowed `changedBindings`
is `["README.md"]`.
- K4: the Ubuntu jobs of `Provider capacity governor contracts` are green.

## Landing B: sealed; an intake-epoch amendment following the 8727672 precedent

1. Phase-8 and phase-9 fail-closed tests: patch `missing_source_objects` to return the three pinned SHAs, so
   the `SOURCE_OBJECTS_UNAVAILABLE_NOT_REVERIFIED` branch is still exercised hermetically.
2. `tools/check_adoption_ledger.py` `CURRENT_NON_PROJECT_SPECS`: add `specs/fleet-cli-currency.md` and
   `specs/fleet-jev-shadow-mode.md`, both portable fleet doctrine and not member project specs. The key must
   confirm that classification.
3. `adoption/current-token-control-r26.json`: add both to `nonProjectSpecs`. Every other change must be
   emitted verbatim by `python tools/refresh_current_adoption_census.py`, which must then exit 0. Dispositions
   are unchanged.
4. `adoption/current-intake-epoch-r1.json`: re-seal every touched control file (bytes, sha256, gitBlobOid) in
   the SAME commit.
   `python tools/check_current_intake_epoch.py` must pass.
- K4: R26 disposition intake (phase-8 and phase-9 steps reached and passing) and the R26 adoption ledger are
  green.

## Out of scope and parked

- **Windows governor cells:** `DEADLINE_SECONDS=720`, `CHILD_FAILED`, and runtime that grows with history.
  Resume condition: an anchor test whose cost does not depend on history length, run as its own K1/K6 subject.
  No budget change.
- **The `--rederive-source-objects` CI step:** it goes in a separate doctrine epoch (`CI-COST-CONTROL.md`
  rule 1).
- **Treadmill guard:** a CI job, not a git hook (hooks run with `GIT_DIR` set; 63ca737 TRAP). It must fail
  when a subject file of an active manifest changes without its re-pin.
