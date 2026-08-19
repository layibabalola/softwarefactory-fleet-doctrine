# Universal provider-control reconciliation R24

Status: **CANDIDATE / ZERO AUTHORITY / NO DEPLOYMENT**

Issue: <https://github.com/layibabalola/softwarefactory-fleet-doctrine/issues/4>

Reconciliation input comment:
<https://github.com/layibabalola/softwarefactory-fleet-doctrine/issues/4#issuecomment-5332348238>

Exact immutable parents: certified-boundary WIP `00542530bfebad8ad7646724f64720adda8d1b49`
and ratified R14 directory-owner subject `874605e43531c9aa230ee16851f8107a8e0d9cec`.

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
The resume boundary rejects `now >= lease.expires_at` and `now >= capacityValidUntil`, where
`capacityValidUntil` is the earliest authenticated `resetsAt` across every estimated capacity
dimension at preparation. Expiry or rollover never releases the persistent claimant, reservation,
OS lock, or artifact handles, and an expired or rolled-over CANARY attempt reseals CLOSED.

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
   expired, noncanonical, or mismatched green state reports only CLOSED. Forward rollout is strictly
   `CLOSED -> SHADOW -> CONTAINMENT -> CANARY -> OPEN`; skipping a stage or moving directly from
   CLOSED to OPEN is refused. A safety close may return any stage to CLOSED.
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
     effort / role / turn / context / cumulative-token-ceiling / frozen-subject positions,
     launcher-config bytes, an exact reviewed provider/adapter/model/effort/role/executable allowlist
     entry, subject path and digest, opaque
     session, opaque seat and epoch, PID and immutable start time, context capsule, compaction
     checkpoint, cache-affinity manifest, current and prior demand fingerprints, the canonical value
     and digest of all capacity estimates, and the earliest capacity-valid boundary. The resulting
     launch attestation repeats those identities and ceilings; a launch wrapper cannot silently select
     a cheaper model, weaker effort, different role, or larger resource envelope.
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
16. The broker recomputes current and prior deterministic demand fingerprints from the retained,
    byte-hashed addressed-work and cursor inputs; caller-supplied current or prior fingerprints are
    assertions to verify, never trusted truth. Equal broker-computed fingerprints produce a
    proof-bearing `IDLE_SKIPPED` with zero provider calls, processes, and token counters. It never
    enters the admission callable.
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
    and never changes route after writing. The POSIX anonymous descriptor is explicitly owned until
    `fdopen` succeeds; an injected `fdopen` failure closes that descriptor exactly once before any
    fallback or propagation. The target-directory descriptor used by `linkat` is also an explicit
    attempt-once owner: false, exception, or ambiguous close retains the exact descriptor, creates
    process-wide cleanup poison, and remains refusal even after the public link's identity and bytes
    verify exactly. Windows likewise tracks the sole owner across native handle, CRT
    descriptor, and file-object states; every failed transfer arms retained-handle deletion and
    closes exactly the current owner. A named fallback never path-deletes: refusal is returned
    as required `temporaryCleanup=REFUSED_BOUNDED`, creates one deterministic no-value block marker, and the deterministic
    `.tmp-owned` name prevents repeated accumulation. Public outputs are never path-cleaned after a
    failure, so a replacement occupant cannot be removed. Every retained admission artifact is
    likewise reread at resume using its exact retained size and ceiling plus at most one drift byte.
    Owner state detaches only after one verified close outcome. Unproven temporary, publication,
    source, or admission-artifact owners remain retained and surfaced; their deterministic refusal
    fence blocks repetition. `temporaryCleanup=CLEAN` is assigned only after discard and every
    required close prove success. Windows checks the BOOL and `GetLastError` outcome of both delete
    disposition and `CloseHandle`; false, exception, or ambiguous results are cleanup refusal.
    Any unproven capsule owner creates a process-wide cleanup poison before control returns. The
    first bounded owner set is retained exactly once without retry; every later capsule request,
    including one rotating to a distinct output path, denies before acquiring a source, temporary,
    or output handle. An explicit process-close assertion surfaces outstanding poison. Admission
    artifacts use the same rule at broker scope, keyed to the canonical state root rather than a
    random request or lease: terminal release cannot reopen acquisition, fresh request/broker
    rotation denies before authorization artifacts are acquired, and broker close cannot silently
    discard outstanding poison. POSIX anonymous-descriptor close catches every exception class,
    retains the sole descriptor owner, and establishes the process-wide fence before returning a
    stable refusal. Within one process, every broker object for the same canonical state root shares
    one root-scoped owner registry and reentrant lock. Poison check, artifact acquisition, lease and
    confirmation publication, authenticated terminal/recovery, cleanup-poison publication, and
    administrative assertion are linearizable across those objects and threads. Admission has a
    four-prepared-lease root quarantine ceiling before artifact acquisition; six retained executable,
    config, capsule, checkpoint, cache, and subject artifacts per lease therefore give an exact
    24-owner refusal bound, and every owner of every already-
    prepared lease remains retained. OS-lock unlock and close have distinct attempt-once states;
    the handle is not removed until close is proven, and an unproven close remains retained and
    poisons later admission. `close()` and `__del__` are administrative assertions only: they never
    release an ACTIVE or RESUME_ATTESTED child, OS lock, or artifact. Only authenticated terminal or
    DEAD recovery can do that. The owner registry and poison are honestly process-local; SQLite
    claimant rows and OS quota locks are the cross-process fence. Process exit releases kernel
    handles, while a surviving process can clear no poison by constructing another broker object.
    Errors remain stable/no-echo: the complete public capsule boundary, including preflight and all
    handlers/finalizers, raises a new `ControlError` only after private exception state has cleared,
    with no private `__cause__`, `__context__`, or formatted traceback content.
