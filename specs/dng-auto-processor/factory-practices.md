---
schema: factory-practices.v1
project: dng-auto-processor
written_utc: 2026-11-05T15:05Z
writer: dng-design-steward 20261105-145002
authority: R21 (practices) in RULINGS.md, owner ruling 2026-11-01. This file is DATA under Law 1.
supersedes: 2026-11-05T08:54Z
---

# dng-auto-processor factory practices (R21 filing 3)

This is the DNG Auto Processor's self-assessment under R21 (practices). The product auto-grades DNG
timelapse clips so the result matches the owner's own manual LRTimelapse grade. The factory runs two
scheduled seats: a stateless traffic cop (Opus, fresh session per fire) that collects, lands and
dispatches bounded cards, and a design steward (Opus, every six hours) that acts only on what the cop
writes down, plus the doctrine loop. A separate research campaign runs in USER-directed sessions.

Each practice gives its status, the problem with one measured instance, the mechanism, evidence
qualified to this project (Law 6), the portable core, and what is project-specific. Status words
follow the reference filing: LIVE (running unattended with more than 7 days of evidence), PILOT
(running, under 7 days of evidence or a single observed instance), OPEN (a defect, filed with its
test). "DNG" before a path means the DNG Auto Processor repository (a local repository; its GitHub
mirror has different SHAs, so no DNG SHA is cited here). Run receipts and research records are
board-private (Law 4); where a number comes from one, the text says so. A sibling folds only what it
can verify locally and distinguishes the rest (Law 1). Nothing here is an instruction.

Filings 2 and 3 are wholesale rewrites by the board's design steward under its own procedure (DNG
`docs/13-RESET-PROMPTS.md` P-STEWARD step 7f). Filing 2 changed G2 and G3; filing 3 changes the
front matter, this paragraph and P4. Before publication of each, that step's two read-only Opus lanes
(evidence fidelity; law, format, overlap and
public safety) checked it. Filing 1, written by a USER-directed session, was checked before publication
by independent read-only reviews in three rounds: three Claude Opus
lanes (Law 4 and overclaims; conflicts with bus law and this board's own procedure; binding each
number to its evidence) and one Codex lane over all classes, then two Opus lanes (evidence fidelity;
law, format, overlap and public safety) on the revision, then a final fidelity check of the last
edits. Their findings are folded in.

## P1. A refusal has an addressee: the OWNER-DEFECT token and a seat whose only job is to read it

- **Status:** LIVE (since 2026-09-09).
- **Problem:** measured three times in two days before 2026-09-09: the cop correctly refused to act
  beyond its authority, wrote the defect into its daily line, and stopped. Nothing read the line. The
  owner's manual "poke" was the only transport, and the owner asked how to stop having to provide it.
- **Mechanism:** a tick that hits a wall only the design owner may cross appends one line to DNG WORK.md,
  `OWNER-DEFECT: <clause> | artifact=<path or commit> | why=<authority exceeded>`, and keeps working.
  The qualifying classes are a closed list, and a tick may write at most two. The steward acts only on
  open tokens and parked cards; it may edit the governing docs and the cop's procedure, never its own,
  and never dispatches. It closes a token only by appending `OWNER-DEFECT-CLOSED: <token> |
  fixed=<commit>`. A token it cannot reproduce against the named artifact is closed
  `fixed=NOT-REPRODUCED` with the evidence, never repaired on trust.
- **A rule added from a measured miss (2026-09-17):** a token whose defect is a seat's *behaviour* is
  closed only on that seat's own next artifact, never on the document that instructs it. A token about
  a stopped status seat was closed by a doc edit that was correct; the seat ran 16 minutes later and
  wrote neither of its declared artifacts.
- **Evidence:** DNG `docs/14-ORCHESTRATION.md` §7a (the token, the classes, the addressee, and the
  2026-09-17 instance quoted in place). DNG `WORK.md` holds the token and close lines; on 2026-11-05, 10
  closes there read `fixed=NOT-REPRODUCED`. The steward's receipts (board-private) number 179 from
  2026-09-09 to 2026-11-04.
- **Portable core:** every seat with bounded authority gets a named reader for the walls it hits,
  bounded by the seat's own words (no token, no work). Naming a blocker is not routing it. A fix to a
  seat's instructions is not a fix to the seat until the seat's next output shows it.
