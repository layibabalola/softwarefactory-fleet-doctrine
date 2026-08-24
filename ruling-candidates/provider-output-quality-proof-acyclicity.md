# Provider output-quality proof must be acyclic (R1 candidate)

> **STATUS: CANDIDATE / ZERO AUTHORITY.** This document proposes portable doctrine.
> It does not relax output quality, admit a provider request, release a lease, approve
> an installation, or grant adoption credit.

## Problem

A governed provider call cannot honestly certify its own semantic quality. The same
is true when its reviewer is another governed provider call whose release requires a
semantic-quality receipt first. That design creates a recursive authority cycle:

1. call A cannot release without an independent semantic noninferiority receipt;
2. reviewer call B is expected to justify A;
3. B cannot return its verdict because B also cannot release without an independent
   semantic noninferiority receipt;
4. any further reviewer repeats the cycle.

Implementations often mask this by checking only that a file named “quality receipt”
exists and has a hash, by comparing an output to itself, or by letting the governed
launcher hold the reviewer signing key. Those are integrity checks or self-attestation,
not independent quality proof.

## Proposed contract

### 1. Separate per-call output-contract proof from semantic quality proof

Every provider call still fails closed unless a distinct, independently accepted
output-contract evaluator proves:

- exact provider, model, effort, role, sandbox, approval, request, and artifact
  identities;
- output-schema validity and role-specific deterministic invariants;
- retained stdout, stderr, output, usage envelope, and process-tree termination;
- bounded turns, wall clock, context, token use, and complete descendant cleanup;
- no missing, stale, malformed, self-referential, or drifted evidence.

This receipt may authorize terminal lease release because it makes only deterministic
claims. It must not call itself semantic noninferiority, and its signer must not be the
provider process or mutable launcher under evaluation.

### 2. Semantic quality requires an acyclic root of trust

Semantic noninferiority remains mandatory for:

- adoption canaries and promotion of an installed fingerprint;
- both required production cadences;
- material model, effort, role, prompt, schema, wrapper, parser, or policy changes;
- continuing risk-based samples after adoption; and
- any due sample after a quality regression, unexplained drift, or evidence gap.

The semantic verdict must originate from an independently accepted evaluator whose
authority does not depend on the governed call it certifies. Lawful roots include a
human adjudicator, an offline deterministic domain oracle, a separately governed
evaluation service with already-proven nonrecursive authority, or a frozen blind
baseline/corpus with an independently reviewed rubric. A second model call is not
independent merely because its role or session id differs.

### 3. No vacuous reference or signer collapse

A candidate output cannot serve as its own reference. A generated reference is valid
only when its generation predates and is independent of the candidate route. The
output-contract evaluator, semantic reviewer, provider launcher, usage parser, and
lease releaser expose distinct identities and signing keys where their claims differ.
One component may not silently mint another component’s receipt.

### 4. Sampling never weakens fail-closed quality preservation

After a stable installed fingerprint has passed canary and cadence proof, ordinary
calls may release on deterministic output-contract proof while semantic comparison is
performed on the accepted risk-based schedule. A due, failed, stale, or ambiguous
semantic sample closes promotion and the affected production route until adjudicated.
Sampling frequency is project-local and evidence-based; “not every call” is not
permission to skip required canary, cadence, change-triggered, or due checks.

### 5. Receipt classes are explicit

Schemas and launch seams name receipt classes precisely. `outputContractReceipt` and
`semanticQualityReceipt` are not interchangeable. A path-plus-hash check cannot prove
either schema, signer, freshness, independence, or claim. Every consumer validates the
closed-key object, signer, subject, request, installed fingerprint, freshness window,
and applicable release policy before granting its narrow authority.

## Minimum portable proof

A project may adopt this ruling only after negative and positive controls prove:

1. an arbitrary hash-bound `{}` file cannot satisfy either receipt class;
2. a provider call cannot sign or select its own semantic-quality verdict;
3. a reviewer call recursively governed by the same semantic pre-release rule is
   detected as an authority cycle, not treated as independent;
