# Ruling candidate: universal quality-floor frontier-family drift R2

Status: **PROPOSED ONLY — ZERO AUTHORITY. NOT A RULING, NOT A FIX, NOT AN ADOPTION.**

Supersedes `ruling-candidates/universal-quality-floor-frontier-family-drift-r1.md` (unmerged, on
branch `claude/strange-chaplygin-6efd1b`, last commit `718a782`, 2026-09-02, no PR ever opened).
This revision changes no bytes in `tools/universal_provider_control.py`, grants no launch, routing,
seat, vote, onboarding or adoption authority, and admits no profile to any fleet role. The automatic
launch gate remains CLOSED.

## Why there is an r2 at all — r1 fails its own verification rule

r1 pinned its bound subject at `12b0a56e6352dc4d5e74e388669abe151141f4e8` and published the rule an
adjudicator must check: *"`git log --oneline 12b0a56..HEAD -- tools/universal_provider_control.py`
must be **empty**."*

Run at the bound subject below, it returns **six commits** (`f94cec8`, `f2f71c2`, `fc76bf6`,
`8e20b4a`, `6a3803f`, `d67b078` — authored 2026-08-20/23, landed on master after the fork point).
All three of r1's pinned files have moved since:

| file | r1 pin (blob) | now (blob) | delta |
|---|---|---|---|
| `tools/universal_provider_control.py` | 266,076 B | 308,014 B | +15.8% |
| `tests/test_universal_provider_control.py` | 273,883 B | 401,821 B | +46.7% |
| `specs/agent-bridge.md` | 31,632 B | 41,995 B | +32.8% |

**r1 is therefore unadjudicable as written** — not refuted, but no longer measured against bytes that
exist. That is the whole reason for this revision. r1 was correct to publish a rule that could catch
its own rot; the rule fired.

## Bound subject

Pinned **as measured**, at commit `62aa8b9ccbeec07f2e67b05bd8589273509275f0`.

r1 recorded working-tree byte counts on a Windows host; this repo has since recorded (`RULINGS.md`,
JEV-FD-C2-ADVISORY-1 r4) that a CRLF checkout does **not** hash to the digest of record. Both
conventions are given here so neither reading can be mistaken for the other. The **blob** column is
the digest of record; reproduce it with `git show <commit>:<path> | sha256sum`.

| file | blob (LF) bytes | blob sha256 | worktree (CRLF) bytes | worktree sha256 |
|---|---|---|---|---|
| `tools/universal_provider_control.py` | 308,014 | `c24eadc90ba14592d355252c753f8d81a14371d4cd52011657d17d09caea4418` | 314,269 | `97e80fd79a70ca20b0f5a9335a2d653b893e72ccc3d681fcf7cad4f4c2b18dd3` |
| `tests/test_universal_provider_control.py` | 401,821 | `52b5d7bf602b50e8efcf0c95abd1223b0a58f5323de2ac64712f081a77040d52` | 409,605 | `0587ffe16777ef26082364ef396506b15368fc995b10d962de7e9f7cafbd82b7` |
| `specs/agent-bridge.md` | 41,995 | `51c65683c4b957148e85c494656771db54c60176d019f56da1348bcf43ee5dd7` | 42,608 | `77f215755aa2ee02aeb1798fb5ab11e3318e734415df70569e9c4176d4deaee1` |
| `RULINGS.md` | 186,772 | `27c065629b564a1e1e4eed88482d995f6a4b2adce469abd1ba2a56da9dbdb479` | 189,161 | `294cace8b2a6876b072bb2d46578658bbb7f6478a70a088826a845a9baa05b98` |

**Do not restate these digests anywhere else.** An adjudicator derives currency, never re-pins. Note
that the second command is anchored on the table's own text rather than on a line number, for the
reason recorded below: a `file:line` citation is a pin and decays with its file.

```
git log --oneline 62aa8b9..HEAD -- tools/universal_provider_control.py      # SHOULD be empty
git log -L '/FRONTIER_HIGH_MODEL = /,+6:tools/universal_provider_control.py'   # the gate block itself
```

