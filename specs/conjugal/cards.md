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

## conjugal/prekey-13-a-limitation-or-residual-describes-what-happens
rule: every limitation, residual, park risk and behaviour-change note is a scope exclusion ("outside the
  declared model; nothing is declared for it") or a relation on check ids; any that says what the code does
  ("leaves", "then depends on", "falls through to") is attacked like a rule.
mechanism: A limitation or residual describes what happens; an independent verification round or the review
  before it found this in a real declaration; recorded cost: 1 refused in 17 minutes.
check: `grep -niE 'leaves|then depends on|falls through' decl.md` prints no line inside a limitation,
  residual, park-risk or behaviour-change note; each such note reads as a scope exclusion or names the check
  ids it relates.
supersedes: this project's uncarded TRAPS.md entry at line 27733 (bus c638439; catalogue rows 13-19), for this
  row
evidence: measured

## conjugal/prekey-14-a-rule-sentence-is-false-somewhere-inside-its-own
rule: formalise the rule sentences from the declaration alone (not from the code) and compare them with the
  real code over an enumerated or sampled set of in-model inputs; a disagreement is a false sentence or a
  model stated too widely.
mechanism: A rule sentence is false somewhere inside its own model; an independent verification round or the
  review before it found this in a real declaration; recorded cost: cited by a subject.
check: a reviewer who has not read the code writes each rule sentence of the declaration as a predicate, runs
  the predicate and the real code over the same enumerated or sampled in-model inputs, and records zero
  disagreements, keeping the input list and both outputs with the review.
supersedes: this project's uncarded TRAPS.md entry at line 27733 (bus c638439; catalogue rows 13-19), for this
  row
evidence: measured

## conjugal/prekey-15-a-successor-repairs-only-the-sentences-its
rule: re-run rows 3 and 6 over the WHOLE successor text, not the predecessor's findings list; every sentence
  about unchanged bytes is a `sed -n`/`grep` claim with its command or is deleted, including trailing clauses
  after a byte claim.
mechanism: A successor repairs only the sentences its predecessor was parked on; an independent verification
  round or the review before it found this in a real declaration; recorded cost: 1 parked.
check: the review record covers every sentence of the successor, not only the predecessor's findings, and each
  sentence about unchanged bytes (trailing clauses included) carries the `sed -n` or `grep` command that
  proves it; a byte sentence with no command fails.
supersedes: this project's uncarded TRAPS.md entry at line 27733 (bus c638439; catalogue rows 13-19), for this
  row
evidence: measured

## conjugal/prekey-16-a-host-fact-names-a-tool-the-subject-s-scripts-do
rule: for every version or path the text states (Python, bash, jq, PowerShell), run the resolver the scripts
  under test use (the project's own launcher helper, the runner's `$BASH`, PATH under the child's names) and
  print what it selects; state that, or state no version.
mechanism: A host fact names a tool the subject's scripts do not select; an independent verification round or
  the review before it found this in a real declaration; recorded cost: 1 parked.
check: for each version or path the declaration states, the reviewer runs the scripts' own resolver in the
  subject's environment (for example `command -v python3 && python3 --version` under the runner's PATH, or the
  project's launcher with `--version`) and the printed result equals the stated one.
supersedes: this project's uncarded TRAPS.md entry at line 27733 (bus c638439; catalogue rows 13-19), for this
  row
evidence: measured

## conjugal/prekey-17-the-cited-authority-row-does-not-fit-the-change-s
rule: for every register row or directive clause the text claims, quote the row's class and check that the
  change is in it; a change no row fits claims none and shows, by commands on the diff, why no gate applies.
mechanism: The cited authority row does not fit the change's class; an independent verification round or the
  review before it found this in a real declaration; recorded cost: 1 refused in 3 minutes.
check: for each register row or directive clause the declaration cites, the review record quotes the row's
  class beside `git diff --stat <base>..<code>`; a changed file outside the quoted class fails the claim.
supersedes: this project's uncarded TRAPS.md entry at line 27733 (bus c638439; catalogue rows 13-19), for this
  row
evidence: measured

## conjugal/prekey-18-the-gate-is-scoped-by-path-not-by-hunk
rule: before claiming that no gate applies, grep earlier declarations for the file's own classification (the
  project's declarations) and the profile's gate list; a file any subject classed security-sensitive takes a
  register row or parks for the owner.
mechanism: The gate is scoped by path, not by hunk; an independent verification round or the review before it
  found this in a real declaration; recorded cost: 1 refused in 5 minutes.
check: `git grep -n -i 'security-sensitive'` over the earlier declarations, read against `git diff --name-only
  <base>..<code>`: each changed file an earlier declaration classed security-sensitive is covered by a cited
  register row, or the subject parks for the owner.
supersedes: this project's uncarded TRAPS.md entry at line 27733 (bus c638439; catalogue rows 13-19), for this
  row
evidence: measured

## conjugal/prekey-19-the-title-is-a-declared-sentence
rule: read the title, headings and table captions as behaviour sentences: each is a relation on check ids, a
  commanded byte claim, or a reading of changed lines that the code bears literally ("signals" includes signal
  0).
mechanism: The title is a declared sentence; an independent verification round or the review before it found
  this in a real declaration; recorded cost: 1 parked.
check: `grep -nE '^#' decl.md` and every table caption: each hit is a relation on check ids, a byte claim with
  its command, or a literal reading of changed lines, and a reviewer reading the diff finds no hit the code
  contradicts.
supersedes: this project's uncarded TRAPS.md entry at line 27733 (bus c638439; catalogue rows 13-19), for this
  row
evidence: measured

## conjugal/prekey-20-a-park-on-a-term-sweeps-the-term
rule: when a subject parks on a word (signal, read, only, first, every), grep the successor's whole text for
  that concept and every synonym and re-read each hit against the code; a corrected title with an uncorrected
  body sentence is the same park.
mechanism: A park on a term sweeps the term; an independent verification round or the review before it found
  this in a real declaration; recorded cost: 1 parked.
check: `grep -niwE '<word>|<synonym>' successor.md` with the parked word and every synonym prints each hit,
  and the review record re-reads every hit against the code; a hit that repeats the parked reading fails.
supersedes: this project's uncarded TRAPS.md entry at line 27753 (bus 3fbb0c3; catalogue rows 20-25), for this
  row
evidence: measured

## conjugal/prekey-21-a-census-heading-names-its-grep
rule: a census is titled by the command that produces it, never by the property the command approximates;
  implicit forms the grep cannot see (a `spawnSync` `timeout`, an `AbortSignal`) are scope exclusions.
mechanism: A census heading names its grep; an independent verification round or the review before it found
  this in a real declaration; recorded cost: 1 parked.
check: `grep -nE '^#+ ' decl.md` shows each census heading as the command that produced it, never a property
  (every, all, may) the command approximates, and each implicit form the command cannot see is listed as a
  scope exclusion.
supersedes: this project's uncarded TRAPS.md entry at line 27753 (bus 3fbb0c3; catalogue rows 20-25), for this
  row
evidence: measured

## conjugal/prekey-22-a-review-that-stops-at-its-first-finding
rule: the pre-key reviewer reads the whole text line by line and reports EVERY finding; the successor applies
  all of them at once. A review that reports one finding and stops costs one successor per sentence.
mechanism: A review that stops at its first finding; an independent verification round or the review before it
  found this in a real declaration; recorded cost: cited by 3 subjects; a subject's exhaustive pass found
  thirteen.
check: the review record lists findings against line numbers spanning the whole draft (`nl -ba decl.md`), not
  one finding and a stop, and the successor applies every listed finding in one commit.
supersedes: this project's uncarded TRAPS.md entry at line 27753 (bus 3fbb0c3; catalogue rows 20-25), for this
  row
evidence: measured

## conjugal/prekey-23-review-without-convergence
rule: a long text yields new findings to every fresh exhaustive reader. After two exhaustive passes have each
  been applied, the next successor gets a fix-verification pass (every applied fix true, nothing new
  introduced) and goes to the key, with that disclosed; the key fails fast on text, so a remaining gap costs
  minutes. Shorter declarations are the durable fix.
mechanism: Review without convergence; an independent verification round or the review before it found this in
  a real declaration; recorded cost: cited by a run of subjects; 1 keyed.
check: the subject's review records show at most two applied exhaustive passes before a fix-verification pass
  (each applied fix checked true, no new text), and the key prompt discloses that pass.
supersedes: this project's uncarded TRAPS.md entry at line 27753 (bus 3fbb0c3; catalogue rows 20-25), for this
  row
evidence: measured

## conjugal/prekey-24-a-condition-sentence-against-every-fixture
rule: for each "X runs only when ..." or "otherwise ..." sentence about the test, list every fixture and check
  that each satisfies or falsifies the condition as stated, including fixtures with no decoy, no record or no
  child.
mechanism: A condition sentence against every fixture; an independent verification round or the review before
  it found this in a real declaration; recorded cost: 1 refused in 4.5 minutes.
check: for each line of `grep -nE 'only when|otherwise' decl.md` about the test, the review record has one
  line per fixture saying whether that fixture satisfies or falsifies the condition, including fixtures with
  no decoy, no record or no child.
supersedes: this project's uncarded TRAPS.md entry at line 27753 (bus 3fbb0c3; catalogue rows 20-25), for this
  row
evidence: measured
