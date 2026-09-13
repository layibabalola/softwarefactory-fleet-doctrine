# Conjugal Standard Posture Template

**Status:** PROVEN. Delivered Approach A from 78.0 to 83.7 composite over 15 rounds.

**Requirement:** Both Claude and Codex families available (check `.claude/machine-inventory.yaml`).

## Standard Posture: Multi-Provider Cross-Family Review

When dispatching a design review or architecture audit on a machine with both families:

### Roles and Models

| Role | Model | Family | Count | Purpose |
|------|-------|--------|-------|---------|
| **Arbiter** | Astra | Codex | 1 | Arbitrate between Designer findings; pick winners |
| **Consolidator** | Fable | Claude | 1 | Weave winners into single coherent adjudication |
| **Designer-Scope** | Opus | Claude | 1 | Slice: architecture, claims, mutations (§0–§4 or equiv.) |
| **Designer-Verify** | Sol | Codex | 1 | Slice: verification, adoption, capacity (§3–§5 or equiv.) |
| **Lint-Consistency** | Haiku (Claude) + Luna (Codex) | Claude + Codex | 2 | Cross-family: find contradictions between sections |
| **Panel** | Mixed cheap models | 3 families | 8 seats | Blinded scoring on six dimensions (Timeline, Completeness, Safety, Autonomy, Throughput, Risk) |
| **Classifier** | Haiku swarm | Claude | N | Stopping evidence; predicted flat rounds accurately |

### Dispatch Pattern

1. **Designers run in parallel** (disjoint slices, different findings per slice)
2. **Lint runs cross-family** (each family finds what the other misses)
3. **Arbiter waits for Designers + Lint**, then picks winners
4. **Consolidator (spawned as chip)** receives arbitrated findings, weaves into final adjudication
5. **Panel scores** the finished design (optional; can be skipped for internal reviews)
6. **Classifier** provides stopping evidence

### Execution Model

**Designers + Lint:** Background agents (parallel, non-blocking)  
**Arbiter:** Background agent (waits for Designers + Lint, picks winners)  
**Consolidator:** Spawned as **chip** (separate task, own session) to weave findings into durably tracked adjudication  
**Panel:** Optional; if running, spawned as background agents or chips

### Fallbacks

**If only Claude available:**
- Designer-Scope (Opus) + Designer-Verify (Sonnet)
- Lint-Consistency (Haiku)
- No Arbiter (both families required)
- No cross-family validation badge

**If only Codex available:**
- Designer-Scope (Luna) + Designer-Verify (Sol)
- Lint-Consistency (Astra)
- No Arbiter (both families required)
- No cross-family validation badge

**If no auth for either family:**
- FAIL; do not downgrade or invent posture
- Report constraint violation and block review

## Key Properties

- **Disjoint slices:** Designers divide the spec; different winners per slice
- **Cross-family validation:** Lint-Consistency finds defects both families independently miss
- **Arbitration:** Arbiter picks one winner per defect class (no merges)
- **Consolidation:** Fable consolidator (singleton, long-context) weaves into one clean doc
- **Stopping rule:** After three flat rounds (Delta 0–2), hand off to next phase

## Integration with Dispatch Trigger

See `specs/dispatch-trigger-standard.md` for how to wire this posture into automatic agent spawning.
