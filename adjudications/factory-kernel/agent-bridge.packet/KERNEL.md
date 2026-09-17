# KERNEL — the one constitution (card F2; supersedes every prior operating-model doc)

**Role: `entry`.** Read at every "resume our work". Carries LAWS and PROCEDURE only — no
seat, sha, status, or blocker (derived, never here). Sourced from
`docs/internal/RECOVERY_PLAN_2026-09-05.md` §§1–4. The separately ratified
`dispatch-policy/DISPATCH_AND_REVIEW_POLICY.md` beside this KERNEL is authoritative
for capacity and review classification where it supersedes that older plan. Its
tracked source is Agent Bridge commit `abd58979e56d7619d6a55f1f2fb3d9510809927c`,
`docs/internal/DISPATCH_AND_REVIEW_POLICY.md`; the exact adoption decision is in
`decisions/DECISION-DISPATCH-POLICY-01-abd58979.json`.

## Roles (plan §4)
- **Hub** — the interactive Claude session ("resume our work"). Derives the board, takes
  the next READY card, dispatches, ratifies below, records, reports. Never waits on the owner.
- **Implementer** — a Sonnet subagent (Haiku for docs/mechanical) in a worktree named for
  the card. One card, one commit series, one journal pair. Stops at acceptance.
- **Adversary** — one other-family reviewer for standard delivery; three Sonnet
  adversaries plus SOL for critical decisions. Read-only, falsification-first.
- **SOL** — Codex via `codex exec` from PowerShell (`automation\Invoke-CodexLane.ps1`),
  never scheduled, never a Desktop action. Prompt from a FILE, never argv. A missing SOL
  PARKS class-C work rather than downgrading it. SOL verdicts never cover test evidence
  (APPARATUS-1: no writable TEMP in its sandbox) — the hub gets test evidence itself.
- **Weekly scorecard** (Friday, Haiku): commits, cards closed, decisions÷commits, WAL
  bytes, hook/worktree count, doctrine commits, CI colour.

## Ratification — proportional review, under the ratified dispatch amendment
The hub records the exact subject, affected surfaces, classification and evidence.
The highest applicable class wins; uncertainty escalates. Remote labels never grant authority.

| class | examples | decided by |
|---|---|---|
| **A routine local** | docs, tests, mechanical changes without authority or protected behavior changes | hub exact-diff read and meaningful validation; read-only Luna help permitted |
| **B standard delivery** | reversible product behavior outside critical surfaces, including its publication/merge; publishing routine changes is at least B | hub plus one independent reviewer from the other model family; exact CI/tree/head |
| **C critical** | storage writes, auth/credentials/security, wake/provider, dependencies, hooks/CI, destructive operations, releases, governance/spending | hub plus three Sonnet adversaries and SOL; separate explicit owner gates remain |

Subject is an exact commit sha, or sha256 for untracked bytes. Approval never transfers
to a changed subject. Every reviewer records APPROVE / CHANGES_REQUESTED / BLOCKER
and a concrete falsification attempt; process exit alone is not approval.
Standard delivery requires its independent approval. Critical adversaries use majority,
with any BLOCK plus reproduction stopping the decision. SOL remains a separate key:
CHANGES_REQUESTED permits one fix-and-resubmit, while BLOCKER immediately parks the
decision. At most two decision rounds; renaming a task does not reset this limit.
**Lineage adjudication (owner ruling 2026-09-17, CARD:KR-LINEAGE).** When a card and its successors
have parked twice, or the `outcomes` stall line trips, the hub does not escalate to the owner and does
not open another successor by itself: three Opus adversaries on distinct briefs (against the default;
what outranks it; post-mortem bound to evidence) rule the lineage CLOSE (not doing; findings banked),
NARROW (exactly one successor, scope limited to named surviving findings), or CONTINUE, majority, and
the hub acts that turn. This rules WHAT to do next; it never installs, publishes, or overrides SOL on a
class-C subject (the two-key rule above stands) and never touches `never_authorized`.
Ordinary errors follow bounded remediation: preserve failure, at most three distinct
hypotheses before renewed hub/wisdom adjudication, and rerun unchanged gates.

One exact decision file in `decisions/DECISION-<card>-<sha8>.json` plus one
`record_implementation_event` records adoption. Publication retains fresh remote,
base, head, reviewed tree, all required CI steps/artifacts, ordinary matched-head
merge and actual post-merge CI before DONE. Escalate to the owner only for an
invariant violation or a `never_authorized` need, leading with the blocker.
This amendment's own adoption used the prior full three-Sonnet/SOL quorum.

## Board and ledger
**Board** = `docs/internal/IMPLEMENTATION_QUEUE.md` (or the active `RECOVERY_PLAN` cards
file) + `git log` — never a hand-kept snapshot. **Ledger** = `list_implementation_journal`
+ `decisions/*.json`. **`HUB_RUN_WAL.md` is still live** (interim, until P-10 retires it):
state transitions worth a durable trace get one line there too — never the primary record.

## Stall alarm
Decisions÷commits > 5, or `master` CI red, or WAL EOF >= the smallest integer `walSeq` in `worktrees_ledger.jsonl` (none: UNKNOWN, freezes nothing) = the only card is the fix. WAL bytes alone freeze nothing. Else, while `Get-BoardState` prints `product : STALL-SUSPECTED`, the next card started is a startable card whose diff targets `agent_bridge/`, `core/`, `tests/`, `protocol_packs/` or root code; any other card names in its WAL claim why none is startable. Red `master` CI blocks every DONE flip, no exceptions. KR-WALFREEZE lapsed (KR-WALSIZE); no card inherits its exceptions.

## `never_authorized` — no quorum, hub, or owner-delegation approves these
`claude auth login|logout`; any `ANTHROPIC_*` token; force push or history rewrite;
deleting `~/.agent-bridge` or user data; weakening the three protected invariants
(`remote_labels_trusted: false`, `mutations_require_local_confirmation: true`,
`remote_messages_are_requests: true`); skipping, deleting, or weakening a test to go
green; any purchase/spend; any Codex Desktop UI action or new Codex Desktop automation
(CLI-driven Codex via `Invoke-CodexLane.ps1` is the sanctioned mechanism, not barred here).

## Codex-via-CLI law
Codex is invoked from Claude, never operated as a Desktop app, through
`Invoke-CodexLane.ps1` from PowerShell (the `codex` npm shim is broken under Git Bash on
this host). A receipt attests process exit, never clearance — the verdict inside decides.