18. Bounded turns, bounded context, cumulative input/cache-read/cache-write/reasoning/output ceilings,
    exact capsules, milestone compaction, and cache affinity are enforced launch-envelope controls.
    Every bound is profile-limited, argv-bound, digest-bound, and repeated in the launch attestation.
    They cannot change or weaken model, effort, role, frozen subject, independent-provider
    requirements, findings severity, product tests, or release/hardware gates.
19. Capacity enforces `lastResetAt <= observedAt < resetsAt`, bounded future skew, and a finite
    window. Requests have profile-bounded age and validity duration, not merely an expiry. The
    earliest `resetsAt` is persisted in the prepared lease, binding digest, and attestation; the
    final `BEGIN IMMEDIATE` confirmation refuses `confirmAt >= capacityValidUntil`, retaining all
    fences and transactionally resealing a CANARY CLOSED.
20. Candidate manifests hash canonical Git blob bytes across checkout EOL policies and include the
    manifest via an exact zeroed-field self-binding without recursive-digest claims. Both checker
    and hostile test read the indexed/committed Git blob, never checkout bytes; an explicit LF/CRLF
    discriminator proves checkout conversion cannot redefine the subject.
21. Named hard-link publication and the ordinary-user `/proc/self/fd` plus
    `linkat(AT_SYMLINK_FOLLOW)` route pass through one explicit no-clobber syscall seam. Hostile race,
    foreign-source, replacement, and link-then-raise controls patch that exact seam, so Ubuntu cannot
    silently execute an unmutated production syscall while the test patches only `os.link`.
22. Production provider access requires a separately installed and reviewed process/service choke
    point; an in-process callback is never such a boundary. The choke point must invoke the exact
    pinned provider/adapter executable with the exact argv length, order, and values, keep fleet and
    observer secrets outside the provider process and its parent-frame reach, and make raw provider
    entrypoints structurally unavailable. Admission reserves
    the full input/cache-read/cache-write/reasoning/output envelope and a terminal-output reserve in
    SQLite before resume. The production boundary must obtain exactly one HMAC-bound permit immediately before
    its sole provider request; a second permit, a terminal count mismatch, missing permit digest, or
    any reported usage above a reserved class is fail-closed. Prepared binding bytes and their fleet-
    secret HMAC are immutable; final confirm and pre-request issuance compare the lease, attestation,
    earliest capacity boundary, exact argv template/count/order, launcher configuration, quality
    cell, and certification digest transactionally.
