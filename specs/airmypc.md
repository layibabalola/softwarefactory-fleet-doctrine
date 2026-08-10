# AirMyPC factory spec — fleet-facing snapshot

**Single writer: the AirMyPC hub. Rewritten wholesale at doctrine seams. Last rewrite:
2026-08-10 00:3x CT by LEAD-CODEX task `019fe992-7136-7f13-a062-7e444bb55001`.**

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
