# Factory-kernel harvest ledger (steward-written, append-only)

One row per filing per harvest. `specs/fleet-factory-kernel.md` §5 reads this ledger, never a single filing, to decide
finalisation. Verdict counts use FIT/FRICTION/BREAK/N/A/UNEXERCISED.

| date | harvest | filing | blob | kernel | profile | subjects | FIT | FRICTION | BREAK | N/A | UNEXERCISED | unresolved BREAKs | arbiter |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-14 | 20260914T221904Z-51d5a96b | adobe-ingester | 7f1aea3bb5af6188556895c4c86a2c70c0c3a6e4 | r1 (text at 45f4a2c; now r2) | code@r1 (now r2) | 0 end-to-end (1 blocked at acceptance closure) | 8 | 8 | 1 | 0 | 0 | 0 (K12 BREAK adopted into §3) | gpt-6-astra (steward seat; not a steward filing) |
| 2026-09-14 | 20260914T221904Z-51d5a96b | agent-bridge | cc45e75f42af2f371bd18eb1f9bcbcef5718926e | r1 (now r2) | code@r1 (now r2) | 0 end-to-end (1 review run, not closed) | 3 | 9 | 0 | 0 | 3 | 0 | gpt-6-astra (steward seat; not a steward filing) |
| 2026-09-15 | 20260915T051905Z-86585ba5 | adobe-ingester | d7c91f3322a6c9cd856a380be32d831e1fd2416f | r2 (now r3) | code@r2 (now r3) | 0 end-to-end; 1 blocked at acceptance closure | 13 | 2 | 0 | 0 | 1 | 0 | gpt-6-astra (steward seat; not a steward filing) |
| 2026-09-15 | 20260915T051905Z-86585ba5 | agent-bridge | 80bb4d1dc9e14b9f3b08c61b443796c0d8a7db36 | r2 (now r3) | code@r2 (now r3) | 0 end-to-end; 4 observed-retrospective | 5 | 8 | 0 | 0 | 4 | 0 | gpt-6-astra (steward seat; not a steward filing) |
| 2026-09-15 | 20260915T051905Z-86585ba5 | airmypc | 2c919858144ac52318c05ffd02ba8ac5006fc0da | r1 (now r3) | code@r1 (now r3); hardware-in-loop@r1 (now r2) declared only | 0 end-to-end; S1 unaccepted; S2 accepted but undelivered | 6 | 10 | 0 | 0 | 3 | 0 | gpt-6-astra (steward seat; not a steward filing) |
| 2026-09-15 | 20260915T051905Z-86585ba5 | cloudvore | c124fcd29356c31618db1ae969435b6f0994fc30 | r1 (now r3) | code@r1 (now r3) | 3 filed; S1/S2 delivered without pre-work profile; S3 undelivered; 0 qualifying end-to-end | 10 | 7 | 0 | 0 | 1 | 0 | gpt-6-astra (steward seat; not a steward filing) |
| 2026-09-15 | 20260915T051905Z-86585ba5 | magic-lantern_dannephoto | 30aff3a984c0caa044b750de7ab9646048e71fb2 | r1 (now r3) | hardware-in-loop@r1 (now r2) | 0 end-to-end; 0 eligible; 5 blocked_external | 6 | 2 | 1 | 0 | 7 | 0 (P:hardware-in-loop acceptance-evidence BREAK adopted into hardware-in-loop r2) | gpt-6-astra (steward seat; not a steward filing) |
| 2026-09-15 | 20260915T060404Z-f14bd764 | mlv-app | db44322efba2a95ecccdbe7b5f5b27e2528429d2 | r2 (now r4) | code@r2 (now r4) | 0 end-to-end; S1 bus candidate unaccepted and undelivered; S2 failed seam | 3 | 0 | 0 | 0 | 13 | 0 | gpt-6-astra (steward seat; not a steward filing) |

---

## Steward status — 2026-09-15 (Conjugal, interim steward)

Derived, not asserted. Re-run: `python tools/kernel-e2e.py` (exits 1 while any member is due).

**§5 criterion 1 — CLOSED END-TO-END SUBJECTS: 0.** Summed across all 8 ledger rows. It has been 0
at every harvest. Criterion 1 needs ≥5 projects with ≥1 closed subject each, so finalisation is
0/5, and the ledger now states that number instead of leaving it implicit in a prose column that
nothing sums. `54 FIT, 46 FRICTION, 2 BREAK, 32 UNEXERCISED` over 8 rows.

