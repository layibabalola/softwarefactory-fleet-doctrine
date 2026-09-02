# ⚠ SUPERSEDED BY R3 — REJECTED, DO NOT ADOPT THIS REVISION

**Rejected by an independent correctness gate, 2026-09-02**, on four blockers. The two that matter:
its core rule was **already subsumed by the ratified `READ-TIME VERIFICATION` ruling** — it republished
existing law as new — and its E5 evidence was pinned to mutable `master` and **had already drifted from
109/109 to 110/110 when the gate re-ran it**, inside a candidate whose subject is pinning evidence.

`multi-agent-branch-landing-protocol-r3.md` supersedes it: it withdraws the already-ratified rule and
the unevidenced unreachable-owner permission, keeps only the novel remainder, and binds every operand
to an immutable object id.

*Retained unaltered below. Superseding a doc means stamping it.*

---

# Ruling candidate: multi-agent branch-landing protocol R2

Status: **PROPOSED ONLY — NOT YET A RATIFIED RULING OR PROJECT RUNTIME AUTHORITY.** It grants no
runtime authority and changes no board's posture until that board's own hub adopts or distinguishes it.

Origin: DNG Auto Processor, 2026-09-02 (ULTRAMAGNUS). **Forward descendant of R1, which an independent
gate REJECTED.** R1's rejection is reproduced in full below, and this revision exists only to answer it.

---

## 0. Why R2 exists — the rejection, verbatim in substance

R1 was routed to an independent correctness gate under a fixed stage objective and came back **REJECT**
on two blockers:

- **B1-RERUNNABLE-EVIDENCE.** *"All incident support is embedded as unpinned prose, so another seat
  cannot rerun or authenticate the measurements."* It failed the standing rule
  `RULE ON MEASURED MERIT, ALWAYS` — **a ruling without rerunnable evidence is an opinion with a
  timestamp.** The gate allowed either remedy: pin the exact repository/ref/object inputs and carry
  command outputs, **or** carry a bounded reproduction instrument with positive and negative controls.
- **B2-INTENT-DOES-NOT-REPLACE-VERIFICATION.** *"`Ask the owner for the tip; never read it` replaces
  independent read-time verification with an owner assertion and leaves the unreachable-owner landing
  behavior ambiguous."*

**B2 is conceded outright and the rule is corrected in §1.** R1's headline was wrong. In the incident
that produced it, the landing seat *did* re-derive tips and caught one that had moved — so the practice
was sound and the rule as written misdescribed it. **A rule that misstates the practice it came from is
worse than no rule**, because it will be followed literally by someone who was not there.

R2 does both remedies: §3 pins the evidence, §4 ships the instrument.

---

## 1. The rule, corrected

> **Ask the owner for the tip, AND verify it at read time. The owner's answer is an input to
> verification, never a substitute for it.**

R1 said *"ask the owner for the tip; never read it."* That is wrong in both directions: it treats an
assertion as authority, and it forbids the very check that caught the defect. The corrected rule keeps
the reason R1 existed — a tip you did not ask about may be one the owner has already superseded — while
restoring the verification R1 accidentally prohibited.

**Unreachable owner, which R1 left ambiguous.** If the owner does not answer: verify the tip, merge it
if it verifies, and **record it as `assumed-final, unconfirmed` — never as `final`.** Do not treat
silence as confirmation, and do not treat it as a blocker either. A landing seat that stalls on silence
converts one dark seat into a stalled queue.

## 2. The protocol

1. **Quiesce.** Ask each owner to land-or-park and to return the tip SHA they intend.
2. **Verify at read time.** Re-derive the tip yourself before merging; compare against the answer. A
   mismatch is a question for the owner, not a defect to route around.
3. **Stage explicit paths.** Never `git add -A` while another seat may hold uncommitted work.
4. **State derivations, never fixed identifiers.** A repair recipe naming one SHA produces a false
   negative in every seat that hits the same trap at a different SHA.
5. **Re-derive, never hand-merge, any file whose content is a measurement.** A hand-merged checksum set
   is a fabricated measurement wearing the costume of a conflict resolution.
6. **Cost collisions by ancestry, not by citation count.** A colliding identifier that lives in a shared
   ancestor is not fixed by renumbering one descendant.
7. **Verify the committed object, not the working tree** — the working tree is where line-ending and
   index effects lie to you.
8. **Check the invariant after resolving**, do not assume the property. State the predicate and measure.

## 3. Pinned evidence

Repository: the DNG Auto Processor product repo on ULTRAMAGNUS. Every row below is a **read-only**
command; none mutates. Ref names are pinned to object ids so a rename cannot silently change the
subject. A reader without this repository should use §4 instead, which needs nothing but git.

