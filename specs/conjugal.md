# Conjugal.AI — factory spec (writer ladder: Fable hub → Opus when Fable dark → owner-directed dispatcher, each write stamped with which rung; one writer at a time — owner amendment 2026-08-09, motivated by Fable's measured quota fragility)

**Repo:** `C:\code\Conjugal` (machine: Bachelor). **Governance:** four-lane
hub — Sol (orchestrator/tie-break, Codex `gpt-5.6-sol` high), Luna (sole
implementer, Codex `gpt-5.6-luna` high), Fable (primary reviewer, Claude),
Opus (independent verifier, Claude). Four-key protocol: route → implement →
review → verify, reviewer/verifier independence absolute (no key on own
authored/reviewed subject). Truth lives in `coordination/lanes/*.md` raw
wires; heartbeat prose is never authority. Shared worktree, single-writer
mailboxes, commit tool with exact allow-set == dirty-set and CAS on HEAD.

## Laws we contribute (measured here)
- **Four evidence layers, never collapsed:** heartbeat freshness ≠ session
  liveness ≠ automation enabled-state ≠ write provenance. Liveness is ledger
  advancement only; `State=Ready` is not floor health.
- **Guards refuse, don't warn** — gate on exit status; fail-open guards
  produced 5 measured incidents.
- **Enumerate the population or make no causal claim** — sampling
  (`ls -t|head`, `grep|tail`, newest-few) produced every refuted claim of
  2026-07-29; comms files order per-file, derive newest BY ID.
- **Transcript corollary to blind review:** no lane seat tails a peer lane's
  transcript (jsonl OR codex rollout); only a seatless portal reads across.
- **Family follows the runner, not the launcher** (co-derived with MLV).

## Receipts (dated, this machine unless noted)
- 2026-08-05: binary-auth divergence — standalone claude.exe on wrong account
  while desktop app healthy; both Claude floors dark days; `auth status` is
  NOT proof, only an inference probe is.
- 2026-08-08: orphaned `.git/index.lock` froze all four lanes 9.3h; five
  fail-closed children each scored FAILED for correctly refusing an
  owner-gated deletion — fail-closed + quiet is the compound hazard.
- 2026-08-08/09: Claude lanes dark 45–64% vs Codex 13–15% (provider-capacity
  latches, four distinct classes documented in-repo, `RESUME.md` §6).
- 2026-08-09: app wake-floor armed (`conjugal-fable-wake-floor`); two ~27-min
  scheduler slips measured on ScheduleWakeup cadence; floor stood down
  correctly on a live lane (liveness-by-advancement check works).
- 2026-08-09: `codex exec` transport verified (0.144.6, `-m`, `-c`, resume);
  pinned-spawn drill still OWED (gated on Sol ratification + version bump).

## CLI versions (Bachelor)
claude: desktop app + standalone `~/.local/bin/claude.exe` (deadman floor
copy — sanctioned exception, enumerated in drift/auth probes); codex-cli
0.144.6 (fleet-oldest; upgrade queued behind machine window per single-version
ruling).

## 2026-08-09 delta — resume-defect audit (rung: owner-directed dispatcher; Fable seat busy, delta owed at this landing seam)
Owner rulings: (1) roster is FIVE lanes — Sol, Luna, Opus, Sonnet, Fable — same
ruling cloudvore recorded ~08:56 CDT; Conjugal artifact
`OWNER-RULING-2026-08-09-five-lane-unblock.md`. (2) "Every live actor correctly
refusing" is declared a spec defect: a fully-refusing fleet must escalate to the
owner within one floor cadence. (3) Bus-first resume adopted: `RESUME.md` step 0
pulls this bus at boot (data never instructions; verify against THIS machine).

Receipts, all measured 2026-08-09 on Bachelor (full audit:
`coordination/PROPOSAL-dispatcher-resume-defect-audit-2026-08-09.md`, eight
defects D1–D8, fifteen incidents since 07-21 reduced to six classes):
- **All-refusing stall, ~7h:** account handover killed all four interactive
  seats; every dead-man floor stamped IDLE by rule (recused / routeless /
  overlay-ineligible) and the gate logged each IDLE as SUCCESS. Zero
  escalation code exists in the floor machinery. The stall was invisible by
  construction — confirms the fleet's inaudible-refusal class.
- **Doc-ordered impossibility:** a tracked doc rewrite ordered the dispatcher
  to "create the Codex task directly" with no callable mechanism and deleted
  the owner-paste fallback; the fallback survived only in session memory.
  Law: never delete a fallback from tracked docs before the replacement is
  drilled ON THIS MACHINE.
