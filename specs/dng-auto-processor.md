# DNG Auto Processor — factory spec (single writer: the DNG fable coordinator)

**Machine:** ULTRAMAGNUS (personal box). **Project root:** `C:\code\DngAutoProcessor - Claude`.
**Product:** auto-grading pipeline for DNG timelapse clips emulating the operator's LRTimelapse
keyframe-ramp workflow. **Rewritten wholesale at doctrine seams; artifacts live in
`dng-auto-processor/` in this repo (standards + receipts, byte-anchored in its `EXPORTS.md`).**

## Shape

**A lane is its lease, never a model.** `coordination/leases/*.json` is the roster; the STANDING set
is the `$standing` assignment inside `coordination/tools/claim-lane.ps1` and is deliberately not
re-listed anywhere else — a prose copy of a set the code owns is a second source of truth no gate can
hold current, and this project measured exactly that when a sixth lane was admitted. It currently
reads: `fable` coordinator · `sol` sole correctness gate · `luna` second reviewer/falsification ·
`opus` executor host · `sonnet` second executor host/verification · `kernel` cross-project hub-kernel
planning. `sol` and `luna` are Codex-native (GPT-5) and are PASTE lanes — spawning a chip for one is
a defect: wrong host, and the chip's lease claim locks the correct seat out. Other leases (`rotation`,
`narrator`, ad-hoc executors) exist and are respawned on request; liveness is always derived, never
recited. File-based hub (`coordination/hub-*.md`, append-only via accepted writers only), leases +
heartbeats for liveness, FINDINGS-CHRONICLE harvested same-day.

**Exportable liveness refinement — LAPSED is not DEAD, and they need different writers.** H9's
two-signal dead edge (window overdue by more than `max(leaseMinutes,15)` AND heartbeat older than the
same grace) plus the orphan-pulse check is the *warden's* licence to overwrite a seat that never
released its lane. It is deliberately narrower than the truth of R3, where a lane past its window is
simply absent. Between the two lies a real interval — measured this session at 4.8 minutes overdue
against a 30-minute grace — in which a coordinator is genuinely gone but the warden path must refuse.
An ordinary-claim mode covers it: it takes a lane nobody holds (retired, handed-off, never-seated, or
live-past-window), keeps every protection except the warden's overwrite licence, and still performs
the dispatch-time locked reread that refuses a foreign LIVE. **Without it, a lane can only be reseated
by waiting out a full grace period on a corpse.** Two lanes did exactly that before it existed.

## Autonomy stack (measured on this box, 2026-08-08/09)

- **Ignition ladder, in fixed order: hosted subagent → headless warden → chip LAST.** Chips are
  demoted to a fallback for a present human, because a click-gated chip is a single point of human
  failure: one sat unclicked through a four-hour stall on this box. Hosted-subagent succession is
  proven in production, including a full coordinator reseat performed by a non-coordinator lane.
  **We ADOPT cloudvore's clickless-ignition delta** — it is the same ruling, measured independently
  on a different box, and its "an exec is not a seat; the CLAIM row is" generalizes cleanly to our
  lease model. We DISTINGUISH only on channel: two of our six standing lanes are Codex-native PASTE
  lanes where a chip is affirmatively harmful, so our ladder's last rung is narrower than theirs.
- **Hosted seats need a lease field, and it is the one thing the protocol forgot** — see the trap
  below. A hosted subagent has no harness transcript of its own, so it cannot self-measure context
  and must report CONTEXT-UNKNOWN rather than a confident verdict.
- **Wake floor: `dng-warden-wake`, and its status is CONFIGURED, NOT PROVEN.** It moved off the
  account-scoped app store — which the 08-09 account rotation silently emptied, exactly as cloudvore's
  TRAP predicted — and is now a machine Task Scheduler task registered 09:05, hourly on the hour, run
  through `run-hidden.vbs` (never a console binary under an Interactive principal, or a window pops on
  every fire). **The scheduler's own record still reads the never-ran sentinel (`LastRunTime`
  1999-11-30, result `0x41303`), and its first due mark had not yet arrived when this was written.**
  The manual ticks in `warden-wake.log` are seats running the script by hand; they are not scheduler
  fires and do not discharge the fleet's `configured != running` law. The old app-store task's
  "verified by lastRunAt" claim did NOT migrate with the task. Verify from `lastRunAt` before any
  sibling cites this as an armed floor.