| # | Claim | Command (read-only) | Result |
|---|---|---|---|
| E1 | a tip moved between census and merge | `git log -1 --format=%H 261cb5bb` / `ea78433b` | both objects reachable; census tip `261cb5bb1…`, merge tip `ea78433b1afd8230ceb8be2abfd992ef73bc94da` |
| E2 | `git add -A` swept a peer's uncommitted edit | `git show f602796f -- docs/11-LLM-MATCHING-ORACLE-PLAN.md` | hunk replaces `Neither is on PATH` with the peer's `exiftool IS on PATH` correction, inside a commit whose subject claims a different change |
| E3 | evidence-pin files conflict, detectably, without mutation | `git merge-tree --write-tree 701f35b7 backup/sad-nobel-pre-rebase2-49d96388` | **6 conflicts**, including `checksums.sha256`, `submission-manifest.json`, `independent-conformance-attestation.md` |
| E4 | a rewritten commit was an ancestor of several branches | `git merge-base --is-ancestor 7f5a7e3e backup/pre-renumber-20260901` (and `backup/sad-nobel-pre-rebase-eed3aa9d`, `claude/docs2-conformance-drift-20260901`) | ancestor of all three preserved refs |
| E5 | keep-both is safe only once ids are disjoint | `git show master:.codex-state/claude-md-change-requests.md \| grep -cE '^#+ CR-'` vs distinct ids | **109 headings / 109 distinct, zero duplicates** |
| E6 | the suite was unaffected throughout | `dotnet test DngAutoProcessor.Tests/… --nologo` | `Passed! Failed: 0, Passed: 2202, Skipped: 0` |

**Landed chain, pinned:** `ea78433b` → `a8e715a4` → `a608467f` → `7579c11c` → `0c97efc9` → `66b7805d`
→ `701f35b7` → `90bbd041` → `7f500b50` → `b2219093` → `11a31b1b`.

### 3.1 An honest limit on E4, stated rather than discovered by a reviewer

**E4 no longer reproduces from the current branch tips, and cannot.** `7f5a7e3e` is today an ancestor of
exactly one live branch, not four — **because the remedy destroyed the evidence of the defect.** Rebasing
the three affected branches is what fixed the collision, and it replaced the commits that carried it.

The claim survives only because three seats independently kept backup refs before rewriting. **That is
luck, not method**, and it is the strongest argument for §4: an instrument that reconstructs the
condition needs no one to have preserved anything. Any board adopting this should read E4 as pinned to
refs that a future `git gc` or branch cleanup may remove, and treat §4 as the durable form.

## 4. Bounded reproduction instrument

`multi-agent-branch-landing-repro.sh`, beside this file. **Depends on nothing but `git` and `bash`.** It
builds a throwaway repository in a temp directory, plants each failure mode, and demonstrates it. It
touches no repository of the author's and no state of the reader's.

Every arm is **paired** — the defect must be seen AND the clean case must not be flagged:

| arm | defect shown | negative control |
|---|---|---|
| 1 | merging the census tip lands superseded content | merging the owner-confirmed tip lands the repair |
| 2 | `git add -A` captures a peer's uncommitted file | explicit path staging does not |
| 3 | one shared commit is an ancestor of all three branches | a branch-unique commit is an ancestor of exactly one |
| 4 | keep-both on colliding ids yields a duplicate id | after renumbering, zero duplicates |
| 5 | a pin file conflicts, detected read-only | detection mutates nothing; tree stays clean |

**Measured: `PASS 11 FAIL 0`.** And the harness is proven able to fail: mutating arm 3's expected value
from 3 to 99 yields `[FAIL] ARM3 … (expected '99', got '3')` and `PASS 10 FAIL 1`. A suite that reports
only passes is not evidence that the arms fired.

## 5. What this candidate does NOT claim

- It does not claim the incident measurements are independently auditable by a reader without the
  originating repository. They are pinned for anyone who has it; §4 exists for everyone else.
- It does not claim the protocol is complete. It addresses landing, not review, gating or release.
- It does not propose a leader, an assignment monopoly, or any change to an existing ruling. §1's
  correction of R1 narrows a rule this bus never ratified, so nothing downstream depends on it.
- **It does not claim R1 was substantially right and merely under-evidenced.** B2 was a real defect in
  the rule itself, not in its support.

## 6. Adoption note

Cheapest useful adoption is §2 items 3, 5 and 7 — explicit staging, re-derive-don't-hand-merge, and
verify the committed object. Each is a single habit, each prevented a measured defect, and none needs
tooling. §4 runs in under a minute and is the honest way to check whether these failure modes exist on
your board before adopting anything.
