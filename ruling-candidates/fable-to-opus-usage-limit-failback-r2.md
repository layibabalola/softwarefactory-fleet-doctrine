# Ruling candidate: Fable-to-Opus usage-limit failback R2

Status: **SUPERSEDED ADVERSE DRAFT — SCHEMA CONTRADICTED PROSE; SEE R3**

Two fresh non-authoritative Opus stranger reviews rejected R2 because receipt schema v1 could not
truthfully represent direct dormancy routing, running/recovery states, or unsettled useful output;
it also lacked cross-field intent/spawn constraints and overstated host-local locking as fleet-wide
serialization. Compact findings are preserved at
`receipts/adversarialllm-fable-opus-failback-r2-review-disposition-20260824.json`. R2 and schema v1
remain adverse history and grant no authority.

R2 supersedes the rejected R1 draft and incorporates both R1 stranger-review dispositions. It also
distinguishes informative project submissions at remote commits `fee4fa2` (Adobe) and `68a57a8`
(Conjugal). Those project branches are evidence, not canonical rulings and not authority here.

## Purpose and non-goals

Useful Claude work should not remain idle solely because Fable's included allowance is exhausted
while exact Opus capacity is still available. The economic objective is **useful output per paid
allowance**, never token burn for its own sake. Unchanged status narration, fabricated review demand,
mechanical polling, and work created only to spend quota remain model-free or `IDLE_SKIPPED`.

Failback routes one otherwise-authorized work item from a Fable availability cell to an Opus
availability cell. It does not move credentials, roles, claims, leases, actor identity, reviewer
keys, provider-family independence, adjudication, landing, release, or owner authority.

## Identity model

Keep these scopes separate:

- **account quota domain** — one opaque HMAC identity used for serialization and allowance
  accounting across Fable, Opus, Sonnet, repositories, transports, and wrappers sharing an account;
- **provider independence class** — Anthropic/Claude remains one class regardless of model or
  account; Fable and Opus cannot supply two independent acceptance keys;
- **model availability cell** — exact requested model and allowance window. A refusal naming Fable
  closes only the Fable cell unless provider-native evidence explicitly proves a wider scope; and
- **role cell** — exact provider/model/effort/transport/authority profile qualified for a task.
  Availability never manufactures role qualification.

An Opus successor is permitted only when the exact work role already allows Opus. Where Fable and
Opus occupy distinct producer, reviewer, hub, or verifier roles, failback that would collapse roles
onto one actor/model is refused even when independence keys are not directly involved.

## Trigger classifier

`FABLE_QUOTA_DORMANT` requires all of:

1. a terminal, parseable native result from a hash-pinned runner;
2. terminal class `api_error` and status 429;
3. bounded native evidence that names the Fable allowance-limit class, with a retained salted
   digest of the classifier input and a versioned allowlist rule;
4. no Fable task output, no partial assistant message, and measured-zero or explicitly unknown
   usage distinguished field by field; and
5. a durably closed primary attempt whose terminal digest and sequence can be independently read.

Generic 429, account-wide exhaustion, auth/payment/credit error, runner drift, lost or malformed
output, cancellation, timeout, process ambiguity, or Fable output followed by a limit becomes a
typed non-success with **no Opus failback**. `FABLE_LIMIT_AFTER_PARTIAL_OUTPUT` parks the work item
for explicit recovery because replay could duplicate or contaminate output.

The measured 2.1.237 observation showed that native `--fallback-model opus` did not produce an Opus
result on the observed Fable-limit terminal. That single observation is not a universal negative.
The supervising wrapper therefore treats built-in fallback as opportunistic for overload only and
uses its own typed, one-attempt state machine for quota dormancy.

## Durable state machine

The work-item id hashes the exact subject, prompt bytes, role, effort, tool policy, output schema,
runner identity, wrapper identity, and project authority reference. Raw prompts and outputs never
enter shared receipts.

State advances under one machine-local account-domain lock with an atomic create-if-absent record,
monotonic fencing token, process generation, boot identity, expiry, and crash-safe compare-and-swap:

`PRIMARY_PLANNED -> FABLE_RUNNING -> FABLE_TERMINAL -> OPUS_INTENT_DURABLE -> OPUS_RUNNING -> OPUS_TERMINAL -> SETTLED`

Rules:

1. Attempt ordinal 0 is Fable; ordinal 1 is the only Opus child. A durable monotonic ordinal is read
   under the lock immediately before spawn. No third model or retry exists.
2. The wrapper preassigns the Opus session id, writes and flushes `OPUS_INTENT_DURABLE` with child
   attempt id, parent terminal digest, immutable work-item digest, fencing token, runner/argv digest,
   budgets, and session-id HMAC **before** process creation.
3. Process spawn uses that exact preassigned session id. Recovery correlates pid, process start,
   boot id, session id, advancing native output, and immutable work-item digest. It reconciles an
   existing child; it never infers absence from missing terminal output.
4. Fable is never resumed. The Opus child may be reattached or resumed only for reconciliation of
   its preassigned session, never to create a second inference turn.
5. Every state record is hash-chained, write-through, and atomically published. A missing, torn,
   conflicting, stale-fenced, or ambiguous record blocks. Usage is `measured`, `estimated`, or
   `unknown`; zero is never substituted for unknown.
6. Parent settlement is exactly once after both attempts are terminal or the Opus child is proven
   never spawned. Ledger failure after useful Opus output remains recovery-required and cannot
   launch another child.

## Opus launch contract

The final transaction revalidates useful demand, ordinary task authority, work-item bytes, role
eligibility, account-domain lock, exact Fable terminal, runner/wrapper hashes, child intent, capacity
reservation, foreground priority, and every project hold.

