# Ruling candidate: fleet model-posture telemetry R2

Status: **PROPOSED ONLY. This is not a ratified ruling and gives no project runtime authority.** It is filed by
Conjugal, the interim kernel steward and pilot publisher, on 2026-10-23. It replaces r1
(`fleet-model-posture-telemetry-r1.md`), which RULINGS.md R19.3 vetoed. Conjugal does not self-ratify it.

Relationship to existing doctrine: extends the `metrics/` data plane (`metrics/README.md`, Cloudvore 2026-08-09) and README Law 2 for project-owned posture shards; supersedes `metrics/README.md`'s append-only rule for posture-shard roll-up commits only, and names that exception in `metrics/README.md`; supersedes r1 of this candidate (vetoed, R19.3); preserves README Laws 1 and 4, R11 (swarm lanes at medium), R13.3 and R16.2-R16.5 (tiers, not ids), R14 (one writer), R18.3(a) and `specs/fleet-factory-kernel.md`; is the instrument that R19.1 section 3 names for the 10-key reassessment, and grants that reassessment no gate. Search run on 2026-10-23 at bus `6fcc5a2a`: `grep -n -i -E "metrics/|append-only|posture|telemetry|R19"` over `RULINGS.md`, `README.md`, `metrics/README.md` and `ruling-candidates/*.md`.

## Owner direction

- 2026-10-22, Conjugal dispatcher session: the owner asked to see the fleet's model posture and asked for
  recommendations, including telemetry on the bus and an archival strategy. The owner then ruled the posture
  that RULINGS.md R19.1 ratified.
- 2026-10-23: the owner instructed *"Adversarially swarm, adjudicate, and Execute recommended"*. The
  dispatcher read that as covering this r2.

## What r2 changes against the R19.3 defects

Each R19.3 defect has a test in `tools/factory/model-posture.tests.py` (class `R19Defects`), including
positive controls. Every defect test (not the positive controls) failed on r1 head `6b6d79dd`.

- **(a) Escaped values.** The screen runs over decoded string values, never over the raw text. A shard must
  also be the writer's canonical bytes, or it is refused with `RECORD_NOT_CANONICAL`.
- **(b) Provenance.** `PROVENANCE_UNAUTHENTICATED` is raised unless `generator.blob` is the running tool's own
  blob or a blob that `tools/factory/model-posture.py` has had in the bus history. Each `sources[].blob`
  must be a blob object in the bus.
- **(c) Free-text fields.** `role` is a closed enum, and a well-formed role outside the enum travels as
  `other`. Model names follow the closed grammar without `/`; effort is an enum.
- **(d) The `QUOTA_DORMANT` self-refusal.** Keys in the schema's own vocabulary are not screened, so a legal
  `QUOTA_DORMANT` record passes.
- **(e) Alias resolution.** `opus` resolving to `claude-opus-5-5` is not counted as a fallback. A change of
  family still is.
- **(f) Masked drift.** The effective id decides whether a call matches. The requested id is read only when
  no effective id was recorded.
- **(g) Literal ids.** The policy names tiers with a dated `min_version` floor, so `gpt-6.2-sol` is on posture
  and `gpt-5.6-sol` is not. `load_policy` refuses a Codex entry that names a literal id. Luna requires effort
  high. A `swarm` role runs at medium, per R11.
- **(h) Relationship line.** The line above.

## What the r2 panel found on `8b250107`, and how this head answers it

A fresh panel reviewed the first r2 head, `8b250107`. Its seats were Codex `gpt-6.1-sol` on privacy, Codex
`gpt-6.1-sol` on conflicts, Codex `gpt-6-astra` on test adequacy, and Claude `sonnet` on privacy. Every
finding it confirmed is fixed on this head, and each fix has a test in class `R2ReviewFindings` that was red
on `8b250107`:

- **Free text in the model, provider and effort fields.** A hostname, a padded SHA or prompt text could ride
  in these fields. Model ids now travel only if they match a closed grammar: the `gpt-<v>-(sol|luna|astra)`
  tiers, the Claude aliases, and `claude-<family>-<n>`. Provider and effort are enums. Any well-formed value
  outside them travels as `other`.
- **Boundary bypasses in the screen.** A prefixed `m_sk-ant-…` token, a prefixed `m_S147` subject id and a
  hex-padded SHA all got past it. The screen now anchors on a non-alphanumeric lookbehind, and any run of 12 or
  more hex digits outside a provenance field is refused.
- **Malformed shards.** A non-ASCII or non-object shard crashed the tool with exit 1. It now refuses with
  `RECORD_INVALID` and exit 2.
