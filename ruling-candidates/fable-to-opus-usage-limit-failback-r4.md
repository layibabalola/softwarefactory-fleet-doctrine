# Ruling candidate: Fable-to-Opus usage-limit failback R4

Status: **FINAL STRATEGY SUBMISSION / PROPOSED ONLY / ZERO RUNTIME AUTHORITY**

Candidate id: `FABLE_TO_OPUS_USAGE_LIMIT_FAILBACK_R4`

Project/date: `adversarialllm` / `2026-08-24`

Adverse review dispositions:
`receipts/adversarialllm-fable-opus-failback-r1-review-disposition-20260824.json`,
`receipts/adversarialllm-fable-opus-failback-r2-review-disposition-20260824.json`, and
`receipts/adversarialllm-fable-opus-failback-r3-review-disposition-20260824.json`.

R4 is the proposed controlling strategy submission. R1-R3 and receipt schemas v1/v2 remain adverse history and are
explicitly non-implementable. R4 intentionally publishes **no executable wrapper or normative
machine schema**: implementation is a later exact-subject work block with its own tests, reviews,
installation, and project authority. This separation prevents a prose strategy from laundering an
incomplete schema into runtime admission.

## Adverse-history disposition

No adverse finding is silently waived:

- R1's named closure set is mapped as follows: immutable parent/child identity, auditable classifier
  input, account-domain/cell separation, write-ahead intent, single-flight fencing, exact model
  identity, runner drift, partial-output refusal, hard budgets, auth prohibition, kill switch,
  staged rollout, and role/independence controls are closed as strategy requirements in R4; their
  executable proofs remain explicitly deferred to the future implementation work block.
- R1's dormancy TTL/reset/anti-flap proposal is replaced by per-item Fable terminals,
  `failbackAdmissionCap`, and the two-consecutive-Opus-dormancy stop-loss; cached dormancy routing remains
  open and excluded from Phase 1.
- R2 schema-v1 contradictions are closed by withdrawing schema v1 from consideration. R2's one-host
  serialization decision is incorporated here; multi-host adoption remains open and blocked.
- R3 schema-v2 crash, recovery, clock, budget, and conditional-soundness findings are deferred to the
  future implementation state machine and hostile fixtures. Schema v2 remains rejected and cannot
  be used as a starting contract without exact finding-by-finding closure tests.

Thus the strategy layer has no open authority-bearing exception. Deferred items block implementation
or adoption until proven; they are not accepted risk.

## Owner objective

Useful paid Claude capacity must not sit idle merely because Fable has exhausted its allowance.
When a useful, already-authorized work item is eligible for Opus, the factory should use Opus rather
than preserve the remaining paid window until expiry. The objective is useful accepted output per
allowance, not token burn, status narration, fabricated review demand, or provider-powered idle
checks.

## Measured fact

On 2026-08-24, native Claude Code 2.1.237 at executable SHA-256
`406167231b3636e55a01d0ce93567256c61e7973489e645883302f14808ae668` was invoked in
non-interactive JSON mode with Fable primary and Opus configured as the native fallback. The Fable
attempt returned `is_error=true`, terminal `api_error`, status 429, a locally normalized
Fable-limit classifier label, zero input/output usage, and an empty model-usage map. No built-in
Opus result was observed in the structured result; this does not prove that no hidden dispatch
occurred. The raw provider text from which the local label was derived was not retained,
so the classification is not independently re-auditable from this receipt.

One separate explicit Opus invocation completed with canonical usage identity
`claude-opus-5`, 12,598 output tokens, 17,387 cache-creation input tokens, 6,623 thinking tokens,
and provider-reported cost USD 0.48883. The evidence does not prove durable ordering between the two invocations or
any inclusion relation between thinking and output tokens. This is one observation consistent with
explicit failback, not proof of a universal native-runner defect or an installed automatic strategy.
The normalized receipt is
`receipts/adversarialllm-fable-opus-failback-probe-20260824.json` and openly lists its evidence
gaps. The probe predates this contract and would not itself satisfy the typed-terminal law below:
it does not bind classifier input, installed rule, immutable work item, or durable attempt ordering.

## Proposed routing law

**Non-operative candidate text.** These rules describe a proposed future contract; they do not
authorize any provider call until separately implemented, reviewed, installed, and activated.

