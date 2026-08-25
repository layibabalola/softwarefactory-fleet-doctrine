# Ruling candidate: Cloudvore Fable-to-Opus capacity fallback R1

Status: **CLOUDVORE ADOPTED; FLEET CANDIDATE — NO CROSS-PROJECT RUNTIME AUTHORITY**

Strategy ID: `CLOUDVORE-FABLE-OPUS-CAPACITY-FALLBACK-1`

This candidate keeps useful independent inference moving when the Fable allowance is exhausted,
rate-limited, or awaiting a known reset. It is a routing rule, not permission to manufacture work,
weaken evidence gates, retry a spent namespace, or represent Opus as Fable.

## Decision

At every scheduler wake and strategic advancement audit, derive provider capacity from durable
terminals, exact reset timestamps, and live claims. Do not infer capacity from a quiet UI, elapsed
time, prose, process exit, or an expected billing window.

When Fable is unavailable and exact first-party Claude Opus 5 capacity is lawfully available, route
the highest-value useful, safe, non-overlapping task to Opus immediately. Prefer work that advances
the current critical path without competing for writer custody: design falsification, read-only
source audit, immutable evidence authentication, recovery analysis, or preparation of the next
lawful package. Never create low-value work solely to consume quota.

Every Opus-backed result carries both:

- `MODEL_CAVEAT`: the review used Claude Opus 5, not Fable.
- `FABLE_DIVERSITY_NOT_DISCHARGED`: Opus inference does not satisfy an independent Fable gate.

No score, source, execution, product, permit, release, or independent-review authority moves merely
because capacity was used or an audit returned READY. The exact downstream durable terminal remains
the authority.

## Admission and one-shot custody

Before invoking the provider:

1. Freeze a useful prompt, runner, immutable input manifest, current diagnostic, and canonical
   authority checkpoint as exact byte/SHA-256 tuples.
2. Bind a unique session and attempt, a fixed output namespace, `maxInvocations = 1`, and every
   unrelated authority false.
3. Require `FileMode.CreateNew` or an equivalent create-once primitive for claim, raw streams,
   postflight, opinion, and terminal. Any existing future is a collision, not a retry opportunity.
4. Rejoin every direct input and every recursively manifest-bound input immediately before and after
   invocation. Drift yields truthful HOLD and no credit.
5. Pass a no-provider self-test that rejects wrong model identity, non-first-party provenance,
   forbidden tools, permission denials, duplicate results or verdicts, and malformed terminals.
6. Obtain fresh independent driver review. A HOLD is repaired in a new unspent successor namespace;
   it is never overwritten or retried.

Provider invocation must request exact account-eligible `claude-opus-5`, not an alias. The terminal
must authenticate the init model and authoritative top-level `modelUsage` entry as canonical
`claude-opus-5` with provider `firstParty`. A narrowly enumerated first-party auxiliary model is
permitted only when the runner expects it; any other model, provider, tool, or permission event yields
HOLD. Restrict tools to the minimum read-only set for audit work.

Process activity and exit are only liveness observations. The immutable result terminal outranks PID
state, and PASS or READY must never be inferred from exit code alone. Provider failure, timeout,
parse failure, stderr, evidence drift, or missing provenance lands HOLD. Once invoked, the namespace
is spent even when the result is HOLD; never probe or retry it.

## Reset-aware scheduling

When a provider terminal exposes an exact reset timestamp, preserve that timestamp and exact
terminal tuple. Do not probe the spent provider namespace before reset. At the first scheduler wake
at or after the timestamp, physically rejoin the frozen successor and confirm all outputs remain
absent before its single authorized invocation.

If the provider does not expose an exact timestamp, record `RESET_UNKNOWN`; never invent one. Use the
other provider only for useful non-overlapping work and keep the unavailable provider's distinct
review obligation open.

## Automation rule

Evaluate fallback on every wake and record the decision at least every thirty minutes while a
critical path is open. If Opus remains idle despite Fable unavailability, record the exact reason:
no lawful useful task, provider unavailable, active one-shot, writer collision, missing immutable
package, or independent review pending. "Saving quota" is not a reason when useful safe work exists.

User updates report only a terminal transition or material liveness, blocker, authority, score, or
next-gate change. Passage of time alone is not progress.

## First proved Cloudvore exercise

The first full exercise used Opus only after an eight-case self-test and independent `DRIVER_READY`.
The exact first-party `claude-opus-5` call completed at the provider layer and returned a truthful
design HOLD: 89,692 output tokens, 4,536,795 cache-read input tokens, and USD 6.5039475 reported by
the provider. It resolved thirteen visible controller-contract findings and exposed three additional
gate-invisible truth defects. Fable diversity remained explicitly undischarged and formal score did
not move.

That outcome is the intended proof of the policy: fallback capacity bought useful falsification and
reduced successor risk without relaxing a gate or counterfeiting provider diversity.

## Fleet acceptance boundary

This submission does not assert that Fable and Opus have independent quota domains, that every
project can request the same exact model, or that any scheduler is already authorized. Each adopter
must publish `ADOPT`, `DISTINGUISH`, or `REJECT`, bind its actual account/quota-domain semantics, and
retain its project-specific writer, review, quality, reserve, rollback, and release gates.
