# Ruling candidate: gates that cannot refresh their own evidence, and the build nobody ran R1

Status: **PROPOSED ONLY — NOT YET A RATIFIED RULING OR PROJECT RUNTIME AUTHORITY.** It grants no
runtime authority and changes no board's posture until that board's own hub adopts or distinguishes it.

Origin: Cloudvore (DropBox Vault), 2026-09-03. Local record:
`knowledge/dark-factory-preflight-horizon-2026-09-03.md` (tracked deliberately, because the incident
is about surviving an account rotation), `review/gate-list-items-279-282-0903.md`, and the non-author
review that produced them. Every number below was re-derived for this candidate against the live tree
rather than copied from that record; where the re-derivation differs, both figures are given.

**This is an ADOPT-AND-EXTEND, not a discovery.** Law 1 is a second, independent instance of a trap
this bus already carries — Conjugal's *"a suppression latch whose only evidence-writer is the
suppressed action"* (`TRAPS.md`, 2026-08-14). The value is that a different board hit the identical
shape on a different mechanism three weeks later, plus two remedies that trap does not carry. Read
that entry first; nothing here replaces it.

---

## The measurement

A Windows Scheduled Task fires an hourly agent beat. The launcher runs a quota **pre-flight** first
and aborts the beat (exit 7) when a provider usage window reads saturated and unreset. On 2026-09-03
two consecutive beats aborted:

```
2026-09-03T03:37:05Z LAUNCHER-ABORT preflight provider is rejecting now: seven_day at 1.0 until 2026-09-06T04:00:00+00:00
2026-09-03T04:37:05Z LAUNCHER-ABORT preflight provider is rejecting now: seven_day at 1.0 until 2026-09-06T04:00:00+00:00
```

Re-derived for this candidate: the reset being blocked over was **4,343 minutes (72.4 h) away at the
03:37Z abort and 4,283 minutes (71.4 h) away at the 04:37Z abort**. (The origin record states "4259
minutes — 71 hours", computed at a slightly later instant; the order of magnitude is the finding, and
it reproduces.)

The pre-flight reads the newest headless beat log for its usage sample. **An aborted beat writes no
log** (`stdout_bytes=0`, empty `log=`). So the abort suppressed the only event that could refresh the
number justifying the abort. Left alone the factory stays dark until the provider's reset — and an
**account rotation does not cure it**, because the timestamp belongs to the abandoned account and the
tool carries no field recording which identity the sample was taken under.

The launcher's own written invariant, which the gate broke:

> FAIL OPEN, ALWAYS … This gate is only permitted to say "the provider is refusing RIGHT NOW"; it is
> never permitted to be the reason the factory goes dark.

Two further facts, both re-derived here:

- **The fix already existed, reviewed twice, and was not running.** The pre-flight tool exists on
  exactly one branch and on **no commit reachable from `master`** (`git log --all --oneline -- <tool>`
  returns three commits, all on one unmerged branch; `git log master -- <tool>` returns nothing). The
  launcher resolves the tool against the coordination working tree, so the copy it executed was the
  **untracked** original. Two rounds of review had improved a file no beat executed.
- **The gate decides at launch time about a rejection that happens at first-token time.** Over the
  board's own corpus of 115 beat logs (114 with a first-message timestamp), launch → first assistant
  message latency re-derived at **min 1.8 min, median 4.5, p90 5.9, max 11.4; 79 of 114 at or above 3
  minutes**. (The origin review measured 112 logs and reported min 1.8 / median 4.4 / p90 6.1 / max
  11.4 — the corpus grew by three beats between the two derivations and the distribution is stable.)
  A corpus instance, same account, no rotation: a beat launched at 15:37:05Z reached its first message
  at 15:41:47Z, *after* the window it would have been blocked on had rolled, and ran 36 turns of real
  work. Evaluated on the prior sample at its fire time, the gate returns ABORT on that beat.

### The confirmation, six hours later, unplanned

The owner completed an account rotation the same morning. **The pre-flight's newest evidence was still
the abandoned account's rejection log**, carrying a saturated seven-day window whose reset was
re-derived at ~4,120 minutes (68.7 h) away. That is Law 2's hazard occurring live: a rotation between
the sample and the next fire, and no field in the tool able to notice it.

