# Ruling candidate: exhausted-model failback to Opus R8

Status: **PROPOSED ONLY — NOT YET RATIFIED DOCTRINE OR PROJECT RUNTIME AUTHORITY**

Owner direction: 2026-08-24. Useful Claude capacity must not remain idle merely because the
preferred Fable model has exhausted its model-specific allowance. When exact Fable exhaustion is
proven, eligible unchanged work should continue on exact Opus under the same hard capacity,
single-flight, quality, and acceptance controls.

## Portable decision

Treat model exhaustion and provider/account exhaustion as different states.

- A Fable attempt that satisfies every field of the terminal-exhaustion discriminator below grants
  **zero work, review, or acceptance credit** for that attempt. A generic 429, wrapper text, or
  account-wide capacity rejection is not model-exhaustion evidence.
- If the same immutable work remains authorized, route it forward to an exact Opus packet. Preserve
  the exact ordered core-subject digest, objective, lane-specific role, effort, tool boundary,
  bounded turns/wall clock, output contract, and required independent acceptance. The immutable
  execution contract and the exact core-subject rows must be packet subjects in both lanes. The new
  route id must make the failed Fable ancestry explicit.
- Refresh signed model-free capacity immediately before Opus admission. The observation may be at
  most 300 seconds old (projects may require a smaller bound, never a larger one). Admit only when
  fresh utilization plus active reservations plus the conservative Opus slice estimate is at or
  below the project's hard ceiling in every applicable window.
- Never infer that Fable exhaustion implies Opus exhaustion, or that authentication implies
  capacity. Conversely, never use model failback to bypass stale telemetry, cross-account
  ambiguity, overlap, a live lease, a closed authority gate, or the hard provider ceiling.
- Use the natural scheduler and ordinary one-shot admission path. Model failback grants no manual
  provider-invocation exception.

## Terminal-exhaustion discriminator

Failback is eligible only when one immutable terminal artifact and its durable zero-credit receipt
prove all of the following without conflict:

1. the provider init event names exact `claude-fable-5` for the admitted Fable route and session;
2. the terminal result has `api_error_status=429`, `terminal_reason=api_error`, and exactly one
   attempted turn, with no `route-review-result.v1` verdict or acceptance artifact;
3. the terminal result text is exactly `You've reached your Fable 5 limit. Run /usage-credits to
   continue or switch models with /model.` and the assistant event's exact `error` field is
   `rate_limit`; both fields must appear in the durable receipt, not merely in an unbound artifact;
4. the terminal result reports zero Fable review input and output tokens; wrapper or meter-probe
   overhead earns no work, review, acceptance, or drain credit;
5. every rate-limit event in the terminal artifact is bound and adjudicated. A rejected base-window
   classifier, signed utilization at 100%, or an explicit provider/account exhaustion classifier is
   `HOLD`. A rejected `seven_day_overage_included` event with overage disabled is an overage-
   entitlement rejection, not base-window exhaustion, when the base `seven_day` event is allowed
   or omitted and the separately signed same-domain base-window utilization is fresh and below
   100%. Omission is eligible only with the exact model-scoped 429, assistant `error=rate_limit`,
   one-turn zero-token terminal evidence, and no contradictory or unenumerated classifier event.
   Missing signed corroboration, a rejected base event, or any contradictory or unenumerated event
   is `HOLD`;
6. a separately signed, model-free, same-domain observation no more than 300 seconds old publishes
   utilization, active reservations, the conservative Opus estimate, and their sum for every
   required window. One named assertion must prove each exact sum is less than or equal to 100%; a
   receipt that merely says the base windows are below 100% is incomplete;
7. packet, authorization, session, exact model, artifact path, artifact SHA-256, terminal fields,
   zero-credit disposition, and the unchanged ordered core-subject digest are bound by one durable
   receipt; and
8. the receipt publishes a closed, ordered assertion-name array and an exact matching assertion
   count so another adjudicator can reproduce every predicate without inferring a field mapping.

Generic rate-limit classification is insufficient. Missing, stale, malformed, cross-domain,
contradictory, unenumerated, or ceiling evidence is `HOLD`. Classifier adjudication, signed base
windows, and exact model text are conjunctive.

## Immutable core subjects and execution contract

The Fable and Opus packets may differ only in lane envelope and ancestry attachment. Each packet
must carry the same ordered core subjects, and each row binds normalized relative path, byte length,
and SHA-256. `core_subjects_sha256` is SHA-256 over the canonical closed-key JSON array of those rows.
The Opus packet has one lane-specific continuation-ancestry attachment, excluded from the core
digest. To fit the bounded carrier without dropping evidence, that single closed-key subject binds
the exact Fable exhaustion receipt, zero-credit campaign-hold disposition, terminal Fable lease,
the Fable and capacity opaque domains, capacity-observation and attachment-creation instants,
their reproducible age, utilization/reservation/estimate/sum rows, hard ceiling, and no-overlap
proof. It may not replace, reorder, or alter a core subject. Staleness and domain mismatch are
distinct `HOLD` predicates. Missing, unreleased, overlapping, incomplete-sum, or hash-mismatched
ancestry is also `HOLD`. Because packet publication precedes natural admission, the attachment is
review evidence rather than reusable capacity authority: the scheduler must refresh capacity at
admission and bind the actual observation/preclaim instants in its durable admission receipt.

One core subject must bind this exact execution contract:

