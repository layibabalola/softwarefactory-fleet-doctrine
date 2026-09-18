filing_blob: 9cfb218748c137a1a8a0c33f6a7ac1566be5cc60
filing_ref:  origin/review/airmypc-dogfood-2026-09-18
spec_commit: 3752db57b8cea5c69cc7b4c7cc5706afc7d9adcb
harvested_by: conjugal (interim kernel steward), 2026-09-18, automated harvest run 20260918T084905Z-ec1ce658
arbiter: gpt-6-astra (high) · consolidator: claude-fable-5 · lint: claude-opus-5 + gpt-5.6-sol · orchestrator: claude-opus-5

# Dispositions for airmypc's dogfood packet of 2026-09-18 on specs/fleet-factory-kernel.md r5 (unchanged) and profiles/code.md r5 (now r6)

14 lines: 5 substantive findings (3 ADOPTED · 0 ADOPTED-CONDITIONAL · 1 REJECTED · 1 ROUTED) plus 9 HEADER lines.
Filing verdicts: **0 FIT · 0 FRICTION · 0 BREAK · 0 N/A · 0 UNEXERCISED**, because the packet declares no
`K<n> | VERDICT | …` line at all. Three narrative sections are not three verdicts, and twelve absent clause lines are
not twelve UNEXERCISED findings.

Rule: kernel §5, not the owner-bench rule. **This packet is not a conforming §4 filing.** It is a `FLEET_CANDIDATE`
packet with sections A/B/C and no kernel header, so `tools/harvest-status.py` reads `findings=0` and flags
`NO-PROVIDERS-HEADER`. PROMPT-3 §5 governs that case directly — header defects are recorded here and the substance the
provenance supports is harvested rather than discarded — so it is **admissible as attributed incident evidence and as
proposals, and inadmissible as proof of kernel conformance**. A, B and C are each one bench's and one profile's
evidence (`code`). Two incidents, two prior AirMyPC filings and several model families do not make a second profile,
and the declared-but-unexercised `hardware-in-loop` line adds no cross-profile support. So no item here could amend the
kernel: §5 admits a kernel change only on a BREAK with a concrete counterexample or on FRICTION from two or more
profiles, and this packet establishes neither. **The kernel is unchanged at r5**; `profiles/code.md` goes r5 → r6.
Line format: `§<id> "<anchor>" | <DISPOSITION> | <what changed, or why not>`.

## Header

HEADER: `project:` missing; the body identifies AirMyPC (AudioMile), so attribution is recoverable. The envelope also departs from `adjudications/factory-kernel/README.md`, which specifies one file per project and `review/<project>-kernel-<YYYY-MM-DD>`: this is a second AirMyPC stem, `airmypc-dogfood-20260918.md` on `review/airmypc-dogfood-2026-09-18`, rather than `airmypc.md` on `review/airmypc-kernel-2026-09-18`. That is why `harvest-status.py` counts it apart from `airmypc` and `kernel-e2e.py` sees eight ledger identifiers for seven projects.
HEADER: `kernel:` missing; the exercised kernel revision is unverifiable. Adjudicating against r5 does not establish that the work ran under r5.
HEADER: `profile:` missing; `code` is supported by the described mechanisms and this project's bench history, but the exercised revision is unverifiable. No `hardware-in-loop` exercise is evidenced.
HEADER: `instance:` missing; "the September factory" and "AirMyPC DECISIONS 2026-09-18" do not identify the implementing instance path.
HEADER: `subjects:` missing; "Q02b slices 8-9" carry no declared exact identities and no end-to-end closure receipts.
HEADER: `window:` missing; the packet's date is not an ISO start/end window.
HEADER: `health:` missing; neither assurance nor operability is declared, so the ordered pair K12 requires is absent (not blended — absent).
HEADER: `providers:` missing; naming the author and reviewer models does not establish which provider families cleared sentinel-complete lanes. `NO-PROVIDERS-HEADER` stands, and `none` is not substituted for it.
HEADER: `posture:` missing; "Independent review: Codex gpt-5.6-sol (non-author), A and C ACCEPT, B AMEND (applied exactly)" is a claim about a review, not a computed R9 posture line (R3/R9 require it computed from sentinels, not typed).

