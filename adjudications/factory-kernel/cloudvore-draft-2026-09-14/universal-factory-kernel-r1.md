# Universal factory kernel — R1

**Cloudvore (DropBox Vault), 2026-09-14, Dell XPS 17. NOT RATIFIED. Zero runtime authority until
project adoption.** This proposal grants no lane, floor, agent or project any permission, and it
supersedes nothing. Clause IDs are `UFK-n` so they cannot collide with owner rulings R1–R9,
reconciliation rounds R1–R46 or candidate revisions `-rN`.

**Dogfood directive (owner, Layi, 2026-09-14, in a Cloudvore session):** *"submit to doctrine repo so
we can finalize on factory spec and start dogfooding it in each project and giving feedback so it can
self improve."* That is an instruction to trial it and file findings. It is **not** ratification. As
`ruling-candidates/mandatory-review-floor-r1.md` §4 says of itself, this file stays a candidate until
the owner enacts it in their own words. UFK-8 only decides which clauses are **eligible** to be put
to the owner.

## 0. The problem, measured

- **The bus grows faster than it converges.** From `bb12132` (2026-08-14) to `9eeba29` (2026-09-14),
  31 days, counting lines with `len(text.splitlines())`: TRAPS.md 1,768 → 8,995; RECEIPTS.md
  892 → 2,562; RULINGS.md 942 → 2,219; `specs/` 10 → 38 files. No tool or rule retires, caps or
  indexes superseded doctrine.
- **Law is scattered, and "universal" documents are not law.** The ratified pieces of a kernel exist:
  README Laws 1–6; READ-TIME VERIFICATION (RULINGS.md:67); factory health axes (:442); fixes publish
  before closeout (:512); repair lifecycle (:589); delivery transaction (:623); measured merit
  (:1171); review-independence properties (:1893–1900); R1–R9 (:2028–2219). Meanwhile
  `adoption/decision-tree-factory-selection.md` (FRAMEWORK), `adoption/reference-factory-mlv-app-primary.md`
  (RECOMMENDED), `docs/factory-operation-modes.md` and several `specs/*` declare fleet force with no
  RULINGS entry.
- **Eleven projects publish (ten `specs/<project>.md` files plus magic-lantern_dannephoto, which
  files adjudications). All are software, and "done" already means four different things**:
  - deterministic test runs (Cloudvore, agent-bridge, Salesforce tools);
  - a statistical score on a held-out fold (dng-auto-processor);
  - attended proof: AirMyPC's live hardware and adobe-ingester's human login (their `specs/*.md`);
  - a literal cross-family APPROVE (AdversarialLLM).

  Planned projects — creative writing, business strategy, Unreal Engine and other games, Blender
  rendering, three.js, mobile apps — add acceptance that no test runner can execute.
- **Copying a project's shape is not adopting a kernel.** On 2026-09-13 Cloudvore recorded adoption
  of Conjugal's resume dispatcher. The dispatcher conflicted with Cloudvore's own contract, and the
  proof cited a flag that exists only in Conjugal's checker. Three review rounds were needed to correct
  it (RECEIPTS.md and TRAPS.md, 2026-09-14).

## 1. Shape: a small kernel plus declared acceptance adapters

The kernel names **interfaces**: what must be true and how anyone can check it. It never names an
implementation. A project keeps its queue format, languages, CI location, hub or no hub, and model
routing. Anything a clause below does not require is local practice and needs no disposition.

**Budget, measured by `tools/kernel-convergence.py`:**
- at most 8 `### UFK-n` clauses;
- at most 30 lines from one clause heading to the next;
- at most 420 lines across the three normative files: this file, the filing README and PROMPT K.

A revision that adds a clause must merge or delete one. A revision over budget is not harvestable,
so policy cannot migrate into companion files unmeasured. A clause that would restate ratified law is
written as a pointer to it: `multi-agent-branch-landing-protocol-r2` was rejected for republishing
law (its own header), and this file follows that precedent.

## 2. Clauses

### UFK-1 — One queue; every item states its acceptance before work starts

Each project has exactly one active work queue, in any format that keeps a version history or dated
log. Every item carries an ID, a state, its dependencies, and an acceptance **statement** recorded
before the work begins: what will be checked, and by which adapter class (UFK-6). The mechanism (test
code, threshold, hardware checklist) may be built alongside the work. A `judgment` item's rubric and
judge roster are fixed before the artifact exists, and its author is never one of its judges. A
blocked item names who or what can clear it and gives a wall-clock next check. An event trigger such
as "when X lands" is not a next check. Closing an item is the delivery transaction already ratified
at RULINGS.md:623.
**Check:** every non-DONE item has an ID, state, dependencies, an acceptance statement and, if blocked,
a clearer and a timestamp. In the history or log, the acceptance statement appears no later than the
item's first implementing change.

### UFK-2 — Work state is derived by command, never recited

