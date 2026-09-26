# S28 — key rounds, receipts (Conjugal, `S28-metric-label-cardinality-unbounded`)

Outcome heading (Conjugal): `Outcome - PARKED at the three-round ceiling, NOT ACCEPTED (counts ZERO). The product defect is fixed.`

Ordering / identity / delivery witness (`python coordination/kernel-dogfood/check-ordering.py`, AUTHOR dates, read-only, run 2026-09-26): `S28 NO-CANDIDATE-CITED decl=27eee81@2026-09-22T07:10:17-05:00 cand=none identity=none delivered=unwitnessed outcome=DELIVERED-NOT-ACCEPTED note=bus-delivery-no-sha`

Key: class `codex-openai`. Every round below is a `codex exec` session (`session_meta.payload.originator=codex_exec`, `model_provider=openai`); `turn_context.payload.model` and `.effort` are quoted per round. Producer: Claude (class `claude-anthropic`), a different independence class.

Source files are Codex CLI rollout logs (JSONL), machine-local under `~/.codex/sessions/2026/09/<DD>/`. Rollout SHA-256 is of the whole file. **Excerpt** = the last `response_item` record with `payload.type=message`, `payload.role=assistant`, `payload.phase=final_answer`; its bytes are the UTF-8 concatenation of `payload.content[].text`, no trailing newline. **Verdict-line** SHA-256 is of the single verdict line of that excerpt, UTF-8, no newline (the S12/S13 convention). Extracted 2026-09-26, read-only, by a Claude Code receipt-extraction agent.

| Round | Tree named by the key | Model / effort | Rollout (`~/.codex/sessions/2026/09/<DD>/`) | Bytes | Rollout SHA-256 | Final-answer record | Excerpt bytes | Excerpt SHA-256 | Verdict line (verbatim) | Verdict-line SHA-256 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `23c52258a` | `gpt-6-astra` / `high` | 22/`rollout-2026-09-22T11-10-24-01a0c9e1-f4e3-7a80-b76d-c3898a0f1b59.jsonl` | 644,352 | `7387dd792b18e7d339d57c4dc791ab3fcb65d9fe60d6046ef6d10fd3ad7df072` | line 100, `2026-09-22T16:16:11.118Z` | 3241 | `1c07a38e433cea5570110171206542c0f6a02d0b8a6a6e9b0250137e7caf62d5` | `VERDICT: REFUSE` | `bd0ac07c453e4b5b94cce2df44b9a6eff50d228eb50952dc2cab7bca77d1a8ed` |
| 2 | `8553aba4f44773c7fda458c6d37e584ccba4c7df` | `gpt-6-astra` / `high` | 22/`rollout-2026-09-22T11-33-27-01a0c9f7-1068-71a2-b48a-254f0d21e6b2.jsonl` | 730,465 | `6f85d13207021551c8ad45f6c1b8c3fecf3665607fc605fb2e63fd3ecacbf3ae` | line 152, `2026-09-22T16:41:36.890Z` | 4439 | `5ed58f855cfe50c27f3332890ae3d0101c5a2c497163b2848e8239f96d970c14` | `VERDICT: REFUSE` | `bd0ac07c453e4b5b94cce2df44b9a6eff50d228eb50952dc2cab7bca77d1a8ed` |
| 3 | `e7410fbae` | `gpt-6-astra` / `high` | 22/`rollout-2026-09-22T12-05-17-01a0ca14-31fd-70c3-9364-9b25fb601622.jsonl` | 933,549 | `cf7201529ac16c4a6cb17dd84950b37538195d61942b1eb41d82d4a4363fde73` | line 169, `2026-09-22T17:16:28.496Z` | 3286 | `95a891d54f2aa8cd0c3615c8d9b8b15b05ce5291d23d1abd5bea4ff238bf9f3b` | `VERDICT: REFUSE` | `bd0ac07c453e4b5b94cce2df44b9a6eff50d228eb50952dc2cab7bca77d1a8ed` |

Every excerpt was extracted from, and hashed against, its rollout file in the same pass; each verdict line is byte-present in its excerpt.

## Reconciliation with the value recorded in the Conjugal Outcome

