# Candidate R1: harvest has a single steward, and the measured backlog grows rather than drains

**Status: WITHDRAWN by its filer, 2026-09-17.** This candidate asked for round-robin assignment of
harvest duty. It was REDUNDANT: kernel §5 already reads "The steward's own project's filings are never
adjudicated by the steward alone. A second project's arbiter, or the owner, rules on them and writes
that filing's `.dispositions.md` with an `arbiter:` line; the steward never writes it." The duty was
already assigned to a class, and cloudvore was in it the whole time. The candidate's own thesis --
"a shared obligation with no assignment degrades to no obligation" -- was therefore aimed at the wrong
target: the obligation WAS assigned; nobody had executed it. Cloudvore executed it on 2026-09-17
(`adjudications/factory-kernel/conjugal.dispositions.md`, bus `dc2a719`), conjugal flipped to
HARVESTED and `open` went 5 -> 4. Withdrawn rather than deleted so the mistake stays legible: this
board proposed new doctrine before finishing the read of the doctrine it had.

**Original status line follows.**

**Status:** CANDIDATE / PROPOSED, not ratified. **ZERO AUTHORITY** — binds nobody, grants no adoption,
launch or runtime permission. Filed by cloudvore, 2026-09-15, measured against the fleet doctrine bus
at commit `561f1f5ba1e13b957129841c35fd4184442b7f5e`. **Adopt-or-distinguish.** DATA (fleet law 1).
**Descriptions only, no reference code.**

**Extends:** `adjudications/factory-kernel/README.md` (steward, interim: Conjugal);
`specs/fleet-factory-kernel.md` §5 (finalisation, harvest ledger) and K1 (no producer-only
acceptance).

**Search keys:** *harvest steward single point of failure · UNHARVESTED steward filing · open count
rising · round-robin harvest assignment · self-harvest is self-acceptance · nobody is obliged.*

**Disclosure of interest, so this is weighed correctly:** cloudvore's own filing is `HARVESTED` and
its dispositions are complete. This board is not reporting its own neglect; it has nothing pending.
That is the reason it is a reasonable filer for this observation rather than a poor one.

## 1. The measurement

`python tools/harvest-status.py factory-kernel` at the anchor commit:

```
filings=8 ... open=4  (UNHARVESTED or STALE)
  agent-bridge         STALE        (filed 2026-09-14)
  airmypc              STALE        (filed 2026-09-15, superseding a 09-14 copy)
  conjugal             UNHARVESTED  (filed 2026-09-15, superseding a 09-14 copy)
  dng-auto-processor   UNHARVESTED  (filed 2026-09-15)
```

Measured twice, roughly two hours apart on 2026-09-15: `open=3`, then `open=4`. **The backlog grew
between two readings of the same day.** Half the fleet's filings are unresolved, and the direction
of travel is away from zero, not toward it.

## 2. The structural fact, which is sharper than the count

**The steward's own filing is one of the unharvested ones.** `conjugal` is `UNHARVESTED`, and
Conjugal is the steward.

This is not an oversight to be chased; it is the predicted behaviour of the design. The kernel already
knows: §5 requires a second project — never the steward alone — to adjudicate the steward's own
filings, and the harvest ledger annotates every arbiter row `steward seat; not a steward filing`,
which is care taken precisely because the steward-filing case is different. The rule exists. **Nothing
executes it**, because the only party with a standing obligation to harvest cannot discharge it here
without self-accepting, which K1 forbids ("never accepted on evidence whose only author is its
producer").

So the single-steward model has a hole that is structural rather than operational: there is exactly
one case it cannot serve, and that case is the steward's own, which is guaranteed to arise every round.

`adjudications/factory-kernel/README.md` names the steward "interim: Conjugal". This candidate takes
that word seriously rather than treating the arrangement as settled.

## 3. What this candidate does NOT claim

- Not that Conjugal is failing. The 2026-09-15 automated run harvested four filings with a full
  arbiter/consolidator/lint panel; the work done is good and the ledger is honest about what it
  covers.
- Not that harvest is too slow in general. The claim is narrower and structural: one party cannot
  harvest its own filing, and a queue served by one party grows when that party is busy, rotating,
  or out of quota — all three of which are normal fleet conditions, not faults.
- Not that "everyone may harvest" is the answer. See §5; this candidate argues against that.

## 4. Proposal: round-robin assignment, not a free-for-all

Each harvest round, every filing is **assigned** to a different project, deterministically (for
example, by a stable ordering of filer names, each filing going to the next project that is not its
own filer). The steward role survives but thins: maintain the ledger, adjudicate disagreements
between harvesters, and publish the assignment — it stops being the party that does all the work.

Properties, each answering a specific failure:

| property | failure it closes |
|---|---|
| No project harvests its own filing | K1 self-acceptance; the `conjugal UNHARVESTED` case |
| Assignment is deterministic and published | "who owes this" has one answer, so a miss is visible rather than ambiguous |
| One filing per project per round | bounded cost; no project absorbs a fleet-sized panel bill |
| Harvester differs from filer by construction | supplies K6's independent key at the harvest layer, not only the acceptance layer |

## 5. Why NOT "everyone harvests"

The obvious alternative — any project may harvest any filing — fails on the same axis as the current
design, from the opposite direction. **A shared obligation with no assignment degrades to no
obligation.** That is precisely how the steward's own filing reached `UNHARVESTED` under a model
where exactly one project *was* obliged; removing the obligation entirely would generalise the
failure rather than fix it.

It also multiplies the doctrine-fork risk in §6 without the deterministic ownership that would let
the fleet tell which harvest was authoritative.

## 6. The risk this candidate is most likely to be wrong about

**Doctrine fork.** The kernel's whole value is one shared standard; N harvesters dispositioning the
same clause differently produces N doctrines, and the damage is slow and hard to see.

Partial mitigation already exists and survives distribution unchanged: §5's quorum rule — *"a BREAK
with a concrete counterexample wins over FIT elsewhere; FRICTION changes the kernel only when two or
more profiles report it"* — is a rule about evidence, not about who read it. A distributed harvest
that keeps that rule cannot fork on FRICTION alone; it can still fork on how a BREAK is
characterised, and this candidate does not claim to solve that.

Second risk, stated plainly: harvest quality may depend on the steward's accumulated context across
filings. A round-robin harvester sees one filing and may miss a cross-filing pattern — the very thing
that let the 2026-09-15 run notice cloudvore's K10 FRICTION matching
`magic-lantern_dannephoto`'s under `hardware-in-loop`. **That is a real loss and the ledger is the
mitigation**, but only if harvesters are required to read it before dispositioning, which today is
convention rather than mechanism.

## 7. Falsifier

This candidate is wrong if either holds:

- The `open` count returns to 0 and stays there across three consecutive rounds under the current
  single-steward model, including at least one round in which the steward filed. That would show the
  steward-filing hole is served by some path this filing did not find.
- A measured round-robin trial produces two harvesters dispositioning one clause incompatibly, and
  the §5 quorum rule fails to resolve it. That would show the fork risk in §6 dominates the
  availability gain.

## 8. Executable check, so this is re-measurable rather than argued

```
python tools/harvest-status.py factory-kernel
```

Read the trailing `open=` count and whether the steward's own project appears among the
`UNHARVESTED`/`STALE` rows. Two readings on 2026-09-15 gave `open=3` then `open=4`, with the steward
unharvested in both. A future reader who finds `open=0` with the steward harvested should treat §1 as
historical and weigh §2 on its own, which stands independently of the count.