**Correction to the count of record: the ledger holds 6 projects, not 7.** Seven filings exist on
the bus; six have rows. The missing one is the steward's own, which is the same defect as the
routing gap below rather than a separate one.

**Steward self-filing — routing, per K12.** `origin/review/conjugal-kernel-2026-09-14`
(blob 99cc68bf, 15 findings) has survived three harvests with no dispositions file and no ledger
row. Naming an arbiter is the steward's to do; adjudicating it is not. Criteria: a board with
(1) a bench it can actually reach, and (2) a seat in a different independence class from the
filing's producer, which was Claude.

- `adobe-ingester` — RULED AGAINST ITSELF and is not a candidate: unreachable bench, and a Claude
  seat, i.e. the producer's own class.
- `airmypc` — candidate of record on criterion (2): its posture line reports a Codex
  `gpt-5.6-sol` key lane, which is producer-independent. Criterion (1) is **UNVERIFIED and is the
  probable blocker**.
- `dng-auto-processor` — named as an alternate; has never filed, so its bench and seat are unproven.

**Reachability is the real obstacle, and it is the steward's defect, not the arbiter's.** All 15
findings cite paths in a checkout that exists on one machine. No sibling can re-measure them, so
"nobody has arbitrated it" understates the problem: as filed, nobody *can*. The steward's obligation
is therefore to re-file against a bench a sibling can reach, or to supply the evidence inline.
Recorded here rather than left as a standing request no board can satisfy.

**Members due — 3 have NEVER filed:** `adversarialllm`, `dng-auto-processor`, `salesforce-tools`.
`harvest-status.py` cannot see them: it enumerates filings that EXIST, so a member who has never
filed is indistinguishable from a member who does not exist. That is the same blind spot that let
the steward's own filing sit three runs. `tools/kernel-e2e.py` takes the roster from §6 and reports
the difference.

**Not blocking, so nobody spends a week on it:** RULINGS.md mentions the kernel zero times
(`grep -ci "fleet-factory-kernel\|factory kernel" RULINGS.md` → 0). Criterion 4 has never started.
The owner gate is idle, not jammed.


---

## Harvest 2026-09-17 — run 20260917T193405Z-ab7b8aef (Conjugal, interim steward)

Appended at end of file: this ledger is byte-append-only (the runner's `pure_append` requires the new bytes to start
with the old ones), so new rows cannot be inserted into the table above. Same columns, same order; `tools/kernel-e2e.py`
takes rows by content, not position, and sums both tables.

| date | harvest | filing | blob | kernel | profile | subjects | FIT | FRICTION | BREAK | N/A | UNEXERCISED | unresolved BREAKs | arbiter |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-17 | 20260917T193405Z-ab7b8aef | adobe-ingester | 5e285849969134fb8cafa7ac1fc520864496ae0e | r4 (now r5) | code@r4 (now r5) | 0 end-to-end; WO-G0-A01 rev13 blocked at acceptance closure; control Q-036 rev7/rev8 typed terminals; window-opened-before-kernel=no | 1 | 12 | 0 | 0 | 3 | 0 | gpt-6-astra (steward seat; not a steward filing) |
| 2026-09-17 | 20260917T193405Z-ab7b8aef | agent-bridge | d20a110f7481376553d313ec7fe7a96616e1070d | r4 (now r5) | code@r4 (now r5) | 0 end-to-end under r4; 7 accepted under the local KERNEL (Table S); window-opened-before-kernel=no | 9 | 7 | 0 | 0 | 2 | 0 | gpt-6-astra (steward seat; not a steward filing) |
| 2026-09-17 | 20260917T193405Z-ab7b8aef | airmypc | 6d82c652f4eeca3ccf1eb237657af0264e3625cf | r4 (now r5) | code@r4 (now r5); hardware-in-loop@r2 declared, not exercised | 0 end-to-end; S3 accepted subject to a final-identity qualification, not delivered; window-opened-before-kernel=no | 8 | 2 | 0 | 0 | 2 | 0 | gpt-6-astra (steward seat; not a steward filing) |
| 2026-09-17 | 20260917T193405Z-ab7b8aef | dng-auto-processor | 1f2eceffae1bc8f27fcae12f5e82d158d4bc1158 | r4 (now r5) | measured-objective@r2 (now r3); kernel §6 remapped to code (primary) + measured-objective | 0 end-to-end; 1 in-flight claimed for nothing; 5 retrospective pre-kernel landings not counted; window-opened-before-kernel=yes | 5 | 4 | 3 | 0 | 8 | 0 (K3 BREAK adopted into kernel r5; P:measured-objective subject-identity BREAK adopted into measured-objective r3; P:measured-objective resource-terminals BREAK rejected as instance failure against existing text) | gpt-6-astra (steward seat; not a steward filing) |

