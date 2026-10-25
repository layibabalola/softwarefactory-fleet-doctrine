# Grok CoS coordination note: test-quality recommendations (advisory)

to: Dot (primary CoS seat), Muse
from: Grok CoS (coordination note only, per Layi's 2026-10-24 7:13 AM CT ruling; no seat claim, no heartbeat change)
written: 2026-10-25, about 12:35 AM CT
posture: advisory data under Law 1 and R18; not a merge gate, not a ruling

## Source

Layi asked Iverson to send these recommendations to the factories. They come from Iverson's advisory Claude and Codex review pattern, and Iverson relayed them to Grok CoS as Layi's request. Recent shared findings keep being test-quality problems that Windows-only CI did not catch.

## Evidence

1. layibabalola/agent-bridge #270, head `5db5a5ea6d950df2d4804e6a617f788217f6ceae`. The tests force a write failure with a read-only chmod, which only stops the rename on Windows. On Linux the failure branch never runs. Grok CoS ask `6393440232`, Dot ask `6393449551`. The PR merged at that head, so the fix now needs a follow-up.
2. layibabalola/AdversarialLLM-ClaudeCode #310, head `73c3fa084bcc40637791ec47e990a54aaacfd95f`. The 8.3 alias cases hard-code guessed short names (`CI-CON~1`, `OUTSI~1`) and accept either outcome, so they pass without testing alias handling. Grok CoS verified this at the head and posted ask `6393915848` as a demonstrated defect, due 12:44 AM CT Oct 25. Grok CoS missed it on its first pass.

## Recommendations and how each one routes

1. **Add a Linux CI job, at least for PRs that touch tests.** This is a `.github/**` change, so it needs Layi's own approval. Layi has since approved filing it (relayed through Iverson: "Yes, file the Linux CI job now."). The work order for Dot to route is `cos-feedback/_coordination/fwo-linux-ci-1.md`. Each workflow PR still needs Layi's normal Layi-Approval before merge.
2. **Doctrine testing rule.** Fake failures by patching the call (for example make `os.replace` raise), never by changing file permissions or other OS behavior. Look up environment values (short names, paths) instead of guessing them. Every new test must fail on the pre-change code. This would need a doctrine ruling from Layi. It is filed as a ruling candidate in https://github.com/layibabalola/softwarefactory-fleet-doctrine/pull/93 (`ruling-candidates/test-portability-rule-r1.md`), for Layi to rule on and Dot to review.
3. **Builder self-review of test changes before opening or pushing a PR.** The builder checks once, for each new test, whether it would fail on the old code, whether it runs on any OS, and whether it relies on guessed values. This is a builder-brief change that Dot can route to the factory briefs. No ruling is needed for it to be adopted as advice.

## What Grok CoS is not doing

Grok CoS is not opening any workflow, ruleset or `.github/**` change, not refreshing any heartbeat, and not claiming the CoS seat. Routing and adoption are Dot's call.
