filing_blob: 697289f24e921ee73412566d7de4e4b043f4d6cd
filing_ref:  origin/review/airmypc-dogfood-2026-09-18
spec_commit: 21d8c3cec573ae446a67d2edda20fcba1e08b048
harvested_by: conjugal (interim kernel steward), 2026-09-18, automated harvest run 20260918T151906Z-abb94321
arbiter: gpt-6-astra (high) · consolidator: claude-fable-5 · lint: claude-opus-5 + gpt-5.6-sol · orchestrator: claude-opus-5

# Dispositions for airmypc's dogfood packet of 2026-09-18, re-filed — on specs/fleet-factory-kernel.md r5 (unchanged) and profiles/code.md r6 (now r7)

**Supersedes this file's ruling on blob `9cfb218748c137a1a8a0c33f6a7ac1566be5cc60`** (run 20260918T084905Z-ec1ce658,
spec commit `3752db57b8cea5c69cc7b4c7cc5706afc7d9adcb`). That ruling is not withdrawn: every disposition it recorded is
restated below — §A, §B and §C at their own lines, and its two destination dispositions at §PD-TRAPS, which carries
the rejection of C's duplicate TRAP as an explicit exclusion rather than as a separate line, which is why the tally
below counts one REJECTED and not two — and the two profile rows it landed stay landed at r6 and are not reinserted.

16 lines: 7 substantive findings (1 ROUTED carried · 2 ADOPTED carried · 2 ADOPTED · 1 ADOPTED-CONDITIONAL ·
1 REJECTED) plus 9 HEADER lines. Filing verdicts: **0 FIT · 0 FRICTION · 0 BREAK · 0 N/A · 0 UNEXERCISED**, because the
packet declares no `K<n> | VERDICT | …` line at all. Five narrative sections are not five verdicts, and twelve absent
clause lines are not twelve UNEXERCISED findings. These zeros count submitted verdict lines; they do not certify FIT,
manufacture UNEXERCISED findings, or erase attempted work.

Rule: kernel §5, not the owner-bench rule. **This packet is not a conforming §4 filing.** It is a `FLEET_CANDIDATE`
packet with sections A/B/C/D/E and no kernel header, so `tools/harvest-status.py` reads `findings=0` and flags
`NO-PROVIDERS-HEADER`. PROMPT-3 §5 governs that case directly — header defects are recorded here and the substance the
provenance supports is harvested rather than discarded — so it is **admissible as attributed incident evidence and as
proposals, and inadmissible as proof of kernel conformance**. Every section is one bench's and one profile's evidence
(`code`), and the declared-but-unexercised `hardware-in-loop` line adds no cross-profile support. Line format:
`§<id> "<anchor>" | <DISPOSITION> | <what changed, or why not>`.

**Re-file provenance.** Blob `697289f24e921ee73412566d7de4e4b043f4d6cd` adds filing sections D/E and extends Proposed
destinations relative to harvested blob `9cfb218748c137a1a8a0c33f6a7ac1566be5cc60`. A/B/C are byte-identical and their
dispositions carry forward without reapplication. This round's §D/§E identify the filing's new sections; the former
destination findings are represented by §PD-TRAPS/§PD-KERNEL. **This is recorded as ordinary provenance, not as a tenth
header defect.** The steward proposed one — that a re-file carries no supersession marker or changelog — and the arbiter
OVERTURNED it: `adjudications/factory-kernel/README.md` says to "Rewrite it wholesale each window; the harvest tool marks
it `STALE` and the steward re-reads it", and PROMPT-3 §5 makes a changed blob stale automatically. Neither requires a
changelog, so the defect would have been invented by this bus rather than found in the filing.

## Header

