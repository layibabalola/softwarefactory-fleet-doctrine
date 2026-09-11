# Phased Concurrent Review Pattern

**Authority:** Adobe Document Cloud Ingester factory, Q-034 rev4 ratification  
**Status:** WORKING STRATEGY, tested 2026-09-11  
**Evidence root:** `.factory/coordination/HUB.md` seq 2026-09-11T06:45:00Z onwards

---

## Problem

**Naive concurrent review** (two reviewers on the same work product simultaneously) fails when:
- Both reviewers consume shared resource (token pool, rate limit)
- Both must publish signals within microseconds (timing windows for publication order)
- Both readers of the same frozen snapshot can see torn state during concurrent reads

**Attempted solution (Q-034 rev3):** Opus and Sonnet vote simultaneously on the same candidate.  
**Outcome:** PROVIDER_NONZERO on both; both ballot slots burned; no votes published; factory stalled.

---

## Solution: Phased Review by Work Product

**Core idea:** Don't make reviewers concurrent on the same work product. Phase them by work product instead.

### Review Tiers

| Tier | Reviewer | Work Product | Role | Venue | Execution |
|------|----------|--------------|------|-------|-----------|
| **1** | Astra (super-high-inference) | **Proposal** (design/spec before implementation) | Pre-implementation hostile design pass | Codex Desktop | Execution before Luna codes |
| **2a** | Opus (high-inference) | **Candidate** (code after implementation) | System/architecture review | Claude CLI | Parallel with Sonnet; independent ballots |
| **2b** | Sonnet (high-inference) | **Candidate** (code after implementation) | Code/security review | Claude CLI | Parallel with Opus; independent ballots |
| **3** | Sol (orchestrator) | **Ballot + Evidence** | Synthesize design issues (Astra advisory) + implementation votes (Opus/Sonnet) | Codex Desktop | After both final reviews published |

### Collision Elimination

**Q-034 rev3 collision (same work product, simultaneous):**
```
T=0: Both Opus and Sonnet wake
T=1: Both try to read frozen snapshot
T=2: Both hit token pool — PROVIDER_NONZERO on both
T=3: Both ballot slots consumed; no votes published
Result: BLOCKED
```

**Phased pattern (different work products, sequential):**
```
T=0:   Astra wakes, reads proposal (design document)
T=1:   Astra publishes design findings (advisory signal)
T=2:   Luna starts implementation
T=3:   Luna publishes candidate (code + tests)
T=4:   Opus wakes, reads candidate (same work product as Sonnet)
T=5:   Sonnet wakes, reads candidate (same work product as Opus)
T=6:   Both read same frozen candidate; no collision (independent tokens + separate ballots)
T=7:   Opus publishes vote + report
T=8:   Sonnet publishes vote + report
T=9:   Sol adjudicates both + Astra advisory findings
Result: UNBLOCKED
```

**Key property:** Astra and final reviewers never compete for the same resource. Opus and Sonnet vote on candidate concurrently (if desired) but on a separate work product from Astra, eliminating the token-pool race.

---

## Ballot Semantics

### Quorum

**Veto-capable lanes (must APPROVE for execution):**
- Sol (orchestrator)
- Opus (system reviewer)
- Sonnet (code reviewer)

**Advisory lanes (inform decision, do not block):**
- Astra (pre-impl design pass)
- Luna (implementer; READY gates transition, not outcome)

**Execution criterion:** Sol + Opus + Sonnet all APPROVE.  
**Advisory influence:** Astra's design findings inform Luna's implementation spec and Sol's adjudication, but are not veto votes.

### Signal Publication

| Lane | Signal | Format | Timing |
|------|--------|--------|--------|
| **Astra** | `DESIGN_REVIEW` | Advisory report + risk findings | Before implementation |
| **Luna** | `IMPLEMENTATION_READY` | Commit hash + evidence root | After code + tests pass |
| **Opus** | `VOTE` | APPROVE/REJECT + system report | After candidate review |
| **Sonnet** | `VOTE` | APPROVE/REJECT + code report | After candidate review |
| **Sol** | `DISPOSITION` | Synthesis + execution gate | After all votes published |

---

## Evidence Structure

```
.factory/evidence/WO-{id}/
├── astra/
│   ├── design-review.md          # Pre-impl findings
│   └── evidence/
│       ├── proposal-sha256.txt
│       └── risk-assessment.md
├── luna/
│   ├── implementation/
│   │   ├── feature-branch commits
│   │   └── test results
│   └── implementation-ready.md    # Signal: ready for review
├── opus/
│   ├── system-review.md           # Opus report
│   └── evidence/
│       ├── candidate-sha256.txt
│       └── architecture-analysis.md
├── sonnet/
│   ├── code-review.md             # Sonnet report
│   └── evidence/
│       ├── candidate-sha256.txt
│       └── test-coverage-report.md
└── sol/
    ├── disposition.md             # Final adjudication
    └── release-gate-closed.txt    # Execution decision
```

---

## Properties Preserved

- **Independence:** Opus and Sonnet do not see each other's reports before publishing
- **Immutability:** Candidate frozen during both Opus and Sonnet review
- **Single-writer:** Luna owns implementation; Sol owns ledger; each lane owns its report
- **Determinism:** Frozen snapshot + redaction rules guarantee same view to all reviewers
- **Auditability:** Every signal and report SHA-256-pinned in ledger

---

## Trade-offs

| Trade-off | Cost | Benefit |
|-----------|------|---------|
| **Sequencing overhead** | Astra runs before Luna; adds 1–2h wall-clock | Catches design faults before implementation; reduces rework |
| **Two work products** | Maintain both proposal and candidate evidence | Clear separation of concerns; simpler redaction rules |
| **Advisory tier** | Astra findings don't veto, only inform | Simpler quorum math; keeps design pass lightweight |

---

## Ratification

This pattern is ratified in the Adobe factory and ready for adoption by other projects.

**When to use:**
- Multi-reviewer concurrent validation where reviewers compete for shared resources
- Pre-implementation design feedback is valuable (catches faults early)
- Reviewers can have different roles (hostile design + system review + code review)

**When NOT to use:**
- Single reviewer per role (no concurrency benefit)
- Pre-impl feedback not valuable (fast-moving iterations, prototypes)
- All reviewers are on the same provider (no token-pool collision risk)

---

## Future Refinements

- **Load shedding:** If Astra unavailable (Codex exhausted), fallback to Fable pre-impl pass
- **Reviewer fallback:** If Opus unavailable, Sonnet can do both system + code (degraded quality)
- **Batch reviews:** Process multiple proposals/candidates in a pipeline (currently one WO at a time)

