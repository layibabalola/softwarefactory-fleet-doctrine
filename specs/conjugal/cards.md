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

## conjugal/prekey-25-an-exclusion-covers-what-a-check-declares
rule: list every limitation and "nothing is declared" clause and, for each, every check id and bar whose
  declared result falls inside it; an exclusion may not cover a declared result. Run it against the fixture
  table and the bars, not only against the code.
mechanism: An exclusion covers what a check declares; an independent verification round or the review before
  it found this in a real declaration; recorded cost: 1 refused in 3.5 minutes.
check: for each limitation and "nothing is declared" clause, the review record lists every check id and bar
  (from the fixture table and the bars) whose declared result falls inside it, and every list is empty.
supersedes: this project's uncarded TRAPS.md entry at line 27753 (bus 3fbb0c3; catalogue rows 20-25), for this
  row
evidence: measured

## conjugal/prekey-26-the-review-runs-after-the-declaration-is-committed
rule: run the lint and the full pre-key review on the DRAFT at a throwaway declaration-then-code pair; commit
  the declaration only on `PREKEY: KEY`. A fix after the declaration commit makes a successor, which earns
  zero K5 credit.
mechanism: The review runs after the declaration is committed; an independent verification round or the review
  before it found this in a real declaration; recorded cost: 1 parked.
check: the review that returned `PREKEY: KEY` records the draft's blob id, and `git rev-parse <declaration
  commit>:decl.md` prints that same id; a declaration edited after its commit fails.
supersedes: this project's uncarded TRAPS.md item for this row, withdrawn from its outbox before it was
  published
evidence: measured

## conjugal/prekey-27-the-delivered-tree-is-not-the-keyed-tree
rule: before a key, merge the current `origin/master` into the subject branch if the code commit is not a
  fast-forward, and key that merge; push nothing while the key runs; on ACCEPT push the keyed commit itself,
  and only then the Outcome commit on top.
mechanism: The delivered tree is not the keyed tree; an independent verification round or the review before it
  found this in a real declaration; recorded cost: twelve accepted subjects earned no K5 credit.
check: `git rev-parse origin/master^{tree}` right after the delivery push equals the keyed tree.
supersedes: this project's uncarded TRAPS.md item for this row, withdrawn from its outbox before it was
  published
evidence: measured

## conjugal/prekey-28-the-rehearsal-ran-at-a-base-the-subject-is-not-cut
rule: build the throwaway declaration-then-code pair on the `origin/master` commit the subject branch will be
  cut from, and after the real declaration and code commits rehearse every labelled command once more before
  the key; restate any pinned-base command against the branch point.
mechanism: The rehearsal ran at a base the subject is not cut from; an independent verification round or the
  review before it found this in a real declaration; recorded cost: 1 parked.
check: the rehearsal log names the pair's parent, and `git merge-base origin/master <code commit>` at the key
  equals it or the log has a second rehearsal at the real commit.
supersedes: none
evidence: measured

## conjugal/prekey-29-the-item-had-an-unmet-sequencing-gate
rule: before choosing an item, grep the triage files and the queue for any sequencing wording on it ("sequence
  after", "after both", "depends on", "blocked by", "held"), and choose it only when every prerequisite it
  names is ACCEPTED on `origin/master`; the declaration carries a command showing each one.
mechanism: The item had an unmet sequencing gate; an independent verification round or the review before it
  found this in a real declaration; recorded cost: 1 refused, 1 parked.
check: for each prerequisite subject, `git show origin/master:<its declaration> | grep -c '^## Outcome -
  ACCEPTED'` prints `1`.
supersedes: none
evidence: measured

## conjugal/prekey-30-the-key-prompt-s-harness-forbade-what-a-declared
rule: build the key prompt's harness constraints from the declaration's own harness and checks, never from a
  fixed block carried over from another subject; before launch, list every suite and command the declaration's
  bars and Baseline require and confirm no harness line forbids one.
mechanism: The key prompt's harness forbade what a declared check runs; an independent verification round or
  the review before it found this in a real declaration; recorded cost: a key round was spent: an inherited
  "start no dashboard" line stopped the key from running two declared dashboard suites, so one bar could not
  be established.
check: for each suite in the Baseline table, the prompt contains no constraint that the suite's own behaviour
  (a dashboard on loopback, a network call, a scheduled-task read) would violate.
supersedes: none
evidence: measured

