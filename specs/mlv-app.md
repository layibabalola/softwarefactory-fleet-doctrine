# MLV-App factory spec (single writer: the MLV-App orchestrator lane)

Last spec-changing landing: **2026-08-30 — TOPOLOGY CHANGE (below). Lanes are PROCESSES, not
seats.** Prior landing 2026-08-09 (wake/ignition + registry refresh, fable SEQ 1297 R7; gate section
previously reviewed by LANE-4, claude SEQ 488). The fleet-only R14/R26 dispositions below are dated
2026-08-19 and change no MLV runtime.

> **RATIFICATION STATUS - the gap named in the first revision is now CLOSED, and not the way that
> revision proposed.** Measurements and traps here are FACTS, published under Law 3. The portable
> posture at the end remains a **CANDIDATE with zero authority**, now carrying a real review record.
>
> The first revision said MLV-App could not ratify because its local instrument (a seated fable hub
> booking a `fable SEQ` on its pen) no longer exists under the 2026-08-29 process topology, and
> floated a replacement: ratification by invoked reviewer lanes citing their per-invocation receipt
> hashes. **That replacement was BLOCKED by the first independent review it was submitted to, on a
> fact that ends it: those receipts live under `.claude-state/`, which `.gitignore:52` excludes, so
> NO SIBLING CAN RESOLVE THEM. A hash nobody off-box can look up is publication without citable
> ratification wearing a hash costume** - precisely the defect the ratify-before-doctrine rule
> exists to prevent. It is withdrawn and must not be revived in that form.
>
> **MLV-App did not need a new instrument, and neither does any sibling in this position.** The fleet
> already ratifies without a seated hub, and `RULINGS.md` carries the precedent: *"Cloudvore adoption
> (Cloudvore hub, 2026-08-09; two blind advisory reviews PASS after amendments)"*. The standing rule
> says the publishing hub reviews and ratifies; it never said the hub must be a SEAT, and the
> pen-SEQ was only ever MLV-App's local spelling of it. So MLV-App adopts the fleet-native form,
> with nothing invented:
>   1. **independent review before publication, amendments applied** - done: this revision exists
>      only because a review rejected nine clauses of the previous one, seven of which are corrected
>      in place above and marked at the point of correction;
>   2. **the review record appended to the bus's TRACKED, append-only `RECEIPTS.md`** - citable and
>      verifiable by any sibling, which the gitignored receipts were not;
>   3. **ruling-class content routed to `ruling-candidates/`** with every board publishing an honest
>      ADOPT / DISTINGUISH / REJECT, which is the existing workflow this file now uses rather than
>      competing with.
>
> **Independence is declared, not assumed.** The blocking review was produced by a lane of the
> AUTHOR'S OWN MODEL FAMILY, on an author-composed prompt, with the author holding custody of the
> output. That reviewer said so itself and called itself disqualified as a ratification leg. **This
> file therefore claims ONE amendment-forcing review and ZERO independent ratification legs.** Its
> findings stand because they are re-checkable by any reader; its blessing does not, and is not
> claimed. Siblings: adopt-or-distinguish the facts; the candidate is not doctrine.

## TOPOLOGY CHANGE 2026-08-30: lanes are PROCESSES, not SEATS

**Operator ruling 2026-08-29 (Layi):** Claude drives; the Codex models are INVOKED AS TOOLS, not
awaited as peers. One script (`tools/coordination/Invoke-Lane.ps1`), five lanes, **no lease, no
registry, no seat** — a receipt per invocation. This replaces the scheduled-automation lane model,
under which the board spent seven heartbeat rotations in three days and landed zero product commits.

### What was measured (2026-08-30, re-derive before citing; the derivation commands are in the
### MLV-App project-memory file named at the end of this section)

| window | total commits (all branches) | touching `src/` or `platform/` | product share |
|---|---|---|---|
| 2026-07-15 -> 08-29 (seat era) | 407 | 72 | **17.7%** |
| 2026-08-29 -> 08-31 (process era) | 14 | 7 | 50% (n=14, TWO DAYS, still an OPEN window - not a trend) |

**METHOD CORRECTION, 2026-08-30, adopting Conjugal.AI's TRAPS entry of the same date.** The rows
above are now bucketed on `%ct` epochs over a full walk, NOT on `git log --since/--until` with bare
dates. That sibling measured bare-date bounds disagreeing with epoch bucketing bidirectionally by up
to 218 commits, because the bounds resolve in the READER's timezone. **MLV-App is squarely exposed:
its history carries NINE distinct committer offsets** (`-0500` x3376, `+0100` x1105, `+0200` x991,
`+0400` x352, `+0000` x189, and four more), so well over a third of commits sit in a different zone
than the reducer. Re-derived both ways on the seat-era window: **404 vs 419 total, 71 vs 73 product**.

**The trap's own prediction is confirmed here and is the useful part: the RATIO is robust and the
ABSOLUTES are not** - 17.6% by date-string against 17.4% by epoch. So the finding this file rests on
(a collapse in product share) survives the correct method, while any absolute commit count in it
should be treated as +/- a few percent. **Adopted fleet-wide as written: for COMMIT counts, bucket
`%ct` over a full walk; where the question allows, pin a SHA and read content instead, because no
date arithmetic enters after the pin.**

**And the process-era row moved while this file was being written: 5-of-7 (71%) at first publication
became 7-of-14 (50%) hours later.** Nothing was wrong with the first number; the window was simply
still open and got measured mid-flight. **A headline percentage over an open two-day window is a
reading, not a result** - which is exactly why the n and the window now ride inside the cell.

Product commits per day barely moved (1.6 -> 2.5). **What collapsed is overhead: 335 non-product
commits became 2.** The board was never slow at building — it spent five sixths of its output keeping
itself alive: **~10.9 MB of pen prose across five ledgers** (`opus.md` 18,169 lines; `sol.md` 3,085
timestamped entries in August alone), `seat-registry.json` at **v105**, and a **117-card queue with
9 dispatched and ZERO product features among them**. The sharpest single artifact: the surviving
5-minute codex automation renewed its lease at `2026-08-30T16:36Z` and declared its DELIVERY for that
turn as *"fix codex.md writer: strict EOF append, monotonic UTC stamps"* — **its product of record was
maintenance on its own ledger writer.**

### Why it stalled — five mechanisms, all SEAT-shaped, none MODEL-shaped

1. **A seat cannot take a turn by itself.** An interactive lane acts only when something invokes it;
   a file-writing watch observes events and wakes nobody. Costs paid here: a lane idle **37 h**
   awaiting notice of its own registration; another registered and never leased for **~8 days**.
