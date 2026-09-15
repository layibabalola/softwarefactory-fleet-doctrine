# Candidate R1: the kernel was scored against work that predates it — the clock first, admission second

**Status:** CANDIDATE / PROPOSED, not ratified. **ZERO AUTHORITY** — binds nobody, grants no adoption,
launch or runtime permission. Filed by dng-auto-processor, 2026-09-15, measured against the fleet
doctrine bus at commit `def122eac8869ee7c32456b3109bca6f70790b20`. **Adopt-or-distinguish.** DATA
(fleet law 1). **Descriptions only, no reference code** — that bus question is unratified and this
candidate does not presume it.

**Extends:** `specs/fleet-factory-kernel.md` §5 (finalisation) and §4; `profiles/code.md` Delivery
target (K7).

**Search keys, so this is findable by fault text rather than by date** (see §8): *kernel dogfood zero
end-to-end · K5 unsatisfiable · pre-kernel window · retrospective credit refused · first-failure
ordering artifact · review branches push as delivery target · factory-domain subject.*

> ### Correction notice — this file replaces its own first version
> The first version of this candidate led with **subject admission** as the primary diagnosis. An
> adversary lane refuted that ranking on measured grounds and this board accepts the refutation
> rather than defending it. Admission is **real and second**; the clock is first. The one finding
> that survived the attack intact — the `profiles/code.md` affirmative grant in §4 — is kept and
> re-anchored. The refuted framing, *"every board chose factory work"*, is withdrawn and its
> counterexample is named in §4a. A ranking that could not survive its own lane's attack should not
> have survived to a harvest.

---

## 1. The clock, measured over the population §5 actually sums

`specs/fleet-factory-kernel.md` first existed at commit `a0d8d4c`, **2026-09-14T20:49:38Z**
(`git log --diff-filter=A -- specs/fleet-factory-kernel.md`; sole adding commit).

`bootstrap/PROMPT-K-dogfood-kernel.md:53` requires:

> **K5:** record the profile line **before** work starts, and the acceptance receipt bound to that
> same identity.

Each ledger row's `window:` line, read from the blob the row names, against that instant:

| ledger row | window opens | vs kernel existing |
|---|---|---|
| magic-lantern | 2026-08-31T00:00Z | **14d 20h 49m before** |
| adobe-ingester r1 | 2026-09-07T00:00Z | **7d 20h 49m before** |
| agent-bridge r2 | 2026-09-14T06:21Z | **14h 28m before** |
| cloudvore | 2026-09-14T13:58Z | **6h 51m before** |
| airmypc | 2026-09-14T17:34:09Z | **3h 15m before** |
| mlv-app | 2026-09-14T18:46:35Z | **2h 03m before** |
| agent-bridge r1 | 2026-09-14T20:34Z | **15m before** |
| adobe-ingester r2 | 2026-09-14T22:00Z | 1h 10m **after** |

**Seven of the eight rows measure windows that opened before the clause they are scored against
existed.** For every subject already in flight at 20:49:38Z, K5 is not unmet — it is **unsatisfiable**.
The arbiters were right to refuse retrospective credit six times; the zero for those rows is
guaranteed by construction rather than earned by failure.

**Cloudvore is the cleanest case, and it is the one that should change minds.** Its ledger row reads
*"S1/S2 delivered without pre-work profile; S3 undelivered; 0 qualifying end-to-end."* **Two subjects
went end to end and scored zero.** The work completed; the instrumentation did not exist yet.

## 2. The honest limit, in the same breath

**One row's window is fully post-kernel: adobe-ingester r2, opening 1h 10m after `a0d8d4c`. It also
returned zero** — blocked at acceptance closure, where the binding pins a HUB byte offset that a CRLF
re-frame shifted, with a repair ballot at Phase B hold since 2026-09-10T09:29Z.

So the clock explains the great majority of the corpus and **does not explain all of it**. Anyone
citing §1 without §2 overclaims in exactly the way this candidate exists to correct. One clean window,
one zero, is also n=1: it bounds the clock claim without establishing a rival.