23. Runtime authority ends at the earliest request, lease, capacity, or watchdog boundary. A
    broker-owned advancing clock is re-read immediately before each provider call/turn and after
    every blocking operation; caller-supplied time is not runtime authority. The separately certified
    process/service boundary must enforce wall time, output limits, process-tree ownership, and terminate on
    `RUNTIME_TERMINATION_REQUIRED`; the broker persists that state without releasing claimant, OS-
    lock, artifact, or token fences. Process-id/start-time pairs are permanently claimed so a serial
    launch cannot reuse a stale observation after release.
24. Demand is a strict broker-normalized semantic snapshot of addressed work and cursor identity.
    Object formatting and work-list order cannot create work. Prior-idle identity is a broker-owned,
    state-root-bound HMAC receipt, so callers cannot select arbitrary raw files or hashes. Capacity
    reservation fractions are derived conservatively from the complete token envelope and the
    reviewed adapter budget; caller-supplied fractions are forbidden.
25. The universal quality floor independently requires the canonical priority-to-role mapping,
    `high` effort, `FRONTIER_HIGH`, a frontier model family, and an exact reviewed cell that includes
    quality-equivalence, executable, launcher-config, argv-contract, single-request certification,
    and watchdog certification. A project cannot self-label a tiny/minimal cell as equivalent.
26. Rollout proofs are typed, fresh, one-use, HMAC-bound, and chained to the prior transition,
    profile, inventory, hosted negative suite, and independent review. A successful CANARY produces
    a token/permit-bound success receipt and returns automatically to unsigned fail-closed
    CONTAINMENT. Only a later CONTAINMENT-to-OPEN adjudication may consume that receipt once;
    CANARY-to-OPEN and stage skipping are forbidden. Quota-domain OS locks live in one canonical
    per-account host namespace, independent of caller-selected state roots.

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
unchanged zero-inference ticks, full-child claimant/OS-lock behavior, rollback, exact reviewed role
profiles, and the sequential CLOSED, SHADOW, and CONTAINMENT evidence. A canary is separately
authorized, one per quota domain, bounded, and automatically returns
to CLOSED on ambiguity or failure. User-present hardware and project release gates are unchanged.

## R14 evidence map

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

Exact 019d1c4 R7-red/R8-green twins prove primary and cleanup failures retain no private exception
chain or formatted traceback content, Windows native-handle-to-CRT-to-file-object transfer failures
dispose exactly the current owner, and POSIX `O_TMPFILE` descriptor transfer closes once on failure
without double-close on success. The candidate author remains recused.

Exact d350e7c R8-red/R9-green twins prove CLEAN requires verified disposition and every close,
unproven publication/source/admission-artifact owners remain retained after exactly one attempt,
preflight and finalizer exceptions are fully sanitized, Windows false disposition/CloseHandle
outcomes deny with a bounded fence, and POSIX anonymous-descriptor close refusal blocks repetition.
The candidate author remains recused.

Exact fe060bf R9-red/R10-green twins prove a capsule cleanup refusal poisons the entire process
before a distinct output can acquire handles, an admission-artifact refusal poisons the canonical
broker state root before fresh lease/request rotation can reacquire artifacts, process/broker close
surfaces the outstanding poison, and a non-`OSError` POSIX anonymous-descriptor close failure retains
the sole owner and blocks repetition. The 102-control universal suite and retained 37-control
governor suite run on Python 3.13 and 3.14; hosted Windows and Ubuntu checks remain required before
adjudication. The candidate author remains recused.

Exact bd9c559 R10-red/R11-green twins prove a terminal cleanup refusal linearizes before concurrent
authorization, confirmation, and close across distinct same-root broker objects; no PREPARED or
ALLOW result can appear after poison. Four prepared provider leases fill the pre-acquisition
quarantine and all 24 possible refused artifact owners remain retained without overflow or retry.
RuntimeError unlock and OSError close failures have attempt-once, no-echo OS-lock ownership, and
administrative close/destruction preserves active child authority until authenticated terminal
release. The 106-control universal suite and retained 37-control governor suite run on Python 3.13
and 3.14; hosted Windows and Ubuntu checks remain required before adjudication. The candidate author
remains recused.

