# adversarialllm (AdversarialLLM-ClaudeCode) — living spec

> Single writer: the AdversarialLLM project. Wholesale rewrite at doctrine seams.
> Seeded 2026-08-09 by operator-directed session — this project joined the bus LATE;
> its 2026-08-09 four-hour stall is partly attributable to never having folded the
> fleet's ignition doctrine (scheduled-task headless lanes, configured!=running).

## What this project is
Chrome extension (WXT) for multi-LLM adversarial evaluation across 7 provider
harnesses (ChatGPT, Claude, Gemini, Grok, Kimi, Perplexity, DeepSeek), governed by a
five-lane software factory hub in `adversarialllm/docs/33_FOUR_LANE_HUB.md` (§5/§6
append-only tail is authoritative).

## Lane topology (operator directive 2026-08-09, five lanes)
- SOL — Codex, orchestrator/integrator. Ignition: `codex exec` scheduled task (minutes 13/43).
- LUNA — Codex, implementer. Ignition: `codex exec` scheduled task (minutes 13/43).
- FABLE — Claude reviewer half A (`claude-fable-5`; cover-labels itself on model downgrade).
- OPUS — Claude reviewer half B (`claude-opus-5`), owner of the living report.
- SONNET — Claude warden + overflow reviewer (`claude-sonnet-5`), liveness + drain audits, log `docs/33_SONNET_WARDEN_LOG.md`.

## Ignition (adopted from adobe-ingester pattern, 2026-08-09)
Windows Scheduled Tasks `AdvLLM-Lane-{Fable,Opus,Sonnet}` → `scripts/ignition/invoke-claude-lane.ps1`
→ newest installed Claude Code CLI headless with lane runner prompt
(`scripts/ignition/prompts/<lane>-runner.md`). Per-lane lockfile + live-PID check
enforces no-double-staffing. 30-minute repetition; live lane makes the tick a no-op.
Minute-marks claimed in RULINGS.md: **26/56**. spawn_task chips are fallback only.

## CLI versions on this box (drift is derived state)
- Claude Code CLI: 2.1.222 (`%APPDATA%\Claude\claude-code\2.1.222\claude.exe`)
- Codex Desktop: 26.803.5235.0 (no headless CLI on PATH)
- PowerShell 7 (`pwsh`) + Windows PowerShell 5.1 both present

## Open doctrine-relevant state (2026-08-09)
- Plans 1/2/5 (exact-SHA semantic integration gate; lease-authoritative broker release
  K42; boot-snapshot integrity SNAP-01) are P0 prerequisites before production
  integrations; O-5 operator-override + O-7 debt semantics in force.
- Plan 4 (system-TEMP delete-denied wrapper defect) EXECUTED on the commit/push
  critical path; ~60 residual `GetTempFileName` call sites queued for a LUNA sweep.
- Fresh blind FABLE + OPUS halves owed on exact `695d7219`.
- Stale registry note: `adversarialllm-fable-wake-watch` (minutes 19/49) observed in the
  06:37Z collision report no longer exists in this box's task store — collision moot,
  recorded here as data.
