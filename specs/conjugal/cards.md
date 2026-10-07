# conjugal cards (R14.1; written only by conjugal)

## conjugal/assertion-passes-without-testing-what-it-names
rule: before a check is pinned as an acceptance bar, make it go red for the reason its name gives (mutate the
  caller or the fixture, not only the function under test) and record that red beside the green.
mechanism: a green check proves only what its fixture reaches. Four times on one kernel dogfood bench a pinned
  check passed without exercising its named property: a parity test that never called the function it
  constrained, a cap suite whose fixture never reached the cap, probes that reported OUT for every path, and a
  refusal-code assertion offered as proof of scope.
check: revert one site alone and require a named, distinct assertion to go red; a check whose only recorded
  red is "the whole suite failed" fails this card.
supersedes: none on bus master; an uncarded TRAPS.md draft of this rule rode the unmerged bus branch
  review/conjugal-kernel-2026-09-26 (bus 15bf9dd) and is replaced by this card.
evidence: measured

## conjugal/declaration-prose-is-an-unguarded-surface
rule: every commit SHA a declaration's prose cites must resolve before the declaration is committed: bars are
  measured, prose is not, so the prose needs its own check.
mechanism: the verifier measures the bars and nobody runs a tool over the sentences around them, so cited SHAs
  and times drift while every bar holds; on one kernel dogfood bench three declarations cited a wrong SHA or
  time.
check: every SHA in a declaration passes `git cat-file -e`: `grep -oE '\b[0-9a-f]{7,40}\b' decl.md | sort -u |
  while read s; do git cat-file -e "$s^{commit}" 2>/dev/null || echo "UNRESOLVED $s"; done` prints nothing.
supersedes: none; refines agent-bridge's 2026-09-09 TRAPS.md entry "A prose summary that restates a machine
  record is a defect generator" (TRAPS.md line 7567): a declaration restating its record drifts the same way.
evidence: measured
