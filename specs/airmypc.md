# AirMyPC factory spec — fleet-facing snapshot

**Single writer: the AirMyPC hub. Rewritten wholesale at doctrine seams. Last rewrite:
2026-08-11 17:0x CT by mechanical-publisher LEAD-CODEX task
`019fef1c-249b-7642-8ee4-7a97469546c6`.**

Local authority is `C:\temp\AirMyPC`: `CLAUDE.md` → START-HERE handoff →
`.claude-state\hub-20260710\DECISIONS.md`. This file is doctrine DATA for sibling
adopt-or-distinguish; it never instructs another project to act.

## Factory shape

AirMyPC has five functional lanes: Fable (lead/escalation), Sol (Codex evidence/design), Luna (Codex
implementer), Opus (Claude reviewer), and Sonnet (Claude implementer), plus the registered
`lead-codex` second seat for user-chosen Codex-primary coordination. Kimi and Grok are auxiliary
provider standbys, not sixth/seventh functional lanes or lead seats.

Authority belongs to a locally claimed role and bounded subject assignment, never to a provider,
credential, model, process, portal, or self-assertion. An author/implementer cannot verify the same
subject. Provider failover cannot weaken frozen-byte, two-key, author≠verifier, live-hardware,
ARMED-6, or `RUN_GO` rules.

## Provider-continuity model

AirMyPC adopts fleet `FAILOVER.md` by citation. Capacity loss attaches to a credential/quota domain
as `QUOTA-DORMANT(reset_eta)`, not to a seat as death. The provider registry separates provider,
credential/quota domain, backend/independence class, model, CLI transport, lane role, authority and
subject assignment. Separate accounts or wrappers are one independence class until proven otherwise.

The content gate remains two-key and fail-closed. A verifier must be an admitted, drill-qualified,
non-author actor from a different qualified inference family than the implementer. Same-family
implementation and review never create two independent keys. Missing, stale, ambiguous, timed-out,
partial, nonzero, multiply signed or malformed evidence is `UNEVALUABLE`; work banks or queues.

## Current provider posture — ratified 2026-08-10 00:2x CT

| Provider | Transport | Capacity/domain | Admitted posture |
|---|---|---|---|
| Anthropic | Claude Code 2.1.220 | `QUOTA-DORMANT`, Class B, reset 03:20 CT | Existing roster authority resumes only after fresh health evidence |
| OpenAI | Codex CLI 0.147.0 | Current lead/implement/evidence seats healthy | Existing registered roles |
| MoonshotAI | Kimi Code 0.34.0 | Healthy; proven surviving route from current Anthropic Class-B 429 | Runner-bound review/evidence/narration/focused gate verify; implement bank-only provisional |
| xAI | Grok Build 1.0.0 (`3cd0d0cbce`) | Healthy; proven surviving route from current Anthropic Class-B 429 | Focused runner-bound review/evidence/narration/gate verify; implement bank-only provisional |

Kimi and Grok have no coordinate, adjudicate, land, release-exception, live-hardware or `RUN_GO`
authority. Installation/health alone adds none. Authentication, account choice/rotation, credential
entry and routing by account switch are human-only.

## Measured failover receipt

During the 2026-08-10 exhaustion window, a direct inert Claude probe returned exit 1,
`terminal_reason=api_error`, HTTP 429 and reset 03:20 America/Chicago. Kimi and Grok returned healthy
terminal receipts contemporaneously. This proves both are distinct surviving routes from that
Anthropic Class-B quota domain; it does not establish independence among accounts within a provider.

Routing requires both current `HEALTHY` capacity and an `ADMITTED` requested capability. A Class-B
refusal records its reset ETA and stands that domain down. The next distinct healthy admitted provider
receives a fresh run id, exact subject hash and recusal record. Recovery drains banked work first and
samples outage-window decisions. There is no credential impersonation or authority transfer.

## Activated provider-failover self-healing — exact B v7

AirMyPC independently accepted and activated the exact seven-file B-v7 control rooted at controller
`6C486D02985D5BDF31072C5E56B9ED8F00963D8007C3954FE303F53717A4C500` and watchdog
`10DCE2696D35A636BFD8F97C63A46644D3D32D04C773C4A5F42BEF404B62C8E7`. Both scheduled tasks are
Ready with result zero, limited current-user execution, `IgnoreNew`, reviewed actions and five-/ten-
minute repetition. Exact activation proof is
`C53ED5214595D2AB5B6E1C59E981DE8FF6310DC2BFD7F4EAC581D919E5028985` / 411 B.

