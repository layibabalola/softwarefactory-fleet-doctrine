# Ruling candidate: exhausted-model failback to Opus R18

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

The installed route packet is also part of the immutable execution contract. Its `authority` is the
native JSON string `read-only-review`, its `result_contract` is the native JSON string
`route-review-result.v1`, its three control flags are native booleans, and every subject `bytes`
value is a native integer. Stringified booleans or integers, object-shaped result contracts,
alternate authority labels, extra keys, or any other type drift are `HOLD` with zero launches.

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
capsule timestamp must equal the immutable issuing packet's `issued_at_utc`; the verifier must
compare both values and derive capacity age from that packet timestamp, never from capsule fields
alone. The current Fable extract must be packet-readable and bind exact model, route, packet,
session, one turn, 429, result text, zero input/output tokens, absent verdict, zero credit, and its
capacity account domain. Opus capacity must prove the same opaque domain against that extract.
Self-asserted hashes, timestamps, or domains are `HOLD`. Per-lane local assertion counts are exact,
not merely positive. The capsule grants no capacity, provider, acceptance, publication,
ratification, installation, or adoption authority.

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

Published R14 binds the adverse history and natural Fable zero credit followed by exact Opus and
Sonnet ACCEPT at `refs/heads/codex/opus-model-failback-r1`. R15 failed carrier size. R16 compacted
history, then Opus held after 18,246 output tokens on packet-time, readable-extract, domain, and
exact-count defects. R17 repaired those findings, but the installed scheduler held its carrier on
three five-minute ticks with `PACKET-TYPE` and zero calls, processes, tokens, or tools; its staged
repair still used a noncanonical authority. R18 binds the installed native contract and restarts
at Fable. Fable remains the completeness front door; exhaustion is not acceptance. Before
ratification, Fable must ACCEPT R18 or prove exact zero-credit exhaustion, and exact Opus and
Sonnet must ACCEPT the unchanged core. Rejected and exhausted generations retain zero credit.
The lanes must reproduce the matrix, capacity, replay, execution, Git, capsule, ancestry, and
terminal evidence. Ratification must be appended to `RULINGS.md` on canonical `master`.

Every project must then publish honest `ADOPT`, `DISTINGUISH`, or `REJECT` with its own authority,
policy, scheduler, transaction, tests, rollback, and natural production proof. This proposal grants
no provider launch, account rotation, gate opening, merge, release, installation, or adoption.