## conjugal/fleet-advisory-channel-candidate-r1
rule: a cross-project request is a card addressed with applies: and answered by one line in the receiver's dispositions file, never free text to a session or runner; review CANDIDATE r1 at specs/conjugal-fleet-advisory-channel.md and file under adjudications/fleet-advisory-channel/ (REVIEW-PROMPT.md there).
mechanism: on 2026-10-09 same-host sessions coordinated well by live messages, but another project's unattended runner was reachable only by an owner paste, and the finding it needed was already a card nothing had addressed to its reader; the fleet spans three hosts with one-way heartbeats only.
check: git -C <bus> ls-tree --name-only origin/master dispositions/ prints nothing at bus 635958f, so no board has an answer slot yet and every addressed card stays unanswerable
supersedes: none
evidence: measured

## conjugal/prekey-31-the-rehearsal-compared-outputs-without-their-order
rule: compare each rehearsed output with the declared text exactly, line order and whitespace included, never
  as a set; a multi-line declared output follows the order the command prints (`grep -o` and `grep -n` print
  in file order).
mechanism: The rehearsal compared outputs without their order; an independent verification round or the review
  before it found this in a real declaration; recorded cost: 1 parked.
check: the rehearsal script diffs each command's stdout byte for byte against the declared block and fails on
  any difference.
supersedes: none
evidence: measured

## conjugal/prekey-33-a-stand-in-s-default-arm
rule: a stub, fake or `case` stand-in in the test has no catch-all arm that answers success: an unmatched
  input fails loudly, so a call the test did not plan cannot pass as a planned one.
mechanism: adopted into the pre-key review from sibling product cards in Conjugal's 2026-10-09 doctrine
  fold; no Conjugal instance of this failure has been measured.
check: read each stub's last arm.
supersedes: none
evidence: reported

## conjugal/blur-upload-stall-is-implicit-sync-not-thermal
rule: a per-frame texture upload that stalls 200+ ms while the app's own fence wait reads zero is a driver implicit-sync block on a texture still in flight; ring-buffer it (or upload via an orphaned PBO, or keep the stage on the decode device) before tuning the host or the thermal gate.
mechanism: on Bachelor 2026-10-10, 44 CUDA playback runs showed present stalls labelled blur_upload at 156-442 ms; per-frame logs show setup_blur_upload_ms ~0.25 ms normally and 216-401 ms on stall frames with blur_drain and realloc ~0, on one blur texture allocated once (452x564 at x4; x2 and x1 runs stalled too); stalls per run were 2.24 before a heatsink upgrade and 2.17 after, while throttling only added frame skips; every one of the 8 builds tested that day stalled.
applies: mlv-app
check: in a fullscreen CUDA run whose log shows "Playback scale effective: requested=x4", grep -E "present_setup_over_50ms|present_setup_max_part|setup_blur_upload_ms" out/diagnostic/logs-*/mlvapp-*.log; a fixed build shows present_setup_over_50ms=0 in each of 5 runs (one unfixed x4 run of 28 also read 0, so a single run proves nothing)
supersedes: none
evidence: measured

## conjugal/hotter-at-equal-watts-key-the-match-on-core-clock
rule: before calling "CPU hotter at the same package power" a cooling fault, match on per-core clock, not only package watts and total CPU %. Few-thread turbo puts the same watts into fewer cores, so the hottest-core reading rises with no change in cooling. A cooling fault heats every core, at every clock.
mechanism: on Bachelor (i9-12900HK), 2026-10-11. The Core Temp feed's "package" column was the hottest single core. Matched on package W, total CPU % and trailing 5-min power, it read 70-73 C every hour on 10-10 until 22:59, then 79-88 C every hour after. The first diagnosis blamed physical cooling (vents, heatsink mounting) and advised a reboot. The Core Temp source log showed instead that average P-core MHz never exceeded 2394 until 23:01 and boosted to 4.7-4.9 GHz from 23:02. At the same clock, 40-60 W rows after the step read 73 C, against 71-73 C before. The E-core median moved 0.5 C at most (64.5 to 65.0 C). All-core and many-thread rows were unchanged (+/-4 C); only rows under 30 % CPU rose ~10 C. The pattern switched off for about 40 min (23:50-00:30) when the work went many-threaded. Median package power at 15-25 % CPU went from ~18 W to ~34 W.
check: from a Core Temp CT-Log (per-core temps plus per-core or average P-core frequency), split rows at a fixed package-power band by P-core MHz (<=2400 vs >3000). The temperature gap between periods should vanish within the low-clock rows, and the E-core mean should not move. A real cooling fault fails both.
supersedes: none
evidence: measured

