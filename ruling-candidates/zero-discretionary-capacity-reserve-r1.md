# Ruling candidate: zero discretionary capacity reserve R1

Status: **PROPOSED ONLY — NOT YET A RATIFIED RULING OR PROJECT RUNTIME AUTHORITY**

Owner direction: 2026-08-23. The owner intends Claude quota to drain through useful, bounded work so
account rotation can occur naturally. A fixed 20% or 30% unused-capacity floor is therefore no longer
the desired fleet utilization policy.

## Proposed portable law

Set the unattended **discretionary capacity reserve to 0%**. Admit a conservatively estimated slice
only when, in every required quota window:

`fresh proven utilization + active reservations + estimated slice <= 100%`

Zero discretionary reserve does not mean unbounded or fail-open execution. Every adopter must retain:

- fresh account-bound capacity observations and refusal of stale, malformed, unknown, or cross-account
  telemetry;
- one quota-domain owner, strict single-flight, bounded turns and wall clock, and no overlap;
- conservative pre-request reservation and post-request reconciliation, including full charging of
  failure, refusal, timeout, retry, and unknown usage;
- exact provider, model, effort, role, review, subject, executable, argv, output, and functionality
  bindings;
- a hard 100% ceiling using the estimated slice before launch; and
- exact terminal receipts, lease release, rollback, and project-local adoption evidence.

The 0% value applies only to the discretionary unused **capacity-window floor**. It does not remove
request accounting reservations, terminal-output token reserves, active work reservations, provider
limits, or independent-review requirements.

## Measured migration surface

The canonical doctrine checkout contains three different numeric positions that must not be silently
treated as one current rule:

1. the ratified governor example carries `interactive_reserve_pct: 30`;
2. the R22 zero-authority token-control candidate carries `completionReserve.quotaWindowFloor: 0.2`;
3. DNG's previously committed local admission policy carried `completion_reserve_pct: 30`.

No other mounted project runtime policy with an exact 30% value was found in the 2026-08-23 bounded
`C:\code` census. Several project specs require an unspecified completion/foreground reserve, but
those prose obligations do not prove the value installed at runtime. Unmounted projects remain
`UNEVALUATED`, never assumed compliant or noncompliant.

## Required project response

Each project owner publishes one current, standalone line in its sole-writer `specs/<project>.md`:

- `ADOPT(ZERO_DISCRETIONARY_CAPACITY_RESERVE_R1, <policy SHA-256>, <review receipt SHA-256>)`; or
- `DISTINGUISH(ZERO_DISCRETIONARY_CAPACITY_RESERVE_R1, <local difference>, <proof>)`; or
- `REJECT(ZERO_DISCRETIONARY_CAPACITY_RESERVE_R1, <specific contradiction>, <proof>)`.

An `ADOPT` must pin the exact local policy and admission/gate bytes, prove the exact-100% boundary is
admitted and an estimated value above 100% is refused, preserve stale/cross-account/overlap negatives,
and include transactional preview/apply/rollback/reinstall plus natural production evidence. Merely
changing a number, this proposal's publication, or an owner statement earns no runtime or adoption
credit.

## Acceptance gate

Before this becomes portable doctrine, a distinct adjudicator must bind the exact candidate commit,
tree, and manifest; reproduce positive and hostile controls; confirm that request-level reservations
and terminal reserve semantics remain intact; obtain independent review; append an exact ruling to
`RULINGS.md`; and merge the reviewed bytes to canonical `master`.

Until then, project-local user authority may change a local reserve policy, but every fleet row remains
honestly pending this amendment's independent doctrine acceptance and project-specific disposition.

## First combined executable candidate

DNG's first provider-free descendant composes the 0% floor with the distinct
`openai-codex-exec/1.0` adapter. A real broker authorization fixture admits fresh proven utilization
plus the conservative request estimate at exactly 100%, and refuses a projection one millionth over
100% as `HARD_CAP_FORECAST`. Old profiles remain fail-closed until explicit adoption. The candidate
and its zero-authority limits are pinned in
[`receipts/dng-openai-codex-zero-reserve-amendment-candidate-20260824.json`](../receipts/dng-openai-codex-zero-reserve-amendment-candidate-20260824.json).

A forward descendant also repairs the broker's prior `high`-only effort schemas. Its full signed
persistent-broker fixture authorizes and attests the exact `gpt-5.6-sol` / `xhigh` / `IMPLEMENT`
Codex route without weakening the 100% ceiling. Evidence and zero-authority limits are pinned in
[`receipts/dng-openai-codex-xhigh-full-broker-authorization-20260824.json`](../receipts/dng-openai-codex-xhigh-full-broker-authorization-20260824.json).

The next forward descendant compiles one exact hash-bound MU-3 request and proves that the full
persistent broker reaches `PREPARED_SUSPENDED` with the Codex/xhigh/IMPLEMENT/zero-reserve route.
It has no work-creation, admission, lease, permit, process, or provider authority. A correctly
signed but stale prior-idle receipt is deliberately left for the broker to reject before launch;
hostile controls also refuse model, effort, role, signer, profile, subject, boundary, and output
identity drift. Evidence and zero-authority limits are pinned in
[`receipts/dng-mu3-broker-request-compiler-candidate-20260824.json`](../receipts/dng-mu3-broker-request-compiler-candidate-20260824.json).

The compiler is now joined provider-free to the real persistent-broker protocol, pre-turn wrapper
gate, usage parser, terminal permit, termination observer, independent quality observer, terminal
checkpoint, exact release, and clean shutdown. The fixture launches only a local fake provider and
makes no network or production mutation. Its native process observation remains synthetic, so this
does not yet prove the Windows suspended-process executor, real PID/start-time/job binding, or any
installation/adoption authority. Evidence and the explicit remaining gap are pinned in
[`receipts/dng-mu3-broker-wrapper-protocol-composition-candidate-20260824.json`](../receipts/dng-mu3-broker-wrapper-protocol-composition-candidate-20260824.json).