For a single frozen work item:

1. Prefer exact Fable when the role permits it.
2. Treat native `--fallback-model opus` as opportunistic for overload/unavailability, not as proof
   that a Fable allowance limit will invoke Opus. R4-admitted Fable attempts must hash-bind native
   fallback as disabled; only the broker may create the explicit Opus child.
3. Classify `FABLE_QUOTA_DORMANT` only from a complete structured Fable terminal that is API-error
   429, matches a versioned bounded Fable-limit rule, produced zero task output, reports zero
   auxiliary/fallback model usage, and is durably
   settled. The classifier may consume only allowlisted structured terminal fields; any retained
   provider-error-text digest is integrity evidence, never a classification input. Free-text/message
   fields and any enum or label locally derived from provider error text are forbidden inputs. The
   allowlist may contain only provider-native non-text status/model/cell codes proven by the funding
   gate; if no such discriminator exists, the candidate is abandoned rather than widening the rule.
   Generic or
   account-wide 429, partial output, auth/payment error, timeout, malformed/lost output, runner
   drift, or process ambiguity produces no Opus launch.
4. If a prelaunch, model-free demand predicate still classifies the work item as actionable and it
   is separately eligible for Opus, and the item has a precommitted mechanically checkable
   acceptance oracle authored by group 2 and hash-certified by group 3, create one new explicit Opus attempt over the same immutable subject, prompt,
   role, effort, tools, and output contract. Open-ended work without that oracle is ineligible.
5. Require exact effective Opus task identity from native structured evidence. Record all auxiliary
   model usage without granting it a task role. Identity mismatch or Opus refusal ends without
   retry or a third model.
6. Settle the Fable refusal and Opus terminal as one parent work item. Fable refusal plus Opus output
   is one effective result, never two blind reviews or two independent provider keys.

R4 deliberately excludes cached direct-to-Opus dormancy routing. Each admitted Phase-1 work item
must first obtain its own exact Fable terminal. The fast zero-usage refusal is acceptable overhead
and counts inside the per-item and aggregate Fable-plus-Opus transaction budgets. Only a refusal that
passes every failback admission gate and creates an Opus intent increments `failbackAdmissionCap`;
a generic 429, partial output, or other non-admitted Fable refusal never increments that intent counter.
This rule remains until a separately reviewed durable dormancy contract exists. It removes stale reset, clock,
multi-work-item replay, and direct-route audit ambiguity from the initial strategy.

For this strategy, `durably settled` means the Fable terminal, classifier decision, usage, and
parent-work-item state are persisted and reconciled with no live Fable process, unclosed child
intent, or ambiguous continuation before any Opus intent may be created.

## Scope and authority

Fable and Opus on one Claude account remain one Anthropic independence class and one local account
domain for serialization, accounting, and conflict-of-interest purposes, even when structured
provider terminals may indicate distinct model-availability cells. A cell-specific observation may
route one frozen work item, but it does not change the shared account domain, prove another cell's
availability, or create review independence.

Initial adoption is one-host only. One host-local broker must serialize all local repositories,
wrappers, transports, Fable, Opus, and Sonnet work sharing the opaque account-domain identity.
That identity must be an owner-installed non-secret alias bound in policy; it must never be derived
by reading credentials, tokens, cookies, browser state, or attended-session data.
Sharing that account across hosts is unsupported and blocks adoption until a separately reviewed
shared arbiter exists. Because a host-local broker cannot discover another host by itself, the owner
must sign a single-host/account attestation at installation and refresh it before every canary and
after any host, account, credential, or transport change. The attestation binds a host-attested
machine identity and monotonic boot generation; VM restore, image clone, host-identity ambiguity,
or generation rollback invalidates it and blocks adoption. The owner signature enrolls one exact
host/account/config generation. A broker-issued continuity lease has a maximum TTL of 15 minutes and
may renew without owner presence only while host attestation, boot generation, account alias,
transport, installed hashes, and kill-switch state remain exact. Any unreadable or changed input
blocks renewal; expiry before launch refuses without consuming authority. Unattended operation is
prohibited until a separately owner-activated, ratified implementation proves this renewal contract.
The owner attestation also asserts no off-host attended session is consuming the enrolled account
alias; uncertainty or contrary evidence invalidates it. This is an accepted owner-asserted detection
limit, not a machine-proven property, and blocks adoption when the owner cannot attest it.

