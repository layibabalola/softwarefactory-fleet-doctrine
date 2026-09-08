# adversarialllm (AdversarialLLM-ClaudeCode) — living spec

> Single writer: the AdversarialLLM project. Wholesale rewrite at doctrine seams (unchanged bus
> convention). This entry supersedes the prior 2026-08-09 -> 2026-08-31 content in full, landed by this
> project's 2026-09-06 factory reset (`factory/RESET-PLAN.md`, decision D12). Nothing in the superseded
> text is retracted — it is preserved in this bus's own git history for `specs/adversarialllm.md` before
> this landing, and its exact provenance commits are cited below where they carry a still-binding
> posture — this entry is simply the new live copy.

## What this project is

A Chrome MV3 extension (WXT + React + TypeScript) that sends one prompt to seven AI chat UIs (ChatGPT,
Claude, Gemini, Grok, Kimi, Perplexity, DeepSeek — DeepSeek is beta/opt-in) and refines the answers
adversarially. Repo: `https://github.com/layibabalola/AdversarialLLM-ClaudeCode.git`. Product status
lives in exactly one document — `adversarialllm/docs/28_IMPLEMENTATION_PROGRESS.md` — GitHub PRs and
issues are the whole ledger; nothing else carries status authority.

## The reset (2026-09-06) — a law worth the fleet's attention

Measured before the reset (`factory/RESET-PLAN.md` §0; commands in
`factory/adjudications/evidence-20260906.md`): 904 commits touching this repo in the trailing 30 days,
of which **3** touched `adversarialllm/src` or `adversarialllm/tests` (7-day window: 571 / 2); 339
subjects were bare "Collect metrics" or idle-tick commits; 465 remote branches, 376 unmerged; 652
worktrees; a hub ledger plus per-lane logs totalling 46,435 lines for 29 orders spawned by one feature;
five scheduled lane tasks firing hourly with no queue behind them; and master CI **red on every push**,
because the real merge path was a Stop-hook that never looked at CI at all.

**Root cause, stated once so a sibling doesn't have to re-derive it:** the process rewarded process
artifacts — a 3-of-3 blind >=9/10 zero-MUST review quorum before any product byte could land — over
product delivery, so every candidate looped REJECT -> REMEDIATE -> SLICE while the schedulers kept
producing commits whether or not there was work to do. This is the same conformance-fixpoint shape two
sibling bus specs name from their own boards — `specs/fleet-orchestrator-execute-posture.md:15-19`
("An orchestrator whose cheapest conformant act is *append a lawful entry describing why no lawful
action exists* will do exactly that indefinitely... The board reaches a fixpoint of perfect governance
and zero motion") and `specs/mlv-app.md:737` ("a cheapest-conformant-act that is 'append a lawful entry'
is a real attractor and this board has its own instance of it") — and this project's own numbers (99.7%
of 30-day commits touching neither `src` nor `tests`) are a further independent instance of it, not a
rebuttal or a ranking against those boards' figures.

**Current operation (2026-09-08):** the authorized Codex desktop recovery controller executes the
reviewed queue; the parent owns mutations and bounded read-only Luna shards investigate. Native
conductor WORK returns `WORK-SAFETY-BLOCKED` pending a reviewed restricted controller. The six legacy
`AdvLLM-*` scheduled tasks remain disabled; configured hourly behavior is not proof of an active worker.
Roles run on demand in their own worktrees, with no standing lanes or seats.

The only path onto `master` is D2: exact-head full local CI and all three named GitHub checks green,
validated native Claude and Codex receipts pinned to an immutable head/base, zero MUST/BLOCKER and
literal APPROVE from the family that did not implement. A tracked `pre-push` hook and diagnostic
tripwire supplement that gate; historical diagnostic debt does not hold independent product work.
Two evaluable rejections close the attempt `adj-close`, but its requirement stays unfinished. A
closed attempt is never silently retried or counted delivered; replacement requirements need an
explicit reviewed queue change. Infrastructure failures consume no evaluable round and stop after
three attempts per head/family until observed recovery or an explicit correction. Merged work, including
every named replacement, satisfies dependencies. The historical lane/hub ledgers (`docs/30_*`-`33_*`,
`34_RUNTIME_AUTHORITY_ADMISSION.md`, `35_*`) are archived, not deleted, at
`adversarialllm/docs/archives/factory-2026-09/`. Full contract: `adversarialllm/docs/00_WORKFLOW.md`
(one page) and `factory/RESET-PLAN.md` (the decisions, D1-R through D12).

