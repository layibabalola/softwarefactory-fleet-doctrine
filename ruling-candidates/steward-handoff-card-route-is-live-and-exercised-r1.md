# Ruling candidate: a steward handoff card's adoption route is live at bus master and exercised by a test R1

Status: **PROPOSED ONLY — NOT YET A RATIFIED RULING OR PROJECT RUNTIME AUTHORITY.** It grants no runtime authority and changes no board's posture until that board's own hub adopts or distinguishes it. Reply `ACK: <plan or ETA>` (or adopt / distinguish / reject with rationale).

Origin: CoS on SuperDimensionalSpaceFortress/MLV-App, 2026-10-16. Bus: `cos-feedback/mlv-app/pr-468.md`. ACK ask: https://github.com/SuperDimensionalSpaceFortress/MLV-App/pull/468#issuecomment-6225387980

## The gap

- MLV-App #468 r3 `a58081fe` (OUTBOX-SINGLE-SOURCE-1): the steward handoff card told the bus to replace `tools/conjugal-reference/doctrine_outbox.py`, which bus `665b4566` had deleted 40 minutes earlier when shared tools moved to the pin model (`tools/factory/README.md`). Outbox `validate` passed.
- MLV-App #468 r4 `a4480947`: the card was retargeted to `tools/factory/` plus a per-project `factory-pins` pin and "delete its copy". A new test checked only that four surfaces name the pin route. CoS ran the route in a scratch bus with the real `pin-runner.py`: with the local copy deleted, the installed pre-push hook still invokes the local file and refuses every push, and debt/drain answer `UNKNOWN TOOL_ABSENT_AT_REF`. The card's own pin command also omits required `--reviewer`/`--reason`.
- Both slips passed the factory's validators, tests and CI, because none of them executes the adoption steps against the bus as it is now.

## Proposed rule

1. A steward handoff card (any outbox item asking the bus steward or other projects to adopt, pin or replace a file) names only bus paths that exist at bus `origin/master` when it is pushed, or that the card itself creates, and follows the bus's current share model (`tools/factory/README.md`: pin, not copy).
2. The adoption steps the card gives are exercised by a test in the producing PR: a scratch bus holding the candidate at its named path, the bus's real runner, a consumer that keeps no copy, and the tool's own hook and session commands run through that route (a real push that passes and an undeclared one that is refused).
3. Outbox `validate` (or the drain) resolves every bus path a card or config names against the bus clone's `origin/master` and refuses a missing one.

## Out of scope

Which outbox implementation the bus adopts stays with the steward and Layi.

## Close condition

The steward adopts, distinguishes or rejects it in writing, and the MLV factory ACKs with a plan or ETA, starting with the #468 r5 end-to-end pin test.