Exact 52ca345 R11-hosted-red/R12-green twins bind the failed PR #10 run `32196027799`: Windows
Python 3.13/3.14 no longer derives manifest self-hashes from CRLF checkout bytes, and Ubuntu Python
3.13/3.14 now injects the foreign-race and source-substitution mutations through the actual anonymous
`linkat` publication seam. The prior exact R11 tests are retained as RED evidence, expectations are
unchanged, and no test is skipped. The 108-control universal suite and retained 37-control governor
suite run locally on Python 3.13 and 3.14; a fresh hosted Windows/Ubuntu run on exact R12 bytes remains
required before adjudication. The candidate author remains recused.

R14 retains immutable R13 commit `ecc8f07` and replaces its full-history checkout and predecessor
preflight with self-contained current canonical-blob and live publication-seam controls. It adds five
hostile repair groups:
prepare-before-reset and confirm-after-reset denial with retained fences and CANARY reseal; exact
reviewed provider/adapter/model/effort/role/executable admission; argv and attestation binding for
turn, context, and every cumulative token ceiling; broker recomputation of both current and prior
demand from frozen addressed-work/cursor bytes; and enforced CONTAINMENT with stage-skip refusal.
The 113-control universal suite and retained 37-control governor suite must pass on the exact R14
bytes; fresh hosted Windows/Ubuntu checks remain required before adjudication. The candidate author
remains recused.

R15 linearly binds certified-boundary WIP `00542530bfebad8ad7646724f64720adda8d1b49`
(itself preserving adverse R14 commit `8eee3e4576778a18f92a3aff922c7574904e3fc3`) and ratified
directory-owner subject `874605e43531c9aa230ee16851f8107a8e0d9cec` without rewriting either.
The exact native R14 hostile twin proves the target-directory descriptor is closed once or retained
as process-wide cleanup poison even after a verified link. Seven R15 hostile groups prove persistent one-request permits,
semantic demand plus broker-owned idle receipts, immutable binding-HMAC comparison, runtime expiry
termination state, universal quality and exact argv/config review, alternate-state-root OS-lock
contention, and successful-canary return to CONTAINMENT followed by one-use receipt adjudication.
The 121-control universal suite and retained 37-control governor suite must pass on exact R15 bytes
on Python 3.13 and 3.14 for Windows and Ubuntu. The candidate invokes no provider, grants no runtime
authority, and the author remains recused from review, adjudication, merge, and activation.

R16 preserves exact R15 merge `30cd9b97eeebd30cb209bdb9798c38b415c9a0b4`, freezes its linear
provider-accounting implementation at `a560c63cbe72736efe4e1d5c3ecfac25d04f68d2`, reconciles through
ordered-parent merge `a0786f2eee16770632a2a947f65db64e60dd9820`, then binds canonical fleet
master `cd21e5830ccb894af5847ce113af8a7d6570748a` at merge
`c6bc94fe3afcdbc927641164fd2d42c621c0bb67`. The merge retains every current project disposition.
Thirteen R16 hostile groups prove broker-persisted fresh/monotonic/one-use prior-idle receipts;
profile-pinned canonical demand; pre-call, per-turn, context-peak, cumulative-token and terminal
reserve accounting; cross-root durable claims that survive owner loss until authenticated recovery;
immutable issued/expiry/capacity/watchdog bindings; typed HMAC quality and wrapper certifications;
typed process-tree termination and output-quality reconciliation; a same-process broker permit CLI
that cannot spawn a provider; completed usage across serial leases; monotonic termination that cannot
mint canary success; canonical schema/HMAC/digest/epoch validation of stored canary receipts; and
exact-key request-permit token ceilings. The candidate remains zero authority and makes no provider
call; the author remains recused from review, adjudication, merge, and activation.

R17 is preserved adverse evidence atop R16 subject
`0daf7b003932b611a01e5a4b5c50848b96873ca1`. Its in-process callback wrapper was not a certified
execution boundary: callback frame inspection could reach broker secrets, caller-selected time could
freeze a lease boundary, and usage could be spent before completion-reserve enforcement. Exact R17
freeze `868265b3044c9d59753f9c01b446a4e933a08629` therefore grants no containment or canary credit.
Every usage checkpoint is canonical, HMAC-authenticated, previous-digest chained, and bound to a signed
mutable head. A terminal permit freezes the checkpoint digest, sequence, and output baseline; later
ordinary turns are forbidden and terminal output may increase only by the reserved completion allowance.
Demand authority is read once under stable identity and rotated through a signed monotonic pin chain.
Independent termination and quality observers bind fresh retained evidence, candidate/reference output,
the exact subject, and immutable launch binding. Cross-root quota claims use PREPARED/ACTIVE and
RELEASE_PREPARED/global-RELEASED/local-RELEASED ordering; local success or canary evidence cannot precede
durable release, and orphan recovery charges the latest verified use or the full conservative reservation.
The canonical quota database uses a signed instance identity,
stable descriptor checks, DELETE journaling, and usage ledgers partitioned by every capacity dimension and
reset window. The candidate remains deployment-inert until independent review, adjudication, merge, and a
separate staged activation decision.

