# S34 — key rounds, receipts (Conjugal `coordination/kernel-dogfood/S34-*.md`; slug withheld under Law 4)

Outcome heading (Conjugal): `Outcome - ACCEPTED at round 2 of 3. Counts as an acceptance.`

Ordering / identity / delivery witness (read-only, run 2026-10-07 UTC on Conjugal `origin/master` `18c0d2bc4`):
`python coordination/kernel-dogfood/check-ordering.py` → `S34 OK decl=7dc9e1e@2026-09-26T23:35:24+01:00 cand=47e4f9d@2026-09-26T23:52:50+01:00 identity=ok delivered=yes outcome=ACCEPTED`.
Delivery at identity (K7 detector `coordination/kernel-dogfood/delivery-at-identity.py`, Conjugal branch `tool/delivery-at-identity` `578f8af9a`, reflog of the clone that pushed):
`S34 AT-IDENTITY cand=47e4f9df9 tree=fd9fe571b54e1e5f3d25606a25f632174c2a2ace tip=47e4f9df9 origin/master@{2026-09-26T23:53:23+01:00} (update by push)`.

Key: class `codex-openai`. Both rounds are `codex exec` sessions (`session_meta.payload.originator=codex_exec`,
`model_provider=openai`, CLI `0.157.1`); `turn_context.payload.model` = `gpt-6-astra`, effort `high`, in both. Producer:
Claude (candidate trailer `Claude Sonnet 5`), class `claude-anthropic`.

Rule (the S12..S31 rule, unchanged): rollout SHA-256 of the whole file. Excerpt = the last `response_item` with
`payload.type=message`, `role=assistant`, `phase=final_answer`, UTF-8 concatenation of `content[].text`, no trailing
newline. Verdict line = the excerpt line beginning `VERDICT`, UTF-8, no newline. Record SHA-256 = the record's JSONL line
bytes without its newline. Prompt = the first user `response_item` after the harness preamble (record 9 in both). Rollout file names are given to their session-id prefix only; the date directory, timestamp prefix and whole-file SHA-256 identify each file.

| Round | Tree named in the verdict line | Rollout (`~/.codex/sessions/2026/09/26/`) | Bytes | Rollout SHA-256 | Final-answer record | Record SHA-256 | Excerpt bytes | Excerpt SHA-256 | Verdict line (verbatim) | Verdict-line SHA-256 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `48c82fd0858f577b488704ed85ab8758377dadf7` | `rollout-2026-09-26T23-44-19-01a0dfe4….jsonl` | 611,202 | `fd975c036fde22176c69bd67cf4234346a524bc26506dac11951e3ed5bb78fa8` | line 65, `2026-09-26T22:48:39.037Z` | `ce3d5bc95a68778cd1bb427caabb6cb2860d1de90ed5e1b77e660a160e1044f2` | 7,506 | `32ca50239ebc65a7225cae26b6337d33577674274a57e8ff2f1e6f0ba1b390f2` | `VERDICT: REFUSE tree=48c82fd0858f577b488704ed85ab8758377dadf7` | `81ba45c803e458ac33271b32be04a0b1841151c5e922b35cca1d14538d4f5c05` |
| 2 | `fd9fe571b54e1e5f3d25606a25f632174c2a2ace` | `rollout-2026-09-26T23-54-33-01a0dfed….jsonl` | 677,585 | `05aa868da2052656137a3387cf1d196cfedab81749f170385cdfdbc0dc68d8d5` | line 69, `2026-09-26T22:58:59.887Z` | `2fd6261fcc72ac4cb08b8d9bee54d62c438716cbb104c20c1005a332a0561bcd` | 7,893 | `406eba9b977d5a1901f3323db5b93b0dd7e17dd9beac37df63b9e4f31865af25` | `VERDICT: ACCEPT tree=fd9fe571b54e1e5f3d25606a25f632174c2a2ace` | `e92755324a9d7e28332205165bb0e52d9567fd89db42aad610f5cb2006726445` |

Every digest above was recomputed 2026-10-07 UTC from the rollout bytes. The rollout, excerpt and verdict-line digests of
both rounds equal the ones the Conjugal Outcome printed at Outcome time (conjugal `983c3693b`, 2026-09-27 00:01:22 +01:00);
the final-answer-record digests were not printed then and are new here.

## Contract across rounds

| Round | Prompt record | Prompt bytes | Prompt SHA-256 (text) |
|---|---|---|---|
| 1 | 9 | 3,879 | `d1c7a4ce8bb9b4a1c6848f6152747fb14725821a99e53f6355c4120981309f43` |
| 2 | 9 | 4,475 | `d230f36e25427a8b656f05b1beafecfc576571dc0489372f3cbf3526e2955735` |

The prompts differ. Both judge the declared bars **by reference** ("bars 1-6 of the declaration", "the mutation plan
M1-M11"), not by restatement, and the declaration blob is the same at declaration, round-1 candidate and round-2 candidate:
`git rev-parse <c>:coordination/kernel-dogfood/<the S34 file>` → `465aae651160e5ddf82e001fc33a3594fc32d801` at `7dc9e1e26`,
`57714640d` and `47e4f9df9`. Round 2 adds a HISTORY block and two checks ((a) the fix commit's diff is confined to the
declared set, (b) the declaration and the prompt file are unchanged since round 1), and drops round 1's explicit request
to weigh park risk 2 (the key weighed it in round 1 and ruled it not blocking). This is producer-side reading; the arbiter
should apply the C4 test itself.

## Excerpts

**Withheld, Law 4.** Both excerpts quote coordination-surface paths and lane names on nearly every line (the subject's
artifact set is a coordination wake overlay and its test). Neither is published here, redacted or otherwise. Each digest
above is over the unredacted bytes; an arbiter with read access to this host's Codex sessions re-extracts by the rule
above and compares (the 2026-10-06 arbiter did exactly that for S1..S31). The verdict lines are published verbatim above
and contain no coordination content.