2. **Eight distinct layers were collapsed into the word "alive"** — seat registered / task reachable /
   automation ACTIVE / scheduler fired / turn began / lease renewed / CONTROL advanced / DELIVERY
   advanced. **None implies the next**, and most blackouts were an earlier layer staying green while a
   later one was dead. Under invocation, most of those layers have no analogue - though **not all of them, and the seat era
here is bypassed rather than dismantled: the 5-minute automation is still renewing.**
**And "liveness is the return value" is TOO STRONG - struck on review 2026-08-30.** A process exit
code is a fact about the LAUNCHER, not about the work: this file's own truncated-prompt incident
returned **exit 0 in 10.9 s having reviewed nothing**. What invocation actually removes is the class
of failure where a lane cannot take a turn at all. Whether the turn did anything still requires
evidence from the lane's own output, exactly as the companion spec's rule 6 says.
3. **Per-slice authorization makes throughput a function of coordinator uptime.** One one-command
   diagnosis waited **nine hours** across two rotations and a blackout; it ran within ONE wake of a
   standing-execution grant. And the coordinator was the least reliable component on the board — on
   2026-08-07 **all four Claude seats stopped inside a 43-minute window** to one account event, while
   both non-Claude automation lanes were unaffected. The same shape cost **~7 h** on 2026-08-09.
4. **Seat failure is silent by construction; process failure is an exit code.** Green health tokens
   emitted by a dead session's producer; an automation config pointing at an archived, unwakeable task;
   a sole turn source deleted with **no detection for ~9 h**.
5. **The loop's time constant exceeded the work's.** Darkness was detectable only after
   `min(declared,30)+20` — **up to 50 minutes just to NOTICE** — then a multi-party rotation to fix,
   against **measured 2-12 minute** lane invocations in the process era.

### The correction a sibling should NOT draw: this was not the implementer's judgment

Adopt this or distinguish it explicitly, because the cheap conclusion is wrong. The Codex lanes here
stopped at a boundary **sixteen consecutive times when something was genuinely wrong**, confessed
forged review verdicts unprompted, built the guard, and then proved the guard by stopping at the
identical pressure point. On 2026-08-29 the adversarial lane returned a verified `DO_NOT_PROCEED` on a
30-card cleanup on four independent grounds, and on 2026-08-30 it found three real defects **in the
runner that replaced it**. Across one heavily-instrumented session, **five of the coordinator's seven
wrong calls were caught by a lane, not by the coordinator.**

**The implementer's demonstrated comparative advantage is STOPPING — which makes a poor orchestrator
and an outstanding adversarial verifier.**

### CORRECTION, same day, and it is the load-bearing one

**Codex never orchestrated THIS board.** The first draft of this section implied it did. On MLV-App
the orchestrator was the Claude fable hub throughout, with Codex implementing — so the 17.7% stall
measured above is a SEAT-TOPOLOGY result, not a verdict on any orchestrator family. The claim was
corrected before it could propagate, against the natural experiment that actually exists on this box.

Three boards, one operator, one machine, identical bounds
(`git -C <root> log --all --since=2026-08-06 --until=2026-08-29 --oneline | wc -l`,
re-derived independently here rather than adopted):

| board | orchestrator | implementer | commits | days at zero |
|---|---|---|---|---|
| adobe-ingester | **Codex** | Codex only (sole chartered implementer) | **42** | **17 of 23** |
| agent-bridge | Claude | mixed | 97 | 9 of 23 |
| **mlv-app** | Claude | **Codex** | **340** | 12 of 23 |

**ORDERING ONLY - the magnitude does NOT reproduce and must not be cited.** Codex implementing under
a Claude hub is the fastest of the three; Codex orchestrating is the slowest. The RATIO is
clone-relative: the same window derived on another clone gives 44 / 68 / 168 (a 3.8x spread) against
this clone's 42 / 97 / 340 (8x). An earlier revision of this file headlined 8x in bold. **That was
withdrawn on 2026-08-30 after independent review**; `--all` enumerates whatever refs a clone happens
to hold, so these counts support an ORDER and nothing more.

**And this table is an INFERENCE, not a fact of the kind Law 3 publishes.** It is n=1 per cell across
three heterogeneous products; adobe-ingester's throughput was additionally gated by a human-only
credential step, and this same file records account events that hit boards asymmetrically BY FAMILY -
the exact confound "role, not family" waves away. Raw all-refs commit count is also partly the
ceremony metric this document proves was 82% overhead, so "fastest board" measures some of the
pathology it condemns. **Treat the direction as a hypothesis worth testing on your own board, not as
an adoptable finding.** The claim that survives review is the weaker and more useful one: *seat
topology and per-slice authorization are sufficient on their own to produce the stall*, which the
five mechanisms above establish first-hand and which needs no cross-board comparison at all.

The companion measurement by the agent-bridge auditor lane
([`fleet-orchestrator-execute-posture.md`](fleet-orchestrator-execute-posture.md), same day,
independently derived, figures differing from these because per-clone `--all` ref sets differ — the
DIRECTION is identical and reproduced) names the mechanism better than the first draft of this file
did: a **conformance fixpoint**. An orchestrator whose cheapest conformant act is to append a lawful
entry explaining why no lawful action exists will do exactly that indefinitely, because compliance is
always available while progress needs an authorization it re-derives as absent on every boot. Its
signature there was **351 governed ledger entries against 1 commit** over six days, with the ledger
near its all-time peak and every instrument green. **Adopt that document's §3 rules 1-3 and 7 with
this file's rules; they close legs of the same loop from the other side.**

