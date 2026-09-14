> **NOT DOCTRINE — superseded draft, kept as evidence.** This is magic-lantern_dannephoto's parallel universal-kernel
> draft. `specs/fleet-factory-kernel.md` r1 (steward: Conjugal) landed first and the owner ruled it is the kernel
> (2026-09-14). What this draft adds is filed to r1's steward in `adjudications/factory-kernel/magic-lantern_dannephoto.md`.
> RULING R10 referenced below was never landed.

# Universal factory kernel — v0 (dogfood candidate)

**Status:** DOGFOOD CANDIDATE v0, binding to *run in shadow* under owner ruling R10 (2026-09-14); **zero runtime
authority**. It was reviewed before landing with the full posture (17/17 lanes, panel 63.88, classifier FLAT 2/3), and
its must-fix findings are folded into this text. The folding itself stays unreviewed until the first §8 amendment round
(`adjudications/universal-factory-kernel/magic-lantern_dannephoto.md`). It replaces no project's ledger, gate, scheduler or landing tool. It becomes the factory specification
only by the promotion rule in §9, from evidence the fleet files in §7. Until then every project keeps its own machinery.

**Executable form:** `tools/factory-kernel/kernel.py` (shadow conformance, metrics, feedback, harvest) and
`tests/test_factory_kernel.py`. The invariant ids below and the tool's `INVARIANTS` table are checked to match.

## 1. Why a kernel, and why not Approach A as the factory

Three measurements, 2026-09-13/14:

- **Approach A did not survive its second project.** The full review posture on `specs/conjugal-approach-a-v7.4.md`
  against the magic-lantern_dannephoto bench left 6 must-fix design findings. Its integration ref was assumed to be
  master (the bench lands on a branch 311 commits ahead). Its lock identity split across 4 worktrees. Its executors
  were admitted with zero eligible work. Replay stood in for verification. Adoptions were counted as delivery. The
  classifier called another design round FLAT (`adjudications/approach-a-design/magic-lantern_dannephoto.md`).
- **The fleet already agrees on a small core and disagrees on everything else.** A survey of ten project specs found:
  - Integration refs vary: `master`, `main`, `fork/master`, a remote-less local master, `codex/*` branches.
  - Checkouts vary: one shared worktree versus a worktree per item.
  - Verification varies by domain: three green runs at one SHA; hash-identical rendered exports; held-out scoreboards;
    frozen-capsule blind reviews; deploy-and-relaunch selftests; a live human login.
  - Yet every project requires independent, exact-commit verification, and none equates adoption with delivery.
    Where admission was not bounded by eligible work, open work went 0→181 and never drained, with four of seven weeks closing zero subjects (Conjugal).
- **Governance motion is the fleet's most measured failure.** Coordination-only commits have been measured at 99.5%
  (Conjugal), 99.7% (adversarialllm), and 351 governed entries to 1 commit (the documented fixpoint). This kernel's first
  shadow check found 31 governance commits and 0 product commits in 14 days on magic-lantern_dannephoto.

So the universal part is small, and a factory spec that fixes substrate details cannot be universal. The kernel fixes
the contract. **Adapters** (§6) fix how each domain verifies and delivers. **Substrates** — the machinery that stores
claims and moves refs, of which Approach A's git-ref oracle is one candidate for the code domain — are per implementation
and must pass the kernel check like any project.

## 2. Terms

- **Project:** a repository plus its owner.
- **Unit:** one owner-authorized piece of work with one verifiable output.
- **Executor:** a lane or process that works a unit.
- **Integration ref:** the ref adopted work must be reachable from, declared per project.
- **Adoption:** a unit's output accepted onto the integration ref with verification evidence.
- **Delivery:** the owner-valued outcome the adoption was for: a release, hardware acceptance, a published chapter, a
  shipped build, a decision taken. Each adapter defines it.
- **Governance commit:** a commit touching only coordination, planning, review or doctrine paths.
- **Product commit:** a commit touching the domain's product paths.

## 3. The unit state machine

`PROPOSED → ELIGIBLE → CLAIMED → CANDIDATE → VERIFIED → ADOPTED → DELIVERED`, plus `BLOCKED_OWNER | BLOCKED_EXTERNAL |
BLOCKED_CAPACITY` (from any pre-adoption state, each carrying a reason) and `REJECTED`.

