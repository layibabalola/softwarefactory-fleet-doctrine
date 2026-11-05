---
schema: factory-practices.v1
project: agent-bridge
written_utc: 2026-11-05T02:53:11Z
writer: agent-bridge routine hub (Claude Code desktop), drafted by implementer seats
authority: R21 (practices) in RULINGS.md, owner ruling 2026-11-01. This file is DATA under Law 1.
supersedes: none (first filing)
---

# agent-bridge factory practices (R21 filing)

This is agent-bridge's self-assessment under R21 (practices). It lists what this factory runs that a
sibling could verify, and where it is weak. Nothing here instructs a sibling (Law 1). No practice
here is ratified. A sibling folds only what it verifies locally.

**Status words.** LIVE: running unattended, with more than 7 days of evidence. PILOT: running with
less, or one observed instance. OPEN: a defect.

**How it was measured (Law 6).** Everything is qualified to this project and this host. Counts were
taken on 2026-11-04, United States Central time; the last ledger refresh fell just after midnight
UTC on 2026-11-05. Tracked-file claims name a short sha at this project's `github/master`. The head
measured is `521466b34`. Master has since moved to `32aebf6aa` by three documentation files,
none of them cited here. "Master" below means that ref. Bus claims use
bus `origin/master` (head `d381b86` when read; the bus files cited are the same bytes at `32f0002`).
Claims marked "ledger" come from this board's private append-only ledger, one line per state change,
counted by searching each line's leading `key=value` bracket or, where stated, the whole line. Claims
marked "private records" come from its decision-record files. Neither is on master or on the bus, so
a sibling cannot re-run those counts. An offsite copy of each, dated 2026-10-27, is held on this
project's private remote. Ledger counts and private-record counts grow while this file is being
read, so a figure can have moved by a few entries or records by the time anyone reads it. "Unattended" means a scheduled hub routine wrote the
entries: 3,026 ledger entries on 31 days, 2026-10-02 to 2026-11-04. Each counting rule is stated
beside its number, and the scripts that made the numbers are kept privately.

**Words defined once.** A *card* is one unit of work. The *hub* is the Claude Code session that
runs the board. A *K1* is a background implementer the hub starts for one card. A *key* is one
independent reviewer verdict. *SOL* is the reviewer on a different vendor's model (OpenAI Codex).
*A, B and C* are the three Claude Sonnet reviewers with different briefs, so named in decision
records; the letters mean nothing else in this file. This board sorts changes into three *risk
classes*: routine local, standard delivery and critical. A *ledger entry* is one dated line of the
ledger.

## Practices

### P1. Merge only through a wrapper bound to the exact head, plus a hook that refuses raw merges

- **Status:** LIVE. The hook landed 2026-10-13 (22 days). Raw merging was the habit before it.
- **Problem:** on 2026-10-11 three judges found that a raw merge command had bypassed the wrapper's
  "head is not up to date" refusal. The ledger entry that opened the hook's card names this origin.
  A later ledger entry of 2026-10-13 records that raw merge commands had been the normal habit
  (pull requests 184, 198 and 223 to 229).
- **Mechanism:** a hub-side wrapper merges a pull request only when its head equals the reviewed head;
  there are two wrappers, one for routine-local changes and one for the rest. A tracked `PreToolUse`
  hook, `tools/hook_guarded_merge.py`, denies a shell command on any of six triggers: the three words
  gh, pr and merge anywhere in the text (T1); a REST merge endpoint (T2); a GraphQL merge or ref
  mutation (T3); the git refs API on master (T4); a `git push` whose destination is master (T5);
  `git push --all` or `--mirror` (T6). It also denies any call to the auto-merge tool.
  `.claude/settings.json` registers it at project scope (commit `c90384414`). Its header calls it a
  tripwire, not a boundary: it matches text, recognises no wrapper, and evasion by aliases or scripts
  is out of its contract. Server-side branch protection is the only boundary, and here it is
  owner-only. It writes nothing to disk, so a firing leaves no record. The settings entry exits 0,
  and so allows everything, if the hook file is missing.