4. candidate-equals-reference and post-candidate reference generation are refused;
5. deterministic output-contract failure prevents terminal release;
6. a valid output-contract receipt cannot grant canary, cadence, promotion, or
   semantic-quality credit;
7. canary promotion fails without a fresh acyclic semantic noninferiority receipt;
8. both production cadences bind the accepted installed fingerprint and semantic
   quality evidence;
9. a due, stale, failed, or ambiguous continuing sample closes the affected route;
10. signer collapse, schema substitution, replay, cross-request reuse, and receipt
    class substitution are refused;
11. changing provider, model, effort, role, prompt, schema, wrapper, parser, evaluator,
    or policy resets the applicable semantic proof; and
12. terminal release, adoption credit, and promotion each consume only the receipt
    class explicitly authorized for that decision.

Project-local evaluator implementations, sampling intervals, prompts, corpora, keys,
paths, providers, and rollout mechanisms do not travel. Sibling projects adopt through
their authority map and production-path proof or publish `DISTINGUISH(reason)`.

The privacy-safe DNG falsification receipt at
[`receipts/dng-quality-release-acyclicity-finding-20260824.json`](../receipts/dng-quality-release-acyclicity-finding-20260824.json)
motivates this candidate. The same field trial includes a provider-free deterministic
observer prototype that passed 23 hostile fixture assertions and 46 manifest/schema/
dependency checks while setting `semanticNoninferiorityClaimed=false`. It grants no
independent acceptance or adoption credit. A second zero-authority prototype applies
the proposed receipt separation to terminal release, next-route closure, and promotion:
29 hostile cases plus 41 manifest/dependency checks passed. Its privacy-safe evidence is
[`receipts/dng-acyclic-release-policy-prototype-20260824.json`](../receipts/dng-acyclic-release-policy-prototype-20260824.json).
Pre-seam falsification then found that the r1 decision omitted its context and artifact
bindings. The immutable r2 descendant returns the exact context, request, provider binding,
output, and receipt identities; it passed 41 hostile assertions and 45 verification checks.
The r1 prototype remains historical zero-authority evidence and is superseded for acceptance
by [`receipts/dng-acyclic-release-policy-replay-repair-20260824.json`](../receipts/dng-acyclic-release-policy-replay-repair-20260824.json).
The first project integration descendant now also separates execution from release:
provider execution may emit only a hash-bound `PENDING_RELEASE` evidence object, with
terminal usage and process-tree termination retained. It refuses both the legacy generic
quality artifact and premature success status. The provider-free seam passed 20 fixture
assertions and 45 verification checks; see
[`receipts/dng-mu3-pending-execution-phase-split-20260824.json`](../receipts/dng-mu3-pending-execution-phase-split-20260824.json).

Finalizer integration exposed a Windows byte-integrity defect in the r1 deterministic
observer: it hashed LF bytes before an exclusive text-mode descriptor wrote CRLF bytes.
Observer r2 uses an exclusive binary descriptor and proves the returned hash equals the
retained receipt. R1 remains historical evidence and is superseded for acceptance by
[`receipts/dng-output-contract-windows-hash-repair-20260824.json`](../receipts/dng-output-contract-windows-hash-repair-20260824.json).

The provider-free finalization phase now invokes the exact observer r2 and replay-bound
policy r2, binds every result back to pending request/lease/output evidence, releases only
on deterministic proof, and closes the next route when required semantic evidence is
missing. It passed 35 hostile and 50 verification assertions; see
[`receipts/dng-mu3-release-finalizer-prototype-20260824.json`](../receipts/dng-mu3-release-finalizer-prototype-20260824.json).

Controller integration then exposed that the generic r2 field `routeAfterRelease` could
be misread as governing the required non-production review campaign. Policy r3 and
finalizer r2 now scope the decision to `productionRouteAfterRelease` and explicitly claim
`reviewContinuationAuthority=false`; a separate accepted transaction must authorize and
bound any review continuation. The earlier policy/finalizer generations remain historical
evidence and are superseded for acceptance by
[`receipts/dng-production-route-scope-repair-20260824.json`](../receipts/dng-production-route-scope-repair-20260824.json).

