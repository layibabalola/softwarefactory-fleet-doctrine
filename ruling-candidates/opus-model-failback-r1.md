# Ruling candidate: exhausted-model failback to Opus R16

Status: **PROPOSED ONLY — NOT RATIFIED DOCTRINE OR RUNTIME AUTHORITY**

Owner direction (2026-08-24): after exact Fable model exhaustion, continue unchanged eligible work
on exact Opus without weakening capacity, seriality, contract, quality, or acceptance gates.

## Decision

Model exhaustion differs from provider/account exhaustion and earns zero credit. If unchanged work
remains authorized, the natural scheduler may publish an exact Opus successor through ordinary
one-shot admission. Preserve ordered core/digest, objective, role, effort, tools, bounds, output
contract, and acceptance requirements; failback grants no manual invocation or quality exception.

Immediately before Opus, refresh signed same-domain model-free capacity, at most 300 seconds old.
Every window must prove `utilization + active reservations + conservative estimate <= 100`.
Otherwise—including stale, cross-domain, ambiguous, overlapping, live-lease, or closed-gate
evidence—`HOLD`. Authentication is not capacity evidence.

## Exact terminal-exhaustion discriminator

One artifact plus zero-credit receipt binds admitted route/session, exact `claude-fable-5`, terminal
`api_error`/429 after one turn, assistant `error=rate_limit`, no verdict, zero review tokens, and
`You've reached your Fable 5 limit. Run /usage-credits to continue or switch models with /model.`
It also binds packet, authorization, artifact/hash, unchanged core, assertion names/count. Wrapper
probes earn no credit.

Enumerate every rate-limit event. Base-window rejection, signed 100%, or account exhaustion is
`HOLD`. Disabled `seven_day_overage_included` is only entitlement rejection when base is allowed or
omitted and fresh same-domain base usage is below 100; omission also requires exact one-turn
zero-token evidence and no contradiction. Publish every window's usage, reservation, estimate,
sum, and named `<=100` assertion.

## Immutable subjects and execution contract

Every packet row binds normalized relative path, bytes, and SHA-256. `core_subjects_sha256` is
SHA-256 of the canonical closed-key ordered-row JSON. Fable and Opus carry the same ordered core;
one lane attachment, excluded from that digest, carries continuation/review evidence without
replacing or reordering core rows. R2.1 remains at most four subjects, 24 KiB each, 32 KiB total.

The immutable contract is:

- Fable `claude-fable-5`, role `coordinator`;
- Opus `claude-opus-5`, role `executor`;
- Sonnet `claude-sonnet-5`, role `verifier`;
- effort `max`, at most 12 turns and 900 seconds, tools exactly broker `Read` plus
  `StructuredOutput`, result `route-review-result.v1`.

Packet hash, preclaim, argv receipt, and admission policy must prove the exact applicable values.
Any drift is `HOLD`.

## Reviewable verification capsule

The single lane attachment is a closed-key, hash-bound capsule generated outside the provider lane.
The verifier reads only the three core subjects and capsule—never cited receipts, raw provider
outputs, mutable ledgers, or Git metadata. It binds clean commit/tree/type/branch evidence; exact
control executable/command/core/repeat/PASS evidence; ancestry packet/route/session/model/core;
signed-capacity signer/proof/ledger snapshot and age derived at the packet issuance timestamp;
validated prior-lane
extracts; and consumed/terminal carrier, terminal receipt/lease, and close-before-clear hashes.

Large outputs may be represented only by packet-readable closed extracts whose generator hashes
and parses the raw bytes and binds its identity through the capsule's exact executable hash. The
capsule must bind its packet issuance timestamp and derive capacity age from that timestamp, not a
self-asserted capsule creation time. Self-asserted hashes or timestamps are `HOLD`. The capsule grants
no capacity, provider, acceptance, publication, ratification, installation, or adoption authority.

## Transactional terminalization and replay prevention

