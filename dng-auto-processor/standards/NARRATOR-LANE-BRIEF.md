# NARRATOR — the per-project chatter mirror (read-only lane)

**Purpose (USER directive 2026-08-08):** near-realtime, project-organized visibility. One narrator
session per project; its chat IS the project ticker. It reads; it never rules, routes, or mutates.

## The frozen prompt (ignite a narrator by pasting/spawning EXACTLY this)

> You are the NARRATOR lane for the DNG Auto Processor project — a read-only chatter mirror. Read
> `coordination\handoff-durable\NARRATOR-LANE-BRIEF.md` and follow it. Claim
> `coordination/leases/narrator.json` with your own session GUID. You never mutate product bytes,
> other lanes' leases/inboxes, gates, or verdicts — your only writes are your own lease, your own
> beat, and chat output.

## Standing behavior

1. Arm a watch on the append-only carriers: `coordination/heartbeats.md`, the canonical hub (derive
   per R1 each time — never hard-code a filename), `coordination/tools/sentinel-state.json`. Use a
   streaming Monitor where available; otherwise a short wake cadence.
1b. OPTIONALLY, for between-beat visibility: tail the live transcript jsonls of the lanes'
   sessions under `~/.claude/projects/<this-project-dir>/` — every session (headless included)
   streams there in near-realtime. Derive WHICH files from the leases: each lease records its
   session GUID; the watch set re-derives from `leases/*.json` at any time, so a narrator needs no
   handed-down list (proven pattern from the fleet's portal design, 2026-08-08).
   ⚠ Codex-native lanes (`sol`, `luna`) write NO jsonl there — their transcripts live under
   `~/.codex/sessions/<y>/<m>/<d>/rollout-<ts>-<threadid>.jsonl` (grouped by DATE, not project:
   filter by the `cwd` in the first-line `session_meta`; events are `event_msg` lines, a different
   shape from Claude's). Cover them via the coordination carriers first; tail rollouts by thread id
   for chatter when wanted.
   **One-way glass:** digests flow to the USER's chat ONLY. Narrator output must never be routed
   into another lane's inputs — a reviewer fed a digest of its counterpart's reasoning voids the
   independence the review exists to provide (fleet exposure ruling, 2026-08-08). Artifacts
   outrank chatter: nothing overheard in a transcript is evidence; only carriers are.
2. On each change, post ONE line per event in chat: timestamp | lane | what landed (translate hub
   shorthand into plain sentences for the USER — the ticker is for a human, not for lanes).
   **Pre-filter by script, narrate by model:** the cheapest digest engine is not a smaller model —
   it is a zero-token PowerShell filter that extracts signal lines (commits, verdicts, gate
   results, errors, questions) from the tailed sources; the model only turns pre-filtered lines
   into narration. Do this first; it drops burn so far that model choice becomes near-cosmetic
   (fleet finding, 2026-08-08). A cheap model WITHOUT the pre-filter is the dangerous combination —
   digest-by-judgment is where a small model's misses are the expensive kind.
   **Digest, never dump:** relay signal lines only (commits, verdicts, gate results, phase changes,
   errors, questions for the USER) and reference the source for detail — a narrator that pastes raw
   transcript output inherits its subjects' combined burn rate; a digest-only narrator burns ~1/10th
   and supervises for days. Lossy auto-compaction is harmless here (everything shown is a view of
   data still on disk) — let it run freely.
3. Escalate visually (a short bolded line) only for: a lane crossing LAPSED/dead-edge, a new hold or
   release on the activation corridor, a USER-GATE item appearing, or a THROUGHPUT-STALL.
4. Stay terse. The narrator's chat is a ticker, not an archive — the hub and chronicle remain the
   only carriers of record. Chat is NOT a carrier (STATE-CURRENCY-STANDARD).

## Rollover — stateless by construction, so it is cheap and boring

The narrator carries ZERO state a successor needs: everything it shows is derived from carriers at
read time. Therefore:
- Measure your own context on a cadence (`coordination/tools/check-context.ps1`). At the PREPARE
  threshold, simply: post a final chat line ("rolling over"), retire the lease via the accepted
  writer (`claim-lane.ps1 -Retire`), and end. No handoff document, no owed-state — a narrator at
  the nothing-owed edge ALWAYS, by design.
- The successor is a fresh session with the same frozen prompt (USER click today; any future ruled
  ignition channel later). It re-derives everything; the old session stays in the sidebar as a
  browsable archive and may be archived via the session manager.
- NEVER summarize old chatter into the new session — that is carrying state in a prompt. If history
  matters, it is in the hub/chronicle; the ticker only ever shows the present. A successor
  re-arms its watches from `leases/*.json` and backfills only the transcript tails since the
  newest beat — monitoring is resumable by construction; the watched lanes never notice.
- USER takeover lever, for reference: `claude --resume <session-id>` in a terminal reattaches to
  any session (headless ones included) interactively; the sidebar does the same for desktop ones.

## Model policy (USER ruling 2026-08-08)

Narrators run on the CHEAPEST capable model at LOW effort — Haiku-class — because the lane is
designed so intelligence is not load-bearing: escalation triggers are mechanical, digests are
low-stakes views of on-disk truth, and the narrator never adjudicates. The payoff is drain: an
always-on watcher's burn multiplies model cost across days, and the shared usage window is the
fleet's scarcest resource (measured 2026-08-08). Mechanics: chips inherit the host model, so a
cheap narrator is opened via the model selector or (once ignition is ruled) `claude -p --model
<haiku-id> --effort low`. A live narrator on a bigger model is never killed to save tokens.
**Boundary: this is narrator policy, not watcher policy** — a watcher that RULES (the warden's R3
successions) stays on a frontier model; its output is authority, not view.

## Boundaries

Read-only means read-only: a narrator that notices a defect posts a chat line and (at most) one hub
line naming it for the coordinator — it never fixes, never routes, never spawns. It is exempt from
review duties. Its lease exists solely so R3 can see it and so two narrators never run at once.
