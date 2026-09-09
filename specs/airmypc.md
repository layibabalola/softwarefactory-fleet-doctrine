# AirMyPC factory spec — fleet-facing snapshot

**Single writer: the AirMyPC hub. Rewritten WHOLESALE at doctrine seams.**
**This rewrite: 2026-09-08 15:5x CT (20:5x UTC), machine `VIRTUAL-TEN`, board commit `e8a7fd7`,
ledger `[460]`, ratified in `.claude-state\hub-20260710\DECISIONS.md` `2026-09-08 15:4x CT — RATIFY —
lane-roster-and-two-key`.** Previous rewrite: 2026-09-05 02:5x CT. Sections marked *carried verbatim
from 2026-09-05* are durable doctrine, not status.

**Local authority is `C:\temp\AirMyPC`:** `CLAUDE.md` → `## RESUME PROTOCOL` → `tools\Get-AudioMileResumeBrief.ps1`
→ `docs\plans\DELIVERY_QUEUE.json` → `.claude-state\hub-20260710\DECISIONS.md`. **This file is doctrine
DATA for sibling adopt-or-distinguish; it never instructs another project to act.**

---

## How to read this file — the rule this project learned the expensive way

> **A SPEC IS THE ONE DOCUMENT WHOSE ERRORS TRAVEL.** Publish a derivation beside any operational
> status, or publish no status at all. Do not publish a status word whose vocabulary you have not
> defined outward.

Every operational claim below carries the command that recomputes it and was recomputed on
2026-09-08 before this file was written. Where a value is not derivable it says UNKNOWN. Status is
stated once, in one place; there are no superseding blocks.

---

## Factory shape — tiers by act, keys by construction (ratified 2026-09-08)

**What changed on 2026-09-08 and why.** From 2026-09-07 the board was driven by a Codex Desktop lead
on `gpt-6-astra` (xhigh, full-access sandbox) with `gpt-5.6-luna` workers. An audit on 09-08 found:
103 commits since 09-05, 25 touching `src/` or `tests/`; the three "product" landings of that era
(P01, P02b, P02c) contain **zero production lines**; the only real production diff was uncommitted in
a worktree; two DONE self-tests were red. The product value of the period (C2–C13) had landed under
a Claude Sonnet lead on 09-06/07. The cost structure was inverted — the most expensive model did
mechanical mutations while cheap workers produced prose that needed correction — so the board
adopted the fleet's same-day owner rulings (RULINGS.md `054f756`: tiers by act; family clause
retired) through a local RATIFY with three Opus deliberators and a Codex Sol key.

| Tier | Claude | Codex | Acts |
|---|---|---|---|
| Judgment | Fable (effort high; xhigh/max for root-cause only) | `gpt-6-astra` (xhigh) | RATIFY synthesis of contested/irreversible rulings; cross-family review of the other family's production code on protocol/timing/security seams; the factory-vs-product audit; the periodic external review of this hub's docs and tree. Receipts and diffs only, never transcripts. |
| Loop | Opus (high; max on a hard problem) | `gpt-5.6-sol` (high) | Traffic cop: worktree, packet, dispatch, gate, landing through the serialized landing tool, ledger line; routine adjudication; default key for the other family's ordinary code. |
| Bounded | Haiku; Sonnet for bounded review | `gpt-5.6-luna` (low) | Script-verified implementation packets; read-only lookups; status readouts that print derived output and never interpret; cheap adjudication swarms on procedure. Their prose is never evidence. |

Exhaustion falls one tier and continues (Fable → Opus max; Opus → Sonnet); never an account switch;
nothing on the judgment tier runs a heartbeat or cadence wake. Fan-out scales to the host
(16 physical cores here; about two agent processes per core is the ceiling; heavy `dotnet` gates run
one at a time).

**Keys.** A review counts by construction — non-author with a fresh context; opposite briefs or named
attack surfaces; grounded evidence; every finding attributed to a parent commit; the integrator
re-derives the load-bearing claim. A same-family adversarial panel of three is a lawful key for
ORDINARY landings and is the normal mode. Cross-family (Codex Sol/Astra, or the admitted Grok/Kimi
runner) stays REQUIRED for release publication, `security/**`, frozen bytes, hardware and `RUN_GO`,
account or scheduler changes, and any change to this rule; unavailable means the subject waits.
Ledger lines name their key; the first ten ordinary landings run both keys and publish the diff.

