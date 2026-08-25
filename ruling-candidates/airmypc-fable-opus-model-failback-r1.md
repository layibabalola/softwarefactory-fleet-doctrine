# AirMyPC exact-model Fable-to-Opus failback strategy

**PROJECT PROPOSAL / ZERO RUNTIME AUTHORITY / NOT AN ACTIVATION RECEIPT.** The owner directed
AirMyPC to consume useful Opus inference when the exact Fable model is exhausted instead of leaving
eligible paid capacity idle. This candidate publishes the resulting strategy for fleet
adopt-or-distinguish review. It does not claim that the current machine can launch Opus.

## Three independent gates

Every Claude dispatch evaluates three facts independently:

1. **Exact-model capacity:** availability of the requested exact model on the observed
   account/plan/quota domain and endpoint.
2. **Project admission:** the project-local immutable launcher, policy, manifest, receipt, and
   semantic-health floor.
3. **Execution authority:** a current bounded role/subject assignment with reviewer independence
   and an unconsumed exact launch authority.

One green fact never substitutes for another. In particular, `IMMUTABLE_BOOTSTRAP`, missing work,
or missing authority is not provider exhaustion; model visibility is not capacity; and provider
capacity grants no project role or release key.

## Typed routing ladder

The router records exact failure classes rather than a generic "Claude unavailable" state:
`MODEL_QUOTA_EXHAUSTED`, `ACCOUNT_QUOTA_EXHAUSTED`, `MODEL_ENDPOINT_UNAVAILABLE`, `AUTH_REFUSED`,
`PROJECT_ADMISSION_DENIED`, `NO_ACTIONABLE_WORK`, `AUTHORITY_MISSING`, and `UNKNOWN`. Unknown,
ambiguous, stale, conflicting, or malformed evidence fails closed.

- A provider-reported exact-model quota refusal suppresses only that exact model until its durable
  reset instant. The controller does not repeatedly probe it. An account-wide refusal suppresses
  every model proved to share that quota domain; a label switch within the same profile is never
  treated as new quota.
- While `claude-fable-5` is suppressed, a ready real-work ticket prefers exact
  `claude-opus-5 --effort max`. The router does not attempt Fable first merely to reproduce a known
  refusal.
- Opus requires fresh positive exact-model capacity evidence at the dispatch boundary. A stale
  prior success permits one ticket-local capacity check only after the real ticket, project
  admission, recusal, and authority prerequisites are otherwise ready. Idle heartbeats never launch
  inference merely to test capacity.
- One quota domain is single-flight. No concurrent Fable/Opus attempts race the same allowance, and
  a refusal or terminal consumes only the allowance its typed receipt defines.
- The work ticket binds exact project, role, subject path/hash, context capsule, requested model and
  effort, account/plan fingerprint without credentials, quota domain, expiry, turn/context bounds,
  artifact destination, and terminal-receipt path. A provider runner may perform only that ticket.
- Requested-model credit requires the same-run authoritative effective model. A downgrade,
  alternate model, missing init, ambiguous terminal, or model mismatch earns zero Opus credit and
  cannot silently continue under another identity.

## Productive use, not artificial burn

The economic objective is to minimize **eligible-idle paid capacity** while completing real factory
work. The router may not create filler prompts, replay terminal work, split a task to inflate usage,
weaken review topology, or spend tokens after a useful terminal. It measures by exact model and
quota domain:

- eligible-idle minutes while actionable admitted work was queued;
- time from typed Fable exhaustion to productive Opus ignition;
- productive terminals, refused terminals, tokens, and utilization for exact Fable and Opus;
- stale-capacity checks, model mismatches, admission denials, and authority denials;
- accepted evidence converted to landing/publication, so inference volume alone is never health.

An Opus job is productive only when its exact work receipt joins one authoritative ignition and one
ordered terminal, and its result enters the required independent review/adjudication chain. Raw
stdout, init events, `DISPATCHED`, or usage movement alone earn no work credit.

## Reset and failback

Fable reset evidence does not preempt a healthy live Opus slice, transfer its claim, or invalidate
its work. At the next new slice boundary, the router refreshes both exact models independently and
selects the best eligible profile for the required role under the current policy. Fable may resume
its preferred work only from positive post-reset evidence; the mere passage of the reset timestamp
does not unsuppress it. Opus remains eligible for later work when its own capacity, admission, and
authority are green. Same-provider Fable and Opus remain one Anthropic independence class and never
supply both acceptance keys.

## AirMyPC evidence at submission

The local structured availability state
`.claude-state/coordination/software-factory/claude-model-availability-current.json` is exact
`BA585D40E7920E7DA3C79C3807645A8270900C8B3A98F0564169108BC26AA56C` / 2,217 B. It records:

- exact `claude-fable-5` as `quota_exhausted`, HTTP 429, suppressed until provider reset evidence
  no earlier than `2026-08-28T06:00:00Z`;
- exact `claude-opus-5` as last observed `available_warning` at utilization `0.76`, but stale after
  `2026-08-24T00:19:02.165Z`; and
- independent project admission `IMMUTABLE_BOOTSTRAP`, so neither model was lawfully launched from
  that observation.

AirMyPC has now frozen a no-execution admission-repair author packet at
`.claude-state/coordination/software-factory/airmypc-claude-opus-admission-r1-author.md`, exact
`8DFD7CBCF97539650066B118DA3C74BED56A0F202CCEDB9F2B9EA3A18427C83F` / 5,116 B, with matching
machine receipt `13A722D8E574A6639A65214ADBAB7959418E866589D47439B94BA9E1B7EFC6F9` / 3,190 B. It adds the
missing v2 immutable-install receipt/pin path but remains under fresh review and authority `NONE`.

The first real Opus target is not a probe: Fleet PR #31 R3 exact-two-file review packet
`6A357ACBF75479BDAED9D91DA313FF5785BBAEEEDC7AA790CE93F36FD93A285C` / 10,593 B plus JSON
`F3701F694C8F8B83C41DD2AC9B5101C037CE06CB3969CE296464E2E55739E4D9` / 11,474 B is
`AUTHOR_COMPLETE_REVIEW_REQUIRED` and reserves its fresh non-author review for exact
`claude-opus-5`. Reservation is actionable-work evidence, not capacity, admission, or launch
authority.

## Activation boundary

Runtime use requires, in order: accepted admission-repair review and distinct adjudication; a
separate exact one-attempt ProgramData immutable-install authority and verified install receipt; a
separate current gate/admission ruling; a still-live actionable ticket; a dispatch-local Opus
capacity rebind; and an unconsumed exact launch authority naming the sole runner and terminal path.
Any red step stops without probing the suppressed Fable model or silently substituting another
model. This proposal grants none of those steps, no credential or billing mutation, no task enable,
no provider call, no doctrine ratification, no Git/release authority, and no `RUN_GO`.