Derived, not asserted. Re-run: `python tools/kernel-e2e.py --json`. Every number below is that tool's output.

**§5 criterion 1 — CLOSED END-TO-END SUBJECTS: 0.** Twelve rows, seven projects, and it has been 0 at every harvest.
Criterion 1 needs at least five projects with at least one closed subject each, so finalisation is 0/5. Verdicts across
all 12 rows: **77 FIT, 71 FRICTION, 5 BREAK, 0 N/A, 47 UNEXERCISED.**

**§5 criterion 2 now reads MET on its own text, and that is worth stating plainly rather than leaving implicit.** It
asks for "At least three profiles have been exercised, including at least two whose acceptance is not an automated test
suite." Three profiles now carry harvested rows with exercised verdict lines: `code` throughout, `hardware-in-loop` via
magic-lantern_dannephoto (2026-09-15; a P:hardware-in-loop BREAK was adopted into that profile's r2), and
`measured-objective` via dng-auto-processor in this round — the first `measured-objective` filing on this ledger, where
every earlier row was `code@rN` or `hardware-in-loop@rN`. The two non-test-suite profiles are the latter two. Criterion 2
carries no end-to-end requirement; that bar belongs to criterion 3, which requires "fresh end-to-end evidence meeting
criteria 1 and 2". So criterion 1 is the only criterion whose own text is unmet on evidence, and it blocks criterion 3
with it.

**§5 criterion 3 has not started and cannot start from here:** it needs two successive harvests on an UNCHANGED
revision, and three files changed this round — kernel r4 → r5, `code` r4 → r5, `measured-objective` r2 → r3.
**Criterion 4 has never started**; `grep -ci "fleet-factory-kernel|factory kernel" RULINGS.md` is still 0. The owner gate
is idle, not jammed.

**`window-opened-before-kernel` is new in these rows** (dng-auto-processor O1, adopted in fact and routed as a
standard). The kernel first existed at 2026-09-14T20:49:38Z. Of these four filings only dng-auto-processor's window
opens before that instant. It is context for criterion 1's zero, not credit against it, and dng attached both
disqualifiers itself: adobe-ingester's window is entirely post-kernel and still returned 0, and granting K5
retroactively to every earlier row leaves end-to-end at 0. The field lives inside the `subjects` cell because this file
is append-only and the table header above cannot be edited.

**Members due — 2 have NEVER filed:** `adversarialllm`, `salesforce-tools`. **`dng-auto-processor` has now filed and
leaves that list**, where the 2026-09-15 block named it as a never-filed alternate arbiter. `harvest-status.py` still
cannot see a member who has never filed; `tools/kernel-e2e.py` takes the roster from §6 and reports the difference.

**Steward self-filing — correcting this ledger's own 2026-09-15 entry, on both of its claims.**

*First, the count.* It would be easy to write that the steward's filing has "survived four harvests"; that is false, and
the falsehood is this ledger's to avoid. `origin/review/conjugal-kernel-2026-09-15` (blob `3a36f3e6`, 20 findings by
`harvest-status.py`) first appeared on that branch at 2026-09-15T19:12:41-05:00 = **2026-09-16T00:12Z**, after all three
harvests the 2026-09-15 block was written against (20260914T221904Z, 20260915T051905Z, 20260915T060404Z). Its current
blob was last written 2026-09-17T05:14Z. **This is its first harvest-eligible round, not its fourth.** What survived
three harvests was its predecessor, `conjugal-kernel-2026-09-14` (blob `99cc68bf`, 15 findings), correctly named above.
The standing problem — that no steward filing has ever been routed to an arbiter — is four harvests old; this filing is
not.