After an Opus child intent exists, lease expiry can create only a fenced settle-only continuation
bound to that exact intent/session/process generation. It may read, terminate, quarantine, and settle
that child through the installed attempt wall ceiling plus recovery bound, but it can never create an
intent, launch, retry, or admit output to a new item. Thus launch authority expires at lease TTL while
duplicate-prevention and cleanup authority survive only for the already-started child.

The owner must enroll every discovered automated launcher, scheduler, wrapper, and transport into the
broker. Any unenrolled or unenrollable launcher blocks adoption. Attended human sessions remain
outside broker control, but their allowance consumption is unknown foreground demand in capacity
accounting and therefore blocks automated admission while an allowance-consuming attended Claude
session is detected or unknown. The owner signs the one-use start out of band before any Claude
process is launched; that signature event alone is not an attended Claude session. The attendance
oracle is limited to the owner-enrolled launcher census plus process
existence/ownership, scheduler-task state, and broker-lease metadata under classifier-artifact
privacy and retention controls; absence is never inferred from one signal, and unresolved state
blocks. Browser storage, profiles, cookies, credentials, tokens, and session content are never read.
If attendance remains unknown for five minutes, the item closes `ATTENDED_STATE_UNKNOWN`, canary
authority remains unconsumed, and an owner-visible receipt is required before any new item.
This is a pre-attempt admission timer; terminal-unsettled recovery begins only after a provider
attempt exists, so the two timers never govern the same state.

Failback carries only the already-authorized task role. It cannot transfer credentials, claims,
leases, actor identity, reviewer/adjudicator keys, recusal status, provider-family independence,
task or scheduler authority, gate state, landing, merge, release, billing, or owner authority.
Role collapse—such as one Opus actor producing and reviewing the same subject—remains prohibited.

The minimum viable seat map has five distinct human/cryptographic governance identities: (1) owner,
candidate author, implementer, and canary operator; (2) evaluator author; (3) independent controls
reviewer/certifier; (4) acceptance-manifest author; and (5) final adjudicator. Each group uses distinct task
identities and keys. Groups 2 through 5 are outside the producing lane and Claude account/independence
class; group 4 is distinct from every candidate/implementation/evaluator/operator/hash-reviewer/adjudicator role;
group 5 is distinct from every author, implementer, operator, evaluator, and reviewer. If these separations are
unavailable, adoption remains blocked; same-account Fable/Opus calls never fill them.
Any later unattended activation additionally requires canary operator and implementer to be distinct.
Phase 1 intentionally fuses the group-1 roles; canary acceptance independence therefore relies on
groups 2 through 5 and never on group-1 self-certification.

## Bounded Opus attempt

Before launch, the project-local supervisor must bind and revalidate exact work-item bytes, ordinary
task authority, role eligibility, runner/wrapper/model policy hashes, one-host account lease,
current owner-signed single-host/account attestation, capacity reservation, and hard ceilings for
wall time, turns, input/cache/reasoning/output tokens, and cost or allowance slice. A missing,
expired, or tuple-mismatched attestation refuses before provider launch.

For Phase-1 canaries, the installed attempt wall ceiling is at most eight minutes and recovery at most
five minutes; this stricter recovery value overrides the general recovery formula and leaves two
minutes for revalidation/spawn/settlement overhead. A fresh 15-minute
lease is issued and revalidated immediately before spawn, so attempt plus recovery fits that lease.
Any spawn delay requires reissuance. Longer work is
ineligible until the ratified unattended renewal contract exists.

Capacity reservation means an active conservative estimate for the complete Fable-plus-Opus
transaction followed by terminal measured/estimated/unknown settlement; it is not a discretionary
idle-capacity floor. A parent policy with zero discretionary reserve therefore does not remove active
transaction or completion reservations. Opus-exclusive authorized demand outranks failback demand
and may displace or block it. `OPUS_EXCLUSIVE` requires an explicit pre-queue owner/task-policy
classification that Fable is ineligible or that the authorized quality/role contract mandates Opus;
failback cannot assign that class to itself. Opus-exclusive work always wins; the failback
starvation bound expires or abandons deferred failback rather than preempting Opus-exclusive work.
Any already-started failback displaced by Opus-exclusive demand is cancelled as typed non-success
and all measured/estimated/unknown consumption is charged to its tranche, aggregate budget, and
stop-loss state.
The installed policy must also impose an aggregate failback window budget, stop-loss, queue priority,
and finite starvation bound across all repositories sharing the account domain. The aggregate window
is one 60-minute quiet-reset account-domain window measured by a monotonic clock. Counters persist across
process restart; a host reboot or unverifiable clock continuity does not reset them and instead
blocks failback. A fresh continuity lease preserves stop-loss state, allowance-cycle reservations,
and the conservative full short-window charge; short-window counters clear only after 60 verified
monotonic minutes with zero failback calls and an owner-visible rollover receipt.

