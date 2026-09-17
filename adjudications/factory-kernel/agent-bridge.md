# Factory-kernel dogfood filing — agent-bridge (KR4-FILE-2 r2)

project: agent-bridge
kernel: fleet-factory-kernel r4
profile: code@r4
instance: .claude-state/coordination/KERNEL.md (3B0EE2D2, gitignored; packet/KERNEL.md)
subjects: 0 end-to-end under r4 (L551: r4 unadopted; product cards ran under the local KERNEL); Table S lists 7 accepted under it.
window: 2026-09-16T21:55Z .. 2026-09-17T15:12Z = WAL lines 500..556 (raw bytes 0..340602, sha256 E014FCCF). packet/WAL-L557-L560.md postdates it (the predecessor review); evidence for N5 and independent-key only.
health: assurance=UNSATISFIED operability=PRESSURED
providers: codex (gpt-5.6-sol, gpt-6-astra; sentinels in packet/RECEIPTS-AND-LANE-CEILING.md)
posture: conjugal-standard-PARTIAL (0/17 lanes; missing: Designer-Scope 0/1; Designer-Verify 0/1; Lint-Consistency 0/2; Arbiter 0/1; Consolidator 0/1; Panel 0/8; Classifier 0/3); cross_family: NO-CROSS-FAMILY-VALIDATION. Computed (packet/POSTURE*.md: bus dc20a28 and 9ae4030, same tool and output); this text's class-C review ran outside those roles.

**Scope.** Retrospective evidence under the local KERNEL, read against r4. P:code lines propose code-profile text; N1 and N4 are domain-general kernel candidates awaiting a second profile (§5), no REPLACES. Claude cleared no lane sentinel: not a provider. `L<n>` = `.claude-state/HUB_RUN_WAL.md` line n; `D <card>` = its record in `.claude-state/coordination/decisions/`; packet = `evidence/KR4-FILE-2-20260917/r2/packet/`; a SOL/ASTRA id = sentinel inspected.

**Table S**

| card | identity | state |
|---|---|---|
| F20e | commit 0aba2cce55fd227515bbc04f3b08400f8ebdda67 (blob, sha256: D F20e) | adopted (doc) |
| F30e | sums 78324490A6AC21517A9DF63717F27E76DFFCF9A74CA4D60B68E3583961D51045 | installed, A3D9152F -> 09EFEEE8 |
| KR-WALFREEZE | sums E9CB461EE995C9FD84782B1E8BEDD8F582BEFE5083E41EDE49F73BF1F236AC1B | installed, B76BDC57 -> 29B63747; lapsed |
| KR-WALHARM | candidate VERDICT-L4-L1.md F8A99278F785B1037B0C4FFFFE92E8B8BAAB97682F4B88FC043BC27C71857C8B | installed, 29B63747 -> 3B0EE2D2 |
| P-16-R | commit 516b436e9b8b0f164a9843437e98d71505cd48cc | pushed, PR #11, CI billing-blocked |
| P-0c | commit 9d83d025716f8c8f7e9bf3cd42e36be836fbeec0 | not merged, CI billing-blocked |
| P-0b | commit 35d82c9c6cec9cc1511d2153109178fee7c0450c | local only |

## Clauses

K1 | INSTANCE-FAILURE | "Producer, verifier, adjudicator and owner are distinct roles." | P-0b: session 52250cd7 wrote the fix (L550), recorded adoption (L551) and is `decidedBy` in D P-0b; only outside key SOL-20260917-093452-631 | PROOF: a P-0b record naming another adjudicator

K2 | INSTANCE-FAILURE | "otherwise only for deadlock, a novel class, high risk, or an irreversible act" | F30e's owner-only re-bless (D F30e; L517) has no channel; L551 names a 09-08 owner gate on Astra absent from packet/KERNEL.md (0 lines match `astra`), yet honoured (N4) | PROOF: a receipt of the re-bless reaching the owner, or a pre-09-17 register line for the Astra gate

K3 | FIT | "an asset manifest of blob hashes for binaries held outside git, or a document hash" | F20e bound by commit, blob and sha256 (D F20e); runtime subjects by sums-file or candidate-file sha256, which K3 allows; cost: subject-identity | PROOF: a Table S identity not recomputable from its artifacts

