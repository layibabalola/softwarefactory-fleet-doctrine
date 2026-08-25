# Fable-exhaustion to Opus failback R1

Status: **OWNER-DIRECTED FLEET DOCTRINE PROPOSAL — ROUTING/PREPARATION AUTHORITY ONLY; NO PROVIDER
CALL, TASK ENABLEMENT, REVIEW CREDIT, VOTE, RATIFICATION, OR PROJECT ADOPTION GRANT.** Projects
consume this proposal as data under the fleet adopt-or-distinguish law. A project must separately
adopt and activate the resulting control before it can launch work.

The owner identified unused Claude included-plan allowance as an economic defect: useful paid
capacity must not be preserved until expiry merely because Fable is unavailable. The proposed fleet
default is therefore **Fable first, Opus failback second** for useful, otherwise eligible
independent-review or advisory demand. This is model-pool routing inside the existing Anthropic quota
domain; it does not create a second acceptance key or weaken role separation.

## Utilization objective

When useful provider-eligible backlog exists, the controller targets an increase of **at least five
percentage points of Claude included-plan utilization per rolling hour**. This is a minimum useful-
work throughput objective, not permission to manufacture work, inflate prompts, repeat unchanged
reviews, or spend metered credits. Measurements must compare fresh samples from the same opaque
account, quota domain, usage window, and provider counter; a reset, missing sample, identity change,
or non-comparable counter yields `UTILIZATION_RATE_UNKNOWN`, never an invented rate.

The controller samples at least every 15 minutes and records the rolling slope. If the observed
useful-work slope is below five percentage points per hour, it must immediately prepare and dispatch
the next lawful bounded job rather than wait for another general review cycle. Fable remains first
choice while usable. Once typed Fable exhaustion or unavailability is established, the next eligible
job is assigned to Opus without an additional idle interval. While the rate remains below target,
Opus stays preferred for subsequent eligible jobs until the combined Claude included-plan slope
recovers or the allowance is exhausted.

Where trustworthy reset timing exists, the pacing target is the greater of five percentage points
per hour and the rate needed to consume otherwise-discretionary allowance before reset, after
reserving only the observed capacity needed to finish admitted work and publish receipts. The target
is not a hard spend command: foreground priority, single-flight quota leases, exact-model identity,
job-specific authority, custody, and completion reserve remain mandatory.

If the target cannot be met, the controller emits `UTILIZATION_TARGET_BLOCKED` with the measured
rate and exact typed blocker, such as `NO_ELIGIBLE_USEFUL_WORK`, `FABLE_STATE_UNKNOWN`,
`OPUS_START_AUTHORITY_MISSING`, `ENDPOINT_UNAVAILABLE`, `QUOTA_LEASE_HELD`, or
`COMPLETION_RESERVE_ONLY`. It then prepares the smallest fresh useful eligible subject it is already
authorized to prepare. A blocked receipt is not successful utilization and must remain visible until
the blocker changes.

## Typed failback trigger

The router may enter `FABLE_EXHAUSTED` only from one of these retained observations:

1. provider-emitted machine-parseable Fable usage or credit exhaustion, including the captured
   `You've reached your Fable 5 limit` class documented in `TRAPS.md`;
2. fresh trusted usage telemetry showing the Fable pool unavailable through its reset boundary;
3. an explicit owner statement that the Fable allowance is exhausted for the current window; or
4. a fresh Fable endpoint response that the exact required model is unavailable while the same
   account remains identity-valid.

Silence, an idle feed, a missing response, stale telemetry, a disabled task, a process count, plan
identity, Desktop interactivity, or a successful authentication check is not exhaustion. Unknown
state is `CAPACITY_UNKNOWN`, never an invented zero. The trigger receipt records the evidence class,
observation time, reset boundary when exposed, opaque quota-domain identity, and raw-evidence hash;
it stores no credentials, account identifiers, or raw transcript.

## Eligible Opus failback work

After `FABLE_EXHAUSTED`, the broker selects the next changed, useful, authority-eligible demand whose
role cell permits Opus. Preferred work is an exact-byte independent review, adversarial audit,
architecture or safety adjudication, or hard defect localization on a frozen subject. Mechanical
health checks, status narration, receipt formatting, unchanged input, fabricated review demand, and
work created only to consume tokens remain model-free or `IDLE_SKIPPED`. A project must not reopen
or replay terminal attempts, reuse consumed one-shot authority, or treat this doctrine publication
as a proposal-specific start receipt.

If no eligible demand exists, the coordinator prepares the smallest fresh useful provider-eligible
subject and reports the exact missing start condition. It must not report unused Claude capacity as
healthy utilization and must not manufacture busywork. Preparation is provider-free; the first Opus
process still waits for the selected job's ordinary project-local authority, immutable subject,
custody, independence, and admission checks.

## Opus launch and stop contract

1. Request the exact hub-configured Opus model identity; retain requested and effective model IDs.
   A moving alias, role label, or prompt self-report earns no exact-model credit. Model mismatch or
   unavailability terminates without silent substitution.
2. Acquire the single full-child-lifetime lease for the Anthropic quota domain. Fable, Opus, and
   Sonnet do not overlap on the shared account unless separately proven quota domains and a reviewed
   concurrency policy exist.
3. Recheck demand, authority, identity, capacity, completion reserve, foreground priority, and all
   project-specific holds in the final launch transaction. The economic directive does not bypass a
   closed task, consumed attempt, quorum requirement, reviewer blindness, or candidate custody.
4. Admit one bounded Opus job with exact subject hash, role, effort, launcher digest, maximum turns,
   and cumulative token ceilings. There is no automatic retry, continuation, API-key fallback,
   metered-credit purchase, account switch, UI automation, or lower-model fallback.
5. Preserve enough observed allowance to finish the admitted job and publish its terminal receipt;
   do not reserve discretionary capacity merely to keep the meter nonzero. A budget stop produces
   `CHECKPOINTED/WIP`, never `PASS`, `APPROVE`, or review credit.
6. On terminal completion, capacity refusal, ambiguity, or custody drift, release the lease, record
   the typed outcome, and stop. When Fable later has fresh capacity, new demand returns to Fable-first
   routing; an already admitted Opus job is not preempted mid-write.

## Required utilization evidence

Every failback decision emits a sanitized provider-usage event plus a routing receipt containing:
Fable trigger class; selected demand fingerprint; requested and effective Opus identity;
quota-domain lease; pre/post usage when observable; input, cache, reasoning, and output tokens or
`unknown`; terminal classification; reset boundary; and whether useful output earned project-local
credit. A successful Opus terminal with zero useful output is visible waste, not proof that the
strategy worked.

Acceptance evidence for this strategy is: one deterministic trigger fixture, one unknown-state
denial, one no-demand `IDLE_SKIPPED`, one wrong-model refusal, one Fable/Opus concurrency denial, and
one separately authorized bounded Opus job that completes with exact identity and a useful
project-local artifact. Until those controls and a lawful job-specific start receipt exist, every
project's automatic provider gate remains CLOSED.