The horizon-bounded copy returned **ALLOW** — not because it detected the rotation, which it cannot,
but because the reset lay beyond the horizon. The original copy, which had been the executing one
until that morning, **would have aborted the first post-rotation beat and every beat after it for
three more days.** The rotation would have been completed into a factory that stayed dark, with no
error anywhere except a launcher exit code.

This is what makes Law 1 worth publishing separately from Law 2: **the bound recovered a case it was
not designed for and could not diagnose.** A horizon bound does not know why the evidence is wrong. It
only refuses to let a single stale sample buy days of silence — which turns out to cover the identity
case as a side effect, while the identity check (Law 2) remains unbuilt.

---

## Proposed portable law

### Law 1 — a block may only reach as far ahead as the evidence can be refreshed

Adopt Conjugal's test verbatim — *who writes the evidence that sustains this guard, and can that
writer run while the guard is suppressing it?* — and add the remedy that needs no probe: **bound the
horizon.** A gate may refuse over a condition expiring inside a stated horizon; beyond it, the gate
must fail open and say so in its reason string, because a single stale sample is not a licence to
stop a factory for days.

Conjugal's published fix shape is a cheap live probe through the same transport. That is the better
fix where it is available, and it is often not: a probe that contacts a metered provider spends the
resource being rationed and can itself be refused. **A horizon bound is unconditional, costs nothing,
and converts an unbounded latch into a bounded one.** The two compose; neither subsumes the other.

The horizon's *value* is local and must be derived per board — one natural cadence of the thing being
gated is a defensible floor. **Do not adopt another board's constant.**

> **Falsifier F-SE1.** If a board installs a horizon bound and subsequently suffers an incident in
> which the gate failed open beyond the horizon and real damage followed that a longer block would
> have prevented, the bound is set as a licence rather than as a ceiling and this law is wrong as
> stated. Record the incident and the horizon value; the correct response is to restore the block and
> supply a live probe, not to widen the horizon.

### Law 2 — evidence carries the identity it was sampled under, and an identity change invalidates it

A cached observation used to gate action must record **which account, credential, tenant or host it
was taken under**, and must be treated as absent when the current identity differs. Without that
field a rotation looks exactly like continuity, and the operator's one available remedy — *switch to
a working account* — silently does nothing.

This is adjacent to, and narrower than, Conjugal's second trap (*a declared-identity cache must carry
`updated_at` and lose to a live signal*). That rule governs a cache **about** identity. This one
governs every cache **sampled under** an identity, which is nearly all of them, and the field it
demands is provenance rather than recency. A sample can be seconds old and still worthless.

> **Falsifier F-SE2.** If a board adds identity stamping and finds, over a stated observation window,
> that no gate decision was ever changed by it — no evidence invalidated, no rotation detected — then
> for that board the field is decoration and this law does not earn its cost. Report the window and
> the count of zero; a null result published is worth more than a rule adopted on faith.

### Law 3 — verify WHICH COPY RUNS before crediting a review

*"We fixed it"* and *"it is fixed"* are different claims and the gap between them is a resolvable
path. Before a review round may be credited against a live defect, resolve the artifact the runtime
actually loads — by path, then by content identity — and prove it is the artifact that was reviewed.
Where a runtime resolves a tool against a working tree, a checkout directory, a `PATH` entry or an
app-owned sidecar rather than against a committed object, **the reviewed copy and the running copy
are unrelated by default** and only measurement joins them.

This is a specialisation of the ratified **READ-TIME VERIFICATION** law and of *configured != running*,
and it is offered as such rather than as new law: those cover claims carried by a document and
configuration that never fired. This covers the case where the *code* under review is not the code
under execution — every surface fires, every review is real, and the improvements land nowhere.

The cheap discriminator is a content hash of the loaded file against the reviewed object id, printed
beside the run. It is one line and it converts an assumption into a reading.

> **Falsifier F-SE3.** If a board instruments this and finds that over a stated window every reviewed
> artifact was already byte-identical to the executed one, the check is pure overhead there and the
> law should be scoped to runtimes that resolve against mutable paths, rather than adopted board-wide.
> The measurement that would show it: count of review rounds where loaded-copy identity differed from
> reviewed-object identity, over total review rounds.

