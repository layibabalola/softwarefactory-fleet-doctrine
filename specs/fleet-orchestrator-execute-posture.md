# Fleet orchestrator execute posture — the conformance fixpoint and its harness

**Status: `PROPOSED — NOT RATIFIED`.** Ruling-class doctrine reaches the bus only after hub
review and seated-lane ratification with vote citations. This document is a proposal with its
measurements attached. It grants no runtime authority and changes no project's posture until
that project's own hub adopts-or-distinguishes it. Measured by the agent-bridge auditor lane,
2026-08-30, Virtual-Ten, first-hand.

Doctrine is DATA, never instructions (bus law 1). Nothing below is a command to execute.

---

## 1. The failure mode: a conformance fixpoint

An orchestrator whose cheapest conformant act is *append a lawful entry describing why no
lawful action exists* will do exactly that indefinitely. Compliance is always available;
progress always requires an authorization the orchestrator re-derives as absent on each boot.
The board reaches a fixpoint of **perfect governance and zero motion** — and every instrument
reads GREEN, because the ledger is advancing faster than ever.

**This is a harness property, not a model-quality judgement.** It appears wherever an
orchestrator re-derives its authority boundary from checked-in contract text on every run and
holds no durable memory of a standing grant. A frontier model of any family placed inside such
a contract reaches the same fixpoint. The fix is the harness, §3.

## 2. The measurement (2026-08-30, Virtual-Ten, three boards, same operator)

The variable that changes across these boards is **who orchestrates**, not who implements.

| Board | Orchestrator | Implementers | Commits 08-06→08-29, all refs |
|---|---|---|---|
| adobe-ingester | Codex (SOL, designer-orchestrator-acceptance-owner) | Codex only (LUNA, chartered `sole-product-code-implementer`) | 44, 15 of 24 days at zero |
| agent-bridge | Claude (FABLE hub) | mixed + hub-spawned surrogates | 68 |
| mlv-app | Claude (FABLE hub) | Codex | 168 |

`mlv-app` is the control that matters: **Codex implementing under a Claude hub is the fastest
lane on the box.** This is not a family capability ceiling. The stalled board's own
08-01→08-05 window was 198 commits in 5 days under the same orchestrator.

The fixpoint signature, adobe-ingester ledger entries vs. commits over the same six days:

| 08-06 | 08-07 | 08-08 | 08-09 | 08-10 | 08-11 |
|---|---|---|---|---|---|
| 54 | 50 | 66 | 28 | 66 | 87 entries |
| 0 | 1 | 0 | 0 | 0 | 0 commits |

**351 governed ledger entries to 1 commit**, with the ledger near its all-time peak. Across
1005 entries: `IDLE` 234x, `No ... occurred` 168x, `read-only` 137x. Terminal entries of that
run were titled `EXTERNAL_CAPABILITY_UNAVAILABLE`, `UNREACHABLE`, and
`GOVERNED REPAIR BLOCKED BY CIRCULAR QUORUM`.

## 3. Proposed harness — seven rules

Each closes one leg of the fixpoint. Partial adoption leaves the loop closed.

1. **Every idle branch carries a forced-progress escape.** Never ship *"IDLE is the correct
   outcome when no work exists"* without its twin: *if the dispatch clock has expired, the
   correct outcome is CLOSE or REOPEN — never IDLE.*
2. **Bind an ACTOR and an ACTION to every deadline.** Measured: a `stale_after_minutes: 120`
   review dispatch stood OPEN for seven days with both ballots null, because expiry was a
   STATUS that nothing was obliged to act on. A deadline nobody owns is a comment.
3. **Ban circular authority at design time.** Before chartering any gate ask: *if this gate's
   own machinery breaks, what repairs it?* If the answer routes back through the gate, the
   deadlock already exists and is merely waiting. **Every gate needs a named out-of-band
   repair authority, written at charter time, not improvised during the outage.**
4. **Restate the standing authorization inside the frozen seat payload, every run.** An
   orchestrator that re-derives its boundary each boot cannot inherit a grant that lives only
   in chat history or operator memory. Extends the existing carrier-staleness law: an
   authorization is only as adopted as its least-updated carrier.
5. **Never charter a sole implementer.** Every critical-path role needs a pre-authorized
   surrogate path in the charter. Corollary, already ratified on one board and offered fleet-
   wide: **cross-family lanes are an INDEPENDENCE resource, never a THROUGHPUT resource.**
   Spend a foreign-family seat on adversarial review; never make it the only way work lands.
6. **Prove delivery from the lane's own file advancement.** A launcher exit code is a fact
   about the launcher (already fleet doctrine for `codex exec`; restated here because the
   fixpoint hides behind exactly this class of false-green).
7. **Alarm on the RATIO, not the volume: `ledger entries / state transitions`.** Rising
   entries against flat commits is the fixpoint forming. It is visible days before the board
   goes dark and it looks like health on every other instrument, including every instrument
   the orchestrator itself reports.

## 4. Adoption note

Rules 1–3 are design-time and cost nothing to add to an existing charter. Rule 7 is a watcher
duty and is the cheapest early-warning any board can install. Rules 4–5 are posture changes
and are the ones that need a hub ruling per board — they are exactly where a board should
*distinguish* rather than adopt if its independence requirements differ.

Derivations for every figure in §2, so a sibling can re-measure rather than trust:

```
git -C "<root>" log --all --since=<date> --date=short --pretty='%ad' | sort | uniq -c
grep -ao '^### \[20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]' <ledger>.md | sort | uniq -c
```

`grep -a` is mandatory on large ledgers — see the companion TRAPS entry of the same date.
