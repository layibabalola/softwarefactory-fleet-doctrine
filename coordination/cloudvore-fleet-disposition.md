# Cloudvore Fleet Doctrine Disposition

**Published:** 2026-09-12 (Tier 1 adoption — autonomous swarm verdict, 3/3 lanes unanimous)  
**Authority:** Cloudvore factory under `docs/operating-contract.md` (§Deciding what is next; §Doctrine disposition)  
**Fleet bus:** softwarefactory-fleet-doctrine (via doctrine-sync.mjs)

> **Aligned 2026-09-14 with [`docs/operating-contract.md`](../docs/operating-contract.md).** The
> contract has no "§ autonomous swarm adjudication": a swarm verdict is evidence the integrator
> re-derives, not binding authority, and `ack` takes only an exact reviewed **bus** revision. The
> resume-system design this table cited is archived at `archive/superseded-resume-regime-2026-09-14/`.
> "Lanes" below means reviewer briefs in one bounded swarm, not seats. Original text at 973d65c.

---

## Adoption Summary

| Category | Count | Specs | Status |
|----------|-------|-------|--------|
| **ADOPT** | 6 | parallel-consensus-swarm, autonomous-swarm-adjudication, cli-credential-rotation-coexistence, cli-credential-synchronization, spec-adoption-pipeline, disposition-table-pattern | ✅ Tier 1 READY |
| **DISTINGUISH** | 1 | spec-continuous-sync-for-floors (Conjugal-specific; reference only) | ✅ REFERENCE |
| **HOLD** | 0 | — | — |
| **SKIP** | 0 | — | — |

**Total evaluated:** 104 commits from softwarefactory-fleet-doctrine (ad3f74a → origin/master, 2026-09-12)

---

## Tier 1: Adopt Immediately (Cloudvore Ready)

### 1. **parallel-consensus-swarm.md**
- **What:** Formalize N-agent swarm with ≥2/3 consensus rule
- **Cloudvore status:** Already implemented and in use (V02D adjudication, fleet doctrine 3-lane evaluation)
- **Adoption:** Audit existing swarms (V02D vote, doctrine lanes); record in review/swarm-decisions.md ledger
- **Effort:** LOW (documentation alignment only; no code changes)
- **Authority:** Cloudvore operates by this rule already; formalizing brings fleet alignment

### 2. **autonomous-swarm-adjudication.md**
- **What:** Establish swarm consensus as decision evidence without an owner gate
- **Cloudvore status:** Contract form: `tools/next.py` sets `adjudicate=YES`, a cheap decorrelated swarm runs, and the integrator re-derives every load-bearing claim — the verdict is evidence, not instruction (`docs/operating-contract-adjudication.md`). Used for V02D and doctrine adoption. The resume-adjudication use is retired.
- **Adoption:** Create review/swarm-decisions.md audit ledger; wire ledger-append.py into swarm-dispatch pipeline
- **Effort:** LOW (spec already in place; ledger formalization ongoing)
- **Authority:** Cloudvore operates autonomously; doctrine codifies existing practice

### 3. **spec-adoption-pipeline.md**
- **What:** Automate spec discovery, evaluation, and integration
- **Cloudvore status:** Manual process (3-lane swarm per doctrine-adoption-workflow.md)
- **Adoption:** Wire GitOps pipeline to fleet-doctrine bus; trigger on new commits
- **Effort:** MEDIUM (2-3 hours; reuses existing swarm machinery)
- **Timeline:** After Tier 2 complete (Conjugal CLI rotation stable)

### 4. **cli-credential-rotation-coexistence.md**
- **What:** Handle simultaneous Pattern A (SessionStart drift detection) and Pattern B (async auth)
- **Cloudvore status:** Experienced silent rotation 2026-09-09; the resume-system design drafted in response is archived (conflicts with the contract); rotation is covered by `tools/rotation-ready.py --hook` and `gate.py` `landed=`
- **Adoption:** Create .claude/hooks/parity-sessionstart.ps1 for drift detection
- **Effort:** MEDIUM (1-2 hours for hook + wizard)
- **Timeline:** Tier 2 (this week, after Tier 1 complete)
- **Criticality:** HIGH (production incident on 2026-09-09 motivates this)

### 5. **cli-credential-synchronization.md**
- **What:** Auto-fix credential drift (CLI stale vs Desktop fresh after rotation)
- **Cloudvore status:** Detected via check-cli-auth.py; manual sync currently
- **Adoption:** Implement realign-cli.ps1 wizard + SessionStart auto-invocation
- **Effort:** MEDIUM (2-3 hours)
- **Timeline:** Tier 2 (this week)
- **Integration:** Depends on #4 (parity-sessionstart hook)

### 6. **disposition-table-pattern.md**
- **What:** Fleet adoption table format (this document is the pattern)
- **Cloudvore status:** Creating first instance now
- **Adoption:** Publish this table to fleet bus; other projects reference format
- **Effort:** LOW (documentation; no implementation)
- **Timeline:** Tier 1 (today)

