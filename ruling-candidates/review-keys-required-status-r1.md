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

- `factory/review-keys` is a check run with an explicit `head_sha`, posted by a verifier that runs only default-branch code
  (`pull_request_target`, `issue_comment` and `workflow_run`; never `pull_request`; never checks out PR code). It reads trust anchors from the base branch
  and computes the result from unedited hub pubs and the effective class (`docs/review-key-publication.md` Rules 1 to 3).
- Each consumer requires the check by name plus source app, and protects `.github/workflows/` with CODEOWNERS (owner) and
  required code-owner review.
- On a new head the check reads `pending` (recomputed with no bound verdicts), except for a content-identical
  master sync, which carries its keys forward. This matches the spec.

## Per-consumer wiring checklist

Measured so far: MLV-App, agent-bridge, context-ultra-salesforce and AdversarialLLM. The other consumers
(dng-auto-processor, cloudvore, airmypc, adobe-ingester) are listed for completeness, and their review flow
hasn't been measured yet.

- [ ] **Anchor (owner decision: "Allow either, App preferred"):** preferred, create a verifier GitHub App, with its key in an environment
      restricted to the default branch, and pin the required check to its App id. Allowed alternative: a ruleset required workflow pinned by path and
      default-branch ref. Pinning to the plain GitHub Actions app is NOT sufficient.
- [ ] Branch protection: code-owner review plus "dismiss stale approvals on new push"; CODEOWNERS covers `/.github/` and the trust-anchor files.
- [ ] Register the **hub identity** (a GitHub App, preferred, or a dedicated bot account) in `CLAUDE.md` / `AGENTS.md`.
      Implementer lanes never hold its credential.
- [ ] **Credentials, least privilege, split by job:**
      - hub identity: Pull requests read/write and Issues read/write (fine-grained), to post pub comments and set labels and body lines;
      - verifier: the workflow's own `GITHUB_TOKEN` (under `pull_request_target`) with `checks: write`, `pull-requests: read`, `issues: read` and `contents: read`. It needs no PAT.
      - Classic `repo:status` is not used; the check comes from Actions.
- [ ] Write the path and diff class rules in the repo's dispatch policy, so the computed class exists. Until then everything is strictest.
- [ ] Add `review-keys-verifier.yml` to the default branch (a class C change where the policy says so). Its triggers are
      `pull_request_target`, `issue_comment` (created, edited, deleted) and `workflow_run`. It does no checkout of PR code and posts its check with an explicit `head_sha`.
- [ ] Add `CODEOWNERS`: `/.github/ @layibabalola` plus the trust-anchor files, and require code-owner review on the default branch.
- [ ] Hub publishes `[[pub:]]` verdicts (Rule 1) and the declared class (Rule 3).
- [ ] **Dry run before protection, covering each case:** the happy path; CHANGES_REQUESTED then APPROVE on an
      unchanged head; a push after approval (`pending`); a content-identical master sync (carried forward);
      class escalation from a diff or label; a forged pub from a non-hub account (ignored); an edited hub pub (invalidated); deleting a seat's latest pub, e.g. r2 CHANGES_REQUESTED after r1 APPROVE (fails: high-water mark and broken chain); a PR that edits the verifier or adds a job with the same name (no effect);
      a PR that edits the hub identity or class policy (no effect until merged); approval under a lower class after escalation (doesn't count); a self-downgrade label
      (ignored); a key that is `UNAVAILABLE`; a pub published and deleted before any verifier run (fails: `issue_comment.deleted`);
      recovery by re-posting the same id and by `supersedes_deleted` (accepted once complete); a forged lower mark from another workflow or branch (ignored: mark read only from the anchor);
      a forged `factory/review-keys` check on any SHA from a non-anchor workflow (doesn't satisfy protection); two racing runs (queued; mark monotonic);
      a force-push after keys (mark kept per PR); a PR retargeted to a non-default base (fails closed); an owner approval followed by a new push to workflows (approval dismissed).
- [ ] The owner makes `factory/review-keys` (source: GitHub Actions) a required check on the default branch.
- [ ] Hub replies on the doctrine PR with `ACK: <plan or ETA>`, or `DISTINGUISH: <reason>`.
