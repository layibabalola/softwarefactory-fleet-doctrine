# Doctrine Export: Spec Adoption Pipeline

**Date:** 2026-09-12T16:30:00Z  
**Source:** Swarm-Designed Spec Discovery System  
**Authority:** Fleet consensus  
**Status:** SPECIFICATION (ready for implementation across projects)

---

## Problem

When new specs land in doctrine repo, projects don't discover them until manual announcement or periodic checks. Example: Conjugal publishes CLI credential rotation (v1.5) relevant to DropBox, DNG, Magic Lantern on UltraMagnus, but none of them know about it.

**Cost:** Manual coordination, delayed adoption, inconsistent fleet practices.

---

## Solution: Spec Adoption Pipeline

Automated discovery → filtering → integration → verification system that automatically discovers, evaluates, and adopts relevant specs across the fleet.

---

## Five-Part Architecture

### Part 1: Discovery Mechanism

**Session-Start Polling**
```python
# Every session start (or on-demand)
python coordination/spec-adoption/derive-fleet-specs.py \
  --doctrine-repo https://github.com/layibabalola/softwarefactory-fleet-doctrine \
  --local-adoption-index ~/.claude/adoption-index.json \
  --output /tmp/available-specs.json
```

**Git Webhook Notifications** (optional)
- Doctrine repo sends push notifications when specs are published
- Enables real-time discovery (not just session-start polling)
- Webhooks deliver to each project's comms inbox

**Metadata Discovery**
Each spec publishes metadata (`spec.json`):
```json
{
  "spec_id": "cli-credential-rotation-automation",
  "version": "1.5",
  "status": "BINDING",
  "domains": ["credential-sync", "cli-automation", "multi-project"],
  "applies_to": ["*"],
  "authority": ["Conjugal"],
  "requires_specs": [],
  "conflicts_with": [],
  "changelog": "Fixed multi-account parity handling"
}
```

### Part 2: Adoption Decision Logic

**Two-Filter System**

**Filter 1: Relevance Matching**
```python
spec_relevant = (
  (project.domains ∩ spec.domains) or
  (project.name in spec.applies_to) or
  (spec.applies_to == ["*"]) or
  (project_id in spec.subscriptions)
)
```

**Filter 2: Status-Based Routing**

