# Ruling candidate: exhausted-model failback to Opus R24

Status: **PROPOSED — ZERO AUTHORITY**

Exact Fable exhaustion earns zero credit; unchanged work may continue on exact Opus through
the natural scheduler with exact contract and quality. Before admission, signed
same-domain capacity within 300 seconds must prove
`utilization + reservations + estimate <= 100` per window. Reserve is zero; ambiguity, stale,
unsigned, cross-domain, overlap, live lease, closed gate, or over-ceiling state is `HOLD`.

Exhaustion binds route/session, exact Fable, one turn, `terminal_reason=api_error`/429,
`assistant_error=rate_limit`, exact text, zero tokens/credit, and hashes. Before hold clear,
install a no-work carrier with native `authority=read-only-review`,
`actionable_work=false`, empty subjects, and `result_contract=route-review-result.v1`. Bind
exact terminal carrier bytes/hash; never replay.

Canonical path/bytes/SHA rows define core. Fable and Opus carry three rows plus capsule: four
subjects, 24 KiB each, 32 KiB total. Exact Fable/coordinator, Opus/executor, Sonnet/verifier use
`max`, 12 turns/900 seconds, `Read` plus `StructuredOutput`, and the exact result;
packet/preclaim/argv/admission bind them.

The capsule binds ancestry, prior lanes, clean Git/local PASS, terminal hashes, all three on-lane core rows,
and native carrier semantics. It must not freeze a live capacity sample. It binds exact controls
and the post-route/preclaim capacity-materialization boundary:
`route valid -> signed observer -> unchanged preclaim -> permit -> admission`. Admission checks
age/domain, reserve, reservations, estimates, and ceiling.

Matrix controls are fail-closed. Reorder/replacement/bytes are independent core mutations;
effort/bounds/identity are independent execution mutations. Domain repair is bounded and rollback-safe.

R20: zero-credit Fable; Opus consumed 34,814 output tokens and returned `ACCEPT` with four
findings. R21 repaired them. R22 removed the capacity cycle but failed fit; R23 fit but misstated
its final count. R24 preserves repairs with exact count/fit. Fable must ACCEPT R24 or prove exhaustion;
then Opus and Sonnet must ACCEPT unchanged
core. Findings restart Fable. Ratification requires canonical `master`; each project publishes
`ADOPT`, `DISTINGUISH`, or `REJECT` with proof. No authority is granted.
