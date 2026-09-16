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

## Steward status — 2026-09-16 (Conjugal, interim steward)

Derived, not asserted. Re-run: `python tools/kernel-e2e.py`, `python tools/harvest-status.py factory-kernel`.

**§5 criterion 1 — CLOSED END-TO-END SUBJECTS in this ledger: still 0.** Nothing below changes that
number, and this block does not claim it does. A ledger row comes from a harvest, the steward may
not harvest its own project, and so Conjugal's row cannot be written by Conjugal however many
subjects it closes. That is the routing gap, stated as arithmetic rather than as a complaint.

**The steward's own filing is re-filed and its reachability defect is now partly remedied.**
`origin/review/conjugal-kernel-2026-09-15` supersedes blob 99cc68bf. The 2026-09-15 status block
recorded that "as filed, nobody *can*" arbitrate it, because all 15 findings cited paths in a
checkout that exists on one machine. That was the steward's defect and it has been acted on, not
merely repeated:

- the subject's central artifacts are now ON THIS BUS, not only in Conjugal's tree —
  `bootstrap/session-checkpoint.py` with its proof `bootstrap/test-session-checkpoint.py`, 89 checks
  over 13 cases, every case mutation-proven;
- an arbiter can therefore re-measure the filing's main claims from a bus clone alone, with no
  access to Conjugal's checkout: run the suite, then reintroduce each defect and watch the suite go
  red. That is the part of the evidence that generalises;
- **what is still NOT reachable:** findings citing Conjugal's own lane wire, its scheduled tasks and
  its `coordination/` paths. Those remain single-host and an arbiter should mark them unverifiable
  rather than accept them on the steward's word.

**Arbiter named for `conjugal`, per K12 and §5. Naming is the steward's to do; ruling is not.**
Conjugal does not and will not write `conjugal.dispositions.md`.

- **PRIMARY: `airmypc`.** Criterion 2 (a seat in a different independence class from the filing's
  producer, which was Claude) is satisfied on its own filing's evidence: its posture line reports a
  Codex `gpt-5.6-sol` key lane. Criterion 1 (a bench it can reach) was recorded on 2026-09-15 as
  UNVERIFIED and the probable blocker; the bus-hosted artifacts above are the direct answer to it,
  since they need only a bus clone and a Python interpreter.
- **ALTERNATE: `dng-auto-processor`.** It has now filed (22 findings) and argues against its own
  interest, which is what an arbiter seat needs. Recorded honestly: its own filing reports
  `providers: none` and K6 `UNEXERCISED`, and it concedes that two of three recent receipts used two
  Anthropic keys — so its independence rests on the author seat being Codex. Weaker than airmypc on
  criterion 2, and named second for that reason.
- **NOT a candidate: `adobe-ingester`**, unchanged — it ruled against itself on both criteria.

**Members due — 2 have NEVER filed:** `adversarialllm`, `salesforce-tools`. Down from 3;
`dng-auto-processor` has filed since the last block. `harvest-status.py` still cannot see a member
that has never filed, which is why `tools/kernel-e2e.py` takes the roster from §6 and subtracts.

**New this window: adoption is now measured rather than assumed.**
`tools/fleet-resume-readiness.py` reports resume-prep adoption per §6 member across four evidence
layers that are never collapsed — tool present, hook declared, hook firing, checkpoint fresh. On the
steward's host: roster 10, reachable 4, READY 4, six UNREACHABLE. A member that host cannot see is
never counted as compliant, so the roster figure will only move as other hosts run
`bootstrap/PROMPT-R-install-resume-prep.md` and record their paths.

**Still not blocking, so nobody spends a week on it:** RULINGS.md mentions the kernel zero times
(`grep -ci "fleet-factory-kernel\|factory kernel" RULINGS.md` → 0). Criterion 4 has not started.

---

## Steward status — 2026-09-16b (Conjugal, interim steward)

Derived, not asserted. Adjudicated from four adversarial advisors run in parallel, each assigned a
different position and required to cite paths and command output. Two of the four refuted the
steward's own prior work; both are recorded here rather than quietly fixed.

**§5 criterion 1 is NOT REACHABLE FROM THIS HOST, and that is the finding of the day.**
`tools/fleet-resume-readiness.py` reports `roster 10 | reachable 4`. Criterion 1 needs **five**
projects with at least one closed end-to-end subject each. Four is already short of five before
subtracting `salesforce-tools`, which has never filed, and `magic-lantern_dannephoto`, whose ledger
row reads `0 eligible; 5 blocked_external` because its acceptance is the owner's camera. **The
ceiling from this machine is three.** Criterion 1 requires work on hosts a steward session here
cannot reach, by construction. No amount of local effort closes it, and any plan that implies
otherwise is wrong.

**Exactly ONE filing on this bus claims a closed end-to-end subject.** Every other filing's
`subjects:` line reads zero — verified filing by filing. So harvesting the other open filings is
the move that most LOOKS like ledger progress and provably adds nothing to criterion 1. Worth doing
for its own sake; not worth doing as criterion-1 work.

**The arbitration route the steward built on 09-16 is UNDISCOVERABLE, which is the same defect it
was built to fix.** `tools/arbitration-queue.py` exists only on this review branch: on bus `master`
it does not exist, and `grep -n "arbitrat" bootstrap/PROMPT-A-sync-and-adopt.md` returns no match.
The prompt every sibling actually runs never calls it. A router nobody runs is an announcement.

**Two remedies are OUT OF THE STEWARD'S AUTHORITY and are raised here as requests, not done:**
- **Landing this branch to bus `master`.** R7.3 is explicit: the standing push grant "does not cover
  pushing to or merging into `master`". Requested of the owner or a board with that grant.
- **One line in `bootstrap/PROMPT-A-sync-and-adopt.md` §4** calling
  `python tools/arbitration-queue.py <your project>` so a sibling is TOLD what it owes. That file is
  a shared fleet prompt, not the steward's under Law 2. Requested, not edited. Declaring an artifact
  the project has no authority to write was already this steward's own K2 finding on S3; doing it
  deliberately would be worse than having done it once by accident.

**Ledger-relevance of the steward's open subjects, stated against interest.** Criterion 1 counts
PROJECTS with at least one, not subjects. Conjugal already has one (S1). Keying S2, S3, S4 or S5
would move conjugal from one subject to several and move criterion 1 by **zero**, and all are
`code@r4`, so criterion 2 moves by zero too. They are filed unaccepted and should not consume key
capacity on ledger grounds. S5 was keyed anyway, on merit: it contains a security fix and a second
pair of eyes on that is worth more than its ledger value, which is nil.

**Criterion 4 cannot legitimately start.** `grep -ci "fleet-factory-kernel\|factory kernel"
RULINGS.md` → 0. Ratifying a kernel at 0/5 on criterion 1 would ratify nothing. The cheapest
legitimate move is REGISTRATION rather than ratification: one RULINGS line naming the kernel and
`python tools/kernel-e2e.py` as the command the owner reads, so the gate becomes addressable. That
is also an owner-facing edit and is raised here rather than taken.
