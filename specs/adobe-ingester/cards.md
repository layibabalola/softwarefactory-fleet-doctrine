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