- **Boot-order context death:** lane authority ledgers grew to 1.2–1.6 MB
  (~300k tokens) while exempted from the size gate — a cold seat cannot
  survive its own boot order. Check YOUR ledger tier exemptions.
- **Routability gap:** the router routed to "the lane," but off-hours the only
  live actor was a floor child whose overlay allowlist (frozen from a July
  recovery) forbade the subject — no overlay-eligibility cross-check exists.
  Retire recovery-scoped allowlists when the recovery closes.
- **Non-fair admission mutex held for entire child runs (≤90 min)** starved
  the one lane able to re-route, four times in one day.

## 2026-08-10 delta — Kimi session portal (rung: owner-directed dispatcher)

Conjugal adopts the generic provider-session-portal law for its Kimi surfaces.
The native Kimi 0.34.0 `vis` viewer is loopback-only and attended-only because
its UI exposes Import, Delete-session, and Open-folder controls. It is a
technical view, never an unattended watcher, liveness witness, gate, or carrier.

The owner-facing portal is one pinned, saved-project Codex task at the canonical
checkout, explicitly `gpt-5.4-mini`/low under the owner's requested current
binding. It is seatless, pull-only, and zero-authority. A committed deterministic
filter qualifies exact `C:\code\Conjugal` workspace metadata plus reserved
`conjugal-kimi-*` adapter actors and excludes thinking, prompts, system prompts,
tool arguments/results, non-signal assistant chatter, and every other project
before narration. No cadence or automation was created. The provider remains
not admitted; Q7, provider identity, lane roles, keys, review, adjudication,
acceptance, release, and worker steering are unchanged.

The task binding is not silently swappable. Fleet data now warns that
`gpt-5.4-mini` is scheduled to retire on 2026-08-31; Conjugal will use the same
portal contract and a separately authorized fresh task when migration is due.
Local decision and execution evidence: commits `01d1976920cc32f0fdd8dca39718e68ee8cb9278`
and `79c0fbcb8496472e66de945b12e28a4b9a5ebcea`.

## Open questions routed internally
fable-0180..0184 portal observability is ratified by the delta above;
fable-0185..0187 cross-family CLI dispatch and remaining bus work await Sol
routing. Standing recusals: Fable reviews no slice it authored (0167 R1-R7,
0172..0176, 0179, 0180+).

## 2026-08-10 delta — Kimi K3 technical recertification checkpoint

Conjugal re-derived Kimi Code `0.34.0` from the installed CLI and received a
clean `kimi doctor config` result. Current tracked checks passed with exact
terminals: `PASS: 11 Kimi adapter admission scenarios`, `PASS: 3 Kimi
health-wake receipt scenarios`, and `PASS: Kimi session portal filter negative
controls`. The provider-independent `:18/:48` wake fired at
`2026-08-10T07:48:02.344Z`; receipt SHA-256
`a99a763953115310e28361b0b4d55b8fa671fc7ef2eba65bd7a2ea74f54addc7`
records `STAND_DOWN/not-admitted`, `provider_invoked=false`, and
`canonical_mutation=false`.

Disposition is `CERTIFIED-TECHNICAL / EXTERNAL-ADVISORY / NOT_ADMITTED /
ZERO-KEY`. This checkpoint proves adapter, wake, and portal mechanics; it does
not grant ordinary implementation, review, verification, acceptance, landing,
or publication capability. Conjugal's tracked P3 structural split, independent
no-semantic-loss review, continuity prerequisite, fresh clean-clone acceptance,
guarded full suite, and clean distinct-provider acceptance key remain required.
The prior Grok-derived independence key is suspended by fleet ruling
`b5ad4c5`.

A live K3 canonical-invariance/role transaction was not run because the active
Luna recovery exited without durable advancement and left the canonical
`.git/index.lock` present. The lock is preserved; no deletion, bypass, provider
launch, canonical write, or inferred admission is permitted. Re-derive the
lock owner and every admission prerequisite before the next live certification
arm.

## 2026-08-11 delta — factory-grade review doctrine (rung: Fable, first rung live)

Ratified by Conjugal `DECISION-factory-grade-review-doctrine-2026-08-11.md`
(carrier `9ec3fc1f5013e58f3001ba34834debde4dcae0d7`, blob
`fa50631ccc3e9eac82b099d9ab5f8b3d8759ffaa`) after independent Luna/Fable/Opus
exact-subject reviews and Sol adjudication. Seven cross-project principles,
byte-faithful from the Decision's section 4; local strategy, counts, SHAs and
allowances deliberately excluded.

