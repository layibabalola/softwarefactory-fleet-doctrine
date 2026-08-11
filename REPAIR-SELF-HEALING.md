# Repair self-healing and fleet transfer

**Status: candidate doctrine; requires fleet ratification before authority or publication.**

## Core rule

Every substantive repair classifies whether its failure mode can exist in another fleet project.
When the answer is yes, the repair work produces a durable transfer packet in the same work block
and routes it through hub review. A local fix is not fleet prevention until the reusable contract,
regression test, rejected alternatives, ratification, and verified remote publication exist.

## Required repair transaction

1. Persist machine-readable intent before prose claims delivery, scheduling, activation, or
   publication.
2. Validate the intent's authority sequence and immutable evidence before executable mutation.
3. Reconcile interrupted intent-to-state writes automatically through a pre-image-pinned writer.
4. Treat a materialized intent as a delivery receipt, not a lifecycle lock: strict collision
   checking applies at new submission; later reconciliation matches immutable identity and
   preserves legitimate state, owner, priority, scope, and additive bookkeeping changes.
5. Keep freshness cursors monotonic with `max(existing, applied intents)` and test both no-regress
   and must-advance directions.
6. Require an independent reviewer to reproduce the defect on the exact prior head, demonstrate
   the fix on the exact proposed head, and run a discriminating falsifier.
7. Treat provider dormancy as typed state. Preserve the exact registered session and suppress
   duplicate ignition until its declared reset. Cross-provider routing is allowed only through an
   already-admitted provider/model/harness/host/role cell and may not weaken review independence,
   exact-range gates, or release authority.
8. After approval, finalize and verify target ancestry and remote bytes. Retain foreign dirty work;
   never absorb it into the repair merely to obtain a clean report.

## Doctrine publication isolation

The long-lived doctrine checkout is never a publication workspace. It may be ahead, dirty, or
owned by another session. The publisher must:

1. pin the expected remote target head;
2. run `tools/new-clean-publication-worktree.ps1` with a new path and new feature branch;
3. apply only ratified paths in that clean worktree;
4. push with an expected-old target ref or equivalent lease;
5. re-read remote ancestry and bytes after push;
6. remove the temporary worktree only after publication proof is durable.

A dirty or ahead canonical checkout is reported as retained evidence. It is never stashed, reset,
cleaned, switched, committed, or silently used as the publication base. This converts canonical
checkout contamination from a recurring publication blocker into an isolated, observable fact.

## Minimum tests

- interrupted delivery heals on the next sweep;
- identical retry is a no-op;
- new same-id conflict refuses before intent installation;
- lifecycle mutation is preserved;
- immutable identity mutation refuses;
- freshness never regresses and still advances;
- prose-only declaration raises attention without inventing authority;
- quota-dormant provider is not duplicated and exact-session resumption works after reset;
- old-head defect/new-head fix arms discriminate;
- an ahead-and-dirty canonical doctrine checkout remains byte-for-byte and HEAD-identical while a
  clean publication worktree is created at the pinned remote head;
- a stale expected remote head refuses before creating a branch or worktree.

## Grounded source

MLV-App landed implementation `dae82b0c6ba7cc4a419d351b315375c26c37c5e0`, approved content
range `db6881645216ce34eb453d6b694570a89cb58b2f..da3fa784beeb42d700ee4f9fefc2d0f2756640dd`.
The independent review reproduced the lifecycle-lock and freshness-regression defects on the prior
head, showed both closed on the new head, and kept dispatch-identity conflict fail-closed.

For public GitHub repositories, ordinary hosted Actions and public-repository branch protection do
not require a paid plan merely to repair red CI or configure enforcement. Recommend payment only
after naming and evidencing an exact paid-only capability.