R18 advances additively from exact R17. Durable PREPARED claims use deterministic HMAC lease identity.
Admission consumes the newest unused prior-idle receipt and
verifies the newest current authority pin, its HMAC, exact retained snapshot, monotonic epoch, and prior
pin link. Once a provider permit exists, dead/nonterminal recovery charges the full reservation unless
independent terminal evidence proves the exact final usage. Ledger and lock authority resolve from the
OS account database/known profile, not HOME or USERPROFILE. The reference implementation deliberately
has no provider callback, wrapper
capability, provider spawn, resume, watchdog, or kill surface; `directInvocationImpossible=false` and
`reference-only-no-execution` are schema-bound. A project must supply the separate production choke
point described by laws 22-23 and independent retained observer evidence before any staged authority.
Merging, ratifying, or locally adopting R18 leaves every automatic gate CLOSED and grants zero
containment, canary, or OPEN authority.

R19 preserves exact frozen R18 `cfb39bbb1da4476d241cc734a1ce007db168c274` and repairs its
restart-time convergence gap without adding execution authority. PREPARED lease time is anchored to
the latest of the authenticated request issue, exact suspended-process start, and non-future signed
process observation, so a restart with an
advancing broker clock reproduces the same binding and lease while never extending the original wall,
request-expiry, or capacity boundary. A claimant that cannot reproduce the exact process and binding
remains durably fenced. The canonical OS-account authority root itself, as well as its ledger, lock
directory, database, and lock children, rejects symlinks, junctions, and reparse points. Observer IDs
must differ from one another; observer key hashes must differ from one another, the fleet signer key,
and the wrapper executable, provider executable, launcher configuration, and argv-contract digests.
The separately retained independent-review digest must also differ from those launch artifacts.
Distinct observer processes and operators remain a production deployment prerequisite, not something
this no-execution reference can prove. The reference test harness redirects the canonical quota
authority to a deterministic per-test temporary root before any broker construction and proves the
persistent account ledger is unchanged. R19 remains zero authority: provider execution, process
resume/kill, containment, CANARY, and OPEN credit are all unavailable, and adoption leaves CLOSED.

R20 preserves exact frozen R19 `f62b916eb952d9515a785334b7fcc5f204155a3b` without adding any
execution surface. `authorize_suspended_child` obtains exactly one broker-owned UTC sample before the
canonical root lock, rejects a caller timestamp outside the permitted skew, and uses the same sampled
instant for the entire serialized admission or retry. A stale caller cannot replay an expired lease; a
future caller cannot extend it; and an injected advancing broker clock proves restart convergence while
retaining the original expiry. Production uses real UTC and tests inject a deterministic clock.

The canonical OS-account authority validation walks every component from the trusted account base to the
authority root before either the quota ledger or quota lock is used. Existing symlink, junction, or reparse
components fail closed, while absent ordinary directories are created and revalidated one component at a
time. The rule is based on component identity rather than lexical resolved-path spelling, avoiding Windows
8.3 aliases as a false-positive heuristic. Real Windows junction/POSIX symlink twins and a portable mocked
component test cover both ledger and lock access.

The same universal provider-capacity workflow that validates the exact candidate on pull requests and
master pushes now runs all canonical `capacity-control/tests/test_*.py` workbench negatives in addition to
the universal and governor suites. R20 remains a zero-authority reference: provider execution, process
resume/kill, containment, CANARY, and OPEN credit remain unavailable, and adoption leaves CLOSED.