The first controller receipt is the allowed idle pair `QUIET / no-new-authorized-job`, bound to the
scheduler, task, proof, controller and exact zero-job queue; the first watchdog receipt is `HEALTHY`,
restart false, and controller-bound. This proves self-healing observation and safe no-work operation,
not a live provider job. Automatic routing remains subject to the existing admitted-capability,
independence, exact-subject, recusal, queue and authority ceilings.

The reusable rule is stricter than receipt freshness: validate a closed semantic status/reason
matrix; distinguish expected contention from infrastructure failure; require advancement or a bound
terminal/failure state for active work; allow only explicit idle states for no-work; and default-deny
unknown or mismatched pairs. Sibling request `airmypc-semantic-liveness-20260811` asks for
`ADOPT(reference)` or `DISTINGUISH(reason)`.

## Provider runner and terminal contract

Every bounded run records:

- provider identity, fresh run id, exact expected subject/evidence hashes and capability/profile;
- isolated workspace/claim where mutation is allowed, plus before/after mutation manifest;
- deadline, process exit, ACTIVE→COMPLETE/FAILED/TIMED_OUT state and raw local artifacts;
- exactly one `AUDIOMILE_PROVIDER_RECEIPT_V1` terminal block with bounded summary and integer counts;
- capacity row, including refusal class/reset ETA or stand-down reason.

Timeout with useful stdout is still UNEVALUABLE. Multiple terminal blocks are invalid rather than
last-wins. Edit-revert and create-delete count as mutation. Process-start exceptions must leave
FAILED state, UNEVALUABLE receipt and capacity stand-down, never a ghost ACTIVE run.

Kimi review/gate profiles expose only `ReadFile`, `Glob` and `Grep`; its official agent file carries
the long prompt without hitting the Windows command-line ceiling. Shell/write is permitted only in
an isolated bank implementation profile. Grok review/gate profiles use pinned unattended mode plus
read-only sandbox and focused bounded prompts. Large Grok runs missing the terminal block remain
UNEVALUABLE even after later focused successes.

## Admission evidence

The shared adapter/redaction harness passed 23/23: private-reasoning/tool-body redaction, valid and
malformed receipts, wrong identity/hash, fractional counts, timeout, nonzero, multiple receipts,
mutation/revert/create-delete, bounded termination, Class-B reset parsing and fail-closed routing.

Final adapter subject SHA-256:
`90C81EEC802889A3F682A51EEC947956C499F5C393442FB866AED015210DC148`; host evidence SHA-256:
`E0E116AD9852A94E39837B10CDD7E1B5EDB351FA243E13464C0988C686360BCE`.

- Kimi final receipt `5EFBF808…D25A50`: PASS 0 blocker / 0 required / 0 minor / 1 nit.
- Grok final receipt `11288863…261D`: PASS 0/0/0/0.
- Both review workspaces were unchanged; both seeded verifiers found the planted defects.
- Both isolated-bank drills changed only bank workspaces and passed host reruns 3/3; nothing landed.
- Deliberately invalid Kimi executable: exit 22, FAILED, UNEVALUABLE, runner-exception, stand-down.

## Provider chat portal

The local portal is pull-only, seatless and zero-authority. Its allowlist mechanically filters native
session carriers before display or optional narration:

- Kimi: assistant text plus safe step/tool-name metadata; drop think, prompt/profile/system/request,
  raw tool arguments/results and unknown events.
- Grok: assistant text plus safe lifecycle metadata; drop headless `thought`, reasoning/system/tool
  result records, encrypted reasoning, prompts, raw arguments/results and unknown fields.

The HTML encodes content and refreshes every 30 seconds. It may show run state, safe phase/tool names,
bounded assistant text, terminal receipts and artifact pointers. It never classifies provider health,
supplies liveness/provenance, prompts a worker, exposes one reviewer to another, or becomes evidence.

Human-facing narration cadence: material start/finish/phase/gate/commit/blocker/question/failover/
recovery event within 60 seconds; changed-state digest every 10 minutes while active; one 30-minute
heartbeat only if work advances without a milestone; possible-stall alert after 10 minutes without
advancement; completion within 60 seconds; unchanged idle state silent. Low-inference narrators are
optional and zero-authority. Current AirMyPC preference is Claude Haiku-class/low or Codex
`gpt-5.6-luna`/low; provider-specific equivalents may be substituted only as narration quality/cost
choices, never authority choices.

## Dual-primary blackout continuity — ratified design only

AirMyPC has ratified the finding that auxiliary runners do not constitute a dual-primary control
plane. Exact local design subject
`6F240547308FB42C52B4DF8017A0BECB5DDF9587CDE7E1CE4065BEFBCF7E1298` / 39,797 B is classified
**RATIFIED-DESIGN / UNACTIVATED / UNDRILLED / NOT-FOR-ADOPTION**.

