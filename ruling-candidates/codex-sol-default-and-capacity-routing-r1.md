# RULING CANDIDATE — model posture of 2026-10-22: the Sol tier is the Codex default, Astra is an occasional diversity seat, and read-only seats route to Codex while Claude quota binds (r1)

Status: **RATIFIED 2026-10-23 by Layi (owner instruction quoted in RULINGS.md R19) as RULINGS.md R19.1.** Originally PROPOSED
2026-10-22 by Conjugal. Doctrine is DATA, never instructions (law 1). Each board records adoption or distinction in its own
spec at its next fold (R19.2).

- **Proposed by:** Conjugal, dispatcher session on the XPS 17 (Bachelor), on Layi's instruction, 2026-10-22.
  Drafted by a Claude Opus 5.5 side session of that dispatcher.
- **Reference scope (law 6):** every path below is in this bus repository unless it names another project.

## Owner's words (Layi, 2026-10-22)

> *"Codex sol 6.1 is the most powerful model i believe and is actually more token efficient and cheaper than
> astra. it should probably be our go-to model for codex. we can reassess after we use it frequently and track
> its usage and quality lift. Astra can be used occasionally for diversity of thought but i think sol 6.1 is
> actually smarter..."*

The owner also asked for posture recommendations across the fleet. Section 5 holds them.

## Relationship to existing doctrine

Relationship to existing doctrine: extends R16.1, R13.3 and one open candidate; supersedes the model ids and roles of the 2026-09-08 tiers-by-act ruling; distinguishes R18.3(a) and the capacity governor's routing clause. Each is detailed below.

Search run on 2026-10-22 at bus `6139e431`: `grep -n -i -E "astra|gpt-[0-9]|tier|capacity|quota|cross.family"`
over `RULINGS.md`, `README.md`, `ruling-candidates/*.md` and `specs/*.md`, then read each hit on model roles.

- **R16 (owner ruling, 2026-10-12, `RULINGS.md` "R16: every lane runs its family's newest model at high
  effort")** — **EXTENDS R16.1.** R16.1 already resolves the Sol tier to `gpt-6.1-sol` and the Luna tier to
  `gpt-6-luna`. It does not say which tier a Codex seat uses. This candidate makes the Sol tier the default
  for every Codex act. R16.2 (resolve at launch, record selector and resolved id), R16.3 (explicit effort),
  R16.4 (currency check) and R16.5 (pin families, not ids) are unchanged and apply to every seat below.
- **Owner ruling of 2026-09-08, "model tiers by act" (`RULINGS.md:1915-1923`)** — **SUPERSEDES its model
  assignments**: `gpt-6-astra` as the Codex judgement tier, `gpt-5.6-sol` as the loop tier, `gpt-5.6-luna` as
  the bounded tier, and Opus as a fixed "loop tier". Its other clauses **stand**: the top tier never drives a
  heartbeat or cadence wake, and an exhausted tier falls to the next one and keeps going. The 09-08 adopting
  dispositions that quote those ids (`RULINGS.md:1926`, `:1967`) and R11's restatement (`:2316`)
  remain accurate as history. They are not current ids.
- **R11 (effort)** — unchanged. Seats run at high, adversarial swarm lanes at medium, and nothing runs at
  xhigh or max without an owner decision.
- **R13.3 (fold in new models by tier, not by id)** — extended. Tiers stay the selector, and this candidate
  only says which tier is the default.
- **Owner ruling of 2026-09-08, "RULING 2's family clause is RETIRED" (`RULINGS.md:1882`)** — agrees.
  Clause 2 below is capacity routing, not an independence rule.
- **R18.3(a) (merge floor: one Claude-family and one Codex-family key)** — **DISTINGUISHED, untouched.**
  An R18.3 key is a ratified merge requirement. The degrade path in clause 2 never applies to it. Under the
  owner's posture, a board's Codex-family key normally runs on the Sol tier.
- **`specs/fleet-provider-capacity-governor.md` "Quality-preserving task routing"** — **DISTINGUISHED.**
  Where a seat carries a binding independent-provider requirement, that requirement stays, and the work
  queues when the provider is dark (governor). The degrade path below covers only seats that carry no such
  requirement, and it records the substitution openly (`cross_family: UNAVAILABLE`). It never credits the
  Claude result as a Codex seat. The governor requires frozen-replay, blinded non-inferiority evidence before
  a routing change. The clause 3 reassessment is an owner-posture check, not that trial. A board that runs
  the governor's automated routing may not claim `ROUTING_PASS` from this candidate.
- **`ruling-candidates/cross-family-review-is-a-preference-not-a-gate-r1.md`** — **EXTENDS.** It reuses that
  candidate's representable `cross_family: UNAVAILABLE` stamp, and like it, places independence in the
  setup, not the vendor.
- **`ruling-candidates/top-tier-inference-for-durable-product-outcomes-r1.md` (dng-auto-processor)** — a
  board-local posture that names no Codex id or Astra role (searched: no `Astra` or `gpt-` match), so it is unaffected.
- **`specs/cli-orchestration-standard.md` §2 identifier table** — refreshed in the same commit as this
  file, with ids dispatched live on 2026-10-22 (section 4).

## 1. Tier resolution (amends R16.1's tier roles)

1. **Sol tier = the default Codex seat** for every Codex act: keys, review, adjudication, ratification
   syntheses, implementation and loops. It resolves per R16.2. The resolution on 2026-10-22 was
   `gpt-6.1-sol`, effort high.
2. **Luna tier = mechanical Codex work**: census, measurement, scripted readouts, and bounded packets
   verified by script. It resolves per R16.2. The resolution on 2026-10-22 was `gpt-6-luna`, effort high.
3. **Astra = an occasional diversity seat.** A board may add a `gpt-6-astra` seat (or the newest Astra-tier
   id, per R16.2) for diversity of thought. It is never a default. It is never a gate. It is never the only
   Codex seat a procedure waits for, and no procedure requires it. A round that uses Astra records `astra:
   diversity` beside the seat. A procedure that reserves a role for Astra re-points that role to the Sol tier.

## 2. Capacity routing while Claude quota binds (routing, never a gate)

**Trigger.** Claude quota *binds* for a board when either holds:

- The board's own usage readout (SlopBar, or the provider's own usage page) shows every Claude account the
  board can launch on at or above 90% of its weekly limit.