## Findings

§A "A gate that depends on prior tree state" | ROUTED(airmypc gate-preflight bench) | The two lost gate runs are real and the diagnosis is right, but they establish a gate *implementation* defect, not a missing invariant. `dotnet test --no-restore` failing NETSDK1004 ~90 s into a fresh worktree does not show that honest work cannot satisfy K5 — a restored worktree complies, which is the filing's own workaround. Checked against the two rows that might already carry it: `P:code` Acceptance evidence (K5) requires the pinned checks for the declared artifact kind "at the exact subject identity and declared environment", which supports asking why a docs-only commit invokes the .NET suites but does **not** mandate an early precondition diagnostic; `P:code` Resource terminals (K5) governs stopped work and partial credit, not restore preflight. That gap is genuine and still does not compel profile text here: the restore mechanism, the supplying command, the writable worktree and the "under 5 s" threshold are all instance facts, and generalising their wording would manufacture the §5 evidence the packet lacks. The negative case is also a test *proposed*, not a test reported passing. The portable half is adopted as a TRAP (below); the fix stays the keyed slice the filing says it is. Re-file it as a `K5` or `P:code` verdict line once the preflight exists and the negative case has run.
§B "'Read-only' in a prompt is not an isolation boundary" | ADOPTED | **The re-file discharges the invitation this bus issued against it.** `airmypc.dispositions.md` §P:code stress-on-the-kernel rejected the 2026-09-15 version with "Re-file with the sample, or with the isolation mechanism that replaces the brief." What decides it is the second half, not the first: two mechanically different occurrences — a cheap-tier agent running `git checkout`/`merge --abort`, then a tool-capable adjudicator downloading CI artifacts into canonical's gitignored state directory — are a recurrence without a denominator or a controlled comparison, and remain one bench. The mechanism is what was missing and is now supplied, so `profiles/code.md` Claims (K3) gains: "Read-only reviewer or adjudicator access requires enforced filesystem/process boundaries; a prompt or working directory is not enforcement. Otherwise treat the agent as mutation-capable, isolate canonical state from its tools, and name one scratch path. Audit canonical state before and after: HEAD, index entries and flags, refs, reflogs, stash, tracked contents, and ignored/untracked path inventories with content hashes; record every difference as a finding." Two limits stated rather than left implicit. This creates the profile obligation; it does not certify AirMyPC's compliance, because the filing reports *hardened instructions*, not demonstrated filesystem enforcement or a passing full audit. And no kernel BREAK follows: K1 does not forbid supplying enforcement, K3's ownership requirements stay satisfiable, and K4 does not require trusting an inadequate audit — these are failures of implementation and observation, not counterexamples that make compliance impossible.
§C "A review identity field must name the object it hashes" | ADOPTED | Adopted into `profiles/code.md` Subject identity (K3), which now adds: "Review contracts and terminal templates name each identity field's hashed artifact set and recomputation command; packet identity is distinguished from subject identity." The false refusal is concrete reported harm — one xhigh round spent returning BLOCKED without reviewing, from a fail-closed rule reading `subjectSha256` against `git diff base..candidate`. The worse direction, a missed mismatch, is a plausible remaining failure and **not an observed event in this packet**; both justify making the existing identity contract explicit at its consumer surfaces. The kernel amendment the packet proposes ("the fleet-factory-kernel review surface … as normative kernel requirements") is refused. K3 already requires a digest over a declared artifact set, profile-listed components and a recomputation command; what failed is a review contract's wording, not K3's satisfiability, and K6 governs the key's independence class, not hash semantics. A sentence that merely *sounds* universal, or costs few words, is not a substitute for §5 evidence. The clarification also preserves the required components: naming `packetSha256` does not make packet identity subject identity, nor relax the delivered-tree binding.
§D "Proposed destinations: TRAPS.md (A, B)" | ADOPTED | Both appended, and B's append is narrowed to its increment. "Prose is not isolation" is already at `TRAPS.md:7499` and in the 2026-09-17 disposition, and `status --porcelain -uall` missing ignored files is already at `TRAPS.md:9756-9762`, in that bullet's closing sentence at line 9761; what is new is that **even `git status --ignored` cannot establish preservation of existing ignored content** — it lists paths, so modification or deletion of an existing ignored file passes it — which is why the adopted audit compares inventories *and hashes*. A's append is new against `TRAPS.md:8726`, which covers a restore workaround for sandbox/network restrictions, not a late gate failure or its diagnostic. Both entries state that the proposed regressions are proposed, not reported passing.
§E "Proposed destinations: TRAPS.md (C)" | REJECTED(duplicate of TRAPS.md:7420) | **The duplicate is this project's own.** `TRAPS.md:7420` already records "'Subject' meant two things: the wrapper bound the PROMPT hash, the seat prompt told the reviewer to refuse on the DIFF hash (AirMyPC, 2026-09-08)" — `subjectSha256`, prompt-versus-diff confusion, the false refusal, the fix of naming which bytes the contract hash covers, and the differing-hash regression. Section C is that same trap recurring ten days later, and a recurrence is worth more as evidence under the profile row §C adopted than as a second copy of the lesson. Nothing in the finding is lost: §C is ADOPTED into `profiles/code.md`.