The second command is the one that matters, and it is why r1's findings survived r1's rot: the
`FRONTIER_HIGH_MODEL` block has **exactly one commit in its entire history** — `0054253`,
2026-08-18, *provider control: certify request and rollout boundaries*. Across the 19 days and the
hundreds of commits between r1 and this revision, the surrounding file grew by 42 KB and the gate
did not move by one byte.

## What carries forward from r1, re-measured and unchanged

Findings 1, 2, 3, 5 and 6 of r1 are **reproduced on the bound subject above** and are not restated
here; read r1 for their evidence
(`git show 718a782:ruling-candidates/universal-quality-floor-frontier-family-drift-r1.md`).
Re-measured on current bytes:

- the four patterns are byte-identical to r1's reading — `claude` `^claude-(?:opus|sonnet)-`,
  `openai` `^(?:gpt-5|o[3-9])`, `kimi` `^kimi-(?:k2|next)`, `grok` `^grok-(?:4|5)`;
- the consumer at `tools/universal_provider_control.py:3571` still calls **`.match()`**, not
  `.fullmatch()`, so r1's finding 6 (every branch is a prefix test and cannot refuse a cheaper
  variant of an admitted family) stands unamended;
- `kimi-code/k3`, `kimi-k3`, `kimi-code/k3-256k` and `kimi-code/kimi-for-coding` are still REFUSED;
  `kimi-k2.5`, `kimi-k2.6` and `kimi-k2.7-code` are still ACCEPTED — r1's finding 1 inversion intact;
- `claude-fable-5` is still REFUSED — r1's finding 5 intact.

r1's ⚠ correction (the root cause: a generation-number prefix cannot express a tier boundary,
because the cheap tiers live *inside* the generation) is likewise unaffected and remains the
load-bearing diagnosis. This revision does not improve on it; it adds the consequence r1 could not
yet see.

**One incidental measurement, recorded because it is the same defect class.** Carrying r1's citations
forward required re-deriving each one rather than copying it, and two had rotted with their files:
r1's `specs/fleet-universal-provider-control-reconciliation.md:30` is now `:33`, and its alias-seam
range `specs/agent-bridge.md:221-226` is now `:219-231`. Both still say what r1 said they say — the
prose moved, the substance did not. A `file:line` citation is a pin like any other and decays at the
rate its file is edited; every one restated in this document was re-derived on the bound subject, and
an adjudicator should re-derive them again rather than trust this sentence.

## Measured finding 7 (NEW) — the floor now contradicts an ADOPTED ruling, not merely a spec

r1 argued from spec standing — which identities `specs/agent-bridge.md` and
`specs/provider-model-benchmarking.md` call flagship, frozen or candidate. Six days after r1 was
written, the register settled the question directly. `RULINGS.md:1974` (**ADOPT — tiers by act**,
user ruling 2026-09-08) assigns a model per act, and `RULINGS.md:2315` (R11) explicitly keeps it
live: *"This cuts a DIFFERENT axis ... and does not retire it."*

- **Judgment tier** (`RULINGS.md:1974`): Fable at effort high; `gpt-6-astra`. Acts: *"one RATIFY
  synthesis, one cross-family review of the other family's production code on a
  protocol/timing/security seam, one factory-vs-product audit, one doctrine seam per packet."*
- **Loop tier**: Opus high, `gpt-5.6-sol`. Acts: *"the traffic cop and routine adjudication."*
- **Bounded tier**: Haiku, Sonnet for bounded review, `gpt-5.6-luna`.

`PRIORITY_ROLE` (`tools/universal_provider_control.py:335-341`) maps `ADJUDICATION → ADJUDICATE` and
`REQUIRED_REVIEW → REVIEW` — **exactly the acts the judgment tier is reserved for.** Evaluated as a
closed set, both directions, on the bound subject:

| tier (RULINGS.md:1974) | identity | `FRONTIER_HIGH_MODEL` |
|---|---|---|
| judgment | `claude-fable-5` | **REFUSE** |
| judgment | `claude-fable-5-1` | **REFUSE** |
| judgment | `gpt-6-astra` | **REFUSE** |
| loop | `claude-opus-5` | ACCEPT |
| loop | `gpt-5.6-sol` | ACCEPT |
| bounded | `claude-haiku-4-5-20251001` | REFUSE |
| bounded | `claude-sonnet-5` | ACCEPT |
| bounded | `gpt-5.6-luna` | ACCEPT |

**Three of three judgment-tier identities are refused. Two of two loop-tier identities are admitted.
Two of three bounded-tier identities are admitted.** A request carrying `priority: ADJUDICATION`,
`role: ADJUDICATE`, `qualityTier: FRONTIER_HIGH` and any judgment-tier model raises
`ControlError("UNIVERSAL_QUALITY_FLOOR_VIOLATION")`; the same request carrying a bounded-tier
narrator passes the family predicate.

The gate named FRONTIER_HIGH **inverts the tier ordering its own register adopted.** This is no
longer an inference about spec standing that an adjudicator may weigh against another reading — it is
a contradiction with an ADOPTED entry, and the register is the authority (`README.md` loses to
`RULINGS.md`; law 2).

`gpt-6-astra` is not a hypothetical cell. `RULINGS.md:2373` records it casting
`RATIFY c2f22a9f…` as one of the two blind cross-family seats that promoted JEV-FD-C2-ADVISORY-1 r4
— a ratification the floor's own predicate would refuse to fund.

**Rebuttable boundary, stated as r1 stated its own.** The floor matches `request["model"]` literally.
Whether the fleet issues judgment-tier work through this broker with these exact strings is
UNEVALUATED here — `capacity-control/PROJECT-ADOPTION-MATRIX.md:10` carries the managed-CLI forms
`claude-fable-5/max` and `claude-opus-5/max`, which is the alias seam `specs/agent-bridge.md:219-231`
forbids reasoning across. The finding is that the predicate contradicts the register on the
identities the register names; an adjudicator should not extend it to a claim about live traffic.

## Measured finding 8 (NEW) — r1's own clause 5 was owed twice and paid zero times

r1's candidate proposition, clause 5, asked that *"a new provider generation entering `specs/`
retro-obligates a sweep of this table in the same pass, since the table is the only place where a
generation name must be restated."* r1 proposed that rule prospectively. The window since has tested
it twice, and it failed both times:

| generation | first entered the repo | commit | swept? |
|---|---|---|---|
| `gpt-6-astra` | 2026-09-08 | `0126be1` | **no** — 13 days, gate unchanged |
| `claude-fable-5-1` | 2026-09-13 | `3dd41c5` | **no** — 8 days, gate unchanged |

Derivable: `git log --reverse -S"gpt-6-astra"` and
`git log -L '/FRONTIER_HIGH_MODEL = /,+6:tools/universal_provider_control.py'` have no commit in
common; the second returns only `0054253` (2026-08-18), which predates both.

This is evidence *about the repair*, not only about the defect. A curated accept-set that nobody
sweeps decays at the observed rate of one missed generation every few days. It is the strongest
available argument for r1's clause 0b — that the predicate must key on tier-bearing identity rather
than on a generation number that must be manually restated here every time a vendor ships.

## Measured finding 9 (NEW) — finding 4's coverage gap widened, and the suite is no longer green

r1's finding 4: no test pins any non-Claude branch of the floor. Re-measured on the bound subject,
after the test file grew **46.7%**:

| probe | r1 (266 KB file) | now (402 KB file) |
|---|---|---|
| `grep -c '"provider": "kimi"'` | 0 | **0** |
| `grep -c '"provider": "openai"'` | 0 | **0** |
| `grep -c '"provider": "grok"'` | 0 | **0** |
| `grep -c '"provider": "claude"'` | 1 | **1** |
| tests matching `def test_.*quality_floor` | 1 | **1** (`:3599`) |