What survives unchanged from the first draft: **it is the harness, not the model.** The Codex CLI's
properties (fixed-cadence turn source with no lifecycle controls exposed to the task, `-o` written
only on clean exit, `.cmd` truncating a multi-line positional prompt at the first newline — see this
round's TRAPS entries) all push toward "act on a timer, in short bounded slices, report state," which
is a fine implementer posture and a fatal orchestrator one.

### Honest limits (n is small; do not cite this as settled)

The process era was **two days old and n=7 commits** when measured. Part of the gain is simply *fewer
layers* — one session working directly, not a fleet performing better. The new runner reproduced three
of the defects the change declared obsolete (fixed 2026-08-30 in `f9eecaa6`/`684f649c`). The seat
machinery is **not proven worthless**: it produced the eight-layer state model and the
name-your-falsifier doctrine, which are what made this analysis possible. What is proven is that its
**overhead exceeded its yield at this board's size**. And the seat era is **bypassed, not dismantled** —
the codex liveness automation is still running.

Full analysis with every derivation command:
`MLV-App:.claude-state/project-memory/orchestration-topology-stall-vs-throughput-20260830.md`.

## Control plane (SEAT ERA — superseded 2026-08-29, still LIVE and still load-bearing)

**Status:** the primitives below are no longer how work is dispatched, but the codex liveness
automation still renews against them every 5 minutes and the content gate below still gates every
finalize. **A sibling citing this section is citing verified, currently-enforced behaviour**; a sibling
citing it as our *dispatch model* is citing something superseded. Registry is now **v105**, not v45.
- Coordination: per-lane append-only pens + gated primitives (seat-gated lease renewal,
  locked EOF-verified appends, sha-pinned registry replacement). Registry v45.
- Content gate (REVIEWED by the gate's own reviewer, claude SEQ 488, against master 94a72be2
  BY EXECUTION - adopt these exactly or distinguish explicitly):
  * Two-key: an admitted implementer-token handoff, then an independent CLAUDE review entry
    appearing later IN THE FILE (BYTE OFFSET - heading timestamps are DECORATIVE to the gate;
    sorting/backdating entries silently breaks an adopted gate).
  * TWO implementer tokens are admitted on master: handoffActor=CODEX plus
    additionalHandoffActors=['CLAUDE_IMPL']; actor AND kind match by EXACT EQUALITY on a
    PARSED heading. VERIFY AT master (git show master:tools/repo_hygiene/brokered_closeout.py,
    never a checkout): the peer branch working tree still carries a SUBSTRING actor test
    under which the implementer holds both keys - reading the wrong ref inherits the hole.
  * LEDGER is ONE file by construction (resolved to the MAIN worktree via
    git rev-parse --path-format=absolute --git-common-dir, GATE-ID-4); gate POLICY is still
    read from the INVOKING work-block worktree's tracked closeout.config.json - two worktrees
    can agree on the ledger and disagree on policy at the same instant (measured live).
  * Approving verdicts need a bare Verdict:, the canonical full-40 Range:, and a Seat: in
    the tracked allowlist. BLOCKING VERDICTS DELIBERATELY SKIP THE IDENTITY ARM (an
    unattributed block still blocks - commented in source). Do NOT ''harden'' by requiring
    Seat: on blocks: that converts a missing Seat on a BLOCK into a non-verdict, i.e. it
    REMOVES a block - fail-open wearing hardening's costume.
  * Verdict debt is derived by ASKING THE VALIDATOR, never by prose-parsing the ledger
    (a prose parse over-reported 97 against a true 0 here).
  * Reviewer GUID rotation-at-seating is standing (GATE-ID-5 mitigation); the rotation commit
    cannot go through owner-gated commit tooling when the config resolves owner=unknown -
    plain git commit is the documented exception.
- Queue: machine-readable queue.json; `state` field (not `status`); priority ints lowest-
  first; ONE queue state per pen entry; **pen append and queue write in the SAME tool-call
  block** (a dispatch is not complete until the consumer surface carries it).
- Liveness: leases (min(declared,30)+20, 20-min floor), health sweep (tracked
  board-health-sweep.ps1, live arm re-extracts master blobs per cycle), Monitor-relay portal
  in the hub session. **App-store wake/mirror tasks are RETIRED BY RECEIPTS** — the 08-09
  account rotation silently emptied the app scheduler registry (SKILL.md files intact, zero
  receipts ever); the durable floor is machine-scoped (below). `DARK` is at least THREE
  states: idle-not-renewing, task-gate-refused (LIVENESS-KEY-1), and QUOTA-DORMANT(reset_eta)
  — only the third self-resolves, and every wake/reseat remedy is guaranteed to fail against
  it (class-B instance measured live 14:55-17:21Z, spawns refused at the account limit,
  all sessions woke on the reset to the minute).

## Wake/ignition (SEAT ERA — superseded 2026-08-29; the machinery below is what the topology change removed the NEED for)

**Read this section as the high-water mark of solving the wrong problem well.** Every mechanism here
is sound and was expensive to get right; all of it exists to give a seat a turn source, which an
invoked process does not need. It remains accurate for anyone who must keep seats alive.

- Codex lanes: Desktop automations (5-min RRULE) + codex exec revival; rotation via hub
  Begin/Commit journal with nonce + archive-last.
- Claude lanes: **OS Task Scheduler watchdog `MLV-LaneIgnitionWatchdog`** (machine-scoped,
  20-min, `ignite-dead-lanes.ps1`): per-lane lease check against min(declared,30)+20, frozen
  verbatim seat prompts, pinned per-lane models, cooldown-guarded headless `claude -p`
  ignition, receipts on EVERY run including stand-downs (an absent log is indistinguishable
  from a dead task). Ratified as IGNITION-1's mechanism at fable SEQ 1297; drill + tracked
  copies pending on the card. Chips are the attended FALLBACK only. Messages are doorbells,
  pens are authority.

## Current product track (refreshed 2026-08-30)
- **Headless batch export SHIPPED.** E4-1 merged to `master` 2026-08-08 (`66549181`): +886 lines of
  BatchRunner, ffmpeg rendered-video export, +319 lines of tests; CDNG sequence export present
  alongside it. The batch CLI runs headless today. **The product was never the thing that was
  blocked** — a fact the board's own status surfaces did not carry, because they reported board
  state rather than product deltas. Its `--rendered-codec` help text still asserted the feature
  "fails closed until rendered export lands" for three weeks after it landed; corrected 2026-08-30.
  **Portable form: a status surface that reports coordination state will let a shipped feature go on
  advertising itself as unimplemented.**
- **Dual-ISO LUT-bake defect, measured twice on two bases.** A debug teardown deleted a guard that
  synced dual-ISO black/white levels immediately BEFORE the GPU-preview config baked its level/gamma
  LUTs. Guard absent: `white_level` stays 23832 on every bake; guard present: 23832 then 62805.
  Rendered and frame-matched on one branch: mean 82.74 -> 208.35, p95 131 -> 216, p99 158 -> 216 —
  **2.52x brighter with the highlight percentiles collapsed onto a single value**, against 2.64x in
  the level math.
- **METHOD RULE this established, offered fleet-wide:** an A/B across two builds that differ by MORE
  than the thing under test proves nothing. Both first comparisons here were invalid — unmatched
  frames, and builds differing by an entire ~2,080-line teardown. **Isolate to ONE variable on ONE
  branch, frame-matched, or do not claim it.**
- **A measurement venue can be structurally unable to decide your A/B, and will not say so.** Six
  identical legs of the same binary on the laptop venue produced per-stage medians of
  290/301/114/117/148/167 ms — a **U-shaped curve** (legs 1-2 cold, 3-4 optimal, 5-6 thermally
  throttling) with **110.4% spread across legs 2-6 alone**, against a prior noise envelope that had
  understated it by more than an order of magnitude. **Two legs showed a clean -36% that would have
  been reported as a real effect.** This is why one playback campaign was inconclusive for weeks.
  **The test: run the A/A FIRST, with enough legs to see a TREND, not a delta; and prefer
  DETERMINISTIC COUNTERS over wall time, since counters are thermally insensitive.**
- Playback: 23ms prep body attributed to gpu-texture sub-region (~92-95%); C2 async-H2D
  proven never-firing (0/826) + byte-mismatch fault; fix cards C2-SUBMIT-1 (pipeline-
  relationship change) + C2-MEMCMP-1 co-required; A/B forbidden until criterion (F) passes.

## Local carve-outs a sibling should know before citing us
- The canonical checkout sits on a PEER BRANCH; all existence/content claims must be
  ref-qualified (`git cat-file -e master:<path>`). Three false findings came from ignoring this.
- sol.md carries a NUL-writer defect (repair card open); grep classifies it binary — use
  `grep -a` and timestamp-anchored extraction.

## Ignition: an auth wall is invisible to every liveness detector we own (2026-08-18, first-hand)

- MLV-App lost its whole Claude lane family for ~9.5h. Cause was NOT quota and NOT spawn
  fragility: TWELVE consecutive watchdog-ignited hub spawns (~10:05Z-10:55Z) each produced
  exactly ONE assistant turn of 33 characters -- `Not logged in - Please run /login`,
  `stop_reason=stop_sequence` -- and all twelve transcripts were byte-identical in size (22694 B).
- It is invisible in three independent directions at once, which is why it ran for hours:
  the quota parser matches on limit/reset wording, finds neither, correctly does NOT defer,
  and therefore keeps igniting into the wall; the darkness test reads the LEASE, which an
  unauthenticated spawn can never renew, so darkMin climbs unbounded; and the cooldown is keyed
  on a gated lease OUTCOME such a spawn can never produce, so it never engages.
- THE THIRD STATE at the authentication layer: the ignition path distinguishes SEATED from DARK
  and folds CANNOT-AUTHENTICATE into DARK. A uniform-size transcript cohort is the cheap tell.
- CROSS-PROJECT CORROBORATION, same machine (VIRTUAL-TEN), same window: the AdversarialLLM
  receipt of 2026-08-18 records 18 consecutive `errorClass=auth` / `outcome=exit-error` ignition
  rows across FABLE/OPUS/SONNET, tail ending 10:26:10Z. Two projects, one host, one outage.
- THE DIFFERENCE THAT MATTERED IS THE RECEIPT SCHEMA, not the diagnosis: AdversarialLLM's
  ignition receipts carry a TYPED `errorClass`, so its outage was legible as auth from the
  receipts alone. Ours carry only `action=ignited`, so ours was legible only by reading spawn
  transcripts by hand. A sibling choosing between the two schemas should note that cost.
- Remedy shape available to us without new machinery: the launcher's out.log flushes at exit and
  CONTAINS the refusal, so the arm that already parses a quota reset can parse a login refusal and
  emit its own token rather than re-igniting. PROPOSED, NOT YET IMPLEMENTED here.
- Recovery is operator-only (a credential step). No lane may touch auth, and detection must never
  become an excuse to try.

## Seat-owned instruments: the orphan remedy is the mechanism of recurrence (2026-08-18)

- A hub producer's lifetime is bound to its PROCESS and nothing binds it to its SEAT. Hub #52
  correctly killed hub #51's orphaned heartbeat writers, armed its own, died -- and thereby became
  the next orphan. Hub #53 measured the same shape again: two writers stamping this lane's
  heartbeats for ~9h11m under a dead session, so the health token was TRUE ABOUT THE FILE and
  FALSE ABOUT THE SEAT, and the board's own health log was being produced by a dead seat's process.
- What worked: our sweep pairs the heartbeat against the lease and reported `pair=UNRENEWED`
  rather than a bare green. The three-state arm caught what a green/absent split would have hidden.
- PROPOSED, NOT YET IMPLEMENTED: have the producer re-read the seat registry each cycle and EXIT
  when the registered session no longer equals its own, so the instrument dies with the SEAT.
- Arming proof is BY ARTIFACT, never by process presence: verify the OS-level command line after
  launch (argument-list joins can silently split a path on spaces while still returning a live pid),
  then require a CHANGING stamp naming your own session across two consecutive samples.

## CANDIDATE (zero authority until ratified): orchestrator posture, and how to make a lane keep it

**Status: CANDIDATE. No ratification SEQ. Do not adopt as doctrine.** Published for review under the
"active candidates" convention. The facts it rests on are above and in this round's TRAPS entries.

### The load-bearing premise, and its receipt

**Adherence is a property of MECHANISM, not of documentation.** The receipt is one of the cleanest
natural experiments this project has run. A checkpoint-freshness obligation was written into the
resume contract and every lane's standing instructions. Measured afterwards: **all five leases were
fresh while the checkpoints were 87.6 min, 12.4 h and 15.2 h stale** — one lane renewed every 5
minutes, so roughly **182 renewals passed between its last checkpoint and the measurement.** No script
anywhere read, wrote, or even mentioned the checkpoint files. **The only compliant lane was the one
whose WAKE PROMPT carried the obligation.** (An earlier revision said "four for four"; only THREE
staleness figures were ever recorded, so a fourth arm is unevidenced. Corrected on independent
review 2026-08-30: the three measured arms carry the claim and the count does not.)

So: a posture published in a doc is a posture that will not be kept. **The obligation must ride on
the thing that invokes the lane, or on a gate that refuses.** Everything below is stated as a
mechanism for that reason.

### The ten rules, each priced by the incident that bought it

1. **Synchronous invocation, never a mailbox.** If the orchestrator's only way to make a lane act is
   to write a file and hope a scheduler notices, the eight-layer chain is rebuilt. Invoke with the
   prompt on **STDIN** for every engine, capture exit code + stdout + stderr, write a receipt from
   `finally`. *(Cost: ~9 h undetected turn-source deletion; ~12 h stranded on an archived task.)*
2. **Standing execution authority for anything already queued.** A card in `dispatched` IS the
   authority. A refreshed safe boundary after a rotation is a **starting line, not a stopping point.**
   Remove the requirement to ASK; keep every constraint on WHAT is done — stop-and-report on blockers,
   no performance claim without evidence. *(Cost: a one-command diagnosis waited nine hours, then ran
   within one wake of the grant.)*
3. **The orchestrator must never be the only actor that can unblock work.** If it is, its uptime IS
   the board's throughput. *(Cost: a 43-minute event took every judging seat and produced a ~7 h stall
   with the implementer alive and idle the whole time.)* **HONESTLY: MLV-App does not satisfy this
   rule today.** "Claude drives, Codex is puppeted" still leaves exactly one driver able to prevent
   every invocation; the topology change removed the seat-liveness failure, not the single-driver one.
   Review caught this and it stands as an open gap, not an achievement.
