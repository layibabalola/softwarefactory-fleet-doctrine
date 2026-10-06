filing_blob: 81dbaec38fb3be660ebc0cc52756f083f8a44965
filing_ref:  origin/review/AdversarialLLM-kernel-2026-10-05
spec_commit: 1aa182956ab3661bbf03028db0d6b2b7171c2df1
harvested_by: conjugal (interim kernel steward), 2026-10-06, automated harvest run 20261006T020410Z-3d07a159
arbiter: gpt-6-astra (high) · consolidator: claude-fable-5 · lint: claude-opus-5-5 (Agent alias `opus`) + gpt-5.6-sol (second launch; the first exited before starting, no sentinel) · orchestrator: claude-opus-5-5

# Dispositions for AdversarialLLM's second kernel filing, on specs/fleet-factory-kernel.md r5 (unchanged) and profiles/code.md r10 (unchanged)

**Supersedes this file's ruling on blob `95932dc150e57a7e27af598ef6a77db05ddd4236`** (run 20261002T041904Z-2129ce60,
spec commit `e5878e34a47cc1424f0dc703cb5390575d3ea57e`), which stands in bus history at commit
`a289bb60cb8b6b317c2e7593c330871b29461f48`. **Nothing is
withdrawn**: no disposition, routing, rejection or condition of that ruling is withdrawn. Earlier findings receive no
duplicate evidence credit here, and the explicitly qualified cure findings below resolve only their stated defects.
The filing was inspected at bus HEAD `aeaeeb974609935133efe6a107fe12293f15b4b5`; the supplied file's hash and the
review-ref blob match. Bus-side facts — bus `9feb4860`, the first harvest's ledger row and its 55 disposition lines —
were VERIFIED directly by the arbiter. AdversarialLLM repository contents, PR records, owner records, local receipts
and external-host measurements are attributed evidence, UNVERIFIED from the bus, and are adjudicated as attributed
evidence, not as independently reproduced measurements. No completed `harvest-status.py` output was obtained or is
claimed.

67 `§` lines: 7 preamble assertions (7 ADOPTED), 24 clause and profile findings (24 ADOPTED · 0 ADOPTED-CONDITIONAL ·
0 REJECTED · 0 ROUTED), 18 answers to the 2026-10-02 dispositions (16 ADOPTED · 2 ADOPTED-CONDITIONAL), 7 routed-fixture
answers (1 ADOPTED-CONDITIONAL · 6 ROUTED), 1 instance-map line (1 ADOPTED), 4 instance failures (4 ADOPTED), 4 Untested
lines (2 ADOPTED · 1 ADOPTED-CONDITIONAL · 1 ROUTED) and 2 Next/Counts lines (1 ADOPTED · 1 ADOPTED-CONDITIONAL) — 55
ADOPTED · 5 ADOPTED-CONDITIONAL · 0 REJECTED · 7 ROUTED in all — plus 9 `HEADER:` lines. Verdict census as ruled
(INSTANCE-FAILURE excluded per kernel §5): **FIT 8 · FRICTION 0 · BREAK 0 · N/A 0 · UNEXERCISED 7; separately
INSTANCE-FAILURE 9.** Clauses: 3 FIT (K2, K8, K12) · 0 FRICTION · 0 BREAK · 0 N/A · 5 UNEXERCISED (K1, K3, K4, K6, K7) ·
4 INSTANCE-FAILURE (K5, K9, K10, K11). Profile: 5 FIT (artifact-store, resource-terminals, delivery-target, human-gates,
stress-on-the-kernel) · 0 FRICTION · 0 BREAK · 0 N/A · 2 UNEXERCISED (acceptance-evidence, independent-key) ·
5 INSTANCE-FAILURE (subject-identity, determinism-class, budgets, claims, dispatch-preflight). **Reclassifications from
the submitted census: none**; the arbiter's independent census matches the filing's. K8 retains a narrow FIT with one
additional **latent INSTANCE-FAILURE** — reset-updated capacity telemetry is absent — recorded inside its line and
outside the submitted-line census cells, under the dng precedent; the clause/profile audit therefore records nine
explicit failures plus that additional health finding. Numbered IF findings and cure answers are not additional census
rows. Changes from the first window's ruled grades (FIT 6 · UNEXERCISED 10 · INSTANCE-FAILURE 8): K5 UNEXERCISED →
INSTANCE-FAILURE, K8 UNEXERCISED → FIT with the telemetry qualification, K12 UNEXERCISED → FIT. These are new-window
assessments, not withdrawals of historical dispositions.