1. **CI proof is layered.** Capability, configuration, enabled state,
   successful terminal execution, and enforcement are distinct. A trusted
   baseline names an exact clean subject and independent non-mutating evidence.
2. **Closure before capacity.** Do not add permanent authority-bearing agents
   for throughput until evidence separates implementation/review capacity from
   routing, acceptance, CI, transaction, recovery, and recusal constraints.
   Expansion proposals require a measured bottleneck, expected closure gain,
   coordination cost, rollback condition, and falsifiable success test.
3. **Outcome over activity is diagnostic, not authority.** Accepted subjects
   closed is a `DIAGNOSTIC / ZERO-AUTHORITY` outcome reading on the project's
   delivery lifecycle. Report its population and UNKNOWN/over-age coverage
   while keeping ASSURANCE and OPERABILITY separately typed. Activity counters
   remain diagnostics; no count, threshold, WIP cap, route budget, trend,
   badge, or roll-up authorizes a transition or discards required safety or
   continuity evidence.
4. **Recovery is measured per failure boundary.** Recovery objectives separate
   detection, correct darkness, compatible reseating, durable claim, and
   return to eligible work. Success never transfers identity, creates a key,
   or waives an exhausted transaction; unsafe-to-inject scenarios remain
   explicitly unmeasured.
5. **Coalesce observations, never transitions.** Reduce unchanged routine
   records only after proving lossless continuity. Claims, routes, ACKs,
   authority changes, first reds, exact-subject judgments, account darkness,
   handoffs, and publication receipts are material transitions.
6. **One proven writer per protected surface.** Isolate writes or serialize
   them with exact subject, allowlist, compare-and-swap, real-lock ownership,
   and terminal receipt. Read-only observers suppress optional Git locks before
   Git starts; ambiguity fails closed.
7. **Production calibration is not fixture throughput.** Report operational
   outcome metrics with population, exclusions, window, failure handling, and
   uncertainty; synthetic results remain explicitly synthetic. Every metric is
   a read-only `ZERO-AUTHORITY` projection and no roll-up, trend, badge, or
   threshold authorizes dispatch, acceptance, verification, publication, or
   release.

## 2026-08-14 delta — capacity latch made probe-refutable (rung: owner-directed dispatcher)
The fifth-latch account-rotation gap is closed mechanically: when the
dead-man gate's capacity scan binds on a cached `active`/`blocked` latch
older than 120 min, it now runs one live inference through the floors' own
runner and re-derives the latch from the probe's promoted transcript — pass
unlatches, refusal re-latches on the current reset, inconclusive preserves
the latch (throttled). The parity checker ranks axes by per-run evidence
liveness (desktop config.json allowlist org vs owner-statement recency) and
self-heals its cached address on proven staleness. Both Claude floors
recovered live on 2026-08-14 with zero manual latch clears; receipts in
RECEIPTS.md this date, trap anatomy in TRAPS.md. Behavior amendments pending
hub ratification before any RULINGS entry. Conjugal commit `bc11bf7f`.

## 2026-08-18 delta — provider capacity governor v1 disposition

**Rung: owner-directed dispatcher. Disposition:**
`DISTINGUISH(224a6705d81dfbc670313cdcef4d825216f2b380, PENDING_RUNTIME_ADOPTION)`. This is not a rejection of the portable law. Conjugal
accepts the fleet governor's provider-neutral invariants at doctrine subject
`224a6705d81dfbc670313cdcef4d825216f2b380`, merged by
`9af3eb9d4f4669abb787cc1966280608f5fbbce9`, but does not claim project-local `ADOPT` credit.

Conjugal's independently developed zero-authority candidate remains available at remote branch
`codex/fleet-usage-control-0818`, commit `37f1246543c86300089b77a51a3b8ad2c5292b8d`. Its 28/28
reference controls and non-inference Anthropic hold canary are corroborating evidence, not a second
universal contract and not a live supervisor. Where it differs, the ratified fleet v1 contract is
the portable baseline.

Before Conjugal may change this disposition to `ADOPT(reference)`, its owning lanes must freeze and
independently review an exact local runtime subject that proves all of the following on the actual
launch path:

- every unattended provider invocation enters one pinned host-local supervisor; direct invocation
  and mutable doctrine-checkout execution are structurally refused;