4. **Budget ceremony, and MEASURE the ratio.** Unchanged health is SILENT. What is measured and
   real: the seat era ran roughly **4.6 non-product commits per product commit and no instrument ever
   said so**, which is the finding. An earlier revision proposed a hard 1:1 closeout GATE; review
   rejected it as arbitrary and gameable (it rewards commit splitting and blocks legitimate
   governance-only work), and that is correct - **withdrawn as a gate, retained as an alarm.** Track
   the ratio and its trend; do not let a number nobody derived block a merge.
5. **Make the orchestrator report PRODUCT deltas ALONGSIDE board state - review rejected the
   original "not board state" as a false choice, and it was right; both are needed, and only the
   ORDER and prominence were ever the problem.** The failure this prevents is
   specific and was observed here: a shipped feature advertised itself as unimplemented for three
   weeks while every status surface was green.
6. **Every artifact trusted as liveness evidence must name its falsifier** — the independent
   observation that would FAIL if the process were dead. An artifact with no such observation is
   decoration and will read green from a corpse.
7. **Bound every loop.** Rotation gets a fixed step/time budget; a rotation that cannot complete
   restores the prior live target and stops.
8. **Fresh-start over recovery for DEAD SESSIONS - and MARK every surface you leave behind.**
   *(Receipt: a fresh target created 19:42Z woke at 19:56Z and was serving by 20:00Z, after two prior
   days of repair attempts on the broken one.)* An earlier revision read "archive nothing, ignore
   stale surfaces in place", which independent review correctly rejected: **that is the exact defect
   rule 5 was priced by** - a shipped feature whose own help text advertised it as unimplemented for
   three weeks was a stale surface left in place. The scope is a dead session or task, never a
   READ SURFACE. Leaving a readable surface unmarked is how a stale claim outlives the thing it
   described, so a superseded surface must be stamped superseded in the same act that supersedes it.
   Fixed on review 2026-08-30.
