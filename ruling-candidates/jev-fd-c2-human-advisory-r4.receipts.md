# Receipts: JEV-FD-C2-ADVISORY-1 r4 — ratification

**Digest convention.** A candidate's digest is the SHA-256 of `git show <commit>:<path>` bytes (the
committed blob, LF), never a working-tree checkout — `autocrlf` on this Windows host CRLF-converts a
checkout and produces a different, non-canonical hash.

- Blob digest of record (`git --no-optional-locks show 88f8acd:ruling-candidates/jev-fd-c2-human-advisory-r4.md | sha256sum`):
  `c2f22a9f58ea4b2df68ffe76aaabe2c561475280566db6fcb93c8007de73ce94`
- CRLF working-tree checkout hash on this host (NOT the digest of record, recorded only to flag the trap):
  `278019960afa173d7930f9cac533f9afa5a690e52109b23ffd3172a6fdf7ab2e`

Both blind seats below were bound to the blob digest of record, `c2f22a9f…`, verified independently
before this receipt was written.

## Seat A — codex-openai `gpt-6-astra`

Verdict line: `RATIFY c2f22a9f58ea4b2df68ffe76aaabe2c561475280566db6fcb93c8007de73ce94`

Full text, quoted verbatim from
`scratchpad/adv4-seat-codex.out` (the seat's own transcript, this session's scratchpad):

> RATIFY c2f22a9f58ea4b2df68ffe76aaabe2c561475280566db6fcb93c8007de73ce94
>
> - **Identity:** Exact candidate bytes at `88f8acd` match the required SHA-256. All five evidence-file digests match; the evidence files and blind harness match `1587b73`. The question blob and `questionSetVersion` also match.
> - **Authority:** The licence permits a manually invoked, human-read comparison that widens review. Its explicit prohibitions preserve §5's "never touches a verdict" boundary. `origin/master:RULINGS.md` R10.2 allows this project-naming further ruling. `CLAUDE.md` identifies `RULINGS.md` as the register; promotion still requires the ratified entry to be recorded.
> - **Recomputed evidence:** Fidelity **114/131**; adjudication **15/17 decided**; Jev–consensus **9/15**; consensus–incumbent **6/15**; rescored **123/131**, or **123/129** excluding undecidables. All match. These remain selected-disagreement results and mixed-reference rescores, not full-cohort blind correctness.
> - **Blindness:** Reconstructed all 131 states: **49 affected samples, 59 removed lines, zero merge-verdict label tokens**. All 17 recorded judge states match reconstruction. The disclosed removal marker occurs in 10/17. All **41** judge/adjudicator input and prompt-template hashes match reconstruction; prompt construction excludes Jev's answer and incumbent-label fields. Consensus decisions recompute without discrepancies. Owner decision (a) exists as the first decision row and admits model-consensus evidence.
> - **Falsifier:** The corrected sheet CLI produces **17 rows**, zero answer-bearing verdict-token leakage, and `stateVersion: state2`. The old arguments reproduce zero rows. Tests explicitly mock downstream adjudication/rescoring; they do not establish a completed live pipeline. Actual local extraction returns **5 rows**, egress clean, below **100**. This makes the fresh-cohort falsifier **honest but not yet runnable**, not void.
>
> **Weakest claim:** The falsifier's "fidelity" is mixed-reference agreement. It also permits `STANDS` with only one decided disagreement while other adjudications are missing; I reproduced that case. Thus it cannot substantiate complete-cohort correctness. This does not contradict its expressly decided-row denominator or the narrow advisory licence; Q6 remains unmet.
>
> **Execution qualification:** Filesystem outputs were captured in memory. Direct child spawning was blocked; dry-run orchestration used actual extraction/screen results supplied in memory. I read the tests but did not independently rerun all 156. No network calls, credential changes, or filesystem writes were made.

Rollout evidence (recovered from `scratchpad/adv4-seat-codex.err`, `session id: 01a0c180-f1bf-7293-93d8-9018705961b2`):

- Rollout file: `rollout-2026-09-20T20-07-28-01a0c180-f1bf-7293-93d8-9018705961b2.jsonl`
  under `%USERPROFILE%\.codex\sessions\2026\09\20\`
- Size: 951073 bytes
- SHA-256 (whole file): `dcd8373ccea3a933f1a2f7105a80e21a84a563921c7237a9d7fa5c103e75c8ff`
- SHA-256 of the verdict line as it appears in the rollout (`RATIFY c2f22a9f…\n`):
  `e4fe6a5233912c789ad368770d7a3f57fa67ad7ab04bb4199833707788402c4a`

## Seat B — claude-anthropic Opus 5 (subagent, in-process)

Verdict line: `RATIFY c2f22a9f58ea4b2df68ffe76aaabe2c561475280566db6fcb93c8007de73ce94`

Summary of the seat's full transcript (held in the orchestrator session, not a separate file):
identity and §4-only diff verified against the blob digest of record; all recounts reproduced
independently (fidelity 114/131; adjudication 15/17; Jev–consensus 9/15; consensus–incumbent 6/15;
rescored 123/131; 123/129 excluding undecidables — matching Seat A's recomputation); the r3→r4
remedy reproduced (17 rows, zero verdict-token leakage, the r3-invocation form returns 0 rows, and
running with the corrected flag omitted still leaks on 8/17); the full local test suites pass
(18/18 and 156/156); a dry run against the live cohort returns 5 rows, well under the 100-row gate;
weakest claim identified independently and consistently with Seat A: the script's `WITHDRAW`
wording, applied to an under-powered (sub-100) cohort, overstates what a 5-row sample can support.
Verdict: `RATIFY c2f22a9f58ea4b2df68ffe76aaabe2c561475280566db6fcb93c8007de73ce94`.

## Ratification statement

Two blind, cross-family seats (codex-openai `gpt-6-astra`; claude-anthropic Opus 5), each bound
independently to the blob digest of record `c2f22a9f…`, both returned `RATIFY` against that exact
digest. Under the owner ruling of 2026-09-06 (adversarial seats ratify), **JEV-FD-C2-ADVISORY-1 r4
is RATIFIED.**
