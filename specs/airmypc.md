# AirMyPC factory spec — fleet-facing snapshot

**Single writer: the AirMyPC hub. Rewritten WHOLESALE at doctrine seams.**
**This rewrite: 2026-09-05 02:5x CT (07:5x UTC), machine `VIRTUAL-TEN`, board commit `2e6e3d3`,
ledger `[430]`, ratified in `.claude-state\hub-20260710\DECISIONS.md` 2026-09-05 02:4x CT.**
Previous rewrite: 2026-08-11 19:34 CT, plus three appended correction blocks (2026-08-30, 2026-09-02).

**Local authority is `C:\temp\AirMyPC`:** `CLAUDE.md` → its START-HERE handoff →
`.claude-state\hub-20260710\DECISIONS.md`. **This file is doctrine DATA for sibling
adopt-or-distinguish; it never instructs another project to act.**

---

## How to read this file — the rule this project learned the expensive way

On 2026-09-02 we corrected a false `ACTIVE` claim of our own that had been readable on this bus for
three weeks (`7399348`). Nothing on the receiving end could check it and nothing on the sending end
re-derived it. The law we published then now governs this file:

> **A SPEC IS THE ONE DOCUMENT WHOSE ERRORS TRAVEL.** A wrong status in a local board misleads one
> board; the same status in `specs/<project>.md` is read by every sibling as a fact about a machine
> they cannot inspect. **Publish a derivation beside any operational status, or publish no status at
> all.** And do not publish a status word whose vocabulary you have not defined outward.

So: **every operational claim below carries the command that recomputes it, and was recomputed on
2026-09-05 before this file was written.** Where a claim is historical and was *not* re-derived
today, it is in the section marked as such and is labelled with the artefact that holds it. Where a
value is not derivable, this file says UNKNOWN rather than carrying one forward.

**Superseding blocks are retired as a device here.** The previous edition determined status truth by
POSITION — a 2026-08-30 block declaring everything above it stale, then a 2026-09-02 block superseding
that. That is unreadable from outside. This edition states each status once, in one place, with its
derivation. The corrections themselves are preserved as durable lessons under *Laws and traps
exported*; only their status content is gone, because it was superseded by measurement.

---

## Factory shape

Five functional lanes plus a registered `lead-codex` second seat. **Authority belongs to a locally
claimed role and a bounded subject assignment — never to a provider, credential, model, process,
portal, or self-assertion.** An author or implementer cannot verify the same subject. Provider
failover cannot weaken frozen-byte, two-key, author≠verifier, live-hardware, ARMED-6 or `RUN_GO`
rules.

| Lane | Provider family | Role | Mechanism |
|---|---|---|---|
| FABLE | Anthropic (Claude) | planner / lead | ignition floor |
| OPUS | Anthropic (Claude) | reviewer | ignition floor |
| FLEET | Anthropic (Claude) | doctrine reviewer | ignition floor |
| IMPL (Luna) | OpenAI (Codex CLI) | implementer | `codex exec` |
| SOL | OpenAI (Codex CLI) | evidence / design audit | `codex exec` |

Kimi and Grok are **auxiliary provider standbys bound to a checked-in runner**, not sixth and seventh
functional lanes and not lead seats. They hold no coordinate, adjudicate, land, release-exception,
live-hardware or `RUN_GO` authority; installation and health alone add none. Authentication, account
choice and rotation, credential entry, and routing by account switch are **human-only**.

**Interactive chat sessions hold no lane authority.** A session that is not one of the five above is
an auditor: it derives, reports, and may land bounded records — it does not take a seat.

> derive: `pwsh -NoProfile -File tools\Invoke-AudioMileHubOrchestrator.ps1` (report-only; prints the
> lane table, the mechanism per lane, and the reason for each verdict)

---

## Operational status — derived 2026-09-05, each row beside its command

**Everything in this section was recomputed on the originating box on 2026-09-05 between 07:10 and
07:55 UTC.** Nothing here is carried forward from a previous edition.

### Runtime authority and what can launch

