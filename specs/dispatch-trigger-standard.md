# Dispatch Trigger Standard

**How to automatically spawn the right review posture based on available providers.**

## Trigger Rule

When a Haiku agent (or any model) receives a design-review, architecture-audit, or cross-family-validation task:

1. Load `.claude/machine-inventory.yaml` (per-project)
2. Check which provider families are available and `available: true`
3. Count available families:
   - **Both Claude + Codex:** Spawn Conjugal standard posture (see `specs/posture-templates-conjugal-standard.md`)
   - **Claude only:** Spawn Claude-only degraded posture
   - **Codex only:** Spawn Codex-only degraded posture
   - **Neither:** FAIL with constraint violation report

## Conjugal Standard Posture Spawn Pattern

When both families available, spawn:

```
┌─────────────────────────────────────────────┐
│ Designer-Scope (Opus)   [background agent]  │
│ Designer-Verify (Sol)   [background agent]  │
│ Lint-Consistency (Haiku + Luna) [bg agents] │
└─────────────────────────────────────────────┘
         ↓ (all complete)
┌─────────────────────────────────────────────┐
│ Arbiter (Astra) [background agent]          │
│   → Arbitrate Designer findings             │
│   → Pick winners                            │
└─────────────────────────────────────────────┘
         ↓ (arbitration complete)
┌─────────────────────────────────────────────┐
│ Consolidator (Fable) [CHIP - separate task] │
│   → Receive arbitrated findings             │
│   → Weave into adjudication file            │
│   → Commit to repo                          │
│   → Update bus receipt                      │
└─────────────────────────────────────────────┘
```

## Chip Spawning for Consolidator

The **Consolidator (Fable) must run as a chip** (separate task), not a background agent in the orchestrating session:

```python
# In the orchestrator session (after Arbiter completes):

spawn_chip(
    model="fable",
    title="Consolidate design findings",
    prompt="""
    You are Fable, the Consolidator. Receive these arbitrated findings from the review swarm:
    [13 findings from Arbiter output]
    
    Task:
    1. Weave into one coherent adjudication file
    2. Remove restated rationale; one REPLACES per finding
    3. No alternatives; one PROOF per finding
    4. Preserve all cross-family insights
    5. Order by severity
    6. Commit to repo with message: "CROSS-FAMILY REVIEW: Consolidate findings from [models] (N findings)"
    7. Update bus RECEIPTS.md with receipt
    8. Push to bus and report completion
    """,
    checklist=[
        "Adjudication file written",
        "Findings consolidated (no alternatives)",
        "Commit made with proper message",
        "Bus RECEIPTS updated",
        "Push completed"
    ]
)
```

## Fallback Postures

### Claude-Only Degraded

If Codex unavailable:

```
Designer-Scope (Opus)       [bg agent]
Designer-Verify (Sonnet)    [bg agent]
Lint-Consistency (Haiku)    [bg agent]
→ Consolidator (Fable)      [chip]
```

**Missing:** Cross-family validation; no Arbiter arbitration (both families required).

### Codex-Only Degraded

If Claude unavailable:

```
Designer-Scope (Luna)       [bg agent]
Designer-Verify (Sol)       [bg agent]
Lint-Consistency (Astra)    [bg agent]
→ Consolidator (Luna)       [chip, long-context model available]
```

**Missing:** Cross-family validation; no Arbiter arbitration.

## Constraint Violation Handling

If machine inventory shows neither family available:

```
FAIL(constraint_violation)
message: "No provider family available. Check .claude/machine-inventory.yaml and CLI auth."
report: "Cannot spawn review posture. Available providers: {list}. Required: ≥1 family."
```

Do NOT attempt degraded posture or downgrade to solo review.

## Integration Checklist for New Projects

- [ ] `.claude/machine-inventory.yaml` created and committed
- [ ] `machine-inventory-schema.md` read and understood
- [ ] `posture-templates-conjugal-standard.yaml` available in fleet specs
- [ ] Dispatch trigger wired into your project's review workflow
- [ ] SessionStart hook configured to call auth check
- [ ] First review spawns correct posture (verify via agent logs)
