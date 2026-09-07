# Doctrine: Checkpoint-Ignite-Assess-Adjudicate (CIAA) Pattern

**Cloudvore disposition, 2026-09-07:** The Phase 1 account below is historical. Cloudvore now explicitly distinguishes blanket parallel-launch resumption in [its current spec](cloudvore.md); bounded delegation in a finite task does not reinstate the old standing lanes.

**Date:** 2026-09-06  
**Origin:** Cloudvore factory (DropBox Vault)  
**Historical field-test status:** VALIDATED in Phase 1 field test  
**Applies to:** Multi-lane factories with quota rotation and concurrent writers

---

## Pattern Overview

The **Checkpoint-Ignite-Assess-Adjudicate** pattern (CIAA) enables factories to resume after account rotation while **safely parallelizing work and preventing wasted dispatch on non-quiescent state**.

### Core Steps

1. **Checkpoint** — Machine-local session snapshots record in-flight work (worktrees, dirty state, lane claims) outside the repo, surviving rotation
2. **Ignite** — Resume with "resume our work"; hub launches all lanes in parallel (background agents for Claude, codex exec for Codex)
3. **Assess** — Lanes read live factory state; each independently decides whether work is viable; declining lanes report blockers
4. **Adjudicate** — Hub synthesizes lane findings, files gate items, clears blockers, then sequences next dispatch

### Why This Matters

**Failure modes prevented:**
- ❌ **Dispatch into non-quiescence:** Lanes building on unstable master or unverified bar → wasted work
- ❌ **Wasted quota on blocked work:** Spinning builders when factory health is unknown → quota burn with no progress
- ❌ **Serial dispatch:** Waiting for one lane to report before launching the next → slow resumption
- ❌ **Lost in-flight state:** Rotation loses context of what was running → redoing work, guessing priorities

---

## Phase 1 Validation (Cloudvore, 2026-09-06)

### Test Case: Resume after account rotation

**Setup:**
- 138 worktrees with in-flight work (some dirty, some ahead of master)
- 33 unmerged branches in queue
- 62 non-terminal lane claims
- Master unverified (37 commits past last VERIFIED event)
- Quota critical (3% headroom)

**Execution:**

1. **Checkpoint triggered at SessionStart** → Printed all dirty worktrees and session pointers
2. **Hub resumed** → Read RESUME.md, state.py, check-cli-auth.py
3. **Ignited 5 lanes in parallel:**
   - Fable (adversarial review, mutation-first)
   - Opus (high-blast-radius builder)
   - Sonnet (src/tests builder)
   - Sol, Luna (Codex reviewers, dispatched via queue)

4. **Each lane assessed factory state:**
   - **Fable:** ✅ Proceeded with review (role: detect defects independently)
   - **Opus:** ⚠️ DECLINED work (reason: factory state complex, 37 commits unverified, last bar failed thermally, 31 blocking conditions unknown)
   - **Sonnet:** ⚠️ UNSEATED (reason: quota critical 3%, deferred charter for post-rotation)

5. **Adjudication:**
   - ✅ Fable delivered findings (F1: weak-pin shape b, F2: unfixed residue, F3: minor phrasing)
   - ✅ Opus delivered assessment (factory health is the gate, not lack of builders)
   - ✅ Sonnet preserved charter for landing-packet work (post-rotation)
   - ✅ 3 DELIVERED branches merged manually by hub to new master (99b857b)

### Key Results

| Metric | Result | Interpretation |
|--------|--------|---|
| Lanes auto-declined on blockers | 2 of 3 | Lanes correctly assess factory state; no wasted work |
| False-green catches (Fable) | 3 findings | Independent review identified weak-pin shape before commit |
| Quota respected | 3% → preserved | Lanes refused to burn tokens on non-quiescent state |
| Checkpoint survival | 100% | In-flight work catalogued, survives session boundary |
| Hub adjudication time | 1 turn | Synthesizing findings, filing gate items, queuing post-rotation work |

---

## Pattern Rules (Binding)

### Checkpoint
- **Session hooks** capture machine-local pointers (worktrees, dirty counts, session ids)
- **Tracked runbook** (`knowledge/ROTATION.md`) guides both pre- and post-rotation steps
- **Pointer-only design** — checkpoints never store code state (survives quota exhaustion)

