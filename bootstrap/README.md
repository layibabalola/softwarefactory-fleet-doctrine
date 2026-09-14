# Bootstrap — joining the fleet review from any project, on any machine

Four prompts. A project pastes **PROMPT 0** and nothing else; the rest are reached by pointer.

| | Who runs it | What it does |
|---|---|---|
| **PROMPT 0** | the session the operator is already in, any model | Decides whether the request is above its tier. If so, spawns exactly one chip naming the recommended model. Does no review itself. |
| **PROMPT 1** | that chip | Syncs this doctrine repo, then derives the machine's provider inventory by probing it. Leaves a receipt. |
| **PROMPT 2** | that chip | Dispatches cross-family review lanes over the provider CLIs, arbitrates, and files `adjudications/<subject>/<project>.md`. |
| **PROMPT 3** | the project that **owns** the subject spec | Harvests every project's filing, adjudicates across them, and rewrites the spec. |

## The paste

In the project you want to join the review, in whatever session you already have open:

> Read and follow `<doctrine>/bootstrap/PROMPT-0-dispatcher.md`. The subject is
> `specs/conjugal-approach-a-v7.4.md` in the fleet doctrine repo, and this project is the
> test bench.

Expect it to refuse to review, ask once with a model pre-selected, and hand back a chip. Set the
model picker to what it names **before** clicking, because a chip inherits the picker at click
time — and the chip re-checks its own model and stops if it is below what was asked for.

## The five rules that are not optional

Binding fleet-wide by owner ruling, 2026-09-13 (`RULINGS.md`; measurements in
`ruling-candidates/mandatory-review-floor-r1.md`). They constrain the honesty of a report, never
its content:

**R1** a session below the review floor escalates or fails closed — it never reviews at a lower
tier. **R2** completion is a sentinel the lane emits, never an exit code or a byte count.
**R3** a cross-family claim is computed from which families cleared the sentinel, never
asserted. **R4** every project-scoped reference names its project. **R5** provider inventory is
machine-scoped and probe-derived.

Each exists because it failed on this fleet within one week, silently, and reported green.

## What a filing must contain

`adjudications/<subject>/<project>.md`, one file per project, single writer. Header declares
`project`, `providers`, `seats`, `rubric_id`. Then findings, one per line:

```
§<section> | "<quote, <=25 words>" | <defect, <=40 words> | REPLACES: "<anchor>" -> "<new>" | PROOF: <what would falsify it>
```

**The test-bench rule is the admission criterion:** every finding names how the defect manifests
in *your* repo — a path, a tool, a measured number — or it goes under `## Untested`. That is what
makes a disagreement between two filings a disagreement between two real environments rather
than two opinions, and it is the only reason the harvest in PROMPT 3 is worth running.

## Measured, so you can argue with it

From the first run of this pipeline (`RECEIPTS.md`, 2026-09-13): three Opus lanes at medium
effort on disjoint slices found 26 findings in 165 s for $2.94; one Opus lane at xhigh on the
whole subject found 27 in 781 s for $3.63. Near-parity on yield, **4.7× on wall clock**. What a
swarm buys is latency and forced coverage, not cheaper findings — cost per finding was within
20% across every arm that worked.

One arm produced nothing at all: Sonnet at max effort spent 47,449 thinking tokens and 19
minutes planning the review, then asked permission to run it — returning `is_error: false`,
`stop_reason: end_turn`, `terminal_reason: completed`. Higher effort is not monotonic in
usefulness, and R2 is why that arm was scored zero instead of counted.