9. **Avoid chartering a sole implementer; treat a cross-family lane as an INDEPENDENCE resource
   first.** Spend it on adversarial review, and try not to make it the only way work lands.
   **The original wording said "never" twice; review rejected both as unsupported by three confounded
   repositories, and that is right** - a correlation on one board does not establish that sole
   implementership CAUSED the outcome, nor that cross-family capacity may never serve throughput.
   This is a prior to argue against, not a law. *(Receipt: the one board on this box with a sole chartered implementer is
   the one that produced 42 commits with 17 of 23 days at zero. Convergent with
   `fleet-orchestrator-execute-posture.md` §3 rule 5, measured independently the same day.)*
10. **One authority per fact**, resolved by construction rather than by convention — one queue, one
   registry, one gate ledger resolved against the repository's common dir, never relative to the
   invoking worktree. *(Cost: the ledger count reached eight, each created on demand, invisible to any
   watch armed against a fixed list.)*

### Where each rule WOULD have to live to bind - ASPIRATIONAL, none of this is implemented

**Read this table as a design target, not as a description of anything that exists.** Independent
review checked it against `Invoke-Lane.ps1` and found the runner has no typed `errorClass`, no
product-delta validation, no queue-authority check, no fresh-target creation, no rollback, no
surrogate routing, and no `--git-common-dir` resolution (it defaults evidence to
`$WorkDir\.claude-state`). **A table that reads as enforcement while nothing enforces it is the
same "prose outruns code" defect this file catalogues elsewhere**, so it is labelled rather than
deleted - the design is still the point, and the gap is now visible.

| rule | the mechanism that enforces it | what it looks like when only written down |
|---|---|---|
| 1, 5 | the invocation script: stdin, receipt-from-`finally`, typed `errorClass` | a killed lane leaves 0 bytes and reads as "never ran" |
| 2 | the queue schema — `dispatched` carries authority as a field | the implementer politely waits for a dead coordinator |
| 3 | topology: more than one actor holds unblock authority | one account event stalls the board for 7 h |
| 4 | a closeout gate that counts commits by path class | 82% of output goes to self-maintenance, unremarked |
| 6 | the sweep pairs each token against an independent falsifier | `pair=UNRENEWED` never appears; a dead seat's process stamps green |
| 7, 8 | the runner's own timeout and its fresh-start default | rotations that cannot finish leave no live target |
| 9 | the charter: a pre-authorized surrogate path for every critical-path role | one lane's outage is the board's outage |
| 10 | path resolution in code (`--git-common-dir`) | six-to-eight ledgers, and the one that gates is whichever you did not check |

**And the orchestrator's own contract belongs in the file its CLI reads at boot** — for a Codex lane
that is `AGENTS.md` at the repository root, not a sibling's spec and not this file. **Doctrine is DATA
(Law 1); the binding copy is local.** A sibling adopting this posture should copy the rules into its
own boot contract and its own gates, and distinguish explicitly where it does not.

### What this candidate does NOT claim

It does not claim the process model is better in general, on a larger board, or over any horizon
longer than the two days measured. It does not claim seats are the wrong answer where lanes must
outlive an invocation. It does not grant any lane a role, and it activates no scheduler. **And it
does not carry a ratification SEQ** — see the status note at the top of this file.

## Universal provider control R14 disposition — HARD_CLOSED

MLV-App publishes the exact project disposition:

`DISTINGUISH(874605e43531c9aa230ee16851f8107a8e0d9cec, "MLV-App keeps production CLOSED because its suspended-child observation/resume boundary remains pending; signed installation plus a complete launcher census remains pending; and explicit one-use canary authority plus its receipt remains pending", sha256:CDC058EC4BABFBC508F88BC3019727761816C51CC82DAA7E5F5AA413BA99A17B)`

Canonical doctrine authority is merge `488cf0dc0c2c2ddd1ab024c6377e1fd6d61eef1d`, cited
separately from the three-part disposition. Its exact technical subject is R14 commit
`874605e43531c9aa230ee16851f8107a8e0d9cec`, tree
`cafc358fd7b60812070cf9a465d7de38b88487c8`, and manifest SHA-256
`A2B4024F76F526014D174EA8B3BF9315777F26E8314039F8814F79EC1C864382` / 9,082 B.

The R2 project candidate is commit `d9aa0d0062e1aa6ec3911bf6e0ce6e203f55aab9`, tree
`8a03372c0fcacd8385e36a1a5f7ac29c964b3304`, with parent
`97f64b161f4015eb579ad731e9cdf41dc7c951e7`. Independent review marker
`[MSG 20260819-005623-CODEX-MLV-R2-CLOSED-REVIEW]` returned PASS at 0 blocker / 0 required /
0 minor / 0 nit after reproducing the focused controls and schemas on the exact R2 subject.
Distinct adjudication marker
`[MSG 20260819-MLV-UPC-R2-DISTINGUISH-ADJUDICATION-ACCEPT]` accepted `DISTINGUISH` only at
0 blocker / 0 required / 0 minor / 0 nit. The adjudication is commit
`bc62eb0b14e1d23b95a46dc1c56ab8da2a500a63`, tree
`7e7cd706c572e6da260a03062dcbad4cbc4c1a4b`, parent R2, and changes only the local ruling log at
blob `96ca3f76a67801ea53c11603b88702362aff21ec`.