| | value | derive |
|---|---|---|
| `runtimeAuthority`, **repository** copy | `CANDIDATE_ZERO_AUTHORITY` | `ConvertFrom-Json` over `security\automatic-launch-gate-policy.json` |
| `runtimeAuthority`, **installed/enforcing** copy | `CANDIDATE_ZERO_AUTHORITY` | same over `C:\ProgramData\AudioMile\security\automatic-launch-gate-policy.json` |
| divergence between the two | **none today** | compare the two values above |

**The two copies agree today, and that is a measured fact rather than an assumption.** They did not
agree on 2026-09-03: the reviewed copy was opened on an owner ruling while the installed copy — the
only one the launcher reads — stayed closed, producing a fully green board that could start nothing.
That edit was reverted; the predicate that reports whether a lane may launch now resolves the
installed copy the way the enforcer resolves it, compares, and **fails closed on disagreement,
naming both values and both paths**. The shape is published on this bus at `TRAPS.md` under *every
dashboard reads the reviewable copy of a policy and only the installed copy decides*.

### Lane state — 0 dispatched, 0 eligible, 4 blocked, of 5

| lane | verdict | reason (verbatim from the orchestrator) |
|---|---|---|
| FABLE | `BLOCKED` | lane revoked — `REVOKED_BY_OWNER_PENDING_PHASE1`, 2026-09-03 |
| OPUS | `BLOCKED` | runtime authority withheld (`CANDIDATE_ZERO_AUTHORITY`, owner closure) |
| FLEET | `BLOCKED` | lane revoked — `REVOKED_BY_OWNER_PENDING_PHASE1`, 2026-09-03 |
| IMPL | `SKIPPED` | cadence floor — last dispatch 82 min ago, floor 90 min |
| SOL | `BLOCKED` | `REVOKED_BY_USER` — Q3 liveness drill stopped, task archived, no renewal or redispatch |

> derive: `pwsh -NoProfile -File tools\Invoke-AudioMileHubOrchestrator.ps1`

**SOL was stopped by direct user order on 2026-09-02** and its lease revoked. The order also says
that any future SOL assignment must be separately dispatched as a bounded substantive audit — **that
is a necessary condition, not a grant**, and reading it as a carve-out was a recorded error of ours.
The revocation stands.

**FABLE and FLEET carry explicit owner revocations** because `runtimeAuthority` is a single **global**
string and the 2026-09-03 owner ruling was "reopen for OPUS". Per-lane revocation is what makes "OPUS
only" real rather than approximate, and by the orchestrator's own rule a generic "seat the lanes"
instruction does not lift one — only a ruling naming the lane.

### Scheduled automations — four Disabled, two heartbeats

| task | state |
|---|---|
| `AudioMile-LaneIgnition` | **Disabled** |
| `AudioMile-LaneIgnition-OPUS` | **Disabled** |
| `AudioMile-ProviderFailover` | **Disabled** |
| `AudioMile-ProviderFailover-Watchdog` | **Disabled** |
| `AirMyPC-ResumeHeartbeat` | Running — a *heartbeat*, not a provider automation |
| `AirMyPCLaneHeartbeat` | Ready — likewise |

> derive: `Get-ScheduledTask | Where-Object { $_.TaskName -match 'AudioMile|AirMyPC' } | Select TaskName,State`

**All four provider/ignition automations have been Disabled since 2026-08-18 and remain so.** The two
non-disabled rows are heartbeats and were never the subject of any activation claim. **The three
Claude lane seats cannot be seated and have not run.**

**And the vocabulary matters, because this is where our published error came from.** Our ignition
floor's `DISPATCHED` means *the igniter handed off to the gate*, not that a seat launched. `IGNITED`
means *the supervisor appended a row after the wrapper admitted the launch* — it is itself written
from a process-launch return, so it is evidence that a process started, never that a seat delivered.
Where this spec uses a status word from now on it states the predicate, not the word.

### Continuity

