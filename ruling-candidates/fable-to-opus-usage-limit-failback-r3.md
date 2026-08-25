# Ruling candidate: Fable-to-Opus usage-limit failback R3

Status: **SUPERSEDED ADVERSE DRAFT — MACHINE SCHEMA REMOVED FROM CONTROLLING R4**

Two fresh non-authoritative Opus reviews rejected R3 because schema v2 still admitted route/status,
intent/attempt, identity, credit, rollout, clock, and budget contradictions. Compact findings are
preserved at
`receipts/adversarialllm-fable-opus-failback-r3-review-disposition-20260824.json`. R3 and schemas
v1/v2 remain adverse design evidence only. They must not be implemented or cited for adoption.

R3 is the controlling candidate. R1 and R2 remain adverse history. R3 preserves R2's fail-closed
authority, role, identity, budget, dormancy, and rollout boundaries while replacing the
contradictory receipt contract with conditional schema v2.

## Portable decision

When a hash-pinned native Fable attempt terminally proves a Fable allowance limit with zero task
output, a project may route the same immutable, otherwise-authorized work item to one bounded Opus
attempt. A Fable refusal never proves Opus unavailable, and a successful Opus result never proves
Fable recovered. The objective is useful work from paid capacity, not token consumption.

The route is eligible only when Opus is already qualified for the exact role. It never transfers
credentials, actor identity, claims, leases, provider-family independence, reviewer keys,
adjudication, merge, landing, release, or owner authority. Fable and Opus remain one Anthropic
independence class and cannot provide two independent keys or collapse producer/reviewer,
hub/verifier, or recusal-separated roles.

## Scope model

- `accountDomainHmac` identifies the local account allowance pool without publishing account data.
- Fable and Opus availability cells are separate observations inside that account domain.
- Serialization in R3 is explicitly **one host**. One host-local broker coordinates all local
  repositories, transports, wrappers, and models sharing the account-domain HMAC.
- Multi-host use of one account is prohibited until a separately reviewed shared arbiter exists.
  R3 neither claims nor simulates fleet-wide mutual exclusion.
- Wall-clock freshness is paired with host boot identity and monotonic timestamps. A boot change,
  monotonic rollback, unavailable clock, or inconsistent wall/monotonic ordering invalidates the
  dormancy record and blocks direct routing.

## Typed Fable terminal

`FABLE_QUOTA_DORMANT` requires terminal native JSON, API error 429, a versioned allowlist match that
names the Fable allowance limit, zero partial task output, a pinned runner/classifier policy, and a
durably hash-chained terminal record. The shared receipt stores only the classifier code, policy
digest, and salted input digest; the salt and native evidence stay in protected local custody.

Generic or account-wide 429, auth/payment/credit error, runner drift, malformed/lost output,
timeout, cancellation, ambiguous process state, or any partial Fable task output produces a typed
terminal and zero Opus intents. `FABLE_LIMIT_AFTER_PARTIAL_OUTPUT` parks the work item; replay is
forbidden.

The single 2.1.237 observation remains `CONSISTENT_WITH_EXPLICIT_FAILBACK`, not proof of a universal
native-fallback defect. The exact executable SHA-256 is
`406167231B3636E55A01D0CE93567256C61E7973489E645883302F14808AE668`;
the observed receipt is explicitly gap-marked and has no runtime authority.

## Two lawful routes

1. **Primary route:** Fable attempt ordinal 0 succeeds or terminally fails. No Opus attempt exists.
2. **Failback route:** Fable ordinal 0 terminally enters `FABLE_QUOTA_DORMANT`; Opus ordinal 1 may
   start after a durable child intent.
3. **Direct dormancy route:** a *new* work item references a still-fresh prior dormancy receipt;
   it has no fabricated Fable attempt and uses Opus ordinal 0. The prior dormancy scope must be
   Fable-cell-only, the host/boot/account/model-policy tuple must match, and both wall and monotonic
   expiry checks must pass.

Schema v2 represents all three routes explicitly. It never requires a terminal or settlement block
for an in-flight receipt.

## Crash-safe state and spawn law

All state records are immutable hash-chained envelopes under a host-local account-domain lock with
atomic create-if-absent, monotonic fence, boot/process generation, compare-and-swap publication,
write-through durability, and one state transition per record.

Before Opus process creation the supervisor:

1. consumes the allowed ordinal under the lock;
2. preassigns the Opus native session id;
3. writes and flushes one intent containing work-item digest, parent/dormancy digest, ordinal,
   attempt/session HMACs, fence, exact runner/argv/policy/model, budgets, and intent digest; and
4. records spawn initiation under the same exclusive transition before invoking the child.

An intent with `spawnCount=0` is proven not spawned. An intent with `spawnCount=1` is always treated
as potentially live until pid/start/boot/session/native-output correlation and terminal settlement
prove otherwise. Recovery may attach only to the preassigned Opus session for reconciliation; it
must not create another inference turn. Fable is never resumed. A crash after useful Opus output
but before parent settlement remains `OPUS_TERMINAL_UNSETTLED`, preserving the output and blocking
replay until the ledger settles exactly once.