| Round | Recorded "verdict SHA-256" | What those recorded bytes actually are | Reproduced from the ROLLOUT? | Recorded rollout SHA reproduced? |
|---|---|---|---|---|
| 1 | `d448de17a1ad2c62f76ac8b7dd369962b0cf1dd3` | SHA-256 of the producer's machine-local **whole console transcript** of the `codex exec` run (124,486 B: banner, prompt, tool calls and outputs, then the final message). Capture hash reproduced: yes. Not a verdict excerpt; the rollout excerpt is contained in it modulo console encoding | **NOT REPRODUCED from rollout** | none recorded |
| 2 | `c6e8e2e1d4df14b0247c463bf3bab4fb6f00d2a4` | SHA-256 of the producer's machine-local **whole console transcript** of the `codex exec` run (138,881 B: banner, prompt, tool calls and outputs, then the final message). Capture hash reproduced: yes. Not a verdict excerpt; the rollout excerpt is contained in it modulo console encoding | **NOT REPRODUCED from rollout** | none recorded |
| 3 | `30cf37594a3b0124342e60d6d2b3fb274d450536` | SHA-256 of the producer's machine-local **whole console transcript** of the `codex exec` run (184,788 B: banner, prompt, tool calls and outputs, then the final message). Capture hash reproduced: yes. Not a verdict excerpt; the rollout excerpt is contained in it modulo console encoding | **NOT REPRODUCED from rollout** | none recorded |

## Excerpts (verbatim)

Machine-local temp paths inside an excerpt are replaced with `[machine-local temp path redacted]`; each digest above is of the **unredacted** original bytes, so a holder of the rollout can verify by re-extracting the record. No other change.

### Round 1

Record: line 100 of `rollout-2026-09-22T11-10-24-01a0c9e1-f4e3-7a80-b76d-c3898a0f1b59.jsonl`; `payload.phase=final_answer`; timestamp `2026-09-22T16:16:11.118Z` (UTC).

~~~~text
Verified candidate tree `23c52258a`; tracked worktree files match it. Measurements used fresh servers, separate temporary data roots, free ports, and only my traffic. Test servers were stopped. Repository files were unchanged.

| Property | Measured value | Result |
|---|---|---|
| P1 | **256** route-label lines after 2,000 distinct unmatched paths | **HOLDS** |
| P2 | **256** after another 2,000 distinct `/api/loop/X/<tail>` paths | **HOLDS** |
| P3 | Exactly **1** label with route `OTHER` after saturation | **HOLDS** |
| P4 | Exactly **1** added label: `GET /api/loop/:id` | **HOLDS** |
| P5 | Exactly **3** labels: `GET /`, `GET /api/docs`, `GET /api/metrics` | **HOLDS** |
| P6 | Exit status **0**, exact output `PASS: 6 assertions (server.metrics)`; finished in **109.113 seconds**, without timeout | **HOLDS** |

**Q1 — Inferred by inspection:** Yes, `+ 1` is correct. The first 255 distinct keys are admitted; the next unseen key creates `OTHER`, bringing the map to 256. Subsequent requests increment existing entries. No request sequence starting from the empty map produces a saturated map with a different count. Unsaturated sequences naturally remain smaller—for example, repeated completed requests only to `/` produce one entry.

**Q2 — Inferred by inspection:** `route_counts` is bounded: its sole insertion uses `boundedRouteKey`. However, another never-evicted map remains unbounded through the returned request context. `observeRequest` returns the uncapped `routeKey`, which [`enforceMutationRateLimit`](/C:/code/Conjugal/.claude/worktrees/modest-rhodes-8f1078/dashboard/server.mjs:1542) incorporates into `mutationRateBuckets` keys. Requests passing the Host/origin/auth checks reach this insertion before route validation. There is no cardinality cap or deletion; window expiration resets a bucket’s value without evicting its key. This was not exercised with additional inputs.

The other direct metrics map, `status_counts`, uses HTTP status codes; request logs rotate.

**Q3 — Inferred by inspection:** There is no complete routing table from which to derive an allowlist. Dispatch uses conditionals and regular expressions beginning at [`server.mjs:9911`](/C:/code/Conjugal/.claude/worktrees/modest-rhodes-8f1078/dashboard/server.mjs:9911). `DASHBOARD_CAPABILITIES` at line 99 and `closeoutRouteMap` at line 6280 contain partial route metadata, not a complete dispatch registry. The stated rationale holds.