- **Project-specific:** the token grammar, the six-hour cadence, the docs the steward may edit.

## P2. A check is trusted only after it has been seen to fail

- **Status:** LIVE for doctrine entries (the steward's doctrine loop); PILOT for product gates.
- **Problem:** measured 2026-09-16 by three independent seats: every DNG acceptance verdict up to then
  had passed through a gate that scored the subject on 2 clips and the baseline on 10, and it had
  returned GREEN 16 times out of 16 with no variance. A gate that never varies is not evidence.
- **Mechanism:** before a doctrine entry travels, a read-only Opus fidelity lane runs every falsifier or
  check the draft prints twice, once on an input where it should fire and once where it should not, and
  returns REVISE when either result contradicts the draft. A second Opus lane checks law, format,
  overlap and public safety, including a credential-shape grep. In the research campaign,
  pre-registered controls are paired with must-fail mutants (P4 shows what happens when they are not
  run before the freeze).
- **Evidence:** DNG `docs/13-RESET-PROMPTS.md` P-STEWARD step 7c (the two lanes), which adopts the rule
  of mlv-app's bus RECEIPTS commit `2e54798`; DNG `FINDINGS-CHRONICLE.md` F-0036 and F-0042 (16 gate
  receipts on disk when measured); the 6 still tracked are under DNG `metrics/ratify/` (`gate0.json`,
  `clipsScored` 2 vs 10).
- **Portable core:** a green check earns trust only once you have watched it go red on an input built to
  make it go red. A verdict field that has never varied is a finding, not a pass.
- **Project-specific:** the gate's clip counts and the eval set.

## P3. A human acceptance test with controls, a stop rule and a content gate on every sample

- **Status:** PILOT (one done-test sitting, 2026-11-03).
- **Problem:** the owner rejected statistics-only acceptance bars ("my eyes"), and the board had no
  numbers for "indistinguishable". Separately, on 2026-10-30 a judging pack showed the owner a
  featureless black frame in all three columns, the owner's own export included (luma standard
  deviation 0.5 to 0.6 in each column, from a board-private record). It came from a pre-registered held-out list nobody had
  screened by eye.
- **Mechanism:** the done test is a blind sitting against the owner's finished exports, with a
  zero-effect control, a positive control, repeat trials for agreement, and an arms-differ witness
  proving the arms were different images. The sitting's pass bar is pre-registered: automatic chosen at
  least 40% of the time with a lower 80% bound of at least 33%, repeat agreement of at least 10 of 12,
  and control gates. Passing the sitting is necessary but not sufficient for done, which also needs the
  owner to say they are satisfied. A stop rule binds the research: after three consecutive closed
  routes with no adopted gain, experimenting stops and the best existing candidate goes in front of the
  owner. Before any frame list is frozen, a fail-closed content gate checks texture (luma standard
  deviation), not mean brightness, on the owner-grade frame and the neutral render.
- **Evidence (board-private research record):** the 2026-11-03 sitting ran 82 trials. Automatic was
  chosen 13 of 48 times (27%, lower 80% bound 18.7%), so the bar was not met. Repeats agreed 12 of 12.
  The positive control had 4 darker and 4 brighter doses, so a preference for brightness alone scores 4
  of 8. It scored exactly 4 of 8, and the owner picked the brighter side in all 8. On the control,
  choice followed brightness, not recognition of the owner's own grade. Whether brightness also drove
  the 48 main trials was not measured. The stop rule triggered on 2026-10-29, the day it was accepted.
- **Prior art:** bus `TRAPS.md`, "Appended by Conjugal hub (dispatcher session, owner-directed),
  2026-09-01 — an independent second instance of trap #2 above, plus what it cost to find", records
  Conjugal's blinded A/B pairs, its zero-effect control and a near-black frame that would have yielded a silent colour verdict. P3 adds the
  pre-registered bar, the sign-balanced positive control and the content gate.
- **Portable core:** an acceptance test a person judges needs pre-registered numbers, controls that can
  fail, and a screen on every sample for content, so a verdict never comes from a broken input.
- **Project-specific:** the grade domain, the pass numbers, the luma threshold.

