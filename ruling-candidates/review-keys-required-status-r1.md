# Ruling candidate (R1): `factory/review-keys` is a required, verifier-computed check on every consumer

Status: **PROPOSED ONLY — NOT YET A RATIFIED RULING OR PROJECT RUNTIME AUTHORITY.** Doctrine is
DATA (bus law 1). This file changes no branch protection. Each repo's owner or hub does the wiring.

**Measuring party:** Chief of Staff (Grok Bot), 2026-10-14, filed at the owner's request.
**Spec:** `docs/review-key-publication.md` Rule 2.

## Why

Hub guard scripts (for example agent-bridge `Hub-GuardedMerge.ps1`) are the only thing enforcing keys,
and merges outside them went through: MLV-App #427 (`1f35ac67`), context-ultra-salesforce #104
(`7bd78b0c`), agent-bridge #231 (`91241d4d`). GitHub did not refuse any of them, because no check requires keys.

## Proposed ruling

- `factory/review-keys` is a GitHub Actions check computed by a verifier workflow from trusted pubs and the
  effective class (`docs/review-key-publication.md` Rules 1 to 3). Nobody posts the result directly.
- Each consumer requires that check **from the GitHub Actions app** on its default branch, so a status with the
  same name from any other poster never satisfies protection.
- On a new head the check reads `pending` (recomputed with no bound verdicts), except for a content-identical
  master sync, which carries its keys forward. This matches the spec.

## Per-consumer wiring checklist

Measured so far: MLV-App, agent-bridge, context-ultra-salesforce and AdversarialLLM. The other consumers
(dng-auto-processor, cloudvore, airmypc, adobe-ingester) are listed for completeness, and their review flow
hasn't been measured yet.

- [ ] Register the **hub identity** (a GitHub App, preferred, or a dedicated bot account) in `CLAUDE.md` / `AGENTS.md`.
      Implementer lanes never hold its credential.
- [ ] **Credentials, least privilege, split by job:**
      - hub identity: Pull requests read/write and Issues read/write (fine-grained), to post pub comments and set labels and body lines;
      - verifier: the workflow's own `GITHUB_TOKEN` with `checks: write`, `pull-requests: read` and `issues: read`. It needs no PAT.
      - Classic `repo:status` is not used; the check comes from Actions.
- [ ] Write the path and diff class rules in the repo's dispatch policy, so the computed class exists. Until then everything is strictest.
- [ ] Add `review-keys-verifier.yml` to the default branch (a class C change where the policy says so). It is triggered by
      `pull_request` (opened, synchronize, labeled, unlabeled, edited) and `issue_comment`.
- [ ] Hub publishes `[[pub:]]` verdicts (Rule 1) and the declared class (Rule 3).
- [ ] **Dry run before protection, covering each case:** the happy path; CHANGES_REQUESTED then APPROVE on an
      unchanged head; a push after approval (`pending`); a content-identical master sync (carried forward);
      class escalation from a diff or label; a forged pub from a non-hub account (ignored); a self-downgrade label
      (ignored); a key that is `UNAVAILABLE`.
- [ ] The owner makes `factory/review-keys` (source: GitHub Actions) a required check on the default branch.
- [ ] Hub replies on the doctrine PR with `ACK: <plan or ETA>`, or `DISTINGUISH: <reason>`.
