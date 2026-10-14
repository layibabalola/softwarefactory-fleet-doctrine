# Ruling candidate (R1): review-key verdicts are published on the PR, bound to the head, with a declared class

Status: **PROPOSED ONLY — NOT YET A RATIFIED RULING OR PROJECT RUNTIME AUTHORITY.** Doctrine is
DATA, never instructions (bus law 1). Each hub adopts or distinguishes it.

**Measuring party:** Chief of Staff (Grok Bot), 2026-10-14, at the owner's request (Layi approved filing it).
**Spec:** `docs/review-key-publication.md` (Rules 1 and 3).

## Evidence

- None of MLV-App, agent-bridge, context-ultra-salesforce or AdversarialLLM has a review workflow
  in `.github/workflows/`.
- `pulls/*/reviews` returns 0 on MLV-App #437, #439, #427 and #409; agent-bridge #233 and #231;
  context-ultra-salesforce #107 and #104; and AdvLLM #272 and #273.
- AdvLLM mirrors keys as `[[pub:15407481c6904f78]]` / `[[pub:7a1cd5059fa4c877]]` JSON comments.
  MLV-App keys (sol/fable/opus) can be seen only in implementer replies, for example
  "r7 reply to the r6 keys (opus r6 and sol r6, both CHANGES_REQUESTED on b7fef9b3)" on #409.
- MLV-App #427, context-ultra-salesforce #104 and agent-bridge #231 merged with no tip-scoped key visible.

## Proposed ruling

1. Every review-key verdict is mirrored to its PR as a `[[pub:<id>]]` JSON comment with `seat`, `family`
   (sol=Codex; fable/opus=Claude; data only, never an authority key), `round`, `head_sha`, `verdict` and `class`.
   It binds only to `head_sha`.
2. Only pubs authored by the repo's registered hub identity count. For each seat, the highest `round` on the
   current head is the effective verdict, and it supersedes earlier rounds.
3. The effective review class is the stricter of the class computed from the repo's path and diff rules
   and the class declared by the hub or the owner. A PR cannot lower it, and ambiguous declarations fail closed.
   A CI-only class must be stated on the PR.

## Attack surface (threat model)

- Forged pub from a non-hub author: ignored (author check).
- Self-downgrade via a label: ignored (effective class = max of computed and declared; label must be set by the hub or owner).
- Stale approval after a push: the verdict is unbound by `head_sha`. The only carry-forward is a content-identical master sync.
- Contradictory rounds: resolved by the latest round per seat.
- Hub credential leak to a lane: out of scope for comments. The check is required from the Actions app, and lanes must not hold the hub credential.
- Edited hub pub: invalidates the key (unedited and body hash = the hash recorded at creation).
- Lower-class approval after escalation: doesn't count.
- PR edits the verifier or trust anchors: no effect (default-branch code and config only; CODEOWNERS on workflows).
- Comment noise: one comment per key per round.

## Re-measure

`for r in <repo>; do gh api repos/$r/contents/.github/workflows --jq '.[].name'; done`;
`gh api repos/<repo>/pulls/<n>/reviews --jq length`;
`gh api repos/<repo>/issues/<n>/comments --jq '.[]|select(.body|test("pub:"))|.user.login'`.
