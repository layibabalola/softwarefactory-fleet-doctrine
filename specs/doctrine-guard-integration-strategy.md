# Doctrine Guard Integration Strategy

**Date:** 2026-09-12  
**Assessment Status:** SWARM VERDICT PENDING  
**Authority:** DNG + Fleet Consensus  
**Scope:** Fleet-wide deployment readiness for automated doctrine repo conflict prevention

---

## Overview

Doctrine Guard is an automated system that intercepts doctrine repo pushes, detects conflicts via a 3-layer algorithm, runs swarm-based reconciliation when needed, and auto-resolves safe changes. It prevents naming collisions, scope overlaps, and verdict contradictions from propagating to fleet doctrine.

**Source:** Discovered in `specs/doctrine-guard-conflict-prevention.md` (authored by Conjugal; ratified 2026-09-12)

---

## Problem Solved

When multiple projects push doctrine specs around the same time:
- Naming collisions (same concept, different names) go undetected
- Scope overlaps (specs claiming authority over same domain) cause downstream confusion
- Verdict contradictions propagate to fleet

**Real example:** Conjugal pushed `autonomous-decision-making-with-adversarial-swarms.md`; DNG pushed `autonomous-swarm-adjudication.md` 19 minutes later. Both valid, but overlapping terminology required manual post-push audit.

---

## Current State

### Spec Completeness
**Status:** ✅ COMPLETE

The Doctrine Guard spec fully defines:
- ✅ 3-layer conflict detection algorithm (name collision, scope overlap, verdict contradiction)
- ✅ Swarm-based reconciliation (4-6 agents with defined roles)
- ✅ Consensus rules (≥3/4 agents must agree)
- ✅ Verdict types (MERGE, RENAME, COEXIST, DEFER, REJECT)
- ✅ User intent specification (propose, validate, explore-alternative, parallel-research)
- ✅ Reconciliation artifact generation (audit trail commits)
- ✅ Implementation architecture (pre-push hook + Python scripts)

**Files:**
- Main spec: `specs/doctrine-guard-conflict-prevention.md`
- Index: `coordination/doctrine-guard/doctrine-index.json` (7 specs catalogued)

### Implementation Status
**Status:** ⚠️ SPEC ONLY (scripts not yet written)

Missing files (referenced in spec, not yet implemented):
- `coordination/doctrine-guard/detect-conflicts.py` — 3-layer detection logic
- `coordination/doctrine-guard/reconcile-swarm.py` — Orchestrate 4-6 agents, consensus logic
- `coordination/doctrine-guard/git-pre-push-hook.sh` — Main hook entry point
- `coordination/doctrine-guard/settings.json` — Config (thresholds, timeouts)
- `coordination/doctrine-guard/prompts/*.md` — Agent role prompts (6 files)

---

## Swarm Assessment Results

**Assessment launched:** 2026-09-12 12:XX UTC  
**Lanes:**
1. ✅ Spec Completeness Analyst — COMPLETE
2. ✅ Algorithm Soundness Reviewer — COMPLETE  
3. ✅ Integration Readiness Assessor — COMPLETE

### Consensus Verdict: **YELLOW (IMPLEMENT WITH REMEDIATION)**

#### Lane 1: Spec Completeness (Verdict: COMPLETE SPEC, ZERO IMPLEMENTATION)
✅ Architecture is sound and ready for development  
✅ All algorithmic pieces defined (3-layer detection, swarm roles, verdicts)  
✅ User intent specification complete  
❌ **Critical gap:** All 8 implementation files missing (only doctrine-index.json exists)
- detect-conflicts.py ✗
- reconcile-swarm.py ✗
- git-pre-push-hook.sh ✗
- settings.json ✗
- 6 prompt files ✗

**Recommendation:** Spec is ready; develop implementation immediately.

#### Lane 2: Algorithm Soundness (Verdict: HAS_GAPS, MEDIUM-HIGH RISK)
✅ Layers 1–3 conceptually valid  
⚠️ **Medium-risk gaps:**
1. **Layer 1 brittleness:** Same ID requires byte-identical content; no versioning path for spec evolution
2. **Layer 2 vagueness:** Scope-overlap detection uses informal set intersection; "overlapping subjects" undefined
3. **Layer 3 incomplete:** Authority-weight calibration rules absent; how weights resolve conflicts not specified
4. **Empty/null specs:** Bypass all checks (no validation)
5. **Intent tags too loose:** Users can suppress genuine conflicts via `explore-alternative` tag without explicit ratification

**Recommendation:** Formalize before deployment—add scope intersection thresholds, authority ledger, explicit ratification gates (not tags).

#### Lane 3: Integration Readiness (Verdict: NEEDS_WORK — Implementation Gap Identified)
❌ **Blocking deployment:**
- 5 critical scripts missing (detect-conflicts.py, reconcile-swarm.py, git-pre-push-hook.sh, settings.json, build-index.py)
- 6 agent role prompts not yet written
- No pilot testing data; false-positive rates unknown
- No settings.json tuning (scope-overlap thresholds, timeout values)

