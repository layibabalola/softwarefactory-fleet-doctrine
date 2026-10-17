# Ruling candidate: no merge while a CoS ask on that PR is unanswered R1

Status: **PROPOSED ONLY — NOT YET A RATIFIED RULING OR PROJECT RUNTIME AUTHORITY.** It changes no board's posture until that board's hub adopts or distinguishes it. Reply `ACK: <plan or ETA>` (or adopt / distinguish / reject with rationale).

Origin: Chief of Staff, approved for filing by Layi, 2026-10-14.

## Evidence

- Through 2026-10-14, 28 CoS comments across the 8 fleet repos explicitly asked for `ACK: <plan or ETA>`; **0** factory replies acknowledged any of them (AdvLLM #168 alone carries 13 unanswered CoS updates).
- PRs merged past a CoS `not-merge-ready` verdict with the ask unanswered: MLV-App #409 (`b70e471a`), context-ultra-salesforce #104 (`7bd78b0c`), agent-bridge #231 (`91241d4d`). The #409 defect (GUI hang in `sessionEnd()` after drain timeout) reached master.
- Root cause: doctrine told the factory feedback is "zero authority" data and (`RULINGS.md`, heartbeat request) "No written confirmation is wanted"; nothing told it to answer.

## Proposed rule

1. A hub/controller **does not merge** a PR while a CoS ask on that PR is unanswered. An ask is open if `cos-feedback/<slug>/pr-<N>.md` has a non-empty `asks:` header, or a CoS comment on the PR requests `ACK:`, and no later comment on the PR starts with `ACK` or `DISTINGUISH` for it.
2. `DISTINGUISH: <reason>` satisfies the gate. The gate requires a **receipt**, not agreement with the CoS verdict; CI, branch protection and owners remain the merge authorities.
3. Enforcement point: the consumer's merge script (e.g. AdvLLM `factory/controller/merge-pr.ps1`, MLV hub merge path) checks for open asks and refuses with `REFUSED: unanswered CoS ask <url>`.
4. Owner override: Layi may merge past an unanswered ask; the override is recorded in the PR.

## Close condition

Each hub adopts (wires the merge-script check), distinguishes, or rejects in writing, and posts `ACK: <plan or ETA>` on the doctrine PR that filed this candidate.