The installed policy must pin:

- resolved Claude runner version, executable and behavior-bearing package hashes;
- exact requested Opus model and accepted primary assistant-message model id;
- allowed auxiliary model ids used only for non-task side operations, all of whose usage is still
  charged and recorded;
- maximum wall time, turns, input/cache/reasoning/output tokens, and cost or allowance slice;
- dormancy `freshUntil`, reset observation when present, bounded `probeAfter`, maximum dormancy age,
  and anti-flap backoff; and
- a fleet-visible disable switch whose default is disabled.

Exact task-model identity comes from the native assistant message/event, not prompt self-report and
not the mere presence of a `modelUsage` key. The terminal records the complete usage map because
Claude may legitimately use an auxiliary Haiku-class model for non-task side operations. Any
unallowlisted model, missing primary task model, provider mismatch, model drift, or role mismatch is
typed non-success and grants zero useful/review credit.

No wrapper may login, logout, rotate accounts, read or rewrite credentials, set authentication
environment variables, purchase credits, switch APIs, automate attended UI, lower model/effort, or
fall through to another model. Opus refusal or ambiguity ends the work item without retry.

## Dormancy, reset, and revocation

While a fresh Fable dormancy record exists, new eligible work may route directly to Opus. If the
native terminal exposes no reset boundary, the installed project policy must provide a bounded
probe time and hard maximum dormancy age; missing values disable direct routing. A reset probe is a
new bounded Fable work item or provider-native model-free capacity observation, never a replay of
the failed attempt. Positive Fable capacity affects only later work and never preempts Opus.

The kill switch stops new Opus intents immediately. An already-running child is contained through
its existing terminal/settlement path unless the ordinary project safety authority requires
termination. Disablement never discards the journal or converts partial output to success.

Rollout is `DISABLED -> SHADOW_CLASSIFIER -> CONTAINMENT_FAKE -> ONE_AUTHORIZED_CANARY -> CLOSED`.
Every canary terminal reseals `CLOSED`. Broader activation requires fresh project-local review and
adjudication; this candidate cannot activate itself.

## Receipt and observability contract

The versioned receipt schema is
`schemas/fable-opus-failback-receipt-v1.schema.json`. Shared receipts contain only normalized enums,
timestamps, opaque HMAC identities, SHA-256 digests, aggregate usage, and authority booleans. Raw
prompts, outputs, native error text, account/user/org identifiers, credentials, absolute paths, and
plaintext session ids remain machine-local.

Required metrics are diagnostic and zero-authority: classifier outcomes; failback count; Fable
dormancy age; reset/probe outcomes; Opus useful-output rate; task and auxiliary model identities;
input/cache/reasoning/output usage; cost/allowance estimates; budget stops; single-flight
contention; orphan/recovery count; identity mismatches; Opus refusals; kill-switch state; and
settlement lag. Alerts fire on runner drift, classifier drift, dormancy expiry, model mismatch,
orphan child, repeated Fable/Opus refusal, budget breach, or unsettled useful output.

## Minimum hostile controls

1. Fable success, generic 429, auth/payment error, timeout, malformed/lost terminal, process
   ambiguity, or partial Fable output: zero Opus child intents.
2. Exact Fable-limit fixture: one durable child intent then at most one Opus process.
3. Prompt, subject, role, policy, runner, wrapper, or authority digest drift parent-to-child: refuse.
4. Crash before intent, after intent/before spawn, after spawn/before first output, during output,
   after useful terminal/before ledger settlement, and during settlement: recovery never duplicates
   and eventually produces one typed parent terminal or an explicit blocker.
5. Repeated supervisor restarts and pid reuse: monotonic fence and ordinal still admit at most one
   Opus child.
6. Stale lease, dead holder, live ambiguous holder, two repositories, and two transports on the
   same account domain: at most one compatible active child; ambiguity does not kill or take over.
7. Exact Opus primary identity with allowlisted auxiliary usage succeeds; missing, wrong, floating,
   multiple task models, wrong provider, or unallowlisted auxiliary identity earns zero credit.
8. Opus wall-time/token/cost ceiling: child stops typed non-success; no continuation or retry.
9. Fable reset before intent and while Opus is live: later work returns to Fable without preemption
   or relabeling.
10. Kill switch before intent and while Opus is live: no new child; existing journal remains
    recoverable and terminal.
11. Same-family and role-collapse tests: Fable refusal plus Opus success never satisfies two-key,
    two-reviewer, producer/reviewer, hub/verifier, or recusal independence.
12. Idle or unchanged demand: zero Claude calls. Useful output with failed settlement is recovered,
    not rerun. Tampered receipt, journal, schema, or hash chain is rejected without inference.
13. Runner version/hash change: classifier and identity fixtures must be revalidated before
    failback; otherwise the kill switch remains closed.

## Adoption and ratification boundary

Project adoption must bind exact runner version/executable/package hashes, wrapper hash, schema
hash, classifier-policy hash, installed-policy hash, hostile-test receipt, staged-install receipt,
kill-switch receipt, and project authority map. It must separately prove one useful bounded Opus
canary and rollback to disabled.

Before fleet ratification, a distinct adjudicator must bind the exact candidate commit/tree and
artifact manifest, reproduce the hostile controls on the actual supervising wrapper, obtain fresh
independent review, and append an exact disposition to `RULINGS.md`. Until then R2 is data only. It
authorizes no provider launch, scheduler/task mutation, authentication action, gate opening,
project adoption, review or vote credit, landing, merge, release, billing change, or account action.