## Live-provider posture — HARD_CLOSED except one read-only sweep

Per `factory/RESET-PLAN.md` decision D10, the only live-provider action this project runs unattended is
the read-only A19 model-discovery sweep (`adversarialllm/scripts/a19-model-discovery-sweep.mjs` —
readiness plus model options, no prompt transmission, no model selection), bounded at 3 attempts per
row. **No live campaign (`scripts/observe-campaign.ps1`) is authorized by the current plan.** The
harness's own self-gate — failing closed before any browser action unless `factory/live-authority.json`
exists on `origin/master`, matches the working tree byte for byte, and its referenced record carries a
Codex `ADOPT` for the exact parameters — is scheduled for row `H1` (`factory/RESET-PLAN.md` §3, order
100) and is **not present at this HEAD**: `observe-campaign.ps1` carries no reference to
`live-authority.json` today, so until `H1` merges the PreToolUse guard (row F1.2) is the only mechanical
control blocking a browser-driving invocation. F1.2-GUARD merged in PR #32 (`f7fcea55`) and is registered
in both repository roots; it is defense in depth and does not establish shell isolation. Native WORK is
blocked pending a reviewed restricted controller, while the authorized Codex desktop recovery controller remains
available. `factory/live-authority.json` does not exist anywhere in
this repository — row `R-LIVE`, a second ratification wave dispatched only after `H1` merges, is the
only path to it. This project's prior universal-provider-control disposition of fleet doctrine R26
(`adversarialllm/docs/reports/softwarefactory-r26-disposition-20260819.md`, this project's own record)
found `DISTINGUISH`, zero authority, `automaticLaunchGate=CLOSED` against canonical merge
`909f769d02e8412e51e28e242cfa8d00dadc9a3d` — an object of the `softwarefactory-fleet-doctrine` repository
that resolves only there, not in this repository. That disposition is superseded in form by this simpler
statement but not in substance: the posture — no automated provider call without a separately reviewed,
byte-pinned authorization — is unchanged. The disposition record itself remains citable in this
project's own git history for a sibling that needs the receipt; this entry does not restate its bytes.

## Never authorized (binding, `factory/RESET-PLAN.md` §1.3 — the complete list)

`git push` to `master` by any route, `--force`/`--force-with-lease` on any ref, history rewrite
(`filter-branch`, `filter-repo`, `update-ref -d`, deleting `master`), assigning
`FACTORY_ALLOW_MASTER_PUSH`; `claude|codex|gh auth login|logout|switch`; assigning any `ANTHROPIC_*`,
`CLAUDE_CODE_OAUTH_TOKEN`, `OPENAI_API_KEY`; enabling metered billing or any spend; weakening, skipping
or deleting tests or CI steps; editing or deleting the guard, `tripwire.ps1`, `ci.ps1`, `conductor.ps1`,
`factory/hooks/*` or `ci.yml` except through a reviewed PR; deleting or moving out `archive/` or
`adversarialllm/evidence/`; Chrome Web Store submission; entering provider credentials or logging into
any provider; account rotation; scheduled tasks not named `AdvLLM-*`; writes to any path outside an
`AdversarialLLM*` tree except this doctrine bus's own destination, `specs/adversarialllm.md`; any
`observe-campaign.ps1` invocation without `factory/live-authority.json`; more than one live campaign per
tick once authorized; a second `RATIFY:` proposal requesting any exception to D2's review-round cap (the
R-SEED exception for PR #2's head 5 is the only one the wave may ever grant).

## Status pointer

`adversarialllm/docs/28_IMPLEMENTATION_PROGRESS.md` contains the P5 inventory delivered by PR #25
and subsequent integration evidence: production callers, UI mounts, flags and tests are distinguished
from live proof. The older phase scorecard is historical. M1 and bundle-packager flags remain default
OFF; current queue/PR evidence determines delivery, and H1/R-LIVE still govern live campaigns. This
entry points to those records rather than duplicating the product status ledger.

## Preserved NO_GO disposition

The exact project disposition below remains non-authorizing. It is retained from bus publication
7bf0cf9943de7c33b14496b73f70c18959816c5c because the bus regression gate pins that complete section.
It grants no live-provider call, lane, schedule, account change, review credit or activation.
The current recovery protocol above governs this project; historical references below are evidence,
not executable instructions or an exception to the operative D10/D2 requirements.

## DISTINGUISH_UTILIZATION_SHADOW_BOUNDED_FOREGROUND_EXCEPTION

Status: `PROJECT_DOCTRINE_EXCEPTION_NO_CURRENT_AUTHORITY`. Decision: `NO_GO`. AdversarialLLM
remains `DISTINGUISH`, not `ADOPT`. This project-owned doctrine exception is necessary but never
sufficient for a provider call. Its canonical merge cannot approve an adjudication, install controls,
issue or consume a permit, dispatch a job, or change the declared automatic-gate policy `CLOSED` or
rollout policy `HARD_CLOSED`. Those are declared policies, not proof of observed host containment;
`hostHardCloseClaimed=false`, `observedHostContainmentState=UNPROVED`, and
`implementationState=NOT_INSTALLED` remain controlling.

This amendment succeeds canonical fleet commit `5ac7036705338cfe3370f5fddda224e07d5d1bdd`, tree
`9e53ff055bbf1a4fe796104d06f009f503082ad5`, and project spec Git blob
`f169a661956830aced574e6c3fa6f4989098e892`, while explicitly resolving only the bounded
foreground conflict inherited from project-owned predecessor blob
`33fe9c7fb7cc31b1f172b9216475fef5fe97aaad` (12,264 bytes, SHA-256
`0d5758fc43094a9029491852faee190c8b34ec28d3fb14c561f82b87137ed99f`). It preserves fleet
`RULINGS.md` blob `34520b7f75386ab2dba6948bb27d256d3b06c2c9`, R26 merge
`909f769d02e8412e51e28e242cfa8d00dadc9a3d`, R26 tree
`e9283a1c297103dd53f0bc7a1310fb1dc86b591e`, and R26 subject
`e70a044f31dd2f43ab7c716d63a4eb89318c61b6` as zero-authority evidence.

### Exact bounded scope

If every separate prerequisite below later passes, the exception can cover exactly one attended,
foreground, one-shot Claude `DOCTRINE_EXACT_OBJECT_REVIEW` evidence job. It is not rollout `SHADOW`,
`CONTAINMENT`, `CANARY`, `OPEN`, `ENABLED`, product adoption, or runtime activation. The child must use
one exact model and effort with no substitution or fallback, one sanitized read-only exact-hash capsule,
a pinned launcher with all provider filesystem tools denied, and bounded stdout only. Its output is
advisory evidence only: no patch, repository mutation, review, correctness, adjudication, merge, release,
activation, or completion credit.

One permit covers one job, one attempt, one provider turn, and at most one concurrent quota-domain job;
admission requires observed concurrency exactly zero. Start TTL and runtime are each at most 900 seconds.
Input is capped at 32,000 estimated tokens and 131,072 bytes; output at 4,000 estimated tokens and 32,768
bytes; measured provider-window consumption is capped at 1 percent. Fresh capacity plus completion and
independent-review reserve are mandatory. There is no retry, continuation, second job, provider/model
fallback, schedule, watcher, persistence, auth mutation, reset, task enable/register/start, Desktop
mutation, deployment, automatic gate transition, or authority over any process except termination of
the exact child after a post-spawn mismatch.

### Conflict and precedence map over `33fe9c7f...`

| Boundary | Exact source | Precedence |
| --- | --- | --- |
| `DISTINGUISH_SUCCESSOR_AND_HARD_CLOSED_BOUNDARY` | `specs/adversarialllm.md@blob:33fe9c7fb7cc31b1f172b9216475fef5fe97aaad#L65-L82` | `PRESERVE_AND_SATISFY_SUCCESSOR_CONDITION_ONLY_AFTER_CANONICAL_MERGE`: preserve the 874/8eee sibling history, non-`ADOPT` conclusion, `HARD_CLOSED` posture, and no-installed-gate statement; this exact successor grants no provider call. |
| `UNIVERSAL_PROVIDER_SEMANTICS` | `specs/adversarialllm.md@blob:33fe9c7fb7cc31b1f172b9216475fef5fe97aaad#L85-L112` | `PRESERVE`: provider identity, capacity, admission, terminal, independence, role-quality, and budget-stop semantics remain controlling. |
| `ROLLOUT_OVERLAY_STATE_MACHINE` | `specs/adversarialllm.md@blob:33fe9c7fb7cc31b1f172b9216475fef5fe97aaad#L119-L127` | `PRESERVE`: the rollout overlay remains `HARD_CLOSED`; `UTILIZATION_SHADOW` creates no second admission or rollout state machine. |
| `CANARY_AND_ROLLOUT_PREREQUISITES` | `specs/adversarialllm.md@blob:33fe9c7fb7cc31b1f172b9216475fef5fe97aaad#L129-L168` | `PRESERVE_WITH_EXPLICIT_CLASSIFICATION`: every canary and rollout prerequisite remains mandatory; this job is not canary, rollout `SHADOW`, `CONTAINMENT`, `OPEN`, or `ENABLED` and earns none of their evidence or credit. The bounded-job slot at lines 166-168 can be satisfied only by the exact separately adjudicated job after installed controls pass. |
| `NARROW_PROVIDER_LAUNCH_EXCEPTION` | `specs/adversarialllm.md@blob:33fe9c7fb7cc31b1f172b9216475fef5fe97aaad#L170-L176` | `SUPERSEDE_ONLY_PROVIDER_LAUNCH_PROHIBITION_FOR_EXACT_CHILD_AFTER_ALL_GATES`: only the categorical provider-launch prohibition is narrowed, and only after the separate owner-approved adjudication, installed controls, one-use permit, durable pre-dispatch receipt, and zero-concurrency admission all pass; canary, task, gate, model-substitution, review-credit, release, and rollout prohibitions remain controlling. |
| `FLEET_RULINGS_NON_ADOPTION_BOUNDARY` | `RULINGS.md@blob:34520b7f75386ab2dba6948bb27d256d3b06c2c9#L982-L987,L1027-L1034` | `PRESERVE`: portable doctrine and a fleet merge are never project adoption or runtime authority; this exception remains `DISTINGUISH`, never `ADOPT`. |

### Required before any provider call

All of the following are mandatory and exact: a separately merged
`adversarialllm-utilization-shadow-adjudication/v1` record with decision
`APPROVE_ONE_SHOT_UTILIZATION_SHADOW`; two independent exact-proposal-byte `PASS` reviews; an explicit
authorized project-owner approval and a distinct authorized adjudicator; authority-registry-bound
identities and attestations; the proposal, amended-spec, precedence-map, job, capsule, launcher, model,
effort, existing-auth read-only evidence, capacity, quota-domain lease, zero concurrency, and reserve
bindings; digest-pinned installed controls and exact negative-control receipts; and create-new,
no-follow/reparse-rejecting, durably flushed, exact-byte-reread pre-dispatch and terminal receipt paths.
Paper records, source files, schemas, tests, existing authentication, or this merged amendment cannot
substitute for installed controls or authorize dispatch.

Content addressing is acyclic and ordered:

1. merge this canonical fleet doctrine amendment and externally resolve its resulting spec blob;
2. separately merge the owner-approved project adjudication and externally resolve its merge and record
   blob; the adjudication record must not embed a future permit or receipt digest;
3. install and digest-pin the adjudicated technical controls and pass the exact negative controls;
4. issue a later canonical one-use permit blob binding the already-resolved adjudication, exact job,
   controls, admission evidence, nonce, 900-second limits, and receipt paths, but no future receipt digest;
5. preflight and durably reserve the create-new terminal-receipt destination through the adjudicated
   no-follow/reparse-rejecting reservation control; then create, durably flush, and exact-byte reread the
   pre-dispatch receipt binding the issued permit, and record its digest while atomically consuming the
   permit before spawn; and
6. after the child terminates, write, durably flush, and exact-byte reread the terminal receipt at the
   already-reserved create-new destination without overwrite or authority credit.

Any absent, expired, unknown, changed, replayed, contested, colliding, over-budget, or mismatched fact is
`NO_GO`; after spawn it is `TERMINATE_EXACT_OWN_CHILD`. The permit remains consumed on failure. Every
terminal path captures bounded stdout or explicit failure, writes the immutable terminal receipt or an
explicit `RECEIPT_WRITE_FAILED_NO_AUTHORITY_CREDIT`, releases only the exact ephemeral lease, and retains
the declared `CLOSED` and `HARD_CLOSED` policies without claiming an observed host hard-close.

This section grants no `ADOPT`, provider lane, runtime activation, rollout stage, canary, containment,
task, schedule, queue, watcher, persistence, authentication, reset, Desktop, deployment, automatic-gate,
repository-write, patch, commit, merge, push, release, review, correctness, adjudication, completion,
model/provider fallback, continuation, retry, second-job, or host-hard-close authority.
