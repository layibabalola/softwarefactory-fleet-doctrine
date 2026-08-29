# Ruling candidate: Fable-to-Opus usage-limit failback R1

Status: **SUPERSEDED ADVERSE DRAFT — NOT RATIFIABLE; SEE R2**

Two independent non-authoritative Opus stranger reviews rejected this draft. Their compact
disposition is preserved at
`receipts/adversarialllm-fable-opus-failback-r1-review-disposition-20260824.json`. R1 remains
published as adverse history because it overclaimed a single observation, did not bind the Fable
and Opus attempts to one immutable work item, lacked a write-ahead child intent and recovery fence,
conflated account/quota identity with per-model availability, and specified neither a spend ceiling
nor an operational kill switch. It grants no authority and must not be implemented.

Owner direction: 2026-08-24. Useful Claude inference must not remain idle merely because the
preferred Fable model has exhausted its allowance. When Fable is quota-dormant, bounded eligible
work should continue on Opus without weakening identity, independence, review, admission, or
release controls.

## Measured trigger

The exact native Claude Code runner was
`claude.exe` 2.1.237, SHA-256
`406167231B3636E55A01D0CE93567256C61E7973489E645883302F14808AE668`.

A non-interactive invocation using `--model fable --fallback-model opus` returned terminal API
status 429, zero input/output/model usage, and the native Fable-limit classification. The built-in
fallback did **not** run. A separate one-attempt invocation of the same immutable work item using
`--model opus` completed successfully. Its structured terminal named exactly one effective model:
`claude-opus-5` / canonical model `claude-opus-5`, with 12,598 output tokens, 17,387 cache-creation
input tokens, and measured cost USD 0.48883. The redacted normalized receipt is
`receipts/adversarialllm-fable-opus-failback-probe-20260824.json`.

Therefore `--fallback-model opus` is not sufficient evidence of failback for a Fable
usage-exhaustion response in this runner version. A supervising wrapper must classify the terminal
and explicitly start Opus.

## Proposed portable strategy

For one immutable work item, subject digest, role, tool policy, and output contract:

1. **Primary attempt.** Start Fable once in non-interactive structured-output mode. Keep Claude's
   built-in Opus fallback configured for overload/unavailability, but do not assume it covers quota
   exhaustion.
2. **Typed classification.** Accept `FABLE_QUOTA_DORMANT` only when the terminal is an API error,
   HTTP status is 429, model usage is empty, and the bounded native result classifier identifies
   the Fable allowance limit. Generic 429, malformed output, lost output, timeout, auth failure, or
   ambiguous process state is not this class and does not authorize Opus.
3. **Durable attempt close.** Persist the Fable attempt id, immutable subject/prompt digest,
   executable/version/hash, argv policy digest, terminal digest, classifier, and zero/nonzero usage
   before any second launch. A missing or uncertain close blocks failback.
4. **One explicit Opus attempt.** Under the same work-item id and immutable input bytes, create a
   distinct one-use child attempt and invoke exact `--model opus`. Never resume the failed Fable
   session and never replay more than once.
5. **Identity enforcement.** Credit useful inference only when terminal JSON is successful and
   `modelUsage` contains exactly one effective entry whose canonical model is `claude-opus-5`.
   Missing, multiple, downgraded, or unexpected identities are typed non-success.
6. **Settlement.** Reconcile both attempts, including failures and unknown usage, into the same
   quota-domain ledger. Record the effective model, native session id, input/cache/output/reasoning
   usage, cost when observable, wall time, and terminal outcome. The parent work item becomes
   terminal exactly once.
7. **Dormancy routing.** While fresh evidence says Fable is quota-dormant, route subsequent
   eligible work directly to Opus. Re-probe Fable only at a provider-observed reset boundary or a
   separately configured bounded probe cadence; do not spend every job rediscovering the same 429.
8. **Fail-closed authority.** Model failback moves useful inference capacity only. It does not move
   credentials, provider-family independence, actor identity, claims, leases, reviewer keys,
   adjudication, merge, landing, release, or owner authority.

## Required safety rules

- Fable and Opus on the same Claude account remain one provider family and normally one quota
  domain. They cannot supply two independent acceptance keys.
- A Fable refusal plus an Opus answer is one effective inference result, not two blind reviews.
- Advisory inference may proceed when project policy permits it, but immutable release-review
  credit still requires the project's separately installed authority and exact-subject gates.
- The supervisor must be single-flight across projects sharing the same quota domain and must
  reserve the estimated Opus slice before launch. Capacity telemetry never grants task authority.
- The wrapper must keep a hash-bound terminal receipt for the Fable refusal and the Opus result;
  transcript prose is not a control plane.
- Auth errors, payment/credit errors, lost stdout, cancellation, timeout, process ambiguity,
  malformed JSON, model-identity mismatch, or an Opus quota refusal all stop without another model
  retry.

## Minimum hostile controls before ratification

1. Fable success: Opus launch count is zero.
2. Exact Fable-limit terminal: exactly one Opus launch occurs after durable Fable settlement.
3. Generic 429, auth error, timeout, malformed/lost terminal, and ambiguous process: Opus launch
   count is zero.
4. Crash after Fable settlement but before Opus start: recovery starts at most one Opus child.
5. Crash after Opus start but before settlement: recovery reconciles the existing child and never
   launches a duplicate.
6. Opus terminal identity is absent, multiple, or not exact `claude-opus-5`: zero useful/review
   credit and no tertiary retry.
7. Two repositories share the quota domain: single-flight admits at most one active Opus child.
8. Fable reset is freshly observed: routing returns to Fable on the next new work item without
   interrupting an in-flight Opus child.
9. Review-policy test: Fable-limit plus Opus success cannot satisfy two-provider or two-reviewer
   independence.
10. Idle-path test: no actionable work produces zero Claude calls, regardless of available quota.

## Adoption and acceptance boundary

Each project may propose `ADOPT(FABLE_TO_OPUS_USAGE_LIMIT_FAILBACK_R1, <wrapper SHA-256>, <test
receipt SHA-256>, <installed-policy receipt SHA-256>)` or record a specific `DISTINGUISH`/`REJECT`.
An owner statement or this candidate alone grants no runtime authority.

Before fleet ratification, a distinct adjudicator must bind the exact candidate commit/tree and
artifact manifest, reproduce the hostile controls against the real wrapper, obtain independent
review, and append an exact acceptance or rejection row to `RULINGS.md`. Until then this file is
data for local review only. It authorizes no provider launch, scheduler change, task mutation,
gate opening, project adoption, review credit, merge, release, or account/authentication action.
