# Ruling candidate: universal quality-floor frontier-family drift R1

Status: **PROPOSED ONLY — ZERO AUTHORITY. NOT A RULING, NOT A FIX, NOT AN ADOPTION.**

This candidate records a measured contradiction between `FRONTIER_HIGH_MODEL` in
`tools/universal_provider_control.py` and the frontier-family identities this doctrine names. It
changes no bytes in the broker, grants no launch, routing, seat, vote, onboarding, or adoption
authority, and does not admit any Kimi or Claude profile to any fleet role. The automatic launch
gate remains CLOSED.

## Bound subject

Pinned **as measured**, at commit `12b0a56e6352dc4d5e74e388669abe151141f4e8`. These are the bytes the
findings below were taken from; they are not a claim about the current tree.

- `tools/universal_provider_control.py` — 271,453 B, `sha256:20d18b936f0d4a21385bb5d8b14475ba942f6a985cda0fc70c2746af6b2f9009`
- `tests/test_universal_provider_control.py` — 279,107 B, `sha256:9cce1ec73c60ebeea1c507dc19e44b731366ca385a750245fc45e88b92a1335b`
- `specs/agent-bridge.md` — 32,110 B, `sha256:2cf23d97141a87fe823a94502c64f66cf8fd4e5f890f1cc48ad9ecd289726050`

The broker file is unchanged from that pin and an adjudicator should verify it still is:
`git log --oneline 12b0a56..HEAD -- tools/universal_provider_control.py` must be **empty**. The test
file has since gained the closed-set controls described in finding 4; derive its current state from
`git log --oneline -- tests/test_universal_provider_control.py` rather than from a SHA restated
here, which would rot.

## Measured finding 1 — the Kimi pattern accepts the complement of the doctrine's Kimi set

`tools/universal_provider_control.py:344` defines the Kimi frontier family as `^kimi-(?:k2|next)`,
consumed at `tools/universal_provider_control.py:3555` where a non-match raises
`ControlError("UNIVERSAL_QUALITY_FLOOR_VIOLATION")`. Evaluated literally against every Kimi identity
this repository names:

| identity | doctrine standing | `^kimi-(?:k2\|next)` |
|---|---|---|
| `kimi-code/k3` | frozen provider-onboarding subject (`specs/agent-bridge.md:228`, `RECEIPTS.md:213`) | **REFUSE** |
| `kimi-k3` | flagship/high-inference API identity (`specs/agent-bridge.md:209`) | **REFUSE** |
| `kimi-code/k3-256k` | selectable profile candidate order 3 (`specs/provider-model-benchmarking.md:55`) | **REFUSE** |
| `kimi-code/kimi-for-coding` | separately role-admitted historical baseline, order 0 (`specs/provider-model-benchmarking.md:52`) | **REFUSE** |
| `kimi-k2.7-code` | coding-tuned tier; explicitly a *separate post-landing* candidate (`specs/agent-bridge.md:231`) | **ACCEPT** |
| `kimi-k2.6` | general mid-tier; **not present in the measured local catalog** (`specs/agent-bridge.md:226-227`) | **ACCEPT** |
| `kimi-k2.5` | *lowest-cost listed tier* (`specs/agent-bridge.md:212`); not in the measured local catalog | **ACCEPT** |
| `kimi-next` | appears nowhere in this repository | **ACCEPT** |

Not one identity in the pattern's accept-set appears in the selectable profile candidate table at
`specs/provider-model-benchmarking.md:50-57`. Every identity in that table is refused. The gate
admits exactly the tiers doctrine calls unverified, lowest-cost, or not-yet-candidate, and refuses
exactly the tiers doctrine calls flagship, frozen-onboarding-subject, and role-admitted.

## Measured finding 2 — the "deliberately candidate-only" reading is refuted

The hypothesis that K3 is fenced out on purpose because it is candidate-only fails on three
independent grounds:

1. **It admits weaker siblings.** `specs/agent-bridge.md:226-227` records that neither K2.6 nor K2.5
   appeared in the measured local managed catalog and that their exact API identifiers remain
   unverified on this machine; `:231-232` records that adding K2.7-Code, K2.6, or K2.5 is a separate
   post-landing candidate that must not alter the frozen K3 subject. A fence built to exclude
   candidate-grade models cannot coherently admit models of strictly lower standing.
2. **It refuses the one already role-admitted Kimi cell.** `kimi-code/kimi-for-coding` is the
   "separately role-admitted historical baseline" (`specs/provider-model-benchmarking.md:52`) and is
   refused by the same pattern.
