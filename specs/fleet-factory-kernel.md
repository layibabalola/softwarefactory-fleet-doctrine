# Fleet factory kernel — the universal core every project's factory runs on

**Status: `CANDIDATE r4 — DOGFOODING`.** Submitted 2026-09-14 on the owner's instruction (Layi): *"Execute recommended
and submit to doctrine repo so we can finalize on factory spec and start dogfooding it in each project and giving
feedback so it can self improve."* This is a submission for dogfooding, not a ratification. It grants no runtime,
adoption or launch authority. A project is bound by it only once it records `ADOPT` (Law 1). RULINGS R1–R9 stay binding
on their own terms, whatever this document says.

**Steward:** Conjugal, as interim steward, until the owner names another. The steward is the single writer of this file
and of `specs/fleet-factory-kernel/`, and harvests `adjudications/factory-kernel/` under §5. **Measure:** under 3,500
whitespace-delimited words (`len(text.split())`, TRAPS 2026-09-14).

## 0. Three layers, and why

A single factory specification cannot be universal. Measured on this bus: Conjugal's Approach A (`specs/conjugal-approach-a-v7.4.md`, v7.5) assumes
git refs, one shared Windows checkout, deterministic replay and acceptance-by-test-suite. Its only test benches are
two Windows code repos, and its harvest rule decides divergences for the bench the spec is written for. That process
hardens one factory; it does not generalise one. Unreal and Blender artifacts are large binaries. Renders are often not
byte-reproducible. Writing and strategy have no test to run. So the factory splits into three layers:

| Layer | Owns | Changes when | Written by |
|---|---|---|---|
| **Kernel** (this file) | Invariants that hold for honest work in *every* domain: roles, authority, subjects, evidence, verification, delivery, capacity, continuity, review honesty, feedback | A clause is shown to break honest work in some profile, or causes the same friction in two or more profiles (§5) | Steward |
| **Profile** (`specs/fleet-factory-kernel/profiles/<domain>.md`) | What *acceptance* means in a domain: subject identity, evidence kinds, determinism class, verifier independence, resource terminals, delivery target, human gates | That domain's benches file evidence | Steward, from that domain's filings |
| **Instance** (in each project) | The mechanism: tools, paths, lanes, schedulers, thresholds | The project decides | The project |

Conjugal's Approach A v7.5 is an **instance** of the `code` profile, not the kernel.

## 1. Terms

**Subject**: one unit of work with an exact identity (§2 K3). **Candidate**: a produced version of a subject.
**Producer / verifier / adjudicator / owner**: roles (K1). **Evidence**: an observation that names subject identity,
actor, method and time. **Receipt**: durable evidence that someone other than its author can re-read. **Profile**: the
acceptance contract for a domain. **Independence class**: the trust domain a key comes from (a provider backend, a
human, a hardware rig). Two wrappers over one backend are one class.

## 2. Kernel clauses

Each clause gives the invariant, the existing doctrine it points to (status quoted as that document states it), and the
**conformance observable**: what a dogfooding project shows to claim the clause holds for it. A clause with no
observable is not a clause.

### K1 — Roles separate; nobody accepts their own work
Producer, verifier, adjudicator and owner are distinct roles. A candidate is never accepted on evidence whose only author
is its producer, and an adjudicator never supplies the key it is adjudicating.
*Doctrine:* RULINGS "RULING 2's first clause… stands untouched" (recusal from self-review, ratified log); Cloudvore
2026-08-10 "The hub adjudicator is not that reviewer and cannot be the second key."
*Observable:* for one completed subject, the receipts name different actors for production and acceptance.

### K2 — Authority is a written register
Each project keeps one register of what needs the owner and what does not. Everything unlisted is autonomous. Escalation
goes to the owner for decisions reserved by that register; otherwise only for deadlock, a novel class, high risk, or an
irreversible act. A register entry beats a memory note, a charter or a handoff.
*Doctrine:* `specs/autonomous-decision-making-with-adversarial-swarms.md` ("IN FORCE (fleet-wide autonomy standard)").
**Overlap:** `specs/autonomous-swarm-adjudication.md` ("Adopted… Ratification: Pending"). Both describe this; the kernel
requires the register, not either mechanism.
*Observable:* the register's path, and one decision the project took without asking because the register allowed it.

### K3 — Every subject has an exact identity and one claimant
A subject's identity is a content digest over its **declared artifact set**. That can be a git tree, an asset manifest
of blob hashes for binaries held outside git, or a document hash. It is never a branch name, a filename or a path alone.
One claimant holds a subject at a time, under a lease that expires. Each durable file has one writer.
*Doctrine:* README Law 2 (single writer, ratified 2026-08-08); RULINGS "exact-worktree claim creates a seat";
recoverable-delivery ruling "exact closure subject". **Gap:** there is no fleet claims/leases spec. This clause states
the invariant. Each profile lists identity components; the identity is `sha256` over the component digests,
joined by newlines in the profile's listed order.
*Observable:* the identity string of one subject, and the command that recomputes it from the artifacts.