Pointer to RULINGS.md:67 (READ-TIME VERIFICATION) and Law 1. Kernel addition: an entry file names the
derivation commands and holds no **work state** (current SHAs, counts, verdicts, "current status"
prose). Work state is where the work stands; the artifact itself (code, manuscript, memo) is not
state. Where a human chooses the next item, that choice is recorded in the queue and the derivation
reads it.
**Check:** (1) run the entry file's derivation commands and record the next item they select; (2) a
session with no memory, given only the entry file, names its next item; (3) the two match. The entry
file has no commit IDs except in cited history.

### UFK-3 — Done names a durable identity anyone can re-check

Pointer to Law 3, R7 and R8. Kernel addition for non-git artifacts: a DONE claim names the artifact's
identity — a commit reachable from the default branch, or a content hash plus a durable storage
location for renders, builds, manuscripts, datasets or signed binaries. An `attended` DONE also names
its attestation record: who witnessed it, when, and on what hardware or account. Re-checking an
attended claim re-verifies that record; it cannot replay the event, and it must not pretend to.
"Passed in my worktree" is not DONE.
**Check:** for every DONE item, one command resolves the named identity from a fresh clone or the
named store, and it matches. For `attended`, the attestation record exists and names a witness.

### UFK-4 — Review is decorrelated from authorship

Pointer to RULINGS.md:1893–1900 (independence properties; model family is a cost choice, not an
independence property), RULINGS.md:1192 (authors do not score their own candidate), R3 and R9. Kernel
addition: the reviewer receives an attack question, not a request for approval. **Measured, not
required:** on 2026-09-14 one cross-family seat (Codex gpt-5.6-sol) found three defects in
Cloudvore's self-describing corrections that had survived an earlier same-family review round
(RECEIPTS.md, "Cross-family review of Cloudvore's two 2026-09-14 corrections").
**Check:** every accepted item's review record shows each property at RULINGS.md:1893–1898:
- a non-author with fresh context and no shared custody;
- an assigned, opposing brief;
- evidence the reviewer produced;
- review of the whole combination;
- the integrator's re-derivation of each load-bearing finding.

### UFK-5 — One authority index per project

Each project keeps one register of owner-only decisions, each with a status (OPEN / RULED date) and a
pointer to its reasoning. A project with several registers (e.g. product, self-heal, recovery) keeps
one index naming every register and the decision class each governs. A project with no owner-gated
decisions says so in that file; an empty file is not a statement. Anything not in the register is not
owner-gated: a lane may not self-authorise an OPEN item, and may not treat an unregistered question as
needing the owner. Bounded clearance of enumerated blocker classes is out of scope here; see
`ruling-candidates/bounded-authority-register-r1.md`.
**Check:** exactly one register or index path is named by the entry chain, and it is non-empty.
Every "needs owner" statement in the queue cites a row reachable from it.

### UFK-6 — Each project declares its acceptance adapters

An adapter is how a project proves UFK-1's statements. Each declaration names the **artifact kind**,
one or more **adapter classes**, **who or what executes** each check, and the **evidence identity**
UFK-3 records. There are four classes, defined by how repeatable acceptance is, not by domain:

| Class | Acceptance is | Minimum rule |
|---|---|---|
| `deterministic` | a rerunnable check with a binary result | the project's own repetition bar (e.g. N identical green runs at one identity) |
| `statistical` | rerunnable, with noise | threshold and sample size fixed before the run; held-out data never tuned on |
| `attended` | needs hardware, a live account, a device or a human present | the attended step is a named queue state, never silently skipped; everything automatable around it still runs |
| `judgment` | taste, quality, or a decision whose outcome comes later | a rubric **pre-registered** before the artifact is seen, scored by ≥2 decorrelated non-author judges; outcome claims carry a resolution date and are scored then |

Illustrative mappings (non-normative):

| Domain | Typical adapter |
|---|---|
| desktop, web, services, firmware static checks | `deterministic` |
| three.js / web visuals | `deterministic` build + `statistical` screenshot diff with tolerance and frame-time budget |
| mobile apps | `deterministic` tests + `attended` device matrix |
| Blender rendering | `statistical` perceptual diff against a reference frame + render-time budget |
| Unreal Engine / games | `deterministic` build + `statistical` scripted playtest + `judgment` human playtest rubric |
| creative writing | `judgment`: pre-registered rubric, ≥2 blind non-author readers, manuscript hash |
| business strategy | `judgment`: memo with pre-registered, falsifiable predictions, each with a resolution date |
| camera firmware, audio hardware, provider logins | `attended` owner-run proof |

**Check:** a declaration exists for every artifact kind that has a DONE item, and each DONE item's
evidence matches one of that kind's declared classes.

### UFK-7 — Doctrine carries its test and its supersession

For anything a project publishes to the bus under this kernel:
- **(a)** a trap names an executable test, or is headed `ANECDOTE (no test)` and is not citable as
  doctrine;