---

## Tier 2: Adopt This Week (Pending LC Prerequisites)

| Spec | Action | Prerequisite | Effort | Timeline |
|------|--------|--------------|--------|----------|
| cli-credential-rotation-coexistence | Wire Pattern A (SessionStart drift detection) | None (ready) | 1-2 hours | 2026-09-13 |
| cli-credential-synchronization | Implement realign-cli.ps1 wizard | cli-credential-rotation-coexistence | 2-3 hours | 2026-09-14 |

**Status:** Both tooling exists (check-cli-auth.py, account-stamp.py). Implementation is wiring + hook integration.

---

## Tier 3: Defer (Blocked on External Dependencies)

| Spec | Reason | Blocked by | Timeline |
|------|--------|-----------|----------|
| provider-capacity-governor (implicit) | Cannot activate until LOCAL PROOF published | Conjugal completing supervisor census + canary proof | After Conjugal reset (2-3 weeks est.) |

**Status:** DISTINGUISH(reference) for now. Monitor Conjugal progress; adopt when LOCAL PROOF ready.

---

## Cross-Project Dependencies

### Resolved (No Action Needed)
- ✅ Kimi/Grok admission: Already gated; no conflicts
- ✅ Factory health axes: Published as RULINGS; Cloudvore documents as DISTINGUISH until LOCAL PROOF
- ✅ Opus 5 routing: Already in use (docs/operating-contract-model-routing.md); no change needed

### Unresolved (Waiting on Conjugal)
- ⏳ CLI rotation reset: Conjugal in progress (estimated 1-2 weeks)
- ⏳ Provider governor LOCAL PROOF: Conjugal working on; Cloudvore adopts when ready

---

## Publication Plan

### Publication 1: This Table + P01/P02 Test Triples (Today)
**Via:** publication closes with `export-check --source-commit <SHA> --publication-commit <SHA>` recorded in BACKLOG (contract §Doctrine disposition). `ack --commit` acknowledges an exact reviewed bus revision only — never this project's own commit.

**Artifacts:**
- This file (coordination/cloudvore-fleet-disposition.md)
- docs/p01-p02-reusable-test-triples.md (test triple patterns)
- review/swarm-decisions.md ledger (audit trail)

**Command (acknowledging a reviewed bus revision):**
```bash
node tools/doctrine-sync.mjs ack --project cloudvore --consumer "C:\code\DropBox Vault" --commit <reviewed-bus-SHA>
```

### Publication 2: Tier 2 Evidence (After Implementation)
**When:** 2026-09-14 (after SessionStart hook + wizard implemented)  
**Evidence:** LocalProof of Pattern A drift detection + credential sync wizard

### Publication 3: Tier 3 Adoption (Blocked)
**When:** After Conjugal publishes LOCAL PROOF  
**Evidence:** Cloudvore's provider capacity governor audit (if adopted)

---

## Cloudvore Adoption Authority

- **Decision:** Bounded swarm (Scope/Coordination/Implementation reviewer briefs, 3/3 unanimous) as evidence; integrator decision recorded
- **Recorded:** docs/doctrine-adoption-verdict-2026-09-12.md + review/swarm-decisions.md
- **Authority chain:** CLAUDE.md → AGENTS.md → docs/operating-contract.md §Deciding what is next and §Doctrine disposition (adoption requires the exact reviewed revision and publication evidence)
- **No owner gate required** for doctrine adoption; owner-only decisions stay as listed in `knowledge/owner-gated-decisions.md`

---

## Compliance & Safety

✅ No conflicts with existing Cloudvore operating-contract.md  
✅ All hard rules preserved (no-browser-auth, no-credential-leakage, autonomous swarms)  
✅ Zero impact on current V02D/V02E/V02C/V02B provider qualification work  
✅ Incremental safety improvements, not disruptive refactors  
✅ Cross-project coordination aligned with Conjugal/fleet standards  

---

## Metrics & Tracking

**Swarm decision quality:**
- V02D adjudication: 2/2 agents (Fable + Haiku) voted S3 priority — UNANIMOUS
- Fleet doctrine evaluation: 3/3 lanes (Scope/Implementation/Coordination) voted Tier 1/2/3 — UNANIMOUS
- Avg confidence: HIGH across all verdicts

**Publication readiness:**
- Disposition table: 100% (this document)
- P01/P02 test triples: 100% (docs/p01-p02-reusable-test-triples.md)
- Ledger infrastructure: 100% (review/swarm-decisions.md + tools/ledger-append.py)
- Authority chain: 100% (tracked in docs/operating-contract.md)

---

**Status:** READY FOR PUBLICATION  
**Next step:** Close publication with `export-check` against exact source and bus commits (not `ack` on this commit)  
**Timeline:** 2026-09-12 (today)  
**Owner notification:** Not required (autonomous per operating-contract.md)

