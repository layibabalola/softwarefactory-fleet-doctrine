# Ruling candidate: MLV Fable-to-Opus Max model failback R1

Status: **PROPOSED ONLY — NOT A RULING, PROJECT ADOPTION, OR RUNTIME AUTHORITY**

Strategy ID: `MLV-FABLE-OPUS-MODEL-FAILBACK-1`

The economic objective is to use paid Claude capacity for real queued work before its provider
window expires. It is not to manufacture prompts merely to move a usage meter. When actionable
work exists, leaving available Opus capacity idle after Fable-model exhaustion is a scheduling
defect; when no authorized work exists, an `IDLE_SKIPPED` receipt is correct.

## Two different failures, two different recoveries

`fable` and `opus` are lane/role labels, not quota-domain evidence. The controller MUST distinguish
model-scoped exhaustion from account-scoped exhaustion:

| Failure class | Required action |
|---|---|
| `FABLE_MODEL_USAGE_EXHAUSTED` while the same authenticated profile has fresh producer-bound Opus-capacity evidence | Preserve the single logical Fable role, queue claim, and, only for an in-process provider-supported model change, the current claimant/session. Change only the admitted model to `claude-opus-5 --effort max`; emit one model-change receipt; launch exactly once. This is model failback, not independent quota failover. Missing, stale, or unproducible positive-capacity evidence means zero launches. |
| Provider session, five-hour, or weekly account quota exhausted | Open an account circuit breaker through the exact reset. Launch zero on the same profile, because Opus shares the exhausted account boundary. A launch is admissible only through a separately provisioned, independently authenticated, locally attested quota domain; re-authenticating the same operator account to evade a limit is prohibited. Credentials never move between profiles. |
| Model overloaded or temporarily unavailable | A same-profile model fallback may be used only for availability and only when role policy permits it. It receives no quota-independence credit. |
| Context overflow or oversized prompt | Start a fresh bounded session from a content-addressed evidence capsule. A model/account switch is not the first remedy. |
| Authentication refusal | Only a typed provider-output detector may open the auth circuit breaker; until that detector is installed, an auth-shaped or empty refusal is `UNKNOWN` and launches zero. Attended recovery is required. Never loop launches, move credentials, or infer quota exhaustion. |
| Dead seat, stale lease, or orphan watcher | Reconcile process ancestry, immutable process start, registry session, lease, and self-produced progress before any model decision. |
| Unknown, ambiguous, or conflicting evidence | Fail closed, launch zero, preserve the queue item, and publish a typed blocker. |

The current MLV V10 ignition source, SHA-256
`7769808F7FBB289CE3097C64673FBA0691345B907FA0612DFFF9FD339B3A3978`, maps both lane
labels to the same first-party profile and `claude-opus-5 --effort max`. That ref-qualified sealed
source state cannot prove either a Fable-to-Opus transition or an independent quota failover.
Runtime implementation must restore an explicit source-model identity and must never treat
renaming a lane as spending a different quota pool.

If the active Fable process can change model in its existing provider-supported resumable session,
that is the preferred transition and the current seat epoch remains fenced to that process. If the
process has ended, normal successor seating advances the seat epoch and rotates the independent
reviewer GUID under GATE-ID-5 while preserving only the logical Fable/hub role and queue subject.
The separate `opus` stage-one criterion-owner seat must not be stolen, duplicated, or relabeled as
the Fable/hub seat.

## Producer-bound transition receipt

Only structured evidence produced at the provider/process boundary may authorize model failback.
The immutable transition receipt binds:

- receipt schema and one exact failure class from the full taxonomy above (`model_exhausted`,
  `account_quota`, `model_unavailable`, `context_overflow`, `authentication`, `liveness`, or
  `unknown`);
- source and target model identifiers, effort, provider domain, opaque profile fingerprint, and
  authentication state;
- seat epoch, generation, scheduled slot, resumable session/process identity, and queue subject
  fingerprint;
- exact provider-produced exhaustion or positive-capacity evidence, observation/reset window,
  freshness bound, byte boundary, and receipt digest;