R21 preserves exact frozen R20 `962dc355cf2049309bedbda48e4a1a174776745f`. The initial broker-clock
sample exists only to reject a stale or future caller timestamp before serialization. Admission obtains
a new broker-owned sample immediately after the canonical root lock and local SQLite write lock, then
again after the quota-domain OS lock and durable quota-ledger write lock. The latest sample governs every
freshness, rollover, admission-deadline, lease, persistence, and activation decision. A contended lock
that advances past any request, process, health, inventory, capacity, prior-idle, certification, canary,
gate, or lease deadline cannot return an activatable PREPARED result. Restart convergence still derives
the same immutable lease identity and never extends the original deadline.

On POSIX, the OS passwd home is the account authority source. If `.local/share` is absent, each component
is created relative to a retained parent descriptor and reopened with `O_DIRECTORY|O_NOFOLLOW`; UID,
directory type, and non-group/world-writable mode are checked after creation. Windows token-profile
resolution is unchanged. From that trusted base through `SoftwareFactory/provider-control`, every
directory identity is captured and revalidated immediately before and after opening either the canonical
ledger or quota lock. A deterministic or native directory replacement fails closed and poisons the
authority for the process rather than falling through to a substituted database or lock namespace.

R21 also makes serialized attended rotation explicitly insufficient for provider containment. Before a
model process or session is created, a deterministic broker-owned no-work decision must prove that the
addressed-work capsule is actionable. Every actual provider request, rather than only an agent turn,
must reserve and reconcile a token-denominated quota envelope. Cache reads count at full input-envelope
and quota-window weight; cache writes, uncached input, reasoning, and output are separately cumulative.
Failure, refusal, timeout, and retry attempts consume the same accounting path, and the reviewed policy
sets a numeric retry cap. Admission must retain at least 20 percent of every applicable provider quota
window for completion and terminal reporting after active, completed, and candidate reservations.

The assembled prefix and addressed-work capsule each have reviewed numeric token ceilings enforced before
session creation. Cache-affinity scheduling may reuse a prefix only under an exact affinity identity and
an unexpired TTL; after expiry, admission budgets a cold prefix instead of assuming a cache hit. Direct
provider launch is denied only by positive, separately certified production choke-point enforcement;
serialization, a declaration, or this no-execution reference cannot prove that boundary.

The normative machine-readable admission laws are:

```text
CACHE_READ_FULL_ENVELOPE_WEIGHT=1.0
REQUEST_LAYER_RECONCILIATION=REQUIRED
MODEL_FREE_NO_WORK=BEFORE_SESSION_CREATION
MAX_ASSEMBLED_PREFIX_TOKENS=REVIEWED_NUMERIC_REQUIRED
MAX_ADDRESSED_WORK_CAPSULE_TOKENS=REVIEWED_NUMERIC_REQUIRED
CACHE_AFFINITY_TTL=EXACT_IDENTITY_AND_UNEXPIRED_TTL
MAX_PROVIDER_RETRIES=REVIEWED_NUMERIC_REQUIRED
COMPLETION_RESERVE_FLOOR=0.20
POSITIVE_DIRECT_LAUNCH_ENFORCEMENT=SEPARATELY_CERTIFIED_REQUIRED
```

The attended four-request rotation that motivated these laws was serialized and no-tools, but still
created 59,319 cache-prefix tokens and read 10,723 cached tokens across one Sonnet and three Opus calls.
It is PRE-SHADOW SEALED evidence only: it earns no ratification, adoption, containment, or activation
credit. R21 retains the universal hosted workflow's exact 168-control universal, 37-control governor,
and 77-control runtime-workbench matrix on pull requests and master pushes. It adds no provider execution,
process resume/kill, containment, CANARY, or OPEN authority; adoption remains CLOSED.

R22 preserves exact frozen R21 `4bca2c36ca69a584cc4c506ad36f1cef66fefab3` and additively
reconciles canonical master `44a33fce7fb0b0f5c17b576397d7d0e0fc9b0c35` through ordered-parent
merge `3b8f957ea8e05cf6629c02ec7ea39e8c961b9396`. The stable authority
snapshot includes the exact direct child used by each surface: `quota-ledger` for the canonical
SQLite database and `quota-locks` for the OS-lock namespace. Both child identities are checked along
with the full trusted ancestor chain immediately before and after open/use under the relevant lock.
Replacing either child directory through the deterministic publication seam or a native rename/recreate
twin poisons the process authority and fails closed.

