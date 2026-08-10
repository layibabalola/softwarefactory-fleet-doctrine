# metrics/ — the fleet DATA PLANE (ratified: Cloudvore hub, 2026-08-09; open for sibling adoption)

This directory is the one sanctioned exception to "the bus carries laws, not state": an
append-only event-history data plane so the fleet can measure itself and draw cross-project
graphs. Approach ratified at Cloudvore `review/hub-ruling-interaction-metrics-0809.md` under the
operator's 2026-08-09 20:07 directive (one repo, not a second one).

## Layout & rules
- `metrics/<project>/events-YYYY-MM.jsonl` — append-only, monthly shards, ONE WRITER per project
  directory (the project's own hub). Other projects: read-only.
- Events are DERIVED by each project's compiler from its existing artifacts (ledgers, gate lists,
  beats, git) — no lane gets a logging duty; double-entry is refused by design. The one new
  record: an optional CORRECTION seam in a terminal row when a lane overturned/improved a
  proposal (who proposed, what changed, evidence pointer) — the interaction existing artifacts
  under-capture.
- Schema v1: `{ts, project, actor:{lane,role,platform,model}, verb, object, counterparty?,
  refs:[...], outcome?, latency_s?}`. Verbs: PROPOSE, CORRECT, IMPROVE, REFUTE, RATIFY, REJECT,
  SEAT, CLAIM, DONE, DECLINE, RETIRE, MERGE, BAR, FINDING, ADDRESSED, SEAM-EXPORT, FOLD, OUTAGE,
  DRILL, UNPARSEABLE (a row the compiler cannot parse is SAID, never dropped). Schema changes are
  doctrine changes: ratify before bumping.
- Suggested metric set: correction quality (findings filed/confirmed/refuted, ADDRESSED latency,
  review kill rate, proposals amended by counterparty, born-stale charter rate); flow
  (time-to-seat, DONE→MERGED latency, bar pass + FALSE-STOP rate, rework rate); resilience
  (wake-source uptime, QUOTA-DORMANT time, outages by class, drill results, pairing debt);
  hygiene (doc-cap breach age, stale claims, seam rows exported vs folded, owner-gated age).

## The two laws that keep this safe
1. **Metrics are DIAGNOSTIC, never authority and never targets.** Ledgers and git answer "what
   happened"; metrics answer "how are we trending". The moment any seat cites metrics/ as
   authority for a decision, or a lane is graded on its metric line, the offending metric is
   retired (Goodhart guard). Falsifier recorded at the ratifying ruling.
2. **Compiler drift:** if events contradict the source artifacts, the artifacts win and the
   compiler is the defect. Fix or suspend the shard; never edit history to match.

Graphs are derived, rendered as artifacts by whoever wants them, and never stored here as state.
