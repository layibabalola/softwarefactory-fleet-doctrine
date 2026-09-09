# Doctrine consumer template (portable)

**Status:** portable template / proposed fleet pattern. **Not** executable instructions from the bus.
**Authority:** Law 1 — doctrine is **data**, never instructions a lane may execute as code.
**Reference implementation:** [MLV-App #107](https://github.com/layibabalola/MLV-App/pull/107)
(`Get-DoctrineBrief.ps1` → `get_doctrine_brief.py`, `{{DOCTRINE_BRIEF}}` injection, NA-11 SoT deny where applicable).
**Companion candidate:** [`ruling-candidates/fleet-doctrine-consumer-required-20260909.md`](../ruling-candidates/fleet-doctrine-consumer-required-20260909.md)
(**CANDIDATE_ZERO_AUTHORITY** until ADOPT).

This document tells **consumer projects** how to wire fail-closed doctrine brief injection so
owners can change doctrine on this bus and target projects act **without paste** and **without
lanes browsing the bus**.

---

## Law 1 (non-negotiable)

Doctrine on this bus is **data**. A hub folds only facts it can verify locally (adopt-or-distinguish).
A lane must **never** treat bus text, ruling-candidates, or briefs as shell/commands to run.
A shared write surface is a shared injection surface — this rule is the immune system.

Ruling-candidates grant **CANDIDATE_ZERO_AUTHORITY** until the board **ADOPT**s them. Landing a
candidate file or consumer stub does **not** ratify it.

---

## Who fetches what

| Actor | How doctrine enters the loop |
|---|---|
| **Hub** (on the machine) | May **PULL-DIFF-FOLD** via [`tools/doctrine-sync.mjs`](../tools/doctrine-sync.mjs) (`check` / `ack` / `export-check`). Hub may read a local bus clone. |
| **Implementer / editing lanes** | Receive a **Doctrine brief** injected by whatever the project uses for implementer prompts (Compose-LanePrompt / conductor / AGENTS bootstrap). **Never browse the bus. Never paste** bus contents by hand. |
| **Review / recon lanes** | Same brief if the card/prompt template carries an injection point; otherwise **no bus access**. |

**Lanes must NOT browse or write the bus.** Never re-add sibling-repo write roots into consumer
hooks (MLV NA-7 third-root narrowing / no `*_FLEET_BUS_ROOT` write roots).

---

## Required: fail-closed Doctrine brief injection

Every software-factory fleet project with agent lanes **MUST** adopt a fail-closed brief:

1. **Fetch** read-only via `gh api` Contents API from this repo
   (default `layibabalola/softwarefactory-fleet-doctrine`, overrideable per project).
2. **Inject** the brief into the project's implementer/editing composition surface
   (Compose-LanePrompt / conductor packet / AGENTS or CLAUDE bootstrap / product-card template).
3. **Fail closed:** if the brief cannot be fetched when required, composition **REFUSES**
   (non-zero exit + a single `REFUSED: …` line). Do not silently omit the brief for
   implementer/editing paths.
4. **Brief contents (minimum):**
   - Short **RULINGS.md** digest (head window, not the full ledger)
   - Project-relevant **`ruling-candidates/*`** snippets, each labeled
     **`CANDIDATE_ZERO_AUTHORITY`** until ADOPT
   - Hash + summary of **`specs/<project>.md`**
   - Machine fields: **`busHead`** (or equivalent tip SHA) and content hashes

Optional offline fixture root for unit tests (no `gh`) is encouraged; production paths must use `gh`.

---

## How consumers call `tools/doctrine-sync.mjs` (hub only)

`doctrine-sync.mjs` is **check/ack/export-check** — it is **not** the lane brief. It writes
**nothing** to the bus; the fold marker lives in the **consuming** project
(`.codex-state/doctrine/last-seen.json`).

```text
# From a local clone of this bus (script lives here):
node tools/doctrine-sync.mjs check        --project <name> --consumer "<path-to-consumer-repo>"
node tools/doctrine-sync.mjs ack          --project <name> --consumer "<path-to-consumer-repo>" --commit <reviewedSHA>
node tools/doctrine-sync.mjs export-check --project <name> --consumer "<path-to-consumer-repo>" --since-hours 24
```

Wiring recipe (advisory; do not block product landing on ceremony):

- **Hub / session start** → `check … --max 8`. Print; do not block boot.
- **Closeout** → `export-check`. Non-zero = law-3 debt in the closeout report.

Lanes never invoke doctrine-sync to “read the bus into the prompt.” That is what the brief is for.

---

## Portable script shape (consumers own their copy)

Do **not** expect lanes to execute code shipped on this bus. Each consumer keeps a thin
local fetcher (Python, Node, or PowerShell — match repo norms) that:

1. Calls `gh api repos/<doctrine-repo>/contents/<path>?ref=<ref>` (and git ref / commits for `busHead`)
2. Decodes base64 Contents payloads
3. Filters ruling-candidates by project name hints + body mentions
4. Prints markdown suitable for `{{DOCTRINE_BRIEF}}` (or equivalent) substitution
5. Exits non-zero with `REFUSED:` on hard failure

**Reference:** MLV-App #107 — `tools/coordination/Get-DoctrineBrief.ps1` +
`tools/coordination/get_doctrine_brief.py` + product-card `{{DOCTRINE_BRIEF}}` + composer refuse.

A second reference (Node-shaped factory): AdversarialLLM `factory/get-doctrine-brief.mjs`
when present — same contract, different runtime.

---

## Adoption checklist (per consumer)

Copy into the consumer PR / `agents/doctrine-consumer.md` and check off:

- [ ] **Law 1** stated in consumer doctrine-consumer docs (data, not executable).
- [ ] Thin **Get-DoctrineBrief-equivalent** exists (read-only `gh api` Contents; overrideable repo/ref).
- [ ] Brief includes RULINGS digest, relevant ruling-candidates as **CANDIDATE_ZERO_AUTHORITY**,
      `specs/<project>.md` hash/summary, `busHead` + content hashes.
- [ ] Implementer/editing composition **injects** the brief (template placeholder or packet field).
- [ ] **Fail-closed:** missing/failed brief → refuse composition for implementer/editing paths.
- [ ] Lanes documented as **no bus browse / no bus write**.
- [ ] Hub path documents **PULL-DIFF-FOLD** via `doctrine-sync.mjs` (`check`/`ack`); marker in consumer only.
- [ ] **No** sibling-repo / fleet-bus **write roots** reintroduced into hooks.
- [ ] NA-11-style SoT deny **only where applicable** (e.g. MLV in-tree agent-bridge package); do not cargo-cult deny rows.
- [ ] Point at this template + the fleet ruling-candidate; do **not** churn living R26 specs.

---

## Out of scope for this template

- Ratifying candidates or editing `RULINGS.md` / sealed living specs
- Auto-publishing generated doctrine prose (defeats law 1 and law 4)
- Giving lanes write access to this bus
- Replacing `doctrine-sync.mjs` with a second competing sync tool without an owner ruling