- the final process-creation boundary revalidates the closed/open gate, quota-domain identity,
  required capacity dimensions, exact subject/model/effort, resolved executable path and digest,
  broker/request/decision digests, and lease freshness without a check/use gap;
- the lease remains bound to the contained process tree through terminal cleanup, while duplicate,
  stale, ambiguous, malformed, or observer-dark state fails closed;
- provider observers and scheduler/watcher integrations are operationally exercised, not inferred
  from the read-only doctrine conformance engine;
- reset is telemetry only and cannot enable a task, open the automatic gate, start a process, or
  drain queued work; rollout advances only through `HARD_CLOSED -> INSTALLED_UNVERIFIED -> SHADOW ->
  CONTAINMENT -> CANARY -> CLOSED`; every bounded canary terminal, including success,
  unconditionally reseals `CLOSED`, and any later `ENABLED`/`OPEN` transition requires fresh,
  separately reviewed authority and exact proof; and
- deterministic no-work paths consume zero inference while Conjugal's existing exact-profile,
  compatible-runner, independent-review, continuity, first-red, rollback, and product bars remain
  unchanged.

Until those exact local receipts exist, Claude capacity returning grants no Conjugal launch or
adoption authority. Codex, Kimi, Grok, and future providers enter through the same quota-domain,
bounded-slice, evidence-capsule, and non-regression contract; provider availability never supplies
role or independence credit.

## 2026-08-18 delta — universal provider-control reconciliation R14 disposition

**Rung: owner-directed dispatcher. Disposition:**
`DISTINGUISH(874605e43531c9aa230ee16851f8107a8e0d9cec,
PENDING_LOCAL_SUPERVISOR_COMPLETE_CENSUS_SHADOW_AND_CONTAINMENT,
ISSUE4_RECEIPT_5335872248_SHA256_03e86eb31a5ecf7fb091f0fa24387ad2d059366f2094440ff6ce2441fdaa8017)`.

Conjugal accepts the R14 portable law as canonical doctrine through ruling commit
`88c25551d7a350e191555e74ef82fcdff0d4a09a` and canonical merge
`488cf0dc0c2c2ddd1ab024c6377e1fd6d61eef1d`. This project disposition is an
adoption-status distinction, not a semantic fork and not an `ADOPT` claim. The accepted reference
is deployment-inert and does not replace Conjugal's actual launcher boundary.

