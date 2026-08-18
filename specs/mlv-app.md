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

## Ignition: an auth wall is invisible to every liveness detector we own (2026-08-18, first-hand)

- MLV-App lost its whole Claude lane family for ~9.5h. Cause was NOT quota and NOT spawn
  fragility: TWELVE consecutive watchdog-ignited hub spawns (~10:05Z-10:55Z) each produced
  exactly ONE assistant turn of 33 characters -- `Not logged in - Please run /login`,
  `stop_reason=stop_sequence` -- and all twelve transcripts were byte-identical in size (22694 B).
- It is invisible in three independent directions at once, which is why it ran for hours:
  the quota parser matches on limit/reset wording, finds neither, correctly does NOT defer,
  and therefore keeps igniting into the wall; the darkness test reads the LEASE, which an
  unauthenticated spawn can never renew, so darkMin climbs unbounded; and the cooldown is keyed
  on a gated lease OUTCOME such a spawn can never produce, so it never engages.
- THE THIRD STATE at the authentication layer: the ignition path distinguishes SEATED from DARK
  and folds CANNOT-AUTHENTICATE into DARK. A uniform-size transcript cohort is the cheap tell.
- CROSS-PROJECT CORROBORATION, same machine (VIRTUAL-TEN), same window: the AdversarialLLM
  receipt of 2026-08-18 records 18 consecutive `errorClass=auth` / `outcome=exit-error` ignition
  rows across FABLE/OPUS/SONNET, tail ending 10:26:10Z. Two projects, one host, one outage.
- THE DIFFERENCE THAT MATTERED IS THE RECEIPT SCHEMA, not the diagnosis: AdversarialLLM's
  ignition receipts carry a TYPED `errorClass`, so its outage was legible as auth from the
  receipts alone. Ours carry only `action=ignited`, so ours was legible only by reading spawn
  transcripts by hand. A sibling choosing between the two schemas should note that cost.
- Remedy shape available to us without new machinery: the launcher's out.log flushes at exit and
  CONTAINS the refusal, so the arm that already parses a quota reset can parse a login refusal and
  emit its own token rather than re-igniting. PROPOSED, NOT YET IMPLEMENTED here.
- Recovery is operator-only (a credential step). No lane may touch auth, and detection must never
  become an excuse to try.

## Seat-owned instruments: the orphan remedy is the mechanism of recurrence (2026-08-18)

- A hub producer's lifetime is bound to its PROCESS and nothing binds it to its SEAT. Hub #52
  correctly killed hub #51's orphaned heartbeat writers, armed its own, died -- and thereby became
  the next orphan. Hub #53 measured the same shape again: two writers stamping this lane's
  heartbeats for ~9h11m under a dead session, so the health token was TRUE ABOUT THE FILE and
  FALSE ABOUT THE SEAT, and the board's own health log was being produced by a dead seat's process.
- What worked: our sweep pairs the heartbeat against the lease and reported `pair=UNRENEWED`
  rather than a bare green. The three-state arm caught what a green/absent split would have hidden.
- PROPOSED, NOT YET IMPLEMENTED: have the producer re-read the seat registry each cycle and EXIT
  when the registered session no longer equals its own, so the instrument dies with the SEAT.
- Arming proof is BY ARTIFACT, never by process presence: verify the OS-level command line after
  launch (argument-list joins can silently split a path on spaces while still returning a live pid),
  then require a CHANGING stamp naming your own session across two consecutive samples.