The privacy-safe receipt at `receipts/attended-provider-rotation-20260819.json` binds four serialized,
one-turn, no-tools successes without session identifiers, local paths, or prompt/output content. It
retains only role/model, UTC timing, terminal metadata, prompt/output hashes, and token counts. Strict
schema and semantic validation reject duplicate roles/hashes, ordering overlap, invalid types/ranges,
and any aggregate drift from 7 input, 59,319 cache-create, 10,723 cache-read, and 7,540 output tokens.
Its public provenance is issue #4 comment `5337603712`; the disposition is PRE_SHADOW_SEALED,
`providerAuthority=false`, and `adoptionCredit=false`.

The nine R21 token laws are executable data in `policy/universal-provider-token-control-r22.json`
under `schemas/universal-provider-token-control-policy-v1.schema.json`. The policy fixes request-level
reserve/reconcile, full cache-read weight, pre-session model-free no-work, numeric prefix/capsule and
retry ceilings, exact cache-affinity TTL with cold-prefix fallback, conservative failed/refused/timed-out
attempt charging, a 20 percent every-window completion reserve, and separately certified positive
direct-launch enforcement. R22 adds no provider execution, process resume/kill, containment, CANARY,
or OPEN authority; adoption remains CLOSED.

The exact R22 candidate is validated by 175 universal controls, 37 retained governor controls, and
78 canonical runtime-workbench controls on Python 3.13 and 3.14. Hosted Windows and Ubuntu checks on
the frozen subject remain required and unclaimed.

R23 preserves exact frozen R22 `91f2d940c39bd15a76074a59deaeee8d13936fad` without changing
broker mechanics or runtime authority. The attended receipt defines `wallDurationMs` as
`floor((completedAt-startedAt) / 1 millisecond)`. `durationMs` means
`CLAUDE_CLI_REPORTED_END_TO_END`, `durationApiMs` means
`CLAUDE_CLI_REPORTED_API`, and `wallDurationMs` means `HOST_OBSERVED_WALL`. Validation requires
`0 <= API <= CLI <= wall`, at most 10,000 ms outside the reported API, and at most 5,000 ms host
overhead/timestamp rounding outside the CLI duration. The four wall durations are 34,299, 59,757,
26,400, and 30,577 ms; aggregate wall time is 151,033 ms.

Receipt provenance is strictly `AUTHOR_ATTESTED_LOCAL_CLI_MEASUREMENT`: `providerAuthenticated`,
`independentObserver`, `rawProviderReceiptCommitted`, and `authorityCredit` are all false. The public
issue URL is informational and optional for schema/semantic validation. Token totals have
`MOTIVATION_AND_MEASUREMENT_ONLY` credit and cannot satisfy provider authentication, independent
review, adoption, containment, CANARY, OPEN, or activation evidence. R23 remains zero authority and
CLOSED.

The exact R23 candidate is validated by 177 universal controls, 37 retained governor controls, and
78 canonical runtime-workbench controls on Python 3.13 and 3.14. Hosted checks remain required and
unclaimed; validation and publication do not grant authority.

R24 preserves exact frozen R23 `ac2db2152fe23aa989745d36a71c67d33da4c89f`. Canonical receipt
timestamps use uppercase `T`/`Z`, UTC only, calendar-valid whole seconds, and zero to nine decimal
fractional digits. Validation parses the whole second and right-pads the fraction to nine digits,
forming integer epoch nanoseconds before subtracting and flooring by 1,000,000. It never truncates to
`datetime.microsecond`: an exact 1.9992 ms delta floors to 1 ms, 0.9999 ms floors to 0, and 2.0000 ms
floors to 2. Offsets, lowercase `z`, malformed dates, and more than nine fractional digits fail closed.
The exact four receipt rows still recompute 151,033 ms wall time and unchanged token totals. R24 changes
no broker mechanics or authority; it remains evidence-only, zero authority, and CLOSED.

The exact R24 candidate is validated by 179 universal controls, 37 retained governor controls, and
78 canonical runtime-workbench controls on Python 3.13 and 3.14. Hosted checks remain required and
unclaimed; validation and publication do not grant authority.
