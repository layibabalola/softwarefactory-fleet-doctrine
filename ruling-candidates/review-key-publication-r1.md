# Ruling candidate: review-key verdicts are published on the PR, bound to the head, with a declared class R1

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

1. Every review-key verdict is mirrored to its PR as a `[[pub:<id>]]` JSON comment with `seat`,
   `family` (sol=Codex; fable/opus=Claude), `round`, `head_sha` and `verdict`. It binds only to `head_sha`.
2. Every factory PR declares its review class with a `review-class:<class>` label and a body line.
   A class whose only key is CI (for example, agent-bridge Routine local / class-A) states that explicitly.
3. An undeclared class is read as the strictest class.

## Attack surface

Comment noise; the cost of publishing. Mitigation: one comment per key per round.