## Identity, budgets, and auth

The primary task model is read from the native assistant message/event. Complete per-model usage is
recorded because permitted auxiliary Haiku-class side operations may appear. Requested and primary
task model ids, provider, exact-model allowlist digest, and every auxiliary model/usage entry must
match installed policy; prompt self-report and a mere aggregate usage key are insufficient.

Both Fable and Opus attempts have hard wall-time, turn, input, cache-creation, cache-read,
reasoning, output, and cost/allowance ceilings. Each usage field is independently `measured`,
`estimated`, or `unknown`; unknown is never zero. Missing budgets or stale capacity prevent launch.

The supervisor may not login/logout, rotate accounts, read or rewrite credentials, set auth
environment variables, buy credits, change API/provider, automate attended UI, lower model/effort,
or choose a third model. Opus refusal or ambiguity is terminal with no retry.

## Dormancy, kill switch, and rollout

A direct-route dormancy record contains source receipt digest, observation/reset/probe times,
monotonic counterparts, maximum age, availability scope, and anti-flap counter. Missing or expired
fields disable direct routing. Positive Fable capacity affects later work only and never preempts an
Opus child.

The installed kill switch defaults `CLOSED`. Closing it forbids new intents. In-flight children
remain bounded by their existing budgets and settle normally unless a separately authorized safety
termination occurs; that termination is a typed non-success, not rollback of inference. Old-runner
work items retain their pinned bytes for settlement but cannot start or continue another turn after
runner drift.

Rollout is `DISABLED -> SHADOW_CLASSIFIER -> CONTAINMENT_FAKE -> ONE_AUTHORIZED_CANARY -> CLOSED`.
Containment receipts are structurally non-credit. Every canary terminal reseals `CLOSED`; broader
activation requires a new project-local authority and is outside R3.

## Machine-readable contract

`schemas/fable-opus-failback-receipt-v2.schema.json` uses conditional route/status validation. It
records receipt identity/time/chain, host and boot identity, rollout and kill-switch state, exact
policy/schema/runner hashes, work item, account and model cells, dormancy, Fable attempt, Opus
intent/attempt, full per-model usage, budgets, settlement, observed actions, and constant-false
authority fields.

The receipt's `usefulOutcome` is set by the project-local frozen outcome evaluator identified by
SHA-256; `UNKNOWN` earns no quality/review credit. Shared artifacts exclude raw prompts, outputs,
errors, account/user/org ids, credentials, absolute paths, and plaintext session ids.

Required diagnostic metrics are classifier distribution, Fable dormancy age, direct/failback route
count, Opus useful outcome, task/auxiliary identities and usage, cost/budget stops, contention,
recovery/orphans, reset/anti-flap outcomes, kill-switch state, and settlement lag. Runner/classifier
drift, dormancy expiry, identity mismatch, orphan, repeated refusal, budget breach, and unsettled
useful output alert visibly but grant no authority.

## Hostile proof floor

Before adoption, mutation tests must prove:

- all non-exact/partial/ambiguous Fable terminals create zero Opus intents;
- exact Fable dormancy creates one flushed intent and at most one Opus process;
- every crash boundary from pre-intent through post-output settlement is restart-safe and duplicate
  free under repeated supervisor restarts and pid reuse;
- intent/spawn/status/settlement contradictions fail schema and semantic validation;
- primary, failback, and direct-dormancy routes validate only their lawful conditional shapes;
- stale/boot-changed/clock-regressed dormancy, stale/dead/ambiguous locks, and two local repositories
  or transports remain fail-closed and single-flight;
- a second host sharing the account is detected as unsupported and cannot claim R3 adoption;
- exact primary identity with permitted auxiliary usage passes; every drift/mismatch fails;
- every budget dimension, kill-switch transition, reset/anti-flap boundary, and runner upgrade has a
  positive and negative control;
- same-family, role-collapse, reviewer-blindness, and recusal boundaries never gain credit;
- useful output with settlement failure is recovered rather than rerun; tampered chain/schema/
  policy/receipt fails without inference; and
- unchanged or idle work makes zero Claude calls.

## Adoption and ratification boundary

An adoption tuple must bind runner version/executable/package hashes, wrapper, schema v2,
classifier policy, model allowlist, installed policy, frozen useful-outcome evaluator, hostile-test
receipt, staged installation, kill-switch proof, host-scoped launcher census, one exact useful Opus
canary, and reseal-to-disabled receipt.

Before fleet ratification, a distinct adjudicator must bind the exact candidate commit/tree and
manifest, reproduce the hostile controls on a real supervisor, obtain fresh independent review,
and append an exact disposition to `RULINGS.md`. Until then R3 is data only and authorizes no
provider launch, task/scheduler mutation, authentication action, gate opening, adoption, review or
vote credit, merge, landing, release, billing change, or account action.