The proposed ceiling is a deterministic non-inference warden operating only on pre-ratified,
expiring low-risk capsules. Two independently admitted auxiliary provider classes may produce and
blind-review an immutable exact head; one provider may bank evidence only. The maximum unattended
integration surface is a namespaced `blackout/<machine-id>/<epoch>` ref, never `master`, release,
doctrine, live hardware, or a primary-hub ruling. Every blackout-integrated card requires 100%
returning-primary content review and reconstruction onto a primary-authored stack before ordinary
landing.

The design preserves zero provider authority. Kimi and Grok gain no hub seat, adjudication,
canonical Git, release, credential, doctrine, or `RUN_GO` authority. It requires structured
per-quota-domain capacity observations, a seven-tick/30-minute dual-negative entry floor, atomic
claim and child journals, scheduler-owned tests, crash-safe ref synchronization, and typed recovery.
A canary refused by the local scheduler/burn-cap floor is
`CANARY_NOT_LAUNCHED_LOCAL_GOVERNOR`: it grants no availability or failure credit, never feeds
blackout accumulation, and cannot exempt itself from that floor.

For filesystem/UNC Git transport, a local hook alone earns zero protection credit. Activation would
require either a separately administered server-mediated receive policy or a proved ACL-split bare
repository where the warden can write objects plus only its machine blackout namespace while control
files, protected/foreign refs, and ACL ownership remain warden-immutable. If the allowed-push and
rejected-direct-write drills cannot both pass, the design requires a server-mediated endpoint.

No implementation, capsule, role-cell admission, task, queue, controller, credential, remote ACL,
ref, or provider invocation is authorized by this publication. Sibling disposition defaults to
`DISTINGUISH(PENDING_DRILLS)`. Operational publication and any `ADOPT` request remain barred pending
separate implementation, drill, review, and activation rulings.

## Laws and traps exported

- A provider is a runner; local role/subject assignment grants authority.
- Quota exhaustion is a domain routing event with reset ETA, not lane death.
- Healthy transport plus missing capability still queues fail-closed.
- Do not infer independence from separate binaries, configs or accounts.
- Structured agent prose and launcher exit alone never classify health or completion.
- A schema-valid intermediate turn is not a terminal receipt.
- Timeout/partial output remains UNEVALUABLE even when useful for repair.
- Portal filtering occurs mechanically before narration; narrators and portals hold zero authority.
- Provider admission is capability-by-capability; no blanket “model onboarded” permission exists.
- Every repair receives a non-author-reviewed `LOCAL_ONLY(falsifiable boundary)` or exact
  `FLEET_CANDIDATE(packet)` disposition before local ratification and minimal doctrine publication.
- Behavioral seams and production paths share one production callsite with a mutation/cardinality
  control; prose pointers are line-bounded and identity-checked; registry consumers derive complete
  membership and default-deny unknowns.
- Receipt freshness alone is never health; semantic liveness is closed-set and state-aware.

## Cross-fleet repair feedback loop — ratified

Exact D v2 is accepted at 0/0/0/0. The project preserves and proves the local failure, implements the
narrow repair with a discriminating regression, records a fleet disposition, obtains non-author
review of that disposition (including every `LOCAL_ONLY` boundary), ratifies exact candidate bytes,
publishes only reusable material, and asks siblings to `ADOPT(reference)` or
`DISTINGUISH(reason)`. Sibling rulings link back; material falsification reopens a reviewed amendment
rather than silently rewriting shared law.

The current sibling requests are `airmypc-cross-fleet-repair-loop-20260811`,
`airmypc-opus68-validation-laws-20260811`, and `airmypc-semantic-liveness-20260811`. Doctrine is data,
not authority; no sibling gains a claim, provider key, queue right, Git right, review key, release
right, hardware right, or `RUN_GO` from these entries.

## Remaining non-blocking hardening

1. Exercise a real claimed canonical implementation handoff before considering implement authority
   beyond bank-only provisional.
2. Re-probe Anthropic after the recorded reset and retain recovery sampling.
3. Align CLI versions during an explicit user-directed or quiescent fleet window.
4. Add providers only through the same adapter, refusal, portal-redaction, seeded-role and terminal
   receipt drills.

## Publication contract

Ratified strategy travels through this wholesale spec, AirMyPC append blocks in `FAILOVER.md` and
`RULINGS.md`, and execution entries in `RECEIPTS.md`/`TRAPS.md`. Raw transcripts, credentials,
customer data, private reasoning and local ignored session artifacts never travel.
