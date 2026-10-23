# Ruling candidate: fleet model-posture telemetry R1

Status: **VETOED at r1, 2026-10-23, by Layi (owner instruction quoted in RULINGS.md R19) as RULINGS.md R19.3.** It is not
ratified and gives no project runtime authority. R19.3 lists the eight confirmed defects (a) to (h) that an r2 must fix,
each with a behavioural test. Originally PROPOSED 2026-10-22 by Conjugal. This PR is held, not merged (R19.4).

## Owner direction

On 2026-10-22, in the Conjugal dispatcher session, the owner asked to see the fleet's model posture and to get
recommendations, including telemetry on the bus and an archival strategy. The owner then ruled on posture:

- `gpt-6.1-sol` is the Codex default;
- Astra is used occasionally, for diversity of thought.

A read-only census on the same day found two things:

- one provider carried about 96% of non-cache tokens fleet-wide over 7 days, while the other provider's quota
  sat near zero;
- no fleet record says which model or effort a seat actually ran.

## Proposed rulings

1. **Data plane.** Ratify `metrics/<project>/posture-*.jsonl` as an extension of `metrics/`, with the
   following conditions:
   - records conform to `schemas/model-posture-rollup-v1.schema.json`;
   - there is one writer per project directory;
   - the shards are diagnostic only (metrics law 1);
   - the shards are outside the doctrine fold surfaces, and a test keeps them there.
2. **Field names** derive from `schemas/provider-usage-event-v1.schema.json`. A new name means bumping the
   schema, and that bump must be ratified first.
3. **Never published:** emails, account or org ids, quota percentages, prompts, verdict reasoning, subject ids,
   session ids, paths, private-repository SHAs, and per-call timestamps. These are enforced by a field
   whitelist and a screen that refuses rather than warns.
4. **Archival.** Weekly shards roll to monthly after 8 weeks. Monthly shards roll to yearly after 12 months.
   Yearly shards are kept forever. Each roll-up is one commit that adds or replaces the rollup and deletes its
   sources, after byte-identical recomputation. History is never rewritten.
   - Budgets: weekly 8/16 KB, monthly 30/60 KB, 256 KB per project.
   - Going over a budget is refused, never truncated.
5. **Owner posture** is recorded in `policy/model-posture.json`, which carries a `reassess_by` date.
6. **Placement.** On ratification, move `specs/fleet-model-posture/spec.md` to `specs/fleet-model-posture.md`
   in the same commit as the sealed adoption-census amendment: `CURRENT_NON_PROJECT_SPECS` in
   `tools/check_adoption_ledger.py`, then the census refresh. Until then the spec stays below the top level,
   because a new top-level spec fails `PROJECT_CLOSED_SET_MISMATCH`, as measured on this branch.

## Evidence the ratifier can re-measure

```bash
python tools/factory/model-posture.tests.py
git log --oneline -- tools/factory/model-posture.py schemas/model-posture-rollup-v1.schema.json policy/model-posture.json
```

## Falsifiers

Any one of the following retires or suspends the plane under metrics law 1:

- a seat cites a posture shard as authority for a decision;
- a lane is graded on its own posture line;
- a published shard is found carrying any never-published class.

A rollup that fails to recompute from its parent's blobs suspends that project's shard until it is fixed.

## Not proposed

- No admission control. Quota stays local.
- No gating on any advisory.
- No new top-level bus section.