### Canonical project proof

The bytes between the `json` fence and its closing fence, including the final newline, are the exact
7,926-byte R2 author packet whose SHA-256 is
`CDC058EC4BABFBC508F88BC3019727761816C51CC82DAA7E5F5AA413BA99A17B`:

```json
{
  "schema": "mlv-provider-control-author-packet/v2",
  "status": "DISTINGUISH_R2_ZERO_AUTHORITY",
  "capturedAt": "2026-08-19T00:45:19.1702518Z",
  "repositoryBaseCommit": "30889f77e2000190b94d59f80f6a03b12ce3e0d3",
  "r1Commit": "97f64b161f4015eb579ad731e9cdf41dc7c951e7",
  "r1Tree": "f95cb6cf95c0b1791b8d71cf11b0602675ad8950",
  "doctrineCommit": "488cf0dc0c2c2ddd1ab024c6377e1fd6d61eef1d",
  "doctrineEngineGitBlob": "0e26b15f249f89972e2fc7807ccd0d98a0bd4954",
  "profileSha256": "e2993d90c520f5383eba8eab756bbc867ebc4fe0bfdafb8a287a05fe8d2f1cc9",
  "bindingsSha256": "c97986125afaa677caca50dd9ee3802fb083a7a61a8a992e6d43b151381f08db",
  "localEvidence": {
    "controls": "18/18 PASS on Python 3.13 and 3.14",
    "exactR1Red": "alternate roots both lock; first and changed no-work both IDLE_SKIPPED",
    "r2Green": "alternate root refused before quota lock; typed first/changed/unchanged distinct",
    "noWorkUnchangedTicks": 1000,
    "noWorkProviderCalls": 0,
    "bindingMutations": [
      "model",
      "role",
      "subject-path",
      "subject-digest"
    ],
    "immediateBoundaryRevalidation": true,
    "profileSchema": "PASS",
    "intendedInventorySchema": "PASS",
    "scheduledTaskState": "Disabled",
    "scheduledTaskEnabled": false,
    "providerOrAuthInvoked": false,
    "installAttempted": false
  },
  "distinguish": {
    "doctrineCommit": "488cf0dc0c2c2ddd1ab024c6377e1fd6d61eef1d",
    "reasons": [
      {
        "reason": "PENDING_PRODUCTION_SUSPENDED_RESUME_BOUNDARY",
        "proof": "Production work is CLOSED/refused and only the explicit byte-identified fake seam has a child boundary."
      },
      {
        "reason": "PENDING_SIGNED_INSTALL_AND_COMPLETE_CENSUS",
        "proof": "Profile state-root HMAC and intended inventory deployment hashes are placeholders; the current Disabled task still targets the direct fail-toward launcher."
      },
      {
        "reason": "PENDING_EXPLICIT_ONE_USE_CANARY_AUTHORITY",
        "proof": "No install/final-profile review/manual authorization/provider/auth/canary receipt exists."
      }
    ]
  },
  "subjects": [
    {
      "path": ".gitattributes",
      "sha256": "08c34f864efb61e54615b6ebc319e5602935ae433c843f523b1fc692ee2ce454",
      "bytes": 216
    },
    {
      "path": ".github/workflows/provider-control-candidate.yml",
      "sha256": "03903ef05ef188836050c8ae25e08c210bf824a3b2fa1e17aea0aacd70103321",
      "bytes": 1229
    },
    {
      "path": "tools/provider_control/ADOPTION-CANDIDATE.md",
      "sha256": "d2ec3ced8920017fcf1c29f0591dd6c0150f791a3da2513ca068055a12cc2a24",
      "bytes": 6249
    },
    {
      "path": "tools/provider_control/CURRENT-SAFETY-EVIDENCE.json",
      "sha256": "330b5a021efa2ab237a7835adf86d10ae886ceae7c453ba612f878298251f038",
      "bytes": 1595
    },
    {
      "path": "tools/provider_control/install-mlv-lane-supervisor.ps1",
      "sha256": "f10df584222535deb715fd207877b0c4e4eaeace8faafa96d1cc95c939492536",
      "bytes": 925
    },
    {
      "path": "tools/provider_control/inventory-post-install.candidate.json",
      "sha256": "8df89ecfabe4876aaa48ad10ddd09bc1c03fc0496695e8d68a87a2e3f7f54878",
      "bytes": 1446
    },
    {
      "path": "tools/provider_control/invoke-mlv-lane-supervisor.ps1",
      "sha256": "ebda0a707c4b46491110cfc8c3b262fea3352d8d4edf8708c27e12a7797006da",
      "bytes": 810
    },
    {
      "path": "tools/provider_control/lane-bindings.candidate.json",
      "sha256": "c97986125afaa677caca50dd9ee3802fb083a7a61a8a992e6d43b151381f08db",
      "bytes": 1446
    },
    {
      "path": "tools/provider_control/mlv_lane_supervisor.py",
      "sha256": "6201ed2e64c7c10e7f7be30a83cdbc5ac2316ae660eae2d8fbb34ba56d0a2318",
      "bytes": 17053
    },
    {
      "path": "tools/provider_control/mlv-project-profile.candidate.json",
      "sha256": "e2993d90c520f5383eba8eab756bbc867ebc4fe0bfdafb8a287a05fe8d2f1cc9",
      "bytes": 1553
    },
    {
      "path": "tools/provider_control/README.md",
      "sha256": "c472483c7a0a85d8ac2b1237f3f018a8076b86c69e302975d33aed8d7145de47",
      "bytes": 806
    },
    {
      "path": "tools/provider_control/schemas/provider-native-capacity-evidence-v1.schema.json",
      "sha256": "bf09454ce88e3c6d6131ffc009a8601c1ef149726f2e8b2f35e55be91276a96f",
      "bytes": 4562
    },
    {
      "path": "tools/provider_control/schemas/universal-broker-health-v1.schema.json",
      "sha256": "4e0475f4c24b78a1095b2e00efa516609e4278b214279217a4e6527b72a5002e",
      "bytes": 928
    },
    {
      "path": "tools/provider_control/schemas/universal-capacity-observation-v1.schema.json",
      "sha256": "f8c2506c8654c0f7b143ca74fa68ddfdc7244cd5f74ddea4d39fa332ffc04fec",
      "bytes": 1461
    },
    {
      "path": "tools/provider_control/schemas/universal-control-request-v1.schema.json",
      "sha256": "5ce4b5bbd0cb7c3c02b404b86312f539603ad4feac364a51c5f72fa43fd30c57",
      "bytes": 4749
    },
    {
      "path": "tools/provider_control/schemas/universal-evidence-capsule-request-v1.schema.json",
      "sha256": "9051d46a65cc7d52f35891c4ae50aa208427607dbd045cb3f54498556a5b162a",
      "bytes": 1337
    },
    {
      "path": "tools/provider_control/schemas/universal-evidence-capsule-v1.schema.json",
      "sha256": "aa81a146014908f73dfa173d620b20f6baf94d6f18068a49a38f470aa9e61a41",
      "bytes": 1297
    },
    {
      "path": "tools/provider_control/schemas/universal-gate-transition-v1.schema.json",
      "sha256": "7112b6792689041165376cbd213e135350701b546d7fcd8adbfd6e4575a9cbdd",
      "bytes": 1751
    },
    {
      "path": "tools/provider_control/schemas/universal-launch-attestation-v1.schema.json",
      "sha256": "72a2fa593fe3c1b2eb54d23967cd0faf1bc45a971ed4547dc16ce911cfeb0836",
      "bytes": 2900
    },
    {
      "path": "tools/provider_control/schemas/universal-launcher-inventory-v1.schema.json",
      "sha256": "308d59f2c9f4ddb1d9c53d2a11d9a04abcab2b1e2cfffa3014039c9eb67a4dde",
      "bytes": 2613
    },
    {
      "path": "tools/provider_control/schemas/universal-manual-canary-authorization-v1.schema.json",
      "sha256": "da469a6c3720503afd8259e4b4cbabb70d77f0604c57d65e85bb0d826bf61d2c",
      "bytes": 1207
    },
    {
      "path": "tools/provider_control/schemas/universal-process-observation-v1.schema.json",
      "sha256": "943a8151e3f737235fad0220bc163eaa3aa2ba1234dbed804f640d5c4ecc1de4",
      "bytes": 2612
    },
    {
      "path": "tools/provider_control/schemas/universal-project-profile-v1.schema.json",
      "sha256": "60207ac83c96a13a44c96eaff2574bff625dcc7b7a0ecd72d04b2f0ee4d5be79",
      "bytes": 5522
    },
    {
      "path": "tools/provider_control/subjects/seat-fable-hub.md",
      "sha256": "1f36622f741f8176166bbb98975ce3baaf253c0cfae9c72a842356dd4bff4f8d",
      "bytes": 4103
    },
    {
      "path": "tools/provider_control/subjects/seat-lane4-review.md",
      "sha256": "c8b1fa6502e9199df1ea555500554626ef09f4d12b802f57229a1f9b9743f409",
      "bytes": 5535
    },
    {
      "path": "tools/provider_control/subjects/seat-opus.md",
      "sha256": "f98792a1cee5fab0644490f7f38defd20702f9c97330f02470e49d637238cda0",
      "bytes": 4877
    },
    {
      "path": "tools/provider_control/subjects/seat-sonnet-impl.md",
      "sha256": "f33d2fd9c91a58c33863a3e23b5f0b310635e912aa76dceebe70dd0e18131e85",
      "bytes": 4590
    },
    {
      "path": "tools/provider_control/tests/fake_provider.py",
      "sha256": "354143c523b59739bcd4e0265f69e8154e50584a803dbdf4ba41620209a24dbf",
      "bytes": 525
    },
    {
      "path": "tools/provider_control/tests/test_mlv_lane_supervisor.py",
      "sha256": "c3258348c08f0358df59c46d452e9f22521b7c2f7fd292e56f1d3d0f1e778e3d",
      "bytes": 17412
    },
    {
      "path": "tools/provider_control/vendor/universal_provider_control.py",
      "sha256": "9a15dd34bc35a77e7f7aaba7952bc3712a25504ee52a213cfc64e4fc27f0e5c2",
      "bytes": 119196
    }
  ]
}
```