HEADER: `project:` missing; the body identifies AirMyPC (AudioMile), so attribution is recoverable. The envelope also departs from `adjudications/factory-kernel/README.md`, which specifies one file per project and `review/<project>-kernel-<YYYY-MM-DD>`: this is a second AirMyPC stem, `airmypc-dogfood-20260918.md` on `review/airmypc-dogfood-2026-09-18`, rather than `airmypc.md` on `review/airmypc-kernel-2026-09-18`. That is why `harvest-status.py` counts it apart from `airmypc` and `kernel-e2e.py` sees eight ledger identifiers for seven projects.
HEADER: `kernel:` missing; the exercised kernel revision is unverifiable. Adjudicating against r5 does not establish that the work ran under r5.
HEADER: `profile:` missing; `code` is supported by the described mechanisms and this project's bench history, but the exercised revision is unverifiable. No `hardware-in-loop` exercise is evidenced.
HEADER: `instance:` missing; "the September factory" and "AirMyPC DECISIONS 2026-09-18" do not identify the implementing instance path.
HEADER: `subjects:` missing; "Q02b slices 8-9" carry no declared exact identities and no end-to-end closure receipts. Section E's "candidate 5, which then landed DONE" is the closest this packet comes and still names no identity, window or bound acceptance receipt.
HEADER: `window:` missing; the packet's date is not an ISO start/end window.
HEADER: `health:` missing; neither assurance nor operability is declared, so the ordered pair K12 requires is absent (not blended — absent).
HEADER: `providers:` missing; naming the author and reviewer models does not establish which provider families cleared sentinel-complete lanes. `NO-PROVIDERS-HEADER` stands, and `none` is not substituted for it.
HEADER: `posture:` missing; "Independent review: Codex gpt-5.6-sol (non-author), A and C ACCEPT, B AMEND (applied exactly)" is a claim about a review, not a computed R9 posture line (R3/R9 require it computed from sentinels, not typed).

## Findings

