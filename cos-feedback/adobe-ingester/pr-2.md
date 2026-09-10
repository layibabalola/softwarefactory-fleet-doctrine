schema: cos-feedback.v1
project: adobe-ingester
repo: layibabalola/adobe-document-cloud-ingester
pr: 2
head: 809b80fc403efbebfbd180ea19296caf5a71bef6
reviewed_utc: 2026-09-10T18:01:15Z
event: pr-pushed
verdict: info
ci_summary: n/a — PR already MERGED into main; no status checks on docs/doctrine-consumer-20260909

## Blockers

(none)

## Improvements

(none for this tip — PR merged)

## Notes

- Push `809b80fc` on `docs/doctrine-consumer-20260909` (then merged): retargets stub off conflicting doctrine #57 tip for the portable template. Template now points at doctrine #59 branch blob (`docs/doctrine-consumer-template.md`; prefer master after #59 lands). Candidate still via #57 until land. CoS feedback README on master (#58).
- Prior CoS Improvement addressed: fleet template / candidate links no longer pin the open #57 branch as the durable template path.
- Prior note still true historically: tip tree only changed `.factory/BOOTSTRAP.md` + `agents/doctrine-consumer.md` (no AGENTS.md / CLAUDE.md pointers in the landed diff despite earlier commit wording).
- Scope: docs-only stub, +53/−0 across history; zero runtime authority; `adobe-ingester` slug matches specs. Candidate `fleet-doctrine-consumer-required-20260909` remains CANDIDATE_ZERO_AUTHORITY until board ADOPT.
- Consumers: ignore or delete this `pr-2.md` once hubs treat the PR as closed; Law 1 preserved in stub text.
- CoS reviewed via `gh`. No GitHub PR comment posted.