`failbackAdmissionCap` is a distinct rolling 60-minute counter over admitted Opus intents; each event
ages out individually. It persists across process restart. After host reboot or unverifiable clock
continuity it is conservatively full until 60 verified monotonic minutes elapse with zero admitted
Opus intents. It never shares reset state with the aggregate quiet-reset budget.
Both the aggregate budget and `failbackAdmissionCap` must independently pass at admission; neither
counter borrows capacity or authority from the other.

Before shadow, the owner signs an installed policy schedule containing every numeric budget,
stop-loss threshold, tranche, queue priority, starvation bound, timer, and cap. Group 3 certifies
that exact schedule hash against the strategy's conservative minima and rejects missing, weaker, or
internally inconsistent values. Neither group may change values after certification without reseal
to `DISABLED` and a fresh two-party schedule receipt.

For Phase 1 those minima are mechanically fixed: at most three admitted Opus intents in any rolling
60 minutes; an aggregate quiet-reset window of at most three complete failback transactions and at
most 25 percent of the owner-approved allowance tranche, whichever binds first; an allowance tranche
of at most 10 percent of provider-reported remaining Opus allowance after committed and forecast
`OPUS_EXCLUSIVE` demand plus its owner-signed safety reserve are subtracted; strict
`OPUS_EXCLUSIVE` queue priority; no new failback while `OPUS_EXCLUSIVE` work is queued, running, or
forecast inside the next 15 minutes; and at most 13 minutes from an unexpected `OPUS_EXCLUSIVE`
arrival until an already-started failback has terminated or entered fenced settle-only recovery.
Deferred failback expires rather than starving exclusive work. The attempt, recovery, lease,
attendance, capture, rollout, and hold timers and the two-consecutive-`OPUS_QUOTA_DORMANT` stop-loss
use the stricter values stated elsewhere in this strategy. Any schedule field without one of these
exact values or an owner-signed stricter value is uncertifiable and blocks the stage.

Failback may consume only an owner-approved Opus allowance tranche measured over the provider's
actual allowance cycle after subtracting committed and forecast Opus-exclusive demand. The
pre-adoption evidence must prove that Opus is separately metered from Fable and that the tranche
would otherwise expire unused. Unknown cycle, metering, reset, or remaining allowance blocks all
provider failback, including canary. Funding-gate failure therefore abandons the candidate; owner
presence cannot waive unknown allowance evidence. A live attended Claude session is separate
foreground demand and still blocks admission. Zero discretionary reserve
does not permit spending committed or forecast Opus-exclusive capacity.

The supervisor must not login/logout, rotate accounts, read or rewrite credentials, set auth
environment variables, buy credits, switch provider/API, automate attended UI, lower model/effort,
or choose a tertiary model. Unknown usage is not zero. A budget stop, refusal, timeout, cancellation,
or ambiguity is typed non-success and cannot be renamed or retried. Opus allowance exhaustion is
typed `OPUS_QUOTA_DORMANT`; it closes the parent item as failed, and later work over the same subject
requires a new owner-issued authorization epoch. Every typed non-success permanently closes that attempt. The parent item
has a distinct owner-issued id/authorization epoch plus an immutable subject digest. Ambiguous or
unsettled outcomes enter bounded recovery for at most the lesser of 30 minutes or twice the installed
attempt wall ceiling. Expiry closes `BLOCKED_OWNER_REVIEW`, launches nothing, and creates an exact
evidence hold. The broker terminates its own child process tree at expiry. If termination cannot be
proved, the child remains fenced/orphaned, any later output is quarantined with zero acceptance or
review credit, and the owner-visible block persists. After 30 days, absent owner extension, payload fields are redacted under the tombstone
contract while non-payload duplicate-prevention state persists. Other terminal
non-successes close the parent item as failed; only a new explicit owner authorization epoch may
create a genuinely new item over the same subject digest, and it must reference the prior terminal
item and changed authority/need or resolved failure evidence. Cosmetic subject changes never create
eligibility. Attended human Claude
sessions are external foreground demand outside broker control: their presence or unknown state
must block automation, and the broker must never attach to, interrupt, or kill them.

