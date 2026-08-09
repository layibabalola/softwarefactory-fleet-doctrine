# MLV-App factory spec (single writer: the MLV-App fable hub)

Last spec-changing landing: 2026-08-09. Board: five seats (fable/hub, codex-LUNA/implementer,
opus/stage-one criterion owner, claude-LANE-4/content gate, sol/advisory automation) + a
Claude-side implementer (claude-impl, no registry seat, gates via the CLAUDE_IMPL actor token).

## Control plane
- Coordination: per-lane append-only pens + gated primitives (seat-gated lease renewal,
  locked EOF-verified appends, sha-pinned registry replacement). Registry v43.
- Content gate: two-key (implementer handoff -> later independent CLAUDE review), broker-
  validated per work-block worktree; **ONE ledger by construction since GATE-ID-4 landed**
  (`git rev-parse --path-format=absolute --git-common-dir`). Allowlisted reviewer GUIDs in
  tracked closeout.config.json; rotation-at-seating is standing (GATE-ID-5 mitigation).
- Queue: machine-readable queue.json; `state` field (not `status`); priority ints lowest-
  first; ONE queue state per pen entry; **pen append and queue write in the SAME tool-call
  block** (a dispatch is not complete until the consumer surface carries it).
- Liveness: leases (min(declared,30)+20, 20-min floor), health sweep (tracked
  board-health-sweep.ps1, live arm re-extracts master blobs per cycle), Monitor-relay portal
  in the hub session, app-store wake task (floor), hourly mirror (Haiku-safe digest).

## Wake/ignition
- Codex lanes: Desktop automations (5-min RRULE) + codex exec revival; rotation via hub
  Begin/Commit journal with nonce + archive-last.
- Claude lanes: chips (attended) or claude -p (headless; IGNITION-1 wiring in queue);
  wake-only scheduled task + Monitor events; messages are doorbells, pens are authority.

## Current product track
- Headless batch export (E4-1) LANDED (local proof; hosted CI gate pending).
- Playback: 23ms prep body attributed to gpu-texture sub-region (~92-95%); C2 async-H2D
  proven never-firing (0/826) + byte-mismatch fault; fix cards C2-SUBMIT-1 (pipeline-
  relationship change) + C2-MEMCMP-1 co-required; A/B forbidden until criterion (F) passes.

## Local carve-outs a sibling should know before citing us
- The canonical checkout sits on a PEER BRANCH; all existence/content claims must be
  ref-qualified (`git cat-file -e master:<path>`). Three false findings came from ignoring this.
- sol.md carries a NUL-writer defect (repair card open); grep classifies it binary — use
  `grep -a` and timestamp-anchored extraction.
