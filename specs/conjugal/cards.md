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
