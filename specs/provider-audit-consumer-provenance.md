# Provider audit-consumer provenance R46

## Status and scope

R46 is a deployment-inert doctrine successor to ratified R45
`0da4a20f9e62a47414f42a8780c695865f1633a0`. R45's authenticated frozen-graph execution remains
unchanged and is the parent trust layer. R46 standardizes how an independent provider audit
consumer proves what ran, what provider actually answered, and why its opinion may be considered by
a later adjudicator.

R46 installs no provider wrapper, process, task, credential, execution gate, adoption, score, or
project authority. Its reference validator never starts a shell, provider, tool, opinion, or
workload. Even a fully conforming `EXECUTION_READY` audit produces only
`ACCEPTED_NO_EXECUTION_AUTHORITY`, which may be consumed by a separate adjudication.

## Laws

### 1. Requested identity is not provider identity

A claim records the requested provider, model, transport, and account scope. Those values prove only
what a wrapper asked for. The terminal must independently carry the same tuple with
`authenticated=true`, `source=provider_terminal`, and a nonempty provider session. Wrapper prose,
command-line arguments, environment, model-authored framing, or a requested-model field cannot
substitute for terminal-authenticated provider telemetry.

An implementation whose transport cannot authenticate terminal identity must publish `HOLD`; it
cannot infer identity from a successful exit or substantive answer.

### 2. Final-opinion custody is exact-byte CreateNew custody

Before any provider claim, the claim binds one opinion path and proves it absent. Publication uses
an exclusive CreateNew operation, succeeds exactly once, and records the exact content bytes,
byte-count, and SHA-256. Postflight physically reopens the path and must reproduce the same count and
digest. Every exact-byte envelope uses the single standard Base64 spelling whose re-encoding exactly
reproduces `contentBase64`; alternate nonzero pad-bit spellings refuse. Append, overwrite,
rename-as-retry, pre-existing content, two writes, a digest without the bytes, or text reconstructed
from a transcript refuses.

The retained bytes are a canonical, versioned final-opinion descriptor binding the verdict,
consumer session, and authenticated provider session. The validator derives the substantive verdict
from those bytes; a mutable sibling verdict or terminal outcome must match and cannot upgrade them.
The complete preclaim custody object is validated for every terminal branch, including resource-limit
`NO_VERDICT`, even though that branch correctly contains no opinion.

The final opinion remains substantive evidence. It is never execution authority by itself.

### 3. The wrapper proves itself under the actual shell before claim

Wrapper syntax and postflight mechanics are not accepted from source inspection alone. Before the
provider claim exists, the wrapper records the actual shell path, exact shell digest, and actual
version, plus its own path, bytes, and digest. Under that exact shell it must complete, in order:

1. wrapper syntax;
2. an isolated CreateNew collision probe;
3. JSONL terminal parsing;
4. a deliberately failed governed-postflight probe that proves substantive READY text cannot pass.

The self-test is disposable mechanics evidence only. It cannot contact a provider or create the
real claim/opinion namespace. A self-test performed by a different shell version is not evidence for
the production wrapper.

### 4. Read commands are explicitly named and every command succeeds

The contract and claim carry the same nonempty, ordered, duplicate-free read-command allowlist. Each
postflight command is identified by an exact allowlisted command identity, is classified read-only,
completes, and exits zero. Unknown, failed, incomplete, denied, or implicitly permitted commands
refuse. A sandbox denial is a failed command, not proof that the audit was read-only.

This contract intentionally avoids parsing free-form shell text to discover whether it was safe.
Production wrappers should bind canonical argv or an equivalent authenticated command descriptor to
each allowlist identity.

### 5. Provider diagnostics are immutable and non-suppressing

Provider diagnostics retain their original bytes, byte-count, SHA-256, immutable marker, and a
canonical versioned JSON descriptor. The authenticated bytes bind the diagnostic kind, code, and
terminal provider session; sibling metadata is accepted only when it exactly matches that descriptor.
Classification is derived from those authenticated bytes:

- `rate_limit` and `quota` become `RESOURCE_LIMIT_NO_VERDICT`;
- `provider_status` becomes `PROVIDER_STATUS_NON_AUTHORITATIVE`.

Unknown, noncanonical, session-detached, or reclassified diagnostics refuse. Provider diagnostics
never suppress wrapper runtime errors, tool errors, nonzero commands, malformed output, identity
gaps, or failed postflight. A transport can be rate-limited and the wrapper can also be broken; the
runtime/tool failure remains a governed failure.

