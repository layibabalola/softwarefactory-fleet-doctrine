# Ruling candidate: exhausted-model failback to Opus R12

Status: **PROPOSED ONLY — NOT RATIFIED DOCTRINE OR RUNTIME AUTHORITY**

Owner direction (2026-08-24): do not idle useful Claude capacity solely because exact Fable has
exhausted its model allowance. Continue unchanged eligible work on exact Opus while preserving the
hard capacity ceiling, seriality, exact contract, review quality, and every acceptance gate.

## Decision

Model exhaustion and provider/account exhaustion are different states. An exact terminal Fable
exhaustion attempt earns zero work, review, acceptance, or drain credit. If the same immutable work
remains authorized, publish an exact Opus successor through the natural scheduler and ordinary
one-shot admission path. Preserve ordered core subjects and digest, objective, lane role, effort,
tools, turn/wall bounds, output contract, and independent-acceptance requirements. Failback grants
no manual invocation, capacity inference, gate-opening, or quality exception.

Immediately before Opus admission, refresh signed model-free capacity for the same opaque quota
domain. Evidence may be at most 300 seconds old (a project may require less). For every required
window prove `utilization + active reservations + conservative Opus estimate <= 100`. Stale,
malformed, cross-domain, ambiguous, missing, overlapping, live-lease, closed-authority, or surplus
evidence is `HOLD`; authentication is not capacity evidence.

## Exact terminal-exhaustion discriminator

One immutable artifact plus durable zero-credit receipt must conjunctively bind the admitted
route/session and exact `claude-fable-5`; terminal `api_error`/429 after exactly one attempted turn;
assistant `error=rate_limit`; no verdict or acceptance; zero review input/output tokens; and the
exact text `You've reached your Fable 5 limit. Run /usage-credits to continue or switch models with
/model.` The receipt also binds packet, authorization, artifact path/hash, unchanged core digest,
closed assertion-name array, and exact assertion count. Wrapper probes earn no drain credit.

Every rate-limit event must be enumerated. Rejected base-window, signed 100%, or explicit account
exhaustion is `HOLD`. Rejected `seven_day_overage_included` with overage disabled is an entitlement
rejection only when the base event is allowed or omitted and fresh same-domain base utilization is
below 100; omitted base additionally requires the exact one-turn zero-token evidence and no
contradiction. Fresh capacity must publish utilization, reservations, estimate, sum, and named
`<=100` assertion for every window.

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

DNG proved terminal Fable zero credit, exact Opus failback, signed capacity, persisted consumption,
and terminal release. Review history is carried in the packet-readable evidence bundle: production
REVISE(9); R1 REVISE(3); R2 REVISE(6); R5 carrier rejection; R6 REVISE(5); R7 REVISE(6); and R8
Fable zero credit, Opus ACCEPT(0), then Sonnet REVISE(3), leaving serial acceptance zero.

R9 naturally reached exact Fable model exhaustion and then exact Opus/max. Opus returned
REVISE(11): the fourth subject was bare ancestry rather than the required capsule; hidden receipt
reads prevented reproduction; Git/local-run evidence was unreadable; the published age was one
millisecond inconsistent; and route, core, signature, and terminal-carrier hashes were unbound.
R10 repaired all eleven findings by using one route-bound capsule, a packet-readable validated
evidence bundle, exact timestamp derivation, explicit signed-capacity proof, and exact old/new
carrier transition hashes. Its exact Fable turn then terminalized zero-credit, but the local
continuation verifier correctly exposed a new defect before Opus: terminal validation was pinned to
R9 hashes and could not validate the current R10 transition. R11 replaces that stale pin with a
closed relationship: the terminal consumed-packet hash must equal the bound ancestry packet, while
Fable entry is also checked against R10's validated extract. R11 exact Fable then terminalized with
one turn, 429, zero tokens, no verdict, and zero credit before exact Opus consumed 27,594 output
tokens and returned REVISE(4). R12 repairs those findings: every successor ancestry digest must equal
the recomputed current core; route ancestry is pinned to the exact predecessor generation for each
lane; the bundle carries generator-bound packet-readable R11 Fable and Opus extracts; every core row
and the capsule independently satisfy the 24 KiB bound; and capacity age is computed at the bound
packet issuance timestamp. R9/R10/R11 retain zero acceptance credit.

Before ratification, distinct natural Fable, Opus, and Sonnet lanes must accept the same R12 core.
The adjudicators must reproduce the executed matrix, exact/surplus ceiling, classifier variants,
stale/cross/same-domain states, real row permutation, ancestry freshness, replay prevention,
execution drift, Git objects, capsule source hashes, and terminal artifacts. Ratification must be
appended to `RULINGS.md` and reach canonical `master`.

Every project must then publish honest `ADOPT`, `DISTINGUISH`, or `REJECT` with its own authority,
policy, scheduler, transaction, tests, rollback, and natural production proof. This proposal grants
no provider launch, account rotation, gate opening, merge, release, installation, or adoption.
