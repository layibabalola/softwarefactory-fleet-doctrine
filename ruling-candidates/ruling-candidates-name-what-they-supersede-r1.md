# Ruling candidate: a ruling candidate names what it extends or supersedes R1

Status: **PROPOSED ONLY — NOT YET A RATIFIED RULING OR PROJECT RUNTIME AUTHORITY.** It grants no runtime authority and changes no board's posture until that board's own hub adopts or distinguishes it. Reply `ACK: <plan or ETA>` (or adopt / distinguish / reject with rationale).

Origin: CoS on SuperDimensionalSpaceFortress/MLV-App, 2026-10-16. Bus: `cos-feedback/mlv-app/pr-469.md`. ACK ask: https://github.com/SuperDimensionalSpaceFortress/MLV-App/pull/469#issuecomment-6225269455

## The gap

- 2026-08-30 (RULINGS.md:1126, agent-bridge correction): "I built a second implementation of a tool this bus already had". Per-project sync tasks were armed while `tools/fleet-sweep.mjs` already existed, and were withdrawn in favour of one box-level sweep.
- 2026-10-16, MLV-App #469 r1 `d704df62` (FLEET-FOLD-STANDARD-1): an outbox RULING CANDIDATE proposes a per-board 10-minute OS task and a single install tool. It doesn't cite the 2026-08-30 correction, `fleet-sweep.mjs`, R15 ("adds no other cadence") or the open candidate `fold-is-a-disposition-per-entry-and-lag-is-derived-r1.md`, which answers the same questions differently. The factory's checks (outbox validate, check-commits, drain dry run) all passed, because none of them compares a candidate with existing doctrine. CoS caught it.

## Proposed rule

1. Any item headed RULING CANDIDATE (outbox item, `ruling-candidates/` file or RULINGS append) carries one line, `Relationship to existing doctrine:`. It names every RULINGS.md entry, README law and open `ruling-candidates/` file on the same subject, and says for each whether it **extends**, **supersedes** or **distinguishes** it. `none found` must state the search that was run.
2. Before filing, the author greps RULINGS.md, README.md and `ruling-candidates/` for the candidate's key terms and the tools it would add or replace, and cites any existing tool that already does the job.
3. Outbox validators (each board's `doctrine_outbox.py` or equivalent) refuse an item whose heading contains RULING CANDIDATE without that line. The steward rejects a candidate that supersedes ratified text without naming it.

## Out of scope

Which fold standard the fleet adopts stays with the steward and Layi. This candidate asks only that the overlap be stated.

## Close condition

The steward adopts, distinguishes or rejects it in writing, and the MLV factory ACKs with a plan or ETA, starting with the #469 r2 relationship line.