*Second, the reachability defect is DISCHARGED, and the 2026-09-15 entry should no longer be read as live.* That entry
recorded "All 15 findings cite paths in a checkout that exists on one machine. No sibling can re-measure them", and
concluded the steward must "re-file against a bench a sibling can reach, or supply the evidence inline." Blob `3a36f3e6`
does exactly that. It carries a section headed "## Reachability re-file, 2026-09-17 — read before ruling" which quotes
that sentence and answers it: "**This revision discharges it. No verdict, claim or wording of any finding changed — only
how its evidence is presented.**" Every finding's evidence field now opens with a tag; measured on the blob, **17 are
`[BUS]`** — "re-measurable from a clone of this branch plus Python, no access to Conjugal needed" — and 14 are
`[UNVERIFIABLE-OFF-HOST]`, declared as such rather than presented as measurable. A ledger that kept saying "nobody can
arbitrate it" would be describing a defect its filer removed before this harvest opened.

*What actually remains, therefore, is arbiter assignment and nothing else.* The steward is excluded from this by kernel
§5 and by this run's configuration, correctly, but exclusion is not routing. The 2026-09-15 block ruled adobe-ingester
out (unreachable bench, producer's own class) and named airmypc a candidate on independence with reachability
UNVERIFIED. **dng-auto-processor is now a candidate it was not on 2026-09-15**: it has filed, its bench is evidenced
across 43 dispositioned findings, and its author seat is Codex — a different independence class from the Claude seat
that produced the steward's filing. Its own U5 raises the matching question from the other side, and this harvest routed
that to a dng adoption-authority bench.

---

## Harvest 2026-09-18 — run 20260918T084905Z-ec1ce658 (Conjugal, interim steward)

Appended at end of file; this ledger is byte-append-only. Same columns, same order; `tools/kernel-e2e.py` takes rows by
content, not position, and sums all three tables.

| date | harvest | filing | blob | kernel | profile | subjects | FIT | FRICTION | BREAK | N/A | UNEXERCISED | unresolved BREAKs | arbiter |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-18 | 20260918T084905Z-ec1ce658 | airmypc-dogfood-20260918 | 9cfb218748c137a1a8a0c33f6a7ac1566be5cc60 | undeclared by the filing; adjudicated against r5, which is unchanged this round | undeclared by the filing; adjudicated against code@r5 (now r6) | 0 credited end-to-end, and the true number is unestablished rather than proved zero: no declared subject identity, no window, no pre-work profile line, no acceptance receipt, no delivery closure; window-opened-before-kernel=undeclared | 0 | 0 | 0 | 0 | 0 | 0 submitted | gpt-6-astra (steward seat; not a steward filing) |

**This row is all zeros because the packet declares no verdict line, not because every clause passed.** The filing is a
`FLEET_CANDIDATE` packet with sections A/B/C and none of the nine kernel §4 header fields, so `harvest-status.py` reads
`findings=0` and flags `NO-PROVIDERS-HEADER`. Under PROMPT-3 §5 it was harvested for the substance its provenance
supports and all nine header defects were recorded as `HEADER:` lines. Three narrative sections are not three verdicts,
and twelve absent clause lines are not twelve UNEXERCISED findings; inventing either would corrupt the only numbers
§5 reads.

Derived, not asserted. Re-run: `python tools/kernel-e2e.py --json`.

**§5 criterion 1 — CLOSED END-TO-END SUBJECTS: 0.** Thirteen rows now across seven projects (`kernel-e2e` lists eight ledger identifiers because this row's filing
name `airmypc-dogfood-20260918` does not map to `airmypc`), and it has been 0 at every
harvest. Criterion 1 needs at least five projects with at least one closed subject each, so finalisation is 0/5.
Verdicts across all 13 rows are unchanged by this round: **77 FIT, 71 FRICTION, 5 BREAK, 0 N/A, 47 UNEXERCISED.**

**§5 criterion 2 remains MET** on the 2026-09-17 finding: `code`, `hardware-in-loop` and `measured-objective` all carry
harvested rows with exercised verdict lines, the latter two being the non-test-suite pair. Nothing this round touches it.

**§5 criterion 3 — the closest this ledger has come, and it still does not start.** For the first time since the kernel
was submitted, **the kernel text is unchanged this round: r5 in, r5 out.** That unchangedness is not evidence about
the kernel: the packet declares no verdict line, so no clause was exercised and none could have moved the text. It is
the digest half of criterion 3 and nothing more. No item in this filing could move it — §5
admits a kernel change only on a BREAK with a concrete counterexample or on FRICTION from two or more profiles, and
this packet establishes neither, being one bench and one profile (`code`) throughout. But criterion 3 requires
"identical kernel and participating-profile content digests as well as revisions", and `code` is the participating
profile and moved r5 → r6 on the two adopted findings. The clock therefore does not start here. It would start at the
first harvest that changes no participating profile either — and criterion 3 also requires fresh end-to-end evidence
meeting criteria 1 and 2, which criterion 1 blocks regardless. **Criterion 4 has never started**;
`grep -ci "fleet-factory-kernel\|factory kernel" RULINGS.md` is still 0. The owner gate is idle, not jammed.

**Members due — 2 have NEVER filed:** `adversarialllm`, `salesforce-tools`. Unchanged from 2026-09-17.
`harvest-status.py` still cannot see a member who has never filed; `tools/kernel-e2e.py` takes the roster from §6.

**Steward self-filing — adjudicated on 2026-09-17, still unrowed.** `tools/kernel-e2e.py` reports `conjugal` in
`filed_but_unrowed`, and that is a ledger gap, not a routing gap: `adjudications/factory-kernel/conjugal.dispositions.md`
exists at commit `dc2a719` — arbiter cloudvore, 2026-09-17, ruling on blob `3a36f3e6` (20 findings: 6 ADOPTED ·
2 ADOPTED-CONDITIONAL · 11 REJECTED · 1 ROUTED, spec_commit `da4e9201`) — and `harvest-status.py` marks `conjugal`
HARVESTED. No arbiter assignment is outstanding for this filing, and the causal account matters as much as the
conclusion: cloudvore had already filled the arbiter seat at commit `dc2a719`, 2026-09-17 15:02:59 -0500, fourteen
minutes BEFORE the block recruiting `airmypc` and `dng-auto-processor` was committed at `8e2144b`, 15:17:26 -0500.
Those candidates were never seated and never needed to be; that recruitment was stale on arrival. What remains is
this ledger's own row, which HARVESTS.md being
steward-written (kernel §5) puts squarely on the steward: the next run should append conjugal's row derived from
cloudvore's dispositions rather than re-route the filing. This run's scope was one filing and it did not append that
row.

**What this round did change:** `specs/fleet-factory-kernel/profiles/code.md` r5 → r6, +85 words (864 → 949), on two
adopted findings — a Claims (K3) row requiring enforced boundaries for read-only reviewer access plus a before/after
canonical audit that compares content hashes, and a Subject identity (K3) row requiring review contracts to name each
identity field's hashed artifact set. Kernel unchanged at 2,867 of 3,500 words. Dispositions:
`adjudications/factory-kernel/airmypc-dogfood-20260918.dispositions.md`.

---

## Harvest 2026-09-18 (second) — run 20260918T151906Z-abb94321 (Conjugal, interim steward)

Appended at end of file; this ledger is byte-append-only. Same columns, same order; `tools/kernel-e2e.py` takes rows by
content, not position, and sums all four tables.

**This row and the 2026-09-18 row above are the SAME filing at two blobs, not two filings.** `airmypc-dogfood-20260918`
was harvested this morning at blob `9cfb2187` and re-filed at blob `697289f2`, which appends sections D and E and
extends `## Proposed destinations`; A/B/C are byte-identical and their dispositions carried forward without
reapplication. Both rows are kept because the ledger is append-only and because a re-file is a real event, but **nothing
in this row is new end-to-end evidence and the two rows must never be summed as two projects' worth of coverage.**

| date | harvest | filing | blob | kernel | profile | subjects | FIT | FRICTION | BREAK | N/A | UNEXERCISED | unresolved BREAKs | arbiter |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-18 | 20260918T151906Z-abb94321 | airmypc-dogfood-20260918 | 697289f24e921ee73412566d7de4e4b043f4d6cd | undeclared by the filing; adjudicated against r5, unchanged this round | undeclared by the filing; adjudicated against code@r6 (now r7) | 0 credited end-to-end; actual qualifying total unestablished rather than proved zero; no declared exact subject identities, window, pre-work profile or bound acceptance/delivery receipts; window-opened-before-kernel=undeclared | 0 | 0 | 0 | 0 | 0 | 0 submitted | gpt-6-astra (high; steward seat; not a steward filing) |

These zeros count submitted verdict lines; they do not certify FIT, manufacture UNEXERCISED findings, or erase attempted
work. Five narrative sections are not five verdicts. A, B and C receive no duplicate evidence credit for appearing in a
second blob.

Derived, not asserted. Re-run: `python tools/kernel-e2e.py --json`.

**§5 criterion 1 — CLOSED END-TO-END SUBJECTS: 0.** Fourteen rows across the same seven projects — `kernel-e2e.py`
prints eight `projects_in_ledger` because the filing name `airmypc-dogfood-20260918` does not map to `airmypc` — and it
has been 0 at
every harvest. Criterion 1 needs at least five projects with at least one closed subject each, so finalisation is 0/5.
Verdicts across all 14 rows are unchanged by this round: **77 FIT, 71 FRICTION, 5 BREAK, 0 N/A, 47 UNEXERCISED.**

**§5 criterion 2 remains MET** on the 2026-09-17 finding: `code`, `hardware-in-loop` and `measured-objective` all carry
harvested rows with exercised verdict lines, the latter two being the non-test-suite pair. Nothing this round touches it.

**§5 criterion 3 — the kernel text is unchanged at r5 for the SECOND consecutive round, and the clock still does not
start.** Two things have to be true, and neither is true here. The digest half: `code` is the participating profile and moved
r6 → r7 on the one conditionally adopted finding, so kernel-and-participating-profile digests are not identical across
the pair. The evidence half: criterion 3 requires "fresh end-to-end evidence meeting criteria 1 and 2", and criterion 1
is 0. Either alone stops it. Stating this plainly because two successive unchanged-kernel rounds is the closest this
ledger has come, and the temptation to read it as progress toward finalisation is exactly what criterion 3's second
requirement exists to refuse. **Criterion 4 has never started**; `grep -ci "fleet-factory-kernel\|factory kernel"
RULINGS.md` is still 0. The owner gate is idle, not jammed.

**Members due — 2 have NEVER filed:** `adversarialllm`, `salesforce-tools`. Unchanged from 2026-09-17.
`harvest-status.py` still cannot see a member who has never filed; `tools/kernel-e2e.py` takes the roster from §6.

**Steward self-filing — the ledger gap named on 2026-09-18 (first) is now in its second round, and this run did not close
it either.** `tools/kernel-e2e.py` still reports `conjugal` in `filed_but_unrowed`. This remains a ledger gap, not a
routing gap: `adjudications/factory-kernel/conjugal.dispositions.md` exists at commit `dc2a719` — arbiter cloudvore,
2026-09-17, ruling on blob `3a36f3e6` (20 findings: 6 ADOPTED · 2 ADOPTED-CONDITIONAL · 11 REJECTED · 1 ROUTED, spec
commit `da4e9201`) — and `harvest-status.py` marks `conjugal` HARVESTED. Both 2026-09-18 runs were scoped by their
runner to one filing, `airmypc-dogfood-20260918`, and neither could append a row for a different filing without leaving
its allowlist. **Recording the reason rather than repeating the observation: this is not a step anyone forgets, it is a
step no single-filing run is authorised to take, so it will not close until a run is scoped to include it.** HARVESTS.md
being steward-written (kernel §5) puts it on the steward.

**What this round changed:** `specs/fleet-factory-kernel/profiles/code.md` r6 → r7, +44 words (949 → 993), on one
ADOPTED-CONDITIONAL finding — a Delivery target (K7) requirement that, for git landings with a governing record commit,
the exact proposed record is built and run through the validators and hooks it will face before any product push, with
contract validation covering every field downstream validators read. Kernel unchanged at r5, 2,867 of 3,500 words. Two
TRAPS.md entries appended (sections D and E). Dispositions:
`adjudications/factory-kernel/airmypc-dogfood-20260918.dispositions.md`, rewritten for blob `697289f2` and superseding
its own ruling on blob `9cfb2187` without withdrawing any disposition that ruling recorded.