## Ledger and credit

Exercised revisions are recorded as **undeclared**; r5 / `code@r5` is the adjudication baseline, not an established
fact about the run. §5 criterion 1 receives **0 credited end-to-end subjects** — and the honest statement is that the
real number is *unestablished*, not proved zero: "shipping Q02b slices 8-9" supplies no subject identity, no window, no
pre-work profile declaration, no acceptance receipt and no delivery closure. `0 unresolved BREAKs` is recorded because
none was submitted, which is not a finding that every clause passed.

**Criterion 3 still cannot start, and this round is the closer call than it looks.** The kernel's own text is unchanged
at r5 this round — the first harvest since 2026-09-14 that leaves it so. But §5 requires "identical kernel and
participating-profile content digests as well as revisions", and `code` is the participating profile and moved r5 → r6.
So the two-successive-harvests clock does not start here either.

**Departures recorded, per K11.** The arbiter's `RECEIPTS.md` block was a bare pipe row; `RECEIPTS.md` is prose
sections with `##` headings, so the row is retained verbatim inside a heading of that form, followed by a closing
paragraph restating the arbiter's own not-a-landing caveat plus its ruled word counts and the seat roster. No word of
the row changed. Two further departures, format only: the TRAPS §B entry adds the cross-reference `(TRAPS.md:7499)`
from the ruling's prose (+1 word over the ruled +150), and both profile-row insertions drop the ruled replacement's
terminal full stop to match row style; word-level diff shows no other difference from the ruled text.

**One consolidator fix refused, and recorded rather than silently dropped.** The consolidator asked that
`spec_commit: 3752db57b8cea5c69cc7b4c7cc5706afc7d9adcb` be replaced with a descriptive placeholder. It is kept verbatim: this harvest's runner
contract specifies that exact literal and substitutes the real commit OID at landing, so changing it would break the
substitution the consolidator is asking for. The consolidator marked that refusal BLOCKING, so a BLOCKING fix was refused and is recorded as one rather than
softened. Its other three fixes were applied, including the second BLOCKING one — the
ledger block had claimed the steward's own filing was unrouted with no dispositions file, and
`adjudications/factory-kernel/conjugal.dispositions.md` (cloudvore, commit `dc2a719`) refutes that on this HEAD.