### K4 — Completion is positive evidence
Work is complete only on positive evidence it was asked to produce: a sentinel, a receipt, an artifact digest. Never
exit code, output size or silence. Capability, configuration, enabled state and actual execution are four different
facts and never stand in for one another.
*Doctrine:* RULINGS R2 (binding); R6 ("capability, configuration, enabled state, and terminal execution are distinct");
"Configured != running".
*Observable:* one receipt, and the negative case the project checked (a lane or job that exited 0 without its evidence).

### K5 — Acceptance is a declared profile, applied to the exact subject
Before work starts, a subject declares its profile and profile version. Accepted means that profile's acceptance
evidence exists **for that exact subject identity**. A resource stop (thermal, quota, disk, time, GPU, device
unavailable) is a typed terminal with zero partial credit. It is never re-read as a pass, and never waived by relabelling.
*Doctrine:* RULINGS "Cloudvore ratification — two-stage resource-blocked assurance failover" and "Minimum portable
adoption proof" (ratified log). Profiles: `specs/fleet-factory-kernel/profiles/`.
*Observable:* the profile line recorded before work, and the acceptance receipt bound to the same identity. Precedence is read from AUTHOR dates or the reflog, never committer dates: a rebase onto a moving integration branch rewrites committer dates, and a verifier reading them has refused a compliant subject (Conjugal S3).

### K6 — At least one independent key
Every acceptance includes a key from an independence class other than the producer's. When the check is model judgment,
the cross-family rule applies and the claim is computed, not asserted (R3). When the check is a human, a hardware rig or
a measured score against held-out ground truth, that is the independent key, and the receipt names it. A profile may
require more keys; it may not require fewer. A key that is dispatched and terminated without producing a verdict --
by a provider safety classifier, a capacity stop, or a crash -- is the typed terminal `KEY_UNAVAILABLE_BY_PROVIDER`.
It carries zero credit and never closes a subject; it exists so that a reachability failure is enumerable and is not
recorded as though no key was ever sought. The receipt names the class that was unreachable.
*Doctrine:* RULINGS R3 (binding); `independence_class` (Cloudvore 2026-08-10, ratified log).
*Observable:* the independence class of each key on one accepted subject.

### K7 — Accepted is not delivered; delivery closes as one recoverable transaction
Acceptance and delivery are separate states. Delivery means moving an accepted subject to the profile's **delivery
target**: an integration branch, an app store track, a render output store, a published document, an owner decision
record. It closes as one transaction, or it reports `CLOSURE_INCOMPLETE` and blocks conflicting deliveries to that target
until reconciliation, evidenced cancellation, or an authorised superseding transaction resolves the attempt.
*Doctrine:* RULINGS "accepted delivery closes as one recoverable transaction" (ratified log).
*Observable:* the delivery target, and how the project detects an accepted subject that never delivered.

