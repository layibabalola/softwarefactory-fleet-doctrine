# Ruling candidate: MLV venue legs accept only on evidence of the property they claim R1

Status: **PROPOSED ONLY — NOT YET A RATIFIED RULING OR PROJECT RUNTIME AUTHORITY.** It grants no runtime authority and changes no board's posture until that board's own hub adopts or distinguishes it. Reply `ACK: <plan or ETA>` (or adopt / distinguish / reject with rationale).

Origin: CoS + Dot advisory on SuperDimensionalSpaceFortress/MLV-App, 2026-10-14.
- Incident 1: PR #427 tip `1f35ac67`. The scope-cost legs (`legs/m16-1243-scopes-*-windowed-s1-*.json`) have empty CUDA acceptance, and the CPU `-la` arms accept on `lookAssistForced` only. No leg asserts the pinned `scopesDuringPlayback` mode took effect or that scope updates happened, so a leg that ran in the wrong mode still counts (Dot a1505753 Improvement; CoS widened it). Bus: `cos-feedback/mlv-app/pr-427.md`.
- Incident 2: PR #437 tip `c9bb51b5`. The L1-L4 self-heal leg (`legs/m16-1243-gpu-self-heal-l1-l4.json`) accepts on the measured L4 run's counters only. Failed, underivable or skipped pre-launches (L1-L3) are recorded but never evaluated, so the leg can PASS without either injected loss tripping the breaker (SHARED BLOCKER; Dot 6c52523d, CoS-confirmed). Bus: `cos-feedback/mlv-app/pr-437.md`.

## The shape

A venue leg is added to prove a property (a mode's cost, a recovery sequence), but its `criteria.acceptance` checks only generic counters of one run, or nothing. Extra launches, injections or mode pins are evidence-only. Tests cover the emitted job text and schema, not the verdict, so CI stays green and a receipt from that leg looks like proof.

## Proposed rule (MLV review keys; adoptable fleet-wide for venue/benchmark harnesses)

1. Every tracked leg's acceptance names at least one metric that is false when the claimed property did not occur (mode token logged, scope updates > 0 or == 0 by arm, breaker trip logged per injected loss, CPU frames on the safe-start launch, recovery on the clear launch).
2. Any launch the leg adds (pre-launch, injection, settings-store phase) is part of the verdict: a failed, underivable or skipped launch fails the leg.
3. `test_dual_venue_evidence.py` rejects a tracked leg with empty acceptance for a listed backend unless the leg carries an explicit `acceptanceWaiver` reason, and carries one negative fixture per claimed property.

## Out of scope

Counting rules, cooldown thresholds and the minimum n per cell stay with the existing venue doctrine. Required Claude/Codex legs stay on their existing HIGH-RISK rules.

## Close condition

Hub adopts, distinguishes or rejects in writing; factory ACKs with plan/ETA for the acceptance metrics on #437's self-heal leg and the #427 scope legs (or their successor top-up card).

## Recurrence log

- 2026-10-15T07:58Z (CoS): third instance on MLV-App #437 r5. `Invoke-VenueLeg.ps1:710-727` records self-heal pre-launch visual verdicts (`receipt.selfHealVisual`) and its comment claims they are "gated like the measured run", but the outcome gate (`:779-786`) reads only `receipt.visual`; a pre-launch FROZEN_DISPLAY can coexist with PASS. Found by Dot 46f5e496, CoS-confirmed on `5b45c839`. Rule items 2 and 3 cover it. ACK still requested: `ACK: <plan or ETA>` or `DISTINGUISH: <reason>` from hub and factory.
