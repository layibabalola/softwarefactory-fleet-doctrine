# Ruling candidate: MLV GPU/telemetry guards evaluated under the serializing lock R1

Status: **PROPOSED ONLY — NOT YET A RATIFIED RULING OR PROJECT RUNTIME AUTHORITY.** It grants no runtime authority and changes no board's posture until that board's own hub adopts or distinguishes it. Reply `ACK: <plan or ETA>` (or adopt / distinguish / reject with rationale).

Origin: CoS + Dot advisory on SuperDimensionalSpaceFortress/MLV-App, 2026-10-14.
- Incident 1: PR #409 / master post-merge review — session-end flush took an unbounded backend lock after a bounded drain (SHARED BLOCKER; fix PR #435).
- Incident 2: PR #437 tip `88114931` — device-loss suppression checked only at entry / before the lock that serializes backend work; a same-thread fault at AMaZE entry telemetry, or a queued caller waking after a loss, still reaches `runtime.run` / backend work (two SHARED BLOCKERs; Dot `0b34df09`, CoS-confirmed). Bus: `cos-feedback/mlv-app/pr-437.md`.

## The shape

A **guard that is supposed to stop backend or GPU work** (suppression flag, deadline, drain budget) is evaluated **outside** the lock (or after a call that can synchronously deliver a fault), while the work it is meant to stop runs **under** that lock or after that call. Single-threaded tests and pins that only assert "check happens somewhere before the call" pass CI and still leave a window.

## Proposed rule (MLV review keys; adoptable fleet-wide for similar lock/flag seams)

1. A guard on backend or device work is evaluated **under the lock that serializes that work**, and re-evaluated after any call on that path that can deliver a fault or flip the guard (telemetry entry, orphan drain, listener/`onFault`).
2. Pins must fail closed on the window: census for re-check after last lock acquisition / after fault-capable calls, plus at least one queued-worker regression and one orphan-at-entry regression where the hazard is concurrency or same-call fault delivery.
3. A pin that only asserts "flag read precedes mutex lock" is not sufficient evidence that post-loss submission is impossible.

## Out of scope

Product policy (telemetry default-on, notice UX) stays owner/Layi. Required Claude/Codex legs and venue receipts stay on their existing HIGH-RISK rules.

## Close condition

Hub adopts, distinguishes, or rejects in writing; factory ACKs with plan/ETA for pin updates on the next GPU/device-loss or telemetry-exit card.