K4 | FIT | "Never exit code, output size or silence." | packet/F30e-REPRO.md on live driver A3D9152F: injected throw: exit 1, no receipt, child and grandchild alive; kill-switch control: receipt, both dead; paid probe not run (D F30e) | PROOF: a lane run on 09EFEEE8 counted complete without its receipt

K5 | INSTANCE-FAILURE | "declares its profile and profile version" | no packet record has a `profile` property: 0 of 16 in-window records, 0 of 17 packet-total (2 prose mentions) | PROOF: a card with `profile: code@r4` recorded before dispatch

K6 | FIT | "Every acceptance includes a key from an independence class other than the producer's." | all 7 acceptances carry a gpt-5.6-sol key (packet receipts), producers Claude. Reviewer-as-producer: independent-key, N5, Untested | PROOF: a Table S acceptance with no codex receipt id

K7 | FIT | "Acceptance and delivery are separate states." | P-16-R accepted 07:22, blocked 07:23 (L542–L543; 2h50m); P-0c "Not merged" (56m); P-0b "NOT PUBLISHED" (28m); accepted-undelivered work is found only via WAL status strings | PROOF: an accepted Table S subject with no WAL status string

K8 | UNEXERCISED | "Running out of quota means rotating or parking" | no quota refusal in L500–L556; L555's Astra refusal was a missing price (N4); capacity refusal: N5 | PROOF: a provider quota refusal in L500–L556

K9 | FIT | "resumes from the project's tree and the bus alone" | five sessions resumed from in-tree HANDOFF files (L522, L524, L529, L533, L544); stale-register cost: dispatch-preflight | PROOF: a window resume needing anything outside the tree or the bus

K10 | UNEXERCISED | "Account parity is verified before any provider work" | not re-measured; no parity output read | PROOF: parity output bound to a window receipt

K11 | FIT | "apply to every report a factory makes about itself" | L532 withdrew L531's 1 MiB claim; this round withdraws round 1's "no entry means no permission" sentence (contradicts K2) and its FIT independent-key line carrying replacement text | PROOF: an uncorrected window claim its own record refutes

K12 | FIT | "The steward harvests every filing and answers each one" | blob 80bb4d1 received 33 dispositions (HARVESTS 20260915). Benches STILL-OPEN: owner-escalation (K2, AD1, AD6), dispatch-preflight (K9), alternate-key (U1), owner-authority (AD3, AD4, AD6), meter-telemetry (AD8), AD11 F17 comparison; EVIDENCE-NOW: reviewer-receipt (AD10; historical distribution WITHDRAWN), AD11 format; WITHDRAWN: recovery coordinator (AD14; F19 closed through the live driver, L528) | PROOF: a routed bench unanswered here

P:code subject-identity | FRICTION | "git tree OID of the candidate commit as it will be delivered" | 3 of 7 subjects are gitignored runtime files identified by a sums-file sha256 (F30e, KR-WALFREEZE) or a candidate-file sha256 (KR-WALHARM; its D record holds 8-hex prefixes). Cost: three identity grammars; one digest recovered from the file, not the record | REPLACES: "a key on a different tree does not transfer" -> "a key on a different tree does not transfer. A register-permitted subject outside git is identified by a runtime manifest (its K3 artifact set): per target file in path order, register-relative path, sha256 of candidate bytes, sha256 of expected pre-state bytes; identity = K3's digest over those; records hold full digests, prefixes are locators" | PROOF: a runtime Table S identity a stranger recomputes to a different digest

P:code artifact-store | FRICTION | "git (shared checkout or worktrees); build outputs are not the subject" | the runtime subjects (KERNEL.md twice, the Claude lane driver) and their candidates live under gitignored `.claude-state/`; D F30e names a banked pre-install backup, D KR-WALFREEZE none. Cost: KR-WALFREEZE's pre-state B76BDC57 survives as a hash only | REPLACES: "build outputs are not the subject" -> "build outputs are not the subject. A register-permitted runtime subject's store is the evidence directory its decision record names, holding candidate, manifest and pre-state bytes, each digest recorded, readable by a verifier who wrote none of them" | PROOF: a runtime Table S subject whose pre-state bytes cannot be produced

