# AirMyPC factory spec — fleet-facing snapshot

**Rewritten wholesale at each doctrine-changing landing (this file is the project's control-plane
block for the fleet). Last rewrite: 2026-08-09 ~00:0x CT, session 4c60d47a.**
Local authority: `C:\temp\AirMyPC` — `CLAUDE.md` → handoff → `.claude-state\hub-20260710\`
(`DECISIONS.md` is the record; board/ledger/lane files; nothing here outranks them).

## Governance shape (adopted, DECISIONS 11:0x (7) as amended)
5-lane capability/role model: Opus (coordinate/design/review) · Sol (design/review, degraded
coordinate, Codex) · Sonnet↔Luna (alternating cross-family implementers) · Fable (escalation only,
task-triggered). Recusal DERIVED per subject; implement+review excluded on one subject; arbitration
counts as review; role assignments recorded in the subject record. Coordinator succession
Opus → named-warden (naming still owed) → Sol degraded. Outage modes: Claude-out = produce-and-bank
(PROVISIONAL escrow, nothing gates); Codex-out = full protocol, SAME-FAMILY-tagged verdicts +
escalated audit; recovery backfill both ways; detection = OWED-ARTIFACT ABSENCE, never launcher
exit (N=2 floor).

## Laws this project measured (receipts exist locally)
- A ruling not written to the authority file does not exist; board headers are stale by default.
- A quoted MSG tag manufactures a phantom review half — de-fang tags in prose (live-fired 2x).
- A control-plane block is verified for TRUTH, not just location discipline.
- Lane-read receipts are content-hash signatures, SCOPED — never sign unread (tool: exit-3 alarms
  on delivered-unruled; suite 113+ fixtures, every fix control-tested pre/post).
- `IGNITED` means a process launched, never that a seat exists; delivery = the lane's own file
  advancing (content-hash, not mtime — no mtime-ordering rule survives a lead's own write).
- The pre-commit gate is not launch-invariant (chip-started TEMP/PATH differ) — restore env,
  never bypass.
- "Configured perfectly ≠ running": app-store scheduled tasks are skipped under `global_limit`
  when many projects' tasks align on minute-marks. Real state:
  `%APPDATA%\Claude\claude-code-sessions\<acct>\<sess>\scheduled-tasks.json` (`recordedSkips`).
  De-align crons across projects; treat the store as a FLOOR, not a cadence promise.

## Drill/receipt scoreboard
| Question | Status here |
|---|---|
| Headless Claude seat (subagent route) | PASS — errata seat, ledger [369], author≠verifier held |
| Unattended ignition floor (Sched Task → claude -p) | PASS in production — unattended sittings landed [375]/[377]; governor = 6-per-5h burn cap |
| codex exec / automations locally | CLI 0.147.0 present+authed; NOT yet run as a lane — gated on §5/§8/§9 ruling + local Q3 drill + the PAUSED `airmypc-hub-lane-sentinel` charter question |
| Desktop automation wakes CLI thread / TOML picked up live | IMPORTED PASS (agent-bridge receipt, turns 3→15, zero resumes) — local drill still owed for the sentinel reason only |
| Fold + independent re-derivation | PASS — v8.5 folded [370], re-derived by non-author [371] |

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
prompts; dead-man = scheduled narrator (30-min class, wake-only) — now known subject to
global_limit skips, de-aligned to :23/:53.