Every `"model":` literal reaching a control request is still Claude-shaped or a synthetic
(`claude-opus-4-1`, `frontier-review-model`, `substitute-model`, `substitute`). **128 KB of new test
bytes added zero cells to three of the four branches this gate has.** Under the closed-set discipline
a four-branch floor owes four positive and four negative cells; it has one of each, both Claude —
unchanged from r1 while the suite grew by half again.

`python -m unittest tests.test_universal_provider_control` on the bound subject: **252 tests, FAILED
(errors=2)**, both surfacing `check_universal_manifest.ManifestError: MANIFEST_SUBJECT_MISMATCH`.
r1 recorded *185 tests, OK*. **The suite is red on master**, so r1's standing caveat — "green means
unchanged, not correct" — no longer even holds its antecedent. The two errors are named and analysed
in `ruling-candidates/universal-quality-floor-frontier-family-drift-r2.suite.md`; on their face they
are a *manifest* subject pin, i.e. **the same defect class as r1's own rotted bound subject and as
finding 8** — a recorded identity that the tree moved out from under. Whether they touch the quality
floor is UNEVALUATED and must not be assumed either way.

## Severity, stated honestly — unchanged from r1

`specs/fleet-universal-provider-control-reconciliation.md:33` documents this module as a
deployment-inert reference contract that cannot launch, resume, terminate, authenticate, schedule or
contact a provider. **No live launch is blocked today and no outage is claimed.** What finding 7
changes is the *character* of the latency: an adopter installing the reference contract as written
inherits a floor that refuses both of the fleet's ratified judgment-tier seats at exactly the
adjudication and review roles the register reserves for them, while admitting a zero-authority
narrator. `specs/mlv-app.md:665` records a vendored copy whose bytes are not in this checkout;
whether it carries this table is still **UNEVALUATED**.

## Candidate proposition

r1's clauses 0a, 0b and 1 through 5 are carried forward unamended and are not restated. This revision
adds one clause, which finding 7 makes available and r1 could not have written:

6. **The accept-set is bounded by the tier register, in both directions.** The frontier-family
   predicate must admit every identity `RULINGS.md` assigns to the judgment tier and must not admit
   an identity it assigns to the bounded tier, for any `role` in `PRIORITY_ROLE` that the judgment
   tier is reserved for (`ADJUDICATE`, `REVIEW`). The register, not a relayed vendor ladder, is the
   source of truth for which identities are frontier — and because the register is append-only, this
   clause is derivable at any later date rather than re-curated.

## Acceptance gate

This candidate is ADJUDICABLE when all four hold, each re-derived rather than read from here:

1. `git log --oneline 62aa8b9..HEAD -- tools/universal_provider_control.py` is empty;
2. `git log -L '/FRONTIER_HIGH_MODEL = /,+6:tools/universal_provider_control.py'` still returns
   only `0054253`;
3. the finding-7 table reproduces — re-run the closed set against the identities `RULINGS.md:1974`
   names, taking the tiers from the register at read time, not from this document;
4. the adjudicator is **not the author of any finding in r1 or r2**.

Condition 4 is not a formality. Every finding in both revisions was authored by the same
claude-anthropic seat, and r1 already published one materially wrong section (the withdrawn
two-of-four count) that was caught only by an independent closed-set sweep — the same method failure
it accused the gate of. A same-author adjudication of r2 would repeat the exact error the r1
correction exists to record.

## What this candidate does NOT ask for

It does not ask for any change to `FRONTIER_HIGH_MODEL`. Under the standing constraint, those bytes
do not move without an adjudicator's entry in `RULINGS.md`, and none exists — `grep -niE
"frontier.family|FRONTIER_HIGH" RULINGS.md` returns nothing on the bound subject. The controls in
`tests/` deliberately pin the current, defective behaviour; asserting the proposed repair would turn
them red and would itself be the unratified change this candidate exists to avoid.
