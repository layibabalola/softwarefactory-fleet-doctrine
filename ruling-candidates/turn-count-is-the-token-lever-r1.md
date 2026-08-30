# Ruling candidate: turn count is the token lever R1

Status: **PROPOSED ONLY — NOT YET A RATIFIED RULING OR PROJECT RUNTIME AUTHORITY**

Origin: DNG Auto Processor, 2026-08-30, after a measured provider exhaustion took an unattended
hourly loop offline for six consecutive wakes. Owner direction was explicit: find token savings that
introduce **no regression and no reduction in code quality**. Supporting measurements are in
`dng-auto-processor/receipts/OPUS-TOKEN-ECONOMY-TURN-COUNT-MEASUREMENT-20260830.md`.

## The mechanism this candidate rests on

In an agentic loop, every turn re-sends the accumulated context. Tool output read on turn 3 is
re-charged on turns 4..N. Therefore the cost of an unattended run is approximately

`cost ≈ Σ(turns) context(turn)`

and because `context(turn)` grows monotonically within a run, cost is **superlinear in turn count**.
Output tokens are a small minority of the bill. A loop is not expensive because it reasons; it is
expensive because it reasons in many small steps, each one paying again for everything before it.

## Proposed portable law

**Treat TURN COUNT as the primary cost metric of an unattended agentic run, and reduce it by batching
independent work into single turns.** Specifically, an adopting project should:

- **Batch independent tool calls.** Calls with no data dependency on one another belong in one turn.
  This is the same reasoning over the same evidence with fewer round trips — it removes no capability
  and truncates no work.
- **Not re-read what is already in context.** A second read of an unchanged file buys nothing and is
  then re-charged on every subsequent turn.
- **Record turns per run** in the run's own receipt, beside cost and cache-read tokens, so the metric
  is derivable rather than estimated.
- **Bound the fixed prefix** — standing instructions, memory files, tool schemas — because it is paid
  on every turn. This is second-order to batching but compounds with it.

## What an adopter must NOT do under this candidate

These reduce cost by reducing quality or completeness and are explicitly **out of scope**:

- Lowering reasoning effort as the primary lever.
- Lowering a max-turn ceiling to force cheaper runs. That truncates work mid-transaction; it makes a
  run cheaper by making it incomplete, sometimes leaving a partial mutation behind.
- Dropping review stages, negative controls, or closed-set obligations.

A token saving that changes what the system concludes is not a saving; it is a silent scope cut.

## Second, independent lever: put review on a different provider

Where a chain has a producer and a reviewer, running the reviewer on a **different provider** removes
review load from the producer's quota entirely and decouples the two failure domains. Measured at
origin: the producing loop exhausted its weekly pool and every gate went down with it, because both
were the same vendor. A cross-vendor gate also strengthens independence rather than weakening it.

This is offered as a separate proposal, not a dependency of the law above.

## Verification an adopter owes before adopting

The mechanism is general; **the magnitudes are not.** Before adopting, derive on your own fleet:

1. The cache-read-to-output ratio of your unattended runs. If output dominates, this candidate does
   not apply to you.
2. Cost against turn count across at least ten real runs. Confirm the relationship is superlinear
   rather than flat before spending effort on batching.
3. A before/after on a workload whose **output is byte-comparable**, to demonstrate that batching
   changed cost without changing conclusions. A saving that cannot show identical conclusions is not
   evidence for this law.

## Honest limits

One project, one model family, one workload shape, twelve runs. No controlled experiment was run: the
superlinear relationship is observational across wakes of differing scope, so scope and turn count are
confounded and the effect size is not isolated. The direction is well supported by the mechanism; the
coefficient is not portable and is not claimed to be.