### K8 — Capacity never stalls the factory
Running out of quota means rotating or parking the work that needs inference, never failing the factory closed. Work that
needs no inference continues. Reset events update capacity telemetry. They never open a gate by themselves.
*Doctrine:* `specs/fleet-provider-capacity-governor.md` ("RATIFIED PORTABLE CORE — NO LIVE ADMISSION, ROUTING, OR
AUTHORITY GRANT").
*Observable:* what happened to in-flight work at the last quota event.

### K9 — Resume from durable artifacts alone
Accounts rotate without warning. A fresh session on a new account, with empty memory, resumes from the project's tree
and the bus alone. Resumability is gated at landing seams, before expensive spend, at the first rate limit and on the
status tick.
*Doctrine:* `specs/account-rotation-and-project-continuity.md`. **Status conflict:** its header says "WORKING STRATEGY"
and its body says "ratified as a fleet standard". `specs/pre-rotation-proof-and-resume-dispatcher.md` ("PROPOSED
portable pattern"). `specs/fleet-continuity-autonomous-resumption.md` is superseded; do not cite it.
*Observable:* the resumability gate's command and its last passing output.

### K10 — Inventory and identity are measured
Provider and model inventory is machine-scoped and probe-derived, and it records the account it was derived under.
Account parity is verified before any provider work.
*Doctrine:* RULINGS R5, R6 (binding); `specs/machine-inventory-schema.md`.
*Observable:* inventory path, `probed_under` identifying the current account, and parity command output. Missing, `unknown` or mismatched account identity makes the inventory stale; re-probe under the current account before provider work.

### K11 — Reports are honest
R1–R5, R7, R8 and R9 apply to every report a factory makes about itself, including dogfood filings under this kernel.
*Doctrine:* RULINGS R1–R9 (binding).
*Observable:* the quoted title line of each rule the project confirms it meets (PROMPT A §3).

### K12 — The factory improves from its own use
Every project that runs the kernel files what happened to `adjudications/factory-kernel/<project>.md` (§4). Each
filing reports its factory health as the ordered pair **assurance** / **operability**, never one blended score. The
steward harvests every filing and answers each one.
*Doctrine:* RULINGS "factory health is an ordered pair" (ratified log); "Filings are consumed, not just filed" and
"filings travel sideways" (owner rulings); `bootstrap/PROMPT-3-harvest.md`; `tools/harvest-status.py`.
*Observable:* the project's filing on `origin`, `harvest-status.py factory-kernel` showing it `HARVESTED`, and a disposition for every filed finding, including Untested items, proposals and addendum claims, bound to that filing's blob.

## 3. The universality test for kernel text

Kernel text must not assume:
- git as the artifact store;
- text artifacts;
- byte-deterministic outputs;
- an automated test suite;
- a single host;
- a model as the verifier;
- a software delivery target;
- a project tree that fleet tooling may write into.

Any sentence that does belongs in a profile. When a new domain joins, its first project checks every clause against
this list before filing.

## 4. Dogfood filings — how feedback is shaped

`bootstrap/PROMPT-K-dogfood-kernel.md` is the paste. Each filing's header:

```
project: <name>
kernel: fleet-factory-kernel r<n>
profile: <profile>@r<n>                  (the profile file's own revision)
instance: <path in the project that implements the kernel>
subjects: <n real subjects run end-to-end in this window, with identities>
window: <ISO start> .. <ISO end>
health: assurance=<SATISFIED|UNSATISFIED|UNEVALUABLE> operability=<NORMAL|PRESSURED|UNEVALUABLE>
providers: <families whose lanes cleared a sentinel, else none>
posture: <R9 line if any model review contributed, else: no model review>
```

After the header comes one line per clause (K1–K12), then one `P:<profile> <field-id> | …` line per profile field
the project exercised. `<field-id>` is the field's table name in lowercase, hyphenated, without the parenthesis
(`subject-identity`, `acceptance-evidence`):

```
K<n> | FIT|FRICTION|BREAK|N/A|UNEXERCISED|INSTANCE-FAILURE | "<≤25-word quote from the kernel or profile>" | <evidence in YOUR repo: path, tool, measured number> | REPLACES: "<anchor>" -> "<replacement>" (FRICTION/BREAK only) | PROOF: <what would falsify this line>
```

- **FIT**: the clause held and cost nothing extra.
- **FRICTION**: it held at a measured cost (time, calls, owner interruptions). Name the cost.
- **BREAK**: honest work in this domain cannot satisfy it as written. Give the concrete counterexample.
- **N/A**: the clause cannot arise in this project's domain. Give the reason.
- **UNEXERCISED**: the clause could arise but did not in this window (for example, no subject ran or no quota event
  happened). It is not evidence about the clause.
- **INSTANCE-FAILURE**: the clause arose and honest compliance was possible, but the instance failed it. Name the
  failure and evidence; no replacement. It counts toward health, never toward conformance or a kernel change.

**Only real work counts.** Subjects are owner-authorised work the project already had. Manufactured subjects are not
filed (Approach A Round F1, cluster C8). Findings with no evidence from your own repo go under `## Untested`.

## 5. How the kernel changes, and when it is final

**Harvest.** PROMPT A §4 surfaces `open>0` on `adjudications/factory-kernel` to the steward. The steward runs
`bootstrap/PROMPT-3-harvest.md` on it with **one rule changed**. For a divergence, do not decide in favour of the bench
the spec is written for, because the kernel is written for all of them. Decide by the universality test (§3):
- A BREAK with a concrete counterexample from any profile wins over FIT elsewhere. The clause is narrowed, or the rule
  moves into a profile.
- FRICTION changes the kernel only when two or more profiles report it. One profile's FRICTION changes that profile.
- The steward's own project's filings are never adjudicated by the steward alone. A second project's arbiter, or the
  owner, rules on them and writes that filing's `.dispositions.md` with an `arbiter: <project or owner>` line; the
  steward never writes it.

**Harvest runs continuously.** The steward automates the harvest; a harvest that waits for someone to remember is not
one. The reference implementation is Conjugal `coordination/harvest/`. A scheduled gate spawns no model unless a filing
waits. A deterministic runner prepares worktrees, census-checks every changed path, lands and publishes by replaying
onto the fresh tip, and proves `HARVESTED`. The session only edits files. Owner direction, 2026-09-14: "I want harvest
to be automated continuously."

**Keep it small.** A clause enters only when a BREAK or cross-profile FRICTION shows a missing invariant. A clause leaves only
when independently reviewed evidence shows it cannot arise in any supported profile, or when it has no observable.
UNEXERCISED windows and quiet periods never count toward removal. The word cap in the header does not rise.

**Versions.** The kernel's `r<n>` and each profile's own `r<n>` increment when that file's text changes. Filings name
the revisions they ran. A harvest is one completed adjudication of a recorded eligible filing set, not a poll or retry.
For finalisation, unchanged means identical kernel and participating-profile content digests as well as revisions. The
harvest tool marks a filing `STALE` when its author changes it and reads its `kernel:`, `profile:`, `subjects:` and
`health:` lines. Each harvest appends one row per filing to `adjudications/factory-kernel/HARVESTS.md`
(steward-written): date, filing, blob, kernel and profile revisions, subjects, verdict counts, unresolved BREAKs.
INSTANCE-FAILURE lines count toward health, not the ledger's verdict counts. The
finalisation rule reads that ledger, never a single filing.

**Kernel v1 is FINAL when all four hold:**
1. At least five member projects have filed, each covering at least one real subject end-to-end with receipts.
2. At least three profiles have been exercised, including at least two whose acceptance is not an automated test suite.
   `hardware-in-loop` and `measured-objective` both have benches today.
3. Two successive harvests in which no **section 2 clause text** changed contain fresh end-to-end evidence meeting
   criteria 1 and 2, with no unresolved BREAK; a disputed rejection of a BREAK is adjudicated by a project other
   than the steward. Profile-only and section 6 roster edits do not reset the window; a clause edit does. Read
   literally, "unchanged revision" was unsatisfiable by construction: the harvest is the process that amends the
   kernel, and every harvest so far bumped the revision (r1 to r4 inside 48 hours), so the criterion was reset by
   the only mechanism that could satisfy it.
4. The owner's ratification is appended to RULINGS.md.

After v1, a BREAK from a new domain opens `v1.<m>`. A profile leaves `DRAFT - NO BENCH` when its first project files.

## 6. Fleet mapping (provisional; each project confirms or corrects it in its first filing)

Derived 2026-09-14 from each project's own spec (or repo instructions where it has none), citing the acceptance bar stated there.

| Project | Proposed profile | Confidence | Acceptance bar as its spec states it |
|---|---|---|---|
| cloudvore (DropBox Vault) | code | high | "three identical green runs at one candidate SHA" |
| conjugal | code | high | "fresh clean-clone acceptance, guarded full suite, and clean distinct-provider acceptance key" |
| salesforce-tools | code (+ mobile for its KMP lane) | high | `build.ps1` publish, self-sign, ~230-check selftest, deploy |
| adversarialllm | code | high | product commits in `src`/`tests` |
| agent-bridge | code (fleet tooling and product) | high | `AGENTS.md:56`: 471 tests pass with `%LOCALAPPDATA%\Temp`; `C:\WINDOWS\TEMP` gives 467 passed / 4 failed |
| adobe-ingester | code (automation probe) | medium | "a real, user-present, headed Adobe login" (human gate) |
| airmypc | code + hardware-in-loop release gate | medium | "live hardware; the one attended sitting" |
| magic-lantern_dannephoto (no bus spec yet; mapped from its repo's CLAUDE.md) | hardware-in-loop | high | "Hardware evidence comes only from the owner's camera" |
| dng-auto-processor | measured-objective | high | auto grade "matches the manual grade per frame", scored on a held-out fold |
| mlv-app | code (primary) + measured-objective (render/export parity and playback measurement) | high | "a falsifier suite that runs"; "compare artifacts by hash, per file, zero tolerance"; A/A trend before claims |

`specs/context-ultra-salesforce.md` is a git-hygiene pattern document, not a project, and is mapped to no profile.
**No bench yet:** `game-engine`, `realtime-web-3d`, `3d-render`, `creative-writing`, `business-strategy`, and `mobile-app`
beyond one scaffold lane.

## 7. Known gaps this candidate carries

1. No fleet claims/leases spec (K3 states the invariant only).
2. Two overlapping autonomy specs at different ratification maturity (K2).
3. The continuity spec's status contradicts itself (K9).
4. Hardware-in-loop has a bench filing; the other non-code profiles still lack harvested evidence.
5. The kernel has never been run end to end. Every clause is `unpassed` until a filing says otherwise.