| transition | who may make it | what it needs |
|---|---|---|
| PROPOSED → ELIGIBLE | the owner, or a delegate named in the project's owner-authority record | dependencies ADOPTED; the authority recorded (K4) |
| ELIGIBLE → CLAIMED | an executor, one per unit | an admission slot, which exists only if the unit is eligible (K3) |
| CLAIMED → CANDIDATE | the claiming executor | an exact candidate identity (commit, artifact hash, document blob) |
| CANDIDATE → VERIFIED | a key that did not author the candidate: a human, or a model seat that did not produce it (a solo novelist's reader panel counts) | an evidence receipt (§5) binding the command, exit status and exact identity (K5) |
| VERIFIED → ADOPTED | the project's single integration writer | the candidate reachable from the integration ref (K1) |
| ADOPTED → DELIVERED | the adapter's delivery rule, or the owner where the adapter reserves it | the delivery evidence (K6) |
| any → BLOCKED_* | anyone who observes the block | a reason and an owner-visible channel (K10) |
| BLOCKED_* → the state it left | whoever clears the block | the reason recorded as cleared |
| CLAIMED or CANDIDATE → ELIGIBLE | the claiming executor, or anyone once the claim's lease expires | the expiry or release recorded |
| VERIFIED → CANDIDATE | anyone, when the candidate identity changes after verification | verification never transfers to a different identity |
| CANDIDATE or VERIFIED → REJECTED | the verifier, or the integration writer | the failing evidence or the reason |

A native ledger need not use these names. The adapter manifest maps native states onto them, and unmapped native
states are reported, never guessed.

## 4. Invariants

| K | invariant | origin (measured) | shadow measurement |
|---|---|---|---|
| **K1** | The integration ref is declared per project and resolves, and every adopted unit whose identity is a commit is reachable from it. Non-commit identities (artifact hashes, document blobs) are bound by their K5 receipt instead. | Approach A assumed master; the fleet lands on five different ref shapes | `rev-parse`; `merge-base --is-ancestor` per adopted commit identity; UNKNOWN when no adopted units are readable |
| **K2** | Checkout identity (locks, journals, leases) is one shared identity per substrate. For git that is the common dir, so worktrees share it; other substrates (Perforce, a document store) declare theirs. | a `.git` file identity split one lock into four across worktrees | git: common dir, worktree count, declared identity (`git-common-dir` PASS; `single-writer-process` PASS only with one worktree); other substrates: the declared identity |
| **K3** | Admission is bounded by eligible work; zero eligible units admits zero executors. | Conjugal open work 0→181, never drained, four of seven weeks closing zero; Approach A's `executors=5` from the first minute | eligible and active counts against the declared admission floor, and against an observed executor count when the manifest declares a probe. Without a probe, K3 cannot see executors it was not told about. |
| **K4** | Work originates from a recorded owner authority; nothing manufactures its own backlog. | "saturation experiments maintain an implementation input backlog" repeated a documented failure | ledger authority record exists |
| **K5** | Adoption cites execution evidence: a receipt (§5) binding the command run, its exit status, the exact candidate identity, and a verifier who is not the author. Not a replay of control state, not a self-report, and not merely a file that exists. | review finding (3/3 classifier must-fix): Approach A signs adoption on replay agreement, which proves control-state consistency, not that a check ran; the bench's own contract rejects a model PASS alone | per adopted unit: evidence exists; at least one `*.receipt.json` with exit status 0, a matching identity and a non-author verifier; failing status files flagged; ledger author ≠ verifier. Existence without a passing receipt is WARN, never PASS |
| **K6** | Adoption and delivery are separate counters. A unit counts as delivered only with delivery evidence (who accepted it, when, and which identity), never from a state or id pattern alone. | 11 adopted desk cards and 0 delivered hardware or release outcomes on one bench | adopted and delivered counts; FAIL when delivery is claimed without evidence; WARN when no delivery-evidence field is mapped |
| **K7** | The governance-to-product commit ratio is measured over a window (default 14 days). A ratio at or above the adapter's alarm ratio (default 0.9), zero product commits, or zero motion raises the conformance-fixpoint alarm. | the 99.5% / 99.7% / 351:1 measurements | `git log` over the window, classified by the adapter's path classes at commit level and file level; the evidence carries the eligible count so starvation reads differently from spin |
| **K8** | The doctrine honesty floor holds: a doctrine sync receipt no older than 7 days exists, and reviews obey R1–R9 (a PARTIAL posture honestly labelled under R9 obeys them). | the R1–R9 measurements in RULINGS | receipt status and age |
| **K9** | Owner-reserved actions are enumerated. | every surveyed project reserves some (push, release, credentials, hardware, a live login) | declared list is non-empty |
| **K10** | Blocked work is visible: every blocked unit has a reason, and an owner channel exists whether or not anything is blocked today. | BLOCKED-CAPACITY that "wakes only on capacity evidence" can stall unseen | blocked units' reasons; owner channel exists |
| **K11** | A liveness floor is measured: at least one declared scheduler probe is live, or the project is owner-interactive with owner-interaction evidence committed in the last 14 days. | a lane supervisor sat Disabled for 18 days while leases looked fresh | every declared probe; the evidence path's last commit on the integration ref |

A result is PASS, FAIL, WARN, UNKNOWN or N/A, each with the evidence that produced it:

- **FAIL:** the invariant is measured and violated.
- **WARN:** the measurement is partial, or the invariant is at risk: existence without proof (K5), no
  delivery-evidence mapping (K6), the fixpoint alarm (K7), a stale receipt (K8), an undeclared identity across
  worktrees (K2), or owner-interactive mode without recent evidence (K11).
- **UNKNOWN:** it cannot be measured on this project with this manifest.
- **N/A:** it does not apply (no adopted units, or the project is the bus itself).

**UNKNOWN is never rounded to PASS.** An invariant the kernel cannot measure on a project is a finding about the
adapter, and the feedback carries it. In shadow mode, recorded authority (K4) and declared owner gates (K9) are
recorded, not authenticated; enforcement after v1 requires owner-signed records.

## 5. The adapter manifest

Each project describes itself in `feedback/factory-kernel/<project>/manifest.json` on the bus (single writer: that
project). Fields:

- `project`, `adapter`, `repo`
- `domain_class`: one of `code`, `firmware`, `media-render`, `game-engine`, `mobile`, `prose-creative`, `strategy`,
  `prose-strategy`; any other value is reported as an unknown class until an amendment adds it
- `integration_ref` (never defaulted)
- `checkout.{substrate (default git), model, lock_identity}`
- `ledger` — how to read the native ledger:
  - `kind`: `json-tasks` (path, list, id, status, commit, evidence, reason, authority, updated, `state_map`),
    plus `author`, `verifier`, `delivery_evidence` and `evidence_status_glob`),
    `command` (`argv` of a read-only command), or `none`
  - `command` output is `{"units": [{"id", "state": <a §3 state>, "commit"?, "evidence": [paths], "reason"?, "author"?,
    "verifier"?, "delivery_evidence"?}], "meta": {"authority"?, "updated"?}}`. A non-zero exit, invalid JSON or an
    unknown state makes the affected invariants UNKNOWN or the unit UNMAPPED, never PASS.
  - `delivery.{describe, id_regex, when_state}` says which units are delivery-class; `delivery_evidence` names the
    field that proves acceptance