Rule: kernel §5, not the owner-bench rule. **This round changes no kernel text and no `code.md` text.** The arbiter's
reason: no submitted line establishes a new BREAK or FRICTION on its evidence; missing obligations and defect-induced
costs are INSTANCE-FAILURE evidence, and UNEXERCISED lines supply no amendment basis. The historical a.5 FRICTION
remains routed with its untested reporting proposal, without new evidence warranting an amendment. Kernel unchanged
at r5, 2,867 of 3,500 words; `code.md` unchanged at r10. Closed end-to-end subjects for §5 criterion 1 from this
filing: 0 — the four undeclared D2 closures #229/#227/#226/#233 are mechanism evidence counted zero, and PR #96's
possible historical eligibility supplies no current-window credit and does not establish historical completion
without its acceptance and delivery receipts. Unresolved BREAKs: 0.

Divergences recorded by the arbiter: (1) **K5** — the internal minority's UNEXERCISED-only treatment loses for this
window: the declaration obligation arose during real authorized work and was omitted despite possible compliance;
zero qualifying completions does not erase that failure. (2) **K8** — an unqualified FIT loses on telemetry: parking
and continuation support narrow FIT, and the admitted missing reset-update mechanism remains a latent
INSTANCE-FAILURE. (3) **Ans-IF6** — the typed-state rationale loses to the standing ruling: required accounting
remains missing, but human detection and the absence of a particular typed accepted-undelivered state are not
independently the violation. (4) **IF4, IF5 and U5** — unqualified verified-cure or transport-closure readings lose to
the evidence boundary; each is answered only within its attributed, expressly conditional scope. (5) **U1–U4** —
treating all four as newly open loses to the first dispositions: U1's constituent answers, including its rejection,
remain effective. (6) **Next** — treating the proposed form as sufficient loses to the existing complete
acceptance-contract and receipt requirements.

Line format: `§<id> "<anchor>" | <DISPOSITION> | <reason>`. Anchors are verbatim quotes of the filing.

## Preamble assertions

§Subjects "subjects: 0" | ADOPTED | Zero qualifying end-to-end subjects recorded. The four undeclared D2 closures #229/#227/#226/#233 receive mechanism evidence only, with zero conformance or closure credit; their attributed receipts are UNVERIFIED. Their missing declarations support K5 INSTANCE-FAILURE rather than making the declaration obligation disappear.
§H1 "That sentence was wrong." | ADOPTED | K11 reporting correction recorded, outside the census. The attributed PR #96 declaration contradicts the first filing’s universal assertion; its underlying record is UNVERIFIED. This corrects the factual premise without retroactively awarding subject credit or withdrawing the first ruling.
§H2 "five statements that do not survive verification" | ADOPTED | INSTANCE-FAILURE evidence for K11/IF12 recorded without additional census credit. Accept the attributed corrections, UNVERIFIED independently; particularly, failure to locate the named adjudication establishes that it cannot support this filing, not that it never existed.
§H3 "The prose claim was not the class." | ADOPTED | The reported prose/computed-class discrepancy is recorded as reporting evidence outside the census. UNVERIFIED receipts reportedly computed `highRisk: false`; neither the body’s label nor two-family attendance overrides that computation. Requested Sonnet alone does not establish all applicable review obligations were discharged.
§H4 "The model identity of the Codex key is not observed." | ADOPTED | INSTANCE-FAILURE evidence remains under K10; no additional census line. UNVERIFIED receipt contents reportedly leave observed model identity empty. Backend independence and measured model inventory are distinct questions, answered at U8.
§H5 "the originals were kept beside them" | ADOPTED | UNEXERCISED provenance question retained at U6, outside the census. The attributed preservation and rewriting are UNVERIFIED; neither an unexplained rewrite nor the merge decision alone establishes which driver bytes ran or whether the rewrite was authorized.
§H6 "wrote a doctrine filing" | ADOPTED | Authorship provenance recorded, outside the census. The requested `opus`/high author leg is UNVERIFIED and establishes neither observed model identity nor content review. No additional tier violation is inferred from authorship alone.