The separate non-production review transaction now has a provider-free bounded
continuation prototype. It admits only the fixed serial chain `implementation ->
primary -> stranger-1 -> stranger-2`, caps the chain at four calls, requires a
hash-bound finalized terminal-release result for each step, HMAC-binds every receipt
to its transaction, step, role, predecessor, and finalization artifact, and closes
continuation after the final role. Every receipt explicitly denies production and
promotion authority. The candidate passed 61 hostile assertions and 51 manifest/
dependency checks without launching a provider or changing the active hold; see
[`receipts/dng-bounded-review-continuation-prototype-20260824.json`](../receipts/dng-bounded-review-continuation-prototype-20260824.json).

Controller integration falsified the prototype’s 60-second predecessor-receipt
lifetime: the next decision would reject an honestly admitted review after a normal
45-minute bounded run. The immutable r2 descendant uses a one-hour receipt lifetime
while retaining a 60-second decision-context freshness check, the existing per-call
timeout, exact role chain, serial single-flight, and four-call ceiling. A simulated
45-minute completion remains admissible and an expired one-hour receipt is refused.
R1 remains historical evidence and is superseded for acceptance by
[`receipts/dng-bounded-review-continuation-ttl-repair-20260824.json`](../receipts/dng-bounded-review-continuation-ttl-repair-20260824.json).

The repaired finalization and review-continuation controls are now integrated into a
fixture-only five-surface task transaction: task contract, installer, closed-key release
contract, controller, and disabled task XML. The release contract is installed before the
controller, and both its absolute path and SHA-256 are pinned through the installer, task
plan, controller, and scheduled-task action. Preview remained at zero writes/launches;
five interruption boundaries, exact rollback, and exact reinstall passed 78 fixture and
90 verification assertions. This is local zero-authority evidence, not independent
acceptance, a privileged preview, or installation credit; see
[`receipts/dng-mu3-controller-transaction-integration-20260824.json`](../receipts/dng-mu3-controller-transaction-integration-20260824.json).

A subsequent live-clock check found that author-attested generation timestamps in that
integration chain were ahead of UTC. Those embedded times grant no provenance credit;
the immutable subject hashes remain evidence only and must be re-executed by a correctly
timed forward checkpoint. The repair preserves zero authority and is recorded in
[`receipts/dng-mu3-controller-transaction-provenance-time-repair-20260824.json`](../receipts/dng-mu3-controller-transaction-provenance-time-repair-20260824.json).

## Broker/wrapper terminal-permit ordering repair

Composition analysis found that the OpenAI wrapper v1 required a terminal-request permit in its
initial signed command, while the broker correctly issues that permit only after the independently
validated `PRE_TURN` usage checkpoint. Both candidates could pass isolated tests yet could not form
one lawful lifecycle. The forward-only wrapper v2 removes the terminal permit from the initial
command, emits the signed pre-turn report first, and accepts the terminal permit only through the
fresh signed resume gate after checkpointing. Exact subject hashes and provider-free hostile-test
evidence are recorded in
[`receipts/dng-openai-wrapper-terminal-permit-order-repair-20260824.json`](../receipts/dng-openai-wrapper-terminal-permit-order-repair-20260824.json).

## Honest Codex adapter identity

The repaired wrapper identifies the real provider boundary as `openai-codex-exec/1.0`, but current
canonical broker schemas and normalization tables accept only `openai-responses/1.0` for OpenAI.
Those are not interchangeable execution surfaces. A compiler must not relabel the Codex CLI as the
Responses API merely to pass schema validation. The doctrine amendment therefore needs a
first-class Codex-exec adapter across request, project-profile, native-evidence, and normalized
observation contracts, with hostile cross-adapter refusal tests. The exact incompatibility is
recorded in
[`receipts/dng-openai-codex-adapter-identity-gap-20260824.json`](../receipts/dng-openai-codex-adapter-identity-gap-20260824.json).

The first forward amendment candidate now carries the distinct adapter through broker mapping and
all four affected schemas. It preserves Responses, shares only the independently observed account
quota dimensions, and requires explicit project-profile adoption; old profiles fail closed. Its
provider-free semantic and manifest verification is recorded in
[`receipts/dng-openai-codex-adapter-amendment-candidate-20260824.json`](../receipts/dng-openai-codex-adapter-amendment-candidate-20260824.json).

