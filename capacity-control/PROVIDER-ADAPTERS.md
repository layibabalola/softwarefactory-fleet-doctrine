# Provider adapter contract

**Candidate only.** Adapters normalize provider evidence; they do not admit work or grant lifecycle
credit. Every adapter is pinned with its CLI/API version and project-local manifest hash. Unknown or
ambiguous fields remain `null`, and a requested profile never substitutes for observed effective
identity.

## Common requirements

Before inference, derive an opaque quota-domain id locally from a provider-owned stable account or
billing subject plus a machine-local salt. Never put the raw subject, salt, credential, prompt, or
transcript in a request, broker database intended for sharing, or doctrine. Different accounts get
different quota domains. The same account across desktop, CLI, project, and model surfaces gets one
domain unless provider evidence proves separate allowance pools.

Each adapter must produce:

- a fresh capacity snapshot with source-artifact digest and every relevant rolling window;
- exact requested provider/model/effort/transport and observed effective model/effort when exposed;
- total input, cached-input subset, output, reasoning, peak-context, turns, and wall time when
  observable;
- one typed terminal plus a compact evidence digest;
- a bounded launch configuration that enforces the broker's wall, turn, and context ceilings.

Cache tokens are not “free.” They can reduce price or a specific rate meter while still showing a
large retained context and repeated processing. Preserve native fields in local evidence, normalize
their meaning explicitly, and never infer one provider's quota formula from another's.

## Anthropic / Claude

Use structured Claude Code session events or API usage fields. Deduplicate repeated snapshots by
native message id. Anthropic defines total input as `input_tokens + cache_creation_input_tokens +
cache_read_input_tokens`; the normalizer records that total and records cache reads as a subset.
Capture `output_tokens_details.thinking_tokens` when present. See Anthropic's official
[rate-limit field definitions](https://platform.claude.com/docs/en/api/rate-limits),
[effort behavior](https://platform.claude.com/docs/en/build-with-claude/effort), and
[task-budget guidance](https://platform.claude.com/docs/en/build-with-claude/task-budgets).

The exact provider refusal family “reached ... session limit” is `QUOTA_BLOCKED`, not a generic
error and not lane death. Record the bounded native reset hint; convert it to `reset_at` only when a
provider-owned machine timestamp or separately verified parser makes the conversion unambiguous.
`max` effort is never a default policy: Anthropic describes it as unconstrained maximum capability,
and effort affects response text, thinking, tool calls, and arguments. Retained context should be
checkpointed into a compact fresh slice before it approaches its budget.

## OpenAI / Codex

Read response/session token events and retain input, cached input, output, reasoning output, model,
context, and turn totals. A cumulative total is sampled once at terminal rather than summed at every
update. Set reasoning effort intentionally; `max` requires measured benefit over `xhigh`, and any
move to a lower effort or a Sol/Terra/Luna profile requires the existing role-cell non-inferiority
gate. OpenAI's official [model guidance](https://developers.openai.com/api/docs/guides/latest-model)
also recommends a relevant tool surface, lean prompts, explicit prompt caching where appropriate,
and programmatic tool calling for bounded filtering, joining, deduplication, and aggregation.

Those deterministic reductions are appropriate before inference. Judgment, approval, independent
review, and final validation remain direct, project-authorized model work.

## Moonshot / Kimi Code

Read the agent `wire.jsonl` usage stream and count one native `usage.record` per turn, not duplicated
step summaries. Pin the exact model alias, resolved model, effort behavior, context limits, and
background configuration. Kimi documents that print-mode steering, background waits, background
task timeouts, and subagent timeouts can be effectively unbounded unless configured; explicitly cap
`print_max_turns`, `print_wait_ceiling_s`, task timeouts, `max_running_tasks`, and AgentSwarm
concurrency. See the official [configuration reference](https://moonshotai.github.io/kimi-code/en/configuration/config-files)
and [subagent resource-cost guidance](https://moonshotai.github.io/kimi-code/en/customization/agents.html).

Subagent contexts are isolated but each independently consumes tokens. Isolation is a quality and
context-management feature, not a quota exemption. Model-free registration and liveness paths must
not spawn a Kimi turn.

## xAI / Grok

Read the latest cumulative `turn_completed` usage rather than summing snapshots. Preserve prompt,
cached-prompt, completion, reasoning, model-call, and turn fields when exposed. Set the native
`max_turns` ceiling; xAI defines a turn as one agentic reasoning/tool iteration and exposes separate
reasoning and cached-prompt token fields in its official
[tool-usage documentation](https://docs.x.ai/developers/tools/tool-usage-details). Set
`reasoning_effort` only to a profile already qualified for the role; see xAI's
[reasoning guide](https://docs.x.ai/developers/model-capabilities/text/reasoning).

Keep a stable conversation/cache key for a bounded slice when safe, but start a fresh capsule when
context growth crosses the project budget. Cache-hit telemetry is efficiency evidence, never
completion or correctness evidence.

## Future providers

A new provider adds a normalized adapter and fixtures, not a new authority branch. If it cannot
prove a fresh capacity observation, bounded agent loop, effective profile, and terminal receipt, it
remains `UNEVALUABLE` and contributes no routed capacity. Installation or authentication alone is
not admission.