- Fable: exact model `claude-fable-5`, role `coordinator`;
- Opus: exact model `claude-opus-5`, role `executor`;
- both: effort `max`, at most 12 turns, at most 900 seconds wall clock, provider tools exactly
  `Read` plus the broker-owned `StructuredOutput`, and result contract `route-review-result.v1`.

The packet hash binds that contract subject before admission. The broker's preclaim and argv receipt
must then prove the lane-specific model/role profile and common effort/turn/tool bounds; the admission
policy binds the wall-clock bound. A packet or argv that omits or differs from any value is `HOLD`.

## Account-domain self-heal

An operator may rotate the authenticated Claude account between the failed Fable attempt and the
Opus continuation. A capacity observer that detects an authenticated account different from the
installed opaque quota domain must fail closed, then invoke one bounded account-domain transaction
instead of repeating an indefinite HOLD.

The transaction requires a closed gate, refuses an unconsumed canary, and proves scheduler
single-flight. It preserves exact opaque-domain, gate, and signed-capacity preimages without raw
identity or credentials; reruns the independently accepted installer against the authenticated
first-party account while closed; requires a different successor opaque domain and a fresh signed
model-free successor observation; reruns accepted hostile controls and returns to closed `SHADOW`;
then atomically receipts actor, policy, predecessor, successor, observation, and verification
identities. Any incomplete or failed step restores every exact preimage and records `ROLLED_BACK`.

Only after commit may the ordinary scheduler retry Opus capacity, preclaim, argv attestation,
one-shot permit, and admission. The self-heal actor has no work-creation, acceptance, release,
credential-mutation, account-selection, or provider-inference authority.

## Liveness and recurrence law

An exact terminal model-exhaustion event is a transition, not a durable global campaign freeze.
The failed route is terminalized with zero credit; the unchanged successor packet is maintained by
the ordinary carrier; and the scheduler advances to Opus on its next eligible natural wake.

Repeated identical account-domain mismatch HOLDs are a control-loop defect when an authorized
account rotation has already occurred. The scheduler must attempt the bounded self-heal once per
freshly observed mismatch, receipt success or rollback, and then either continue or emit the changed
blocker. It must never silently refresh timestamps while leaving the causal mismatch untouched.

## Invariants preserved

- exact model identity: the successor is Opus, never an alias or automatic substitute;
- exact immutable subjects and no laundering of failed Fable output;
- strict serial order and one quota-domain owner for the full child lifetime;
- zero discretionary reserve where locally authorized, while retaining the hard 100% ceiling and
  conservative request reservation;
- fresh account-bound capacity, no cross-account telemetry reuse, and no raw identity persistence;
- closed-by-default gate, one-use canary, bounded execution, validated terminal output, and exact
  terminal lease disposition through the canonical writer; a `retired-by-directive` receipt proves
  terminal retirement but must not be described as a stronger deterministic-release mechanism;
- independent acceptance, installer, preview, rollback/reinstall, cadence, and adoption gates remain
  separate and fully required.

## DNG production evidence (non-portable, no fleet adoption credit)

On 2026-08-24 DNG proved exact Fable exhaustion and zero-credit hold disposition, then published the
unchanged four-subject Opus continuation. Its first natural wake refused an authenticated-account /
installed-domain mismatch. A forward self-heal passed 8 controls, including exact rollback and
open-gate refusal; the next natural wake committed rotation, observed signed 4% five-hour and 83%
seven-day utilization, preclaimed and attested exact Opus, and launched exact `claude-opus-5` at
maximum effort. Exact output and consumption were persisted and the canonical writer retired the
terminal session by directive (terminal retirement, not deterministic-release proof). This
initial production-path review returned `REVISE` with nine actionable findings. Later immutable
candidate reviews were distinct subjects: R1 returned 3, R2 returned 6, R6 returned 5, and R7
returned 6 actionable findings. R5 was carrier-rejected before admission with zero provider launch,
so it was not an independent Opus review. Each exact count and receipt hash is bound in the R8
evidence bundle; none is acceptance credit. Adverse verdicts prove quality preservation: Opus
capacity was spent without laundering Fable failure or weakening review.

The bound `receipts/dng-opus-model-failback-20260824.json` proves only that DNG transition, never
portable acceptance or another project's adoption.

## Required acceptance and project response

Before ratification, a distinct adjudicator must bind the candidate commit/tree and reproduce the R8
matrix and execution contract in `test-opus-model-failback-r3-controls.ps1`. Controls cover positive
failback; every missing/conflicting discriminator; classifier enumeration; base and overage
rejections; rollback/open gate; isolated stale, cross-domain, overlap, live-lease, malformed-output,
and ancestry failures; same-domain successor; exact/surplus ceiling; core order/replacement;
execution drift; and unconsumed versus consumed canaries with zero authority. Every mutation must be
executed. The suite compares an externally supplied core digest, proves changed-row and actual
permuted-row negatives, and validates shipped ancestry freshness, both opaque domains, and
no-overlap. The adjudicator also verifies the terminal Opus receipt.
Ratification must be appended to `RULINGS.md` and reach canonical `master`.

Each project then publishes one current `ADOPT`, `DISTINGUISH`, or `REJECT` disposition with its own
policy, scheduler, account-domain transaction, tests, rollback, natural production proof, and owner
authority. This candidate itself grants no provider launch, account rotation, gate opening,
installation, merge, release, or adoption authority.
