# Automated bounded provider rotation R1

Status: **CANDIDATE / ZERO AUTHORITY / NO DEPLOYMENT**

This amendment responds to an owner requirement that paid provider capacity not
remain unused merely because per-launch attendance is impractical. It does not
open a gate, authorize a provider call, amend canonical R14, or grant project
adoption until exact-head independent review, distinct adjudication, canonical
ratification, and project-local installation evidence all exist.

## Proposed optional mode

`AUTOMATED_BOUNDED_ROTATION` permits one durable, locally authenticated owner
authorization window to nominate multiple provider runs without requiring the
owner to approve each run. The window itself never opens the automatic launch
gate. Every selected run still requires a fresh transactional broker admission,
exact launch binding, capacity evidence, and suspended-child attestation. Between
runs the gate is `CLOSED`; every terminal, ambiguous, expired, or failed path
transactionally reseals `CLOSED` before releasing any claimant.

The mode is deliberately zero acceptance authority. Its outputs may be used as
draft implementation work or findings, but never as independent review,
adjudication, adoption, merge, landing, release, or completion credit.

## Mandatory installation floor

No project may install or activate this mode until it proves, on the exact local
subject:

1. a pinned R14 project profile and canonical host-local state root;
2. a complete hash-bound census of scheduled-task, app-scheduler,
   repository-wrapper, and service surfaces, with every provider path routed
   through one supervisor;
3. a singleton persistent broker, one inference-bearing root per quota domain,
   full-child claimant fencing, authenticated terminal/dead recovery, and
   rollback;
4. fresh HMAC-qualified capacity and broker-health evidence plus deterministic
   no-work proof before any provider process exists;
5. hostile fake-provider, duplicate-scheduler, forged-window, state-replay,
   expiry, crash, ambiguity, bypass, and concurrent-planner controls;
6. a fresh independent review of the installed bytes and a current `CLOSED`
   receipt.

These prerequisites intentionally do not waive census, broker, claimant, or
review safety. The proposed compromise replaces per-launch owner interaction and
the 1,000-tick/canary sequencing requirement only for zero-credit temporary work;
it does not constitute R14 `ADOPT` and cannot restore an ordinary unattended lane.

## Window contract

The canonical window schema is
`schemas/automated-rotation-window-v1.schema.json`. A valid window is create-once,
fleet-secret HMAC authenticated, and binds its UUID, project, provider family,
opaque quota identity, policy digest, exact installed candidate subject,
authorized lane order, issue/expiry, run ceiling, and per-run wall/turn/context
ceilings.

Portable maximums are:

- 24 hours per window;
- 288 planned runs;
- 30 minutes per run;
- 16 turns per run;
- 100,000 context tokens per run;
- at least 60 seconds between planned runs;
- exactly one inference-bearing root per quota domain.

Projects may shorten any ceiling and raise reserve floors. They may not extend a
window, auto-renew it, increase concurrency, or treat a new window identifier as
recovery from an ambiguous predecessor. Any state/signature mismatch, unknown
lane, extra launcher, stale evidence, capacity uncertainty, subject drift, or
unproved child state closes and poisons the window.

## Fair deterministic rotation

The scheduler considers only lanes in the signed ordered lane set. It derives
addressed work without inference, starts from the durable signed cursor, selects
the first actionable lane, advances the cursor once, and persists the signed plan
before any provider admission. `NO_WORK` consumes no run and records zero provider
processes, calls, tools, or token counters. Concurrent planners fail closed rather
than both selecting a lane.

Planning is not launch authority. A provider child may resume only after the
existing inside-lock R14 checks revalidate the exact plan, window, inventory,
health, capacity, request, executable, argv, subject, process image, claimant,
and remaining limits.

## Canonical DNG competing evidence

Canonical master `92912d9a8bfdbb944ef040379b3d62b5dc7a985a` publishes a
DNG-local automated three-lane campaign at product subject
`3dc9100507c35e3724200dabaa3df6ffd2eb3cd0` and shipping-evidence subject
`4f5cacfa2f03c916ab8123ecd8e0e2b9d6bdea41`. DNG reports serial Fable, Opus,
and Sonnet execution, a closed gate between slices, fresh per-slice capacity and
one-use permits, bounded terminal artifacts, and exact residual-lease release.
This is material project evidence that unattended serial rotation can be built
without simultaneous quota-domain roots; it is not independent review or
portable adoption evidence for this candidate.

The candidates remain deliberately distinguished. DNG binds a standing local
owner directive to fresh lane-specific one-use permits and explicitly declines
this candidate's reusable 24-hour create-once window. This candidate instead
requires an expiring signed window plus fresh transactional broker admission for
every run. Neither project-local mechanism ratifies the other. A citing project
must preserve the stricter common intersection—serial domain ownership, current
capacity, one-run broker admission, closed-between-runs behavior, terminal
fencing, and zero acceptance authority—and publish its exact local disposition.

## Project disposition

Each project must publish one exact outcome after canonical ratification:

- `ADOPT_AUTOMATED_ROTATION(<canonical amendment>, <installed subject>, <review receipt>)`;
- `DISTINGUISH_AUTOMATED_ROTATION(<local difference>, <proof>)`; or
- `REJECT_AUTOMATED_ROTATION(<specific contradiction>, <proof>)`.

Until then the mode is test data and every provider-bearing automatic gate remains
closed.

## Submitted Agent Bridge candidate evidence

The initial closed implementation candidate is attributable to Agent Bridge Git
commit `ea50e08cee3a42576e4ace18e587a738fe73cf7b`, tree
`8d2aae0eb4927661a3d8ef4100e71b28a69b8f26`, with deterministic Git-archive
SHA-256
`AC2439BA659291E1A0E54790383EC5373983BDA37E1A5377982C2803EF49A001`.
It implements only create-once signed windows and a signed fair rotation planner;
all results retain `HARD_CLOSED` and zero provider-process/call counters. It does
not implement or claim the installation floor, broker admission, provider launch,
review, or activation.

Local verification on that exact candidate reported 43 focused tests passing;
925 regression tests and 47 subtests passing with only the two canonical-root
identity assertions deselected because the candidate was tested in a linked Git
worktree; Ruff and `git diff --check` passed. The unadjusted full run produced the
same 925 passes and 47 subtests, with only those two path-identity assertions
failing. These results are evidence for review, not adoption authority.