P:code delivery-target | FRICTION | "integration branch via the project's landing path" | three runtime installs, three safeguard sets (D records): F30e copy-over, backup, parse check, rollback described; KR-WALFREEZE pre/post sha, no backup; KR-WALHARM pre-sha assert, read-back. None rehearsed its reversal (F20g's, L519, never installed). Cost: safeguards re-derived per install, none reversible on evidence | REPLACES: "review branches push (R7)" -> "review branches push (R7). A register-permitted runtime subject delivers to its manifest's files as one transaction: pre-state digests asserted, pre-state bytes banked, candidate written, post digests read back, all recorded; the reversal is rehearsed once on a copy first" | PROOF: a Table S runtime install recorded without a pre-state assert or post read-back

P:code acceptance-evidence | FRICTION | "run at the exact commit and declared environment" | runtime subjects have no commit; acceptance ran at a sums-file digest. D F30f (bytes unchanged since F30b r2) drew a new SOL test-depth finding in each of 6 rounds; F20e and F30e, bars frozen before review (D LINEAGE-20260917), adopted in round 1; D KR-WALHARM `procedureNote` names a bar differing from the procedure applied. Cost: 6 rounds on one unchanged candidate | REPLACES: "run at the exact commit and declared environment, including interpreter and TEMP/TMP where applicable (for example N identical green runs), executed or authenticated" -> "run at the exact subject identity (commit, or runtime manifest digest) and declared environment, including interpreter and TEMP/TMP where applicable (for example N identical green runs), executed or authenticated. The acceptance contract (arms, mutation classes, round budget, the rule closing a round) is digest-bound before round one and judges every round; a finding outside it opens a follow-up, not a block; no contract suppresses a breach of a binding invariant" | PROOF: a window subject accepted against a contract digest-bound after its first round

P:code independent-key | FRICTION | "a verifier from another model family (R3)" | all 7 acceptances carry a gpt-5.6-sol key. Cost (extension): KR4-FILE parked at round 2 when SOL declined to key lines its park record calls Astra-close (D KR4-FILE; L560); one successor card; two Codex rounds on the parked draft, 0.52 USD | REPLACES: "a verifier from another model family (R3), a CI runner the producer does not control, or an attended human verifier other than the producer named by the register" -> "a verifier from another model family (R3) whose class has not become a producer of the subject, a CI runner the producer does not control, or an attended human verifier other than the producer named by the register" | PROOF: a subject keyed by a class whose design it adopted

P:code resource-terminals | FIT | "parked work names its resume condition and the actor who can satisfy it" | the billing block is typed owner-only and no DONE flip was taken (L543) | PROOF: a DONE flip without post-merge CI

P:code human-gates | INSTANCE-FAILURE | "names an owner-facing escalation channel" | no channel for the F30e re-bless (K2); packet/KERNEL.md lists no provider-tier approval, yet L551 names one on Astra (09-08) | PROOF: a register entry and channel for both gates

P:code budgets | FRICTION | "review rounds also report dispositions completed and subject changes, including zero" | (N2) L500: a 1:1 throughput line hid a 24 h stall with 1 product commit (cost: a day); local fix Get-BoardState 217B4EAF -> 8EC09508 | REPLACES: "including zero" -> "including zero, and per window the subjects accepted, delivered, parked and closed undelivered, with age and blocker for accepted undelivered work; commit and path counts are supplementary" | PROOF: a window whose outcome counts read healthy while nothing delivered

P:code claims | INSTANCE-FAILURE | "leases name the subject, owner, expiry and owned processes" | 7 CLAIMED events in L500–L556 name card and session id only (L510, L535, L539), never an expiry or owned process. Single claimant held: two sessions read a live claim and deferred (L554, L556) | PROOF: a window claim record naming expiry and owned processes

P:code determinism-class | FIT | "flaky suites are declared per test, never silently retried" | P-0b (D P-0b): flake not reproduced by repetition (10/10 green at base); cause shown by probe (90/300 identical mtimes, 0/300 backdated), fix by 10/10 green at 35d82c9; the third failure named per test, carded P-0b-trig, no repro, parked unfixed (L553); F19r round 2 read a 48/1 re-run as "not reproducible", not a pass (D F19r) | PROOF: a window acceptance counting a rerun with no named cause

P:code dispatch-preflight | FRICTION | "the spending tool runs the project's resume gate before dispatch" | hub 8b82e3d8 resumed on a KERNEL view KR-WALHARM had replaced and stood down without installing (L551); cost: one hub session forgone | REPLACES: "retains its result" -> "retains its result; the gate fails when the register digest the session holds differs from the register on disk" | PROOF: a dispatch recorded under a KERNEL sha that differs from the live file

## Findings

**N1 — A bounded lineage ruling stopped the successor loop** (kernel-candidate, K5; §5). D KR-CONVERGE: 14 parks to 3 adoptions on 09-16, successors repeating (F30 x6, F20a x3, F29 x3); after the owner ruling (L507), L509–L556: 7 adoptions, 6 parks. Repetition stopped; acceptance and delivery did not improve. Candidate text: *Before its first review a subject records its acceptance contract and the rounds it and any renamed successor may spend. When spent, a register-named adjudicator writes CLOSE, NARROW or CONTINUE with reasons, surviving findings and any further finite budget; that record accepts, installs and publishes nothing and removes no key.*

**N3 — One named freeze exception delivered; the two beside it were unusable as written.** D KR-WALFREEZE names three start-only exceptions: P-16-A6, P-16-A7 (exact-path manifest, effect exclusions) and F30e. F30e installed twelve minutes later (L515, L517); P-16-A6 stopped at the manifest step (L518): the defect sits in repo-root `wake_codex.ps1`, outside the exception's paths, with possible excluded lane-driver or auth effects, and A7 targets the same file. Nobody walked the manifests before the 4/4 ratification. Lesson: test each named task's files and effects against every kept restriction before ratifying an exception, recording per task whether a path exists.

**N4 — A model tier went unused for two separate reasons** (kernel-candidate, K2; §5). Unverified: L551 measures 0 ASTRA receipts ever (SOL 135) and blames a 09-08 owner instruction to ask before spending Astra, absent from packet/KERNEL.md: under K2 the spend was autonomous, yet sessions honoured the unregistered gate, and the superseding D OWNER-RULING-KR-FLEETKERNEL is still not a register line. Measured: Set-LaneCeiling.ps1:88 refused the unpriced ASTRA lane (L555; packet/RECEIPTS-AND-LANE-CEILING.md); one line fixed it (packet/LANE-BUDGET-ASTRA-RATE.md); the first Astra run followed within a minute (L557). Candidate text: *An approval the owner has reserved stays required when the register or a record omits it; the omission is a register defect filed that turn, never a grant. Work no register line and no owner instruction reserves is autonomous (K2); a missing entry is not a prohibition. Per provider tier, report runs eligible, requested, refused by instance, refused by provider and completed, so an unused tier is a number.*

**N5 — Independence exhausted with two classes; two runtime refusals** (extension: L557–L560, D KR4-FILE, packet/ASTRA-CAPACITY-REFUSAL.md). Evidence, test, text: P:code independent-key; every Claude reviewer shares the author's class, so both classes were spent on one subject (remedy: Authorship). Refusals: the unpriced ASTRA lane failed dispatch closed (N4); after pricing, ASTRA-20260917-102129-346 died in 8 s on "Selected model is at capacity" (exit 1, NO VERDICT; K4 held) and the hub parked and carded the successor (K8). Differs from the REJECTED proposal: no extra class unless a merge happened.

## Untested

- K6: whether "other than the producer's" should read "other than every producer's" under the material-contribution test (§5). PROOF: two profiles filing the same exhaustion.
- N5, for the steward: does a reviewer's class become a producer's when the candidate adopts that reviewer's design in any words, a corrected fact, count, citation or phrasing aside? PROOF: two profiles hitting the same independence exhaustion.

## Authorship

Round 2 (method in PROVENANCE): a fresh Claude (Fable) author wrote every line; reviewer output reached it only as the hub's concept-only defect list (packet/ROUND2-DEFECTS-HUB.md). Round 3 withdraws by name round 2's "a codex key covers all of it": through that list the Codex reviewers (SOL, ASTRA) materially contributed the designs at r2 lines 53-61 and 81-83. A Codex key covers the other lines and the accuracy of this disclosure (K11).