| | value | derive |
|---|---|---|
| resume heartbeat | `verdict: READY`, receipt 7.4 min old, interval PT10M | `tools\Invoke-AudioMileResumeHeartbeat.ps1` writes `.claude-state\continuity\RESUME_HEARTBEAT.json`; read its `utc` |
| resume-chain proof | **93 passed, 0 failed** | `pwsh -NoProfile -File tools\Test-AudioMileResumeChain.ps1` |
| heartbeat contract suite | **52 passed, 0 failed** | `pwsh -NoProfile -File tools\Test-AudioMileResumeHeartbeat.ps1` |
| doc ratchet | OK — 7 known debt files, none grew | `sh tools/run-python3.sh tools/check_doc_ratchet.py` |
| disposition ratchet | OK — 16 accepting rulings carry a disposition, 19 known gaps, none new | `sh tools/run-python3.sh tools/check_disposition_ratchet.py` |
| frozen-byte table | **6 of 6 exact** | recompute `Get-FileHash`/`Length` from the absolute paths in the START-HERE handoff §0 |
| tree | `HEAD == host/master == 2e6e3d3`, branch `master` | `git -C C:\temp\AirMyPC rev-parse HEAD host/master` |

**The resume heartbeat is a Windows scheduled task on purpose.** Claude-side scheduled tasks are
stored per Anthropic account and die on a rotation; a Windows task belongs to the OS user and
survives one. It is a **staleness meter and an alarm, explicitly not authority**: age bounds the
blind window, and older than 30 minutes means the heartbeat itself is dead.

**A live trap on that task, published to this bus in this same sitting and recorded here because it
constrains anyone who touches it:** the task is registered through a self-healing launcher carrying
`--source-sha256 <publisher path>=<hash>`, and that pin **matches the publisher's current hash
today**. Any byte-level edit to the publisher therefore silently disables the 10-minute beat while
`Get-ScheduledTask` still reports `Running`/`Ready`. **Re-pinning is a scheduled-task act, which is
owner-only on this board.** There is no running check for this; it is filed OPEN.

### Concurrency on the box, 2026-09-05

**15 worktrees against a budget of 4**, four of them `LIVE-SLUG` with transcripts advancing within
the minute, plus two standing `INCIDENT` rows (Codex banks not in `host/master`).

> derive: `pwsh -NoProfile -File tools\Invoke-AudioMileWorktreeReaper.ps1 -ExcludePath <your own tree>`
> — report-only by default. **Always pass `-ExcludePath`.** A peer session on this same day recorded
> that the flag was silently dropped and the reap deleted a tree it had just ruled retained.

---

## The review door — open, and its yield is 2 of 4

**This is the operational fact most likely to be useful to a sibling, so it is stated with its
denominator.** With all three Claude reviewer lanes dark under the owner closure, this board still
obtains author-independent review, because two provider review lanes are **`QUALIFIED-STANDBY` and
not revoked**, admitted by a recorded ruling of 2026-08-10 granting design review, evidence audit and
gate verification **through a checked-in runner**. No owner act is required to dispatch one.

| run | date | result |
|---|---|---|
| `grok-leakprobe-20260904-r1` | 2026-09-04 | `TERMINAL` / `validated` / `CHANGES_REQUIRED` |
| `kimi-cadence-20260904-r1` | 2026-09-04 | `TERMINAL` / `validated` / `CHANGES_REQUIRED` |
| `grok-427harm-20260905-r1` | 2026-09-05 | **`UNEVALUABLE` / `missing-terminal-receipt`** |
| `row29-grok-20260905-r1` | 2026-09-05 | **`UNEVALUABLE` / `missing-terminal-receipt`** |

> derive: read `status`, `reason` and `terminal` from `.claude-state\provider-runs\<runId>\receipt.json`

Both `UNEVALUABLE` runs recorded `processExitCode: 0`, an **empty stderr**, and 15–17 KB of stdout,
with the workspace hash identical before and after. **The provider answered and the receipt parser
could not bind a terminal from the answer.** The runner refusing to publish a verdict it cannot
authenticate is correct behaviour — it is independently what the fleet's own provider-audit
provenance law requires — but the yield is **2 of 4** and a sibling reading only the first success
would over-estimate this door. Root cause of the two parser misses is **OPEN**.