**Q4 — Inferred by inspection:** Still true. `observeRequest` runs at line 9869, before Host rejection at line 9898 and authentication at line 9904. A 421 response therefore still records a route label through finalization. Leaving this ordering unchanged is consistent with bounding route-label cardinality: rejected requests also obey the cap. This does not resolve the separate collection identified in Q2.

VERDICT: REFUSE

1. **INFERRED BY INSPECTION, not measured:** `mutationRateBuckets` remains a never-evicted collection keyed by the uncapped route key returned from `observeRequest`. A caller passing the mutation security checks can continue adding distinct keys without a bound. Thus all six measured properties hold, but the broader collection-boundedness check in Q2 does not.
~~~~

### Round 2

Record: line 152 of `rollout-2026-09-22T11-33-27-01a0c9f7-1068-71a2-b48a-254f0d21e6b2.jsonl`; `payload.phase=final_answer`; timestamp `2026-09-22T16:41:36.890Z` (UTC).

~~~~text
Verified candidate tree `8553aba4f44773c7fda458c6d37e584ccba4c7df` from the specified worktree. No repository changes. All test servers stopped.

| Property | Measured value | Result |
|---|---|---|
| R1 | Exactly **256** labels after 2,000 unmatched paths | HOLDS |
| R2 | Exactly **256** after 2,000 further loop-tail paths | HOLDS |
| R3 | Exactly **1** `OTHER` label | HOLDS |
| R4 | Exactly **1** added label: `GET /api/loop/:id` | HOLDS |
| R5 | Exactly **3**: `GET /`, `GET /api/docs`, `GET /api/metrics` | HOLDS |
| R6 | **256** buckets when the 800 authenticated POSTs are the fresh server’s first HTTP traffic | **FAILS** |
| R7 | Exit status **0**; printed `PASS: 8 assertions (server.metrics)` | HOLDS |

R6 repeated with `/api/metrics` warm-up measured **255**, satisfying the threshold in that setup. The strict `<256` assertion depends on prior traffic. Both runs used the specified authenticated POST sequence.

**Q1. Every route-key consumer**

All five receive the result of `routeLabel`:

1. `route_counts` increment — yes.
2. Request log’s `route` field — yes.
3. Returned request context’s `routeKey` — yes.
4. Mutation bucket’s route component through `requestContext.routeKey` — yes.
5. Mutation bucket fallback — yes, calls `routeLabel` directly.

None bypasses that function. However, receiving its result does **not** establish an unconditional cardinality bound: its check does not reserve capacity for requests still in flight. See finding 2. [Source](C:/code/Conjugal/.claude/worktrees/modest-rhodes-8f1078/dashboard/server.mjs:1471)

**Q2. Other retained collections — inspection, not growth measurements**

- `savedViews` has no cardinality quota or automatic eviction. Authenticated view creation with distinct normalized IDs adds entries and persists them. Explicit DELETE removes entries, so this is retained application data, not literally a collection with no removal path. [Source](C:/code/Conjugal/.claude/worktrees/modest-rhodes-8f1078/dashboard/server.mjs:7901)
- `dashboardStreams` removes disconnected or dropped clients; `loopDecisionLocks` removes IDs in `finally`.
- `status_counts` uses HTTP status codes, a finite domain.
- `SYMBOL_INDEX` is rebuilt from repository files and replaces its previous value; request-selected lookup keys do not accumulate.
- Other inspected Maps/Sets are request-local or fixed enumerations; caches replace snapshots.

The two telemetry Maps remain never-evicted, and their shared admission check has the inspection finding below.

**Q3. Address component**

Conditionally: assuming a fixed, bounded set of actual socket source addresses, a valid route bound would also bound the product of address and route keys. For ordinary traffic exclusively from `127.0.0.1`, there is one address component.

Binding to `127.0.0.1` establishes the listening destination; it does not itself validate that every peer address equals that address. The key uses the socket address, not a forwarded-address header. This is an **inspection-based deployment assumption**, not a measured guarantee. The in-flight admission issue separately prevents certifying the intended route cap.

**Q4. Information loss**

The `route` field, context and rate-limit grouping lose route distinctions after overflow. The log retains the full parsed **pathname** separately.

**Measured:** the log contained `path: "/api/loop/X/tail-1999"` alongside `route: "OTHER"`. Query strings are excluded because logging uses `URL.pathname`; that is separate from this cap change.