Any authenticated `RESOURCE_LIMIT_NO_VERDICT` diagnostic precludes a substantive `EXECUTION_READY`
or `HOLD` terminal and its opinion. Such a diagnostic belongs only to the spent `NO_VERDICT` branch;
mutable outcome or opinion metadata cannot convert it into substantive evidence. A substantive
terminal may retain only `PROVIDER_STATUS_NON_AUTHORITATIVE` diagnostics.

### 6. Quota and rate limit are spent no-verdict lineage

A quota/rate-limit terminal is `NO_VERDICT` only when its provider identity is terminal-authenticated
and matches the requested tuple, inference did not occur, no opinion exists, the consumer session is
permanently spent, and retry is false. The versioned complete canonical contract-plus-evidence
package receives a lineage SHA-256. The portable schema admits only `rate_limit` or `quota`
diagnostics classified `RESOURCE_LIMIT_NO_VERDICT` on this branch; provider-status-only or mixed
diagnostics refuse before lineage. The lineage grants no execution or opinion authority.

Resume, retry, renamed retry, or reuse of the consumer session is prohibited. A later consumer is a
provider substitution even when it selects the same vendor after reset.

### 7. Provider substitution is a separate explicit authority

Substitution requires a canonical, versioned, exact-byte authority artifact. Every governing field
is parsed from those authenticated bytes rather than trusted from mutable sibling metadata. It binds:

- the spent session and exact no-verdict lineage digest;
- `EXPLICIT_PROVIDER_SUBSTITUTION_ONLY`;
- a fresh consumer session;
- the exact newly selected provider/model/transport/account tuple.

The new claim's exact fresh session and identity must match the artifact. Reusing the artifact for a
different session, an automatic fallback, model downgrade, stale checkpoint, unbound provider
choice, or spent session refuses. Substitution authorizes only a fresh
audit consumer; it does not authorize the governed workload.

Before reading any nested field, the substitution evaluator validates that the complete prior
package is an object with exactly `contract` and `evidence`. Null, array, string, or extra-field roots
produce deterministic `HOLD`, never an uncaught host-language exception.

### 8. Governed postflight dominates substantive text

The reference validator enforces the portable evidence shape at runtime, including exact object
fields, exact lowercase SHA-256 grammar, and nonempty custody paths. Postflight must prove all of the
following before final opinion content is admitted:

- all frozen inputs physically rejoined;
- claim physically rejoined;
- terminal identity authenticated;
- exact-byte CreateNew opinion rejoined;
- zero unauthorized writes;
- zero failed or denied commands;
- zero runtime and tool errors.

If any postflight fact fails, the result is `HOLD` even when transcript, last message, opinion bytes,
or model framing says `EXECUTION_READY`. No launcher, controller, permit issuer, or downstream gate may
consume substantive text from a failed governed postflight.

### 9. Classification and authority are separate

The reference module can classify:

- `ACCEPTED_NO_EXECUTION_AUTHORITY`;
- `HOLD`;
- `NO_VERDICT_RESOURCE_LIMIT`;
- `SUBSTITUTION_AUDIT_ELIGIBLE`.

Every decision has `execution_authorized=false`. Acceptance means only that a separate adjudicator
may consider the exact audit opinion. Substitution eligibility means only that a fresh audit may be
claimed. Neither is a workload permit.

### 10. R45 and adverse history remain immutable

R46 does not modify R45's checker, tests, manifest, frozen graph, source anchors, historical
execution, or closed accounting. R45 remains the provenance foundation; R46 adds a bounded audit
consumer contract in new files plus successor documentation. Landing, adoption, activation, score,
and execution remain separate owner-governed acts.

## Reference artifacts

- `schemas/provider-audit-consumer-provenance-v1.schema.json` defines the portable evidence shape.
- `tools/provider_audit_consumer_provenance.py` implements deterministic, deployment-inert
  classification.
- `tests/test_provider_audit_consumer_provenance.py` contains bounded hostile cases for every law.
- `tools/check_provider_audit_consumer_manifest.py` verifies the successor manifest and exact subject
  bytes without invoking the provider consumer.
- `manifests/provider-audit-consumer-provenance-r46.json` binds R45, this doctrine, and its bounded
  evidence with zero authority.
