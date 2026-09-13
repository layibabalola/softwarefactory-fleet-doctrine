# Machine Inventory Schema

**File:** `.claude/machine-inventory.yaml` (git-ignored, per-project)

Durable, per-machine inventory of available provider families and models. Used to dispatch the correct review posture.

## Schema

```yaml
project: <name>
managed_by: <owner-email>
last_verified: <ISO date>

providers:
  claude:
    models: [opus, sonnet, haiku, fable]
    available: true
    cli_path: claude
  codex:
    models: [sol, luna, astra]
    available: true
    cli_path: codex

machines:
  <machine-id>:
    providers: [claude, codex]  # list of available provider families
    agents_max: N              # concurrent agents safe on this machine
    can_spawn_background: bool
    primary_role: hub|scope|impl|verify|codex
    notes: "descriptive"

defaults:
  model_ordering: [claude, codex]     # dispatch preference
  family_preference: [claude, codex]  # fallback order
```

## Rules

- **Missing field:** Inherit fleet default (see `specs/posture-templates/conjugal-standard.yaml`)
- **Providers availability:** Mark `available: false` to disable a family (e.g., auth failure, quota exhausted)
- **agents_max:** Must be ≤ (host_cores / 2); prevents overload
- **primary_role:** Hints to dispatcher which agent types this machine should launch (e.g., hub for orchestrators, verify for checkers)

## Usage

When a review or design task needs to run:

1. Load `.claude/machine-inventory.yaml`
2. Check `providers[*].available`
3. If both Claude and Codex available: spawn Conjugal standard posture
4. If only Claude available: spawn Claude-only degraded posture
5. If only Codex available: spawn Codex-only degraded posture
6. If neither available: FAIL and report constraint violation

## Example (Cloudvore)

```yaml
project: cloudvore
managed_by: darktravellersinfo@gmail.com
last_verified: 2026-09-13

providers:
  claude:
    models: [opus, sonnet, haiku, fable]
    available: true
    cli_path: claude
  codex:
    models: [sol, luna, astra]
    available: true
    cli_path: codex

machines:
  dell-xps-17-primary:
    providers: [claude, codex]
    agents_max: 5
    can_spawn_background: true
    primary_role: hub
    notes: "Primary machine; both families available"

defaults:
  model_ordering: [claude, codex]
  family_preference: [claude, codex]
```