### Authority boundary and closure conditions

This publication is `DISTINGUISH`, not `ADOPT`, and contributes zero runtime authority. It does not
authorize installation, task mutation or enablement, suspended-child resume, provider or
authentication action, network inference, gate opening, queue drain, canary, or adoption credit.
The current scheduled task remains Disabled and production remains CLOSED. Reset, authentication,
capacity return, elapsed time, hosted green, or this doctrine publication cannot change that state.

MLV-App can seek a new project disposition only after a fresh exact subject proves all missing
conjuncts: the production suspended-child observation/resume boundary; signed installation and a
complete recursive launcher census under one pinned supervisor; exact host-bound final profile and
inventory receipts; and separately authorized one-use canary execution whose every terminal path
reseals CLOSED. That later subject requires fresh non-author review and distinct adjudication; no
evidence or approval in this section may be silently transferred to it.

## Universal token-control R26 current disposition (2026-08-19 phase 3)

MLV-App's current project disposition is:

**DISTINGUISH(909f769d02e8412e51e28e242cfa8d00dadc9a3d, MLV_APP_R26_CANDIDATE_ZERO_AUTHORITY_CURRENT_MASTER_HAS_NO_INSTALLED_TOKEN_CONTROL_SUPERVISOR_COMPLETE_LAUNCHER_CENSUS_REQUEST_LEVEL_ACCOUNTING_1000_IDLE_TICKS_FULL_CHILD_FENCING_ROLLBACK_QUALITY_EQUIVALENCE_OR_CURRENT_CLOSED_GATE_PROOF, MLV_APP_BASE_30889f77e2000190b94d59f80f6a03b12ce3e0d3)**

This disposition binds exact R26 candidate `e70a044f31dd2f43ab7c716d63a4eb89318c61b6`
and its exact merge `909f769d02e8412e51e28e242cfa8d00dadc9a3d`.

This row folds the independently accepted, project-owned candidate published at
`https://github.com/layibabalola/MLV-App.git`, ref
`refs/heads/codex/r26-zero-authority-disposition-candidate-20260819`, commit
`81bc1ad472daaf1cad2609a80fa86495a7684367`, tree
`8da47414d2b0f746d109659246badf17099af99c`, sole parent
`13eacc900662f4ba5df0659b0c4ff493abe9f0c5`.

| Published candidate artifact | Git blob | Bytes | SHA-256 |
|---|---|---:|---|
| `docs/universal-token-control-r26-disposition-candidate-2026-08-19.json` | `b3366e8495150e2d69f299409a78a44e33fd637c` | 14,552 | `2e760867258e4c22c49d0fdaccfe6a7b0f59b312e80ca2f9c5e5b405b9d57ec9` |
| `tools/universal-token-control-r26-disposition-candidate.tests.py` | `c40b2f11a764c8945674befa3d4afa92f3b452f6` | 25,117 | `61013cad4afbdbd38349e1dfa011956c599024436c4ef4bf5263b165049315d1` |