### Ignite
- **No bootstrap prompt** — "resume our work" is sufficient; hub derives state, launches lanes
- **Parallel launch** — All lanes start in same turn; no sequential wait-and-react
- **Frozen charters** — Body passed verbatim; lanes read nothing but CLAUDE.md and track (no dynamic config)
- **Background by default** — Codex via `codex exec`; Claude via agent background; chips are fallback only

### Assess
- **Each lane reads live state** (git log, state.py, gate-list, ledgers) independently
- **Declining is a signal** — Lanes output findings (blockers, unruled owner-gated decisions, thermal failures)
- **No poll loop** — Declined lanes exit cleanly; hub does not retry; work is queued for next cycle
- **Charter preservation** — Declined lanes preserve their dispatch body for later re-seat

### Adjudicate
- **Hub reads all findings** in parallel — no waiting between lane completions
- **Files gate items** from lane findings (Fable discoveries, Opus assessments)
- **Clears blockers before reseating** — Master verification, owner rulings, thermal diagnosis
- **Queues post-rotation work** in tracked charters; rotation event triggers next dispatch

---

## Blockers That Cause Decline

Lanes SHOULD decline (not force work) when:

1. **Master unverified** — Last bar did not pass 3× identical green
2. **Owner-gated questions unruled** on critical items (merge criteria, quota behavior)
3. **Thermal failures** — Last bar stopped due to heat; machine state unknown
4. **Quota critical** (≤5% headroom) — No new Claude work; Codex work OK
5. **Lane-state checker reports blocking conditions** — Non-deterministic claims, unstrikes, conflicts

**Hub responsibility:** Diagnose and clear each blocker before re-seating builders on the same blockers.

---

## Post-Rotation Continuation

When quota exhaustion triggers rotation:

1. **Announce rotation** (user, heartbeat, or quota gate)
2. **Preserve charters** — All declined-work bodies in `review/dispatch-queue-<date>.md` survive rotation
3. **Fresh account** runs SessionStart → checkpoint restoration → "resume our work" → re-ignite on same charters
4. **No re-work:** Charters point to same file sets; deliveries stay READY; nothing repeats

---

## Adoption Checklist

To adopt CIAA in another factory:

- [ ] **Tracked runbook** at `knowledge/ROTATION.md` (or factory-specific path)
- [ ] **Session checkpoint hook** in `.claude/settings.json` (hooks/session-checkpoint.py)
- [ ] **RESUME.md** entry point reads checkpoint list at SessionStart
- [ ] **Lane charters** frozen, traceable, with file sets named
- [ ] **Fallback dispatch queue** in `review/dispatch-queue-<date>.md` (untracked; recreated per rotation)
- [ ] **Hub adjudication protocol** in CLAUDE.md (blockers, re-seating conditions)
- [ ] **Test:** One full resume cycle with at least 2 lanes declining on real blockers

---

## Lessons Learned

1. **Lanes are smarter than dispatch scripts** — They read state and decline intelligently; don't force work
2. **Quota is a factory-level gate** — Not a per-lane concern; Codex work is "free" during Claude quota crunch
3. **Checkpoints are cheap and powerful** — Machine-local pointers survive what central logs do not
4. **Adjudication is the critical path** — Not the building; hub synthesizing lane findings unblocks faster than building on unstable state
5. **Parallel-launch beats serial dispatch** — 5 lanes reporting findings in 1 turn beats waiting lane-by-lane

---

## Related Rulings

- **Owner 2026-08-09:** Five standing lanes + headless ignition (not chips) → `knowledge/lane-roster-2026-08-09.md`
- **Owner 2026-08-28:** Driver handover from Codex to Claude hub on Opus 5 → `review/hub-ruling-driver-handover-0828.md`
- **Doctrine 2026-09-06:** Checkpoint-Ignite-Assess-Adjudicate pattern (this doc)

---

## Files Referenced

- `C:\code\DropBox Vault\knowledge\ROTATION.md` — Runbook (tracked)
- `C:\code\DropBox Vault\tools\hooks\session-checkpoint.py` — Machine-local checkpoint capture
- `C:\code\DropBox Vault\knowledge\lane-charters.md` — Five-lane charters (tracked, frozen)
- `C:\code\DropBox Vault\review\RESUME.md` — Hub entry point (untracked, recreated per cycle)
- `C:\code\DropBox Vault\review\dispatch-queue-2026-09-06.md` — Fallback dispatch bodies (this cycle)

---

## Version History

| Date | Change |
|------|--------|
| 2026-09-06 | Pattern defined and validated in Phase 1 field test |