3. **The predicate is a family test, not a status test.** `specs/fleet-universal-provider-control-reconciliation.md:213-216`
   states the universal quality floor requires the priority-to-role mapping, `high` effort,
   `FRONTIER_HIGH`, **a frontier model family**, *and* an exact reviewed cell. Onboarding status is
   carried by the exact reviewed cell and the launch allowlist, not by the family regex. Encoding
   onboarding status in the family predicate would duplicate a control that already exists and
   invert its meaning.

## Measured finding 3 — the "stale regex" reading is also refuted; the alias seam is the better explanation

`git log -L 341,346:tools/universal_provider_control.py` returns exactly one commit: `0054253`,
2026-08-18, *provider control: certify request and rollout boundaries*. The block has never been
amended. K3 entered doctrine eight days earlier, in `2357f8e`, 2026-08-10, *docs: add Kimi provider
parity strategy* — the same commit that introduced `kimi-k3`, `kimi-code/k3`, and the K2.7/K2.6/K2.5
ladder. The pattern was therefore authored *after* K3 was already the named subject, so this is not a
generation that landed and was never picked up.

The accept-set is instead exactly the *API survey* naming ladder relayed on 2026-08-10
(`RECEIPTS.md:205-206`), transcribed into a gate that is applied to `request["model"]` — a field the
onboarding pin, the profile allowlist, and the benchmarking table all express in *managed-CLI* form
(`kimi-code/...`). `specs/agent-bridge.md:221-226` forbids precisely this move: the adapter must
record requested identity, effective backend, and transport, and "name similarity, display labels,
and pricing pages never prove alias equivalence." The regex treats the survey's API ladder as
authoritative over the measured local catalog, which is the identity-seam error that section exists
to prevent. `kimi-next`, present in the pattern and nowhere else in the repository, is consistent
with an externally-sourced or speculative ladder rather than a measured one.

This paragraph is an inference about authorship drawn from the accept-set and the commit order. It
is offered as the best-supported reading, not as a proven intent, and the adjudicator should treat it
as rebuttable.

## Measured finding 4 — no test pins any non-Claude branch of the floor

`tests/test_universal_provider_control.py` never executes the `kimi`, `openai`, or `grok` branch of
`FRONTIER_HIGH_MODEL`, in either direction:

- the profile fixture loops all four providers at `:225-231` but hardcodes `"model": "claude-opus-4-1"`
  for every row (`:206`), so the allowlist asserts that `kimi` / `kimi-code/1.0` is reviewed for a
  Claude model;
- every control request is built with `"provider": "claude"` (`:385`) and `"model": "claude-opus-4-1"`
  (`:389`);
- the sole quality-floor test, `test_r15_05_quality_floor_and_exact_argv_contract_reject_weak_or_extra_launches`
  (`:3404-3414`), sets `"tiny-economy-model"` and so exercises only the Claude pattern's negative;
- the Kimi lines cited during triage — `:228`, `:253`, `:259`, `:351-354`, `:1082` — all bind the
  *adapter* (`kimi-code/1.0`) and its capacity dimensions (`context`, `monthly`). None touches
  `request["model"]`.

`python -m unittest tests.test_universal_provider_control` on the bound bytes: **185 tests, OK**. The
suite is green and the inversion is invisible to it. Under the closed-set discipline, a floor with
four provider branches owes four positive and four negative cells; it currently has one of each, both
Claude. That coverage gap is a finding in its own right and would have caught findings 1 and 5.

## Measured finding 5 — the same drift is present in the Claude pattern

`^claude-(?:opus|sonnet)-` refuses `claude-fable-5`, which `RECEIPTS.md:1191`, `:1197`, `:1302` and
`:1382` record as measurably executed fleet work (`fable/claude-fable-5 PASS 7.5s`; a 456.5 s run
returning `PORT_VERDICT: BLOCK` with exact output bytes and SHA), and which
`capacity-control/PROJECT-ADOPTION-MATRIX.md:10` names alongside `claude-opus-5/max` as a fleet
mapping. `ruling-candidates/opus-model-failback-r4.md:5,11` makes an exact Fable coordinator seat
part of a proposed failback chain.

## ⚠ CORRECTION to finding 5 — this candidate undercounted the drift, and the correction is the better doctrine

**Withdrawn:** the first revision of this section claimed *"the `openai` and `grok` patterns are
currently consistent with the identities this repository names (`gpt-5.6-sol`, `grok-4.5` both
match)"* and concluded the defect was **two-of-four**. That was wrong, and it was wrong by exactly
the method failure this candidate elsewhere accuses the table of. It tested only the **accept-side**
— do the doctrine-named frontier identities pass? — and never the **refuse-side**: does the pattern
wrongly admit a doctrine-named *sub-frontier* identity? A closed set owes both directions. This one
was published with half of it.

