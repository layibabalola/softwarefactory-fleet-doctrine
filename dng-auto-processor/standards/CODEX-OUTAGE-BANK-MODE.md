# Codex Outage Bank Mode — bounded candidate production during Claude-family unavailability

**Status:** fleet-adoptable law, ratified by the DNG Auto Processor hub on 2026-08-09.  
**Local ruling:** `SOL-RULING-CODEX-OUTAGE-BANK-MODE-RATIFY-20260809.md`, 4,827 B,
`6254E42A277A48E7732524AEEF42728E5E2E129BE7B150AD4ADB7C2967391524`.  
**Scope:** coordination posture only. It grants no acceptance, landing, release, deployment, or
external-mutation authority.

## Purpose

When Claude-family lanes cannot advance a hub, fresh Codex workers may preserve independent design,
implementation, test, and review capacity by producing **banked candidates**. The bank is an exact-byte
queue for later cross-family adjudication. It is never a substitute hub, never an alternate ledger,
and never accepted state.

This standard deliberately separates two questions:

1. **May this project enter the mode?** Entry requires explicit proof described below.
2. **What may workers do after entry?** Candidate-only semantics are fixed and do not expand merely
   because the unavailable period lasts longer than expected.

## Entry proof

A project may enter only through one of these mutually explicit proofs:

- a direct local USER authorization naming the mode and its local scope; or
- a separately ratified outage classifier whose exact version and evidence tuple are bound in the
  mode marker.

A local USER authorization proves authority to bank locally. It does **not** assert that a provider is
globally down, and it does not adopt an unfinished outage-versus-account-drainage classifier. Missing,
stale, copied, ambiguous, or unverifiable proof means mode **OFF**.

Before the first worker is dispatched, the controller durably writes:

- a unique mode id, state `ACTIVE`, activation time, controller identity, and entry-proof reference;
- the allowed worker family and candidate-only scope;
- a closed assignment order naming existing cards or cards explicitly assigned by the USER locally;
- the absolute forbidden acts;
- a project-specific positive-advancement predicate for the returning family;
- end and drain behavior; and
- an initially exact bank register.

The marker is authoritative. Absence of an active marker means OFF. Workers re-read it immediately
before every durable candidate write.

## Worker identity and allowed work

A bank worker is fresh and task-scoped. It does not claim or impersonate a standing lane. It may:

- produce candidate code, tests, designs, patches, or evidence in an isolated branch, worktree, or
  dedicated bank directory;
- prepare an advisory review matrix for a routed proposal; and
- report `WAITING-EXACT-BYTES` when a review's frozen tuple does not yet exist.

Workers may act only on an existing card or an assignment named explicitly in the local entry proof.
The bank status vocabulary is candidate-shaped: `BANKED-CANDIDATE`, `BANKED-ADVISORY`, and
`WAITING-EXACT-BYTES`. These words never imply acceptance or closure.

## Absolute prohibitions

A bank worker may not:

- land, merge, push, deploy, publish, clear, ratify, accept, reject canonically, close status, or
  release a hold;
- create a card or silently broaden an assigned card;
- change a protected invariant or weaken an acceptance, recusal, security, or USER gate;
- claim or modify another lane's lease, heartbeat, hub entry, inbox, ledger, roadmap, or role record;
- modify scheduled tasks, account binding, provider configuration, or machine settings; or
- change product refs or a shared index.

Long duration, worker agreement, passing tests, and returning-family recovery do not relax this list.

## Exact bank register

The controller owns the register. Each row binds at least:

- mode id, order, existing/explicit assignment, and assignment authority;
- unique worker task/session identity without standing-lane authority;
- isolated base and branch/worktree/directory identity;
- declared closed changed-path set;
- exact path, byte size, and SHA-256 for every candidate artifact;
- tests run, host/runtime identity, outcomes, and declared caps;
- candidate status; and
- arrival and completion times or typed failure/waiting state.

Unreceipted, mismatched, ambiguous, or out-of-scope bytes are incomplete and are excluded from the
drain. A second worker may not share ambiguous ownership of the same card. Projects should reserve a
card attempt atomically and require a fresh admission measurement for each launch; prior arrival is
not authority for a later launch.

## End predicate

The mode ends on either:

- direct USER revocation; or
- the first event satisfying the marker's positive returning-family advancement predicate.

The predicate must prove work advancement, not mere presence. A claim, lease renewal, heartbeat,
health sweep, process start, login success, or unchanged status is never positive advancement by
itself. DNG's initial profile requires a post-activation Claude-family canonical-hub entry that
advances an existing routed item and binds a new or changed artifact by path, size, and SHA-256.

End transition is fail-safe and single-writer:

1. re-read the marker and qualifying evidence under the coordination lock;
2. transition ACTIVE to FROZEN and stop fresh dispatch;
3. write an exact end receipt and freeze the register's closed set;
4. route the whole bank as one batched cross-family drain; and
5. leave every candidate unlanded.

Recovery never auto-lands, auto-ratifies, or auto-closes banked work.

## Drain law

The returning canonical hub reviews the closed register in one batch and produces one consolidated
blocker list. Reviewers consume exact bytes, not worker narrative. Existing recusal, gate identity,
independence, acceptance, USER, and landing laws apply normally. An advisory packet may accelerate a
review but cannot become the verdict merely because it was prepared by a worker named for that role.

After drainage, accepted items land only through their ordinary project corridor. Held or rejected
items remain ordinary governed work; the bank does not invent a cleanup authority.

## Required fail-closed controls

An adopting project must exercise and retain negative controls for all of these:

1. entry spoofing or unverifiable authorization;
2. pulse/claim/health activity misclassified as advancement;
3. duplicate workers or ambiguous card ownership;
4. card invention or scope broadening;
5. status laundering (`ACCEPT`, `RATIFY`, `CLOSED`, `LANDED`, or `PUSHED` in candidate state);
6. foreign lease/ledger/canonical-carrier mutation;
7. unreceipted or hash-mismatched bytes;
8. automatic landing on recovery; and
9. a mode that cannot reach a durable end edge.

Any failed negative holds mode adoption or the affected drain. Safety-critical or externally mutating
cards default to waiting unless their ordinary gates explicitly permit isolated candidate work.

## Relationship to automatic provider failover

This law adopts bounded banking semantics, not automatic outage classification. A future ratified
classifier may supply alternate entry proof without changing this standard. Until then, projects must
not infer provider outage from account exhaustion, a depleted usage window, a silent lane, or a failed
launch. Option B — wait for the unavailable family — remains the mandatory fallback when entry proof,
isolation, receipts, or any negative gate cannot be proven.
