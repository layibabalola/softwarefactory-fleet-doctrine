# MLV-App factory spec (single writer: the MLV-App fable hub)

Last spec-changing landing: 2026-08-09 (wake/ignition + registry refresh, fable SEQ 1297 R7; gate section previously reviewed by LANE-4, claude SEQ 488). Board: SIX registered seats (fable/hub, codex-LUNA/implementer,
opus/stage-one criterion owner, claude-LANE-4/content gate, sol/advisory automation, and
claude-impl — FIRST-CLASS since registry v45 per the operator's five-lane topology: registered
seat, lease file `claude-impl.json`, own pen, gates via the CLAUDE_IMPL actor token).

## Control plane
- Coordination: per-lane append-only pens + gated primitives (seat-gated lease renewal,
  locked EOF-verified appends, sha-pinned registry replacement). Registry v45.
- Content gate (REVIEWED by the gate's own reviewer, claude SEQ 488, against master 94a72be2
  BY EXECUTION - adopt these exactly or distinguish explicitly):
  * Two-key: an admitted implementer-token handoff, then an independent CLAUDE review entry
    appearing later IN THE FILE (BYTE OFFSET - heading timestamps are DECORATIVE to the gate;
    sorting/backdating entries silently breaks an adopted gate).
  * TWO implementer tokens are admitted on master: handoffActor=CODEX plus
    additionalHandoffActors=['CLAUDE_IMPL']; actor AND kind match by EXACT EQUALITY on a
    PARSED heading. VERIFY AT master (git show master:tools/repo_hygiene/brokered_closeout.py,
    never a checkout): the peer branch working tree still carries a SUBSTRING actor test
    under which the implementer holds both keys - reading the wrong ref inherits the hole.
  * LEDGER is ONE file by construction (resolved to the MAIN worktree via
    git rev-parse --path-format=absolute --git-common-dir, GATE-ID-4); gate POLICY is still
    read from the INVOKING work-block worktree's tracked closeout.config.json - two worktrees
    can agree on the ledger and disagree on policy at the same instant (measured live).
  * Approving verdicts need a bare Verdict:, the canonical full-40 Range:, and a Seat: in
    the tracked allowlist. BLOCKING VERDICTS DELIBERATELY SKIP THE IDENTITY ARM (an
    unattributed block still blocks - commented in source). Do NOT ''harden'' by requiring
    Seat: on blocks: that converts a missing Seat on a BLOCK into a non-verdict, i.e. it
    REMOVES a block - fail-open wearing hardening's costume.
  * Verdict debt is derived by ASKING THE VALIDATOR, never by prose-parsing the ledger
    (a prose parse over-reported 97 against a true 0 here).
  * Reviewer GUID rotation-at-seating is standing (GATE-ID-5 mitigation); the rotation commit
    cannot go through owner-gated commit tooling when the config resolves owner=unknown -
    plain git commit is the documented exception.
- Queue: machine-readable queue.json; `state` field (not `status`); priority ints lowest-
  first; ONE queue state per pen entry; **pen append and queue write in the SAME tool-call
  block** (a dispatch is not complete until the consumer surface carries it).
- Liveness: leases (min(declared,30)+20, 20-min floor), health sweep (tracked
  board-health-sweep.ps1, live arm re-extracts master blobs per cycle), Monitor-relay portal
  in the hub session. **App-store wake/mirror tasks are RETIRED BY RECEIPTS** — the 08-09
  account rotation silently emptied the app scheduler registry (SKILL.md files intact, zero
  receipts ever); the durable floor is machine-scoped (below). `DARK` is at least THREE
  states: idle-not-renewing, task-gate-refused (LIVENESS-KEY-1), and QUOTA-DORMANT(reset_eta)
  — only the third self-resolves, and every wake/reseat remedy is guaranteed to fail against
  it (class-B instance measured live 14:55-17:21Z, spawns refused at the account limit,
  all sessions woke on the reset to the minute).

## Wake/ignition
- Codex lanes: Desktop automations (5-min RRULE) + codex exec revival; rotation via hub
  Begin/Commit journal with nonce + archive-last.
- Claude lanes: **OS Task Scheduler watchdog `MLV-LaneIgnitionWatchdog`** (machine-scoped,
  20-min, `ignite-dead-lanes.ps1`): per-lane lease check against min(declared,30)+20, frozen
  verbatim seat prompts, pinned per-lane models, cooldown-guarded headless `claude -p`
  ignition, receipts on EVERY run including stand-downs (an absent log is indistinguishable
  from a dead task). Ratified as IGNITION-1's mechanism at fable SEQ 1297; drill + tracked
  copies pending on the card. Chips are the attended FALLBACK only. Messages are doorbells,
  pens are authority.

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
