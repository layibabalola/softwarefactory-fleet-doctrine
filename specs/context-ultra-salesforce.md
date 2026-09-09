# Context Ultra Safeguards: Grace-Period + TTL Model

## Overview

Context Ultra implements a three-layer safeguard system to prevent stale worktree accumulation, memory divergence, and documentation drift. This model is portable to other fleet projects (Bazel, Cargo, and custom build systems).

## Problem Statement

Parallel development sessions and worktree-per-branch workflows create three failure modes:

1. **Stale branches accumulate** → `git branch | wc -l` exceeds 50 within months
   - Impact: Fetch slowdown, UI confusion when picking branches
   - Root cause: Developers forget merged branches still exist locally

2. **Memory files diverge** → Two sessions read the same memory file, one updates it, the other proceeds with stale data
   - Impact: Lost decisions, duplicate work, conflicting claims
   - Root cause: Advisory lock files don't prevent concurrent writes

3. **Documentation drifts from code** → R-numbers committed without ROADMAP entries; new laws shipped without CLAUDE.md updates
   - Impact: Future developers don't know patterns exist; they re-invent or copy old code
   - Root cause: No gate enforcement

## What We Adopted (and Why)

**From Git:** Grace-period orphan detection (3d stale branch removal)
- ✅ DIRECTLY APPLICABLE: mtime-based detection for abandoned branches
- Implementation: Post-success build hook removes merged branches >7d old

**From GitHub Actions:** TTL-based auto-cleanup with configurable grace period
- ✅ PARTIALLY APPLICABLE: 4h active / 1h stale TTL for R-claim expiry
- Implementation: claim-r.ps1 tracks mtime; prune loop checks age

**Why we skipped:** Bazel (over-engineered action-key locking), Cargo (lock-file immutability masks conflicts), Kubernetes (single-machine doesn't need distributed leases)

## Critical Gap All Five Systems Miss

**None can distinguish "abandoned for 2 days" from "in-progress but quiet".**

- Bazel assumes determinism (doesn't match our mutable, human-claimed R-numbers)
- Cargo assumes immutability (masks write conflicts; we're collaborative)
- Git assumes orphan-detection is post-hoc (no heartbeat proof)
- GitHub Actions uses TTL but it's fire-and-forget (no feedback loop)
- Kubernetes uses TTL + renewal (overkill for single-machine)

**Our solution:** Add active-use heartbeat to claim-r.ps1 — lightweight mtime touch during build proves liveness.

## Phase 1: Adopt Now (Context Ultra)

### 1. Stale Branch Auto-Prune (Priority 1)
**Rule:** After successful `build.ps1`:
```powershell
# Remove branches merged to main AND >7d old
# Remove worktrees with stale lock files >7d old
# Log results to .git/prune-log.txt
```

**Safeguard:** Keep any branch with `.claude/keep-alive` metadata file

**Test:** Verify `git branch | wc -l` decreases after each green gate

**Status:** Triggers at >50 branches (currently 36, approaching threshold)

### 2. Memory File Versioning (Priority 2)
**Rule:** Every memory .md file gets:
```yaml
---
version: 2 (increment on structure change)
session_id: gracious-blackwell-2f77e5
modified: 2026-09-08T18:20:00Z
---
```

**Safeguard:** Advisory lock file `~/.claude/memory.lock` blocks concurrent writes

**Test:** Two sessions write resume-our-work simultaneously; second waits or warns

**Status:** Triggers on first divergence incident (already happened once)

### 3. ROADMAP Entry Validation Pin (Priority 3)
**Rule:** Selftest pin checks:
- Every R<N> in git log has a `## R<N>` entry in ROADMAP.md
- Every `## R<N>` entry has a date (not future-planned)

**Test:** Commit with R<N> but no entry; gate should fail

**Status:** Enforces existing CLAUDE.md law: "name revisions with definitions"

## Phase 2: If Scale Increases

- Claim expiry + liveness check (30 LOC)
- Law-closure audit pre-merge (60 LOC)
- Session heartbeat (50 LOC, optional)

## Integration with Existing Doctrine

These safeguards enforce existing CLAUDE.md laws:
- Stale-branch prune → "feedback-prune-worktrees" (automates manual task)
- Memory versioning → "volatile-state = pointer + date" (adds enforcement)
- ROADMAP validation → "name revisions with definitions" (gates on this)
- Law-closure audit → "post-block audits" (gates this too)

No new doctrine entries needed; these are implementations of existing laws.

## Known Limitations (Recorded Seams)

1. **Active-use heartbeat:** Not implemented yet. Claims can't prove "in-progress" vs "abandoned."
   - Mitigation: TTL is conservative (4h), false positives acceptable
   - Future: build.ps1 touches claim ref mtime during build

2. **Memory lock is advisory:** Two sessions CAN write simultaneously (lock file just warns).
   - Mitigation: Memory is advisory only; code stays correct even with stale data
   - Future: Real lock (filesystem exclusivity) if memory becomes authoritative

3. **Claim expiry clock-skew:** mtime-based pruning assumes monotonic clock.
   - Mitigation: Only run on single machine (user's clock is authoritative)
   - Future: If multi-machine, switch to git timestamp instead of filesystem mtime

## For Other Fleet Projects

**Applicability:**
- ✅ Single-machine builds with worktree-per-branch (Cargo, Bazel, custom)
- ✅ Teams using git branches + human R-number claims
- ⚠️ Distributed builds (add heartbeat + clock-skew handling)

**Minimum implementation:**
1. Stale branch prune hook (40 LOC)
2. Post-success cleanup in build script
3. Test: git branch count doesn't exceed threshold after green gate

**Optional enhancements:**
- Memory file versioning (if using shared mutable state)
- ROADMAP validation (if using R-number scheme)
- Law-closure audit (if documenting architectural decisions)
