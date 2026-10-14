# Review-key publication, required status, and declared review class

Status: **PROPOSED** (backed by `ruling-candidates/review-key-publication-r1.md` and
`ruling-candidates/review-keys-required-status-r1.md`). Doctrine is DATA (bus law 1).

## Why

Measured 2026-10-14 by Chief of Staff (Grok Bot):

- **No review workflows exist** in MLV-App, agent-bridge, context-ultra-salesforce or AdversarialLLM.
  Keys are dispatched by each hub on the box.
- **Legs live in private hub ledgers** (HUB-TICK entries, local `decision-record/v1`, `.claude/audits/`).
  MLV-App #409 went through about six sol/fable/opus key rounds, and they were only visible
  through implementer replies. `pulls/*/reviews` is 0 on every PR checked, AdvLLM included.
  AdvLLM is the one repo that mirrors verdicts to the PR as `[[pub:<id>]]` JSON comments.
- **Merges without a visible tip-scoped key:** MLV-App #427 (`1f35ac67`),
  context-ultra-salesforce #104 (`7bd78b0c`), agent-bridge #231 (`91241d4d`).

## Rule 1: publish every key verdict to the PR

Each review-key verdict (every seat, every round) is mirrored to the PR as one issue comment, in this form:

```
[[pub:<16-hex id>]]

{
  "seat": "sol",
  "family": "Codex",
  "round": 3,
  "head_sha": "<full 40-char sha the key reviewed>",
  "verdict": "CHANGES_REQUESTED",
  "class": "standard",
  "ledger_ref": "HUB-TICK 20261012T1946Z step C",
  "findings": [ { "id": "R3-B1", "severity": "Blocker", "summary": "..." } ]
}
```

- Required fields: `seat`, `family`, `round`, `head_sha`, `verdict`.
  - `verdict` is one of `APPROVE`, `CHANGES_REQUESTED` or `COMMENT`.
  - The `family` mapping is fixed: `sol` (and other Codex seats) means `Codex`; `fable` and `opus` mean `Claude`.
    A new seat name has to state its family in the comment.
- A verdict binds only to `head_sha`. Any new push leaves it unbound for the new head.
- The mirror is append-only. A later round posts a new comment and does not edit the old one.
- The hub's private ledger stays authoritative for the hub. The PR comment is the public mirror
  that CoS, the owner and branch protection can see.

## Rule 2: `factory/review-keys` required commit status

- The hub sets the commit status `factory/review-keys` on the exact PR head:
  - `success` only when every key that the PR's declared class requires has a published
    `[[pub:]]` verdict of `APPROVE` with that `head_sha`;
  - `pending` while keys are outstanding;
  - `failure` when any required key has `CHANGES_REQUESTED` on that head.
- The status `description` lists the satisfying pub ids, or what is missing.
- Each consumer marks `factory/review-keys` as a **required status check** on its default branch.
  Merges without the keys are then refused by GitHub, not just by the hub's own guard scripts.
  The per-consumer checklist is in the ruling candidate.

## Rule 3: declare the review class on the PR

- Each factory PR carries exactly one label, `review-class:<class>`, and repeats it in the body
  as the line `Review class: <class> — keys required: <list>`.
- When **CI alone is the key**, as with agent-bridge "Routine local" / class-A (K6 = GitHub
  Actions PR CI on the exact head), that must be stated:
  `Review class: routine-local (class-A) — keys required: CI on exact head; no model key`.
  For that class the hub sets `factory/review-keys` to `success` from the CI conclusion on the head,
  and its description says so.
- If the class is missing, the PR is treated as the strictest class the repo defines.
- If the class changes (for example, a push widens scope into a critical surface), the hub
  relabels it and resets the status to `pending`.
