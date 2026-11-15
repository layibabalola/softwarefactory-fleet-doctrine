# FWO-LINUX-CI-1: add a Linux CI job, at least for PRs that touch tests (agent-bridge and AdversarialLLM-ClaudeCode first)

status: APPROVED to file (Layi, relayed through Iverson as Layi's own words, 2026-10-25 about 12:27 AM CT: "Yes, file the Linux CI job now.")
issued_by: Grok CoS (coordination note for Dot to route; no seat claim, no heartbeat change)
issued_ct: 2026-10-25 about 12:35 AM CT
routed_by: Dot (primary CoS seat)
repos: layibabalola/agent-bridge, layibabalola/AdversarialLLM-ClaudeCode (first), then other boards whose CI is Windows-only
ack_due: 24 hours after Dot delivers it to each factory thread
asks: FWO-LINUX-CI-1 items 1 to 3, ACK with plan and ETA or DISTINGUISH per item

## Why
CI on both repos runs only on Windows, so tests that only work on Windows pass CI. Two recent cases:
- agent-bridge #270, head `5db5a5ea6d950df2d4804e6a617f788217f6ceae`: a read-only chmod is used to force a rename failure, which only happens on Windows. On Linux T1 to T3 fail and T4 passes without exercising anything. It merged green. Asks `6393440232` (Grok CoS) and `6393449551` (Dot).
- AdversarialLLM-ClaudeCode #310, head `73c3fa084bcc40637791ec47e990a54aaacfd95f`: hard-coded guessed 8.3 short names (`CI-CON~1`, `OUTSI~1`) with an either-or assertion. Ask `6393915848` (Grok CoS).
Related candidate: `ruling-candidates/ci-matrix-covers-declared-runtime-floor-r1.md`.

## Items
1. **Each repo's factory builds its own Linux job.** Add an `ubuntu-latest` job that runs the test suite, or at least the test files a PR changes, on PRs that touch tests. A cheap job scoped to changed test files is enough to start.
2. **Handle Windows-only tests honestly.** Tests that truly need Windows behavior are skipped on Linux with a stated reason, rather than failing or passing vacuously. The first Linux run should list which tests are skipped and why.
3. **Report the first Linux run.** In the workflow PR body, give the Linux result on the current master, including any tests that fail there today (the #270 tests are expected to).

## Limits
- The workflow PRs change `.github/**`, so each one still needs Layi's normal Layi-Approval before merge. Filing this order does not approve any specific workflow PR, ruleset, branch protection or required check.
- Grok CoS does not open the workflow PRs. Each repo's factory builds its own job.
- Whether the new job becomes a required check is a separate decision for Layi.
- Under R18 this order is advisory and not a merge gate on other work.

## Related
- cos-feedback/_coordination/grok-2026-10-25-test-quality-advisory.md
- https://github.com/layibabalola/softwarefactory-fleet-doctrine/pull/93 (test-portability-rule-r1 candidate)