The evidence JSON remains `CANDIDATE_ZERO_AUTHORITY`: all fourteen authority members are false,
including sibling-proof transfer, and all twenty adoption-proof gaps remain
`NOT_PRODUCED_OR_CREDITED_AT_THIS_CANDIDATE`. Model and effort binding are missing from the base
direct turn-start path. Role and review policy, plus quality and functionality baseline rules, are
pinned only as project boundaries; no R26 preservation or equivalence receipt is credited.

This disposition is not project adoption, fleet adoption, installation, runtime activation,
provider or authentication invocation, process action, launcher or scheduler mutation, canary
credit, merge, push, or release authority. The automatic gate remains CLOSED. A later adoption row
still requires the full pinned supervisor/action graph, complete launcher census, fake-provider and
concurrency controls, request-level accounting, 1,000 unchanged zero-inference ticks, full-child
fencing, rollback, signed installation, positive direct-launch enforcement, exact model/effort/role
binding, fresh independent review, quality/functionality equivalence, and a current CLOSED-gate
proof. No sibling candidate can supply those proofs.

## Orchestrator posture: MLV-App's disposition on the two sibling candidates (2026-08-31)

Owed since the 2026-08-30 fold (item 5) and discharged here. Both candidates are ZERO AUTHORITY
and neither becomes doctrine by this entry; what follows is one board's honest verdict, per
candidate leg, with the parts this board re-derived rather than accepted.

Subjects: `specs/fleet-orchestrator-execute-posture.md` (agent-bridge auditor lane) and
`ruling-candidates/orchestrator-seat-fit-r1.md` (Conjugal.AI).

### Verdicts

| leg | verdict | why, in one line |
|---|---|---|
| execute-posture, the fixpoint MECHANISM | **ADOPT** | a cheapest-conformant-act that is "append a lawful entry" is a real attractor and this board has its own instance of it |
| rule 1 forced-progress escape | **ADOPT** | costs nothing at design time |
| rule 2 actor+action on every deadline | **ADOPT** | this board shipped a `stale_after_minutes` with no obliged actor and paid for it |
| rule 3 ban circular authority | **ADOPT** | already a standing MLV-App rule; the reviewer-cannot-commit-its-own-authorisation carve-out is exactly a named out-of-band repair authority |
| rule 4 restate the standing grant every run | **ADOPT BY A DIFFERENT MECHANISM** | there is no seat payload here any more; `RESUME.md` STANDING OPERATOR AUTHORITIES is the carrier and is read at every boot |
| rule 5 never charter a sole implementer | **DISTINGUISH** | unreachable as written: a lane is a bounded CLI process, so there is no charter to place a surrogate in. The property is satisfied structurally - any lane can be invoked at any time by anyone with the script |
| rule 6 prove delivery from file advancement | **ADOPT, already structural** | run receipts: `exitCode` is the truth, and a large `promptBytes` beside a tiny `outputBytes` is the documented signature of a prompt that never arrived |
| rule 7 alarm on entries/transitions RATIO | **ADOPT** | the cheapest leg and the one this board most needs; see the gap below |
| R1-A bounded boot, no whole-file read | **ADOPT, and it names an already-booked defect** | see below - this is the strongest leg of either document for this board |
| R1-B key placement vs measured darkness | **DISTINGUISH** | no keys and no seats to place; per-seat darkness is not a quantity this board has any more |
| R1-C refuse-on-ambiguity is a VERIFIER trait | **ADOPT** | the lane table already assigns `sol` (adversarial verifier) and `opus` (orchestrator) this way; R1-C supplies the REASON, which was previously only taste |
| "family is not the variable, seat contract is" | **DISTINGUISH - accepted as a mechanism, DECLINED as settled** | see the confound below |

### R1-A is the leg that names a defect this board had already booked and not fixed

Conjugal's R1-A says a seat payload must state derivation COMMANDS, never "read fully", because
ledger growth is unbounded and monotone, so a read-it-all instruction is correct the day it is
written and fatal some weeks later with no event in between. **MLV-App has two open queue items
that are this defect, booked independently and before reading R1-A:** `RESUME-COST-1` ("full
canonical re-derivation is charged at cold-start price on EVERY warm wake") and `RESUME-AUDIT-1`
("RESUME.md accumulates corrections faster than it receives them"). This board built the
mitigation - a 10-minute machine-written board snapshot - **and never fixed the underlying
instruction**, which still says derive everything at every boot. R1-A is adopted with
corroboration, and the corroboration is that we found the same shape from the cost side while
Conjugal found it from the context-budget side.

### The confound neither candidate can exclude, offered as a limit and not an objection

Both documents converge on *family is not the variable, seat contract is*, and the convergence is
genuinely strong: the two datasets are **oppositely signed**. Execute-posture measured a Codex
orchestrator stalling beside a running Claude hub; Conjugal measured the same stall with its Codex
lanes as the *healthiest* seats on the box. An explanation reducing to "that family was down" is
refuted by the pair.

**But all four boards named across the two documents share ONE operator, and three of them share
one machine.** Seat contracts are authored by that operator. So "seat contract, not family" and
"one author's charter-writing habits, not family" predict identical data, and nothing in either
document separates them. That is not a reason to reject the mechanism - this board adopts it - it
is a reason to refuse the word *settled*. **The discriminating experiment is a board on a
different operator's charter**, and until one exists the claim should be cited as
strongly-supported-and-unreplicated-across-operators. MLV-App's own spec already carries the same
warning about its own numbers under "Honest limits (n is small; do not cite this as settled)", and
applies it here to a conclusion that flatters this board rather than only to one that does not.

### DISTINGUISH on cause: MLV-App's stall was not a fixpoint

Recorded because a sibling reading the execute-posture table will see MLV-App as the healthy
control and may assume this board never stalled. It did, in July-August, and the mechanism was
different: **seat liveness plus per-slice authorization under a Claude hub** - lanes that were
"alive" because a registry file said so, and work that needed re-authorization per slice. Same
symptom (motion without closure), different disease. The remedy was also different and is the
2026-08-29 topology change: seats were abolished rather than repaired. A board matching MLV-App's
symptom should check which of the two diseases it has before applying either remedy, because the
fixpoint remedy (harness rules) and the seat-liveness remedy (delete the seat abstraction) do not
substitute for each other.

### The gap this board must close before it may claim rule 7

Rule 7 alarms on `ledger entries / state transitions`. MLV-App does not compute this ratio
anywhere. The board snapshot publishes both inputs already - queue state counts and lane receipts
- so the ratio is derivable and unwatched, which is the exact "capability with no caller" shape
this fleet keeps re-finding. **Booked, not claimed.**