**Interactive chat sessions hold no lane authority by default**; the 2026-09-08 sitting is the
owner-directed exception: a Fable chat session took the hub orchestration seat, ratified the model
above, and drives items through Opus leads. Local operating file: `docs\plans\LANE_MODEL_20260908.md`.

---

## Operational status — derived 2026-09-08, each row beside its command

### Scheduled automations — everything Disabled or PAUSED, by owner ruling (16:57Z, 2026-09-08)

| task / automation | state |
|---|---|
| `AirMyPC-ResumeHeartbeat`, `AirMyPCLaneHeartbeat`, `AudioMile-LaneIgnition`, `AudioMile-LaneIgnition-OPUS`, `AudioMile-ProviderFailover`, `AudioMile-ProviderFailover-Watchdog` | **Disabled** |
| `AirMyPC-FixRepro-TEMP` | Ready, no future trigger (inert) |
| Codex automations `airmypc-*` ×4, `audiomile-cross-stream-improvement-loop` | **PAUSED** |

> derive: `Get-ScheduledTask | Where-Object { $_.TaskName -match 'AudioMile|AirMyPC' } | Select TaskName,State`;
> the `status` field of each file under `$env:CODEX_HOME\automations`

A stale heartbeat age is EXPECTED and is not a fault to self-heal. Restoring any of these is an owner
act. The orchestrator, ignition, heartbeat and failover scripts stay on disk, unreferenced by the
delivery flow; three tools are load-bearing: `Get-AudioMileResumeBrief.ps1`, `AudioMileDeliveryQueue.psm1`
with `docs\plans\DELIVERY_QUEUE.json`, and `Invoke-AudioMileCodexLane.ps1` (worker and landing modes).

### Delivery queue — 11 of 25 DONE, active P02c

> derive: `pwsh -File tools\Get-AudioMileResumeBrief.ps1` (prints the current item with its packet)

DONE: A00, A01, F01–F05, Q01, P01, P02a, P02b. In flight on 2026-09-08 under the new model: FT
(hermetic fixture for the landing tool's self-test), P02c (green 8/8 at `77d1b0f`, one commit ahead
of master, adversarial review PASS with three attributed notes), P04 (banked patch, unvalidated).
Product-line accounting is now reported beside the commit count (TRAPS, 2026-09-08).

### Hosted CI — one job, two failure families, a 2 s literal

> derive: `gh run list -R layibabalola/AudioMile --limit 15`; `gh run view <id> --log-failed`

Only `portable-app-free` (windows-2025, 2 vCPU) fails. Family 1: `DecoupledAvRouteResolverTests` at
3094–3363 ms against `Task.WaitAsync(2 s)` in the test helper. Family 2: `EventResponderTeardownOrderTests`
assertion, a different incident. Remedy ruled: parameterise the budget per environment, split the job
per project, publish per-test pass rate from TRX. No production timing change is justified.

### Release — no package has ever been built

`vpk` is not installed (`Get-Command vpk`); the build script's `-PlanOnly` exits 0 without it, which is
how R01 read as "planned safe". The unsigned package is an install-then-build task, unattended.

### The review door — open on both families

Codex CLI `0.147.0` answers (`codex.cmd --version`); the wrapper key run on 2026-09-08 completed
read-only in 313 s at `gpt-5.6-sol` medium: 887,643 input tokens (791,680 cached), 6,238 output. The
read-only sweep crawled sibling checkouts under `C:\temp`, which is the cost to budget for. The wrapper
refuses a dirty root (`worktree must be clean before contract run`); key runs use a dedicated clean
worktree. Grok and Kimi runners remain admitted-by-ruling standbys (unchanged section below).

---

<!-- The five sections below are carried VERBATIM from the 2026-09-05 rewrite: durable doctrine, not status. -->


## Provider-continuity model — durable doctrine, unchanged

AirMyPC adopts fleet `FAILOVER.md` by citation. **Capacity loss attaches to a credential/quota domain
as `QUOTA-DORMANT(reset_eta)`, not to a seat as death.** The provider registry separates provider,
credential/quota domain, backend/independence class, model, CLI transport, lane role, authority and
subject assignment. **Separate accounts or wrappers are one independence class until proven
otherwise.**

