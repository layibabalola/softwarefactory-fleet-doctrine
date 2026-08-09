# DNG Auto Processor — factory spec (single writer: the DNG fable coordinator)

**Machine:** UltraMagnus (personal box). **Project root:** `C:\code\DngAutoProcessor - Claude`.
**Product:** auto-grading pipeline for DNG timelapse clips emulating the operator's LRTimelapse
keyframe-ramp workflow. **Rewritten wholesale at doctrine seams; artifacts live in
`dng-auto-processor/` in this repo (standards + receipts, byte-anchored in its `EXPORTS.md`).**

## Shape

Six standing lanes, lease-based (`coordination/leases/*.json` is the roster; a lane is its lease,
never a model): `fable` coordinator · `sol` sole correctness gate (Codex-native, exact-byte
verdicts) · `luna` second reviewer/falsification (Codex-native) · `opus` executor host ·
`rotation` design lane · `narrator` read-only ticker. File-based hub (`coordination/hub-*.md`,
append-only via accepted writers only), leases + heartbeats for liveness (H9 two-signal dead edge
with the orphan-pulse check), FINDINGS-CHRONICLE harvested same-day.

## Autonomy stack (all measured in production 2026-08-08/09)

- **Warden-driven succession:** a live coordinator seats executors as orchestrator-hosted
  subagents — five full cycles run (claim → brief-by-derivation → byte-anchored receipts → clean
  `-Handoff` release). Chips only as no-coordinator fallback.
- **Wake floor:** `dng-warden-wake` app-store task, hourly :21 (wake-only scope; fail-closed
  claim writer makes double-seating impossible). Verified firing by `lastRunAt`, never by config.
- **Codex lanes:** desktop automations pulse sol/luna every 10 min against pinned threads;
  codex-cli 0.147.0 installed for new-thread ignition (smoke-proven; production ignition HELD
  behind the I8 package ruling).
- **Ignition independence:** design ceiling CLOSED-ACCEPT at R3 (I1–I8: one-byte-array prompt
  capture, prospective separation events, byte-identity carrier snapshots, bound canonical
  snapshot, launcher-code rule, verdict-blind invocation). The I8 refusal drill exists: 11 arms
  each RED-by-construction with tree-digest zero-child-write proofs, dual-host. Package awaiting
  final falsification + ruling.

## Carve-outs a citing sibling must know

- The real git root is a NESTED repo (`DngAutoProcessor\`); `coordination/` is deliberately in no
  git repo (chip worktrees must not fork it) — our bus exports are therefore copies, not submodules.
- Merges execute via commit-tree (no remote exists on the product repo); master mutation is
  hub-adjudicated CONSENSUS-CALL, never solo.
- Review discipline: batched across defect classes, hard 3-round ceiling, closed sets including
  negatives; every census states its predicate; every green check must be able to fail.

## CLI versions (law 5)

claude 2.1.224 (Claude Code) · codex-cli 0.147.0 (npm global, installed 2026-08-08, exec
smoke-proven). One version per machine per the operator ruling.
