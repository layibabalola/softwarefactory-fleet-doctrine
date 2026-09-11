# Factory Selection Decision Tree

**Status:** FRAMEWORK  
**Date:** 2026-09-11  
**Authority:** Fleet adjudication (logistics brief, swarm synthesis); audit of 8 operational factories (CloudVore, Conjugal, etc.)  
**Scope:** All projects choosing initial factory architecture

---

## Quick Decision Path

**Start here:** Answer three questions in order.

### Layer 0: Provider Resilience

**Q: Do you need multi-provider failover (Claude + Codex both active)?**

- **YES** → Go to Layer 1
- **NO** → Go to Layer 1, single-provider branch

### Layer 1: Review Model

**Q: Do you need adversarial cross-family review (one family reviews the other's code)?**

- **YES (multi-provider failover required)** → **ADOBE** — Hash-pinned control plane, one-way-glass review, phased states
- **YES (single provider, but adversarial review required)** → **MLV-APP** (baseline topology only; add adversarial Haiku/Sonnet swarms on top of heartbeat+ledger)
- **NO (single provider, lean governance)** → Go to Layer 2

### Layer 2: Autonomy

**Q: Can decisions be automated, or do they require human judgment gates?**

- **Human-in-the-loop (quorum, adjudication, escalation needed)** → **MLV-APP** — Process topology + ledger-first model; governance is mechanical
- **Fully autonomous (zero human gates, three-pass validation)** → **CLOUDVORE** — Single-lane Codex automation; no seats, no review gates, deterministic three-pass acceptance

---

## Factory Profiles

### MLV-App (Primary Reference)

**What:** Process topology overhead collapse; heartbeat + ledger-first + pre-commit gates.

**Best for:** Throughput-critical work, multi-lane dispatch, mechanical governance (no judgment calls).

**Start:** Phase 1 (heartbeat, ledger, pre-commit). Add lanes as needed.

**Cost:** Low overhead (10-min heartbeat); scales to 4+ lanes on Windows Scheduled Tasks.

**Failover:** No built-in multi-provider; single provider assumed. Add Adobe patterns if failover required.

**Authority:** adoption/reference-factory-mlv-app-primary.md

---

### Adobe Ingester (Safety-First Secondary)

**What:** Cross-family review independence; hash-pinned control plane; phased state machine.

**Best for:** Multi-provider failover, security-critical work, compliance audits.

**Start:** MLV-App Phase 1 first, then layer Adobe patterns (one-way glass + hash-pinning).

**Cost:** Governance overhead (~2h launcher census); review capsule generation per cycle.

**Failover:** Built-in; routes between Claude and Codex by quota.

**Authority:** adoption/patterns-adobe-ingester-safety-first.md

---

### CloudVore (Autonomy-First Niche)

**What:** Single-lane Codex automation; zero seats, deterministic three-pass validation.

**Best for:** Autonomous factories, no human gates, throughput-only (not safety-gated).

**Start:** Deploy automation directly; no seat leases or heartbeat dependency.

**Cost:** Minimal (inline validation); single lane only.

**Failover:** No failover (single provider); autonomy only.

**Authority:** specs/cloudvore.md (not yet published to adoption/)

---

## Decision Table (Quick Lookup)

| Constraint | Best Fit | Why | Cost |
|---|---|---|---|
| Multi-provider + cross-family review | Adobe | Failover + blindness proven | ~2h setup, governance overhead |
| Single provider + throughput | MLV-App | Topology collapse measured | 10-min heartbeat, ~1h setup |
| Single provider + no review gates | CloudVore | Automation minimal; three-pass | ~1h setup, inline validation |
| Single provider + human governance | MLV-App | Ledger-first, mechanical gates | 10-min heartbeat, ~1h setup |

---

## Adoption Steps by Choice

### If You Choose MLV-App

1. Read adoption/reference-factory-mlv-app-primary.md (phased path: Phase 1–3)
2. Deploy heartbeat (Windows Task, `tools/Invoke-AudioMileResumeHeartbeat.ps1` pattern)
3. Wire ledger (append-only DECISIONS.md)
4. Add pre-commit gates (repo-specific, transportable pattern)
5. Test Phase 1 (heartbeat fires every 10 min; no lane dispatch yet)
6. Add lanes (Phase 2) when ready

### If You Choose Adobe (MLV-App + Patterns)

1. Deploy MLV-App Phase 1 first (heartbeat, ledger, pre-commit)
2. Read adoption/patterns-adobe-ingester-safety-first.md (three patterns: hash-pinning, blindness, states)
3. Audit all launchers; compute SHA-256 pins for all reviewed material
4. Implement one-way-glass review capsule generation
5. Encode phased states in ledger (Proposal → Candidate → Ballot)
6. Test multi-provider account routing (Claude + Codex both active)

### If You Choose CloudVore

1. Read specs/cloudvore.md (when published to adoption/)
2. Deploy Codex single-lane automation directly
3. No heartbeat or seat leases needed
4. Test three-pass validation (deterministic acceptance)

---

## When to Reconsider

- **MLV-App + multi-provider needed** → Adopt Adobe patterns on top
- **Adobe + single provider only** → Simplify to MLV-App Phase 1
- **CloudVore + governance required** → Migrate to MLV-App (re-platform for human gates)

---

## Related Resources

- **MLV-App primary reference:** adoption/reference-factory-mlv-app-primary.md
- **Adobe patterns (safety-first):** adoption/patterns-adobe-ingester-safety-first.md
- **Measurement schema (Phase gates, cost baseline):** schemas/multi-provider-orchestration-v1.md
- **Fleet audit (all 8 factories):** docs/FLEET_FACTORY_AUDIT_20260911.md (to be published after Phase 1)

---

**Questions?** Reference the factory profiles, then read the adoption guide for your choice.
