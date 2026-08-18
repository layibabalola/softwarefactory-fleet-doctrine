# Fleet provider capacity governor

Status: **CANDIDATE — NO LIVE ADMISSION, ROUTING, OR AUTHORITY GRANT**

Date: 2026-08-18 CT

This specification converts the fleet's repeated provider-exhaustion incidents into one
provider-neutral control contract. It preserves project-local authority, exact-model review gates,
and independent-provider acceptance while preventing unattended orchestration from consuming the
capacity needed to finish or review product work.

The candidate does not activate a scheduler, change a project's model, or authorize a provider.
Each project must adopt it through its own ruling, adapter, tests, and receipts.

## Decision: one doctrine repository, a separate runtime boundary

`softwarefactory-fleet-doctrine` remains the single policy and evidence bus. Do not create a second
telemetry doctrine repository. This repository owns:

- versioned schemas and semantic laws;
- project-authored, append-only aggregate telemetry shards;
- portable traps, receipts, and ratified rulings;
- conformance fixtures and a reference decision engine.

Git is not a real-time lock service. Live admission, process fencing, usage polling, and crash-safe
leases run outside Git in a host-local supervisor. If one quota domain is intentionally shared by
multiple hosts, a later separately reviewed fleet broker service may coordinate that domain. Its
runtime store is operational state, not a second doctrine bus. Raw transcripts, credentials,
account identifiers, prompts, customer data, and process command lines never enter doctrine.

## Quota-domain identity

Admission is keyed by a **quota domain**, not repository, lane, provider name, or machine:

`provider / account-fingerprint / organization-or-plan-scope / transport-scope`

Two projects using the same authenticated account and shared provider limit have the same quota
domain. Two deliberately separate accounts have different quota domains and may run concurrently.
Models that share one subscription window remain one domain even when their model names differ.

The published `quota_domain_id` is an opaque value such as
`anthropic/hmac-sha256:7f...`. The local supervisor derives it with a fleet-local secret from the
provider's stable account or organization identifier. When no stable identifier is observable, the
owner supplies a stable local alias; the raw alias is never published. Hashing an email, API key, or
access token without a secret is prohibited.

## Control-plane law

Provider inference is for judgment and production, not orchestration plumbing.

The following operations must be deterministic and consume zero model turns:

- lease acquisition, renewal, expiry, and fencing;
- process liveness and process-tree correlation;
- registry comparison and duplicate suppression;
- idle-input fingerprinting and addressed-work detection;
- usage collection, reset parsing, reservation arithmetic, and retry scheduling;
- hashing, evidence packet creation, test execution, receipt framing, and telemetry compilation.

A model may adjudicate ambiguity, but its absence cannot create an unbounded ignition loop. Unknown
identity, capacity, or ownership fails closed for unattended work and remains visible to the owner.

## Admission state machine

Every inference-bearing root session follows one idempotent sequence:

`QUEUED -> STARTING -> CLAIMED -> RUNNING -> CHECKPOINTED | TERMINAL -> COOLDOWN`

`CAPACITY_BLOCKED`, `IDENTITY_BLOCKED`, and `AMBIGUOUS` are non-green terminal admission states.

The idempotency key is `(quota_domain_id, lane_or_role, seat_epoch, attempt_id)`. Before process
launch, the supervisor atomically creates a claimant record containing the seat epoch, process id,
process start time, requested provider/model/effort, task, and bounded startup expiry. A new process
cannot launch while a nonterminal claimant exists. A launch attempt receives cooldown from launch,
not from its first successful model response.

An inference lease is live only when all of these agree:

1. lease freshness;
2. process id and immutable process start time;
3. requested and observed provider/model identity;
4. seat epoch and registered session identity;
5. recent self-produced transcript or terminal progress when the transport exposes it.

A fresh file written by an orphan watcher is never process liveness. Watchers re-read registration
and owner-process identity every poll and exit on mismatch. An ambiguous process is not killed and
does not authorize takeover; it produces a durable blocker.

The frozen admission snapshot carries process ID/start time, `live`/`dead`/`ambiguous` process
status, requested and observed provider/model, seat epoch, registered and observed opaque session
hashes, registry status, and progress status for every claimant record. A dead process is not made
live by a fresh lease. A live process with a stale lease, or any live identity/registry/session
mismatch, denies takeover with a non-green reason. A `STARTING` process remains fenced through its
bounded startup expiry even before observed identity is available.

## Default admission policy

The safe initial default is one unattended inference-bearing root session per quota domain. The
priority order is:

1. owner foreground work;
2. already-booked independent verifier or release gate;
3. bounded product implementation;
4. hub adjudication with actionable work;
5. maintenance and experiments.

Priority affects queue order. It does not authorize killing a live model mid-write, stealing a
claim, or bypassing a required reviewer. Parallelism above one requires an explicit project policy,
a measured quota envelope, distinct work, and a completion reserve.

Before unattended admission, the supervisor requires:

- a fresh provider usage observation or an explicit `capacity_unknown` result;
- all outstanding reservations for the quota domain;
- a bounded session estimate derived from completed comparable slices;
- a reserve for foreground work and one required independent review;
- actionable work whose deterministic input fingerprint changed since the last idle result.

The policy sets `capacity_observation_max_age_seconds`. Capacity observations later than the frozen
snapshot or older than that bound deny admission. Every request carries the current deterministic
idle-input fingerprint and the prior `IDLE_SKIPPED` fingerprint (or `null` when no prior idle result
exists). Identical current and prior fingerprints deny unattended admission; an owner override does
not convert unchanged idle input into work.

The initial reserve may be 30% of a provider window, but it is a canary value, not doctrine truth.
Projects tune it from measured windows. Unknown capacity blocks unattended sessions by default.
Foreground override is explicit, visible, bounded, and never presented as ordinary automatic
admission.

Capacity failure supersedes ordinary exponential backoff. A provider reset observation clears only
the backoff caused by that same quota event. Recovery happens without spending an inference probe.

### Pre-reset containment barrier

The repair must be installed while the provider is unavailable. Waiting for reset creates the same
race the governor exists to prevent. Before the next capacity window opens:

1. enumerate every unattended launcher for the affected quota domain and disable only that exact
   allowlist;
2. prove there is no surviving inference-bearing launcher process (desktop UI and authentication
   helpers are not inference credit);
3. keep the automatic launch gate `closed` while installing the supervisor, adapters, and tests;
4. require every re-enabled launcher to enter through the same pinned supervisor entrypoint and
   reject direct provider invocation structurally;
5. run frozen reset, concurrency, refusal, orphan, and no-work controls with the provider still
   unavailable or through a no-inference fake adapter;
6. move the gate from `closed` to `open` only after the exact supervisor build and policy hash pass;
7. re-enable one bounded canary launcher, not the whole fleet, and preserve the completion reserve;
8. automatically return the gate to `closed` on identity ambiguity, duplicate claimant, telemetry
   loss, quota refusal, or a direct-launch bypass.

A reset observation updates capacity state only. It never changes `automatic_launch_gate`, enables a
scheduled task, creates a process, or drains queued work by itself.

## Quality-preserving task routing

Savings come from removing duplicate work, shrinking irrelevant context, and moving mechanical
work out of model loops. They do not come from silently weakening the verification bar.

- Exact-model, exact-effort, named-authority, or independent-provider requirements remain binding.
- If the required profile is unavailable, work queues or fails closed; it is not silently credited
  to another model.
- Premium profiles are reserved for architecture, ambiguous safety/correctness reasoning, hard
  defect localization, adversarial review, and final ratification.
- Bounded implementation from a frozen plan may use a separately admitted implementation profile.
- Health checks, idle heartbeats, status derivation, and receipt formatting use deterministic code.
- A budget boundary produces `CHECKPOINTED/WIP`, never `PASS`, `APPROVE`, or completion credit.

Routing changes require frozen replay and blinded non-inferiority evidence. Provider/model/effort,
adapter, host boundary, and effective backend remain part of the exact role-cell identity defined in
`specs/provider-model-benchmarking.md`.

## Context and token discipline

Each session receives a mechanically generated **evidence capsule** instead of broad historical
orientation. The capsule contains current derived state, exact addressed work after the lane cursor,
subject hashes, controlling rulings, protected invariants, focused diffs, bounded test output, and
pointers to raw evidence. It is content-addressed and size-measured. Required raw evidence remains
available for targeted expansion.

Common requirements:

- spill oversized tool output to a content-addressed local artifact and return a digest, error
  summary, hash, and path;
- checkpoint after major task phases and before provider-specific context pressure;
- preserve the same functional prompt and required evidence across a compacted continuation;
- set a bounded number of agent/tool turns for unattended invocations;
- never truncate required evidence silently or treat a context/budget stop as a verdict;
- record input, cached-input, cache-creation/write, reasoning, and output tokens separately when
  observable; record `unknown` rather than inventing a value.

### Provider adapters

| Provider family | Adapter requirements |
|---|---|
| Anthropic / Claude | One account-wide lease; parse session, five-hour, and weekly exhaustion; use bounded resumable turns; preserve exact Opus/Fable identity where required; scheduled lanes yield to foreground and review reserve. |
| OpenAI / Codex | Record input, cached input, output, and reasoning where exposed; checkpoint/compact at major milestones; select model and effort only through role evals; keep long-lived automation behind the same quota-domain admission and evidence-capsule rules. |
| Moonshot / Kimi | Read provider-reported plus estimated context; configure bounded `max_steps_per_turn` and transient attempts; use `/usage` and milestone `/compact`; a secondary model is a separately evaluated role cell, never automatic review credit. |
| xAI / Grok | Use a stable `x-grok-conv-id` or `prompt_cache_key` where the transport supports it; keep the prompt prefix append-only; record cached and reasoning tokens and exact cost where exposed; bound `max_turns`; treat CLI fields unavailable from the API as `unknown`. |
| Other providers | Implement the same identity, usage, terminal, and refusal contract. Missing fields remain `unknown`; unknown capacity blocks unattended work until project policy explicitly proves a safe bound. |