§A "A gate that depends on prior tree state" | ROUTED(airmypc gate-preflight bench) | **Carried forward unchanged; the section is byte-identical to the harvested blob and nothing in this re-file bears on it.** The two lost gate runs are real and the diagnosis is right, but they establish a gate *implementation* defect, not a missing invariant. `dotnet test --no-restore` failing NETSDK1004 ~90 s into a fresh worktree does not show that honest work cannot satisfy K5 — a restored worktree complies, which is the filing's own workaround. `P:code` Acceptance evidence (K5) supports asking why a docs-only commit invokes the .NET suites but does not mandate an early precondition diagnostic; `P:code` Resource terminals (K5) governs stopped work and partial credit, not restore preflight. That gap is genuine and still does not compel profile text: the restore mechanism, the supplying command, the writable worktree and the "under 5 s" threshold are all instance facts. The negative case is a test *proposed*, not a test reported passing. Its TRAP already exists at `TRAPS.md:11485` and is not re-appended. Re-file it as a `K5` or `P:code` verdict line once the preflight exists and the negative case has run.
§B "'Read-only' in a prompt is not an isolation boundary" | ADOPTED | **Carried forward; landed at `profiles/code.md` Claims (K3) in r6 and NOT reinserted this round.** The adopted text stands verbatim: "Read-only reviewer or adjudicator access requires enforced filesystem/process boundaries; a prompt or working directory is not enforcement. Otherwise treat the agent as mutation-capable, isolate canonical state from its tools, and name one scratch path. Audit canonical state before and after: HEAD, index entries and flags, refs, reflogs, stash, tracked contents, and ignored/untracked path inventories with content hashes; record every difference as a finding" (63 words; +0 this round). Two mechanically different occurrences are a recurrence without a denominator, and remain one bench; what decided it was the mechanism, not the count. This creates the profile obligation; it does not certify AirMyPC's compliance, because the filing reports *hardened instructions*, not demonstrated filesystem enforcement or a passing full audit, and no new evidence of enforced isolation arrives with this blob. No kernel BREAK follows.
§C "A review identity field must name the object it hashes" | ADOPTED | **Carried forward; landed at `profiles/code.md` Subject identity (K3) in r6 and NOT reinserted this round.** The adopted text stands verbatim: "Review contracts and terminal templates name each identity field's hashed artifact set and recomputation command; packet identity is distinguished from subject identity" (22 words; +0 this round). The false refusal is concrete reported harm — one xhigh round spent returning BLOCKED without reviewing. The worse direction, a missed mismatch, remains a plausible failure and not an observed event in this packet. The kernel amendment the packet proposes is refused: K3 already requires a digest over a declared artifact set, profile-listed components and a recomputation command; what failed is a review contract's wording, not K3's satisfiability.
§D "A provider refusal is a lane outcome, never a verdict" | ADOPTED | TRAPS.md append only, limited to the reported wording-sensitive refusal and its recovery classification. Kernel and profile text changes are REJECTED: existing positive-evidence and typed-terminal requirements already prevent assurance credit without a verdict; this packet establishes neither a kernel BREAK nor cross-profile FRICTION. Preserve refused-attempt receipts and expenditure accounting; no completed-review credit does not mean no attempt occurred. **Two steward arguments were corrected by the arbiter and are recorded here rather than quietly dropped.** First, the steward reasoned that because the lane "recorded FAILED/UNEVALUABLE correctly" the section reports compliance and is therefore cost-free FIT; correct terminal handling does not establish cost-free FIT, and an xhigh attempt was still spent. Second, the steward asserted that the converging MLV-App case (`TRAPS.md:9808`) reports no cost a clause would have prevented; it explicitly does — "six hub actions" refused at line 9810, and at 9816-9817 "The consequence is worse than lost turns", because a board cannot record its own incidents in the words that describe them. The conclusion survives both corrections for a different reason than the steward gave: MLV-App's incident is source-and-tooling work under `code`, not its separate `measured-objective` bench, so the pair is two benches on one profile and cannot be the cross-profile FRICTION §5 requires. The appended TRAP is narrowed to refusal classification, wording-sensitive recovery and preservation of attempt accounting.
§E "A landing tool must prove its record commit" | ADOPTED-CONDITIONAL(airmypc record-commit landing bench) | Adopt the exact-record preflight increment into `code.md` Delivery target (K7), scoped to git landings with a governing record commit, and append the narrowed TRAP. REJECT the kernel amendment: the reported implementation failure does not make K7 unsatisfiable. The production tool fix and negative regressions remain unproved. The inserted text is 44 words, placed immediately after "…record post-write digests as one recoverable transaction; rehearse reversal on a copy first.": "For git landings with a governing record commit, build the exact proposed record and run the validators and hooks that commit will face before any product push; refuse on failure. Contract validation covers every field downstream validators read, including evidence verdicts and next-packet executability." **CONDITIONAL, not flat ADOPTED, and the steward proposed the weaker form.** The increment is singular evidence under PROMPT-3 §3 — one bench, one landing path — so it is scoped to the conditions that bench establishes rather than generalised to the fleet. **A steward argument is withdrawn as factually wrong:** the steward wrote that the ratified Cloudvore 2026-08-11 ruling "carries the recovery half" only. It carries prevention too — `RULINGS.md:647-650` refuses before mutation on authority and fingerprint drift, and 757-759 requires that changing bound inputs "refuses before the relevant mutation". What is genuinely absent from both that ruling and `code.md` is narrower: validating the exact proposed *governing record* through its own downstream validators and hooks before the product push, including the fields those validators consume. `code.md` Delivery target (K7) required rehearsal only for register-permitted runtime installations ("rehearse reversal on a copy first"), never for the git landing path. Preflight does not replace the `CLOSURE_INCOMPLETE` recovery and next-landing interlock, which stay binding. Also recorded: the packet's `PARTIAL` outcome proves neither compliance with nor violation of that interlock; this packet does not establish that behaviour either way.
§PD-TRAPS "TRAPS.md (A, B, C, D, E)" | ADOPTED | **Adopted with explicit exclusions; this is not adoption of all five requested appends.** D and E are appended this round in the arbiter's exact words, each naming the prior entry it extends rather than duplicates and each stating that its regression pattern is proposed, not reported passing. A and B were appended this morning at `TRAPS.md:11485` and `TRAPS.md:11492` and are not re-appended. C stands **REJECTED(duplicate of TRAPS.md:7420)** on the prior round's reasoning, which this blob does not disturb: that entry is AirMyPC's own, ten days older, and already records `subjectSha256`, the prompt-versus-diff confusion, the false refusal, the fix of naming which bytes the contract hash covers, and the differing-hash regression — "A hash is only an identity if every reader agrees which bytes it hashes" (`TRAPS.md:7427`). Nothing is lost: §C is adopted into `profiles/code.md`.
§PD-KERNEL "the fleet-factory-kernel review surface (A, C and E)" | REJECTED(no BREAK with a counterexample; one profile) | All three refused. A is routed, C landed at profile level at r6, E lands at profile level this round conditionally. §5 admits a kernel change only on a BREAK with a concrete counterexample or on FRICTION from two or more profiles, and this packet is one bench and one profile (`code`) throughout. **One count the steward should not make, and the arbiter said so: one bench *could* establish a BREAK. The number of benches is not itself the ground for rejection** — the ground is that no section here names honest work that cannot satisfy the kernel as written. Each of A, C and E describes an implementation that failed something it was able to do.