A terminal model-exhaustion event is a transition, not a global freeze. Before clearing its
campaign hold, the controller must atomically replace the consumed actionable carrier with a strict
closed-key terminal no-work packet (`authority=read-only-review`, `actionable_work=false`, empty
subjects), bind old/new hashes and the terminal receipt, then publish the unchanged successor.
The terminal consumed-packet hash must equal the bound ancestry packet.
If replacement fails, keep the hold closed and launch nothing. A consumed route id, matching
terminal receipt, or terminal lease can never be revived by timestamp refresh.

The executed matrix requires hostile `terminal_fable_carrier_replay` and close-before-clear proof;
documenting a duplicate is not repair.

## Account-domain self-heal

An authenticated-account/installed-domain mismatch is fail-closed. At most one bounded hash-pinned
transaction may run with closed gate, no concurrency or unconsumed canary, exact opaque rollback
preimages, different successor domain, fresh signed successor capacity, hostile controls, and an
atomic outcome. Persist no identity or credentials; only commit permits a later ordinary retry.

## Preserved invariants

Preserve exact model/subjects, serial order, one quota-domain owner, zero reserve, hard 100% ceiling,
conservative reservation, closed gate, bounded execution, validated output, and truthful release.
Cross-domain telemetry, overlap, live lease, stale carrier, and failed-output laundering remain
`HOLD`. Fable is completeness only. Findings restart at Fable on a forward subject; installation,
cadence, tick, disposition, and adoption gates remain separate.

## Evidence and acceptance

DNG proved natural terminal Fable zero credit, exact Opus failback, signed capacity, persisted
consumption, and deterministic release. Published R14 binds the complete ordered adverse history.
The R15 packet carries that bundle hash, the exact R14 Fable/Opus/Sonnet terminal rows, and the
current-master integration identity; the verifier asserts those values without reopening history.

R9 exposed capsule, hidden-read, Git, timestamp, route, core, signature, and terminal-binding gaps.
R10 repaired them but revealed a stale current-transition pin. R11 repaired that relationship, then
Opus consumed 27,594 output tokens and returned REVISE(4). R12 repaired digest recomputation,
per-lane predecessor pinning, packet-readable prior extracts, per-row size enforcement, and
issuance-derived capacity age; its Fable attempt was exact one-turn zero-credit exhaustion and its
Opus run consumed 32,182 output tokens before REVISE(3). R13 completed and asserted the review
history and added generator-bound packet-readable R12 extracts, but its local verifier rejected the
missing literal terminal relationship before provider publication. R14 preserved those repairs,
stated that relationship exactly, then completed the natural completeness front door with exact
one-turn Fable model exhaustion and zero credit before exact Opus and Sonnet both returned ACCEPT.
The exact accepted R14 commit is published at `refs/heads/codex/opus-model-failback-r1`.

R15 integrated the published lineage on current master but failed its 35,380-byte carrier check.
R16 preserves the law and compacts prior history to its bundle hash plus exact R14 terminal rows.
Fable remains the completeness front door; exact model-scoped exhaustion with zero tokens and no
verdict is not acceptance and does not block ratification. Before ratification, Fable must end on
the R16 core as ACCEPT or exact zero-credit model exhaustion; exact Opus and Sonnet must then ACCEPT
that unchanged core. R15 and every rejected or exhausted generation retain zero acceptance credit.
The lanes must reproduce the matrix, ceiling cases, classifier variants,
domain/freshness states, row permutation, replay prevention, execution drift, Git objects, capsule
hashes, publication ancestry, and terminal evidence.
Ratification must be appended to `RULINGS.md` and reach canonical `master`.

Every project must then publish honest `ADOPT`, `DISTINGUISH`, or `REJECT` with its own authority,
policy, scheduler, transaction, tests, rollback, and natural production proof. This proposal grants
no provider launch, account rotation, gate opening, merge, release, installation, or adoption.