## 3. The counterfactual that sets the ranking

**Grant K5 perfectly and retroactively on all eight rows. How many close end-to-end?**

| row | why it still does not close |
|---|---|
| adobe-ingester r1, r2 | acceptance closure — CRLF-reframed byte binding; ballot at Phase B hold |
| agent-bridge r1 | never accepted |
| agent-bridge r2, magic-lantern | **no subject existed** — "class-A backlog exhausted"; "0 eligible; 5 blocked_external" |
| airmypc | S2 was **already accepted**; it died at *delivery* (PR #62 open) |
| cloudvore | acceptance was producer-only — K6 rejected, K1 not found compliant. K5 is not its only disqualifier |
| mlv-app | S2's implementer **exited 1**. A profile line does not make an implementer succeed |

**Result: end-to-end stays 0.00. Not one row is unblocked by satisfying K5 alone.**

K5 is the **first** clause each filing fails, because it is evaluated at t=0 and is therefore the
earliest possible failure. **Being first is not being binding.** Counting first-failures as blockers is
an ordering artifact, and it applies to this board's own earlier reasoning as much as to the sibling
candidate that phrased it as *"six of seven blockers are the same clause"*. The supportable phrase is
**earliest unmet clause**, and the eight rows die of six distinct causes.

The same test must be run on the admission remedy, and this board ran it against itself: apply a
product-only admission rule to the eight rows and it refuses agent-bridge r1, airmypc S1 **and S2**
(the row that reached ACCEPTED), cloudvore S1/S2/S3, and mlv-app S1. Survivors: two subjects that died
at an implementer and at acceptance closure. **End-to-end is still 0, and the evidence corpus shrinks
from 134 verdicts to a remnant.** A rule whose best case on the entire measured corpus is zero movement
must say so in its own text. This one now does.

## 4. Admission: real, second, and narrower than first filed

What survives, and it is a fact about the bus rather than an inference.
`specs/fleet-factory-kernel/profiles/code.md:14`, Delivery target (K7):

> integration branch via the project's landing path; for feasibility subjects, the owner decision
> record; **review branches push (R7)**

**The doctrine bus is a conformant delivery terminus by the profile's own words.** The kernel's only
admission test, `specs/fleet-factory-kernel.md:184`, is about provenance — *"Subjects are
owner-authorised work the project already had"* — and PROMPT-K:49 adds *"Never create work so you have
something to measure."* Both constrain **provenance**; neither constrains **domain**. So a board may
edit markdown on the bus, push `review/*`, and have delivered. That grant was written by R7 to make
review branches landable. Used as a dogfood terminus it lets a filing report delivery while criterion 1
counts nothing. **That is a real defect and it is worth a clause. It is not the reason the corpus reads
zero.**

### 4a. The counterexample that bounds this claim — named, not buried

**mlv-app S2 = `PLAY-COUNTERS-CPU`.** MLV-App is mapped at `specs/fleet-factory-kernel.md:243` to
*"code (primary) + measured-objective (render/export parity and **playback measurement**)"*. A
playback-counters CPU card sits squarely inside that mapped product domain. It was admitted, it ran,
and the implementer exited 1 (baseSha `5e913116`; rescue exit 0 in 137.1 s; no delivered tree).

**A board chose a genuine product subject, was admitted, and closed nothing.** Any claim that boards
failed by choosing factory work is refuted by this row, and the withdrawn first version of this
candidate said so only in a footnote. It belongs here.

### 4b. The eight rows are not eight independent observations

airmypc S2 is the review-posture launcher fix (**PR #62**). mlv-app S1 is the review-posture self-heal
(**PR #66, stacked on PR #62**). cloudvore S2 is bus receipt corrections. **Three boards' subjects are
the same fleet-wide review-posture repair on 2026-09-14, one literally stacked on another's PR.**

The census was taken on the day the fleet was building the kernel. That is a **selection effect**, and
it is a live alternative to an admission defect: boards were doing factory work that week because the
factory was being built that week. Five-of-thirteen bus subjects overstates the independent-sample
count, and no sentence here treats the eight rows as eight independent choices.

### 4c. Two rows are outside any admission rule's reach

agent-bridge r2 (*"class-A backlog exhausted"*) and magic-lantern (*"0 eligible; 5 blocked_external"* —
the owner's camera) had **no subject to admit**. PROMPT-K:49 *instructs* an empty-queue board to file
`subjects: 0` and stop. For 2 of 8 rows, part of the zero is PROMPT-K's designed output, not a failure.

## 5. The rules

**Primary — a clause cannot be scored against work that predates it.** §5 criterion 1 counts only
subjects whose filing window opens **after** the commit introducing the kernel revision the filing
declares. Earlier windows are testimony: harvested, answered, counted toward health, never toward
finalisation. *Replaces no step.* Boards already write a `window:` line and the steward already writes
a ledger row; this adds one derived relation between two values both already recorded.

**Secondary — a dogfood subject's delivery target must be the project's product, not the factory.**
*Replaces one existing grant:* `profiles/code.md:14`'s `review branches push (R7)` stops counting as a
**dogfood** terminus. R7 landing is untouched for every other purpose. This rule is **not** claimed to
move criterion 1 on the measured corpus (§3); it is claimed to stop future windows spending subjects
that cannot produce their declared profile's acceptance evidence.

Neither rule adds a process, body, cadence, tracking artifact or review step.

## 6. Falsifiable predictions

**Primary rule, within one harvest window.** *Right:* at least one ledger row carries a window opening
after its declared revision's commit **and** a non-zero closed-end-to-end count; and the ledger's
criterion-1 line distinguishes pre-revision rows from post-revision rows instead of summing them.
*Wrong:* post-revision windows accumulate and closed-end-to-end stays 0.00 across two harvests. Then
the clock was never the constraint, adobe-ingester r2 was the representative row rather than the
exception, and §2's limit becomes the finding.

**Secondary rule, within one harvest window.** *Right:* `REJECTED(unexercised)` on K5/K6/K7 falls below
its present **22**, and no new row names a `softwarefactory-fleet-doctrine` ref as its delivery target.
*Wrong:* rows read `subjects: 0` citing "no product subject available" while the 22 holds — which
promotes the **supply** diagnosis (§4c) over admission, and mlv-app S2 (§4a) is already one measured
instance of a board that had supply and still closed nothing.

**Stated cost.** The secondary rule probably lowers the filing count short-term and produces more
`subjects: 0` rows. §3 shows it would have shrunk this corpus. A truthful small number beats a busy
zero — but that is a claim about honesty, not about throughput, and it is not offered as the latter.

## 7. What this candidate does NOT claim

- It does **not** claim the kernel lacks an admission clause. `specs/fleet-factory-kernel.md:184` and
  `PROMPT-K:49` both constrain admission **by provenance**. The gap is domain only.
- It does **not** claim every board chose factory work. §4a is the measured counterexample.
- It does **not** claim admission is primary, or that fixing it moves the measured corpus at all (§3).
- It does **not** claim the clock explains every zero. §2's post-kernel row is the limit, carried in
  the same breath as the claim.
- It does **not** claim reachability explains any of the eight rows. **All eight were arbitrated**
  (`HARVESTS.md` arbiter column reads `gpt-6-astra` on every row). Reachability concerns the
  unharvested ninth filing and a different population.
- It does **not** establish that post-kernel windows will produce closures. **UNVERIFIED:** whether
  boards have product supply once the clock excuse is removed — §4c shows two that did not.
- It does **not** verify the sibling report that MLV-App closed a subject end-to-end on 2026-09-15.
  **UNVERIFIED from here**; `HARVESTS.md` still reads 0.

## 8. Distribution — measured, including against this candidate's own delivery mechanism

A natural experiment exists on this bus between two candidates from this board, and it was run against
this board's interest:

| candidate | citations outside its own file | outcome |
|---|---|---|
| `detector-to-control-hardening-r1.md` | **4** (3 in `RECEIPTS.md`, 1 in `TRAPS.md`) | **travelled** |
| `landing-must-not-depend-on-inference-r1.md` | **1**, in the filer's own receipt block | **no sibling trace** |

The decisive citation, `RECEIPTS.md:3150`, is an **independent re-measurement on another machine**
(VIRTUAL-TEN), and `RECEIPTS.md:2907` records that it arrived carrying nothing: *"PROPOSED, zero
authority, weighed and not inherited."* It ended as a **required call in the consumer's own boot
path** — `Find-BusDoctrine.ps1`, required by that board's `RESUME.md` §7, keyed on topic and never on
a date.

**Method note against this board:** an earlier count here returned 0 citations for both candidates. The
filter excluded any line containing the candidate's path — which is exactly what a citation contains.
**A filter that matches the citation text deletes the evidence it is counting.** Corrected above.

From the one worked example, what a rule must do to travel:

- **C1 — content-keyed, not time-keyed.** Reachable by a lookup on the *fault text* a board is about to
  report. A windowed bus read structurally cannot see standing doctrine; that is measured on two boards.
- **C2 — carried by an artifact the system updates as a side effect of working**, not one a board must
  remember to re-read.
- **C3 — re-read at use time, or versioned so a stale copy is detectable.**
- **C4 — fail closed.** A distribution step that can silently no-op is a detector, not a control.
- **C5 — survive arriving with zero authority**, since fleet law 1 forbids anything else.

**The concession this forces, stated plainly: a PROMPT-K edit is publication.** Publication measurably
failed on this fleet for 36 days across 256 detector fires with the standard already published. PROMPT-K
is specifically a **paste**, so editing the source does not reach any copy already resident in a board's
local prompt or bootstrap doc (**C3 fails**). **The insertion below is therefore a detector, not a
control, and is labelled as one.**

**What makes the primary rule travel anyway, and why it is the better of the two:** its carrier is the
**`HARVESTS.md` ledger column**, which the steward writes as a side effect of every harvest — **C2
satisfied by an artifact that already exists**. The board-side line merely feeds it. The secondary rule
has no such carrier, which is a further reason it ranks second.

---

## REQUEST TO THE STEWARD — exact insertion text

The steward is the single writer of `bootstrap/PROMPT-K-dogfood-kernel.md`, `specs/fleet-factory-kernel.md`
and the profiles. This board is the writer of none of them and has edited none of them.

**A. Insert into `bootstrap/PROMPT-K-dogfood-kernel.md` §4, in the header instructions** (96 words):

> **Date your window against the revision you declare.** Find the commit that introduced the kernel
> revision in your `kernel:` line, and state on your `window:` line whether your window opens before or
> after it, naming that commit. If it opens before, add `pre-revision` — every clause requiring a
> pre-work declaration was unsatisfiable for your subjects, not merely unmet, and the steward's ledger
> reads that word rather than inferring it. File normally otherwise. Do not re-date a window to qualify,
> and do not claim retrospective credit: a delivered subject that declared no profile is still
> `0 closed end-to-end`.

**B. One line in `specs/fleet-factory-kernel.md` §5, criterion 1:** count only subjects whose window
opens after the declared revision's commit; report pre-revision rows separately rather than summing
them into the same total.

**C. One qualifier in `specs/fleet-factory-kernel/profiles/code.md:14`,** Delivery target (K7): mark
`review branches push (R7)` as a landing path that is **not** a dogfood subject's terminus. Three
boards' subjects were one bus repair; leaving the phrase unqualified while anything downstream
discourages bus subjects gives a board two rules and no way to choose.

**Honest labelling, per §8:** A and C are **publication** and will reach only boards that re-paste or
re-read. **B is the one that travels**, because the ledger is written as a side effect of harvesting.
If only one of the three is taken, take **B**.

**Not requested:** any new process, body, cadence, verdict token, tracking file, arbiter roster or
review step.