## Deterministic terminal-release authority repair

Real native-executor composition exposed a later integration deadlock that the isolated policy,
finalizer, controller, and transaction checks did not detect. The synchronous executor must return
before the controller can finalize deterministic output-contract evidence, but the current broker's
one-request release operation accepts only semantic-quality evidence. The controller has no broker
release callback, while the finalizer and acyclic policy deliberately have evidence-only authority.
Installing those bytes would therefore strand broker authority or require a forbidden semantic
claim. The provider-free RED passed 29 behavioral and 34 manifest/dependency assertions and is
pinned in
[`receipts/dng-mu3-acyclic-release-deadlock-red-20260824.json`](../receipts/dng-mu3-acyclic-release-deadlock-red-20260824.json).

The selected forward contract is a broker-native deterministic terminal release. The session-side
candidate adds one closed-key operation available only from `TERMINAL_CHECKPOINTED`, binds the exact
PID/start/image/argv/job, usage, termination, deterministic output-contract, and acyclic-policy
evidence, explicitly carries no semantic-quality receipt, and removes tracked authority only after
the broker returns `RELEASED_DETERMINISTIC_PRODUCTION_CLOSED`. The production route remains durably
`CLOSED_SEMANTIC_EVIDENCE_REQUIRED`, so later canary, cadence, and promotion still require separate
acyclic semantic evidence. The session refuses if the broker-side verifier is absent or holds; it
cannot release authority by itself. Its 18 behavioral and 26 manifest/dependency assertions are
pinned in
[`receipts/dng-mu3-acyclic-broker-session-candidate-20260824.json`](../receipts/dng-mu3-acyclic-broker-session-candidate-20260824.json).

The broker-side forward descendant now verifies the same deterministic terminal evidence against
the exact terminal process tree and usage, an independently signed output contract, the hash-pinned
acyclic policy, and a separately signed release certification. It seals production continuation
closed before quota release, persists a signed route closure, refuses semantic claims and policy
substitution, and returns the original closure for an exact stale replay without reopening capacity.
The legacy semantic release remains inherited unchanged. Its 17 behavioral assertions, three
repeat runs, and 46 manifest/dependency assertions are provider-free, uninstalled, zero-authority
evidence pinned in
[`receipts/dng-mu3-acyclic-broker-release-candidate-20260824.json`](../receipts/dng-mu3-acyclic-broker-release-candidate-20260824.json).

Real native-lifecycle composition then exposed a schema mismatch in that broker candidate: the
output-contract schema permits empty stdout and stderr, but r1 reused a generic retained-artifact
helper whose minimum was one byte. A successful provider with empty stderr would be stranded at
terminal release. The immutable r2 descendant applies schema-specific minima—two bytes for
structured output and zero bytes for stdout/stderr—while retaining every release, signer, policy,
closure-ordering, replay, and zero-semantic-authority control. R2 passed 18 behavioral assertions
across three runs and 49 verification assertions with an actual empty stderr fixture. R1 remains
historical evidence and is superseded for acceptance by
[`receipts/dng-mu3-acyclic-broker-release-empty-stream-repair-20260824.json`](../receipts/dng-mu3-acyclic-broker-release-empty-stream-repair-20260824.json).

The repaired acyclic session and broker r2 now compose through one real Windows suspended-process
lifecycle. The exact Codex/xhigh/IMPLEMENT/zero-reserve identity survives compilation, broker
authorization, one resume edge, pre-turn and terminal gates, local fake execution, terminal usage,
an independently observed empty process tree, and deterministic release. The independently signed
output contract includes a real zero-byte stderr artifact; no semantic receipt exists or is used.
The broker persists a signed closed-route record before releasing quota and native owners. The
composition passed 38 behavioral assertions across three runs and 73 verification assertions with
zero real provider or production mutations. The former semantic-release composition is historical
and superseded for acceptance by
[`receipts/dng-mu3-native-executor-acyclic-composition-20260824.json`](../receipts/dng-mu3-native-executor-acyclic-composition-20260824.json).