- `admission.{configured_min_executors, observed_executors_argv}`
- `paths.{product, governance, alarm_ratio}` (globs; `*` stays within one path segment, `**` crosses segments)
- `owner_reserved[]`, `owner_channel`
- `liveness.{mode: scheduled | owner-interactive, probes: [{argv, ok}], evidence_path}`
- `doctrine_receipt` (a path, or `false` for the bus itself)

**Evidence receipt** (`<anything>.receipt.json` under an evidence path, 2 KB or less; large logs live outside git):
`{"candidate_identity", "command", "exit_status", "finished_at", "author", "verifier", "toolchain"?, "log_sha256"?}`.
The receipt is what makes an evidence directory prove an execution. Native status files (`*.status`) are read as
corroboration and flagged when failing, never as proof.

A project with no machine-readable ledger declares `kind: none` and files anyway: its UNKNOWNs are the most useful
feedback the kernel can get.

## 6. Domain adapters

An adapter answers five questions for its domain. **Unit:** what one unit produces. **Verification:** the execution
evidence that makes CANDIDATE → VERIFIED, bound to the exact candidate identity. **Delivery:** the owner-valued outcome and its evidence.
**Artifacts:** where large outputs live (outside git, with receipts of 2 KB or less in git, per DNG's measured breach of
87 MB in git). **Owner gates:** what never automates. Status is one of three:

- **CONTRACT:** no project has filed under the adapter.
- **MEASURED:** at least one project has filed a kernel record under it. This says the kernel ran against the domain,
  not that the domain's delivery works.
- **PROVEN:** a unit has reached DELIVERED under it with delivery evidence.

| adapter | unit | verification (execution evidence) | delivery | owner gates | status |
|---|---|---|---|---|---|
| **code** | a commit or PR | tests, CI and gate at the exact SHA, repeated (Cloudvore: three green runs at one SHA); non-author review bound to that head | a release or deploy the owner accepts | release, tagging, credentials, spend | CONTRACT in kernel form (Cloudvore, adversarialllm, airmypc, agent-bridge practice it natively) |
| **firmware-hardware** | a firmware or tooling commit | build plus emulator (QEMU) evidence; hardware sessions as first-class blocking gates, never substituted by tests | hardware acceptance on the device, or a published release | device sessions, defaults, release | **MEASURED** (magic-lantern_dannephoto, 2026-09-14; 0 delivered) |
| **media-render** (render pipelines, Blender, three.js scenes, image and video processing) | a pipeline change or a rendered output set | base and head built independently at one toolchain; outputs compared per file by hash, or by frame-matched statistics against a measured noise floor; held-out scoreboards; A/A runs before performance claims; synthetic input flagged as not covering real input | an output set the owner accepts, or a shipped build | visual acceptance, final-look sign-off | CONTRACT in kernel form (MLV-App, DNG, adobe-ingester practice it natively) |
| **game-engine** (Unreal, video games) | a code, blueprint or asset change | automated functional tests in the engine's headless runner; capture-based comparison of fixed camera paths; frame-time and memory budgets from deterministic counters; cook/package success on each target platform | a playtest build the owner accepts, or a shipped build | playtest judgement, platform submission, store assets | CONTRACT |
| **mobile** | an app change | unit and UI tests on emulators and a device farm at the exact build; signed-build reproducibility | a store submission accepted | signing keys, store submission, privacy declarations | CONTRACT |
| **prose-creative** (fiction, scripts, essays) | a chapter, scene or revision | a consistency lint (continuity, character, timeline) across the whole manuscript; a blinded reader panel against a pinned craft rubric; every claim of improvement cites the passage | the owner accepts a draft, or it is published | voice, final text, publication | CONTRACT |
| **strategy** (business strategy, plans, doctrine) | a decision memo, plan or ruling | every factual claim carries a derivation command or source; a pre-mortem; a falsifiable forecast with a resolution date; adversarial review (R1–R9 posture) | the decision is taken, and later scored against its forecast | the decision itself, commitments, spend | **MEASURED** as prose-strategy (softwarefactory-fleet-doctrine, 2026-09-14; no unit ledger yet) |

A domain not listed gets an adapter by the amendment rule (§8), first as CONTRACT, then MEASURED when a project files a
record under it, and PROVEN on its first evidenced delivery. A project may split across adapters (for example code plus media-render); it then files one manifest
per adapter, with a suffix in the file name.

## 7. Dogfooding in shadow — every project, every sync

At each doctrine sync (PROMPT A), and at least weekly, a project:

1. Keeps its manifest current (§5). The first time, it writes one. An honest `ledger.kind: none` is acceptable.
2. Runs `python tools/factory-kernel/kernel.py feedback --manifest <its manifest> --doctrine <bus> [--notes <file>]`.
   This writes `feedback/factory-kernel/<project>/<UTC-timestamp>-<ref-head12>.json`, single writer, and refuses to
   overwrite an existing record.
3. Writes the notes file with friction: an invariant that was wrong for its domain, a measurement the kernel got wrong,
   an adapter field it needed and lacked. Notes are the self-improvement input, so write them even when the tally is clean.
4. Commits the record, notes and manifest **to the doctrine bus**, whose integration ref is the bus's own `master`,
   at the landing seam. Then pushes and leaves the bus synced (Law 3, R8). Nothing is committed to the project's own
   repository, so its integration ref (K1) is untouched by dogfooding.
5. Acts on its own FAILs, or records why not. A shadow FAIL grants no authority to change anything, but a FAIL left
   unexamined is the fixpoint again.

