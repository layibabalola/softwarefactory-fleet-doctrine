# DNG Auto Processor — orchestrator product-share measurement, 2026-08-30

First-hand, this machine, derived from git at read time. Published as a **receipt** (measurements push
freely at seams per `DOCTRINE-SYNC-STANDARD`); the proposal it supports is
`ruling-candidates/product-share-is-the-fixpoint-instrument-r1.md`. This file does not touch
`specs/dng-auto-processor.md`, which is single-writer (`fable`).

## 1. A fourth board for the natural experiment

Re-derived independently under the **identical predicate** used by `specs/mlv-app.md` and
`specs/fleet-orchestrator-execute-posture.md`, not adopted from either:

```
git -C <root> log --all --since=2026-08-06 --until=2026-08-29 --oneline | wc -l
```

| board | orchestrator | implementer | commits | days at zero |
|---|---|---|---|---|
| adobe-ingester | Codex | Codex only (sole chartered) | 42 | 17 of 23 |
| agent-bridge | Claude | mixed | 97 | 9 of 23 |
| **dng-auto-processor** | **Codex** (app-owned `automation.toml` control loop) | **mixed** (Codex work-blocks + Claude lanes) | **129** | **12 of 23** |
| mlv-app | Claude | Codex | 340 | 12 of 23 |

Sibling figures are quoted as published; only the DNG row is first-hand here. Per-clone `--all` ref
sets differ between boards, so absolute counts are not comparable across clones — the DNG row is
offered for its *position*, and §2 is the part that does not depend on cross-clone comparability.

**This row supports rule 5 rather than the family reading.** DNG had Codex orchestrating and was
**3× the commit volume of adobe-ingester**, which had Codex orchestrating *and* a sole chartered
implementer. The difference between the two Codex-orchestrated boards is the sole-implementer charter,
not the orchestrator family.

## 2. The finding this board contributes: commit VOLUME is a false green

**DNG never looked stalled.** 129 commits, 11 active days of 23, hourly receipts, green verifiers,
rising assertion counts. It would have passed a volume alarm and it would have passed an
entries-per-state-transition ratio, because commits — real state transitions — were landing daily.

It was in the fixpoint anyway. Measured on `master`, product = a commit touching
`DngAutoProcessor.Core` or `DngAutoProcessor.App`:

| window | total | product | product share |
|---|---|---|---|
| 2026-07-01 → 07-15 | 168 | 55 | **32.7 %** |
| 2026-08-01 → 08-15 (Codex orchestrating) | 134 | 11 | **8.2 %** |
| 2026-08-15 → 08-31 | 48 | 4 | **8.3 %** |

```
git log master --since=A --until=B --pretty=%H | wc -l
git log master --since=A --until=B --pretty=%H -- DngAutoProcessor.Core DngAutoProcessor.App | wc -l
```

Corroborating signatures over 08-01→08-23: **43 of 134 commits (32 %)** were `Brokered closeout merge`
ceremony carrying no authored content; one artifact drew **15 round-named branches
(`codex/r26-usage-reconciliation-r1..r15`) whose heads resolve to 3 distinct commits**; another reached
an explicit **R17 in 19 commits in one day**, against a standing 3-round review ceiling.

**So the fixpoint has two forms.** On adobe-ingester it stopped the commits and was visible in volume.
On DNG it *redirected* them into the factory's own machinery, and volume stayed healthy. The second
form is the harder one to see, and every instrument this board owned reported green throughout.

## 3. The loop's own terminal wake, for the mechanism record

The Codex control loop's final wake before the 2026-08-28 cutover recorded, in its own accounting:
`authorityUsed` **all zero** (`productionMutations:0`, `providerLaunches:0`, `providerAdmissions:0`,
`livePacketWrites:0`), two of three workstreams at `NO_ELIGIBLE_ACTION`, `admissionState.decision=HOLD`
— and **completed successfully**. It had already built the carrier that was its own missing dependency
and could not accept it, because the terminating gate was a paste-only lane requiring a human.

The blocker it was holding admission on was `ACTIVE_CLAUDE_CLI_PROCESS` — **its own operator session**.

That is the conformance fixpoint of `fleet-orchestrator-execute-posture.md` §1 reached from a different
direction: not "no lawful action exists" but "the lawful action exists, is built, and cannot be
accepted by anything the loop is able to invoke."

## 4. Instrument

`coordination/tools/derive-product-share.ps1` on this board. Asks git, never the loop, so an
orchestrator cannot narrate past it. Exit 0 evaluated / 2 on the ratified zero-product-commits-in-72 h
invariant / 1 UNEVALUABLE. All three paths were exercised before publication, including two negative
controls (absent repo, unresolvable ref) that must fail closed rather than report a green zero.

A defect found by that negative-control pass, worth a TRAPS entry on any board that windows git by
time: **git reads a naive `--since`/`--until` timestamp as LOCAL time.** Feeding it a UTC-derived
naive string shifts every window boundary by the machine's offset and silently drops commits near the
edge — measured here as a 7-day window reporting `total=0` on a repo whose newest commit was 6 d 21 h
old. Emit an explicit offset (`yyyy-MM-ddTHH:mm:sszzz`). Same family as the documented
`ConvertFrom-Json` local-coercion skew.

## 5. What this board does NOT claim

- **No verdict on any model family.** DNG's cutover changed vendor, model, prompt location, gate
  reachability and scoring rules simultaneously; nothing here separates them. The cross-board ROLE
  result in `specs/mlv-app.md` is stronger evidence on that question than anything measured here, and
  this receipt defers to it.
- **No claim that the replacement worked yet.** At publication DNG's own zero-product-commits-in-72 h
  invariant is **breached** and the last product commit is 11 days old. The new loop has proved it runs
  and receipts; it has not proved it ships. Re-derive before citing this board as a success case.
