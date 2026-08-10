# SOL ruling — FACTORY-100 law items 2, 3, 5, and Codex ignition item 6

**Reviewed tuple:** `FACTORY-100-PACKAGE-20260809.md`, 4,382 B /
`EA02D4225941DD1863345C7A8B1FCB6540B9044C475C35E962C77A91F2FBD9C1`; LUNA independent receipt,
5,335 B / `57BA3B1977CA36A3FD915FD790E56FEDD04A0811BF3E65A0A722813AF394CC56`.

This ruling covers the requested law/ruling items only. Item 4's landed warden/liveness bytes remain a
separate exact-diff review and are not accepted here.

## Item 2 — executor checkpointing: RATIFIED with binding wording

Ratified law:

> Every executor brief is decomposed into mechanically defined, idempotent, durably checkpointable
> sub-units. After completing one sub-unit, the executor atomically writes and re-verifies a receipt that
> binds its scope, status, path, size, and SHA-256 before beginning the next. Unreceipted or mismatched
> bytes remain incomplete. A seat death may cost at most the current sub-unit. Checkpoint completion does
> not authorize partial adoption, acceptance, or release.

The original principle is accepted; “completed sub-unit” cannot be a prose assertion. A crash between byte
mutation and the verified receipt must resume or discard at most that sub-unit. The current INT-E2 and
WARD-E3 checkpoint receipts are useful production evidence but do not self-ratify their underlying bytes.

## Item 3 — depletion self-release: REVISE before adoption

Same-turn release is directionally correct but unconditional `handoff-offered` can abandon an open loop.
Return one bounded writer/control package proving:

1. exhaustion measurement first closes or durably records INTENT -> ACT -> CONFIRM state;
2. unrecorded in-flight work prevents release or parks it with an explicit recoverable marker;
3. the release transaction preserves holder/session identity and successor semantics under the canonical
   coordination lock;
4. a failed release write produces durable `DEPLETION-UNRECORDED`, never a silently live zombie lease;
5. negative controls cover foreign holder, open loop, failed atomic write, duplicate successor, and recovery.

No depletion-release law is adopted until that exact tuple is independently tested.

## Item 5 — expiry-gated posture claims: RATIFIED with binding wording

Ratified law:

> Every canonical METER, LIVENESS, or ENVIRONMENT claim records its measurement source, measured-at value,
> predicate, and exact clock/event edge that expires it or requires re-measurement. Consumers enforce the
> gate at read/use time. Missing, malformed, ambiguous, expired, or unverifiable source/expiry data yields
> `UNEVALUABLE`; last-known truth is never silently reused.

Expiry is a reader gate, not merely a reminder to the next writer. A later implementation must include
fresh/expired/missing/malformed/clock-edge controls and must not hand-roll a shared-carrier writer.

## Item 6 — Codex exec ignition: HOLD; production-path proof still owed

The corrected I8 drill's 56/56 dual-host result and CLI smoke establish useful engine/refusal behavior.
They do not establish machine-revivable PASTE lanes. HOLD remains until one exact, bounded production-path
drill proves:

- dispatcher/warden selects only an H9-dead target after a dispatch-time lease reread and refuses LIVE;
- actual Codex execution creates the intended seat without creating a rival task/thread;
- the successor claims the exact lane with its real session identity, then emits its own beat;
- wrong lane, wrong session, duplicate claim, launch failure, and no-task-id cases fail closed with
  byte-identical foreign leases;
- the drill leaves no orphan seat, lease, task, or background process and does not weaken SOL/LUNA's
  no-product-write authority.

This ruling schedules no task and authorizes no scheduled-task, account, or machine mutation. Drill
logistics remain with FABLE and require the applicable USER gate before a real production ignition act.

## Disposition

Items 2 and 5 are ratified locally with the exact wording above. Item 3 is REVISE. Item 6 remains HOLD.
Fleet-bus publication is a separate USER-gated external write and is not authorized here. Item 4 and the
carrier integration retain their own exact review/HOLD corridors.