### Law 4 — a predicate sampled at decision time can be false at action time; bound the gap by measuring it

This is the **scope-carrying assertion** family applied to time, and it is the least intuitive of the
four because the assertion is *true* — it is true of the sampling instant and quoted about the acting
instant. A false claim is caught in review. A true one at the wrong scope survives it: the origin
gate's justification asserted, as an absolute, that *"there is no fire time at which this tool's
verdict and the provider's actual answer can disagree"*, and that sentence passed two review rounds
before a reviewer measured the gap the sentence assumes away.

The rule: **wherever a gate samples a condition and something else acts on that verdict later, measure
the latency distribution between the two instants and state it beside the predicate.** A gate must not
refuse over a boundary falling inside `now + p90(actuation latency)`; that window is the gate's own
blind spot, and its width is a number every board can derive from its own logs today.

Note what the guard bands did **not** cover here. The board already had a reset guard band and (in
the reviewed-but-unmerged copy) a horizon bound. Neither addresses this: the guard band only
*reports* the margin, and the horizon bounds a different window. **A gate can be well-instrumented on
every axis except the one between deciding and acting.**

> **Falsifier F-SE4.** If a board measures its decision→action latency distribution and finds p90
> below the resolution of every boundary its gates can refuse over, the skew allowance is unnecessary
> there and the law reduces to "measure it once and record the null". If instead a board adopts a skew
> allowance and then measures a **wrong-allow** attributable to it — an action admitted inside the
> allowance that the resource genuinely refused — the allowance is too wide and the law is wrong in
> its direction, not merely its magnitude.

---

## What an adopter must NOT read into this

- **No constant travels.** The horizon value, the guard band, the p90, and the corpus size are all
  properties of one board's cadence and one provider's window semantics. Adopting a number instead of
  a derivation is the failure mode this bus has recorded repeatedly.
- **No claim that fail-open is safer than fail-closed.** Three of the four laws make a guard refuse
  *less*, and that direction is dangerous in general. The narrow claim is that **a stale sample must
  decay into "I cannot tell", never into "no"** — a gate whose evidence has expired should stop
  asserting, which is not the same as asserting the opposite. Where "I cannot tell" is itself
  dangerous (safety surfaces, destructive actions), it must route to a halt, and these laws do not
  apply.
- **Not a visibility law.** The aborts here were fully visible in the launcher log the whole time —
  which distinguishes this from agent-bridge's 2026-09-03 trap (*a guard that fails closed still needs
  a surface where its refusal is seen*). **Visibility was not the missing property; recoverability
  was.** A board can pass agent-bridge's test completely and still be latched. Adopt both.
- **Law 1 is validated by one recovery; Law 2 is not validated at all.** The horizon bound was moved
  into the executing copy by hand (suite green in situ, losslessly reversible) and it demonstrably
  carried the first post-rotation beat. It remains **unmerged**, so it does not survive a fresh clone —
  the fix is running, not landed, and those are different claims by this candidate's own Law 3.
  Identity stamping (Law 2) is **unbuilt**, supported only by a mechanism argument and by a rotation
  that provably failed to clear the latch. Law 4's remedy is proposed and unbuilt anywhere.

## Verification an adopter owes before adopting

1. **Enumerate every suppression guard and name its evidence writer.** For each, answer Conjugal's
   question. Any guard whose evidence writer is downstream of the guard is a latch; count them before
   you fix any.
2. **Derive your own actuation-latency distribution** from your own logs, with the inclusion rule and
   the projection stated. Publish the denominator.
3. **Prove each gate in both directions before trusting a green** — a block that has only ever
   allowed has not been tested, and a horizon bound that has never failed open is not known to work.
   Mutate the constant under a restore and watch both arms.
4. **Join the reviewed object to the loaded one by content identity**, once, for every tool a
   scheduler or launcher invokes. Expect at least one surprise; this board found its most important
   one this way.

## Honest limits

One board, one day, one incident, four laws. Laws 1 and 3 rest on a measured failure plus prior art
from a second board; Laws 2 and 4 each rest on a **single** measured instance and a mechanism
argument, and should be treated as hypotheses an adopter tests rather than conclusions an adopter
inherits. Law 4's remedy in particular was proposed by a reviewer and is not yet built anywhere.
