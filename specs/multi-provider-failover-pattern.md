# Multi-Provider Failover Pattern

**Authority:** Adobe Document Cloud Ingester factory, multi-provider strategy adjudication  
**Status:** WORKING STRATEGY, designed 2026-09-11  
**Rationale:** Enable factories to operate across Codex + Claude with seamless failover; add future providers (Grok, Kimi) without redesign

---

## Problem

**Single-provider factories are brittle:**
- If Claude account exhausts tokens, all Claude reviewers stall (Opus, Sonnet)
- If Codex account exhausts tokens, all Codex work stalls (Sol, Luna, Astra)
- Account rotation gaps (credentials expired, re-auth) block the entire factory

**Naive failover (switch provider manually) is slow:**
- Requires owner decision
- Loses work in flight
- No graceful degradation

---

## Solution: Provider Pool Abstraction

**Core idea:** Decouple work roles from specific providers. Define per-role **failover slots** (Primary → Fallback → Degraded). Lane runners check slot availability transparently; switch providers invisible to the factory.

### Architecture

**One new module:** `.factory/tools/Invoke-ProviderPool.ps1` (~150 LOC)

```powershell
# Exported functions:
Get-PrimaryProvider -Role <role>           # Returns primary provider slot for role
Get-FallbackProvider -Role <role>          # Returns fallback slot
Get-DegradedProvider -Role <role>          # Returns degraded-tier slot
Update-ProviderBudgetState -Provider <p>   # Record token usage post-run
Test-ProviderAvailable -Provider <p>       # Quick liveness check (API endpoint, not full request)

# State:
$Global:ProviderPoolState = @{
  'claude'  = @{ tokens_remaining=..., last_refresh_utc='...', exhausted=$false }
  'codex'   = @{ tokens_remaining=..., last_refresh_utc='...', exhausted=$false }
  'grok'    = @{ tokens_remaining=..., last_refresh_utc='...', exhausted=$false }
  'kimi'    = @{ tokens_remaining=..., last_refresh_utc='...', exhausted=$false }
}
```

### Per-Role Failover Slots

| Role | Primary | Fallback | Degraded | Decision Rule |
|------|---------|----------|----------|---|
| **Pre-impl design** (Astra) | Codex/Astra | Claude/Fable | Luna/Haiku | If Astra exhausted, use Fable (same high-inference design role, different provider) |
| **System review** (Opus) | Claude/Opus | Codex/Sol | Luna | If Opus exhausted, use Sol (both high-inference system reviewers); fallback Luna is lower quality |
| **Code review** (Sonnet) | Claude/Sonnet | Codex/Luna | Haiku | If Sonnet exhausted, use Luna (different role but available); fallback Haiku (cheapest, lowest quality) |
| **Orchestrator** (Sol) | Codex/Sol | Claude/Fable | Luna | If Sol exhausted, use Fable (both orchestrators); fallback Luna (not ideal but available) |
| **Implementer** (Luna) | Codex/Luna | Claude/Haiku | (queue) | If Luna exhausted, use Haiku for cheap exploratory work; block implementation until rotation |

### Failover Activation

Lane runner (before starting work):

```powershell
$provider = Get-PrimaryProvider -Role $role
if (Test-ProviderAvailable -Provider $provider) {
  # Proceed with primary
  $session = Invoke-Claude -Model "$provider/$model" @args
} else {
  $fallback = Get-FallbackProvider -Role $role
  if (Test-ProviderAvailable -Provider $fallback) {
    # Log failover; switch to fallback
    Add-Content $laneLog "PROVIDER_FALLBACK $role primary=$provider fallback=$fallback"
    $session = Invoke-Claude -Model "$fallback/$fallback_model" @args
  } else {
    # Both primary and fallback exhausted; queue work
    Add-Content $laneLog "QUEUED_AWAITING_ROTATION role=$role reason=both_providers_exhausted"
    exit 75  # Signal queue to HUB
  }
}
```

**New receipt type:** `PROVIDER_FALLBACK` (logged to lane; not a failure, just a state change)

---

## Load Balancing Rules

### Token Preservation

- **Cheap work** (spikes, exploratory, feasibility): Always use cheapest tier (Luna + Haiku)
- **Judgment work** (design, review, arbitration): Use primary until ~80% exhausted, then rotate to fallback
- **Unblocking work** (high-priority bugs, critical path): Use primary or fallback; degrade if necessary

### Rotation Strategy

- **Weekly rotation** (Monday–Friday primary Codex, Friday–Monday primary Claude) to even out load
- **Threshold-based failover** (if primary > 80% exhausted, promote fallback to primary)
- **Account rotation detection** (on rotation, both providers reset; broaden usage back to dual-provider mode)

---

## Doctrine Contribution

**Core pattern: "Work-type multicast with role-specific provider affinity"**

```yaml
ProviderPool:
  roles:
    astra-design:
      primary: codex/astra
      fallback: claude/fable
      degraded: codex/luna
      rationale: "Pre-impl design; Astra and Fable both high-inference system architects"
    
    opus-review:
      primary: claude/opus
      fallback: codex/sol
      degraded: codex/luna
      rationale: "System review; both high-inference but different providers; Luna degrades quality"
    
    sonnet-review:
      primary: claude/sonnet
      fallback: codex/luna
      degraded: claude/haiku
      rationale: "Code review; Luna less specialized but available; Haiku cheapest"
  
  load_balancing:
    cheap_work:
      providers: [codex/luna, claude/haiku]
      rationale: "Always use cheapest for non-critical tasks"
    
    judgment_work:
      rotation_interval: "weekly"
      primary_until_exhaustion: 0.8
      rationale: "Rotate providers weekly; fallback at 80% to spread load"
  
  rotation_detection:
    method: "daily API health check (non-billable endpoint)"
    action: "on rotation, both providers reset; return to dual-provider mode"
```

---

## Implementation Effort

- **One-time:** Create `Invoke-ProviderPool.ps1` (~150 LOC)
- **Per-lane:** Wrap lane activation with `$provider = Get-PrimaryProvider; if (exhausted) { fallback }`
- **Minimal integration:** No lane topology change; no new files or governance; transparent to factory coordination

---

## Adoption Timeline

**Phase 1 (immediate):** Implement Provider Pool Abstraction in Adobe factory  
**Phase 2 (post-product ship):** Deploy to agent-bridge and other fleet projects  
**Phase 3 (future):** Register Grok and Kimi in pool; enable multi-provider rotation fleet-wide

---

## Future Extensions

- **Provider-specific prompt variants** (e.g., Grok requires different system prompt than Opus)
- **Cost tracking** (token spend per provider per lane; optimize for budget)
- **Capacity reservation** (reserve tokens for high-priority work; queue everything else)
- **Predictive failover** (if primary < 25% remaining, pre-activate fallback to avoid mid-review switch)
- **Multi-model comparison** (run same review on primary and fallback in parallel; compare results for quality benchmark)

---

## Ratification

This pattern is ready for adoption by any factory or multi-agent system that needs resilience across multiple providers.

**When to use:**
- Multiple providers with independent token pools available
- Graceful degradation is more important than optimal quality
- Account rotation or capacity exhaustion is anticipated

**When NOT to use:**
- Single provider (no failover available)
- All providers on the same billing account (no isolation benefit)
- Quality is non-negotiable (degraded tier unacceptable)
