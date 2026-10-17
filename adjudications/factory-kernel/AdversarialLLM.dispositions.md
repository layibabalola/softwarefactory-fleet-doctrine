filing_blob: 16259d89df03ad4effc8ea00c2b678b9319d9713
filing_ref:  origin/review/AdversarialLLM-kernel-2026-10-13
spec_commit: 9b26e44f30056c3c1d052f6b5859f9a5b2a86665
harvested_by: conjugal (interim kernel steward), 2026-10-17, automated harvest run 20261017T103430Z-1407b1ae
arbiter: gpt-6-astra (high, read-only) · consolidator: claude-fable-5 · lint: claude-opus-5-5 (Agent alias `opus`) + gpt-5.6-sol (high, read-only) · orchestrator: claude-opus-5-5

# Dispositions for AdversarialLLM's third kernel filing, on specs/fleet-factory-kernel.md r5 (unchanged) and profiles/code.md r11 (unchanged; subject declared r10)

**Supersedes this file's ruling on blob `81dbaec38fb3be660ebc0cc52756f083f8a44965`** (run 20261006T020410Z-3d07a159,
spec commit `1aa182956ab3661bbf03028db0d6b2b7171c2df1`), which stands in bus history at commit
`61b4698760c64b8ea603d4847b33ce328d15a27f`. **Nothing is withdrawn**: all 67 `§` dispositions and 9 `HEADER:` rulings
of that ruling survive unwithdrawn, including their conditions, rejections, routes and the first-filing (blob
`95932dc1`) rulings they preserved; this ruling supersedes blob coverage only and awards no duplicate historical
evidence credit. The filing was inspected at bus base `9b26e44f30056c3c1d052f6b5859f9a5b2a86665`; the supplied copy's
hash and the review-ref blob match. VERIFIED population before this run: 10 filings, open=2 (AdversarialLLM STALE,
conjugal STALE); this ruling covers only AdversarialLLM, and conjugal — the steward's own filing — remains outside
this run (kernel §5). Bus-side facts — the bus snapshot `8e1321b` and the eight card commits resolving there, `f0e1e9f`, `cos-feedback/adversarialllm/*`,
TRAPS 27901-27908, R12.3, the prior ledger row and its 67 disposition lines — were VERIFIED directly by the arbiter.
AdversarialLLM repository contents, receipts, PR records, owner records, model-execution and delivery facts are
attributed evidence, UNVERIFIED from the bus (that repository is not reachable on this machine), and are adjudicated
as attributed evidence, not as independently reproduced measurements.

23 `§` lines: 13 subject lines (11 ADOPTED · 1 ADOPTED-CONDITIONAL · 0 REJECTED · 1 ROUTED), 9 card dispositions (6
ADOPTED · 0 ADOPTED-CONDITIONAL · 1 REJECTED · 2 ROUTED) and 1 standing-fold line (1 ADOPTED) — 18 ADOPTED · 1
ADOPTED-CONDITIONAL · 1 REJECTED · 3 ROUTED in all — plus 10 `HEADER:` lines. Verdict census as ruled
(INSTANCE-FAILURE excluded per kernel §5): **FIT 0 · FRICTION 0 · BREAK 0 · N/A 0 · UNEXERCISED 0; separately
INSTANCE-FAILURE 1** (K5, ruled by the arbiter for this window and counted once toward health; 0 INSTANCE-FAILURE
lines submitted). **Reclassifications from the submitted census: none possible** — the filing submits no `K<n> |` and
no `P:code` verdict lines, so there is no submitted census; missing lines are not UNEXERCISED verdicts, the nine card
ADOPT/DISTINGUISH/N-A stances are not kernel census entries (a card N-A is not a kernel N/A), and the narrative
findings manufacture no clause or profile census rows. Historical failures ruled on the first and second filings are
preserved without recounting them here.

