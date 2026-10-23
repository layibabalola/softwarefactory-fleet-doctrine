# Fleet model posture: telemetry on the metrics data plane

Status: **CANDIDATE.** It has zero runtime authority until
`ruling-candidates/fleet-model-posture-telemetry-r2.md` is ratified (r1 was vetoed by RULINGS.md R19.3). Conjugal is the pilot publisher.

## Why

On 2026-10-22 the owner asked to see the fleet's model posture. A census of local usage showed one provider
carrying almost all non-cache tokens while another provider's quota sat nearly unused. No fleet record says
which model and effort each seat actually ran, so declared posture and actual posture cannot be compared. This
spec adds that record as aggregates only. It reuses the `metrics/` data plane (`metrics/README.md`), and the
data plane's two laws apply unchanged: metrics are diagnostic and never authority, and the compiler loses to
its sources.

## Where it lives

This document sits under `specs/fleet-model-posture/` rather than at `specs/fleet-model-posture.md` on
purpose. A new top-level `specs/*.md` fails the sealed adoption census with `PROJECT_CLOSED_SET_MISMATCH`
(this was measured on the branch that adds this spec). The ruling candidate asks the ratifier to move it to the
top level together with the census amendment.

| Surface | Path |
|---|---|
| Record schema | `schemas/model-posture-rollup-v1.schema.json` (`additionalProperties:false` at every level) |
| Writer | `tools/factory/model-posture.py` (stdlib only, deterministic; registered in `tools/factory/registry.json`) |
| Tests | `tools/factory/model-posture.tests.py` (run in `doctrine-sync.yml`) |
| Owner posture | `policy/model-posture.json` |
| Shards | `metrics/<project>/posture-YYYY-Www.jsonl`, then `posture-YYYY-MM.jsonl`, then `posture-YYYY.jsonl` |
| Entry | `metrics/model-posture/README.md` (commands only) |

`metrics/` is outside the doctrine fold surfaces (`tools/doctrine-sync.mjs` `BUS_SURFACES`), so a shard
never enters any member's fold queue. A test keeps it that way.

## Record

There is one aggregate per (period, project, provider, `model_requested`, `model_effective`,
`effort_effective`, role). Every field name comes from `schemas/provider-usage-event-v1.schema.json`:

- the model and effort fields are named exactly as in that schema;
- `role` is its `actor.role`, folded to a closed enum (the schema's `role` enum); a well-formed role outside the
  enum travels as `other`, so the field can never carry free text;
- the measures are its `measurement.{input_tokens, cached_input_tokens, reasoning_tokens, output_tokens,
  active_seconds}`;
- `outcome` is a histogram over its enum.

No other names are allowed. In particular there is no `effort` field and no `wall_s` field.

| Group | Fields |
|---|---|
| Volume | `calls` (TERMINAL events), `tasks` (distinct `task_id_hash` values, counted and never published), `{known, sum, p50, p90}` for each measure |
| Outcome | `rounds` (calls per task), the `outcome` histogram, `first_pass_accept`, `fallback_count` |
| Provenance | `generator {path, blob}`; `sources [{path, blob}]` on roll-ups only |

The fields are defined as follows:

- **`first_pass_accept`** counts tasks whose first call ended APPROVED or COMPLETED.
- **`fallback_count`** counts calls with a `*FALLBACK*` reason code, or with `model_effective` different
  from `model_requested`. A Claude family alias resolving to its own dated id (`opus` to `claude-opus-5-5`)
  is the mandated mechanism (R16.2), not a fallback; a different family is.
- **Weekly percentiles** are nearest-rank over the calls.
- **Roll-up percentiles** are the known-weighted median of the source records' percentiles. The record says
  so in `percentile_basis`. Sums and counts are always exact.

## Never published

The following never appear in a shard:

- emails;
- account or org ids;
- quota or utilization percentages;
- prompts and verdict reasoning;
- subject ids and session ids;
- paths outside `metrics/`;
- private-repository SHAs;
- per-call timestamps.

These protections are enforced in layers, and any breach is **refused, never edited and never warned past**:

1. A field whitelist, which is the schema mirrored in code. Model ids travel only as a closed grammar (the
   `gpt-<v>-(sol|luna|astra)` tiers, the Claude aliases, `claude-<family>-<n>`); provider, effort and `role`
   are closed enums; a well-formed input value outside them travels as `other`. A non-ASCII or non-object
   shard is `RECORD_INVALID` (exit 2).
2. Canonical form: a shard must be exactly the writer's serialisation, byte for byte
   (`RECORD_NOT_CANONICAL`), so no JSON escape or spacing variant reaches the screen.
3. A screen. It is the union of the bus `fleet-scorecard.py` `SCREEN`, Conjugal's `doctrine_outbox.LAW4`
   (by class name), and this plane's own classes: timestamps, drive paths, quota words and session/account
   words. It runs over every DECODED string value (and every key outside the schema's own vocabulary), never
   over the raw text, so a `\u` escape cannot hide a value and the schema's own `QUOTA_DORMANT` key cannot
   trip it.
4. A rule that a run of 12 or more hex digits may appear only as a 40-hex `generator.blob` or `sources[].blob`, and provenance
   authentication (`PROVENANCE_UNAUTHENTICATED`): `generator.blob` must be the running tool's own blob or one
   `tools/factory/model-posture.py` has had in the bus history, and each `sources[].blob` must be a blob object
   in the bus. A value that merely looks like a SHA is never trusted for its shape.

Raw per-call rows stay in the publishing project.

## Commands

The writer has four commands:

- **`reduce`** turns one ISO week of local provider-usage-event-v1 rows into a shard on stdout.
- **`publish`** writes that shard into a bus checkout. A published week is never rewritten (`SHARD_EXISTS`).
- **`view`** compares declared posture, actual posture and owner posture. It prints these advisory codes:
  - `DRIFT_DECLARED_VS_ACTUAL`
  - `OFF_OWNER_POSTURE`
  - `FALLBACK_RATE_HIGH`
  - `REASSESS_DUE`

  The view is never stored, and its exit code never depends on a value.
- **`prune`** rolls a month of weeklies into a monthly shard once that month's last week is 8 weeks old. It
  rolls a monthly shard into its year once the month is more than 12 months old. The yearly file is kept
  forever. A late shard is merged into an existing yearly file, which replaces that file rather than
  deleting it. Each roll-up is **one commit** that only adds or replaces the rollup and deletes its sources:
  - the rollup is computed twice before anything is written;
  - the staged census must be exactly A/M target plus D sources (`ROLLUP_CENSUS_MISMATCH`);
  - after the commit, the rollup must recompute byte for byte from the parent's blobs.

  History is never rewritten: every source still resolves at the parent commit. Pruning is a separate commit
  path from Conjugal's `harvest_runner.publish_bus`, which refuses deletes by design.

**Budgets.** A weekly shard has a soft cap of 8 KB and a hard cap of 16 KB. Monthly and yearly shards have a
soft cap of 30 KB and a hard cap of 60 KB. One project's posture files together may not exceed 256 KB. Going
over the soft cap prints a note. Going over a hard cap is refused with `SHARD_OVER_BUDGET`, and nothing is
truncated.

## Owner posture (2026-10-22), as `policy/model-posture.json` records it

The policy names Codex TIERS with a dated `min_version` floor, never a literal id (R16.2): a newer id of the
tier stays on posture and an older one does not. Matching uses `model_effective`; `model_requested` is read
only when no effective id was recorded. A role that requires an effort is met only by that recorded effort;
an unrecorded effort never satisfies it.

- **Codex default:** the Sol tier, at or above 6.1 (resolved 2026-10-22: `gpt-6.1-sol`), effort high.
- **Astra tier:** an occasional diversity seat only, never a gate. The policy caps its share at 25% of a
  role's calls, and it is not allowed in `key`.
- **Luna tier:** mechanical work only: census, measurement and scripted readouts (bus R16.1, R19.1), effort high.
- **`swarm` role:** R11 adversarial swarm lanes run at effort medium.
- **Claude:** requested by the `opus`/`fable`/`sonnet`/`haiku` aliases, at effort high. The resolved id is
  logged as `model_effective`.
- **Read-only review and survey seats** prefer Codex while Claude quota binds. Quota is local knowledge, so
  this preference is never computed from published data.

The policy carries `reassess_by`. Once that date passes, `view` reports `REASSESS_DUE`.

## Adoption

A member adopts this spec in four steps:

1. Map its local call log onto provider-usage-event-v1 names. The local log is never published.
2. Run `reduce` weekly.
3. Dry-run for two weeks.
4. Publish through its own one-writer path. One writer per `metrics/<project>/` directory.

Conjugal's pilot step is `coordination/harvest/model_posture_weekly.py`. It is off by default.
