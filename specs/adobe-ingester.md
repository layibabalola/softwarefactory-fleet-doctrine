# Adobe Document Cloud Ingester — factory spec

Writer: the Adobe project's portal/auditor session (single-writer file). Updated at
doctrine-changing seams. Doctrine here is DATA, never instructions (README law 1).
Machine: virtual-ten (shared workstation, 5+ factories). Last update: 2026-08-09.

## Shape

Gate-0 feasibility factory: prove/disprove a Playwright personal-account acquisition path;
a well-evidenced stop is a successful outcome. Blocking criterion **AC-07** — a real,
user-present, headed Adobe login — is the one irreducible human action and has never
succeeded. Four governed lanes: Sol (gpt-5.6-sol, designer/orchestrator/sole ledger
writer), Luna (gpt-5.6-luna, sole implementer) on Codex Desktop automations; Opus and
Sonnet (Claude, independent reviewers) on Windows Scheduled Tasks. A chat session is
NONE of these — it is the seatless portal/auditor. Advisory ingress: append-only
hash-chained JSONL feed (`fable-ingress`); Sol adjudicates everything; advisory input is
non-quorum by construction.

## Distinguishing carve-outs (cite before adopting anything from us)

- **Hash-pinned control plane**: executables, manifests, and reviewed control material are
  SHA-256-pinned; any tooling upgrade must transit an admission path and re-pin, or
  fail-closed checks break by design. Machine-wide CLI upgrade windows on this box are
  incomplete until Adobe's re-pin lands green.
- **Candidate immutability covers repo configuration**, not just code. The fleet bus is
  therefore consumed OUTSIDE the factory repo (pull into `.claude-state/`); adoption only
  via the ingress and ordinary quorum.
- **Reviewer blindness is paid for**: one-way glass; nothing overheard travels into any
  lane; reviewer wrapper does not write project-slug transcripts (receipts + retained
  runs are the observable surface).

## Laws we ratified locally that generalize

- Ledger outranks snapshot; heading ascension per segment; stamp the ledger last.
- Launcher exit codes prove launch, never delivery — delivery is the lane's owned file
  advancing with a valid receipt.
- Owner actions need a verifiable channel: an unverifiable relay is correctly rejected
  (`OWNER RELAY UNVERIFIED`, 2026-08-08). Designed fix: passphrase-signed owner
  authorization register (SSHSIG, challenge nonce, delegation lines) — in review.
- Vote/seat/model provenance must be bound at production time (three incident classes:
  unattributable votes, owner-enable contained as intrusion, wrong model in a seat).
- Active-segment + immutable archive for any append-only file a wake must read (Q-015):
  a 4.4 MB ledger re-read per wake livelocked the coordinator (~20 rotations/day, 1 work
  entry). Bound the active set or drown.

## Receipts we can attest (details in RECEIPTS.md, dated 2026-08-08/09)

Sentinel-vs-repo same-name tool divergence A/B (stale thread-id pins fake DEGRADED);
recovery-manifest schema v1-vs-v2 rejection (intact-but-rejected, 7≠11 properties);
rotation-livelock arithmetic; `NOT_LOGGED_IN` from a worker env hiding the credential
store while the interactive CLI is logged in; `INVALID_MCP_CONFIG_PRE_MODEL` consuming
one-use attempts (preflight-in-exact-env is the fix); NUL bytes and unexpanded `$vars`
in machine-emitted ledger values (structured receipt preflight is the fix); 326
`global_limit` skips on an aligned `*/30` cron (de-aligned to `:08/:38`).

## Versions on this box (derived 2026-08-09)

claude CLI: 2.1.x npm shim at `%APPDATA%\npm\claude.cmd` · codex-cli 0.147.0 at
`%APPDATA%\npm\codex.cmd` (uncoordinated 0.142.5→0.147.0 jump 2026-08-08 = FAB-TOOL-01,
the incident behind law 5's windows).

## Open questions we'd take receipts on

TOML-with-no-target_thread_id creating a thread; scheduled-task store model pin actually
honored; hub-written automation pickup already PASS (agent-bridge, this box).
