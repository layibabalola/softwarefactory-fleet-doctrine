# Example cards file (R14.1 format, as specs/adobe-ingester/cards.md would hold it)

This file is a sample, not a filing: it sits under examples/, so no tool counts it as a card.
Validate it with `node tools/validate-cards.mjs --file examples/cards-v1.md --project adobe-ingester`.
The first card uses the plain "<name>: <value>" spelling; the second spells the same six fields as
bold bullets ("- **<Name>:** <value>"), the form several boards already file in. Both are valid.

## adobe-ingester/termination-budget-1s
rule: give a child-process termination at least 15 s before declaring it hung.
mechanism: on a loaded Windows box a 1 s budget expired before the kill landed, so a clean exit
  was recorded as a hang and the lane retried work that had finished.
applies: adobe-ingester, mlv-app
check: pwsh -NoProfile -File .factory/tools/Test-TerminationBudget.ps1 (Adobe Document Cloud Ingester
  repository; harness pointer under the bus directory adobe-ingester/ once pushed)
supersedes: none
evidence: measured

## adobe-ingester/example-reported-card
- **Rule:** a timed call to a function that was never exported "takes" time without running.
- **Mechanism:** the dot-sourced script failed to export the function; the timer measured the
  error path.
- **Applies to:** adobe-ingester
- **Check:** grep the call site and Test-Path the root before trusting any timing.
- **Supersedes:** none
- **Evidence:** reported

no-card: T27404 example only; an author marks its own legacy entry this way under R14.4
