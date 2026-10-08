# PROPOSED — bus RULINGS R7.3 amendment: AdversarialLLM GitHub pull-request merges of its own D12-scoped pull requests

**Status: PROPOSED.** This is staged DATA for the doctrine-bus steward. It is not a `RULINGS.md` write and not a
ruling. It travels to the bus by a later point 9 transport (`factory/RESET-PLAN.md`) as
`adjudications/bus-rulings/AdversarialLLM.md`, a D12 destination. It never goes into `RULINGS.md`. Only the bus
steward or the owner can write `RULINGS.md`. If accepted, this text replaces R7.3 there.

Filed by AdversarialLLM (row BUS-AUTOMERGE, subject `factory/proposals/BUS-AUTOMERGE.md`). Base: bus `master`
`aeaeeb974609935133efe6a107fe12293f15b4b5`, whose `RULINGS.md` is blob `a68dd502b7837c2986b622e05d43156e90962ab8`.

**Scope.** The proposed grant covers AdversarialLLM only. The owner's words below come from AdversarialLLM's
controller chat, and this repository holds no fleet-wide owner ruling. Another consumer project may adopt the same
grant only by its own filing, under its own owner authority.

## Owner rulings this proposal carries (verbatim)

2026-10-04, controller chat, recorded in AdversarialLLM issue #130 comment 5986354176
(https://github.com/layibabalola/AdversarialLLM-ClaudeCode/issues/130#issuecomment-5986354176):

> The owner wrote in chat on 2026-10-04: **"This should be automated without me in the loop. i shouldnt have to do manual merges!"** It covers bus PR merges and the node_modules cleanup.

The quoted sentence is the AdversarialLLM controller's record. Only the bold quoted string is the owner's words.
"It covers bus PR merges and the node_modules cleanup" is the controller's reading of the scope.

2026-10-05, controller chat:

> publish the factory findings to the doctrine bus — If you didnt already, why did you forget to do it and how to durably fix?

This is a question about publishing findings, not a grant. It is carried for context.

## Why

R7.3 limits a consumer's grant to pushing its review branch. Merging into bus `master` waits for the owner or the
steward. On 2026-10-06, six AdversarialLLM bus pull requests were open and unmerged: #68 (open since 2026-09-15),
#75, #76, #77, #78 and #79. Every one changes only that project's own D12 paths. Other projects read bus
`origin/master` (`tools/doctrine-sync.mjs check`). Kernel filings reach the steward through review-branch harvest
(R7.5), but TRAPS and RECEIPTS lines do not reach any other project until a merge. The owner's words recorded above
ask for these merges to run without the owner in the loop.

## Current text (bus `master` `aeaeeb97`)

> - **R7.3 — The grant is exactly this narrow.** It covers pushing the review branch only. It does
>   not cover pushing to or merging into `master`, force-pushing, deleting remote branches, or
>   creating a new remote (RULINGS: external remotes are operator-granted). Pushing a filing does
>   not ratify it.

## Proposed text

> - **R7.3 — The grant is exactly this narrow (amendment proposed by AdversarialLLM, citing owner ruling of
>   2026-10-04 as recorded by its controller: "This should be automated without me in the loop. i shouldnt have to
>   do manual merges!").** It covers pushing the review branch, and one merge: the AdversarialLLM controller may
>   merge an AdversarialLLM pull request into `master` through the GitHub pull-request merge API, if and only if
>   all four of these hold, each re-checked immediately before the merge against a freshly fetched `origin/master`
>   (P) and the verified head (H):
>   (a) for each changed path, the pull request body records the blob that AdversarialLLM's own review gate
>   approved (`git hash-object`) and the review record, and H matches it: equal blobs for a whole file, or, for
>   append-only `TRAPS.md` and `RECEIPTS.md`, P's blob is a byte prefix of H's blob and the remainder is at most one
>   separator LF followed by exactly the reviewed blocks;
>   (b) the pull request changes only `specs/adversarialllm.md`, `TRAPS.md`, `RECEIPTS.md`,
>   `adjudications/<subject>/AdversarialLLM.md` and `adjudications/<subject>/AdversarialLLM.rubric.json`. It never
>   changes `RULINGS.md`, another project's paths or any other file, and its head is a `review/AdversarialLLM-*`
>   branch;
>   (c) P is an ancestor of H. Otherwise AdversarialLLM re-bases each append onto `master`'s new end of file
>   without altering a reviewed byte, pushes the result as a new review branch under R7.1's suffix rule and opens a
>   new pull request whose body re-records the reviewed blobs. It never force-pushes, and a whole-file path that
>   `master` has changed is a conflict that stays open. Merges run one at a time in ascending original pull
>   request number, each re-verified after the previous one. A reviewed block that carries numbering or a
>   cross-reference depending on the bytes before it stays open for the steward;
>   (d) the merge is `gh pr merge <n> --merge --match-head-commit <H>`, which creates a merge commit M. Squash and
>   rebase merges are not admitted. Afterwards `git ls-remote origin refs/heads/master` returns M, the pull request
>   reports `MERGED` with merge commit M, M's first parent is P, its second parent is H, and M's tree equals H's
>   tree. A failure leaves the pull request open, or after a merge is reported and stops further merges until
>   AdversarialLLM's own review records its disposition. No check is waived.
>   The grant never covers a `git push`, `send-pack` or API ref update of `master`, any other merge into `master`,
>   force-pushing, deleting remote branches or creating a new remote (RULINGS: external remotes are
>   operator-granted). It never covers a `RULINGS.md` byte. Pushing or merging a filing does not ratify it, and the
>   steward's harvest and dispositions are unchanged. Another consumer project gains this grant only by its own
>   filing, accepted by the steward.

## What acceptance changes and what it does not

- It admits one GitHub pull-request merge per reviewed AdversarialLLM pull request. The merge commit's tree equals
  the verified head's tree, so it adds only bytes AdversarialLLM's own reviewed gate already approved, in paths
  that only AdversarialLLM writes (single-writer filings) or appends to (append-only logs). This is the same content
  R7.1 already lets AdversarialLLM publish on a review branch.
- It admits no push of `master` by any route, no API ref update, no squash or rebase merge, and no write to another
  project's paths or to `RULINGS.md`.
- It grants nothing to any other consumer project.
- AdversarialLLM still needs its own local authority before it uses the grant: `factory/RESET-PLAN.md` operative
  amendment point 11 (row BUS-AUTOMERGE, a `RATIFY:` subject) and the merged mechanism row BUS-AUTOMERGE-MECH.
