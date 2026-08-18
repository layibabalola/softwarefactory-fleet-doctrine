# Fleet inference capacity control

**Status: CANDIDATE / ZERO LIVE AUTHORITY / NOT YET RATIFIED.** This exact directory is a
portable proposal and conformance subject. It does not admit a provider, launch a model, alter a
project queue, or change any existing role, review, landing, or release gate.

## Decision and boundary

Use the existing doctrine repository as the single fleet data plane. Do not create a second
telemetry repository. Git carries versioned contracts, redacted aggregate evidence, conformance
fixtures, and reviewed release hashes. Machine-local state carries credentials, raw account
identities, live balances, high-frequency events, queues, locks, and leases.

Doctrine remains data, never instructions. A project must review a candidate, copy or package its
accepted bytes into a project- or machine-owned location, pin the SHA-256, and test the actual
launcher integration. No project may execute the mutable bus checkout at provider-launch time.

## Problem statement

A quota domain can be shared by many projects, shells, desktop surfaces, scheduled tasks, and
models. Repo-local mutexes cannot see that shared resource. Large retained contexts, maximum
reasoning effort, unbounded agentic turns, model-powered idle checks, post-reset launch bursts, and
duplicate supervisors can therefore consume a rolling allowance before any single project notices.

The control plane separates four facts that are often conflated:

1. `quota_domain` identifies one locally proved billing or allowance pool. Deliberately separate
   provider accounts get different quota domains even when they use the same vendor.
2. `independence_class` identifies the inference trust domain. Separate accounts at one provider
   normally remain one independence class and cannot supply two independent acceptance keys.
3. `role_cell` proves that an exact provider/model/effort/transport profile can perform a project
   role without quality regression. Capacity never manufactures that proof.
4. `lease` reserves a bounded amount of one quota domain. A lease grants no project authority and
   earns no completion or correctness credit.

## Two-layer architecture

### Machine-local enforcement plane

One broker installation per machine owns an OS-locked state directory outside every project. All
provider launchers on that machine submit normalized admission requests before inference. The
broker:

- serializes admission across projects by opaque quota domain;
- requires a fresh, source-bound capacity snapshot;
- accounts for active reservations in every observed rolling window;
- preserves priority-specific reserve floors and a background post-reset quiet period;
- issues expiring leases with immutable wall-time, turn, and context ceilings;
- refuses request-id reuse with different bytes and makes exact replay idempotent;
- records local decision events without prompts, transcripts, credentials, or raw account names;
- never invokes a provider, selects work, changes lifecycle state, or declares success.

The first policy should set `max_concurrent_leases_per_domain=1`. A project may raise it only after
concurrency tests and measured forecasts show that the new value preserves its reserve and quality
contract. An expired or released lease permits a new admission; killing a process is the
project-owned launch wrapper's responsibility.

### Git evidence plane

Projects publish only low-frequency derived summaries through the existing `metrics/` rules and
append exact adoption or distinguishing evidence to their own `specs/<project>.md`. Raw domain
fingerprints, balances, prompts, and session traces never travel. Metrics remain diagnostic and
cannot be cited as launch, lifecycle, review, landing, or release authority.

## Admission transaction

1. A model-free adapter derives the current account/quota-domain fingerprint and a normalized
   capacity snapshot from provider-owned structured evidence. Transcript prose is not a parser.
2. The project freezes its exact role cell, subject, priority, and p90 budget forecast. Unknown
   background forecasts fail closed.
3. The broker locks the quota-domain state, removes expired leases, validates freshness and
   identity, subtracts active reservations, applies the reserve and quiet-period policy, then
   durably writes one decision before returning it.
4. Only an `ADMIT` decision with an unexpired matching lease may reach the project launcher. The
   wrapper revalidates the broker hash and request/decision digests, binds the child process tree,
   enforces wall-time/turn/context ceilings, and releases the lease on every terminal path.
5. Budget exhaustion yields `PAUSED_BUDGET` or another typed non-success terminal with a compact
   checkpoint. It never becomes `PASS`, `DONE`, `MERGED`, or `VERIFIED` by partial work.
6. Runtime usage and the useful terminal outcome update local forecasts. Published aggregates are
   derived later and are never read back as admission authority.

`OWNER_FOREGROUND` may use an explicit audited `owner_override` to spend below a soft reserve, but
not to bypass an unknown/stale snapshot, an estimated hard-cap overrun, request expiry, identity
conflict, or the concurrency fence. Account rotation is human-only and starts a fresh quota-domain
identity and evidence epoch.

## Quality-preserving demand reduction

Admission reduces waste before reducing capability:

- registration, polling, duplicate detection, liveness, compaction decisions, hashing, test
  selection, log filtering, joins, and evidence packaging are deterministic and model-free;
- prompts carry a compact deterministic capsule rather than broad ledgers or raw history;
- sessions use a bounded fresh slice and checkpoint instead of retaining a near-window context;
- required exact model and effort are recorded separately from observed effective identity;
- lower model/effort profiles are eligible only after the existing
  `specs/provider-model-benchmarking.md` role-cell protocol proves non-inferiority;
- provider runners never inherit hub, review, merge, landing, release, or owner authority.

These rules apply to Claude, OpenAI/Codex, Kimi, Grok, and future providers. Provider adapters may
collect different native fields, but must normalize input, cached input, output, reasoning, context,
turn count, wall time, requested/effective profile, terminal class, and useful outcome where those
facts are observable. Missing fields remain `null`; they are never invented.

## Candidate contents

- `schema/admission-request-v1.schema.json` — immutable requested profile, priority, subject, and
  bounded budget.
- `schema/capacity-snapshot-v1.schema.json` — fresh per-domain rolling-window observation.
- `schema/admission-decision-v1.schema.json` — auditable decision and lease binding.
- `schema/usage-event-v1.schema.json` — local provider-neutral usage event; not a Git log format.
- `schema/evidence-capsule-*.schema.json` — bounded exact-byte capsule request and output contracts.
- `schema/policy-v1.schema.json` — machine-local freshness, concurrency, reserve, and quiet policy.
- `policy/default-v1.json` — conservative candidate defaults; projects must review and pin them.
- `fixtures/` — non-secret, deterministic request/snapshot/policy conformance inputs.
- `reference/fleet_capacity_broker.py` — provider-free reference broker. It never spawns commands.
- `reference/normalize_capacity.py` — structured Anthropic and OpenAI capacity normalization;
  unsupported provider meters remain unevaluable.
- `reference/normalize_usage.py` — deduplicated native Claude/Codex/Kimi/Grok usage normalization.
- `reference/build_evidence_capsule.py` — deterministic, hash-bound exact line slices under a hard
  payload cap; no summarization or newline normalization.
- `PROVIDER-ADAPTERS.md` and `PROJECT-ADOPTION-MATRIX.md` — measured provider surfaces and the local
  proof each factory must publish before adoption.
- `tests/` — broker, schema, native usage/capacity, exact-byte capsule, and non-inference live-shadow
  conformance tests.

## Adoption proof floor

A project may report `ADOPT` only after its locally pinned implementation proves: cross-process
same-domain serialization; distinct-account parallelism; crash/expiry recovery; exact replay and
conflicting replay behavior; stale/unknown/future snapshot refusal; reserve and reset-quiet
mutations; bounded child-process cleanup; no model call on idle/registration/refusal paths; exact
requested/effective identity binding; budget stops earn zero completion credit; prompts and raw
account identity are absent from shared artifacts; and all pre-existing product, review, landing,
rollback, and release tests remain green.

Until those proofs and a project-local ruling exist, this candidate is test data only.