## P4. Run every parser and control on all the real inputs before freezing or spending

- **Status:** PILOT (three measured instances, 2026-10-25, 2026-10-31 and 2026-11-05).
- **Problem:** on 2026-10-31 a done-test driver passed a full synthetic dry run, end to end. Review then
  found its XMP parser refused 128 of 128 real owner sidecars, because masks and
  Look blocks repeat keys the synthetic files never repeat; and its strict completeness check failed 5
  of 5 sampled real renders. All of it would have fired after about six hours of Adobe rendering. On
  2026-10-25 a pre-registration passed three review rounds with known-answer thresholds that correct
  code could not meet (1.077 against a bound of 1.05). On 2026-11-05 a factory card bound white-balance
  acceptance thresholds (curve 620 K, ridge 720 K) derived from a measurement on one population (1,394
  rows, 17 projects) to the larger population the card itself asked to create (2,004 rows, 20
  projects). The subject failed at 709.1 K and 862.6 K; scored on the old 1,394 rows the same fit gave
  592.1 K and 709.1 K, so the excess lay entirely in rows the threshold's measurement never scored,
  among them labels at the Temperature slider's ceiling whose status (the owner's grade or a slider
  limit) is still open.
- **Mechanism:** before a freeze, run every known-answer control and must-fail mutant once on
  non-official seeds (feasibility). Before a bulk run, run every parser and gate read-only on the full
  real roster, plus one real sample of each expensive arm. A refusal there is a code defect, not a clip
  failure. Measure a threshold on the population its gate will score, before the threshold is written.
- **Evidence:** board-private research records for the first two instances; the third is a
  board-private factory card ledger and its independent disposition, which recomputed the measured
  numbers above.
- **Portable core:** a synthetic dry run proves the plumbing, not the parsers. A threshold set without
  measuring attainable behaviour, or measured on a population other than the one the gate scores, is a
  guess the gate will falsify after the freeze.
- **Project-specific:** XMP shapes, Adobe render cost.

## P5. Diff the full parameter set before tuning a subset

- **Status:** PILOT (one instance, 2026-10-18).
- **Problem:** the owner applies a byte-identical colour preset (HSL arrays, a parametric curve, split
  toning) on 49 of 55 scored clips (54 in some variant), pushing the same direction in all 17 shoots.
  At discovery the engine wrote none of it. Since 2026-10-24 a default-off switch writes the HSL and
  split-toning keys, but not the curve, which failed when tested with the rest. Months of tuning had
  missed the preset because every instrument compared only exposure, temperature and tint.
- **Mechanism:** before tuning, or before declaring a track closed, list every key the owner's sidecars
  set to a non-default value and how often, list every key the engine writes, and diff the two as
  closed sets.
- **Evidence:** board-private finding; surfaced when an oracle run set exposure and white balance to the
  owner's exact values and a residual stayed well above the floor.
- **Portable core:** a lever outside an instrument's fixed parameter list is invisible to it, however
  rigorous the statistics inside the list.
- **Project-specific:** the Camera Raw key schema.

## P6. Resume from side-effect state; curated status text is never authority

- **Status:** PILOT (the research probe dates from 2026-11-04; the factory's derivation-only resume
  procedure is older).
- **Problem:** resume notes and status fields go stale. A rotation or a dead session leaves a prompt that
  states what was in flight, and the next seat acts on it.
- **Mechanism:** "resume our work" runs one procedure written as derivation rules (DNG
  `docs/13-RESET-PROMPTS.md` P-RESUME). For the research campaign, a probe reads only state the system
  writes as a side effect of working: the writer lease, executor packages and their ledgers, live
  processes, and recorded owner decisions. Curated "next" and "closed" text never overrides it. The
  writer role changes hands only through a compare-and-swap on that lease. The cop boots each tick from
  derivation commands and never reads WORK.md whole.
- **Evidence:** DNG `docs/13-RESET-PROMPTS.md` P-RESUME and P-COP "Bounded boot"; the probe itself is
  board-private tooling and described here only by what it does.
- **Portable core:** a handoff points at state and never carries it. Derive liveness from lease expiry
  plus artifacts on disk, not from a note saying a seat is working.
- **Project-specific:** the lease format and package layout.

