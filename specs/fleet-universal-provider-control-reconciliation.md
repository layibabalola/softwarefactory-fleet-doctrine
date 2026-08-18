# Universal provider-control reconciliation R7

Status: **CANDIDATE / ZERO AUTHORITY / NO DEPLOYMENT**

Issue: <https://github.com/layibabalola/softwarefactory-fleet-doctrine/issues/4>

Reconciliation input comment:
<https://github.com/layibabalola/softwarefactory-fleet-doctrine/issues/4#issuecomment-5332348238>

Exact starting baseline: `9af3eb9d4f4669abb787cc1966280608f5fbbce9`.

This is an additive reference amendment to the ratified provider-capacity governor. It does not
replace that governor, deploy a supervisor, change a task, open a gate, authenticate, contact a
provider, or grant any project adoption credit. It reconciles the portable controls in Conjugal
candidate `37f1246543c86300089b77a51a3b8ad2c5292b8d` (actual commit tree
`35a44265d358aa8ec3544ba2f08e0ef8e4b38216`) with the ratified governor and the Agent Bridge
64/100 NO-GO findings. Final authority requires stranger review, distinct adjudication, hosted
checks on the exact candidate, a durable ruling, and an accepted canonical merge.

## One policy bus, explicit runtime boundaries

The existing doctrine repository remains the sole policy/schema/redacted-receipt bus. Raw quota
identity, native observations, credentials, commands, process identity, reservations, and live gate
state remain outside Git in the project supervisor's pinned state root. A project with one physical
host uses one host-local supervisor. This reference rejects every multi-host or `SHARED_BROKER`
profile: a declarative identity is not a shared backend. A future genuinely shared implementation
requires separate exact review and adjudication. No second telemetry doctrine repository is created.

`tools/universal_provider_control.py` is a deployment-inert reference contract. It cannot launch,
resume, terminate, authenticate, schedule, or contact a provider. Initial admission creates only a
`PREPARED_SUSPENDED` lease while retaining exact artifact and quota-lock handles. A second fresh,
HMAC-qualified observation of the actual suspended image and argv must pass the inside-lock resume
boundary before `ALLOW_ATTESTED` exists.
The resume boundary rejects `now >= lease.expires_at`; expiry never releases the persistent
claimant, reservation, OS lock, or artifact handles, and an expired CANARY attempt reseals CLOSED.

## Universal invariants

Project profiles may lower age, turn, context, lease, or capsule ceilings; raise reserve floors or
post-reset quiet; and add required capacity dimensions. They may never weaken these invariants:

1. Every gate starts persistently `CLOSED`. A missing, malformed, oversized, unreadable, reparse,
   expired, unknown, or binding-drifted state is non-green.
2. Reset, authentication success, capacity return, and quota refusal only append provider signals.
   They cannot change a gate, task, launcher, queue, or process.
3. A non-close gate transition is fresh, monotonically epoch-bound, fleet-secret HMAC authenticated,
   and exact-hash bound to doctrine, broker, project profile, complete inventory, qualified broker
   health, independent review, and tests. Exact canonical signed bytes are persisted and every gate
   read revalidates bytes, HMAC, epoch, expiry, digest, and duplicated binding columns. Forged, NULL,
   expired, noncanonical, or mismatched green state reports only CLOSED.
4. Quota identity is `provider/hmac-sha256:<hex>` derived from a host-local stable identity and a
   fleet secret. Raw or unkeyed account identifiers never enter requests, receipts, or doctrine.
5. A canonical state root is HMAC bound into the profile and its database name is fixed. Choosing a
   second SQLite path or state root cannot create an independent allowance. Multiple hosts require
   the shared-broker boundary above.
6. Every executable input and every schema uses strict UTF-8, duplicate-key rejection, non-finite
   rejection, bounded bytes/tree shape, Draft 2020-12 validation, explicit timezone parsing, stable
   reason codes, and empty-error/no-value-echo behavior.
7. Every supplied native capacity record is schema checked and HMAC authenticated before newest
   selection. A malformed newest record makes the set `UNEVALUABLE`; it is never skipped in favor of
   a stale record. Claude, OpenAI/Codex, Kimi, and Grok adapters accept only their exact v1 version.