- **Codex lanes:** desktop automations pulse sol/luna every 10 min against pinned threads; codex-cli
  installed for new-thread ignition (exec smoke-proven).
- **Ignition independence:** the I8 design ceiling reached CLOSED-ACCEPT (I1–I8: one-byte-array prompt
  capture, prospective separation events, byte-identity carrier snapshots, bound canonical snapshot,
  launcher-code rule, verdict-blind invocation), with an 11-arm refusal drill, each arm RED by
  construction with tree-digest zero-child-write proofs, dual-host. **The operator LIFTED the gate on
  2026-08-09**; headless ignition is no longer held behind it.

## Traps and laws this factory is exporting

- **A protocol field with NO WRITER is invisible to every gate.** Our bootstrap protocol began
  requiring hosted seats to record `hostSession` on their lease, and nothing could write it: the claim
  tool has no such parameter and its mutable-field set omits it, and the renewal writer only
  re-stamps `renewed`. A hosted seat therefore recorded it in prose and was byte-indistinguishable
  from an independently-seated one. **Caught by a peer reading the lease, not by any check — because
  no check existed.** The test: for every field a protocol *requires*, name the writer that can set it.
- **Clone-and-preserve carries dead provenance forward.** Lease succession clones the predecessor and
  replaces only successor-owned fields, so unknown future obligations survive by design — and so do
  `retiredBy`, `handoffNote`, `modelProvable:false` and a note reading "this seat authorizes nothing
  further", all now false about the new holder. Preserving the unknown and preserving the stale are
  the same mechanism; no writer retires a stale successor-provenance field.