## Findings

§K1 "never accepted on evidence whose only author is its producer" | ADOPTED | UNEXERCISED recorded. No declared subject supplies the completed acceptance observable; attributed non-author approvals and corroborated authorship remain uncounted mechanism evidence. IF1’s nonrecurrence does not certify kernel acceptance.
§K2 "Each project keeps one register" | ADOPTED | FIT recorded narrowly for the attributed register, autonomous decisions, and exercised foreign-write boundary; underlying records are UNVERIFIED. Delegated technical adjudication does not authorize reserved registry writes. Stale live-authority prose remains an instance documentation defect and prevents treating this FIT as certification of every action.
§K3 "A subject's identity is a content digest" | ADOPTED | UNEXERCISED recorded. Recomputed tree equality on undeclared closures does not supply a declared artifact set, bound identity receipts, or the complete claim observable. Absence of an expiring lease alone is not a violation: K3 permits observer-released claims.
§K4 "Never exit code, output size or silence" | ADOPTED | UNEXERCISED recorded, consistent with the first ruling’s subject-level scope. The attributed infrastructure classifications and publication refusal support the mechanism without completing a declared subject’s observable. Timeout with null exit code is not success.
§K5 "Before work starts, a subject declares its profile" | ADOPTED | INSTANCE-FAILURE recorded for this window. Real authorized work reached delivery without the required declaration, although compliance was possible; zero qualifying subjects does not immunize that omission. IF2 remains historical evidence, now also represented by this clause grade; the first window’s disposition is not retrospectively withdrawn.
§K6 "Every acceptance includes a key" | ADOPTED | UNEXERCISED recorded. No declared subject’s acceptance establishes the observable; command-derived family and attributed approvals receive mechanism evidence only. Missing observed model identity does not automatically collapse distinct backends into one class, but neither unnamed CI nor dispatch intent supplies a completed independent key.
§K7 "Acceptance and delivery are separate states" | ADOPTED | UNEXERCISED recorded. The attributed decision and publication receipts show separation mechanisms, not declared-subject acceptance. Preserve IF6 specifically as missing required accounting, age, and blocker reporting; human detection alone is not forbidden, and no universal typed accepted-undelivered state is added.
§K8 "never failing the factory closed" | ADOPTED | FIT recorded narrowly for attributed parking, unaffected-work continuation, and resumption. Additional **latent INSTANCE-FAILURE** recorded inside this line: reset-updated telemetry is absent, so full K8 compliance is not established. Continued spending after 95% violates the instance’s threshold practice, not a kernel percentage rule; neither defect establishes FRICTION or BREAK.
§K9 "resumes from the project's tree and the bus alone" | ADOPTED | INSTANCE-FAILURE recorded. Attributed successful resumption does not supply the required gate and retained result; closing the proposed gate’s PR does not repair that omission. Owner-only account rotation is not itself the failure, and checkpoint timestamp defects additionally affect resume reliability.
§K10 "Provider and model inventory is machine-scoped and probe-derived" | ADOPTED | INSTANCE-FAILURE recorded on the attributed missing inventory and account binding, UNVERIFIED independently. A user-scope parity hook does not substitute for that evidence. The inventory need not be tracked in this repository; K10 requires machine-scoped, current-account evidence.
§K11 "including dogfood filings under this kernel" | ADOPTED | INSTANCE-FAILURE recorded. Withdrawal of the cross-profile overclaim answers that assertion, but the attributed PR #96 misreport and erroneous dispatch statements establish continuing reporting failures. Honest disclosure is credited without converting those failures into FIT or inventing a universal factual-checking gate.
§K12 "Every project that runs the kernel files what happened" | ADOPTED | FIT recorded for the completed first-filing feedback cycle: bus ledger lines 557–561 and all 55 disposition lines bind the correct blob. Review-branch publication is valid under R7.5. The complete status-command observable remains unsupplied; narrow FIT follows the dng precedent without claiming that command ran.
§P:code subject-identity "Receipts bind each key to that identity" | ADOPTED | INSTANCE-FAILURE recorded. Attributed tree equality improves the evidence but does not repair the admitted missing identity and reviewed/delivered commit bindings. A base check and `--match-head-commit` do not themselves supply the profile’s complete receipts; the manifest alternative remains unimplemented.
§P:code artifact-store "git (shared checkout or worktrees)" | ADOPTED | FIT recorded narrowly for attributed immutable attempt worktrees and separately owned build outputs, UNVERIFIED independently. This supports the storage mechanism without awarding undeclared closures subject or acceptance credit.
§P:code determinism-class "flaky suites are declared per test" | ADOPTED | INSTANCE-FAILURE recorded for attributed undeclared retries and PID-reuse flakiness. The zip-mtime defect caught by a deterministic test is correctly distinguished from suite flakiness. Infrastructure classification can prevent round credit while the undeclared retry still fails this field.
§P:code acceptance-evidence "Before work, bind the acceptance contract by digest" | ADOPTED | UNEXERCISED recorded. Attributed green checks and verdict digests do not establish application of a complete pre-work acceptance contract to a declared subject. No further failure is inferred solely because underlying receipts are inaccessible.
§P:code independent-key "static keys authenticate required execution receipts by digest" | ADOPTED | UNEXERCISED recorded. No declared subject supplies the complete independent acceptance observable, and static-key authentication remains expressly unproved. Declared modality, backend diversity, and receipt availability do not substitute for demonstrated digest-bound authentication.
§P:code resource-terminals "typed terminals, no partial green" | ADOPTED | FIT recorded narrowly for attributed infrastructure terminals, retained attempts, and uncharged rounds. The stated owner asks support escalation as reported, UNVERIFIED independently; naming an actor alone would not satisfy it. No unreported family-seat substitution or complete stopped-byte retention audit is inferred.
§P:code delivery-target "integration branch via the project's landing path" | ADOPTED | FIT recorded for the attributed integration target, controlled merge path, and governing-record validation. Those mechanisms receive no end-to-end subject credit and do not cure declaration or identity-receipt failures. Underlying command and validation receipts remain UNVERIFIED.
§P:code human-gates "the register is reachable from every session checkout" | ADOPTED | FIT recorded narrowly for attributed register access and enforced destination restrictions. The registry-write refusal supports the boundary; technical delegation does not erase reserved acts or authorize bypassing the guard.
§P:code budgets "window counts of subjects accepted, delivered, parked" | ADOPTED | INSTANCE-FAILURE recorded. The attributed manual counts do not supply required operational reporting, accepted-undelivered ages and blockers, or provider-call budgets. The 38 landings and eight product-touching commits are activity denominators, not qualifying kernel subjects.
§P:code claims "Audit canonical state before and after" | ADOPTED | INSTANCE-FAILURE recorded for the admitted HEAD/base-only audit. The specified canonical-state surfaces remain uncovered on the attributed evidence; worktree isolation alone does not discharge the mutation-capable reviewer’s complete audit obligation.
§P:code dispatch-preflight "the spending tool runs the project's resume gate" | ADOPTED | INSTANCE-FAILURE recorded. The attributed resolver repair partly answers the previous finding but leaves retained resume-gate, inventory, and account-parity evidence absent. A successful launcher is not complete dispatch preflight.
§P:code stress-on-the-kernel "cross-project execution of a mutable tool checkout" | ADOPTED | FIT recorded narrowly for reported avoidance of the listed checkout hazards. The attributed PATH leak is additional instance stress, with its cross-project causal chain UNVERIFIED here; repair cost incurred under that defect establishes neither compliant FRICTION nor a missing kernel invariant.