8. Every required capacity dimension is present in the project profile, request estimate, and
   latest observation. Admission applies post-reset quiet, current use, active reservations, the
   new estimate, and the request priority's reserve floor to every dimension. Admission additionally
   requires `now < resetsAt` for every dimension; pre-reset evidence cannot cross a rollover.
9. Request replay is transactional. Any changed field under the same ID is
   `REQUEST_REPLAY_CONFLICT`. Cached prepared/allowed results are never authority: duplicate,
   restart, or broker-close replay is denied while its persistent lease remains fenced.
10. A fresh strict HMAC observer receipt first proves the actual child is suspended and binds PID,
    immutable start, loaded image path/digest, actual argv, request, session, seat, and seat epoch.
    A claimant also binds quota domain, exact executable path and digest, canonical argv and its model /
    effort / frozen-subject positions, launcher-config bytes, role, subject path and digest, opaque
    session, opaque seat and epoch, PID and immutable start time, context capsule, compaction
    checkpoint, cache-affinity manifest, and the canonical value and digest of all capacity estimates.
11. All final path, file, schema, HMAC, health, inventory, capacity, gate, subject, argv, and process
    checks run again after `BEGIN IMMEDIATE`. Pre-lock checks provide no launch authority.
12. The persistent claimant and active reservations remain until a fresh authenticated terminal
    receipt proves the exact PID/start/session/seat-epoch claimant; an arbitrary digest is not
    evidence. Lease wall time is not automatic release. LIVE or AMBIGUOUS orphan
    state, or any claimant mismatch, remains fenced. Orphan recovery additionally requires a fresh,
    fleet-secret-HMAC-qualified process-observer receipt; a caller-supplied `DEAD` enum is not proof.
    An authenticated AMBIGUOUS recovery observation for a CANARY transactionally reseals CLOSED
    before refusing release; malformed observations are schema/HMAC rejected before field access.
    The quota lock directory and file are canonical-handle/reparse checked, and transaction rollback
    after OS-lock acquisition releases the in-process handle while the persistent claimant remains
    fail-closed.
13. Inventory is fresh, rehashes every launcher, rejects duplicate canonical paths regardless of a
    claimed digest, and asserts exact configured/observed per-surface census of scheduled-task, app-
    scheduler, repository-wrapper, and service surfaces. Unknown, extra, direct-provider, unhashed,
    unbrokered, or count-mismatched launchers block.
14. Qualified broker health is fresh and HMAC authenticated. Missing, stale, future, forged, or
    hash-drifted health or capacity cannot admit.
15. CANARY requires a fresh, one-use, fleet-secret HMAC authorization bound to the entire canonical
    request except its unavoidable authorization-digest self-reference,
    quota domain, project profile, reviewer receipt, and short expiry. A non-null arbitrary digest
    is not authority. Only one canary may consume a gate epoch; any terminal success, failure, or
    ambiguity reseals CLOSED, and a new authorization ID cannot create a sequential canary.
16. An unchanged deterministic demand fingerprint produces a proof-bearing `IDLE_SKIPPED` with zero
    provider calls, processes, and token counters. It never enters the admission callable.
17. Evidence capsules consolidate lexical and hard-link aliases by stable retained file identity;
    conflicting alias digest or size denies. Each identity is opened once, every alias identity is
    rechecked, and one forward pass reads exactly the initial finite size plus at most one drift
    byte while hashing and capturing all slices from those identical bytes. Continuous growth and
    repeated aliases cannot amplify I/O beyond fixed ceilings. The temporary file is exclusively
    created and its handle/identity remains retained through atomic same-volume no-clobber linking,
    destination-identity proof, and an exact bounded destination-byte rehash. A link wrapper that
    raises after completing the exact link is verified as success; absent or foreign destinations
    fail without deleting foreign bytes. No branch check-then-unlinks a pathname. Windows temp
    disposal is attached to the retained DELETE-capable file handle; Linux prefers anonymous
    `O_TMPFILE` and selects, before writing, the ordinary-user `/proc/self/fd` plus
    `linkat(AT_SYMLINK_FOLLOW)` publication route. It never relies on privileged `AT_EMPTY_PATH`
    and never changes route after writing. A named fallback never path-deletes: refusal is returned
    as required `temporaryCleanup=REFUSED_BOUNDED`, creates one deterministic no-value block marker, and the deterministic
    `.tmp-owned` name prevents repeated accumulation. Public outputs are never path-cleaned after a
    failure, so a replacement occupant cannot be removed. Every retained admission artifact is
    likewise reread at resume using its exact retained size and ceiling plus at most one drift byte.
    Errors remain stable/no-echo.