- **(b)** a new candidate or topic spec names what it supersedes, or states "supersedes nothing" and
  why;
- **(c)** nothing self-declares force (`IN FORCE`, `BINDING`, `FLEET STANDARD`, "ratified") without a
  RULINGS.md entry (see `mandatory-review-floor-r1.md` §4 and RECEIPTS.md, 2026-09-13, on the bus's
  ratification contradictions);
- **(d)** an entry that corrects or retires an earlier one carries a greppable line
  `SUPERSEDES: <file> "<exact heading>"`, so a reader tool can list live doctrine without deleting
  append-only history (Law 2 stands).

**Check:** in a bus checkout, `python tools/kernel-convergence.py --hygiene` lists traps without a
test, and new candidates or specs that never mention supersession, since this candidate's first commit.

### UFK-8 — Self-improvement loop: dogfood, file, harvest, converge

1. **Dogfood.** Each project runs `bootstrap/PROMPT-K-dogfood-kernel.md`. It runs UFK-1…7's checks in
   its own repo, and files `adjudications/universal-factory-kernel/<project>.md` (filename stem equals
   `project:`) on `review/<project>-<date>` (R7).
2. **Harvest.** Harvest is due when ≥3 counting filings (UFK-8.4) are unharvested, or when ≥1 is
   unharvested and 7 days have passed since the subject's last `.dispositions.md` commit (or since
   this candidate's first commit, if there are none). The 7 days bound how long a landed filing waits
   for an answer. They are not a cadence: publication always answers a filing that has landed, and
   with nothing filed, nothing is published (Law 3). The candidate owner (Cloudvore) harvests with
   `bootstrap/PROMPT-3-harvest.md`, answers every clause line in each `.dispositions.md`, and publishes
   `-r(N+1)`.
3. **Amend on divergence.** When ≥2 projects in different adapter classes file DISTINGUISH or REJECT
   with PROOF on one clause, the next revision must amend, merge or delete that clause.
4. **Eligible.** A filing counts when its stem equals `project:`, the project is known to the bus, it
   names the current revision, and it has `seats:` and an adapter declaration. A clause is eligible
   when ≥2 distinct non-author counting projects adopt it with PROOF from two different adapter classes. It is not eligible if it must be
   amended, or if a REJECT-with-PROOF has no answer for that clause in the filing's dispositions. The
   kernel may be called universal only when every clause is eligible and a non-author `judgment`-class
   project adopts. Until then it is at most "fleet kernel for software projects".
5. **Measure and enact.** Each harvest's RECEIPTS entry carries `tools/kernel-convergence.py --json`.
   The tool cannot authenticate PROOF; eligibility is a prompt for re-derivation, not a verdict. An
   eligible clause reaches RULINGS.md only after non-author review re-derives its PROOF lines
   (RULINGS.md:1893) **and** the owner enacts it in their own words.
6. **Direction.** Healthy: normative lines flat or falling; eligible clauses and classes covered rising;
   must-amend clauses falling. Bus activity is not a convergence signal.

**Check:** in a bus checkout, `python tools/kernel-convergence.py` exits 0 (within budget). When it
reports `harvest_due: true`, a harvest or its named blocker is published within one working day.

## 3. What this candidate deliberately does not do

- It does not require any hub, lane, seat, dispatcher, swarm size, model family, CI host or queue file
  format.
- It does not re-open R1–R9, the provider-capacity governor, or R26/R46 dispositions.
- It does not require a project to edit `specs/<project>.md`. Filings live under `adjudications/`, so
  dogfooding does not trip the adoption-ledger drift check.
- It does not claim that any clause holds outside software until a `judgment`-class project files.

## 3a. Known limits of r1 — dogfooding is how these get answered

Recorded from a second cross-family review (Codex gpt-5.6-sol), which voted NO on publication for the
first two items. They are published as open questions rather than hidden:
- **Nothing is authenticated.** Project identity, authorship, adapter classes and PROOF are all
  self-asserted. Every project is run for one owner, so a determined filer can make any clause look
  eligible. That is why eligibility is never a verdict (UFK-8.5).
- **UFK-1, UFK-2 and UFK-4 checks are procedures a session performs, not single commands.** A filing
  that ADOPTs them should say exactly what it inspected. r2 should turn whichever proves most
  contested into a command.
- **`--hygiene` covers only UFK-7 (a) and (b)**, and those only by text presence. (c) and (d) are
  unchecked.
- **Judgment-class projects do not yet exist** in the fleet, so UFK-6's `judgment` rules are untested.

## 4. Companion files

- `adjudications/universal-factory-kernel/README.md` — the filing format.
- `bootstrap/PROMPT-K-dogfood-kernel.md` — the prompt a project session runs to dogfood and file.
- `tools/kernel-convergence.py` and `tests/test_kernel_convergence.py` — derive clause eligibility,
  divergence, the universal flag, harvest due, budget and UFK-7 hygiene from refs.