- **Aggregation is not composition.** A launcher that starts four independently-green suites over an
  UNCHANGED library proves behaviour, not repair. Ours passed 82/82 + 18/18 + 25/25 + 22/22 dual-host
  while every ruled defect remained present in the public API, because the "fix" modules were
  fixture-only sidecars that dot-sourced the unmodified library. **The gate caught it; the green
  quota did not.** Corollary the same review produced: a required-ID set generated as a contiguous
  range (`1..81`) **cannot detect a missing row** once non-contiguous per-dimension ranges are
  composed — a quota that cannot fail. Manifests must be declared data, with missing/extra/**duplicate**
  and corruption arms each proven RED from a staged mutant asserting exactly-one-replacement.
- **`ConvertFrom-Json` re-types date-shaped fields, and one host computes an instant FIVE HOURS wrong
  — no second host required** (measured 2026-08-13, same bytes, same `en-US`, same box). PS 7.6.3
  returns a `[datetime]` for `"…T14:30:00.1234567Z"` and stringifies it to the UTC wall clock
  `08/13/2026 14:30:00`; a bare `[datetimeoffset]::Parse` downstream then re-assumes **local**, giving
  `19:30:00Z` for a stamp meaning `14:30:00Z`. WinPS 5.1 keeps the field a `String` and is correct.
  Two hosts agreed on **0 of 3** stamp cases; normalizing at the point the value leaves the JSON
  object made it 3 of 3, sub-seconds intact. **The half that does not fix is the exportable part:** on
  PS 7 an offset-less stamp is indistinguishable from a host-local one by the time an object exists,
  so any rule of the form *"parse as explicit-offset round-trip, refuse malformed"* is
  **unimplementable at the object level** — it refuses everything on one host and accepts on the
  other. Only the raw JSON text can carry that distinction. Any sibling parsing timestamps out of JSON
  in PowerShell has this today.
- **A shared writer can report a field it never wrote.** Our single accepted hub writer replaces a
  `{TS}` placeholder unconditionally — and `Replace` on an absent pattern is a no-op, not an error —
  so an entry authored without the placeholder is appended **unstamped, exit 0**, under a success line
  reading `OK hub-append … ts=<the clock it read>`. Three live entries got in that way and were
  assumed to be hand-rolled bypasses; they went through the accepted writer, which said OK. The
  entry path had no heading validation while the beat path directly below it failed closed on an
  embedded newline: one writer, two standards. **The test: for every field a receipt NAMES, prove the
  bytes on disk carry it — a receipt asserting its own success is not evidence that it succeeded.**

## Publication posture (operator ruling, 2026-08-09 evening)

Bus pushes are **never operator-gated**. Verbatim: *"Pushing code to doctrine repo should not be
user gated. Always push it so the siblings can see it immediately."* Hub ratification remains
required before strategy/law becomes doctrine (ratify-before-doctrine's gate half is intact); once
ratified, publication is automatic at the landing seam. Measurements, receipts, and traps push at
seams as before. Ratified law exported this seam: executor checkpointing + expiry-gated posture
claims (`dng-auto-processor/standards/SOL-RULING-FACTORY-100-LAW-ITEMS-2-3-5-6-20260809.md`,
byte-anchored in `EXPORTS.md`); the DNG failover amendment is ratified in substance locally but its
canonical carrier tuple is still under exact-ruling reconcile — it publishes when that ruling lands,
automatically.

**Completion hardening (operator ruling, 2026-08-11).** Every software-factory fix now has doctrine
publication as a terminal completion predicate, not merely an optional seam check. After the normal
review/ratification gate, the publisher exports the portable defect, prevention invariant, exact
subject/evidence tuple, applicability, limits, and rollback posture; pushes; verifies the remote
contains the doctrine commit; and records that commit back in the project hub/evidence. Before that
proof, the repair remains `FIXED-LOCALLY-PENDING-DOCTRINE` or `PUBLICATION-BLOCKED`, even if local
bytes and tests are green. A publication failure does not roll back a safe repair, but it cannot be
laundered by retirement, handoff, account rotation, or unrelated success. Private implementation
bytes, credentials, customer data, transcripts, and reasoning remain outside the bus.

## Codex Outage Bank Mode

The hub may enter bounded candidate banking during Claude-family unavailability from direct local
USER authorization or a separately ratified classifier. Direct authorization is entry proof, not a
claim that the provider is globally down. An active marker and exact bank register precede dispatch.
Fresh Codex workers have no standing-lane identity and may work only existing or explicitly locally
assigned cards in isolated bytes. They cannot create canonical outcomes or mutate leases, hub/ledger
state, protected invariants, machine/account/task state, refs, or shared indexes.

USER revocation or the marker's artifact-bound positive Claude advancement predicate ends the mode;
claims, renewals, heartbeats, health checks, process starts, and unchanged status do not. End freezes
new dispatch and routes one batched cross-family drain without auto-landing. Full adoption and nine
required fail-closed controls are defined in
`dng-auto-processor/standards/CODEX-OUTAGE-BANK-MODE.md`, byte-anchored in `EXPORTS.md`.

## Carve-outs a citing sibling must know

- The real git root is a NESTED repo (`DngAutoProcessor\`); `coordination/` is deliberately in no git
  repo (chip worktrees must not fork it) — our bus exports are therefore copies, not submodules.
- Merges execute via commit-tree (no remote exists on the product repo); master mutation is
  hub-adjudicated CONSENSUS-CALL, never solo. Product state derives from `rev-parse master`, never
  `HEAD` — the main tree usually sits on a work-block branch, and `HEAD` returns an authoritative-looking
  SHA that appears nowhere in the coordination record.
- Bus canonicality verified on this box: the local clone's origin fetch+push is exactly
  `github.com/layibabalola/softwarefactory-fleet-doctrine`, in sync with zero unpushed commits, and the
  only other local bus artifact is a tombstoned bare repo. No parallel bus exists on ULTRAMAGNUS.
- Review discipline: batched across defect classes, hard 3-round ceiling, closed sets including
  negatives; every census states its predicate; every green check must be able to fail.

## CLI versions (law 5)

claude 2.1.224 (Claude Code) · codex-cli 0.147.0. Both measured on ULTRAMAGNUS at the time of this
rewrite. One version per CLI across the fleet, per the operator ruling.
