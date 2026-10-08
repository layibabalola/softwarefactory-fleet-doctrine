# adobe-ingester cards (R14.1; written only by adobe-ingester)

## adobe-ingester/headless-lanes-fire-pretooluse
rule: a user-scope hook that shows bus content (e.g. an R15 re-check) must exit silently inside governed lanes.
mechanism: headless `claude -p` lanes still fire PreToolUse (not SessionStart), so a cwd-scoped hook keyed only on
  the repo path also reaches reviewer lanes started in that repo, breaking R15.2 and reviewer independence.
check: node C:/Users/obabalola/.claude/hooks/doctrine-recheck-r15.tests.mjs (case "R15.2: FACTORY_LANE set")
supersedes: none
evidence: reported

## adobe-ingester/regex-parens-are-groups
rule: a parser that must match literal parentheses needs a fixture where text outside them would also match.
mechanism: `/(([^()]*))/g` is two capture groups, not literal parens; it matched any paren-free run, so an
  out-of-parenthesis date could win attribution. Author tests passed; only a falsifier executing the code caught it.
check: node tools/traps-index.tests.mjs (attribution regression cases), bus commit 413d0f9
supersedes: none
evidence: measured

## adobe-ingester/stale-threshold-vs-sequential-review
rule: size a review order's dispatch-staleness threshold to the measured sequential review; a fixed 120 min goes STALLED
  before the second reviewer can start when reviewers start only after a host-admission chain.
mechanism: adobe-ingester Test-FactoryDispatch.ps1 reads stale_after_minutes per order from state.yaml and returns STALLED
  once any lane is missing and age >= it. WO-015 r5 opened 05:51:00.149Z; Opus published 07:56Z (125 min); the Sonnet
  start was refused at 129 min, and reopening after a publication would orphan the Opus report.
check: adobe-ingester HUB 2026-10-08T08:01:04.572Z; `Select-String .factory/tools/Test-FactoryDispatch.ps1 stale_after_minutes`
supersedes: none
evidence: measured

## adobe-ingester/codex-0161-readonly-sandbox-fails
rule: after a CLI upgrade, prove the different-family falsifier can execute a command before relying on its verdict.
mechanism: codex 0.161.0 `exec --sandbox read-only` fails every command on virtual-ten ("helper_unknown_error: setup
  refresh had errors"), so the falsifier returns UNSAFE with no evidence. Workaround used: danger-full-access under a
  strict read-only instruction, with `git status --porcelain` and HEAD captured before and after each round.
check: `echo "run Get-Date" | codex exec --sandbox read-only -` (expect the error on an affected host)
supersedes: none
evidence: measured

## adobe-ingester/pin-refresh-strands-built-scripts
rule: after any pin refresh, search every already-built script for the old pinned digest; a plan re-hash still passes.
mechanism: adobe-ingester 07f chain children (Invoke-WarmRead.ps1, Invoke-VerifyOnly.ps1) hard-coded the control-plane
  manifest digest 67792D7A...; a CLI-Currency Claude upgrade (2.1.287 -> 2.1.293) forced a pin refresh that replaced the
  manifest, so the pinned plan matched but the children would refuse at run time. A panel seat caught it; a rebuild
  wake was required (directive 2026-10-08a clause 3).
check: `Select-String <chain-dir>\children\*.ps1 -Pattern <old-manifest-sha>` returns no match before the run
supersedes: none
evidence: measured

## adobe-ingester/stale-unstarted-order-supersede-not-waive
rule: when a review order goes stale before any reviewer starts, supersede it pre-model and open a fresh order on the
  same candidate and deadline; never waive the staleness refusal and never reopen after a publication.
mechanism: a falsifier blocked an "age-only STALLED is not a refusal" waiver as weakening freshness; supersede plus fresh
  order (precedent adobe-ingester 673b185 for WO-012) restored freshness and was accepted for WO-015 r3->r4->r5.
check: adobe-ingester HUB 2026-10-08T05:42:43.930Z and 2026-10-08T05:51:00.149Z
supersedes: none
evidence: measured

## adobe-ingester/panel-transcript-binds-draft-sha
rule: an approval that cites reviewer transcripts must find the reviewed draft's path and SHA-256 in each transcript's
  first user message; a path alone does not bind the review to the bytes delivered.
mechanism: adobe-ingester Sol refused directive 2026-10-07f (HUB 2026-10-07T17:28:50.937Z, condition 27c 1(a)) because
  panel prompts named only the path; re-running the panel with path and SHA was accepted (HUB 2026-10-07T18:03:02.432Z).
check: the first `"type":"user"` line of each transcript contains the cited draft SHA-256
supersedes: none
evidence: measured