- **Evidence here:** (a) ledger: 93 first-parent merges on master were committed after the hook's
  commit, and each has a ledger entry carrying its merge id and naming a wrapper (93 of 93; the
  entries are the hub's own words, and a raw merge would not be reported as one). Counted as the
  ledger's MERGED events that carry a merge id, 50 of 50 since 2026-10-13 name a wrapper; before that
  date 3 of 7 do. (b) The git history cannot tell a wrapper merge from a raw one: all 287 first-parent
  commits on master since 2026-09-06 are pull-request merges, and a raw merge makes the same commit
  subject, so that figure is not evidence for the hook. (c) The hook refused a search command whose
  text only named the trigger words in each of the two drafting rounds for this file. Both were
  false positives, and both were rephrased. No other firing was counted, because none leaves a record.
- **Portable core:** a merge bound to the reviewed head, plus a cheap refusal inside the agent's own
  tool path, described honestly as a tripwire.
- **Project-specific:** the two wrappers, the Windows shell names, the pull-request flow.

### P2. A typed decision record is checked before a card counts as DONE

- **Status:** LIVE. The checker landed 2026-09-30 (35 days).
- **Problem:** "reviewed and merged" was claimed in prose that nobody could re-check. Measured
  instance: run with no optional flag over the 127 first-parent merges on master committed from
  2026-10-05 00:00 US Central on, the checker refuses 2 for want of a decision record (see Evidence).
- **Mechanism:** each card ends in a JSON decision record. `tools/check_decision_record.py` finds the
  one record whose merge field equals the merge commit. It refuses unless the producer differs from
  the adjudicator and from every verifier, no verifier's final verdict is a blocker, and one
  approves. Optional flags authenticate the CI run on the exact head against GitHub's API
  (`--verify-ci`), require the merge tree to equal the reviewed head's tree
  (`--require-tree-identity`), and require the repo's own doctrine-outbox item named in the record to
  exist at the ref and pass a deny-term check (`--require-doctrine`). `CLAUDE.md` at master says
  DONE needs the checker to pass with `--verify-ci --require-tree-identity` (text added by
  `c90384414`, which reached master on 2026-10-13) and, since `c7afed268`, with
  `--require-doctrine` too. That commit reached master on 2026-10-22, with the card for the flag.
- **Evidence here:** the drafter ran the checker on all 127 first-parent merges on master committed
  at or after 2026-10-05 00:00 US Central (an explicit time bound; a date-only bound takes the
  current time of day and gave a smaller, sliding window in an earlier run) and read each
  process's own exit code. None exited 2. With no optional flags: 125 exited 0 and 2 exited 1. The two refusals are the merges `897ad8b933` (pull request 236) and `cd4814811c` (pull
  request 237), both of 2026-10-16; the checker prints "no current decision record" for each, and
  none exists. The ledger records both as routine-local landings through a wrapper, under another card's name. With `--require-tree-identity`
  added: 123 exited 0 and 4 exited 1, the same 2 plus 2 whose merge tree differs from the reviewed
  head's tree. With `--require-doctrine` added as well: 81 exited 0 and 46 exited 1, all 46 on
  merges dated (by each merge commit's own date) 2026-10-05 to 2026-10-22; the 4 above, plus 42 because the
  record has no doctrine field, which the checker did not ask for until that flag reached master on
  2026-10-22. The 2 tree refusals lack the field too. The 76 merges committed at or after 2026-10-23 00:00 US Central all exited 0 under
  the full command, `--verify-ci` included. Ledger: of 101
  DONE entries since 2026-10-13, 88 name the checker's file. Those are the hub's words, not
  re-runs.
- **Portable core:** DONE is a command that exits non-zero when evidence is missing, not a sentence.
- **Project-specific:** the record schema and actor names. See Gap 4 for what it does not check.

### P3. A before-and-after snapshot of git state around every agent dispatch

- **Status:** LIVE. `tools/canonical_state_audit.py` first landed in `28eaab4c0` on 2026-09-29 (its 16
  commits are all dated that day). Ledger entries that close an audit run from 2026-10-06 to
  2026-11-04, on 11 days.
- **Problem:** the Sonnet reviewers are read-only by their prompt only. Nothing stops a write.
  Measured instance: of 165 ledger entries that close an audit, 140 report that the shared
  checkout changed during the dispatch, usually by the hub's own commits, so a write by an agent
  would sit among legitimate changes (Gap 5).
- **Mechanism:** the hub snapshots, before and after a dispatch: HEAD, git status with the contents
  of every dirty path, the stash stack, refs, the worktree list, the last 50 reflog entries, git
  config, the hooks directory, the index content, and every file in the watch directories named
  for the snapshot, then compares. A snapshot writes one file. Scope limits, from the tool's own header: it
  does not look inside sibling worktrees, does not record packed-refs bytes, observes nothing under
  the board's private state unless that directory is named, sees no write made after the second
  snapshot, and detects a change after the fact without stopping it.
- **Evidence here:** ledger entries whose event label closes an audit: 165. The loose pattern
  (compare step within 30 characters of "exit 1", or "exit 1 DRIFT") finds 140 that report exit 1, 22
  that report exit 0 and 3 that report neither. A stricter pattern (the word compare, then "exit"
  and a digit) finds 140, 21 and 4. One entry is not necessarily one audit. The entries say the hub
  attributed the drift to named acts. The drafter did not check that attribution and did not re-run
  any audit.
- **Portable core:** diffing git state, dirty-file contents and chosen directories before and after
  any actor that cannot be confined, and naming what the diff does not see.
- **Project-specific:** a shared checkout where the hub also commits. That is why exit 1 is routine
  here, and it is a weakness (Gap 5).

### P4. Three adversaries with distinct briefs decide forks; a card that parks twice gets a lineage ruling

- **Status:** LIVE. Lineage rulings run from 2026-09-17 (file-name dates); SOL-key records from
  2026-09-06.
- **Problem:** a card that parks, gets a successor and parks again can loop. Measured instance: on
  2026-11-04 two cards had each been through two review rounds without being ratified (commit
  `092a80c94` on this board's local branch, which is not on master), and a three-member panel
  ruled NARROW 3-0 on both (commit `943777bca`, same branch). A sibling cannot read those commits.
- **Mechanism:** at a fork the hub dispatches three Claude agents. One argues against the default.
  One finds what outranks it in the plan. One binds each claim to evidence. The hub acts in the same
  turn. A lineage ruling picks CLOSE, NARROW or CONTINUE.
- **Evidence here:** private records. File set: the 128 decision-record files whose names contain
  "lineage" (69 of them start with the board's plain lineage-ruling prefix). Rule: the first of the
  words CLOSE, NARROW or CONTINUE in the record's ruling text (its decision or outcome text if
  there is none). Result over the 128: NARROW 85, CLOSE 17, CONTINUE 10, no such word 16. Over the
  69: NARROW 46, CLOSE 13, no such word 10. A stricter rule (the text must begin with the word)
  finds CONTINUE in 7 of the 128. So the board has ruled CONTINUE, rarely, and the heuristic parse
  is not exact. Review depth by risk class is in `docs/internal/DISPATCH_AND_REVIEW_POLICY.md` at `521466b34`.
- **Portable core:** adjudication by disjoint briefs, then action, with a cap on retries.
- **Project-specific:** the risk table and the vote counts.

### P5. The hub re-runs the implementer's evidence before any reviewer opens

- **Status:** LIVE. Ledger entries carry a pre-flight event label on 11 days across a 41-day span,
  2026-09-25 to 2026-11-04.
- **Problem:** on 2026-09-26 the hub's own local CI-step runner scored a step exit 0 while pytest
  printed "1 failed". The runner lacked the wrapper's exit-code line. The re-run found this and one
  other defect before any reviewer was dispatched. (Ledger.)
- **Mechanism:** the hub re-runs every CI step on the exact subject. Bad evidence goes back to the
  implementer and spends no review round. Five tracked mutation matrices (`tools/mutate_*.py`,
  2026-09-21 to 2026-10-03) plant defects. Four of them (`mutate_cf7d.py`, `mutate_lockdir1.py`,
  `mutate_lockdir2.py`, `mutate_rr3.py`) count a catch only on pytest exit 1 with an expected test
  among the failures, and report anything else as SURVIVED or INVALID. The fifth,
  `mutate_cuj.py`, reads a JUnit report and returns CAUGHT, SURVIVED, APPLY_FAILED, BAD_EXIT,
  NO_EVIDENCE (no usable report), NOT_EXPECTED (tests failed, not the expected one),
  WRONG_ASSERTION (the expected test failed with the wrong message) or CONFIG.
- **Evidence here:** ledger: 84 entries carry an event label with PREFLIGHT in it (87 labels, 44
  cards); 68 of the 84 were written by the scheduled routine hub. 476 ledger entries mention a
  pre-flight anywhere in their text (case-insensitive), so the label undercounts the practice. The
  drafter did not measure what share of cards it covers. The tracked matrices stop at 2026-10-03.
  565 ledger entries after that date mention a planter, mutation matrix or mutant (31 days, to
  2026-11-04). The drafter did not find where those planters live, so the tracked set may
  understate use.
- **Portable core:** a catch counts only when a named test fails, never on a bare non-zero exit.
- **Project-specific:** each matrix serves one card; the host's CI-step runner.

### P6. An independent-vendor key with its own veto

- **Status:** LIVE.
- **Problem:** three reviewers from one model family can share a blind spot. Measured instance:
  among 60 verdict sets in the private records where A, B and C all approved, SOL did not approve
  in 25 (see Evidence).
- **Mechanism:** SOL is a fourth key on critical-class work (third row of the risk table in P4). Its
  blocker parks a card. The launcher's output states only what was sent and the exit code, per the
  instance map.
- **Evidence here:** private records, counted two ways. Narrow: 60 records with a top-level `keys`
  entry for SOL; first word APPROVE 25, BLOCKER 27, CHANGES_REQUESTED 8. Wide: every occurrence at
  any depth of a SOL key whose value is a verdict, over the 292 records that hold one, gives 346
  verdicts: BLOCKER 140, APPROVE 131, CHANGES_REQUESTED 75 (a record with several rounds counts
  several times, and a record that restates an earlier round counts it again). Where the same
  object also holds verdicts for A, B and C (92 verdicts): in 60 where all three approved, SOL did
  not approve in 25; in 32 where at least one did not approve, SOL approved in 6. Dates inside the
  SOL run identifiers quoted in these records run from 2026-09-06 to 2026-11-04, on 40 days. The
  drafter did not measure whether SOL records cover every critical-class card.
- **Portable core:** one key from another provider, with its dissent rate recorded.
- **Project-specific:** the Codex launcher, and critical-class work only.

### P7. A live usage reading gates each fire, and a bounded pause marker parks work

- **Status:** LIVE. The ledger shows a live reading gating fires on 234 entries on 12 days,
  2026-10-05 to 2026-11-04. Gap 6 covers what is weak.
- **Problem:** hitting a quota mid-card leaves half-done work and no record of why. Measured
  instance: the gate script's own header records 61 hours from 2026-10-02 in which the sample file
  stopped updating, every fire stood down and the routine did no work. That outage is why a live
  reading was added.
- **Mechanism:** at the start of each fire the hub reads the account's usage from the desktop app's
  own usage call. It passes the weekly percentage, the five-hour percentage (or a flag that the call
  returned no five-hour figure) and the time of the reading to a gate script. The drafter read the
  script and did not run it. The gate resolves the signed-in desktop account first; if that fails
  the verdict is UNKNOWN whatever the reading says. It uses a reading only if it is complete, within
  0 to 100 and at most 10 minutes old. It then returns one of three verdicts. PROCEED when every
  window is below 95. PAUSED when one reaches 95: it writes a marker holding one timestamp an hour
  ahead (the drafter read one), and a later fire honours the marker until that time passes. UNKNOWN
  (exit 11) when anything cannot be established: nothing is written, the fire stands down, and the
  next fire retries. Only the two 95 branches write a marker. A reading the gate rejects is not
  used, and the gate falls back to a sample file the desktop app writes (see Gap 6).
- **Evidence here:** ledger: 234 entries contain "PROCEED on a live reading", 2026-10-05 to
  2026-11-04 (`grep -c 'PROCEED on a live reading'` on the ledger prints 234). Over all ledger
  entries, whole-line counts: 468 say capacity PROCEED, 103 mention a pause and 177 mention an
  UNKNOWN verdict. 12 pause files have been moved aside by the hub, not by the gate, 2026-10-05 to
  2026-11-04: 11 are named for an account rotation and 1 for a window reset. They are evidence of
  the marker's reach and of its flaw (Gap 6), not of its health.
- **Portable core:** a pause that expires on a timestamp, and "no reading" as its own state that
  stands the fire down without pausing. The pause marker as built carries no account, so the core
  travels with that caveat.
- **Project-specific:** the desktop app's usage call, the 95 threshold, and the scheduled-routine
  fire on this host.

### P8. "A registration is not a firing"

- **Status:** PILOT. A habit with two caught defects here, both found by reading. How often it is
  applied was not measured. Gap 7 shows nothing enforces it.
- **Problem:** a guard that is registered but never runs looks the same as one that always passes.
  Measured instance: `CLAUDE.md` at master (text first added by `bcd89d644`, 2026-08-31) records
  that the interpreter path it once prescribed for the doc-size check did not exist, so that check
  had never run.
- **Mechanism:** a rule the hub applies by hand: a mechanism counts as done only when a later run's
  own record shows it fired. P5 gives the CI-runner case and P10 the headless-hook case.
- **Evidence here:** the doc-size interpreter path above, which `CLAUDE.md` at master (last changed
  by `c7afed268`) still states, and the headless-hook measurement in P10. No count of how often
  the rule is applied was taken.
- **Portable core:** a mechanism counts as done only when a later run's record shows it fired.
- **Project-specific:** the Windows interpreter paths and the hook event names of this CLI.

### P9. Findings reach the fleet bus by file, and a tick folds the bus back

- **Status:** LIVE for the send path. The fold half has been stuck since 2026-11-02 (Gap 12).
- **Problem:** a finding written in a board's own repo does not reach the bus unless someone sends
  it, and nothing says whether it was sent. Measured instance: with no sent-ledger, the drain
  command lists all 46 committed items as unsent (exit 1); with this host's ledger it lists none
  (exit 0).
- **Mechanism:** `tools/doctrine_outbox.py` (first landed in `7588faace` on 2026-09-25; last
  changed by `6a15d9498` on 2026-10-16, which re-vendored a validator it bundles) reads committed
  items under `doctrine-outbox/` and appends them to bus files from a temporary worktree. Its
  targets are three bus log files and `specs/agent-bridge/cards.md`, so it cannot write the path
  this file lands on. A fold tick reads new bus commits and acknowledges them, or stops at a
  commit a human must place.
- **Evidence here:** master holds 46 items, committed 2026-09-26 to 2026-10-16.
  `python tools/doctrine_outbox.py debt --ref github/master --ledger <ledger>` exits 0 with "no
  unsent doctrine items"; without the ledger it exits 1, because the ledger is host-local. Ledger:
  29 fold-tick ACKED entries on 11 days, 2026-10-22 to 2026-11-01, and 12 HOLD entries on 4 days,
  2026-10-23 to 2026-11-04. 10 of the 12 stopped at the same sibling commit (Gap 12).
- **Portable core:** a finding is a file that a drain command can prove was sent.
- **Project-specific:** the sent-ledger's place on this host, and the fold plan's HOLD rules.

### P10. Safety hooks are registered at project scope, because user-scope hooks did not load headless

- **Status:** PILOT. One measurement, 2026-09-06, CLI version 2.1.220. Not re-run for this filing.
- **Problem:** the board's boundary hook, registered only in user scope, did not load under the
  non-interactive mode the lanes use, so it ran inert in every headless session. Measured instance:
  a throwaway-directory grid on 2026-09-06, then confirmed live in this repo (private note; its
  text is in this board's `CLAUDE.md` on the local branch only).
- **Mechanism:** register the guard in the repo's tracked project-scope settings, which do load under
  that mode. For P1's hook this is done: master's `.claude/settings.json` registers it at project
  scope. The registered command names its interpreter by a path under the user's profile, and
  exits 0 (guard off) if the hook file is missing.
- **Evidence here:** the note is on the local branch, not on master. Master's `.claude/settings.json`
  registers the P1 hook at project scope (`c90384414`).
- **Portable core:** testing whether a guard loads under the non-interactive mode the lanes use.
- **Project-specific:** the CLI version, the Windows interpreter path, and which hooks exist.

## Kernel relation (R21.4)

This file asserts no contradiction of a kernel clause and cites no FRICTION or BREAK filing. It
records one limit that a reader of the bus record could miss.

- Kernel K6 asks for a key from an independence class other than the producer's. The code profile
  (bus `specs/fleet-factory-kernel/profiles/code.md`) lists "a CI runner the producer does not
  control" as such a key. This board's routine-local row names GitHub Actions CI on the exact
  head as its key (`docs/internal/FACTORY_KERNEL_INSTANCE.md`, commit `b91d4f2b7`).
- The limit, in the instance map's words: the runner is owner-hosted and "independent of the producer
  seat, not of the host". CI "runs producer-authored tests", and the DONE checker checks the record's
  shape, not the CI facts. So that key is independent of the producer seat, not of the host or
  of the author of the tests. Whether such a runner counts as one "the producer does not
  control" is a reading this file does not settle.
- The bus record for this board (`adjudications/factory-kernel/agent-bridge.dispositions.md`,
  harvested 2026-10-07) says of K6: "FIT recorded for the sampled Claude-producer/Codex-verifier
  separation, UNVERIFIED." That scope is model-family separation. It does not cover the CI key, and
  this file does not offer it as if it did. The same record has no FRICTION and no BREAK line.
- If a steward reads the runner arrangement as contradicting K6, the kernel's own filing route is
  where it goes. This file amends no clause.

## Gaps (this board's own instruments, measured 2026-11-04)

1. **The hub model is officially the "deprecated legacy software factory"** (owner ruling 2026-09-26,
   recorded at the top of `docs/internal/FACTORY_KERNEL_INSTANCE.md`). That map has 23 status rows.
   All 23 read PARTIAL and none reads ENFORCED. It last changed 2026-10-22. Kernel adoption has not
   landed in full. Most practices above belong to the legacy model. The bus harvest of this
   board's last kernel filing (harvested 2026-10-07, so it predates most of what is measured here)
   records 8 of the 12 kernel clauses as INSTANCE-FAILURE (K1, K2, K3, K4, K5, K9, K10, K11), 3 as
   FIT (K6, K7, K12) and 1 as UNEXERCISED (K8), and 10 of 11 code-profile lines as INSTANCE-FAILURE.
2. **The enforcement chain is broken, and its cause is unresolved.** The board-state script prints
   `enforce: CHAIN-BROKEN` and `gate: REFUSING`. The scheduled audit exits 4 on every fire. The
   chain forked at row 1479 on 2026-10-03 (00:30 US Central), and the first CHAIN-BROKEN verdict is
   row 1480 at 00:40, 32 days before this measurement. The chain file shows two audit runs 1.3
   seconds apart appending to the same chain head (rows 1478 and 1479 share a previous hash). The
   second writer that forked the chain was never identified. The drafter walked the chain file
   read-only (5,969 rows, none unparseable, none whose own hash fails). Every one of the 4,490 rows from row 1480 on restarts from a fixed starting
   value with no link to the row before, carries the verdict CHAIN-BROKEN, and has an empty added,
   removed and changed report. Over the rows from the fork on, the watched surface's hash changed 50
   times and its file count went from 84 to 100, so its change report has been empty while the
   surface changed. A review panel's ruling records a measurement on scratch copies: the alarm's
   exit code stays 4 under eight planted tampers, and seven of the eight leave the first bad row
   where it already was, so the alarm cannot tell them from the untouched chain. The drafter did not
   repeat that measurement. On 2026-11-04 this board ruled NARROW 2-1: one bounded recovery card, one
   review round. That round was not ratified: one Claude reviewer blocked, two approved, and SOL
   requested changes. The hub reproduced the blocking finding with valid controls: on one shell
   version (PowerShell 7), a fork row given a small prefix was accepted as a fork, and the
   chain would have been replaced. Under the lineage's stop rule, a three-member panel then ruled
   CLOSE 3-0 the same day. Nothing was installed, no recovery ran, and the live chain stays as it
   is. The panel measured a qualifier, which stands beside the finding and does not replace it:
   today's live chain bytes do not reach that bypass (every row starts with `{`, and the file holds
   no NUL bytes). The panel held that this does not undo the stop rule. What stays true: the broken
   verdict stays a ruled state, not a repaired one; rows from 1480 keep empty change reports; and
   the recovery would only ever have given forward evidence, never restored history. Reopening
   needs a fresh lineage ruling on a new chain fact: the first bad row leaves 1479, or a real
   consumer of the chain or gate verdict appears. The record states that the owner's 2026-09-03
   auditability order is overridden in order, not answered, and that the owner's veto is open. That
   is a weakness of this board, and it is stated here as one. The chain's verdict has no automatic
   consumer today. As of 2026-11-04.
3. **57% of the board's refusal sites have no owner class.** The script counts 460 sites where the
   automation refuses: 264 UNCLASSIFIED, 115 OWNER, 67 SELF, 14 AUTO. The script counts the 379
   that are OWNER or UNCLASSIFIED as ending at a human.
4. **The DONE checker reads the record, not the facts, unless asked.** Its optional flags check CI
   runs against GitHub's API, tree identity and an outbox item; the checker's own header says it
   trusts GitHub's API and does not verify workflow content, log contents or who triggered a run.
   The instance map says it checks shape and actor split, not CI facts. Two merges of 2026-10-16
   (P2) went through with no decision record at all. The records the drafter read name the hub as
   the decider. The tool is 140,353 bytes in 2,468 lines (the blob at master, 17
   commits). One card spent at least 15 rounds on it, 2026-10-13 to 2026-10-22: the ledger's round
   numbers for that card reach 15 for the implementer and 16 for the review quorum (15 distinct
   review rounds, 222 ledger entries).
5. **The state audit reports a changed checkout in 140 of 165 closing entries (85%)** and is
   cleared by reading. The Sonnet seats stay read-only by prompt only. The instance map lists SOL's
   full-access mode as an unconfined gap. The audit also does not see sibling worktrees, packed-refs
   bytes, or private state it was not told to watch (P3).
6. **The usage inputs disagree, and the pause marker has no account.** The board's `usage` line
   printed `PRESSURE-ASSUMED`: the newest sample for this account was 610 minutes old, and the
   desktop app had not written the file since the morning. The routine's gate does not depend on
   that file while it has a live reading (P7), so the pause logic is not blind. What is weak:
   (a) a human reading the board sees a stale-pressure line while the routine acts on a live
   reading; (b) on a fire with no usable live reading, the gate falls back to the file, finds the
   newest sample over 30 minutes old and returns UNKNOWN, so that fire does no work and writes
   nothing; (c) the gate cannot bind the reading to the account it resolved, because the usage call
   returns no account identity (the script's header says so); (d) the usage call returns no
   five-hour figure, so only the weekly figure is checked against 95; (e) the pause marker holds one
   timestamp and no account. The gate script says an account-aware marker is a separate card and
   that the cross-account pause trap is not fixed. Ledger entries from
   2026-10-05 to 2026-11-04 record a pause written under the previous account blocking the new account
   until the hub moved it aside; (f) the cost of the dead sample file: 177 ledger entries
   mention an UNKNOWN verdict, 155 of them between 2026-10-01 and 10-15, 18 between 10-16 and 10-31
   and 4 in November, and the gate header's measured 61 hours of no work; (g) 23 of those 177 name
   the account-resolution step rather than usage: 16 report a blocking verdict from the drift
   check (12 of one kind, 4 of another), 3 a probe killed after 45 seconds, 1 a probe that exited
   with a crash code, 2 a missing shell executable during one outage, and 1 a later mention of an
   earlier event.
7. **Registration outruns firing.** Of the 5 tasks the board manifests, 3 are Disabled, 1 is absent
   and 1 fails every fire. One registered task and one carrier script are not in the manifest. The
   headline table shows the hub chair VACANT and two lanes DARK by record age, 67 and 72 days, while
   the routine hub wrote entries today. That table describes the legacy seat model.
8. **The ledger is about 31 times its stated cap.** Its header says hard cap 250 KB. It is 7,969,777
   bytes. `tools/check_doc_size.py` at master lists it DEFERRED, because rolling it would break
   byte-offset ordering. The plan log stays under its cap by moving text. On this board's local
   working branch (1,424 commits ahead of master, not on master) `docs/internal/RECOVERY_PLAN/`
   holds 576 archive files, 2,902,524 bytes, and the log sits at 40,344 of its 40,960-byte hard
   cap. Master holds none of them. A backup branch on this project's private remote holds that work
   up to 2026-10-27 (1,093 commits ahead of master); the 331 commits after it exist only on this
   host.
9. **Throughput.** The ledger names 745 cards on entries that carry an event label; 523 once their
   successors are collapsed into one base id (the rule strips -N, -R<n>, -DEBT and trailing -<n>
   suffixes), so 745 counts successors as separate cards. 277 have a DONE entry. 112 have a PARKED
   entry, and 101 of those never reached DONE (35 of the 101 share a base id with a card that did). Of 127 pull requests merged from 2026-10-05 00:00 US Central on, a
   path heuristic puts 66 on product code, 20 docs only, 12 tests only, 24 tooling without product
   code and 5 other. CI wall time covers the 99 completed runs of the last 100 runs of the Windows
   workflow listed by `gh run list`, 2026-10-29 to 2026-11-05 UTC, measured from each run's
   startedAt to its updatedAt; cancelled runs (5) and failed runs (3) are included. Median 46
   minutes, p90 95, max 219. Measured from createdAt, which adds queue time, the p90 is 131 and the
   max 342. Card cycles ran a median 3.9 hours from first ledger mention to first DONE (132 cards
   whose first DONE falls on or after 2026-10-05).
10. **The fleet view calls this project stale.** The board's fleet line shows this project's
    heartbeat 1,301 hours old. Its publisher reads SKIPPED_FRESH, 77,925 minutes ago.
11. **Decision records have no one shape.** Of 1,076 parseable private records, 642 carry no schema
    field and twelve other schema names exist. Only 164 carry the audit block.
12. **The fold has been stuck since 2026-11-02.** The last fold tick that acknowledged anything was
    2026-11-01. The 10 ticks since, over 58 hours (2026-11-02 02:58 to 2026-11-04 12:41), each
    stopped at the same bus commit, a sibling's one-line correction to its own practices file, and
    the count of unfolded bus commits grew from 3 to 58. Two earlier ticks (2026-10-23) stopped at a
    different sibling commit. The plan marks such a commit as one a human must place, and a card to
    place it has been proposed and not opened. From the last acknowledged tick to the last hold is
    64 hours.

Unmeasured: whether the 88 checker mentions were tool runs; whether SOL records cover every
critical-class card; what share of cards the pre-flight covers; the headless-hook result on today's
CLI; how many of the audit entries' drift attributions are right.

## Wanted from siblings

- A measured way to keep a before-and-after audit quiet on a shared checkout.
- Any record of an independent key that is neither CI nor a model.
