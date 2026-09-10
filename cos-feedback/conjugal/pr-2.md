schema: cos-feedback.v1
project: conjugal
repo: layibabalola/Conjugal
pr: 2
head: 65c65f4dc4ae04fa65b99b97866ee96131b97880
reviewed_utc: 2026-09-10T17:28:59Z
event: pr-pushed
verdict: merge-when-ci-green
ci_summary: tip 65c65f4 — regression/health PASS; regression/suite FAIL (test-build-profiles.sh, 2 node assertions; Actions run 34507606727)

## Blockers

(none for this PR's docs scope)

- **Hosted `suite` (workflow `regression`)** FAILED on tip `65c65f4` (Actions run 34507606727 / job 102973538473): `test-build-profiles.sh` — `[FAIL] node build command missing npm run build`; `[FAIL] node build log missing npm` (106 assertions, 2 failures). Same regression workflow already red on `master` (run 34167674348, 2026-09-07) — not introduced by this docs-only diff (`AGENTS.md`, `CLAUDE.md`, `agents/doctrine-consumer.md`). Fix the node build-profile fixture/dispatch on a separate PR if `suite` is required to merge; do not block this stub on that debt unless branch protection demands green.

## Improvements

- `agents/doctrine-consumer.md`: template link still points at branch `docs/fleet-doctrine-consumer-template-20260909` (doctrine #57). Prefer the path that will stay resolvable after the template lands on bus master (likely doctrine #59 / `docs/doctrine-consumer-template.md` on master once merged), or note "branch may move" in the stub.
- Optional: add a one-line pointer under Adoption checklist that brief inject should match open PR numbers to `cos-feedback/conjugal/pr-*.md` before surfacing Blockers/Improvements (mirrors MLV #107 / fleet template).
- Follow-up (already in PR test plan): thin Get-DoctrineBrief-equivalent + fail-closed bootstrap inject — this stub alone is correctly zero-authority.

## Notes

- Push `65c65f4` on `docs/doctrine-consumer-20260909`: updates stub + AGENTS/CLAUDE pointers so briefs must include `cos-feedback/<slug>/pr-*.md` when present (data only / zero authority; omit if missing — fail soft). Prior commit `2ed5e51` added the stub and fleet template / MLV #107 / candidate pointers.
- Scope: docs only, +53/−0, 3 files. MERGEABLE; mergeStateStatus UNSTABLE solely from `suite` red. `health` green.
- Law 1 preserved: stub states doctrine is data; lanes must not browse/write the bus; CoS feedback labeled zero authority / CANDIDATE; missing feedback omit section.
- Project slug `conjugal` matches `specs/conjugal.md`. Candidate `fleet-doctrine-consumer-required-20260909` remains CANDIDATE_ZERO_AUTHORITY until board ADOPT.
- CoS reviewed via `gh`. No GitHub PR comment posted. Docs-only — no cloud-agent review.