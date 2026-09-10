schema: cos-feedback.v1
project: agent-bridge
repo: layibabalola/agent-bridge
pr: 6
head: 22410f1224fafe18e73f979e1b1ff40e88f426bc
reviewed_utc: 2026-09-10T17:59:04Z
event: pr-pushed
verdict: merge-when-ci-green
ci_summary: Windows CI test IN_PROGRESS (run 34511235753); prior head had SUCCESS

## Blockers

(none)

## Improvements

- Adoption checklist in `agents/doctrine-consumer.md` still unchecked — stub is fine to merge; follow-up should implement thin Get-DoctrineBrief-equivalent + fail-closed bootstrap injection before claiming consumer wiring.
- After doctrine #59 lands, flip the template URL from branch `docs/cos-feedback-brief-wire-20260910` to `blob/master/docs/doctrine-consumer-template.md` (stub already documents that preference).

## Notes

- Docs-only (+57/−0): new `agents/doctrine-consumer.md` + pointers in `AGENTS.md` / `CLAUDE.md`.
- Head `22410f1` retargets template off conflicting #57 onto doctrine #59 branch blob (master after merge); candidate path stays via #57 until land; cos-feedback README points at master (#58). Addresses prior CoS Improvement about rotting on a deleted #57 branch tip.
- Briefs must include `cos-feedback/<slug>/pr-*.md` when present (data only / zero authority; omit if missing — fail soft).
- MERGEABLE / UNSTABLE while checks run; CANDIDATE_ZERO_AUTHORITY until board ADOPT.
- Related: fleet template doctrine #59 (was #57 for template); candidate #57; reference MLV-App #107; CoS surface #58.
- No GitHub PR comment posted (CoS chat + bus only).