Nothing in shadow mode claims, admits, adopts or delivers. The kernel measures the project's existing machinery.

## 8. Self-improvement: how the kernel changes

- **Harvest.** `kernel.py harvest --doctrine <bus>` derives per-invariant pass rates, coverage, demotions and the
  promotion checklist from the current-version records. The output is derived: it is printed or written to a local
  file, and **never committed**. So it has no writer to conflict over, and nobody can hand-edit it.
- **Proposals.** An amendment is `feedback/factory-kernel/proposals/<YYYY-MM-DD>-<slug>.md`. It starts with the line
  `status: PROPOSED | UNDER-REVIEW | LANDED | WITHDRAWN`, plus `landing_commit: <sha on the bus>` once landed. It states: the invariant,
  adapter or tool change as an anchored patch (`REPLACES: "<exact anchor>" → "<replacement>"`); the feedback records it
  rests on (**at least two records from at least two projects**, or one record plus a measured incident); and the
  falsifier that would show the amendment wrong.
- **Review.** A proposal is reviewed with `tools/review-posture/run.sh` on the full posture (R9), using
  `tools/review-posture/rubrics/factory-kernel-v0.json`, with the proposing project as test bench. A PARTIAL posture is
  allowed but is labelled, and its findings are read accordingly.
- **Landing.** A proposal whose must-fix findings are resolved is applied to this spec, the tool and the tests in one
  commit.
  - A change to measurement code that leaves every invariant's meaning intact lands by the proposing project.
  - **A change to an invariant's meaning, a new invariant, a promotion or demotion constant, or an authority rule
    lands only with an owner approval recorded in RULINGS**, cited in the commit. It is recorded in RECEIPTS with the proposal path, then harvested again. Changing
  an invariant's meaning bumps the minor version (v0.1, v0.2, …). Records carry `kernel_version`, so the harvest never
  mixes versions silently.
- **Demotion.** The harvest lists an invariant as due for demotion when its pass rate is under 0.5 across at least
  three measured projects, over at least 14 days of records. It then needs a proposal:
  amend it, narrow it to the domains where it holds, or show the projects are wrong. Leaving it untouched is not an option.

## 9. Promotion to v1 (the factory specification)

The kernel is eligible for owner ratification as v1 when the harvest shows all of the following (the constants are
`PROMOTION` in the tool):

- at least 5 projects filing records;
- at least 3 domain classes;
- at least 14 days of records;
- every invariant's PASS rate ≥ 0.8 where measured;
- every invariant measured (PASS, FAIL or WARN) on at least 0.8 of filing projects, and on at least one project in
  every represented domain class;
- at least one proposal with `status: LANDED` whose `landing_commit` is reachable on the bus (checked by the tool),
  which proves the loop works, not just that it exists;
- no invariant due for demotion.

A WARN that fires correctly, such as an honest fixpoint alarm, counts against the PASS rate on purpose. Promotion asks
whether the fleet *conforms*, not whether the kernel measured well. A project that is right to alarm is not yet a v1
factory.

Ratification is owner-reserved. v1 grants no runtime authority by itself. A project moves from shadow to enforcement
only by its own recorded disposition, per invariant, once v1 is ratified.

## 10. Relationship to existing doctrine

- **Approach A (Conjugal):** a candidate code-domain substrate. Its six must-fix findings are kernel invariants: K1
  (integration ref), K2 (common-dir identity), K5 (execution evidence), K3 (admission), K4 (no manufactured backlog),
  K6 (delivery counter). A substrate that fails K1–K6 cannot back a v1 factory in any project.
- **Review:** `tools/review-posture/` and RULINGS R9; the honesty floor R1–R5; push and sync R7–R8.
- **Providers:** `specs/fleet-provider-capacity-governor.md`, `specs/cli-orchestration-standard.md`, the machine
  inventory (R5), and account parity (R6). The kernel does not route providers.
- **Conformance-fixpoint:** `specs/fleet-orchestrator-execute-posture.md` §1. K7 is its measurement.

## 11. Not in v0

- No runtime authority, no scheduler, and no cross-project admission.
- No replacement of native ledgers; the `command` ledger kind is how a project exposes a markdown or database ledger.
- No provider routing.
- No automatic proposal landing.
- CONTRACT adapters are contracts, not claims.