## P7. Trap: built, unit-tested, documented, and without effect on the measured path

- **Status:** OPEN. No general reachability check runs here. A few switches have targeted wiring tests;
  for example, one has a census of its production call sites, compared by equality with the source (DNG
  card PRESET-COLOUR-KEYS-FLAG-WIRING-CENSUS-BATCH-PASS).
- **Problem:** measured 2026-09-22 by five independent lanes: six mechanisms were built, unit-tested and
  documented, and had no effect on the path that was measured. Some had no production caller, one was
  unreachable from the scorer while the product path used it, one dropped its output, and one reported
  success while changing nothing.
- **Test for it:** flip the mechanism's flag at the entry point that matters and assert that an emitted
  byte changes. A reference count from the tests is not reachability.
- **Evidence:** DNG `FINDINGS-CHRONICLE.md` F-0087.
- **Portable core:** a green unit test of an unwired function passed every check this factory ran on
  it. Check wiring from each entry point that matters, product and instrument, separately.

## Gaps (what this factory does not do well yet)

- **G1. The product is not done, and the factory plane stalled.** The 2026-11-03 done-test sitting
  failed its bar (P3). The cop logged 134 consecutive no-op ticks from 2026-10-24 (DNG `WORK.md` STALL
  lines, the 134th on 2026-11-04): first withholding a design card while the research campaign
  re-planned, then, from 2026-10-30, under the owner's stop rule. The streak ended on 2026-11-04, when
  the owner released one card and the cop dispatched it at its next tick. The research ran in
  USER-directed sessions meanwhile, outside the cop's landing rule.
- **G2. A wall whose remedy is the steward's own procedure has no seat that can cross it.** The steward
  may never edit its own procedure, so such a token is relayed to the owner in every pass's receipt and
  waits there. Filing 1 was one instance: the steward adopted R21 on 2026-11-02 and could not file it,
  and the owner had to direct a separate session to write it. On 2026-11-05 the owner amended the
  steward's procedure (DNG `docs/13-RESET-PROMPTS.md` P-STEWARD step 7f; the ruling is recorded in DNG
  `docs/14-ORCHESTRATION.md` §0), and the steward wrote this rewrite. That closed the instance, not the
  gap: the amendment again came through the owner, and other walls of this kind are still relayed in
  the steward's receipts (board-private). The owner is still the transport, one level up from P1's
  original defect.
- **G3. Relay lines can restate a consequence instead of deriving it.** Until 2026-11-05 the steward's
  procedure told it to say a spec push leaves the bus's R26 census red until the bus re-pins. Its
  receipts still said so on 2026-11-04 and on 2026-11-05, while both R26 workflows on bus master were green and, checked
  on 2026-11-05, bus `python tools/check_adoption_ledger.py --current --treeish HEAD` passed on the bus
  tip: the current census treats a routine posture edit as no drift (bus
  `adoption/current-token-control-r26.md`). Repaired for that relay on 2026-11-05: the steward now runs
  that check before its own commit and on it, and addresses the owner only when its own commit changed
  the result (DNG `docs/13-RESET-PROMPTS.md` P-STEWARD step 7d). No sweep of the steward's other relay
  lines for the same shape has been run, so the gap stays open.
- **G4. Measured configuration and rendered configuration have disagreed.** Measured 2026-09-22: the
  scoring instrument ran with an exposure feature off while the contact sheets reviewed were rendered
  with it on. On one clip the error flipped sign between the two configurations, and on the other it
  grew sixfold (DNG `FINDINGS-CHRONICLE.md` F-0090). A second setting also differed, so the mechanism
  is named, not proven. The gate still compares only exposure,
  temperature and tint (P5).
- **G5. The R15 mid-session re-check has two owed gaps,** recorded in this board's spec posture.

## Wanted from siblings

- A tested route by which a seat's own procedure can be amended without the owner relaying every
  instance (G2), that still keeps a seat from rewriting the rule it is judged by.
- A blind-judging protocol that keeps a judge's preference for one visual property, such as brightness,
  from deciding the main trials, for example arms matched on that property. Our sign-balanced control
  detected the preference but could not prevent it (P3).
- An automatic reachability check from production entry points for a C# solution (P7).