**What a refuse-side sweep actually finds:**

- `^(?:gpt-5|o[3-9])` **admits `gpt-5.4-mini`**, which `FAILOVER.md:169` names as the cheapest
  low-effort **narrator**, `FAILOVER.md:222` states *"Narrators have zero authority"*, `RULINGS.md:168`
  says to *never route the derivative digest into a reviewer seat*, and `FAILOVER.md:223-224` plus
  `specs/conjugal.md:101` record as **scheduled to retire on 2026-08-31** — a date already past. It
  also admits `gpt-5.6-luna`, named a zero-authority narrator at `FAILOVER.md:222` and `RULINGS.md:206`
  (with dual standing as adobe-ingester's sole implementer at `specs/adobe-ingester.md:13`, so that
  cell is ambiguous rather than plainly wrong).
- The floor gates a cell whose `role` may be `REVIEW` (`PRIORITY_ROLE`, `:334-340`). So a model
  doctrine forbids from a reviewer seat currently satisfies the frontier-family half of the floor.

**THE ROOT CAUSE, which the corrected count exposes and the original framing hid.** The four patterns
are not four instances of one rule — they are two different *kinds* of rule:

| branch | keyed on | can it express a tier boundary? | consequence |
|---|---|---|---|
| `claude` | **family names** `opus\|sonnet` | **yes** — Haiku-class is outside the alternation | correctly refuses its own narrator; its defect is *omission* (`fable` missing), not breadth |
| `openai` | generation number `gpt-5`, `o[3-9]` | **no** | admits `gpt-5.4-mini`, `gpt-5.6-luna` |
| `kimi` | generation number `k2` | **no** | admits `kimi-k2.5`, the *lowest-cost listed tier* |
| `grok` | generation number `4\|5` | **no** | admits any `grok-4.x`/`grok-5.x` tier |

> **A generation-number prefix cannot express a quality floor, because the cheap tiers live INSIDE
> the generation.** `gpt-5.4-mini` is a `gpt-5`. `kimi-k2.5` is a `k2`. Only the branch that keys on
> family names can say *opus but not haiku* — and it is the only branch that gets the tier boundary
> right. The Kimi inversion is not a transcription slip in one row; it is the predictable output of a
> matcher shape that has no way to say "not the cheap one."

The corrected count is therefore: **all four branches carry a defect. Three of four wrongly ADMIT an
identity; two of four wrongly REFUSE one.** The `grok` branch is the mildest — it wrongly refuses
nothing, and pre-authorizes `grok-4`/`grok-5` generation ranges that `RECEIPTS.md:366` records as
unmeasured (only `grok-4.5` appears in the measured catalog), which is the same
pre-authorization the Kimi branch performs with `kimi-next`.

**Why this correction strengthens rather than weakens the candidate.** The original proposition
asked for a curated accept-set per provider — which, applied to a generation-number matcher, would
have to be re-curated on every point release and would silently readmit the next `-mini`. The root
cause says the repair is *structural*: prefer family/tier-bearing identities over generation numbers,
so the pattern can state the boundary it is supposed to enforce. A count that had stayed at
two-of-four would have licensed patching two rows and leaving the shape intact.

## Measured finding 6 — the floor uses PREFIX matching, so no branch can enforce a tier boundary

Found while mutation-testing the controls, and it is the deepest layer of the same defect. Line 3555
calls `.match()`, not `.fullmatch()`. `re.match` anchors only the start, so every pattern in the
table is a prefix test. Every branch — **including `claude`** — admits an arbitrary cheaper variant
that shares a prefix with an admitted family:

| provider | probe | verdict |
|---|---|---|
| `claude` | `claude-opus-nano-9`, `claude-sonnet-lite-1` | **ADMIT** |
| `openai` | `gpt-5-nano` | **ADMIT** |
| `kimi` | `kimi-k2-ultracheap` | **ADMIT** |
| `grok` | `grok-4-mini-fast` | **ADMIT** |

None of those identities exists; that is what makes the point. **The Claude branch is correct only by
accident of naming** — Anthropic puts the tier in the family-name slot, so `haiku` falls outside
`opus|sonnet`. Nothing in the pattern enforces that, and a vendor who ships an `opus-mini` would land
inside the floor on day one.

This also makes the repair easy to get wrong in exactly the same way. While mutation-testing, an
attempt to narrow the OpenAI branch to `^(?:gpt-5(?:\.\d+-(?:sol|codex))?|o[3-9])` — which reads as
though it admits only `sol`/`codex` variants — was a **no-op**: with prefix semantics the leading
`gpt-5` still matches `gpt-5.4-mini`, and the controls correctly stayed green because nothing had
changed. Substituting a genuinely exclusive pattern turned them red. Any repair that does not anchor
the end will look like a fix in review and enforce nothing.