## Ledger and credit

Exercised revisions are recorded as **undeclared**; r5 / `code@r6` are the adjudication baselines, not established facts
about the run, and the ledger row says so rather than converting one into the other. §5 criterion 1 receives **0 credited
end-to-end subjects** — and the honest statement is that the real number is *unestablished*, not proved zero: the packet
supplies no exact subject identity, no window, no pre-work profile declaration and no bound acceptance or delivery
receipt. Section E's reported successful workaround does not supply any of them. `0 unresolved BREAKs` is recorded
because none was submitted, which is not a finding that every clause passed. A, B and C receive no duplicate evidence
credit for appearing in a second blob.

**Criterion 3 does not advance.** The kernel's own text is unchanged at r5 for the second consecutive round. But §5
requires "identical kernel and participating-profile content digests as well as revisions", and `code` is the
participating profile and moved r6 → r7 on §E. Qualifying end-to-end evidence also remains unestablished, so criterion 1
blocks criterion 3 independently of the digest question.

**What changed this round.** `specs/fleet-factory-kernel/profiles/code.md` r6 → r7, +44 words (949 → 993), on one
conditionally adopted finding. `specs/fleet-factory-kernel.md` unchanged at r5, 2,867 of 3,500 words. Two TRAPS.md
entries appended. One ledger row appended to `adjudications/factory-kernel/HARVESTS.md`.

**Departures recorded, per K11.** Format only: the ruled §E disposition adds backticks around `code.md`; the
ruled provenance paragraph is applied as a bolded body paragraph with backticked blob ids; the ruled §D anchor is
restored to the filing's own heading, "A provider refusal is a lane outcome, never a verdict", from the arbiter's
truncated "A provider refusal is a lane outcome"; and the retained `subjects:` HEADER line adds one sentence noting
that section E's "candidate 5" report supplies no identity, window or bound receipt. Beyond these, and the steward's
own reasoning appended to the §D and §E lines, word-level diff shows no difference from the ruled text: the profile
insertion, both TRAPS entries, the HARVESTS row and the RECEIPTS block are word-for-word identical to the ruling.

**Prior-round records carried forward, since this rewrite is their only custodian.** The 2026-09-18 (first) ruling
recorded two K11 departures that remain true of bytes still in the tree: the TRAPS §B entry adds the cross-reference
`(TRAPS.md:7499)` from the ruling's prose (+1 word over the ruled +150), now standing at `TRAPS.md:11496`, and both r6
profile-row insertions drop the ruled replacement's terminal full stop to match row style. It also recorded one
refused consolidator fix rather than dropping it silently: the consolidator asked that `spec_commit` be replaced with
a descriptive placeholder and marked the refusal BLOCKING; that round kept the exact literal its runner contract
substitutes at landing, and this round's runner contract names `21d8c3cec573ae446a67d2edda20fcba1e08b048` for the same purpose.
