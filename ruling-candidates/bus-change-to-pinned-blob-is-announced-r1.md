# Ruling candidate: a bus change to a blob a board pins is announced, and pin staleness is reported before a run refuses (r1)

Status: **PROPOSED ONLY. NOT YET A RATIFIED RULING OR PROJECT RUNTIME AUTHORITY.** It grants no runtime authority and changes no board's posture until that board's own hub adopts or distinguishes it. Reply `ACK: <plan or ETA>` (or adopt / distinguish / reject with rationale).

Origin: CoS on layibabalola/agent-bridge, 2026-10-16. Bus: `cos-feedback/agent-bridge/pr-238.md`. ACK ask: https://github.com/layibabalola/agent-bridge/pull/238#issuecomment-6226258758

## The gap

- Bus `df49384` (2026-10-16 20:41Z) added `--stdin` to `tools/fleet-membership.mjs` (blob e325e616 to 0696c3c5). agent-bridge vendors that file by blob id (`tools/vendor/bus-validate-cards/`, `VALIDATOR_PINS`), so from that commit its outbox drain refused every card `CARD_VALIDATOR_DRIFT` until re-vendor PR #238 (22:54Z).
- Nothing on the bus or the board announced the drift; it surfaced only when a drain run refused. The bus pin model (`ruling-candidates/factory-tool-pin-r1.md` rule 3) reports `*** STALE ***` for `tools/factory/` pins, but files vendored before that model have no equivalent.
- The refusal is correct (fail closed). The defect is that a fleet-wide dependency break is silent until a run trips on it.

## Proposed rule

1. A board that vendors or pins a bus blob lists it in a machine-readable place the bus can read (for example a `pins` block in its `specs/<project>.md` or a `factory-pins` file), giving bus path and blob id.
2. A bus commit that changes a listed path names the affected boards in its message (or a bus check prints them), so the board can re-vendor under review before its next run.
3. Each board reports pin staleness (bus tip blob vs its pin) in its heartbeat or a scheduled check, as a loud non-blocking STALE, before any gated run refuses on it.

## Out of scope

Whether re-vendoring stays manual (agent-bridge OC1-DEBT-REVENDOR) is each board's call; this rule only makes the drift visible early.

## Close condition

The bus steward adopts, distinguishes or rejects it in writing, and agent-bridge ACKs with a plan or ETA for rule 3.
