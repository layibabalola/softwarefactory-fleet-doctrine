schema: cos-feedback.v1
project: agent-bridge
repo: layibabalola/agent-bridge
pr: 6
head: 2c7fc1897015ae5af66db6541a1ba2c3d7675604
reviewed_utc: 2026-09-10T17:33:22Z
event: pr-pushed
verdict: merge-ready
ci_summary: Windows CI test SUCCESS (run 34507598726)

## Blockers

(none)

## Improvements

- Adoption checklist in `agents/doctrine-consumer.md` still unchecked — stub is fine to merge; follow-up should implement thin Get-DoctrineBrief-equivalent + fail-closed bootstrap injection before claiming consumer wiring.
- Template link points at branch `docs/fleet-doctrine-consumer-template-20260909` (doctrine PR #57). After #57 lands on master, prefer master blob URLs so the stub does not rot on a deleted branch tip.

## Notes

- Docs-only (+53/−0): new `agents/doctrine-consumer.md` stub + short pointers in `AGENTS.md` / `CLAUDE.md`.
- Push `2c7fc18` adds: briefs must include `cos-feedback/<slug>/pr-*.md` when present (data only / zero authority; omit if missing — fail soft).
- MERGEABLE / CLEAN; CANDIDATE_ZERO_AUTHORITY until board ADOPT of the fleet candidate.
- Related: fleet template doctrine PR #57; reference MLV-App #107.
- No GitHub PR comment posted (CoS chat + bus only).