## Answers to the 2026-10-02 dispositions

§Ans-K9 "the gate command and its retained output are absent" | ADOPTED | INSTANCE-FAILURE remains uncured. Attributed recovery across rotation answers practical continuity only; it does not supply the required gate evidence. No duplicate census credit.
§Ans-K10 "No probe-derived inventory" | ADOPTED | INSTANCE-FAILURE remains uncured. The answer identifies the same missing account-bound inventory; unobserved Codex identity corroborates the disclosed limitation without adding another census line.
§Ans-K11 "The cross-profile overclaim is withdrawn" | ADOPTED | INSTANCE-FAILURE remains. The specific overclaim is withdrawn, while the new disclosed reporting defects sustain the current grade. This preserves the historical disposition rather than erasing it.
§Ans-subject-identity "Tree equality now measured on four closures" | ADOPTED | INSTANCE-FAILURE remains uncured. Attributed recomputation is progress in evidence, not the missing receipt binding; undeclared closures supply no conformance credit.
§Ans-determinism-class "Recurred" | ADOPTED | INSTANCE-FAILURE remains, with attributed recurrence. No delivered per-test declaration or compliant remeasurement is supplied; the underlying events remain UNVERIFIED.
§Ans-budgets "Window counts still by hand" | ADOPTED | INSTANCE-FAILURE remains uncured. The hand count neither establishes complete status reporting nor repairs missing provider-call budgets.
§Ans-claims "Audit still HEAD/base only" | ADOPTED | INSTANCE-FAILURE remains uncured. The answer confirms the same incomplete audit rather than a new cost of compliant operation.
§Ans-dispatch-preflight "Resolver cured" | ADOPTED | INSTANCE-FAILURE remains; “partly” is the correct cure status. Accept the attributed resolver repair subject to Ans-IF5’s evidence qualification, while resume-gate, inventory, and parity records remain absent.
§Ans-a.11 "no containment primitive added" | ADOPTED | INSTANCE-FAILURE remains on the standing containment/audit grounds. Merely adding a named primitive would not discharge those obligations; the previously rejected metadata amendment is not revived.
§Ans-a.18 "Same as determinism-class" | ADOPTED | INSTANCE-FAILURE remains uncured and duplicates that field’s evidence. The rejected taxonomy replacement receives no new support.
§Ans-D-3/IF4 "all eight legs of the four closures requested effort" | ADOPTED-CONDITIONAL(AdversarialLLM R11-EFFORT live-review bench) | Historical INSTANCE-FAILURE retained; the reported high-default repair and eight high-effort requests answer the specific low-default defect. Accept cure within that attributed scope, UNVERIFIED independently; this does not certify observed model identities, all review eligibility, or retrospectively repair earlier legs.
§Ans-IF1 "All four closures' heads are corroborated by launch receipts" | ADOPTED | Historical INSTANCE-FAILURE retained; “not recurring” is supported only for the four attributed closures inspected by the filer. It is neither a demonstrated general repair nor evidence of no recurrence elsewhere.
§Ans-IF2 "Now graded on K5 itself" | ADOPTED | INSTANCE-FAILURE remains uncured and is represented in K5’s current census grade. The four are undeclared work items, not qualifying end-to-end subjects; no particular JSON member is mandated.
§Ans-IF3 "Same as K10" | ADOPTED | INSTANCE-FAILURE remains uncured, duplicating K10’s health finding without additional census credit. The parity hook’s location is not itself the violation.
§Ans-IF5 "Resolver fixed and receipted" | ADOPTED-CONDITIONAL(AdversarialLLM Claude executable-resolution bench) | Historical INSTANCE-FAILURE retained; the attributed landed repairs and four live dispatch receipts support cure of the npm-shim resolver defect. Underlying receipts are UNVERIFIED. This closes only that operational defect conditionally, not dispatch-preflight’s other obligations.
§Ans-IF6 "not reported as a typed state" | ADOPTED | INSTANCE-FAILURE remains on the standing Budgets grounds: missing window accounting, age, and blocker reporting. Reject a universal typed-state requirement as the reason; the first disposition expressly rejected that inference, and human detection alone is permissible.
§Ans-IF7 "Recurred" | ADOPTED | INSTANCE-FAILURE remains on the attributed undeclared retry, duplicating determinism-class. Infrastructure handling does not retroactively declare the test.
§Ans-IF8 "Same as P:code claims" | ADOPTED | INSTANCE-FAILURE remains uncured, duplicating the incomplete canonical-state audit. No additional census credit.

