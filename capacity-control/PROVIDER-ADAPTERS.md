# Provider adapters and quality-preserving demand controls

**Status: measured candidate; no role admission or live enforcement.** Universal fields are
normalized only where native structured evidence exposes them. `null` or `UNEVALUABLE` is a real
state, never a cue to estimate from transcript prose.

| Provider surface measured 2026-08-18 | Native capacity/usage evidence | Bounded-context and turn controls | Adapter rule |
|---|---|---|---|
| Anthropic Claude Code 2.1.233 | OAuth usage buckets; assistant message ids and input/cache-create/cache-read/output usage | `--max-turns`, `--autocompact 100k`, `--output-format stream-json` | Deduplicate message snapshots by message id. Preserve exact model/effort when credit is model-bound; never enable fallback for such a run. |
| OpenAI Codex CLI 0.144.6 | `token_count` events with cumulative input/cached/output/reasoning totals and rate-limit windows | JSONL output and durable task checkpoints; no max-turn option exposed by this installed CLI | Use the latest cumulative total, not a sum. Project wrapper enforces wall/slice boundaries. Fresh tasks/checkpoints replace bloated resumed contexts at material seams. |
| Moonshot Kimi Code 0.34.0 | `usage.record` per-turn events with input-other/cache-read/cache-create/output | wire streaming and explicit/automatic compaction; no max-turn option exposed by this installed CLI | Count only `usage.record`, not its duplicate `step.end`. Avoid subagents for trivial work; each subagent consumes an independent context. External wrapper supplies the hard slice boundary. |
| xAI Grok Build 1.0.3 | cumulative durable `turn_completed.usage` including input/cache/output/reasoning/modelCalls/turns | `--max-turns`, structured streaming, `/context`, `/compact` | Use the newest cumulative terminal event. API adapters keep a stable conversation/cache key and append-only prompt prefix; a cache miss remains correct and observable. |

Sources: [Claude CLI reference](https://docs.anthropic.com/en/docs/claude-code/cli-usage),
[OpenAI compaction guidance](https://developers.openai.com/api/docs/guides/latest-model),
[Kimi sessions and context](https://moonshotai.github.io/kimi-code/en/guides/sessions.html),
[Kimi agent context isolation](https://moonshotai.github.io/kimi-code/en/customization/agents.html), and
[xAI prompt-caching guidance](https://docs.x.ai/developers/advanced-api-usage/prompt-caching/best-practices).

## Universal ordering

1. Eliminate model-powered polling, registration, hashing, joins, liveness, and no-work heartbeats.
2. Require a frozen exact subject for review and a bounded, role-qualified profile for every run.
3. Generate a compact deterministic evidence capsule with hashes and raw-evidence pointers.
4. Admit against the exact quota domain, fresh snapshot, active reservations, priority reserve, and
   post-reset quiet period.
5. Bound the slice; checkpoint unfinished work as `PAUSED_BUDGET`, never as success.
6. Normalize native usage and compare useful outcomes, defects found, rework, and unchanged project
   gates before changing a role cell, model, or effort.

Provider/model routing is a separately qualified quality decision. Capacity control never grants a
role cell and never silently substitutes a cheaper profile. A lower-cost profile is eligible only
after the fleet's existing provider-model benchmark protocol proves it for the exact role.

## Cross-host limit

The reference broker is a machine-local enforcement plane. If one quota domain is used from more
than one host, local leases cannot serialize it. Such a domain remains shadow-only until a reviewed
distributed lease backend exists, or each host receives a conservatively partitioned allowance that
cannot overrun the shared hard cap. Git and the doctrine bus are too latent to serve as a live lock.