18. Bounded turns, bounded context, exact capsules, milestone compaction, and cache affinity are
    efficiency controls only. They cannot change or weaken model, effort, role, frozen subject,
    independent-provider requirements, findings severity, product tests, or release/hardware gates.
19. Capacity enforces `lastResetAt <= observedAt < resetsAt`, bounded future skew, and a finite
    window. Requests have profile-bounded age and validity duration, not merely an expiry.
20. Candidate manifests hash canonical Git blob bytes across checkout EOL policies and include the
    manifest via an exact zeroed-field self-binding without recursive-digest claims.

## Provider-normalization dimensions

| Exact adapter | Mandatory dimensions |
|---|---|
| `claude-code/1.0` | `session`, `weekly` |
| `openai-responses/1.0` | `primary`, `secondary` |
| `kimi-code/1.0` | `context`, `monthly` |
| `xai-api/1.0` | `requests`, `tokens` |

Provider version drift is `UNEVALUABLE` until a separately reviewed adapter and fixtures exist.
Unknown dimensions are not selected away. A project may require more dimensions, never fewer.

## Adoption contract

Doctrine merge alone does not activate a project. Each project must publish one exact disposition:

- `ADOPT(<canonical commit>, <profile hash>, <review receipt>)`;
- `DISTINGUISH(<portable invariants>, <local difference>, <proof>)`; or
- `REJECT(<specific contradiction>, <proof>)`.

Before any canary, the project must prove its state root and broker singleton, all four census
surfaces, direct-invocation prohibition, fake-provider refusal and concurrency controls, 1,000
unchanged zero-inference ticks, full-child claimant/OS-lock behavior, rollback, and current CLOSED
gate. A canary is separately authorized, one per quota domain, bounded, and automatically returns
to CLOSED on ambiguity or failure. User-present hardware and project release gates are unchanged.

## R7 evidence map

The hostile suite in `tests/test_universal_provider_control.py` reproduces every retained
reconciliation finding: unenforced schemas; malformed-newest fallback; unkeyed identity; permissive
or unbounded intake; value/path error echo; parallel-contract gate/idle omissions; missing persisted
gate; missing inside-lock revalidation; basename executable identity; disappearing capacity
dimensions; frozen-subject TOCTOU; unqualified health; incomplete inventory; telemetry-failure
admission; multi-host split-brain; arbitrary canary hashes; and capsule check/use races.

The suite retains exact d98934c R1-red/R2-green discriminators and exact 4fc0fe1
R2-red/R3-green twins for expiry, rollover, capsule handle/cleanup, estimate binding, and ambiguous
CANARY recovery findings. It adds exact 1c06687 R3-red/R4-green twins proving same-pass bound bytes,
fixed expected-size-plus-one growth work, and no-clobber publication that preserves a racing foreign
destination on both supported operating systems. It adds exact b48c882 R4-red/R5-green twins for
retained temp/publication identity and bytes, foreign temp collisions, bounded retained-artifact
resume reads, 64-hardlink alias consolidation/conflicts, and a link wrapper that raises after a real
link. The candidate's author is recused from review and adjudication.

Exact 58e4146 R5-red/R6-green twins prove private and public replacement occupants survive the
cleanup boundary, cleanup refusal is surfaced and repetition-bounded, and the complete 83-control
suite passes unchanged production behavior on Python 3.13 and 3.14. The candidate's author remains
recused from review and adjudication.

Exact 300e2bb R6-red/R7-green twins prove ordinary unprivileged Linux anonymous-file publication
uses the capability-free exact-fd route, `temporaryCleanup` is mandatory runtime evidence, cleanup
helper exceptions are contained behind stable no-echo refusal results, and the successful cleanup
path remains green. The 87-control universal suite and retained 37-control governor suite run on
both Python 3.13 and 3.14; the dual-platform hosted matrix remains required before adjudication.