## conjugal/nvidia-smi-wakes-a-d3-dgpu-and-reports-the-wake
rule: on a hybrid-graphics laptop, read the dGPU's device power state (D-state) before trusting any nvidia-smi P-state or power reading. A query against a D3 (off) card wakes it and reports the wake, not the resting state. Never build a heat or admission gate on polled nvidia-smi watts without reading the D-state first.
mechanism: on Bachelor (XPS 17 9720, RTX 3060 Laptop, iGPU drives the panel), 2026-10-11: DEVPKEY_Device_PowerData read D3 for every NVIDIA function across repeated samples, and that read does not wake the card. One `nvidia-smi --query-gpu=pstate,power.draw` call took ~1.35 s and returned "P0, ~21 W", with power.draw.average 0-1 W. D-state reads 1 s apart never caught the card out of D3. Held awake by nvidia-smi alone (no client context), the card read pstate "[Unknown Error]" at 1282 MHz and ~16 W. With a real CUDA context held idle, it settled at P8, ~9 W, 210 MHz, within ~10 s. Three sessions spent ~10 h treating this as a "GPU stuck at P0" fault: a driver-reset script, a scheduled-guard proposal, and a device restart that "failed". An admission gate that polled nvidia-smi read >=15 W on every probe and blocked every second-job join from 03:15 to ~12:30.
check: on an idle hybrid laptop, `(Get-PnpDeviceProperty -InstanceId <VEN_10DE id> -KeyName DEVPKEY_Device_PowerData).Data`, where bytes 4-7 minus 1 = D-state, reads 3. Then time one `nvidia-smi --query-gpu=pstate,power.draw,power.draw.average --format=csv,noheader`: expect >1 s, "P0" with ~20 W instantaneous and an average of a few W or less. D-state reads from 1 s after the call show D3 again.
supersedes: none
evidence: measured

## conjugal/prekey-37-a-fixed-timeout-in-a-fixture-had-no-headroom-for-a
rule: size every fixed wait or timeout in a test fixture from the slowest measurement on a throttled host
  (record the package temperature with it), with at least 5x headroom, or make the check wait on the event
  instead of the clock.
mechanism: A fixed timeout in a fixture had no headroom for a throttled host; an independent verification
  round or the review before it found this in a real declaration; recorded cost: 1 keyed, 1 refused.
check: for each fixed timeout in the new test, the evidence carries its worst measured duration under load,
  and the timeout is at least 5x it.
supersedes: none
evidence: measured

## conjugal/standing-context-probe-verifies-nothing
rule: a model verdict that closes an adoption item must cite a probe that could have FAILED for that item; a probe quoting a sentence true for every item (a deprecation line, a mission statement) or a sibling's identifier as "absent" verifies nothing and is refused.
mechanism: an automated adjudicator injected a project's "legacy model is deprecated" line into every item's evidence and its prompt told the model to distinguish legacy-homed items; 34 of 45 model-settled closures cited one of three constant sentences, the probe passed every time, and 30 of the 36 re-read closures were live learnings (the "legacy" module was imported by the live scheduler gate).
check: count closed items per (file, probe text); any probe that closed more than two items, or whose text is not in that item's own search evidence, is a tautology.
supersedes: none
evidence: measured

## conjugal/k7-detector-reads-acceptance-time
rule: A delivery-at-identity (K7) detector passes a subject only when the keyed tree was the delivery ref's tip at an instant at or after the key's acceptance time and the ref's next move recorded the Outcome; it reads the acceptance time from the receipted final-answer record, and refuses when that time cannot be proven.
mechanism: "Was this tree ever the tip" cannot see a tree that was the tip only before its key accepted it. The detector passed a subject from local master's reflog that the 2026-10-17 dispositions refused because the tip moved 83 s before acceptance. Reflog times are the clock; commit dates are not (rebase rewrites committer dates).
check: python tools/factory/delivery-at-identity.tests.py
supersedes: none
evidence: measured