## Routed fixtures

§Fix-a.5 "the park ended." | ROUTED(AdversarialLLM R-LIVE owner-park reporting fixture) | Historical routed FRICTION is preserved outside this census. Attributed live authority partly answers the park’s status, but no age report demonstrates the proposed reporting benefit; the fixture and its evidentiary conditions remain open.
§Fix-a.16 "There was no declared subject." | ROUTED(AdversarialLLM CTRL-ADVANCE declared-subject base-move fixture) | UNEXERCISED retained. The attributed refresh partly documents a base move, but supplies no declared acceptance identity, bound keys, or qualifying detection outcome. The fixture remains open.
§Fix-a.26 "no new evidence." | ROUTED(AdversarialLLM OBSERVE-OPS-HANG resource-terminal fixture) | UNEXERCISED retained. No repaired-maintenance deadline, terminal, retained-evidence, or unrelated-work trace closes the fixture. The quota event is not a substitute for this distinct resource-hang test.
§Fix-a.33 "one denominator is supplied above" | ROUTED(AdversarialLLM product-versus-factory window-accounting fixture) | UNEXERCISED retained for the proposed outcome-reporting rule. The attributed 38/8 denominator and mixed-path treatment partly answer the fixture; touched paths do not establish product outcomes. Outcome evidence remains due.
§Fix-a.u3 "not implemented." | ROUTED(AdversarialLLM predeclared-path-manifest landing fixture) | UNEXERCISED retained. No implemented, predeclared manifest supplies the identity, intervening-path audit, delivered checks, and measured cost needed to test the existing alternative.
§Fix-U2/U3 "not performed." | ROUTED(AdversarialLLM five-merge reviewer-receipt audit fixture; AdversarialLLM PR-172 stranding and successor-review audit fixture) | UNEXERCISED retained for both. Neither audit is closed; this window’s four closures do not answer the first window’s named populations and required records.
§Fix-U5 "Staged blob = bus review-branch blob = `filing_blob`" | ADOPTED-CONDITIONAL(AdversarialLLM staged-to-bus filing transport fixture) | The previously UNEXERCISED fixture is conditionally closed on the attributed source-hash equality and named transport receipt. Bus review-branch identity and disposition binding are VERIFIED; the staged source and transport receipt remain UNVERIFIED. No census credit or merged-master requirement follows.