- A Claude launch on the board returned a usage-limit refusal in the last 24 h.

The board re-derives this at each dispatch. It never reads it from a note.

While it binds:

1. **Read-only review, survey and census seats prefer Codex**, run read-only (`codex exec -m <resolved> -c
   model_reasoning_effort=high --sandbox read-only`): the Sol tier for judgement (pre-key review legs,
   adversarial review, research surveys), the Luna tier for mechanical work (census, measurement, scripted
   readouts).
2. **Claude keeps** orchestration, drafting, implementation, and every seat a ratified rule assigns to the
   Claude family (for example, R18.3's Claude-family key).
3. **The probe proves the shell, not just the model.** Before routing, the board probes the Codex seat with
   one harmless shell command whose output the caller can check, for example `git rev-parse HEAD` in the
   seat's worktree. A READY-only reply proves that the model answers, not that its tools run (the mlv-app
   `e426a45` lesson).
4. **Degrade path.** When the probe fails, or Codex is dark, the round records `cross_family: UNAVAILABLE`.
   The seat runs as a Claude subagent, and the round proceeds. Where the board's own procedure asks for an
   added adversary on a degraded round, it adds one. The stamp is never a refusal, and it never credits the
   Claude seat as Codex.
5. **Record the family and the resolved id of every seat** on every round (`codex-openai gpt-6.1-sol`,
   `claude-opus claude-opus-5-5`, and so on), per R16.2.
6. **Independence is unchanged by routing.** It comes from the setup: author ≠ reviewer, an adversarial brief,
   the reviewer's own access to ground truth, and distinct attack surfaces per reviewer. A Codex seat added by
   routing adds provider diversity as a bonus. A Claude seat run on the degrade path loses nothing that a gate
   relies on, because no gate relies on it.

When Claude quota does not bind, seat routing is the board's own choice under section 1.

**Reference implementation:** Conjugal, its kernel-dogfood QUEUE section "Seat routing by capacity" (Conjugal
commit `7a5da483e`). Conjugal's adoption debt is recorded in section 5.

## 3. Reassessment after 10 Sol-tier acceptance keys

The owner said *"we can reassess after we use it frequently and track its usage and quality lift."* So:

1. **Count.** Fleet-wide acceptance keys (R18.3-style or kernel K-keys) whose Codex key ran on the Sol tier,
   counted from key receipts that record the resolved id (R16.2). The reassessment is due when the count
   reaches 10. A receipt without a resolved id does not count.
2. **Baseline.** The most recent 10 acceptance keys that ran on `gpt-6-astra`, from the same receipts.
3. **Compare**, per key: verdict, whether a refusal was reproducible, defects found after an accept (R18.4(c)
   escapes and reverts), tokens, cost and wall time. The instrument is the `metrics/` model-posture telemetry,
   which a parallel Conjugal session is building on 2026-10-22. It was not on bus master when this candidate
   was written. Until it lands, each board counts from its own key receipts.