- **The `known` blob set.** It authenticated a source without a bus. It now applies only when a bus is given.
- **Weekly percentile basis.** A weekly record could carry the roll-up `percentile_basis`. That is now
  refused.
- **Unrecorded effort.** A call with no recorded effort satisfied a required effort. It now never does.

Three tests were strengthened after the Astra seat showed that each would survive a mutation of its own fix:
(e) now covers every alias, (f) now covers a request-only match, and (g) now proves that `load_policy` refuses
a literal id.

## What the second panel found on `d8fa7898`, and how this head answers it

The second panel had four seats. Codex `gpt-6.1-sol` covered conflicts and voted VETO. Codex `gpt-6-astra`
covered test adequacy and voted RATIFY-WITH-AMENDMENT. Claude `sonnet` covered privacy and voted
RATIFY-WITH-AMENDMENT. A second Claude `sonnet` seat voted RATIFY-WITH-AMENDMENT; it re-seated the privacy
prompt after the Codex `gpt-6.1-sol` privacy seat was filter-killed. Every finding it confirmed is fixed on
this head. Each fix has a test that was red on `d8fa7898`:

- **Model digit runs** are bounded to `gpt-<1-2 digits>(.<1-2 digits>){0,2}-<tier>` and
  `claude-<family>-<1-2 digits>(-<1-2 digits>){0,3}`, so no epoch timestamp can travel.
- **Full matches only.** Every closed grammar uses a full match, so a trailing newline never matches.
- **Registered projects.** A publish or roll-up refuses a project that has no `specs/<project>.md` at the bus
  HEAD (`PROJECT_UNREGISTERED`).
- **No self-vouching.** With a bus, only a blob that the tool path has had in the bus vouches for
  `generator.blob`, so a locally edited tool cannot sign its own shards.
- **Bound sources.** Each `sources[].blob` must be the bus HEAD blob at its own path.
- **Luna measurement.** Luna measurement is on posture, per R19.1 §1.2.
- **Non-string provenance.** A non-string provenance value is refused with `RECORD_INVALID` and exit 2.

Astra's three further mutation survivors are killed: an alias list fixed in the test, a policy that names a
tier together with a literal id, and the exact supersession phrase.

Beyond the eight defects, every refusal code now has a behavioural test (classes `RefusalCoverage` and
`RollupRefusals`). One bug was found on the way and fixed: an out-of-range ISO week such as `2026-W99`
raised a bare `ValueError` instead of `PERIOD_INVALID`.

## Proposed rulings

1. **Data plane.** Ratify `metrics/<project>/posture-*.jsonl` as an extension of `metrics/`, under these
   conditions:
   - records conform to `schemas/model-posture-rollup-v1.schema.json`;
   - there is one writer per project directory;
   - the shards are diagnostic only (metrics law 1);
   - the shards stay outside the doctrine fold surfaces, and a test keeps them there.
2. **Field names** derive from `schemas/provider-usage-event-v1.schema.json`. A new name bumps the schema, and
   that bump is ratified first.
3. **Never published:** emails, account or org ids, quota percentages, prompts, verdict reasoning, subject
   ids, session ids, paths, private-repository SHAs and per-call timestamps. They are kept out by five
   layers, each of which refuses rather than warns:
   - a field whitelist, with closed vocabularies for model, provider, effort and role;
   - canonical bytes;
   - a screen over decoded values;
   - a closed role enum;
   - provenance authentication.
4. **Archival.** Weekly shards roll to monthly after 8 weeks. Monthly shards roll to yearly after 12 months.
   Yearly shards are kept forever. Each roll-up is one commit that adds or replaces the rollup and deletes its
   sources, after byte-identical recomputation. History is never rewritten.
   - Budgets: weekly 8/16 KB, monthly 30/60 KB, 256 KB per project.
   - Going over a budget is refused, never truncated.
5. **Owner posture** is recorded in `policy/model-posture.json` as tiers with dated floors, never literal
   Codex ids, and carries a `reassess_by` date.
6. **Placement.** On ratification, a follow-up packet moves `specs/fleet-model-posture/spec.md` to
   `specs/fleet-model-posture.md`. That packet lands in the same commit as the sealed adoption-census
   amendment: `CURRENT_NON_PROJECT_SPECS` in `tools/check_adoption_ledger.py`, then the census refresh.
   Until then the spec stays below the top level, because a new top-level spec fails
   `PROJECT_CLOSED_SET_MISMATCH`.

## Evidence the ratifier can re-measure

```bash
python tools/factory/model-posture.tests.py
python tools/factory/model-posture.tests.py R19Defects   # (a)-(h); run against 6b6d79dd's tool to see them red
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