| Status | Action | Use Case |
|--------|--------|----------|
| **BINDING** 🟢 | Auto-adopt immediately | Fleet-wide standard (CLI rotation) |
| **PROVISIONAL** 🟡 | Stage to temporary; await ratification | Under review (DNG's swarm variant) |
| **REFERENCE** 🔵 | Index in catalogue; manual opt-in only | Non-binding reference (Adobe pattern) |
| **EXPERIMENTAL** 🔴 | Ignore unless explicitly subscribed | Active exploration (research specs) |

### Part 3: Integration & Verification

**BINDING Specs: Mandatory Auto-Adopt**
1. Fetch spec files from doctrine repo
2. Validate checksum + semver compatibility
3. Merge into project tree (copy + configuration)
4. Run adoption test suite (verify spec works)
5. Commit adoption (record adoption version + checksum)

**PROVISIONAL Specs: Stage + Await Ratification**
1. Fetch spec to staging area (`~/.claude/adoption-staging/`)
2. Commit adoption ACK (record "staged for v1.1 adoption")
3. Notify lane owner (heartbeat message + comms inbox)
4. Auto-promote to applied tree when ratified to BINDING

**REFERENCE Specs: Catalogue Only**
1. Index in `adoption-index.json` (available-specs list)
2. Suggest in session heartbeat ("Consider adopting: pattern-xyz")
3. Manual opt-in via `adoption-subscribe` command

### Part 4: Continuous Updates & Versioning

**Patch/Minor Updates** (1.5 → 1.5.1, 1.5 → 1.6)
- Auto-apply via semver compatibility check
- No floor restart required; hot-load new version

**Major Updates** (1.5 → 2.0)
- Hold for manual opt-in (high-risk)
- Lane owner gets notification + decision window (30 days)
- Auto-downgrade after window if not approved

**Ratification Promotion** (PROVISIONAL → BINDING)
- PROVISIONAL specs auto-promote when doctrine marks BINDING
- Auto-adopt via Part 3 integration process
- Lane owner notified of promotion

**Rejection**
- Projects can opt-out via `adoption-subscribe --reject spec-id`
- Add to `specs.rejected` list (persisted, survives sessions)

### Part 5: Doctrine Guard Coordination

**Conflict Prevention Gates**

Adoption is HELD if any of these are true:
1. **File overlap** — Spec file path already exists outside spec system
2. **Semver incompatibility** — Spec requires newer framework version
3. **Authority clash** — Two BINDING specs from different authorities affect same system
4. **Mutual exclusivity** — Spec's `conflicts_with` list includes already-adopted spec
5. **Unmet dependencies** — Spec requires non-BINDING spec (PROVISIONAL not yet adopted)

**On Conflict**
1. Adoption held pending resolution
2. Lane owner notified with detailed guidance
3. Conflict resolved (manually or via doctrine guard)
4. Retry adoption on next session

---

## Real Example: Conjugal Publishes Credential-Sync v1.5

### Timeline

```
T=0:     Conjugal commits credential-sync v1.5 to doctrine repo
         Status: BINDING
         Domains: [credential, cli-automation]
         Applies_to: ["*"]

T=30s:   Git webhook publishes to all projects' comms inboxes
         Message: "New BINDING spec available: credential-sync v1.5"

T=1m:    DropBox session starts
         → derive-fleet-specs.py discovers credential-sync v1.5
         → Status filter: BINDING → auto-adopt
         → Doctrine guard: no conflicts
         → Integration: fetch + validate + merge + test + commit
         → Adoption index: marked "applied v1.5"
         → ✓ Ready to use

T=2m:    DNG session starts
         → Same discovery → auto-adoption
         → ✓ Ready to use

T=3m:    Magic Lantern session starts
         → Same discovery → auto-adoption
         → ✓ Ready to use
```

**No manual announcement, no coordination overhead.** All three projects adopt within minutes of publication.

---

## Implementation Checklist

### Phase 1: Infrastructure (Week 1)
- [ ] adoption-index.json (local tracking)
- [ ] adoption-config.yaml (subscriptions + rejections)
- [ ] adoption-staging/ directory
- [ ] Metadata spec.json template

### Phase 2: Discovery & Filtering (Weeks 2-3)
- [ ] derive-fleet-specs.py (polling + webhook handler)
- [ ] spec-matcher.py (relevance filtering)
- [ ] spec-status-filter.py (routing logic)
- [ ] Git webhook endpoint

### Phase 3: Integration Tools (Week 3)
- [ ] apply-binding-spec.py (fetch → merge → test → commit)
- [ ] stage-provisional-spec.py (staging logic)
- [ ] promote-provisional-spec.py (ratification promotion)
- [ ] adoption-test-suite (verify spec works)

### Phase 4: Doctrine Guard Gate (Week 4)
- [ ] doctrine-guard-gate.py (conflict prevention)
- [ ] Conflict logging + resolution guidance
- [ ] Escalation to lane owner

### Phase 5: Versioning (Week 4-5)
- [ ] check-spec-updates.py (detect new versions)
- [ ] semver-checking (compat logic)
- [ ] Deprecation warnings (30-day window)
- [ ] Manual pin override logic

### Phase 6: Heartbeat Integration (Week 5-6)
- [ ] Adoption status reporting
- [ ] Recommended actions (e.g., "adopt pending")
- [ ] Ratification notifications

### Phase 7: Testing & Rollout (Weeks 6-8)
- [ ] Test suite for all adoption scenarios
- [ ] Parallel deploy to DropBox, DNG, Magic Lantern
- [ ] Monitoring + alerting
- [ ] Rollback procedures

---

## Why This Design Works

1. **Automatic + Safe**: BINDING specs auto-adopt (no friction); doctrine guard blocks conflicts
2. **Ratification Path**: PROVISIONAL specs don't ship until blessed; projects can stage early
3. **Semver-Driven**: Patch/minor auto-flow; major breaks require explicit review
4. **Reversible**: Projects opt-out via rejection list; no forced upgrades
5. **Auditable**: Every adoption logged in adoption index with version, checksum, status
6. **Parallel**: All projects discover/adopt independently; no single point of failure
7. **Offline-Safe**: Cached specs work offline; batch sync on reconnect

---

## Success Metrics

- **Adoption latency**: New BINDING spec adopted by 90% of fleet within 1 session start
- **Conflict rate**: <1% of adoptions held due to conflicts
- **False positive rate**: <5% of filtered specs (relevance matching accuracy)
- **Automation rate**: 95% of adoptions are automated (no manual intervention)

---

## Related Specs

- `specs/doctrine-guard-conflict-prevention.md` — Conflict prevention on push
- `specs/spec-continuous-sync-for-floors.md` — Long-running session updates

---

## Revision History

- **2026-09-12 v1.0**: Initial specification (swarm-designed discovery/adoption pipeline)