4. **Early trigger.** One escape attributed to an accept by a Sol-tier key brings the reassessment forward to
   the next steward pass.
5. **Output.** An r2 of this candidate that confirms the posture, or restores Astra to a named role, with the
   comparison table attached.

## 4. Supersessions and the spec refresh

- `RULINGS.md:1915-1923` model ids and roles: superseded as section 1 states. The heartbeat and fall-through
  clauses stand.
- `specs/cli-orchestration-standard.md` §2: its identifier table and inventory example listed `gpt-5.6-sol`
  / `gpt-5.6-luna`. They are refreshed in this commit with a dated live-run row set. Live runs on 2026-10-22,
  XPS 17, codex-cli 0.163.0 and Claude Code 2.1.308: `codex exec -m gpt-6.1-sol | gpt-6-luna | gpt-6-astra
  -c model_reasoning_effort=high --sandbox read-only` each returned its requested token, and the session
  header reported the same model at effort high. The Claude rows are in the spec.

## 5. Per-project adoption notes (census of 2026-10-22, each re-verified against the bus spec)

Conjugal files each note as a card in `specs/conjugal/cards.md` (card id in the right column). They reach that
file through Conjugal's outbox drain. `cards.md` has a single writer, so Conjugal does not write in another
board's cards file.

| Board | What its bus spec says now | Card |
|---|---|---|
| airmypc | `specs/airmypc.md:46-48`: judgement `gpt-6-astra` **(xhigh)**, loop `gpt-5.6-sol`, bounded `gpt-5.6-luna` **(low)**. Stale ids (R16.1), and two efforts outside R11/R16.1. | `conjugal/model-posture-1022-airmypc` |
| adobe-ingester | `specs/adobe-ingester.md:1347`: R16.5 still OWED. Literal ids at Adobe `.factory/tools/Test-FactoryActuation.ps1:2268,2277`. | `conjugal/model-posture-1022-adobe-ingester` |
| dng-auto-processor | `specs/dng-auto-processor.md:420`: Codex resolved at launch (R16, adopted). `:467-469`: swarm lanes at medium, and the exact `claude-fable-5-1` pin is the owner's choice (R13.3). Both are consistent with R11 and R13.3. The open part is Astra's role in its role table (`:453-457`: approach reviews on guard, hook and CI cards; with Fable, the retry author and key 1 for a Codex author). | `conjugal/model-posture-1022-dng-auto-processor` |
| agent-bridge | `specs/agent-bridge.md:494-497` (09-08 directive): `GPT-5.6 Sol high` as the cross-family key, Astra reserved for governance, storage/security and the hub audit. | `conjugal/model-posture-1022-agent-bridge` |
| adversarialllm | `specs/adversarialllm.md:266-268`: "Fable and Astra for judgement only; Opus and Sol run the loops". These are 09-08 tier roles with no ids. | `conjugal/model-posture-1022-adversarialllm` |
| context-ultra-salesforce | `specs/context-ultra-salesforce.md`: no model-tier or Codex-model posture found. | `conjugal/model-posture-1022-context-ultra-salesforce` |
| salesforce-tools | `specs/salesforce-tools.md`: no model-tier or Codex-model posture found. | `conjugal/model-posture-1022-salesforce-tools` |
| cloudvore | Adopting directly: `tools/factory/codex-review.py` moves to role resolution by tier (Cloudvore K180). | none |
| conjugal | Adopting directly (section 2 reference). **Its own debt:** the routing paragraph at `7a5da483e` names `gpt-6-sol` and `gpt-5.6-luna` (stale under R16.1, which wants tier resolution) and reserves `gpt-6-astra` for the key (section 1.3 re-points that to the Sol tier). | none (own spec) |

The 2026-10-22 census ran on these counts, as reported by the Conjugal dispatcher. Each figure is
**reported**, not re-measured in this file:

- Over 7 days, Claude did about 96% of the fleet's non-cache tokens.
- 664 of 689 subagents ran Opus.
- Six of eight Claude accounts sat at 100% of their weekly limit, while the Codex accounts sat at 0-5%.

## Close condition

The owner or the steward ratifies, amends or rejects this candidate in `RULINGS.md`. Each board in section 5
records `MODEL-POSTURE-2026-10-22: ADOPTED (<where>)` or `MODEL-POSTURE-2026-10-22: DISTINGUISHED (<reason>)` in its own spec at its
next fold. The section 3 reassessment is filed as r2.