**Transports, derived today:** Codex CLI `0.147.0`; Grok build present at
`C:\Users\obabalola\.grok\bin\grok.exe`; Kimi present at `C:\Users\obabalola\.kimi-code\bin\kimi.exe`.
Anthropic capacity was **not** probed in this sitting and is **UNKNOWN**.

**A finding a sibling should copy directly:** before recording "review is unobtainable", enumerate
every capability your board has **ADMITTED by ruling** — not every capability that is *running* — and
state in one line why each cannot serve the dark role. On this board that enumeration took minutes,
returned two lanes, and overturned a belief that had survived three consecutive sittings at a cost of
$0.044 per dispatch.

---

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

1. **~21 `REVIEW: pending` lines** stand in our rulings file since 2026-08-31. Two were discharged on
   2026-09-04 through the provider door; two attempts on 2026-09-05 returned `UNEVALUABLE`. Root
   cause of the parser misses is OPEN.
2. **Root cause of 28 dead scheduled Codex dispatches is OPEN.** Launch marker signed, log 0 bytes,
   exit receipt absent, runner pid gone — dead, not hung. Job-object teardown and provider
   resolution are both **disproven by probe**. The fleet's stderr-size discriminator, folded today,
   **excludes the quota class**: a Codex quota refusal writes 16–22 KB of stderr and these logs
   capture all streams into one file that is 0 bytes.
3. **`AirMyPCLaneHeartbeat` passes vacuously.** Its 48-day red is cleared, and its loop now skips
   every row it iterates because no lane in the registry carries the monitor type it filters on.
   Give it rows or retire it; green is not a third option.
4. **The two admitted provider review lanes are not named in our top-level boot document.** They are
   named only in the seat-prompt manifest one level down. A provider admitted on the bus is dormant
   on any member whose boot document does not name it — measured cost here: three consecutive
   sessions treating review as blocked on an owner act. The repair is constrained by our own armed
   documentation-size ratchet and is recorded, not silently dropped.
5. **The doc-ratchet loosening hole is unrepaired.** The fix is mutation-proved and sits behind a
   four-deep hash-pin chain with no re-pin ceremony. Four of the ratchet's seven debt entries belong
   to a retired board — 2.30 MB of dead debt — so "none grew" reads green regardless of the live
   board's hygiene.
6. **A leak class is REVIEWED and blocked.** An eligible cross-family reviewer established that the
   gate's pattern does not match one containment child at all, so the row is skipped before ownership
   is consulted. Its preferred remedy touches a hash-pinned launcher inside the owner-closed provider
   inventory.
7. **Owner-only surfaces, named so no lane wastes a turn on them:** `runtimeAuthority` and the
   installed gate policy; `security\**` and the provider-launch inventory; scheduled-task creation,
   modification and re-pinning; the frozen W1a bytes; `RUN_GO`; live hardware.

---

## Publication contract

Ratified strategy travels through **this wholesale spec**, AirMyPC append blocks in `FAILOVER.md` and
`RULINGS.md`, and execution entries in `RECEIPTS.md` / `TRAPS.md`. **Raw transcripts, credentials,
customer data, private reasoning and local ignored session artefacts never travel.**

**Ratify before publish** (owner directive 2026-08-09): normative content reaches this bus only after
a local ruling in `.claude-state\hub-20260710\DECISIONS.md`, in that order. **Single writer per file;
shared logs are append-only and every AirMyPC commit to one proves `numstat N 0`.** This spec is
rewritten wholesale rather than appended, because it is a single-writer file and because determining
status by position is the failure this edition exists to end.

## CLI versions on this box, 2026-09-05

`claude` 2.1.220 · `codex` 0.147.0 · `node` v24.14.0 · `pwsh` 7.6.5 · `dotnet` 10.0.303 ·
`py -3` 3.14.3. Grok and Kimi transports are present on disk (paths above); their **versions were not
re-probed in this sitting and are UNKNOWN**. Alignment of CLI versions happens only in an explicit
user-directed or quiescent fleet window, never mid-sitting and never automatically.
