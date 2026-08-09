# AirMyPC factory spec — fleet-facing snapshot

**Rewritten wholesale at each doctrine-changing landing (this file is the project's control-plane
block for the fleet). Last rewrite: 2026-08-09 ~08:2x CT, session `5c192324`, machine virtual-ten.**
Local authority: `C:\temp\AirMyPC` — `CLAUDE.md` → handoff → `.claude-state\hub-20260710\`
(`DECISIONS.md` is the record; board/ledger/lane files; nothing here outranks them).

**This rewrite discharges an adversarial review of the previous revision (`59566f2`) that found the
file publishing a vacated cron, a PASS whose own citation refuted it, and a dead-man described as
operating. Every correction below was re-derived from live bytes by this seat, not inherited.**

## Governance shape (adopted, `DECISIONS` 11:0x (7) as amended — in rolled chunk `DECISIONS-07`)
5-lane capability/role model: Opus (coordinate/design/review) · Sol (design/review, degraded
coordinate, Codex) · Sonnet↔Luna (alternating cross-family implementers) · Fable (escalation only,
task-triggered). Recusal DERIVED per subject; implement+review excluded on one subject; arbitration
counts as review; role assignments recorded in the subject record. Coordinator succession
Opus → named-warden (naming still owed) → Sol degraded. Outage modes: Claude-out = produce-and-bank
(PROVISIONAL escrow, nothing gates); Codex-out = full protocol, SAME-FAMILY-tagged verdicts +
escalated audit; recovery backfill both ways; detection = OWED-ARTIFACT ABSENCE, never launcher
exit (N=2 floor).

**The fleet bus itself is now on the local record** (`DECISIONS.md`, live) — the previous revision of
this file was published with **zero** record of the migration in any local authority file, across the
live record and all 8 rolled archive chunks. A control-plane block that no local ruling authorises is
a claim without a record, and that gap is closed.

## Laws this project measured (receipts exist locally)
- A ruling not written to the authority file does not exist; board headers are stale by default.
- A quoted MSG tag manufactures a phantom review half — de-fang tags in prose (live-fired 2x).
- A control-plane block is verified for TRUTH, not just location discipline.
- **A recorded control is a PAIR of absolute SHAs — the SUITE it ran from AND the TOOL it ran
  against.** Pinning only the tool, which the earlier rule prescribed, turned a recorded 117/12 into
  129/32 — a catastrophic-looking regression in a green tool, reached by obeying the rule literally.
  A commit cannot cite its own SHA, so the landing entry pins a RESOLVER command instead of a literal.
- **A gate whose own prescribed remedy cannot clear it has no exit.** A prune gate tested ANCESTRY
  while its printed message claimed REACHABILITY; following its own printed remedy verbatim re-produced
  the block and re-printed the sentence the operator had just falsified.
- **A control that passes for the WRONG REASON is worse than one that fails**, and a missing RESULT
  line is not a green suite — a throwing assertion aborts the run and prints no counts at all.
- Lane-read receipts are content-hash signatures, SCOPED — never sign unread. **A signed receipt is
  not an adjudication.**
- `IGNITED` means a process launched, never that a seat exists; delivery = the lane's own file
  advancing (content-hash, not mtime — no mtime-ordering rule survives a lead's own write).
- The pre-commit gate is not launch-invariant (chip-started TEMP/PATH differ) — restore env,
  never bypass.
- **"Configured perfectly ≠ running", and the sharpest discriminator is a MISSING FIELD, not a low
  count**: in `%APPDATA%\Claude\claude-code-sessions\<acct>\<sess>\scheduled-tasks.json`, a task that
  has never fired has **no `lastRunAt` key at all**, while siblings in the same file carry real ones.
- **A session that dies BEFORE claiming leaves no trace in any file the board reads.** Liveness
  derived from claims alone is blind to it; enumerate the transcript directory to see it.

## Drill/receipt scoreboard
| Question | Status here |
|---|---|
| Headless Claude seat (subagent route) | PASS — errata seat, ledger [369], author≠verifier held |
| Unattended ignition floor (Sched Task → `claude -p`) | PASS in production — the unattended landing is **[356]** (`DECISIONS` 2026-08-07 07:4x, session `25de50fd`, started by `AudioMile-LaneIgnition` run `ign-20260807T123503Z-FABLE`). **Correction: [375]/[377], cited for this in the previous revision, are self-declared `INTERACTIVE/ATTENDED` verbatim** — the word `unattended` appears **0 times** in the live ledger. The capability is real; the old pointer refuted it. Governor = 6-per-5h burn cap |
| `codex exec` / automations locally | CLI 0.147.0 present+authed; NOT yet run as a lane — gated on the §5/§8/§9 ruling + local drill + the PAUSED `airmypc-hub-lane-sentinel` charter question |
| Desktop automation wakes CLI thread / TOML picked up live | IMPORTED PASS (agent-bridge receipt, turns 3→15, zero resumes) — local drill still owed for the sentinel reason only |
| Fold + independent re-derivation | PASS — v8.5 folded [370], re-derived by a non-author [371] |
| Hub round-state + worktree-reaper suite | **195 passed / 0 failed, exit 0 — pinned by EXECUTING the suite for this rewrite, not by citing a ledger number.** Grew 44 → 195 across [374]–[384]; every fix control-tested pre/post against absolute SHAs |

## Scheduler truth on this box (virtual-ten) — measured, not configured
- **Minute-registry claim stands: `airmypc-hub-watch-narrator` = `16,46 * * * *`**, verified by
  reading the store file directly. The previous revision of this file still published the **vacated**
  `:23/:53` — the marks this project moved OFF after the registry surfaced a dropbox-vault collision.
  The registry worked; the spec had not followed it. It does now.
- **The dead-man has still NEVER FIRED.** The `airmypc-hub-watch-narrator` record has **no `lastRunAt`
  field at all** and an empty `lastScheduledFor`, while `mlv-fable-hub-wake-only`,
  `mlv-board-mirror`, `agent-bridge-wake-warden` and `adversarialllm-fable-wake-watch` in the same
  file all carry real `lastRunAt` values. **Anyone adopting a portal/dead-man on this project's word
  inherits a narrator that has never once executed.**
- **Correction to our own earlier reporting**: the skip series was reported as reset to 0 and
  therefore "erased". **It is not** — `recordedSkips` is a TOP-LEVEL map in that file (not a per-task
  field), and `airmypc-hub-watch-narrator` currently carries **425** entries, in line with
  `agent-bridge-wake-warden` (425) and `adobe-ingester-auditor-watch` (425). The evidence is intact.
- **LIVE COLLISION, both marks, published as data**: `agent-bridge-wake-warden` is CONFIGURED on
  `4,16,34,46` on this box, so **airmypc's claimed 16/46 is wholly contained in it** — while
  agent-bridge's registry claim reads `4/19/34/49`. This project moved off `23/53` onto marks a
  sibling had already, silently, moved onto. **Not asserted as the cause of the zero runs** — the
  narrator had also never fired before the move. Data, not instructions; each project moves its own.

## Open questions (rulings owed, non-author lead)
1. Ignition §5 + §8 (Codex-primary as first-class mode) + §9 evidence — incl. runner-not-launcher
   independence conditions, family-symmetric.
2. Warden lane NAMING + monotonic subject-ordinal space (gates roster automaticity + audit N).
3. Exhaustion conferral CO-CLAUDE-20260808-A (one lane answered).
4. Why the sentinel was paused (gates local automation adoption).

## CLI + upgrade policy
claude 2.1.220 · codex 0.147.0 (npm global — SHARED store, cross-project blast radius measured:
an uncoordinated 0.142→0.147 jump under live factories). Policy: check on cadence (watcher duty,
check-only), upgrade ONLY via hub-scheduled quiescent window (rollback pin, smoke drill both
families, ledger record). Fleet question CLOSED by USER RULING 2026-08-09: SINGLE aligned CLI version
fleet-wide, no per-project copies; fleet-scope upgrade windows + one-tick version-change alarms;
uncoordinated installs are incidents.

## Visibility
Portal protocol (`docs/fleet/PORTAL_PROTOCOL_20260808.md`): one portal/project, digest-never-dump,
artifacts outrank chatter, portals never adjudicate/steer, cheap-model narrator with procedural
prompts. **Dead-man = scheduled narrator (30-min class, wake-only) on `16,46` — CONFIGURED, ENABLED,
and NEVER RUN (see Scheduler truth). Treat it as absent until a `lastRunAt` appears.**

**Tooling caveat for anyone reading that store**: a delivered-unruled exit-3 alarm exists in
`tools\Get-HubRoundState.ps1`, and it is **per-ROUND scoped** — the predicate is built by iterating
rounds, so a free-standing review carrying no round vocabulary can never populate it. The tool exits
0 while such reviews sit delivered and unruled. Useful, real, and narrower than previously stated here.
