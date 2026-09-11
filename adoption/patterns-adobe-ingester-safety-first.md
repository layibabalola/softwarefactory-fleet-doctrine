# Adobe Ingester: Safety-First Review & Cross-Family Patterns

**Status:** SECONDARY REFERENCE (complement to MLV-App primary)  
**Date:** 2026-09-11  
**Authority:** Fleet adjudication (swarm synthesis); Adobe factory spec (softwarefactory-fleet-doctrine/specs/adobe-ingester.md), production measurement 2026-09-05  
**Scope:** Projects requiring multi-provider failover, cross-family review independence, or security-critical governance

---

## When to Use Adobe Patterns

Adobe excels where **safety must precede velocity**:
- Multi-provider failover required (Claude + Codex account both active)
- Cross-family review needed (one family reviews the other's code, e.g., Claude reviews Codex work)
- Security-critical or compliance-gated work (hash-pinned control plane, immutable audits)
- Gate-0 feasibility proof required (owner-intensive hardware constraints)

**Do not use if:** Single provider, no cross-family review, velocity prioritized over safety. Use MLV-App instead.

---

## Three Portable Patterns from Adobe

### Pattern 1: Hash-Pinned Control Plane

**What it is:** Executables, manifests, and reviewed control material carry SHA-256 pins. Any tooling upgrade transits an admission gate and re-pins, or fail-closed checks abort.

**Why it works:** Eliminates supply-chain drift without human ceremony. A pinned hash is immutable; a pin mismatch is a hard gate.

**Cost:** Requires governance over every launcher (Scheduled Tasks, app schedulers, wrappers). Census overhead ~2h per project, then maintenance on upgrade.

**Example:** Adobe's `Test-FactoryActuation.ps1` (adobe-ingester.md, line 765–792) pins reviewer control-plane module SHA-256; throw on mismatch before lane population.

### Pattern 2: One-Way-Glass Review (Reviewer Blindness)

**What it is:** Review lanes are blind to each other until publication. No peer verdict, no peer lane material visible to either reviewer until both publish independently.

**Why it works:** Independence by construction, not policy. Reviewers cannot copy verdicts or collide. Both lanes reached production 2026-09-05 (adobe-ingester.md line 526–540) with zero cross-contamination.

**Cost:** Review wrapper complexity; isolated capsule generation; separate ledger tracking per lane.

**Example:** Adobe's Sol (Codex orchestrator) and Luna (Codex implementer) feed blind capsules to Opus and Sonnet (Claude reviewers). Neither Claude lane reads Sol/Luna material before publishing.

### Pattern 3: Phased State Machine (Proposal → Candidate → Ballot)

**What it is:** Work progresses through mechanical states: Proposal (schema check), Candidate (nominated), Ballot (quorum voting). Each state has a gate; any lane can unblock the next.

**Why it works:** Removes judgment calls. Progression is mechanical; no waiting for orchestrator discretion.

**Cost:** Requires quorum model definition; ledger state machine discipline.

**Example:** Adobe Q-025 rev4 (adobe-ingester.md line 667–670) opens Phase A only to Luna (no judgment; Luna state alone gates entry).

---

## Adoption Prerequisites

Before adopting Adobe patterns, ensure:
- **MLV-App foundation in place** (heartbeat, ledger-first, pre-commit gates; see reference-factory-mlv-app-primary.md)
- **Multi-provider account setup:** Both Claude and Codex accounts active, separate quotas
- **Governance readiness:** Audit all launchers (tool census); pin all reviewed material
- **Review independence model:** Define which lanes are blind to which; document capsule boundaries

---

## How to Layer Adobe on MLV-App

1. **Extend heartbeat:** Add multi-provider lane health polling (both Claude and Codex queues)
2. **Hash-pin control plane:** Identify all launchers; enumerate all reviewed material; compute and store SHA-256 for each
3. **Implement one-way-glass:** Add review capsule generation (freeze work order + candidate bytes + tests only; exclude peer verdicts)
4. **Add state machine:** Encode phase gates in ledger state (Proposal marker → Candidate marker → Ballot state)
5. **Enable failover:** Use multi-provider orchestration schema (schemas/multi-provider-orchestration-v1.md) to route between Claude/Codex by quota

---

## Cost Baseline

**Pending P05c Phase 3 measurement** (AirMyPC Luna cross-provider test, post-P05a/P05b):
- Cross-family review verdicts (did Claude+Codex lanes converge on acceptance?)
- Multi-provider cost comparison (Haiku+Sonnet vs. Luna+Opus vs. all four)
- Failover proof (routing worked under provider exhaustion)

Baseline data will populate this section after Phase 3 lands (expected week of 2026-09-18).

---

## Related Patterns

- **Process topology foundation (MLV-App):** see adoption/reference-factory-mlv-app-primary.md — required base layer
- **Factory selection decision tree:** see adoption/decision-tree-factory-selection.md — Layer 1: multi-provider fallback required? → Yes, use Adobe
- **Measurement schema:** see schemas/multi-provider-orchestration-v1.md — phase gates, defect count, parity bounds

---

**Next review:** Post-P05c (after Luna cross-provider test, multi-provider proof complete)