## Severity, stated honestly

`specs/fleet-universal-provider-control-reconciliation.md:30` documents
`tools/universal_provider_control.py` as a deployment-inert reference contract that cannot launch,
resume, terminate, authenticate, schedule, or contact a provider. **No live launch is blocked today
and no outage is claimed.** The defect is latent and propagating: this is the reference contract
projects are asked to ADOPT, so an adopter that installs it as written inherits a floor that refuses
its frontier models and admits its cheapest — including, on the OpenAI branch, a model doctrine
forbids from a reviewer seat and which was scheduled to retire on 2026-08-31. `specs/mlv-app.md:665` records a vendored copy
(`tools/provider_control/vendor/universal_provider_control.py`, 119,196 B,
`sha256:9a15dd34bc35a77e7f7aaba7952bc3712a25504ee52a213cfc64e4fc27f0e5c2`) whose bytes are not
present in this checkout; whether it carries this table is **UNEVALUATED** and must not be assumed
either way.

## Candidate proposition

Adopt, as a reviewed amendment to the universal quality floor, the position that
`FRONTIER_HIGH_MODEL` is a **frontier-family predicate over locally measured identities**, and:

0a. **the predicate is end-anchored** — `fullmatch`, or an explicit `$` — so that a pattern excludes
   what it appears to exclude. Without this, every other clause in this proposition is decorative:
   a prefix test cannot refuse a cheaper variant of an admitted family, on any branch (finding 6);
0b. **it keys on tier-bearing identity, never on a bare generation number.** This is the structural
   repair the ⚠ correction above exposes: `gpt-5.4-mini` is a `gpt-5` and `kimi-k2.5` is a `k2`, so a
   generation prefix cannot state the boundary the floor exists to enforce. Only the `claude` branch,
   which keys on `opus|sonnet`, can currently say *this family but not the cheap one* — and it is the
   only branch whose tier boundary is right. Curating the accept-set without changing the matcher
   shape would have to be re-curated at every point release and would silently readmit the next
   `-mini`;
1. its accept-set is derived from the measured local catalog and the selectable profile table, never
   from a relayed external API ladder;
2. it may not name an identity, or pre-authorize a generation range, that appears in no local
   measurement (`kimi-next` is removed; `o[3-9]` and `grok-(?:4|5)` stop pre-authorizing unmeasured
   generations);
3. it never encodes onboarding or candidacy status — that control stays solely in the exact reviewed
   cell and the launch allowlist, so a family match still admits nothing on its own;
4. every provider branch owes a positive and a negative test cell using an identity that provider
   actually carries, and the profile fixture stops asserting a Claude model for non-Claude rows;
5. a new provider generation entering `specs/` retro-obligates a sweep of this table in the same
   pass, since the table is the only place where a generation name must be restated.

Under 0-3 the OpenAI branch would stop admitting the zero-authority narrators `gpt-5.4-mini` and
`gpt-5.6-luna` into a cell whose role may be `REVIEW`; the Kimi branch would accept the `kimi-code/k3`, `kimi-code/k3-256k`, and
`kimi-code/kimi-for-coding` identities and the `kimi-k3` API identity, and would stop accepting
`kimi-k2.5`, `kimi-k2.6`, `kimi-k2.7-code`, and `kimi-next` until each is locally measured; the
Claude branch would accept `claude-fable-5`. **This candidate proposes those values; it does not
install them, and no byte of `tools/universal_provider_control.py` is changed by this file.**

## Required adjudication record before acceptance

- exact candidate commit, tree, and byte manifest for any implementing change;
- confirmation by a distinct adjudicator that widening the Kimi accept-set to K3 grants no routing,
  seat, vote, or independence authority, and that `specs/agent-bridge.md:228-232` (frozen onboarding
  subject; empty role cells) is preserved unaltered;
- the closed set for the coverage dimension: all four provider branches, positive and negative, with
  the reason each cell passes;
- hostile controls and the ratified governor suite green on the exact bytes, including a negative
  proving a below-family model is still refused per provider;
- an explicit accept/reject with reasoning appended by a distinct adjudicator to `RULINGS.md`.

Each project owner then publishes one standalone line in its sole-writer `specs/<project>.md`:
`ADOPT(UNIVERSAL_QUALITY_FLOOR_FRONTIER_FAMILY_DRIFT_R1, <table SHA-256>, <review receipt SHA-256>)`,
`DISTINGUISH(...)`, or `REJECT(...)`. Publication of this file earns no runtime or adoption credit.

This file must not be treated as the final `RULINGS.md` entry.
