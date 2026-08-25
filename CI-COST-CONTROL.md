# Fleet CI Cost Control

Status: `CANONICAL_OPERATING_POLICY`

By direct owner decision, `layibabalola/softwarefactory-fleet-doctrine` is public. Public visibility
is intentional and is not runtime, provider, Product, release, or credential authority. Fleet
projects may cite and pull the canonical public doctrine bytes, but every project continues to
verify locally and ADOPT, DISTINGUISH, or REJECT under the existing doctrine-as-data law.

## Billing evidence

The August 2026 GitHub billing ledger reported `$117.028664` gross usage, `$67.028664` discounts,
and an exact `$50.00` net cap. Actions accounted for all `$50.00`. Windows runners accounted for
`$37.43`, Linux for `$12.333891`, and Actions storage for `$0.236109`. Fleet Doctrine was the
largest paid repository at `$26.859891`; `context-ultra-salesforce` was `$15.911461`; Cloudvore was
`$7.050084`.

The Fleet Doctrine branch `codex/fleet-workstream-liveness-strategy-20260823` alone produced 117
workflow runs and 468 matrix jobs, equivalent to 39 complete three-workflow trigger sets. Repeated
intermediate publication, not storage, was the dominant avoidable cost.

## Canonical operating rule

1. Pull requests run one representative `ubuntu-latest` / Python 3.14 job per relevant workflow.
2. Canonical `master` pushes and deliberate `workflow_dispatch` runs retain the complete
   Windows/Linux x Python 3.13/3.14 evidence matrix.
3. Native path filters prevent unrelated changes from launching adoption, disposition, provider,
   or runtime-extension suites.
4. `cancel-in-progress` remains mandatory, and agents batch evidence refinements into one landing
   publication instead of pushing every intermediate draft.
5. Public standard hosted runners or separately controlled self-hosted runners may provide the
   evidence. A skipped, budget-blocked, cancelled, or locally asserted job is never a PASS.
6. Before purchasing additional private-repository Actions usage, attribute the current-period
   spend by repository, runner SKU, workflow, branch, and run count. Buy only after the remaining
   private repositories have bounded fan-out and a monitoring threshold.

This policy changes CI scheduling and repository visibility only. It grants no merge, deployment,
provider spend, model invocation, task enablement, Product path, release, policy, or runtime
authority.