Provider-side caching changes latency and cost but does not make unbounded growing histories safe.
Cached tokens remain traffic and may count toward limits. Stable prefixes are useful; compact evidence
capsules and bounded turns are still required.

## Telemetry contract

Raw usage remains project-local. Each project compiles append-only events conforming to
`schemas/provider-usage-event-v1.schema.json`. Events bind:

- project, host cell, quota domain, provider, transport, model, effort, actor, role, and task;
- admission request/decision, lease epoch, process-correlated start, checkpoint, and terminal;
- exact/estimated/unknown token and monetary observations;
- capacity window, utilization, reset, reservation, and refusal classification;
- useful outcome such as completed slice, accepted review, blocker found, or idle/no-work.

`IDLE_SKIPPED` is a proof-bearing event: it requires the deterministic input fingerprint and
explicit zero request, input, cached-input, cache-write, reasoning, output, and tool-call counters.
Missing, `unknown`, or nonzero counters cannot be published as idle/no-inference.

Doctrine receives only opaque identities and derived events under the existing one-writer project
shard law. Metrics are diagnostic and never authority. Live admission reads local authoritative
state, not Git metrics. A telemetry outage cannot turn into an admission success.

The reference CLI loads and enforces both Draft 2020-12 schemas before semantic evaluation. Schema
absence, validator absence, invalid format, extra properties, or malformed claimant state fails
closed. The CLI remains a frozen decision/telemetry conformance tool only: it does not inspect live
processes, acquire leases, mutate the automatic gate, or launch a provider. Projects populate the
snapshot from their separately reviewed host-local supervisor.

## Evidence campaign and non-regression bar

Rollout is staged:

1. **Shadow:** compile events and decisions without changing launches.
2. **Containment:** enforce single-flight claims, orphan exit, cooldown-from-launch, and model-free
   idle checks. These do not alter prompts or role assignments.
3. **Capacity:** enforce quota-domain admission and reserve while preserving exact required profiles.
4. **Context:** introduce evidence capsules and bounded continuations behind frozen replay.
5. **Routing:** change model/effort only after role-specific blinded non-inferiority trials.

The campaign must include these negative controls:

- two repositories request the same account simultaneously: exactly one unattended job starts;
- two intentionally different account fingerprints: both may start within their separate policies;
- dead process with a fresh lease: not live;
- live process with a stale lease: degraded, not duplicated;
- orphan watcher or registry mismatch: exits within one poll;
- launch with no registration outcome: remains fenced through startup grace and cooldown;
- empty or partial provider output: cannot trigger an ignition loop;
- quota refusal: no automatic model process starts before reset observation;
- no actionable dispatch: zero model calls and a deterministic idle receipt;
- ambiguous identity: no kill, no takeover, durable blocker;
- budget/context boundary: checkpoint only, never a green verdict;
- exact-model review unavailable: queues without downgrade;
- frozen replay: no missed blocker, no weaker severity, no dropped work, and identical authority
  boundaries compared with the accepted baseline.

Measure usage per independently accepted slice, requests per useful terminal, median/p90 context,
cached and uncached input, output/reasoning, duplicate launches, idle model calls, time-to-recovery,
review findings, rework, rollback, and regression rate. Quality and authority are hard gates; token
savings cannot average them away.

## Publication by projects

Each adopting project publishes only its own `specs/<project>.md` and its own metrics shard. A
portable finding must name the provider adapter/version, quota-domain class, frozen policy hash,
sample count, before/after usage, quality outcomes, falsifiers, and evidence hashes. Provider account
identifiers and credentials remain local.

A project may report `SHADOW_PASS`, `CONTAINMENT_PASS`, `CAPACITY_PASS`, or `ROUTING_PASS` only for the
stage it actually proved. Local implementation without remote doctrine publication remains
`FIXED-LOCALLY-PENDING-DOCTRINE` under the existing doctrine seam law.

## Provider documentation used for the adapter baseline

- Anthropic: <https://support.claude.com/en/articles/14552983-models-usage-and-limits-in-claude-code>
  and <https://support.claude.com/en/articles/8664678-change-the-model-effort-and-thinking-settings>
- OpenAI: <https://developers.openai.com/api/docs/guides/latest-model>
- Moonshot/Kimi: <https://www.kimi.com/code/docs/en/kimi-code-cli/configuration/config-files.html>
  and <https://www.kimi.com/code/docs/en/kimi-code-cli/guides/sessions.html>
- xAI/Grok: <https://docs.x.ai/developers/advanced-api-usage/prompt-caching>,
  <https://docs.x.ai/developers/advanced-api-usage/prompt-caching/usage-and-pricing>, and
  <https://docs.x.ai/developers/tools/tool-usage-details>

Provider documentation can change. Project adapters bind their behavior to exact CLI/API versions
and fresh receipts rather than treating this reference list as runtime proof.
