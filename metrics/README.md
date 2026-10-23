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
  DRILL, VERIFY, BEAT, UNPARSEABLE (a row the compiler cannot parse is SAID, never dropped). Schema changes are
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

## Fleet self-improvement health (daily rows, weekly review; added 2026-10-16)

Owner request 2026-10-16: regular checks of each fleet project's self-improvement health. One tool, no
second copy: `tools/factory/fleet-scorecard.py` (row schema `fleet/scorecard-row/v1`, file
`metrics/scorecard-daily.jsonl`, documented in the root README "Fleet scorecard"). Each row now carries
`machine` and a `health` block `{status: GREEN|RED|UNMEASURED, reasons, unmeasured, thresholds_sha256}`
judged by [`fleet-health-thresholds.json`](fleet-health-thresholds.json).

- **Cadence.** DAILY, one machine task per machine, mechanical (no model calls):
  `python tools/factory/fleet-scorecard.py --fleet --bus <bus clone> --publish`. `--fleet` measures every
  member derived from `specs/` (the shared `tools/fleet-membership.mjs` rule) that has a clone in the
  machine-local `~/.fleet-roots.json`; every other member is an UNMEASURED row, listed and never published.
  WEEKLY, the hub's model review reads the rows (trend, RED reasons, members no machine measured).
- **Measures** (per project): census copies and double registrations against the tool-census schedule max
  in force; the project's own rule coverage against its own floor (NONE when it has no census);
  14-day product share (one `Get-ProductThroughput.ps1 -Lines` run); days since the newest bus commit
  attributed to the project; fold lag = doctrine-bearing commits after its `doctrine-sync` ack cursor
  (doctrine-sync's surfaces, minus `cos-feedback/_heartbeat/`) and the oldest one's age; days since its
  newest `adjudications/factory-kernel/<project>*.md` filing on master or a review branch.
- **Rows are diagnostic (law 1).** RED names an OVERDUE duty; it never blocks a commit, a landing or a
  lane, and the exit code never depends on a value (`--dry-run --print` for a human look).

## Amendment log
- 2026-08-09 (Cloudvore): +VERIFY, +BEAT — filed as the first CORRECTION seam by the compiler
  lane against the ratifying hub's own schema (the ruling omitted lane-state's VERIFY terminal
  and the warden BEAT the wake-gap histogram is built from). Hub folded per doctrine cadence.
  Also measured: git MERGE counts are NOT rebase-stable; treat them as generation-stamped.

## Candidate extension: provider capacity events (NOT YET RATIFIED)

The fleet provider-capacity candidate proposes append-only
`metrics/<project>/provider-usage-YYYY-MM.jsonl` shards conforming to
`schemas/provider-usage-event-v1.schema.json`. This is a separate event shape from interaction
schema v1 and grants no live admission authority. Projects must not publish raw account identifiers,
credentials, prompts, transcripts, or command lines. Until a fleet ruling ratifies the extension,
the schema and examples are conformance candidates only.

## Candidate extension: model posture (NOT YET RATIFIED)

`metrics/<project>/posture-*.jsonl` holds weekly, then monthly, then yearly AGGREGATES of which model and effort each
role actually ran (`schemas/model-posture-rollup-v1.schema.json`, writer `tools/factory/model-posture.py`). Raw
per-call rows never travel. Entry: [`model-posture/README.md`](model-posture/README.md). Candidate:
`ruling-candidates/fleet-model-posture-telemetry-r2.md` (r1 vetoed, RULINGS.md R19.3). Posture shards are the one
named exception to this directory's append-only rule: a roll-up commit deletes its weekly or monthly sources
after byte-identical recomputation, and history is never rewritten (every source resolves at the parent).