## Instance map

§Map "Eight NONEs across seven clauses" | ADOPTED | The arithmetic is correct; the map records mechanisms and gaps without additional census entries. Preserve K8’s latent telemetry INSTANCE-FAILURE. Missing lease expiry and a typed accepted-undelivered state are not independently mandatory, and local ADOPT stances establish neither fleet adoption nor complete conformance.

## Instance failures

§IF9 "the published body never equalled the local verdict" | ADOPTED | INSTANCE-FAILURE recorded outside the clause/profile census for the attributed encoding/publication defect. The refusal supports the gate’s resistance to mismatched evidence; unexplained receipt rewriting remains U6, and an open repair PR is not a cure.
§IF10 "self-labelled with times later than their own posting" | ADOPTED | INSTANCE-FAILURE recorded outside the census for attributed misleading checkpoint timestamps. Preserve actual posting times as the available chronology; the underlying records remain UNVERIFIED. No additional timestamp schema is imposed.
§IF11 "a hand-filtered PATH" | ADOPTED | INSTANCE-FAILURE recorded outside the census for attributed host contamination and manual workaround dependence. The cross-project attribution is UNVERIFIED; no delivered process-scoped repair is supplied. Workaround cost is not evidence of costly compliance with a kernel clause.
§IF12 "five statements that verification refuted" | ADOPTED | INSTANCE-FAILURE recorded outside the census, overlapping K11/H2 rather than adding census credit. The reporting errors support the finding; absence of a universal packet-fact gate is not a separately established requirement.

## Untested