## Required future implementation contract

The separately reviewed implementation must provide:

- an immutable work-item digest and distinct Fable/Opus attempt ids;
- a preassigned Opus session id and durable write-ahead child intent before spawn;
- one host-local account lease with atomic create/CAS, monotonic fencing, boot/process generation,
  and restart-safe at-most-one Opus spawn;
- native process/session/output correlation and an exit path for every crash boundary;
- hash-chained state that truthfully distinguishes planned, running, terminal-unsettled, recovery,
  blocked, and settled states;
- exact primary task-model evidence plus full per-model auxiliary usage;
- a privacy-bounded classifier artifact retaining structured terminal fields plus a digest of any
  redacted provider-error text; this is error evidence, not prompt, task output, or hidden reasoning;
- installed declarative definitions for Opus role eligibility, the model-free demand predicate, and
  the bounded Fable-limit classifier rule and auxiliary-model allowlist, each hash-bound before launch;
- per-dimension measured/estimated/unknown usage and enforced budgets;
- a deterministic, project-owned, non-provider useful-outcome evaluator that is independent of the
  producing lane and Claude account/independence class, frozen before either attempt, and model-free
  throughout evaluation; unknown earns no quality or review credit;
- aggregate reservation, Opus-exclusive priority and displacement, stop-loss, queue-priority, and
  starvation controls across the account domain;
- a maximum of three classified refusals admitted to Opus failback per rolling 60-minute
  account-domain window, enforced after the ordinary Fable terminal and before Opus intent; this
  never delays or blocks the already-authorized primary Fable attempt;
- distinct policy fields and counters for `failbackAdmissionCap`, `fundingSampleMinimum`, and
  `opusDormancyStopLoss`; equal numeric values never merge their scope or reset semantics;
- an installed kill switch that defaults to blocking all failback launches; unreadable, unverified,
  missing, expired, or drifted state blocks; plus staged rollout, canary reseal, rollback/disable path,
  alerts, metrics, and raw-evidence privacy controls; and
- a bounded retention policy: classifier artifacts, hash-chained state, and metrics expire no later
  than 30 days after terminal settlement unless an exact evidence hold applies; expiry securely
  removes payload-bearing fields while preserving non-sensitive aggregate/hash audit facts, chain
  anchors, and hash-chained tombstone events so surviving history remains verifiable;
- permanent non-payload retention of stop-loss counters and persisted attempt-order anchors; these
  safety facts do not expire with the 30-day payload window;
- an automatic evidence hold on every capture terminal and label, shadow and containment terminal,
  canary terminal, and acceptance-manifest artifact until fleet ratification or explicit abandonment,
  capped at 90 days after the first captured terminal (or the capture-epoch terminal when no item
  terminal was captured);
  reaching the cap
  automatically abandons, redacts payload fields under the tombstone contract, and preserves only
  chain anchors and non-payload safety facts;
- a strict machine schema whose hostile fixtures prove that contradictory route, status, intent,
  attempt, identity, budget, credit, rollout, and settlement combinations are rejected.

The group-2 per-item oracle is the item-specific frozen rule inside the deterministic evaluator; the
group-4 manifest aggregates those exact evaluator results and cannot redefine the item oracle.
`CANARY_PROGRAM_HOLD` is the automatic hold capped at 90 days. `BLOCKED_RECOVERY_HOLD` is the
30-day payload hold used for terminal ambiguity before tombstone redaction. Neither class silently
extends the other.

Receipt schemas v1/v2 in this branch are negative-control design history. They are not acceptable
starting points unless a future work block explicitly preserves and closes every adverse review
finding with exact schema-negative tests.

## Minimum hostile proof

The implementation must show:

1. Fable success or any non-exact/partial/ambiguous terminal launches zero Opus attempts.
2. Exact zero-output Fable limit creates one durable Opus intent and at most one process.
3. Every crash point from pre-intent through post-output settlement, repeated restarts, and pid
   reuse remains duplicate-free and recoverable or explicitly blocked.
4. Prompt, subject, role, effort, tools, policy, authority, runner, or model drift refuses.
5. Wrong/missing/multiple task models and unallowlisted auxiliary models earn zero credit.
6. Every wall/turn/token/cost ceiling stops without continuation or retry.
7. Two local repositories/transports serialize; a second host sharing the account blocks adoption.
8. Same-family and role-collapse cases never satisfy independence or recusal.
9. Auth mutation, account rotation, attended UI, third-model, and kill-switch negatives remain zero.
10. Useful Opus output with failed settlement is recovered, not rerun; tampered state is rejected.
11. Idle or unchanged demand produces zero Claude calls.
12. Canary reseal and rollback/disable work at every terminal and recovery boundary.
13. Alerts and metrics expose classifier-rule drift, attempt state, measured/estimated/unknown usage,
    displacement, stop-loss, and settlement without retaining prompts, outputs, credentials, or
    hidden reasoning.
14. Active reservations cannot exceed the account-domain window budget, and Opus-exclusive demand
    preempts failback without duplicate launch or lost settlement.
15. Queue and starvation fixtures prove deterministic priority, bounded deferral, cancellation, and
    permanently closed attempts under concurrent demand.
16. Missing, expired, wrong-host, wrong-account, or tuple-mismatched owner attestation refuses before
    provider launch and does not consume canary authority.
17. Two consecutive `OPUS_QUOTA_DORMANT` outcomes in persisted failback-attempt order—across windows,
    leases, restarts, and serial canary cycles—trigger the stop-loss, reseal `DISABLED`, and require a
    new owner plus group-3 independent-reviewer cell-availability hypothesis receipt.
18. Stop-loss state persists across windows, leases, process/host restart, and serial canary cycles;
    only the explicit owner plus group-3 hypothesis receipt defined in proof 17 can clear it.
19. Continuity-lease expiry before launch, expiry during an attempt, every renewal-input drift,
    boot-generation rollback, and failed renewal all block new launch without duplicate settlement.
20. The three-per-hour `failbackAdmissionCap` blocks the fourth Opus intent—not the primary Fable
    attempt—and survives restart. This control is proven in containment fixtures; Phase-1 serial
    canaries do not exercise the fourth-intent path live.
21. Any enabled native fallback flag or any auxiliary/Opus usage in the Fable terminal refuses before
    broker Opus intent creation; fixtures prove the broker never duplicates hidden/provider fallback.
22. Lease expiry permits settle-only continuation for the exact existing child, never launch; forced
    termination, termination failure, and output arriving after `BLOCKED_OWNER_REVIEW` are fenced,
    quarantined, duplicate-free, and earn zero acceptance or review credit.

## Rollout and adoption

The adopting project may first authorize only the reviewed capture-only writer under `DISABLED`.
That provisional instrumentation build grants no failback, classifier, or provider-launch authority. It
cannot begin until group 3 independently binds and certifies the exact writer, artifact schema,
privacy policy, and retention-policy hashes; drift or missing certification blocks capture.
For funding only, a conforming capture terminal is structurally fixed as API-error 429, zero task
output, zero auxiliary/fallback usage, native fallback hash-bound disabled, and durably settled.
Classifier-rule matching is not a funding-sample criterion; the rule is authored only after capture.

Before cohort registration, group 2 authors the mechanically checkable pre-capture eligibility/oracle
predicate and group 3 certifies its hash. That exact predicate is part of the frozen inclusion
criteria; missing or changed predicate blocks capture.

