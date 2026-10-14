# Ruling candidate: `factory/review-keys` is a required commit status on every consumer R1

Status: **PROPOSED ONLY — NOT YET A RATIFIED RULING OR PROJECT RUNTIME AUTHORITY.** Doctrine is
DATA (bus law 1). This file changes no branch protection. Each repo's owner or hub does the wiring.

**Measuring party:** Chief of Staff (Grok Bot), 2026-10-14, filed at the owner's request.
**Spec:** `docs/review-key-publication.md` Rule 2.

## Why

Hub guard scripts (for example agent-bridge `Hub-GuardedMerge.ps1`) are the only thing enforcing keys,
and merges outside them went through: MLV-App #427 (`1f35ac67`), context-ultra-salesforce #104
(`7bd78b0c`), agent-bridge #231 (`91241d4d`). GitHub did not refuse any of them, because no check requires keys.

## Proposed ruling

- The hub posts the commit status `factory/review-keys` on the exact PR head:
  `success` only once every key its declared class requires has an `APPROVE` `[[pub:]]` verdict on that head
  (for a CI-only class, once CI succeeds on that head).
- Each consumer adds `factory/review-keys` to its default branch's required status checks.
- A new push leaves the status absent on the new head until the hub sets it again, so stale keys never satisfy it.

## Per-consumer wiring checklist

For each of MLV-App, agent-bridge, context-ultra-salesforce, AdversarialLLM, dng-auto-processor,
cloudvore, airmypc, adobe-ingester (and any later consumer):

- [ ] The hub can post commit statuses (a token with `repo:status` only; nothing broader).
- [ ] The hub publishes `[[pub:]]` verdicts (Rule 1) and the `review-class:*` label and body line (Rule 3).
- [ ] The hub sets `factory/review-keys` on every head push and every new key verdict.
- [ ] The required-key set per class is written in the repo's `CLAUDE.md` / `AGENTS.md` (or its dispatch policy).
- [ ] Dry run: one PR shows `pending`, then `success`, before protection is turned on.
- [ ] Owner adds `factory/review-keys` as a required check on the default branch.
- [ ] Hub replies on the doctrine PR with `ACK: <plan or ETA>`, or `DISTINGUISH: <reason>`.