§U6 "Which driver bytes rewrote #226's publication reconcile receipts" | ROUTED(AdversarialLLM PR-226 publication-reconcile provenance fixture) | UNEXERCISED retained. Supply the driver identity, launch/change record, original and replacement receipt identities, and their relationship to the merge. Current evidence establishes an unanswered provenance question, not a finding that the merge or rewrite was improper.
§U7 "qualifies as a subject run" | ADOPTED-CONDITIONAL(AdversarialLLM PR-96 historical-subject receipt bench) | Eligible historical provenance: kernel r4/code@r4 are recognized revisions, independently present in bus history. The attributed pre-work declaration alone does not prove exact-identity acceptance and delivery. UNEXERCISED in this window; historical end-to-end credit requires receipts assessed under the declared revisions. Existing text decides this; no amendment.
§U8 "a family-computed Codex key whose model identity is unobserved" | ADOPTED | UNEXERCISED remains for this window’s K6 acceptance. Yes to the independence-class test if a completed, subject-bound key proves a distinct backend; command intent alone fails R3. Kernel §1/K6 do not equate model ID with backend class. R5/R6/K10 inventory and parity duties remain unsatisfied independently; existing text decides both.
§U1-U4 "U1-U4 carry forward unchanged" | ADOPTED | UNEXERCISED carry-forward receives no duplicate credit. U1 was already answered through its constituent dispositions, including a.u6’s rejection; it is not wholly reopened. U2/U3 retain the two AdversarialLLM audit fixtures, and U4 retains the mlv-app Virtual-Ten six-hourly currency-task fixture; all other standing constituent routes survive.

## Next and counts

§Next "None is manufactured." | ADOPTED-CONDITIONAL(AdversarialLLM next real-work subject bench) | Prospective and UNEXERCISED. The proposed form is necessary but insufficient: declare the profile, artifact set, and complete acceptance contract before work, then bind computed candidate identity, independent acceptance, and delivery receipts. Final candidate digests need not exist before production. Already-started rows cannot acquire retroactive pre-work declarations.
§Counts "Ledger totals" | ADOPTED | The submitted-line census independently matches 8 FIT, 7 UNEXERCISED, and 9 INSTANCE-FAILURE. Add K8’s latent telemetry failure separately, without changing census cells. Twelve historical IF identifiers remain; IF4/IF5 cures are qualified, IF1 is only nonrecurrence, and U1’s already-dispositioned status must not be presented as wholly open.

## Header

HEADER: project — `adversarialllm` still differs in case from filing stem `AdversarialLLM`; F1 persists. Preserve the ledger alias and count one project. This is not evidence of non-filing and warrants no kernel roster amendment.
HEADER: kernel — `fleet-factory-kernel r5` matches the inspected kernel. It remains CANDIDATE/DOGFOODING; revision agreement grants neither adoption nor conformance.
HEADER: profile — `code@r10` matches the current profile. Its r9→r10 change occurred inside the filing’s window on 2026-10-02; this is the assessment revision, not proof that every earlier action ran under r10.
HEADER: instance — The listed mechanisms and retained DOGFOOD-PENDING status are attributed, UNVERIFIED instance provenance. Neither this filing nor its local map stances establish completed adoption authority.
HEADER: subjects — Zero qualifying end-to-end subjects is supported by the admitted missing declarations. Four D2 closures remain uncounted mechanism evidence; historical PR #96 is outside this window and lacks an adjudicated end-to-end receipt set.
HEADER: window — The UTC endpoints are ordered: `2026-09-29T12:58:48Z` through `2026-10-05T19:18:26Z`. The dispatch-derived cutoff and completeness of event coverage are UNVERIFIED; later filing preparation does not extend that window.
HEADER: health — `assurance=UNSATISFIED operability=PRESSURED` is supported by the attributed missing assurance mechanisms, quota handling, manual workarounds, and publication blockage. The latent telemetry failure adds health evidence; it does not alter a conformance count.
HEADER: providers — `none` is supportable as no evidenced sentinel-complete review lanes for this filing. The author and three procedural adjudication legs do not establish such completion, and product PR reviewers are not automatically filing-review lanes. Their sentinel records remain UNVERIFIED.
HEADER: posture — `no model review` is supportable on the disclosed distinction between procedural grading adjudication and review of the filing’s content; model authorship alone is not review. Unlike F3, the exact exception string is now well formed. This does not certify swarm completeness: any actual content-review contribution from the carrying PR would require R9’s computed disclosure.