Ground-truth class comes only from `captureLabel.v1`: the owner signs manually captured
provider-surface evidence binding account alias, model cell, terminal timestamp, allowance
cycle/state, and raw-evidence digest, then group 5 independently adjudicates and signs the label.
An exact provider-signed fixture is the only alternative. Labels are adjudication evidence, never
runtime classifier inputs. If neither source labels both classes, funding abandons.
Group 5 must sign the frozen complete label set before group 3 may use it for funding-gate
certification. Group 5 alone adjudicates labels; group 3 alone certifies the funding gate, so those
two authoritative functions never share one identity.
The capture evidence set must first prove structured-field distinguishability on captured positive and generic/account-wide
negative terminals; this funding gate is authoritative and failure abandons before further
measurement. Shadow later revalidates the same frozen rule and samples against installed bytes but
cannot reverse a funding-gate failure. The writer then measures ordinary
authorized work to bind Fable-dormancy frequency, zero-output refusal
latency/usage, oracle-eligible queued demand, provider allowance-cycle behavior, and the no-failback
baseline. No further implementation is funded unless the capture proves at least three naturally
occurring, oracle-eligible, fallback-disabled, contract-conforming Fable-cell refusals in one
seven-day period plus at least three identically admissible natural or provider-signed,
contract-conforming generic/account-wide 429 negatives, demonstrates separately
metered expiring Opus capacity, and projects conservative useful-output gain at least twice the
combined provider-refusal and broker overhead. The owner may strengthen but not weaken this gate;
failure abandons the candidate.

Allowance-cycle evidence must be either a native structured provider usage/limit receipt or a
manually captured, owner-signed statement from the provider-visible account surface binding account
alias, model cell, cycle start/end, remaining allowance, capture time, and source-artifact digest.
Automation must not read browser/profile/credential state to obtain it. If neither evidence source is
available, separate metering and expiry remain unknown and the funding gate fails.

Group 3 independently certifies the authoritative funding gate against hash-bound capture artifacts,
sample count, allowance evidence, and the conservative projection, and signs a terminal disposition.
Group 1 cannot self-certify or fund past a missing, failed, or ambiguous group-3 disposition.

Before `CAPTURE_ONLY` opens, group 3 pre-registers and hash-freezes a criterial cohort rule, inclusion
criteria, and denominator procedure. The owner signs one class-level opt-in acknowledging native
fallback loss for every future item matching that rule during the epoch; per-item discretionary
selection is forbidden. Every matching terminal, including non-conforming outcomes, is captured.
Any omission or post-hoc rule/criterion change abandons that capture epoch.

Funding samples come only from already-planned primary Fable work matching that frozen rule; the
strategy creates no extra call. This owner authority is exact-class/configuration authority and does
not alter non-matching primary work. Any
non-conforming or fallback-enabled ordinary terminal counts toward neither positive nor negative
funding/shadow samples. The funding model charges the lost overload/unavailability fallback value.

The 2x projection includes provider refusal, broker operation, one-time implementation and hostile
fixtures amortized over the measured allowance horizon, and recurring five-identity governance,
attestation, review, manifest, adjudication, and canary costs. A separate owner-signed total-program
go/no-go is required before any implementation beyond capture instrumentation is funded.

Capture-only observations make no incremental calls and therefore consume zero `failbackAdmissionCap`;
they supply the measured refusal latency/usage and instrumentation overhead used by the funding model.
The 2026-08-24 probe is non-conforming evidence and cannot count toward `fundingSampleMinimum`.
Every settled capture terminal and label enters `CANARY_PROGRAM_HOLD` immediately, with the 90-day
absolute cap anchored to the first captured terminal (or the epoch terminal receipt if no terminal
was captured). The same hold covers exact shadow, containment, canary, and acceptance-manifest
artifacts through ratification, abandonment, or that one absolute cap. Before `CAPTURE_ONLY` opens,
group 3 must certify from installed stage TTLs and the ten-cycle/30-day canary bound that the entire
maximum program can finish before the cap; an absent or negative certification blocks capture. The
hold cannot be extended to rescue a late program: reaching the cap automatically abandons it.

`CAPTURE_ONLY` is a sub-stage of `DISABLED`; its single measurement epoch has a minimum eight-day
and maximum ten-day TTL, terminal receipt, privacy expiry, and return to `DISABLED`, so the seven-day
funding sample is never aggregated across unrelated capture epochs. Expiry without sufficient
evidence abandons. Continuity-lease renewal is exercised only by proof-19 fixtures
until a later owner activation separately authorizes unattended operation.

