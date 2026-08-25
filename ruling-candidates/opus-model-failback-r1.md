# Ruling candidate: exhausted-model failback to Opus R10

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

The single lane attachment is a closed-key, hash-bound verification capsule generated outside the
provider lane. It must make evidence reproducible without broadening provider tools. The core
verifier may read only the three core subjects and that capsule; it may not reopen cited receipts,
provider outputs, mutable capacity ledgers, or Git metadata. The capsule contains:

- candidate commit/tree plus literal results of `git cat-file -t`, `git show --format=%T`, branch,
  and clean-status checks, and the independent generator path/hash;
- the exact local-control command, executable identity, externally supplied core digest, repeat
  count, assertion/case counts, exact PASS outputs and output hashes;
- exact ancestry packet hash, route id, session id, model, and normalized ancestry-core digest;
- the continuation ancestry: Fable exhaustion receipt, hold disposition, terminal lease, both
  opaque domains, observed/created instants (age is derived, never rounded or self-published),
  utilization/reservation/estimate/sum rows, ceiling, and no-overlap;
- signed-capacity source/signer, signature/proof, immutable ledger snapshot hash, and same-domain
  attestation; and
- the consumed carrier hash, terminal no-work carrier hash, terminal receipt, lease, and exact
  close-before-clear receipt;
- for prior completed lanes, exact packet/consumption/terminal-lease objects or closed-key validated
  extracts, their whole-file hashes/bytes, and the exact structured result copied from the raw output
  with raw-output path/hash/bytes.

Large raw provider output need not fit the carrier: its compact extract is eligible only when the
evidence-bundle generator hashes the raw bytes, parses the terminal result, proves the copied
structured result exact, validates every cited compact object against its source bytes, and binds
the generator identity. The packet-readable evidence bundle then carries those closed extracts and
source hashes; the capsule binds the exact bundle hash and copies only the lane facts needed for the
current transition. A self-asserted hash without these checks is `HOLD`. Capsule evidence grants no
capacity, provider, acceptance, publication, ratification, installation, or adoption authority.

## Transactional terminalization and replay prevention

A terminal model-exhaustion event is a transition, not a global freeze. Before clearing its
campaign hold, the controller must atomically replace the consumed actionable carrier with a strict
closed-key terminal no-work packet (`authority=read-only-review`, `actionable_work=false`, empty
subjects), bind old/new hashes and the terminal receipt, then publish the unchanged successor.
If replacement fails, keep the hold closed and launch nothing. A consumed route id, matching
terminal receipt, or terminal lease can never be revived by timestamp refresh.

R8 exposed the reason: hold clearance raced carrier replacement and the next natural cadence
replayed the same exact Fable packet. The duplicate also ended in exact one-turn zero-token Fable
exhaustion and earned zero credit, but it is a control defect. R9 requires a hostile
`terminal_fable_carrier_replay` case and close-before-clear receipt; merely documenting the duplicate
is not repair.

## Account-domain self-heal

An authenticated-account/installed-domain mismatch is fail-closed. At most one bounded hash-pinned
transaction may run for a fresh mismatch, with closed gate, no concurrency or unconsumed canary,
exact opaque rollback preimages, no raw identity or credentials, different successor domain, fresh
signed successor capacity, hostile controls, and atomic `COMMITTED` or `ROLLED_BACK` receipt. Only
commit permits a later ordinary retry; the actor has no work, acceptance, release, credential,
account-selection, or inference authority.

## Preserved invariants

Preserve exact successor model and subjects, strict serial order, one quota-domain owner, zero
discretionary reserve, hard 100% ceiling, conservative reservation, closed gate, one-use canary,
bounded execution, validated output, and truthful terminal lease. Cross-account telemetry, overlap,
live lease, stale carrier, and failed-output laundering remain `HOLD`. Fable is the completeness
front door, not acceptance or owner authority. Findings restart at Fable on a forward immutable
subject. Installer, preview, rollback/reinstall, cadences, ticks, project disposition, and adoption
remain separate gates.

## Evidence and acceptance

DNG proved terminal Fable zero credit, exact Opus failback, signed capacity, persisted consumption,
and terminal release. Review history is carried in the packet-readable evidence bundle: production
REVISE(9); R1 REVISE(3); R2 REVISE(6); R5 carrier rejection; R6 REVISE(5); R7 REVISE(6); and R8
Fable zero credit, Opus ACCEPT(0), then Sonnet REVISE(3), leaving serial acceptance zero.

R9 naturally reached exact Fable model exhaustion and then exact Opus/max. Opus returned
REVISE(11): the fourth subject was bare ancestry rather than the required capsule; hidden receipt
reads prevented reproduction; Git/local-run evidence was unreadable; the published age was one
millisecond inconsistent; and route, core, signature, and terminal-carrier hashes were unbound.
R10 repairs all eleven findings by using one route-bound capsule, a packet-readable validated
evidence bundle, exact timestamp derivation, explicit signed-capacity proof, and exact old/new
carrier transition hashes. The R9 adverse verdict remains zero acceptance credit.

Before ratification, distinct natural Fable, Opus, and Sonnet lanes must accept the same R10 core.
The adjudicators must reproduce the executed matrix, exact/surplus ceiling, classifier variants,
stale/cross/same-domain states, real row permutation, ancestry freshness, replay prevention,
execution drift, Git objects, capsule source hashes, and terminal artifacts. Ratification must be
appended to `RULINGS.md` and reach canonical `master`.

Every project must then publish honest `ADOPT`, `DISTINGUISH`, or `REJECT` with its own authority,
policy, scheduler, transaction, tests, rollback, and natural production proof. This proposal grants
no provider launch, account rotation, gate opening, merge, release, installation, or adoption.