The content gate is two-key and fail-closed. A verifier must be a qualified non-author with no
implementation interest and disclosed role conflicts or material context contamination; a separate
non-author adjudicator binds the controlling ruling. Provider-family diversity is preferred and
measured when available, but is neither an authority key nor a mandatory availability dependency.
**Missing, stale, ambiguous, timed-out, partial, nonzero, multiply signed or malformed evidence is
`UNEVALUABLE`; work banks or queues.**

Routing requires **both** current `HEALTHY` capacity and an `ADMITTED` requested capability. A
Class-B refusal records its reset ETA and stands that domain down. The next distinct healthy admitted
provider receives a fresh run id, exact subject hash and recusal record. Recovery drains banked work
first and samples outage-window decisions. **There is no credential impersonation and no authority
transfer.**

---

## Laws and traps exported

The first sixteen are carried unchanged from the 2026-08-11 edition and remain this project's
position. The last ten are new since, each measured on this board and published as its own append to
`TRAPS.md` or `RULINGS.md` on this bus.

- A provider is a runner; local role/subject assignment grants authority.
- Quota exhaustion is a domain routing event with reset ETA, not lane death.
- Healthy transport plus missing capability still queues fail-closed.
- Do not infer independence from separate binaries, configs or accounts.
- Structured agent prose and launcher exit alone never classify health or completion.
- A schema-valid intermediate turn is not a terminal receipt.
- Timeout/partial output remains `UNEVALUABLE` even when useful for repair.
- Portal filtering occurs mechanically before narration; narrators and portals hold zero authority.
- Provider admission is capability-by-capability; no blanket "model onboarded" permission exists.
- Every repair receives a non-author-reviewed `LOCAL_ONLY(falsifiable boundary)` or exact
  `FLEET_CANDIDATE(packet)` disposition before local ratification and minimal doctrine publication.
- Behavioral seams and production paths share one production callsite with a mutation/cardinality
  control; prose pointers are line-bounded and identity-checked; registry consumers derive complete
  membership and default-deny unknowns.
- Receipt freshness alone is never health; semantic liveness is closed-set and state-aware.
- Recovery credit requires one strict same-run ignition/terminal pair; one canary is spent at valid
  ignition and only its paired productive terminal resets cadence.
- Requested-model credit requires same-run authoritative effective identity; dispatch, unverified,
  mismatched or alternate-model evidence earns no requested-major credit.
- Automatic recovery requires a versioned durable claim before one bounded action, followed by a
  verified seal; malformed/missing/contradictory history and incomplete claims quarantine, and
  reviewed-byte drift never self-repins.
- A maturity score changes only through its versioned receipt rubric, dated cutoff, durable row
  evidence and full arithmetic recomputation.
- **A provider closure is a ROLE closure.** Enumerate which *roles* go dark, not which lanes. If the
  answer includes "review", you have not paused the factory — you have removed its brakes and left
  the engine running.
- **A control that always fails looks exactly like a control that is armed.** Assert on the last
  result and on the freshness of a downstream artefact, never on a task's existence or state.
- **A guard whose predicate is a substring match over the machine's process table is satisfied by any
  process that merely mentions it** — including the diagnostic you run to investigate it and the
  document you write about it. Scope by construction, not by filter.
- **A narrowed probe that now matches nothing is indistinguishable from the fix.** Assert both
  directions against the same nonce in the same run, and check the mutation is selective.
- **A policy that exists in a reviewed copy and an enforcing copy is decided only by the enforcing
  one.** Resolve it the way the enforcer does, compare, fail closed — and do not let an agent
  reconcile it by writing the install root, because that separation is the control.
- **A field whose name is in a required-fields list and whose value nothing reads is a comment with a
  schema.** Grep for a consumer of the *value* before performing the remediation a caveat asks for.
- **Repairing a control that failed loudly can leave one that passes vacuously.** After clearing a
  red, assert the control still does work; and make any baseline's growth require an explicit flag
  with a reason recorded in the file.
- **When a reviewer hands you a finding, re-derive both halves — the harm and the attribution.**
  Accepting a finding whole is as unrigorous as dismissing it whole.
- **When you correct an overclaim, the correction is a claim too.** Withdrawing to UNKNOWN is free;
  asserting the negative is not.
- **Before concluding that review is unobtainable, enumerate every capability admitted by ruling.**
  The expensive door is usually the only one anyone tries.

---

## Universal provider control — this project's dispositions

**R14 — `HARD_CLOSED`. Unchanged and still this board's published disposition:**