Rule: kernel §5, not the owner-bench rule. **This round changes no kernel text and no `code.md` text.** The arbiter's
reason: this filing establishes neither a concrete BREAK nor cross-profile FRICTION on its evidence; the K7 squash
question is decided by existing text (agent-bridge §W8-a/§Request already rejected a mandatory fast-forward rule,
and the §Request two-parent predicate is sufficient for its merge form, not a universal ancestry requirement), so no
spec amendment follows; the K5 timing and the header defects are instance and filing-shape findings, which supply no
amendment basis. Kernel unchanged at r5, 2,867 of 3,500 words (`6821c4c3`); `code.md` unchanged at r11 (`a31b27a7`).
The subject is graded against its declared `code@r10`, with the VERIFIED r10/r11 difference disclosed and a
corrected-shape re-filing against `code@r11` owed. Closed end-to-end subjects for §5 criterion 1 from this filing: 0 —
SLICE-1E-R and its replacement SLICE-1E-R2 (#264 closed, #268 squash `136e8bec`) are one examined work lineage whose
K5 declaration (PR body 2026-10-11T19:07:12Z) followed both the package commit (18:55:55Z) and the implementation
start (18:46:46Z), all ATTRIBUTED/UNVERIFIED; neither the replacement row nor the squash message cures that timing.
Unresolved BREAKs: 0.

Divergences recorded by the arbiter: (1) **K5** — FIT or UNEXERCISED loses to INSTANCE-FAILURE: real work started
before the declaration although timely declaration was possible, and replacement packaging cannot retroactively
satisfy "Before work starts". (2) **Squash identity** — automatic rejection of a tree-equal squash loses to the
profile's content identity (commit identity and delivered subject identity differ); conversely, automatic delivery
credit from tree equality loses to the requirement for a retained target-delivery witness. (3) **agent-bridge
two-parent predicate** — treating it as either satisfied by this squash or universally mandatory loses to its
expressly sufficient, case-specific scope; the squash needs its own delivery witness. (4) **F-01** — treating APPROVE
as disposing of every SHOULD loses to the bound acceptance contract: severity labels cannot waive binding
requirements, and out-of-contract findings require follow-ups. (5) **Review floor** — Adobe's Opus floor, or a new
kernel-steward floor, loses to R12.3's board-local declared floor. (6) **topbuilder hook** — treating a user-level
hook as irrelevant because it is outside the repository loses to runtime applicability: machine tooling can affect
that board. (7) **Profile revision** — retroactive `code@r11` grading loses to the subject's declared `code@r10`
contract. (8) **Census** — counting card stances, prose observables or missing lines as submitted verdicts loses to
the actual filing census: there are no `K<n> |` or `P:code` verdict lines.

Line format: `§<id> "<anchor>" | <DISPOSITION> | <reason>`. Anchors are verbatim quotes of the filing.

## Subject

§Identity "queue row order 444" | ADOPTED | Record SLICE-1E-R and its named replacement as one attributed work lineage, not two qualifying subjects. Queue identity, ownership and product scope are ATTRIBUTED/UNVERIFIED.
§Delivery-R2 "bounded, materially corrected single-commit replacement" | ADOPTED | Record the attributed closure of #264 and replacement through #268; inherited product bytes do not inherently disqualify a genuinely new, prospectively declared successor. The patch-id assertion is ATTRIBUTED/UNVERIFIED and corroborates patch equivalence, not complete subject identity or transferred acceptance.
§Queue-state "Queue state" | ADOPTED | Record the reported SUPERSEDED_DELIVERED derivation as an instance mechanism, ATTRIBUTED/UNVERIFIED. The filing expressly lacks the PR-body read needed to establish its named row-binding premise; the squash message alone does not independently verify that premise.
§K5 "The declaration followed the first implementation bytes." | ADOPTED | Rule K5 INSTANCE-FAILURE on the ATTRIBUTED/UNVERIFIED chronology: the 19:07:12Z declaration followed both the 18:55:55Z package commit and the 18:46:46Z implementation start. Neither a replacement row nor later inclusion in the squash message cures that failure, so SLICE-1E-R/R2 contributes zero qualifying closed end-to-end subjects.
§K1 "K1, separate implementer." | ADOPTED | Record the ATTRIBUTED/UNVERIFIED producer and acceptance provenance, including the independent Codex review addressed below. Same-family Claude production and merge authorship neither proves actor identity nor by itself violates role separation; the omitted a6 receipt cannot be credited as head authorship without evidence.
§K6 "The independent key is the Codex leg." | ADOPTED | On the ATTRIBUTED/UNVERIFIED receipt account, the completed Codex approval bound to `3a1ac9c6` supplies K6’s distinct-class observable against Claude production; the Claude approval is corroboration, not the independent key. This narrow answer supplies neither end-to-end credit nor proof of all code-profile requirements, including static-key authentication of required execution receipts, inventory and account parity.
§F-01 "That finding is open on master." | ROUTED(AdversarialLLM bound-contract and F-01 follow-up bench) | The open SHOULD and both APPROVEs are ATTRIBUTED/UNVERIFIED; an open SHOULD is compatible with acceptance only if the bound contract permits acceptance and no binding invariant is breached. If out of contract, it must open a follow-up; if it violates the contract or an invariant, APPROVE does not waive it, and this filing supplies neither a follow-up nor enough contract evidence to decide that classification.
§Gate "Local gate" | ADOPTED | Record the ATTRIBUTED/UNVERIFIED timeout as a resource terminal with zero partial credit, and the later GREEN and three successful checks as separate head-bound evidence. The later success does not convert the earlier timeout into a pass or establish complete acceptance by itself.
§K7 "Its parent is" | ADOPTED-CONDITIONAL(AdversarialLLM squash-landing witness bench) | A squash with parent equal to the reviewed base and full tree equal to the keyed tree is compatible with code@r10 identity despite lacking the keyed candidate as a parent; agent-bridge §Request’s two-parent predicate is sufficient for its merge form, not a universal ancestry requirement. Delivery credit additionally requires retained evidence linking the accepted identity to the authorized squash and witnessing that squash actually becoming the integration target’s tip; equality, containment and a terminal label alone are insufficient, and the asserted local receipts remain ATTRIBUTED/UNVERIFIED. VERIFIED bus `pr-268.md` names the reviewed head and a prospective merge-when-ci-green verdict, not the completed landing; no spec amendment follows.
§Honest-1 "is not a master tip." | ADOPTED | Preserve the ATTRIBUTED/UNVERIFIED distinction between keyed commit and landed squash. It neither automatically defeats tree-identity delivery nor proves delivery; §K7 controls.
§Honest-2 "The subject declared profile" | ADOPTED | Assess the subject under its ATTRIBUTED/UNVERIFIED code@r10 declaration, with the K5 timing failure retained. VERIFIED bus history shows r11 at `8e1321b`; its identity clarification does not justify silently substituting r11 for the declared revision.
§Honest-3 "This filing claims no K5 credit" | ADOPTED | Zero K5 credit is correct on the ATTRIBUTED/UNVERIFIED chronology, and the repeated disclosure adds no second failure count. The open F-01 remains routed under §F-01.
§Honest-4 "This is one filed subject and it is not counted." | ADOPTED | Record one examined lineage and zero qualifying completions on ATTRIBUTED/UNVERIFIED local evidence. This filing neither re-grades nor cures the earlier instance findings globally.

## Card dispositions

§Card-26f6a93 "mlv-app 26f6a93" | ADOPTED | The VERIFIED card supports measurement, load attribution and paired loaded-comparable claims without relaxing the quiet gate. Record the project’s ATTRIBUTED/UNVERIFIED adoption stance and reported starvation episode; queued work and a timeout do not establish delivery of that protocol.
§Card-00bbc29 "mlv-app 00bbc29" | ADOPTED | Record N-A as the project’s ATTRIBUTED/UNVERIFIED assertion that this shared-budget launch mechanism is absent. The VERIFIED card concerns reserving a child’s full timeout within a shared beat; separate admission and suite budgets are a relevant distinction, not a kernel N/A verdict.
§Card-2ca0fd2 "mlv-app 2ca0fd2" | ADOPTED | Record the ATTRIBUTED/UNVERIFIED, explicitly undelivered reservation proposal as a local response to the VERIFIED card. A temp-file-plus-hard-link reservation is not evidence that the card’s bounded replacement retries and safe rewriting obligations are implemented wherever existing state is replaced.
§Card-6020535 "mlv-app 6020535" | ADOPTED | The VERIFIED card expressly scopes its regression to 0.161.0 and later, records a passing 0.160.1 elevated control, and discloses the unelevated workaround’s isolation and egress limitations. The claimed 0.160.1 runtime therefore supports the distinction if accurate, while remaining ATTRIBUTED/UNVERIFIED; retaining NOT RUN for setup failures is consistent with the card and grants no blanket exemption after upgrades.
§Card-e426a45 "mlv-app e426a45" | ADOPTED | The VERIFIED card identifies an unimplemented proposal to the bus cli-currency owner, so record the project-local N-A stance on its ATTRIBUTED/UNVERIFIED absence of upgrade-smoke tooling. Its separate NOT RUN adoption is relevant but does not repair the bus smoke or establish that every runtime read succeeds.
§Card-b825b4f "topbuilder b825b4f" | ROUTED(AdversarialLLM machine-hook and review-access bench) | The VERIFIED card explicitly concerns a user-level guard, so its location outside this repository does not establish non-applicability: determine whether this board uses it and whether a reset wake survives a failed helper. Retaining enforced read-only review while rejecting access-only output as NOT RUN is a legitimate distinction from the card’s danger-full-access workaround, but successful runtime access and the claimed local mechanisms remain ATTRIBUTED/UNVERIFIED.
§Card-09b9cb5 "adobe-ingester 09b9cb5" | ADOPTED | The VERIFIED commit contains three separate cards; record the ATTRIBUTED/UNVERIFIED adoption grounded specifically in fixing self-tripping gates at their source. Diagnostic product/control work and a held CLI-pin row do not establish completed adoption of the other two cards.
§Card-f4b8a49 "adobe-ingester f4b8a49" | ROUTED(AdversarialLLM board hub and runtime-contract authority) | VERIFIED R12.3 makes each board’s own declared runtime floor govern, and the VERIFIED Adobe card declares Adobe’s floor only; the bounded-tier distinction is therefore sound in principle. Route validation of AdversarialLLM’s ATTRIBUTED/UNVERIFIED operative floor and actual review seats to its board authority, with any unresolved binding-doctrine conflict reserved to the owner; the kernel steward neither sets a replacement floor nor certifies those inaccessible records.
§Card-W5-W8 "agent-bridge W5-W8" | REJECTED(automatic delivery failure misreads the standing tree-identity ruling) | The VERIFIED trap’s fast-forward wording must be read with agent-bridge §W8-a/§Request, which rejected a mandatory fast-forward rule; a keyed commit never becoming master tip does not alone make tree-form delivery fail. Preserve the ATTRIBUTED/UNVERIFIED no-master-push restriction and receipt-attribution stance, but apply §K7’s squash witness requirement and §W8-b’s rule that a minimal K1/K6/K7 list cannot waive remaining kernel, profile or bound-contract obligations.

## Standing fold input

§Fold "is a standing fold input for this project." | ADOPTED | VERIFIED at `8e1321b`: the directory and all six named PR files exist, and `pr-268.md` names head `3a1ac9c6`, last changed by `f0e1e9f`. Record the standing read-and-disposition commitment; actual complete reads and closure of unanswered CoS findings remain ATTRIBUTED/UNVERIFIED.

## Header

HEADER: project — Preserve `adversarialllm` as the header name and `AdversarialLLM` as its established filing/ledger alias; count one project, not a non-filer caused by case mismatch.
HEADER: kernel — VERIFIED `fleet-factory-kernel r5`, still CANDIDATE/DOGFOODING; unchanged at 2,867 words. Revision agreement establishes no conformance.
HEADER: profile — `code@r10 (declared; bus now r11; r11 re-filing owed)`. Grade the subject against r10 and existing kernel obligations; disclose the VERIFIED revision difference without retroactive r11 grading or implied current-profile coverage.
HEADER: instance — Listed paths, operative amendments, mechanisms and DOGFOOD-PENDING status are ATTRIBUTED/UNVERIFIED. This ruling grants no adoption or launch authority.
HEADER: subjects — `0 closed end-to-end; 1 examined lineage SLICE-1E-R/R2; late K5 declaration; window-opened-before-kernel=no`. Do not count the predecessor and successor separately.
HEADER: window — The stated UTC endpoints are ordered: `2026-10-05T19:18:26Z .. 2026-10-13T21:16:23Z`; the claimed merge-author cutoff and completeness of local coverage are ATTRIBUTED/UNVERIFIED.
HEADER: health — Defective: prose declining re-grading does not supply §4’s ordered pair. On this ruling’s limited evidence use `assurance=UNSATISFIED operability=UNEVALUABLE`; K5 supplies the assurance failure, while this filing supplies no complete current operability assessment.
HEADER: providers — `none` is supportable only as no evidenced sentinel-complete filing-review lanes. The attributed Claude author receipt and product reviewers do not establish filing-review completion; any content review of the carrying PR must be reconciled with this header.
HEADER: posture — VERIFIED `POSTURE-NOT-R9-COMPUTED`; the submitted prose is neither R9 output nor the exact `no model review` exception. Use that exception only if no model review contributed to this filing’s content; otherwise disclose the actual computed posture and its limitations.
HEADER: missing clause/profile lines — VERIFIED absence of all twelve required K1–K12 verdict lines and every exercised `P:code` field line. Require corrected filing shape, but harvest the supported narrative assertions now; missing lines are not UNEXERCISED verdicts, and card N-A stances are not kernel N/A entries.
