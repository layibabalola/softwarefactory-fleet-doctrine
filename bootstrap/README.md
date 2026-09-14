# Bootstrap — joining the fleet review from any project, on any machine

**Two pastes.** Everything else is reached by pointer.

| | You paste | Who runs it | What it does |
|---|---|---|---|
| **PROMPT A** | ✅ | your session, any model | Syncs the bus, derives the machine inventory, records this project's adoptions, and harvests what the fleet has learned since you last synced. No review. |
| **PROMPT B** | ✅ | your session, any model | Decides the request is above its tier and spawns **one** chip naming the model it recommends. No review. |
| `lane-orchestrator.md` | — | that chip | Dispatches cross-family lanes over the provider CLIs, arbitrates, files `adjudications/<subject>/<project>.md`. |
| **PROMPT K** | ✅ | every project, after A | Runs this project's real work through `specs/fleet-factory-kernel.md` and files FIT/FRICTION/BREAK evidence to `adjudications/factory-kernel/`. |
| **PROMPT 3** | — | the project that **owns** the subject spec | Harvests every filing, adjudicates across projects, rewrites the spec, publishes dispositions back. |

A and B are separate pastes on purpose: a failed sync should never be mistakable for a failed
review, and A is cheap enough to re-run whenever you have been away.

## The pastes

**A**, in the project you want to join:

> Read and follow `<doctrine>/bootstrap/PROMPT-A-sync-and-adopt.md`. If that Read fails, do not
> search for the file or try another path: run `git -C "<doctrine>" ls-files bootstrap/`, report
> `UNREADABLE` with both errors verbatim, and stop.

**B**, once A reports ready:

> Read and follow `<doctrine>/bootstrap/PROMPT-B-begin-review.md`. The subject is
> `specs/conjugal-approach-a-v7.4.md`; THIS project is the test bench. If that Read fails, do not
> search: run `git -C "<doctrine>" ls-files bootstrap/`, report `UNREADABLE` verbatim, and stop.

### When a paste reports `UNREADABLE`

The guard exists because the failure is outside the prompt. A session that cannot open the file
cannot read any guard written inside it. Measured 2026-09-14 (Dell XPS 17): a Haiku session
opened in `DngAutoProcessor - Claude` reported that PROMPT A "doesn't exist", then spent six shell
commands searching for it. The file was present at that exact path, and a Conjugal session read it
the same hour. The path was right; the session could not reach it.

The `ls-files` line tells the causes apart, so re-pasting is safe:

| `ls-files` result | Cause | Fix |
|---|---|---|
| lists the file | **Access.** The session is scoped to its own folder (Claude Desktop does this) | Grant the session the doctrine folder, or open the session in a project that has it, then paste again |
| `cannot change to` / `not a git repository` | **No checkout** at `<doctrine>` on this machine | Clone the bus there (PROMPT A §1 `UNREACHABLE`), then paste again |
| lists `bootstrap/` without the file | **Renamed** | Use the name this README gives now |

**Paste into the project you mean to join, never into a frozen archive.** An archive may not mark
itself as frozen. `DngAutoProcessor - Claude` is read-only by owner rule, and that rule lives only
in the Conjugal instructions. PROMPT A writes `.claude/doctrine-sync.json` and adoption records, so
a successful run there would have broken the rule.

Expect B to refuse to review, ask once with a model pre-selected, and hand back a chip. Set the
model picker to what it names **before** clicking — a chip inherits the picker at click time —
and the chip re-checks its own model and stops if it is below what was asked for.

## The bus is lateral, not just vertical

The obvious flow is upward: projects file, the spec owner harvests, the spec improves. That is
PROMPT 3, and it is only half the value.

**The other half is sideways, and it is free.** A finding grounded in another project's test
bench usually names a defect your repo has too — you simply have not hit it yet. Reading a
sibling's filing is the cheapest defect-finding available anywhere on this bus, because someone
else already paid for it. PROMPT A §4 makes that a step rather than a virtue: on every sync,
read `RECEIPTS.md` / `TRAPS.md` since your last sync, and read siblings' filings in
`adjudications/`, not only your own.

So: **a finding that generalises beyond its subject belongs in `RECEIPTS.md` or `TRAPS.md` as
well as in the filing.** A filing is indexed by subject and read by that subject's owner; a
receipt is read by everyone. Putting a portable lesson only in a filing hides it from every
project that is not reviewing that spec.

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
`project`, `providers`, `seats`, `rubric_id`, and a `posture:` line copied from
`tools/review-posture/review_posture.py posture` (RULINGS R9). Then findings, one per line:

```
§<section> | "<quote, <=25 words>" | <defect, <=40 words> | REPLACES: "<anchor>" -> "<new>" | PROOF: <what would falsify it>
```

**The test-bench rule is the admission criterion:** every finding names how the defect manifests
in *your* repo — a path, a tool, a measured number — or it goes under `## Untested`. That is what
makes a disagreement between two filings a disagreement between two real environments rather
than two opinions.

## Measured, so you can argue with it

From the first run of this pipeline (`RECEIPTS.md`, 2026-09-13, Dell XPS 17): three Opus lanes
at medium effort on disjoint slices found 26 findings in **165 s** for $2.94; one Opus lane at
xhigh on the whole subject found 27 in **781 s** for $3.63. Near-parity on yield, 4.7× on wall
clock, cost per finding within 20% across every arm that worked.

Read that as: **the active ingredient is disjoint slicing, not model strength.** A swarm does not
buy cheaper findings — it buys latency and forced coverage, because slices examine dimensions a
single lane chooses away from. Budget by the coverage you need, not in the hope that swarming is
cheaper.

One arm produced nothing: Sonnet at max effort spent 47,449 thinking tokens and 19 minutes
planning the review, then asked permission to run it — returning `is_error: false`,
`stop_reason: end_turn`, `terminal_reason: completed`. **Effort is not monotonic in usefulness.**
Run autonomous lanes at medium; reserve the top of the range for a step where something can
receive a question. R2 is why that arm scored zero instead of counting as a lane.

Re-measuring any of this on your own hardware is not redundant — it is the independent evidence
`specs/cli-orchestration-standard.md` needs to stop being author-measured on one box.