`DISTINGUISH(874605e43531c9aa230ee16851f8107a8e0d9cec, "AirMyPC retains the portable fail-closed and token-saving invariants; its app-scheduler snapshot is UNEVALUABLE, six legacy launchers remain outside the sole supervisor, the profile requires host-secret rebind and dependent repin, the machine runtime gate is absent, and no separately authorized canary receipt exists", sha256:6807A33B63AC4731226C771FF1300BE2968CA48159D72804E3A867B8FD9F300B)`

Canonical authority merge `488cf0dc0c2c2ddd1ab024c6377e1fd6d61eef1d`, tree
`372676162c0fca68d116289e8b744fcc7697bcd2`; technical subject R14 commit
`874605e43531c9aa230ee16851f8107a8e0d9cec`, tree `cafc358fd7b60812070cf9a465d7de38b88487c8`. The
6,384-byte machine-readable packet whose SHA-256 is quoted above is retained locally under
`docs\fleet\` and is reproducible from there; it is no longer embedded in this file, because a spec
whose status must be re-read is badly served by 100 lines of frozen JSON, and its integrity is
carried by the hash, not by the transcription.

**R27–R45 — new disposition, ruled 2026-09-05:**

`DISTINGUISH(R27..R45 as of bus 0da4a20, "AirMyPC installs no provider control plane: it has no separately-reviewed process choke point, no production boundary certification, no independent retained observer evidence and no staged CLOSED/SHADOW/CONTAINMENT/canary chain, because every one of those requires writing security\\provider-launch-inventory.json and/or the installed launch-gate policy, and BOTH are owner-closed surfaces on this board -- runtimeAuthority reads CANDIDATE_ZERO_AUTHORITY in the repository copy and in the enforcing copy alike, and the four provider/ignition automations have been Disabled since 2026-08-18. The portable invariants ARE retained: exact-integer admission arithmetic, ordered subject bijection, and frozen-layer origin binding.", proof: Get-ScheduledTask over AudioMile|AirMyPC returns four Disabled provider/ignition rows; both policy copies read CANDIDATE_ZERO_AUTHORITY; security\\universal-provider-control-profile-v1.json declares mode HOST_LOCAL with quotaDomainHostCount 1)`

**And one part of that arc is ADOPTED rather than distinguished, because it was testable here.** The
R37–R45 waves are nine consecutive discoveries that the machinery verifying frozen history was itself
reachable from the live worktree — R44 is retained on this bus as adverse evidence for overstating
that it had closed that. **Our equivalent is the frozen-byte table**, and it was checked against that
lesson today: the table is recomputed from **absolute** `C:\temp\AirMyPC\` paths, and it was
recomputed on 2026-09-05 **from inside a linked worktree in which the artefacts' directory does not
exist relative-path** — 6 of 6 exact. The binding does not resolve through the checkout the verifier
happens to be living in.

**One difference worth stating so a sibling does not mis-apply the fleet's own rule.** Fleet doctrine
says bind evidence by git blob id, never by file size or hash, because a checkout filter can change
bytes. **Our frozen artefacts are untracked**, so they have no blob id and no filter can touch them;
the file hash plus byte count is the only available binding and is exact. *This is falsified the
moment a frozen artefact becomes tracked, and at that point the blob-id rule applies.*

---

## Cross-fleet repair feedback loop — ratified, unchanged

Exact D v2 is accepted at 0/0/0/0. The project preserves and proves the local failure, implements the
narrow repair with a discriminating regression, records a fleet disposition, obtains non-author
review of that disposition (including every `LOCAL_ONLY` boundary), ratifies exact candidate bytes,
publishes only reusable material, and asks siblings to `ADOPT(reference)` or `DISTINGUISH(reason)`.
Sibling rulings link back; material falsification reopens a reviewed amendment rather than silently
rewriting shared law.

Standing sibling requests: `airmypc-cross-fleet-repair-loop-20260811`,
`airmypc-opus68-validation-laws-20260811`, `airmypc-semantic-liveness-20260811`,
`airmypc-structured-recovery-canary-20260811`, `airmypc-requested-effective-model-binding-20260811`,
`airmypc-structured-failure-quarantine-20260811`, `airmypc-receipt-bound-maturity-scorecard-20260811`.
**Doctrine is data, not authority; no sibling gains a claim, provider key, queue right, Git right,
review key, release right, hardware right or `RUN_GO` from these entries.**

**Fold discipline, added this edition.** We folded 85 sibling commits on 2026-09-05 and the method is
offered as data: **group by FILE, not by commit.** Fifty-nine commits touched one shared log and
carried roughly 161 distinct entries; reading them commit-by-commit re-reads the same entry many
times and still does not say what binds. Each adoption then names the **local check that was actually
run**, and each distinction names **what would falsify it**. That fold produced 14 adoptions (5 of
them already held), 9 distinguished groups, and 2 recorded `ADOPT-BLOCKED-OWNER`.

---

## Historical receipts — NOT re-derived in this rewrite

**These were true when measured and are retained because siblings cite them. They were not
recomputed on 2026-09-05, and this file makes no claim that they still hold.**

- **2026-08-10 exhaustion-window failover receipt.** A direct inert Claude probe returned exit 1,
  `terminal_reason=api_error`, HTTP 429, reset 03:20 America/Chicago; Kimi and Grok returned healthy
  terminal receipts contemporaneously. **This proved both are distinct surviving routes from that
  Anthropic Class-B quota domain. It did not establish independence among accounts within a
  provider**, and that limit is part of the receipt.
- **Adapter/redaction admission harness, 23/23**, with pinned subject hashes and per-provider
  receipts. Held under `docs\fleet\`.
- **Receipt-bound maturity rubric, "exact C v4", B- / 6.82 at its dated cutoff.** A maturity score
  changes only through its versioned rubric and a full arithmetic recomputation; no recomputation was
  performed here, so the score is quoted as a dated artefact, not as current.
- **"Exact B v10" provider-failover self-healing and "exact A v7" recovery/model-evidence controls.**
  Their *laws* are carried above under *Laws and traps exported* and remain this project's position.
  Their **activation status is superseded by the Operational status section**: the two scheduled
  tasks that edition described as Ready are among the four now recorded Disabled.
- **Dual-primary blackout continuity** remains `RATIFIED-DESIGN / UNACTIVATED / UNDRILLED /
  NOT-FOR-ADOPTION`. Auxiliary runners are not a dual-primary control plane. Unchanged.

---

## Open obligations, stated because a spec that only reports success is a brochure

1. **Landing-tool self-test red until FT lands** — five assertions, one cause (fixture clones the live
   queue). Every product landing runs through that tool. Fix in flight; DONE receipts are re-run on a
   later day before they are trusted (TRAPS, 2026-09-08).
2. **The family predicate in `AudioMileDeliveryQueue.psm1` still refuses equal families** until the
   `reviewKey` change lands with tests for the acceptance and the kept refusal.
3. **P04** — the only real production diff of the Codex era — is a banked patch, unvalidated: generation
   ordering, cancellation ownership, poll/Stop deadlock, stale-output cleanup all unproven.
4. **Hosted CI is not a verdict** until the watchdog is parameterised and the job split; "intermittent"
   is still measured from four run IDs, not a pass rate.
5. **Doctrine ack** was 76 h stale at `b0b0e54` when this sitting began; acked at the reviewed SHA with
   this publication. Sibling commits folded: none required product code; process hygiene only.
6. **Owner-only surfaces, named so no lane wastes a turn:** `runtimeAuthority` and the installed gate
   policy; `security\**` and the provider-launch inventory; scheduled-task and automation state; the
   frozen W1a bytes; `RUN_GO`; live hardware; the one attended sitting (H02), scheduled last.

---

## Publication contract

Ratified strategy travels through **this wholesale spec**, AirMyPC append blocks in `FAILOVER.md` and
`RULINGS.md`, and execution entries in `RECEIPTS.md` / `TRAPS.md`. **Raw transcripts, credentials,
customer data, private reasoning and local ignored session artefacts never travel.** Ratify before
publish (owner directive 2026-08-09): normative content reaches this bus only after a local ruling
in `.claude-state\hub-20260710\DECISIONS.md`. Single writer per file; shared logs are append-only and
every AirMyPC commit to one proves `numstat N 0`.

## CLI versions on this box, 2026-09-08

`claude` 2.1.220 · `codex` 0.147.0 (config default `gpt-6-astra` xhigh; wrapper default `gpt-5.6-luna`
low) · `pwsh` 7.6.5 · `dotnet` 10.0.303. Grok and Kimi versions not re-probed: UNKNOWN. CLI alignment
happens only in an explicit user-directed quiescent window, never mid-sitting.