## conjugal/heavy-slot-admission-is-one-unit
rule: A machine-wide heavy-slot admission covers one bounded unit of work (a test file, a mutant set, a benchmark leg, or a bar measured to finish in minutes), never a multi-hour batch or a whole tier; a batch runner takes one admission per unit so an exclusive waiter can start between units, and refuses to run whole inside an outer admission (a nested admission passes straight through).
mechanism: Measured 2026-10-18 on the shared laptop: one admission wrapped around a ~60-file tools bar (1200 s per-file timeout) held a slot 2 h+ while an exclusive CUDA benchmark waited ~3.0 h, over 2 h of it at the queue head, and three shared runs queued behind it. The free slot stayed idle because the joiner heat gate was correctly closed (0 of 90 minutes passable), so backfill or a drain change would not have helped, and a kill ceiling would have killed a legitimate 136-min bar. heavy-slot 2.2.0 prints each holder's age inside the slot line's parentheses ("since S, held M min)") and warns the holder on stderr once it has held 60 min while others wait; neither changes admission.
check: run the machine ops self-test heavy-slot.overrun.test.py against heavy-slot.py (26 sandboxed checks: held field inside the parentheses, both production parsers still match, notice only past the threshold with a waiter, rc passed through); on the 2.1.0 copy it fails 7 and then aborts
supersedes: none
evidence: measured

## conjugal/shared-host-protects-short-exclusive-work
rule: On a shared host, the admission wrapper itself serves a short, predictable exclusive job ahead of shared work that has not yet waited long, and never lets a shared run take an empty machine from it; per-caller unit rules are necessary but are not relied on, because sessions type admissions ad hoc from briefs and no project contract treats that operational choice as a decision needing adversarial review.
mechanism: Measured 2026-10-18: a builder subagent following a brief that allowed a whole suite per admission saw a starved exclusive job of the same benchmark agent at the head of the queue status 9 min before it wrapped a ~64-suite tier in one admission (the benchmark it then starved queued 10 min later); no swarm ran and no rule required one. When the machine emptied, oldest-first gave the tier 141 min; the benchmark then ran in 3 min. That agent's holds measured p90 2.7, max 7.7 min over 857 holds (689 benchmark legs: p90 2.8, max 7.7). heavy-slot 2.3.0 orders them ahead of shared tickets waiting under 60 min, reserves the empty machine for them, and turns the promotion off for good if one runs past 15 min.
check: run the machine ops self-test heavy-slot.shortexcl.test.py against heavy-slot.py and its 2.2.0 copy (24 sandboxed checks incl. an end-to-end replay where the 2.2.0 copy gives the freed machine to the older shared run and 2.3.0 to the benchmark; 5 planted mutants killed by the author, 3 more by the reviewer; harness not shipped)
supersedes: none
evidence: measured

## conjugal/windows-append-is-not-atomic-across-processes
rule: On Windows, a file that more than one process appends to (a JSONL ledger, a shadow log, a test fake's record) is written through a handle opened for FILE_APPEND_DATA only, one WriteFile per record, or else one file per writer; Python's open(path, "a") is never relied on for concurrent appends.
mechanism: The MS C runtime emulates O_APPEND as seek-to-end then write, so two processes can write at one offset and overwrite or tear each other's lines. Measured 2026-10-18 on the shared laptop: 8 writers x 1500 JSON lines through "a" kept 10,566 and 10,948 of 12,000 lines intact; the same load through a FILE_APPEND_DATA handle kept 12,000 of 12,000 twice. A live machine-wide admission log already held two torn tails written within one second of a second appender, and a sibling project's test flaked from the same race.
check: run the machine ops self-test heavy-slot.append.test.py against heavy-slot.py (8 processes x 1500 lines through the atomic append: all intact and unique; a planted mutant that falls back to plain append loses lines and is caught)
supersedes: none
evidence: measured

## conjugal/reservation-parks-never-halts
rule: a reserved class parks the subject that needs it, and the next subject proceeds. No list, report or
  interpretation may turn reservations into a queue-wide stop, and a limit that rests only on a recorder's
  interpretation, not on the owner's words, is never grounds for one.
mechanism: a drafter read one line of a directive's "recorder's interpretation (not the owner's words)"
  section as reserving every item outside an audit. It reserved every remaining product, control and
  doctrine-adopt candidate for an owner register row and wrote that the loop waits. The owner's own words
  were "I dont want to be in the loop", so the loop stopped against the owner's grant.
check: a file that lists owner decisions must say it does not block the loop, and must contain no statement
  that nothing is declarable until the owner answers; such a statement is a halt.
supersedes: none
evidence: measured