- the authorization generation and the single production launch boundary.

The consumer hash-opens and validates those exact bytes. It does not accept caller-selected paths,
regexes, timestamps, substrings, or a separately supplied "matching" value. A remote message,
operator prose, lane label, live PID, or stale watcher is a request/evidence input, never authority.
Empty claims, reservations, reviewers, errors, and owner sets serialize canonically as `[]`, never
as `{}`, `null`, omitted fields, or prose.

One receipt digest authorizes at most one transition in one generation/slot. Staleness is measured
against that same generation and provider capacity/reset window. Replay, changed bytes, a newly
live claimant, a closed account gate, or a different subject produces zero launches. Return to
Fable only after a fresh reset/capacity receipt and after the Opus-mode Fable turn terminates; a
reset never preempts a live turn or creates a duplicate.

## Admission and utilization policy

Before the single Opus launch boundary, the supervisor freezes and revalidates under one lock:

1. authorized actionable work and its deterministic input fingerprint;
2. exactly one logical Fable claimant/seat epoch and no starting duplicate;
3. the producer-bound exhaustion receipt and exact account/model capacity state;
4. exact `claude-opus-5 --effort max`, profile identity, process/session ancestry, and scheduled slot;
5. current reservations plus completion and independent-review reserve;
6. reviewed watchdog/task preimage, exact actor/path authority, and stop authority.

The existing singleton watchdog is the only automatic launch boundary. Model failback is a
decision inside that scheduler, never a second scheduler or sidecar launcher. While shadowing or
when the watchdog is Disabled, the controller records a decision but creates no process.

As reset approaches, scheduling may prefer high-value bounded work that fits remaining capacity,
but quality and completion reserve remain hard constraints. The controller never launches synthetic
burn work, weakens review independence, splits one job across duplicate seats, or begins work that
cannot reasonably checkpoint before the window closes.

## Required proof and rollout

Hostile tests MUST cover at least:

- exact Fable-model exhaustion plus explicit same-profile Opus capacity: one Fable-role Opus launch;
- absent, stale, malformed, or wrong-window positive Opus-capacity evidence: zero launches;
- account/session/weekly exhaustion on the same profile: zero launches;
- ambiguous scope, stale/broad receipt, changed receipt bytes, or caller-controlled match: zero;
- replay of an already consumed digest or slot: zero;
- a claimant appearing or account gate closing between receipt and launch: zero;
- a separate Opus reviewer seat: no collision, transfer, or independence loss;
- canonical `[]` encoding for every empty security-relevant collection;
- reset during a live Opus-mode Fable turn: no preemption or duplicate;
- context overflow, auth refusal, and orphan liveness: their typed routes only.

The authentication route additionally requires a tested parser over newly produced provider
output. Until that prerequisite exists, the known MLV auth-wall shape remains `UNKNOWN` and cannot
ignite or select a model.

Rollout is staged: shadow classification with zero launches; one separately authorized contained
canary; automatic model failback only after hostile tests and independent review; and non-preemptive
return to Fable on a fresh reset receipt. Ordinary scheduled execution and an independently checked
terminal work receipt remain mandatory before unattended recovery can be graded healthy.

This candidate contributes zero runtime authority. It does not enable the watchdog, install
credentials, mutate provider/account state, grant Product paths, satisfy reviewer independence, or
authorize spending merely because a Claude process exists. Runtime changes require their own exact
implementation ownership, tests, reviews, and local activation authority. Its completion/review
reserve is non-discretionary safety capacity and is compatible with the fleet's
zero-discretionary-reserve candidate; neither rule authorizes synthetic burn work.

## Acceptance gate

Before this becomes portable doctrine, a distinct adjudicator must bind the exact candidate commit,
tree, and manifest; reproduce positive and hostile controls; confirm the account-vs-model failure
taxonomy and single-launch invariant; obtain independent review; append an exact ruling to
`RULINGS.md`; and merge the reviewed bytes to canonical `master`. MLV must then publish a separate
project disposition before changing `specs/mlv-app.md` or any runtime behavior.
