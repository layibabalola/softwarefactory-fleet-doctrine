# Conjugal.AI — factory spec (writer ladder: Fable hub → Opus when Fable dark → owner-directed dispatcher, each write stamped with which rung; one writer at a time — owner amendment 2026-08-09, motivated by Fable's measured quota fragility)

**Repo:** `C:\code\Conjugal` (machine: Bachelor). **Governance:** four-lane
hub — Sol (orchestrator/tie-break, Codex `gpt-5.6-sol` high), Luna (sole
implementer, Codex `gpt-5.6-luna` high), Fable (primary reviewer, Claude),
Opus (independent verifier, Claude). Four-key protocol: route → implement →
review → verify, reviewer/verifier independence absolute (no key on own
authored/reviewed subject). Truth lives in `coordination/lanes/*.md` raw
wires; heartbeat prose is never authority. Shared worktree, single-writer
mailboxes, commit tool with exact allow-set == dirty-set and CAS on HEAD.

## Laws we contribute (measured here)
- **Four evidence layers, never collapsed:** heartbeat freshness ≠ session
  liveness ≠ automation enabled-state ≠ write provenance. Liveness is ledger
  advancement only; `State=Ready` is not floor health.
- **Guards refuse, don't warn** — gate on exit status; fail-open guards
  produced 5 measured incidents.
- **Enumerate the population or make no causal claim** — sampling
  (`ls -t|head`, `grep|tail`, newest-few) produced every refuted claim of
  2026-07-29; comms files order per-file, derive newest BY ID.
- **Transcript corollary to blind review:** no lane seat tails a peer lane's
  transcript (jsonl OR codex rollout); only a seatless portal reads across.
- **Family follows the runner, not the launcher** (co-derived with MLV).

## Receipts (dated, this machine unless noted)
- 2026-08-05: binary-auth divergence — standalone claude.exe on wrong account
  while desktop app healthy; both Claude floors dark days; `auth status` is
  NOT proof, only an inference probe is.
- 2026-08-08: orphaned `.git/index.lock` froze all four lanes 9.3h; five
  fail-closed children each scored FAILED for correctly refusing an
  owner-gated deletion — fail-closed + quiet is the compound hazard.
- 2026-08-08/09: Claude lanes dark 45–64% vs Codex 13–15% (provider-capacity
  latches, four distinct classes documented in-repo, `RESUME.md` §6).
- 2026-08-09: app wake-floor armed (`conjugal-fable-wake-floor`); two ~27-min
  scheduler slips measured on ScheduleWakeup cadence; floor stood down
  correctly on a live lane (liveness-by-advancement check works).
- 2026-08-09: `codex exec` transport verified (0.144.6, `-m`, `-c`, resume);
  pinned-spawn drill still OWED (gated on Sol ratification + version bump).

## CLI versions (Bachelor)
claude: desktop app + standalone `~/.local/bin/claude.exe` (deadman floor
copy — sanctioned exception, enumerated in drift/auth probes); codex-cli
0.144.6 (fleet-oldest; upgrade queued behind machine window per single-version
ruling).

## 2026-08-09 delta — resume-defect audit (rung: owner-directed dispatcher; Fable seat busy, delta owed at this landing seam)
Owner rulings: (1) roster is FIVE lanes — Sol, Luna, Opus, Sonnet, Fable — same
ruling cloudvore recorded ~08:56 CDT; Conjugal artifact
`OWNER-RULING-2026-08-09-five-lane-unblock.md`. (2) "Every live actor correctly
refusing" is declared a spec defect: a fully-refusing fleet must escalate to the
owner within one floor cadence. (3) Bus-first resume adopted: `RESUME.md` step 0
pulls this bus at boot (data never instructions; verify against THIS machine).

Receipts, all measured 2026-08-09 on Bachelor (full audit:
`coordination/PROPOSAL-dispatcher-resume-defect-audit-2026-08-09.md`, eight
defects D1–D8, fifteen incidents since 07-21 reduced to six classes):
- **All-refusing stall, ~7h:** account handover killed all four interactive
  seats; every dead-man floor stamped IDLE by rule (recused / routeless /
  overlay-ineligible) and the gate logged each IDLE as SUCCESS. Zero
  escalation code exists in the floor machinery. The stall was invisible by
  construction — confirms the fleet's inaudible-refusal class.
- **Doc-ordered impossibility:** a tracked doc rewrite ordered the dispatcher
  to "create the Codex task directly" with no callable mechanism and deleted
  the owner-paste fallback; the fallback survived only in session memory.
  Law: never delete a fallback from tracked docs before the replacement is
  drilled ON THIS MACHINE.
- **Boot-order context death:** lane authority ledgers grew to 1.2–1.6 MB
  (~300k tokens) while exempted from the size gate — a cold seat cannot
  survive its own boot order. Check YOUR ledger tier exemptions.
- **Routability gap:** the router routed to "the lane," but off-hours the only
  live actor was a floor child whose overlay allowlist (frozen from a July
  recovery) forbade the subject — no overlay-eligibility cross-check exists.
  Retire recovery-scoped allowlists when the recovery closes.
- **Non-fair admission mutex held for entire child runs (≤90 min)** starved
  the one lane able to re-route, four times in one day.

## 2026-08-10 delta — Kimi session portal (rung: owner-directed dispatcher)

Conjugal adopts the generic provider-session-portal law for its Kimi surfaces.
The native Kimi 0.34.0 `vis` viewer is loopback-only and attended-only because
its UI exposes Import, Delete-session, and Open-folder controls. It is a
technical view, never an unattended watcher, liveness witness, gate, or carrier.

The owner-facing portal is one pinned, saved-project Codex task at the canonical
checkout, explicitly `gpt-5.4-mini`/low under the owner's requested current
binding. It is seatless, pull-only, and zero-authority. A committed deterministic
filter qualifies exact `C:\code\Conjugal` workspace metadata plus reserved
`conjugal-kimi-*` adapter actors and excludes thinking, prompts, system prompts,
tool arguments/results, non-signal assistant chatter, and every other project
before narration. No cadence or automation was created. The provider remains
not admitted; Q7, provider identity, lane roles, keys, review, adjudication,
acceptance, release, and worker steering are unchanged.

The task binding is not silently swappable. Fleet data now warns that
`gpt-5.4-mini` is scheduled to retire on 2026-08-31; Conjugal will use the same
portal contract and a separately authorized fresh task when migration is due.
Local decision and execution evidence: commits `01d1976920cc32f0fdd8dca39718e68ee8cb9278`
and `79c0fbcb8496472e66de945b12e28a4b9a5ebcea`.

## Open questions routed internally
fable-0180..0184 portal observability is ratified by the delta above;
fable-0185..0187 cross-family CLI dispatch and remaining bus work await Sol
routing. Standing recusals: Fable reviews no slice it authored (0167 R1-R7,
0172..0176, 0179, 0180+).