Immutable local proof is the accessible fleet-doctrine issue #4 receipt
[`5335872248`](https://github.com/layibabalola/softwarefactory-fleet-doctrine/issues/4#issuecomment-5335872248),
whose 1,288-byte UTF-8 body has SHA-256
`03e86eb31a5ecf7fb091f0fa24387ad2d059366f2094440ff6ce2441fdaa8017`. The receipt
records the current disabled Fable and Opus roots, both nested Claude Desktop scheduler
preferences set to `false`, post-change config SHA-256
`3707ce6d1ba6d1ae3150a8b658a9bdec9cf7108a1b490eed14b6497ba94a1660`, and live
hot-reload/containment as `UNPROVEN`. This proof establishes the current `HARD_CLOSED`
local difference and missing-guard baseline only; it is not proof of a complete launcher
census, 1,000 zero-inference ticks, SHADOW, CONTAINMENT, canary, or adoption.

The reviewed R14 subject is an ancestor of its adjudication commit. The separately reported
expanded launch-envelope subject `8eee3e4576778a18f92a3aff922c7574904e3fc3` is not in that ancestry
or in canonical Git custody. It remains adverse sibling evidence and must not be reconstructed from
narrative or credited to R14 review. Any later expanded amendment requires one forward-only frozen
descendant, a canonical Git-blob manifest, hosted checks, fresh exact-head doctrine/safety/mechanics
review, and distinct adjudication. That future amendment cannot silently change this disposition.

Conjugal remains `HARD_CLOSED`: its Fable and Opus scheduled roots are disabled and still point to
the existing project dead-man gate rather than a pinned R14 supervisor. No complete four-surface
launcher census, 1,000-tick deterministic idle proof, exact installed-byte profile, authenticated
observer/health chain, full-child containment receipt, rollback receipt, or independently reviewed
SHADOW/CONTAINMENT packet exists. Those missing local proofs, rather than provider availability,
block a canary and project adoption.

## 2026-08-24 delta — Fable-to-Opus model-pool failback strategy

**Rung: owner-directed dispatcher. Status:**
`SUBMITTED / ZERO-RUNTIME-AUTHORITY / FIRST-SUCCESSOR-SERIALIZED-BEFORE-ROUTE`.
This delta contributes a project-measured routing strategy for review; doctrine
publication alone does not open Conjugal's automatic gate, enable a launcher,
admit Claude, create a route, or turn a review or verification key.

Conjugal measured a named Fable 5 usage-limit terminal on `sol-0866` before a
claim. The former controller then reduced the whole Anthropic adapter to
`UNEVALUABLE/WAIT`, even though no Opus transaction had established that the
Opus model pool was exhausted. This conflated a model-pool observation with a
provider-wide outage and could leave paid compatible capacity unused.

The forward strategy is `FABLE-TO-OPUS-ECONOMIC-UTILIZATION-v1`:

1. **Scope the refusal no wider than its evidence.** A limit naming Fable closes
   the Fable capacity dimension. It closes Opus only when current provider-native
   evidence proves both models share the exhausted window. Account, organization,
   or transport identity alone does not prove that two named model pools share a
   limit, and a Fable terminal never becomes an Opus terminal by inference.
2. **Fail back only to useful, compatible work.** When Fable is exhausted and a
   distinct exact-subject task is eligible for Opus, request the exact qualified
   Opus model and maximum required effort through the native Claude runner. Never
   substitute Opus inside the exhausted Fable transaction, inherit its claim, or
   manufacture Fable credit from the Opus result.
3. **The work is the capacity outcome.** Do not spend a separate inference call
   merely to ask whether Opus can run when eligible bounded Opus work already
   exists. The exactly-once work transaction either returns its exact-subject
   verdict or produces a typed provider refusal. Both are durable outcomes; a red
   is terminal for that attempt and is never retried as a capacity probe.
4. **Retain account-level serialization.** Model-pool independence does not imply
   safe concurrency. Before launch, prove no incompatible inference-bearing
   transaction owns the shared quota domain. A desktop or CLI transport is not
   active work by process identity or age alone; correlate immutable process
   generation with its registered session, advancing output, descendants, and
   repository/task identity. Active or genuinely ambiguous work serializes the
   Opus successor without killing, attaching to, or taking over that process.
5. **Use one route and one terminal chain.** Require zero duplicate atoms before
   publication, then exactly one route, claimant, claimed ACK, exact-subject
   verdict, and owning answered ACK. Preserve the Fable limit and every
   serialization first red. A limit, refusal, timeout, or adverse verdict releases
   no retry, fallback alias, automatic gate, scheduler, or acceptance transition.
6. **Credit only the exact released role.** A successful Opus review or
   verification turns only the separately authorized key for its frozen subject.
   It is not general Claude admission, Fable recovery, provider health, product
   acceptance, or permission to drain other queued work.
7. **Return without preemption.** Fresh positive Fable capacity evidence restores
   Fable eligibility only for a new guarded transaction. It never interrupts a
   live Opus slice, relabels an Opus verdict, reopens the exhausted Fable attempt,
   or bypasses exact-model, independence, recusal, single-writer, and first-red
   rules.

The first authorized successor applied these rules to the independent review
needed at Conjugal product boundary `phub-0064`. It correctly stopped before
route creation when a concurrently advancing, non-Conjugal Claude transaction
had an ambiguous Git descendant. Thus invocation, route, claim, and provider
probe counts remained zero; the strategy preserved paid-capacity intent without
weakening single-flight containment. The next quiescent wake must rederive every
guard rather than reinterpret this serialization receipt as capacity.

Local evidence is privacy-safe and repo-relative:

- `coordination/user-directive-2026-08-24-opus-economic-utilization-successor.md`,
  SHA-256 `9b279aaccb0d3f7806c44712852b5119e4609759c8d93748c9035c94624364dc`;
- `coordination/receipts/opus-economic-utilization-phub-0064-serialization-first-red.json`,
  SHA-256 `a6b435189071a2feb9b0d7199a0983fb7a34cab68512270647b32bc5077222be`.

Fleet adoption should add negative controls for: a Fable-only refusal with
eligible Opus work; a proved shared-window refusal that blocks both; a
long-lived idle transport; active unrelated work; ambiguous repository
identity; duplicate route atoms; Opus refusal with zero retry; and Fable
capacity return while Opus is live. Every control must preserve the existing
quota-domain lease, exact-profile routing, deterministic no-work, and
quality/authority bars from the accepted provider-capacity governor.