Rollout is `DISABLED[CAPTURE_ONLY] -> SHADOW_CLASSIFIER -> CONTAINMENT_FAKE -> ONE_AUTHORIZED_CANARY -> DISABLED`.
The adopting project must explicitly authorize the exact capture-only writer, shadow classifier,
and fake containment subjects after review. The capture-only writer is installed while `DISABLED`,
makes zero incremental provider calls, observes only ordinary authorized terminals, and is bound to
the same privacy, retention, TTL, hash, and disable controls. `SHADOW_CLASSIFIER` and
`CONTAINMENT_FAKE` operate only on retained already-authorized terminals or replayed fixtures, make
zero incremental provider calls, and spawn zero Opus processes. Each stage has an
installed TTL and terminal receipt and reseals `DISABLED` on success, failure, expiry, or ambiguity.
Before canary, shadow evidence must replay the same frozen, funding-qualified set of at least three
naturally occurring, ordinarily authorized Fable refusals and three natural or provider-signed
generic/account-wide 429 negatives captured by the contract-conforming structured-terminal artifact;
this is an installed-bytes revalidation of the funding set, not an independent sample. The strategy grants
no call merely to manufacture that sample. It must also prove that allowlisted structured fields
separate a Fable-cell refusal from generic/account-wide 429 negatives. If positive and negative
samples cannot establish that distinction, the candidate is abandoned. The canary requires a
separate one-use owner start.
Group 3 certifies every shadow/containment terminal disposition and the complete pre-canary evidence
set. Missing, ambiguous, or non-independent certification blocks canary and consumes no authority.
Group 1 authors the proposed classifier field allowlist and bounded rule from capture evidence;
group 3 independently freezes and certifies their exact hashes before shadow or canary use.
Every canary terminal reseals disabled. Canary success requires output
accepted by the deterministic non-provider evaluator within every item and aggregate budget, no
displacement of Opus-exclusive demand, exact settlement, and clean reseal.
Evaluator unavailability, non-termination, error, or hash drift is typed canary non-success and
reseals `DISABLED` with no acceptance credit.
Failure returns disabled for revision or abandonment. Adoption must compare useful accepted output
per paid allowance, blocked Opus-exclusive demand, cost, and incident rate against a no-failback
baseline. Before the owner canary start, a canary-acceptance manifest authored by an identity
distinct from the candidate author, implementing/producing lane, evaluator author, canary operator,
pre-canary hash reviewer,
and final adjudicator must
freeze those metric definitions, bounds, evaluator hash, no-failback baseline, and abandon outcome;
at minimum it requires a positive lower-confidence-bound improvement in useful accepted output per
paid allowance, zero displaced Opus-exclusive work, no budget breach, and no increase in material
incident rate. Failing any bound abandons the candidate. Any broader activation is a separate owner decision after
fresh installed-byte review and production evidence.

One canary cycle may prove mechanics but cannot by itself prove the statistical improvement bound.
The acceptance manifest must freeze its aggregation basis and minimum sample size; any additional
canary is a separately authorized, serial, resealed cycle. The evidence program is capped at ten
canary cycles and 30 elapsed days; reaching either cap without satisfying the bound automatically
abandons. Fleet ratification remains blocked until the accumulated exact canary set satisfies that
precommitted basis.
Before the first canary, group 3 must certify that the frozen aggregation basis and minimum sample
size are satisfiable within ten cycles and 30 days. Non-satisfiability blocks without consuming
canary authority.

Here, Phase 1 means the complete bounded sequence from `DISABLED` through separately authorized
shadow, fake, and canary cycles, always returning to `DISABLED`. Stop-loss reseal expires all queued
failback items as failed; none remains queued across reseal or competes with later Opus-exclusive work.

Immediately before the one-use owner canary start, an independent reviewer must bind and approve
the exact installed runner, wrapper, classifier, policy, schema, evaluator, and kill-switch hashes;
any byte drift refuses and consumes no canary authority.

Project adoption must bind the exact runner/package, wrapper, classifier, installed policy,
machine schema, hostile tests, host-scoped launcher census, kill-switch test, one useful bounded
Opus canary, reseal receipt, independent useful evaluator, portfolio budget and displacement policy,
and fresh owner-signed single-host/account attestation. Before fleet ratification, a distinct
adjudicator must bind the candidate commit/tree/manifest, reproduce the tests, obtain fresh
independent review, and append a disposition to `RULINGS.md`.

Until those steps occur, R4 is strategy data only. It authorizes no provider launch, task or
scheduler mutation, authentication action, gate opening, adoption, review/vote credit, merge,
landing, release, billing change, or account action.