VERDICT: REFUSE

1. **MEASURED — R6 fails on an initially empty server.** The prescribed 800 authenticated POSTs produced **256** buckets: 255 distinct POST labels plus `OTHER`. A prior metrics GET reduces the mutation allocation to 255, explaining the passing warm-up result. The strict requirement does not hold without that additional precondition.

2. **INFERRED BY INSPECTION — label admission does not reserve capacity.** `routeLabel` checks `route_counts.size` when a request begins, but that Map is updated only when the response finishes or closes. Overlapping requests can therefore receive distinct labels against the same available capacity; finalization inserts those labels without rechecking. Moving the check to creation fixes consumer consistency but does not prove the 256-key bound under overlapping requests. This was not measured, and no additional attack inputs were constructed.
~~~~

### Round 3

Record: line 169 of `rollout-2026-09-22T12-05-17-01a0ca14-31fd-70c3-9364-9b25fb601622.jsonl`; `payload.phase=final_answer`; timestamp `2026-09-22T17:16:28.496Z` (UTC).

~~~~text
Candidate tree verified: `e7410fbae`. Repository unchanged; all test servers stopped.

| Test | Measured result | Status |
|---|---|---|
| T1 | 2,000 unmatched paths → **256 labels** | HOLDS |
| T2 | Further 2,000 loop-tail paths → **256 labels** | HOLDS |
| T3 | **1 added label:** `GET /api/loop/:id` | HOLDS |
| T4 | **3 labels:** `GET /`, `GET /api/docs`, `GET /api/metrics` | HOLDS |
| T5 | Empty map; six `Promise.all` waves of 500; **3,000 completed, zero errors, 256 labels** | HOLDS |
| T6 | 800 authenticated POSTs → **256 buckets**; **no prior HTTP traffic** | HOLDS |
| T7 | **Exit 0**, printed `PASS: 10 assertions (server.metrics)` | HOLDS |

Earlier T5 attempts encountered connection errors. The successful measurement used 500 pre-established TCP connections per wave, without preliminary HTTP requests, and closed connections after each response.

**Q1 — `route_counts`:** Yes, bounded for every request interleaving, by inspection. The insertion check and `Map.set` execute synchronously without yielding. At 255 entries, an unseen key becomes `OTHER`; at 256, subsequent insertions only update existing entries. No request sequence exceeding the cap was found.

**Q2 — `mutationRateBuckets`:** Its cardinality is likewise bounded by the synchronous insertion check. The check is defensive in the supplied suite, but load-bearing generally: overlapping authenticated mutations can populate buckets while unfinished responses leave `route_counts` unsaturated. Contrary to the comment, bucket insertion occurs before handler execution, not at response completion. Removing this bound was **not tested**, per the no-modification instruction.

However, bucket lookup occurs **before** overflow remapping, causing the counter defect below.

**Q3 — Other collections:** By inspection, `savedViews` has caller-controlled IDs and no cardinality cap or automatic eviction; records persist until explicitly deleted. It is intentional application storage, not another append-only telemetry collection. I found no additional never-evicted request-metadata collection with unbounded caller-selected keys: status keys are finite, stream clients are removed, and decision locks are released. This is **inspection, not measurement**.

**Q4 — Creation-time bound:** Redundant for the two Maps’ cardinality guarantees now that both insertion sites enforce their own bounds. It still changes downstream route labels and bucket grouping, so removing it is not behavior-neutral. Document that distinction; the creation-time check alone cannot guarantee bounded keys across overlapping requests.

VERDICT: REFUSE

1. **INFERRED BY INSPECTION, supported by MEASURED T6 behavior:** In [server.mjs](C:/code/Conjugal/.claude/worktrees/modest-rhodes-8f1078/dashboard/server.mjs:1566), the rate limiter retrieves the original client/route bucket before remapping new keys to bare `OTHER`. Overflow requests therefore miss the stored overflow bucket, create a fresh counter, and overwrite `OTHER` with count 1. T6 returned **800 HTTP 404 responses and zero 429s in 6.333 seconds** under the default 60-request/60-second setting. Cardinality holds, but overflow rate limiting loses its accumulated count. Resolve the final bucket key before retrieving and incrementing its counter.
~~~~
