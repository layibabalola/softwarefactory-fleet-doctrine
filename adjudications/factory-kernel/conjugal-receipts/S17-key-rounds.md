# S17 — key rounds, receipts (Conjugal, `S17-jev-product-hook-python-io-helper`)

Subject: the product hook's I/O moves into a Python helper (`scripts/jev/jev_shadow_helper.py`) with
handle-authoritative writes, answering S16's wall ("a bash-resident write path on a msys/Windows hybrid
namespace cannot be made handle-authoritative"). CJ-A3 of the fleet Jev shadow-mode standard, product
path, shadow only, opt-in. Declaration Conjugal `535135396` (author 2026-09-20T22:15:54-05:00), before
any code; candidate `72b00e182` (author 23:15:25), identity `62bdfe78ec1a1b12b081dc6e979be7f74e3f77c1`,
recomputable via `git -C C:\code\Conjugal rev-parse 72b00e182^{tree}`; fast-forwarded to `master` and
pushed; ordering witnessed by `coordination/kernel-dogfood/check-ordering.py` against AUTHOR dates.
Key: class `codex-openai`, `gpt-6-astra`, high effort, each round a detached OS process bound
per-command; the SAME prompt bytes both rounds.

| Round | Tree | Verdict | Rollout under `%USERPROFILE%\.codex\sessions\2026\09\20\` | Rollout SHA-256 |
|---|---|---|---|---|
| 1 | `62bdfe78ec1a1b12b081dc6e979be7f74e3f77c1` | none — `KEY_UNAVAILABLE_BY_PROVIDER` ("This content was flagged for possible cybersecurity risk", 1 occurrence) | `rollout-2026-09-20T23-17-02-01a0c22e-7df3-7661-acbd-bfe77126b525.jsonl`, 836,460 bytes | `5063916c18c65c1328d3211ff57218d97f2df713feacc09aef7eb90a154ab181` |
| 2 | `62bdfe78ec1a1b12b081dc6e979be7f74e3f77c1` | none — `KEY_UNAVAILABLE_BY_PROVIDER` (2 occurrences; identical re-run, not a rephrasing) | `rollout-2026-09-20T23-43-48-01a0c247-0009-7d73-829b-e2b23c07c84c.jsonl`, 730,298 bytes | `3b02f3259048a6c0e01f6a381639d5eba8b16cf5888e479c94a4ed6197f8d7a9` |

No verdict line exists in either rollout, so there is no verdict-line digest. The third reserved round
was NOT spent: the two rollouts show the filter firing on the review's own reasoning (constructing
alias, egress and secret-handling attacks against a write path), not on any fixture — the S14 fixture
rule (no token-shaped strings) held and was re-verified by grep before round 1. A third identical
launch is a third identical kill; the standing rule "never re-prompt around the provider filter" binds.

**Disposition.** Delivered, NOT accepted, PARKED, counts zero — an empty eligible reviewer pool is
typed HELD, never reviewed solo, never downgraded. **Wall named:** the `codex-openai` class cannot
finish reading a Conjugal write-path subject (S14 round 3 and both S17 rounds were filter-terminated;
S15 and S16 reached verdicts only because their attacks were narrower). **Resume actor (owner-side,
credentials/account):** authorise the Codex account for security-adjacent review, or name a second
independence class the kernel accepts for K6. Until then the product hook stays opt-in, shadow-only,
unkeyed.

**Bars (producer-measured, offline unless stated):** 1–2 met (bash suite; `tally-votes.sh` output
byte-identical to `git show 535135396:scripts/tally-votes.sh`; no python spawn on opt-out); 3, 4, 5, 8
met (22 python assertions: hard link, symlink, junction, swap-after-validate, no-final-newline,
fd-1/fd-2 alias, HOME inside a git work tree — all REFUSED; response fakes all `invalid_response`; the
captured real response passes whole); 6 met (S15 `--dry` output byte-identical across the extraction;
52 tests); 7 met, live and opt-in: 20 packets, 20 lines to the fixed log, 17 agree, 2 disagree = the two
known salvage reversals (1.00 / 0.97), 1 timeout fallback, USD 0.0007.

Trap for the fleet: **a security-hardening subject can be unreviewable by construction under a provider
cyber filter.** The filter is keyed to what the reviewer must write, not what it reads; a fixture rule
cannot clear it. Declare the second independence class BEFORE the subject, or the K6 budget is spent on
kills.