✅ **Ready to proceed with Phase 1:**
- Implementation effort: 4–6 hours
- Primary integration point: Local pre-push hook (`.git/hooks/pre-push`)
- Fallback: Server-side pre-receive hook
- Key risks identified: false positives (mitigated via keyword filtering + intent tags), swarm deadlock (40-min timeout), hook bypass (server-side fallback), cascading swarms (queue serialization)

**Critical Path:**
1. Complete Phase 1 implementation (code + prompts)
2. Dry-run test on doctrine repo with synthetic conflicts
3. Pilot with 3–5 volunteers for 2 weeks (tuning scope-overlap thresholds)
4. Measure false positive rate; adjust settings.json
5. Deploy to mandatory when confidence threshold met (≥3/4 agreement swarm verdicts align with manual audit)

**Timeline:**
- Phase 1 (Implementation): 4–6 hours (parallel with algorithm refinement)
- Phase 2 (Pilot + tuning): 2–3 weeks  
- Phase 3 (Fleet deployment): Week 4+ (confidence-driven, not calendar-driven)

---

## Integration Plan

### Phase 1: Implementation (Pre-Deployment)
1. Write Python scripts (detect-conflicts.py, reconcile-swarm.py)
2. Create settings.json config file (thresholds: scope-overlap %, verdict-contradiction sensitivity)
3. Write agent role prompts (6 files: novelty, quality, scope, authority, synthesis, risk)
4. Test hook locally (dry-run via `git push --dry-run`)
5. Verify swarm spawning and consensus logic

**Effort:** 4-6 hours (1-2 developers)  
**Risk:** Low (isolated to doctrine repo; doesn't affect product code)

### Phase 2: Rollout (With Safeguards)
1. Deploy hook to doctrine repo `.git/hooks/pre-push`
2. Test with intentional conflicts (dry-run + live)
3. Monitor for false positives (scope-overlap sensitivity may need tuning)
4. Enable on-demand for volunteers (opt-in per project)
5. Flip to mandatory after 2 weeks confidence

**Rollout timeline:** 2-3 weeks (confidence-driven, not calendar-driven)

### Phase 3: Feedback & Refinement
- Tune conflict detection thresholds based on false positive rate
- Gather feedback on swarm verdict quality
- Document common verdicts and patterns for fleet teams
- Extend to other shared repos (if applicable)

---

## Deployment Checklist

- [ ] Python scripts implemented and unit-tested
- [ ] Agent prompts reviewed by 2+ experienced Haiku sessions
- [ ] Dry-run test on doctrine repo with synthetic conflicts
- [ ] settings.json tuned (scope-overlap sensitivity, timeout thresholds)
- [ ] Hook installed and chmod +x
- [ ] 3-5 volunteers opt-in for week 1
- [ ] Swarm verdict audits logged for quality feedback
- [ ] Deploy to mandatory after 2-week pilot confidence threshold

---

## Risks & Mitigations

| Risk | Severity | Mitigation |
|------|----------|-----------|
| False positive on harmless overlap | MEDIUM | Keyword-only filtering + intent tags; user override available |
| Swarm consensus deadlock | LOW | Escalate to owner; 40-min timeout with audit trail |
| Performance: swarm spawn latency | LOW | Async swarm; user can push with `--force-doctrine-push` |
| Hook bypass (e.g., `git push --force`) | MEDIUM | Server-side pre-receive fallback hook |
| Cascading swarms (push while swarm runs) | LOW | Queue incoming pushes; serialize pre-push analysis |

---

## Success Criteria

✅ **Week 1:** No naming collisions missed; <5% false positives  
✅ **Week 2:** Swarm verdicts align with manual audits; 0 escalations  
✅ **Week 3:** Deploy to mandatory; all projects opt-in without complaints  
✅ **Week 4:** Document patterns; recommend to other shared repos

---

## Authority & Next Steps

**Ratified:** Doctrine Guard spec (Conjugal design, fleet consensus 2026-09-12)  
**Pending:** Implementation + pilot deployment  
**Owner:** DNG + volunteer implementer  
**Review cycle:** Daily swarm audit during week 1; weekly thereafter

---

## References

- Spec: `specs/doctrine-guard-conflict-prevention.md`
- Parallel Consensus Swarms: `specs/parallel-consensus-swarm.md`
- Autonomous Adjudication: `specs/autonomous-swarm-adjudication.md`
- Index: `coordination/doctrine-guard/doctrine-index.json`

---

**Status:** READY FOR IMPLEMENTATION  
**Swarm Verdict:** YELLOW (3/3 lanes agree: spec complete, implementation needed, algorithm gaps require refinement before deployment)  
**Authority:** DNG + Fleet (via 3-lane consensus swarm)  
**Next:** Phase 1 implementation (4–6 hours); parallel algorithm refinement

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
